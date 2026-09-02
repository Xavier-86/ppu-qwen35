# Minimal backport shim for the v0.5.x piecewise-compilation package.
# The 0.4.6 base has no torch piecewise compilation support; these shims
# provide the import surface used by the Qwen3-Next / Qwen3.5 hybrid
# linear-attention code paths with no-op behavior.
