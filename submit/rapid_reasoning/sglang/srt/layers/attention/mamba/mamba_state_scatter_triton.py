"""Fused Mamba state gather/scatter backported from SGLang 0.5.13 #18088."""

import os
import torch
import triton
import triton.language as tl


@triton.jit
def _fused_mamba_state_scatter_with_mask_kernel(
    src_ptr,
    dst_ptr,
    dst_indices_ptr,
    step_indices_ptr,
    elem_per_entry: tl.constexpr,
    src_layer_stride,
    src_req_stride,
    src_step_stride,
    dst_layer_stride,
    dst_req_stride,
    src_req_size,
    src_step_size,
    dst_req_size,
    BLOCK_SIZE: tl.constexpr,
):
    pid_req = tl.program_id(0)
    pid_layer = tl.program_id(1).to(tl.int64)
    pid_block = tl.program_id(2).to(tl.int64)
    step_idx = tl.load(step_indices_ptr + pid_req).to(tl.int64)
    if step_idx < 0:
        return
    dst_idx = tl.load(dst_indices_ptr + pid_req).to(tl.int64)
    if not (
        (dst_idx >= 0)
        & (dst_idx < dst_req_size)
        & (pid_req < src_req_size)
        & (step_idx < src_step_size)
    ):
        return
    src_offset = (
        pid_layer * src_layer_stride
        + pid_req * src_req_stride
        + step_idx * src_step_stride
    )
    dst_offset = pid_layer * dst_layer_stride + dst_idx * dst_req_stride
    offsets = pid_block * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    mask = offsets < elem_per_entry
    data = tl.load(src_ptr + src_offset + offsets, mask=mask)
    tl.store(dst_ptr + dst_offset + offsets, data, mask=mask)


def fused_mamba_state_scatter_with_mask(
    dst: torch.Tensor,
    src: torch.Tensor,
    dst_indices: torch.Tensor,
    step_indices: torch.Tensor,
) -> None:
    """Copy ``src[:, request, step]`` to masked destination cache rows."""
    total_requests = step_indices.shape[0]
    if total_requests == 0:
        return
    if dst.device != src.device or not dst.is_cuda or not src.is_cuda:
        raise ValueError("Mamba state scatter requires CUDA tensors on one device")
    if dst.ndim < 2 or src.ndim < 3 or dst.shape[0] != src.shape[0]:
        raise ValueError(f"Unexpected state shapes: {dst.shape=} {src.shape=}")
    if dst.shape[2:] != src.shape[3:]:
        raise ValueError(f"State trailing dimensions differ: {dst.shape=} {src.shape=}")
    if dst_indices.ndim != 1 or step_indices.ndim != 1:
        raise ValueError("Mamba state scatter indices must be one-dimensional")
    if dst_indices.shape[0] != total_requests:
        raise ValueError("Mamba state scatter index lengths differ")
    if not dst.is_contiguous() or not src.is_contiguous():
        raise ValueError("Mamba state scatter tensors must be contiguous")

    dst_indices = dst_indices.to(torch.int32).contiguous()
    step_indices = step_indices.to(torch.int32).contiguous()
    elem_per_entry = dst.numel() // (dst.shape[0] * dst.shape[1])
    # Nightly tuning hook; the default is the validated production value.
    block_size = int(os.getenv("SGLANG_MAMBA_SCATTER_BLOCK_SIZE", "1024"))
    if block_size not in (128, 256, 512, 1024, 2048):
        raise ValueError(f"Unsupported Mamba scatter block size: {block_size}")
    grid = (
        total_requests,
        dst.shape[0],
        triton.cdiv(elem_per_entry, block_size),
    )
    _fused_mamba_state_scatter_with_mask_kernel[grid](
        src,
        dst,
        dst_indices,
        step_indices,
        elem_per_entry,
        src.stride(0),
        src.stride(1),
        src.stride(2),
        dst.stride(0),
        dst.stride(1),
        src.shape[1],
        src.shape[2],
        dst.shape[1],
        BLOCK_SIZE=block_size,
    )
