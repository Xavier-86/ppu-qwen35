# PPU 平台：入门指南 · Holmes 推理引擎 · 内核驱动 <span style="float: right;"><a href="../../README.md">目录</a></span>

## 目录

- [文件](#文件)
- [比赛要点](#比赛要点)
- [配套](#配套)


> 面向比赛：基于 Qwen3.5-2B 的 VLM 在阿里平头哥 PPU 服务器上的高效推理优化。

## 文件

| 文件 | 内容 |
| --- | --- |
| [01_guide.md](01_guide.md) | T-Head SAIL 入门指南：软件栈三层架构、术语表、快速开始（KMD/SDK 安装与验证）、SDK 各模块能力、部署方式选型（裸金属/容器/虚拟机、MIG/vGPU/Passthrough、ICN 隔离约束）、Driver/Runtime API 文档结构索引 |
| [02_holmes.md](02_holmes.md) | Holmes 推理引擎：概述与架构、获取安装、ResNet50 端到端快速入门、Holmes-Frontend（torch/onnx/tf 导入）、Holmes-Compile（编译参数与辅助工具）、Holmes-Runtime（C++ API、并发与 Graph/Stream 执行模式、压测工具） |
| [03_driver.md](03_driver.md) | 内核驱动：KMD 安装/升级与 4 类故障排查、PPU XID 定义（PPU001 66 行矩阵 + 23 个详解；PPU0015 92 行矩阵 + 28 个详解）、修复策略表、ECC 处理流程 |

## 比赛要点

- **硬件底数**：810E 单卡显存 98304 MiB，单机最多 16 卡——决定权重 + KV cache 显存预算与 batch 上限（01）。
- **部署链路**：`torch.export → holmes-import-torch → holmes-compile → Runtime C++ API` 官方推荐路径；`--holmes-flow-demote-f32-to-f16` 全图降级降显存提吞吐；Graph 模式降 launch 开销；`holmes-benchmark-module` 官方压测（02）。
- **复赛部署**：裸金属/容器/虚拟机选型表与 ICN 互斥约束（01）；KMD 安装故障自救（`lsof /dev/alixpu`、vfio-pci 清除、驱动回退修复）（03）。
- **压测排障**：进程 hang/掉卡按 XID 修复策略表处理；XID 16258 是多实例并发压测常见问题；UECC 屏蔽显存页会缩水可用显存，压测前后用 `ppu-smi -q -d ECC` 检查（03）。

## 配套

- SDK 参考手册：[../ppu_sdk/00_index.md](../ppu_sdk/00_index.md)
- HGGC 编程指南笔记：[../ppu_hggc/00_index.md](../ppu_hggc/00_index.md)
- Asight 性能分析：[../ppu_asight/00_index.md](../ppu_asight/00_index.md)
- 视频图像硬件加速：[../ppu_video/00_index.md](../ppu_video/00_index.md)
