"""Env-gated speculative decode round profiler (P0 final-profile tooling).

Set ``SGLANG_SPEC_PROF=1`` to enable. The MTPWorker decode loop calls
``round_begin()`` / ``now()`` / ``mark()`` / ``round_end()``; when disabled
these are near-no-ops (a module flag check plus returning 0.0), so the hot
path is unaffected.

Segments per speculative round (host wall time). By default no device syncs
are added, so a segment that ends without a D2H transfer only measures CPU
enqueue time and the GPU execution lands in whichever later segment syncs
first (in practice ``accept`` absorbs the target verify GPU time via its
``.tolist()``). For true GPU-inclusive per-segment attribution set
``SGLANG_SPEC_PROF_SYNC=1``: a ``torch.cuda.synchronize()`` is then inserted
at every segment boundary. Sync mode perturbs pipelining, so compare totals
only against other sync-mode runs.

- ``draft_build``: MtpVerifyInput chain construction. The draft model
  forward itself is not here: with num_steps=1 the proposal is produced at
  the tail of the previous round (see ``draft_extend``).
- ``verify_meta``: prepare_for_verify + model_worker_batch construction.
- ``target_verify``: TARGET_VERIFY forward of the target model (graph
  replay): embedding + 18 GDN + 6 full attention + verify LM head.
- ``accept``: greedy acceptance comparison (spec_info.verify).
- ``commit``: accepted-step mamba state commit (commit graph replay or the
  eager fallback).
- ``draft_extend``: forward_draft_extend_after_decode = draft catch-up for
  the accepted tokens + next draft proposal (draft body + draft LM head +
  argmax). This is the P1 "Winning-State Reuse" target segment.
- ``round_gap``: wall time between the end of the previous round and the
  begin of this one, inside the worker. Scheduler/RPC overhead outside the
  worker is not included; it shows up as benchmark elapsed minus round sums.
- ``round_total``: begin-to-end wall time of the whole round.

Stats (count/sum/mean/p50/p95/max) are dumped every ``_DUMP_EVERY`` rounds;
the full payload including the raw per-round series (for per-accept-length
splitting) is written at process exit. Output path defaults to
``spec_prof.json`` and is overridden with ``SGLANG_SPEC_PROF_OUT``.
"""

import atexit
import json
import os
import time
from typing import Dict, List, Optional

ENABLED = os.environ.get("SGLANG_SPEC_PROF", "0") == "1"
SYNC = ENABLED and os.environ.get("SGLANG_SPEC_PROF_SYNC", "0") == "1"


def _sync() -> None:
    """Sync-mode barrier at segment boundaries (torch is already loaded in
    the scheduler process; import lazily to keep module import cheap)."""
    if SYNC:
        import torch

        torch.cuda.synchronize()

# One-shot import diagnostic: record pid + env as seen by this process, so we
# can tell whether spawned scheduler children inherit SGLANG_SPEC_PROF.
if os.environ.get("SGLANG_SPEC_PROF_DIAG") == "1":
    with open(f"/tmp/spec_prof_import_{os.getpid()}.log", "w") as _f:
        _f.write(f"enabled={ENABLED} out={os.environ.get('SGLANG_SPEC_PROF_OUT')}\n")
_OUT = os.environ.get("SGLANG_SPEC_PROF_OUT", "spec_prof.json")
_DUMP_EVERY = 256

SEGMENTS = (
    "draft_build",
    "verify_meta",
    "target_verify",
    "accept",
    "commit",
    "draft_extend",
    # P1 sub-segments (nested inside accept / draft_extend; not additive).
    "accept_argmax",
    "accept_d2h",
    "accept_loop",
    "accept_tail",
    "ext_prep",
    "ext_meta",
    "ext_replay",
    "ext_capture",
)

_seg: Dict[str, List[float]] = {name: [] for name in SEGMENTS}
_gap: List[float] = []
_total: List[float] = []
_accept: List[int] = []
_prev_round_end: Optional[float] = None
_rounds = 0


def now() -> float:
    if not ENABLED:
        return 0.0
    _sync()
    return time.perf_counter()


def mark(stage: str, started_at: float) -> None:
    if ENABLED:
        _sync()
        _seg[stage].append((time.perf_counter() - started_at) * 1e3)


def round_begin() -> float:
    """Stamp the begin of a speculative round; returns the start timestamp."""
    global _prev_round_end
    if not ENABLED:
        return 0.0
    t = time.perf_counter()
    if _prev_round_end is not None:
        _gap.append((t - _prev_round_end) * 1e3)
    return t


def round_end(started_at: float, accept_length: int) -> None:
    global _prev_round_end, _rounds
    if not ENABLED:
        return
    _sync()
    t = time.perf_counter()
    _total.append((t - started_at) * 1e3)
    _accept.append(accept_length)
    _prev_round_end = t
    _rounds += 1
    if _rounds % _DUMP_EVERY == 0:
        dump()


def _stats(xs: List[float]) -> dict:
    n = len(xs)
    if n == 0:
        return {"count": 0}
    s = sorted(xs)
    return {
        "count": n,
        "sum_ms": round(sum(s), 3),
        "mean_ms": round(sum(s) / n, 4),
        "p50_ms": round(s[n // 2], 4),
        "p95_ms": round(s[min(n - 1, int(0.95 * (n - 1)))], 4),
        "max_ms": round(s[-1], 4),
    }


def _payload(include_raw: bool) -> dict:
    payload = {
        "rounds": _rounds,
        "segments": {name: _stats(_seg[name]) for name in SEGMENTS},
        "round_gap": _stats(_gap),
        "round_total": _stats(_total),
        "accept_length": {
            "mean": round(sum(_accept) / len(_accept), 4) if _accept else 0.0,
            "hist": {
                str(k): _accept.count(k) for k in sorted(set(_accept))
            },
        },
    }
    if include_raw:
        payload["raw"] = {
            **{name: _seg[name] for name in SEGMENTS},
            "round_gap": _gap,
            "round_total": _total,
            "accept_length": _accept,
        }
    return payload


def dump() -> None:
    """Write the aggregated stats (no raw series) to ``_OUT``."""
    if not ENABLED or _rounds == 0:
        return
    with open(_OUT, "w") as f:
        json.dump(_payload(include_raw=False), f)


def _dump_final() -> None:
    if not ENABLED or _rounds == 0:
        return
    with open(_OUT, "w") as f:
        json.dump(_payload(include_raw=True), f)


atexit.register(_dump_final)
