#!/usr/bin/env python3
"""GEMV autotune for Qwen3.5-2B decode/verify projections on PPU 810E.

Searches BLOCK_N/BLOCK_K/num_warps/num_stages for M=1/2/3 shapes,
graph-times each valid config with L2 defeated by weight rotation, and
prints the best configs in a format ready to paste into
sglang/srt/layers/gemv_q2.py.

Run:
    python gemv_autotune.py          # reduced sweep, ~10-20 min
    python gemv_autotune.py full     # larger sweep
"""

import json
import sys
import time
from dataclasses import dataclass
from typing import Optional, Tuple

import torch
import triton
import triton.language as tl

# (K, N) text-model projection shapes seen in Qwen3.5-2B decode/verify.
# Weights are row-major (N, K); LM head is excluded (it has its own path).
SHAPES = [
    (2048, 6144),    # GDN in_proj_qkv x18
    (2048, 5120),    # full-attn qkv+gate x6
    (2048, 12288),   # MLP gate_up x24
    (2048, 2048),    # GDN in_proj_z / all out_proj
    (6144, 2048),    # MLP down_proj x24
    (4096, 2048),    # full-attn q_proj x6
    (512, 2048),     # full-attn k/v_proj x12
]

REDUCED_SPACE = {
    "BLOCK_N": [32, 64, 128],
    "BLOCK_K": [64, 128, 256],
    "num_warps": [2, 4, 8],
    "num_stages": [2, 3],
}

FULL_SPACE = {
    "BLOCK_N": [32, 64, 128, 256],
    "BLOCK_K": [64, 128, 256, 512],
    "num_warps": [2, 4, 8],
    "num_stages": [2, 3, 4],
}


@triton.jit
def _gemv_q1_dot_kernel(
    x_ptr, w_ptr, y_ptr,
    N, K,
    BLOCK_N: tl.constexpr,
    BLOCK_K: tl.constexpr,
):
    """M=1 GEMV via tl.dot, matching gemv_q2.py production kernel."""
    pid = tl.program_id(0)
    offs_n = pid * BLOCK_N + tl.arange(0, BLOCK_N)
    acc = tl.zeros((BLOCK_N, 1), dtype=tl.float32)
    for k0 in range(0, K, BLOCK_K):
        offs_k = k0 + tl.arange(0, BLOCK_K)
        x = tl.load(x_ptr + offs_k, mask=offs_k < K, other=0.0)
        w = tl.load(
            w_ptr + offs_n[:, None] * K + offs_k[None, :],
            mask=(offs_n[:, None] < N) & (offs_k[None, :] < K),
            other=0.0,
        )
        acc += tl.dot(w, x[:, None], out_dtype=tl.float32)
    tl.store(y_ptr + offs_n, acc[:, 0].to(tl.bfloat16), mask=offs_n < N)


@triton.jit
def _gemv_q1_sum_kernel(
    x_ptr, w_ptr, y_ptr,
    N, K,
    BLOCK_N: tl.constexpr,
    BLOCK_K: tl.constexpr,
):
    """M=1 GEMV via elementwise multiply + tl.sum (alternative numerics)."""
    pid = tl.program_id(0)
    offs_n = pid * BLOCK_N + tl.arange(0, BLOCK_N)
    acc = tl.zeros((BLOCK_N,), dtype=tl.float32)
    for k0 in range(0, K, BLOCK_K):
        offs_k = k0 + tl.arange(0, BLOCK_K)
        x = tl.load(x_ptr + offs_k, mask=offs_k < K, other=0.0)
        w = tl.load(
            w_ptr + offs_n[:, None] * K + offs_k[None, :],
            mask=(offs_n[:, None] < N) & (offs_k[None, :] < K),
            other=0.0,
        )
        acc += tl.sum(w.to(tl.float32) * x.to(tl.float32)[None, :], axis=1)
    tl.store(y_ptr + offs_n, acc.to(tl.bfloat16), mask=offs_n < N)


@triton.jit
def _gemv_q2_kernel(
    x_ptr, w_ptr, y_ptr,
    M, N, K,
    BLOCK_N: tl.constexpr,
    BLOCK_K: tl.constexpr,
    BLOCK_M: tl.constexpr,
):
    """M=2/3 GEMV via tl.dot, matching gemv_q2.py production kernel."""
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


def _call_q1_dot(x, w, y, BLOCK_N, BLOCK_K, num_warps, num_stages):
    N, K = w.shape
    _gemv_q1_dot_kernel[(triton.cdiv(N, BLOCK_N),)](
        x.view(-1), w, y.view(-1), N, K,
        BLOCK_N=BLOCK_N, BLOCK_K=BLOCK_K,
        num_warps=num_warps, num_stages=num_stages,
    )


