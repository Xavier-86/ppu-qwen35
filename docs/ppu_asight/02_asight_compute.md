# Asight Compute 参考手册 <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [1. 概述](#1-概述)
- [2. 安装指南](#2-安装指南)
  - [2.1. 获取 acu 命令行工具](#21-获取-acu-命令行工具)
  - [2.2. 获取 Asight Compute GUI 工具](#22-获取-asight-compute-gui-工具)
- [3. 快速入门](#3-快速入门)
  - [3.1. 采集性能数据](#31-采集性能数据)
  - [3.2. 分析报告](#32-分析报告)
  - [3.3. 下一步](#33-下一步)
- [4. acu 命令行采集](#4-acu-命令行采集)
  - [4.1. 采集性能数据](#41-采集性能数据)
  - [4.2. 控制采集过程](#42-控制采集过程)
  - [4.3. Warp Sampling](#43-warp-sampling)
  - [4.4. 指令统计](#44-指令统计)
- [5. Asight Compute GUI 分析](#5-asight-compute-gui-分析)
  - [5.1. Details Page](#51-details-page)
  - [5.2. Source Page](#52-source-page)
  - [5.3. Raw Page](#53-raw-page)
  - [5.4. Summary Page](#54-summary-page)
  - [5.5. Session Page](#55-session-page)
  - [5.6. Kernel Filter](#56-kernel-filter)
  - [5.7. Baseline](#57-baseline)
  - [5.8. Occupancy Calculator Page](#58-occupancy-calculator-page)
  - [5.9. Metric Details Panel](#59-metric-details-panel)
- [6. 命令生成助手](#6-命令生成助手)
  - [6.1. 命令生成助手菜单栏](#61-命令生成助手菜单栏)
  - [6.2. 参数配置区](#62-参数配置区)
  - [6.3. 命令行生成区](#63-命令行生成区)
- [7. Rule 系统](#7-rule-系统)
  - [7.1. 管理 Rule 文件](#71-管理-rule-文件)
  - [7.2. 内置 Rule](#72-内置-rule)
  - [7.3. 编写自定义 Rule](#73-编写自定义-rule)
- [8. 常见问题](#8-常见问题)
  - [8.1. 减少测试环境差异](#81-减少测试环境差异)
  - [8.2. 目标应用已经结束，但 acu 没有收到目标应用退出消息而卡死](#82-目标应用已经结束但-acu-没有收到目标应用退出消息而卡死)
  - [8.3. 报错：Device is not ready for profiling](#83-报错device-is-not-ready-for-profiling)
  - [8.4. LLC 向 DRAM 写入数据偏少](#84-llc-向-dram-写入数据偏少)
- [9. 已知问题](#9-已知问题)
- [10. 版本说明](#10-版本说明)
  - [10.1. 新增改动](#101-新增改动)


## 1. 概述
Asight Compute 是一款用于 **PPU 程序 Kernel 性能分析** 的工具套件。

它能够在 Kernel 执行期间采集硬件性能指标（Metrics），并通过可视化方式展示分析结果，从而帮助开发者定位性能瓶颈并优化 Kernel 性能。

Asight Compute 包含以下两个工具：

+ **acu（Asight Compute CLI）**  
    命令行工具，用于在目标系统（Target）上采集 Kernel 的性能指标并生成分析报告。
    该工具运行在 **Linux** 平台。

+ **Asight Compute GUI**  
    图形化分析工具，用于加载并分析 acu 生成的报告。支持 **Windows** 和 **Mac** 平台（Host 端）。

    Asight Compute GUI 提供多种可视化视图用于展示性能数据，如 Roofline Chart、Bar Chart、Memory Table 等，同时支持 **Baseline 对比分析**，可用于比较不同 Kernel 或不同运行之间的性能差异。

> **注意：** **Target**（目标系统）是运行被分析程序的 Linux 服务器，acu 命令行工具在此执行数据采集。
> **Host**（主机）是运行 Asight Compute GUI 的本地计算机（Windows / Mac），用于查看和分析报告。

Asight Compute 工具的典型使用流程为：

1. 在 Target 端使用 **acu** 对目标应用程序进行 profiling，生成报告文件（`.acurep`）。
2. 将报告文件拷贝到 Host 端。
3. 用 **Asight Compute GUI** 打开报告文件并分析 Kernel 性能数据。


**比赛关联：** Asight Compute 是比赛中 kernel 级算子调优的核心取证工具——对 VLM 推理中的 GEMM、Attention 等关键 kernel 采集硬件计数器，可定量判断算子是计算受限还是访存受限，为量化、融合、tiling 等优化提供依据和前后对比证据。

<a id="安装指南"></a>

## 2. 安装指南

### 2.1. 获取 acu 命令行工具

#### 2.1.1. 配置环境变量

acu 命令行工具包含在 T-Head SAIL SDK 中，获取 SDK 请参见SDK 使用指南。安装完成后，进入 SDK 目录，执行以下命令配置所需环境变量：

```bash
source envsetup.sh
```

#### 2.1.2. 检查运行环境

环境变量配置完成后，执行以下命令查看当前安装的 acu 版本信息：

```bash
acu -v
```

### 2.2. 获取 Asight Compute GUI 工具

Asight Compute GUI 工具安装包单独发布，支持以下操作系统：

+ Windows 10 / Windows 11
+ macOS 10.15 及以上版本

请前往下载页面获取安装包，根据操作系统选择对应的格式：

+ Windows 系统请选择 `.msi` 安装包
+ macOS 系统请选择 `.dmg` 安装包

## 3. 快速入门

本文将引导您快速完成一次完整的 Kernel 性能分析流程：从采集数据到查看报告。

在本文中，将运行 PPU 程序的设备称为 **目标机（Target）**，将查看报告的设备称为 **主机（Host）**。

Asight Compute 的基本使用流程如下：

1. 在 **目标机（Target）** 上使用 **acu 命令行工具**采集性能数据并生成报告。
2. 在 **主机（Host）** 上使用 **Asight Compute GUI** 打开报告并进行性能分析。

**前提条件：**

+ 目标机已配备 PPU 设备，且驱动已正确安装。
+ 目标机已安装 acu 命令行工具。如尚未安装，请参见 [安装指南](#安装指南)。
+ 主机已安装 Asight Compute GUI 工具。

### 3.1. 采集性能数据

在目标机上使用 **acu** 命令行工具启动目标应用程序，并在应用程序运行期间采集性能数据。应用程序结束后，acu 会自动输出 profiling 报告文件。

命令格式：

```bash
acu [options] <application> [application args]
```

以下示例演示如何采集目标程序中所有 Kernel 启动的性能数据：

```bash
acu -o test_report -f python test_linear.py
```

参数说明：

| 参数 | 说明 |
| --- | --- |
| `-o test_report` | 指定输出报告名称（无需指定文件后缀名） |
| `-f` | 强制覆盖已存在的报告文件 |
| `python test_linear.py` | 要进行性能分析的目标应用程序 |

应用程序运行结束后，acu 会生成对应的报告文件：`test_report.acurep`。

> **注意：** 如果 acu 运行时报错：`device is not ready for profiling`，请参考 [报错：device is not ready for profiling](#J5Ul3) 处理。

acu 还提供了多种高级选项，用于精细控制采集范围和内容：

+ **过滤 Kernel**：通过 `-c`、`-s`、`-k` 等选项按启动次数或名称过滤采集的 Kernel。详见：[过滤 Kernel](#NjM0a)
+ **指定采集指标**：通过 `--set`、`--section`、`--metrics` 等选项指定采集的性能指标集合。详见：[指定采集的 Metrics 集合](#Uu8pH)
+ **Replay 模式**：当采集的 Metrics 超过硬件计数器限制时，acu 会自动通过多次执行应用获取完整数据。详见：[Replay 模式](#UziBy)
+ **终端输出**：不指定 `-o` 时，acu 默认在终端输出 `details` 页面。可通过 `--page=<Page>` 指定输出页面，当前支持：`details`、`raw`

### 3.2. 分析报告

acu 生成的报告文件使用 `.acurep` 作为文件后缀。报告文件是独立的，可以从目标机拷贝到主机上，使用 Asight Compute GUI 打开并查看分析结果。

Asight Compute GUI 支持以下方式打开报告：

+ 主菜单打开：File -> Open...
+ 将文件拖拽（Drag & Drop）到 Asight Compute GUI 主窗口
+ 右键菜单打开：在 Project Explorer 空白区域点击右键 -> Open...
+ 通过命令行打开：`acu-ui report.acurep`

> **注意：** + 用于查看报告的 Asight Compute GUI 版本不应低于生成报告时使用的 acu 工具版本。
> + 如果使用较旧版本的 GUI 打开新版本工具生成的报告，GUI 会给出相应提示。

有关 GUI 的更多功能和使用说明，请参见 [Asight Compute GUI 工具](#XOXk5)。

### 3.3. 下一步

完成上述流程后，您已经掌握了 Asight Compute 的基本使用方法。如需了解更多高级功能，请参阅以下文档：

+ [使用指南](#acu-命令行采集) — 详细介绍 acu 命令行工具与 GUI 的各项功能
+ [常见问题](#常见问题) — 使用过程中的高频问题与解决方案

<a id="acu-命令行采集"></a>

## 4. acu 命令行采集

Asight Compute 提供了命令行工具 Asight Compute CLI（下面简称 acu），可以在不使用 GUI 工具的情况下对目标应用进行性能分析，并输出报告文件。此报告可以拷贝到 Host 端，后续由 GUI 工具进行解析展示。

**acu 主要功能：**

+ 支持采集应用在 PPU 上执行时的性能数据，并汇总为各项指标（metric）输出，如：
    - 理论峰值相关指标
    - 计算工作负载
    - 内存工作负载
    - Warp 调度器统计
    - Warp 运行状态和指令 Stall 原因统计
    - 指令统计
    - ICN 链路相关指标
+ 支持以 set、section、metric 三种粒度指定采集的 metric 集合
+ 当需要采集的 metric 列表超过 PPU 设备能力时，支持自动 replay 应用程序以获取所有性能数据
    - 支持 Application Replay 模式
    - 支持 Kernel Replay 模式
    - 支持 Range Replay 模式
    - 支持 Application Range Replay 模式
+ 支持指定性能数据采集范围，并支持多种 Kernel 过滤方式
    - 可指定采集的 PPU 设备
    - 可指定采集的 Context ID 和 Stream ID
    - 可指定采集的 Kernel 名称
    - 可通过 `cudaProfilerStart/Stop()`、`hggcProfilerStart/Stop()` 指定采集范围
    - 指定采集 Kernel 的个数
    - 指定跳过 Kernel 的个数
+ 支持 Warp Sampling

### 4.1. 采集性能数据

#### 4.1.1. 查看支持的 Metric

可通过指定 metric 集合，来指定性能数据的采集范围。指定 metric 集合可以通过三种粒度：

+ **metric**  
    衡量 PPU 某方面性能的一个指标，是 acu 可指定采集范围的最小粒度

+ **section**  
    由多个逻辑相关的 metrics 组成，acu 内置了多种 section，也可通过创建/修改一个 `section 文件` 来自定义 section

+ **set**  
    由一个或多个 section 组成，是 acu 可指定采集范围的最大粒度

##### 4.1.1.1. 查询 Metric Set 信息
可通过`--list-sets`命令行选项，查看当前 acu 支持的 metrics set 的详细信息，显示的表格说明如下：

```bash
root@d29fb2dd227a:/# acu --list-sets
 ------------ ----------------------------------------------------------------------------- --------- ------------------- 
  Identifier   Sections                                                                      Enabled   Estimated Metrics  
 ------------ ----------------------------------------------------------------------------- --------- ------------------- 
  default      Occupancy,MemoryWorkloadAnalysis,SpeedOfLight,SpeedOfLight_TensorRooflineC-   yes       314                
               hart,ComputeWorkloadAnalysis,SpeedOfLight_RooflineChart,LaunchStats               
                                                                                                                            
  detailed     MemoryWorkloadAnalysis_Tables,SchedulerStats,Occupancy,SourceCounters,Memo-   no        520                
               ryWorkloadAnalysis,SpeedOfLight,WarpStateStats,SpeedOfLight_TensorRoofline-    
               Chart,InstructionStats,ComputeWorkloadAnalysis,SpeedOfLight_RooflineChart,-                                
               LaunchStats  
               
  full         Icnlink_Tables,MemoryWorkloadAnalysis_Tables,InternalDebug,SchedulerStats,-   no        821                
               Occupancy,Icnlink_Topology,SourceCounters,MemoryWorkloadAnalysis,Professio- 
               nal,SpeedOfLight,WarpStateStats,SpeedOfLight_TensorRooflineChart,MemoryWor-                                
               kloadAnalysis_Chart,InstructionStats,ComputeWorkloadAnalysis,SpeedOfLight_-                                
               RooflineChart,LaunchStats,Icnlink 
                                                                                                                                         
  systems      Systems                                                                       no        0   
```

+ `Identifier列`: metrics set 的名称，此名称可作为`--set`选项的参数来指定采集哪个 set
+ `Sections列`：set 包含的 section 列表，可通过查看 section 列表，以确定此 set 是否满足采集需求
+ `Enabled列`: set 是否被使能，默认使能 default set
+ `Estimated Metrics列`: set 内包含的 metrics 个数，个数可用来评估采集引入的 overhead 的相对大小

> **注意：** set 的详细信息在不同的版本，可能会有差异，以实际查询到结果为准

##### 4.1.1.2. 查询 Metric Section 信息
可通过`--list-sections`命令行选项，查看支持的 section 列表，section 在 GUI 中显示的名称，以及 section 文件的预置路径，默认显示`default set`包含的 section 信息。显示的表格说明如下：

```bash
root@d29fb2dd227a:/# acu --list-sections
 ---------------------------------- ------------------------------------------------- --------- --------------------------------------------------
  Identifier                         Display Name                                      Enabled   FileName
 ---------------------------------- ------------------------------------------------- --------- --------------------------------------------------
  InstructionStats                   Instruction Statistics                            no        /usr/sections/InstructionStatistics.section
  MemoryWorkloadAnalysis             Memory Workload Analysis                          yes       /usr/sections/MemoryWorkloadAnalysis.section
  MemoryWorkloadAnalysis_Chart       Memory Workload Analysis Chart                    no        /usr/sections/MemoryWorkloadAnalysis_Chart.sect-
                                                                                                 ion
  MemoryWorkloadAnalysis_Tables      Memory Workload Analysis Tables                   no        /usr/sections/MemoryWorkloadAnalysis_Tables.sec-
                                                                                                 tion
  SchedulerStats                     Scheduler Statistics                              no        /usr/sections/SchedulerStatistics.section
  SpeedOfLight_RooflineChart         PPU Speed Of Light Roofline Chart                 yes       /usr/sections/SpeedOfLight_RooflineChart.section
  SpeedOfLight_TensorRooflineChart   PPU Speed Of Light Roofline Chart (Tensor Cell)   yes       /usr/sections/SpeedOfLight_TensorRooflineChart.-
                                                                                                 section
  ComputeWorkloadAnalysis            PPU Compute Workload Analysis                     yes       /usr/sections/ComputeWorkloadAnalysis.section
  Icnlink                            ICNLink                                           no        /usr/sections/Icnlink.section
  InternalDebug                      Debug PPU All Metrics                             no        /usr/sections/InternalDebug.section
  SpeedOfLight                       PPU Speed Of Light Throughput                     yes       /usr/sections/SpeedOfLight.section
  WarpStateStats                     Warp State Statistics                             no        /usr/sections/WarpStateStatistics.section

```

+ `Identifier列`: metrics section 的名称，后续可通过`--section`选项指定此名称以指定采集范围
+ `Display Name列`：本 section 在`Asight Compute`中显示的名称
+ `Enabled列`: 本 section 是否被使能
+ `FileName列`: 本 section 对应的`section文件`存放路径

> **注意：** section 的详细信息在不同的版本，可能会有差异，以实际查询到结果为准

另外，也可通过`--set`选项查看指定 set 的 section 信息，`Enabled列`的值为`yes`表示该 section 在指定的 set 中可用：

```bash
root@eb8b441561f7:~# acu --set=full --list-sections
 ---------------------------------- ------------------------------------------------- --------- --------------------------------------------------
  Identifier                         Display Name                                      Enabled   FileName
 ---------------------------------- ------------------------------------------------- --------- --------------------------------------------------
  InstructionStats                   Instruction Statistics                            yes       /usr/sections/InstructionStatistics.section
  MemoryWorkloadAnalysis_Chart       Memory Workload Analysis Chart                    yes       /usr/sections/MemoryWorkloadAnalysis_Chart.sect-
                                                                                                 ion
  MemoryWorkloadAnalysis_Tables      Memory Workload Analysis Tables                   yes       /usr/sections/MemoryWorkloadAnalysis_Tables.sec-
                                                                                                 tion
  ComputeWorkloadAnalysis            PPU Compute Workload Analysis                     yes       /usr/sections/ComputeWorkloadAnalysis.section
  Icnlink                            ICNLink                                           no        /usr/sections/Icnlink.section
  InternalDebug                      Debug PPU All Metrics                             yes       /usr/sections/InternalDebug.section
  MemoryWorkloadAnalysis             Memory Workload Analysis                          yes       /usr/sections/MemoryWorkloadAnalysis.section
  SchedulerStats                     Scheduler Statistics                              yes       /usr/sections/SchedulerStatistics.section
  SpeedOfLight                       PPU Speed Of Light Throughput                     yes       /usr/sections/SpeedOfLight.section
  SpeedOfLight_RooflineChart         PPU Speed Of Light Roofline Chart                 yes       /usr/sections/SpeedOfLight_RooflineChart.section
  SpeedOfLight_TensorRooflineChart   PPU Speed Of Light Roofline Chart (Tensor Cell)   yes       /usr/sections/SpeedOfLight_TensorRooflineChart.-
                                                                                                 section
  WarpStateStats                     Warp State Statistics                             yes       /usr/sections/WarpStateStatistics.section
```

> **注意：** set 包含哪些 section，在不同的版本，可能会有差异，以实际查询到结果为准

###### 4.1.1.2.1. 指定 Section 文件搜索路径
acu 支持指定`section文件`的搜索路径，如果指定了搜索路径，则查询到的 section 为路径下的所有以`.section`为后缀的文件。有两种指定方式：

+ `--section-folder`：指定`section文件`的搜索路径，acu 在此文件夹内搜索以`.section`为后缀的文件，不递归搜索子文件夹
+ `--section-folder-recursive`：指定`section文件`的搜索路径，acu 在此文件夹和所有子文件夹内递归搜索以`.section`为后缀的文件

例如，查看`/usr/custom`的 section 信息：

```bash
acu --list-sections --section-folder=/usr/custom/
```

##### 4.1.1.3. 查询 Metric 列表
可通过`--list-metrics`命令行选项，查询支持的 metric 列表。默认情况下查询`default set`所包含的 metric 列表，可以通过`--section`或者`--set`查询指定 section 或者 set 所包含的 metric。

###### 4.1.1.3.1. 查询 Section 包含的 Metric 列表
通过`--section`查询指定 section 所包含的 metric

```bash
root@d29fb2dd227a:/# acu --section SpeedOfLight --list-metrics
breakdown:cu__throughput.avg.pct_of_peak_sustained_elapsed
breakdown:ppu__compute_memory_throughput.avg.pct_of_peak_sustained_elapsed
ce__cycles_active.max
ce__cycles_elapsed.avg.per_second
ce__cycles_elapsed.max
cu__cycles_active.avg
cu__throughput.avg.pct_of_peak_sustained_elapsed
dram__cycles_elapsed.avg.per_second
l1__throughput.avg.pct_of_peak_sustained_active
l2__throughput.avg.pct_of_peak_sustained_elapsed
llc__throughput.avg.pct_of_peak_sustained_elapsed
ppu__compute_memory_throughput.avg.pct_of_peak_sustained_elapsed
ppu__dram_throughput.avg.pct_of_peak_sustained_elapsed
ppu__time_duration.sum
```

###### 4.1.1.3.2. 查询 Set 包含的 Metric 列表
通过`--set`查询指定 set 所包含的 metric

```bash
root@d29fb2dd227a:/# acu --set=default --list-metrics
breakdown:cu__throughput.avg.pct_of_peak_sustained_elapsed
breakdown:ppu__compute_memory_throughput.avg.pct_of_peak_sustained_elapsed
ce__cycles_active.max
ce__cycles_elapsed.avg.per_second
ce__cycles_elapsed.max
cu__cycles_active.avg
cu__inst_executed.avg.pct_of_peak_sustained_active
cu__inst_executed.avg.per_cycle_active
cu__inst_executed.avg.per_cycle_elapsed
cu__inst_executed_pipe_falu_fp16.avg.pct_of_peak_sustained_active
cu__inst_executed_pipe_falu_fp32.avg.pct_of_peak_sustained_active
cu__inst_executed_pipe_lsu.avg.pct_of_peak_sustained_active
cu__inst_executed_pipe_sfu.avg.pct_of_peak_sustained_active
cu__inst_executed_pipe_simt_control.avg.pct_of_peak_sustained_active
cu__inst_executed_pipe_sls.avg.pct_of_peak_sustained_active
cu__inst_executed_pipe_tensor_fp16.avg.pct_of_peak_sustained_active
cu__inst_executed_pipe_tensor_tf32.avg.pct_of_peak_sustained_active
cu__instruction_throughput.avg.pct_of_peak_sustained_active
cu__memory_throughput.avg.pct_of_peak_sustained_elapsed
cu__throughput.avg.pct_of_peak_sustained_elapsed
dram__bytes.sum.peak_sustained
dram__bytes.sum.per_second
dram__cycles_elapsed.avg.per_second
ksd__transaction_hit_rate.pct
kvd__transaction_hit_rate.pct
l1__throughput.avg.pct_of_peak_sustained_active
l2__throughput.avg.pct_of_peak_sustained_elapsed
l2__transaction_hit_rate.pct
llc__average_lcu_input_transaction_success_rate.pct
llc__average_lcu_output_transaction_compression_achieved_rate.ratio
llc__throughput.avg.pct_of_peak_sustained_elapsed
llc__transaction_hit_rate.pct
ppu__compute_memory_access_throughput.avg.pct_of_peak_sustained_elapsed
ppu__compute_memory_request_throughput.avg.pct_of_peak_sustained_elapsed
ppu__compute_memory_throughput.avg.pct_of_peak_sustained_elapsed
ppu__dram_throughput.avg.pct_of_peak_sustained_elapsed
ppu__time_duration.sum
pu__cycles_elapsed.avg.per_second
```

##### 4.1.1.4. 查询 Metric 描述信息
可通过执行`acu --query-metrics`，查询 metric 的描述信息，例如：

```bash
root@0549cf16bb85:~# acu --query-metrics
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Metric Name                                                                                    Type        Unit           Metric Description
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 ce__cycles_active.avg                                                                          Counter     cycle          # of cycles active on CE across CEs
 ce__cycles_active.max                                                                          Counter     cycle          # of cycles active on CE across CEs
 ... 
 dram__bytes_read.sum                                                                           Counter     byte           # of bytes read from DRAM
 dram__bytes_read.sum.pct_of_peak_sustained_elapsed                                             Counter     %              # of bytes read from DRAM
 dram__bytes_read.sum.per_second                                                                Counter     byte/second    # of bytes read from DRAM
 ...
 l2__transaction_hit_rate                                                                       Ratio       unitless       (0.x) hit rate of L2 cacheable requests
 l2__transaction_hit_rate.pct                                                                   Ratio       %              (0.x) hit rate of L2 cacheable requests
 ...
```

+ `Metric Name列`: 查询 metric 的 name
+ `Type列`：metric 的类型，有三种：
    - Counter：PPU 的原始 counter
    - Ratio：两个 Counter 的比值
    - Throughput：由一组 Counter 组成，计算每一个 Counter 占 PPU 峰值的百分比，其中，最大的百分比即为 Throughput
+ `Unit列`: metric 的单位
+ `Metric Description列`: metric 的描述信息

> **提示：** 在`Asight Compute GUI`中，可通过鼠标悬停在性能指标名字上的方式，或打开 Metric Details 页面，查看对应的 metric 和相关描述信息：
> ![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125028766/c72251e6364cd2585edc6c7cfb0737a9/unit_metric_1.png)

<a id="Uu8pH"></a>

#### 4.1.2. 指定采集的 Metric 集合
可选择`set`、`section`和`metric`中的一种粒度，来指定采集的 metric 集合。

三种粒度的组合效果描述如下：

+ 若`--set` `--section` `--metrics`三个选项都没有指定，则生效的 metric 集合为`default set`
+ 若指定`--section`或者`--metrics`，则`--set`的默认值不生效
+ `--set` `--section`和`--metrics`选项可混合使用，生效的 metric 集合为三者的并集

> **提示：** 粒度越大，采集的 metric 也就越多。当需要采集的 metric 个数超过 PPU 能力上限时，应用程序可能会被 replay 多次以采集所有 metric 数据，从而导致 acu 的 profile 耗时增加。

##### 4.1.2.1. 指定采集的 Set
通过`--set`选项可指定使能的 metric set，基本规则如下：

+ 只允许一个 set 被使能
+ 若无`--set`被指定，并且`--section`或`--metrics`也没被指定，默认使能`default set`。

例如，使能`detailed set`，可通过下面命令：

```bash
acu -o test_report -f --set="detailed" ./cuda_test 10
```

默认使能的`default set`不是所有 metric 的集合，比如内存吞吐量的 metric 就不在`default set`。如果有需要采集内存吞吐量等相关的 metric，可使能`full set`，以采集所有 metric，命令如下：

```bash
acu -o test_report -f --set="full" ./cuda_test 10
```

##### 4.1.2.2. 指定采集的 Section
通过`--section`选项可指定使能的 metric section，基本规则如下：

+ 每个`--section`指定一个 section 的匹配规则
+ section 规则匹配方式有两种：
    - 精准匹配：指定 section 的 Identifier，只有 Identifier 完全匹配的 section 才会被使能（可通过`--list-sections`选项查看 section 的 Identifier）
    - 正则匹配：指定正则表达式，规则语法为`regex:<expression>`。所有 Identifier 能匹配正则表达式`<expression>`的 section 都将被使能
+ 如果同时指定多个`--section`匹配规则，匹配的 section 规则都会生效。

举例：通过正则表达式`"regex:.*WorkloadAnalysis"`使能所有以`WorkloadAnalysis`结尾的 section，这样，`ComputeWorkloadAnalysis`、`MemoryWorkloadAnalysis`等 section 都会被使能：

```bash
acu --section="regex:.*WorkloadAnalysis" python test_linear.py
```

举例：依次指定`SpeedOfLight`和`SchedulerStats`两个精准匹配规则，两个 section 都会被采集：

```bash
acu --section SpeedOfLight --section SchedulerStats python test_linear.py
```

> **提示：** 由于正则表达式语法可能会被 Linux shell 处理，使用正则表达式指定 section 时，建议用`""`包裹参数，例如：--section="regex:.*Analysis.*"

##### 4.1.2.3. 指定采集的 Metric
通过`--metrics`选项可指定使能的 metric 列表，基本规则如下：

+ 多个 metric 名字之间通过`,`分隔，可通过`--list-metrics`查看支持的 metric 名称列表
+ 如果同时指定多个`--metrics`选项，所有设置的 metrics 都会生效
+ 如果同时指定`--section`，那么，该 section 包含的 metric 和`--metrics`指定的 metric 都会被采集
+ `--metrics`的名称规则匹配方式有两种：
    - 精准匹配，包含 3 种情况：
        * 指定 metric 全名
        * 指定 metric group 全名：语法为`group:<group name>`，本 metric group 内的所有 metric 都将被采集
        * 指定 breakdown 全名：语法为`breakdown:<metric name>`，本 metric 拆分的所有子 metric 都将被采集并计算
    - 正则匹配：语法为`regex:<expression>`，所有名称能匹配正则表达式`<expression>`的 metric 将被采集。

> **提示：** - metric group 和 breakdown 可通过--list-metrics 命令行选项查询
> - 由于正则表达式语法可能会被 Linux shell 处理，使用正则表达式指定 metric 时，建议用`""`包裹参数，例如：--metrics="regex:dram.*"

举例：采集`ce__cycles_active.max`和`dram__bytes.sum.per_second`2 个 metric，命令如下：

```bash
acu --metrics=ce__cycles_active.max,dram__bytes.sum.per_second python test_linear.py
```

举例：采集 group`memory__chart`包含的所有 metric，命令如下：

```bash
acu --metrics="group:memory__chart" python test_linear.py
```

举例：采集并计算 `cu__throughput.avg.pct_of_peak_sustained_elapsed`和`ppu__compute_memory_throughput.avg.pct_of_peak_sustained_elapsed`两个 metric 的所有子 metric 的值（不计算这两个 metric 的值），命令如下：

```bash
acu --metrics=breakdown:cu__throughput.avg.pct_of_peak_sustained_elapsed,breakdown:ppu__compute_memory_throughput.avg.pct_of_peak_sustained_elapsed python test_linear.py
```

举例：指定正则表达式，采集包含`cycles_elapsed`的所有 metric（比如：`ce__cycles_elapsed.avg.per_second`和`ce__cycles_elapsed.max`），命令如下：

```bash
acu --metrics="regex:cycles_elapsed.*" python test_linear.py
```

举例：指定正则表达式，采集所有以`dram`开头的 metric（比如：`dram__bytes.sum.peak_sustained`和`dram__bytes.sum.per_second`会被采集，`ppu__dram_throughput.avg.pct_of_peak_sustained_elapsed`不会被采集），命令如下：

```bash
acu --metrics="regex:^dram.*$" python test_linear.py
```

##### 4.1.2.4. 自定义 Section 文件采集 Metric
当 Asight Compute 中内置的 Section 文件中的 Metric 不能满足分析需求，或者需要自定义 Metric 计算公式时，都可以通过自定义 Section 文件来实现。

一个自定义的 Section 文件需要放在 SDK 的`asight/sections`目录下，在 GUI 端， 此 section 文件也需要放`<Asight Install Path>/sections`目录下

一个 Section 文件需要以下信息：

```bash
Identifier: "Custom" 
DisplayName: "Custom"
Description: "Custom"
Sets {                                                                                                                                                                              
    Identifier: "default"                                                                                                                                                           
} 
MetricDefinitions {                                                                                                                                                                 
    MetricDefinitions {  
        Name: "derived__test_metric"                                                                                                                                                    
        Expression: "dram__bytes_read_sum + dram__bytes_write.sum"   
    }
    ...
}
Header {
    Metrics {                                                                                                                                                                                  
        Label: "Dram Total Bytes"
        Name: "derived__test_metric"                                                                                                                                                                
    } 
    ...
}
```

+ `Identifier` 必须与其它 Section 文件中的不同
+ `Sets`指明当前 Section 归于的 Set，如果配置为`default`，acu 命令行不用指定 metric、section、set，默认参数就可以采集到
+ `MetricDefinitions`：用于声明 Metric，声明的 Metric 并不会用于采集，共有两级
    - 第一级：是 Metric 声明的列表，这里可以有多个 Metric 的声明。
    - 第二级：声明 Metric 的详细信息
        * Name：此为 Metric Name 不能与其它 Metric 名称重复，建议使用`derived__`做为前缀，不能使用`_`外的其它字符。
        * Expression：为 Metric 的计算公式，计算公式中可以使用内置的 Metric 做为算子，不要使用自定义的 Metric 做为算子。公式支持` + - * /`操作，支持函数：`max`和`min`
            + 例如： `Expression: "M1 + M2 * (M3 + M4) + max(M5, M6, M7) "`
+ Header：用于 Metric 的采集与显示，Header 中可以有多个`Metrics`的定义，在 Header 中定义的 Metric，会在 GUI 的 Detail Page 中显示出来。
    - 在 Header 下定义的`Metrics`可以在`acu --list-metric`中显示出来，在采集时会被用于采集，`Metrics`中的 Name 必须为内部 Metric Name 或者是以上`MetricDefinitions`中声明的 Metric Name。

<a id="UziBy"></a>

#### 4.1.3. 指定 Replay 模式
由于在 PPU 上同时可采集的 Performance Counter（硬件）个数是有上限的，当需要采集 Performance Counter（所有 metric 依赖的）个数超过上限时，acu 需要重播（replay） kernel 多次（重播一次称为一个 pass），并且每次重播需设置不同的 counter 配置，以保证所有 metric 数据被采集。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124984334/249471165ec255c9eb69d1a5d1309937/acu_listmetric_1.png)

acu 支持多种重播（replay）模式，默认采用 kernel replay 模式采集数据，可通过`--replay-mode`选项指定 replay 模式：

| Replay 模式 | 模式说明 | Profiling 对象 | 程序执行次数 | 保存/恢复内存 | Overhead | 不适用场景 |
| --- | --- | --- | --- | --- | --- | --- |
| **kernel** | 在一次程序执行中，依次分别对每个 kernel 进行 replay | Kernel | 1 次 | 是 |  Save/Restore 内存的耗时<br/> 额外内存用于 Save/Restore |  Kernel 必须 concurrent 执行 |
| **application** | 多次执行应用程序，一次程序执行对应一次 replay，并依次采集每个 kernel 的性能指标 | Kernel | 多次 | 否 |   多次应用程序启动耗时 |  Kernel 必须 concurrent 执行<br/>+ 程序的执行行为不确定 |
| **range** | 在一次程序执行中，依次分别对每个 Range（包含 kernel launch，HGGC API 调用）进行 replay | Range | 1 次 | 是 |  Save/Restore 内存的耗时<br/> 额外内存用于 Save/Restore<br/> Capture Range 耗时 |  Range 中存在不支持的 HGGC API<br/> 应用程序中没有通过 cu(da)ProfilerStart/Stop 定义 Range |
| **app-range** | 多次执行应用程序，一次程序执行对应一次 replay，并依次采集每个 Range（包含 kernel launch，HGGC API 调用）的性能指标 | Range | 多次  | 否 |  多次应用程序启动耗时 |  程序的执行行为不确定 |

由于每种 replay 模式对应用程序的影响方式各有不同（或改变程序中 kernel 的执行顺序，或引入一些性能损耗），需要根据应用程序的具体实现，选择适合本应用程序的 replay 模式。

举例：使用 kernel replay 模式采集性能数据

```bash
acu --replay-mode kernel python test_linear.py
```

##### 4.1.3.1. Kernel Replay 模式
Kernel Replay 模式是在一次应用程序执行过程中，通过对每个 kernel 执行多次的方式，采集所有 metric 数据。在 kernel 第一次执行前备份 PPU 设备内存，后续在每一次 replay kernel 前恢复第一个 pass 备份设备内存。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125006986/28162f4ff282851fc46f95c9fb2cfbfb/kernel_replay_1.png)

Kernel Replay 模式的主要特点如下：

+ replay 在一次应用程序执行中完成
+ 按照 kernel 粒度采集性能数据
+ 应用程序的 kernel 被强制串行执行
+ kernel 执行前，存在内存备份 / 恢复操作，将增加整个应用执行耗时
+ 内存备份将消耗设备内存资源

因为 Kernel Replay 在 profiling 时会对 kernel 强制串行化，所以，并不是所有程序都适用，下面详述其适用/不适用场景。

<a id="roEou"></a>

###### 4.1.3.1.1. 适用场景
- 单进程，单线程（所有 kernel 在一个线程里依次 launch）

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125004707/1447526e7f45e3534caecb337db68c02/kernel_launch_example_1.png)

- 单进程，多线程（多个线程里的 kernel 不相互依赖）

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125005001/2d1b2cab1429c311fe1508469aa73730/kernel_launch_example_2.png)

- 多进程（多个进程里的 kernel 不相互依赖）

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124986898/3b8dddbd6b7dcf1b42f69e1e7f8e3368/applicable_scenarios_1.png)

- Graph 场景

支持对 graph 中的 kernel node 进行 profiling，该功能需要通过选项`--graph-profiling node`打开。详细介绍请参考：[Graph Profiling 的 node 模式](#nkFgy)

<a id="eznow"></a>

###### 4.1.3.1.2. 不适用场景
如果 kernel 之间有依赖关系，在使用 Kernel Replay 时，会出现 hang 的情况

- 单进程，单线程（kernel 之间有依赖关系）

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125000528/21b59e50c1dc204dcc42f3867947a501/inapplicable_scenarios_1.png)

`例子：`pccl-tests（1 个进程，1 个线程，2 个 rank）

```bash
acu --set full -f -o all_reduce_2_ranks_2M ./build/all_reduce_perf -g 2 -n 1 -w 0 -b 2M -e 2M -c 0
```

- 单进程，多线程（多个线程里的 kernel 存在依赖关系）

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125000825/6735185ea6ca918062dd0b90f9da0826/inapplicable_scenarios_2.png)

`例子：`pccl-tests（1 个进程，2 个线程，每 1 个线程一个 rank）

```bash
acu --set full -f -o all_reduce_2_ranks_2M ./build/all_reduce_perf -g 1 -t 2 -n 1 -w 0 -b 2M -e 2M -c 0
```

- 多进程（多个进程里的 kernel 存在依赖关系）

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125001078/1679092473207898f6e6e0fe1a1df66b/inapplicable_scenarios_3.png)

`例子：`pccl-tests（2 个进程，每 1 个进程 1 个线程，每 1 个线程 1 个 rank）

```bash
acu --set full --replay-mode kernel --target-processes all -o all_reduce_perf_kernel_p2_t1_g1 mpirun -np 2 --allow-run-as-root ./build/all_reduce_perf -g 1 -t 1 -n 1 -w 0 -b 2M -e 2M -c 0
```

##### 4.1.3.2. Application Replay 模式
Application Replay 模式是通过多次执行应用程序的方式，采集所有 metric 数据。由于是重复启动应用程序，Application Replay 模式不需要对每个 kernel 做内存的备份和恢复，但是需要保证应用程序在多次执行中行为应尽可能保持一致（比如：kernel 的名称 / 数量 / 执行顺序等）。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124987793/711bb055c17aa445449f6c91c8a90f22/application_replay_1.png)

Application Replay 模式的主要特点如下：

+ 应用程序被执行多次，以保证所有 metric 数据被采集
+ 按照 kernel 粒度采集性能数据
+ 应用程序 kernel 之间强制串行执行
+ 若应用程序 host 端存在大量耗时操作（如初始化），多次 replay 将增加执行耗时

###### 4.1.3.2.1. 适用/不适用场景
因为 Application Replay 和 Kernel Replay 一样，在 profiling 时会对 kernel 强制串行化，所以，Kernel Replay 的适用/不适用场景说明同样适用于 Application Replay。具体请参考 Kernel Replay 的：[适用场景](#roEou)和[不适用场景](#eznow)

由于 Application Replay 是跨应用程序的 replay，一个 kernel 的 metric 数据分散在多次应用程序执行中，这就存在一个跨应用程序 kernel 如何匹配的问题，acu 针对这种情况，提供了`--app-replay-mode`和` --app-replay-match`两个命令行选项。

###### 4.1.3.2.2. kernel 匹配模式
acu 提供`--app-replay-mode`选项，可以在 Application Replay 做 kernel 匹配时，指定是否严格检查应用多次执行的行为一致，有两种模式：

| app-replay-mode 可选值 | 模式描述 |
| --- | --- |
| strict | 默认值，每次应用程序执行中的所有 kernel 都要和应用程序第一次执行中的所有 kernel 匹配。在任何一个 pass 中，如果匹配失败，则中断 profiling 流程。 |
| relaxed | 不要求跨应用程序的所有 kernel 全部匹配，只输出能匹配的 kernel 的 metric 数据 |

> **提示：** 如果一个程序在`strict`模式下无法生成报告，这说明应用程序的执行行为是不确定的，可以尝试`relaxed`模式，但最终生成的报告可能缺失某些 kernel 的性能数据

###### 4.1.3.2.3. kernel 匹配策略
acu 提供` --app-replay-match`选项，可以在 Application Replay 做 kernel 匹配时，指定 kernel 匹配策略（满足什么条件才认为是同一个 kernel）。支持下面 3 种匹配策略：

| app-replay-match 可选值 | 匹配策略描述 |
| --- | --- |
| name | kernel 按照以下顺序匹配：<br/>1. mangled 名称<br/>2. 执行顺序 |
| grid | 默认值，<br/>kernel 按照以下顺序匹配：<br/>1. mangled 名称<br/>2. kernel 的 grid / block 大小<br/>3. 执行顺序 |
| all | kernel 按照以下顺序匹配：<br/>1. mangled 名称<br/>2. grid / block 大小<br/>3. context id<br/>4. stream id<br/>5. 执行顺序 |

举例：使用 application replay 模式采集性能数据，宽松模式匹配，使用 grid 匹配策略进行匹配：

```bash
acu --replay-mode application --app-replay-mode relaxed --app-replay-match grid python test_linear.py
```

<a id="J4lHG"></a>

##### 4.1.3.3. Range Replay 模式
Range Replay 模式是在一次应用程序执行过程中，通过对一个 Range（包含 kernel launch 和 HGGC API 调用）执行多次的方式，采集所有 metric 数据，并且 metric 数据跟整个 range 相关，而不再是其中的某个 kernel。Range Replay 会捕获 range 中的 kernel launch 和 HGGC API 调用，并执行必要的 Host 和 Device 内存的保存和恢复。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125016558/10a4211028e78bd5abb3c49a3f393849/range_replay_1.png)

Range Replay 模式的主要特点如下：

+ replay 在一次应用程序执行中完成
+ 按照 range 粒度采集性能数据，非 Kernel 粒度
+ range 内的多个 kernel 可并行执行，不作强制串行化
+ replay range 存在内存备份 / 恢复操作，将增加应用执行耗时
+ range 范围内只有部分 HGGC API 允许使用
+ range replay 仅 replay PPU Device 侧的行为，Host 端应用行为不会 replay
+ 应用程序通过`hg(gc)ProfilerStart`和`hg(gc)ProfilerStop`定义 range，并保证 acu 可以在 range 开始时同步所有 context
+ 一个 range 内仅支持采集 1 个 PPU 设备上的性能数据

<a id="yVvxx"></a>

###### 4.1.3.3.1. range 的定义
Range replay 需要在应用程序中指定性能分析的 range（范围）。一个 range 由起始和结束标记定义，包含在这些标记之间从任何 CPU 线程启动的所有 HGGC API 调用和内核。应用程序负责在线程之间插入适当的同步，以确保捕获到预期的 API 调用集合。可以使用以下两种方式定义 range：

* Profiler Start/Stop API

使用 hg(gc)ProfilerStart 设置起始标记，并使用 hg(gc)ProfilerStop 设置结束标记，这是 Asight Compute range 定义的默认选项

```c
hggcProfilerStart();
/* code for profiling, include HGGC API and Kernels */
hggcProfilerStop();  
```

* HGTX range

使用 [HGTX include ](#B36sq)表达式来定义 range。range 捕获从第一个 HGGC API 调用开始，并在匹配到表达式的最后一个 API 调用处结束。如果指定了多个表达式，则在任何一个表达式匹配时都定义一个 range。因此，可以使用多个表达式方便地捕获和分析同一应用程序执行的多个 range。 应用程序必须使用 HGTX API 进行 range 的标记，以使表达式能够匹配。例如，在程序`cuda_test`中，定义一个名字为`Range 1`的 hgtx range：

```c
hgtxRangeId_t r1 = hgtxRangeStartA("Range 1");
/* code for profiling, include HGGC API and Kernels */
hgtxRangeEnd(r1);

```

那么，使用下面命令，即可 profiling 程序`cuda_test`中`Range 1`区间内的代码。

```bash
acu --hgtx --hgtx-include "Range 1" cuda_test
```

> **注意：** 上文例子，如果不用 start/end 定义 range，改为 push/pop 定义的 range，则 acu 命令需要改为 `--hgtx-include "Range 1/"`，更多细节请参考[ HGTX 过滤](#B36sq)
> Range 和 Application Range Replay 的 range 定义表达式不支持 hgtx-exclude
> + 如`--hgtx --hgtx-include --hgtx-exclude`则忽略--hgtx-exclude，并提示不支持--hgtx-exclude
> + 如`--hgtx --hgtx-exclude`则提示如下错误：
> ==ERROR== Option hgtx-exclude is not supported during range replay.

###### 4.1.3.3.2. 适用场景
虽然 Range Replay 也可以在 Kernel Replay 的 3 个[适用场景](#roEou)中运行，但 Range Replay 主要是为解决并行执行的多个 kernel 的 profiling 问题的（也就是 Kernel Replay 的[不适用场景](#eznow)中的 1，2 两种情况）

- 单进程，单线程（依赖的 kernel 在同一个 range 内）

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125006427/274d9bbd372c1cf0bbfc13839b2ca0d0/kernel_range_replay_1.png)

`例子：`pccl-tests（1 个进程，1 个线程，2 个 rank）

```bash
acu --set full --replay-mode range -o all_reduce_perf_range_p1_t1_g2 ./build/all_reduce_perf -g 2 -n 1 -w 0 -b 2M -e 2M -c 0
```

- 单进程，多线程（依赖的 kernel 在同一 range 内）

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125006651/04a753d20d7e3fb642ce10cca2c96a88/kernel_range_replay_2.png)

`例子：`pccl-tests（1 个进程，1 个线程，2 个 rank）

```bash
acu --set full --replay-mode range -f -o all_reduce_2_ranks_2M ./build/all_reduce_perf -g 1 -t 2 -n 1 -w 0 -b 2M -e 2M -c 0
```

<a id="KkTZt"></a>

###### 4.1.3.3.3. 不适用场景
Range Replay 的 range 是进程级的，所以，如果 kernel 在不同的线程中且相互依赖，那么，需要保证 range 包含这些相互依赖的 kernel，否则，会发生 hang。

另外，Range Replay 会对 range 强制串行化，所以，一个进程内的 range 依赖其他进程的 kernel 或者 range 的话，会发生 hang 的情况。

- 单进程，多线程（相互依赖的 kernel 没有在同一个 range）

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125005812/9955522c28dcbad8f9e2437e381bbd7c/kernel_range_1.png)

- 多进程（一个进程内的 range 和另外一个进程的 kernel 存在依赖）

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125006118/8a46d0d832afb51c65dc8808b2897f33/kernel_range_2.png)

`例子：`pccl-tests（2 个进程，每 1 个进程 1 个线程，每 1 个线程 1 个 rank，只在 1 个 rank 上定义了 range）

```bash
acu --set full --replay-mode range --target-processes all -o all_reduce_perf_range_p2_t1_g1 mpirun -np 2 --allow-run-as-root ./build/all_reduce_perf -g 1 -t 1 -n 1 -w 0 -b 2M -e 2M -c 0 -j 0
```

- 多进程（一个进程内的 range 和另外一个进程的 range 存在依赖）

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125017111/2c7e86f628dc7fa91bd25e5f3e3bb4b0/range_replay_dependencies_1.png)

`例子：`pccl-tests（2 个进程，每 1 个进程 1 个线程，每 1 个线程 1 个 rank，2 个 rank 上都定义了 range）

```bash
acu --set full --replay-mode range --target-processes all -o all_reduce_perf_range_p2_t1_g1 mpirun -np 2 --allow-run-as-root ./build/all_reduce_perf -g 1 -t 1 -n 1 -w 0 -b 2M -e 2M -c 0
```

##### 4.1.3.4. Application Range Replay
在 Application Range Replay 模式下，所有请求的 metrics 被分组为一个或多个 pass。与[Range Replay](#J4lHG)类似，metrics 不是与单个 kernel 关联，而是与整个选择的 range 关联。工具无需对工作负载（kernel，graph 等）串行化，所以，支持对需要并发执行的工作负载进行性能分析。

与 Range Replay 不同的是，每一个 range 不需要先被显式地捕获（captured）再执行多次，而是将整个应用程序重新运行多次（每一次程序执行对应一个 pass），并在每次应用程序执行中，采集每一个 range 的 metrics 数据。这样做的好处是：不需要跟踪和捕获每个 range 的应用程序状态（比如：不需要对 memory 进行保存和恢复），因为 range 的正确执行由应用程序本身处理。

range 的定义跟[Range Replay](#yVvxx)一样，并且需要用户保证 range 工作负载执行的确定性。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124987469/e8a9ecf25bec30d6f7da1db012c5a1ce/application_range_replay_1.png)

###### 4.1.3.4.1. 适用场景

Application Range Replay 可以解决 Range Replay 不能解决的[不适用场景 2](#KkTZt)，只需保证仅有一个进程定义 range。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124987190/210405cb02de333671beef62f8934381/applicable_scenarios_2.png)

`例子：`pccl-tests（2 个进程，每 1 个进程 1 个线程，每 1 个线程 1 个 rank，只在 1 个 rank 上定义了 range）

```bash
acu --section Icnlink --replay-mode app-range --target-processes all mpirun -np 2 --allow-run-as-root ./build/all_gather_perf -g 1 -t 1 -n 1 -w 0 -b 512M -e 512M -c 0 -q 1 -s 1 -j 0
```

###### 4.1.3.4.2. 不适用场景

应用程序包含多个进程，每个进程都定义 range，如果这些 range 中的 kernel 存在依赖，那么，会发生 hang.

另外，这些 range 在每次 replay 时，如果执行顺序无法保证，多次 replay 得到的这些性能数据可能无法按 range 进行匹配，从而，导致无报告生成。

1. 多进程（2 个 range，其中一个进程的 range 依赖另一个进程的 range）

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125001366/16676eb8bf3c09f3d132667ddde4a40e/inapplicable_scenarios_4.png)

2. 多进程（2 个 range，不相互依赖，但是 2 个 range 的执行顺序无法保证）

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125001660/c6a5be49292c448e864feb969fc7611c/inapplicable_scenarios_5.png)

3. 多线程（2 个 range，不相互依赖，但两个 range 的执行顺序无法保证）

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124997049/9fb403037da7840f94aedaed64bc1202/graph_profiling_1.png)

##### 4.1.3.5. Graph Profiling
acu 支持对 graph 整体，以及 graph 中的单个 kernel node 进行 profiling，可以通过选项`--graph-profiling`指定模式。

###### 4.1.3.5.1. graph 模式
Graph Profiling 的 graph 模式是把 HGGC graph 作为单个工作负载实体进行性能分析。

该功能可以通过选项`--graph-profiling graph`打开。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124997349/1993653cf6b86dffd18e2966de6a3cd1/graph_profiling_2.png)

此模式的主要使用场景包括：

+ graph 中包含了必须并发执行的 kernel node
+ 需要更准确地分析包含多个 kernel node 的 graph 的性能

<a id="nkFgy"></a>

###### 4.1.3.5.2. node 模式
Graph Profiling 的 node 模式是把 HGGC graph 中的单个 kernel node 作为工作负载实体进行性能分析。

该功能可以通过选项`--graph-profiling node`打开。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124997617/061b8de2861249d514eb934080b2a123/graph_profiling_node_1.png)

此模式的主要使用场景包括：

+ 需要准确地分析 graph 中单个 kernel node 的性能
+ graph 中 kernel node 之间没有依赖关系

需要注意的是，启用 Graph Profiling 时：

+ 必须在`--replay-mode kernel`下才能使用，默认为 graph 模式
+ 如果不关注 graph 的性能，可以通过`--graph-profiling none`关闭 graph profiling 功能。
+ 某些性能指标，比如指令统计相关的指标，在 graph 模式下不可用

**比赛关联：** 对 VLM 推理服务做 kernel 级采集时，多轮 decode 会产生大量重复 kernel，应配合 `--launch-skip`/`--launch-count`/`--kernel-name` 只采集目标 kernel，并优先使用默认的 kernel replay；若 kernel 间存在依赖（如通信/并发算子）导致 hang，需改用 range 或 app-range 模式。

#### 4.1.4. 采集 CUDA 源码文件
acu 支持将目标应用程序中的 CUDA 源码文件导入报告文件，当报告中包含了 CUDA 源码文件，在 GUI 打开报告环境中没有 CUDA 源码文件，Source Page 中也能正常显示出 CUDA 源码信息。不需要再手动选择 CUDA 源码路径。

acu 默认配置中不采集 CUDA 源码文件，如需采集需要使用参数 `--import-source yes` 例如：

```bash
acu --import-source yes <other acu param> <target program>
```

> **注意：** 采集 CUDA 源码文件，需要目标应用程序中编译时包含源码信息，因此需要在编译参数中增加 `-lineinfo`选项。如果需要准确的汇编代码与 CUDA 文件行号定位，还需要编译时增加 Debug 信息。例如：`nvcc -g --lineinfo -O0 -o <my_program> <my_program.cu>`

### 4.2. 控制采集过程

#### 4.2.1. 指定采集设备

通过 `--devices` 可指定使能采集的 PPU 设备列表：

+ 设备由序号（PPU 设备上电后从 0 开始的索引）指定
+ 多个 PPU 设备通过逗号 `,` 分隔
+ 若不指定，默认允许在所有 PPU 设备上采集数据。

举例：采集 PPU 设备 1 和 2 上运行的性能数据：

```bash
 acu --devices 1,2 python test_linear.py
```

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125016845/7a077139b750be637099771cc880f35f/range_replay_2.png)

> **注意：** `range replay`模式下，`--devices`只允许指定 1 个 PPU 设备

#### 4.2.2. 指定采集时间范围
通过`--profile-from-start`选项可指定 metric 采集是否从应用程序启动开始，对于`Application Replay`/`Kernel Replay`模式生效。支持的选项说明如下：

| profile-from-start 可选值 | 策略描述 |
| --- | --- |
| on 或者 yes（默认值） | 从应用启动开始采集性能数据 |
| off 或者 no | 从`profiler start API`开始采集性能数据，<br/>直到`profiler stop API`停止性能数据采集。<br/>`profiler start/stop API`参见下文描述。 |

acu 支持的`profiler start/stop API`组合如下：

+ `cudaProfilerStart/Stop`
+ `hggcProfilerStart/Stop`
+ `cuProfilerStart/Stop`
+ `hgProfilerStart/Stop`

举例：指定采集从`profiler start API`开始，到`profiler stop API`截止，命令如下：

```bash
acu --profile-from-start off python test_linear.py
```

如果应用程序中`cu(da)ProfilerStart()`和`cu(da)ProfilerStop()`定义的采集的范围如下图所示，那么，第一个 range（3 个 kernel）和第 2 个 range（1 个 kernel）的性能数据将被采集：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124992179/f7a4a3cbf93837d7197e1fee5bc64b3b/cuda_profiler_api_1.png)

**disable-profiler-start-stop**

通过`--disable-profiler-start-stop`选项，可指定忽略`profiler start/stop API`

+ 如果指定了`--disable-profiler-start-stop`选项，`--profile-from-start`选项会被忽略，性能数据的采集会从应用程序启动时开始。

<a id="NjM0a"></a>

#### 4.2.3. 过滤 Kernel

acu 支持多种过滤方式来确定是否对程序中 kernel 进行性能数据的采集。  

> **注意：** 这些 kernel 级别的过滤方式仅对`Application Replay`/`Kernel Replay`模式生效。

##### 4.2.3.1. 指定 Kernel 名称基准
可以通过`--kernel-name-base` 为`--kernel-name`选项或者`--kernel-id`选项指定 kernel name 基准。它支持的可选项包括 function, mangled, demangled。默认值是 function。

+ `function` 不带参数和模版的 function 名称，例如 `foo`
+ `demangled` demangled function 名称，包括参数和模板，例如` foo(float*,int,int)`
+ `mangled` mangled function 名称，编译器生成的 mangled kernel 名称，例如 `_S4_S4_9TileShapeS4_S4_iSC`

举例：指定 kernel 的`function`名称作为过滤基准，采集所有 function 名称包含`foo`的 kernel 的性能数据，命令如下：

```bash
acu --kernel-name-base function --kernel-name regex:foo -o cuda_test ./cuda_test 1
```

##### 4.2.3.2. 指定 Kernel 名称
可以通过`--kernel-name`设置要匹配的 kernel 名称的表达式，kernel 名称要匹配的基准取决于`--kernel-name-base`的值，具体请查看`--kernel-name-base`相关描述。`--kernel-name`支持如下方式指定：

+ `通过kernel名称指定`：采集名称与指定名称完全匹配的 kernel
+ `通过正则表达式指定`：语法为`regex:<expression>`，采集名称与正则表达式匹配的所有 kernel

> **注意：** 由于正则表达式语法可能会被 Linux shell 处理，使用正则表达式指定 kernel-name 时，建议用`""`包裹参数，例如：--kernel-name="regex:^.*foo$"

举例：匹配所有名为`Bar`的 kernel

```bash
acu --kernel-name Bar ./cuda_test 1
```

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125005299/80fb99960e9be092a259932f1a030834/kernel_name_example_1.png)

举例：匹配所有包含字符串"Bar"的 kernel，例如`Bar`和`FooBar`

```bash
acu --kernel-name "regex:Bar" ./cuda_test 1
```

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125005578/f5e314f00e3ebcf859523ef5cec84c81/kernel_name_regex_example_1.png)

举例：匹配所有包括字符串"foo"或"bar"的 kernel，例如`foo`、`foobar`、`_bar2`

```bash
acu --kernel-name "regex:foo|bar" ./cuda_test 1
```

##### 4.2.3.3. 指定 Kernel ID
可以通过`--kernel-id`指定 kernel id 表达式。只有 kernel 的 id 与指定的表达式匹配，此 kernel 的性能数据才会被采集。

`kernel-id`表达式的语法格式为`context-id:stream-id:[name-operator:]kernel-name:invocation-nr`，字段间通过冒号`:`分隔，字段若不提供可填为空，表示对此字段不加过滤，5 个字段含义描述如下：

+ `context id`：指定 kernel 的 context ID
+ `stream id`: 指定 kernel 的 stream ID
+ `name-operator`:  用于修饰下一个字段`kernel-name`的描述符，可选（缺省时不需要携带`:`）
    - 当前仅支持填写为`regex`，表示`kernel-name`为正则表达式格式
+ `kernel-name`: kernel 名称的表达式，kernel 名称要匹配的基准取决于`--kernel-name-base`的值，具体请查看`--kernel-name-base`相关描述
    - 当`name-operator`为`regex`：采集名称与正则表达式匹配的所有 kernel
    - 当`name-operator`为空：采集名称与指定名称完全匹配的 kernel
+ `invocation-nr`：指定此 kernel 的第几次调用
    - 指定多次调用可以通过正则表达式定义
    - 调用次数+1 的条件是，上述的 context-id / stream-id / kernel name 等条件均匹配

> **注意：** 由于正则表达式语法可能会被 Linux shell 处理，使用正则表达式指定 kernel-id 时，建议用`""`或者`''`包裹参数，例如：--kernel-id="::regex:^.*foo$:"

举例：不指定 context / stream id，匹配 kernel 名称为`Foo`的第 2 次调用

```bash
acu --kernel-id ::Foo:2 ./cuda_test
```

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125003186/402462671949330c9137d4fafa19828a/kernel_1.png)

举例：匹配所有 kernel 的第 3 次调用，以及调用次数以 5 结尾的调用

```bash
acu --kernel-id "::::.*5|3" ./cuda_test
```

举例：匹配所有以“foo”结尾的 kernel

```bash
acu --kernel-id "::regex:^.*foo$:" ./cuda_test
```

举例：匹配所有不以“foo”开头的 kernel

```bash
acu --kernel-id '::regex:^(?!foo):' ./cuda_test
```

举例：匹配所有在 context 1, stream 3 上的 kernel 的第 5 次调用

```bash
acu --kernel-id 1:3::5 ./cuda_test
```

##### 4.2.3.4. 指定采集 Kernel 的个数
可以通过`--launch-count`指定需要 profile 的 kernel 个数的上限，并且只有满足`--kernel-name`和`--kernel-id`中的过滤条件的 kernel 才会被统计计数。

> **注意：** Range Replay 也支持该参数，只是统计的是 range 的个数

举例：只采集 2 个 kernel 的性能数据，后续 kernel 的性能数据不会被采集

```bash
acu --launch-count 2 ./cuda_test
```

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125009001/266eeac7032d4aebf102355923bb39df/launch_skip_1.png)

##### 4.2.3.5. 指定跳过 Kernel 的个数
可以通过`--launch-skip`设置 profile 之前忽略掉的 kernel 个数，并且只有满足`--kernel-name`和`--kernel-id`中的过滤条件的 kernel 才会被统计计数。

> **注意：** Range Replay 也支持该参数，只是统计的是 range 的个数

举例：先跳过 1 个 kernel，然后采集后续所有 kernel 的性能数据

```bash
acu --launch-skip 1 ./cuda_test
```

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125003417/44022b5c0488f65c074cd09af2ff5c10/kernel_2.png)

举例：先跳过 1 个 kernel，然后采集 2 个 kernel 的性能数据，剩下 kernel 的性能数据不会被采集

```bash
acu --launch-skip 1 --launch-count 2 ./cuda_test
```

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125009222/ddd8ac79036070c4c9f68cc8d1add2da/launch_skip_before_match_1.png)

##### 4.2.3.6. 指定匹配前跳过 Kernel 的个数
可以通过`--launch-skip-before-match`设置 profile 之前忽略掉的 kernel 个数，不管是否满足过滤条件，所有 kernel 都会被统计计数。

举例：无条件跳过 2 个 kernel 后，采集所有 kernel 名称包含`Foo`的 kernel

```bash
acu --launch-skip-before-match 2 --kernel-name regex:Foo ./cuda_test
```

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125003634/fc4f62d9f2f951e7939ad5dcf555d93e/kernel_3.png)

举例：不论 kernel 名称是否匹配，先跳过 2 个 kernel（黑色），在所有匹配（kernel 名字包含`Foo`）的 kernel 中，先跳过 2 个 kernel（红色），然后采集 2 个 kernel（绿色）的性能数据，剩下 kernel 的性能数据不会被采集

```bash
acu --launch-skip-before-match 2 --launch-skip 2 --launch-count 2 --kernel-name regex:Foo ./cuda_test
```

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125003869/163cacb4720d4bbb9e5b71cb70908d21/kernel_4.png)

##### 4.2.3.7. 采集完成后退出程序
通过指定`--kill`选项，决定是否在 launch-count 达到后，退出程序。默认为`yes`

举例：采集 2 个 kernel 的性能数据，然后退出程序。

```bash
acu --launch-count 2 --kill yes ./cuda_test
```

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125004179/d86b400d8f3aafe1c82db4a2b86386ea/kernel_5.png)

举例：采集 2 个 kernel 的性能数据，程序继续执行直至结束，后续 kernel 的性能数据不再采集

```bash
acu --launch-count 2 --kill no ./cuda_test
```

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125004433/b2009668b0a155822b167fb28835b744/kernel_6.png)

#### 4.2.4. 指定报告文件名
使用 `-o <报告名>` 可以将结果保存为报告文件（无需写后缀），acu 会自动添加在文件名后添加.acurep 后缀。

如果不指定`-o`参数，acu 会默认使用 `--page=details `将分析结果以 `details` 页面格式打印到屏幕 

#### 4.2.5. 以 Page/CSV 格式输出到屏幕
除了将结果存储在报告文件中，acu 还支持将结果以不同的页面（page）格式打印到屏幕。这些页面与 GUI 报告中的对应页面一致。

要选择不同的页面，或者在结果存储到指定文件的同时打印到屏幕，请使用`--page=<Page>` 命令。目前，acu 支持以下页面：`details, raw`。

如果只指定了 `-o` 而没有设置 `--page`，则不会在控制台看到结果。

使用 `--csv `可以将屏幕输出格式以 CSV 格式呈现

使用 `--csv-file <文件>` 可以将 CSV 格式的数据输出到指定文件中，不再输出到屏幕上，可避免屏幕上的输出信息对 CSV 格式数据的污染。 

#### 4.2.6. 导入报告文件
使用 `--import <报告文件>` 可以加载已有的 `.acurep` 文件，并在屏幕打印分析内容。

可与 `--page <Page>` 搭配使用，选择显示的页面。

输出相关的常用参数对照表：

| 参数 | 功能说明 | 输出位置 | 默认行为 |
| --- | --- | --- | --- |
| `-o <文件名>` | 保存分析结果为 `.acurep`报告文件（自动添加后缀） | 文件 | 可与 `--page`结合使用 |
| `--page <Page>` | 指定输出页面（`details`/ `raw`） | 屏幕 | 如果无 `-o`，默认 `details` |
| `--csv` | 屏幕输出为 CSV 格式 | 屏幕 | 可与 `--page`结合使用 |
| `--csv-file <文件>` | 将 CSV 格式数据输出到指定文件中 | 文件 | 可与 `--page`结合使用 |
| `--import <文件>` | 导入并显示现有报告文件 | 屏幕 | 可与 `--page`搭配使用 |
|（无参数） | 默认执行分析并在屏幕显示 `details`页面 | 屏幕 | 不生成文件 |

<a id="B36sq"></a>

#### 4.2.7. HGTX 过滤
`--hgtx-include <configuration> --hgtx-exclude <configuration>`

使用这些命令选项可以只对满足配置条件的 kernel 进行采样。通过这些选项，用户可以选择指定范围内的 kernel。

使用 HGTX 过滤功能必须指定`--hgtx`选项，同时用户可以一次或多次指定`--hgtx-include`和`--hgtx-exclude`选项。

HGTX 范围配置有两种类型：HgtxRangeStart/End and HgtxRangePush/Pop，两种类型的配置语法介绍如下。

+ **Start-End Ranges**

| Quantifier | Description | Example |
| --- | --- | --- |
| , | Delimiter between range names | Range A,Range B<br/>Range B,Range A,Range C |
| @ | Specify domain name. If not mentioned, assuming <default domain> | Domain A@Range A<br/>Domain B@Range B,Range Z |

`acu --hgtx --hgtx-include "Domain A@Range A" hgtx_filtering_test`

在 Domain A@Range A 范围内的 kernel 会被采样。

`acu --hgtx --hgtx-include "Range A,Range B" hgtx_filtering_test`

同时在 Range A 和 Range B 范围内的 kernel 会被采样。

`acu --hgtx --hgtx-include "Range A" --hgtx-include "Range B" hgtx_filtering_test`

在 Range A 或者在 Range B 范围内的 kernel 会被采样。

`acu --hgtx --hgtx-exclude "Range A" hgtx_filtering_test`

除了 Range A 范围内的 kernel 都会被采样。

`acu --hgtx --hgtx-include "Range B" --hgtx-exclude "Range A" hgtx_filtering_test`

在 Range B 范围内，但不在 Range A 范围内的 kernel 会被采样。

+ **Push-Pop Ranges**

| Quantifier | Description | Example |
| --- | --- | --- |
| / | Delimiter between range names | Range A/Range B<br/>Range A/*/Range B<br/>Range A/ |
| [ | Range is at the bottom of the stack | [Range A<br/>[Range A/+/Range Z |
| ] | Range is at the top of the stack | Range Z]<br/>Range C/*/Range Z] |
| + | Only one range between the two other ranges | Range B/+/Range D |
| * | Zero or more range(s) between the two other ranges | Range B/*/Range Z |
| @ | Specify domain name. If not mentioned, assuming <default domain> | Domain A@Range A<br/>Domain B@Range A/*/Range Z] |

`acu --hgtx --hgtx-include "Domain A@Range A/" hgtx_filtering_test`

在 Domain A@Range A 范围内的 kernel 会被采样。

`acu --hgtx --hgtx-include "[Range A" hgtx_filtering_test`

在 Range A 范围内，同时 Range A 为栈底的 kernel 会被采样。

`acu --hgtx --hgtx-include "Range A/*/Range B" hgtx_filtering_test`

同时在 Range A 和 Range B 范围内，并且 Range A 和 Range B 之间有 0 个或多个 Range 的 kernel 会被采样。

`acu --hgtx --hgtx-exclude "Range A/*/Range B" hgtx_filtering_test`

除了同时在 Range A 和 Range B 范围内，并且 Range A 和 Range B 之间有 0 个或多个 Range 的 kernel 都不会被采样。

`acu --hgtx --hgtx-include "Range A/" --hgtx-exclude "Range B]" hgtx_filtering_test`

在 Range A 范围内，但不在以 Range B 为栈顶范围内的 kernel 会被采样。

+ **其他配置**

`--hgtx-include DomainA@RangeA,DomainB@RangeB // 无效的配置`

单个 HGTX 配置，多个 Range 只需要指定一个 Domain。不支持同一个 HGTX 配置里有不同的 Domain。

`--hgtx-include "Range A\[i\]"`

名字中的限定符'@' ',' '[' ']' '/' '*' '+' 可以被'\'转义。'Range A\[i\]'是指名字为'Range A[i]'的范围。

`--hgtx-include "Range A"  // Start/End 配置`

`--hgtx-include "Range A/" // Push/Pop 配置`

`--hgtx-include "Range A]" // Push/Pop 配置`

如果名字里包含'\'，需要使用'\\\\'，同时在限定符前不要使用'\\\\'。

包含或排除单个 Push/Pop 配置内，在结尾处使用'/'，不要使用'['或']'。

`--hgtx-include "Range A/*/RangeB"`

Push/Pop 配置中的顺序很重要，示例中 Range A 在 Range B 的下面。

#### 4.2.8. acu 支持使用多实例运行
acu 支持以多实例的方式启动，可以在同一个 terminal session/(Docker container）内启动多个 acu 来做采集，每个 acu 独立输出不同的报告，此方式可以使用在`mpirun`命令上。

由于 acu 的采集只能工作在一个 PPU 设备上， 当有多个 acu 实例在运行时，需要用户保证每个 acu 实例中的目标应用程序独占一个 PPU 设备。如果 acu 在采集时，发现当前的采集设备有其它应用也在使用，会有如下的日志信息输出：

```bash
The application running on the device[0], may affect the metrics results of profiling.
   Running application list: xxxxxxxxxx 
```

如果出现以上错误信息，当前 acu 的采集会继续，但采集到的数据可能是错误的，有可能包含了其它应用中运行的 kernel 数据。

使用 `mpirun`命令来做 acu 采集有两种方式，分别为：

- mpirun 放到 acu 后面，做为目标应用来启动，命令格式如下：

` acu -o your_report mpirun -np 8 <your_target_application>`

此方式只有一个 acu 实例被启动，但是 mpirun 可能会 fork 出多个应用进程，此方式下，所有 fork 出的进程中的 kernel 数据都会被采集，且合并输出到一个报告文件中。

- mpirun 放到 acu 前面，acu 做为 mpirun 的启动程序来启动，命令格式如下：

`mpirun -np 8 acu -o mpi_report_%p <your_target_application>`

此方式下，会有 8 个 acu 实例被启动，每一个 acu 实例会启动一个`<your_target_application>`进程做 profiling。最后输出 8 份报告

> **注意：** 此命令组合方式仅适用于 kernel replay 与 range replay 两个模式下，目标应用中不能有 pccl API。
> 以上命令中，acu 有个关键参数：
> -o： 此处使用通配符 %p，%p 代表使用`<your_target_application>` 的 pid 来替换，以保证每个 acu 实例输出的报告名不重复，以避免重名报告造成的互相覆盖。 更多的通配符可以查看 acu --help 中的 -o，--export 一项的说明

#### 4.2.9. Cache Control
| cache-control 可选值 | 策略描述 |
| --- | --- |
| none | 默认值。在 profiling 过程中仅刷新 L1 与 L2 两级 PPU 缓存。<br/>如果仅仅是单个 kernel replay 来收集 metrics 时，该模式下可以提高性能并可以更好地重现应用程序行为和 metrics 结果。</br>但是，某些 metrics 结果将取决于之前的 PPU 工作以及多次 replay 之间的差异，这样的话可能导致 metrics 值的波动。 |
| all | 在 profiling 过程中，在每次 kernel replay 之前刷新所有 PPU 缓存，包含 LLC 缓存。<br/>在这种没有无效的缓存的情况下，虽然应用程序的执行环境中的 metrics 值可能略有不同，</br>但可以在 replay 过程中以及在目标应用程序的多次 profiling 运行之间稳定重现 metrics 结果。 |

 在 Kernel Replay 时，可能需要多次 replay kernel 以便收集所有请求的 metrics。虽然 Asight Compute 的 checkpoint 可以保存和恢复由 kernel 访问的 PPU 设备的内存数据，但是无法做保存和恢复 L1、L2 以及 LLC 缓存数据。因为缓存可能已经被 kernel 最近一次访问的数据给填充了。同样，第一次 replay 收集的硬件 perf counter 值可能取决于在 profiling kernel launch 之前执行了哪些 kernel，这些因素都可能导致后续 replay 过程的性能比第一次 replay 时更好或更差。

为了使硬件 perf counter 值采集时更加稳定准确，Asight Compute 提供了`--cache-control all`参数，让用户可以在每次 replay kernel 之前刷新所有 PPU 缓存。因此，在每次 replay 中，kernel 将可以访问一个干净的缓存，行为就好像 kernel 是在完全隔离的状态下执行的一样。

但这种模式下的行为也存在副作用，特别是在 profiling 较大应用程序执行中的某一个 kernel，且收集的数据针对缓存为重点的 metrics，可能会不利于性能分析。这种情况下，用户就需要考虑使用` --cache-control none` 来关闭工具对任何硬件缓存的刷新。

同样，在 Application Replay 中，由于 kernel 访问的内存无需通过 checkpoint 进行保存和恢复，所以每次 kernel launch 只会在应用程序进程的生命周期中执行一次。所以 Application Replay 也是可以通过`--cache-control none` 来关闭工具对任何硬件缓存的刷新。除非说应用程序需要在特定 kernel launch 之前，达到干净缓存的状态，那我们也可以通过设置 cache control 来实现。

#### 4.2.10. Clock Control
此功能用于控制性能分析过程中 PPU 时钟的行为。

对于许多 metrics 来说，它们的值直接受到当前 PPU CU 和内存时钟频率的影响。比如下面场景，

+ 如果分析的 Kernel 在应用程序中有其他 Kernel 在它之前执行，则 PPU 可能已经处于较高的时钟频率，导致 kernel 的执行时间和其他一些 metrics 将会受到影响。
+ 如果 Kernel 是应用程序中启动的第一个 Kernel，PPU 时钟频率通常会较低。
+ 由于 acu 会进行 kernel replay，metrics 的值可能会受采集它的 pass 的影响，因为后面的 pass 将导致更高的时钟频率。

为了减轻这种不确定性，acu 尝试将 PPU 时钟频率限制为其基本值（通过 `--clock-control base`）。这样，metrics 的值受 Kernel 在应用程序中的位置，以及所在 pass 的影响就会小很多。

然而，在某些场景下，用户可能不需要将时钟频率固定到基本值。比如，用户已经使用外部工具（ppu-smi 等）固定了时钟频率。为了解决这个问题，用户可以通过设置`--clock-control none`选项来指定 acu 不固定任何时钟频率。

| clock-control 可选值 | 描述 |
| --- | --- |
| base | 在性能分析期间，CU 和内存时钟被锁定到各自的基本频率。 当前 CU 的 base clock 为 900MHz。 |
| none | 默认值<br/>在性能分析期间，acu 不会更改 CU 或内存频率。 |
| reset | 重置所有或所选设备（通过--devices 指定设备）的 CU 和内存时钟，然后退出。 如果由于 acu 意外退出导致 PPU 时钟处于锁定状态，请使用此选项。 |

> **注意：**
> + 热调节（thermal throttling）会导致 PPU 时钟频率发生变化，该行为无法由 acu 控制
> + clock-control 的行为需要 sudo 权限，否则会中断性能分析，并提示权限警告
> + 在采用--clock-control base 时，acu 会在应用程序结束时，reset PPU clocks，并不会回退到开始性能分析前的 clocks（比如通过 ppu-smi 设定的 clocks）

<a id="cxBZo"></a>

### 4.3. Warp Sampling
Warp Sampling 功能支持对 warp 调度器的状态进行周期性采样。在固定的周期间隔内，每个采样器会选择一个 active warp，并输出指令的 PC 地址和对应的 warp 调度状态。

acu 默认开启 Warp Sampling 功能。所以，通过 GUI 工具打开 report，就可以查看采样数据。

#### 4.3.1. GUI 展示
Warp Sampling 的采样数据会分别在`Details Page`和`Source Page`展示

##### 4.3.1.1. Details Page
在`Details Page`的`Source Counters` section 中，`Warp Stall Sampling`表会展示 5 条计数最高的 stall reason 数据，其中 All Samples 表显示的是 issued+not issued 的数据，Not Issued 表显示的只是 not issued 的数据，表格由以下信息组成：

+ 源码位置
+ stall reason 计数
+ stall reason 占比

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124992480/91b99a7ab0f4d47721783607c2f1de13/details_page_1.png)

详细的 stall reason，请参考：[warp stall reason 介绍](#Sulms)

<a id="dczXQ"></a>

##### 4.3.1.2. Source Page
在`Source Page`，会以柱状图的形式展示 stall reason 数据，`Source View`和`PASM View`都会逐行展示当前代码行（或指令）对应的所有 stall reason 的数值和总和数值。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125024158/834ab07a5d5cec09d97d9d5ff5f195d7/source_page_1.png)

#### 4.3.2. 指定采样周期间隔
采样周期间隔可以由用户指定。如果在采样过程中发现采样的数据很少，以致无法进行有效分析时，可以通过`--warp-sampling-interval`设置更小的采样周期间隔。

+ 最小的采样周期不低于 128 cycles（2^7），而最大的不得高于 65536 cycles（2^16），不满足要求的采样周期将不会设置成功。
+ `--warp-sampling-interval`在[0..9]范围内取值。实际采样周期为 2 ^ (7 + `选取值`）cycles。
+ 如果设置为`auto`（默认），则会基于当前环境配置自动选择最高采样频率，以避免采样数据过少，或者缓冲区溢出情况的发生。

举例：设置采样周期间隔为 256 cycles 进行 warp sampling 采样

```bash
acu --warp-sampling-interval 1 -o cuda_test  ./cuda_test
```

举例：设置自动选择最高采样频率进行 warp sampling

```bash
acu --warp-sampling-interval auto -o cuda_test  ./cuda_test
```

<a id="ZRHVb"></a>

### 4.4. 指令统计
指令统计功能可统计 kernel function、device function 等函数的指令执行信息。该功能默认开启。要关闭指令统计功能，需要在启动 acu 之前，设置环境变量：`export ASIGHT_FEATURE_INSTRUCTION_COUNT=0`。

除了 graph（也即`--graph-profiling graph`场景下），指令统计支持在所有 replay 模式下，对 kernel 或者 range 进行 profiling。

| Workload Type | Instruction Level Source |
| :---: | :---: |
| Kernel | 支持 |
| Range | 支持 |
| Graph | 不支持 |

acu 增加一个单独的 pass，用于收集指令执行信息以及解析 function 的汇编指令。指令统计功能会在采集过程中，收集每条指令执行的 warp 次数，以及每条指令执行的线程次数。指令统计信息会以不同的形式在 GUI 工具内展示

#### 4.4.1. Source Page 展示
GUI 打开包含指令统计信息的报告，切换到`Source Page`，可以看到`Source View`和`PASM View`里都有`Instructions Executed`和`Thread Instructions Executed`两列数据。

+ `Instructions Executed：`统计每个独立 warp 中指令执行的次数，与每个 warp 内参与的线程数量无关。
+ `Thread Instructions Executed：`统计指令被所有线程执行的次数。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125024457/129531f0a682dda98b048ec175d729bb/source_page_2.png)

另外，有了指令统计功能，GUI 还可以展示 kernel function 调用的 device function 的汇编指令信息和源码关联信息，详情请看：[Source Page](#dczXQ)：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125027523/8ec99cf7e80e7b70f79e18981b9cfe86/thread_instructions_executed_1.png)

#### 4.4.2. Details Page 展示
在`Details`页面的`Instruction Statistics Section`下，新增柱状图用于显示指令执行的分布，详情请查看： [Executed Instruction Mix Bar Chart](#nHvrY)：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125020429/4109eb3eb9750ff73a346a5d2af5508a/source_counters_section_1.png)

在`Details`页面的`Source Counters Section`下新增了 Most Instruction Executed 与 Most Thread Instruction Executed 信息的展示，详情请查看：[Source Counter Section](#PoDoS)：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125020805/8506bd46ec9cd2b8771d6f3677f6a178/source_counters_section_2.png)

<a id="XOXk5"></a>

## 5. Asight Compute GUI 分析

通过 acu 命令行工具在 Target 端生成 `.acurep` 报告文件之后，可以将其拷贝到 Host 端，通过 Asight Compute GUI 工具打开并进行可视化分析。

**UI 功能亮点：**

+ 通过配置各种 metric 性能指标，进行多样化的展示（表格、图表等）。
+ 支持详细的 Memory Workload 结构层次图和表格的展示。
+ 通过 Baselines 功能，在不同的 Kernel 与报告之间，可以直接比较性能结果来定位差异。
+ Raw Page 提供 pdf/png/csv 格式文件的导出，可通过 export csv 导出相关格式的原始报告数据，进行后处理分析。
+ 利用 Project Explorer 可方便管理报告，支持批量打开和删除选定的报告。
+ 支持 Dock Widget，可以将报告拖出主窗口，方便在不同的窗口和屏幕查看报告，如下图所示。

可以通过拖拽 tab 的方式实现 dock: 

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124990300/272628444a622f25fe43a968326740f0/baselines_kernel_1.png)

还可以通过右键菜单中的 Detach/Attach 选项：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124992808/283aae2f4ddef938d8a103605a3323ed/details_page_2.png)

### 5.1. Details Page
Details Page 是 kernel 启动期间采集的所有 metrics 数据的主页面。它被分成单独的 section 进行展示。每个 section 都有一个 header table 来展示该 section 主题包含的主要 metrics。section 通常还有至少一个可展开/折叠的 section body，body 中以表格或图表的形式展示了更详细的 metrics。如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124993151/28f5f5b5df6105129a9a70eae59967cf/details_page_3.png)

1. 展开/折叠 section body
2. section 描述
3. header table
4. 切换 section body
5. section body
6. 专家建议

将鼠标悬停在表格或图表上会详细显示该 metrics 的具体数值和详细信息，以及相关的名词解释，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124993654/20ceb2d408af7581f30ba353fbb86dbe/details_page_4.png)

点击 tooltip 中的标题，可以跳转至 Metrics Details 页面，可以查看该 metric 的详细信息。

对于部分 section，会在 section 的下方显示当前 kernel 可能的瓶颈以及优化建议：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124993921/210cb6b330af327276e46bcf4c9b6c07/details_page_5.png)

除了内置的标准 rule 外，Asight Compute 还支持通过修改 py 文件自定义 rule，具体请参见[Rule 系统](#QrQtD)。

Details Page 提供了多种主题的 section，涵盖计算负载，缓存命中，以及 Warp 调度等多个维度，通过分析这些 metrics，可以全方位地查探 kernel 的运行情况，找出瓶颈和优化点。

以下分别介绍每个 section。

#### 5.1.1. Speed Of Light Throughput Section
该 section 提供了 kernel 运行过程中 PPU 的计算资源和内存资源利用率的概览，分别从计算和访存的角度展示了该 kernel 吞吐量相对于理论值的百分比。对 kernel 的分析工作通常从该 section 开始，来确定该 kernel 的性能受限于计算还是访存。

对于带有 throughput 字样的 metrics，可以在 Metric Details 页面查看 throughput 的 breakdown 信息

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125024993/dc8d36d8a23e9b1a7853ab8842b70b97/speed_of_light_throughput_section_1.png)

##### 5.1.1.1. Header Table

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125025280/a6de86122af29da11a214ff3ce350352/speed_of_light_throughput_section_2.png)

Header table 展示了 PPU 各单元吞吐的利用率以及 kernel 执行的周期数等总览信息，具体含义如下：

| 项目 | 详细信息 |
| --- | --- |
| Compute (CU) Throughput | 计算单元的整体吞吐利用率 |
| Memory Throughput | 内存单元的整体吞吐利用率 |
| L1 Cache Throughput | L1 缓存的吞吐利用率 |
| L2 Cache Throughput | L2 缓存的吞吐利用率 |
| LLC Cache Throughput | LLC 缓存的吞吐利用率 |
| DRAM Throughput | DRAM 的吞吐利用率 |
| Duration | kernel 执行的耗时 |
| Elapsed Cycles | kernel 执行过程中 PPU 经历的周期数 |
| Active Cycles | kernel 执行过程中 PPU 活动的周期数 |
| CU Active Cycles | kernel 执行过程中 CU 活动的周期数 |
| CE Frequency | CE 的运行频率 |
| DRAM Frequency | DRAM 的运行频率 |

##### 5.1.1.2. PPU Throughput Bar Chart

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124990903/cedeae89abed44b924285965d8361925/compute_cu_throughput_1.png)

Bar Chart 中分别显示了计算和内存单元的吞吐百分比，两个 category 分别对应 header table 中的`Compute (CU) Throughput`和`Memory Throughput`。

通过图表可以容易看出 kernel 的性能是受限于计算还是访存，并采取不同的优化策略。通常根据性能瓶颈，kernel 可以分为以下三种类型：

###### 5.1.1.2.1. 计算受限型 kernel
当一个 kernel 使得 PPU 的某个计算单元吞吐接近理论最大值时（通常大于 80%），kernel 的性能受限于该类型的计算单元，称其为计算受限型 kernel，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124991229/3cdd49a8b2c8799c68d12a57c8a8351b/compute_cu_throughput_2.png)

计算受限型 kernel 的计算指令远多于访存，要进一步提升性能，可以查看 Compute Workload Analysis section，找出利用率最高的计算单元 pipeline：

+ 考虑将该种类型的计算转换为其他类型
+ 检查是否有多余计算，减少计算量
+ 利用查找表代替计算

###### 5.1.1.2.2. 访存受限型 kernel
当一个 kernel 使得 PPU 的某个内存单元吞吐接近理论最大值时（通常大于 80%），kernel 的性能受限于访存，称其为访存受限型 kernel，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125025604/56fd36f7e0b2ea250f41b8acd095acfc/speed_of_light_throughput_section_3.png)

访存受限型 kernel 运行时多数时间都在等待数据，要进一步提升性能，可以查看 Memory Workload Analysis section，优化各种内存子系统的使用：

+ 确保合并访问 global memory
+ 充分利用各层次内存，如共享内存，各层次 cache
+ 充分复用数据，减少访存指令
+ 利用实时计算代替查找表

###### 5.1.1.2.3. 延迟受限型 kernel
当一个 kernel 在计算和访存都无法接近理论峰值时，称该 kernel 为延迟受限型，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125025888/697ed7b4a7fbf6733e77c8c22848305d/speed_of_light_throughput_section_4.png)

对于延迟受限型 kernel，首先应该通过 Launch Statistics section 查看 kernel 的启动配置，确保 grid 足够大；另一方面查看

Scheduler Statistics section 和 Warp State Statistics section，检查是否有其他潜在原因导致每个线程多数时间都在等待而不是执行。

要提升延迟受限型 kernel 的性能：

+ 确保有足够多的 block 填满 PPU，争取实现最大的占有率
+ 增加每个线程的工作量，例如每个线程处理多个输入元素

##### 5.1.1.3. Breakdown Tables
Breakdown Tables 分为两种，分别展示了 PPU 计算和内存各个单元的吞吐百分比，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125026271/d6f84693e4845b6b3edc5c519793bbfd/speed_of_light_throughput_section_5.png)

在 breakdown table 中，展示了当前子系统所有单元的吞吐百分比，并按照降序排列，可以方便地查看当前 kernel 具体受限于哪个单元。将最繁忙单元的吞吐率视为当前子系统的吞吐率，并在 bar chart 中展示。

##### 5.1.1.4. Roofline Chart
Kernel 需要数据来进行计算，因此其性能不仅取决于 PPU 的计算速度，还取决于 PPU 向 kernel 提供数据的速度。为了更直观地表示 kernel 所达到的性能，Asight Compute 提供了 roofline chart，将 PPU 的峰值计算性能和多级缓存以及内存带宽与一个叫做 "算术强度 "的指标（工作和内存流量之间的比值）结合到一个图表中，一个典型的 roofline chart 如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125026618/c172eee697348367c1822a2a6e5fad73/speed_of_light_throughput_section_6.png)

+ 纵坐标轴：纵坐标轴代表每秒浮点运算数（FLOPS），对于 PPU 而言这个数值会非常大，为了方便展示，坐标轴刻度以对数的方式呈现。
+ 横坐标轴：横坐标轴代表“算术强度”，是工作（FLOP/s）和内存流量（byte/s）之间的比值，其单位是 FLOP/byte。坐标轴刻度也以对数的方式呈现。
+ 内存带宽边界：是 roofline 的斜线部分，这个值由 PPU 的内存带宽决定。斜率表示在对应计算强度下需要的内存带宽上限。
+ 峰值性能边界：是 roofline 的水平部分，这个值由 PPU 的峰值计算性能决定。它代表设备的算力上限。
+ 屋脊点：屋脊点是内存带宽边界与峰值性能边界的结合点。可参考该点分析 kernel 性能。
+ 性能达到值：代表了 kernel 在当前算术强度下达到的性能。进行 baseline 比对时，也会显示 baseline 的性能值，该点的轮廓颜色代表了它是来自哪条 baseline。

利用 roofline chart 可以直观地判断一个 kernel 是计算受限型还是访存受限型，以 DRAM roofline 为例：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125019012/684bab764cc8f98c08b3a05894e4d855/roofline_1.png)

在上图中，屋脊点将 roofline 分为了两个区域：内存带宽边界下的蓝色阴影区域是访存受限区域；峰值性能边界下的绿色阴影区域是计算受限区域。

根据 kernel 性能实现值所处的位置，可以判断 kernel 的性能限制因素。性能实现值到上方边界的距离（上图中为白色虚线），代表了性能优化的空间。实现值越接近上方边界，kernel 性能越好。当一个 kernel 的实现值位于内存带宽边界时，只有增加算术强度才能进一步提高性能。

为方便查看，roofline chart 支持缩放平移操作：

+ 放大：
    - Ctrl + 鼠标滚轮
    - 鼠标左键框选放大
    - 点击右上角的放大按钮
    - 键盘“+”
+ 缩小：
    - Ctrl + 鼠标滚轮
    - 鼠标右键单击
    - 点击右上角的缩小按钮
    - 键盘“-”
+ 复位：
    - 点击右上角的复位按钮
    - 键盘“Esc”
+ 平移
    - Ctrl + 鼠标左键拖拽

**比赛关联：** Speed Of Light 与 Roofline 图可直接判定 Qwen3.5-2B 中各 kernel 的瓶颈类型：prefill 的 GEMM 通常计算受限（看 tensor pipe 利用率），decode 阶段多受访存带宽限制（看 DRAM Throughput），量化（INT8/FP8）收益可通过优化前后 DRAM 吞吐与算术强度变化量化论证。

#### 5.1.2. Compute Workload Analysis Section
Compute Workload Analysis Section 详细展示 PPU 计算单元的各种计算资源的性能数据，包含两类信息：

+ Instructions Per Clock（IPC）：统计 CU 每一个周期的指令发出情况
+ Pipe Utilization：CU 各类 pipeline 的利用率

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125002682/a7b947bf6ec4eb2cd7e521446f8ed96c/instructions_per_clock_1.png)

##### 5.1.2.1. Header Table

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125002914/a70bb0b8ba66bb063f586346fd2e7416/instructions_per_clock_2.png)

Header table 展示了 CU 利用率以及 kernel 执行过程中每活动周期执行的指令数等关键信息，具体含义如下：

| 项目 | 详细信息 |
| --- | --- |
| Executed Ipc Elapsed | CU 经过的周期内，每周期执行的指令数 |
| Executed Ipc Active | CU 活动的周期内，每周期执行的指令数 |
| Issued Ipc Active | CU 活动的周期内，每周期发出的指令数 |
| CU Busy | CU 的利用率 |
| Issue Slots Busy | 指令发射槽的利用率 |

##### 5.1.2.2. Pipe Utilization Bar Chart

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124991595/42fc3c42048318f1aae13c02ae069a34/compute_workload_analysis_section_1.png)

Pipe Utilization Bar Chart 展示了 kernel 执行过程中 PPU 各计算 pipe 的利用率，常用的 Pipeline 信息如下：

| pipe 名称 | 描述 |
| :--- | :--- |
| salu | 标量算术逻辑单元 |
| valu | 矢量算术逻辑单元，包括 ialu 和 falu 两种 |
| ialu | 整型算术逻辑单元 |
| falu | 浮点型算术逻辑单元 |
| sls | 标量加载/存储单元 |
| sfu | 特殊函数单元 |
| tensor | 张量计算单元 |
| lsu | 矢量加载/存储单元 |
| ffma | FP32 积和熔加运算 |
| fadd | FP32 加法运算 |
| fmul | FP32 乘法运算 |
| hfma | FP16 积和熔加运算 |
| hadd | FP16 加法运算 |
| hmul | FP16 乘法运算 |

当所有的计算 pipe 的利用率都较低时（通常小于 60%），可能当前 kernel 的启动配置过小，或者 warp scheduler 上没有足够的 warp 可供调度，可以查看 Launch Statistics section 和 Scheduler Statistics section 获取详细信息。

当某一个计算单元的 pipe 利用率过高时（通常大于 80%），该 pipe 可能是性能瓶颈，可以考虑平衡各 pipe 的利用率以提升性能。

#### 5.1.3. Memory Workload Analysis Section
Memory Workload Analysis section 详细展示了 PPU 各内存单元的性能数据。当 PPU 各内存单元被充分利用时，访存可能成为 kernel 的性能瓶颈，这可能是由于内存单元的利用率过高，内存带宽被耗尽，或者发出访存指令的吞吐量达到最大等。该 section 有两个 section body：

+ Memory Chart
+ Memory Table

##### 5.1.3.1. Header Table

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125010032/4dd95b8d13c74acf772e2974ff4c1072/memory_chart_1.png)

Header table 展示了 PPU 各内存单元的利用信息，如 cache 命中率，达到的带宽，访存 pipe 利用率等信息，具体含义如下：

| 项目 | 详细信息 |
| --- | --- |
| Memory Throughput | DRAM 吞吐量，单位为 byte/second |
| Mem Busy | 访存吞吐利用率 |
| KVD Hit Rate | Vector Data Cache 命中率 |
| KSD Hit Rate  | Scalar Data Cache 命中率 |
| Max Bandwidth | 最大访存带宽利用率 |
| L2 Hit Rate | L2 Cache 命中率 |
| LLC Hit Rate | Last Level Cache 命中率 |
| Mem Pipes Busy | 访存 pipe 利用率 |

##### 5.1.3.2. Memory Chart

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125010372/b145adaf4d75d2b0b7156d34531af9f2/memory_workload_analysis_section_1.png)

Memory Chart 可视化展示各内存单元间的数据传输情况，包括 cache 命中率，instruction 数，以及 memory request 数等：

+ 逻辑单元（绿色部分），包括
    - Kernel：PPU 上执行的 kernel
    - Global：HGGC global memory
    - Shared：HGGC shared memory
    - Load Global Store Shared：指令直接从 global memory load 到 shared memory
+ 物理单元（蓝色部分），包括：
    - L1 cache：包括 KSD，KVD，TSM 等单元
    - L2 cache
    - LLC cache
    - System Memory：system（CPU）memory
    - Device Memory：device（PPU） memory
    - Peer Memory：其他 PPU 设备上的 memory
+ 链接
    - Kernel 与其他逻辑单元之间的链接，代表各逻辑单元执行的指令的数量。例如 Kernel 和 Global 之间的链接表示全局内存空间的加载/存储的指令数量
    - 逻辑单元和物理单元之间的链接代表了由于相关指令而发出的请求（Req）的数量
    - 物理单元之间的连接代表了各单元间传输的数据量
    - 连接的箭头代表数据传输的方向，颜色代表了该链路的利用率百分比，右侧的图例代表了从 0%到 100%之间不同利用率的颜色。某些链路共享同一个数据端口，在图表中，端口用带颜色的梯形表示，其颜色代表了该端口的利用率
    - 鼠标悬停在箭头上时，内存传输的箭头将高亮显示，同时对应的利用率图例标记也会同步高亮，便于查看该传输路径的利用率
+ 可以通过右上角的组合框切换 transfer size 和 throughput 显示

##### 5.1.3.3. Memory Table

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125028171/611a6b652feeae7efaf77e235bba5e15/transfer_size_throughput_1.png)

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125028469/15da2bf03a34c58c142c50f2f5d7ea24/transfer_size_throughput_2.png)

Memory table 展示了各种内存单元的详细指标，例如 shared memory，cache，和 device memory 等。将鼠标悬停在表格条目上时，可以查看具体的 metrics 和详细信息。

#### 5.1.4. Scheduler Statistics Section
Scheduler Statistics section 展示了 warp scheduler 的 warp 调度情况，每个 warp scheduler 维护一个 warp 池，可以为其中的 warp 发出指令。warp 池的大小受 kernel 启动配置的限制，最多 16 个 warp。每个周期，warp scheduler 都会检查每个 warp 的状态。根据 warp 状态的不同，将 warp 分为以下 4 类：

+ Active Warp：一个 warp 只要可以被 warp scheduler 调度，就处于 Active 状态，直到 warp 执行完最后一条指令
+ Eligible Warp：可以发射下一条指令的 warp，比如某个计算指令所需的数据都已就绪
+ Stalled Warp：由于各种原因而不能发射下一条指令的 warp，比如等待 barrier，等待上一条指令的执行结果等
+ Selected Warp：被选中执行下一条指令的 eligible warp

下图展示了各状态 warp 的关系：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124995705/1281f49f027e761b881299f56a3fbd43/eligible_warps_1.png)

由上图可知，active 的 warp 个数不会超过理论 active warp 个数，即`Device Limit` >= `Theoretical Active Warps` >= `Active Warps`

根据是否可以发射下一条指令，active warp 被分为 stalled warp 和 eligible warp，即`Active Warps `= `Stalled Warps` + `Eligible Warps`

每个周期，warp scheduler 会从 eligible warps 选择一个 warp 发射下一条指令，在没有 eligible warp 的周期中，不发出任何指令，影响 kernel 性能。

##### 5.1.4.1. Header Table

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124995464/5787b438b218b4cf0d605bb165ea9fc6/device_limit_1.png)

Header table 展示了 warp scheduler 的指令发出情况，具体含义如下：

| 项目 | 详细信息 |
| :--- | :--- |
| Active Warps Per Scheduler | 每个周期，平均每个 warp scheduler 中的 active warps 数量，取值范围：[0, 16] |
| Eligible Warps Per Warp Execution | 每个周期，平均每个 warp scheduler 中的 eligible warps 数量，小于`Active Warps Per Scheduler` |
| Issued Warps Per Scheduler | 每个周期，平均每个 warp scheduler 发射的 warp 个数，理想值为 1 |
| No Eligible | 是一个百分比，代表没有 eligible warps 的周期数占整个活动周期数的比例。没有 eligible warp 可用，warp scheduler 就不会发射指令 |
| One or More Eligible | 是一个百分比，代表至少有一个 eligible warps 的周期数占整个活动周期数的比例，理想值为 100%。<br/>`One or More Eligible` = 1 - `No Eligible` |

##### 5.1.4.2. Warps Per Scheduler Bar Chart

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124983282/1707ac8751f22ec484d8fa5b61caab6c/active_warps_per_scheduler_1.png)

