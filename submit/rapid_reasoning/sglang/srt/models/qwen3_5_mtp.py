"""Inference-only Qwen3.5 MTP (Multi-Token Prediction) draft model.

Single full-attention layer draft head used for self-speculative decoding:

    fc(cat(pre_fc_norm_embedding(embed(token)), pre_fc_norm_hidden(target_hidden)))
    -> one Qwen3_5AttentionDecoderLayer -> final norm -> shared lm_head

The embedding table and lm_head are shared with the target model (the
checkpoint carries no dedicated MTP embeddings: mtp_use_dedicated_embeddings
is false). Weight loading keeps only the ``mtp.*`` tensors and remaps them
onto this module tree (mtp.layers.0.* -> model.layers.0.*, mtp.norm ->
model.norm, mtp.{fc,pre_fc_norm_*} -> model.{fc,pre_fc_norm_*}), following
the DeepSeek/Qwen3-Next NextN convention.
"""
import logging
import os
from typing import Iterable, Optional, Set, Tuple

import torch
import torch.nn as nn

from sglang.srt.configs.qwen3_5 import Qwen3_5Config
from sglang.srt.layers.dp_attention import is_dp_attention_enabled
from sglang.srt.layers.layernorm import GemmaRMSNorm
from sglang.srt.layers.logits_processor import LogitsProcessor
from sglang.srt.layers.quantization.base_config import QuantizationConfig
from sglang.srt.layers.vocab_parallel_embedding import (
    ParallelLMHead,
    VocabParallelEmbedding,
)
from sglang.srt.model_executor.forward_batch_info import ForwardBatch
from sglang.srt.model_loader.weight_utils import default_weight_loader
from sglang.srt.models.qwen3_5 import Qwen3_5AttentionDecoderLayer
from sglang.srt.utils import add_prefix

logger = logging.getLogger(__name__)


class Qwen3_5MTPModel(nn.Module):
    def __init__(
        self,
        config,  # Qwen3_5TextConfig
        quant_config: Optional[QuantizationConfig] = None,
        prefix: str = "",
    ) -> None:
        super().__init__()
        self.config = config
        self.vocab_size = config.vocab_size

        self.embed_tokens = VocabParallelEmbedding(
            config.vocab_size,
            config.hidden_size,
            org_num_embeddings=config.vocab_size,
            enable_tp=not is_dp_attention_enabled(),
        )

        self.pre_fc_norm_embedding = GemmaRMSNorm(
            config.hidden_size, eps=config.rms_norm_eps
        )
        self.pre_fc_norm_hidden = GemmaRMSNorm(
            config.hidden_size, eps=config.rms_norm_eps
        )
        self.fc = nn.Linear(2 * config.hidden_size, config.hidden_size, bias=False)

        self.layers = nn.ModuleList(
            [
                Qwen3_5AttentionDecoderLayer(
                    config=config,
                    layer_id=0,
                    quant_config=quant_config,
                    prefix=add_prefix("layers.0.self_attn", prefix),
                )
            ]
        )

        self.norm = GemmaRMSNorm(config.hidden_size, eps=config.rms_norm_eps)

    def get_input_embeddings(self) -> nn.Embedding:
        return self.embed_tokens

    @torch.no_grad()
    def forward(
        self,
        input_ids: torch.Tensor,
        positions: torch.Tensor,
        forward_batch: ForwardBatch,
        hidden_states: torch.Tensor,
    ) -> torch.Tensor:
        residual = None
        for layer in self.layers:
            hidden_states, residual = layer(
                positions=positions,
                hidden_states=hidden_states,
                residual=residual,
                forward_batch=forward_batch,
            )
        hidden_states, _ = self.norm(hidden_states, residual)
        return hidden_states


class Qwen3_5MTPForCausalLM(nn.Module):
    def __init__(
        self,
        config: Qwen3_5Config,
        quant_config: Optional[QuantizationConfig] = None,
        prefix: str = "",
    ) -> None:
        super().__init__()
        self.config = config
        text_config = config.get_text_config()
        # The MTP head is a single full-attention layer; make the layer
        # scatter / hybrid-layer-type bookkeeping agree (otherwise the
        # rewritten single layer counts as a linear/GDN layer and the
        # draft worker profiles a zero-size KV cell).
        text_config.num_hidden_layers = 1
        text_config.full_attention_interval = 1
        self.quant_config = quant_config

        rope_config = getattr(text_config, "rope_parameters", None) or getattr(
            text_config, "rope_scaling", {}
        )
        self.is_mrope_enabled = "mrope_section" in rope_config

        self.model = Qwen3_5MTPModel(
            text_config, quant_config, prefix=add_prefix("model", prefix)
        )
        self.lm_head = ParallelLMHead(
            text_config.vocab_size,
            text_config.hidden_size,
            quant_config=quant_config,
            prefix=add_prefix("lm_head", prefix),
        )
        self.logits_processor = LogitsProcessor(text_config)

        # BACKPORT-PPU: P1.5 GEMV scope bisect (see gemv_q2.py); default on.
        if os.environ.get("SGLANG_GEMV_Q2_DRAFT", "1") == "0":
            from sglang.srt.layers.gemv_q2 import disable_in_subtree

            disable_in_subtree(self)

    @torch.no_grad()
    def forward(
        self,
        input_ids: torch.Tensor,
        positions: torch.Tensor,
        forward_batch: ForwardBatch,
        input_embeds: Optional[torch.Tensor] = None,
        **kwargs,
    ):
        if self.is_mrope_enabled:
            positions = forward_batch.mrope_positions

        if input_embeds is None:
            input_embeds = self.model.embed_tokens(input_ids)

        hidden_states = forward_batch.spec_info.hidden_states
        if not forward_batch.forward_mode.is_idle():
            input_embeds = self.model.pre_fc_norm_embedding(input_embeds)
            hidden_states = self.model.pre_fc_norm_hidden(hidden_states)
        hidden_states = self.model.fc(
            torch.cat((input_embeds, hidden_states), dim=-1)
        )

        hidden_states = self.model(
            input_ids,
            positions,
            forward_batch,
            hidden_states,
        )

        return self.logits_processor(
            input_ids, hidden_states, self.lm_head, forward_batch
        )

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
            # Keep only the MTP tensors; everything else belongs to the
            # target model (whose embedding/lm_head are shared separately).
            if "mtp" not in name:
                continue
            if name.startswith("mtp.fc") or name.startswith("mtp.pre_fc_norm"):
                name = name.replace("mtp.", "model.", 1)
            else:
                # mtp.layers.0.* -> model.layers.0.*; mtp.norm -> model.norm
                name = name.replace("mtp", "model", 1)
            if ".self_attn." in name:
                name = name.replace(".self_attn", "")

            for param_name, weight_name, shard_id in stacked_params_mapping:
                if weight_name not in name:
                    continue
                name = name.replace(weight_name, param_name)
                # Skip loading extra bias for GPTQ models.
                if name.endswith(".bias") and name not in params_dict:
                    continue
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


EntryClass = [Qwen3_5MTPForCausalLM]
