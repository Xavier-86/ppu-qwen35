"""PPU device-memory IPC transport for batch-one multimodal requests.

The tokenizer process already produces ``pixel_values`` on the PPU. Plain
``pickle`` serializes the full tensor through host memory before ZMQ sends the
request. This module copies the tensor into a fixed device ring and uses
PyTorch's CUDA-IPC reducer (backed by HGGC on PPU), so pickle contains only
allocation and event metadata.

The competition wrapper submits one request at a time. Multiple slots tolerate
short producer/consumer overlap; inputs larger than one slot fall back to the
ordinary transport rather than changing request semantics.
"""

from __future__ import annotations

import os
from typing import Any

import torch
from torch.multiprocessing.reductions import reduce_tensor

# BACKPORT-PPU: PyTorch-for-SAIL maps the CUDA IPC reducer to HGGC IPC.


class _DeviceIpcTensor:
    """Pickle envelope that rebuilds directly as a CUDA/PPU tensor."""

    __slots__ = ("tensor",)

    def __init__(self, tensor: torch.Tensor) -> None:
        self.tensor = tensor

    def __reduce_ex__(self, protocol: int):
        del protocol
        return reduce_tensor(self.tensor)


class DeviceIpcRing:
    """Fixed device allocation shared repeatedly with the scheduler process."""

    def __init__(self) -> None:
        self.enabled = os.environ.get("SGLANG_DEVICE_IPC", "1") == "1"
        self.slot_bytes = int(
            os.environ.get("SGLANG_DEVICE_IPC_SLOT_BYTES", str(8 * 1024 * 1024))
        )
        self.slot_count = int(os.environ.get("SGLANG_DEVICE_IPC_SLOTS", "2"))
        if self.slot_bytes <= 0 or self.slot_count <= 0:
            raise ValueError("device IPC slot size and count must be positive")
        self._storage: torch.Tensor | None = None
        self._next_slot = 0

    def _ensure_storage(self, device: torch.device) -> torch.Tensor:
        if self._storage is None:
            # One large allocation gives all slots the same IPC handle. The
            # receiver-side PyTorch IPC cache therefore opens it only once.
            self._storage = torch.empty(
                self.slot_count * self.slot_bytes,
                dtype=torch.uint8,
                device=device,
            )
        return self._storage

    def _stage_tensor(self, tensor: torch.Tensor) -> _DeviceIpcTensor | None:
        if (
            not self.enabled
            or tensor.device.type != "cuda"
            or tensor.requires_grad
            or not tensor.is_contiguous()
        ):
            return None

        num_bytes = tensor.numel() * tensor.element_size()
        if num_bytes == 0 or num_bytes > self.slot_bytes:
            return None

        storage = self._ensure_storage(tensor.device)
        slot = self._next_slot
        self._next_slot = (slot + 1) % self.slot_count
        start = slot * self.slot_bytes
        byte_view = storage.narrow(0, start, num_bytes)
        staged = byte_view.view(tensor.dtype).view(tensor.shape)
        staged.copy_(tensor, non_blocking=True)
        return _DeviceIpcTensor(staged)

    def wrap_multimodal_inputs(self, mm_inputs: dict[str, Any] | None) -> bool:
        """Replace supported pixel tensors with IPC envelopes in place."""
        if not self.enabled or not mm_inputs:
            return False

        wrapped_any = False
        for item in mm_inputs.get("mm_items", []) or []:
            tensor = getattr(item, "pixel_values", None)
            if not isinstance(tensor, torch.Tensor):
                continue
            wrapped = self._stage_tensor(tensor)
            if wrapped is not None:
                item.pixel_values = wrapped
                wrapped_any = True
        return wrapped_any
