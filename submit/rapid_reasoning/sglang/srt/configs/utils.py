from typing import Type

from transformers import (
    AutoImageProcessor,
    AutoProcessor,
    BaseImageProcessor,
    PretrainedConfig,
    ProcessorMixin,
)


def register_image_processor(
    config: Type[PretrainedConfig], image_processor: Type[BaseImageProcessor]
):
    """
    register customized hf image processor while removing hf impl
    """
    AutoImageProcessor.register(config, None, image_processor, None, exist_ok=True)


def register_processor(config: Type[PretrainedConfig], processor: Type[ProcessorMixin]):
    """
    register customized hf processor while removing hf impl
    """
    AutoProcessor.register(config, processor, exist_ok=True)

import os
import hashlib
import logging

logger = logging.getLogger(__name__)

class SailConfig:
    """Dataclass which contains the SAIL strategy of the engine."""

    acext_version: int = 1050100
    """ acext mini version """

    acext_num_tokens: int = 6144
    """ ACEXT_NUM_TOKENS_LIMIT """

    def __init__(self, acext_num_tokens = 6144):
        self.acext_num_tokens = acext_num_tokens
        self.check_version_compatibility()
        self.set_token_limit()

    def set_token_limit(self):
        if 'ACEXT_NUM_TOKENS_LIMIT' not in os.environ:
            os.environ['ACEXT_NUM_TOKENS_LIMIT']=str(self.acext_num_tokens)
        logger.warning(f"acext token limit: {os.environ['ACEXT_NUM_TOKENS_LIMIT']}")


    def check_version_compatibility(self):
        from sgl_kernel import acext_get_version
        current_ver = acext_get_version()
        if current_ver < self.acext_version:
            logger.warning(f"acext version {current_ver} don't satisify minimum version {self.acext_version}. Fallback to tritonMoE")
            os.environ['USE_ACEXT_CUDA']="0"
        else:
            logger.warning(f"Current acext version: {current_ver}")

