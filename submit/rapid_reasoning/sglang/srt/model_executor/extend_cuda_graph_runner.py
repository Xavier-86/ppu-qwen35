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
"""Run the model extend (prefill) step with CUDA graph capture/replay.

BACKPORT-PPU: opt-in prototype (SGLANG_EXTEND_GRAPH=1, default off) for the
fixed Qwen3.5-2B PPU path — bs=1, pure prefill (no prefix, no chunked
prefill, no logprob), using a small set of token buckets. The prefill is launch-bound
(~29ms for ~244 tokens), so capturing the whole language-model forward plus
the logits head removes per-kernel launch overhead.

Design notes:
- Static shapes: every request is padded to BUCKET tokens. The padded token
  block is modeled as a second logical segment and a third zero-length
  segment supplies one safe dummy chunk when the real/pad split is aligned.
  The cu_seqlens / qo_indptr / query_start_loc buffers therefore read
  [0, real, BUCKET, BUCKET] and only element [1] changes between replays.
- The fla chunked-GDN kernels derive their grid from prepare_chunk_indices(
  cu_seqlens, chunk_size), which syncs on GPU content and caches by object
  identity. Fixed-address maximum-size index/offset buffers are injected at
  capture and refreshed from the CPU `real` length before replay. Their valid
  entries exactly match eager; only an aligned split needs one masked dummy
  entry assigned to the zero-length third segment.
- The pad segment's state writes go to scratch slots that no real request
  ever reads: KV pool slot 0 (padded dummy slot, never allocated) and mamba
  pool slot 0 (free_slots start at 1). The pad rows' outputs are discarded:
  the logits head gathers row real-1 and the FULL hidden-states output is
  sliced to [:real].
- The multimodal embed merge (ViT + masked_scatter) keeps running eagerly
  outside the graph; replay() writes the merged embeddings into the static
  input_embeds buffer, replicating general_mm_embed_routine numerics.
"""

from __future__ import annotations

import logging
import os
import sys
import time

import torch

from sglang.srt.distributed.parallel_state import graph_capture
from sglang.srt.layers.attention.fla.index import set_chunk_layout_override
from sglang.srt.layers.logits_processor import LogitsProcessorOutput
from sglang.srt.managers.mm_utils import embed_mm_inputs
from sglang.srt.model_executor.cuda_graph_runner import CudaGraphRunner
from sglang.srt.model_executor.forward_batch_info import (
    CaptureHiddenMode,
    ForwardBatch,
    ForwardMode,
)

logger = logging.getLogger(__name__)


