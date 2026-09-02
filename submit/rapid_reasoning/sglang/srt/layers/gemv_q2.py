"""P1.5/P1.x: Triton split-N GEMV for the M=1/2/3 decode/verify paths.

BACKPORT-PPU (2026-08-24, see technical_route_v2.md section 6 / profile_v2):
acBLAS BF16 GEMM at small M runs the per-layer projections at low achieved
occupancy, while a tuned Triton split-N kernel can raise effective bandwidth.
This module routes decode/verify projections for M=1 (draft/target decode),
M=2 (depth-one verify / accept=2 draft extend), M=3 (depth-two verify),
M=4/M=5 (depth-three/four verify and the matching draft extend rows).

Shapes are whitelisted per (M, K, N) and tuned offline by graph-timed sweep
with L2 defeated by weight rotation.  Run
    python rapid_reasoning/docs/profile_v2/gemv_autotune.py
    python rapid_reasoning/docs/profile_v2/gemv_autotune.py reduced --M 1
    python rapid_reasoning/docs/profile_v2/gemv_autotune.py reduced --M 2 3
to regenerate the config tables.

FP32 accumulation, BF16 in/out.  M>=2 kernels are bitwise identical to
F.linear for the tuned shapes (same FP32 sequential accumulation class).
M=1 uses a dedicated GEMV kernel and is kept opt-in because near-tie
argmax can still differ; enable with SGLANG_GEMV_Q1=1 only after A/B
validation.

Enabled by default for M>=2; set SGLANG_GEMV_Q2=0 to fall back to F.linear.
Set SGLANG_GEMV_Q3=0 to disable only the M==3 extension.
Set SGLANG_GEMV_Q45=0 to disable only the M==4/5 extension.
Set SGLANG_GEMV_Q1=1 to enable the experimental M==1 path.
"""

import logging
import os
from typing import Optional

import torch
import triton
import triton.language as tl

logger = logging.getLogger(__name__)

ENABLED = os.environ.get("SGLANG_GEMV_Q2", "1") == "1"
Q1_ENABLED = os.environ.get("SGLANG_GEMV_Q1", "0") == "1"
Q3_ENABLED = os.environ.get("SGLANG_GEMV_Q3", "1") == "1"
Q45_ENABLED = os.environ.get("SGLANG_GEMV_Q45", "1") == "1"

# (K, N) -> (BLOCK_N, BLOCK_K, num_warps, num_stages).
# Seeded from graph-timed sweeps (gemv_autotune.py, PPU-ZW810E).
# Only shapes that beat acBLAS in graph-timed micro-benchmark are included;
# others fall back to F.linear/acBLAS.
_Q1_CONFIGS = {
    # M=1: draft/target decode projections.
    # The q1_sum kernel is within 1-2 BF16 ULP of F.linear but caused a
    # near-tie argmax flip in EN1000 (qid 1653, 1/1000).  Kept empty by
    # default until a bitwise-equal M=1 GEMV kernel is found.  Experimental
    # configs from autotune:
    #   (2048, 5120): (32, 256, 8, 3),   # full-attn qkv+gate, EQ in micro-bench
    #   (2048, 6144): (32, 128, 8, 3),   # GDN in_proj_qkv, ~+14%, non-EQ
    #   (2048, 12288): (64, 128, 8, 2),  # MLP gate_up, ~+16%, non-EQ
}

_Q2_CONFIGS = {
    # M=2: depth-one target verify / accept=2 draft extend
    (2048, 6144): (64, 128, 4, 3),   # GDN in_proj_qkv, ~+15%
    (2048, 5120): (64, 128, 4, 4),   # full-attn qkv+gate, ~+21%
    (2048, 12288): (64, 128, 2, 2),  # MLP gate_up, ~+14%
    (512, 2048): (32, 64, 2, 3),     # full-attn k/v_proj, ~+49%
}

_Q3_CONFIGS = {
    # M=3: depth-two target verify
    (2048, 6144): (64, 128, 4, 3),
    (2048, 5120): (64, 128, 4, 4),
    (2048, 12288): (64, 128, 2, 2),
    (512, 2048): (32, 64, 2, 3),
}

