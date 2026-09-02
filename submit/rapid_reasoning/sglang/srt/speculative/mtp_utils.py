"""MTP (Multi-Token Prediction) self-speculative decoding utilities.

Chain-style speculative decoding for Qwen3.5-2B MTP: topk=1, num_steps=1/2,
num_draft_tokens=2/3, greedy sampling, page_size=1. Ported from the pre-slim
``eagle_utils.py`` with the tree machinery (build_eagle_tree /
verify_tree_greedy / sampling path) removed; acceptance is a plain torch
comparison of the draft token against the target's greedy prediction.

KV length semantics for the triton extend kernel: the kv_indices segment
covers ONLY the prefix tokens; the extend (query) tokens are passed via
K_Extend/V_Extend and masked causally by the kernel's stage 2. This differs
deliberately from upstream ``EagleDraftInput.generate_attn_arg_prefill``
(which follows the flashinfer bottom-right-causal convention and includes
the query tokens in kv_indices).
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional

import torch
import triton
import triton.language as tl

from sglang.srt.layers.attention.utils import create_flashinfer_kv_indices_triton
from sglang.srt.layers.logits_processor import LogitsProcessorOutput
from sglang.srt.model_executor.forward_batch_info import CaptureHiddenMode
from sglang.srt.utils import next_power_of_2

if TYPE_CHECKING:
    from sglang.srt.managers.schedule_batch import ScheduleBatch
    from sglang.srt.mem_cache.memory_pool import TokenToKVPoolAllocator

logger = logging.getLogger(__name__)

# Debug only: force a simulated accept length (with spec_steps=1 this clamps
# to 1, i.e. reject-all) to measure the no-acceptance overhead bound.
SIMULATE_ACC_LEN = os.environ.get("SIMULATE_ACC_LEN")


@dataclass
class MtpDraftInput:
    """Draft model state carried between decode iterations."""

    # Draft decode inputs (captured after the last draft extend)
    # shape: (b, 1)
    topk_p: torch.Tensor = None
    topk_index: torch.Tensor = None
    # shape: (b, hidden_size); target hidden states feeding the draft fc
    hidden_states: torch.Tensor = None
    capture_hidden_mode: CaptureHiddenMode = CaptureHiddenMode.FULL

    # Inputs for extend
    # shape: (b,); the last emitted token per request
    verified_id: torch.Tensor = None
    accept_length: torch.Tensor = None
    accept_length_cpu: List[int] = None

    # Filled by prepare_extend_after_decode
    positions: torch.Tensor = None
    seq_lens_for_draft_extend: torch.Tensor = None
    req_pool_indices_for_draft_extend: torch.Tensor = None

    def prepare_for_extend(self, batch: ScheduleBatch):
        """Shift the prefill input left by one and append the sampled token.

        The draft model predicts token t_{i+1} from (emb(t_i), hidden(t_{i-1})),
        so its prefill input is the target input shifted by one position.
        """
        # Prefill only generates 1 token.
        assert len(self.verified_id) == len(batch.seq_lens)

        pt = 0
        for i, extend_len in enumerate(batch.extend_lens):
            input_ids = batch.input_ids[pt : pt + extend_len]
            batch.input_ids[pt : pt + extend_len] = torch.cat(
                (input_ids[1:], self.verified_id[i].reshape(1))
            )
            pt += extend_len

    def prepare_extend_after_decode(
        self,
        batch: ScheduleBatch,
        speculative_num_steps: int,
    ):
        assert len(self.verified_id) == len(batch.out_cache_loc)
        accept_length_cpu = batch.spec_info.accept_length_cpu

        # BACKPORT-PPU (P1 post-verify slimming): bs=1 chain fast path.
        # The generic path below pays a D2H sync (seq_lens.tolist()) plus
        # cumsum / spec-info kernel per round; for bs=1 the extend positions
        # are seq_lens - n + arange(n) and the new verified id is the last
        # accepted token, all derivable without leaving the GPU.
        if (
            len(accept_length_cpu) == 1
            and os.environ.get("SGLANG_MTP_FAST_POSTVERIFY", "1") == "1"
        ):
            n = accept_length_cpu[0] + 1  # extend token count (1 or 2)
            batch.extend_lens = [n]
            batch.extend_num_tokens = n
            batch.seq_lens = self.seq_lens_for_draft_extend
            batch.req_pool_indices = self.req_pool_indices_for_draft_extend
            batch.seq_lens_sum += n

            self.accept_length.add_(1)
            self.positions = (batch.seq_lens - n).to(torch.int64) + torch.arange(
                n, device=batch.seq_lens.device, dtype=torch.int64
            )
            batch.input_ids = self.verified_id
            self.verified_id = self.verified_id[n - 1 :].to(torch.int64)
            return

        batch.extend_lens = [x + 1 for x in accept_length_cpu]
        batch.extend_num_tokens = sum(batch.extend_lens)
        batch.seq_lens = batch.spec_info.seq_lens_for_draft_extend
        batch.req_pool_indices = batch.spec_info.req_pool_indices_for_draft_extend
        seq_lens_cpu = batch.seq_lens.tolist()

        self.positions = torch.empty_like(self.verified_id, dtype=torch.long)
        new_verified_id = torch.empty_like(self.accept_length, dtype=torch.int64)
        self.accept_length.add_(1)

        create_extend_spec_info[(self.accept_length.numel(),)](
            self.verified_id,
            batch.seq_lens,
            self.accept_length,
            torch.cumsum(self.accept_length, axis=0, dtype=torch.int),
            self.positions,
            new_verified_id,
            next_power_of_2(speculative_num_steps + 1),
        )

        batch.seq_lens_sum = sum(seq_lens_cpu)
        batch.input_ids = self.verified_id
        self.verified_id = new_verified_id

    def generate_attn_arg_prefill(
        self,
        req_pool_indices: torch.Tensor,
        paged_kernel_lens: torch.Tensor,
        paged_kernel_lens_sum: int,
        req_to_token: torch.Tensor,
    ):
        """Build attention args for DRAFT_EXTEND on the triton backend.

        NOTE: ``paged_kernel_lens`` are the post-accept sequence lengths
        (prefix + extend). The triton extend kernel expects kv_indices to
        cover the prefix only, so subtract the extend length per request.
        ``self.accept_length`` has already been incremented to the per-req
        extend length by prepare_extend_after_decode.
        """
        bs = self.accept_length.numel()

        prefix_lens = paged_kernel_lens - self.accept_length.to(paged_kernel_lens.dtype)

        qo_indptr = torch.zeros((bs + 1,), dtype=torch.int32, device="cuda")
        qo_indptr[1:] = torch.cumsum(self.accept_length, dim=0)

        cum_kv_seq_len = torch.zeros((bs + 1,), dtype=torch.int32, device="cuda")
        cum_kv_seq_len[1:] = torch.cumsum(prefix_lens, dim=0)

        kv_indices = torch.empty(
            int(cum_kv_seq_len[-1].item()), dtype=torch.int32, device="cuda"
        )

        create_flashinfer_kv_indices_triton[(bs,)](
            req_to_token,
            req_pool_indices,
            prefix_lens,
            cum_kv_seq_len,
            None,
            kv_indices,
            req_to_token.size(1),
        )

        return kv_indices, cum_kv_seq_len, qo_indptr, None

    def filter_batch(self, new_indices: torch.Tensor):
        self.topk_p = self.topk_p[: len(new_indices)]
        self.topk_index = self.topk_index[: len(new_indices)]
        self.hidden_states = self.hidden_states[: len(new_indices)]
        self.verified_id = self.verified_id[: len(new_indices)]

    def merge_batch(self, spec_info: "MtpDraftInput"):
        if self.hidden_states is None:
            self.hidden_states = spec_info.hidden_states
            self.verified_id = spec_info.verified_id
            self.topk_p = spec_info.topk_p
            self.topk_index = spec_info.topk_index
            return
        if spec_info.hidden_states is None:
            return
        self.hidden_states = torch.cat(
            [self.hidden_states, spec_info.hidden_states], axis=0
        )
        self.verified_id = torch.cat([self.verified_id, spec_info.verified_id], axis=0)
        self.topk_p = torch.cat([self.topk_p, spec_info.topk_p])
        self.topk_index = torch.cat([self.topk_index, spec_info.topk_index])


@dataclass
class MtpVerifyOutput:
    # Draft input batch for the next round
    draft_input: MtpDraftInput
    # Logit outputs from the target worker
    logits_output: LogitsProcessorOutput
    # Accepted token ids including the bonus token
    verified_id: torch.Tensor
    # Accepted length per request in the batch, on CPU
    accept_length_per_req_cpu: List[int]
    # Per-request accepted draft-token count on device (all requests,
    # including finished ones); used for the mamba state commit
    accept_length: torch.Tensor
    # Indices into the flat logits/hidden tensors of the accepted rows
    accepted_indices: torch.Tensor


@dataclass
class MtpVerifyInput:
    """Chain verify input ``[v0, d1, ...]`` at consecutive positions."""

    draft_token: torch.Tensor
    positions: torch.Tensor
    custom_mask: torch.Tensor  # always None: a chain is plain causal
    draft_token_num: int
    spec_steps: int
    capture_hidden_mode: CaptureHiddenMode
    topk: int = 1
    # Filled by the worker after the target forward
    hidden_states: torch.Tensor = None

    @classmethod
    def create_chain(
        cls,
        verified_id: torch.Tensor,
        draft_token_ids: torch.Tensor,
        seq_lens: torch.Tensor,
    ) -> "MtpVerifyInput":
        """Build the verify batch directly (no tree kernel needed for topk=1).

        Args:
            verified_id: (bs,) the last emitted token v0 per request.
            draft_token_ids: (bs, spec_steps) draft proposals per request.
            seq_lens: (bs,) current sequence length S per request.
        """
        bs = verified_id.shape[0]
        proposals = draft_token_ids.to(torch.int64).reshape(bs, -1)
        spec_steps = proposals.shape[1]
        draft_tokens = torch.cat(
            [verified_id.to(torch.int64).reshape(bs, 1), proposals], dim=1
        ).flatten()
        offsets = torch.arange(
            spec_steps + 1, device=seq_lens.device, dtype=seq_lens.dtype
        )
        positions = (seq_lens[:, None] + offsets[None, :]).flatten()
        return cls(
            draft_token=draft_tokens,
            positions=positions,
            custom_mask=None,
            draft_token_num=spec_steps + 1,
            spec_steps=spec_steps,
            capture_hidden_mode=CaptureHiddenMode.FULL,
        )

    def prepare_for_verify(self, batch: ScheduleBatch, page_size: int):
        assert page_size == 1, "MTP speculative decoding requires page_size == 1"
        batch.input_ids = self.draft_token
        batch.out_cache_loc = batch.alloc_token_slots(len(batch.input_ids))
        end_offset = batch.seq_lens + self.draft_token_num

        bs = batch.batch_size()
        assign_req_to_token_pool[(bs,)](
            batch.req_pool_indices,
            batch.req_to_token_pool.req_to_token,
            batch.seq_lens,
            end_offset,
            batch.out_cache_loc,
            batch.req_to_token_pool.req_to_token.shape[1],
            next_power_of_2(bs),
        )

    def generate_attn_arg_prefill(
        self,
        req_pool_indices: torch.Tensor,
        paged_kernel_lens: torch.Tensor,
        paged_kernel_lens_sum: int,
        req_to_token: torch.Tensor,
    ):
        """flashinfer-convention attention args (kv covers prefix + draft).

        Kept for backend compatibility; the triton backend builds its
        target_verify metadata inline and does not call this method.
        """
        batch_size = len(req_pool_indices)
        qo_indptr = torch.arange(
            0,
            (1 + batch_size) * self.draft_token_num,
            step=self.draft_token_num,
            dtype=torch.int32,
            device="cuda",
        )
        cum_kv_seq_len = torch.zeros(
            (batch_size + 1,), dtype=torch.int32, device="cuda"
        )

        paged_kernel_lens = paged_kernel_lens + self.draft_token_num
        cum_kv_seq_len[1:] = torch.cumsum(paged_kernel_lens, dim=0)

        kv_indices = torch.empty(
            paged_kernel_lens_sum + self.draft_token_num * batch_size,
            dtype=torch.int32,
            device="cuda",
        )
        create_flashinfer_kv_indices_triton[(batch_size,)](
            req_to_token,
            req_pool_indices,
            paged_kernel_lens,
            cum_kv_seq_len,
            None,
            kv_indices,
            req_to_token.size(1),
        )
        return kv_indices, cum_kv_seq_len, qo_indptr, self.custom_mask

    def verify(
        self,
        batch: ScheduleBatch,
        logits_output: LogitsProcessorOutput,
        token_to_kv_pool_allocator: "TokenToKVPoolAllocator",
        page_size: int,
    ) -> MtpVerifyOutput:
        """Greedy chain verification.

        The target prediction for row i validates draft row i+1. Predictions
        are accepted only along the matching prefix; row 0 is always emitted
        as the target bonus token.
        """
        assert batch.sampling_info.is_all_greedy, (
            "MTP speculative decoding currently supports greedy sampling only"
        )
        assert page_size == 1, "MTP speculative decoding requires page_size == 1"

        bs = len(batch.reqs)
        device = logits_output.next_token_logits.device
        candidates = self.draft_token.reshape(bs, self.draft_token_num)
        from sglang.srt import spec_prof

        t_sub = spec_prof.now()
        target_predict = torch.argmax(logits_output.next_token_logits, dim=-1)
        target_predict = target_predict.reshape(bs, self.draft_token_num)

        # BACKPORT-PPU: prefix-chain acceptance for slim depth-one/two MTP.
        # Draft d[i] is accepted iff every earlier
        # proposal matched and d[i] equals the target prediction t[i-1].
        matches = candidates[:, 1:] == target_predict[:, :-1]
        prefix_accept = torch.cumprod(matches.to(torch.int32), dim=1).bool()

        # accept_index rows: [v0 row, accepted draft rows..., -1...]
        row_idx = torch.arange(bs, device=device, dtype=torch.int32)
        row_idx = row_idx * self.draft_token_num
        accept_index = torch.full(
            (bs, self.spec_steps + 1), -1, dtype=torch.int32, device=device
        )
        accept_index[:, 0] = row_idx
        for step in range(self.spec_steps):
            accept_index[:, step + 1] = torch.where(
                prefix_accept[:, step],
                row_idx + step + 1,
                torch.full_like(row_idx, -1),
            )
        accept_length = prefix_accept.sum(dim=1, dtype=torch.int32)
        predict = target_predict.reshape(-1).to(torch.int32)

        if SIMULATE_ACC_LEN:
            accept_index = _generate_simulated_accept_index(
                accept_index=accept_index,
                predict=predict,  # mutable
                accept_length=accept_length,  # mutable
                simulate_acc_len=SIMULATE_ACC_LEN,
                bs=bs,
                spec_steps=self.spec_steps,
            )

        new_accept_index = []
        unfinished_index = []
        # Single GPU->CPU transfer for everything the acceptance loop needs
        # (was: accept_index.tolist() + predict.tolist() + two separate
        # accept_length.tolist() syncs).
        spec_prof.mark("accept_argmax", t_sub)
        t_sub = spec_prof.now()
        packed_cpu = torch.cat([accept_index.view(-1), predict]).tolist()
        spec_prof.mark("accept_d2h", t_sub)
        t_sub = spec_prof.now()
        accept_index_cpu = [
            packed_cpu[i * self.draft_token_num : (i + 1) * self.draft_token_num]
            for i in range(bs)
        ]
        predict_cpu = packed_cpu[bs * self.draft_token_num :]
        accept_length_cpu = []
        has_finished = False

        # Iterate every accepted token and check if req has finished after
        # appending the token; this must be done BEFORE freeing kv cache slots.
        for i, (req, accept_index_row) in enumerate(zip(batch.reqs, accept_index_cpu)):
            new_accept_index_ = []
            for j, idx in enumerate(accept_index_row):
                if idx == -1:
                    break
                id = predict_cpu[idx]
                req.output_ids.append(id)
                req.check_finished()
                if req.finished():
                    has_finished = True
                    # set all tokens after the finished token to -1 and break
                    accept_index[i, j + 1 :] = -1
                    break
                else:
                    new_accept_index_.append(idx)
            # accepted draft count = emitted tokens - 1; for a finished req
            # the finishing token is not in new_accept_index_, which makes
            # the count come out right without the -1.
            accept_length_cpu.append(
                len(new_accept_index_)
                if req.finished()
                else len(new_accept_index_) - 1
            )
            if not req.finished():
                new_accept_index.extend(new_accept_index_)
                unfinished_index.append(i)
            req.spec_verify_ct += 1

        if has_finished:
            accept_length = (accept_index != -1).sum(dim=1) - 1
        spec_prof.mark("accept_loop", t_sub)
        t_sub = spec_prof.now()

        # BACKPORT-PPU (P1 post-verify slimming): bs=1 chain fast path.
        # Accepted rows are always the prefix [0..k] of the 2-row verify
        # batch, so the nonzero/gather/evict-mask chain collapses into
        # prefix slicing with k already known on CPU. Semantics identical
        # to the generic path below (five-field parity required).
        if (
            bs == 1
            and not has_finished
            and os.environ.get("SGLANG_MTP_FAST_POSTVERIFY", "1") == "1"
        ):
            n = accept_length_cpu[0] + 1  # kept tokens: v0 (+ d1 if accepted)
            verified_id = predict[:n]
            if n < self.draft_token_num:
                token_to_kv_pool_allocator.free(batch.out_cache_loc[n:])
            accept_length_all = accept_length.clone()
            batch.out_cache_loc = batch.out_cache_loc[:n]
            assign_req_to_token_pool[(bs,)](
                batch.req_pool_indices,
                batch.req_to_token_pool.req_to_token,
                batch.seq_lens,
                batch.seq_lens + n,
                batch.out_cache_loc,
                batch.req_to_token_pool.req_to_token.shape[1],
                next_power_of_2(bs),
            )
            batch.seq_lens.add_(n)

            draft_input = MtpDraftInput()
            draft_input.hidden_states = self.hidden_states[:n]
            draft_input.verified_id = verified_id
            draft_input.accept_length = accept_length
            draft_input.accept_length_cpu = accept_length_cpu
            draft_input.seq_lens_for_draft_extend = batch.seq_lens
            draft_input.req_pool_indices_for_draft_extend = batch.req_pool_indices

            spec_prof.mark("accept_tail", t_sub)
            return MtpVerifyOutput(
                draft_input=draft_input,
                logits_output=logits_output,
                verified_id=verified_id,
                accept_length_per_req_cpu=accept_length_cpu,
                accept_length=accept_length_all,
                accepted_indices=accept_index[0, :n],
            )

        # Free the KV cache for unaccepted tokens
        accept_index_flat = accept_index[accept_index != -1]
        verified_id = predict[accept_index_flat]
        evict_mask = torch.full_like(self.draft_token, True, dtype=torch.bool)
        evict_mask[accept_index_flat] = False
        token_to_kv_pool_allocator.free(batch.out_cache_loc[evict_mask])

        # Keep a full (all-request) copy for the mamba state commit before
        # any unfinished-request filtering below.
        accept_length_all = accept_length.clone()

        if not has_finished:
            batch.out_cache_loc = batch.out_cache_loc[accept_index_flat]
            assign_req_to_token_pool[(bs,)](
                batch.req_pool_indices,
                batch.req_to_token_pool.req_to_token,
                batch.seq_lens,
                batch.seq_lens + accept_length + 1,
                batch.out_cache_loc,
                batch.req_to_token_pool.req_to_token.shape[1],
                next_power_of_2(bs),
            )
            batch.seq_lens.add_(accept_length + 1)

            draft_input = MtpDraftInput()
            draft_input.hidden_states = self.hidden_states[accept_index_flat]
            draft_input.verified_id = verified_id
            draft_input.accept_length = accept_length
            draft_input.accept_length_cpu = accept_length_cpu
            draft_input.seq_lens_for_draft_extend = batch.seq_lens
            draft_input.req_pool_indices_for_draft_extend = batch.req_pool_indices

            spec_prof.mark("accept_tail", t_sub)
            return MtpVerifyOutput(
                draft_input=draft_input,
                logits_output=logits_output,
                verified_id=verified_id,
                accept_length_per_req_cpu=accept_length_cpu,
                accept_length=accept_length_all,
                accepted_indices=accept_index_flat,
            )
        else:
            assign_req_to_token_pool[(bs,)](
                batch.req_pool_indices,
                batch.req_to_token_pool.req_to_token,
                batch.seq_lens,
                batch.seq_lens + accept_length + 1,
                batch.out_cache_loc[accept_index_flat],
                batch.req_to_token_pool.req_to_token.shape[1],
                next_power_of_2(bs),
            )
            batch.seq_lens.add_(accept_length + 1)

            draft_input = MtpDraftInput()
            if len(new_accept_index) > 0:
                new_accept_index = torch.tensor(new_accept_index, device=device)
                unfinished_index_device = torch.tensor(unfinished_index, device=device)
                draft_input.hidden_states = self.hidden_states[new_accept_index]
                draft_input.verified_id = predict[new_accept_index]
                draft_input.accept_length_cpu = [
                    accept_length_cpu[i] for i in unfinished_index
                ]
                draft_input.accept_length = accept_length[unfinished_index_device]
                draft_input.seq_lens_for_draft_extend = batch.seq_lens[
                    unfinished_index_device
                ]
                draft_input.req_pool_indices_for_draft_extend = batch.req_pool_indices[
                    unfinished_index_device
                ]
            batch.out_cache_loc = batch.out_cache_loc[new_accept_index]

            spec_prof.mark("accept_tail", t_sub)
            return MtpVerifyOutput(
                draft_input=draft_input,
                logits_output=logits_output,
                verified_id=verified_id,
                accept_length_per_req_cpu=accept_length_cpu,
                accept_length=accept_length_all,
                accepted_indices=accept_index_flat,
            )


@triton.jit
def create_extend_spec_info(
    verified_id,
    seq_len,
    accept_len,
    accept_len_cum,
    positions,
    new_verified_id,
    accept_len_upper: tl.constexpr,
):
    pid = tl.program_id(axis=0)
    offset = 0 if pid == 0 else tl.load(accept_len_cum + pid - 1)
    seq_length = tl.load(seq_len + pid)
    accept_length = tl.load(accept_len + pid)
    positions_ptr = positions + offset
    data = tl.arange(0, accept_len_upper)
    mask = data < accept_length
    tl.store(positions_ptr + data, seq_length - accept_length + data, mask)

    offset = tl.load(accept_len_cum + pid) - 1
    verified_id_data = tl.load(verified_id + offset)
    tl.store(new_verified_id + pid, verified_id_data)


@triton.jit
def assign_req_to_token_pool(
    req_pool_indices,
    req_to_token,
    start_offset,
    end_offset,
    out_cache_loc,
    pool_len: tl.constexpr,
    bs_upper: tl.constexpr,
):
    BLOCK_SIZE: tl.constexpr = 32
    pid = tl.program_id(axis=0)
    kv_start = tl.load(start_offset + pid)
    kv_end = tl.load(end_offset + pid)
    token_pool = req_to_token + tl.load(req_pool_indices + pid) * pool_len

    length_offset = tl.arange(0, bs_upper)
    start = tl.load(start_offset + length_offset, mask=length_offset < pid)
    end = tl.load(end_offset + length_offset, mask=length_offset < pid)
    out_offset = tl.sum(end - start, axis=0)

    out_cache_ptr = out_cache_loc + out_offset

    save_offset = tl.arange(0, BLOCK_SIZE) + kv_start
    load_offset = tl.arange(0, BLOCK_SIZE)

    num_loop = tl.cdiv(kv_end - kv_start, BLOCK_SIZE)
    for _ in range(num_loop):
        mask = save_offset < kv_end
        data = tl.load(out_cache_ptr + load_offset, mask=mask)
        tl.store(token_pool + save_offset, data, mask=mask)
        save_offset += BLOCK_SIZE
        load_offset += BLOCK_SIZE


def _generate_simulated_accept_index(
    accept_index,
    predict,
    accept_length,
    simulate_acc_len,
    bs,
    spec_steps,
):
    simulate_acc_len_float = float(simulate_acc_len)
    simulated_values = torch.normal(
        mean=simulate_acc_len_float,
        std=1.0,
        size=(1,),
        device="cpu",
    )
    # clamp simulated values to be between 1 and spec_steps
    simulated_values = torch.clamp(simulated_values, min=1.0, max=spec_steps)
    simulate_acc_len = int(simulated_values.round().item())

    accept_indx_first_col = accept_index[:, 0].view(-1, 1)
    sim_accept_index = torch.full(
        (bs, spec_steps + 1), -1, dtype=torch.int32, device=accept_index.device
    )
    sim_accept_index[:, :simulate_acc_len] = accept_indx_first_col + torch.arange(
        simulate_acc_len, device=accept_index.device
    )
    accept_length.fill_(simulate_acc_len - 1)
    predict.fill_(100)  # some legit token id
    return sim_accept_index
