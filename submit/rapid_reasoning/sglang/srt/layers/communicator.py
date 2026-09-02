# BACKPORT: adapted subset of sglang v0.5.9 srt/layers/communicator.py.
#
# This tree (0.4.6-based) has no DP-attention buffers, no context-parallel,
# no NSA, no aiter and no flashinfer allreduce fusion. This port therefore
# keeps the full LayerScatterModes / LayerCommunicator API surface used by
# the backported Qwen3-Next / Qwen3.5 model code, but only implements the
# TP-only code paths (no DP attention, no CP, MoE a2a backend "none").
# Any scattered / DP / CP path raises NotImplementedError instead of silently
# computing wrong results.
import logging
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum, auto
from functools import partial
from typing import Callable, Dict, List, Optional, Tuple

import torch

from sglang.srt.distributed import (
    get_tensor_model_parallel_rank,
    get_tensor_model_parallel_world_size,
    get_tp_group,
    tensor_model_parallel_all_reduce,
)
from sglang.srt.layers.dp_attention import (
    get_attention_dp_size,
    get_attention_tp_rank,
    get_attention_tp_size,
    is_dp_attention_enabled,
)
from sglang.srt.model_executor.forward_batch_info import ForwardBatch
from sglang.srt.server_args import get_global_server_args

# SLIM: removed SpeculativeAlgorithm import (fixed Qwen3.5-2B config: no
# speculative decoding)

logger = logging.getLogger(__name__)


def apply_flashinfer_allreduce_fusion(batch_size: int) -> bool:
    # BACKPORT: flashinfer allreduce fusion is not available on PPU.
    return False


class ScatterMode(Enum):
    """
    Suppose we have TP=4, DP=2, enable-dp-attention, and the system handles seq a,b,c,d
    Model input/output: [ab, ab, cd, cd] for four ranks respectively
    SCATTERED: [a, b, c, d]
    TP_ATTN_FULL: [ab, ab, cd, cd], i.e. all ranks inside a TP attn group have full data of the group
    FULL: [abcd, abcd, abcd, abcd]
    """

    SCATTERED = auto()
    TP_ATTN_FULL = auto()
    FULL = auto()

    @staticmethod
    def model_input_output():
        """The scatter mode for model forward pass input and output data"""
        # BACKPORT: no NSA prefill CP in this tree.
        return ScatterMode.TP_ATTN_FULL


@dataclass
class AttentionInputs:
    hidden_states: torch.Tensor
    forward_batch: ForwardBatch
    qkv_latent_func: Optional[Callable] = None

    def __init__(
        self,
        hidden_states: torch.Tensor,
        forward_batch: ForwardBatch,
        qkv_latent_func: Callable,
    ):
        self.hidden_states = hidden_states
        self.forward_batch = forward_batch
        self.qkv_latent_func = qkv_latent_func
        self._qkv_latent = None

    def fetch_qkv_latent(self):
        if self._qkv_latent is None:
            self._qkv_latent = self.qkv_latent_func(
                self.hidden_states, self.forward_batch
            )
        return self._qkv_latent

    def fetch_hidden_states(self):
        return self.hidden_states


class AttnTpContext:
    # BACKPORT: attention-TP (input scattering across attn tp ranks) requires
    # DP-attention buffers that are not backported; this context always
    # reports non-scattered input.
    def __init__(self):
        self._input_scattered = False
        self._attn_inputs = None

    def init_context(self, q_lora_rank, is_nsa):
        pass

    def use_input_scattered(self, forward_batch: ForwardBatch):
        return False

    @property
    def input_scattered(self):
        return False

    def set_attn_inputs(self, attn_inputs: AttentionInputs):
        self._attn_inputs = attn_inputs

    def fetch_qkv_latent(self):
        return self._attn_inputs.fetch_qkv_latent()

    def fetch_hidden_states(self):
        return self._attn_inputs.fetch_hidden_states()

    def maybe_input_scattered(self, forward_batch: ForwardBatch):
        return False


_ATTN_TP_CONTEXT = AttnTpContext()


def get_attn_tp_context():
    global _ATTN_TP_CONTEXT
    return _ATTN_TP_CONTEXT


