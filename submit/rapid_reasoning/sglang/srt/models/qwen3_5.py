# Copyright 2025 Qwen Team
# Copyright 2025 SGLang Team
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Inference-only Qwen3.5 model and Qwen3.5 MoE model compatible with HuggingFace weights."""

import logging
import os
from functools import lru_cache
from typing import Iterable, Optional, Set, Tuple, Union

import torch
import torch.nn as nn
from einops import rearrange

# Model Executor
from sglang.srt.compilation.piecewise_context_manager import get_forward_context

# Configs
from sglang.srt.configs.qwen3_5 import (
    Qwen3_5Config,
    Qwen3_5TextConfig,
)

# Distributed
from sglang.srt.distributed import get_pp_group
# SLIM: removed eplb imports (fixed Qwen3.5-2B config: dense model, no MoE)

# Layers - Attention
from sglang.srt.layers.activation import SiluAndMul
from sglang.srt.layers.attention.fla.layernorm_gated import RMSNorm as RMSNormGated
from sglang.srt.layers.attention.mamba.mamba import mamba_v2_sharded_weight_loader
from sglang.srt.layers.communicator import LayerCommunicator, LayerScatterModes
from sglang.srt.layers.dp_attention import (
    get_attention_tp_rank,
    get_attention_tp_size,
    is_dp_attention_enabled,
)

# Layers - Others
from sglang.srt.layers.layernorm import GemmaRMSNorm

# Layers - Linear
from sglang.srt.layers.linear import (
    ColumnParallelLinear,
    MergedColumnParallelLinear,
    QKVParallelLinear,
    RowParallelLinear,
)
# SLIM: removed FusedMoE import (fixed Qwen3.5-2B config: dense model, no MoE)
from sglang.srt.layers.quantization.base_config import QuantizationConfig
from sglang.srt.layers.radix_attention import RadixAttention
from sglang.srt.layers.radix_linear_attention import RadixLinearAttention
from sglang.srt.layers.rotary_embedding import get_rope
from sglang.srt.layers.vocab_parallel_embedding import VocabParallelEmbedding
# SLIM: removed get_is_capture_mode import (fixed Qwen3.5-2B config: CUDA graph
# capture always disabled); the capture-mode branch is folded to the
# non-capture path below.
from sglang.srt.model_executor.forward_batch_info import ForwardBatch, PPProxyTensors
from sglang.srt.model_loader.weight_utils import (
    default_weight_loader,
    sharded_weight_loader,
)

# SLIM: removed qwen2_moe / qwen3_next imports (fixed Qwen3.5-2B config: dense
# model); Qwen2MoeMLP and gdn_with_output are inlined in this file.

# Models
from sglang.srt.models.qwen3_vl import Qwen3VLForConditionalGeneration

# Utils
from sglang.srt.utils import add_prefix, is_cuda, is_npu, make_layers, set_weight_attrs
from sglang.srt.hf_transformers_utils import get_processor  # BACKPORT: was sglang.srt.utils.hf_transformers_utils in v0.5.9

logger = logging.getLogger(__name__)
_is_cuda = is_cuda()
_is_npu = is_npu()

if _is_cuda:
    import triton
    import triton.language as tl

# BACKPORT-PPU: decode-hot-path micro fusions (candidate C follow-ups).
# All three replicate eager bf16 opmath rounding (fp32 compute, RNE round
# after each op) or are pure copies, and are bit-exact vs the eager path
# by unit test. Each is individually gated, default on, with eager fallback.
# 1) SGLANG_FUSED_ATTN_GATE: sigmoid(gate) + attn*gate in one launch.
_FUSED_ATTN_GATE = os.environ.get("SGLANG_FUSED_ATTN_GATE", "1") == "1"
# 2) SGLANG_FUSED_BA_PROJ: in_proj_a/in_proj_b (two [2048->16] GEMMs plus two
# acblas reduction kernels per GDN layer) merged into one [2048->32] GEMM.
_FUSED_BA_PROJ = os.environ.get("SGLANG_FUSED_BA_PROJ", "1") == "1"
# 3) SGLANG_FUSED_QKG_NORM: gather the strided gated-Q/K/V projection slices,
# copy the attention gate, and apply both 256-wide Gemma RMSNorms in one
# launch.  This removes four materialization copies and one norm launch per
# full-attention layer in the fixed Qwen3.5-2B decode/verify shapes.
_FUSED_QKG_MODE = os.environ.get("SGLANG_FUSED_QKG_NORM", "1").strip().lower()
_FUSED_QKG_NORM = _FUSED_QKG_MODE in ("1", "gather")
try:
    _FUSED_QKG_NUM_WARPS = int(os.environ.get("SGLANG_QKG_NUM_WARPS", "4"))
except ValueError as exc:
    raise ValueError("SGLANG_QKG_NUM_WARPS must be an integer") from exc
if _FUSED_QKG_NUM_WARPS not in (2, 4, 8):
    raise ValueError(f"Unsupported SGLANG_QKG_NUM_WARPS={_FUSED_QKG_NUM_WARPS}")

if _is_cuda:

    @triton.jit
    def _sigmoid_gate_mul_kernel(
        attn,
        gate,
        out,
        numel,
        BLOCK: tl.constexpr,
    ):
        pid = tl.program_id(0)
        offs = pid * BLOCK + tl.arange(0, BLOCK)
        mask = offs < numel
        g = tl.load(gate + offs, mask=mask)
        a = tl.load(attn + offs, mask=mask)
        # eager: sigmoid in fp32 -> RNE to bf16; mul in fp32 -> RNE to bf16
        s = tl.sigmoid(g.to(tl.float32)).to(tl.bfloat16)
        o = (a.to(tl.float32) * s.to(tl.float32)).to(tl.bfloat16)
        tl.store(out + offs, o, mask=mask)

    @triton.jit
    def _fused_qkg_norm_kernel(
        q_gate,
        k,
        v,
        q_out,
        k_out,
        v_out,
        gate_out,
        q_weight,
        k_weight,
        q_gate_stride_t,
        q_gate_stride_h,
        k_stride_t,
        v_stride_t,
        num_kv_heads: tl.constexpr,
        eps: tl.constexpr,
        HEAD_DIM: tl.constexpr,
        APPLY_NORM: tl.constexpr,
    ):
        i_t = tl.program_id(0)
        i_h = tl.program_id(1)
        offs = tl.arange(0, HEAD_DIM)

        q_base = q_gate + i_t * q_gate_stride_t + i_h * q_gate_stride_h
        q = tl.load(q_base + offs).to(tl.float32)
        if APPLY_NORM:
            # Match FlashInfer/sgl-kernel GemmaRMSNorm's d=256 reduction:
            # 32 lanes each accumulate 8 adjacent values serially, followed
            # by a 32-lane tree reduction. A flat 256-wide tl.sum differs by
            # one bf16 ULP on rare boundary values.
            lanes = tl.arange(0, 32)
            q_lane_sum = tl.zeros((32,), tl.float32)
            for j in tl.static_range(0, 8):
                qv = tl.load(q_base + lanes * 8 + j).to(tl.float32)
                q_lane_sum += qv * qv
            q_var = tl.sum(q_lane_sum, axis=0) / HEAD_DIM
            q_scale = tl.rsqrt(q_var + eps)
            qw = tl.load(q_weight + offs).to(tl.float32)
            q_norm = (q * q_scale * (1.0 + qw)).to(tl.bfloat16)
        else:
            q_norm = q.to(tl.bfloat16)
        q_dst = q_out + (i_t * tl.num_programs(1) + i_h) * HEAD_DIM
        tl.store(q_dst + offs, q_norm)

        gate = tl.load(q_base + HEAD_DIM + offs)
        gate_dst = gate_out + (i_t * tl.num_programs(1) + i_h) * HEAD_DIM
        tl.store(gate_dst + offs, gate)

        if i_h < num_kv_heads:
            k_base = k + i_t * k_stride_t + i_h * HEAD_DIM
            kv = tl.load(k_base + offs).to(tl.float32)
            if APPLY_NORM:
                k_lane_sum = tl.zeros((32,), tl.float32)
                for j in tl.static_range(0, 8):
                    kval = tl.load(k_base + lanes * 8 + j).to(tl.float32)
                    k_lane_sum += kval * kval
                k_var = tl.sum(k_lane_sum, axis=0) / HEAD_DIM
                k_scale = tl.rsqrt(k_var + eps)
                kw = tl.load(k_weight + offs).to(tl.float32)
                k_norm = (kv * k_scale * (1.0 + kw)).to(tl.bfloat16)
            else:
                k_norm = kv.to(tl.bfloat16)
            k_dst = k_out + (i_t * num_kv_heads + i_h) * HEAD_DIM
            tl.store(k_dst + offs, k_norm)
            v_base = v + i_t * v_stride_t + i_h * HEAD_DIM
            vv = tl.load(v_base + offs)
            v_dst = v_out + (i_t * num_kv_heads + i_h) * HEAD_DIM
            tl.store(v_dst + offs, vv)

    def _fused_qkg_norm(
        q_gate: torch.Tensor,
        k: torch.Tensor,
        v: torch.Tensor,
        q_weight: torch.Tensor,
        k_weight: torch.Tensor,
        eps: float,
        apply_norm: bool,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        num_tokens, num_heads, doubled_head_dim = q_gate.shape
        head_dim = doubled_head_dim // 2
        num_kv_heads = k.shape[-1] // head_dim
        q_out = torch.empty(
            (num_tokens, num_heads * head_dim),
            dtype=q_gate.dtype,
            device=q_gate.device,
        )
        k_out = torch.empty_like(k, memory_format=torch.contiguous_format)
        v_out = torch.empty_like(v, memory_format=torch.contiguous_format)
        gate_out = torch.empty_like(q_out)
        _fused_qkg_norm_kernel[(num_tokens, num_heads)](
            q_gate,
            k,
            v,
            q_out,
            k_out,
            v_out,
            gate_out,
            q_weight,
            k_weight,
            q_gate.stride(0),
            q_gate.stride(1),
            k.stride(0),
            v.stride(0),
            num_kv_heads=num_kv_heads,
            eps=eps,
            HEAD_DIM=head_dim,
            APPLY_NORM=apply_norm,
            num_warps=_FUSED_QKG_NUM_WARPS,
        )
        return q_out, k_out, v_out, gate_out

cached_get_processor = lru_cache(get_processor)


# SLIM: Qwen2MoeMLP inlined from models/qwen2_moe.py (file deleted); it is the
# dense MLP used by the fixed Qwen3.5-2B model. Code copied verbatim.
class Qwen2MoeMLP(nn.Module):
    def __init__(
        self,
        hidden_size: int,
        intermediate_size: int,
        hidden_act: str,
        quant_config: Optional[QuantizationConfig] = None,
        reduce_results: bool = True,
        prefix: str = "",
    ) -> None:
        super().__init__()
        self.gate_up_proj = MergedColumnParallelLinear(
            hidden_size,
            [intermediate_size] * 2,
            bias=False,
            quant_config=quant_config,
            prefix=add_prefix("gate_up_proj", prefix),
        )
        self.down_proj = RowParallelLinear(
            intermediate_size,
            hidden_size,
            bias=False,
            quant_config=quant_config,
            reduce_results=reduce_results,
            prefix=add_prefix("down_proj", prefix),
        )
        if hidden_act != "silu":
            raise ValueError(
                f"Unsupported activation: {hidden_act}. "
                "Only silu is supported for now."
            )
        self.act_fn = SiluAndMul()

    # BACKPORT: accept the v0.5.9 call-site flags (qwen3_5 passes
    # forward_batch positionally plus use_reduce_scatter). Allreduce fusion
    # and reduce-scatter are not wired in this tree (TP-only paths), and
    # LayerCommunicator.should_use_reduce_scatter returns False here, so the
    # flags are consumed and ignored.
    def forward(
        self,
        x,
        should_allreduce_fusion: bool = False,
        use_reduce_scatter: bool = False,
    ):
        gate_up, _ = self.gate_up_proj(x)
        x = self.act_fn(gate_up)
        x, _ = self.down_proj(x)
        return x


# SLIM: gdn_with_output inlined from models/qwen3_next.py (file deleted).
# Code copied verbatim.
def gdn_with_output(
    hidden_states: torch.Tensor,
    output: torch.Tensor,
    layer_id: int,
) -> None:
    context = get_forward_context()
    forward_batch = context.forward_batch
    attention_layers = context.attention_layers
    attention_layer = attention_layers[layer_id]

    ret = attention_layer._forward(hidden_states, forward_batch)

    assert (
        output.numel() == ret.numel()
    ), f"Output tensor element mismatch: {output.numel()} != {ret.numel()}"

    output.view(ret.shape).copy_(ret)
    return


class Qwen3_5GatedDeltaNet(nn.Module):
    def __init__(
        self,
        config: Qwen3_5TextConfig,
        layer_id: int,
        quant_config: Optional[QuantizationConfig] = None,
        alt_stream: Optional[torch.cuda.Stream] = None,
        prefix: str = "",
    ) -> None:
        super().__init__()
        self.config = config
        self.attn_tp_rank = get_attention_tp_rank()
        self.attn_tp_size = get_attention_tp_size()
        self.hidden_size = config.hidden_size
        self.num_v_heads = config.linear_num_value_heads
        self.num_k_heads = config.linear_num_key_heads
        self.head_k_dim = config.linear_key_head_dim
        self.head_v_dim = config.linear_value_head_dim
        self.key_dim = self.head_k_dim * self.num_k_heads
        self.value_dim = self.head_v_dim * self.num_v_heads
        self.alt_stream = alt_stream

        self.conv_kernel_size = config.linear_conv_kernel_dim
        self.layer_id = layer_id
        self.activation = config.hidden_act
        self.layer_norm_epsilon = config.rms_norm_eps

        # Conv1d layer
        self.conv_dim = self.key_dim * 2 + self.value_dim
        self.conv1d = ColumnParallelLinear(
            input_size=self.conv_kernel_size,
            output_size=self.conv_dim,
            bias=False,
            quant_config=None,
            tp_rank=self.attn_tp_rank,
            tp_size=self.attn_tp_size,
            prefix=add_prefix("conv1d", prefix),
        )
        self.conv1d.weight.data = self.conv1d.weight.data.unsqueeze(1)

        # Split projection layers (following vLLM's implementation)
        # Instead of fused in_proj_qkvz and in_proj_ba, use separate layers
        self.in_proj_qkv = MergedColumnParallelLinear(
            input_size=self.hidden_size,
            output_sizes=[self.key_dim, self.key_dim, self.value_dim],
            bias=False,
            quant_config=quant_config,
            tp_rank=self.attn_tp_rank,
            tp_size=self.attn_tp_size,
            prefix=add_prefix("in_proj_qkv", prefix),
        )
        self.in_proj_z = ColumnParallelLinear(
            input_size=self.hidden_size,
            output_size=self.value_dim,
            bias=False,
            quant_config=quant_config,
            tp_rank=self.attn_tp_rank,
            tp_size=self.attn_tp_size,
            prefix=add_prefix("in_proj_z", prefix),
        )
        self.in_proj_b = ColumnParallelLinear(
            input_size=self.hidden_size,
            output_size=self.num_v_heads,
            bias=False,
            quant_config=quant_config,
            tp_rank=self.attn_tp_rank,
            tp_size=self.attn_tp_size,
            prefix=add_prefix("in_proj_b", prefix),
        )
        self.in_proj_a = ColumnParallelLinear(
            input_size=self.hidden_size,
            output_size=self.num_v_heads,
            bias=False,
            quant_config=quant_config,
            tp_rank=self.attn_tp_rank,
            tp_size=self.attn_tp_size,
            prefix=add_prefix("in_proj_a", prefix),
        )

        # BACKPORT-PPU: lazily concatenated [a; b] weight for the fused
        # single-GEMM path in _forward (SGLANG_FUSED_BA_PROJ). Not a
        # parameter; built once after weights are loaded, before any graph
        # capture warmup completes its first eager pass.
        self._ba_weight: Optional[torch.Tensor] = None

        # Conv1d weight loader setup
        query_key_settings = (self.key_dim, 0, False)
        value_settings = (self.value_dim, 0, False)

        delattr(self.conv1d.weight, "weight_loader")
        set_weight_attrs(
            self.conv1d.weight,
            {
                "weight_loader": mamba_v2_sharded_weight_loader(
                    [
                        query_key_settings,
                        query_key_settings,
                        value_settings,
                    ],
                    self.attn_tp_size,
                    self.attn_tp_rank,
                )
            },
        )

        # State parameters
        self.dt_bias = nn.Parameter(
            torch.ones(self.num_v_heads // self.attn_tp_size),
        )
        self.A_log = nn.Parameter(
            torch.empty(self.num_v_heads // self.attn_tp_size),
        )

        set_weight_attrs(self.A_log, {"weight_loader": sharded_weight_loader(0)})
        set_weight_attrs(self.dt_bias, {"weight_loader": sharded_weight_loader(0)})

        conv_weights = self.conv1d.weight.view(
            self.conv1d.weight.size(0), self.conv1d.weight.size(2)
        )
        # RadixLinearAttention layer
        self.attn = RadixLinearAttention(
            layer_id=layer_id,
            num_q_heads=self.num_k_heads // self.attn_tp_size,
            num_k_heads=self.num_k_heads // self.attn_tp_size,
            num_v_heads=self.num_v_heads // self.attn_tp_size,
            head_q_dim=self.head_k_dim,
            head_k_dim=self.head_k_dim,
            head_v_dim=self.head_v_dim,
            conv_weights=conv_weights,
            bias=self.conv1d.bias,
            activation=self.activation,
            A_log=self.A_log,
            dt_bias=self.dt_bias,
        )

        # Normalization layer
        self.norm = RMSNormGated(
            self.head_v_dim,
            eps=self.layer_norm_epsilon,
            group_size=None,
            norm_before_gate=True,
            device=torch.get_device_module().current_device(),
            dtype=config.torch_dtype,
        )

        # Output projection
        self.out_proj = RowParallelLinear(
            self.value_dim,
            self.hidden_size,
            bias=False,
            input_is_parallel=True,
            reduce_results=False,
            quant_config=quant_config,
            tp_rank=self.attn_tp_rank,
            tp_size=self.attn_tp_size,
            prefix=add_prefix("out_proj", prefix),
        )

    def fix_query_key_value_ordering(
        self,
        mixed_qkv,
        z,
        b,
        a,
    ):
        raise NotImplementedError(
            "Qwen3.5 Series dont need to fix query key value ordering"
        )

    def forward(
        self,
        hidden_states: torch.Tensor,
        forward_batch: ForwardBatch,
    ):
        output = torch.empty_like(hidden_states)
        if forward_batch.forward_mode.is_extend() and get_forward_context() is not None:
            gdn_with_output(
                hidden_states,
                output,
                self.layer_id,
            )
            return output
        else:
            return self._forward(hidden_states, forward_batch)

    def _forward(
        self,
        hidden_states: torch.Tensor,
        forward_batch: ForwardBatch,
    ):
        """
        Forward pass with three parts:
        1. Input projection
        2. Core attention (custom op)
        3. Output projection
        """
        seq_len, _ = hidden_states.shape

        mixed_qkv, _ = self.in_proj_qkv(hidden_states)
        z, _ = self.in_proj_z(hidden_states)
        z = z.reshape(z.size(0), -1, self.head_v_dim)
        # BACKPORT-PPU: extend/verify only — one [hidden, 2*V] GEMM instead of
        # two [hidden, V] GEMMs plus their acblas reduction kernels. The
        # outputs feed fused_gdn_gating, which takes row strides, so no
        # contiguous copies are needed. Decode keeps the original two-proj
        # path (its gating kernel assumes contiguous inputs).
        if (
            _FUSED_BA_PROJ
            and forward_batch.forward_mode.is_extend()
            and hidden_states.dtype == torch.bfloat16
            and getattr(self.in_proj_a, "quant_config", None) is None
            and getattr(self.in_proj_b, "quant_config", None) is None
        ):
            if self._ba_weight is None:
                self._ba_weight = torch.cat(
                    [self.in_proj_a.weight, self.in_proj_b.weight], dim=0
                ).contiguous()
            ba = torch.nn.functional.linear(hidden_states, self._ba_weight)
            a = ba[:, : self.num_v_heads]
            b = ba[:, self.num_v_heads :]
        else:
            b, _ = self.in_proj_b(hidden_states)
            a, _ = self.in_proj_a(hidden_states)

            b = b.contiguous()
            a = a.contiguous()

        core_attn_out = self.attn.forward(
            forward_batch=forward_batch,
            mixed_qkv=mixed_qkv,
            a=a,
            b=b,
        )

        z_shape_og = z.shape
        core_attn_out = core_attn_out.reshape(-1, core_attn_out.shape[-1])
        z = z.reshape(-1, z.shape[-1])
        core_attn_out = self.norm(core_attn_out, z)
        core_attn_out = core_attn_out.reshape(z_shape_og)
        core_attn_out = rearrange(core_attn_out, "... h d -> ... (h d)")
        output, _ = self.out_proj(core_attn_out)
        return output


class Qwen3_5LinearDecoderLayer(nn.Module):
    """Qwen3.5 Decoder Layer with Linear Attention (GatedDeltaNet)."""

    def __init__(
        self,
        config: Qwen3_5TextConfig,
        layer_id: int,
        quant_config: Optional[QuantizationConfig] = None,
        prefix: str = "",
        alt_stream: Optional[torch.cuda.Stream] = None,
    ) -> None:
        super().__init__()
        self.config = config
        self.layer_id = layer_id

        linear_attn_quant_config = (
            None
            if quant_config and quant_config.get_name() == "modelopt_fp4"
            else quant_config
        )
        self.linear_attn = Qwen3_5GatedDeltaNet(
            config, layer_id, linear_attn_quant_config, alt_stream, prefix
        )

        # NOTE: Determine the MLP type based on the model type
        # SLIM: removed the qwen3_5_moe_text sparse-MoE branch (fixed
        # Qwen3.5-2B config: dense model); only the dense MLP remains.
        if config.model_type == "qwen3_5_text":
            self.mlp = Qwen2MoeMLP(
                hidden_size=config.hidden_size,
                intermediate_size=config.intermediate_size,
                hidden_act=config.hidden_act,
                quant_config=quant_config,
                prefix=add_prefix("mlp", prefix.replace(".linear_attn", "")),
            )
            is_layer_sparse = False
            is_previous_layer_sparse = False
            is_next_layer_sparse = False
        else:
            raise ValueError(f"Invalid model type: {config.model_type}")

        self.layer_scatter_modes = LayerScatterModes.init_new(
            layer_id=layer_id,
            num_layers=config.num_hidden_layers,
            is_layer_sparse=is_layer_sparse,
            is_previous_layer_sparse=is_previous_layer_sparse,
            is_next_layer_sparse=is_next_layer_sparse,
        )

        self.input_layernorm = GemmaRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.post_attention_layernorm = GemmaRMSNorm(
            config.hidden_size, eps=config.rms_norm_eps
        )
        self.layer_communicator = LayerCommunicator(
            layer_scatter_modes=self.layer_scatter_modes,
            input_layernorm=self.input_layernorm,
            post_attention_layernorm=self.post_attention_layernorm,
            allow_reduce_scatter=True,
        )

    def forward(
        self,
        hidden_states: torch.Tensor,
        residual: Optional[torch.Tensor],
        **kwargs,
    ):
        forward_batch = kwargs.get("forward_batch", None)

        hidden_states, residual = self.layer_communicator.prepare_attn(
            hidden_states, residual, forward_batch
        )

        if not forward_batch.forward_mode.is_idle():
            hidden_states = self.linear_attn(
                hidden_states,
                forward_batch,
            )

        # Fully Connected
        hidden_states, residual = self.layer_communicator.prepare_mlp(
            hidden_states, residual, forward_batch
        )

        use_reduce_scatter = self.layer_communicator.should_use_reduce_scatter(
            forward_batch
        )
        hidden_states = self.mlp(hidden_states, forward_batch, use_reduce_scatter)

        hidden_states, residual = self.layer_communicator.postprocess_layer(
            hidden_states, residual, forward_batch
        )

        return hidden_states, residual


class Qwen3_5AttentionDecoderLayer(nn.Module):
    """Qwen3.5 Decoder Layer with Full Attention."""

    def __init__(
        self,
        config: Qwen3_5TextConfig,
        layer_id: int,
        quant_config: Optional[QuantizationConfig] = None,
        prefix: str = "",
        alt_stream: Optional[torch.cuda.Stream] = None,
    ) -> None:
        super().__init__()
        self.config = config
        self.hidden_size = config.hidden_size
        self.attn_tp_rank = get_attention_tp_rank()
        self.attn_tp_size = get_attention_tp_size()
        self.total_num_heads = config.num_attention_heads
        assert self.total_num_heads % self.attn_tp_size == 0
        self.num_heads = self.total_num_heads // self.attn_tp_size
        self.total_num_kv_heads = config.num_key_value_heads
        if self.total_num_kv_heads >= self.attn_tp_size:
            assert self.total_num_kv_heads % self.attn_tp_size == 0
        else:
            assert self.attn_tp_size % self.total_num_kv_heads == 0
        self.num_kv_heads = max(1, self.total_num_kv_heads // self.attn_tp_size)
        self.head_dim = config.head_dim or (self.hidden_size // self.num_heads)
        self.q_size = self.num_heads * self.head_dim
        self.kv_size = self.num_kv_heads * self.head_dim
        self.scaling = self.head_dim**-0.5
        self.max_position_embeddings = getattr(config, "max_position_embeddings", 8192)

        if hasattr(config, "rope_parameters"):
            self.rope_scaling = getattr(config, "rope_parameters", None)
        else:
            self.rope_scaling = getattr(config, "rope_scaling", None)

        self.rope_theta = self.rope_scaling.get("rope_theta", 10000)
        self.partial_rotary_factor = self.rope_scaling.get("partial_rotary_factor", 1.0)
        self.layer_id = layer_id

        self.attn_output_gate = getattr(config, "attn_output_gate", True)
        if self.attn_output_gate:
            logger.warning_once("using attn output gate!")

        self.rotary_emb = get_rope(
            head_size=self.head_dim,
            rotary_dim=self.head_dim,
            max_position=self.max_position_embeddings,
            rope_scaling=self.rope_scaling,
            base=self.rope_theta,
            partial_rotary_factor=self.partial_rotary_factor,
            is_neox_style=True,
            dtype=torch.get_default_dtype(),
        )

        attn_quant_config = (
            None
            if quant_config and quant_config.get_name() == "modelopt_fp4"
            else quant_config
        )

        self.qkv_proj = QKVParallelLinear(
            config.hidden_size,
            self.head_dim,
            self.total_num_heads * (1 + self.attn_output_gate),
            self.total_num_kv_heads,
            bias=False,
            quant_config=attn_quant_config,
            tp_rank=self.attn_tp_rank,
            tp_size=self.attn_tp_size,
            prefix=add_prefix("qkv_proj", prefix),
        )

        self.o_proj = RowParallelLinear(
            self.total_num_heads * self.head_dim,
            config.hidden_size,
            bias=False,
            quant_config=attn_quant_config,
            reduce_results=False,
            tp_rank=self.attn_tp_rank,
            tp_size=self.attn_tp_size,
            prefix=add_prefix("o_proj", prefix),
        )

        self.attn = RadixAttention(
            self.num_heads,
            self.head_dim,
            self.scaling,
            num_kv_heads=self.num_kv_heads,
            layer_id=layer_id,
            prefix=f"{prefix}.attn",
        )

        # Dense MLP for non-MoE variant
        # SLIM: removed the qwen3_5_moe_text sparse-MoE branch (fixed
        # Qwen3.5-2B config: dense model); only the dense MLP remains.
        if config.model_type == "qwen3_5_text":
            self.mlp = Qwen2MoeMLP(
                hidden_size=config.hidden_size,
                intermediate_size=config.intermediate_size,
                hidden_act=config.hidden_act,
                quant_config=quant_config,
                prefix=add_prefix("mlp", prefix.replace(".self_attn", "")),
            )
            is_layer_sparse = False
            is_previous_layer_sparse = False
            is_next_layer_sparse = False
        else:
            raise ValueError(f"Invalid model type: {config.model_type}")

        self.layer_scatter_modes = LayerScatterModes.init_new(
            layer_id=layer_id,
            num_layers=config.num_hidden_layers,
            is_layer_sparse=is_layer_sparse,
            is_previous_layer_sparse=is_previous_layer_sparse,
            is_next_layer_sparse=is_next_layer_sparse,
        )

        self.input_layernorm = GemmaRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.post_attention_layernorm = GemmaRMSNorm(
            config.hidden_size, eps=config.rms_norm_eps
        )

        self.q_norm = GemmaRMSNorm(self.head_dim, eps=config.rms_norm_eps)
        self.k_norm = GemmaRMSNorm(self.head_dim, eps=config.rms_norm_eps)

        self.layer_communicator = LayerCommunicator(
            layer_scatter_modes=self.layer_scatter_modes,
            input_layernorm=self.input_layernorm,
            post_attention_layernorm=self.post_attention_layernorm,
            allow_reduce_scatter=True,
        )

        self.alt_stream = alt_stream

    def _apply_qk_norm(
        self, q: torch.Tensor, k: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Apply Q/K normalization with optional alt_stream overlap."""
        # SLIM: removed the CUDA-graph capture-mode alt_stream branch (fixed
        # Qwen3.5-2B config: capture always disabled); only the non-capture
        # path remains.
        q_by_head = q.reshape(-1, self.head_dim)
        q_by_head = self.q_norm(q_by_head)
        k_by_head = k.reshape(-1, self.head_dim)
        k_by_head = self.k_norm(k_by_head)
        q = q_by_head.view(q.shape)
        k = k_by_head.view(k.shape)
        return q, k

    def self_attention(
        self,
        positions: torch.Tensor,
        hidden_states: torch.Tensor,
        forward_batch: ForwardBatch,
    ) -> torch.Tensor:
        """Full attention forward pass."""
        qkv, _ = self.qkv_proj(hidden_states)

        if self.attn_output_gate:
            q_gate, k, v = qkv.split(
                [self.q_size * 2, self.kv_size, self.kv_size], dim=-1
            )
            orig_shape = q_gate.shape[:-1]
            q_gate = q_gate.view(*orig_shape, self.num_heads, -1)
            if (
                _FUSED_QKG_NORM
                and _is_cuda
                and q_gate.dtype == torch.bfloat16
                and q_gate.ndim == 3
                and q_gate.shape[-1] == 2 * self.head_dim
                and k.ndim == 2
                and k.shape[-1] == self.kv_size
                and self.head_dim == 256
                and self.q_norm.weight.dtype == torch.bfloat16
                and self.k_norm.weight.dtype == torch.bfloat16
                and self.q_norm.variance_epsilon == self.k_norm.variance_epsilon
            ):
                q, k, v, gate = _fused_qkg_norm(
                    q_gate,
                    k,
                    v,
                    self.q_norm.weight,
                    self.k_norm.weight,
                    self.q_norm.variance_epsilon,
                    _FUSED_QKG_MODE == "1",
                )
                qk_norm_done = _FUSED_QKG_MODE == "1"
            else:
                q, gate = torch.chunk(q_gate, 2, dim=-1)
                q = q.reshape(*orig_shape, -1)
                gate = gate.reshape(*orig_shape, -1)
                qk_norm_done = False
        else:
            q, k, v = qkv.split([self.q_size, self.kv_size, self.kv_size], dim=-1)
            qk_norm_done = False

        if not qk_norm_done:
            q, k = self._apply_qk_norm(q, k)
        q, k = self.rotary_emb(positions, q, k)
        attn_output = self.attn(q, k, v, forward_batch)

        if self.attn_output_gate:
            # BACKPORT-PPU: fused sigmoid+mul, bit-exact vs the two eager
            # kernels (see _sigmoid_gate_mul_kernel).
            if (
                _FUSED_ATTN_GATE
                and _is_cuda
                and attn_output.dtype == torch.bfloat16
                and attn_output.is_contiguous()
                and gate.is_contiguous()
                and attn_output.numel() == gate.numel()
            ):
                fused_out = torch.empty_like(attn_output)
                numel = attn_output.numel()
                _sigmoid_gate_mul_kernel[(triton.cdiv(numel, 1024),)](
                    attn_output, gate, fused_out, numel, BLOCK=1024
                )
                attn_output = fused_out
            else:
                gate = torch.sigmoid(gate)
                attn_output = attn_output * gate

        output, _ = self.o_proj(attn_output)
        return output

    def forward(
        self,
        positions: torch.Tensor,
        hidden_states: torch.Tensor,
        residual: Optional[torch.Tensor],
        forward_batch: ForwardBatch,
        **kwargs,
    ):
        hidden_states, residual = self.layer_communicator.prepare_attn(
            hidden_states, residual, forward_batch
        )

        if not forward_batch.forward_mode.is_idle():
            hidden_states = self.self_attention(
                positions=positions,
                hidden_states=hidden_states,
                forward_batch=forward_batch,
            )

        # Fully Connected
        hidden_states, residual = self.layer_communicator.prepare_mlp(
            hidden_states, residual, forward_batch
        )
        use_reduce_scatter = self.layer_communicator.should_use_reduce_scatter(
            forward_batch
        )
        hidden_states = self.mlp(hidden_states, forward_batch, use_reduce_scatter)

        hidden_states, residual = self.layer_communicator.postprocess_layer(
            hidden_states, residual, forward_batch
        )

        return hidden_states, residual


