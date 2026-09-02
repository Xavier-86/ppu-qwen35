import torch
from typing import Optional
import os

libth_op_default_path = "/usr/local/PPU_SDK/lib/th_op/libth_op.so"
libth_op = os.environ.get("ACEXT_THOP_LIB_PATH", libth_op_default_path)

try:
    torch.classes.load_library(libth_op)
    acext_int8_gemm = torch.ops.int8_gemm_ops.int8_gemm
    grouped_gemm_nt_masked = torch.ops.moe_unit_ops.grouped_gemm_nt_masked
    print(f"[ACEXT] [INFO]: load libthop.so success.")
except Exception:
    acext_int8_gemm = None
    grouped_gemm_nt_masked = None
    print(f"[ACEXT] [Warning]: load libthop.so failed, fallback triton backend.")

def acext_fusedmoe_warpper(
    hidden_state: torch.Tensor,
    w1: torch.Tensor,
    w2: torch.Tensor,
    topk_weights: torch.Tensor,
    topk_sids: torch.Tensor,
    output_hidden_states: torch.Tensor,
    expanded_source_row_to_dest_size: int,
    w1_scale: torch.Tensor,
    w2_scale: torch.Tensor,
    w1_zp: torch.Tensor,
    w2_zp: torch.Tensor,
    a1_scale: torch.Tensor,
    a2_scale: torch.Tensor,
    use_int8_w8a8: bool,
    ep_rank: int = 0,
    ep_size: int = 1
) -> None:
    try:
        with hidden_state.device as device:
            torch.ops.sgl_kernel.acext_fusedmoe_warpper(
                hidden_state,
                w1,
                w2,
                topk_weights,
                topk_sids,
                output_hidden_states,
                expanded_source_row_to_dest_size,
                w1_scale,
                w2_scale,
                w1_zp,
                w2_zp,
                a1_scale,
                a2_scale,
                use_int8_w8a8,
                ep_rank,
                ep_size)
    except AttributeError as ae:
        print(f"[ACEXT] [Error]: acext_fusedmoe_warpper is not found, assert.")
        raise ae
    except Exception as e:
        print(f"[ACEXT] [Warning]: {type(e).__name__}: {str(e)}")

def get_acext_fusedmoe_status_wrapper(
    hidden_state: torch.Tensor,
    w1: torch.Tensor,
    w2: torch.Tensor,
    topk_weights: torch.Tensor,
    topk_sids: torch.Tensor,
    output_hidden_states: torch.Tensor,
    expanded_source_row_to_dest_size: int,
    w1_scale: torch.Tensor,
    w2_scale: torch.Tensor,
    w1_zp: torch.Tensor,
    w2_zp: torch.Tensor,
    a1_scale: torch.Tensor,
    a2_scale: torch.Tensor,
    ep_rank: int = 0,
    ep_size: int = 1,
    q_type: int = 0
) -> int:
    try:
        with hidden_state.device as device:
            status = torch.ops.sgl_kernel.get_acext_fusedmoe_status_wrapper(
                hidden_state,
                w1,
                w2,
                topk_weights,
                topk_sids,
                output_hidden_states,
                expanded_source_row_to_dest_size,
                w1_scale,
                w2_scale,
                w1_zp,
                w2_zp,
                a1_scale,
                a2_scale,
                ep_rank,
                ep_size,
                q_type)
    except AttributeError:
        print(f"[ACEXT] [Warning]: get_acext_fusedmoe_status_wrapper is not found, so skip it.")
        status = -1
    except Exception as e:
        print(f"[ACEXT] [Warning]: {type(e).__name__}: {str(e)}")
        status = -2
    return status

def acext_get_version() -> int:
    try:
        status  = torch.ops.sgl_kernel.acext_get_version()
    except AttributeError:
        print(f"[ACEXT] [Warning]: acext_get_version is not found, so disable acext.")
        status = -1
    except Exception as e:
        print(f"[ACEXT] [Warning]: {type(e).__name__}: {str(e)}")
        status = -2
    return status