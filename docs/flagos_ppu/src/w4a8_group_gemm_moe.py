import torch
import triton
import triton.language as tl


BLOCK_M_DEFAULT = 16
BLOCK_N_DEFAULT = 32
BLOCK_K_DEFAULT = 64
UNPACK_BLOCK_N = 16
UNPACK_BLOCK_K = 128
ASCEND_SCALAR_BLOCK_N = 1
ASCEND_SCALAR_BLOCK_K = 128
SCALAR_NBLOCK_N = 4
SCALAR_NBLOCK_K = 64


def _backend_tag(t: torch.Tensor) -> str:
    parts = [str(t.device).lower(), str(getattr(t.device, "type", "")).lower()]
    cuda = getattr(torch, "cuda", None)
    if cuda is not None and cuda.is_available():
        index = t.device.index
        if index is None:
            index = cuda.current_device()
        parts.append(str(cuda.get_device_name(index)).lower())
    c_mod = getattr(torch, "_C", None)
    get_private = getattr(c_mod, "_get_privateuse1_backend_name", None)
    if get_private is not None:
        parts.append(str(get_private()).lower())
    version = getattr(torch, "version", None)
    if version is not None:
        hip_version = getattr(version, "hip", None)
        if hip_version:
            parts.append("hip rocm dcu")
    return " ".join(parts)


def _use_direct_gemm(t: torch.Tensor) -> bool:
    tag = _backend_tag(t)
    compile_risky = ("ascend", "npu", "910", "moore", "musa", "hygon", "hip", "rocm", "dcu")
    if any(key in tag for key in compile_risky):
        return False
    fast_ok = ("nvidia", "metax", "maca", "t-head", "thead", "tian", "iluvatar", "corex", "cuda")
    return any(key in tag for key in fast_ok)


def _use_scalar_bridge(t: torch.Tensor) -> bool:
    tag = _backend_tag(t)
    return any(key in tag for key in ("ascend", "npu", "910", "hygon", "moore", "musa", "hip", "rocm", "dcu"))


def _use_hygon_bridge(t: torch.Tensor) -> bool:
    tag = _backend_tag(t)
    return any(key in tag for key in ("hygon", "hip", "rocm", "dcu"))


def _use_ascend_bridge(t: torch.Tensor) -> bool:
    tag = _backend_tag(t)
    return any(key in tag for key in ("ascend", "npu", "910"))


def _use_tianshu_direct(t: torch.Tensor) -> bool:
    tag = _backend_tag(t)
    return any(key in tag for key in ("tianshu", "tian", "iluvatar", "corex"))


@triton.jit
def _unpack_w4_kernel(w_q4_packed, w_zero, w_signed,
                      E:tl.constexpr, N:tl.constexpr, K:tl.constexpr,
                      GROUP_SIZE:tl.constexpr, G:tl.constexpr, K_HALF:tl.constexpr,
                      BLOCK_N_:tl.constexpr, BLOCK_K_:tl.constexpr):
    expert = tl.program_id(0)
    pid_n = tl.program_id(1)
    pid_k = tl.program_id(2)
    ns = pid_n * BLOCK_N_ + tl.arange(0, BLOCK_N_)
    ks = pid_k * BLOCK_K_ + tl.arange(0, BLOCK_K_)
    byte_k = ks // 2
    group = ks // GROUP_SIZE

    packed = tl.load(
        w_q4_packed + expert * N * K_HALF + ns[:, None] * K_HALF + byte_k[None, :],
        mask=(ns[:, None] < N) & (ks[None, :] < K),
        other=0,
    ).to(tl.uint8)
    low = packed & 0x0F
    high = (packed >> 4) & 0x0F
    w4 = tl.where((ks[None, :] & 1) == 0, low, high).to(tl.int16)
    wz = tl.load(
        w_zero + expert * N * G + ns[:, None] * G + group[None, :],
        mask=(ns[:, None] < N) & (ks[None, :] < K),
        other=0,
    ).to(tl.int16)
    signed = (w4 - wz).to(tl.int8)
    tl.store(
        w_signed + expert * N * K + ns[:, None] * K + ks[None, :],
        signed,
        mask=(ns[:, None] < N) & (ks[None, :] < K),
    )






