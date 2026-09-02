# Copyright 2023-2024 SGLang Team
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
"""ModelRunner runs the forward passes of the models."""

import datetime
import gc
import logging
import os
import sys
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

import torch
import torch.distributed as dist

from sglang.srt.configs.device_config import DeviceConfig
from sglang.srt.configs.load_config import LoadConfig
from sglang.srt.configs.model_config import AttentionArch, ModelConfig
from sglang.srt.distributed import (
    get_tp_group,
    init_distributed_environment,
    initialize_model_parallel,
    set_custom_all_reduce,
)
from sglang.srt.distributed.parallel_state import monkey_patch_vllm_parallel_state
from sglang.srt.layers.dp_attention import (
    get_attention_tp_group,
    get_attention_tp_size,
    initialize_dp_attention,
)
from sglang.srt.layers.logits_processor import LogitsProcessorOutput
from sglang.srt.environ import envs
from sglang.srt.layers.sampler import Sampler
from sglang.srt.layers.torchao_utils import apply_torchao_config_to_model
# SLIM: removed quantization monkey-patch and LoRA imports (fixed Qwen3.5-2B
# config: bf16, no quantization, no LoRA)
from sglang.srt.managers.schedule_batch import global_server_args_dict
from sglang.srt.mem_cache.memory_pool import (
    HybridLinearKVPool,
    HybridReqToTokenPool,
    MHATokenToKVPool,
    MLATokenToKVPool,
    ReqToTokenPool,
    TokenToKVPoolAllocator,
)
from sglang.srt.mem_cache.paged_allocator import PagedTokenToKVPoolAllocator
# BACKPORT-PPU: CudaGraphRunner restored for bs=1 decode-only graph capture
# (hybrid GDN capture is now supported on this fixed config).
from sglang.srt.model_executor.cuda_graph_runner import (
    CudaGraphRunner,
    MtpTargetVerifyGraphRunner,
)
from sglang.srt.model_executor.forward_batch_info import ForwardBatch
from sglang.srt.model_loader import get_model
from sglang.srt.model_loader.loader import (
    DefaultModelLoader,
    device_loading_context,
    get_model_loader,
)
from sglang.srt.model_loader.utils import set_default_torch_dtype
from sglang.srt.model_loader.weight_utils import default_weight_loader
from sglang.srt.patch_torch import monkey_patch_torch_reductions
from sglang.srt.sampling.sampling_batch_info import SamplingBatchInfo
from sglang.srt.server_args import ServerArgs
from sglang.srt.speculative.spec_info import SpeculativeAlgorithm
from sglang.srt.torch_memory_saver_adapter import TorchMemorySaverAdapter
from sglang.srt.utils import (
    MultiprocessingSerializer,
    enable_show_time_cost,
    get_available_gpu_memory,
    get_bool_env_var,
    init_custom_process_group,
    is_cuda,
    is_hip,
    monkey_patch_p2p_access_check,
    monkey_patch_vllm_gguf_config,
    set_cpu_offload_max_bytes,
    set_cuda_arch,
)

# Use a small KV cache pool size for tests in CI
SGLANG_CI_SMALL_KV_SIZE = os.getenv("SGLANG_CI_SMALL_KV_SIZE", None)

# Detect stragger ranks in model loading
UNBALANCED_MODEL_LOADING_TIMEOUT_S = 300

logger = logging.getLogger(__name__)

# BACKPORT: mamba cache sizing ratios from sglang v0.5.9
MAMBA_CACHE_SIZE_MAX_RUNNING_REQUESTS_RATIO = 3
MAMBA_CACHE_V2_ADDITIONAL_RATIO_OVERLAP = 2
MAMBA_CACHE_V2_ADDITIONAL_RATIO_NO_OVERLAP = 1


