from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

import torch
import triton
import triton.language as tl

from sglang.srt.layers.attention.base_attn_backend import AttentionBackend
from sglang.srt.layers.attention.utils import create_flashinfer_kv_indices_triton
from sglang.srt.layers.dp_attention import get_attention_tp_size
from sglang.srt.layers.radix_attention import AttentionType
from sglang.srt.model_executor.forward_batch_info import ForwardBatch, ForwardMode
from sglang.srt.utils import get_bool_env_var, get_device_core_count

if TYPE_CHECKING:
    from sglang.srt.layers.radix_attention import RadixAttention
    from sglang.srt.model_executor.model_runner import ModelRunner

# SLIM: removed speculative decoding TYPE_CHECKING import (fixed Qwen3.5-2B
# config: no speculative decoding)

# FLASH-ATTN: optional PPU flash_attn 2.5.6 fast path for full-attention
# layers. Disabled by default — measured no speedup on the MMBench workload
# (short prompts, 6/24 full-attention layers), so the default behavior is
# byte-identical to the pure-triton build. Enable with
# SGLANG_ENABLE_FLASH_ATTN=1. Unavailable/unsupported cases fall back to the
# triton kernels.
flash_attn_varlen_func = None
if get_bool_env_var("SGLANG_ENABLE_FLASH_ATTN"):
    try:
        from flash_attn import flash_attn_varlen_func
    except ImportError:
        pass


@triton.jit
def get_num_kv_splits_triton(
    num_kv_splits_ptr,
    seq_lens_ptr,
    num_seq,
    num_group,
    num_head,
    num_kv_head,
    max_kv_splits,
    device_core_count,
    MAX_NUM_SEQ: tl.constexpr,
):
    # TODO: this method is tunable, we need more online serving data to tune it
    offs_seq = tl.arange(0, MAX_NUM_SEQ)
    mask_seq = offs_seq < num_seq

    seq_lens = tl.load(seq_lens_ptr + offs_seq, mask=mask_seq, other=0)
    max_seq_len = tl.max(seq_lens)
    seq_lens = tl.load(seq_lens_ptr + offs_seq, mask=mask_seq, other=max_seq_len)
    min_seq_len = tl.min(seq_lens)
    if max_seq_len * 8 < min_seq_len * 10:
        min_seq_len = max_seq_len
    max_kv_splits_1 = tl.minimum(tl.cdiv(max_seq_len, min_seq_len), max_kv_splits)
    kv_chunk_size_1 = tl.cdiv(max_seq_len, max_kv_splits_1)

    # NOTE: this is a hack to let num_kv_split grows up with seqlen gradually
    ext_seq_len = tl.cast(max_seq_len, tl.float32) / 64.0
    ext_device_core_count = tl.cast(
        device_core_count * tl.maximum(tl.log2(ext_seq_len), 1.0), tl.int32
    )
    block_h, num_kv_group = 16, num_head // num_kv_head
    if num_kv_group == 1:
        token_grid = num_seq * num_group * num_head
    else:
        # from triton_ops/decode_attention.py:_decode_grouped_att_m_fwd
        block_h = tl.minimum(block_h, num_kv_group)
        token_grid = num_seq * num_group * tl.cdiv(num_head, block_h)
    max_kv_splits_2 = tl.minimum(
        tl.cdiv(ext_device_core_count, token_grid), max_kv_splits
    )
    kv_chunk_size_2 = tl.cdiv(max_seq_len, max_kv_splits_2)

    num_kv_splits = tl.maximum(
        tl.cdiv(seq_lens, kv_chunk_size_1), tl.cdiv(seq_lens, kv_chunk_size_2)
    )

    offs_token = offs_seq * num_group
    mask_token = offs_token < num_seq * num_group
    for i in range(0, num_group):
        tl.store(num_kv_splits_ptr + i + offs_token, num_kv_splits, mask=mask_token)


@dataclass
class ForwardMetadata:
    attn_logits: torch.Tensor
    attn_lse: torch.Tensor
    max_extend_len: int
    num_kv_splits: torch.Tensor
    kv_indptr: torch.Tensor
    kv_indices: torch.Tensor
    qo_indptr: torch.Tensor
    custom_mask: torch.Tensor
    mask_indptr: torch.Tensor
    # FLASH-ATTN: metadata for the flash_attn_varlen_func fast path.
    # fa_kv_indices / fa_cu_seqlens_k cover the full KV (prefix + new tokens);
    # fa_max_seqlen_k is the max full KV length in the batch.
    fa_kv_indices: Optional[torch.Tensor] = None
    fa_cu_seqlens_k: Optional[torch.Tensor] = None
    fa_max_seqlen_k: int = 0


