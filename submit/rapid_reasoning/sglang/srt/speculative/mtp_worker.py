"""MTP (Multi-Token Prediction) self-speculative decoding worker.

Chain-style speculative decoding for Qwen3.5-2B MTP: topk=1, num_steps=1..4,
num_draft_tokens=2..5, greedy sampling, page_size=1.
Ported from the pre-slim ``eagle_worker.py`` with the multi-step draft
decode / tree building / CUDA graph / sampling machinery removed.

Per decode iteration:
  1. draft(): build [v0, d1] directly, or run one draft-decode graph to build
     the depth-two verify chain [v0, d1, d2].
  2. verify(): run the target model in TARGET_VERIFY mode, compare the
     draft token against the target's greedy prediction, emit accepted
     tokens, then commit the accepted-step mamba states.
  3. forward_draft_extend_after_decode(): backfill the draft KV with the
     accepted tokens and capture the next draft proposal.

The production graph path captures draft decode (depth two), target verify,
and accept-keyed draft extend/commit graphs. SGLANG_DISABLE_CUDA_GRAPH=1
falls back to the eager path.
"""
import atexit
import logging
import os
import sys
import time
from types import SimpleNamespace
from typing import List, Optional, Tuple

import torch

from sglang.srt.layers.logits_processor import LogitsProcessorOutput
from sglang.srt.managers.schedule_batch import ScheduleBatch
from sglang.srt.managers.tp_worker import TpModelWorker
from sglang.srt.model_executor.forward_batch_info import (
    CaptureHiddenMode,
    ForwardBatch,
    ForwardMode,
)
from sglang.srt import spec_prof
from sglang.srt.server_args import ServerArgs
from sglang.srt.speculative.mtp_utils import (
    MtpDraftInput,
    MtpVerifyInput,
    MtpVerifyOutput,
    assign_req_to_token_pool,
)
from sglang.srt.speculative.spec_info import SpeculativeAlgorithm
from sglang.srt.utils import empty_context, fast_topk, next_power_of_2

logger = logging.getLogger(__name__)

# The draft model is looked up in the model registry under this architecture
# name (see srt/models/qwen3_5_mtp.py). The target model's config.json names
# the VLM architecture, so we override it for the draft ModelConfig.
MTP_DRAFT_MODEL_OVERRIDE_ARGS = '{"architectures": ["Qwen3_5MTPForCausalLM"]}'

# Investigation-only per-round tracer (SGLANG_ROUND_DEBUG=1), used to A/B the
# joint-head path against the three-runner path round by round. Zero overhead
# when unset.
_ROUND_DEBUG = os.environ.get("SGLANG_ROUND_DEBUG", "0") == "1"


def _round_dbg(tag: str, *fields):
    if _ROUND_DEBUG:
        print("ROUNDDBG", tag, *fields, file=sys.stderr, flush=True)


