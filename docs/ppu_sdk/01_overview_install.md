# T-Head SAIL SDK 概览、Release Notes 与安装指南 <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [概览](#概览)
  - [编程指南](#编程指南)
  - [API 参考](#api-参考)
  - [工具链](#工具链)
  - [设备运维和管理](#设备运维和管理)
  - [MISC](#misc)
- [Release Notes (V2.1.1)](#release-notes-v211)
  - [1. 版本概述](#1-版本概述)
  - [2. 支持的操作系统](#2-支持的操作系统)
  - [3. 版本兼容性说明](#3-版本兼容性说明)
  - [4. 已知问题](#4-已知问题)
- [安装指南](#安装指南)
  - [1. 概述](#1-概述)
  - [2. 系统要求](#2-系统要求)
  - [3. 安装方式](#3-安装方式)
  - [4. 设置环境变量](#4-设置环境变量)
  - [5. 验证安装](#5-验证安装)
  - [6. 卸载指南](#6-卸载指南)
  - [7. 下一步](#7-下一步)


## 概览

T-Head SAIL SDK (PPU SDK) 是面向真武 PPU 的软件开发工具包，包含加速库、调试与优化工具、C/C++ 编译器，以及用于部署应用程序的运行时库，提供从开发、优化到部署的全链路支持。

本文随后两节分别是 T-Head SAIL Release Notes（发行说明）与 T-Head SAIL SDK 安装指南（在标准系统上安装和验证 T-Head SAIL SDK 的最基本入门步骤）。

### 编程指南

- **T-Head SAIL HGGC 编程指南**（见 `../ppu_hggc/` 笔记）：详细探讨了 HGGC (HeteroGeneous General-purpose Computing) 编程模型与编程接口，并就如何实现最佳性能提供了简要指导。
- **T-Head SAIL TIX 编程指南**（见 `02_tix_programming.md`）：介绍了如何将 TIX (T-Head Instruction eXtension) 汇编语言语句内联到 HGGC 代码中。TIX 是 HGGC 的虚拟汇编语言和指令集架构（ISA）。文中描述了可用的汇编语句参数和约束条件，并详细介绍了 TIX 的各指令语义和使用方法。
- **T-Head SAIL HGGC 示例程序**（见 `03_hggc_samples.md`）：介绍了 HGGC 示例程序集，面向开发者展示 T-Head SAIL 软件工具包的各项特性，涵盖入门示例、工具类示例、算法与技术、HGGC 特性、HGGC 库、领域应用以及性能优化等多个分类。

### API 参考

- **T-Head SAIL HGGC Runtime API**（见 `04_runtime_api.md`）：HGGC 运行时应用程序编程接口。
- **T-Head SAIL HGGC Driver API**（见 `05_driver_api.md`）：HGGC 驱动应用程序编程接口。
- **T-Head SAIL HGGC Math API**（见 `06_math_api.md`）：HGGC 数学应用程序编程接口。
- **T-Head SAIL acDNN**（见 `07_acdnn.md`）：T-Head SAIL acDNN 库用户指南。T-Head SAIL acDNN 库是一套基于上下文的 API，提供多线程编程支持及与 HGGC Stream 的互操作性，涵盖 Batch Normalization、Softmax、Dropout、CNN、RNN、CTC Loss、Multi-Head Attention 等常见机器学习算子的推理与训练功能。
- **T-Head SAIL acBLAS**（见 `08_acblas.md`）：T-Head SAIL acBLAS 库用户指南。T-Head SAIL acBLAS 库是在真武 PPU 运行时之上实现的 BLAS（基本线性代数子程序）库。
- **T-Head SAIL acFFT**：T-Head SAIL acFFT 库用户指南。T-Head SAIL acFFT 库用于计算离散傅里叶变换（DFT，Discrete Fourier Transform），提供基于 plan 的配置机制，针对给定配置和特定真武 PPU 硬件优化变换性能。
- **T-Head SAIL acSOLVER**：T-Head SAIL acSOLVER 库用户指南。T-Head SAIL acSOLVER 库用于求解稠密线性方程组 Ax = b，提供 QR 分解、LU 分解、Cholesky 分解、Bunch-Kaufman 分解及奇异值分解（SVD）等功能，并提供与 LAPACK 兼容的 API。
- **T-Head SAIL acRAND**：T-Head SAIL acRAND 库用户指南。T-Head SAIL acRAND 库专注于高效生成高质量的伪随机数和拟随机数，支持在设备（PPU）端和主机（CPU）端生成随机数。
- **T-Head SAIL acSPARSE**（见 `09_acsparse.md`）：T-Head SAIL acSPARSE 库用户指南。T-Head SAIL acSPARSE 库提供两套 API 接口，支持稀疏矩阵-向量乘法（SpMV）和稀疏矩阵-矩阵乘法（SpMM）等稀疏线性代数运算，支持 CSR、COO 等存储格式及混合精度计算。

### 工具链

- **T-Head SAIL HGCC**（见 `10_hgcc.md`）：T-Head SAIL HGCC 编译器驱动程序。支持丰富的编译选项。
- **T-Head SAIL HGRTC**（见 `11_hgrtc_jitlink.md`）：HGRTC（HG Runtime Compilation）是一个运行时编译库，接受字符串形式的 HGGC 设备端源代码，在应用程序运行期间即时生成可执行的 HGGC 二进制代码。
- **T-Head SAIL hgJitLink**（见 `11_hgrtc_jitlink.md`）：hgJitLink 库用户指南。hgJitLink 是设备端链接库，支持在运行时将多个 HGGC 设备端目标文件或 LTO IR 链接为可执行的设备二进制代码，适用于动态模块组合与链接时优化（LTO）场景。
- **T-Head SAIL libHGVM**：libHGVM（HG Virtual Machine IR）应用程序编程接口。
- **T-Head SAIL libPPUDevice**：libPPUDevice 库是一个 LLVM（Low Level Virtual Machine）位码库，用于为真武 PPU 核函数实现常用函数。
- **T-Head SAIL Binary Utilities**（见 `12_binary_utilities.md`）：T-Head SAIL 二进制工具应用说明，包括：hgobjdump, hgbat 以及 hgprune。
- **T-Head SAIL hgFatbinary**（见 `12_binary_utilities.md`）：hgfatbinary 是 fatbinary 文件管理工具，用于将不同 PPU 架构的设备代码打包到单一文件中，供驱动程序运行时根据硬件自动选择加载。
- **T-Head SAIL PPU-GDB**（见 `13_ppu_gdb.md`）：PPU-GDB 是基于 GNU GDB 扩展的调试工具，支持在 Linux 系统上同时调试 PPU 设备端代码和 CPU 主机端代码，为开发者提供断点、单步、内存检查等完整的调试能力。
- **T-Head SAIL HGGC Memcheck**（见 `14_memcheck.md`）：HGGC Memcheck 是一套运行时功能正确性检查工具，用于检测 HGGC 应用程序中的设备端内存越界访问、未初始化内存读取等错误，并支持生成 coredump 供 PPU-GDB 加载分析。
- **T-Head SAIL Sanitizer API**：Sanitizer API 支持创建针对 HGGC 应用程序的 sanitizer 工具，例如memcheck（内存访问错误检测）和 racecheck（数据竞争检测）等。

### 设备运维和管理

- **T-Head SAIL PPU-SMI 用户指南**（见 `15_ppu_smi_mps.md`）：PPU-SMI（PPU System Management Interface）是一个基于 HGML（HG Management Library）的命令行工具，用于辅助用户管理和查看 PPU 设备。

### MISC

- **MPS 使用指南**（见 `15_ppu_smi_mps.md`）：PPU MPS（Multi-Process Service）使用指南，介绍多进程共享 PPU 设备的服务机制与配置方法。

比赛关联：概览确认了 SDK 的全组件版图——比赛中模型算子加速主要看 acDNN（MultiHeadAttn、Softmax、Backend fusion）与 acBLAS（Gemm/Matmul+epilogue），量化 kernel 看 Acext 库，自定义算子走 HGCC/TIX/示例程序路线，性能瓶颈定位用 Asight Systems/Compute，设备监控用 PPU-SMI。

## Release Notes (V2.1.1)

### 1. 版本概述

T-Head SAIL 是平头哥独立自主开发的 AI 软件栈，拥有自主可控的软件知识产权，T-Head SAIL 软件生态设计上由接口层、SDK 层与 OS 层组成，具备统一的编程接口，支持平头哥自研软件生态。用户可以基于 T-Head SAIL APIs 开发各种应用软件。

目前主要支持的硬件包括：ICN Switch 1.0、真武 M890、真武 810、真武 805、真武 610、真武 810E、真武 610E。

本文重点介绍 T-Head SAIL 软件栈的主要功能，如果你已经拥有真武 PPU（Parallel Process Unit） 硬件产品，想快速体验的话，请参照开发者文档中心的快速开始，我们提供了多种快速上手体验方式供你选择。

#### 1.1. 支持硬件平台

| **产品** | **真武 PPU 硬件架构** | **支持状态** |
| :---: | :---: | :---: |
| ICN Switch 1.0 | - | 支持 |
| 真武 M890 | ppu0015 | 支持 |
| 真武 810 | ppu001 | 支持 |
| 真武 805 | ppu001 | 支持 |
| 真武 610 | ppu001 | 支持 |
| 真武 810E | ppu001 | 支持 |
| 真武 610E | ppu001 | 支持 |

#### 1.2. 软件栈介绍

T-Head SAIL 软件栈由平头哥独立研发，拥有自主可控的完整知识产权。产品体系采用接口层、SDK 层与 OS 层三层架构，向下抽象与管理底层硬件算力，向上响应并支撑上层应用需求，构建完整的软硬件协同体系，端到端助力客户业务高效落地。

- **接口层**：无缝集成平头哥自研工具链，并全面兼容主流软件生态；有效屏蔽底层硬件差异，显著降低开发者接入门槛。
- **SDK 层**：提供丰富的算法库、运行时组件及开发工具链，赋能开发者与业务团队快速开展应用开发，实现从算法模型到硬件部署的高效转化与落地。
- **OS 层**：通过 内核驱动（KMD，Kernel Mode Driver） 与 OS（操作系统）的深度结合，广泛兼容不同底层硬件平台与主流操作系统，通过系统级性能调优，确保全栈运行效率最大化。

面对未来算力需求的持续增长与场景的不断拓展，平头哥软件栈将以全栈自主能力，充分释放芯片算力潜能，赋能开发者高效创新，持续驱动 AI 产业演进。

<img src="https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125010257/6099b8b665c123239420784582f838ea/SAIL-software-stack.png" alt="T-Head SAIL 软件栈架构图" style="height: 500px; display: block; margin-left: auto; margin-right: auto;" />

#### 1.3. 核心组件

| **组件名称** | **概要说明** |
| :---: | :---: |
| T-Head SAIL KMD |T-Head SAIL 内核驱动  |
| T-Head SAIL UMD/HGGC |T-Head SAIL 用户态驱动和运行时 |
| T-Head SAIL Compiler Toolchain |T-Head SAIL 编译工具链  |
| T-Head SAIL acDNN|T-Head SAIL 深度神经网络库|
| T-Head SAIL acBLAS|T-Head SAIL 基础线性代数库|
| T-Head SAIL acFFT| T-Head SAIL 快速傅里叶变换库|
| T-Head SAIL acSOLVER|T-Head SAIL 求解器库|
| T-Head SAIL acRAND|T-Head SAIL 随机数库|
| T-Head SAIL acSPARSE|T-Head SAIL 稀疏矩阵库|
| T-Head SAIL Acext |T-Head SAIL 量化加速库 |
| T-Head SAIL PCCL |T-Head SAIL 通信加速库 |
| T-Head SAIL PPU-SMI |T-Head SAIL 设备管理工具  |
| T-Head SAIL Asight Systems |T-Head SAIL 性能分析工具 |
| T-Head SAIL Asight Compute |T-Head SAIL 性能分析工具 |
| T-Head SAIL Holmes Inference Engine | T-Head SAIL Holmes 推理引擎 |

#### 1.4. 主要功能

##### 1.4.1. 支持产品系列

+ ICN Switch 1.0、真武 M890、真武 810、真武 805、真武 610、真武 810E、真武 610E，覆盖训练、推理场景。

##### 1.4.2. T-Head SAIL 内核驱动

+ 支持二进制包安装（rpm 或 deb）和 runfile 包安装两种方式，用户可根据需要自由选择，详细用法请参考内核驱动安装指南。
+ 支持内核驱动和 T-Head SAIL SDK 解耦，内核驱动和 T-Head SAIL SDK 在前后三个版本间可兼容使用。
+ 支持单机单卡、单机 8 卡/16 卡（单节点ICN互联）、ICN64超节点（多节点ICN互联）、多机多卡（GDR，GPU Direct RDMA）多种灵活的互联形态，使用 GDR 功能之前需确保系统已安装 alixpu-peermem 内核模块（随 T-Head SAIL 内核驱动一起发布）。
+ 支持真武 PPU 故障上报和故障处理，真武 PPU 故障码详细介绍请参考 PPU XID 定义，错误纠正码（ECC，Error Correcting Code）故障详细处理流程请参考文档 ECC 处理流程。
+ 支持 MPS（Multi Pipe Service）功能，详细使用说明可参考：T-Head SAIL MPS 使用指南（见 `15_ppu_smi_mps.md`）。
+ 支持容器云原生部署方式，详细用法请参考：容器隔离指南。
+ 支持整卡直通虚拟化功能，用户可以在 Host 上解绑真武 PPU 驱动直通进虚拟机内使用，此时需要注意不同虚拟机之间的 ICN 隔离，详细用法请参考 ICN 隔离指南。
+ 支持 MIG（Multi Instance GPU）多实例切分功能，详细用法请参考 MIG 使用指南，使用 MIG 功能时 ICN 互联功能不可使用。
+ 支持虚拟化功能，包括 SR-IOV（Single Root IO Virtualization）和 mdev vgpu 两种虚拟化方式，详细用法请参考 虚拟化指南。

##### 1.4.3. T-Head SAIL 用户态驱动和运行时

+ 支持运行时 API 和驱动 API 两套用户编程接口，详细用法和 API 接口描述请参考文档 T-Head SAIL HGGC Runtime API（见 `04_runtime_api.md`）和文档 T-Head SAIL HGGC Driver API（见 `05_driver_api.md`）。
+ 运行时 API 提供 v2 和 v3 两个版本，用户可根据需求选取对应版本，两个版本的差异请参考文档 HGGC 运行时 API 版本差异（见 `04_runtime_api.md`）。
+ 支持 AD 系列 API 接口，提供真武 PPU 特有的用户编程接口。

##### 1.4.4. T-Head SAIL 编译工具链

+ 全面支持多代芯片产品的编译，可以通过 option 来指定具体架构，默认情况下为全系支持的混合 fatbin 产物。详细介绍请参考 T-Head SAIL HGCC（见 `10_hgcc.md`）。
+ 基于 clang/llvm 的编译框架，实现面向真武 PPU 架构的、host/device 混合编程风格的 C/C++ 扩展语言编译器。
+ 提供丰富的编译功能模块，方便开发者通过 API 的调用方式，灵活构建编译流程，方便集成 JIT（Just-In-Time，即时编译）编译的能力。
+ 支持 system level reserved shared memory 特性。
+ gcc host compiler 的版本支持范围在 [5.5 - 15.0]，clang host compiler 的支持范围在 [clang 9 - clang 21]。
+ 支持 triton 2.3.x、3.0.x、3.1.x、3.2.x、3.3.x、3.4.x、3.5.x; 扩展 triton.lang 的语法，引入对 AIU 的支持; 基于 triton 3.4.x 和 3.5.x 在真武 M890 上支持原生 mxfp4。
+ 支持 tilelang 0.1.6、0.1.7、0.1.7.post3。
+ Device ELF（Executable and Linkable Format，可执行与可链接格式）binary 格式默认打开 split section 选项，减少运行时 module load 开销。
+ 丰富的开发库和二进制工具：hgobjdump、memcheck、ppu-gdb、sanitizer library、hgprune、hgfatbin、hglink & hgJitlink，可以让开发者更加方便地开发和调试。
    - 运行时 JIT 编译库 T-Head SAIL HGRTC（HG Runtime Compilation）, 详细介绍请参考文档 T-Head SAIL HGRTC（见 `11_hgrtc_jitlink.md`）。
    - 发布了真武 PPU 调试工具 PPU-GDB，允许在同一个应用程序中同时调试 PPU 和 CPU 代码，详细介绍请参考文档 T-Head SAIL PPU-GDB（见 `13_ppu_gdb.md`）。
    - 发布了真武 PPU Memcheck，是一组用于功能性正确检查的工具套件。该套件中包含了一系列的检查工具，包括 memcheck、initcheck、synccheck、racecheck。详细介绍请参考文档 T-Head SAIL HGGC Memcheck（见 `14_memcheck.md`）。
    - 发布了真武 PPU Binary 工具 hgobjdump，用于提取 binary 中的 device 相关信息。详细介绍请参考文档 T-Head SAIL Binary Utilities（见 `12_binary_utilities.md`）。
    - 发布了真武 PPU Prune 工具 hgprune，用于提取 binary 中的 device 相关信息。详细介绍请参考文档 T-Head SAIL Binary Utilities（见 `12_binary_utilities.md`）。
    - 发布了真武 PPU Fatbin 开发库 hgfatbin，支持运行时对 fatbin 文件的各类操作。详细介绍请参考文档 T-Head SAIL hgFatbinary（见 `12_binary_utilities.md`）。
    - 发布了真武 PPU JitLink 开发库 hgjitlink，支持运行时对真武 PPU device code 的 link 操作。详细介绍请参考文档 T-Head SAIL hgJitLink（见 `11_hgrtc_jitlink.md`）。

比赛关联：编译工具链对 Triton（2.3.x–3.5.x）与 tilelang 的支持意味着可以把现有的 Triton kernel（如量化 GEMM、attention）移植到 PPU；真武 M890 上基于 triton 3.4.x/3.5.x 的原生 mxfp4 是极低比特量化的硬件路径；Device ELF 默认 split section 减少 module load 开销，直接有利于降低冷启动 TTFT。

##### 1.4.5. T-Head SAIL 加速库

###### 1.4.5.1. 计算加速库

T-HEAD SAIL 计算加速库主要包括：acdnn、acblas、acfft、acsolver、acrand、acsparse。

+ **acdnn 支持算子:**
    - 支持 Conv, BatchNorm, Pooling, Softmax。
    - 支持 Activation, CTCLoss, Dropout, LRN。
    - 支持 LSTM, GRU, MultiHeadAttn, Tensor Ops。
    - 支持 Spatial Transform, Backend fusion。
+ **acblas 支持算子:**
    - 支持 Level1 系列 Op, Gemv, Gemm, Matmul + epilogue。
    - 支持 MatrixTransform, trsm, getrfBatched, getrsBatched。
    - 支持 geqrfBatched, gelsBatched, geam。
    - 新增 SetVector/GetVector/SetMatrix/GetMatrix 系列 API 支持。
    - 新增真武 M890 scale mode 的支持：支持 NT 模式下 VEC128/BLK128x128 scale mode 组合。
+ **acfft 支持算子:**
    - acfft 支持：R2C/C2R/C2C/D2Z/Z2Z + FFT/iFFT 变换。
+ **acsolver 支持算子:**
    - acsolver 支持：矩阵 LU 分解/求解，cholesky 分解/求解，QR 分解，SVD 分解，特征值分解。
+ **acrand 支持算子:**
    - 伪随机生成器 XORWOW、MRG32K3A、PHILOX4_32_10。
    - 数据分布：Default/Uniform/Normal/LogNormal
+ **acsparse 支持算子:**
    - 支持大部分 generic API 及部分 legacy API。
+ **acext 支持算子（不支持真武 M890）:**
    - 支持 A16W8/A16W4 以及 PerChannel/GroupWise 的各种 Kernel 变种。
    - 支持 A8W8 以及 PerChannel/PerToken 的各种 Kernel 变种。
    - 支持 WeightonlyBatchedGemv 对小 batchsize 的加速 kernel。
    - 支持以下类型 MoE：FP16/BF16，a8w8 PerChannel/PerToken。
    - 支持 A8W4-Int8 PerToken/PerChannel GroupGemm Kernel。

###### 1.4.5.2. 互联加速库

+ **PCCL:**
    - 支持 ICN Switch 1.0、真武 M890、真武 810、真武 805、真武 810E、真武 610 及真武 610E 等多种芯片构成的多卡服务器类型；
    - 支持 AllReduce、AllGather、ReduceScatter、Broadcast、Reduce、Send、Recv 等典型互联算子。
    - 支持单机内通过 ICN、PCIE、ShareMemory 等方式做卡间通信。
    - 支持多机之间通过 RDMA (GDR & non GDR)、Socket、ICN 等方式做机间通信。
    - 支持 symmetric memory 功能实现的 AllReduce、AllGather、ReduceScatter 算子。
    - 支持基于 symmetric memory 与 DMA 引擎实现的 AllGather、AlltoAll、Scatter、Gather 算子。
    - 支持用于做通信 hang debug 的 RAS 功能，具体用法可见：PCCL Debug 指南。
    - comm tools:
        * pccl perf:
            + 支持 AllReduce、AllGather、ReduceScatter、AlltoAll、Broadcast 及 Reduce 等典型算子的性能评估。
        * p2pBandwidthAndLatencyPerf:
            + 支持真武 M890、真武 810、真武 805、真武 810E、真武 610 及真武 610E 等多卡服务器下的 icn p2p 互联带宽与延迟性能评估。
        * DeviceOrderSearch tool:
            + 基于 Megatron 框架模型训练任务上的并行配置得到 810 与 810E 机器上的最佳 visible device order 选择。
        * pccl check tools:
            + 支持真武 M890、真武 810、真武 805、真武 810E、真武 610 及真武 610E 等产品多机多卡业务场景下的环境完备性检查。
        * sailbandwidth:
            + 支持真武 M890、真武 810、真武 805、真武 810E、真武 610 及真武 610E 等服务器单机与多机环境下的 PPU IO 带宽性能评估, 具体用法可见 sailbandwidth 使用指南。

+ **DeepEP-for-sail:**
    - 支持 ICN Switch 1.0、真武 M890、真武 810、真武 805、真武 810E、真武 610 及真武 610E 等多种芯片构成的多卡服务器类型。
    - 兼容支持 DeepEP 绝大多数 python API 用法; DeepEP-for-sail API 指南。
    - 支持单机内与多机间的 dispatch 与 combine intranode、internode 与 internode low latency 三种类型 kernel 实现。
    - 支持通过 icn link 及节点间的 rdma ibgda 或 ibrc 等传输方式进行通信。
    - 支持 low latency dispatch kernel 经过 int8 & fp8 & fp4 量化后做低精度传输的优化。
    - 支持 low latency combine kernel 经过 int8 & fp8 量化后做低精度传输的优化。
    - 支持 combine single batch overlap 功能。

比赛关联：Acext 量化加速库（A16W8/A16W4 PerChannel/GroupWise、A8W8 PerChannel/PerToken、WeightonlyBatchedGemv 小 batch 加速）是比赛"量化"评分的核心武器，但注意其不支持真武 M890；acBLAS 的 Matmul + epilogue 融合和 M890 scale mode（VEC128/BLK128x128）则对应吞吐与量化 GEMM 优化。

##### 1.4.6. T-Head SAIL Video/Image 硬件加速

真武 PPU 上支持视频编解码，图像编解码和 2D 图像后处理的硬件加速，包括 HG Decoder（HGDEC）、HG Encoder（HGENC）、HG JPEG（hgJPEG）、HG Image Processing Primitives（HGPP）。支持真武 M890、真武 610、真武 810、真武 805、真武 810E、真武 610E 平台。

###### 1.4.6.1. Video Decode

+ Codecs：
    - 高效视频编码（HEVC，High Efficiency Video Coding）（H.265）-ITU-T Rec.H.265（04/2013）, ISO/IEC 23008-2：
        * Main Profile, Level 5.1, High Tier。
        * Main10 Profile, Level 5.1, High Tier。
        * Main Still Profile。
    - VP9 - vp9-bitstream-specification-v0.6-20160331-draft：
        * Profile 0, 8-bit。
        * Profile 2, 10-bit。
    - 高级视频编码（AVC，Advanced Video Coding）（H.264）- ITU-T Rec.H.264（03/2010）/ ISO / IEC 14496-10：
        * Main Profile, levels 1 - 5.2。
        * High Profile, levels 1 - 5.2。
        * High 10 Profile, levels 1 - 5.2。
        * Baseline Profile, levels 1 - 5.2。
    - AV1 Bitstream & Decoding Process Specification Version 1.0.0 with Errata 1：
        * Main Profile, Level 5.1。
    - AVS2。
+ 最高分辨率支持到 8192x8192。

###### 1.4.6.2. Video Encode

+ Codecs：
    - AVC（H.264）：Spec Version 12:ISO/IEC 14496-10 / ITU-T Rec.H.264（03/2010）：
        * Baseline Profile, levels 1 – 5.2。
        * Main Profile, levels 1 - 5.2。
        * High Profile, levels 1 - 5.2。
        * High 10 Profile, levels 1 - 5.2。
    - HEVC（H265）：ITU-T Rec. H.265（04/2013）, ISO/IEC 23008-2：
        * Main Profile, Level 5.1, High Tier。
        * Main10 profile, Level 5.1, High Tier。
        * Main Still Profile。
    - AV1 Bitstream Specification Version 1.0.0 with Errata 1：
        * Main Profile, Level 5.1。
+ 分辨率最高支持到 4K。
+ 支持输入 RGB format（converted to YUV420 via inlinePP）。
+ 支持 crop, scale, rotate with inlinePP。

###### 1.4.6.3. Jpeg

+ 最高分辨率：32Kx32K。
+ 支持 RGB format input and output with inlinePP。
+ 支持 crop, scale, rotate with inlinePP。

###### 1.4.6.4. Image Process

+ 支持 HGPP 2D image processing。

###### 1.4.6.5. 性能

| **真武 810E** | **真武 M890** |
| :---: | :---: |
| FHD 160 streams | FHD 64 streams |
| FHD 32 streams | FHD 16 streams |
| UHD 960FPS | UHD 480FPS |

比赛关联：VLM 的图像预处理（解码、crop、scale）可卸载到 HGPP/hgJPEG 硬件单元，减少 host 侧预处理对 TTFT 的占用。

##### 1.4.7. T-Head SAIL 性能分析工具

我们发布了 T-HEAD SAIL 性能分析工具 T-Head SAIL Asight Systems 和 T-Head SAIL Asight Compute，可以支持开发者进行单机、多机训练、推理等场景的性能分析。

###### 1.4.7.1. T-Head SAIL Asight Systems

Asight Systems 是一款低开销的系统级的性能分析工具，用来采集系统各种事件，CPU 和 PPU 的活动，API 执行时间以及相关调用栈，HG Tool Extension（HGTX），CPU/PPU activity 关联关系等，在 Timeline View 上统一的可视化呈现出来。 通过 Timeline View，开发人员可以方便分析 CPU/PPU 的负载和关联关系，找到性能瓶颈，确保 CPU 和 PPU 能够协调的工作，确保最大的并行度。Asight 支持统计系统方便对报告进行后处理。详细介绍请参考 Asight Systems 使用指南。

关于 Asight Systems 版本的详细功能更新请参考 Asight Systems Release Notes。

###### 1.4.7.2. T-Head SAIL Asight Compute

Asight Compute 是一款 kernel 性能分析工具，通过采集真武 PPU 硬件 perf counter，组合成为一系列性能指标，我们称为 metrics。GUI 通过各种维度，把这些 metrics 呈现出来, 帮助开发者深入分析和优化 kernel。详细介绍请参考 Asight Compute 使用指南。

关于 Asight Compute 版本的详细功能更新请参考 Asight Compute Release Notes。

比赛关联：Asight Systems（timeline 级 CPU/PPU 关联分析）定位 TTFT 瓶颈（host 开销 vs device 空闲），Asight Compute（硬件 perf counter/metrics）做 kernel 级算子调优，两者是"系统级优化深度"评分的主要取证工具。

##### 1.4.8 T-Head SAIL 设备运维和管理

为了满足云计算大规模集群监控需求，我们发布了如下真武 PPU 管理和监控工具和库文件，以便集成到客户集群运维监控系统中。

PPU-SMI（PPU System Management Interface） 是一个基于 HG Management Library（HGML） 的命令行工具，用于辅助用户管理和查看真武 PPU 设备。

通过 PPU-SMI 命令行工具，用户可以：

+ 修改设备配置/特性开关
+ 查询指定设备运行参数和特性使能状态
+ 收集运行数据/特定事件，导出至表格供后续分析
+ 分析各个应用程序的设备资源使用情况
+ 查询多个真武 PPU 设备的拓扑信息

详细介绍请参考文档 T-Head SAIL PPU-SMI（见 `15_ppu_smi_mps.md`）。

+ PPU-SMI v2.1.1 新功能主要包含：
    - 增加支持指定设备组件复位的描述
    - 增加查询 PCI class code、addressing mode、Fabric 信息、Compute Capability、Extended GPU Memory（EGM）能力的描述
    - 增加 drain 子命令支持 discover 和 remove 选项的描述
+ 支持真武 M890、真武 610、真武 810、真武 805、真武 810E、真武 610E 平台

### 2. 支持的操作系统

| **操作系统** | **架构** | **默认 GCC 版本** |
| :---: | :---: | :---: |
| Ubuntu 24.04 LTS | x86_64 | 13.3.0 |
| Ubuntu 22.04 LTS | x86_64 | 11.4.0 |
| Ubuntu 20.04 LTS | x86_64 | 9.5.0 |
| Ubuntu 18.04 LTS | x86_64 | 7.5.0 |
| CentOS7.9 | x86_64 | 7.3.1 |
| CentOS8.2 | x86_64 | 8.5.0 |
| Alios7u2 | x86_64 | 8.3.1 |
| Alios8u2 | x86_64 | 10.2.1 |
| ALinux3 | x86_64 | 10.2.1 |

### 3. 版本兼容性说明

V2.1.1 是 T-Head SAIL SDK 首个公开发布的版本，如需获取早期版本的 SDK，请联系技术支持团队（sail.support@thead.com）获取。

#### 3.1. KMD 兼容性

+ 真武 M890 产品需同时使用 V2.1 SDK 和 V2.1 KMD 版本。
+ V2.1 版本 T-Head SAIL SDK 向前兼容 V1.6.x 和 V2.0.x 版本的 KMD。
+ V2.1 版本 KMD 向前兼容 V1.7.x 和 V2.0.x 版本的 T-Head SAIL SDK。
+ V2.1 版本 T-Head SAIL SDK 推荐搭配 V2.1 版本 KMD 使用，以获得最全的功能和最佳性能。

#### 3.2. SDK 兼容性

+ device binary 在 SDK V1.5 中对文件格式做了版本升级，不再兼容旧版本的 binary 格式。
+ SDK V2.1 同 SDK V2.0、V1.7、V1.6、V1.5 之间，保持在编程API接口的兼容性。但在Device二进制格式和库文件的兼容性方面：
    - 后向兼容：
      在旧版本 SDK（V2.0、V1.7、V1.6、V1.5）上编译的产物能够在 SDK V2.1 的环境中正常执行。
    - 前向不兼容：
      在SDK V2.1 上编译的产物不能确保在旧版本 SDK （V2.0、V1.7、V1.6、V1.5）的环境中正常执行。
+ SDK V2.1 同 SDK V1.4 及之前的版本不兼容。

### 4. 已知问题

#### 4.1. 加速库

+ 性能：性能泛化能力加强中。
+ **acblas：**
    - 不支持复数数据类型。
    - Gemm: 默认打开 FP32 Tensor Cell，由于计算顺序等原因导致精度不能和 FP32 FMA 完全匹配。
        * 可以通过 `export PPU_FP32_TENSOR_OVERRIDE=0` 关闭 FP32 Tensor Cell 解决。
    - Gemv：仅支持 host 指针模式。
    - BlasLt：不支持 algo/perf 等指定属性；真武 M890 不支持 col32 layout。
+ **acdnn：**
    - Conv：不支持 INT64/BOOLEAN 数据类型，不支持输入 FP16 + 输出 FP32。
    - 3DConv：有限调优，性能待加强。
    - depthwise：某些 dgrad 用例性能待加强。
    - BN：仅支持`alpha==1`和`beta==0`参数；不支持`ACDNN_BATCHNORM_PER_ACTIVATION`模式。
    - Pooling：不支持`ACDNN_PROPAGATE_NAN`。
    - RNN：仅支持`acdnnRNNBiasMode_t DOUBLE`；仅支持 FP16/F32 数据类型；仅支持`ACDNN_RNN_ALGO_STANDARD`。
    - Activation：不支持`ACDNN_PROPAGATE_NAN`；不支持 SWISH Op。
    - Softmax：不支持`SoftmaxAlgorithm_t FAST`。
    - TensorOp：acdnnReduceTensor 不支持`MUL_NO_ZEROS`。
    - MultiHeadAttn：仅支持前向 op；不支持真武 M890。
    - Backend：不支持前处理融合；仅支持最多 4 个 pointwise 后处理融合；仅支持 fp16/fp32/bf16 数据类型（真武 M890 有限支持 FP8）；融合的 pointwise 操作仅支持`alpha1 = 1`和`alpha2 = 1`。
+ **acsolver：**
    - 不支持复数数据类型。
+ **acfft：**
    - 不支持 LTO 优化。
+ **acrand：**
    - 仅支持类型：XORWOW/MRG32K3A/PHILOX4_32_10。
    - 仅支持 Legacy order。
    - 仅支持分布类型：default、uniform、uniform double、normal、normal double、lognormal、lognormal double。
+ **acext:**
    - 只支持 TP 和 Native EP 运行模式，不支持 DeepEP。
    - A8W4-Int8 算子量化仅支持 Channelwise，暂不支持 Groupwise/Blockwise，部分模型可能存在精度损失；且目前只接入 MoE 接口，暂未支持 DenseGemm 接口；ACEXT 算子性能泛化需配合 AutoTune LUT。
+ **DeepGemm:**
    - 真武 M890 支持 MXFP4，Scale 类型为 E8M0；当前算子性能泛化需配合 AutoTune LUT。

比赛关联：已知问题里有三条直接影响比赛精度与算子选型——(1) acBLAS Gemm 默认开启 FP32 Tensor Cell 导致与 FP32 FMA 精度不完全匹配，可用 `export PPU_FP32_TENSOR_OVERRIDE=0` 关闭，这是精度对齐排查的第一环境变量；(2) acdnn MultiHeadAttn 仅前向且不支持 M890，attention 可能需自写或用 Backend fusion；(3) Acext A8W4-Int8 仅 Channelwise、未接 DenseGemm，且算子性能泛化依赖 AutoTune LUT，量化方案设计需避开这些缺口。

#### 4.2. 互联库

+ T-Head SAIL PCCL 已知问题请参考：PCCL 已知问题。

#### 4.3. Video Codec/Image 硬件加速

+ Video decode 不支持 MPEG1，MPEG2，MPEG4，VC1，VP8 等 legacy 格式。
+ JPEG 不支持 lossless，不支持 JPEG2000。
+ HGPP 目前只支持 Image Process 接口，不支持 Signal Process 接口。

#### 4.4. 工具

+ T-Head SAIL Asight Systems 已知问题请参考： Asight Systems 已知问题。
+ T-Head SAIL Asight Compute 已知问题请参考： Asight Compute 已知问题。

#### 4.5. 设备运维和管理

T-Head SAIL PPU-SMI 已知问题请参考： PPU-SMI 已知问题（见 `15_ppu_smi_mps.md`）。

## 安装指南

### 1. 概述

本文档旨在为开发者提供在 Linux 系统上快速安装和运行 T-Head SAIL SDK（也称为 PPU SDK）的完整指南。通过本指南，你将了解如何下载、安装 PPU SDK，并验证安装是否成功。

安装完成后，可参阅 T-Head SAIL HGGC 编程指南（见 `../ppu_hggc/`）开始编写第一个 PPU 程序，或通过 HGGC 示例程序（见 `03_hggc_samples.md`）快速体验各项功能。

### 2. 系统要求

#### 2.1. 支持的硬件平台

目前主要支持的真武 PPU 硬件产品系列包括：真武 M890、真武 810、真武 805、真武 610、真武 810E、真武 610E。

#### 2.2. 支持的操作系统

| 操作系统系列 | 支持版本 |
| :---: | :---: |
| Ubuntu | 18.04 , 20.04 , 22.04 , 24.04 |
| CentOS | 7.9 , 8.2 |
| AliOS | 7 Update 2 , 8 Update 2 |
| Alinux | 3，4 |
| Anolis OS | 8.6 |

#### 2.3. 依赖软件要求

- **GCC**: 5.5 ~ 15.0
- **Clang**: 9 ~ 21

### 3. 安装方式

在 Linux 系统上，PPU SDK 可以通过 Runfile 进行安装。Runfile 是一个自解压脚本安装包，支持通过命令行参数自定义安装行为。安装前可使用 `--help` 参数查看所有可用选项。

#### 3.1. 下载安装包

请访问 T-Head 开发者下载中心下载与你操作系统匹配的安装包。
每个操作系统提供 HGGCRT（HGGC Runtime，HGGC 运行时库）v2 和 v3 两个版本的安装包。v3 版本向下兼容 v2 的 API，并新增了更多功能接口，推荐下载 HGGCRT v3 版本。

#### 3.2. 安装参数说明

下表列出了 Runfile 安装程序支持的常用参数：

| 参数 | 功能描述 | 示例/备注 |
| :---: | :---: | :---: |
| `--help` | 显示帮助信息并退出 | 用于快速查阅所有可用参数 |
| `--silent` | 静默安装模式：自动跳过所有交互式提示，隐含接受最终用户许可协议（EULA） | 适用于自动化部署场景 |
| `--prefix=<PATH>` | 指定软件安装根目录，默认路径：`/usr/local/PPU_SDK` | 示例：`--prefix=/opt/`，请确保目标路径存在且当前用户有写入权限 |
| `--tmpdir <PATH>` | 指定临时文件存放目录，默认使用系统 `/tmp` 目录。当 `/tmp` 挂载为 `noexec` 时需手动指定其他可执行目录 | 示例：`--tmpdir /var/tmp` |

#### 3.3. 执行安装

以 Ubuntu 24.04、HGGCRT v3 为例（此制品版本为示例信息，请以实际下载制品为准），使用静默模式安装：

```bash
bash ppu_hggcrt3_ubuntu2404-2.1.1-d63d35.run --silent
```

以上命令未使用 `--prefix` 参数指定安装路径，PPU SDK 将默认安装到 `/usr/local/PPU_SDK` 目录。

如需安装到指定位置，可使用 `--prefix` 参数，如：

```bash
bash ppu_hggcrt3_ubuntu2404-2.1.1-d63d35.run --prefix=/opt/ --silent
```

### 4. 设置环境变量

安装完成后，需要设置 PPU SDK 环境，才能使用相关命令和工具。

```bash
source /usr/local/PPU_SDK/envsetup.sh
```

> **注意**：如果安装时使用了 `--prefix` 指定了自定义路径，请将环境变量命令中的路径替换为实际安装路径。例如，指定 `--prefix=/opt/` 时：
>
> ```bash
> source /opt/PPU_SDK/envsetup.sh
> ```

### 5. 验证安装

#### 5.1. 检查设备状态

运行以下命令，确认 Driver Version 和设备信息正确显示：

```bash
ppu-smi
```

#### 5.2. 验证 PPU SDK

运行以下命令，确认 PPU SDK 版本信息正确显示：

```bash
hgcc --version
```

### 6. 卸载指南

Runfile 安装的 PPU SDK 需要手动卸载，只需删除安装目录即可：

```bash
# 默认安装路径
rm -rf /usr/local/PPU_SDK

# 或自定义安装路径，如：
rm -rf /opt/PPU_SDK
```

### 7. 下一步

安装完成后，可以通过以下文档继续：

- T-Head SAIL HGGC 编程指南（见 `../ppu_hggc/`）：了解 PPU 并行编程模型，编写第一个核函数
- T-Head SAIL HGGC 示例程序（见 `03_hggc_samples.md`）：运行完整示例，快速熟悉各项功能
- T-Head SAIL SDK Release Notes（见本文"Release Notes"一节）：了解当前版本的新功能与已知问题

比赛关联：复赛 PPU 服务器部署的关键动作全在本节——选 HGGCRT v3 安装包（向下兼容 v2 API）、`--silent` 静默安装、自定义 `--prefix` 时同步改 `envsetup.sh` 路径，最后用 `ppu-smi` + `hgcc --version` 两条命令验收环境，即可进入 HGGC 编程与 benchmark 移植。