ALL_DECODER_LAYER_TYPES = {
    "attention": Qwen3_5AttentionDecoderLayer,
    "linear_attention": Qwen3_5LinearDecoderLayer,
}


class Qwen3_5ForCausalLM(nn.Module):
    """Qwen3.5 Model with support for dense variant."""

    def __init__(
        self,
        config: Qwen3_5TextConfig,
        quant_config: Optional[QuantizationConfig] = None,
        prefix: str = "",
    ) -> None:
        super().__init__()
        self.config = config
        self.hidden_size = config.hidden_size
        self.pp_group = get_pp_group()

        alt_stream = torch.cuda.Stream() if _is_cuda else None

        # Embedding layer
        if self.pp_group.is_first_rank:
            self.embed_tokens = VocabParallelEmbedding(
                config.vocab_size,
                config.hidden_size,
                org_num_embeddings=config.vocab_size,
                enable_tp=not is_dp_attention_enabled(),
            )

        # Decoder layers
        def get_layer(idx: int, prefix: str):
            layer_type = config.layers_block_type[idx]
            layer_class = ALL_DECODER_LAYER_TYPES[layer_type]
            if layer_type == "attention":
                prefix = add_prefix("self_attn", prefix)
            else:
                prefix = add_prefix("linear_attn", prefix)
            return layer_class(
                config=config,
                layer_id=idx,
                quant_config=quant_config,
                prefix=prefix,
                alt_stream=alt_stream,
            )

        self.layers = make_layers(
            config.num_hidden_layers,
            get_layer,
            prefix=f"{prefix}.layers",
        )

        # Final normalization
        if self.pp_group.is_last_rank:
            self.norm = GemmaRMSNorm(config.hidden_size, eps=config.rms_norm_eps)

    def get_input_embeddings(self) -> nn.Embedding:
        return self.embed_tokens

    @torch.no_grad()
    def forward(
        self,
        input_ids: torch.Tensor,
        positions: torch.Tensor,
        forward_batch: ForwardBatch,
        input_embeds: Optional[torch.Tensor] = None,
        pp_proxy_tensors: Optional[PPProxyTensors] = None,
        input_deepstack_embeds: Optional[torch.Tensor] = None,
    ) -> Union[torch.Tensor, PPProxyTensors]:
        # Initialize hidden states
        if self.pp_group.is_first_rank:
            if input_embeds is None:
                hidden_states = self.embed_tokens(input_ids)
            else:
                hidden_states = input_embeds
            residual = None
        else:
            assert pp_proxy_tensors is not None
            hidden_states = pp_proxy_tensors["hidden_states"]
            residual = pp_proxy_tensors["residual"]

        # Pass through decoder layers
        # SLIM: removed eplb expert-distribution recorder wrapper (fixed
        # Qwen3.5-2B config: dense model, no MoE)
        for layer_idx in range(len(self.layers)):
            layer = self.layers[layer_idx]
            hidden_states, residual = layer(
                positions=positions,
                hidden_states=hidden_states,
                residual=residual,
                forward_batch=forward_batch,
            )

            # Process deepstack embeddings if provided
            if (
                input_deepstack_embeds is not None
                and input_deepstack_embeds.numel() > 0
                and layer_idx < 3
            ):
                sep = self.hidden_size * layer_idx
                hidden_states.add_(
                    input_deepstack_embeds[:, sep : sep + self.hidden_size]
                )

        # Return intermediate tensors for pipeline parallelism
        if not self.pp_group.is_last_rank:
            return PPProxyTensors(
                {
                    "hidden_states": hidden_states,
                    "residual": residual,
                }
            )

        # Apply final normalization
        if hidden_states.shape[0] != 0:
            if residual is None:
                hidden_states = self.norm(hidden_states)
            else:
                hidden_states, _ = self.norm(hidden_states, residual)

        return hidden_states

    def load_weights(self, weights: Iterable[Tuple[str, torch.Tensor]]):
        stacked_params_mapping = [
            # (param_name, shard_name, shard_id)
            ("qkv_proj", "q_proj", "q"),
            ("qkv_proj", "k_proj", "k"),
            ("qkv_proj", "v_proj", "v"),
            ("gate_up_proj", "gate_proj", 0),
            ("gate_up_proj", "up_proj", 1),
        ]

        loaded_params: Set[str] = set()
        params_dict = dict(self.named_parameters(remove_duplicate=False))
        for name, loaded_weight in weights:
            if "rotary_emb.inv_freq" in name:
                continue
            if "mtp" in name:
                continue
            if "visual" in name:
                continue
            if "language_model" in name:
                name = name.replace(r"model.language_model.", r"model.")
            if ".self_attn." in name:
                name = name.replace(".self_attn", "")

            for param_name, weight_name, shard_id in stacked_params_mapping:
                if weight_name not in name:
                    continue

                # SLIM: removed the "mlp.experts" skip guard (fixed Qwen3.5-2B
                # config: dense model, no expert weights)

                name = name.replace(weight_name, param_name)
                # Skip loading extra bias for GPTQ models.
                if name.endswith(".bias") and name not in params_dict:
                    continue
                # Skip layers on other devices.
                # if is_pp_missing_parameter(name, self):
                #     continue
                if name not in params_dict:
                    continue
                param = params_dict[name]
                weight_loader = getattr(param, "weight_loader")
                weight_loader(param, loaded_weight, shard_id)
                break
            else:
                # Skip loading extra bias for GPTQ models.
                if name.endswith(".bias") and name not in params_dict:
                    continue
                if name not in params_dict:
                    logger.warning(f"Parameter {name} not found in params_dict")
                    continue
                param = params_dict[name]

                weight_loader = getattr(param, "weight_loader", default_weight_loader)
                weight_loader(param, loaded_weight)
            loaded_params.add(name)
        return loaded_params