Warps Per Scheduler bar chart 以柱状图的形式展示了每个周期，每个 warp scheduler 上平均各状态 warp 的数量。

理想情况下，每个周期，warp scheduler 可以发出一条指令，当`Issued Warps Per Scheduler`较低时（通常小于 0.6），说明 PPU 资源没有被很好地利用，导致 kernel 性能不佳。`Issued Warps Per Scheduler`数值较低的直接原因是 eligible warps 数量不足，要提升 kernel 性能，可以：

+ 查看 Occupancy section，确保 kernel 的高占有率，使其 theoretical active warps 的值为 16
+ 查看 Warp State Statistics section，找到最主要的 stall reason，减少 warp 花在该 stall reason 的时间，提高 eligible warps 数量
+ 避免因为负载不均衡导致的 warp 执行时间差异

#### 5.1.5. Warp State Statistics Section
Warp State Statistics section 展示了 kernel 执行过程中，warp 执行每条指令花费的平均周期数，这个周期数决定了执行两条指令之间的延迟，周期数越高，则需要更多的 warp 并行来隐藏延迟。Section 中还展示了在执行指令的周期中，active warps 的状态统计。Warp 状态描述了当前周期 warp 能否准备好发出下一条指令，以及相关的原因。

<a id="Sulms"></a>

