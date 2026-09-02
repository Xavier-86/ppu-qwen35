# Asight 性能分析工具 · 比赛参考 <span style="float: right;"><a href="../../README.md">目录</a></span>

## 目录

- [文件](#文件)
- [比赛要点](#比赛要点)
- [配套](#配套)


> 面向比赛：基于 Qwen3.5-2B 的 VLM 在阿里平头哥 PPU 服务器上的高效推理优化。

## 文件

| 文件 | 内容 |
| --- | --- |
| [01_asight_systems.md](01_asight_systems.md) | Asight Systems（对标 Nsight Systems）：系统级 timeline 分析。安装/快速入门、跟踪目标程序（PPU 活动/metrics/HGTX/CPU 采样/内存/Python/PyTorch/PCCL）、统计系统与 30 个统计规则、asys CLI 全命令、GUI 分析、FAQ 与已知问题 |
| [02_asight_compute.md](02_asight_compute.md) | Asight Compute（对标 Nsight Compute）：kernel 级硬件计数器分析。acu 采集（metric set/section/metric 三级、四种 Replay 模式、Kernel 过滤）、GUI 各 Section（SOL/Roofline、Warp Stall、Occupancy）、Rule 系统自定义、FAQ 与已知问题 |

## 比赛要点

- **算子级热点定位**：`asys stats -r ppu_op_sum/ppu_op_kernel_breakdown` 输出 GEMM/Attention 算子耗时占比（先 `export PPU_LIB_PERF_INSTRUMENT=1`），是选定优化目标的第一步。
- **TTFT/吞吐瓶颈定量**：`ppu_gaps`（空闲气泡）、`ppu_time_util` 专家规则 + DRAM/PCIe/ICN 带宽指标，区分 prefill 计算瓶颈、decode 带宽瓶颈与 Host 调度开销。
- **优化前后对比取证**：`asys compare` 逐算子输出 Perf Ratio，直接用于比赛报告。
- **kernel 级调优**：SOL/Roofline 判定计算/访存/延迟受限；15 种 Warp Stall Reason 定位调度瓶颈；`--launch-skip/--launch-count/--kernel-name` 精准采集 decode 重复 kernel。
- **可复现性**：`ppu-smi -lpc` 锁频后再 profiling（见 [../ppu_sdk/15_ppu_smi_mps.md](../ppu_sdk/15_ppu_smi_mps.md)）。

## 配套

- SDK 参考：[../ppu_sdk/00_index.md](../ppu_sdk/00_index.md)
- HGGC 编程指南笔记：[../ppu_hggc/00_index.md](../ppu_hggc/00_index.md)