@dataclass
class _LayerModeComputationContext:
    num_layers: int
    layer_id: int
    is_layer_sparse: bool
    is_previous_layer_sparse: Optional[bool]
    is_next_layer_sparse: Optional[bool]

    def previous_layer(self):
        assert self.is_previous_layer_sparse is not None
        return _LayerModeComputationContext(
            num_layers=self.num_layers,
            layer_id=self.layer_id - 1,
            is_layer_sparse=self.is_previous_layer_sparse,
            is_previous_layer_sparse=None,
            is_next_layer_sparse=self.is_layer_sparse,
        )


@dataclass
class LayerScatterModes:
    layer_input_mode: ScatterMode
    attn_mode: ScatterMode
    # Can be further split into e.g. mlp_input_mode and mlp_output_mode if needed
    mlp_mode: ScatterMode
    middle_residual_mode: ScatterMode
    layer_output_mode: ScatterMode

    @classmethod
    def init_new(cls, **kwargs):
        context = _LayerModeComputationContext(**kwargs)
        return cls(
            layer_input_mode=cls._compute_layer_input_mode(context),
            attn_mode=ScatterMode.TP_ATTN_FULL,
            mlp_mode=cls._compute_mlp_mode(context),
            middle_residual_mode=cls._compute_middle_residual_mode(context),
            layer_output_mode=cls._compute_layer_output_mode(context),
        )

    @classmethod
    def _compute_layer_input_mode(cls, context: _LayerModeComputationContext):
        if context.layer_id == 0:
            return ScatterMode.model_input_output()
        return cls._compute_layer_output_mode(context.previous_layer())

    @classmethod
    def _compute_mlp_mode(cls, context: _LayerModeComputationContext):
        if context.is_layer_sparse:
            # BACKPORT: MoE a2a backend is always "none" and flashinfer
            # cutlass fp4 allgather is unavailable in this tree, so token
            # dispatch is never handled outside of LayerCommunicator.
            return ScatterMode.FULL
        else:
            return (
                ScatterMode.SCATTERED
                if enable_moe_dense_fully_dp()
                else ScatterMode.FULL
            )

    @classmethod
    def _should_gather_for_tbo(cls, context: _LayerModeComputationContext):
        return (
            not context.is_layer_sparse
            and context.is_next_layer_sparse
            and enable_moe_dense_fully_dp()
            and getattr(get_global_server_args(), "enable_two_batch_overlap", False)
        )

    @classmethod
    def _compute_middle_residual_mode(cls, context: _LayerModeComputationContext):
        mlp_mode = cls._compute_mlp_mode(context)
        if mlp_mode == ScatterMode.SCATTERED:
            return ScatterMode.SCATTERED
        if mlp_mode == ScatterMode.FULL:
            return ScatterMode.TP_ATTN_FULL
        raise NotImplementedError

    @classmethod
    def _compute_layer_output_mode(cls, context: _LayerModeComputationContext):
        mlp_mode = cls._compute_mlp_mode(context)
        if context.layer_id == context.num_layers - 1:
            return ScatterMode.model_input_output()
        if mlp_mode == ScatterMode.SCATTERED:
            if cls._should_gather_for_tbo(context):
                return ScatterMode.TP_ATTN_FULL
            return ScatterMode.SCATTERED
        if mlp_mode == ScatterMode.FULL:
            return ScatterMode.TP_ATTN_FULL
        raise NotImplementedError


def enable_moe_dense_fully_dp():
    return get_global_server_args().moe_dense_tp_size == 1