##### 5.1.5.1. Warp Stall Reasons
PPU 将 active warps 的状态分为 15 种，如下表所示：

| Warp 状态 | 详细信息 |
| --- | --- |
| Instruction Fetch | 等待指令的获取。如果 kernel 的规模很小，不到一个完整的 wave，这种 stall 会比较常见；如果代码中有频繁的分支跳转，指令缓存命中率低，也会出现这种 stall |
| Compute Dependency | 等待其所依赖的上一条计算指令的完成 |
| Memory Dependency | 等待其所依赖的上一条访存指令的完成 |
| Memory Throttle | 因为 memory 指令队列满而 stall，这种 stall 在 memory 管道利用率很高时出现 |
| Not Selected | 等待 warp scheduler 调度。该状态下的 warp 属于 eligible warps，由于另一个 eligible warps 被 warp scheduler 选中，所以此 warp 的状态为 Not Selected，如果此状态下的 warp 数量很多，意味着有充足的 warp 来掩盖延迟 |
| Selected | 被 warp scheduler 选中，并发出了下一条指令。该状态下的 warp 属于 selected warp |
| Stall Pipe Busy | 因为相关的功能单元 pipe 繁忙而 stall |
| Stall Sleeping | 因为 warp 处于 sleep 状态而 stall |
| Stall Sync | 因为等待其他 warp 到达同步点而 stall。这种 stall 通常是因为在 barrier 之前的代码分支导致的，可能导致某些 warp 花费较长时间等待其他 warp。如果可能，尽量减少 block 内的代码分支。 |
| Stall SALU Control | 因为等待上一条 scalar 控制指令而 stall，或者 SCTL pipe 繁忙 |
| Stall SIMT Control | 因为等待上一条 SIMT 指令而 stall |
| Stall SREG Read | 因为等待 SREG 读取而 stall，或者 SREG port 繁忙 |
| Stall Fence Sys | 因为等待 fence.sys 指令而 stall |
| Stall AMC | 因为 AMC 电源管理而 stall |
| Stall Others | 因为其他硬件原因而 stall |

