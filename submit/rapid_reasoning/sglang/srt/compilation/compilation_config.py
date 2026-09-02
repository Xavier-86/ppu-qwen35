# Backport shim (no-op) for sglang.srt.compilation.compilation_config.
# Piecewise compilation is not supported on the 0.4.6 base; split-op
# registration is recorded but never consumed.
from typing import Callable, Optional

SPLIT_OPS = []


def register_split_op(op_name: Optional[str] = None):
    def decorator(op_func: Callable):
        name = op_name or op_func.__name__
        SPLIT_OPS.append(f"sglang.{name}")
        return op_func

    return decorator