class Qwen3_5ForConditionalGeneration(Qwen3VLForConditionalGeneration):
    def __init__(
        self,
        config: Qwen3_5Config,
        quant_config: Optional[QuantizationConfig] = None,
        prefix: str = "",
        language_model_cls=Qwen3_5ForCausalLM,
    ):
        super().__init__(config, quant_config, prefix, language_model_cls)

        rope_config = getattr(self.config, "rope_parameters", None) or getattr(
            self.config, "rope_scaling", {}
        )
        self.is_mrope_enabled = "mrope_section" in rope_config

        self.deepstack_visual_indexes = self.visual.deepstack_visual_indexes

        # BACKPORT-PPU: P1.5 GEMV scope bisect (see gemv_q2.py); default on.
        if os.environ.get("SGLANG_GEMV_Q2_TARGET", "1") == "0":
            from sglang.srt.layers.gemv_q2 import disable_in_subtree

            disable_in_subtree(self)

    def get_embed_and_head(self):
        return self.model.embed_tokens.weight, self.lm_head.weight

    def set_embed_and_head(self, embed, head):
        del self.model.embed_tokens.weight
        del self.lm_head.weight
        self.model.embed_tokens.weight = embed
        self.lm_head.weight = head
        torch.cuda.empty_cache()
        torch.cuda.synchronize()

    def load_weights(self, weights: Iterable[Tuple[str, torch.Tensor]]):
        stacked_params_mapping = [
            # (param_name, shard_name, shard_id)
            ("qkv_proj", "q_proj", "q"),
            ("qkv_proj", "k_proj", "k"),
            ("qkv_proj", "v_proj", "v"),
            ("gate_up_proj", "gate_proj", 0),
            ("gate_up_proj", "up_proj", 1),
        ]

        loaded_params: Set[str] = set()
        params_dict = dict(self.named_parameters(remove_duplicate=False))
        for name, loaded_weight in weights:
            if "rotary_emb.inv_freq" in name:
                continue
            if "mtp" in name:
                continue
            if "language_model" in name:
                name = name.replace(r"model.language_model.", r"model.")
            if ".self_attn." in name:
                name = name.replace(".self_attn", "")

            for param_name, weight_name, shard_id in stacked_params_mapping:
                if weight_name not in name:
                    continue

                # SLIM: removed the "mlp.experts" skip guard (fixed Qwen3.5-2B
                # config: dense model, no expert weights)
                if "visual" in name:
                    continue

                name = name.replace(weight_name, param_name)
                # Skip loading extra bias for GPTQ models.
                if name.endswith(".bias") and name not in params_dict:
                    continue
                # Skip layers on other devices.
                # if is_pp_missing_parameter(name, self):
                #     continue
                if name not in params_dict:
                    continue
                param = params_dict[name]
                weight_loader = getattr(param, "weight_loader")
                weight_loader(param, loaded_weight, shard_id)
                break
            else:
                if "visual" in name:
                    # adapt to VisionAttention
                    name = name.replace(r"attn.qkv.", r"attn.qkv_proj.")
                    name = name.replace(r"model.visual.", r"visual.")

                # print(name, loaded_weight.shape)
                # Skip loading extra bias for GPTQ models.
                if name.endswith(".bias") and name not in params_dict:
                    continue
                if name not in params_dict:
                    logger.warning(f"Parameter {name} not found in params_dict")
                    continue
                param = params_dict[name]

                weight_loader = getattr(param, "weight_loader", default_weight_loader)
                weight_loader(param, loaded_weight)
            loaded_params.add(name)
        return loaded_params


# SLIM: removed Qwen3_5MoeForCausalLM / Qwen3_5MoeForConditionalGeneration
# (fixed Qwen3.5-2B config: dense model, no MoE)
EntryClass = [Qwen3_5ForConditionalGeneration]