def _call_q1_sum(x, w, y, BLOCK_N, BLOCK_K, num_warps, num_stages):
    N, K = w.shape
    _gemv_q1_sum_kernel[(triton.cdiv(N, BLOCK_N),)](
        x.view(-1), w, y.view(-1), N, K,
        BLOCK_N=BLOCK_N, BLOCK_K=BLOCK_K,
        num_warps=num_warps, num_stages=num_stages,
    )


def _call_q2(x, w, y, M, BLOCK_N, BLOCK_K, num_warps, num_stages):
    N, K = w.shape
    _gemv_q2_kernel[(triton.cdiv(N, BLOCK_N),)](
        x, w, y, M, N, K,
        BLOCK_N=BLOCK_N, BLOCK_K=BLOCK_K,
        BLOCK_M=16,
        num_warps=num_warps, num_stages=num_stages,
    )


def bench_graph(call, inner: int = 24, reps: int = 50):
    """Capture `inner` sequential calls into a CUDA graph and time replay."""
    s = torch.cuda.Stream()
    with torch.cuda.stream(s):
        for i in range(inner):
            call(i)
    torch.cuda.current_stream().wait_stream(s)
    g = torch.cuda.CUDAGraph()
    with torch.cuda.graph(g):
        for i in range(inner):
            call(i)
    g.replay()
    torch.cuda.synchronize()
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    start.record()
    for _ in range(reps):
        g.replay()
    end.record()
    torch.cuda.synchronize()
    return start.elapsed_time(end) / (reps * inner) * 1e3  # us per call


@dataclass
class Result:
    M: int
    K: int
    N: int
    kind: str
    BLOCK_N: int
    BLOCK_K: int
    num_warps: int
    num_stages: int
    us: float
    tb_s: float
    max_abs_diff: float
    bit_equal: bool


def _gb(M: int, K: int, N: int) -> float:
    return (2 * N * K + 2 * M * K + 2 * M * N) / 1e9