class LayerCommunicator:
    def __init__(
        self,
        layer_scatter_modes: LayerScatterModes,
        input_layernorm: torch.nn.Module,
        post_attention_layernorm: torch.nn.Module,
        # Reduce scatter requires skipping all-reduce in model code after MoE/MLP, so only enable for models which have that implemented. Remove flag once done for all models that use LayerCommunicator.
        allow_reduce_scatter: bool = False,
        is_last_layer: bool = False,
        qkv_latent_func: Optional[Callable] = None,
    ):
        self.layer_scatter_modes = layer_scatter_modes
        self.input_layernorm = input_layernorm
        self.post_attention_layernorm = post_attention_layernorm
        self.allow_reduce_scatter = allow_reduce_scatter
        self.is_last_layer = is_last_layer
        self.qkv_latent_func = qkv_latent_func

        self._context = CommunicateContext.init_new()
        self._post_init_communicate()
        # SLIM: removed _speculative_algo (fixed Qwen3.5-2B config: no
        # speculative decoding); it had no readers in this tree.

    def _post_init_communicate(self):
        self._communicate_simple_fn = CommunicateSimpleFn.get_fn(
            input_mode=self.layer_scatter_modes.layer_input_mode,
            output_mode=self.layer_scatter_modes.attn_mode,
            context=self._context,
        )
        self._communicate_with_all_reduce_and_layer_norm_fn = (
            CommunicateWithAllReduceAndLayerNormFn.get_fn(
                hidden_states_input_mode=self.layer_scatter_modes.attn_mode,
                residual_input_mode=self.layer_scatter_modes.layer_input_mode,
                hidden_states_output_mode=self.layer_scatter_modes.mlp_mode,
                residual_output_mode=self.layer_scatter_modes.middle_residual_mode,
                context=self._context,
            )
        )
        self._communicate_summable_tensor_pair_fn = (
            CommunicateSummableTensorPairFn.get_fn(
                hidden_states_input_mode=self.layer_scatter_modes.mlp_mode,
                residual_input_mode=self.layer_scatter_modes.middle_residual_mode,
                output_mode=self.layer_scatter_modes.layer_output_mode,
                context=self._context,
            )
        )

    def prepare_attn_and_capture_last_layer_outputs(
        self,
        hidden_states: torch.Tensor,
        residual: torch.Tensor,
        forward_batch: ForwardBatch,
        captured_last_layer_outputs: Optional[List[torch.Tensor]] = None,
        post_residual_addition: Optional[torch.Tensor] = None,
    ):
        hidden_states, residual = self.prepare_attn(
            hidden_states,
            residual,
            forward_batch,
            post_residual_addition=post_residual_addition,
        )
        if captured_last_layer_outputs is not None:
            gathered_last_layer_output = self._communicate_simple_fn(
                hidden_states=residual,
                forward_batch=forward_batch,
                context=self._context,
            )
            if gathered_last_layer_output is residual:
                # Clone to avoid modifying the original residual by Custom RMSNorm inplace operation
                gathered_last_layer_output = residual.clone()
            captured_last_layer_outputs.append(gathered_last_layer_output)
        return hidden_states, residual

    def prepare_attn(
        self,
        hidden_states: torch.Tensor,
        residual: torch.Tensor,
        forward_batch: ForwardBatch,
        quant_format: str = "",
        post_residual_addition: Optional[torch.Tensor] = None,
    ):
        # BACKPORT: aiter fused-quant, allreduce-fusion and input-scattered
        # branches from v0.5.9 are dropped (unavailable on this platform).
        if post_residual_addition is not None:
            # 0.4.6 RMSNorm has no post_residual_addition parameter.
            residual = (
                post_residual_addition
                if residual is None
                else residual + post_residual_addition
            )
        if hidden_states.shape[0] == 0:
            residual = hidden_states
        else:
            if residual is None:
                residual = hidden_states
                hidden_states = self.input_layernorm(hidden_states)
            else:
                hidden_states, residual = self.input_layernorm(
                    hidden_states,
                    residual,
                )

        hidden_states = self._communicate_simple_fn(
            hidden_states=hidden_states,
            forward_batch=forward_batch,
            context=self._context,
        )
        if self.qkv_latent_func is not None:
            attn_inputs = AttentionInputs(
                hidden_states, forward_batch, self.qkv_latent_func
            )
            get_attn_tp_context().set_attn_inputs(attn_inputs)
        return hidden_states, residual

    def _tp_reduce_scatter(
        self,
        hidden_states: torch.Tensor,
        residual: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        if hidden_states.shape[0] == 0:
            return hidden_states, hidden_states
        assert (
            hidden_states.shape[0] % self._context.tp_size == 0
        ), f"Expected total tokens {hidden_states.shape[0]} % tp_size {self._context.tp_size} to be 0"
        local_tokens = hidden_states.shape[0] // self._context.tp_size
        output = hidden_states.new_empty(local_tokens, *hidden_states.shape[1:])
        get_tp_group().reduce_scatter_tensor(output, hidden_states)
        if residual is not None:
            residual = residual.tensor_split(self._context.tp_size)[
                self._context.tp_rank
            ]
        return output, residual

    def prepare_mlp(
        self,
        hidden_states: torch.Tensor,
        residual: torch.Tensor,
        forward_batch: ForwardBatch,
        cache=None,
    ):
        if cache is not None:
            self._context.cache = cache

        return self._communicate_with_all_reduce_and_layer_norm_fn(
            hidden_states=hidden_states,
            residual=residual,
            forward_batch=forward_batch,
            layernorm=self.post_attention_layernorm,
            context=self._context,
        )

    def postprocess_layer(
        self,
        hidden_states: torch.Tensor,
        residual: torch.Tensor,
        forward_batch: ForwardBatch,
    ):
        return self._communicate_summable_tensor_pair_fn(
            hidden_states=hidden_states,
            residual=residual,
            forward_batch=forward_batch,
            context=self._context,
            allow_reduce_scatter=self.allow_reduce_scatter,
        )

    def should_use_reduce_scatter(self, forward_batch: ForwardBatch):
        if not self.allow_reduce_scatter:
            return False
        if (
            self._communicate_summable_tensor_pair_fn
            is CommunicateSummableTensorPairFn._scatter_hidden_states
            and forward_batch.dp_padding_mode.is_max_len()
        ):
            return True
        return False

    # NOTE: This function will cause torch recompilation
    def should_fuse_mlp_allreduce_with_next_layer(
        self, forward_batch: ForwardBatch
    ) -> bool:
        # BACKPORT: flashinfer allreduce fusion is unavailable on PPU.
        return False


@dataclass
class CommunicateContext:
    process_group_sizes: Dict[ScatterMode, int]
    attn_tp_rank: int
    attn_tp_size: int
    attn_dp_size: int
    attn_cp_rank: int
    attn_cp_size: int
    tp_size: int
    cache = None
    tp_rank: int

    def is_same_group_size(self, a: ScatterMode, b: ScatterMode):
        return self.process_group_sizes[a] == self.process_group_sizes[b]

    @classmethod
    def init_new(cls):
        attn_tp_rank = get_attention_tp_rank()
        attn_tp_size = get_attention_tp_size()
        attn_dp_size = get_attention_dp_size()
        # BACKPORT: no attention context parallel in this tree.
        attn_cp_size = 1
        attn_cp_rank = 0
        tp_size = get_tensor_model_parallel_world_size()
        tp_rank = get_tensor_model_parallel_rank()
        process_group_sizes = {
            ScatterMode.SCATTERED: 1,
            ScatterMode.TP_ATTN_FULL: attn_tp_size,
            # TODO: support --moe-dense-tp-size > 1
            ScatterMode.FULL: tp_size,
        }
        return cls(
            process_group_sizes=process_group_sizes,
            attn_tp_rank=attn_tp_rank,
            attn_tp_size=attn_tp_size,
            attn_dp_size=attn_dp_size,
            attn_cp_rank=attn_cp_rank,
            attn_cp_size=attn_cp_size,
            tp_size=tp_size,
            tp_rank=tp_rank,
        )


class CommunicateSimpleFn:
    @staticmethod
    def get_fn(
        input_mode: ScatterMode,
        output_mode: ScatterMode,
        context: CommunicateContext,
    ):
        if context.is_same_group_size(input_mode, output_mode):
            return CommunicateSimpleFn._trivial

        # BACKPORT: scattered <-> tp_attn_full transitions need DP-attention
        # buffers that are not backported.
        raise NotImplementedError(f"{input_mode=} {output_mode=}")

    @staticmethod
    def _trivial(
        hidden_states: torch.Tensor,
        forward_batch: ForwardBatch,
        context: CommunicateContext,
    ) -> torch.Tensor:
        return hidden_states


class CommunicateWithAllReduceAndLayerNormFn:
    """Besides communication, needs to
    1. All reduce in tp_attn_group on hidden_states
    2. Apply layer norm
    """

    @staticmethod
    def get_fn(
        hidden_states_input_mode: ScatterMode,
        residual_input_mode: ScatterMode,
        hidden_states_output_mode: ScatterMode,
        residual_output_mode: ScatterMode,
        context: CommunicateContext,
    ):

        if (
            context.is_same_group_size(
                hidden_states_input_mode, hidden_states_output_mode
            )
            and context.is_same_group_size(residual_input_mode, residual_output_mode)
            and context.attn_tp_size == 1
        ):
            return CommunicateWithAllReduceAndLayerNormFn._simple

        if (
            (hidden_states_input_mode == ScatterMode.TP_ATTN_FULL)
            and (residual_input_mode == ScatterMode.TP_ATTN_FULL)
            and (hidden_states_output_mode == ScatterMode.FULL)
            and (residual_output_mode == ScatterMode.TP_ATTN_FULL)
            and context.attn_dp_size == 1
        ):
            # BACKPORT: only the non-DP, non-scattered sub-path of v0.5.9's
            # _gather_hidden_states_and_residual is implemented.
            return CommunicateWithAllReduceAndLayerNormFn._gather_hidden_states_and_residual

        raise NotImplementedError(
            f"{hidden_states_input_mode=} {residual_input_mode=} {hidden_states_output_mode=} {residual_output_mode=}"
        )

    @staticmethod
    def _simple(
        hidden_states: torch.Tensor,
        residual: torch.Tensor,
        forward_batch: ForwardBatch,
        layernorm: torch.nn.Module,
        context: CommunicateContext,
    ):
        # TODO move these `if shape != 0` into LayerNorm itself
        if hidden_states.shape[0] != 0:
            hidden_states, residual = layernorm(hidden_states, residual)
        return hidden_states, residual

    @staticmethod
    def _gather_hidden_states_and_residual(
        hidden_states: torch.Tensor,
        residual: torch.Tensor,
        forward_batch: ForwardBatch,
        layernorm: torch.nn.Module,
        context: CommunicateContext,
    ):
        hidden_states = tensor_model_parallel_all_reduce(hidden_states)
        if hidden_states.shape[0] != 0:
            hidden_states, residual = layernorm(hidden_states, residual)
        return hidden_states, residual


class CommunicateSummableTensorPairFn:
    """It is allowed to make (hidden_states, residual) := (hidden_states + residual, None) if needed."""

    @classmethod
    def execute(
        cls,
        hidden_states_input_mode,
        residual_input_mode,
        output_mode,
        context,
        **kwargs,
    ):
        return cls.get_fn(
            hidden_states_input_mode=hidden_states_input_mode,
            residual_input_mode=residual_input_mode,
            output_mode=output_mode,
            context=context,
        )(context=context, **kwargs)

    @staticmethod
    def get_fn(
        hidden_states_input_mode: ScatterMode,
        residual_input_mode: ScatterMode,
        output_mode: ScatterMode,
        context: CommunicateContext,
    ):
        if context.is_same_group_size(
            hidden_states_input_mode, output_mode
        ) and context.is_same_group_size(residual_input_mode, output_mode):
            return CommunicateSummableTensorPairFn._trivial

        # BACKPORT: scattered / DP transitions are not implemented in this tree.
        raise NotImplementedError(
            f"{hidden_states_input_mode=} {residual_input_mode=} {output_mode=}"
        )

    @staticmethod
    def _trivial(
        hidden_states: torch.Tensor,
        residual: torch.Tensor,
        forward_batch: ForwardBatch,
        context: CommunicateContext,
        **kwargs,
    ):
        return hidden_states, residual

    @staticmethod
    def _scatter_hidden_states(
        hidden_states: torch.Tensor,
        residual: torch.Tensor,
        forward_batch: ForwardBatch,
        context: CommunicateContext,
        allow_reduce_scatter: bool = False,
    ):
        raise NotImplementedError(
            "DP-attention scattered hidden states are not supported in this tree"
        )