class ModelRunner:
    """ModelRunner runs the forward passes of the models."""

    def __init__(
        self,
        model_config: ModelConfig,
        mem_fraction_static: float,
        gpu_id: int,
        tp_rank: int,
        tp_size: int,
        nccl_port: int,
        server_args: ServerArgs,
        is_draft_worker: bool = False,
        req_to_token_pool: Optional[ReqToTokenPool] = None,
        token_to_kv_pool_allocator: Optional[TokenToKVPoolAllocator] = None,
    ):
        # Parse args
        self.model_config = model_config
        # BACKPORT: worker processes receive ServerArgs via pickle (bypassing
        # __post_init__), so re-register the global accessor here for v0.5.9
        # backported code paths (qwen3_vl / hybrid backends).
        from sglang.srt.server_args import set_global_server_args

        set_global_server_args(server_args)
        self.mem_fraction_static = mem_fraction_static
        self.device = server_args.device
        self.gpu_id = gpu_id
        self.tp_rank = tp_rank
        self.tp_size = tp_size
        self.dist_port = nccl_port
        self.server_args = server_args
        self.is_draft_worker = is_draft_worker
        self.is_generation = model_config.is_generation
        self.is_multimodal = model_config.is_multimodal
        self.should_log = tp_rank == 0
        self.spec_algorithm = SpeculativeAlgorithm.from_string(
            server_args.speculative_algorithm
        )
        # MTP phase 2: spec-mode CUDA graph runners (created in
        # init_cuda_graphs / by the MTPWorker for the draft model).
        self.cuda_graph_verify_runner = None
        self.cuda_graph_draft_runner = None
        # SGLANG_EXTEND_GRAPH: extend (prefill) graph runner, created at the
        # end of initialize() when the env gate is on; None = eager prefill.
        self.extend_graph_runner = None
        self.page_size = server_args.page_size
        self.req_to_token_pool = req_to_token_pool
        self.token_to_kv_pool_allocator = token_to_kv_pool_allocator
        self.use_mla_backend = self.model_config.attention_arch == AttentionArch.MLA
        # BACKPORT: radix-cache mamba tracking (MambaRadixCache) is not
        # backported; force the no-radix ChunkCache path for hybrid GDN models.
        if self.hybrid_gdn_config is not None and not server_args.disable_radix_cache:
            logger.info(
                "Forcing disable_radix_cache=True for hybrid GDN models "
                "(mamba-aware radix cache is not supported in this tree)."
            )
            server_args.disable_radix_cache = True
        self.attention_chunk_size = model_config.attention_chunk_size

        # Model-specific adjustment
        self.model_specific_adjustment()

        if server_args.show_time_cost:
            enable_show_time_cost()

        # Global vars
        global_server_args_dict.update(
            {
                "attention_backend": server_args.attention_backend,
                "sampling_backend": server_args.sampling_backend,
                "triton_attention_reduce_in_fp32": server_args.triton_attention_reduce_in_fp32,
                "torchao_config": server_args.torchao_config,
                "enable_nan_detection": server_args.enable_nan_detection,
                "enable_dp_attention": server_args.enable_dp_attention,
                "enable_ep_moe": server_args.enable_ep_moe,
                "enable_deepep_moe": server_args.enable_deepep_moe,
                "deepep_mode": server_args.deepep_mode,
                "device": server_args.device,
                "speculative_accept_threshold_single": server_args.speculative_accept_threshold_single,
                "speculative_accept_threshold_acc": server_args.speculative_accept_threshold_acc,
                "disable_radix_cache": server_args.disable_radix_cache,
                "flashinfer_mla_disable_ragged": server_args.flashinfer_mla_disable_ragged,
                "moe_dense_tp_size": server_args.moe_dense_tp_size,
                "debug_tensor_dump_output_folder": server_args.debug_tensor_dump_output_folder,
                "debug_tensor_dump_inject": server_args.debug_tensor_dump_inject,
                "n_share_experts_fusion": server_args.n_share_experts_fusion,
                "disable_chunked_prefix_cache": server_args.disable_chunked_prefix_cache,
                "use_mla_backend": self.use_mla_backend,
            }
        )

        # CPU offload
        set_cpu_offload_max_bytes(int(server_args.cpu_offload_gb * 1024**3))

        # Get memory before model loading
        min_per_gpu_memory = self.init_torch_distributed()

        # SLIM: removed deep-gemm JIT config update (fixed Qwen3.5-2B config:
        # bf16, no quantization)

        # If it is a draft model, tp_group can be different
        self.initialize(min_per_gpu_memory)

    def initialize(self, min_per_gpu_memory: float):
        server_args = self.server_args
        self.memory_saver_adapter = TorchMemorySaverAdapter.create(
            enable=self.server_args.enable_memory_saver
        )

        # Load the model
        self.sampler = Sampler()
        self.load_model()

        # Apply torchao quantization
        torchao_applied = getattr(self.model, "torchao_applied", False)
        # In layered loading, torchao may have been applied
        if not torchao_applied:
            apply_torchao_config_to_model(
                self.model, global_server_args_dict["torchao_config"]
            )

        # Apply torch TP if the model supports it
        supports_torch_tp = getattr(self.model, "supports_torch_tp", False)
        if self.tp_size > 1 and supports_torch_tp:
            self.apply_torch_tp()

        # Init memory pool and attention backends
        self.init_memory_pool(
            min_per_gpu_memory,
            server_args.max_running_requests,
            server_args.max_total_tokens,
        )
        if self.device == "cuda":
            self.init_cublas()
        # SLIM: removed LoRA init (fixed Qwen3.5-2B config: no LoRA)
        self.init_attention_backend()
        # BACKPORT-PPU: re-enabled bs=1 decode-only CUDA graph capture; the
        # graph runner needs the attention backend to be initialized first.
        if self.device == "cuda":
            self.init_cuda_graphs()
        else:
            self.cuda_graph_runner = None

        # BACKPORT-PPU: pre-capture the ViT bucket graphs at engine init
        # (after weights, memory pool and decode graphs are ready) so
        # benchmark requests all hit replay; shapes outside the warmup range
        # still capture on demand. Best-effort: on failure, on-demand capture
        # and the eager fallback in the vision forward remain in place.
        if self.device == "cuda":
            visual = getattr(self.model, "visual", None)
            vit_runner = getattr(visual, "cuda_graph_runner", None)
            if vit_runner is not None and envs.SGLANG_VIT_ENABLE_CUDA_GRAPH.get():
                try:
                    vit_runner.warmup_buckets(hi=envs.SGLANG_VIT_WARMUP_HI.get())
                except Exception:
                    logger.warning(
                        "ViT CUDA graph warmup failed; on-demand capture remains",
                        exc_info=True,
                    )

        # BACKPORT-PPU: opt-in extend (prefill) CUDA graph capture
        # (SGLANG_EXTEND_GRAPH=1). Runs after weights, memory pool, decode
        # graphs and ViT warmup are ready. Best-effort: on any failure the
        # runner stays None and every prefill falls back to eager.
        # In MTP mode the draft model is constructed after this target
        # runner.  Defer EXTEND capture until MTPWorker has finished loading
        # the draft model and its graphs, otherwise the extra allocations and
        # capture warmups perturb the draft initialization/runtime layout.
        if self.spec_algorithm.is_none():
            self.init_extend_cuda_graph()
            self.init_long_prefill_warmup()

    def init_extend_cuda_graph(self):
        """Best-effort initialization of the opt-in prefill CUDA graph."""
        if self.device != "cuda" or not envs.SGLANG_EXTEND_GRAPH.get():
            return
        try:
            from sglang.srt.model_executor.extend_cuda_graph_runner import (
                ExtendCudaGraphRunner,
            )

            self.extend_graph_runner = ExtendCudaGraphRunner(self)
            logger.info(
                "Extend CUDA graphs captured (buckets=%s, bs=1).",
                self.extend_graph_runner.buckets,
            )
        except Exception:
            logger.warning(
                "Extend CUDA graph capture failed; prefill stays eager",
                exc_info=True,
            )
            self.extend_graph_runner = None

    def init_long_prefill_warmup(self):
        """Best-effort eager prefill warmup for out-of-bucket prompt lengths.

        BACKPORT-PPU: prompts above the largest extend-graph bucket take the
        eager path, and the first such request would otherwise pay Triton
        JIT/autotune mid-run. Run one synthetic bs=1 pure prefill (no prefix,
        no mm, no spec) per configured length at engine init. Outputs are
        discarded; all KV/mamba writes land in scratch slot 0, which is
        zeroed afterwards — the same discipline as the extend graph capture
        warmup, whose leftover dummy state corrupted the first draft forward
        before the zeroing was added.
        """
        if self.device != "cuda" or not envs.SGLANG_LONG_PREFILL_WARMUP.get():
            return
        try:
            from sglang.srt.model_executor.forward_batch_info import (
                CaptureHiddenMode,
                ForwardMode,
            )

            raw = envs.SGLANG_LONG_PREFILL_WARMUP_LENS.get()
            lens = sorted(
                {int(item) for item in raw.replace(",", " ").split() if item}
            )
            if not lens:
                return

            started = time.perf_counter()
            try:
                for n in lens:
                    with torch.device("cuda"):
                        input_ids = torch.zeros((n,), dtype=torch.int64)
                        req_pool_indices = torch.zeros((1,), dtype=torch.int32)
                        seq_lens = torch.full((1,), n, dtype=torch.int32)
                        out_cache_loc = torch.zeros((n,), dtype=torch.int64)
                        positions = torch.arange(n, dtype=torch.int64).repeat(3, 1)
                        extend_seq_lens = torch.full((1,), n, dtype=torch.int32)
                        extend_prefix_lens = torch.zeros((1,), dtype=torch.int32)
                        extend_start_loc = torch.zeros((1,), dtype=torch.int32)
                    forward_batch = ForwardBatch(
                        forward_mode=ForwardMode.EXTEND,
                        batch_size=1,
                        input_ids=input_ids,
                        req_pool_indices=req_pool_indices,
                        seq_lens=seq_lens,
                        req_to_token_pool=self.req_to_token_pool,
                        token_to_kv_pool=self.token_to_kv_pool,
                        attn_backend=self.attn_backend,
                        out_cache_loc=out_cache_loc,
                        seq_lens_sum=n,
                        return_logprob=False,
                        positions=positions,
                        mrope_positions=positions,
                        capture_hidden_mode=CaptureHiddenMode.FULL,
                        extend_num_tokens=n,
                        extend_start_loc=extend_start_loc,
                        extend_seq_lens=extend_seq_lens,
                        extend_prefix_lens=extend_prefix_lens,
                        extend_seq_lens_cpu=[n],
                        extend_prefix_lens_cpu=[0],
                    )
                    self.forward_extend(forward_batch)
                    torch.cuda.synchronize()
                    print(
                        f"LONGPREFILL warmup len={n} done",
                        file=sys.stderr,
                        flush=True,
                    )
            finally:
                # The synthetic batch writes dummy K/V and mamba states into
                # scratch slot 0 (out_cache_loc=0, req 0 maps to mamba slot 0
                # at init). Always zero it — even when a warmup forward
                # failed halfway — so no later forward can observe garbage.
                pool = self.token_to_kv_pool
                mc = pool.mamba_pool.mamba_cache
                for c in mc.conv:
                    c[:, 0].zero_()
                mc.temporal[:, 0].zero_()
                fp = pool.full_kv_pool
                for lb in fp.k_buffer:
                    lb[0].zero_()
                for lb in fp.v_buffer:
                    lb[0].zero_()
                torch.cuda.synchronize()
            print(
                f"LONGPREFILL warmup lens={lens} "
                f"seconds={time.perf_counter() - started:.1f}",
                file=sys.stderr,
                flush=True,
            )
        except Exception:
            logger.warning(
                "Long-prefill warmup failed; first long prompt pays JIT",
                exc_info=True,
            )

    def model_specific_adjustment(self):
        server_args = self.server_args

        # SLIM: removed attention backend auto-selection chain (fa3 / flashinfer
        # / MLA / double-sparsity) — fixed Qwen3.5-2B config uses the triton
        # backend. Reject other backends explicitly instead of silently
        # overriding them.
        if server_args.attention_backend not in (None, "triton"):
            raise ValueError(
                f"Invalid attention backend for this build: "
                f"{server_args.attention_backend} (only 'triton' is supported)"
            )
        server_args.attention_backend = "triton"

        if self.is_multimodal:
            self.mem_fraction_static *= 0.90
            logger.info(
                f"Automatically reduce --mem-fraction-static to {self.mem_fraction_static:.3f} "
                f"because this is a multimodal model."
            )
            logger.info(
                "Automatically turn off --chunked-prefill-size for multimodal model."
            )
            server_args.chunked_prefill_size = -1

        # SLIM: chunked prefix cache is MLA-only; the fixed Qwen3.5-2B config is
        # non-MLA, so it is always disabled.
        server_args.disable_chunked_prefix_cache = True

    def init_torch_distributed(self):
        logger.info("Init torch distributed begin.")

        try:
            torch.get_device_module(self.device).set_device(self.gpu_id)
        except Exception:
            logger.warning(
                f"Context: {self.device=} {self.gpu_id=} {os.environ.get('CUDA_VISIBLE_DEVICES')=} {self.tp_rank=} {self.tp_size=}"
            )
            raise

        if self.device == "cuda":
            backend = "nccl"
        elif self.device == "xpu":
            backend = "xccl"
        elif self.device == "hpu":
            backend = "hccl"
        elif self.device == "cpu":
            backend = "gloo"

        before_avail_memory = get_available_gpu_memory(self.device, self.gpu_id)
        if not self.server_args.enable_p2p_check:
            monkey_patch_p2p_access_check()

        if self.server_args.dist_init_addr:
            dist_init_method = f"tcp://{self.server_args.dist_init_addr}"
        else:
            dist_init_method = f"tcp://127.0.0.1:{self.dist_port}"
        set_custom_all_reduce(not self.server_args.disable_custom_all_reduce)

        if not self.is_draft_worker:
            # Only initialize the distributed environment on the target model worker.
            init_distributed_environment(
                backend=backend,
                world_size=self.tp_size,
                rank=self.tp_rank,
                local_rank=self.gpu_id,
                distributed_init_method=dist_init_method,
                timeout=self.server_args.dist_timeout,
            )
            initialize_model_parallel(tensor_model_parallel_size=self.tp_size)
            # SLIM: DP attention is fixed off (fixed Qwen3.5-2B config: TP=1, DP=1)
            initialize_dp_attention(
                enable_dp_attention=False,
                tp_rank=self.tp_rank,
                tp_size=self.tp_size,
                dp_size=1,
            )

        min_per_gpu_memory = get_available_gpu_memory(
            self.device, self.gpu_id, distributed=self.tp_size > 1
        )
        self.tp_group = get_tp_group()
        self.attention_tp_group = get_attention_tp_group()

        # Check memory for tensor parallelism
        local_gpu_memory = get_available_gpu_memory(self.device, self.gpu_id)
        if self.tp_size > 1:
            if min_per_gpu_memory < local_gpu_memory * 0.9:
                if get_bool_env_var("SGL_DISABLE_TP_MEMORY_INBALANCE_CHECK"):
                    logger.warning(
                        "The memory capacity is unbalanced. Some GPUs may be occupied by other processes. "
                        f"{min_per_gpu_memory=}, {local_gpu_memory=}, {local_gpu_memory * 0.9=}"
                    )
                else:
                    raise ValueError(
                        "The memory capacity is unbalanced. Some GPUs may be occupied by other processes. "
                        f"{min_per_gpu_memory=}, {local_gpu_memory=}, {local_gpu_memory * 0.9=}"
                    )

        logger.info(
            f"Init torch distributed ends. mem usage={(before_avail_memory - local_gpu_memory):.2f} GB"
        )
        return min_per_gpu_memory

    def load_model(self):
        before_avail_memory = get_available_gpu_memory(self.device, self.gpu_id)
        logger.info(
            f"Load weight begin. avail mem={get_available_gpu_memory(self.device, self.gpu_id):.2f} GB"
        )

        # This can reduce thread conflicts and speed up weight loading.
        if self.device != "cpu":
            torch.set_num_threads(1)
        if self.device == "cuda":
            if torch.cuda.get_device_capability()[0] < 8:
                logger.info(
                    "Compute capability below sm80. Use float16 due to lack of bfloat16 support."
                )
                self.server_args.dtype = "float16"
                self.model_config.dtype = torch.float16
                if torch.cuda.get_device_capability()[1] < 5:
                    raise RuntimeError("SGLang only supports sm75 and above.")

        set_cuda_arch()

        # Prepare the model config
        self.load_config = LoadConfig(
            load_format=self.server_args.load_format,
            download_dir=self.server_args.download_dir,
        )
        if self.server_args.load_format == "gguf":
            monkey_patch_vllm_gguf_config()

        # Load the model
        # Remove monkey_patch when linear.py quant remove dependencies with vllm
        monkey_patch_vllm_parallel_state()

        with self.memory_saver_adapter.region():
            self.model = get_model(
                model_config=self.model_config,
                load_config=self.load_config,
                device_config=DeviceConfig(self.device),
            )
        monkey_patch_vllm_parallel_state(reverse=True)

        # SLIM: removed quantization isinstance monkey-patch and FP8 KV-cache
        # scaling-factor loading (fixed Qwen3.5-2B config: bf16, no quantization)

        # Parse other args
        self.sliding_window_size = (
            self.model.get_attention_sliding_window_size()
            if hasattr(self.model, "get_attention_sliding_window_size")
            else None
        )
        self.dtype = self.model_config.dtype

        after_avail_memory = get_available_gpu_memory(self.device, self.gpu_id)
        logger.info(
            f"Load weight end. "
            f"type={type(self.model).__name__}, "
            f"dtype={self.dtype}, "
            f"avail mem={after_avail_memory:.2f} GB, "
            f"mem usage={(before_avail_memory - after_avail_memory):.2f} GB."
        )

        # Handle the case where some ranks do not finish loading.
        try:
            dist.monitored_barrier(
                group=get_tp_group().cpu_group,
                timeout=datetime.timedelta(seconds=UNBALANCED_MODEL_LOADING_TIMEOUT_S),
                wait_all_ranks=True,
            )
        except RuntimeError:
            raise ValueError(
                f"TP rank {self.tp_rank} could finish the model loading, but there are other ranks that didn't finish loading. It is likely due to unexpected failures (e.g., OOM) or a slow node."
            ) from None

    def update_weights_from_disk(
        self, model_path: str, load_format: str
    ) -> tuple[bool, str]:
        """Update engine weights in-place from the disk."""
        logger.info(
            f"Update engine weights online from disk begin. "
            f"avail mem={get_available_gpu_memory(self.device, self.gpu_id):.2f} GB"
        )

        target_device = torch.device(self.device)
        self.model_config.model_path = model_path
        load_config = LoadConfig(load_format=load_format)

        # Only support DefaultModelLoader for now
        loader = get_model_loader(load_config)
        if not isinstance(loader, DefaultModelLoader):
            message = f"Failed to get model loader: {loader}."
            return False, message

        def get_weight_iter(config):
            iter = loader._get_weights_iterator(
                DefaultModelLoader.Source(
                    config.model_path,
                    revision=config.revision,
                    fall_back_to_pt=getattr(
                        self.model, "fall_back_to_pt_during_load", True
                    ),
                )
            )
            return iter

        def model_load_weights(model, iter):
            model.load_weights(iter)
            for _, module in self.model.named_modules():
                quant_method = getattr(module, "quant_method", None)
                if quant_method is not None:
                    with device_loading_context(module, target_device):
                        quant_method.process_weights_after_loading(module)
            return model

        with set_default_torch_dtype(self.model_config.dtype):
            try:
                iter = get_weight_iter(self.model_config)
            except Exception as e:
                message = f"Failed to get weights iterator: {e}."
                return False, message
            try:
                model = model_load_weights(self.model, iter)
            except Exception as e:
                message = (
                    f"Failed to update weights: {e}.\nRolling back to original weights."
                )
                del iter
                gc.collect()
                iter = get_weight_iter(self.model_config)
                self.model = model_load_weights(self.model, iter)
                return False, message

        self.model = model
        self.server_args.model_path = model_path
        self.server_args.load_format = load_format
        self.load_config = load_config

        logger.info("Update weights end.")
        return True, "Succeeded to update model weights."

    def init_weights_update_group(
        self,
        master_address,
        master_port,
        rank_offset,
        world_size,
        group_name,
        backend="nccl",
    ):
        """Initialize the Torch process group for model parameter updates.

        `_model_update_group` is used in the RLHF workflow, where rank
        0 is the actor model in the training engine, and the other ranks are
        the inference engine, which is used for rollout.

        In the RLHF workflow, the training engine updates the model
        weights/parameters online, and broadcasts them to the inference
        engine through the `_model_update_group` process group.
        """
        assert (
            torch.distributed.is_initialized()
        ), "Default torch process group must be initialized"
        assert group_name != "", "Group name cannot be empty"

        rank = rank_offset + self.tp_rank

        logger.info(
            f"init custom process group: master_address={master_address}, master_port={master_port}, "
            f"rank_offset={rank_offset}, rank={rank}, world_size={world_size}, group_name={group_name}, backend={backend}"
        )

        try:
            self._model_update_group = init_custom_process_group(
                backend=backend,
                init_method=f"tcp://{master_address}:{master_port}",
                world_size=world_size,
                rank=rank,
                group_name=group_name,
            )
            dist.barrier(group=self._model_update_group, device_ids=[rank])
            return True, "Succeeded to initialize custom process group."
        except Exception as e:
            message = f"Failed to initialize custom process group: {e}."
            logger.error(message)
            return False, message

    def update_weights_from_distributed(self, name, dtype, shape):
        """
        Update specific parameter in the model weights online
        through `_model_update_group` process group.

        Args:
            name: the name of the parameter to be updated.
            dtype: the data type of the parameter to be updated.
            shape: the shape of the parameter to be updated.
        """
        target_dtype = (
            dtype if isinstance(dtype, torch.dtype) else getattr(torch, dtype)
        )

        assert (
            self._model_update_group is not None
        ), "model update group must be initialized"

        try:
            weights = torch.empty(shape, dtype=target_dtype, device=self.device)
            torch.distributed.broadcast(weights, src=0, group=self._model_update_group)
            self.model.load_weights([(name, weights)])
            return True, f"Succeeded to update parameter {name} online."

        except Exception as e:
            error_msg = (
                f"Failed to update parameter online: {e}. "
                f"The full weights of the ModelRunner are partially updated. "
                f"Please discard the whole weights."
            )
            logger.error(error_msg)
            return False, error_msg

    def update_weights_from_tensor(
        self,
        named_tensors: List[Tuple[str, Union[torch.Tensor, "LocalSerializedTensor"]]],
        load_format: Optional[str] = None,
    ):
        named_tensors = [
            (name, _unwrap_tensor(tensor, tp_rank=self.tp_rank))
            for name, tensor in named_tensors
        ]
        if load_format == "direct":
            _model_load_weights_direct(self.model, named_tensors)
        elif load_format is None:
            self.model.load_weights(named_tensors)
        else:
            raise NotImplementedError(f"Unknown load_format={load_format}")
        return True, "Success"

    def get_weights_by_name(
        self, name: str, truncate_size: int = 100
    ) -> Optional[torch.Tensor]:
        """Get the weights of the parameter by its name. Similar to `get_parameter` in Hugging Face.

        Only used for unit test with an unoptimized performance.
        For optimized performance, please use torch.save and torch.load.
        """
        # TODO: (chenyang) Add support for Qwen models.
        try:
            return self.model.get_weights_by_name(
                name, truncate_size, tp_size=self.tp_size
            )
        except Exception as e:
            logger.error(f"Error when getting parameter {name}: {e}")
            return None

    def profile_max_num_token(self, total_gpu_memory: int):
        available_gpu_memory = get_available_gpu_memory(
            self.device, self.gpu_id, distributed=self.tp_size > 1
        )
        # BACKPORT: for hybrid GDN models only full-attention layers consume
        # KV cache; mamba state memory is carved out separately below.
        if mambaish := self.mambaish_config:
            num_kv_layers = len(mambaish.full_attention_layer_ids)
        else:
            num_kv_layers = self.model_config.num_hidden_layers
        if self.use_mla_backend:
            cell_size = (
                (self.model_config.kv_lora_rank + self.model_config.qk_rope_head_dim)
                * num_kv_layers
                * torch._utils._element_size(self.kv_cache_dtype)
            )
        else:
            cell_size = (
                self.model_config.get_num_kv_heads(get_attention_tp_size())
                * self.model_config.head_dim
                * num_kv_layers
                * 2
                * torch._utils._element_size(self.kv_cache_dtype)
            )
        rest_memory = available_gpu_memory - total_gpu_memory * (
            1 - self.mem_fraction_static
        )
        if self.mambaish_config is not None:
            rest_memory = self.handle_max_mamba_cache(rest_memory)
        max_num_token = int(rest_memory * (1 << 30) // cell_size)
        return max_num_token

    # BACKPORT: from sglang v0.5.9 model_runner_kv_cache_mixin.py
    def handle_max_mamba_cache(self, total_rest_memory):
        config = self.mambaish_config
        server_args = self.server_args
        assert config is not None

        # reserve the memory for the intermediate mamba states used for spec dec
        if not self.spec_algorithm.is_none():
            assert server_args.speculative_num_draft_tokens is not None
            assert server_args.max_running_requests is not None

            max_running_requests = server_args.max_running_requests // (
                server_args.dp_size if server_args.enable_dp_attention else 1
            )
            mamba_state_intermediate_size = (
                config.mamba2_cache_params.mamba_cache_per_req
                * max_running_requests
                * server_args.speculative_num_draft_tokens
            )
            total_rest_memory = total_rest_memory - (
                mamba_state_intermediate_size / (1 << 30)
            )

        if server_args.max_mamba_cache_size is not None:
            # Use explicitly set max_mamba_cache_size
            pass
        elif (
            server_args.disable_radix_cache
            and server_args.max_running_requests is not None
        ):
            # Use explicitly set max_running_requests when radix cache is disabled
            server_args.max_mamba_cache_size = server_args.max_running_requests
        else:
            # Use ratio-based calculation to auto-fit available memory
            assert config.mamba2_cache_params.mamba_cache_per_req > 0

            # allocate the memory based on the ratio between mamba state memory vs. full kv cache memory
            # solve the equations:
            # 1. mamba_state_memory + full_kv_cache_memory == total_rest_memory
            # 2. mamba_state_memory / full_kv_cache_memory == server_args.mamba_full_memory_ratio
            mamba_state_memory_raw = (
                total_rest_memory
                * server_args.mamba_full_memory_ratio
                / (1 + server_args.mamba_full_memory_ratio)
            )
            # calculate the max_mamba_cache_size based on the given total mamba memory
            server_args.max_mamba_cache_size = int(
                (mamba_state_memory_raw * (1 << 30))
                // config.mamba2_cache_params.mamba_cache_per_req
            )

        mamba_state_memory = (
            server_args.max_mamba_cache_size
            * config.mamba2_cache_params.mamba_cache_per_req
            / (1 << 30)
        )
        return total_rest_memory - mamba_state_memory

    def init_memory_pool(
        self,
        total_gpu_memory: int,
        max_num_reqs: Optional[int] = None,
        max_total_tokens: Optional[int] = None,
    ):
        if self.server_args.kv_cache_dtype == "auto":
            self.kv_cache_dtype = self.dtype
        elif self.server_args.kv_cache_dtype == "fp8_e5m2":
            if is_hip():  # Using natively supported format
                self.kv_cache_dtype = torch.float8_e5m2fnuz
            else:
                self.kv_cache_dtype = torch.float8_e5m2
        elif self.server_args.kv_cache_dtype == "fp8_e4m3":
            if is_cuda():
                self.kv_cache_dtype = torch.float8_e4m3fn
        else:
            raise ValueError(
                f"Unsupported kv_cache_dtype: {self.server_args.kv_cache_dtype}."
            )

        self.max_total_num_tokens = self.profile_max_num_token(total_gpu_memory)

        if max_num_reqs is None:
            max_num_reqs = min(
                max(
                    int(
                        self.max_total_num_tokens / self.model_config.context_len * 512
                    ),
                    2048,
                ),
                4096,
            )

        # BACKPORT: cap the number of requests by the mamba cache size (v0.5.9)
        if self.mambaish_config is not None:
            additional_ratio = 0
            if self.server_args.enable_mamba_extra_buffer():
                if not self.spec_algorithm.is_none():
                    additional_ratio = MAMBA_CACHE_V2_ADDITIONAL_RATIO_NO_OVERLAP
                else:
                    additional_ratio = MAMBA_CACHE_V2_ADDITIONAL_RATIO_OVERLAP
            if self.server_args.disable_radix_cache:
                ratio = 1
            else:
                ratio = MAMBA_CACHE_SIZE_MAX_RUNNING_REQUESTS_RATIO + additional_ratio
            max_num_reqs = min(
                max_num_reqs, self.server_args.max_mamba_cache_size // ratio
            )

        if SGLANG_CI_SMALL_KV_SIZE:
            self.max_total_num_tokens = int(SGLANG_CI_SMALL_KV_SIZE)

        if not self.spec_algorithm.is_none():
            if self.is_draft_worker:
                self.max_total_num_tokens = self.server_args.draft_runner_cache_size
                max_num_reqs = self.server_args.max_num_reqs
            else:
                # We are sharing the `token_to_kv_pool`, and both verify and draft tokens
                # can be concurrently allocated, so we should give a headroom for it.
                self.server_args.draft_runner_cache_size = (
                    self.max_total_num_tokens
                    # draft
                    + max_num_reqs
                    * self.server_args.speculative_num_steps
                    * self.server_args.speculative_eagle_topk
                    # verify
                    + max_num_reqs * self.server_args.speculative_num_draft_tokens
                    # buffer
                    + 100
                )
                # Target worker and draft worker shares the same indices for the
                # token_to_kv_pool, so we should make sure to match max_total_num_tokens.
                self.max_total_num_tokens = self.server_args.draft_runner_cache_size
                self.server_args.max_num_reqs = max_num_reqs

        if max_total_tokens is not None:
            if max_total_tokens > self.max_total_num_tokens:
                logging.warning(
                    f"max_total_tokens={max_total_tokens} is larger than the profiled value "
                    f"{self.max_total_num_tokens}. "
                    f"Use the profiled value instead."
                )
            self.max_total_num_tokens = min(self.max_total_num_tokens, max_total_tokens)

        self.max_total_num_tokens = (
            self.max_total_num_tokens
            // self.server_args.page_size
            * self.server_args.page_size
        )

        if self.max_total_num_tokens <= 0:
            raise RuntimeError(
                "Not enough memory. Please try to increase --mem-fraction-static."
            )

        if self.req_to_token_pool is None:
            # BACKPORT: hybrid GDN models use a hybrid req-to-token pool (v0.5.9)
            if mambaish := self.mambaish_config:
                self.req_to_token_pool = HybridReqToTokenPool(
                    size=max_num_reqs + 1,
                    mamba_size=self.server_args.max_mamba_cache_size,
                    mamba_spec_state_size=max_num_reqs + 1,
                    max_context_len=self.model_config.context_len + 4,
                    device=self.device,
                    enable_memory_saver=self.server_args.enable_memory_saver,
                    cache_params=mambaish.mamba2_cache_params,
                    enable_mamba_extra_buffer=self.server_args.enable_mamba_extra_buffer(),
                    speculative_num_draft_tokens=self.server_args.speculative_num_draft_tokens,
                )
            else:
                self.req_to_token_pool = ReqToTokenPool(
                    size=max_num_reqs + 1,
                    max_context_len=self.model_config.context_len + 4,
                    device=self.device,
                    enable_memory_saver=self.server_args.enable_memory_saver,
                )
        else:
            # Draft worker shares req_to_token_pool with the target worker.
            assert self.is_draft_worker

        # BACKPORT: hybrid GDN models use a hybrid linear KV pool (v0.5.9)
        if mambaish := self.mambaish_config:
            extra_args = {}
            if self.use_mla_backend:
                extra_args = {
                    "kv_lora_rank": self.model_config.kv_lora_rank,
                    "qk_rope_head_dim": self.model_config.qk_rope_head_dim,
                }
            self.token_to_kv_pool = HybridLinearKVPool(
                page_size=self.page_size,
                size=self.max_total_num_tokens,
                dtype=self.kv_cache_dtype,
                head_num=self.model_config.get_num_kv_heads(get_attention_tp_size()),
                head_dim=self.model_config.head_dim,
                # if draft worker, we only need 1 attention layer's kv pool
                full_attention_layer_ids=(
                    [0] if self.is_draft_worker else mambaish.full_attention_layer_ids
                ),
                enable_kvcache_transpose=False,
                device=self.device,
                mamba_pool=self.req_to_token_pool.mamba_pool,
                enable_memory_saver=self.server_args.enable_memory_saver,
                use_mla=self.use_mla_backend,
                **extra_args,
            )
        elif self.use_mla_backend:
            self.token_to_kv_pool = MLATokenToKVPool(
                self.max_total_num_tokens,
                page_size=self.page_size,
                dtype=self.kv_cache_dtype,
                kv_lora_rank=self.model_config.kv_lora_rank,
                qk_rope_head_dim=self.model_config.qk_rope_head_dim,
                layer_num=self.model_config.num_hidden_layers,
                device=self.device,
                enable_memory_saver=self.server_args.enable_memory_saver,
            )
        else:
            self.token_to_kv_pool = MHATokenToKVPool(
                self.max_total_num_tokens,
                page_size=self.page_size,
                dtype=self.kv_cache_dtype,
                head_num=self.model_config.get_num_kv_heads(get_attention_tp_size()),
                head_dim=self.model_config.head_dim,
                layer_num=self.model_config.num_hidden_layers,
                device=self.device,
                enable_memory_saver=self.server_args.enable_memory_saver,
            )

        if self.token_to_kv_pool_allocator is None:
            if self.page_size == 1:
                self.token_to_kv_pool_allocator = TokenToKVPoolAllocator(
                    self.max_total_num_tokens,
                    dtype=self.kv_cache_dtype,
                    device=self.device,
                    kvcache=self.token_to_kv_pool,
                )
            else:
                self.token_to_kv_pool_allocator = PagedTokenToKVPoolAllocator(
                    self.max_total_num_tokens,
                    page_size=self.page_size,
                    dtype=self.kv_cache_dtype,
                    device=self.device,
                    kvcache=self.token_to_kv_pool,
                )
        else:
            assert self.is_draft_worker

        logger.info(
            f"Memory pool end. "
            f"avail mem={get_available_gpu_memory(self.device, self.gpu_id):.2f} GB"
        )

    def init_cublas(self):
        """We need to run a small matmul to init cublas. Otherwise, it will raise some errors later."""
        dtype = torch.float16
        device = "cuda"
        a = torch.ones((16, 16), dtype=dtype, device=device)
        b = torch.ones((16, 16), dtype=dtype, device=device)
        c = a @ b
        return c

    def init_attention_backend(self):
        """Init attention kernel backend."""
        # SLIM: removed flashinfer / flashinfer_mla / torch_native / flashmla /
        # fa3 / cutlass_mla / double-sparsity backend branches (fixed Qwen3.5-2B
        # config: attention_backend="triton")
        assert self.sliding_window_size is None, (
            "Window attention is not supported in the triton attention backend. "
            "Please use `--attention-backend flashinfer`."
        )
        assert not self.model_config.is_encoder_decoder, (
            "Cross attention is not supported in the triton attention backend. "
            "Please use `--attention-backend flashinfer`."
        )
        from sglang.srt.layers.attention.triton_backend import TritonAttnBackend

        self.attn_backend = TritonAttnBackend(self)

        # BACKPORT: wrap the full-attention backend for hybrid GDN models
        # (Qwen3-Next / Qwen3.5), from sglang v0.5.9 attn_backend_wrapper.
        # The user-selected attention_backend (e.g. "triton") is kept as the
        # full-attention sub-backend.
        # The draft (MTP) model has a single full-attention layer and no GDN
        # layers, so it keeps the bare triton backend.
        if self.hybrid_gdn_config is not None and not self.is_draft_worker:
            from sglang.srt.layers.attention.fla.utils import check_environments
            from sglang.srt.layers.attention.hybrid_linear_attn_backend import (
                GDNAttnBackend,
                HybridLinearAttnBackend,
            )

            assert not self.use_mla_backend, (
                "hybrid_gdn can only be used with non-MLA models."
            )
            check_environments()
            logger.info(
                "Using hybrid linear attention backend for hybrid GDN models."
            )
            linear_attn_backend = GDNAttnBackend(self)
            full_attn_layers = self.hybrid_gdn_config.full_attention_layer_ids
            self.attn_backend = HybridLinearAttnBackend(
                self.attn_backend, linear_attn_backend, full_attn_layers
            )

    def init_cuda_graphs(self):
        """Capture cuda graphs."""
        self.cuda_graph_runner = None

        if not self.is_generation:
            # Cuda graph only captures decode steps, which only exist for
            # generation models.
            return

        if self.server_args.disable_cuda_graph:
            return

        # BACKPORT-PPU: the pre-slim tree skipped capture for hybrid GDN
        # models; the bs=1 decode-only capture path is now supported by the
        # hybrid linear attention backend, so the skip is removed.
        tic = time.time()
        before_mem = get_available_gpu_memory(self.device, self.gpu_id)
        logger.info(
            f"Capture cuda graph begin. This can take up to several minutes. avail mem={before_mem:.2f} GB"
        )
        self.cuda_graph_runner = CudaGraphRunner(self)
        # MTP phase 2: capture the TARGET_VERIFY graph (fixed 2-token chain
        # verify) for the target model when speculation is enabled. The
        # draft model's DRAFT_EXTEND graphs are created by the MTPWorker.
        if not self.spec_algorithm.is_none() and not self.is_draft_worker:
            self.cuda_graph_verify_runner = MtpTargetVerifyGraphRunner(self)
        after_mem = get_available_gpu_memory(self.device, self.gpu_id)
        logger.info(
            f"Capture cuda graph end. Time elapsed: {time.time() - tic:.2f} s. "
            f"mem usage={(before_mem - after_mem):.2f} GB. avail mem={after_mem:.2f} GB."
        )

    def apply_torch_tp(self):
        logger.info(f"Enabling torch tensor parallelism on {self.tp_size} devices.")
        from sglang.srt.model_parallel import tensor_parallel

        device_mesh = torch.distributed.init_device_mesh(self.device, (self.tp_size,))
        tensor_parallel(self.model, device_mesh)

    def forward_decode(self, forward_batch: ForwardBatch):
        self.attn_backend.init_forward_metadata(forward_batch)
        return self.model.forward(
            forward_batch.input_ids, forward_batch.positions, forward_batch
        )

    def forward_extend(
        self, forward_batch: ForwardBatch, skip_attn_backend_init: bool = False
    ):
        if not skip_attn_backend_init:
            self.attn_backend.init_forward_metadata(forward_batch)

        if self.is_generation:
            if forward_batch.input_embeds is None:
                ret = self.model.forward(
                    forward_batch.input_ids, forward_batch.positions, forward_batch
                )
            else:
                ret = self.model.forward(
                    forward_batch.input_ids,
                    forward_batch.positions,
                    forward_batch,
                    input_embeds=forward_batch.input_embeds.bfloat16(),
                )
            return ret
        else:
            # Only embedding models have get_embedding parameter
            return self.model.forward(
                forward_batch.input_ids,
                forward_batch.positions,
                forward_batch,
                get_embedding=True,
            )

    def forward_idle(self, forward_batch: ForwardBatch):
        return self.model.forward(
            forward_batch.input_ids, forward_batch.positions, forward_batch
        )

    def forward(
        self, forward_batch: ForwardBatch, skip_attn_backend_init: bool = False
    ) -> LogitsProcessorOutput:
        # BACKPORT-PPU: restored CUDA graph replay branch (bs=1 decode only).
        if forward_batch.forward_mode.is_cuda_graph():
            # MTP phase 2: spec-mode graphs take precedence.
            if (
                forward_batch.forward_mode.is_target_verify()
                and self.cuda_graph_verify_runner is not None
                and self.cuda_graph_verify_runner.can_run(forward_batch)
            ):
                return self.cuda_graph_verify_runner.replay(forward_batch)
            if (
                forward_batch.forward_mode.is_draft_extend()
                and self.cuda_graph_draft_runner is not None
                and self.cuda_graph_draft_runner.can_run(forward_batch)
            ):
                return self.cuda_graph_draft_runner.replay(forward_batch)
            if self.cuda_graph_runner and self.cuda_graph_runner.can_run(
                forward_batch
            ):
                return self.cuda_graph_runner.replay(
                    forward_batch, skip_attn_backend_init=skip_attn_backend_init
                )

        if forward_batch.forward_mode.is_decode():
            return self.forward_decode(forward_batch)
        elif forward_batch.forward_mode.is_extend():
            # SGLANG_EXTEND_GRAPH: bucketed prefill graph takes precedence
            # over the eager path for plain bs=1 extends that fit the bucket.
            if (
                self.extend_graph_runner is not None
                and forward_batch.spec_info is None
                and self.extend_graph_runner.can_run(forward_batch)
            ):
                return self.extend_graph_runner.replay(forward_batch)
            from sglang.srt.ttft_prof import ENABLED as _TTFT_PROF, mark as _ttft_mark

            if _TTFT_PROF and forward_batch.spec_info is None:
                torch.cuda.synchronize()
                _ext_t0 = time.perf_counter()
                ret = self.forward_extend(
                    forward_batch, skip_attn_backend_init=skip_attn_backend_init
                )
                torch.cuda.synchronize()
                _ttft_mark(
                    "extend_gpu",
                    _ext_t0,
                    mode=str(forward_batch.forward_mode),
                    extend_num_tokens=forward_batch.extend_num_tokens,
                )
                return ret
            # SGLANG_PREFILL_TRACE=1: chrome trace for the first real prefill,
            # to test the launch-bound hypothesis (kernel count vs wall time).
            if (
                os.environ.get("SGLANG_PREFILL_TRACE", "0") == "1"
                and forward_batch.spec_info is None
            ):
                # Skip the first prefill (one-time Triton JIT); trace the 2nd.
                self._prefill_seen = getattr(self, "_prefill_seen", 0) + 1
                if self._prefill_seen < 2:
                    return self.forward_extend(
                        forward_batch, skip_attn_backend_init=skip_attn_backend_init
                    )
                from torch.profiler import ProfilerActivity, profile

                os.environ["SGLANG_PREFILL_TRACE"] = "0"
                torch.cuda.synchronize()
                with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA]) as prof:
                    ret = self.forward_extend(
                        forward_batch, skip_attn_backend_init=skip_attn_backend_init
                    )
                    torch.cuda.synchronize()
                prof.export_chrome_trace("/root/prefill_trace.json")
                return ret
            return self.forward_extend(
                forward_batch, skip_attn_backend_init=skip_attn_backend_init
            )
        elif forward_batch.forward_mode.is_idle():
            return self.forward_idle(forward_batch)
        else:
            raise ValueError(f"Invalid forward mode: {forward_batch.forward_mode}")

    def _preprocess_logits(
        self, logits_output: LogitsProcessorOutput, sampling_info: SamplingBatchInfo
    ):
        # Apply logit bias
        if sampling_info.sampling_info_done:
            # Overlap mode: the function update_regex_vocab_mask was executed
            # in process_batch_result of the last batch.
            if sampling_info.grammars:
                sampling_info.sampling_info_done.wait()
        else:
            # Normal mode: Put CPU-heavy tasks here. They will be overlapped with the forward pass.
            sampling_info.update_regex_vocab_mask()
        sampling_info.apply_logits_bias(logits_output.next_token_logits)

    def sample(
        self,
        logits_output: LogitsProcessorOutput,
        forward_batch: ForwardBatch,
    ) -> torch.Tensor:
        """Sample and compute logprobs and update logits_output.

        Args:
            logits_output: The logits output from the model forward
            forward_batch: The forward batch that generates logits_output

        Returns:
            A list of next_token_ids
        """
        # For duplex models with multiple output streams.
        if isinstance(logits_output, tuple):
            return torch.stack(
                [self.sample(values, forward_batch) for values in logits_output],
                axis=-1,
            )

        self._preprocess_logits(logits_output, forward_batch.sampling_info)

        # Sample the next tokens
        next_token_ids = self.sampler(
            logits_output,
            forward_batch.sampling_info,
            forward_batch.return_logprob,
            forward_batch.top_logprobs_nums,
            forward_batch.token_ids_logprobs,
        )
        return next_token_ids

    @property
    def model_is_mrope(self) -> bool:
        """Detect if the model has "mrope" rope_scaling type.
        mrope requires keep "rope_deltas" between prompt and decoding phases."""
        # BACKPORT: v0.5.9 detection — Qwen3.5/Qwen3-VL expose mrope under
        # text_config.rope_parameters (0.4.6 only checked hf_config.rope_scaling).
        rope_scaling = getattr(
            self.model_config.hf_text_config, "rope_parameters", None
        ) or getattr(self.model_config.hf_text_config, "rope_scaling", {})
        if rope_scaling is None:
            return False
        is_mrope_enabled = "mrope_section" in rope_scaling
        return is_mrope_enabled

    # BACKPORT: hybrid GDN (Qwen3-Next / Qwen3.5) support from sglang v0.5.9.
    @property
    def hybrid_gdn_config(self):
        # Imported lazily to avoid a module import cycle with model_runner.
        from sglang.srt.configs.qwen3_5 import Qwen3_5Config, Qwen3_5MoeConfig
        from sglang.srt.configs.qwen3_next import Qwen3NextConfig

        config = self.model_config.hf_config.get_text_config()
        if isinstance(config, (Qwen3NextConfig, Qwen3_5Config, Qwen3_5MoeConfig)):
            return config
        return None

    @property
    def mambaish_config(self):
        # v0.5.9 also covers mamba2 / kimi_linear / lightning configs here;
        # only hybrid GDN is backported.
        return self.hybrid_gdn_config

    def save_remote_model(self, url: str):
        # SLIM: RemoteModelLoader removed (model path is always a local dir)
        raise NotImplementedError("remote model saving is not supported")

    def save_sharded_model(
        self, path: str, pattern: Optional[str] = None, max_size: Optional[int] = None
    ):
        from sglang.srt.model_loader.loader import ShardedStateLoader

        logger.info(
            f"Save sharded model to {path} with pattern {pattern} and max_size {max_size}"
        )
        ShardedStateLoader.save_model(self.model, path, pattern, max_size)


def _model_load_weights_direct(model, named_tensors: List[Tuple[str, torch.Tensor]]):
    params_dict = dict(model.named_parameters())
    for name, tensor in named_tensors:
        default_weight_loader(params_dict[name], tensor)


def _unwrap_tensor(tensor, tp_rank):
    if isinstance(tensor, LocalSerializedTensor):
        monkey_patch_torch_reductions()
        tensor = tensor.get(tp_rank)
    return tensor.to(torch.cuda.current_device())


@dataclass
class LocalSerializedTensor:
    """torch.Tensor that gets serialized by MultiprocessingSerializer (which only serializes a pointer and not the data).
    The i-th element in the list corresponds to i-th rank's GPU."""

    values: List[bytes]

    def get(self, rank: int):
        return MultiprocessingSerializer.deserialize(self.values[rank])