@triton.jit
def _w4a8_scalar_global_nblock_kernel(x_q, x_scale, w_q4_packed, w_scale, w_zero, expert_offsets, out,
                                      M_TOTAL:tl.constexpr, E:tl.constexpr, N:tl.constexpr, K:tl.constexpr,
                                      GROUP_SIZE:tl.constexpr, G:tl.constexpr, K_HALF:tl.constexpr,
                                      BLOCK_N_:tl.constexpr, BLOCK_K_:tl.constexpr):
    row = tl.program_id(0)
    n0 = tl.program_id(1) * BLOCK_N_
    ns = n0 + tl.arange(0, BLOCK_N_)
    ks_off = tl.arange(0, BLOCK_K_)

    expert = tl.full((), 0, tl.int32)
    for e in range(0, E):
        next_start = tl.load(expert_offsets + e + 1).to(tl.int32)
        expert += tl.where(row >= next_start, 1, 0)

    valid = row < M_TOTAL
    n_mask = ns < N
    acc = tl.zeros((BLOCK_N_,), tl.float32)
    for g in range(0, G):
        group_acc = tl.zeros((BLOCK_N_,), tl.float32)
        for kk in range(0, GROUP_SIZE, BLOCK_K_):
            ks = g * GROUP_SIZE + kk + ks_off
            k_mask = (ks < K) & (ks < (g + 1) * GROUP_SIZE)
            byte_k = ks // 2
            packed = tl.load(
                w_q4_packed + expert * N * K_HALF + ns[None, :] * K_HALF + byte_k[:, None],
                mask=valid & n_mask[None, :] & k_mask[:, None],
                other=0,
            ).to(tl.uint8)
            low = packed & 0x0F
            high = (packed >> 4) & 0x0F
            w4 = tl.where((ks[:, None] & 1) == 0, low, high).to(tl.int32)
            wz = tl.load(
                w_zero + expert * N * G + ns * G + g,
                mask=valid & n_mask,
                other=0,
            ).to(tl.int32)
            wdiff = w4 - wz[None, :]
            wv = ((wdiff + 128) & 0xFF) - 128
            xv = tl.load(
                x_q + row * K + ks,
                mask=valid & k_mask,
                other=0,
            ).to(tl.int32)
            group_acc += tl.sum((xv[:, None] * wv).to(tl.float32), axis=0)

        ws = tl.load(
            w_scale + expert * N * G + ns * G + g,
            mask=valid & n_mask,
            other=0.0,
        ).to(tl.float32)
        acc += group_acc * ws

    xs = tl.load(x_scale + row, mask=valid, other=0.0).to(tl.float32)
    out_val = (acc * xs).to(tl.bfloat16)
    tl.store(out + row * N + ns, out_val, mask=valid & n_mask)








@triton.jit
def _w4a8_scalar_global_bridge_loop_kernel(x_q, x_scale, w_q4_packed, w_scale, w_zero, expert_offsets, out,
                                           M_TOTAL:tl.constexpr, E:tl.constexpr, N:tl.constexpr, K:tl.constexpr,
                                           GROUP_SIZE:tl.constexpr, G:tl.constexpr, K_HALF:tl.constexpr,
                                           TOTAL_LOGICAL:tl.constexpr, NCORE:tl.constexpr,
                                           BLOCK_K_:tl.constexpr):
    pid0 = tl.program_id(0)
    ks_off = tl.arange(0, BLOCK_K_)

    for base in range(0, TOTAL_LOGICAL, NCORE):
        logical = base + pid0
        if logical < TOTAL_LOGICAL:
            row = logical // N
            n = logical - row * N

            expert = tl.full((), 0, tl.int32)
            for e in range(0, E):
                next_start = tl.load(expert_offsets + e + 1).to(tl.int32)
                expert += tl.where(row >= next_start, 1, 0)

            valid = (row < M_TOTAL) & (n < N)
            acc = 0.0
            for g in range(0, G):
                group_acc = 0.0
                for kk in range(0, GROUP_SIZE, BLOCK_K_):
                    ks = g * GROUP_SIZE + kk + ks_off
                    k_mask = (ks < K) & (ks < (g + 1) * GROUP_SIZE)
                    byte_k = ks // 2
                    packed = tl.load(
                        w_q4_packed + expert * N * K_HALF + n * K_HALF + byte_k,
                        mask=valid & k_mask,
                        other=0,
                    ).to(tl.uint8)
                    low = packed & 0x0F
                    high = (packed >> 4) & 0x0F
                    w4 = tl.where((ks & 1) == 0, low, high).to(tl.int32)
                    wz = tl.load(
                        w_zero + expert * N * G + n * G + g,
                        mask=valid,
                        other=0,
                    ).to(tl.int32)
                    wdiff = w4 - wz
                    wv = ((wdiff + 128) & 0xFF) - 128
                    xv = tl.load(
                        x_q + row * K + ks,
                        mask=valid & k_mask,
                        other=0,
                    ).to(tl.int32)
                    group_acc += tl.sum((xv * wv).to(tl.float32), axis=0)

                ws = tl.load(
                    w_scale + expert * N * G + n * G + g,
                    mask=valid,
                    other=0.0,
                ).to(tl.float32)
                acc += group_acc * ws

            xs = tl.load(x_scale + row, mask=valid, other=0.0).to(tl.float32)
            out_val = (acc * xs).to(tl.bfloat16)
            tl.store(out + row * N + n, out_val, mask=valid)




