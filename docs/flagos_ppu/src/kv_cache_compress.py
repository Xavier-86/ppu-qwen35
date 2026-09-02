import torch
import triton
import triton.language as tl


HEAD_DIM = 512
ROPE_HEAD_DIM = 64
NOPE_HEAD_DIM = 448
KV_BLOCK_SIZE = 64
TOKEN_STRIDE = 576
SCALE_DIM = 8
BLOCK_D_C128_LARGE = 32
BLOCK_D_C128_SMALL = 64
BLOCK_D_C256_LARGE = 16
BLOCK_D_C256_SMALL = 32
BLOCK_D_C512_LARGE = 8
BLOCK_D_C512_SMALL = 16


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
    return " ".join(parts)


def _is_ascend(t: torch.Tensor) -> bool:
    tag = _backend_tag(t)
    return any(key in tag for key in ("ascend", "npu", "910"))


def _is_metax(t: torch.Tensor) -> bool:
    tag = _backend_tag(t)
    return any(key in tag for key in ("metax", "maca"))


def _is_thead(t: torch.Tensor) -> bool:
    tag = _backend_tag(t)
    return any(key in tag for key in ("t-head", "thead"))


def _is_nvidia_target(t: torch.Tensor) -> bool:
    tag = _backend_tag(t)
    return any(key in tag for key in ("nvidia", "geforce", "rtx", "tesla", "a100", "a800", "h100", "h800", "v100", "l40"))


def _use_contiguous_block_fast_path(t: torch.Tensor) -> bool:
    tag = _backend_tag(t)
    target_keys = ("nvidia", "geforce", "rtx", "tesla", "a100", "a800", "h100", "h800", "v100", "l40", "hygon", "dcu", "rocm", "hip", "tianshu", "tian", "iluvatar", "corex")
    avoid_keys = ("ascend", "npu", "910", "metax", "maca", "moore", "musa", "t-head", "thead")
    return any(key in tag for key in target_keys) and not any(key in tag for key in avoid_keys)


def _use_global_flat_fast_path(t: torch.Tensor) -> bool:
    tag = _backend_tag(t)
    target_keys = ("nvidia", "geforce", "rtx", "tesla", "a100", "a800", "h100", "h800", "v100", "l40", "hygon", "dcu", "rocm", "hip", "tianshu", "tian", "iluvatar", "corex")
    avoid_keys = ("ascend", "npu", "910", "metax", "maca", "moore", "musa", "t-head", "thead")
    return any(key in tag for key in target_keys) and not any(key in tag for key in avoid_keys)


def _use_wide_compress_tiles(t: torch.Tensor) -> bool:
    tag = _backend_tag(t)
    benefit_keys = ("t-head", "thead", "tian", "iluvatar", "corex", "moore", "musa")
    avoid_keys = ("ascend", "npu", "910", "metax", "maca")
    return any(key in tag for key in benefit_keys) and not any(key in tag for key in avoid_keys)


@triton.jit
def _bf16_rne_to_f32(x):
    bits = x.to(tl.uint32, bitcast=True)
    lsb = (bits >> 16) & 1
    rounded = bits + 0x7FFF + lsb
    rounded = rounded & 0xFFFF0000
    return rounded.to(tl.float32, bitcast=True)




