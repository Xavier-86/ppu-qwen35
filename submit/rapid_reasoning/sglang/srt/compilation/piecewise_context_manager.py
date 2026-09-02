# Backport shim (no-op) for sglang.srt.compilation.piecewise_context_manager.
# Without piecewise compilation there is never an active forward context,
# so get_forward_context() always returns None and callers take their
# non-compiled code path.
from contextlib import contextmanager


def get_forward_context():
    return None


@contextmanager
def set_forward_context(forward_batch=None, *args, **kwargs):
    yield None