##### 5.1.5.2. Header Table

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125030137/377680fcddae1d5018881fb5e25ea7d6/warp_state_statistics_section_1.png)

Header table 中项目具体含义如下：

| 项目 | 详细信息 |
| --- | --- |
| Warp Cycles Per Issued Instruction | 对于每条发出的指令，warp 花费的平均周期数 |
| Warp Cycles Per Executed Instruction | 对于每条执行的指令，warp 花费的平均周期数 |
| Avg. Active Threads Per Warp | 平均每个 warp 活动的线程数，目前仅包含 valu 单元指令 |

执行每条发射指令的平均周期数（Cycles Per Issued Instruction，CPI），是衡量 kernel 性能的重要指标

##### 5.1.5.3. Warps Per Scheduler Bar Chart

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125030460/b187650f7ca56c8b1a7e5433cc18b923/warp_state_statistics_section_2.png)

Warps Per Scheduler bar chart 列出了所有的 warp stall reason，并按照降序排列。所有的 warp stall reason 周期加起来，再加 1（发射 cycle），等于`Warp Cycles Per Issued Instruction`。

Warp stall 是无法避免的，只有在 Warp State Statistics section 中`No Eligible`值较高时，才会考虑 warp stall reason。

#### 5.1.6. Instruction Statistics Section
本 section 可查看执行低级汇编指令（SASS）的相关统计信息。