class MTPWorker(TpModelWorker):

    def __init__(
        self,
        server_args: ServerArgs,
        gpu_id: int,
        tp_rank: int,
        dp_rank: Optional[int],
        nccl_port: int,
        target_worker: TpModelWorker,
    ):
        # Parse arguments
        self.server_args = server_args
        self.topk = server_args.speculative_eagle_topk
        self.speculative_num_steps = server_args.speculative_num_steps
        self.speculative_num_draft_tokens = server_args.speculative_num_draft_tokens
        assert (
            self.topk == 1
            and self.speculative_num_steps in (1, 2, 3, 4)
            and self.speculative_num_draft_tokens
            == self.speculative_num_steps + 1
        ), (
            "MTPWorker only supports chain speculation: "
            f"{self.topk=} {self.speculative_num_steps=} "
            f"{self.speculative_num_draft_tokens=}"
        )
        self._chain2_rounds = 0
        self._chain2_accepted = 0
        self._chain2_first_accepted = 0
        self._chain2_second_accepted = 0
        self._chain2_third_accepted = 0
        self._chain2_fourth_accepted = 0
        self._chain2_stats_enabled = (
            self.speculative_num_steps >= 2
            and os.environ.get("SGLANG_CHAIN2_STATS", "0") == "1"
        )
        if self._chain2_stats_enabled:
            atexit.register(self._print_chain2_stats)
        # Dynamic chain depth (SGLANG_MTP_DYNAMIC_DEPTH=1): keep the joint
        # verify graph at the configured max depth, but choose per round how
        # many draft-decode steps (extra proposals) to run; the chain is
        # padded by repeating the last proposal. Padded rows are verified
        # against target predictions exactly like real proposals, so emitted
        # tokens stay correct. Strictly single-sample: only the speculation
        # length of the one running request changes.
        self._dyn_depth_enabled = (
            self.speculative_num_steps >= 2
            and os.environ.get("SGLANG_MTP_DYNAMIC_DEPTH", "1") == "1"
        )
        self._dyn_alpha = float(os.environ.get("SGLANG_MTP_DYN_ALPHA", "0.25"))
        # Minimum chain steps: 1 keeps the proven static depth=2 behaviour as
        # the floor; depth=1 rounds are never profitable in measurements.
        self._dyn_min_extra = int(os.environ.get("SGLANG_MTP_DYN_MIN_EXTRA", "1"))
        # q[j] = EMA P(accept >= j+1 | d_{j+1} was proposed), j = 1..steps-1.
        # Optimistic init so the controller explores full depth first.
        self._dyn_q = [0.0] + [1.0] * (self.speculative_num_steps - 1)
        self._dyn_step_ms = 0.6  # EMA wall cost per draft-decode step
        self._dyn_token_ms = 2.0  # EMA wall time per emitted token
        self._dyn_round = 0
        self._dyn_last_extra = self.speculative_num_steps - 1
        self._dyn_round_t = None
        self._dyn_extra_hist = [0] * self.speculative_num_steps
        _force = os.environ.get("SGLANG_MTP_FORCE_EXTRA")
        self._dyn_force_extra = int(_force) if _force is not None else None
        self.enable_nan_detection = server_args.enable_nan_detection
        self.gpu_id = gpu_id
        self.device = server_args.device
        self.target_worker = target_worker
        self.page_size = server_args.page_size
        assert self.page_size == 1, "MTPWorker requires page_size == 1"
        self.speculative_algorithm = SpeculativeAlgorithm.from_string(
            server_args.speculative_algorithm
        )

        # Override context length with the target model's context length
        server_args.context_length = target_worker.model_runner.model_config.context_len

        # Do not capture cuda graphs in `super().__init__()`.
        backup_disable_cuda_graph = server_args.disable_cuda_graph
        server_args.disable_cuda_graph = True

        # The draft model registers under its own architecture name.
        backup_model_override_args = server_args.json_model_override_args
        server_args.json_model_override_args = MTP_DRAFT_MODEL_OVERRIDE_ARGS

        # Share the allocator with the target worker.
        # Draft and target worker own their own KV cache pools.
        self.req_to_token_pool, self.token_to_kv_pool_allocator = (
            target_worker.get_memory_pool()
        )

        # Init the draft worker
        with empty_context():
            super().__init__(
                gpu_id=gpu_id,
                tp_rank=tp_rank,
                server_args=server_args,
                nccl_port=nccl_port,
                dp_rank=dp_rank,
                is_draft_worker=True,
                req_to_token_pool=self.req_to_token_pool,
                token_to_kv_pool_allocator=self.token_to_kv_pool_allocator,
            )

        server_args.json_model_override_args = backup_model_override_args
        self.draft_model_runner.server_args.disable_cuda_graph = (
            backup_disable_cuda_graph
        )

        # Share the embedding and lm_head with the target model
        embed, head = self.target_worker.model_runner.model.get_embed_and_head()
        self.draft_model_runner.model.set_embed_and_head(embed, head)

        # Depth one needs no draft-decode forward. Depth two captures one
        # fixed-row draft-decode graph before the verify/extend graph pair.
        self.joint_graph_runner = None
        self.joint_graph_runners = {}
        if not server_args.disable_cuda_graph:
            from sglang.srt.model_executor.cuda_graph_runner import (
                MtpCommitGraphRunner,
                MtpDraftDecodeGraphRunner,
                MtpDraftExtendGraphRunner,
            )

            self.draft_model_runner.cuda_graph_draft_runner = (
                MtpDraftExtendGraphRunner(self.draft_model_runner)
            )
            self.draft_decode_graph_runner = (
                MtpDraftDecodeGraphRunner(self.draft_model_runner)
                if self.speculative_num_steps >= 2
                else None
            )
            # Phase 3: the mamba commit (accepted-step intermediate states ->
            # persistent slots) as two tiny graphs keyed by accept count.
            self.commit_graph_runner = (
                None
                if os.environ.get("T8_NO_COMMIT_GRAPH")
                else MtpCommitGraphRunner(
                    self.target_worker.model_runner.attn_backend,
                    self.target_worker.model_runner.model,
                    self.speculative_num_steps,
                )
            )
            # Joint target-verify plus accept-keyed draft-extend/commit graphs.
            # Replaces the independent verify/commit/extend runners at verify.
            # Default on; SGLANG_JOINT_HEAD=0 falls back to the trio.
            if os.environ.get("SGLANG_JOINT_HEAD", "1") == "1":
                from sglang.srt.model_executor.cuda_graph_runner import (
                    MtpJointGraphRunner,
                )

                if self._dyn_depth_enabled and os.environ.get(
                    "SGLANG_MTP_DYN_MULTI", "0"
                ) == "1":
                    # Multi-runner variant: one joint runner per candidate
                    # chain length. SGLANG_MTP_DYN_GRAPHS="2,4" restricts the
                    # resident set so shallow rounds keep a cheap q_len=3
                    # verify graph while deep rounds use the q_len=5 one;
                    # the chain is padded up to the chosen runner's shape.
                    # NOTE: on this card a full 1..N resident set cost a few
                    # percent on the shallow path even when unused, so the
                    # default dynamic mode remains the single max-depth
                    # runner with a padded chain (see draft()).
                    self.joint_graph_runners = {}
                    graphs_env = os.environ.get("SGLANG_MTP_DYN_GRAPHS")
                    if graphs_env:
                        wanted = sorted(
                            {
                                min(max(int(s), 1), self.speculative_num_steps)
                                for s in graphs_env.split(",")
                                if s.strip()
                            }
                        )
                        # The max-depth runner is the fallback for any chain
                        # longer than the largest requested graph.
                        if self.speculative_num_steps not in wanted:
                            wanted.append(self.speculative_num_steps)
                    else:
                        wanted = list(range(1, self.speculative_num_steps + 1))
                    capture_order = [2] + [s for s in wanted[::-1] if s != 2]
                    for steps in capture_order:
                        self.joint_graph_runners[steps] = MtpJointGraphRunner(
                            self.target_worker.model_runner,
                            self.draft_model_runner,
                            num_tokens=steps + 1,
                        )
                    self.joint_graph_runner = self.joint_graph_runners[
                        max(self.joint_graph_runners)
                    ]
                else:
                    self.joint_graph_runner = MtpJointGraphRunner(
                        self.target_worker.model_runner, self.draft_model_runner
                    )
            # Dynamic depth relies on the joint runner's fixed-shape verify
            # graph (padded chain); without it there is nothing to pad into.
            self._dyn_depth_enabled = (
                self._dyn_depth_enabled and self.joint_graph_runner is not None
            )
        else:
            self.commit_graph_runner = None
            self.draft_decode_graph_runner = None
            self._dyn_depth_enabled = False

        # Capture the target EXTEND graph only after the draft model and all
        # speculative graph runners are fully initialized.  Keeping the draft
        # startup sequence identical to EXTEND_GRAPH=0 prevents graph setup
        # allocations/warmups from changing its first-forward numerics.
        self.target_worker.model_runner.init_extend_cuda_graph()
        # Same deferral for the long-prefill eager warmup.
        self.target_worker.model_runner.init_long_prefill_warmup()

    @property
    def draft_model_runner(self):
        return self.model_runner

    def forward_batch_speculative_generation(
        self, batch: ScheduleBatch
    ) -> Tuple[LogitsProcessorOutput, List[int], int, int]:
        """Run speculative decoding forward.

        NOTE: Many states of the batch are modified as you go through. It is
        not guaranteed that the final output batch has the same state as the
        input.
        """
        if batch.forward_mode.is_decode():
            # SGLANG_DECODE_TRACE=1: torch profiler on the Nth decode step
            # (SGLANG_DECODE_TRACE_STEP, default 20), exporting one chrome
            # trace to SGLANG_DECODE_TRACE_OUT for kernel inspection.
            # Investigation-only knob; zero overhead when unset.
            if os.environ.get("SGLANG_DECODE_TRACE", "0") == "1":
                self._decode_trace_seen = getattr(self, "_decode_trace_seen", 0) + 1
                target_step = int(os.environ.get("SGLANG_DECODE_TRACE_STEP", "20"))
                if self._decode_trace_seen == target_step:
                    from torch.profiler import ProfilerActivity, profile

                    os.environ["SGLANG_DECODE_TRACE"] = "0"
                    torch.cuda.synchronize()
                    with profile(
                        activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA]
                    ) as prof:
                        spec_info = self.draft(batch)
                        logits_output, verify_output, model_worker_batch = (
                            self.verify(batch, spec_info)
                        )
                        if (
                            batch.spec_info.verified_id is not None
                            and self.joint_graph_runner is None
                        ):
                            self.forward_draft_extend_after_decode(batch)
                        torch.cuda.synchronize()
                    out = os.environ.get(
                        "SGLANG_DECODE_TRACE_OUT", "/root/decode_trace.json"
                    )
                    prof.export_chrome_trace(out)
                    logger.info(
                        "DECODETRACE step=%d exported to %s", target_step, out
                    )
                    return (
                        logits_output,
                        verify_output.verified_id,
                        model_worker_batch.bid,
                        sum(verify_output.accept_length_per_req_cpu),
                    )
            # P0 final-profile tooling (sglang/srt/spec_prof.py): env-gated
            # per-round segment timing; near-no-op unless SGLANG_SPEC_PROF=1.
            t_round = spec_prof.round_begin()
            spec_info = self.draft(batch)
            spec_prof.mark("draft_build", t_round)
            logits_output, verify_output, model_worker_batch = self.verify(
                batch, spec_info
            )

            # If it is None, it means all requests are finished
            if (
                batch.spec_info.verified_id is not None
                and self.joint_graph_runner is None
            ):
                t_ext = spec_prof.now()
                self.forward_draft_extend_after_decode(batch)
                spec_prof.mark("draft_extend", t_ext)
            spec_prof.round_end(
                t_round, sum(verify_output.accept_length_per_req_cpu)
            )
            return (
                logits_output,
                verify_output.verified_id,
                model_worker_batch.bid,
                sum(verify_output.accept_length_per_req_cpu),
            )
        elif batch.forward_mode.is_idle():
            model_worker_batch = batch.get_model_worker_batch()
            logits_output, next_token_ids = self.target_worker.forward_batch_generation(
                model_worker_batch
            )
            return logits_output, next_token_ids, model_worker_batch.bid, 0
        else:
            from sglang.srt.ttft_prof import stamp as _ttft_stamp

            logits_output, next_token_ids, bid = self.forward_target_extend(batch)
            _ttft_stamp("tgt_ext_done", rid=batch.reqs[0].rid)
            self.forward_draft_extend(
                batch, logits_output.hidden_states, next_token_ids
            )
            _ttft_stamp("draft_ext_done", rid=batch.reqs[0].rid)
            return logits_output, next_token_ids, bid, 0

    def forward_target_extend(
        self, batch: ScheduleBatch
    ) -> Tuple[LogitsProcessorOutput, List[int], int]:
        """Run the target prefill, capturing full hidden states for the draft."""
        model_worker_batch = batch.get_model_worker_batch()
        model_worker_batch.capture_hidden_mode = CaptureHiddenMode.FULL
        logits_output, next_token_ids = self.target_worker.forward_batch_generation(
            model_worker_batch
        )
        return logits_output, next_token_ids, model_worker_batch.bid

    def draft(self, batch: ScheduleBatch) -> MtpVerifyInput:
        """Build the chain verify batch and optionally produce proposal d2."""
        spec_info = batch.spec_info

        if _ROUND_DEBUG:
            _round_dbg(
                "draft_in",
                batch.seq_lens.tolist(),
                (
                    spec_info.verified_id.tolist()
                    if torch.is_tensor(spec_info.verified_id)
                    else spec_info.verified_id
                ),
                spec_info.topk_index.flatten().tolist(),
            )

        # Accumulate penalty (relaxed version for speculative decoding)
        if batch.sampling_info.penalizer_orchestrator.is_required:
            batch.sampling_info.penalizer_orchestrator.cumulate_output_tokens(
                spec_info.verified_id.to(torch.int64)
            )

        # BACKPORT-PPU: chain depth >= 2 adds fixed-row draft decode steps.
        if self._dyn_depth_enabled:
            self._dyn_round_t = time.perf_counter()
        draft_token_ids = spec_info.topk_index.flatten()
        if self.speculative_num_steps >= 2:
            extra = self.speculative_num_steps - 1
            if self._dyn_depth_enabled:
                extra = self._choose_dynamic_extra()
            self._dyn_last_extra = extra
            if self._dyn_depth_enabled:
                self._dyn_extra_hist[extra] += 1
            if extra > 0:
                t_chain = time.perf_counter() if self._dyn_depth_enabled else 0.0
                draft_token_ids = self._draft_chain_tokens(
                    batch, spec_info, extra
                )
                if self._dyn_depth_enabled:
                    step_ms = (time.perf_counter() - t_chain) * 1e3 / extra
                    self._dyn_step_ms += self._dyn_alpha * (
                        step_ms - self._dyn_step_ms
                    )
            else:
                draft_token_ids = draft_token_ids.reshape(1, 1)
            # Pad the chain to the chosen verify graph's fixed shape by
            # repeating the last proposal: in multi-runner mode pick the
            # smallest captured runner covering the chain, in single-runner
            # mode always the max-depth shape. Padded rows are still verified
            # against target predictions, so emitted tokens remain exact.
            if self.joint_graph_runners:
                needed = extra + 1
                target_len = min(
                    k for k in self.joint_graph_runners if k >= needed
                )
            else:
                target_len = self.speculative_num_steps
            n_pad = target_len - draft_token_ids.shape[1]
            if n_pad > 0:
                draft_token_ids = torch.cat(
                    [
                        draft_token_ids,
                        draft_token_ids[:, -1:].expand(-1, n_pad),
                    ],
                    dim=1,
                )

        return MtpVerifyInput.create_chain(
            verified_id=spec_info.verified_id,
            draft_token_ids=draft_token_ids,
            seq_lens=batch.seq_lens,
        )

    def _choose_dynamic_extra(self) -> int:
        """Pick how many draft-decode steps to run this round.

        A step that produces d_{k+1} only pays off when the probability of
        reaching accept >= k+1 times the wall value of one token exceeds the
        measured step cost. The chain never goes below ``_dyn_min_extra``
        (default 1, i.e. the proven static depth=2 behaviour): depth=1 rounds
        save one draft step but lose more in tokens/round than they save.
        Every 32 rounds probe ONE level deeper than the current choice (not
        full depth): this keeps the acceptance EMA exactly at the decision
        boundary fresh at minimal cost, and avoids the starvation artifact
        where a closed gate stops receiving data and never reopens.
        """
        self._dyn_round += 1
        max_extra = self.speculative_num_steps - 1
        min_extra = min(self._dyn_min_extra, max_extra)
        # A/B hook: pin the chain length to isolate per-depth graph cost.
        if self._dyn_force_extra is not None:
            return min(self._dyn_force_extra, max_extra)
        # Sequential gating: step j (proposing d_{j+1}) only pays off when
        # P(accept >= j+1) x token value exceeds the measured step cost, and
        # deeper steps are unreachable once a shallower one is skipped.
        extra = 0
        for j in range(1, max_extra + 1):
            if self._dyn_q[j] * self._dyn_token_ms > self._dyn_step_ms:
                extra = j
            else:
                break
        if extra < min_extra:
            extra = min_extra
        if self._dyn_round % 32 == 0:
            extra = min(extra + 1, max_extra)
        return extra

    def _update_dynamic_stats(self, accept: int):
        """EMA updates after verify: acceptance indicators (only for chain
        positions that carried real proposals) and per-token wall time."""
        a = self._dyn_alpha
        for j in range(1, self._dyn_last_extra + 1):
            self._dyn_q[j] += a * (float(accept >= j + 1) - self._dyn_q[j])
        if self._dyn_round_t is not None:
            round_ms = (time.perf_counter() - self._dyn_round_t) * 1e3
            # Round trips are a few ms; larger gaps mean a prefill/scheduler
            # boundary, not a speculative round.
            if 0.0 < round_ms < 15.0:
                token_ms = round_ms / (accept + 1)
                self._dyn_token_ms += a * (token_ms - self._dyn_token_ms)
            self._dyn_round_t = None
        if self._chain2_stats_enabled and self._dyn_round % 20 == 0:
            print(
                "DYNDEPTH "
                f"rounds={self._dyn_round} extra_hist={self._dyn_extra_hist} "
                f"q={[round(v, 4) for v in self._dyn_q[1:]]} "
                f"step_ms={self._dyn_step_ms:.4f} "
                f"token_ms={self._dyn_token_ms:.4f}",
                file=sys.stderr,
                flush=True,
            )

    def _draft_chain_tokens(
        self, batch: ScheduleBatch, draft_input: MtpDraftInput, extra: int
    ) -> torch.Tensor:
        """Run ``extra`` temporary draft-decode steps for d2..d_{extra+1}.

        Each step consumes the previous proposal and its carried hidden
        state, writing one temporary draft KV row.  The temporary draft KV
        slots are returned to the shared allocator after the forwards,
        exactly as in the pre-slim EAGLE multi-step path.  Target verify
        immediately overwrites the req-to-token entries with its own fixed
        (num_steps + 1)-row allocation.
        """
        bs = batch.batch_size()
        out_cache_loc, allocator_state = batch.alloc_token_slots(
            bs * extra, backup_state=True
        )
        assign_req_to_token_pool[(bs,)](
            batch.req_pool_indices,
            batch.req_to_token_pool.req_to_token,
            batch.seq_lens,
            batch.seq_lens + extra,
            out_cache_loc,
            batch.req_to_token_pool.req_to_token.shape[1],
            next_power_of_2(bs),
        )

        d1 = draft_input.topk_index.flatten().to(torch.int64)
        draft_input.capture_hidden_mode = CaptureHiddenMode.LAST
        tokens = [d1]
        prev_token = d1
        prev_hidden = draft_input.hidden_states
        seq_lens_backup = batch.seq_lens
        try:
            for step in range(extra):
                slot = out_cache_loc[step * bs : (step + 1) * bs]
                batch.input_ids = prev_token
                batch.out_cache_loc = slot
                # Step k decodes at position seq_len + k and must attend over
                # the temporary rows written by steps 0..k-1.
                step_seq_lens = seq_lens_backup + step
                draft_input.positions = step_seq_lens.to(torch.int64)
                draft_input.hidden_states = prev_hidden
                # The graph replay reads the proposal from topk_index, so it
                # must be refreshed with the previous step's output.
                draft_input.topk_index = prev_token.reshape(bs, 1)
                if self.draft_decode_graph_runner is not None:
                    shim = SimpleNamespace(
                        req_pool_indices=batch.req_pool_indices,
                        seq_lens=step_seq_lens,
                        seq_lens_sum=batch.seq_lens_sum + step,
                        reqs=batch.reqs,
                    )
                    prev_token, prev_hidden = (
                        self.draft_decode_graph_runner.replay(
                            shim, draft_input, slot
                        )
                    )
                else:
                    batch.seq_lens = step_seq_lens
                    model_worker_batch = batch.get_model_worker_batch()
                    forward_batch = ForwardBatch.init_new(
                        model_worker_batch, self.draft_model_runner
                    )
                    logits_output = self.draft_model_runner.forward(
                        forward_batch
                    )
                    self._detect_nan_if_needed(logits_output)
                    prev_token = torch.argmax(
                        logits_output.next_token_logits, dim=-1, keepdim=True
                    ).flatten()
                    prev_hidden = logits_output.hidden_states
                # The graph path returns fixed output buffers that the next
                # replay overwrites; snapshot the token for the chain.
                tokens.append(prev_token.clone())
        finally:
            batch.seq_lens = seq_lens_backup
            self.token_to_kv_pool_allocator.restore_state(allocator_state)
        return torch.stack(tokens, dim=1)

    def verify(self, batch: ScheduleBatch, spec_info: MtpVerifyInput):
        if self.joint_graph_runner is not None and len(batch.reqs) == 1:
            return self._verify_joint(batch, spec_info)
        t_seg = spec_prof.now()
        spec_info.prepare_for_verify(batch, self.page_size)
        batch.forward_mode = ForwardMode.TARGET_VERIFY
        batch.spec_info = spec_info
        model_worker_batch = batch.get_model_worker_batch()
        spec_prof.mark("verify_meta", t_seg)
        t_seg = spec_prof.now()
        logits_output, _ = self.target_worker.forward_batch_generation(
            model_worker_batch, skip_sample=True
        )
        spec_prof.mark("target_verify", t_seg)
        self._detect_nan_if_needed(logits_output)
        spec_info.hidden_states = logits_output.hidden_states
        t_seg = spec_prof.now()
        res: MtpVerifyOutput = spec_info.verify(
            batch,
            logits_output,
            self.token_to_kv_pool_allocator,
            self.page_size,
        )
        spec_prof.mark("accept", t_seg)

        if self._chain2_stats_enabled:
            self._record_chain2_stats(res.accept_length_per_req_cpu)

        # Commit the mamba states of the accepted steps into the persistent
        # cache slots. Must run after acceptance is known and before the
        # draft extend below (which reads the committed states).
        t_seg = spec_prof.now()
        if self.commit_graph_runner is not None and len(batch.reqs) == 1:
            # bs=1 chain only: the commit graph reads the verify graph's
            # fixed state-index buffer, which is valid only when the verify
            # forward went through MtpTargetVerifyGraphRunner (bs=1). The
            # accept count is already on the CPU.
            self.commit_graph_runner.replay(res.accept_length_per_req_cpu[0])
        else:
            self.target_worker.model_runner.attn_backend.update_mamba_state_after_mtp_verify(
                res.accept_length, None, None, self.target_worker.model_runner.model
            )
        spec_prof.mark("commit", t_seg)

        # Prepare the batch for the next draft forwards.
        batch.forward_mode = ForwardMode.DECODE
        batch.spec_info = res.draft_input

        if _ROUND_DEBUG:
            _round_dbg(
                "verify_out",
                spec_info.draft_token.tolist(),
                res.verified_id.tolist(),
                res.accept_length_per_req_cpu,
            )
        return logits_output, res, model_worker_batch

    def _print_chain2_stats(self):
        if self._chain2_rounds == 0:
            return
        first_rate = self._chain2_first_accepted / self._chain2_rounds
        second_rate = self._chain2_second_accepted / self._chain2_rounds
        second_conditional = (
            self._chain2_second_accepted / self._chain2_first_accepted
            if self._chain2_first_accepted
            else 0.0
        )
        third_rate = self._chain2_third_accepted / self._chain2_rounds
        third_conditional = (
            self._chain2_third_accepted / self._chain2_second_accepted
            if self._chain2_second_accepted
            else 0.0
        )
        fourth_rate = self._chain2_fourth_accepted / self._chain2_rounds
        fourth_conditional = (
            self._chain2_fourth_accepted / self._chain2_third_accepted
            if self._chain2_third_accepted
            else 0.0
        )
        print(
            "CHAIN2STATS "
            f"rounds={self._chain2_rounds} "
            f"tokens_per_round="
            f"{1 + self._chain2_accepted / self._chain2_rounds:.4f} "
            f"first_accept_rate={first_rate:.4f} "
            f"second_accept_rate={second_rate:.4f} "
            f"second_accept_conditional={second_conditional:.4f} "
            f"third_accept_rate={third_rate:.4f} "
            f"third_accept_conditional={third_conditional:.4f} "
            f"fourth_accept_rate={fourth_rate:.4f} "
            f"fourth_accept_conditional={fourth_conditional:.4f}",
            file=sys.stderr,
            flush=True,
        )

    def _record_chain2_stats(self, accept_lengths):
        self._chain2_rounds += len(accept_lengths)
        self._chain2_accepted += sum(accept_lengths)
        self._chain2_first_accepted += sum(value >= 1 for value in accept_lengths)
        self._chain2_second_accepted += sum(value >= 2 for value in accept_lengths)
        self._chain2_third_accepted += sum(value >= 3 for value in accept_lengths)
        self._chain2_fourth_accepted += sum(value >= 4 for value in accept_lengths)
        if self._chain2_rounds % 20 == 0:
            self._print_chain2_stats()

    def _verify_joint(self, batch: ScheduleBatch, spec_info: MtpVerifyInput):
        """P3-B joint-graph verify: two graph replays (verify half, then
        draft half) cover the target verify forward, both LM-head
        projections, the acceptance ops and the mamba commit; only the
        acceptance bookkeeping stays on the host.

        The emitted tokens and every batch/spec_info state update are kept
        identical to MtpVerifyInput.verify()'s bs=1 paths (five-field parity
        is required against the default three-runner path).
        """
        t_seg = spec_prof.now()
        spec_info.prepare_for_verify(batch, self.page_size)
        batch.forward_mode = ForwardMode.TARGET_VERIFY
        batch.spec_info = spec_info
        model_worker_batch = batch.get_model_worker_batch()
        spec_prof.mark("verify_meta", t_seg)

        if self.joint_graph_runners:
            # Dynamic depth: the chain length chosen in draft() selects the
            # matching fixed-shape joint runner.
            runner = self.joint_graph_runners[spec_info.draft_token_num - 1]
        else:
            runner = self.joint_graph_runner
        t_seg = spec_prof.now()
        predictions, accept = runner.replay(batch, spec_info)
        if self._chain2_stats_enabled:
            self._record_chain2_stats([accept])
        if self._dyn_depth_enabled:
            self._update_dynamic_stats(accept)
        spec_prof.mark("target_verify", t_seg)

        logits_output = LogitsProcessorOutput(
            next_token_logits=runner.verify_logits,
            hidden_states=runner.hidden_verify,
        )
        self._detect_nan_if_needed(logits_output)

        # One packed D2H for the round: [predictions..., accept]. It is issued between
        # the two graph launches, so it only waits for the verify half; the
        # draft half (graph2) executes while the host does the bookkeeping
        # below. proposal/new_verified_id are consumed from graph2's fixed
        # output buffers (aliased into draft_input below, no host read).
        t_seg = spec_prof.now()

        # Emit the target bonus token and every accepted draft-prefix row.
        req = batch.reqs[0]
        emitted = 0
        for token_id in predictions[: accept + 1]:
            req.output_ids.append(token_id)
            req.check_finished()
            emitted += 1
            if req.finished():
                break
        req.spec_verify_ct += 1
        spec_prof.mark("accept", t_seg)
        t_seg = spec_prof.now()

        bs = 1
        verified_id = runner.predict32[:emitted]
        if not req.finished():
            # Same prefix-slice bookkeeping as MtpVerifyInput.verify().
            n = accept + 1
            if n < runner.num_tokens:
                self.token_to_kv_pool_allocator.free(batch.out_cache_loc[n:])
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

            # The next round's draft state. The draft body and the proposal
            # already ran inside the joint graph, so this is pure aliasing of
            # the graph's fixed output buffers (consumed by next round's
            # draft() before the buffers are overwritten by its replay).
            draft_input = MtpDraftInput()
            draft_input.topk_index = runner.proposal32.view(1, 1)
            draft_input.topk_p = torch.ones_like(
                draft_input.topk_index, dtype=torch.float32
            )
            draft_input.hidden_states = runner.draft_row
            draft_input.verified_id = runner.new_verified32
            runner.accept_length.fill_(accept)
            draft_input.accept_length = runner.accept_length
            draft_input.accept_length_cpu = [accept]
            draft_input.seq_lens_for_draft_extend = batch.seq_lens
            draft_input.req_pool_indices_for_draft_extend = batch.req_pool_indices
            accept_length_per_req_cpu = [accept]
            accepted_indices = runner.row_indices[:n]
            # Fidelity with the old post-verify state: prepare_extend_after_decode
            # leaves batch.input_ids holding the accepted predictions.
            batch.input_ids = runner.predict32[:n]
        else:
            # The in-graph commit used the raw accept count. This is harmless
            # for a finished request because its state slot is released.
            add = emitted
            keep = emitted
            if keep < runner.num_tokens:
                self.token_to_kv_pool_allocator.free(batch.out_cache_loc[keep:])
            assign_req_to_token_pool[(bs,)](
                batch.req_pool_indices,
                batch.req_to_token_pool.req_to_token,
                batch.seq_lens,
                batch.seq_lens + add,
                batch.out_cache_loc[:keep],
                batch.req_to_token_pool.req_to_token.shape[1],
                next_power_of_2(bs),
            )
            batch.seq_lens.add_(add)
            batch.out_cache_loc = batch.out_cache_loc[:keep]
            draft_input = MtpDraftInput()
            accept_length_per_req_cpu = [emitted - 1]
            accepted_indices = runner.row_indices[:emitted]

        # Prepare the batch for the next draft forwards.
        batch.forward_mode = ForwardMode.DECODE
        batch.spec_info = draft_input
        spec_prof.mark("accept_tail", t_seg)

        if _ROUND_DEBUG:
            _round_dbg(
                "verify_out",
                spec_info.draft_token.tolist(),
                verified_id.tolist(),
                accept_length_per_req_cpu,
            )

        res = MtpVerifyOutput(
            draft_input=draft_input,
            logits_output=logits_output,
            verified_id=verified_id,
            accept_length_per_req_cpu=accept_length_per_req_cpu,
            # The mamba commit already ran inside the graph; this field is
            # kept for interface parity (raw GPU accept, as in the old
            # non-finished path).
            accept_length=runner.accept,
            accepted_indices=accepted_indices,
        )
        return logits_output, res, model_worker_batch

    def forward_draft_extend(
        self,
        batch: ScheduleBatch,
        hidden_states: torch.Tensor,
        next_token_ids: List[int],
    ):
        """Run the draft model prefill after the target prefill.

        This API modifies the states of the batch.
        """
        batch.spec_info = MtpDraftInput(
            hidden_states=hidden_states,
            verified_id=next_token_ids,
        )
        batch.spec_info.prepare_for_extend(batch)
        batch.spec_info.capture_hidden_mode = CaptureHiddenMode.LAST
        model_worker_batch = batch.get_model_worker_batch()
        forward_batch = ForwardBatch.init_new(
            model_worker_batch, self.draft_model_runner
        )
        forward_batch.return_logprob = False
        logits_output = self.draft_model_runner.forward(forward_batch)
        self._detect_nan_if_needed(logits_output)
        assert forward_batch.spec_info is batch.spec_info
        self.capture_for_decode(logits_output, forward_batch.spec_info)

    def forward_draft_extend_after_decode(self, batch: ScheduleBatch):
        t_sub = spec_prof.now()
        # Backup fields that will be modified in-place
        seq_lens_backup = batch.seq_lens.clone()
        req_pool_indices_backup = batch.req_pool_indices
        accept_length_backup = batch.spec_info.accept_length
        return_logprob_backup = batch.return_logprob

        # Prepare metadata
        batch.forward_mode = ForwardMode.DRAFT_EXTEND
        batch.spec_info.prepare_extend_after_decode(
            batch,
            self.speculative_num_steps,
        )
        batch.spec_info.capture_hidden_mode = CaptureHiddenMode.LAST
        batch.return_logprob = False
        spec_prof.mark("ext_prep", t_sub)
        t_sub = spec_prof.now()

        # BACKPORT-PPU (P1 post-verify slimming): bs=1 graph replay fast
        # path. The generic get_model_worker_batch + ForwardBatch.init_new
        # detour rebuilds extend metadata (2 H2D copies + compute_position)
        # that the captured graph never reads; feed the fixed-shape replay
        # shim directly instead. Semantics identical (graph inputs are the
        # same tensors); set SGLANG_MTP_FAST_POSTVERIFY=0 to fall back.
        runner = self.draft_model_runner.cuda_graph_draft_runner
        n = batch.input_ids.shape[0]
        if (
            runner is not None
            and len(batch.reqs) == 1
            and n in runner.graphs
            and os.environ.get("SGLANG_MTP_FAST_POSTVERIFY", "1") == "1"
        ):
            shim = SimpleNamespace(
                input_ids=batch.input_ids,
                req_pool_indices=batch.req_pool_indices,
                seq_lens=batch.seq_lens,
                out_cache_loc=batch.out_cache_loc,
                positions=batch.spec_info.positions,
                mrope_positions=None,
                mm_inputs=[batch.reqs[0].multimodal_inputs],
                spec_info=batch.spec_info,
                seq_lens_sum=batch.seq_lens_sum,
                seq_lens_cpu=None,
            )
            spec_prof.mark("ext_meta", t_sub)
            t_sub = spec_prof.now()
            logits_output = runner.replay(shim)
            spec_prof.mark("ext_replay", t_sub)
            t_sub = spec_prof.now()
            self._detect_nan_if_needed(logits_output)
            self.capture_for_decode(logits_output, batch.spec_info)
            spec_prof.mark("ext_capture", t_sub)
        else:
            model_worker_batch = batch.get_model_worker_batch()
            forward_batch = ForwardBatch.init_new(
                model_worker_batch, self.draft_model_runner
            )
            spec_prof.mark("ext_meta", t_sub)
            t_sub = spec_prof.now()

            # Run
            logits_output = self.draft_model_runner.forward(forward_batch)
            spec_prof.mark("ext_replay", t_sub)
            t_sub = spec_prof.now()
            self._detect_nan_if_needed(logits_output)
            self.capture_for_decode(logits_output, forward_batch.spec_info)
            spec_prof.mark("ext_capture", t_sub)

        # Restore backup.
        batch.forward_mode = ForwardMode.DECODE
        batch.seq_lens = seq_lens_backup
        batch.req_pool_indices = req_pool_indices_backup
        batch.spec_info.accept_length = accept_length_backup
        batch.return_logprob = return_logprob_backup

    def capture_for_decode(
        self, logits_output: LogitsProcessorOutput, draft_input: MtpDraftInput
    ):
        # BACKPORT-PPU (SGLang 0.5.13 #26235): chain/topk=1 never consumes
        # draft probabilities. Argmax(logits) is identical to top1(softmax)
        # and avoids a full-vocabulary softmax on every draft step.
        if self.topk == 1:
            draft_input.topk_index = torch.argmax(
                logits_output.next_token_logits, dim=-1, keepdim=True
            )
            draft_input.topk_p = torch.ones_like(
                draft_input.topk_index, dtype=torch.float32
            )
        else:
            probs = torch.softmax(logits_output.next_token_logits, dim=-1)
            draft_input.topk_p, draft_input.topk_index = fast_topk(
                probs, self.topk, dim=-1
            )
        draft_input.hidden_states = logits_output.hidden_states

    def _detect_nan_if_needed(self, logits_output: LogitsProcessorOutput):
        if self.enable_nan_detection:
            logits = logits_output.next_token_logits
            if torch.any(torch.isnan(logits)):
                logger.error("Detected errors during sampling! NaN in the logits.")
                raise ValueError("Detected errors during sampling! NaN in the logits.")
