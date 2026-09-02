# 第 4 章 PPU 专项功能 <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [4.1 HGGC 图](#41-hggc-图)
  - [4.1.1 图编程模型概述](#411-图编程模型概述)
  - [4.1.2 创建图](#412-创建图)
  - [4.1.3 图的生命周期管理](#413-图的生命周期管理)
  - [4.1.4 图内存节点](#414-图内存节点)
  - [4.1.5 条件执行](#415-条件执行)
  - [4.1.6 HGGC 用户对象](#416-hggc-用户对象)
  - [4.1.7 使用图 API](#417-使用图-api)
- [4.2 流有序内存分配器](#42-流有序内存分配器)
  - [4.2.1 概述与查询支持](#421-概述与查询支持)
  - [4.2.2 内存管理](#422-内存管理)
  - [4.2.3 内存池管理](#423-内存池管理)
  - [4.2.4 多设备与 IPC 支持](#424-多设备与-ipc-支持)
  - [4.2.5 同步 API 的动作](#425-同步-api-的动作)
  - [4.2.6 附录](#426-附录)
- [4.3 协作组（Cooperative Groups）](#43-协作组cooperative-groups)
  - [4.3.1 简介](#431-简介)
  - [4.3.2 协作组句柄与成员函数](#432-协作组句柄与成员函数)
  - [4.3.3 默认行为/协作组执行](#433-默认行为协作组执行)
  - [4.3.4 创建协作组](#434-创建协作组)
  - [4.3.5 同步](#435-同步)
  - [4.3.6 协作操作](#436-协作操作)
  - [4.3.7 异步数据移动](#437-异步数据移动)
  - [4.3.8 大规模组](#438-大规模组)
- [4.4 延迟加载（Lazy Loading）](#44-延迟加载lazy-loading)
  - [4.4.1 简介](#441-简介)
  - [4.4.2 延迟加载的要求](#442-延迟加载的要求)
  - [4.4.3 使用方法](#443-使用方法)
  - [4.4.4 潜在风险](#444-潜在风险)
- [4.5 异步屏障与流水线](#45-异步屏障与流水线)
  - [4.5.1 初始化](#451-初始化)
  - [4.5.2 屏障的阶段：到达（Arrival）、倒计时（Countdown）、完成（Completion）和重置（Reset）](#452-屏障的阶段到达arrival倒计时countdown完成completion和重置reset)
  - [4.5.3 早期退出](#453-早期退出)
  - [4.5.4 完成函数（Completion Function）](#454-完成函数completion-function)
  - [4.5.5 使用屏障的生产者-消费者模式](#455-使用屏障的生产者-消费者模式)
  - [4.5.6 流水线（Pipelines）](#456-流水线pipelines)
  - [4.5.7 异步数据拷贝（Asynchronous Data Copies）](#457-异步数据拷贝asynchronous-data-copies)
- [4.6 进程间通信与虚拟内存管理（IPC & VMM）](#46-进程间通信与虚拟内存管理ipc-vmm)
  - [4.6.1 使用传统进程间通信 API 的 IPC](#461-使用传统进程间通信-api-的-ipc)
  - [4.6.2 使用虚拟内存管理 API 的 IPC](#462-使用虚拟内存管理-api-的-ipc)
  - [4.6.3 虚拟内存管理（VMM）](#463-虚拟内存管理vmm)
- [本章速查（对比赛最有用的 API 索引）](#本章速查对比赛最有用的-api-索引)


> 代码/API/枚举保留英文原文；pdftotext 提取导致的断行已人工整理，个别疑似截断处标注"（需查原文确认）"。

本章是 PPU 推理优化的核心章节，涵盖 HGGC 图（降 TTFT 核心机制）、流有序内存分配器、协作组、延迟加载（关系 TTFT 测量真实性）、异步屏障与流水线、IPC 与虚拟内存管理（VMM，原文明确面向 LLM KV-cache 动态管理）。

---

## 4.1 HGGC 图

HGGC 图为任务提交提供新模型：图是一系列由依赖关系连接的操作（核函数启动、数据移动等），**定义与执行分离**，允许定义一次后多次重复启动。带来的优化：

1. **CPU 启动开销降低**——大部分设置工作在预先阶段完成；对执行时间短的核函数，每次启动的驱动设置开销可能占端到端时间的重要部分，图模式可在实例化期间为整个图支付一次开销，随后以极低开销重复启动。
2. 将整个工作流呈现给 HGGC，可实现流的碎片化任务提交无法实现的优化。

比赛关联：Qwen3.5-2B decode 阶段每步要启动数十个小 kernel（attention、MLP、norm 等），单 kernel 执行短、启动开销占比高。把一次 decode step 捕获为 HGGC 图并实例化后反复 launch，是降低 TTFT/提升吞吐的最直接手段。

### 4.1.1 图编程模型概述

HGGC 图是**有向无环图（DAG）**：节点对应一项可调度操作（核函数启动、内存拷贝、主机回调等），边表示先后约束。当一个节点的所有前驱完成后即可被调度——**调度时机和执行顺序由 HGGC 运行时自行决定，应用不应做假设**。

**节点类型**（完整列表）：

- 核函数（Kernel）
- CPU 函数调用
- 内存拷贝（memcpy）
- memset
- 空节点（Empty node）
- 等待 HGGC 事件
- 记录 HGGC 事件
- 发送外部信号量
- 等待外部信号量
- 条件节点（Conditional）
- 内存节点（Memory node）
- 子图（Child graph）：执行独立的嵌套图

**边数据**：边数据结构由三个字段构成：

| 字段 | 含义 | 默认值（零值） |
|---|---|---|
| 输出端口（Outgoing port） | 指定源节点的哪个完成信号触发此边 | 0 — 整个任务完成后触发 |
| 输入端口（Incoming port） | 指定目标节点的哪个部分受此边约束 | 0 — 阻塞整个任务 |
| 类型（Type） | 定义两端点之间的依赖语义（如是否包含内存屏障） | 0 — 完全依赖，含内存同步 |

- API 传递方式：各图 API 通过与节点数组**平行的可选数组**接收或返回边数据。省略时默认取零值；作为查询输出省略时，若被忽略的边数据中存在非零值，API 返回 `hggcErrorLossyQuery` 以警示信息丢失。
- 与流捕获配合：`hggcStreamBeginCaptureToGraph()`、`hggcStreamGetCaptureInfo()`、`hggcStreamUpdateCaptureDependencies()` 同样支持边数据。捕获期间下游节点尚未创建，边数据暂时附着在"悬空半边"上——最终连接到后续捕获的节点，或在捕获终止时被丢弃。
- 注意：使用**非完全依赖类型**的边不会等待上游节点全部完成；在判断分支流是否已汇合回源流时此类边不参与计算，且捕获结束时不可丢弃（详见流捕获方式）。

### 4.1.2 创建图

使用图进行任务提交分为三个阶段：

- **定义（Definition）/ 创建（Creation）**：创建图中操作的描述及依赖关系。
- **实例化（Instantiation）**：对图模板拍快照、验证，并执行大部分设置和初始化工作，最小化启动时工作量。产物称为**可执行图（Executable graph）**。
- **执行**：可执行图像任何 HGGC 任务一样被启动到流中，可启动任意次数而无需重新实例化。

两种创建机制：**显式图 API** 与 **流捕获（Stream capture）**。

#### 4.1.2.1 图 API 方式

```c
// PPU 推理流水线图化：前处理→推理→后处理的 3 阶段图
hggcGraphCreate(&graph, 0);
hggcGraphNode_t preprocessNode, inferNode, postNode, memcpyNode;
// 1. 数据传输节点：H2D 拷贝
hggcGraphNodeParams mcpParams;
memset(&mcpParams, 0, sizeof(mcpParams));
// ... 配置 memcpy 参数 ...
mcpParams.type = hggcGraphNodeTypeMemcpy;
hggcGraphAddNode(&memcpyNode, graph, NULL, 0, &mcpParams);
// 2. 前处理核函数节点：输入归一化
hggcGraphNodeParams prepParams;
memset(&prepParams, 0, sizeof(prepParams));
prepParams.type = hggcGraphNodeTypeKernel;
prepParams.kernel.func = (void *)preprocess_kernel;
prepParams.kernel.gridDim = dim3((inputSize + 255) / 256);
prepParams.kernel.blockDim = dim3(256);
hggcGraphAddNode(&preprocessNode, graph, &memcpyNode, 1, &prepParams);
// 3. 推理核函数节点：依赖前处理完成
hggcGraphNodeParams infParams;
memset(&infParams, 0, sizeof(infParams));
infParams.type = hggcGraphNodeTypeKernel;
infParams.kernel.func = (void *)inference_kernel;
infParams.kernel.gridDim = dim3(inferGrid);
infParams.kernel.blockDim = dim3(inferBlock);
hggcGraphAddNode(&inferNode, graph, &preprocessNode, 1, &infParams);
// 4. 后处理核函数节点：依赖推理完成
hggcGraphNodeParams postParams;
memset(&postParams, 0, sizeof(postParams));
postParams.type = hggcGraphNodeTypeKernel;
postParams.kernel.func = (void *)postprocess_kernel;
postParams.kernel.gridDim = dim3(postGrid);
postParams.kernel.blockDim = dim3(postBlock);
hggcGraphAddNode(&postNode, graph, &inferNode, 1, &postParams);
```

#### 4.1.2.2 流捕获方式

对已有基于流的代码，流捕获可将一段正常流操作序列直接"录制"为图，无需手动调用图 API。在现有代码前后分别调用 `hggcStreamBeginCapture()` / `hggcStreamEndCapture()`：

```c
// 将 PPU 算子融合流水线（LayerNorm + GELU + Linear）通过流捕获转为图
hggcGraph_t fusedOpGraph;
hggcStreamBeginCapture(stream);
// 算子1：LayerNorm 归一化
layernorm_kernel<<<gridLN, blockLN, sharedLN, stream>>>(d_input, d_normed, hiddenDim);
// 算子2：GELU 激活
gelu_kernel<<<gridAct, blockAct, 0, stream>>>(d_normed, d_activated, hiddenDim);
// 算子3：Linear 线性变换
linear_kernel<<<gridMM, blockMM, 0, stream>>>(d_activated, d_weights, d_output, M, N, K);
hggcStreamEndCapture(stream, &fusedOpGraph);
```

- 进入捕获模式后，向该流提交的所有操作**不实际执行**，而是被记录为图节点和边。`hggcStreamEndCapture()` 返回完整的捕获图对象（`hggcGraph_t`），流随即恢复正常调度。
- 最大优势是**零侵入性迁移**：大部分基于流的代码只需包裹一对 Begin/End 即可获得图模式性能。
- 除 `hggcStreamLegacy`（"NULL 流"）外，流捕获可用于任何 HGGC 流。**可以用于 `hggcStreamPerThread`**。若程序使用传统流，可将流 0 重新定义为线程专属流（Per-thread stream），功能上无变化。
- 用 `hggcStreamIsCapturing()` 查询流是否正在被捕获。
- 用 `hggcStreamBeginCaptureToGraph()` 可将任务捕获到**现有的图中**（用户提供的图，而非内部图）。

##### 4.1.2.2.1 跨流依赖与事件

- 捕获支持跨流依赖：通过 `hggcEventRecord()` / `hggcStreamWaitEvent()` 在多条流之间建立先后关系。只要事件属于同一次捕获会话，运行时自动把依赖边加入捕获图。
- 捕获模式下记录的事件称**捕获事件（Captured event）**，代表捕获图中已完成的一组节点；另一条流等待该捕获事件时，该流也被纳入同一捕获图。
- **关键约束**：所有分支流最终必须通过事件**汇合回发起捕获的源流（Origin stream）**，否则 `hggcStreamEndCapture()` 报错。

```c
// primary_stream 是源流
hggcStreamBeginCapture(primary_stream);
setup_kernel<<< ..., primary_stream >>>(...);
// 分叉：将 aux_stream 纳入捕获
hggcEventRecord(branch_event, primary_stream);
hggcStreamWaitEvent(aux_stream, branch_event);
stage_A<<< ..., primary_stream >>>(...);
stage_B<<< ..., aux_stream >>>(...);
// 汇合：aux_stream 完成后通知 primary_stream
hggcEventRecord(sync_event, aux_stream);
hggcStreamWaitEvent(primary_stream, sync_event);
finalize_kernel<<< ..., primary_stream >>>(...);
// 在源流上结束捕获
hggcStreamEndCapture(primary_stream, &graph);
// 此时 primary_stream 和 aux_stream 均退出捕获模式
```

> NOTE：流退出捕获模式后，该流上后续提交的非捕获操作仍保持与进入捕获前最后一个操作的依赖关系。

##### 4.1.2.2.2 使用注意事项与异常恢复

捕获模式下操作仅录入图结构而非实际执行，因此依赖实际执行状态或破坏图结构约束的操作在捕获期间均为无效：

- **状态查询与同步**：对捕获状态的流/捕获事件执行同步或查询无效；对包含活动流捕获的更广句柄（设备句柄、上下文句柄）查询或同步也无效。
- **传统流（Legacy Stream）限制**：同一上下文中存在正被捕获的流、且该流不是通过 `hggcStreamNonBlocking` 创建时，任何对传统流的使用无效（传统流句柄隐式包含同上下文其他流）。推论：此场景下调用隐式使用传统流的同步 API（如 `hggcMemcpy()`，它向传统流排队任务并阻塞等待完成）也无效。
- **跨捕获图/跨边界事件等待**：
  - 在正在捕获的流中等待属于另一个捕获图的事件（试图合并两个独立捕获图）无效。
  - 未指定 `hggcEventWaitExternal` 标志时，从正在捕获的流中等待非捕获事件无效。
- **不支持图化的 API**：少数向流排队异步操作的 API 在图中不受支持（如 `hggcStreamAttachMemAsync()`），捕获期间调用返回错误。

> NOTE：当依赖关系试图把已捕获操作与未捕获的实时执行操作相连时，HGGC **优先返回错误而非静默忽略**。流进入/退出捕获模式是唯一例外——模式转换自动切断转换前后的依赖链。

**捕获失效与恢复**：捕获期间触发任何非法操作，整个捕获图被标记为**失效（Invalidated）**。失效后对该捕获图关联的流或事件的任何后续操作都返回错误。唯一恢复路径是调用 `hggcStreamEndCapture()`——它将所有流移出捕获模式，但返回错误码和 NULL 图指针。之后可重新开始捕获。

##### 4.1.2.2.3 捕获自省

`hggcStreamGetCaptureInfo()` 可检查活动的流捕获：获取捕获状态、捕获的唯一（进程内）ID、底层图对象、以及流中下一个即将被捕获节点的依赖关系/边数据。依赖信息可用于获取流中最后被捕获节点的句柄。

### 4.1.3 图的生命周期管理

#### 4.1.3.1 实例化与执行

```c
hggcGraphExec_t graphExec;
hggcGraphInstantiate(&graphExec, graph, NULL, NULL, 0);
```

启动到指定流：

```c
hggcGraphLaunch(graphExec, stream);
```

完整流程（流捕获 → 实例化 → 启动）：

```c
hggcGraph_t graph;
hggcStreamBeginCapture(stream);
init_kernel<<< ..., stream >>>(...);
compute_kernel<<< ..., stream >>>(...);
libraryProcess(stream);
reduce_kernel<<< ..., stream >>>(...);
hggcStreamEndCapture(stream, &graph);
hggcGraphExec_t graphExec;
hggcGraphInstantiate(&graphExec, graph, NULL, NULL, 0);
hggcGraphLaunch(graphExec, stream);
```

#### 4.1.3.2 参数刷新

- **问题**：许多负载图拓扑在多次迭代间稳定，但节点参数（核函数入参、缓冲区地址、传输大小）逐次变化。每次重建+重新实例化会抵消图执行收益。
- **解决方案**：HGGC 允许对已实例化的图做**原地参数刷新**，无需重建拓扑或重新优化。拓扑未变时此路径代价远低于完整重新实例化；拓扑确实变化（增删节点、改变依赖）则必须重新实例化。
- 更新在图**下一次启动时生效**，不影响正在执行的先前启动。图可在同一流中反复更新并重新启动。

两条更新路径：

| 路径 | 适用场景 | 说明 |
|---|---|---|
| 全图更新 | 需刷新大量节点，或调用方不持有各节点句柄 | 提交一个拓扑相同但参数不同的 `hggcGraph_t`，运行时自动逐节点匹配并写入新参数 |
| 单个节点更新 | 变化节点少，调用方持有目标节点句柄 | 通过专用 API 直接设置各节点参数，跳过全图比对，效率更高 |

此外还支持在不修改参数的情况下**启用/禁用单个节点**。

**全图更新**：`hggcGraphExecUpdate()` 传入拓扑完全相同的"更新图"，运行时将更新图各节点参数（核函数指针、内存地址等）写入对应已实例化节点。要求：更新图拓扑与原始图完全一致，且依赖关系的指定顺序、汇节点（Sink nodes）排列顺序必须匹配。

节点匹配约束（确定性匹配算法）：

| 约束维度 | 要求 | 违反后果 |
|---|---|---|
| 捕获流操作顺序 | 同一捕获流上所有 API 调用（含事件等待等非节点操作）必须与原始图构建时顺序一致 | 节点匹配失败，`hggcGraphExecUpdate()` 返回错误 |
| 入边指定顺序 | 操作节点入边的 API（捕获流 API、节点/边添加移除）调用顺序和依赖数组内元素顺序必须一致 | 节点匹配失败 |
| 汇节点顺序 | 无输出边的节点（汇节点）集合及相对顺序必须一致；影响汇节点顺序的操作：节点添加、边移除、`hggcStreamUpdateCaptureDependencies()` 移除汇节点、`hggcStreamEndCapture()` | 节点匹配失败 |

推荐用法示例（首次完整实例化，后续优先原地刷新，失败才回退重建）：

```c
hggcGraphExec_t runnable = NULL;
hggcStream_t pipeline;
hggcStreamCreate(&pipeline);
for (int step = 0; step < totalSteps; step++) {
    // 捕获本轮迭代的计算图（参数可能随 step 变化）
    hggcGraph_t snapshot;
    hggcStreamBeginCapture(pipeline, hggcStreamCaptureModeGlobal);
    assemble_pipeline_stage(pipeline, step);
    hggcStreamEndCapture(pipeline, &snapshot);
    // 尝试就地刷新参数；首次运行或拓扑变更时回退到完整实例化
    bool needsRebuild = (runnable == NULL);
    if (!needsRebuild) {
        hggcGraphExecUpdateResult status;
        hggcGraphNode_t errNode;
        hggcGraphExecUpdate(runnable, snapshot, &errNode, &status);
        needsRebuild = (status != hggcGraphExecUpdateSuccess);
    }
    if (needsRebuild) {
        if (runnable != NULL) hggcGraphExecDestroy(runnable);
        hggcGraphInstantiate(&runnable, snapshot, NULL, NULL, 0);
    }
    hggcGraphDestroy(snapshot);
    hggcGraphLaunch(runnable, pipeline);
    hggcStreamSynchronize(pipeline);
}
```

（注：原文 pdftotext 断行将末尾三行排在循环外，按语义应位于循环体内——需查原文确认排版。）

- 也可先用 `hggcGraphKernelNodeSetParams()` 等 API 逐个修改 `hggcGraph_t` 中的节点，再调用 `hggcGraphExecUpdate()` 同步到 `hggcGraphExec_t`；少量节点变更用单节点更新 API 更高效。
- 图更新同时刷新**条件句柄的标志位和默认值**。

**单个节点更新 API**（表 3，直接修改 `hggcGraphExec_t` 中对应节点参数）：

| API | 节点类型 |
|---|---|
| `hggcGraphExecKernelNodeSetParams()` | 核函数节点 |
| `hggcGraphExecMemcpyNodeSetParams()` | 内存拷贝节点 |
| `hggcGraphExecMemsetNodeSetParams()` | 内存设置节点 |
| `hggcGraphExecHostNodeSetParams()` | 主机节点 |
| `hggcGraphExecChildGraphNodeSetParams()` | 子图节点 |
| `hggcGraphExecEventRecordNodeSetEvent()` | 事件记录节点 |
| `hggcGraphExecEventWaitNodeSetEvent()` | 事件等待节点 |

**单个节点启用（超集图模式）**：`hggcGraphNodeSetEnabled()` 允许对已实例化图中的**核函数节点、memset 节点、memcpy 节点**动态启用/禁用，实现"超集图"设计模式——构建涵盖所有可能操作的图，每次启动前按需激活/关闭特定节点。查询用 `hggcGraphNodeGetEnabled()`。

- 禁用的节点在重新启用前功能上等同于空节点。
- 节点参数不受启用/禁用影响；启用状态不受单节点更新或 `hggcGraphExecUpdate()` 全图更新影响。
- 禁用期间进行的参数更新将在重新启用时生效。

#### 4.1.3.3 参数刷新限制

各节点类型在全图更新和单节点更新时的可修改属性与限制：

| 节点类型 | 可更改属性 | 不可更改/限制 |
|---|---|---|
| 核函数节点 | 核函数参数、启动配置 | 上下文不可变；不能从非动态并行切换为动态并行 |
| Memset/Memcpy 节点 | 1D 操作的源/目标地址和大小 | 设备不可变；源/目标必须来自同一上下文；不支持 2D/3D 节点更新 |
| Memcpy 节点（额外） | — | 不支持更改内存类型（`hggcPitchedPtr`、`hggcArray_t`）或传输方向（`hggcMemcpyKind`） |
| 条件节点 | 默认值、标志 | 句柄创建和赋值顺序必须匹配；不支持更改图数量或上下文；条件体内节点受本表规则约束 |
| 内存节点 | — | 若 `hggcGraph_t` 已实例化为其他 `hggcGraphExec_t`，不能用于更新 |
| 主机节点 / 事件记录节点 / 事件等待节点 | 所有参数 | 无限制 |

比赛关联：decode 循环中每步只有 KV-cache 写指针、sampling 参数等少量变化——用单节点更新 API 或"超集图 + SetEnabled"（如 prefill/decode 两路径共图切换）可避免每步重建图；变长 batch 时可用全图更新回退模式。注意 memcpy 方向、kernel 上下文等不可改项。

### 4.1.4 图内存节点

典型负载中图每次执行需要临时设备内存做中间计算。若每次启动前由主机侧分配/释放，既引入主机-设备同步开销，又无法利用跨次启动的物理内存复用。图内存节点将**内存分配和释放直接编码为图节点**，由运行时按 PPU 有序生命周期语义自动管理分配时机和物理内存复用。

- 图分配的**虚拟地址**在分配节点整个生命周期（包括重复实例化和启动）内保持不变，图内其他节点可直接引用该地址而无需图更新，即使运行时更改底层物理内存映射。
- 同一图中生命周期不重叠的图分配可**共享同一物理内存**，运行时通过虚拟别名（Virtual aliasing）透明实现。多图启动到同一流时，不同图中生命周期不重叠的分配也可物理共享。
- 图内存节点语义与 `hggcMallocAsync` / `hggcFreeAsync` 一致，捕获这些流有序 API 调用可自动生成图内存节点。

#### 4.1.4.1 API 使用方式

| 节点类型 | 作用 | 创建时机 |
|---|---|---|
| 分配节点 | 创建一块图分配（Graph allocation），运行时在节点创建时即分配虚拟地址 | 图构建阶段 |
| 释放节点 | 释放先前由分配节点创建的图分配 | 图构建阶段 |

- 虚拟地址在分配节点存续期间不变，但**内存内容释放后不保证持久**，底层物理内存可能被重新映射给其他分配。
- 图分配生命周期遵循 **PPU 有序语义**——在 PPU 实际执行到分配节点时开始（而非 API 调用时），在以下任一事件发生时结束：
  - PPU 执行到达图中的释放节点；
  - PPU 执行到达流中的 `hggcFreeAsync()` 调用；
  - 主机侧调用 `hggcFree()` 立即释放。

> NOTE：图的销毁**不会自动释放**任何存活的图分配内存。该分配必须随后在另一个图中释放，或用 `hggcFreeAsync()` / `hggcFree()` 释放。

程序必须通过依赖边保证所有访问图分配的操作位于分配节点之后、释放操作之前。因生命周期起止由 PPU 实际执行顺序决定（而非入队顺序），图分配被称为"PPU 有序的"。

##### 4.1.4.1.1 图节点 API

通过 `hggcGraphAddNode` 显式创建。`hggcGraphNodeTypeMemAlloc` 类型节点：运行时分配的虚拟地址写入 `hggcGraphNodeParams` 结构的 `alloc::dptr` 字段供后续节点引用。释放节点用 `hggcGraphNodeTypeMemFree` 创建，且必须依赖所有使用该分配的节点。

```c
hggcGraphCreate(&graph, 0);
// 配置分配参数：在设备 0 上分配锁页内存
hggcGraphNodeParams allocParams = { hggcGraphNodeTypeMemAlloc };
allocParams.alloc.poolProps.allocType = hggcMemAllocationTypePinned;
allocParams.alloc.poolProps.location.type = hggcMemLocationTypeDevice;
allocParams.alloc.poolProps.location.id = 0;
allocParams.alloc.bytesize = bufferSize;
hggcGraphAddNode(&allocNode, graph, NULL, 0, &allocParams);
// 创建使用该分配的核函数节点
hggcGraphNodeParams kParams = { hggcGraphNodeTypeKernel };
kParams.kernel.kernelParams[0] = allocParams.alloc.dptr;
// ...设置其他核函数参数...
// 节点 procA 依赖分配节点，procB 和 procC 分别依赖 procA（形成扇出）
hggcGraphAddNode(&procA, graph, &allocNode, 1, &kParams);
hggcGraphAddNode(&procB, graph, &procA, 1, &kParams);
hggcGraphAddNode(&procC, graph, &procA, 1, &kParams);
// 释放节点必须依赖所有访问该分配的节点（procB 和 procC）
// procB 对 procA 的依赖已间接建立，因此释放节点无需显式依赖 procA
hggcGraphNode_t freeDeps[2] = { procB, procC };
hggcGraphNodeParams freeParams = { hggcGraphNodeTypeMemFree };
freeParams.free.dptr = allocParams.alloc.dptr;
hggcGraphAddNode(&freeNode, graph, freeDeps, 2, &freeParams);
// procD 不依赖释放节点，因此不得访问已释放的图分配
hggcGraphAddNode(&procD, graph, &procC, 1, &kParams);
// procE 不依赖分配节点，因此不得访问该图分配（即使释放节点依赖 procE 也是如此）
hggcGraphAddNode(&procE, graph, NULL, 0, &kParams);
```

##### 4.1.4.1.2 流捕获

捕获模式下调用 `hggcMallocAsync` / `hggcFreeAsync`，运行时自动转换为图中分配/释放节点。被捕获分配返回的虚拟地址可直接在后续捕获操作中使用；流有序依赖一并被捕获，原始流代码排序正确则图节点依赖也正确。

```c
hggcMallocAsync(&buf, bufferSize, captureStream);
process_A<<< ..., captureStream >>>(buf, ...);
// 分叉到辅助流
hggcEventRecord(splitEvent, captureStream);
hggcStreamWaitEvent(auxStream, splitEvent);
process_B<<< ..., captureStream >>>(buf, ...);
// 事件依赖自动转换为图依赖，process_C 对分配节点的依赖由此建立
process_C<<< ..., auxStream >>>(buf, ...);
// 辅助流汇合回源流
hggcEventRecord(mergeEvent, auxStream);
hggcStreamWaitEvent(captureStream, mergeEvent);
// 释放操作依赖于所有访问该内存的工作
hggcFreeAsync(buf, captureStream);
// 在源流上结束捕获
hggcStreamEndCapture(captureStream, &graph);
```

##### 4.1.4.1.3 在分配图之外访问和释放图内存

图分配不一定要由分配它的图释放。图未释放某分配时，该分配在图执行结束后依然存续，可被后续 HGGC 操作访问——只要访问通过 HGGC 事件或其他流排序机制置于分配之后。释放途径：

- 常规 `hggcFree` / `hggcFreeAsync`；
- 启动另一个包含相应释放节点的图；
- 通过该分配图的后续启动释放（实例化时设置 `hggcGraphInstantiateFlagAutoFreeOnLaunch` 标志）。

内存释放后访问它是非法的；释放必须通过图依赖、HGGC 事件等排序机制置于所有访问之后。

> NOTE：图分配可能共享底层物理内存，释放操作必须在所有设备操作完成后执行。**带外同步**（如核函数内基于内存的同步）对内存写入与释放之间的排序是不够的（见虚拟别名支持规则）。

**方式一：单流排序**（同一流上操作天然有序）：

```c
// 分配图：创建图分配节点
void *workspace;
hggcGraphNodeParams ap = { hggcGraphNodeTypeMemAlloc };
ap.alloc.poolProps.allocType = hggcMemAllocationTypePinned;
ap.alloc.poolProps.location.type = hggcMemLocationTypeDevice;
ap.alloc.bytesize = workspaceSize;
hggcGraphAddNode(&allocNode, allocGraph, NULL, 0, &ap);
workspace = ap.alloc.dptr;
hggcGraphInstantiate(&allocExec, allocGraph, NULL, NULL, 0);
// 在同一流上依次启动分配图、使用内存的核函数、释放操作
hggcGraphLaunch(allocExec, taskStream);
compute_kernel<<< ..., taskStream >>>(workspace, ...);
hggcFreeAsync(workspace, taskStream);
```

**方式二：跨流事件排序**：

```c
// 分配图
void *workspace;
hggcGraphAddNode(&allocNode, allocGraph, NULL, 0, &allocParams);
workspace = allocParams.alloc.dptr;
// 消费/释放图
// 注意：此处释放节点在图内无显式依赖（NULL），其执行顺序通过下方的跨流事件同步保证。
// 在实际使用中，释放节点应依赖所有使用该内存分配的节点，确保释放操作在所有使用完成后执行。
consumeParams.kernel.kernelParams[0] = allocParams.alloc.dptr;
hggcGraphAddNode(&freeNode, freeGraph, NULL, 1, &workspace);
hggcGraphInstantiate(&allocExec, allocGraph, NULL, NULL, 0);
hggcGraphInstantiate(&freeExec, freeGraph, NULL, NULL, 0);
hggcGraphLaunch(allocExec, producerStream);
// 通过事件让消费者流等待分配完成
hggcEventRecord(readyEvent, producerStream);
hggcStreamWaitEvent(consumerStream, readyEvent);
compute_kernel<<< ..., consumerStream >>>(workspace, ...);
// 通过事件让释放图等待消费者完成
hggcEventRecord(doneEvent, consumerStream);
hggcStreamWaitEvent(cleanupStream, doneEvent);
// 消费者完成后启动释放图
hggcGraphLaunch(freeExec, cleanupStream);
```

**方式三：图外部事件节点建立排序**：

```c
// ── 分配图：创建内存并记录就绪事件 ──
void *workspace;
hggcEvent_t allocReadyEvt;   // 分配完成后触发，通知消费方可安全访问
hggcEvent_t computeDoneEvt;  // 外部流计算结束后触发，通知释放图可回收内存
// 向分配图添加分配节点，并获取运行时分配的虚拟地址
hggcGraphAddNode(&allocNode, allocGraph, NULL, 0, &allocNodeParams);
workspace = allocNodeParams.alloc.dptr;
// 事件记录节点依赖分配节点，确保分配完成后才发出就绪信号
hggcGraphNodeParams allocEvtNodeParams = { hggcGraphNodeTypeEventRecord };
allocEvtNodeParams.eventRecord.event = allocReadyEvt;
hggcGraphAddNode(&recordNode, allocGraph, &allocNode, 1, &allocEvtNodeParams);
hggcGraphInstantiate(&allocGraphExec, allocGraph, NULL, NULL, 0);
// ── 释放图：等待就绪事件和计算完成事件后释放内存 ──
hggcGraphNodeParams computeDoneWaitParams = { hggcGraphNodeTypeEventWait };
computeDoneWaitParams.eventWait.event = computeDoneEvt;
hggcGraphAddNode(&computeDoneEventNode, cleanupGraph, NULL, 0, &computeDoneWaitParams);
hggcGraphNodeParams allocReadyWaitParams = { hggcGraphNodeTypeEventWait };
allocReadyWaitParams.eventWait.event = allocReadyEvt;
hggcGraphAddNode(&allocReadyEventNode, cleanupGraph, NULL, 0, &allocReadyWaitParams);
kernelNodeParams->kernelParams[0] = allocNodeParams.alloc.dptr;
// 核函数节点依赖就绪事件节点，保证分配已可用
hggcGraphAddNode(&kernelNode, cleanupGraph, &allocReadyEventNode, 1, &kernelNodeParams);
// 释放节点须同时依赖核函数节点和外部计算完成事件节点，
// 确保所有使用者（图内和图外）都已结束对该分配的访问
dependencies[0] = kernelNode;
dependencies[1] = computeDoneEventNode;
hggcGraphNodeParams freeNodeParams = { hggcGraphNodeTypeMemFree };
freeNodeParams.free.dptr = workspace;
hggcGraphAddNode(&freeNode, cleanupGraph, &dependencies, 2, &freeNodeParams);
hggcGraphInstantiate(&cleanupGraphExec, cleanupGraph, NULL, NULL, 0);
hggcGraphLaunch(allocGraphExec, allocStream);
// 外部流通过等待就绪事件建立对分配图的依赖
hggcStreamWaitEvent(computeStream, allocReadyEvt);
kernel<<< ..., computeStream >>> (workspace, ...);
hggcEventRecord(computeDoneEvt, computeStream);
// 释放图中的事件等待节点确保回收操作不会与外部流的计算并发执行
hggcGraphLaunch(cleanupGraphExec, releaseStream);
```

##### 4.1.4.1.4 子图中的内存节点

HGGC 12.9 引入**将子图所有权转移到父图**的功能。被转移的子图允许包含内存分配和释放节点，使含分配/释放节点的子图可在加入父图前独立构建。转移后限制：

- 不能被独立实例化或销毁；
- 不能作为另一个独立父图的子图添加；
- 不能用作 `hggcGraphExecUpdate` 的参数；
- 不能添加额外的内存分配或释放节点。

```c
// 创建子图
hggcGraphCreate(&child, 0);
// 配置分配参数：在设备 0 上分配锁页内存
hggcGraphNodeParams allocNodeParams = { hggcGraphNodeTypeMemAlloc };
allocNodeParams.alloc.poolProps.allocType = hggcMemAllocationTypePinned;
allocNodeParams.alloc.poolProps.location.type = hggcMemLocationTypeDevice;
// 指定驻留设备为设备 0
allocNodeParams.alloc.poolProps.location.id = 0;
allocNodeParams.alloc.bytesize = size;
hggcGraphAddNode(&allocNode, graph, NULL, 0, &allocNodeParams);
// 此处可插入使用该分配的其他节点
hggcGraphNodeParams freeNodeParams = { hggcGraphNodeTypeMemFree };
freeNodeParams.free.dptr = allocNodeParams.alloc.dptr;
hggcGraphAddNode(&freeNode, graph, &allocNode, 1, &freeNodeParams);
// 创建父图
hggcGraphCreate(&parent, 0);
// 将子图所有权转移给父图
hggcGraphNodeParams childNodeParams = { hggcGraphNodeTypeGraph };
childNodeParams.graph.graph = child;
childNodeParams.graph.ownership = hggcGraphChildGraphOwnershipMove;
hggcGraphAddNode(&parentNode, parent, NULL, 0, &childNodeParams);
```

#### 4.1.4.2 资源管理与性能优化

##### 4.1.4.2.1 内存重用机制

HGGC 通过两种方式重用内存：

- **图内**：虚拟和物理内存重用基于虚拟地址分配（类似流有序分配器）。生命周期不重叠的不同分配可能被分配相同虚拟地址范围——因此不同生命周期且不相交的分配指针不保证唯一。
- **图间**：物理内存重用通过**虚拟别名（Virtual aliasing）**实现：不同图把相同物理内存映射到各自唯一的虚拟地址。

物理内存管理与共享规则：

- PPU 执行顺序中，HGGC 负责在分配节点到达前将物理内存映射到虚拟地址。
- 多个不会同时运行的图可使用相同物理内存做不同分配；但物理页面同时绑定到超过一个正在执行的图、或绑定到未释放的图分配时，不能重用。
- HGGC 可能在实例化、启动或执行期间任何时间更新物理内存映射，也可能在未来图启动之间引入同步以防止存活分配引用相同物理内存。
- **陷阱**：对任何"分配-释放-分配"模式，若在分配生命周期之外访问指针，可能静默读写属于另一个分配的存活数据（即使虚拟地址唯一）。用**计算消毒工具（Compute sanitizer tools）**捕获此类错误。

##### 4.1.4.2.2 性能调优

- 多图启动到同一流时，HGGC 尝试为它们分配相同物理内存（执行不重叠）。图的物理映射在启动之间保留，避免重映射成本。
- 若某图后续启动方式导致执行可能与其他图重叠（如启动到不同流），HGGC 必须重映射（并发图需要不同内存避免数据损坏）。
- 图内存重映射常由以下操作引起：
  - 更改图启动时所在的流；
  - 对图内存池执行修剪（Trim）操作（显式释放未使用内存，见 4.2.6.5 节——原文如此引用，实际对应内存池修剪内容在 4.2.3.2）；
  - 在来自另一个图的未释放分配映射到相同内存时重新启动某个图。
- 重映射必须按执行顺序、且在该图任何先前执行完成后进行；映射是操作系统调用，相对昂贵。**应用可通过始终将含内存节点的图启动到同一流来避免此成本。**

**首次启动 / `hggcGraphUpload`**：物理内存不能在实例化期间分配/映射（此时图将在哪个流执行未知），映射在图启动期间完成。调用 `hggcGraphUpload` 可立即执行该图的所有映射并将图与上传流关联，把分配成本从启动阶段分离。若随后启动到相同流，无需额外重映射。使用不同流上传与启动，表现类似切换流，很可能导致重映射；不相关的内存池管理允许从空闲流提取内存，可能抵消上传收益。

##### 4.1.4.2.3 物理内存占用管理

- 异步分配的池管理行为意味着：销毁含内存节点的图（即使分配已释放）**不会立即把物理内存还给 OS**。
- 显式释放回 OS：`hggcDeviceGraphMemTrim` —— 取消映射并释放图内存节点保留的、未被主动使用的物理内存。未释放分配及处于调度/运行状态的图不受影响。修剪后物理内存可供其他分配 API 和其他进程使用，但会导致下次启动时重新分配和重映射。
- 注意 `hggcDeviceGraphMemTrim` 操作的池与 `hggcMemPoolTrimTo()` 不同——**图内存池不暴露给流有序内存分配器**。
- 查询图内存占用：`hggcDeviceGetGraphMemAttribute`：
  - `hggcGraphMemAttrReservedMemCurrent`：驱动为当前进程中的图分配保留的物理内存量；
  - `hggcGraphMemAttrUsedMemCurrent`：当前至少被一个图映射的物理内存量。
  - 两者可用于追踪 HGGC 何时为图获取新物理内存、检查共享机制节省了多少内存。

#### 4.1.4.3 多设备内存访问

图分配可配置为允许从多个 PPU 访问，HGGC 按需将分配映射到对等 PPU。需要不同映射的图分配可重用相同虚拟地址，此时地址范围会被映射到所有所需 PPU 上——分配有时允许比创建时请求更多的对等访问，但**依赖这些额外映射仍是错误的**。

##### 4.1.4.3.1 使用图节点 API 的对等访问

`hggcGraphAddNode` 接受分配节点参数结构中 `accessDescs` 数组字段的映射请求。`poolProps.location` 指定驻留设备；驻留 PPU 的访问是假定的，无需在 `accessDescs` 中为其指定条目。

```c
hggcGraphNodeParams allocNodeParams = { hggcGraphNodeTypeMemAlloc };
allocNodeParams.alloc.poolProps.allocType = hggcMemAllocationTypePinned;
allocNodeParams.alloc.poolProps.location.type = hggcMemLocationTypeDevice;
// 指定设备 1 为分配的驻留设备
allocNodeParams.alloc.poolProps.location.id = 1;
allocNodeParams.alloc.bytesize = size;
// 创建驻留在设备 1 上、仅设备 1 可访问的分配
hggcGraphAddNode(&allocNode, graph, NULL, 0, &allocNodeParams);
accessDescs[2];
// 初始化访问描述符（图节点 API 仅支持 ReadWrite 与 Device 类型）
accessDescs[0].flags = hggcMemAccessFlagsProtReadWrite;
accessDescs[0].location.type = hggcMemLocationTypeDevice;
accessDescs[1].flags = hggcMemAccessFlagsProtReadWrite;
accessDescs[1].location.type = hggcMemLocationTypeDevice;
// 请求设备 0 和设备 2 的访问权限；设备 1 作为驻留设备隐式具备访问权限
accessDescs[0].location.id = 0;
accessDescs[1].location.id = 2;
// 访问描述符数组包含 2 个条目
allocNodeParams.accessDescCount = 2;
allocNodeParams.accessDescs = accessDescs;
// 创建驻留在设备 1、设备 0/1/2 均可访问的分配（0 和 2 来自描述符，1 为驻留设备）
hggcGraphAddNode(&allocNode, graph, NULL, 0, &allocNodeParams);
```

##### 4.1.4.3.2 使用流捕获的对等访问

流捕获时，分配节点记录**捕获时刻**分配池的对等可访问性。捕获 `hggcMallocFromPoolAsync` 调用之后再更改池的对等可访问性，不影响已为该分配做的映射。

```c
// 初始化访问描述符（图节点 API 仅支持 ReadWrite 与 Device 类型）
accessDesc.flags = hggcMemAccessFlagsProtReadWrite;
accessDesc.location.type = hggcMemLocationTypeDevice;
accessDesc.location.id = 1;
// 假设 memPool 驻留在设备 0 且初始仅设备 0 可访问
hggcStreamBeginCapture(stream);
hggcMallocAsync(&allocPtr1, size, memPool, stream);   // 原文如此；按上下文应为 hggcMallocFromPoolAsync（需查原文确认）
hggcStreamEndCapture(stream, &graph1);
hggcMemPoolSetAccess(memPool, &accessDesc, 1);
hggcStreamBeginCapture(stream);
hggcMallocAsync(&allocPtr2, size, memPool, stream);   // 同上
hggcStreamEndCapture(stream, &graph2);
// allocPtr1 对应的图节点仅具有设备 0 的可访问性，即使 memPool 此时已具有设备 1 可访问性。
// allocPtr2 对应的图节点将具有设备 0 和设备 1 的可访问性，因为捕获时池已具备该权限。
```

比赛关联：图内存节点把中间激活/临时 buffer 的分配释放并入图内，消除主机侧 malloc/free 同步；`hggcGraphUpload` 可把物理内存映射成本从首次计时启动中剥离——对 TTFT 测量有利。注意"固定同一流启动"和"生命周期外访问指针静默踩内存"两条纪律。

---

### 4.1.5 条件执行

许多场景需要按运行时状态做分支或循环（迭代至收敛、按中间结果选路径）。传统方式需返回主机决策再提交工作，引入主机-设备往返延迟。**条件图节点**把控制流内嵌到图结构中，分支和循环完全在设备侧评估与调度，主机 CPU 不参与中间决策。

三种条件节点类型：

| 类型 | 触发条件 | 执行行为 | 主体图数量 |
|---|---|---|---|
| IF | 条件值非零时触发 | 执行主体图一次；可选提供第二个主体图（else 分支），条件值为零时执行 | 1 或 2 |
| WHILE | 条件值非零时触发 | 反复执行主体图，每轮结束后重新评估条件值，直到为零 | 1 |
| SWITCH | 条件值等于索引 n | 执行索引为 n 的主体图一次；无匹配索引则不执行任何主体图 | 用户指定（≥1） |

- 条件值读写通过**条件句柄（Conditional handle）**，设备代码中用 `hggcGraphSetConditional()` 写入。
- 创建条件节点时，运行时为每个主体图槽位生成一个空图并返回句柄，可用图 API 或 `hggcStreamBeginCaptureToGraph()` 填充节点。
- 条件节点支持嵌套。

#### 4.1.5.1 条件句柄

类型为 `hggcGraphConditionalHandle`，通过 `hggcGraphConditionalHandleCreate()` 创建。句柄必须与**单个**条件节点关联；句柄无法销毁，无需跟踪。

条件值初始化两种策略：

| 策略 | 做法 | 适用场景 |
|---|---|---|
| 指定默认值 | 创建时传入 `hggcGraphCondAssignDefault` 标志和默认值，运行时在每次图启动时自动初始化 | 条件值在图启动前即可确定 |
| 上游核函数赋值 | 不指定默认值，条件值在每次执行开始时处于未定义状态，由上游核函数通过 `hggcGraphSetConditional()` 写入 | 条件值需在设备侧动态计算 |

句柄关联的默认值和标志随全图更新一同刷新。

#### 4.1.5.2 条件节点主体图要求

违反以下约束将导致实例化失败：

| 约束类别 | 具体要求 |
|---|---|
| 设备一致性 | 所有节点必须驻留在同一设备上 |
| 允许的节点类型 | 仅限核函数节点、空节点、Memcpy 节点、Memset 节点、子图节点和条件节点 |
| 核函数节点限制 | 不允许 HGGC 动态并行（Dynamic Parallelism）或设备图启动（Device Graph Launch）；非 MPS 环境下允许协作启动（Cooperative launches） |
| Memcpy/Memset 限制 | 仅允许涉及设备内存和/或锁页（pinned）设备映射主机内存的操作；不允许涉及 HGGC 数组；实例化时两个操作数都必须能从当前设备访问（即使目标内存位于其他设备，拷贝仍由图所在设备执行） |

#### 4.1.5.3 条件节点类型及示例

**条件 IF 节点**（条件值非零执行主体图一次；示例按 batch 大小动态选路径）：

```c
// PPU 推理场景：根据 batch 大小动态选择执行路径
__global__ void checkBatchSize(hggcGraphConditionalHandle cond,
                               int *batchSize, int threshold)
{
    // 当 batch 大于阈值时启用大 batch 优化路径
    hggcGraphSetConditional(cond, (*batchSize > threshold) ? 1 : 0);
}
void buildBatchAdaptiveGraph(int threshold) {
    hggcGraph_t topGraph;
    hggcGraphExec_t executable;
    hggcGraphNode_t prevNode;
    hggcGraphCreate(&topGraph, 0);
    // 条件句柄：由检查核函数动态决定
    hggcGraphConditionalHandle cond;
    hggcGraphConditionalHandleCreate(&cond, topGraph);
    // 检查 batch 大小的核函数
    hggcGraphNodeParams kp = { hggcGraphNodeTypeKernel };
    kp.kernel.func = (void *)checkBatchSize;
    kp.kernel.gridDim = dim3(1);
    kp.kernel.blockDim = dim3(1);
    void *args[] = { &cond, &d_batchSize, &threshold };
    kp.kernel.kernelParams = args;
    hggcGraphAddNode(&prevNode, topGraph, NULL, 0, &kp);
    // IF 条件节点：满足条件时执行大 batch 优化核函数
    hggcGraphNodeParams cp = { hggcGraphNodeTypeConditional };
    cp.conditional.handle = cond;
    cp.conditional.type = hggcGraphCondTypeIf;
    cp.conditional.size = 1;
    hggcGraphAddNode(&prevNode, topGraph, &prevNode, 1, &cp);
    // 大 batch 优化路径：使用 tiling 策略提升吞吐
    hggcGraph_t optimizedPath = cp.conditional.phGraph_out[0];
    hggcGraphNodeParams optKp = { hggcGraphNodeTypeKernel };
    optKp.kernel.func = (void *)largeBatchInferenceKernel;
    optKp.kernel.gridDim = dim3(largeGrid);
    optKp.kernel.blockDim = dim3(256);
    hggcGraphAddNode(&prevNode, optimizedPath, NULL, 0, &optKp);
    hggcGraphInstantiate(&executable, topGraph, NULL, NULL, 0);
    hggcGraphLaunch(executable, 0);
    hggcDeviceSynchronize();
    hggcGraphExecDestroy(executable);
    hggcGraphDestroy(topGraph);
}
```

**IF-ELSE 分支**（`size` 设为 2，条件为零时执行第二主体图；示例按输入规模选择 FP16/FP32 路径）：

```c
// 根据输入规模选择不同精度（FP16/FP32）计算路径
void buildPrecisionSelectGraph() {
    hggcGraph_t topGraph;
    hggcGraphExec_t executable;
    hggcGraphNode_t prevNode;
    hggcGraphCreate(&topGraph, 0);
    hggcGraphConditionalHandle cond;
    hggcGraphConditionalHandleCreate(&cond, topGraph);
    // 上游核函数：根据输入规模决定精度模式
    // 大规模输入使用 FP16 加速，小规模使用 FP32 保精度
    hggcGraphNodeParams kp = { hggcGraphNodeTypeKernel };
    kp.kernel.func = (void *)selectPrecisionKernel;
    kp.kernel.gridDim = dim3(1);
    kp.kernel.blockDim = dim3(1);
    void *args[] = { &cond, &d_inputSize, &precisionThreshold };
    kp.kernel.kernelParams = args;
    hggcGraphAddNode(&prevNode, topGraph, NULL, 0, &kp);
    // IF-ELSE 条件节点：size=2 表示包含 if 和 else 分支
    hggcGraphNodeParams cp = { hggcGraphNodeTypeConditional };
    cp.conditional.handle = cond;
    cp.conditional.type = hggcGraphCondTypeIf;
    cp.conditional.size = 2;
    hggcGraphAddNode(&prevNode, topGraph, &prevNode, 1, &cp);
    // IF 分支（条件为真）：FP16 快速推理
    hggcGraph_t fp16Branch = cp.conditional.phGraph_out[0];
    hggcGraphNodeParams fp16Kp = { hggcGraphNodeTypeKernel };
    fp16Kp.kernel.func = (void *)fp16InferenceKernel;
    fp16Kp.kernel.gridDim = dim3(fp16Grid);
    fp16Kp.kernel.blockDim = dim3(256);
    hggcGraphAddNode(&prevNode, fp16Branch, NULL, 0, &fp16Kp);
    // ELSE 分支（条件为假）：FP32 高精度推理
    hggcGraph_t fp32Branch = cp.conditional.phGraph_out[1];
    hggcGraphNodeParams fp32Kp = { hggcGraphNodeTypeKernel };
    fp32Kp.kernel.func = (void *)fp32InferenceKernel;
    fp32Kp.kernel.gridDim = dim3(fp32Grid);
    fp32Kp.kernel.blockDim = dim3(256);
    hggcGraphAddNode(&prevNode, fp32Branch, NULL, 0, &fp32Kp);
    hggcGraphInstantiate(&executable, topGraph, NULL, NULL, 0);
    hggcGraphLaunch(executable, 0);
    hggcDeviceSynchronize();
    hggcGraphExecDestroy(executable);
    hggcGraphDestroy(topGraph);
}
```

**条件 WHILE 节点**（条件非零反复执行主体图；进入循环前和每轮结束后重新评估。示例：共轭梯度收敛循环，`hggcGraphCondAssignDefault` 设默认 1）：

```c
// PPU 迭代收敛算法（共轭梯度法）：条件判断收敛阈值
__global__ void conjugateGradientStep(hggcGraphConditionalHandle cond,
                                      float *residual, float *x,
                                      float *p, float *Ap,
                                      float *threshold, int n)
{
    // 执行一步共轭梯度迭代
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        // ... 共轭梯度迭代计算 ...
        x[idx] += alpha * p[idx];
        residual[idx] -= alpha * Ap[idx];
    }
    // 线程 0 检查收敛条件
    if (idx == 0) {
        float normR = computeNorm(residual, n);
        if (normR < *threshold) {
            hggcGraphSetConditional(cond, 0); // 已收敛，退出循环
        }
    }
}
void buildConvergenceGraph(float convergenceThreshold) {
    hggcGraph_t topGraph;
    hggcGraphExec_t executable;
    hggcGraphNode_t loopNode;
    hggcGraphCreate(&topGraph, 0);
    // 条件句柄：默认值 1（进入迭代循环）
    hggcGraphConditionalHandle cond;
    hggcGraphConditionalHandleCreate(&cond, topGraph, 1, hggcGraphCondAssignDefault);
    // WHILE 条件节点
    hggcGraphNodeParams cp = { hggcGraphNodeTypeConditional };
    cp.conditional.handle = cond;
    cp.conditional.type = hggcGraphCondTypeWhile;
    cp.conditional.size = 1;
    hggcGraphAddNode(&loopNode, topGraph, NULL, 0, &cp);
    // 循环体：共轭梯度迭代步
    hggcGraph_t loopBody = cp.conditional.phGraph_out[0];
    hggcGraphNodeParams kp = { hggcGraphNodeTypeKernel };
    kp.kernel.func = (void *)conjugateGradientStep;
    kp.kernel.gridDim = dim3((n + 255) / 256);
    kp.kernel.blockDim = dim3(256);
    void *args[] = { &cond, &d_residual, &d_x, &d_p, &d_Ap, &d_threshold, &n };
    kp.kernel.kernelParams = args;
    hggcGraphAddNode(&loopNode, loopBody, NULL, 0, &kp);
    // 设置收敛阈值
    hggcMemcpy(d_threshold, &convergenceThreshold, sizeof(float), hggcMemcpyHostToDevice);
    hggcGraphInstantiate(&executable, topGraph, NULL, NULL, 0);
    hggcGraphLaunch(executable, 0);
    hggcDeviceSynchronize();
    hggcGraphExecDestroy(executable);
    hggcGraphDestroy(topGraph);
}
```

**条件 SWITCH 节点**（按条件值选索引分支执行一次，索引从零开始，越界则不执行任何分支；示例：5 分支算子调度器）：

```c
// PPU 多算子调度器：根据算子类型分派到不同核函数
__global__ void dispatchOperator(hggcGraphConditionalHandle cond, int *opType)
{
    // opType: 0=卷积, 1=矩阵乘, 2=归约, 3=元素级, 4=归一化
    hggcGraphSetConditional(cond, *opType);
}
void buildOperatorDispatchGraph() {
    hggcGraph_t topGraph;
    hggcGraphExec_t executable;
    hggcGraphNode_t prevNode;
    hggcGraphCreate(&topGraph, 0);
    hggcGraphConditionalHandle cond;
    hggcGraphConditionalHandleCreate(&cond, topGraph);
    // 调度核函数：读取算子类型并设置分支索引
    hggcGraphNodeParams kp = { hggcGraphNodeTypeKernel };
    kp.kernel.func = (void *)dispatchOperator;
    kp.kernel.gridDim = dim3(1);
    kp.kernel.blockDim = dim3(1);
    void *args[] = { &cond, &d_opType };
    kp.kernel.kernelParams = args;
    hggcGraphAddNode(&prevNode, topGraph, NULL, 0, &kp);
    // SWITCH 条件节点：5 种算子类型
    hggcGraphNodeParams cp = { hggcGraphNodeTypeConditional };
    cp.conditional.handle = cond;
    cp.conditional.type = hggcGraphCondTypeSwitch;
    cp.conditional.size = 5;
    hggcGraphAddNode(&prevNode, topGraph, &prevNode, 1, &cp);
    // 各分支填充对应的算子核函数
    hggcGraph_t *branches = cp.conditional.phGraph_out;
    // 分支0：卷积算子
    hggcGraphNodeParams convKp = { hggcGraphNodeTypeKernel };
    convKp.kernel.func = (void *)conv2d_kernel;
    convKp.kernel.gridDim = dim3(convGrid);
    convKp.kernel.blockDim = dim3(256);
    hggcGraphAddNode(&prevNode, branches[0], NULL, 0, &convKp);
    // 分支1：矩阵乘算子
    hggcGraphNodeParams matmulKp = { hggcGraphNodeTypeKernel };
    matmulKp.kernel.func = (void *)matmul_kernel;
    matmulKp.kernel.gridDim = dim3(matmulGrid);
    matmulKp.kernel.blockDim = dim3(256);
    hggcGraphAddNode(&prevNode, branches[1], NULL, 0, &matmulKp);
    // 分支2：归约算子
    hggcGraphNodeParams reduceKp = { hggcGraphNodeTypeKernel };
    reduceKp.kernel.func = (void *)reduce_kernel;
    reduceKp.kernel.gridDim = dim3(reduceGrid);
    reduceKp.kernel.blockDim = dim3(256);
    hggcGraphAddNode(&prevNode, branches[2], NULL, 0, &reduceKp);
    // 分支3：元素级算子
    hggcGraphNodeParams elemKp = { hggcGraphNodeTypeKernel };
    elemKp.kernel.func = (void *)elementwise_kernel;
    elemKp.kernel.gridDim = dim3(elemGrid);
    elemKp.kernel.blockDim = dim3(256);
    hggcGraphAddNode(&prevNode, branches[3], NULL, 0, &elemKp);
    // 分支4：归一化算子
    hggcGraphNodeParams normKp = { hggcGraphNodeTypeKernel };
    normKp.kernel.func = (void *)normalize_kernel;
    normKp.kernel.gridDim = dim3(normGrid);
    normKp.kernel.blockDim = dim3(256);
    hggcGraphAddNode(&prevNode, branches[4], NULL, 0, &normKp);
    hggcGraphInstantiate(&executable, topGraph, NULL, NULL, 0);
    hggcGraphLaunch(executable, 0);
    hggcDeviceSynchronize();
    hggcGraphExecDestroy(executable);
    hggcGraphDestroy(topGraph);
}
```

比赛关联：条件节点可实现**设备侧 early-exit / 投机解码循环**（WHILE 节点包住 decode step，满足停止条件时设备侧置 0 退出），消除每步回主机判断的往返；IF/SWITCH 可按 batch 或序列长度在 prefill/decode、不同精度 kernel 间零主机开销切换。

### 4.1.6 HGGC 用户对象

异步工作涉及动态分配资源时，核心难题是何时安全释放。流模型可用事件或主机回调追踪；图模式下操作被反复启动、图生命周期与单次执行脱钩，传统方案失效。**用户对象（User Object）** 是为此设计的轻量引用计数机制，特别适用于图和流捕获场景。

两种典型资源管理模式在图环境下的困难：

```c
// 模式 A：池化管理——每次启动前需检查可用性并在完成后归还
void submitAsyncTask(hggcStream_t taskStream) {
    auto &slot = resourcePool.acquire();
    slot.ensureReady(taskStream);
    runComputation(taskStream, slot);
    slot.markInUse(taskStream);
}
// 模式 B：回调驱动的释放——通过主机函数在操作完成后清理
void submitAsyncTask(hggcStream_t taskStream) {
    Workspace *ws = new Workspace(...);
    runComputation(taskStream, ws);
    hggcLaunchHostFunc(
        taskStream,
        [](void *arg) {
            delete static_cast<Workspace *>(arg);
        },
        ws,
        0);
}
```

困难：池化方式每次启动需更新资源指针（需图更新或间接寻址）；回调方式涉及同步 API 且在捕获中被禁止。

**工作机制**：用户对象内部维护引用计数和用户指定析构回调。引用持有方：

- **开发者代码（CPU 端）**：`hggcUserObjectCreate` 创建时获得初始引用。与 C++ 智能指针不同，不存在表示引用的对象，开发者须手动追踪用户拥有的引用。
- **HGGC 图**：`hggcGraphRetainUserObject` 将引用附着到图上。

典型用法：创建后立即把唯一"用户拥有引用"转移给图（`hggcGraphRetainUserObject` + `hggcGraphUserObjectMove` 标志），此后资源生命周期完全由图托管。

图操作对引用的影响：

| 图操作 | 引用行为 |
|---|---|
| `hggcGraphClone` | 新图继承源图持有的全部引用副本（含多重性） |
| `hggcGraphInstantiate` | 可执行图获得图模板引用的独立副本 |
| 销毁 `hggcGraphExec_t`（未同步时） | 引用保留直到所有在途执行完成后才释放 |

引用计数降为零时，运行时自动调用创建时注册的析构回调。

```c
hggcGraph_t taskGraph; // 已构建好的图模板
// 创建一个带有非平凡析构逻辑的 C++ 对象
ScratchBuffer *buf = new ScratchBuffer(1024 * 1024);
hggcUserObject_t managedObj;
hggcUserObjectCreate(
    &managedObj,
    buf,
    // 使用 HGGC 提供的模板包装器，
    // 该包装器生成删除 C++ 对象指针的回调
    1,                             // 初始引用计数
    hggcUserObjectNoDestructorSync // 表明回调不能通过 HGGC 等待
);
// 将所有权从调用线程转移给图
hggcGraphRetainUserObject(
    taskGraph,
    managedObj,
    1,                       // 引用数量
    hggcGraphUserObjectMove  // 转移调用方拥有的引用（不修改总引用计数）
);
// 实例化——可执行图获得独立的引用副本
hggcGraphExec_t runnableGraph;
hggcGraphInstantiate(&runnableGraph, taskGraph, nullptr, nullptr, 0);
hggcGraphDestroy(taskGraph);
// 异步提交并同步
hggcGraphLaunch(runnableGraph, 0);
hggcGraphExecDestroy(runnableGraph);
hggcStreamSynchronize(0);
// 同步完成后所有引用已释放，ScratchBuffer 的析构函数被自动调用
```

（注：原文 pdftotext 将析构回调参数行错位，已按语义整理——需查原文确认 `hggcUserObjectCreate` 的完整参数列表。）

- 子图节点中的图所拥有的引用与子图关联而非父图；子图被更新/删除时引用相应变化。可执行图或子图通过 `hggcGraphExecUpdate` / `hggcGraphExecChildGraphNodeSetParams` 更新时，新源图中的引用被克隆并替换目标图中的引用。若之前的启动未同步，将被释放的引用保持到启动执行完成。
- 目前无机制通过 HGGC API 等待用户对象析构函数；可在析构函数中手动向同步对象发信号。
- **从析构函数中调用 HGGC API 是非法的**（与 `hggcLaunchHostFunc` 限制类似），避免阻塞 HGGC 内部共享线程。若依赖单向且调用线程不阻塞 HGGC 工作进度，通知另一线程执行 API 调用是合法的。
- 入口 API：`hggcUserObjectCreate`。

### 4.1.7 使用图 API

- `hggcGraph_t` 对象**不是线程安全的**，开发者须确保多线程不会同时访问同一 `hggcGraph_t`。
- `hggcGraphExec_t` **不能与其自身并发运行**：其启动按顺序排在同一可执行图的先前启动之后。
- 图的执行在流中完成以便与其他异步工作排序；但**流仅用于排序**，不限制图的内部并行性，也不影响图节点执行的位置。

---

## 4.2 流有序内存分配器

### 4.2.1 概述与查询支持

许多 PPU 应用中内存分配/释放在迭代训练循环、流水线推理等场景高频发生。传统 `hggcMalloc` / `hggcFree` 每次调用引发**跨所有流的隐式同步**，多流重叠执行时成为严重瓶颈。

流有序内存分配器核心思想：把分配/释放**绑定到 HGGC 流**——分配在流时间线某点变为可用，释放在另一点生效——融入流有序执行模型，无需额外同步。分配器内部维护内存池，在池缓存策略允许范围内自动复用已释放块，减少向 OS 申请/归还开销。应用可通过释放阈值配置权衡内存占用与分配性能。原生支持进程间内存共享。

三方面收益：

- 简化高频分配场景内存管理，降低自实现内存池复杂度；
- 不同库和模块可共享同一驱动管理的内存池，避免各自管理的浪费；
- 驱动能利用流有序语义做更优分配与调度决策。

**查询支持**：

- `hggcDeviceGetAttribute()` + `hggcDevAttrMemoryPoolsSupported`：设备是否支持流有序内存分配器。
- `hggcDevAttrMemoryPoolSupportedHandleTypes`：IPC 内存池支持。

```c
int driverVersion = 0;
int deviceSupportsMemoryPools = 0;
int poolSupportedHandleTypes = 0;
hggcDriverGetVersion(&driverVersion);
if (driverVersion >= 11020) {
    hggcDeviceGetAttribute(&deviceSupportsMemoryPools,
                           hggcDevAttrMemoryPoolsSupported, device);
}
if (deviceSupportsMemoryPools != 0) {
    // 该设备支持流有序内存分配器
}
if (driverVersion >= 11030) {
    hggcDeviceGetAttribute(&poolSupportedHandleTypes,
                           hggcDevAttrMemoryPoolSupportedHandleTypes, device);
}
if (poolSupportedHandleTypes & hggcMemHandleTypePosixFileDescriptor) {
    // 该设备上的内存池可使用基于 POSIX 文件描述符的 IPC 机制
}
```

查询前先查驱动版本，可避免在属性未定义的驱动上触发 `hggcErrorInvalidValue`；也可用 `hggcGetLastError` 清除错误。

### 4.2.2 内存管理

`hggcMallocAsync` 与 `hggcFreeAsync` 是流有序内存管理 API，都接收 stream 参数定义分配何时可用/何时失效，不阻塞主机线程或其他流，避免 `hggcMalloc`/`hggcFree` 的高代价同步。结合内存池可进一步优化：池管理复用大块内存，降低开销并防碎片。

#### 4.2.2.1 分配内存

`hggcMallocAsync` 在 PPU 上触发异步分配并与特定流关联。

> NOTE：`hggcMallocAsync` 决定分配驻留位置时**忽略当前 device/context**，而是基于指定的内存池或所提供的流确定设备。

基本模式：

```c
void *devBuf;
size_t nbytes = 512;
hggcMallocAsync(&devBuf, nbytes, hggcStreamPerThread);
// 在已分配的缓冲区上执行核函数计算
kernel<<<..., hggcStreamPerThread>>>(devBuf, ...);
// 流有序释放——无需显式 CPU/PPU 同步
hggcFreeAsync(devBuf, hggcStreamPerThread);
```

> NOTE：从非分配该内存的流访问这段分配时，开发者必须保证访问发生在分配操作之后，否则行为未定义。

#### 4.2.2.2 释放内存

`hggcFreeAsync()` 以流有序方式异步释放设备内存，不阻塞主机或其他流。开发者必须保证释放发生在分配及其所有使用之后；释放开始后再使用即未定义行为。用事件/流同步保证跨流访问在释放前完成：

```c
hggcMallocAsync(&devBuf, nbytes, allocStream);
hggcEventRecord(allocReady, allocStream);
// 计算流需等待分配完成后才可访问该缓冲区
hggcStreamWaitEvent(computeStream, allocReady);
kernel<<<..., computeStream>>>(devBuf, ...);
hggcEventRecord(computeDone, computeStream);
// 释放流需等待计算流完成后才可回收该缓冲区
hggcStreamWaitEvent(releaseStream, computeDone);
hggcFreeAsync(devBuf, releaseStream);
```

`hggcMalloc()` 分配的内存可用 `hggcFreeAsync()` 释放（同样须先完成所有访问）：

```c
hggcMalloc(&devBuf, nbytes);
kernel<<<..., workStream>>>(devBuf, ...);
hggcFreeAsync(devBuf, workStream);
```

`hggcMallocAsync` 分配的内存也可用 `hggcFree()` 释放——驱动假定所有访问已完成、不做额外同步；开发者可用 `hggcStreamQuery` / `hggcStreamSynchronize` / `hggcEventQuery` / `hggcEventSynchronize` / `hggcDeviceSynchronize` 保证异步工作完成：

```c
hggcMallocAsync(&devBuf, nbytes, workStream);
kernel<<<..., workStream>>>(devBuf, ...);
// 使用同步 API 释放时须确保所有异步操作已完成
hggcStreamSynchronize(workStream);
hggcFree(devBuf);
```

### 4.2.3 内存池管理

#### 4.2.3.1 默认池与显式池

内存池封装虚拟地址与物理内存资源，按属性分配管理，最主要的是内存类型与位置。

- 所有 `hggcMallocAsync` 调用都使用内存池资源。未指定池时使用所提供 stream 的设备的**当前内存池**。
- 当前内存池：`hggcDeviceSetMempool` 设置，`hggcDeviceGetMempool` 查询。每设备有默认内存池，未调用 `hggcDeviceSetMempool` 时默认池活动。

> NOTE：设备的当前 mempool 是该设备的本地资源——不指定池分配总会得到位于该流设备上的本地分配。

- `hggcMallocFromPoolAsync` 及"hggcMallocAsync 的 C++ 重载"允许在不设为当前池的情况下为某次分配指定池。
- `hggcDeviceGetDefaultMempool` 与 `hggcMemPoolCreate` 返回池句柄；`hggcMemPoolSetAttribute` / `hggcMemPoolGetAttribute` 控制池属性。
- 默认池（隐式池）的分配是**不可迁移（non-migratable）**的设备分配，始终可从该设备访问；可访问性用 `hggcMemPoolSetAccess` 修改、`hggcMemPoolGetAccess` 查询。**默认池不支持 IPC。**
- `hggcMemPoolCreate` 创建显式池，可指定 IPC 能力、最大池大小、（受支持平台上）驻留特定 CPU NUMA 节点等。

```c
// 场景 1：为指定 PPU 创建显式设备本地池
int ppuIdx = 0;
hggcMemPoolProps devPoolCfg = { };
devPoolCfg.allocType = hggcMemAllocationTypePinned;
devPoolCfg.location.id = ppuIdx;
devPoolCfg.location.type = hggcMemLocationTypeDevice;
hggcMemPool_t devicePool;
hggcMemPoolCreate(&devicePool, &devPoolCfg);
// 场景 2：在指定 CPU NUMA 节点上创建支持 IPC 共享的池
int numaNode = 0;
hggcMemPoolProps ipcPoolCfg = { };
ipcPoolCfg.allocType = hggcMemAllocationTypePinned;
ipcPoolCfg.location.id = numaNode;
ipcPoolCfg.location.type = hggcMemLocationTypeHostNuma;
ipcPoolCfg.handleType = hggcMemHandleTypePosixFileDescriptor;
hggcMemPool_t sharedPool;
hggcMemPoolCreate(&sharedPool, &ipcPoolCfg);
```

#### 4.2.3.2 缓存行为与复用策略

默认分配器尽量最小化池拥有的物理内存。为减少向 OS 申请/释放物理内存的调用，应用应为每个池配置内存占用上限（footprint）——通过**释放阈值属性 `hggcMemPoolAttrReleaseThreshold`**：

- 释放阈值：池在尝试把内存释放回 OS 之前应保留的字节数。池持有内存超过阈值时，分配器在下一次流/事件/设备同步调用时尝试释放回 OS。
- 设为 `UINT64_MAX` 阻止驱动每次同步后收缩池。

```c
Hguint64_t setVal = UINT64_MAX;
hggcMemPoolSetAttribute(memPool, hggcMemPoolAttrReleaseThreshold, &setVal);
```

显式收缩：`hggcMemPoolTrimTo`，`minBytesToKeep` 参数允许保留预期后续阶段所需内存量。

```c
Hguint64_t setVal = UINT64_MAX;
hggcMemPoolSetAttribute(memPool, hggcMemPoolAttrReleaseThreshold, &setVal);
// 需要大量流有序内存的应用阶段
for (i=0; i<10; i++) {
    for (j=0; j<10; j++) {
        hggcMallocAsync(&ptrs[j],size[j], stream);
    }
    kernel<<<...,stream>>>(ptrs,...);
    for (j=0; j<10; j++) {
        hggcFreeAsync(ptrs[j], stream);
    }
}
// 下一阶段不再需要这么多内存
// 同步以确保收缩操作知道分配已不再使用
hggcStreamSynchronize(stream);
hggcMemPoolTrimTo(mempool, 0);
// 收缩操作释放的物理内存现在可供其他进程或分配机制使用
```

**内存复用策略**：满足分配请求时，驱动优先复用之前 `hggcFreeAsync()` 释放的内存，再向 OS 申请。同流中释放的内存可在同流后续分配中立即复用；某流与 CPU 同步后，该流中先前释放的内存对任何流的分配可复用。适用于默认池与显式池。

三个可控策略属性（用 `hggcMemPoolSetAttribute` 启用/禁用；升级驱动可能改变枚举次序）：

| 策略 | 触发条件 | 效果 |
|---|---|---|
| `hggcMemPoolReuseFollowEventDependencies` | 存在由 HGGC 事件建立的跨流依赖 | 利用事件依赖关系复用其他流中已释放的内存 |
| `hggcMemPoolReuseAllowOpportunistic` | 释放操作的流有序语义已满足 | 根据流实际执行进度进行机会式复用 |
| `hggcMemPoolReuseAllowInternalDependencies` | 无法从 OS 获取更多物理内存 | 驱动自动插入流间依赖以强制复用 |

`hggcMemPoolReuseFollowEventDependencies` 示例：

```c
hggcMallocAsync(&ptr, size, originalStream);
kernel<<<..., originalStream>>>(ptr, ...);
hggcFreeAsync(ptr, originalStream);
hggcEventRecord(event,originalStream);
// 等待捕获了另一流中释放操作的事件，使得分配器在
// hggcMemPoolReuseFollowEventDependencies 启用时可以复用该内存
// 来满足其他流中的新分配请求
hggcStreamWaitEvent(otherStream, event);
hggcMallocAsync(&ptr2, size, otherStream);
```

`hggcMemPoolReuseAllowOpportunistic`：分配器检查已释放分配，判断释放的流有序语义是否已满足（如流是否已执行过释放点）。禁用后仍复用流与 CPU 同步后变得可用的内存；禁用不阻止 `hggcMemPoolReuseFollowEventDependencies` 生效。

```c
hggcMallocAsync(&ptr, size, originalStream);
kernel<<<..., originalStream>>>(ptr, ...);
hggcFreeAsync(ptr, originalStream);
// 经过一段时间后，核函数执行完成
wait(10);
// 当 hggcMemPoolReuseAllowOpportunistic 启用时，分配器可根据
// originalStream 的实际执行进度，使用先前释放的内存满足此分配请求
hggcMallocAsync(&ptr2, size, otherStream);
```

`hggcMemPoolReuseAllowInternalDependencies`：无法从 OS 分配更多物理内存时，驱动寻找可用性依赖另一流待完成进度的内存，在发起分配的流中插入所需依赖并复用。

```c
hggcMallocAsync(&ptr, size, originalStream);
kernel<<<..., originalStream>>>(ptr, ...);
hggcFreeAsync(ptr, originalStream);
// 当 hggcMemPoolReuseAllowInternalDependencies 启用且驱动无法分配更多物理内存时，
// 驱动可能在发起分配的流中隐式插入 hggcStreamWaitEvent，
// 以确保 otherStream 中的后续工作发生在原始流中对该分配的访问完成之后
hggcMallocAsync(&ptr2, size, otherStream);
```

##### 4.2.3.2.2 禁用复用策略

- 机会式复用（`hggcMemPoolReuseAllowOpportunistic`）会按 CPU/PPU 执行交错引入**运行间差异**，每次运行分配模式不同。
- 内部依赖插入（`hggcMemPoolReuseAllowInternalDependencies`）可能以出乎意料且潜在非确定的方式串行化工作；开发者可能更希望在分配失败时显式同步事件或流。

#### 4.2.3.3 资源使用统计

- `hggcMemPoolAttrReservedMemCurrent`：池当前消耗的物理 PPU 内存总量。
- `hggcMemPoolAttrUsedMemCurrent`：从池分配且尚不可复用的内存总大小。
- `hggcMemPoolAttr*MemHigh`：水位线，记录自上次重置以来对应 `*MemCurrent` 的最大值；可用 `hggcMemPoolSetAttribute` 重置为当前值。

```c
// 批量获取使用统计的辅助函数示例
struct usageStatistics {
    hguint64_t reserved;
    hguint64_t reservedHigh;
    hguint64_t used;
    hguint64_t usedHigh;
};
void getUsageStatistics(hggcMemoryPool_t memPool, struct usageStatistics *statistics)
{
    hggcMemPoolGetAttribute(memPool, hggcMemPoolAttrReservedMemCurrent, statistics->reserved);
    hggcMemPoolGetAttribute(memPool, hggcMemPoolAttrReservedMemHigh, statistics->reservedHigh);
    hggcMemPoolGetAttribute(memPool, hggcMemPoolAttrUsedMemCurrent, statistics->used);
    hggcMemPoolGetAttribute(memPool, hggcMemPoolAttrUsedMemHigh, statistics->usedHigh);
}
// 重置水位线后，它们将取当前值作为新的起点
void resetStatistics(hggcMemoryPool_t memPool)
{
    hguint64_t value = 0;
    hggcMemPoolSetAttribute(memPool, hggcMemPoolAttrReservedMemHigh, &value);
    hggcMemPoolSetAttribute(memPool, hggcMemPoolAttrUsedMemHigh, &value);
}
```

### 4.2.4 多设备与 IPC 支持

#### 4.2.4.1 面向多 PPU 支持的设备可访问性

- 内存池分配的可访问性**不遵循** `hggcDeviceEnablePeerAccess` / `hgCtxEnablePeerAccess`；用 `hggcMemPoolSetAccess` 修改哪些设备可访问池中的分配。
- 默认分配仅能从驻留设备访问且不可撤销。允许其他设备访问前，访问设备必须与池所在设备具备 peer 能力（用 `hggcDeviceCanAccessPeer` 验证）。未检查 peer 能力时设置访问可能以 `hggcErrorInvalidDevice` 失败；若池尚无分配，即使无 peer 能力调用也可能成功，但下一次分配将失败。
- `hggcMemPoolSetAccess` 影响池中**所有**分配（不仅是未来的）；`hggcMemPoolGetAccess` 同样报告全池可访问性。**不建议频繁更改**某池针对某 PPU 的可访问性——一旦允许访问，应在池生命周期内保持。

```c
// 为目标 PPU 开启对指定内存池的读写访问权限
hggcError_t enableCrossDeviceAccess(hggcMemPool_t pool, int ownerPpu,
                                    int peerPpu) {
    // 先验证两个 PPU 之间是否具备 peer 能力
    int peerCapable = 0;
    hggcError_t status = hggcDeviceCanAccessPeer(&peerCapable, peerPpu,
                                                 ownerPpu);
    if (status != hggcSuccess) {
        return status;
    }
    if (peerCapable == 0) {
        return hggcErrorPeerAccessUnsupported;
    }
    // 构造访问描述符并设置权限
    hggcMemAccessDesc peerDesc = {};
    peerDesc.location.type = hggcMemLocationTypeDevice;
    peerDesc.location.id = peerPpu;
    peerDesc.flags = hggcMemAccessFlagsProtReadWrite;
    return hggcMemPoolSetAccess(pool, &peerDesc, 1);
}
```

#### 4.2.4.2 为 IPC 启用内存池

内存池可启用进程间通信（IPC），在进程间轻松、高效、安全地共享 PPU 内存，提供与 VMM API 相同的安全收益。分两步：先共享对**池**的访问权限（建立并强制安全策略），再共享池中的**特定分配**（协调各进程使用的虚拟地址及导入进程中映射生效时机）。

##### 4.2.4.2.1 创建并共享 IPC 内存池

`hggcMemPoolExportToShareableHandle()` 获取池的 OS 原生句柄 → 用 OS 原生 IPC 机制传给导入进程 → `hggcMemPoolImportFromShareableHandle()` 创建导入池。导出成功的前提是池创建时在属性结构中指定了所请求的句柄类型。

```c
// ── 导出进程 ──
// 在设备 0 上创建支持 IPC 导出的内存池
hggcMemPoolProps exportPoolCfg = { };
exportPoolCfg.handleTypes = HG_MEM_HANDLE_TYPE_POSIX_FILE_DESCRIPTOR;
exportPoolCfg.allocType = hggcMemAllocationTypePinned;
exportPoolCfg.location.type = hggcMemLocationTypeDevice;
exportPoolCfg.location.id = 0;
hggcMemPoolCreate(&ipcPool, &exportPoolCfg));
// 基于文件描述符的句柄为整数类型
int shareFd = 0;
// 获取内存池的操作系统原生句柄
// 注意：此处传入的是句柄变量的指针
hggcMemPoolExportToShareableHandle(&shareFd,
                                   ipcPool,
                                   HG_MEM_HANDLE_TYPE_POSIX_FILE_DESCRIPTOR,
                                   0);
// 需要通过操作系统特定的 IPC 机制将句柄发送给导入进程

// ── 导入进程 ──
int shareFd;
// 需要通过操作系统特定的 IPC 机制从导出进程获取句柄
// 使用共享句柄创建导入的内存池
// 注意：此处句柄以值传递
hggcMemPoolImportFromShareableHandle(&importedMemPool,
                                     (void*)shareFd,
                                     HG_MEM_HANDLE_TYPE_POSIX_FILE_DESCRIPTOR,
                                     0);
```

（注：原文中导出/导入进程处分别出现 `handleType` 与 `handleTypes` 字段写法，以及 `hggcMemPoolCreate(...))` 多出的右括号，均为提取瑕疵——需查原文确认。）

##### 4.2.4.2.2 在导入进程中设置访问权限

导入池起初仅能从其驻留设备访问，**不继承导出进程的可访问性**。导入进程需为计划访问该内存的任意 PPU 调用 `hggcMemPoolSetAccess`。若导入池属于导入进程不可见的设备，必须用 `hggcMemPoolSetAccess` 为将使用分配的 PPU 启用访问。

##### 4.2.4.2.3 创建并共享来自已导出池的分配

共享池后，导出进程中用该池 `hggcMallocAsync()` 创建的分配可与导入进程共享。因池级已建立安全策略，OS 无需为特定池分配做额外安全记账——用于导入池分配的不透明数据 `hggcMemPoolPtrExportData` 可通过任何机制发送。导入进程访问规则与导出进程相同：访问必须发生在分配流中分配操作执行之后。用 IPC 事件保证导入进程不在分配就绪前访问：

```c
// ── 导出进程：准备分配 ──
hggcMemPoolPtrExportData ptrShareData;
hggcEvent_t allocReadyEvent;
hggcIpcEventHandle_t allocReadyEventHandle;
// 创建用于跨进程协调的 IPC 事件
// hggcEventInterprocess 标志使事件支持跨进程传递
// hggcEventDisableTiming 用于提升性能
hggcEventCreate(&allocReadyEvent, hggcEventDisableTiming | hggcEventInterprocess)
// 从导出内存池中分配
hggcMallocAsync(&ptr, size, exportMemPool, stream);
// 记录事件以通知导入进程分配已就绪
hggcEventRecord(allocReadyEvent, stream);
hggcMemPoolExportPointer(&ptrShareData, ptr);
hggcIpcGetEventHandle(&allocReadyEventHandle, allocReadyEvent);
// 通过任意 IPC 机制将事件句柄和指针导出数据发送给导入进程
// 此处以共享内存为例
shmem->ptrData = ptrShareData;
shmem->allocReadyEventHandle = allocReadyEventHandle;
// 通知消费者数据已就绪

// ── 导入进程：导入分配 ──
hggcMemPoolPtrExportData *importData = &shmem->prtData;   // 原文如此（prtData 疑为 ptrData 笔误）
hggcEvent_t allocReadyEvent;
hggcIpcEventHandle_t *allocReadyEventHandle = &shmem->allocReadyEventHandle;
// 通过任意 IPC 机制获取事件句柄和导出数据
// 此处使用共享内存，需确保共享内存已被导出进程填充
hggcIpcOpenEventHandle(&allocReadyEvent, allocReadyEventHandle);
// 导入分配；该操作不会阻塞等待分配就绪
hggcMemPoolImportPointer(&ptr, importedMemPool, importData);
// 在导入进程中使用该分配前，必须等待导出进程中的分配操作完成
hggcStreamWaitEvent(stream, allocReadyEvent);
kernel<<<..., stream>>>(ptr, ...);
```

（注：原文分配调用写作 `hggcMallocAsync(&ptr, size, exportMemPool, stream)`，按四参形式应为 `hggcMallocFromPoolAsync`——需查原文确认。）

释放顺序：**必须先在导入进程中释放，再在导出进程中释放**。两进程中 `hggcFreeAsync` 之间用 HGGC IPC 事件同步（也可用两个进程都调用 `hggcFree`，或其他流同步 API 替代 IPC 事件）：

```c
// 必须先在导入进程中释放，再在导出进程中释放
kernel<<<..., stream>>>(ptr, ...);
// 导入进程中的最后一次访问
hggcFreeAsync(ptr, stream);
// 释放后导入进程不可再访问该内存
hggcEventRecord(finishedIpcEvent, stream);

// ── 导出进程 ──
// 导出进程的释放操作需要与导入进程的释放保持流有序协调
hggcStreamWaitEvent(stream, finishedIpcEvent);
kernel<<<..., stream>>>(ptrInExportingProcess, ...);
// 导入进程的释放不影响导出进程继续使用该分配
hggcFreeAsync(ptrInExportingProcess,stream);
```

##### 4.2.4.2.4 IPC 导出池的限制

IPC 池目前**不支持将物理块释放回 OS**：`hggcMemPoolTrimTo` 无效，`hggcMemPoolAttrReleaseThreshold` 被事实上忽略。该行为由驱动控制，未来驱动更新可能变化。

##### 4.2.4.2.5 IPC 导入池的限制

- 不允许从导入池分配：不能设为当前池，不能用于 `hggcMallocFromPoolAsync`；分配复用策略属性对其无意义。
- 同样不支持将物理块释放回 OS。
- 资源使用统计查询只反映导入到该进程的分配及相关物理内存。

### 4.2.5 同步 API 的动作

用户请求 HGGC 驱动同步时，驱动等待异步工作完成；返回前确定哪些释放操作已被该同步保证完成——这些分配变得可用于后续分配（不受指定流或已禁用分配策略影响）。驱动同时在此检查 `hggcMemPoolAttrReleaseThreshold` 并尽量释放多余物理内存。

### 4.2.6 附录

- **4.2.6.1 `hggcMemcpyAsync` 的当前上下文/设备敏感性**：当前 HGGC 驱动中，任何涉及 `hggcMallocAsync` 内存的异步 memcpy 都应在指定流的上下文作为调用线程当前上下文时执行。`hggcMemcpyPeerAsync` 不需要（它引用参数中指定的设备主上下文）。
- **4.2.6.2 `hggcPointerGetAttributes` 查询**：对某分配调用 `hggcFreeAsync` 之后再对其调用 `hggcPointerGetAttributes` 导致未定义行为（即使该分配仍可从某流访问）。
- **4.2.6.3 `hggcGraphAddMemsetNode`**：无法与流有序分配器分配的内存一起工作；但可以对这些分配做 stream capture 的 memset。
- **4.2.6.4 指针属性**：`hggcPointerGetAttributes` 适用于流有序分配。因流有序分配不与上下文关联，查询 `HG_POINTER_ATTRIBUTE_CONTEXT` 成功但 `*data` 返回 NULL。`HG_POINTER_ATTRIBUTE_DEVICE_ORDINAL` 可确定分配位置（选择 `hggcMemcpyPeerAsync` p2h2p 拷贝上下文时有用）。`HG_POINTER_ATTRIBUTE_MEMPOOL_HANDLE` 用于调试及 IPC 前确认分配来自哪个池。
- **4.2.6.5 CPU 虚拟内存**：使用 HGGC 流有序内存分配器 API 时，应避免用 `ulimit -v` 设置 VRAM 限制——不受支持。

比赛关联：`hggcMallocAsync`/`hggcFreeAsync` + 释放阈值设 `UINT64_MAX` 是推理服务显存管理基座：消除 decode 循环中 malloc 引起的全流隐式同步，KV-cache/中间激活池化复用；`hggcMemPoolAttrUsedMemHigh` 水位线可用于显存峰值 profiling（32GB VRAM 预算规划）。

---

## 4.3 协作组（Cooperative Groups）

### 4.3.1 简介

协作组是 HGGC 编程模型的扩展，用于组织协同工作的线程组，允许控制线程协作粒度、表达更丰富的并行分解，并提供常见并行原语实现（扫描 scan、并行归约 reduce）。HGGC 最初只提供跨线程块屏障 `__syncthreads()`；协作组为更广泛的并行交互模式提供安全、面向未来的机制。

### 4.3.2 协作组句柄与成员函数

协作组通过句柄管理，句柄让参与线程了解自己在组中的位置、组大小等信息。部分成员函数：

| 访问接口 | 返回值 |
|---|---|
| `thread_rank()` | 调用线程的 rank |
| `num_threads()` | 组中线程总数 |
| `thread_index()` | 在启动块中线程的三维索引 |
| `dim_threads()` | 启动块的三维尺寸（以线程为单位） |

### 4.3.3 默认行为/协作组执行

grid 网格和 block 线程块由核函数启动配置隐式创建。这些"隐式"组可显式分解为更细粒度组。访问器：

| 访问器 | 组作用域 |
|---|---|
| `this_thread_block()` | 返回包含当前线程块中所有线程的组句柄 |
| `this_grid()` | 返回包含网格中所有线程的组句柄 |
| `coalesced_threads()` ¹ | 返回 warp 中当前活动线程组的句柄 |

#### 4.3.3.1 尽早创建隐式组句柄

为获得最佳性能，**尽早创建隐式组句柄**（尽可能早，在任何分支发生之前），并在整个核函数中使用该句柄。

#### 4.3.3.2 传引用传递协作组句柄

句柄必须在声明时初始化（无默认构造函数）；不鼓励复制构造组句柄。

### 4.3.4 创建协作组

协作组通过将父组分区为子组创建，分区时创建组句柄管理子组。分区操作：

| 分区类型 | 描述 |
|---|---|
| `tiled_partition` | 将父组划分为一系列固定大小的子组，排列成一维行优先格式 |
| `stride_partition` | 将父组划分为等大小的子组，线程以循环方式分配给子组 |
| `labeled_partition` | 基于条件标签将父组划分为一维子组，标签可以是任意整数类型 |
| `binary_partition` | 标记分区的专门形式，标签只能是 "0" 或 "1" |

```c
namespace cg = cooperative_groups;
// 获取当前线程的协作组
cg::thread_block my_group = cg::this_thread_block();
// 将协作组分割为大小为8的瓦片
cg::thread_block_tile<8> my_subgroup = cg::tiled_partition<8>(cta);
// 作为my_subgroup工作
```

#### 4.3.4.1 避免组创建危险

分区是**集体操作**，组中所有线程都必须参与。在不是所有线程都能到达的条件分支中创建组，可能导致死锁或数据损坏。

### 4.3.5 同步

协作组允许在不同粒度级别同步合作线程组（此前只能在核函数完成边界的线程块级同步）。

#### 4.3.5.1 cg::sync

集体 `sync()` 函数与 `__syncthreads()` 一样保证：

- 所有线程在同步点之前的内存访问（读写）对组中所有线程在同步点之后可见；
- 组中所有线程都在任何线程被允许继续前进之前到达同步点。

```c
namespace cg = cooperative_groups;
cg::thread_block my_group = cg::this_thread_block();
// 同步块中的线程
cg::sync(my_group);
```

#### 4.3.5.2 Barriers 屏障

协作组提供类似 `ppu_barrier_sync_cnt` 的屏障 API，关键差异：

- 协作组屏障**自动初始化**；
- 组中所有线程必须在一个阶段内一次全部到达并等待在屏障处；
- `barrier_arrive` 返回一个 `arrival_token` 对象，必须传入相应的 `barrier_wait`，在其中被消耗且不能再用。

危险注意事项：

- 调用 `barrier_arrive` 之后、`barrier_wait` 之前，不能在组间使用任何集体操作；
- `barrier_wait` 仅保证组中所有线程都已调用 `barrier_arrive`，**不保证所有线程都已调用 `barrier_wait`**。

```c
namespace cg = cooperative_groups;
cg::thread_block my_group = cg::this_thread_block();
auto token = block.barrier_arrive();
// 可选：做一些本地处理以隐藏同步延迟
local_processing();
// 确保同步后再访问 shared memory
block.barrier_wait(std::move(token));
```

### 4.3.6 协作操作

协作操作要求指定组中所有线程参与。除非 API 明确允许不同的值，否则组中所有线程必须为每个协作调用传递相应参数的相同值，否则行为未定义。

#### 4.3.6.1 归约操作

`reduce` 对组中每个线程提供的数据执行并行归约，须指定操作符：

| 操作符 | 返回值 |
|---|---|
| `plus` | 组中所有值的总和 |
| `less` | 最小值 |
| `greater` | 最大值 |
| `bit_and` | 按位 AND 归约 |
| `bit_or` | 按位 OR 归约 |
| `bit_xor` | 按位 XOR 归约 |

PPU 现存的所有硬件都对归约操作有加速效果。

warp 级 tile 求和归约示例（`__shfl_down_sync`）：

```c
__global__ void tileReduceKernel(float* d_in, float* d_out) {
    namespace cg = cooperative_groups;
    // 1. 获取线程块组，并创建 warp 级别的 tile
    cg::thread_block block = cg::this_thread_block();
    cg::thread_block_tile<32> tile = cg::tiled_partition<32>(block);
    // 2. 将数据加载到寄存器中（例如每个线程处理一个元素）
    float val = d_in[blockIdx.x * blockDim.x + threadIdx.x];
    // 3. 使用 __shfl_down_sync 进行 warp 级归约
    float tile_sum = val;
    for (int offset = tile.size() / 2; offset > 0; offset /= 2) {
        tile_sum += __shfl_down_sync(0xFFFFFFFF, tile_sum, offset);
    }
    // 4. 每个 warp 的线程0将结果写入共享内存，再由线程块的线程0汇总
    __shared__ float warp_sums[32];
    if (tile.thread_rank() == 0) {
        warp_sums[tile.meta_group_rank()] = tile_sum;
    }
    block.sync();
    // 线程块的线程0汇总所有 warp 的结果
    if (threadIdx.x == 0) {
        float block_sum = 0.0f;
        int num_warps = (blockDim.x + 31) / 32;
        for (int i = 0; i < num_warps; i++) {
            block_sum += warp_sums[i];
        }
        d_out[blockIdx.x] = block_sum;
    }
}
```

#### 4.3.6.2 扫描

`inclusive_scan` 和 `exclusive_scan` 可在任意组大小上使用，可选指定归约运算符（同上表）。

```c
namespace cg = cooperative_groups;
cg::thread_block block = cg::this_thread_block();
cg::thread_block_tile<32> tile = cg::tiled_partition<32>(block);
int val = data[block.thread_rank()];
// 使用 __shfl_up_sync 实现 exclusive scan
int scan_val = val;
for (int offset = 1; offset < tile.size(); offset <<= 1) {
    int n = __shfl_up_sync(0xFFFFFFFF, scan_val, offset);
    if (tile.thread_rank() >= offset) scan_val += n;
}
int exclusive_sum = __shfl_up_sync(0xFFFFFFFF, scan_val, 1);
if (tile.thread_rank() == 0) exclusive_sum = 0;
result[block.thread_rank()] = exclusive_sum;
```

#### 4.3.6.3 从组中挑选一个

- `invoke_one`：从调用组中选择单一任意线程，用该线程调用供应函数（带所提供参数）。
- `invoke_one_broadcast`：同上，但调用结果广播到组中所有线程。
- 注意：`invoke_one_broadcast` 仅支持 tile 类型（`thread_block_tile` 或 `coalesced_group`），不支持直接传入 `thread_block`（广播需要 warp 级 shuffle）。
- 线程选择机制**不保证确定性**。

```c
__global__ void invokeOneBroadcastExample(int *d_out) {
    namespace cg = cooperative_groups;
    // 获取当前线程块，并创建 warp 级别的 tile
    cg::thread_block block = cg::this_thread_block();
    cg::thread_block_tile<32> tile = cg::tiled_partition<32>(block);
    // lambda 表达式：代表单线程要执行的计算逻辑
    // 假设我们让选定的线程计算 42 * 2 = 84
    auto compute_func = []() -> int {
        int result = 42 * 2;
        return result;
    };
    // 调用 invoke_one_broadcast
    // tile 内所有线程都会等待，直到 1 个被选中的线程执行完 compute_func，
    // 并将结果（84）广播回给 tile 内所有线程。
    int broadcasted_val = cg::invoke_one_broadcast(tile, compute_func);
    // 将结果写入全局内存
    if (block.thread_rank() == 0) {
        *d_out = broadcasted_val;
    }
}
```

### 4.3.7 异步数据移动

协作组 `memcpy_async` 提供全局内存与共享内存之间的异步拷贝，特别适用于优化内存传输、重叠计算与数据传输。`memcpy_async` 用作"预取"（需要数据之前加载）；`wait` 强制组中所有线程等待异步传输完成——数据可在共享内存访问前，组中所有线程都必须调用 `wait`。

```c
__global__ void kernel(int* global_data) {
    cg::thread_block tb = cg::this_thread_block();
    const size_t elementsPerThreadBlock = 16 * 1024;
    const size_t elementsInShared = 128;
    __shared__ int local_smem[elementsInShared];
    size_t copy_count;
    size_t index = 0;
    while (index < elementsPerThreadBlock) {
        cg::memcpy_async(tb, local_smem, elementsInShared, global_data + index, elementsPerThreadBlock - index);
        copy_count = min(elementsInShared, elementsPerThreadBlock - index);
        cg::wait(tb);
        index += copy_count;
    }
}
```

#### 4.3.7.1 Memcpy Async 对齐要求

`memcpy_async` 仅在**源地址位于全局内存、目标地址位于共享内存、且两者至少 4 字节对齐**时才是异步的。最佳性能：共享内存和全局内存都 **16 字节对齐**。

### 4.3.8 大规模组

协作组允许跨越整个网格的大组，前述所有功能可用于大组，但有一个显著例外：**同步整个网格需要使用 `hggcLaunchCooperativeKernel` 运行时启动 API**。

#### 4.3.8.1 何时使用 hggcLaunchCooperativeKernel

`hggcLaunchCooperativeKernel` 用于启动采用协作组的单设备核函数，专为需要块间同步的核函数设计：核函数中所有线程可在整个网格范围同步协作（传统核函数只允许线程块内同步）。它确保启动是**原子的**——API 调用成功则提供的线程块数量将全部在指定设备上启动。

良好做法：先查询设备属性 `hggcDevAttrCooperativeLaunch` 确认支持：

```c
int dev = 0;
int supportsCoopLaunch = 0;
hggcDeviceGetAttribute(&supportsCoopLaunch, hggcDevAttrCooperativeLaunch, dev);
```

比赛关联：warp 级 `__shfl_down_sync` 归约是 Softmax/RMSNorm/LayerNorm kernel 的基本构件（Qwen3.5 的 RMSNorm 直接受益）；`tiled_partition<32>` + scan 可用于采样阶段的 prefix-sum；grid 级协作启动适合 persistent kernel 形态的全模型融合。

---

## 4.4 延迟加载（Lazy Loading）

### 4.4.1 简介

延迟加载通过**等到需要时才加载 HGGC 模块**来减少程序初始化时间。对只使用其所含核函数一小部分的程序（使用库时很常见）特别有效。设计为在遵循 HGGC 编程模型时对开发者透明（见 4.4.4 潜在风险）。通过 **`HGGC_MODULE_LOADING` 环境变量**控制。

### 4.4.2 延迟加载的要求

#### 4.4.2.1 核函数要求

延迟加载不影响包含管理变量（managed variables）的模块，这些模块仍将 eagerly 加载。

### 4.4.3 使用方法

#### 4.4.3.1 启用与禁用

- `HGGC_MODULE_LOADING=2`：**启用**延迟加载。
- `HGGC_MODULE_LOADING=1`：**禁用**延迟加载。

#### 4.4.3.2 在运行时检查延迟加载是否启用

驱动 API `hgModuleGetLoadingMode` 可确定延迟加载是否启用（调用前必须先初始化 HGGC）：

```c
#include <hggc.h>
#include <assert.h>
#include <iostream>
int main() {
    HGmoduleLoadingMode mode;
    assert(HGGC_SUCCESS == hgInit(0));
    assert(HGGC_SUCCESS == hgModuleGetLoadingMode(&mode));
    std::cout << "HGGC Module Loading Mode is " << ((mode == HG_MODULE_LAZY_LOADING) ? "lazy" : "eager") << std::endl;
    return 0;
}
```

#### 4.4.3.3 在运行时强制模块 eager 加载

核函数和变量的加载自动发生，无需显式加载。即使不执行核函数，也可通过以下方式显式加载：

- `hgModuleGetFunction()` 会导致模块被加载到设备内存中；
- `hggcFuncGetAttributes()` 会导致核函数被加载到设备内存中。

> NOTE：`hgModuleLoad()` **不能保证**模块会被立即加载。

### 4.4.4 潜在风险

延迟加载设计为使用时不需修改应用，但应用不完全符合编程模型时有以下注意事项。

#### 4.4.4.1 对并发核函数执行的影响

一些程序错误地假设并发核函数执行有保证。若需跨核函数同步但核函数执行已被序列化，可能死锁。为减少影响：

- 启动之前**预加载所有希望并发执行的核函数**；或
- 用 `HGGC_MODULE_LOADING=1` 运行，强制急迫加载数据（而不强制每个函数急迫加载）。

#### 4.4.4.2 大内存分配

延迟加载把模块内存分配从程序初始化推迟到接近执行时间。若应用启动时分配整个 VRAM，HGGC 运行时可能无法为模块分配内存。解决方案：

- 用 `hggcMallocAsync()` 代替启动时分配整个 VRAM 的分配器；
- 添加缓冲区余量以补偿核函数的延迟加载；
- 在初始化分配器之前预加载程序将使用的所有核函数。

#### 4.4.4.3 对性能测量的影响

延迟加载可能把 HGGC 模块初始化**移入被测量的执行窗口**，扭曲性能测量。为避免：

- 测量之前至少执行一次**预热迭代**；
- 启动被测核函数之前先预加载它。

比赛关联：**直接关系 TTFT 测量真实性**——首次推理若触发模块/核函数延迟加载，初始化开销会算进 TTFT。比赛提交前应：固定 `HGGC_MODULE_LOADING` 取值并实测两种模式、预热迭代、用 `hgModuleGetFunction()`/`hggcFuncGetAttributes()` 预加载全部 kernel，确保 TTFT 测的是推理本身而非加载开销；同时注意延迟加载与"启动时占满 VRAM"的显存规划冲突。

---

## 4.5 异步屏障与流水线

异步屏障扩展 HGGC 同步功能，超越 `__syncthreads()` 和 `__syncwarp()`，实现细粒度、非阻塞协调以及更好的通信-计算重叠。本节介绍 `hggc::barrier` API。

### 4.5.1 初始化

初始化必须在任何线程开始参与屏障之前发生。

```c
// HGGC C++ hggc::barrier
#include <hggc/barrier>
#include <cooperative_groups.h>
__global__ void barrier_setup_demo()
{
    __shared__ hggc::barrier<hggc::thread_scope_block> blk_bar;
    auto grp = cooperative_groups::this_thread_block();
    if (grp.thread_rank() == 0)
    {
        init(&blk_bar, grp.size());
    }
    grp.sync();
}
```

### 4.5.2 屏障的阶段：到达（Arrival）、倒计时（Countdown）、完成（Completion）和重置（Reset）

- 屏障对象跟踪各线程的 `arrive()` 调用：每次 `arrive()` 使内部计数器递增（倒计时递减），达到预设期望值后屏障进入完成状态，等待中的线程可继续。
- 若线程调用 `token=bar.arrive()` 且在调用 `bar.wait(std::move(token))` 之前阶段没有翻转（仍为零），线程不阻塞；若线程在 `bar.wait(std::move(token))` 中被阻塞时阶段提前，则线程被解除阻塞。

使用规则（复杂 arrive/wait 模式中何时可能/不可能重置）：

- 线程对 `token=bar.arrive()` 和 `bar.wait(std::move(token))` 的调用必须按顺序进行：`arrive()` 发生在屏障当前阶段，`wait()` 发生在同一或下一阶段。
- `bar.arrive()` 必须发生在屏障计数器非零时。初始化后，若 `arrive()` 使倒计时达到零，必须先有对 `bar.wait(std::move(token))` 的调用，屏障才能用于后续 `arrive()`。
- 只能用**当前阶段或前一阶段**的令牌对象调用 `bar.wait()`；其他令牌值行为未定义。

#### 4.5.2.1 Warp 缠绕（Warp Entanglement）

Warp 分歧（Divergence）影响 arrive-on 操作更新屏障的次数：warp 完全收敛时屏障仅更新一次；完全发散时应用 32 个单独更新。**建议由收敛线程使用 `arrive-on(bar)`** 以最小化更新；前述代码使线程分歧时，应先 `__syncwarp` 重新汇聚 warp 再调用 arrive-on。

### 4.5.3 早期退出

需从循环提前返回但保持同步不变量时，用 `arrive_and_drop()`：减少屏障的预期到达计数，并把调用线程从屏障删除。

```c
// HGGC C++ hggc::barrier
#include <hggc/barrier>
#include <cooperative_groups.h>
__device__ bool should_terminate();
__global__ void adaptive_worker(int iterations)
{
    __shared__ hggc::barrier<hggc::thread_scope_block> sync_bar;
    auto grp = cooperative_groups::this_thread_block();
    if (grp.thread_rank() == 0)
    {
        init(&sync_bar, grp.size());
    }
    grp.sync();
    for (int step = 0; step < iterations; ++step)
    {
        if (should_terminate())
        {
            sync_bar.arrive_and_drop();
            return;
        }
        auto phase = sync_bar.arrive();
        /* 在 arrive 与 wait 之间可执行不依赖其他线程的独立计算 */
        sync_bar.wait(std::move(phase));
    }
    /* 所有存活线程均已到达，可安全读取共享数据 */
}
```

### 4.5.4 完成函数（Completion Function）

屏障完成后立即执行自定义代码：向屏障构造函数传递可调用对象。

```c
// HGGC C++ hggc::barrier
#include <hggc/barrier>
#include <cooperative_groups.h>
#include <functional>
namespace cg = cooperative_groups;
__device__ int branch_compute(int *, int);
__device__ int solo_work(int *, int);
__global__ void block_reduce(int *input, int totalElems, int *result)
{
    auto grp = cg::this_thread_block();
    constexpr int THREADS_PER_BLK = 128;
    __shared__ int tile[THREADS_PER_BLK];
    assert(THREADS_PER_BLK == grp.size());
    assert(totalElems % THREADS_PER_BLK == 0);
    auto on_phase_complete = [&]
    {
        int partial = 0;
        for (int k = 0; k < THREADS_PER_BLK; ++k)
        {
            partial += tile[k];
        }
        *result += partial;
    };
    using callback_t = decltype(on_phase_complete);
    using bar_type = hggc::barrier<hggc::thread_scope_block,
                                   callback_t>;
    __shared__ std::aligned_storage<sizeof(bar_type),
                                    alignof(bar_type)>
        bar_mem;
    bar_type *sync_bar = reinterpret_cast<bar_type*>(&bar_mem);
    if (grp.thread_rank() == 0)
    {
        new (sync_bar) bar_type(grp.size(), on_phase_complete);
    }
    grp.sync();
    for (int i = 0; i < totalElems; i += THREADS_PER_BLK)
    {
        tile[grp.thread_rank()] = input[i] + *result;
        auto phase = sync_bar->arrive();
        // 此处可执行独立计算。
        sync_bar->wait(std::move(phase));
    }
    grp.sync();
    if (grp.thread_rank() == 0)
    {
        sync_bar->~bar_type();
    }
    grp.sync();
}
```

### 4.5.5 使用屏障的生产者-消费者模式

生产者填充缓冲区并发信号表示缓冲区已满，但**不等待**该信号。实现完全的生产者/消费者并发至少需要**双缓冲**，每个缓冲区需要**两个屏障**。

```c
// HGGC C++ hggc::barrier
using barrier_t = hggc::barrier<hggc::thread_scope_block>;

__device__ void fill_buffer(barrier_t buf_available[], barrier_t buf_ready[], float *shared_data, int chunk_size, float *src, int total)
{
    for (int step = 0; step < total / chunk_size; ++step)
    {
        buf_available[step % 2].arrive_and_wait(); /* 等待 slot (step%2) 可写入 */
        /* 将源数据写入 shared_data 的对应 slot */
        barrier_t::arrival_token tok = buf_ready[step % 2].arrive(); /* 通知 slot (step%2) 数据就绪 */
    }
}

__device__ void process_buffer(barrier_t buf_available[], barrier_t buf_ready[], float *shared_data, int chunk_size, float *dst, int total)
{
    barrier_t::arrival_token tok_a = buf_available[0].arrive(); /* slot 0 初始可写 */
    barrier_t::arrival_token tok_b = buf_available[1].arrive(); /* slot 1 初始可写 */
    for (int step = 0; step < total / chunk_size; ++step)
    {
        buf_ready[step % 2].arrive_and_wait(); /* 等待 slot (step%2) 数据就绪 */
        /* 处理 shared_data 的 slot (step%2) */
        buf_available[step % 2].arrive(); /* 释放 slot (step%2) 以供下次写入 */
    }
}

__global__ void dual_buffer_pipeline(int total, float *src, float *dst, int chunk_size)
{
    constexpr int warpSize = 32;
    /* 共享内存分为两个 slot，每个大小为 chunk_size，
       交替用于写入和处理 */
    extern __shared__ float shared_data[];
    /* sync[0]/sync[1] 标记 slot 0/1 是否可写入，
       sync[2]/sync[3] 标记 slot 0/1 的数据是否就绪 */
    #pragma hggc_diag_suppress static_var_with_dynamic_init
    __shared__ hggc::barrier<hggc::thread_scope_block> sync[4];
    if (threadIdx.x < 4)
    {
        init(&sync[threadIdx.x], blockDim.x);
    }
    __syncthreads();
    // ...
}
```

（注：原文 PDF 中两个 `__device__` 函数签名在行尾被截断，参数按语义补全为 `int total`、`float *dst`——需查原文确认。）

示例说明：第一个 warp 专门填充（写入），其余 warp 处理（读取）。所有线程参与每个屏障的 arrive（`sync[].arrive()` 或 `sync[].arrive_and_wait()`），因此每个屏障预期到达计数等于 `blockDim.x`。
写入线程等待处理线程通过 `buf_available` 屏障发出 slot 可写信号；等待屏障需先 `arrive()` 取令牌再 `wait(token)`，`arrive_and_wait()` 合并两步：

```c
sync[k].arrive_and_wait();
/* 相当于 */
sync[k].wait(sync[k].arrive());
```

写入线程完成填充后通过到达 `buf_ready` 屏障通知数据就绪（`buf_ready[step%2].arrive()`），此时不阻塞，继续等下一个 slot 可写——双缓冲核心：一个 slot 被处理的同时另一个可写入。
处理线程启动时先把两个 slot 都标记可写；每次迭代等待当前 slot 数据就绪（`buf_ready[step%2].arrive_and_wait()`），处理完释放该 slot（`buf_available[step%2].arrive()`），再等下一个 slot。

### 4.5.6 流水线（Pipelines）

流水线用于分阶段处理工作、协调多缓冲生产者-消费者模式，常用于重叠计算与异步数据复制。本节介绍 `hggc::pipeline` API。

#### 4.5.6.1 初始化

`hggc::pipeline` 可在不同线程作用域创建。除 `hggc::thread_scope_thread` 外的作用域需要一个 `hggc::pipeline_shared_state<scope, count>` 对象协调参与线程——封装有限资源，使流水线能处理多达 count 个并发阶段。

```c
// 在线程作用域创建流水线
constexpr auto scope = hggc::thread_scope_thread;
hggc::pipeline<scope> pipeline = hggc::make_pipeline();
// 在块作用域创建流水线
constexpr auto scope = hggc::thread_scope_block;
constexpr auto stages_count = 2;
__shared__ hggc::pipeline_shared_state<scope, stages_count> shared_state;
auto pipeline = hggc::make_pipeline(group, &shared_state);
```

流水线可是**统一的（unified）**或**分区的（partitioned）**：统一流水线中所有线程既是生产者又是消费者；分区流水线中每个线程要么是生产者要么是消费者，生命周期内角色不变。**线程本地流水线不能被分区**。创建分区流水线需向 `hggc::make_pipeline()` 提供生产者数量或线程角色：

```c
// 创建一个分区的块级流水线，其中只有线程0是生产者
constexpr auto scope = hggc::thread_scope_block;
constexpr auto stages_count = 2;
__shared__ hggc::pipeline_shared_state<scope, stages_count> shared_state;
auto thread_role = (group.thread_rank() == 0) ? hggc::pipeline_role::producer : hggc::pipeline_role::consumer;
auto pipeline = hggc::make_pipeline(group, &shared_state, thread_role);
```

为支持分区，共享 `hggc::pipeline` 有额外开销（每阶段使用一组共享内存屏障同步），即使流水线统一且可改用 `__syncthreads()` 也如此。**可能时用线程本地流水线避免这些开销。**

#### 4.5.6.2 提交工作

向流水线阶段提交工作：

- `pipeline.producer_acquire()`：生产者线程集体获取流水线头部；
- 向流水线头提交异步操作（如 `memcpy_async`）；
- `pipeline.producer_commit()`：集体提交（推进）流水线头。

若所有资源都在使用，`producer_acquire()` 阻塞生产者线程，直到消费者释放下一阶段资源。

#### 4.5.6.3 消费工作

从已提交阶段消费：

- `pipeline.consumer_wait()`：消费者线程集体等待尾部（最老）阶段完成；
- `pipeline.consumer_release()`：集体释放阶段。

对 `hggc::pipeline<hggc::thread_scope_thread>` 还可用友元函数 `hggc::pipeline_consumer_wait_prior<N>()` 等待除最后 N 个阶段外的所有阶段完成（类似 primitives API 的 `__pipeline_wait_prior(N)`）。

#### 4.5.6.4 Warp 纠缠

流水线机制在同一流水线内的 HGGC 线程间共享，提交的操作序列在 warp 内纠缠，某些情况下影响性能。

- **Commit**：提交操作被合并——流水线序列对所有收敛线程只递增一次，其提交的操作批量组合。warp 完全收敛：序列递增 1，所有提交操作批处理到同一阶段；完全发散：序列递增至 32，提交操作分散到不同阶段。
  - 设 PB 为 warp 共享流水线的实际操作序列：`PB = {BP0, BP1, BP2, …, BPL}`。
  - 设 TB 为线程感知的操作序列（就像序列仅由该线程的 commit 递增）：`TB = {BT0, BT1, BT2, …, BTL}`。`pipeline::producer_commit()` 返回值来自线程感知批次序列。
  - 线程感知序列中的索引总与实际 warp 共享序列中相等或更大的索引对齐；仅当所有提交从完全收敛线程调用时两序列相等。`BTn ≤ BPm`（n <= m）。
  - 完全发散 warp 示例：warp 共享实际序列 `PB = {0, 1, 2, 3, ..., 31}`（PL=31）；各线程感知序列均为 `TB = {0}`（TL=0，线程 0…31 皆同）。
- **Wait**：线程调用 `pipeline::consumer_wait()` 或 `pipeline_consumer_wait_prior<N>()` 等待感知序列 TB 中的批次完成。`consumer_wait()` 等价于 `pipeline_consumer_wait_prior<N>()`（N = PL）。wait_prior 变体等待实际序列中至少到包括 PL-N 的批次；因 TL <= PL，等待最多到包括 PL-N 的批次包含等待 TL-N 批次——**TL < PL 时线程会无意中等待额外的、更新的批次**。极端完全发散示例中每个线程可能等待全部 32 个批次。

> NOTE：建议通过汇聚线程执行 commit 调用以免过度等待，保持线程感知批次序列与实际序列对齐。操作前代码使线程发散时，应在提交前用 `__syncwarp` 重新汇聚 warp。

#### 4.5.6.5 提前退出

参与流水线的线程必须提前退出时，须在退出前显式放弃参与：`hggc::pipeline::quit()`。剩余线程可正常进行后续操作。

#### 4.5.6.6 跟踪异步内存操作

用流水线独立提交内存拷贝、等待完成并消费数据，集体把数据从全局内存复制到共享内存：

```c
// HGGC C++ hggc::pipeline 示例
#include <hggc/pipeline>
__global__ void example_kernel(const float *in)
{
    constexpr int block_size = 128;
    __shared__ __align__(sizeof(float)) float buffer[4 * block_size];
    // 为每个线程创建统一流水线
    hggc::pipeline<hggc::thread_scope_thread> pipeline = hggc::make_pipeline();
    // 内存复制第一阶段
    pipeline.producer_acquire();
    // 每个线程获取第一块的一个元素
    hggc::memcpy_async(buffer, in, sizeof(float), pipeline);
    pipeline.producer_commit();
    // 内存复制第二阶段
    pipeline.producer_acquire();
    // 每个线程获取第二和第三块的一个元素
    hggc::memcpy_async(buffer + block_size, in + block_size, sizeof(float), pipeline);
    hggc::memcpy_async(buffer + 2 * block_size, in + 2 * block_size, sizeof(float), pipeline);
    pipeline.producer_commit();
    // 内存复制第三阶段
    pipeline.producer_acquire();
    // 每个线程获取最后一块的一个元素
    hggc::memcpy_async(buffer + 3 * block_size, in + 3 * block_size, sizeof(float), pipeline);
    pipeline.producer_commit();
    // 等待最旧阶段(等待第一阶段)
    pipeline.consumer_wait();
    pipeline.consumer_release();
    // __syncthreads();
    // 使用第一阶段的数据
    // 等待最旧阶段(等待第二阶段)
    pipeline.consumer_wait();
    pipeline.consumer_release();
    // __syncthreads();
    // 使用第二阶段的数据
    // 等待最旧阶段(等待第三阶段)
    pipeline.consumer_wait();
    pipeline.consumer_release();
    // __syncthreads();
    // 使用第三阶段的数据
}
```

#### 4.5.6.7 使用流水线的生产者-消费者模式

4.5.5 节用空间划分线程块 + 异步屏障实现生产者-消费者；有了 `hggc::pipeline`，可用**单一分区流水线 + 每个数据缓冲区一个阶段**简化实现，而非每缓冲区两个异步屏障。

### 4.5.7 异步数据拷贝（Asynchronous Data Copies）

涵盖：元素级拷贝的 `async_cp`、批量（一维和多维）传输的张量内存拷贝器 **AIU**，及其与异步屏障/流水线的集成。

#### 4.5.7.1 使用 async_cp

许多应用需在全局内存和共享内存间频繁移动小数据元素或不规则访问。`async_cp` 目标是提供全局→共享的高效异步传输机制，用于较小的逐元素传输，同时通过重叠执行更好利用计算资源。

##### 4.5.7.1.1 ppu.async.cp

```text
ppu.cp.async.ca.shared.global [shrd], [gbl + 4], 4;
```

- `ppu.cp.async` 是**非阻塞指令**：发起异步拷贝，从源操作数 src（全局状态空间）拷到目标 dst（共享状态空间）。
- `cp-size`：整数常量，指定拷贝到 dst 的字节数。
- 可选 32 位整数操作数 `src-size`：从 src 实际拷贝的字节数，必须**小于** cp-size；dst 中剩余字节**用零填充**。
- 异步拷贝**仅支持全局内存 → 共享内存**方向。
- 指针需按拷贝数据大小对齐到 **4、8 或 16 字节**；共享内存和全局内存对齐都是 **128 字节**时性能最佳。
- 使用 **LDGSTS** 的数据传输是异步的，建模为异步线程操作——发起线程可在硬件异步复制数据的同时继续计算。

##### 4.5.7.1.2 条件代码中的批处理加载

条件代码导致分支发散：循环中多个小加载只有满足条件的线程执行，其余闲置。用异步拷贝直接从全局内存加载到共享内存——既减少寄存器使用（直接拷入共享内存），又确保所有全局内存加载都在飞行中（in flight）。

```c
// HGGC C++ hggc::memcpy_async
#include <cooperative_groups.h>
#include <hggc/barrier>
__global__ void block_relu_kernel(const float *left, const float *center, const float *right)
{
    auto block = cooperative_groups::this_thread_block();
    auto thread = cooperative_groups::this_thread();
    using barrier_t = hggc::barrier<hggc::thread_scope_block>;
    __shared__ barrier_t barrier;
    __shared__ float buffer[8 + 32 + 8];
    // 初始化同步对象。
    if (block.thread_rank() == 0) {
        init(&barrier, block.size());
    }
    __syncthreads();
    // 版本1: 在各个线程中发出拷贝。
    if (tid < 8) {
        hggc::memcpy_async(buffer + tid, left + tid, hggc::aligned_size_t<4>(sizeof(float)), barrier); // 左halo
        // 或 hggc::memcpy_async(thread, buffer + tid, left + tid, hggc::aligned_size_t<4>(sizeof(float)), barrier);
    } else if (tid >= 32 - 8) {
        hggc::memcpy_async(buffer + tid + 16, right + tid, hggc::aligned_size_t<4>(sizeof(float)), barrier); // 右halo
        // 或 hggc::memcpy_async(thread, buffer + tid + 16, right + tid, hggc::aligned_size_t<4>(sizeof(float)), barrier);
    }
    // 等待拷贝完成。
    auto token = barrier.arrive();
    barrier.wait(std::move(token));
    __syncthreads();
}
```

```c
// HGGC C++ cooperative_groups::memcpy_async
#include <cooperative_groups.h>
#include <cooperative_groups/memcpy_async.h>
namespace cg = cooperative_groups;
__global__ void block_relu_kernel(const float *left, const float *center, const float *right)
{
    cg::thread_block block = cg::this_thread_block();
    // 左halo (8个元素) - 中心 (32个元素) - 右halo (8个元素).
    __shared__ float buffer[8 + 32 + 8];
    // 跨所有线程协作发出拷贝。
    cg::memcpy_async(block, buffer, left, 8 * sizeof(float)); // 左halo
    cg::memcpy_async(block, buffer + 8, center, 32 * sizeof(float)); // 中心
    cg::memcpy_async(block, buffer + 40, right, 8 * sizeof(float)); // 右halo
    cg::wait(block); // 等待所有拷贝完成。
    __syncthreads();
    // 计算stencil。
}
```

##### 4.5.7.1.3 预取数据

迭代"拷贝-计算"模式中，用异步拷贝从全局内存预取到共享内存，把未来迭代的数据传输延迟隐藏在当前迭代计算之下：

```c
// HGGC C++ hggc::memcpy_async
#include <cooperative_groups.h>
#include <hggc/pipeline>
template <size_t num_stages = 2 /* 具有num_stages阶段的流水线 */>
__global__ void prefetch_kernel(int* global_out, int const* global_in, size_t size, size_t batch_size) {
    auto grid = cooperative_groups::this_grid();
    auto block = cooperative_groups::this_thread_block();
    auto thread = cooperative_groups::this_thread();
    assert(size == batch_size * grid.size()); // 假设输入大小适合batch_size * grid_size
    extern __shared__ int shared[]; // num_stages * block.size() * sizeof(int) 字节
    size_t shared_offset[num_stages];
    for (int s = 0; s < num_stages; ++s) shared_offset[s] = s * block.size();
    hggc::pipeline<hggc::thread_scope_thread> pipeline = hggc::make_pipeline();
    auto block_batch = [&](size_t batch) -> int {
        return block.group_index().x * block.size() + grid.size() * batch;
    };
    // 用前"num_stages"批次填充流水线。
    for (int s = 0; s < num_stages; ++s) {
        size_t block_batch_idx = block_batch(s);
        hggc::memcpy_async(
            shared + shared_offset[s],
            global_in + block_batch_idx,
            hggc::aligned_size_t<4>(block.size() * sizeof(int)),
            pipeline);
        pipeline.producer_commit();
    }
    // 加载未来阶段"num_stages"超出当前计算批次。
    pipeline.producer_acquire();
    // ...
}
```

（注：原文 `producer_commit()`/`producer_acquire()` 因断行错位，已按语义移入循环——需查原文确认。）

##### 4.5.7.1.4 批量拷贝指令（AIU copy）

**AIU** 是 PPU 中专门负责数据搬运的硬件机制，支持更高效的异步数据加载，主要用于全局内存与共享内存之间高效传输**多维张量数据**。特点：

- 指令编程模型为**异步、bulk 风格**，AIU 是 **warp-level** 指令；
- 支持多维数据的异步搬移；
- AIU 写共享内存时采用 **swizzle memory layout** 解决 bank conflicts，开发者无需感知具体 swizzle layout；
- 从共享内存往寄存器加载 AIU 写入的数据时，要用 PPU 共享内存上**带 Swizzle 功能的读指令**解析 swizzle layout，并按 **Tile** 为单位完成数据加载。

详细指令介绍参考 aiu-copy 文档。

比赛关联：`ppu.cp.async` / `memcpy_async` + pipeline 多阶段预取是 GEMM/GEMV kernel 隐藏全局内存延迟的标准技法（权重、激活分块预取，对应 cuBLAS/CUTLASS 式流水）；AIU 的 swizzle 写共享内存免 bank conflict，直接利好 attention/MLP 的 tile 加载；异步屏障 arrive/wait 分离可在 GEMM 主循环中重叠 epilogue 计算。这些都是"系统级优化深度（算子融合、计算调度）"评分点的直接素材。

---

## 4.6 进程间通信与虚拟内存管理（IPC & VMM）

不同宿主进程管理的多块 PPU 之间通信，通过 **IPC API + 可 IPC 共享的内存缓冲区**实现：创建可跨进程移植的句柄，再用句柄获取指向对端 PPU 设备内存的、本进程内有效的设备指针（process-local device pointers）。

- 同一进程内，某宿主线程创建的设备内存指针/事件句柄可被进程内其他线程直接引用；但在创建进程之外无效。
- 跨进程访问设备内存与 HGGC 事件，必须用 **HGGC IPC 或 VMM API** 创建可移植句柄，并用标准宿主 OS IPC 机制（进程间共享内存、文件）共享给其他进程；然后用 IPC/VMM API 从句柄取回本进程有效的设备指针。
- 单节点单 OS 实例的可移植句柄方法同样用于多节点互连集群的 P2P 通信。多节点场景中 PPU 由各集群节点上独立 OS 实例的进程管理，需要在 OS 实例之上的抽象层——通过创建并交换 **"fabric" 句柄**实现多节点 PPU 对等体间通信。

> NOTE：HGGC IPC API 与 VMM API 各有优劣。**HGGC IPC API 目前只在 Linux 平台受支持**。VMM API 允许在内存分配时按分配粒度控制对等可访问性与共享，但需要使用 HGGC 驱动 API。

### 4.6.1 使用传统进程间通信 API 的 IPC

- `hggcIpcGetMemHandle()`：获取给定设备内存指针的 IPC 句柄。句柄可通过标准宿主 OS IPC 机制传给另一进程。
- `hggcIpcOpenMemHandle()`：用 IPC 句柄取回在另一进程内可用的有效设备指针。
- 事件句柄通过类似入口点共享。
- 典型用例：单个主进程生成一批输入数据，无需重新生成或复制即可提供给多个从进程。

> NOTE（重要限制）：
> - IPC API **只在 Linux 上受支持**；
> - **不支持** `hggcMallocManaged` 分配的内存；
> - 使用 HGGC IPC 通信的应用应使用**相同版本**的 HGGC driver 与 runtime 编译、链接、运行；
> - 出于性能原因，`hggcMalloc()` 分配可能从更大内存块中子分配（sub-allocate）。此时 IPC API 将共享**整个底层内存块**，其他子分配可能也被共享，引发进程间信息泄露。**建议仅共享大小按 8MiB 对齐的分配。**

### 4.6.2 使用虚拟内存管理 API 的 IPC

VMM API 允许创建可 IPC 共享的内存分配，并通过 OS 特定 IPC 句柄数据结构支持多种操作系统。

### 4.6.3 虚拟内存管理（VMM）

**传统分配模型的局限**：`hggcMalloc()` 返回的地址可直接用于 HGGC API 与设备端 kernel；跨设备访问用 `hggcEnablePeerAccess`，但有两个问题：

- **粒度过粗**：启用对等访问后，当前及未来所有分配都映射到目标设备，即使只需共享少量分配也要承担全量映射开销；
- **多节点扩展困难**：对等访问模型难以扩展到多节点场景。

**VMM API** 把 OS 中「地址保留」与「物理提交」两阶段分离的思想引入 PPU 内存管理：先保留连续虚拟地址范围（不分配物理内存），再按需把物理 PPU 内存映射进去。可精确选择哪些分配对哪些设备可见，不再依赖全局对等映射。

VMM 核心能力：

- **地址连续化**：非连续物理内存块映射到连续虚拟地址空间，减少碎片、提升利用率，适用于深度神经网络训练等大规模负载；
- **按需提交**：虚拟地址保留与物理分配独立，先保留大块地址区间再逐步映射物理内存，避免高成本拷贝或重分配；
- **动态增长**：不拷贝已有数据即可扩展分配，类似 CPU 侧 realloc 或 `std::vector` 扩容；
- **自定义分配器**：为构建复杂内存管理系统（**如大语言模型中的 KV-cache 动态管理**）提供底层原语，可改善吞吐与延迟；
- **多设备/多节点共享**：解耦虚拟地址与物理存储，创建统一虚拟地址空间并把数据动态映射到不同 PPU，优化跨设备通信、减少传输开销。

> NOTE：本节 API 需要系统支持 **UVA**。

#### 4.6.3.1 预备知识

##### 4.6.3.1.1 定义

- **Fabric 内存**：可通过高速互连 fabric 访问的内存。fabric 为多 PPU/多节点提供内存一致性与高带宽通信层，使其像访问统一 fabric 上的内存一样高效共享。HGGC 更高版本提供 VMM 分配句柄类型 **`HG_MEM_HANDLE_TYPE_FABRIC`**：受支持平台且 IMEX 守护进程运行时，该句柄允许节点内（经 MPI 等任意机制）及跨节点共享——多节点 Icnlink 系统中不同节点的 PPU 也能映射同一 fabric 内其他 PPU 的内存。
- **内存句柄**：VMM 中表示物理内存分配的不透明标识符，唯一标识一个物理内存分配，不暴露直接指针；支持跨进程/跨设备导出导入，促进内存共享与虚拟化。
- **IMEX 通道**：IMEX = internode memory exchange，跨节点 PPU 到 PPU 通信方案的一部分。IMEX 通道是 PPU 驱动特性，在 IMEX 域内为多用户/多节点环境提供基于用户的内存隔离（安全与隔离机制）。与 fabric 句柄直接相关，**多节点 PPU 通信中必须启用**：PPU 分配内存并希望其他节点 PPU 可访问时，先用 IMEX 通道导出安全的 fabric 句柄，该句柄只能被具有正确通道访问权限的远端进程导入。
- **单播内存访问**：特定设备/进程对某段物理内存受控、直接地映射访问，映射到唯一虚拟地址范围（与广播相对）——某个 PPU 被显式授予对所保留 VA 范围的读写权限。
- **多播内存访问**：通过多播机制把单个物理内存分配/区域同时映射到多个设备的虚拟地址空间，数据以"一对多"方式在多 PPU 间高效共享，减少冗余传输。VMM API 支持创建多播对象，绑定来自多个设备的物理内存分配。

##### 4.6.3.1.2 查询支持情况

使用前应先查询支持情况（随 PPU 架构、驱动版本、软件库变化）。

**VMM 支持**：

```c
int deviceSupportsVmm;
HGresult result = hgDeviceGetAttribute(&deviceSupportsVmm, HG_DEVICE_ATTRIBUTE_VIRTUAL_MEMORY_MANAGEMENT_SUPPORTED, device);
if (deviceSupportsVmm != 0) {
    // `device` supports Virtual Memory Management
}
```

（注：原文属性名在 PDF 行尾截断为 `HG_DEVICE_ATTRIBUTE_VIRTUAL_MEMORY_MANAGEM…`，后缀按命名惯例补全——需查原文确认。）

**Fabric 内存支持**：

```c
int deviceSupportsFabricMem;
HGresult result = hgDeviceGetAttribute(&deviceSupportsFabricMem, HG_DEVICE_ATTRIBUTE_HANDLE_TYPE_FABRIC_SUPPORTED, device);
if (deviceSupportsFabricMem != 0) {
    // `device` supports Fabric Memory
}
```

（注：同上，属性名后缀 `…_FABRIC_…` 截断后按惯例补全——需查原文确认。）

除用 `HG_MEM_HANDLE_TYPE_FABRIC` 作句柄类型、交换句柄时不需要 OS 原生 IPC 机制外，fabric 内存用法与其他句柄类型无区别。

**IMEX 通道支持**：IMEX 驱动通过创建字符设备 `alixpu-caps-imex-channels` 实现。使用 fabric 句柄共享前应验证两点：

1. 设备存在于 `/proc/dev` 下：

```text
cat /proc/dev | grep alixpu
alixpu
alixpu_ctl
alixpu-caps-imex-channels
```

2. 两个 HGGC 进程（导出者与导入者）都能访问同一 IMEX 通道文件。这些文件（如 `/dev/alixpu-caps-imex-channels/channel0`）是表示单个 IMEX 通道的节点，须由系统管理员创建，例如：

```bash
mknod /dev/alixpu-caps-imex-channels/channelN c <major_number> 0
```

该命令用从 `/proc/dev` 获取的主设备号创建 channelN。

#### 4.6.3.2 API 概览

VMM API 提供虚拟内存细粒度控制；是非常底层的 API，**需要直接使用 HGGC 驱动 API**，可用于单节点与多节点环境。

前置知识要求：OS 虚拟内存基础（页面与地址空间）、内存层级与硬件特性、IPC 方法（socket/消息传递）、内存访问权限安全性。

**VMM 工作流**：

1. 在源设备上分配物理内存；
2. 导出共享句柄（OS 特定句柄：仅单节点进程间；fabric 句柄：单节点或多节点，需启用 IMEX 通道）；
3. 通过某种进程间通信协议（开发者自选）把句柄共享给接收进程；
4. 接收进程用 VMM API 导入句柄；
5. 源进程与目标进程都保留一段将映射该物理内存的虚拟地址空间；
6. 为每个设备设置内存访问权限。

#### 4.6.3.3 单播内存共享

步骤：**分配并导出 → 共享并导入 → 保留并映射 → 访问权限 → 释放内存**。

##### 4.6.3.3.1 分配并导出

**分配物理内存**：第一步创建物理内存作为分配支撑（backing）。用 **`hgMemCreate`**，创建的分配不具有任何设备或主机映射。参数 `HGmemGenericAllocationHandle`（属性结构 `HGmemAllocationProp`）描述分配位置、是否共享到其他进程、物理属性等。**分配大小必须按粒度对齐**，粒度用 `hgMemGetAllocationGranularity` 查询。

OS 特定句柄（Linux）：

```c
HGmemGenericAllocationHandle allocatePhysicalMemory(int device, size_t size) {
    HGmemAllocationHandleType handleType = HG_MEM_HANDLE_TYPE_POSIX_FILE_DESCRIPTOR;
    HGmemAllocationProp prop = {};
    prop.type = HG_MEM_ALLOCATION_TYPE_PINNED;
    prop.location.type = HG_MEM_LOCATION_TYPE_DEVICE;
    prop.location.id = device;
    prop.requestedHandleTypes = handleType;
    size_t granularity = 0;
    hgMemGetAllocationGranularity(&granularity, &prop, HG_MEM_ALLOC_GRANULARITY_MINIMUM);
    // Ensure size matches granularity requirements for the allocation
    size_t padded_size = ROUND_UP(size, granularity);
    // Allocate physical memory
    HGmemGenericAllocationHandle allocHandle;
    hgMemCreate(&allocHandle, padded_size, &prop, 0);
    return allocHandle;
}
```

Fabric 句柄（仅句柄类型不同，`HG_MEM_HANDLE_TYPE_FABRIC`）：

```c
HGmemGenericAllocationHandle allocatePhysicalMemory(int device, size_t size) {
    HGmemAllocationHandleType handleType = HG_MEM_HANDLE_TYPE_FABRIC;
    HGmemAllocationProp prop = {};
    prop.type = HG_MEM_ALLOCATION_TYPE_PINNED;
    prop.location.type = HG_MEM_LOCATION_TYPE_DEVICE;
    prop.location.id = device;
    prop.requestedHandleTypes = handleType;
    size_t granularity = 0;
    hgMemGetAllocationGranularity(&granularity, &prop, HG_MEM_ALLOC_GRANULARITY_MINIMUM);
    // Ensure size matches granularity requirements for the allocation
    size_t padded_size = ROUND_UP(size, granularity);
    // Allocate physical memory
    HGmemGenericAllocationHandle allocHandle;
    hgMemCreate(&allocHandle, padded_size, &prop, 0);
    return allocHandle;
}
```

> NOTE：`hgMemCreate` 分配的内存由其返回的 `HGmemGenericAllocationHandle` 引用——**这不是指针，此内存尚不可访问**。

> NOTE：可用 `hgMemGetAllocationPropertiesFromHandle` 查询分配句柄属性。

**导出内存句柄**：`hgMemExportToShareableHandle`。OS 特定 IPC 句柄仅用于单节点；fabric 句柄单/多节点皆可。

OS 特定句柄（Linux）：

```c
HGmemAllocationHandleType handleType = HG_MEM_HANDLE_TYPE_POSIX_FILE_DESCRIPTOR;
HGmemGenericAllocationHandle handle = allocatePhysicalMemory(0, 1<<21);
int fd;
hgMemExportToShareableHandle(&fd, handle, handleType, 0);
```

Fabric 句柄：

```c
HGmemAllocationHandleType handleType = HG_MEM_HANDLE_TYPE_FABRIC;
HGmemGenericAllocationHandle handle = allocatePhysicalMemory(0, 1<<21);
HGmemFabricHandle fh;
hgMemExportToShareableHandle(&fh, handle, handleType, 0);
```

> NOTE：OS 特定句柄要求所有进程属于同一个 OS；fabric 特定句柄要求系统管理员启用 IMEX 通道。

##### 4.6.3.3.2 共享并导入

**共享句柄**：导出后用任意 IPC 协议共享给接收进程。OS 特定 IPC（如 Unix socket）性能高但仅限同机、不可移植；fabric 特定 IPC 更简单可移植但需系统级支持。

发送：OS 特定 IPC（Linux，Unix socket + SCM_RIGHTS 传 fd）：

```c
int ipcSendShareableHandle(int socket, int fd, pid_t process) {
    struct msghdr msg;
    struct iovec iov[1];
    union {
        struct cmsghdr cm;
        char* control;
    } control_un;
    size_t sizeof_control = CMSG_SPACE(sizeof(int)) * sizeof(char);
    control_un.control = (char*) malloc(sizeof_control);
    struct cmsghdr *cmptr;
    ssize_t readResult;
    struct sockaddr_un cliaddr;
    socklen_t len = sizeof(cliaddr);
    // 构造客户端地址，以便将可共享句柄发送给目标进程
    memset(&cliaddr, 0, sizeof(cliaddr));
    cliaddr.sun_family = AF_UNIX;
    char temp[20];
    sprintf(temp, "%s%u", "/tmp/", process);
    strcpy(cliaddr.sun_path, temp);
    len = sizeof(cliaddr);
    // 将对应的可共享句柄发送给客户端
    int sendfd = fd;
    msg.msg_control = control_un.control;
    msg.msg_controllen = sizeof_control;
    cmptr = CMSG_FIRSTHDR(&msg);
    cmptr->cmsg_len = CMSG_LEN(sizeof(int));
    cmptr->cmsg_level = SOL_SOCKET;
    cmptr->cmsg_type = SCM_RIGHTS;
    memmove(CMSG_DATA(cmptr), &sendfd, sizeof(sendfd));
    msg.msg_name = (void *)&cliaddr;
    msg.msg_namelen = sizeof(struct sockaddr_un);
    iov[0].iov_base = (void *)"";
    iov[0].iov_len = 1;
    msg.msg_iov = iov;
    msg.msg_iovlen = 1;
    ssize_t sendResult = sendmsg(socket, &msg, 0);
    if (sendResult <= 0) {
        perror("IPC failure: Sending data over socket failed");
        free(control_un.control);
        return -1;
    }
    free(control_un.control);
    return 0;
}
```

发送：Fabric IPC：

```c
MPI_Send(&fh, sizeof(HGmemFabricHandle), MPI_BYTE, 1, 0, MPI_COMM_WORLD);
```

接收：OS 特定 IPC（Linux）：

```c
int ipcRecvShareableHandle(int socket, int* fd) {
    struct msghdr msg = {0};
    struct iovec iov[1];
    struct cmsghdr cm;
    // 使用联合体以满足控制数组的对齐要求
    union {
        struct cmsghdr cm;
        // 此写法在 QNX 上不可用，因为 QNX 的 CMSG_SPACE 调用了 __cmsg_alignbytes，
        // 而 __cmsg_alignbytes 是运行时函数而非编译期宏
        // char control[CMSG_SPACE(sizeof(int))]
        char* control;
    } control_un;
    size_t sizeof_control = CMSG_SPACE(sizeof(int)) * sizeof(char);
    control_un.control = (char*) malloc(sizeof_control);
    struct cmsghdr *cmptr;
    ssize_t n;
    int receivedfd;
    char dummy_buffer[1];
    ssize_t sendResult;
    msg.msg_control = control_un.control;
    msg.msg_controllen = sizeof_control;
    iov[0].iov_base = (void *)dummy_buffer;
    iov[0].iov_len = sizeof(dummy_buffer);
    msg.msg_iov = iov;
    msg.msg_iovlen = 1;
    if ((n = recvmsg(socket, &msg, 0)) <= 0) {
        perror("IPC failure: Receiving data over socket failed");
        free(control_un.control);
        return -1;
    }
    if (((cmptr = CMSG_FIRSTHDR(&msg)) != NULL) &&
        (cmptr->cmsg_len == CMSG_LEN(sizeof(int)))) {
        if ((cmptr->cmsg_level != SOL_SOCKET) || (cmptr->cmsg_type != SCM_RIGHTS)) {
            free(control_un.control);
            return -1;
        }
        memmove(&receivedfd, CMSG_DATA(cmptr), sizeof(receivedfd));
        *fd = receivedfd;
    } else {
        free(control_un.control);
        return -1;
    }
    free(control_un.control);
    return 0;
}
```

接收：Fabric IPC：

```c
MPI_Recv(&fh, sizeof(HGmemFabricHandle), MPI_BYTE, 1, 0, MPI_COMM_WORLD);
```

**导入内存句柄**：`hgMemImportFromShareableHandle`。OS 特定句柄仅单节点；fabric 句柄单/多节点皆可。

```c
// OS 特定句柄（Linux）
HGmemAllocationHandleType handleType = HG_MEM_HANDLE_TYPE_POSIX_FILE_DESCRIPTOR;
hgMemImportFromShareableHandle(handle, (void*) &fd, handleType);
// Fabric 句柄
HGmemAllocationHandleType handleType = HG_MEM_HANDLE_TYPE_FABRIC;
hgMemImportFromShareableHandle(handle, (void*) &fh, handleType);
```

##### 4.6.3.3.3 保留并映射

**保留虚拟地址范围**：VMM 中地址与内存概念分离，应用必须划出能容纳 `hgMemCreate` 所建分配的地址范围——保留范围至少不小于计划放入的所有物理分配大小之和。用 **`hgMemAddressReserve`** 保留；保留的 VA 范围不关联任何设备/主机物理内存，可映射到系统中任意设备的内存块，从而获得由不同设备内存支撑的连续 VA。归还用 **`hgMemAddressFree`**——调用前必须确保整个 VA 范围已解除映射（unmap）。概念上类似 Linux `mmap`/`munmap` 或 Windows `VirtualAlloc`/`VirtualFree`：

```c
HGdeviceptr ptr;
// `ptr` holds the returned start of virtual address range reserved.
HGresult result = hgMemAddressReserve(&ptr, size, 0, 0, 0); // alignment = 0 for default alignment
```

**映射内存**：`hgMemAddressReserve` 得到的地址范围与 `hgMemCreate` / `hgMemImportFromShareableHandle` 得到的物理分配，通过 **`hgMemMap`** 关联。只要预留地址空间足够，可把来自多个设备的分配关联到连续虚拟地址范围。解除关联用 **`hgMemUnmap`**；不在已映射 VA 预留范围上重复创建映射的前提下，可对同一地址范围任意次映射/解除映射：

```c
HGdeviceptr ptr;
// `ptr`：先前通过 hgMemAddressReserve 预留的地址范围中的地址。
// `allocHandle`：先前通过 hgMemCreate 获取的 HGmemGenericAllocationHandle。
HGresult result = hgMemMap(ptr, size, 0, allocHandle, 0);
```

##### 4.6.3.3.4 访问权限

用 `hgMemMap` 把分配映射到地址范围**并不会使该地址可访问**——HGGC kernel 访问会崩溃。必须在源设备与访问设备上用 **`hgMemSetAccess`** 显式设置访问控制：

```c
void setAccessOnDevice(int device, HGdeviceptr ptr, size_t size) {
    HGmemAccessDesc accessDesc = {};
    accessDesc.location.type = HG_MEM_LOCATION_TYPE_DEVICE;
    accessDesc.location.id = device;
    accessDesc.flags = HG_MEM_ACCESS_FLAGS_PROT_READWRITE;
    // 设置地址的访问权限
    hgMemSetAccess(ptr, size, &accessDesc, 1);
}
```

`hggcEnablePeerAccess` 强制把过去与未来所有 `hggcMalloc` 分配映射到目标对等设备（方便但有性能影响）；VMM 在**分配粒度**上控制访问，以最小开销实现对等映射。

##### 4.6.3.3.5 释放内存

源进程与目标进程都应依次使用 `hgMemUnmap` → `hgMemRelease` → `hgMemAddressFree`：先解除映射（物理内存与 VA 分离），再释放物理内存归还系统，最后释放保留的 VA 范围。按此顺序确保干净完整释放：

```c
hgMemUnmap(ptr, size);
hgMemRelease(handle);
hgMemAddressFree(ptr, size);
```

> NOTE：OS 特定场景下，导出的句柄必须使用 `fclose` 关闭；不适用于 fabric 场景。

#### 4.6.3.4 高级配置

##### 4.6.3.4.1 内存类型

VMM 允许分配某些设备支持的特殊类型内存：`hgMemCreate` 时用 `HGmemAllocationProp::allocFlags` 指定内存类型需求，选择性启用特定内存特性。应用必须确保所请求内存类型被设备支持。

##### 4.6.3.4.2 虚拟别名支持

VMM API 允许对同一分配用多个不同虚拟地址分别调用 `hgMemMap`，创建多个虚拟内存映射或"代理（proxy）"——**虚拟别名（virtual aliasing）**。

- 除非 TIX 另有说明，对某个代理的写入，在写入设备操作（网格启动、memcpy、memset 等）完成之前，与该内存的其他代理被认为是**不一致且不相干（incoherent）**的。写入设备操作之前已在 PPU 上存在、但在写入设备操作完成后才读取的网格，也被认为具有不一致且不相干的代理。

未定义行为示例（A、B 是同一分配的虚拟别名）：

```c
__global__ void write_and_read(char *A, char *B) {
    *A = 0x1;
    printf("%d\n", *B); // 未定义行为！*B 可能取到先前的值，
                        // 也可能取到某个中间状态的值。
}
```

已定义行为（两个 kernel 通过 streams/events 单调排序）：

```c
__global__ void write_kernel(char *A) {
    *A = 0x1;
}
__global__ void read_kernel(char *B) {
    printf("%d\n", *B); // 假设 read_kernel 在 write_kernel 完成后才启动，
                        // 则 *B == *A == 0x1
}
hggcMemcpyAsync(B, input, size, stream1); // 别名访问允许出现在
                                          // 操作边界处
write_kernel<<<1,1,0,stream1>>>(A);
// 允许 write_kernel 访问 A
hggcEventRecord(event, stream1);
hggcStreamWaitEvent(stream2, event);
read_kernel<<<1,1,0,stream2>>>(B);
hggcStreamWaitEvent(stream3, event);
hggcMemcpyAsync(output, B, size, stream3); // read_kernel 和 hggcMemcpy
                                           //（均为读操作）都会等待
                                           // write_kernel（写操作）
                                           // 完成后再执行
```

比赛关联：VMM 的“自定义分配器”能力可用于 Qwen3.5-2B 的单卡 KV/Mamba cache 动态管理：用 `hgMemAddressReserve` 预留虚拟地址空间，随生成长度用 `hgMemCreate`+`hgMemMap` 按需提交物理页，避免按最大上下文预分配。fabric、IMEX 和 IPC 属于多卡/多进程扩展，不进入比赛实现；虚拟别名规则仍用于解释图内存复用中“生命周期外访问指针静默踩数据”的一致性语义。

---

## 本章速查（对比赛最有用的 API 索引）

| 目标 | 关键 API / 机制 |
|---|---|
| 消除 decode 每步 kernel 启动开销（TTFT/吞吐） | `hggcStreamBeginCapture`/`EndCapture`、`hggcGraphInstantiate`、`hggcGraphLaunch` |
| 变参数不重建图 | `hggcGraphExecUpdate`、单节点 `hggcGraphExec*SetParams`、`hggcGraphNodeSetEnabled`（超集图） |
| 设备侧分支/循环 | 条件节点 `hggcGraphCondTypeIf/While/Switch`、`hggcGraphSetConditional` |
| 图内临时显存 | 图内存节点 `hggcGraphNodeTypeMemAlloc/MemFree`、`hggcGraphUpload`、`hggcDeviceGraphMemTrim` |
| 无同步显存分配 | `hggcMallocAsync`/`hggcFreeAsync`、池 `hggcMemPoolAttrReleaseThreshold=UINT64_MAX`、`hggcMemPoolTrimTo` |
| 模块加载开销不计入 TTFT | `HGGC_MODULE_LOADING` 环境变量、`hgModuleGetLoadingMode`、`hgModuleGetFunction()`/`hggcFuncGetAttributes()` 预加载 + 预热 |
| kernel 内 warp 归约/扫描 | cooperative_groups：`tiled_partition<32>`、`__shfl_down_sync`、`__shfl_up_sync`、`reduce`/`scan` |
| GEMM 数据预取流水 | `ppu.cp.async`（LDGSTS，4/8/16B 对齐，128B 最佳）、`hggc::memcpy_async`、`hggc::pipeline`（`producer_acquire/commit`、`consumer_wait/release`）、`hggc::barrier`（`arrive/wait/arrive_and_drop`）、AIU 批量张量拷贝（swizzle） |
| KV-cache 分页管理 | VMM：`hgMemAddressReserve`/`hgMemCreate`/`hgMemMap`/`hgMemSetAccess`/`hgMemUnmap`/`hgMemRelease`/`hgMemAddressFree`，`hgMemGetAllocationGranularity` |
| 多进程/多卡共享 | 内存池 IPC（`hggcMemPoolExportToShareableHandle`/`hggcMemPoolExportPointer`）、VMM fabric 句柄（`HG_MEM_HANDLE_TYPE_FABRIC` + IMEX 通道） |
