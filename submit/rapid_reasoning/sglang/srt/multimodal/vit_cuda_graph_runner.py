# Copyright 2023-2025 SGLang Team
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""ViT CUDA Graph Runner class."""

from __future__ import annotations

import inspect
import os
import sys
import time
from typing import Dict, Hashable, List, Optional, Tuple

import torch
import torch.nn as nn

from sglang.srt.layers.attention.vision import VisionAttention
from sglang.srt.server_args import get_global_server_args


class ViTCudaGraphRunner:
    """Generic ViT CUDA Graph Runner.

    This runner captures the "blocks + merger + deepstack merger (optional)" part
    of a vision transformer into a CUDA graph and replays it for identical shapes.

    Optional for Qwen2.5 windowed attention:
      - vit.fullatt_block_indexes: Sequence[int]
      - run() provides both cu_seqlens and cu_window_seqlens

    Optional for Qwen3 deepstack:
      - vit.deepstack_vision_indexes: Sequence[int]
      - vit.deepstack_merger_list: nn.ModuleList (same length as deepstack_vision_indexes)
    """

    def __init__(
        self,
        vit: nn.Module,
    ) -> None:
        self.vit = vit

        # graph_key -> buffers / graphs
        self.block_input: Dict[Hashable, torch.Tensor] = {}
        self.block_ws: Dict[Hashable, torch.Tensor] = {}
        self.block_graphs: Dict[Hashable, torch.cuda.CUDAGraph] = {}
        self.block_output: Dict[Hashable, torch.Tensor] = {}

        # captured seqlens buffers (addresses must be stable for cuda-graph replay)
        self.cu_full_len: Dict[Hashable, torch.Tensor] = {}
        self.cu_window_len: Dict[Hashable, torch.Tensor] = {}
        self.cu_full_len_kk: Dict[Hashable, torch.Tensor] = {}
        self.cu_window_len_kk: Dict[Hashable, torch.Tensor] = {}

        # BACKPORT: per-graph rotary buffers. Upstream shares one buffer pair
        # across all graphs and reallocates it when a larger seq_len arrives;
        # reallocation moves the storage address, silently corrupting every
        # previously captured graph that still reads the old (freed) address.
        # Buffers also follow the incoming cos/sin dtype (fp32 on this tree)
        # instead of self.dtype, to stay bit-identical with the eager path.
        self.sin_cos_ws: Dict[Hashable, Tuple[torch.Tensor, torch.Tensor]] = {}

        # Qwen2.5-VL specific viarable.
        self._fullatt_block_indexes = set(getattr(vit, "fullatt_block_indexes", ()))

        # Qwen3-VL specific variables.
        self._deepstack_visual_indexes = list(
            getattr(vit, "deepstack_visual_indexes", []) or []
        )
        self._deepstack_merger_list = getattr(vit, "deepstack_merger_list", None)

        first_blk = vit.blocks[0]
        self._blk_accepts_output_ws = (
            "output_ws" in inspect.signature(first_blk.forward).parameters
        )

        self._attn: Optional[VisionAttention] = getattr(first_blk, "attn", None)
        self._attn_backend = getattr(self._attn, "qkv_backend", None)

    @property
    def device(self) -> torch.device:
        return self.vit.device

    @property
    def dtype(self) -> torch.dtype:
        return self.vit.dtype

    def _get_rotary_ws(
        self,
        graph_key: Hashable,
        cos: torch.Tensor,
        sin: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        # BACKPORT: allocate once per graph_key (stable addresses) and refresh
        # the content on every call.
        if graph_key not in self.sin_cos_ws:
            self.sin_cos_ws[graph_key] = (torch.empty_like(cos), torch.empty_like(sin))
        cos_ws, sin_ws = self.sin_cos_ws[graph_key]
        cos_ws.copy_(cos)
        sin_ws.copy_(sin)
        return cos_ws, sin_ws

    def _update_cu_seqlens(self, graph_key: Hashable, cu_seqlens: torch.Tensor):
        # BACKPORT: keep per-graph device buffers at stable addresses and
        # refresh their content on every call, so bucketed replays with a
        # different real length update the segmentation seen by the captured
        # kernels (upstream stored the first sample's tensors, which freezes
        # cu_seqlens at capture time).
        kk = cu_seqlens[1:] - cu_seqlens[:-1]
        if graph_key not in self.cu_full_len:
            self.cu_full_len[graph_key] = cu_seqlens.clone()
            self.cu_full_len_kk[graph_key] = kk.clone()
        else:
            self.cu_full_len[graph_key].copy_(cu_seqlens)
            self.cu_full_len_kk[graph_key].copy_(kk)

    def _get_graph_key(self, x_3d: torch.Tensor) -> int:
        # x_3d: [S, B, H], B=1, S as graph_key
        return x_3d.shape[0]

    def _create_graph(
        self,
        graph_key: int,
        position_embeddings: Optional[
            Tuple[torch.Tensor, torch.Tensor]
        ] = None,  # (cos, sin), [S, D]
        rotary_pos_emb_cos: Optional[torch.Tensor] = None,
        rotary_pos_emb_sin: Optional[torch.Tensor] = None,
    ):

        graph = torch.cuda.CUDAGraph()
        vit = self.vit

        # Qwen2.5-VL
        if self._fullatt_block_indexes:
            cu_window = self.cu_window_len[graph_key]
            cu_window_kk = self.cu_window_len_kk[graph_key]
            max_window_len = int(cu_window_kk.max().item())

        cu_full = self.cu_full_len[graph_key]
        cu_full_kk = self.cu_full_len_kk[graph_key]
        # BACKPORT: bake max_input_len = graph_key (the bucket size) instead of
        # the first sample's exact max segment length. graph_key is an upper
        # bound for any segment in the bucket, the triton kernel early-exits
        # extra programs via b_seq_len, and a stable value keeps replays with
        # different real lengths inside the same bucket correct.
        max_full_len = graph_key

        # BACKPORT: this slim 0.4.6 PPU tree only has the triton vision
        # context-attention backend (no fa3) and mm_attention_backend stays
        # None, so default to "triton_attn" instead of raising.
        override_backend = get_global_server_args().mm_attention_backend
        if override_backend is None:
            override_backend = "triton_attn"

        with torch.cuda.graph(graph):
            y = None
            deepstack_outs: List[torch.Tensor] = []
            deepstack_capture_idx = 0

            for layer_num, blk in enumerate(vit.blocks):
                if self._fullatt_block_indexes:
                    if layer_num in vit.fullatt_block_indexes:
                        cu_seqlens_now = cu_full
                        cu_seqlens_kk_now = cu_full_kk
                        max_len = max_full_len
                    else:
                        cu_seqlens_now = cu_window
                        cu_seqlens_kk_now = cu_window_kk
                        max_len = max_window_len
                else:
                    cu_seqlens_now = cu_full
                    cu_seqlens_kk_now = cu_full_kk
                    max_len = max_full_len

                if override_backend == "triton_attn":
                    cu_seq_len_ws = [cu_seqlens_now, cu_seqlens_kk_now, max_len]
                elif override_backend == "fa3":
                    cu_seq_len_ws = [cu_seqlens_now, max_len]
                else:
                    raise RuntimeError("Not supported ViT attention backend")

                if position_embeddings is not None:
                    if layer_num == 0:
                        y = blk(
                            self.block_input[graph_key],
                            cu_seqlens=cu_seq_len_ws,
                            position_embeddings=position_embeddings,
                            output_ws=self.block_ws[graph_key],
                        )
                    else:
                        y = blk(
                            y,
                            cu_seqlens=cu_seq_len_ws,
                            position_embeddings=position_embeddings,
                            output_ws=self.block_ws[graph_key],
                        )
                elif rotary_pos_emb_cos is not None and rotary_pos_emb_sin is not None:
                    if layer_num == 0:
                        y = blk(
                            self.block_input[graph_key],
                            cu_seqlens=cu_seq_len_ws,
                            rotary_pos_emb_cos=rotary_pos_emb_cos,
                            rotary_pos_emb_sin=rotary_pos_emb_sin,
                            output_ws=self.block_ws[graph_key],
                        )
                    else:
                        y = blk(
                            y,
                            cu_seqlens=cu_seq_len_ws,
                            rotary_pos_emb_cos=rotary_pos_emb_cos,
                            rotary_pos_emb_sin=rotary_pos_emb_sin,
                            output_ws=self.block_ws[graph_key],
                        )

                # Optional deepstack support (Qwen3-VL)
                if (
                    self._deepstack_visual_indexes
                    and layer_num in self._deepstack_visual_indexes
                ):
                    if self._deepstack_merger_list is None:
                        raise RuntimeError(
                            "deepstack_visual_indexes exists but deepstack_merger_list is missing."
                        )
                    deepstack_out = self._deepstack_merger_list[deepstack_capture_idx](
                        y
                    )
                    deepstack_outs.append(deepstack_out)
                    deepstack_capture_idx += 1

            main_out = vit.merger(y)

            if deepstack_outs:
                self.block_output[graph_key] = torch.cat(
                    [main_out] + deepstack_outs, dim=1
                )
            else:
                self.block_output[graph_key] = main_out

        self.block_graphs[graph_key] = graph

    def create_graph(
        self,
        x_3d: torch.Tensor,  # [S, 1, H]
        cu_seqlens: torch.Tensor,
        cu_window_seqlens: torch.Tensor,
        position_embeddings: Optional[
            Tuple[torch.Tensor, torch.Tensor]
        ],  # (cos, sin), [S, D]
        rotary_pos_emb_cos: Optional[torch.Tensor] = None,
        rotary_pos_emb_sin: Optional[torch.Tensor] = None,
    ) -> int:
        vit = self.vit
        graph_key = self._get_graph_key(x_3d)

        if graph_key in self.block_graphs:
            return graph_key

        # pre-allocate workspace
        attn_module: VisionAttention = vit.blocks[0].attn
        num_heads = attn_module.num_attention_heads_per_partition
        attn_head_dim = attn_module.head_size

        if graph_key not in self.block_output:
            self.block_output[graph_key] = torch.empty_like(
                x_3d, device=self.device
            ).contiguous()
            self.block_input[graph_key] = torch.empty_like(
                x_3d, device=self.device
            ).contiguous()
            self.block_ws[graph_key] = torch.empty(
                graph_key,
                num_heads,
                attn_head_dim,
                device=self.device,
                dtype=self.dtype,
            )

        # Qwen2.5-VL
        if self._fullatt_block_indexes:
            if graph_key not in self.cu_window_len:
                self.cu_window_len[graph_key] = cu_window_seqlens
                self.cu_full_len[graph_key] = cu_seqlens
                self.cu_window_len_kk[graph_key] = (
                    cu_window_seqlens[1:] - cu_window_seqlens[:-1]
                )
                self.cu_full_len_kk[graph_key] = cu_seqlens[1:] - cu_seqlens[:-1]
        else:
            self._update_cu_seqlens(graph_key, cu_seqlens)

        # One line per capture so runs can count them (stderr).
        print(f"VITGRAPH capture bucket={graph_key}", file=sys.stderr, flush=True)

        if position_embeddings is not None:
            persist_position_embeddings = self._get_rotary_ws(
                graph_key, position_embeddings[0], position_embeddings[1]
            )
            self._create_graph(
                graph_key=graph_key, position_embeddings=persist_position_embeddings
            )
        elif rotary_pos_emb_cos is not None and rotary_pos_emb_sin is not None:
            used_cos_ws, used_sin_ws = self._get_rotary_ws(
                graph_key, rotary_pos_emb_cos, rotary_pos_emb_sin
            )
            self._create_graph(
                graph_key=graph_key,
                position_embeddings=None,
                rotary_pos_emb_cos=used_cos_ws,
                rotary_pos_emb_sin=used_sin_ws,
            )

        return graph_key

    def replay(
        self,
        graph_key: int,
        x_3d: torch.Tensor,
        position_embeddings: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,
        rotary_pos_emb_cos: Optional[torch.Tensor] = None,
        rotary_pos_emb_sin: Optional[torch.Tensor] = None,
        output_indices: Optional[torch.Tensor] = None,
        cu_seqlens: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:

        # BACKPORT: refresh segmentation for bucketed replays (no-op for the
        # Qwen2.5-VL window path, which keeps capture-time tensors).
        if cu_seqlens is not None and not self._fullatt_block_indexes:
            self._update_cu_seqlens(graph_key, cu_seqlens)

        if position_embeddings is not None:
            # update rotary workspace content
            self._get_rotary_ws(
                graph_key, position_embeddings[0], position_embeddings[1]
            )
        elif rotary_pos_emb_cos is not None and rotary_pos_emb_sin is not None:
            # update rotary workspace content
            self._get_rotary_ws(graph_key, rotary_pos_emb_cos, rotary_pos_emb_sin)

        # copy input
        self.block_input[graph_key].copy_(x_3d)

        # replay
        self.block_graphs[graph_key].replay()

        out = self.block_output[graph_key]

        # Optional output reordering (Qwen2.5-VL window permutation inverse)
        if output_indices is not None:
            out = out.index_select(0, output_indices)

        return out

    def run(
        self,
        x: torch.Tensor,
        cu_seqlens: torch.Tensor,
        cu_window_seqlens: torch.Tensor,
        position_embeddings: Optional[Tuple[torch.Tensor, torch.Tensor]],
        rotary_pos_emb_cos: Optional[torch.Tensor] = None,
        rotary_pos_emb_sin: Optional[torch.Tensor] = None,
        output_indices: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        # x: [seq_len, hidden] -> [S, B=1, H]
        x_3d = x.unsqueeze(1)
        graph_key = self._get_graph_key(x_3d)

        if graph_key not in self.block_graphs:
            self.create_graph(
                x_3d=x_3d,
                position_embeddings=position_embeddings,
                cu_seqlens=cu_seqlens,
                cu_window_seqlens=cu_window_seqlens,
                rotary_pos_emb_cos=rotary_pos_emb_cos,
                rotary_pos_emb_sin=rotary_pos_emb_sin,
            )

        return self.replay(
            graph_key=graph_key,
            x_3d=x_3d,
            position_embeddings=position_embeddings,
            rotary_pos_emb_cos=rotary_pos_emb_cos,
            rotary_pos_emb_sin=rotary_pos_emb_sin,
            output_indices=output_indices,
            cu_seqlens=cu_seqlens,
        )

    def warmup_buckets(self, lo: int = 256, hi: int = 1024, step: int = 64) -> int:
        # BACKPORT: pre-capture the standard patch buckets at engine init so
        # benchmark shapes all hit replay instead of paying ~0.2s per new
        # shape mid-run. Each bucket uses a synthetic single-image grid
        # [1, 8, B/8] (8 and B/8 are even, so merger 2x2 groups stay legal and
        # S == B exactly) pushed through the real forward_with_cuda_graph
        # pad+capture path; capture only records kernel topology, so the dummy
        # zero pixels are irrelevant. A bucket that fails to capture is
        # skipped and falls back to on-demand capture on first real use.
        vit = self.vit
        pe = vit.patch_embed
        patch_dim = pe.in_channels * pe.temporal_patch_size * pe.patch_size**2

        t0 = time.perf_counter()
        captured = 0
        step = int(os.environ.get("SGLANG_VIT_GRAPH_BUCKET_STEP", str(step)))
        if step not in (32, 64, 128):
            raise ValueError("SGLANG_VIT_GRAPH_BUCKET_STEP must be 32, 64, or 128")
        for bucket in range(lo, hi + 1, step):
            if bucket in self.block_graphs:
                continue
            try:
                pixel_values = torch.zeros(
                    bucket, patch_dim, device=self.device, dtype=self.dtype
                )
                # explicit CPU: model init may run under a cuda default device
                grid_thw = torch.tensor(
                    [[1, 8, bucket // 8]], dtype=torch.int64, device="cpu"
                )
                vit.forward_with_cuda_graph(pixel_values, grid_thw)
                captured += 1
            except Exception as e:
                print(
                    f"VITGRAPH warmup skip bucket={bucket}: {e!r}",
                    file=sys.stderr,
                    flush=True,
                )
        print(
            f"VITGRAPH warmup captured {captured} buckets "
            f"in {time.perf_counter() - t0:.1f}s",
            file=sys.stderr,
            flush=True,
        )
        return captured
