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
"""Utilities for Huggingface Transformers."""

import contextlib
import os
import warnings
from pathlib import Path
from typing import Dict, Optional, Type, Union

from huggingface_hub import snapshot_download
from transformers import (
    AutoConfig,
    AutoImageProcessor,
    AutoProcessor,
    AutoTokenizer,
    PretrainedConfig,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
)
from transformers.models.qwen2_5_vl.processing_qwen2_5_vl import (
    Qwen2_5_VLProcessor,
)
from transformers.models.auto.modeling_auto import MODEL_FOR_CAUSAL_LM_MAPPING_NAMES

from sglang.srt.configs import (
    Qwen3NextConfig,
    Qwen3VLConfig,
    Qwen3_5Config,
    Qwen3_5MoeConfig,
)
# SLIM: removed remote connector import (model path is always a local dir)

_CONFIG_REGISTRY: Dict[str, Type[PretrainedConfig]] = {
    Qwen3NextConfig.model_type: Qwen3NextConfig,
    Qwen3VLConfig.model_type: Qwen3VLConfig,
    Qwen3_5Config.model_type: Qwen3_5Config,
    Qwen3_5MoeConfig.model_type: Qwen3_5MoeConfig,
}

for name, cls in _CONFIG_REGISTRY.items():
    with contextlib.suppress(ValueError):
        AutoConfig.register(name, cls)


def download_from_hf(model_path: str):
    if os.path.exists(model_path):
        return model_path

    return snapshot_download(model_path, allow_patterns=["*.json", "*.bin", "*.model"])


def get_config(
    model: str,
    trust_remote_code: bool,
    revision: Optional[str] = None,
    model_override_args: Optional[dict] = None,
    **kwargs,
):
    is_gguf = check_gguf_file(model)
    if is_gguf:
        kwargs["gguf_file"] = model
        model = Path(model).parent

    config = AutoConfig.from_pretrained(
        model, trust_remote_code=trust_remote_code, revision=revision, **kwargs
    )

    # FIXME: Pour contents of janus-pro's langauge_config to first-level
    if isinstance(model, str) and model.lower().startswith("deepseek-ai/janus-pro"):
        assert hasattr(config, "language_config")
        for key, val in config.language_config.__dict__.items():
            setattr(config, key, val)
        setattr(config, "architectures", ["MultiModalityCausalLM"])

    if config.model_type in _CONFIG_REGISTRY:
        config_class = _CONFIG_REGISTRY[config.model_type]
        config = config_class.from_pretrained(model, revision=revision)
        # NOTE(HandH1998): Qwen2VL requires `_name_or_path` attribute in `config`.
        setattr(config, "_name_or_path", model)
    if model_override_args:
        config.update(model_override_args)

    # Special architecture mapping check for GGUF models
    if is_gguf:
        if config.model_type not in MODEL_FOR_CAUSAL_LM_MAPPING_NAMES:
            raise RuntimeError(f"Can't get gguf config for {config.model_type}.")
        model_type = MODEL_FOR_CAUSAL_LM_MAPPING_NAMES[config.model_type]
        config.update({"architectures": [model_type]})

    return config


# Models don't use the same configuration key for determining the maximum
# context length.  Store them here so we can sanely check them.
# NOTE: The ordering here is important. Some models have two of these and we
# have a preference for which value gets used.
CONTEXT_LENGTH_KEYS = [
    "max_sequence_length",
    "seq_length",
    "max_seq_len",
    "model_max_length",
    "max_position_embeddings",
]


def get_context_length(config):
    """Get the context length of a model from a huggingface model configs."""
    text_config = config
    rope_scaling = getattr(text_config, "rope_scaling", None)
    if rope_scaling:
        rope_scaling_factor = rope_scaling.get("factor", 1)
        if "original_max_position_embeddings" in rope_scaling:
            rope_scaling_factor = 1
        if rope_scaling.get("rope_type", None) == "llama3":
            rope_scaling_factor = 1
    else:
        rope_scaling_factor = 1

    for key in CONTEXT_LENGTH_KEYS:
        val = getattr(text_config, key, None)
        if val is not None:
            return int(rope_scaling_factor * val)
    return 2048


