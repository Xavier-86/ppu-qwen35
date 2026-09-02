# T-Head SAIL 入门指南：软件栈概览、环境搭建与部署 <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [1. T-Head SAIL 软件栈概览](#1-t-head-sail-软件栈概览)
  - [1.1 应用层](#11-应用层)
  - [1.2 SDK 层](#12-sdk-层)
  - [1.3 OS 层 — 内核驱动（KMD）](#13-os-层-内核驱动kmd)
  - [1.4 文档入门指南导览](#14-文档入门指南导览)
- [2. 术语表](#2-术语表)
- [3. 快速开始](#3-快速开始)
  - [3.1 前置条件](#31-前置条件)
  - [3.2 软件制品清单](#32-软件制品清单)
  - [3.3 安装 KMD 内核驱动](#33-安装-kmd-内核驱动)
  - [3.4 安装 T-Head SAIL SDK](#34-安装-t-head-sail-sdk)
  - [3.5 安装高性能互联库（可选）](#35-安装高性能互联库可选)
  - [3.6 验证安装](#36-验证安装)
  - [3.7 常见安装问题](#37-常见安装问题)
  - [3.8 下一步](#38-下一步)
- [4. SDK 层](#4-sdk-层)
  - [4.1 T-Head SAIL 用户驱动](#41-t-head-sail-用户驱动)
  - [4.2 T-Head SAIL HGGC 运行时（Runtime）](#42-t-head-sail-hggc-运行时runtime)
  - [4.3 编译器](#43-编译器)
  - [4.4 性能分析工具](#44-性能分析工具)
  - [4.5 计算加速库](#45-计算加速库)
  - [4.6 高性能互联](#46-高性能互联)
- [5. KMD 层](#5-kmd-层)
  - [5.1 KMD 内核驱动](#51-kmd-内核驱动)
  - [5.2 KMD 安装指南](#52-kmd-安装指南)
  - [5.3 ECC 错误处理](#53-ecc-错误处理)
  - [5.4 XID 错误代码](#54-xid-错误代码)
- [6. 部署方式](#6-部署方式)
  - [6.1 选型概览](#61-选型概览)
  - [6.2 共性前置条件](#62-共性前置条件)
  - [6.3 裸金属部署](#63-裸金属部署)
  - [6.4 容器部署](#64-容器部署)
  - [6.5 虚拟机部署](#65-虚拟机部署)
- [7. 支持](#7-支持)
  - [7.1 获取帮助](#71-获取帮助)
- [8. T-Head SAIL HGGC Driver API 文档结构](#8-t-head-sail-hggc-driver-api-文档结构)
- [9. T-Head SAIL HGGC Runtime API 文档结构](#9-t-head-sail-hggc-runtime-api-文档结构)



## 1. T-Head SAIL 软件栈概览

**T-Head SAIL** 是平头哥为真武系列 AI 芯片打造的软件栈，拥有完整自主知识产权，全面兼容主流 AI 生态。软件栈覆盖 **OS 层**、**SDK 层**与**接口层**的完整链路——向下释放真武硬件算力，向上承接上层应用需求。

<img src="https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125010257/6099b8b665c123239420784582f838ea/SAIL-software-stack.png" alt="T-Head SAIL 软件栈架构图" style="height: 500px; display: block; margin-left: auto; margin-right: auto;" />

> **名称说明**：真武系列 AI 芯片也称真武 PPU（Parallel Process Unit）。考虑到开发者表述习惯，文档与代码/路径中的 **PPU** 指**真武 PPU**，**PPU_SDK** 标识符指 **T-Head SAIL SDK**。

### 1.1 应用层

**T-Head SAIL 软件栈**已全面支持主流开源 AI 框架与工具链，覆盖各类深度学习及高性能计算等应用场景。所有软件框架均通过 **T-Head SAIL API** 调用底层真武 PPU 硬件算力，应用层代码可以实现无缝迁移。

- vLLM、SGLang、PyTorch、TensorFlow、MXNet
- Triton、Megatron-LM、DeepSpeed、PaddlePaddle、Holmes-LLM、etc

> 完整适配列表与使用指南，请访问 **[平头哥 GitHub 主页](https://github.com/t-head/)** 查阅对应仓库。

### 1.2 SDK 层

**T-Head SAIL SDK** 是平头哥自主研发的完整 AI 软件开发工具包，具备统一的编程接口 **T-Head SAIL API**，提供 HGGC 运行时 API / HGGC 驱动 API 等原生编程能力。当前版本 **T-Head SAIL v2.1.1**，支持 真武 M890、真武 810E 等全系列硬件产品。

SDK 层包含五大核心模块：

| 模块 | 说明 | 文档 |
|:---|:---|:---|
| **T-Head SAIL 用户驱动** | T-Head SAIL HGGC Driver API | [T-Head SAIL HGGC Driver API →](../ppu_sdk/05_driver_api.md) |
| **T-Head SAIL 运行时** | T-Head SAIL HGGC Runtime API | [T-Head SAIL HGGC Runtime API →](../ppu_sdk/04_runtime_api.md) |
| **编译器** | T-Head SAIL HGCC、HGRTC、hgJitLink、libHGVM、libPPUDevice、Binary Utilities、hgFatbinary、PPU-GDB、HGGC Memcheck、Sanitizer API 等编译器驱动、编译库和编译工具 | [T-Head SAIL HGCC →](../ppu_sdk/10_hgcc.md) |
| **设备运维和管理** | T-Head SAIL PPU-SMI | [T-Head SAIL PPU-SMI →](../ppu_sdk/15_ppu_smi_mps.md) |
| **加速库** | T-Head SAIL acDNN、acBLAS、acFFT、acSOLVER、acRAND、acSPARSE 闭源加速库 | [T-Head SAIL acDNN →](../ppu_sdk/07_acdnn.md) |
| **高性能互联** | PCCL 集合通信、DeepEP 专家并行、sailbandwidth 带宽性能诊断工具 — 支持 ICN/PCIe/RDMA 互联 | 高性能互联文档 |
| **性能分析工具** | Asight Systems / Asight Compute 性能分析工具 | 性能分析工具文档 |

> 详见 [SDK 层](#4-sdk-层) 获取各模块的完整文档与使用指南。

### 1.3 OS 层 — 内核驱动（KMD）

OS 层包含内核驱动（KMD）及操作系统适配。本节重点介绍 KMD 部分，它负责硬件抽象、资源调度与多租户环境下的性能隔离与稳定性：

| 模块 | 说明 | 文档 |
|:---|:---|:---|
| **内核驱动** | 真武 PPU 内核驱动、ECC 错误处理、电源与性能管理 | 内核驱动文档 |
| **虚拟化** | MIG 多实例隔离、vGPU 虚拟化、SR-IOV 与容器化支持 | 虚拟化文档 |
| **操作系统** | Ubuntu、CentOS、AliOS 兼容适配 | [快速开始 →](#3-快速开始) |

> 详见 [KMD 层](#5-kmd-层) 获取各模块的完整文档与使用指南。

### 1.4 文档入门指南导览

| 我想了解... | 请查阅 | 描述 |
|:---|:---|:---|
| 从零开始安装和验证 | [**快速开始**](#3-快速开始) | 驱动安装、SDK 配置、Hello World 运行的端到端指南 |
| AI 框架适配 | [**平头哥 GitHub**](https://github.com/t-head/) | vLLM、SGLang、PyTorch、DeepSpeed 等框架的适配仓库与使用指南 |
| SDK 开发 | [**SDK 层**](#4-sdk-层) | HGGC Runtime API、HGGC Driver API、T-Head SAIL acDNN/acBLAS 等加速库、编译器、高性能互联、性能分析工具 |
| 内核驱动和虚拟化 | [**KMD 层**](#5-kmd-层) | KMD 安装、ECC/XID、MIG/vGPU、ICN 隔离 |
| 生产环境部署方案 | [**部署方式**](#6-部署方式) | 虚拟机、裸金属、Docker 容器的参考架构与步骤 |
| 版本策略和技术支持 | [**支持**](#7-支持) | 生命周期、版本分支、兼容性矩阵、求助渠道 |

根据您的角色推荐入门路径：

1. 如果是**首次接触 PPU**，从[**快速开始**](#3-快速开始)开始，30 分钟完成环境搭建
2. 如果是**应用开发者**，查看 [**SDK 层**](#4-sdk-层)了解框架适配和 SDK API
3. 如果是**系统管理员**，查阅 [**KMD 层**](#5-kmd-层)和[**部署方式**](#6-部署方式)完成集群部署
4. 如果是**运维人员**，参考[**支持**](#7-支持)中的监控工具和健康检查指南

比赛关联：本表即整套手册的"路由图"——比赛涉及的 Runtime/Driver API、acDNN/acBLAS 加速库、性能分析工具分别对应 `ppu_sdk/` 下的各分册，查接口前先在这里定位入口。

## 2. 术语表

以下术语在开发者文档、API 参考与源码中频繁出现，本表提供统一的缩写对照供开发者查阅。

| 缩写 | 全称 |
|:---|:---|
| **HG** | Heterogeneous，the brief of SW API |
| **HGBAT-INFO** | HG Binary Analyze Tool Information |
| **HGBIN** | HG Binary |
| **HGBINS** | Heterogeneous General-purpose Binaries |
| **HGCC** | HG C/C++ Compiler |
| **HGCONTEXT** | HG Context |
| **HGFATBIN** | HG Fatbin |
| **HGGC** | HeteroGeneous General-purpose Computing |
| **HGGCCC** | HGGC C Compiler |
| **HGGCRT** | HGGC Runtime |
| **HGJITLINK** | HG Just-in-Time Link |
| **HGML** | HG Management Library |
| **HGRTC** | HG Runtime Compilation library |
| **HGTX** | HG Tool Extension |
| **HGVM** | HG Virtual Machine |
| **LibPPUDevice** | PPU Device Library |
| **PPU** | Parallel Process Unit |
| **PPU-GDB** | PPU GDB |
| **PPU-SMI** | PPU System Management Interface |
| **PPU001** | Arch Number for Zhenwu 810, Zhenwu 805, Zhenwu 610, Zhenwu 810E, Zhenwu 610E |
| **PPU0015** | Arch Number for Zhenwu M890 |
| **TIX** | T-Head Instruction eXtension |

## 3. 快速开始

> **预计时间**：完整快速开始流程约需 **30-60 分钟**，涵盖驱动与 T-Head SAIL 部署与验证。

### 3.1 前置条件

在开始之前，请确保您的环境满足以下要求：

#### 硬件要求

- 真武 PPU 支持型号：真武 M890、真武 810、真武 810E、真武 805、真武 610、真武 610E
- 标准 RDMA 网卡 / 高性能网卡（EIC），若使用高性能网卡（EIC）请联系阿里云合作方获取相关制品，或者发送邮件至 sail.support@thead.com 咨询。

#### 软件要求

- Linux 操作系统：Ubuntu 20.04 及以上版本、CentOS 7.9/8.2、AliOS 7u2/8u2、Alinux 3、Anolis 8.6
- 内核版本：≥ 5.4（推荐 5.15 LTS）
- GCC 版本：5.5 – 15.0；Clang 版本：9 – 21
- CMake：≥ 3.18

### 3.2 软件制品清单

真武 PPU 软件栈包含以下组件，请从制品库获取对应版本：

| 组件 | 安装包格式 | 说明 |
|---|---|---|
| T-Head SAIL SDK | runfile | 开发工具包（含 HGGC Driver API、 HGGC Runtime API、编译器、加速库、高性能互联、调试与检查工具） |
| 内核驱动 | runfile | 内核模式驱动，需根据操作系统与内核版本选择对应的包 |
| 高性能互联库 | tar.gz | 集合通信库和专家通信库，多卡/多机场景必须 |
| 性能分析工具 | msi / dmg | Asight 分析工具 |
| ICN 超节点配置和管理 | rpm / deb | 多节点显存交换组件和网络组件 |

### 3.3 安装 KMD 内核驱动

KMD 支持 runfile 安装方式, 安装命令如下所示：

```bash
chmod +x ppu-driver-<version>.run
sudo ./ppu-driver-<version>.run
```

安装成功后终端输出 `install succeed`。

验证驱动加载：

```bash
ppu-smi
```

真武 810E 正常输出示例（版本号为示例信息，请以实际制品为准）：

```text
+-------------------------------------------------------------------------------+
| PPU-SMI 1.28          Driver Version: 2.1.2-rd1dcd     HGGC Version: N/A      |
+---------------------------------+----------------------+----------------------+
| PPU  Name        Persistence M. | Bus-Id               | Volatile Uncorr. ECC |
| Fan  Temp  Perf   Pwr:Usage/Cap | Memory-Usage         | PPU-Util  Compute M. |
|                                 |                      |               MIG M. |
+=================================+======================+======================+
| 0  PPU-ZW810E        N/A        | 00000001:C9:00.0     |                    0 |
| N/A  38C   N/A       81W / 400W | 1MiB / 98304MiB      |   0%        Default  |
|                                 |                      |             Disabled |
+---------------------------------+----------------------+----------------------+
| 1  PPU-ZW810E        N/A        | 00000001:C8:00.0     |                    0 |
| N/A  38C   N/A       82W / 400W | 1MiB / 98304MiB      |   0%        Default  |
|                                 |                      |             Disabled |
+---------------------------------+----------------------+----------------------+
| 2  PPU-ZW810E        N/A        | 00000001:80:00.0     |                    0 |
| N/A  43C   N/A       82W / 400W | 1MiB / 98304MiB      |   0%        Default  |
|                                 |                      |             Disabled |
+---------------------------------+----------------------+----------------------+
| 3  PPU-ZW810E        N/A        | 00000001:81:00.0     |                    0 |
| N/A  43C   N/A       80W / 400W | 1MiB / 98304MiB      |   0%        Default  |
|                                 |                      |             Disabled |
+---------------------------------+----------------------+----------------------+
| 4  PPU-ZW810E        N/A        | 00000000:7E:00.0     |                    0 |
| N/A  33C   N/A       79W / 400W | 1MiB / 98304MiB      |   0%        Default  |
|                                 |                      |             Disabled |
+---------------------------------+----------------------+----------------------+
| 5  PPU-ZW810E        N/A        | 00000000:7F:00.0     |                    0 |
| N/A  37C   N/A       81W / 400W | 1MiB / 98304MiB      |   0%        Default  |
|                                 |                      |             Disabled |
+---------------------------------+----------------------+----------------------+
| 6  PPU-ZW810E        N/A        | 00000000:C7:00.0     |                    0 |
| N/A  37C   N/A       80W / 400W | 1MiB / 98304MiB      |   0%        Default  |
|                                 |                      |             Disabled |
+---------------------------------+----------------------+----------------------+
| 7  PPU-ZW810E        N/A        | 00000000:C6:00.0     |                    0 |
| N/A  35C   N/A       80W / 400W | 1MiB / 98304MiB      |   0%        Default  |
|                                 |                      |             Disabled |
+---------------------------------+----------------------+----------------------+
| 8  PPU-ZW810E        N/A        | 00000001:A5:00.0     |                    0 |
| N/A  28C   N/A       80W / 400W | 1MiB / 98304MiB      |   0%        Default  |
|                                 |                      |             Disabled |
+---------------------------------+----------------------+----------------------+
| 9  PPU-ZW810E        N/A        | 00000001:A4:00.0     |                    0 |
| N/A  33C   N/A       81W / 400W | 1MiB / 98304MiB      |   0%        Default  |
|                                 |                      |             Disabled |
+---------------------------------+----------------------+----------------------+
| 10  PPU-ZW810E        N/A       | 00000001:0A:00.0     |                    0 |
| N/A  27C   N/A       81W / 400W | 1MiB / 98304MiB      |   0%        Default  |
|                                 |                      |             Disabled |
+---------------------------------+----------------------+----------------------+
| 11  PPU-ZW810E        N/A       | 00000001:0B:00.0     |                    0 |
| N/A  26C   N/A       79W / 400W | 1MiB / 98304MiB      |   0%        Default  |
|                                 |                      |             Disabled |
+---------------------------------+----------------------+----------------------+
| 12  PPU-ZW810E        N/A       | 00000000:08:00.0     |                    0 |
| N/A  27C   N/A       79W / 400W | 1MiB / 98304MiB      |   0%        Default  |
|                                 |                      |             Disabled |
+---------------------------------+----------------------+----------------------+
| 13  PPU-ZW810E        N/A       | 00000000:09:00.0     |                    0 |
| N/A  28C   N/A       79W / 400W | 1MiB / 98304MiB      |   0%        Default  |
|                                 |                      |             Disabled |
+---------------------------------+----------------------+----------------------+
| 14  PPU-ZW810E        N/A       | 00000000:A3:00.0     |                    0 |
| N/A  29C   N/A       79W / 400W | 1MiB / 98304MiB      |   0%        Default  |
|                                 |                      |             Disabled |
+---------------------------------+----------------------+----------------------+
| 15  PPU-ZW810E        N/A       | 00000000:A2:00.0     |                    0 |
| N/A  28C   N/A       80W / 400W | 1MiB / 98304MiB      |   0%        Default  |
|                                 |                      |             Disabled |
+---------------------------------+----------------------+----------------------+

+-------------------------------------------------------------------------------+
| Processes:                                                                    |
| PPU    GI   CI   PID      Type  Process name                       PPU Memory |
|        ID   ID                                                     Usage      |
+===============================================================================+
| No running processes found                                                    |
+-------------------------------------------------------------------------------+
```

### 3.4 安装 T-Head SAIL SDK

T-Head SAIL SDK 以 runfile 包形式发布，支持通过命令行参数自定义安装：

```bash
chmod +x ppu_<hggcrt>_<os>-<version>.run

# 静默安装（默认路径 /usr/local/PPU_SDK）
sudo ./ppu_<hggcrt>_<os>-<version>.run --silent

# 或指定安装路径
sudo ./ppu_<hggcrt>_<os>-<version>.run --silent --prefix=/opt/ppu

# 配置环境变量, 以默认路径为例
source /usr/local/PPU_SDK/envsetup.sh
```

常用安装参数：

| 参数 | 说明 |
|---|---|
| `--silent` | 静默安装，自动跳过交互提示，隐含接受 EULA |
| `--prefix=<PATH>` | 指定安装根目录，默认 `/usr/local/PPU_SDK` |
| `--tmpdir <PATH>` | 指定临时文件目录，当 `/tmp` 挂载为 noexec 时需手动指定 |
| `--help` | 查看完整参数列表 |

### 3.5 安装高性能互联库（可选）

> **说明**：当前版本 **T-Head SAIL SDK** 已内置高性能互联库，无需重复安装。本节仅面向需要独立构建或自定义集成 PCCL 的开发者，作为参考。PCCL 运行依赖完整的 T-Head SAIL SDK 环境（包括驱动、运行时库等），因此使用 PCCL 独立制品包时，必须先安装并配置好 T-Head SAIL SDK。

PCCL 高性能互联库支持单机 ICN/PCIe/ShareMemory 及多机 RDMA/Socket/ICN 通信：

```bash
tar -xzf pccl_<hggcrt>_<os>-<version>.tar.gz
cd pccl
source envsetup.sh
```

### 3.6 验证安装

#### 步骤 1：检查设备状态

```bash
ppu-smi
```

确认 `Driver Version` 和设备信息正确显示。

#### 步骤 2：验证 SDK

```bash
hgcc --version
```

#### 步骤 3：验证多卡通信

从指定位置获取 `comm_tools` 后执行单进程 8 卡测试和多进程 16 卡测试。

```bash
# 单进程 8 卡测试
all_reduce_perf -t 1 -g 8 -d float -b 8 -e 2GB -f 2 -n 20 -w 5
# 多进程 16 卡测试
mpirun -np 16 -npernode 8 all_reduce_perf -t 1 -g 1 -d float -b 8 -e 2GB -f 2 -n 20 -w 5
```

### 3.7 常见安装问题

| 问题 | 原因 | 解决方案 |
|---|---|---|
| Module alixpu is in use | PPU 设备被进程占用 | `sudo lsof /dev/alixpu` 查找占用进程并 kill，再 `sudo ppudbg --reset` 后重试 |
| Failed to open /dev/alixpu | 驱动未加载 | 手动加载：`insmod alipci.ko && insmod alixpu.ko` |
| PPU 设备被 vfio-pci 占用 | 容器运行时占用 | 清除 driver_override：`echo "" > /sys/bus/pci/devices/<id>/driver_override` |
| 重启后驱动版本回退 | 旧版 alixpu 打包在 initramfs 中 | 卸载旧驱动 → `depmod` → `dracut -f` → 重启 → 重新安装 |

> 更多 KMD 安装指南与故障排查内容见内核驱动文档的对应章节。

### 3.8 下一步

安装完成后，推荐按以下路径继续：

1. **学习 HGGC 编程模型** — 阅读 [T-Head SAIL HGGC 编程指南](../ppu_hggc/00_index.md)
2. **了解加速库 API** — 查阅 acDNN / acBLAS / acFFT 等库的 [T-Head SAIL acBLAS](../ppu_sdk/08_acblas.md)
3. **配置多卡多机训练** — 参阅高性能互联文档中的 PCCL 用户指南和 DeepEP 用户指南
4. **性能调优** — 使用 Asight Systems / Asight Compute 进行性能分析
5. **生产部署** — 参阅 [部署方式](#6-部署方式) 选择合适的部署架构

比赛关联：比赛服务器到手后先用 `ppu-smi` 确认卡数、显存容量（810E 单卡 98304MiB）与驱动版本，这是后续显存预算（权重 + KV cache）和压测取证的基础；`all_reduce_perf` 可作为多卡通信基准。

## 4. SDK 层

T-Head SAIL SDK 是平头哥面向真武 PPU 打造的全栈 AI 软件开发工具包，提供将底层算力转化为上层应用的标准化开发能力，当前版本 **v2.1.1**。其核心能力包括：

SDK 在编程模型上同时提供 HGGC Driver API（细粒度上下文与资源控制）与 HGGC Runtime API（高层封装、易用化的运行时接口）两套原生 API，支持二者混合调用；在工具链上集成基于 clang/LLVM 的异构编译器（HGCC / Clang / HGRTC）、TIX 跨代抽象指令集，以及 hgobjdump/hgbat/hgprune 等二进制工具，覆盖 AOT 与 JIT 两条编译路径，并支持 Triton（V2.3 以上） 与 tilelang 等主流 DSL。

在算子与生态层面，SDK 提供 acDNN、acBLAS、acFFT、acSOLVER、acRAND、acSPARSE 等高性能计算加速库，并适配了 FlashMLA、Flash-Attention、DeepGemm、Xformers、FasterTransformer 等开源加速组件；通信层面提供 PCCL 集合通信库、DeepEP 专家并行通信库与 sailbandwidth P2P 带宽测试工具，支持 ICN/PCIe/RDMA 多种互联方式；同时配套 Asight Systems/Compute、PPU-SMI、PPU-DCGM、HGGC-GDB、Compute Sanitizer 等性能分析、设备管理与调试工具，帮助开发者在真武 PPU 上高效完成训练、推理与部署全流程开发。

<img src="https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125009803/d9ad2e5be3769af745a6ecd3ab6a6e58/SAIL-sdk-stack.png" alt="T-Head SAIL SDK 模块框图" style="display: block; width: min(100%, 532px); height: auto; margin: 0 auto;" />

### 4.1 T-Head SAIL 用户驱动

T-Head SAIL 用户驱动模块提供对 PPU 设备的细粒度控制，所有入口函数以 `hg` 作为前缀。适用于需要显式管理上下文、模块加载、虚拟内存映射等高级场景：

| 模块 | 说明 |
|:---|:---|
| **基础与初始化** | 驱动初始化、数据类型、版本查询、错误处理、入口点访问 |
| **设备与上下文** | 设备查询、上下文创建/销毁/切换、P2P 内存互访 |
| **模块与代码加载** | 加载模块/库、获取函数/全局变量、链接 |
| **内存管理** | 分配/释放、memcpy/memset、虚拟内存管理、内存池 |
| **流与事件** | 事件创建/同步、流创建/同步/捕获、流内 wait/write 操作 |
| **执行与调度** | 核函数启动、函数属性、占用率查询、图构建/实例化/启动 |
| **图像资源** | 纹理对象创建/查询 |
| **性能分析** | 性能分析控制 |

> 详见 [T-Head SAIL HGGC Driver API →](../ppu_sdk/05_driver_api.md)

### 4.2 T-Head SAIL HGGC 运行时（Runtime）

T-Head SAIL 运行时模块提供了可用于静态与动态链接的独立函数库，所有入口函数以 `hggc` 作为前缀。它对驱动 API 进行概念封装与简化，支持与驱动 API 混合调用：

| 模块 | 说明 |
|:---|:---|
| **基础与初始化** | 数据类型、版本查询、错误处理、驱动入口点访问 |
| **设备管理** | 设备查询、属性配置、异步通知、P2P 内存互访 |
| **模块管理** | 获取函数句柄、符号地址/大小查询 |
| **内存管理** | 分配/释放、memcpy/memset、内存池管理 |
| **流与事件** | 事件创建/同步、流创建/同步/捕获 |
| **执行与调度** | 核函数启动、函数属性、占用率查询、图构建/实例化/启动 |
| **互操作与扩展** | 外部内存/信号量导入导出 |
| **性能分析** | 性能分析控制 |

> 详见 [T-Head SAIL HGGC Runtime API →](../ppu_sdk/04_runtime_api.md)

### 4.3 编译器

T-Head SAIL SDK 提供完整的编译工具链，覆盖从源码编写、离线编译、运行时编译与链接，到二进制分析、调试和正确性检查的全流程。工具链基于 clang/LLVM 构建，兼容 HGGC C/C++ 编程规范，支持 Triton（V2.3 以上） 和 tilelang。

#### 组件一览

| 组件 | 说明 |
|:---|:---|
| **T-Head SAIL HGCC** | HGGC 编译驱动统一入口，负责宿主代码与设备代码拆分、编译与链接编排 |
| **T-Head SAIL Clang** | 异构编译器驱动，支持 .hg 混合源、分离编译与链接优化 |
| **T-Head SAIL TIX** | 跨代 PPU 抽象指令扩展，支持在 C/C++ 中以内联汇编方式调用底层能力 |
| **T-Head SAIL HGRTC + libHGVM + hgJitLink** | 运行时编译与链接链路：IR 编译、设备代码生成、JIT 链接与优化 |
| **T-Head SAIL hgfatbinary** | 多架构产物打包工具，支持按目标硬件在运行时自动选择匹配二进制 |
| **T-Head SAIL 二进制工具** | hgobjdump、hgbat、hgprune：反汇编、控制流分析、寄存器生命周期分析与产物裁剪 |
| **T-Head SAIL 调试与检查工具** | PPU-GDB、HGGC Memcheck、Sanitizer API：联合调试、越界与同步检查、自定义检查扩展 |
| **T-Head SAIL libDevice** | 设备端运行时基础库，提供原子、同步、异步拷贝等底层接口支撑 |

#### 编程基础与编译驱动

HGGC 编程指南用于建立异构编程基础，包括线程块与网格执行模型、内存层次和常见编译流程。实际工程中，推荐通过 HGCC 作为统一入口完成多阶段编译任务：它会自动处理宿主/设备代码拆分、目标架构选择和链接编排，减少手工拼接命令带来的复杂度。对于需要更细粒度硬件控制的场景，可结合 TIX 在关键路径中插入抽象底层指令。

#### 运行时编译、链接与多架构部署

当业务需要动态生成或按场景加载设备代码时，可使用 HGRTC 在运行时完成编译，再通过 libHGVM 生成可执行设备二进制，并借助 hgJitLink 进行链接与优化。对于同一应用覆盖多代真武 PPU 的部署场景，推荐使用 hgfatbinary 预打包多架构产物，由驱动在运行时自动选择最优目标代码，以平衡兼容性与维护成本。

#### 二进制分析与调试校验

在性能调优阶段，可使用 hgobjdump、hgbat、hgprune 对设备二进制做可读化分析与裁剪，定位控制流、寄存器压力和冗余代码路径。在正确性阶段，PPU-GDB 支持 CPU/PPU 联合调试；HGGC Memcheck 提供 memcheck、initcheck、synccheck、racecheck 四类检查能力；Sanitizer API 支持构建面向特定场景的自定义检测逻辑，适合做自动化回归与质量门禁。

#### 设备端运行时支持

LibPPUDevice 以 LLVM 字节码形式提供设备端基础函数集合，是编译链接过程中的关键运行时依赖。该库覆盖原子操作、同步原语、异步拷贝等常用能力，为上层 Kernel 与算子提供稳定的一致性支撑。

> 详见 [SDK 文档 编程指南 →](../ppu_hggc/00_index.md) 、 [HGCC 手册 →](../ppu_sdk/10_hgcc.md) 和 [二进制工具手册 →](../ppu_sdk/12_binary_utilities.md)

### 4.4 性能分析工具

性能分析工具包含 Asight Systems 和 Asight Compute 两款工具。

**T-Head SAIL Asight Systems** 是一款用于 PPU 程序性能分析的工具套件，能够跟踪 CPU 和 PPU 上的各种运行事件，并通过时间线（Timeline）方式进行可视化展示，帮助开发者进行系统级性能分析并定位瓶颈。Asight Systems 由两部分组成：

- **asys 命令行工具**：运行在 Linux 上的 Target 端采集器，支持 HGGC、HGTX、OSRT、PCCL、acDNN/acBLAS 等事件类型，提供灵活的采集起止控制。
- **T-Head SAIL Asight Systems GUI**：运行在 Windows / Mac 上的 Host 端分析工具，提供 Timeline View、Events View、Function Table 等多种视图，高效展示大规模事件数据。

**T-Head SAIL Asight Compute** 是一款用于 PPU 程序 Kernel 性能分析的工具套件，在 Kernel 执行期间采集硬件性能指标（Metrics）并进行可视化，帮助开发者优化 Kernel 性能。Asight Compute 同样由命令行与 GUI 两部分组成：

- **acu 命令行工具**：在 Target 端对应用进行 profiling，输出 `.acurep` 报告，覆盖计算/内存负载、Warp 调度与指令 Stall、ICN 链路等多类指标，支持 Application / Kernel / Range Replay 与 Warp Sampling。
- **T-Head SAIL Asight Compute GUI**：在 Host 端打开报告，提供 Roofline Chart、Bar Chart、Memory Table 等视图，并支持 Baseline 对比分析。

比赛关联：TTFT 与吞吐量两个评分项的取证都靠这套工具——asys 的 Timeline 定位 prefill/decode 各阶段耗时，acu 的 Metrics（内存负载、指令 Stall）定位 kernel 瓶颈，报告中可附 Roofline 与 Baseline 对比作为系统级优化深度的证据。

### 4.5 计算加速库

T-Head SAIL SDK 提供一组高性能计算加速库，覆盖深度学习、线性代数、信号处理、稀疏计算、随机数生成等场景。所有库均基于 HGGC Runtime 构建，面向真武 PPU 架构深度优化，支持 Stream 异步执行与多真武 PPU 协同。

#### 库一览

| 库 | 头文件 | 定位 |
|:---|:---|:---|
| **T-Head SAIL acDNN** | `acdnn.h` | 深度神经网络算子库 |
| **T-Head SAIL acBLAS** | `acblas.h` / `acblasLt.h` | 基础线性代数库（BLAS） |
| **T-Head SAIL acFFT** | `acfft.h` / `acfftXt.h` | 快速傅里叶变换库 |
| **T-Head SAIL acSOLVER** | `acsolverDn.h` | 稠密矩阵求解库（LAPACK） |
| **T-Head SAIL acRAND** | `acrand.h` / `acrand_kernel.h` | 随机数生成库 |
| **T-Head SAIL acSPARSE** | `acsparse.h` | 稀疏矩阵运算库 |

#### 各库能力概述

##### T-Head SAIL acDNN — 深度神经网络算子库

面向推理与训练的全场景算子库，按功能域划分为 ops / cnn / adv 三个子库。

| 算子族 | 覆盖范围 |
|:---|:---|
| 卷积与池化 | Conv（多种前向/反向算法）、Max/Avg/Adaptive Pooling、Conv+Bias+Activation 融合 |
| 归一化与激活 | BatchNorm、LRN、Softmax、Dropout、逐点运算（add/mul/sqrt 等）、张量归约 |
| 序列模型 | RNN / LSTM / GRU（单双向、多层堆叠） |
| 注意力机制 | Multi-Head Attention |
| 损失函数 | CTC Loss |
| 高级特性 | Graph API（声明式算子图描述与融合执行）、Backend 描述符体系（运行时自动选择最优 engine）、Tensor Cell / TF32 / 稀疏 Tensor Op |

支持数据类型：FP64 / FP32 / FP16 / BF16 / TF32 / INT8 / INT16 / INT32 / UINT8 / BOOL。

> 详见 [T-Head SAIL acDNN →](../ppu_sdk/07_acdnn.md)

##### T-Head SAIL acBLAS — 基础线性代数库

完整覆盖标准 BLAS 规范，并提供面向真武 PPU 深度调优的扩展接口。

| 运算层级 | 覆盖范围 |
|:---|:---|
| Level-1 | 向量运算：amax、amin、asum、axpy、copy、dot、nrm2、rot、scal、swap 等 |
| Level-2 | 矩阵-向量运算：gemv、ger、spr 等 |
| Level-3 | 矩阵-矩阵运算：gemm（含 Hgemm 半精度）、symm、trsm 等 |
| BLAS 扩展 | 混合精度 GEMM（GemmEx / GemmBatchedEx / GemmStridedBatchedEx）、批处理线性方程组（LU / 三角求解 / 求逆 / QR / 最小二乘）、扩展 Level-1（Nrm2Ex / AxpyEx / DotEx 等） |
| acblasLt | 轻量级 GEMM 专用接口，采用描述符-plan 模式做精细调优，支持 Epilogue 融合 |

支持数据类型：FP64 / FP32 / FP16 / BF16 / FP8（E4M3 / E5M2）/ INT8 / INT32 / Complex。

> 详见 [T-Head SAIL acBLAS →](../ppu_sdk/08_acblas.md)

##### T-Head SAIL acFFT — 快速傅里叶变换库

采用「先规划（plan）、再执行（execute）」的两阶段模型，内置 radix-2/3/5/7 优化路径。

| 维度 | 变换类型 |
|:---|:---|
| 1D / 2D / 3D | R2C / C2R / C2C（单精度），D2Z / Z2D / Z2Z（双精度） |

支持批处理（batch）、in-place / out-of-place 两种执行模式、高级数据布局（stride / embed / dist）、多真武 PPU 协同（Xt API，最多 16 个）、半精度（FP16）与 BFloat16 变换（维度须为 2 的幂）、64 位索引（总元素数可超 4G）。相同参数与硬件条件下输出逐位可复现。

##### T-Head SAIL acSOLVER — 稠密矩阵求解库

面向稠密线性代数的 LAPACK 风格求解库，覆盖六大分解族。

| 分解族 | 覆盖范围 |
|:---|:---|
| Cholesky | potrf（分解）/ potrs（求解）/ potri（求逆） |
| LU | getrf（分解）/ getrs（求解） |
| QR | geqrf（分解）/ orgqr（生成 Q）/ ormqr（乘 Q） |
| SVD | gesvd / gesvdj（Jacobi）/ gesvdaStridedBatched |
| 对称特征值 | syevd（Divide-and-Conquer）/ syevj / syevjBatched（Jacobi） |
| 矩阵约简 | gebrd（双对角化）/ sytrd（三对角化）/ orgbr / orgtr / ormtr |

支持 64 位扩展 API（X-API）与 Batched 接口。数据类型：FP32 / FP64。

##### T-Head SAIL acRAND — 随机数生成库

提供主机端批量生成与设备端内核内即时生成两条路径。

| 生成器类别 | 算法 |
|:---|:---|
| 伪随机（PRNG） | XORWOW（默认）、MRG32k3a、MTGP32、MT19937、Philox_4x32_10 |
| 拟随机（QRNG） | Sobol' 32-bit / 64-bit、Scrambled Sobol' 32-bit / 64-bit |

支持分布：Uniform / Normal / LogNormal / Poisson。设备 API 支持与算子内核融合（Dropout / Noise Injection / Monte Carlo），拟随机序列支持最多 20000 维。

##### T-Head SAIL acSPARSE — 稀疏矩阵运算库

同时提供 Legacy（逐函数调用）与 Generic（基于描述符）两套 API 体系。

| 算子族 | 覆盖范围 |
|:---|:---|
| 稀疏-稠密运算 | SpMV（稀疏矩阵×稠密向量）、SpMM（稀疏矩阵×稠密矩阵） |
| 稀疏-稀疏运算 | SpGEMM（稀疏矩阵×稀疏矩阵） |
| 三角求解 | SpSV（稀疏三角向量求解）、SpSM（稀疏三角矩阵求解） |
| 不完全分解预条件 | IC0（csric02 / bsric02）、ILU0（csrilu02 / bsrilu02） |
| 三对角 / 五对角求解 | gtsv2 系列（含批量与 interleaved 变体） |
| 格式转换与排序 | CSR / CSC / COO / Dense / BSR 互转、行/列索引排序 |

支持存储格式：CSR（首选）、CSC、COO、BSR、Sliced ELL、Blocked-ELL、稀疏向量。Generic API 支持混合精度与算法选型。

> 详见 [T-Head SAIL acSPARSE →](../ppu_sdk/09_acsparse.md)

#### 开源加速生态

除上述闭源库外，T-Head SAIL SDK 同时适配以下开源加速组件：FlashMLA、Flash-Attention、DeepGemm、Xformers、FasterTransformer 等。

> 详见 [平头哥 GitHub 主页 →](https://github.com/t-head/)

比赛关联：VLM 推理的 GEMM 路径直接落在 acBLAS（含 FP8 E4M3/E5M2 与 INT8 混合精度 GemmEx、acblasLt Epilogue 融合）上，这是量化（INT8/FP8）与吞吐优化最可能用到的库；acDNN 的 Multi-Head Attention 与 Graph API 对应注意力融合与算子图优化。

### 4.6 高性能互联

真武 PPU 高性能互联包含集合通信库、专家并行通信库与 P2P 带宽测试工具：

| 库 | 说明 |
|:---|:---|
| **PCCL** | 集合通信库 — 支持 AllReduce、AllGather、ReduceScatter、Broadcast、Send/Recv 等多种通信原语；支持单机 ICN/PCIe/SHM 及多机 RDMA/Socket/ICN 通信方式 |
| **DeepEP** | 专家并行通信库 — 支持 IntraNode/InterNode/LowLatency 三种 Kernel；支持 INT8/FP8/MXFP4 量化；支持 HGGC Graph 与 TBO & SBO（two-batch overlap & single-batch overlap） |
| **sailbandwidth** | P2P 带宽测试工具 — 支持 H2D/D2H/D2D/H2ALL/ALL2H 等多场景带宽性能评测 |

> 详见高性能互联文档。

## 5. KMD 层

### 5.1 KMD 内核驱动

KMD (Kernel Mode Driver) 是真武 PPU 的内核驱动模块，负责硬件初始化、显存管理、任务调度与用户态接口提供，提供 runfile 源码编译安装方式（相关制品正在准备中，将于近期开放下载，敬请期待）。

### 5.2 KMD 安装指南

KMD 支持 runfile 安装方式。详细步骤见内核驱动安装指南。

| 功能 | 说明 |
|:---|:---|
| **硬件初始化** | PCI 设备枚举、ICN 拓扑发现与建立 |
| **显存管理** | HBM 显存分配/回收、Page Migration、Peer Memory 支持 |
| **任务调度** | Compute / DMA / Video 引擎的任务提交与上下文切换 |
| **错误处理** | XID 错误上报、ECC 检测与修复、Page Retirement |

#### 常见安装问题

| 问题 | 解决方案 |
|:---|:---|
| 设备占用导致安装失败 | `sudo lsof /dev/alixpu` 查找并杀掉占用进程，再执行 `sudo ppu-smi -r` |
| 内核版本不匹配 | 改用 runfile 包本地编译安装 |
| Failed to create /dev/alixpu | 手动 `insmod alipci.ko && insmod alixpu.ko` |
| vfio-pci 占用设备 | 清除 driver_override：`echo "" > /sys/bus/pci/devices/.../driver_override` |
| 重启后驱动版本回退 | 卸载旧驱动 → `depmod` → `dracut -f` → 重启 → 重装 |

> 更多内容见内核驱动故障排查章节。

### 5.3 ECC 错误处理

真武 PPU HBM 支持 ECC 校验：CECC（1-bit 可纠正）硬件自动修正；UECC（2-bit 不可纠正）驱动屏蔽出错 Page，退出进程后可重新拉起。

### 5.4 XID 错误代码

XID 消息是 真武 PPU 驱动上报的错误事件，用于帮助系统管理员、开发人员和运维分析和定位 PPU 相关问题。完整错误代码列表见内核驱动文档的 XID 错误代码章节。

## 6. 部署方式

真武 PPU 支持三种部署形态：**裸金属**、**容器** 和 **虚拟机**。每种形态可结合 MIG、vGPU、Passthrough 等切分/共享策略，从单机独占到多租户精细分配的全场景均可覆盖。

### 6.1 选型概览

| 部署形态 | 隔离粒度 | 性能开销 | 可选切分策略 | 典型场景 |
|:---|:---|:---|:---|:---|
| **裸金属** | 主机级 | 无 | MIG | 训练集群、单租户、最大性能要求 |
| **容器** | 容器级 | 极低 | 整卡 / MIG | 多租户容器化、K8s 调度 |
| **虚拟机** | VM 级 | 低 | Passthrough（整卡）/ vGPU（SR-IOV、mdev） | 公有云、VM 级强隔离、跨租户安全 |

切分策略说明：

- **MIG (Multi-Instance GPU)** — 硬件级空间分片，算力与显存物理隔离，支持故障隔离与单独复位；单卡最多 2 GI（GPU Instance）。目前仅 810/805/810e/610/610e 支持 MIG 功能。
- **Passthrough** — 整张 PCI 卡直通给单个 VM，无虚拟化损耗，VM 独占。
- **vGPU** — 单张 PF 拆分为多个 VF/mdev 实例分配给多个 VM。810/805/810e/610/610e 基于 SR-IOV，M890 基于 Linux vfio/mdev。

> 切分策略原理与配置详见虚拟化文档。

### 6.2 共性前置条件

| 项目 | 要求 | 适用场景 |
|:---|:---|:---|
| **BIOS** | 启用 VT-x / AMD-V | 容器、虚拟机 |
| **内核参数** | `intel_iommu=on iommu=pt`（或 `iommu=nopt`） | 虚拟机、vGPU |
| **KMD 驱动** | 与内核版本匹配的 rpm/deb 或 runfile | 全部 |
| **虚拟化栈** | QEMU ≥ 2.9，virsh ≥ 2.0 | 虚拟机 |
| **T-Head SAIL SDK** | T-Head SAIL SDK v2.1.1 及以上 | 全部 |

> 驱动安装详见内核驱动安装指南。

### 6.3 裸金属部署

App 与 KMD 驱动直接运行在物理主机上，无虚拟化开销，是性能最佳的部署形态。

#### 适用场景

- 最大性能要求，无虚拟化损耗
- 单机多卡训练（最多 16x PPU）
- 超算中心、AI 训练集群

#### 部署架构

```text
+--------------------------------------------+
|              Linux Host OS                 |
|  +-------------------------------------+   |
|  |  App + T-Head + PCCL + Frameworks   |   |
|  +-------------------------------------+   |
|                    |                       |
|  +-------------------------------------+   |
|  |              KMD Driver             |   |
|  +-------------------------------------+   |
|          |      |      |      |            |
|     +----v------v------v------v----+       |
|     |  PPU 0  PPU 1  PPU 2  PPU 3  |       |
|     |  PPU 4  PPU 5  PPU 6  PPU 7  |       |
|     +-------------------------------+      |
+--------------------------------------------+
```

#### 部署步骤

1. 安装 KMD 内核驱动
2. 安装 T-Head SAIL 与高性能互联库（PCCL / DeepEP）
3. 配置 ICN 互联（多机场景）
4. 安装 AI 框架（PyTorch、vLLM 等）
5. 运行基准测试验证性能

#### 同主机多任务分时共享

若需在同一主机上让多个进程独立使用同一张卡的不同算力分片，可启用 **MIG** 将一张物理卡划分为最多 2 个 GI，每个 GI 拥有独立的算力、显存与故障域，互不干扰。

> 详见虚拟化文档中的 MIG 使用指南。

### 6.4 容器部署

真武 PPU 容器部署通过 **设备节点挂载** 实现容器级隔离，无需专用运行时。

#### 适用场景

- 多租户环境下的 PPU 资源隔离
- K8s + device-plugin 自动化调度
- MIG 实例级精细分配

#### 部署架构

```text
+--------------------------------------------+
|              Linux Host OS                 |
|  +----------+ +----------+ +----------+    |
|  | Container| | Container| | Container|    |
|  |  + App   | |  + App   | |  + App   |    |
|  |  + SDK   | |  + SDK   | |  + SDK   |    |
|  +-----+----+ +-----+----+ +-----+----+    |
|        | dev mount  | dev mount  |         |
|  +-------------------------------------+   |
|  |              KMD Driver             |   |
|  +-------------------------------------+   |
|          |             |          |        |
|     +----v----+   +----v----+   +-v---+    |
|     |  PPU 0  |   |  PPU 1  |   | ... |    |
|     +---------+   +---------+   +-----+    |
+--------------------------------------------+
```

#### 整卡挂载

```bash
docker run --rm -it \
    --device /dev/alixpu_ppu0 \
    --device /dev/alixpu \
    --device /dev/alixpu_ctl \
    ppu/sdk:2.1 bash
```

容器中执行 `ppu-smi` 只能看到挂载的 PPU0，实现卡级隔离。

#### MIG 实例挂载

启用 MIG 后，每个 GI / CI 都有独立的 cap 设备节点（`/dev/alixpu-caps/alixpu-capxxx`），可单独挂载到容器实现硬件级隔离：

```bash
docker run --rm -it \
    --device /dev/alixpu_ppu0 \
    --device /dev/alixpu-caps/alixpu-cap256 \
    --device /dev/alixpu-caps/alixpu-cap257 \
    --device /dev/alixpu \
    --device /dev/alixpu_ctl \
    ppu/sdk:2.1 bash
```

cap 节点的 minor id 可从 `/proc/driver/alixpu/capabilities` 目录查询。

> 详见虚拟化文档中的容器隔离使用指南。

### 6.5 虚拟机部署

虚拟机部署支持两种模式：**PCI Passthrough**（整卡直通）和 **vGPU**（单卡多 VM）。

#### PCI Passthrough（整卡直通）

将整张 PPU 卡直通到虚拟机内使用，VM 独占 GPU 资源，无虚拟化性能损耗。

**适用场景：**

- 公有云环境
- VM 级别强隔离
- GPU 按卡粒度分配

**部署架构：**

```text
+------------------+     +------------------+
|   VM 1 (PT)      |     |   VM 2 (PT)      |
|  App + PPU SDK   |     |  App + PPU SDK   |
|  + KMD Driver    |     |  + KMD Driver    |
+--------+---------+     +--------+---------+
         |                        |
+--------v------------------------v---------+
|              Hypervisor (KVM)             |
|  +-------------------------------------+  |
|  |       IOMMU + PCI Passthrough       |  |
|  +-------------------------------------+  |
|              |                |           |
|         +----v---+       +----v---+       |
|         | PPU 0  |       |  PPU 1 |       |
|         +--------+       +--------+       |
+-------------------------------------------+
```

> **多卡直连 Passthrough：ICN 隔离** — 多张 ICN 直连的卡分别 Passthrough 到不同 VM 时，需通过 `ppucli --iso` 断开跨 VM 的 ICN 链路，避免不同 VM 间内核驱动初始化冲突与跨租户安全风险。详见虚拟化文档中的 ICN 隔离指南。

#### vGPU（单卡多 VM）

将单张 PF 拆分为多个 vGPU 实例分配给不同 VM 使用，支持算力与显存的灵活配比。不同芯片的实现方式不同：

| 芯片 | 实现方式 | 管理工具 | 文档 |
|:---|:---|:---|:---|
| **PPU001** | SR-IOV（PF/VF 模型） | `ppu-smi vgpu` | vGPU + SR-IOV 用户指南 (PPU001) |
| **PPU0015** | vfio/mdev（内核 6.8） | `/sys/class/mdev_bus/` | vGPU 虚拟化用户指南 (PPU0015) |

**适用场景：**

- 多租户共享单卡
- 推理服务弹性切片
- 显存与算力按需分配

**部署架构：**

```text
+--------+ +--------+ +--------+ +--------+
|  VM 1  | |  VM 2  | |  VM 3  | |  VM 4  |
| + vGPU | | + vGPU | | + vGPU | | + vGPU |
+----+---+ +----+---+ +----+---+ +----+---+
     |          |          |          |
+----v----------v----------v----------v----+
|        Hypervisor (KVM) + IOMMU          |
|  +-------------------------------------+ |
|  |     SR-IOV (PF/VF) | vfio/mdev      | |
|  +-------------------------------------+ |
|       |     |     |     |     |          |
|  +----v-----v-----v-----v-----v----+     |
|  | VF0  VF1  VF2  VF3  VF4 ... PF  |     |
|  |              PPU 0              |     |
|  +---------------------------------+     |
+------------------------------------------+
```

> **互斥约束**：
> - 整卡 Passthrough 与 vGPU (SR-IOV / mdev) 互斥，不可同时启用
> - 开启 vGPU 模式后，PF 上不允许运行计算任务，请在对应 VM 内运行计算
> - 关闭 vGPU 模式前，需先销毁该卡上所有已创建的 vGPU 实例

> 完整的虚拟机准备、xml 配置与驱动加载流程详见虚拟化使用指南。

比赛关联：本赛道固定单卡、单样本且不启用 batch。本节用于确认目标 810E 是否被 MIG/vGPU 切分、容器是否只暴露一个正确设备，以及 `/dev/alixpu*` 设备节点是否完整挂载；KV/Mamba cache 和 workspace 预算必须以实际可见的单卡显存为准。

## 7. 支持

### 7.1 获取帮助

如果在使用过程中遇到问题，可以通过以下渠道获取支持：

- **技术文档**：各模块详细文档
- **问题排查**：各模块文档中的"问题排查/常见问题"章节
- **社区论坛**：平头哥开发者社区论坛后续版本即将上线
- **技术支持**：sail.support@thead.com

> **文档版本**：各模块文档的详细版本信息请参见对应模块文档的 Release Notes。

## 8. T-Head SAIL HGGC Driver API 文档结构

以下为 [T-Head SAIL HGGC Driver API](../ppu_sdk/05_driver_api.md) 的完整章节结构，供查阅 API 时定位：

- [概念与约束](../ppu_sdk/05_driver_api.md)
    - [驱动 API 与运行时 API 的区别](../ppu_sdk/05_driver_api.md) — 两套 API 的定位、适用场景与选型建议
    - [API 同步行为](../ppu_sdk/05_driver_api.md) — 各 API 的阻塞/非阻塞语义
    - [流同步行为](../ppu_sdk/05_driver_api.md) — 流内操作的排序与同步保证
    - [图对象线程安全](../ppu_sdk/05_driver_api.md) — 图创建/实例化/启动的线程安全规则
    - [版本混用规则](../ppu_sdk/05_driver_api.md) — 不同版本驱动与工具链的兼容约束
- [基础与初始化](../ppu_sdk/05_driver_api.md)
    - [HGGC 驱动程序使用的数据类型](../ppu_sdk/05_driver_api.md) — 枚举、结构体、类型别名
    - [全局控制](../ppu_sdk/05_driver_api.md) — 驱动初始化
    - [实用工具](../ppu_sdk/05_driver_api.md) — 版本查询、错误处理、入口点访问
- [设备与上下文](../ppu_sdk/05_driver_api.md)
    - [设备管理](../ppu_sdk/05_driver_api.md) — 设备查询、主上下文
    - [上下文管理](../ppu_sdk/05_driver_api.md) — 创建/销毁/切换上下文
    - [对等上下文内存访问](../ppu_sdk/05_driver_api.md) — 对等设备内存互访
- [模块与代码加载](../ppu_sdk/05_driver_api.md)
    - [模块管理](../ppu_sdk/05_driver_api.md) — 加载模块/库、获取函数/全局变量、链接
- [内存管理](../ppu_sdk/05_driver_api.md)
    - [内存管理](../ppu_sdk/05_driver_api.md) — 分配/释放、数组、指针属性、预取
    - [内存复制](../ppu_sdk/05_driver_api.md) — 同步/异步 memcpy 操作
    - [内存填充](../ppu_sdk/05_driver_api.md) — 同步/异步 memset 操作
    - [虚拟内存管理](../ppu_sdk/05_driver_api.md) — 地址预留/映射/访问控制
    - [内存池管理](../ppu_sdk/05_driver_api.md) — 流有序内存分配器
- [流与事件](../ppu_sdk/05_driver_api.md)
    - [资源管理](../ppu_sdk/05_driver_api.md) — 事件创建/同步、流创建/同步/捕获
    - [流内存操作](../ppu_sdk/05_driver_api.md) — 流内 wait/write 内存操作
- [执行与调度](../ppu_sdk/05_driver_api.md)
    - [执行控制](../ppu_sdk/05_driver_api.md) — 核函数启动、函数属性、占用率查询
    - [图管理](../ppu_sdk/05_driver_api.md) — 图构建/实例化/启动
- [图像资源](../ppu_sdk/05_driver_api.md)
    - [图像资源管理](../ppu_sdk/05_driver_api.md) — 纹理对象创建/查询
- [参考](../ppu_sdk/05_driver_api.md)
    - [数据结构](../ppu_sdk/05_driver_api.md)
    - [数据字段](../ppu_sdk/05_driver_api.md)

## 9. T-Head SAIL HGGC Runtime API 文档结构

以下为 [T-Head SAIL HGGC Runtime API](../ppu_sdk/04_runtime_api.md) 的完整章节结构，供查阅 API 时定位：

- [概念与约束](../ppu_sdk/04_runtime_api.md)
    - [驱动 API 与运行时 API 的区别](../ppu_sdk/04_runtime_api.md) — 两套 API 的定位、适用场景与选型建议
    - [API 同步行为](../ppu_sdk/04_runtime_api.md) — 各 API 的阻塞/非阻塞语义
    - [流同步行为](../ppu_sdk/04_runtime_api.md) — 流内操作的排序与同步保证
    - [图对象的线程安全性](../ppu_sdk/04_runtime_api.md) — 图创建/实例化/启动的线程安全规则
    - [版本混用规则](../ppu_sdk/04_runtime_api.md) — 不同版本驱动与工具链的兼容约束
    - [HGGC 运行时 API 版本差异](../ppu_sdk/04_runtime_api.md) — 各版本间接口变更说明
- [基础与初始化](../ppu_sdk/04_runtime_api.md)
    - [HGGC 运行时使用的数据类型](../ppu_sdk/04_runtime_api.md) — 枚举、结构体、类型别名
    - [实用工具](../ppu_sdk/04_runtime_api.md) — 版本查询、错误处理、驱动入口点访问
- [设备与上下文](../ppu_sdk/04_runtime_api.md)
    - [设备管理](../ppu_sdk/04_runtime_api.md) — 设备查询、属性配置、异步通知
    - [对等设备内存访问](../ppu_sdk/04_runtime_api.md) — 对等设备内存互访
- [模块与代码加载](../ppu_sdk/04_runtime_api.md)
    - [模块与符号管理](../ppu_sdk/04_runtime_api.md) — 获取函数句柄、符号地址/大小查询
- [内存管理](../ppu_sdk/04_runtime_api.md)
    - [内存管理](../ppu_sdk/04_runtime_api.md) — 分配/释放、数组、指针属性、预取
    - [内存复制](../ppu_sdk/04_runtime_api.md) — 同步/异步 memcpy 操作
    - [内存填充](../ppu_sdk/04_runtime_api.md) — 同步/异步 memset 操作
    - [流有序内存分配器](../ppu_sdk/04_runtime_api.md) — 流有序内存分配器
- [流与事件](../ppu_sdk/04_runtime_api.md)
    - [流与事件管理](../ppu_sdk/04_runtime_api.md) — 事件创建/同步、流创建/同步/捕获
- [执行与调度](../ppu_sdk/04_runtime_api.md)
    - [执行控制](../ppu_sdk/04_runtime_api.md) — 核函数启动、函数属性、占用率查询
    - [图管理](../ppu_sdk/04_runtime_api.md) — 图构建/实例化/启动
- [互操作与扩展](../ppu_sdk/04_runtime_api.md)
    - [外部资源互操作](../ppu_sdk/04_runtime_api.md) — 外部内存/信号量导入导出
- [参考](../ppu_sdk/04_runtime_api.md)
    - [数据结构索引](../ppu_sdk/04_runtime_api.md)
    - [数据字段索引](../ppu_sdk/04_runtime_api.md)

比赛关联：写自定义推理路径（绕过框架直接调 Runtime/Driver API）时，这两张结构表是查 API 的索引——内存池、流捕获、图（Graph）实例化与启动是降低 decode 阶段 launch 开销、压 TTFT 的关键入口。