##### 5.1.6.1. Header Table

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125014340/317c0b59f205cb0efcc4f8dd56ff880b/no_eligible_1.png)

Header table 中项目具体含义如下：

| 项目 | 详细信息 |
| --- | --- |
| Executed Instructions | kernel 执行过程中执行的指令数 |
| Issued Instructions | kernel 执行过程中发出的指令数 |
| Avg. Executed Instructions Per Scheduler | 平均每个 warp scheduler 执行的指令数 |
| Avg. Issued Instructions Per Scheduler | 平均每个 warp scheduler 发出的指令数 |

<a id="nHvrY"></a>

##### 5.1.6.2. Executed Instruction Mix Bar Chart

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125002290/bc84aa871389a505d4a9f2e9d5f4021e/instruction_statistics_section_1.png)

Executed Instruction Mix bar chart 列出了每个 kernel 执行的各项指令，并且按指令执行数降序排列。可以通过该 bar chart 查看 fused 指令（例如 fma）和 non-fused 指令（例如 add、mul）的数量，如果 non-fused 指令占比较高，可以考虑将其转变为 fused 指令以提高指令吞吐。

#### 5.1.7. ICN Link Section
本 section 可查看 ICN link 利用率的概况，包括接收和发送的总的内存大小、链路的峰值利用率等。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124998717/0f46ab7e7ffcec78ea895727fc1336ed/icnlink_section_1.png)