# A fast LLaMA tokenizer with the pre-processed `tokenizer.json` file.
_FAST_LLAMA_TOKENIZER = "hf-internal-testing/llama-tokenizer"


def get_tokenizer(
    tokenizer_name: str,
    *args,
    tokenizer_mode: str = "auto",
    trust_remote_code: bool = False,
    tokenizer_revision: Optional[str] = None,
    **kwargs,
) -> Union[PreTrainedTokenizer, PreTrainedTokenizerFast]:
    """Gets a tokenizer for the given model name via Huggingface."""
    if tokenizer_mode == "slow":
        if kwargs.get("use_fast", False):
            raise ValueError("Cannot use the fast tokenizer in slow tokenizer mode.")
        kwargs["use_fast"] = False

    is_gguf = check_gguf_file(tokenizer_name)
    if is_gguf:
        kwargs["gguf_file"] = tokenizer_name
        tokenizer_name = Path(tokenizer_name).parent

    # SLIM: removed remote URL pull branch (model path is always a local dir)

    try:
        tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_name,
            *args,
            trust_remote_code=trust_remote_code,
            tokenizer_revision=tokenizer_revision,
            clean_up_tokenization_spaces=False,
            **kwargs,
        )
    except TypeError as e:
        # The LLaMA tokenizer causes a protobuf error in some environments.
        err_msg = (
            "Failed to load the tokenizer. If you are using a LLaMA V1 model "
            f"consider using '{_FAST_LLAMA_TOKENIZER}' instead of the "
            "original tokenizer."
        )
        raise RuntimeError(err_msg) from e
    except ValueError as e:
        # If the error pertains to the tokenizer class not existing or not
        # currently being imported, suggest using the --trust-remote-code flag.
        if not trust_remote_code and (
            "does not exist or is not currently imported." in str(e)
            or "requires you to execute the tokenizer file" in str(e)
        ):
            err_msg = (
                "Failed to load the tokenizer. If the tokenizer is a custom "
                "tokenizer not yet available in the HuggingFace transformers "
                "library, consider setting `trust_remote_code=True` in LLM "
                "or using the `--trust-remote-code` flag in the CLI."
            )
            raise RuntimeError(err_msg) from e
        else:
            raise e

    if not isinstance(tokenizer, PreTrainedTokenizerFast):
        warnings.warn(
            "Using a slow tokenizer. This might cause a significant "
            "slowdown. Consider using a fast tokenizer instead."
        )

    attach_additional_stop_token_ids(tokenizer)
    return tokenizer


