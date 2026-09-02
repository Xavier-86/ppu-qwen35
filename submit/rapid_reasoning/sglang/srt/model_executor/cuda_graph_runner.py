# Copyright 2023-2024 SGLang Team
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
"""Run the model decode step with CUDA graph capture/replay.

BACKPORT-PPU: restored from the pre-slim tree and trimmed to the fixed
Qwen3.5-2B inference path — batch size 1, DECODE only, TP=1. The DP
attention / SP layernorm / encoder-decoder / torch.compile branches of the
original runner are deleted. The MTP runners below capture fixed chain
TARGET_VERIFY, DRAFT_DECODE and accept-keyed DRAFT_EXTEND shapes.
"""

from __future__ import annotations

import json
import os
import sys
import time
from contextlib import contextmanager
from types import SimpleNamespace
from typing import TYPE_CHECKING, Callable

import torch

from sglang.srt.distributed.parallel_state import graph_capture
from sglang.srt.layers.logits_processor import LogitsProcessorOutput
from sglang.srt.model_executor.forward_batch_info import (
    CaptureHiddenMode,
    ForwardBatch,
    ForwardMode,
)

if TYPE_CHECKING:
    from sglang.srt.model_executor.model_runner import ModelRunner


# BACKPORT: capture-mode flag from sglang v0.5.9, kept for the model-side
# capture_mode hooks (memory_pool alt-stream KV writes, qwen3_5 q/k norm).
is_capture_mode = False


def get_is_capture_mode():
    return is_capture_mode


@contextmanager
def model_capture_mode():
    global is_capture_mode
    is_capture_mode = True

    yield

    is_capture_mode = False


