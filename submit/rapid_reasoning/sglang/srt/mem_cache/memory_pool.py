"""
Copyright 2023-2024 SGLang Team
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from sglang.srt.torch_memory_saver_adapter import TorchMemorySaverAdapter

"""
Memory pool.

SGLang has two levels of memory pool.
ReqToTokenPool maps a request to its token locations.
TokenToKVPoolAllocator manages the indices to kv cache data.
KVCache actually holds the physical kv cache.
"""

import abc
import dataclasses
import logging
import os
import threading
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass
from enum import IntEnum
from functools import wraps
from typing import Iterator, List, Optional, Tuple, Union

import numpy as np
import psutil
import torch
import triton
import triton.language as tl

from sglang.srt.configs.mamba_utils import BaseLinearStateParams
from sglang.srt.layers.radix_attention import RadixAttention
from sglang.srt.mem_cache.utils import maybe_init_custom_mem_pool
from sglang.srt.utils import (
    cpu_has_amx_support,
    debug_timing,
    get_compiler_backend,
    is_cpu,
    is_npu,
)

logger = logging.getLogger(__name__)

GB = 1024 * 1024 * 1024

# BACKPORT: from sglang v0.5.9 srt/constants.py; the 0.4.6 memory saver
# adapter's region() takes no tag, so this is only kept for API parity.
GPU_MEMORY_TYPE_KV_CACHE = "kv_cache"

# BACKPORT: module-level platform flags, as in v0.5.9 memory_pool.py
_is_cpu = is_cpu()
_is_npu = is_npu()
_cpu_has_amx_support = cpu_has_amx_support()

# BACKPORT-PPU: fuse the two advanced-indexing writes of set_kv_buffer
# (k_buffer[loc] = k; v_buffer[loc] = v — two at::native index kernels,
# ~6us each per layer in the verify graph) into one Triton launch. Pure
# copy with matching dtypes, so the result is bit-identical to eager by
# construction. Gated by SGLANG_FUSED_KV_SCATTER (default on); any
# dtype/layout mismatch falls back to the stock index_put path. cache_k /
# cache_v may be strided row-wise (e.g. qkv split views): only the
# innermost dimension must be contiguous.
_FUSED_KV_SCATTER = os.environ.get("SGLANG_FUSED_KV_SCATTER", "1") == "1"


@triton.jit
def _fused_set_kv_kernel(
    k_in,
    v_in,
    k_buf,
    v_buf,
    loc,
    row_dim,
    k_row_stride,
    v_row_stride,
    BLOCK: tl.constexpr,
):
    i_t = tl.program_id(0)
    dst = tl.load(loc + i_t).to(tl.int64)
    offs = tl.arange(0, BLOCK)
    mask = offs < row_dim
    dst_off = dst * row_dim + offs
    tl.store(
        k_buf + dst_off, tl.load(k_in + i_t * k_row_stride + offs, mask=mask), mask=mask
    )
    tl.store(
        v_buf + dst_off, tl.load(v_in + i_t * v_row_stride + offs, mask=mask), mask=mask
    )


def _fused_set_kv(k_buf, v_buf, loc, cache_k, cache_v):
    n = cache_k.shape[0]
    row_dim = cache_k[0].numel()
    _fused_set_kv_kernel[(n,)](
        cache_k,
        cache_v,
        k_buf,
        v_buf,
        loc,
        row_dim,
        cache_k.stride(0),
        cache_v.stride(0),
        BLOCK=triton.next_power_of_2(row_dim),
        num_warps=4,
    )


# BACKPORT: from sglang v0.5.9
def get_tensor_size_bytes(t: Union[torch.Tensor, List[torch.Tensor]]):
    if isinstance(t, list):
        return sum(get_tensor_size_bytes(x) for x in t)
    return t.numel() * t.element_size()


class ReqToTokenPool:
    """A memory pool that maps a request to its token locations."""

    def __init__(
        self,
        size: int,
        max_context_len: int,
        device: str,
        enable_memory_saver: bool,
    ):
        memory_saver_adapter = TorchMemorySaverAdapter.create(
            enable=enable_memory_saver
        )

        self.size = size
        self.max_context_len = max_context_len
        self.device = device
        with memory_saver_adapter.region():
            self.req_to_token = torch.zeros(
                (size, max_context_len), dtype=torch.int32, device=device
            )
        self.free_slots = list(range(size))

    def write(self, indices, values):
        self.req_to_token[indices] = values

    def available_size(self):
        return len(self.free_slots)

    def alloc(self, need_size: int) -> List[int]:
        if need_size > len(self.free_slots):
            return None

        select_index = self.free_slots[:need_size]
        self.free_slots = self.free_slots[need_size:]

        return select_index

    def free(self, free_index: Union[int, List[int]]):
        if isinstance(free_index, (int,)):
            self.free_slots.append(free_index)
        else:
            self.free_slots.extend(free_index)

    def clear(self):
        self.free_slots = list(range(self.size))


class KVCache(abc.ABC):

    @abc.abstractmethod
    def get_key_buffer(self, layer_id: int) -> torch.Tensor:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_value_buffer(self, layer_id: int) -> torch.Tensor:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_kv_buffer(self, layer_id: int) -> Tuple[torch.Tensor, torch.Tensor]:
        raise NotImplementedError()

    @abc.abstractmethod
    def set_kv_buffer(
        self,
        layer: RadixAttention,
        loc: torch.Tensor,
        cache_k: torch.Tensor,
        cache_v: torch.Tensor,
    ) -> None:
        raise NotImplementedError()

    # SLIM: removed get_flat_data / transfer / transfer_per_layer abstract
    # methods (fixed Qwen3.5-2B config: no PD disaggregation host transfer)

    def register_layer_transfer_counter(self, layer_transfer_counter):
        self.layer_transfer_counter = layer_transfer_counter

    # BACKPORT: from sglang v0.5.9 KVCache; used by HybridLinearKVPool.
    def maybe_get_custom_mem_pool(self):
        return getattr(self, "custom_mem_pool", None)


class TokenToKVPoolAllocator:
    """An allocator managing the indices to kv cache data."""

    def __init__(
        self,
        size: int,
        dtype: torch.dtype,
        device: str,
        kvcache: KVCache,
    ):
        self.size = size
        self.dtype = dtype
        self.device = device
        self.page_size = 1

        self.free_slots = None
        self.is_not_in_free_group = True
        self.free_group = []
        self.clear()

        self._kvcache = kvcache

    def available_size(self):
        return len(self.free_slots)

    def get_kvcache(self):
        return self._kvcache

    def alloc(self, need_size: int):
        if need_size > len(self.free_slots):
            return None

        select_index = self.free_slots[:need_size]
        self.free_slots = self.free_slots[need_size:]
        return select_index

    def free(self, free_index: torch.Tensor):
        if free_index.numel() == 0:
            return

        if self.is_not_in_free_group:
            self.free_slots = torch.cat((self.free_slots, free_index))
        else:
            self.free_group.append(free_index)

    def free_group_begin(self):
        self.is_not_in_free_group = False
        self.free_group = []

    def free_group_end(self):
        self.is_not_in_free_group = True
        if self.free_group:
            self.free(torch.cat(self.free_group))

    def backup_state(self):
        return self.free_slots

    def restore_state(self, free_slots):
        self.free_slots = free_slots

    def clear(self):
        # The padded slot 0 is used for writing dummy outputs from padded tokens.
        self.free_slots = torch.arange(
            1, self.size + 1, dtype=torch.int64, device=self.device
        )
        self.is_not_in_free_group = True
        self.free_group = []


class MHATokenToKVPool(KVCache):

    def __init__(
        self,
        size: int,
        page_size: int,
        dtype: torch.dtype,
        head_num: int,
        head_dim: int,
        layer_num: int,
        device: str,
        enable_memory_saver: bool,
    ):
        self.size = size
        self.page_size = page_size
        self.dtype = dtype
        self.device = device
        if dtype in (torch.float8_e5m2, torch.float8_e4m3fn):
            # NOTE: Store as torch.uint8 because Tensor.index_put is not implemented for torch.float8_e5m2
            self.store_dtype = torch.uint8
        else:
            self.store_dtype = dtype
        self.memory_saver_adapter = TorchMemorySaverAdapter.create(
            enable=enable_memory_saver
        )

        self.head_num = head_num
        self.head_dim = head_dim
        self.layer_num = layer_num
        self._create_buffers()

        self.layer_transfer_counter = None
        self.capture_mode = False
        self.device_module = torch.get_device_module(self.device)
        self.alt_stream = self.device_module.Stream()

        k_size, v_size = self.get_kv_size_bytes()
        logger.info(
            f"KV Cache is allocated. #tokens: {size}, K size: {k_size / GB:.2f} GB, V size: {v_size / GB:.2f} GB"
        )

    def _create_buffers(self):
        with self.memory_saver_adapter.region():
            # [size, head_num, head_dim] for each layer
            # The padded slot 0 is used for writing dummy outputs from padded tokens.
            self.k_buffer = [
                torch.zeros(
                    (self.size + self.page_size, self.head_num, self.head_dim),
                    dtype=self.store_dtype,
                    device=self.device,
                )
                for _ in range(self.layer_num)
            ]
            self.v_buffer = [
                torch.zeros(
                    (self.size + self.page_size, self.head_num, self.head_dim),
                    dtype=self.store_dtype,
                    device=self.device,
                )
                for _ in range(self.layer_num)
            ]

    def _clear_buffers(self):
        del self.k_buffer
        del self.v_buffer

    def get_kv_size_bytes(self):
        assert hasattr(self, "k_buffer")
        assert hasattr(self, "v_buffer")
        k_size_bytes = 0
        for k_cache in self.k_buffer:
            k_size_bytes += np.prod(k_cache.shape) * k_cache.dtype.itemsize
        v_size_bytes = 0
        for v_cache in self.v_buffer:
            v_size_bytes += np.prod(v_cache.shape) * v_cache.dtype.itemsize
        return k_size_bytes, v_size_bytes

    # for disagg
    def get_contiguous_buf_infos(self):
        kv_data_ptrs = [
            self.get_key_buffer(i).data_ptr() for i in range(self.layer_num)
        ] + [self.get_value_buffer(i).data_ptr() for i in range(self.layer_num)]
        kv_data_lens = [
            self.get_key_buffer(i).nbytes for i in range(self.layer_num)
        ] + [self.get_value_buffer(i).nbytes for i in range(self.layer_num)]
        kv_item_lens = [
            self.get_key_buffer(i)[0].nbytes * self.page_size
            for i in range(self.layer_num)
        ] + [
            self.get_value_buffer(i)[0].nbytes * self.page_size
            for i in range(self.layer_num)
        ]
        return kv_data_ptrs, kv_data_lens, kv_item_lens

    # Todo: different memory layout
    def get_flat_data(self, indices):
        # prepare a large chunk of contiguous data for efficient transfer
        flatten = torch.stack(
            [
                torch.stack([self.k_buffer[i][indices] for i in range(self.layer_num)]),
                torch.stack([self.v_buffer[i][indices] for i in range(self.layer_num)]),
            ]
        )
        return flatten

    @debug_timing
    def transfer(self, indices, flat_data):
        # transfer prepared data from host to device
        flat_data = flat_data.to(device=self.device, non_blocking=False)
        k_data, v_data = flat_data[0], flat_data[1]
        for i in range(self.layer_num):
            self.k_buffer[i][indices] = k_data[i]
            self.v_buffer[i][indices] = v_data[i]

    def transfer_per_layer(self, indices, flat_data, layer_id):
        # transfer prepared data from host to device
        flat_data = flat_data.to(device=self.device, non_blocking=False)
        k_data, v_data = flat_data[0], flat_data[1]
        self.k_buffer[layer_id][indices] = k_data
        self.v_buffer[layer_id][indices] = v_data

    def get_key_buffer(self, layer_id: int):
        if self.layer_transfer_counter is not None:
            self.layer_transfer_counter.wait_until(layer_id)

        if self.store_dtype != self.dtype:
            return self.k_buffer[layer_id].view(self.dtype)
        return self.k_buffer[layer_id]

    def get_value_buffer(self, layer_id: int):
        if self.layer_transfer_counter is not None:
            self.layer_transfer_counter.wait_until(layer_id)

        if self.store_dtype != self.dtype:
            return self.v_buffer[layer_id].view(self.dtype)
        return self.v_buffer[layer_id]

    def get_kv_buffer(self, layer_id: int):
        return self.get_key_buffer(layer_id), self.get_value_buffer(layer_id)

    def set_kv_buffer(
        self,
        layer: RadixAttention,
        loc: torch.Tensor,
        cache_k: torch.Tensor,
        cache_v: torch.Tensor,
        k_scale: Optional[float] = None,
        v_scale: Optional[float] = None,
        layer_id_override: Optional[int] = None,  # BACKPORT: from v0.5.9
    ):
        if layer_id_override is not None:
            layer_id = layer_id_override
        else:
            layer_id = layer.layer_id
        if cache_k.dtype != self.dtype:
            if k_scale is not None:
                cache_k.div_(k_scale)
            if v_scale is not None:
                cache_v.div_(v_scale)
            cache_k = cache_k.to(self.dtype)
            cache_v = cache_v.to(self.dtype)

        if self.store_dtype != self.dtype:
            cache_k = cache_k.view(self.store_dtype)
            cache_v = cache_v.view(self.store_dtype)

        # BACKPORT-PPU: one fused launch instead of two index_put kernels
        # (also replaces the capture-mode alt_stream overlap below).
        # cache_k/cache_v are [tokens, kv_heads, head_dim]; dim0 may be
        # strided (qkv split views) as long as each token row is contiguous.
        _kv_fused_ok = (
            _FUSED_KV_SCATTER
            and cache_k.dtype == self.dtype
            and self.store_dtype == self.dtype
            and cache_k.shape == cache_v.shape
            and cache_k.dim() >= 2
            and cache_k.stride(-1) == 1
            and cache_v.stride(-1) == 1
            and cache_k[0].is_contiguous()
            and cache_v[0].is_contiguous()
            and loc.is_contiguous()
            and self.k_buffer[layer_id].is_contiguous()
            and self.v_buffer[layer_id].is_contiguous()
            and cache_k.shape[0] == loc.shape[0]
        )
        if _kv_fused_ok:
            _fused_set_kv(
                self.k_buffer[layer_id],
                self.v_buffer[layer_id],
                loc,
                cache_k,
                cache_v,
            )
            return

        if self.capture_mode and cache_k.shape[0] < 4:
            # Overlap the copy of K and V cache for small batch size
            current_stream = self.device_module.current_stream()
            self.alt_stream.wait_stream(current_stream)
            with self.device_module.stream(self.alt_stream):
                self.k_buffer[layer_id][loc] = cache_k
            self.v_buffer[layer_id][loc] = cache_v
            current_stream.wait_stream(self.alt_stream)
        else:
            self.k_buffer[layer_id][loc] = cache_k
            self.v_buffer[layer_id][loc] = cache_v

    # BACKPORT: from sglang v0.5.9. Only the native implementation is kept;
    # v0.5.9's tiled triton fast path (copy_all_layer_kv_cache_tiled, requiring
    # enable_kv_cache_copy init) is not backported.
    def move_kv_cache(self, tgt_loc: torch.Tensor, src_loc: torch.Tensor):
        move_kv_cache_native(self.k_buffer, self.v_buffer, tgt_loc, src_loc)


# BACKPORT: from sglang v0.5.9
def move_kv_cache_native(
    k_buffer: List[torch.Tensor],
    v_buffer: List[torch.Tensor],
    tgt_loc: torch.Tensor,
    src_loc: torch.Tensor,
):
    if tgt_loc.numel() == 0:
        return

    tgt_loc_flat = tgt_loc.view(-1).long()
    src_loc_flat = src_loc.view(-1).long()
    for k_cache, v_cache in zip(k_buffer, v_buffer):
        k_cache[tgt_loc_flat] = k_cache[src_loc_flat]
        v_cache[tgt_loc_flat] = v_cache[src_loc_flat]


@torch.compile
def fused_downcast(
    cache_k: torch.Tensor,
    cache_v: torch.Tensor,
    k_scale: torch.Tensor,
    v_scale: torch.Tensor,
    dtype: torch.dtype,
    store_dtype: torch.dtype,
    max_fp8: float,
    min_fp8: float,
):
    cache_k = cache_k / k_scale
    cache_k = torch.clamp(cache_k, min_fp8, max_fp8)
    cache_v = cache_v / v_scale
    cache_v = torch.clamp(cache_v, min_fp8, max_fp8)
    cache_k = cache_k.to(dtype)
    cache_v = cache_v.to(dtype)
    cache_k = cache_k.view(store_dtype)
    cache_v = cache_v.view(store_dtype)
    return cache_k, cache_v


# This compiled version is slower in the unit test
# python3 -m unittest test_bench_serving.TestBenchServing.test_offline_throughput_non_stream_small_batch_size
@torch.compile(dynamic=True, backend=get_compiler_backend())
def copy_two_array(loc, dst_1, src_1, dst_2, src_2, dtype, store_dtype):
    dst_1[loc] = src_1.to(dtype).view(store_dtype)
    dst_2[loc] = src_2.to(dtype).view(store_dtype)


@triton.jit
def set_mla_kv_buffer_kernel(
    kv_buffer_ptr,
    cache_k_nope_ptr,
    cache_k_rope_ptr,
    loc_ptr,
    buffer_stride: tl.constexpr,
    nope_stride: tl.constexpr,
    rope_stride: tl.constexpr,
    nope_dim: tl.constexpr,
    rope_dim: tl.constexpr,
    BLOCK: tl.constexpr,
):
    pid_loc = tl.program_id(0)
    pid_blk = tl.program_id(1)

    base = pid_blk * BLOCK
    offs = base + tl.arange(0, BLOCK)
    total_dim = nope_dim + rope_dim
    mask = offs < total_dim

    loc = tl.load(loc_ptr + pid_loc)
    dst_ptr = kv_buffer_ptr + loc * buffer_stride + offs

    if base + BLOCK <= nope_dim:
        src = tl.load(
            cache_k_nope_ptr + pid_loc * nope_stride + offs,
            mask=mask,
        )
    else:
        offs_rope = offs - nope_dim
        src = tl.load(
            cache_k_rope_ptr + pid_loc * rope_stride + offs_rope,
            mask=mask,
        )

    tl.store(dst_ptr, src, mask=mask)


def set_mla_kv_buffer_triton(
    kv_buffer: torch.Tensor,
    loc: torch.Tensor,
    cache_k_nope: torch.Tensor,
    cache_k_rope: torch.Tensor,
):
    nope_dim = cache_k_nope.shape[-1]
    rope_dim = cache_k_rope.shape[-1]
    total_dim = nope_dim + rope_dim
    BLOCK = 128
    n_loc = loc.numel()
    grid = (n_loc, triton.cdiv(total_dim, BLOCK))

    set_mla_kv_buffer_kernel[grid](
        kv_buffer,
        cache_k_nope,
        cache_k_rope,
        loc,
        kv_buffer.stride(0),
        cache_k_nope.stride(0),
        cache_k_rope.stride(0),
        nope_dim,
        rope_dim,
        BLOCK=BLOCK,
    )


class MLATokenToKVPool(KVCache):
    def __init__(
        self,
        size: int,
        page_size: int,
        dtype: torch.dtype,
        kv_lora_rank: int,
        qk_rope_head_dim: int,
        layer_num: int,
        device: str,
        enable_memory_saver: bool,
    ):
        self.size = size
        self.page_size = page_size
        self.dtype = dtype
        self.device = device
        if dtype in (torch.float8_e5m2, torch.float8_e4m3fn):
            # NOTE: Store as torch.uint8 because Tensor.index_put is not implemented for torch.float8_e5m2
            self.store_dtype = torch.uint8
        else:
            self.store_dtype = dtype
        self.kv_lora_rank = kv_lora_rank
        self.qk_rope_head_dim = qk_rope_head_dim
        self.layer_num = layer_num

        memory_saver_adapter = TorchMemorySaverAdapter.create(
            enable=enable_memory_saver
        )

        with memory_saver_adapter.region():
            # The padded slot 0 is used for writing dummy outputs from padded tokens.
            self.kv_buffer = [
                torch.zeros(
                    (size + page_size, 1, kv_lora_rank + qk_rope_head_dim),
                    dtype=self.store_dtype,
                    device=device,
                )
                for _ in range(layer_num)
            ]

        self.layer_transfer_counter = None
        self.page_size = page_size

        kv_size = self.get_kv_size_bytes()
        logger.info(
            f"KV Cache is allocated. #tokens: {size}, KV size: {kv_size / GB:.2f} GB"
        )

    def get_kv_size_bytes(self):
        assert hasattr(self, "kv_buffer")
        kv_size_bytes = 0
        for kv_cache in self.kv_buffer:
            kv_size_bytes += np.prod(kv_cache.shape) * kv_cache.dtype.itemsize
        return kv_size_bytes

    # for disagg
    def get_contiguous_buf_infos(self):
        # MLA has only one kv_buffer, so only the information of this buffer needs to be returned.
        kv_data_ptrs = [self.kv_buffer[i].data_ptr() for i in range(self.layer_num)]
        kv_data_lens = [self.kv_buffer[i].nbytes for i in range(self.layer_num)]
        kv_item_lens = [
            self.kv_buffer[i][0].nbytes * self.page_size for i in range(self.layer_num)
        ]
        return kv_data_ptrs, kv_data_lens, kv_item_lens

    def get_key_buffer(self, layer_id: int):
        if self.layer_transfer_counter is not None:
            self.layer_transfer_counter.wait_until(layer_id)

        if self.store_dtype != self.dtype:
            return self.kv_buffer[layer_id].view(self.dtype)
        return self.kv_buffer[layer_id]

    def get_value_buffer(self, layer_id: int):
        if self.layer_transfer_counter is not None:
            self.layer_transfer_counter.wait_until(layer_id)

        if self.store_dtype != self.dtype:
            return self.kv_buffer[layer_id][..., : self.kv_lora_rank].view(self.dtype)
        return self.kv_buffer[layer_id][..., : self.kv_lora_rank]

    def get_kv_buffer(self, layer_id: int):
        return self.get_key_buffer(layer_id), self.get_value_buffer(layer_id)

    def set_kv_buffer(
        self,
        layer: RadixAttention,
        loc: torch.Tensor,
        cache_k: torch.Tensor,
        cache_v: torch.Tensor,
    ):
        layer_id = layer.layer_id
        if cache_k.dtype != self.dtype:
            cache_k = cache_k.to(self.dtype)
        if self.store_dtype != self.dtype:
            self.kv_buffer[layer_id][loc] = cache_k.view(self.store_dtype)
        else:
            self.kv_buffer[layer_id][loc] = cache_k

    def set_mla_kv_buffer(
        self,
        layer: RadixAttention,
        loc: torch.Tensor,
        cache_k_nope: torch.Tensor,
        cache_k_rope: torch.Tensor,
    ):
        layer_id = layer.layer_id
        if cache_k_nope.dtype != self.dtype:
            cache_k_nope = cache_k_nope.to(self.dtype)
            cache_k_rope = cache_k_rope.to(self.dtype)
        if self.store_dtype != self.dtype:
            cache_k_nope = cache_k_nope.view(self.store_dtype)
            cache_k_rope = cache_k_rope.view(self.store_dtype)

        set_mla_kv_buffer_triton(
            self.kv_buffer[layer_id], loc, cache_k_nope, cache_k_rope
        )

    def get_flat_data(self, indices):
        # prepare a large chunk of contiguous data for efficient transfer
        return torch.stack([self.kv_buffer[i][indices] for i in range(self.layer_num)])

    @debug_timing
    def transfer(self, indices, flat_data):
        # transfer prepared data from host to device
        flat_data = flat_data.to(device=self.device, non_blocking=False)
        for i in range(self.layer_num):
            self.kv_buffer[i][indices] = flat_data[i]

    def transfer_per_layer(self, indices, flat_data, layer_id):
        # transfer prepared data from host to device
        flat_data = flat_data.to(device=self.device, non_blocking=False)
        self.kv_buffer[layer_id][indices] = flat_data


class DoubleSparseTokenToKVPool(KVCache):
    def __init__(
        self,
        size: int,
        page_size: int,
        dtype: torch.dtype,
        head_num: int,
        head_dim: int,
        layer_num: int,
        device: str,
        heavy_channel_num: int,
        enable_memory_saver: bool,
    ):
        self.size = size
        self.page_size = page_size
        self.dtype = dtype
        self.device = device
        if dtype in (torch.float8_e5m2, torch.float8_e4m3fn):
            # NOTE: Store as torch.uint8 because Tensor.index_put is not implemented for torch.float8_e5m2
            self.store_dtype = torch.uint8
        else:
            self.store_dtype = dtype
        memory_saver_adapter = TorchMemorySaverAdapter.create(
            enable=enable_memory_saver
        )

        with memory_saver_adapter.region():
            # [size, head_num, head_dim] for each layer
            self.k_buffer = [
                torch.zeros(
                    (size + page_size, head_num, head_dim), dtype=dtype, device=device
                )
                for _ in range(layer_num)
            ]
            self.v_buffer = [
                torch.zeros(
                    (size + page_size, head_num, head_dim), dtype=dtype, device=device
                )
                for _ in range(layer_num)
            ]

            # [size, head_num, heavy_channel_num] for each layer
            self.label_buffer = [
                torch.zeros(
                    (size + 1, head_num, heavy_channel_num), dtype=dtype, device=device
                )
                for _ in range(layer_num)
            ]

    def get_key_buffer(self, layer_id: int):
        return self.k_buffer[layer_id]

    def get_value_buffer(self, layer_id: int):
        return self.v_buffer[layer_id]

    def get_label_buffer(self, layer_id: int):
        return self.label_buffer[layer_id]

    def get_kv_buffer(self, layer_id: int):
        return self.k_buffer[layer_id], self.v_buffer[layer_id]

    def set_kv_buffer(
        self,
        layer: RadixAttention,
        loc: torch.Tensor,
        cache_k: torch.Tensor,
        cache_v: torch.Tensor,
        cache_label: torch.Tensor,
    ):
        # NOTE(Andy): ignore the dtype check
        layer_id = layer.layer_id
        self.k_buffer[layer_id][loc] = cache_k
        self.v_buffer[layer_id][loc] = cache_v
        self.label_buffer[layer_id][loc] = cache_label

    def get_flat_data(self, indices):
        pass

    def transfer(self, indices, flat_data):
        pass

    def transfer_per_layer(self, indices, flat_data, layer_id):
        pass


class MemoryStateInt(IntEnum):
    IDLE = 0
    RESERVED = 1
    PROTECTED = 2
    SYNCED = 3
    BACKUP = 4


def synchronized(debug_only=False):
    def _decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if (not debug_only) or self.debug:
                return func(self, *args, **kwargs)
                with self.lock:
                    return func(self, *args, **kwargs)
            else:
                return True

        return wrapper

    return _decorator


class HostKVCache(abc.ABC):

    def __init__(
        self,
        device_pool: MHATokenToKVPool,
        host_to_device_ratio: float,
        host_size: int,
        pin_memory: bool,
        device: str,
        page_size: int,
    ):
        self.device_pool = device_pool
        self.dtype = device_pool.store_dtype
        self.pin_memory = pin_memory
        self.device = device
        self.page_size = page_size
        self.size_per_token = self.get_size_per_token()
        if host_size > 0:
            self.size = int(host_size * 1e9 // self.size_per_token)
        else:
            self.size = int(device_pool.size * host_to_device_ratio)
        # Align the host memory pool size to the page size
        self.size = self.size - (self.size % self.page_size)

        assert (
            self.size > device_pool.size
        ), "The host memory should be larger than the device memory with the current protocol"

        # Verify there is enough available host memory.
        host_mem = psutil.virtual_memory()
        requested_bytes = self.size * self.size_per_token
        # preserve at least 10GB for other usage
        ten_gb = 10 * (1024**3)
        if requested_bytes > host_mem.available - ten_gb:
            raise ValueError(
                f"Not enough host memory available. Requesting "
                f"{requested_bytes / 1e9:.2f} GB but only have "
                f"{host_mem.available / 1e9:.2f} GB free. Please reduce the "
                f"size of the hierarchical cache."
            )
        else:
            logger.info(
                f"Allocating {requested_bytes / 1e9:.2f} GB host memory for hierarchical KV cache."
            )

        self.kv_buffer = self.init_kv_buffer()

        # A lock for synchronized operations on memory allocation and state transitions.
        self.lock = threading.RLock()
        self.debug = logger.isEnabledFor(logging.DEBUG)
        self.clear()

    @abc.abstractmethod
    def get_size_per_token(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def init_kv_buffer(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def transfer(self, indices, flat_data):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_flat_data(self, indices):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_flat_data_by_layer(self, indices, layer_id):
        raise NotImplementedError()

    @abc.abstractmethod
    def assign_flat_data(self, indices, flat_data):
        raise NotImplementedError()

    @synchronized()
    def clear(self):
        # Initialize memory states and tracking structures.
        self.mem_state = torch.zeros(
            (self.size,), dtype=torch.uint8, device=self.device
        )
        self.free_slots = torch.arange(self.size, dtype=torch.int64)

    def available_size(self):
        return len(self.free_slots)

    @synchronized()
    def alloc(self, need_size: int) -> torch.Tensor:
        if need_size > self.available_size():
            return None

        select_index = self.free_slots[:need_size]
        self.free_slots = self.free_slots[need_size:]

        if self.debug:
            self.mem_state[select_index] = MemoryStateInt.RESERVED

        return select_index

    @synchronized()
    def free(self, indices: torch.Tensor) -> int:
        self.free_slots = torch.cat([self.free_slots, indices])
        if self.debug:
            self.mem_state[indices] = MemoryStateInt.IDLE
        return len(indices)

    @synchronized(debug_only=True)
    def get_state(self, indices: torch.Tensor) -> MemoryStateInt:
        assert len(indices) > 0, "The indices should not be empty"
        states = self.mem_state[indices]
        assert (
            states == states[0]
        ).all(), "The memory slots should have the same state {}".format(states)
        return MemoryStateInt(states[0].item())

    @synchronized(debug_only=True)
    def is_reserved(self, indices: torch.Tensor) -> bool:
        return self.get_state(indices) == MemoryStateInt.RESERVED

    @synchronized(debug_only=True)
    def is_protected(self, indices: torch.Tensor) -> bool:
        return self.get_state(indices) == MemoryStateInt.PROTECTED

    @synchronized(debug_only=True)
    def is_synced(self, indices: torch.Tensor) -> bool:
        return self.get_state(indices) == MemoryStateInt.SYNCED

    @synchronized(debug_only=True)
    def is_backup(self, indices: torch.Tensor) -> bool:
        return self.get_state(indices) == MemoryStateInt.BACKUP

    @synchronized(debug_only=True)
    def update_backup(self, indices: torch.Tensor):
        if not self.is_synced(indices):
            raise ValueError(
                f"The host memory slots should be in SYNCED state before turning into BACKUP. "
                f"Current state: {self.get_state(indices)}"
            )
        self.mem_state[indices] = MemoryStateInt.BACKUP

    @synchronized(debug_only=True)
    def update_synced(self, indices: torch.Tensor):
        self.mem_state[indices] = MemoryStateInt.SYNCED

    @synchronized(debug_only=True)
    def protect_write(self, indices: torch.Tensor):
        if not self.is_reserved(indices):
            raise ValueError(
                f"The host memory slots should be RESERVED before write operations. "
                f"Current state: {self.get_state(indices)}"
            )
        self.mem_state[indices] = MemoryStateInt.PROTECTED

    @synchronized(debug_only=True)
    def protect_load(self, indices: torch.Tensor):
        if not self.is_backup(indices):
            raise ValueError(
                f"The host memory slots should be in BACKUP state before load operations. "
                f"Current state: {self.get_state(indices)}"
            )
        self.mem_state[indices] = MemoryStateInt.PROTECTED

    @synchronized(debug_only=True)
    def complete_io(self, indices: torch.Tensor):
        if not self.is_protected(indices):
            raise ValueError(
                f"The host memory slots should be PROTECTED during I/O operations. "
                f"Current state: {self.get_state(indices)}"
            )
        self.mem_state[indices] = MemoryStateInt.SYNCED


class MHATokenToKVPoolHost(HostKVCache):
    def __init__(
        self,
        device_pool: MHATokenToKVPool,
        host_to_device_ratio: float,
        host_size: int,
        page_size: int,
        pin_memory: bool = True,
        device: str = "cpu",
    ):
        super().__init__(
            device_pool, host_to_device_ratio, host_size, pin_memory, device, page_size
        )

    def get_size_per_token(self):
        self.head_num = self.device_pool.head_num
        self.head_dim = self.device_pool.head_dim
        self.layer_num = self.device_pool.layer_num

        return self.head_dim * self.head_num * self.layer_num * self.dtype.itemsize * 2

    def init_kv_buffer(self):
        return torch.empty(
            (2, self.layer_num, self.size, self.head_num, self.head_dim),
            dtype=self.dtype,
            device=self.device,
            pin_memory=self.pin_memory,
        )

    @debug_timing
    def transfer(self, indices, flat_data):
        # backup prepared data from device to host
        self.kv_buffer[:, :, indices] = flat_data.to(
            device=self.device, non_blocking=False
        )

    def get_flat_data(self, indices):
        return self.kv_buffer[:, :, indices]

    def get_flat_data_by_layer(self, indices, layer_id):
        return self.kv_buffer[:, layer_id, indices]

    def assign_flat_data(self, indices, flat_data):
        self.kv_buffer[:, :, indices] = flat_data

    def write_page_all_layers(self, host_indices, device_indices, device_pool):
        device_indices_cpu = device_indices[:: self.page_size].cpu()
        for i in range(len(device_indices_cpu)):
            h_index = host_indices[i * self.page_size]
            d_index = device_indices_cpu[i]
            for j in range(self.layer_num):
                self.kv_buffer[0, j, h_index : h_index + self.page_size].copy_(
                    device_pool.k_buffer[j][d_index : d_index + self.page_size],
                    non_blocking=True,
                )
                self.kv_buffer[1, j, h_index : h_index + self.page_size].copy_(
                    device_pool.v_buffer[j][d_index : d_index + self.page_size],
                    non_blocking=True,
                )

    def load_page_per_layer(self, host_indices, device_indices, device_pool, layer_id):
        device_indices_cpu = device_indices[:: self.page_size].cpu()
        for i in range(len(device_indices_cpu)):
            h_index = host_indices[i * self.page_size]
            d_index = device_indices_cpu[i]
            device_pool.k_buffer[layer_id][d_index : d_index + self.page_size].copy_(
                self.kv_buffer[0, layer_id, h_index : h_index + self.page_size],
                non_blocking=True,
            )
            device_pool.v_buffer[layer_id][d_index : d_index + self.page_size].copy_(
                self.kv_buffer[1, layer_id, h_index : h_index + self.page_size],
                non_blocking=True,
            )


class MLATokenToKVPoolHost(HostKVCache):
    def __init__(
        self,
        device_pool: MLATokenToKVPool,
        host_to_device_ratio: float,
        host_size: int,
        page_size: int,
        pin_memory: bool = True,
        device: str = "cpu",
    ):
        super().__init__(
            device_pool, host_to_device_ratio, host_size, pin_memory, device, page_size
        )

    def get_size_per_token(self):
        self.kv_lora_rank = self.device_pool.kv_lora_rank
        self.qk_rope_head_dim = self.device_pool.qk_rope_head_dim
        self.layer_num = self.device_pool.layer_num

        return (
            (self.kv_lora_rank + self.qk_rope_head_dim)
            * 1
            * self.dtype.itemsize
            * self.layer_num
        )

    def init_kv_buffer(self):
        return torch.empty(
            (
                self.layer_num,
                self.size,
                1,
                self.kv_lora_rank + self.qk_rope_head_dim,
            ),
            dtype=self.dtype,
            device=self.device,
            pin_memory=self.pin_memory,
        )

    @debug_timing
    def transfer(self, indices, flat_data):
        # backup prepared data from device to host
        self.kv_buffer[:, indices] = flat_data.to(
            device=self.device, non_blocking=False
        )

    def get_flat_data(self, indices):
        return self.kv_buffer[:, indices]

    def get_flat_data_by_layer(self, indices, layer_id):
        return self.kv_buffer[layer_id, indices]

    def assign_flat_data(self, indices, flat_data):
        self.kv_buffer[:, indices] = flat_data

    def write_page_all_layers(self, host_indices, device_indices, device_pool):
        device_indices_cpu = device_indices[:: self.page_size].cpu()
        for i in range(len(device_indices_cpu)):
            h_index = host_indices[i * self.page_size]
            d_index = device_indices_cpu[i]
            for j in range(self.layer_num):
                self.kv_buffer[j, h_index : h_index + self.page_size].copy_(
                    device_pool.kv_buffer[j][d_index : d_index + self.page_size],
                    non_blocking=True,
                )

    def load_page_per_layer(self, host_indices, device_indices, device_pool, layer_id):
        device_indices_cpu = device_indices[:: self.page_size].cpu()
        for i in range(len(device_indices_cpu)):
            h_index = host_indices[i * self.page_size]
            d_index = device_indices_cpu[i]
            device_pool.kv_buffer[layer_id][d_index : d_index + self.page_size].copy_(
                self.kv_buffer[layer_id, h_index : h_index + self.page_size],
                non_blocking=True,
            )


# ============================================================================
# BACKPORT: hybrid linear-attention (Qwen3-Next / mamba) pools from
# sglang v0.5.9 srt/mem_cache/memory_pool.py.
# Adaptations for this 0.4.6-based tree:
# - TorchMemorySaverAdapter.region() here takes no memory-type tag argument.
# - The 0.4.6 ReqToTokenPool.alloc/free use (need_size / index) semantics;
#   HybridReqToTokenPool below implements the v0.5.9 (reqs) semantics
#   self-contained so the 0.4.6 scheduler paths keep working.
# ============================================================================


class MambaPool:
    @dataclass(frozen=True, kw_only=True)
    class State:
        conv: List[torch.Tensor]
        temporal: torch.Tensor

        def at_layer_idx(self, layer: int):
            kwargs = {}
            for k, v in vars(self).items():
                if k == "conv" or k == "intermediate_conv_window":
                    kwargs[k] = [conv[layer] for conv in v]
                else:
                    kwargs[k] = v[layer]
            return type(self)(**kwargs)

        def mem_usage_bytes(self):
            return sum(
                get_tensor_size_bytes(getattr(self, f.name))
                for f in dataclasses.fields(self)
            )

    @dataclass(frozen=True, kw_only=True)
    class SpeculativeState(State):
        intermediate_ssm: torch.Tensor
        intermediate_conv_window: List[torch.Tensor]

    def __init__(
        self,
        *,
        size: int,
        spec_state_size: int,
        cache_params: BaseLinearStateParams,
        device: str,
        enable_memory_saver: bool = False,
        speculative_num_draft_tokens: Optional[int] = None,
    ):
        conv_state_shape = cache_params.shape.conv
        temporal_state_shape = cache_params.shape.temporal
        conv_dtype = cache_params.dtype.conv
        ssm_dtype = cache_params.dtype.temporal
        self.memory_saver_adapter = TorchMemorySaverAdapter.create(
            enable=enable_memory_saver
        )
        num_mamba_layers = len(cache_params.layers)

        self.size = size
        self.device = device

        # for disagg with nvlink
        self.enable_custom_mem_pool, self.custom_mem_pool, _ = (
            maybe_init_custom_mem_pool(device=self.device)
        )

        with self.memory_saver_adapter.region(), (
            torch.cuda.use_mem_pool(self.custom_mem_pool)
            if self.enable_custom_mem_pool
            else nullcontext()
        ):
            conv_state = [
                torch.zeros(
                    size=(num_mamba_layers, size + 1) + conv_shape,
                    dtype=conv_dtype,
                    device=device,
                )
                for conv_shape in conv_state_shape
            ]

            if _is_cpu and _cpu_has_amx_support:
                from sglang.srt.layers.amx_utils import _init_amx_conv_state

                # CPU uses a different layout of conv_state for kernel optimization
                conv_state = _init_amx_conv_state(conv_state)

            temporal_state = torch.zeros(
                size=(num_mamba_layers, size + 1) + temporal_state_shape,
                dtype=ssm_dtype,
                device=device,
            )
            if speculative_num_draft_tokens is not None:
                # Cache intermediate SSM states per draft token during target verify
                # Shape: [num_layers, size + 1, speculative_num_draft_tokens, HV, K, V]
                intermediate_ssm_state_cache = torch.zeros(
                    size=(
                        num_mamba_layers,
                        spec_state_size + 1,
                        speculative_num_draft_tokens,
                        temporal_state_shape[0],
                        temporal_state_shape[1],
                        temporal_state_shape[2],
                    ),
                    dtype=ssm_dtype,
                    device="cuda",
                )
                # Cache intermediate conv windows (last K-1 inputs) per draft token during target verify
                # Shape: [num_layers, size + 1, speculative_num_draft_tokens, dim, K-1]
                intermediate_conv_window_cache = [
                    torch.zeros(
                        size=(
                            num_mamba_layers,
                            spec_state_size + 1,
                            speculative_num_draft_tokens,
                            conv_shape[0],
                            conv_shape[1],
                        ),
                        dtype=conv_dtype,
                        device="cuda",
                    )
                    for conv_shape in conv_state_shape
                ]
                self.mamba_cache = self.SpeculativeState(
                    conv=conv_state,
                    temporal=temporal_state,
                    intermediate_ssm=intermediate_ssm_state_cache,
                    intermediate_conv_window=intermediate_conv_window_cache,
                )
                logger.info(
                    f"Mamba Cache is allocated. "
                    f"max_mamba_cache_size: {size}, "
                    f"conv_state size: {get_tensor_size_bytes(conv_state) / GB:.2f}GB, "
                    f"ssm_state size: {get_tensor_size_bytes(temporal_state) / GB:.2f}GB "
                    f"intermediate_ssm_state_cache size: {get_tensor_size_bytes(intermediate_ssm_state_cache) / GB:.2f}GB "
                    f"intermediate_conv_window_cache size: {get_tensor_size_bytes(intermediate_conv_window_cache) / GB:.2f}GB "
                )
            else:
                self.mamba_cache = self.State(conv=conv_state, temporal=temporal_state)
                logger.info(
                    f"Mamba Cache is allocated. "
                    f"max_mamba_cache_size: {size}, "
                    f"conv_state size: {get_tensor_size_bytes(conv_state) / GB:.2f}GB, "
                    f"ssm_state size: {get_tensor_size_bytes(temporal_state) / GB:.2f}GB "
                )
            # The padded slot 0 is used for writing dummy outputs from padded tokens.
            self.free_slots = torch.arange(
                1, self.size + 1, dtype=torch.int64, device=self.device
            )
            self.mem_usage = self.mamba_cache.mem_usage_bytes() / GB
            self.num_mamba_layers = num_mamba_layers

        # BACKPORT-PPU: SGLang 0.5.13 batches waiting-request Mamba slot
        # allocation.  During a group window alloc(1) consumes this iterator,
        # avoiding one device slice/update sequence per request.
        self._alloc_iter: Optional[Iterator] = None

    def get_speculative_mamba2_params_all_layers(self) -> SpeculativeState:
        assert isinstance(self.mamba_cache, self.SpeculativeState)
        return self.mamba_cache

    def mamba2_layer_cache(self, layer_id: int):
        return self.mamba_cache.at_layer_idx(layer_id)

    def available_size(self):
        return len(self.free_slots)

    def alloc_group_begin(self, num_reqs: int):
        self._alloc_iter = None
        if num_reqs > 0:
            result = self._do_alloc(num_reqs)
            if result is not None:
                self._alloc_iter = iter(result.split(1))

    def alloc_group_end(self):
        if self._alloc_iter is not None:
            remaining = list(self._alloc_iter)
            if remaining:
                self.free(torch.cat(remaining))
        self._alloc_iter = None

    def alloc(self, need_size: int) -> Optional[torch.Tensor]:
        if self._alloc_iter is not None and need_size == 1:
            slot = next(self._alloc_iter, None)
            if slot is not None:
                return slot
        return self._do_alloc(need_size)

    def _do_alloc(self, need_size: int) -> Optional[torch.Tensor]:
        if need_size > len(self.free_slots):
            return None

        select_index = self.free_slots[:need_size]
        self.free_slots = self.free_slots[need_size:]
        # clear at alloc time, fill allocated slots with zeros
        for i in range(len(self.mamba_cache.conv)):
            self.mamba_cache.conv[i][:, select_index] = 0
        self.mamba_cache.temporal[:, select_index] = 0

        return select_index

    def free(self, free_index: torch.Tensor):
        if free_index.numel() == 0:
            return
        self.free_slots = torch.cat((self.free_slots, free_index))

    def clear(self):
        self.free_slots = torch.arange(
            1, self.size + 1, dtype=torch.int64, device=self.device
        )

    def copy_from(self, src_index: torch.Tensor, dst_index: torch.Tensor):
        for i in range(len(self.mamba_cache.conv)):
            self.mamba_cache.conv[i][:, dst_index] = self.mamba_cache.conv[i][
                :, src_index
            ]
        self.mamba_cache.temporal[:, dst_index] = self.mamba_cache.temporal[
            :, src_index
        ]
        return

    def fork_from(self, src_index: torch.Tensor) -> Optional[torch.Tensor]:
        dst_index = self.alloc(1)
        if dst_index == None:
            return None
        self.copy_from(src_index, dst_index)
        return dst_index

    def get_contiguous_buf_infos(self):
        """
        Get buffer info for RDMA registration.
        Only returns conv and temporal state buffers, excluding intermediate buffers
        used for speculative decoding (intermediate_ssm, intermediate_conv_window).
        """
        state_tensors = []
        for field in vars(self.mamba_cache):
            # Skip intermediate buffers used only for speculative decoding
            # These buffers have different size (spec_state_size + 1) and should not be transferred
            if field in ("intermediate_ssm", "intermediate_conv_window"):
                continue
            value = getattr(self.mamba_cache, field)
            if isinstance(value, list):
                state_tensors.extend(value)
            else:
                state_tensors.append(value)
        data_ptrs, data_lens, item_lens = [], [], []

        for _, state_tensor in enumerate(state_tensors):
            data_ptrs += [
                state_tensor[i].data_ptr() for i in range(self.num_mamba_layers)
            ]
            data_lens += [state_tensor[i].nbytes for i in range(self.num_mamba_layers)]
            item_lens += [
                state_tensor[i][0].nbytes for i in range(self.num_mamba_layers)
            ]
        return data_ptrs, data_lens, item_lens

    def get_state_dim_per_tensor(self):
        """Get the sliceable dimension size for each state tensor.

        For mamba state, the layout is:
        - conv_state: [num_layers, size+1, conv_dim/tp, conv_kernel-1]
        - temporal_state: [num_layers, size+1, num_heads/tp, head_dim, state_size]

        The 3rd dimension (index 2) is the one that gets sliced by TP.
        Returns the size of this dimension for each tensor (repeated for each layer).
        """
        state_tensors = []
        for field in vars(self.mamba_cache):
            value = getattr(self.mamba_cache, field)
            if isinstance(value, list):
                state_tensors.extend(value)
            else:
                state_tensors.append(value)

        dim_per_tensor = []
        for state_tensor in state_tensors:
            # state_tensor shape: [num_layers, size+1, sliceable_dim, ...]
            # The sliceable dimension is at index 2 (after num_layers and size)
            sliceable_dim = state_tensor.shape[2]
            # Repeat for each layer since we have per-layer data_ptrs
            dim_per_tensor += [sliceable_dim] * self.num_mamba_layers
        return dim_per_tensor


class HybridReqToTokenPool(ReqToTokenPool):
    """A memory pool that maps a request to its token locations."""

    def __init__(
        self,
        *,
        size: int,
        mamba_size: int,
        mamba_spec_state_size: int,
        max_context_len: int,
        device: str,
        enable_memory_saver: bool,
        cache_params: BaseLinearStateParams,
        enable_mamba_extra_buffer: bool,
        speculative_num_draft_tokens: int = None,
    ):
        super().__init__(
            size=size,
            max_context_len=max_context_len,
            device=device,
            enable_memory_saver=enable_memory_saver,
        )
        self.mamba_ping_pong_track_buffer_size = (
            2 if speculative_num_draft_tokens is None else 1
        )
        self.enable_mamba_extra_buffer = enable_mamba_extra_buffer
        self.enable_memory_saver = enable_memory_saver
        self._init_mamba_pool(
            size=mamba_size,
            mamba_spec_state_size=mamba_spec_state_size,
            cache_params=cache_params,
            device=device,
            enable_mamba_extra_buffer=enable_mamba_extra_buffer,
            speculative_num_draft_tokens=speculative_num_draft_tokens,
        )

    def _init_mamba_pool(
        self,
        size: int,
        mamba_spec_state_size: int,
        cache_params: BaseLinearStateParams,
        device: str,
        enable_mamba_extra_buffer: bool,
        speculative_num_draft_tokens: int = None,
    ):
        self.mamba_pool = MambaPool(
            size=size,
            spec_state_size=mamba_spec_state_size,
            cache_params=cache_params,
            device=device,
            enable_memory_saver=self.enable_memory_saver,
            speculative_num_draft_tokens=speculative_num_draft_tokens,
        )
        self.mamba_map = {layer_id: i for i, layer_id in enumerate(cache_params.layers)}

        self.device = device
        # BACKPORT-PPU: this table is indexed by ``req_pool_idx`` (the
        # request-token pool), not by the Mamba state index.  ``mamba_size``
        # can be smaller than the request pool capacity, which previously
        # caused an IndexError after enough requests had been recycled.
        self.req_index_to_mamba_index_mapping: torch.Tensor = torch.zeros(
            self.size, dtype=torch.int32, device=self.device
        )
        if enable_mamba_extra_buffer:
            self.req_index_to_mamba_ping_pong_track_buffer_mapping: torch.Tensor = (
                torch.zeros(
                    (self.size, self.mamba_ping_pong_track_buffer_size),
                    dtype=torch.int32,
                    device=self.device,
                )
            )

    # BACKPORT: v0.5.9 ReqToTokenPool.alloc(reqs) semantics, inlined here
    # because the 0.4.6 base class uses alloc(need_size) semantics.
    def _alloc_req_slots(self, reqs: list) -> Optional[List[int]]:
        chunked = [i for i, r in enumerate(reqs) if r.req_pool_idx is not None]
        if not any(getattr(r, "is_dllm", lambda: False)() for r in reqs):
            assert (
                len(chunked) <= 1
            ), "only one chunked request may reuse req_pool_idx in a batch"
        assert all(
            reqs[i].is_chunked > 0 or reqs[i].kv_committed_len > 0 for i in chunked
        ), "request has req_pool_idx but is not chunked"

        need_size = len(reqs) - len(chunked)
        if need_size > len(self.free_slots):
            return None
        select_index = self.free_slots[:need_size]
        self.free_slots = self.free_slots[need_size:]
        offset = 0
        for r in reqs:
            if r.req_pool_idx is None:
                r.req_pool_idx = select_index[offset]
                offset += 1
        return [r.req_pool_idx for r in reqs]

    # For chunk prefill req, we do not need to allocate mamba cache,
    # We could use allocated mamba cache instead.
    # BACKPORT: accept the 0.4.6 alloc(need_size: int) call style too — the
    # 0.4.6 scheduler allocates req slots by count and assigns req_pool_idx
    # itself; mamba slots are then allocated via alloc_mamba_for_req below.
    def alloc(self, reqs: Union[int, list]) -> Optional[List[int]]:
        if isinstance(reqs, int):
            return super().alloc(reqs)
        select_index = self._alloc_req_slots(reqs)
        if select_index is None:
            return None

        mamba_index = []
        mamba_ping_pong_track_buffer_list = []
        for req in reqs:
            mid = None
            if req.mamba_pool_idx is not None:  # for radix cache
                mid = req.mamba_pool_idx
            else:
                mid = self.mamba_pool.alloc(1)
                assert (
                    mid is not None
                ), f"Not enough space for mamba cache, try to increase --mamba-full-memory-ratio or --max-mamba-cache-size. {mid=}, {self.mamba_pool.size=}, {self.mamba_pool.available_size()=}, {len(reqs)=}"
                mid = mid[0]
                req.mamba_pool_idx = mid
            mamba_index.append(mid)
            if self.enable_mamba_extra_buffer:
                if req.mamba_ping_pong_track_buffer is None:
                    req.mamba_ping_pong_track_buffer = self.mamba_pool.alloc(
                        self.mamba_ping_pong_track_buffer_size
                    )
                    assert (
                        req.mamba_ping_pong_track_buffer is not None
                    ), "Not enough space for mamba ping pong idx, try to increase --mamba-full-memory-ratio."
                    req.mamba_next_track_idx = 0
                mamba_ping_pong_track_buffer_list.append(
                    req.mamba_ping_pong_track_buffer.tolist()
                )
        assert len(select_index) == len(
            mamba_index
        ), f"Not enough space for mamba cache, try to increase --mamba-full-memory-ratio or --max-mamba-cache-size."
        if self.enable_mamba_extra_buffer:
            assert len(select_index) == len(
                mamba_ping_pong_track_buffer_list
            ), f"Not enough space for mamba ping pong idx, try to increase --mamba-full-memory-ratio."
        self.req_index_to_mamba_index_mapping[select_index] = torch.tensor(
            mamba_index, dtype=torch.int32, device=self.device
        )
        if self.enable_mamba_extra_buffer:
            self.req_index_to_mamba_ping_pong_track_buffer_mapping[select_index] = (
                torch.tensor(
                    mamba_ping_pong_track_buffer_list,
                    dtype=torch.int32,
                    device=self.device,
                )
            )
        return select_index

    # BACKPORT: 0.4.6-scheduler-facing mamba slot allocation. Called from
    # ScheduleBatch.prepare_for_extend after req.req_pool_idx is assigned.
    def alloc_mamba_for_req(self, req):
        if req.mamba_pool_idx is None:
            mid = self.mamba_pool.alloc(1)
            assert (
                mid is not None
            ), "Not enough space for mamba cache, try to increase --mamba-full-memory-ratio or --max-mamba-cache-size."
            req.mamba_pool_idx = mid[0]
        self.req_index_to_mamba_index_mapping[req.req_pool_idx] = req.mamba_pool_idx

    # BACKPORT: v0.5.9 ReqToTokenPool.free(req) semantics; the 0.4.6 base
    # class frees by index. Provided as free_req to keep both call styles
    # available on this hybrid pool.
    def free_req(self, req):
        assert req.req_pool_idx is not None, "request must have req_pool_idx"
        self.free_slots.append(req.req_pool_idx)
        req.req_pool_idx = None

    def get_mamba_indices(self, req_indices: torch.Tensor) -> torch.Tensor:
        return self.req_index_to_mamba_index_mapping[req_indices]

    def mamba2_layer_cache(self, layer_id: int):
        assert layer_id in self.mamba_map
        return self.mamba_pool.mamba2_layer_cache(self.mamba_map[layer_id])

    def get_speculative_mamba2_params_all_layers(self) -> MambaPool.SpeculativeState:
        return self.mamba_pool.get_speculative_mamba2_params_all_layers()

    def get_mamba_ping_pong_other_idx(self, mamba_next_track_idx: int) -> int:
        if self.mamba_ping_pong_track_buffer_size == 2:
            return 1 - mamba_next_track_idx
        else:
            return mamba_next_track_idx

    def free_mamba_cache(
        self, req, mamba_ping_pong_track_buffer_to_keep: Optional[int] = None
    ):
        mamba_index = req.mamba_pool_idx
        assert mamba_index is not None, "double free? mamba_index is None"
        self.mamba_pool.free(mamba_index.unsqueeze(0))
        req.mamba_pool_idx = None

        if self.enable_mamba_extra_buffer:
            mamba_ping_pong_track_buffer_to_free = (
                self.req_index_to_mamba_ping_pong_track_buffer_mapping[req.req_pool_idx]
            )
            if mamba_ping_pong_track_buffer_to_keep is not None:
                assert mamba_ping_pong_track_buffer_to_keep in [
                    0,
                    1,
                ], f"mamba_ping_pong_track_buffer_to_keep must be 0 or 1, {mamba_ping_pong_track_buffer_to_keep=}"
                idx_to_free = list(range(self.mamba_ping_pong_track_buffer_size))
                idx_to_free.remove(mamba_ping_pong_track_buffer_to_keep)
                mamba_ping_pong_track_buffer_to_free = (
                    mamba_ping_pong_track_buffer_to_free[idx_to_free]
                )
            self.mamba_pool.free(mamba_ping_pong_track_buffer_to_free)

    def clear(self):
        logger.info("Reset HybridReqToTokenPool")
        super().clear()
        self.mamba_pool.clear()
        self.req_index_to_mamba_index_mapping.zero_()
        if self.enable_mamba_extra_buffer:
            self.req_index_to_mamba_ping_pong_track_buffer_mapping.zero_()


class HybridLinearKVPool(KVCache):
    """KV cache with separate pools for full and linear attention layers."""

    def __init__(
        self,
        size: int,
        dtype: torch.dtype,
        page_size: int,
        head_num: int,
        head_dim: int,
        full_attention_layer_ids: List[int],
        enable_kvcache_transpose: bool,
        device: str,
        mamba_pool: MambaPool,
        enable_memory_saver: bool = False,
        # TODO: refactor mla related args
        use_mla: bool = False,
        kv_lora_rank: int = None,
        qk_rope_head_dim: int = None,
    ):
        self.size = size
        self.dtype = dtype
        self.device = device
        self.full_layer_nums = len(full_attention_layer_ids)
        self.page_size = page_size
        # TODO support pp?
        self.start_layer = 0
        self.head_num = head_num
        self.head_dim = head_dim
        self.mamba_pool = mamba_pool
        # TODO MHATransposedTokenToKVPool if enable_kvcache_transpose is True
        assert not enable_kvcache_transpose
        self.use_mla = use_mla
        if not use_mla:

            TokenToKVPoolClass = MHATokenToKVPool

            if _is_npu:
                from sglang.srt.hardware_backend.npu.memory_pool_npu import (
                    NPUMHATokenToKVPool,
                )

                TokenToKVPoolClass = NPUMHATokenToKVPool

            self.full_kv_pool = TokenToKVPoolClass(
                size=size,
                page_size=self.page_size,
                dtype=dtype,
                head_num=head_num,
                head_dim=head_dim,
                layer_num=self.full_layer_nums,
                device=device,
                enable_memory_saver=enable_memory_saver,
            )
        else:

            TokenToKVPoolClass = MLATokenToKVPool

            if _is_npu:
                from sglang.srt.hardware_backend.npu.memory_pool_npu import (
                    NPUMLATokenToKVPool,
                )

                TokenToKVPoolClass = NPUMLATokenToKVPool

            self.full_kv_pool = TokenToKVPoolClass(
                size=size,
                page_size=self.page_size,
                dtype=dtype,
                layer_num=self.full_layer_nums,
                device=device,
                kv_lora_rank=kv_lora_rank,
                qk_rope_head_dim=qk_rope_head_dim,
                enable_memory_saver=enable_memory_saver,
            )
        self.full_attention_layer_id_mapping = {
            id: i for i, id in enumerate(full_attention_layer_ids)
        }
        if use_mla:
            self.mem_usage = self.get_kv_size_bytes() / GB
        else:
            k_size, v_size = self.get_kv_size_bytes()
            self.mem_usage = (k_size + v_size) / GB

    def get_kv_size_bytes(self):
        return self.full_kv_pool.get_kv_size_bytes()

    def get_contiguous_buf_infos(self):
        return self.full_kv_pool.get_contiguous_buf_infos()

    def get_state_buf_infos(self):
        mamba_data_ptrs, mamba_data_lens, mamba_item_lens = (
            self.mamba_pool.get_contiguous_buf_infos()
        )
        return mamba_data_ptrs, mamba_data_lens, mamba_item_lens

    def get_state_dim_per_tensor(self):
        """Get the sliceable dimension size for each mamba state tensor."""
        return self.mamba_pool.get_state_dim_per_tensor()

    def maybe_get_custom_mem_pool(self):
        return self.full_kv_pool.maybe_get_custom_mem_pool()

    def _transfer_full_attention_id(self, layer_id: int):
        if layer_id not in self.full_attention_layer_id_mapping:
            raise ValueError(
                f"{layer_id=} not in full attention layers: {self.full_attention_layer_id_mapping.keys()}"
            )
        return self.full_attention_layer_id_mapping[layer_id]

    def get_key_buffer(self, layer_id: int):
        layer_id = self._transfer_full_attention_id(layer_id)
        return self.full_kv_pool.get_key_buffer(layer_id)

    def get_value_buffer(self, layer_id: int):
        layer_id = self._transfer_full_attention_id(layer_id)
        return self.full_kv_pool.get_value_buffer(layer_id)

    def get_kv_buffer(self, layer_id: int):
        layer_id = self._transfer_full_attention_id(layer_id)
        return self.full_kv_pool.get_kv_buffer(layer_id)

    @contextmanager
    def _transfer_id_context(self, layer: RadixAttention):

        @contextmanager
        def _patch_layer_id(layer):
            original_layer_id = layer.layer_id
            layer.layer_id = self._transfer_full_attention_id(layer.layer_id)
            try:
                yield
            finally:
                layer.layer_id = original_layer_id

        with _patch_layer_id(layer):
            yield

    def set_kv_buffer(
        self,
        layer: RadixAttention,
        loc: torch.Tensor,
        cache_k: torch.Tensor,
        cache_v: torch.Tensor,
        k_scale: float = 1.0,
        v_scale: float = 1.0,
    ):
        layer_id = self._transfer_full_attention_id(layer.layer_id)
        if not self.use_mla:
            self.full_kv_pool.set_kv_buffer(
                None,
                loc,
                cache_k,
                cache_v,
                k_scale,
                v_scale,
                layer_id_override=layer_id,
            )
        else:
            with self._transfer_id_context(layer):
                self.full_kv_pool.set_kv_buffer(
                    layer,
                    loc,
                    cache_k,
                    cache_v,
                )

    def move_kv_cache(self, tgt_loc: torch.Tensor, src_loc: torch.Tensor):
        self.full_kv_pool.move_kv_cache(tgt_loc, src_loc)

    def get_v_head_dim(self):
        return self.full_kv_pool.get_value_buffer(0).shape[-1]

    def set_mla_kv_buffer(
        self,
        layer: RadixAttention,
        loc: torch.Tensor,
        cache_k_nope: torch.Tensor,
        cache_k_rope: torch.Tensor,
    ):
        assert self.use_mla, "set_mla_kv_buffer called when use_mla is False"
        with self._transfer_id_context(layer):
            self.full_kv_pool.set_mla_kv_buffer(layer, loc, cache_k_nope, cache_k_rope)

    def get_mla_kv_buffer(
        self,
        layer: RadixAttention,
        loc: torch.Tensor,
        dst_dtype: Optional[torch.dtype] = None,
    ):
        assert self.use_mla, "get_mla_kv_buffer called when use_mla is False"
        with self._transfer_id_context(layer):
            return self.full_kv_pool.get_mla_kv_buffer(layer, loc, dst_dtype)

    # SLIM: removed get_flat_data / transfer / transfer_per_layer
    # NotImplementedError stubs (fixed Qwen3.5-2B config: no PD disaggregation
    # host transfer; the KVCache ABC no longer declares them)
