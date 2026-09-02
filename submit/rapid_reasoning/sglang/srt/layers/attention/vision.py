from __future__ import annotations

from functools import lru_cache
from typing import Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from einops import rearrange

from sglang.srt.distributed import parallel_state
from sglang.srt.distributed import utils as dist_utils
from sglang.srt.layers.attention.triton_ops.prefill_attention import (
    context_attention_fwd,
)
from sglang.srt.layers.linear import (
    ColumnParallelLinear,
    QKVParallelLinear,
    RowParallelLinear,
)
from sglang.srt.layers.quantization import QuantizationConfig
from sglang.srt.layers.rotary_embedding import apply_rotary_pos_emb
from sglang.srt.utils import add_prefix, get_bool_env_var, is_cuda

_is_cuda = is_cuda()

if _is_cuda:
    import triton
    import triton.language as tl


# Qwen3-VL supplies half-width cos/sin to every ViT block. The compatibility
# path used to materialize cos/sin twice and then execute the generic eager
# rotary sequence independently for q and k. Fuse it into one graph-safe
# launch per block.
_FUSED_VIT_ROPE = get_bool_env_var("SGLANG_FUSED_VIT_ROPE", default="true")
_FUSED_VIT_QKV_ROPE = get_bool_env_var(
    "SGLANG_FUSED_VIT_QKV_ROPE", default="true"
)

if _is_cuda:

    # Keep the eager path's two FP32 multiplies and one FP32 add as separate
    # rounding points. A plain Triton expression is contracted to FMA on PPU
    # and changes a few BF16 outputs by one ULP on real vision inputs.
    @triton.jit
    def _ppu_mul_f32(a, b):
        return tl.inline_asm_elementwise(
            "mul.rn.f32 $0, $1, $2;",
            "=f,f,f",
            [a, b],
            dtype=tl.float32,
            is_pure=True,
            pack=1,
        )

    @triton.jit
    def _ppu_add_f32(a, b):
        return tl.inline_asm_elementwise(
            "add.rn.f32 $0, $1, $2;",
            "=f,f,f",
            [a, b],
            dtype=tl.float32,
            is_pure=True,
            pack=1,
        )

    @triton.jit
    def _fused_vit_rope_kernel(
        q,
        k,
        q_out,
        k_out,
        cos,
        sin,
        num_heads: tl.constexpr,
        head_dim: tl.constexpr,
        half_dim: tl.constexpr,
        BLOCK: tl.constexpr,
    ):
        token = tl.program_id(0)
        head = tl.program_id(1)
        offs = tl.arange(0, BLOCK)
        mask = offs < head_dim
        partner = tl.where(offs < half_dim, offs + half_dim, offs - half_dim)
        rope_offs = offs % half_dim

        row = (token * num_heads + head) * head_dim
        qv = tl.load(q + row + offs, mask=mask).to(tl.float32)
        kv = tl.load(k + row + offs, mask=mask).to(tl.float32)
        qr = tl.load(q + row + partner, mask=mask).to(tl.float32)
        kr = tl.load(k + row + partner, mask=mask).to(tl.float32)
        c = tl.load(cos + token * half_dim + rope_offs, mask=mask).to(tl.float32)
        s = tl.load(sin + token * half_dim + rope_offs, mask=mask).to(tl.float32)
        qr = tl.where(offs < half_dim, -qr, qr)
        kr = tl.where(offs < half_dim, -kr, kr)
        q_result = _ppu_add_f32(_ppu_mul_f32(qv, c), _ppu_mul_f32(qr, s))
        k_result = _ppu_add_f32(_ppu_mul_f32(kv, c), _ppu_mul_f32(kr, s))

        tl.store(q_out + row + offs, q_result, mask=mask)
        tl.store(k_out + row + offs, k_result, mask=mask)

    @triton.jit
    def _fused_vit_qkv_rope_kernel(
        qkv,
        q_out,
        k_out,
        v_out,
        cos,
        sin,
        num_heads: tl.constexpr,
        head_dim: tl.constexpr,
        half_dim: tl.constexpr,
        BLOCK: tl.constexpr,
    ):
        """Split packed QKV and apply Q/K RoPE in one graph-safe launch."""
        token = tl.program_id(0)
        head = tl.program_id(1)
        offs = tl.arange(0, BLOCK)
        mask = offs < head_dim
        partner = tl.where(offs < half_dim, offs + half_dim, offs - half_dim)
        rope_offs = offs % half_dim

        packed_dim = num_heads * head_dim
        packed_row = token * 3 * packed_dim
        head_row = head * head_dim
        out_row = (token * num_heads + head) * head_dim
        q_base = packed_row + head_row
        k_base = q_base + packed_dim
        v_base = k_base + packed_dim

        qv = tl.load(qkv + q_base + offs, mask=mask).to(tl.float32)
        kv = tl.load(qkv + k_base + offs, mask=mask).to(tl.float32)
        qr = tl.load(qkv + q_base + partner, mask=mask).to(tl.float32)
        kr = tl.load(qkv + k_base + partner, mask=mask).to(tl.float32)
        vv = tl.load(qkv + v_base + offs, mask=mask)
        c = tl.load(cos + token * half_dim + rope_offs, mask=mask).to(tl.float32)
        s = tl.load(sin + token * half_dim + rope_offs, mask=mask).to(tl.float32)
        qr = tl.where(offs < half_dim, -qr, qr)
        kr = tl.where(offs < half_dim, -kr, kr)
        q_result = _ppu_add_f32(_ppu_mul_f32(qv, c), _ppu_mul_f32(qr, s))
        k_result = _ppu_add_f32(_ppu_mul_f32(kv, c), _ppu_mul_f32(kr, s))

        tl.store(q_out + out_row + offs, q_result, mask=mask)
        tl.store(k_out + out_row + offs, k_result, mask=mask)
        tl.store(v_out + out_row + offs, vv, mask=mask)