class CudaGraphRunner:
    """Captures and replays the bs=1 decode forward pass as a CUDA graph."""

    def __init__(self, model_runner: ModelRunner):
        self.model_runner = model_runner
        self.graphs = {}
        self.output_buffers = {}

        # BACKPORT-PPU: the competition workload is bs=1 decode only.
        self.capture_bs = [1]

        self.capture_forward_mode = ForwardMode.DECODE
        self.capture_hidden_mode = CaptureHiddenMode.NULL
        self.num_tokens_per_bs = 1

        # Attention backend fixed-address state
        self.max_bs = max(self.capture_bs)
        self.max_num_token = self.max_bs * self.num_tokens_per_bs
        self.model_runner.attn_backend.init_cuda_graph_state(
            self.max_bs, self.max_num_token
        )
        self.seq_len_fill_value = (
            self.model_runner.attn_backend.get_cuda_graph_seq_len_fill_value()
        )
        self.seq_lens_cpu = torch.full(
            (self.max_bs,), self.seq_len_fill_value, dtype=torch.int32
        )

        # Graph inputs (fixed-address buffers, refreshed before every replay)
        with torch.device("cuda"):
            self.input_ids = torch.zeros((self.max_num_token,), dtype=torch.int64)
            self.req_pool_indices = torch.zeros((self.max_bs,), dtype=torch.int32)
            self.seq_lens = torch.full(
                (self.max_bs,), self.seq_len_fill_value, dtype=torch.int32
            )
            self.out_cache_loc = torch.zeros(
                (self.max_num_token,), dtype=torch.int64
            )
            self.positions = torch.zeros((self.max_num_token,), dtype=torch.int64)
            self.mrope_positions = torch.zeros((3, self.max_bs), dtype=torch.int64)

        # Capture
        try:
            with self.model_capture_mode():
                self.capture()
        except RuntimeError as e:
            raise Exception(
                f"Capture cuda graph failed: {e}\n"
                "Possible solutions:\n"
                "1. set --mem-fraction-static to a smaller value (e.g., 0.8 or 0.7)\n"
                "2. disable cuda graph by --disable-cuda-graph.\n"
            )

    @contextmanager
    def model_capture_mode(self):
        global is_capture_mode
        is_capture_mode = True
        if hasattr(self.model_runner.model, "capture_mode"):
            self.model_runner.model.capture_mode = True
        if hasattr(self.model_runner.token_to_kv_pool, "capture_mode"):
            self.model_runner.token_to_kv_pool.capture_mode = True

        yield

        is_capture_mode = False
        if hasattr(self.model_runner.model, "capture_mode"):
            self.model_runner.model.capture_mode = False
        if hasattr(self.model_runner.token_to_kv_pool, "capture_mode"):
            self.model_runner.token_to_kv_pool.capture_mode = False

    def can_run(self, forward_batch: ForwardBatch):
        # BACKPORT-PPU: bs=1 only; batch_size never exceeds 1 in this config,
        # so no padding is needed.
        # Only plain DECODE batches may take the graph: TARGET_VERIFY also
        # reports is_cuda_graph() but carries 2x tokens and spec metadata.
        return (
            forward_batch.forward_mode.is_decode()
            and forward_batch.batch_size in self.graphs
        )

    def capture(self):
        with graph_capture() as graph_capture_context:
            self.stream = graph_capture_context.stream
            for bs in reversed(self.capture_bs):
                graph, output_buffers = self.capture_one_batch_size(
                    bs, self.model_runner.model.forward
                )
                self.graphs[bs] = graph
                self.output_buffers[bs] = output_buffers

    def capture_one_batch_size(self, bs: int, forward: Callable):
        graph = torch.cuda.CUDAGraph()
        stream = self.stream
        num_tokens = bs * self.num_tokens_per_bs

        # Graph inputs
        input_ids = self.input_ids[:num_tokens]
        req_pool_indices = self.req_pool_indices[:bs]
        seq_lens = self.seq_lens[:bs]
        out_cache_loc = self.out_cache_loc[:num_tokens]
        positions = self.positions[:num_tokens]
        mrope_positions = self.mrope_positions[:, :bs]

        forward_batch = ForwardBatch(
            forward_mode=self.capture_forward_mode,
            batch_size=bs,
            input_ids=input_ids,
            req_pool_indices=req_pool_indices,
            seq_lens=seq_lens,
            req_to_token_pool=self.model_runner.req_to_token_pool,
            token_to_kv_pool=self.model_runner.token_to_kv_pool,
            attn_backend=self.model_runner.attn_backend,
            out_cache_loc=out_cache_loc,
            # seq_lens is filled with seq_len_fill_value (=1) at capture time
            seq_lens_sum=num_tokens * self.seq_len_fill_value,
            return_logprob=False,
            positions=positions,
            mrope_positions=mrope_positions,
            capture_hidden_mode=self.capture_hidden_mode,
        )

        # Attention backend
        self.model_runner.attn_backend.init_forward_metadata_capture_cuda_graph(
            bs,
            num_tokens,
            req_pool_indices,
            seq_lens,
            None,
            forward_batch.forward_mode,
            None,
        )

        # Run and capture
        def run_once():
            logits_output = forward(input_ids, forward_batch.positions, forward_batch)
            return logits_output.next_token_logits, logits_output.hidden_states

        for _ in range(2):
            torch.cuda.synchronize()
            run_once()

        with torch.cuda.graph(graph, stream=stream):
            out = run_once()

        return graph, out

    def replay_prepare(self, forward_batch: ForwardBatch):
        raw_bs = forward_batch.batch_size
        assert raw_bs in self.graphs, f"unexpected decode batch size {raw_bs}"
        bs = raw_bs
        raw_num_token = raw_bs * self.num_tokens_per_bs

        # Common inputs
        self.input_ids[:raw_num_token].copy_(forward_batch.input_ids)
        self.req_pool_indices[:raw_bs].copy_(forward_batch.req_pool_indices)
        self.seq_lens[:raw_bs].copy_(forward_batch.seq_lens)
        self.out_cache_loc[:raw_num_token].copy_(forward_batch.out_cache_loc)
        self.positions[:raw_num_token].copy_(forward_batch.positions)
        if forward_batch.seq_lens_cpu is not None:
            self.seq_lens_cpu[:raw_bs].copy_(forward_batch.seq_lens_cpu)
        if forward_batch.mrope_positions is not None:
            self.mrope_positions[:, :raw_bs].copy_(forward_batch.mrope_positions)

        # Attention backend (recomputes kv indices / num_kv_splits / mamba
        # state indices into the fixed-address buffers outside the graph)
        self.model_runner.attn_backend.init_forward_metadata_replay_cuda_graph(
            bs,
            self.req_pool_indices,
            self.seq_lens,
            forward_batch.seq_lens_sum,
            None,
            forward_batch.forward_mode,
            None,
            seq_lens_cpu=self.seq_lens_cpu,
        )

        # Store fields
        self.raw_bs = raw_bs
        self.raw_num_token = raw_num_token
        self.bs = bs

    def replay(
        self, forward_batch: ForwardBatch, skip_attn_backend_init: bool = False
    ) -> LogitsProcessorOutput:
        if not skip_attn_backend_init:
            self.replay_prepare(forward_batch)
        else:
            self.input_ids[: self.raw_num_token].copy_(forward_batch.input_ids)
            self.positions[: self.raw_num_token].copy_(forward_batch.positions)

        # Replay
        self.graphs[self.bs].replay()
        next_token_logits, hidden_states = self.output_buffers[self.bs]

        logits_output = LogitsProcessorOutput(
            next_token_logits=next_token_logits[: self.raw_num_token],
            hidden_states=(
                hidden_states[: self.raw_num_token]
                if hidden_states is not None
                else None
            ),
        )
        return logits_output


def _copy_or_derive_mrope_positions(
    mrope_buffer: torch.Tensor, n: int, forward_batch: ForwardBatch
) -> None:
    """Fill the graph's mrope position buffer for the next replay.

    BACKPORT-PPU: MTP phase 3. The verify / draft-extend CPU mrope
    computation syncs on GPU positions, so init_new skips it when a graph
    will replay; here we derive it on GPU instead. For this VLM
    (bs=1, single mrope delta per request) the mrope positions equal the
    linear positions plus the request's mrope_position_delta, broadcast
    over the 3 mrope rows. The delta lives on CPU, so no sync is needed.
    """
    if forward_batch.mrope_positions is not None:
        mrope_buffer[:, :n].copy_(forward_batch.mrope_positions)
        return
    delta = 0
    if forward_batch.mm_inputs and forward_batch.mm_inputs[0] is not None:
        from sglang.srt.utils import flatten_nested_list

        delta = flatten_nested_list(
            forward_batch.mm_inputs[0].mrope_position_delta.tolist()
        )[0]
    mrope_buffer[:, :n] = forward_batch.positions.unsqueeze(0) + delta