Header table 中项目具体含义如下：

| 项目 | 详细信息 |
| --- | --- |
| Received Bytes | 通过 ICN link 接收的数据大小 |
| Received Peak Utilization | ICN link 接收数据的峰值利用率 |
| Received Overhead Bytes | 通过 ICN link 接收的 overhead 数据大小 |
| Received User Bytes | 通过 ICN link 接收的 user 数据大小 |
| Transmitted Bytes | 通过 ICN link 发送的数据大小 |
| Transmitted Peak Utilization | ICN link 发送数据的峰值利用率 |
| Transmitted Overhead Bytes | 通过 ICN link 发送的 overhead 数据大小 |
| Transmitted User Bytes | 通过 ICN link 发送的 user 数据大小 |

拓扑图直观地展示了各个 device 的连接情况以及数据传输情况： 

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124999032/524da659008ace501503e9558dfe1224/icnlink_section_2.png)

属性表格展示了 ICN link 的属性，包括峰值带宽、物理连接数量等信息：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124999303/60b0b29fb6159b2dd56227f8356f4712/icnlink_section_3.png)

吞吐表格则展示了当前 range 执行时 ICN link 的吞吐、带宽利用率和空闲时间：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125000207/6238867218746415ec9868644396976d/icnlink_section_4.png)

#### 5.1.8. Launch Statistics Section
本 section 可查看执行本 kernel 时使用的配置信息，包括 grid size、block size 以及执行本 kernel 所需的 PPU 资源信息等。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125009485/5b917c97b5aff990530601e40bd37ce0/launch_statistics_section_1.png)

Header table 中项目具体含义如下：

| 项目 | 详细信息 |
| --- | --- |
| Grid Size | Grid 中 block 的数量 |
| Block Size | Block 中 thread 的数量 |
| Threads | Kernel 启动的总 thread 数，等于`Grid Size` * `Block Size` |
| Waves Per CU | 平均每个 CU 的 Wave 数量 |
| Registers Per Thread | 每个线程使用的寄存器数量 |
| Static Shared Memory Per Block | 每个 block 使用的静态分配的共享内存大小 |
| Dynamic Shared Memory Per Block | 每个 block 使用的动态分配的共享内存大小 |

Kernel 的启动配置直接影响占有率的大小，为保证 kernel 性能，考虑：

+ Warp 中有 32 个线程，`Block Size`应该为 32 的倍数
+ `Grid Size`应该远大于 CU 的数量，如果 block 的数量比 CU 小，会导致部分 CU 没有负载，考虑减少`Block Size`或者增加`Grid Size`
+ 通过`Waves Per CU`，判断是否有拖尾效应（Tail Effect）。PPU 上能够同时执行的 block 数被称为一个 wave，如果`Waves Per CU`的值不为整数，则说明 PPU 执行的最后一个 wave 不能填满 PPU，导致占有率降低，性能下降。考虑调整`Block Size`使得`Waves Per CU`的值接近整数

#### 5.1.9. Occupancy Section
Occupancy section 展示了 kernel 执行的占有率信息。占有率是一个 CU 上 active warp 数与最大可同时运行的 Warp 数的比值，当有足够多的 Warp 时，PPU 可以利用 Warp 的切换掩盖延迟，高占有率是 Kernel 高效执行的必要条件。目前每个 CU 上理论最大 active warp 数为 64 个。

一个 CU 上 active warp 数受到如下 3 个因素的限制：

+ Block 尺寸
+ 每个 Thread 使用的 Register 数量
+ 每个 Block 使用的 Shared Memory 尺寸

##### 5.1.9.1. Header Table

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125027859/89a632107baa3b6343efdcd19203e5f6/threadregister_1.png)

Header table 中项目具体含义如下：

| 项目 | 详细信息 |
| --- | --- |
| Theoretical Occupancy | 理论占有率，根据 kernel 的启动配置计算出来的理论值 |
| Theoretical Active Warps per CU | 理论每个 CU 上活动的 warp 数，根据 kernel 的启动配置计算出来的理论值 |
| Achieved Occupancy | 实际占有率，由于取的是各 CU 的平均值，可能与理论值有差距 |
| Achieved Active Warps Per CU | 实际每个 CU 上活动的 warp 数，由于取的是各 CU 的平均值，可能与理论值有差距 |
| Block Limit Registers | 当前寄存器数量限制下，每个 CU 上 block 的最大数量 |
| Block Limit Shared Mem | 当前共享内存尺寸限制下，每个 CU 上 block 的最大数量 |
| Block Limit Warps | 在 active warp 数量最大为 64 的限制下，每个 CU 上 block 的最大数量 |
| Block Limit CU | 在 CU 上管理的最大 block 数的限制下，每个 CU 上 block 的最大数量 |

##### 5.1.9.2. Occupancy Line Chart
Occupancy Section 以 3 个折线图分别反映了上述 3 个条件对 Occupancy 值的影响。折线图的横坐标表示某条件的理论取值上限，纵坐标表示在其余 2 个条件的值固定为实际值时，该条件对应的 Occupancy 的理论值。折线上的圆点表示当前实际值，将鼠标悬停在点上可以查看具体值。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125015437/4f6edd8aaa317d45559042d77dd840fc/occupancy_section_1.png)

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125015720/968aacd4b524ba444a43dd8c7b32c9d8/occupancy_section_2.png)

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125016015/1ea78ff3fe5cc94e15b842d2e980d848/occupancy_section_3.png)

<a id="PoDoS"></a>

#### 5.1.10. Source Counters Section
Source Counters section 可以辅助找到 kernel 代码中的性能问题。此 section 提供 3 个表格，每个表格分别显示当前 kernel 的所有汇编代码行中，指定 metric（all stall reasons/not issued stall reasons/inst executed/ thread inst executed）值最高的几行，点击后可跳转至 source page 查看详情，方便用户快速定位到有性能瓶颈的代码：

+ Warp Stall Sampling (All Samples)
+ Warp Stall Sampling (Not Issued Samples)
+ Most Instructions Executed
+ Most Thread Instructions Executed

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125029847/6d4e50711beb5f57d081d2ed596bad7a/warp_stall_sampling_all_samples_1.png)

表格第一列为相关代码行的地址和所属 function 的名称，点击后可跳转到 Source Page 查看详情。

表格第二列为该行代码的 metric 的值。鼠标悬放到单元格，可以从 tooltip 查看该 metric 的构成情况，比如 Warp Stall Sampling 表，tooltip 为具体每个 stall reason 的值以及占比。

表格第三列为该行代码的 metric 值占所有行的 metric 总值的百分比。

### 5.2. Source Page
Source Page 主要是显示源代码与汇编代码之间的关联，同时还包括一些与源代码相关联的 metric 信息，包括通过[warp sampling](#cxBZo)采集的各种 stall reasons、通过[指令统计](#ZRHVb)得到的指令执行次数 metrics，以及默认采集的 live register metrics。鼠标悬放到这些 metric 的表头上可以查看 metric 的详细含义。

Source Page 支持汇编代码、C++/CUDA 代码、Python 代码的语法高亮。

如果应用程序通过`-G`或者`-lineinfo`编译配置参数进行编译，程序内部会附带 debug 信息，当解析报告时，可以将源代码与汇编进行关联。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125021106/2b47d40255a5eaa501a96b18b7d3d61a/source_counters_section_3.png)

可以在 Source and PASM 界面点击左侧源代码行，右侧汇编会高亮显示与之相关联的代码行。反之，右侧点击汇编，左侧源代码会高亮与之相关联的代码行。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125021463/b39bc3a491976f57f4748ef413581e46/source_counters_section_4.png)

Warp Stall Sampling (All Samples) metric 汇总了各种类型的 stall reasons，Warp Stall Sampling (Not Issued Samples) metric 汇总了 not issued 的各类型的 stall reasons，可以通过鼠标悬停，了解当前代码行对应的 stall reason 的汇总信息。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125021800/577c7faff8aafc0fd9153e5b7aa35b8c/source_counters_section_5.png)

当鼠标悬停在 Warp Stall Sampling 列时，会显示详细的 stall reason 信息：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125022150/0eef246e77c3d43319b95f90d38fcc24/source_counters_section_6.png)

Instruction Executed 以及 Thread Instruction Executed 汇总不同指令执行的 warp 数和 thread 数。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125022481/7e352fad6116b32bdb448fc31a4608d2/source_counters_section_7.png)

Vector Live Register 和 Scalar Live Register 表示每行代码用到的活跃 Vector 寄存器或 Scalar 寄存器的数量。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125022758/e7a8a215a049c4ecd239bee9642a336e/source_counters_section_8.png)

#### 5.2.1. 基本功能
**View 下拉菜单**

可以使用该下拉菜单，在`Source`，`PASM`以及`Source and PASM`这三个界面切换显示状态。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125020174/ebad70876bee55c90d8f4dee385981a2/source_and_pasm_1.png)

**Source 下拉菜单**

可以通过该下拉菜单，在不同 source code 之间切换显示。

对于源代码，source 是按文件名升序排序的；对于汇编代码，source 是按 function 地址升序排序的：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125019937/c76880a1860e3fcfe58d10d541f8d0d5/source_1.png)

> **备注：** 对于 Source View（源码）来说，source 即源码文件，对 PASM View（汇编码）来说，source 即 function。

**Metric 显示格式切换按钮**

提供 3 种 metric 显示样式调节按钮，对指令统计、stall reasons 类型的 metric 列生效：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125010689/3ac4187708ecb34a2b3c5b0959225ad4/metric_1.png)

-  相对值/绝对值按钮
    + 默认选相对值，metric 值以相对总值的百分比形式显示（总值是全局还是局部取决于第三个选项）

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125010911/83427cccbacb793a000b59fec595943e/metric_2.png)