_Q4_CONFIGS = {
    # M=4: depth-three target verify / accept=4 draft extend
    (2048, 6144): (64, 128, 4, 3),   # 1.16x vs acBLAS
    (2048, 5120): (64, 128, 4, 3),   # 1.21x vs acBLAS
    (2048, 12288): (64, 128, 2, 2),  # 1.15x vs acBLAS
    (512, 2048): (32, 64, 2, 3),     # 1.49x vs acBLAS
}

_Q5_CONFIGS = {
    # M=5: depth-four target verify / accept=5 draft extend
    (2048, 6144): (64, 128, 4, 3),   # 1.15x vs acBLAS
    (2048, 5120): (64, 128, 4, 3),   # 1.21x vs acBLAS
    (2048, 12288): (64, 128, 2, 2),  # 1.15x vs acBLAS
    (512, 2048): (32, 64, 2, 3),     # 1.49x vs acBLAS
}


def _get_config(M: int, K: int, N: int):
    if M == 1:
        return _Q1_CONFIGS.get((K, N))
    if M == 2:
        return _Q2_CONFIGS.get((K, N))
    if M == 3:
        return _Q3_CONFIGS.get((K, N))
    if M == 4:
        return _Q4_CONFIGS.get((K, N))
    if M == 5:
        return _Q5_CONFIGS.get((K, N))
    return None


@triton.jit
def _gemv_q1_kernel(
    x_ptr,  # (K,) bf16
    w_ptr,  # (N, K) bf16, row-major
    y_ptr,  # (N,) bf16
    N, K,
    BLOCK_N: tl.constexpr,
    BLOCK_K: tl.constexpr,
):
    """Dedicated M=1 GEMV: one CTA per BLOCK_N outputs, elementwise sum over K.

    tl.dot requires both non-batch dims >= 16, so a true (BLOCK_K, 1) GEMV
    dot is not expressible.  We use tl.sum(w * x[None, :], axis=1) instead.
    This matches the autotune-winning q1_sum kernel and is within 1-2 BF16
    ULP of F.linear for the tuned shapes; A/B validation is required.
    """
    pid = tl.program_id(0)
    offs_n = pid * BLOCK_N + tl.arange(0, BLOCK_N)
    acc = tl.zeros((BLOCK_N,), dtype=tl.float32)
    for k0 in range(0, K, BLOCK_K):
        offs_k = k0 + tl.arange(0, BLOCK_K)
        x = tl.load(
            x_ptr + offs_k,
            mask=offs_k < K,
            other=0.0,
        )
        w = tl.load(
            w_ptr + offs_n[:, None] * K + offs_k[None, :],
            mask=(offs_n[:, None] < N) & (offs_k[None, :] < K),
            other=0.0,
        )
        acc += tl.sum(w.to(tl.float32) * x.to(tl.float32)[None, :], axis=1)
    tl.store(
        y_ptr + offs_n,
        acc.to(tl.bfloat16),
        mask=offs_n < N,
    )


@triton.jit
def _gemv_q2_kernel(
    x_ptr,  # (M, K) bf16
    w_ptr,  # (N, K) bf16, row-major
    y_ptr,  # (M, N) bf16
    M, N, K,
    BLOCK_N: tl.constexpr,
    BLOCK_K: tl.constexpr,
    BLOCK_M: tl.constexpr,  # M padded to >=16 for tl.dot
):
    pid = tl.program_id(0)
    offs_n = pid * BLOCK_N + tl.arange(0, BLOCK_N)
    offs_m = tl.arange(0, BLOCK_M)
    acc = tl.zeros((BLOCK_N, BLOCK_M), dtype=tl.float32)
    for k0 in range(0, K, BLOCK_K):
        offs_k = k0 + tl.arange(0, BLOCK_K)
        x = tl.load(
            x_ptr + offs_m[:, None] * K + offs_k[None, :],
            mask=(offs_m[:, None] < M) & (offs_k[None, :] < K),
            other=0.0,
        )
        w = tl.load(
            w_ptr + offs_n[:, None] * K + offs_k[None, :],
            mask=(offs_n[:, None] < N) & (offs_k[None, :] < K),
            other=0.0,
        )
        acc += tl.dot(w, tl.trans(x), out_dtype=tl.float32)
    tl.store(
        y_ptr + offs_m[None, :] * N + offs_n[:, None],
        acc.to(tl.bfloat16),
        mask=(offs_m[None, :] < M) & (offs_n[:, None] < N),
    )