class MtpTargetVerifyGraphRunner:
    """Captures/replays the bs=1 fixed-length TARGET_VERIFY forward.

    BACKPORT-PPU: MTP phase 2. Same fixed-address-buffer pattern as the
    decode CudaGraphRunner; a fixed q_len=2 or q_len=3 graph covers every
    decode step. Attention metadata (kv prefix
    indices, mamba state indices) is recomputed outside the graph into the
    backend's fixed buffers on every replay; the mamba intermediate-state
    buffers live at fixed pool addresses. The mamba commit and the greedy
    acceptance comparison stay outside the graph.
    """

    def __init__(self, model_runner: ModelRunner):
        self.model_runner = model_runner
        self.num_tokens = model_runner.server_args.speculative_num_draft_tokens
        self.metadata_in_graph = (
            os.environ.get("SGLANG_VERIFY_FUSED_METADATA_COPY", "1") == "1"
        )
        self.profile_replay = os.environ.get("SGLANG_VERIFY_PROFILE", "0") == "1"
        self._profile_count = 0
        self._profile_totals = {
            "copies_host_ms": 0.0,
            "metadata_host_ms": 0.0,
            "graph_host_ms": 0.0,
            "sync_host_ms": 0.0,
            "gpu_total_ms": 0.0,
        }

        with torch.device("cuda"):
            self.input_ids = torch.zeros((self.num_tokens,), dtype=torch.int64)
            self.req_pool_indices = torch.zeros((1,), dtype=torch.int32)
            self.seq_lens = torch.ones((1,), dtype=torch.int32)
            self.out_cache_loc = torch.zeros((self.num_tokens,), dtype=torch.int64)
            self.positions = torch.zeros((self.num_tokens,), dtype=torch.int64)
            self.mrope_positions = torch.zeros((3, self.num_tokens), dtype=torch.int64)

        from sglang.srt.speculative.mtp_utils import MtpVerifyInput

        self.spec_info = MtpVerifyInput(
            draft_token=self.input_ids,
            positions=self.positions,
            custom_mask=None,
            draft_token_num=self.num_tokens,
            spec_steps=self.num_tokens - 1,
            capture_hidden_mode=CaptureHiddenMode.FULL,
        )

        try:
            with CudaGraphRunner.model_capture_mode(self):
                self._capture()
        except RuntimeError as e:
            raise Exception(f"Capture MTP verify cuda graph failed: {e}")

    def _capture(self):
        from sglang.srt.distributed.parallel_state import graph_capture

        with graph_capture() as ctx:
            stream = ctx.stream
            forward_batch = ForwardBatch(
                forward_mode=ForwardMode.TARGET_VERIFY,
                batch_size=1,
                input_ids=self.input_ids,
                req_pool_indices=self.req_pool_indices,
                seq_lens=self.seq_lens,
                req_to_token_pool=self.model_runner.req_to_token_pool,
                token_to_kv_pool=self.model_runner.token_to_kv_pool,
                attn_backend=self.model_runner.attn_backend,
                out_cache_loc=self.out_cache_loc,
                seq_lens_sum=1,
                return_logprob=False,
                positions=self.positions,
                mrope_positions=self.mrope_positions,
                capture_hidden_mode=CaptureHiddenMode.FULL,
                spec_info=self.spec_info,
            )
            self.model_runner.attn_backend.init_forward_metadata_capture_cuda_graph(
                1,
                self.num_tokens,
                self.req_pool_indices,
                self.seq_lens,
                None,
                ForwardMode.TARGET_VERIFY,
                self.spec_info,
            )

            def run_once():
                if self.metadata_in_graph:
                    self.model_runner.attn_backend.init_forward_metadata_replay_cuda_graph(
                        1,
                        self.req_pool_indices,
                        self.seq_lens,
                        1,
                        None,
                        ForwardMode.TARGET_VERIFY,
                        self.spec_info,
                        seq_lens_cpu=None,
                    )
                logits_output = self.model_runner.model.forward(
                    self.input_ids, forward_batch.positions, forward_batch
                )
                return logits_output.next_token_logits, logits_output.hidden_states

            for _ in range(2):
                torch.cuda.synchronize()
                run_once()

            self.graph = torch.cuda.CUDAGraph()
            with torch.cuda.graph(self.graph, stream=stream):
                self.output = run_once()

    def can_run(self, forward_batch: ForwardBatch):
        return (
            forward_batch.forward_mode.is_target_verify()
            and forward_batch.batch_size == 1
            and forward_batch.input_ids.shape[0] == self.num_tokens
        )

    def replay(self, forward_batch: ForwardBatch) -> LogitsProcessorOutput:
        n = self.num_tokens
        if self.profile_replay:
            started = time.perf_counter()
            gpu_started = torch.cuda.Event(enable_timing=True)
            gpu_finished = torch.cuda.Event(enable_timing=True)
            gpu_started.record()
        self.input_ids[:n].copy_(forward_batch.input_ids)
        self.req_pool_indices[:1].copy_(forward_batch.req_pool_indices)
        self.seq_lens[:1].copy_(forward_batch.seq_lens)
        self.out_cache_loc[:n].copy_(forward_batch.out_cache_loc)
        self.positions[:n].copy_(forward_batch.positions)
        _copy_or_derive_mrope_positions(self.mrope_positions, n, forward_batch)
        if self.profile_replay:
            copies_done = time.perf_counter()

        if not self.metadata_in_graph:
            self.model_runner.attn_backend.init_forward_metadata_replay_cuda_graph(
                1,
                self.req_pool_indices,
                self.seq_lens,
                forward_batch.seq_lens_sum,
                None,
                ForwardMode.TARGET_VERIFY,
                self.spec_info,
                seq_lens_cpu=forward_batch.seq_lens_cpu,
            )
        if self.profile_replay:
            metadata_done = time.perf_counter()

        self.graph.replay()
        if self.profile_replay:
            graph_done = time.perf_counter()
            gpu_finished.record()
            gpu_finished.synchronize()
            synced = time.perf_counter()
            values = {
                "copies_host_ms": (copies_done - started) * 1e3,
                "metadata_host_ms": (metadata_done - copies_done) * 1e3,
                "graph_host_ms": (graph_done - metadata_done) * 1e3,
                "sync_host_ms": (synced - graph_done) * 1e3,
                "gpu_total_ms": gpu_started.elapsed_time(gpu_finished),
            }
            self._profile_count += 1
            for key, value in values.items():
                self._profile_totals[key] += value
            if self._profile_count % 50 == 0:
                averages = {
                    key: round(value / self._profile_count, 4)
                    for key, value in self._profile_totals.items()
                }
                print(
                    "VERIFYPROF "
                    + json.dumps(
                        {"count": self._profile_count, **averages},
                        ensure_ascii=False,
                    ),
                    file=sys.stderr,
                    flush=True,
                )
        next_token_logits, hidden_states = self.output
        return LogitsProcessorOutput(
            next_token_logits=next_token_logits[:n],
            hidden_states=hidden_states[:n] if hidden_states is not None else None,
        )


