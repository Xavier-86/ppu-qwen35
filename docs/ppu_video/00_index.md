# 视频图像硬件加速 · 比赛参考 <span style="float: right;"><a href="../../README.md">目录</a></span>

## 目录

- [文件](#文件)
- [比赛要点](#比赛要点)
- [配套](#配套)


> 面向比赛：基于 Qwen3.5-2B 的 VLM 在阿里平头哥 PPU 服务器上的高效推理优化。

## 文件

| 文件 | 内容 |
| --- | --- |
| [01_hgjpeg.md](01_hgjpeg.md) | 视频图像硬件加速概述（HGDEC/HGENC/hgJPEG/HGPP 四模块规格与性能）+ hgJPEG 编程指南（硬件 JPEG 解码/编码/转码全部 API） |
| [02_hgpp.md](02_hgpp.md) | HGPP 图像处理库（对标 NPP）：数据类型与约定、内存管理、算术逻辑运算、颜色转换、数据交换、滤波、**几何变换（Resize/Warp 及 Batch 版）**、形态学、统计（MSE/PSNR/SSIM）、阈值比较 |

## 比赛要点

- **VLM 图像预处理 offload**（降 TTFT 的直接手段）：
  - `hgjpegDecodeBatched()` 批量解码直接落 device 显存，自动 8 线程打满 8 个 JPEG 硬件核（1080P 最高 5430 FPS）；`hgjpegDecodeParamsSetScaleFactor()` 解码阶段硬件缩图，省独立 resize。
  - HGPP `hgppiResizeSqrPixel_*`/`ResizeBatch` 缩放到视觉编码器分辨率；SwapChannels/Convert/SubC/MulC/ColorTwist 覆盖归一化链路。
- **零拷贝异步流水**：HGPP 函数经 `HgppStreamContext` 提交、设备指针、线程安全，预处理可与 LLM 推理重叠；`VIDEO_MEMORY_OPTIMIZE=1` 峰值显存降约 37%（性能代价约 13%），为 KV cache 腾显存。
- **精度取证**：HGPP §12 设备端 MSE/PSNR/SSIM（含 Batch 版）可做 offload 结果与 CPU 参考的精度对比。

未收录：HGDEC/HGENC 视频编解码编程指南（VLM 图像输入场景用不到）。

## 配套

- SDK 参考：[../ppu_sdk/00_index.md](../ppu_sdk/00_index.md)
- Holmes 推理引擎：[../ppu_platform/02_holmes.md](../ppu_platform/02_holmes.md)
