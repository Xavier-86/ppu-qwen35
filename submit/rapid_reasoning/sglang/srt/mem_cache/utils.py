# BACKPORT: minimal subset of sglang v0.5.9 srt/mem_cache/utils.py.
# Only maybe_init_custom_mem_pool is provided (used by MambaPool).
from typing import Any, Optional, Tuple


def maybe_init_custom_mem_pool(
    device: str,
) -> Tuple[bool, Optional[Any], Optional[str]]:
    """
    Initialize custom memory pool based on environment variable.

    This function can be modified to support more features that require a custom memory pool.

    Args:
        device: The device to allocate memory on

    Returns:
        Tuple of (enable_custom_mem_pool, custom_mem_pool, custom_mem_pool_type)
    """
    # SLIM: removed mooncake disaggregation custom mem pool branch (fixed
    # Qwen3.5-2B config: no PD disaggregation; srt/disaggregation deleted)
    return False, None, None