class MtpDraftExtendGraphRunner:
    """Captures/replays bs=1 DRAFT_EXTEND for every accepted chain length.

    BACKPORT-PPU: MTP phase 2. The draft extend input length is
    accept_length + 1 with accept known on CPU after verify, so two graphs
    (keyed by token count) cover all cases; the right one is picked at
    replay time. The draft model consumes the target's hidden states, which
    are copied into a fixed-address buffer hanging off a static spec_info.
    """

    def __init__(self, model_runner: ModelRunner):
        self.model_runner = model_runner
        self.max_tokens = model_runner.server_args.speculative_num_draft_tokens
        hidden_size = model_runner.model_config.hidden_size

        # The draft ModelRunner was created with graphs disabled (its decode
        # graph is never used), so the backend graph state is initialized
        # here instead.
        self.model_runner.attn_backend.init_cuda_graph_state(1, self.max_tokens)

        from sglang.srt.speculative.mtp_utils import MtpDraftInput

        with torch.device("cuda"):
            self.input_ids = torch.zeros((self.max_tokens,), dtype=torch.int64)
            self.req_pool_indices = torch.zeros((1,), dtype=torch.int32)
            self.seq_lens = torch.full((1,), 2, dtype=torch.int32)
            self.out_cache_loc = torch.zeros((self.max_tokens,), dtype=torch.int64)
            self.positions = torch.zeros((self.max_tokens,), dtype=torch.int64)
            self.mrope_positions = torch.zeros(
                (3, self.max_tokens), dtype=torch.int64
            )
            self.hidden_states = torch.zeros(
                (self.max_tokens, hidden_size), dtype=torch.bfloat16
            )

        self.spec_info = MtpDraftInput(
            hidden_states=self.hidden_states,
            capture_hidden_mode=CaptureHiddenMode.LAST,
        )

        self.graphs = {}
        self.output_buffers = {}
        try:
            with CudaGraphRunner.model_capture_mode(self):
                self._capture()
        except RuntimeError as e:
            raise Exception(f"Capture MTP draft extend cuda graph failed: {e}")

    def _capture(self):
        from sglang.srt.distributed.parallel_state import graph_capture

        with graph_capture() as ctx:
            stream = ctx.stream
            for num_tokens in range(self.max_tokens, 0, -1):
                # Each graph reads its own row-slice of the shared hidden
                # buffer (same base pointer; the model cats it with the
                # per-graph input embeds, so the row count must match).
                self.spec_info.hidden_states = self.hidden_states[:num_tokens]
                # LogitsProcessor prunes the last row per request via
                # extend_seq_lens in DRAFT_EXTEND; it is a per-graph
                # constant ([num_tokens] for bs=1).
                extend_seq_lens = torch.full(
                    (1,), num_tokens, dtype=torch.int32, device="cuda"
                )
                forward_batch = ForwardBatch(
                    forward_mode=ForwardMode.DRAFT_EXTEND,
                    batch_size=1,
                    input_ids=self.input_ids[:num_tokens],
                    req_pool_indices=self.req_pool_indices,
                    seq_lens=self.seq_lens,
                    req_to_token_pool=self.model_runner.req_to_token_pool,
                    token_to_kv_pool=self.model_runner.token_to_kv_pool,
                    attn_backend=self.model_runner.attn_backend,
                    out_cache_loc=self.out_cache_loc[:num_tokens],
                    seq_lens_sum=num_tokens,
                    return_logprob=False,
                    positions=self.positions[:num_tokens],
                    mrope_positions=self.mrope_positions[:, :num_tokens],
                    capture_hidden_mode=CaptureHiddenMode.LAST,
                    spec_info=self.spec_info,
                    extend_seq_lens=extend_seq_lens,
                )
                self.model_runner.attn_backend.init_forward_metadata_capture_cuda_graph(
                    1,
                    num_tokens,
                    self.req_pool_indices,
                    self.seq_lens,
                    None,
                    ForwardMode.DRAFT_EXTEND,
                    self.spec_info,
                )

                def run_once():
                    logits_output = self.model_runner.model.forward(
                        self.input_ids[:num_tokens],
                        forward_batch.positions,
                        forward_batch,
                    )
                    return (
                        logits_output.next_token_logits,
                        logits_output.hidden_states,
                    )

                for _ in range(2):
                    torch.cuda.synchronize()
                    run_once()

                graph = torch.cuda.CUDAGraph()
                with torch.cuda.graph(graph, stream=stream):
                    self.graphs[num_tokens] = graph
                    self.output_buffers[num_tokens] = run_once()

    def can_run(self, forward_batch: ForwardBatch):
        return (
            forward_batch.forward_mode.is_draft_extend()
            and forward_batch.batch_size == 1
            and forward_batch.input_ids.shape[0] in self.graphs
        )

    def replay(self, forward_batch: ForwardBatch) -> LogitsProcessorOutput:
        n = forward_batch.input_ids.shape[0]
        assert n in self.graphs
        self.input_ids[:n].copy_(forward_batch.input_ids)
        self.req_pool_indices[:1].copy_(forward_batch.req_pool_indices)
        self.seq_lens[:1].copy_(forward_batch.seq_lens)
        self.out_cache_loc[:n].copy_(forward_batch.out_cache_loc)
        self.positions[:n].copy_(forward_batch.positions)
        _copy_or_derive_mrope_positions(self.mrope_positions, n, forward_batch)
        self.hidden_states[:n].copy_(forward_batch.spec_info.hidden_states)
        # The triton replay metadata derives the kv prefix length from the
        # per-request extend length.
        self.spec_info.accept_length_cpu = [n]

        self.model_runner.attn_backend.init_forward_metadata_replay_cuda_graph(
            1,
            self.req_pool_indices,
            self.seq_lens,
            forward_batch.seq_lens_sum,
            None,
            ForwardMode.DRAFT_EXTEND,
            self.spec_info,
            seq_lens_cpu=forward_batch.seq_lens_cpu,
        )

        self.graphs[n].replay()
        next_token_logits, hidden_states = self.output_buffers[n]
        return LogitsProcessorOutput(
            next_token_logits=next_token_logits,
            hidden_states=hidden_states,
        )


