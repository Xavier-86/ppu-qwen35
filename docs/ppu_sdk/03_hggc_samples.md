# T-Head SAIL HGGC 示例程序 <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [1. 概述](#1-概述)
  - [1.1. 获取 HGGC 示例程序](#11-获取-hggc-示例程序)
  - [1.2. 构建 HGGC 示例程序](#12-构建-hggc-示例程序)
  - [1.3. 使用测试脚本运行所有示例程序](#13-使用测试脚本运行所有示例程序)
- [2. 示例程序列表](#2-示例程序列表)
  - [2.1. 入门](#21-入门)
  - [2.2. 实用工具](#22-实用工具)
  - [2.3. 算法与技术](#23-算法与技术)
  - [2.4. HGGC 特性](#24-hggc-特性)
  - [2.5. HGGC 库](#25-hggc-库)
  - [2.6. 性能](#26-性能)
- [3. 依赖项](#3-依赖项)
  - [3.1. 第三方依赖](#31-第三方依赖)
  - [3.2. HGGC 特性](#32-hggc-特性)


## 1. 概述

HGGC-Samples 是面向 HGGC 开发者的示例程序集，展示了 T-Head SAIL 软件工具包的各项特性。当前版本支持 SAIL 2.1。

### 1.1. 获取 HGGC 示例程序

有关 T-Head SAIL 软件工具包的系统要求和安装说明，请参阅 T-Head SAIL SDK 安装指南。

使用 git 克隆 HGGC 示例程序仓库（命令见下方）。

`git clone git@github.com:t-head/hggc-samples.git`

如果不使用 git，最简便的方式是点击仓库页面上的“Download ZIP”按钮下载当前版本的压缩包，解压后即可使用这些示例程序。

### 1.2. 构建 HGGC 示例程序

HGGC 示例程序使用 CMake 构建。请按照以下 Linux 构建说明操作。

确保已安装 CMake（3.20 或更高版本）。如有必要，可通过包管理器安装：

例如： `sudo apt install cmake`

进入克隆的仓库根目录并创建构建目录：

```bash
mkdir build && cd build
```

使用 CMake 配置项目：

```bash
cmake ..
```

构建示例程序：

```bash
make -j$(nproc)
```

从构建目录中各自的子目录运行示例程序。也可以从示例程序仓库的任意子目录，或从单个示例程序目录中执行上述流程。

### 1.3. 使用测试脚本运行所有示例程序

需要注意的是，HGGC 示例程序**并非** HGGC 的验证套件。它们不覆盖边界情况，不完整覆盖运行时和驱动 API，也不用于性能基准测试。我们提供了 `run_tests.py` 脚本，可运行所有示例程序作为快速完整性检查。

该 Python3 脚本会在你指定的子目录中查找所有 `.out` 可执行文件（自动排除 CMake 构建系统生成的临时文件），并将应用程序名称与 `test_args.json` 中指定的命令行参数进行匹配。它接受以下命令行参数：

| 开关 | 用途 | 示例 |
| --- | --- | --- |
| --dir | 指定递归搜索可执行文件的根目录 | --dir ./build |
| --config | 可执行文件参数的 JSON 配置文件（可选） | --config test_args.json |
| --output | 测试结果的输出目录（stdout 保存为 .txt 文件，目录不存在时自动创建） | --output ./test |
| --parallel | 并行执行的应用程序数量 | --parallel 4 |

应用程序配置从 `test_args.json` 中加载，并与可执行文件名称进行匹配。

脚本成功时返回 0，测试失败时返回遇到的第一个非零错误码。如有失败的示例程序，也会打印一份汇总列表。

配置示例：

```json
{
    "multi_device_collab": {
        "min_ppus": 2
    }
}
```

#### 1.3.1. 示例用法

以下是构建并测试所有示例程序的一组示例命令。

首先，构建：

```bash
mkdir build && cd build
cmake ..
make -j$(nproc)
```

然后运行测试脚本：

```bash
# 基本用法
python3 run_tests.py --dir ./build --output ./test

# 使用配置文件
python3 run_tests.py --dir ./build --output ./test --config test_args.json

# 并行运行
python3 run_tests.py --dir ./build --output ./test --parallel 4
```

如果所有应用程序均运行成功，你将看到类似如下的输出：

```text
Test Summary:
Ran N test runs for N executables.
All test runs passed!
```

如果部分示例程序失败，你将看到类似如下的输出：

```text
Test Summary:
Ran N test runs for N executables.
Failed runs (2):
  acdnn_conv_activation: Failed (code 1)
  multi_device_collab: Failed (code 1)
```

你可以查看输出目录中的 stdout 日志（通常为 `APM_<application_name>.txt` 或 `APM_<application_name>.run<n>.txt`），从输出日志中判断可能出现的问题。如果你认为某个示例程序在你的系统上出现了不合理的失败，请在示例程序仓库中提交 issue。

## 2. 示例程序列表

除特别说明外，本章所有示例程序均满足以下共同条件：

- 支持的操作系统：Linux
- 支持的 CPU 架构：x86_64
- 前置条件：下载并安装适用于所用平台的 T-Head SAIL 软件工具包

各示例条目仅列出其特有的描述、关键概念、命令行参数、模式说明，以及涉及的运行时 API / 驱动 API / TIX 指令 / 库 API 和额外构建依赖。

### 2.1. 入门

本目录收录 HGGC 入门级示例，按主题归类后的全部子目录如下。部分目录在同一 sample 下提供 Runtime API、HGRTC、Driver API 等多种构建变体。

#### 2.1.1. assert - 设备端断言不变量校验

**描述**

本示例演示如何将设备端 `assert()` 用作核函数输出的不变量校验工具：

1. **前缀最大值核函数**产生单调非递减的输出；
2. **校验核函数**断言相邻元素满足 `array[i] <= array[i+1]`；
3. 主机端运行两种场景：正确输出（断言不触发）与故意破坏的输出（断言触发，主机检测到错误状态）。

相比简单的“线程 ID 越界”演示，本示例展示了 `assert()` 在真实开发中作为调试工具的实际用法。提供两个构建目标：

- **运行时 API 实现**（`assert.hg`）：kernel 与 host 代码静态编译。
- **HGRTC 运行时编译实现**（`assert_runtime_compile.cpp` + `assert_kernel.hg`）：使用 libHGRTC 即时编译 + 驱动 API 加载执行。

**关键概念**：断言（Assert）、运行时编译（Runtime Compilation）。

**HGGC 运行时 API**：hggcMalloc, hggcMemcpy, hggcFree, hggcDeviceSynchronize, hggcGetErrorString, hggcGetLastError, hggcDeviceReset

**HGGC 驱动 API**：hgMemAlloc, hgMemFree, hgMemcpyHtoD, hgModuleGetFunction, hgLaunchKernel, hgCtxSynchronize

**构建/运行所需依赖**：HGRTC（运行时编译实现需要）

#### 2.1.2. async_event_timing - 异步 API

**描述**

本示例演示了如何使用 HGGC 事件（Events）进行 PPU 计时，以及如何实现 CPU 和 PPU 的并行执行。事件被插入到 HGGC 调用流（Stream）中。由于 HGGC 流调用是异步的，CPU 可以在 PPU 执行任务（包括主机与设备之间的 DMA 内存拷贝）的同时进行计算。CPU 可以查询 HGGC 事件来判断 PPU 是否已完成任务。

**关键概念**：异步数据传输（Asynchronous Data Transfers）、HGGC 流和事件（Streams and Events）。

**HGGC 运行时 API**：hggcProfilerStop, hggcMalloc, hggcMemcpyAsync, hggcFree, hggcMallocHost, hggcProfilerStart, hggcDeviceSynchronize, hggcEventRecord, hggcFreeHost, hggcMemset, hggcEventDestroy, hggcEventQuery, hggcEventElapsedTime, hggcGetDeviceProperties, hggcEventCreate

#### 2.1.3. atomic_intrinsics - 简单原子操作

**描述**

本示例以“全局内存原子指令”为共同算法载体，从不同代码路径展示同一组原子内置函数的使用方式：

- **运行时 API 实现**（`static.hg` + `atomic_kernel.hgh`）：基于 HGGC 运行时 API，演示全局内存原子指令的最简使用。
- **HGRTC 运行时编译实现**（`runtime_compile.cpp` + `atomic_kernel_rtc.hg`）：使用 HGRTC 在程序启动时即时编译 kernel 源，通过驱动 API 加载执行，演示同一组原子内置函数在运行时编译路径上的等价行为。

**关键概念**：原子操作内置函数（Atomic Intrinsics）、运行时编译（Runtime Compilation）。

**HGGC 运行时 API**：hggcStreamCreateWithFlags, hggcFree, hggcMallocHost, hggcFreeHost, hggcStreamSynchronize, hggcMalloc, hggcMemcpyAsync, hggcStreamDestroy

**HGGC 驱动 API**：hgMemcpyDtoH, hgLaunchKernel, hgMemcpyHtoD, hgCtxSynchronize, hgMemAlloc, hgMemFree, hgModuleGetFunction

**构建/运行所需依赖**：HGRTC（运行时编译实现需要）

#### 2.1.4. block_sort_merge - Block 排序 + 双调归并

**描述**

本示例演示在 PPU 上的两阶段并行排序：

1. **块内排序（Block sort）**：每个线程块使用奇偶换位排序网络（Odd-Even Transposition Network）在共享内存中对一段元素进行排序。
2. **双调归并（Bitonic merge）**：相邻的有序块通过共享内存中的双调归并网络进行合并。

该排序处理键值对（Key-Value Pairs），并以 `std::stable_sort` 作为 CPU 参考，验证排序的稳定性（相等的键保持原始值顺序）。

**关键概念**：并行排序（Parallel Sorting）、奇偶换位排序（Odd-Even Transposition Sort）、双调归并（Bitonic Merge）、键值稳定性（Key-Value Stability）、共享内存（Shared Memory）。

**HGGC 运行时 API**：hggcMalloc, hggcFree, hggcMemcpy, hggcDeviceSynchronize

#### 2.1.5. clock - 设备端时钟微基准

**描述**

本示例使用设备端 `clock()` 内置函数测量不同内存访问模式的时钟周期开销，通过对比**合并访问（coalesced）**与**跨步访问（strided）**，直观展示内存访问合并对吞吐的影响。

两个构建目标共享相同的算法逻辑，演示不同的编译/加载路径：

- **运行时 API 实现**（`clock.hg`）：kernel 与 host 代码在同一文件中静态编译。
- **HGRTC 运行时编译实现**（`clock_runtime_compile.cpp` + `clock_kernel.hg`）：kernel 源在程序启动时由 libHGRTC 即时编译，通过驱动 API 加载执行。

**关键概念**：设备端时钟测量（On-Device Clock）、HGGC 运行时 API、HGRTC 运行时编译、性能优化策略（Performance Strategies）。

**HGGC 运行时 API**：hggcMalloc, hggcMemcpy, hggcFree, hggcDeviceSynchronize

**HGGC 驱动 API**：hgMemAlloc, hgMemFree, hgMemcpyHtoD, hgMemcpyDtoH, hgModuleGetFunction, hgLaunchKernel, hgCtxSynchronize

**构建/运行所需依赖**：HGRTC（运行时编译实现需要）

#### 2.1.6. cooperative_sync - 协作同步原语

**描述**

本示例演示两种 HGGC 协作同步原语：到达等待屏障（Arrive-Wait Barrier）下的向量归一化，以及协作组（Cooperative Groups）下的块内基本用法。两条路径共享设备发现与命令行解析，通过 `--mode=barrier|groups` 子命令切换两种同步原语；默认 `groups` 模式。

**关键概念**：到达等待屏障（Arrive-Wait Barrier）、协作组（Cooperative Groups）。

**HGGC 运行时 API**：hggcStreamCreateWithFlags, hggcFree, hggcDeviceGetAttribute, hggcMallocHost, hggcFreeHost, hggcStreamSynchronize, hggcLaunchCooperativeKernel, hggcMalloc, hggcOccupancyMaxActiveBlocksPerMultiprocessor, hggcMemcpyAsync, hggcOccupancyMaxPotentialBlockSize, hggcDeviceSynchronize, hggcGetErrorString, hggcStreamDestroy

**构建/运行所需依赖**：CPP11, MBCG（`--mode=barrier` 路径需要）

**模式说明**

- `--mode=barrier`：到达等待屏障实现：所有线程通过到达—等待原语完成阶段同步，演示设备端协作屏障下的向量归一化。
- `--mode=groups`（默认）：协作组实现：使用 `cooperative_groups` 提供的 thread_block / thread_block_tile / coalesced_threads 等抽象，展示协作组在线程块内的基本用法。

#### 2.1.7. cpp_template_kernels - C++ 模板内核

**描述**

本示例通过一个**基于策略（Policy-based）的并行归约**，演示 C++ 模板在 PPU 核函数中的高级用法：

- **模板模板参数**：将归约策略（SumOp / MaxOp）作为参数注入核函数；
- **类型安全的动态共享内存包装**：通过 `DynamicSharedBuffer<T>` 实现；
- **模板特化**：为不同数据类型提供单位元（如 `INT_MIN` / `-FLT_MAX`）；
- **多类型 × 多操作组合分发**：一次性验证 `{float, int}` × `{Sum, Max}` 四种组合。

**关键概念**：C++ 模板（Templates）。

**HGGC 运行时 API**：hggcMalloc, hggcMemcpy, hggcGetDeviceProperties, hggcFree, hggcDeviceSynchronize

#### 2.1.8. device_diagnostics - 设备端诊断输出

**描述**

本示例是一个基础的 HGGC 运行时 API 示例，演示了如何在设备代码中使用 printf 函数。

**关键概念**：调试（Debugging）。

**HGGC 运行时 API**：hggcGetDeviceProperties, hggcDeviceSynchronize, hggcGetDevice

#### 2.1.9. driver_runtime_interop - 简单驱动-运行时交互

**描述**

一个简单的示例，演示了 HGGC 驱动 API 和运行时 API 如何协同工作，加载向量加法核函数的 hggc fatbinary 并执行向量加法。

**关键概念**：HGGC 驱动 API、HGGC 运行时 API、向量加法。

**HGGC 运行时 API**：hggcStreamCreateWithFlags, hggcFree, hggcMallocHost, hggcFreeHost, hggcStreamSynchronize, hggcMalloc, hggcMemcpyAsync, hggcStreamDestroy

**HGGC 驱动 API**：hgLaunchKernel, hgModuleLoadData, hgCtxDestroy, hgModuleUnload, hgModuleGetFunction, hgCtxCreate, hgInit

#### 2.1.10. fp16_dot_product - FP16 标量乘积

**描述**

计算两个 FP16 数值向量的标量乘积（点积）。

**关键概念**：HGGC 运行时 API。

**HGGC 运行时 API**：hggcMemcpy, hggcFree, hggcMallocHost, hggcFreeHost, hggcMalloc, hggcGetDeviceProperties

**构建/运行所需依赖**：FP16

#### 2.1.11. matrix_mul - 矩阵乘法

**描述**

本示例演示 PPU 上带偏置的分块 GEMM（`C = alpha * A * B + beta * C`），通过三种 API 路径实现：

- **运行时 API 实现**（`matrix_mul.hg`）：单文件包含 kernel 与主机端，使用事件进行计时。
- **HGRTC 运行时编译实现**（`runtime_compile.cpp`）：使用 HGRTC 对 kernel 源进行 JIT 编译。
- **驱动 API 实现**（`driver_api.cpp`）：加载离线 fatbin，并基于占用率选择 tile 尺寸。

所有实现均采用固定随机种子生成输入，并按相对误差容差与 CPU 参考三重循环计算结果进行校验。

**关键概念**：分块 GEMM（Tiled GEMM）、共享内存（Shared Memory）、偏置项（Bias Term）、CPU 参考校验、HGGC 运行时 API、HGGC 驱动 API、运行时编译（Runtime Compilation）。

**HGGC 运行时 API**：hggcMalloc, hggcMemcpy, hggcFree, hggcEventCreate, hggcEventRecord, hggcEventSynchronize, hggcEventElapsedTime, hggcEventDestroy, hggcDeviceSynchronize

**HGGC 驱动 API**：hgInit, hgCtxCreate, hgCtxDestroy, hgModuleLoadData, hgModuleGetFunction, hgMemAlloc, hgMemFree, hgMemcpyHtoD, hgMemcpyDtoH, hgLaunchKernel, hgOccupancyMaxPotentialBlockSize

**构建/运行所需依赖**：HGRTC（运行时编译实现需要）

#### 2.1.12. mpi_ppu_dispatch - 简单 MPI

**描述**

本示例演示 MPI 与 PPU 结合完成一维温度梯度计算。温度分布通过 `MPI_Scatter` 分发到各 MPI rank，每个 rank 在 PPU 上计算中心差分梯度，随后通过 `MPI_Gather` 收集到根进程进行统计与 CPU 参考校验。

流程：

1. 根进程生成一维温度分布（线性梯度 + 随机扰动）。
2. `MPI_Scatter` 将各分段分发到所有 rank。
3. 每个 rank 在 PPU 上计算梯度：`out[i] = (T[i+1] - T[i-1]) / 2`。
4. `MPI_Gather` 将梯度收集回根进程。
5. 根进程报告最小/最大/均值统计，并与 CPU 参考结果进行校验。

**关键概念**：MPI 集成、PPU 核函数、中心差分（Central Difference）、Scatter/Gather、温度梯度（Temperature Gradient）。

**HGGC 运行时 API**：hggcMalloc, hggcMemcpy, hggcFree, hggcGetLastError

**构建/运行所需依赖**：MPI

#### 2.1.13. multi_device_collab - 多设备协作

**描述**

本示例演示在多个 HGGC 设备上协作工作的两条典型路径：基于 HGGC 上下文管理与多线程访问的多 PPU 异步派发，以及在两块支持点对点（P2P）能力的 PPU 之间通过 P2P 拷贝、P2P 寻址和统一虚拟内存寻址（UVA）完成跨设备核函数计算。两条路径共享设备枚举与拓扑探测，通过 `--mode=multi_dispatch|p2p` 子命令切换；缺省时若存在至少一对 P2P 可达 PPU 自动选择 `p2p`，否则回退到 `multi_dispatch`。

**关键概念**：性能优化策略（Performance Strategies）、异步数据传输（Asynchronous Data Transfers）、HGGC 流和事件（Streams and Events）、统一虚拟地址空间（Unified Virtual Address Space）、点对点数据传输（Peer to Peer Data Transfers）、多线程（Multithreading）、多 PPU。

**HGGC 运行时 API**：hggcStreamDestroy, hggcFree, hggcMallocHost, hggcSetDevice, hggcFreeHost, hggcStreamSynchronize, hggcMalloc, hggcMemcpyAsync, hggcStreamCreate, hggcGetDeviceCount, hggcMemcpy, hggcEventCreateWithFlags, hggcEventSynchronize, hggcDeviceDisablePeerAccess, hggcDeviceSynchronize, hggcEventRecord, hggcGetDeviceProperties, hggcDeviceEnablePeerAccess, hggcEventDestroy, hggcEventElapsedTime, hggcDeviceCanAccessPeer

**构建/运行所需依赖**：only-64-bit

**模式说明**

- `--mode=multi_dispatch`：多 PPU 异步派发：使用 HGGC 上下文管理和多线程访问，在多个 PPU 上运行 HGGC 核函数。
- `--mode=p2p`：跨设备 P2P 协作：在两块相同型号的 PPU 之间通过点对点（P2P）拷贝、P2P 寻址和统一虚拟内存寻址（UVA）完成跨设备 kernel 计算。

#### 2.1.14. occupancy_calculator - 占用率计算器

**描述**

本示例演示了 HGGC 占用率计算器和基于占用率的启动配置器 API 的基本用法，通过启动配置器启动核函数，并测量其与手动配置启动之间的利用率差异。

**关键概念**：占用率计算器（Occupancy Calculator）。

**HGGC 运行时 API**：hggcMemcpy, hggcFree, hggcDeviceSynchronize, hggcEventRecord, hggcGetDevice, hggcMalloc, hggcEventElapsedTime, hggcOccupancyMaxActiveBlocksPerMultiprocessor, hggcGetDeviceProperties, hggcOccupancyMaxPotentialBlockSize, hggcEventCreate

#### 2.1.15. openmp_ppu_dispatch - HGGC OpenMP

**描述**

本示例演示使用 OpenMP 开发多 PPU 应用程序。每个 OpenMP 线程绑定一个 PPU 设备，并使用缩放平移核函数（`out[i] = in[i] * scale + shift`）处理浮点数组的一个切片。结果通过带容差的比较与 CPU 参考结果进行校验。

**关键概念**：OpenMP 集成、多设备派发（Multi-Device Dispatch）、数组缩放（Array Scaling）、CPU 参考校验。

**HGGC 运行时 API**：hggcGetDeviceCount, hggcGetDeviceProperties, hggcSetDevice, hggcGetDevice, hggcMalloc, hggcMemcpy, hggcFree

**构建/运行所需依赖**：OpenMP

#### 2.1.16. project_template - GEMV 项目模板

**描述**

一个基于 **GEMV（矩阵-向量乘 `y = A · x`）** 的 HGGC 项目模板，可作为创建新 HGGC 项目的起点。本示例还演示：

- **混合编译**：`.hg` 核函数 + `.cpp` 主机参考实现，分别编译后链接为单个可执行文件；
- **共享内存分块**：将向量 `x` 分块加载到共享内存，供同一 block 内所有线程复用；
- **多 block 并行**：每个线程负责输出向量 `y` 的一行，grid 自动覆盖整个 M 维；
- **完整的主机端流水线**：设备查询 → 设备内存分配 → H→D / D→H 数据传输 → 核函数启动 → 计时 → CPU 校验。

**关键概念**：共享内存与 `__syncthreads()` 同步（Shared Memory & `__syncthreads()`）、Block/线程索引（Block/Thread Indexing）、设备内存分配与同步（Device Memory Allocation & Synchronization）、主机/设备协作与 CPU 参考校验（Host/Device Collaboration & CPU Reference Verification）。

**HGGC 运行时 API**：hggcMalloc, hggcFree, hggcMemcpy, hggcDeviceSynchronize

#### 2.1.17. stream_callback - 简单 HGGC 回调

**描述**

本示例通过 `hggcStreamAddCallback` 演示异步流回调。多个工作线程（C++11 `std::thread`）在各自独立的流上启动 PPU 核函数；每个流完成时触发主机回调，回调校验结果并对一个 `std::atomic` 计数器发出信号。本示例使用标准 C++ 线程，而非自定义线程封装。

**关键概念**：流回调（Stream Callbacks）、异步执行（Asynchronous Execution）、多线程工作负载（Multi-Threaded Workloads）、std::thread、std::atomic。

**HGGC 运行时 API**：hggcGetDeviceCount, hggcSetDevice, hggcStreamCreate, hggcStreamDestroy, hggcMalloc, hggcFree, hggcHostAlloc, hggcFreeHost, hggcMemcpyAsync, hggcStreamAddCallback

#### 2.1.18. streams_concurrency - 流级并发与计算-拷贝重叠

**描述**

本示例演示 HGGC 流（Streams）级并发的三类典型用法：使用 HGGC 流重叠核函数执行与主机—PPU 设备之间的内存拷贝（并复用 HGGC 固定通用主机内存特性），使用 HGGC 流并发执行多个核函数，以及使用 HGGC 流实现核函数执行与设备数据拷贝的重叠。三条路径共享设备发现与命令行解析，通过 `--mode=streams|hyperq|multicopy` 子命令切换；缺省运行 `streams` 路径。

**关键概念**：异步数据传输（Asynchronous Data Transfers）、HGGC 流和事件（Streams and Events）、HGGC 系统集成、性能优化策略（Performance Strategies）、计算与拷贝重叠（Overlap Compute and Copy）、PPU 性能。

**HGGC 运行时 API**：hggcMemcpy, hggcSetDeviceFlags, hggcSetDevice, hggcEventDestroy, hggcStreamCreate, hggcMallocHost, hggcEventCreateWithFlags, hggcFreeHost, hggcMemcpyAsync, hggcGetDeviceCount, hggcStreamDestroy, hggcMemset, hggcEventElapsedTime, hggcHostAlloc, hggcFree, hggcEventSynchronize, hggcEventRecord, hggcMalloc, hggcGetDeviceProperties, hggcEventCreate, hggcDeviceSynchronize, hggcDeviceGetAttribute

**模式说明**

- `--mode=streams`（默认）：使用 HGGC 流重叠核函数执行与主机—PPU 设备之间的内存拷贝，并复用 HGGC 固定通用主机内存特性。
- `--mode=hyperq`：使用 HGGC 流并发执行多个核函数。
- `--mode=multicopy`：使用 HGGC 流实现核函数执行与设备数据拷贝的重叠。

#### 2.1.19. unified_memory_models - 统一内存编程模型对比

**描述**

本示例对比演示 HGGC 上的两种统一内存编程模型：使用零拷贝（Zero MemCopy），核函数直接读写固定的系统内存；以及在单个 PPU 上使用 OpenMP 和流（Streams）与统一内存（Unified Memory）协同工作。两条路径共享设备发现与命令行解析，通过 `--mode=zero_copy|managed_streams` 子命令切换；缺省时若设备具备 managed memory 能力则自动选择 `managed_streams`，否则回退到 `zero_copy`。

**关键概念**：性能优化策略（Performance Strategies）、固定系统分页内存（Pinned System Paged Memory）、向量加法、HGGC 系统集成、OpenMP、ACBLAS、多线程（Multithreading）、统一内存（Unified Memory）、HGGC 流和事件（Streams and Events）。

**HGGC 运行时 API**：hggcHostAlloc, hggcSetDeviceFlags, hggcSetDevice, hggcGetDeviceCount, hggcHostGetDevicePointer, hggcDeviceSynchronize, hggcFreeHost, hggcGetDeviceProperties, hggcStreamDestroy, hggcFree, hggcMallocManaged, hggcStreamAttachMemAsync, hggcStreamSynchronize, hggcStreamCreate

**构建/运行所需依赖**：OpenMP, UVM, ACBLAS（`--mode=managed_streams` 路径需要）

**模式说明**

- `--mode=zero_copy`：使用零拷贝（Zero MemCopy），核函数可以直接读写固定的系统内存。
- `--mode=managed_streams`：在单个 PPU 上使用 OpenMP 和流（Streams）与统一内存（Unified Memory）协同工作。

#### 2.1.20. vector_add - 向量加法

**描述**

本示例演示 PPU 上的加权向量线性组合（`out[i] = alpha * x[i] + beta * y[i] + gamma`），通过四种 API 路径实现：

- **运行时 API 实现**（`vector_add.hg`）：单文件包含 kernel 与主机端。
- **HGRTC 运行时编译实现**（`runtime_compile.cpp`）：使用 HGRTC 对 kernel 源进行 JIT 编译。
- **驱动 API 实现**（`driver_api.cpp`）：通过驱动 API 加载离线 fatbin。
- **多设备 VMM 实现**（`mmap_multidevice.cpp`）：在支持 P2P 的设备之间进行条带式虚拟地址映射。

所有实现均采用确定性正弦输入，并按相对误差容差进行校验。

**关键概念**：向量运算（Vector Operations）、HGGC 运行时 API、HGGC 驱动 API、运行时编译（Runtime Compilation）、虚拟内存管理（VMM）、多设备映射（Multi-Device Mapping）。

**HGGC 运行时 API**：hggcMalloc, hggcMemcpy, hggcFree, hggcGetLastError

**HGGC 驱动 API**：hgInit, hgCtxCreate, hgCtxDestroy, hgModuleLoadData, hgModuleGetFunction, hgMemAlloc, hgMemFree, hgMemcpyHtoD, hgMemcpyDtoH, hgLaunchKernel

**构建/运行所需依赖**：HGRTC（运行时编译实现需要）；支持多设备 P2P 的真武 PPU（多设备 VMM 实现需要，至少 2 张可互通的设备）

#### 2.1.21. warp_vote_ops - 简单投票内置函数

**描述**

一个简单的程序，演示了如何在 HGGC 核函数中使用投票（Vote）内置指令（__any_sync、__all_sync）。

**关键概念**：投票内置函数（Vote Intrinsics）。

**HGGC 运行时 API**：hggcMemcpy, hggcFree, hggcDeviceSynchronize, hggcMalloc, hggcGetDeviceProperties

比赛关联：入门示例中的 `streams_concurrency`（计算-拷贝重叠）、`async_event_timing`（事件计时）和 `occupancy_calculator`（占用率调优）是做 TTFT 与吞吐量优化时最直接可复用的参考代码。

### 2.2. 实用工具

本目录收录用于查询设备属性与系统拓扑的工具类示例。部分目录在同一 sample 下提供 Runtime API、Driver API 等多种构建变体。

#### 2.2.1. device_query - 设备查询

**描述**

本示例查询并按功能类别（计算、内存、调度、纹理限制、特性）展示 PPU 设备属性，提供两种 API 路径：

- **运行时 API 实现**（`device_query.cpp`）：使用 `DeviceReporter` 类，以分组属性报告和框线绘制格式输出。
- **驱动 API 实现**（`device_query_drv.cpp`）：使用 `hgDeviceGetAttribute` 逐属性查询，并以分段的键值对形式输出。

两个版本还会枚举设备之间的 P2P 拓扑。

**关键概念**：HGGC 运行时 API、HGGC 驱动 API、设备查询（Device Query）、属性检查（Property Inspection）、P2P 拓扑。

**HGGC 运行时 API**：hggcGetDeviceCount, hggcGetDeviceProperties, hggcSetDevice, hggcDriverGetVersion, hggcRuntimeGetVersion, hggcDeviceGetAttribute, hggcDeviceCanAccessPeer, hggcGetErrorString

**HGGC 驱动 API**：hgInit, hgDeviceGetCount, hgDeviceGetName, hgDeviceTotalMem, hgDeviceGetAttribute, hgDriverGetVersion, hgDeviceCanAccessPeer

#### 2.2.2. topology_query - 拓扑查询

**描述**

本示例生成一份结构化的多 PPU 系统拓扑报告，包含四个部分：

1. **设备概览表** — 每个 PPU 的名称、计算单元数量、内存容量与时钟频率；
2. **P2P 连通性矩阵** — 以 ASCII 矩阵可视化展示设备间的访问能力与原子操作支持；
3. **性能分组** — 按 P2P 性能等级分组，辅助选择最优的设备配对；
4. **主机 ↔ 设备属性** — 主机的原子操作、UVA 与托管内存支持状态。

用于在多设备工作负载分配前理解系统互连拓扑，为数据放置与迁移策略提供决策依据。

**关键概念**：性能优化策略（Performance Strategies）、多 PPU。

**HGGC 运行时 API**：hggcGetDeviceCount, hggcGetDeviceProperties, hggcDeviceGetAttribute, hggcDeviceGetP2PAttribute

比赛关联：`device_query` 是拿到比赛用 PPU 服务器后第一件事——确认计算单元数、共享内存大小、显存容量等关键硬件参数，为后续 tile 尺寸与 batch 配置提供依据。

### 2.3. 算法与技术

#### 2.3.1. convolution_separable - HGGC 可分离卷积

**描述**

本示例以高斯模糊为例，演示应用于图像处理的**可分离卷积（Separable Convolution）**：

- 将二维卷积分解为水平 + 垂直两趟一维卷积（复杂度从 O(N²K²) 降至 O(N²K)）；
- 行卷积核函数：每个 block 将 TILE_W 个像素 + 左右 halo 加载到共享内存；
- 列卷积核函数：转置布局确保垂直方向的合并读取；
- 一维核权重存放于 `__constant__` 内存以便广播；
- 高斯核在主机端由 sigma 参数生成，而非随机值。

**关键概念**：图像处理（Image Processing）、数据并行算法（Data Parallel Algorithms）。

**HGGC 运行时 API**：hggcMalloc, hggcMemcpy, hggcFree, hggcDeviceSynchronize, hggcMemcpyToSymbol

#### 2.3.2. ctx_management - 多上下文生命周期管理

**描述**

本示例演示 HGGC Driver API 的**多上下文（Multi-Context）管理**机制：

1. **创建多个上下文** — 在同一设备上创建 N 个独立 `HGcontext`。
2. **上下文迁移** — 工作线程通过 `hgCtxPushCurrent` / `hgCtxPopCurrent` 绑定/解绑上下文。
3. **上下文共享** — 多个线程轮流使用同一上下文（序列化访问）。
4. **HGRTC 编译** — 每个上下文内独立编译和加载 kernel 模块。
5. **正确销毁** — `hgModuleUnload` + `hgCtxDestroy` 清理。

展示的核心 API：

- `hgCtxCreate` — 创建浮动上下文。
- `hgCtxPushCurrent` — 将上下文绑定到当前线程。
- `hgCtxPopCurrent` — 从当前线程解绑上下文（变为浮动）。
- `hgCtxSynchronize` — 等待上下文中所有工作完成。
- `hgCtxDestroy` — 销毁上下文。

**关键概念**：Driver API 上下文管理、多线程上下文迁移、hgCtxPushCurrent / hgCtxPopCurrent、HGRTC 运行时编译。

**HGGC 驱动 API**：hgInit, hgDeviceGet, hgDeviceGetName, hgDeviceGetAttribute, hgDeviceGetCount, hgCtxCreate, hgCtxPushCurrent, hgCtxPopCurrent, hgCtxSynchronize, hgCtxDestroy, hgModuleLoadData, hgModuleGetFunction, hgModuleUnload, hgLaunchKernel, hgMemAlloc, hgMemFree, hgMemcpyDtoH

**构建/运行所需依赖**：HGRTC, C++11 (std::thread)

#### 2.3.3. histogram - HGGC 直方图

**描述**

本示例通过**三种逐步优化的策略**实现 256-bin 字节直方图，展示原子操作与内存私有化对吞吐的影响：

1. **全局 atomicAdd**（基线）— 每个字节直接原子累加到全局内存，争用最高；
2. **共享内存私有化** — 每个 block 在共享内存中维护私有直方图，最后合并到全局；
3. **Warp 级私有化** — 每个 warp 拥有独立子直方图，消除 warp 间争用，吞吐最高。

三种策略在同一数据集上运行以便对比，分别输出各自的吞吐（GB/s），并与 CPU 参考实现校验正确性。

**关键概念**：图像处理（Image Processing）、数据并行算法（Data Parallel Algorithms）。

**HGGC 运行时 API**：hggcMalloc, hggcMemcpy, hggcMemset, hggcFree, hggcDeviceSynchronize, atomicAdd

#### 2.3.4. inline_tix - TIX 内联汇编指令展示

**描述**

本示例演示通过 `asm()` 语句在 HGGC 核函数中嵌入多类 TIX 指令，每条指令配以一个实际用例：

1. **ppu.fma.rtte.f32** — 融合乘加，用于 Horner 法多项式求值（单次舍入精度优势）；
2. **ppu.popc.b32** — 位计数，计算汉明重量；
3. **ppu.mul.wide.s32** — 宽乘法，32×32 → 64 位全精度乘积；
4. **ppu.bfe.u32** — 位域提取，从任意位置提取指定长度的位片段。

每个测试用例均与 CPU 参考实现校验。提供两种构建模式：

- **运行时 API 实现**（`inline_tix.hg`）：静态编译，4 个测试核函数与 host 在同一文件；
- **HGRTC 运行时编译实现**（`inline_tix_hgrtc.cpp` + `inline_tix_kernel.hg`）：HGRTC 即时编译 + 驱动 API。

**关键概念**：性能优化策略（Performance Strategies）、TIX 汇编（TIX Assembly）、HGGC 驱动 API、运行时编译（Runtime Compilation）。

**HGGC 运行时 API**：hggcMemcpy, hggcFree, hggcDeviceSynchronize, hggcMalloc

**HGGC 驱动 API**：hgMemcpyDtoH, hgMemcpyHtoD, hgLaunchKernel, hgCtxSynchronize, hgMemAlloc, hgMemFree, hgModuleGetFunction

**构建/运行所需依赖**：HGRTC（运行时编译实现需要）

#### 2.3.5. radix_sort_thrust - Thrust 数据并行算法流水线

**描述**

本示例演示使用 Thrust 库构建完整的数据处理流水线，展示多个 Thrust 原语的组合使用：

1. **sort** — 基数排序（Thrust 的经典强项）；
2. **unique** — 移除连续重复元素；
3. **transform** — 应用一元函子（对每个元素求平方）；
4. **reduce** — 全局归约（求和）；
5. **inclusive_scan** — 前缀和。

每一步独立计时，展示 Thrust 作为可组合数据并行工具集的能力。

**关键概念**：数据并行算法（Data-Parallel Algorithms）、性能优化策略（Performance Strategies）。

**HGGC 运行时 API**：hggcEventCreate, hggcEventRecord, hggcEventSynchronize, hggcEventElapsedTime, hggcEventDestroy

#### 2.3.6. scan - 多 Block 独占前缀和（Blelloch 算法）

**描述**

本示例采用经典的 Blelloch 工作高效算法实现任意长度的**独占前缀和（exclusive prefix sum）**：

1. **上扫（归约阶段）**：自底向上构建部分和树；
2. **下扫（分发阶段）**：自顶向下分发前缀和。

多 block 策略采用三趟执行：

- 第 1 趟：每个 block 独立扫描其分配的数据块，并写出 block 总和；
- 第 2 趟：对 block 总和数组做前缀和（单 block）；
- 第 3 趟：将 block 前缀加到每个元素上。

支持非 2 的幂次输入长度，并在多种规模下校验正确性。

**关键概念**：数据并行算法（Data-Parallel Algorithms）、性能优化策略（Performance Strategies）。

**HGGC 运行时 API**：hggcMalloc, hggcMemcpy, hggcFree, hggcDeviceSynchronize

#### 2.3.7. spmv - CSR 稀疏矩阵-向量乘

**描述**

本示例实现 **CSR 格式稀疏矩阵-向量乘（y = A * x）**，展示两种 PPU 并行策略在不规则数据结构上的差异：

1. **Scalar（每线程一行）** — 每个线程独立遍历一行的非零元素求内积。实现最简单，但行长度不均匀时存在负载不均衡。
2. **Vector（每 warp 一行）** — 一个 warp（32 线程）协作处理一行：各 lane 以 stride 方式读取非零元素，最后 warp shuffle 归约求和。适合长行、变长行（如幂律图）。

教学要点：

- **间接寻址**：`col_idx[j]` 导致不规则内存访问模式。
- **负载不均衡**：不同行的非零数差异巨大。
- **Warp 协作归约**：`__shfl_down_sync` 在 SpMV 中的实际应用。

测试矩阵为合成的带状稀疏矩阵（对角占优），带宽可配置。

**关键概念**：稀疏矩阵（Sparse Matrix）、CSR 格式、不规则并行（Irregular Parallelism）、负载均衡、Warp 协作归约。

**HGGC 运行时 API**：hggcMalloc, hggcMemcpy, hggcMemset, hggcFree, hggcDeviceSynchronize, __shfl_down_sync

#### 2.3.8. stream_compact - 流压缩（条件过滤）

**描述**

本示例演示 **流压缩（Stream Compaction）** —— 从输入数组中提取满足谓词的元素到紧凑的输出数组中。以"提取素数"为实际用例，展示三种渐进优化策略：

1. **Naive atomic** — 满足条件的线程用 `atomicAdd` 获取输出位置，直接 scatter。实现最简单，但输出无序。
2. **Ballot + popc** — warp 内用 `__ballot_sync` 收集谓词结果，`__popc` 计算 warp 内前缀偏移，block 级用 shared atomic 协调，最后全局 atomic 获取 block 基址。输出 block 内有序。
3. **Two-pass scan** — 第一遍标记 + block 级 exclusive prefix sum 计算写入偏移；第二遍按偏移 scatter。输出完全有序（保留原始相对顺序）。

三种策略在同一数据集 [0, 65536) 上运行，分别计时并与 CPU 参考实现验证正确性。

**关键概念**：流压缩（Stream Compaction）、前缀和（Prefix Sum）、Warp Ballot、原子操作（Atomic Operations）、条件过滤。

**HGGC 运行时 API**：hggcMalloc, hggcMemcpy, hggcMemset, hggcFree, hggcDeviceSynchronize, atomicAdd, __ballot_sync, __popc, __shfl_sync

#### 2.3.9. stream_ordered_allocation - 流有序分配

**描述**

本示例深入演示 HGGC **流有序内存池（Stream-Ordered Memory Pools）**的完整生命周期与机制，通过三种分配策略的性能对比揭示内存池复用的价值：

1. **hggcMalloc（同步）** — 基线：每次迭代同步分配/释放，开销最高；
2. **hggcMallocAsync（threshold=0）** — 异步分配，但内存在释放后立即归还操作系统，无池复用；
3. **hggcMallocAsync（threshold=MAX）** — 异步分配 + 高释放阈值，内存保留在池中供后续分配复用。

演示的内存池管理机制：

- `hggcDeviceGetDefaultMemPool` — 获取默认内存池；
- `hggcMemPoolSetAttribute(hggcMemPoolAttrReleaseThreshold)` — 控制释放策略；
- `hggcMemPoolTrimTo` — 手动裁剪内存池，归还未使用内存；
- **地址复用观测** — 在池复用模式下，连续迭代分配到相同地址。

输出格式化的性能对比表，直观展示池复用带来的分配开销降低。

**关键概念**：性能优化策略（Performance Strategies）。

**HGGC 运行时 API**：hggcMallocAsync, hggcFreeAsync, hggcDeviceGetDefaultMemPool, hggcMemPoolSetAttribute, hggcMemPoolTrimTo, hggcStreamCreateWithFlags, hggcStreamSynchronize, hggcDeviceGetAttribute, hggcDeviceSynchronize, hggcFree, hggcMalloc, hggcMemcpy, hggcMemcpyAsync, hggcMemset, hggcMemsetAsync, hggcStreamDestroy

#### 2.3.10. warp_bitonic_sort - Warp Shuffle 双调排序

**描述**

本示例实现了一种**纯寄存器**的双调排序（Bitonic Sort），使用 `__shfl_xor_sync` 在 warp 内完成 32 元素排序，无需共享内存。然后通过共享内存中的双调合并网络将各 warp 的有序序列合并为 block 级有序输出。

两阶段设计：

1. **Warp-level sort**（Phase 1）：每个 lane 持有一个元素，通过 5 轮 shuffle-XOR 比较交换完成 32 元素双调排序，全程在寄存器中完成。
2. **Block-level merge**（Phase 2）：将 8 个已排序 warp（共 256 元素）通过共享内存双调合并网络合并为一个有序块。

与传统实现的区别：

- 传统方法：所有数据加载到 shared memory → 全部在 shared memory 做比较交换。
- 本方法：warp 内部排序零 shared memory 开销 → 仅跨 warp 合并时使用 shared memory。

**关键概念**：双调排序（Bitonic Sort）、Warp Shuffle（__shfl_xor_sync）、排序网络（Sorting Networks）、寄存器级优化。

**HGGC 运行时 API**：hggcMalloc, hggcMemcpy, hggcFree, hggcDeviceSynchronize

#### 2.3.11. warp_redux - 硬件 Warp 级归约（ppu.redux.sync）

**描述**

本示例演示 TIX 的 `ppu.redux.sync` 指令——一条硬件指令即可完成整个 warp 的归约运算，无需多轮 shuffle 迭代。

每种归约操作同时用两种方式实现并交叉验证：

- **ppu.redux.sync**（单指令，硬件加速）
- **__shfl_down_sync 循环**（传统 5 轮 shuffle 方式）

展示的操作：

1. **ppu.redux.sync.add.s32** — warp 求和。
2. **ppu.redux.sync.min.s32** — warp 最小值。
3. **ppu.redux.sync.max.s32** — warp 最大值。
4. **ppu.redux.sync.xor.b32** — warp 异或（奇偶校验）。

**关键概念**：Warp 级归约（Warp-Level Reduction）、TIX 内联汇编、ppu.redux.sync、硬件加速原语、__shfl_down_sync 对比。

**HGGC 运行时 API**：hggcMalloc, hggcMemcpy, hggcFree, hggcDeviceSynchronize

**TIX 指令**：ppu.redux.sync.add.s32, ppu.redux.sync.min.s32, ppu.redux.sync.max.s32, ppu.redux.sync.xor.b32

比赛关联：`warp_redux` 的单指令 warp 归约可直接用于 softmax、LayerNorm、采样（top-k/argmax）等 decode 热点算子；`stream_ordered_allocation` 的内存池复用对降低每步 decode 的分配开销、压 TTFT 有参考价值。

### 2.4. HGGC 特性

#### 2.4.1. aiu_async_copy - AIU TIX 1.0 异步张量拷贝 + ldmatrix.swzl 解地址

**描述**

本示例展示 **ppu.cp.async.aiu**（TIX 1.0）从全局内存到共享内存的异步张量批量拷贝，以及配套的 **ppu.tc01.ldmatrix.swzl** 解 swizzle 地址并加载到寄存器的完整流水线：

1. **AIU 拷贝** — Thread 0 使用 `ppu.cp.async.aiu.bulk.tensor.shared.global.3d.cg.padz.swzl.b16` 将 16×16 bf16 矩阵从全局内存异步拷贝到 128B 对齐的共享内存，AIU 硬件自动对共享内存地址进行 swizzle 变换以减少 bank conflicts。
2. **同步** — `commit_group` + `wait_group 0` + `__syncthreads` 确保拷贝完成且所有线程可见。
3. **ldmatrix.swzl 加载** — 32 个线程组成的 warp 集体执行 `ppu.tc01.ldmatrix.swzl.sync.aligned.m8n8.x4.shared.b16`，从 swizzle 布局的共享内存中解码数据，每线程获得 4 个 b32 寄存器（共 8 个 bf16 值）。
4. **内容验证** — 每个线程将寄存器片段写回全局内存，主机端对输入/输出做排序后逐元素比对，验证数据搬运正确性。

载荷：单个 16×16 bf16 矩阵（256 元素），顺序递增模式，纯数据搬运（无算术操作），专注 AIU + ldmatrix.swzl 协同机制。

**关键概念**：AIU 硬件单元（ppu.cp.async.aiu）、128B Swizzle 地址变换、ldmatrix.swzl 解地址、异步拷贝同步（commit_group/wait_group）、批量张量拷贝（Bulk Tensor Copy）。

**HGGC 运行时 API**：hggcMalloc, hggcMemcpy, hggcFree, hggcDeviceSynchronize

**TIX 指令**：ppu.cp.async.aiu.bulk.tensor.shared.global, ppu.cp.async.commit_group, ppu.cp.async.wait_group, ppu.tc01.ldmatrix.swzl.sync.aligned.m8n8.x4.shared.b16, ppu.cvta.to.shared.u32

#### 2.4.2. aiu_gemm - AIU GEMM: BF16 GEMM via AIU .swzl Bulk Tensor Copy

**描述**

本示例使用 AIU `.swzl` 模式（128B swizzle）搬运 A 和 B 矩阵，配合 `ldmatrix.swzl` 解地址加载，实现 BF16 矩阵乘法 D = A × B。

关键特性：

- **AIU .swzl** 批量搬运 16×64 tile（dim_c=64 → 128B swizzle）。
- **A 矩阵**：预排列为 16 M-rows × 64 K-cols，`ldmatrix.swzl.m8n8.x4.b16`（无 trans）加载。
- **B 矩阵**：预排列为 16 K-rows × 64 N-cols（原始 row-major，非转置），4 个 N-tile 打包，`ldmatrix.swzl.m16n16.x1.trans.b16` 转置加载 → column-major fragment。
- **channel_offset**：A 选 K-tile，B 选 N-tile。
- **ppu.tc01.mma.m16n16k16.row.col** 累加计算。
- 随机输入验证，相对误差 < 5%。

**分块方案**

```
A tile: 16 M-rows x 64 K-cols (1 M-tile x 1 K-group)
B tile: 16 K-rows x 64 N-cols (1 K-tile x 4 N-tiles packed)

Each block outputs 16x64 (1 M-tile x 4 N-tiles)
Grid: (N/64, M/16)
```

**B 矩阵端到端布局**

```
gmem: B[k][n] row-major (KxN)
  -> pre-tile: B_tiled[r=K, c=N] remains row-major
  -> AIU .swzl: smem remains row-major (with swizzle)
  -> ldmatrix.swzl.m16n16.x1.trans: .trans transpose
  -> fragment: column-major (same n, adjacent k) -> MMA .col check
```

**关键概念**：AIU 硬件单元（ppu.cp.async.aiu）、128B Swizzle 批量搬运、ldmatrix.swzl 解地址、Tensor Cell MMA（ppu.tc01.mma）、BF16 矩阵乘法。

**HGGC 运行时 API**：hggcMalloc, hggcMemcpy, hggcFree, hggcDeviceSynchronize

**TIX 指令**：ppu.cp.async.aiu.bulk.tensor.shared.global, ppu.tc01.ldmatrix.swzl.sync.aligned.m8n8.x4.shared.b16, ppu.tc01.ldmatrix.swzl.sync.aligned.m16n16.x1.trans.shared.b16, ppu.tc01.mma.sync.aligned.m16n16k16

#### 2.4.3. bf16_tensor_cell_gemm - TIX Tensor Cell BF16 GEMM (Double-Buffer)

**描述**

本示例使用**纯 TIX 内联汇编**实现 BF16 矩阵乘法（D = A*B），演示 Tensor Cell 指令的底层用法与双缓冲异步流水线：

核心 TIX 指令：

- `ppu.cp.async.cg.shared.global` — 全局 → 共享异步拷贝（16 字节/线程）；
- `ppu.cp.async.commit_group` / `ppu.cp.async.wait_group` — 异步拷贝组管理；
- `ppu.tc01.ldmatrix.sync.aligned.m8n8.x4.b16` — A 矩阵共享 → 寄存器片段加载；
- `ppu.tc01.ldmatrix.sync.aligned.m16n16.x1.trans.shared.b16` — B 矩阵加载（`.trans` 转置生成列主序片段）；
- `ppu.tc01.mma.sync.aligned.m16n16k16.row.col.f32.bf16.bf16.f32` — 16×16×16 MMA。

算法结构：

1. **序幕（Prologue）**：预取第一个 K-tile 到 shared buffer[0]；
2. **主循环**：预取下一个 K-tile 到 buffer[1-cur]，同时用 buffer[cur] 做 ldmatrix + mma；
3. **尾声（Epilogue）**：处理最后一个 K-tile，写回 f32 结果。

每线程寄存器片段布局（m16n16k16 bf16）：

- A 片段：4 个 `.f16x2` 寄存器（约束 `"r"`）；
- B 片段：4 个 `.f16x2` 寄存器（约束 `"r"`）；
- C/D 片段：8 个 `.f32` 寄存器（约束 `"f"`）。

**关键概念**：矩阵乘法（Matrix Multiply）、AWMMA、Tensor Cell（Tensor Cells）。

**HGGC 运行时 API**：hggcMalloc, hggcMemcpy, hggcMemset, hggcFree, hggcDeviceSynchronize

**TIX 指令**：ppu.cp.async.cg.shared.global, ppu.cp.async.commit_group, ppu.cp.async.wait_group, ppu.tc01.ldmatrix.sync.aligned.m8n8.x4.b16, ppu.tc01.ldmatrix.sync.aligned.m16n16.x1.trans.shared.b16, ppu.tc01.mma.sync.aligned.m16n16k16

**构建/运行所需依赖**：CPP11

#### 2.4.4. binary_partition_cg - Warp 级条件分流（Binary Partition）

**描述**

本示例演示 `cg::binary_partition()` 实现的 **Warp 级动态条件分流**：

给定一组浮点数，每个 warp 在运行时根据数值符号动态拆分为两组：

- **正数组**：组内归约求最大值（`cg::reduce` + `greater`）；
- **负数组**：组内归约求最小值（`cg::reduce` + `less`）。

每个子组的 leader 线程将结果原子写回全局内存，随后与 CPU 参考实现对比校验。

应用场景：

- 机器学习推理中的条件路由（MoE 门控）；
- 物理仿真中的粒子分类；
- 图算法中的异构邻居处理。

**关键概念**：协作组（Cooperative Groups）。

**HGGC 运行时 API**：hggcMalloc, hggcMemcpy, hggcMemset, hggcFree, hggcDeviceSynchronize, cg::binary_partition, cg::reduce

#### 2.4.5. global_to_shmem_async_copy - 异步拷贝同步策略对比

**描述**

本示例对比全局内存 → 共享内存异步拷贝的三种**同步策略**，展示 PPU 特有的 awbar 机制：

1. **Naive** — 显式加载（global → 寄存器 → shared）+ `__syncthreads()`；
2. **cp.async + commit_group/wait_group** — 经典异步拷贝流水线（TIX `ppu.cp.async` 指令族）；
3. **cp.async + awbar** — 到达-等待屏障，将异步拷贝完成与线程同步统一到同一原语中。

awbar 的独特之处：

- `ppu.cp.async.awbar.arrive` 自动将拷贝完成事件关联到屏障；
- 线程与异步操作共享同一计数器；
- `ppu.awbar.test_wait` 非阻塞轮询，支持多阶段奇偶切换；
- 比 commit_group/wait_group 更细粒度，无需全局组编号。

负载：分块向量归约（简单，聚焦于同步机制差异）。

**关键概念**：HGGC 运行时 API、线性代数（Linear Algebra）、CPP11 HGGC。

**HGGC 运行时 API**：hggcMalloc, hggcMemcpy, hggcMemset, hggcFree, hggcDeviceSynchronize

**TIX 指令**：ppu.cp.async.ca.shared.global, ppu.cp.async.commit_group, ppu.cp.async.wait_group, ppu.cp.async.awbar.arrive, ppu.awbar.init, ppu.awbar.arrive, ppu.awbar.test_wait, ppu.cvta.to.shared.u32

**构建/运行所需依赖**：CPP11

#### 2.4.6. graph_conditional_nodes - Graph 条件循环迭代求解器

**描述**

本示例使用 HGGC 图条件节点实现一个**设备端收敛控制的迭代求解器**：用 Jacobi 方法求解三对角线性方程组，循环直至收敛。

图结构：

```text
init_kernel -> WHILE [ jacobi_step -> check_convergence ] -> done_kernel
```

关键机制：

- `hggcGraphConditionalHandleCreate` 创建条件句柄（默认值 1，确保至少执行一次）；
- `hggcGraphAddNode(hggcGraphNodeTypeConditional, hggcGraphCondTypeWhile)` 添加 while 条件节点；
- `hggcGraphSetConditional(handle, 0/1)` 在设备端控制循环终止；
- `hggcStreamBeginCaptureToGraph` 使用流捕获填充循环体。

与 `power_iteration_graph`（使用 `hggcGraphExecKernelNodeSetParams` 动态更新核函数参数）互补——本示例演示条件节点的设备端循环控制能力。

**关键概念**：HGGC 图（Graphs）。

**HGGC 运行时 API**：hggcGraphCreate, hggcGraphAddNode, hggcGraphConditionalHandleCreate, hggcGraphSetConditional, hggcGraphInstantiate, hggcGraphLaunch, hggcGraphExecDestroy, hggcGraphDestroy, hggcStreamCreate, hggcStreamBeginCaptureToGraph, hggcStreamEndCapture, hggcDeviceSynchronize, hggcFree, hggcMalloc, hggcMemcpy, hggcStreamDestroy

#### 2.4.7. graph_memory_footprint - Graph 内存节点缓冲区复用

**描述**

本示例演示 HGGC 图内存节点如何**自动复用临时缓冲区**，降低多步计算流水线的峰值内存占用。

场景：一个 3 步计算流水线（`input*2 -> +1 -> *0.5`），每步需要不同大小的临时缓冲区。

对比：

- **无复用**：所有缓冲区同时存在 → 峰值 = buf1 + buf2 + buf3 = 16 KB；
- **图内存节点**：alloc/free 节点让运行时在上一步释放后复用物理内存 → 峰值 ≈ max(buf1, buf2, buf3) = 8 KB。

演示的 API：

- `hggcGraphAddMemAllocNode` — 在图内分配临时内存；
- `hggcGraphAddMemFreeNode` — 在图内释放（使运行时得以复用）；
- `hggcDeviceGetGraphMemAttribute` — 查询实际内存使用量；
- `hggcDeviceGraphMemTrim` — 释放所有未使用的图内存。

**关键概念**：HGGC 运行时 API、性能优化策略（Performance Strategies）、HGGC 图（Graphs）。

**HGGC 运行时 API**：hggcGraphCreate, hggcGraphAddMemAllocNode, hggcGraphAddMemFreeNode, hggcGraphAddKernelNode, hggcGraphInstantiate, hggcGraphLaunch, hggcDeviceGetGraphMemAttribute, hggcDeviceGraphMemTrim, hggcGraphExecDestroy, hggcGraphDestroy, hggcFree, hggcMalloc, hggcMemcpy, hggcStreamCreateWithFlags, hggcStreamDestroy, hggcStreamSynchronize

#### 2.4.8. graph_memory_nodes - Graph 构建方式对比（API vs Stream Capture）

**描述**

本示例演示构建 HGGC 图的**两种等价方式**，并验证它们产生相同的执行结果：

1. **图 API（显式构建）** — 手动创建节点并指定依赖关系；
   - `hggcGraphAddMemAllocNode` / `hggcGraphAddMemFreeNode` + `hggcGraphAddKernelNode`；
   - 更灵活，可精确控制依赖拓扑。
2. **流捕获（隐式构建）** — 在捕获模式下的普通 HGGC 代码自动生成图；
   - `hggcStreamBeginCapture` → 普通核函数启动 → `hggcStreamEndCapture`；
   - 代码更简洁，与非图代码一致。

计算：`output = input * 2 + 1`（两个核函数节点 + 一个 memcpy 节点）。

**关键概念**：HGGC 图（Graphs）、流捕获（Stream Capture）。

**HGGC 运行时 API**：hggcGraphCreate, hggcGraphAddKernelNode, hggcGraphAddMemAllocNode, hggcGraphAddMemFreeNode, hggcGraphInstantiate, hggcGraphLaunch, hggcGraphExecDestroy, hggcGraphDestroy, hggcStreamBeginCapture, hggcStreamEndCapture, hggcStreamCreateWithFlags, hggcFree, hggcFreeAsync, hggcMalloc, hggcMallocAsync, hggcMemcpy, hggcStreamDestroy, hggcStreamSynchronize

#### 2.4.9. imma_tensor_cell_gemm - TIX Tensor Cell INT8 GEMM (m16n16k32)

**描述**

本示例使用**纯 TIX 内联汇编**实现 INT8 矩阵乘法（D = A*B，s8 输入，s32 累加）。

与 bf16/tf32 版本对比：

| | bf16 | tf32 | **int8（本示例）** |
|---|---|---|---|
| MMA 形状 | m16n16k16 | m16n16k8 | **m16n16k32** |
| A/B 类型 | bf16 (2B) | tf32 (4B) | **s8 (1B)** |
| C/D 类型 | f32 | f32 | **s32** |
| 每 tile 的 K | 16 | 8 | **32** |
| 迭代次数 (K=256) | 16 | 32 | **8** |

核心 TIX 指令：

- `ppu.tc01.mma.sync.aligned.m16n16k32.row.col.s32.s8.s8.s32` — INT8 MMA；
- `ppu.cp.async.cg.shared.global` — 异步拷贝；
- `ppu.tc01.ldmatrix.sync.aligned.m8n8.x4.b16` — 片段加载。

精度特性：整数 MMA 计算无舍入误差，结果应与 CPU 参考精确匹配。

**关键概念**：矩阵乘法（Matrix Multiply）、AWMMA、Tensor Cell。

**HGGC 运行时 API**：hggcMalloc, hggcMemcpy, hggcMemset, hggcFree, hggcDeviceSynchronize

**TIX 指令**：ppu.tc01.mma.sync.aligned.m16n16k32, ppu.cp.async.cg.shared.global, ppu.tc01.ldmatrix.sync.aligned, ppu.cvta.to.shared.u32

#### 2.4.10. new_delete - 设备端链表（new/delete + 虚函数）

**描述**

本示例演示在 PPU 设备端的 **C++ 动态内存管理与多态**：

在设备上构建一个**单向链表**，节点通过 `new` 在设备堆上分配，遍历时通过**虚函数**实现多态行为，并通过 `delete` 释放。

- **DataNode**：`contribute()` 返回 `value`；
- **DoubleNode**：`contribute()` 返回 `value * 2`（多态派生）。

演示的 C++ 特性：

- 设备端 `new` / `delete`（设备堆分配）；
- 虚函数（设备端虚分派）；
- 虚析构函数（正确释放派生类）；
- 指针遍历（链表遍历）；
- `hggcDeviceSetLimit(hggcLimitMallocHeapSize)` 配置设备堆大小。

**关键概念**：设备内存分配（Device Memory Allocation）、C++ 模板（Templates）。

**HGGC 运行时 API**：hggcDeviceSetLimit, hggcMalloc, hggcMemset, hggcMemcpy, hggcFree, hggcDeviceSynchronize

#### 2.4.11. power_iteration_graph - Graph Exec 参数动态更新（幂迭代法）

**描述**

本示例通过**幂迭代法（Power Iteration）**求矩阵最大特征值，展示 `hggcGraphExecKernelNodeSetParams` 在不重建 graph 的情况下**动态更新 kernel 参数**。

算法：

```text
v_new = A * v_old / ||A * v_old||
重复直到收敛，每步交换 v_old ↔ v_new
```

Graph 结构（通过 Stream Capture 构建）：

```text
matvec(A, src, dst) -> norm(dst) -> normalize(dst)
```

每次迭代后通过 `hggcGraphExecKernelNodeSetParams` 交换 src/dst 指针，无需重新实例化 graph。

与 `graph_conditional_nodes`（设备端 while 循环）的区别：本示例的循环在 host 端控制，graph exec 被反复 launch，但节点参数在每次 launch 前更新。

**关键概念**：Graph Exec 参数更新（hggcGraphExecKernelNodeSetParams）、幂迭代法、Stream Capture、迭代收敛。

**HGGC 运行时 API**：hggcGraphExecKernelNodeSetParams, hggcGraphGetNodes, hggcStreamBeginCapture, hggcStreamEndCapture, hggcGraphInstantiate, hggcGraphLaunch, hggcGraphExecDestroy, hggcGraphDestroy, hggcFree, hggcMalloc, hggcMemcpy, hggcStreamCreateWithFlags, hggcStreamDestroy, hggcStreamSynchronize

#### 2.4.12. simple_hggc_graphs - Graph 节点类型全展示

**描述**

本示例在一个连贯的流水线中演示 HGGC 图的**所有核心节点类型**：

**演示 1：事件记录/等待节点**

- `hggcGraphAddEventRecordNode` — 在图内标记完成点；
- `hggcGraphAddEventWaitNode` — 等待来自另一个图的事件；
- 实现精确的跨图同步。

**演示 2：子图节点**

- `hggcGraphAddChildGraphNode` — 将一个完整的图作为单个节点嵌入父图；
- 实现模块化的图组合。

**演示 3：图克隆**

- `hggcGraphClone` — 复制已有图；
- `hggcGraphGetNodes` — 遍历克隆图的节点；
- 用于创建图变体（修改选定节点）。

此外还演示：核函数节点、主机回调节点（`hggcGraphAddHostNode`）。

**关键概念**：HGGC 图（Graphs）、流捕获（Stream Capture）。

**HGGC 运行时 API**：hggcGraphCreate, hggcGraphAddKernelNode, hggcGraphAddEventRecordNode, hggcGraphAddEventWaitNode, hggcGraphAddHostNode, hggcGraphAddChildGraphNode, hggcGraphClone, hggcGraphGetNodes, hggcGraphInstantiate, hggcGraphLaunch, hggcGraphExecDestroy, hggcGraphDestroy, hggcGraphKernelNodeSetParams, hggcEventCreate, hggcEventDestroy, hggcFree, hggcMalloc, hggcMemcpy, hggcStreamCreateWithFlags, hggcStreamDestroy, hggcStreamSynchronize

#### 2.4.13. tf32_tensor_cell_gemm - TIX Tensor Cell TF32 GEMM (m16n16k8)

**描述**

本示例使用**纯 TIX 内联汇编**实现 TF32 精度矩阵乘法（D = A*B），演示 m16n16k8 形状的 Tensor Cell 指令用法。

与 bf16 版本（`bf16_tensor_cell_gemm`）的关键差异：

| | bf16 版本 | tf32 版本（本示例） |
|---|---|---|
| MMA 形状 | m16n16k**16** | m16n16k**8** |
| A/B 数据类型 | bf16 (2B, `.f16x2` 打包) | tf32/f32 (4B, `.b32`) |
| K-tile 大小 | 16 | 8 |
| A/B 加载方式 | ldmatrix | ppu.ld.shared.b32（逐元素） |
| C/D 布局 | 8 个 8×4 子矩阵 | 8 个 8×4 子矩阵（相同） |

核心 TIX 指令：

- `ppu.tc01.mma.sync.aligned.m16n16k8.row.col.f32.tf32.tf32.f32` — 16×16×8 MMA；
- `ppu.cp.async.cg.shared.global` — 异步拷贝；
- `ppu.ld.shared.b32` — 从共享内存加载 tf32 片段；
- `ppu.cvta.to.shared.u32` — 地址空间转换。

**关键概念**：矩阵乘法（Matrix Multiply）、AWMMA、Tensor Cell。

**HGGC 运行时 API**：hggcMalloc, hggcMemcpy, hggcMemset, hggcFree, hggcDeviceSynchronize

**TIX 指令**：ppu.tc01.mma.sync.aligned.m16n16k8, ppu.cp.async.cg.shared.global, ppu.ld.shared.b32, ppu.cvta.to.shared.u32

**构建/运行所需依赖**：CPP11

比赛关联：本节是全套示例中对比赛价值最高的部分——`imma_tensor_cell_gemm`（INT8 m16n16k32 MMA）直接对应 W8 量化推理的底层算子实现；`bf16_tensor_cell_gemm`/`aiu_gemm` 展示双缓冲 + AIU 批量拷贝 + Tensor Cell 的完整高性能 GEMM 流水线；Graph 系列（条件节点、参数动态更新、内存节点复用）对应 decode 阶段的 graph capture 优化，可同时压 TTFT 与每 token 启动开销。

### 2.5. HGGC 库

#### 2.5.1. acdnn_conv_activation - ACDNN 卷积+ReLU 流水线

**描述**

本示例使用 ACDNN 库构建一个经典的 CNN 前向计算流水线：2D 卷积 + ReLU 激活。

演示流程：

1. 创建输入张量（NCHW, FP32）和卷积滤波器（KCRS），用随机数据初始化。
2. 设置 ACDNN 张量描述符、滤波器描述符、卷积描述符和激活描述符。
3. 查询卷积工作空间大小并执行卷积前向计算（`acdnnConvolutionForward`）。
4. 对卷积输出施加 ReLU 激活（`acdnnActivationForward`）。
5. 将结果拷回主机并打印。
6. 在主机端用朴素循环实现参考卷积+ReLU，验证真武 PPU 结果。

**关键概念**：深度学习（Deep Learning）、卷积（Convolution）、激活函数（Activation Function）、ACDNN 库。

**命令行参数**

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| -N=<int> | batch size | 1 |
| -C=<int> | 输入通道数 | 4 |
| -H=<int> | 输入高度 | 8 |
| -W=<int> | 输入宽度 | 8 |
| -K=<int> | 输出通道数 | 8 |
| -R=<int> | 卷积核高度 | 3 |
| -S=<int> | 卷积核宽度 | 3 |
| -device=<id> | 指定真武 PPU 设备 | 默认设备 |

**ACDNN API**：acdnnCreate, acdnnDestroy, acdnnSetStream, acdnnCreateTensorDescriptor, acdnnSetTensor4dDescriptor, acdnnDestroyTensorDescriptor, acdnnCreateFilterDescriptor, acdnnSetFilter4dDescriptor, acdnnDestroyFilterDescriptor, acdnnCreateConvolutionDescriptor, acdnnSetConvolution2dDescriptor, acdnnDestroyConvolutionDescriptor, acdnnGetConvolutionForwardWorkspaceSize, acdnnConvolutionForward, acdnnCreateActivationDescriptor, acdnnSetActivationDescriptor, acdnnDestroyActivationDescriptor, acdnnActivationForward

**HGGC 运行时 API**：hggcMalloc, hggcFree, hggcMemcpy, hggcStreamCreate, hggcStreamDestroy, hggcDeviceSynchronize

**构建/运行所需依赖**：ACDNN

#### 2.5.2. acsolver_dn_lu_factorization - LU 分解深度演示

**描述**

本示例使用 acsolverDn 库对稠密矩阵执行带部分选主元的 LU 分解，并深入展示分解结果的内部结构。

与简单的 "分解→求解" 流程不同，本程序以程序方式生成测试矩阵，提取并打印 L、U 因子和主元序列，在主机端验证 P·A = L·U 的一致性，然后利用分解结果求解线性方程组 A·x = b 并与已知真解对比。

**关键概念**：线性代数（Linear Algebra）、LU 分解（LU Factorization）、ACSOLVER 库。

**工作流程**

1. 生成一个对角占优的随机矩阵 A 和已知解 x_true，计算 b = A*x_true。
2. 在真武 PPU 上执行 LU 分解（`acsolverDnDgetrf`），A 被紧凑的 L*U 存储覆盖。
3. 提取 L（单位下三角）和 U（上三角）因子，并显示主元序列。
4. 在主机端验证 P*A = L*U（重构一致性检查）。
5. 使用分解结果求解线性方程组 A*x = b（`acsolverDnDgetrs`）。
6. 与已知解 x_true 比较，计算相对残差 ||b - A*x|| / (||A||*||x||)。

**命令行参数**

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| -N=<int> | 矩阵阶数 | 5 |
| -seed=<int> | 随机种子 | 基于时间 |
| -device=<id> | 指定真武 PPU 设备 | 默认设备 |

**ACSOLVER API**：acsolverDnCreate, acsolverDnDestroy, acsolverDnSetStream, acsolverDnDgetrf_bufferSize, acsolverDnDgetrf, acsolverDnDgetrs

**ACBLAS API**：acblasCreate, acblasDestroy, acblasSetStream, acblasDgemm_v2

**HGGC 运行时 API**：hggcMalloc, hggcFree, hggcMemcpy, hggcMemset, hggcStreamCreate, hggcStreamDestroy, hggcDeviceSynchronize

**构建/运行所需依赖**：ACSOLVER, ACBLAS

#### 2.5.3. hg_jpeg - HGGCJPEG 简单示例

**描述**

本示例演示使用 hgjpeg 进行批量 JPEG 解码，并在设备端计算像素统计信息。JPEG 文件从目录中加载，通过 `hgjpegDecodeBatched` 批量解码，随后使用自定义 PPU 归约核函数计算每通道像素统计（最小值/最大值/均值），展示 hgjpeg 与核函数的互操作。

流程：

1. 从目录加载 JPEG 文件。
2. 通过 `hgjpegGetImageInfo` 查询图像元数据（尺寸、通道数、子采样）。
3. 通过 `hgjpegDecodeBatched` 批量解码。
4. 在设备端计算每通道像素统计（最小值/最大值/均值）。
5. 打印包含元数据与统计信息的汇总表。

**关键概念**：HGGCJPEG 库、批量解码（Batch Decoding）、像素统计（Pixel Statistics）、设备核函数归约（Device Kernel Reduction）、图像处理（Image Processing）。

**HGGC 运行时 API**：hggcMalloc, hggcMemcpy, hggcMemset, hggcFree, hggcDeviceSynchronize

**HGGCJPEG API**：hgjpegCreateEx, hgjpegJpegStateCreate, hgjpegDecodeBatchedInitialize, hgjpegGetImageInfo, hgjpegDecodeBatched, hgjpegJpegStateDestroy, hgjpegDestroy

**构建/运行所需依赖**：HGGCJPEG

#### 2.5.4. hg_jpeg_encoder - HGGCJPEG 编码器

**描述**

本示例解码 JPEG 图像，并以多个质量等级（30/50/70/90）重新编码，以展示质量与体积之间的权衡。对每张图像，报告各质量等级下的编码体积以及原始文件大小，随后将最高质量的输出写入磁盘。

每张图像的处理流程：

1. 通过 `hgjpegDecode` 解码 JPEG，得到设备端像素数据。
2. 对每个质量等级 Q ∈ {30, 50, 70, 90}：
    - 通过 `hgjpegEncoderParamsSetQuality` 设置质量。
    - 通过 `hgjpegEncodeImage` 编码。
    - 通过 `hgjpegEncodeRetrieveBitstream` 获取码流大小。
3. 打印质量与体积对比表。
4. 将最高质量的输出写入磁盘。

**关键概念**：HGGCJPEG 库、JPEG 编码（JPEG Encoding）、质量-体积权衡（Quality-Size Tradeoff）、转码（Transcoding）、图像压缩（Image Compression）。

**HGGC 运行时 API**：hggcMalloc, hggcFree, hggcDeviceSynchronize

**HGGCJPEG API**：hgjpegCreate, hgjpegJpegStateCreate, hgjpegEncoderStateCreate, hgjpegEncoderParamsCreate, hgjpegEncoderParamsSetQuality, hgjpegEncoderParamsSetSamplingFactors, hgjpegGetImageInfo, hgjpegDecode, hgjpegEncodeImage, hgjpegEncodeRetrieveBitstream, hgjpegEncoderParamsDestroy, hgjpegEncoderStateDestroy, hgjpegJpegStateDestroy, hgjpegDestroy

**构建/运行所需依赖**：HGGCJPEG

#### 2.5.5. jit_lto - 使用 libhgJitLink 的 Saxpy

**描述**

本示例演示对两个分别编译的模块进行运行时 JIT 链接，使用混合输入类型：

- **模块 A（LTO IR）**：使用 `-dlto` 编译的 JIT kernel（`weighted_average`），调用外部设备函数（`blend`）。
- **模块 B（HGBIN）**：`blend` 设备函数的实现，编译为普通 HGBIN（不含 LTO）。

与纯 LTO 链接示例不同，本示例展示混合输入场景：JIT 编译的 kernel 链接到预编译的库函数，这是插件架构和可热更新 kernel 的常见模式。

算法：加权平均（`out[i] = w*x[i] + (1-w)*y[i]`），并与 CPU 参考结果进行校验。

**关键概念**：HGGC 驱动 API、运行时编译（HGRTC）、JIT 链接（hgJitLink）、LTO、LTO IR 与 HGBIN 混合链接。

**HGRTC API**：hgrtcCreateProgram, hgrtcCompileProgram, hgrtcGetLTOIR, hgrtcGetHGBIN, hgrtcGetProgramLog, hgrtcDestroyProgram

**hgJitLink API**：hgJitLinkCreate, hgJitLinkAddData, hgJitLinkComplete, hgJitLinkGetLinkedHgbin, hgJitLinkDestroy, hgJitLinkVersion

**HGGC 驱动 API**：hgInit, hgDeviceGet, hgDeviceGetAttribute, hgCtxCreate, hgCtxDestroy, hgCtxSynchronize, hgModuleLoadData, hgModuleGetFunction, hgModuleUnload, hgMemAlloc, hgMemFree, hgMemcpyHtoD, hgMemcpyDtoH, hgLaunchKernel

#### 2.5.6. simple_acblas_lu - 简单 ACBLAS LU

**描述**

本示例使用 **BLAS Level 1/2/3 基本运算** 实现带部分选主元的 LU 分解，展示基础 BLAS 运算如何组合成更高层的线性代数算法。

本示例并非调用高层的 `getrfBatched`，而是逐步构建分解过程：

- `acblasDswap`：行交换（选主元）。
- `acblasDscal`：列缩放（归一化）。
- `acblasDger`：秩 1 更新（Schur 补）。
- `acblasDgemm`：验证 L*U = P*A。
- `acblasDtrsm`：三角求解（Ax=b 的前代/回代）。

算法：

```text
for k = 0..n-1:
  1. 查找主元（主机端列最大值搜索）
  2. acblasDswap —— 交换第 k 行与主元行
  3. acblasDscal —— 将对角线以下元素按 1/A[k,k] 缩放
  4. acblasDger  —— 对尾部子矩阵做秩 1 更新
```

验证：通过 `acblasDgemm` 计算 L*U，并与置换后的 P*A 比较。

线性求解：通过 `acblasDtrsm` 进行前代（Ly=Pb）与回代（Ux=y）。

**关键概念**：ACBLAS 库、LU 分解（LU Decomposition）、BLAS Level 1/2/3、部分选主元（Partial Pivoting）、Doolittle 分解（Doolittle Factorization）。

**HGGC 运行时 API**：hggcMalloc, hggcMemcpy, hggcFree

**ACBLAS API**：acblasCreate, acblasDestroy, acblasDswap, acblasDscal, acblasDger, acblasDgemm, acblasDtrsm

**构建/运行所需依赖**：ACBLAS

#### 2.5.7. simple_acfft - 简单 ACFFT

**描述**

本示例演示使用 ACFFT 进行频谱分析与频域滤波。将一个复合信号（多个正弦波之和 + 噪声）变换到频域，分析检测主导频率，使用理想矩形低通滤波器进行滤波，再通过逆 FFT 重建。

流程：

1. 在主机端构建复合信号（3 个已知频率的正弦波 + 白噪声）。
2. 通过 `acfftExecC2C` 执行正向 FFT。
3. 设备核函数：计算幅度谱。
4. 检测峰值频率分量（主机端搜索）。
5. 设备核函数：施加理想矩形低通滤波器。
6. 通过 `acfftExecC2C` 执行逆 FFT。
7. 与 CPU DFT 参考结果比较。

**关键概念**：ACFFT 库、频谱分析（Spectrum Analysis）、频域滤波（Frequency Domain Filtering）、低通滤波器（Low-Pass Filter）、DFT。

**HGGC 运行时 API**：hggcMalloc, hggcMemcpy, hggcFree, hggcDeviceSynchronize

**ACFFT API**：acfftPlan1d, acfftExecC2C, acfftDestroy

**构建/运行所需依赖**：ACFFT

比赛关联：`hg_jpeg` 的设备端批量 JPEG 解码对 VLM 比赛的图像预处理环节有直接参考价值——把解码放到 PPU 上可削减 host 端预处理对 TTFT 的拖累。

### 2.6. 性能

#### 2.6.1. aiu_throughput - AIU 与 cp.async 拷贝吞吐对比

**描述**

本示例对比两种 PPU 异步数据拷贝机制，将逐渐增大的 bf16 张量（2KB 到 32KB）从全局内存经共享内存搬运再写回：

- **cp.async**：每线程 4 字节异步拷贝，配合 commit/wait 同步。
- **AIU 批量拷贝**：每 warp 张量拷贝，配合 swizzle 与 ldmatrix.swzl 解地址加载。

测试五种张量规模（16×1×64 到 256×1×64 bf16），以展示吞吐随规模的扩展情况。两种方法均校验数据完整性（输出 == 输入），并报告 GB/s 及加速比。

**关键概念**：AIU 批量拷贝（AIU Bulk Copy）、cp.async、张量共享内存（Tensor Shared Memory）、ldmatrix.swzl、吞吐基准测试（Throughput Benchmarking）、扩展性分析（Scaling Analysis）。

**HGGC 运行时 API**：hggcMalloc, hggcFree, hggcMemcpy, hggcEventCreate, hggcEventRecord, hggcEventSynchronize, hggcEventElapsedTime, hggcEventDestroy, hggcDeviceSynchronize

#### 2.6.2. hggc_graphs_perf_scaling - HGGC 图性能扩展

**描述**

本示例测量 HGGC 图 API 操作（捕获、实例化、启动）随图拓扑规模的扩展表现。通过流捕获构建复杂度递增的并行链式图（10 到 200 个节点），随后对每个阶段分别计时，以展示其扩展行为。

**关键概念**：图捕获（Graph Capture）、图实例化（Graph Instantiation）、图启动（Graph Launch）、流捕获（Stream Capture）、性能扩展（Performance Scaling）、并行拓扑（Parallel Topology）。

**HGGC 运行时 API**：hggcStreamCreate, hggcStreamDestroy, hggcStreamBeginCapture, hggcStreamEndCapture, hggcStreamSynchronize, hggcStreamWaitEvent, hggcEventCreate, hggcEventDestroy, hggcEventRecord, hggcGraphInstantiateWithFlags, hggcGraphLaunch, hggcGraphExecDestroy, hggcGraphDestroy

#### 2.6.3. mem_strategy_bench - 内存分配策略性能对比

**描述**

本示例针对一个简单的逐元素缩放核函数，对比 4 种 PPU 内存分配策略：

- **托管内存（Managed Memory）**：`hggcMallocManaged` + `hggcMemPrefetchAsync`，实现设备/主机间迁移。
- **零拷贝（Zero Copy）**：`hggcHostAlloc`（映射）+ `hggcHostGetDevicePointer`，供设备直接访问主机内存。
- **页锁定 + 异步（Pinned + Async）**：`hggcHostAlloc`（portable）+ `hggcMemcpyAsync`，实现分级传输。
- **可分页 + 同步（Pageable + Sync）**：`malloc` + `hggcMemcpy`，作为基线对比。

测试多种数据规模（256KB 到 4MB），以展示各策略随数据量的扩展表现。

**关键概念**：托管内存（Managed Memory）、零拷贝（Zero Copy）、页锁定内存（Pinned Memory）、异步内存拷贝（Async Memcpy）、内存分配策略（Memory Allocation Strategy）、性能基准测试（Performance Benchmarking）。

**HGGC 运行时 API**：hggcMalloc, hggcFree, hggcMallocManaged, hggcMemPrefetchAsync, hggcHostAlloc, hggcFreeHost, hggcHostGetDevicePointer, hggcMemcpy, hggcMemcpyAsync, hggcDeviceSynchronize

#### 2.6.4. smem_bank_conflict - 共享内存 Bank 冲突影响

**描述**

本示例以不同的访问步长（stride）测量共享内存读取吞吐，展示 bank 冲突如何降低性能。PPU 共享内存包含 32 个 bank（每个 4 字节）；当同一 warp 中的多个线程访问同一 bank 时，访问将被串行化。

测试步长从 1（无冲突）到 32（最大冲突），并报告每种访问模式的有效吞吐（GB/s）及相对效率。

**关键概念**：共享内存（Shared Memory）、Bank 冲突（Bank Conflict）、访问步长（Access Stride）、内存吞吐（Memory Throughput）、性能退化（Performance Degradation）。

**HGGC 运行时 API**：hggcMalloc, hggcFree, hggcMemcpy, hggcEventCreate, hggcEventRecord, hggcEventSynchronize, hggcEventElapsedTime, hggcEventDestroy, hggcDeviceSynchronize

#### 2.6.5. transpose - 矩阵转置

**描述**

本示例针对 bf16 方阵对比三种矩阵转置方法：

- **原生实现（Native）**：使用 16×16 tile 的共享内存分块，并通过填充避免 bank 冲突。
- **AIU + ldmatrix 实现**：AIU 批量拷贝到 TSM + ldmatrix.swzl 解地址 + 转置写回（64×64 tile，每个 tile 4 个 warp）。
- **AIU pipeline 实现**：生产者-消费者双缓冲 + awbarrier 同步（64×64 tile，1 个生产者 warp + 4 个消费者 warp，cp.async.awbar.arrive 关联 AIU 拷贝）。

测试多种矩阵规模（64×64 到 16384×16384）以展示吞吐扩展。三种方法均校验正确性（输出 == 输入的转置）。

**关键概念**：矩阵转置（Matrix Transpose）、共享内存分块（Shared Memory Tiling）、AIU 批量拷贝（AIU Bulk Copy）、ldmatrix.swzl、Bank 冲突规避（Bank Conflict Avoidance）、吞吐基准测试（Throughput Benchmarking）。

**HGGC 运行时 API**：hggcMalloc, hggcFree, hggcMemcpy, hggcEventCreate, hggcEventRecord, hggcEventSynchronize, hggcEventElapsedTime, hggcEventDestroy, hggcDeviceSynchronize

比赛关联：本节的四个微基准（AIU vs cp.async 吞吐、Graph 扩展性、四种内存分配策略、bank 冲突、转置三实现）是评估 PPU 平台特性、为自定义算子选择数据搬运与内存策略的直接依据，可作为吞吐优化实验的起点模板。

## 3. 依赖项

部分 HGGC 示例程序依赖第三方应用程序和/或库，或依赖 T-Head SAIL 软件工具包和驱动程序提供的特性，才能完成构建或执行。以下列出了这些依赖项。

如果某个示例程序所依赖的第三方库在系统上可用但未安装，该示例程序将在构建时自动跳过。

每个示例程序的依赖项列在其 README 的“依赖项”章节中。

### 3.1. 第三方依赖

以下第三方依赖项被部分 HGGC 示例程序所需。如果可用，这些依赖项通常已自动安装在系统上，或可通过系统包管理器（Linux）或第三方网站安装。

#### 3.1.1. 消息传递接口（MPI）

MPI（消息传递接口）是用于分布式进程间数据通信的 API。可通过 Linux 发行版的包管理器安装 MPI 编译器，也可从 Open MPI 等在线资源获取。

#### 3.1.2. OpenMP

OpenMP 是用于多进程编程的 API，可通过 Linux 发行版的包管理器安装，通常随 GCC 预装，也可从 OpenMP 官网获取。

### 3.2. HGGC 特性

部分 HGGC 示例程序展示了以下 HGGC 特性：

#### 3.2.1. 多块协作组

多块协作组（MBCG）扩展了协作组和 HGGC 编程模型，以表达线程块间的同步。

#### 3.2.2. 多设备协作组

多设备协作组扩展了协作组和 HGGC 编程模型，使在多个 PPU 上执行的线程块能够协作和同步。

#### 3.2.3. HGRTC

HGRTC（HGGC 运行时编译）是用于 HGGC C++ 的运行时编译库。

#### 3.2.4. 统一虚拟内存

UVM（统一虚拟内存）支持 CPU 和 PPU 无需显式复制即可访问同一块内存。UVM 仅在 Linux 系统上可用。

#### 3.2.5. 16 位浮点数

FP16 是 16 位浮点格式。1 位用于符号位，5 位用于指数，10 位用于尾数。

#### 3.2.6. C++11 HGGC

hgcc 支持 C++11 特性。