def get_processor(
    tokenizer_name: str,
    *args,
    tokenizer_mode: str = "auto",
    trust_remote_code: bool = False,
    tokenizer_revision: Optional[str] = None,
    use_fast: Optional[bool] = True,
    **kwargs,
):
    # pop 'revision' from kwargs if present.
    revision = kwargs.pop("revision", tokenizer_revision)

    config = AutoConfig.from_pretrained(
        tokenizer_name,
        trust_remote_code=trust_remote_code,
        revision=revision,
        **kwargs,
    )

    # fix: for Qwen2-VL model, inject default 'size' if not provided.
    if config.model_type in {"qwen2_vl"}:
        if "size" not in kwargs:
            kwargs["size"] = {"shortest_edge": 3136, "longest_edge": 1003520}

    if config.model_type not in {"llava", "clip"}:
        kwargs["use_fast"] = use_fast

    # BACKPORT-PPU: transformers 4.51 does not ship Qwen3VLProcessor, so
    # AutoProcessor falls back to the raw tokenizer. Newer transformers return
    # a real Qwen3VLProcessor for qwen3_vl / qwen3_5; use it when available.
    if config.model_type in ("qwen3_vl", "qwen3_5"):
        processor = AutoProcessor.from_pretrained(
            tokenizer_name,
            *args,
            trust_remote_code=trust_remote_code,
            revision=revision,
            **kwargs,
        )
        if hasattr(processor, "image_processor"):
            attach_additional_stop_token_ids(getattr(processor, "tokenizer", processor))
            return processor
        # Fallback for older transformers: build a Qwen2.5-VL-compatible processor.
        # transformers 4.51 Qwen2VLImageProcessorFast.__init__ silently drops a
        # valid ``size`` dict (the ``else: size = self.size`` branch always
        # runs), so the model's preprocessor_config.json size bounds never
        # reach the processor. Only the min_pixels/max_pixels kwargs survive.
        # Forward them explicitly so small images are upscaled (and large ones
        # kept) exactly as the real Qwen3VLProcessor does on newer
        # transformers; otherwise image token counts shrink and accuracy drops.
        image_kwargs = {}
        if "size" not in kwargs:
            try:
                import json as _json
                import os as _os

                with open(
                    _os.path.join(tokenizer_name, "preprocessor_config.json")
                ) as _f:
                    _size = _json.load(_f).get("size") or {}
                if "shortest_edge" in _size:
                    image_kwargs["min_pixels"] = _size["shortest_edge"]
                if "longest_edge" in _size:
                    image_kwargs["max_pixels"] = _size["longest_edge"]
            except (OSError, ValueError):
                pass
        # transformers 4.51 smart_resize raises when an image edge is smaller
        # than patch_size*merge_size; the native Qwen3VL path on newer
        # transformers has no such raise and simply upscales tiny edges. Patch
        # both qwen2_vl variants to the 4.57 behavior so thin benchmark images
        # resize exactly like the real processor instead of crashing or
        # needing lossy black-padding.
        import math as _math

        from transformers.models.qwen2_vl import (
            image_processing_qwen2_vl as _q2v_slow,
        )
        from transformers.models.qwen2_vl import (
            image_processing_qwen2_vl_fast as _q2v_fast,
        )

        def _smart_resize_qwen3(height, width, factor, min_pixels, max_pixels):
            # Verbatim transformers>=4.57 smart_resize semantics.
            if max(height, width) / min(height, width) > 200:
                raise ValueError(
                    "absolute aspect ratio must be smaller than 200, got "
                    f"{max(height, width) / min(height, width)}"
                )
            h_bar = round(height / factor) * factor
            w_bar = round(width / factor) * factor
            if h_bar * w_bar > max_pixels:
                beta = _math.sqrt((height * width) / max_pixels)
                h_bar = max(factor, _math.floor(height / beta / factor) * factor)
                w_bar = max(factor, _math.floor(width / beta / factor) * factor)
            elif h_bar * w_bar < min_pixels:
                beta = _math.sqrt(min_pixels / (height * width))
                h_bar = _math.ceil(height * beta / factor) * factor
                w_bar = _math.ceil(width * beta / factor) * factor
            return h_bar, w_bar

        _q2v_slow.smart_resize = _smart_resize_qwen3
        _q2v_fast.smart_resize = _smart_resize_qwen3
        image_processor = AutoImageProcessor.from_pretrained(
            tokenizer_name,
            *args,
            trust_remote_code=trust_remote_code,
            revision=revision,
            **image_kwargs,
            **kwargs,
        )
        # BACKPORT-PPU: fast single-image _preprocess. The generic HF path
        # pays for make_flat_list_of_images, group_images_by_shape x2,
        # reorder_images x2, a per-image python loop and torch.stack even for
        # one image (~0.4-1 ms/request of pure host overhead, all inside
        # TTFT). The benchmark is strictly single-PIL-image; for that case we
        # run the identical op sequence on the batched (1,C,H,W) tensor
        # directly. Verified bitwise-identical to the generic path on 50
        # MMBench images (docs/profile_v2/fast_preprocess_verify.py).
        # Anything else (multi-image, numpy/torch input, explicit
        # input_data_format) falls back to the generic implementation.
        # SGLANG_MM_FAST_PREPROCESS=0 disables.
        import os as _os2

        if _os2.environ.get("SGLANG_MM_FAST_PREPROCESS", "1") == "1" and hasattr(
            image_processor, "_preprocess"
        ):
            import types as _types

            import torch as _torch
            from PIL import Image as _PILImage

            _orig_preprocess = image_processor._preprocess

            def _preprocess_single_fast(
                self,
                images,
                do_resize,
                size,
                interpolation,
                do_rescale,
                rescale_factor,
                do_normalize,
                image_mean,
                image_std,
                patch_size,
                temporal_patch_size,
                merge_size,
                do_convert_rgb,
                input_data_format,
                device,
            ):
                from transformers.image_transforms import ChannelDimension

                if (
                    not isinstance(images, _PILImage.Image)
                    or input_data_format not in (None, ChannelDimension.FIRST)
                ):
                    return _orig_preprocess(
                        images, do_resize, size, interpolation, do_rescale,
                        rescale_factor, do_normalize, image_mean, image_std,
                        patch_size, temporal_patch_size, merge_size,
                        do_convert_rgb, input_data_format, device,
                    )
                from torchvision.transforms.v2 import functional as _F

                image = images
                if do_convert_rgb:
                    image = self.convert_to_rgb(image)
                # (1,C,H,W) uint8, matching the generic grouped/stacked input
                stacked = _F.pil_to_tensor(image).unsqueeze(0)
                if device is not None:
                    stacked = stacked.to(device)
                height, width = stacked.shape[-2], stacked.shape[-1]
                resized_height, resized_width = height, width
                if do_resize:
                    resized_height, resized_width = _q2v_fast.smart_resize(
                        height,
                        width,
                        factor=patch_size * merge_size,
                        min_pixels=size["shortest_edge"],
                        max_pixels=size["longest_edge"],
                    )
                    stacked = _F.resize(
                        stacked,
                        size=(resized_height, resized_width),
                        interpolation=interpolation,
                    )
                stacked = self.rescale_and_normalize(
                    stacked, do_rescale, rescale_factor, do_normalize,
                    image_mean, image_std,
                )
                patches = stacked
                if patches.shape[0] % temporal_patch_size != 0:
                    repeats = patches[-1].unsqueeze(0).repeat(
                        temporal_patch_size - 1, 1, 1, 1
                    )
                    patches = _torch.cat([patches, repeats], dim=0)
                channel = patches.shape[1]
                grid_t = patches.shape[0] // temporal_patch_size
                grid_h, grid_w = (
                    resized_height // patch_size,
                    resized_width // patch_size,
                )
                patches = patches.view(
                    grid_t, temporal_patch_size, channel,
                    grid_h // merge_size, merge_size, patch_size,
                    grid_w // merge_size, merge_size, patch_size,
                )
                patches = patches.permute(0, 3, 6, 4, 7, 2, 1, 5, 8)
                flatten_patches = patches.reshape(
                    grid_t * grid_h * grid_w,
                    channel * temporal_patch_size * patch_size * patch_size,
                )
                return flatten_patches, (grid_t, grid_h, grid_w)

            image_processor._preprocess = _types.MethodType(
                _preprocess_single_fast, image_processor
            )

        tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_name,
            *args,
            trust_remote_code=trust_remote_code,
            revision=revision,
            **kwargs,
        )
        processor = Qwen2_5_VLProcessor(
            image_processor=image_processor, tokenizer=tokenizer
        )
        attach_additional_stop_token_ids(tokenizer)
        return processor

    processor = AutoProcessor.from_pretrained(
        tokenizer_name,
        *args,
        trust_remote_code=trust_remote_code,
        revision=revision,
        **kwargs,
    )

    attach_additional_stop_token_ids(getattr(processor, "tokenizer", processor))
    return processor


def attach_additional_stop_token_ids(tokenizer):
    # Special handling for stop token <|eom_id|> generated by llama 3 tool use.
    if "<|eom_id|>" in tokenizer.get_added_vocab():
        tokenizer.additional_stop_token_ids = set(
            [tokenizer.get_added_vocab()["<|eom_id|>"]]
        )
    else:
        tokenizer.additional_stop_token_ids = None


def check_gguf_file(model: Union[str, os.PathLike]) -> bool:
    """Check if the file is a GGUF model."""
    model = Path(model)
    if not model.is_file():
        return False
    elif model.suffix == ".gguf":
        return True

    with open(model, "rb") as f:
        header = f.read(4)
    return header == b"GGUF"
