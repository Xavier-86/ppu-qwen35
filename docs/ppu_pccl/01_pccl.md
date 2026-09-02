# PCCL 集合通信库 <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [1. 简介](#1-简介)
  - [1.1. 概述](#11-概述)
  - [1.2. 适用范围说明](#12-适用范围说明)
- [2. 环境配置与运行示例](#2-环境配置与运行示例)
  - [2.1. 环境配置](#21-环境配置)
  - [2.2. 运行示例（PCCL-TESTS 带宽基准）](#22-运行示例pccl-tests-带宽基准)
- [3. 概念介绍](#3-概念介绍)
  - [3.1. 创建通信域](#31-创建通信域)
  - [3.2. 错误处理与通信域中止](#32-错误处理与通信域中止)
  - [3.3. 集合通信](#33-集合通信)
  - [3.4. HGGC Stream 语义](#34-hggc-stream-语义)
  - [3.5. 组调用](#35-组调用)
  - [3.6. 点对点通信](#36-点对点通信)
  - [3.7. 线程安全](#37-线程安全)
  - [3.8. 使用 HGGC Graphs 捕获 PCCL 通信算子](#38-使用-hggc-graphs-捕获-pccl-通信算子)
  - [3.9. 用户缓冲区注册](#39-用户缓冲区注册)
  - [3.10. RAS](#310-ras)
- [4. 编程实践](#4-编程实践)
  - [4.1. 通信域创建与销毁示例](#41-通信域创建与销毁示例)
  - [4.2. 通信示例](#42-通信示例)
- [5. 高性能实践](#5-高性能实践)
  - [5.1. Device Order Search：Megatron 多维并行下的拓扑感知调度](#51-device-order-searchmegatron-多维并行下的拓扑感知调度)
  - [5.2. 训练推理显存优化建议](#52-训练推理显存优化建议)
  - [5.3. 计算通信并行场景优化](#53-计算通信并行场景优化)
  - [5.4. 大规模训练中的 Desync 排查](#54-大规模训练中的-desync-排查)
- [6. API 指南](#6-api-指南)
  - [6.1. 概述](#61-概述)
  - [6.2. 通信域创建与管理函数](#62-通信域创建与管理函数)
  - [6.3. 集合通信函数](#63-集合通信函数)
  - [6.4. 点对点通信函数](#64-点对点通信函数)
  - [6.5. 组调用函数](#65-组调用函数)
  - [6.6. 数据类型](#66-数据类型)
  - [6.7. PCCL API 支持的标志](#67-pccl-api-支持的标志)
- [7. 环境变量使用指南](#7-环境变量使用指南)
  - [7.1. 网络传输配置](#71-网络传输配置)
  - [7.2. 性能优化](#72-性能优化)
  - [7.3. 内存与资源管理](#73-内存与资源管理)
  - [7.4. 通信域初始化](#74-通信域初始化)
  - [7.5. 插件配置](#75-插件配置)
  - [7.6. 调试与诊断](#76-调试与诊断)
- [8. Debug 指南](#8-debug-指南)
  - [8.1. 快速现场初判](#81-快速现场初判)
  - [8.2. Crash 现场分析](#82-crash-现场分析)
  - [8.3. Hang 现场分析](#83-hang-现场分析)
- [9. 已知问题](#9-已知问题)
  - [9.1. 环境与配置](#91-环境与配置)
  - [9.2. 性能相关](#92-性能相关)
  - [9.3. 稳定性](#93-稳定性)


PCCL（PPU Collective Communications Library）是平头哥 PPU 平台上的高性能集合通信库，功能与接口对标 NCCL，是多卡张量并行、多实例推理部署的通信底座。本文档涵盖 PCCL 简介、环境配置、核心概念、编程实践、高性能实践、完整 API、全部环境变量、故障诊断与已知问题。

## 1. 简介

### 1.1. 概述

PCCL (PPU Collective Communications Library) 是基于 PPU 多卡及多机互联功能而设计的高性能集合通信库。它实现了一系列易用的 PPU 卡间通信原语以供上层应用友好集成，同时也能够对所有已发布的 PPU 多卡产品做到兼容支持。

PCCL 提供了全面的集合通信功能，支持包括

- AllReduce
- AllGather
- ReduceScatter
- AlltoAll
- Broadcast
- Reduce
- Gather
- Scatter

在内的多种标准原语。此外，它还支持灵活的点对点（Send/Recv）通信，能够满足复杂的数据分发与聚合需求。

PPU 各代际产品的芯片底层功能与卡间拓扑设计存在差异。为此，PCCL 针对 PPU 芯片特性及多卡互联架构，对典型通信操作在不同通信规模和用户负载下进行了专项优化。该方案不仅确保单机多卡及多机通信在大负载下达到理想的硬件带宽效率，还通过一系列低延迟互联算子，有效满足了小负载场景下的性能需求。

PCCL 全面兼容主流 AI 生态，开发者可调用软件栈中统一的 API，无需修改过多应用代码即可平滑迁移至 PPU 平台，极大地降低了开发者的迁移成本并支持自主扩展。结合完整的 AI 框架、平台、模型和应用，PCCL 在深度学习框架中显著提升了多 PPU 和多节点神经网络训练的扩展效率。

### 1.2. 适用范围说明

- **支持硬件**：支持平头哥真武 610、真武 610E、真武 805、真武 810、真武 810E、 真武 M890 以及 ICN Switch 1.0 等芯片产品。
- **机内卡间通信**：支持平头哥自研的 ICN 卡间通信与标准 PCIe 通信。
- **机间通信**：支持标准 RDMA RoCE 通信与 socket 通信；在 真武 M890 的超节点产品上支持多机走 ICN 的通信。

> **注意**：若使用阿里云自研高性能网卡 EIC，请联系阿里云获取相应支持。

## 2. 环境配置与运行示例

### 2.1. 环境配置

当前 PCCL 代码尚未开源，因此暂不支持用户自行编译。后续开源后，我们会补充对应的源码获取和编译说明。

现阶段，用户可以通过以下两种方式获取和配置 PCCL 环境：

#### 2.1.1. 通过 T-Head SAIL SDK 安装

T-Head SAIL SDK v2.1 版本已内置 PCCL，包含了所有必需的头文件和动态库。用户只需安装 T-Head SAIL SDK 并配置环境变量即可直接使用 PCCL，无需额外安装。

为避免手动设置较多环境变量（如 `PATH`、`LD_LIBRARY_PATH`），可以运行 T-Head SAIL SDK 提供的环境配置脚本 `T_Head_SAIL_SDK/envsetup.sh`。建议将下面这条命令追加到 `~/.bashrc`，然后重新加载 `~/.bashrc`，或直接打开一个新的 shell 终端，使相关环境变量自动生效。

```bash
echo 'source /your_path/T_Head_SAIL_SDK/envsetup.sh > /dev/null' >> ~/.bashrc
```

#### 2.1.2. 通过 PCCL 独立制品包安装

PCCL 独立制品包提供了 PCCL 相关的所有组件，适用于需要单独更新或管理 PCCL 版本的场景。

该制品包包含：

```text
pccl/
├── bin
│   └── pcclras
├── envsetup.sh
├── include
│   ├── pccl.h
│   └── pccl_net.h
└── lib
    ├── libpccl-ext-kernel.so
    ├── libpccl-profiler-example.so
    ├── libpccl-tuner.so
    └── libpccl.so.2.1.1
```

制品包内容说明：

- `bin/pcclras`：PCCL RAS 工具
- `envsetup.sh`：环境变量配置脚本
- `include/`：PCCL 头文件
- `lib/`：PCCL 动态库及插件

用户可以运行 `envsetup.sh` 来完成环境变量配置。建议将下面的命令追加到 `~/.bashrc`，一键完成配置：

```bash
# ppusdk 环境变量配置示例
echo 'source /your_path/T_Head_SAIL_SDK/envsetup.sh > /dev/null' >> ~/.bashrc

# pccl 环境变量配置示例
echo 'source /your_path/pccl/envsetup.sh > /dev/null' >> ~/.bashrc
```

PCCL 运行依赖完整的 T-Head SAIL SDK 环境（包括驱动、运行时库等），因此使用 PCCL 独立制品包时，必须先安装并配置好 T-Head SAIL SDK。

### 2.2. 运行示例（PCCL-TESTS 带宽基准）

PCCL-TESTS 提供了 collective op 测试。代码目前尚未开源，后续开源后，我们会补充对应的源码获取和编译说明。

现阶段，用户可以获取 `comm_tools` 制品包，直接使用预编译好的 PCCL-TESTS 运行测试。`comm_tools/multi_process` 和 `comm_tools/single_process` 两个目录下分别提供了依赖 MPI 编译的多进程测试和不依赖 MPI 编译的单进程测试。

- 可执行文件
  - all_reduce_perf
  - all_gather_perf
  - broadcast_perf
  - reduce_perf
  - reduce_scatter_perf
  - alltoall_perf
  - hypercube_perf
  - sendrecv_perf
  - gather_perf
  - scatter_perf

- 参数说明
  - `-g <INTEGER>` 每个线程对应的 device 数目。
  - `-d <STR>` 指定使用的数据类型，默认为 `float`。
  - `-b <STR>` 最小传输 size，值可以是数字如 32，表示 32 bytes，也可以是带单位的字符串如 32MB。对于所有 collective kernel，这里的 size 指的是 output buffer 的大小。
  - `-e <STR>` 最大传输 size。
  - `-f <INTEGER>` 从最小传输 size 遍历到最大传输 size 的 step，一般设置为 2，表示后一次测试的 size 是前一次的两倍。
  - `-n <INTEGER>` 重复执行 kernel 的次数，最终的单次执行时间为总时间除以执行次数。
  - `-w <INTEGER>` warmup 的执行次数。
  - `-a <0/1/2/3>` 每轮 iter 的时间记录方式，0 表示只记录 RANK0 上的时间，1/2/3 分别表示记录所有 dev 上的时间平均值/最小值/最大值，默认值为 2。
  - `-x <0/1/2>` 时间统计方式（默认值：0）。
    - 0: cpu 统计方式，基于 C++ 标准库 `<chrono>` 提供的高精度时钟采集时间戳，测量包括 host 和 device 侧的端到端执行时间。适用于评估端到端性能。
    - 1: hggc stream event 统计方式，在 kernel 所在 stream 的前后插入 event 采集时间戳，测量 device 侧的 kernel 执行时间，event 和 kernel 之间的微小开销也会统计在内，所以实际测量时间一般会低于 cpu 统计方式但高于 hgpti 统计方式。适用于所有 device 侧性能评估。
    - 2: hgpti 统计方式，通过性能分析工具接口订阅 kernel 活动事件并采集时间戳，严格统计实际的 kernel 执行时间。适用于小数据量的 kernel 性能精确评估，但不支持 ce copy 等的评估。
  - `-R <0/1/2>` buffer register. 0: 关闭，1: 开启 local register，2: 开启 symmetric memory register。

在真武 M890 机器上执行多进程 8 卡测试，数据量范围为 8B 到 2GB

```bash
$mpirun -np 8 all_reduce_perf -t 1 -g 1 -d float -b 8 -e 2GB -f 2 -n 20 -w 5
# nThread 1 nGpus 1 minBytes 8 maxBytes 2147483648 offset <0>/<0> step: 2(factor) warmup iters: 5 iters: 20 redop: sum validation: 1 single_test: 0 test_buffer_kind: both elapsed_type: cpu_time average: MIN register: 0
#
# Using devices
#   Rank  0 Group  0 Pid 3957602 on ppu_node0 device  0 [0xc7] ZW-M890P
#   Rank  1 Group  0 Pid 3957603 on ppu_node0 device  1 [0xa3] ZW-M890P
#   Rank  2 Group  0 Pid 3957604 on ppu_node0 device  2 [0x7f] ZW-M890P
#   Rank  3 Group  0 Pid 3957605 on ppu_node0 device  3 [0x09] ZW-M890P
#   Rank  4 Group  0 Pid 3957606 on ppu_node0 device  4 [0x7e] ZW-M890P
#   Rank  5 Group  0 Pid 3957607 on ppu_node0 device  5 [0x08] ZW-M890P
#   Rank  6 Group  0 Pid 3957608 on ppu_node0 device  6 [0xc6] ZW-M890P
#   Rank  7 Group  0 Pid 3957609 on ppu_node0 device  7 [0xa2] ZW-M890P
#
#                                                              out-of-place                      in-place
#       size         count      type   redop   root   cpu_time   algbw  busbw   #wrong   cpu_time   algbw  busbw   #wrong
#        (B)    (elements)                              (us)    (GB/s)  (GB/s)             (us)    (GB/s)  (GB/s)
           8             2     float     sum     -1    31.55    0.00    0.00        0    31.50    0.00    0.00        0
          16             4     float     sum     -1     7.58    0.00    0.00        0     7.29    0.00    0.00        0
          32             8     float     sum     -1     7.26    0.00    0.01        0     7.08    0.00    0.01        0
          64            16     float     sum     -1     7.37    0.01    0.02        0     7.24    0.01    0.02        0
         128            32     float     sum     -1     7.41    0.02    0.03        0     7.24    0.02    0.03        0
         256            64     float     sum     -1     7.63    0.03    0.06        0     7.33    0.03    0.06        0
         512           128     float     sum     -1     7.74    0.07    0.12        0     7.58    0.07    0.12        0
        1024           256     float     sum     -1     7.69    0.13    0.23        0     7.60    0.13    0.24        0
        2048           512     float     sum     -1     7.85    0.26    0.46        0     7.70    0.27    0.47        0
        4096          1024     float     sum     -1     7.95    0.52    0.90        0     8.08    0.51    0.89        0
        8192          2048     float     sum     -1     8.74    0.94    1.64        0     8.52    0.96    1.68        0
       16384          4096     float     sum     -1     9.73    1.68    2.95        0     9.12    1.80    3.14        0
       32768          8192     float     sum     -1    14.90    2.20    3.85        0    14.69    2.23    3.90        0
       65536         16384     float     sum     -1    15.74    4.16    7.29        0    15.53    4.22    7.38        0
      131072         32768     float     sum     -1    16.74    7.83   13.70        0    16.82    7.79   13.64        0
      262144         65536     float     sum     -1    19.48   13.46   23.55        0    19.44   13.48   23.59        0
      524288        131072     float     sum     -1    24.11   21.74   38.05        0    24.08   21.77   38.10        0
     1048576        262144     float     sum     -1    26.85   39.06   68.35        0    26.73   39.23   68.66        0
     2097152        524288     float     sum     -1    33.94   61.79  108.13        0    33.43   62.73  109.78        0
     4194304       1048576     float     sum     -1    48.12   87.17  152.54        0    47.62   88.08  154.14        0
     8388608       2097152     float     sum     -1    77.60  108.10  189.17        0    76.10  110.23  192.91        0
    16777216       4194304     float     sum     -1   134.80  124.46  217.81        0   133.35  125.82  220.18        0
    33554432       8388608     float     sum     -1   242.06  138.62  242.58        0   241.09  139.18  243.57        0
    67108864      16777216     float     sum     -1   399.11  168.15  294.26        0   402.01  166.93  292.13        0
   134217728      33554432     float     sum     -1   752.38  178.39  312.19        0   752.39  178.39  312.18        0
   268435456      67108864     float     sum     -1  1442.01  186.15  325.77        0  1443.55  185.95  325.42        0
   536870912     134217728     float     sum     -1  2856.30  187.96  328.93        0  2858.51  187.82  328.68        0
  1073741824     268435456     float     sum     -1  5661.67  189.65  331.89        0  5668.68  189.42  331.48        0
  2147483648     536870912     float     sum     -1  11260.5  190.71  333.74        0  11259.6  190.73  333.77        0
# Out of bounds values : 0 OK
# Avg bus bandwidth    : 103.523
#
```

在 ICN64 机器上执行多进程 16 卡测试，起 16 个 MPI 进程分布在两台机器上，每台机器 8 个进程，每个进程对应 1 张卡，数据量范围为 8B 到 2GB

```bash
$mpirun -np 16 -npernode 8 -H <ip1>:8,<ip2>:8 all_reduce_perf -t 1 -g 1 -d float -b 8 -e 2GB -f 2 -n 20 -w 5
# nThread 1 nGpus 1 minBytes 8 maxBytes 2147483648 offset <0>/<0> step: 2(factor) warmup iters: 5 iters: 20 redop: sum validation: 1 single_test: 0 test_buffer_kind: both elapsed_type: cpu_time average: MIN register: 0
#
# Using devices
#   Rank  0 Group  0 Pid 3657775 on ppu_node0 device  0 [0xc7] ZW-M890P
#   Rank  1 Group  0 Pid 3657776 on ppu_node0 device  1 [0xa3] ZW-M890P
#   Rank  2 Group  0 Pid 3657777 on ppu_node0 device  2 [0x7f] ZW-M890P
#   Rank  3 Group  0 Pid 3657778 on ppu_node0 device  3 [0x09] ZW-M890P
#   Rank  4 Group  0 Pid 3657779 on ppu_node0 device  4 [0x7e] ZW-M890P
#   Rank  5 Group  0 Pid 3657780 on ppu_node0 device  5 [0x08] ZW-M890P
#   Rank  6 Group  0 Pid 3657785 on ppu_node0 device  6 [0xc6] ZW-M890P
#   Rank  7 Group  0 Pid 3657797 on ppu_node0 device  7 [0xa2] ZW-M890P
#   Rank  8 Group  0 Pid 3718147 on ppu_node1 device  0 [0xc7] ZW-M890P
#   Rank  9 Group  0 Pid 3718305 on ppu_node1 device  1 [0xa3] ZW-M890P
#   Rank 10 Group  0 Pid 3718315 on ppu_node1 device  2 [0x7f] ZW-M890P
#   Rank 11 Group  0 Pid 3718317 on ppu_node1 device  3 [0x09] ZW-M890P
#   Rank 12 Group  0 Pid 3718318 on ppu_node1 device  4 [0x7e] ZW-M890P
#   Rank 13 Group  0 Pid 3718319 on ppu_node1 device  5 [0x08] ZW-M890P
#   Rank 14 Group  0 Pid 3718320 on ppu_node1 device  6 [0xc6] ZW-M890P
#   Rank 15 Group  0 Pid 3718321 on ppu_node1 device  7 [0xa2] ZW-M890P
#
#                                                              out-of-place                      in-place
#       size         count      type   redop   root   cpu_time   algbw  busbw   #wrong   cpu_time   algbw  busbw   #wrong
#        (B)    (elements)                              (us)    (GB/s)  (GB/s)             (us)    (GB/s)  (GB/s)
           8             2     float     sum     -1    52.22    0.00    0.00        0    51.73    0.00    0.00        0
          16             4     float     sum     -1    10.18    0.00    0.00        0     9.93    0.00    0.00        0
          32             8     float     sum     -1     9.58    0.00    0.01        0     9.72    0.00    0.01        0
          64            16     float     sum     -1     9.22    0.01    0.01        0     9.12    0.01    0.01        0
         128            32     float     sum     -1     9.69    0.01    0.02        0     9.74    0.01    0.02        0
         256            64     float     sum     -1    10.15    0.03    0.05        0     9.80    0.03    0.05        0
         512           128     float     sum     -1    10.29    0.05    0.09        0    10.07    0.05    0.10        0
        1024           256     float     sum     -1    10.13    0.10    0.19        0    10.14    0.10    0.19        0
        2048           512     float     sum     -1    10.27    0.20    0.37        0    10.25    0.20    0.37        0
        4096          1024     float     sum     -1    10.51    0.39    0.73        0    10.48    0.39    0.73        0
        8192          2048     float     sum     -1    12.04    0.68    1.28        0    12.03    0.68    1.28        0
       16384          4096     float     sum     -1    18.88    0.87    1.63        0    18.74    0.87    1.64        0
       32768          8192     float     sum     -1    19.71    1.66    3.12        0    19.82    1.65    3.10        0
       65536         16384     float     sum     -1    21.22    3.09    5.79        0    21.11    3.10    5.82        0
      131072         32768     float     sum     -1    23.84    5.50   10.31        0    23.78    5.51   10.33        0
      262144         65536     float     sum     -1    25.09   10.45   19.59        0    25.19   10.41   19.51        0
      524288        131072     float     sum     -1    26.93   19.47   36.50        0    26.77   19.58   36.72        0
     1048576        262144     float     sum     -1    30.70   34.16   64.05        0    30.56   34.31   64.33        0
     2097152        524288     float     sum     -1    38.89   53.93  101.12        0    39.01   53.77  100.81        0
     4194304       1048576     float     sum     -1   132.75   31.60   59.24        0   124.75   33.62   63.04        0
     8388608       2097152     float     sum     -1   143.03   58.65  109.96        0   138.86   60.41  113.27        0
    16777216       4194304     float     sum     -1   207.12   81.00  151.88        0   202.69   82.77  155.20        0
    33554432       8388608     float     sum     -1   350.55   95.72  179.47        0   350.43   95.75  179.53        0
    67108864      16777216     float     sum     -1   479.00  140.10  262.69        0   479.86  139.85  262.22        0
   134217728      33554432     float     sum     -1   814.65  164.75  308.91        0   818.00  164.08  307.65        0
   268435456      67108864     float     sum     -1  1558.98  172.19  322.85        0  1560.82  171.98  322.47        0
   536870912     134217728     float     sum     -1  3018.19  177.88  333.52        0  3021.51  177.68  333.16        0
  1073741824     268435456     float     sum     -1  6001.62  178.91  335.45        0  6001.98  178.90  335.43        0
  2147483648     536870912     float     sum     -1  11943.3  179.81  337.14        0  11959.1  179.57  336.69        0
# Out of bounds values : 0 OK
# Avg bus bandwidth    : 91.3739
#
```

平台扩展关联：PCCL-TESTS 面向张量并行或多实例 serving，不属于本次单卡比赛路径；`all_reduce_perf` 等基准只用于通用多卡平台研究。

## 3. 概念介绍

本章节介绍 PCCL 的核心使用方式，包括通信域创建、集合通信、点对点通信、组调用、错误处理、线程安全，以及 HGGC Stream、HGGC Graph、用户缓冲区注册、RAS 和 SDK 兼容性等内容。

### 3.1. 创建通信域

创建通信域时，需要为其中的每个 PPU device 分配一个唯一的 rank，取值范围为 0 到 n-1。同一个 PPU device 不能在同一个 PCCL 通信域中映射到多个 rank，否则可能导致程序退出。

当 rank 与 PPU device 的映射确定后，可以通过 [`pcclCommInitRank()`](#625-pcclcomminitrank)、[`pcclCommInitRankConfig()`](#627-pcclcomminitrankconfig) 或 [`pcclCommInitAll()`](#626-pcclcomminitall) 创建通信域对象。每个对象都绑定一个 rank 和一个 PPU device，后续通信操作都基于这些对象发起。

调用 [`pcclCommInitRank()`](#625-pcclcomminitrank) 之前，需要先生成一个唯一标识，用来让所有相关进程和线程确认自己属于同一个通信域。这个标识可通过 [`pcclGetUniqueId()`](#624-pcclgetuniqueid) 获取。

[`pcclGetUniqueId()`](#624-pcclgetuniqueid) 返回的 ID 需要通过 CPU 侧通信机制分发给所有参与的线程和进程。例如，可以直接把 ID 指针传给多个线程，或者借助 MPI、socket 等并行运行环境将其广播到其他进程。

如果是在单进程内使用，也可以直接调用 [`pcclCommInitAll()`](#626-pcclcomminitall) 一次性创建 n 个通信域对象。由于该接口只适用于单进程，因此不支持跨节点通信。可以把 `pcclCommInitAll()` 理解为对 [`pcclGetUniqueId()`](#624-pcclgetuniqueid) 和 [`pcclCommInitRank()`](#625-pcclcomminitrank) 的一层封装。

下面的代码给出了 `pcclCommInitAll()` 的一个简化实现：

```c
pcclResult_t pcclCommInitAll(pcclComm_t* comm, int ndev, const int* devlist) {
    pcclUniqueId Id;
    pcclGetUniqueId(&Id);
    pcclGroupStart();
    for (int i = 0; i < ndev; i++) {
        hggcSetDevice(devlist[i]);
        pcclCommInitRank(comm + i, ndev, Id, i);
    }
    pcclGroupEnd();
}
```

相关链接：

- [`pcclGetUniqueId()`](#624-pcclgetuniqueid)
- [`pcclCommInitRankConfig()`](#627-pcclcomminitrankconfig)

#### 3.1.1. 通信域配置

[`pcclCommInitRankConfig()`](#627-pcclcomminitrankconfig) 支持在创建 PCCL 通信域时显式指定配置项。

PCCL 支持的配置参数可参考 [`pcclConfig_t`](#666-pcclconfig_t)。

例如，可以把 `blocking` 设为 0，使 PCCL 调用以非阻塞方式执行；同时还可以配合其他参数进一步约束通信域行为。下面是一个简单示例：

```c
pcclConfig_t config = PCCL_CONFIG_INITIALIZER;
config.blocking = 0;
config.minCTAs = 16;
config.maxCTAs = 32;
config.netName = "Socket";
CHECK(pcclCommInitRankConfig(&comm, nranks, id, rank, &config));
do {
  CHECK(pcclCommGetAsyncError(comm, &state));
  // 处理外部事件、超时、进度等...
} while(state == pcclInProgress);
```

相关链接：[`pcclCommGetAsyncError()`](#6214-pcclcommgetasyncerror)

#### 3.1.2. 使用多个 pcclUniqueId 创建通信域

[`pcclCommInitRankScalable()`](#628-pcclcomminitrankscalable) 支持通过多个 pcclUniqueId 创建 PCCL 通信域。所有 PCCL rank 都必须传入完全一致的 pcclUniqueId 数组，包括内容一致、顺序一致。为了获得更好的性能，建议将这些 pcclUniqueId 尽量均匀地分配到各个 PCCL rank。

在实现上，每个 PCCL rank 主要基于单个 pcclUniqueId 建立通信，因此把 pcclUniqueId 均匀分摊到各个 rank 上通常更合适。

下面给出一种判断“哪些 PCCL rank 负责生成 pcclUniqueId”的实现方式：

```c
bool rankHasRoot(const int rank, const int nRanks, const int nIds) {
  const int rmr = nRanks % nIds;
  const int rpr = nRanks / nIds;
  const int rlim = rmr * (rpr+1);
  if (rank < rlim) {
    return !(rank % (rpr + 1));
  } else {
    return !((rank - rlim) % rpr);
  }
}
```

先把全部 rank 尽量平均地划分给多个 pcclUniqueId。前 `nRanks % nIds` 组会比后面的分组多 1 个 rank。每一组的起始 rank 负责创建对应的 pcclUniqueId，所以该函数只会在这些起始 rank 上返回 `true`。

以 7 个 PCCL rank 对应 3 个 pcclUniqueId 为例，这 7 个 rank 可以分成 `0-2`、`3-4` 和 `5-6` 三组。这样，rank 0、3、5 分别作为各组的起始 rank 创建 pcclUniqueId，其余 rank 返回 `false`。

需要注意的是，只有第一个 pcclUniqueId 会用于生成通信域哈希 ID。日志中也是通过这个 ID 来标识通信域的。

相关链接：[`pcclCommInitRankScalable()`](#628-pcclcomminitrankscalable)

#### 3.1.3. 缩小通信域

[`pcclCommShrink()`](#6210-pcclcommshrink) 可用于在现有通信域的基础上移除部分 rank，并创建一个新的通信域。这个接口适合用于需要把某些 PPU device 或节点排除出集合通信的场景，例如故障恢复，或者动态调整资源使用范围。

下面的示例演示了一个常见场景：把 rank 1 从当前通信域中移除，并在剩余 rank 上创建新的通信域。

```c
int excludeRanks[] = {1};   // 需要移出的 rank 列表
int excludeCount = 1;       // 列表中的 rank 数量
pcclComm_t newcomm;

// 只有保留在新通信域中的 rank 才参与 shrink
if (myRank != 1) {
  pcclResult_t res = pcclCommShrink(comm, excludeRanks, excludeCount, &newcomm, NULL, PCCL_SHRINK_DEFAULT);
  if (res != pcclSuccess) {
    // 按需处理错误
  }
  // 后续集合操作改为在 newcomm 上执行
  // ...
  // 使用结束后释放新的通信域
  pcclCommDestroy(newcomm);
}
```

如果是在通信错误后执行恢复，也可以使用错误处理模式：

```c
if (myRank != 1) {
  // 在错误恢复场景下，使用 PCCL_SHRINK_ABORT 中止父通信域上的操作
  // 如果父通信域上可能还有未完成操作，这种模式也更合适
  pcclResult_t res = pcclCommShrink(comm, excludeRanks, excludeCount, &newcomm, NULL, PCCL_SHRINK_ABORT);
  // ...
}
```

使用 [`pcclCommShrink()`](#6210-pcclcommshrink) 时需要注意：

1. 只有保留在新通信域中的 rank 才应调用 [`pcclCommShrink()`](#6210-pcclcommshrink)。
2. 位于排除列表中的 rank 不应调用该函数。
3. 新通信域中的 rank 会重新编号，并保持连续。
4. 如果需要同步创建多个新通信域，可以配合 [`pcclGroupStart()`](#651-pcclgroupstart) / [`pcclGroupEnd()`](#652-pcclgroupend) 一起使用。

相关链接：[`pcclCommShrink()`](#6210-pcclcommshrink)

#### 3.1.4. 创建更多通信域

[`pcclCommSplit()`](#629-pcclcommsplit) 可用于在现有通信域的基础上创建新的通信域。它既可以把原通信域拆分成多个子通信域，也可以复制原通信域，或者只保留其中一部分 rank 来生成新通信域。

[`pcclCommSplit()`](#629-pcclcommsplit) 需要由原通信域中的所有 rank 一起调用。如果某些 rank 不属于任何子通信域，它们仍然需要参与调用，只是要把 `color` 设置为 `PCCL_SPLIT_NOCOLOR`。

新生成的通信域会继承父通信域的配置，例如非阻塞模式。如果父通信域本身以非阻塞方式运行，那么在需要中止 [`pcclCommSplit()`](#629-pcclcommsplit) 时，可以先对父通信域调用 [`pcclCommAbort()`](#6213-pcclcommabort)，再对返回的新通信域调用同样的接口。这么做的原因是：无论在父通信域还是子通信域上继续操作，都有可能出现挂起。

下面的代码演示了如何复制一个已有通信域：

```c
int rank;
pcclCommUserRank(comm, &rank);
pcclCommSplit(comm, 0, rank, &newcomm, NULL);
```

下面的示例将原通信域按 rank 分成两个子通信域：

```c
int rank, nranks;
pcclCommUserRank(comm, &rank);
pcclCommCount(comm, &nranks);
pcclCommSplit(comm, rank/(nranks/2), rank%(nranks/2), &newcomm, NULL);
```

下面的示例只保留前 2 个 rank，并基于它们创建一个新的通信域，其余 rank 不参与拆分：

```c
int rank;
pcclCommUserRank(comm, &rank);
pcclCommSplit(comm, rank<2 ? 0 : PCCL_SPLIT_NOCOLOR, rank, &newcomm, NULL);
```

相关链接：

- [`pcclCommSplit()`](#629-pcclcommsplit)

#### 3.1.5. 终止通信域

[`pcclCommFinalize()`](#6211-pcclcommfinalize) 会把通信域的状态从 *pcclSuccess* 切换为 *pcclInProgress*，随后在后台完成剩余操作，并与其他 rank 同步——这些 rank 此时可能仍在使用相关资源执行通信。与该通信域相关的未完成操作和网络资源都会在 [`pcclCommFinalize()`](#6211-pcclcommfinalize) 过程中被清理和释放。等所有 PCCL 操作都完成后，通信域状态会重新回到 *pcclSuccess*。用户可以通过 [`pcclCommGetAsyncError()`](#6214-pcclcommgetasyncerror) 查询当前状态。如果该通信域被配置为非阻塞模式，那么这里也是非阻塞调用；否则就是阻塞调用。

相关链接：[`pcclCommFinalize()`](#6211-pcclcommfinalize)

#### 3.1.6. 销毁通信域

通信域终止后，下一步就是释放相关资源，包括通信域对象本身。与通信域关联的本地资源可以通过 [`pcclCommDestroy()`](#6212-pcclcommdestroy) 释放。如果通信域当前处于 *pcclSuccess* 状态，那么 [`pcclCommDestroy()`](#6212-pcclcommdestroy) 保证是非阻塞的；否则调用可能发生阻塞。无论哪种情况，[`pcclCommDestroy()`](#6212-pcclcommdestroy) 在返回时都会完成资源释放，返回之后就不应再访问该通信域。

相关链接：[`pcclCommDestroy()`](#6212-pcclcommdestroy)

### 3.2. 错误处理与通信域中止

所有 PCCL 调用都会返回一个 PCCL 错误码，见下表。

下表概括了各类错误的含义以及建议的处理方式，后面会分别展开说明。

PCCL 错误：

| 错误 | 描述 | 解决方式 | 错误处理 | 组调用影响范围 |
| --- | --- | --- | --- | --- |
| pcclSuccess | 无错误 | 无 | 无 | 无 |
| pcclUnhandledHggcError | HGGC 调用期间的错误 (1) | HGGC 配置 | 通信域中止 (5) | 全局 (6) |
| pcclSystemError | 系统调用期间的错误 (1) | 系统配置 | 通信域中止 (5) | 全局 (6) |
| pcclInternalError | PCCL 内部错误 (2) | 修复 PCCL (2) | 通信域中止 (5) | 全局 (6) |
| pcclInvalidArgument | PCCL 调用参数无效 (3) | 修复应用程序 | 无 (3) | 个别 (3) |
| pcclInvalidUsage | PCCL 使用方式不正确 (4) | 修复应用程序 | 通信域中止 (5) | 全局 (6) |
| pcclRemoteError | 远端错误 (6) | 检查网络或远端进程 | 通信域中止 (5) | 全局 (6) |
| pcclInProgress | PCCL 调用仍在进行中 | 轮询等待完成 | 无 | 无 |

(1) `pcclUnhandledHggcError` 和 `pcclSystemError` 表示 PCCL 调用外部组件失败，导致当前 PCCL 操作失败。错误信息通常会指出需要检查哪个组件，以及大致的排查方向。

(2) `pcclInternalError` 通常表示 PCCL 本身存在 bug。

(3) `pcclInvalidArgument` 表示传入的参数值不合法，例如传入 `NULL` 指针，或者参数超出允许范围。出现该错误时，本次 PCCL 调用不会产生任何副作用，组状态保持不变，通信域本身也仍然可用。应用程序既可以调用 `pcclCommAbort`，也可以按“本次调用未发生”来继续执行。若该错误出现在组调用内部，会立即针对对应的那次 PCCL 调用返回；而由于 `pcclGroupEnd` 本身不接收参数，因此这类错误最终也会通过 `pcclGroupEnd` 返回给用户。

(4) `pcclInvalidUsage` 表示运行时条件不满足，导致 PCCL API 被错误使用。

(5) 这几类错误对通信域来说都是致命的。要恢复运行，应用程序需要调用 `pcclCommAbort` 中止当前通信域，然后重新创建。

(6) 在组调用中，运行时错误总是通过 `pcclGroupEnd` 报告，并会影响该组中的所有操作——无论这些操作已经完成、尚未完成，还是处于中间状态。应用程序需要对组内涉及的所有通信域调用 `pcclCommAbort`。

#### 3.2.1. 异步错误与错误处理

某些通信错误，尤其是网络错误，会通过 `pcclCommGetAsyncError` 上报。出现异步错误后，相关操作通常不会再继续推进，也不会完成。因此，一旦检测到异步错误，就应尽快中止当前操作，并通过 `pcclCommAbort` 销毁通信域。

在等待 PCCL 操作结束时，应用程序应主动轮询 `pcclCommGetAsyncError`，并在发生错误时及时销毁通信域。

下面的示例展示了如何在不调用 `hggcStreamSynchronize` 的情况下，等待 PCCL 操作完成并轮询异步错误。

```c
int pcclStreamSynchronize(hggcStream_t stream, pcclComm_t comm) {
  hggcError_t hggcErr;
  pcclResult_t pcclErr, pcclAsyncErr;
  while (1) {
    hggcErr = hggcStreamQuery(stream);
    if (hggcErr == hggcSuccess)
      return 0;

    if (hggcErr != hggcErrorNotReady) {
      printf("HGGC Error : hggcStreamQuery returned %d\n", hggcErr);
      return 1;
    }

    pcclErr = pcclCommGetAsyncError(comm, &pcclAsyncErr);
    if (pcclErr != pcclSuccess) {
      printf("PCCL Error : pcclCommGetAsyncError returned %d\n", pcclErr);
      return 1;
    }

    if (pcclAsyncErr != pcclSuccess) {
      // 发生异步错误，停止当前操作并销毁通信域
      pcclErr = pcclCommAbort(comm);
      if (pcclErr != pcclSuccess)
        printf("PCCL Error : pcclCommAbort returned %d\n", pcclErr);
      // 调用者可以选择直接退出，或重新创建通信域后继续
      return 2;
    }

    // 这里主动让出 CPU，便于其他线程（包括 PCCL 线程）继续运行。
    sched_yield();
  }
}
```

相关链接：

- [pcclCommAbort()](#6213-pcclcommabort)

#### 3.2.2. 容错机制

PCCL 提供了容错能力，用于帮助应用程序从致命错误中恢复，例如网络故障、节点故障或进程故障。出现这类问题后，应用程序通常需要调用 `pcclCommAbort` 释放通信域相关资源，再重新创建新的通信域继续执行。

如果需要更复杂的恢复流程，也可以结合 `PCCL_SHRINK_ABORT` 使用 `pcclCommShrink`，把故障的 rank 从原通信域中移除，并基于剩余 rank 创建新的通信域，同时尽量安全地处理尚未完成的操作。这种方式尤其适合只有部分 rank 出现故障的分布式场景。

为了能够安全地中止 PCCL 通信域，PCCL 要求应用程序将通信域设为非阻塞模式，并确保在调用 `pcclCommAbort` 时，没有其他线程正在执行任何 PCCL 调用。启用非阻塞模式后，除 `pcclCommDestroy` 和 `pcclCommAbort` 之外，其余 PCCL 调用都会以非阻塞方式返回，因此无论是在初始化阶段、通信阶段，还是通信域结束阶段，都可以调用 `pcclCommAbort`。相反，如果通信域处于阻塞模式，线程可能会因为网络错误卡在某个 PCCL 调用内部，最终导致整个通信域长期挂起，甚至无法恢复。

为了正确执行中止流程，当通信域中的任意 rank 出现故障时，例如发生段错误，其他 rank 也需要调用 `pcclCommAbort` 来中止各自的 PCCL 通信域。至于何时中止、是否重建通信域以及如何恢复，通常由应用程序自行决定。下面的示例展示了如何以非阻塞方式初始化和拆分通信域，从而支持在任意时刻中止：

```c
bool globalFlag;
bool abortFlag = false;
pcclConfig_t config = PCCL_CONFIG_INITIALIZER;
/* 将通信域设置为非阻塞 */
config.blocking = 0;
CHECK(pcclCommInitRankConfig(&comm, nRanks, id, myRank, &config));
do {
  CHECK(pcclCommGetAsyncError(comm, &state));
} while(state == pcclInProgress && checkTimeout() != true);

if (checkTimeout() == true || state != pcclSuccess) abortFlag = true;

/* 在所有健康的 rank 之间同步 abortFlag。 */
reportErrorGlobally(abortFlag, &globalFlag);

if (globalFlag) {
  /* 超时或初始化失败：每个 rank 都需要中止并重新启动。 */
  pcclCommAbort(comm);
  /* 重新启动 PCCL；这是用户实现的函数，可能包括
   * 资源清理和 pcclCommInitRankConfig() 来创建新的通信域。 */
  restartPCCL(&comm);
}

/* 非阻塞通信域拆分。 */
CHECK(pcclCommSplit(comm, color, key, &childComm, &config));
do {
  CHECK(pcclCommGetAsyncError(comm, &state));
} while(state == pcclInProgress && checkTimeout() != true);

if (checkTimeout() == true || state != pcclSuccess) abortFlag = true;

/* 在所有健康的 rank 之间同步 abortFlag。 */
reportErrorGlobally(abortFlag, &globalFlag);

if (globalFlag) {
  pcclCommAbort(comm);
  /* 如果 childComm 不是 PCCL_COMM_NULL，用户也应在此中止子通信域
   * 以回收资源。 */
  if (childComm != PCCL_COMM_NULL) pcclCommAbort(childComm);
  restartPCCL(&comm);
}
/* 应用程序工作负载 */
```

`checkTimeout` 需要由用户自行实现，用于决定应用程序最多等待 PCCL 初始化多长时间。当然，除了超时机制，也可以使用其他方式来判断是否发生错误。类似的处理思路同样适用于 PCCL 的终止过程。

相关链接：

- [pcclCommShrink()](#6210-pcclcommshrink)
- [pcclCommSplit()](#629-pcclcommsplit)
- [pcclCommDestroy()](#6212-pcclcommdestroy)

### 3.3. 集合通信

集合通信操作需要在每个 rank 上调用，也就是每个 PPU 都要参与调用，并且各 rank 需要使用相同的 `count` 和相同的数据类型，才能共同组成一次完整的集合通信。否则可能出现未定义行为，包括挂起、崩溃或数据损坏。

#### 3.3.1. AllReduce

AllReduce 会对多个 PPU 上的数据执行归约操作，例如 `sum`、`min`、`max`，并将归约结果写入每个 rank 的接收缓冲区。

以 k 个 rank 之间的 `sum` AllReduce 为例：每个 rank 提供一个包含 N 个元素的输入数组，最终每个 rank 都会得到一个同样包含 N 个元素的结果数组，其中 `out[i] = in0[i] + in1[i] + ... + in(k-1)[i]`。

![AllReduce 操作：每个 rank 接收所有 rank 输入值的归约结果](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124973548/2aed8a585e40160a08c589507a36b03b/allreduce.svg)

相关链接：[pcclAllReduce()](#631-pcclallreduce)

#### 3.3.2. AllGather

在 AllGather 中，K 个 rank 中的每一个都会提供 N 个值，最终每个 rank 都会得到一份大小为 `K*N` 的输出，其中包含所有 rank 的输入数据，并按 rank 顺序依次排列。

![AllGather 操作：所有 rank 从所有 rank 收集数据](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124973280/2f357abedf302db913e2495d89101803/allgather.svg)

相关链接：[pcclAllGather()](#632-pcclallgather)

#### 3.3.3. Broadcast

Broadcast 会把 root rank 上包含 N 个元素的缓冲区复制到所有 rank。

![Broadcast 操作：所有 rank 从 root rank 接收数据](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124974002/2cce1ff7c4a8701da03c84329cd845d1/broadcast.svg)

重要提示：`root` 参数表示的是 rank，而不是 PPU 编号，因此结果会受到 rank 与 PPU 映射关系的影响。

相关链接：[pcclBroadcast()](#633-pcclbroadcast)

#### 3.3.4. ReduceScatter

ReduceScatter 的归约过程与 Reduce 类似，不同的是结果不会集中写到单个 rank，而是会被拆分成大小相同的数据块，分发给各个 rank。每个 rank 会根据自己的 rank 索引获得对应的一块结果。

由于数据块的分配顺序由 rank 决定，因此 ReduceScatter 也会受到 rank 与 PPU 映射关系的影响。

![ReduceScatter 操作：输入值在各 rank 间进行归约，每个 rank 接收结果的一部分](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124974709/9c3a77ad9eb9f314537f9c8b21a3e1d5/reducescatter.svg)

相关链接：[pcclReduceScatter()](#634-pcclreducescatter)

#### 3.3.5. Scatter

Scatter 会将 root rank 上总计 `N*K` 个值分发到 K 个 rank，每个 rank 接收其中的 N 个值。

![Scatter 操作：root rank 将数据分发到所有 rank](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124974962/7a7708c7aae6238dc370ab71606bf1a5/scatter.svg)

重要提示：`root` 参数表示的是 rank，而不是 PPU 编号，因此结果会受到 rank 与 PPU 映射关系的影响。

相关链接：[pcclScatter()](#635-pcclscatter)

#### 3.3.6. AlltoAll

在 K 个 rank 参与的 AlltoAll 操作中，每个 rank 都会提供一个大小为 `K*N` 的输入缓冲区。其中第 j 个、长度为 N 的数据块会发送给目标 rank j。与此同时，每个 rank 也会接收一个大小为 `K*N` 的输出缓冲区，其中第 i 个、长度为 N 的数据块来自源 rank i。

![AlltoAll 操作：每个 rank 向所有其他 rank 发送不同的数据，并从每个 rank 接收不同的数据](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124973782/b15bad993583ff98c3cd6ea717c5d54b/alltoall.svg)

相关链接：[pcclAlltoAll()](#636-pcclalltoall)

#### 3.3.7. Reduce

Reduce 与 AllReduce 的归约过程相同，不同之处在于结果只会写入 root rank 的接收缓冲区。

以 k 个 rank 之间的 `sum` Reduce 为例：每个 rank 提供一个包含 N 个元素的输入数组，root rank 最终接收一个同样包含 N 个元素的结果数组，其中 `out[i] = in0[i] + in1[i] + ... + in(k-1)[i]`。

![Reduce 操作：仅 root rank 接收所有 rank 输入值的归约结果](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124974451/e33bcbaaaacb728424197918cf777882/reduce.svg)

重要提示：`root` 参数表示的是 rank，而不是 PPU 编号，因此结果会受到 rank 与 PPU 映射关系的影响。

相关链接：[pcclReduce()](#637-pcclreduce)

#### 3.3.8. Gather

Gather 会从 K 个 rank 中各收集 N 个值，并把结果汇总到 root rank 的输出缓冲区中，输出总大小为 `K*N`。

![Gather 操作：root rank 从所有 rank 收集数据](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124974241/d7e3528716600d5a8df06c53db45eaab/gather.svg)

重要提示：`root` 参数表示的是 rank，而不是 PPU 编号，因此结果会受到 rank 与 PPU 映射关系的影响。

相关链接：[pcclGather()](#638-pcclgather)

### 3.4. HGGC Stream 语义

每个 PCCL 调用都需要关联一个 stream，它作为集合通信函数的最后一个参数传入。当操作已经成功加入指定 stream 的执行队列后，PCCL 调用就会返回；如果失败，则返回对应的错误码。后续集合通信会在 HGGC 上异步执行。操作状态可以沿用标准 HGGC 语义来判断，例如调用 `hggcStreamSynchronize`，或配合 HGGC event 进行同步。

#### 3.4.1. 在同一组调用中混用多个 stream

PCCL 允许在同一个 `pcclGroupStart()` / `pcclGroupEnd()` 组内使用多个 stream。这样做会在 PCCL kernel 真正启动前，先在这些 stream 之间建立依赖关系，并让它们一直等待到 PCCL kernel 执行完成。

可以把这种行为理解为：同一组 PCCL 操作分别提交到了各个 stream 上，但由于它们属于同一次组调用，因此这些 stream 之间会形成一个全局同步点。

### 3.5. 组调用

组调用接口（`pcclGroupStart` / `pcclGroupEnd`）可用于将多个 PCCL 调用合并为一次提交，主要有三个用途：在单线程中管理多个 PPU 以避免死锁、聚合多个通信操作以提升性能，以及合并多个点对点发送/接收操作（参见点对点通信）。这三种用法可以组合使用，但有一个例外：对 [pcclCommInitRank()](#625-pcclcomminitrank) 的调用不能与其他调用合并。

#### 3.5.1. 从单线程管理多个 PPU

当单个线程需要管理多个 PPU 时，必须使用组调用。原因是每个 PCCL 调用都可能阻塞，等待其他线程或其他 rank 到达同一阶段后，才能将操作真正提交到对应的 stream。因此，像下面这样遍历多个 PPU 的简单循环，可能会在第一次调用时就阻塞住，等待其他调用到达：

```c
for (int dev = 0; dev < nLocalDevs; dev++) {
  pcclAllReduce(..., comms[dev], streams[dev]);
}
```

为了表明这些调用属于同一个集合操作，需要使用 `pcclGroupStart` 和 `pcclGroupEnd`：

```c
pcclGroupStart();
for (int dev = 0; dev < nLocalDevs; dev++) {
  pcclAllReduce(..., comms[dev], streams[dev]);
}
pcclGroupEnd();
```

这样，PCCL 就会把 `pcclGroupStart` 和 `pcclGroupEnd` 之间的所有调用视为一次对多个 PPU 的整体调用。

> **注意**：在组内调用通信接口时，类似 `pcclAllReduce` 这样的操作可能会在尚未真正入队到 stream 时就返回。因此，`hggcStreamSynchronize` 这类 stream 同步操作只能在 `pcclGroupEnd` 返回之后调用。

当一个线程管理多个 PPU 并创建通信域时，同样必须使用组调用：

```c
pcclGroupStart();
for (int dev = 0; dev < nLocalDevs; dev++) {
  hggcSetDevice(devices[dev]);
  pcclCommInitRank(comms + dev, nranks, commId, ranks[dev]);
}
pcclGroupEnd();
```

相关链接：

- [pcclGroupEnd()](#652-pcclgroupend)

#### 3.5.2. 聚合操作

组调用还可以用于把多个集合通信操作合并为单次 PCCL 操作，从而减少启动开销，多次操作只会引入一次启动延迟。需要注意，初始化函数之间不能聚合，初始化函数也不能与通信函数聚合。

要实现集合操作聚合，只需在 `pcclGroupStart` 和 `pcclGroupEnd` 之间连续发起多次 PCCL 调用即可。

下面的示例中，一个 broadcast 和两个 allReduce 会作为一次 PCCL 启动统一发起：

```c
pcclGroupStart();
pcclBroadcast(sendBuff1, recvBuff1, count1, datatype, root, comm, stream);
pcclAllReduce(sendBuff2, recvBuff2, count2, datatype, comm, stream);
pcclAllReduce(sendBuff3, recvBuff3, count3, datatype, comm, stream);
pcclGroupEnd();
```

聚合可以与多 PPU 调用结合使用，也可以在同一次组启动中混用不同通信域。当同时使用多 PPU 启动和聚合时，`pcclGroupStart` 和 `pcclGroupEnd` 既可以只在最外层使用一次，也可以在每一层都写上。下面的示例把多个 PPU、多个层上的 allReduce 操作一起分组：

```c
pcclGroupStart();
for (int layer = 0; layer < nLayers; layer++) {
  pcclGroupStart();
  for (int ppu = 0; ppu < nPpus; ppu++) {
    pcclAllReduce(sendBuffs[ppu] + offsets[layer], recvBuffs[ppu] + offsets[layer], counts[layer], datatypes[layer], comms[ppu], streams[ppu]);
  }
  pcclGroupEnd();
}
pcclGroupEnd();
```

> **注意**：PCCL 操作只会在最后一次调用 `pcclGroupEnd` 时统一启动。因此，上面示例中 for 循环里的 `pcclGroupStart` 和 `pcclGroupEnd` 实际上不是必需的，不会带来额外效果。

相关链接：

- [pcclGroupEnd()](#652-pcclgroupend)

#### 3.5.3. 组操作的顺序语义

虽然 PCCL 允许在一个组内一次性发起多个不同操作，但用户仍然必须保证：不同 PPU 上发起操作的顺序完全一致，不论这些操作使用的是不是同一个通信域。

例如，下面的代码就是正确的顺序。在这个示例中，`comm0` 和 `comm1` 是两个相互独立但成员相同的通信域，均包含 rank 0 和 rank 1。

```c
// RANK0/PPU0/Process0:
pcclGroupStart();
pcclBroadcast(sendBuff1, recvBuff1, count1, datatype, root, comm0, stream);
pcclAllReduce(sendBuff2, recvBuff2, count2, datatype, comm0, stream);
pcclAllReduce(sendBuff3, recvBuff3, count3, datatype, comm0, stream);
pcclAllReduce(sendBuff4, recvBuff4, count4, datatype, comm1, stream);
pcclGroupEnd();

// RANK1/PPU1/Process1:
pcclGroupStart();
pcclBroadcast(sendBuff1, recvBuff1, count1, datatype, root, comm0, stream);
pcclAllReduce(sendBuff2, recvBuff2, count2, datatype, comm0, stream);
pcclAllReduce(sendBuff3, recvBuff3, count3, datatype, comm0, stream);
pcclAllReduce(sendBuff4, recvBuff4, count4, datatype, comm1, stream);
pcclGroupEnd();
```

如果任意一端改变了操作顺序，就可能得到错误结果，甚至导致程序挂起。下面两个示例都属于错误用法：

```c
// RANK0/PPU0/Process0:
pcclGroupStart();
pcclBroadcast(sendBuff1, recvBuff1, count1, datatype, root, comm0, stream);
pcclAllReduce(sendBuff3, recvBuff3, count3, datatype, comm0, stream); // WRONG: reversed order
pcclAllReduce(sendBuff2, recvBuff2, count2, datatype, comm0, stream); // WRONG: reversed order
pcclAllReduce(sendBuff4, recvBuff4, count4, datatype, comm1, stream);
pcclGroupEnd();

// RANK1/PPU1/Process1:
pcclGroupStart();
pcclBroadcast(sendBuff1, recvBuff1, count1, datatype, root, comm0, stream);
pcclAllReduce(sendBuff2, recvBuff2, count2, datatype, comm0, stream); // WRONG: reversed order
pcclAllReduce(sendBuff3, recvBuff3, count3, datatype, comm0, stream); // WRONG: reversed order
pcclAllReduce(sendBuff4, recvBuff4, count4, datatype, comm1, stream);
pcclGroupEnd();
```

```c
// RANK0/PPU0/Process0:
pcclGroupStart();
pcclAllReduce(sendBuff4, recvBuff4, count4, datatype, comm1, stream); // WRONG: reversed order
pcclBroadcast(sendBuff1, recvBuff1, count1, datatype, root, comm0, stream);
pcclAllReduce(sendBuff2, recvBuff2, count2, datatype, comm0, stream);
pcclAllReduce(sendBuff3, recvBuff3, count3, datatype, comm0, stream);
pcclGroupEnd();

// RANK1/PPU1/Process1:
pcclGroupStart();
pcclBroadcast(sendBuff1, recvBuff1, count1, datatype, root, comm0, stream);
pcclAllReduce(sendBuff2, recvBuff2, count2, datatype, comm0, stream);
pcclAllReduce(sendBuff3, recvBuff3, count3, datatype, comm0, stream);
pcclAllReduce(sendBuff4, recvBuff4, count4, datatype, comm1, stream); // WRONG: reversed order
pcclGroupEnd();
```

#### 3.5.4. 非阻塞组操作

如果通信域通过 `pcclCommInitRankConfig` 配置为非阻塞模式，那么组调用也会相应变为异步。在这种情况下，即使 `pcclGroupEnd()` 已经返回，也不代表 PCCL 通信 kernel 已经提交到 HGGC stream。

- 如果 `pcclGroupEnd()` 返回 `pcclSuccess`，表示 PCCL kernel 已经提交到 stream。
- 如果返回 `pcclInProgress`，表示 PCCL kernel 仍在后台提交到 stream。

因此，在调用 `hggcStreamSynchronize` 之类的 HGGC 接口前，用户需要先确保通信域状态已经变为 `pcclSuccess`：

```c
pcclGroupStart();
for (int ppu = 0; ppu < nPpus; ppu++) {
  pcclAllReduce(sendBuffs[ppu] + offsets[layer], recvBuffs[ppu] + offsets[layer], counts[layer], datatypes[layer], comms[ppu], streams[ppu]);
}
ret = pcclGroupEnd();

if (ret == pcclInProgress) {
  for (int ppu = 0; ppu < nPpus; ppu++) {
    do {
      pcclCommGetAsyncError(comms[ppu], &state);
    } while (state == pcclInProgress);
  }
} else if (ret == pcclSuccess) {
  /* Successfully issued */
  printf("PCCL kernel issue succeeded\n");
} else {
  /* Errors happen */
  reportErrorAndRestart();
}

for (int ppu = 0; ppu < nPpus; ppu++) {
  hggcStreamSynchronize(streams[ppu]);
}
```

相关链接：

- [pcclCommGetAsyncError()](#6214-pcclcommgetasyncerror)

### 3.6. 点对点通信

#### 3.6.1. 双边通信

点对点通信可用于表达 rank 之间任意形式的数据交换。一次完整的点对点通信需要两个 PCCL 调用配合完成：一个 rank 调用 `pcclSend()`，另一个 rank 调用对应的 `pcclRecv()`，并且双方的 `count` 和数据类型需要保持一致。

如果需要构造更复杂的通信模式，可以把多个面向不同对端的 `pcclSend()` 和 `pcclRecv()` 调用放进同一个 `pcclGroupStart()` / `pcclGroupEnd()` 组中。例如，一对多（scatter）、多对一（gather）、全对全（all-to-all），都可以这样实现。

组内的点对点调用会一直等到整组调用完成后才一起结束，但组内各个调用在语义上仍可视为彼此独立，因此它们之间不应互相等待。所以凡是需要并发执行的调用，都应尽量放到同一个组里，以避免死锁。唯一的例外是：如果组内有多个点对点调用针对的是*同一个*对端，那么这些调用会按顺序执行。

下面列出几种并行程序中常见的点对点通信模式。PCCL 允许不同 rank 使用不同大小、不同数据类型以及不同缓冲区。

#### 3.6.2. Sendrecv

在 MPI 中，sendrecv 表示两个 rank 同时进行发送和接收，也就是双向交换数据。用 PCCL 表达时，可以把 `pcclSend` 和 `pcclRecv` 放进同一个组里：

```c
pcclGroupStart();
pcclSend(sendbuff, sendcount, sendtype, peer, comm, stream);
pcclRecv(recvbuff, recvcount, recvtype, peer, comm, stream);
pcclGroupEnd();
```

#### 3.6.3. Scatter

如果要从一个 root rank 向多个 rank 分发数据，可以把所有 send 和 recv 操作放在同一个组中：

```c
pcclGroupStart();
if (rank == root) {
  for (int r=0; r<nranks; r++)
    pcclSend(sendbuff[r], size, type, r, comm, stream);
}
pcclRecv(recvbuff, size, type, root, comm, stream);
pcclGroupEnd();
```

#### 3.6.4. Gather

反过来，如果要把多个 rank 的数据汇总到一个 root rank，也可以使用同样的方式表达：

```c
pcclGroupStart();
if (rank == root) {
  for (int r=0; r<nranks; r++)
    pcclRecv(recvbuff[r], size, type, r, comm, stream);
}
pcclSend(sendbuff, size, type, root, comm, stream);
pcclGroupEnd();
```

#### 3.6.5. All-to-All

全对全通信可以通过对所有对端依次发起 send/recv，并把这些调用合并到同一个组中来实现：

```c
pcclGroupStart();
for (int r=0; r<nranks; r++) {
  pcclSend(sendbuff[r], sendcount, sendtype, r, comm, stream);
  pcclRecv(recvbuff[r], recvcount, recvtype, r, comm, stream);
}
pcclGroupEnd();
```

### 3.7. 线程安全

PCCL 原语通常不是线程安全的，但支持重入。在多线程环境下，多个线程不能并行地向同一个通信域发起 PCCL 操作；同样，多个线程也不应并行地向位于同一个 PPU device 上的不同通信域发起 PCCL 操作（参见创建通信域）。如果子通信域和父通信域共享资源，也就是通过 [`pcclConfig_t`](#666-pcclconfig_t) 中的 `splitShare` 配置建立关联，那么也不能并行地向父子通信域发起 PCCL 操作。

如果能够保证任一时刻只有一个线程在操作某个通信域，那么从多个线程轮流使用同一个通信域是安全的。不过，对于任何组调用，用户都需要确保整组 PCCL 操作由同一个线程发起。

下面给出一个简单的线程安全示例。这里两个线程按顺序执行，因此同一时刻只有一个线程访问该通信域。

```c
// 线程 0：
pcclConfig_t config = PCCL_CONFIG_INITIALIZER;
config.blocking = 0;
hggcSetDevice(0);
pcclCommInitRankConfig(&comm, nranks, id, rank, &config);
pcclGroupStart();
pcclAllReduce(sendbuff0, recvbuff0, count0, datatype, redOp, comm, stream);
pcclAllReduce(sendbuff1, recvbuff1, count1, datatype, redOp, comm, stream);
pcclGroupEnd();
thread_exit();

// 线程 1：
pcclResult_t state = pcclSuccess;
// 等待线程 0 发起的 allReduce 操作完成
do {
  pcclCommGetAsyncError(comm, &state);
} while (state == pcclInProgress);
assert(state == pcclSuccess);
pcclAllReduce(sendbuff2, recvbuff2, count2, datatype, redOp, comm, stream);
do {
  pcclCommGetAsyncError(comm, &state);
} while (state == pcclInProgress);
assert(state == pcclSuccess);
```

另一种常见做法是：由一个线程发起成组的 PCCL 操作，再由其他线程分别轮询各自通信域的状态，如下所示。

```c
// 线程 0：
pcclConfig_t config = PCCL_CONFIG_INITIALIZER;
config.blocking = 0;
pcclGroupStart();
for (int i = 0; i < nPPUs; i++) {
  hggcSetDevice(i);
  pcclCommInitRankConfig(&comms[i], nranks, id, ranks[i], &config);
}
pcclGroupEnd();

// 线程 0/1/2/3：
pcclResult_t state = pcclSuccess;
// 等待线程 0 发起的 init 操作完成
do {
  pcclCommGetAsyncError(comms[thread_id], &state);
} while (state == pcclInProgress);
assert(state == pcclSuccess);
pcclAllReduce(sendbuff, recvbuff, count, datatype, redOp, comms[thread_id], stream);
do {
  pcclCommGetAsyncError(comms[thread_id], &state);
} while (state == pcclInProgress);
assert(state == pcclSuccess);
```

### 3.8. 使用 HGGC Graphs 捕获 PCCL 通信算子

PCCL 操作可以被 HGGC Graph 捕获。

HGGC Graph 提供了一种用图来组织工作流的方法，而不是把每一步都作为独立操作逐个启动。这样可以通过一次 CPU 侧发起，驱动多个 PPU 操作执行，从而减少启动开销。

PCCL 的集合通信、P2P 通信以及组操作都支持 HGGC Graph 捕获。

某次操作是否处于 graph 捕获过程中，属于该操作的集合属性，因此所有参与该次启动的 rank 都必须保持一致。对集合通信来说，这意味着通信域内所有 rank 都要一致；对点对点通信来说，则至少要求发送方和接收方一致。对于包含已捕获 PCCL 操作的 graph，后续通过 `hggcGraphLaunch()` 启动时，会被视为针对与捕获阶段相同 rank 集合的一次集合操作，因此这些 rank 都必须使用由同一次捕获生成的 graph。

下面的示例展示了如何在 HGGC Graph 中同时捕获计算 kernel 和 PCCL 操作：

```c
hggcGraph_t graph;
hggcStreamBeginCapture(stream);
kernel_A<<< ..., stream >>>(...);
kernel_B<<< ..., stream >>>(...);
pcclAllReduce(..., stream);
kernel_C<<< ..., stream >>>(...);
hggcStreamEndCapture(stream, &graph);

hggcGraphExec_t instance;
hggcGraphInstantiate(&instance, graph, NULL, NULL, 0);
hggcGraphLaunch(instance, stream);
hggcStreamSynchronize(stream);
```

PCCL 支持同时存在多个尚未完成的操作，无论这些操作来自 graph 捕获，还是普通方式启动。但需要注意的是，如果多个通信域对应的 graph 由同一线程通过 `hggcGraphLaunch()` 启动，PCCL 内部的某些机制可能导致 HGGC 死锁。

### 3.9. 用户缓冲区注册

用户缓冲区注册允许 PCCL 直接在用户提供的缓冲区上完成数据发送、接收和处理，无需额外的内部拷贝，即可实现零拷贝。这样既能提升集合通信性能，也能显著降低资源占用，例如减少通道数。PCCL 提供两种用户缓冲区注册方式：HGGC Graph 注册（默认注册）和显式注册。

在调用 PCCL 通信函数（如 allReduce、sendRecv 等）时，如果通信域内任意一个 rank 传入的是已注册缓冲区，那么同一通信域中的其他 rank 也必须传入已注册缓冲区。已注册缓冲区与未注册缓冲区混用会导致未定义行为。另外，只有源缓冲区和目标缓冲区都完成注册后，PCCL 才能启用用户缓冲区注册能力。

#### 3.9.1. 通用缓冲区注册

PCCL 支持节点内缓冲区注册，可用于所有节点内点对点通信场景（例如 AllGather Ring），从而降低内存压力，并提升通信与计算并行效果。用户既可以在开始时通过 `pcclCommRegister` 注册缓冲区，也可以使用 HGGC Graph，为 PCCL 集合通信和 sendRecv 操作启用节点内缓冲区注册。

用户缓冲区可以通过 VMM API（即 `hggcMem*`）、任意基于 VMM 的分配器，或者 `pcclMemAlloc` 来分配。通过传统 HGGC API（如 `hggcMalloc`）分配的缓冲区也可以注册，但这种方式存在风险：运行过程中可能出现挂起，在故障或中止时还可能触发段错误。因此，不建议使用传统方式分配的缓冲区进行注册。

#### 3.9.2. 缓冲区注册与 PXN

网络通信（如 InfiniBand）的缓冲区注册与 PXN 在机制上并不兼容。只要平台支持，PCCL 默认会启用 PXN，适用于基于 sendRecv 的操作和集合通信。在 PXN 启用的情况下，即使用户已经通过 `pcclCommRegister` 注册了缓冲区，也不会启用网络缓冲区注册。

#### 3.9.3. 内存分配器

为了方便使用，PCCL 提供了 `pcclMemAlloc`，用于通过 VMM API 分配缓冲区。通过该接口分配的缓冲区可以直接用于后续的 PCCL 注册。由于这个接口是专门为 PCCL 设计的，因此不建议在应用程序的其他场景中使用 `pcclMemAlloc` 分配的缓冲区。

对于通用缓冲区注册，基于 VMM API 的分配器需要满足以下条件：

- 分配缓冲区时使用共享标志 `HG_MEM_HANDLE_TYPE_POSIX_FILE_DESCRIPTOR`。
- 缓冲区的物理内存大小必须是 HGGCMEM 推荐粒度的整数倍，即 `hggcMemGetAllocationGranularity(..., HG_MEM_ALLOC_GRANULARITY_RECOMMENDED)`。
- 缓冲区的虚拟起始地址至少按 HGGCMEM 推荐粒度对齐，且缓冲区大小也必须是该推荐粒度的整数倍。

#### 3.9.4. 窗口注册

PCCL 支持窗口注册，允许用户将本地缓冲区注册到 PCCL 窗口中，以获得更低延迟和更高带宽的通信能力。目前，窗口注册仅支持以下两类输入缓冲区：基于 VMM 的分配器分配的缓冲区，以及通过 `pcclMemAlloc` 分配的缓冲区；其他类型的 HGGC 缓冲区注册都会失败。

PCCL 窗口注册默认开启。用户也可以通过 [PCCL API 支持的标志](#67-pccl-api-支持的标志) 控制窗口注册的行为。

目前只支持 AllReduce、AllGather 和 ReduceScatter 三种集合通信，并且需要运行在单个或多个 ICN 域内，不支持 IB/ROCE 等网络场景。

以下示例展示了如何将缓冲区注册到 PCCL 窗口，并将其用于通信：

```c
void* sendBuff;
void* recvBuff;
pcclWindow_t sendWin;
pcclWindow_t recvWin;

PCCLCHECK(pcclMemAlloc(&sendBuff, sendBuffSize));
PCCLCHECK(pcclMemAlloc(&recvBuff, recvBuffSize));

// 指定 PCCL_WIN_COLL_SYMMETRIC 后，所有 rank 都需要提供对称缓冲区。
// 每个 rank 都必须调用 pcclCommWindowRegister 注册自己的缓冲区。
PCCLCHECK(pcclCommWindowRegister(comm, sendBuff, sendBuffSize, &sendWin, PCCL_WIN_COLL_SYMMETRIC));
PCCLCHECK(pcclCommWindowRegister(comm, recvBuff, recvBuffSize, &recvWin, PCCL_WIN_COLL_SYMMETRIC));

// 使用已注册缓冲区进行通信，以启用对称通信优化。
// 在这个示例中，每个 rank 分别从起始地址偏移 0x1000 和 0x2000 处参与通信，
// sendBuff 和 recvBuff 均满足对称缓冲区要求。
PCCLCHECK(pcclAllGather((uint8_t*)sendBuff + 0x1000, (uint8_t*)recvBuff + 0x2000, 1, pcclInt8, comm, stream));
PCCLCHECK(hggcStreamSynchronize(stream));

PCCLCHECK(pcclCommWindowDeregister(comm, sendWin));
PCCLCHECK(pcclCommWindowDeregister(comm, recvWin));

PCCLCHECK(pcclMemFree(sendBuff));
PCCLCHECK(pcclMemFree(recvBuff));
```

相关链接：

- [`pcclCommWindowDeregister()`](#6221-pcclcommwindowderegister)

#### 3.9.5. Zero-CTA 优化

PCCL 支持 Zero-CTA 优化。该优化的目标是不再占用 CTA 执行通信，从而提升通信与计算并行能力。

目前，Zero-CTA 优化支持通过 Copy Engine（CE）执行通信。启用该优化需要满足以下条件：

- 集合操作运行在单个 ICN 域内，不支持 IB/RoCE 等网络场景
- 缓冲区已通过 PCCL 窗口完成对称注册
- 通信域配置了 `PCCL_CTA_POLICY_ZERO` 标志（参见 [PCCL API 支持的标志](#67-pccl-api-支持的标志)）
- 支持的集合操作包括：AlltoAll、AllGather、Scatter 和 Gather
- 实验性支持 AllReduce：归约 + 广播，通过环境变量 `PCCL_CE_ENABLE_AR=1` 开启

以下示例展示了如何启用 Zero-CTA 优化：

```c
pcclConfig_t config = PCCL_CONFIG_INITIALIZER;

// 设置 PCCL_CTA_POLICY_ZERO，尽可能启用 Zero-CTA 优化。
config.CTAPolicy = PCCL_CTA_POLICY_ZERO;
PCCLCHECK(pcclCommInitRankConfig(&comm, nranks, id, rank, &config));

void* sendBuff;
void* recvBuff;
pcclWindow_t sendWin;
pcclWindow_t recvWin;

PCCLCHECK(pcclMemAlloc(&sendBuff, sendBuffSize));
PCCLCHECK(pcclMemAlloc(&recvBuff, recvBuffSize));

// 将缓冲区注册到 PCCL 对称窗口。
PCCLCHECK(pcclCommWindowRegister(comm, sendBuff, sendBuffSize, &sendWin, PCCL_WIN_COLL_SYMMETRIC));
PCCLCHECK(pcclCommWindowRegister(comm, recvBuff, recvBuffSize, &recvWin, PCCL_WIN_COLL_SYMMETRIC));
PCCLCHECK(pcclAllGather(sendBuff, recvBuff, 1, pcclInt8, comm, stream));
PCCLCHECK(hggcStreamSynchronize(stream));

PCCLCHECK(pcclCommWindowDeregister(comm, sendWin));
PCCLCHECK(pcclCommWindowDeregister(comm, recvWin));

PCCLCHECK(pcclMemFree(sendBuff));
PCCLCHECK(pcclMemFree(recvBuff));
```

##### 3.9.5.1. CE Collective 实现概述

PPU Copy Engine（CE）集合通信实现利用硬件 DMA 引擎在 rank 间完成数据搬运，无需占用 SM/CTA 资源。基于对称内存窗口（Symmetric Memory Window），每个 rank 可以通过 LSA（Load-Store Architecture）地址空间映射直接读写对端 rank 的内存，从而实现高效的单边通信。所有 CE 集合操作在启动前后进行 PPU 全局同步，保证各 rank 的通信时序正确。

##### 3.9.5.2. 直连与非直连拓扑的差异

CE 集合通信实现根据 PPU 间互联拓扑的不同，自动选择最优通信策略：

**直连拓扑（全连接）**：在所有 rank 之间存在直接 ICN 链路的全连接拓扑下，通信采用单阶段（one-stage）策略。每个 rank 通过 CE DMA 将自身数据直接写入所有对端 rank 的对称内存窗口中，一次批量操作即可完成。

**非直连拓扑（部分互联）**：对于真武 810 /真武 810E 等硬件平台上的 8 卡通信组，如果 PPU 间并非全连接，此时实现采用两阶段中继（two-stage relay）策略：

- 第一阶段：每个 rank 通过 CE DMA 将数据推送到 4 个直连对端的对称内存窗口
- 第二阶段：直连对端在收到数据后，将其继续转发给剩余 3 个非直连 rank

拓扑信息在运行时自动发现，策略选择基于 rank 数、硬件类型和连接矩阵自动判定，对用户透明。

##### 3.9.5.3. 实验性 AllReduce 支持

CE 路径提供了实验性的 AllReduce 实现，可通过环境变量 `PCCL_CE_ENABLE_AR=1` 开启。该实现将 CE DMA 搬运与片上 kernel 归约相结合，实现低 SM 占用率的 AllReduce。

**算法流程**：

AllReduce 采用 reduce-scatter + allgather 模式：

1. 数据按 rank 数均匀切分，每个 rank 负责归约一个切片
2. 每个 rank 通过 CE DMA 将对应切片的数据 scatter 到各目标 rank 的 staging buffer 中
3. 本地归约 kernel 在收到数据后立即对所有 rank 发来的对应切片执行累加归约
4. 归约完成后，每个 rank 再通过 CE DMA 将结果广播回所有其他 rank

**使用限制**：

- 数据类型：仅支持 `pcclHalf`、`pcclBfloat16` 和 `pcclFloat32`
- 归约操作：仅支持 Sum
- Rank 数：支持 2、4 或 8 rank
- 消耗额外的 device memory

**收益**：

CE AllReduce 对计算密集型负载具有显著优势。通过将大部分数据搬运工作卸载到 Copy Engine，SM 资源可以完全释放用于并行计算。归约 kernel 仅使用极少量的 SM 资源（最多 4 个 blocks，每个 block 1024 个 threads），以高吞吐但低 SM 占用率的方式完成累加。

平台扩展关联：TP AllReduce、Zero-CTA 和窗口注册面向多卡张量并行，不属于本次单卡比赛路径，也不作为系统级优化评分素材。

### 3.10. RAS

RAS（可靠性、可用性和可维护性）子系统可用于在程序运行过程中查询 PCCL 任务的健康状态，适合用来诊断崩溃、卡死等问题。它是一套低开销的运行时基础设施，PCCL 用户和开发者都可以在应用执行期间使用。RAS 能够提供当前通信的全局视图，并帮助识别无响应进程等异常情况。结合交互式调试、系统日志分析等手段，可以更快地缩小问题范围并定位错误原因。

#### 3.10.1. 工作原理

RAS 内建于 PCCL，会在 PCCL 初始化期间启动。它由一组线程组成，每个进程对应一个 RAS 线程。这些线程会彼此建立连接，组成一个监控网络，并通过这个网络交换信息、监控对方健康状态。

在典型配置下，RAS 产生的网络流量使用普通 TCP/IP socket，并运行在 PCCL 初始化阶段所依赖的 bootstrap / 带外网络接口上，因此通常不会与主要的 PCCL 数据流量（例如 RDMA）直接竞争。RAS 本身比较轻量，设计目标就是尽量不干扰主业务通信，因此默认处于开启状态。

RAS 线程会互相同步任务配置变化，同时周期性发送保活消息。如果某个 PCCL 进程崩溃或卡住，其他进程上的 RAS 线程通常可以通过对应的 RAS 网络连接感知到该进程已经退出，或者已经失去响应。

#### 3.10.2. RAS 查询

RAS 线程还会在 `localhost:28028` 上监听客户端连接。用户可以使用 `pcclras` 客户端连接该 socket，查询当前作业的状态，结果会输出到标准输出。

`pcclras` 支持以下常用参数：

- `-h,--host <host>`：指定主机名
- `-p,--port <port>`：指定端口
- `-d,--dump <hex>`: 触发状态保存，为以下可选 dump 类型的并集
  - 0x1: ROUGH，communicator 关键信息（channel、peer）文本
  - 0x2: RAW，communicator 二进制文件
  - 0x4: BUFFER，二进制文件包含中间传输 buffer
  - 0x10: HWINFO，hardware core dump 文件
- `-t,--timeout <seconds>`：指定超时时间，默认 `5` 秒；设为 `0` 表示禁用超时
- `-v,--verbose`：在出现问题时输出更详细的信息
- `-q,--quit`：发起 abort 终止任务（**慎用！**）

由于客户端协议本身是纯文本协议，因此除了 `pcclras`，也可以使用 telnet、netcat 等标准网络工具发起查询。常用命令包括 `STATUS`、`VERBOSE STATUS`（等价于 `pcclras -v`）以及 `TIMEOUT seconds`（等价于 `-t`）。例如：`echo verbose status | nc localhost 28028`。

无论使用哪种方式查询，接收请求的 RAS 线程都会返回任务摘要，以及所有 PCCL 通信域的汇总信息；这些数据会从任务中的所有进程收集而来。因此，如果任务本身存在异常，或者规模非常大，生成响应时可能需要几秒钟。如果收集过程中出现问题，返回结果中也会附带额外的诊断信息。

## 4. 编程实践

本章节提供 PCCL 的基础示例，帮助用户快速了解通信域生命周期管理以及常见通信模式的使用方式。

### 4.1. 通信域创建与销毁示例

下面通过几个例子介绍 PCCL 初始化和通信域管理的常见用法。

#### 4.1.1. 示例 1：单进程、单线程、多个 PPU device

在单进程场景下，可以使用 `pcclCommInitAll`。下面的示例会为 4 个 PPU device 创建通信域，因此最终会得到 4 个通信域对象：

```c
pcclComm_t comms[4];
int devs[4] = { 0, 1, 2, 3 };
pcclCommInitAll(comms, 4, devs);
```

创建完成后，可以由单线程配合组调用来发起 PCCL 集合通信，也可以为每个 `comm` 对象分别分配线程。

在程序结束前，需要销毁所有通信域对象：

```c
for (int i=0; i<4; i++)
  pcclCommDestroy(comms[i]);
```

下面的代码给出了一个单进程管理多个 PPU device 的完整可运行示例：

```c
#include <stdlib.h>
#include <stdio.h>
#include "hggc_runtime.h"
#include "pccl.h"

#define HGGCCHECK(cmd) do {                         \
  hggcError_t err = cmd;                            \
  if (err != hggcSuccess) {                         \
    printf("Failed: HGGC error %s:%d '%s'\n",      \
        __FILE__,__LINE__,hggcGetErrorString(err)); \
    exit(EXIT_FAILURE);                             \
  }                                                 \
} while(0)

#define PCCLCHECK(cmd) do {                         \
  pcclResult_t res = cmd;                           \
  if (res != pcclSuccess) {                         \
    printf("Failed, PCCL error %s:%d '%s'\n",      \
        __FILE__,__LINE__,pcclGetErrorString(res)); \
    exit(EXIT_FAILURE);                             \
  }                                                 \
} while(0)

int main(int argc, char* argv[])
{
  pcclComm_t comms[4];

  // 管理 4 个 PPU device
  int nDev = 4;
  int size = 32*1024*1024;
  int devs[4] = { 0, 1, 2, 3 };

  // 分配并初始化 PPU device 缓冲区
  float** sendbuff = (float**)malloc(nDev * sizeof(float*));
  float** recvbuff = (float**)malloc(nDev * sizeof(float*));
  hggcStream_t* s = (hggcStream_t*)malloc(sizeof(hggcStream_t)*nDev);

  for (int i = 0; i < nDev; ++i) {
    HGGCCHECK(hggcSetDevice(i));
    HGGCCHECK(hggcMalloc((void**)sendbuff + i, size * sizeof(float)));
    HGGCCHECK(hggcMalloc((void**)recvbuff + i, size * sizeof(float)));
    HGGCCHECK(hggcMemset(sendbuff[i], 1, size * sizeof(float)));
    HGGCCHECK(hggcMemset(recvbuff[i], 0, size * sizeof(float)));
    HGGCCHECK(hggcStreamCreate(s+i));
  }

  // 初始化 PCCL
  PCCLCHECK(pcclCommInitAll(comms, nDev, devs));

  // 发起 PCCL 通信。单线程管理多个 PPU device 时需要使用组调用 API
  PCCLCHECK(pcclGroupStart());
  for (int i = 0; i < nDev; ++i)
    PCCLCHECK(pcclAllReduce((const void*)sendbuff[i], (void*)recvbuff[i], size, pcclFloat, pcclSum,
        comms[i], s[i]));
  PCCLCHECK(pcclGroupEnd());

  // 同步 stream，等待 PCCL 操作完成
  for (int i = 0; i < nDev; ++i) {
    HGGCCHECK(hggcSetDevice(i));
    HGGCCHECK(hggcStreamSynchronize(s[i]));
  }

  // 释放 PPU device 缓冲区
  for (int i = 0; i < nDev; ++i) {
    HGGCCHECK(hggcSetDevice(i));
    HGGCCHECK(hggcFree(sendbuff[i]));
    HGGCCHECK(hggcFree(recvbuff[i]));
  }

  // 结束 PCCL
  for(int i = 0; i < nDev; ++i)
      pcclCommDestroy(comms[i]);

  printf("Success\n");
  return 0;
}
```

#### 4.1.2. 示例 2：每个进程或线程对应一个 PPU device

当每个进程或线程至多只负责一个 PPU device 时，可以使用 `pcclCommInitRank` 这个集合式调用来创建通信域。每个线程或进程都会得到自己的通信域对象。

下面的代码展示了一个结合 MPI、每个 MPI rank 使用一个 PPU device 的通信域创建示例。

首先，获取 MPI 进程信息：

```c
int myRank, nRanks;
MPI_Comm_rank(MPI_COMM_WORLD, &myRank);
MPI_Comm_size(MPI_COMM_WORLD, &nRanks);
```

接着，由一个 rank 创建唯一 ID，并将其广播给其他所有 rank，确保每个进程都获得同一个 ID：

```c
pcclUniqueId id;
if (myRank == 0) pcclGetUniqueId(&id);
MPI_Bcast(&id, sizeof(id), MPI_BYTE, 0, MPI_COMM_WORLD);
```

最后，创建通信域：

```c
pcclComm_t comm;
pcclCommInitRank(&comm, nRanks, id, myRank);
```

之后就可以使用该通信域来调用 PCCL 集合通信操作：

```c
pcclAllReduce(..., comm, s);
```

最后，销毁通信域对象：

```c
pcclCommDestroy(comm);
```

下面的代码给出了一个包含多个 MPI 进程、每个进程对应一个 PPU device 的完整可运行示例：

```c
#include <stdio.h>
#include "hggc_runtime.h"
#include "pccl.h"
#include "mpi.h"
#include <unistd.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define MPICHECK(cmd) do {                          \
  int e = cmd;                                      \
  if( e != MPI_SUCCESS ) {                          \
    printf("Failed: MPI error %s:%d '%d'\n",       \
        __FILE__,__LINE__, e);                      \
    exit(EXIT_FAILURE);                             \
  }                                                 \
} while(0)

#define HGGCCHECK(cmd) do {                         \
  hggcError_t e = cmd;                              \
  if( e != hggcSuccess ) {                          \
    printf("Failed: HGGC error %s:%d '%s'\n",      \
        __FILE__,__LINE__,hggcGetErrorString(e));   \
    exit(EXIT_FAILURE);                             \
  }                                                 \
} while(0)

#define PCCLCHECK(cmd) do {                         \
  pcclResult_t r = cmd;                             \
  if (r != pcclSuccess) {                           \
    printf("Failed, PCCL error %s:%d '%s'\n",      \
        __FILE__,__LINE__,pcclGetErrorString(r));   \
    exit(EXIT_FAILURE);                             \
  }                                                 \
} while(0)

static uint64_t getHash(const char* string, size_t n) {
  uint64_t result = 5381;
  for (size_t c = 0; c < n; c++) {
    result = ((result << 5) + result) ^ string[c];
  }
  return result;
}

#define HOSTID_FILE "/proc/sys/kernel/random/boot_id"
static uint64_t getHostHash(const char* hostname) {
  char hostHash[1024];

  (void) strncpy(hostHash, hostname, sizeof(hostHash));
  int offset = strlen(hostHash);

  FILE *file = fopen(HOSTID_FILE, "r");
  if (file != NULL) {
    char *p;
    if (fscanf(file, "%ms", &p) == 1) {
      strncpy(hostHash+offset, p, sizeof(hostHash)-offset-1);
      free(p);
    }
    fclose(file);
  }

  hostHash[sizeof(hostHash)-1] = '\0';
  return getHash(hostHash, strlen(hostHash));
}

static void getHostName(char* hostname, int maxlen) {
  gethostname(hostname, maxlen);
  for (int i = 0; i < maxlen; i++) {
    if (hostname[i] == '.') {
      hostname[i] = '\0';
      return;
    }
  }
}

int main(int argc, char* argv[])
{
  int size = 32*1024*1024;

  int myRank, nRanks, localRank = 0;

  MPICHECK(MPI_Init(&argc, &argv));
  MPICHECK(MPI_Comm_rank(MPI_COMM_WORLD, &myRank));
  MPICHECK(MPI_Comm_size(MPI_COMM_WORLD, &nRanks));

  uint64_t hostHashs[nRanks];
  char hostname[1024];
  getHostName(hostname, 1024);
  hostHashs[myRank] = getHostHash(hostname);
  MPICHECK(MPI_Allgather(MPI_IN_PLACE, 0, MPI_DATATYPE_NULL, hostHashs, sizeof(uint64_t), MPI_BYTE, MPI_COMM_WORLD));
  for (int p = 0; p < nRanks; p++) {
    if (p == myRank) break;
    if (hostHashs[p] == hostHashs[myRank]) localRank++;
  }

  pcclUniqueId id;
  pcclComm_t comm;
  float *sendbuff, *recvbuff;
  hggcStream_t s;

  if (myRank == 0) pcclGetUniqueId(&id);
  MPICHECK(MPI_Bcast((void *)&id, sizeof(id), MPI_BYTE, 0, MPI_COMM_WORLD));

  HGGCCHECK(hggcSetDevice(localRank));
  HGGCCHECK(hggcMalloc((void**)&sendbuff, size * sizeof(float)));
  HGGCCHECK(hggcMalloc((void**)&recvbuff, size * sizeof(float)));
  HGGCCHECK(hggcStreamCreate(&s));

  PCCLCHECK(pcclCommInitRank(&comm, nRanks, id, myRank));

  PCCLCHECK(pcclAllReduce((const void*)sendbuff, (void*)recvbuff, size, pcclFloat, pcclSum,
        comm, s));

  HGGCCHECK(hggcStreamSynchronize(s));

  HGGCCHECK(hggcFree(sendbuff));
  HGGCCHECK(hggcFree(recvbuff));

  pcclCommDestroy(comm);

  MPICHECK(MPI_Finalize());

  printf("[MPI Rank %d] Success\n", myRank);
  return 0;
}
```

#### 4.1.3. 示例 3：每个线程管理多个 PPU device

用户可以将“多进程或多线程”与“每个进程或线程管理多个 PPU device”结合起来使用。在这种情况下，需要配合组语义。

下面的示例结合了 MPI，以及“每个进程（即每个 MPI rank）管理多个 PPU device”的用法。

首先，获取 MPI 进程信息：

```c
int myRank, nRanks;
MPI_Comm_rank(MPI_COMM_WORLD, &myRank);
MPI_Comm_size(MPI_COMM_WORLD, &nRanks);
```

接着，由一个 rank 创建唯一 ID，并将其广播给其他所有 rank：

```c
pcclUniqueId id;
if (myRank == 0) pcclGetUniqueId(&id);
MPI_Bcast((void *)&id, sizeof(id), MPI_BYTE, 0, MPI_COMM_WORLD);
```

然后，创建 `ngpus` 个通信域对象，它们共同组成一个规模为 `ngpus*nRanks` 的更大通信域：

```c
pcclComm_t comms[ngpus];
pcclGroupStart();
for (int i = 0; i < ngpus; i++) {
  hggcSetDevice(devs[i]);
  pcclCommInitRank(comms+i, ngpus*nRanks, id, myRank*ngpus+i);
}
pcclGroupEnd();
```

接下来，可以使用单线程配合组调用来发起 PCCL 集合通信，或者为每个 `comm` 对象分配不同线程。

程序结束前，需要销毁所有通信域对象：

```c
for (int i = 0; i < ngpus; i++)
  pcclCommDestroy(comms[i]);
```

下面的代码给出了一个包含多个 MPI 进程、每个进程多个 device 的完整可运行示例：

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "hggc_runtime.h"
#include "pccl.h"
#include "mpi.h"
#include <unistd.h>
#include <stdint.h>

#define MPICHECK(cmd) do {                          \
  int e = cmd;                                      \
  if( e != MPI_SUCCESS ) {                          \
    printf("Failed: MPI error %s:%d '%d'\n",       \
        __FILE__,__LINE__, e);                      \
    exit(EXIT_FAILURE);                             \
  }                                                 \
} while(0)

#define HGGCCHECK(cmd) do {                         \
  hggcError_t e = cmd;                              \
  if( e != hggcSuccess ) {                          \
    printf("Failed: HGGC error %s:%d '%s'\n",      \
        __FILE__,__LINE__,hggcGetErrorString(e));   \
    exit(EXIT_FAILURE);                             \
  }                                                 \
} while(0)

#define PCCLCHECK(cmd) do {                         \
  pcclResult_t r = cmd;                             \
  if (r != pcclSuccess) {                           \
    printf("Failed, PCCL error %s:%d '%s'\n",      \
        __FILE__,__LINE__,pcclGetErrorString(r));   \
    exit(EXIT_FAILURE);                             \
  }                                                 \
} while(0)

static uint64_t getHash(const char* string, size_t n) {
  uint64_t result = 5381;
  for (size_t c = 0; c < n; c++) {
    result = ((result << 5) + result) ^ string[c];
  }
  return result;
}

#define HOSTID_FILE "/proc/sys/kernel/random/boot_id"
static uint64_t getHostHash(const char* hostname) {
  char hostHash[1024];

  (void) strncpy(hostHash, hostname, sizeof(hostHash));
  int offset = strlen(hostHash);

  FILE *file = fopen(HOSTID_FILE, "r");
  if (file != NULL) {
    char *p;
    if (fscanf(file, "%ms", &p) == 1) {
      strncpy(hostHash+offset, p, sizeof(hostHash)-offset-1);
      free(p);
    }
    fclose(file);
  }

  hostHash[sizeof(hostHash)-1] = '\0';
  return getHash(hostHash, strlen(hostHash));
}

static void getHostName(char* hostname, int maxlen) {
  gethostname(hostname, maxlen);
  for (int i = 0; i < maxlen; i++) {
    if (hostname[i] == '.') {
      hostname[i] = '\0';
      return;
    }
  }
}

int main(int argc, char* argv[])
{
  int size = 32*1024*1024;

  int myRank, nRanks, localRank = 0;

  MPICHECK(MPI_Init(&argc, &argv));
  MPICHECK(MPI_Comm_rank(MPI_COMM_WORLD, &myRank));
  MPICHECK(MPI_Comm_size(MPI_COMM_WORLD, &nRanks));

  uint64_t hostHashs[nRanks];
  char hostname[1024];
  getHostName(hostname, 1024);
  hostHashs[myRank] = getHostHash(hostname);
  MPICHECK(MPI_Allgather(MPI_IN_PLACE, 0, MPI_DATATYPE_NULL, hostHashs, sizeof(uint64_t), MPI_BYTE, MPI_COMM_WORLD));
  for (int p = 0; p < nRanks; p++) {
    if (p == myRank) break;
    if (hostHashs[p] == hostHashs[myRank]) localRank++;
  }

  int nDev = 2;

  float** sendbuff = (float**)malloc(nDev * sizeof(float*));
  float** recvbuff = (float**)malloc(nDev * sizeof(float*));
  hggcStream_t* s = (hggcStream_t*)malloc(sizeof(hggcStream_t)*nDev);

  for (int i = 0; i < nDev; ++i) {
    HGGCCHECK(hggcSetDevice(localRank*nDev + i));
    HGGCCHECK(hggcMalloc((void**)sendbuff + i, size * sizeof(float)));
    HGGCCHECK(hggcMalloc((void**)recvbuff + i, size * sizeof(float)));
    HGGCCHECK(hggcMemset(sendbuff[i], 1, size * sizeof(float)));
    HGGCCHECK(hggcMemset(recvbuff[i], 0, size * sizeof(float)));
    HGGCCHECK(hggcStreamCreate(s+i));
  }

  pcclUniqueId id;
  pcclComm_t comms[nDev];

  if (myRank == 0) pcclGetUniqueId(&id);
  MPICHECK(MPI_Bcast((void *)&id, sizeof(id), MPI_BYTE, 0, MPI_COMM_WORLD));

  PCCLCHECK(pcclGroupStart());
  for (int i = 0; i < nDev; i++) {
     HGGCCHECK(hggcSetDevice(localRank*nDev + i));
     PCCLCHECK(pcclCommInitRank(comms+i, nRanks*nDev, id, myRank*nDev + i));
  }
  PCCLCHECK(pcclGroupEnd());

  PCCLCHECK(pcclGroupStart());
  for (int i = 0; i < nDev; i++)
     PCCLCHECK(pcclAllReduce((const void*)sendbuff[i], (void*)recvbuff[i], size, pcclFloat, pcclSum,
           comms[i], s[i]));
  PCCLCHECK(pcclGroupEnd());

  for (int i = 0; i < nDev; i++)
      HGGCCHECK(hggcStreamSynchronize(s[i]));

  for (int i = 0; i < nDev; i++) {
     HGGCCHECK(hggcFree(sendbuff[i]));
     HGGCCHECK(hggcFree(recvbuff[i]));
  }

  for (int i = 0; i < nDev; i++) {
     pcclCommDestroy(comms[i]);
  }

  MPICHECK(MPI_Finalize());

  printf("[MPI Rank %d] Success\n", myRank);
  return 0;
}
```

#### 4.1.4. 示例 4：每个 PPU device 对应多个通信域

PCCL 支持用户在每个 PPU device 上创建多个通信域。下面的代码展示了一个包含多个 MPI 进程、每个进程对应一个 PPU device、且每个 PPU device 上创建多个通信域的示例。

阻塞通信域：

```c
HGGCCHECK(hggcSetDevice(localRank));
for (int i = 0; i < commNum; ++i) {
  if (myRank == 0) pcclGetUniqueId(&id);
  MPICHECK(MPI_Bcast((void *)&id, sizeof(id), MPI_BYTE, 0, MPI_COMM_WORLD));
  PCCLCHECK(pcclCommInitRank(&blockingComms[i], nRanks, id, myRank));
}
```

非阻塞通信域：

```c
HGGCCHECK(hggcSetDevice(localRank));
pcclConfig_t config = PCCL_CONFIG_INITIALIZER;
config.blocking = 0;
for (int i = 0; i < commNum; ++i) {
  if (myRank == 0) pcclGetUniqueId(&id);
  MPICHECK(MPI_Bcast((void *)&id, sizeof(id), MPI_BYTE, 0, MPI_COMM_WORLD));
  PCCLCHECK(pcclCommInitRankConfig(&nonblockingComms[i], nRanks, id, myRank, &config));
  do {
    PCCLCHECK(pcclCommGetAsyncError(nonblockingComms[i], &state));
  } while(state == pcclInProgress && checkTimeout() != true);
}
```

`checkTimeout()` 需要由用户自行实现。更多非阻塞通信域的使用方式，可参考[错误处理与通信域中止](#32-错误处理与通信域中止)。另外，如需基于已有通信域进行拆分，而不是重新创建新的通信域，可参考 [`pcclCommSplit()`](#629-pcclcommsplit)。

### 4.2. 通信示例

下面通过几个例子介绍 PCCL 集合通信的常见用法。

#### 4.2.1. 示例 1：每个进程或线程对应一个 PPU device

如果每个 PPU device 都由一个独立线程或进程管理，那么每个线程只需要在自己的 PPU device 上发起集合通信即可，例如执行 AllReduce：

```c
pcclAllReduce(sendbuff, recvbuff, count, datatype, op, comm, stream);
```

当调用返回时，这个操作已经加入到对应的 stream 队列中。如果需要等待它真正执行完成，可以继续调用：

```c
hggcStreamSynchronize(stream);
```

如果需要查看包含 MPI、且每个 MPI 进程对应一个 PPU device 的完整可运行示例，可以参考[通信域创建与销毁示例](#41-通信域创建与销毁示例)。

#### 4.2.2. 示例 2：每个线程管理多个 PPU device

如果一个线程要同时管理多个 PPU device，就需要使用组调用，在多个 PPU device 上统一发起操作：

```c
pcclGroupStart();
for (int i=0; i<ngpus; i++)
  pcclAllReduce(sendbuffs[i], recvbuff[i], count, datatype, op, comms[i], streams[i]);
pcclGroupEnd();
```

当 `pcclGroupEnd` 返回后，所有操作都已经分别加入对应的 stream。如果需要等待这些操作全部执行完成，可以再同步各自的 stream：

```c
for (int i=0; i<ngpus; i++)
  hggcStreamSynchronize(streams[i]);
```

如果需要查看包含 MPI、且每个 MPI 进程管理多个 PPU device 的完整可运行示例，也可以参考[通信域创建与销毁示例](#41-通信域创建与销毁示例)。

## 5. 高性能实践

本章节汇总面向不同使用场景的 PCCL 性能优化实践，帮助用户充分发挥 PCCL 在 PPU 平台上的性能潜力。当前主要涵盖以下四方面内容：

- **训练场景 —— 拓扑感知调度**：面向 Megatron 训练框架，在多维并行训练前通过 Device Order Search 工具搜索最优的 PPU 设备编排，尽可能让每个并行 Group 落在 ICN 互联的 PPU 上。
- **训练推理 —— 显存优化**：通过 splitShare 共享通信资源与调整 Channel 数量，降低 PCCL 的显存占用。
- **计算通信并行 —— Zero-CTA 优化**：在计算通信可重叠的场景下，将通信任务卸载到 Copy Engine 执行，释放 SM 用于计算，提升端到端性能。
- **大规模训练 —— Desync 排查**：介绍各 rank 到达时间不一致（desync）对集合通信性能的影响，以及在训练推理中通信性能明显低于 pccl-tests 基准时的排查思路。

### 5.1. Device Order Search：Megatron 多维并行下的拓扑感知调度

> **何时使用**：在 **不支持 ICN Switch** 的 PPU 平台（如 ZW810 / ZW810E）上，使用 **Megatron 训练框架**运行多维并行训练时，**建议在训练启动前使用 Device Order Search 工具**，为 TP / CP / EP / DP / PP 等并行 Group 搜索一组 ICN 互联的设备顺序。

#### 5.1.1. 功能说明

Device Order Search 是面向 **Megatron 训练框架**的多维并行训练场景设计的专用工具。它用于在启动 Megatron 多维并行训练前，基于当前节点的 PPU ICN 拓扑，为 Megatron 使用的 Tensor / Context / Expert / Data / Pipeline 等并行 Group 搜索出一组 ICN 互联的设备编排。工具会将搜索结果输出为可直接写入 `HGGC_VISIBLE_DEVICES` 的设备顺序字符串。

**典型使用步骤**：

1. 在启动 Megatron 训练前运行 Device Order Search，根据实际并行配置生成设备顺序；
2. 将输出结果导出到 `HGGC_VISIBLE_DEVICES`；
3. 启动 Megatron 训练脚本。

#### 5.1.2. 支持的并行 Group

| Group | 用途 |
|---|---|
| **TP** | Used for Tensor Parallel |
| **CP** | Used for Context Parallel |
| **EP** | Used for Expert Parallel |
| **DP** | Used for Data Parallel |
| **PP** | Used for Pipeline Parallel |
| **TP × CP** | Used for loading balance to calculate the auxiliary loss |
| **TP × EP** | Used for token dispatcher |
| **DP × CP** | Used for Data Parallel when Context Parallel also enabled |
| **(DP × CP) mod EP** | Used for MoE layer Data Parallel when both Expert Parallel and Context Parallel also enabled |
| **DP mod EP** | Used for MoE layer Data Parallel when Expert Parallel also enabled|

工具默认打印所有维度大于 1 的 Group 组合，便于人工比对与验证。

#### 5.1.3. 硬件相关的重点优化

工具在搜索时会针对具体 PPU 型号做额外优化：

- **ZW810 上的 4-FC 拓扑与算法**：如果切分维度允许，优先搜索出 4-FC 分组
    - 机内 4-FC 算法带宽高于 Ring
    - 机间通信中，4-FC 拓扑保有更高的机内聚合带宽，能让网卡跑满
- **ZW810E 双 ICN Link**：对于 TP=2 场景，优先搜索出带有 2 条 ICN link 的切分，最大化 TP 通信性能
- **Context Parallel + TE**：Ring Attention 采用 P2P Send/Recv 模式，工具会优先保证 rank 顺序的 PPU 完全 ICN 互联，避免转发损耗

若上述场景无法搜到满足条件的编排，工具会自动回退到普通的环形搜索（ring search），仍尽力保证 ICN 互联比例最大化。

#### 5.1.4. 工具位置

Device Order Search 位于独立发布的 `comm-tools` 制品包中，核心脚本为 `DeviceOrderSearch.py`。获取制品包后可直接使用其中的 `DeviceOrderSearch.py`。

#### 5.1.5. 命令行使用

```bash
python DeviceOrderSearch.py --help
```

主要参数：

| 参数 | 别名 | 说明 |
|---|---|---|
| `--tensor-model-parallel-size` | `--tp` | TP 维度 |
| `--pipeline-model-parallel-size` | `--pp` | PP 维度 |
| `--context-parallel-size` | `--cp` | CP 维度 |
| `--expert-model-parallel-size` | `--ep` | EP 维度 |
| `--world-size` | | 全局 rank 数量 |
| `--rank` | | 当前 rank |
| `--use-tp-pp-dp-mapping` | | rank 初始化顺序从默认的 tp-dp-pp 改为 tp-pp-dp；启用后 EP/CP 不可用 |
| `--ppu-num-per-node` | | 手动指定每节点 PPU 数量（默认自动检测） |
| `--devices-order` | | 指定候选设备顺序 |

工具在下列两种环境下均可运行：

- **PPU 物理机**：自动检测本机 ICN 拓扑
- **纯 CPU 机器**：通过 `--ppu-num-per-node 8` 或 `16` 生成对应拓扑用于离线搜索

#### 5.1.6. 使用示例

以 world-size=16、TP=2、CP=2、DP=4 为例：

```bash
python DeviceOrderSearch.py --tp 2 --cp 2 --world-size 16 --ppu-num-per-node 8
```

工具输出一个设备顺序后，在训练脚本启动前导出：

```bash
export HGGC_VISIBLE_DEVICES="0,3,1,2,4,7,5,6,9,10,8,11,13,14,12,15"
```

#### 5.1.7. FAQ

- **搜不到完全 ICN 互联的编排怎么办？**
    - 工具会打印失败提示。多数常见并行配置都能搜到，若失败可联系工具维护同学（`comm-tools`）人工确认。
    - 失败并不意味着无法训练，工具通常会 fallback 到环形搜索（ring search），尽力最大化 ICN 覆盖率。
- **能不能不用工具，凭经验手写 `HGGC_VISIBLE_DEVICES`？**
    - 5D 并行下手工排布极易出错。强烈建议使用工具输出的结果，并保留完整的搜索日志作为 checklist。

### 5.2. 训练推理显存优化建议

训练与推理场景中，device memory 需要同时承载模型权重、激活/KV Cache 与通信缓冲区。以下方法可用于减少 PCCL 自身的显存占用。

#### 5.2.1. 启用 splitShare 共享通信资源

当框架通过 `pcclCommSplit` 从父通信域派生子通信域时，可以启用 `splitShare`，让父子通信域共享同一份 send / recv buffer，从而显著降低 device memory 占用。

**启用方式**：

1. 设置环境变量：

    ```bash
    export PCCL_COMM_SPLIT_SHARE_RESOURCES=1
    ```

2. 框架侧调用 `pcclCommSplit` 创建通信域，并在 `pcclConfig_t` 中设置 `.splitShare = 1`。

**收益**：父通信域与子通信域共用通信缓冲区，避免子通信域重复申请 send / recv buffer。

**注意事项**：`splitShare` 会让父子通信域共享底层资源，禁止在父子通信域上并发发起 PCCL 操作，具体线程安全约束参见[线程安全](#37-线程安全)。

#### 5.2.2. 减少 Channel 数量

Channel 数量决定了 PCCL 用于并行通信的 Channel 数量，Channel 越多分配的通信 buffer 越多。在 device memory 紧张的场景下，可以适当减少 Channel 数量，以峰值带宽换显存。

**背景**：以真武 810E 单机 16 卡为例，PCCL 默认为追求峰值带宽会将 Channel 数放大到超过 24 个，带来相应的 buffer 分配。

**调整方式**：

```bash
# 峰值带宽下降约 20%
export PCCL_MAX_NCHANNELS=12

# 峰值带宽下降约 34%
export PCCL_MAX_NCHANNELS=6
```

**建议**：先在实际推理负载上测量减少 Channel 后的整体吞吐/延迟表现，避免为省显存而付出过高的通信性能代价。

### 5.3. 计算通信并行场景优化

在计算与通信可以并行执行的场景（如大模型训练中的梯度同步与反向计算重叠、推理中的通信与算子执行重叠），通信任务与计算任务会争抢 SM 资源。将通信任务卸载到 Copy Engine（CE）执行，能够显著降低通信对 SM 的占用，从而释放算力用于并行计算，提升端到端性能。

#### 5.3.1. 通过 Zero-CTA 策略走 Copy Engine

将通信域的 CTA 策略配置为 `ZERO` 后，PCCL 会在满足条件时通过 Copy Engine 完成数据搬运，通信过程几乎不占用 SM。

**启用方式**（选其一）：

- **环境变量**：

    ```bash
    export PCCL_CTA_POLICY=ZERO
    ```

- **通信域配置**：

    ```c
    pcclConfig_t config = PCCL_CONFIG_INITIALIZER;
    config.CTAPolicy = PCCL_CTA_POLICY_ZERO;
    pcclCommInitRankConfig(&comm, nranks, id, rank, &config);
    ```

**收益**：将数据搬运卸载到 Copy Engine，SM 资源可释放给计算 kernel 使用；对于计算通信重叠的负载，端到端性能提升明显。

**适用条件**：

- 需运行在单 ICN 域内；
- 通信使用的 `sendbuff` / `recvbuff` 必须是 Symmetric Memory，即通过 `pcclMemAlloc` 或基于 VMM 的分配器分配，并通过 `pcclCommWindowRegister` 完成对称窗口注册；
- 具体前置条件与限制参见[Zero-CTA 优化](#395-zero-cta-优化)。

### 5.4. 大规模训练中的 Desync 排查

在大规模分布式训练中，各 rank 到达同一次集合通信的时间点存在天然差异，这种差异称为 **desync**（rank 间的到达时间不一致）。集合通信必须等待最慢的 rank 到齐后才能真正开始，因此 desync 会直接放大集合通信在训练中的耗时表现。

#### 5.4.1. Desync 的影响

- **拉长通信 tail**：即便通信本身很快，一旦各 rank 到达点分散，通信就会表现为等待占比大、实际带宽利用低。
- **规模越大越敏感**：rank 数越多，每一次集合通信被最慢 rank 拉长的概率越高，端到端影响越显著。
- **难以从单机 profile 定位**：单卡 profile 只能看到“通信 kernel 耗时长”，但根因可能在其他 rank 的计算慢、CPU 侧同步、数据加载抖动，或不均衡负载。

#### 5.4.2. 与 pccl-tests 的对比排查

pccl-tests 中的集合通信基准是一个理想化的场景：所有 rank 同步进入通信、无计算干扰、无框架开销。当训练中观察到某个 PCCL op 的耗时**明显高于 pccl-tests(相关测试工具可从 comm-tools 中获取) 在相同规模、相同数据量下的基准**时，通常并不是 PCCL 本身出了问题，建议排查：

- 是否存在计算负载不均衡（数据 padding、变长序列、专家不均等）；
- 是否有数据加载 / IO 抖动（部分 rank 未准备好即进入通信）；
- 是否有上层框架的隐式同步（如 checkpoint、metrics 同步）落在通信前；
- 是否有个别节点 CPU / 内存 / 温度异常，导致慢节点。

#### 5.4.3. 观测建议

推荐使用 **ASight System** 对训练过程进行观测和分析：

- 采集训练中所有 rank 的时间线，直观展示各 rank 到达同一集合通信的时间差；
- 将计算 kernel 与通信 kernel 时间线对齐，快速识别哪些 rank 拖慢了整体节奏；
- 结合负载分布与节点资源信息，定位 desync 的根因（负载不均衡、IO 抖动、慢节点等）。

平台扩展关联：这些 PCCL 显存和 AllReduce 优化面向多卡 VLM，不属于本次单卡比赛路径；比赛进程不应初始化 PCCL buffer 或 TP 通信组。

## 6. API 指南

### 6.1. 概述

本章节汇总 PCCL 提供的主要 API，涵盖通信域创建与管理、集合通信、组调用、点对点通信、数据类型以及相关标志位。

可按功能查阅以下内容：

### 6.2. 通信域创建与管理函数

以下 PCCL API 用于创建、查询、拆分、缩小、终止和销毁通信域，以及执行与通信域相关的缓冲区注册和内存分配操作。

#### 6.2.1. pcclGetLastError

```c
const char* pcclGetLastError(pcclComm_t comm)
```

返回与通信域 `comm` 关联的最近一次错误状态。该接口主要用于辅助诊断，通常与 `pcclGetErrorString` 一起使用，以便将返回值转换为可读字符串。

相关链接：[错误处理与通信域中止](#32-错误处理与通信域中止)。

#### 6.2.2. pcclGetErrorString

```c
const char* pcclGetErrorString(pcclResult_t result)
```

将 PCCL 错误码 `result` 转换为可读字符串，便于日志输出和问题定位。

相关链接：[错误处理与通信域中止](#32-错误处理与通信域中止)。

#### 6.2.3. pcclGetVersion

```c
pcclResult_t pcclGetVersion(int* version)
```

返回当前 PCCL 版本号，并将结果写入 `version`。

#### 6.2.4. pcclGetUniqueId

```c
pcclResult_t pcclGetUniqueId(pcclUniqueId* uniqueId)
```

创建一个新的唯一 ID。该 ID 需要在所有参与创建同一通信域的进程或线程之间共享，随后可用于 `pcclCommInitRank`、`pcclCommInitRankConfig` 或 `pcclCommInitRankScalable`。

相关链接：[创建通信域](#31-创建通信域)。

#### 6.2.5. pcclCommInitRank

```c
pcclResult_t pcclCommInitRank(pcclComm_t *comm, int nranks, pcclUniqueId commId, int rank)
```

使用共享的唯一 ID `commId` 创建一个通信域，并将当前调用者加入到总大小为 `nranks` 的通信域中，逻辑 rank 为 `rank`。

相关链接：[创建通信域](#31-创建通信域)。

#### 6.2.6. pcclCommInitAll

```c
pcclResult_t pcclCommInitAll(pcclComm_t *comm, int ndev, const int* devlist)
```

在单个进程内一次性创建 `ndev` 个通信域对象。`devlist` 指定每个通信域所对应的 PPU device。该接口适用于单进程场景，不用于跨节点通信。

相关链接：[创建通信域](#31-创建通信域)。

#### 6.2.7. pcclCommInitRankConfig

```c
pcclResult_t pcclCommInitRankConfig(pcclComm_t *comm, int nranks, pcclUniqueId commId, int rank, pcclConfig_t *config)
```

与 `pcclCommInitRank` 类似，但允许用户通过 `config` 指定通信域的创建选项，例如阻塞模式、CTA 策略和网络相关参数。

相关链接：[创建通信域](#31-创建通信域)。

#### 6.2.8. pcclCommInitRankScalable

```c
pcclResult_t pcclCommInitRankScalable(pcclComm_t *newcomm, int nranks, int myrank, int nId, pcclUniqueId* commIds, pcclConfig_t *config)
```

使用多个唯一 ID 创建通信域。所有 rank 必须提供相同数量、相同顺序的 `commIds`，以便在大规模场景下更灵活地完成通信域初始化。

相关链接：[创建通信域](#31-创建通信域)。

#### 6.2.9. pcclCommSplit

```c
pcclResult_t pcclCommSplit(pcclComm_t comm, int color, int key, pcclComm_t *newcomm, pcclConfig_t *config)
```

基于现有通信域 `comm` 创建新的子通信域。`color` 用于指定当前 rank 属于哪个子组，`key` 用于决定新通信域中的 rank 顺序。若某个 rank 不属于任何子组，则应传入 `PCCL_SPLIT_NOCOLOR`。

相关链接：[创建通信域](#31-创建通信域)。

#### 6.2.10. pcclCommShrink

```c
pcclResult_t pcclCommShrink(pcclComm_t comm, int* excludeRanksList, int excludeRanksCount, pcclComm_t *newcomm, pcclConfig_t *config, int shrinkFlags)
```

通过从现有通信域 `comm` 中排除 `excludeRanksList` 指定的 rank，创建一个新的通信域。该接口常用于错误恢复和动态裁剪资源等场景。`shrinkFlags` 可用于控制 shrink 的行为。

相关链接：

- [PCCL API 支持的标志](#67-pccl-api-支持的标志)

#### 6.2.11. pcclCommFinalize

```c
pcclResult_t pcclCommFinalize(pcclComm_t comm)
```

开始结束通信域 `comm`。PCCL 会在后台完成剩余操作，并释放与通信域相关的资源。对于非阻塞通信域，该调用本身也可以是非阻塞的。

相关链接：[创建通信域](#31-创建通信域)。

#### 6.2.12. pcclCommDestroy

```c
pcclResult_t pcclCommDestroy(pcclComm_t comm)
```

销毁通信域 `comm` 并释放其本地资源。调用返回后，不应再访问该通信域。

相关链接：[创建通信域](#31-创建通信域)。

#### 6.2.13. pcclCommAbort

```c
pcclResult_t pcclCommAbort(pcclComm_t comm)
```

立即中止通信域 `comm`，用于错误恢复或超时处理。调用该接口后，通信域不应再继续用于正常通信。

相关链接：[错误处理与通信域中止](#32-错误处理与通信域中止)。

#### 6.2.14. pcclCommGetAsyncError

```c
pcclResult_t pcclCommGetAsyncError(pcclComm_t comm, pcclResult_t *asyncError)
```

查询通信域 `comm` 的异步错误状态，并将结果写入 `asyncError`。当通信在后台推进时，应用程序可轮询该接口以检测网络错误或其他致命错误。

相关链接：[错误处理与通信域中止](#32-错误处理与通信域中止)。

#### 6.2.15. pcclCommCount

```c
pcclResult_t pcclCommCount(const pcclComm_t comm, int* count)
```

返回通信域 `comm` 中的 rank 数量，并将结果写入 `count`。

#### 6.2.16. pcclCommCuDevice

```c
pcclResult_t pcclCommCuDevice(const pcclComm_t comm, int* device)
```

返回与通信域 `comm` 关联的本地 PPU device 编号，并将结果写入 `device`。

#### 6.2.17. pcclCommUserRank

```c
pcclResult_t pcclCommUserRank(const pcclComm_t comm, int* rank)
```

返回当前调用者在通信域 `comm` 中的用户 rank，并将结果写入 `rank`。

#### 6.2.18. pcclCommRegister

```c
pcclResult_t pcclCommRegister(const pcclComm_t comm, void* buff, size_t size, void** handle)
```

将用户缓冲区 `buff` 注册到通信域 `comm` 中，以便 PCCL 在后续通信中直接使用该缓冲区。返回的注册句柄会写入 `handle`，后续可通过 `pcclCommDeregister` 注销。

相关链接：[用户缓冲区注册](#39-用户缓冲区注册)。

#### 6.2.19. pcclCommDeregister

```c
pcclResult_t pcclCommDeregister(const pcclComm_t comm, void* handle)
```

注销先前通过 `pcclCommRegister` 获得的缓冲区注册句柄 `handle`。

相关链接：[用户缓冲区注册](#39-用户缓冲区注册)。

#### 6.2.20. pcclCommWindowRegister

```c
pcclResult_t pcclCommWindowRegister(pcclComm_t comm, void* buff, size_t size, pcclWindow_t* win, int winFlags)
```

将本地缓冲区 `buff` 注册到 PCCL 窗口中，并将生成的窗口对象写入 `win`。`winFlags` 用于指定窗口注册行为，例如是否要求集合通信偏移对称。

相关链接：[用户缓冲区注册](#39-用户缓冲区注册)。

#### 6.2.21. pcclCommWindowDeregister

```c
pcclResult_t pcclCommWindowDeregister(pcclComm_t comm, pcclWindow_t win)
```

注销先前通过 `pcclCommWindowRegister` 创建的窗口对象 `win`。

相关链接：[用户缓冲区注册](#39-用户缓冲区注册)。

#### 6.2.22. pcclMemAlloc

```c
pcclResult_t pcclMemAlloc(void** ptr, size_t size)
```

分配一段可用于 PCCL 缓冲区注册的内存，并将分配得到的地址写入 `ptr`。

相关链接：[用户缓冲区注册](#39-用户缓冲区注册)。

#### 6.2.23. pcclMemFree

```c
pcclResult_t pcclMemFree(void* ptr)
```

释放先前通过 `pcclMemAlloc` 分配的内存。

相关链接：[用户缓冲区注册](#39-用户缓冲区注册)。

### 6.3. 集合通信函数

以下列出了 PCCL 提供的常用集合通信操作。

#### 6.3.1. pcclAllReduce

```c
pcclResult_t pcclAllReduce(const void* sendbuff, void* recvbuff, size_t count, pcclDataType_t datatype, pcclRedOp_t op, pcclComm_t comm, hggcStream_t stream)
```

对长度为 `count` 的输入数组执行 `op` 归约，并将相同的结果副本写入每个 rank 的 `recvbuff`。

如果 `sendbuff == recvbuff`，则会发生原地操作。

相关链接：[集合通信](#33-集合通信)。

#### 6.3.2. pcclAllGather

```c
pcclResult_t pcclAllGather(const void* sendbuff, void* recvbuff, size_t sendcount, pcclDataType_t datatype, pcclComm_t comm, hggcStream_t stream)
```

从所有 PPU 收集 `sendcount` 个值，并将结果的相同副本保留在每个 `recvbuff` 中，其中来自 rank `i` 的数据会放置在偏移 `i*sendcount` 处。

> **注意**：这假设接收计数等于 `nranks*sendcount`，因此 `recvbuff` 至少需要包含 `nranks*sendcount` 个元素。

如果 `sendbuff == recvbuff + rank * sendcount`，则会发生原地操作。

相关链接：[集合通信](#33-集合通信)。

#### 6.3.3. pcclBroadcast

```c
pcclResult_t pcclBroadcast(const void* sendbuff, void* recvbuff, size_t count, pcclDataType_t datatype, int root, pcclComm_t comm, hggcStream_t stream)
```

将 rank `root` 上 `sendbuff` 中的 `count` 个元素复制到所有 rank 的 `recvbuff` 中。`sendbuff` 仅在 rank `root` 上使用，其他 rank 会忽略该参数。

如果 `sendbuff == recvbuff`，则会发生原地操作。

```c
pcclResult_t pcclBcast(void* buff, size_t count, pcclDataType_t datatype, int root, pcclComm_t comm, hggcStream_t stream)
```

`pcclBroadcast` 的旧版原地形式，其行为与 MPI_Bcast 类似。调用：

> `pcclBcast(buff, count, datatype, root, comm, stream)`

等价于：

> `pcclBroadcast(buff, buff, count, datatype, root, comm, stream)`

相关链接：[集合通信](#33-集合通信)。

#### 6.3.4. pcclReduceScatter

```c
pcclResult_t pcclReduceScatter(const void* sendbuff, void* recvbuff, size_t recvcount, pcclDataType_t datatype, pcclRedOp_t op, pcclComm_t comm, hggcStream_t stream)
```

使用 `op` 对来自所有 PPU 的 `sendbuff` 数据进行归约，并将归约结果按块分散到各个 PPU 上，使得 rank `i` 上的 `recvbuff` 包含结果中的第 `i` 块。

> **注意**：这假设发送计数等于 `nranks*recvcount`，因此 `sendbuff` 至少需要包含 `nranks*recvcount` 个元素。

如果 `recvbuff == sendbuff + rank * recvcount`，则会发生原地操作。

相关链接：[集合通信](#33-集合通信)。

#### 6.3.5. pcclScatter

```c
pcclResult_t pcclScatter(const void* sendbuff, void* recvbuff, size_t count, pcclDataType_t datatype, int root, pcclComm_t comm, hggcStream_t stream)
```

每个 rank 从 rank `root` 接收 `count` 个元素。在 rank `root` 上，发送到 rank `i` 的 `count` 个元素取自 `sendbuff + i*count`。在非 root rank 上，`sendbuff` 不会使用。

> **注意**：这假设发送计数等于 `nranks*count`，因此 `sendbuff` 至少需要包含 `nranks*count` 个元素。

如果 `recvbuff == sendbuff + root * count`，则会发生原地操作。

相关链接：[集合通信](#33-集合通信)。

#### 6.3.6. pcclAlltoAll

```c
pcclResult_t pcclAlltoAll(const void* sendbuff, void* recvbuff, size_t count, pcclDataType_t datatype, pcclComm_t comm, hggcStream_t stream)
```

每个 rank 向所有其他 rank 发送 `count` 个值，并从所有其他 rank 接收 `count` 个值。发送到目标 rank `j` 的数据取自 `sendbuff+j*count`，从源 rank `i` 接收的数据放置在 `recvbuff+i*count`。

> **注意**：这假设发送与接收的总计数都等于 `nranks*count`，因此 `sendbuff` 和 `recvbuff` 至少需要包含 `nranks*count` 个元素。

当前不支持原地操作。

相关链接：[集合通信](#33-集合通信)。

#### 6.3.7. pcclReduce

```c
pcclResult_t pcclReduce(const void* sendbuff, void* recvbuff, size_t count, pcclDataType_t datatype, pcclRedOp_t op, int root, pcclComm_t comm, hggcStream_t stream)
```

使用操作 `op` 对来自 `sendbuff` 的长度为 `count` 的数据数组执行归约，并将结果写入 rank `root` 上的 `recvbuff`。`recvbuff` 仅在 rank `root` 上使用，在其他 rank 上会被忽略。

如果 `sendbuff == recvbuff`，则会发生原地操作。

相关链接：[集合通信](#33-集合通信)。

#### 6.3.8. pcclGather

```c
pcclResult_t pcclGather(const void* sendbuff, void* recvbuff, size_t count, pcclDataType_t datatype, int root, pcclComm_t comm, hggcStream_t stream)
```

每个 rank 将 `sendbuff` 中的 `count` 个元素发送到 rank `root`。在 rank `root` 上，来自 rank `i` 的数据会放置到 `recvbuff + i*count`。在非 root rank 上，`recvbuff` 不会使用。

> **注意**：这假设接收计数等于 `nranks*count`，因此 `recvbuff` 至少需要包含 `nranks*count` 个元素。

如果 `sendbuff == recvbuff + root * count`，则会发生原地操作。

相关链接：[集合通信](#33-集合通信)。

### 6.4. 点对点通信函数

当 rank 之间需要彼此发送和接收任意数据，且这种通信无法表示为 broadcast 或 allgather 时，也就是发送和接收的数据内容并不相同时，就需要使用双边点对点通信原语。发送方和接收方都必须显式参与。

#### 6.4.1. pcclSend

```c
pcclResult_t pcclSend(const void* sendbuff, size_t count, pcclDataType_t datatype, int peer, pcclComm_t comm, hggcStream_t stream)
```

将 `sendbuff` 中的数据发送到 rank `peer`。

rank `peer` 需要使用相同的 `datatype` 和相同的 `count` 调用 `pcclRecv`。

该操作会阻塞 PPU。如果需要让多个 `pcclSend()` 和 `pcclRecv()` 操作并发推进，则必须将它们融合在 `pcclGroupStart()` / `pcclGroupEnd()` 代码段中。

相关链接：[点对点通信](#36-点对点通信)。

#### 6.4.2. pcclRecv

```c
pcclResult_t pcclRecv(void* recvbuff, size_t count, pcclDataType_t datatype, int peer, pcclComm_t comm, hggcStream_t stream)
```

从 rank `peer` 接收数据到 `recvbuff`。

rank `peer` 需要使用相同的 `datatype` 和相同的 `count` 调用 `pcclSend`。

该操作会阻塞 PPU。如果需要让多个 `pcclSend()` 和 `pcclRecv()` 操作并发推进，则必须将它们融合在 `pcclGroupStart()` / `pcclGroupEnd()` 代码段中。

相关链接：[点对点通信](#36-点对点通信)。

### 6.5. 组调用函数

组调用原语用于定义当前线程的提交边界，以避免不必要的阻塞，因此多个线程可以独立使用。

相关链接：[组调用](#35-组调用)。

#### 6.5.1. pcclGroupStart

```c
pcclResult_t pcclGroupStart()
```

开始一个组调用。

在 `pcclGroupEnd` 之前，后续所有 PCCL 调用都不会因为 CPU 间同步而阻塞。

#### 6.5.2. pcclGroupEnd

```c
pcclResult_t pcclGroupEnd()
```

结束一个组调用。

当自 `pcclGroupStart` 以来的所有操作都已被处理后，该函数返回。这意味着通信原语已经被入队到所提供的 stream 中，但不一定已经执行完成。

当与 `pcclCommInitRank` 一起使用时，`pcclGroupEnd` 会等待所有通信域初始化完成。

### 6.6. 数据类型

以下是 PCCL 库中使用的数据类型。

#### 6.6.1. pcclComm_t

```c
type pcclComm_t
```

PCCL 通信域类型。它指向 PCCL 内部的一个不透明结构体。

#### 6.6.2. pcclResult_t

```c
type pcclResult_t
```

所有 PCCL 函数的返回值类型。可能的取值包括：

- **pcclSuccess**：`(0)` 函数执行成功。
- **pcclUnhandledHggcError**：`(1)` 对某个 HGGC 函数的调用失败。
- **pcclSystemError**：`(2)` 系统调用失败。
- **pcclInternalError**：`(3)` 内部检查失败。这通常意味着 PCCL 内部存在缺陷，或者发生了内存损坏。
- **pcclInvalidArgument**：`(4)` 参数值无效。
- **pcclInvalidUsage**：`(5)` 对 PCCL 的调用方式不正确。这通常反映了程序使用上的错误。
- **pcclRemoteError**：`(6)` 调用失败，可能由网络错误或远端进程提前退出导致。
- **pcclInProgress**：`(7)` 该通信域上的某个 PCCL 操作正在入队，并在后台推进。

当函数返回错误时（既不是 `pcclSuccess`，也不是 `pcclInProgress`），应用程序需要根据错误类型采取相应的处理措施。详细的错误处理方式请参考[错误处理与通信域中止](#32-错误处理与通信域中止)。

#### 6.6.3. pcclDataType_t

```c
type pcclDataType_t
```

PCCL 定义了如下整型与浮点型数据类型。

- **pcclInt8**：有符号 8 位整数。
- **pcclChar**：有符号 8 位整数。
- **pcclUint8**：无符号 8 位整数。
- **pcclInt32**：有符号 32 位整数。
- **pcclInt**：有符号 32 位整数。
- **pcclUint32**：无符号 32 位整数。
- **pcclInt64**：有符号 64 位整数。
- **pcclUint64**：无符号 64 位整数。
- **pcclFloat16**：16 位浮点数（half precision）。
- **pcclHalf**：16 位浮点数（half precision）。
- **pcclFloat32**：32 位浮点数（single precision）。
- **pcclFloat**：32 位浮点数（single precision）。
- **pcclFloat64**：64 位浮点数（double precision）。
- **pcclDouble**：64 位浮点数（double precision）。
- **pcclBfloat16**：16 位浮点数（bfloat16 截断精度格式）。
- **pcclFloat8e4m3**：8 位浮点数，4 位指数，3 位尾数。
- **pcclFloat8e5m2**：8 位浮点数，5 位指数，2 位尾数。

#### 6.6.4. pcclRedOp_t

```c
type pcclRedOp_t
```

定义归约操作类型。

- **pcclSum**：执行求和（`+`）操作。
- **pcclProd**：执行乘积（`*`）操作。
- **pcclMin**：执行最小值操作。
- **pcclMax**：执行最大值操作。
- **pcclAvg**：执行平均值操作，即先对所有 rank 求和，再除以 rank 数量。

#### 6.6.5. pcclScalarResidence_t

```c
type pcclScalarResidence_t
```

指示标量参数所在的内存空间，以及它们应在何时被解引用。

- **pcclScalarHostImmediate**：标量位于主机内存中，应以最即时的方式进行解引用。
- **pcclScalarDevice**：标量位于 device 可见内存中，应在真正需要时再解引用。

#### 6.6.6. pcclConfig_t

```c
type pcclConfig_t
```

这是一个结构体配置类型，用户可在初始化通信域时通过它设置相关参数。新创建的配置对象必须使用 `PCCL_CONFIG_INITIALIZER` 初始化。

- **PCCL_CONFIG_INITIALIZER**：配置宏初始化器。新创建的配置对象必须先赋值为该初始化器。
- **blocking**：该属性可设置为整数 `0` 或 `1`，分别表示非阻塞或阻塞通信域行为。默认行为为阻塞。
- **minCTAs**：设置 PCCL 对每个内核应使用的最小 CTA 数量。可设置为正整数，最大不超过 `32`。默认值为 `1`。
- **maxCTAs**：设置 PCCL 对每个内核应使用的最大 CTA 数量。可设置为正整数，最大不超过 `32`。默认值为 `32`。
- **netName**：指定 PCCL 在网络通信中应使用的网络模块名称。`netName` 的值必须与网络模块名完全匹配（不区分大小写）。PCCL 内部网络模块名包括 `IB`（通用 IB verbs）和 `Socket`（TCP/IP sockets）；外部网络插件可定义自己的名称。默认值未定义，此时 PCCL 会自动选择网络模块。
- **splitShare**：指定在通信域 split 期间，是否与子通信域共享资源。`splitShare` 可设置为 `0` 或 `1`，默认值为 `0`。当父通信域在 `pcclCommInitRankConfig` 中以 `splitShare=1` 创建时，split 产生的子通信域可共享父通信域的内部资源。发生资源共享时，这些 split 出来的通信域属于同一个 family。共享资源后，中止任意一个通信域，都可能导致同一 family 中的其他通信域不可用。无论是否共享资源，用户都应及时 abort 或 destroy 不再使用的通信域以释放资源。
- **shrinkShare**：指定在通信域 shrink 期间，是否与子通信域共享资源。`shrinkShare` 可设置为 `0` 或 `1`，默认值为 `0`。该标志的整体行为与 `splitShare` 类似。
- **CTAPolicy**：设置通信域的 CTA 策略。完整的受支持策略列表可参见 [PCCL API 支持的标志](#67-pccl-api-支持的标志)。
- **commName**：指定用户自定义的通信域名称。PCCL 可使用该名称丰富日志和 profiling 信息。

#### 6.6.7. pcclWindow_t

```c
type pcclWindow_t
```

PCCL 窗口对象类型，用于窗口注册与注销。

### 6.7. PCCL API 支持的标志

以下列出了 PCCL API 支持的各类标志。

#### 6.7.1. 窗口注册标志

**PCCL_WIN_DEFAULT**

以默认行为将缓冲区注册到 PCCL 窗口中。该默认行为允许用户在调用 PCCL 集合通信操作时，以缓冲区首地址的任意偏移作为输入。但由于缓冲区使用方式不对称，这种行为可能降低 PCCL 性能。

**PCCL_WIN_COLL_SYMMETRIC**

将缓冲区注册到 PCCL 窗口中，并要求用户在调用 PCCL 集合通信操作时，所有 rank 相对于缓冲区首地址的偏移必须相同。它允许 PCCL 以对称方式访问缓冲区，并获得最佳性能。

#### 6.7.2. PCCL 通信域 CTA 策略标志

**PCCL_CTA_POLICY_DEFAULT**

对 PCCL 通信域使用默认 CTA 策略。在该策略下，PCCL 会自动调整资源使用以获得最佳性能。此策略适用于大多数应用。

**PCCL_CTA_POLICY_EFFICIENCY**

对 PCCL 通信域使用 CTA efficiency 策略。在该策略下，PCCL 会尽可能优化 CTA 使用，并用尽量少的 CTA 数量获得合适性能；部分机型下，通信任务将优先调度到不与计算任务竞争计算资源的处理单元上执行，从而降低通信与计算之间的资源竞争。此策略适用于计算通信重叠（overlap）场景，可提升整体吞吐。

**PCCL_CTA_POLICY_ZERO**

对 PCCL 通信域使用 Zero-CTA 策略。在该策略下，PCCL 会在可能的情况下尽量不使用 CTA，即使这种选择可能会牺牲部分性能。当应用需要为计算内核保留尽可能多的 CTA 时，可选择该模式。

#### 6.7.3. 通信域缩小标志

这些标志用于修改 `pcclCommShrink` 操作的行为。

**PCCL_SHRINK_DEFAULT**

默认行为。在不影响正在进行中的操作的前提下，对父通信域执行 shrink。取值：`0x00`。

**PCCL_SHRINK_ABORT**

首先终止父通信域上正在进行中的操作，然后再继续执行 shrink。该标志适用于错误恢复场景，即父通信域可能已经处于卡死状态。父通信域的资源此时仍不会被释放，用户应自行决定是否需要在 shrink 之后对父通信域调用 `pcclCommAbort`。取值：`0x01`。

比赛关联：`pcclCommSplit` + `splitShare` 是推理框架从全局通信域派生 TP 子通信域的标准做法；`pcclConfig_t` 的 `minCTAs/maxCTAs/CTAPolicy` 是控制通信占用多少 SM 资源的旋钮，直接影响通信与 decode 计算的竞争关系。

## 7. 环境变量使用指南

本章节介绍 PCCL 运行过程中可用的环境变量配置项。

### 7.1. 网络传输配置

本章节介绍用于配置网络传输层的环境变量，包括 Socket、RDMA 等网络接口的配置选项。

#### 7.1.1. PCCL_SOCKET_IFNAME

`PCCL_SOCKET_IFNAME` 用于指定通信时应使用哪些 IP 网络接口。

取值说明：

设置为一个前缀列表，用于筛选 PCCL 可使用的网卡接口。

多个前缀可以使用 `,` 分隔。

使用 `^` 前缀时，表示排除所有以这些前缀开头的接口。

如果要精确匹配某个接口名，需要在前缀前加上 `=`。

示例：

- `eth`：使用所有以 `eth` 开头的接口，例如 `eth0`、`eth1` 等。
- `=eth0`：仅使用接口 `eth0`。
- `=eth0,eth1`：仅使用接口 `eth0` 和 `eth1`。
- `^docker`：不使用所有以 `docker` 开头的接口。
- `^=docker0`：不使用接口 `docker0`。

> **注意**：默认情况下，PCCL 不会选择回环接口 `lo` 和 docker 接口（`docker*`），除非系统中没有其他可用接口。如果希望优先使用 `lo` 或 `docker*`，需要显式设置 `PCCL_SOCKET_IFNAME`。默认算法还会优先选择以 `ib` 开头的接口。设置 `PCCL_SOCKET_IFNAME` 后，将绕过自动选网卡逻辑，并可能使用所有满足手动筛选条件的接口。

#### 7.1.2. PCCL_SOCKET_FAMILY

`PCCL_SOCKET_FAMILY` 用于强制 PCCL 仅使用 IPv4 或 IPv6 接口。

取值说明：

- `AF_INET`：强制使用 IPv4。
- `AF_INET6`：强制使用 IPv6。

#### 7.1.3. PCCL_SOCKET_RETRY_CNT

`PCCL_SOCKET_RETRY_CNT` 用于指定在出现 `ETIMEDOUT`、`ECONNREFUSED` 或 `EHOSTUNREACH` 错误后，PCCL 重试建立 socket 连接的次数。

取值说明：

默认值为 `34`，任意正整数均有效。

#### 7.1.4. PCCL_SOCKET_RETRY_SLEEP_MSEC

`PCCL_SOCKET_RETRY_SLEEP_MSEC` 用于指定在第一次出现 `ETIMEDOUT`、`ECONNREFUSED` 或 `EHOSTUNREACH` 错误后，PCCL 在重试建立 socket 连接前等待的毫秒数。对于后续错误，等待时间会随错误次数线性增长。

因此，总等待时间为 `(N+1) * N / 2 * PCCL_SOCKET_RETRY_SLEEP_MSEC`，其中 `N` 由 `PCCL_SOCKET_RETRY_CNT` 指定。使用默认值时，总重试时间大约为 60 秒。

取值说明：

默认值为 `100` 毫秒，任意正整数均有效。

#### 7.1.5. PCCL_SOCKET_NTHREADS

`PCCL_SOCKET_NTHREADS` 用于指定 socket 传输中，每条网络连接使用的 CPU 辅助线程数量。增大该值可能提升 socket 传输性能，但也会增加 CPU 占用。

取值说明：

取值范围为 `1` 到 `16`。

对于通用 100G 网络，可手动设置为 `4`。但 `PCCL_SOCKET_NTHREADS * PCCL_NSOCKS_PERTHREAD` 的乘积不能超过 `64`。另请参见 `PCCL_NSOCKS_PERTHREAD`。

#### 7.1.6. PCCL_NSOCKS_PERTHREAD

`PCCL_NSOCKS_PERTHREAD` 用于指定 socket 传输中，每个辅助线程打开的 socket 数量。在单 socket 带宽受限的环境中，将该值设置为大于 1 可能会提升网络性能。

取值说明：

- 默认值因平台实现与运行环境而异。

对于通用 100G 网络，可手动设置为 `4`。但 `PCCL_SOCKET_NTHREADS * PCCL_NSOCKS_PERTHREAD` 的乘积不能超过 `64`。另请参见 `PCCL_SOCKET_NTHREADS`。

#### 7.1.7. PCCL_CROSS_NIC

`PCCL_CROSS_NIC` 用于控制 PCCL 是否允许 ring/tree 在不同节点上使用不同的 NIC，即是否允许跨 NIC 进行节点间通信。

在多 NIC 场景下，为了获得更高的节点间通信性能，PCCL 会尽量让不同节点之间使用相同编号的 NIC，以适配每个 NIC 分别连接到不同交换机（rail）的网络设计，从而减少流量干扰。因此，这个参数是否合适，取决于具体的网络拓扑，尤其取决于网络是否针对 rail 做了优化。

该变量在只有一个 NIC 的系统上不生效。

取值说明：

- `0`：始终为相同 ring/tree 使用相同 NIC，避免跨 rail。适用于每个 NIC 分别连接到独立交换机，且 rail 之间互联较慢的网络。注意，如果通信域中各节点的 PPU 布局不一致，PCCL 仍可能需要跨 NIC 通信。
- `1`：允许相同 ring/tree 使用不同 NIC。适用于同一节点上的所有 NIC 都连接到同一个交换机的网络，此时强制使用相同 NIC 并不能避免流量冲突。
- `2`：默认值。尽量对相同 ring/tree 使用相同 NIC，但如果使用不同 NIC 可以获得更好性能，也允许这样做。

#### 7.1.8. PCCL_IB_HCA

`PCCL_IB_HCA` 用于指定通信时应使用哪些 Host Channel Adapter（RDMA）接口。

取值说明：

设置为一个筛选列表，用于过滤 PCCL 可使用的 IB Verbs 接口。列表使用 `,` 分隔；可使用 `:` 指定端口号。

可选前缀：

- `^`：表示排除列表。
- `=`：表示精确匹配名称；若不加，则默认按前缀匹配。

示例：

- `mlx5`：使用所有名称以 `mlx5` 开头的卡上的所有端口。
- `=mlx5_0:1,mlx5_1:1`：使用 `mlx5_0` 和 `mlx5_1` 两张卡的 1 号端口。
- `^=mlx5_1,mlx5_4`：不使用 `mlx5_1` 和 `mlx5_4`。

> **注意**：如果设置为 `mlx5_1` 且不加 `=`，则除了 `mlx5_1` 之外，还会匹配 `mlx5_10` 到 `mlx5_19`（若存在）。因此通常建议使用 `=` 做精确匹配。

> **注意**：PCCL 最多支持 `32` 个 HCA 设备。

#### 7.1.9. PCCL_IB_TIMEOUT

`PCCL_IB_TIMEOUT` 用于控制 InfiniBand Verbs 的超时时间。

超时时间按 `4.096 µs * 2 ^ timeout` 计算，最佳取值取决于网络规模。在非常大的网络中增大该值可能有帮助，例如当 PCCL 在调用 `ibv_poll_cq` 时出现 error 12。

总等待时间还取决于 `PCCL_IB_RETRY_CNT`，即总响应等待时间约等于 `PCCL_IB_TIMEOUT * PCCL_IB_RETRY_CNT`。

取值说明：

默认值为 `20`。

可设置范围为 `0` 到 `31`。

> **注意**：设置为 `0` 或大于等于 `32` 时，将得到无限超时。

#### 7.1.10. PCCL_IB_RETRY_CNT

`PCCL_IB_RETRY_CNT` 用于控制 InfiniBand 的重试次数。总重试等待时间由重试次数与超时时间的乘积决定。

例如，使用默认配置 `PCCL_IB_TIMEOUT=20` 和 `PCCL_IB_RETRY_CNT=7` 时，网络错误被报告前大约会等待 30 秒。

取值说明：

默认值为 `7`，有效取值范围为 `0` 到 `7`。

#### 7.1.11. PCCL_IB_GID_INDEX

`PCCL_IB_GID_INDEX` 用于指定在 RoCE 模式下使用的 Global ID 索引。可参考 InfiniBand 的 `show_gids` 命令来设置该值。

取值说明：

默认值为 `-1`。

#### 7.1.12. PCCL_IB_ADDR_FAMILY

`PCCL_IB_ADDR_FAMILY` 用于定义当 `PCCL_IB_GID_INDEX` 未设置时，PCCL 动态选择的 InfiniBand GID 所对应的 IP 地址族。

取值说明：

默认值为 `AF_INET`。

#### 7.1.13. PCCL_IB_ADDR_RANGE

`PCCL_IB_ADDR_RANGE` 用于定义当 `PCCL_IB_GID_INDEX` 未设置时，PCCL 动态选择 GID 的合法范围。

取值说明：

默认不设置该参数。

GID 范围可使用 IPv4 或 IPv6 的 CIDR 格式指定。

#### 7.1.14. PCCL_IB_ROCE_VERSION_NUM

`PCCL_IB_ROCE_VERSION_NUM` 用于定义当 `PCCL_IB_GID_INDEX` 未设置时，PCCL 动态选择的 InfiniBand GID 所对应的 RoCE 版本号。

取值说明：

默认值为 `2`。

#### 7.1.15. PCCL_IB_SL

`PCCL_IB_SL` 用于定义 InfiniBand Service Level。

取值说明：

默认值为 `0`。

#### 7.1.16. PCCL_IB_TC

`PCCL_IB_TC` 用于定义 InfiniBand 的 traffic class 字段。

取值说明：

默认值为 `0`。

#### 7.1.17. PCCL_IB_DISABLE

`PCCL_IB_DISABLE` 用于禁止 PCCL 使用 IB/RoCE 传输。设置后，PCCL 会回退到使用 IP sockets。

取值说明：

设置为 `1` 以禁用基于 InfiniBand Verbs 的通信（并强制使用其他方式，例如 IP sockets）。

#### 7.1.18. PCCL_IB_AR_THRESHOLD

`PCCL_IB_AR_THRESHOLD` 用于指定阈值。当消息大小超过该阈值时，PCCL 会将 InfiniBand 数据拆分为单独消息发送，从而利用 adaptive routing。

取值说明：

单位为字节，默认值为 `8192`。

如果将其设置为大于 `PCCL_BUFFSIZE`，将完全禁用 adaptive routing。

#### 7.1.19. PCCL_IB_QPS_PER_CONNECTION

`PCCL_IB_QPS_PER_CONNECTION` 用于指定每两个 rank 之间的每条连接使用多少个 IB queue pairs。在多层网络中，使用多个 QP 可以获得更好的路由熵。不同的数据拆分方式可能影响性能，另见 `PCCL_IB_SPLIT_DATA_ON_QPS`。

取值说明：

取值范围为 `1` 到 `128`，默认值为 `1`。

#### 7.1.20. PCCL_IB_SPLIT_DATA_ON_QPS

`PCCL_IB_SPLIT_DATA_ON_QPS` 用于控制当创建多个 queue pair 时如何使用它们。

设置为 `1`（split 模式）时，每条消息会平均拆分到各个 queue pair 上；如果 QP 数量很多，可能会带来明显的延迟上升。

设置为 `0`（round-robin 模式）时，queue pair 会按轮询方式用于每条发送消息；不发送多条消息的操作不会使用到所有 QP。

取值说明：

- `0` 或 `1`
- 默认值为 `0`
- 设置为 `1` 时启用 split 模式

#### 7.1.21. PCCL_IB_DISABLE_ACC_BONDING_PORT

`PCCL_IB_DISABLE_ACC_BONDING_PORT` 用于控制是否关闭获取 bonding 网口速率的功能。

取值说明：

- `0` 或 `1`
- 默认值为 `0`

#### 7.1.22. PCCL_IB_NIC_SPEED_SCALING_FACTOR

`PCCL_IB_NIC_SPEED_SCALING_FACTOR` 用于设置 IB 网卡速率的 scale 系数。

取值说明：

- 默认值为 `1`

#### 7.1.23. PCCL_OOB_NET_ENABLE

`PCCL_OOB_NET_ENABLE` 用于启用基于 PCCL net 的带外通信。启用后，通信域初始化阶段执行的 allgather 实现方式会发生变化。

取值说明：

- `0`：禁用。
- `1`：启用。

#### 7.1.24. PCCL_OOB_NET_IFNAME

如果启用了 `PCCL_OOB_NET_ENABLE`，则 `PCCL_OOB_NET_IFNAME` 用于指定带外通信应使用哪些网络接口。

取值说明：

设置为一个过滤列表，用于筛选带外通信可使用的接口。具体可接受的接口取决于 PCCL 所使用的网络模块。列表使用 `,` 分隔；可使用 `:` 指定端口号。

可选前缀：

- `^`：表示排除列表。
- `=`：表示精确匹配；若不加，则按前缀匹配。

如果指定多个接口，PCCL 会选择列表中第一个匹配的接口。

示例：

- `PCCL_NET="IB" PCCL_OOB_NET_ENABLE=1 PCCL_OOB_NET_IFNAME="=mlx5_1"`：使用 Infiniband NET，并使用接口 `mlx5_1`。
- `PCCL_NET="IB" PCCL_OOB_NET_ENABLE=1 PCCL_OOB_NET_IFNAME="mlx5_1"`：使用 Infiniband NET，并从 `mlx5_1`、`mlx5_10`、`mlx5_11` 等中选择第一个匹配项。
- `PCCL_NET="Socket" PCCL_OOB_NET_ENABLE=1 PCCL_OOB_NET_IFNAME="ens1"`：使用 socket NET，并从 `ens1f0`、`ens1f1` 等中选择第一个匹配项。

#### 7.1.25. PCCL_NET

`PCCL_NET` 用于强制 PCCL 使用指定网络模块，例如确保 PCCL 使用某个外部插件，而不是自动回退到内部的 IB 或 Socket 实现。

设置该变量后，会覆盖所有通信域中的 `netName` 配置（见 `pcclConfig_t`）：

- 若未设置，则由配置决定；
- 若调用时也未传配置，则 PCCL 会自动选择最佳网络模块。

取值说明：

取值必须与目标 PCCL 网络模块名称完全匹配（大小写不敏感）。内部网络名称包括：

- `IB`：通用 IB verbs
- `Socket`：TCP/IP sockets

外部网络插件可定义自己的名称。默认值为未定义。

#### 7.1.26. PCCL_NET_PLUGIN

`PCCL_NET_PLUGIN` 用于在多个 PCCL net 插件中选择一个，可设置为后缀字符串或完整库名。

加载策略如下：

1. 若设置了 `PCCL_NET_PLUGIN`，先尝试按该值直接加载库；
2. 若失败，再尝试加载 `libpccl-net-<PCCL_NET_PLUGIN>.so`；
3. 若未设置，则尝试加载 `libpccl-net.so`；
4. 若仍未找到插件，则使用内部网络插件。

例如，设置 `PCCL_NET_PLUGIN=ppu` 时，PCCL 会先尝试将 `ppu` 作为库名直接加载，失败后再尝试 `libpccl-net-ppu.so`。

取值说明：

插件后缀、插件文件名，或 `none`。

#### 7.1.27. PCCL_NET_AFFINITY

`PCCL_NET_AFFINITY` 用于指定 PPU 与网卡之间的亲和性。

取值说明：

- 格式：`ppuid:netid[,ppuid:netid]`
- 默认不设置

### 7.2. 性能优化

本章节介绍用于调优 PCCL 性能的环境变量，包括算法选择、协议配置、通信参数、P2P 传输等优化选项。

#### 7.2.1. PCCL_PROTO

`PCCL_PROTO` 用于定义 PCCL 允许使用哪些协议。

通常不建议主动设置该变量，除非为了排查 PCCL 可能存在的问题而需要临时禁用某种协议。特别是，在不支持 LL128 的平台上强行启用 LL128 可能会导致数据损坏。

取值说明：

可设置为不区分大小写的逗号分隔协议列表，包括：`LL`、`LL128`、`Simple`、`Signal`、`SimpleBulk`、`SignalBulk`、`SimpleBulkAR`。

若要指定“排除哪些协议”而不是“包含哪些协议”，可在列表前加 `^`。

默认行为是启用所有支持的协议。该变量也支持为不同函数指定不同协议。

#### 7.2.2. PCCL_ALGO

`PCCL_ALGO` 用于定义 PCCL 允许使用哪些算法。

取值说明：

可设置为不区分大小写的逗号分隔算法列表，包括：

- `Ring`
- `Tree`
- `FC`

若要指定“排除哪些算法”而不是“包含哪些算法”，可在列表前加 `^`。

该变量支持更灵活的“按函数分别指定算法”的形式。如果解析到未知算法，会给出警告并失败。并且如果未将 `ring` 显式列为某个函数的合法算法，则不会在无可用算法时隐式回退到 ring，而是直接失败。

此时格式为：由分号分隔的“函数名 + 算法列表”对，其中第一个条目的函数名可以省略；若省略，则适用于所有未在后续单独列出的函数。函数名与算法列表之间使用 `:` 分隔，算法列表内部使用 `,` 分隔；若算法列表首字符为 `^`，则表示反选。

例如：

- `PCCL_ALGO="ring,tree;allreduce:tree,ring;broadcast:ring"`
- `PCCL_ALGO=allreduce:^tree`

默认情况下该变量未设置，此时 PCCL 会根据节点拓扑与架构自动选择可用算法。

#### 7.2.3. PCCL_BUFFSIZE

`PCCL_BUFFSIZE` 用于控制 PCCL 在 PPU 之间传输数据时使用的缓冲区大小。

如果在使用 PCCL 时遇到内存约束问题，或者认为调整缓冲区大小可以改善性能，可以使用该变量。

取值说明：

默认值为 `4194304`（4 MiB）。

取值为字节数整数。通常建议使用 2 的幂，例如 `1024` 表示 1 KiB 缓冲区。

#### 7.2.4. PCCL_NTHREADS

`PCCL_NTHREADS` 用于设置每个 HGGC block 中的 HGGC 线程数。PCCL 会为每个通信 channel 启动一个 HGGC block。

如果认为 PPU 时钟较低并希望增加线程数，可以使用该变量；也可以通过减少线程数来降低 PPU 负载。

取值说明：

默认值依平台而定。

允许的取值为：`64`、`128`、`256`、`512`。

#### 7.2.5. PCCL_MAX_NCHANNELS

`PCCL_MAX_NCHANNELS` 用于限制 PCCL 可使用的最大 channel 数。减少 channel 数也会减少通信所使用的 HGGC blocks 数量，因此会降低对 PPU 计算资源的占用。

取值说明：

任意大于等于 `1` 的值。

#### 7.2.6. PCCL_MIN_NCHANNELS

`PCCL_MIN_NCHANNELS` 用于控制 PCCL 使用的最小 channel 数。增加 channel 数通常也会增加 PCCL 使用的 HGGC blocks 数量，这可能有助于提升性能，但也会消耗更多 HGGC 计算资源。

在某些平台上，当使用聚合型集合通信而 PCCL 通常只会创建一个 channel 时，该变量特别有用。

旧的 `PCCL_MIN_NRINGS` 在新版本中仍可作为别名使用，但如果设置了 `PCCL_MIN_NCHANNELS`，则会被忽略。

取值说明：

默认值依平台而定。可设置为整数。

#### 7.2.7. PCCL_MAX_CTAS

`PCCL_MAX_CTAS` 用于设置 PCCL 可使用的最大 CTA 数量。环境变量优先级高于配置项，若环境变量和配置项都未设置，则默认值为 MAXCHANNELS（64）。

增大 CTA 数量会消耗更多 PPU 资源，但也可能提升吞吐。PCCL 通常优先追求吞吐，但在某些平台上，为了达到峰值吞吐可能需要消耗大量 PPU 资源，因此默认值可能会限制最大 CTA 数。这通常可以在 PPU 密集型应用中获得更平衡的性能，但也明显依赖具体工作负载；尤其在 benchmark 场景下，手动提高上限可能获得更高吞吐数据。

取值说明：

设置为正整数。默认值为未定义。

#### 7.2.8. PCCL_MIN_CTAS

`PCCL_MIN_CTAS` 用于设置 PCCL 应使用的最小 CTA 数量。环境变量优先级高于配置项，若环境变量和配置项都未设置，则默认值为 1。

对于每个集合通信操作，PCCL 都会估算一个最优 CTA 数。如果这个估算过于保守，可以通过增大最小 CTA 数来调整。需要注意的是，使用超过必要数量的 CTA 反而可能降低性能，尤其是在较小消息上，因此应谨慎使用（对于非常小的消息，PCCL 实际使用的 channel 数也可能少于 `PCCL_MIN_CTAS`）。

这个参数通常用于 benchmark 和测试，以强制使用特定数量的 channel；此时通常会将最小值和最大值设为相同。

取值说明：

设置为正整数。默认值为未定义。

#### 7.2.9. PCCL_CTA_POLICY

`PCCL_CTA_POLICY` 允许用户设置通信域的 CTA 策略。

取值说明：

- `DEFAULT`（或旧值 `0`）：使用 `PCCL_CTA_POLICY_DEFAULT` 策略，也是默认值。
- `EFFICIENCY`（或旧值 `1`）：使用 `PCCL_CTA_POLICY_EFFICIENCY` 策略。
- `ZERO`（或旧值 `2`）：使用 `PCCL_CTA_POLICY_ZERO` 策略。

多个非 legacy 策略可通过 `|` 进行组合。

#### 7.2.10. PCCL_P2P_DISABLE

`PCCL_P2P_DISABLE` 用于禁用 peer-to-peer（P2P）传输。P2P 传输通过 ICN 或 PCI 实现 PPU 之间的直接访问。

取值说明：

设置为 `1` 以禁用 PPU 之间的直接 P2P 通信。

#### 7.2.11. PCCL_P2P_LEVEL

`PCCL_P2P_LEVEL` 允许用户更细粒度地控制 PPU 之间何时启用 P2P 传输。该级别定义了 PCCL 可使用 P2P 的最大 PPU 拓扑距离，应使用表示拓扑路径类型的短字符串来指定启用 P2P 的拓扑范围。

如果未设置，PCCL 会根据运行时架构和环境自动选择一个合适值。

取值说明：

- `LOC`：从不使用 P2P（始终禁用）。
- `NVL`：当 PPU 通过 ICN 相连时使用 P2P。
- `PIX`：当 PPU 位于同一个 PCI 交换机下时使用 P2P。
- `PXB`：当 PPU 通过 PCI 交换机相连时使用 P2P（可能包含多跳）。
- `PHB`：当 PPU 位于同一个 NUMA 节点时使用 P2P，此时流量会经过 CPU。
- `SYS`：跨 NUMA 节点使用 P2P，可能跨越 SMP 互联（如 QPI/UPI）。

可接受的 legacy 整数值如下：

- `LOC`：`0`
- `PIX`：`1`
- `PXB`：`2`
- `PHB`：`3`
- `SYS`：`4`

大于 `4` 的值会被解释为 `SYS`。`NVL` 不支持 legacy 整数形式。

#### 7.2.12. PCCL_P2P_DIRECT_DISABLE

`PCCL_P2P_DIRECT_DISABLE` 用于禁止 PCCL 在同一进程内的多个 PPU 之间通过 P2P 直接访问用户缓冲区。当用户缓冲区由某些 API 分配，且这些 API 不会自动让缓冲区对同一进程内其他 PPU 可见时，可以使用该变量。

取值说明：

设置为 `1` 以禁用跨 PPU 的直接用户缓冲区访问。

#### 7.2.13. PCCL_P2P_PXN_LEVEL

`PCCL_P2P_PXN_LEVEL` 用于控制在 send/receive 操作中何时使用 PXN。

取值说明：

- `0`：禁用 send/receive 中的 PXN。
- `1`：当目标首选 NIC 无法通过 PCI 交换机访问时启用 PXN。
- `2`：默认值。始终使用 PXN，即使 NIC 通过 PCI 交换机相连，也会将节点内所有 PPU 的数据汇聚到中间 PPU 以最大化聚合效果。

#### 7.2.14. PCCL_SHM_DISABLE

`PCCL_SHM_DISABLE` 用于禁用共享内存（SHM）传输。当无法进行 P2P 时，SHM 会被用于 PPU 之间通信，此时会使用主机内存。禁用 SHM 后，PCCL 会改用网络（如 InfiniBand 或 IP sockets）在 CPU socket 之间通信。

取值说明：

设置为 `1` 以禁用通过共享内存（SHM）进行通信。

#### 7.2.15. PCCL_NET_GDR_LEVEL

`PCCL_NET_GDR_LEVEL`（原名 `PCCL_IB_GDR_LEVEL`）允许用户更细粒度地控制在 NIC 与 PPU 之间何时使用 PPU Direct RDMA。该级别定义了 NIC 与 PPU 之间允许启用 GDR 的最大距离。

如果未设置，PCCL 会根据运行时架构和环境自动选择一个合适值。

取值说明：

- `LOC`：从不使用 PPU Direct RDMA（始终禁用）。
- `PIX`：当 PPU 与 NIC 位于同一个 PCI 交换机下时使用 PPU Direct RDMA。
- `PXB`：当 PPU 与 NIC 通过 PCI 交换机相连时使用 PPU Direct RDMA（可能包含多跳）。
- `PHB`：当 PPU 与 NIC 位于同一个 NUMA 节点时使用 PPU Direct RDMA，此时流量会经过 CPU。
- `SYS`：即使跨 NUMA 节点之间的 SMP 互联（如 QPI/UPI），也使用 PPU Direct RDMA。

可接受的 legacy 整数值如下：

- `LOC`：`0`
- `PIX`：`1`
- `PXB`：`2`
- `PHB`：`3`
- `SYS`：`4`

大于 `4` 的值会被解释为 `SYS`。

#### 7.2.16. PCCL_NET_GDR_READ

`PCCL_NET_GDR_READ` 用于在发送数据时启用 PPU Direct RDMA，只要 PPU-NIC 距离位于 `PCCL_NET_GDR_LEVEL` 指定的范围内即可。

启用后，发送数据会直接从 PPU 内存传给 NIC，而不是先拷贝到 CPU 内存。

> **注意**：在某些平台（如 PCI-E）上，发送时直接从 PPU 内存读取数据，可能会比先读到 CPU 内存稍慢。

取值说明：

- `0` 或 `1`
- 设置为 `1` 时，发送数据会直接通过 PPU Direct RDMA 写入 NIC（绕过 CPU）
- 默认值依平台而定

#### 7.2.17. PCCL_NET_SHARED_BUFFERS

`PCCL_NET_SHARED_BUFFERS` 允许在节点间点对点通信中使用共享缓冲区。这会为所有远端 peer 使用一个统一的大缓冲池，而不是让缓冲区随远端 peer 数量线性增长，从而使内存占用保持恒定。

取值说明：

默认值为 `1`（启用），设置为 `0` 时禁用。

#### 7.2.18. PCCL_NET_SHARED_COMMS

`PCCL_NET_SHARED_COMMS` 用于在 PXN 场景中复用相同连接。这有助于消息聚合，但也可能降低网络包的熵。

取值说明：

默认值为 `1`（启用），设置为 `0` 时禁用。

#### 7.2.19. PCCL_NVB_DISABLE

`PCCL_NVB_DISABLE` 用于禁用通过中间 PPU 借助 ICN 实现的节点内通信。

由于 PPU 平台原生支持跨节点转发且无需占用中转节点的显存，PCCL 在多数场景下无需显式借助中间 PPU 中转即可完成通信。若观察到 NVB 路径带来额外开销、或希望禁止使用节点间路由转发，可通过该变量将其关闭。

取值说明：

默认值为 `0`，设置为 `1` 时禁用该机制。

#### 7.2.20. PCCL_PXN_DISABLE

`PCCL_PXN_DISABLE` 用于禁用通过非本地 NIC、借助 ICN 和中间 PPU 实现的节点间通信。

取值说明：

默认值为 `0`，设置为 `1` 时禁用该机制。

#### 7.2.21. PCCL_SYM_WARPS

`PCCL_SYM_WARPS` 用于指定 symmetric kernel 使用的 warp 数量。

取值说明：

- 取值范围为 `[1,16]`
- 默认值为 `16`

#### 7.2.22. PCCL_SYM_OP_ACC_PRECISION_INC

`PCCL_SYM_OP_ACC_PRECISION_INC` 用于指定 reduce 相关操作是否需要提升到 float 精度进行计算。

取值说明：

- `0` 或 `1`
- 默认值为 `0`，表示不提升；对于 fp8，仍会提升到 fp16，但不会进一步提升到 fp32

#### 7.2.23. PCCL_SYM_KERNEL_ID

`PCCL_SYM_KERNEL_ID` 用于指定 symmetric kernel 的 kernelId 并集。

取值说明：

- 根据需要配置。例如，若希望所有 kernel 都使用 LL 算法，可指定为 `37`

### 7.3. 内存与资源管理

本章节介绍用于配置内存分配、缓冲区注册等资源管理相关的环境变量。

#### 7.3.1. PCCL_CUMEM_ENABLE

`PCCL_CUMEM_ENABLE` 用于控制 PCCL 是否使用 HGGC `hgMem*` 系列函数分配内存。

取值说明：

- `0` 或 `1`
- 默认是否启用取决于系统支持情况；仍可通过 `PCCL_CUMEM_ENABLE` 覆盖自动探测结果

#### 7.3.2. PCCL_LOCAL_REGISTER

`PCCL_LOCAL_REGISTER` 用于在用户显式调用 `pcclCommRegister` 时启用本地用户缓冲区注册。

取值说明：

- `0` 或 `1`
- 默认值为 `1`（启用）

#### 7.3.3. PCCL_LEGACY_HGGC_REGISTER

`PCCL_LEGACY_HGGC_REGISTER` 用于控制是否允许注册通过 `HGGCMalloc`（及相关分配器）分配的 legacy HGGC 缓冲区。

使用旧版缓冲区注册可能引入隐式同步，这对 PCCL 不安全，并可能导致卡死。因此，PCCL 默认禁用旧版缓冲区注册，建议用户转向基于 `hgMem` 的内存分配器。

取值说明：

- `0` 或 `1`
- 默认值为 `0`（禁用）

#### 7.3.4. PCCL_GRAPH_REGISTER

`PCCL_GRAPH_REGISTER` 用于在 PCCL 调用被 HGGC Graph 捕获时启用用户缓冲区注册。

仅当以下条件同时满足时才生效：

1. 同一节点内所有 PPU 之间都具备 P2P 访问能力；
2. 每个进程至多只有一个 PPU。

用户缓冲区注册可以减少用户缓冲区与 PCCL 内部缓冲区之间的数据拷贝。当 HGGC Graph 被销毁时，用户缓冲区会自动注销。

取值说明：

- `0` 或 `1`
- 默认值为 `1`（启用）

#### 7.3.5. PCCL_GDR_USE_DEV_MEM_FOR_RX_TAIL

`PCCL_GDR_USE_DEV_MEM_FOR_RX_TAIL` 用于在 GDR 场景下，通过轮询 device 地址上的 tail 指针来判断数据是否到达。

取值说明：

- 默认值为 `1`

#### 7.3.6. PCCL_GDR_CPU_FLUSH

`PCCL_GDR_CPU_FLUSH` 用于在 GDR 场景下，通过 x86 指令发起 PCIe read 来完成数据 flush，以替代 local RDMA read。

取值说明：

- 默认值为 `0`

#### 7.3.7. PCCL_WIN_ENABLE

`PCCL_WIN_ENABLE` 用于启用窗口内存注册。

取值说明：

- `0` 或 `1`
- 默认值为 `1`（启用）

### 7.4. 通信域初始化

本章节介绍用于控制通信域初始化行为的环境变量，包括连接建立、拓扑检测、MNNVL 等配置。

#### 7.4.1. PCCL_RUNTIME_CONNECT

`PCCL_RUNTIME_CONNECT` 用于控制是否在运行期动态建立 peer 连接，例如在调用 `pcclAllreduce()` 时建立，而不是在初始化阶段完成。

取值说明：

默认值为 `1`，设置为 `0` 时会在初始化阶段建立 peer 连接。

#### 7.4.2. PCCL_UID_STAGGER_THRESHOLD

`PCCL_UID_STAGGER_THRESHOLD` 用于控制是否启用 PCCL rank 与 `pcclUniqueId` 之间通信的错峰机制，以避免 `pcclUniqueId` 过载。

如果参与通信的 PCCL rank 数量超过该阈值，则会根据 rank 值进行错峰（另见 `PCCL_UID_STAGGER_RATE`）；如果每个 `pcclUniqueId` 对应的 rank 数量小于或等于该阈值，则不会进行错峰。

例如，当有 128 个 PCCL rank、1 个 `pcclUniqueId`、阈值为 64 时，将启用错峰；但若有 2 个 `pcclUniqueId` 且总 rank 数仍为 128，则不会错峰。

取值说明：

必须为严格正整数。若未设置，默认值为 `256`。

#### 7.4.3. PCCL_UID_STAGGER_RATE

`PCCL_UID_STAGGER_RATE` 用于定义启用错峰通信时期望的消息速率。启用错峰时（见 `PCCL_UID_STAGGER_THRESHOLD`），该速率会用于计算某个 PCCL rank 应等待的时间。

取值说明：

必须为严格正整数，单位为消息/秒。若未设置，默认值为 `7000`。

#### 7.4.4. PCCL_BLOCKING_BOOTSTRAP

`PCCL_BLOCKING_BOOTSTRAP` 用于关闭 bootstrap socket 的异步通信模式。

取值说明：

- `0` 或 `1`
- 默认值为 `0`

#### 7.4.5. PCCL_LAUNCH_MODE

`PCCL_LAUNCH_MODE` 用于控制 PCCL 如何启动 HGGC kernels。

取值说明：

默认值为 `PARALLEL`。

设置为 `GROUP` 时，对于管理多个 PPU 的进程会使用 cooperative groups。该模式已废弃，未来版本中可能被移除。

#### 7.4.6. PCCL_COMM_BLOCKING

`PCCL_COMM_BLOCKING` 用于控制 PCCL 调用是否允许阻塞。这包括所有 PCCL 调用，例如 init/finalize 函数，以及由于 send/receive 懒连接初始化而可能阻塞的通信函数。

设置该环境变量后，会覆盖所有通信域中的 blocking 配置：

- 若未设置，则通信域行为由配置决定；
- 若调用时也未传配置，则通信域默认为阻塞。

取值说明：

- `0` 或 `1`
- `1` 表示阻塞通信域
- `0` 表示非阻塞通信域
- 默认值为未定义

#### 7.4.7. PCCL_CHECK_POINTERS

`PCCL_CHECK_POINTERS` 用于在每次集合通信调用时检查 HGGC 内存指针。该检查在开发阶段有助于调试，但会增加延迟。

取值说明：

默认值为 `0`，设置为 `1` 时启用检查。

设置为 `1` 时，会恢复到该功能的原始行为。

#### 7.4.8. PCCL_MNNVL_ENABLE

`PCCL_MNNVL_ENABLE` 用于在可用时启用 Multi-Node ICN（MNNVL）。如果系统或驱动不支持 Multi-Node ICN，则会自动禁用。该特性还要求启用 PCCL CUMEM 支持（`PCCL_CUMEM_ENABLE`）。MNNVL 要求构成 ICN 域的所有节点都已正确配置并正常运行 IMEX domain，更多细节可参考 HGGC 文档。

取值说明：

- `0`：禁用 MNNVL 支持。
- `1`：启用 MNNVL 支持；如果系统不支持或无法启用，PCCL 初始化会失败。
- `2`：自动探测 MNNVL 支持；若不支持或资源无法分配，不会导致失败。

#### 7.4.9. PCCL_MNNVL_UUID

`PCCL_MNNVL_UUID` 可用于将 Multi-Node ICN（MNNVL）的 UUID 设置为用户自定义值。给定值会同时赋给 128-bit UUID 的高 64 位和低 64 位。通常 MNNVL UUID 由 Fabric Manager 分配，一般无需手动覆盖。

取值说明：

64 位整数。

#### 7.4.10. PCCL_MNNVL_CLIQUE_ID

`PCCL_MNNVL_CLIQUE_ID` 可用于将 Multi-Node ICN（MNNVL）的 Clique Id 设置为用户自定义值。通常 Clique Id 由 Fabric Manager 分配，但该环境变量也可用于对 MNNVL 作业进行“软分区”，即 PCCL 只会将具有相同 `<UUID,CLIQUE_ID>` 的 rank 视为属于同一个 ICN 域。

取值说明：

32 位整数。

#### 7.4.11. PCCL_TOPO_FILE

`PCCL_TOPO_FILE` 用于指定一个 XML 文件路径，在拓扑探测前加载该文件。默认情况下，如果存在，PCCL 会先加载 `/var/run/nvidia-topologyd/virtualTopology.xml`。

取值说明：

可访问的文件路径，该文件描述部分或全部拓扑结构。

#### 7.4.12. PCCL_TOPO_DUMP_FILE

`PCCL_TOPO_DUMP_FILE` 用于指定一个文件路径，在完成拓扑探测后将 XML 拓扑信息导出到该文件。

取值说明：

文件路径，如果文件已存在则会被覆盖。

#### 7.4.13. PCCL_IGNORE_CPU_AFFINITY

`PCCL_IGNORE_CPU_AFFINITY` 用于使 PCCL 忽略作业指定的 CPU 亲和性，仅依据 PPU 亲和性进行选择。

取值说明：

默认值为 `0`。设为 `1` 时，PCCL 将忽略作业传入的 CPU affinity。

### 7.5. 插件配置

本章节介绍用于加载和配置 PCCL 插件的环境变量，包括 tuner、profiler、ext-kernel 等插件。

#### 7.5.1. PCCL_TUNER_PLUGIN

`PCCL_TUNER_PLUGIN` 用于在多个 PCCL tuner 插件中选择一个，可设置为后缀字符串或完整库名。

加载策略如下：

1. 若设置了 `PCCL_TUNER_PLUGIN`，先尝试按该值直接加载库；
2. 若失败，再尝试加载 `libpccl-net-<PCCL_TUNER_PLUGIN>.so`；
3. 若未设置，则尝试加载 `libpccl-tuner.so`；
4. 若未找到 tuner 插件，则继续在 net 插件中查找 tuner 符号（见 `PCCL_NET_PLUGIN`）；
5. 若仍未找到，则使用内部 tuner 插件。

例如，设置 `PCCL_TUNER_PLUGIN=ppu` 时，PCCL 会先尝试按 `ppu` 直接加载库，失败后再尝试 `libpccl-tuner-ppu.so`。

取值说明：

插件后缀、插件文件名，或 `none`。

#### 7.5.2. PCCL_PROFILER_PLUGIN

`PCCL_PROFILER_PLUGIN` 用于在多个 PCCL profiler 插件中选择一个，可设置为后缀字符串或完整库名。

加载策略如下：

1. 若设置了 `PCCL_PROFILER_PLUGIN`，先尝试按该值直接加载库；
2. 若失败，再尝试加载 `libpccl-profiler-<PCCL_PROFILER_PLUGIN>.so`；
3. 若未设置，则尝试加载 `libpccl-profiler.so`；
4. 若仍未找到插件，则不启用 profiling。

若设置为 `STATIC_PLUGIN`，则会在程序二进制中查找插件符号。

例如，设置 `PCCL_PROFILER_PLUGIN=ppu` 时，PCCL 会先尝试按 `ppu` 直接加载库，失败后再尝试 `libpccl-profiler-ppu.so`。

取值说明：

插件后缀、插件文件名，或 `none`。

#### 7.5.3. PCCL_EXT_KERNEL_PLUGIN

`PCCL_EXT_KERNEL_PLUGIN` 需要与 `PCCL_ENABLE_EXT_KERNEL` 配合使用，可用于指定 ext kernel 动态库。

取值说明：

- ext kernel 动态库路径或库名
- 默认使用 T-Head SAIL SDK 自带的 `libpccl-ext-kernel.so`

#### 7.5.4. PCCL_ENABLE_EXT_KERNEL

`PCCL_ENABLE_EXT_KERNEL` 用于启用 ext kernel，以优化小 size AllReduce 的性能。

取值说明：

- 默认启用

#### 7.5.5. PCCL_CONF_FILE

`PCCL_CONF_FILE` 允许用户指定一个静态配置文件路径。

> **注意**：该路径不支持 `~` 字符，请使用相对路径或绝对路径。

取值说明：

若未设置，则 PCCL 会在用户主目录下查找 `.pccl.conf`（如果存在）。

#### 7.5.6. PCCL_SET_THREAD_NAME

`PCCL_SET_THREAD_NAME` 用于为 PCCL CPU 线程设置更有意义的线程名，以便于调试与分析。

取值说明：

- `0` 或 `1`
- 默认值为 `0`（禁用）

### 7.6. 调试与诊断

本章节介绍用于调试和诊断 PCCL 问题的环境变量，包括日志输出、错误处理、状态监控等功能。

#### 7.6.1. PCCL_DEBUG

`PCCL_DEBUG` 用于控制 PCCL 输出的调试信息级别。该变量通常用于调试。

取值说明：

- `VERSION`：在程序启动时打印 PCCL 版本。
- `WARN`：当任意 PCCL 调用报错时打印明确的错误信息。
- `INFO`：打印调试信息。
- `TRACE`：为每一次调用打印可回放的 trace 信息。

#### 7.6.2. PCCL_DEBUG_SUBSYS

`PCCL_DEBUG_SUBSYS` 允许用户对 `PCCL_DEBUG=INFO` 输出按子系统进行过滤。该变量的值为逗号分隔的子系统列表，用于指定哪些子系统应出现在调试日志中。

在子系统名称前加 `^`，表示禁用该子系统日志。

取值说明：

默认值为 `INIT,BOOTSTRAP,ENV`。

支持的子系统名称包括：

- `INIT`：初始化
- `COLL`：集合通信
- `P2P`：点对点通信
- `SHM`：共享内存
- `NET`：网络
- `GRAPH`：拓扑探测与图搜索
- `TUNING`：算法/协议调优
- `ENV`：环境变量设置
- `ALLOC`：内存分配
- `CALL`：函数调用
- `PROXY`：代理线程操作
- `BOOTSTRAP`：早期初始化
- `REG`：内存注册
- `PROFILE`：初始化阶段的粗粒度性能分析
- `RAS`：可靠性、可用性与可维护性子系统
- `ALL`：包含所有子系统

#### 7.6.3. PCCL_DEBUG_DEV

`PCCL_DEBUG_DEV` 用于指定输出 debug 日志的 HGGC device id。

取值说明：

- HGGC device id
- 默认不设置

#### 7.6.4. PCCL_RAS_ENABLE

`PCCL_RAS_ENABLE` 用于启用 PCCL 的 RAS（可靠性、可用性、可维护性）子系统。RAS 可用于在程序运行期间查询 PCCL 作业的健康状态。

取值说明：

默认值为 `1`（启用）；设置为 `0` 时禁用 RAS。

#### 7.6.5. PCCL_RAS_ADDR

`PCCL_RAS_ADDR` 用于指定 RAS 子系统监听客户端连接的 socket 的 IP 地址与端口号。RAS 可以在多个进程之间共享该 socket，但如果一个节点上同时运行多个彼此独立的 PCCL 作业，通常不建议共享；若这些作业属于不同用户，操作系统甚至不会允许共享该 socket。因此，这种场景下应为每个作业使用不同的值，例如 `localhost:12345`、`localhost:12346` 等。

由于默认使用的是 `localhost`，只有能访问运行节点的用户才能连接该 socket。如有需要，也可以指定外部可访问网卡的地址，使 RAS 可从其他节点（例如集群 head node）访问，但这会带来安全影响，需要谨慎评估。

取值说明：

默认值为 `localhost:28028`。地址部分既可以使用主机名，也可以使用 IP 地址；若为 IPv6 地址，则需要使用方括号包裹，例如 `[::1]`。

#### 7.6.6. PCCL_RAS_TIMEOUT_FACTOR

`PCCL_RAS_TIMEOUT_FACTOR` 用于为 RAS 子系统中的所有超时设置一个统一的倍率因子。RAS 依赖多个 5 到 60 秒不等的超时来判断应用状态并维持内部通信，这些超时之间存在复杂的依赖关系。

当默认超时过小，例如高开销的调试、trace 等机制导致 PCCL 应用运行变慢，导致执行时间更不可预测时，可使用该变量以安全且一致的方式放大所有超时。如果希望在这种情况下继续使用 `pcclras` 客户端，客户端超时也可能需要相应增大（或关闭超时）。

取值说明：

默认值为 `1`。设置为更大值时，会增加所有超时。

#### 7.6.7. PCCL_STATE_MONITOR_LEVEL

`PCCL_STATE_MONITOR_LEVEL` 用于指定 hang monitor 的监测模式。

取值说明：

- `0`：关闭 hang monitor
- `1`：在 kernel 侧监控 polling marker 是否超时
- `2`：在 host 侧监控 kernel 执行时间是否超时
- `0` / `1` / `2`，默认值为 `1`

#### 7.6.8. PCCL_COMM_DUMP_SIGNAL

`PCCL_COMM_DUMP_SIGNAL` 用于指定触发进程执行 `dump_work_elem` 的 signal 编号。向目标进程发送该 signal 后，进程会执行相应的 dump。

取值说明：

- signal 编号整数
- 默认值为 `12`

#### 7.6.9. PCCL_COMM_DUMP_LEVEL

`PCCL_COMM_DUMP_LEVEL` 用于指定 hang dump 中包含的 debug 信息类型。

取值说明：

- `DUMP_ROUGH`：输出 workfifo 文本信息
- `DUMP_RAW` 或 `DUMP_BUFFER`：输出 workfifo 二进制信息（`.bin`）
- `DUMP_HWINFO`：输出 device status（`.core`）
- 可通过 `[DUMP_ROUGH,DUMP_RAW,DUMP_BUFFER,DUMP_HWINFO]` 指定包含项
- 也可通过 `^[DUMP_ROUGH,DUMP_RAW,DUMP_BUFFER,DUMP_HWINFO]` 指定排除项
- 默认值为 `DUMP_ROUGH`

#### 7.6.10. PCCL_DUMP_WORK_ELEMS

`PCCL_DUMP_WORK_ELEMS` 用于调试时输出每个 rank 实际执行的通信算子信息，例如 bytes、peer rank 等。使用该变量时，需要将 `PCCL_DEBUG` 设置为 `INFO`，并将 `PCCL_DEBUG_SUBSYS` 设置为 `PCCL_COLL|PCCL_P2P`。

取值说明：

- `0` 或 `1`
- 默认值依实现而定

#### 7.6.11. PCCL_DISABLE_ABORT

`PCCL_DISABLE_ABORT` 用于控制是否禁用 `pcclCommAbort` 中的主动 abort 通知机制。

取值说明：

- `0`（默认）：正常执行 abort，并通知未完成的通信任务退出。
- `1`：禁用该通知，不主动设置 abort flag，但仍继续执行后续清理流程。

#### 7.6.12. PCCL_ERROR_YIELD

`PCCL_ERROR_YIELD` 用于在出现错误日志时让 CPU 停留在当前位置，以便协助问题分析。

取值说明：

- 默认不启用

平台扩展关联：这些通信调优旋钮面向多卡推理，不属于本次单卡比赛路径；比赛报告不把 PCCL 配置列为优化项。

## 8. Debug 指南

本章节介绍使用 PPU 做多卡或多机模型训练时遇到 crash、hang 等问题时的 debug 方法，包括现场日志分析、复杂 hang 问题现场状态保存与离线分析等内容。

### 8.1. 快速现场初判

本节主要包含问题现场的常规分析方法，尝试从应用和系统层面诊断故障点。

#### 8.1.1. 应用日志分析

在上层应用所报的日志中我们主要关注 PCCL 初始化阶段的日志信息与上层应用（含框架/模型训练代码）中的 Error/Warning 等信息，需要在应用启动前配置环境变量 `PCCL_DEBUG=INFO`。

- PCCL 日志
  - 关注通信 ranks 间使用的传输类型，一般高效的单机内通信会发生在 ICN Link 链路上，而高效的多机间通信则会通过 IB 网卡参与的 RDMA 链路来进行。当日志中出现其他类型的 path type 时，就需要保持警惕，可以怀疑节点内的 ICN Link 状态或者节点之间网络是否存在问题。
    - 当发现机内 ICN Link 连接问题时，在问题机器上使用 `ppu-smi topo -m` 观察机内 topo 是否符合预期。
    - 当出现 IB 相关问题时，在问题机器上使用 IB 相关工具检查网络是否正常。
  - 关注 topo 创建的情况。进一步可以通过设置 `PCCL_TOPO_DUMP_FILE` 和 `PCCL_GRAPH_DUMP_FILE` 将初始化阶段生成的 topo 或 graph dump 到文件中做离线分析。
  - 特别地，当任务配置了 `PCCL_DEBUG_SUBSYS=ALL` 或者 `PCCL_DEBUG_SUBSYS=COLL` 时，可以解析通信 op 的执行序列。
- 框架日志中的 Error 情况
  - 通过检查参与通信的各个进程执行的状态，检查是否有某 rank 对应的进程或线程提前退出的情况，此时其他 peer rank 对应的进程或线程因某步通信同步未能得到响应一般会陷入 hang 的状态，乃至可能会 timeout 退出。当上述情况发生时，一般需要先检查异常 rank 提前退出的原因。

下面 8.1.1.1 与 8.1.1.2 小节中我们将重点说明下如何得到 PCCL 执行时生成日志及关键 topo / graph dump 文件以进一步做分析的方法。

##### 8.1.1.1. PCCL Topo & Graph 分析

配置 `PCCL_TOPO_DUMP_FILE=pccl_topo.xml` 和 `PCCL_GRAPH_DUMP_FILE=pccl_graph.xml`，PCCL 初始化完成后，会在当前路径生成类似 pccl_topo_rank0000.xml、pccl_topo_rank0001.xml、pccl_graph.xml 的 XML 文件。

Topo 文件示意如下，可以检查系统中的 PPU 和网卡连接关系是否符合预期。

```toml
<system version="1">
  <cpu numaid="0" affinity="ffffffff,ffffffff,ffffffff" arch="x86_64" vendor="GenuineIntel" familyid="6" modelid="85">
    <pci busid="0001:05:00.0" class="0x030200" link_speed="8 GT/s" link_width="16">
      <gpu dev="0" sm="89" rank="0" gdr="0">
        <icnlink target="ffff:ff:ff:ff" count="8" tclass="0x068000" />
      </gpu>
    </pci>
    <pci busid="0001:5B:00.0" class="0x030200" link_speed="8 GT/s" link_width="16">
      <gpu dev="1" sm="89" rank="1" gdr="0">
        <icnlink target="ffff:ff:ff:ff" count="8" tclass="0x068000" />
      </gpu>
    </pci>
  </cpu>
</system>
```

Graph 文件示意如下，可以检查 ring/tree/fc 等算法 topo，以及 typeintra/typeinter 等连接类型是否符合预期。

```toml
<graphs version="1">
  <graph id="0" pattern="4" crossnic="0" nchannels="8" speedintra="21" speedinter="21" typeintra="ICN" typeinter="PXN" samechannels="0">
    <channel>
      <net dev="0"/>
      <gpu dev="0"/>
      <gpu dev="1"/>
      <gpu dev="2"/>
      <gpu dev="3"/>
      <gpu dev="5"/>
      <gpu dev="4"/>
      <gpu dev="7"/>
      <gpu dev="6"/>
      <net dev="0"/>
    </channel>
    <channel>
      <net dev="1"/>
      <gpu dev="1"/>
      <gpu dev="2"/>
      <gpu dev="3"/>
      <gpu dev="5"/>
      <gpu dev="7"/>
      <gpu dev="4"/>
      <gpu dev="6"/>
      <gpu dev="0"/>
      <net dev="1"/>
    </channel>
    <!-- 省略展示 -->
  </graph>
</graphs>
```

##### 8.1.1.2. PCCL 日志分析

PCCL 日志分为两部分：初始化过程日志和运行时过程日志。在开启 `PCCL_DEBUG=INFO` 后，如无其他 `PCCL_DEBUG_SUBSYS` 设置，默认显示部分初始化过程日志。每行日志格式为“[*HostName*][*ProcessId*:*ThreadId*][*DeviceId*][*FileName*:*LineNumber*] PCCL <*INFO/WARN/VERBOSE/ERROR*> <*具体日志信息*>”。

日志默认打印到终端，通过配置环境变量可以选择区分 comm，hostname 和 pid 分别打印到不同的文件中，具体配置方法如下：

- 如果不需要区分 comm，可以配置 `PCCL_DEBUG_FILE=xxx-%h-%p.log`，那么日志路径为 xxx-hostname-pid.log，%h 和 %p 是可选的，配上后会按照 hostname 和 pid 的不同而分别进行日志文件存放。
- 如果需要区分 comm，可以配置 `PCCL_PER_COMM_HASH_DEBUG_FILE=xxx-%c-%h-%p.log`，那么日志路径为 xxx-commHash-hostname-pid.log，pcclCommInitAll 或者 pcclCommInitRank 之前的打印，仍然按照原规则不变：如果没有配 `PCCL_DEBUG_FILE`，打印在屏幕，配了 `PCCL_DEBUG_FILE`，打印在对应路径下。

限制：目前当需要区分 comm 来输出 log 到不同文件时，设置 `PCCL_PER_COMM_HASH_DEBUG_FILE` 这种方式只支持一个线程起一个通信 comm 的情况，如果一个线程有多个 comms，所有 comms 的日志都会打印到第一次调用 pcclCommInitAll 或者 pcclCommInitRank 使用的 comms 对应的日志文件。

在默认的日志中，我们主要关心以下信息：

- 机内 peer 之间是否选择 ICN P2P（某些异常情况如机器内部发生 ICN Link down，或者 PPU 间没有直接的 ICN Link 链接时会使用 SHM 或者 PCIe P2P），日志中有“via P2P/IPC”表示两个 peer 之间选择了 ICN P2P。

  ```text
  [xxx][xxx:xxx][6][p2p.cc:xxx] PCCL INFO Channel 01 : 6[1aa000] -> 4[110000] via P2P/IPC ...
  [xxx][xxx:xxx][6][p2p.cc:xxx] PCCL INFO Channel 06 : 6[1aa000] -> 4[110000] via P2P/IPC ...
  ```

- 跨节点的 peer 之间是否选择 RDMA，以及是否通过较高性能的 GDR 方式进行 PPU 与网卡间数据传输，日志中有“via NET/IB”表示两个 peer 之间选择了 RDMA。

  ```text
  [xxx][xxx:xxx][6][net.cc:xxx] PCCL INFO Channel 14/0 : 6[1aa000] -> 14[1aa000] [send] via NET/IB/6/GDRDMA
  [xxx][xxx:xxx][0][net.cc:xxx] PCCL INFO Channel 00/0 : 0[8000] -> 8[8000] [send] via NET/IB/0/GDRDMA
  ```

- 还有一种特殊情况，即部分节点的初始化日志已经显示完成，但存在一些节点的初始化日志不全，这种情况一般意味某些 rank 因某种原因尚未参与/或部分参与初始化。需要定位 host 侧原因。它的出现往往会发生在训练或者推理的第一个 iteration。

#### 8.1.2. 系统 Dmesg 分析

在内核日志中，我们主要关注 PPU 和 RDMA NIC 相关的错误和报警信息。可通过如下 shell 命令过滤。

```bash
dmesg -T | grep IH
dmesg -T | grep Error
dmesg -T | grep mlx5
dmesg -T | grep Xid
```

> **注意**：需要确保 dmesg 信息的开始时间早于应用启动时间。如果有异常信息，它的发生事件应晚于任务启动时间。

### 8.2. Crash 现场分析

Crash 主要分为两类，一类是 crash in host，另一类是 crash in PPU.

#### 8.2.1. Crash in Host

建议使能操作系统的 coredump。通过配置 `ulimit -c unlimited` 打开。应用 crash 后会在相应的路径下生成 host coredump 文件。此时建议用户先 high level 做上层应用逻辑出错排查。

#### 8.2.2. Crash in PPU

##### 8.2.2.1. 现场分析与生成 coredump

PPU 上发生 crash 时应用会退出，同时在 dmesg 信息中有日志显示（`dmesg -T | grep IH -A2 -B2`）。PPU 不会默认生成 coredump，建议使用如下环境变量保存 lightweight 的 coredump。coredump 生成后用户可尝试使用 ppu-gdb 工具进一步做问题排查，复杂涉及到 T-Head SAIL SDK 中的 device kernels 出错也可找平头哥同学协助进行排查。

```bash
export UMD_ENABLE_COREDUMP_ON_EXCEPTION=1
export UMD_ENABLE_LIGHTWEIGHT_COREDUMP=1
export UMD_COREDUMP_FILE=${HOME}/hggc.core.%h.%p.%t
```

##### 8.2.2.2. 保持现场不生成 coredump

如果配置生成 coredump 发生 Exception 的 device 会在生成 coredump 文件后，退出程序，从而退出应用。此时只会生成一个 device 的 coredump 文件，丢失全局信息。

如果需要全局信息，可配置 `UMD_MUTE_DEV_ERR=1`，该环境变量在发生 IH 后，会保持住现场，方便用于检查全局现场（此时可使用[章节 8.3](#83-hang-现场分析) 的方案保存全局现场）。考虑部分框架像 PyTorch 在通信 kernel 执行超过一定时间仍不退出时会显式 abort 掉 kernel 执行，因此为了保持 PCCL kernel 异常现场，还需要额外设置环境变量 `PCCL_DISABLE_ABORT=1`.

> **注意**：此种 device 异常后保留现场不退出的做法与上述 8.2.2.1 节中介绍的保留 coredump 的方法是相冲突的，不要同时设置两种方法中提到的环境变量。另外它也不能保证所有的 device 异常现场都能成功保留。

### 8.3. Hang 现场分析

PCCL 内部集成了状态监控与状态保存功能。状态监控用于辅助判断 hang 状态，状态保存功能支持在 hang 发生时，保存通信库和硬件内部状态，用于后续进一步定位 hang 的原因。

#### 8.3.1. Hang 状态监控（Hang Monitor）

PCCL 内部会记录每个 rank 每次通信操作 kernel launch 到 PPU 上后持续的时间，超过 5 分钟（默认配置，可通过环境变量 `PCCL_STATE_MONITOR_TIMEOUT_MS` 配置，单位为毫秒）后无状态更新后，会报 WARNING（配置 `PCCL_DEBUG=INFO/WARN` 后可见），并触发状态保存，所有状态保存文件都默认位于 $HOME/.pccl 路径下。

```text
pccl/
├── comm_dump
│   ├── pccl_comm_dump_comm-<CommHash>_nranks-8_rank-0_hgmldev-0_<HostName>_pid-2588105_<Time>.txt
│   ├── pccl_comm_dump_comm-<CommHash>_nranks-8_rank-1_hgmldev-1_<HostName>_pid-2588106_<Time>.txt
│   ├── ...
└── state_monitor_dump
    ├── pccl_state_monitor_dump_comm-<CommHash>_nranks-8_rank-0_hgmldev-0_<HostName>_pid-2588105.txt
    ├── pccl_state_monitor_dump_comm-<CommHash>_nranks-8_rank-1_hgmldev-1_<HostName>_pid-2588106.txt
    ├── ...
```

状态保存包括 comm_dump、state_monitor_dump、proxy_dump 三个子目录，其中 proxy_dump 只在多机场景会产生。comm_dump 下每个文件对应一个 rank 在某一时刻产生的 dump 文件，文件内容包含当前的 workfifo 执行状态。state_monitor_dump 下每个文件对应一个 rank，文件内容包含该 rank 主动检测到 timeout 的日志。proxy_dump 与 comm_dump 类似，文件内容包含当前跨机收发状态。

更多可配置环境变量如下：

- `PCCL_DEBUG_DUMP_DIR=<dirpath>` 指定保存状态文件的目录。状态文件将保存在 <dirpath>/.pccl 目录下。默认保存在 $HOME/.pccl 目录下。
- `PCCL_STATE_MONITOR_LEVEL=[0,1,2]` 状态监控级别。0: 关闭状态监控；1: device 侧监控，能应对绝大部分 hang 场景且性能友好；2: host 侧监控，能应对所有 hang 场景但可能影响 latency。默认值为 1。
  - level 1 监控日志示例

  ```text
  [xxx][xxx:xxx][1][monitor.cc:xxx] PCCL WARN RAS kernel begins at work 2 may hang in polling, comm 0x7fb2cbfdb010, rank 1, nranks 8, commhash 87b6247dfe7939bf, channel 7, time 20260417-170058
  [xxx][xxx:xxx][1][monitor.cc:xxx] PCCL WARN RAS kernel begins at work 4 may hang in polling, comm 0x7f3bcf0fd010, rank 3, nranks 8, commhash 87b6247dfe7939bf, channel 6, time 20260417-170058
  ```

  - level 2 监控日志示例

  ```text
  [xxx][xxx:xxx][1][monitor.cc:xxx] PCCL WARN RAS no pending work(s) completed over 300.30 seconds, comm 0x7fe2d7df0010, rank 2, nranks 8, commhash 8ac0fc6d7c8364c2, channel 11, enqueued 5, completed 3, datetime 20260417-171657
  [xxx][xxx:xxx][1][monitor.cc:xxx] PCCL WARN RAS no pending work(s) completed over 300.30 seconds, comm 0x7f466067e010, rank 0, nranks 8, commhash 8ac0fc6d7c8364c2, channel 10, enqueued 5, completed 2, datetime 20260417-171657
  ```

- `PCCL_STATE_MONITOR_DISABLE=[0,1]` 是否关闭状态监控。1: 关闭状态监控；0: 开启状态监控。配置 `PCCL_STATE_MONITOR_DISABLE=1` 或 `PCCL_STATE_MONITOR_LEVEL=0` 状态监控都会被关闭，建议使用后者。
- `PCCL_STATE_MONITOR_DUMP_WHEN_EXCEPTION_DISABLE=1` 是否关闭自动状态保存。0: 不关闭，检测到 timeout 后会打印 warning 并且保存 comm/proxy dump 状态文件；1: 关闭，检测到 timeout 后只打印 warning 但是不保存任何状态文件。
- `PCCL_STATE_MONITOR_LOG_EVERY_MS=xx` 是否要显示实时的执行进度，以及每隔 xx 毫秒打印一次。xx=0: 不打印；xx>0: 每隔 xx 毫秒打印一次当前已入队和已结束的 op 数。
- `PCCL_STATE_MONITOR_DUMP_DIR_SIZE_LIMIT_MB=<MBytes>` 指定 dump 目录最大空间限制，默认 2GB.

PCCL 带有 RAS 功能，支持在运行时由用户主动查询执行状态、触发 comm/proxy dump，可以从独立发布的 PCCL 包下找到 pcclras 工具。

使用方法：

- 查询状态：pcclras

  ```text
  $ pcclras
  PCCL version 2.1.0 compiled with HGGC .
  HGML runtime version 12090, driver version 13000

  Job summary
  ===========

  Nodes   Processes     GPUs   Processes     GPUs
  (total) per node   per process  (total)    (total)
    1        4           1         4          4

  Communicators... (0.00s)
  =================

  Group  Comms   Nodes   Ranks   Ranks   Ranks   Status  Errors
  #    in group per comm per node per comm in group
  0       1        1       4       4       4    RUNNING MISMATCH

  Errors
  ======

  Warnings
  ========

  #0-0 (d159e5c7ed79bb41) MISMATCH
  Communicator ranks have different collective operation counts
  2 ranks have launched up to operation 5
  2 ranks have launched up to operation 1
  ```

- 触发 dump: pcclras -d 0x1

#### 8.3.2. Hang 状态保存

目前支持保存 3 种不同的状态文件：

- DUMP_ROUGH： 包含 communicator 中每个 channel 的 workFifo 与 peers（head/tail/step 等）信息，可直接打开。
- DUMP_RAW： 导出 communicator 整个 binary 空间，包含更多数据，二进制文件，需要特定解析程序打开。
- DUMP_HWINFO： core dump 文件，需要使用 ppu-gdb 解析。

通过配置 `PCCL_COMM_DUMP_LEVEL` 可以指定保存哪些文件，默认为 DUMP_ROUGH。例如：`PCCL_COMM_DUMP_LEVEL=DUMP_ROUGH,DUMP_RAW` 可同时保存 ROUGH 和 RAW 文件。所有状态文件默认位于用户 $HOME/.pccl/comm_dump 路径下，格式如前述。

触发状态保存有以下 2 种方法：

- 自动保存：如果状态监控发现有可疑 timeout 发生，会自动（无需用户参与）触发一次状态保存。
- pcclras 主动保存：`pcclras -d <dump_level>`

#### 8.3.3. Hang 状态分析

目前上述状态文件收集后尚不能自动解析并对问题类型做判断，尚需要转交给平头哥研发同学进一步做问题分析与定位。

比赛关联：多实例 serving 压测时最常见的事故就是通信 hang；`pcclras` 可在不杀进程的情况下查询各 rank 的通信域状态与 op 计数错位（MISMATCH），`PCCL_STATE_MONITOR_*` 系列变量则给出自动 hang 检测与现场 dump，是压测取证与稳定性排查的核心手段。

## 9. 已知问题

本章节汇总 PCCL 使用中遇到的已知问题及其解决方案或规避方法。

### 9.1. 环境与配置

#### 9.1.1. ICN Link 状态异常

**现象**：机内多卡通信时，PCCL 日志显示未使用 P2P/IPC 传输，而是回退到 SHM 或 PCIE P2P，导致通信性能下降。

**原因**：机内 ICN Link 状态异常或拓扑配置不符合预期。

**诊断方法**：
```bash
ppu-smi topo -m

```

**解决方案**：
1. 使用 `ppu-smi topo -m` 检查 ICN Link 连接状态，确认 PPU 之间的直连关系是否符合预期。
2. 如果发现 Link Down 或连接异常，联系硬件维护人员检查 ICN 物理连接。
3. 重启 PPU 驱动尝试恢复 Link 状态。

#### 9.1.2. RDMA 网络通信失败

**现象**：多机通信场景下，PCCL 初始化失败或通信发生挂起，日志中显示 RDMA 相关错误。

**原因**：IB/RoCE 网络配置问题、网卡驱动异常或防火墙阻断。

**首要建议**：在深入排查 PCCL 前，**先使用 `ib_*perf` 工具（如 `ib_write_bw`、`ib_read_bw`、`ib_send_bw`、`ib_send_lat`）验证节点间 RDMA 网络的连通性与性能**，确认底层网络本身工作正常且带宽/延迟符合预期。若测试本身即失败或性能异常，问题应先在网络层面解决，再回到 PCCL 侧。

`ib_*perf` 工具由社区 linux-rdma/perftest 项目提供，README 中有各子工具的详细用法说明。最小用法示例：

```bash
# 服务端
ib_write_bw -d mlx5_0 -F

# 客户端（指向服务端 IP）
ib_write_bw -d mlx5_0 -F <server_ip>
```

特别地，对于 `ibv_reg_mr` 注册失败，初始化或运行时日志中出现类似如下报错：
```text
PCCL ERROR Call to ibv_reg_mr failed with error Invalid argument
```

**可能原因与对应处理**：

1. **`alixpu_peermem` 驱动未安装**：PPU RDMA 通信依赖该内核模块提供 peer memory 注册能力。
    - 通过 `lsmod | grep alixpu_peermem` 确认是否加载；
    - 未加载则参考驱动安装文档手动安装该模块。
2. **系统开启了 IOMMU，导致 PDR / GDR 无法正常工作**：
    - 执行 `dmesg | grep -i iommu`，若有相关输出则表示 IOMMU 已开启；
    - 建议在内核启动参数中关闭 IOMMU（例如 `intel_iommu=off` 或 `iommu=off`）后重启。
3. **PCIe Large BAR 未 Enable**：需要将 strapping pin GPIO5 设置为 1。
    - 该项属于硬件层面的出厂配置，正常情况下出货前已完成设置；
    - 若确需调整，请联系硬件团队协助处理。
4. **系统资源限制不足**：RDMA 大量内存注册场景下，可能触发 memlock 上限。
    - 确保 `memlock` 为 `unlimited`；
    - 会话中可执行 `ulimit -l unlimited`；
    - 生产环境建议在 `/etc/security/limits.conf` 中设置 `* soft memlock unlimited` 与 `* hard memlock unlimited`。

#### 9.1.3. Docker 容器 shm 空间不足

**现象**：在容器化训练/推理环境下，PCCL 初始化或运行过程中出现 CPU 共享内存分配失败、`/dev/shm` 空间耗尽等错误。

**原因**：Docker 默认为容器分配的 `/dev/shm` 大小较小（一般为 64MB），无法满足 PCCL 在多进程通信、bootstrap 阶段的共享内存需求。

**推荐配置**（二选一）：

- **使用 `--ipc=host`**：让容器共享宿主机的 IPC 命名空间，`/dev/shm` 直接使用宿主机容量。

    ```bash
    docker run --ipc=host ...
    ```

- **显式指定 `--shm-size`**：为容器单独放大 `/dev/shm`，示例设置为 16GB。

    ```bash
    docker run --shm-size=16g ...
    ```

### 9.2. 性能相关

#### 9.2.1. 直连 PPU 服务器上的部分设备选择

**适用场景**：8 卡或 16 卡直连 PPU 服务器。

**建议**：

- 当使用的 rank 数少于服务器总卡数时（如 8 卡服务器中只使用 4 卡），应选择编号连续的设备（例如 `0/1/2/3` 或 `4/5/6/7`），以获得更优的通信性能。
- 采用 TP 2 / 4 / 8 配置进行模型训练时，建议提前了解所用机器的 ICN 拓扑（通过 `ppu-smi topo -m` 查看），据此选择最佳的设备分配方案。

### 9.3. 稳定性

#### 9.3.1. 集合通信 Hang

**现象**：执行集合通信操作时，部分或所有 rank 发生挂起，无法完成通信。

**原因**：rank 数量不匹配、通信参数不一致（count/datatype/op）、部分 rank 提前退出或崩溃。

**诊断方法**：
```bash
pcclras
pcclras -d 0x1
dmesg -T | grep -i "killed\|segfault"
```

**解决方案**：
1. 确认所有 rank 都调用了相同的集合通信操作，且参数完全一致。
2. 检查是否有 rank 因异常提前退出。
3. 如果在 MPI 程序中使用 PCCL，注意 progress 问题避免死锁。
4. 使用 `pcclras -d 0x1` 转储通信状态以供分析。

#### 9.3.2. AlltoAllV 在特定负载下的 ICN 超时（真武 810 / 810E）

**现象**：在直连拓扑下执行 AlltoAllV，若各 peer 间收发 sizes 差异显著且并发量极高，极少数情况下可能出现通信超时（`dmesg` 中表现为 `ERR_FAB_REQ_TO`）。常规负载下不会触发此现象。

**规避方法**：减少单次操作的 block 数目可有效规避。若已触发，执行 `ppu-smi -r` 即可恢复正常，不影响后续使用。

#### 9.3.3. 多 Communicator 并发场景下系统死锁

**现象**：多个 PCCL communicator 同时向同一个 PPU device 上提交通信操作且并发压力极高时，极个别情况下可能触发系统死锁。

**规避方法**：在应用层面将同一 device 的通信操作串行化，或减少每个 communicator 的 Channels 数量，降低冲突概率。

比赛关联：容器化部署推理服务时 `--ipc=host` 是必备项；多实例 serving 意味着同一 device 上可能有多个 communicator 并发，需按 9.3.3 的指引做串行化或减少 Channel 数规避死锁。
