import asyncio
import math
from typing import List, Union

import torch
from PIL import Image

from sglang.srt.layers.rotary_embedding import MRotaryEmbedding
from sglang.srt.managers.multimodal_processors.base_processor import (
    BaseMultimodalProcessor as SGLangBaseProcessor,
)
from sglang.srt.managers.multimodal_processors.base_processor import (
    MultimodalSpecialTokens,
)
from sglang.srt.managers.schedule_batch import Modality, MultimodalDataItem
# This submission serves the Qwen3-VL/Qwen3.5 family only.  Keeping the
# Qwen2/2.5 model imports here would eagerly load two unrelated vision stacks
# during scheduler startup.
from sglang.srt.models.qwen3_5 import Qwen3_5ForConditionalGeneration
from sglang.srt.models.qwen3_vl import Qwen3VLForConditionalGeneration


# Compatible with Qwen3VL and Qwen3.5
class Qwen2_5VLImageProcessor(SGLangBaseProcessor):
    models = [
        Qwen3VLForConditionalGeneration,
        Qwen3_5ForConditionalGeneration,
    ]

    def __init__(self, hf_config, server_args, _processor):
        super().__init__(hf_config, server_args, _processor)
        # BACKPORT: Qwen3-VL/Qwen3.5 resize with factor 32 (patch 16 x merge 2)
        # inside the HF image processor; the manual factor-28 resize below is
        # Qwen2/2.5-specific and must be skipped for the qwen3 family.
        self._skip_manual_resize = hf_config.model_type.startswith(
            ("qwen3_vl", "qwen3_5")
        )
        self.IMAGE_TOKEN = "<|vision_start|><|image_pad|><|vision_end|>"
        self.IM_START_TOKEN_ID = hf_config.vision_start_token_id
        self.IM_END_TOKEN_ID = hf_config.vision_end_token_id
        self.image_token_id = hf_config.image_token_id
        self.video_token_id = hf_config.video_token_id
        self.vision_start_token_id = hf_config.vision_start_token_id
        self.vision_end_token_id = hf_config.vision_end_token_id
        self.NUM_TOKEN_PER_FRAME = 770
        self.IMAGE_FACTOR = 28
        self.MIN_PIXELS = 4 * 28 * 28
        self.MAX_PIXELS = 16384 * 28 * 28
        self.MAX_RATIO = 200

    def _fast_process_mm_data(self, base_output):
        """Single-PIL-image fast path; returns None to use the generic path."""
        try:
            images = base_output.images
            if not images or len(images) != 1:
                return None
            from PIL import Image as _PIL

            if not isinstance(images[0], _PIL.Image):
                return None
            processor = self._processor
            ip = getattr(processor, "image_processor", None)
            tok = getattr(processor, "tokenizer", None)
            if ip is None or tok is None:
                return None
            from transformers.image_processing_utils_fast import (
                BaseImageProcessorFast,
                pil_torch_interpolation_mapping,
            )

            if not isinstance(ip, BaseImageProcessorFast):
                return None
            # Mirror preprocess()'s size resolution: this processor is built
            # via the min_pixels/max_pixels backcompat path (the 4.51
            # __init__ drops the size dict), so the effective bounds come
            # from min_pixels/max_pixels, NOT ip.size.
            size = ip.size
            if ip.min_pixels is not None and ip.max_pixels is not None:
                size = {
                    "shortest_edge": ip.min_pixels,
                    "longest_edge": ip.max_pixels,
                }
            fused = None
            if self._skip_manual_resize:
                # BACKPORT-PPU: preserve the exact torchvision resize, then
                # fuse normalize + temporal duplicate + patchify and emit the
                # final BF16 transport tensor in one kernel.
                from sglang.srt.managers.multimodal_processors.ppu_patchify import (
                    fused_qwen35_patchify_or_none,
                )

                fused = fused_qwen35_patchify_or_none(ip, images[0])
            if fused is not None:
                patches, grid = fused
            else:
                patches, grid = ip._preprocess(
                    images[0],
                    do_resize=ip.do_resize,
                    size=size,
                    interpolation=pil_torch_interpolation_mapping[ip.resample],
                    do_rescale=ip.do_rescale,
                    rescale_factor=ip.rescale_factor,
                    do_normalize=ip.do_normalize,
                    image_mean=(
                        tuple(ip.image_mean) if ip.image_mean is not None else None
                    ),
                    image_std=(
                        tuple(ip.image_std) if ip.image_std is not None else None
                    ),
                    patch_size=ip.patch_size,
                    temporal_patch_size=ip.temporal_patch_size,
                    merge_size=ip.merge_size,
                    do_convert_rgb=ip.do_convert_rgb,
                    input_data_format=None,
                    device="cuda",
                )
            # Qwen2_5_VLProcessor.__call__ expands each image token to
            # grid.prod() // merge_size**2 copies before tokenizing.
            text = base_output.input_text
            image_token = getattr(processor, "image_token", "<|image_pad|>")
            if image_token in text:
                n_tokens = (grid[0] * grid[1] * grid[2]) // (ip.merge_size ** 2)
                text = text.replace(image_token, image_token * n_tokens, 1)
            enc = tok([text], padding=True, return_tensors="pt")
            return {
                "input_ids": enc["input_ids"],
                "pixel_values": patches,
                "image_grid_thw": torch.tensor([grid]),
            }
        except Exception:
            import logging
            import traceback

            logging.getLogger(__name__).warning(
                "mm fast path fell back to generic processor:\n%s",
                traceback.format_exc(),
            )
            return None

    async def process_mm_data_async(
        self,
        image_data: List[Union[str, bytes]],
        input_text,
        request_obj,
        max_req_input_len,
        *args,
        **kwargs,
    ):
        # BACKPORT: wrap any single (non-list) image payload, not just str —
        # GenerateReqInput unwraps a one-element list to a bare PIL Image.
        if not isinstance(image_data, list):
            image_data = [image_data]

        image_token = self.IMAGE_TOKEN
        from sglang.srt.ttft_prof import ENABLED as _TTFT_PROF, mark as _ttft_mark

        if _TTFT_PROF:
            import time as _time

            _mm_t0 = _time.perf_counter()
        base_output = self.load_mm_data(
            prompt=input_text,
            image_data=image_data,
            multimodal_tokens=MultimodalSpecialTokens(image_token=image_token),
            max_req_input_len=max_req_input_len,
        )
        if _TTFT_PROF:
            _ttft_mark("mm_load", _mm_t0, rid=getattr(request_obj, "rid", None))
            _mm_t1 = _time.perf_counter()

        def smart_resize(
            height: int,
            width: int,
            factor: int = self.IMAGE_FACTOR,
            min_pixels: int = self.MIN_PIXELS,
            max_pixels: int = self.MAX_PIXELS,
        ) -> tuple[int, int]:
            """
            Rescales the image so that the following conditions are met:

            1. Both dimensions (height and width) are divisible by 'factor'.

            2. The total number of pixels is within the range ['min_pixels', 'max_pixels'].

            3. The aspect ratio of the image is maintained as closely as possible.
            """
            if max(height, width) / min(height, width) > self.MAX_RATIO:
                raise ValueError(
                    f"absolute aspect ratio must be smaller than {self.MAX_RATIO}, got {max(height, width) / min(height, width)}"
                )
            h_bar = max(factor, round_by_factor(height, factor))
            w_bar = max(factor, round_by_factor(width, factor))
            if h_bar * w_bar > max_pixels:
                beta = math.sqrt((height * width) / max_pixels)
                h_bar = floor_by_factor(height / beta, factor)
                w_bar = floor_by_factor(width / beta, factor)
            elif h_bar * w_bar < min_pixels:
                beta = math.sqrt(min_pixels / (height * width))
                h_bar = ceil_by_factor(height * beta, factor)
                w_bar = ceil_by_factor(width * beta, factor)
            return h_bar, w_bar

        def resize_image(image, size_factor: int = self.IMAGE_FACTOR) -> Image.Image:
            width, height = image.size
            min_pixels = self.MIN_PIXELS
            max_pixels = self.MAX_PIXELS
            resized_height, resized_width = smart_resize(
                height,
                width,
                factor=size_factor,
                min_pixels=min_pixels,
                max_pixels=max_pixels,
            )
            image = image.resize((resized_width, resized_height))
            return image

        def round_by_factor(number: int, factor: int) -> int:
            """Returns the closest integer to 'number' that is divisible by 'factor'."""
            return round(number / factor) * factor

        def ceil_by_factor(number: int, factor: int) -> int:
            """Returns the smallest integer greater than or equal to 'number' that is divisible by 'factor'."""
            return math.ceil(number / factor) * factor

        def floor_by_factor(number: int, factor: int) -> int:
            """Returns the largest integer less than or equal to 'number' that is divisible by 'factor'."""
            return math.floor(number / factor) * factor

        async def resize_image_async(image):
            return resize_image(image)

        if base_output.images and not self._skip_manual_resize:
            resize_tasks = [resize_image_async(image) for image in base_output.images]
            base_output.images = await asyncio.gather(*resize_tasks)

        # BACKPORT-PPU: bypass the transformers processor wrapper for the
        # fixed single-image benchmark path. Offline split (GPU, MMBench
        # images): full processor.__call__ 2.0ms of which only ~0.6ms is real
        # work (tokenize 0.19 + patched _preprocess 0.43); the rest is kwargs
        # validation / BatchFeature / make_flat_list plumbing. This fast path
        # calls the tokenizer and the (fast-patched, bitwise-verified)
        # image_processor._preprocess directly and returns the same keys the
        # generic path provides. SGLANG_MM_FAST_PATH=0 disables; any
        # unexpected input falls back to process_mm_data().
        import os as _os

        ret = None
        if _os.environ.get("SGLANG_MM_FAST_PATH", "1") == "1":
            ret = self._fast_process_mm_data(base_output)
        if ret is None:
            ret = self.process_mm_data(
                input_text=base_output.input_text,
                images=base_output.images,
            )
        if _TTFT_PROF:
            _ttft_mark("mm_proc", _mm_t1, rid=getattr(request_obj, "rid", None))
            _mm_t2 = _time.perf_counter()

        items = []

        input_ids = ret["input_ids"].flatten().tolist()
        if "pixel_values" in ret:
            items += [
                MultimodalDataItem(
                    pixel_values=ret["pixel_values"],
                    image_grid_thws=torch.concat([ret["image_grid_thw"]]),
                    # TODO
                    video_grid_thws=None,
                    second_per_grid_ts=ret.get("second_per_grid_ts", None),
                    modality=Modality.IMAGE,
                )
            ]

        mrope_positions, mrope_position_delta = MRotaryEmbedding.get_rope_index(
            spatial_merge_size=self.hf_config.vision_config.spatial_merge_size,
            image_token_id=self.image_token_id,
            video_token_id=self.video_token_id,
            vision_start_token_id=self.vision_start_token_id,
            model_type=self.hf_config.model_type,
            tokens_per_second=getattr(
                self.hf_config.vision_config, "tokens_per_second", None
            ),
            input_ids=torch.tensor(input_ids).unsqueeze(0),
            image_grid_thw=ret.get("image_grid_thw", None),
            video_grid_thw=ret.get("video_grid_thw", None),
            second_per_grid_ts=ret.get("second_per_grid_ts", None),
        )
        mrope_positions = mrope_positions.squeeze(1)
        if _TTFT_PROF:
            _ttft_mark("mm_rope", _mm_t2, rid=getattr(request_obj, "rid", None))

        return {
            "input_ids": input_ids,
            "mm_items": items,
            "im_start_id": self.IM_START_TOKEN_ID,
            "im_end_id": self.IM_END_TOKEN_ID,
            "im_token_id": self.image_token_id,
            "video_token_id": self.video_token_id,
            "mrope_positions": mrope_positions,
            "mrope_position_delta": mrope_position_delta,
        }
