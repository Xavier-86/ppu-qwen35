# PPU Qwen3.5 推理优化

> 面向比赛：在单张阿里平头哥 810E PPU 上实现并优化基于 Qwen3.5-2B 的 VLM 推理；评测为单样本且不启用 batch。
> 核心内容位于 [submit/](submit/)：比赛提交版本，包含评测入口、选手 wrapper、推理引擎源码闭包（含修改版 SGLang，不依赖外部环境中的同名包）与技术报告；[docs/](docs/) 收录平台手册笔记与第三方参考实现。

克隆仓库：

```bash
git clone https://github.com/Xavier-86/ppu-qwen35.git
cd ppu-qwen35
git lfs pull
```

## 目录

- [项目总览](#项目总览)
- [最终自测性能](#最终自测性能)
- [按需求查阅文档](#按需求查阅文档)
- [全部文件清单](#全部文件清单)

## 项目总览

| 路径 | 内容 | 适用场景 |
| --- | --- | --- |
| [submit/](submit/) | **比赛提交版本**：`evaluation_wrapper.py` 模型封装、`benchmark_public.py` 公开评测入口、`datasets/mmbench/` 自测数据目录（数据不随仓库分发）、`rapid_reasoning/` 推理引擎源码与运行时闭包、`docs/TECHNICAL_REPORT.md` 技术报告 | 运行 benchmark、复现提交成绩、查阅优化实现 |
| [docs/aliyun/](docs/aliyun/00_index.md) | 阿里云比赛运维：CLI/RAM 凭证、ACK/PPU 集群、ACR 镜像和 NAS/CPFS 操作 | 配置云端访问、连接比赛集群、发布镜像、排查存储 |
| [docs/ppu_platform/](docs/ppu_platform/00_index.md) | 入门指南（软件栈架构/部署选型）、Holmes 推理引擎、内核驱动（XID/ECC） | 环境搭建、模型部署、驱动故障排查 |
| [docs/ppu_hggc/](docs/ppu_hggc/00_index.md) | HGGC 编程指南笔记（5 章：编程模型/核心编程/进阶/专项功能/技术参考） | kernel 开发、算子融合、显存管理、HGGC 图优化 |
| [docs/ppu_sdk/](docs/ppu_sdk/00_index.md) | SAIL SDK 参考手册（15 份：TIX 指令集/Runtime/Driver API/Math/加速库/hgcc/调试工具/PPU-SMI/MPS） | 查阅 API、指令集、编译选项、量化与算子优化 |
| [docs/ppu_asight/](docs/ppu_asight/00_index.md) | Asight Systems（timeline/算子热点/对比取证）+ Asight Compute（kernel 级 Roofline/Stall/Occupancy） | 性能分析、瓶颈定位、优化前后对比取证 |
| [docs/ppu_pccl/](docs/ppu_pccl/00_index.md) | PCCL 集合通信 + DeepEP + sailbandwidth | 多卡/多实例 serving、通信优化（单卡场景可跳过） |
| [docs/ppu_video/](docs/ppu_video/00_index.md) | hgJPEG 硬件解码 + HGPP 图像处理库 | VLM 图像预处理 offload |
| [docs/flagos_ppu/](docs/flagos_ppu/00_index.md) | FlagOS 算子挑战赛获奖实现的 PPU 部分：6 道推理算子的 Triton kernel、PPU 加速比与技术报告 | Triton PPU kernel 开发时参考真实硬件（PPU-ZW810E）的调优方法 |

## 最终自测性能

提交默认配置（不传任何调优环境变量）在单张 810E 上按 `benchmark_public.py` 全量运行公开 MMBench 数据的最终结果：

| 数据集 | 样本数 | 平均 TTFT | 平均 decode 吞吐 | 准确率 | public validation |
| --- | ---: | ---: | ---: | ---: | ---: |
| MMBench dev EN | 4029 | **27.628 ms** | **594.200 tok/s** | 79.9702%（3222/4029） | 通过 |
| MMBench dev CN | 4029 | **27.990 ms** | **401.827 tok/s** | 84.0159%（3385/4029） | 通过 |

对照主办方 Transformers 基准（EN 185.1 ms / 58.7 tok/s，CN 141.0 ms / 41.5 tok/s）：TTFT 降低 85.1%/80.1%，decode 吞吐 10.12×/9.68×，正确题数 +3/−3，准确率无实质退化。优化方案与复现方式见[技术报告](submit/docs/TECHNICAL_REPORT.md)，自测命令见 [submit/README.md](submit/README.md)。

## 按需求查阅文档

| 需求 | 参考文档 |
| --- | --- |
| 配置 RAM 用户与阿里云 CLI | [docs/aliyun/01_cli_ram.md](docs/aliyun/01_cli_ram.md) |
| 连接 ACK、查询 PPU 节点、排查 Pod | [docs/aliyun/02_ack_ppu.md](docs/aliyun/02_ack_ppu.md) |
| 推送比赛镜像、检查 NAS/CPFS | [docs/aliyun/03_image_storage.md](docs/aliyun/03_image_storage.md) |
| 搭建与验证 PPU 环境 | [docs/ppu_platform/01_guide.md](docs/ppu_platform/01_guide.md)、[docs/ppu_sdk/01_overview_install.md](docs/ppu_sdk/01_overview_install.md) |
| 部署 Qwen3.5-2B 推理 | [docs/ppu_platform/02_holmes.md](docs/ppu_platform/02_holmes.md) |
| 驱动安装失败、掉卡、hang 排查 | [docs/ppu_platform/03_driver.md](docs/ppu_platform/03_driver.md)（XID 修复策略表） |
| 量化（FP8/INT8/MXFP4） | [docs/ppu_sdk/08_acblas.md](docs/ppu_sdk/08_acblas.md)、[docs/ppu_sdk/06_math_api.md](docs/ppu_sdk/06_math_api.md)、[docs/ppu_sdk/02_tix_programming.md](docs/ppu_sdk/02_tix_programming.md)、[docs/ppu_hggc/05_technical_reference.md](docs/ppu_hggc/05_technical_reference.md)（awmma） |
| 剪枝与稀疏计算 | [docs/ppu_sdk/09_acsparse.md](docs/ppu_sdk/09_acsparse.md) |
| 降低 TTFT | [docs/ppu_hggc/04_ppu_features.md](docs/ppu_hggc/04_ppu_features.md)（HGGC 图/延迟加载/VMM）、[docs/ppu_sdk/04_runtime_api.md](docs/ppu_sdk/04_runtime_api.md)、[docs/ppu_video/01_hgjpeg.md](docs/ppu_video/01_hgjpeg.md)（图像预处理 offload） |
| 提升 decode 吞吐 | [docs/ppu_sdk/15_ppu_smi_mps.md](docs/ppu_sdk/15_ppu_smi_mps.md)（单卡状态/锁频）、[docs/ppu_sdk/08_acblas.md](docs/ppu_sdk/08_acblas.md)（acblasLt 融合）、[docs/ppu_sdk/03_hggc_samples.md](docs/ppu_sdk/03_hggc_samples.md)（Tensor Cell GEMM 范式） |
| 编写与融合自定义 kernel | [docs/ppu_hggc/02_core_programming.md](docs/ppu_hggc/02_core_programming.md)（SIMT 编程）、[docs/ppu_sdk/02_tix_programming.md](docs/ppu_sdk/02_tix_programming.md)（指令集）、[docs/ppu_sdk/05_driver_api.md](docs/ppu_sdk/05_driver_api.md)（参数对齐陷阱） |
| 显存与 KV cache 管理 | [docs/ppu_hggc/04_ppu_features.md](docs/ppu_hggc/04_ppu_features.md)（VMM/流有序分配器）、[docs/ppu_sdk/05_driver_api.md](docs/ppu_sdk/05_driver_api.md)（内存池/VMM API） |
| 性能分析与瓶颈定位 | [docs/ppu_asight/01_asight_systems.md](docs/ppu_asight/01_asight_systems.md)（ppu_op_sum 算子占比）、[docs/ppu_asight/02_asight_compute.md](docs/ppu_asight/02_asight_compute.md)（Roofline/Stall） |
| 优化前后对比取证 | [docs/ppu_asight/01_asight_systems.md](docs/ppu_asight/01_asight_systems.md)（asys compare）、[docs/ppu_sdk/15_ppu_smi_mps.md](docs/ppu_sdk/15_ppu_smi_mps.md)（锁频压测）、[docs/ppu_pccl/02_deepep_bandwidth.md](docs/ppu_pccl/02_deepep_bandwidth.md)（sailbandwidth） |
| 调试自定义算子 | [docs/ppu_sdk/14_memcheck.md](docs/ppu_sdk/14_memcheck.md)（越界/竞态）、[docs/ppu_sdk/13_ppu_gdb.md](docs/ppu_sdk/13_ppu_gdb.md)（异常代码表/autostep）、[docs/ppu_sdk/12_binary_utilities.md](docs/ppu_sdk/12_binary_utilities.md)（反汇编/寄存器分析） |
| 编译选项调优 | [docs/ppu_sdk/10_hgcc.md](docs/ppu_sdk/10_hgcc.md)（104 项选项全表）、[docs/ppu_sdk/11_hgrtc_jitlink.md](docs/ppu_sdk/11_hgrtc_jitlink.md)（运行时注入算子） |
| 数学函数精度取舍 | [docs/ppu_sdk/06_math_api.md](docs/ppu_sdk/06_math_api.md)（快速/精确对照）、[docs/ppu_hggc/05_technical_reference.md](docs/ppu_hggc/05_technical_reference.md)（ULP 表） |
| 多卡与通信（平台资料，非本比赛路径） | [docs/ppu_pccl/01_pccl.md](docs/ppu_pccl/01_pccl.md) |
| 图像预处理加速 | [docs/ppu_video/01_hgjpeg.md](docs/ppu_video/01_hgjpeg.md)（批量硬解落显存）、[docs/ppu_video/02_hgpp.md](docs/ppu_video/02_hgpp.md)（Resize/归一化） |

## 全部文件清单

### docs/aliyun/ —— RAM · ACK/PPU 集群 · ACR 镜像 · NAS/CPFS

| 文件 | 内容 |
| --- | --- |
| [docs/aliyun/00_index.md](docs/aliyun/00_index.md) | 阿里云比赛运维索引、推荐流程、安全边界与命令速查 |
| [docs/aliyun/01_cli_ram.md](docs/aliyun/01_cli_ram.md) | CLI 3.3+、OAuth/AccessKey/RAM 角色、Profile、插件、身份和权限排查 |
| [docs/aliyun/02_ack_ppu.md](docs/aliyun/02_ack_ppu.md) | ACK 集群发现、短期 KubeConfig、RBAC、PPU 节点、Pod、日志、端口转发与受控更新 |
| [docs/aliyun/03_image_storage.md](docs/aliyun/03_image_storage.md) | ACR 镜像构建/推送与拉取排查、NAS/CPFS 查询、比赛数据分层 |

### docs/ppu_platform/ —— 平台：入门指南 · Holmes 推理引擎 · 内核驱动

| 文件 | 内容 |
| --- | --- |
| [docs/ppu_platform/00_index.md](docs/ppu_platform/00_index.md) | 本库索引与比赛要点 |
| [docs/ppu_platform/01_guide.md](docs/ppu_platform/01_guide.md) | T-Head SAIL 入门指南：软件栈三层架构、术语表、快速开始、部署方式选型（裸金属/容器/虚拟机、MIG/vGPU、ICN 约束） |
| [docs/ppu_platform/02_holmes.md](docs/ppu_platform/02_holmes.md) | Holmes 推理引擎：安装、torch/onnx/tf 导入、编译参数、Runtime C++ API、Graph/Stream 执行、压测工具 |
| [docs/ppu_platform/03_driver.md](docs/ppu_platform/03_driver.md) | 内核驱动：KMD 安装与故障排查、PPU001/PPU0015 全部 XID 错误码矩阵与修复策略、ECC 处理流程 |

### docs/ppu_hggc/ —— HGGC 编程指南笔记

| 文件 | 内容 |
| --- | --- |
| [docs/ppu_hggc/00_index.md](docs/ppu_hggc/00_index.md) | 本库索引 + 按评分维度的优化路线 |
| [docs/ppu_hggc/01_intro.md](docs/ppu_hggc/01_intro.md) | 编程模型、硬件模型（CU/block/warp/SIMT）、七条算子性能指引 |
| [docs/ppu_hggc/02_core_programming.md](docs/ppu_hggc/02_core_programming.md) | C++/hgcc 编程、SIMT kernel、异步编程（流/事件/优先级）、统一内存、编译选项 |
| [docs/ppu_hggc/03_advanced_programming.md](docs/ppu_hggc/03_advanced_programming.md) | 驱动 API、参数对齐陷阱、多设备 P2P、IOMMU 注意事项 |
| [docs/ppu_hggc/04_ppu_features.md](docs/ppu_hggc/04_ppu_features.md) | HGGC 图、流有序内存分配器、协作组、延迟加载、异步流水线、IPC 与 VMM（KV cache） |
| [docs/ppu_hggc/05_technical_reference.md](docs/ppu_hggc/05_technical_reference.md) | 语言扩展（awmma 张量核/低精度类型/warp 函数）、环境变量、数学函数 ULP 表、硬件规格全表 |

### docs/ppu_sdk/ —— SAIL SDK 参考手册

| 文件 | 内容 |
| --- | --- |
| [docs/ppu_sdk/00_index.md](docs/ppu_sdk/00_index.md) | 本库索引 + 按评分维度的使用路线 |
| [docs/ppu_sdk/01_overview_install.md](docs/ppu_sdk/01_overview_install.md) | SDK 概览、Release Notes v2.1.1（含已知问题）、安装指南 |
| [docs/ppu_sdk/02_tix_programming.md](docs/ppu_sdk/02_tix_programming.md) | TIX 指令集编程指南：全部指令、Tensor Cell MMA（FP8/MXFP4）、AIU 异步拷贝、内联汇编 |
| [docs/ppu_sdk/03_hggc_samples.md](docs/ppu_sdk/03_hggc_samples.md) | 59 个官方示例：Tensor Cell GEMM、Graph、内存策略、性能微基准 |
| [docs/ppu_sdk/04_runtime_api.md](docs/ppu_sdk/04_runtime_api.md) | Runtime API 完整参考（236 函数：同步语义、内存池、图 78 函数） |
| [docs/ppu_sdk/05_driver_api.md](docs/ppu_sdk/05_driver_api.md) | Driver API 完整参考（VMM、模块预加载、Graph 72 函数、参数对齐规则） |
| [docs/ppu_sdk/06_math_api.md](docs/ppu_sdk/06_math_api.md) | 数学函数库（812 函数：FP8/half/bf16 内建、快速/精确对照、SIMD 内建） |
| [docs/ppu_sdk/07_acdnn.md](docs/ppu_sdk/07_acdnn.md) | acDNN 深度学习库：卷积、MultiHeadAttn 增量解码、RNN、Graph API、融合算子 |
| [docs/ppu_sdk/08_acblas.md](docs/ppu_sdk/08_acblas.md) | acBLAS：GEMM 全精度组合表（FP8/IMMA）、acblasLt epilogue 融合、性能硬约束 |
| [docs/ppu_sdk/09_acsparse.md](docs/ppu_sdk/09_acsparse.md) | acSPARSE 稀疏库：CSR/BSR/Blocked-ELL、SpMV/SpMM/SpGEMM（剪枝相关） |
| [docs/ppu_sdk/10_hgcc.md](docs/ppu_sdk/10_hgcc.md) | hgcc 编译器手册：104 项编译选项全表、多架构编译、RDC+LTO |
| [docs/ppu_sdk/11_hgrtc_jitlink.md](docs/ppu_sdk/11_hgrtc_jitlink.md) | HGRTC 运行时编译 + hgJitLink JIT 链接（运行时注入自定义算子） |
| [docs/ppu_sdk/12_binary_utilities.md](docs/ppu_sdk/12_binary_utilities.md) | 二进制工具：hgobjdump 反汇编/资源信息、hgbat CFG/寄存器活跃区间、hgprune、hgFatbinary |
| [docs/ppu_sdk/13_ppu_gdb.md](docs/ppu_sdk/13_ppu_gdb.md) | PPU-GDB 调试器：kernel 断点/单步、寄存器查看、autostep、核心转储、36 条异常代码表 |
| [docs/ppu_sdk/14_memcheck.md](docs/ppu_sdk/14_memcheck.md) | HGGC Memcheck：memcheck/racecheck/initcheck/synccheck 四工具与全部示例 |
| [docs/ppu_sdk/15_ppu_smi_mps.md](docs/ppu_sdk/15_ppu_smi_mps.md) | PPU-SMI 设备管理监控（时钟锁定、stats/dmon、MIG、拓扑）+ MPS 多进程服务 |

### docs/ppu_asight/ —— 性能分析工具

| 文件 | 内容 |
| --- | --- |
| [docs/ppu_asight/00_index.md](docs/ppu_asight/00_index.md) | 本库索引与比赛要点 |
| [docs/ppu_asight/01_asight_systems.md](docs/ppu_asight/01_asight_systems.md) | Asight Systems：timeline 跟踪（PPU 活动/metrics/HGTX/CPU 采样/内存/PyTorch/PCCL）、30 个统计规则、asys CLI、compare 对比取证、GUI |
| [docs/ppu_asight/02_asight_compute.md](docs/ppu_asight/02_asight_compute.md) | Asight Compute：kernel 级计数器（SOL/Roofline、15 种 Warp Stall、Occupancy）、四种 Replay 模式、Rule 系统 |

### docs/ppu_pccl/ —— 高性能互联

| 文件 | 内容 |
| --- | --- |
| [docs/ppu_pccl/00_index.md](docs/ppu_pccl/00_index.md) | 本库索引与比赛要点 |
| [docs/ppu_pccl/01_pccl.md](docs/ppu_pccl/01_pccl.md) | PCCL 集合通信库：概念、完整 API、76 个环境变量、Zero-CTA/窗口注册、Debug 指南、PCCL-TESTS |
| [docs/ppu_pccl/02_deepep_bandwidth.md](docs/ppu_pccl/02_deepep_bandwidth.md) | DeepEP-for-sail（MoE 专家并行、量化通信）+ sailbandwidth 带宽测试工具 |

### docs/ppu_video/ —— 视频图像硬件加速

| 文件 | 内容 |
| --- | --- |
| [docs/ppu_video/00_index.md](docs/ppu_video/00_index.md) | 本库索引与比赛要点 |
| [docs/ppu_video/01_hgjpeg.md](docs/ppu_video/01_hgjpeg.md) | 视频图像概述 + hgJPEG：硬件 JPEG 批量解码（直接落显存）、编码、转码全部 API |
| [docs/ppu_video/02_hgpp.md](docs/ppu_video/02_hgpp.md) | HGPP 图像处理库：Resize/Warp 及 Batch 版、颜色转换、归一化算子链、MSE/PSNR/SSIM 精度取证 |

### docs/flagos_ppu/ —— FlagOS 算子挑战赛 PPU 获奖实现

| 文件 | 内容 |
| --- | --- |
| [docs/flagos_ppu/00_index.md](docs/flagos_ppu/00_index.md) | 本库索引：来源、PPU-ZW810E 硬件参数、6 道题的 PPU 加速比与优化要点速查、可借鉴点小结 |
| [docs/flagos_ppu/src/](docs/flagos_ppu/src/) | 6 道题的 Triton kernel：RMSNorm+Group Quant、DSA TopK 页表变换、MLA Backward、W4A8 MoE GEMM、KV Cache 压缩、SwiGLU 量化融合 |
| [docs/flagos_ppu/reports/](docs/flagos_ppu/reports/) | 7 份技术报告（含 1 份获奖分享整理稿，PPU 相关内容见索引） |