def _capture_len_for_bucket(bucket: int) -> int:
    value = int(os.environ.get("SGLANG_EXTEND_GRAPH_CAPTURE_LEN", "0"))
    mode = os.environ.get("SGLANG_EXTEND_GRAPH_CAPTURE_MODE", "half").strip().lower()
    if mode not in {"half", "full"}:
        raise ValueError(
            "SGLANG_EXTEND_GRAPH_CAPTURE_MODE must be 'half' or 'full', "
            f"got {mode!r}"
        )
    capture_len = value if value > 0 else (bucket if mode == "full" else bucket // 2)
    if not 1 <= capture_len <= bucket:
        raise ValueError(
            "SGLANG_EXTEND_GRAPH_CAPTURE_LEN must be in [1, bucket], "
            f"got {capture_len} for bucket {bucket}"
        )
    return capture_len


def _configured_buckets(default: tuple[int, ...]) -> tuple[int, ...]:
    raw = os.environ.get("SGLANG_EXTEND_GRAPH_BUCKETS", "").strip()
    if not raw:
        return default
    buckets = tuple(sorted({int(item.strip()) for item in raw.split(",") if item.strip()}))
    if not buckets or any(bucket <= 0 for bucket in buckets):
        raise ValueError(f"Invalid SGLANG_EXTEND_GRAPH_BUCKETS={raw!r}")
    return buckets


class _SingleBucketExtendCudaGraphRunner:
    """Captures and replays the bs=1 EXTEND forward for one bucket."""

    def __init__(self, model_runner, bucket: int):
        self.model_runner = model_runner
        self.bucket = bucket
        self.profile_ttft = os.environ.get("SGLANG_TTFT_PROF", "0") == "1"
        # CUDA graph construction may advance the default generators even
        # when the captured forward has no stochastic layers. Preserve both
        # RNG streams so graph setup is invisible to any later initialization.
        cpu_rng_state = torch.random.get_rng_state()
        cuda_rng_state = torch.cuda.get_rng_state(model_runner.device)
        # Capture with both segments non-empty so every kernel branch is
        # exercised; replay works for any real in [1, bucket].
        self.capture_len = _capture_len_for_bucket(self.bucket)

        hidden_size = model_runner.model_config.hidden_size

        # Graph inputs (fixed-address buffers, refreshed before every replay)
        with torch.device("cuda"):
            self.input_ids = torch.zeros((self.bucket,), dtype=torch.int64)
            self.req_pool_indices = torch.zeros((1,), dtype=torch.int32)
            # Carries the extend length to the backend capture/replay hooks.
            self.seq_lens = torch.full(
                (1,), self.capture_len, dtype=torch.int32
            )
            self.out_cache_loc = torch.zeros((self.bucket,), dtype=torch.int64)
            self.mrope_positions = torch.zeros(
                (3, self.bucket), dtype=torch.int64
            )
            self.input_embeds = torch.zeros(
                (self.bucket, hidden_size), dtype=model_runner.dtype
            )
            # Logits last-token gather: content [real], refreshed per replay.
            self.extend_seq_lens = torch.full(
                (1,), self.capture_len, dtype=torch.int32
            )
            # Three segments (real, pad, empty), never a prefix.
            self.extend_prefix_lens = torch.zeros((3,), dtype=torch.int32)

        # Sane capture-time content (finite, valid indices).
        self.mrope_positions[:] = torch.arange(
            self.bucket, dtype=torch.int64, device="cuda"
        )
        # Do not consume the global CUDA RNG here. A finite non-zero constant
        # exercises the same captured kernels without perturbing initialization
        # performed by the caller before or after this runner is constructed.
        self.input_embeds.fill_(0.01)

        # Fixed-address FLA chunk buffers. Their contents are refreshed per
        # replay while their maximum shapes stay captured.
        self._chunk_layout = {
            chunk: self._build_chunk_layout(chunk, self.capture_len)
            for chunk in (16, 64)
        }

        capture_started = time.perf_counter()
        try:
            try:
                with CudaGraphRunner.model_capture_mode(self):
                    self._capture()
            except RuntimeError as e:
                raise Exception(f"Capture extend cuda graph failed: {e}")
        finally:
            torch.random.set_rng_state(cpu_rng_state)
            torch.cuda.set_rng_state(cuda_rng_state, model_runner.device)
        self.capture_seconds = time.perf_counter() - capture_started
        print(
            f"EXTGRAPH capture bucket={self.bucket} "
            f"capture_len={self.capture_len} seconds={self.capture_seconds:.3f}",
            file=sys.stderr,
            flush=True,
        )

    def _chunk_layout_values(self, chunk_size: int, real: int):
        real_chunks = (real + chunk_size - 1) // chunk_size
        pad = self.bucket - real
        pad_chunks = (pad + chunk_size - 1) // chunk_size
        max_chunks = self.bucket // chunk_size + 1
        pairs = [[0, i] for i in range(real_chunks)]
        pairs.extend([1, i] for i in range(pad_chunks))
        valid_chunks = len(pairs)
        if valid_chunks < max_chunks:
            # Aligned splits need bucket/chunk entries rather than n+1. The
            # last captured program points at an empty third segment and all
            # its loads/stores are masked by cu_seqlens [BUCKET, BUCKET].
            pairs.append([2, 0])
        assert len(pairs) == max_chunks
        offsets = [0, real_chunks, valid_chunks, valid_chunks]
        return pairs, offsets

    def _build_chunk_layout(self, chunk_size: int, real: int):
        pairs, offset_values = self._chunk_layout_values(chunk_size, real)
        indices = torch.tensor(pairs, dtype=torch.int32, device="cuda")
        offsets = torch.tensor(offset_values, dtype=torch.int32, device="cuda")
        return indices, offsets

    def _refresh_chunk_layout(self, real: int):
        for chunk_size, (indices, offsets) in self._chunk_layout.items():
            pairs, offset_values = self._chunk_layout_values(chunk_size, real)
            indices.copy_(torch.tensor(pairs, dtype=torch.int32))
            offsets.copy_(torch.tensor(offset_values, dtype=torch.int32))

    def _capture(self):
        forward_batch = ForwardBatch(
            forward_mode=ForwardMode.EXTEND,
            batch_size=1,
            input_ids=self.input_ids,
            req_pool_indices=self.req_pool_indices,
            seq_lens=self.seq_lens,
            req_to_token_pool=self.model_runner.req_to_token_pool,
            token_to_kv_pool=self.model_runner.token_to_kv_pool,
            attn_backend=self.model_runner.attn_backend,
            out_cache_loc=self.out_cache_loc,
            seq_lens_sum=self.capture_len,
            return_logprob=False,
            positions=self.mrope_positions,
            mrope_positions=self.mrope_positions,
            capture_hidden_mode=CaptureHiddenMode.FULL,
            extend_num_tokens=self.bucket,
            extend_seq_lens=self.extend_seq_lens,
            extend_prefix_lens=self.extend_prefix_lens,
            # Host-side maximums only size the conv launch grid; GPU
            # query_start_loc masks the real, pad and empty segments.
            extend_seq_lens_cpu=[self.bucket, self.bucket, 0],
            extend_prefix_lens_cpu=[0, 0, 0],
        )

        # Attention backend fixed-address metadata (EXTEND branches).
        self.model_runner.attn_backend.init_forward_metadata_capture_cuda_graph(
            1,
            self.bucket,
            self.req_pool_indices,
            self.seq_lens,
            None,
            ForwardMode.EXTEND,
            None,
        )

        model = self.model_runner.model
        language_model = model.model

        def run_once():
            hidden_states = language_model(
                input_ids=None,
                positions=self.mrope_positions,
                forward_batch=forward_batch,
                input_embeds=self.input_embeds,
            )
            logits_output = model.logits_processor(
                self.input_ids, hidden_states, model.lm_head, forward_batch
            )
            return logits_output.next_token_logits, logits_output.hidden_states

        set_chunk_layout_override(self._chunk_layout)
        try:
            with graph_capture() as graph_capture_context:
                stream = graph_capture_context.stream
                for _ in range(2):
                    torch.cuda.synchronize()
                    run_once()
                self.graph = torch.cuda.CUDAGraph()
                with torch.cuda.graph(self.graph, stream=stream):
                    self.output = run_once()
        finally:
            set_chunk_layout_override(None)
        # Capture warmup writes dummy K/V and mamba states into scratch slot 0.
        # The MTP draft path's state slots start at 0, so without this reset
        # the first request's first draft forward reads garbage state (EN50
        # showed answer diffs from this; zeroing removed them).
        pool = self.model_runner.token_to_kv_pool
        mc = pool.mamba_pool.mamba_cache
        for c in mc.conv:
            c[:, 0].zero_()
        mc.temporal[:, 0].zero_()
        fp = pool.full_kv_pool
        for lb in fp.k_buffer:
            lb[0].zero_()
        for lb in fp.v_buffer:
            lb[0].zero_()
        torch.cuda.synchronize()

    def can_run(self, forward_batch: ForwardBatch):
        if self.graph is None:
            return False
        return (
            forward_batch.forward_mode == ForwardMode.EXTEND
            and forward_batch.spec_info is None
            and forward_batch.batch_size == 1
            and not forward_batch.return_logprob
            and forward_batch.extend_num_tokens is not None
            and forward_batch.extend_num_tokens <= self.bucket
            and list(forward_batch.extend_prefix_lens_cpu) == [0]
        )

    def replay(self, forward_batch: ForwardBatch) -> LogitsProcessorOutput:
        real = forward_batch.input_ids.shape[0]
        model = self.model_runner.model
        if self.profile_ttft:
            torch.cuda.synchronize()
            profile_started = time.perf_counter()

        # SGLANG_EXTEND_TRACE=1: torch profiler around the Nth bucketed
        # extend replay (SGLANG_EXTEND_TRACE_NTH, default 3 — skips one-time
        # JIT), exporting one chrome trace to SGLANG_EXTEND_TRACE_OUT.
        # Investigation-only knob; zero overhead when unset.
        if os.environ.get("SGLANG_EXTEND_TRACE", "0") == "1":
            self._extend_trace_seen = getattr(self, "_extend_trace_seen", 0) + 1
            nth = int(os.environ.get("SGLANG_EXTEND_TRACE_NTH", "3"))
            if self._extend_trace_seen == nth:
                from torch.profiler import ProfilerActivity, profile

                os.environ["SGLANG_EXTEND_TRACE"] = "0"
                torch.cuda.synchronize()
                with profile(
                    activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA]
                ) as prof:
                    ret = self._replay_inner(forward_batch)
                    torch.cuda.synchronize()
                out = os.environ.get(
                    "SGLANG_EXTEND_TRACE_OUT", "/root/extend_trace.json"
                )
                prof.export_chrome_trace(out)
                logger.info("EXTENDTRACE nth=%d exported to %s", nth, out)
                return ret

        return self._replay_inner(forward_batch)

    def _replay_inner(self, forward_batch: ForwardBatch) -> LogitsProcessorOutput:
        real = forward_batch.input_ids.shape[0]
        model = self.model_runner.model
        if self.profile_ttft:
            torch.cuda.synchronize()
            profile_started = time.perf_counter()

        # Multimodal embed merge, eager (replicates the numerics of
        # general_mm_embed_routine; the ViT itself may already be graphed).
        if forward_batch.contains_mm_inputs():
            mm_input = forward_batch.merge_mm_inputs()
            embeds = embed_mm_inputs(
                mm_inputs=mm_input,
                input_ids=forward_batch.input_ids,
                input_embedding=model.get_input_embeddings(),
                image_data_embedding_func=model.get_image_feature,
            )
            # Match the eager side effect: mm_inputs are single-use.
            forward_batch.mm_inputs = None
        else:
            embeds = model.get_input_embeddings()(forward_batch.input_ids)

        # Refresh the fixed-address buffers.
        self.input_embeds[:real].copy_(embeds)
        if real < self.bucket:
            self.input_embeds[real:].zero_()
            self.out_cache_loc[real:].zero_()
        self.input_ids[:real].copy_(forward_batch.input_ids)
        self.mrope_positions[:, :real].copy_(forward_batch.mrope_positions)
        self.req_pool_indices[:1].copy_(forward_batch.req_pool_indices)
        self.out_cache_loc[:real].copy_(forward_batch.out_cache_loc)
        self.seq_lens.fill_(real)
        self.extend_seq_lens.fill_(real)
        self._refresh_chunk_layout(real)

        # Refresh backend metadata buffers (qo_indptr[1], query_start_loc[1],
        # mamba state slot) outside the graph.
        self.model_runner.attn_backend.init_forward_metadata_replay_cuda_graph(
            1,
            self.req_pool_indices,
            self.seq_lens,
            real,
            None,
            ForwardMode.EXTEND,
            None,
        )

        # All bucket graphs deliberately share the backend's fixed-address
        # metadata tensors. Capture of the next bucket therefore overwrites
        # the two constant segment ends left by the previous bucket. Restore
        # them for the selected graph before replay, otherwise a smaller graph
        # can observe the largest bucket's end and launch out of bounds.
        attn_backend = self.model_runner.attn_backend
        linear_backend = getattr(attn_backend, "linear_attn_backend", None)
        full_backend = getattr(attn_backend, "full_attn_backend", None)
        if linear_backend is not None:
            linear_backend._extend_graph_qsl[2:].fill_(self.bucket)
        if full_backend is not None:
            full_backend._graph_extend_qo_indptr[2:].fill_(self.bucket)

        self.graph.replay()
        next_token_logits, hidden_states = self.output
        if self.profile_ttft:
            torch.cuda.synchronize()
            from sglang.srt.ttft_prof import mark

            mark(
                "extend_gpu",
                profile_started,
                mode=str(forward_batch.forward_mode),
                extend_num_tokens=real,
                graph_bucket=self.bucket,
            )
        return LogitsProcessorOutput(
            next_token_logits=next_token_logits[:1],
            hidden_states=hidden_states[:real],
        )


class ExtendCudaGraphRunner:
    """Routes bs=1 EXTEND requests to the smallest fitting captured bucket."""

    BUCKETS = (192, 256, 320, 384)

    def __init__(self, model_runner):
        self.model_runner = model_runner
        self.buckets = _configured_buckets(self.BUCKETS)
        started = time.perf_counter()
        self.runners = {
            bucket: _SingleBucketExtendCudaGraphRunner(model_runner, bucket)
            for bucket in self.buckets
        }
        self.capture_seconds = time.perf_counter() - started
        print(
            f"EXTGRAPH capture total buckets={self.buckets} "
            f"seconds={self.capture_seconds:.3f}",
            file=sys.stderr,
            flush=True,
        )

    def _select(self, forward_batch: ForwardBatch):
        real = forward_batch.extend_num_tokens
        if real is None:
            return None
        for bucket in self.buckets:
            if real <= bucket:
                return self.runners[bucket]
        return None

    def can_run(self, forward_batch: ForwardBatch):
        runner = self._select(forward_batch)
        return runner is not None and runner.can_run(forward_batch)

    def replay(self, forward_batch: ForwardBatch) -> LogitsProcessorOutput:
        runner = self._select(forward_batch)
        assert runner is not None
        return runner.replay(forward_batch)
