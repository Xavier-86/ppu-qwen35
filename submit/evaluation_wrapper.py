"""Participant model wrapper for the DNDX benchmark."""

from __future__ import annotations

import logging
import os
import re
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


_ANSWER_MARK = r"(?:\*{1,3}|_{1,3}|`{1,3})*"
_ANSWER_CHOICE = (
    rf"{_ANSWER_MARK}\s*[\(\[（【]?\s*([ABCD])\s*[\)\]）】]?"
    rf"\s*{_ANSWER_MARK}"
)
_ANSWER_PATTERNS = (
    re.compile(
        r"(?:final\s*)?(?:answer|choice|option|答案|选项|选择|正确答案|最终答案)"
        rf"\s*(?:(?:is|为|是|[:：])\s*)*{_ANSWER_CHOICE}",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:我(?:会)?选|我认为(?:是)?|应(?:该)?选|请选择|选|答案为|答案是)"
        rf"\s*(?:[:：]\s*)?{_ANSWER_CHOICE}",
        re.IGNORECASE,
    ),
    re.compile(
        rf"^\s*{_ANSWER_CHOICE}\s*(?:[\.。,:：\)\]）】\s]|$)",
        re.IGNORECASE | re.MULTILINE,
    ),
)


def _has_explicit_choice(text: str) -> bool:
    return any(pattern.search(text or "") for pattern in _ANSWER_PATTERNS)


@dataclass
class GenerationConfig:
    max_new_tokens: int
    temperature: float = 0.0
    top_p: float = 1.0


@dataclass
class GenerationResult:
    text: str
    token_count: int
    ttft_seconds: float
    elapsed_seconds: float
    meta: dict[str, Any]