def sweep_shape(M: int, K: int, N: int, space: dict, copies: int = 24):
    x = torch.randn(M, K, device="cuda", dtype=torch.bfloat16)
    w_all = torch.randn(copies, N, K, device="cuda", dtype=torch.bfloat16) * 0.01
    y_ref = torch.nn.functional.linear(x, w_all[0])
    gb = _gb(M, K, N)

    results = []
    t_ref = bench_graph(lambda i: torch.nn.functional.linear(x, w_all[i % copies]))
    print(f"\n{K:>5}x{N:<6} M={M}: acBLAS {t_ref:6.1f} us ({gb/t_ref*1e3:5.2f} TB/s)")

    # M=1 kernels
    if M == 1:
        for kernel_name, call_fn in (("q1_dot", _call_q1_dot), ("q1_sum", _call_q1_sum)):
            for BLOCK_N in space["BLOCK_N"]:
                for BLOCK_K in space["BLOCK_K"]:
                    for num_warps in space["num_warps"]:
                        for num_stages in space["num_stages"]:
                            try:
                                y = torch.empty(1, N, device="cuda", dtype=torch.bfloat16)
                                call_fn(x, w_all[0], y, BLOCK_N, BLOCK_K, num_warps, num_stages)
                                max_abs_diff = (y.float() - y_ref.float()).abs().max().item()
                                bit_equal = torch.equal(y, y_ref)
                                if max_abs_diff > 1.0:
                                    continue
                                t = bench_graph(
                                    lambda i: call_fn(x, w_all[i % copies],
                                                      torch.empty(1, N, device="cuda", dtype=torch.bfloat16),
                                                      BLOCK_N, BLOCK_K, num_warps, num_stages),
                                    inner=min(24, copies),
                                )
                                results.append(Result(
                                    M, K, N, kernel_name, BLOCK_N, BLOCK_K, num_warps, num_stages,
                                    t, gb / t * 1e3, max_abs_diff, bit_equal,
                                ))
                            except Exception:
                                pass
    else:
        # M=2/3 dot kernel
        for BLOCK_N in space["BLOCK_N"]:
            for BLOCK_K in space["BLOCK_K"]:
                for num_warps in space["num_warps"]:
                    for num_stages in space["num_stages"]:
                        try:
                            y = torch.empty(M, N, device="cuda", dtype=torch.bfloat16)
                            _call_q2(x, w_all[0], y, M, BLOCK_N, BLOCK_K, num_warps, num_stages)
                            max_abs_diff = (y.float() - y_ref.float()).abs().max().item()
                            bit_equal = torch.equal(y, y_ref)
                            if not bit_equal:
                                continue
                            t = bench_graph(
                                lambda i: _call_q2(x, w_all[i % copies],
                                                   torch.empty(M, N, device="cuda", dtype=torch.bfloat16),
                                                   M, BLOCK_N, BLOCK_K, num_warps, num_stages),
                                inner=min(24, copies),
                            )
                            results.append(Result(
                                M, K, N, "dot", BLOCK_N, BLOCK_K, num_warps, num_stages,
                                t, gb / t * 1e3, max_abs_diff, bit_equal,
                            ))
                        except Exception:
                            pass

    results.sort(key=lambda r: r.us)
    eq_results = [r for r in results if r.bit_equal]
    best_eq = eq_results[0] if eq_results else None
    print(f"  best {len(results)} valid configs:")
    for r in results[:5]:
        eq = "EQ" if r.bit_equal else "~="
        print(f"    {r.kind:<8} BN={r.BLOCK_N:<4} BK={r.BLOCK_K:<4} "
              f"warps={r.num_warps} stages={r.num_stages}: "
              f"{r.us:6.1f} us ({r.tb_s:5.2f} TB/s) {eq} diff={r.max_abs_diff:.5f}")
    if best_eq and best_eq is not results[0]:
        print(f"  fastest EQ: {best_eq.kind:<8} BN={best_eq.BLOCK_N:<4} BK={best_eq.BLOCK_K:<4} "
              f"warps={best_eq.num_warps} stages={best_eq.num_stages}: "
              f"{best_eq.us:6.1f} us ({best_eq.tb_s:5.2f} TB/s)")
    return t_ref, results


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", nargs="?", default="reduced", choices=["reduced", "full"])
    parser.add_argument("--M", type=int, nargs="+", default=[1, 2, 3], choices=[1, 2, 3, 4, 5])
    args = parser.parse_args()

    space = FULL_SPACE if args.mode == "full" else REDUCED_SPACE
    torch.manual_seed(0)

    all_results = {}
    for M in args.M:
        table = {}
        for K, N in SHAPES:
            t_ref, results = sweep_shape(M, K, N, space)
            best = results[0] if results else None
            best_eq = next((r for r in results if r.bit_equal), None)
            table[(K, N)] = {
                "acBLAS_us": t_ref,
                "best": {
                    "kind": best.kind if best else None,
                    "BLOCK_N": best.BLOCK_N if best else None,
                    "BLOCK_K": best.BLOCK_K if best else None,
                    "num_warps": best.num_warps if best else None,
                    "num_stages": best.num_stages if best else None,
                    "us": best.us if best else None,
                    "TB_s": best.tb_s if best else None,
                    "bit_equal": best.bit_equal if best else None,
                    "max_abs_diff": best.max_abs_diff if best else None,
                },
                "best_eq": {
                    "kind": best_eq.kind if best_eq else None,
                    "BLOCK_N": best_eq.BLOCK_N if best_eq else None,
                    "BLOCK_K": best_eq.BLOCK_K if best_eq else None,
                    "num_warps": best_eq.num_warps if best_eq else None,
                    "num_stages": best_eq.num_stages if best_eq else None,
                    "us": best_eq.us if best_eq else None,
                    "TB_s": best_eq.tb_s if best_eq else None,
                } if best_eq else None,
                "speedup": t_ref / best.us if best else None,
                "all_results": [
                    {
                        "kind": r.kind, "BLOCK_N": r.BLOCK_N, "BLOCK_K": r.BLOCK_K,
                        "num_warps": r.num_warps, "num_stages": r.num_stages,
                        "us": r.us, "TB_s": r.tb_s, "bit_equal": r.bit_equal,
                        "max_abs_diff": r.max_abs_diff,
                    }
                    for r in results
                ],
            }
            all_results[f"M{M}_{K}x{N}"] = table[(K, N)]
        print(f"\n# M={M} config table (paste into gemv_q2.py):")
        print(f"_Q{M}_CONFIGS = {{")
        for (K, N), info in table.items():
            b = info["best"]
            if b["BLOCK_N"] is not None:
                print(f"    ({K}, {N}): ({b['BLOCK_N']}, {b['BLOCK_K']}, {b['num_warps']}, {b['num_stages']}),  # {info['speedup']:.2f}x vs acBLAS")
        print("}")

    out_path = f"/root/gemv_autotune_{args.mode}_{'_'.join(map(str, args.M))}_{int(time.time())}.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nFull results written to {out_path}")


if __name__ == "__main__":
    main()
