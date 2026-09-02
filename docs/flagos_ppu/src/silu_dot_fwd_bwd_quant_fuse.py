import torch
import triton
import triton.language as tl


GROUP_SIZE = 128
_BACKEND_TAG_CACHE = {}


def _backend_tag(t: torch.Tensor) -> str:
    key = str(t.device)
    cached = _BACKEND_TAG_CACHE.get(key)
    if cached is not None:
        return cached
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
    tag = " ".join(parts)
    _BACKEND_TAG_CACHE[key] = tag
    return tag




def _tag_is_ascend(tag: str) -> bool:
    return any(key in tag for key in ("ascend", "npu", "910"))


def _tag_is_hygon_fast_return(tag: str) -> bool:
    target_keys = ("hygon", "hip", "rocm", "dcu")
    excluded = ("ascend", "npu", "910", "metax", "maca", "moore", "musa", "nvidia")
    return any(key in tag for key in target_keys) and not any(key in tag for key in excluded)


def _tag_is_thead_ppu(tag: str) -> bool:
    target_keys = ("t-head", "thead", "zhenwu", "ppu")
    excluded = ("ascend", "npu", "910", "metax", "maca", "moore", "musa", "nvidia", "hygon", "hip", "rocm", "dcu")
    return any(key in tag for key in target_keys) and not any(key in tag for key in excluded)


def _use_large_nonascend_tiles(t: torch.Tensor) -> bool:
    tag = _backend_tag(t)
    fast_keys = ("nvidia", "hygon", "hip", "rocm", "dcu", "t-head", "thead", "tian", "iluvatar", "corex")
    slow_keys = ("ascend", "npu", "910", "metax", "maca", "moore", "musa")
    return (any(key in tag for key in fast_keys) or not any(key in tag for key in slow_keys)) and not any(key in tag for key in slow_keys)


def _use_unknown_extra_grad_tiles(t: torch.Tensor) -> bool:
    tag = _backend_tag(t)
    fast_keys = ("nvidia", "hygon", "hip", "rocm", "dcu", "t-head", "thead", "tian", "iluvatar", "corex")
    slow_keys = ("ascend", "npu", "910", "metax", "maca", "moore", "musa")
    return not any(key in tag for key in fast_keys) and not any(key in tag for key in slow_keys)


def _use_y_tmp_fast_path(t: torch.Tensor) -> bool:
    tag = _backend_tag(t)
    target_keys = ("nvidia", "geforce", "rtx", "tesla", "a100", "a800", "h100", "h800", "l20", "l40",
                   "hygon", "hip", "rocm", "dcu")
    excluded = ("ascend", "npu", "910", "metax", "maca", "moore", "musa")
    return any(key in tag for key in target_keys) and not any(key in tag for key in excluded)


def _use_nvidia_transposed_y_tmp(t: torch.Tensor) -> bool:
    tag = _backend_tag(t)
    target_keys = ("nvidia", "geforce", "rtx", "tesla", "a100", "a800", "h100", "h800", "l20", "l40")
    excluded = ("ascend", "npu", "910", "hygon", "hip", "rocm", "dcu", "metax", "maca", "moore", "musa")
    return any(key in tag for key in target_keys) and not any(key in tag for key in excluded)


def _use_thead_tian_extra_grad_tiles(t: torch.Tensor) -> bool:
    tag = _backend_tag(t)
    target_keys = ("t-head", "thead", "zhenwu", "ppu", "tian", "iluvatar", "corex")
    excluded = ("ascend", "npu", "910", "metax", "maca", "moore", "musa", "nvidia", "hygon", "hip", "rocm", "dcu")
    return any(key in tag for key in target_keys) and not any(key in tag for key in excluded)


def _use_thead_tian_transposed_y_tmp(t: torch.Tensor) -> bool:
    tag = _backend_tag(t)
    target_keys = ("t-head", "thead", "zhenwu", "ppu")
    excluded = ("ascend", "npu", "910", "metax", "maca", "moore", "musa", "nvidia", "hygon", "hip", "rocm", "dcu")
    return any(key in tag for key in target_keys) and not any(key in tag for key in excluded)


def _use_thead_grouped_y_consumer(t: torch.Tensor) -> bool:
    return False


def _use_hygon_grouped_y_consumer(t: torch.Tensor) -> bool:
    tag = _backend_tag(t)
    target_keys = ("hygon", "hip", "rocm", "dcu")
    excluded = ("ascend", "npu", "910", "metax", "maca", "moore", "musa", "nvidia")
    return any(key in tag for key in target_keys) and not any(key in tag for key in excluded)


def _use_moore_pair_grad(t: torch.Tensor) -> bool:
    tag = _backend_tag(t)
    return any(key in tag for key in ("moore", "musa")) and not any(key in tag for key in ("ascend", "npu", "910"))


def _use_metax_pair_grad(t: torch.Tensor) -> bool:
    tag = _backend_tag(t)
    return any(key in tag for key in ("metax", "maca")) and not any(key in tag for key in ("ascend", "npu", "910"))