class VLMModel:
    """
    Default participant wrapper.

    `backend="sglang"` uses the local SGLang source under `rapid_reasoning/`.
    `backend="transformers"` uses a local Hugging Face model directory.
    `backend="dummy"` is for demo-only smoke tests.
    Participants can replace the internals while preserving `generate_with_metrics`.
    """

    def __init__(
        self,
        model_path: str,
        *,
        backend: str = "sglang",
        device: str = "cuda",
    ) -> None:
        self.model_path = model_path
        self.device = device
        self.backend = backend
        self._model = None
        self._processor = None
        self._tokenizer = None
        self._chat_template = None
        self._backend_name = "dummy"

        # Resolve participant-owned runtime code before probing any backend.
        # This also makes backend="auto" independent of a site-packages
        # SGLang installation.
        self._prefer_local_sglang_source()
        if backend == "auto":
            try:
                import sglang as sgl  # noqa: F401
                backend = "sglang"
            except Exception:
                backend = "transformers"
            self.backend = backend

        if backend == "sglang":
            self._load_sglang_backend()
            self._backend_name = "sglang"
        elif backend == "transformers":
            self._load_transformers_backend()
            self._backend_name = "transformers"
        elif backend == "dummy":
            self._load_dummy_backend("backend=dummy")
        else:
            raise ValueError(f"Unsupported backend: {backend}")

    @property
    def backend_name(self) -> str:
        return self._backend_name

    def generate_with_metrics(
        self,
        *,
        image,
        prompt: str,
        choices: dict[str, str],
        generation_config: GenerationConfig,
        sample_id: str,
    ) -> GenerationResult:
        if self._backend_name == "sglang":
            return self._generate_with_sglang(
                image=image,
                prompt=prompt,
                generation_config=generation_config,
            )
        if self._backend_name == "transformers":
            return self._generate_with_transformers(
                image=image,
                prompt=prompt,
                generation_config=generation_config,
            )
        return self._generate_with_dummy(
            prompt=prompt,
            choices=choices,
            generation_config=generation_config,
            sample_id=sample_id,
        )

    def shutdown(self) -> None:
        """Release backend resources cleanly before process exit."""
        engine = getattr(self, "_sgl_engine", None)
        if engine is not None:
            try:
                engine.shutdown()
            except Exception:
                pass
            self._sgl_engine = None
        torch_mod = getattr(self, "_torch", None)
        if torch_mod is not None:
            try:
                if torch_mod.cuda.is_available():
                    torch_mod.cuda.synchronize()
                    torch_mod.cuda.empty_cache()
                    torch_mod.cuda.synchronize()
            except Exception:
                pass
        # Stop Python's resource_tracker daemon to avoid noisy warnings
        # when sglang child processes release shared memory on exit.
        try:
            from multiprocessing.resource_tracker import _resource_tracker
            _resource_tracker.stop()
        except Exception:
            pass

    def _load_dummy_backend(self, reason: str) -> None:
        self._dummy_reason = reason

    def _filter_noisy_dependency_warnings(self) -> None:
        def _is_noisy_transformers_deprecation(message: str) -> bool:
            return (
                "deprecated" in message
                and ("use_fast" in message or "torch_dtype" in message)
            )

        original_handle = logging.Logger.handle
        if not getattr(original_handle, "_sglang_filtered", False):

            def _filtered_handle(logger_self, record):
                if _is_noisy_transformers_deprecation(record.getMessage()):
                    return
                return original_handle(logger_self, record)

            _filtered_handle._sglang_filtered = True
            logging.Logger.handle = _filtered_handle

        class _TransformersDeprecationFilter(logging.Filter):
            def filter(self, record: logging.LogRecord) -> bool:
                return not _is_noisy_transformers_deprecation(record.getMessage())

        logging.getLogger("transformers").addFilter(_TransformersDeprecationFilter())

    def _prefer_local_sglang_source(self) -> None:
        local_source = Path(__file__).resolve().parent / "rapid_reasoning"
        runtime_packages = local_source / "runtime_packages"
        use_bundled_kernel = os.environ.get(
            "DNDX_DIAG_USE_BUNDLED_SGL_KERNEL", "1"
        ) == "1"
        required = [
            local_source / "sglang" / "__init__.py",
            runtime_packages / "triton" / "__init__.py",
            runtime_packages / "triton" / "_C" / "libtriton.so",
        ]
        if use_bundled_kernel:
            required.extend(
                (
                    runtime_packages / "sgl_kernel" / "__init__.py",
                    runtime_packages / "sgl_kernel" / "common_ops.abi3.so",
                )
            )
        missing = [str(path) for path in required if not path.is_file()]
        if missing:
            raise RuntimeError(
                "Incomplete dndx runtime bundle; missing: " + ", ".join(missing)
            )
        local_paths = [str(local_source)]
        if use_bundled_kernel:
            local_paths.insert(0, str(runtime_packages))
        sys.path[:] = [path for path in sys.path if path not in local_paths]
        sys.path[:0] = local_paths

    @staticmethod
    def _assert_local_runtime_module(module, package_name: str) -> None:
        bundle_root = Path(__file__).resolve().parent / "rapid_reasoning"
        module_file = Path(module.__file__).resolve()
        if not module_file.is_relative_to(bundle_root):
            raise RuntimeError(
                f"{package_name} resolved outside dndx bundle: {module_file}"
            )

    @staticmethod
    def _silence_resource_tracker() -> None:
        """Prevent spurious resource_tracker warnings from SGLang shared memory cleanup.

        SGLang uses multiprocessing shared memory for inter-process communication.
        When child processes exit out of order, the stdlib resource_tracker may
        log warnings or KeyError tracebacks that are harmless but noisy. This
        disables tracking for shared_memory segments in the current process tree.
        """
        try:
            import multiprocessing.resource_tracker as resource_tracker

            # Remove the cleanup function so shared_memory segments are not tracked.
            resource_tracker._CLEANUP_FUNCS.pop("shared_memory", None)

            # Turn register/unregister into no-ops to stop the tracker daemon
            # from being spawned for shared memory in this process.
            def _noop(*args: Any, **kwargs: Any) -> None:
                pass

            resource_tracker.register = _noop
            resource_tracker.unregister = _noop

            # Stop the singleton tracker if it is already running.
            tracker = resource_tracker._resource_tracker
            if tracker._check_alive() and tracker._fd is not None:
                tracker.stop()
        except Exception:
            pass

    def _load_sglang_backend(self) -> None:
        self._prefer_local_sglang_source()
        self._filter_noisy_dependency_warnings()
        self._silence_resource_tracker()
        import sglang as sgl
        import sgl_kernel
        import torch
        import triton

        self._assert_local_runtime_module(sgl, "sglang")
        self._assert_local_runtime_module(triton, "triton")
        if os.environ.get("DNDX_DIAG_USE_BUNDLED_SGL_KERNEL", "1") == "1":
            self._assert_local_runtime_module(sgl_kernel, "sgl_kernel")
        self._torch = torch
        self._load_chat_template()
        # MTP self-speculative decoding (chain, topk=1, greedy). Chain depth
        # can be selected as 1..4 for A/B tests; both eager and graph
        # paths support the corresponding two- to five-token verify batch.
        # Default is the adaptive-depth configuration: max chain depth 4 with
        # the dynamic controller (SGLANG_MTP_DYNAMIC_DEPTH default 1 in
        # mtp_worker.py) choosing per-round depth from measured acceptance
        # rates. Set SGLANG_MTP_CHAIN_DEPTH=2 for the old fixed-depth path.
        # Enabled by default; set
        # SGLANG_ENABLE_MTP=0 for diagnostics. Server-side validation forces
        # disable_overlap_schedule / disable_cuda_graph when it is on.
        mtp_engine_kwargs: dict[str, Any] = {}
        if os.environ.get("SGLANG_ENABLE_MTP", "1") == "1":
            chain_depth = int(os.environ.get("SGLANG_MTP_CHAIN_DEPTH", "4"))
            if chain_depth not in (1, 2, 3, 4):
                raise ValueError("SGLANG_MTP_CHAIN_DEPTH must be 1, 2, 3 or 4")
            mtp_engine_kwargs = {
                "speculative_algorithm": "NEXTN",
                "speculative_num_steps": chain_depth,
                "speculative_eagle_topk": 1,
                "speculative_num_draft_tokens": chain_depth + 1,
            }
        capacity_kwargs: dict[str, Any] = {}
        if "SGLANG_MAX_RUNNING_REQUESTS" in os.environ:
            capacity_kwargs["max_running_requests"] = int(
                os.environ["SGLANG_MAX_RUNNING_REQUESTS"]
            )
        if "SGLANG_MAX_TOTAL_TOKENS" in os.environ:
            capacity_kwargs["max_total_tokens"] = int(
                os.environ["SGLANG_MAX_TOTAL_TOKENS"]
            )
        self._sgl_engine = sgl.Engine(
            model_path=self.model_path,
            trust_remote_code=True,
            dtype="bfloat16",
            # The competition evaluates one request on exactly one 810E.
            tp_size=1,
            enable_multimodal=True,
            attention_backend="triton",
            mem_fraction_static=float(
                os.environ.get("SGLANG_MEM_FRACTION_STATIC", "0.8")
            ),
            triton_attention_num_kv_splits=int(
                os.environ.get("SGLANG_TRITON_ATTENTION_KV_SPLITS", "8")
            ),
            # bs=1 decode CUDA graph capture is enabled by default; set
            # SGLANG_DISABLE_CUDA_GRAPH=1 to force the eager path (A/B).
            disable_cuda_graph=os.environ.get("SGLANG_DISABLE_CUDA_GRAPH", "0")
            == "1",
            **capacity_kwargs,
            **mtp_engine_kwargs,
        )

    def _load_transformers_backend(self) -> None:
        import torch
        from transformers import AutoModelForImageTextToText, AutoProcessor

        self._torch = torch
        self._processor = AutoProcessor.from_pretrained(
            self.model_path,
            local_files_only=True,
            trust_remote_code=True,
        )
        device = self.device
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self._model = AutoModelForImageTextToText.from_pretrained(
            self.model_path,
            local_files_only=True,
            trust_remote_code=True,
            torch_dtype=torch.bfloat16,
            device_map={"": device},
            attn_implementation="eager",
        ).eval()
        self._tokenizer = getattr(self._processor, "tokenizer", None)

    def _load_chat_template(self) -> None:
        template_path = Path(self.model_path) / "chat_template.jinja"
        self._chat_template = template_path.read_text(encoding="utf-8")

    def _build_sglang_prompt(self, prompt: str) -> str:
        from jinja2 import Environment, StrictUndefined

        def raise_exception(message: str) -> None:
            raise ValueError(message)

        messages = [{
            "role": "user",
            "content": [
                {"type": "image", "image": None},
                {"type": "text", "text": prompt},
            ],
        }]
        env = Environment(undefined=StrictUndefined)
        env.globals["raise_exception"] = raise_exception
        template = env.from_string(self._chat_template)
        return template.render(
            messages=messages,
            tools=None,
            add_generation_prompt=True,
            add_vision_id=False,
        )

    def _generate_with_sglang(
        self,
        *,
        image,
        prompt: str,
        generation_config: GenerationConfig,
    ) -> GenerationResult:
        sgl_prompt = self._build_sglang_prompt(prompt)
        sampling_params = {
            "max_new_tokens": generation_config.max_new_tokens,
            "temperature": generation_config.temperature,
            "top_p": generation_config.top_p,
        }

        start = time.perf_counter()
        first_chunk_at = None
        output = None
        previous_text = ""
        for chunk in self._sgl_engine.generate(
            prompt=sgl_prompt,
            image_data=image,
            sampling_params=sampling_params,
            stream=True,
        ):
            now = time.perf_counter()
            chunk_text = chunk.get("text") or ""
            if first_chunk_at is None and len(chunk_text) > len(previous_text):
                first_chunk_at = now
            previous_text = chunk_text
            output = chunk
        end = time.perf_counter()

        output = output or {}
        meta_info = output.get("meta_info") or {}
        text = (output.get("text") or "").strip()
        token_count = int(meta_info.get("completion_tokens") or len(output.get("output_ids") or []))
        # Generic output-validity fallback (report 2.14): no per-question,
        # per-language, or per-dataset special-casing. Any output without an
        # explicit A/B/C/D choice is answered again by the same model with the
        # evaluator's original sampling parameters; both generations' tokens
        # and wall time are merged into the metrics, TTFT stays with the
        # initial request.
        repair_enabled = os.environ.get("SGLANG_OUTPUT_REPAIR", "1") == "1"
        if repair_enabled and not _has_explicit_choice(text):
            initial_text = text
            initial_meta = dict(meta_info)
            repair_prompt = (
                f"{prompt}\n\n"
                "A previous attempt analyzed the question but did not state a "
                "valid final choice. Based on the question, image, choices, and "
                "analysis below, output only `Final answer: X`, where X is exactly "
                "one of A/B/C/D. Do not add any explanation.\n"
                "上一次回答进行了分析但没有给出有效选项。请根据题目、图片、选项和"
                "下方分析，只输出 `Final answer: X`，其中 X 只能是 A/B/C/D，"
                "不要添加解释。\n\n"
                f"Previous analysis / 上一次分析：\n{initial_text[:1600]}"
            )
            repair_output = None
            for chunk in self._sgl_engine.generate(
                prompt=self._build_sglang_prompt(repair_prompt),
                image_data=image,
                sampling_params=sampling_params,
                stream=True,
            ):
                repair_output = chunk
            end = time.perf_counter()
            repair_output = repair_output or {}
            repair_meta = repair_output.get("meta_info") or {}
            repair_text = (repair_output.get("text") or "").strip()
            repair_tokens = int(
                repair_meta.get("completion_tokens")
                or len(repair_output.get("output_ids") or [])
            )
            text = repair_text
            token_count += repair_tokens
            meta_info = dict(repair_meta)
            meta_info["completion_tokens"] = token_count
            meta_info["output_repair"] = {
                "initial_completion_tokens": token_count - repair_tokens,
                "repair_completion_tokens": repair_tokens,
                "initial_finish_reason": initial_meta.get("finish_reason"),
                "initial_e2e_latency": initial_meta.get("e2e_latency"),
            }
            meta_info["e2e_latency"] = end - start
        # The public interface limits returned display text to 1200 characters.
        # Keep token_count and both timing fields unchanged so all generated
        # work remains represented in the performance metrics.
        if len(text) > 1200:
            text = text[:1200]
        # Match the public reference wrapper exactly: all timing values use the
        # same local monotonic clock, TTFT ends when the first non-empty decoded
        # text chunk reaches this wrapper, and elapsed covers the full stream.
        elapsed = max(end - start, 0.0)
        raw_ttft = (
            (first_chunk_at - start) if first_chunk_at is not None else elapsed
        )
        ttft = min(max(raw_ttft, 0.0), elapsed)
        return GenerationResult(
            text=text,
            token_count=token_count,
            ttft_seconds=ttft,
            elapsed_seconds=elapsed,
            meta={
                "backend": "sglang",
                "metric_scope": "full_generate_call_to_visible_text",
                "sglang_meta": meta_info,
            },
        )

    def _generate_with_transformers(
        self,
        *,
        image,
        prompt: str,
        generation_config: GenerationConfig,
    ) -> GenerationResult:
        import torch
        from transformers import TextIteratorStreamer

        messages = [{
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": prompt},
            ],
        }]
        inputs = self._processor.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self._model.device)
        input_len = inputs.input_ids.shape[1]
        streamer = TextIteratorStreamer(
            self._processor.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True,
        )
        generation_kwargs = {
            **inputs,
            "max_new_tokens": generation_config.max_new_tokens,
            "temperature": generation_config.temperature,
            "top_p": generation_config.top_p,
            "do_sample": generation_config.temperature > 0,
            "use_cache": True,
            "streamer": streamer,
        }

        output_holder: dict[str, Any] = {}

        def _run_generate() -> None:
            with torch.no_grad():
                output_holder["output_ids"] = self._model.generate(**generation_kwargs)

        worker = threading.Thread(target=_run_generate, daemon=True)
        start = time.perf_counter()
        worker.start()

        first_chunk_at = None
        chunks: list[str] = []
        for chunk in streamer:
            now = time.perf_counter()
            if first_chunk_at is None and chunk:
                first_chunk_at = now
            chunks.append(chunk)
        worker.join()
        end = time.perf_counter()

        output_ids = output_holder["output_ids"]
        generated_ids = output_ids[0][input_len:]
        # Decode from the actual generated token IDs for a reliable text string.
        # The streamer is still used above to measure TTFT accurately.
        text = self._processor.tokenizer.decode(
            generated_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        ).strip()

        # Normalize common markdown bold markers so the benchmark answer
        # parser can extract A/B/C/D from outputs like "正确答案是：**B**".
        text = text.replace("**", "")

        ttft = (first_chunk_at - start) if first_chunk_at is not None else (end - start)
        return GenerationResult(
            text=text,
            token_count=int(generated_ids.shape[0]),
            ttft_seconds=ttft,
            elapsed_seconds=end - start,
            meta={"backend": "transformers"},
        )

    def _generate_with_dummy(
        self,
        *,
        prompt: str,
        choices: dict[str, str],
        generation_config: GenerationConfig,
        sample_id: str,
    ) -> GenerationResult:
        start = time.perf_counter()
        usable_choices = [key for key, value in choices.items() if (value or "").strip()]
        picked = usable_choices[hash(sample_id) % len(usable_choices)] if usable_choices else "A"
        text = (
            f"Answer: {picked}\n"
            f"Explanation: dummy backend selected a deterministic option for smoke testing."
        )
        token_count = max(1, min(generation_config.max_new_tokens, len(text.split())))
        end = time.perf_counter()
        return GenerationResult(
            text=text,
            token_count=token_count,
            ttft_seconds=max(end - start, 1e-4),
            elapsed_seconds=max(end - start, 2e-4),
            meta={"backend": "dummy", "reason": getattr(self, "_dummy_reason", "n/a"), "prompt_chars": len(prompt)},
        )
