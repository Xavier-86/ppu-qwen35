# PCCL 高性能互联 · 平台扩展参考 <span style="float: right;"><a href="../../README.md">目录</a></span>

## 目录

- [文件](#文件)
- [比赛要点](#比赛要点)
- [配套](#配套)


> 面向比赛：基于 Qwen3.5-2B 的 VLM 在阿里平头哥 PPU 服务器上的高效推理优化。

## 文件

| 文件 | 内容 |
| --- | --- |
| [01_pccl.md](01_pccl.md) | PCCL 集合通信库（对标 NCCL）：简介与适用范围、环境配置与 PCCL-TESTS、概念（通信域/8 种集合通信/组调用/P2P/Graph 捕获/Zero-CTA）、编程实践、高性能实践、完整 API、全部环境变量（网络 27 + 性能 23 + 内存 7 + 初始化 13 + 插件 6 + 调试 12）、Debug 指南、已知问题 |
| [02_deepep_bandwidth.md](02_deepep_bandwidth.md) | DeepEP-for-sail（MoE 专家并行通信：low_latency_dispatch/combine、INT8/FP8/MXFP4 量化通信、示例与 Benchmark）+ sailbandwidth（CE/SM Copy 带宽测试工具全参数） |

## 比赛要点

- **Zero-CTA + 窗口注册**：`PCCL_CTA_POLICY=ZERO` + `pcclMemAlloc`/`pcclCommWindowRegister` 把 AllReduce 卸载到 Copy Engine，不占 SM，通信/计算重叠压 TTFT。
- **显存旋钮**：`splitShare`、`PCCL_MAX_NCHANNELS`、`minCTAs/maxCTAs/PCCL_BUFFSIZE` 可在显存紧张时回收通信 buffer。
- **注意**：Qwen3.5-2B 是稠密模型且单卡可放，PCCL/DeepEP 主要用于多卡/多实例 serving 场景与"系统级优化深度"论述；MPS 与 ICN 多卡互斥（见 [../ppu_sdk/15_ppu_smi_mps.md](../ppu_sdk/15_ppu_smi_mps.md)）。
- **取证**：PCCL-TESTS 三种计时方式、`PCCL_DEBUG=INFO` 抓实际传输路径、sailbandwidth `-j` JSON 输出带宽达标证据。

## 配套

- SDK 参考：[../ppu_sdk/00_index.md](../ppu_sdk/00_index.md)
- 性能分析：[../ppu_asight/00_index.md](../ppu_asight/00_index.md)
