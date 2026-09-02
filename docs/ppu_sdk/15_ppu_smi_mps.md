# PPU-SMI 与 MPS 多进程服务 <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [1. PPU-SMI 概述](#1-ppu-smi-概述)
- [2. 查看设备汇总信息](#2-查看设备汇总信息)
  - [2.1. 查看设备列表](#21-查看设备列表)
  - [2.2. 查看基本信息汇总](#22-查看基本信息汇总)
- [3. 查询设备信息](#3-查询设备信息)
  - [3.1. 通用查询](#31-通用查询)
  - [3.2. 选择性查询](#32-选择性查询)
- [4. 修改设备配置](#4-修改设备配置)
  - [4.1. 设备配置选项](#41-设备配置选项)
  - [4.2. 通用控制选项](#42-通用控制选项)
- [5. 收集设备统计信息](#5-收集设备统计信息)
  - [5.1. 打印格式](#51-打印格式)
  - [5.2. 统计 Metrics 说明](#52-统计-metrics-说明)
  - [5.3. 通用控制选项](#53-通用控制选项)
- [6. 监视设备状态](#6-监视设备状态)
  - [6.1. 监视 Metrics 说明](#61-监视-metrics-说明)
  - [6.2. 通用控制选项](#62-通用控制选项)
- [7. 监控进程状态](#7-监控进程状态)
  - [7.1. 监视 Metrics 说明](#71-监视-metrics-说明)
  - [7.2. 通用控制选项](#72-通用控制选项)
- [8. 查询 ICN 链路信息](#8-查询-icn-链路信息)
  - [8.1. 查询 ICN 链路状态](#81-查询-icn-链路状态)
  - [8.2. 查询 ICN 链路能力](#82-查询-icn-链路能力)
  - [8.3. 查询链路对端 PCI Bus ID](#83-查询链路对端-pci-bus-id)
  - [8.4. 查询链路对端信息](#84-查询链路对端信息)
  - [8.5. 查询线缆在位状态](#85-查询线缆在位状态)
  - [8.6. 查询链路位宽](#86-查询链路位宽)
  - [8.7. 查询链路到物理端口的映射](#87-查询链路到物理端口的映射)
  - [8.8. 查询链路统计数据和错误计数](#88-查询链路统计数据和错误计数)
  - [8.9. 查询链路吞吐量](#89-查询链路吞吐量)
- [9. 查询设备间拓扑信息](#9-查询设备间拓扑信息)
  - [9.1. 查询拓扑矩阵信息](#91-查询拓扑矩阵信息)
  - [9.2. 查询 RDMA 网卡设备列表](#92-查询-rdma-网卡设备列表)
  - [9.3. 查询指定 CPU 的亲和设备列表](#93-查询指定-cpu-的亲和设备列表)
  - [9.4. 查询临近的 PPU 设备列表](#94-查询临近的-ppu-设备列表)
  - [9.5. 查询两个 PPU 设备间最短路径](#95-查询两个-ppu-设备间最短路径)
  - [9.6. 查询设备间 P2P 能力](#96-查询设备间-p2p-能力)
- [10. 管理多设备实例 (MIG)](#10-管理多设备实例-mig)
  - [10.1. 查询 GPU Instance profile 信息](#101-查询-gpu-instance-profile-信息)
  - [10.2. 查询 GPU Instance profile 可能的创建位置](#102-查询-gpu-instance-profile-可能的创建位置)
  - [10.3. 创建 GPU Instance 实例](#103-创建-gpu-instance-实例)
  - [10.4. 查看 GPU Instance 信息](#104-查看-gpu-instance-信息)
  - [10.5. 删除 GPU Instance 实例](#105-删除-gpu-instance-实例)
  - [10.6. 复位 GPU Instance 实例](#106-复位-gpu-instance-实例)
  - [10.7. 查询 Compute Instance profile 信息](#107-查询-compute-instance-profile-信息)
  - [10.8. 查询 Compute Instance profile 可能的创建位置](#108-查询-compute-instance-profile-可能的创建位置)
  - [10.9. 创建 Compute Instance 实例](#109-创建-compute-instance-实例)
  - [10.10. 查询 Compute Instance 信息](#1010-查询-compute-instance-信息)
  - [10.11. 删除 Compute Instance 实例](#1011-删除-compute-instance-实例)
- [11. 管理虚拟化设备 (vGPU)](#11-管理虚拟化设备-vgpu)
  - [11.1. 查询支持的 vGPU 类型](#111-查询支持的-vgpu-类型)
  - [11.2. 查询可创建的 vGPU 类型](#112-查询可创建的-vgpu-类型)
  - [11.3. 创建 vGPU Instance 实例](#113-创建-vgpu-instance-实例)
  - [11.4. 查询已创建的 vGPU Instance 信息](#114-查询已创建的-vgpu-instance-信息)
  - [11.5. 查询已关联 VM 的 vGPU Instance 信息](#115-查询已关联-vm-的-vgpu-instance-信息)
  - [11.6. 删除 vGPU Instance 实例](#116-删除-vgpu-instance-实例)
- [12. 隔离 PPU 设备 (drain)](#12-隔离-ppu-设备-drain)
  - [12.1. 设置隔离状态](#121-设置隔离状态)
  - [12.2. 查询隔离状态](#122-查询隔离状态)
  - [12.3. 移除 PPU 设备](#123-移除-ppu-设备)
  - [12.4. 发现 PPU 设备](#124-发现-ppu-设备)
- [13. 管理性能监控功能 (gpm)](#13-管理性能监控功能-gpm)
  - [13.1. 设置性能监控输出状态](#131-设置性能监控输出状态)
  - [13.2. 查询性能监控输出状态](#132-查询性能监控输出状态)
  - [13.3. 查询性能监控采集状态](#133-查询性能监控采集状态)
- [14. 已知问题](#14-已知问题)
- [15. Release Notes](#15-release-notes)
  - [15.1. 新增改动](#151-新增改动)
- [16. MPS 多进程服务](#16-mps-多进程服务)
  - [16.1. MPS 开关](#161-mps-开关)
  - [16.2. MPS 配置](#162-mps-配置)
  - [16.3. MPS 用法](#163-mps-用法)


## 1. PPU-SMI 概述
T-Head SAIL（以下简称 SAIL）PPU-SMI（PPU System Management Interface）是一个基于 HGML（HG Management Library）的命令行工具，用于辅助用户管理和查看 PPU 设备。

通过 PPU-SMI 命令行工具，用户可以：

+ 修改设备配置 / 特性开关
+ 查询指定设备运行参数和特性使能状态
+ 收集运行数据 / 特定事件，导出至表格供后续分析
+ 分析各个应用程序的设备资源使用情况
+ 查询多个 PPU 设备的拓扑信息

## 2. 查看设备汇总信息

### 2.1. 查看设备列表
通过执行`ppu-smi -L`查看系统内 PPU 设备列表

```bash
root@0549cf16bb85:~# ppu-smi -L
PPU 0: PPU (UUID: GPU-019ea108-c110-0828-0000-0000c07e1a46)
PPU 1: PPU (UUID: GPU-019ea108-c120-040c-0000-0000c0267f1e)
```

列表包含如下信息：

+ 设备索引：设备上电后分配的从 0 开始的枚举编号
+ 设备名称
+ 设备 UUID

#### 2.1.1. MIG 设备信息
在开启 MIG 模式后，`ppu-smi -L`将显示 PPU 设备下属的 MIG 设备信息，示例如下：

```bash
root@0549cf16bb85:~# ppu-smi -L
PPU 0: PPU (UUID: GPU-019ea108-c110-0828-0000-0000c07e1a46)
PPU 1: PPU (UUID: GPU-019ea108-c120-040c-0000-0000c0267f1e)
    MIG g1.c1.i1, Device 0 (UUID: MIG-79c62632-04cc-574b-af7b-cb2e307121c85)
    MIG g1.c0.i0, Device 1 (UUID: MIG-79c62632-04cc-574b-af7b-cb2e307121c84)
```

### 2.2. 查看基本信息汇总
通过执行`ppu-smi`，无任何参数，可查看系统内 PPU 设备列表。

```bash
root@122d8d7a7e37:~# ppu-smi
Thu May  7 10:36:57 2026
+---------------------------------------------------------------------------------+
| PPU-SMI 1.28          Driver Version: 2.1.0-dbda51  HGGC Version: 13.0          |
+---------------------------------+------------------------+----------------------+
| PPU  Name        Persistence M. | Bus-Id                 | Volatile Uncorr. ECC |
| Fan  Temp  Perf   Pwr:Usage/Cap | Memory-Usage           | PPU-Util  Compute M. |
|                                 |                        |               MIG M. |
+=================================+========================+======================+
| 0  PPU-ZW810E        N/A        | 00000000:08:00.0       |                    0 |
| N/A  24C   N/A       74W / 400W | 49MiB / 98304MiB       |   4%        Default  |
|                                 |                        |             Disabled |
+---------------------------------+------------------------+----------------------+
| 1  PPU-ZW810E        N/A        | 00000000:7E:00.0       |                    0 |
| N/A  23C   N/A       77W / 400W | 9MiB / 98304MiB        |   0%        Default  |
|                                 |                        |             Disabled |
+---------------------------------+------------------------+----------------------+

+---------------------------------------------------------------------------------+
| Processes:                                                                      |
| PPU    GI   CI   PID      Type  Process name                         PPU Memory |
|        ID   ID                                                       Usage      |
+=================================================================================+
| 0      N/A  N/A  525179   C     hggc_test1                                48MiB |
| 0      N/A  N/A  525179   C     hggc_test2                                48MiB |
+---------------------------------------------------------------------------------+
```

查询结果分为两个表格，分别是`PPU设备列表`和`PPU进程列表`，其中当前设备不支持的信息，显示为`N/A`。

`PPU设备列表`表格信息说明如下：

+ PPU: 设备上电后分配的从 0 开始的枚举编号
+ Name: 设备名称
+ Persistence M.: 是否开启持久化模式（Persistence Mode）
+ Fan: 风扇目标转速占最大转速的百分比
+ Temp: 设备当前温度
+ Perf: 设备性能状态级别（performance state），P0 为最高性能，P1 / P2 等性能逐级下降，不支持时显示为`N/A`
+ Pwr:Usage/Cap: 当前设备功率（W） / 设备功率限制（W）
+ Bus-Id: 设备 PCI Bus Id
+ Memory-Usage: 已使用设备内存大小（MiB） / 总共设备内存大小（MiB）
+ Volatile Uncorr. ECC: 自驱动加载后，设备发生的所有不可纠错的 ECC 错误个数汇总
+ PPU-Util: 当前 PPU 流处理器利用率
+ Compute M.: 当前的计算模式（Compute Mode），如 Default / Prohibited / Exclusive Process（显示 E. Process）模式
+ MIG M.: 当前 MIG 模式（MIG Mode）

`PPU进程列表`表格信息说明如下：

+ PPU: 设备上电后分配的从 0 开始的枚举编号
+ CI ID: 计算继承占用的 Compute Instance 资源的 ID
+ PID: 系统进程 ID
+ Type: 本进程的计算类型，其中 C 表示 Compute
+ Process name: 进程名称
+ PPU Memory Usage: 本进程使用的 PPU 内存大小（MiB）

> **注意：** 若查询过程中使用 PPU 设备的进程正在退出，PPU 进程列表中的进程名称可能为空。

#### 2.2.1. MIG 设备信息
若存在 PPU 设备开启了 MIG 功能，通过执行`ppu-smi`，可查看当前存在的 MIG 设备信息表格：

```bash
+-----------------------------------------------------------------------------+
| MIG devices:                                                                |
+------------------+---------------------+----------+-------------------------+
| PPU  GI  CI  MIG |        Memory-Usage |      Vol |         Shared          |
|      ID  ID  DEV |                     |  CU  Unc | CpyEng ENC DEC OFA JPEG |
|                  |                     |      ECC |                         |
+==================+=====================+==========+=========================+
|  0   0   0    5  |   106MiB / 33618MiB |  64    0 |   4     2   2   0   0   |
+------------------+---------------------+----------+-------------------------+
|  1   1   2    3  |     6MiB / 16809MiB |  32    0 |   2     0   0   0   0   |
+------------------+---------------------+----------+-------------------------+
|  1   1   3    2  |     6MiB / 16809MiB |  32    0 |   2     0   0   0   0   |
+------------------+---------------------+----------+-------------------------+
```

`MIG设备列表`表格信息说明如下：

+ PPU: 设备上电后分配的从 0 开始的枚举编号
+ GI ID: MIG device 关联的 GPU instance ID
+ CI ID: MIG device 关联的 compute instance ID
+ MIG DEV: MIG device 枚举编号
+ Memory-Usage: 本 MIG device 已使用设备内存大小（MiB） / 总共设备内存大小（MiB）
+ CU: 本 MIG device 独占的 CU 资源个数
+ Vol Unc ECC: 自驱动加载后，设备发生的所有不可纠错的 ECC 错误个数汇总
+ Shared：以下列出的资源，本 MIG device 和 GPU instance 上其他 MIG device 共享
    - CpyEng: 共享的 copy engine 资源个数
    - ENC: 共享的编码器个数
    - DEC: 共享的解码器个数
    - OFA: 共享的 OFA 处理单元个数
    - JPEG: 共享的 JPEG 处理单元个数

#### 2.2.2. 通用控制选项
| 选项 | 说明 |
| --- | --- |
| -i,   --id= | 指定查询某一个特定设备，可以是如下值：<br/>+ 设备上电后分配的从 0 开始的枚举编号<br/>+ 板卡序列号（serial number）<br/>+ UUID<br/>+ PCI Bus ID<br/>推荐使用 UUID 或者 PCI Bus ID 指定设备：<br/>+ 设备枚举编号在重启后可能不一致<br/>+ 单卡多 PPU 场景，多个 PPU 的板卡序列号相同 |
| -f,   --filename= | 显示结果输出到文件 |
| -l,   --loop= | 指定每间隔多少秒查询一次，直到用户`Ctrl + C`打断 |
| -lms, --loop-ms= | 指定每间隔多少毫秒查询一次，直到用户`Ctrl + C`打断 |

比赛关联：`ppu-smi` 无参输出是压测时最常用的一屏概览——显存占用（Memory-Usage）、流处理器利用率（PPU-Util）、功率/温度、进程显存占用一屏可见，是验证推理服务显存预算和算力利用率的入口命令。

## 3. 查询设备信息

### 3.1. 通用查询
通过执行`ppu-smi -q`可查询系统相关信息，以及各个 PPU 设备的配置和状态信息。

```bash
root@122d8d7a7e37:~# ppu-smi -q

==============PPUSMI LOG==============

Timestamp                                   : Wed Sep  7 19:13:36 2022
Driver Version                              : 510.39.01
HGGC Version                                : 11.6
SDK Version                                 : 1.4.45-5188b0

Attached PPUs                               : 1
PPU 00000000:01:00.0
    Product Name                            : alixpu
    Persistence Mode                        : Disabled
    MIG Mode
        Current                             : N/A
        Pending                             : N/A
    Serial Number                           : N/A
    PPU UUID                                : PPU-7f53d39f-ce6e-dc78-c3d4-4c18653c19c0
    PCI
        Bus                                 : 0x01
        Device                              : 0x00
        Domain                              : 0x0000
        Device Id                           : 0x1E0410DE
...
```

可通过选项`-d`指定查询某些类型的信息，多个类型之间可通过`,`间隔，类型大小写不敏感，例如`ppu-smi -q -d ECC,POWER`，则 PPU-SMI 只会查询和 ECC / POWER 相关的信息。选项`-d`可选值说明如下：

| -d 选项可选值 | 说明 |
| --- | --- |
| MEMORY | 内存相关信息：总内存大小 / 使用情况等 |
| UTILIZATION | PPU 处理器 / 内存 / 编解码器等利用率 |
| ECC | ECC 模式 / 错误计数器状态等 |
| TEMPERATURE | 设备温度信息 |
| POWER | 设备当前功率 / 功率限制等 |
| CLOCK | 各时钟域时钟频率 / 最大可配置频率等 |
| COMPUTE | 设备计算模式（Compute Mode） |
| PIDS | 当前和本设备相关的进程信息 |
| SUPPORTED_CLOCKS | 设备支持的处理器和内存的时钟频率配置组合 |
| PAGE_RETIREMENT | 设备内存 Retired Page 相关信息 |
| ROW_REMAPPER | 设备内存 Remapped Row 相关信息 |
| VERSION | SDK 各组件版本信息 |

执行`ppu-smi -q`时，会查询上表中所有的类型的信息，部分将不会展示，若想查看采样相关信息，需通过`-d`指定类型查询，例如：

+ `ppu-smi -q -d POWER`将会展示功率采样的时间段 / 最大值 / 最小值 / 平均值等采样信息（Sampling）
+ `ppu-smi -q -d VERSION`将会展示 SDK 各组件的版本信息

#### 3.1.1. 基础查询说明
执行`ppu-smi -q`时会打印一些设备基本信息，这些信息不属于`-d`选项指定范畴，信息含义说明如下：

+ Driver Version：驱动（KMD）版本号
+ HGGC Version: HGGC 版本号
+ SDK Version: T-Head SAIL SDK 版本号
+ Product Name: 设备名称
+ Product Architecture: 产品架构
+ Compute Capability：HGGC 计算能力，格式为`major.minor`
+ Persistence Mode: 持久化特性开启状态
+ Addressing Mode：PPU 设备寻址模式
+ MIG Mode: MIG 特性状态
    - Current: 当前 MIG 特性开启状态
    - Pending: 重启后 MIG 特性开启状态
+ Serial Number: 板卡序列号
+ PPU UUID: 设备 UUID
+ Minor Number: 设备 Minor number，Linux 系统设备节点名称规则为：/dev/alixpu_ppu[minor number]
+ Rear ID：机尾 ID
+ PPU Virtualization Mode：设备虚拟化信息
    - Virtualization Mode：是否开启虚拟化功能
    - Host VGPU Mode：当前 host 系统是否支持 SR-IOV
+ PPU Recovery Action：PPU 异常所需的恢复操作
+ VBIOS Version: 设备 VBIOS（firmware）版本号
+ Auto Reset: 设备自动复位功能的开启状态
+ Performance Counter：Performance Counter 是否在激活状态
+ Tide Mode：潮汐模式是否使能
+ MPS Mode：MPS 模式是否使能
+ PCI: PPU PCI 接口信息
    - BUS / Device / Domain / Base Classcode / Sub Classcode / Device Id / Bus Id / Sub System Id / Vendor Id: 设备 PCI 标识
    - PPU Link Info: PCI 链路配置信息
        * PCIe Generation: 协议版本
            + Max: PPU 在本系统可能的最高协议版本，若 PPU 支持的 Generation 大于系统支持的 Generation，则显示的是系统支持的 Generation
            + Current: 当前生效的 PCIe 版本
        * Link Width: 链路传输位宽
            + Max: PPU 在本系统可能的最高链路传输位宽，若 PPU 支持的 Link Width 大于系统支持的 Link Width，则显示的是系统支持的 Link Width
            + Current: 当前生效的链路传输位宽
        * Replays Since Reset: 自上次复位计数器后，发生的 PCI 重传的次数
        * Tx Throughput / Rx Throughput: 当前 PCI 链路吞吐量（KB / s）
+ Fan Speed: 期望的风扇转速百分比，并不一定反应真实风扇转速（比如风扇被卡住无法转动）
+ Performance State: 设备性能状态级别，P0 为最高性能，P1 / P2 等性能逐级下降
+ Clocks Throttle Reasons: 时钟降频原因
    - Idle: 因 PPU 空闲降频
    - Applications Clocks Setting: 时钟受当前 Applications Clocks 配置限制
    - SW Power Cap: 达到软件配置功率上限
    - HW Slowdown: 因硬件原因受限，任何一个子项受限，则本项标记为`Active`
        * HW Thermal Slowdown: 达到硬件温度限制
        * HW Power Brake Slowdown: 触发外部功率限制，导致降频
    - Sync Boost: 因所在 Sync Group 中的其他 PPU 降频，本 PPU 跟随降频，请查询 Sync Group 其他 PPU 降频原因
    - SW Thermal Slowdown: 达到软件配置温度上限
+ Xid Errors: 驱动 XID 错误码（HGML 版本高于 12 环境，此字段废弃）
    - PPU Reset Correctable：需要复位 PPU 修正的 XID 错误码，不存在时显示为`N/A`
    - OS Reboot Correctable：需要操作系统重启修正的 XID 错误码，不存在时显示为`N/A`
    - Cold Reboot Correctable：需要系统断电重启修正的 XID 错误码，不存在时显示为`N/A`
+ Fabric：ICN 互联网络信息
    - State：PPU 设备的 ICN 组网状态
    - Status：查询 ICN 组网状态结果的结果是否可用
    - CliqueId：PPU 设备的集群 ID
    - ClusterUUID：PPU 设备的集群 UUID
+ Capabilities：设备能力
    - EGM：是否支持 EGM（Extended GPU memory）

#### 3.1.2. 内存查询说明
执行`ppu-smi -q -d MEMORY`，打印的信息含义说明如下：

```bash
root@122d8d7a7e37:~# ppu-smi -q -d MEMORY
...
PPU 00000000:01:00.0
    HBM Vendor                              : Samsung
    Memory Usage
        Total                               : 11264 MiB
        Used                                : 248 MiB
        Free                                : 11016 MiB
```

+ HBM Vendor：HBM 生产厂商
+ Total: 本设备总共内存大小（MiB）
+ Used: 当前使用的内存大小（MiB）
+ Free: 可用的内存大小（MiB）

#### 3.1.3. 利用率查询说明
执行`ppu-smi -q -d UTILIZATION`，打印的信息含义说明如下：

```bash
root@2b92dd1ad851:~# ppu-smi -q -d UTILIZATION
...
PPU 00000000:3E:00.0
    Utilization
        Ppu                                 : 38 %
        Core                                : 30 %
        Memory                              : 0 %
        Encoder                             : 0 %
        Decoder                             : 0 %
    PPU Utilization Samples
        Duration                            : 19.89 sec
        Number of Samples                   : 99
        Max                                 : 56 %
        Min                                 : 1 %
        Avg                                 : 31 %
    Memory Utilization Samples
        Duration                            : 19.89 sec
        Number of Samples                   : 99
        Max                                 : 0 %
        Min                                 : 0 %
        Avg                                 : 0 %
    ENC Utilization Samples
        Duration                            : 19.89 sec
        Number of Samples                   : 99
        Max                                 : 0 %
        Min                                 : 0 %
        Avg                                 : 0 %
    DEC Utilization Samples
        Duration                            : 19.89 sec
        Number of Samples                   : 99
        Max                                 : 0 %
        Min                                 : 0 %
        Avg                                 : 0 %

```

+ Utilization: 汇总的利用率显示
    - Ppu: PPU 处理器利用率
    - Core: PPU 核心利用率
    - Memory: 内存利用率
    - Encoder: 编码器利用率
    - Decoder: 解码器利用率
+ PPU Utilization Samples: PPU 处理器利用率采样信息
    - Duration: 采样数据持续时间
    - Number of Samples: 收集到的利用率采样数据个数
    - Max / Min / Avg: 采样点中最大 / 最小 / 平均利用率
+ Memory Utilization Samples: 内存利用率采样信息
+ ENC Utilization Samples: 编码器利用率采样信息
+ DEC Utilization Samples: 解码器利用率采样信息

#### 3.1.4. ECC 查询说明
执行`ppu-smi -q -d ECC`，打印的信息含义说明如下：

```bash
root@2b92dd1ad851:~# ppu-smi -q -d ECC
...
PPU 00000000:3E:00.0
    Ecc Mode
        Current                             : Enabled
        Pending                             : Enabled
    ECC Errors
        Volatile
            SRAM Correctable                : 0
            SRAM Uncorrectable              : 0
            DRAM Correctable                : 0
            DRAM Uncorrectable              : 0
        Aggregate
            SRAM Correctable                : 0
            SRAM Uncorrectable              : 0
            DRAM Correctable                : 0
            DRAM Uncorrectable              : 0

```

+ Ecc Mode: ECC 特性开启状态
    - Current: 当前 ECC 特性开启状态
    - Pending: 重启后 ECC 特性开启状态
+ ECC Errors: ECC 校验错误统计
    - Volatile
        * SRAM Correctable: SRAM 可纠错的 ECC 错误（1 bit 错误）
        * SRAM Uncorrectable: SRAM 不可纠错的 ECC 错误（2 bit 错误）
        * DRAM Correctable: DRAM 可纠错的 ECC 错误（1 bit 错误）
        * DRAM Uncorrectable: DRAM 不可纠错的 ECC 错误（2 bit 错误）
    - Aggregate: 设备累计的 ECC 错误计数（持久化，设备重启不清零）

#### 3.1.5. 温度查询说明
执行`ppu-smi -q -d TEMPERATURE`，打印的信息含义说明如下：

```bash
root@2b92dd1ad851:~# ppu-smi -q -d TEMPERATURE
...
PPU 00000000:3E:00.0
    Temperature
        PPU Current Temp                    : 42 C
        PPU Shutdown Temp                   : 95 C
        PPU Slowdown Temp                   : 92 C
        PPU Max Operating Temp              : 85 C
        PPU Target Temperature              : N/A
        Memory Current Temp                 : 42 C
        Memory Max Operating Temp           : 95 C

```

+ PPU Current Temp: 处理器当前温度
+ PPU Shutdown Temp: 硬件停止工作温度
+ PPU Slowdown Temp: 硬件降频保护温度（Hardware slowdown）
+ PPU Max Operating Temp: PPU 工作温度软件配置上限，超过则降频（Software slowdown）
+ PPU Target Temperature: PPU 工作目标温度，系统通过控制工作频率接近此目标温度
+ Memory Current Temp: 内存当前温度
+ Memory Max Operating Temp: 内存工作温度软件配置上限，超过则降频（Software slowdown）

#### 3.1.6. 功率查询说明
执行`ppu-smi -q -d POWER`，打印的信息含义说明如下：

```bash
root@2b92dd1ad851:~# ppu-smi -q -d POWER
...
PPU 00000000:3E:00.0
    Power Readings
        Power Management                    : Supported
        Power Draw                          : 51.99 W
        Power Limit                         : 250.00 W
        Default Power Limit                 : 250.00 W
        Enforced Power Limit                : 250.00 W
        Min Power Limit                     : 150.00 W
        Max Power Limit                     : 250.00 W
    Power Samples
        Duration                            : 2.39 sec
        Number of Samples                   : 119
        Max                                 : 58.68 W
        Min                                 : 51.40 W
        Avg                                 : 55.23 W

```

+ Power Readings: 功率相关状态值
    - Power Management: 是否支持功率控制特性
    - Power Draw: 当前消耗功率
    - Power Limit: 软件配置功率上限
    - Default Power Limit: 设备重启后默认的功率上限
    - Enforced Power Limit: 实际生效的功率上限，此上限可能在软件配置上限的基础上，叠加了其他功率控制特性的影响
    - Min Power Limit: 允许配置的最低功率上限
    - Max Power Limit: 允许配置的最高功率上限
+ Power Samples: 功率使用采样信息
    - Duration: 采样数据持续时间
    - Number of Samples: 收集到的利用率采样数据个数
    - Max / Min / Avg: 采样点中最大 / 最小 / 平均功率

#### 3.1.7. 时钟查询说明
执行`ppu-smi -q -d CLOCK`，打印的信息含义说明如下：

```bash
root@2b92dd1ad851:~# ppu-smi -q -d CLOCK
...
PPU 00000000:08:00.0
    Clocks
        CU                                  : 200 MHz
        Memory                              : 1800 MHz
        Video                               : 1000 MHz
    Applications Clocks
        CU                                  : 1700 MHz
        Memory                              : 1800 MHz
    Default Applications Clocks
        CU                                  : 1700 MHz
        Memory                              : 1800 MHz
    Max Clocks
        CU                                  : 1700 MHz
        Memory                              : 1800 MHz
        Video                               : 1000 MHz
```

+ Clocks: 当前时钟配置
    - CU: 流处理器（Streaming Multiprocessors）域时钟频率
    - Memory: 内存域时钟频率
    - Video: 视频编解码器域时钟频率
+ Applications Clocks：应用运行时钟配置
+ Default Applications Clocks：应用运行时钟默认配置
+ Max Clocks: 允许配置的最大时钟频率

#### 3.1.8. 计算模式查询说明
执行`ppu-smi -q -d COMPUTE`，打印的信息含义说明如下：

```bash
root@2b92dd1ad851:~# ppu-smi -q -d COMPUTE
...
PPU 00000000:3E:00.0
    Compute Mode                            : Default

```

+ Compute Mode: 当前生效的计算模式
    - Default 模式：设备允许多 context
    - Prohibited 模式：设备不允许建立任何 context
    - Exclusive Process 模式：设备只允许建立一个 context，此 context 可以在多线程中共享

#### 3.1.9. 进程信息查询说明
执行`ppu-smi -q -d PIDS`，打印的信息含义说明如下：

```bash
root@2b92dd1ad851:~# ppu-smi -q -d PIDS
...
PPU 00000000:3E:00.0
    Processes
        Compute instance ID                 : N/A
        Process ID                          : 85637
            Type                            : Compute
            Name                            : ppu_test
            Used PPU Memory                 : 413 MiB
        Compute instance ID                 : N/A
        Process ID                          : 87771
            Type                            : Compute
            Name                            : ppu_test_threads
            Used PPU Memory                 : 413 MiB

```

+ Compute Mode: 在 MIG 模式使能时，本进程占用的 Compute instance 的 ID
+ Process ID: 进程的系统 PID
    - Type: 进程工作模式，Compute 表示为通用计算类型
    - Name: 进程名称
    - Used PPU Memory: 本进程占用 PPU 内存大小（MiB）

#### 3.1.10. 支持时钟配置查询说明
执行`ppu-smi -q -d SUPPORTED_CLOCKS`，打印的信息含义说明如下：

```bash
root@122d8d7a7e37:~# ppu-smi -q -d SUPPORTED_CLOCKS
...
PPU 00000000:01:00.0
    Supported Clocks
        Memory                              : 7000 MHz
            CU                              : 2100 MHz
            CU                              : 2085 MHz
            CU                              : 2070 MHz
            CU                              : 2055 MHz
            CU                              : 2040 MHz
            ...
        Memory                              : 6800 MHz
            CU                              : 2100 MHz
            CU                              : 2085 MHz
            CU                              : 2070 MHz
            CU                              : 2055 MHz
            CU                              : 2040 MHz
            ...
```

+ Memory: 内存时钟域可配置的时钟频率（如 7000MHz）
    - CU: 当内存域配置为指定频率时（如 7000MHz），流处理器时钟域可配置的时钟频率

#### 3.1.11. Retired Pages 查询说明
执行`ppu-smi -q -d PAGE_RETIREMENT`，打印的信息含义说明如下：

```bash
root@122d8d7a7e37:~# ppu-smi -q -d PAGE_RETIREMENT
...
PPU 00000000:10:00.0
    Retired Pages
        Single Bit ECC                      : 0
        Double Bit ECC                      : 0
        Pending Page Blacklist              : No
```

+ Single Bit ECC：由于多次出现 Single Bit ECC 错误导致 retired 的 page 的个数
+ Double Bit ECC：由于出现 Double Bit ECC 错误导致 retired 的 page 的个数
+ Pending Page Blacklist：当前是否有等待重启后生效的 retired page，在重启之前性能下降的 page 仍可能使用并出现错误

#### 3.1.12. Remapped Rows 查询说明
执行`ppu-smi -q -d ROW_REMAPPER`，打印的信息含义说明如下：

```bash
root@122d8d7a7e37:~# ppu-smi -q -d ROW_REMAPPER
...
PPU 00000000:10:00.0
    Remapped Rows
        Correctable Error                   : 0
        Uncorrectable Error                 : 0
        Pending                             : No
        Remapping Failure Occurred          : No
        Bank Remap Availability Histogram
            Max                             : 3072 bank(s)
            High                            : 0 bank(s)
            Partial                         : 0 bank(s)
            Low                             : 0 bank(s)
            None                            : 0 bank(s)
```

+ Correctable Error：由于多次出现 Single Bit ECC 错误导致 remap 的 row 的个数
+ Uncorrectable Error：由于出现 Double Bit ECC 错误导致 remap 的 row 的个数
+ Pending：当前是否有等待重启后生效的 remapped row，在重启之前性能下降的 row 仍可能使用并出现错误
+ Bank Remap Availability Histogram：PPU 设备所有 bank 的 remap 能力统计直方图，例如：
    - Max：能 remap 到所有预留的 row 的 bank 的个数
    - None：不能 remap 到任何预留的 row 的 bank 的个数

#### 3.1.13. 版本信息查询说明
执行`ppu-smi -q -d VERSION`，打印 SDK 各组件的版本信息，未安装的组件版本信息显示为`N/A`，查询结果示例如下：

```bash
root@122d8d7a7e37:~# ppu-smi -q -d VERSION
...
Driver Version                              : 1.4.1-4a27c0
HGGC Version                                : 11.1
SDK Version                                 : 1.4.2-383431
clang Version                               : 13.0.1 (1.4.2-383431)
hgas Version                                : 1.4.2-383431-
hgobjdump Version                           : 1.4.2-383431-
hgbat Version                               : 1.4.2-383431-
ppu-gdb Version                             : 1.4.2
hggc-memcheck Version                       : 1.4.2-383431-
hgprune Version                             : 1.4.2-383431-
ppudbg Version                              : 1.1
ppu-smi Version                             : 1.17
asys Version                                : 1.4.2_20250125-78d58cc
acu Version                                 : 1.4.2_20250125-78d58cc
DCGM Version                                : 3.0.26
HGGC Driver Version                         : 1.0
HGGC Runtime Version                        : 1.0
UMD Version                                 : 1.0
UKI Version                                 : 1.0
HGML Version                                : 1.0
Debug API Version                           : 1.0
PCCL Version                                : 1.4.2
HGPTI Version                               : 21 (3)
acBLAS Version                              : 1.4.0
acFFT Version                               : 1.4.0
acDNN Version                               : 1.4.0
acRAND Version                              : 1.4.0
acSOLVER Version                            : 1.4.0
Holmes Version                              : 0.3.0-88a832
```

#### 3.1.14. 通用控制选项
| 选项 | 说明 |
| --- | --- |
| -i,   --id= | 指定查询某一个特定设备，可以是如下值：<br/>+ 设备上电后分配的从 0 开始的枚举编号<br/>+ 板卡序列号（serial number）<br/>+ UUID<br/>+ PCI Bus ID<br/>推荐使用 UUID 或者 PCI Bus ID 指定设备：<br/>+ 设备枚举编号在重启后可能不一致<br/>+ 单卡多 PPU 场景，多个 PPU 的板卡序列号相同 |
| -f,   --filename= | 显示结果输出到文件 |
| -l,   --loop= | 指定每间隔多少秒查询一次，直到用户`Ctrl + C`打断 |
| -lms, --loop-ms= | 指定每间隔多少毫秒查询一次，直到用户`Ctrl + C`打断 |

### 3.2. 选择性查询
PPU-SMI 支持用户查询指定的设备信息，用户通过选项传入希望查询的属性名称的列表（通过`,`分隔），PPU-SMI 将查询结果以`CSV`表格的方式打印输出。

例如执行`ppu-smi --query-ppu=timestamp,index,name,compute_mode,memory.total,memory.used --format=csv`：

```bash
root@2b92dd1ad851:~# ppu-smi --query-ppu=timestamp,index,name,compute_mode,memory.total,memory.used --format=csv
timestamp, index, name, compute_mode, memory.total [MiB], memory.used [MiB]
2022/09/08 09:24:11.132, 0, alixpu, Default, 40960 MiB, 606 MiB
2022/09/08 09:24:11.139, 1, alixpu, Default, 24576 MiB, 508 MiB
```

PPU-SMI 支持的选择性查询功能如下：

| 选择性查询选项 | 说明 |
| --- | --- |
| --query-ppu= | 查询各个 PPU 设备的属性信息，每行打印一个 PPU 设备的相关信息 |
| --query-supported-clocks= | 查询各个 PPU 设备支持的时钟配置信息，每行打印一个 PPU 一对内存时钟域和处理器时钟域的相关信息 |
| --query-compute-apps= | 查询各个 PPU 设备的进程信息，每行打印一个 PPU 设备的一个进程的相关信息 |
| --query-retired-pages= | 查询各个 PPU 设备内存的 retired pages 信息，每行打印一个 retired page 的相关信息 |
| --query-remapped-rows= | 查询各个 PPU 设备内存的 remapped rows 信息，每行打印一个 PPU 设备的 remapped row 的相关信息 |

选择性查询需要指定结果输出格式，通过选项`--format`进行指定，多个选项间通过`,`分隔，其中`csv`为必选项：

| 输出格式选项 | 说明 |
| --- | --- |
| csv | **必选项**，查询结果以`CSV`格式输出打印 |
| noheader | 不打印表头信息 |
| nounits | 不打印表头和数据中的单位信息 |

#### 3.2.1. 查询 PPU 信息
使用`--query-ppu`选项指定查询的属性名称列表，不同属性通过`,`分隔。可执行`ppu-smi --help-query-ppu`查看所有支持的属性信息：

```bash
root@2b92dd1ad851:~# ppu-smi --help-query-ppu
List of valid properties to query for the switch "--query-ppu=":

"timestamp"
The timestamp of when the query was made in format "YYYY/MM/DD HH:MM:SS.msec".

"driver_version"
The version of the installed driver. This is an alphanumeric string.

"count"
The number of PPUs in the system.

"name" or "ppu_name"
The official product name of the PPU. This is an alphanumeric string. For all products.

"serial" or "ppu_serial"
This number matches the serial number physically printed on each board. It is a globally unique immutable alphanumeric value.

"uuid" or "ppu_uuid"
This value is the globally unique immutable alphanumeric identifier of the PPU. It does not correspond to any physical label on the board.

"pci.bus_id" or "ppu_bus_id"
PCI bus id as "domain:bus:device.function", in hex.
...
```

选择部分属性进行查询，例如查询设备名称 / 序号列 / 设备枚举索引 / uuid 等信息，执行`ppu-smi --query-ppu=timestamp,count,name,serial,index,uuid --format=csv`：

```bash
root@2b92dd1ad851:~# ppu-smi --query-ppu=timestamp,count,name,serial,index,uuid --format=csv
timestamp, count, name, serial, index, uuid
2022/09/08 09:42:34.913, 2, alixpu, 1320421013145, 0, PPU-0cdd7938-b576-2411-a408-3ad81dfc1a78
2022/09/08 09:42:34.920, 2, alixpu, 1323921045367, 1, PPU-16c4c41f-9214-5e29-3b86-7a26ab011d3e
```

#### 3.2.2. 查询支持时钟配置信息
使用`--query-supported-clocks`选项指定查询的属性名称列表，不同属性通过`,`分隔。可执行`ppu-smi --help-query-supported-clocks`查看所有支持的属性名称和描述信息：

```bash
root@2b92dd1ad851:~# ppu-smi --help-query-supported-clocks
List of valid properties to query for the switch "--query-supported-clocks=":

[Section about Supported Clocks properties]
List of possible memory and processor clocks combinations that the PPU can operate on (not taking into account HW brake reduced clocks).

"timestamp"
The timestamp of when the query was made in format "YYYY/MM/DD HH:MM:SS.msec".

"name" or "ppu_name"
The official product name of the PPU. This is an alphanumeric string. For all products.

...

"memory" or "mem"
Memory clock.

"processor" or "sm"
Streaming multiprocessors clock.
```

例如查询内存域和流处理器域时钟配置组合列表，执行`ppu-smi --query-supported-clocks=timestamp,ppu_bus_id,memory,processor --format=csv`：

```bash
root@2b92dd1ad851:~# ppu-smi --query-supported-clocks=timestamp,ppu_bus_id,memory,processor --format=csv
timestamp, pci.bus_id, memory [MHz], processor [MHz]
2022/09/08 09:50:26.289, 00000000:3E:00.0, 1215 MHz, 1410 MHz
2022/09/08 09:50:26.289, 00000000:3E:00.0, 1215 MHz, 1395 MHz
2022/09/08 09:50:26.289, 00000000:3E:00.0, 1215 MHz, 1380 MHz
2022/09/08 09:50:26.289, 00000000:3E:00.0, 1215 MHz, 1365 MHz
2022/09/08 09:50:26.289, 00000000:3E:00.0, 1215 MHz, 1350 MHz
2022/09/08 09:50:26.289, 00000000:3E:00.0, 1215 MHz, 1335 MHz
2022/09/08 09:50:26.289, 00000000:3E:00.0, 1215 MHz, 1320 MHz
2022/09/08 09:50:26.289, 00000000:3E:00.0, 1215 MHz, 1305 MHz
2022/09/08 09:50:26.289, 00000000:3E:00.0, 1215 MHz, 1290 MHz
...
```

#### 3.2.3. 查询进程信息
使用`--query-compute-apps`选项指定查询的属性名称列表，不同属性通过`,`分隔。可执行`ppu-smi --help-query-compute-apps`查看所有支持的属性信息：

```bash
root@2b92dd1ad851:~# ppu-smi --help-query-compute-apps
List of valid properties to query for the switch "--query-compute-apps=":

[Section about Active Compute Processes properties]
List of processes having compute context on the device.

"timestamp"
The timestamp of when the query was made in format "YYYY/MM/DD HH:MM:SS.msec".

"name" or "ppu_name"
The official product name of the PPU. This is an alphanumeric string. For all products.

...

"pid"
Process ID of the compute application.

"process_name"
Process Name.

"used_ppu_memory" or "used_memory"
Amount memory used on the device by the context.
```

例如查询 PPU 设备相关的进程 PID / 名称 / 内存占用信息，执行`ppu-smi --query-compute-apps=timestamp,uuid,pid,process_name,used_ppu_memory --format=csv`:

```bash
root@2b92dd1ad851:~# ppu-smi --query-compute-apps=timestamp,uuid,pid,process_name,used_ppu_memory --format=csv
timestamp, uuid, pid, process_name, used_ppu_memory [MiB]
2022/09/08 09:57:57.660, PPU-0cdd7938-b576-2411-a408-3ad81dfc1a78, 61785, ppu_test, 413 MiB
2022/09/08 09:57:57.660, PPU-0cdd7938-b576-2411-a408-3ad81dfc1a78, 62103, ppu_test_threads, 413 MiB
```

#### 3.2.4. 查询 Retired Page 信息
使用`--query-retired-pages`选项指定查询的属性名称列表，不同属性通过`,`分隔。可执行`ppu-smi --help-query-retired-pages`查看所有支持的属性信息：

```bash
root@0549cf16bb85:~# ppu-smi --help-query-retired-pages
List of valid properties to query for the switch "--query-retired-pages=":

[Section about Retired Pages properties]
List of pages have been retired or pending to be retired.

"timestamp"
The timestamp of when the query was made in format "YYYY/MM/DD HH:MM:SS.msec".

"name" or "ppu_name"
The official product name of the PPU. This is an alphanumeric string. For all products.
...

"retired_pages.address"
Address of a retired page. Address might be different when ECC is Enabled or Disabled.

"retired_pages.timestamp"
Timestamp at which the page was retired.

"retired_pages.cause"
Reason that describes why the page was retired. Can take one of two values:
 - Double Bit ECC: The number of PPU device memory pages that have been retired due to a double bit ECC error.
 - Single Bit ECC: The number of PPU device memory pages that have been retired due to multiple single bit ECC errors.
```

例如查询 PPU 设备发生的 retired page 列表，查看地址、发生时间和原因，执行`ppu-smi --query-retired-pages=timestamp,uuid,retired_pages.address,retired_pages.timestamp,retired_pages.cause --format=csv`:

```bash
root@2b92dd1ad851:~# ppu-smi --query-retired-pages=timestamp,uuid,retired_pages.address,retired_pages.timestamp,retired_pages.cause --format=csv
timestamp, uuid, retired_pages.address, retired_pages.timestamp, retired_pages.cause
12:32:15.329, PPU-3f53d39f-ce6e-dc78-c3d4-4c18653c19c0, 0x0000000073234722, 1663256354, Single Bit ECC
```

#### 3.2.5. 查询 Remapped Row 信息
使用`--query-remapped-rows`选项指定查询的属性名称列表，不同属性通过`,`分隔。可执行`ppu-smi --help-query-remapped-rows`查看所有支持的属性信息：

```bash
root@0549cf16bb85:~# ppu-smi --help-query-remapped-rows
List of valid properties to query for the switch "--query-remapped-rows=":

"timestamp"
The timestamp of when the query was made in format "YYYY/MM/DD HH:MM:SS.msec".

"name" or "ppu_name"
The official product name of the PPU. This is an alphanumeric string. For all products.
...

"remapped_rows.correctable"
The number of rows that have been remapped due to correctable ECC errors.

"remapped_rows.uncorrectable"
The number of rows that have been remapped due to uncorrectable ECC errors.

"remapped_rows.pending"
Whether or not there are pending row-remappings.

"remapped_rows.failure"
Whether or not a row remapping has failed in the past.

"remap_availability.bank_histogram.max"
The number of banks that have max remap availability(all reserved rows are available).

"remap_availability.bank_histogram.high"
The number of banks that have high remap availability.

"remap_availability.bank_histogram.partial"
The number of banks that have partial remap availability.
...
```

例如查询 PPU 设备发生的 remapped rows 统计结果，执行`ppu-smi --query-remapped-rows=timestamp,uuid,remapped_rows.correctable,remapped_rows.uncorrectable,remap_availability.bank_histogram.max --format=csv`：

```bash
root@2b92dd1ad851:~# ppu-smi --query-remapped-rows=timestamp,uuid,remapped_rows.correctable,remapped_rows.uncorrectable,remap_availability.bank_histogram.max --format=csv
timestamp, uuid, remapped_rows.correctable, remapped_rows.uncorrectable, remap_availability.bank_histogram.max
2022/09/08 16:24:40.435, GPU-099ea108-0181-0230-0000-000060f19f20, 0, 0, 3072
2022/09/08 16:24:40.435, GPU-019ea108-01a1-0222-0000-000040dff62d, 0, 0, 3072
2022/09/08 16:24:40.435, GPU-019ea108-0121-0222-0000-0000605e6417, 0, 0, 3072
```

#### 3.2.6. 通用控制选项
| 选项 | 说明 |
| --- | --- |
| -i,   --id= | 指定查询某一个特定设备，可以是如下值：<br/>+ 设备上电后分配的从 0 开始的枚举编号<br/>+ 板卡序列号（serial number）<br/>+ UUID<br/>+ PCI Bus ID<br/>推荐使用 UUID 或者 PCI Bus ID 指定设备：<br/>+ 设备枚举编号在重启后可能不一致<br/>+ 单卡多 PPU 场景，多个 PPU 的板卡序列号相同 |
| -f,   --filename= | 显示结果输出到文件 |
| -l,   --loop= | 指定每间隔多少秒查询一次，直到用户`Ctrl + C`打断 |
| -lms, --loop-ms= | 指定每间隔多少毫秒查询一次，直到用户`Ctrl + C`打断 |

比赛关联：`--query-ppu=... --format=csv,noheader,nounits` 配合 `-l`/`-lms` 循环采样，是编写自动化压测脚本（采集吞吐压测期间的显存、利用率、功率时序数据）的最佳接口；`-q -d CLOCK` 和 `Clocks Throttle Reasons` 可用来确认压测中是否发生降频，避免把降频后的成绩误当作优化收益。

<a id="Kgcc3"></a>

## 4. 修改设备配置

### 4.1. 设备配置选项
PPU-SMI 支持修改设备配置，例如修改处理器时钟频率，执行`ppu-smi -lpc 1410`：

```bash
root@122d8d7a7e37:~# ppu-smi -lpc 1410
Set PPU clock to (min clock 1410MHz, max clock 1410MHz) for PPU 00000000:01:00.0.
All done.
```

支持的选项如下，单次 PPU-SMI 支持修改一种设备配置（选项中的其中一个）：

| 选项 | 说明 |
| --- | --- |
| -e,   --ecc-config= | 设置 ECC 功能是否使能，支持输入参数如下，大小写敏感：<br/>+ 0 或者 DISABLED：禁用 ECC 模式<br/>+ 1 或者 ENABLED：使能 ECC 模式<br/>例如：<br/>`ppu-smi -e 0`：禁用设备 ECC 功能<br/>可执行`ppu-smi -q`验证修改已生效 |
| -c,   --compute-mode= | 修改设备计算模式（Compute Mode），支持输入参数如下，大小写敏感：<br/>+ 0 或者 DEFAULT：设备允许多 context<br/>+ 1 或者 EXCLUSIVE_PROCESS：设备只允许建立一个 context，此 context 可以在多线程中共享<br/>+ 2 或者 PROHIBITED：设备不允许建立任何 context<br/>例如：<br/>`ppu-smi -c 0`：修改设备为默认模式<br/>`ppu-smi -c EXCLUSIVE_PROCESS`：修改设备为独占模式<br/>可执行`ppu-smi`验证修改生效。 |
| -r,   --ppu-reset | 复位 PPU 设备，执行`ppu-smi -r`复位设备。<br/>可用于复位 PPU 硬件状态，避免重启整个系统。<br/>复位操作不保证任何场景下均生效，请小心使用。 |
| --reset= | 复位 PPU 组件，支持输入参数如下，大小写敏感：<br/>+ 0 或者 PPU：仅复位 PPU 核心<br/>+ 1 或者 ICN：仅复位 ICN 链路<br/>+ 2 或者 PPU_ICN：复位 PPU 核心和 ICN 链路 |
|  -vm,  --virt-mode= | 修改设备的虚拟化模式，支持输入参数如下，大小写敏感：<br/>+ 0 或者 NONE：关闭虚拟化模式<br/>+ 2 或者 VGPU：开启虚拟化模式<br/>可执行`ppu-smi -q`验证修改已生效 |
| -lpc, --lock-ppu-clocks= | 执行`ppu-smi -lpc <minPpuClock,maxPpuClock>`锁定 PPU 处理器时钟域频率到一定范围，单位 MHz。参数中的`最低频率（minPpuClock）`和`最高频率（maxPpuClock）`通过`,`分隔。<br/>若希望时钟频率锁定在单个频点，可只传入单个频率值，`ppu-smi -lpc <PpuClockValue>`。<br/>配置无论当前 PPU 是否有应用运行，均立刻生效。<br/>例如：<br/>`ppu-smi -lpc 1410`：锁定处理器域时钟到 1410MHz |
| -rpc, --reset-ppu-clocks | 执行`ppu-smi -rpc`复位 PPU 处理器时钟域频率到默认范围。 |
| -lmc, --lock-memory-clocks= | 执行`ppu-smi -lmc <minMemClock,maxMemClock>`锁定内存时钟域频率到一定范围，单位 MHz。参数中的`最低频率（minMemClock）`和`最高频率（maxMemClock）`通过`,`分隔。<br/>若希望时钟频率锁定在单个频点，可只传入单个频率值，`ppu-smi -lmc <MemClockValue>`。<br/>例如：<br/>`ppu-smi -lmc 1215`：锁定内存域时钟到 1215MHz |
| -rmc, --reset-memory-clocks | 执行`ppu-smi -rmc`复位内存时钟域频率到默认范围。 |
| -ac,  --applications-clocks= | 执行`ppu-smi -ac <memory,CU>`锁定运行应用程序时内存域时钟和 PPU 处理器时钟到固定值，单位 MHz。<br/>例如：<br/>`ppu-smi -ac 1800,1500`：锁定运行应用程序时内存域时钟到 1800MHz，PPU 处理器时钟到 1500MHz |
| -rac, --reset-applications-clocks | 执行`ppu-smi -rac`复位运行应用程序时的时钟频率到默认范围。 |
| -pl,  --power-limit= | 设置设备最大功率限制，单位为`瓦（W）`，支持指定小数，如`215.5`。<br/>设备支持设置的功率范围可通过执行`ppu-smi -q -d POWER`查询。<br/>例如：<br/>`ppu-smi -pl 215.5`：设定设备最大功率为`215.5W` |
| -mig, --multi-instance-gpu= | 设置 MIG 功能是否使能，支持输入参数如下，大小写敏感：<br/>+ 0 或者 DISABLED：关闭 MIG 模式<br/>+ 1 或者 ENABLED：使能 MIG 模式<br/>例如：<br/>`ppu-smi -mig 1`: 使能 MIG 模式<br/>可执行`ppu-smi`验证修改生效。<br/><br/> **注意：**当有 MIG 实例存在，无法关闭 MIG 模式，请删除本设备所有 MIG 实例后，再尝试关闭 MIG 模式<br/> |
| --auto-reset= | 设置 PPU 设备自动复位功能是否使能，支持输入参数如下，大小写敏感：<br/>+ 0 或者 DISABLED：关闭自动复位功能<br/>+ 1 或者 ENABLED：使能自动复位功能<br/>当`auto reset`功能使能时，若 PPU 驱动检测到 PPU 设备状态异常，将自动触发 PPU 设备复位操作。<br/>可执行`ppu-smi -q`验证修改已生效 |
| -mps, --multi-process-service= | 设置 PPU 设备 MPS 模式是否使能，支持输入参数如下，大小写敏感：<br/>+ 0 或者 DISABLED：关闭 MPS 模式<br/>+ 1 或者 ENABLED：使能 MPS 模式<br/>例如：<br/>`ppu-smi -mps 1`: 使能 MPS 模式<br/>可执行`ppu-smi -q`验证修改已生效 |

#### 4.1.1. 复位 PPU 设备
执行`ppu-smi -r`可复位所有 PPU 设备，通过`-i`选项可复位指定 PPU 设备，比如`ppu-smi -r -i 0`复位 PPU 0 号设备。复位 PPU 设备需要满足如下前提：

1. 所有 PPU 设备没有 HGGC 相关的应用（compute application）
2. 所有 PPU 设备没有 PPU 相关的监控、工具类应用，如 ppu-smi、ppudbg、T-Head SAIL DCGM 等软件

执行`ppu-smi --reset PPU`或者`ppu-smi --reset ICN`可以仅复位 PPU 设备的部分组件。

若复位 PPU 设备由于存在上述应用导致失败，可通过如下命令查询相关应用：

```bash
# 查询HGGC相关的应用
ppu-smi pmon -c 1

# 查询PPU相关的监控、工具类应用
lsof /dev/alixpu
```

### 4.2. 通用控制选项
| 选项 | 说明 |
| --- | --- |
| -i,   --id= | 若不指定设备，则对系统内所有 PPU 设备执行修改配置操作。<br/>若通过选项`-i`指定修改某一个特定设备，可以是如下值：<br/>+ 设备上电后分配的从 0 开始的枚举编号<br/>+ 板卡序列号（serial number）<br/>+ UUID<br/>+ PCI Bus ID<br/>推荐使用 UUID 或者 PCI Bus ID 指定设备：<br/>+ 设备枚举编号在重启后可能不一致<br/>+ 单卡多 PPU 场景，多个 PPU 的板卡序列号相同 |
| -eow, --error-on-warning | 若修改配置失败，PPU-SMI 命令行返回非 0 错误码。<br/>以下场景修改配置失败不作为错误处理：<br/>+ 设备不支持此修改操作 |

比赛关联：`-lpc`/`-ac` 锁定时钟可以让 TTFT/吞吐的多次测量结果可复现、可对比，是 benchmark 数据可信的前提；`-mps 1` 面向多客户端并发，不符合本次比赛口径，保持关闭。

## 5. 收集设备统计信息
PPU-SMI 支持收集设备采样 / 事件信息，以`CSV`表格方式打印，供后续统计设备运行状态。用户可通过子命令`stats`使用设备统计功能，通过执行`ppu-smi stats -h`查看统计功能帮助信息：

```bash
root@2b92dd1ad851:~# ppu-smi stats -h
Generates PPU statistics such as power samples,
utilization samples, xid events, clock change events
and performance capping events.

ppu-smi stats [OPTION1 [ARG1]] [OPTION2 [ARG2]] ...
    -i,   --id
        Enumeration index, Serial number, PCI bus ID or UUID.
        Provide comma separated values for more than one device
    -f,   --filename
        Log to a specified file, rather than to stdout
    -d,   --display
        Display specific metric:
            pwrDraw,temp,memUtil,ppuUtil,
            encUtil,decUtil,memClk,procClk,
            violPwr,violThm,xidEvent,sbEcc,
            dbEcc,pState,clkChg,pwrChg,migChg
        Metric can be combined with comma e.g. pwrDraw,temp
    -c,   --count
        Run for specified number of monitoring cycles and exit
    -h,   --help
        Display help information

Stats in following CSV format:
Device, Power Drawn (pwrDraw), Timestamp (us), Value (Watts)
Device, PPU Temperature (temp), Timestamp (us), Value (C)
Device, PPU Util (ppuUtil), Timestamp (us), Value (%)
...
```

### 5.1. 打印格式
查询结果输出的`CSV`表格，执行`ppu-smi stats`结果如下：

```bash
root@122d8d7a7e37:~# ppu-smi stats
0, violPwr , 1662606252538553, 0
0, violThm , 1662606252537681, 0
0, temp    , 1662606252536736, 51
0, pState  , 1662606252559897, 0
0, clkChg  , 1662606252559964, 0
0, pState  , 1662606252568416, 0
0, clkChg  , 1662606252568499, 0
...
0, temp    , 1662606253541531, 52
0, pwrDraw , 1662606252543916, 45
0, pwrDraw , 1662606252567432, 54
0, pwrDraw , 1662606252584972, 66
0, pwrDraw , 1662606252605044, 66
...
```

`CSV`表格格式含义如下，无表头，每列含义为：

1. 第一列： 设备索引，设备上电后分配的从 0 开始的枚举编号
2. 第二列： 统计的 metric 名称缩写，如`pwrDraw`，`temp`等
3. 第三列： 数据获取的时间戳，单位为`微秒`，值为系统时钟`system_clock`开始到采样时间的微秒数
4. 第四列： 采样数值，无单位，具体含义参见下文 metric 介绍

### 5.2. 统计 Metrics 说明
希望采集的 metrics 可通过`-d`选项指定，多个 metrics 通过`,`分隔，如`ppu-smi stats -d pwrDraw,temp`：

```bash
root@122d8d7a7e37:~# ppu-smi stats -d pwrDraw,temp
0, temp    , 1662606935107702, 51
0, pwrDraw , 1662606935059582, 38
0, pwrDraw , 1662606935079459, 39
0, pwrDraw , 1662606935099668, 39
...
```

若不通过`-d`选项指定，则默认统计所有支持的 metrics。支持的 metrics 说明如下：

| metric 名称 | 事件型 metric | 说明 | 值含义 |
| --- | --- | --- | --- |
| pwrDraw | 否 | 设备当前消耗功率的采样值 | 功率值，单位：W |
| temp | 否 | 设备当前温度的采样值 | 温度值，单位：摄氏度 |
| ppuUtil | 否 | 设备处理器利用率的采样值 | 利用率百分比，单位：% |
| memUtil | 否 | 设备内存利用率的采样值 | 利用率百分比，单位：% |
| encUtil | 否 | 设备编码器利用率的采样值 | 利用率百分比，单位：% |
| decUtil | 否 | 设备解码器利用率的采样值 | 利用率百分比，单位：% |
| memClk | 否 | 内存时钟域频率的采样值 | 时钟频率，单位：MHz |
| procClk | 否 | 处理器时钟域频率的采样值 | 时钟频率，单位：MHz |
| violPwr | 否 | 自上次采样后，设备因超过功率限制而降频的持续时间汇总 | 总共的降频持续时间，单位：纳秒 |
| violThm | 否 | 自上次采样后，设备因超过温度限制而降频的持续时间汇总 | 总共的降频持续时间，单位：纳秒 |
| xidEvent | 是 | 驱动上报的 XID 事件 | XID 错误代码 |
| sbEcc | 是 | 发生了一次 single bit ECC error 事件 | 0，无含义 |
| dbEcc | 是 | 发生了一次 double bit ECC error 事件 | 0，无含义 |
| pState | 是 | 性能等级（Performance State）配置变更事件 | 0，无含义 |
| clkChg | 是 | 时钟配置变更事件 | 0，无含义 |
| pwrChg | 是 | 功率配置变更事件 | 0，无含义 |
| migChg | 是 | MIG 配置变更事件 | 0，无含义 |

对于事件性的 metric（如 xidEvent），PPU-SMI 将在事件发生时打印输出。对于非事件性的 metric（如 pwrDraw），PPU-SMI 每秒汇总一次采样结果并打印输出。

PPU-SMI 默认将持续运行和采集数据，直到用户`Ctrl + C`打断。

### 5.3. 通用控制选项
| 选项 | 说明 |
| --- | --- |
| -i,   --id= | 指定特定设备，支持指定多个设备，通过`,`分隔，如`-i 0,1`，可以是如下值：<br/>+ 设备上电后分配的从 0 开始的枚举编号<br/>+ 板卡序列号（serial number）<br/>+ UUID<br/>+ PCI Bus ID<br/>推荐使用 UUID 或者 PCI Bus ID 指定设备：<br/>+ 设备枚举编号在重启后可能不一致<br/>+ 单卡多 PPU 场景，多个 PPU 的板卡序列号相同 |
| -f,   --filename= | 显示结果输出到文件 |
| -c,   --count= | 指定多少次统计周期后停止统计 |

比赛关联：`ppu-smi stats -d ppuUtil,memUtil,procClk -f log.csv` 可在 benchmark 运行期间留档设备侧利用率曲线，是报告"系统级优化深度"时证明算力被打满、或定位 prefill/decode 阶段瓶颈的直接证据。

## 6. 监视设备状态
PPU-SMI 支持滚动输出设备监视信息，用户可通过子命令`dmon`使用监控设备功能，每行打印一个设备的检视信息，每类监视信息作为一列滚动打印，例如执行`ppu-smi dmon`:

```bash
root@2b92dd1ad851:~# ppu-smi dmon
# ppu   pwr ptemp mtemp    cu  core   mem   enc   dec  mclk  pclk
# idx     W     C     C     %     %     %     %     %   MHz   MHz
    0   109    30    32     0     2     0     0     0  1800  1500
    1   119    33    34     0     0     0     0     0  1800  1500
    0   109    30    32     0     0     0     0     0  1800  1500
    1   121    33    34     0     0     0     0     0  1800  1500
...
```

通过执行`ppu-smi dmon -h`可查看监视设备功能帮助信息：

```bash
root@2b92dd1ad851:~# ppu-smi dmon -h
PPU statistics are displayed in scrolling format with one line
per sampling interval. Metrics to be monitored can be adjusted
based on the width of terminal window.

ppu-smi dmon [OPTION1 [ARG1]] [OPTION2 [ARG2]] ...
    -i,   --id=
        Enumeration index, Serial number, PCI bus ID or UUID.
        Provide comma separated values for more than one device
    -d,   --delay=
        Collection delay/interval in seconds [default=1sec]
    -c,   --count=
        Collect specified number of samples and exit
    -s,   --select=
        One or more metrics [default=puc]
        Can be any of the following:
            p - Power Usage and Temperature
            u - Utilization
            c - Proc and Mem Clocks
            v - Power and Thermal Violations
            m - SM Memory
            e - ECC Errors and PCIe Replay errors
            t - PCIe Rx and Tx Throughput
    -o,   --options=
        One or more from the following:
            D - Include Date (YYYYMMDD) in scrolling output
            T - Include Time (HH:MM:SS) in scrolling output
...
```

### 6.1. 监视 Metrics 说明
可通过`-s`选项指定希望监视的 metrics，每个 metric 使用单个字符标识，多个 metric 对应的字符可拼接在一起，作为`-s`选项传入，例如`ppu-smi dmon -s pc`，指定打印功率（p）和时钟（c）相关 metrics。

```bash
root@2b92dd1ad851:~# ppu-smi dmon -s pc
# ppu   pwr ptemp mtemp  mclk  pclk
# idx     W     C     C   MHz   MHz
    0    41    45    45  1215   765
    1    30    36    36  1215   930
...
```

支持的 metrics 说明如下：

| -s 选项 metric 字符 | 说明 |
| --- | --- |
| p | 当前功率 / 处理器和内存温度信息 |
| u | 处理器 / 内存 / 编码器 / 解码器利用率 |
| c | 处理器时钟域和内存时钟域的频率信息 |
| v | PPU 因温度或者功耗限制而降频的比例信息 |
| m | 内存使用信息 |
| e | ECC error 错误计数和 PCI replay 错误计数 |
| t | PCI 接口的吞吐量信息 |

PPU-SMI 滚动输出的每列信息，含义说明如下：

+ 基础信息
    - Date: 当前日期
    - Time: 当前时间
    - ppu: 设备上电后分配的从 0 开始的枚举编号
+ metric 类型`p`
    - pwr: 当前消耗功率，单位 W
    - ptemp: 处理器当前温度
    - mtemp: 内存当前温度
+ metric 类型`u`
    - sm: 流处理器利用率，单位%
    - core: 核心利用率，单位%
    - mem: 内存利用率，单位%
    - enc: 编码器利用率，单位%
    - dec: 解码器利用率，单位%
+ metric 类型`c`
    - pclk: 处理器时钟域频率，单位 MHz
    - mclk: 内存时钟域频率，单位 MHz
+ metric 类型`v`
    - pviol: 因功率受限而降频的时间，占采样间隔时间的比例，单位%
    - tviol: 因温度受限而降频的时间，占采样间隔时间的比例，单位%
+ metric 类型`m`
    - mem: 当前内存已使用大小，单位 MiB
+ metric 类型`e`
    - sbecc: 自驱动加载以来，出现的 single bit ECC error 的次数
    - dbecc: 自驱动加载以来，出现的 double bit ECC error 的次数
    - pci: 出现的 PCI replay 次数
+ metric 类型`t`
    - rxpci: PCI 接收吞吐量，单位 MB / s
    - txpci: PCI 发送吞吐量，单位 MB / s

### 6.2. 通用控制选项
| 选项 | 说明 |
| --- | --- |
| -i,   --id= | 指定特定设备，支持指定多个设备，通过`,`分隔，如`-i 0,1`，可以是如下值：<br/>+ 设备上电后分配的从 0 开始的枚举编号<br/>+ 板卡序列号（serial number）<br/>+ UUID<br/>+ PCI Bus ID<br/>推荐使用 UUID 或者 PCI Bus ID 指定设备：<br/>+ 设备枚举编号在重启后可能不一致<br/>+ 单卡多 PPU 场景，多个 PPU 的板卡序列号相同 |
| -d,   --delay= | 设定两次查询的等待间隔，单位：秒 |
| -c,   --count= | 指定多少次统计周期后停止统计 |
| -o,   --options= | 指定滚动信息是否包含日期或者时间列 |
| -f,   --filename= | 显示结果输出到文件 |

## 7. 监控进程状态
PPU-SMI 支持滚动输出进程监视信息，用户可通过子命令`pmon`使用监控设备功能，每行打印一个设备一个进程的检视信息，每类监视信息作为一列滚动打印，例如执行`ppu-smi pmon`:

```bash
root@122d8d7a7e37:~# ppu-smi pmon
# ppu     pid  type    sm   mem   enc   dec   command
# idx       #   C/G     %     %     %     %   name
    0    4563     C     0     0     0     0   ppu_test
    0    4991     C     0     0     0     0   ppu_test_thread
...
```

通过执行`ppu-smi pmon -h`可查看监视进程功能帮助信息：

```bash
root@122d8d7a7e37:~# ppu-smi pmon -h
Process statistics are displayed in scrolling format per sampling
interval. This tool lists the statistics for all the compute
processes running on each device. Metrics to be monitored
can be adjusted based on the width of terminal window.

ppu-smi pmon [OPTION1 [ARG1]] [OPTION2 [ARG2]] ...
    -i,   --id=
        Enumeration index, Serial number, PCI bus ID or UUID.
        Provide comma separated values for more than one device
    -d,   --delay=
        Collection delay/interval in seconds [default=1sec]
    -c,   --count=
        Collect specified number of samples and exit
    -s,   --select=
        One or more metrics [default=u]
        Can be any of the following:
            u - Utilization
            m - Memory usage
    -o,   --options=
        One or more from the following:
            D - Include Date (YYYYMMDD) in scrolling output
            T - Include Time (HH:MM:SS) in scrolling output
...
```

### 7.1. 监视 Metrics 说明
可通过`-s`选项指定希望监视的 metrics，每个 metric 使用单个字符标识，多个 metric 对应的字符可拼接在一起，作为`-s`选项传入，例如`ppu-smi pmon -s um`，指定进程利用率（u）和内存占用（m）相关 metrics。

```bash
root@122d8d7a7e37:~# ppu-smi pmon -s um
# ppu     pid  type    sm   mem   enc   dec   mem   command
# idx       #   C/G     %     %     %     %    MB   name
    0    4563     C     0     0     0     0   151   ppu_test
    0    4991     C     0     0     0     0   151   ppu_test_thread
```

支持的 metrics 说明如下：

| -s 选项 metric 字符 | 说明 |
| --- | --- |
| u | 进程的处理器 / 内存 / 编码器 / 解码器利用率 |
| m | 进程的内存使用信息 |

PPU-SMI 滚动输出的每列信息，含义说明如下：

+ 基础信息
    - Date: 当前日期
    - Time: 当前时间
    - ppu: 设备上电后分配的从 0 开始的枚举编号
    - pid: 进程的系统 PID
    - type: 进程的类型，C 表示为计算类型（Compute）进程
+ metric 类型`u`
    - sm: 流处理器利用率，单位%
    - mem: 内存利用率，单位%
    - enc: 编码器利用率，单位%
    - dec: 解码器利用率，单位%
+ metric 类型`p`
    - mem: 进程内存占用大小，单位 MiB

### 7.2. 通用控制选项
| 选项 | 说明 |
| --- | --- |
| -i,   --id= | 指定特定设备，支持指定多个设备，通过`,`分隔，如`-i 0,1`，可以是如下值：<br/>+ 设备上电后分配的从 0 开始的枚举编号<br/>+ 板卡序列号（serial number）<br/>+ UUID<br/>+ PCI Bus ID<br/>推荐使用 UUID 或者 PCI Bus ID 指定设备：<br/>+ 设备枚举编号在重启后可能不一致<br/>+ 单卡多 PPU 场景，多个 PPU 的板卡序列号相同 |
| -d,   --delay= | 设定两次查询的等待间隔，单位：秒 |
| -c,   --count= | 指定多少次统计周期后停止统计 |
| -o,   --options= | 指定滚动信息是否包含日期或者时间列 |
| -f,   --filename= | 显示结果输出到文件 |

## 8. 查询 ICN 链路信息
PPU-SMI 支持查询 ICN 链路相关信息，用户可通过子命令`icn`查询 ICN 相关信息，相关结果按照每设备每 ICN 链路的顺序显示，例如执行`ppu-smi icn -s`

```bash
root@dfc623e46a90:~# ppu-smi icn -s
PPU 0: PPU (UUID: GPU-019ea108-c180-040a-0000-000000000000)
    Link 0: 50 GB/s
    Link 1: <inactive>
    Link 2: <inactive>
    Link 3: 50 GB/s
    Link 4: 50 GB/s
    Link 5: 50 GB/s
    Link 6: 50 GB/s
PPU 1: PPU (UUID: GPU-019ea108-c180-060c-0000-000000000000)
    Link 0: 50 GB/s
    Link 1: <inactive>
    Link 2: <inactive>
    Link 3: 50 GB/s
...
```

通过执行`ppu-smi icn -h`可查看 ICN 功能帮助信息，用户可通过`-i`和`-l`选项约束查询的设备和链路范围（不指定表示查询所有），用户每次可指定一个 ICN 查询子选项（例如`-s`）进行查询：

```bash
root@dfc623e46a90:~# ppu-smi icn -h
icn -- Display ICN link information.

ppu-smi icn [OPTION1 [ARG1]] [OPTION2 [ARG2]] ...
    -h,   --help
        Display help information
    -i,   --id=
        Enumeration index, Serial number, PCI bus ID or UUID.
        Provide comma separated values for more than one device.
    -l,   --link=
        Specify a target link ID (0-based link index),
        Without this parameter, all links information are displayed.

    [any one of]

    -s,   --status
        Display link state (active/inactive).
    -c,   --capabilities
        Display link capabilities.
    -p,   --pcibusid
        Display remote node PCI bus ID for a link.
    -r,   --remotelinkinfo
        Display remote device PCI bus ID and ICN link ID for a link.
```

### 8.1. 查询 ICN 链路状态
使用`ppu-smi icn -s`查询链路的激活状态，带宽规格等信息，用户可通过`-i`选项约束查询的设备，例如执行`ppu-smi icn -s -i 0`，查询结果说明如下：

```bash
root@dfc623e46a90:~# ppu-smi icn -s -i 0
PPU 0: PPU (UUID: GPU-019ea108-c180-040a-0000-000000000000)
    Link 0: 50 GB/s
    Link 1: <inactive>
    Link 2: <inactive>
    Link 3: 50 GB/s
    Link 4: 50 GB/s
    Link 5: 50 GB/s
    Link 6: 50 GB/s
```

+ `Link 0: 50 GB/s`：PPU 0 的 ICN link 0 连接了其他设备，带宽为 50 GB/s
+ `Link 1: <inactive>`: PPU 0 的 ICN link 1 未连接其他设备

### 8.2. 查询 ICN 链路能力
使用`ppu-smi icn -c`查询每条 ICN 链路的能力，仅显示激活的 ICN 链路信息，查询结果示例如下：

```bash
root@dfc623e46a90:~# ppu-smi icn -c
PPU 0: PPU (UUID: GPU-019ea108-c180-040a-0000-000000000000)
    Link 0, P2P is supported: true
    Link 0, Access to system memory is supported: false
    Link 0, P2P atomics is supported: true
    Link 0, System memory atomics is supported: false
    Link 0, SLI is supported: false
    Link 0, Link is supported: true
    Link 3, P2P is supported: true
    Link 3, Access to system memory is supported: false
    Link 3, P2P atomics is supported: true
    Link 3, System memory atomics is supported: false
    Link 3, SLI is supported: false
    Link 3, Link is supported: true
...
```

### 8.3. 查询链路对端 PCI Bus ID
使用`ppu-smi icn -p`查询 ICN 链路对端设备的 PCI Bus ID，仅显示激活的 ICN 链路信息，查询结果示例如下：

```bash
root@dfc623e46a90:~# ppu-smi icn -p
PPU 0: PPU (UUID: GPU-019ea108-c180-040a-0000-000000000000)
    Link 0: 00000001:CE:00.0
    Link 3: 00000000:89:00.0
    Link 4: 00000000:89:00.0
    Link 5: 00000000:CC:00.0
    Link 6: 00000001:CE:00.0
PPU 1: PPU (UUID: GPU-019ea108-c180-060c-0000-000000000000)
    Link 0: 00000001:D1:00.0
    Link 3: 00000000:C9:00.0
    Link 4: 00000000:86:00.0
    Link 5: 00000000:86:00.0
    Link 6: 00000001:D1:00.0
...
```

### 8.4. 查询链路对端信息
使用`ppu-smi icn -r`查询 ICN 链路对端的信息，包含对端设备的 PCI Bus ID，以及对端的 ICN 链路索引，查询结果示例如下：

```bash
root@dfc623e46a90:~# ppu-smi icn -r
PPU 0: PPU (UUID: GPU-019ea108-c180-040a-0000-000000000000)
    Link 0: Remote Device 00000001:CE:00.0: Link 6
    Link 3: Remote Device 00000000:89:00.0: Link 1
    Link 4: Remote Device 00000000:89:00.0: Link 1
    Link 5: Remote Device 00000000:CC:00.0: Link 3
    Link 6: Remote Device 00000001:CE:00.0: Link 6
PPU 1: PPU (UUID: GPU-019ea108-c180-060c-0000-000000000000)
    Link 0: Remote Device 00000001:D1:00.0: Link 7
    Link 3: Remote Device 00000000:C9:00.0: Link 2
    Link 4: Remote Device 00000000:86:00.0: Link 0
    Link 5: Remote Device 00000000:86:00.0: Link 0
    Link 6: Remote Device 00000001:D1:00.0: Link 7
...
```

### 8.5. 查询线缆在位状态
使用`ppu-smi icn -cs`查询 ICN 链路各端口线路的在位状态，查询结果示例如下：

```bash
root@dfc623e46a90:~# ppu-smi icn -cs
PPU 0: t-head ppu 0 (UUID: GPU-3f53d39f-ce6e-dc78-c3d4-4c18653c19c0)
    Link 0: Connected
    Link 1: Disconnected
    Link 2: Connected
...
PPU 1: t-head ppu 1 (UUID: GPU-3f53d39f-ce6e-dc78-c3d4-4c18653c19c1)
    Link 0: Connected
    Link 1: Connected
    Link 2: Connected
...
```

> **注意：** 部分 PPU 产品不支持线缆在位检测，对于此类 PPU 查询线缆状态将提示不支持此功能。

### 8.6. 查询链路位宽
使用`ppu-smi icn -lw`查询 ICN 链路位宽，仅显示激活的 ICN 链路信息，查询结果示例如下：

```bash
root@dfc623e46a90:~# ppu-smi icn -lw
PPU 0: PPU-ZW810 (UUID: GPU-019ea108-4111-0220-0000-0000006ef62f)
    Link 0: 16x
    Link 3: 16x
    Link 4: 16x
    Link 5: 16x
    Link 6: 8x
PPU 1: PPU-ZW810 (UUID: GPU-019ea108-8191-042a-0000-0000c0d6cc1d)
    Link 0: 16x
    Link 3: 16x
    Link 4: 16x
    Link 5: 16x
    Link 6: 8x
...
```

+ `16x`：链路位宽为 16bit
+ `8x`：链路位宽为 8bit

### 8.7. 查询链路到物理端口的映射
使用`ppu-smi icn -lm`查询 ICN 链路到物理端口的映射关系，查询结果示例如下：

```bash
root@dfc623e46a90:~# ppu-smi icn -lm
PPU 0: PPU-ZW810 (UUID: GPU-019ea108-4111-0220-0000-0000006ef62f)
    Link 0: Physical Port 2
    Link 1: N/A
    Link 2: Physical Port 5
...
PPU 1: PPU-ZW810 (UUID: GPU-019ea108-8191-042a-0000-0000c0d6cc1d)
    Link 0: Physical Port 2
    Link 1: N/A
    Link 2: Physical Port 5
...
```

+ 无物理端口映射的链路将显示为`N/A`

> **注意：** 部分 PPU 产品不支持查询物理端口的映射，对于此类 PPU 查询线缆状态将显示为`N/A`。

### 8.8. 查询链路统计数据和错误计数
使用`ppu-smi icn -e`查询 ICN 链路统计数据和错误计数，仅显示激活的 ICN 链路信息，查询结果示例如下：

```bash
PPU 0: PPU-ZW810 (UUID: GPU-019ea108-4111-0220-0000-0000006ef62f)
    Link 0: 2 link up times
    Link 0: 1 link down times
    Link 0: 0 FEC correctable errors
    Link 0: 0 FEC uncorrectable errors
    Link 0: 0 TX packet errors
    Link 0: 0 RX packet errors
    Link 0: 13 total TX packets
    Link 0: 11 total RX packets

    Link 3: 2 link up times
    Link 3: 1 link down times
    Link 3: 0 FEC correctable errors
    Link 3: 0 FEC uncorrectable errors
    Link 3: 0 TX packet errors
    Link 3: 0 RX packet errors
    Link 3: 16 total TX packets
    Link 3: 8 total RX packets
...

PPU 1: PPU-ZW810 (UUID: GPU-019ea108-8191-042a-0000-0000c0d6cc1d)
    Link 0: 2 link up times
    Link 0: 1 link down times
    Link 0: 0 FEC correctable errors
    Link 0: 0 FEC uncorrectable errors
    Link 0: 0 TX packet errors
    Link 0: 0 RX packet errors
    Link 0: 9 total TX packets
    Link 0: 4 total RX packets
...
```

+ `link up times`：链路上线的次数
+ `link down times`：链路下线的次数
+ `FEC correctable errors`：链路 FEC 可纠错的错误计数
+ `FEC uncorrectable errors`：链路 FEC 不可纠错的错误计数
+ `TX packet errors`：链路发送错误的包数
+ `RX packet errors`：链路接收错误的包数
+ `total TX packets`：链路总的发送包数
+ `total RX packets`：链路总的接收包数

### 8.9. 查询链路吞吐量
使用`ppu-smi icn -gt r`查询 ICN 链路当前的数据吞吐量汇总，查询结果示例如下：

```bash
root@0549cf16bb85:~# ppu-smi icn -gt r
PPU 0: PPU (UUID: GPU-019ea108-c110-0828-0000-000000000000)
    Link 0: Raw Tx: 1618498333 KiB
    Link 0: Raw Rx: 1657515730 KiB
    Link 3: Raw Tx: 1653010223 KiB
    Link 3: Raw Rx: 1693049419 KiB
    Link 4: Raw Tx: 1622645860 KiB
    Link 4: Raw Rx: 1662045442 KiB
...
PPU 1: PPU (UUID: GPU-019ea108-c120-040c-0000-000000000000)
    Link 0: Raw Tx: 1618498333 KiB
    Link 0: Raw Rx: 1657515730 KiB
    Link 3: Raw Tx: 1653010223 KiB
    Link 3: Raw Rx: 1693049419 KiB
    Link 4: Raw Tx: 1622645860 KiB
    Link 4: Raw Rx: 1662045442 KiB
...
```

## 9. 查询设备间拓扑信息
PPU-SMI 支持查询设备间的拓扑信息，用户可通过子命令`topo`查询相关信息，例如执行`ppu-smi topo -m`:

```bash
root@dfc623e46a90:~# ppu-smi topo -m
         PPU0    PPU1    PPU2    PPU3    PPU4    PPU5    PPU6    PPU7    CPU Affinity    NUMA Affinity
 PPU0    X       ICN2    SYS     ICN1    SYS     SYS     ICN2    SYS     0-47,96-143     0
 PPU1    ICN2    X       ICN1    SYS     SYS     SYS     SYS     ICN2    0-47,96-143     0
 PPU2    SYS     ICN1    X       ICN2    ICN1    ICN1    SYS     SYS     0-47,96-143     0
 PPU3    ICN1    SYS     ICN2    X       ICN1    ICN1    SYS     SYS     0-47,96-143     0
 PPU4    SYS     SYS     ICN1    ICN1    X       ICN2    SYS     ICN1    48-95,144-191   1
 PPU5    SYS     SYS     ICN1    ICN1    ICN2    X       ICN1    SYS     48-95,144-191   1
 PPU6    ICN2    SYS     SYS     SYS     SYS     ICN1    X       ICN2    48-95,144-191   1
 PPU7    SYS     ICN2    SYS     SYS     ICN1    SYS     ICN2    X       48-95,144-191   1
...
```

通过执行`ppu-smi topo -h`可查询拓扑信息相关帮助信息，用户每次可指定一个`topo`查询子选项（例如`-m`）进行查询。在使用`-n`或者`-p`选项时，需要通过`-i`选项指定相关设备：

```bash
root@dfc623e46a90:~# ppu-smi topo -h
topo -- Display topological information about the system.

ppu-smi topo [OPTION1 [ARG1]] [OPTION2 [ARG2]] ...
    -h,   --help
        Display help information
    -i,   --id=
        Enumeration index, Serial number, PCI bus ID or UUID.
        Provide comma separated values for more than one device.
        Must be used in conjunction with -n or -p.
    -ri,  --rear-id=
        When used with the option to display matrix (-m or -mp),
        Show PPU devices that match the specified rear id.
    -po,  --ppu-only
        When used with the option to display matrix (-m or -mp),
        Show PPU devices only.
    -rg,  --rear-group
        When used with the option to display matrix (-m or -mp),
        Group PPU device by rear id.

    [any one of]

    -m,   --matrix
        Display the PPUDirect communication matrix for the system.
    -mp,  --matrix_pci
        Display the PPUDirect communication matrix for the system (PCI Only).
    -lni, --list-network-interface
        Display a list of RDMA network interface controller(NIC) connected to the system.
    -c,   --cpu=
        Specify a CPU number, Display all PPUs with an affinity.
    -n,   --nearest_ppus=
        Display the nearest PPUs for a given traversal path.
        Could be one of the following:
            0 = a single PCIe switch on a dual PPU board
            1 = a single PCIe switch
            2 = multiple PCIe switches
            3 = a PCIe host bridge
            4 = an on-CPU interconnect link between PCIe host bridges
            5 = an SMP interconnect link between NUMA nodes
        Used in conjunction with -i which must be a single device ID.
    -p,   --ppu_path
        Display the most direct path traversal for a pair of PPUs.
        Used in conjunction with -i which must be a pair of device IDs.
    -p2p, --p2pstatus=
        Displays the p2p status between the PPUs of a given p2p capability.
        Could be one of the following:
            r - p2p read capability
            w - p2p write capability
            n - p2p ICN link capability
            a - p2p atomics capability
            p - p2p prop capability
```

### 9.1. 查询拓扑矩阵信息
通过执行`ppu-smi topo -m`，可查询两两设备间的连接状态，以及 PPU 和 RDMA 网卡之间的连接状态，若 ICN 链路激活，优先显示互联的 ICN 链路信息，查询结果说明如下：

```bash
root@dfc623e46a90:/# ppu-smi topo -m
         PPU0    PPU1    PPU2    PPU3    PPU4    PPU5    PPU6    PPU7    NIC0    NIC1    NIC2    NIC3    NIC4    NIC5    NIC6    NIC7    CPU Affinity    NUMA Affinity
 PPU0    X       ICN2    SYS     ICN1    SYS     SYS     ICN2    SYS     PXB     SYS     SYS     SYS     SYS     SYS     PXB     SYS     0-47,96-143     0
 PPU1    ICN2    X       ICN1    SYS     SYS     SYS     SYS     ICN2    PIX     SYS     SYS     SYS     SYS     SYS     PIX     SYS     0-47,96-143     0
 PPU2    SYS     ICN1    X       ICN2    ICN1    ICN1    SYS     SYS     SYS     PXB     SYS     SYS     SYS     SYS     SYS     PXB     0-47,96-143     0
 PPU3    ICN1    SYS     ICN2    X       ICN1    ICN1    SYS     SYS     SYS     PXB     SYS     SYS     SYS     SYS     SYS     PXB     0-47,96-143     0
 PPU4    SYS     SYS     ICN1    ICN1    X       ICN2    SYS     ICN1    SYS     SYS     SYS     PXB     SYS     SYS     SYS     SYS     48-95,144-191   1
 PPU5    SYS     SYS     ICN1    ICN1    ICN2    X       ICN1    SYS     SYS     SYS     SYS     PXB     SYS     SYS     SYS     SYS     48-95,144-191   1
 PPU6    ICN2    SYS     SYS     SYS     SYS     ICN1    X       ICN2    SYS     SYS     PXB     SYS     SYS     PXB     SYS     SYS     48-95,144-191   1
 PPU7    SYS     ICN2    SYS     SYS     ICN1    SYS     ICN2    X       SYS     SYS     PIX     SYS     SYS     PIX     SYS     SYS     48-95,144-191   1
 NIC0    PXB     PIX     SYS     SYS     SYS     SYS     SYS     SYS     X       SYS     SYS     SYS     SYS     SYS     PIX     SYS     0-47,96-143     0
 NIC1    SYS     SYS     PXB     PXB     SYS     SYS     SYS     SYS     SYS     X       SYS     SYS     SYS     SYS     SYS     PIX     0-47,96-143     0
 NIC3    SYS     SYS     SYS     SYS     SYS     SYS     PXB     PIX     SYS     SYS     X       SYS     SYS     PIX     SYS     SYS     48-95,144-191   1
 NIC4    SYS     SYS     SYS     SYS     PXB     PXB     SYS     SYS     SYS     SYS     SYS     X       SYS     SYS     SYS     SYS     48-95,144-191   1
 NIC5    SYS     SYS     SYS     SYS     SYS     SYS     SYS     SYS     SYS     SYS     SYS     SYS     X       SYS     SYS     SYS     0-47,96-143     0
 NIC6    SYS     SYS     SYS     SYS     SYS     SYS     PXB     PIX     SYS     SYS     PIX     SYS     SYS     X       SYS     SYS     48-95,144-191   1
 NIC7    PXB     PIX     SYS     SYS     SYS     SYS     SYS     SYS     PIX     SYS     SYS     SYS     SYS     SYS     X       SYS     48-95,144-191   1

Legend:

  X    = Self
  SYS  = Connection traversing PCIe as well as the SMP interconnect between NUMA nodes (e.g., QPI/UPI)
  NODE = Connection traversing PCIe as well as the interconnect between PCIe Host Bridges within a NUMA node
  PHB  = Connection traversing PCIe as well as a PCIe Host Bridge (typically the CPU)
  PXB  = Connection traversing multiple PCIe bridges (without traversing the PCIe Host Bridge)
  PIX  = Connection traversing at most a single PCIe bridge
  ICN# = Connection traversing a bonded set of # ICN links

NIC Legend:

  NIC0: mlx5_bond_0
  NIC1: mlx5_bond_1
  NIC2: mlx5_bond_2
  NIC3: mlx5_bond_3
  NIC4: mlx5_bond_4
  NIC5: mlx5_bond_5
  NIC6: mlx5_bond_6
  NIC7: mlx5_bond_7

PPU Rear Group:

  Rear ID 0: PPU 0,1,2,3,4,5,6,7
```

+ `ICN2`：例如 PPU0 和 PPU1 之间有 2 个激活的 ICN 链路，显示为`ICN2`，链路可能是 PPU 之间直接连接，或者通过 ICNSwitch 路由连接
+ `SYS`：例如 PPU0 和 PPU2 之间无激活的 ICN 链路，将显示基于 PCIe 总线的链接状态信息，具体含义参见`Legend`标注说明
+ `CPU Affinity 0-47,96-143`: PPU 设备和 CPU 核的亲和关系说明，例如 PPU0 亲和的 CPU 核为：`CPU0至CPU47`以及`CPU96至CPU143`
+ `NUMA Affinity 0`: PPU 设备和 NUMA node 的亲和信息，例如 PPU0 亲和的 NUMA node 为`node 0`
+ `NIC0`：连接在系统上的 RDMA 网卡设备，通过`NIC Legend`查看实际对应的网卡设备名称
+ `PPU Rear Group`：按照机尾分组的 PPU 列表。每行显示连接在本机尾的 PPU 列表

通过选项`-po`可在拓扑矩阵中只显示 PPU 设备不显示 RDMA 网卡，通过选项`-mp`可只显示 PCI 总线连接关系，不包含 ICN 链接的连接状态。

例如执行`ppu-smi topo -mp -po`，可查询两两 PPU 设备间 PCI 总线连接关系，查询结果示例如下：

```bash
root@dfc623e46a90:/# ppu-smi topo -mp -po
         PPU0    PPU1    PPU2    PPU3    PPU4    PPU5    PPU6    PPU7    CPU Affinity    NUMA Affinity
 PPU0    X       PXB     SYS     SYS     SYS     SYS     SYS     SYS     0-47,96-143     0
 PPU1    PXB     X       SYS     SYS     SYS     SYS     SYS     SYS     0-47,96-143     0
 PPU2    SYS     SYS     X       PXB     SYS     SYS     SYS     SYS     0-47,96-143     0
 PPU3    SYS     SYS     PXB     X       SYS     SYS     SYS     SYS     0-47,96-143     0
 PPU4    SYS     SYS     SYS     SYS     X       PXB     SYS     SYS     48-95,144-191   1
 PPU5    SYS     SYS     SYS     SYS     PXB     X       SYS     SYS     48-95,144-191   1
 PPU6    SYS     SYS     SYS     SYS     SYS     SYS     X       PXB     48-95,144-191   1
 PPU7    SYS     SYS     SYS     SYS     SYS     SYS     PXB     X       48-95,144-191   1

Legend:

  X    = Self
  SYS  = Connection traversing PCIe as well as the SMP interconnect between NUMA nodes (e.g., QPI/UPI)
  NODE = Connection traversing PCIe as well as the interconnect between PCIe Host Bridges within a NUMA node
  PHB  = Connection traversing PCIe as well as a PCIe Host Bridge (typically the CPU)
  PXB  = Connection traversing multiple PCIe bridges (without traversing the PCIe Host Bridge)
  PIX  = Connection traversing at most a single PCIe bridge
```

#### 9.1.1. 按照机尾过滤和分组
PPU-SMI 支持显示拓扑矩阵时指定机尾 ID，只显示连接在指定机尾的 PPU 之间的拓扑信息。通过选项`-ri`指定过滤的机尾 ID。PPU 对应的机尾 ID 可通过`ppu-smi -q`或者`ppu-smi --query-ppu`等命令查询，也可查看拓扑矩阵显示的`PPU Rear Group`信息获取分组信息。

例如执行`ppu-smi topo -m -po -ri 1`，查询机尾 ID 为 1 的 PPU 之间的拓扑信息，查询结果示例如下，只有机尾 ID 为 1 的 PPU 1,3,5 等被显示，连接在其他机尾的 PPU 将不显示：

```bash
root@dfc623e46a90:/# ppu-smi topo -m -po -ri 1
         PPU1    PPU3    PPU5    PPU7    PPU9    PPU11   PPU13   PPU15  CPU Affinity    NUMA Affinity
 PPU1    X       ICN2    SYS     ICN1    SYS     SYS     ICN2    SYS    0-47,96-143     0
 PPU3    ICN2    X       ICN1    SYS     SYS     SYS     SYS     ICN2   0-47,96-143     0
 PPU5    SYS     ICN1    X       ICN2    ICN1    ICN1    SYS     SYS    0-47,96-143     0
 PPU7    ICN1    SYS     ICN2    X       ICN1    ICN1    SYS     SYS    0-47,96-143     0
 PPU9    SYS     SYS     ICN1    ICN1    X       ICN2    SYS     ICN1   48-95,144-191   1
 PPU11   SYS     SYS     ICN1    ICN1    ICN2    X       ICN1    SYS    48-95,144-191   1
 PPU13   ICN2    SYS     SYS     SYS     SYS     ICN1    X       ICN2   48-95,144-191   1
 PPU15   SYS     ICN2    SYS     SYS     ICN1    SYS     ICN2    X      48-95,144-191   1

...

PPU Rear Group:

  Rear ID 1: PPU 1,3,5,7,9,11,13,15
```

PPU-SMI 支持显示拓扑矩阵时按照机尾 ID 分组，拓扑矩阵中的 PPU 将先按照机尾 ID 排序，再按照 PPU 索引排序，例如机尾 ID 为 0 的 PPU 将集中排列在前显示。

通过选项`-rg`使能按照机尾 ID 分组功能，例如执行`ppu-smi topo -mp -po -rg`，查询结果示例如下，PPU 首先按照机尾 ID 排列：

```bash
root@dfc623e46a90:/# ppu-smi topo -mp -po -rg
         PPU0    PPU2    PPU4    PPU6    PPU8    PPU10   PPU12   PPU14   PPU1    PPU3    PPU5    PPU7    PPU9    PPU11   PPU13   PPU15   CPU Affinity    NUMA Affinity
 PPU0    X       PHB     SYS     PXB     NODE    PIX     PHB     SYS     PXB     NODE    PIX     PHB     SYS     PXB     NODE    PIX     0-1,64-65       0
 PPU2    PHB     X       PXB     NODE    PIX     PHB     SYS     PXB     NODE    PIX     PHB     SYS     PXB     NODE    PIX     PHB     0-1,64-65       0
 PPU4    SYS     PXB     X       PIX     PHB     SYS     PXB     NODE    PIX     PHB     SYS     PXB     NODE    PIX     PHB     SYS     0-1,64-65       0
 PPU6    PXB     NODE    PIX     X       SYS     PXB     NODE    PIX     PHB     SYS     PXB     NODE    PIX     PHB     SYS     PXB     0-1,64-65       0
 PPU8    NODE    PIX     PHB     SYS     X       NODE    PIX     PHB     SYS     PXB     NODE    PIX     PHB     SYS     PXB     NODE    0-1,64-65       0
 PPU10   PIX     PHB     SYS     PXB     NODE    X       PHB     SYS     PXB     NODE    PIX     PHB     SYS     PXB     NODE    PIX     0-1,64-65       0
 PPU12   PHB     SYS     PXB     NODE    PIX     PHB     X       PXB     NODE    PIX     PHB     SYS     PXB     NODE    PIX     PHB     0-1,64-65       0
 PPU14   SYS     PXB     NODE    PIX     PHB     SYS     PXB     X       PIX     PHB     SYS     PXB     NODE    PIX     PHB     SYS     0-1,64-65       0
 PPU1    PXB     NODE    PIX     PHB     SYS     PXB     NODE    PIX     X       SYS     PXB     NODE    PIX     PHB     SYS     PXB     0-1,64-65       0
 PPU3    NODE    PIX     PHB     SYS     PXB     NODE    PIX     PHB     SYS     X       NODE    PIX     PHB     SYS     PXB     NODE    0-1,64-65       0
 PPU5    PIX     PHB     SYS     PXB     NODE    PIX     PHB     SYS     PXB     NODE    X       PHB     SYS     PXB     NODE    PIX     0-1,64-65       0
 PPU7    PHB     SYS     PXB     NODE    PIX     PHB     SYS     PXB     NODE    PIX     PHB     X       NODE    PIX     PHB     SYS     0-1,64-65       0
 PPU9    SYS     PXB     NODE    PIX     PHB     SYS     PXB     NODE    PIX     PHB     SYS     PXB     X       PIX     PHB     SYS     0-1,64-65       0
 PPU11   PXB     NODE    PIX     PHB     SYS     PXB     NODE    PIX     PHB     SYS     PXB     NODE    PIX     X       SYS     PXB     0-1,64-65       0
 PPU13   NODE    PIX     PHB     SYS     PXB     NODE    PIX     PHB     SYS     PXB     NODE    PIX     PHB     SYS     PXB     NODE    0-1,64-65       0
 PPU15   PIX     PHB     SYS     PXB     NODE    PIX     PHB     SYS     PXB     NODE    PIX     PHB     SYS     PXB     NODE    PIX     0-1,64-65       0

 ...

 PPU Rear Group:

  Rear ID 0: PPU 0,2,4,6,8,10,12,14
  Rear ID 1: PPU 1,3,5,7,9,11,13,15
```

### 9.2. 查询 RDMA 网卡设备列表
PPU-SMI 支持通过选项`-lni`查询系统中的 RDMA 网卡信息，例如执行`ppu-smi topo -lni`，将会显示网卡的列表，包含名称和 PCI Bus Id 等信息，查询结果示例如下：

```bash
root@dfc623e46a90:/# ppu-smi topo -lni
NIC 0: mlx5_bond_0 (PCI Bus Id: 00000000:8A:00.1)
NIC 1: mlx5_bond_1 (PCI Bus Id: 00000000:CF:00.1)
NIC 2: mlx5_bond_2 (PCI Bus Id: 00000001:D2:00.0)
NIC 3: mlx5_bond_3 (PCI Bus Id: 00000001:87:00.0)
NIC 4: mlx5_bond_4 (PCI Bus Id: 00000000:2A:00.1)
NIC 5: mlx5_bond_5 (PCI Bus Id: 00000001:D2:00.1)
NIC 6: mlx5_bond_6 (PCI Bus Id: 00000000:8A:00.0)
NIC 7: mlx5_bond_7 (PCI Bus Id: 00000000:CF:00.0)
```

### 9.3. 查询指定 CPU 的亲和设备列表
PPU-SMI 支持查询指定 CPU 的亲和设备列表，通过`-c`选项指定 CPU 索引，例如执行`ppu-smi topo -c 0`，查询 CPU 0 的亲和设备列表，查询结果示例如下：

```bash
root@dfc623e46a90:/# ppu-smi topo -c 0
The PPUs that have an affinity with CPU 0 are: 0, 1, 2, 3
```

### 9.4. 查询临近的 PPU 设备列表
PPU-SMI 支持查询指定 PPU 的临近设备列表，通过`-n`选项指定查询的`拓扑范围`，`拓扑范围`的定义参见帮助信息，通过`-i`选项指定目标 PPU 设备。例如执行`ppu-smi topo -n 5 -i 0`，查询结果示例如下：

```bash
root@dfc623e46a90:/# ppu-smi topo -n 5 -i 0
Device 0 is connected by way of a SMP interconnect link between NUMA nodes to device(s): 1, 2, 3, 4, 5, 6, 7
```

### 9.5. 查询两个 PPU 设备间最短路径
PPU-SMI 支持查询两个 PPU 设备之间的最短路径，通过`-i`选项指定 2 个 PPU 设备，例如执行`ppu-smi topo -p -i 0,1`，查询结果示例如下：

```bash
root@dfc623e46a90:/# ppu-smi topo -p -i 0,1
Device 0 is connected to device 1 by way of potentially multiple PCIe switches.
```

### 9.6. 查询设备间 P2P 能力
通过`-p2p`选项指定一种`能力类型`，PPU-SMI 可显示设备间的 P2P 能力支持状态，`能力类型`的定义参见帮助信息。例如执行`ppu-smi topo -p2p r`，查询设备间`P2P read`的能力，查询结果示例如下：

```bash
root@dfc623e46a90:/# ppu-smi topo -p2p r
         PPU0    PPU1    PPU2    PPU3    PPU4    PPU5    PPU6    PPU7
 PPU0    X       OK      OK      OK      OK      OK      OK      OK
 PPU1    OK      X       OK      OK      OK      OK      OK      OK
 PPU2    OK      OK      X       OK      OK      OK      OK      OK
 PPU3    OK      OK      OK      X       OK      OK      OK      OK
 PPU4    OK      OK      OK      OK      X       OK      OK      OK
 PPU5    OK      OK      OK      OK      OK      X       OK      OK
 PPU6    OK      OK      OK      OK      OK      OK      X       OK
 PPU7    OK      OK      OK      OK      OK      OK      OK      X

Legend:

  X    = Self
  OK   = Status Ok
  CNS  = Chipset not supported
  PNS  = PPU not supported
  TNS  = Topology not supported
  NS   = Not supported
  U    = Unknown
```

平台扩展关联：`topo -m` 的 ICN/SYS 信息面向多卡部署，不属于本次单卡比赛路径。比赛只用 CPU/NUMA 亲和列把 host 预处理和 scheduler 线程绑定到目标 810E 的本地 NUMA 节点。

## 10. 管理多设备实例 (MIG)
PPU-SMI 支持查询 MIG 模式下各实例信息，并支持创建 / 删除相关实例。MIG 相关概念介绍如下：

+ GPU instance：PPU 硬件资源切分为若干实例，每个实例为一个 GPU instance。GPU instance 互相之间隔离运行。
+ GPU instance profile：表示支持的 PPU 硬件资源切分方法，例如本切分实例支持独占的 CU 个数和内存大小等
+ Compute instance：GPU instance 切分为若干实例，每个实例为一个 Compute instance。Compute instance 独占 CU 资源，复用其他资源。应用可指定在 Compute instance 上运行。
+ Compute instance profile：表示支持的 GPU instance 切分方法，例如本切分实例支持独占的 CU 个数，以及共享的资源情况。

用户可通过执行`ppu-smi -mig 1`开启 PPU 设备的 MIG 模式（详细信息参见[修改设备配置](#Kgcc3)）。用户可通过子命令`mig`查询 MIG 相关信息，例如执行`ppu-smi mig -lgip`查看支持的 GPU instance profile 信息：

```bash
root@0549cf16bb85:~# ppu-smi mig -lgip
+---------------------------------------------------------------------------------+
| GPU instance profiles:                                                          |
| PPU  Name                 Profile  Instances   Memory  P2P  CU      DEC   ENC   |
|                             ID     Free/Total   GiB         CpyEng  JPEG  OFA   |
+=================================================================================+
| 1    MIG 8g48gb              3        0/1      48.00   No   64      4     4     |
|                                                             2       4     0     |
+---------------------------------------------------------------------------------+
| 1    MIG 4g24gb              2        1/2      24.00   No   32      2     2     |
|                                                             2       2     0     |
+---------------------------------------------------------------------------------+
| 1    MIG 2g12gb              1        2/4      12.00   No   16      1     1     |
|                                                             2       1     0     |
+---------------------------------------------------------------------------------+
| 1    MIG 1g6gb               0        4/8      6.00    No   8       0     0     |
|                                                             2       0     0     |
+---------------------------------------------------------------------------------+
```

通过执行`ppu-smi mig -h`可查询 MIG 相关帮助信息，用户每次可指定一个`mig`查询子选项进行查询。部分子选项可通过`-i` / `-gi` / `-ci`约束操作范围，指定的范围可组合或单独使用，比如`-i 0 -gi 1`可指定作用域`PPU0`的`gpu instance 1`。

```bash
root@dfc623e46a90:/# ppu-smi mig -h
mig -- Multi Instance GPU management.

ppu-smi mig [OPTION1 [ARG1]] [OPTION2 [ARG2]] ...
    -h,   --help
        Display help information
    -i,   --id=
        Enumeration index, Serial number, PCI bus ID or UUID.
        Provide comma separated values for more than one device.
    -gi,  --gpu-instance-id=
        GPU instance ID.
        Provide comma separated values for more than one GPU instance.
    -ci,  --compute-instance-id=
        Compute instance ID.
        Provide comma separated values for more than one compute instance.
    -C,   --default-compute-instance
        When used with the option to create a GPU instance (-cgi),
        Create compute instance with the default profile.

    [any one of]

    -lgip,--list-gpu-instance-profiles
        List supported GPU instance profiles.
        Option -i can be used to restrict the command to run on a specific PPU.
    -lgipp,--list-gpu-instance-possible-placements
        List possible GPU instance placements in the following format:
          {Start,Start...}:Size
        Option -i can be used to restrict the command to run on a specific PPU.
    -cgi, --create-gpu-instance=
        Create GPU instances for the given profile tuples.
        A profile tuple consists of a profile name or ID and an optional placement specifier,
        which consists of a colon and a placement start index.
        Provide comma separated values for more than one profile tuple(e.g. 1:0,4:2).
        Option -i can be used to restrict the command to run on a specific PPU.
    -dgi, --destroy-gpu-instance
        Destroy GPU instances.
        Options -i and -gi can be used individually or combined
        to restrict the command to run on a specific PPU or GPU instance.
    -lgi, --list-gpu-instances
        List GPU instances.
        Option -i can be used to restrict the command to run on a specific PPU.
    -r,   --reset-gpu-instance
        Trigger reset of the GPU instance.
        Options -i and -gi can be used individually or combined
        to restrict the command to run on a specific PPU or GPU instance.
    -lcip,--list-compute-instance-profiles
        List supported compute instance profiles.
        Options -i and -gi can be used individually or combined
        to restrict the command to run on a specific PPU or GPU instance.
    -lcipp,--list-compute-instance-possible-placements
        List possible compute instance placements in the following format:
          {Start,Start...}:Size
        Options -i and -gi can be used individually or combined
        to restrict the command to run on a specific PPU or GPU instance.
    -cci, --create-compute-instance=
        Create compute instance for the given profile tuples.
        A profile tuple consists of a profile name or ID and an optional placement specifier,
        which consists of a colon and a placement start index.
        Provide comma separated values for more than one profile tuple(e.g. 1:0,4:2).
        If no profile name or ID is given, then the default*
        compute instance profile ID will be used.
        Options -i and -gi can be used individually or combined
        to restrict the command to run on a specific PPU or GPU instance.
    -dci, --destroy-compute-instance
        Destroy compute instances.
        Options -i, -gi and -ci can be used individually or combined
        to restrict the command to run on a specific PPU or GPU instance or compute instance.
    -lci, --list-compute-instances
        List compute instances.
        Options -i and -gi can be used individually or combined
        to restrict the command to run on a specific PPU or GPU instance.
```

### 10.1. 查询 GPU Instance profile 信息
通过`-lgip`选项可查询 GPU instance profile 信息，后续可通过`-cgi`选项指定其中某类 profile 信息创建 GPU instance。通过`-i`选项可约束查询的设备范围，例如执行`ppu-smi mig -i 1 -lgip`，查询结果说明如下：

```bash
root@a475cc8d4c49:/# ppu-smi mig -i 1 -lgip
+---------------------------------------------------------------------------------+
| GPU instance profiles:                                                          |
| PPU  Name                 Profile  Instances   Memory  P2P  CU      DEC   ENC   |
|                             ID     Free/Total   GiB         CpyEng  JPEG  OFA   |
+=================================================================================+
| 1    MIG 8g96gb              3        1/1      96.00   No   64      4     4     |
|                                                             2       4     0     |
+---------------------------------------------------------------------------------+
| 1    MIG 4g48gb              2        2/2      48.00   No   32      2     2     |
|                                                             2       2     0     |
+---------------------------------------------------------------------------------+
| 1    MIG 2g24gb              1        4/4      24.00   No   16      1     1     |
|                                                             2       1     0     |
+---------------------------------------------------------------------------------+
| 1    MIG 1g12gb              0        8/8      12.00   No   8       0     0     |
|                                                             2       0     0     |
+---------------------------------------------------------------------------------+
```

+ PPU: 设备上电后分配的从 0 开始的枚举编号
+ Name: GPU instance profile 的名称，后续可通过`-cgi`指定此名称来创建 GPU instance
+ Profile ID: GPU instance profile 的 ID 编号，后续可通过`-cgi`指定此 ID 来创建 GPU instance
+ Instances Free/Total: 本 profile 剩余可创建的 GPU instance 个数 / 总共可支持创建的 GPU instance 个数
+ Memory GiB: 本 profile 分配的设备内存，单位`GiB`
+ P2P: 本 profile 是否支持 peer-to-peer 能力
+ CU: 本 profile 独占的 CU 资源个数
+ DEC: 本 profile 独占的解码器资源个数
+ ENC: 本 profile 独占的编码器资源个数
+ CpyEng: 本 profile 独占的 copy engine 资源个数
+ JPEG: 本 profile 独占的 JPEG 处理单元个数
+ OFA: 本 profile 独占的 OFA 处理单元个数

### 10.2. 查询 GPU Instance profile 可能的创建位置
通过`-lgipp`选项可查询 GPU instance profile 可能的创建位置信息，后续可通过`-cgi`选项指定在具体的位置创建 GPU instance。

可能的创建位置显示格式为：`{start0, start1, start2}:size`，即可能多个开始位置（`start0 / start1 / start2`），每种创建位置的尺寸`size`均相同。比如下文表示可在 0 和 4 位置创建 profile，每个实例的尺寸都是 4。

```bash
{0,4}:4
```

例如执行`ppu-smi mig -i 1 -lgipp`，查询结果示例如下：

```bash
root@a475cc8d4c49:/# ppu-smi mig -i 1 -lgipp
PPU 1 profile ID 0 placements: {0,1,2,3,4,5,6,7}:1
PPU 1 profile ID 1 placements: {0,2,4,6}:2
PPU 1 profile ID 2 placements: {0,4}:4
PPU 1 profile ID 3 placements: {0,4}:4
```

### 10.3. 创建 GPU Instance 实例
通过`-cgi`选项可创建一个或者多个 GPU instance，多个 GPU instance 信息之间通过逗号`,`分隔，对于每个需要建立的 GPU instance：

1. 通过传入 GPU instance profile 的名称或者 ID，来指定使用哪个 GPU instance profile 创建 GPU instance
    1. profile 名称支持使用全名或者短名称，比如`MIG 1g12gb`，若指定名称，可指定为`MIG 1g12gb`或者`1g12gb`
2. 在 profile 信息后可通过冒号`:`指定 GPU instance 创建的开始位置
    1. 可选项，创建位置可以不指定

举例：通过指定 GPU instance profile ID 为`3`，创建一个 GPU instance，不指定创建位置

```bash
-cgi 3
```

举例：通过指定 GPU instance profile ID 分别为`0`和`1`，创建两个 GPU instance，不指定创建位置

```bash
-cgi 0,1
```

举例：通过指定 GPU instance profile ID 为`1`，创建一个 GPU instance，指定创建位置从`4`开始

```bash
-cgi 1:4
```

举例：通过指定 GPU instance profile 短名称`1g12gb`，创建一个 GPU instance，不指定创建位置

```bash
-cgi 1g12gb
```

举例：通过指定 GPU instance profile 名称`MIG 1g12gb`和`MIG 2g24gb`，创建两个 GPU instance，分别指定创建位置

```bash
-cgi "MIG 1g12gb:0,MIG 2g24gb:4"
```

用户可通过`-i`选项指定创建 GPU instance 的 PPU 设备，若不指定，则将在每个 PPU 设备上尝试创建。例如执行`ppu-smi mig -i 1 -cgi 1`，创建结果显示如下：

```bash
root@a475cc8d4c49:~# ppu-smi mig -i 1 -cgi 1
Successfully created GPU instance ID 0 on PPU 1 using profile MIG 2g24gb (Profile ID 1)
```

### 10.4. 查看 GPU Instance 信息
通过`-lgi`选项可查询已存在的 GPU instance 信息，通过`-i`选项可约束查询的设备范围，例如执行`ppu-smi mig -i 1 -lgi`，查询结果说明如下：

```bash
root@0549cf16bb85:~# ppu-smi mig -i 1 -lgi
+---------------------------------------------------------+
| GPU instances:                                          |
| PPU  Name                 Profile  Instance  Placement  |
|                             ID        ID     Start:Size |
+=========================================================+
| 1    MIG 2g12gb              1        0         0:2     |
+---------------------------------------------------------+
| 1    MIG 2g12gb              1        2         2:2     |
+---------------------------------------------------------+
```

+ PPU: 设备上电后分配的从 0 开始的枚举编号
+ Name: GPU instance 的名称
+ Profile ID: 创建本 GPU instance 时使用的 GPU instance profile 的 ID 编号
+ Instance ID：GPU instance 的 ID 编号，后续可在`-gi`选项中通过此 ID 指定对应的 GPU instance
+ Placement：本 GPU instance 创建的位置信息

### 10.5. 删除 GPU Instance 实例
通过`-dgi`选项可删除 GPU instance，通过`-i`选项可约束操作的设备范围，通过`-gi`选项可约束操作的 GPU instance 范围，`-i`和`-gi`选项可单独或者配合使用。

例如执行`ppu-smi mig -dgi -i 1 -gi 1`，删除`PPU 1`设备的`gpu instance 1`，操作示例如下：

```bash
root@0549cf16bb85:~# ppu-smi mig -dgi -i 1 -gi 1
Successfully destroyed GPU instance ID 1 from PPU 1
```

### 10.6. 复位 GPU Instance 实例
通过`-r`选项可复位 GPU instance，复位一个 GPU instance 不会影响其他 GPU instance 的运行。通过`-i`选项可约束操作的设备范围，通过`-gi`选项可约束操作的 GPU instance 范围，`-i`和`-gi`选项可单独或者配合使用。

例如执行`ppu-smi mig -i 1 -gi 0 -r`，复位`PPU 1`设备的`gpu instance 0`，操作示例如下：

```bash
root@0549cf16bb85:~# ppu-smi mig -i 1 -gi 0 -r
Successfully trigger reset of GPU instance ID 0 from PPU 1.
```

### 10.7. 查询 Compute Instance profile 信息
通过`-lcip`选项可查询 GPU instance 支持切分的 Compute instance profile 信息，通过`-i`选项可约束查询的设备范围，通过`-gi`选项可约束查询的 GPU instance 范围，`-i`和`-gi`选项可单独或者配合使用。例如执行`ppu-smi mig -lcip -i 1 -gi 0`，查询`PPU 1`上`gpu instance 0`支持切分 Compute instance 的情况，结果说明如下：

```bash
root@0549cf16bb85:~# ppu-smi mig -lcip -i 1 -gi 0
+--------------------------------------------------------------------------------------+
| Compute instance profiles:                                                           |
| PPU    GPU     Name                 Profile  Instances   Exclusive       Shared      |
|      Instance                         ID     Free/Total     CU       DEC   ENC  OFA  |
|         ID                                                          CpyEng JPEG      |
+======================================================================================+
| 1       0      MIG 1u.2g12gb           0       16/16         1         0    0    0   |
|                                                                        2    0        |
+--------------------------------------------------------------------------------------+
| 1       0      MIG 2u.2g12gb           1        8/8          2         0    0    0   |
|                                                                        2    0        |
+--------------------------------------------------------------------------------------+
| 1       0      MIG 3u.2g12gb           2        4/4          3         0    0    0   |
|                                                                        2    0        |
+--------------------------------------------------------------------------------------+
| 1       0      MIG 4u.2g12gb           3        4/4          4         0    0    0   |
|                                                                        2    0        |
+--------------------------------------------------------------------------------------+
| 1       0      MIG 8u.2g12gb           4        2/2          8         0    0    0   |
|                                                                        2    0        |
+--------------------------------------------------------------------------------------+
| 1       0      MIG 12u.2g12gb          5        1/1         12         0    0    0   |
|                                                                        2    0        |
+--------------------------------------------------------------------------------------+
| 1       0      MIG 16u.2g12gb         6*        1/1         16         1    1    0   |
|                                                                        2    1        |
+--------------------------------------------------------------------------------------+
```

+ PPU: 设备上电后分配的从 0 开始的枚举编号
+ GPU Instance ID：GPU instance 的 ID
+ Name：Compute instance profile 的名称，可通过`-cci`选项指定本 profile 名称创建 Compute instance
+ Profile ID：Compute instance profile 的 ID，可通过`-cci`选项指定本 profile 的 ID 创建 Compute instance
    - 包含`*`标记的 ID 为默认的 Compute instance profile ID，通过`-C`或者`-cci`创建默认 Compute instance 时，将创建此 profile 对应的 Compute instance
+ Instances Free/Total：本 Compute instance profile 支持建立的 Compute instance 最大个数和可用个数
+ Exclusive CU：本 Compute instance profile 创建的 Compute instance 中独占的 CU 个数
+ DEC: 本 profile 共享的解码器资源个数
+ ENC: 本 profile 共享的编码器资源个数
+ CpyEng: 本 profile 共享的 copy engine 资源个数
+ JPEG: 本 profile 共享的 JPEG 处理单元个数
+ OFA: 本 profile 共享的 OFA 处理单元个数

### 10.8. 查询 Compute Instance profile 可能的创建位置
通过`-lcipp`选项可查询 Compute instance profile 可能的创建位置信息，后续可通过`-cci`选项指定在具体的位置创建 Compute instance。

通过`-i`选项可约束操作的设备范围，通过`-gi`选项可约束操作的 GPU instance 范围，`-i`和`-gi`选项可单独或者配合使用。

可能的创建位置显示格式为：`{start0, start1, start2}:size`，即可能多个开始位置（`start0 / start1 / start2`），每种创建位置的尺寸`size`均相同。比如下文表示可在 0 和 4 位置创建 profile，每个实例的尺寸都是 4。

```bash
{0,4}:4
```

例如执行`ppu-smi mig -i 3 -gi 0 -lcipp`，查询结果示例如下：

```bash
root@0549cf16bb85:~# ppu-smi mig -i 3 -gi 0 -lcipp
PPU 3 GPU instance 0 profile ID 0 placements: {0,1,2,3,4,5,6,7}:1
PPU 3 GPU instance 0 profile ID 1 placements: {0,2,4,6}:2
PPU 3 GPU instance 0 profile ID 2 placements: {0,4}:3
PPU 3 GPU instance 0 profile ID 3 placements: {0,4}:4
PPU 3 GPU instance 0 profile ID 4 placements: {0}:8
```

### 10.9. 创建 Compute Instance 实例
通过`-cci`选项可创建一个或者多个 Compute instance，可指定对应的 Compute instance profile 的名称或者 ID，若不指定参数，则使用默认的 Compute instance profile 进行创建。多个 Compute instance 信息之间通过逗号`,`分隔，对于每个需要建立的 Compute instance：

1. 通过传入 Compute instance profile 的名称或者 ID，来指定使用哪个 Compute instance profile 创建 Compute instance
    1. profile 名称支持使用全名或者短名称，比如`MIG 1u.1g6gb`，若指定名称，可指定为`MIG 1u.1g6gb`或者`1u.1g6gb`
2. 在 profile 信息后可通过冒号`:`指定 Compute instance 创建的开始位置
    1. 可选项，创建位置可以不指定

通过`-i`选项可约束操作的设备范围，通过`-gi`选项可约束操作的 GPU instance 范围，`-i`和`-gi`选项可单独或者配合使用。

此外用户可在创建 GPU instance 时同时创建默认的 Compute instance，例如执行`ppu-smi mig -i 1 -cgi 1 -C`：

```bash
root@0549cf16bb85:~# ppu-smi mig -i 1 -cgi 1 -C
Successfully created GPU instance ID 4 on PPU 1 using profile MIG 2g12gb (Profile ID 1)
Successfully created compute instance ID 0 on PPU 1 GPU instance ID 4 using profile MIG 16u.2g12gb (Profile ID 6)
```

举例：通过指定 Compute instance profile ID 为`3`，创建一个 Compute instance

```bash
-cci 3
```

举例：通过指定 Compute instance profile ID 为`3,4`，创建两个 Compute instance

```bash
-cci 3,4
```

举例：通过指定 Compute instance profile ID 为`1`，创建一个 Compute instance，指定创建位置从`4`开始

```bash
-cci 1:4
```

举例：通过指定 Compute instance profile 短名称为`1u.2g12gb`，创建一个 Compute instance

```bash
-cci 1u.2g12gb
```

举例：通过指定 Compute instance profile 名称为`MIG 1u.2g12gb`和`MIG 2u.2g12gb`，创建两个 Compute instance

```bash
-cci "MIG 1u.2g12gb,MIG 2u.2g12gb"
```

举例：不指定 Compute instance profile 名称或者 ID，使用默认的 Compute instance profile 创建一个 Compute instance

```bash
ppu-smi mig -cci -i 1 -gi 0
```

用户可通过`-i`和`-gi`选项指定创建 Compute instance 实例的位置，若不指定，将在所有的 PPU 设备和 GPU instance 上尝试创建。例如执行`ppu-smi mig -i 1 -gi 0 -cci 3`，操作示例如下：

```bash
root@0549cf16bb85:~# ppu-smi mig -i 1 -gi 0 -cci 3
Successfully created compute instance ID 0 on PPU 1 GPU instance ID 0 using profile MIG 4u.2g12gb (Profile ID 3)
```

### 10.10. 查询 Compute Instance 信息
通过`-lci`选项可查询已存在的 Compute instance 信息，通过`-i`选项可约束查询的设备范围，通过`-gi`选项可约束查询的 GPU instance 范围，`-i`和`-gi`选项可单独或者配合使用。例如执行`ppu-smi mig -i 1 -gi 0 -lci`，查询结果说明如下：

```bash
root@0549cf16bb85:~# ppu-smi mig -i 1 -gi 0 -lci
+-------------------------------------------------------------------+
| Compute instances:                                                |
| PPU    GPU     Name                 Profile  Instance  Placement  |
|      Instance                         ID        ID     Start:Size |
|         ID                                                        |
+===================================================================+
| 1       0      MIG 4u.2g12gb           3        0         0:0     |
+-------------------------------------------------------------------+
| 1       0      MIG 8u.2g12gb           4        1         0:1     |
+-------------------------------------------------------------------+
```

+ PPU: 设备上电后分配的从 0 开始的枚举编号
+ GPU Instance ID：GPU instance 的 ID
+ Name：Compute instance 的名称
+ Profile ID：创建本 Compute instance 使用的 Compute instance profile 的 ID
+ Instance ID：本 Compute instance 的 ID，后续可通过`-ci`选项指定 Compute instance 实例
+ Placement：本 Compute instance 创建的位置信息

### 10.11. 删除 Compute Instance 实例
通过`-dci`选项可删除 Compute instance，通过`-i`选项可约束操作的设备范围，通过`-gi`选项可约束操作的 GPU instance 范围，通过`-ci`选项可约束操作的 Compute instance 范围，`-i`、`-gi`和`-ci`选项可单独或者配合使用。

例如执行`ppu-smi mig -dci -i 1 -gi 0 -ci 1`，删除`PPU 1`设备的`gpu instance 0`的`compute instance 1`，操作示例如下：

```bash
root@0549cf16bb85:~# ppu-smi mig -dci -i 1 -gi 0 -ci 1
Successfully destroyed compute instance ID 1 from PPU 1 GPU instance 0
```

平台扩展关联：MIG 多实例面向并发 serving，不符合本次比赛单卡设备、单样本、无 batch 的口径；比赛前应确认目标 810E 未被意外切分，不能用 MIG 副本制造吞吐收益。

## 11. 管理虚拟化设备 (vGPU)
PPU-SMI 支持查询设备虚拟化（vGPU）的相关信息，并支持创建 / 删除 vGPU 实例。使用 vGPU 相关功能需要用户具备管理员权限。

vGPU 相关概念介绍如下：

+ vGPU type：PPU 设备支持的 vGPU 类型信息，即此类 vGPU 的 PPU 资源切分方法，例如本 vGPU type 切分方案下每个 vGPU 实例分配的 CE 个数和内存大小等
+ vGPU instance：按照指定的 vGPU type 创建的 vGPU 实例，用户可使用 vGPU instance 创建虚拟机（VM）

vGPU instance 实例的状态说明如下：

+ active instance：指已被创建且存在 VM 与之关联的 vGPU 实例
+ alive instance：指已被创建的 vGPU 实例，包含未关联任何 VM 的 vGPU 实例

可通过执行`ppu-smi -vm VGPU`开启 PPU 设备的 vGPU 模式（详细信息参见[修改设备配置](#Kgcc3)）。可通过`vgpu`子命令查询 vGPU 相关信息，例如执行`ppu-smi vgpu -s`查看设备支持的 vGPU type 信息：

```bash
root@0549cf16bb85:~# ppu-smi vgpu -s
PPU 0: PPU (UUID: GPU-019ea108-c110-0420-0000-0000e0b7fe3c)
    vGPU Type 0: vGPU-0 (Class: MIG-Backed: 2 CE 5GB Memory 0 ICN 0 DVG 0 EVG)
    vGPU Type 1: vGPU-1 (Class: MIG-Backed: 2 CE 5GB Memory 0 ICN 1 DVG 0 EVG)
    vGPU Type 2: vGPU-2 (Class: MIG-Backed: 2 CE 5GB Memory 0 ICN 0 DVG 1 EVG)
    vGPU Type 3: vGPU-3 (Class: MIG-Backed: 2 CE 5GB Memory 1 ICN 0 DVG 0 EVG)
    vGPU Type 4: vGPU-4 (Class: MIG-Backed: 2 CE 5GB Memory 1 ICN 1 DVG 0 EVG)
    vGPU Type 5: vGPU-5 (Class: MIG-Backed: 2 CE 5GB Memory 1 ICN 0 DVG 1 EVG)
...
```

通过执行`ppu-smi vgpu -h`可查询 vGPU 相关帮助信息，每次可指定一个`vgpu`查询 / 操作子选项进行操作。可通过`-i`选项指定操作单个或多个 PPU 设备。`vgpu`子命令的所有查询功能均可通过`-l`选项指定周期输出查询结果，单位为秒，例如`-l 5`表示每 5 秒输出一次结果，直到输入`Ctrl + C`取消查询操作。

```bash
root@0549cf16bb85:~# ppu-smi vgpu -h
vgpu -- Virtual GPU management.

ppu-smi vgpu [OPTION1 [ARG1]] [OPTION2 [ARG2]] ...
    -h,   --help
        Display help information
    -i,   --id=
        Enumeration index, Serial number, PCI bus ID or UUID.
        Provide comma separated values for more than one device.
    -v,   --verbose
        Display detailed information about supported vGPU types or vGPU types that can be created.
    -l,   --loop=
        Display information at the specified time interval in seconds until Ctrl-C is pressed.
    -f,   --force
        When used with the option to delete a vGPU instance (-di),
        Delete vGPU instance regardless of VM state.

    [any one of]

    -q,   --query
        Display information about currently running vGPU instances (VM active).
    -a,   --alive
        Display information about currently alive vGPU instances.
    -s,   --supported
        Display supported vGPU types.
    -c,   --creatable
        Display the vGPU types that can currently be created.
    -ci,  --create-instance=
        Create a vGPU instance for the given vGPU type ID.
    -di,  --delete-instance=
        Delete a vGPU instance for the given vGPU instance ID.
        Use option -f to delete vGPU instance regardless of VM state.
```

### 11.1. 查询支持的 vGPU 类型
通过`-s`选项可查询 PPU 设备支持的 vGPU 类型信息（vGPU type）。通过`-i`选项可约束查询的设备范围，例如执行`ppu-smi vgpu -i 0 -s`，查询结果说明如下：

```bash
root@0549cf16bb85:~# ppu-smi vgpu -i 0 -s
PPU 0: PPU (UUID: GPU-019ea108-c110-0420-0000-0000e0b7fe3c)
    vGPU Type 0: vGPU-0 (Class: MIG-Backed: 2 CE 5GB Memory 0 ICN 0 DVG 0 EVG)
    vGPU Type 1: vGPU-1 (Class: MIG-Backed: 2 CE 5GB Memory 0 ICN 1 DVG 0 EVG)
    vGPU Type 2: vGPU-2 (Class: MIG-Backed: 2 CE 5GB Memory 0 ICN 0 DVG 1 EVG)
    vGPU Type 3: vGPU-3 (Class: MIG-Backed: 2 CE 5GB Memory 1 ICN 0 DVG 0 EVG)
    vGPU Type 4: vGPU-4 (Class: MIG-Backed: 2 CE 5GB Memory 1 ICN 1 DVG 0 EVG)
    vGPU Type 5: vGPU-5 (Class: MIG-Backed: 2 CE 5GB Memory 1 ICN 0 DVG 1 EVG)
...
```

每个 PPU 设备下的列表包含如下信息：

+ vGPU type ID
+ vGPU type 的名称
+ vGPU type 的分类详细信息

通过`-s`和`-v`选项组合，可以查询更详细的 vGPU 类型信息，例如执行`ppu-smi vgpu -i 0 -s -v`，查询结果说明如下：

```bash
root@0549cf16bb85:~# ppu-smi vgpu -i 0 -s -v
+-------------------------------------------------------------------+
| Supported vGPU types:                                             |
| PPU  Type   Name                 Instances     GPU       Memory   |
|       ID                         Free/Total  Instance     GiB     |
|                                                 ID                |
+===================================================================+
| 0      0    vGPU-0                  4/8         N/A      5.00     |
+-------------------------------------------------------------------+
| 0      1    vGPU-1                  0/1         N/A      5.00     |
+-------------------------------------------------------------------+
| 0      2    vGPU-2                  2/4         N/A      11.00    |
+-------------------------------------------------------------------+
```

+ PPU: 设备上电后分配的从 0 开始的枚举编号
+ Type ID：vGPU type 的 ID
+ Name：vGPU type 的名称
+ Instances Free/Total：当前可建立的 vGPU 实例个数 / 总共可建立的 vGPU 实例个数
+ GPU Instance ID：vGPU type 对应的 MIG GPU instance ID，`N/A`表示没有对应关系
+ Memory GiB：每个 vGPU 实例分配的内存大小

### 11.2. 查询可创建的 vGPU 类型
通过`-c`选项可查询 PPU 设备当前可创建的 vGPU 类型信息（vGPU type），通过`-i`选项可约束查询的设备范围，例如执行`ppu-smi vgpu -i 0 -c`，查询结果仅包含当前 PPU 资源允许创建的 vGPU type：

```bash
root@0549cf16bb85:~# ppu-smi vgpu -i 0 -c
PPU 0: PPU (UUID: GPU-019ea108-c110-0420-0000-0000e0b7fe3c)
    vGPU Type 0: vGPU-0 (Class: MIG-Backed: 2 CE 5GB Memory 0 ICN 0 DVG 0 EVG)
    vGPU Type 3: vGPU-3 (Class: MIG-Backed: 2 CE 5GB Memory 1 ICN 0 DVG 0 EVG)
...
```

每个 PPU 设备下的列表包含如下信息：

+ vGPU type ID
+ vGPU type 的名称
+ vGPU type 的分类详细信息

通过`-c`和`-v`选项组合，可以查询更详细的允许创建的 vGPU 类型信息，例如执行`ppu-smi vgpu -i 0 -c -v`，查询结果说明如下：

```bash
root@0549cf16bb85:~# ppu-smi vgpu -i 0 -c -v
+-------------------------------------------------------------------+
| Supported vGPU types:                                             |
| PPU  Type   Name                 Instances     GPU       Memory   |
|       ID                         Free/Total  Instance     GiB     |
|                                                 ID                |
+===================================================================+
| 0      0    vGPU-0                  4/8         N/A      5.00     |
+-------------------------------------------------------------------+
| 0      2    vGPU-2                  2/4         N/A      11.00    |
+-------------------------------------------------------------------+
```

+ PPU: 设备上电后分配的从 0 开始的枚举编号
+ Type ID：vGPU type 的 ID
+ Name：vGPU type 的名称
+ Instances Free/Total：当前可建立的 vGPU 实例个数 / 总共可建立的 vGPU 实例个数
+ GPU Instance ID：vGPU type 对应的 MIG GPU instance ID，`N/A`表示没有对应关系
+ Memory GiB：每个 vGPU 实例分配的内存大小

### 11.3. 创建 vGPU Instance 实例
通过`-ci`选项可指定一个 vGPU type 类型，创建对应类型的 vGPU instance 实例。

通过`-i`选项可约束操作的设备范围，例如执行`ppu-smi vgpu -i 0 -ci 0`，在 PPU 设备 0 上创建 vGPU 类型 ID 为 0 的一个 vGPU 实例，操作示例如下：

```bash
root@0549cf16bb85:~# ppu-smi vgpu -ci 0 -i 0
Successfully created vGPU instance 0 (PCI Bus ID 00000000:5E:00.0) on PPU 0 using vGPU type 0.
```

### 11.4. 查询已创建的 vGPU Instance 信息
通过`-a`选项可查询已创建（状态为`alive`）的 vGPU instance 的信息，通过`-i`选项可约束查询的设备范围，例如执行`ppu-smi vgpu -i 0 -a`，查询结果说明如下：

```bash
root@0549cf16bb85:~# ppu-smi vgpu -i 0 -a
PPU 00000000:10:00.0
    Alive vGPUs                             : 2
    vGPU Instance 1
        vGPU Instance ID                    : 1
        vGPU Name                           : vGPU-10
        vGPU Type                           : 10
        vGPU UUID                           : VGPU-3f53d39f-ce6e-dc78-c3d4-4c18653c19c0
        vGPU PCI Bus ID                     : 00000000:10:01.0
        MDEV UUID                           : N/A
        GPU Instance ID                     : N/A
        ECC Mode                            : Enabled
        Memory Size                         : 28672 MiB
    vGPU Instance 5
        vGPU Instance ID                    : 5
        vGPU Name                           : vGPU-1
        vGPU Type                           : 1
        vGPU UUID                           : VGPU-3f53d39f-ce6e-dc78-c3d4-4c18653c19c1
        vGPU PCI Bus ID                     : 00000000:10:01.4
        MDEV UUID                           : N/A
        GPU Instance ID                     : N/A
        ECC Mode                            : Enabled
        Memory Size                         : 7168 MiB
```

对于每个 PPU 设备：

+ Alive vGPUs: 当前 PPU 设备已创建的 vGPU 实例个数

对于每个 vGPU 实例：

+ vGPU Instance ID: vGPU 实例的 ID，后续可通过`-di`选项指定此 ID，删除对应 vGPU 实例
+ vGPU Name：本 vGPU 实例的名称
+ vGPU Type：对应 vGPU 类型的 ID
+ vGPU UUID：vGPU 实例的 UUID
+ vGPU PCI Bus ID：vGPU 实例的 PCI Bus ID，即`Bus:Device.Function`信息
+ MDEV UUID：vGPU 实例对应的 MIG device 的 UUID，`N/A`表示没有对应关系
+ GPU Instance ID：vGPU 实例对应的 MIG GPU instance ID，`N/A`表示没有对应关系
+ ECC Mode：vGPU 实例的 ECC 工作模式
+ Memory Size：vGPU 实例分配的内存总量

### 11.5. 查询已关联 VM 的 vGPU Instance 信息
通过`-q`选项可查询已关联 VM（状态为`active`）的 vGPU instance 的信息，通过`-i`选项可约束查询的设备范围，例如执行`ppu-smi vgpu -i 0 -q`，查询结果说明如下：

```bash
root@0549cf16bb85:~# ppu-smi vgpu -i 0 -q
PPU 00000000:10:00.0
    Active vGPUs                            : 1
    vGPU Instance 1
        vGPU Instance ID                    : 1
        VM UUID                             : ee7b7a4b-388a-4357-a425-5318b2c65b30
        vGPU Name                           : vGPU-10
        vGPU Type                           : 10
        vGPU UUID                           : VGPU-3f53d39f-ce6e-dc78-c3d4-4c18653c19c0
        vGPU PCI Bus ID                     : 00000000:10:01.0
        MDEV UUID                           : N/A
        Guest Driver Version                : 0.8.0
        GPU Instance ID                     : N/A
        ECC Mode                            : Enabled
        Memory Usage
            Total                           : 28672 MiB
            Used                            : 3 MiB
            Free                            : 28669 MiB
```

对于每个 PPU 设备：

+ Active vGPUs: 当前 PPU 设备已创建且关联 VM 的 vGPU 实例个数

对于每个 vGPU 实例：

+ vGPU Instance ID: vGPU 实例的 ID，后续可通过`-di`选项指定此 ID，删除对应 vGPU 实例
+ VM UUID：VM 虚拟机的 UUID
+ VM Domain ID：VM 虚拟机的 domain ID
+ vGPU Name：本 vGPU 实例的名称
+ vGPU Type：对应 vGPU 类型的 ID
+ vGPU UUID：vGPU 实例的 UUID
+ vGPU PCI Bus ID：vGPU 实例的 PCI Bus ID，即`Bus:Device.Function`信息
+ MDEV UUID：vGPU 实例对应的 MIG device 的 UUID，`N/A`表示没有对应关系
+ Guest Driver Version：VM 虚拟机内的驱动版本
+ GPU Instance ID：vGPU 实例对应的 MIG GPU instance ID，`N/A`表示没有对应关系
+ ECC Mode：vGPU 实例的 ECC 工作模式
+ Memory Usage：vGPU 实例的内存使用情况
    - Total：vGPU 实例分配的内存总量
    - Used：vGPU 实例已使用内存量
    - Free：vGPU 实例剩余可用内存量

### 11.6. 删除 vGPU Instance 实例
通过`-di`选项可指定一个指定 vGPU instance ID，删除此 ID 对应的 vGPU instance 实例。通过`-i`选项可约束操作的设备范围，默认不允许删除正在被 VM 使用的 vGPU instance，可通过`-f`强制删除正在使用的 vGPU instance。例如执行`ppu-smi vgpu -i 0 -di 1`，在 PPU 设备 0 上创建 vGPU 类型 ID 为 1 的一个 vGPU 实例，操作示例如下：

```bash
root@0549cf16bb85:~# ppu-smi vgpu -i 0 -di 1
Successfully deleted vGPU instance 9 from PPU 0.
```

## 12. 隔离 PPU 设备 (drain)
PPU-SMI 支持设置和查询 PPU 设备的隔离状态（drain state），以支持当某个 PPU 设备出现故障时，将此 PPU 设备屏蔽和隔离。对于被隔离（drain）的 PPU 设备介绍如下：

+ PPU 设备正在执行的任务将不受影响
+ PPU 设备不会接受新的计算任务
+ PPU 设备在 PPU-SMI 和 PPUDBG 等工具中不可见

例如执行`ppu-smi drain -p 0001:AA:00.0 -m 1`将 PCI bus ID 为`0001:AA:00.0`的 PPU 设备设置为隔离状态：`draining`：

```bash
root@dfc623e46a90:~# ppu-smi drain -p 0001:AA:00.0 -m 1
Successfully set PPU 0001:AA:00.0 drain state to: draining.
```

通过执行`ppu-smi drain -h`可查看 drain 功能帮助信息，相关功能需要通过`-p`传入 PPU 的 PCI bus ID 以指定对应 PPU 设备：

```bash
root@dfc623e46a90:~# ppu-smi drain -h
drain -- Displays/modifies PPU drain states for power idling.

ppu-smi drain [OPTION1 [ARG1]] [OPTION2 [ARG2]] ...
    -h,   --help
        Display help information
    -p,   --pciid=
        PPU PCI ID in the format XXXX:YY:Z.a
            XXXX = domain
            YY   = bus
            Z    = device
            a    = function

    [any one of]

    -m,   --modify=
        Modify the drain state of a PPU specified by -p.
            0 = not draining
            1 = draining
    -q,   --query
        Query the drain state of a PPU specified by -p.
```

### 12.1. 设置隔离状态
使用`-m`选项可设置或者取消 PPU 设备的隔离状态（drain state），通过`-p`传入 PPU 的 PCI bus ID 以指定对应 PPU 设备。例如执行`ppu-smi drain -p 0001:AA:00.0 -m 1`将 PPU 进行隔离，操作结果示例如下：

```bash
root@dfc623e46a90:~# ppu-smi drain -p 0001:AA:00.0 -m 1
Successfully set PPU 0001:AA:00.0 drain state to: draining.
```

> **提示：** 由于被隔离的 PPU 设备在 PPU-SMI 等工具中不可见，若需要查询相关 PPU 设备的 PCI bus ID 信息，可通过`lspci`工具进行查询，例如执行：`lspci | grep 6001` 查询和过滤显示所有 PPU 设备。

### 12.2. 查询隔离状态
使用`-q`选项可查询 PPU 设备的隔离状态（drain state），通过`-p`传入 PPU 的 PCI bus ID 以指定对应 PPU 设备。例如执行`ppu-smi drain -p 0001:AA:00.0 -q`查询隔离状态，结果示例如下：

```bash
root@dfc623e46a90:~# ppu-smi drain -p 0001:AA:00.0 -q
The current drain state of PPU 0000:12:1.0 is: draining.
```

### 12.3. 移除 PPU 设备
使用`-r`选项可移除已经处于隔离状态（draining state）的 PPU 设备，通过`-p`传入 PPU 的 PCI bus ID 以指定对应 PPU 设备。设备需要先处于隔离状态（draining state），才能通过此选项进行移除，例如执行`ppu-smi drain -p 0001:AA:00.0 -r`移除设备，结果示例如下：

```bash
root@dfc623e46a90:~# ppu-smi drain -p 0001:AA:00.0 -r
Successfully remove 0001:AA:00.0.
```

### 12.4. 发现 PPU 设备
使用`-d`选项可触发驱动发现之前通过`-r`选项被移除的 PPU 设备，执行此操作将会尝试发现并初始化所有之前被移除的设备。例如执行`ppu-smi drain -d`移除设备，结果示例如下：

```bash
root@dfc623e46a90:~# ppu-smi drain -d
Discovery completed successfully. Any discovered PPUs will now appear in the enumeration list and device count.
```

## 13. 管理性能监控功能 (gpm)
PPU-SMI 支持设置和查询`性能监控（GPM）`的使能状态，`性能监控（GPM）`功能使能时将会使用 PPU 设备 performance counter 采集数据，其他使用 PPU 设备 performance counter 功能的应用将无法运行。可通过 PPU-SMI 查询`性能监控（GPM）`功能的使能状态，以及暂停`性能监控（GPM）`功能以使用其他应用采集 performance counter 数据，并在使用完成后恢复`性能监控（GPM）`功能。

例如执行`ppu-smi gpm --get-stream-state`查询 PPU 设备的`性能监控（GPM）`功能是否被暂停的状态：

```bash
root@dfc623e46a90:~# ppu-smi gpm --get-stream-state
PPU 0 GPM stream state: Enabled.
PPU 1 GPM stream state: Disabled.
```

通过执行`ppu-smi gpm -h`可查看 drain 功能帮助信息，可通过`-i`选项指定单个或多个 PPU 设备，多个设备 ID 通过逗号`,`分隔。

```bash
root@dfc623e46a90:~# ppu-smi gpm -h
gpm -- GPU Performance Monitoring management.

ppu-smi gpm [OPTION1 [ARG1]] [OPTION2 [ARG2]] ...
    -h,   --help
        Display help information
    -i,   --id=
        Enumeration index, Serial number, PCI bus ID or UUID.
        Provide comma separated values for more than one device.

    [any one of]

    -s,   --set-stream-state=
        Set GPU Performance Monitoring Stream State:
        0/DISABLED, 1/ENABLED
    -g,   --get-stream-state
        Get GPU Performance Monitoring Stream State
    --get-sample-state
        Get GPU Performance Monitoring Sample State
```

### 13.1. 设置性能监控输出状态
使用`-s`选项可使能或者禁止`性能监控（GPM）`功能的输出状态开关，当`性能监控（GPM）`功能被禁止时：

+ 订阅`性能监控（GPM）`数据的应用获取的性能结果为`N/A`
+ `性能监控（GPM）`功能不再使用 PPU 设备的 performance counter

例如执行`ppu-smi gpm -s DISABLED -i 0`暂停`PPU 0`设备的`性能监控（GPM）`的输出：

```bash
root@dfc623e46a90:~# ppu-smi gpm -s DISABLED -i 0
Set GPM stream state to DISABLED for PPU 00000000:5E:00.0.
```

> **提示：**
>
> + 通过使用`-s`选项暂时禁止`性能监控（GPM）`功能可以让其他使用 PPU 设备 performance counter 的应用（如`Asight`）可正常采集 PPU 性能数据。
> + 应用通过其他方式采集 performance counter 数据（非`性能监控（GPM）`方式）的采集行为，不受此选项控制。

### 13.2. 查询性能监控输出状态
使用`-g`选项可查询`性能监控（GPM）`功能的输出状态开关，通过`-i`选项可约束查询的设备范围。例如执行`ppu-smi gpm -g -i 0`查询`PPU 0`设备的`性能监控（GPM）`输出状态：

```bash
root@dfc623e46a90:~# ppu-smi gpm -g -i 0
PPU 0 GPM stream state: Disabled.
```

> **提示：**
>
> + `性能监控（GPM）`输出状态开关查询为使能时，可使用`--get-sample-state`选项查询`性能监控（GPM）`的采集状态，确认存在应用通过`性能监控（GPM）`采集性能指标，并占用 PPU 设备 performance counter 资源。
> + 可通过`ppu-smi -q`查询 PPU 设备 performance counter 是否正在使能。

### 13.3. 查询性能监控采集状态
使用`--get-sample-state`选项可查询`性能监控（GPM）`功能的采集状态，即是否存在应用使用`性能监控（GPM）`采集性能指标。例如执行`ppu-smi gpm --get-sample-state`查询所有 PPU 设备的`性能监控（GPM）`功能的采集状态：

```bash
root@dfc623e46a90:~# ppu-smi gpm --get-sample-state
PPU 0 GPM sample state: Enabled.
PPU 1 GPM sample state: Disabled.
```

## 14. 已知问题

+ `ppu-smi -q -d UTILIZATION`中，和采样相关信息暂不支持
+ `stats`子命令中，和采样相关信息暂不支持
+ `ppu-smi icn -gt d`查询 ICN 链路负载数据吞吐量暂不支持
+ `ppu-smi icn -gt r`查询 ICN 链路数据量低于实际值
+ 因温度或者功耗限制而降频的比例统计信息暂不支持
+ PCIe replay counter 和 error counter 相关信息查询暂不支持

## 15. Release Notes

### 15.1. 新增改动
- 增加支持指定设备组件复位的描述
- 增加查询 PCI class code、addressing mode、Fabric 信息、Compute Capability、EGM 能力的描述
- 增加 `drain` 子命令支持 `discover` 和 `remove` 选项的描述

## 16. MPS 多进程服务

T-Head SAIL（以下简称 SAIL）MPS (Multi Process Service) 提供了一种轻量级的用户态共享 PPU 的方案，通过利用硬件设计中的多管道并行提交任务特性，在单个任务对算力要求不高的推理场景下可以有效提升整体的吞吐率和计算单元利用率。

### 16.1. MPS 开关

MPS 模式默认处于关闭状态，用户可通过 ppu-smi 命令来开启/关闭/查询 MPS 模式，用法如下：

+ 开启 MPS

```bash
ppu-smi -mps 1 (对系统中所有PPU设备开启MPS)
ppu-smi -i x -mps 1 (对系统中PPU x单个设备开启MPS，x取值范围从0到设备数-1)
```

+ 关闭 MPS

```bash
ppu-smi -mps 0 (对系统中所有PPU设备关闭MPS)
ppu-smi -i x -mps 0 (对系统中PPU x单个设备关闭MPS，x取值范围从0到设备数-1)
```

+ 查询 MPS

```bash
ppu-smi --query-ppu=mps_mode --format=csv
```

> **注意：**
>
> 开启/关闭 MPS 模式需确保 PPU 设备无进程使用，否则切换会失败。
>
> MPS 模式下不支持 ICN（Inter-Chip Network，芯片间互联网络）多卡互联功能。
>
> PPU MPS 实现无 daemon server 进程，所以开启之后不会在系统中观察到 daemon server。

### 16.2. MPS 配置

**真武 810/ 真武 805 / 真武 610 / 真武 810E / 真武 610E 产品：**

MPS 模式开启成功之后，用户可通过环境变量 `UMD_MPS_ACTIVE_CE_COUNT`（UMD：User Mode Driver，用户态驱动；CE：Compute Engine，计算引擎）来控制每一个 MPS client 需要的计算单元数量，最小为 1，最大为 16，该值越小代表每一个 MPS client 能够使用的算力资源越小，所以建议用户根据实际业务需求配置合适的值，推荐配置为 2/4/8。

**真武 M890 产品：**

MPS 模式开启成功之后，用户可通过环境变量 `UMD_MPS_ACTIVE_CE_COUNT` 或 `UMD_MPS_ACTIVE_CU_COUNT`（CU：Compute Unit，计算单元；推荐使用，粒度更细）来控制每一个 MPS client 需要的计算单元数量，该值越小代表每一个 MPS client 能够使用的算力资源越小，所以建议用户根据实际业务需求配置合适的值。

### 16.3. MPS 用法

根据用法不同，MPS 又可以大致分为多进程和单进程多 context 两种用法，用户可以根据实际需求灵活选择。

+ **多进程用法**

用户启动多个进程，每个进程可视为一个 MPS client，单张卡上用户最多可启动 7 个进程，超出此数量后驱动会报错，优点是用户无需修改自己的应用代码即可使用。

+ **单进程多 context 用法**

用户可以在一个进程内通过使用 `hgCtxCreate` API 来创建多个 HGGC context 使用，每一个 HGGC context 可以看作是一个 MPS client，单张卡上用户最多能够创建的 context 数量和 `UMD_MPS_ACTIVE_CE_COUNT` 或 `UMD_MPS_ACTIVE_CU_COUNT` 配置有关，目前最大数量为 18 个，超出此数量后驱动会报错。

平台扩展关联：MPS 用于多 client 并发，不符合本次比赛“单卡、单样本、不启用 batch”的性能口径，因此不能用于成绩优化。比赛只使用本节的设备状态查询和锁频能力；MPS/ICN 互斥约束保留作通用平台知识。
