"""GDN prefill QKV split fusion backported from SGLang 0.5.13 #26206."""

import os
import torch
import triton
import triton.language as tl


@triton.jit
def _fused_qkv_split_gdn_prefill_kernel(
    q,
    k,
    v,
    mixed_qkv,
    MIXED_QKV_STRIDE_T: tl.constexpr,
    MIXED_QKV_STRIDE_D: tl.constexpr,
    NUM_Q_HEADS: tl.constexpr,
    NUM_K_HEADS: tl.constexpr,
    NUM_V_HEADS: tl.constexpr,
    HEAD_Q: tl.constexpr,
    HEAD_K: tl.constexpr,
    HEAD_V: tl.constexpr,
    BLOCK_SIZE: tl.constexpr,
):
    token_idx = tl.program_id(0)
    offsets = tl.arange(0, BLOCK_SIZE)
    q_dim: tl.constexpr = NUM_Q_HEADS * HEAD_Q
    k_dim: tl.constexpr = NUM_K_HEADS * HEAD_K
    v_dim: tl.constexpr = NUM_V_HEADS * HEAD_V
    qk_dim: tl.constexpr = q_dim + k_dim
    qkv_dim: tl.constexpr = qk_dim + v_dim
    values = tl.load(
        mixed_qkv
        + token_idx * MIXED_QKV_STRIDE_T
        + offsets * MIXED_QKV_STRIDE_D,
        mask=offsets < qkv_dim,
    )
    tl.store(q + token_idx * q_dim + offsets, values, mask=offsets < q_dim)
    k_offsets = offsets - q_dim
    tl.store(
        k + token_idx * k_dim + k_offsets,
        values,
        mask=(offsets >= q_dim) & (offsets < qk_dim),
    )
    v_offsets = offsets - qk_dim
    tl.store(
        v + token_idx * v_dim + v_offsets,
        values,
        mask=(offsets >= qk_dim) & (offsets < qkv_dim),
    )


def fused_qkv_split_gdn_prefill(
    mixed_qkv: torch.Tensor,
    num_q_heads: int,
    num_k_heads: int,
    num_v_heads: int,
    head_q: int,
    head_k: int,
    head_v: int,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Split packed QKV into three contiguous ``[1, T, H, D]`` tensors."""
    seq_len = mixed_qkv.shape[0]
    q = torch.empty(
        (1, seq_len, num_q_heads, head_q),
        dtype=mixed_qkv.dtype,
        device=mixed_qkv.device,
    )
    k = torch.empty(
        (1, seq_len, num_k_heads, head_k),
        dtype=mixed_qkv.dtype,
        device=mixed_qkv.device,
    )
    v = torch.empty(
        (1, seq_len, num_v_heads, head_v),
        dtype=mixed_qkv.dtype,
        device=mixed_qkv.device,
    )
    qkv_dim = num_q_heads * head_q + num_k_heads * head_k + num_v_heads * head_v
    num_warps = int(os.getenv("SGLANG_GDN_QKV_SPLIT_NUM_WARPS", "8"))
    # PPU EN1000 nightly sweep (two repeats): stages=4 reached a 318.749
    # tok/s median versus 318.335 for stages=3. Keep the environment override
    # for reproducible A/B tests, but use the measured winner by default.
    num_stages = int(os.getenv("SGLANG_GDN_QKV_SPLIT_NUM_STAGES", "4"))
    if num_warps not in (1, 2, 4, 8, 16):
        raise ValueError(f"Unsupported GDN QKV split num_warps: {num_warps}")
    if num_stages not in (1, 2, 3, 4):
        raise ValueError(f"Unsupported GDN QKV split num_stages: {num_stages}")
    _fused_qkv_split_gdn_prefill_kernel[(seq_len,)](
        q,
        k,
        v,
        mixed_qkv,
        mixed_qkv.stride(0),
        mixed_qkv.stride(1),
        num_q_heads,
        num_k_heads,
        num_v_heads,
        head_q,
        head_k,
        head_v,
        BLOCK_SIZE=triton.next_power_of_2(qkv_dim),
        num_warps=num_warps,
        num_stages=num_stages,
    )
    return q, k, v