@triton.jit
def _w4a8_gemm_direct_kernel(x_q, x_scale, w_q4_packed, w_scale, w_zero, expert_offsets, out,
                             M_TOTAL:tl.constexpr, E:tl.constexpr, N:tl.constexpr, K:tl.constexpr,
                             GROUP_SIZE:tl.constexpr, G:tl.constexpr, K_HALF:tl.constexpr,
                             BLOCK_M_:tl.constexpr, BLOCK_N_:tl.constexpr, BLOCK_K_:tl.constexpr):
    expert = tl.program_id(0)
    pid_m = tl.program_id(1)
    pid_n = tl.program_id(2)

    m_start = tl.load(expert_offsets + expert).to(tl.int32)
    m_end = tl.load(expert_offsets + expert + 1).to(tl.int32)
    rows = m_start + pid_m * BLOCK_M_ + tl.arange(0, BLOCK_M_)
    ns = pid_n * BLOCK_N_ + tl.arange(0, BLOCK_N_)
    offs_k = tl.arange(0, BLOCK_K_)

    row_mask = rows < m_end
    n_mask = ns < N
    acc = tl.zeros((BLOCK_M_, BLOCK_N_), tl.float32)

    for g in range(0, G):
        group_acc = tl.zeros((BLOCK_M_, BLOCK_N_), tl.float32)
        for kk in range(0, GROUP_SIZE, BLOCK_K_):
            ks = g * GROUP_SIZE + kk + offs_k
            byte_k = ks // 2
            packed = tl.load(
                w_q4_packed + expert * N * K_HALF + ns[None, :] * K_HALF + byte_k[:, None],
                mask=(n_mask[None, :] & (ks[:, None] < K)),
                other=0,
            ).to(tl.uint8)
            low = packed & 0x0F
            high = (packed >> 4) & 0x0F
            w4 = tl.where((ks[:, None] & 1) == 0, low, high).to(tl.int16)
            wz = tl.load(
                w_zero + expert * N * G + ns * G + g,
                mask=n_mask,
                other=0,
            ).to(tl.int16)
            wv = (w4 - wz[None, :]).to(tl.int8)
            xv = tl.load(
                x_q + rows[:, None] * K + ks[None, :],
                mask=(row_mask[:, None] & (ks[None, :] < K)),
                other=0,
            ).to(tl.int8)
            group_acc += tl.dot(xv, wv)

        ws = tl.load(
            w_scale + expert * N * G + ns * G + g,
            mask=n_mask,
            other=0.0,
        ).to(tl.float32)
        acc += group_acc * ws[None, :]

    xs = tl.load(x_scale + rows, mask=row_mask, other=0.0).to(tl.float32)
    acc = acc * xs[:, None]
    tl.store(
        out + rows[:, None] * N + ns[None, :],
        acc,
        mask=row_mask[:, None] & n_mask[None, :],
    )