def _fused_vit_rope(
    q: torch.Tensor,
    k: torch.Tensor,
    cos: torch.Tensor,
    sin: torch.Tensor,
) -> Optional[Tuple[torch.Tensor, torch.Tensor]]:
    if not (
        _FUSED_VIT_ROPE
        and _is_cuda
        and q.is_cuda
        and k.is_cuda
        and q.is_contiguous()
        and k.is_contiguous()
        and cos.is_contiguous()
        and sin.is_contiguous()
        and q.shape == k.shape
        and cos.shape == sin.shape
        and q.ndim == 3
        and cos.ndim == 2
        and cos.shape[0] == q.shape[0]
        and cos.shape[1] * 2 == q.shape[2]
    ):
        return None

    num_tokens, num_heads, head_dim = q.shape
    # Do not write q/k in place: the PPU compiler can schedule partner loads
    # after stores from another lane in the same rotate-half row.
    q_out = torch.empty_like(q)
    k_out = torch.empty_like(k)
    _fused_vit_rope_kernel[(num_tokens, num_heads)](
        q,
        k,
        q_out,
        k_out,
        cos,
        sin,
        num_heads=num_heads,
        head_dim=head_dim,
        half_dim=head_dim // 2,
        BLOCK=triton.next_power_of_2(head_dim),
    )
    return q_out, k_out


def _fused_vit_qkv_rope(
    qkv: torch.Tensor,
    cos: torch.Tensor,
    sin: torch.Tensor,
    num_heads: int,
) -> Optional[Tuple[torch.Tensor, torch.Tensor, torch.Tensor]]:
    """Fuse the three strided QKV copies with Q/K rotary embedding."""
    if not (
        _FUSED_VIT_QKV_ROPE
        and _FUSED_VIT_ROPE
        and _is_cuda
        and qkv.is_cuda
        and qkv.dtype == torch.bfloat16
        and qkv.is_contiguous()
        and cos.is_contiguous()
        and sin.is_contiguous()
        and qkv.ndim == 3
        and qkv.shape[2] % (3 * num_heads) == 0
        and cos.shape == sin.shape
        and cos.ndim == 2
        and cos.shape[0] == qkv.shape[0] * qkv.shape[1]
    ):
        return None

    num_tokens = qkv.shape[0] * qkv.shape[1]
    head_dim = qkv.shape[2] // (3 * num_heads)
    if cos.shape[1] * 2 != head_dim:
        return None
    out_shape = (num_tokens, num_heads, head_dim)
    q_out = torch.empty(out_shape, dtype=qkv.dtype, device=qkv.device)
    k_out = torch.empty_like(q_out)
    v_out = torch.empty_like(q_out)
    _fused_vit_qkv_rope_kernel[(num_tokens, num_heads)](
        qkv,
        q_out,
        k_out,
        v_out,
        cos,
        sin,
        num_heads=num_heads,
        head_dim=head_dim,
        half_dim=head_dim // 2,
        BLOCK=triton.next_power_of_2(head_dim),
    )
    return q_out, k_out, v_out