-  数字缩写/原值按钮
    + 此选项仅当第一个选项选了绝对值时，才启用
    + 默认选缩写，比如 3670 为原值，3.67K 为缩写

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125029538/c4015710f44a1b0c6d2ac91eb772d925/warp_stall_1.png)

-  局部、全局范围按钮
    + 局部 指的是计算相对值时，分母是当前 source 的所有代码行的 metric 总值。
    + 全局 指的是计算相对值时，分母是所有 source 的代码行的 metric 总值
    + 默认选全局

例如下面的例子，该 kernel 源码总共有两个 source，saxpy.cu 和 vector_functions.hpp。对于 saxpy.cu 的某行代码，其 inst_executed 这个 metric 的值为 5，而 saxpy.cu 的所有代码行的 inst_executed 总值为 40，vector_functions.hpp 的所有代码行的 inst_executed 总值为 60。在局部+相对模式下，表格中显示的值为 5/40 = 12.5%；在全局+相对模式下，表格中显示的值为 5/100 = 5%；而在绝对模式中，局部/全局模式会被忽略，表格中直接显示原值 5。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125023906/1d86211a535cdbb7ea887f287eac6fb9/source_metric_2.png)

每次打开报告后，默认使用上述选项的默认值。在 Options 中可以改变前两种选项的默认值：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125024719/b7201e0872cd6f4cd5d2aeb3c5ea843c/source_page_basic_1.png)

在 Options 中修改这两项默认值不会在已打开的 source page 中生效。

**Find 栏**

界面提供了查找功能，当想要快速地查找 Source 中包含某个关键词的行时，可以键入关键词，所有匹配的搜索结果将会高亮为黄色，通过上下按钮查找上一条/下一条包含关键词的结果。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125013824/90105f1257fdb69c1cae9e499dfcbd95/navigation_1.png)

**Navigation 栏**

Navigation 栏是为了快速定位到指定 metric 有值的代码行上，并通过上下按钮进行上一条/下一条记录的切换。例如下图是通过向下按钮找到并选中了 saxpy.cu 中第一行有 Warp Stall Sampling (All Samples)值的一行。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125014109/641ce70177a7bdffd5e669f9f4b611b9/navigation_2.png)

**Metric 排序按钮**

Source Page metric 排序功能用于快速找到所有行中，指定 metric 的最大/次大/次小/最小的一行代码。例如希望找到某个 metric 最大的代码行，首先在 metric 下拉列表中选择相应的 metric，再点击选择最大按钮，就能找到最大的一行，若想找到更小的一行，则再点击选择次小按钮。

图中从左到右依次为选择最大/次大/次小/最小按钮。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125011234/0d64fc10a6332da0bd1649ab4f3cc4b5/metric_5.png)

**右键菜单**

Source Page 中的表格支持以下右键菜单功能：

+ Copy：复制选择的内容到剪贴板
+ Copy as CSV：以 CSV 格式复制选择的内容到剪贴板
+ Select All：选中表格的所有内容

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124991940/0cafff403fca3fa7c6661409444667a4/copy_as_csv_menu_1.png)

**点击分支指令跳转**

点击分支指令上的地址/偏移，可以跳转到目的指令所在行。比如对于图中的第 236 行指令，`s.cbr.az emsk, 0x2`，点击`0x2`会跳过当前行往下的 2 行汇编指令到达 239 行。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124995163/5619110fa5d622e68c7b7ee774173bc1/device_info_example_1.png)

**显示/隐藏指定列**

可以在表头的右键菜单中打开列选择器，定制显示感兴趣的列：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124997871/c90df8dec0bb19a815ccb7ec26d9c138/heatmap_1.png)

**代码行 Heatmap**

在滚动条的右侧会显示代码行的 heatmap，可以通过颜色深浅直观显示某列数据的分布，快速发现热点代码行：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124998147/08a483fea68342c932ac8536179b2968/heatmap_2.png)

可以通过 Navigation 组合框选择不同的列作为 heatmap 的数据源，heatmap 会根据当前视图自动适配。在 stall reason 的 heatmap 中，颜色越深，表示该行的性能开销越大；颜色越浅，表示该行对总体性能的影响越小。

#### 5.2.2. 导入源码

##### 5.2.2.1. 报告附带源码
acu 支持将源码采集到报告中，只需要在采集时把--import-source 选项设置为 yes/on，报告中就会包含 kernel 的源码。此选项默认关闭。

对于附带源码的报告，打开 Source Page 则会看到对应的源代码，无需手动导入。

##### 5.2.2.2. Resolve
默认情况下，报告中没有携带源码。打开 Source Page 时，1.工具会尝试在采集报告时源码所在的路径把源码导入，若导入失败，会提示当前源代码文件没有找到，需要点击 Resolve 来指定源代码目录。点击 Resolve 按钮后，Source Page 会 2.先尝试从 Source Lookup 列表导入，若失败，则 3.由用户选择某一目录或者文件，并尝试根据相对路径导入其他文件。

可以通过 Resolve 按钮旁边的配置按钮进入 Source Lookup 窗口，配置查找源码优先使用的路径。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125018184/2f6b7126e35e85c640e756a60b42ee4a/resolve_1.png)

也可以点击 File Not Found 的链接打开 resolve 窗口。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125018465/88846d72377741d3f255ee3ef629252c/resolve_2.png)

界面中可以查看源码导入来源的提示，可以是前述的三种来源之一，即采集时的路径、Source Lookup 的路径、用户临时选择的路径。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125018765/197e10c8f9ba2272405d994de6bc13d2/resolve_3.png)

Source 下拉列表中，每一个源码的开头也会有图标提示此源码是否已经导入。

##### 5.2.2.3. Redo Resolve
在已导入 source file 的情况下，Source View 提供 Redo Resolve 按钮，通过按钮可重新选择并导入当前的单个源码。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125023064/8800ef793b3339bed8c6a953258d1864/source_lookup_1.png)

##### 5.2.2.4. Source Lookup
如果想指定固定的源码导入目录，比如固定的库的位置，可以使用 Source Lookup 功能，点击 resolve 按钮后，工具会优先从 Source Lookup 中的目录导入源码。选择`Tools`->`Options...`->`Source Lookup`或者通过 Source Page Resolve 按钮旁边的配置按钮，可以进入到 Source Location 管理菜单。在该界面可以通过勾选决定是否启用已经加入的 Source Loaction，还可以选择是否自动保存通过 Resolve 按钮选择的路径。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125023332/8f37d90b0300160dc8825c68510f2391/source_lookup_2.png)

还可以通过小菜单按钮，添加、删除，调整加载源代码顺序。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125023614/c4767f61ca73ba2bc2ad4ba02c8afa39/source_lookup_3.png)

### 5.3. Raw Page
Raw Page 显示收集到的所有 kernel launch 的 metrics 信息。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125017404/000f4f9f8bdcabb62ffd52bd6252554a/raw_page_1.png)

**排序**

点击 metric 列可以对该列进行排序。

**筛选**

在 Filter 输入框输入关键词，可以过滤掉不包含该关键词的 metrics 列。

**转置**

Raw Page 支持表格转置的功能，提供 metrics 作为列，kernels 作为行的浏览视角。

**kernels 间比较**

双击表格内容会将对应的 kernel 切换为当前 kernel。

添加 baselines 之后，表格中的值更新为差值形式：

`<focus value> (<difference to baselines average [%]>, z=<standard score>) (<number of values>)`

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125017659/6084be381b8a05a29b53c7912698bf07/raw_page_2.png)

**导出**

可以通过右上角的菜单，将 Raw Page 中的表格导出到 CSV 等格式。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125011476/c3af9c613004c14d8af1b50ec51075ba/metric_6.png)

**多实例 metric 格式更改**

多实例类型的 metric，在表格中有两种显示方式，在 Options 中可以配置以下方式显示：

+ not instanced：totalValue {instanceCount}如 12 {3}
    - 加 baseline 之后，多了 totalValue 跟其他 baseline 的差异，如 12 (+0.00%){3}

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124989637/841f112e354a47866c24a1226a84bc19/baseline_example_1.png)

+ instanced：totalValue {value1; value2; ...}如 12 (2; 4; 6)，
    - 加 baseline 之后，多了 totalValue 跟其他 baseline 的差异，如 12 (+0.00%)(2; 4; 6)

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124989951/09ebc1a6a5f844b45877b99c32e34183/baseline_example_2.png)

多实例类型的 metric 目前主要有 3 类：

+ 指令执行次数：`inst_executed`、`thread_inst_executed`
+ 指令分类：`sass__inst_executed_per_opcode`
+ stall reason：`pu__pcsamp_warps_issue_stalled*`

### 5.4. Summary Page
Summary Page 显示收集到的所有 kernel launch 的重点关注的 metrics 信息，提供概览 metrics 的视角，方便从概要的 metrics 信息中确定需要进一步分析的 kernel。

本页面默认显示 ID、Time、API Call ID、Function Name、Demangled Name、Process、Device Name、Grid Size、Block Size。

可以在 `Tools`->`Options`->`Profile`->`Report Summary Page`选项中进行设置，新增额外显示的 metric。填写格式为`{customized_name:metric_name}`，metric_name 为 metric 的原始名称，customized_name 为显示名称。metrics 间以逗号分隔。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125017945/fac78fea73336ff6b5a19f436e5341a5/report_summary_page_1.png)

Summary Page 的排序、筛选、转置、kernels 间比较、导出功能与 Raw Page 相似，此外，双击 Summary Page 表格内容会跳转到 Details Page 以供查看详细的 metrics 信息。

### 5.5. Session Page
Session Page 显示报告的一些基本信息，包括 Launch Settings、Session Info、Processes、Environment、Device Attributes 五组信息。切换 kernel 时，Session Page 会高亮该 kernel 对应的 device attributes。

+ Launch Settings

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125007311/c0cbd9128b8a673488ed652c83938106/launch_settings_1.png)

+ Session Info

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125008727/48ec44c18e2ddc2a71d3593512adfd80/launch_settings_2.png)

+ Environment

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125019664/f68ac9de8ef97767666081f3183879bf/session_info_1.png)

+ Processes

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124995973/5f068cb5441859517b5729ce1972ffd7/environment_1.png)

+ Device Attributes

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124994594/09192bcf019a82a334563075215eb3b6/device_attributes_1.png)

### 5.6. Kernel Filter

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124994896/ffe76d8e2d432445f1c23b4654af3902/device_attributes_2.png)

Asight Compute 支持对采集到的 Kernel launch 进行过滤以缩小 Result 中的结果范围。点击“Apply Filters”按钮，打开过滤器对话框，支持使用多种过滤器共同对 Result 中的 Kernel launch 进行过滤。

+ Process：通过 Kernel launch 所在的进程号进行过滤，默认为 All
+ Launch Name：对 Kernel launch name 进行过滤，支持正则表达式（默认不启用，语法为 Perl 兼容）。若不勾选正则表达式，为大小写不敏感的字符串包含过滤；若勾选正则表达式，则为大小写敏感的正则表达式匹配过滤。
+ Device ID：对 Kernel launch 运行的 Device ID 进行过滤，支持过滤多个 Device，多个 Device ID 间使用','分隔。

正则表达式和 Device ID 输入有语法检查，若输入内容不符合语法规则，则会有错误提示且无法保存。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125016288/9c06dd5856921ecffc0dd32705176efb/process_kernel_launch_1.png)

点击箭头下拉菜单即可通过 Clear Filters 清除所有过滤器。

### 5.7. Baseline
Asight Compute 提供 Baseline 对比功能，可以将多个 kernel 的 profile 结果进行对比，并且支持跨报告。Baseline 管理界面如下所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124988132/3d6a4f3450888204ef406a5bdfa3ce40/baseline_1.png)

1. baseline 的图例，在图表中 baseline 的颜色与图例相同
2. baseline 的名字，鼠标悬停时，可以重命名 baseline
3. 将当前 kernel 添加为 baseline
4. 清除所有 baselines

在不同的类型的 UI 中，baseline 的表现形式不同

**图表中的 Baseline**

图表中除了当前 kernel 之外，还会显示 baseline，其颜色与 baseline 的图例相同，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124988469/d90a5a52ecbb9bed75adf391d82feda6/baseline_2.png)

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124988791/7139685be88873146303aef3372f860f/baseline_3.png)

图表中的 tooltip 也会显示 baseline 的详细信息。

**表格中的 Baseline**

当有一条 baseline 时，表格中会显示当前 kernel 的 metrics 与 baseline 对应 metrics 的差值百分比，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124989073/76861d13bb3a7bf0fe348a4e76d88653/baseline_4.png)

当有超过一条 baseline 时，表格中除了会显示 metrics 的差值百分比之外，还会显示标准分 z（Standard Score）如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124989353/bd0d62eb791a42a6a7d9c14842b94337/baseline_5.png)

### 5.8. Occupancy Calculator Page
Occupancy Calculator Page 可以计算指定配置下的占有率，并支持保存为文件供下次打开查看。此页面包含输入表单和结果图表两部分，其中结果图表又分为 Tables、Graphs、GPU Data 3 个部分：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125014633/38504f2b2ab7b14ab9a6677196ae8eab/occupancy_calculator_page_1.png)

通过以下 3 种方式会新建/打开一个计算器：

1. 点击报告上方的 Tools 按钮->Occupancy Calculator 按钮：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125014908/663266b20f97c01764dabb14d11fbcc8/occupancy_calculator_page_2.png)

2. 点击 Occupancy Section 旁边的计算器按钮：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125015191/5dfb9656954c151257ab9b206a521e83/occupancy_calculator_page_3.png)

3. 通过`File -> Open`菜单打开文件时，选择`.acu-occ`文件可打开此前保存的 occ 文件

### 5.9. Metric Details Panel
勾选主菜单`View->Metric Details`或者点击报告顶部的 Metric Details 按钮，可以在应用右侧打开 Metric Details Panel:

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125029031/0b0b6dd75955b94b4678eb0b99f0fa73/viewmetric_details_1.png)

或者

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125029273/3481ab87b7ad1534602641f0d845e3e0/viewmetric_details_2.png)

在打开的报告中，点击 Details page、Raw page、Summary page 中的 metric，可以在 Metric Details 窗口中查看 metric 的详细信息。Metric Details Widget 也提供搜索功能，可以查找当前报告中某个 metric 的详细信息：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125011814/e706ec423cd682a4b89f8d9f5b5dd2a4/metric_details_panel_1.png)

metric 详细信息包括以下部分：

+ metric information，包括 metric name、unit、value、report
+ additional information，包括 metric description、knowledgebase entry
+ instance List，对于具有多 instance 的 metric，instance list 可以查看具体每一个 instance 的值。例如，打开 Raw Page，选择 inst_executed 这个 metric，可以看到每一个汇编码地址对应的指令执行次数值。除了指令执行次数的 metric（inst_executed、thread_inst_executed）之外，指令统计 metric（sass__inst_executed_per_opcode）、stall reason metric（pu__pcsamp_warps_issue_stalled*）也属于多 instance metric，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125012097/0b41a7a488de80681d6af775030bc8e5/metric_details_panel_2.png)

对于 throughput 类型的 metrics，Metric Details 还会显示其 breakdown 信息：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125012389/527b43fffe2b3c3af8209cfe66d7545b/metric_details_panel_3.png)

对于多实例的 metrics，Metric Details 还会显示其实例的统计信息：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125012685/d3d3c38ed1c1855e5f9ba4820b36b100/metric_details_panel_4.png)

点击报告中的 metric 或搜索某个 metric 后，默认会在第一个 tab（Default Tab）中显示该 metric 的详细信息。可以通过 Pin Tab 按钮将 Default Tab 中的 metric 固定到一个新的独立的 tab 中（Pinned Tab），方便将多个 metrics 暂存并在它们当中切换进行对比。

## 6. 命令生成助手

命令生成助手是 Asight Compute GUI 提供的一个辅助功能，可以通过可视化界面配置采集参数，自动生成对应的 acu 命令行。

点击 Asight Compute GUI 菜单栏中的 `Tools` -> `acu Command Helper` 打开命令生成助手，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124983566/a2e6b7967a56d4f0360e42a7b1a7cccf/acu_command_helper_1.png)

命令生成助手的界面如下所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124983941/a18b314819e347211ddd3b33012b81d4/acu_command_helper_2.png)

1. 命令生成助手菜单栏 —— 根据参数类型分类，相同类型的参数归组展示
2. 参数配置区 —— 开启和配置采集选项
3. 命令展示区 —— 实时生成 acu 命令

### 6.1. 命令生成助手菜单栏

根据下图菜单的分类情况，可快速找到需要配置的采集选项：

| 菜单栏 | 含义 |
| --- | --- |
| Target Application | 配置与目标程序有关的选项，如目标程序路径和参数、输出报告路径等 |
| Replay Mode | 配置 replay 模式，以及各个 replay 模式特有的参数 |
| Metrics Selection | 指定 metrics 性能数据的采集范围以及 warp 调度器的状态采样 |
| Filter | 配置过滤器来控制采集范围，包括过滤 Kernel、过滤 device、控制采集时间范围 |

### 6.2. 参数配置区
对于可配置的选项，选项前有对应的文字描述，部分选项的上方会有示意图描述，下面灰色斜体的部分为选项的补充描述：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124990661/caaad6de4adb20560d4f066b4184f6f0/command_helper_params_1.png)

#### 6.2.1. 输入限制
对于一些输入框，会限制输入的内容与格式，例如 Target devices filter 的输入框中仅允许输入数字和逗号：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125001953/5956a0a4bb648b9b84cc2bee0550ab78/input_limits_1.png)

#### 6.2.2. 错误提示
部分选项开启后需要填入参数，参数为空时会有红色的错误提示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124996291/090ea82dc8fa82320397720f1132470e/error_hints_1.png)

#### 6.2.3. 跳转到帮助文档
部分选项旁有帮助图标，点击帮助图标可以跳转到文档对应的位置，帮助对选项的理解

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124998441/c90b9ac647a62e83e0ab93a9e4972444/help_doc_jump_1.png)

#### 6.2.4. 选择 Metrics
部分选项中需要填入 metrics，命令生成助手提供了 metrics 选择对话框， 点击如下按钮进入：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125012935/18574e0f2e76ea0e7334dedfdce589b1/metrics_1.png) 

点击后打开 metrics 选择对话框：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125013219/d0ddaf6f3edbf06dd651ce13c6e1b1d6/metrics_2.png)

在上述对话框中可以选择不同的计算能力，加载不同的 metrics 列表，同时支持过滤功能。

### 6.3. 命令行生成区
在上述参数配置发生改变的时候，会同步生成 acu 命令，在下方的命令展示区显示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124996541/dd839f1dffacd7753bc3e4a0106ed369/format_as_multiline_1.png)

勾选`Format as multi-line`复选框，可以将命令行格式化成多行显示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124996766/1fcf96d4ed8e736dd595077c3a2b0514/format_as_multiline_2.png)

点击`Copy`按钮可以复制命令到剪贴板，粘贴到终端中运行即可对目标程序进行 profiling。

<a id="QrQtD"></a>

## 7. Rule 系统

Asight Compute 提供了一个基于 Python 的 Rule 系统，用于在报告中自动检测潜在的性能问题并给出优化建议。Rule 基于采集到的 metrics 进行分析，当满足设定条件时，会在报告中生成提示、警告或错误信息，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125013569/e3ef3a29ecc6049b8f228c684437663f/metrics_3.png)

