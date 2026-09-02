# Adapted from https://raw.githubusercontent.com/vllm-project/vllm/v0.5.5/vllm/model_executor/layers/quantization/__init__.py
# SLIM: the fixed Qwen3.5-2B runtime is bf16 with no quantization. All
# quantized method implementations (fp8/int8 kernels, awq, gptq, modelopt,
# w8a8_*, blockwise_int8, moe_wna16, deep_gemm, compressed-tensors) and the
# vllm fallback monkey-patching are removed. Only base_config and an empty
# method registry remain; the unquantized methods live in
# sglang.srt.layers.linear / sglang.srt.layers.vocab_parallel_embedding.
from typing import Dict, Type

from sglang.srt.layers.quantization.base_config import (
    QuantizationConfig,
    QuantizeMethodBase,
)

# No quantization methods are supported: the runtime is fixed to bf16.
QUANTIZATION_METHODS: Dict[str, Type[QuantizationConfig]] = {}


def get_quantization_config(quantization: str) -> Type[QuantizationConfig]:
    raise ValueError(
        f"Invalid quantization method: {quantization}. "
        "This build only supports unquantized (bf16) models."
    )


__all__ = [
    "QuantizationConfig",
    "QuantizeMethodBase",
    "QUANTIZATION_METHODS",
    "get_quantization_config",
]