# BACKPORT-PPU: fixed-row graph used by slim MTP chain depths two/three.
class MtpDraftDecodeGraphRunner:
    """Capture the extra one-row draft decode used by chain depth >= two.

    This graph consumes the carried hidden state and previous draft token,
    writes one temporary draft KV row, and returns the next proposal together
    with its hidden state (the next chain step consumes both).  The temporary
    allocator slot is restored by the worker after replay.
    """

    def __init__(self, model_runner: ModelRunner):
        self.model_runner = model_runner
        hidden_size = model_runner.model_config.hidden_size

        from sglang.srt.speculative.mtp_utils import MtpDraftInput

        with torch.device("cuda"):
            self.input_ids = torch.zeros((1,), dtype=torch.int64)
            self.req_pool_indices = torch.zeros((1,), dtype=torch.int32)
            self.seq_lens = torch.ones((1,), dtype=torch.int32)
            self.out_cache_loc = torch.zeros((1,), dtype=torch.int64)
            self.positions = torch.zeros((1,), dtype=torch.int64)
            self.mrope_positions = torch.zeros((3, 1), dtype=torch.int64)
            self.hidden_states = torch.zeros(
                (1, hidden_size), dtype=torch.bfloat16
            )

        self.spec_info = MtpDraftInput(
            hidden_states=self.hidden_states,
            capture_hidden_mode=CaptureHiddenMode.LAST,
        )
        try:
            with CudaGraphRunner.model_capture_mode(self):
                self._capture()
        except RuntimeError as e:
            raise Exception(f"Capture MTP chain-2 draft graph failed: {e}")

    def _capture(self):
        from sglang.srt.distributed.parallel_state import graph_capture

        with graph_capture() as ctx:
            stream = ctx.stream
            forward_batch = ForwardBatch(
                forward_mode=ForwardMode.DECODE,
                batch_size=1,
                input_ids=self.input_ids,
                req_pool_indices=self.req_pool_indices,
                seq_lens=self.seq_lens,
                req_to_token_pool=self.model_runner.req_to_token_pool,
                token_to_kv_pool=self.model_runner.token_to_kv_pool,
                attn_backend=self.model_runner.attn_backend,
                out_cache_loc=self.out_cache_loc,
                seq_lens_sum=1,
                return_logprob=False,
                positions=self.positions,
                mrope_positions=self.mrope_positions,
                capture_hidden_mode=CaptureHiddenMode.LAST,
                spec_info=self.spec_info,
            )
            self.model_runner.attn_backend.init_forward_metadata_capture_cuda_graph(
                1,
                1,
                self.req_pool_indices,
                self.seq_lens,
                None,
                ForwardMode.DECODE,
                self.spec_info,
            )

            def run_once():
                logits_output = self.model_runner.model.forward(
                    self.input_ids, forward_batch.positions, forward_batch
                )
                return (
                    torch.argmax(logits_output.next_token_logits, dim=-1).to(
                        torch.int64
                    ),
                    logits_output.hidden_states,
                )

            for _ in range(2):
                torch.cuda.synchronize()
                run_once()
            self.graph = torch.cuda.CUDAGraph()
            with torch.cuda.graph(self.graph, stream=stream):
                self.proposal, self.hidden_out = run_once()

    def replay(self, batch, draft_input, out_cache_loc):
        self.input_ids.copy_(draft_input.topk_index.flatten())
        self.req_pool_indices.copy_(batch.req_pool_indices)
        self.seq_lens.copy_(batch.seq_lens)
        self.out_cache_loc.copy_(out_cache_loc)
        self.positions.copy_(batch.seq_lens.to(torch.int64))
        _copy_or_derive_mrope_positions(
            self.mrope_positions,
            1,
            SimpleNamespace(
                mrope_positions=None,
                mm_inputs=[batch.reqs[0].multimodal_inputs],
                positions=self.positions,
            ),
        )
        self.hidden_states.copy_(draft_input.hidden_states)
        self.model_runner.attn_backend.init_forward_metadata_replay_cuda_graph(
            1,
            self.req_pool_indices,
            self.seq_lens,
            batch.seq_lens_sum,
            None,
            ForwardMode.DECODE,
            self.spec_info,
            seq_lens_cpu=None,
        )
        self.graph.replay()
        return self.proposal, self.hidden_out