# FLASH-ATTN: optional PPU flash_attn 2.5.6 fast path for the ViT
# (varlen, non-causal). Disabled by default (no measured speedup on the
# MMBench workload); enable with SGLANG_ENABLE_FLASH_ATTN=1. Falls back to
# the triton kernel when unavailable.
flash_attn_varlen_func = None
if get_bool_env_var("SGLANG_ENABLE_FLASH_ATTN"):
    try:
        from flash_attn import flash_attn_varlen_func
    except ImportError:
        pass


class VisionAttention(nn.Module):
    r"""
        Multi-headed attention without any cache, mostly used for ViT.


    Args:
        use_qkv_parallel (bool, optional): If True, use QKV-parallel attention.
        use_context_forward (bool, default to True):
            if ``True``, a flash_attn style attention will be applied
            Otherwise, a full-sequence attention will be applied.
        softmax_in_single_precision (bool, default to False):
            if ``True``, the softmax will be performed in single-precision
            Otherwise, it will be performed in half-precision

    """

    def __init__(
        self,
        embed_dim: int,
        num_heads: int,
        projection_size: int,
        use_qkv_parallel: bool,
        quant_config: Optional[QuantizationConfig] = None,
        dropout: float = 0.0,
        use_context_forward: bool = True,
        softmax_in_single_precision: bool = False,
        flatten_batch: bool = False,
        prefix: str = "",
        # BACKPORT: kwargs added for v0.5.9 qwen3_vl compatibility. DP
        # attention is unsupported on the 0.4.6 PPU base; the flags are
        # accepted and must stay False.
        proj_bias: bool = True,
        use_data_parallel: bool = False,
        use_dp_attention_reduce: bool = False,
        **kwargs,
    ):
        super().__init__()
        assert not use_data_parallel and not use_dp_attention_reduce
        self.use_context_forward = use_context_forward
        world_size = parallel_state.get_tensor_model_parallel_world_size()
        self.dropout = dropout
        self.head_size = embed_dim // num_heads
        self.hidden_size_per_attention_head = dist_utils.divide(
            projection_size, num_heads
        )
        self.num_attention_heads_per_partition = dist_utils.divide(
            num_heads, world_size
        )

        if self.use_context_forward:
            self.qkv_backend = VisionTritonAttention()
        else:
            self.qkv_backend = VisionSdpaAttention(
                head_size=self.head_size,
                dropout=dropout,
                flatten_batch=flatten_batch,
                softmax_in_single_precision=softmax_in_single_precision,
            )

        self.use_qkv_parallel = use_qkv_parallel
        if use_qkv_parallel:
            self.qkv_proj = QKVParallelLinear(
                hidden_size=embed_dim,
                head_size=self.head_size,
                total_num_heads=num_heads,
                quant_config=quant_config,
                prefix=add_prefix("qkv_proj", prefix),
            )
        else:
            self.qkv_proj = ColumnParallelLinear(
                input_size=embed_dim,
                output_size=3 * projection_size,
                quant_config=quant_config,
                prefix=add_prefix("qkv_proj", prefix),
            )
        self.proj = RowParallelLinear(
            input_size=embed_dim,
            output_size=embed_dim,
            bias=proj_bias,
            quant_config=quant_config,
            prefix=add_prefix("proj", prefix),
        )

    def forward(
        self,
        x: torch.Tensor,
        cu_seqlens: Optional[torch.Tensor] = None,
        position_embeddings: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,
        attention_mask: Optional[torch.Tensor] = None,
        # BACKPORT: v0.5.9 call convention used by qwen3_vl; output_ws is a
        # cuda-graph workspace and is ignored in eager mode.
        rotary_pos_emb_cos: Optional[torch.Tensor] = None,
        rotary_pos_emb_sin: Optional[torch.Tensor] = None,
        output_ws: Optional[torch.Tensor] = None,
        **kwargs,
    ) -> torch.Tensor:
        r"""
        Args:
            x: [b, s, embed_dim]
            cu_seqlens: [b]
        Returns:
             [s, b, head * head_size]
        """
        bsz, s, _ = x.shape
        head = self.num_attention_heads_per_partition
        # BACKPORT-PPU: Qwen3-VL supplies rotary tensors separately. Resolve
        # them before splitting QKV so the PPU fast path can combine all four
        # memory-bound operations in one launch.
        if position_embeddings is None and rotary_pos_emb_cos is not None:
            position_embeddings = (rotary_pos_emb_cos, rotary_pos_emb_sin)
        fused_qkv_rope_done = False
        if self.use_qkv_parallel:
            # [b, s, embed_dim] --> [b, s, embed_dim]
            qkv, _ = self.qkv_proj(x)
            fused_qkv = None
            if position_embeddings is not None:
                fused_qkv = _fused_vit_qkv_rope(
                    qkv, position_embeddings[0], position_embeddings[1], head
                )
            if fused_qkv is not None:
                q, k, v = fused_qkv
                fused_qkv_rope_done = True
            else:
                q, k, v = qkv.chunk(3, dim=-1)

                # [b, s, embed_dim] --> [b * s, head, head_size]
                q, k, v = [
                    x.reshape(bsz * s, head, -1).contiguous() for x in (q, k, v)
                ]
        else:
            # [b, s, embed_dim] --> [s, b, embed_dim]
            x = rearrange(x, "b s ... -> s b ...")
            # [s, b, embed_dim] --> [s, b, head * 3 * head_size]
            qkv, _ = self.qkv_proj(x)
            # [s, b, head * 3 * head_size] --> [s, b, head, 3 * head_size]
            new_x_shape = qkv.size()[:-1] + (
                head,
                3 * self.hidden_size_per_attention_head,
            )
            qkv = qkv.view(*new_x_shape)

            # [s, b, head, 3 * head_size] --> 3 [s, b, head, head_size]
            q, k, v = dist_utils.split_tensor_along_last_dim(qkv, 3)

            # [s, b, head, head_size] --> [b, s, head, head_size]
            q, k, v = [
                rearrange(x, "s b ... -> b s ...").contiguous() for x in (q, k, v)
            ]

        if position_embeddings is not None and not fused_qkv_rope_done:
            cos, sin = position_embeddings
            original_shape = q.shape
            # [total_tokens, head, head_size]
            q = q.view(-1, head, self.head_size)
            k = k.view(-1, head, self.head_size)

            # Qwen3-VL supplies half-dim cos/sin. Keep the generic path for
            # other vision models and unsupported layouts.
            fused_qk = _fused_vit_rope(q, k, cos, sin)
            if fused_qk is None:
                if cos.size(-1) * 2 == self.head_size:
                    cos = torch.cat([cos, cos], dim=-1)
                    sin = torch.cat([sin, sin], dim=-1)
                q, k = apply_rotary_pos_emb(q, k, cos, sin)
            else:
                q, k = fused_qk

            q = q.view(original_shape)
            k = k.view(original_shape)

        if self.use_qkv_parallel:
            pass
        else:
            # [b, s, head, head_size] --> [b * s, head, head_size]
            q, k, v = [rearrange(x, "b s ... -> (b s) ...") for x in [q, k, v]]

        # BACKPORT: in ViT cuda-graph mode (v0.5.9 idiom) the graph runner
        # passes a pre-allocated output workspace and list-form cu_seqlens
        # through to the triton backend.
        if output_ws is not None:
            output = self.qkv_backend.forward(
                q, k, v, bsz, cu_seqlens, attention_mask, output_ws=output_ws
            )
        else:
            output = self.qkv_backend.forward(q, k, v, bsz, cu_seqlens, attention_mask)

        if self.use_qkv_parallel:
            # [b * s, h, head_size] --> [b, s, h * head_size]
            output = rearrange(output, "(b s) ... h d -> b s ... (h d)", b=bsz)

            # [b, s, h * head_size] --> [b, s, h * head_size]
            output, _ = self.proj(output)
        else:
            # [b * s, h, head_size] --> [s, b, h * head_size]
            context_layer = rearrange(
                output, "(b s) h d -> s b (h d)", b=bsz, s=s
            ).contiguous()

            # [s, b, h * head_size] --> [s, b, h * head_size]
            output, _ = self.proj(context_layer)

            # [s, b, h * head_size] --> [b, s, h * head_size]
            output = output.view(bsz, s, -1)

        return output