### 7.1. 管理 Rule 文件

每个 Rule 都是一个 `.py` 文件，位置在当前用户的 `文档` 目录下，例如：

`C:\Users\<用户名>\Documents\Asight Compute\2.0.0.0\Sections\`

除了内置的标准 Rule 外，还可以通过 `.py` 文件自定义 Rule，灵活指定 Rule 名称、依赖的 metrics 以及触发条件和改进建议等。`Sections Info` 窗口中展示了所有的 Rule，可以通过 `View` -> `Show Section Tool` 打开：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125019326/a4c314bf014c7e134187a7bcc0d08a2a/sections_info_1.png)

上述窗口中 Rule 显示在其所属的 section 节点下，`State` 列展示了当前 Rule 的状态：

+ Stock —— 内置的 Rule，未经修改
+ User Modified —— 用户修改过的 Rule
+ User Created —— 用户添加的 Rule
+ User Deleted —— 用户删除的 Rule

可以通过点击 `File Name` 列快速跳转到 Rule 所在文件夹。修改完 Rule 后，可以点击上方的 `Reload` 按钮重新加载，对于加载失败的 Rule，表格中会显示相应的错误信息，例如：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125027167/5aa859c2a943fbca4ce0a5741580d356/stock_rule_1.png)

点击上方的 `Restore` 按钮可以将选中的 Rule 文件恢复成初始状态。

可以点击 `Details Page` 中的 `Apply Rules` 按钮应用 Rule：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124994300/73b6fcb0a4806ce6bf87de3ae35a6d63/details_page_6.png)

### 7.2. 内置 Rule

Asight Compute 已经内置了如下 Rule，用来分析和定位采集报告中潜在的性能、计算资源和内存资源利用率等问题：

+ **LaunchStatistics** —— 内核启动配置分析，比如 grid 和 block 配置分析等。
+ **TheoreticalOccupancy** —— 分析理论占有率及其影响因素，比如 CU 可管理的最大 block 数、寄存器和共享内存使用大小、block 大小等。
+ **AchievedOccupancy** —— 分析实际占有率。
+ **IssueSlotUtilization** —— 基于调度器指令发射机制的 warp 停滞类型原因分析。
+ **PCSamplingData** —— 分析当前 PC 采样事件为零计数的原因。

### 7.3. 编写自定义 Rule

Asight Compute 通过 `HgRules` 模块提供了对外的 Python 接口。因此每个自定义 Rule 都需要 `import HgRules`。

参照下面的“自定义 Rule 示例”，每个 Rule 均需要实现如下方法：

+ `get_identifier()` —— 该 Rule 的内部标识符。
+ `get_name()` —— 该 Rule 的可读性描述名称，比如 `Basic Template Rule`。
+ `get_description()` —— 该 Rule 的描述信息，比如 `A rule template, demonstration basic HgRules functionality`。
+ `get_section_identifier()` —— 该 Rule 所对应的`section`的标识符，比如 `LaunchStats`。
+ `apply()` —— 该 Rule 的主处理函数，其中参数`handle`用于获取 Rule 的上下文。

实现了上述方法之后，请将自定义 Rule 文件放在和内置 Rule 相同的目录下面。

```python
import HgRules

def get_identifier():
    return "TemplateRule1"

def get_name():
    return "Basic Template Rule"

def get_description():
    return "A rule template, demonstration basic HgRules functionality"

def get_section_identifier():
    return "LaunchStats"

def apply(handle):
    # get the rule context, which provides all remaining functions, access to actions, metrics etc.
    ctx = HgRules.get_context(handle)

    # select the first action (CUDA workload) from the first range (CUDA stream)
    action = ctx.range_by_idx(0).action_by_idx(0)

    # get the frontend object, which interacts with the UI and profiler report
    fe = ctx.frontend()

    # get two metrics from this action
    grid_size = int(action.metric_by_name("launch__grid_size").as_double())
    block_size = int(action.metric_by_name("launch__block_size").as_double())

    # post a message to the frontend
    fe.message(HgRules.IFrontend.MsgType_MSG_OK, "Workload launch config: " + str(grid_size) + "x" + str(block_size))

    # post a warning message to the frontend
    fe.message(HgRules.IFrontend.MsgType_MSG_WARNING, "This is what a warning of the analysis might look like")
```

<a id="常见问题"></a>

## 8. 常见问题

### 8.1. 减少测试环境差异

可通过锁定设备频率，减少设备调频对 acu 采样的影响：

```bash
# 锁定设备频率到1.5GHz
ppu-smi -lpc 1500

# 解除频率锁定
ppu-smi -rpc
```

### 8.2. 目标应用已经结束，但 acu 没有收到目标应用退出消息而卡死
有些目标应用程序在启动后，会 fork 出很多的子进程，在目标程序主进程退出后，还有子进程一直存在不退出，acu 此时就会一直等待子进程，看到的现象会误以为 acu 卡死。

**确认此场景方法：**

1. 安装 pstree 工具
2. 在 acu 出现卡死现象后，在另一个终端中输入命令：`pstree <acu_pid>`，确认是否有目标应用 fork 出的进程出现在了此命令的列表中。如果有，就说明有 fork 出的子进程不退出。

**规避方法：**

在 acu 命令中使用 `--wait primary` 参数，让 acu 仅等待目标应用的主进程退出。

<a id="J5Ul3"></a>

### 8.3. 报错：Device is not ready for profiling
这个报错大概率是 PPU 性能数据采集资源 PCM 被其他应用占用，导致 acu 无法采集。可能是其它 asys 或者 acu 应用正在采集，也可能是其它采集 PPU 运行指标的监控程序正在后台运行。

1. 请运行 `sudo lsof /dev/alixpu` 和`dmesg --level=err,crit,alert,emerg`命令，查询哪个应用在占用 PPU PCM
2. 请运行` ppu-smi`，查询当前环境的 Driver Version（KMD 版本）
    1. 如果 KMD 版本低于 1.4.0，需要手动停止步骤 1 查询到的 PCM 占用程序，重新运行 acu
    2. 如果 KMD 版本大于或者等于 1.4.0，可以用 PPU-SMI 临时关闭其它应用的采集功能。请参考下面命令，更详细说明请参考[设置性能监控输出状态](../ppu_sdk/15_ppu_smi_mps.md)

```bash
#查询性能监控GPM stream状态，如果PCM被占用，acu无法采集时，期望返回ENABLED
ppu-smi gpm -g

#临时禁止GPM stream功能，让acu可正常采集
ppu-smi gpm -s DISABLED

#查询性能监控采集状态，期望返回DISABLED
ppu-smi gpm -g

#此时acu应该可以正常使用

#acu采集完成后，恢复GPM stream状态
ppu-smi gpm -s ENABLED

#查询性能监控采集状态，期望返回ENABLED
ppu-smi gpm -g
```

### 8.4. LLC 向 DRAM 写入数据偏少
如下图，memory D2H 的行为中 L2 向 LLC 写入了 64M 数据，但 LLC 仅向 DRAM 写入了 45.88M 数据。

造成这种数据不匹配的情况，是因为驱动层在将数据写入 LLC 后，就认为已经到 DRAM 了，随即结束 kernel 的执行。kernel 执行结束后，counter 的采集也会停止。但 LLC 向 DRAM 写入数据不受外部的控制，时机不确定，所以 LLC 向 DRAM 写入数据的 counter 会少一部分记录。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125009747/9ca52604758d6ea54af947ae00629d4b/llcdram_1.png)

**比赛关联：** 压测取证前用 `ppu-smi -lpc 1500` 锁定设备频率，可排除调频干扰，保证 TTFT/吞吐数据与 acu 采集结果的可比性与可复现性。

## 9. 已知问题

+ 不支持采集使用 hggcLaunchCooperativeKernelMultiDevice 的应用程序
+ 当 acu -o 选项指定报告输出位置的文件 IO 读写速率很低时，acu 报告文件可能生成不完整
+ `--profile-from-start`不支持跨进程控制采集时间范围
+ 应用程序编译需包含`-pthread`选项，否则可能导致 acu 运行崩溃
+ 若 acu 采集过程中被打断，已采集的跟踪信息可能无法正确展示
+ Warp State Statistics 中 Avg. Active Threads Per Warp [inst]值会偏低
+ Range Replay 模式下，capture 和 replay memory 相关 API（详细列表如下）还不稳定，可能影响数据的准确性

```bash
# HGGC runtime API
hggcMemcpy2D,
hggcMemcpy2DArrayToArray,
hggcMemcpy2DArrayToArray_ptds,
hggcMemcpy2DAsync,
hggcMemcpy2DAsync_ptsz,
hggcMemcpy2DFromArray,
hggcMemcpy2DFromArrayAsync,
hggcMemcpy2DFromArrayAsync_ptsz,
hggcMemcpy2DFromArray_ptds,
hggcMemcpy2DToArray,
hggcMemcpy2DToArrayAsync,
hggcMemcpy2DToArrayAsync_ptsz,
hggcMemcpy2DToArray_ptds,
hggcMemcpy2D_ptds,
hggcMemcpy3D,
hggcMemcpy3DAsync,
hggcMemcpy3DAsync_ptsz,
hggcMemcpy3DPeer,
hggcMemcpy3DPeerAsync,
hggcMemcpy3DPeerAsync_ptsz,
hggcMemcpy3DPeer_ptds,
hggcMemcpy3D_ptds,
hggcMemcpyArrayToArray,
hggcMemcpyArrayToArray_ptds,
hggcMemcpyAsync,
hggcMemcpyAsync_ptsz,
hggcMemcpyFromArray,
hggcMemcpyFromArrayAsync,
hggcMemcpyFromArrayAsync_ptsz,
hggcMemcpyFromArray_ptds,
hggcMemcpyFromSymbol,
hggcMemcpyFromSymbolAsync,
hggcMemcpyFromSymbolAsync_ptsz,
hggcMemcpyFromSymbol_ptds,
hggcMemcpyPeer,
hggcMemcpyPeerAsync,
hggcMemcpyToArray,
hggcMemcpyToArrayAsync,
hggcMemcpyToArrayAsync_ptsz,
hggcMemcpyToArray_ptds,
hggcMemcpyToSymbol,
hggcMemcpyToSymbolAsync,
hggcMemcpyToSymbolAsync_ptsz,
hggcMemcpyToSymbol_ptds,
hggcMemcpy_ptds,
hggcMemset,
hggcMemset2D,
hggcMemset2DAsync,
hggcMemset2DAsync_ptsz,
hggcMemset2D_ptds,
hggcMemset3D,
hggcMemset3DAsync,
hggcMemset3DAsync_ptsz,
hggcMemset3D_ptds,
hggcMemsetAsync,
hggcMemsetAsync_ptsz,
hggcMemset_ptds,
hggcStreamAttachMemAsync,
hggcStreamAttachMemAsync_ptsz,
hggcHostAlloc,
hggcMalloc,
hggcMalloc3D,
hggcMalloc3DArray,
hggcMallocArray,
hggcMallocHost,
hggcMallocManaged,
hggcMallocMipmappedArray,
hggcMallocPitch,
hggcFree,
hggcFreeArray,
hggcFreeHost,
hggcFreeMipmappedArray,
hggcLaunch,
hggcLaunch_ptsz,
hggcLaunchKernel_ptsz,
hggcLaunchCooperativeKernel_ptsz,
hggcLaunchCooperativeKernelMultiDevice,

# Hggc Driver API
hgMemcpyHtoD,
hg64MemcpyHtoD,
hgMemcpyDtoH,
hg64MemcpyDtoH,
hgMemcpyDtoD,
hg64MemcpyDtoD,
hgMemcpyDtoA,
hg64MemcpyDtoA,
hgMemcpyAtoD,
hg64MemcpyAtoD,
hgMemcpyHtoA,
hgMemcpyAtoH,
hgMemcpyAtoA,
hgMemcpy2D,
hgMemcpy2DUnaligned,
hgMemcpy3D,
hg64Memcpy3D,
hgMemcpyHtoDAsync,
hg64MemcpyHtoDAsync,
hgMemcpyDtoHAsync,
hg64MemcpyDtoHAsync,
hgMemcpyDtoDAsync,
hg64MemcpyDtoDAsync,
hgMemcpyHtoAAsync,
hgMemcpyAtoHAsync,
hgMemcpy2DAsync,
hgMemcpy3DAsync,
hg64Memcpy3DAsync,
hg64Memcpy2D,
hg64Memcpy2DUnaligned,
hg64Memcpy2DAsync,
hgMemcpy_v2,
hgMemcpyHtoD_v2,
hgMemcpyHtoDAsync_v2,
hgMemcpyDtoH_v2,
hgMemcpyDtoHAsync_v2,
hgMemcpyDtoD_v2,
hgMemcpyDtoDAsync_v2,
hgMemcpyAtoH_v2,
hgMemcpyAtoHAsync_v2,
hgMemcpyAtoD_v2,
hgMemcpyDtoA_v2,
hgMemcpyAtoA_v2,
hgMemcpy2D_v2,
hgMemcpy2DUnaligned_v2,
hgMemcpy2DAsync_v2,
hgMemcpy3D_v2,
hgMemcpy3DAsync_v2,
hgMemcpyHtoA_v2,
hgMemcpyHtoAAsync_v2,
hgMemcpy,
hgMemcpyAsync,
hgMemcpyPeer,
hgMemcpyPeerAsync,
hgMemcpy3DPeer,
hgMemcpy3DPeerAsync,
hgMemcpyHtoD_v2_ptds,
hgMemcpyDtoH_v2_ptds,
hgMemcpyDtoD_v2_ptds,
hgMemcpyDtoA_v2_ptds,
hgMemcpyAtoD_v2_ptds,
hgMemcpyHtoA_v2_ptds,
hgMemcpyAtoH_v2_ptds,
hgMemcpyAtoA_v2_ptds,
hgMemcpy2D_v2_ptds,
hgMemcpy2DUnaligned_v2_ptds,
hgMemcpy3D_v2_ptds,
hgMemcpy_ptds,
hgMemcpyPeer_ptds,
hgMemcpy3DPeer_ptds,
hgMemcpyAsync_ptsz,
hgMemcpyHtoAAsync_v2_ptsz,
hgMemcpyAtoHAsync_v2_ptsz,
hgMemcpyHtoDAsync_v2_ptsz,
hgMemcpyDtoHAsync_v2_ptsz,
hgMemcpyDtoDAsync_v2_ptsz,
hgMemcpy2DAsync_v2_ptsz,
hgMemcpy3DAsync_v2_ptsz,
hgMemcpyPeerAsync_ptsz,
hgMemcpy3DPeerAsync_ptsz,
hgMemsetD8,
hg64MemsetD8,
hgMemsetD16,
hg64MemsetD16,
hgMemsetD32,
hg64MemsetD32,
hgMemsetD2D8,
hg64MemsetD2D8,
hgMemsetD2D16,
hg64MemsetD2D16,
hgMemsetD2D32,
hg64MemsetD2D32,
hgMemsetD8Async,
hg64MemsetD8Async,
hgMemsetD16Async,
hg64MemsetD16Async,
hgMemsetD32Async,
hg64MemsetD32Async,
hgMemsetD2D8Async,
hg64MemsetD2D8Async,
hgMemsetD2D16Async,
hg64MemsetD2D16Async,
hgMemsetD2D32Async,
hg64MemsetD2D32Async,
hgMemsetD8_v2,
hgMemsetD16_v2,
hgMemsetD32_v2,
hgMemsetD2D8_v2,
hgMemsetD2D16_v2,
hgMemsetD2D32_v2,
hgMemsetD8_v2_ptds,
hgMemsetD16_v2_ptds,
hgMemsetD32_v2_ptds,
hgMemsetD2D8_v2_ptds,
hgMemsetD2D16_v2_ptds,
hgMemsetD2D32_v2_ptds,
hgMemsetD8Async_ptsz,
hgMemsetD16Async_ptsz,
hgMemsetD32Async_ptsz,
hgMemsetD2D8Async_ptsz,
hgMemsetD2D16Async_ptsz,
hgMemsetD2D32Async_ptsz,
hgMemSetAccess,
hgStreamAttachMemAsync,
hgStreamAttachMemAsync_ptsz,
hgMemAlloc,
hg64MemAlloc,
hgMemAllocPitch,
hg64MemAllocPitch,
hgMemAllocHost,
hgMemHostAlloc,
hg64MemHostAlloc,
hgMemAlloc_v2,
hgMemAllocPitch_v2,
hgMemHostAlloc_v2,
hgMemAllocHost_v2,
hgMemAllocAsync,
hgMemAllocAsync_ptsz,
hgMemAllocFromPoolAsync,
hgMemAllocFromPoolAsync_ptsz,
hgMemFree,
hg64MemFree,
hgMemFreeHost,
hgMemFree_v2,
hgMemAddressFree,
hgMemFreeAsync,
hgMemFreeAsync_ptsz,
```

+ App-Range Replay 模式下开启指令统计功能，在多卡场景下由于只能开单线程，无法通过多线程进行加速，所以 profiling 相对会比较慢。
+ ICN Link Section 中显示的 logical ICN link throughput 查询的是 MAC 层数据，所以会比实际用户通过 ICN link 所产生的收发数据要多。
+ Mac 系统上，在打开报告时强制退出 GUI，可能会出现 crash 或 hang 的问题。 
+ 当打开使用 Asight Compute 1.5/1.6 版本采集的报告时，会因为缺少`ws__we_warps_active.avg.per_cycle_active`，导致在执行`IssueSlotUtilization`rule 时失败。
+ 为了防止数据兼容性问题，不再支持打开 1.5 及以前的报告
+ Details Page 中 Memory Workload Analysis Section 中的 TSM Table 里的 % Peak 列的 Metric 数据偏小， 带宽使用了读写双向带宽。
+ 当报告采集于 810E 平台，Kernel 中有使用 MMA 指令， Details Page 中 Memory Workload Analysis Section 中的 TSM， KSD， KVD， L2 表格中的 %peak 的 metric 偏小， 带宽使用的 CU 数量是 PPU 上的总 CU 数。

## 10. 版本说明

### 10.1. 新增改动

#### 10.1.1. 新增 PM Sampling 功能
  - 可在 Details Page 中查看任意时刻的硬件指标变化

#### 10.1.2. acu 新增统计系统功能
  - 系统可通过基于 Python 脚本的内置规则或自定义规则，汇总、计算性能数据，将结果导出到文件，或直接显示在终端

#### 10.1.3. acu 命令行参数增强
  - `--csv` 参数支持与 `--page` 联动，输出格式受 `--page` 参数控制
  - 新增 `--csv-file <文件>` 参数，支持将 csv 数据直接输出到文件中

#### 10.1.4. 加强 Details Page 的 tooltip 显示
  - 集成 tab 与表格等内容，丰富信息展示样式

#### 10.1.5. 提升 baseline 对比体验
  - 当 current kernel 为 baseline 时，不再参与对比

#### 10.1.6. 统一 Memory 相关 metrics 的命名
  - 按 Metric 命名规范修正一致性

#### 10.1.7. 改进 kernel 选项错误提示
  - 使用 `--kernel-name` 或 `--kernel-id` 时，如遇到 "No Kernels" 错误，acu 会自动打印出当前程序中所有可用的 kernel 名称
