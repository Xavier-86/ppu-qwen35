"""Validate that the submit branch resolves participant code from dndx."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = PROJECT_ROOT / "runtime_manifest.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as input_file:
        for chunk in iter(lambda: input_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_file(relative_path: str) -> Path:
    path = PROJECT_ROOT / relative_path
    if not path.is_file():
        raise RuntimeError(f"missing bundled file: {relative_path}")
    return path


def _require_tree(relative_path: str) -> Path:
    path = PROJECT_ROOT / relative_path
    if not path.is_dir() or not any(path.iterdir()):
        raise RuntimeError(f"missing or empty bundled tree: {relative_path}")
    return path


def _check_symlinks() -> None:
    for path in PROJECT_ROOT.rglob("*"):
        if not path.is_symlink():
            continue
        target = path.resolve()
        if not target.is_relative_to(PROJECT_ROOT):
            raise RuntimeError(f"external symlink: {path} -> {target}")


def _check_source_paths() -> None:
    forbidden = ("/home/", "/mnt/data/")
    active_roots = (
        PROJECT_ROOT / "evaluation_wrapper.py",
        PROJECT_ROOT / "benchmark_public.py",
        PROJECT_ROOT / "rapid_reasoning" / "sglang",
    )
    for root in active_roots:
        paths = [root] if root.is_file() else root.rglob("*.py")
        for path in paths:
            text = path.read_text(encoding="utf-8", errors="replace")
            for marker in forbidden:
                if marker in text:
                    relative = path.relative_to(PROJECT_ROOT)
                    raise RuntimeError(f"host-specific path {marker!r} in {relative}")


def _check_local_imports() -> dict[str, str]:
    bundle_root = PROJECT_ROOT / "rapid_reasoning"
    local_paths = (
        str(bundle_root / "runtime_packages"),
        str(bundle_root),
    )
    sys.path[:] = [path for path in sys.path if path not in local_paths]
    sys.path[:0] = local_paths

    origins = {}
    for package_name in ("sglang", "sgl_kernel", "triton"):
        module = importlib.import_module(package_name)
        origin = Path(module.__file__).resolve()
        if not origin.is_relative_to(bundle_root):
            raise RuntimeError(f"{package_name} resolved outside bundle: {origin}")
        origins[package_name] = str(origin.relative_to(PROJECT_ROOT))
    return origins


def check_submission(import_modules: bool) -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    components = manifest["bundled_components"]
    binary_hashes = {}
    for name, component in components.items():
        relative_path = component["path"]
        _require_tree(relative_path)
        binary_name = component.get("binary")
        if not binary_name:
            continue
        binary_path = _require_file(f"{relative_path}/{binary_name}")
        actual_hash = _sha256(binary_path)
        if actual_hash != component["binary_sha256"]:
            raise RuntimeError(f"{name} checksum mismatch: {actual_hash}")
        _require_file(component["license"])
        binary_hashes[name] = actual_hash
    _check_symlinks()
    _check_source_paths()

    versions = {}
    for distribution_name, expected in manifest["platform_abi"].items():
        actual = importlib.metadata.version(distribution_name)
        if actual != expected:
            raise RuntimeError(
                f"{distribution_name} ABI mismatch: expected {expected}, got {actual}"
            )
        versions[distribution_name] = actual

    origins = _check_local_imports() if import_modules else {}
    return {
        "status": "ok",
        "project_root": str(PROJECT_ROOT),
        "platform_abi": versions,
        "local_imports": origins,
        "binary_sha256": binary_hashes,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-imports",
        action="store_true",
        help="Only validate files, checksums and installed distribution versions.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    print(json.dumps(check_submission(not arguments.skip_imports), indent=2))