class MtpCommitGraphRunner:
    """Captures/replays the mamba state commit as two tiny CUDA graphs.

    BACKPORT-PPU: MTP phase 3. ``update_mamba_state_after_mtp_verify``
    scatters the accepted-step intermediate conv/ssm states back into the
    persistent slots: ~36 small kernel launches (18 GDN layers x conv+ssm)
    per verify step. The only data-dependent value is the accepted count
    (0 or 1 with chain MTP): it lives in a fixed buffer that replay()
    refills before launching the graph (captured kernels read the buffer
    contents at replay time, so the value cannot be baked at capture).
    All tensors involved (intermediate buffers, persistent states, verify
    state indices) are fixed-address.
    """

    def __init__(self, attn_backend, model, max_accept: int):
        self.attn_backend = attn_backend
        self.model = model
        self.accepted_steps = torch.zeros((1,), dtype=torch.int32, device="cuda")
        self.graphs = {}
        from sglang.srt.distributed.parallel_state import graph_capture

        with graph_capture() as ctx:
            stream = ctx.stream
            for accept in range(max_accept + 1):
                self.accepted_steps.fill_(accept)

                def run_once():
                    self.attn_backend.update_mamba_state_after_mtp_verify(
                        self.accepted_steps, None, None, self.model
                    )

                for _ in range(2):
                    torch.cuda.synchronize()
                    run_once()

                graph = torch.cuda.CUDAGraph()
                with torch.cuda.graph(graph, stream=stream):
                    run_once()
                self.graphs[accept] = graph

    def replay(self, accept_length: int):
        # The captured kernels read accepted_steps from its fixed address at
        # replay time; the value is NOT baked into the graph, so it must be
        # refilled before every replay (async memset, ordered on-stream).
        self.accepted_steps.fill_(accept_length)
        self.graphs[accept_length].replay()