def disable_in_subtree(root: torch.nn.Module) -> None:
    """Mark every LinearBase layer under `root` as GEMV-ineligible.

    Used for target/draft scope bisection (SGLANG_GEMV_Q2_TARGET /
    SGLANG_GEMV_Q2_DRAFT): the draft and target share the Linear classes,
    so scope is tagged per module tree at model construction time.
    """
    from sglang.srt.layers.linear import LinearBase

    for m in root.modules():
        if isinstance(m, LinearBase):
            m._gemv_q2_disable = True


def gemv_q2_or_none(
    x: torch.Tensor, weight: torch.Tensor, bias: Optional[torch.Tensor],
    layer: Optional[torch.nn.Module] = None,
) -> Optional[torch.Tensor]:
    """Return x @ weight.T via the tuned kernel, or None to fall back.

    Eligible: 2D contiguous x with M in {1,2,3,4,5}, contiguous BF16 weight
    whose (K, N) shape is in the tuned whitelist, no bias.

    M>=2 kernels are bitwise identical to F.linear for the tuned shapes.
    M=1 is opt-in (SGLANG_GEMV_Q1=1) because its GEMV kernel can still differ
    on near-tie logits; use EN/CN 1000-question A/B before defaulting it on.
    """
    if bias is not None or x.dim() != 2 or x.shape[0] not in (1, 2, 3, 4, 5):
        return None
    if layer is not None and getattr(layer, "_gemv_q2_disable", False):
        return None
    M, K = x.shape
    N = weight.shape[0]
    cfg = _get_config(M, K, N)
    if (
        cfg is None
        or (M == 1 and not Q1_ENABLED)
        or (M == 3 and not Q3_ENABLED)
        or (M in (4, 5) and not Q45_ENABLED)
        or weight.dtype != torch.bfloat16
        or x.dtype != torch.bfloat16
        or not x.is_contiguous()
        or not weight.is_contiguous()
    ):
        return None
    BLOCK_N, BLOCK_K, num_warps, num_stages = cfg
    y = torch.empty((M, N), device=x.device, dtype=torch.bfloat16)
    if M == 1:
        _gemv_q1_kernel[(triton.cdiv(N, BLOCK_N),)](
            x.view(-1), weight, y.view(-1), N, K,
            BLOCK_N=BLOCK_N, BLOCK_K=BLOCK_K,
            num_warps=num_warps, num_stages=num_stages,
        )
    else:
        _gemv_q2_kernel[(triton.cdiv(N, BLOCK_N),)](
            x, weight, y, M, N, K,
            BLOCK_N=BLOCK_N, BLOCK_K=BLOCK_K,
            BLOCK_M=16,
            num_warps=num_warps, num_stages=num_stages,
        )
    if _CHECK:
        _check_against_reference(x, weight, y)
    return y


_CHECK = os.environ.get("SGLANG_GEMV_Q2_CHECK", "0") == "1"
_check_stats = {"calls": 0, "mismatch": 0}


def _check_against_reference(x, weight, y) -> None:
    """SGLANG_GEMV_Q2_CHECK=1: bitwise-compare against F.linear in context
    and print pointer alignments on mismatch (investigation-only knob).
    Uses print: sglang subprocesses filter INFO/WARNING logs."""
    import sys

    import torch.nn.functional as F

    ref = F.linear(x, weight)
    _check_stats["calls"] += 1
    if not torch.equal(y, ref):
        _check_stats["mismatch"] += 1
        diff = (y.float() - ref.float()).abs().max().item()
        print(
            f"GEMVQ2CHECK mismatch #{_check_stats['mismatch']}"
            f"/{_check_stats['calls']} shape=({x.shape[0]},"
            f"{weight.shape[1]},{weight.shape[0]}) max_abs_diff={diff:.6f} "
            f"x_ptr%256={x.data_ptr() % 256} w_ptr%256={weight.data_ptr() % 256} "
            f"x_stride={tuple(x.stride())}",
            file=sys.stderr, flush=True,
        )
    elif _check_stats["calls"] % 2000 == 0:
        print(f"GEMVQ2CHECK {_check_stats['calls']} calls, all equal",
              file=sys.stderr, flush=True)
