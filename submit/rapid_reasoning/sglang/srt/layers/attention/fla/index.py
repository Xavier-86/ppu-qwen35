# Adapt from https://github.com/fla-org/flash-linear-attention/blob/main/fla/ops/utils/index.py
# -*- coding: utf-8 -*-
# Copyright (c) 2023-2025, Songlin Yang, Yu Zhang

from typing import Dict, Optional, Tuple

import torch
import triton

from sglang.srt.layers.attention.fla.utils import tensor_cache


@tensor_cache
def prepare_lens(cu_seqlens: torch.LongTensor) -> torch.LongTensor:
    return cu_seqlens[1:] - cu_seqlens[:-1]


# BACKPORT-PPU: fixed chunk-layout override for the extend (prefill) CUDA
# graph. prepare_chunk_indices/prepare_chunk_offsets sync on GPU content
# (.tolist()), which is illegal during graph capture, and tensor_cache is
# keyed by object identity, so a fixed buffer whose content changes per
# replay would read stale entries. The extend graph uses a two-segment
# layout [0, real, bucket] whose *constant* decomposition (bucket/64 and
# bucket/16 chunks per segment, content-independent) is injected here while
# the graph warms up and captures; the captured kernels read cu_seqlens
# content at replay time and clip out-of-range chunks via boundary checks.
# The override is only set during warmup/capture (single-threaded, no
# concurrent requests) and cleared right after, so eager requests are never
# affected.
_CHUNK_LAYOUT_OVERRIDE: Optional[Dict[int, Tuple[torch.Tensor, torch.Tensor]]] = None


def set_chunk_layout_override(
    layout: Optional[Dict[int, Tuple[torch.Tensor, torch.Tensor]]]
) -> None:
    """Set/clear the fixed {chunk_size: (chunk_indices, chunk_offsets)} layout."""
    global _CHUNK_LAYOUT_OVERRIDE
    _CHUNK_LAYOUT_OVERRIDE = layout


@tensor_cache
def _prepare_chunk_indices_cached(
    cu_seqlens: torch.LongTensor, chunk_size: int
) -> torch.LongTensor:
    indices = torch.cat(
        [
            torch.arange(n)
            for n in triton.cdiv(prepare_lens(cu_seqlens), chunk_size).tolist()
        ]
    )
    return torch.stack([indices.eq(0).cumsum(0) - 1, indices], 1).to(cu_seqlens)


def prepare_chunk_indices(
    cu_seqlens: torch.LongTensor, chunk_size: int
) -> torch.LongTensor:
    if _CHUNK_LAYOUT_OVERRIDE is not None:
        return _CHUNK_LAYOUT_OVERRIDE[chunk_size][0]
    return _prepare_chunk_indices_cached(cu_seqlens, chunk_size)


@tensor_cache
def _prepare_chunk_offsets_cached(
    cu_seqlens: torch.LongTensor, chunk_size: int
) -> torch.LongTensor:
    return torch.cat(
        [cu_seqlens.new_tensor([0]), triton.cdiv(prepare_lens(cu_seqlens), chunk_size)]
    ).cumsum(-1)


def prepare_chunk_offsets(
    cu_seqlens: torch.LongTensor, chunk_size: int
) -> torch.LongTensor:
    if _CHUNK_LAYOUT_OVERRIDE is not None:
        return _CHUNK_LAYOUT_OVERRIDE[chunk_size][1]
    return _prepare_chunk_offsets_cached(cu_seqlens, chunk_size)