# BACKPORT-PPU: joint chain-MTP graphs specialized for bs=1 PPU evaluation.
class MtpJointGraphRunner:
    """Joint target-verify and accept-keyed draft-extend graphs for chain MTP.

    One verify graph produces all target predictions plus the accepted draft
    prefix length.  A second graph, selected by that length, runs the exact
    1/2/3-row draft-extend shape and commits target Mamba state.  Chain depth
    two has a separate preceding one-row draft-decode graph.
    """

    def __init__(self, target_model_runner: ModelRunner, draft_model_runner: ModelRunner, num_tokens: int = None):
        self.model_runner = target_model_runner
        self.draft_model_runner = draft_model_runner
        # num_tokens is the fixed verify chain length (speculative steps + 1).
        # Dynamic-depth mode captures one runner per candidate chain length;
        # static mode passes None and uses the server-wide value.
        self.num_tokens = (
            num_tokens
            if num_tokens is not None
            else target_model_runner.server_args.speculative_num_draft_tokens
        )
        target_model = target_model_runner.model
        self.lm_head_weight = target_model.lm_head.weight
        self.vocab_size = target_model.logits_processor.config.vocab_size
        assert hasattr(draft_model_runner.attn_backend, "cuda_graph_kv_indices")

        with torch.device("cuda"):
            self.input_ids = torch.zeros((self.num_tokens,), dtype=torch.int64)
            self.req_pool_indices = torch.zeros((1,), dtype=torch.int32)
            self.seq_lens = torch.ones((1,), dtype=torch.int32)
            self.out_cache_loc = torch.zeros((self.num_tokens,), dtype=torch.int64)
            self.positions = torch.zeros((self.num_tokens,), dtype=torch.int64)
            self.mrope_positions = torch.zeros(
                (3, self.num_tokens), dtype=torch.int64
            )
            self.accept_length = torch.zeros((1,), dtype=torch.int32)
            self.row_indices = torch.arange(
                self.num_tokens, dtype=torch.int32
            )

        from sglang.srt.speculative.mtp_utils import MtpDraftInput, MtpVerifyInput

        self.verify_spec_info = MtpVerifyInput(
            draft_token=self.input_ids,
            positions=self.positions,
            custom_mask=None,
            draft_token_num=self.num_tokens,
            spec_steps=self.num_tokens - 1,
            capture_hidden_mode=CaptureHiddenMode.FULL,
        )
        self.draft_spec_infos = {
            n: MtpDraftInput(capture_hidden_mode=CaptureHiddenMode.LAST)
            for n in range(1, self.num_tokens + 1)
        }
        hidden_size = target_model.config.hidden_size
        with torch.device("cuda"):
            self.proposal32 = torch.zeros((1,), dtype=torch.int32)
            self.new_verified32 = torch.zeros((1,), dtype=torch.int32)
            self.draft_row = torch.zeros(
                (1, hidden_size), dtype=self.lm_head_weight.dtype
            )

        try:
            with self._joint_capture_mode():
                self._capture()
        except RuntimeError as e:
            raise Exception(f"Capture MTP joint head cuda graph failed: {e}")

    @contextmanager
    def _joint_capture_mode(self):
        draft_runner = self.draft_model_runner
        with CudaGraphRunner.model_capture_mode(self):
            if hasattr(draft_runner.model, "capture_mode"):
                draft_runner.model.capture_mode = True
            if hasattr(draft_runner.token_to_kv_pool, "capture_mode"):
                draft_runner.token_to_kv_pool.capture_mode = True
            try:
                yield
            finally:
                if hasattr(draft_runner.model, "capture_mode"):
                    draft_runner.model.capture_mode = False
                if hasattr(draft_runner.token_to_kv_pool, "capture_mode"):
                    draft_runner.token_to_kv_pool.capture_mode = False

    def _capture(self):
        from sglang.srt.distributed.parallel_state import graph_capture
        from sglang.srt.layers.attention.utils import (
            create_flashinfer_kv_indices_triton,
        )

        target_runner = self.model_runner
        draft_runner = self.draft_model_runner
        target_model = target_runner.model
        draft_model = draft_runner.model
        weight = self.lm_head_weight
        vocab_size = self.vocab_size

        with graph_capture() as ctx:
            stream = ctx.stream
            target_batch = ForwardBatch(
                forward_mode=ForwardMode.TARGET_VERIFY,
                batch_size=1,
                input_ids=self.input_ids,
                req_pool_indices=self.req_pool_indices,
                seq_lens=self.seq_lens,
                req_to_token_pool=target_runner.req_to_token_pool,
                token_to_kv_pool=target_runner.token_to_kv_pool,
                attn_backend=target_runner.attn_backend,
                out_cache_loc=self.out_cache_loc,
                seq_lens_sum=1,
                return_logprob=False,
                positions=self.positions,
                mrope_positions=self.mrope_positions,
                capture_hidden_mode=CaptureHiddenMode.FULL,
                spec_info=self.verify_spec_info,
            )
            target_runner.attn_backend.init_forward_metadata_capture_cuda_graph(
                1,
                self.num_tokens,
                self.req_pool_indices,
                self.seq_lens,
                None,
                ForwardMode.TARGET_VERIFY,
                self.verify_spec_info,
            )

            def run_verify():
                target_runner.attn_backend.init_forward_metadata_replay_cuda_graph(
                    1,
                    self.req_pool_indices,
                    self.seq_lens,
                    1,
                    None,
                    ForwardMode.TARGET_VERIFY,
                    self.verify_spec_info,
                    seq_lens_cpu=None,
                )
                target_positions = (
                    self.mrope_positions
                    if target_model.is_mrope_enabled
                    else self.positions
                )
                hidden_verify = target_model.model(
                    self.input_ids, target_positions, target_batch
                )
                verify_logits = torch.matmul(
                    hidden_verify.to(weight.dtype), weight.T
                )[:, :vocab_size].float()
                # PPU graph-capture warmup can expose uninitialized argmax
                # scratch values before the first replay. Clamp at the model
                # vocabulary boundary before feeding predictions to the
                # shared embedding; real argmax results are already in range.
                predict = torch.argmax(verify_logits, dim=-1).clamp(
                    min=0, max=vocab_size - 1
                )
                matches = self.input_ids[1:] == predict[:-1]
                accepted_prefix = torch.cumprod(
                    matches.to(torch.int32), dim=0
                )
                accept = accepted_prefix.sum().reshape(1).to(torch.int32)
                predict32 = predict.to(torch.int32)
                packed = torch.cat([predict32, accept])
                return (
                    predict,
                    accept,
                    predict32,
                    packed,
                    verify_logits,
                    hidden_verify,
                )

            for _ in range(2):
                torch.cuda.synchronize()
                self._verify_out = run_verify()
            self.graph_verify = torch.cuda.CUDAGraph()
            with torch.cuda.graph(self.graph_verify, stream=stream):
                self._verify_out = run_verify()

            # Materialize valid prediction/accept buffers before draft-graph
            # warmup. Capture-time output storage is not guaranteed to retain
            # the warmup values on PPU, and an uninitialized accept index can
            # address beyond the q_len=3 Mamba intermediate-state dimension.
            self.graph_verify.replay()
            torch.cuda.synchronize()

            self.graph_drafts = {}
            # Capture the largest shape first. The PPU Triton/acBLAS backend
            # specializes shared graph metadata/workspaces on first use; an
            # ascending capture made the later M=3 o_proj hit an internal
            # GEMM assertion, while this order matches DraftExtendGraphRunner.
            for n in range(self.num_tokens, 0, -1):
                spec_info = self.draft_spec_infos[n]
                draft_batch = ForwardBatch(
                    forward_mode=ForwardMode.DRAFT_EXTEND,
                    batch_size=1,
                    input_ids=self.input_ids[:n],
                    req_pool_indices=self.req_pool_indices,
                    seq_lens=self.seq_lens,
                    req_to_token_pool=draft_runner.req_to_token_pool,
                    token_to_kv_pool=draft_runner.token_to_kv_pool,
                    attn_backend=draft_runner.attn_backend,
                    out_cache_loc=self.out_cache_loc[:n],
                    seq_lens_sum=n,
                    return_logprob=False,
                    positions=self.positions[:n],
                    mrope_positions=self.mrope_positions[:, :n],
                    capture_hidden_mode=CaptureHiddenMode.LAST,
                    spec_info=spec_info,
                )
                draft_runner.attn_backend.init_forward_metadata_capture_cuda_graph(
                    1,
                    n,
                    self.req_pool_indices,
                    self.seq_lens,
                    None,
                    ForwardMode.DRAFT_EXTEND,
                    spec_info,
                )

                def run_draft(num_rows=n, forward_batch=draft_batch):
                    predict, accept, _, _, _, hidden_verify = self._verify_out
                    draft_backend = draft_runner.attn_backend
                    kv_indptr = draft_backend.kv_indptr
                    kv_indptr[1:2] = torch.cumsum(self.seq_lens, dim=0)
                    create_flashinfer_kv_indices_triton[(1,)](
                        draft_backend.req_to_token,
                        self.req_pool_indices,
                        self.seq_lens,
                        kv_indptr[:2],
                        None,
                        draft_backend.cuda_graph_kv_indices,
                        draft_backend.req_to_token.stride(0),
                    )
                    predict_n = predict[:num_rows]
                    hidden_n = hidden_verify[:num_rows]
                    positions_n = (
                        self.mrope_positions[:, :num_rows]
                        if draft_model.is_mrope_enabled
                        else self.positions[:num_rows]
                    )
                    draft_layers = draft_model.model
                    input_embeds = draft_layers.pre_fc_norm_embedding(
                        draft_layers.embed_tokens(predict_n)
                    )
                    draft_hidden = draft_layers.pre_fc_norm_hidden(hidden_n)
                    draft_hidden = draft_layers.fc(
                        torch.cat((input_embeds, draft_hidden), dim=-1)
                    )
                    draft_out = draft_layers(
                        predict_n, positions_n, forward_batch, draft_hidden
                    )
                    draft_row = draft_out[-1:]
                    draft_logits = torch.matmul(
                        draft_row.to(weight.dtype), weight.T
                    )[:, :vocab_size].float()
                    proposal = torch.argmax(draft_logits, dim=-1)
                    target_runner.attn_backend.update_mamba_state_after_mtp_verify(
                        accept, None, None, target_model
                    )
                    self.proposal32.copy_(proposal.to(torch.int32))
                    self.new_verified32.copy_(
                        predict_n[-1:].to(torch.int32)
                    )
                    self.draft_row.copy_(draft_row)

                for _ in range(2):
                    torch.cuda.synchronize()
                    run_draft()
                graph = torch.cuda.CUDAGraph()
                with torch.cuda.graph(graph, stream=stream):
                    run_draft()
                self.graph_drafts[n] = graph

        (
            _predict,
            self.accept,
            self.predict32,
            self.packed,
            self.verify_logits,
            self.hidden_verify,
        ) = self._verify_out

    def replay(self, batch, spec_info):
        self.input_ids.copy_(batch.input_ids)
        self.req_pool_indices.copy_(batch.req_pool_indices)
        self.seq_lens.copy_(batch.seq_lens)
        self.out_cache_loc.copy_(batch.out_cache_loc)
        self.positions.copy_(spec_info.positions)
        _copy_or_derive_mrope_positions(
            self.mrope_positions,
            self.num_tokens,
            SimpleNamespace(
                mrope_positions=None,
                mm_inputs=[batch.reqs[0].multimodal_inputs],
                positions=spec_info.positions,
            ),
        )
        self.graph_verify.replay()
        packed = self.packed.tolist()
        predictions, accept = packed[:-1], packed[-1]
        self.graph_drafts[accept + 1].replay()
        return predictions, accept