class TritonAttnBackend(AttentionBackend):
    def __init__(
        self,
        model_runner: ModelRunner,
        skip_prefill: bool = False,
        kv_indptr_buf: Optional[torch.Tensor] = None,
    ):
        # Lazy import to avoid the initialization of cuda context
        from sglang.srt.layers.attention.triton_ops.decode_attention import (
            decode_attention_fwd,
        )
        from sglang.srt.layers.attention.triton_ops.extend_attention import (
            extend_attention_fwd,
        )

        super().__init__()

        self.decode_attention_fwd = decode_attention_fwd
        self.extend_attention_fwd = extend_attention_fwd

        self.skip_prefill = skip_prefill

        max_bs = model_runner.req_to_token_pool.size

        if kv_indptr_buf is None:
            self.kv_indptr = torch.zeros(
                (max_bs + 1,), dtype=torch.int32, device=model_runner.device
            )
        else:
            self.kv_indptr = kv_indptr_buf

        self.req_to_token = model_runner.req_to_token_pool.req_to_token

        if not self.skip_prefill:
            self.qo_indptr = torch.zeros(
                (max_bs + 1,), dtype=torch.int32, device=model_runner.device
            )

            self.mask_indptr = torch.zeros(
                (max_bs + 1,), dtype=torch.int64, device=model_runner.device
            )

        # Speculative decoding (MTP): number of draft tokens per verify step.
        # None when speculative decoding is disabled.
        self.num_draft_tokens = model_runner.server_args.speculative_num_draft_tokens

        self.num_head = (
            model_runner.model_config.num_attention_heads // get_attention_tp_size()
        )
        self.num_kv_head = model_runner.model_config.get_num_kv_heads(
            get_attention_tp_size()
        )

        self.static_kv_splits = get_bool_env_var(
            "SGLANG_TRITON_DECODE_ATTN_STATIC_KV_SPLITS", "false"
        )
        self.max_kv_splits = model_runner.server_args.triton_attention_num_kv_splits
        # BACKPORT: for hybrid linear models, layer_id = 0 may not be full
        # attention (from sglang v0.5.9).
        if model_runner.hybrid_gdn_config is not None:
            self.v_head_dim = model_runner.token_to_kv_pool.get_v_head_dim()
        else:
            self.v_head_dim = model_runner.token_to_kv_pool.get_value_buffer(0).shape[-1]

        self.forward_metadata: ForwardMetadata = None

        self.max_context_len = model_runner.model_config.context_len

        self.device = model_runner.device
        self.device_core_count = get_device_core_count(model_runner.gpu_id)

    def get_num_kv_splits(
        self,
        num_kv_splits: torch.Tensor,
        seq_lens: torch.Tensor,
    ):
        num_token, num_seq = num_kv_splits.shape[0], seq_lens.shape[0]
        num_group = num_token // num_seq

        assert (
            num_group * num_seq == num_token
        ), f"num_seq({num_seq}), num_token({num_token}), something goes wrong!"

        if self.static_kv_splits or self.device_core_count <= 0:
            num_kv_splits.fill_(self.max_kv_splits)
            return

        if num_seq < 256:
            SCHEDULE_SEQ = 256
        else:
            SCHEDULE_SEQ = triton.next_power_of_2(num_seq)

        get_num_kv_splits_triton[(1,)](
            num_kv_splits,
            seq_lens,
            num_seq,
            num_group,
            self.num_head,
            self.num_kv_head,
            self.max_kv_splits,
            self.device_core_count,
            MAX_NUM_SEQ=SCHEDULE_SEQ,
        )

    def init_forward_metadata(self, forward_batch: ForwardBatch):
        """Init auxiliary variables for triton attention backend."""

        spec_info = forward_batch.spec_info
        bs = forward_batch.batch_size
        kv_indptr = self.kv_indptr

        if forward_batch.forward_mode.is_decode_or_idle():
            kv_indptr[1 : bs + 1] = torch.cumsum(forward_batch.seq_lens, dim=0)
            kv_indptr = kv_indptr[: bs + 1]
            kv_indices = torch.empty(
                forward_batch.seq_lens_sum, dtype=torch.int32, device=self.device
            )
            create_flashinfer_kv_indices_triton[(bs,)](
                self.req_to_token,
                forward_batch.req_pool_indices,
                forward_batch.seq_lens,
                kv_indptr,
                None,
                kv_indices,
                self.req_to_token.stride(0),
            )

            attn_logits = torch.empty(
                (bs, self.num_head, self.max_kv_splits, self.v_head_dim),
                dtype=torch.float32,
                device=self.device,
            )
            attn_lse = torch.empty(
                (bs, self.num_head, self.max_kv_splits),
                dtype=torch.float32,
                device=self.device,
            )
            num_kv_splits = torch.empty((bs,), dtype=torch.int32, device=self.device)

            self.get_num_kv_splits(num_kv_splits, forward_batch.seq_lens)

            qo_indptr = None
            custom_mask = None
            mask_indptr = None
            max_extend_len = None

            # FLASH-ATTN: decode uses the triton kernel (the per-step O(seqlen)
            # gather outweighed the flash_attn gain); no FA metadata needed.
            fa_kv_indices = None
            fa_cu_seqlens_k = None
            fa_max_seqlen_k = 0
        elif forward_batch.forward_mode.is_target_verify():
            # MTP: verify [v0, d1] per request. kv_indices covers the prefix
            # only (seq_lens does not include the draft tokens here); the
            # draft tokens are the extend queries.
            bs = len(forward_batch.req_pool_indices)
            qo_indptr = torch.arange(
                0,
                (1 + bs) * self.num_draft_tokens,
                step=self.num_draft_tokens,
                dtype=torch.int32,
                device=self.device,
            )
            # Different from the flashinfer kv_indptr/kv_indices construction
            kv_indptr[1 : bs + 1] = torch.cumsum(forward_batch.seq_lens, dim=0)
            kv_indptr = kv_indptr[: bs + 1]
            kv_indices = torch.empty(
                forward_batch.seq_lens_sum, dtype=torch.int32, device=self.device
            )
            create_flashinfer_kv_indices_triton[(bs,)](
                self.req_to_token,
                forward_batch.req_pool_indices,
                forward_batch.seq_lens,
                kv_indptr,
                None,
                kv_indices,
                self.req_to_token.stride(0),
            )

            custom_mask = spec_info.custom_mask
            seq_mask_len = self.num_draft_tokens * (
                forward_batch.seq_lens + self.num_draft_tokens
            )
            mask_indptr = self.mask_indptr
            mask_indptr[1 : bs + 1] = torch.cumsum(seq_mask_len[:bs], dim=0)
            mask_indptr = mask_indptr[: bs + 1]
            max_extend_len = self.num_draft_tokens
            num_kv_splits = None
            attn_logits = None
            attn_lse = None
            fa_kv_indices = None
            fa_cu_seqlens_k = None
            fa_max_seqlen_k = 0
        elif forward_batch.forward_mode.is_draft_extend():
            # MTP: backfill the draft KV with the accepted tokens.
            # spec_info.generate_attn_arg_prefill returns prefix-only
            # kv_indices (triton extend-kernel convention).
            kv_indices, kv_indptr, qo_indptr, custom_mask = (
                spec_info.generate_attn_arg_prefill(
                    forward_batch.req_pool_indices,
                    forward_batch.seq_lens,
                    None,
                    self.req_to_token,
                )
            )
            mask_indptr = None
            max_extend_len = torch.max(spec_info.accept_length).item()
            num_kv_splits = None
            attn_logits = None
            attn_lse = None
            fa_kv_indices = None
            fa_cu_seqlens_k = None
            fa_max_seqlen_k = 0
        else:
            kv_indptr[1 : bs + 1] = torch.cumsum(
                forward_batch.extend_prefix_lens, dim=0
            )
            kv_indptr = kv_indptr[: bs + 1]
            kv_indices = torch.empty(
                forward_batch.extend_prefix_lens.sum().item(),
                dtype=torch.int32,
                device=self.device,
            )
            create_flashinfer_kv_indices_triton[(bs,)](
                self.req_to_token,
                forward_batch.req_pool_indices,
                forward_batch.extend_prefix_lens,
                kv_indptr,
                None,
                kv_indices,
                self.req_to_token.stride(0),
            )

            qo_indptr = self.qo_indptr
            qo_indptr[1 : bs + 1] = torch.cumsum(forward_batch.extend_seq_lens, dim=0)
            qo_indptr = qo_indptr[: bs + 1]
            custom_mask = None
            mask_indptr = None
            attn_logits = None
            attn_lse = None
            max_extend_len = torch.max(forward_batch.extend_seq_lens).item()
            num_kv_splits = None

            # FLASH-ATTN: with radix cache disabled the common case is
            # prefix_len == 0 for every sequence (pure prefill), so the full
            # KV is exactly the extend tokens themselves — mark this so
            # forward_extend can skip the pool gather entirely. Only build
            # the metadata when the FA path is enabled.
            fa_kv_indices = None
            fa_cu_seqlens_k = None
            fa_max_seqlen_k = 0
            if flash_attn_varlen_func is None:
                pass
            elif kv_indices.numel() == 0:
                fa_cu_seqlens_k = qo_indptr
                fa_max_seqlen_k = max_extend_len
            else:
                # Chunked prefill: build gather indices for the full KV
                # (prefix + extend tokens). req_to_token rows already contain
                # the newly allocated token slots, so a single index build
                # with the full lengths covers both parts.
                fa_kv_lens = (
                    forward_batch.extend_prefix_lens + forward_batch.extend_seq_lens
                )
                fa_cu_seqlens_k = torch.zeros(
                    (bs + 1,), dtype=torch.int32, device=self.device
                )
                fa_cu_seqlens_k[1:] = torch.cumsum(fa_kv_lens, dim=0).to(torch.int32)
                fa_kv_indices = torch.empty(
                    fa_kv_lens.sum().item(), dtype=torch.int32, device=self.device
                )
                create_flashinfer_kv_indices_triton[(bs,)](
                    self.req_to_token,
                    forward_batch.req_pool_indices,
                    fa_kv_lens,
                    fa_cu_seqlens_k,
                    None,
                    fa_kv_indices,
                    self.req_to_token.stride(0),
                )
                fa_max_seqlen_k = fa_kv_lens.max().item()

        self.forward_metadata = ForwardMetadata(
            attn_logits,
            attn_lse,
            max_extend_len,
            num_kv_splits,
            kv_indptr,
            kv_indices,
            qo_indptr,
            custom_mask,
            mask_indptr,
            # FLASH-ATTN:
            fa_kv_indices,
            fa_cu_seqlens_k,
            fa_max_seqlen_k,
        )

    # BACKPORT-PPU: restored init_cuda_graph_state /
    # init_forward_metadata_capture_cuda_graph /
    # init_forward_metadata_replay_cuda_graph /
    # get_cuda_graph_seq_len_fill_value. Decode-only originally; MTP phase 2
    # adds TARGET_VERIFY (fixed 2 tokens, prefix-only kv) and DRAFT_EXTEND
    # (fixed 1/2 tokens, prefix-only kv) branches for the chain-MTP graphs.

    def init_cuda_graph_state(self, max_bs: int, max_num_tokens: int = None):
        self.cuda_graph_attn_logits = torch.zeros(
            (max_bs, self.num_head, self.max_kv_splits, self.v_head_dim),
            dtype=torch.float32,
            device=self.device,
        )
        self.cuda_graph_attn_lse = torch.zeros(
            (max_bs, self.num_head, self.max_kv_splits),
            dtype=torch.float32,
            device=self.device,
        )
        self.cuda_graph_num_kv_splits = torch.full(
            (max_bs,), self.max_kv_splits, dtype=torch.int32, device=self.device
        )
        self.cuda_graph_kv_indices = torch.zeros(
            (max_bs * self.max_context_len),
            dtype=torch.int32,
            device=self.device,
        )

    def init_forward_metadata_capture_cuda_graph(
        self,
        bs: int,
        num_tokens: int,
        req_pool_indices: torch.Tensor,
        seq_lens: torch.Tensor,
        encoder_lens: Optional[torch.Tensor],
        forward_mode: ForwardMode,
        spec_info,
    ):
        assert encoder_lens is None, "Not supported"
        if forward_mode.is_decode_or_idle():
            kv_indptr = self.kv_indptr
            kv_indptr[1 : bs + 1] = torch.cumsum(seq_lens, dim=0)
            kv_indptr = kv_indptr[: bs + 1]
            kv_indices = self.cuda_graph_kv_indices
            create_flashinfer_kv_indices_triton[(bs,)](
                self.req_to_token,
                req_pool_indices,
                seq_lens,
                kv_indptr,
                None,
                kv_indices,
                self.req_to_token.stride(0),
            )

            self.forward_metadata = ForwardMetadata(
                self.cuda_graph_attn_logits,
                self.cuda_graph_attn_lse,
                None,
                self.cuda_graph_num_kv_splits,
                kv_indptr,
                kv_indices,
                None,
                None,
                None,
            )
            return

        # SGLANG_EXTEND_GRAPH: plain EXTEND (prefill) bucket graph. The
        # request is padded to num_tokens as real + pad + empty segments;
        # qo_indptr content is refreshed on
        # every replay, the prefix is always empty (radix cache / chunked
        # prefill are disabled for hybrid GDN models), so kv_indptr stays
        # [0, 0] and kv_indices stays empty. max_extend_len is baked to the
        # bucket size; the triton extend kernel masks by qo_indptr content.
        if forward_mode == ForwardMode.EXTEND:
            if getattr(self, "_graph_extend_qo_indptr", None) is None:
                self._graph_extend_qo_indptr = torch.zeros(
                    (4,), dtype=torch.int32, device=self.device
                )
                self._graph_extend_kv_indptr = torch.zeros(
                    (4,), dtype=torch.int32, device=self.device
                )
                self._graph_extend_kv_indices = torch.empty(
                    (0,), dtype=torch.int32, device=self.device
                )
            # seq_lens carries the capture-time extend length in its first
            # (and only) slot.
            self._graph_extend_qo_indptr[1:2].copy_(seq_lens[:1])
            self._graph_extend_qo_indptr[2] = num_tokens
            self._graph_extend_qo_indptr[3] = num_tokens
            self.forward_metadata = ForwardMetadata(
                attn_logits=None,
                attn_lse=None,
                max_extend_len=num_tokens,
                num_kv_splits=None,
                kv_indptr=self._graph_extend_kv_indptr,
                kv_indices=self._graph_extend_kv_indices,
                qo_indptr=self._graph_extend_qo_indptr,
                custom_mask=None,
                mask_indptr=None,
            )
            return

        # MTP phase 2: speculative capture modes (bs=1 chain).
        assert bs == 1, f"speculative cuda graph capture is bs=1 only, got {bs=}"
        if forward_mode.is_target_verify():
            num_draft = self.num_draft_tokens
            qo_indptr = getattr(self, "_graph_verify_qo_indptr", None)
            if qo_indptr is None:
                qo_indptr = torch.arange(
                    0,
                    (bs + 1) * num_draft,
                    step=num_draft,
                    dtype=torch.int32,
                    device=self.device,
                )
                self._graph_verify_qo_indptr = qo_indptr
            max_extend_len = num_draft
            prefix_lens = seq_lens[:bs]
        else:
            assert forward_mode.is_draft_extend(), (
                f"Invalid forward mode: {forward_mode=} for CUDA Graph capture."
            )
            # qo_indptr is a per-graph constant, so each token count gets its
            # own fixed buffer (the two graphs must not share it).
            num_tokens_per_req = num_tokens // bs
            qo_indptr_map = getattr(self, "_graph_draft_qo_indptr", None)
            if qo_indptr_map is None:
                qo_indptr_map = {}
                self._graph_draft_qo_indptr = qo_indptr_map
            qo_indptr = qo_indptr_map.get(num_tokens_per_req)
            if qo_indptr is None:
                qo_indptr = torch.arange(
                    0,
                    (bs + 1) * num_tokens_per_req,
                    step=num_tokens_per_req,
                    dtype=torch.int32,
                    device=self.device,
                )
                qo_indptr_map[num_tokens_per_req] = qo_indptr
            max_extend_len = num_tokens_per_req
            # seq_lens carries the post-accept lengths; kv covers the prefix
            # only (triton extend-kernel convention).
            prefix_lens = (seq_lens[:bs] - num_tokens_per_req).clamp(min=0)

        kv_indptr = self.kv_indptr
        kv_indptr[1 : bs + 1] = torch.cumsum(prefix_lens, dim=0)
        kv_indptr = kv_indptr[: bs + 1]
        kv_indices = self.cuda_graph_kv_indices
        create_flashinfer_kv_indices_triton[(bs,)](
            self.req_to_token,
            req_pool_indices,
            prefix_lens,
            kv_indptr,
            None,
            kv_indices,
            self.req_to_token.stride(0),
        )

        self.forward_metadata = ForwardMetadata(
            None,
            None,
            max_extend_len,
            None,
            kv_indptr,
            kv_indices,
            qo_indptr,
            None,
            None,
        )

    def init_forward_metadata_replay_cuda_graph(
        self,
        bs: int,
        req_pool_indices: torch.Tensor,
        seq_lens: torch.Tensor,
        seq_lens_sum: int,
        encoder_lens: Optional[torch.Tensor],
        forward_mode: ForwardMode,
        spec_info,
        seq_lens_cpu: Optional[torch.Tensor] = None,
    ):
        if forward_mode.is_decode_or_idle():
            # Recompute kv_indptr / kv_indices / num_kv_splits into the
            # fixed-address buffers outside the graph; the captured decode
            # kernels read these buffers at replay time.
            kv_indptr = self.kv_indptr
            kv_indptr[1 : bs + 1] = torch.cumsum(seq_lens[:bs], dim=0)
            kv_indptr = kv_indptr[: bs + 1]
            kv_indices = self.cuda_graph_kv_indices
            create_flashinfer_kv_indices_triton[(bs,)](
                self.req_to_token,
                req_pool_indices[:bs],
                seq_lens[:bs],
                kv_indptr,
                None,
                kv_indices,
                self.req_to_token.stride(0),
            )
            num_kv_splits = self.cuda_graph_num_kv_splits
            self.get_num_kv_splits(num_kv_splits[:bs], seq_lens[:bs])
            return

        # SGLANG_EXTEND_GRAPH: EXTEND replay — only the real/pad split point
        # (qo_indptr[1]) changes here; the runner restores the selected bucket
        # end because all bucket graphs share this fixed-address tensor. The
        # kv prefix is always empty and max_extend_len is baked at capture.
        if forward_mode == ForwardMode.EXTEND:
            self._graph_extend_qo_indptr[1:2].copy_(seq_lens[:1])
            return

        # MTP phase 2: rewrite the kv prefix segment of the fixed buffers.
        # qo_indptr / max_extend_len are per-graph constants baked at
        # capture; the metadata object is not re-read during replay.
        if forward_mode.is_target_verify():
            prefix_lens = seq_lens[:bs]
        else:
            assert forward_mode.is_draft_extend(), (
                f"Invalid forward mode: {forward_mode=} for CUDA Graph replay."
            )
            num_tokens_per_req = spec_info.accept_length_cpu[0]
            prefix_lens = (seq_lens[:bs] - num_tokens_per_req).clamp(min=0)

        kv_indptr = self.kv_indptr
        kv_indptr[1 : bs + 1] = torch.cumsum(prefix_lens, dim=0)
        kv_indptr = kv_indptr[: bs + 1]
        kv_indices = self.cuda_graph_kv_indices
        create_flashinfer_kv_indices_triton[(bs,)](
            self.req_to_token,
            req_pool_indices[:bs],
            prefix_lens,
            kv_indptr,
            None,
            kv_indices,
            self.req_to_token.stride(0),
        )

    def get_cuda_graph_seq_len_fill_value(self):
        return 1

    # FLASH-ATTN: the flash_attn 2.5.6 fast path cannot handle softcap
    # (no softcap arg), sliding-window attention, or head_dim > 256; those
    # layers keep using the triton kernels.
    def _flash_attn_supported(self, layer: RadixAttention) -> bool:
        return (
            flash_attn_varlen_func is not None
            and layer.logit_cap == 0.0
            and (layer.sliding_window_size is None or layer.sliding_window_size == -1)
            and layer.qk_head_dim <= 256
            and layer.v_head_dim <= 256
        )

    def forward_extend(
        self,
        q: torch.Tensor,
        k: torch.Tensor,
        v: torch.Tensor,
        layer: RadixAttention,
        forward_batch: ForwardBatch,
        save_kv_cache=True,
    ):
        # TODO: reuse the buffer across layers
        if layer.qk_head_dim != layer.v_head_dim:
            o = q.new_empty((q.shape[0], layer.tp_q_head_num * layer.v_head_dim))
        else:
            o = torch.empty_like(q)

        if save_kv_cache:
            forward_batch.token_to_kv_pool.set_kv_buffer(
                layer, forward_batch.out_cache_loc, k, v
            )

        causal = True
        if layer.attn_type == AttentionType.ENCODER_ONLY:
            causal = False

        # FLASH-ATTN: two fast paths, both bottom-right causal (matches
        # extend: q holds the last extend_len tokens of each sequence).
        # - fa_kv_indices is None  => every sequence has prefix_len == 0, the
        #   full KV is exactly k/v themselves; no pool gather at all.
        # - otherwise (chunked prefill) => gather prefix + new tokens (the
        #   latter written by set_kv_buffer above) from the pool.
        # Speculative modes (target_verify / draft_extend) keep the triton
        # kernels: their kv/extend bookkeeping differs from plain extend.
        if (
            self._flash_attn_supported(layer)
            and save_kv_cache
            and self.forward_metadata.custom_mask is None
            and not forward_batch.forward_mode.is_target_verify()
            and not forward_batch.forward_mode.is_draft_extend()
            and q.shape[0] > 0
        ):
            if self.forward_metadata.fa_kv_indices is None:
                k_full = k.contiguous()
                v_full = v.contiguous()
            else:
                k_full = forward_batch.token_to_kv_pool.get_key_buffer(
                    layer.layer_id
                )[self.forward_metadata.fa_kv_indices]
                v_full = forward_batch.token_to_kv_pool.get_value_buffer(
                    layer.layer_id
                )[self.forward_metadata.fa_kv_indices]
            o3 = flash_attn_varlen_func(
                q.view(-1, layer.tp_q_head_num, layer.qk_head_dim),
                k_full,
                v_full,
                self.forward_metadata.qo_indptr,
                self.forward_metadata.fa_cu_seqlens_k,
                self.forward_metadata.max_extend_len,
                self.forward_metadata.fa_max_seqlen_k,
                softmax_scale=layer.scaling,
                causal=causal,
            )
            return o3.view(-1, layer.tp_q_head_num * layer.v_head_dim)

        self.extend_attention_fwd(
            q.view(-1, layer.tp_q_head_num, layer.qk_head_dim),
            k.contiguous(),
            v.contiguous(),
            o.view(-1, layer.tp_q_head_num, layer.v_head_dim),
            forward_batch.token_to_kv_pool.get_key_buffer(layer.layer_id),
            forward_batch.token_to_kv_pool.get_value_buffer(layer.layer_id),
            self.forward_metadata.qo_indptr,
            self.forward_metadata.kv_indptr,
            self.forward_metadata.kv_indices,
            self.forward_metadata.custom_mask,
            causal,
            self.forward_metadata.mask_indptr,
            self.forward_metadata.max_extend_len,
            layer.scaling,
            layer.logit_cap,
        )
        return o

    def forward_decode(
        self,
        q: torch.Tensor,
        k: torch.Tensor,
        v: torch.Tensor,
        layer: RadixAttention,
        forward_batch: ForwardBatch,
        save_kv_cache=True,
    ):
        # During torch.compile, there is a bug in rotary_emb that causes the
        # output value to have a 3D tensor shape. This reshapes the output correctly.
        q = q.reshape(-1, layer.tp_q_head_num * layer.qk_head_dim)

        # TODO: reuse the buffer across layers
        if layer.qk_head_dim != layer.v_head_dim:
            o = q.new_empty((q.shape[0], layer.tp_q_head_num * layer.v_head_dim))
        else:
            o = torch.empty_like(q)

        if save_kv_cache:
            forward_batch.token_to_kv_pool.set_kv_buffer(
                layer, forward_batch.out_cache_loc, k, v
            )

        # FLASH-ATTN: no flash_attn fast path for decode — the per-step
        # O(seqlen) pool gather outweighed the kernel gain, so decode always
        # uses the triton split-K kernel below.
        self.decode_attention_fwd(
            q.view(-1, layer.tp_q_head_num, layer.qk_head_dim),
            forward_batch.token_to_kv_pool.get_key_buffer(layer.layer_id),
            forward_batch.token_to_kv_pool.get_value_buffer(layer.layer_id),
            o.view(-1, layer.tp_q_head_num, layer.v_head_dim),
            self.forward_metadata.kv_indptr,
            self.forward_metadata.kv_indices,
            self.forward_metadata.attn_logits,
            self.forward_metadata.attn_lse,
            self.forward_metadata.num_kv_splits,
            self.max_kv_splits,
            layer.scaling,
            layer.logit_cap,
        )
        return o

# SLIM: removed TritonMultiStepDraftBackend (fixed Qwen3.5-2B config: no speculative decoding)