@triton.jit
def _w4a8_gemm_unpacked_kernel(x_q, x_scale, w_signed, w_scale, expert_offsets, out,
                               M_TOTAL:tl.constexpr, E:tl.constexpr, N:tl.constexpr, K:tl.constexpr,
                               GROUP_SIZE:tl.constexpr, G:tl.constexpr,
                               BLOCK_M_:tl.constexpr, BLOCK_N_:tl.constexpr, BLOCK_K_:tl.constexpr):
    expert = tl.program_id(0)
    pid_m = tl.program_id(1)
    pid_n = tl.program_id(2)

    m_start = tl.load(expert_offsets + expert).to(tl.int32)
    m_end = tl.load(expert_offsets + expert + 1).to(tl.int32)
    rows = m_start + pid_m * BLOCK_M_ + tl.arange(0, BLOCK_M_)
    ns = pid_n * BLOCK_N_ + tl.arange(0, BLOCK_N_)
    offs_k = tl.arange(0, BLOCK_K_)

    row_mask = rows < m_end
    n_mask = ns < N
    acc = tl.zeros((BLOCK_M_, BLOCK_N_), tl.float32)

    for g in range(0, G):
        group_acc = tl.zeros((BLOCK_M_, BLOCK_N_), tl.float32)
        for kk in range(0, GROUP_SIZE, BLOCK_K_):
            ks = g * GROUP_SIZE + kk + offs_k
            xv = tl.load(
                x_q + rows[:, None] * K + ks[None, :],
                mask=(row_mask[:, None] & (ks[None, :] < K)),
                other=0,
            ).to(tl.int8)
            wv = tl.load(
                w_signed + expert * N * K + ns[None, :] * K + ks[:, None],
                mask=(n_mask[None, :] & (ks[:, None] < K)),
                other=0,
            ).to(tl.int8)
            group_acc += tl.dot(xv, wv)

        ws = tl.load(
            w_scale + expert * N * G + ns * G + g,
            mask=n_mask,
            other=0.0,
        ).to(tl.float32)
        acc += group_acc * ws[None, :]

    xs = tl.load(x_scale + rows, mask=row_mask, other=0.0).to(tl.float32)
    acc = acc * xs[:, None]
    tl.store(
        out + rows[:, None] * N + ns[None, :],
        acc,
        mask=row_mask[:, None] & n_mask[None, :],
    )


@triton.jit
def _w4a8_hygon_fp16_transb_dot_kernel(x_q, x_scale, w_signed, w_scale, expert_offsets, out,
                                       M_TOTAL:tl.constexpr, E:tl.constexpr, N:tl.constexpr, K:tl.constexpr,
                                       GROUP_SIZE:tl.constexpr, G:tl.constexpr,
                                       BLOCK_M_:tl.constexpr, BLOCK_N_:tl.constexpr, BLOCK_K_:tl.constexpr):
    expert = tl.program_id(0)
    pid_m = tl.program_id(1)
    pid_n = tl.program_id(2)

    m_start = tl.load(expert_offsets + expert).to(tl.int32)
    m_end = tl.load(expert_offsets + expert + 1).to(tl.int32)
    rows = m_start + pid_m * BLOCK_M_ + tl.arange(0, BLOCK_M_)
    ns = pid_n * BLOCK_N_ + tl.arange(0, BLOCK_N_)
    offs_k = tl.arange(0, BLOCK_K_)

    row_mask = rows < m_end
    n_mask = ns < N
    acc = tl.zeros((BLOCK_M_, BLOCK_N_), tl.float32)

    for g in range(0, G):
        group_acc = tl.zeros((BLOCK_M_, BLOCK_N_), tl.float32)
        for kk in range(0, GROUP_SIZE, BLOCK_K_):
            ks = g * GROUP_SIZE + kk + offs_k
            x_tile = tl.load(
                x_q + rows[:, None] * K + ks[None, :],
                mask=row_mask[:, None] & (ks[None, :] < K),
                other=0,
            ).to(tl.float16)
            w_tile = tl.load(
                w_signed + expert * N * K + ns[:, None] * K + ks[None, :],
                mask=n_mask[:, None] & (ks[None, :] < K),
                other=0,
            ).to(tl.float16)
            group_acc += tl.dot(x_tile, tl.trans(w_tile), out_dtype=tl.float32)

        ws = tl.load(
            w_scale + expert * N * G + ns * G + g,
            mask=n_mask,
            other=0.0,
        ).to(tl.float32)
        acc += group_acc * ws[None, :]

    xs = tl.load(x_scale + rows, mask=row_mask, other=0.0).to(tl.float32)
    acc = acc * xs[:, None]
    tl.store(
        out + rows[:, None] * N + ns[None, :],
        acc,
        mask=row_mask[:, None] & n_mask[None, :],
    )