@triton.jit
def _compress_kernel(state_cache, token_to_req, positions, boundary_token_indices, block_table,
                     tmp,
                     num_outputs:tl.constexpr, block_size:tl.constexpr, compress_ratio:tl.constexpr,
                     HEAD_DIM_:tl.constexpr,
                     blocks_per_req:tl.constexpr, BLOCK_R:tl.constexpr, BLOCK_D_:tl.constexpr):
    out_id = tl.program_id(0)
    d0 = tl.program_id(1) * BLOCK_D_
    ds = d0 + tl.arange(0, BLOCK_D_)
    rs = tl.arange(0, BLOCK_R)

    boundary_idx = tl.load(boundary_token_indices + out_id)
    boundary_pos = tl.load(positions + boundary_idx).to(tl.int64)
    req = tl.load(token_to_req + boundary_idx).to(tl.int32)
    pos = boundary_pos - compress_ratio + 1 + rs
    block_idx = (pos // block_size).to(tl.int32)
    block_off = (pos % block_size).to(tl.int32)
    block_num = tl.load(block_table + req * blocks_per_req + block_idx, mask=rs < compress_ratio, other=0).to(tl.int32)
    flat = block_num * block_size + block_off

    score = tl.load(
        state_cache + flat[:, None] * (2 * HEAD_DIM_) + HEAD_DIM_ + ds[None, :],
        mask=(rs[:, None] < compress_ratio) & (ds[None, :] < HEAD_DIM_),
        other=-float("inf"),
    ).to(tl.float32)
    mx = tl.max(score, axis=0)
    ex = tl.exp(score - mx[None, :])
    den = tl.sum(ex, axis=0)
    kv = tl.load(
        state_cache + flat[:, None] * (2 * HEAD_DIM_) + ds[None, :],
        mask=(rs[:, None] < compress_ratio) & (ds[None, :] < HEAD_DIM_),
        other=0.0,
    ).to(tl.float32)
    comp = tl.sum(kv * ex, axis=0) / den
    tl.store(tmp + out_id * HEAD_DIM_ + ds, comp, mask=ds < HEAD_DIM_)


@triton.jit
def _compress_contiguous_blocks_kernel(state_cache, token_to_req, positions, boundary_token_indices, block_table,
                                       tmp,
                                       num_outputs:tl.constexpr, block_size:tl.constexpr, compress_ratio:tl.constexpr,
                                       HEAD_DIM_:tl.constexpr,
                                       blocks_per_req:tl.constexpr, BLOCK_R:tl.constexpr, BLOCK_D_:tl.constexpr):
    out_id = tl.program_id(0)
    d0 = tl.program_id(1) * BLOCK_D_
    ds = d0 + tl.arange(0, BLOCK_D_)
    rs = tl.arange(0, BLOCK_R)

    boundary_idx = tl.load(boundary_token_indices + out_id)
    boundary_pos = tl.load(positions + boundary_idx).to(tl.int64)
    req = tl.load(token_to_req + boundary_idx).to(tl.int32)
    first_block = tl.load(block_table + req * blocks_per_req).to(tl.int64)
    flat = first_block * block_size + boundary_pos - compress_ratio + 1 + rs

    score = tl.load(
        state_cache + flat[:, None] * (2 * HEAD_DIM_) + HEAD_DIM_ + ds[None, :],
        mask=(rs[:, None] < compress_ratio) & (ds[None, :] < HEAD_DIM_),
        other=-float("inf"),
    ).to(tl.float32)
    mx = tl.max(score, axis=0)
    ex = tl.exp(score - mx[None, :])
    den = tl.sum(ex, axis=0)
    kv = tl.load(
        state_cache + flat[:, None] * (2 * HEAD_DIM_) + ds[None, :],
        mask=(rs[:, None] < compress_ratio) & (ds[None, :] < HEAD_DIM_),
        other=0.0,
    ).to(tl.float32)
    comp = tl.sum(kv * ex, axis=0) / den
    tl.store(tmp + out_id * HEAD_DIM_ + ds, comp, mask=ds < HEAD_DIM_)


@triton.jit
def _compress_contiguous_blocks_softmax_kernel(state_cache, token_to_req, positions, boundary_token_indices, block_table,
                                               tmp,
                                               num_outputs:tl.constexpr, block_size:tl.constexpr, compress_ratio:tl.constexpr,
                                               HEAD_DIM_:tl.constexpr,
                                               blocks_per_req:tl.constexpr, BLOCK_R:tl.constexpr, BLOCK_D_:tl.constexpr):
    out_id = tl.program_id(0)
    d0 = tl.program_id(1) * BLOCK_D_
    ds = d0 + tl.arange(0, BLOCK_D_)
    rs = tl.arange(0, BLOCK_R)

    boundary_idx = tl.load(boundary_token_indices + out_id)
    boundary_pos = tl.load(positions + boundary_idx).to(tl.int64)
    req = tl.load(token_to_req + boundary_idx).to(tl.int32)
    first_block = tl.load(block_table + req * blocks_per_req).to(tl.int64)
    flat = first_block * block_size + boundary_pos - compress_ratio + 1 + rs

    score = tl.load(
        state_cache + flat[:, None] * (2 * HEAD_DIM_) + HEAD_DIM_ + ds[None, :],
        mask=(rs[:, None] < compress_ratio) & (ds[None, :] < HEAD_DIM_),
        other=-float("inf"),
    ).to(tl.float32)
    prob = tl.softmax(score, dim=0)
    kv = tl.load(
        state_cache + flat[:, None] * (2 * HEAD_DIM_) + ds[None, :],
        mask=(rs[:, None] < compress_ratio) & (ds[None, :] < HEAD_DIM_),
        other=0.0,
    ).to(tl.float32)
    comp = tl.sum(kv * prob, axis=0)
    tl.store(tmp + out_id * HEAD_DIM_ + ds, comp, mask=ds < HEAD_DIM_)


@triton.jit
def _compress_global_flat_kernel(state_cache, boundary_token_indices,
                                 tmp,
                                 num_outputs:tl.constexpr, compress_ratio:tl.constexpr,
                                 HEAD_DIM_:tl.constexpr,
                                 BLOCK_R:tl.constexpr, BLOCK_D_:tl.constexpr):
    out_id = tl.program_id(0)
    d0 = tl.program_id(1) * BLOCK_D_
    ds = d0 + tl.arange(0, BLOCK_D_)
    rs = tl.arange(0, BLOCK_R)

    boundary_idx = tl.load(boundary_token_indices + out_id).to(tl.int64)
    flat = boundary_idx - compress_ratio + 1 + rs

    score = tl.load(
        state_cache + flat[:, None] * (2 * HEAD_DIM_) + HEAD_DIM_ + ds[None, :],
        mask=(rs[:, None] < compress_ratio) & (ds[None, :] < HEAD_DIM_),
        other=-float("inf"),
    ).to(tl.float32)
    mx = tl.max(score, axis=0)
    ex = tl.exp(score - mx[None, :])
    den = tl.sum(ex, axis=0)
    kv = tl.load(
        state_cache + flat[:, None] * (2 * HEAD_DIM_) + ds[None, :],
        mask=(rs[:, None] < compress_ratio) & (ds[None, :] < HEAD_DIM_),
        other=0.0,
    ).to(tl.float32)
    comp = tl.sum(kv * ex, axis=0) / den
    tl.store(tmp + out_id * HEAD_DIM_ + ds, comp, mask=ds < HEAD_DIM_)


@triton.jit
def _compress_global_flat_softmax_kernel(state_cache, boundary_token_indices,
                                         tmp,
                                         num_outputs:tl.constexpr, compress_ratio:tl.constexpr,
                                         HEAD_DIM_:tl.constexpr,
                                         BLOCK_R:tl.constexpr, BLOCK_D_:tl.constexpr):
    out_id = tl.program_id(0)
    d0 = tl.program_id(1) * BLOCK_D_
    ds = d0 + tl.arange(0, BLOCK_D_)
    rs = tl.arange(0, BLOCK_R)

    boundary_idx = tl.load(boundary_token_indices + out_id).to(tl.int64)
    flat = boundary_idx - compress_ratio + 1 + rs

    score = tl.load(
        state_cache + flat[:, None] * (2 * HEAD_DIM_) + HEAD_DIM_ + ds[None, :],
        mask=(rs[:, None] < compress_ratio) & (ds[None, :] < HEAD_DIM_),
        other=-float("inf"),
    ).to(tl.float32)
    prob = tl.softmax(score, dim=0)
    kv = tl.load(
        state_cache + flat[:, None] * (2 * HEAD_DIM_) + ds[None, :],
        mask=(rs[:, None] < compress_ratio) & (ds[None, :] < HEAD_DIM_),
        other=0.0,
    ).to(tl.float32)
    comp = tl.sum(kv * prob, axis=0)
    tl.store(tmp + out_id * HEAD_DIM_ + ds, comp, mask=ds < HEAD_DIM_)


@triton.jit
def _compress_global_flat_shared_score_kernel(state_cache, boundary_token_indices,
                                              tmp,
                                              num_outputs:tl.constexpr, compress_ratio:tl.constexpr,
                                              HEAD_DIM_:tl.constexpr,
                                              BLOCK_R:tl.constexpr, BLOCK_D_:tl.constexpr):
    out_id = tl.program_id(0)
    d0 = tl.program_id(1) * BLOCK_D_
    ds = d0 + tl.arange(0, BLOCK_D_)
    rs = tl.arange(0, BLOCK_R)

    boundary_idx = tl.load(boundary_token_indices + out_id).to(tl.int64)
    flat = boundary_idx - compress_ratio + 1 + rs

    score = tl.load(
        state_cache + flat * (2 * HEAD_DIM_) + HEAD_DIM_,
        mask=rs < compress_ratio,
        other=-float("inf"),
    ).to(tl.float32)
    mx = tl.max(score, axis=0)
    ex = tl.exp(score - mx)
    den = tl.sum(ex, axis=0)
    kv = tl.load(
        state_cache + flat[:, None] * (2 * HEAD_DIM_) + ds[None, :],
        mask=(rs[:, None] < compress_ratio) & (ds[None, :] < HEAD_DIM_),
        other=0.0,
    ).to(tl.float32)
    comp = tl.sum(kv * ex[:, None], axis=0) / den
    tl.store(tmp + out_id * HEAD_DIM_ + ds, comp, mask=ds < HEAD_DIM_)






@triton.jit
def _norm_quant_rope_write_kernel(tmp, rms_norm_weight, positions, boundary_token_indices,
                                  cos_sin_cache, kv_slot_mapping, out,
                                  rms_norm_eps:tl.constexpr, compress_ratio:tl.constexpr,
                                  BLOCK_STRIDE:tl.constexpr, BLOCK:tl.constexpr,
                                  HEAD_DIM_:tl.constexpr, NOPE_HEAD_DIM_:tl.constexpr,
                                  ROPE_HEAD_DIM_:tl.constexpr, KV_BLOCK_SIZE_:tl.constexpr,
                                  TOKEN_STRIDE_:tl.constexpr, SCALE_DIM_:tl.constexpr,
                                  QBLOCKS:tl.constexpr, VALID_QBLOCKS:tl.constexpr,
                                  QWIDTH:tl.constexpr):
    out_id = tl.program_id(0)
    offs = tl.arange(0, BLOCK)
    v_all = tl.load(tmp + out_id * HEAD_DIM_ + offs, mask=offs < HEAD_DIM_, other=0.0).to(tl.float32)
    ss = tl.sum(v_all * v_all, axis=0)
    r = tl.rsqrt(ss / HEAD_DIM_ + rms_norm_eps)

    boundary_idx = tl.load(boundary_token_indices + out_id)
    kv_slot = tl.load(kv_slot_mapping + boundary_idx).to(tl.int64)
    page = kv_slot // KV_BLOCK_SIZE_
    slot = kv_slot - page * KV_BLOCK_SIZE_
    value_base = page * BLOCK_STRIDE + slot * TOKEN_STRIDE_
    scale_base = page * BLOCK_STRIDE + KV_BLOCK_SIZE_ * TOKEN_STRIDE_ + slot * SCALE_DIM_

    qblk = tl.arange(0, QBLOCKS)
    qoff = tl.arange(0, QWIDTH)
    qd = qoff[:, None] + qblk[None, :] * QWIDTH
    qmask = qd < NOPE_HEAD_DIM_
    qv = tl.load(tmp + out_id * HEAD_DIM_ + qd, mask=qmask, other=0.0).to(tl.float32)
    qw = tl.load(rms_norm_weight + qd, mask=qmask, other=0.0).to(tl.float32)
    normed = (qv * r * qw).to(tl.bfloat16).to(tl.float32)
    amax = tl.max(tl.abs(normed), axis=0)
    amax = tl.maximum(amax, 1.0e-4)
    exponent = tl.ceil(tl.log2(amax * (1.0 / 127.0)))
    inv_scale = tl.exp2(-exponent)
    q = tl.minimum(tl.maximum(normed * inv_scale[None, :], -127.0), 127.0).to(tl.int8)
    tl.store(out + value_base + qd, q.to(tl.uint8, bitcast=True), mask=qmask)
    scale_u8 = tl.minimum(tl.maximum(exponent + 127.0, 0.0), 255.0).to(tl.uint8)
    tl.store(out + scale_base + qblk, scale_u8, mask=qblk < VALID_QBLOCKS)

    pair = tl.arange(0, 32)
    d_even = NOPE_HEAD_DIM_ + pair * 2
    d_odd = d_even + 1
    even = tl.load(tmp + out_id * HEAD_DIM_ + d_even, mask=pair < 32, other=0.0).to(tl.float32)
    odd = tl.load(tmp + out_id * HEAD_DIM_ + d_odd, mask=pair < 32, other=0.0).to(tl.float32)
    w_even = tl.load(rms_norm_weight + d_even, mask=pair < 32, other=0.0).to(tl.float32)
    w_odd = tl.load(rms_norm_weight + d_odd, mask=pair < 32, other=0.0).to(tl.float32)
    even = even * r * w_even
    odd = odd * r * w_odd

    boundary_idx = tl.load(boundary_token_indices + out_id)
    boundary_pos = tl.load(positions + boundary_idx).to(tl.int64)
    compressed_pos = (boundary_pos // compress_ratio) * compress_ratio
    cos_v = tl.load(cos_sin_cache + compressed_pos * ROPE_HEAD_DIM_ + pair, mask=pair < 32, other=1.0).to(tl.float32)
    sin_v = tl.load(cos_sin_cache + compressed_pos * ROPE_HEAD_DIM_ + 32 + pair, mask=pair < 32, other=0.0).to(tl.float32)
    rot_even = (even * cos_v - odd * sin_v).to(tl.bfloat16)
    rot_odd = (odd * cos_v + even * sin_v).to(tl.bfloat16)
    bits_even = rot_even.to(tl.uint16, bitcast=True)
    bits_odd = rot_odd.to(tl.uint16, bitcast=True)

    value_base = page * BLOCK_STRIDE + slot * TOKEN_STRIDE_ + NOPE_HEAD_DIM_
    out_even = pair * 4
    out_odd = out_even + 2
    tl.store(out + value_base + out_even, (bits_even & 0xFF).to(tl.uint8), mask=pair < 32)
    tl.store(out + value_base + out_even + 1, (bits_even >> 8).to(tl.uint8), mask=pair < 32)
    tl.store(out + value_base + out_odd, (bits_odd & 0xFF).to(tl.uint8), mask=pair < 32)
    tl.store(out + value_base + out_odd + 1, (bits_odd >> 8).to(tl.uint8), mask=pair < 32)


@triton.jit
def _rrms_kernel(tmp, rrms, rms_norm_eps:tl.constexpr,
                 HEAD_DIM_:tl.constexpr, BLOCK:tl.constexpr):
    out_id = tl.program_id(0)
    offs = tl.arange(0, BLOCK)
    v = tl.load(tmp + out_id * HEAD_DIM_ + offs, mask=offs < HEAD_DIM_, other=0.0).to(tl.float32)
    ss = tl.sum(v * v, axis=0)
    tl.store(rrms + out_id, tl.rsqrt(ss / HEAD_DIM_ + rms_norm_eps))




@triton.jit
def _write_nope_native_kernel(tmp, rrms, rms_norm_weight, boundary_token_indices, kv_slot_mapping, out,
                              BLOCK_STRIDE:tl.constexpr,
                              HEAD_DIM_:tl.constexpr, NOPE_HEAD_DIM_:tl.constexpr,
                              KV_BLOCK_SIZE_:tl.constexpr, TOKEN_STRIDE_:tl.constexpr,
                              SCALE_DIM_:tl.constexpr, BLOCK:tl.constexpr):
    out_id = tl.program_id(0)
    qblk = tl.program_id(1)
    offs = tl.arange(0, BLOCK)
    d = qblk * BLOCK + offs

    r = tl.load(rrms + out_id).to(tl.float32)
    w = tl.load(rms_norm_weight + d, mask=d < NOPE_HEAD_DIM_, other=0.0).to(tl.float32)
    v = tl.load(tmp + out_id * HEAD_DIM_ + d, mask=d < NOPE_HEAD_DIM_, other=0.0).to(tl.float32)
    normed = (v * r * w).to(tl.bfloat16).to(tl.float32)
    amax = tl.max(tl.abs(normed), axis=0)
    amax = tl.maximum(amax, 1.0e-4)
    exponent = tl.ceil(tl.log2(amax * (1.0 / 127.0)))
    inv_scale = tl.exp2(-exponent)
    q = tl.minimum(tl.maximum(normed * inv_scale, -127.0), 127.0).to(tl.int8)
    scale_u8 = tl.minimum(tl.maximum(exponent + 127.0, 0.0), 255.0).to(tl.uint8)

    boundary_idx = tl.load(boundary_token_indices + out_id)
    kv_slot = tl.load(kv_slot_mapping + boundary_idx).to(tl.int64)
    page = kv_slot // KV_BLOCK_SIZE_
    slot = kv_slot - page * KV_BLOCK_SIZE_
    value_base = page * BLOCK_STRIDE + slot * TOKEN_STRIDE_
    scale_base = page * BLOCK_STRIDE + KV_BLOCK_SIZE_ * TOKEN_STRIDE_ + slot * SCALE_DIM_
    tl.store(out + value_base + d, q.to(tl.uint8, bitcast=True), mask=d < NOPE_HEAD_DIM_)
    tl.store(out + scale_base + qblk, scale_u8)
















@triton.jit
def _write_rope_kernel(tmp, rrms, rms_norm_weight, positions, boundary_token_indices,
                       cos_sin_cache, kv_slot_mapping, out,
                       compress_ratio:tl.constexpr, BLOCK_STRIDE:tl.constexpr,
                       HEAD_DIM_:tl.constexpr, NOPE_HEAD_DIM_:tl.constexpr,
                       ROPE_HEAD_DIM_:tl.constexpr, KV_BLOCK_SIZE_:tl.constexpr,
                       TOKEN_STRIDE_:tl.constexpr, BLOCK:tl.constexpr):
    out_id = tl.program_id(0)
    pair = tl.arange(0, BLOCK)
    d_even = NOPE_HEAD_DIM_ + pair * 2
    d_odd = d_even + 1

    r = tl.load(rrms + out_id).to(tl.float32)
    even = tl.load(tmp + out_id * HEAD_DIM_ + d_even, mask=pair < 32, other=0.0).to(tl.float32)
    odd = tl.load(tmp + out_id * HEAD_DIM_ + d_odd, mask=pair < 32, other=0.0).to(tl.float32)
    w_even = tl.load(rms_norm_weight + d_even, mask=pair < 32, other=0.0).to(tl.float32)
    w_odd = tl.load(rms_norm_weight + d_odd, mask=pair < 32, other=0.0).to(tl.float32)
    even = even * r * w_even
    odd = odd * r * w_odd

    boundary_idx = tl.load(boundary_token_indices + out_id)
    boundary_pos = tl.load(positions + boundary_idx).to(tl.int64)
    compressed_pos = (boundary_pos // compress_ratio) * compress_ratio
    cos_v = tl.load(cos_sin_cache + compressed_pos * ROPE_HEAD_DIM_ + pair, mask=pair < 32, other=1.0).to(tl.float32)
    sin_v = tl.load(cos_sin_cache + compressed_pos * ROPE_HEAD_DIM_ + 32 + pair, mask=pair < 32, other=0.0).to(tl.float32)
    rot_even = (even * cos_v - odd * sin_v).to(tl.bfloat16)
    rot_odd = (odd * cos_v + even * sin_v).to(tl.bfloat16)
    bits_even = rot_even.to(tl.uint16, bitcast=True)
    bits_odd = rot_odd.to(tl.uint16, bitcast=True)

    kv_slot = tl.load(kv_slot_mapping + boundary_idx).to(tl.int64)
    page = kv_slot // KV_BLOCK_SIZE_
    slot = kv_slot - page * KV_BLOCK_SIZE_
    value_base = page * BLOCK_STRIDE + slot * TOKEN_STRIDE_ + NOPE_HEAD_DIM_
    out_even = pair * 4
    out_odd = out_even + 2
    tl.store(out + value_base + out_even, (bits_even & 0xFF).to(tl.uint8), mask=pair < 32)
    tl.store(out + value_base + out_even + 1, (bits_even >> 8).to(tl.uint8), mask=pair < 32)
    tl.store(out + value_base + out_odd, (bits_odd & 0xFF).to(tl.uint8), mask=pair < 32)
    tl.store(out + value_base + out_odd + 1, (bits_odd >> 8).to(tl.uint8), mask=pair < 32)




@triton.jit
def _ascend_postprocess_scalar_loop_kernel(tmp, rms_norm_weight, positions, boundary_token_indices,
                                           cos_sin_cache, kv_slot_mapping, out,
                                           rms_norm_eps:tl.constexpr, compress_ratio:tl.constexpr,
                                           BLOCK_STRIDE:tl.constexpr,
                                           HEAD_DIM_:tl.constexpr, NOPE_HEAD_DIM_:tl.constexpr,
                                           ROPE_HEAD_DIM_:tl.constexpr, KV_BLOCK_SIZE_:tl.constexpr,
                                           TOKEN_STRIDE_:tl.constexpr, SCALE_DIM_:tl.constexpr,
                                           BLOCK:tl.constexpr):
    out_id = tl.program_id(0)
    offs_all = tl.arange(0, 512)
    v_all = tl.load(tmp + out_id * HEAD_DIM_ + offs_all, mask=offs_all < HEAD_DIM_, other=0.0).to(tl.float32)
    ss = tl.sum(v_all * v_all, axis=0)
    r = tl.rsqrt(ss / HEAD_DIM_ + rms_norm_eps)

    boundary_idx = tl.load(boundary_token_indices + out_id)
    kv_slot = tl.load(kv_slot_mapping + boundary_idx).to(tl.int64)
    page = kv_slot // KV_BLOCK_SIZE_
    slot = kv_slot - page * KV_BLOCK_SIZE_
    value_base = page * BLOCK_STRIDE + slot * TOKEN_STRIDE_
    scale_base = page * BLOCK_STRIDE + KV_BLOCK_SIZE_ * TOKEN_STRIDE_ + slot * SCALE_DIM_

    offs = tl.arange(0, BLOCK)
    for qblk in tl.static_range(0, 7):
        d = qblk * BLOCK + offs
        w = tl.load(rms_norm_weight + d, mask=d < NOPE_HEAD_DIM_, other=0.0).to(tl.float32)
        v = tl.load(tmp + out_id * HEAD_DIM_ + d, mask=d < NOPE_HEAD_DIM_, other=0.0).to(tl.float32)
        normed = _bf16_rne_to_f32(v * r * w)
        amax = tl.max(tl.abs(normed), axis=0)
        amax = tl.maximum(amax, 1.0e-4)
        exponent = tl.ceil(tl.log2(amax * (1.0 / 127.0)))
        inv_scale = tl.exp2(-exponent)
        qf = tl.minimum(tl.maximum(normed * inv_scale, -127.0), 127.0)
        q_abs = tl.floor(tl.abs(qf))
        q_i32 = tl.where(qf < 0.0, -q_abs, q_abs).to(tl.int32)
        q_u8 = tl.where(q_i32 < 0, q_i32 + 256, q_i32).to(tl.uint8)
        scale_i32 = tl.minimum(tl.maximum((exponent + 127.0).to(tl.int32), 0), 255)
        tl.store(out + value_base + d, q_u8, mask=d < NOPE_HEAD_DIM_)
        tl.store(out + scale_base + qblk, scale_i32)
    tl.store(out + scale_base + 7, tl.full((), 0, tl.int32))

    boundary_pos = tl.load(positions + boundary_idx).to(tl.int64)
    compressed_pos = (boundary_pos // compress_ratio) * compress_ratio
    for pair in tl.static_range(0, 32):
        d_even = NOPE_HEAD_DIM_ + pair * 2
        d_odd = d_even + 1
        even = tl.load(tmp + out_id * HEAD_DIM_ + d_even).to(tl.float32)
        odd = tl.load(tmp + out_id * HEAD_DIM_ + d_odd).to(tl.float32)
        w_even = tl.load(rms_norm_weight + d_even).to(tl.float32)
        w_odd = tl.load(rms_norm_weight + d_odd).to(tl.float32)
        even = even * r * w_even
        odd = odd * r * w_odd
        cos_v = tl.load(cos_sin_cache + compressed_pos * ROPE_HEAD_DIM_ + pair).to(tl.float32)
        sin_v = tl.load(cos_sin_cache + compressed_pos * ROPE_HEAD_DIM_ + 32 + pair).to(tl.float32)
        rot_even = (even * cos_v - odd * sin_v).to(tl.bfloat16)
        rot_odd = (odd * cos_v + even * sin_v).to(tl.bfloat16)
        bits_even = rot_even.to(tl.uint16, bitcast=True)
        bits_odd = rot_odd.to(tl.uint16, bitcast=True)
        rope_base = value_base + NOPE_HEAD_DIM_ + pair * 4
        tl.store(out + rope_base, (bits_even & 0xFF).to(tl.uint8))
        tl.store(out + rope_base + 1, (bits_even >> 8).to(tl.uint8))
        tl.store(out + rope_base + 2, (bits_odd & 0xFF).to(tl.uint8))
        tl.store(out + rope_base + 3, (bits_odd >> 8).to(tl.uint8))


def c128_256_512_compress(
    state_cache: torch.Tensor,
    token_to_req: torch.Tensor,
    positions: torch.Tensor,
    boundary_token_indices: torch.Tensor,
    block_table: torch.Tensor,
    rms_norm_weight: torch.Tensor,
    cos_sin_cache: torch.Tensor,
    kv_slot_mapping: torch.Tensor,
    kv_cache: torch.Tensor,
    block_size: int,
    compress_ratio: int,
    rms_norm_eps: float = 1.0e-6,
) -> torch.Tensor:
    num_outputs = boundary_token_indices.numel()
    out = kv_cache
    if num_outputs == 0:
        return out

    tmp = torch.empty((num_outputs, HEAD_DIM), device=state_cache.device, dtype=torch.float32)
    blocks_per_req = block_table.shape[1]
    block_stride = kv_cache.shape[1]
    use_global_flat_fast_path = _use_global_flat_fast_path(state_cache)
    use_contiguous_fast_path = _use_contiguous_block_fast_path(state_cache) or _is_ascend(state_cache)
    use_nvidia_target = _is_nvidia_target(state_cache)
    use_thead_shared_score = _is_thead(state_cache)
    if use_global_flat_fast_path or use_contiguous_fast_path:
        if compress_ratio >= 512:
            block_d = BLOCK_D_C512_SMALL
        elif compress_ratio >= 256:
            block_d = BLOCK_D_C256_SMALL
        else:
            block_d = BLOCK_D_C128_SMALL
    elif _use_wide_compress_tiles(state_cache):
        if compress_ratio >= 512:
            block_d = BLOCK_D_C512_SMALL
        elif compress_ratio >= 256:
            block_d = BLOCK_D_C256_SMALL
        else:
            block_d = BLOCK_D_C128_SMALL
    else:
        if compress_ratio >= 512:
            block_d = BLOCK_D_C512_SMALL if num_outputs <= 64 else BLOCK_D_C512_LARGE
        elif compress_ratio >= 256:
            block_d = BLOCK_D_C256_SMALL if num_outputs <= 128 else BLOCK_D_C256_LARGE
        else:
            block_d = BLOCK_D_C128_SMALL if num_outputs <= 256 else BLOCK_D_C128_LARGE
    if use_thead_shared_score:
        if compress_ratio >= 512:
            block_d = 32
        elif compress_ratio >= 256:
            block_d = 64
        _compress_global_flat_shared_score_kernel[(num_outputs, triton.cdiv(HEAD_DIM, block_d))](
            state_cache, boundary_token_indices,
            tmp,
            num_outputs, compress_ratio, HEAD_DIM,
            BLOCK_R=compress_ratio,
            BLOCK_D_=block_d,
            num_warps=4,
            num_stages=3,
        )
    elif use_global_flat_fast_path:
        if use_nvidia_target:
            _compress_global_flat_softmax_kernel[(num_outputs, triton.cdiv(HEAD_DIM, block_d))](
                state_cache, boundary_token_indices,
                tmp,
                num_outputs, compress_ratio, HEAD_DIM,
                BLOCK_R=compress_ratio,
                BLOCK_D_=block_d,
                num_warps=8,
                num_stages=3,
            )
        else:
            _compress_global_flat_kernel[(num_outputs, triton.cdiv(HEAD_DIM, block_d))](
                state_cache, boundary_token_indices,
                tmp,
                num_outputs, compress_ratio, HEAD_DIM,
                BLOCK_R=compress_ratio,
                BLOCK_D_=block_d,
                num_warps=4,
                num_stages=3,
            )
    elif use_contiguous_fast_path:
        if use_nvidia_target:
            _compress_contiguous_blocks_softmax_kernel[(num_outputs, triton.cdiv(HEAD_DIM, block_d))](
                state_cache, token_to_req, positions, boundary_token_indices, block_table,
                tmp,
                num_outputs, block_size, compress_ratio, HEAD_DIM, blocks_per_req,
                BLOCK_R=compress_ratio,
                BLOCK_D_=block_d,
                num_warps=8,
                num_stages=3,
            )
        else:
            _compress_contiguous_blocks_kernel[(num_outputs, triton.cdiv(HEAD_DIM, block_d))](
                state_cache, token_to_req, positions, boundary_token_indices, block_table,
                tmp,
                num_outputs, block_size, compress_ratio, HEAD_DIM, blocks_per_req,
                BLOCK_R=compress_ratio,
                BLOCK_D_=block_d,
                num_warps=4,
                num_stages=3,
            )
    else:
        _compress_kernel[(num_outputs, triton.cdiv(HEAD_DIM, block_d))](
            state_cache, token_to_req, positions, boundary_token_indices, block_table,
            tmp,
            num_outputs, block_size, compress_ratio, HEAD_DIM, blocks_per_req,
            BLOCK_R=compress_ratio,
            BLOCK_D_=block_d,
            num_warps=8,
            num_stages=3,
        )
    if not _is_ascend(state_cache):
        if _is_metax(state_cache):
            rrms = torch.empty((num_outputs,), device=state_cache.device, dtype=torch.float32)
            _rrms_kernel[(num_outputs,)](
                tmp, rrms, rms_norm_eps,
                HEAD_DIM_=HEAD_DIM,
                BLOCK=HEAD_DIM,
                num_warps=8,
            )
            _write_nope_native_kernel[(num_outputs, NOPE_HEAD_DIM // 64)](
                tmp, rrms, rms_norm_weight, boundary_token_indices, kv_slot_mapping, out,
                block_stride,
                HEAD_DIM_=HEAD_DIM,
                NOPE_HEAD_DIM_=NOPE_HEAD_DIM,
                KV_BLOCK_SIZE_=KV_BLOCK_SIZE,
                TOKEN_STRIDE_=TOKEN_STRIDE,
                SCALE_DIM_=SCALE_DIM,
                BLOCK=64,
                num_warps=2,
            )
            _write_rope_kernel[(num_outputs,)](
                tmp, rrms, rms_norm_weight, positions, boundary_token_indices,
                cos_sin_cache, kv_slot_mapping, out,
                compress_ratio, block_stride,
                HEAD_DIM_=HEAD_DIM,
                NOPE_HEAD_DIM_=NOPE_HEAD_DIM,
                ROPE_HEAD_DIM_=ROPE_HEAD_DIM,
                KV_BLOCK_SIZE_=KV_BLOCK_SIZE,
                TOKEN_STRIDE_=TOKEN_STRIDE,
                BLOCK=32,
                num_warps=1,
            )
            return out
        _norm_quant_rope_write_kernel[(num_outputs,)](
            tmp, rms_norm_weight, positions, boundary_token_indices,
            cos_sin_cache, kv_slot_mapping, out,
            rms_norm_eps, compress_ratio, block_stride,
            BLOCK=HEAD_DIM,
            HEAD_DIM_=HEAD_DIM,
            NOPE_HEAD_DIM_=NOPE_HEAD_DIM,
            ROPE_HEAD_DIM_=ROPE_HEAD_DIM,
            KV_BLOCK_SIZE_=KV_BLOCK_SIZE,
            TOKEN_STRIDE_=TOKEN_STRIDE,
            SCALE_DIM_=SCALE_DIM,
            QBLOCKS=SCALE_DIM,
            VALID_QBLOCKS=NOPE_HEAD_DIM // 64,
            QWIDTH=64,
            num_warps=8,
        )
        return out

    _ascend_postprocess_scalar_loop_kernel[(num_outputs,)](
        tmp, rms_norm_weight, positions, boundary_token_indices,
        cos_sin_cache, kv_slot_mapping, out,
        rms_norm_eps, compress_ratio, block_stride,
        HEAD_DIM_=HEAD_DIM,
        NOPE_HEAD_DIM_=NOPE_HEAD_DIM,
        ROPE_HEAD_DIM_=ROPE_HEAD_DIM,
        KV_BLOCK_SIZE_=KV_BLOCK_SIZE,
        TOKEN_STRIDE_=TOKEN_STRIDE,
        SCALE_DIM_=SCALE_DIM,
        BLOCK=64,
        num_warps=1,
    )
    return out
