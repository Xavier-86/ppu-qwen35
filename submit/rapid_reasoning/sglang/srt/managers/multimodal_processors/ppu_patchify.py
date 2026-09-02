"""Exact Qwen3.5 image normalize/patchify fusion for the PPU fast path."""

import os
from typing import Optional, Tuple

import torch
import triton
import triton.language as tl
from PIL import Image


ENABLED = os.environ.get("SGLANG_FUSED_MM_PATCHIFY", "1") == "1"


@triton.jit
def _normalize_patchify_kernel(
    image,
    output,
    height,
    width,
    grid_width,
    merge: tl.constexpr,
    patch: tl.constexpr,
    output_width: tl.constexpr,
    BLOCK: tl.constexpr,
):
    row = tl.program_id(0)
    column = tl.arange(0, BLOCK)
    mask = column < output_width

    merge_w = row % merge
    row_rest = row // merge
    merge_h = row_rest % merge
    row_rest = row_rest // merge
    grid_group_w = row_rest % (grid_width // merge)
    grid_group_h = row_rest // (grid_width // merge)
    grid_h = grid_group_h * merge + merge_h
    grid_w = grid_group_w * merge + merge_w

    patch_w = column % patch
    patch_h = (column // patch) % patch
    channel = column // (2 * patch * patch)
    image_h = grid_h * patch + patch_h
    image_w = grid_w * patch + patch_w
    image_offset = (channel * height + image_h) * width + image_w
    value = tl.load(image + image_offset, mask=mask).to(tl.float32)
    # BACKPORT-PPU: the fixed Qwen3.5 processor has mean/std=0.5 and
    # rescale=1/255, so this is exactly (uint8 / 255 - 0.5) / 0.5.
    normalized = (value - 127.5) / 127.5
    tl.store(output + row * output_width + column, normalized, mask=mask)


def _has_fixed_qwen35_config(image_processor) -> bool:
    """Return whether the processor matches the kernel's exact contract."""
    return (
        image_processor.do_resize
        and image_processor.do_rescale
        and image_processor.do_normalize
        and image_processor.patch_size == 16
        and image_processor.temporal_patch_size == 2
        and image_processor.merge_size == 2
        and image_processor.rescale_factor == 1 / 255
        and tuple(image_processor.image_mean or ()) == (0.5, 0.5, 0.5)
        and tuple(image_processor.image_std or ()) == (0.5, 0.5, 0.5)
        and image_processor.min_pixels is not None
        and image_processor.max_pixels is not None
    )


def fused_qwen35_patchify_or_none(
    image_processor, image: Image.Image
) -> Optional[Tuple[torch.Tensor, Tuple[int, int, int]]]:
    """Prepare, resize and patchify one image, or return None if unsupported."""
    if not ENABLED or not isinstance(image, Image.Image):
        return None
    if not _has_fixed_qwen35_config(image_processor):
        return None

    from torchvision.transforms.v2 import functional as tvf
    from transformers.image_processing_utils_fast import (
        pil_torch_interpolation_mapping,
    )
    from transformers.models.qwen2_vl.image_processing_qwen2_vl_fast import (
        smart_resize,
    )

    prepared = image_processor._prepare_input_images(
        image,
        do_convert_rgb=image_processor.do_convert_rgb,
        input_data_format=None,
        device="cuda",
    )[0]
    if prepared.dtype != torch.uint8 or prepared.ndim != 3 or prepared.shape[0] != 3:
        return None

    height, width = smart_resize(
        image.height,
        image.width,
        factor=image_processor.patch_size * image_processor.merge_size,
        min_pixels=image_processor.min_pixels,
        max_pixels=image_processor.max_pixels,
    )
    resized = tvf.resize(
        prepared.unsqueeze(0),
        size=(height, width),
        interpolation=pil_torch_interpolation_mapping[image_processor.resample],
    )[0].contiguous()

    patch = image_processor.patch_size
    temporal = image_processor.temporal_patch_size
    grid_height = height // patch
    grid_width = width // patch
    output_width = 3 * temporal * patch * patch
    output = torch.empty(
        (grid_height * grid_width, output_width),
        dtype=torch.bfloat16,
        device=resized.device,
    )
    _normalize_patchify_kernel[(grid_height * grid_width,)](
        resized,
        output,
        height,
        width,
        grid_width,
        merge=image_processor.merge_size,
        patch=patch,
        output_width=output_width,
        BLOCK=triton.next_power_of_2(output_width),
        num_warps=4,
    )
    return output, (1, grid_height, grid_width)
