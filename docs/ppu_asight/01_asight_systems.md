# Asight Systems <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [1. 概述](#1-概述)
- [2. 安装指南](#2-安装指南)
  - [2.1. 获取 asys 命令行工具](#21-获取-asys-命令行工具)
  - [2.2. 获取 Asight Systems GUI 工具](#22-获取-asight-systems-gui-工具)
- [3. 快速入门](#3-快速入门)
  - [3.1. 采集性能数据](#31-采集性能数据)
  - [3.2. 分析报告](#32-分析报告)
  - [3.3. 下一步](#33-下一步)
- [4. 跟踪目标程序](#4-跟踪目标程序)
  - [4.1. PPU 活动跟踪](#41-ppu-活动跟踪)
  - [4.2. PPU Metrics 跟踪](#42-ppu-metrics-跟踪)
  - [4.3. HGTX 跟踪](#43-hgtx-跟踪)
  - [4.4. OS Runtime 跟踪](#44-os-runtime-跟踪)
  - [4.5. CPU 与线程活动跟踪](#45-cpu-与线程活动跟踪)
  - [4.6. API 调用栈跟踪](#46-api-调用栈跟踪)
  - [4.7. 内存使用情况跟踪](#47-内存使用情况跟踪)
  - [4.8. Python 跟踪](#48-python-跟踪)
  - [4.9. PyTorch 跟踪（实验特性）](#49-pytorch-跟踪实验特性)
  - [4.10. PCCL 活动跟踪](#410-pccl-活动跟踪)
  - [4.11. RDMA 网卡指标跟踪](#411-rdma-网卡指标跟踪)
- [5. 统计系统与报告分析](#5-统计系统与报告分析)
  - [5.1. 专家系统](#51-专家系统)
  - [5.2. 统计系统](#52-统计系统)
  - [5.3. 报告比较](#53-报告比较)
- [6. asys 命令行采集](#6-asys-命令行采集)
  - [6.1. 采集跟踪信息](#61-采集跟踪信息)
  - [6.2. 控制采集过程](#62-控制采集过程)
  - [6.3. 交互式采集跟踪](#63-交互式采集跟踪)
  - [6.4. Attach 模式采集（Beta）](#64-attach-模式采集beta)
  - [6.5. 多节点跟踪采集](#65-多节点跟踪采集)
- [7. Asight Systems GUI 分析](#7-asight-systems-gui-分析)
  - [7.1. 菜单栏](#71-菜单栏)
  - [7.2. Project Explorer](#72-project-explorer)
  - [7.3. Timeline View](#73-timeline-view)
  - [7.4. Analysis Summary Page](#74-analysis-summary-page)
  - [7.5. Diagnostics Summary Page](#75-diagnostics-summary-page)
  - [7.6. Files Page](#76-files-page)
  - [7.7. Options](#77-options)
- [8. 命令生成助手](#8-命令生成助手)
  - [8.1. 命令行助手菜单栏](#81-命令行助手菜单栏)
  - [8.2. 参数配置区](#82-参数配置区)
  - [8.3. 命令展示区](#83-命令展示区)
- [9. PPU 运行环境检查](#9-ppu-运行环境检查)
  - [9.1. 静态环境检查](#91-静态环境检查)
  - [9.2. 运行时环境检查](#92-运行时环境检查)
  - [9.3. 检查项说明](#93-检查项说明)
- [10. 常见问题](#10-常见问题)
  - [10.1. 减小报告尺寸](#101-减小报告尺寸)
  - [10.2. 启动应用后采集多份报告](#102-启动应用后采集多份报告)
  - [10.3. 通过事件触发跟踪采集](#103-通过事件触发跟踪采集)
  - [10.4. 采集 OSRT 信息查看 CPU 线程挂起的原因](#104-采集-osrt-信息查看-cpu-线程挂起的原因)
  - [10.5. 使用 asys 采集 mpirun 等多机多卡应用](#105-使用-asys-采集-mpirun-等多机多卡应用)
  - [10.6. 采集包含 fork 的应用程序](#106-采集包含-fork-的应用程序)
  - [10.7. 没有采集到设备内存使用信息](#107-没有采集到设备内存使用信息)
  - [10.8. 安装 SSH 服务](#108-安装-ssh-服务)
  - [10.9. 清理 asys 运行环境](#109-清理-asys-运行环境)
  - [10.10. asys 采集完成应用未停止](#1010-asys-采集完成应用未停止)
  - [10.11. 采集 Tensorflow Eager 模式应用跟踪不完整](#1011-采集-tensorflow-eager-模式应用跟踪不完整)
  - [10.12. Linux 上开启 Timeline View 的 Alt 平移快捷键](#1012-linux-上开启-timeline-view-的-alt-平移快捷键)
  - [10.13. 采集 Heap 内存使用量和进程内存占用量不同](#1013-采集-heap-内存使用量和进程内存占用量不同)
  - [10.14. 没有采集到使用 Ray 框架应用的跟踪数据](#1014-没有采集到使用-ray-框架应用的跟踪数据)
  - [10.15. CUDA GPU 环境使用 asys 采集跟踪](#1015-cuda-gpu-环境使用-asys-采集跟踪)
- [11. 已知问题](#11-已知问题)
- [12. 版本说明](#12-版本说明)
  - [12.1. 新增改动](#121-新增改动)

## 1. 概述

Asight Systems 是一款用于 **PPU 程序性能分析** 的工具套件。它能够跟踪 CPU 和 PPU 上的各种运行事件，并通过时间线（Timeline）的方式进行可视化展示，从而帮助开发者进行系统级性能分析并定位性能瓶颈。

Asight Systems 由以下两个工具组成：

+ **asys 命令行工具**
    用于采集目标程序在运行期间产生的事件数据，并生成分析报告。工具运行在 **Linux 平台**（Target 端）。asys 支持采集多种类型的事件，包括 HGGC、HGTX（基于 NVTX 标准的 PPU 实现）、OSRT（OS Runtime）及其调用栈信息等，同时支持灵活的采集开始和结束控制方式。

+ **Asight Systems GUI**
    图形化分析工具，用于加载并展示 asys 生成的报告，支持 **Windows** 和 **Mac** 平台（Host 端）。
    Asight Systems GUI 提供多种视图用于分析程序运行行为，如 Timeline View、Events View、Function Table 等，能够高效展示和分析大规模事件数据，同时提供流畅的交互体验。

**注意：**
**Target**（目标系统）是运行被分析程序的 Linux 服务器，asys 命令行工具在此执行数据采集。
**Host**（主机）是运行 Asight Systems GUI 的本地计算机（Windows / Mac），用于查看和分析报告。

Asight Systems 工具套件的使用流程为：

1. 在 Target 上使用 **asys 命令行工具** 跟踪目标程序，生成报告（`.asysrep` 文件）。
2. 将报告文件拷贝到 Host。
3. 使用 **Asight Systems GUI** 打开报告文件并进行性能分析。

**比赛关联：** Asight Systems 是定位 TTFT 与吞吐瓶颈的核心取证工具——用 asys 采集 benchmark 推理过程的 timeline，可精确区分 prefill 阶段的 PPU kernel 时间、Host 侧 API/调度开销与 PPU 空闲气泡，为优化效果提供量化证据。

<a id="install"></a>

## 2. 安装指南

### 2.1. 获取 asys 命令行工具

<a id="ZFzMg"></a>
#### 2.1.1. 配置环境变量

asys 命令行工具包含在 T-Head SAIL SDK 中，获取 SDK 请参见SDK 使用指南。安装完成后，进入 SDK 目录，执行以下命令配置所需环境变量：

```bash
source envsetup.sh
```

#### 2.1.2. 检查运行环境

环境变量配置完成后，执行以下命令查看当前安装的 asys 版本信息：

```bash
asys -v
```

执行以下命令检查当前环境是否满足 asys 跟踪采样要求：

```text
$ asys status

[Asight]: Profiling Environment Check
[Asight]: Root privilege: enabled: OK
[Asight]: Linux Kernel Paranoid Level = 2
[Asight]: Linux Distribution = Ubuntu: OK
[Asight]: Linux Kernel Version = 5.10.134-13.al8.x86_64: OK
[Asight]: Linux perf_event_open syscall available: OK
[Asight]: Linux Ftrace Support: available: OK
[Asight]: Glibc version requires 2.39 and above, Current version 2.39: OK 
[Asight]: SDK Installed: OK(0.0.0-000000)
[Asight]: CPU Profiling Environment: OK
[Asight]: Profiling Environment Check: OK
```

若命令显示采样环境检查通过，即可使用 asys 采集应用跟踪数据。

**注意：**
部分配置的检查失败不影响 asys 命令行工具的正常使用，但会影响部分功能：

+ `root` 权限检查失败将无法进行 CPU 采样及其调用栈采集。
+ `perf_event_open` syscall 检查失败将无法使用调用栈采集。如果使用 Docker，可在 `docker run` 命令中增加参数 `--pid=host --privileged=true` 来开启此功能。
+ `Ftrace` 检查失败将无法使用 CPU 采样。如果使用 Docker，可在 `docker run` 命令中增加参数 `--privileged=true -v /sys/kernel/debug:/sys/kernel/debug --pid=host` 来挂载 Ftrace 目录，同时需确认宿主机上的 `/sys/kernel/debug` 目录不为空。

### 2.2. 获取 Asight Systems GUI 工具

Asight Systems GUI 工具安装包单独发布，支持以下操作系统：

+ Windows 10 / Windows 11
+ macOS 10.15 及以上版本

请前往下载页面获取安装包，根据操作系统选择对应的格式：

+ Windows 系统请选择 `.msi` 安装包
+ macOS 系统请选择 `.dmg` 安装包

## 3. 快速入门

本文将引导您快速完成一次完整的性能分析流程：从采集数据到查看报告。

在本文中，将运行 PPU 程序的设备称为 **目标机（Target）**，将查看报告的设备称为 **主机（Host）**。

Asight Systems 的基本使用流程如下：

1. 在 **目标机（Target）** 上使用 **asys 命令行工具**采集性能数据并生成报告。
2. 在 **主机（Host）** 上使用 **Asight Systems GUI** 打开报告并进行性能分析。

**前提条件：**

+ 目标机已配备 PPU 设备，且驱动已正确安装。
+ 目标机已安装 asys 命令行工具。如尚未安装，请参见 安装指南。
+ 主机已安装 Asight Systems GUI 工具。

### 3.1. 采集性能数据

在目标机上执行 `asys profile` 命令，启动目标应用程序并采集跟踪数据，完成后自动生成跟踪报告。

命令格式：

```bash
asys profile [options] <application> [application args]
```

以下示例演示如何对目标程序 `test` 进行数据采集，并将报告输出为 `report.asysrep`：

```bash
asys profile -o report test
```

参数说明：

| 参数 | 说明 |
| --- | --- |
| `-o report` | 指定输出报告文件名（生成的文件为 `report.asysrep`） |
| `test` | 要进行性能分析的目标应用程序 |

执行该命令后，终端将输出类似如下信息：

```text
[Asight]: Profile executed.

[Asight]: Start trace service, this may take a while...
[Asight]: Starting target app: ./test
[Asight]: Target application pid: 125290, pgrp:125290

[Asight]: Collecting data...

[Asight]: All target application created processes are terminated.
[Asight]: Trace written into the output file: report.asysrep
```

默认情况下，asys 会采集 `hggc,hgtx,acdnn,acblas` 跟踪项。如需指定其他跟踪项，可使用 `-t` 选项，例如：

```bash
asys profile -t hggc,hgtx -o report test
```

asys 支持多种跟踪项与灵活的采集控制方式，详细信息请参见 [asys 命令行工具](#l80Hg)。

**提示：**
推荐将报告文件的尺寸控制在 200MB 以内。要减少报告尺寸，可以指定 `-s none` 选项关闭 CPU 采样，请参见 [CPU 采样](#CU82J)；也可以控制采样时长，请参见 [控制采集过程](#Oz0mt)。

### 3.2. 分析报告

asys 生成的报告文件使用 `.asysrep` 作为文件后缀。报告文件是独立的，可以从目标机拷贝到主机上，使用 Asight Systems GUI 打开并进行分析。

Asight Systems GUI 支持以下方式打开报告：

+ 主菜单打开：File -> Open...
+ 将文件拖拽（Drag & Drop）到 Asight Systems GUI 主窗口
+ 右键菜单打开：在 Project Explorer 空白区域点击右键 -> Open...
+ 通过命令行打开：`asys-ui report.asysrep`

**注意：**
+ 用于查看报告的 Asight Systems GUI 版本不应低于生成报告时使用的 asys 工具版本。
+ 如果使用较旧版本的 GUI 打开新版本工具生成的报告，GUI 会给出相应提示。

有关 GUI 的更多功能和使用说明，请参见 [使用 Asight Systems GUI 查看报告](#cEMJf)。

### 3.3. 下一步

完成上述流程后，您已经掌握了 Asight Systems 的基本使用方法。如需了解更多高级功能，请参阅以下文档：

+ 使用指南 — 详细介绍 asys 命令行工具与 GUI 的各项功能
+ 常见问题 — 使用过程中的高频问题与解决方案

## 4. 跟踪目标程序

本章介绍 asys 支持的各类跟踪采集功能，包括 PPU 活动、CPU 调度、内存使用、Python 调用栈等。每个小节说明对应的采集选项及 GUI 中的查看方式。

### 4.1. PPU 活动跟踪
asys 支持同时采集 `HGGC` 和 `CUDA` 的跟踪信息，允许通过 asys 对 `CUDA` 应用采集跟踪数据。通过 `-t` 选项指定要采集的跟踪项。

如果不指定跟踪项，默认采集 `hggc,hgtx,acdnn,acblas`。

`--trace`（`-t`）选项支持的 PPU 相关跟踪项如下：

| -t 支持的跟踪项 | 采集内容 |
| --- | --- |
| hggc | HGGC runtime/driver API 的执行时间以及调用栈信息<br/>CUDA runtime/driver API 的执行时间以及调用栈信息<br/>PPU 执行信息： kernel/memcpy/memset<br/>HGGC/CUDA API 和 PPU 执行关联关系 |
| acdnn | acDNN API: 执行时间信息 |
| acblas | acBLAS API: 执行时间信息 |
| hgvideo | HG-Encode API 的执行时间<br/>HG-ACVID API 的执行时间<br/>HG-JPEG API 的执行时间<br/>PPU 执行信息：video 编解码<br/>video API 和 PPU 执行关联关系 |
| pccl | PCCL 通信过程各阶段的执行时间 |

跟踪项 `hggc` 对 HGGC / CUDA 的采集范围，可通过 `--hggc-trace-set` 控制开启哪些子跟踪项。支持指定多个子集，用 `,` 分隔，例如 `--hggc-trace-set=kernel-activity,kernel-api`：

| HGGC 跟踪子集 | 采集内容 |
| --- | --- |
| kernel-activity | 采集 PPU 上执行 kernel 相关信息 |
| memory-activity | 采集 PPU 上 memory 操作相关信息 |
| kernel-api | 采集 CPU 上 kernel 相关 API 执行信息 |
| memory-api | 采集 CPU 上 memory 相关 API 执行信息 |
| default-set | 默认值，包含可指定的跟踪子集，以及其他 HGGC/CUDA 跟踪信息 |

+ 若希望精确禁止跟踪项 `hggc` 中采集某些 API，可通过配置 `ASIGHT_HGGC_TRACE_BLACKLIST` 环境变量，指定被禁止的 API 列表，多个 API 名称用 `,` 分隔。例如：`export ASIGHT_HGGC_TRACE_BLACKLIST=cudaEventQuery,cuEventQuery`。

#### 4.1.1. Device 端 PPU 活动

##### 4.1.1.1. PPU Activity
依赖的 asys 采集选项：

+ `--trace hggc`

采集到的报告在 GUI 工具打开后，可按照以下层级展示 PPU 的工作情况，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125087610/34b6186fb811209921938c7af5d36e73/trace_hggc_1.png)

为方便查看，同一个时间线会绘制在多个行中，例如上图中的`add` kernel 除了在其本行内显示外，还在 Kernels，Stream 等多个行中绘制。

如果 Context 下有多个 Stream，则会显示[All Stream]行，其中显示了所有 Stream 的汇总信息。

**注意：**
+ 如果 Device 下只有一个 Context，则不显示 Context 节点，直接显示其下面的 Stream 节点。同理，如果 Context 下只有一个 Stream，Stream 节点也被隐藏。
+ 显示的 PPU 设备索引为物理索引，不受`CUDA_VISIBLE_DEVICES`环境变量配置影响
+ HGGC stream memory write 活动时间仅显示开始时间，时长固定为 0。

PPU 的节点名字前显示了当前节点占其父节点的时间占比，以 stream 节点为例，具体规则如下：

```bash
stream时间占比 = 100.0 * stream耗时 / context耗时
stream耗时 = stream内的所有事件的时间总和
context耗时 = context内的所有事件的时间总和
```

所以 50.3% Stream 8 代表该 Stream 内所有事件时间占 Context 内所有事件时间的 50.3%。

**注意：**
+ Kernels 下面的 Kernel HGTX 节点的百分比计算方式是例外，其百分比计算的分母不是其父节点，而是 Stream 节点。
+ 在进行 filter 后，PPU 节点的时间占比会根据 filter 的范围重新计算，并且重新排序。

PPU Device 行汇总了整个设备的活动情况，分为上下两层显示，上层为 Kernel 执行，下层为内存操作。用不同的颜色用以区分内存操作类型，如 HtoD/DtoH/DtoD，Pinned/Pageable 等，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125067639/e8a40c834bf042bbf4a1e27a58cd30a1/ppu_device_timeline_1.png)

##### 4.1.1.2. PPU Graph
依赖的 asys 采集选项：

+ `--trace hggc`

Timeline View 支持 Graph 时间线的独立显示，方便对 graph 的执行情况进行分析。如果报告中有 graph 信息，在 stream 节点下会显示 graph 节点，具体层级为：

+ Graph Group
    - Graph
        * Graph Exec

对于 graph 时间线，会显示其 Graph ID 和 Graph Exec ID，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125050534/0493e3d9bf7a4b3f1ff12d644a696bf9/graph_group_1.png)

在 device 行上也会显示 graph 的汇总信息：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125041467/418f360a420c0c572c2c4d3c8d44f82f/device_ppu_1.png)

##### 4.1.1.3. PPU Video
依赖的 asys 采集选项：

+ `--trace hgvideo`

asys 还支持采集 PPU 上的 Video Activity 数据，并在时间轴上显示相关时间线，帮助分析 video 处理性能。如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125088228/9c34d4a16094f909f7f7390f84a5a07e/trace_hgvideo_1.png)

在 stream 节点下会有 video 节点，显示当前 stream 下的所有 Video Activity，并且与 kernel 时间线一样，会汇总到 device 节点中。在选择时间范围时，tooltip 中会有 Video Activity 的时间占比，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125041796/4eb47ed87a4160839387cb66185cf801/device_ppu_2.png)

##### 4.1.1.4. PPU HGTX 投影
依赖的 asys 采集选项：

+ `--trace hggc,hgtx`

Timeline View 支持在 PPU 节点下的每个 HGGC stream 行显示 HGTX range 在 PPU 上的投影，展示 HGTX range 范围内触发的 PPU 活动在 PPU 上的活动时间范围。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125067945/de3c63c10997a3983492721a0df4bdc7/ppu_hgtx_projection_1.png)

HGTX range 在 PPU 上的投影通过如下方式进行关联：

+ 通过在 HGTX range 范围内执行 HGGC API 关联，HGTX range 将投影到 HGGC API 触发的 PPU 上的各类活动之上。
+ 通过在 HGTX range 范围内创建的 HGGC graph node 关联（如通过 HGGC stream capture 创建 HGGC graph），HGTX range 将投影到 HGGC graph node 对应的 PPU 各类活动之上。

##### 4.1.1.5. PPU Kernel 节点组织方式
Timeline View 支持两种 kernel 节点的组织方式：

1. 按 kernel base name 分类
2. 按 kernel 所属的 HGTX 分类

按 kernel base name 分类如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125069010/b2163b8ae6c2ffc6abf637dec9036f49/ppu_node_form_1.png)

kernel 所属的 HGTX 分类如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125069281/987581d0bae9402938e71df4f48c6552/ppu_node_form_2.png)

两种分类组织方式可以在 Options Dialog 中进行切换：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125042158/ea8ccbc192edf56d0dc38941829af3fd/device_ppu_5.png)

#### 4.1.2. Host 端 API 调用情况

##### 4.1.2.1. HGGC API
依赖的 asys 采集选项：

+ `--trace hggc`

线程节点下会显示 HGGC 的调用情况，可查看 HGGC 中 Kernel 的分发时间，以及内存操作的启动时间：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125087879/5a96486321794e8c0acdbc6975da3e6b/trace_hggc_2.png)

**注意：**
部分场景可能无法采集 HGGC API 返回值信息。

对于返回结果非 0 的 HGGC API，会显示一个高亮标记：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125059989/4b0563b5e0ffdb161ee74edfbda89fb1/host_api_1.png)

##### 4.1.2.2. ACDNN
依赖的 asys 采集选项：

+ `--trace acdnn`

开启采集后，线程节点下会显示 ACDNN 的时间线：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125087317/b8f1c7a3b6db063ace7aac942450b65b/trace_acdnn_1.png)

##### 4.1.2.3. ACBLAS
依赖的 asys 采集选项：

+ `--trace acblas`

开启采集后，线程节点下会显示 ACBLAS 的时间线：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125087038/b2078f303402605f2da31aeea2372ef7/trace_acblas_1.png)

##### 4.1.2.4. Video API
依赖的 asys 采集选项：

+ `--trace hgvideo`

开启后，Video API 的调用情况如下所示，包括 Encode API，Decode API，HGJPEG API：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125088552/6ed0c3210c86a8b522646c801a3dc266/trace_hgvideo_2.png)

#### 4.1.3. Host API 与 Device Activity 跳转
Asight Systems 支持显示 Host API 与 Device Activity 之间的关联关系，并且支持二者之间的相互跳转：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125050109/65e984273c148dcf770415deeb035013/go_to_host_api_1.png)

上图点击 cudaLaunchKernel，在 Device 上执行的 kernel 被关联高亮。可利用右键菜单中的`Go to Host API`或者`Go to Device Activity`进行相互跳转。

#### 4.1.4. Launch API 与 Kernel 名称切换
可以通过`Tools`->`Options`->`Systems Profile`->`HGGC API Name Mode`来切换 launch API 名字的显示方式：

+ 显示 Host API 名字
+ 显示启动的 Kernel 的名字

#### 4.1.5. PPU Activity 依赖关系
PPU 上不同 stream 上的 kernel 之间可能通过 cudaEventRecord 和 cudaStreamWait，建立起执行的依赖关系，Timeline View 支持该依赖关系的显示

可以通过 PPU Activity 时间线或相关 Event API 时间线的右键菜单显示依赖：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125066786/870f37c282f5e9b16e920de0fd4c20fc/ppu_activity_1.png)

对于通过 event 相关 API 产生依赖的时间线，Timeline View 利用橙色曲线表示二者之间的依赖关系，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125067101/281400aaf933de6ff7928f0d3395f2ce/ppu_activity_2.png)

与依赖无关的时间线会被置为灰色，鼠标悬停在曲线上时会显示当前依赖的细节。点击曲线后，与该依赖路径相关的时间线会被高亮

对 default stream 的依赖用绿色曲线表示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125067335/544ef872ee9c75651c431acf9af7a521/ppu_activity_3.png)

对于依赖多个 stream 上的多个事件的场景，依赖关系的显示方式：

+ 显示被依赖 stream 的最后一个被依赖事件
+ 不显示当前查询的 PPU activity 所在 stream 的被依赖事件

默认显示的依赖关系为`实际生效的依赖关系`，例如查询 kernel 的依赖关系时，显示的是从 launch kernel API 执行开始，到 PPU 实际开始执行此 kernel 之前，这段时间存在的依赖关系（导致本 kernel 执行时间推迟的依赖关系）。

若希望查看所有的依赖关系（如包含逻辑上依赖但实际已经结束的依赖项），可通过菜单栏`Tools`/`Options`/`Systems Profile`进入设置界面，设置`HGGC Dependency Display Mode`为`All`，以显示所有逻辑上的依赖关系。

**注意：**
依赖关系由报告中的跟踪数据计算生成，若多个线程操作 HGGC stream 存在竞争，依赖关系显示可能不准确。

#### 4.1.6. 深入分析单个 Kernel
当某一个 kernel 的性能不符合预期并且想要深入分析该 kernel 时，在 Timeline View 中选中该 kernel，通过`右键菜单`->`Analyze the Selected Kernel with Asight Compute`可以复制生成 Asight Compute 报告的命令，在 Compute 命令行工具中使用该命令即可生成 Compute 报告，然后在 Compute GUI 工具中进一步分析该 kernel。 

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125034456/0456e40aff2fe22ea3c469dc18c81678/asys_kernel_1.png)

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125034762/e41e3dddce9a6d2f25ae64a7d536b3b5/asys_kernel_2.png)

### 4.2. PPU Metrics 跟踪
asys 支持周期采集设备运行时的各类指标数据（metric），例如资源利用率、IO 吞吐速率等指标，并在 Asight Systems GUI 中展示各类指标随时间的变化情况：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125068266/d96508e692f2bcd21fdecb132fbd61e6/ppu_metrics_1.png)

同一类别的 metrics 以分组的形式显示，支持 Overlay 和 Stacked 两种汇总显示方式。

PPU metrics 时间线支持统一高度显示比例，可以在 Options Dialog 或者 Timeline Options 中切换：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125068701/9da61172e414871ae119a2298fe9f363/ppu_metrics_height_1.png)

可通过`--ppu-metrics-device`选项指定 asys 采集的设备列表，可通过`--ppu-metrics-device all`指定采集所有设备，例如：

```bash
asys profile -t hggc --ppu-metrics-device all python test_linear.py
```

使用默认的 metrics set，采集所有 device。

可通过`--ppu-metrics-set`选项指定采集的指标集合，例如`--ppu-metrics-set throughput`采集 IO 吞吐速率相关指标集合：

```bash
asys profile -t hggc --ppu-metrics-device all --ppu-metrics-set throughput python test_linear.py
```

可通过`--ppu-metrics-device help`选项查询当前可指定的设备列表，可指定多个设备，通过`,`分隔，比如`--ppu-metrics-device 0,1`表示只采集设备 0 和 1 的运行指标：

```bash
root@02892cb56ba5:~# asys profile --ppu-metrics-device help
Possible --ppu-metrics-device values are:
    all: Select all supported PPUs
    none: Disable PPU Metrics [Default]
    device ID list: comma separated device ID list(eg.: 0,1)

Available PPU metrics sampling devices are:
    0: PPU, PCI Bus ID: 00000000:10:00.0
    1: PPU, PCI Bus ID: 00000000:11:00.0
    2: PPU, PCI Bus ID: 00000000:CE:00.0
    3: PPU, PCI Bus ID: 00000000:CF:00.0
```

设备的各类指标是周期采集的，默认采集频率为每秒采集 1000 次（1kHz），可通过`--ppu-metrics-frequency`设置采集指标数据的频率，例如`--ppu-metrics-frequency 10000`设置采集频率为 10kHz。

asys 支持采集众多设备指标种类，由于设备性能数据采集的容量限制，每次可采集的指标种类受限。asys 提供了若干预设的采集指标集合，可通过`--ppu-metrics-set help`选项查看支持的指标集合：

```bash
root@02892cb56ba5:~# asys profile --ppu-metrics-set help
Possible --ppu-metrics-set values are:
 ---------------- ---------------------------------------- --------------------------------------------
  Identifier       Description                              Enabled Metrics
 ---------------- ---------------------------------------- --------------------------------------------
  summary          Collect clock / memory / CU activity /   ce__cycles_elapsed.avg.per_second
                   Bus throughput information.              ce__cycles_active.avg.pct_of_peak_sustained_elapsed
                                                            gd__dispatch_count.avg.pct_of_peak_sustained_elapsed
                                                            ce__warps_active_accumulated.avg.pct_of_peak_sustained_elapsed
                                                            ce__warps_inactive_cu_active_accumulated.avg.pct_of_peak_sustained_elapsed
                                                            ce__warps_inactive_cu_idle_accumulated.avg.pct_of_peak_sustained_elapsed
                                                            cu__cycles_active.avg.pct_of_peak_sustained_elapsed
                                                            cu__ws_issue_active.avg.pct_of_peak_sustained_elapsed
                                                            cu__we_pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed
                                                            dram__exclude_hbm_bytes_read.sum.pct_of_peak_sustained_elapsed
                                                            dram__exclude_hbm_bytes_write.sum.pct_of_peak_sustained_elapsed
...
  throughput       Collect DRAM / PCIe / ICN link           kvd__transaction_hit_rate.pct
                   throughput information.                  ksd__transaction_hit_rate.pct
                                                            l2__transaction_hit_rate.pct
                                                            dram__exclude_hbm_bytes_read.sum.pct_of_peak_sustained_elapsed
                                                            dram__exclude_hbm_bytes_write.sum.pct_of_peak_sustained_elapsed
                                                            pcie__read_bytes.avg.pct_of_peak_sustained_elapsed
                                                            pcie__write_bytes.avg.pct_of_peak_sustained_elapsed
                                                            icnltx__bytes.sum.pct_of_peak_sustained_elapsed
                                                            icnlrx__bytes.sum.pct_of_peak_sustained_elapsed
...
```

asys 支持自定义采集的指标列表，可通过`--ppu-metrics-list help`选项查看 asys 支持的指标说明信息：

```bash
root@02892cb56ba5:~# asys profile --ppu-metrics-list help
Possible --ppu-metrics-list values are:

ce__cycles_active.avg
    Display Name:
        ce__cycles_active.avg
    Unit: cycle
    Description:
        # of cycles active on CE across CEs
...
kvd__transaction_hit_rate.pct
    Display Name:
        kvd__transaction_hit_rate.pct
    Unit: %
    Description:
        (%) hit rate of KVD cacheable requests
...
```

可通过`--ppu-metrics-list`指定自定义的指标列表，指标通过`,`分隔。通过`--ppu-metrics-list`指定的指标和通过`--ppu-metrics-set`指定的指标集合将合并采集。例如`--ppu-metrics-list ce__cycles_active.avg,kvd__transaction_hit_rate.pct`指定采集 CE 利用率和 KVD cache 命中情况：

```bash
asys profile -t hggc --ppu-metrics-device all --ppu-metrics-set none --ppu-metrics-list ce__cycles_active.avg,kvd__transaction_hit_rate.pct python test_linear.py
```

由于设备性能数据采集的容量限制，通过`--ppu-metrics-list`指定自定义的指标列表时，需要确保采集的指标不超过设备容量限制，可通过`--check-ppu-metrics-list`检查指标列表，指标通过`,`分隔：

```bash
root@02892cb56ba5:~# asys profile --check-ppu-metrics-list ce__cycles_active.avg,kvd__transaction_hit_rate.pct,pu__we_average_warps_issue_stalled_compute_sfu_raw_per_issue_active.ratio
Check sampling metrics list result: PASS.
Metrics list is suitable for PPU sampling capacity.
```

**注意：**
asys 采集设备运行指标可能由于 PPU 性能数据采集资源被其他应用占用而导致失败，可能由于如下原因导致无法采集设备运行指标数据：
+ 其他 asys 应用正在采集设备运行指标数据
+ 其他 acu 应用正在采集跟踪数据
+ DCGM 正在采集性能分析指标，可通过执行`dcgmi profile --pause`暂停 DCGM 采集
+ 可通过 PPU-SMI 查询 PPU performance counter 和 HGML GPM 服务的繁忙状态
- `ppu-smi -q`查询 PPU performance counter 工作状态
- `ppu-smi gpm --get-sample-state`查询 HGML GPM 服务是否使能（使能将会占用 PPU performance counter）
- 可通过`ppu-smi gpm -s 0`暂停 HGML GPM 服务的输出，暂停其对 PPU performance counter 的占用

**比赛关联：** `--ppu-metrics-set throughput` 采集的单卡 DRAM 读写带宽可用于论证 decode 阶段是否受 HBM 带宽限制，以及量化（如 INT8/FP8）带来的带宽收益；PCIe/ICN 指标不作为本次单卡比赛优化依据。

### 4.3. HGTX 跟踪
HGTX 是基于 NVTX 标准的 PPU 实现，用于在代码中插入自定义标记以标注时间线。Asight Systems 支持对 HGTX 的跟踪采集，支持自定义 Domain、push/pop、start/end API 以及 payload API。

下面展示了一个使用 HGTX 的例子：

```c
#include <nvtx3/nvToolsExt.h>

for (int index = 0; index < 1000; ++index) {
    nvtxRangePushA("Loop");
    nvtxRangePushA("DoProcess");
    DoProcess();
    nvtxRangePop();
    ...
    nvtxRangePop();
}

```

依次 push 进 Loop 和 DoProcess 两个 HGTX range，最内层的 DoProcess()函数调用了一些 HGGC API。通过如下命令采集 hgtx：

```bash
 asys profile -t hgtx -o test_report sample
```

在采集报告后，在 GUI 中显示如下：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125035109/f9a864069c2b00586ca25586cd150a21/asys_kernel_3.png)

上图中可以看出，外层 NVTX 的时间线在上层，内层 NVTX 显示在下层。Loop 的时间线包括 DoProcess 的时间线，DoProcess 的时间线又包括最内层调用的 CUDA API 的时间线。

Asight 支持采集并显示用户指定的颜色：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125070132/b22adcd7a4f86b394ddc5d8ca3bdb4d0/pthread_mutex_lock_1.png)

### 4.4. OS Runtime 跟踪
OS Runtime（OSRT）跟踪用于查看 CPU 线程挂起的原因，如 `pthread_mutex_lock`、`sleep` 等系统调用。要采集 OSRT，需要在 `-t` 参数中增加 `osrt`：

+ 可通过 `--osrt-threshold` 选项指定采集门限
+ 可通过 `--osrt-backtrace-threshold` 指定调用栈回溯门限

例如：

```bash
asys profile -t osrt --osrt-backtrace-threshold 80000 python /test_script/ops/test_linear.py
```

通过 GUI 查看 OSRT 的时间线：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125065426/f6bba4d75174af56fe5436f04358968a/os_runtime_1.png)

<a id="CU82J"></a>

### 4.5. CPU 与线程活动跟踪
Asight Systems 支持采集线程在 CPU 各核心的调度情况。通过 `--sample`（`-s`）选项，可采集应用程序在系统各 CPU 上的执行情况，并支持周期性地采集 CPU 执行调用栈信息，以及通过汇总调用栈信息提供函数耗时统计信息。

例如：采集 CPU 执行信息，指定调用栈采集周期：

```bash
asys profile -s process-tree -b dwarf --sample-period 2000000 python test_linear.py
```

+ `-s process-tree`采集本应用进程及其子孙进程的 CPU 调度跟踪
+ `-b dwarf`开启采集 CPU 执行调用栈信息，默认开启，可省略
+ `--sample-period 2000000`指定每个 CPU 调用栈采集的周期，单位为 CPU 执行 cycle 数
+ `--sample-backtrace-depth`指定 cpu sampling 调用栈深度，默认为 24。

**注意：**
+ 开启 CPU 执行信息采样将会使报告大小显著增加，`--sample-period`设置越小，对应用程序的影响越大。
+ 通过`--sample-period`选项指定的采集周期可能受操作系统限制，小于设定的采集频率。
+ 通过`--sample-period`指定较短的采样周期时，部分采样点可能因为吞吐能力原因被忽略。

#### 4.5.1. CPU 活动情况
依赖以下 2 个采集选项之一：

+ `--sample process-tree`：采集进程树
+ `--sample system-wide`：采集系统所有进程 

开启 CPU 采样后，可查看 CPU 的活动情况：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125073925/8e85e3a11af4534d0f5bdda5a9d1d57d/sample_process_tree_1.png)

上图中 CPU Group 行显示了整体 CPU 活动的情况，下面每个节点分别代表了各核心的工作负载，Timeline 占比高的部分代表该时间段该核心繁忙，空白的部分代表该时间段该核心空闲。主进程的活动情况用深蓝色表示，子进程的活动用黑色表示。左侧的 CPU 核心节点有一个代表其颜色的 label，该 label 将在线程行中使用。

在 Timeline 的 tooltip 中会显示当前 CPU 具体在执行哪个进程和线程：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125039906/8ca1966775374669dac6158b08f2fd7e/cpu_1.png)

通过右键菜单中的"Go to Thread Row"功能，可以跳转至相应的线程行：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125040158/9c275a12833d967af3e0cec9da4a6082/cpu_2.png)

**注意：**
+ 若在 Docker 内采集 CPU 活动情况，Docker 启动时需要配置选项`--privileged=true -v /sys/kernel/debug:/sys/kernel/debug --pid=host`
+ CPU Sampling 的采样率较高，会增加报告文件的尺寸。如果对 CPU 采样不感兴趣，可以在 asys 命令行中传入`-s none`关闭采样。

#### 4.5.2. 线程调度情况
依赖以下 2 个采集选项之一：

+ `--sample process-tree`：采集进程树
+ `--sample system-wide`：采集系统所有进程 

开启 CPU 采样的线程时间线如下所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125074189/f338e3db06f9e8a383a1bc65a9a7c7af/sample_process_tree_2.png)

线程行的子节点显示了各类 API 的调用，线程行中展示了其在 CPU 各核心上的执行情况，分为 4 个子行：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125078105/eca12acd8394f5d99c953e6ca4647074/thread_scheduling_1.png)

从上到下依次为：

+ CPU 利用率：CPU 资源利用情况
+ CPU 核心：当前线程在哪个核心上调度，其颜色与 CPU 核心节点的 label 颜色对应
+ 线程状态，分为 4 种：
    - 运行中
![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125078920/a32379d3906d0a653e25096eae804c6a/thread_state_running_1.png)
    - 未调度
![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125040457/315c1effae517fbf6642855db9ea465a/cpu_label_1.png)
    - 等待中
![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125040684/a18da1e32edb005d95b0b9359bbac84e/cpu_label_2.png)
    - 正在调用 OSRT
![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125037027/40bcc31f71c83caedf940399127625db/backtrace_tooltip_1.png)
+ Backtrace 采样点：代表采样点，其 tooltip 中有详细的调用栈信息

将鼠标悬停在 item 上会有更详细的信息显示。

在未开启 CPU 采样，但开启了 OSRT 采集时，Asight Systems 支持利用 OSRT 的执行情况估算线程状态，将 OSRT 中执行的时间片视为 CPU 空闲；将 OSRT 外执行的时间片视为 CPU 忙碌，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125037287/f659b73ca974144589a9c65d8a09d53f/backtrace_tooltip_2.png)

此时线程状态分为两种：

+ 可能运行中
![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125078920/a32379d3906d0a653e25096eae804c6a/thread_state_running_1.png)
+ 可能等待中
![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125079182/04239684e9f39cf2a41fa39bb201d2b8/thread_state_waiting_1.png)

在仅开启 backtrace 采样时，线程行会显示采样点：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125036779/bae38a460c7c6e1091ee2fbea09d1ccd/backtrace_sample_marker_1.png)

可以在 GUI 下方的 Function View 中查看应用程序中函数耗时统计信息：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125078605/54a5b520e105c9fd6b8cc250949b3151/thread_scheduling_2.png)

**注意：**
若在 Docker 内采集线程调度情况，Docker 启动时需要配置选项`--privileged=true -v /sys/kernel/debug:/sys/kernel/debug --pid=host`

#### 4.5.3. CPU Metrics 采集
asys 支持周期采集 CPU 运行时的各类指标数据（metric），包含 hardware 及 software（operation system）指标，例如 IPC，Cache Miss 率等，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125045013/37e15282c80c85b6a99f80bfeae5e305/event_sample_systemwide_1.png)

因为 CPU metrics 采集是系统级跟踪，需使能`--event-sample=system-wide`。

可通过`--cpu-core-events`指定具体的 hardware 指标，使用`--cpu-core-events=help`查看具体的指标及定义，例如：

```bash
asys profile --event-sample=system-wide --cpu-core-events=1,2,3
```

可通过`--os-events`指定具体的 software（operation system）指标，使用`--os-events=help`查看具体的指标及定义，例如：

```bash
asys profile --event-sample=system-wide --os-events=1,2,3
```

asys 提供了若干预设的 CPU 采集指标集合，可通过`--cpu-core-events-set`指定具体的 hardware 指标集合，可通过`--cpu-core-events-set=help`选项查看支持的指标集合（默认为 summary），例如

```bash
asys profile --event-sample=system-wide --cpu-core-events-set=cache
```

可通过`--os-events-set`指定具体的 software 指标集合，可通过`--os-events-set=help`选项查看支持的指标集合（默认为 summary），例如

```bash
asys profile --event-sample=system-wide --os-events-set=fault
```

CPU 的各类指标是周期采集的，可通过`--sample-period 2000000`指定每个 CPU 指标采集的周期，单位为 CPU 执行 cycle 数（默认为 2000000）。

<a id="PP2Xv"></a>

### 4.6. API 调用栈跟踪
asys 支持采集 HGGC / CUDA / OSRT / ACDNN / ACBLAS / CUDNN / CUBLAS 相关 API 的调用栈信息。可以指定仅对运行时长超过指定门限的 API 采集调用栈信息，并可控制调用栈回溯的最大深度。

开启调用栈跟踪后，可以在 GUI 中的[Function View](#WGnXs)中查看函数调用的火焰图/冰川图，以及 Top Down/Bottom Up/Flat 表格。

#### 4.6.1. 采集 HGGC 调用栈
使用如下命令采集 HGGC 跟踪，并采集调用栈信息：

```bash
asys profile -t hggc --hggcbacktrace all:1000 --hggc-backtrace-depth 24 python test_linear.py
```

+ `-t hggc`：开启 hggc 跟踪
+ `--hggcbacktrace all:1000`：采集所有 HGGC 跟踪的调用栈，触发调用栈采集的 API 运行时长门限，单位纳秒（ns）
+ `--hggc-backtrace-depth 24`：HGGC 调用栈最大回溯深度（24 帧）

可将鼠标悬停时间线上查看调用栈：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125057182/83c4628b44643038e53b7eb85dfa8343/hggc_api_table_1.png)

#### 4.6.2. 采集 OSRT 调用栈
使用如下命令采集 OSRT 跟踪，并采集调用栈信息：

```bash
asys profile -t osrt --osrt-backtrace-threshold 80000 --osrt-backtrace-depth 24 python /test_script/ops/test_linear.py
```

+ `-t osrt`：开启 osrt 跟踪
+ `--osrt-backtrace-threshold 80000`：采集 OSRT API 调用栈，触发调用栈采集的 API 运行时长门限，单位纳秒（ns）
+ `--osrt-backtrace-depth 24`：OSRT 调用栈最大回溯深度（24 帧）

调用栈如下所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125065843/eb7cba7bd6a8a9fd2099bf81583631f7/osrt_api_table_1.png)

#### 4.6.3. 采集 ACDNN/ACBLAS 调用栈
使用如下命令采集 ACDNN 和 ACBLAS 跟踪，并采集调用栈信息：

```bash
asys profile -t acdnn,acblas --acompute-backtrace-threshold 80000 python /test_script/ops/test_linear.py
```

+ `-t acdnn,acblas`：开启 ACDNN 和 ACBLAS 跟踪
+ `--acompute-backtrace-threshold 80000`：采集 ACDNN 和 ACBLAS API 调用栈，触发调用栈采集的 API 运行时长门限，单位纳秒（ns）

调用栈如下所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125030812/0af76c320ecffcd56b872c90141923b3/acdnn_acblas_table_1.png)

### 4.7. 内存使用情况跟踪

本节介绍如何跟踪 PPU 设备内存、Host 内存、Heap 内存及 Pinned 内存的使用情况。

<a id="VlQaR"></a>

#### 4.7.1. PPU 内存使用跟踪
asys 支持采集应用程序对设备内存的使用情况，采集申请、释放设备内存时的调用栈信息，并通过汇总调用栈信息提供设备内存使用统计信息。可通过 `--hggc-memory-usage` 选项使能对内存使用的采集，例如：

```bash
asys profile -t hggc --hggc-memory-usage device python test_linear.py
```

当开启内存用量跟踪时，Asight Systems 会在时间轴上显示 PPU 内存的使用情况，可以对内存用量进行分析，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125041174/74348237415dcaecc07c3929d52f98e6/device_memory_usage_1.png)

Device memory usage 行中显示了程序运行过程中 PPU 内存的用量，功能包括：

+ 支持与 CUDA/HGGC API 的关联显示
+ 支持 Callstack
+ 支持在 Events View 中显示内存分配/释放事件

当 PPU 内存申请失败时，会以小红点的形式在 Device memory usage 行显示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125057516/6828260e2b2b990d242b65d1b18a9458/hggc_api_table_2.png) 

在 GUI 的[Device Memory View](#gY4WW)中可以查看火焰图/冰川图，以及 Top Down/Bottom Up/Flat 表格

**注意：**
+ 可通过`--hggc-backtrace-depth`选项控制调用栈采集深度，默认采集 24 帧，例如`--hggc-backtrace-depth 50`指定最多回溯 50 帧调用栈。
+ 进程结束时 HGGC 析构释放设备内存不在本功能的采集范围

##### 4.7.1.1. Memory Timeline
展开 Device memory usage 行，或者点击右侧的 Toggle memory timeline details 按钮，可以显示 Memory Timeline，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125057896/85e21760d5a25fc325fe4505ff7e73bd/hggc_backtrace_depth_1.png)

上图显示了每笔内存申请的细节，包括内存的申请时间和释放时间，对于很小用量的内存申请会被合并显示在最上方。

除了上图中的普通模式外，还支持两种模式：分组模式和分组着色模式

**分组模式**

将内存分配按照模块进行划分，例如可以分为 PyTorch 模块，通信库模块等等，可以查看某个模块的内存使用情况，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125061100/634d49a88ffbe022583ebf4ea62566f6/memory_timeline_1.png)

可以点击模式切换组合框右侧的按钮，打开分组规则对话框进行配置分组规则：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125061486/1f969938f7ee004e451e067eb82e0cf6/memory_timeline_2.png)

分组规则从上到下依次进行匹配，每笔内存分配只能属于一个分组。可以点击色块修改分组的颜色。

**分组着色模式**

普通模式和分组模式的组合，每笔内存分配仍然单独显示，但是其颜色与其所属的分组颜色相同，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125060342/33f22a4af1d22097d554a21483817d2c/host_memory_sampling_1.png)

#### 4.7.2. Host 内存使用采样
asys 支持周期采样应用程序对 CPU 侧系统内存的使用情况。可通过`--host-memory-sampling`选项使能系统内存使用采样，通过`--host-memory-sampling-frequency`控制采样频率，例如：

```bash
asys profile -t hggc --host-memory-sampling true --host-memory-sampling-frequency 500 python test_linear.py
```

通过采样进程的系统内存使用数据，可以在 Asight Systems GUI 中查看每个进程的 CPU 侧内存使用的变化情况：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125059712/67c377774b4f87330e66818287f4b01b/host_1.png)

支持显示两种内存用量：

Resident set size：实际的物理内存用量

Water mark：采集过程中物理内存用量的峰值

**注意：**
asys 支持采集本应用程序进程树（根进程和子孙进程）的系统内存使用，当`系统级跟踪采集`使能时（`-s system-wide`），采集系统内存使用功能将不生效。

<a id="Tekvl"></a>

#### 4.7.3. Heap 内存使用跟踪
asys 支持采集应用程序对 CPU 侧动态分配内存 / 堆内存（Heap memory）的使用情况，比如通过`malloc` / `new`等方式动态分配的内存，采集申请动态分配内存的调用栈信息，并通过汇总调用栈信息提供动态分配内存的使用统计。可通过`--heap-memory-usage`选项使能对动态分配内存使用的采集，例如：

```bash
asys profile --heap-memory-usage true python test_linear.py
```

通过采集动态分配内存使用，可以在 Asight Systems GUI 中查看每个进程的动态分配内存使用的变化情况：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125055443/6ecd7149f62acaa90ae3a8190cb1a9d9/heap_memory_usage_1.png)

点击`Heap memory usage`对应的时间位置，可查看进程截止到此刻的动态分配内存使用火焰图 / 冰川图等信息，支持内存泄露分析，支持内存使用量 / 申请次数统计，例如：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125055831/e7f25b8166301beb5c055d303cbcf7f5/heap_memory_usage_2.png)

**注意：**
通过`Filter and Zoom in`选定一段时间，点击`Heap memory usage`对应的时间位置，可查看从选定的起始时间到当前时间的内存使用统计信息，如查看这一时间段的内存泄露。

可通过`--heap-sampling-interval-bytes`选项调整 asys 对动态分配内存使用的`平均采样间隔字节数`，较小的采样间隔会提升对较小尺寸的动态分配内存使用的采集精度，也会显著增加 asys 跟踪采集的性能开销。

可通过`--heap-backtrace-depth`选项调整动态分配内存使用调用栈的采集深度，可通过`--heap-report-interval`选项调整动态分配内存使用信息的汇总间隔，例如：

```bash
asys profile --heap-memory-usage true --heap-sampling-interval-bytes 16777216 --heap-backtrace-depth 50 --heap-report-interval 2 python test_linear.py
```

+ `--heap-memory-usage true`：使能动态分配内存使用跟踪采集
+ `--heap-sampling-interval-bytes 16777216`：设置`平均采样间隔字节数`为 16MiB
+ `--heap-report-interval 2`：设置动态分配内存使用的信息每`2毫秒`汇总记录一次

**注意：**
+ 通过`--heap-sampling-interval-bytes`选项设置`平均采样间隔字节数`，asys 可能合并上报小于此门限的动态分配内存使用，以减少跟踪采集的性能开销
+ 通过设置`--heap-sampling-interval-bytes=1`，asys 将会完整采集每一笔动态分配内存使用，也会显著增加 asys 跟踪采集的性能开销，不建议运行复杂应用程序时配置为 1
+ 通过`--multi-node-mode`使能多节点跟踪采集时，不支持采集 Heap 内存使用跟踪数据

<a id="m0dAK"></a>

#### 4.7.4. Pinned 内存使用跟踪
asys 支持采集应用程序对锁页内存（pinned memory）的使用情况，采集申请、释放锁页内存时的调用栈信息，并通过汇总调用栈信息提供锁页内存使用统计信息。可通过`--hggc-memory-usage`选项使能对 pinned 内存使用的采集，例如：

```bash
asys profile -t hggc --hggc-memory-usage pinned python test_linear.py
```

通过采集锁页内存使用，可以在 Asight Systems GUI 中查看每个进程锁页使用随时间的变化情况，并可查看应用程序中各个 API 的设备内存使用汇总信息，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125066484/3ff387ac483b110610ef729bd6fb8d45/pinned_1.png)

上图中，展示了 Pinned 内存随时间变化的情况，tooltip 中显示了本次内存变化的分配/释放情况，以及调用栈信息。Pinned 内存同样支持在 Events View 中显示。

在 GUI 的[Host Pinned Memory View](#k5lmj)中可以查看火焰图/冰川图，以及 Top Down/Bottom Up/Flat 表格

**注意：**
+ 可通过`--hggc-backtrace-depth`选项控制调用栈采集深度，默认采集 24 帧，例如`--hggc-backtrace-depth 50`指定最多回溯 50 帧调用栈。
+ 支持同时采集 device 和 pinned 内存使用情况，多个选项通过`,`间隔，例如`--hggc-memory-usage device,pinned`
+ 进程结束时 HGGC 析构释放锁页内存不在本功能的采集范围

#### 4.7.5. 内存用量显示比例
为方便分析 OOM 场景，Timeline View 中可以切换显示内存用量的显示比例，可以在 Options Dialog 或者 Timeline Options 中切换：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125058272/8b0853302b53bcca7c12ee8320cd4c30/hggc_memory_usage_1.png)

Unified memory usage scale 开启时，所有相同类型的内存用量，使用相同的高度比例：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125082033/3938181612b54480992912a2d34e116d/timeline_view_1.png)

Unified memory usage scale 未开启时，每行的内存用量以本行的最大值作为最高点：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125061762/3ba4ddbf04055660475ffca7eef17512/memory_usage_1.png)

### 4.8. Python 跟踪

#### 4.8.1. 采集 Python 调用栈

##### 4.8.1.1. 周期采集 Python 调用栈 (Python Sampling)
asys 支持周期采集 Python 脚本运行时的调用栈，包含函数名、文件名、行号，并在 Asight Systems GUI 中展示调用栈情况：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125071261/4d0ca40501bd6352056aa51f969cad88/python_sampling_1.png)

可通过`--python-sampling`选项使能 Python backtrace 周期采集，通过`--python-sampling-frequency`控制采样频率，asys 将周期采集 python 脚本内的调用栈情况。例如：

```bash
asys profile --python-sampling true --python-sampling-frequency 1000 python launch.py
```

+ `--python-sampling true`：使能 Python backtrace 周期采集，默认为 true。
+ `--python-sampling-frequency 1000`：控制采样频率，范围为 1Hz - 1kHz，默认为每秒采集 500 次（500Hz）。
+ `--python-backtrace-depth`：指定 python sampling 调用栈深度，默认为 24。

##### 4.8.1.2. 采集特定事件时 Python 调用栈 (Python Backtrace)
asys 支持在跟踪特定事件时，采集当前的 Python 调用栈，并结合 C 调用栈展示完整调用链路。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125073005/69a668cd5f31e59ddfd6cbb343800e40/python_sampling_true_1.png)

可通过`--python-backtrace=hggc`进行使能及通过`--python-backtrace-depth`控制采集调用栈深度，目前 asys python backtrace 支持的跟踪项为：

+ hggc

例如：

```bash
asys profile --python-backtrace=hggc python launch.py
```

+ device memory / pinned memory

例如：

```bash
asys profile --hggc-memory-usage=true --host-memory-sampling=true --python-backtrace=hggc python launch.py
```

**注意：**
+ asys Python 调用栈采集目前只支持 Python 3.8-3.12 版本
+ 暂时不支持使用别名的 Python 解释器（非官方的 python/python3 名称）启动应用场景的 Python 调用栈采集

#### 4.8.2. 采集 Python 函数 (Python Functions Trace)
asys 支持在不修改 python 源码的情况下采集 python 函数执行信息，并以 HGTX range 的形式展示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125072650/cb0ed9a292cb141953d505e85d5e5e45/python_sampling_config_1.png)

可通过`--python-functions-trace`选项以不同的模式指定函数，指定模式如下：

| python-functions-trace 参数选项 | 采集内容 |
| --- | --- |
| none | 默认值，不进行采集 |
| all | 采集 python 内所有函数 |
| module:`<module_name>` | 采集当前模块下所有函数，可以指定父模块，多个模块之间通过`,`分隔，例如：module:torch,threading |
| `<json_file>` | 根据 json 内指定的函数进行采集 |

可以通过`--python-functions-threshold`触发 Python 函数采集的 API 运行时长门限，单位纳秒（ns），默认 80000ns。

<a id="pStlT"></a>
通过 JSON 指定有如下三种方法：

+ 只填写 module 模块，默认采集当前模块下所有函数（模块可以是父模块，例如指定'torch'，则'torch.nn'下所有函数都进行采集）

```bash
[
    {    
        "module": "torch.nn.functional"
    },
    {
        "module": "threading"
    }
]
```

+ 填写指定 module 模块（完整层级模块名）下的 functions 函数名列表，可自定义 domain（默认值为'Python Hgtx'）

```bash
[
    {    
        "module": "torch.nn.functional",
        "domain": "Torch Domain",
        "functions": ["sigmoid","log_softmax"]
    }
]
```

+ 在指定模块下的函数名列表中，可以对 function 函数名进行属性覆盖，若 function 内指定 module，则覆盖父 module，若 function 内指定 domain，则该函数将在多个 domain 中进行展示

```bash
[
    {    
        "module": "torch.nn.functional",
        "domain": "Parent Domain",
        "functions": [
            "sigmoid",
            {"function": "Adadelta.step", "module": "torch.optim.adadelta", "domain": "Child Domain"}
        ]
    }
]
```

上述 JSON 内指定方法可混合使用，若指定逻辑发生冲突，则按最后一次指定方法进行采集。

例如：采集 python 内 torch 模块下所有函数，并设置 API 运行时长门限为 1000ns：

```bash
asys profile --python-functions-trace module:torch --python-functions-threshold 1000 python xx.py
```

**注意：**
+ asys python function trace 只支持 Python 3.8 及之后版本
+ 多线程场景下，子线程从创建到被采集可能存在延时
+ __main__模块下函数不支持指定
+ 应用程序在 fork 前后阶段，函数采集可能不准确

### 4.9. PyTorch 跟踪（实验特性）
asys 支持`--pytorch`选项使能对 PyTorch 框架的跟踪采集，支持的选项如下：

| `--pytorch`参数选项 | 采集内容 |
| --- | --- |
| autograd-shapes-hgtx | 采集 PyTorch 算子的名称、Tensor 参数的 shape 信息<br/>+ 通过`torch.autograd.profiler.emit_nvtx(record_shapes=True)`采集算子信息 |
| autograd-hgtx | 采集 PyTorch 算子的名称信息<br/>+ 通过`torch.autograd.profiler.emit_nvtx(record_shapes=False)`采集算子信息 |
| dispatch-function | 采集 PyTorch 算子的名称、所有入参的参数信息，可用于生成算子的单元测试 |
| function-wrapper | 对指定函数进行 wrapper，采集 PyTorch 算子的名称、所有入参的参数信息（默认采集部分相关算子函数） |
| functions-trace | 采集 PyTorch 函数的执行时间信息，该功能等价于`--python-functions-trace=module:torch` |
| none | 关闭 PyTorch 相关跟踪采集 |

`autograd-shapes-hgtx`和`autograd-hgtx`选项通过 HGTX range 标记 PyTorch 算子信息，HGTX range 示例如下：

```bash
# --pytorch autograd-shapes-hgtx
aten::mm, op_id = 1529997, sizes = [[4, 1024], [1024, 2048]], input_op_ids = [(1529991,0), (1529993,0)]

# --pytorch autograd-hgtx
aten::mm, op_id = 1515155
```

`dispatch-function`选项通过 HGTX range 标记 PyTorch 算子参数信息，HGTX range 示例如下：

```bash
# --pytorch dispatch-function
TorchFunction: torch.ops.aten.mm.default | arg_type=torch.Tensor, dtype=torch.float32, device=cuda:0, shape=(100, 100), requires_grad=False | arg_type=torch.Tensor, dtype=torch.float32, device=cuda:0, shape=(100, 100), requires_grad=False
```

`dispatch-function`选项支持指定采集更为详细的参数信息，例如采集 Tensor 参数的具体矩阵内容，`dispatch-function`支持的子选项如下：

| `dispatch-function`子选项 | 说明 |
| :--- | :--- |
| value-output-dir=`<dir>` | 使能对 tensor value 的记录，传入路径`<dir>`参数，路径为目录，用于存放采集过程中序列化后的 tensor pt 文件 |
| tensor-list | 使能对 tensor list 的记录，将输出 list 中每一个 tensor 元素的信息 |
| tensor-value-filter-name=`<name_regex>` | 当使能对 tensor value 记录时，可通过 op name 的正则表达式过滤，指定 op 输出 tensor value |
| tensor-value-filter-range=`<start/count>` | 当使能对 tensor value 记录时，可通过 op 出现的次数范围 range 进行过滤，指定开始记录的 op index 及记录的次数 |
| tensor-value-filter-shape=`<shape/shape>` | 当使能对 tensor value 记录时，可通过 op 内 tensor 参数的 shape 进行过滤，指定满足 tensor shape 的 op 输出 tensor value，例如`:tensor-value-filter-shape=100x50/50x100` |
| value-max-size=`<MiB>` | 指定存放 value size 文件的大小上限，默认为 1024 MiB |
| no-multi-thread | 关闭多线程 op 采集 |

多个子选项可通过冒号`:`拼接使用，例如：

```bash
--pytorch=dispatch-function:value-output-dir=/tmp/tensor-value:tensor-list:tensor-value-filter-name=torch.ops.aten.mm.default:tensor-value-filter-range=5/1:tensor-value-filter-shape=100x100/100x100
```

+ `--pytorch=dispatch-function`：使能 PyTorch 算子信息跟踪采集
+ `value-output-dir=/tmp/tensor-value`：使能 Tensor 数据采集功能，指定 Tensor 数据存储路径为`/tmp/tensor-value`
+ `tensor-value-filter-name=torch.ops.aten.mm.default`：指定 Tensor 数据采集的 PyTorch 算子名称的正则表达式，仅采集匹配`torch.ops.aten.mm.default`名称的算子的 Tensor 入参
+ `tensor-value-filter-range=5/1`：指定 Tensor 数据采集的 PyTorch 算子的范围，从本 PyTorch 算子的第 5 次出现时开始采集，采集 1 次参数取值
+ `tensor-value-filter-shape=100x100/100x100`：指定 Tensor shape 过滤条件，仅采集存在 2 个 Tensor 入参，且每个 Tensor shape 为 100x100 的 PyTorch 算子

**注意：**
+ `--pytorch=dispatch-function`选项需要满足 PyTorch 版本 >= 2.0
+ `--pytorch=dispatch-function`选项为实验特性，使能此选项可能导致应用崩溃或者应用行为异常。
+ 若使用 Docker 环境，Docker 启动需要增加`--privileged=true`参数

`function-wrapper`选项通过对指定函数 wrapper 并用 HGTX range 标记函数参数信息，HGTX range 示例如下：

```bash
# --pytorch function-wrapper
PythonFunction: sgl_kernel.top_k_top_p_sampling_from_probs | arg_type=torch.Tensor, dtype=torch.float32, device=cuda:0, shape=(1, 151936), requires_grad=False | arg_type=torch.Tensor, dtype=torch.int32, device=cuda:0, shape=(1,), requires_grad=False | arg_type=torch.Tensor, dtype=torch.float32, device=cuda:0, shape=(1,), requires_grad=False | kwarg_name=filter_apply_order, arg_type=str, value='joint' | kwarg_name=check_nan, arg_type=bool, value=False
```

`function-wrapper`选项默认配置部分相关算子函数信息

 主要涵盖：
 + ["torch.nn.functional", "torch.autograd", "sgl_kernel"] module 中的所有函数
 + ["torch.optim"] module 中优化器类的 step 函数
 + ["torch.nn.modules"] module 中基础模型类的 forward 函数

可通过额外子选项进行指定：

| `function-wrapper`子选项 | 说明 |
| :--- | :--- |
| module-whitelist=`<module/module>` | 指定 wrapper 该 module 下的所有纯 python 函数 |
| function-blacklist=`<name_regex/name_regex>` | 指定黑名单函数名的正则表达式，将在 wrapper 每个 module 下函数时按此规则进行过滤 |
| class-method-whitelist=`<'module'.'class'.'method'/'module'.'class'.'method'>` | 指定 module 下 class 类里的白名单函数（完整路径），当 wrapper 每个 module 时识别到类时，会匹配该白名单，对类的成员函数进行 wrapper；例如`:class-method-whitelist=torch.nn.modules.Bilinear.forward/torch.nn.modules.Identity.forward` |

多个子选项可通过冒号`:`拼接使用，例如：

```bash
--pytorch=function-wrapper:module-whitelist=torch/torch.nn.modules/sgl_kernel:function-blacklist=is_:class-method-whitelist=torch.nn.modules.LSTM.forward/torch.nn.modules.Linear.forward
```

+ `--pytorch=function-wrapper`：使能 PyTorch 函数包装跟踪采集。
+ `module-whitelist=torch/torch.nn.modules/sgl-kernel`：使能当指定的 module 被导入时，会扫描该 module 下的所有函数并进行 wrapper，例如当感知`import sgl-kernel`完成时，会扫描下`sgl-kernel`module 下的函数，例如`sgl_kernel.rmsnorm`函数。
+ `function-blacklist=is_`：指定黑名单函数名称正则表达，例如当扫描`torch`module 时，会过滤掉`is_`开头的函数，不对其进行 wrapper。
+ `class-method-whitelist=torch.nn.modules.LSTM.forward/torch.nn.modules.Linear.forward`：指定完整类成员函数路径，例如当扫描`torch.nn.modules`module 时，会识别到`Linear`类，其类中有函数匹配白名单函数`torch.nn.modules.Linear.forward`，会对其进行 wrapper。

**注意：**
+ `--pytorch=function-wrapper`选项为实验特性，wrapper 某些函数可能导致应用崩溃或者应用行为异常。
+ 若使用 Docker 环境，Docker 启动需要增加`--privileged=true`参数

### 4.10. PCCL 活动跟踪
PCCL 是 PPU 集合通信库。asys 支持采集 PCCL 的活动事件，以便查看通信过程的时序信息。通过 `-t pccl` 开启采集，例如：

```bash
asys profile -t pccl python test_pccl.py
```

时间线如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125070493/b849e5289de1111c809869523e11eac0/python_functions_trace_1.png)

PCCL 的时间线按照 channel 进行分类，channel 中按照 pipeline 分类。

### 4.11. RDMA 网卡指标跟踪
asys 支持周期采集系统内 RDMA 网卡的运行指标，如收发字节数、收发包平均大小、拥塞控制等信息，并在 Asight Systems GUI 中展示网卡各类指标随时间的变化情况：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125070833/0568d3b4ca10cf7df8083b5f33177442/python_functions_trace_2.png)

支持显示的内容有：

+ 网络接收速度
+ 网络发送速度
+ 网络接收包尺寸
+ 网络发送包尺寸
+ 网络接收 CNP 速率
+ 网络发送 CNP 速率
+ Send Wait

在框选时间范围时，tooltip 中会显示所选时间范围内的平均网络传输速度，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125063018/d51563a865d6c8473cc0fc29f450dd1b/nicmetrics_1.png)

可通过`--nic-metrics`选项使能网卡指标采集，asys 将采集系统内所有网卡设备的运行情况，并在 GUI 显示活跃的网卡设备。例如：

```bash
asys profile --nic-metrics true ./all_reduce_perf
```

+ `--nic-metrics true`使能网卡运行指标采集

可通过`--nic-device-include`选项指定网卡设备过滤的设备名称匹配`正则表达式`规则，多个`正则表达式`规则通过`,`连接。若网卡名称匹配任意一个指定的规则，该网卡将会被使能采集。例如：

```bash
asys profile --nic-metrics true --nic-device-include "bond" ./all_reduce_perf
```

+ `--nic-device-include "bond"`：采集名称中包含`bond`的网卡设备指标

```bash
asys profile --nic-metrics true --nic-device-include "bond,eth" ./all_reduce_perf
```

+ `--nic-device-include "bond,eth"`：采集名称中包含`bond`或者`eth`的网卡设备指标

可通过`--nic-metrics-frequency`选项控制采样频率，范围为 1Hz - 100kHz，默认为 1kHz

```bash
asys profile --nic-metrics true --nic-metrics-frequency 10000 ./all_reduce_perf
```

**注意：**
+ 受 RDMA 驱动接口影响，实际采样能力频率可能无法达到最高值，当设置采样频率大过实际采样频率最高值时，将以实际采样频率最高值进行采集
+ 启动 Docker 时配置--network host --device=/dev/infiniband

## 5. 统计系统与报告分析

本章介绍 Asight Systems 提供的三大分析功能：专家系统（识别性能问题并给出优化建议）、统计系统（对报告数据进行多维度统计）和报告比较（对比两份报告的性能差异）。

### 5.1. 专家系统
专家系统是 Asight Systems 中的智能分析系统，可以帮助识别常见的性能问题。专家系统分析报告中的事件，并提出优化建议，以便能够更有效地进行性能优化。

#### 5.1.1. 从命令行端使用专家系统
可以通过执行 `asys analyze` 子命令，使用 asys 专家系统对 `asysrep` 文件进行分析，生成一系列分析报告。

`asys analyze` 子命令的使用方式为：`asys analyze [option] <file.asysrep>`

##### 5.1.1.1. 指定报告分析类型
`asys analyze` 支持多种报告分析类型，通过 `asys analyze --help-rules ALL` 可查看分析类型的详细说明。

通过 `--rule` 选项可指定报告分析类型，该选项可以多次指定，也可以使用逗号分隔列表来指定多个分析类型。如果未指定报告分析类型，将使用默认报告分析类型来生成报告。

例如：指定使用`ppu_gaps`和`ppu_time_util`报告分析类型生成报告：

```bash
asys analyze --rule ppu_gaps,ppu_time_util report.asysrep
```

##### 5.1.1.2. 指定报告输出格式
`asys analyze` 支持通过 `--format` 选项指定统计报告输出格式。通过 `asys analyze --help-formats ALL` 可查看支持的输出格式和帮助信息。

+ column —— 输出到终端的默认格式，按照列表方式打印，易于阅读，支持选项：
    - `设置单位`：设置输出数据的单位和精度
+ csv —— 输出到文件的默认格式，按照 CSV 表格格式打印，易于导出表格以后续处理，支持选项：
    - `设置单位`：设置输出数据的单位和精度
+ xlsx —— 按照 xlsx 格式输出电子表格，支持在 Excel、WPS、LibOffice 等办公软件打开，统计结果更加易读，支持选项：
    - `设置单位`：设置输出数据的单位和精度

`设置单位`选项允许指定显示指定种类数据时使用的单位，支持的种类和单位选项如下：

+ `ratio` —— 比例 / 百分比类型数据，支持的单位：
    - `%` 或者 `.1%`：精确到小数点后一位
    - `.2%`：精确到小数点后两位
    - `.3%`：精确到小数点后三位

例如指定按照列表方式输出，`ratio`种类数据精确到小数点后三位：

```bash
asys analyze -r ppu_time_util --format column:ratio=.3% report.asysrep
```

**提示：**
若报告输出列较多，column 输出格式将默认隐藏部分列，可通过指定报告类型的`column`选项控制显示的列

##### 5.1.1.3. 指定报告输出类型
通过`--output`选项可指定报告输出的输出类型，目前有 3 种输出类型： 打印到 console 控制台，输出到文件，或者输出到命令。不指定默认打印到控制台。

通过`--output %`指定输出类型`%`表示输出到控制台 console，例如：

```bash
asys analyze --output % --rule ppu_gaps report.asysrep
```

通过`--output .`指定输出类型为`输出到asysrep报告所在目录`，则 asys 将会根据 asysrep 报告文件名、指定的报告分析类型和输出格式生成报告输出的文件名，输出文件名格式为：`<report_name>_<rule_name>.<format>`。例如指定`--output .`在报告所在目录生成`report.asysrep`的`ppu_gaps`分析类型的分析报告，本地报告文件名称为`report_ppu_gaps.csv`：

```bash
asys analyze --output . --rule ppu_gaps report.asysrep
```

通过`--output @post_command`指定输出结果通过`post_command`进行二次处理，分析报告的内容将通过管道传输到给定的命令。例如：通过`grep 1142417`匹配结果包含关键字`1142417`的结果：

```bash
asys analyze --output "@grep 1142417" --rule ppu_gaps report.asysrep
```

##### 5.1.1.4. 指定报告输出的列
`asys analyze`支持为每种报告类型指定输出的列，在输出统计结果时，仅会输出指定列的统计结果。在指定报告类型时，使用`column`选项指定列的名称，多个列通过`/`分割，例如：

```bash
asys analyze -r "ppu_gaps:column=Duration/Device ID" -r "ppu_time_util:column=In-Use/Device ID" report.asysrep
```

+ 统计报告`ppu_gaps`仅输出`Duration`和`Device ID`列
+ 统计报告`ppu_time_util`仅输出`In-Use`和`Device ID`列

##### 5.1.1.5. 指定统计时间范围
可通过`--filter-time`选项指定统计的时间范围，时间格式为`开始时间/结束时间`，单位为纳秒，时间指从采集开始的偏移时间，其中`开始时间`或者`结束时间`可以省略一种。例如指定统计从第 10 秒到第 20 秒的跟踪数据：

```bash
asys analyze --filter-time 10000000000/20000000000 --rule ppu_gaps report.asysrep
```

可通过`--filter-hgtx`选项通过 HGTX 标注指定统计的时间范围，当`--filter-hgtx`选项被指定时，将忽略`--filter-time`选项。

使用`--filter-hgtx`选项可指定匹配的 HGTX range 的名称、domain 和匹配索引，格式为`range_name@domain/index`，若匹配的 HGTX range 不存在 domain，则`@domain`可省略，否则`@domain`需要指定。

默认 asys 将使用匹配的第一个 HGTX range 作为统计的时间范围，此时`/index`部分可省略，若需要指定匹配索引，则通过`/index`指定，索引从 0 开始。

例如：使用名称为`self_attention`的 HGTX range 指定统计时间范围，无 domain，使用首个匹配的 HGTX range 的时间范围。

```bash
asys analyze --filter-hgtx self_attention --rule ppu_gaps report.asysrep
```

例如：使用名称为`pcclGroupEnd`的 HGTX range 指定统计时间范围，domain 为`NCCL`，使用第 9 个匹配的 HGTX range 的时间范围（索引为 8）。

```bash
asys analyze --filter-hgtx "pcclGroupEnd@NCCL/8" --rule ppu_gaps report.asysrep
```

**提示：**
+ asys analyze 输出的时间戳信息可能由于`--rule`选项不同而不同。若希望统一时间戳信息，可指定选项`--ts-normalize true`使能转换时间戳为 UTC 时间
+ asys analyze 支持通过选项`--ts-shift`手动调整时间戳偏移值，此选项可以和`--ts-normalize`配合使用

#### 5.1.2. 专家系统规则

##### 5.1.2.1. PPU 长时间空闲分析
分析和汇总 asysrep 报告中 PPU 长时间空闲的时间段（PPU bubble），并按照空闲时长降序输出。

对于各个 PPU 设备，对每个进程进行检查，从该设备上第一个 PPU 活动开始到该设备上最后一个 PPU 活动结束的时间范围内，查找满足设置门限的空闲时间。

依赖的 asys 采集选项：

+ `--trace hggc`

**分析规则**

当 PPU 没有下述活动时，视为 PPU 空闲：

+ 执行 kernel
+ 执行 memcpy / memset
+ 执行 video 编解码

按照`每进程、每PPU`级别，统计 PPU 空闲时间段。若空闲时间段大于参数`gap`设置的门限，则此空闲时间段汇入统计结果。

统计结果按照空闲时长排序降序输出。

`ppu_gaps`表格列说明如下：

```text
Row# : Row number of the PPU gap
Duration [ns] : Duration of the PPU gap
Start [ns] : Start time of the PPU gap
PID : Process identifier
Device ID : PPU device identifier
```

**命令行使用方法**

```bash
asys analyze --rule ppu_gaps report.asysrep
```

通过`--rule`选定`ppu_gaps`时，可通过拼接多个`:option`的方式指定分析的相关参数，可通过`asys analyze --help-rules ppu_gaps`查看具体帮助信息，支持的选项举例如下：

+ `rows=<limit>`：限制输出的 PPU 长时间空闲结果的条数
+ `gap=<threshold>`：设置长时间空闲的时间门限，单位为`毫秒`

例如：分析 PPU 长时间空闲，空闲时间门限为 20ms，输出空闲时长最长的前 10 条结果：

```bash
asys analyze --rule ppu_gaps:rows=10:gap=20 report.asysrep
```

报告结果示例如下：

```text
Row#,Duration,Start,PID,Device ID,
1,1232895501,126020393150,1142419,6,
2,1219910832,126016153086,1142417,4,
3,1219804936,126017799911,1142416,3,
...
```

**GUI 使用指南**

+ 规则设置（Settings）
    - Maximum number of results：限制输出的 PPU 长时间空闲结果的条数上限，默认值为 50
    - Minimum duration of PPU gaps in ms：设置长时间空闲的时间门限，单位为`毫秒`，默认值为 500
+ 表格右键菜单功能
    - 支持在 Timeline View 中高亮或缩放至所选的范围
+ 饼图统计：对每个进程/设备的长时间空闲的持续时间进行汇总。通过饼图可以查看哪个进程/设备的 bubble 更多。

##### 5.1.2.2. PPU 时间利用率分析
分析和汇总 asysrep 报告中 PPU 时间层面的利用率，并按照时间利用率升序输出。对于各个 PPU 设备，对每个进程进行基于 Range Mode 的检查，将该时间范围划分为相等的块（chunks），并计算每个块的 PPU 时间利用率。

如果选择了“PPU Active Time Range”模式，则统计的时间范围从该设备上的第一个 PPU 操作开始，到该设备上的最后一个 PPU 操作结束。如果选择了“Filtered Time Range”范围模式，则时间范围与指定的过滤时间范围相同。请注意，利用率是指“时间”利用率，而不是“资源”利用率。因此，一个简单的 memcpy 的“利用率”与调用所有资源的复杂 kernel 相同。如果多个操作在同一块中同时运行，则它们的利用率将加起来为 100%。展示的结果为利用率百分比小于设定阈值的块。如果多个连续块的利用率较低，则多个块将合并展示为一条结果，并加权平均计算利用率，因此得到的各条结果的时间长度可能不同。

依赖的 asys 采集选项：

+ `--trace hggc`

**分析规则**

当 PPU 有下述活动时，视为 PPU 繁忙：

+ 执行 kernel
+ 执行 memcpy / memset
+ 执行 video 编解码

按照`每进程、每PPU`级别，计算 PPU`整体有活动的时间`：从第一个活动开始到最后一个活动结束。

`整体有活动的时间`按照参数`chunks`分为等长的时间段，对每个时间段计算 PPU 在本时间段的时间利用率：`繁忙时间`/`时间段长度`。

时间利用率低于参数`threshold`的时间段将汇入统计结果。若多个相邻的时间段利用率均低于参数`threshold`，这些时间段将被合并计算利用率作为统计结果输出。

统计结果按照时间利用率升序输出。

**提示：**
+ 时间上重叠的 kernel / memcpy 等活动，重叠部分的时间不会重复计算，每个时间段的时间利用率不会高于 100%
+ 可通过 GUI 端通过在 timeline 界面圈选一段时间范围，右键`Filter and zoom in`指定过滤的时间范围
+ 可通过调整`chunks`和`threshold`参数计算整个报告的 PPU 时间利用率，例如：`asys analyze --rule ppu_time_util:threshold=100:chunks=1:range-mode=full report.asysrep`

`ppu_time_util`表格列说明如下：

```text
Row# : Row number of the chunk
In-Use [%] : Percentage of time the PPU is being used
Duration [ns] : Duration of the chunk
Start [ns] : Start time of the chunk
PID : Process identifier
Device ID : PPU device identifier
```

**命令行使用方法**

```bash
asys analyze --rule ppu_time_util report.asysrep
```

通过`--rule`选定`ppu_time_util`时，可通过拼接多个`:option`的方式指定分析的相关参数，可通过`asys analyze --help-rules ppu_time_util`查看具体帮助信息，支持的选项举例如下：

+ `rows=<limit>`：限制输出的 PPU 低利用率时间段的结果的条数
+ `threshold=<percent>`：设置 PPU 繁忙占比的百分比门限
+ `chunks=<number>`：PPU 整体有活动的时间段的切分个数
+ `range-mode=<mode>`：统计时间范围的选择模式，支持`active`和`full`模式：
    - `active`：默认模式，时间范围从第一个 PPU 活动开始，到最后一个 PPU 活动结束截止
    - `full`：时间范围选取为用户指定的统计时间范围，若没有指定统计时间范围，则统计报告整体的时间范围
+ `compute-pipe=<index_list>`：参与统计的 Compute Pipe 列表，多个 Pipe Index 之间通过`/`分割，若不指定，默认统计所有的 Compute Pipe，可用于分析 MPS 模式使能时的时间利用率
+ `merge-process-id`：合并进程统计结果，按照 PPU 设备级别统计时间利用率

例如：分析 PPU 时间利用率，利用率门限为 60%，时间等分为 80 段，输出利用率最低的前 20 条结果：

```bash
asys analyze --rule ppu_time_util:rows=20:threshold=60:chunks=80:range-mode=full report.asysrep
```

报告结果示例如下：

```text
Row#,In-Use,Duration,Start,PID,Device ID,
1,0.000000,12411,124667294244,1142418,5,
2,0.000000,7648,124667369358,1142419,6,
3,0.000000,7648,124667378918,1142419,6,
4,2.425268,7092,124667285970,1142418,5,
5,4.258319,7092,124667278287,1142418,5,
...
```

**GUI 使用指南**

+ 规则设置（Settings）
    - Maximum number of results：限制输出的 PPU 低利用率时间段的结果的条数上限，默认值为 50
    - MPS Compute Pipe Index：设置参与统计的 MPS Compute Pipe Index，默认为 All（统计所有的 Compute Pipe）
    - Minimum percentage of PPU utilization：设置 PPU 繁忙占比的百分比门限，输出 PPU 时间利用率低于该值的区间，默认值为 50
    - Number of equal-duration chunks：PPU 整体有活动的时间段的切分个数，默认值为 100
    - Time Range Mode：设置统计时间范围的模式
        * `PPU Active Time Range`：默认模式，时间范围从第一个 PPU 活动开始，到最后一个 PPU 活动结束截止
        * `Filtered Time Range`：时间范围选取为用户指定的统计时间范围，若没有指定统计时间范围，则统计报告整体的时间范围
+ 表格右键菜单功能
    - 支持在 Timeline View 中高亮或缩放至所选的范围
+ 饼图统计：对每个进程/设备的低利用率的持续时间进行汇总。通过饼图可以查看哪个进程/设备的利用率更低。

### 5.2. 统计系统
统计系统是 Asight Systems 中的一项重要功能，它对报告中的数据进行多维度统计，可以通过这些统计结果全面了解程序的性能。

#### 5.2.1. 从 GUI 端使用统计系统
在 GUI 中，可以通过下方 tab 中的 "Stats System View" 切换到统计系统页面。统计系统页面如下所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125052500/e11f229b95a879d74db0ca96801cd2c8/gui_1.png)

1. 规则列表，可以在此选择统计规则，支持搜索
2. 当前生效的参数配置，鼠标悬停时会显示参数的详细信息
3. 搜索框，支持搜索和过滤两种模式
4. 规则参数配置对话框，可以在此改变当前统计规则的配置
5. 统计结果的饼图，以及相关的优化建议，可以通过顶部 tab 切换
6. 统计结果表格，显示当前规则的分析结果，可以通过右键菜单导出分析结果

##### 5.2.1.1. 设置统计区间
可以通过 Timeline View 的 filter 功能设置一个时间区间，统计系统只会对该时间区间内的事件进行统计。在 Timeline View 中按住鼠标左键拖动，在选定的区间内打开右键菜单，点击 "Filter and Zoom in"，即可设置统计区间。

##### 5.2.1.2. 跳转至 Timeline View
对于部分规则（目前包括 Trace 和 Detail 类的规则），支持从表格中跳转至 Timeline View，可以通过在表格中打开右键菜单选择跳转的方式。

##### 5.2.1.3. 统计结果的饼图
规则的统计结果除了以表格的形式展示外，统计系统还支持以饼图的形式展示结果：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125053016/61318493cae8ccd15fb6b3207fa49de1/gui_2.png)

上图中：

1. 当前饼图实现的是以"Name"为 key，将右侧的表格的每一行进行分类，每一类将"Duration"这一列的值进行累加，最终计算"Duration"的时间占比显示在饼图中。这里的 key 可以通过组合框进行选择
2. 设置显示的扇形数量
3. 饼图，每个扇形显示的百分比是每"Name"的"Duration"占整体"Duration"的时间占比
4. 图例，上图中显示的"Name"，并按"Duration"的降序排列

饼图中的扇形支持点击，点击后表格只会显示对应 key 的行。如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125053449/53f6b41900d3b61654a3f4ba74bcfadf/gui_3.png)

上图中，点击了 name 为 add(int*,int*,int*)的扇形，因此在右侧表格中只会显示该名字的项，其他项被隐藏。再次点击扇形或饼图空白部分表格会复位

##### 5.2.1.4. 通过选中行来统计列和
统计系统中，部分规则支持通过选中行来统计列和，并将结果显示在表头中，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125053782/22f0e5a9b0fb3852aad9dcde419a7b86/gui_4.png)

上图中选中了前三行，这三行的 Time 和 Total Time 列的值会累加显示在表头中

#### 5.2.2. 从命令行端使用统计系统
在命令行端，可以通过执行`asys stats`命令，对指定报告进行统计分析，提供高效的统计功能和跟踪导出功能，分析结果支持输出到控制台、文件或命令管道，方便用户对数据进行查阅和二次处理。部分统计和分析功能也可通过 Asight Systems GUI 查看结果。

`stats`子命令的使用方式为：

```bash
asys stats [option] <file.asysrep>
```

可以在使用`asys profile`命令采集跟踪时，通过指定`--stats true`选项，在生成报告后输出报告统计结果，输出结果和使用`asys stats report.asysrep`类似。例如：

```bash
asys profile --stats true python test_linear.py
```

+ `--stats true`：采集结束输出报告统计结果

##### 5.2.2.1. 指定统计报告类型
`asys stats`支持多种统计报告类型，通过`asys stats --help-reports ALL`可查看统计报告类型的详细说明。

通过`--report`选项可指定统计报告类型，该选项可以多次指定，也可以使用逗号分隔列表来指定多个统计报告类型。若未指定统计报告类型，将使用默认统计报告类型来生成报告。

例如：指定使用`hggc_ppu_kern_sum`和`device_memory_usage_summary`统计报告类型生成报告：

```bash
asys stats --report hggc_ppu_kern_sum,device_memory_usage_summary report.asysrep
```

`--report`选项指定的报告类型可能包含配置选项，配置选项的逗号`,`和冒号`:`需要使用反斜线`\`逃脱，若在`bash`等命令行环境中使用，配置选项的取值请使用`"`包裹，例如：

```bash
asys stats --report ppu_op_sum:range-include="seqlen_q\:1\,is_fixed_seqs\:0\,head_dim\:128/data_type\:fp8\,groups\:1\,m\:925":range-exclude="em\:0\,gpu\:1" report.asysrep
```

##### 5.2.2.2. 指定报告输出格式
`asys stats`支持多种输出格式，通过`asys stats --help-formats ALL`可查看支持的输出格式和帮助信息。

通过`--format`选项可指定统计报告输出格式。该选项可以多次指定，也可以使用逗号分隔列表来指定多个统计报告输出格式。

若未指定报告输出格式，输出到终端默认为 column 格式，输出到文件默认为 csv 格式

+ column：按照列表方式打印，易于阅读的输出格式，支持选项列举如下：
    - `设置单位`：设置输出数据的单位和精度
+ csv：按照 csv 表格格式打印，易于导出表格以后续处理，支持选项列举如下：
    - `设置单位`：设置输出数据的单位和精度
+ xlsx：按照 xlsx 格式输出电子表格，支持在 Excel、WPS、LibOffice 等办公软件打开，统计结果更加易读，支持选项列举如下：
    - `设置单位`：设置输出数据的单位和精度

`设置单位`选项允许指定显示指定种类数据时使用的单位，支持的种类和单位选项列举如下：

+ `ratio`：比例 / 百分比类型数据，支持的单位：
    - `%`或者`.1%`：精确到小数点后一位
    - `.2%`：精确到小数点后两位
    - `.3%`：精确到小数点后三位

例如指定按照列表方式输出，`ratio`种类数据精确到小数点后三位：

```bash
asys stats -r hgtx_ppu_proj_sum --format column:ratio=.3% report.asysrep
```

**提示：**
+ 若报告输出列较多，column 输出格式将默认隐藏部分列，可通过指定统计报告类型的`column`选项控制显示的列
+ xlsx 格式不支持输出到终端，若指定输出到终端，将按照`column`格式输出

##### 5.2.2.3. 指定报告输出类型
`asys stats`支持多种报告输出类型，包括输出到 console 控制台，输出到文件和输出到命令。

通过`--output`选项可指定报告输出的输出类型，该选项可以多次指定，也可以使用逗号分隔列表来指定多个报告输出类型。不指定时，默认输出到控制台。

+ 如果指定的输出名称是 `"%"`，则分析结果会显示在控制台上。
+ 如果输出名称以 `"@"`开头，表示输出目标是一个要执行的命令。
+ 除此之外，任何其他输出名称都被认为是`文件输出的目录`和`文件名前缀`的组合，格式为`<output_dir>/<prefix>`。前缀可以为空，路径最后一个`/`之前的路径被认为是输出目录。

输出类型对照表如下： 

| 输出类型 | 参数写法 | 说明 |
| --- | --- | --- |
| **控制台输出** | `--output %` | 将分析结果直接打印到控制台（stdout），不生成文件。 |
| **默认文件输出** | `--output .` | 输出到 asysrep 报告所在目录，使用默认基础文件名，格式为：<br/>`<asys_report_name>_<stats_report_name>.<format>` |
| **自定义文件输出** | `--output <output_dir>/<prefix>` | 输出到`<output_dir>`目录，文件名格式为<br/>`<prefix>_<stats_report_name>.<format>` |
| **命令管道输出** | `--output @<command>` | 将分析结果通过管道传给指定命令的标准输入，命令的 stdout/stderr 仍输出到控制台。 |

使用`--output %`可以将分析结果直接输出到控制台 console，例如：

```bash
asys stats --output % --report hgtx_sum report.asysrep
```

使用`--output .`可以将分析结果输出到`asysrep报告所在目录`则 asys 将会根据 asysrep 报告文件名、指定的统计报告类型和输出格式生成报告输出的文件名，

例如：指定`--output .`在报告所在目录生成`report.asysrep`的`hggc_api_sum`类型的统计报告，本地报告文件名称为`report_hggc_api_sum.csv`：

```bash
asys stats --output . --report hggc_api_sum report.asysrep
```

例如：指定`--output /test/mytest`，在目录/test 生成`report.asysrep`的`hggc_api_sum`类型的统计报告，本地报告文件名称为`mytest_hggc_api_sum.csv`：

```bash
asys stats --output /test/mytest --report hggc_api_sum report.asysrep
```

使用`--output @post_command`可以将统计报告的输出结果通过指定的命令行`post_command`进行二次处理，统计结果将通过管道传输到给定的命令。

例如：使用`grep 1142417`筛选结果包含关键字`1142417`的结果：

```bash
asys stats --output "@grep 1142417" --report device_memory_usage_summary report.asysrep
```

##### 5.2.2.4. 指定报告输出的列
`asys stats`支持为每种统计报告类型指定输出的列，在输出统计结果时，仅会输出指定列的统计结果。在指定统计报告类型时，使用`column`选项指定列的名称，多个列通过`/`分割，例如：

```bash
asys stats -r "hggc_ppu_kern_sum:column=Time/Name" -r "hgtx_ppu_proj_sum:column=Range/Total Proj Time" report.asysrep
```

+ 统计报告`hggc_ppu_kern_sum`仅输出`Time`和`Name`列
+ 统计报告`hgtx_ppu_proj_sum`仅输出`Range`和`Total Proj Time`列

##### 5.2.2.5. 指定算子识别规则
`asys stats`的统计结果中包含 PPU 算子相关对比，通过内置的 PPU 算子识别规则识别报告中的算子并统计相关性能，可通过`--ppu-op-config`选项自定义算子识别规则，可指定正则表达式通过匹配 HGTX range 名称或者 kernel 名称识别指定算子类型，格式为`算子类型=匹配类型：过滤规则`，可多次通过`--ppu-op-config`选项创建多个算子识别规则，例如：

```bash
asys stats --ppu-op-config GEMM=kernel:gemv --ppu-op-config Pytorch=hgtx:aten report.asysrep
```

+ `--ppu-op-config GEMM=kernel:gemv`：匹配 kernel 名称包含`gemv`关键字的 kernel，分类到`GEMM`算子类型
+ `--ppu-op-config Pytorch=hgtx:aten`：匹配 HGTX range 名称包含`aten`关键字，HGTX range 关联的 PPU 活动分类到`PyTorch`算子类型

##### 5.2.2.6. 指定统计时间范围
可通过`--filter-time`选项指定统计的时间范围，时间格式为`开始时间/结束时间`，单位为纳秒，时间指从采集开始的偏移时间，其中`开始时间`或者`结束时间`可以省略一种。例如指定统计从第 10 秒到第 20 秒的跟踪数据：

```bash
asys stats --filter-time 10000000000/20000000000 --report device_memory_usage_summary report.asysrep
```

可通过`--filter-hgtx`选项通过 HGTX 标注指定统计的时间范围，当`--filter-hgtx`选项被指定时，将忽略`--filter-time`选项。

使用`--filter-hgtx`选项可指定匹配的 HGTX range 的名称、domain 和匹配索引，格式为`range_name@domain/index`，若匹配的 HGTX range 不存在 domain，则`@domain`可省略，否则`@domain`需要指定。

默认 asys 将使用匹配的第一个 HGTX range 作为统计的时间范围，此时`/index`部分可省略，若需要指定匹配索引，则通过`/index`指定，索引从 0 开始。

例如：使用名称为`self_attention`的 HGTX range 指定统计时间范围，无 domain，使用首个匹配的 HGTX range 的时间范围。

```bash
asys stats --filter-hgtx self_attention --report device_memory_usage_summary report.asysrep
```

例如：使用名称为`pcclGroupEnd`的 HGTX range 指定统计时间范围，domain 为`NCCL`，使用第 9 个匹配的 HGTX range 的时间范围（索引为 8）。

```bash
asys stats --filter-hgtx "pcclGroupEnd@NCCL/8" --report device_memory_usage_summary report.asysrep
```

##### 5.2.2.7. 参数匹配规则
专家系统的报告生成需要指定 3 个方面的参数：

1）报告类型（以及相关参数）；  
2）报告格式（以及相关参数）；  
3）输出类型（文件名、控制台或命令）。    

这三个参数均可以多次指定，也可以使用逗号分隔列表来指定多个选项。

第一个报告会使用第一个指定的格式，并通过第一个指定的输出类型进行呈现；第二个报告则使用第二个格式，配合第二个输出，以此类推。

如果指定的报告数量多于格式或输出类型数量，那么会通过重复列表中最后一个指定的元素（或者默认值，如果未指定）来扩展格式和/或输出列表，从而使它们与报告的数量相匹配。

例如：

下面的命令将生成三个报告。其中 "hggc_api_sum" 报告将以 CSV 格式输出到文件 "report1_hggc_api_sum.csv"。另外两个报告 "osrt_sum" 和 "hgtx_sum" 将以 CSV 数据的形式输出到控制台。尽管指定了三个报告，但只指定了一个输出格式和两个输出类型。为了匹配报告数量，格式列表和输出列表都会通过重复最后一个元素来扩展到与报告列表数量一致。

```bash
asys stats --report hggc_api_sum --report osrt_sum --report hgtx_sum --format csv --output .,% report1.asysrep
```

**提示：**
+ asys stats 输出的时间戳信息可能由于`--report`选项不同而不同。若希望统一时间戳信息，可指定选项`--ts-normalize true`使能转换时间戳为 UTC 时间
+ asys stats 支持通过选项`--ts-shift`手动调整时间戳偏移值，此选项可以和`--ts-normalize`配合使用

#### 5.2.3. 统计系统规则

##### 5.2.3.1. 设备内存使用分组汇总
分析和汇总 asysrep 报告中多种数据种类的 PPU 设备内存使用记录，按照分组（如算子库、框架）统计内存使用量，输出各个分组的内存使用汇总和详细信息。

依赖的 asys 采集选项：

+ `--hggc-memory-usage device`

**统计规则**

按照`每进程、每PPU`级别，汇总已申请且没有释放的 PPU 设备内存使用记录。

对于每个申请且没有释放的内存使用记录，根据内存申请时的调用栈信息（帧的排列顺序，每帧匹配的关键字），匹配分组规则。

内存使用记录可能匹配到多个分组，输出的分组信息将显示记录归属的所有分组，通过`/`间隔。

汇总每种分组组合的内存使用量，结果按照内存使用量汇总降序排列。

`device_memory_usage_detail`表格列说明如下：

```text
Row# : Row number of the device memory usage
PID : Process identifier
Device ID : PPU device identifier
Group List : Memory usage belonged group list, split by '/'
Time [ns] : Memory usage timestamp
TID : Thread identifier
Context ID : Context identifier
Memory : Memory identifier
Size [bytes] : Memory usage size
Access Flag : Memory access flag
Event ID : Memory usage event identifier
```

`device_memory_usage_summary`表格列说明如下：

```text
Row# : Row number of the device memory usage
PID : Process identifier
Device ID : PPU device identifier
Group List : Memory usage belonged group list, split by '/'
Memory Usage [bytes] : Device memory usage
```

**命令行使用方法**

可通过`-r <rule>:usage-mode=<mode>`选项指定数据种类

`device_memory_usage_detail`规则支持两种数据种类：

+ 'all'：支持导出申请和释放的内存跟踪
+ 'unreleased'：支持导出泄漏的内存跟踪（默认值）

`device_memory_usage_summary`规则支持四种数据种类：

+ 'alloc-count': 申请的内存次数汇总
+ 'alloc-size': 申请的内存量汇总
+ 'unreleased-count': 泄漏的内存次数汇总
+ 'unreleased-size': 泄漏的内存量汇总（默认值）

可通过`--callstack-group-config`选项添加分组规则，可通过`:match-first-group`选项指定分组策略按第一个匹配组（默认匹配所有组）

通过`--report`指定分组统计报告，举例如下：

```bash
asys stats -r device_memory_usage_summary:usage-mode=unreleased-size:match-first-group \
--callstack-group-config "acompute=(libacblas|libacdnn)" \
--callstack-group-config "launch_kernel=libtorch/LaunchKernel" \
--callstack-group-config "loss=loss.py" \
report.asysrep
```

+ `-r device_memory_usage_summary`：指定设备内存使用汇总报告
+ `:usage-mode=unreleased-size`：指定泄漏的内存量汇总
+ `:match-first-group`：指定只归属于第一个匹配的组
+ `--callstack-group-config "acompute=(libacblas|libacdnn)"`：
    - 创建分组名称`acompute`
    - 匹配的正则表达式`(libacblas|libacdnn)`：匹配调用栈包含`libacblas`或者`libacdnn`关键字的内存使用
+ `--callstack-group-config "launch_kernel=libtorch/LaunchKernel"`：
    - 创建分组名称`launch_kernel`
    - 匹配的正则表达式`libtorch/LaunchKernel`：匹配调用栈层级关系：父函数所在帧包含关键字`libtorch`，且子函数所在帧包含关键字`LaunchKernel`的内存使用。
        * 匹配的父、子函数所在的调用栈帧之间允许存在未匹配的调用栈帧
+ `--callstack-group-config "loss=loss.py"`
    - 创建分组名称`loss`
    - 匹配的正则表达式`loss.py`：匹配调用栈包含`loss.py`关键字的内存使用
        * 匹配的调用栈支持 python 调用栈

分组的统计结果输出示例如下，按照 CSV 格式输出，可通过`--output`指定输出到 csv 文件等处理。

```text
PID,Device ID,Group List,Memory Usage,
1873,0,launch_kernel,213174,
1873,0,others,48674898730,
1873,0,acompute,1610624066,
1873,0,loss,28591
```

+ 报告内容提供了分组`acompute`、`launch_kernel`、`loss`的已申请且未释放的内存汇总，单位`字节`
+ 不归属于用户指定组的内存使用，汇总到缺省的`others`分组

设备内存使用分组统计功能提供下述两种报告类型，可通过`--report`指定单个或者多个报告：

+ `device_memory_usage_summary`：输出每进程、每设备、每分组的已申请且未释放的内存汇总
+ `device_memory_usage_detail`：输出每笔申请且未释放的内存使用记录，以及所属的分组

具体设备内存使用分组统计功能的描述信息，可通过` --help-reports`选项查询，包含功能描述，输出格式说明等，例如执行`asys stats --help-report device_memory_usage_summary`，输出结果示例如下：

```bash
root@eb4c64fd3401:~# asys stats --help-report device_memory_usage_summary
device_memory_usage_summary -- Device Memory Usage Summary

    Options:
        match-first-group
            Optional argument. When used with --callstack-group-config:
            If given, only matching the first callstack group.
            Default is matching all callstack group.
        usage-mode=<mode>
            Possible values are 'alloc-size', 'unreleased-size', 'alloc-count' or 'unreleased-count'.
            Specify the memory usage mode.
            If 'alloc-size', statistic overall allocated device memory usage.
            If 'unreleased-size', statistic allocated but not freed device memory usage.
            If 'alloc-count', statistic overall allocated device memory count.
            If 'unreleased-count', statistic allocated but not freed device memory count.
            Default is 'unreleased-size'.
        Use --filter-time / --filter-hgtx to specify report time range.
        Use --callstack-group-config to create report group configuration.
        Try 'asys stats --help' for more information.
        
    Output:
        Row# : Row number of the device memory usage
        PID : Process identifier
        Device ID : PPU device identifier
        Group List : Memory usage belonged group list, split by '/'
        Memory Usage [bytes] : Device memory usage

    Group and statistic device memory usage of specified mode,
    If 'alloc-size' mode,  display allocated device memory usage summary.
    If 'alloc-count' mode, display allocated device memory count summary.
    If 'unreleased-size' mode, display allocated but not freed device memory usage summary.
    If 'unreleased-count' mode, display allocated but not freed device memory count summary.
```

当内存使用记录分组匹配策略按匹配多个分组时，报告输出的分组信息将显示记录归属的所有分组，通过`/`间隔，例如：

```bash
acompute/launch_kernel
```

+ 内存使用同时归属于`acompute`和`launch_kernel`分组
+ 若分组匹配策略按匹配第一组，则只归属于第一个满足条件的分组
+ 分组的排列顺序取决于命令行选项`--callstack-group-config`的创建分组顺序

通过选项`--callstack-group-config`可创建分组并通过正则表达式指定匹配规则，格式为`group_name=frame_filters`，其中`frame_filters`可指定多个帧的匹配正则表达式，格式为：`frame_regex1/frame_regex2/...`，帧匹配正则表达式之间通过`/`间隔，帧的排列方向为`从父函数到子函数方向排列`。分组的匹配规则说明如下：

+ 帧的匹配方式为：若正则表达式可`部分匹配`调用栈的`库名称`或者`函数签名`，则判定帧匹配
+ 调用栈的匹配方式为：若调用栈中匹配的帧的层级关系，符合`frame_filters`中指定的层级关系，则判定分组匹配

选项`--callstack-group-config`举例如下，通过多次使用`--callstack-group-config`创建多个分组，每个分组指定匹配多个帧的规则：

```bash
--callstack-group-config "torch=libtorch" --callstack-group-config "acompute=(libacblas|libacdnn)" --callstack-group-config "buffer_init=_to_copy/empty_strided"
```

**注意：**
- 若没有通过`--callstack-group-config`添加分组规则，将会使用默认内置的分组规则
- 当多个`--callstack-group-config`创建的分组名称相同时，匹配任一分组规则的内存使用记录，将被归属到本分组

**GUI 使用指南**

+ 规则设置（Settings）
    - Usage Mode：统计数据种类。
        - `Device Memory Usage Detail`规则支持两种数据种类：
            * Unreleased Alloc Trace：支持导出泄漏的内存跟踪（默认值）
            * All Alloc and Free Trace：支持导出申请和释放的内存跟踪
        - `Device Memory Usage Summary`规则支持四种数据种类：
            * Unreleased Alloc Size: 泄漏的内存量汇总（默认值）
            * Total Alloc Size: 申请的内存量汇总
            * Unreleased Alloc Count: 泄漏的内存次数汇总
            * Total Alloc Count: 申请的内存次数汇总
    - Group Config：创建分组并通过正则表达式指定匹配规则。格式为`group_name=frame_filters`，其中`frame_filters`可指定一个或多个帧的匹配正则表达式，格式为：`frame_regex1/frame_regex2/...`，帧匹配正则表达式之间通过`/`间隔，帧的排列方向为`从父函数到子函数方向排列`。
    - Only match the first group in order：指定只归属于按从上至下顺序第一个匹配的组。默认为不勾选，即归属于所有匹配的组。
+ 表格右键菜单功能
    - `Device Memory Usage Detail`规则右键菜单支持在 Timeline View 中高亮或缩放至所选内存跟踪
+ 饼图统计：对每个 group/进程/设备的未释放内存使用情况进行汇总。通过饼图可以查看每个 group/进程/设备可能存在的内存泄露情况。

##### 5.2.3.2. HGGC API 汇总
汇总 asysrep 报告中 HGGC API 的耗时，按照 API 总耗时降序输出。

**统计规则**

按照`每HGGC API名称`级别进行统计，累加相同名称 API 的耗时时间，按照 API 总耗时降序输出。

`hggc_api_sum`表格列说明如下：

+ 注意“Time”列是根据“Total Time”列的总和计算得出的，表示该函数占所有列出函数执行时间的百分比，而不是根据应用执行时间得到的百分比。

```text
Row# : Row number of the HGGC API summary
Time [%] : Percentage of 'Total Time'
Total Time [ns] : Total time used by all executions of this function
Num Calls : Number of calls to this function
Avg [ns] : Average execution time of this function
Med [ns] : Median execution time of this function
Min [ns] : Smallest execution time of this function
Max [ns] : Largest execution time of this function
StdDev [ns] : Standard deviation of the time of this function
Name : Name of the function
```

**命令行使用方法**

依赖的 asys 采集选项：

+ `--trace hggc`

```bash
asys stats -r hggc_api_sum report.asysrep
```

可通过`asys stats --help-report hggc_api_sum`查看具体帮助信息。

报告结果示例如下：

```text
Row#,Time (%),Total Time (ns),Num Calls,Avg (ns),Med (ns),Min (ns),Max (ns),StdDev (ns),Name,
1,84.9,393100090,342,1149415,98746,3981,11001565,2011747,"hgMemcpyHtoDAsync_v2",
2,4.3,19851112,1297,15305,5351,2893,3860175,147778,"hgLaunchKernel",
3,2.9,13492044,1486,9079,2861,613,3707197,108998,"hgEventQuery",
4,2.9,13487638,1495,9021,6027,3191,222379,14733,"hggcLaunchKernel",
...
```

**GUI 使用指南**

+ 规则设置（Settings）
    - 该规则没有可以配置的设置选项
+ 饼图统计：对每个 HGGC API 的耗时进行汇总。

##### 5.2.3.3. HGGC API 跟踪
导出 asysrep 报告中的 HGGC API 跟踪数据，按照 API 执行时间升序输出

依赖的 asys 采集选项：

+ `--trace hggc`

**统计规则**

`每HGGC API调用`导出一行数据，按照 API 执行时间升序输出。

`hggc_api_trace`表格列说明如下：

```text
Row# : Row number of the HGGC API trace
Start [ns] : Timestamp when API call was made
Duration [ns] : Length of API calls
Name : API function name
CorrID : Correlation used to map to other HGGC traces
Pid : Process ID that made the call
Tid : Thread ID that made the call
Thread Name : Name of thread that called API function
```

**命令行使用方法**

```bash
asys stats -r hggc_api_trace report.asysrep
```

可通过`asys stats --help-report hggc_api_trace`查看具体帮助信息。

报告结果示例如下：

```text
Row#,Start (ns),Duration (ns),Name,CorrID,Pid,Tid,Thread Name,
1,41550,12737,"cudaProfilerStart",0,104699,104699,"python",
2,938476,28340,"cudaLaunchKernel",130170,104699,104699,"python",
3,999414,9382,"cudaLaunchKernel",130171,104699,104699,"python",
...
```

**GUI 使用指南**

+ 规则设置（Settings）
    - 该规则没有可以配置的设置选项
+ 表格右键菜单功能
    - 支持在 Timeline View 中高亮或缩放至所选 HGGC API
+ 饼图统计：对 HGGC API 的耗时进行汇总。支持切换至以进程级别对 HGGC API 耗时进行统计。

##### 5.2.3.4. HGGC Kernel 执行跟踪
导出 asysrep 报告中的 HGGC kernel 通过 API launch 启动到 Kernel 实际执行的跟踪数据，根据本 kernel 的 launch API 的起始时间升序输出。

**统计规则**

导出结果组织如下：`每Kernel执行信息`导出一行数据，根据本 kernel 的 launch API 的起始时间升序输出。

对于 HGGC Graph 等单个 HGGC API 关联多个 Kernel 的场景，每个 Kernel 导出一行数据。

Kernel Launch 后的等待时间相关列（Queue Start / Queue Dur）的计算方式如下：

+ 认为 Kernel 存在等待时间：Kernel 实际执行开始时间 > 执行 HGGC API 结束时间
+ 等待时间计算：Kernel 实际执行开始时间 - 执行 HGGC API 结束时间
+ 若 Kernel 在 HGGC API 执行结束前即开始执行，则 Queue Start / Queue Dur 列标记为无效值`-`

`hggc_kern_exec_trace`表格列说明如下：

```text
Row# : Row number of the kernel trace
API Start [ns] : Start timestamp of HGGC API launch call
API Dur [ns] : Duration of HGGC API launch call
Queue Start [ns] : Start timestamp of queue wait time, if it exists
Queue Dur [ns] : Duration of queue wait time, if it exists
Kernel Start [ns] : Start timestamp of HGGC kernel
Kernel Dur [ns] : Duration of HGGC kernel
Total Dur [ns] : Duration from API start to kernel end
PID : Process ID that made kernel launch call
TID : Thread ID that made kernel launch call
DevId : HGGC Device ID that executed kernel (which PPU)
API Function : Name of HGGC API call used to launch kernel
GridXYZ : Grid dimensions for kernel launch call
BlockXYZ : Block dimensions for kernel launch call
Kernel Name : Name of HGGC Kernel
```

**命令行使用方法**

依赖的 asys 采集选项：

+ `--trace hggc`

```bash
asys stats -r hggc_kern_exec_trace report.asysrep
```

可通过`asys stats --help-report hggc_kern_exec_trace`查看具体帮助信息，支持的选项列举如下：

+ base：导出 kernel 的短名称（仅函数名，不包含参数）
+ mangled：导出 kernel 的 mangled 名称

默认导出 HGGC Kernel 的名称为 demangle 之后的名称。

报告结果示例如下：

```text
Row#,API Start (ns),API Dur (ns),Queue Start (ns),Queue Dur (ns),Kernel Start (ns),Kernel Dur (ns),Total Dur (ns),PID,TID,DevId,API Function,GridXYZ,BlockXYZ,Kernel Name,
1,504935256,20348911,525284167,21237024,526172280,357034784,378271808,631660,631660,0,"hggcLaunchKernel","2 1 1","512 1 1","pcclKernel_AllReduce_RING_LL_Sum_int8_t(pcclWorkElem)",
2,845563829,20332834,865896663,20934656,866498485,17898735,38833391,631660,631660,1,"hggcLaunchKernel","2 1 1","512 1 1","pcclKernel_AllReduce_RING_LL_Sum_int8_t(pcclWorkElem)",
3,884469702,40488,884510190,627234,885096936,16944871,17572105,631660,631660,0,"hggcLaunchKernel","2 1 1","512 1 1","pcclKernel_AllReduce_RING_LL_Sum_int8_t(pcclWorkElem)",
...
```

**GUI 使用指南**

+ 规则设置（Settings）
    - Kernel Name Mode：Kernel Name 的展示模式。包括三种模式：
        * Base：导出 kernel 的短名称（仅函数名，不包含参数）
        * Mangled：导出 kernel 的 mangled 名称
        * Demangled：导出 kernel 的 demangle 之后的名称（默认值）
+ 表格右键菜单功能
    - 支持在 Timeline View 中高亮或缩放至所选 HGGC API
    - 支持在 Timeline View 中高亮或缩放至所选的 Device Activity
+ 饼图统计：对所有 kernel/进程/设备的 kernel 执行耗时进行汇总。

##### 5.2.3.5. HGGC Kernel Grid Block 汇总
统计 asysrep 报告中 HGGC kernel grid block 等信息，输出`每kernel名称，每grid size，每block size`的统计信息。

依赖的 asys 采集选项：

+ `--trace hgtx,hggc`

**统计规则**

统计方式：

+ 将`相同kernel名称`且`相同grid size`且`相同block size`的 Kernel 执行信息进行汇总：Kernel 执行时间，出现次数等。
+ 若使能`hgtx-name`选项，`kernel名称`包含拼接的 HGTX range 名称

统计结果组织如下：`每kernel名称，每grid size，每block size`导出一行数据，结果按照`Total Time`列降序输出。

`hggc_ppu_kern_gb_sum`表格列说明如下：

+ 注意“Time”列是根据“Total Time”列的总和计算得出的，表示该 kernel 占所有列出 kernels 执行时间的百分比，而不是根据应用执行时间得到的百分比。

```text
Row# : Row number of the kernel summary
Time [%] : Percentage of 'Total Time'
Total Time [ns] : Total time used by all executions of this kernel
Instances : Number of calls to this kernel
Avg [ns] : Average execution time of this kernel
Med [ns] : Median execution time of this kernel
Min [ns] : Smallest execution time of this kernel
Max [ns] : Largest execution time of this kernel
StdDev [ns] : Standard deviation of the time of this kernel
GridXYZ : Grid dimensions for kernel launch call
BlockXYZ : Block dimensions for kernel launch call
Name : Name of the kernel
```

**命令行使用方法**

```bash
asys stats -r hggc_ppu_kern_gb_sum report.asysrep
```

可通过`asys stats --help-report hggc_ppu_kern_gb_sum`查看具体帮助信息，支持的选项列举如下：

+ hgtx-name：kernel 名字前通过`/`拼接最接近 kernel launch 的 HGTX range 名称
+ base：使用 kernel 的短名称（仅函数名，不包含参数）进行统计和输出
+ mangled：使用 kernel 的 mangled 名称进行统计和输出
+ device：指定统计的 PPU device ID 列表，多个 PPU device ID 之间通过`/`分割。若不指定，默认统计所有 PPU device

报告结果示例如下：

```text
Row#,Time (%),Total Time (ns),Instances,Avg (ns),Med (ns),Min (ns),Max (ns),StdDev (ns),GridXYZ,BlockXYZ,Name,
1,6.7,16337781,65,251350,260801,115520,277681,39767,"960 1 64","256 1 1","[prof_range]: iter 9/_ZN5acdnn4cuda9transposeILNS0_8LoopModeE0ELi32ELi8ELb0ELb0EN7",
2,3.1,7415267,20,370763,370601,366482,374162,1936,"2048 1 1","512 1 1","[prof_range]: iter 8/_ZL35batch_norm_bwd_single_vector_accessILb0EN5acdnn16identity",
3,3.0,7348069,20,367403,366401,361281,375921,3885,"122880 1 1","128 1 1","_ZN2at6native29vectorized_elementwise_kernelILi4EZZZNS0_12",
```

**GUI 使用指南**

+ 规则设置（Settings）
    - Kernel Name Mode：Kernel Name 的展示模式。包括三种模式：
        * Base：导出 kernel 的短名称（仅函数名，不包含参数）
        * Mangled：导出 kernel 的 mangled 名称
        * Demangled：导出 kernel 的 demangle 之后的名称（默认值）
    - PPU Devices：PPU device 过滤器，统计结果按照所选的 PPU device 进行过滤，默认值为“All”，统计所有 PPU devices 的数据，此项不能为空。
    - Add HGTX name as a prefix：使能名字前拼接最接近 kernel launch 的 HGTX 名称，通过`/`间隔。默认不勾选。
+ 饼图统计：对所有 kernel 的执行耗时进行汇总。

##### 5.2.3.6. HGGC Kernel Grid Block 跟踪
导出 asysrep 报告中的 HGGC kernel 执行的跟踪数据，以及 grid size / block size 等信息，根据执行的开始时间升序输出。

**统计规则**

导出结果组织如下：`每Kernel执行信息`导出一行数据，根据本 kernel 的执行起始时间升序输出。

`hggc_ppu_kern_gb_trace`表格列说明如下：

```text
Row# : Row number of the kernel trace
Start [ns] : Timestamp of start time
Duration [ns] : Length of event
PID : Process identifier
Device ID : PPU device identifier
Context ID : Context identifier
Stream ID : Stream identifier
GridXYZ : Grid dimensions for kernel launch call
BlockXYZ : Block dimensions for kernel launch call
Name : Name of the kernel
```

**命令行使用方法**

依赖的 asys 采集选项：

+ `--trace hgtx,hggc`

```bash
asys stats -r hggc_ppu_kern_gb_trace report.asysrep
```

可通过`asys stats --help-report hggc_ppu_kern_gb_trace`查看具体帮助信息，支持的选项列举如下：

+ hgtx-name：kernel 名字前通过`/`拼接最接近 kernel launch 的 HGTX range 名称
+ base：使用 kernel 的短名称（仅函数名，不包含参数）进行统计和输出
+ mangled：使用 kernel 的 mangled 名称进行统计和输出

报告结果示例如下：

```text
Row#,Start (ns),Duration (ns),PID,Device ID,Context ID,Stream ID,GridXYZ,BlockXYZ,Name,
1,970508,6240,104699,0,1,1,"3 1 1","128 1 1","[prof_range]: iter 5/unrolled_elementwise_kernel",
2,1014188,44480,104699,0,1,1,"15360 1 1","128 1 1","[prof_range]: iter 5/unrolled_elementwise_kernel",
3,1158469,98480,104699,0,1,1,"960 1 64","256 1 1","[prof_range]: iter 5/transpose",
4,1257269,1880,104699,0,1,1,"1 1 32","256 1 1","[prof_range]: iter 5/transpose",
```

**GUI 使用指南**

+ 规则设置（Settings）
    - Kernel Name Mode：Kernel Name 的展示模式。包括三种模式：
        * Base：导出 kernel 的短名称（仅函数名，不包含参数）
        * Mangled：导出 kernel 的 mangled 名称
        * Demangled：导出 kernel 的 demangle 之后的名称（默认值）
    - Add HGTX name as a prefix：使能名字前拼接最接近 kernel launch 的 HGTX 名称，通过`/`间隔。默认不勾选。
+ 表格右键菜单功能
    - 支持在 Timeline View 中高亮或缩放至所选的 Device Activity
+ 饼图统计：对所有 kernel/进程/设备的 kernel 执行耗时进行汇总。

##### 5.2.3.7. HGGC PPU kernel 汇总
汇总 asysrep 报告中 HGGC kernel 的耗时，按照 HGGC kernel 总耗时降序输出。

依赖的 asys 采集选项：

+ `--trace hggc`

**统计规则**

按照`每HGGC kernel名称`进行统计，`HGGC kernel名称`取决于 base / mangled 选项是否设置，默认为 demangle 后 kernel 名称（包含函数参数列表），按照 HGGC kernel 总耗时降序输出。

`hggc_ppu_kern_sum`表格列说明如下：

+ 注意“Time”列是根据“Total Time”列的总和计算得出的，表示该 kernel 占所有列出 kernels 执行时间的百分比，而不是根据应用执行时间得到的百分比。

```text
Row# : Row number of the kernel summary
Time [%] : Percentage of 'Total Time'
Total Time [ns] : Total time used by all executions of this kernel
Instances : Number of calls to this kernel
Avg [ns] : Average execution time of this kernel
Med [ns] : Median execution time of this kernel
Min [ns] : Smallest execution time of this kernel
Max [ns] : Largest execution time of this kernel
StdDev [ns] : Standard deviation of the time of this kernel
Name : Name of the kernel
```

**命令行使用方法**

```bash
asys stats -r hggc_ppu_kern_sum report.asysrep
```

可通过`asys stats --help-report hggc_ppu_kern_sum`查看具体帮助信息，支持的选项列举如下：

+ rows=`<limit>`：限制输出结果的条数
+ hgtx-name：kernel 名字前通过/拼接最接近 kernel launch 的 HGTX range 名称
+ base：使用 kernel 的短名称（仅函数名，不包含参数）进行统计和输出
+ mangled：使用 kernel 的 mangled 名称进行统计和输出
+ device=`<device_list>`：指定统计的 PPU device ID 列表，多个 PPU device ID 之间通过`/`分割。若不指定，默认统计所有 PPU device

报告结果示例如下：

```text
Row#,Time (%),Total Time (ns),Instances,Avg (ns),Med (ns),Min (ns),Max (ns),StdDev (ns),Name,
1,81.6,826473830,28,29516922,17075623,16812011,357034784,64193935,"_Z39pcclKernel_AllReduce_RING_LL_Sum_int8_t12ncclWorkElem",
2,13.9,141273640,4,35318410,34326818,31248932,41371071,4288359,"_Z9deltaKernIaLi256EEvPvS0_mPd",
3,2.3,23263744,4,5815936,5866699,4743763,6786583,1087875,"_Z14InitDataKernelIaEvPT_mii",
4,2.2,22033972,4,5508493,5461251,4528464,6583005,1031905,"_Z20InitDataReduceKernelIaXadL_Z9ncclOpSumIaET_S1_S1_EEEvPS1_mmii",
```

**GUI 使用指南**

+ 通过选中行来统计求列和
    - 统计结果表格中的“Time”和“Total Time”列支持对选中行数据自动求和，统计结果显示在表头的第二行中。当没有行被选中时，对该列的所有行进行统计求和。
+ 规则设置（Settings）
    - Kernel Name Mode：Kernel Name 的展示模式。包括三种模式：
        * Base：导出 kernel 的短名称（仅函数名，不包含参数）
        * Mangled：导出 kernel 的 mangled 名称
        * Demangled：导出 kernel 的 demangle 之后的名称（默认值）
    - PPU Devices：PPU device 过滤器，统计结果按照所选的 PPU device 进行过滤，默认值为“All”，统计所有 PPU devices 的数据，此项不能为空。
+ 饼图统计：对所有 kernel 的 kernel 执行耗时进行汇总。

##### 5.2.3.8. HGGC PPU 跟踪
导出 asysrep 报告中的 PPU 执行 HGGC Kernel / Memcpy / Memset 的跟踪数据，根据执行的开始时间升序输出。

**统计规则**

导出结果组织如下：`每Kernel / Memcpy / Memset执行信息`导出一行数据，根据执行的开始时间升序输出。

由于导出结果的列包含 Kernel / Memcpy / Memset 的信息，对于导出的每一行数据，不适用的单元格被标记为无效值`-`。

`hggc_ppu_trace`表格列说明如下：

```text
Row# : Row number of the PPU trace
Start [ns] : Timestamp of start time
Duration [ns] : Length of event
CorrId : Correlation ID
GrdX : Grid X values
GrdY : Grid Y values
GrdZ : Grid Z values
BlkX : Block X values
BlkY : Block Y values
BlkZ : Block Z values
Reg/Trd : Registers per thread
StcSMem [bytes] : Size of Static Shared Memory
DymSMem [bytes] : Size of Dynamic Shared Memory
Bytes [bytes] : Size of memory operation
Throughput [B/s] : Memory throughput
SrcMemKd : Memcpy source memory kind or memset memory kind
DstMemKd : Memcpy destination memory kind
Device : PPU device name and ID
Ctx : Context ID
Strm : Stream ID
Name : Trace event name
```

**命令行使用方法**

依赖的 asys 采集选项：

+ `--trace hggc`

```bash
asys stats -r hggc_ppu_trace report.asysrep
```

可通过`asys stats --help-report hggc_ppu_trace`查看具体帮助信息，支持的选项列举如下：

+ hgtx-name：kernel 名字前通过/拼接最接近 kernel launch 的 HGTX range 名称
+ base：导出 kernel 的短名称（仅函数名，不包含参数）
+ mangled：导出 kernel 的 mangled 名称

默认导出 HGGC Kernel 的名称为 demangle 之后的名称。

报告结果示例如下，不适用的单元格被标记为无效值`-`：

```bash
Row#,Start (ns),Duration (ns),CorrId,GrdX,GrdY,GrdZ,BlkX,BlkY,BlkZ,Reg/Trd,StcSMem (bytes),DymSMem (bytes),Bytes (bytes),Throughput (B/s),SrcMemKd,DstMemKd,Device,Ctx,Strm,Name,
1,193282492,3009,5,"-","-","-","-","-","-","-","-","-",256,85078016,"Device","-","",1,1,"Memset",
2,193329286,1332,6,"-","-","-","-","-","-","-","-","-",256,192192000,"Pageable","Device","",1,1,"Memcpy HtoD (device)",
3,193380562,3415,7,"-","-","-","-","-","-","-","-","-",256,74963200,"Pageable","Device","",1,1,"Memcpy HtoD (device)",
4,231829389,4562345,8,64,1,1,1,1,1,32,0,0,"-","-","-","-","",1,1,"add(int*, int*, int*)",
```

**GUI 使用指南**

+ 规则设置（Settings）
    - Kernel Name Mode：Kernel Name 的展示模式。包括三种模式：
        * Base：导出 kernel 的短名称（仅函数名，不包含参数）
        * Mangled：导出 kernel 的 mangled 名称
        * Demangled：导出 kernel 的 demangle 之后的名称（默认值）
+ 表格右键菜单功能
    - 支持在 Timeline View 中高亮或缩放至所选 kernel 或内存操作
+ 饼图统计：对所有 PPU 事件/设备的执行耗时进行汇总。

##### 5.2.3.9. HGTX 关联 kernel 汇总
统计 asysrep 报告中 HGTX range 和关联的 HGGC Kernel 跟踪数据，输出`每HGTX range名称，每Kernel名称`的统计信息。

依赖的 asys 采集选项：

+ `--trace hgtx,hggc`

**统计规则**

判断 HGTX range 和 HGGC kernel 的原则为：HGTX range 持续时间范围内，相同线程的 HGGC API 触发的 HGGC kernel，认为和此 HGTX range 关联。

统计方式：

+ 对每进程、每线程，将相同`HGTX range名称`且相同`Kernel名称`的 Kernel 执行信息进行汇总：Kernel 执行时间、同名 HGTX 出现次数、同名 Kernel 出现次数等

统计结果组织如下：`每线程，每HGTX range名称，每HGGC kernel名称`导出一行数据，若选项`standalone`使能，未关联 HGTX range 的 HGGC kernel 所在行的 HGTX 相关信息将标记为无效符号`-`。统计结果排序方式如下：

+ 按照 HGTX range 名称、进程 ID 和线程 ID 升序排列
+ 相同线程相同 HGTX range 名称的 Kernel 按照 Total Time 列降序排列

`hgtx_kern_sum`表格列说明如下：

```text
Row# : Row number of the HGTX range kernel summary
HGTX Range : Name of the range
Style : Range style; Start/End or Push/Pop
PID : Process ID for this set of ranges and kernels
TID : Thread ID for this set of ranges and kernels
HGTX Inst : Number of HGTX range instances
Kern Inst : Number of HGGC kernel instances
Total Time [ns] : Total time used by all kernel instances of this range
Avg [ns] : Average execution time of this kernel
Med [ns] : Median execution time of this kernel
Min [ns] : Smallest execution time of this kernel
Max [ns] : Largest execution time of this kernel
StdDev [ns] : Standard deviation of the time of this kernel
Kernel Name : Name of the kernel
```

**命令行使用方法**

```bash
asys stats -r hgtx_kern_sum report.asysrep
```

可通过`asys stats --help-report hgtx_kern_sum`查看具体帮助信息，支持的选项列举如下：

+ base：导出 kernel 的短名称（仅函数名，不包含参数）
+ mangled：导出 kernel 的 mangled 名称
+ standalone：导出结果包含未关联任何 HGTX range 的 HGGC kernel
+ device：指定统计的 PPU device ID 列表，多个 PPU device ID 之间通过`/`分割。若不指定，默认统计所有 PPU device
+ no-graph-mapping：导出结果不包含通过 HGGC graph node 映射的 HGTX range 信息
+ range-include=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式白名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ range-exclude=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式黑名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range

报告结果示例如下：

```text
Row#,HGTX Range,Style,PID,TID,HGTX Inst,Kern Inst,Total Time (ns),Avg (ns),Med (ns),Min (ns),Max (ns),StdDev (ns),Kernel Name,
1,"DoProcess","PushPop",3588556,3588556,2,2,8036961,4018480,4018480,3474616,4562345,543864,"add(int*, int*, int*)",
2,"Loop1","PushPop",3588556,3588556,1,1,4562345,4562345,4562345,4562345,4562345,0,"add(int*, int*, int*)",
3,"Loop2","PushPop",3588556,3588556,1,1,3474616,3474616,3474616,3474616,3474616,0,"add(int*, int*, int*)",
4,"profile","PushPop",3588556,3588556,1,2,8036961,4018480,4018480,3474616,4562345,543864,"add(int*, int*, int*)",
```

**GUI 使用指南**

+ 规则设置（Settings）
    - Kernel Name Mode：Kernel Name 的展示模式。包括三种模式：
        * Base：导出 kernel 的短名称（仅函数名，不包含参数）
        * Mangled：导出 kernel 的 mangled 名称
        * Demangled：导出 kernel 的 demangle 之后的名称（默认值）
    - Include Standalone Kernel：是否导出未匹配到任何 HGTX 的 kernel 信息，此类 kernel 导出的 HGTX 相关信息为非法值。默认不导出。
    - HGTX graph node mapping：是否投影 HGGC graph capture 阶段 HGTX 到 PPU 侧（通过在 HGTX range 范围内创建的 HGGC graph node 建立与 PPU 侧的关联）。默认值为“Yes”。
    - PPU Devices：PPU device 过滤器，统计结果按照所选的 PPU device 进行过滤，默认值为“All”，统计所有 PPU devices 的数据，此项不能为空。
+ 饼图统计：对所有 HGTX Range/进程/kernel name 的 kernel 执行耗时进行汇总。

##### 5.2.3.10. HGTX 关联 kernel 跟踪
建立关联 HGTX 和 HGGC kernel 的关联关系，并按照`每HGTX range，每HGGC kernel`级别导出关联关系。

**统计规则**

判断 HGTX range 和 HGGC kernel 的原则为：HGTX range 持续时间范围内，相同线程的 HGGC API 触发的 HGGC kernel，认为和此 HGTX range 关联。

导出结果组织如下：`每HGTX range，每HGGC kernel`导出一行数据，若选项`standalone`使能，未关联 HGTX range 的 HGGC kernel 行中的 HGTX range 信息将标记为无效符号`-`。

导出顺序：

+ HGGC kernel 按照 PPU 开始执行时间升序排序
+ 相同 HGGC kernel 关联的各个 HGTX range 行按照 HGTX range 的开始时间升序排序

`hgtx_kern_trace`表格列说明如下：

+ `API Start`和`API duration`列对于 HGTX 通过 HGGC graph node 关联 kernel 的场景输出为无效值

```text
Row# : Row number of the HGTX range kernel trace
Range name : Name of the HGTX range
Style : Range style; Start/End or Push/Pop
PID : Process identifier
TID : Thread identifier
Device ID : PPU device identifier
Context ID : Context identifier
Stream ID : Stream identifier
HGTX range ID : HGTX range identifier
Kernel exec ID : Kernel execution identifier
Kernel Start [ns] : Start timestamp of HGGC kernel
Kernel duration [ns] : Duration of HGGC kernel
API Start [ns] : Start timestamp of API call
API duration [ns] : Duration of API call
GridXYZ : Grid dimensions for kernel launch call
BlockXYZ : Block dimensions for kernel launch call
Correlation ID : Correlation identifier
Graph ID : HGGC graph identifier
Graph Node ID : HGGC graph node identifier
Kernel Name : Name of the kernel
Mangled Name : Mangled name of the kernel
```

**命令行使用方法**

依赖的 asys 采集选项：

+ `--trace hgtx,hggc`

```bash
asys stats -r hgtx_kern_trace report.asysrep
```

可通过`asys stats --help-report hgtx_kern_trace`查看具体帮助信息，支持的选项列举如下：

+ base：导出 kernel 的短名称（仅函数名，不包含参数）
+ mangled：导出 kernel 的 mangled 名称
+ standalone：导出结果包含未关联任何 HGTX range 的 HGGC kernel
+ no-graph-mapping：导出结果不包含通过 HGGC graph node 映射的 HGTX range 信息
+ range-include=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式白名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ range-exclude=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式黑名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range

报告结果示例如下：

```bash
Row#,Range Name,Style,PID,TID,Device ID,Context ID,Stream ID,HGTX Range ID,Kernel Exec ID,Kernel Start (ns),Kernel Duration (ns),API Start (ns),API Duration (ns),GridXYZ,BlockXYZ,Correlation ID,Graph ID,Graph Node ID,Kernel Name,Mangled Name,
1,"profile","PushPop",4010376,4010376,0,1,1,6,23,85579190,11136752,80913269,4025776,"64 1 1","1 1 1",8,"-","-","add(int*, int*, int*)","_Z3addPiS_S_",
2,"Loop1","PushPop",4010376,4010376,0,1,1,7,23,85579190,11136752,80913269,4025776,"64 1 1","1 1 1",8,"-","-","add(int*, int*, int*)","_Z3addPiS_S_",
3,"DoProcess","PushPop",4010376,4010376,0,1,1,8,23,85579190,11136752,80913269,4025776,"64 1 1","1 1 1",8,"-","-","add(int*, int*, int*)","_Z3addPiS_S_",
...
```

**GUI 使用指南**

+ 规则设置（Settings）
    - Kernel Name Mode：Kernel Name 的展示模式。包括三种模式：
        * Base：导出 kernel 的短名称（仅函数名，不包含参数）
        * Mangled：导出 kernel 的 mangled 名称
        * Demangled：导出 kernel 的 demangle 之后的名称（默认值）
    - HGTX graph node mapping：是否投影 HGGC graph capture 阶段 HGTX 到 PPU 侧（通过在 HGTX range 范围内创建的 HGGC graph node 建立与 PPU 侧的关联）。默认值为“Yes”。
    - Include Standalone Kernel：是否导出未匹配到任何 HGTX 的 kernel 信息，此类 kernel 导出的 HGTX 相关信息为非法值。默认不导出。
+ 表格右键菜单功能
    - 支持在 Timeline View 中高亮或缩放至所选的 HGTX Range
    - 支持在 Timeline View 中高亮或缩放至所选的 Device Activity
+ 饼图统计：对所有 HGTX Range/kernel name/进程/设备的 kernel 执行耗时进行汇总。

##### 5.2.3.11. HGTX 向 PPU 投影汇总
将 asysrep 报告中的 CPU 侧 HGTX range 向 PPU 侧投影，输出 HGTX range 在 PPU 侧实际活跃时间的统计信息。

依赖的 asys 采集选项：

+ `--trace hgtx,hggc`

**统计规则**

判断 HGTX range 和 HGGC kernel 的原则为：HGTX range 持续时间范围内，相同线程的 HGGC API 触发的 HGGC kernel，认为和此 HGTX range 关联。

CPU 侧 HGTX range 向 PPU 侧投影的方式为：HGTX range 在 PPU 侧的活跃时间，从本 HGTX 关联的最早的 PPU 活动开始，到最晚的 PPU 活动结束。PPU 活动包括：HGGC Kernel / memcpy / memset 相关执行信息。

统计方式：

+ 将`相同HGTX range`且`相同Style`的 HGTX range 信息进行汇总，如 CPU 侧时长，PPU 侧投影时长等
+ 相同的 HGTX range 在 PPU 侧的总的活跃时间`Proj Active Time`计算方式为：指定的时间点存在一个或者更多 HGTX range 投影，则记为活跃时间。如果多个 HGTX range 的投影在时间上重叠，重叠的部分不会被多次计入活跃时间。
+ 相同的 HGTX range 投影的 PPU 侧占比`In-Use`计算方式为：`Proj Active Time`/ `PPU侧统计时间范围`，其中`PPU侧统计时间范围`计算方式取决于`range-mode`选项。

统计结果组织如下：按照`In-Use`降序排列，按照 HGTX Range 名称升序排列。

`hgtx_ppu_proj_sum`表格列说明如下：

```text
Row# : Row number of the HGTX PPU projection summary
Range : Name of the HGTX range
Style : Range style; Start/End or Push/Pop
In-Use [%] : Percentage of projected active time to time range
Proj Active Time [ns] : Total projected time excluding overlapping for this range name
Total Proj Time [ns] : Total projected time used by all instances of this range name
Total Range Time [ns] : Total original HGTX range time used by all instances of this range name
Range Instances : Number of instances of this range
Proj Avg [ns] : Average projected time for this range
Proj Med [ns] : Median projected time for this range
Proj Min [ns] : Minimum projected time for this range
Proj Max [ns] : Maximum projected time for this range
Proj StdDev [ns] : Standard deviation of projected times for this range
Total PPU Ops : Total number of PPU operations
Avg PPU Ops : Average number of PPU operations
Avg Range Lvl : Average range stack depth
Avg Num Child : Average number of children ranges
```

**命令行使用方法**

```bash
asys stats -r hgtx_ppu_proj_sum report.asysrep
```

可通过`asys stats --help-report hgtx_ppu_proj_sum`查看具体帮助信息，支持的选项列举如下：

+ `device=<device_list>`：指定统计的 PPU device ID 列表，多个 PPU device ID 之间通过`/`分割。若不指定，默认统计所有 PPU device
+ `range-mode=<mode>`：PPU 侧统计时间范围的选择模式，支持 active 和 full 模式
    - active：默认模式，时间范围从第一个 PPU 活动开始，到最后一个 PPU 活动结束截止
    - full：时间范围选取为用户指定的统计时间范围，若没有指定统计时间范围，则统计报告整体的时间范围
+ `range-include=<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式白名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ `range-exclude=<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式黑名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ `no-graph-mapping`：导出结果不包含通过 HGGC graph node 映射的 HGTX range 信息

**GUI 使用指南**

+ 规则设置（Settings）
    - PPU Devices：PPU device 过滤器，统计结果按照所选的 PPU device 进行过滤，默认值为“All”，统计所有 PPU devices 的数据，此项不能为空。
    - Time Range Mode：设置统计时间范围的模式
        * `PPU Active Time Range`：默认模式，时间范围从第一个 PPU 活动开始，到最后一个 PPU 活动结束截止
        * `Filtered Time Range`：时间范围选取为用户指定的统计时间范围，若没有指定统计时间范围，则统计报告整体的时间范围
    - HGTX graph node mapping：是否投影 HGGC graph capture 阶段 HGTX 到 PPU 侧（通过在 HGTX range 范围内创建的 HGGC graph node 建立与 PPU 侧的关联）。默认值为“Yes”。
    - Range Name Filter：对结果中的 HGTX range name 进行过滤，采用（Perl 兼容的）正则表达式匹配的方式，默认显示所有 HGTX range。带有正则表达式语法检查，当输入的正则表达式语法错误时，出现错误提示并且不允许保存设置
+ 饼图统计：对 CPU 侧所有 HGTX Range 的在 PPU 侧的投影活动时间进行汇总。可以直观地查看各 HGTX Range 投影至 PPU 侧后的运行耗时占比。

##### 5.2.3.12. HGTX 向 PPU 投影跟踪
将 asysrep 报告中的 CPU 侧 HGTX range 向 PPU 侧投影，以展示 CPU 侧 HGTX range 在 PPU 侧实际活跃的时间，并导出 HGTX 的堆栈信息。

依赖的 asys 采集选项：

+ `--trace hgtx,hggc`

**统计规则**

判断 HGTX range 和 HGGC kernel 的原则为：HGTX range 持续时间范围内，相同线程的 HGGC API 触发的 HGGC kernel，认为和此 HGTX range 关联。

CPU 侧 HGTX range 向 PPU 侧投影的方式为：HGTX range 在 PPU 侧的活跃时间，从本 HGTX 关联的最早的 PPU 活动开始，到最晚的 PPU 活动结束。PPU 活动包括：HGGC Kernel / memcpy / memset 相关执行信息。

HGTX range 在 PPU 侧的活跃时间`PPU Active Time`计算方式为：指定的时间点存在一个或者多个 PPU 侧活动，则记为活跃时间。若多个 PPU 侧活动在时间上重叠，重叠的部分不会被多次计入活跃时间。

导出结果组织如下：`每HGTX range`导出一行数据，结果按照 Projected Start 升序输出。

`hgtx_ppu_proj_trace`表格列说明如下：

```text
Row# : Row number of the HGTX PPU projection trace
Name : Name of the HGTX range
Projected Start [ns] : Projected range start timestamp
Projected Duration [ns] : Projected range duration
PPU Active Time [ns] : Total PPU active time excluding overlapping for this range
Orig Start [ns] : Original HGTX range start timestamp
Orig Duration [ns] : Original HGTX range duration
Style : Range style; Start/End or Push/Pop
PID : Process identifier
TID : Thread identifier
NumPPUOps : Number of enclosed PPU operations
Lvl : Stack level, starts at 0
NumChild : Number of children ranges
RangeId : Arbitrary ID for range
ParentId : Range ID of the enclosing range
RangeStack : Range IDs that make up the push/pop stack
```

**命令行使用方法**

```bash
asys stats -r hgtx_ppu_proj_trace report.asysrep
```

可通过`asys stats --help-report hgtx_ppu_proj_trace`查看具体帮助信息，支持的选项列举如下：

+ `device=<device_list>`：指定统计的 PPU device ID 列表，多个 PPU device ID 之间通过`/`分割。若不指定，默认统计所有 PPU device
+ `range-include=<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式白名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ `range-exclude=<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式黑名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ `no-graph-mapping`：导出结果不包含通过 HGGC graph node 映射的 HGTX range 信息

报告结果示例如下：

```text
Row#,Name,Projected Start (ns),Projected Duration (ns),PPU Active Time (ns),Orig Start (ns),Orig Duration (ns),Style,PID,TID,NumPPUOps,Lvl,NumChild,RangeId,ParentId,RangeStack,
1,"profile",777876074,53206947,21448563,776113485,56055065,"PushPop",295684,295684,50,0,10,6,"-",":6",
2,"Loop1",777876074,14961664,10470590,776142784,28572367,"PushPop",295684,295684,5,1,1,7,6,":6:7",
3,"DoProcess",777876074,14961664,10470590,776146124,27485685,"PushPop",295684,295684,5,2,0,8,7,":6:7:8",
...
```

**GUI 使用指南**

+ 规则设置（Settings）
    - PPU Devices：PPU device 过滤器，统计结果按照所选的 PPU device 进行过滤，默认值为“All”，统计所有 PPU devices 的数据，此项不能为空。
    - HGTX graph node mapping：是否投影 HGGC graph capture 阶段 HGTX 到 PPU 侧（通过在 HGTX range 范围内创建的 HGGC graph node 建立与 PPU 侧的关联）。默认值为“Yes”。
    - Range Name Filter：对结果中的 HGTX range name 进行过滤，采用（Perl 兼容的）正则表达式匹配的方式，默认显示所有 HGTX range。带有正则表达式语法检查，当输入的正则表达式语法错误时，出现错误提示并且不允许保存设置
+ 表格右键菜单功能
    - 支持在 Timeline View 中高亮或缩放至所选的 HGTX Range
    - 支持在 Timeline View 中高亮或缩放至所选的 Device Activity
+ 饼图统计：对 CPU 侧所有 HGTX Range 以 range name 或进程进行分类，在 PPU 侧的投影活动时间进行汇总。可以直观地查看各 HGTX Range 或进程投影至 PPU 侧后的运行耗时占比。

##### 5.2.3.13. HGTX range 汇总
汇总 asysrep 报告中 HGTX range 的耗时，按照 range 总耗时降序输出。

依赖的 asys 采集选项：

+ `--trace hgtx`

**统计规则**

按照`每HGTX range domain和名称`级别进行统计，累加相同 domain 和名称的 HGTX range 的耗时时间，若 HGTX range 包含 domain，输出的 HGTX range 名称格式为`domain:range`，按照 range 总耗时降序输出。

若通过`process`/`thread`选项指定统计范围，线程匹配`thread`过滤条件或者所属进程匹配`process`过滤条件，均参与统计。

`hgtx_sum`表格列说明如下：

+ 注意“Time”列是根据“Total Time”列的总和计算得出的，表示该 range 占所有列出 ranges 执行时间的百分比，而不是根据应用执行时间得到的百分比。

```text
Row# : Row number of the HGTX range summary
Time [%] : Percentage of 'Total Time'
Total Time [ns] : Total time used by all instances of this range
Instances : Number of instances of this range
Avg [ns] : Average execution time of this range
Med [ns] : Median execution time of this range
Min [ns] : Smallest execution time of this range
Max [ns] : Largest execution time of this range
StdDev [ns] : Standard deviation of the time of this range
Style : Range style; Start/End or Push/Pop
Range : Name of the range
```

**命令行使用方法**

```bash
asys stats -r hgtx_sum report.asysrep
```

可通过`asys stats --help-report hgtx_sum`查看具体帮助信息。支持的选项列举如下：

+ `rows=<limit>`：限制输出的 HGTX range 的条数
+ `process=<pid_list>`：指定统计的进程的 PID 列表，多个 PID 之间通过`/`分割。若不指定，默认统计所有进程
+ `thread=<tid_list>`：指定统计的线程的 TID 列表，多个 TID 之间通过`/`分割。若不指定，默认统计所有线程

报告结果示例如下：

```text
Row#,Time (%),Total Time (ns),Instances,Avg (ns),Med (ns),Min (ns),Max (ns),StdDev (ns),Style,Range,
1,25.7,181837947,1,181837947,181837947,181837947,181837947,0,"PushPop","[prof_range]: iter 6",
2,25.1,177622641,1,177622641,177622641,177622641,177622641,0,"PushPop","[prof_range]: iter 9",
3,25.1,177254919,1,177254919,177254919,177254919,177254919,0,"PushPop","[prof_range]: iter 7",
4,24.1,170843422,1,170843422,170843422,170843422,170843422,0,"PushPop","[prof_range]: iter 8",
...
```

**GUI 使用指南**

+ 规则设置（Settings）
    - Processes：指定统计的进程。默认为“All”，统计所有进程
    - Maximum number of results：展示结果的最大行数。默认为-1，表示无上限
+ 饼图统计：对所有 HGTX Range 的总耗时进行汇总。可以直观地查看各 HGTX Range 的耗时占比。

##### 5.2.3.14. OSRT API 汇总
分析和汇总 asysrep 报告中操作系统 API（OS runtime API）的耗时，按照 API 总耗时降序输出。

依赖的 asys 采集选项：

+ `--trace osrt`

**统计规则**

按照`每OSRT API名称`级别进行统计，累加相同名称 API 的耗时时间，按照 API 总耗时降序输出。

`osrt_sum`表格列说明如下：

+ 注意“Time”列是根据“Total Time”列的总和计算得出的，表示该函数占所有列出函数执行时间的百分比，而不是根据应用执行时间得到的百分比。

```text
Row# : Row number of the OS runtime summary
Time [%] : Percentage of 'Total Time'
Total Time [ns] : Total time used by all executions of this function
Num Calls : Number of calls to this function
Avg [ns] : Average execution time of this function
Med [ns] : Median execution time of this function
Min [ns] : Smallest execution time of this function
Max [ns] : Largest execution time of this function
StdDev [ns] : Standard deviation of the time of this function
Name : Name of the function
```

**命令行使用方法**

```bash
asys stats -r osrt_sum report.asysrep
```

可通过`asys stats --help-report osrt_sum`查看具体帮助信息。支持的选项列举如下：

+ `rows=<limit>`：限制输出结果的条数

报告结果示例如下：

```text
Row#,Time (%),Total Time (ns),Num Calls,Avg (ns),Med (ns),Min (ns),Max (ns),StdDev (ns),Name,
1,85.6,8901500720,255,34907845,4994783,1095,348667026,63811239,"pthread_cond_wait",
2,6.9,721563692,1105,652998,1055069,52083,1072141,485233,"nanosleep",
3,6.7,700892565,7,100127509,100123388,100121020,100143853,8411,"poll",
...
```

**GUI 使用指南**

+ 规则设置（Settings）
    - 该规则没有可以配置的设置选项
+ 饼图统计：对所有 OSRT API 的总耗时进行汇总。可以直观地查看各 OSRT API 的耗时占比。

##### 5.2.3.15. PCCL 传输各阶段汇总
分析和汇总 asysrep 报告中 PCCL 传输各阶段耗时，按照阶段总耗时降序输出。

依赖的 asys 采集选项：

+ `--trace pccl`

**统计规则**

按照`每线程、每channel、每方向、每传输阶段`，统计传输阶段的耗时（平均值、最大值、最小值等）、出现次数等指标，按照传输阶段总耗时降序输出。

`pccl_stage_sum`表格列说明如下：

```text
Row# : Row number of the stage summary
PID : Process identifier
Device ID : PPU device identifier
TID : Thread identifier
Channel ID : PCCL channel identifier
Channel Type : PCCL channel type
Name : Stage name
Total Time [ns] : Stage total time
Instances : Number of this stage
Avg [ns] : Average of stage duration
Med [ns] : Median of stage duration
Min [ns] : Minimum of stage duration
Max [ns] : Maximum of stage duration
Stdev [ns] : Standard deviation of stage duration
```

**命令行使用方法**

```bash
asys stats --report pccl_stage_sum report.asysrep
```

可通过`asys stats --help-report pccl_stage_sum`查看具体帮助信息。

报告结果示例如下：

```text
Row#,PID,Device ID,TID,Channel ID,Channel Type,Name,Total Time,Instances,Avg,Med,Min,Max,Stdev,
1,631660,0,631712,1,RX,RecvWait,305528068,24,12730336,13761981,9669723,18509164,2407844,
2,631660,1,631711,1,TX,GPUWait,299988851,24,12499535,12786840,9625474,16580086,2217489,
3,631660,0,631712,1,TX,GPUWait,297674072,24,12403086,12579239,9570100,17151019,2208876,
...
```

**GUI 使用指南**

+ 规则设置（Settings）
    - 该规则没有可以配置的设置选项
+ 饼图统计：对所有 PCCL stage/进程/设备的 PCCL stage 总耗时进行汇总。可以直观地查看在不同统计维度下 PCCL stage 总的耗时占比。

##### 5.2.3.16. HGGC PPU memory 数据量汇总
汇总 asysrep 报告中 HGGC PPU memory 操作（memcpy / memset）的数据量，按照 memory 操作数据量总和降序输出。

依赖的 asys 采集选项：

+ `--trace hggc`

**统计规则**

按照`每memory操作类型`，统计本类型操作数据量，按照操作数据量总和降序输出。

+ memcpy 根据拷贝的类型进行区分，如`[HGGC memcpy Host-to-Device]` / `[HGGC memcpy Device-to-Host]`

`hggc_ppu_mem_size_sum`表格列说明如下：

```text
Row# : Row number of the memory summary
Total [bytes] : Total memory utilized by this operation
Count : Number of executions of this operation
Avg [bytes] : Average memory size of this operation
Med [bytes] : Median memory size of this operation
Min [bytes] : Smallest memory size of this operation
Max [bytes] : Largest memory size of this operation
StdDev [bytes] : Standard deviation of the memory size of this operation
Operation : Name of the memory operation
```

**命令行使用方法**

```bash
asys stats --report hggc_ppu_mem_size_sum report.asysrep
```

可通过`asys stats --help-report hggc_ppu_mem_size_sum`查看具体帮助信息。

报告结果示例如下：

```text
Row#,Total (bytes),Count,Avg (bytes),Med (bytes),Min (bytes),Max (bytes),StdDev (bytes),Operation,
1,9896352144,564,17546723,1024,12,556254464,74087070,"[HGGC memset]",
2,536876208,342,1569813,16,4,67108864,10157989,"[HGGC memcpy Host-to-Device]",
3,156,44,3,1,1,16,4,"[HGGC memcpy Device-to-Host]",
4,64,12,5,4,4,8,1,"[HGGC memcpy Device-to-Device]",
```

**GUI 使用指南**

+ 规则设置（Settings）
    - 该规则没有可以配置的设置选项
+ 饼图统计：对所有 Memory operation 的 memory 操作数据量进行汇总。可以直观地查看各个 Memory operation 的 memory 操作数据量的对比情况。

##### 5.2.3.17. HGGC PPU memory 耗时汇总
汇总 asysrep 报告中 HGGC PPU memory 操作（memcpy / memset）的耗时，按照 memory 操作耗时总时长降序输出。

依赖的 asys 采集选项：

+ `--trace hggc`

**统计规则**

按照`每memory操作类型`，统计本类型操作耗时，按照操作耗时总时长降序输出。

+ memcpy 根据拷贝的类型进行区分，如`[HGGC memcpy Host-to-Device]` / `[HGGC memcpy Device-to-Host]`

`hggc_ppu_mem_time_sum`表格列说明如下：

+ 注意“Time”列是根据“Total Time”列的总和计算得出的，表示该 memory 操作类型占所有列出的 memory 操作耗时总时长的百分比，而不是根据应用执行时间得到的百分比。

```text
Row# : Row number of the memory summary
Time [%] : Percentage of 'Total Time'
Total Time [ns] : Total time used by all executions of this operation
Count : Number of operations to this type
Avg [ns] : Average execution time of this operation
Med [ns] : Median execution time of this operation
Min [ns] : Smallest execution time of this operation
Max [ns] : Largest execution time of this operation
StdDev [ns] : Standard deviation of the time of this operation
Operation : Name of the memory operation
```

**命令行使用方法**

```bash
asys stats --report hggc_ppu_mem_time_sum report.asysrep
```

可通过`asys stats --help-report hggc_ppu_mem_time_sum`查看具体帮助信息。

报告结果示例如下：

```text
Row#,Time (%),Total Time (ns),Count,Avg (ns),Med (ns),Min (ns),Max (ns),StdDev (ns),Operation,
1,69.3,19697314,342,57594,1240,1080,2413129,364424,"[HGGC memcpy Host-to-Device]",
2,30.6,8687991,564,15404,720,120,496801,67433,"[HGGC memset]",
3,0.1,20920,44,475,400,320,960,165,"[HGGC memcpy Device-to-Host]",
4,0.1,15600,12,1300,1240,920,1800,293,"[HGGC memcpy Device-to-Device]",
```

**GUI 使用指南**

+ 规则设置（Settings）
    - 该规则没有可以配置的设置选项
+ 饼图统计：对所有 Memory operation 的耗时进行汇总。可以直观地查看各个 Memory operation 的耗时占比。

##### 5.2.3.18. PCCL 不同步跟踪
将 asysrep 报告中的 PCCL kernel 根据通信进行分组，计算每组通信的 PCCL kernel 之间执行时间不同步的占比，并导出最晚开始执行的 PCCL kernel 的信息。

依赖的 asys 采集选项：

+ `--trace hggc`

**统计规则**

将执行时间上存在重叠的 PCCL kernel 分入一个通信组，对每个通信组的所有 kernel 计算如下时间：

+ `重叠时间`：本通信组内所有 PCCL kernel 重叠的时间
+ `持续时间`：从本通信组第一个 kernel 开始执行到最后一个 kernel 停止执行的时间

不同步比例计算方式为：(`持续时间` - `重叠时间`) / `持续时间`。每通信组输出一行跟踪数据，结果按照不同步占比降序输出。

`pccl_desync_trace`表格列说明如下：

```text
Row# : Row number of PCCL communication trace
Start [ns] : Start time of PCCL communication
Duration [ns] : Elapsed duration of PCCL communication
Overlap [ns] : Overlapping duration of all PCCL kernel
Desync Rate [%] : Desynchronization rate of PCCL communication
Last Process : Last kernel process ID in this PCCL communication
Last Device : Last kernel device ID in this PCCL communication
Last Kernel : Last kernel ID in this PCCL communication
Max Duration [ns] : Longest kernel duration in this PCCL communication
Min Duration [ns] : Shortest kernel duration in this PCCL communication
Avg Duration [ns] : Average kernel duration in this PCCL communication
Instances : Number of kernel in this PCCL communication
Kernel Name : Name of the PCCL kernel
```

**命令行使用方法**

```bash
asys stats -r pccl_desync_trace report.asysrep
```

可通过`asys stats --help-report pccl_desync_trace`查看具体帮助信息，支持的选项列举如下：

+ hgtx-name：kernel 名字前通过`/`拼接最接近 kernel launch 的 HGTX range 名称
+ base：使用 kernel 的短名称（仅函数名，不包含参数）进行统计和输出
+ mangled：使用 kernel 的 mangled 名称进行统计和输出
+ device：指定统计的 PPU device ID 列表，多个 PPU device ID 之间通过`/`分割。若不指定，默认统计所有 PPU device

报告结果示例如下：

```text
Row#,Start (ns),Duration (ns),Overlap (ns),Desync Rate (%),Last Process,Last Device,Last Kernel,Max Duration (ns),Min Duration (ns),Avg Duration (ns),Instances,Kernel Name,
1,113393971366,699213,15256,97.8,1142413,0,38654,697883,15400,538712,8,"pcclKernel_AllReduce_RING_LL_Sum_uint8_t(ncclWorkElem)",
2,113395036610,267497,12450,95.3,1142419,6,38798,266721,14040,191886,8,"pcclKernel_AllReduce_RING_LL_Sum_uint8_t(ncclWorkElem)",
...
```

**GUI 使用指南**

+ 规则设置（Settings）
    - Kernel Name Mode：Kernel Name 的展示模式。包括三种模式：
        * Base：导出 kernel 的短名称（仅函数名，不包含参数）
        * Mangled：导出 kernel 的 mangled 名称
        * Demangled：导出 kernel 的 demangle 之后的名称（默认值）
    - PPU Devices：PPU device 过滤器，统计结果按照所选的 PPU device 进行过滤，默认值为“All”，统计所有 PPU devices 的数据，此项不能为空。
    - Add HGTX name as a prefix：使能名字前拼接最接近 kernel launch 的 HGTX 名称，通过`/`间隔。默认不勾选。
+ 表格右键菜单功能
    - 支持在 Timeline View 中高亮或缩放至所选追踪的最后一个不同步的 PCCL Kernel。
+ 饼图统计：对 PCCL 不同步情况出现时，最慢的进程/设备进行汇总。可以直观地查看哪个进程/设备上最容易出现 PCCL 执行时间最晚导致 PCCL 不同步情况出现。

##### 5.2.3.19. PCCL 不同步汇总
将 asysrep 报告中的 PCCL kernel 根据通信进行分组，计算每组通信的 PCCL kernel 之间执行时间不同步的占比，输出同名 PCCL kernel 通信组的不同步占比的统计结果。

依赖的 asys 采集选项：

+ `--trace hggc`

**统计规则**

将执行时间上存在重叠的 PCCL kernel 分入一个通信组，对每个通信组的所有 kernel 计算如下时间：

+ `重叠时间`：本通信组内所有 PCCL kernel 重叠的时间
+ `持续时间`：从本通信组第一个 kernel 开始执行到最后一个 kernel 停止执行的时间

不同步比例计算方式为：(`持续时间` - `重叠时间`) / `持续时间`。

`Desync P90`列的计算方法为：将`相同kernel名称`的通信组统计结果根据不同步率升序排列，获取第 90 百分位的不同步率，本数值表示大部分 PCCL 通信不同步率优于此结果。

按照`每kernel名称`统计通信组的耗时和不同步占比，按照通信组的耗时汇总降序输出。

`pccl_desync_summary`表格列说明如下：

+ 注意“Time”列是根据“Total Duration”列的总和计算得出的，表示该 PCCL kernel 所在通信组耗时占所有列出的通信组耗时总时长的百分比，而不是根据应用执行时间得到的百分比。

```text
Row# : Row number of PCCL communication summary
Time [%] : Percentage of 'Total Duration'
Count : Number of communication of this PCCL kernel
Desync P90 [%] : 90th percentile desynchronization rate of this PCCL kernel
Desync Avg [%] : Average desynchronization rate of this PCCL kernel
Desync Med [%] : Median desynchronization rate of this PCCL kernel
Desync Min [%] : Smallest desynchronization rate of this PCCL kernel
Desync Max [%] : Largest desynchronization rate of this PCCL kernel
Desync StdDev [%] : Standard deviation of desynchronization rate of this PCCL kernel
Total Duration [ns] : Total elapsed duration of all communication of this PCCL kernel
Total Overlap [ns] : Total overlap duration of all communication of this PCCL kernel
Kernel Name : Name of the PCCL kernel
```

**命令行使用方法**

```bash
asys stats -r pccl_desync_summary report.asysrep
```

可通过`asys stats --help-report pccl_desync_summary`查看具体帮助信息，支持的选项列举如下：

+ hgtx-name：kernel 名字前通过`/`拼接最接近 kernel launch 的 HGTX range 名称
+ base：使用 kernel 的短名称（仅函数名，不包含参数）进行统计和输出
+ mangled：使用 kernel 的 mangled 名称进行统计和输出
+ device：指定统计的 PPU device ID 列表，多个 PPU device ID 之间通过`/`分割。若不指定，默认统计所有 PPU device

报告结果示例如下：

```text
Row#,Time (%),Count,Desync Avg (%),Desync Med (%),Desync Min (%),Desync Max (%),Desync StdDev (%),Total Duration (ns),Total Overlap (ns),Kernel Name,
1,95.4,4,98.3,98.9,95.3,100.0,1.9,931583768,60421,"pcclKernel_AllReduce_RING_LL_Sum_uint8_t(ncclWorkElem)",
2,4.6,1,100.0,100.0,100.0,100.0,0.0,44549251,17168,"pcclKernel_AllReduce_RING_LL_Sum_double(ncclWorkElem)",
```

**GUI 使用指南**

+ 规则设置（Settings）
    - Kernel Name Mode：Kernel Name 的展示模式。包括三种模式：
        * Base：导出 kernel 的短名称（仅函数名，不包含参数）
        * Mangled：导出 kernel 的 mangled 名称
        * Demangled：导出 kernel 的 demangle 之后的名称（默认值）
    - PPU Devices：PPU device 过滤器，统计结果按照所选的 PPU device 进行过滤，默认值为“All”，统计所有 PPU devices 的数据，此项不能为空。
    - Add HGTX name as a prefix：使能名字前拼接最接近 kernel launch 的 HGTX 名称，通过`/`间隔。默认不勾选。
+ 饼图统计：对所有 PCCL kernel 通信组的总耗时进行汇总。

##### 5.2.3.20. 设备属性信息
将 asysrep 报告中的 PPU 设备属性信息导出，输出 PPU 设备的基础参数信息，按照设备索引升序输出。

依赖的 asys 采集选项：

+ `--trace hggc`

**统计规则**

将 PPU 设备的各项参数信息，按照设备索引升序输出，每个 PPU 设备为表格的一行信息。

ppu_device_attribute 表格列说明如下，

+ 注意`CU Clock`和`Memory Clock`为设备支持的最高频率，并非 PPU 设备的实时频率信息：

```text
Row# : Row number of device attribute
Device ID : PPU device identifier
Device Name : PPU device name
PCI Bus ID : PCI bus identifier
Host Name : Host Name
UUID : PPU device universally unique identifier
Compute Capability Major : Compute capability major version
Compute Capability Minor : Compute capability minor version
CE Number : Compute engine number
CU Number : Compute unit number
Total Memory [bytes] : Total device memory size
CU Clock [Hz] : Compute unit clock frequency
Memory Clock [Hz] : Memory clock frequency
```

**命令行使用方法**

```bash
asys stats -r ppu_device_attribute report.asysrep
```

报告结果示例如下：

```text
Row#,Device ID,Device Name,PCI Bus ID,Host Name,UUID,Compute Capability Major,Compute Capability Minor,CE Number,CU Number,Total Memory (bytes),CU Clock (Hz),Memory Clock (Hz),
1,0,"PPU-ZW810E","00000001:C9:00.0","host.example.com","-",8,0,16,64,103079215104,1700000000,1800000000,
2,1,"PPU-ZW810E","00000001:C8:00.0","host.example.com","-",8,0,16,64,103079215104,1700000000,1800000000,
...
```

##### 5.2.3.21. PPU 算子汇总
将 asysrep 报告中的 PPU 算子按照类型和参数取值进行分组，汇总每组 PPU 算子在 PPU 上的执行时间，并估算每组 PPU 算子的 PPU 硬件利用率。

依赖的 asys 采集选项：

+ `--trace hggc,hgtx`

**注意：**
在采集 asysrep 报告前，建议使能 PPU 算子 HGTX range 标注相关功能：
- 执行`export PPU_LIB_PERF_INSTRUMENT=1`配置环境变量，使能基础框架 PPU 算子 HGTX range 标注功能
- asys 添加选项`--pytorch autograd-shapes-hgtx`，使能 PyTorch 算子 HGTX range 标注功能

**统计规则**

PPU 算子的执行时间统计方式为：

+ 每个 PPU 算子在 PPU 侧的执行时间为：本算子关联的 PPU 侧第一个活动开始，到最后一个活动结束的持续时间

PPU 算子的 PPU 活跃时间`PPU Active Time`计算方式为：

+ 指定的时间点存在一个或者多个本 PPU 算子关联的 PPU 活动，则记为活跃时间。如果多个 PPU 活动在时间上重叠，重叠的部分不会被多次计入活跃时间

PPU 算子的执行信息汇总时，若两个 PPU 算子之间大部分参数相同，仅少量对性能影响较小的参数存在差异，默认会忽略参数差异，按照相同的 PPU 算子合并汇总。

若算子类型指定了`others`类型，未关联到 PPU 算子的 kernel 也参与统计，根据 kernel 名称进行汇总。

汇总结果组织如下：每 PPU 算子参数组合（默认忽略性能影响较小的参数差异），汇总每个算子的执行时间信息，结果按照 Total Time 列降序输出。

PPU 计算能力利用率估算的计算方法为：

+ `本算子计算量` / (`PPU计算每秒峰值能力` * `算子平均执行时间`)

HBM load 和 store 利用率估算的计算方法为：

+ `本算子的数据量` / (`HBM每秒峰值吞吐能力` * `算子平均执行时间`)

`ppu_op_sum`表格列说明如下：

+ 注意“Percent”列是根据“Total Time”列的总和计算得出的，表示该 PPU 算子总耗时占所有列出的算子耗时总时长的百分比，而不是根据应用执行时间得到的百分比。

```text
Row# : Row number of the PPU operator summary
OP type : PPU operator type
Total Time [ns] : Total time used by all kernel instances of this operator
Percent [%] : Percentage of 'Total Time'
Instances : Number of this operator
Avg [ns] : Average execution time of this operator
Med [ns] : Median execution time of this operator
Min [ns] : Smallest execution time of this operator
Max [ns] : Largest execution time of this operator
PPU Active Time [ns] : Total PPU active time excluding overlapping for this operator
Active Percent [%] : Percentage of active time to total duration time
StdDev [ns] : Standard deviation of the time of this operator
Compute Util [%] : Utilization ratio of PPU compute capability
HBM Load Util [%] : Utilization ratio of PPU HBM load bandwidth
HBM Store Util [%] : Utilization ratio of PPU HBM store bandwidth
OP Name : Name of the PPU operator
```

**命令行使用方法**

```bash
asys stats -r ppu_op_sum report.asysrep
```

可通过`asys stats --help-report ppu_op_sum`查看具体帮助信息，支持的选项列举如下：

+ rows=`<limit>`：限制输出结果的条数
+ device=`<device_list>`：指定统计的 PPU device ID 列表，多个 PPU device ID 之间通过`/`分割。若不指定，默认统计所有 PPU device
+ range-include=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式白名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ range-exclude=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式黑名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ op=`<operator_filter>`：指定参与统计的 PPU 算子类型列表，多个 PPU 算子类型之间通过`/`分割。若不指定，默认统计所有支持的 PPU 算子类型。若指定`others`类型，未关联到 PPU 算子的 kernel 也将在统计结果中体现
+ order-by=`<order_type>`：指定输出结果排序方式，默认按照算子时间占比排序
+ no-graph-mapping：若指定，不再映射 HGGC graph 创建阶段的 HGTX 到 HGGC graph 执行阶段
+ no-merge-flash-attention-prefill-decode-operator：若指定，不再匹配和合并 prefill 和 decode 的 flash attention 算子
+ no-merge-flash-attention-parameter：若指定，不再忽略 flash attention 算子对性能影响较小的参数差异
+ no-merge-communication-parameter：若指定，不再忽略通信算子对性能影响较小的参数差异
+ no-merge-moe-parameter：若指定，不再忽略 MoE 算子对性能影响较小的参数差异
+ no-merge-pytorch-parameter：若指定，不再忽略 PyTorch 算子对性能影响较小的参数差异
+ no-merge-gemm-parameter：若指定，不再忽略 GEMM 算子对性能影响较小的参数差异

可通过`--ppu-op-config`选项自定义算子识别规则，可指定正则表达式通过匹配 HGTX range 名称或者 kernel 名称识别指定算子类型，格式为`算子类型=匹配类型：过滤规则`，可多次通过`--ppu-op-config`选项创建多个算子识别规则，例如：

```bash
--ppu-op-config GEMM=kernel:gemv --ppu-op-config Pytorch=hgtx:aten
```

+ `--ppu-op-config GEMM=kernel:gemv`：匹配 kernel 名称包含`gemv`关键字的 kernel，分类到`GEMM`算子类型
+ `--ppu-op-config Pytorch=hgtx:aten`：匹配 HGTX range 名称包含`aten`关键字，HGTX range 关联的 PPU 活动分类到`PyTorch`算子类型

报告结果示例如下：

```text
Row#,OP Type,Total Time (ns),Percent (%),Instances,Avg (ns),Med (ns),Min (ns),Max (ns),StdDev (ns),PPU Active Time (ns),Active Percent (%),Compute Util (%),HBM Load Util (%),HBM Store Util (%),OP Name,
1,"MoE",1714874135,51.1,3020,567839,564123,1280,668923,21134,1711260616,99.8,8.6,"-",0.1,"MoE:M_72_E8_H6144_In8192_topk2",
2,"PCCL",146435489,4.4,6088,24053,20080,16240,6148511,86558,146435489,100.0,"-","-","-","AllReduce, p:0, c:442368, d:9, r:0, w:4, h:c70515c91cef61c7, t:1, b:0x119e800000/0x119e8d8000",
3,"GEMM",79589151,2.4,3022,26336,26240,25200,31761,720,78991428,99.2,15.4,33.3,0.0,"ACBLAS:GemmEx,t,n,2048,72,6144,6144,6144,2048,1,0,1,DEFAULT,BF16,ACBLAS_GEMM_DEFAULT_TENSOR_OP,32F,EPILOGUE_DEFAULT",
...
```

**GUI 使用指南**

+ 通过选中行来统计求列和
    - 统计结果表格中的“Total Time”和“Percent”列支持对选中行数据自动求和，统计结果显示在表头的第二行中。当没有行被选中时，对该列的所有行进行统计求和。
+ 规则设置（Settings）
    - PPU Devices：PPU device 过滤器，统计结果按照所选的 PPU device 进行过滤，默认值为“All”，统计所有 PPU devices 的数据，此项不能为空。
    - Merge operator parameters：忽略对算子对性能影响较小的参数差异，将其合并统计。默认对所有类型的算子都启用。
    - HGTX graph node mapping：是否投影 HGGC graph capture 阶段 HGTX 到 PPU 侧（通过在 HGTX range 范围内创建的 HGGC graph node 建立与 PPU 侧的关联）。默认值为“Yes”。
    - Range Name Filter：对结果中的 HGTX range name 进行过滤，采用（Perl 兼容的）正则表达式匹配的方式，默认显示所有 HGTX range。带有正则表达式语法检查，当输入的正则表达式语法错误时，出现错误提示并且不允许保存设置
    - Show top N results：展示前 N 条结果，默认为“-1”，即不限制展示结果条数。
    - Parse from：选择解析算子的来源，所有 ppu 活动都只能通过使能的算子解析来源尝试进行解析，若解析成功则会纳入算子统计的结果中。默认值为“ALL”，从所有支持的解析来源对 ppu 活动进行解析，此项不能为空。
    - Custom operator parse config：自定义算子解析规则，使能后可以自行添加算子解析规则，通过 kernel 名或 HGTX 名+正则表达式匹配，解析出自定义的算子类型。该自定义解析规则优先级高于上面的“Parse from”选项。默认为空。
+ 饼图统计：对算子类型（OP Type）或算子名称（OP Name）的总耗时进行统计。可以直观地查看各个算子类型或具体算子的耗时占比。

##### 5.2.3.22. MoE 算子汇总
将 asysrep 报告中的 MoE 算子按照类型和参数取值进行分组，汇总每组 MoE 算子在 PPU 上的执行时间，并估算每组 MoE 算子 GEMM 运算的 PPU 硬件利用率。

依赖的 asys 采集选项：

+ `--trace hggc,hgtx`

**注意：**
在采集 asysrep 报告前，需要执行`export PPU_LIB_PERF_INSTRUMENT=1`配置环境变量，使能 PPU 算子 HGTX range 标注功能。

**统计规则**

MoE 算子的执行时间统计方式为：

+ 每个 MoE 算子在 PPU 侧的执行时间为：本算子关联的 PPU 侧 kernel 的执行时间累加
+ 统计每个 MoE 算子的第一个和第二个 GEMM 算子的执行时间

MoE 算子的执行信息汇总时，若两个 MoE 算子之间大部分参数相同，仅少量对应能影响较小的参数差异，默认会忽略参数差异，按照相同的 MoE 算子合并汇总。

汇总结果组织如下：每 MoE 算子参数组合（默认忽略性能影响较小的参数差异），汇总每个算子的执行时间信息，结果按照 Total Time 列降序输出。

GEMM 算子的 PPU 计算能力利用率估算的计算方法为，第一个和第二个 GEMM 算子的利用率单独计算：

+ `本GEMM算子计算量` / (`PPU计算每秒峰值能力` * `GEMM kernel平均执行时间`)

GEMM 算子的 HBM load 和 store 利用率估算的计算方法为：

+ `本GEMM算子的数据量` / (`HBM每秒峰值吞吐能力` * `GEMM kernel平均执行时间`)

moe_op_sum 表格说明如下：

+ 注意“Percent”列是根据“Total Time”列的总和计算得出的，表示该 MoE 算子总耗时占所有列出的算子耗时总时长的百分比，而不是根据应用执行时间得到的百分比。

```text
Row# : Row number of the MoE operator summary
Total Time [ns] : Total time used by all kernel instances of this operator
Percent [%] : Percentage of 'Total Time'
GEMM1 Total Time [ns] : Total time used by GEMM 1 kernel
GEMM2 Total Time [ns] : Total time used by GEMM 2 kernel
Instances : Number of this MoE operator
Avg [ns] : Average execution time of this operator's kernel
Med [ns] : Median execution time of this operator's kernel
Min [ns] : Smallest execution time of this operator's kernel
Max [ns] : Largest execution time of this operator's kernel
StdDev [ns] : Standard deviation of the time of this operator's kernel
GEMM1 Compute Util [%] : GEMM 1 utilization ratio of PPU compute capability
GEMM2 Compute Util [%] : GEMM 2 utilization ratio of PPU compute capability
GEMM1 HBM Load Util [%] : GEMM 1 Utilization ratio of PPU HBM load bandwidth
GEMM1 HBM Store Util [%] : GEMM 1 Utilization ratio of PPU HBM Store bandwidth
GEMM2 HBM Load Util [%] : GEMM 2 Utilization ratio of PPU HBM load bandwidth
GEMM2 HBM Store Util [%] : GEMM 2 Utilization ratio of PPU HBM Store bandwidth
OP Name : Name of the MoE operator
```

**命令行使用方法**

```bash
asys stats -r moe_op_sum report.asysrep
```

可通过 asys stats --help-report moe_op_sum 查看具体帮助信息，支持的选项列举如下：

+ device=`<device_list>`：指定统计的 PPU device ID 列表，多个 PPU device ID 之间通过`/`分割。若不指定，默认统计所有 PPU device
+ range-include=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式白名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ range-exclude=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式黑名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ no-graph-mapping：若指定，不再映射 HGGC graph 创建阶段的 HGTX 到 HGGC graph 执行阶段
+ no-merge-moe-parameter：若指定，不再忽略 MoE 算子对性能影响较小的参数差异

报告结果示例如下：

```text
Row#,Total Time (ns),Percent (%),GEMM1 Total Time (ns),GEMM2 Total Time (ns),Instances,Avg (ns),Med (ns),Min (ns),Max (ns),StdDev (ns),GEMM1 Compute Util (%),GEMM2 Compute Util (%),GEMM1 HBM Load Util (%),GEMM1 HBM Store Util (%),GEMM2 HBM Load Util (%),GEMM2 HBM Store Util (%),OP Name,
1,4400578,0.2,2199129,1617367,6,733429,732642,729163,739724,3299,43.2,29.4,30.2,0.1,20.1,0.9,"MoE:M_876_E_128_H_4096_In_384_topk_8_topkids[136,0,25,167,68,17,3,5...]_unique_102",
2,4377299,0.2,2218248,1581567,6,729549,729244,726804,734042,2398,42.8,30.0,29.9,0.1,20.6,0.9,"MoE:M_876_E_128_H_4096_In_384_topk_8_topkids[0,28,0,17,24,81,10,143,...]_unique_102",
...
```

**GUI 使用指南**

+ 通过选中行来统计求列和
    - 统计结果表格中的“Total Time”和“Percent”列支持对选中行数据自动求和，统计结果显示在表头的第二行中。当没有行被选中时，对该列的所有行进行统计求和。
+ 规则设置（Settings）
    - PPU Devices：PPU device 过滤器，统计结果按照所选的 PPU device 进行过滤，默认值为“All”，统计所有 PPU devices 的数据，此项不能为空。
    - HGTX graph node mapping：是否投影 HGGC graph capture 阶段 HGTX 到 PPU 侧（通过在 HGTX range 范围内创建的 HGGC graph node 建立与 PPU 侧的关联）。默认值为“Yes”。
    - Range Name Filter：对结果中的 HGTX range name 进行过滤，采用（Perl 兼容的）正则表达式匹配的方式，默认显示所有 HGTX range。带有正则表达式语法检查，当输入的正则表达式语法错误时，出现错误提示并且不允许保存设置
    - Merge MoE parameters：忽略对 MoE 算子对性能影响较小的参数差异，将其合并统计，默认使能。
+ 饼图统计：对算子名称（OP Name）的总耗时进行统计。可以直观地查看各个算子的耗时占比。

##### 5.2.3.23. PCCL 算子汇总
将 asysrep 报告中的 PCCL 算子按照类型和参数取值进行分组，汇总每组 PCCL 通信在各个 PPU 设备的通信时间，计算每组 PCCL 通信的 PPU 通信带宽。

依赖的 asys 采集选项：

+ `--trace hggc,hgtx`

**统计规则**

PCCL 算子的合并规则为：

+ 相同通信组、相同的 PCCL 算子类型（如 AllReduce）、相同数据量的多个 PPU 设备的算子合并计算

PCCL 算子类型分为如下两类：

+ collective 类型，如 AllReduce、Broadcast
+ point to point 类型，如 Send、Recv

对于 collective 类型的 PCCL 算子，统计规则如下：

+ 对于每次 PCCL 算子通信，将参与通信的 PPU 设备中执行时间最短的 PCCL kernel 的执行时间，作为本次通信的传输时间`Trans Time`，所有参与通信的 PPU 设备的传输时间的累加，作为统计结果的`Trans Time`的取值
+ 统计结果的`Instances`列表示 PCCL 算子通信发生的次数，对于 PCCL 算子通信涉及多个 PPU 设备的场景，多个 PPU 设备不会导致`Instances`累加多次
+ 对于每次 PCCL 算子通信，将每个 PPU 设备传输数据量进行累加，作为统计结果的`Trans Size`的取值

对于 point to point 类型的 PCCL 算子，统计规则如下：

+ 每次 PCCL 算子通信的 kernel 执行时间即认为是算子的传输时间，作为统计结果的`Trans Time`的取值
+ PCCL 算子通信的 kernel 执行次数，作为统计结果的`Instances`的取值

输出结果按照`Trans Time`降序输出。

pccl_op_sum 表格说明如下：

+ `Trans Time`列表示本组 PCCL 通信的实际传输耗时，去除由于多个 PPU 设备不同步导致的等待时间
+ `Instances`列表示本算子对应的每组 PCCL 通信发生的次数，例如对于`AllReduce`算子，所有 PPU 完成一次`AllReduce`操作，本列取值+1
+ `Device Mask`列表示本算子涉及的 PPU 设备的 bitmap，每个 bit 表示参与的 PPU 设备索引

```text
Row# : Row number of the PCCL operator summary
Trans Time [ns] : Transmission time used by all kernel instances of this operator
Trans Percent [%] : Percentage of actual transmission time relative to 'Total Time'
Total Time [ns] : Total time used by all kernel instances of this operator
Instances : Number of grouped transmission of this PCCL operator
Device Mask : PPU device mask of this PCCL operator
Trans Size [bytes] : Total transmission data size of this operator
Trans Bandwidth [B/s] : Transmission bandwidth
OP Name : Name of the PCCL operator
```

**命令行使用方法**

```bash
asys stats -r pccl_op_sum report.asysrep
```

可通过 asys stats --help-report pccl_op_sum 查看具体帮助信息，支持的选项列举如下：

+ device=`<device_list>`：指定统计的 PPU device ID 列表，多个 PPU device ID 之间通过`/`分割。若不指定，默认统计所有 PPU device
+ range-include=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式白名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ range-exclude=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式黑名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ no-graph-mapping：若指定，不再映射 HGGC graph 创建阶段的 HGTX 到 HGGC graph 执行阶段

报告结果示例如下：

```text
Row#,Trans Time (ns),Trans Percent (%),Total Time (ns),Instances,Device Mask,Trans Size (bytes),Trans Bandwidth (B/s),OP Name,
1,3899723152,94.0,4149397116,461,"0xF",464057794560,118997625337,"AllReduce, p:0, c:83886080, d:9, r:1, w:4, h:9da3d23b9ccef54c, t:1, b:0x301a000000/0x302d000000",
2,999480648,98.1,1018779730,129,"0xF",118878474240,118940246094,"AllReduce, p:0, c:76794880, d:9, r:1, w:4, h:9da3d23b9ccef54c, t:1, b:0x301a000000/0x3023279800",
3,100490800,68.8,146110859,1419,"0xF",1394933760,13881208628,"AllReduce, p:0, c:81920, d:9, r:1, w:4, h:9da3d23b9ccef54c, t:1, b:0x573c00000/0x573c28000",
...
```

**GUI 使用指南**

+ 通过选中行来统计求列和
    - 统计结果表格中的“Trans Time”、“Total Time”和“Trans Size”列支持对选中行数据自动求和，统计结果显示在表头的第二行中。当没有行被选中时，对该列的所有行进行统计求和。
+ 规则设置（Settings）
    - PPU Devices：PPU device 过滤器，统计结果按照所选的 PPU device 进行过滤，默认值为“All”，统计所有 PPU devices 的数据，此项不能为空。
    - HGTX graph node mapping：是否投影 HGGC graph capture 阶段 HGTX 到 PPU 侧（通过在 HGTX range 范围内创建的 HGGC graph node 建立与 PPU 侧的关联）。默认值为“Yes”。
    - Range Name Filter：对结果中的 HGTX range name 进行过滤，采用（Perl 兼容的）正则表达式匹配的方式，默认显示所有 HGTX range。带有正则表达式语法检查，当输入的正则表达式语法错误时，出现错误提示并且不允许保存设置
+ 饼图统计：对算子名称（OP Name）的传输耗时（Trans Time）进行统计。可以直观地查看各个算子的传输耗时占比。

##### 5.2.3.24. PPU metric 跟踪
将 asysrep 报告中的 PPU metrics sampling 跟踪数据导出，输出每 PPU 设备每 metric 名称每次采样的结果。

依赖的 asys 采集选项：

+ `--ppu-metrics-device all`

**统计规则**

导出结果组织如下：每 PPU 设备、每 PPU metric 名称、每采样时间导出一行数据，按照采样时间升序输出。

ppu_metric_trace 表格列说明如下：

```bash
Row# : Row number of the PPU metric trace
Device ID : PPU device identifier
Start [ns] : Timestamp when metric sample begin
Duration [ns] : Length of metric sample
Name : PPU metric name
Value : PPU metric value
Unit : PPU metric unit
```

**命令行使用方法**

```bash
asys stats -r ppu_metric_trace report.asysrep
```

可通过`asys stats --help-report ppu_metric_trace`查看具体帮助信息，支持的选项列举如下：

+ device=`<device_list>`：指定统计的 PPU device ID 列表，多个 PPU device ID 之间通过`/`分割。若不指定，默认统计所有 PPU device
+ metrics=`<regex_filter>`：指定参与统计的 PPU metrics 过滤正则表达式。若不指定，默认统计所有 PPU metrics

报告结果示例如下：

```text
Row#,Device ID,Start (ns),Duration (ns),Name,Value,Unit,
1,0,201274082,1089858,"ce__cycles_elapsed.avg.per_second",1600518599.7,"cycle/second",
2,0,201274082,1089858,"ce__cycles_active.avg.pct_of_peak_sustained_elapsed",98.7,"%",
...
16,1,201285295,1100045,"ce__cycles_elapsed.avg.per_second",199990000.4,"cycle/second",
17,1,201285295,1100045,"ce__cycles_active.avg.pct_of_peak_sustained_elapsed",0.0,"%",
18,1,201285295,1100045,"gd__dispatch_count.avg.pct_of_peak_sustained_elapsed",0.0,"%",
...
```

**GUI 使用指南**

+ 规则设置（Settings）
    - PPU Devices：PPU device 过滤器，统计结果按照所选的 PPU device 进行过滤，默认值为“All”，统计所有 PPU devices 的 metric sampling 数据，此项不能为空。
    - Metric Name Filter：对结果中的 PPU metric name 进行过滤，采用（Perl 兼容的）正则表达式匹配的方式，默认显示所有 metrics。带有正则表达式语法检查，当输入的正则表达式语法错误时，出现错误提示并且不允许保存设置

##### 5.2.3.25. HGTX push pop range 跟踪
将 asysrep 报告中的 push pop 类型的 HGTX range 跟踪数据导出，输出 HGTX range 堆栈信息和父子关系信息。

依赖的 asys 采集选项：

+ `--trace hgtx`

**统计规则**

HGTX domain push pop range 和非 domain 类型的 push pop range 均参与统计，HGTX range 的堆栈信息取决于 HGTX range 开始时本线程的 HGTX range 堆栈状态。

对于每个 HGTX range，统计结果中的 child range 指堆栈中本 HGTX range 嵌套的次级 HGTX range，不包含更深层级嵌套的 HGTX range。

导出结果组织如下：每 HGTX range 跟踪输出一行数据，按照 HGTX range 开始时间升序输出。

hgtx_pushpop_trace 表格列说明如下：

```text
Row# : Row number of the HGTX range trace
Start [ns] : Range start timestamp
End [ns] : Range end timestamp
Duration [ns] : Range duration
DurChild [ns] : Duration of all child ranges
DurNonChild [ns] : Duration of this range minus child ranges
Name : Name of the HGTX range
PID : Process ID
TID : Thread ID
Lvl : Stack level, starts at 0
NumChild : Number of children ranges
RangeId : Arbitrary ID for range
ParentId : Range ID of the enclosing range
RangeStack : Range IDs that make up the push/pop stack
NameTree : Range name prefixed with level indicator
```

**命令行使用方法**

```bash
asys stats -r hgtx_pushpop_trace report.asysrep
```

可通过`asys stats --help-report hgtx_pushpop_trace`查看具体帮助信息，支持的选项列举如下：

+ range=`<regex_filter>`：指定参与统计的 HGTX range 过滤正则表达式。若不指定，默认统计所有 HGTX range

报告结果示例如下：

```text
Row#,Start (ns),End (ns),Duration (ns),DurChild (ns),DurNonChild (ns),Name,PID,TID,Lvl,NumChild,RangeId,ParentId,RangeStack,NameTree,
1,173403462,309023366,135619904,0,135619904,"profile",3730996,3730996,0,0,6,"-",":6","profile",
2,173765782,298721096,124955314,112237187,12718127,"Loop1",3730996,3731078,0,1,7,"-",":7","Loop1",
3,173985240,264616466,90631226,78300490,12330736,"Loop1",3730996,3731079,0,1,9,"-",":9","Loop1",
4,174054855,298794768,124739913,109974015,14765898,"Loop1",3730996,3731080,0,1,11,"-",":11","Loop1",
5,185211331,263511821,78300490,0,78300490,"DoProcess",3730996,3731079,1,0,13,9,":9:13","-DoProcess",
...
```

**GUI 使用指南**

+ 规则设置（Settings）
    - Range Name Filter：对结果中的 HGTX range name 进行过滤，采用（Perl 兼容的）正则表达式匹配的方式，默认显示所有 HGTX range。带有正则表达式语法检查，当输入的正则表达式语法错误时，出现错误提示并且不允许保存设置
+ 饼图统计：对各 HGTX Range 的时长（Duration）进行统计。

##### 5.2.3.26. PPU 算子跟踪
识别 asysrep 报告中的 PPU 算子，导出每个 PPU 算子关联的每个 PPU 活动跟踪。

依赖的 asys 采集选项：

+ `--trace hggc,hgtx`

**注意：**
在采集 asysrep 报告前，建议使能 PPU 算子 HGTX range 标注相关功能：
- 执行`export PPU_LIB_PERF_INSTRUMENT=1`配置环境变量，使能基础框架 PPU 算子 HGTX range 标注功能
- asys 添加选项`--pytorch autograd-shapes-hgtx`，使能 PyTorch 算子 HGTX range 标注功能

**统计规则**

PPU 算子的执行时间统计方式为：

+ 每个 PPU 算子在 PPU 侧的执行时间为：本算子关联的 PPU 侧第一个活动开始，到最后一个活动结束的持续时间

跟踪导出结果组织如下：每 PPU 算子、每 PPU 活动输出一行数据，按照 PPU 算子开始时间升序排列，相同 PPU 算子内的 PPU 活动按照活动起始时间升序排列。

`ppu_op_trace`表格列说明如下：

```text
Row# : Row number of the PCCL operator trace
OP Type : PPU operator type
Start [ns] : Start timestamp of PPU operator
Duration [ns] : Duration of PPU operator
PID : Process identifier
Device ID : PPU device identifier
Context ID : Context identifier
Stream ID : Stream identifier
PPU Active Time [ns] : PPU active time excluding overlapping for this operator
Active Percent [%] : Percentage of active time to duration time
OP Name : Name of the PPU operator
```

**命令行使用方法**

```bash
asys stats -r ppu_op_trace report.asysrep
```

可通过`asys stats --help-report ppu_op_trace`查看具体帮助信息，支持的选项列举如下：

+ device=`<device_list>`：指定统计的 PPU device ID 列表，多个 PPU device ID 之间通过`/`分割。若不指定，默认统计所有 PPU device
+ range-include=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式白名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ range-exclude=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式黑名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ op=`<operator_filter>`：指定参与统计的 PPU 算子类型列表，多个 PPU 算子类型之间通过`/`分割。若不指定，默认统计所有支持的 PPU 算子类型。若指定`others`类型，未关联到 PPU 算子的 kernel 也将在统计结果中体现
+ no-merge-flash-attention-prefill-decode-operator：若指定，不再匹配和合并 prefill 和 decode 的 flash attention 算子

可通过`--ppu-op-config`选项自定义算子识别规则，可指定正则表达式通过匹配 HGTX range 名称或者 kernel 名称识别指定算子类型，格式为`算子类型=匹配类型：过滤规则`，可多次通过`--ppu-op-config`选项创建多个算子识别规则，例如：

```bash
--ppu-op-config GEMM=kernel:gemv --ppu-op-config Pytorch=hgtx:aten
```

+ `--ppu-op-config GEMM=kernel:gemv`：匹配 kernel 名称包含`gemv`关键字的 kernel，分类到`GEMM`算子类型
+ `--ppu-op-config Pytorch=hgtx:aten`：匹配 HGTX range 名称包含`aten`关键字，HGTX range 关联的 PPU 活动分类到`PyTorch`算子类型

报告结果示例如下：

```text
Row#,OP Type,OP Name,OP Start (ns),OP Duration (ns),OP ID,Activity ID,PID,Device ID,Context ID,Stream ID,Activity Start (ns),Activity Duration (ns),Activity Name,
1,"PCCL","AllReduce, p:0, c:442368, d:9, r:2, w:4, h:c70515c91cef61c7, t:1, b:0x119e800000/0x119e8d8000",136493999,16760,429199,535257,3790741,2,1,1,136493999,16760,"void pcclKernel_twoShotAllReduceKernel<__ppu_bfloat16, 4, 0, 0, 1, 1>(twoShotDevParams)",
2,"GEMM","ACBLAS:GemmEx,t,n,2048,72,6144,6144,6144,2048,1,0,1,DEFAULT,BF16,ACBLAS_GEMM_DEFAULT_TENSOR_OP,32F,EPILOGUE_DEFAULT",136513799,30320,429204,535262,3790741,2,1,1,136513799,26520,"gemm_ktype0_aiu1_mtype1_dtypeBF16xBF16xFP32xBF16xBF16_tile128x256x64x64x64x2_layout0x1x0x0_align1x1x8x8_splitk2_fusion0_prefetch0_fp32tc0_ptrhost1_schedule0",
...
```

**GUI 使用指南**

+ 规则设置（Settings）
    - PPU Devices：PPU device 过滤器，统计结果按照所选的 PPU device 进行过滤，默认值为“All”，统计所有 PPU devices 的数据，此项不能为空。
    - Range Name Filter：对结果中的 HGTX range name 进行过滤，采用（Perl 兼容的）正则表达式匹配的方式，默认显示所有 HGTX range。带有正则表达式语法检查，当输入的正则表达式语法错误时，出现错误提示并且不允许保存设置
    - Parse from：选择解析算子的来源，所有 ppu 活动都只能通过使能的算子解析来源尝试进行解析，若解析成功则会纳入算子统计的结果中。默认值为“ALL”，从所有支持的解析来源对 ppu 活动进行解析，此项不能为空。
    - Custom operator parse config：自定义算子解析规则，使能后可以自行添加算子解析规则，通过 kernel 名或 HGTX 名+正则表达式匹配，解析出自定义的算子类型。该自定义解析规则优先级高于上面的“Parse from”选项。默认为空。
    - Merge flash attention prefill decode operators：将 flash attention 算子中的 prefill 和 decode 视作一个算子合并统计。
+ 饼图统计：对算子类型（OP Type）或算子名称（OP Name）的总耗时进行统计。可以直观地查看各个算子类型或具体算子的耗时占比。

##### 5.2.3.27. PPU 算子类型汇总
识别 asysrep 报告中的 PPU 算子，按照算子类型分组，汇总每种算子类型的所有算子在 PPU 上的执行时间，并输出每种算子类型的热点算子信息。

依赖的 asys 采集选项：

+ `--trace hggc,hgtx`

**注意：**
在采集 asysrep 报告前，建议使能 PPU 算子 HGTX range 标注相关功能：
- 执行`export PPU_LIB_PERF_INSTRUMENT=1`配置环境变量，使能基础框架 PPU 算子 HGTX range 标注功能
- asys 添加选项`--pytorch autograd-shapes-hgtx`，使能 PyTorch 算子 HGTX range 标注功能

**统计规则**

PPU 算子的执行时间统计方式为：

+ 每个 PPU 算子在 PPU 侧的执行时间为：本算子关联的 PPU 侧第一个活动开始，到最后一个活动结束的持续时间

PPU 算子的 PPU 活跃时间`PPU Active Time`计算方式为：

+ 指定的时间点存在一个或者多个本 PPU 算子关联的 PPU 活动，则记为活跃时间。如果多个 PPU 活动在时间上重叠，重叠的部分不会被多次计入活跃时间

汇总结果组织如下：

+ 每 PPU 算子类型，汇总每个算子的执行时间信息，结果按照 Total Time 降序排列
+ 每 PPU 算子类型内，对每种算子参数组合的执行时间汇总，挑选汇总执行时间最长的算子参数组合，作为热点算子
+ 固定生成`Summary`类型的汇总行，汇总所有 PPU 算子类型的执行时间信息，挑选汇总执行时间最长的算子参数组合，作为汇总行的热点算子

`ppu_op_type_sum`表格列说明如下：

+ `OP Type`列为`Summary`的行固定为汇总行，汇总所有 PPU 算子类型的执行时间信息

```text
Row# : Row number of the PPU operator type summary
OP Type : PPU operator type
Percent [%] : Percentage of 'Total Time'
Avg [ns] : Average duration of this operator type
Total Time [ns] : Total duration used by all instances of this operator type
Instances : Number of this PPU operator type
PPU Active Time [ns] : Total PPU active time excluding overlapping for this operator type
Active Percent [%] : Percentage of active time to total duration time
Top OP Percent [%] : Percentage of top PPU operator of 'Total Time'
Top OP Name : Name of the top PPU operator of this type
```

**命令行使用方法**

```bash
asys stats -r ppu_op_type_sum report.asysrep
```

可通过 asys stats --help-report ppu_op_type_sum 查看具体帮助信息，支持的选项列举如下：

+ device=`<device_list>`：指定统计的 PPU device ID 列表，多个 PPU device ID 之间通过`/`分割。若不指定，默认统计所有 PPU device
+ range-include=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式白名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ range-exclude=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式黑名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ op=`<operator_filter>`：指定参与统计的 PPU 算子类型列表，多个 PPU 算子类型之间通过`/`分割。若不指定，默认统计所有支持的 PPU 算子类型。若指定`others`类型，未关联到 PPU 算子的 kernel 也将在统计结果中体现
+ no-graph-mapping：若指定，不再映射 HGGC graph 创建阶段的 HGTX 到 HGGC graph 执行阶段
+ no-merge-flash-attention-prefill-decode-operator：若指定，不再匹配和合并 prefill 和 decode 的 flash attention 算子
+ no-merge-flash-attention-parameter：若指定，不再忽略 flash attention 算子对性能影响较小的参数差异
+ no-merge-communication-parameter：若指定，不再忽略通信算子对性能影响较小的参数差异
+ no-merge-moe-parameter：若指定，不再忽略 MoE 算子对性能影响较小的参数差异
+ no-merge-pytorch-parameter：若指定，不再忽略 PyTorch 算子对性能影响较小的参数差异
+ no-merge-gemm-parameter：若指定，不再忽略 GEMM 算子对性能影响较小的参数差异

可通过`--ppu-op-config`选项自定义算子识别规则，可指定正则表达式通过匹配 HGTX range 名称或者 kernel 名称识别指定算子类型，格式为`算子类型=匹配类型：过滤规则`，可多次通过`--ppu-op-config`选项创建多个算子识别规则，例如：

```bash
--ppu-op-config GEMM=kernel:gemv --ppu-op-config Pytorch=hgtx:aten
```

+ `--ppu-op-config GEMM=kernel:gemv`：匹配 kernel 名称包含`gemv`关键字的 kernel，分类到`GEMM`算子类型
+ `--ppu-op-config Pytorch=hgtx:aten`：匹配 HGTX range 名称包含`aten`关键字，HGTX range 关联的 PPU 活动分类到`PyTorch`算子类型

报告结果示例如下：

```text
Row#,OP Type,Percent (%),Avg (ns),Total Time (ns),Instances,PPU Active Time (ns),Active Percent (%),Top OP Percent (%),Top OP Name,
1,"Summary",100.0,49885,3354637726,67247,3348054119,99.8,51.1,"MoE:M_72_E8_H6144_In8192_topk2",
2,"MoE",63.6,293641,2133601622,7266,2129239591,99.8,51.1,"MoE:M_72_E8_H6144_In8192_topk2",
3,"PCCL",8.2,37031,273847048,7395,273847048,100.0,4.4,"AllReduce, p:0, c:442368, d:9, r:2, w:4, h:c70515c91cef61c7, t:1, b:0x119e800000/0x119e8d8000",
...
```

**GUI 使用指南**

+ 通过选中行来统计求列和
    - 统计结果表格中的“Total Time”，“Total”，“Instances”和“PPU Active Time”列均支持对选中行数据自动求和，统计结果显示在表头的第二行中。类型为“Summary”的行不参与列的求和统计。当没有行被选中时，对该列的所有行进行统计求和。
+ 规则设置（Settings）
    - PPU Devices：PPU device 过滤器，统计结果按照所选的 PPU device 进行过滤，默认值为“All”，统计所有 PPU devices 的数据，此项不能为空。
    - Merge operator parameters：忽略对算子对性能影响较小的参数差异，将其合并统计。默认对所有类型的算子都启用。
    - Range Name Filter：对结果中的 HGTX range name 进行过滤，采用（Perl 兼容的）正则表达式匹配的方式，默认显示所有 HGTX range。带有正则表达式语法检查，当输入的正则表达式语法错误时，出现错误提示并且不允许保存设置
    - Parse from：选择解析算子的来源，所有 ppu 活动都只能通过使能的算子解析来源尝试进行解析，若解析成功则会纳入算子统计的结果中。默认值为“ALL”，从所有支持的解析来源对 ppu 活动进行解析，此项不能为空。
    - Custom operator parse config：自定义算子解析规则，使能后可以自行添加算子解析规则，通过 kernel 名或 HGTX 名+正则表达式匹配，解析出自定义的算子类型。该自定义解析规则优先级高于上面的“Parse from”选项。默认为空。
+ 饼图统计：对算子类型（OP Type）的总耗时进行统计。可以直观地查看各个算子类型的耗时占比。

##### 5.2.3.28. PPU 算子 kernel 性能分解
识别 asysrep 报告中的 PPU 算子，根据算子的种类和嵌套关系，将算子分为框架层、加速库层和 kernel 层三个层级，汇总每种算子在 PPU 上的执行时间，将性能数据逐级分解到 kernel 层，输出嵌套的算子逐层细化的性能分解信息。

依赖的 asys 采集选项：

+ `--trace hggc,hgtx`

**注意：**
在采集 asysrep 报告前，建议使能 PPU 算子 HGTX range 标注相关功能：
- 执行`export PPU_LIB_PERF_INSTRUMENT=1`配置环境变量，使能基础框架 PPU 算子 HGTX range 标注功能
- asys 添加选项`--pytorch autograd-shapes-hgtx`，使能 PyTorch 算子 HGTX range 标注功能

**统计规则**

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125073352/04bf8aeb02e8c684f4739d3aa2f835aa/pytorch_autograd_shape_1.png)

根据 HGTX 标记和 kernel 名称识别各个层级的算子，根据算子在 PPU 上的投影时间范围确定算子之间的嵌套关系。

PPU 算子被分为框架层、加速库层和 kernel 层三个层级，部分层级可能不存在 PPU 算子信息。以自顶向下的顺序查看算子的嵌套关系，处于嵌套顶层的算子（无论其归属哪个层级）为`顶层算子`。

PPU 算子汇总的`Total Time`的计算方式为：

+ 所有`顶层算子`的执行时间的累加

每种 PPU 算子的时间占比的计算方式为：

+ 累加本 PPU 算子的执行时间，得到`执行时间汇总`
+ 计算`执行时间汇总` / `Total Time`，得到本 PPU 算子的时间占比

父一级 PPU 算子范围内，未存在子一级 PPU 算子的时间范围（PPU 设备空闲），被标记为`Idle`。各个层级中缺失的父一级 PPU 算子被标记为`Native`。

汇总结果组织如下：

+ 每框架层算子、每加速库层算子、每 kernel 层算子，按照逐层的时间占比降序排列

`ppu_op_kernel_breakdown`表格列说明如下：

```text
Row# : Row number of the PPU operator kernel breakdown
OP Type : PPU operator type
Framework OP : Name of the framework layer operator
Framework Time [%] : Framework operator time percentage of 'Total Time'
Framework Avg [ns] : Average duration of this framework operator
Framework Instances : Number of this framework operator
Library OP : Name of the compute library layer operator
Library Time [%] : Library operator time percentage of 'Total Time'
Library Avg [ns] : Average duration of this library operator
Library Instances : Number of this library operator
Kernel Name : Name of the HGGC kernel
Kernel Time [%] : HGGC kernel time percentage of 'Total Time'
Kernel Avg [ns] : Average duration of this kernel
Kernel Instances : Number of this kernel
```

**命令行使用方法**

```bash
asys stats -r ppu_op_kernel_breakdown report.asysrep
```

可通过`asys stats --help-report ppu_op_kernel_breakdown`查看具体帮助信息，支持的选项列举如下：

+ rows=`<limit>`：限制输出结果的条数，部分占比较小的算子将会被忽略
+ device=`<device_list>`：指定统计的 PPU device ID 列表，多个 PPU device ID 之间通过`/`分割。若不指定，默认统计所有 PPU device
+ range-include=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式白名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ range-exclude=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式黑名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ base：使用 kernel 的短名称（仅函数名，不包含参数）进行统计和输出
+ mangled：使用 kernel 的 mangled 名称进行统计和输出
+ op=`<operator_filter>`：指定参与统计的 PPU 算子类型列表，多个 PPU 算子类型之间通过`/`分割。若不指定，默认统计所有支持的 PPU 算子类型。若指定`others`类型，未关联到 PPU 算子的 kernel 也将在统计结果中体现
+ order-by=`<order_type>`：指定输出结果排序方式，默认按照算子时间占比排序
+ no-merge-flash-attention-prefill-decode-operator：若指定，不再匹配和合并 prefill 和 decode 的 flash attention 算子
+ no-merge-flash-attention-parameter：若指定，不再忽略 flash attention 算子对性能影响较小的参数差异
+ no-merge-communication-parameter：若指定，不再忽略通信算子对性能影响较小的参数差异
+ no-merge-moe-parameter：若指定，不再忽略 MoE 算子对性能影响较小的参数差异
+ no-merge-pytorch-parameter：若指定，不再忽略 PyTorch 算子对性能影响较小的参数差异
+ no-merge-gemm-parameter：若指定，不再忽略 GEMM 算子对性能影响较小的参数差异

可通过`--ppu-op-config`选项自定义算子识别规则，通过 HGTX range 名称匹配到的自定义算子将作为框架层算子统计，通过 kernel 名称匹配到的自定义算子将作为 kernel 层算子统计。

报告结果示例如下：

```text
Row#,OP Type,Framework OP,Framework Time (%),Library OP,Library Time (%),Kernel Name,Kernel Time (%),Avg (ns),Instances,
1,"MoE","D_MoE,M_8_E_128_H_2048_In_768_topk_8",44.3,"DeepGemm:GroupedNoPad,data_type:bf16,groups:128,m:64,n:768,k:2048,gpu:0",23.3,"void deep_gemm::batched_gemvt_kernel<__nv_bfloat16, __nv_bfloat16, float, int4, int4, 256, 32, 2, 2, 2>(deep_gemm::GemvtArgs)",23.3,55495,28128,
2,"MoE","D_MoE,M_8_E_128_H_2048_In_768_topk_8",44.3,"DeepGemm:GroupedNoPad,data_type:bf16,groups:128,m:64,n:2048,k:384,gpu:0",13.0,"void deep_gemm::batched_gemvt_kernel<__nv_bfloat16, __nv_bfloat16, float, int4, int4, 256, 8, 4, 1, 1>(deep_gemm::GemvtArgs)",13.0,30975,28128,
3,"MoE","D_MoE,M_8_E_128_H_2048_In_768_topk_8",44.3,"Native",7.3,"_fwd_kernel_ep_gather",2.3,17378,28128,
4,"MoE","D_MoE,M_8_E_128_H_2048_In_768_topk_8",44.3,"Native",7.3,"_fwd_kernel_ep_scatter_2_optimal",1.1,17378,28128,
...
```

**提示：**
建议使用选项`--format xlsx`输出电子表格，统计结果更加易读。

##### 5.2.3.29. PPU 算子性能分解
识别 asysrep 报告中的 PPU 算子，根据算子的种类和嵌套关系，将算子分为框架层、加速库层和 kernel 层三个层级，将性能数据逐级分解到加速库层，输出加速库层级的性能分解信息和设备利用率信息。

依赖的 asys 采集选项：

+ `--trace hggc,hgtx`

**注意：**
在采集 asysrep 报告前，建议使能 PPU 算子 HGTX range 标注相关功能：
+ 执行`export PPU_LIB_PERF_INSTRUMENT=1`配置环境变量，使能基础框架 PPU 算子 HGTX range 标注功能
+ asys 添加选项`--pytorch autograd-shapes-hgtx`，使能 PyTorch 算子 HGTX range 标注功能

**统计规则**

根据 HGTX 标记和 kernel 名称识别各个层级的算子，根据算子在 PPU 上的投影时间范围确定算子之间的嵌套关系。

PPU 算子被分为框架层、加速库层和 kernel 层三个层级，部分层级可能不存在 PPU 算子信息。以自顶向下的顺序查看算子的嵌套关系，处于嵌套顶层的算子（无论其归属哪个层级）为`顶层算子`。

PPU 算子汇总的`Total Time`的计算方式为：

+ 所有`顶层算子`的执行时间的累加

每种 PPU 算子的时间占比的计算方式为：

+ 累加本 PPU 算子的执行时间，得到`执行时间汇总`
+ 计算`执行时间汇总` / `Total Time`，得到本 PPU 算子的时间占比

父一级 PPU 算子范围内，未存在子一级 PPU 算子的时间范围（PPU 设备空闲），被标记为`Idle`。各个层级中缺失的父一级 PPU 算子被标记为`Native`。

汇总结果组织如下：

+ 每框架层算子、每加速库层算子，按照逐层的时间占比降序排列

`ppu_op_breakdown`表格列说明如下：

```text
Row# : Row number of the PPU operator breakdown
OP Type : PPU operator type
Framework OP : Name of the framework layer operator
Framework Time [%] : Framework operator time percentage of 'Total Time'
Framework Avg [ns] : Average duration of this framework operator
Framework Instances : Number of this framework operator
Library OP : Name of the compute library layer operator
Library Time [%] : Library operator time percentage of 'Total Time'
Library Avg [ns] : Average duration of this library operator
Library Instances : Number of this library operator
Compute Util [%] : Utilization ratio of PPU compute capability
HBM Load Util [%] : Utilization ratio of PPU HBM load bandwidth
HBM Store Util [%] : Utilization ratio of PPU HBM store bandwidth
```

**命令行使用方法**

```bash
asys stats -r ppu_op_breakdown report.asysrep
```

可通过`asys stats --help-report ppu_op_breakdown`查看具体帮助信息，支持的选项列举如下：

+ rows=`<limit>`：限制输出结果的条数，部分占比较小的算子将会被忽略
+ device=`<device_list>`：指定统计的 PPU device ID 列表，多个 PPU device ID 之间通过`/`分割。若不指定，默认统计所有 PPU device
+ range-include=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式白名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ range-exclude=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式黑名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ op=`<operator_filter>`：指定参与统计的 PPU 算子类型列表，多个 PPU 算子类型之间通过`/`分割。若不指定，默认统计所有支持的 PPU 算子类型。若指定`others`类型，未关联到 PPU 算子的 kernel 也将在统计结果中体现
+ order-by=`<order_type>`：指定输出结果排序方式，默认按照算子时间占比排序
+ no-merge-flash-attention-prefill-decode-operator：若指定，不再匹配和合并 prefill 和 decode 的 flash attention 算子
+ no-merge-flash-attention-parameter：若指定，不再忽略 flash attention 算子对性能影响较小的参数差异
+ no-merge-communication-parameter：若指定，不再忽略通信算子对性能影响较小的参数差异
+ no-merge-moe-parameter：若指定，不再忽略 MoE 算子对性能影响较小的参数差异
+ no-merge-pytorch-parameter：若指定，不再忽略 PyTorch 算子对性能影响较小的参数差异
+ no-merge-gemm-parameter：若指定，不再忽略 GEMM 算子对性能影响较小的参数差异

可通过`--ppu-op-config`选项自定义算子识别规则，通过 HGTX range 名称匹配到的自定义算子将作为框架层算子统计，通过 kernel 名称匹配到的自定义算子将作为 kernel 层算子统计。

报告结果示例如下（部分列未展示）：

```text
Row#,OP Type,Framework OP,Framework Time (%),Library OP,Library Time (%),Library Avg (ns),Library Instances,Compute Util (%),HBM Load Util (%),HBM Store Util (%),
1,"MoE","D_MoE,M_8_E_128_H_2048_In_768_topk_8",44.3,"DeepGemm:GroupedNoPad,data_type:bf16,groups:128,m:64,n:768,k:2048,gpu:0",23.3,55495,28128,2.6,262.6,0.0,
2,"MoE","D_MoE,M_8_E_128_H_2048_In_768_topk_8",44.3,"DeepGemm:GroupedNoPad,data_type:bf16,groups:128,m:64,n:2048,k:384,gpu:0",13.0,30975,28128,2.3,235.1,0.0,
3,"MoE","D_MoE,M_8_E_128_H_2048_In_768_topk_8",44.3,"Native",7.3,2482,196896,"-","-","-",
4,"MoE","D_MoE,M_8_E_128_H_2048_In_768_topk_8",44.3,"Idle",0.7,1681,28128,"-","-","-",
...
```

##### 5.2.3.30. PPU 算子单元测试（实验特性）
将 asysrep 报告中的 PPU 算子按照类型和参数取值进行分组，对汇总结果的每种 PPU 算子生成单元测试代码。

依赖的 asys 采集选项：

+ `--trace hggc,hgtx`
+ `--pytorch=dispatch-function`

**注意：**
`--pytorch=dispatch-function`选项为实验特性，使能此选项可能导致应用崩溃或者应用行为异常。

**统计规则**

PPU 算子的执行时间统计方式为：

+ 每个 PPU 算子在 PPU 侧的执行时间为：本算子关联的 PPU 侧第一个活动开始，到最后一个活动结束的持续时间

PPU 算子的执行信息汇总时，若两个 PPU 算子之间大部分参数相同，仅少量对性能影响较小的参数存在差异，默认会忽略参数差异，按照相同的 PPU 算子合并汇总。

汇总结果组织如下：每 PPU 算子参数组合（默认忽略性能影响较小的参数差异），汇总每个算子的执行时间信息，结果按照 Total Time 列降序逐个生成单元测试代码。

**注意：**
部分算子不支持生成单元测试代码，所有 PPU 算子汇总的单元测试名称在报告尾部列出。

**命令行使用方法**

```bash
asys stats -r ppu_op_unit_test report.asysrep
```

可通过`asys stats --help-report ppu_op_unit_test`查看具体帮助信息，支持的部分选项列举如下：

+ device=`<device_list>`：指定统计的 PPU device ID 列表，多个 PPU device ID 之间通过`/`分割。若不指定，默认统计所有 PPU device
+ range-include=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式白名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ range-exclude=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式黑名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ op=`<operator_filter>`：指定参与统计的 PPU 算子类型列表，多个 PPU 算子类型之间通过`/`分割。若不指定，默认统计所有支持的 PPU 算子类型。若指定`others`类型，未关联到 PPU 算子的 kernel 也将在统计结果
+ no-merge-pytorch-parameter：若指定，不再忽略 PyTorch 算子对性能影响较小的参数差异

运行生成的单元测试示例如下，默认运行所有的单元测试各一次，可通过选项控制运行的用例和次数：

```bash
python report_ppu_op_unit_test.py --top 3 --warm-up 5 --repeat 5
```

+ `--top 3`：运行总耗时占比前 3 的算子的测试用例
+ `--warm-up 5`：计时之前运行 5 次
+ `--repeat 5`：计时阶段运行 5 次计算平均耗时
+ 支持`--test`选项指定测试用例名称，多个用例名称通过`,`分隔

### 5.3. 报告比较
比较两个报告的统计数据是 Asight Systems 提供的一项用于性能对比的实用功能，可以用于直观地比较两个报告在算子、kernel 等方面的性能数据。

#### 5.3.1. 从 GUI 端使用报告比较视图
与统计系统类似，在 GUI 中，可以通过下方 tab 中的 "Comparison View" 切换到报告比较视图。报告比较视图如下所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125054293/ada225bced37bb33337e966bfa5747a2/gui_5.png)

1. 规则列表，可以在此选择统计规则，支持搜索
2. 当前生效的参数配置，鼠标悬停时会显示参数的详细信息
3. 对比报告选择框，在这里选择已经打开的另一个 asys 报告作为对比的目标报告
4. 报告对比信息，给出了 base 和 target 报告的设备名、别名、报告名、统计区间等信息。同时提供交换 base/target 报告、更改报告别名的功能
5. 搜索框，支持搜索和过滤两种模式
6. 规则参数配置对话框，可以在此改变当前统计规则的配置
7. 热点柱状图，展示 base 和 target 报告的性能热点
8. 报告对比统计结果表格，显示当前规则的报告对比结果，可以通过右键菜单导出分析结果

##### 5.3.1.1. 设置统计区间
报告对比功能支持为两个进行对比的报告分别设置参与统计的时间区间，在进行报告对比时只会对选定时间区间内的事件进行统计。打开需要设置统计区间的报告，在 Timeline View 中按住鼠标左键拖动，在选定的区间内打开右键菜单，点击“Filter and Zoom in”，即可为当前报告设置统计区间。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125054739/59ae76c50519f6e4386a6b347e4097fd/gui_6.png)

##### 5.3.1.2. 对比报告选择框和对比信息
通过顶部的“Compare with”选择框，可以选择另一个已经打开的 asys 报告作为 target 报告，与当前报告进行对比。完成了选择 target 报告后，下方会显示一个对比信息表格，给出了 base 报告和 target 报告的设备名、别名、报告名、统计区间等信息。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125055138/a12911f035f07bd842fad469ee332fd3/gui_7.png)

在对比信息表格中：

+“Device”右侧，有一个交换按钮，点击后 base 报告和 target 报告会相互交换。
+“Alias”行是可编辑的，双击这一行的单元格，可以为报告起一个别名，这个别名会显示在热点柱状图的图例和右侧对比结果表格的表头中。
+“Time Range”表示当前报告的统计区间，默认会统计整个报告的时间区间。可以在对应的报告中选择一个时间区间并“Filter and Zoom in”来应用一个新的统计区间。

##### 5.3.1.3. 热点柱状图
热点柱状图会展示当前报告对比统计结果中，base 和 target 报告中的性能热点，从上到下降序排序。可以通过增加“Comparison View”的高度，使得热点柱状图中显示更多的热点行。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125040911/4813c0f3c910b28d3f4d29bf9419f7a8/device_base_target_1.png)

上图中：

+ 图题，表示柱状图展示的热点内容。
+ 图例，用不同颜色区分两个对比的报告，并显示两个报告的别名
+ 纵轴，如上图展示的是各个热点算子，排序依据是根据算子在两个报告中的占比较大值进行降序排序。点击任意一个数据柱，可以跳转至对比结果表格中的对应行。
+ 横轴，表示评估热点的指标，如上图是根据占报告总时间的比率来排序热点算子。

##### 5.3.1.4. 报告对比统计结果表格
该表格展示了各个性能参数指标在两个对比报告中的数值。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125066165/fb826e4c3c3e1a1daf4da43e1101c09d/perf_ratio_10_1.png)

+ 部分性能指标给出了 Perf Ratio，表示 target 报告相比 base 报告的性能表现，`Perf Ratio > 1.0`表示 target 报告在该性能指标上优于 base 报告，反之则表示 base 报告性能更优。
+ 部分单元格显示的值为“-”，表示当前列所在的报告没有对应的匹配项。
+ 可以点击任意列的表头对表格进行排序，点击右键可以将整个表格导出为 csv 文件。

##### 5.3.1.5. 报告对比自定义配置
在右上角的“Settings”按钮中，可以对报告对比进行一些配置，每个对比规则支持的配置项不完全相同。这里列举一些报告对比中比较有用的配置项进行介绍：

###### 5.3.1.5.1. 自定义算子解析配置
比较系统还支持自定义算子的解析方式，例如添加`SpecialGemm`算子类型：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125076274/89844df13ea178bc965807f609c264f5/special_gemm_config_1.png)

配置完成后，结果如下所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125076640/dff917db4d7b3e9fc992ed185a72617f/special_gemm_result_1.png)

**注意：**
自定义的算子解析优先级高于 asys 预置的解析

###### 5.3.1.5.2. 仅展示有效匹配的结果
在对比结果表格中，有部分行是只有 base 报告中有，target 报告中没有的未成功匹配的结果，如下图方框中所示。若只想看匹配成功的结果，可以勾选“Show matched only”选项，即可过滤掉未成功匹配的结果。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125032951/3f32e2fb70f595c4ea86e370b3c5f377/asys_compare_1.png)

#### 5.3.2. 从命令行端比较报告
可使用`asys compare`子命令比较两个 asysrep 报告文件，`asys compare`子命令是`asys stats`子命令的简化形式，支持显示简要的比较结果，并输出详细汇总数据到 csv 文件，使用示例如下：

```bash
asys compare -f true report1.asysrep report2.asysrep
```

+ `-f true`：允许输出的比较结果文件覆盖已存在的文件

可执行`asys compare -h`查看更多帮助信息。

`asys compare`子命令默认执行的比较规则示例如下：

+ PPU 算子类型汇总比较（ppu_operator_type_summary_compare）
+ PPU 时间利用率比较（ppu_time_util_compare）
+ PPU 算子汇总比较（ppu_operator_summary_compare）
+ PPU 算子 kernel 性能分解（ppu_operator_kernel_breakdown_compare）
+ PCCL 不同步汇总比较（pccl_desync_summary_compare）
+ PPU kernel 汇总比较（ppu_kernel_summary_compare）

##### 5.3.2.1. 指定统计时间范围
可通过`--filter-hgtx`选项通过 HGTX 标注指定统计的时间范围，两个报告中都将使用指定的 HGTX 确定统计时间范围。

使用`--filter-hgtx`选项可指定匹配的 HGTX range 的名称、domain 和匹配索引，格式为`range_name@domain/index`，若匹配的 HGTX range 不存在 domain，则`@domain`可省略，否则`@domain`需要指定。

默认 asys 将使用匹配的第一个 HGTX range 作为统计的时间范围，此时`/index`部分可省略，若需要指定匹配索引，则通过`/index`指定，索引从 0 开始。

例如：使用名称为`self_attention`的 HGTX range 指定统计时间范围，无 domain，使用首个匹配的 HGTX range 的时间范围。

```bash
asys compare --filter-hgtx self_attention report1.asysrep report2.asysrep
```

例如：使用名称为`pcclGroupEnd`的 HGTX range 指定统计时间范围，domain 为`NCCL`，使用第 9 个匹配的 HGTX range 的时间范围（索引为 8）。

```bash
asys compare --filter-hgtx "pcclGroupEnd@NCCL/8" report1.asysrep report2.asysrep
```

##### 5.3.2.2. 指定报告输出文件
`asys compare`将输出精简的比较结果到控制台，并输出详细的比较结果到 csv 文件。

通过`--output`选项可指定输出文件名称的前缀，指定的名称为`文件输出的目录`和`文件名前缀`的组合，格式为`<output_dir>/<prefix>`。前缀可以为空，路径最后一个`/`之前的路径被认为是输出目录。若未通过`--output`指定，asys 将会根据 asysrep 报告文件名和统计报告类型生成文件名称。

例如：指定`--output /test/mytest`，在目录`/test`生成各类对比报告，例如`mytest_ppu_operator_summary_compare.csv`、`mytest_ppu_kernel_summary_compare`等：

```bash
asys compare -f true --output /test/mytest report1.asysrep report2.asysrep
```

+ `-f true`：允许输出的比较结果文件覆盖已存在的文件
+ `--output /test/mytest`：在`/test`目录生成对比报告，报告文件名称前缀`mytest`

##### 5.3.2.3. 指定算子识别规则
`asys compare`的对比结果中包含 PPU 算子相关对比，通过内置的 PPU 算子识别规则识别报告中的算子并比较相关性能，可通过`--ppu-op-config`选项自定义算子识别规则，可指定正则表达式通过匹配 HGTX range 名称或者 kernel 名称识别指定算子类型，格式为`算子类型=匹配类型：过滤规则`，可多次通过`--ppu-op-config`选项创建多个算子识别规则，例如：

```bash
asys compare --ppu-op-config GEMM=kernel:gemv --ppu-op-config Pytorch=hgtx:aten report1.asysrep report2.asysrep
```

+ `--ppu-op-config GEMM=kernel:gemv`：匹配 kernel 名称包含`gemv`关键字的 kernel，分类到`GEMM`算子类型
+ `--ppu-op-config Pytorch=hgtx:aten`：匹配 HGTX range 名称包含`aten`关键字，HGTX range 关联的 PPU 活动分类到`PyTorch`算子类型

#### 5.3.3. 报告比较规则

##### 5.3.3.1. PPU kernel 汇总比较
比较两个 asysrep 报告中的 PPU kernel 汇总结果，匹配和比较两个报告中的 PPU kernel 耗时差异。

依赖的 asys 采集选项：

+ `--trace hggc`

**统计规则**

对每个 asysrep 报告，计算`HGGC PPU kernel汇总`，按照`每HGGC kernel名称`进行统计。通过`HGGC kernel名称`匹配两个 asysrep 汇总结果的 kernel 信息，按照每个报告的 HGGC kernel 总耗时降序输出。`HGGC kernel名称`取决于 base / mangled 选项是否设置，默认为 demangle 后 kernel 名称（包含函数参数列表）。

`ppu_kernel_summary_compare`表格列说明如下，比较结果通过`/`分隔，未匹配的列通过`-`表示：

```text
Row# : Row number of the compare result
Device Name : PPU Device name
Instances : Number of calls to this kernel
Percent [%] : Percentage of 'Total' time
Avg [ns] : Average execution time of this kernel
Avg Ratio : Target average execution time compared to base
Total [ns] : Total time used by all executions of this kernel
Total Ratio : Target total execution time compared to base
Base Kernel : Name of the kernel in base report
Target Kernel : Name of the kernel in target report
```

**命令行使用方法**

使用 asys stats 传入两个 asysrep 报告进行比较：

```bash
asys stats -r ppu_kernel_summary_compare base_report.asysrep target_report.asysrep
```

可通过`asys stats --help-report ppu_kernel_summary_compare`查看具体帮助信息，支持的选项列举如下：

+ hgtx-name：kernel 名字前通过/拼接最接近 kernel launch 的 HGTX range 名称
+ base：使用 kernel 的短名称（仅函数名，不包含参数）进行统计和输出
+ mangled：使用 kernel 的 mangled 名称进行统计和输出
+ device：指定统计的 PPU device ID 列表，多个 PPU device ID 之间通过`/`分割。若不指定，默认统计所有 PPU device

报告结果示例如下：

```text
Row#,Device Name,Instances,Percent (%),Avg (ns),Avg Ratio,Total (ns),Total Ratio,Base Kernel,Target Kernel,
1,"ZW-M890P / PPU-ZW810E","3781 / 4016","1.9 / 0.4","13806 / 7021",2.0,"52200644 / 28196837",1.9,"void vllm::act_and_mul_kernel<c10::BFloat16, &(c10::BFloat16 vllm::silu_kernel<c10::BFloat16>(c10::BFloat16 const&)), true>(c10::BFloat16*, c10::BFloat16 const*, int)","void vllm::act_and_mul_kernel<c10::BFloat16, &(c10::BFloat16 vllm::silu_kernel<c10::BFloat16>(c10::BFloat16 const&)), true>(c10::BFloat16*, c10::BFloat16 const*, int)",
2,"ZW-M890P / PPU-ZW810E","78 / 83","1.2 / 0.3","425945 / 276146",1.5,"33223717 / 22920188",1.4,"void at::native::(anonymous namespace)::cunn_SoftMaxForward<4, float, float, float, at::native::(anonymous namespace)::SoftMaxForwardEpilogue>(float*, float const*, int)","void at::native::(anonymous namespace)::cunn_SoftMaxForward<4, float, float, float, at::native::(anonymous namespace)::SoftMaxForwardEpilogue>(float*, float const*, int)",
...
```

**GUI 使用指南**

+ 规则设置（Settings）
    - Kernel Name Mode：Kernel Name 的展示模式。包括三种模式：
        * Base：导出 kernel 的短名称（仅函数名，不包含参数）
        * Mangled：导出 kernel 的 mangled 名称
        * Demangled：导出 kernel 的 demangle 之后的名称（默认值）
    - PPU Devices：PPU device 过滤器，统计结果按照所选的 PPU device 进行过滤，默认值为“All”，统计所有 PPU devices 的数据，此项不能为空。
    - Show top N results：展示前 N 条结果，默认为“-1”，即不限制展示结果条数。在报告对比时，会展示两个报告各自的前 N 条结果。
    - Add HGTX name as a prefix：使能名字前拼接最接近 kernel launch 的 HGTX 名称，通过`/`间隔。默认不勾选。
    - Show matched kernels only：使能后仅展示 base 和 target 报告中都包含的成功匹配 kernels，即会隐藏所有包含无效结果“-”的行。默认不使能。

##### 5.3.3.2. HGTX 向 PPU 投影汇总比较
比较两个 asysrep 报告中的 HGTX range 向 PPU 侧投影的汇总结果，匹配和比较两个报告中的 HGTX range PPU 投影汇总的执行时间差异。

依赖的 asys 采集选项：

+ `--trace hgtx,hggc`

**统计规则**

对每个 asysrep 报告，计算`HGTX向PPU投影汇总`，每个 HGTX range 判断关联的 PPU 活动的原则为：

+ CPU 侧的 HGTX range 覆盖了 PPU 活动对应的 HGGC API
+ CPU 侧的 HGTX range 覆盖了 PPU 活动所在 HGGC graph node 的创建 API

HGTX range 在 PPU 侧的投影时间，从本 HGTX 关联的最早的 PPU 活动开始，到最晚的 PPU 活动结束。

HGTX range 在 PPU 侧的总的活跃时间`Proj Active Time`计算方式为：指定的时间点存在一个或者更多 HGTX range 投影，则记为活跃时间。如果多个 HGTX range 的投影在时间上重叠，重叠的部分不会被多次计入活跃时间。

HGTX range 投影的 PPU 侧占比`In-Use`计算方式为：`Proj Active Time`/ `PPU侧统计时间范围`，其中`PPU侧统计时间范围`计算方式取决于`range-mode`选项。

对每个 asysrep 报告，按照`相同HGTX range`汇总 PPU 侧的投影时间信息。通过`HGTX range`匹配两个 asysrep 汇总结果的投影信息，按照每个报告的`In-Use`降序排列。

`hgtx_ppu_projection_summary_compare`表格列说明如下，比较结果通过`/`分隔，未匹配的列通过`-`表示：

```text
Row# : Row number of the compare result
Device Name : PPU Device name
In-Use [%] : Percentage of projected active time to time range
Range Instance : Number of instances of this range
Proj Avg [ns] : Average projected time for this range
Proj Avg Ratio : Target average projected time compared to base
Proj Active Time [ns] : Total projected time excluding overlapping for this range name
Proj Active Ratio : Target total projected time excluding overlapping compared to base
Total Proj Time [ns] : Total projected time used by all instances of this range name
Total Proj Ratio : Target total projected time compared to base
Total Range Time [ns] : Total original HGTX range time used by all instances of this range name
Total Range Ratio : Target total original HGTX range time compared to base
Base Range : Name of the HGTX range in base report
Target Range : Name of the HGTX range in target report
```

**命令行使用方法**

使用 asys stats 传入两个 asysrep 报告进行比较：

```bash
asys stats -r hgtx_ppu_projection_summary_compare base_report.asysrep target_report.asysrep
```

可通过`asys stats --help-report hgtx_ppu_projection_summary_compare`查看具体帮助信息，支持的选项列举如下：

+ `device=<device_list>`：指定统计的 PPU device ID 列表，多个 PPU device ID 之间通过`/`分割。若不指定，默认统计所有 PPU device
+ `range-mode=<mode>`：PPU 侧统计时间范围的选择模式，支持 active 和 full 模式
    - active：默认模式，时间范围从第一个 PPU 活动开始，到最后一个 PPU 活动结束截止
    - full：时间范围选取为用户指定的统计时间范围，若没有指定统计时间范围，则统计报告整体的时间范围
+ `range-include=<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式白名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ `range-exclude=<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式黑名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ `no-graph-mapping`：导出结果不包含通过 HGGC graph node 映射的 HGTX range 信息

报告结果示例如下：

```text
Row#,Device Name,In-Use (%),Range Instance,Proj Avg (ns),Proj Avg Ratio,Proj Active Time (ns),Proj Active Ratio,Total Proj Time (ns),Total Proj Ratio,Total Range Time (ns),Total Range Ratio,Base Range,Target Range,
1,"PPU-ZW810 / PPU-ZW610","24.7 / 19.4","1 / 1","107599873 / 61168391",0.6,"107599873 / 61168391",0.6,"107599873 / 61168391",0.6,"108253331 / 62298650",0.6,"[prof_range]: iter 7","[prof_range]: iter 7",
2,"PPU-ZW810 / PPU-ZW610","3.0 / 4.6","4 / 5","3307076 / 2890162",0.9,"13228306 / 14450814",1.1,"13228306 / 14450814",1.1,"4966272 / 1315786",0.3,"DALI:[DALI][Executor] RunMixed","DALI:[DALI][Executor] RunMixed",
...
```

**GUI 使用指南**

+ 规则设置（Settings）
    - PPU Devices：PPU device 过滤器，统计结果按照所选的 PPU device 进行过滤，默认值为“All”，统计所有 PPU devices 的数据，此项不能为空。
    - Time Range Mode：设置统计时间范围的模式
        * `PPU Active Time Range`：默认模式，时间范围从第一个 PPU 活动开始，到最后一个 PPU 活动结束截止
        * `Filtered Time Range`：时间范围选取为用户指定的统计时间范围，若没有指定统计时间范围，则统计报告整体的时间范围
    - HGTX graph node mapping：是否投影 HGGC graph capture 阶段 HGTX 到 PPU 侧（通过在 HGTX range 范围内创建的 HGGC graph node 建立与 PPU 侧的关联）。默认值为“Yes”。
    - Range Name Filter：对结果中的 HGTX range name 进行过滤，采用（Perl 兼容的）正则表达式匹配的方式，默认显示所有 HGTX range。带有正则表达式语法检查，当输入的正则表达式语法错误时，出现错误提示并且不允许保存设置。
    - Show matched only：使能后仅展示 base 和 target 报告中都包含的成功匹配结果，即会隐藏所有包含无效结果“-”的行。默认不使能。

##### 5.3.3.3. PPU 算子汇总比较
比较两个 asysrep 报告中的 PPU 算子汇总结果，匹配和比较两个报告中的 PPU 算子执行时间差异。

依赖的 asys 采集选项：

+ `--trace hggc,hgtx`

**注意：**
在采集 asysrep 报告前，建议使能 PPU 算子 HGTX range 标注相关功能：
+ 执行`export PPU_LIB_PERF_INSTRUMENT=1`配置环境变量，使能基础框架 PPU 算子 HGTX range 标注功能
+ asys 添加选项`--pytorch autograd-shapes-hgtx`，使能 PyTorch 算子 HGTX range 标注功能

**统计规则**

对每个 asysrep 报告，计算`PPU算子汇总`，汇总统计 PPU 算子的执行时间，PPU 算子的执行时间统计方式为：

+ 每个 PPU 算子在 PPU 侧的执行时间为：本算子关联的 PPU 侧第一个活动开始，到最后一个活动结束的持续时间

PPU 算子的 PPU 活跃时间`PPU Active Time`计算方式为：

+ 指定的时间点存在一个或者多个本 PPU 算子关联的 PPU 活动，则记为活跃时间。如果多个 PPU 活动在时间上重叠，重叠的部分不会被多次计入活跃时间

PPU 算子的执行信息汇总时，若两个 PPU 算子之间大部分参数相同，仅少量对性能影响较小的参数存在差异，默认会忽略参数差异，按照相同的 PPU 算子合并汇总。

通过 PPU 算子类型和 PPU 算子参数匹配两个 asysrep 报告的算子汇总结果，按照每个报告的算子占比降序输出。

`ppu_operator_summary_compare`表格列说明如下，比较结果通过`/`分隔，未匹配的列通过`-`表示：

```text
Row# : Row number of the compare result
Device Name : PPU Device name
OP Type : PPU operator type
Percent [%] : Percentage of 'Total Time'
Instances : Number of this PPU operator
Avg [ns] : Average execution time of this operator's kernel
Avg Ratio : Target average time compared to base
Total [ns] : Total time used by all kernel instances of this operator
Total Ratio : Target total time compared to base
Active [ns] : Total PPU active time excluding overlapping for this operator
Active Ratio : Target active time compared to base
Compute Util [%] : Utilization ratio of PPU compute capability
HBM Load Util [%] : Utilization ratio of PPU HBM load bandwidth
HBM Store Util [%] : Utilization ratio of PPU HBM store bandwidth
Base OP Name : Name of the PPU operator in base report
Target OP Name : Name of the PPU operator in target report
```

**命令行使用方法**

使用 asys stats 传入两个 asysrep 报告进行比较：

```bash
asys stats -r ppu_operator_summary_compare base_report.asysrep target_report.asysrep
```

可通过`asys stats --help-report ppu_operator_summary_compare`查看具体帮助信息，支持的选项列举如下：

+ top=`<limit>`：仅比较每个报告 top N 占比的算子
+ device=`<device_list>`：指定统计的 PPU device ID 列表，多个 PPU device ID 之间通过`/`分割。若不指定，默认统计所有 PPU device
+ range-include=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式白名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ range-exclude=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式黑名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ op=`<operator_filter>`：指定参与统计的 PPU 算子类型列表，多个 PPU 算子类型之间通过`/`分割。若不指定，默认统计所有支持的 PPU 算子类型。若指定`others`类型，未关联到 PPU 算子的 kernel 也将在统计结果中体现
+ order-by=`<order_type>`：指定输出结果排序方式，默认按照算子时间占比排序
+ no-graph-mapping：若指定，不再映射 HGGC graph 创建阶段的 HGTX 到 HGGC graph 执行阶段
+ no-merge-flash-attention-prefill-decode-operator：若指定，不再匹配和合并 prefill 和 decode 的 flash attention 算子
+ no-merge-flash-attention-parameter：若指定，不再忽略 flash attention 算子对性能影响较小的参数差异
+ no-merge-communication-parameter：若指定，不再忽略通信算子对性能影响较小的参数差异
+ no-merge-moe-parameter：若指定，不再忽略 MoE 算子对性能影响较小的参数差异
+ no-merge-pytorch-parameter：若指定，不再忽略 PyTorch 算子对性能影响较小的参数差异
+ no-merge-gemm-parameter：若指定，不再忽略 GEMM 算子对性能影响较小的参数差异

通过`--ppu-op-config`选项自定义算子识别规则，可指定正则表达式通过匹配 HGTX range 名称或者 kernel 名称识别指定算子类型，格式为`算子类型=匹配类型：过滤规则`，可多次通过`--ppu-op-config`选项创建多个算子识别规则，例如：

```bash
--ppu-op-config GEMM=kernel:gemv --ppu-op-config Pytorch=hgtx:aten
```

+ `--ppu-op-config GEMM=kernel:gemv`：匹配 kernel 名称包含`gemv`关键字的 kernel，分类到`GEMM`算子类型
+ `--ppu-op-config Pytorch=hgtx:aten`：匹配 HGTX range 名称包含`aten`关键字，HGTX range 关联的 PPU 活动分类到`PyTorch`算子类型

报告结果示例如下：

```text
Row#,Device Name,OP Type,Percent (%),Instances,Avg (ns),Avg Ratio,Total (ns),Total Ratio,Active (ns),Active Ratio,Compute Util (%),HBM Load Util (%),HBM Store Util (%),Base OP Name,Target OP Name,
1,"ZW-M890P / PPU-ZW810E","GEMM","2.1 / 0.5","3396 / 3632","17988 / 9057",2.0,"61089747 / 32897426",1.9,"60114246 / 32328985",1.9,"1.3 / 8.0","2.7 / 5.2","0.0 / 0.0","ACBLAS:GemmEx,t,n,128,192,2048,2048,2048,128,1,0,1,DEFAULT,BF16,ACBLAS_GEMM_DEFAULT_TENSOR_OP,32F,EPILOGUE_DEFAULT","ACBLAS:GemmEx,t,n,128,192,2048,2048,2048,128,1,0,1,DEFAULT,BF16,ACBLAS_GEMM_DEFAULT_TENSOR_OP,32F,EPILOGUE_DEFAULT",
2,"ZW-M890P / PPU-ZW810E","PCCL","1.1 / 0.3","194 / 194","160435 / 109407",1.5,"31124497 / 21225020",1.5,"31124497 / 21225020",1.5,"- / -","- / -","- / -","AllReduce, p:0, c:2347008, d:9, r:1, w:2, h:7dda1c67c65a5e44, t:1, b:0x469000000/0x46947a000","AllReduce, p:0, c:2347008, d:9, r:1, w:2, h:b2268f5abee7947e, t:1, b:0x497800000/0x497c7a000",
...
```

**GUI 使用指南**

+ 规则设置（Settings）
    - PPU Devices：PPU device 过滤器，统计结果按照所选的 PPU device 进行过滤，默认值为“All”，统计所有 PPU devices 的数据，此项不能为空。
    - Merge operator parameters：忽略对算子对性能影响较小的参数差异，将其合并统计。默认对所有类型的算子都启用。
    - HGTX graph node mapping：是否投影 HGGC graph capture 阶段 HGTX 到 PPU 侧（通过在 HGTX range 范围内创建的 HGGC graph node 建立与 PPU 侧的关联）。默认值为“Yes”。
    - Range Name Filter：对结果中的 HGTX range name 进行过滤，采用（Perl 兼容的）正则表达式匹配的方式，默认显示所有 HGTX range。带有正则表达式语法检查，当输入的正则表达式语法错误时，出现错误提示并且不允许保存设置。
    - Show top N results：展示前 N 条结果，默认为“-1”，即不限制展示结果条数。在报告对比时，会展示两个报告各自的前 N 条结果。
    - Parse from：选择解析算子的来源，所有 ppu 活动都只能通过使能的算子解析来源尝试进行解析，若解析成功则会纳入算子统计的结果中。默认值为“ALL”，从所有支持的解析来源对 ppu 活动进行解析，此项不能为空。
    - Show matched only：使能后仅展示 base 和 target 报告中都包含的成功匹配结果，即会隐藏所有包含无效结果“-”的行。默认不使能。
    - Custom operator parse config：自定义算子解析规则，使能后可以自行添加算子解析规则，通过 kernel 名或 HGTX 名+正则表达式匹配，解析出自定义的算子类型。该自定义解析规则优先级高于上面的“Parse from”选项。默认为空。

##### 5.3.3.4. PPU 算子类型汇总比较
比较两个 asysrep 报告中的 PPU 算子类型汇总结果，匹配和比较两个报告中的 PPU 算子类型的执行时间差异。

依赖的 asys 采集选项：

+ `--trace hggc,hgtx`

**注意：**
在采集 asysrep 报告前，建议使能 PPU 算子 HGTX range 标注相关功能：
+ 执行`export PPU_LIB_PERF_INSTRUMENT=1`配置环境变量，使能基础框架 PPU 算子 HGTX range 标注功能
+ asys 添加选项`--pytorch autograd-shapes-hgtx`，使能 PyTorch 算子 HGTX range 标注功能

**统计规则**

对每个 asysrep 报告，计算`PPU算子类型汇总`，汇总统计 PPU 算子的执行时间，PPU 算子的执行时间统计方式为：

+ 每个 PPU 算子在 PPU 侧的执行时间为：本算子关联的 PPU 侧第一个活动开始，到最后一个活动结束的持续时间

PPU 算子的 PPU 活跃时间`PPU Active Time`计算方式为：

+ 指定的时间点存在一个或者多个本 PPU 算子关联的 PPU 活动，则记为活跃时间。如果多个 PPU 活动在时间上重叠，重叠的部分不会被多次计入活跃时间

通过 PPU 算子类型匹配两个 asysrep 报告的算子类型汇总结果，按照每个报告的算子类型占比降序排列。固定生成`Summary`类型的汇总行，汇总比较两个报告所有 PPU 算子类型的执行时间信息和热点算子。

`ppu_operator_type_summary_compare`表格列说明如下，比较结果通过`/`分隔，未匹配的列通过`-`表示：

```text
Row# : Row number of the compare result
Device Name : PPU Device name
OP Type : PPU operator type
Percent [%] : Percentage of 'Total Time'
Instances : Number of this PPU operator
Avg [ns] : Average duration of this operator type
Avg Ratio : Target average duration compared to base
Total [ns] : Total duration used by all instances of this operator type
Total Ratio : Target total time compared to base
PPU Active Time [ns] : Total PPU active time excluding overlapping for this operator type
Active Time Ratio : Target PPU active time compared to base
Top OP Percent [%] : Percentage of top PPU operator of 'Total Time'
Base Top OP Name : Name of the top PPU operator of this type in base report
Target Top OP Name : Name of the top PPU operator of this type in target report
```

**命令行使用方法**

使用 asys stats 传入两个 asysrep 报告进行比较：

```bash
asys stats -r ppu_operator_type_summary_compare base_report.asysrep target_report.asysrep
```

可通过`asys stats --help-report ppu_operator_type_summary_compare`查看具体帮助信息，支持的选项列举如下：

+ device=`<device_list>`：指定统计的 PPU device ID 列表，多个 PPU device ID 之间通过`/`分割。若不指定，默认统计所有 PPU device
+ range-include=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式白名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ range-exclude=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式黑名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ op=`<operator_filter>`：指定参与统计的 PPU 算子类型列表，多个 PPU 算子类型之间通过`/`分割。若不指定，默认统计所有支持的 PPU 算子类型。若指定`others`类型，未关联到 PPU 算子的 kernel 也将在统计结果中体现
+ no-graph-mapping：若指定，不再映射 HGGC graph 创建阶段的 HGTX 到 HGGC graph 执行阶段
+ no-merge-flash-attention-prefill-decode-operator：若指定，不再匹配和合并 prefill 和 decode 的 flash attention 算子
+ no-merge-flash-attention-parameter：若指定，不再忽略 flash attention 算子对性能影响较小的参数差异
+ no-merge-communication-parameter：若指定，不再忽略通信算子对性能影响较小的参数差异
+ no-merge-moe-parameter：若指定，不再忽略 MoE 算子对性能影响较小的参数差异
+ no-merge-pytorch-parameter：若指定，不再忽略 PyTorch 算子对性能影响较小的参数差异
+ no-merge-gemm-parameter：若指定，不再忽略 GEMM 算子对性能影响较小的参数差异

可通过`--ppu-op-config`选项自定义算子识别规则，可指定正则表达式通过匹配 HGTX range 名称或者 kernel 名称识别指定算子类型，格式为`算子类型=匹配类型：过滤规则`，可多次通过`--ppu-op-config`选项创建多个算子识别规则，例如：

```bash
--ppu-op-config GEMM=kernel:gemv --ppu-op-config Pytorch=hgtx:aten
```

+ `--ppu-op-config GEMM=kernel:gemv`：匹配 kernel 名称包含`gemv`关键字的 kernel，分类到`GEMM`算子类型
+ `--ppu-op-config Pytorch=hgtx:aten`：匹配 HGTX range 名称包含`aten`关键字，HGTX range 关联的 PPU 活动分类到`PyTorch`算子类型

报告结果示例如下：

```text
Row#,Device Name,OP Type,Percent (%),Instances,Avg (ns),Avg Ratio,Total (ns),Total Ratio,PPU Active Time (ns),Active Time Ratio,Top OP Percent (%),Base Top OP Name,Target Top OP Name,
1,"ZW-M890P / PPU-ZW810E","Summary","100.0 / 100.0","84653 / 106815","33908 / 67216",2.0,"2870439050 / 7179687391",2.5,"2802370718 / 7178423429",2.6,"29.6 / 47.3","MoE:M_192_E128_H2048_In768_topk8","void marlin_moe_wna16::Marlin<__nv_bfloat16, 2814749767172868l, 1125899906909960l, 256, 1, 8, 8, false, 4, 8, false>(int4 const*, int4 const*, int4*, int4*, int4 const*, int4 const*, unsigned short const*, int4 const*, int const*, int const*, int const*, int const*, float const*, int, bool, bool, int, int, int, int, int*, bool, bool, bool, int)",
2,"ZW-M890P / PPU-ZW810E","MoE","41.6 / 65.8","7559 / 20081","157975 / 235204",1.5,"1194135831 / 4723135684",4.0,"1128253823 / 4723135684",4.2,"29.6 / 47.3","MoE:M_192_E128_H2048_In768_topk8","void marlin_moe_wna16::Marlin<__nv_bfloat16, 2814749767172868l, 1125899906909960l, 256, 1, 8, 8, false, 4, 8, false>(int4 const*, int4 const*, int4*, int4*, int4 const*, int4 const*, unsigned short const*, int4 const*, int const*, int const*, int const*, int const*, float const*, int, bool, bool, int, int, int, int, int*, bool, bool, bool, int)",
...
```

**GUI 使用指南**

+ 规则设置（Settings）
    - PPU Devices：PPU device 过滤器，统计结果按照所选的 PPU device 进行过滤，默认值为“All”，统计所有 PPU devices 的数据，此项不能为空。
    - Merge operator parameters：忽略对算子对性能影响较小的参数差异，将其合并统计。默认对所有类型的算子都启用。
    - Range Name Filter：对结果中的 HGTX range name 进行过滤，采用（Perl 兼容的）正则表达式匹配的方式，默认显示所有 HGTX range。带有正则表达式语法检查，当输入的正则表达式语法错误时，出现错误提示并且不允许保存设置。
    - Parse from：选择解析算子的来源，所有 ppu 活动都只能通过使能的算子解析来源尝试进行解析，若解析成功则会纳入算子统计的结果中。默认值为“ALL”，从所有支持的解析来源对 ppu 活动进行解析，此项不能为空。
    - Show matched only：使能后仅展示 base 和 target 报告中都包含的成功匹配结果，即会隐藏所有包含无效结果“-”的行。默认不使能。
    - Custom operator parse config：自定义算子解析规则，使能后可以自行添加算子解析规则，通过 kernel 名或 HGTX 名+正则表达式匹配，解析出自定义的算子类型。该自定义解析规则优先级高于上面的“Parse from”选项。默认为空。

##### 5.3.3.5. PCCL 不同步汇总比较
比较两个 asysrep 报告中的 PCCL 不同步汇总结果，匹配和比较两个报告中的 PCCL kernel 通信组的不同步占比。

依赖的 asys 采集选项：

+ `--trace hggc`

**统计规则**

对每个 asysrep 报告，计算`PCCL不同步汇总`，将执行时间上存在重叠的 PCCL kernel 分入一个通信组，对每个通信组的所有 kernel 计算如下时间：

+ `重叠时间`：本通信组内所有 PCCL kernel 重叠的时间
+ `持续时间`：从本通信组第一个 kernel 开始执行到最后一个 kernel 停止执行的时间

不同步比例计算方式为：(`持续时间` - `重叠时间`) / `持续时间`。

`Desync P90`列的计算方法为：将`相同kernel名称`的通信组统计结果根据不同步率升序排列，获取第 90 百分位的不同步率，本数值表示大部分 PCCL 通信不同步率优于此结果。

通过 kernel 名称匹配两个 asysrep 报告的汇总结果，按照每个报告的通信组耗时占比降序输出。

`pccl_desync_summary_compare`表格列说明如下，比较结果通过`/`分隔，未匹配的列通过`-`表示：

```text
Row# : Row number of the compare result
Device Name : PPU Device name
Time [%] : Percentage of 'Total Duration'
Count : Number of communication of this PCCL kernel
Desync P90 [%] : 90th percentile desynchronization rate of this PCCL kernel
Desync Avg [%] : Average desynchronization rate of this PCCL kernel
Total Duration [ns] : Total elapsed duration of all communication of this PCCL kernel
Total Overlap [ns] : Total overlap duration of all communication of this PCCL kernel
Base Kernel : Name of the kernel in base report
Target Kernel : Name of the kernel in target report
```

**命令行使用方法**

使用 asys stats 传入两个 asysrep 报告进行比较：

```bash
asys stats -r pccl_desync_summary_compare base_report.asysrep target_report.asysrep
```

可通过`asys stats --help-report pccl_desync_summary_compare`查看具体帮助信息，支持的选项列举如下：

+ hgtx-name：kernel 名字前通过`/`拼接最接近 kernel launch 的 HGTX range 名称
+ base：使用 kernel 的短名称（仅函数名，不包含参数）进行统计和输出
+ mangled：使用 kernel 的 mangled 名称进行统计和输出
+ device：指定统计的 PPU device ID 列表，多个 PPU device ID 之间通过`/`分割。若不指定，默认统计所有 PPU device

报告结果示例如下：

```text
Row#,Device Name,Time (%),Count,Desync P90 (%),Desync Avg (%),Total Duration (ns),Total Overlap (ns),Base Kernel,Target Kernel,
1,"ZW-M890P / PPU-ZW810E","48.5 / 59.3","3294 / 3592","30.4 / 42.1","14.0 / 21.8","79985018 / 83745513","65187134 / 57385652","void pcclKernel_oneShotAllReduceKernel<__ppu_bfloat16, 2, 0, 1, 1>(oneShotDevParams)","void pcclKernel_oneShotAllReduceKernel<__ppu_bfloat16, 2, 0, 1, 1>(oneShotDevParams)",
2,"ZW-M890P / PPU-ZW810E","42.0 / 29.0","381 / 388","75.0 / 30.5","48.1 / 15.7","69295561 / 40951632","30304259 / 27014248","void pcclKernel_twoShotAllReduceKernel<__ppu_bfloat16, 2, 0, 0, 1, 1>(twoShotDevParams)","void pcclKernel_twoShotAllReduceKernel<__ppu_bfloat16, 2, 0, 0, 1, 1>(twoShotDevParams)",
...
```

**GUI 使用指南**

- Kernel Name Mode：Kernel Name 的展示模式。包括三种模式：
    * Base：导出 kernel 的短名称（仅函数名，不包含参数）
    * Mangled：导出 kernel 的 mangled 名称
    * Demangled：导出 kernel 的 demangle 之后的名称（默认值）
- PPU Devices：PPU device 过滤器，统计结果按照所选的 PPU device 进行过滤，默认值为“All”，统计所有 PPU devices 的数据，此项不能为空。
- Add HGTX name as a prefix：使能名字前拼接最接近 kernel launch 的 HGTX 名称，通过`/`间隔。默认不勾选。
- Show matched only：使能后仅展示 base 和 target 报告中都包含的成功匹配结果，即会隐藏所有包含无效结果“-”的行。默认不使能。

##### 5.3.3.6. PPU 时间利用率比较
比较两个 asysrep 报告中的 PPU 时间利用率汇总结果，匹配和比较两个报告中的 PPU 在时间利用率的差异。

依赖的 asys 采集选项：

+ `--trace hggc`

**统计规则**

对每个 asysrep 报告，计算 PPU 的时间利用率，统计在指定的时间范围内 PPU 存在操作的时间。

时间范围的选择：

+ 如果选择了“PPU Active Time Range”模式，则统计的时间范围从该设备上的第一个 PPU 操作开始，到该设备上的最后一个 PPU 操作结束
+ 如果选择了“Filtered Time Range”范围模式，则时间范围与指定的过滤时间范围相同

请注意，利用率是指“时间”利用率，而不是“资源”利用率，PPU 设备在指定时间存在操作，即认为 PPU 此刻的时间利用率为 100%。如果多个操作在同时运行，对应的时间利用率也不会超过 100%。

对于每个 PPU 设备，PPU 在时间范围的时间利用率为：`繁忙时间`/`时间段长度`。两个报告的统计结果根据 PPU 设备索引匹配和对比，对比结果按照每个报告的 PPU 时间利用率降序排列。

`ppu_time_util_compare`表格列说明如下，比较结果通过`/`分隔，未匹配的列通过`-`表示：

```text
Row# : Row number of the compare result
Device Name : PPU Device name
In-Use [%] : Percentage of time the PPU is being used
Duration [ns] : Duration of the time range
PPU Active Time [ns] : PPU active time excluding overlapping
Active Time Ratio : Target PPU active time compared to base
Base Device ID : PPU device identifier in base report
Target Device ID : PPU device identifier in target report
```

**命令行使用方法**

使用 asys stats 传入两个 asysrep 报告进行比较：

```bash
asys stats -r ppu_time_util_compare base_report.asysrep target_report.asysrep
```

可通过`asys stats --help-report ppu_time_util_compare`查看具体帮助信息，支持的选项列举如下：

+ `range-mode=<mode>`：统计时间范围的选择模式，支持`active`和`full`模式：
    - `active`：默认模式，时间范围从第一个 PPU 活动开始，到最后一个 PPU 活动结束截止
    - `full`：时间范围选取为用户指定的统计时间范围，若没有指定统计时间范围，则统计报告整体的时间范围

报告结果示例如下：

```text
Row#,Device Name,In-Use (%),Duration (ns),PPU Active Time (ns),Base Device ID,Target Device ID,
1,"ZW-M890P / PPU-ZW810E","77.1 / 91.3","1781485096 / 3874625379","1373679518 / 3538770219",1,1,
2,"ZW-M890P / PPU-ZW810E","76.2 / 91.2","1885995849 / 4001152909","1437072950 / 3650124332",0,0,
```

**GUI 使用指南**

+ 规则设置（Settings）
    - Time Range Mode：设置统计时间范围的模式
        * `PPU Active Time Range`：默认模式，时间范围从第一个 PPU 活动开始，到最后一个 PPU 活动结束截止
        * `Filtered Time Range`：时间范围选取为用户指定的统计时间范围，若没有指定统计时间范围，则统计报告整体的时间范围
    - Show matched only：使能后仅展示 base 和 target 报告中都包含的成功匹配结果，即会隐藏所有包含无效结果“-”的行。默认不使能。

##### 5.3.3.7. PPU 算子 kernel 性能分解比较
比较两个 asysrep 报告中的 PPU 算子和 kernel 性能分解结果，匹配和比较两个报告中的性能分解 kernel 层的差异。

依赖的 asys 采集选项：

+ `--trace hggc,hgtx`

**注意：**
在采集 asysrep 报告前，建议使能 PPU 算子 HGTX range 标注相关功能：
+ 执行`export PPU_LIB_PERF_INSTRUMENT=1`配置环境变量，使能基础框架 PPU 算子 HGTX range 标注功能
+ asys 添加选项`--pytorch autograd-shapes-hgtx`，使能 PyTorch 算子 HGTX range 标注功能

**统计规则**

对每个 asysrep 报告，计算`PPU算子kernel性能分解`，识别 asysrep 报告中的 PPU 算子，根据算子的种类和嵌套关系，将算子分为框架层、加速库层和 kernel 层三个层级，获取嵌套的算子逐层细化的性能分解信息。

父一级 PPU 算子范围内，未存在子一级 PPU 算子的时间范围（PPU 设备空闲），被标记为`Idle`。各个层级中缺失的父一级 PPU 算子被标记为`Native`。

通过三个层级的 PPU 算子参数匹配两个 asysrep 报告的 kernel 层性能分解数据，并比较 kernel 层的性能数据。输出结果按照每个报告中的每级算子的占比降序排列。

`ppu_operator_kernel_breakdown_compare`表格列说明如下，比较结果通过`/`分隔，未匹配的列通过`-`表示：

```text
Row# : Row number of the compare result
Device Name : PPU Device name
OP Type : PPU operator type
Base Framework OP : Name of the framework layer operator in base report
Base Framework Time [%] : Framework operator time percentage of 'Total Time' in base report
Base Framework Avg [ns] : Average duration of this framework operator in base report
Base Framework Instances : Number of this framework operator in base report
Base Library OP : Name of the compute library layer operator in base report
Base Library Time [%] : Library operator time percentage of 'Total Time' in base report
Base Library Avg [ns] : Average duration of this library operator in base report
Base Library Instances : Number of this library operator in base report
Base Kernel : Name of the HGGC kernel in base report
Base Kernel Time [%] : HGGC kernel time percentage of 'Total Time' in base report
Base Kernel Avg [ns] : Average duration of this kernel in base report
Base Kernel Instances : Number of this kernel in base report
Target Framework OP : Name of the framework layer operator in target report
Target Framework Time [%] : Framework operator time percentage of 'Total Time' in target report
Target Framework Avg [ns] : Average duration of this framework operator in target report
Target Framework Instances : Number of this framework operator in target report
Target Library OP : Name of the compute library layer operator in target report
Target Library Time [%] : Library operator time percentage of 'Total Time' in target report
Target Library Avg [ns] : Average duration of this library operator in target report
Target Library Instances : Number of this library operator in target report
Target Kernel : Name of the HGGC kernel in target report
Target Kernel Time [%] : HGGC kernel time percentage of 'Total Time' in target report
Target Kernel Avg [ns] : Average duration of this kernel in target report
Target Kernel Instances : Number of this kernel in target report
Avg Ratio : Target kernel average time compared to base
```

**命令行使用方法**

使用 asys stats 传入两个 asysrep 报告进行比较：

```text
asys stats -r ppu_operator_kernel_breakdown_compare base_report.asysrep target_report.asysrep
```

可通过`asys stats --help-report ppu_operator_kernel_breakdown_compare`查看具体帮助信息，支持的选项列举如下：

+ top=`<limit>`：仅比较每个报告 top N 占比的 kernel 层算子，部分占比较小的算子将会被忽略
+ device=`<device_list>`：指定统计的 PPU device ID 列表，多个 PPU device ID 之间通过`/`分割。若不指定，默认统计所有 PPU device
+ range-include=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式白名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ range-exclude=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式黑名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ base：使用 kernel 的短名称（仅函数名，不包含参数）进行统计和输出
+ mangled：使用 kernel 的 mangled 名称进行统计和输出
+ op=`<operator_filter>`：指定参与统计的 PPU 算子类型列表，多个 PPU 算子类型之间通过`/`分割。若不指定，默认统计所有支持的 PPU 算子类型。若指定`others`类型，未关联到 PPU 算子的 kernel 也将在统计结果中体现
+ order-by=`<order_type>`：指定输出结果排序方式，默认按照算子时间占比排序
+ no-merge-flash-attention-prefill-decode-operator：若指定，不再匹配和合并 prefill 和 decode 的 flash attention 算子
+ no-merge-flash-attention-parameter：若指定，不再忽略 flash attention 算子对性能影响较小的参数差异
+ no-merge-communication-parameter：若指定，不再忽略通信算子对性能影响较小的参数差异
+ no-merge-moe-parameter：若指定，不再忽略 MoE 算子对性能影响较小的参数差异
+ no-merge-pytorch-parameter：若指定，不再忽略 PyTorch 算子对性能影响较小的参数差异
+ no-merge-gemm-parameter：若指定，不再忽略 GEMM 算子对性能影响较小的参数差异

可通过`--ppu-op-config`选项自定义算子识别规则，通过 HGTX range 名称匹配到的自定义算子将作为框架层算子统计，通过 kernel 名称匹配到的自定义算子将作为 kernel 层算子统计。

报告结果示例如下（部分列未展示）：

```text
Row#,Device Name,OP Type,Base Framework OP,Base Framework Time (%),Base Library OP,Base Library Time (%),Base Kernel,Base Kernel Time (%),Base Kernel Avg (ns),Base Kernel Instances,Target Framework OP,Target Framework Time (%),Target Library OP,Target Library Time (%),Target Kernel,Target Kernel Time (%),Target Kernel Avg (ns),Target Kernel Instances,Avg Ratio,
1,"PPU-ZW810E","PCCL","sglang::outplace_all_reduce, op_id = 2174848, sizes = [[948, 2048], [], []], input_op_ids = [(2174845,0), (0,-1), (0,-1)]",0.6,"Native",0.6,"void sglang::cross_device_reduce_1stage<__nv_bfloat16, 2>(sglang::RankData*, sglang::RankSignals, sglang::Signal*, __nv_bfloat16*, int, int)",0.6,201675,194,"sglang::outplace_all_reduce, op_id = 1814850, sizes = [[948, 2048], [], []], input_op_ids = [(1814847,0), (0,-1), (0,-1)]",0.9,"Native",0.8,"void sglang::cross_device_reduce_1stage<__nv_bfloat16, 2>(sglang::RankData*, sglang::RankSignals, sglang::Signal*, __nv_bfloat16*, int, int)",0.8,190988,194,0.9,
2,"PPU-ZW810E","MoE","D_MoE,M_4_E_128_H_2048_In_768_topk_8",0.4,"Native",0.1,"_fwd_kernel_ep_scatter_1",0.0,16955,288,"D_MoE,M_4_E_128_H_2048_In_768_topk_8",1.0,"Native",1.0,"-","-","-","-","-",
3,"PPU-ZW810E","MoE","D_MoE,M_4_E_128_H_2048_In_768_topk_8",0.4,"Native",0.1,"void at::native::vectorized_elementwise_kernel<4, at::native::FillFunctor<int>, std::array<char*, 1ul> >(int, at::native::FillFunctor<int>, std::array<char*, 1ul>)",0.0,16955,288,"D_MoE,M_4_E_128_H_2048_In_768_topk_8",1.0,"Native",1.0,"-","-","-","-","-",
...
```

**提示：**
建议使用选项`--format xlsx`输出电子表格，统计结果更加易读。

##### 5.3.3.8. PPU 算子性能分解比较
比较两个 asysrep 报告中的 PPU 算子性能分解结果，匹配和比较两个报告中的性能分解加速库层的差异。

依赖的 asys 采集选项：

+ `--trace hggc,hgtx`

**注意：**
在采集 asysrep 报告前，建议使能 PPU 算子 HGTX range 标注相关功能：
+ 执行`export PPU_LIB_PERF_INSTRUMENT=1`配置环境变量，使能基础框架 PPU 算子 HGTX range 标注功能
+ asys 添加选项`--pytorch autograd-shapes-hgtx`，使能 PyTorch 算子 HGTX range 标注功能

**统计规则**

对每个 asysrep 报告，计算`PPU算子性能分解`，识别 asysrep 报告中的 PPU 算子，根据算子的种类和嵌套关系，将算子分为框架层、加速库层和 kernel 层三个层级，获取加速库层的性能分解信息和硬件利用率信息。

父一级 PPU 算子范围内，未存在子一级 PPU 算子的时间范围（PPU 设备空闲），被标记为`Idle`。各个层级中缺失的父一级 PPU 算子被标记为`Native`。

通过框架层和加速库层的 PPU 算子参数匹配两个 asysrep 报告的加速库层性能分解数据，并比较差异。输出结果按照每个报告中的每级算子的占比降序排列。

`ppu_operator_breakdown_compare`表格列说明如下，比较结果通过`/`分隔，未匹配的列通过`-`表示：

```text
Row# : Row number of the compare result
Device Name : PPU Device name
OP Type : PPU operator type
Base Framework OP : Name of the framework layer operator in base report
Base Framework Time [%] : Framework operator time percentage of 'Total Time' in base report
Base Framework Avg [ns] : Average duration of this framework operator in base report
Base Framework Instances : Number of this framework operator in base report
Base Library OP : Name of the compute library layer operator in base report
Base Library Time [%] : Library operator time percentage of 'Total Time' in base report
Base Library Avg [ns] : Average duration of this library operator in base report
Base Library Instances : Number of this library operator in base report
Base Compute Util [%] : Utilization ratio of PPU compute capability in base report
Base HBM Load Util [%] : Utilization ratio of PPU HBM load bandwidth in base report
Base HBM Store Util [%] : Utilization ratio of PPU HBM store bandwidth in base report
Target Framework OP : Name of the framework layer operator in target report
Target Framework Time [%] : Framework operator time percentage of 'Total Time' in target report
Target Framework Avg [ns] : Average duration of this framework operator in target report
Target Framework Instances : Number of this framework operator in target report
Target Library OP : Name of the compute library layer operator in target report
Target Library Time [%] : Library operator time percentage of 'Total Time' in target report
Target Library Avg [ns] : Average duration of this library operator in target report
Target Library Instances : Number of this library operator in target report
Target Compute Util [%] : Utilization ratio of PPU compute capability in target report
Target HBM Load Util [%] : Utilization ratio of PPU HBM load bandwidth in target report
Target HBM Store Util [%] : Utilization ratio of PPU HBM store bandwidth in target report
Avg Ratio : Target average time compared to base
```

**命令行使用方法**

使用 asys stats 传入两个 asysrep 报告进行比较：

```bash
asys stats -r ppu_operator_breakdown_compare base_report.asysrep target_report.asysrep
```

可通过`asys stats --help-report ppu_operator_breakdown_compare`查看具体帮助信息，支持的选项列举如下：

+ top=`<limit>`：仅比较每个报告 top N 占比的加速库层算子，部分占比较小的算子将会被忽略
+ device=`<device_list>`：指定统计的 PPU device ID 列表，多个 PPU device ID 之间通过`/`分割。若不指定，默认统计所有 PPU device
+ range-include=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式白名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ range-exclude=`<regex_list>`：指定参与统计的 HGTX range 过滤正则表达式黑名单，多个正则表达式之间通过`/`分割。若不指定，默认统计所有 HGTX range
+ op=`<operator_filter>`：指定参与统计的 PPU 算子类型列表，多个 PPU 算子类型之间通过`/`分割。若不指定，默认统计所有支持的 PPU 算子类型。若指定`others`类型，未关联到 PPU 算子的 kernel 也将在统计结果中体现
+ order-by=`<order_type>`：指定输出结果排序方式，默认按照算子时间占比排序
+ no-merge-flash-attention-prefill-decode-operator：若指定，不再匹配和合并 prefill 和 decode 的 flash attention 算子
+ no-merge-flash-attention-parameter：若指定，不再忽略 flash attention 算子对性能影响较小的参数差异
+ no-merge-communication-parameter：若指定，不再忽略通信算子对性能影响较小的参数差异
+ no-merge-moe-parameter：若指定，不再忽略 MoE 算子对性能影响较小的参数差异
+ no-merge-pytorch-parameter：若指定，不再忽略 PyTorch 算子对性能影响较小的参数差异
+ no-merge-gemm-parameter：若指定，不再忽略 GEMM 算子对性能影响较小的参数差异

可通过`--ppu-op-config`选项自定义算子识别规则，通过 HGTX range 名称匹配到的自定义算子将作为框架层算子统计，通过 kernel 名称匹配到的自定义算子将作为 kernel 层算子统计。

报告结果示例如下（部分列未展示）：

```text
Row#,Device Name,OP Type,Base Framework OP,Base Framework Time (%),Base Library OP,Base Library Time (%),Base Library Avg (ns),Base Library Instances,Base Compute Util (%),Base HBM Load Util (%),Base HBM Store Util (%),Target Framework OP,Target Framework Time (%),Target Library OP,Target Library Time (%),Target Library Avg (ns),Target Library Instances,Target Compute Util (%),Target HBM Load Util (%),Target HBM Store Util (%),Avg Ratio,
1,"PPU-ZW810E","MoE","D_MoE,M_8_E_128_H_2048_In_768_topk_8",44.3,"DeepGemm:GroupedNoPad,data_type:bf16,groups:128,m:64,n:768,k:2048,gpu:0",23.3,55495,28128,2.6,262.6,0.0,"D_MoE,M_8_E_128_H_2048_In_768_topk_8",41.9,"-","-","-","-","-","-","-","-",
2,"PPU-ZW810E","MoE","D_MoE,M_8_E_128_H_2048_In_768_topk_8",44.3,"DeepGemm:GroupedNoPad,data_type:bf16,groups:128,m:64,n:2048,k:384,gpu:0",13.0,30975,28128,2.3,235.1,0.0,"D_MoE,M_8_E_128_H_2048_In_768_topk_8",41.9,"-","-","-","-","-","-","-","-",
3,"PPU-ZW810E","MoE","D_MoE,M_8_E_128_H_2048_In_768_topk_8",44.3,"Native",7.3,2482,196896,"-","-","-","D_MoE,M_8_E_128_H_2048_In_768_topk_8",41.9,"Native",40.7,11049,165526,"-","-","-",4.5,
4,"PPU-ZW810E","MoE","D_MoE,M_8_E_128_H_2048_In_768_topk_8",44.3,"Idle",0.7,1681,28128,"-","-","-","D_MoE,M_8_E_128_H_2048_In_768_topk_8",41.9,"Idle",1.2,1992,27647,"-","-","-",1.2,
...
```
**比赛关联：** `asys stats -r ppu_op_sum / ppu_op_type_sum / ppu_op_kernel_breakdown` 直接给出 VLM 推理中 GEMM、FlashAttention 等算子的耗时占比与 PPU 计算/HBM 利用率估算，可用于筛选重点优化算子；`asys compare` 可对比优化前后两份报告，量化每类算子的收益，适合作为比赛报告中的压测取证材料。

<a id="l80Hg"></a>

## 6. asys 命令行采集

Asight Systems 命令行工具 asys，可以在不使用 GUI 工具的情况下对目标应用进行性能分析数据的采集，并输出报告。此报告可以拷贝到其它系统，后续由 GUI 工具进行分析。

asys 主要功能有：

+ **采集跟踪信息**
    - 支持采集 CUDA / cuDNN / cuBLAS / NVTX / OSRT API 执行信息
    - 支持采集 PPU 设备上 Kernel 执行和内存操作信息，支持 CPU 侧和 PPU 侧信息关联
    - 支持采集 PCCL 通信过程执行信息
    - 支持采集 CUDA / OSRT API 调用栈
    - 支持采集 CPU 调度信息，支持采集 CPU 执行时调用栈信息，支持基于调用栈统计函数耗时占比
    - 支持采集 PPU 侧和 CPU 侧内存使用信息
    - 支持采集网卡设备吞吐量等指标
+ **采集过程控制**
    - 支持控制采集时长，支持延迟启动跟踪采集，支持手动打断采集过程
    - 支持通过 NVTX range 指定采集范围
    - 支持通过 CUDA profiler API（cudaProfilerStart/Stop）指定采集范围
    - 支持循环触发跟踪采集，支持指定循环次数
    - 支持自动生成报告名称，支持通过宏组装报告名
    - 支持自定义应用运行环境，可配置应用运行时环境变量，可控制应用打印输出
    - 支持采集 daemon 方式应用程序，可指定等待应用结束方式
    - 支持长时间采集轮转生成报告文件
+ **交互式采集跟踪**
    - 支持分别控制应用启动和跟踪采集（start/stop/launch/shutdown 子命令）
    - 支持应用运行过程中多次启动和停止跟踪采集
    - 支持多个采集过程共存，支持查看采集过程列表
    - 支持附着到已启动的应用中采集跟踪信息（attach 子命令）
+ **支持数据统计分析后处理**
    - 支持设备内存使用分组统计
    - 支持 PPU 时间利用率统计分析

asys 的环境配置请参见[获取 asys 命令行工具](#ZFzMg)。

可以通过 `asys -h` 命令查看帮助。asys 支持多个子命令，用于支持多样化的跟踪采集方式：

```bash
root@0b0f55fa89fd:~# asys -h

usage: asys [--version] [--help] <command> [<args>] [application] [<application args>]

 The most commonly used asys commands are:
        profile       Run an application and capture its profile into a asysrep file.
        attach        Attach to process and capture its profile into a asysrep file.
        launch        Launch an application ready to be profiled.
        start         Start a profiling session.
        stop          Stop a profiling session and capture its profile into a asysrep file.
        cancel        Cancel a profiling session and discard any collected data.
        shutdown      Disconnect launched processes from the profiler and shutdown the profiler.
        sessions      List active sessions.
        status        Provide current status of CLI or the collection environment.
        export        Export asysrep file into another format.
        stats         Generate statistics from an existing asysrep or SQLite file.
        analyze       Identify optimization opportunities in a asysrep file.

 Use 'asys --help <command> ' for more information about a specific command.
```

若希望查看子命令的帮助信息，可通过`asys <sub_command> -h`的方式进行查询，例如查询`profile`子命令的使用帮助，可执行如下命令：

```bash
asys profile -h
```

此外，若希望查看当前安装的 asys 的版本信息，可执行如下命令：

```bash
asys -v
```

### 6.1. 采集跟踪信息
可以通过执行`asys profile`命令，指定跟踪项，运行应用程序，并生成跟踪报告。

`profile`子命令的使用方式为：`asys profile [option] <application> [application args]`

#### 6.1.1. 指定跟踪项
asys 支持通过`--trace`或者`-t`选项指定开启的跟踪类型（跟踪项），多个跟踪项之间通过`,`分隔。 例如：

```bash
asys profile -t hggc,hgtx,acblas -o baseline python test_linear.py
```

+ `-t hggc,hgtx,acblas`指定开启的跟踪项：hggc / hgtx / acblas
+ `-o baseline`指定输出报告名称（不需要指定后缀名）
+ `python test_linear.py`运行应用程序

在应用程序运行结束后，或者输入`Ctrl + C`打断后，asys 会生成对应的跟踪报告（本例中：`baseline.asysrep`），可以在`Asight Systems`中查看报告内容。

<a id="Oz0mt"></a>

### 6.2. 控制采集过程

#### 6.2.1. 采集时间控制
可以通过`--delay`或者`-y`选项指定应用程序启动到开始跟踪采集的时延，可通过`--duration`或者 `-d`选项指定跟踪采集的时长，超时后停止应用，并生成报告，例如：

```bash
asys profile -t hggc --delay 2 --duration 3 python test_linear.py
```

+ `--delay 2`启动应用后，延时 2 秒后开始采集
+ `--duration 3`采集时长 3 秒，超时后停止应用并生成报告

最终采集过程执行流程如下图：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125044138/8ab34a31200b7e174628b2c94582c203/duration_3_1.png)

**注意：**
若希望跟踪采集超时结束后不停止应用，可以用`--kill none `选项。

#### 6.2.2. 限制生成报告文件尺寸
可以通过`--max-report-size`选项指定采集过程生成`asysrep`报告文件的尺寸上限，设置单位为兆字节`MiB`，当跟踪数据生成的报告文件超过此限制后，asys 将停止跟踪采集，例如：

```bash
asys profile -t hggc --max-report-size 10 python test_linear.py
```

+ `--max-report-size 10`限制报告文件最大尺寸为 10 MiB，报告文件超过此大小后停止采集

**注意：**
+ 若同时设置`--max-report-size`报告尺寸限制和`--duration`采集时间限制，任一条件满足时，asys 将停止跟踪采集。
+ 可通过`--max-report-size`选项配合`--trace-rotation`选项，限制轮转报告采集时每个报告文件的尺寸上限。
+ asys 在报告达到`--max-report-size`设置的尺寸后停止采集，采集停止过程可能追加写入跟踪数据，最终生成的报告文件将略大于指定的尺寸上限

#### 6.2.3. 事件触发跟踪采集
可以通过在应用程序插入指定事件的方式来指定采集范围，并在 asys 中指定采集开始和结束的触发事件，以精确控制跟踪抓取范围。

asys 支持两种触发方式，通过 `--capture-range`或者 `-c`选项指定，对应触发事件介绍如下：

| `--capture-range`选项取值 | 触发事件说明 |
| --- | --- |
| hggcProfilerApi | 使用 hggcProfilerStart / cudaProfilerStart 触发开始<br/>使用 hggcProfilerStop / cudaProfilerStop 触发结束 |
| hgtx | 使用 HGTX / NVTX range 触发开始和结束 |
| none | 默认值，不使用事件触发采样 |

举例：使用`hggcProfilerApi`作为事件触发，抓取指定代码范围的跟踪，应用代码中插入事件 API：`cudaProfilerStart` / `cudaProfilerStop`

```bash
cudaProfilerStart(); // profile start
DoProcess();
cudaProfilerStop(); // profile stop
DoOtherProcess();
```

```bash
asys profile -t hggc -c hggcProfilerApi cuda_test
```

+ `-c hggcProfilerApi`在`cudaProfilerStart`开始时启动跟踪抓取，在`cudaProfilerStop`停止时停止跟踪抓取，应用结束。（本例中仅抓取`DoProcess`执行过程中的跟踪）

**注意：**
当`hggcProfilerStart`和`hggcProfilerStop`在采集过程中多次出现时，比如 start 两次后 stop，asys 将生效`第一次出现的start`和`第一次出现的stop`，以确定采集时间范围。

举例：使用`hgtx`作为事件触发，抓取指定代码范围的跟踪，应用代码中插入 nvtx range，名称为`DoProcess`

```bash
for (int index = 0; index < 5; ++index) {
    nvtxRangePushA("DoProcess"); // start
    DoProcess();
    nvtxRangePop(); // stop
}
```

```bash
asys profile -t hggc,hgtx -c hgtx -p DoProcess cuda_test
```

+ `-c hgtx`指定使用 HGTX / NVTX 作为事件触发源
+ `-p DoProcess`指定 HGTX / NVTX range 名称，本例中 range 名称为`DoProcess`，domain 为默认 domain。`DoProcess`range 开始时启动跟踪抓取，range 结束时停止跟踪抓取，应用结束。

当使用 HGTX / NVTX 作为事件触发源时， `--hgtx-capture `或者 `-p`选项支持多种方式指定 domain 和 range 匹配模板：

| `--hgtx-capture`选项取值 | 匹配方式说明 |
| --- | --- |
| range@domain | 匹配 domain 下名称为 range 的时间范围，例如通过`nvtxDomainRangePushEx`创建 range |
| range | 匹配默认 domain 下名称为 range 的时间范围，例如通过`nvtxRangePushA`创建 range |
| range@* | 匹配任意 domain 下名称为 range 的时间范围 |

无论触发方式为`hggcProfilerApi`还是`hgtx`，asys 均支持事件多次触发，以及指定触发事件结束后的行为，通过`--capture-range-end`选项进行控制：

| `--capture-range-end`选项取值 | 触发结束事件后的行为 |
| --- | --- |
| none | 忽略结束事件，即事件触发采样后，持续采样到程序结束，或者`Ctrl + C`打断。 |
| stop | 本次结束事件后跟踪采集停止，应用程序继续运行，后续的触发事件被忽略。 |
| stop-shutdown | **默认值**，本次结束事件后跟踪采集停止，且停止应用程序。 |
| repeat[:N] | 循环通过事件触发跟踪采集`N`次，`N`次跟踪采集后，应用程序继续运行，后续的触发事件被忽略。<br/>`N`为可选值，例如`--capture-range-end=repeat`，则 asys 会循环根据事件触发采集。<br/>每次触发生成一份报告，报告名称将追加索引编号。 |
| repeat-shutdown:N | 行为和`repeat[:N]`选项类似，循环通过事件触发跟踪采集`N`次，`N`次跟踪采集后停止应用程序。<br/>每次触发生成一份报告，报告名称将追加索引编号。 |
| merge[:N] | 当前进程循环通过事件触发跟踪采集`N`次，`N`次跟踪采集后，应用程序继续运行，当前进程后续的触发事件被忽略。<br/>`N`为可选值，例如`--capture-range-end=merge`，则 asys 会循环根据事件触发采集。<br/>`N`次跟踪采集后，生成一份报告。 |
| merge-shutdown:N | 行为和`merge:N`选项类似，当前进程循环通过事件触发跟踪采集`N`次，`N`次跟踪采集后，`N`次跟踪采集后停止应用程序。<br/>`N`次跟踪采集后，生成一份报告。 |

循环采集跟踪举例如下，使用`repeat-shutdown:N`选项，循环采集 2 次跟踪，生成 2 个报告，随后应用程序停止：

```bash
asys profile -t hggc,hgtx -c hgtx -p DoProcess --capture-range-end repeat-shutdown:2 cuda_test
```

+ `-c hgtx`指定使用 HGTX / NVTX 作为事件触发源
+ `-p DoProcess`指定 HGTX / NVTX range 名称，本例中 range 名称为`DoProcess`
+ `--capture-range-end repeat-shutdown:2`循环触发 2 次跟踪采集，随后应用程序停止

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125058575/f2d673d31776d117887c6bc8ce547218/hgtx_nvtx_range_1.png)

循环采集跟踪生成一份报告文件举例如下，使用`merge-shutdown:N`选项，循环采集 2 次跟踪，生成 1 个报告，随后应用程序停止：

```bash
asys profile -t hggc,hgtx -c hgtx -p DoProcess --capture-range-end merge-shutdown:2 cuda_test
```

+ `-c hgtx`指定使用 HGTX / NVTX 作为事件触发源
+ `-p DoProcess`指定 HGTX / NVTX range 名称，本例中 range 名称为`DoProcess`
+ `--capture-range-end merge-shutdown:2`循环触发 2 次跟踪采集，随后应用程序停止

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125058856/ee24881048f7d34a832719a6371976a1/hgtx_nvtx_range_2.png)

**注意：**
当`--capture-range-end`为`repeat[:N]`或`repeat-shutdown:N`时，若应用程序中触发停止事件和下个触发开始事件间隔时间较短：
+ asys 可能无法响应此跟踪开始事件，asys 将会在匹配到后续跟踪开始事件后开始跟踪采集。
+ 其他进程（可触发事件不同进程）的跟踪数据可能在开始采集初期存在丢失。

**注意：**
当`--capture-range-end`为`merge[:N]`或`merge-shutdown:N`时，应用程序中的开始事件和停止事件仅应用本进程内的跟踪采集：
+ 应用程序当前进程的开始事件和停止事件不会触发其他进程的跟踪采集的开始或者停止。
+ 部分跟踪采集功能不受应用程序进程的事件重复启停控制，将始终采集跟踪数据，例如：CPU 与线程相关活动跟踪，RDMA 网卡运行指标跟踪等等。

#### 6.2.4. 长时间采集报告文件轮转
对于需要长时间跟踪采集的场景，asys 支持通过`--trace-rotation`选项配合`--duration`选项进行报告文件轮转：

+ asys 每次采集`--duration`指定的时间后生成报告文件，并继续启动下一轮跟踪采集。
+ 仅保留最近的若干报告文件，保留的文件个数通过`--trace-rotation`选项指定
+ 可通过`--output`指定报告名称模板，名称中使用`%t`参数记录跟踪起始时间，避免报告文件名重复

例如，指定每 30 秒生成一份报告文件，保留最近 3 份报告文件：

```bash
asys profile -t hggc --duration 30 --trace-rotation 3 --output test_report_%t cuda_test
```

+ `--duration 30`指定每次采集时间为 30 秒
+ `--trace-rotation 3`指定保留最近 3 份报告文件
+ `--output test_report_%t`指定生成报告名称模板，`%t`被替换为跟踪起始时间，生成文件名举例：`test_report_08_09_33.asysrep`

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125043811/6fc3ae9a5280473874e76c869485daee/duration_30_1.png)

**注意：**
+ `--trace-rotation`选项不支持和`--capture-range`选项配合使用
+ 本轮跟踪采集结束，到下一轮跟踪采集开始之间存在短的间隙，这段跟踪数据将不会被采集
+ asys 将持续采集跟踪数据直到应用程序结束，可通过输入`Ctrl + C`停止应用程序结束跟踪采集

#### 6.2.5. 指定报告名
asys 支持通过`--output`或者`-o`选项指定报告名（无需指定后缀，asys 会自动添加.asysrep 后缀），通过`--force-overwrite true`或者`-f true`选项允许覆盖同名文件。

通过`-o`选项指定报告名称时，asys 支持识别宏变量并替换为对应的值，支持的宏变量格式如下：

| 宏变量 | 替换的值 |
| --- | --- |
| %q{ENV} |“ENV”环境变量的值 |
| %h | 主机名 |
| %p | 应用程序的 PID |
| %i | 文件夹中不重名的索引编号 |
| %t | 跟踪起始时间，格式`hh_mm_ss` |

举例如下：

```bash
asys profile -t hggc -o report_%q{HGGC_DRIVER_CANDIDATE}_%i python test_linear.py
```

+ `-o report_%q{HGGC_DRIVER_CANDIDATE}_%i`，本例最终生成报告文件为：`report_UMD_2.asysrep`
    - `%q{HGGC_DRIVER_CANDIDATE}`替换为环境变量`HGGC_DRIVER_CANDIDATE`对应值
    - `%i`替换为确保本文件夹相同名称前缀文件不重名的索引值

**注意：**
默认`-o`选项值为`report%i`，因此默认不指定`-o`选项时，报告文件也不会覆盖。

#### 6.2.6. 自定义应用运行环境
asys 支持指定应用程序运行时的环境配置：

可通过选项`--env-var`或者`-e`添加应用执行时的环境变量，多个环境变量通过`,`分隔。

可通过选项`--inherit-environment false`  或者 `-n false`指定应用程序运行时不继承系统环境变量。

可通过`--show-output false`或者`-w false`禁止应用程序打印输出。

举例如下：

```bash
asys profile -e ENABLE_DEBUG=1,LOG_LEVEL=DEBUG -n false -w false python test_linear.py
```

+ `-e ENABLE_DEBUG=1,LOG_LEVEL=DEBUG`运行应用程序时，配置环境变量`ENABLE_DEBUG`和`LOG_LEVEL`
+ `-n false`运行应用程序时，不继承系统环境变量
+ `-w false`禁止应用程序打印输出

#### 6.2.7. 等待应用程序结束
asys 支持指定应用程序结束的判断方式，默认是等待应用程序 fork 出的所有进程结束后，认为应用程序结束。比如 daemon 方式运行的应用，asys 默认等待后台的 daemon 进程均已结束后，停止跟踪采集。

具体等待应用程序结束的方式，通过`--wait`选项指定：

| `--wait`选项取值 | 等待应用程序结束条件 |
| --- | --- |
| primary | asys 等待应用程序主进程（初始进程）结束 |
| all | 默认值，asys 等待应用程序进程，和 re-parent 到应用程序的进程结束 |

#### 6.2.8. 系统级跟踪采集
asys 采集跟踪数据时，默认采集本应用程序进程树（根进程和子孙进程）的跟踪信息。若当前系统内存在其他背景应用程序抢占 CPU 侧资源，导致应用程序执行受影响，此类问题仅通过进程树的跟踪信息难以定位。可使用 asys 采集本操作系统内所有进程的跟踪数据（系统级跟踪），以分析背景应用的影响。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125073689/11fbae1af1fec21ce55a626abab152d0/sample_1.png)

可通过选项`--sample`或者`-s`使能系统级跟踪采集，例如：

```bash
asys profile -s system-wide -t hggc python test_linear.py
```

+ `-s system-wide`：采集系统内所有进程的 CPU 调度跟踪数据

系统级跟踪采集支持不指定应用程序，不指定应用程序时无法采集`应用级跟踪采集项`，例如：

```bash
asys profile -s system-wide --ppu-metrics-device all --nic-metrics true
```

+ `-s system-wide`：采集系统内所有进程的 CPU 调度跟踪数据
+ `--ppu-metrics-device all`：使能所有 PPU 设备的 metrics 采样
+ `--nic-metrics true`：采集网卡运行指标

asys 支持多种`系统级跟踪采集项`，例如`--ppu-metrics-device`等功能，在帮助信息中均标记为`System scope`。与之对应的，asys 支持多种`应用级跟踪采集项`，例如`--trace`等功能，在帮助信息中均标记为`Application scope`。`-s`选项可通过设置为`system-wide`或者`process-tree`可切换 CPU 调度采集为系统级或者应用级。具体跟踪项类型说明请参见`asys profile -h`帮助信息。

#### 6.2.9. 限制采集的应用程序进程
asys 默认采集应用程序的所有进程的跟踪数据并记录到同一份报告文件，跟踪数据量可能巨大，若希望只采集部分进程的跟踪数据，可通过选项指定进程的过滤条件。

可通过`--process-ppu-include`选项指定采集的 PPU 设备 ID 列表，多个 PPU 设备 ID 之间通过逗号`,`拼接，例如只采集使用 PPU 设备 ID 为`0`和`2`的进程的跟踪数据：

```bash
asys profile --process-ppu-include 0,2 python test_linear.py
```

**注意：**
+ 若通过`--process-ppu-include`指定采集进程的使用的 PPU 设备 ID，未使用 PPU 设备的进程的跟踪数据依然会被采集。
+ 若进程使用多个 PPU 设备，若部分 PPU 设备不在指定采集的 PPU 设备 ID 列表，此进程的跟踪数据将**不会**被采集。

可通过`--process-rank-include`选项指定需要采集的进程的 Rank ID，多个 Rank ID 之间通过逗号`,`拼接，例如只采集 Rank ID 为`0`和`2`的进程的跟踪数据：

```bash
asys profile --process-rank-include 0,2 python test_linear.py
```

在指定`--process-rank-include`选项时，asys 默认通过以下环境变量检测进程的 Rank ID：

```bash
OMPI_COMM_WORLD_RANK
SLURM_PROCID
RANK
PMI_RANK
```

若需要通过其他环境变量获取进程的 Rank ID，可通过选项`--process-rank-env`指定环境变量名称，例如指定通过`PROCESS_RANK_ID`环境变量检测 Rank ID：

```bash
asys profile --process-rank-include 0,2 --process-rank-env=PROCESS_RANK_ID python test_linear.py
```

**注意：**
若通过`--process-rank-include`指定采集进程的 Rank ID，无法检测到 Rank ID 的进程的跟踪数据将`不会`被采集。

### 6.3. 交互式采集跟踪
在使用`asys profile`采集跟踪的方式之外，asys 支持通过命令单独控制`启动应用`/`开始采集`/`停止采集`/`停止应用`等行为，允许灵活地控制跟踪抓取行为。

#### 6.3.1. 交互式命令说明
asys 支持通过以下子命令控制跟踪采集过程，各个子命令支持的选项和`asys profile`支持的选项类似，可以通过`asys <subcommand> -h`查看帮助信息：

| asys 子命令 | 功能 |
| --- | --- |
| launch | + 启动被采集应用程序，指定应用程序运行过程中允许被抓取的跟踪项<br/>+ asys launch 命令可在 asys start 命令执行之前或者之后执行<br/>+ 通过`asys launch -h`查看帮助信息 |
| start | + 开始跟踪采集，指定跟踪报告文件，事件触发条件等<br/>+ asys start 命令可在 asys launch 命令执行之前或者之后执行<br/>+ 通过`asys start -h`查看帮助信息 |
| stop | + 停止跟踪采集，输出跟踪报告<br/>+ asys stop 仅停止跟踪采集，不停止应用程序<br/>+ 通过`asys stop -h`查看帮助信息 |
| cancel | + 取消跟踪采集，不生成报告<br/>+ asys cancel 仅取消跟踪采集，不停止应用程序<br/>+ 通过`asys cancel -h`查看帮助信息 |
| shutdown | + 停止应用程序<br/>+ 若存在跟踪采集，取消跟踪采集，不生成报告<br/>+ 通过`asys shutdown -h`查看帮助信息 |
| sessions | + 执行`asys sessions list`查看当前存在的跟踪采集过程列表 |

通过子命令的配合执行，可以灵活的决定应用运行和跟踪采集的时机。

举例：先启动应用程序，抓取两次跟踪，随后停止应用：

```bash
asys launch -t hggc cuda_test
asys start -o test_report1
asys stop
asys start -o test_report2
asys stop
asys shutdown
```

+ `asys launch ...`启动应用程序
+ `asys start ...`开始跟踪采集，指定报告文件。
+ `asys stop`停止跟踪采集，执行后应用程序仍在运行，后续可继续执行`asys start ...`开启新一轮的跟踪采集
+ `asys shutdown`停止应用程序

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125035436/31f1e739c491b532a3d39ae14504bc1b/asys_launch_1.png)

举例：先启动跟踪采集，指定事件触发条件，然后启动应用程序：

```bash
asys start -o test_report -c hgtx -p DoProcess
asys launch -t hggc,hgtx cuda_test
```

+ `asys start ...`启动跟踪采集，通过`-c`和`-p`选项指定事件触发条件，跟踪会等待应用程序启动后，开始跟踪抓取
    - `-c hgtx`：使能通过 HGTX range 事件触发跟踪采集
    - `-p DoProcess`：指定跟踪采集通过名称为`DoProcess`的 HGTX range 触发
+ `asys launch ...`启动应用程序，由于已通过`asys start`开启跟踪抓取，`asys launch ...`在应用启动后即可开始跟踪抓取。跟踪会在匹配到事件触发条件后开始记录。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125035681/17803c80b2fa6432d8772ddac21978fd/asys_start_1.png)

#### 6.3.2. 多个采集过程共存
asys 支持多个采集过程共存，例如多个`asys profile`或者`asys launch / start`采集过程同时执行。每个采集过程对应一个`session`，用于区分多个共存的采集过程，可通过选项`创建`或者`关联`一个 session。

每个 session 有对应的名称和 session ID，多个 session 之间名称不可相同

| session 选项 | 功能 |
| --- | --- |
| --session-new | + `创建`一个新的 session，指定 session 名称，多个 session 之间名称不可相同<br/>+ `asys profile / launch / start`子命令支持创建 session |
| --session | + `关联`一个已存在的 session，通过 session 名称或者 ID 指定<br/>+ `asys launch / start / stop / cancel / shutdown`子命令支持关联 session |

举例：执行`asys launch`创建一个 session，执行`asys start`时关联此 session，指定此`session`开始跟踪采集

```bash
asys launch -t hggc --session-new test cuda_test
asys start --session test
```

+ `--session-new test`创建一个名称为`test`的 session
+ `--session test`关联到名称为`test`的 session

查看当前存在的采集过程 session 列表：

```bash
asys sessions list
```

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125060759/0f5e75ebfe5a279131d7d035a7272755/interactive_collection_1.png)

其中`ID`列为 session 对应的 session ID，用于可在`--session`选项中使用此 ID 指定 session。

若不指定 session 选项，则默认 session 名称如下：

+ `asys profile`子命令：session 名称`profile-<pid>-<application>`
+ `asys launch / start / stop / cancel / shutdown`子命令：session 名称`[default]`

**注意：**
多个 asys profile 子命令，因 session 名称不同默认可共存。交互式子命令，只允许一个默认名称的 session 存在

### 6.4. Attach 模式采集（Beta）
asys 支持通过`attach`附着到应用程序采集跟踪数据，应用程序不需要事先通过 asys 启动。`asys attach`支持同时附着到多个应用进程，并支持反复附着到相同应用程序采集数据。`asys attach`完成采集后不会影响应用程序继续运行。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125031844/3660aed729781c89d9f523300127973d/asys_attach_1.png)

#### 6.4.1. Attach 跟踪采集说明
使用`asys attach`附着到多个应用进程采集跟踪，示例如下：

```bash
asys attach -t hggc -f true -o attach_report 94644,94923
```

+ `-t hggc`采集 HGGC 相关跟踪
+ `-f true`允许同名报告文件覆盖
+ `-o attach_report`指定报告名称为`attach_report`
+ `94644,94923`同时附着到 PID 为`94644`和`94923`的进程，多个 PID 通过`,`区分

`asys attach`执行后开始采集跟踪数据，可通过输入`Ctrl + C`停止跟踪采集并生成报告文件，或者通过`--duration`指定采集时长，例如：

```bash
asys attach -t hggc --duration 10 94644,94923 
```

+ `--duration 10`采集 10 秒后停止跟踪采集，并生成报告，应用程序运行不受影响

`asys attach`支持反复附着到应用程序采集跟踪数据，在采集结束后不会停止应用程序。`asys attach`在停止采集后对应用性能影响小，不干扰应用程序继续运行。

#### 6.4.2. 跟踪采集支持范围
`asys attach`支持的跟踪采集功能和`asys profile`类似，可通过执行`asys attach -h`查看具体支持的功能项。

选项`-t`支持的各个跟踪项，对应采集的信息内容，参见如下表格：

| 跟踪项 | 采集内容 |
| --- | --- |
| hggc | HGGC runtime/driver API 的执行时间以及调用栈信息<br/>CUDA runtime/driver API 的执行时间以及调用栈信息<br/>PPU 执行信息： kernel/memcpy/memset<br/>HGGC/CUDA API 和 PPU 执行关联关系 |
| pccl | PCCL 通信过程各阶段的执行时间 |

其他`asys attach`支持的跟踪采集功能如下：

+ 支持`--sample`CPU 执行信息和`--backtrace`调用栈采集
+ 支持`--python-sampling` Python 调用栈采集
+ 支持`--python-functions-trace`Python 函数采集
+ 支持`--python-backtrace`采集 HGGC API python backtrace
+ 支持`--host-memory-sampling`系统内存使用采集
+ 支持`--ppu-metrics-device`设备运行指标采集
+ 支持`--nic-metrics`网卡运行指标采集
+ 支持`--hggcbacktrace` HGGC 调用栈采集
+ 支持`--hggc-memory-usage`设备内存使用采集和锁页内存使用采集

#### 6.4.3. Attach 注意事项
使用`asys attach`进行跟踪采集时，需要注意如下事项：

+ `asys attach`只支持在`x86_64`/`arm`指令集环境中运行
+ `asys attach`在附着到应用程序的过程中，可能导致应用程序崩溃或死锁
+ 相同应用进程不支持不同 release 版本的`asys attach`混合使用

`asys attach`的使用限制如下：

+ 暂不支持采集 HGTX / ACDNN / ACBLAS / OSRT / Video 等跟踪数据
+ 不支持采集在 attach 之前已经实例化的 legacy HGGC graph 相关跟踪信息
+ 不支持 attach 到已使用 HGPTI 库的进程

### 6.5. 多节点跟踪采集
`asys profile`支持多节点跟踪采集模式，通过执行一次`asys profile`命令在每台服务器生成一份报告文件，无需修改应用代码，支持多种多节点应用启动框架。

**注意：**
请确保每台服务器已安装 T-Head SAIL SDK，并已完成 SDK 相关初始化配置

#### 6.5.1. 采集 Ray 框架启动的多节点应用
asys 支持采集通过`Ray`框架启动的多节点应用跟踪数据，如使用`vLLM`的模型应用。在完成`Ray`框架组网后，通过`asys profile`启动应用时，通过`--multi-node-mode ray`使能多节点跟踪采集模式，例如：

```bash
asys profile --multi-node-mode ray -f true -o demo_vllm bash eval_llm_infer.sh
```

+ `--multi-node-mode ray`：使能支持`Ray`框架的多节点跟踪采集模式
+ `-f true`：覆盖已存在的报告文件
+ `-o demo_vllm`：指定报告名称为`demo_vllm`

多节点跟踪采集模式将在每台服务器生成一份报告文件，报告文件名称将会追加`_node_<hostname>`信息，例如`demo_vllm`报告名称在各个服务器实际生成的名字示例如下：

+ demo_vllm_node_node0.asysrep
+ demo_vllm_node_node1.asysrep

**信息：**
+ 需要使用 root 用户或者拥有相同权限，使能`Ray`框架多节点跟踪采集模式可能导致应用程序崩溃或死锁
+ 通过--multi-node-mode 使能多节点跟踪采集时，不支持采集 Heap 内存使用跟踪数据，不支持采集应用 stdout / stderr 输出信息
+ 受限于`Ray`框架 worker 停止方式，应用停止阶段跟踪采集可能不完整，建议通过`--capture-range`使用事件触发跟踪采集，或使能`--flush-on-context-synchronize true`选项及时保存跟踪数据

#### 6.5.2. 采集 mpirun 启动的多节点应用
asys 支持采集通过`mpirun`框架启动的多节点应用跟踪数据，通过`asys profile`启动应用时，通过`--multi-node-mode mpirun`使能多节点跟踪采集模式，例如：

```bash
asys profile --multi-node-mode mpirun -f true -o pccl_all_reduce mpirun -np 16 -npernode 8 -H node0:8,node1:8 all_reduce_perf
```

+ `--multi-node-mode mpirun`：使能支持`mpirun`启动的多节点跟踪采集模式
+ `-f true`：覆盖已存在的报告文件
+ `-o pccl_all_reduce`：指定报告名称为`pccl_all_reduce`

多节点跟踪采集模式将在每台服务器生成一份报告文件，报告文件名称将会追加`_node_<hostname>`信息，例如`pccl_all_reduce`报告名称在各个服务器实际生成的名字示例如下：

+ pccl_all_reduce_node_node0.asysrep
+ pccl_all_reduce_node_node1.asysrep

**注意：**
+ 通过--multi-node-mode 使能多节点跟踪采集时，不支持采集 Heap 内存使用跟踪数据，不支持采集应用 stdout / stderr 输出信息
+ 不支持通过绝对路径的方式使用 mpirun 启动应用，例如`/usr/bin/mpirun`

**比赛关联：** 用 `-c hgtx -p <range>` 事件触发或 `--delay/--duration` 只采集稳态 decode 区间，配合 `--stats true` 可在压测时自动生成统计结果；测量 TTFT 时应采集包含首个请求完整生命周期的区间，报告控制在 200MB 以内（`-s none` 关闭 CPU 采样）以保证分析效率。

<a id="cEMJf"></a>

## 7. Asight Systems GUI 分析

本章介绍 Asight Systems GUI 的主要界面组成和操作方法，包括 Timeline View、Events View、Function View 等核心视图。

Asight Systems GUI 用于展示采集的报告。打开报告后的 GUI 如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125031406/d0eb418b87204eb90ea01441ba49836b/asight_systems_gui_1.png)

上图中，GUI 的主要部分有：

1. 菜单栏，详情请见[菜单栏](#UGOJG)
2. Project Explorer，详情请见[Project Explorer](#Wj5P1)
3. Timeline View，详情请见[Timeline View](#wqLns)
4. Events View，详情请见[Events View](#n44Ub)

<a id="UGOJG"></a>

### 7.1. 菜单栏
Asight Systems GUI 的菜单栏功能如下：

**File**

+ Open：打开报告
+ Save：保存报告（如果报告支持）
+ Open Advanced：报告的高级打开功能，详情请参见[报告的高级打开功能](#czyWc)
+ Exit：退出 Asight Systems GUI

**View**

+ Show Project Explorer：是否显示 Project Explorer
+ Show Output Messages：是否显示 Output Window
+ Show Section Tool：是否显示 Section Tool
+ Metric Details：是否显示 Metric Details 窗口

**Tools**

+ asys Command Helper：打开 asys 命令生成助手
+ acu Command Helper：打开 acu 命令生成助手
+ Metrics List：打开 Metrics List 窗口
+ Occupancy Calculator：打开占有率计算器
+ Options：打开 Options Dialog，详情请参见[Options Dialog](#ADyNl)

**Help**

+ Documentation：打开 Asight Systems 用户手册
+ Welcome Page：打开欢迎页面
+ Change Log：打开 Change Log 窗口
+ Download：下载最新的 Asight Systems GUI
+ Check for Updates：检查更新
+ About：关于 Asight Systems

<a id="czyWc"></a>

#### 7.1.1. 报告的高级打开功能
Asight Systems 提供了报告的高级打开功能，支持：

1. 在 Timeline View 中打开多个报告
2. 允许打开报告的任意部分（按百分比计算）
3. 指定要加载的事件类型，只有被勾选的类型才会在打开报告时加载

高级打开功能的入口在`File`->`Open Advanced`，其 UI 如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125063436/1bffa1d1e10a7a32dc253019f60f055d/open_advanced_1.png)

1. 要打开的报告列表，这些报告会在同一 Timeline View 中显示
2. 报告路径的控制按钮，从左到右依次为：
    1. 添加一个新路径
    2. 删除当前选中的路径
    3. 将当前选中路径上移一行
    4. 将当前选中路径下移一行
3. 打开文件浏览器，选择新路径代替当前路径
4. 选择是否将多个报告按其起始时间对齐
5. 选择要加载的事件类型，只有被勾选的类型才会被加载
6. 选择打开报告的百分比，上图中代表打开报告的 30%-60%部分

加载事件类型和跟踪数据的对应关系如下：

| 加载事件类型 | 跟踪数据类型 |
| --- | --- |
| Metrics sampling | PPU Metrics 跟踪<br/>CPU Metrics 跟踪 |
| CPU schedule | CPU 线程调度情况 |
| Memory usage | PPU 内存使用跟踪<br/>Pinned 内存使用跟踪<br/>Host 内存使用采样<br/>Heap 内存使用跟踪 |
| OS runtime | OS Runtime（OSRT）跟踪和调用栈 |
| HGTX | HGTX 跟踪 |
| HGGC | HGGC API 跟踪和调用栈<br/>HGGC PPU Activity 跟踪 |
| acDNN | acDNN API 跟踪和调用栈 |
| acBlas | acBlas API 跟踪和调用栈 |
| Video | Video API 跟踪<br/>Video PPU Activity 跟踪 |
| PCCL | PCCL 活动跟踪 |
| Log | 应用 stdout 和 stderr 日志 |
| NIC metrics | RDMA 网卡运行指标跟踪 |
| Backtrace | HGGC / acDNN /  acBlas / OSRT API 调用栈<br/>CPU backtrace 采样跟踪<br/>Python backtrace 采样跟踪<br/>PPU / Pinned / Heap 内存使用调用栈 |

当选中多个报告在同一 Timeline View 显示时，各报告中的时间线将按照事件发生的时间在 Timeline View 中显示，如需对齐不同报告中的时间线，请参见[多报告的时间线对齐](#IRK3I)。

<a id="Wj5P1"></a>

### 7.2. Project Explorer
Asight Systems GUI 提供了 Project Explorer 来管理打开的报告，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125069848/a5b961efa2cf09fe42729024c448a961/project_explorer_1.png)

上图中加粗的报告代表被打开。Project Explorer 会保存打开的报告记录，可以在右键菜单中将报告记录移除。

要快速导航到报告文件的所在目录，可以在 Project Explorer 中右键单击报告，然后在右键菜单中选择 Show in Finder/Explorer。

**注意：**
Project Explorer 只保存报告的引用，当报告被删除、移动时，这些引用会失效。

<a id="wqLns"></a>

### 7.3. Timeline View
Timeline View 展示所有事件的时间线，包括 HGGC、HGTX、OSRT、CPU Sampling 等。通过 Timeline View 可以查看 PPU 以及 CPU 的工作负载，准确地定位瓶颈。

Timeline View 从上到下分为两部分：顶部的 Timeline 区域，以及底部的 Events View 部分，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125083206/ad76129dcaf6b6ef64ca58c98d803b80/timeline_view_2.png)

1. Page 切换下拉列表，可以从 Timeline View 切换至 Analysis Summary View
2. Timeline Tree
3. 报告级 Options 按钮，点击打开 Options Dialog
4. 搜索框
5. Timeline Area
6. 操作指南按钮，点击打开操作指南
7. 纵向缩放滑块，用来纵向缩放 Timeline
8. 点击切换至 Diagnostics Summary View
9. Events View

采集的事件以树状的形式组织在左侧的 Timeline Tree 中，如果某项采集没有启用，对应的行不会在 Timeline 中显示。

#### 7.3.1. 操作指南
Asight Systems GUI 支持多种操作浏览时间线，操作指南中列出了支持的操作及其快捷键：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125080616/56040956337ba1e92c2e95d2daedb96a/timeline_operation_guide_1.png)

##### 7.3.1.1. 键鼠操作
| 动作 | 键鼠操作 |
| --- | --- |
| 向左平移 | 键盘←/A |
| 向右平移 | 键盘→/D |
| 水平放大 | 键盘+ or 键盘= or 键盘 W or CTRL/Command + 滚轮↑  |
| 水平缩小 | 键盘- or 键盘 S or CTRL/Command + 滚轮↓ |
| 下一行 | 键盘↓ |
| 上一行 | 键盘↑  |
| 撤销一次操作 | Backspace |

##### 7.3.1.2. 触控板操作
| 动作 | 触控板操作 |
| --- | --- |
| 向左平移 | 两指向左滑动 |
| 向右平移 | 两指向右滑动 |
| 水平放大 | 两指放大 |
| 水平缩小 | 两指缩小 |
| 向上滚动 | 两指向下滑动 |
| 向下滚动 | 两指向上滑动 |

##### 7.3.1.3. 选择 Item
| 动作 | 键鼠操作 |
| --- | --- |
| 在 Timeline 中选中一项 | 鼠标左键单击 |
| 在 Events View 中选中一项 | 鼠标左键双击 |
| 选中一项并放大至整个屏幕 | CTRL/Command + 鼠标左键单击 |

##### 7.3.1.4. 选择时间范围
| 动作 | 键鼠操作 |
| --- | --- |
| 选择时间范围 | 鼠标左键框选 |
| 拖动选中的时间范围 | 鼠标左键拖动 |
| 取消选择时间范围 | ESC or 在选中范围外点击鼠标 |
| 放大至时间范围 | Z |
| 放大至时间范围并取消选择 | Shift + Z or 鼠标左键双击时间范围 |
| 过滤当前时间范围 | F |
| 过滤当前时间范围并取消选择 | Shift + F |

##### 7.3.1.5. 纵向缩放
除了横向缩放操作外，Timeline View 还提供纵向缩放功能，可以点击右上方的缩放滑块进行操作：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125083717/aad9297deb7d42d2d55d58d8da6cc190/timeline_view_3.png)

点击左侧的放大镜按钮
![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125038638/de0b9e8d57df6393fd65e0592af5bf8f/command_palette_1.png)进行复位。

##### 7.3.1.6. Pin Row
Timeline View 支持 Pin Row 功能，通过`右键菜单`或`CTRL/Command + P`快捷键可以将感兴趣的行锁定显示在屏幕的上方或下方，方便对比查看：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125038935/ccafcc9efc81d63a5fc17bfabfa78031/command_palette_2.png)

##### 7.3.1.7. 隐藏尾部节点
为了显示简洁，Timeline Tree 的某些节点支持将尾部的子节点隐藏：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125059162/7fa3427123b13f8934fc6b2c47c70d20/hide_tail_nodes_1.png)

隐藏节点功能支持如下操作：

| 动作 | 键鼠操作 |
| --- | --- |
| 增加显示 1 个节点 | 鼠标左键单击“+” |
| 减少显示 1 个节点 | 鼠标左键单击“-” |
| 增加显示 5 个节点 | CTRL/Command + 鼠标左键单击“+” |
| 减少显示 5 个节点 | CTRL/Command + 鼠标左键单击“-” |
| 显示所有隐藏节点 | 鼠标左键双击 |

也可以利用右键菜单进行操作：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125059486/61446433b13e437cf90f797a2e6be064/hide_tail_nodes_2.png)

| 动作 | 键鼠操作 |
| --- | --- |
| Show More | 增加显示 1 个节点 |
| Show Less | 减少显示 1 个节点 |
| Show All | 显示所有节点 |
| Reset View | 恢复默认显示状态 |

节点隐藏功能被用于以下节点：

+ CPU Core
+ 线程
+ 进程
+ PPU Stream
+ PPU HGTX
+ PPU Kernel

##### 7.3.1.8. 展开/折叠所有子节点
在包含子节点的节点的右键菜单中，可以展开/折叠其所有子节点，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125069533/023a3c500091360f785ba0ee25d9964e/ppu_stream_1.png)

##### 7.3.1.9. Tooltip
Timeline View 中所有的 item 都提供 tooltip，可以将鼠标悬停在 item 上查看详细信息：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125086067/073d3f698b0a46ced70f42f0e2a13270/tooltip_1.png)

可以点击 tooltip 右上角的按钮将其 pin 住方便阅读，也可以点击复制按钮复制 tooltip 内容。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125086384/a4f6049c281ca6689575f45a5a66b390/tooltip_2.png)  

对于名字较长的时间线，例如 kernel 或 HGTX，支持切换显示完整内容：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125039299/66ff891eb546095b5676a5ace243768d/copy_tooltip_1.png)

时间线也支持通过`右键菜单`->`Copy Tooltip`将 tooltip 导出：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125039601/7716df1e4a6bf4513cac2f46a097db06/copy_tooltip_2.png)

##### 7.3.1.10. 切换时间轴时间显示模式
Timeline View 的时间轴支持两种时间显示模式：

1. Session Time：该显示模式以报告的起始时间作为时间轴上的原点显示时间，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125083992/c0965a0c0d7c5f1c1679fb3227973777/timeline_view_4.png)

2. Global Time：该显示模式显示真实的时间

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125081510/95bd9c1996f1e9632b09c2734e2fb7b7/timeline_time_display_1.png)

两种时间显示模式可以通过左侧的三角按钮进行切换：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125081801/4757d80fe3d8503fc720f6b60f91ba8c/timeline_time_display_2.png)

##### 7.3.1.11. Dock Widget
支持 Dock Widget，可以将报告拖出主窗口，方便在不同的窗口和屏幕查看报告

可以通过拖拽 tab 的方式实现 dock: 

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125043096/dd6a73615f8e3dd1ead5e948748b53ee/dock_widget_1.png)

还可以通过右键菜单中的 Detach/Attach 选项：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125043524/f14f788196f9f06a0826d017c902221a/dock_widget_2.png)

##### 7.3.1.12. 标记时间线
Timeline View 支持将时间线标记为 bookmark，方便在大型报告中标记感兴趣的时间线，可以通过时间线的右键菜单进行标记/取消标记：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125084229/a55c35587c1f4aabe5e42bd04b7febbe/timeline_view_5.png)

在进行标记后，该时间线会持久显示一个标志，标志中会有该 bookmark 的序号：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125084465/c5e25d9c2a16a5e007666a11000ff85e/timeline_view_6.png)

同时在下方的 Bookmarks 窗口中可以管理所有的 bookmark：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125079414/2668ab1eeac78a8912dd4eb6c1269f0c/timeline_bookmark_1.png)

在该窗口中支持：

+ 修改 bookmark 的序号
+ 对 bookmark 添加注释
+ 一键清除所有 bookmark
+ 双击 Name 列或者通过右键菜单可以跳转至对应时间线的位置
+ 通过剪贴板导入/导出 bookmark 的 code
+ 在关闭报告时，会将 bookmark 写入文件，在报告同目录下生成一个与报告同名的 asysrepbm 文件。再次打开报告时会读取该文件自动导入 bookmark
    - 该行为可以通过菜单栏`Tools`->`Options`->`Systems Profile`->`Bookmark Management Mode`选项修改

#### 7.3.2. Timeline Item 显示策略

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125037603/91465b36cad7b3a245a8bf9fd39e1e03/bookmark_code_1.png)

Timeline View 的上方是一条时间轴，时间从左至右增长，为方便查看，当 Timeline View 放大到一定程度时，采用**基准**+**增量**的形式显示时间。

在 Timeline View 中，事件的时间线被称为 Timeline Item。不同类型的 Timeline Item 用不同的颜色表示，Item 的左侧边缘为事件的起始时间，Item 的右侧边缘为事件的结束时间，Item 的宽度代表该事件持续时间的长短。

在 Timeline View 没有被完全放大时，Asight 采用占有率柱状图的方式显示事件：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125079746/423d48c7ca6be8d8a9c901ed94f3bd14/timeline_item_1.png)

上图中 Kernel 的时间线以不同高度的柱状图的形式显示，这种柱状图显示策略被应用于 CPU 利用率，线程和进程占有率，Kernel 和 Memcpy 等多种数据。

##### 7.3.2.1. 通信算子分层显示
Timeline View 中通信算子被分层，并以特别的颜色显示，例如在[All Streams]行中：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125080280/2ef84e8c2b4958de1c2f5baa40e06309/timeline_item_2.png)

##### 7.3.2.2. 不同的 Kernel 以不同的颜色显示
为了方便分辨每个 kernel 的时间线，Timeline View 支持将不同的 kernel 以不同的颜色，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125063803/f874b9fd2c12dc54610f3c631d8c55b9/options_dialog_1.png)

可以通过`Options Dialog`中的`Systems Profile`->`Color HGGC Kernels`开启该功能。

#### 7.3.3. 时间线关联
当选中一项 item 后，所有与之相关的 item 都会被高亮：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125064261/84f46dc4b5f95a5619633a4ab001aca7/options_dialog_2.png)

事件在以下两种情况下会产生关联

1. 同属于同一个调用栈内，例如 HGGC 嵌套在 HGTX 内
2. 由 Host API 调用发起的 Device Activity，例如 launch kernel API 与 kernel

##### 7.3.3.1. 事件关联的操作与标记
在选中 item 后，Timeline View 中会显示相应的标记与按钮：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125084914/20c1673ca8b8739fe11247d522e41d3f/timeline_view_7.png)

#### 7.3.4. 选择时间范围
Timeline View 支持时间范围的选取，只需点击鼠标左键并拖拽，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125085360/59206de89a49c3144a0d591dee726a79/timeline_view_8.png)

在选择时间范围时，会出现 tooltip 显示时间范围的起始时间和持续时间，同时会显示当前时间范围内 PPU 的 active/idle 时间占比以及 kernel 执行和 memory 操作的时间占比情况。

在选取时间范围或调整大小时，可以按住 Shift 按键来触发吸附功能，时间范围会自动吸附到最近的时间线的起点/终点。

在选中时间范围后，支持拖拽改变其位置大小。双击时间范围可以将其放大至整个屏幕。Asight Systems 支持过滤功能，可以通过`右键菜单`->`Filter and Zoom in`过滤出当前时间范围的事件，在 Events View 中进一步查看。

<a id="IRK3I"></a>

#### 7.3.5. 多报告的时间线对齐
当在[Timeline View 中打开多个报告](#czyWc)时，不同报告中的时间线按照事件发生的时间在 Timeline View 中显示。如需调整不同报告中的时间线偏移量，Asight Systems 提供了时间线对齐功能，其入口如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125046994/d8fb6c30ab63e677026796fee3ee0695/filter_and_zoom_in_1.png)

点击后，会弹出时间线对齐对话框：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125085757/3d3aaf4b0b8d525c23faece0c1da5623/timeline_view_9.png)

1. 不同报告时间线相对其各自采集开始时间的偏移量，单位为纳秒，默认为 0，可以手动输入时间偏移量进行校准
2. 选择是否将报告按其起始时间对齐
3. 进入时间线挑选模式，在每个报告中选择一个时间线作为基准进行对齐
4. 选择时间线的对齐模式

Timeline View 支持两种对齐模式：

##### 7.3.5.1. 手动对齐
如果知道报告之间的时间偏移量，可以手动输入偏移量，单位为纳秒，正值代表报告中的时间线整体向右移动；负值代表时间线整体向左移动。第一行的报告无法指定其偏移量。

##### 7.3.5.2. 半自动对齐
如果知道报告中的哪些事件是同时发生的，可以以这些时间线为基准进行半自动对齐，Timeline View 会根据这些时间线自动计算不同报告之间的时间偏移量。

首先点击 Pick 按钮，进入到时间线挑选模式：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125082485/6be2f02da6d52cd036f9c05bed7615a2/timeline_view_10.png)

进入时间线挑选模式后，时间线对齐对话框会消失，在窗口下方出现一行 tooltip；在 Timeline View 中单击鼠标左键选择作为基准的时间线，被选中的时间线会高亮显示。每个报告只能选择一个，如果选择同一报告下的多条时间线，之前被选中的时间线将被取消选中。

选中时间线后，在时间线对齐对话框中可以选择左对齐或右对齐：

**左对齐**：所选的时间线是同时开始的，即以时间线的左侧进行对齐

**右对齐**：所选的时间线是同时结束的，即以时间线的右侧进行对齐

可以通过如下键盘操作退出时间线挑选模式：

**回车键**：确认挑选的时间线，重新弹出时间线对齐对话框

**ESC 键**：放弃挑选时间线，重新弹出时间线对齐对话框

如果确认挑选的时间线，重新弹出的时间线对齐对话框如下所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125044683/411d74d2b7c2a0607ac5bd308e944c11/esc_1.png)

首先每个报告的时间线偏移量会被自动计算并填充；在 Pick 按钮中会显示有 4 条时间线被选择了；在下方的组合框中可以选择左对齐或者右对齐，上方的时间偏移量会根据对齐方式的不同，而自动计算。

**注意：**
在挑选时间线作为基准时，以第一个报告里选中的时间线作为基准计算时间偏移量，当没有为第一个报告选中时间线时，在左对齐模式下，将以第一个报告的起始时间为基准计算偏移量；在右对齐模式下将以第一个报告的结束时间为基准。因此建议总为第一个报告选择作为基准的时间线。
对于其他的报告可以不选择时间线，未选择时间线的报告将不会执行对齐操作。

#### 7.3.6. Timeline Row 的搜索过滤
Timeline Row 的搜索过滤功能可以帮助快速找到感兴趣的 Timeline Row，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125080948/d631cb4e89d76075a2e4c2d97c4f3496/timeline_row_1.png)

可以切换搜索/过滤两种模式 

+ 搜索模式：高亮匹配项，并且支持跳转至下一个/上一个匹配项 
+ 过滤模式：仅显示匹配项 

搜索模式下的搜索结果如下图所示： 

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125081209/e4c7bb706770d92c91ced330436e608d/timeline_row_2.png)

#### 7.3.7. 在 Group View 中显示时间线
一些大型报告中往往有着海量的时间线，为了方便分析感兴趣的时间线，Timeline View 中提供了时间线的分组显示功能，可以将感兴趣的时间线添加到 Group View 中单独显示。

可以在感兴趣的时间线行上点击右键，将其添加到一个 Group View 中：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125050890/2e3a5286a4d413fab0504ee23d856176/group_view_1.png)

添加完毕后，在 Timeline View 的上方会出现切换 Group View 的按钮，在当前时间线行的右侧会出现 Group 的标志，其颜色与上方的 Group View 按钮颜色相同。点击该按钮可以切换到该 Group View，效果如下所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125051224/17dd30d87a83607466d9abd0f1c52040/group_view_2.png)

可以看到，上图中只有感兴趣的[All Streams]行显示，其他相关的时间线行已经被隐藏。与目标行一同显示的还有：

+ 目标行的所有祖先
+ 目标行的子节点

可以在 Group 按钮上点击右键来重命名该 Group：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125051575/1cc4601438913ee4653ee5f435e3d57c/group_view_3.png)

同一个时间线行支持添加到多个 Group View 中：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125051969/aff52e14c39fdaef610b7b651512219d/group_view_4.png)

#### 7.3.8. Timeline View 支持报告级选项设置
除了`Tools`->`Options`的全局选项外，Timeline View 还支持报告级的选项设置，这些选项有如下特点：

1. 只针对当前报告生效
2. 不记忆，重启 Asight 后复位
3. 如果某个选项在全局选项中也存在，则会覆盖全局选项
4. 立即生效，不用重新打开报告

可以通过 Timeline View 的搜索框左侧`Options`按钮打开`Options Dialog`：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125064536/2dee237f6fd342e06dcb485a99770374/options_dialog_3.png)

打开后如图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125064806/7b3953e4ae7247f9af1fc8d7cfe20e85/options_dialog_4.png)

支持的选项有：

- Show correlation arrows：控制是否显示选中时间线的箭头，默认为 Yes  
- Show CPU sampling rows：控制是否显示 CPU sampling 的相关行，默认为 Yes  
- Show PPU metrics rows：控制是否显示 PPU metrics 的相关行，默认为 Yes  
- Show NIC metrics rows：控制是否显示 NIC metrics 的相关行，默认为 Yes  
- Show non-HGGC process and thread rows：控制是否显示没有 HGGC 信息的线程行和进程行，默认为 Yes  
- Show graph node based HGTX timelines：控制是否显示基于 graph node 映射的 HGTX 时间线，默认为 Yes  
- Unified memory usage scale：控制是否按统一比例显示内存用量类型的时间线，默认值与全局选项相同  
- Unified metric value scale：控制是否按统一比例显示 PPU/CPU metrics，默认值与全局选项相同  
- Color HGGC kernels：控制是否将不同的 kernel 显示成不同的颜色，默认值与全局选项相同  
- Color CPU Usage by Thread：控制是否将 CPU 时间线按线程名称上色，默认值与全局选项相同  
- HGGC API name mode：控制是否将 host 端的 HGGC launch API 显示为对应 kernel 的名字，默认值与全局选项相同  

当报告级选项生效时，`Options`按钮中会显示一个圆点：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125038417/3a7c66a9a4dd87459dda5f1b610552a9/color_hggc_kernels_1.png)

<a id="n44Ub"></a>

#### 7.3.9. Events View
Events View 支持以列表的形式显示事件，支持事件的排序，搜索以及过滤，支持与 Timeline 的相互跳转。

可以在 Timeline 中通过`右键菜单`->`Show in Events View`(快捷键为 Shift+双击鼠标左键）将特定节点的事件在 Events View 中显示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125075412/b88045017d385c70829fb1da44cebd24/show_in_events_view_1.png)

选中节点的子节点事件也会在 Events View 中显示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125075854/3a16b1dd2e0c96a093a99e108ff55702/show_in_events_view_2.png)

1. 选择显示模式。如果是有嵌套关系的 HGTX 事件，可选择以树形或平铺列表的方式显示。
2. 选择搜索功能按 Name/Description 进行搜索
3. 高级搜索选项
4. 搜索栏
5. Events 表格
6. 选中 item 的 description，与 item 的 tooltip 相同

表格中显示的列有：

+ 序号
+ Name
+ Start
+ Duration
+ TID

如果 Events View 显示的是 PPU 相关节点，还会显示 PPU，Context，Stream 列：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125074452/84829a59a1b317dcd707a6bed3194dd7/select_all_1.png)

在表格中选中事件后，可以通过`右键菜单`->`Copy`功能将选中项导出，支持利用 Shfit/Ctrl 多选，也可以通过`右键菜单`->`Select All`功能全选。

此外，若需要将所有事件直接导出到 CSV 文件，则可以使用`右键菜单`->`Export All to CSV`功能。

点击列头，支持按升序或降序进行排序。

##### 7.3.9.1. 搜索
Events View 支持搜索功能：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125046360/dd013d282889a15ab20f3f0ef07e659e/export_all_to_csv_1.png)

支持两种搜索方式：

1. 按 Name 搜索
2. 按 Description 搜索

支持两种模式：

1. 搜索
2. 过滤

搜索的结果如图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125045402/6a65dca4b0bc249c026c7bb350f1ff59/events_view_1.png)

1. 搜索结果会高亮显示
2. 显示匹配项数目
3. 左右跳转按钮，支持跳转至临近的匹配项
4. 在 Timeline View 中高亮搜索结果

重新 Show in Events View 后，搜索栏和搜索结果将重置。

Events View 还支持高级搜索功能，点击放大镜旁的三角按钮，会出现高级搜索选项：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125037903/0a5b19af625567340b3534ce7194a76a/case_sensitive_1.png)

+ Case Sensitive：关键字是否大小写敏感
+ Show Only Matched：是否仅显示匹配项，如果勾选，Events View 会仅显示匹配项，不匹配的项目被隐藏

##### 7.3.9.2. 跳转到目标行
在 Events View 中可以使用快捷键`Ctrl + G`跳转到目标行，只需输入行号，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125038160/3f41cfec4ce0c8dcb8f2813a09ed7d4d/case_sensitive_2.png)

##### 7.3.9.3. 跳转至 Timeline
Events View 支持与 Timeline 的相互跳转：

+ 当 Timeline Item 在 Events View 中显示时，在 Timeline 中双击 item，Events View 会跳转至该 item
+ 在 Events View 双击 item，Timeline 中对应的 item 会被高亮

也可以通过右键菜单进行跳转：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125045798/fded581a2d0af384f2b792b78b5bcc20/events_view_context_menu_1.png)

+ Highlight Selected on Timeline：在 Timeline 中高亮该 item，与双击 item 行为相同
+ Show Current on Timeline：在 Timeline 中高亮该 item，并且放大该 item 至整个屏幕

##### 7.3.9.4. 使用时间范围过滤事件
与时间范围配合使用，Events View 可以仅显示特定时间范围内的事件，首先在 Timeline 中选取一个时间范围，通过`右键菜单`->`Filter and Zoom in`将事件过滤，此时 Events View 中仅显示当前时间范围内的事件：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125075091/5fdadb44311e1b4d248c771525f9ad0e/show_current_on_timeline_1.png)
<a id="WGnXs"></a>

#### 7.3.10. Function View
Asight Systems 提供 Function View，用于分析所有函数的 CPU 使用情况。Function View 的 CPU 使用数据支持以 Top-Down、Bottom-Up、Flat 三种表格以及 Flame Graph（火焰图）、Icicle Graph（冰川图）两种图的方式呈现。支持排序、搜索、过滤功能，帮助迅速找到热点函数。要使用 Function View，需在采集报告时开启 Backtrace 采样，请参见[采集 API 调用栈](#PP2Xv)。

##### 7.3.10.1. 火焰图和冰川图
火焰图可以快速找到 CPU 消耗最多的一支调用栈，冰川图则可以快速定位到 CPU 消耗最多的函数以及该函数的调用者。通过火焰图和冰川图能够从整体概览所有函数的耗时长短，并快速定位到热点函数和相应调用栈。

火焰图效果如下：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125047796/53a1647f98cfa4b406d3a906d3388773/function_view_1.png)

冰川图效果如下：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125048137/f345e556be8ed83646f66788f215561a/function_view_2.png)

火焰图和冰川图的主要功能：

+ 图中每个矩形代表一个函数，矩形的宽度表示该函数消耗的 CPU 时间，矩形的颜色用来区分不同的模块。x 轴不代表函数在时间上的先后顺序，y 轴表示调用栈的深度，下方是调用者，上方是被调用者。
+ 鼠标悬放在函数上，可以在弹出的 tooltip 或者图的顶部看到函数的详细 CPU 消耗、函数所属的模块名称等。
+ 鼠标点击函数可以将其放大，查看其详细的调用者和被调用者。
+ 在函数上使用鼠标右键菜单，可以拷贝函数的 function name、module name。
+ 支持搜索函数，搜索结果将在图中高亮显示。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125086689/dd532f3ecd65e72573aa56225c294a7d/tooltip_cpu_1.png)

##### 7.3.10.2. Function 表格
Function 表格包括 Top-Down、Bottom-Up、Flat 三种，主要功能分布如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125048560/97bb06fa660f47da8e9c09a859912b2d/function_view_3.png)

1. Tab 栏，可以切换到其他子页面
2. 选择要分析的目标进程
3. 选择要分析的目标线程，当进程中只有一个线程时，该组合框不显示
4. 搜索框
5. Filter Dialog

Function 表格显示的信息有：

+ Symbol Name：函数名
+ Self：函数本身耗时占比
+ Total：函数本身及其调用的子函数的耗时占比
+ Module Name：函数从属的模块名

Function 表格支持排序功能，点击列头，支持按升序或降序进行排序。

Function 表格支持搜索功能，同时搜索函数的 Symbol Name 和 Module Name，并且支持 Case Sensitive 选项，搜索结果跟 Events View 类似，包含以下信息：

1. 搜索结果会高亮显示
2. 显示匹配项数目
3. 左右跳转按钮，支持跳转至临近的匹配项

Function 表格支持过滤功能，包括：

+ 隐藏时间占比低于指定阈值的函数（默认不隐藏）
+ 可指定时间占比显示的小数位数

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125048931/85311f39151efba3a5e6ca75a4b18a57/function_view_4.png)

Function 表格支持以下右键菜单功能：

+ Expand：展开选中行，及其所有子行
+ Collapse：折叠选中行，及其所有子行
+ Expand All：展开表格中的所有行及其子行
+ Collapse All：折叠表格中的所有行及其子行
+ Copy：复制所选的 function 内容到剪贴板
+ Export All to CSV：导出表格的所有 functions（包含被隐藏的行）到 CSV 文件

###### 7.3.10.2.1. Top-Down 表

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125046045/645011bb140292acd71b661a6059ec25/expand_all_1.png)

以函数耗时的 Top-Down 模式举例，Top-Down View 中的函数按照调用关系，从顶层到底层按照树状展示。上图中 DoProcessLoop 和 ProfilerStart 函数都在 main 函数中调用，所以以上两个函数都属于 main 节点。

main 函数的 self 值为 0，说明 main 函数中本身的逻辑非常简单；total 值为 90.24%，说明主要耗时在 main 函数所调用的函数中。

**注意：**
调用栈的深度由采集时指定的调用栈最大回溯深度决定。如果函数的调用深度超过了最大回溯深度，则以此时回溯到的最顶层函数作为根节点。
如果无法获取符号的名字，则显示函数的地址。

###### 7.3.10.2.2. Bottom-Up 表

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125049284/d7e187f165428662b5432b911ed92c99/function_view_5.png)

以函数耗时的 Bottom-Up 模式举例，Bottom-Up View 的显示方式与 Top-Down View 相反，以最深调用的函数为根节点，最浅调用的函数为叶节点，例如上图中 main 函数在叶节点中。Bottom-Up View 不显示 Total 列。

###### 7.3.10.2.3. Flat 表

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125049651/4927c6e007a40bd4f0ec48555509d1b2/function_view_6.png)

以函数耗时的 Flat 模式举例，Flat View 以平铺的形式显示所有的函数，在不关心调用关系的场景下，可迅速找到 Self，Total 耗时最多的函数

<a id="gY4WW"></a>

#### 7.3.11. Device Memory View
Asight Systems 提供 Device Memory View，用于分析所有函数的设备内存申请释放情况。

Device Memory View 支持 4 种查看模式，在下拉框中可以切换：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125088939/cadb13aa95697185af09c3da6b2399ff/unreleased_malloc_size_1.png)

+ Unreleased Malloc Size：查看各函数的申请但未释放的内存大小
+ Total Malloc Size：查看各函数申请的内存大小
+ Unreleased Malloc Count：查看各函数的内存申请但未释放的次数
+ Total Malloc Count：查看各函数的内存申请次数

Device Memory View 同样支持火焰图、冰川图，以及 Top-Down、Bottom-Up、Flat 三种表格，并且支持排序、搜索、过滤功能，帮助迅速找到热点函数。要使用 Device Memory View，需在采集报告时按需开启设备内存采样，参考[分析 PPU 内存使用情况](#VlQaR)。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125089163/22efb9dbb175aa794d40f68dfe3f5928/unreleased_malloc_size_2.png)

表格显示的信息有：

+ Symbol Name：函数名
+ Self：函数本身的设备内存申请/释放大小（正值为申请，并显示为红色，负值为释放，并显示为蓝色）
+ Total：函数本身及其调用的子函数的设备内存申请/释放大小
+ Module Name：函数从属的模块名

<a id="k5lmj"></a>

#### 7.3.12. Host Pinned Memory View
Asight Systems 提供 Host Pinned Memory View，用于分析所有函数的锁页内存申请释放大小。跟 Device Memory View 一样支持 4 种查看模式，支持火焰图、冰川图，以及 Top-Down、Bottom-Up、Flat 三种表格，并且支持排序、搜索、过滤功能，帮助迅速找到热点函数。要使用 Host Pinned Memory View，需在采集报告时按需开启锁页内存采样，参考[分析 Pinned 内存使用情况](#m0dAK)。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125062716/e3f63277fd606e4f52305c4f8abbf6e9/module_name_1.png)

#### 7.3.13. Heap Memory View
Asight Systems 提供 Heap Memory View，用于分析函数的 CPU 侧动态分配内存 / 堆内存的使用情况。跟 Device Memory View 一样支持 4 种查看模式，支持火焰图、冰川图，以及 Top-Down、Bottom-Up、Flat 三种表格，并且支持排序、搜索、过滤功能，帮助迅速找到热点函数。要使用 Heap Memory View，需在采集报告时按需开启 heap 内存采样，参考[Heap 内存使用跟踪](#Tekvl)。点击 Timeline View 中的`Heap memory usage`行的时间块，可查看进程截止到该时刻的内存使用信息。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125056167/69b16c871b29ad9f4185b52ac4a0894a/heap_memory_usage_3.png)

### 7.4. Analysis Summary Page
Analysis Summary 以多个表格的形式展示了报告的摘要信息，可以查看生成报告时的采集选项，表格中的信息支持选择复制。

在 Page 切换列表中切换到 Analysis Summary View：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125056542/1ca97a7f6ea03c389e04ca8fb9acdb27/heap_memory_view_1.png)

Analysis Summary View 如图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125056820/c4c8128ada38f5c2baa66fbd5aa43256/heap_memory_view_2.png)

Analysis Summary View 的信息分为以下部分：

+ Launch Settings
+ Session Info
+ Processes
+ Threads
+ Environment
+ Device Attributes

#### 7.4.1. Launch Settings
Launch Settings 列表显示了采集报告时的配置：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124995973/5f068cb5441859517b5729ce1972ffd7/environment_1.png)

| 项目 | 描述 |
| --- | --- |
| Collect HGGC trace | 是否采集 HGGC 信息 |
| Collect HGGC backtraces | 是否采集 HGGC Backtrace |
| Backtracing algorithm | Backtrace 的采集算法 |
| Collect OSRT trace | 是否采集 OSRT 信息 |
| Collect OSRT backtraces | 是否采集 OSRT Backtrace |
| Collect HGTX trace | 是否采集 HGTX 信息 |
| Collect acDNN trace | 是否采集 acDNN 信息 |
| Collect acBLAS trace | 是否采集 acBLAS 信息 |
| Collect CPU samples | 是否进行 CPU 采样 |
| Delay | 采集开始前的延迟时间 |

#### 7.4.2. Session Info
Session Info 列表显示了采集报告的 Session 信息：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125019664/f68ac9de8ef97767666081f3183879bf/session_info_1.png)

| 项目 | 描述 |
| --- | --- |
| Report File | 生成的报告路径 |
| Report Size | 报告尺寸 |
| Tracing Started Time | 报告采集的时间 |
| Target Name | 目标机名 |
| Target OS | 目标机操作系统 |
| Platform | 操作系统平台 |
| Target Architecture | 目标机架构 |
| Target Processor | 目标机处理器 |
| Asight Systems Target | asys 命令行版本 |
| CLI Command Used | 调用的 asys 命令行工具参数 |

#### 7.4.3. 其他信息
Analysis Summary View 还展示了一些表格：

| 项目 | 描述 |
| --- | --- |
| Processes | 报告中的进程信息 |
| Threads | 报告中的线程信息 |
| Environment | PPU 程序的环境变量 |
| Device Attributes | PPU 的设备属性 |

### 7.5. Diagnostics Summary Page
此页面用于查看本报告的所有诊断信息，包括信息的级别、来源、进程 ID、事件发生的相对时间、描述。在 Timeline View 的右上方提供诊断信息的累计概况，点击可跳转至 Diagnostics Summary View。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125042509/929324f8022e15ca93e20453eeef91c8/diagnostics_summary_1.png)

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125042746/e37958e18c641cc3c5d520aaea494663/diagnostics_summary_2.png)

### 7.6. Files Page
Files 页面支持查看报告中保存的应用程序日志文件，方便问题的定位。目前可以查看 stdout、stderr、python functions trace json 这三种日志。如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125046683/d434b4ee9e7a14c978e20ab42ba2d3f6/files_1.png)

**注意：**
asys 命令行默认保存 stdout、stderr 到报告。python functions trace json 需要[使用 json 指定采集](#pStlT)时才显示 json 内容。

<a id="ADyNl"></a>

### 7.7. Options
Asight Systems GUI 提供了 Options Dialog，允许对 GUI 进行定制。

在菜单栏的`Tools`菜单中选择`Options...`选项来启动`Options Dialog`，如下图所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125065130/e4b0ea2286fe5a8eeb6e57924edccf12/options_dialog_5.png)

Options Dialog 中有两个 Tab 与 Asight Systems 有关：

+ Environment
+ Systems Profile

被修改的选项以粗体显示，点击 Restore Defaults 按钮恢复为默认状态。

#### 7.7.1. Environment
Environment 页面中包含了 Asight Systems GUI 的整体环境设置：

| 选项 | 功能 |
| --- | --- |
| Color Theme | 切换主题，支持 Light，Dark 两种主题 |
| General Font | 改变 GUI 中的字体 |
| Documents Folder | section 和 rule 文件所在目录 |
| Show tips | 是否显示全局提示信息 |

#### 7.7.2. Systems Profile
Profile 页面中的选项指定了 asys 报告的显示行为：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125077018/efb49d84c5b2c45b45564ec53fd78499/systems_profile_1.png)

| 选项 | 功能 |
| --- | --- |
| Default Report Page | 打开报告后显示的页面，默认值为 Auto，由 Asight 决定显示的页面 |
| Timeline Mode | 控制 PPU 信息与 CPU 信息的显示位置<br>默认值为 GPU Rows on Top |
| Rename HGGC kernels by HGTX | 控制 kernel 节点的组织形式是否按 kernel 所属的 HGTX 分类<br>默认值为 No |
| Color HGGC Kernels | 控制 Timeline View 中不同的 kernel 是否以不同的颜色显示<br>默认值为 No |
| HGGC API Name Mode | 开启后 HGGC launch API 会以其对应的 kernel 名字显示<br>默认值为 Host API name |
| HGGC Dependency Display Mode | 控制 PPU activity 依赖关系计算的起点是从报告起始时间开始， <br>还是从其对应的 Host API 起始时间开始。<br>默认值为 Effective，从 Host API 起始时间开始计算 |
| Group Small Streams into Others | 是否将时间占比小的 stream 合并为 other streams 显示<br>默认值为 Yes |
| Compact Single-Child PPU Nodes | 开启后会合并显示某些 PPU 节点。例如当 Device 节点下只有一个 Context 节点时，<br>则不显示 Context 节点，Device 节点下直接显示 Context 节点的子节点；Stream 节点同理。<br>默认值为 Yes |
| Unified memory usage scale | 控制是否按统一比例显示内存用量类型的时间线<br>默认值为 Yes |
| Unified metric value scale | 控制是否按统一比例显示 PPU/CPU metrics<br>默认值为 Yes |
| Color CPU usage by thread | 控制是否将 CPU 时间线按线程名称上色<br>默认值为 No |
| Bookmark management mode | 控制 bookmark 的管理模式，模式分别为：自动保存与加载； 仅自动加载；不保存也不加载<br>默认值为自动保存与加载 |
| Maximum Callstack Display Depth | 最大调用栈显示深度 |
| Maximum Timeline Row Display Depth | 最大 Timeline Row 显示深度，超过最大深度的行将被折叠<br>可以点击![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125077369/c81ef8bc9a936d6bfc1f2e386b088c3e/systems_profile_2.png)按钮展开查看 |

## 8. 命令生成助手

命令助手是 Asight Systems GUI 内置的可视化 asys 命令生成工具，可以通过图形化界面配置采集参数，自动生成对应的 asys 命令行。

点击 Asight Systems GUI 菜单栏中的 `Tools` -> `asys Command Helper` 打开 asys 的命令生成助手：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125032106/fd00cfd377d3f95db206964a80e6c792/asys_command_helper_1.png)

命令生成助手的界面如下所示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125032491/8c3b43ed3da536550653c6a523c5c667/asys_command_helper_2.png)

1. 命令生成助手菜单栏，根据参数的类型分类
2. 参数配置区， 配置跟踪选项
3. 命令生成区，显示生成的命令

### 8.1. 命令行助手菜单栏
通过菜单栏的分类，可快速找到需要配置的采集选项：

| 菜单栏 | 含义 |
| --- | --- |
| Target Application | 配置与目标程序有关的选项，如目标程序路径和参数、输出报告的路径、环境变量等 |
| Trace Control | 配置与控制采集过程有关的选项，如事件触发跟踪采集、采集时间控制、长时间采集报告文件轮转 |
| PPU | 配置 PPU 活动跟踪选项，如 HGGC、PPU Metrics、ACDNN、ACBLAS 等 |
| CPU | 配置 CPU 活动跟踪选项，采集应用程序在 CPU 上的执行情况、CPU Metrics 等 |
| Memory | 配置 PPU 内存、Host 内存、Heap 内存、Pinned 内存的使用情况跟踪 |
| Network | 配置 RDMA 网卡的运行指标采集 |
| Python | 配置 Python 跟踪，如 Python 调用栈采集、Python 函数采集等 |

### 8.2. 参数配置区
对于配置的采集选项，选项前面有一些对选项的文字描述，有些选项的上方会有示意图描述，下面灰色斜体的部分为对选项的补充描述。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125077643/e22ac70c92c0f17ab5986ccf8985ec98/systems_profile_3.png)

#### 8.2.1. 输入限制
对于一些输入框，会限制输入的内容与格式。例如 PPU device ID 的输入框中仅允许输入数字和逗号：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125034199/a8a6945ea267b04aafe83d809ba8062c/asys_input_limits_1.png)

#### 8.2.2. 错误提示
部分选项开启后需要填入参数，参数为空时会有红色的错误提示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125033311/841e8a34ee1fccd420f16b1db914da88/asys_error_hints_1.png)

部分选项是互斥的，无法同时开启。同时开启的时候， 父选项上会有错误提示，同时选项自身会被置灰：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125033696/d9da49a5c1bee23f29586341a6fc96ec/asys_error_hints_2.png)

#### 8.2.3. 跳转到帮助文档
部分选项上有帮助图标，点击帮助图标可以跳转到文档对应的位置，帮助理解选项的含义。

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125033950/5cb24ee89d0f5b829ff85bf86d628598/asys_help_doc_jump_1.png)

#### 8.2.4. Metrics 选择对话框
部分选项中需要填入 Metrics，命令生成助手提供了 Metrics 选择对话框，点击如下按钮进入：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125012935/18574e0f2e76ea0e7334dedfdce589b1/metrics_1.png)

点击后打开 Metrics 选择对话框：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125013219/d0ddaf6f3edbf06dd651ce13c6e1b1d6/metrics_2.png)

在上述对话框中可以选择不同的计算能力，加载不同的 Metrics 列表。一次采集的 Metrics 数量是有限的，如果超过了数量限制，会给出错误提示，同时 OK 按钮也无法选中。

### 8.3. 命令展示区
在上述参数配置发生改变时，会同步生成 asys 命令，在下方的命令展示区显示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124996541/dd839f1dffacd7753bc3e4a0106ed369/format_as_multiline_1.png)

勾选 `Format as multi-line` 复选框，可以将命令行格式化成多行显示：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124996766/1fcf96d4ed8e736dd595077c3a2b0514/format_as_multiline_2.png)

点击 `Copy` 按钮可以复制命令到剪贴板，粘贴到终端中运行即可对目标程序进行性能分析数据采集。

## 9. PPU 运行环境检查

Asight Systems 提供 PPU 环境检查功能，用于检查当前系统中 PPU 相关环境是否配置正确。命令如下：

```bash
asys status [--ppu-env] [app] [app args]
```

此命令提供两种检查模式：`静态环境检查` 和 `运行时环境检查`。

### 9.1. 静态环境检查
```bash
asys status --ppu-env
```

静态环境检查不需要指定目标程序，可独立运行，仅检查 `asys status` 命令所在环境。

示例输出信息如下：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125036014/73570bf8cefddeeb0bf7faf3f6a168c4/asys_status_1.png)

### 9.2. 运行时环境检查
```bash
asys status --ppu-env <app> <app args>
```

运行时环境检查需要指定一个目标应用程序。`asys status` 会启动目标应用程序，并注入检查库到目标应用程序进程中采集环境信息。可检查出目标应用程序在运行过程中修改 PPU 环境信息引起的 PPU 程序运行异常问题（如使用 shell 脚本启动的模型程序等）。

运行时环境检查示例输出信息如下：

![](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125036429/b5bcf9abb07f569330218ca557e1852b/asys_status_2.png)

### 9.3. 检查项说明
PPU 环境检查工具提供了 8 类数据的检查功能：

1. SDK 有效性与路径检查（静态、运行时）
2. SDK 软件栈版本匹配检查（静态、运行时）
3. PPU 设备有效性检查（静态、运行时）
4. CUDA 残留文件检查（静态、运行时）
5. Docker 环境检查（静态、运行时）
6. 黑名单库文件检查（静态、运行时）
7. 目标应用加载库中的 SDK 库文件有效性检查（运行时）
8. 目标应用的 shell log 信息检查（运行时）

<a id="faq"></a>

## 10. 常见问题

### 10.1. 减小报告尺寸
推荐将采集的报告尺寸控制在 200MB 以内，可以采用以下办法减小报告尺寸：

+ 关闭 CPU 采样：使用选项`-s none`
+ 延迟启动采集，控制采样时间：使用`-y`和`-d`
+ 通过事件触发采集：使用`-c`指定触发方式
+ 通过`--trace-rotation`选项配合`--duration`选项进行报告文件轮转采集
+ 采集类似 mpirun 方式启动应用时，使用`--process-rank-include`指定只采集部分 Rank 进程的跟踪数据

对于已采集到的大尺寸报告，可在 Asight Systems GUI 中通过`File` -> `Open Advanced...`自定义查看报告的部分内容：

+ 约束加载部分报告的比例（如只加载前 50%的跟踪数据）
+ 不解析指定类型的跟踪数据（如忽略 CPU 调度信息跟踪数据）

**注意：**
使用加载部分报告功能打开配置`capture range`的报告文件时，或者打开采集时间较短的报告文件时，若部分加载比例较低，可能打开报告后无跟踪数据，请尝试扩大部分加载的比例。

### 10.2. 启动应用后采集多份报告
在应用启动后，可通过以下方法采集多份报告：

可通过`asys launch`启动应用，随后通过`asys start/stop`启动采集，例如：

```bash
asys launch -t hggc cuda_test
asys start
asys stop
asys start
asys stop
```

若应用程序中包含多个 capture range 的插桩，可以通过`--capture-range-end repeat-shutdown:N`多次触发采集，例如通过 capture range 事件触发生成 3 个报告文件：

```bash
asys profile --capture-range-end repeat-shutdown:3 python test_linear.py 
```

可通过`asys profile`子命令的`--duration`和`--trace-rotation`选项，通过报告文件轮转的方式，周期地生成报告文件，例如每 30 秒生成一个报告文件，保留最近的 3 份报告文件：

```bash
asys profile --duration 30 --trace-rotation 3 --output test_report_%t python test_linear.py 
```

可通过`asys attach`子命令通过多次附着到目标应用的方式，采集多份报告，例如多次采集 PID 为 94644 的进程跟踪数据，可多次执行命令：

```bash
asys attach -o report_%i 94644
```

### 10.3. 通过事件触发跟踪采集
asys 支持以事件触发的方式进行采集，例如：

```bash
asys profile -c hgtx -p msg python test_linear.py 
```

事件支持 NVTX 与 profilerStart/Stop 两种标记，下面给出了一些添加事件标记的例子：

**PyTorch 框架中增加 NVTX 范围信息：**

```python
import torch.cuda.nvtx as nvtx

nvtx.range_push("msg")
...
nvtx.range_pop()
```

**C/C++应用增加 NVTX 标记：**

```cpp
#include <nvtx3/nvToolsExt.h>

nvtxRangePushA("msg");
...
nvtxRangePop();
```

**PyTorch 框架中增加 profilerStart/Stop 标记：**

```python
torch.cuda.cudart().cudaProfilerStart()
...
torch.cuda.cudart().cudaProfilerStop()
```

### 10.4. 采集 OSRT 信息查看 CPU 线程挂起的原因
通过采集 OSRT 信息可以查看 CPU 线程挂起的原因。

指定采集 OSRT 跟踪：跟踪选项-t 参数增加 osrt

+ 可通过--osrt-threshold 选项指定采集门限
+ 可通过--osrt-backtrace-threshold 指定调用栈回溯门限

### 10.5. 使用 asys 采集 mpirun 等多机多卡应用
对于需要在多个计算节点的多个 PPU 上运行的应用程序，运行时常常通过`mpirun`/`deepspeed`等方式进行启动，asys 采集此类应用程序时，可通过以下方式采集跟踪数据，以`mpirun`应用为例：

+ 使用多节点跟踪采集模式（推荐）：
    - 通过 asys 启动`mpirun`应用，通过`--multi-node-mode mpirun`使能多节点跟踪采集模式，每个节点生成一份报告文件
+ 不使用多节点采集模式：
    - 单节点方式：通过 asys 启动`mpirun`应用，本节点的所有进程跟踪数据记录到一份报告文件，其他节点不采集跟踪数据
    - 多节点方式：通过`mpirun`应用启动 asys，每个节点的每个应用（通常对应一个 Rank / 一个 PPU）跟踪数据记录到一个报告文件

单节点方式和多节点方式的使用方法举例如下，采集单节点跟踪信息，汇总生成一份报告文件：

```bash
asys profile mpirun -np 4 cuda_test
```

多个节点采集，每个应用程序生成一份报告文件，可使用`-o`选项`%h`和`%p`根据 host name 和 PID 生成报告名称，避免报告重名问题。可使用`-o`选项通过环境变量生成报告名称，例如通过`mpirun`启动的应用程序，`-o`选项可通过`%q{OMPI_COMM_WORLD_RANK}`在报告名称中包含 Rank ID。

```bash
mpirun -np 4 asys profile -o report_%h_%p cuda_test
```

在使用单节点方式采集跟踪数据时，由于所有进程的跟踪数据记录到同一份报告文件，跟踪数据量可能巨大，若希望只采集部分进程的跟踪数据，可通过`--process-rank-include`选项指定需要采集的进程的 Rank ID，多个 Rank ID 之间通过逗号`,`拼接，例如只采集 Rank ID 为`0`和`2`的进程的跟踪数据：

```bash
asys profile --process-rank-include 0,2 mpirun -np 4 cuda_test
```

可通过`--process-ppu-include`选项指定采集的 PPU 设备 ID 列表，多个 PPU 设备 ID 之间通过逗号`,`拼接，例如只采集使用 PPU 设备 ID 为`0`和`2`的进程的跟踪数据：

```bash
asys profile --process-ppu-include 0,2 mpirun -np 4 cuda_test
```

### 10.6. 采集包含 fork 的应用程序
若发现采集的应用程序的子进程跟踪缺失，可能由于应用程序调用了`fork`函数，且`fork`后没有执行`exec`启动其他应用程序，asys 默认在`fork`后`exec`前不采集跟踪数据，若希望采集`fork`后子进程的跟踪数据，需要通过`--trace-fork-before-exec`使能此场景的跟踪采集：

```bash
asys profile --trace-fork-before-exec true cuda_test
```

### 10.7. 没有采集到设备内存使用信息
应用程序可能仅在初始化阶段申请设备内存，后续运行过程中无内存申请、释放动作，请检查 asys 选项：

+ 若存在`-c`或`--capture-range`选项，或存在`-y`或`--delay`选项，尝试删除以抓取启动阶段跟踪数据
+ 若使用`asys start`或者`asys attach`方式在应用运行过程中采集，尝试更换为`asys profile`方式采集包含应用程序初始化阶段的跟踪数据

### 10.8. 安装 SSH 服务
Ubuntu 操作系统安装 SSH 服务步骤参考如下：

```bash
# install openssh service
sudo apt-get update
sudo apt-get install openssh-server

# edit ssh service config to modify SSH port / environment / authentication
# vi /etc/ssh/sshd_config

# restart ssh service
sudo service ssh restart
```

Centos 操作系统安装 SSH 服务步骤参考如下：

```bash
# install openssh service
sudo yum install openssh-server

# edit ssh service config to modify SSH port / environment / authentication
# vi /etc/ssh/sshd_config

# restart ssh service
sudo systemctl restart sshd.service
```

使用 Docker 场景需配置转发 Docker 内 SSH 端口到主机端口，以 SSH 使用 22 端口为例，若转发到主机的 50022 端口，需在 Docker 启动命令中添加如下选项：

```bash
--expose=22 -p 50022:22
```

### 10.9. 清理 asys 运行环境
若发现 asys 运行异常，请尝试如下步骤清理 asys 运行环境：

+ 运行`asys sessions list`检查是否有长时间未结束的 session，可通过`asys shutdown --session xxx`命令停止相关 session
+ 运行`ps -aux | grep traced | grep -v grep |  awk '{print $2}' | xargs kill`停止 asys 相关后台服务后，再次尝试运行 asys
+ 重新安装 T-Head SAIL SDK

### 10.10. asys 采集完成应用未停止
在指定`--duration`或者`--capture-range`选项时，在采集停止时，asys 默认发送`SIGTERM`停止应用，若应用程序中包含`SIGTERM`的处理且未及时停止，可能导致应用程序 asys 采集结束后无法停止，请尝试：

+ 指定选项`--kill 9`，asys 将发送不可拦截的信号`SIGKILL`停止应用

### 10.11. 采集 Tensorflow Eager 模式应用跟踪不完整
若发现 asys 采集 Tensorflow Eager 模式应用的跟踪数据不完整，可添加选项` --flush-on-context-synchronize true`，使能 asys 在每次 HGGC context / stream 同步时保存数据，配置后 asys 采集性能开销将会增大：

```bash
asys profile --flush-on-context-synchronize true cuda_test
```

### 10.12. Linux 上开启 Timeline View 的 Alt 平移快捷键
在 Linux 平台上，如果 Alt + 滚轮被全局缩放功能占用，可以通过以下办法关闭全局缩放，释放 Alt 键：

在终端中，执行：

```bash
xfconf-query -c xfwm4 -p /general/zoom_desktop -s false
```

可以用`xfconf-query -c xfwm4 -p /general/zoom_desktop`来检查其值是否为 false

### 10.13. 采集 Heap 内存使用量和进程内存占用量不同
asys 支持通过如下选项采集进程在 CPU 侧的内存使用：

+ `--heap-memory-usage`：采集进程的`动态分配内存使用量`，比如通过`malloc` / `new`等方式动态分配的内存
+ `--host-memory-sampling`：采样进程的`实际物理内存使用量`，比如通过 Linux 的`top`命令查看进程的`RES`列内存占用大小

asys 采集到的进程的`动态分配内存使用量`和`实际物理内存使用量`受到如下因素影响，内存使用量可能有较大差异：

+ 受到 C 库内存缓存优化机制以及内存碎片化的影响，内存可能被进程持有而不是被操作系统回收，导致`实际物理内存使用量`显著高于`动态分配内存使用量`
+ 受到操作系统内存分页机制和惰性内存分配策略影响，通过`malloc`等方式分配但未访问的内存不会分配实际物理内存，导致`实际物理内存使用量`显著低于`动态分配内存使用量`

### 10.14. 没有采集到使用 Ray 框架应用的跟踪数据
asys 的默认采集模式不支持采集 Ray 框架应用的跟踪数据，需要通过`--multi-node-mode ray`选项使能多节点跟踪采集模式，每个节点生成一份报告文件：

```bash
asys profile --multi-node-mode ray -f true -o demo_vllm bash eval_llm_infer.sh
```

### 10.15. CUDA GPU 环境使用 asys 采集跟踪
asys 支持在 CUDA GPU 环境采集跟踪，使用方式和在 PPU 环境采集跟踪相同，大部分 asys 特性均可在 CUDA GPU 环境生效，例如：

+ 支持映射 CUDA graph 创建阶段 NVTX 到 CUDA graph 执行阶段
+ 支持采集 CUDA graph 节点在 GPU 上执行信息，并汇总显示 CUDA graph 整体生命周期
+ 支持 python function trace 采集所有 python 函数的执行信息
+ 支持 attach 方式采集跟踪数据

在 CUDA GPU 环境中，可以单独安装 asight 工具，或者使用 T-Head SAIL SDK 中包含的 asight 工具，单独安装 asight 工具的方法为：

1. 前往 PPU artifactory 页面下载 asight 安装包
2. 解压 asight 安装包，以`asight_ubuntu2404.tar.gz`举例，执行`tar -xf asight_ubuntu2404.tar.gz`
3. 进入解压生成的`asight`文件夹，执行`source envsetup.sh`，即可开始使用 asys 工具

使用 SDK 中的 asight 工具的方法为：

1. 进入 SDK 下`asight`目录，执行`source envsetup.sh`，即可开始使用 asys 工具
2. 注意通过`source`执行的并非`SDK`文件夹根目录下的`envsetup.sh`，请注意分辨

可分别采集 GPU 和 PPU 环境应用的 asysrep 报告，通过`asys compare`输出比较结果，例如：

```bash
asys compare gpu_report.asysrep ppu_report.asysrep
```

**注意：**
在采集 asysrep 报告前，建议使能 PPU 算子 HGTX range 标注相关功能：

1. 执行`export PPU_LIB_PERF_INSTRUMENT=1`配置环境变量，使能基础框架 PPU 算子 HGTX range 标注功能
2. asys 添加选项`--pytorch autograd-shapes-hgtx`，使能 pytorch 算子 HGTX range 标注功能

在 CUDA GPU 环境不支持的特性列举如下：

+ video 跟踪
+ pccl 跟踪
+ PPU metrics 采样
+ HGGC memory usage 跟踪
+ CUDA event 参数采集和依赖关系查询

**比赛关联：** 比赛压测取证时优先使用事件触发（`-c hgtx`）与 `--duration` 控制采集窗口，避免报告过大；在 Docker 环境中需按本节说明补齐 `--pid=host --privileged=true` 等参数，否则 CPU 采样与调用栈功能不可用。

## 11. 已知问题

+ asys 采集过程中通过 Ctrl + C 中断采集，采集结束阶段跟踪可能不会写入报告文件
+ asys 不支持在 Linux Kernel 4.1 以下的操作系统中采集 CPU 调用栈信息
+ asys 采集过程可能导致 HGGC stream synchronize 耗时明显变长
+ 应用程序编译需包含`-pthread`选项，否则可能导致 asys 运行崩溃
+ asys attach 可能导致某些应用卡住或者崩溃
+ asys attach 不支持采集在 attach 之前已经实例化的 legacy HGGC graph 相关跟踪信息
+ asys 采集 RDMA 网卡数据吞吐量低于实际值
+ asys 仅支持在 ftrace 时钟设置为 boottime 时钟的环境采集 CPU 线程切换信息
+ asys 采集使能 PyTorch Profiler 功能的应用时，PyTorch Profiler 将无法采集到数据

## 12. 版本说明

### 12.1. 新增改动

#### 12.1.1. asys stats 统计规则增强
  - 新增 `PPU operator type summary` 统计规则，支持分析算子类型占比、列出热点算子
  - 支持 `PPU operator trace` 跟踪导出，导出每算子关联的 PPU 活动跟踪
  - 新增 `PPU kernel summary compare` 对比规则，比较两个报告的 PPU kernel 汇总结果
  - 新增 `HGTX PPU projection summary compare` 对比规则，比较两个报告的 HGTX→PPU 投影汇总结果
  - 新增 `PPU operator summary compare` 对比规则，比较两个报告的算子汇总结果
  - 新增 `PPU operator type summary compare` 对比规则，比较两个报告的算子类型汇总结果

#### 12.1.2. PPU operator summary 统计功能增强
  - 支持识别更多算子
  - 支持自定义算子识别规则

#### 12.1.3. HGTX 关联 PPU 活动统计增强
  - 支持 `range-include` 和 `range-exclude` 选项，指定 HGTX 黑/白名单
  - `PPU 算子统计规则` 支持 `order-by` 选项，指定排序方式

#### 12.1.4. asys stats 命令参数与输出增强
  - 指定统计报告类型时支持对逗号 `,` 和冒号 `:` 使用 `\` 转义
  - 未指定类型时：
    - 默认在终端打印简要统计结果
    - 输出详细统计结果到文件

#### 12.1.4. 统计输出样式优化
  - 调整 `asys stats` 和 `analysis` 子命令 column 样式，使输出结果更加易读
  - 调整 `asys stats` 默认生效的统计规则

#### 12.1.5. PCCL Desynchronization Summary 增强
  - 新增 P90 指标统计，显示大部分 PCCL 通信不同步率优于此门限

#### 12.1.6. 报告对比功能扩展
  - 新增 `asys compare` 子命令，比较两个报告文件
    - 支持显示精简结果
    - 输出详细比较数据到 CSV 文件
  - 新增 `PCCL desynchronization summary compare` 对比规则
  - 新增 `PPU time utilization compare` 对比规则
  - 新增 `PPU Operator Breakdown` 与 `PPU Operator Kernel Breakdown` 统计规则
  - 新增 `Breakdown Compare` 对比规则，比较性能分解结果
  - 新增比较视图（Compare View），可选择任意两个 `.asysrep` 报告对算子、kernel 性能进行对比

#### 12.1.7. PyTorch 算子采集与分析支持
  - 采集 PyTorch 算子跟踪
  - 支持通过 HGTX 标记 PyTorch 算子的执行时间
  - 支持采集 PyTorch 算子参数信息

#### 12.1.8. PPU operator unit test 规则（实验特性）
  - 支持批量生成 PyTorch 算子测试用例代码

#### 12.1.9. Function View 功能增强
  - 支持选择目标线程，仅对该线程进行分析

#### 12.1.10. 时间线显示改进
  - tooltip 支持切换显示完整时间线名字
  - 选中时间线时高亮效果和边框颜色加强
  - 支持统一高度比例尺显示 PPU metrics 与 CPU metrics 时间线
  - 当 HGTX 行层数较多时，标题名字保持居中显示
  - Timeline View 更新 range filter 时，自动同步 Heap Memory View 内容

#### 12.1.11. Events View 优化
  - 默认使用 list 模式，并提升操作性能

#### 12.1.12. asys profile 新增功能
  - 新增 `--stats` 选项，报告生成后打印简要统计结果到终端，并输出详细结果到文件
  - 新增 `--format` 选项支持 `xlsx` 格式输出