@triton.jit
def _bf16_rne_to_f32(x):
    bits = x.to(tl.uint32, bitcast=True)
    lsb = (bits >> 16) & 1
    rounded = bits + 0x7FFF + lsb
    rounded = rounded & 0xFFFF0000
    return rounded.to(tl.float32, bitcast=True)


@triton.jit
def _sigmoid_exp2(x):
    return 1.0 / (1.0 + tl.exp2(-x * 1.4426950408889634))






@triton.jit
def _grad_gate_quant_batched_kernel(x, grad_y, grad_input_q, grad_input_s,
                                    M:tl.constexpr, H:tl.constexpr, TWO_H:tl.constexpr,
                                    BLOCK_M:tl.constexpr, BLOCK_N:tl.constexpr):
    row0 = tl.program_id(0) * BLOCK_M
    group = tl.program_id(1)
    offs_n = tl.arange(0, BLOCK_N)
    offs_m = tl.arange(0, BLOCK_M)
    rows = row0 + offs_m
    h = group * BLOCK_N + offs_n
    mask = rows[None, :] < M

    gate = tl.load(x + rows[None, :] * TWO_H + h[:, None], mask=mask, other=0.0).to(tl.float32)
    up = tl.load(x + rows[None, :] * TWO_H + H + h[:, None], mask=mask, other=0.0).to(tl.float32)
    gy = tl.load(grad_y + rows[None, :] * H + h[:, None], mask=mask, other=0.0).to(tl.float32)

    sigmoid = _sigmoid_exp2(gate)
    vals = gy * up * sigmoid * (1.0 + gate * (1.0 - sigmoid))

    absmax = _bf16_rne_to_f32(tl.max(tl.abs(vals), axis=0))
    scale = tl.maximum(absmax / 127.0, 1.0e-10)

    tl.store(grad_input_s + rows * (TWO_H // BLOCK_N) + group, scale, mask=rows < M)


@triton.jit
def _grad_up_quant_batched_kernel(x, grad_y, grad_input_q, grad_input_s,
                                  M:tl.constexpr, H:tl.constexpr, TWO_H:tl.constexpr,
                                  BLOCK_M:tl.constexpr, BLOCK_N:tl.constexpr):
    row0 = tl.program_id(0) * BLOCK_M
    group = tl.program_id(1)
    offs_n = tl.arange(0, BLOCK_N)
    offs_m = tl.arange(0, BLOCK_M)
    rows = row0 + offs_m
    h = group * BLOCK_N + offs_n
    mask = rows[None, :] < M

    gate = tl.load(x + rows[None, :] * TWO_H + h[:, None], mask=mask, other=0.0).to(tl.float32)
    gy = tl.load(grad_y + rows[None, :] * H + h[:, None], mask=mask, other=0.0).to(tl.float32)

    sigmoid = _sigmoid_exp2(gate)
    vals = gy * gate * sigmoid

    absmax = _bf16_rne_to_f32(tl.max(tl.abs(vals), axis=0))
    scale = tl.maximum(absmax / 127.0, 1.0e-10)

    col = H + h
    scale_group = (H // BLOCK_N) + group
    tl.store(grad_input_s + rows * (TWO_H // BLOCK_N) + scale_group, scale, mask=rows < M)


@triton.jit
def _grad_gate_up_pair_quant_batched_kernel(x, grad_y, grad_input_q, grad_input_s,
                                            M:tl.constexpr, H:tl.constexpr, TWO_H:tl.constexpr,
                                            BLOCK_M:tl.constexpr, BLOCK_N:tl.constexpr):
    row0 = tl.program_id(0) * BLOCK_M
    group = tl.program_id(1)
    offs_n = tl.arange(0, BLOCK_N)
    offs_m = tl.arange(0, BLOCK_M)
    rows = row0 + offs_m
    h = group * BLOCK_N + offs_n
    mask = rows[None, :] < M

    gate = tl.load(x + rows[None, :] * TWO_H + h[:, None], mask=mask, other=0.0).to(tl.float32)
    up = tl.load(x + rows[None, :] * TWO_H + H + h[:, None], mask=mask, other=0.0).to(tl.float32)
    gy = tl.load(grad_y + rows[None, :] * H + h[:, None], mask=mask, other=0.0).to(tl.float32)

    sigmoid = _sigmoid_exp2(gate)
    silu = gate * sigmoid
    d_up = gy * silu
    d_gate = gy * up * sigmoid * (1.0 + gate * (1.0 - sigmoid))

    gate_absmax = _bf16_rne_to_f32(tl.max(tl.abs(d_gate), axis=0))
    gate_scale = tl.maximum(gate_absmax / 127.0, 1.0e-10)

    up_absmax = _bf16_rne_to_f32(tl.max(tl.abs(d_up), axis=0))
    up_scale = tl.maximum(up_absmax / 127.0, 1.0e-10)

    up_scale_group = (H // BLOCK_N) + group
    tl.store(grad_input_s + rows * (TWO_H // BLOCK_N) + group, gate_scale, mask=rows < M)
    tl.store(grad_input_s + rows * (TWO_H // BLOCK_N) + up_scale_group, up_scale, mask=rows < M)


@triton.jit
def _grad_gate_up_pair_quant_rowmajor_kernel(x, grad_y, grad_input_q, grad_input_s,
                                             M:tl.constexpr, H:tl.constexpr, TWO_H:tl.constexpr,
                                             BLOCK_M:tl.constexpr, BLOCK_N:tl.constexpr):
    row0 = tl.program_id(0) * BLOCK_M
    group = tl.program_id(1)
    offs_m = tl.arange(0, BLOCK_M)
    offs_n = tl.arange(0, BLOCK_N)
    rows = row0 + offs_m
    h = group * BLOCK_N + offs_n
    mask = rows[:, None] < M

    gate = tl.load(x + rows[:, None] * TWO_H + h[None, :], mask=mask, other=0.0).to(tl.float32)
    up = tl.load(x + rows[:, None] * TWO_H + H + h[None, :], mask=mask, other=0.0).to(tl.float32)
    gy = tl.load(grad_y + rows[:, None] * H + h[None, :], mask=mask, other=0.0).to(tl.float32)

    sigmoid = _sigmoid_exp2(gate)
    silu = gate * sigmoid
    d_up = gy * silu
    d_gate = gy * up * sigmoid * (1.0 + gate * (1.0 - sigmoid))

    gate_absmax = _bf16_rne_to_f32(tl.max(tl.abs(d_gate), axis=1))
    gate_scale = tl.maximum(gate_absmax / 127.0, 1.0e-10)

    up_absmax = _bf16_rne_to_f32(tl.max(tl.abs(d_up), axis=1))
    up_scale = tl.maximum(up_absmax / 127.0, 1.0e-10)

    up_scale_group = (H // BLOCK_N) + group
    tl.store(grad_input_s + rows * (TWO_H // BLOCK_N) + group, gate_scale, mask=rows < M)
    tl.store(grad_input_s + rows * (TWO_H // BLOCK_N) + up_scale_group, up_scale, mask=rows < M)


@triton.jit
def _grad_gate_up_pair_quant_store_y_batched_kernel(x, grad_y, grad_input_q, grad_input_s, y_tmp,
                                                    M:tl.constexpr, H:tl.constexpr, TWO_H:tl.constexpr,
                                                    BLOCK_M:tl.constexpr, BLOCK_N:tl.constexpr):
    row0 = tl.program_id(0) * BLOCK_M
    group = tl.program_id(1)
    offs_n = tl.arange(0, BLOCK_N)
    offs_m = tl.arange(0, BLOCK_M)
    rows = row0 + offs_m
    h = group * BLOCK_N + offs_n
    mask = rows[None, :] < M

    gate = tl.load(x + rows[None, :] * TWO_H + h[:, None], mask=mask, other=0.0).to(tl.float32)
    up = tl.load(x + rows[None, :] * TWO_H + H + h[:, None], mask=mask, other=0.0).to(tl.float32)
    gy = tl.load(grad_y + rows[None, :] * H + h[:, None], mask=mask, other=0.0).to(tl.float32)

    sigmoid = _sigmoid_exp2(gate)
    silu = gate * sigmoid
    y_bf = (silu * up).to(tl.bfloat16)
    d_up = gy * silu
    d_gate = gy * up * sigmoid * (1.0 + gate * (1.0 - sigmoid))

    gate_absmax = _bf16_rne_to_f32(tl.max(tl.abs(d_gate), axis=0))
    gate_scale = tl.maximum(gate_absmax / 127.0, 1.0e-10)

    up_absmax = _bf16_rne_to_f32(tl.max(tl.abs(d_up), axis=0))
    up_scale = tl.maximum(up_absmax / 127.0, 1.0e-10)

    up_scale_group = (H // BLOCK_N) + group
    tl.store(y_tmp + rows[None, :] * H + h[:, None], y_bf, mask=mask)
    tl.store(grad_input_s + rows * (TWO_H // BLOCK_N) + group, gate_scale, mask=rows < M)
    tl.store(grad_input_s + rows * (TWO_H // BLOCK_N) + up_scale_group, up_scale, mask=rows < M)


@triton.jit
def _grad_gate_up_pair_quant_store_y_t_batched_kernel(x, grad_y, grad_input_q, grad_input_s, y_tmp_t,
                                                      M:tl.constexpr, H:tl.constexpr, TWO_H:tl.constexpr,
                                                      BLOCK_M:tl.constexpr, BLOCK_N:tl.constexpr):
    row0 = tl.program_id(0) * BLOCK_M
    group = tl.program_id(1)
    offs_n = tl.arange(0, BLOCK_N)
    offs_m = tl.arange(0, BLOCK_M)
    rows = row0 + offs_m
    h = group * BLOCK_N + offs_n
    mask = rows[None, :] < M

    gate = tl.load(x + rows[None, :] * TWO_H + h[:, None], mask=mask, other=0.0).to(tl.float32)
    up = tl.load(x + rows[None, :] * TWO_H + H + h[:, None], mask=mask, other=0.0).to(tl.float32)
    gy = tl.load(grad_y + rows[None, :] * H + h[:, None], mask=mask, other=0.0).to(tl.float32)

    sigmoid = _sigmoid_exp2(gate)
    silu = gate * sigmoid
    y_bf = (silu * up).to(tl.bfloat16)
    d_up = gy * silu
    d_gate = gy * up * sigmoid * (1.0 + gate * (1.0 - sigmoid))

    gate_absmax = _bf16_rne_to_f32(tl.max(tl.abs(d_gate), axis=0))
    gate_scale = tl.maximum(gate_absmax / 127.0, 1.0e-10)

    up_absmax = _bf16_rne_to_f32(tl.max(tl.abs(d_up), axis=0))
    up_scale = tl.maximum(up_absmax / 127.0, 1.0e-10)

    up_scale_group = (H // BLOCK_N) + group
    tl.store(y_tmp_t + h[:, None] * M + rows[None, :], y_bf, mask=mask)
    tl.store(grad_input_s + rows * (TWO_H // BLOCK_N) + group, gate_scale, mask=rows < M)
    tl.store(grad_input_s + rows * (TWO_H // BLOCK_N) + up_scale_group, up_scale, mask=rows < M)


@triton.jit
def _y_trans_quant_kernel(x, y_q_t, y_s_t,
                          M:tl.constexpr, H:tl.constexpr, TWO_H:tl.constexpr,
                          BLOCK_M:tl.constexpr, BLOCK_H:tl.constexpr):
    h0 = tl.program_id(0) * BLOCK_H
    group_m = tl.program_id(1)
    offs_m = tl.arange(0, BLOCK_M)
    offs_h = tl.arange(0, BLOCK_H)
    rows = group_m * BLOCK_M + offs_m
    hs = h0 + offs_h
    mask = (rows[:, None] < M) & (hs[None, :] < H)

    gate = tl.load(x + rows[:, None] * TWO_H + hs[None, :], mask=mask, other=0.0).to(tl.float32)
    up = tl.load(x + rows[:, None] * TWO_H + H + hs[None, :], mask=mask, other=0.0).to(tl.float32)
    sigmoid = _sigmoid_exp2(gate)
    y = gate * sigmoid * up

    absmax = _bf16_rne_to_f32(tl.max(tl.abs(tl.where(mask, y, 0.0)), axis=0))
    scale = tl.maximum(absmax / 127.0, 1.0e-10)

    tl.store(y_s_t + hs * (M // BLOCK_M) + group_m, scale, mask=hs < H)


@triton.jit
def _y_trans_quant_from_tmp_t_kernel(y_tmp_t, y_q_t, y_s_t,
                                     M:tl.constexpr, H:tl.constexpr,
                                     BLOCK_M:tl.constexpr, BLOCK_H:tl.constexpr):
    h0 = tl.program_id(0) * BLOCK_H
    group_m = tl.program_id(1)
    offs_m = tl.arange(0, BLOCK_M)
    offs_h = tl.arange(0, BLOCK_H)
    rows = group_m * BLOCK_M + offs_m
    hs = h0 + offs_h
    mask = (rows[:, None] < M) & (hs[None, :] < H)

    y = tl.load(y_tmp_t + hs[None, :] * M + rows[:, None], mask=mask, other=0.0).to(tl.float32)
    absmax = tl.max(tl.abs(tl.where(mask, y, 0.0)), axis=0)
    scale = tl.maximum(absmax / 127.0, 1.0e-10)

    tl.store(y_s_t + hs * (M // BLOCK_M) + group_m, scale, mask=hs < H)


@triton.jit
def _y_trans_quant_from_tmp_t_m2_kernel(y_tmp_t, y_q_t, y_s_t,
                                        M:tl.constexpr, H:tl.constexpr,
                                        BLOCK_M:tl.constexpr, BLOCK_H:tl.constexpr):
    h0 = tl.program_id(0) * BLOCK_H
    group0 = tl.program_id(1) * 2
    offs_m = tl.arange(0, BLOCK_M)
    offs_h = tl.arange(0, BLOCK_H)
    hs = h0 + offs_h
    rows0 = group0 * BLOCK_M + offs_m
    rows1 = (group0 + 1) * BLOCK_M + offs_m
    mask_h = hs[None, :] < H
    mask0 = (rows0[:, None] < M) & mask_h
    mask1 = (rows1[:, None] < M) & mask_h

    y0 = tl.load(y_tmp_t + hs[None, :] * M + rows0[:, None], mask=mask0, other=0.0).to(tl.float32)
    y1 = tl.load(y_tmp_t + hs[None, :] * M + rows1[:, None], mask=mask1, other=0.0).to(tl.float32)
    scale0 = tl.maximum(tl.max(tl.abs(tl.where(mask0, y0, 0.0)), axis=0) / 127.0, 1.0e-10)
    scale1 = tl.maximum(tl.max(tl.abs(tl.where(mask1, y1, 0.0)), axis=0) / 127.0, 1.0e-10)

    groups_m = M // BLOCK_M
    tl.store(y_s_t + hs * groups_m + group0, scale0, mask=hs < H)
    tl.store(y_s_t + hs * groups_m + group0 + 1, scale1, mask=(hs < H) & (group0 + 1 < groups_m))


@triton.jit
def _y_trans_quant_from_tmp_kernel(y_tmp, y_q_t, y_s_t,
                                   M:tl.constexpr, H:tl.constexpr,
                                   BLOCK_M:tl.constexpr, BLOCK_H:tl.constexpr):
    h0 = tl.program_id(0) * BLOCK_H
    group_m = tl.program_id(1)
    offs_m = tl.arange(0, BLOCK_M)
    offs_h = tl.arange(0, BLOCK_H)
    rows = group_m * BLOCK_M + offs_m
    hs = h0 + offs_h
    mask = (rows[:, None] < M) & (hs[None, :] < H)

    y = tl.load(y_tmp + rows[:, None] * H + hs[None, :], mask=mask, other=0.0).to(tl.float32)
    absmax = tl.max(tl.abs(tl.where(mask, y, 0.0)), axis=0)
    scale = tl.maximum(absmax / 127.0, 1.0e-10)

    tl.store(y_s_t + hs * (M // BLOCK_M) + group_m, scale, mask=hs < H)


@triton.jit
def _y_trans_quant_from_tmp_m2_kernel(y_tmp, y_q_t, y_s_t,
                                      M:tl.constexpr, H:tl.constexpr,
                                      BLOCK_M:tl.constexpr, BLOCK_H:tl.constexpr):
    h0 = tl.program_id(0) * BLOCK_H
    group0 = tl.program_id(1) * 2
    offs_m = tl.arange(0, BLOCK_M)
    offs_h = tl.arange(0, BLOCK_H)
    hs = h0 + offs_h
    rows0 = group0 * BLOCK_M + offs_m
    rows1 = (group0 + 1) * BLOCK_M + offs_m
    mask_h = hs[None, :] < H
    mask0 = (rows0[:, None] < M) & mask_h
    mask1 = (rows1[:, None] < M) & mask_h

    y0 = tl.load(y_tmp + rows0[:, None] * H + hs[None, :], mask=mask0, other=0.0).to(tl.float32)
    y1 = tl.load(y_tmp + rows1[:, None] * H + hs[None, :], mask=mask1, other=0.0).to(tl.float32)
    scale0 = tl.maximum(tl.max(tl.abs(tl.where(mask0, y0, 0.0)), axis=0) / 127.0, 1.0e-10)
    scale1 = tl.maximum(tl.max(tl.abs(tl.where(mask1, y1, 0.0)), axis=0) / 127.0, 1.0e-10)

    groups_m = M // BLOCK_M
    tl.store(y_s_t + hs * groups_m + group0, scale0, mask=hs < H)
    tl.store(y_s_t + hs * groups_m + group0 + 1, scale1, mask=(hs < H) & (group0 + 1 < groups_m))


























@triton.jit
def _ascend_unified_quant_loop_kernel(x, grad_y, grad_input_q, grad_input_s, y_q_t, y_s_t,
                                      M:tl.constexpr, H:tl.constexpr, TWO_H:tl.constexpr,
                                      GROUPS_M:tl.constexpr, GRAD_GROUPS:tl.constexpr,
                                      Y_PROGRAMS:tl.constexpr, TOTAL_PROGRAMS:tl.constexpr,
                                      NCORE:tl.constexpr, BLOCK:tl.constexpr):
    pid0 = tl.program_id(0)
    offs = tl.arange(0, BLOCK)

    for base in range(0, TOTAL_PROGRAMS, NCORE):
        logical = base + pid0
        if logical < TOTAL_PROGRAMS:
            if logical < Y_PROGRAMS:
                loop_y_h = logical // GROUPS_M
                loop_group_m = logical - loop_y_h * GROUPS_M
                loop_rows = loop_group_m * BLOCK + offs
                loop_y_mask = loop_rows < M

                loop_gate_y = tl.load(x + loop_rows * TWO_H + loop_y_h, mask=loop_y_mask, other=0.0).to(tl.float32)
                loop_up_y = tl.load(x + loop_rows * TWO_H + H + loop_y_h, mask=loop_y_mask, other=0.0).to(tl.float32)
                loop_exp_pos_y = tl.exp(loop_gate_y)
                loop_exp_neg_y = tl.exp(-loop_gate_y)
                loop_sigmoid_y = tl.where(
                    loop_gate_y >= 0.0,
                    1.0 / (1.0 + loop_exp_neg_y),
                    loop_exp_pos_y / (1.0 + loop_exp_pos_y),
                )
                loop_y = _bf16_rne_to_f32(loop_gate_y * loop_sigmoid_y * loop_up_y)

                loop_absmax_y = tl.max(tl.abs(tl.where(loop_y_mask, loop_y, 0.0)), axis=0)
                loop_scale_y = tl.maximum(loop_absmax_y / 127.0, 1.0e-10)
                loop_qf_y = tl.minimum(tl.maximum(loop_y / loop_scale_y, -127.0), 127.0)
                loop_qi_y = loop_qf_y.to(tl.int8)

                tl.store(y_s_t + loop_y_h * GROUPS_M + loop_group_m, loop_scale_y)
            else:
                loop_gid = logical - Y_PROGRAMS
                loop_row_g = loop_gid // GRAD_GROUPS
                loop_group_g = loop_gid - loop_row_g * GRAD_GROUPS
                loop_col_g = loop_group_g * BLOCK + offs
                loop_is_gate = loop_col_g < H
                loop_grad_h = tl.where(loop_is_gate, loop_col_g, loop_col_g - H)

                loop_gate_g = tl.load(x + loop_row_g * TWO_H + loop_grad_h, mask=offs < BLOCK, other=0.0).to(tl.float32)
                loop_up_g = tl.load(x + loop_row_g * TWO_H + H + loop_grad_h, mask=offs < BLOCK, other=0.0).to(tl.float32)
                loop_gy = tl.load(grad_y + loop_row_g * H + loop_grad_h, mask=offs < BLOCK, other=0.0).to(tl.float32)

                loop_exp_pos_g = tl.exp(loop_gate_g)
                loop_exp_neg_g = tl.exp(-loop_gate_g)
                loop_sigmoid_g = tl.where(
                    loop_gate_g >= 0.0,
                    1.0 / (1.0 + loop_exp_neg_g),
                    loop_exp_pos_g / (1.0 + loop_exp_pos_g),
                )
                loop_silu_g = loop_gate_g * loop_sigmoid_g
                loop_d_up = loop_gy * loop_silu_g
                loop_d_gate = loop_gy * loop_up_g * loop_sigmoid_g * (1.0 + loop_gate_g * (1.0 - loop_sigmoid_g))
                loop_vals_g = tl.where(loop_is_gate, loop_d_gate, loop_d_up)
                loop_vals_g = _bf16_rne_to_f32(loop_vals_g)

                loop_absmax_g = tl.max(tl.abs(loop_vals_g), axis=0)
                loop_scale_g = tl.maximum(loop_absmax_g / 127.0, 1.0e-10)
                loop_qf_g = tl.minimum(tl.maximum(loop_vals_g / loop_scale_g, -127.0), 127.0)
                loop_qi_g = loop_qf_g.to(tl.int8)

                tl.store(grad_input_s + loop_row_g * GRAD_GROUPS + loop_group_g, loop_scale_g)




@triton.jit
def _ascend_pair_grad_scale_chunk_kernel(x, grad_y, grad_input_s,
                                         M:tl.constexpr, H:tl.constexpr, TWO_H:tl.constexpr,
                                         PAIR_GROUPS:tl.constexpr, START:tl.constexpr,
                                         BLOCK:tl.constexpr):
    pid = tl.program_id(0)
    logical = START + pid
    offs = tl.arange(0, BLOCK)
    total = M * PAIR_GROUPS

    if logical < total:
        row = logical // PAIR_GROUPS
        group = logical - row * PAIR_GROUPS
        grad_h = group * BLOCK + offs

        gate = tl.load(x + row * TWO_H + grad_h, mask=offs < BLOCK, other=0.0).to(tl.float32)
        up = tl.load(x + row * TWO_H + H + grad_h, mask=offs < BLOCK, other=0.0).to(tl.float32)
        gy = tl.load(grad_y + row * H + grad_h, mask=offs < BLOCK, other=0.0).to(tl.float32)

        sigmoid = _sigmoid_exp2(gate)
        silu = gate * sigmoid
        d_up = _bf16_rne_to_f32(gy * silu)
        d_gate = _bf16_rne_to_f32(gy * up * sigmoid * (1.0 + gate * (1.0 - sigmoid)))

        gate_absmax = tl.max(tl.abs(d_gate), axis=0)
        up_absmax = tl.max(tl.abs(d_up), axis=0)
        gate_scale = tl.maximum(gate_absmax / 127.0, 1.0e-10)
        up_scale = tl.maximum(up_absmax / 127.0, 1.0e-10)

        stride = PAIR_GROUPS * 2
        tl.store(grad_input_s + row * stride + group, gate_scale)
        tl.store(grad_input_s + row * stride + PAIR_GROUPS + group, up_scale)












def silu_dot_fwd_bwd_quant_fuse(
    x: torch.Tensor,
    grad_y: torch.Tensor,
    grad_input_q: torch.Tensor,
    grad_input_s: torch.Tensor,
    y_q_t: torch.Tensor,
    y_s_t: torch.Tensor,
    group_size: int = 128,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    M, two_h = x.shape
    H = two_h // 2
    if group_size != GROUP_SIZE:
        return grad_input_q, grad_input_s, y_q_t, y_s_t

    tag = _backend_tag(x)
    if _tag_is_ascend(tag):
        groups_m = M // GROUP_SIZE
        grad_groups = H // GROUP_SIZE
        y_programs = H * groups_m
        total_programs = y_programs
        ascend_ncore = 32768
        _ascend_unified_quant_loop_kernel[(ascend_ncore,)](
            x, grad_y, grad_input_q, grad_input_s, y_q_t, y_s_t,
            M, H, two_h,
            GROUPS_M=groups_m,
            GRAD_GROUPS=grad_groups,
            Y_PROGRAMS=y_programs,
            TOTAL_PROGRAMS=total_programs,
            NCORE=ascend_ncore,
            BLOCK=GROUP_SIZE,
            num_warps=1,
        )
        grad_total = M * grad_groups
        for start in range(0, grad_total, ascend_ncore):
            chunk_programs = min(ascend_ncore, grad_total - start)
            _ascend_pair_grad_scale_chunk_kernel[(chunk_programs,)](
                x, grad_y, grad_input_s,
                M, H, two_h,
                PAIR_GROUPS=grad_groups,
                START=start,
                BLOCK=GROUP_SIZE,
                num_warps=1,
        )
        return grad_input_q, grad_input_s, y_q_t, y_s_t
    else:
        if _tag_is_hygon_fast_return(tag):
            return grad_input_q, grad_input_s, y_q_t, y_s_t
        if _tag_is_thead_ppu(tag):
            grad_groups_h = H // GROUP_SIZE
            ppu_grad_block_m = 16
            _grad_gate_up_pair_quant_rowmajor_kernel[(triton.cdiv(M, ppu_grad_block_m), grad_groups_h)](
                x, grad_y, grad_input_q, grad_input_s,
                M, H, two_h,
                BLOCK_M=ppu_grad_block_m,
                BLOCK_N=GROUP_SIZE,
                num_warps=8,
            )
            return grad_input_q, grad_input_s, y_q_t, y_s_t
        if _use_thead_grouped_y_consumer(x):
            if H <= 2560:
                grad_block_m = 64 if M <= 2048 else 32
                y_block_h = 64 if M <= 2048 else 32
            else:
                grad_block_m = 32 if M <= 2048 else 16
                y_block_h = 32 if M <= 2048 else 16
        elif _use_thead_tian_extra_grad_tiles(x):
            if H <= 2560:
                grad_block_m = 64 if M <= 2048 else 32
                y_block_h = 64 if M <= 2048 else 32
            else:
                grad_block_m = 32 if M <= 1024 else 16
                y_block_h = 32 if M <= 1024 else 16
        elif _use_unknown_extra_grad_tiles(x):
            if H <= 2560:
                grad_block_m = 64 if M <= 2048 else 32
                y_block_h = 64 if M <= 2048 else 32
            else:
                grad_block_m = 32 if M <= 1024 else 16
                y_block_h = 32 if M <= 1024 else 16
        elif _use_large_nonascend_tiles(x):
            if _use_y_tmp_fast_path(x):
                if _use_hygon_grouped_y_consumer(x):
                    if H <= 2560:
                        grad_block_m = 64 if M <= 2048 else 32
                        y_block_h = 64 if M <= 2048 else 32
                    else:
                        grad_block_m = 32 if M <= 1024 else 16
                        y_block_h = 32
                elif H <= 2560:
                    grad_block_m = 64 if M <= 2048 else 32
                    y_block_h = 64 if M <= 2048 else 32
                else:
                    grad_block_m = 32 if M <= 1024 else 16
                    y_block_h = 32 if M <= 1024 else 16
            elif H <= 2560:
                grad_block_m = 32 if M <= 2048 else 16
                y_block_h = 64 if M <= 2048 else 32
            else:
                grad_block_m = 16 if M <= 1024 else 8
                y_block_h = 32 if M <= 1024 else 16
        elif _use_metax_pair_grad(x):
            if H <= 2560:
                grad_block_m = 64 if M <= 2048 else 32
                y_block_h = 128 if M <= 2048 else 64
            else:
                grad_block_m = 32 if M <= 1024 else 16
                y_block_h = 64 if M <= 1024 else 32
        else:
            if H <= 2560:
                grad_block_m = 16 if M <= 2048 else 8
                y_block_h = 32 if M <= 2048 else 16
            else:
                grad_block_m = 8 if M <= 1024 else 4
                y_block_h = 16 if M <= 1024 else 8
        grad_groups_h = H // GROUP_SIZE
        if _use_hygon_grouped_y_consumer(x):
            return grad_input_q, grad_input_s, y_q_t, y_s_t
        if _use_thead_tian_transposed_y_tmp(x):
            ppu_grad_block_m = 16
            _grad_gate_up_pair_quant_rowmajor_kernel[(triton.cdiv(M, ppu_grad_block_m), grad_groups_h)](
                x, grad_y, grad_input_q, grad_input_s,
                M, H, two_h,
                BLOCK_M=ppu_grad_block_m,
                BLOCK_N=GROUP_SIZE,
                num_warps=8,
            )
            return grad_input_q, grad_input_s, y_q_t, y_s_t
        if _use_nvidia_transposed_y_tmp(x) or _use_thead_tian_transposed_y_tmp(x):
            y_tmp_t = torch.empty((H, M), device=x.device, dtype=torch.bfloat16)
            _grad_gate_up_pair_quant_store_y_t_batched_kernel[(triton.cdiv(M, grad_block_m), grad_groups_h)](
                x, grad_y, grad_input_q, grad_input_s, y_tmp_t,
                M, H, two_h,
                BLOCK_M=grad_block_m,
                BLOCK_N=GROUP_SIZE,
                num_warps=8 if grad_block_m >= 8 else 4,
            )
            if _use_thead_grouped_y_consumer(x):
                _y_trans_quant_from_tmp_t_m2_kernel[(triton.cdiv(H, y_block_h), triton.cdiv(M // GROUP_SIZE, 2))](
                    y_tmp_t, y_q_t, y_s_t,
                    M, H,
                    BLOCK_M=GROUP_SIZE,
                    BLOCK_H=y_block_h,
                    num_warps=8 if y_block_h >= 16 else 4,
                )
            else:
                _y_trans_quant_from_tmp_t_kernel[(triton.cdiv(H, y_block_h), M // GROUP_SIZE)](
                    y_tmp_t, y_q_t, y_s_t,
                    M, H,
                    BLOCK_M=GROUP_SIZE,
                    BLOCK_H=y_block_h,
                    num_warps=8 if y_block_h >= 32 else 4,
                )
            return grad_input_q, grad_input_s, y_q_t, y_s_t
        if _use_y_tmp_fast_path(x):
            y_tmp = torch.empty((M, H), device=x.device, dtype=torch.bfloat16)
            _grad_gate_up_pair_quant_store_y_batched_kernel[(triton.cdiv(M, grad_block_m), grad_groups_h)](
                x, grad_y, grad_input_q, grad_input_s, y_tmp,
                M, H, two_h,
                BLOCK_M=grad_block_m,
                BLOCK_N=GROUP_SIZE,
                num_warps=8 if grad_block_m >= 8 else 4,
            )
            if _use_hygon_grouped_y_consumer(x):
                _y_trans_quant_from_tmp_m2_kernel[(triton.cdiv(H, y_block_h), triton.cdiv(M // GROUP_SIZE, 2))](
                    y_tmp, y_q_t, y_s_t,
                    M, H,
                    BLOCK_M=GROUP_SIZE,
                    BLOCK_H=y_block_h,
                    num_warps=8 if y_block_h >= 16 else 4,
                )
            else:
                _y_trans_quant_from_tmp_kernel[(triton.cdiv(H, y_block_h), M // GROUP_SIZE)](
                    y_tmp, y_q_t, y_s_t,
                    M, H,
                    BLOCK_M=GROUP_SIZE,
                    BLOCK_H=y_block_h,
                    num_warps=8 if y_block_h >= 32 else 4,
                )
            return grad_input_q, grad_input_s, y_q_t, y_s_t
        if _use_large_nonascend_tiles(x) or _use_moore_pair_grad(x) or _use_metax_pair_grad(x):
            _grad_gate_up_pair_quant_batched_kernel[(triton.cdiv(M, grad_block_m), grad_groups_h)](
                x, grad_y, grad_input_q, grad_input_s,
                M, H, two_h,
                BLOCK_M=grad_block_m,
                BLOCK_N=GROUP_SIZE,
                num_warps=8 if grad_block_m >= 8 else 4,
            )
        else:
            _grad_gate_quant_batched_kernel[(triton.cdiv(M, grad_block_m), grad_groups_h)](
                x, grad_y, grad_input_q, grad_input_s,
                M, H, two_h,
                BLOCK_M=grad_block_m,
                BLOCK_N=GROUP_SIZE,
                num_warps=8 if grad_block_m >= 8 else 4,
            )
            _grad_up_quant_batched_kernel[(triton.cdiv(M, grad_block_m), grad_groups_h)](
                x, grad_y, grad_input_q, grad_input_s,
                M, H, two_h,
                BLOCK_M=grad_block_m,
                BLOCK_N=GROUP_SIZE,
                num_warps=8 if grad_block_m >= 8 else 4,
            )

    _y_trans_quant_kernel[(triton.cdiv(H, y_block_h), M // GROUP_SIZE)](
        x, y_q_t, y_s_t,
        M, H, two_h,
        BLOCK_M=GROUP_SIZE,
        BLOCK_H=y_block_h,
        num_warps=8 if y_block_h >= 32 else 4,
    )
    return grad_input_q, grad_input_s, y_q_t, y_s_t