def w4a8_group_gemm_moe(
    x_q: torch.Tensor,
    x_scale: torch.Tensor,
    w_q4_packed: torch.Tensor,
    w_scale: torch.Tensor,
    w_zero: torch.Tensor,
    expert_offsets: torch.Tensor,
    out: torch.Tensor,
    group_size: int,
) -> torch.Tensor:
    M_total, K = x_q.shape
    E, N, K_half = w_q4_packed.shape
    G = K // group_size

    block_m = BLOCK_M_DEFAULT
    block_n = BLOCK_N_DEFAULT
    block_k = BLOCK_K_DEFAULT
    rows_per_expert = triton.cdiv(M_total, E)
    tiles_m = triton.cdiv(rows_per_expert, block_m)
    tiles_n = triton.cdiv(N, block_n)
    grid = (E, tiles_m, tiles_n)
    if _use_scalar_bridge(x_q):
        if _use_ascend_bridge(x_q):
            total_logical = M_total * N
            ascend_ncore = min(total_logical, 32768)
            _w4a8_scalar_global_bridge_loop_kernel[(ascend_ncore,)](
                x_q, x_scale, w_q4_packed, w_scale, w_zero, expert_offsets, out,
                M_total, E, N, K, group_size, G, K_half,
                TOTAL_LOGICAL=total_logical,
                NCORE=ascend_ncore,
                BLOCK_K_=ASCEND_SCALAR_BLOCK_K,
                num_warps=4,
                num_stages=3,
            )
        else:
            if _use_hygon_bridge(x_q):
                hygon_block_n = 128
                hygon_grid = (E, tiles_m, triton.cdiv(N, hygon_block_n))
                w_signed = torch.empty((E, N, K), device=x_q.device, dtype=torch.int8)
                _unpack_w4_kernel[(E, triton.cdiv(N, UNPACK_BLOCK_N), triton.cdiv(K, UNPACK_BLOCK_K))](
                    w_q4_packed, w_zero, w_signed,
                    E, N, K, group_size, G, K_half,
                    BLOCK_N_=UNPACK_BLOCK_N,
                    BLOCK_K_=UNPACK_BLOCK_K,
                    num_warps=4,
                    num_stages=3,
                )
                _w4a8_hygon_fp16_transb_dot_kernel[hygon_grid](
                    x_q, x_scale, w_signed, w_scale, expert_offsets, out,
                    M_total, E, N, K, group_size, G,
                    BLOCK_M_=block_m,
                    BLOCK_N_=hygon_block_n,
                    BLOCK_K_=block_k,
                    num_warps=8,
                    num_stages=3,
                )
            else:
                _w4a8_scalar_global_nblock_kernel[(M_total, triton.cdiv(N, SCALAR_NBLOCK_N))](
                    x_q, x_scale, w_q4_packed, w_scale, w_zero, expert_offsets, out,
                    M_total, E, N, K, group_size, G, K_half,
                    BLOCK_N_=SCALAR_NBLOCK_N,
                    BLOCK_K_=SCALAR_NBLOCK_K,
                    num_warps=4,
                    num_stages=3,
                )
    elif _use_direct_gemm(x_q):
        if _use_tianshu_direct(x_q):
            w_signed = torch.empty((E, N, K), device=x_q.device, dtype=torch.int8)
            _unpack_w4_kernel[(E, triton.cdiv(N, UNPACK_BLOCK_N), triton.cdiv(K, UNPACK_BLOCK_K))](
                w_q4_packed, w_zero, w_signed,
                E, N, K, group_size, G, K_half,
                BLOCK_N_=UNPACK_BLOCK_N,
                BLOCK_K_=UNPACK_BLOCK_K,
                num_warps=4,
                num_stages=3,
            )
            _w4a8_gemm_unpacked_kernel[grid](
                x_q, x_scale, w_signed, w_scale, expert_offsets, out,
                M_total, E, N, K, group_size, G,
                BLOCK_M_=block_m,
                BLOCK_N_=block_n,
                BLOCK_K_=block_k,
                num_warps=4,
                num_stages=3,
            )
        else:
            _w4a8_gemm_direct_kernel[grid](
                x_q, x_scale, w_q4_packed, w_scale, w_zero, expert_offsets, out,
                M_total, E, N, K, group_size, G, K_half,
                BLOCK_M_=block_m,
                BLOCK_N_=block_n,
                BLOCK_K_=block_k,
                num_warps=4,
                num_stages=3,
            )
    else:
        _w4a8_gemm_direct_kernel[grid](
            x_q, x_scale, w_q4_packed, w_scale, w_zero, expert_offsets, out,
            M_total, E, N, K, group_size, G, K_half,
            BLOCK_M_=block_m,
            BLOCK_N_=block_n,
            BLOCK_K_=block_k,
            num_warps=4,
            num_stages=3,
        )
    return out