class VisionSdpaAttention(nn.Module):
    r"""
    Scaled Dot Product Attention inner product

    """

    def __init__(
        self,
        head_size: int,
        dropout: float = 0.0,
        flatten_batch: bool = False,
        softmax_in_single_precision: bool = False,
    ):
        super().__init__()
        self.head_size = head_size
        self.flatten_batch = flatten_batch
        self.softmax_in_single_precision = softmax_in_single_precision
        self.dropout = dropout

    @staticmethod
    @lru_cache(maxsize=128)
    def _generate_mask_cache(
        s: int, flatten_batch: bool, cu_seqlens: tuple
    ) -> torch.BoolTensor:
        """
        Generate a boolean attention mask with caching mechanism.
        Args:
            s: sequence length
            flatten_batch: whether to flatten batch dimension
            cu_seqlens: tuple of cumulative sequence lengths
        Returns:
            attention mask tensor
        """
        if flatten_batch:
            mask = torch.zeros([1, s, s], dtype=torch.bool)
            for i in range(1, len(cu_seqlens)):
                start = cu_seqlens[i - 1]
                end = cu_seqlens[i]
                mask[..., start:end, start:end] = True
        else:
            # [1, 1, 1, s]
            row_indices = torch.arange(s).view(1, 1, 1, s)
            # [1, 1, s, 1]
            col_indices = torch.arange(s).view(1, 1, s, 1)
            # [b, 1, 1, 1]
            seq_lens = torch.tensor(
                [end - start for start, end in zip(cu_seqlens[:-1], cu_seqlens[1:])],
            ).view(-1, 1, 1, 1)

            mask = (row_indices < seq_lens) & (col_indices < seq_lens)

        return mask

    def generate_patch_attention_mask(
        self,
        s: int,
        cu_seqlens: Optional[torch.Tensor],
        flatten_batch: bool = False,
    ) -> Optional[torch.Tensor]:
        r"""
        Creates a non-causal 4D mask of shape `(b, 1, s, s)` or `(1, 1, s, s)`.
        Args:
            s: sequence length
            cu_seqlens: cumulative sequence lengths tensor. If not, returns an empty mask
            flatten_batch: whether to flatten batch dimension
        Returns:
            attention mask tensor or None
        """
        if cu_seqlens is None:
            return None

        cu_seqlens_tuple = tuple(cu_seqlens.cpu().tolist())

        return self._generate_mask_cache(s, flatten_batch, cu_seqlens_tuple)

    def forward(
        self,
        q: torch.Tensor,
        k: torch.Tensor,
        v: torch.Tensor,
        bsz: int,
        cu_seqlens: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        r"""
        Args:
            cu_seqlens: [b]
        Returns:
             [b * s, h, head_size]
        """
        if self.flatten_batch:
            assert bsz == 1, "flatten_batch is True, bsz must be 1"

        s = q.shape[0] // bsz

        # [b, 1, s, s]
        if attention_mask is None:
            attention_mask = self.generate_patch_attention_mask(
                s, cu_seqlens, flatten_batch=self.flatten_batch
            )

        if attention_mask is None:
            if self.softmax_in_single_precision:
                raise RuntimeError("Empty attention mask")
        else:
            attention_mask = attention_mask.to(device=q.device)

        q, k, v = [rearrange(x, "(b s) h d -> b h s d", b=bsz) for x in [q, k, v]]

        if self.softmax_in_single_precision:
            scale = self.head_size**-0.5
            k_transposed = rearrange(k, "b h s d -> b h d s")
            attn_weights = torch.matmul(q, k_transposed) * scale
            del k, k_transposed
            attention_mask = (~attention_mask) * torch.finfo(q.dtype).min
            attn_weights = attn_weights + attention_mask
            del attention_mask
            # full-precision
            attn_weights = nn.functional.softmax(
                attn_weights, dim=-1, dtype=torch.float32
            ).to(q.dtype)
            attn_weights = nn.functional.dropout(
                attn_weights, p=self.dropout, training=False
            )
            output = torch.matmul(attn_weights, v)
            del attn_weights, v
        else:
            # SDPA
            # [b, h, s, head_size]
            output = F.scaled_dot_product_attention(
                q,
                k,
                v,
                attn_mask=attention_mask,
                dropout_p=self.dropout,
                is_causal=False,
            )

        # [b, h, s, head_size] --> [b * s, h, head_size]
        output = rearrange(output, "b h s d -> (b s) h d")

        return output


class VisionTritonAttention(nn.Module):
    """
    Triton-implemented attention without a causal mask
    """

    def __init__(
        self,
    ):
        super().__init__()

    def forward(
        self,
        q: torch.Tensor,
        k: torch.Tensor,
        v: torch.Tensor,
        _bsz: int,
        cu_seqlens: Optional[torch.Tensor],
        # BACKPORT: accept (and ignore) the extra kwargs VisionAttention
        # forwards for the SDPA backend, e.g. when qwen3_vl drives this
        # backend in eager mode.
        attention_mask: Optional[torch.Tensor] = None,
        output_ws: Optional[torch.Tensor] = None,
        **kwargs,
    ) -> torch.Tensor:
        r"""
        Args:
            cu_seqlens: [b]
        Returns:
             [b * s, h, head_size]
        """

        # BACKPORT: v0.5.9 cuda-graph mode. The ViT graph runner supplies
        # cu_seqlens as [cu_seqlens, seq_lens, max_seqlen] (device tensors plus
        # a python int) so no host sync happens inside the captured graph, and
        # a reusable output workspace. Numerically identical to the default
        # eager triton path below (same kernel, same arguments). The optional
        # flash-attn fast path is eager-only; enabling SGLANG_ENABLE_FLASH_ATTN
        # together with ViT cuda graph would diverge numerically from eager.
        if isinstance(cu_seqlens, list):
            if output_ws is None:
                raise RuntimeError("output_ws should be prepared for cuda-graph mode")
            output = output_ws
            context_attention_fwd(
                q,
                k,
                v,
                output,
                cu_seqlens[0],
                cu_seqlens[1],
                cu_seqlens[2],
                is_causal=False,
            )
            return output

        seq_lens = cu_seqlens[1:] - cu_seqlens[:-1]
        max_seqlen = seq_lens.max().item()

        # FLASH-ATTN: flash_attn_varlen_func fast path. q/k/v are already
        # (total, heads, head_dim) and non-causal; any failure falls back to
        # the original triton kernel below.
        if flash_attn_varlen_func is not None:
            try:
                cu = cu_seqlens.to(device=q.device, dtype=torch.int32)
                return flash_attn_varlen_func(
                    q,
                    k,
                    v,
                    cu,
                    cu,
                    max_seqlen,
                    max_seqlen,
                    causal=False,
                )
            except Exception:
                pass

        # [b * s, head, head_size]
        output = torch.empty_like(q)
        context_attention_fwd(
            q,
            k,
            v,
            output,
            cu_seqlens.cuda(),
            seq_lens.cuda(),
            max_seqlen,
            is_causal=False,
        )

        return output
