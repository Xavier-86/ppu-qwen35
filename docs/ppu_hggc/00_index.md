# T-Head SAIL HGGC 编程指南 · 比赛全套笔记索引 <span style="float: right;"><a href="../../README.md">目录</a></span>

## 目录

- [笔记结构](#笔记结构)
- [比赛优化路线速查（按评分维度）](#比赛优化路线速查按评分维度)
  - [1. 精度保持（40%）](#1-精度保持40)
  - [2. TTFT 优化（30%）](#2-ttft-优化30)
  - [3. 吞吐量提升（30%）](#3-吞吐量提升30)
  - [4. 系统级优化深度（20%）](#4-系统级优化深度20)
- [工具链](#工具链)
- [使用注意](#使用注意)


> 面向比赛：基于 Qwen3.5-2B 的 VLM 在阿里平头哥 PPU 服务器上的高效推理优化。

## 笔记结构

| 文件 | 对应原文章节 | 内容 | 规模 |
| --- | --- | --- | --- |
| [01_intro.md](01_intro.md) | 第 1 章 PPU 与 HGGC 入门 | 编程模型、硬件模型（CU/block/grid/warp/SIMT）、计算能力、TIX、**§1.5 特性概览（七条算子性能指引 + 延迟优化手段）** | ~23 KB |
| [02_core_programming.md](02_core_programming.md) | 第 2 章 核心编程 | C++/hgcc 编程、kernel 编写与启动、SIMT 编程、异步编程（流/事件/回调/优先级）、统一内存、**hgcc 全部编译选项表** | ~106 KB |
| [03_advanced_programming.md](03_advanced_programming.md) | 第 3 章 进阶编程 | 驱动 API（context/module/hgLaunchKernel）、参数对齐陷阱、多设备与 P2P、IOMMU 注意事项 | ~33 KB |
| [04_ppu_features.md](04_ppu_features.md) | 第 4 章 PPU 专项功能 | **HGGC 图（降 TTFT 核心）**、流有序内存分配器、协作组、延迟加载、异步屏障与流水线、IPC 与 **VMM（KV-cache 管理）** | ~135 KB |
| [05_technical_reference.md](05_technical_reference.md) | 第 5 章 技术参考 | C++ 语言支持、语言扩展（**awmma 张量核/低精度类型/warp 函数/DPX**）、环境变量、数学函数 ULP 精度表、**ppu001/ppu0015 硬件规格全表** | ~172 KB |

术语对照：HGGC ≈ CUDA；hgcc ≈ nvcc；CU ≈ SM；TIX ≈ PTX；hgbin/hgfatbin ≈ cubin/fatbin。

## 比赛优化路线速查（按评分维度）

### 1. 精度保持（40%）

- **量化路线**：ppu0015 张量核原生支持 FP8（E4M3/E5M2，2× FP16 算力）与 MXFP4/FP4（E2M1，每 32 元素共享 E8M0 scale，4× FP16 算力），FP4 明确面向推理 → 权重量化 group size 对齐 32。见 01 §1.5.1.7、05 §5.2.7 + §5.5 Tensor Cell 表。
- **注意**：FP8/FP4 在 C++ awmma 层未完全暴露，部分需 Inline TIX；INT8→int 的 W8A8 路径在 awmma 可用。
- **数学函数精度**：softmax exp、SiLU/GELU、量化取整逐函数查 ULP 表做精度-速度权衡，不要盲目全局 `--use_fast_math`。见 05 §5.4。

### 2. TTFT 优化（30%）

- **HGGC 图**：decode 循环 kernel 链固定 → stream capture 建图、实例化后反复 `hggcGraphLaunch`；单节点参数刷新（`hggcGraphExecKernelNodeSetParams`）匹配"每步只换输入指针"的推理模式；条件节点（IF/WHILE）可做设备侧分支。见 04 §4.1。
- **延迟加载陷阱**：`HGGC_MODULE_LOADING` 默认 lazy，首次调用 kernel 才加载模块，会污染 TTFT 测量 → 设 eager 或预热（`hgModuleGetFunction`/`hggcFuncGetAttributes`）。见 04 §4.4、05 §5.3。
- **驱动 API 预加载**：自研 kernel 离线编成 hgbin，驱动 API 直接拿句柄启动，压冷启动。见 03 §3.1.2/3.1.3。
- **隐式同步 6 类操作**会悄悄串行化流水线，逐条排查。见 02 §2.3。

### 3. 吞吐量提升（30%）

- **占用率调优闭环**：`--maxrregcount`/`__launch_bounds__`/`__maxnreg__` + `-res-usage` + Asight 实测；硬件上限：64K VREG/CU、255 VREG/warp、2048 线程/CU、256KB smem/32 bank。见 02 §2.2.6、05 §5.2.4 + §5.5。
- **awmma GEMM tiling**：BF16/FP16→FP32 累加三种 warp 形状（16x16x16 / 32x8x16 / 8x32x16），decode 小 M 场景选 8x32x16。见 05 §5.2.7。
- **异步拷贝流水线**：`ppu.cp.async`（LDGSTS）、`hggc::pipeline` 双缓冲、AIU warp-level 批量拷贝 + swizzle → GEMM 数据搬运与计算重叠。见 04 §4.5。
- **微架构数值**：ppu001 共享内存 2 组×128B/拍（256B 间隔同组冲突）、原子操作 128B 对齐；ppu0015 升 4 组×1024B、load/aiu 预取提示、三级缓存独立 bypass。见 01 §1.5.1、05 §5.5。

### 4. 系统级优化深度（20%）

- **VMM（虚拟内存管理）**：原文点名"为 LLM KV-cache 动态管理提供底层原语"——`hgMemAddressReserve`/`hgMemMap` 按需提交物理页，可实现 PagedAttention 式分页 KV-cache。见 04 §4.6.3。
- **流有序内存分配器**：`hggcMallocAsync`/`hggcFreeAsync` + 内存池复用策略 + `hggcGraphUpload`/`hggcDeviceGraphMemTrim`。见 04 §4.2。
- **统一内存陷阱**：平台仅支持**有限统一内存**（kernel 启动时整批迁入/迁出，不可超额订阅）→ 权重/KV cache 必须 `hggcMalloc` 显式驻留显存。见 02 §2.4.2.3。
- **算子融合注意**：驱动 API 传参对齐规则（double 恒 8B、float4=16B、结构体跨端 padding），错了只表现为静默精度下降。见 03 §3.1.3。
- **多卡**（如复赛涉及）：P2P `hggcDeviceEnablePeerAccess`、优先 VMM 按需开启；裸机必须禁用 IOMMU 否则 PCIe P2P 静默损坏显存。见 03 §3.2.2。

## 工具链

- **编译**：hgcc（`-arch=ppu_10|ppu_15`，支持多架构混合编译进 hgfatbin）。见 02 §2.5。
- **性能分析**：Asight（Occupancy 等指标采集）。
- **调试**：PPU-GDB；**监控**：ppu-smi。
- **官方库**：acBLAS（GEMM）、acFFT、acDNN、CUTLASS（模板化 GEMM）、PCCL（多卡通信）——优先调用而非重写。见 01 §1.1。

## 使用注意

- 笔记中标注"（需查原文确认）"处为原文歧义或存疑之处（如 `__hg_bfloat16` vs `__ppu_bfloat16` 命名、个别 ULP 上标指数），关键决策前需自行核实。
