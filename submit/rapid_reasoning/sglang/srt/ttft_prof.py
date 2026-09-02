"""Env-gated TTFT stage breakdown profiler.

Set ``SGLANG_TTFT_PROF=1`` to enable. Each instrumented stage logs one
``TTFTPROF {json}`` line. The benchmark is strictly serial (bs=1), so lines
align with samples by order; ``rid`` is attached where available to join
against ``meta.sglang_meta.id`` in the benchmark result JSON.

Stages:
- ``mm_host``: host-side multimodal preprocessing (tokenizer_manager).
- ``vision_gpu``: vision encoder forward inside the prefill (qwen3_vl).
- ``extend_gpu``: full eager extend forward incl. vision (model_runner);
  LLM prefill time = ``extend_gpu`` - ``vision_gpu``.

Residual (wrapper TTFT - all stages) covers tokenize/RPC/scheduling/first
decode/detokenize/stream-return.
"""

import json
import os
import sys
import time

ENABLED = os.environ.get("SGLANG_TTFT_PROF", "0") == "1"


def mark(stage: str, started_at: float, rid=None, **extra) -> None:
    """Log one stage timing; ``started_at`` is a perf_counter() value."""
    if not ENABLED:
        return
    rec = {"stage": stage, "ms": round((time.perf_counter() - started_at) * 1e3, 3)}
    if rid is not None:
        rec["rid"] = rid
    rec.update(extra)
    # print instead of logging: sglang subprocesses filter INFO logs.
    print(f"TTFTPROF {json.dumps(rec, ensure_ascii=False)}", file=sys.stderr, flush=True)



def stamp(stage: str, rid=None, **extra) -> None:
    """Log an absolute perf_counter timestamp (ms) for cross-process segments."""
    if not ENABLED:
        return
    rec = {"stage": stage, "ts": round(time.perf_counter() * 1e3, 3)}
    if rid is not None:
        rec["rid"] = rid
    rec.update(extra)
    print(f"TTFTPROF {json.dumps(rec, ensure_ascii=False)}", file=sys.stderr, flush=True)
