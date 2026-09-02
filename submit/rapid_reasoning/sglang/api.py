"""Public APIs of the language."""

# SLIM: removed the sglang.lang frontend language APIs (function, gen,
# select, Runtime, choices, ...); only Engine is kept for the fixed
# Qwen3.5-2B inference path.


def Engine(*args, **kwargs):
    # Avoid importing unnecessary dependency
    from sglang.srt.entrypoints.engine import Engine

    return Engine(*args, **kwargs)
