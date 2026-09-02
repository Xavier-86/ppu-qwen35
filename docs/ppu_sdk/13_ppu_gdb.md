# T-Head SAIL PPU-GDB <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [1. 概述](#1-概述)
  - [1.1 PPU-GDB 简介](#11-ppu-gdb-简介)
  - [1.2 功能概览](#12-功能概览)
- [2. 快速入门](#2-快速入门)
  - [2.1 安装](#21-安装)
  - [2.2 编译与调试程序](#22-编译与调试程序)
  - [2.3 启动调试会话](#23-启动调试会话)
- [3. PPU 扩展命令](#3-ppu-扩展命令)
  - [3.1 命名规则](#31-命名规则)
  - [3.2 PPU 扩展命令帮助系统](#32-ppu-扩展命令帮助系统)
- [4. 调试基础](#4-调试基础)
  - [4.1 断点](#41-断点)
  - [4.2 单步执行与程序控制](#42-单步执行与程序控制)
  - [4.3 变量与内存查看](#43-变量与内存查看)
- [5. PPU 设备状态查看](#5-ppu-设备状态查看)
  - [5.1 设备坐标系统与焦点切换](#51-设备坐标系统与焦点切换)
  - [5.2 设备与 Kernel 状态](#52-设备与-kernel-状态)
  - [5.3 反汇编](#53-反汇编)
  - [5.4 寄存器查看](#54-寄存器查看)
  - [5.5 共享内存大小查看](#55-共享内存大小查看)
- [6. 异常功能](#6-异常功能)
  - [6.1 异常检查](#61-异常检查)
  - [6.2 自动步进（Autostep）](#62-自动步进autostep)
- [7. 核心转储（Coredump）](#7-核心转储coredump)
  - [7.1 启用核心转储](#71-启用核心转储)
  - [7.2 使用核心转储文件](#72-使用核心转储文件)
- [附录 A：PPU 异常代码表](#附录-appu-异常代码表)


## 1. 概述

### 1.1 PPU-GDB 简介

PPU-GDB 是 T-Head SAIL SDK 工具链中的调试器，支持在同一应用程序中同时调试主机端（CPU）和设备端（PPU）代码。该工具基于 GNU GDB 扩展，增加了一组以 `ppu` 为前缀的命令用于与 PPU 设备交互，同时保留 GDB 原有的主机端调试能力。

PPU-GDB 的可执行文件名为 `ppu-gdb`，运行于 Linux 操作系统。

> **注意**：PPU-GDB 尚未随本版 SDK 发布，预计将在后续版本中推出，敬请期待。

### 1.2 功能概览

| 类别   | 项目                 | 说明                                                                    |
| ------ | -------------------- | ----------------------------------------------------------------------- |
| 支持   | C/C++ HGGC 应用调试  | 主机端与设备端代码的混合调试                                            |
| 支持   | 断点                 | 符号、行号、地址、kernel 入口、条件断点                                 |
| 支持   | 单步执行             | `next`/`nexti`/`step`/`stepi`                                           |
| 支持   | 变量与内存检查       | 包括线程块共享内存（TSM，Thread block Shared Memory）、全局内存、寄存器 |
| 支持   | 异常检查             | 捕获并报告 PPU 硬件异常，提供异常现场                                   |
| 支持   | 自动步进（autostep） | 精确定位异常发生的具体指令和线程                                        |
| 支持   | 核心转储             | 设备端核心转储文件生成与离线分析                                        |
| 支持   | Attach/Detach        | 附加到已运行的进程进行调试                                              |
| 不支持 | 多卡同时调试         | 受硬件限制，每次会话仅能调试一张 PPU 卡                                 |
| 不支持 | 远程调试             | —                                                                       |
| 不支持 | 设备端观察点         | 主机端观察点按 GDB 标准支持                                             |

## 2. 快速入门

### 2.1 安装

PPU-GDB 随 T-Head SAIL SDK 一同安装。安装完成后，执行以下命令确认版本信息：

```bash
bash$: ppu-gdb -v

T-Head (R) PPU Debugger
release (version), build version: 12.0.50-(date)--git
Portions Copyright (C) 2023-2025 T-Head Corporation

GNU gdb (GDB) 12.0.50.20211207-git
Copyright (C) 2021 Free Software Foundation, Inc.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
```

### 2.2 编译与调试程序

要使用 PPU-GDB 调试 HGGC 程序，编译时需要向 HGGC 编译器前端传递调试选项以生成调试信息：

```bash
hgcc -g -G test.cu -o test
```

使用 `-g -G` 编译时，编译器行为如下：

- 强制使用 O0 编译，设备端编译器仅保留极少数的优化
- 在可执行程序中嵌入调试信息

**调试选项说明**

| 选项        | 作用               | 副作用                                       |
| ----------- | ------------------ | -------------------------------------------- |
| `-g`        | 生成主机端调试信息 | —                                            |
| `-G`        | 生成设备端调试信息 | 增加二进制文件大小，因缺少优化降低运行性能   |
| `-lineinfo` | 生成设备端行号信息 | 不影响二进制文件大小和性能，但不支持变量打印 |

### 2.3 启动调试会话

**直接启动程序**

使用 `HGGC_VISIBLE_DEVICES` 环境变量指定调试使用的 PPU 卡，以确保调试会话独占该设备：

```bash
HGGC_VISIBLE_DEVICES=1 ppu-gdb my_app
```

**附加到已运行的进程**

查找目标进程的 PID 后执行 attach：

```bash
ppu-gdb -p ID
```

指定 PPU 卡进行 attach（PPU ID 可通过 `ppu-smi` 获取）：

```bash
ppu-gdb -p ID -deviceid=id
```

> **警告**
>
> - PPU-GDB 由于硬件限制不支持同时调试多卡
> - PPU-GDB 不支持 remote 调试

比赛关联：调试自研 HGGC kernel 时，`-lineinfo` 是不损失性能的折中选项——可在保留优化的情况下用行号定位问题，适合对量化/算子优化后的 kernel 做正确性核查。

## 3. PPU 扩展命令

### 3.1 命名规则

GDB 原生命令在 PPU-GDB 中保持不变。所有 PPU 专用的扩展命令和选项均以 `ppu` 关键字为前缀，命令名称尽可能与 GDB 中等效的主机端命令保持一致。

**示例对比**

| 操作     | 主机端命令     | PPU 设备端命令     |
| -------- | -------------- | ------------------ |
| 查看线程 | `info threads` | `info ppu threads` |
| 切换线程 | `thread 1`     | `ppu thread 1`     |

### 3.2 PPU 扩展命令帮助系统

所有 PPU 扩展命令均提供内置帮助信息：

```bash
(ppu-gdb) help ppu
Print or select the PPU focus.

List of ppu subcommands:

ppu all -- Print the current PPU all msg .
ppu block -- Print or select the current PPU block.
ppu device -- Print or select the current PPU device.
ppu grid -- Print or select the current PPU grid.
ppu kernel -- Print or select the current PPU kernel.
ppu lane -- Print or select the current PPU lane.
ppu register -- Print register addr in THM（Trap Handler Memory）.
ppu thread -- Print or select the current PPU thread.
ppu warp -- Print or select the current PPU warp.

(ppu-gdb) help info ppu
Print information about the current PPU activities. Available options:
           devices : information about all the device in the current dispatch
        exceptions : information about all the warp with exception in the current dispatch
             warps : information about all the warps in the current dispatch
             lanes : information about all the lanes in the current warp
           kernels : information about all the active kernels
            blocks : information about all the active blocks in the current kernel
           threads : information about all the active threads in the current kernel
 kernel_byval_args : information about the kernel args with byval in the current kernel
```

## 4. 调试基础

本章介绍使用 PPU-GDB 进行日常调试的核心操作。在开始之前，有必要了解 PPU 设备上的线程组织方式，因为这直接影响断点和单步执行的行为。

PPU-GDB 使用 **kernel**、**grid**、**block**、**thread**、**warp**、**lane** 等坐标来定位设备端线程，并提供了一套命令在这些坐标之间进行切换（详见[第 5 章](#5-ppu-设备状态查看)）。

### 4.1 断点

在设备代码上设置断点所使用的命令与主机代码相同。本节介绍几种断点设置方式，以及 PPU 设备上断点的特殊行为。

**设备端断点的生效时机**

在设备代码上设置的断点起初处于挂起状态。当 kernel 的 ELF 映像加载完毕后，断点被解析为实际地址并立即生效。

**断点命中与线程停止**

当程序计数器（PC）到达断点地址时，PPU 上所有活跃线程均会停止。一个线程命中断点时，无法保证其他线程也同时命中该断点，因此**同一个断点可能被多次命中**。每次命中时应检查当前焦点所在的线程，以确认是哪个线程触发了断点。

#### 4.1.1 符号断点

在函数入口处设置断点，支持普通 C/C++ 函数、类方法和模板函数：

```bash
(ppu-gdb) break func
(ppu-gdb) break class::func
(ppu-gdb) break add<float>
```

#### 4.1.2 行号断点

在指定源文件的行号处设置断点：

```bash
(ppu-gdb) break test.cu:185
```

如果指定行对应模板函数中的指令，将为每个模板实例创建一个断点。

#### 4.1.3 地址断点

在指定地址（主机或设备）上设置断点：

```bash
(ppu-gdb) break *0x1afe34d0
```

> **警告**：PPU-GDB 使用时遵循 GDB 的地址断点设计，如果调试中存在地址断点，重新 run 之前需要将地址断点 delete 或者 disable，否则将导致 run 失败。

#### 4.1.4 Kernel 入口断点

在每个 kernel 的第一条指令处自动设置断点：

```bash
(ppu-gdb) set ppu break_on_launch application
```

#### 4.1.5 条件断点

使用 `if` 关键字或 `cond` 命令为断点附加条件：

```bash
(ppu-gdb) break test.cu:10 if threadIdx.x == 1 && i < 5
(ppu-gdb) cond 3 threadIdx.x == 1 && i < 5
```

条件表达式可以引用任何变量，包括 `threadIdx`、`blockIdx` 等 internal 变量。不允许在条件表达式中调用函数。

#### 4.1.6 观察断点

观察断点指 GDB 中的 **watchpoint** 功能。

> **警告**
>
> - 不支持对 HGGC 程序设置观察点
> - 支持对主机代码设置观察点，观察点数量和使用请参考 GDB 文档

### 4.2 单步执行与程序控制

**中断程序**

当 PPU-GDB 运行中的程序出现卡顿或陷入死循环时，按下 **CTRL+C** 可中断执行。调试器收到中断信号后，CPU 和 PPU 会同时暂停，并出现 `(ppu-gdb)` 提示符。此时可以检查状态、修改变量、单步执行、恢复运行或退出程序。

此功能仅适用于在调试器内部启动的程序。对于调试器外部启动的程序，请使用 attach 功能。

**单步执行命令**

程序的启动方式（`run` 命令）与标准 GDB 相同。以下单步执行命令与 GNU GDB 功能相同：

| 命令    | 缩写 | 步进粒度      | 是否进入被调函数 | 说明                                     |
| ------- | ---- | ------------- | ---------------- | ---------------------------------------- |
| `next`  | `n`  | 源代码行      | 否               | 单步到下一行源代码                       |
| `nexti` | `ni` | 单条 ISA 指令 | 否               | 单步到下一条 ISA 指令                    |
| `step`  | `s`  | 源代码行      | 是               | 进入被调函数，跳过序言，停在函数体第一行 |
| `stepi` | `si` | 单条汇编指令  | 是               | 进入被调函数，不跳过序言，停在第一条指令 |

### 4.3 变量与内存查看

GDB 的 `print` 命令可访问以下内存区域中的数据：

- 主机端通过 `hggcMalloc` 分配的变量
- PPU 设备各内存区域中的数据：共享内存（TSM）、本地内存、全局内存
- 运行时内建变量：`threadIdx`、`blockIdx`、`warpSize` 等

**变量存储位置**

根据变量的类型和用途，变量可能存储在寄存器或各级内存（共享内存、本地内存、全局内存）中。使用 `print` 命令查看变量地址可确定其存储位置。

**访问共享内存中的数组**

```bash
__shared__ int cache[224]; // 源码

(ppu-gdb) print cache
$2 = {1 <repeats 224 times>}

(ppu-gdb) print &cache
$3 = (@shared int [*](224)) tsm#0x0

(ppu-gdb) p cache[0]@4
$4 = {1, 1, 1, 1}
```

**通过偏移地址访问共享内存**

```bash
(ppu-gdb) print *(@shared int*) tsm#0x20
$5 = 1

(ppu-gdb) print *(@shared int*) tsm#0x24
$6 = 1

(ppu-gdb) print *(@shared int*) tsm#0x28
$7 = 1
```

## 5. PPU 设备状态查看

### 5.1 设备坐标系统与焦点切换

HGGC 程序可能同时运行在多个主机线程和大量设备端线程上。PPU-GDB 使用一套坐标来定位设备端线程：**device**、**kernel**、**grid**、**block**、**thread**、**warp**、**lane**。所有设备端命令作用于当前焦点所在的坐标，设备端最小焦点级别为线程。

**坐标系层级**

各坐标包含关系如下：

```bash
device              PPU 物理设备（一张 PPU 卡）
 └─ kernel          当前设备上正在执行的 kernel 函数
     └─ grid        kernel 启动时创建的 grid（一个 kernel 对应一个 grid）
         └─ block   grid 中的线程块，由 blockIdx (x, y, z) 索引
             └─ warp    block 中的线程组，硬件以 warp 为单位调度执行
                 └─ lane    warp 中的单个执行通道（编号 0~31），每个 lane 对应一个 thread
```

**thread** 是线程在 block 内的软件视角索引，由 `threadIdx (x, y, z)` 表示，与 lane 一一对应。例如 block 中 `threadIdx.x = 0~31` 的线程属于 warp 0，分别对应 lane 0~31；`threadIdx.x = 32~63` 属于 warp 1，以此类推。切换 thread 时 warp/lane 会同步更新，反之亦然。

**焦点（Focus）**

焦点是 PPU-GDB 当前正在调试的坐标位置。调试器在任意时刻只有一个焦点，所有设备端命令（如 `print`、`info registers`）均作用于当前焦点所在的线程。断点命中或异常发生时，焦点会自动切换到触发事件的线程；用户也可通过 `ppu` 命令手动切换焦点（详见下文）。

**查看当前焦点**

支持单独查看各级坐标，也可使用 `all` 一次查看全部：

```bash
(ppu-gdb) ppu device kernel grid block thread lane
kernel 0, grid 24677911420207104, block (0,0,0), thread (128,0,0), lane 0
(ppu-gdb) ppu all
kernel 0, grid 24677911420207104, block (0,0,0), thread (128,0,0), warp 4, lane 0
```

**切换焦点**

支持单级切换和 Dim3 坐标切换。如果目标坐标不存在则切换失败：

```bash
(ppu-gdb) ppu warp 2
[Switching to thread 6, lane 0 (PPU focus kernel 0, grid 24677911420207104, block(0,0,0), thread(64,0,0), device 0, warp 2, lane 0)]
# 0  run_tsm_of_range (dev_data=0x21b800000) at tsm_out_of_range.cu:12
12     int tid = threadIdx.x + blockIdx.x * blockDim.x;

(ppu-gdb) ppu warp 4 lane 1
[Switching to thread 3, lane 1 (PPU focus kernel 0, grid 24677911420207104, block(0,0,0), thread(129,0,0), device 0, warp 4, lane 1)]
# 0  run_tsm_of_range (dev_data=0x21b800000) at tsm_out_of_range.cu:12
12     int tid = threadIdx.x + blockIdx.x * blockDim.x;

(ppu-gdb) ppu thread(32, 0, 0)
[Switching to thread 5, lane 0 (PPU focus kernel 0, grid 24677911420207104, block(0,0,0), thread(32,0,0), device 0, warp 1, lane 0)]
# 0  run_tsm_of_range (dev_data=0x21b800000) at tsm_out_of_range.cu:12
12     int tid = threadIdx.x + blockIdx.x * blockDim.x;
```

### 5.2 设备与 Kernel 状态

以下 `info ppu` 子命令用于查看 PPU 设备和 HGGC 应用程序的运行状态：

| 命令                         | 作用                                                 |
| ---------------------------- | ---------------------------------------------------- |
| `info ppu devices`           | 查看所有设备信息（单卡调试时仅当前 PPU ID 信息准确） |
| `info ppu kernels`           | 查看当前设备上正在执行的所有 kernel                  |
| `info ppu blocks`            | 查看当前 kernel 下所有正在运行的 block               |
| `info ppu threads`           | 查看当前 kernel 下所有线程信息                       |
| `info ppu warps`             | 查看当前计算单元中所有 warp 信息                     |
| `info ppu lanes`             | 查看当前 warp 中所有活跃线程                         |
| `info ppu exceptions`        | 查看当前出现异常的 warp                              |
| `info ppu kernel_byval_args` | 查看通过设备内存传递给 kernel 的参数信息             |

**设备信息**

```bash
(ppu-gdb) info ppu devices
Device_id  Name   Lanes/Warp   Max_Regs/Lane  Active_CEs
* 0          PPU#0    32           256            0x2
  1          PPU#1    32           256            0x0
```

**Kernel 信息**

```bash
(ppu-gdb) info ppu kernels
    KernelIdx DeviceIdx Status GridDim BlockDim Invocation

* 0         0         active (1,1,1) (256,1,1) run_tsm_of_range(int*)

```

**Block 信息**

```bash
(ppu-gdb) info ppu blocks
    Kernel  BlockIdx   To  BlockIdx   Count  State
* 0       (0,0,0)    to  (0,0,0)    1      running

```

**Warp 信息**

```bash
(ppu-gdb) info ppu warps
      WarpId ActiveLaneMsk DivergentLaneMsk ActivePC     Kernel BlockIdx FirstActiveThreadIdx
      0      0xffffffff    0x0              0x21b001098  0      (0,0,0)  (0,0,0)
      1      0xffffffff    0x0              0x21b001098  0      (0,0,0)  (32,0,0)
      2      0xffffffff    0x0              0x21b001098  0      (0,0,0)  (64,0,0)
      3      0xffffffff    0x0              0x21b001098  0      (0,0,0)  (96,0,0)
*     4      0xffffffff    0x0              0x21b001098  0      (0,0,0)  (128,0,0)
      5      0xffffffff    0x0              0x21b001098  0      (0,0,0)  (160,0,0)
      6      0xffffffff    0x0              0x21b001098  0      (0,0,0)  (192,0,0)
      7      0xffffffff    0x0              0x21b001098  0      (0,0,0)  (224,0,0)

```

**Lane 信息**

```bash
(ppu-gdb) info ppu lanes
      LaneId    State    EMSK PMSK YMSK WMSK QMSK       PC        ThreadIdx       Exception

*     0      active      0x1  0x0  0x0  0x0  0x0  0x21b001098     (128,0,0)       None
      1      active      0x1  0x0  0x0  0x0  0x0  0x21b001098     (129,0,0)       None
      2      active      0x1  0x0  0x0  0x0  0x0  0x21b001098     (130,0,0)       None
      3      active      0x1  0x0  0x0  0x0  0x0  0x21b001098     (131,0,0)       None
      4      active      0x1  0x0  0x0  0x0  0x0  0x21b001098     (132,0,0)       None
      5      active      0x1  0x0  0x0  0x0  0x0  0x21b001098     (133,0,0)       None
      6      active      0x1  0x0  0x0  0x0  0x0  0x21b001098     (134,0,0)       None
      7      active      0x1  0x0  0x0  0x0  0x0  0x21b001098     (135,0,0)       None
      8      active      0x1  0x0  0x0  0x0  0x0  0x21b001098     (136,0,0)       None
      9      active      0x1  0x0  0x0  0x0  0x0  0x21b001098     (137,0,0)       None
      10     active      0x1  0x0  0x0  0x0  0x0  0x21b001098     (138,0,0)       None
      11     active      0x1  0x0  0x0  0x0  0x0  0x21b001098     (139,0,0)       None
...
...
      31     active      0x1  0x0  0x0  0x0  0x0  0x21b001098     (159,0,0)       None

```

**thread 信息**

```bash
(ppu-gdb) info ppu threads
    Kernel  BlockIdx  ThreadIdx  To  BlockIdx  ThreadIdx Count      PC         Filename           Line

*     0   (0,0,0)    (0,0,0)  to   (0,0,0)  (255,0,0)   256     0x21b001098 tsm_out_of_range.cu   12

```

**异常信息**

```bash
(ppu-gdb) info ppu exceptions
WarpId ActivePC  Kernel BlockIdx  Exception
   7   0x21b001150 0      (0,0,0)   PPU_EXCEPTION_9 : TSM out of range
```

### 5.3 反汇编

使用 GDB 标准命令（`x/i`、`display/i`）查看设备端 ISA 指令：

```bash
(ppu-gdb) x/4i $pc-32
   0x21b001130 <_Z16run_tsm_of_rangePi+200>:  v.mov.v2s sreg19, vreg41, 0x20
   0x21b001138 <_Z16run_tsm_of_rangePi+208>:  vmem.ld.b32.sign vreg4, [0x0 + vreg42 * 0x4] @sreg[18:19]
   0x21b001140 <_Z16run_tsm_of_rangePi+216>:  s.mov.b32 sreg7, 0x0
   0x21b001148 <_Z16run_tsm_of_rangePi+224>:  tsm.ld.b32 vreg5, [sreg7 + vreg42 * 0x4]
=> 0x21b001150 <_Z16run_tsm_of_rangePi+232>:  s.wait vldcnt(0), tsmcnt(0)
```

### 5.4 寄存器查看

使用 GDB 标准命令检查和修改设备寄存器。PPU 寄存器类型如下：

- **Uniform 寄存器**（`sreg`，前缀 `s`）：标量寄存器，warp 内所有线程共享同一值
- **Divergent 寄存器**（`vreg`，前缀 `v`）：向量寄存器，warp 内各线程可持有不同值
- **特殊寄存器**：使用 `info all-registers` 查看完整列表

**查看 Uniform 寄存器**

```bash
(ppu-gdb) info registers s0 s1 s2 s3
s0             0x0                 0
s1             0x0                 0
s2             0x0                 0
s3             0x0                 0
```

**查看 Divergent 寄存器**

```bash
(ppu-gdb) info registers v0 v1 v42
v0             0x43600225          1130365477
v1             0x0                 0
v42            0xe0                224
```

由于 Divergent 寄存器在各 lane 中可能持有不同的值，`info registers` 仅显示当前焦点 lane 的值。为方便查看所有 lane 的内容，PPU-GDB 提供了 `ppu register` 命令，可一次性显示全部 32 个 lane 的寄存器值：

```bash
(ppu-gdb) ppu register v42
register v42:
lane 0~4:  0xe0, 0xe1, 0xe2, 0xe3
lane 4~8:  0xe4, 0xe5, 0xe6, 0xe7
lane 8~12:  0xe8, 0xe9, 0xea, 0xeb
lane 12~16: 0xec, 0xed, 0xee, 0xef
lane 16~20: 0xf0, 0xf1, 0xf2, 0xf3
lane 20~24: 0xf4, 0xf5, 0xf6, 0xf7
lane 24~28: 0xf8, 0xf9, 0xfa, 0xfb
lane 28~32: 0xfc, 0xfd, 0xfe, 0xff
```

> **警告**：`ppu register` 命令统一打印 16 进制数据，浮点类型请自行转换。

### 5.5 共享内存大小查看

查看共享内存分配大小有助于判断内存访问是否越界：

```bash
(ppu-gdb) ppu register TSM_SIZE
register TSM_SIZE: 0x380

(ppu-gdb) info registers TSM_SIZE
TSM_SIZE       0x380               896
```

比赛关联：`info ppu warps` 的 ActiveLaneMsk/DivergentLaneMsk 和反汇编能力可用于分析 kernel 的分支分歧与访存指令序列，是算子优化阶段定位 warp 分歧、核对编译产物的直接手段。

## 6. 异常功能

### 6.1 异常检查

PPU-GDB 遵循 GDB 对 signal 处理的原则，将 PPU 硬件异常映射为信号进行管理。当 PPU 设备在执行过程中发生硬件异常时，PPU-GDB 会暂停程序并允许查看出错现场。暂停后程序无法继续正常执行。

> **警告**：**异常定位精度说明**：PPU-GDB 捕获并报告最先上报中断的 warp。由于硬件机制，实际发生异常的指令地址小于或等于 PPU-GDB 停止时报告的 PC 地址。

**示例**

```bash
bash$: ppu-gdb test -q
Reading symbols from test...
(ppu-gdb) r
Starting program: test
[New Thread 0x7ffff750b6c0 (LWP 3982119)]

Thread 3 "test" received signal PPU_EXCEPTION_9, TSM out of range.
[Switching to thread 3, lane 0 (PPU focus kernel 0, grid 25629100647383040, block(0,0,0), thread(224,0,0), device 0, warp 7, lane 0)]
0x000000021b001150 in run_tsm_of_range (dev_data=0x21b800000) at tsm_out_of_range.cu:16
16     dev_data[tid]= dev_data[tid]+cache[tid];
```

完整的异常代码列表见[附录 A](#附录-appu-异常代码表)。

### 6.2 自动步进（Autostep）

#### 6.2.1 命令语法

```bash
autostep [LOCATION]
autostep [LOCATION] for LENGTH [lines|instructions]
```

`astep` 可作为 `autostep` 的缩写。

**快速示例**

```bash
(ppu-gdb) autostep test.cu:10 for 49 instructions
(ppu-gdb) autostep test.cu:20 for 11 lines
```

#### 6.2.2 使用场景

当需要精确定位异常发生的具体指令和线程时，使用 `autostep`。用户指定一段可能出现异常的代码区间，程序在该区间内自动逐步执行，区间之外仍正常运行。如果异常发生在指定区间内，PPU-GDB 能够报告异常的确切来源。

#### 6.2.3 技术背景

如 [6.1 节](#61-异常检查)所述，异常实际发生的位置小于等于 PPU-GDB 捕获到的 PC 位置。手动单步执行虽然能提供精确结果，但过程缓慢，且需要逐一对每个 warp 进行单步操作。`autostep` 在指定区间内自动完成这一过程，兼顾精度与效率。

#### 6.2.4 参数说明

| 参数       | 说明                                                                                                      |
| ---------- | --------------------------------------------------------------------------------------------------------- |
| `LOCATION` | 断点位置，支持行号、函数名或 `*地址`。省略时使用当前指令地址                                              |
| `LENGTH`   | 自动步进区间的长度，单位为行（`lines` / `l`）或指令（`instructions` / `i`）。省略 `for` 子句时默认为 1 行 |

#### 6.2.5 行为细节

- 在自动步进过程中，遇到的函数调用会被跳过（不进入）
- 遇到分支时，每个 warp 的步进长度以其第一个活跃 lane 的行数或指令数为准
- 如果区间内存在断点，命中断点的 warp 在程序恢复运行时不会继续自动步进
- 不支持重叠的 autostep 断点；执行一个 autostep 区间时遇到另一个 autostep，后者会被忽略

#### 6.2.6 排查未捕获异常

如果设置了 autostep 区间但异常未被捕获，可能的原因是指定的步进范围太小，或在 autostep 起始地址与触发异常的指令之间存在函数调用（autostep 不会进入函数内部）。解决方法：

- 增大步进范围以覆盖出错指令
- 将 autostep 起始位置移动到更接近出错指令的位置

#### 6.2.7 管理命令

| 命令                 | 作用                                                        |
| -------------------- | ----------------------------------------------------------- |
| `info autosteps`     | 列出所有 autostep 断点和普通断点（类似 `info breakpoints`） |
| `disable autosteps`  | 禁用 autostep 断点（等价 `disable breakpoints n`）          |
| `delete autosteps n` | 删除指定 autostep 断点（等价 `delete breakpoints n`）       |

```bash
(ppu-gdb) info autosteps
Num  Type      Disp Enb Address            What
1    autostep  keep y   0x0000000000401234 in kernel_test at test.cu:10 for 49 instructions
3    autostep  keep y   0x0000000000489913 in kernel_test at test.cu:20 for 11 lines
```

比赛关联：自研量化/融合 kernel 出现 TSM 越界、全局内存越界等硬件异常时，`autostep` 能自动把异常定位到具体指令和 warp，比逐 warp 手动单步快得多，是算子调试阶段的关键效率工具。

## 7. 核心转储（Coredump）

PPU-GDB 支持生成设备端核心转储文件，用于离线分析异常现场。主机端核心转储请参考标准 GDB 文档。

### 7.1 启用核心转储

通过环境变量控制核心转储的生成方式和存储路径。相关环境变量默认均为关闭状态。

**选择转储模式**

根据调试需求选择合适的转储模式：

| 调试场景                                   | 推荐模式 | 环境变量设置                                                               | 转储内容                                 |
| ------------------------------------------ | -------- | -------------------------------------------------------------------------- | ---------------------------------------- |
| 需要检查设备端全局内存的访问情况           | 全量转储 | `UMD_ENABLE_COREDUMP_ON_EXCEPTION=1`                                       | 所有内存区域、寄存器、kernel ELF 文件    |
| 仅需检查共享内存和寄存器状态，优先转储速度 | 轻量转储 | `UMD_ENABLE_COREDUMP_ON_EXCEPTION=1` + `UMD_ENABLE_LIGHTWEIGHT_COREDUMP=1` | 共享内存（TSM）、寄存器、kernel ELF 文件 |

> **警告**：全量转储在大型程序上可能导致转储缓慢或磁盘空间不足。如果不需要检查设备端全局内存，建议使用轻量转储模式以提高效率。

**转储文件路径**

使用 `UMD_COREDUMP_FILE` 指定转储文件的存储路径，默认在当前目录下生成。路径中支持以下占位符：

| 占位符 | 含义     |
| ------ | -------- |
| `%p`   | 进程 PID |
| `%h`   | 程序名称 |
| `%t`   | 时间戳   |

```bash
export UMD_COREDUMP_FILE=path/%p.%h.%t
```

### 7.2 使用核心转储文件

```bash
//执行程序
./a.out

//转储完成提示
[umd error]: coredump succeeded, file was written to hggc.core.2840365.a.out.1773827837.dev0! (./os/linux/lnx_coredumpelf.cpp:646:CreateCoreFile)

//ppu-gdb读取文件
bash$ ppu-gdb
T-Head (R) PPU Debugger
release (version), build version: 12.0.50-(date)--git
Portions Copyright (C) 2023-2025 T-Head Corporation
GNU gdb (GDB) 12.0.50.20211207-git
Copyright (C) 2021 Free Software Foundation, Inc.
For help, type "help".
Type "apropos word" to search for commands related to "word".
(ppu-gdb) target ppucore hggc.core.2840365.a.out.1773827837.dev0
Opening GPU coredump: hggc.core.2840365.a.out.1773827837.dev0
warning: PPU-GDB requires target-async, GPU debugging is disabled

PPU_EXCEPTION_9, TSM out of range
# 0  0x000000021b001150 in run_tsm_of_range (dev_data=0x21b800000) at tsm_out_of_range.cu:16
16     dev_data[tid]= dev_data[tid]+cache[tid];
(ppu-gdb)
```

比赛关联：核心转储可在评测环境崩溃后离线复盘显存越界/非法访问现场，轻量转储模式开销小，适合在压力测试（高吞吐场景）下长期开启以捕获偶发错误。

## 附录 A：PPU 异常代码表

| 异常代码         | 描述                                |
| ---------------- | ----------------------------------- |
| PPU_EXCEPTION_0  | Invalid instruction                 |
| PPU_EXCEPTION_1  | Invalid SIMT candidate mask         |
| PPU_EXCEPTION_2  | Invalid barrier parameter           |
| PPU_EXCEPTION_3  | Invalid warp sync                   |
| PPU_EXCEPTION_4  | Hardware hang                       |
| PPU_EXCEPTION_5  | Invalid vreg                        |
| PPU_EXCEPTION_6  | Invalid sreg                        |
| PPU_EXCEPTION_7  | Invalid vreg alignment              |
| PPU_EXCEPTION_8  | Invalid sreg alignment              |
| PPU_EXCEPTION_9  | TSM out of range                    |
| PPU_EXCEPTION_10 | Invalid TSM access alignment        |
| PPU_EXCEPTION_11 | Global mem out of range             |
| PPU_EXCEPTION_12 | Invalid global mem access alignment |
| PPU_EXCEPTION_13 | Invalid atomic op on system mem     |
| PPU_EXCEPTION_14 | AIU_ld TSM size out of range        |
| PPU_EXCEPTION_15 | AIU_ld cube out of range            |
| PPU_EXCEPTION_16 | KI out of range                     |
| PPU_EXCEPTION_17 | Invalid PA (including c2c request)  |
| PPU_EXCEPTION_18 | Invalid PA on page-walk             |
| PPU_EXCEPTION_19 | Invalid page                        |
| PPU_EXCEPTION_20 | Read permission violation           |
| PPU_EXCEPTION_21 | Write permission violation          |
| PPU_EXCEPTION_22 | Exec permission violation           |
| PPU_EXCEPTION_23 | Invalid VA                          |
| PPU_EXCEPTION_24 | KI invalid PA                       |
| PPU_EXCEPTION_25 | KI invalid PA on page-walk          |
| PPU_EXCEPTION_26 | KI invalid page                     |
| PPU_EXCEPTION_27 | KI read permission violation        |
| PPU_EXCEPTION_28 | KI exec permission violation        |
| PPU_EXCEPTION_29 | KI invalid VA                       |
| PPU_EXCEPTION_30 | Hbm ECC error on page-walk          |
| PPU_EXCEPTION_31 | KI hbm ECC error on page-walk       |
| PPU_EXCEPTION_32 | Hbm ECC error on data               |
| PPU_EXCEPTION_33 | KI hbm ECC error on data            |
| PPU_EXCEPTION_34 | Prefetch_error                      |
| PPU_EXCEPTION_35 | Invalid RLSU ld/st address          |
