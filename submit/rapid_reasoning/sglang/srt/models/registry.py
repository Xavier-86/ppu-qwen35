# Adapted from https://github.com/vllm-project/vllm/blob/v0.6.4.post1/vllm/model_executor/models/registry.py

import logging
from dataclasses import dataclass, field
from typing import AbstractSet, Dict, List, Optional, Tuple, Type, Union

import torch.nn as nn

logger = logging.getLogger(__name__)


@dataclass
class _ModelRegistry:
    # Keyed by model_arch
    models: Dict[str, Union[Type[nn.Module], str]] = field(default_factory=dict)

    def get_supported_archs(self) -> AbstractSet[str]:
        return self.models.keys()

    def _raise_for_unsupported(self, architectures: List[str]):
        all_supported_archs = self.get_supported_archs()

        if any(arch in all_supported_archs for arch in architectures):
            raise ValueError(
                f"Model architectures {architectures} failed "
                "to be inspected. Please check the logs for more details."
            )

        raise ValueError(
            f"Model architectures {architectures} are not supported for now. "
            f"Supported architectures: {all_supported_archs}"
        )

    def _try_load_model_cls(self, model_arch: str) -> Optional[Type[nn.Module]]:
        if model_arch not in self.models:
            return None

        return self.models[model_arch]

    def _normalize_archs(
        self,
        architectures: Union[str, List[str]],
    ) -> List[str]:
        if isinstance(architectures, str):
            architectures = [architectures]
        if not architectures:
            logger.warning("No model architectures are specified")

        return architectures

    def resolve_model_cls(
        self,
        architectures: Union[str, List[str]],
    ) -> Tuple[Type[nn.Module], str]:
        architectures = self._normalize_archs(architectures)

        for arch in architectures:
            model_cls = self._try_load_model_cls(arch)
            if model_cls is not None:
                return (model_cls, arch)

        return self._raise_for_unsupported(architectures)


def import_model_classes():
    """Return the model classes supported by this fixed-model submission.

    The upstream registry scans and imports every module under ``srt.models``.
    That is useful for a general serving distribution, but it pulls in many
    unrelated architectures (and their optional dependencies) before the
    first request.  The submission only serves the Qwen3.5-2B target and its
    MTP draft, so keep the registry explicit and deterministic.
    """
    from sglang.srt.models.qwen3_5 import Qwen3_5ForConditionalGeneration
    from sglang.srt.models.qwen3_5_mtp import Qwen3_5MTPForCausalLM

    return {
        Qwen3_5ForConditionalGeneration.__name__: Qwen3_5ForConditionalGeneration,
        Qwen3_5MTPForCausalLM.__name__: Qwen3_5MTPForCausalLM,
    }


ModelRegistry = _ModelRegistry(import_model_classes())
