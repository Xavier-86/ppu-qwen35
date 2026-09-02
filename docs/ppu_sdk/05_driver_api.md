# T-Head SAIL HGGC Driver API <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [1. 概念与约束 {#concepts}](#1-概念与约束-concepts)
  - [1.1. 驱动 API 与运行时 API 的区别 {#driver-vs-runtime}](#11-驱动-api-与运行时-api-的区别-driver-vs-runtime)
  - [1.2. API 同步行为 {#api-sync}](#12-api-同步行为-api-sync)
  - [1.3. 流同步行为 {#stream-sync}](#13-流同步行为-stream-sync)
  - [1.4. 图对象线程安全 {#graph-thread-safety}](#14-图对象线程安全-graph-thread-safety)
  - [1.5. 版本混用规则 {#version-mixing}](#15-版本混用规则-version-mixing)
- [2. 基础与初始化 {#basics}](#2-基础与初始化-basics)
  - [2.1. HGGC 驱动程序使用的数据类型 {#driver-data-types}](#21-hggc-驱动程序使用的数据类型-driver-data-types)
  - [2.2. 全局控制 {#global-control}](#22-全局控制-global-control)
  - [2.3. 实用工具 {#utilities}](#23-实用工具-utilities)
- [3. 设备与上下文 {#device-ctx}](#3-设备与上下文-device-ctx)
  - [3.1. 设备管理 {#device-mgmt}](#31-设备管理-device-mgmt)
  - [3.2. 上下文管理 {#ctx-mgmt}](#32-上下文管理-ctx-mgmt)
  - [3.3. 对等上下文内存访问 {#p2p}](#33-对等上下文内存访问-p2p)
- [4. 模块与代码加载 {#module}](#4-模块与代码加载-module)
  - [4.1. 模块管理 {#module-mgmt}](#41-模块管理-module-mgmt)
- [5. 内存管理 {#memory}](#5-内存管理-memory)
  - [5.1. 内存管理 {#mem-mgmt}](#51-内存管理-mem-mgmt)
  - [5.2. 内存复制 {#memcpy}](#52-内存复制-memcpy)
  - [5.3. 内存填充 {#memset}](#53-内存填充-memset)
  - [5.4. 虚拟内存管理 {#vmm}](#54-虚拟内存管理-vmm)
  - [5.5. 内存池管理 {#mempool}](#55-内存池管理-mempool)
- [6. 流与事件 {#streams}](#6-流与事件-streams)
  - [6.1. 资源管理 {#stream-event}](#61-资源管理-stream-event)
  - [6.2. 流内存操作 {#stream-memop}](#62-流内存操作-stream-memop)
- [7. 执行与调度 {#exec}](#7-执行与调度-exec)
  - [7.1. 执行控制 {#exec-control}](#71-执行控制-exec-control)
  - [7.2. 图管理 {#graph-mgmt}](#72-图管理-graph-mgmt)
- [8. 图像资源 {#image}](#8-图像资源-image)
  - [8.1. 图像资源管理 {#texture}](#81-图像资源管理-texture)
- [9. 参考 {#reference}](#9-参考-reference)
  - [9.1. 数据结构 {#data-structures-index}](#91-数据结构-data-structures-index)
  - [9.2. 数据字段 {#data-fields-index}](#92-数据字段-data-fields-index)


HGGC Driver API（函数前缀 `hg`）是 T-Head SAIL SDK 暴露的低级驱动接口层：相比 Runtime API 的"约定优于配置"，它以显式句柄管理上下文、模块、内存、流/事件与核函数启动，覆盖与 Runtime API 相同的硬件能力，二者可在同一进程中混用。虚拟内存管理（VMM）、模块预加载/热替换、流有序内存池、HGGC Graph 调度等高级优化都建立在这一层之上。对应的 Runtime API 参考见 [04_runtime_api.md](04_runtime_api.md)。

文中所有函数返回值均为 `HGresult`；错误码枚举见 [HGresult](#hgresult)，公共数据类型（枚举/结构体/句柄/宏）汇总于 [HGGC 驱动程序使用的数据类型](#driver-data-types) 一节。

---

## 1. 概念与约束 {#concepts}

本节阐述 HGGC Driver API 的核心概念与使用约束，建议在使用具体 API 前先行阅读。

---

### 1.1. 驱动 API 与运行时 API 的区别 {#driver-vs-runtime}

HGGC 向主机端暴露两层接口：**Driver API** 与 **Runtime API**。它们覆盖相同的硬件能力，可在同一进程中混用，但设计哲学不同——Driver API 强调"显式可控"，Runtime API 强调"约定优于配置"。

#### 1. 核心差异 {#核心差异}

| 维度 | Driver API | Runtime API |
|---|---|---|
| 上下文 | 显式创建 / 销毁 / 压栈（`hgCtxCreate`、`hgCtxSetCurrent`） | 隐式绑定主上下文 |
| 模块管理 | 按需 `hgModuleLoad` / `hgModuleUnload`，支持热替换 | 启动时自动加载全部 device code，运行期常驻 |
| 核函数启动 | `hgLaunchKernel` 逐项填充执行配置与参数缓冲区 | `<<<>>>` 语言级语法糖 |
| 语言无关性 | 仅依赖 hgbin 二进制，可被任意语言 FFI 调用 | 紧耦合编译器前端（hgcc） |

**一句话**：Driver API 用更冗长的代码换取对上下文、模块、生命周期的完全掌控。

#### 2. 上下文协作机制 {#上下文协作机制}

当 Runtime API 需要使用上下文时：

1. 若当前线程已通过 Driver API `hgCtxSetCurrent` 设置了上下文 → Runtime API 直接复用；
2. 否则 → Runtime API 使用主上下文（每个 (进程， 设备) 组合只有一个，引用计数管理）。

这意味着通过 Driver API 预建上下文后，Runtime API 及基于它的库（如 hgBLAS、hgFFT）会自动工作在同一上下文之上，无需额外绑定。

##### 2.1. 典型陷阱：同进程多组件共享主上下文 {#典型陷阱：同进程多组件共享主上下文}

多个独立模块（插件/SDK）默认共享主上下文。若任一方调用 `hggcDeviceReset()` 销毁主上下文，其他模块后续调用将失败。

**推荐模式**：宿主进程用 Driver API 显式建立上下文并 push 为当前上下文，各组件通过 Runtime API 协同工作于该上下文，不再依赖主上下文的隐式共享。

#### 3. 何时选择 Driver API {#何时选择-Driver-API}

| 场景 | 理由 |
|---|---|
| JIT / 异构调度器等底层运行时 | 需要按需加载/卸载 hgbin |
| 多语言绑定（Python、Rust FFI） | 语言无关，无需 hgcc 编译器 |
| 多组件共存，需隔离上下文 | 可为每组件创建独立上下文 |
| 热更新 kernel（开发工具链） | `hgModuleUnload` + 重新加载 |

如果应用场景不涉及以上需求，优先使用 Runtime API 以获得更简洁的代码。

---

### 1.2. API 同步行为 {#api-sync}

HGGC 的数据传输和核函数启动 API 在主机端具有不同的同步语义。理解这些语义是正确编排计算与传输重叠的基础。

> 注意：任何 HGGC API 调用都可能因内部资源争用而临时阻塞。此行为未被约束，不应依赖其发生或不发生。

#### 1. Memcpy 同步规则 {#Memcpy-同步规则}

带“Async”后缀的 memcpy 函数与不带后缀的版本并非简单的“异步 vs 同步”对立——实际行为取决于源/目标内存类型。下表汇总关键场景：

| 方向 | 同步版本的主机端行为 | Async 版本的主机端行为 |
|---|---|---|
| 分页主机 → 设备 | 流同步 + 复制到 staging 缓冲后返回（DMA 此时可能未完成） | 可能与流同步（如需暂存到 pinned 内存） |
| 固定(pinned)主机 → 设备 | 主机同步（复制完成后返回） | 完全异步 |
| 设备 → 主机（任意类型） | 主机同步（复制完成后返回） | 可能与流同步 |
| 设备 → 设备 | 不同步主机 | 完全异步 |
| 主机 → 主机 | 主机完全同步 | 主机完全同步 |

**设计要点**：若追求传输与计算的完全重叠，应使用 pinned 内存 + Async API + 非默认流。

#### 2. Memset {#Memset}

`hgMemsetD*` 系列函数对主机是异步的（目标为设备内存时）。当目标为 pinned 主机内存时，同步版本会阻塞直到完成。Async 变体始终对主机异步。

#### 3. 核函数启动 {#核函数启动}

`hgLaunchKernel` 及其变体对主机始终是异步的——函数在将启动命令排入流后立即返回，不等待核函数执行完成。可通过 `hgStreamSynchronize` 或事件机制等待执行结束。

---

### 1.3. 流同步行为 {#stream-sync}
<a id="ptds"></a>
<a id="legacy-default-stream"></a>

HGGC 的默认流存在两套语义模式：传统默认流（legacy）与每线程默认流（per-thread）。模式选择在编译期确定，影响并发行为和性能上限。

#### 1. 默认流 {#默认流}

向 Driver API 传入流参数 `0` 时，或调用隐式操作流的 API 时，实际生效的就是"默认流"。默认流的同步行为取决于编译单元的模式设置。

可通过以下方式控制：

- 编译选项 `--default-stream`（作用于单个编译单元）
- 在包含任何 HGGC 头文件之前定义宏 `HGGC_API_PER_THREAD_DEFAULT_STREAM`

两种模式可在同一进程内共存（不同编译单元使用不同模式）。

#### 2. 传统默认流 {#legacy-default-stream}

传统默认流是一个**隐式全局同步点**。每当向传统默认流提交操作时：

1. 传统流先等待当前上下文中所有“阻塞流”完成已排操作；
2. 将新操作排入传统流；
3. 所有阻塞流随后等待传统流完成。

示例：

```c
hgLaunchKernel(k_1, ..., s, ...);   // 排入流 s
hgLaunchKernel(k_2, ..., 0, ...);   // 排入传统默认流
hgLaunchKernel(k_3, ..., s, ...);   // 排入流 s
```

执行顺序约束：`k_1 → k_2 → k_3`。传统流效果等价于全局栅栅。

**非阻塞流**：通过 `HG_STREAM_NON_BLOCKING` 标志创建的流不参与上述同步。

**显式句柄**：`HG_STREAM_LEGACY`。

#### 3. 每线程默认流 {#ptds}

每线程默认流是 **(thread, HGcontext) 二元组局部**的隐式流，行为与显式创建的普通流一致：

- 不与其他流自动同步（无“全局栅栅”语义）；
- **不是** `HG_STREAM_NON_BLOCKING` 流；若同进程中同时存在 legacy 编译单元，per-thread 默认流仍会与传统流互相同步；
- 显式句柄：`HG_STREAM_PER_THREAD`。

#### 4. 选择建议 {#选择建议}

| 场景 | 建议 |
|---|---|
| 历史代码迁移、需保留全局栅栅语义 | Legacy |
| 多线程并发、追求最大设备占用 | Per-thread |
| 同进程既有 legacy 又有 per-thread 库 | 按编译单元分别配置，二者自动正确共存 |

---

### 1.4. 图对象线程安全 {#graph-thread-safety}

#### 1. 基本规则 {#基本规则}

Graph 对象（`HGgraph`）内部不做同步保护。多线程不得并发访问同一 `HGgraph` 实例，无论是读还是写。

这包括看似只读的操作：

- `hgGraphClone` —— 克隆过程中会遍历源图的内部状态；
- `hgGraphInstantiate` —— 实例化会读取并缓存图拓扑。

**结论**：任意两个以同一 `HGgraph` 为参数的 API 调用，必须在外部做序列化（mutex / 事件等）。

#### 2. GraphExec 与提交 {#GraphExec-与提交}

实例化后的 `HGgraphExec` 同样不是线程安全的。对同一 `HGgraphExec` 的多次提交或更新操作必须串行化；但在不同流上提交不同 `HGgraphExec` 实例是安全的。

---

### 1.5. 版本混用规则 {#version-mixing}

在同一可执行文件中混合不同版本的 HGGC 库或 API 时，需遵守以下三条规则以避免未定义行为。

#### 1. Runtime 主版本绑定 {#Runtime-主版本绑定}

HGGC Runtime 的 ABI 以主版本号为边界。透明句柄和结构体（如 `hggcDeviceProp`）的内存布局与该主版本绑定。

若函数 A、函数 B 分别用不同主版本工具链编译并链接到同一可执行文件，在它们之间传递 HGGC 定义的类型是**不安全**的。

#### 2. Driver API 逐函数 ABI {#Driver-API-逐函数-ABI}

Driver API 为每个函数独立维护 ABI 版本，以 `_v*` 后缀标识。结构体与对应 API 版本一一匹配，不得跨版本传递。

反例：

```c
// 错误：使用 _v2 的函数却传入 _v1 的结构体
HGGC_MEMCPY2D_v1 params_old;
hgMemcpy2D_v2(&params_old);  // ✗ ABI 不匹配

// 正确：版本匹配
HGGC_MEMCPY2D_v2 params;
hgMemcpy2D_v2(&params);      // ✓
```

#### 3. 资源生命周期一致性 {#资源生命周期一致性}

在同一资源的生命周期内，不应混用不同 ABI 版本的分配/释放接口。资源包括：IPC 句柄、内存、流、上下文、事件等。

反例：

```c
HGdeviceptr p;
hgMemAlloc_v2(&p, size);
hgMemFree(p);       // ✗ 与 _v2 分配不匹配
hgMemFree_v2(p);    // ✓
```

---

比赛关联：弄清各 API 的同步语义（memcpy 何时真正异步）与 legacy/per-thread 默认流差异，是用 pinned 内存 + Async API + 非默认流实现 H2D 传输与计算重叠的前提，直接影响 TTFT 与吞吐上限。

---

## 2. 基础与初始化 {#basics}

本节涵盖驱动程序的基础设施：数据类型定义、驱动初始化接口以及通用辅助工具。

---

### 2.1. HGGC 驱动程序使用的数据类型 {#driver-data-types}
<a id="hggc_external_semaphore_signal_skip_hgscibuf_memsync"></a>
<a id="hggc_cooperative_launch_multi_device_no_pre_launch_sync"></a>
<a id="hggc_cooperative_launch_multi_device_no_post_launch_sync"></a>

本模块定义 HGGC Driver API 使用的**全部公共数据类型**：枚举、结构体 typedef、不透明句柄与宏常量。其他模块的 API 签名均依赖此处的类型定义。

#### 1. 数据结构 (Classes) {#数据结构-(Classes)}

struct HGGC_ARRAY3D_DESCRIPTOR_v2

struct HGGC_ARRAY_DESCRIPTOR_v2

struct HGGC_ARRAY_MEMORY_REQUIREMENTS_v1

struct HGGC_ARRAY_SPARSE_PROPERTIES_v1

struct HGGC_BATCH_MEM_OP_NODE_PARAMS_v1

struct HGGC_BATCH_MEM_OP_NODE_PARAMS_v2

struct HGGC_CHILD_GRAPH_NODE_PARAMS

struct HGGC_CONDITIONAL_NODE_PARAMS

struct HGGC_EVENT_RECORD_NODE_PARAMS

struct HGGC_EVENT_WAIT_NODE_PARAMS

struct HGGC_EXTERNAL_MEMORY_BUFFER_DESC_v1

struct HGGC_EXTERNAL_MEMORY_HANDLE_DESC_v1

struct HGGC_EXTERNAL_MEMORY_MIPMAPPED_ARRAY_DESC_v1

struct HGGC_EXTERNAL_SEMAPHORE_HANDLE_DESC_v1

struct HGGC_EXTERNAL_SEMAPHORE_SIGNAL_PARAMS_v1

struct HGGC_EXTERNAL_SEMAPHORE_WAIT_PARAMS_v1

struct HGGC_EXT_SEM_SIGNAL_NODE_PARAMS_v1

struct HGGC_EXT_SEM_SIGNAL_NODE_PARAMS_v2

struct HGGC_EXT_SEM_WAIT_NODE_PARAMS_v1

struct HGGC_EXT_SEM_WAIT_NODE_PARAMS_v2

struct HGGC_GRAPH_INSTANTIATE_PARAMS

struct HGGC_HOST_NODE_PARAMS_v1

struct HGGC_HOST_NODE_PARAMS_v2

struct HGGC_KERNEL_NODE_PARAMS_v1

struct HGGC_KERNEL_NODE_PARAMS_v2

struct HGGC_KERNEL_NODE_PARAMS_v3

struct HGGC_LAUNCH_PARAMS_v1

struct HGGC_MEMCPY2D_v2

struct HGGC_MEMCPY3D_PEER_v1

struct HGGC_MEMCPY3D_v2

struct HGGC_MEMCPY_NODE_PARAMS

struct HGGC_MEMSET_NODE_PARAMS_v1

struct HGGC_MEMSET_NODE_PARAMS_v2

struct HGGC_MEM_ALLOC_NODE_PARAMS_v1

struct HGGC_MEM_ALLOC_NODE_PARAMS_v2

struct HGGC_MEM_FREE_NODE_PARAMS

struct HGGC_POINTER_ATTRIBUTE_P2P_TOKENS_v1

struct HGGC_RESOURCE_DESC_v1

struct HGGC_RESOURCE_VIEW_DESC_v1

struct HGGC_TEXTURE_DESC_v1

struct HGaccessPolicyWindow_v1

struct HGarrayMapInfo_v1

struct HGasyncNotificationInfo

struct HGcheckpointCheckpointArgs

struct HGcheckpointLockArgs

struct HGcheckpointRestoreArgs

struct HGcheckpointUnlockArgs

struct HGctxCigParam

struct HGctxCreateParams

struct HGdevprop_v1

struct HGeglFrame_v1

struct HGexecAffinityParam_v1

struct HGexecAffinitySmCount_v1

struct HGextent3D_v1

struct HGgraphEdgeData

struct HGgraphExecUpdateResultInfo_v1

struct HGgraphNodeParams

struct HGipcEventHandle_v1

struct HGipcMemHandle_v1

struct HGlaunchAttribute

union HGlaunchAttributeValue

struct HGlaunchConfig

struct HGlaunchMemSyncDomainMap

struct HGmemAccessDesc_v1

struct HGmemAllocationProp_v1

struct HGmemFabricHandle_v1

struct HGmemLocation_v1

struct HGmemPoolProps_v1

struct HGmemPoolPtrExportData_v1

struct HGmemcpy3DOperand_v1

struct HGmemcpyAttributes_v1

struct HGmulticastObjectProp_v1

struct HGoffset3D_v1

union HGstreamBatchMemOpParams_v1

struct HGstreamCigCaptureParams

struct HGstreamCigParam

struct HGtensorMap

---

#### 2. 宏定义 (Defines) {#宏定义-(Defines)}

<a id="hggc_array3d_2darray"></a>

\#define [HGGC_ARRAY3D_2DARRAY](#hggc_array3d_2darray) 0x01

<a id="hggc_array3d_color_attachment"></a>

\#define [HGGC_ARRAY3D_COLOR_ATTACHMENT](#hggc_array3d_color_attachment) 0x20

<a id="hggc_array3d_cubemap"></a>

\#define [HGGC_ARRAY3D_CUBEMAP](#hggc_array3d_cubemap) 0x04

<a id="hggc_array3d_deferred_mapping"></a>

\#define [HGGC_ARRAY3D_DEFERRED_MAPPING](#hggc_array3d_deferred_mapping) 0x80

<a id="hggc_array3d_depth_texture"></a>

\#define [HGGC_ARRAY3D_DEPTH_TEXTURE](#hggc_array3d_depth_texture) 0x10

<a id="hggc_array3d_layered"></a>

\#define [HGGC_ARRAY3D_LAYERED](#hggc_array3d_layered) 0x01

<a id="hggc_array3d_sparse"></a>

\#define [HGGC_ARRAY3D_SPARSE](#hggc_array3d_sparse) 0x40

<a id="hggc_array3d_surface_ldst"></a>

\#define [HGGC_ARRAY3D_SURFACE_LDST](#hggc_array3d_surface_ldst) 0x02

<a id="hggc_array3d_texture_gather"></a>

\#define [HGGC_ARRAY3D_TEXTURE_GATHER](#hggc_array3d_texture_gather) 0x08

<a id="hggc_array3d_video_encode_decode"></a>

\#define [HGGC_ARRAY3D_VIDEO_ENCODE_DECODE](#hggc_array3d_video_encode_decode) 0x100

<a id="hggc_cooperative_launch_multi_device_no_post_launc"></a>

\#define [HGGC_COOPERATIVE_LAUNCH_MULTI_DEVICE_NO_POST_LAUNCH_SYNC](#hggc_cooperative_launch_multi_device_no_post_launch_sync) 0x02

<a id="hggc_cooperative_launch_multi_device_no_pre_launch"></a>

\#define [HGGC_COOPERATIVE_LAUNCH_MULTI_DEVICE_NO_PRE_LAUNCH_SYNC](#hggc_cooperative_launch_multi_device_no_pre_launch_sync) 0x01

<a id="hggc_egl_infinite_timeout"></a>

\#define [HGGC_EGL_INFINITE_TIMEOUT](#hggc_egl_infinite_timeout) 0xFFFFFFFF

<a id="hggc_external_memory_dedicated"></a>

\#define [HGGC_EXTERNAL_MEMORY_DEDICATED](#hggc_external_memory_dedicated) 0x1

<a id="hggc_external_semaphore_signal_skip_hgscibuf_memsy"></a>

\#define [HGGC_EXTERNAL_SEMAPHORE_SIGNAL_SKIP_HGSCIBUF_MEMSYNC](#hggc_external_semaphore_signal_skip_hgscibuf_memsync) 0x01

<a id="hggc_external_semaphore_wait_skip_hgscibuf_memsync"></a>

\#define [HGGC_EXTERNAL_SEMAPHORE_WAIT_SKIP_HGSCIBUF_MEMSYNC](#hggc_external_semaphore_wait_skip_hgscibuf_memsync) 0x02

<a id="hggc_hgscisync_attr_signal"></a>

\#define [HGGC_HGSCISYNC_ATTR_SIGNAL](#hggc_hgscisync_attr_signal) 0x1

<a id="hggc_hgscisync_attr_wait"></a>

\#define [HGGC_HGSCISYNC_ATTR_WAIT](#hggc_hgscisync_attr_wait) 0x2

<a id="hggc_version"></a>

\#define [HGGC_VERSION](#hggc_version) 13020

<a id="hg_array_sparse_properties_single_miptail"></a>

\#define [HG_ARRAY_SPARSE_PROPERTIES_SINGLE_MIPTAIL](#hg_array_sparse_properties_single_miptail) 0x1

<a id="hg_device_cpu"></a>

\#define [HG_DEVICE_CPU](#hg_device_cpu) ((HGdevice)-1)

<a id="hg_device_invalid"></a>

\#define [HG_DEVICE_INVALID](#hg_device_invalid) ((HGdevice)-2)

<a id="hg_graph_cond_assign_default"></a>

\#define [HG_GRAPH_COND_ASSIGN_DEFAULT](#hg_graph_cond_assign_default) 0x1

<a id="hg_graph_kernel_node_port_default"></a>

\#define [HG_GRAPH_KERNEL_NODE_PORT_DEFAULT](#hg_graph_kernel_node_port_default) 0

<a id="hg_graph_kernel_node_port_launch_order"></a>

\#define [HG_GRAPH_KERNEL_NODE_PORT_LAUNCH_ORDER](#hg_graph_kernel_node_port_launch_order) 2

<a id="hg_graph_kernel_node_port_programmatic"></a>

\#define [HG_GRAPH_KERNEL_NODE_PORT_PROGRAMMATIC](#hg_graph_kernel_node_port_programmatic) 1

<a id="hg_ipc_handle_size"></a>

\#define [HG_IPC_HANDLE_SIZE](#hg_ipc_handle_size) 64

<a id="hg_launch_kernel_required_block_dim"></a>

\#define [HG_LAUNCH_KERNEL_REQUIRED_BLOCK_DIM](#hg_launch_kernel_required_block_dim) 1

<a id="hg_launch_param_buffer_pointer"></a>

\#define [HG_LAUNCH_PARAM_BUFFER_POINTER](#hg_launch_param_buffer_pointer)

<a id="hg_launch_param_buffer_pointer_as_int"></a>

\#define [HG_LAUNCH_PARAM_BUFFER_POINTER_AS_INT](#hg_launch_param_buffer_pointer_as_int) 0x01

<a id="hg_launch_param_buffer_size"></a>

\#define [HG_LAUNCH_PARAM_BUFFER_SIZE](#hg_launch_param_buffer_size)

<a id="hg_launch_param_buffer_size_as_int"></a>

\#define [HG_LAUNCH_PARAM_BUFFER_SIZE_AS_INT](#hg_launch_param_buffer_size_as_int) 0x02

<a id="hg_launch_param_end"></a>

\#define [HG_LAUNCH_PARAM_END](#hg_launch_param_end)

<a id="hg_launch_param_end_as_int"></a>

\#define [HG_LAUNCH_PARAM_END_AS_INT](#hg_launch_param_end_as_int) 0x00

<a id="hg_memhostalloc_devicemap"></a>

\#define [HG_MEMHOSTALLOC_DEVICEMAP](#hg_memhostalloc_devicemap) 0x02

<a id="hg_memhostalloc_portable"></a>

\#define [HG_MEMHOSTALLOC_PORTABLE](#hg_memhostalloc_portable) 0x01

<a id="hg_memhostalloc_writecombined"></a>

\#define [HG_MEMHOSTALLOC_WRITECOMBINED](#hg_memhostalloc_writecombined) 0x04

<a id="hg_memhostregister_devicemap"></a>

\#define [HG_MEMHOSTREGISTER_DEVICEMAP](#hg_memhostregister_devicemap) 0x02

<a id="hg_memhostregister_iomemory"></a>

\#define [HG_MEMHOSTREGISTER_IOMEMORY](#hg_memhostregister_iomemory) 0x04

<a id="hg_memhostregister_portable"></a>

\#define [HG_MEMHOSTREGISTER_PORTABLE](#hg_memhostregister_portable) 0x01

<a id="hg_memhostregister_read_only"></a>

\#define [HG_MEMHOSTREGISTER_READ_ONLY](#hg_memhostregister_read_only) 0x08

<a id="hg_mem_create_usage_hw_decompress"></a>

\#define [HG_MEM_CREATE_USAGE_HW_DECOMPRESS](#hg_mem_create_usage_hw_decompress) 0x2

<a id="hg_mem_create_usage_tile_pool"></a>

\#define [HG_MEM_CREATE_USAGE_TILE_POOL](#hg_mem_create_usage_tile_pool) 0x1

<a id="hg_mem_pool_create_usage_hw_decompress"></a>

\#define [HG_MEM_POOL_CREATE_USAGE_HW_DECOMPRESS](#hg_mem_pool_create_usage_hw_decompress) 0x2

<a id="hg_param_tr_default"></a>

\#define [HG_PARAM_TR_DEFAULT](#hg_param_tr_default) -1

<a id="hg_stream_legacy"></a>

\#define [HG_STREAM_LEGACY](#hg_stream_legacy) ((HGstream)0x1)

<a id="hg_stream_per_thread"></a>

\#define [HG_STREAM_PER_THREAD](#hg_stream_per_thread) ((HGstream)0x2)

<a id="hg_tensor_map_num_qwords"></a>

\#define [HG_TENSOR_MAP_NUM_QWORDS](#hg_tensor_map_num_qwords) 16

<a id="hg_trsa_override_format"></a>

\#define [HG_TRSA_OVERRIDE_FORMAT](#hg_trsa_override_format) 0x01

<a id="hg_trsf_disable_trilinear_optimization"></a>

\#define [HG_TRSF_DISABLE_TRILINEAR_OPTIMIZATION](#hg_trsf_disable_trilinear_optimization) 0x20

<a id="hg_trsf_normalized_coordinates"></a>

\#define [HG_TRSF_NORMALIZED_COORDINATES](#hg_trsf_normalized_coordinates) 0x02

<a id="hg_trsf_read_as_integer"></a>

\#define [HG_TRSF_READ_AS_INTEGER](#hg_trsf_read_as_integer) 0x01

<a id="hg_trsf_seamless_cubemap"></a>

\#define [HG_TRSF_SEAMLESS_CUBEMAP](#hg_trsf_seamless_cubemap) 0x40

<a id="hg_trsf_srgb"></a>

\#define [HG_TRSF_SRGB](#hg_trsf_srgb) 0x10

<a id="max_planes"></a>

\#define [MAX_PLANES](#max_planes) 3

---

#### 3. 类型定义 (Typedefs) {#类型定义-(Typedefs)}

<a id="hgaccesspolicywindow"></a>

typedef struct HGaccessPolicyWindow_v1 [HGaccessPolicyWindow](#hgaccesspolicywindow)

<a id="hgarray"></a>

typedef HGarray_st * [HGarray](#hgarray)

<a id="hgasynccallback"></a>

typedef void ( *[HGasyncCallback](#hgasynccallback) )( HGasyncNotificationInfo* info, void* userData, HGasyncCallbackHandle callback )

<a id="hgasynccallbackhandle"></a>

typedef HGasyncCallbackEntry_st * [HGasyncCallbackHandle](#hgasynccallbackhandle)

<a id="hgcontext"></a>

typedef HGctx_st * [HGcontext](#hgcontext)

<a id="hgdevice"></a>

typedef [HGdevice_v1](#driver-data-types) [HGdevice](#hgdevice)

typedef int [HGdevice_v1](#driver-data-types)

<a id="hgdeviceptr"></a>

typedef [HGdeviceptr_v2](#driver-data-types) [HGdeviceptr](#hgdeviceptr)

typedef unsigned int [HGdeviceptr_v2](#driver-data-types)

<a id="hgevent"></a>

typedef HGevent_st * [HGevent](#hgevent)

<a id="hgexecaffinityparam"></a>

typedef struct HGexecAffinityParam_v1 [HGexecAffinityParam](#hgexecaffinityparam)

<a id="hgexternalmemory"></a>

typedef HGextMemory_st * [HGexternalMemory](#hgexternalmemory)

<a id="hgexternalsemaphore"></a>

typedef HGextSemaphore_st * [HGexternalSemaphore](#hgexternalsemaphore)

<a id="hgfunction"></a>

typedef HGfunc_st * [HGfunction](#hgfunction)

<a id="hggraph"></a>

typedef HGgraph_st * [HGgraph](#hggraph)

<a id="hggraphconditionalhandle"></a>

typedef hguint64_t [HGgraphConditionalHandle](#hggraphconditionalhandle)

<a id="hggraphdevicenode"></a>

typedef HGgraphDeviceUpdatableNode_st * [HGgraphDeviceNode](#hggraphdevicenode)

<a id="hggraphexec"></a>

typedef HGgraphExec_st * [HGgraphExec](#hggraphexec)

<a id="hggraphnode"></a>

typedef HGgraphNode_st * [HGgraphNode](#hggraphnode)

<a id="hggraphicsresource"></a>

typedef HGgraphicsResource_st * [HGgraphicsResource](#hggraphicsresource)

<a id="hggreenctx"></a>

typedef HGgreenCtx_st * [HGgreenCtx](#hggreenctx)

<a id="hghostfn"></a>

typedef void(HGGC_CB* [HGhostFn](#hghostfn) )( void* userData )

<a id="hgkernel"></a>

typedef HGkern_st * [HGkernel](#hgkernel)

<a id="hglibrary"></a>

typedef HGlib_st * [HGlibrary](#hglibrary)

<a id="hgmemorypool"></a>

typedef HGmemPoolHandle_st * [HGmemoryPool](#hgmemorypool)

<a id="hgmipmappedarray"></a>

typedef HGmipmappedArray_st * [HGmipmappedArray](#hgmipmappedarray)

<a id="hgmodule"></a>

typedef HGmod_st * [HGmodule](#hgmodule)

<a id="hgoccupancyb2dsize"></a>

typedef size_t(HGGC_CB* [HGoccupancyB2DSize](#hgoccupancyb2dsize) )( int blockSize )

<a id="hgstream"></a>

typedef HGstream_st * [HGstream](#hgstream)

<a id="hgstreamcallback"></a>

typedef void(HGGC_CB* [HGstreamCallback](#hgstreamcallback) )( HGstream hStream, HGresult status, void* userData )

<a id="hgsurfobject"></a>

typedef [HGsurfObject_v1](#driver-data-types) [HGsurfObject](#hgsurfobject)

typedef unsigned long long [HGsurfObject_v1](#driver-data-types)

<a id="hgsurfref"></a>

typedef HGsurfref_st * [HGsurfref](#hgsurfref)

<a id="hgtexobject"></a>

typedef [HGtexObject_v1](#driver-data-types) [HGtexObject](#hgtexobject)

typedef unsigned long long [HGtexObject_v1](#driver-data-types)

<a id="hgtexref"></a>

typedef HGtexref_st * [HGtexref](#hgtexref)

<a id="hguserobject"></a>

typedef HGuserObject_st * [HGuserObject](#hguserobject)

---

#### 4. 枚举类型 (Enumerations) {#枚举类型-(Enumerations)}

<a id="hggc_pointer_attribute_access_flags"></a>

enum [HGGC_POINTER_ATTRIBUTE_ACCESS_FLAGS](#hggc_pointer_attribute_access_flags) 

<a id="hggpudirectrdmawritesordering"></a>

enum [HGGPUDirectRDMAWritesOrdering](#hggpudirectrdmawritesordering)
 
<a id="hgaccessproperty"></a>

enum [HGaccessProperty](#hgaccessproperty)
 
<a id="hgaddress_mode"></a>

enum [HGaddress_mode](#hgaddress_mode)
 
<a id="hgarraysparsesubresourcetype"></a>

enum [HGarraySparseSubresourceType](#hgarraysparsesubresourcetype)
 
<a id="hgarray_cubemap_face"></a>

enum [HGarray_cubemap_face](#hgarray_cubemap_face)
 
<a id="hgarray_format"></a>

enum [HGarray_format](#hgarray_format)
 
<a id="hgasyncnotificationtype"></a>

enum [HGasyncNotificationType](#hgasyncnotificationtype)
 
<a id="hgatomicoperation"></a>

enum [HGatomicOperation](#hgatomicoperation)
 
<a id="hgatomicoperationcapability"></a>

enum [HGatomicOperationCapability](#hgatomicoperationcapability)
 
<a id="hgclusterschedulingpolicy"></a>

enum [HGclusterSchedulingPolicy](#hgclusterschedulingpolicy)
 
<a id="hgcomputemode"></a>

enum [HGcomputemode](#hgcomputemode)
 
<a id="hgctx_flags"></a>

enum [HGctx_flags](#hgctx_flags)
 
<a id="hgdevicenumaconfig"></a>

enum [HGdeviceNumaConfig](#hgdevicenumaconfig)
 
<a id="hgdevice_p2pattribute"></a>

enum [HGdevice_P2PAttribute](#hgdevice_p2pattribute)
 
<a id="hgdevice_attribute"></a>

enum [HGdevice_attribute](#hgdevice_attribute)
 
<a id="hgdriverprocaddressqueryresult"></a>

enum [HGdriverProcAddressQueryResult](#hgdriverprocaddressqueryresult)
 
<a id="hgdriverprocaddress_flags"></a>

enum [HGdriverProcAddress_flags](#hgdriverprocaddress_flags)
 
<a id="hgeglcolorformat"></a>

enum [HGeglColorFormat](#hgeglcolorformat)
 
<a id="hgeglframetype"></a>

enum [HGeglFrameType](#hgeglframetype)
 
<a id="hgeglresourcelocationflags"></a>

enum [HGeglResourceLocationFlags](#hgeglresourcelocationflags)
 
<a id="hgevent_flags"></a>

enum [HGevent_flags](#hgevent_flags)
 
<a id="hgevent_record_flags"></a>

enum [HGevent_record_flags](#hgevent_record_flags)
 
<a id="hgevent_sched_flags"></a>

enum [HGevent_sched_flags](#hgevent_sched_flags)
 
<a id="hgevent_wait_flags"></a>

enum [HGevent_wait_flags](#hgevent_wait_flags)
 
<a id="hgexecaffinitytype"></a>

enum [HGexecAffinityType](#hgexecaffinitytype)
 
<a id="hgexternalmemoryhandletype"></a>

enum [HGexternalMemoryHandleType](#hgexternalmemoryhandletype)
 
<a id="hgexternalsemaphorehandletype"></a>

enum [HGexternalSemaphoreHandleType](#hgexternalsemaphorehandletype)
 
<a id="hgfilter_mode"></a>

enum [HGfilter_mode](#hgfilter_mode)
 
<a id="hgflushgpudirectrdmawritesoptions"></a>

enum [HGflushGPUDirectRDMAWritesOptions](#hgflushgpudirectrdmawritesoptions)
 
<a id="hgflushgpudirectrdmawritesscope"></a>

enum [HGflushGPUDirectRDMAWritesScope](#hgflushgpudirectrdmawritesscope)
 
<a id="hgflushgpudirectrdmawritestarget"></a>

enum [HGflushGPUDirectRDMAWritesTarget](#hgflushgpudirectrdmawritestarget)
 
<a id="hgfunc_cache"></a>

enum [HGfunc_cache](#hgfunc_cache)
 
<a id="hgfunction_attribute"></a>

enum [HGfunction_attribute](#hgfunction_attribute)
 
<a id="hggraphchildgraphnodeownership"></a>

enum [HGgraphChildGraphNodeOwnership](#hggraphchildgraphnodeownership)
 
<a id="hggraphconditionalnodetype"></a>

enum [HGgraphConditionalNodeType](#hggraphconditionalnodetype)
 
<a id="hggraphdebugdot_flags"></a>

enum [HGgraphDebugDot_flags](#hggraphdebugdot_flags)
 
<a id="hggraphdependencytype"></a>

enum [HGgraphDependencyType](#hggraphdependencytype)
 
<a id="hggraphexecupdateresult"></a>

enum [HGgraphExecUpdateResult](#hggraphexecupdateresult)
 
<a id="hggraphinstantiateresult"></a>

enum [HGgraphInstantiateResult](#hggraphinstantiateresult)
 
<a id="hggraphinstantiate_flags"></a>

enum [HGgraphInstantiate_flags](#hggraphinstantiate_flags)
 
<a id="hggraphnodetype"></a>

enum [HGgraphNodeType](#hggraphnodetype)
 
<a id="hggraphicsmapresourceflags"></a>

enum [HGgraphicsMapResourceFlags](#hggraphicsmapresourceflags)
 
<a id="hggraphicsregisterflags"></a>

enum [HGgraphicsRegisterFlags](#hggraphicsregisterflags)
 
<a id="hgipcmem_flags"></a>

enum [HGipcMem_flags](#hgipcmem_flags)
 
<a id="hgjitinputtype"></a>

enum [HGjitInputType](#hgjitinputtype)
 
<a id="hgjit_cachemode"></a>

enum [HGjit_cacheMode](#hgjit_cachemode)
 
<a id="hgjit_fallback"></a>

enum [HGjit_fallback](#hgjit_fallback)
 
<a id="hgjit_option"></a>

enum [HGjit_option](#hgjit_option)
 
<a id="hgjit_target"></a>

enum [HGjit_target](#hgjit_target)
 
<a id="hglaunchattributeid"></a>

enum [HGlaunchAttributeID](#hglaunchattributeid)
 
<a id="hglaunchattributeportableclustermode"></a>

enum [HGlaunchAttributePortableClusterMode](#hglaunchattributeportableclustermode)
 
<a id="hglaunchmemsyncdomain"></a>

enum [HGlaunchMemSyncDomain](#hglaunchmemsyncdomain)
 
<a id="hglibraryoption"></a>

enum [HGlibraryOption](#hglibraryoption)
 
<a id="hglimit"></a>

enum [HGlimit](#hglimit)
 
<a id="hgmemaccess_flags"></a>

enum [HGmemAccess_flags](#hgmemaccess_flags)
 
<a id="hgmemallocationcomptype"></a>

enum [HGmemAllocationCompType](#hgmemallocationcomptype)
 
<a id="hgmemallocationgranularity_flags"></a>

enum [HGmemAllocationGranularity_flags](#hgmemallocationgranularity_flags)
 
<a id="hgmemallocationhandletype"></a>

enum [HGmemAllocationHandleType](#hgmemallocationhandletype)
 
<a id="hgmemallocationtype"></a>

enum [HGmemAllocationType](#hgmemallocationtype)
 
<a id="hgmemattach_flags"></a>

enum [HGmemAttach_flags](#hgmemattach_flags)
 
<a id="hgmemhandletype"></a>

enum [HGmemHandleType](#hgmemhandletype)
 
<a id="hgmemlocationtype"></a>

enum [HGmemLocationType](#hgmemlocationtype)
 
<a id="hgmemoperationtype"></a>

enum [HGmemOperationType](#hgmemoperationtype)
 
<a id="hgmempool_attribute"></a>

enum [HGmemPool_attribute](#hgmempool_attribute)
 
<a id="hgmemrangeflags"></a>

enum [HGmemRangeFlags](#hgmemrangeflags)
 
<a id="hgmemrangehandletype"></a>

enum [HGmemRangeHandleType](#hgmemrangehandletype)
 
<a id="hgmem_advise"></a>

enum [HGmem_advise](#hgmem_advise)
 
<a id="hgmemcpy3doperandtype"></a>

enum [HGmemcpy3DOperandType](#hgmemcpy3doperandtype)
 
<a id="hgmemcpyflags"></a>

enum [HGmemcpyFlags](#hgmemcpyflags)
 
<a id="hgmemcpysrcaccessorder"></a>

enum [HGmemcpySrcAccessOrder](#hgmemcpysrcaccessorder)
 
<a id="hgmemorytype"></a>

enum [HGmemorytype](#hgmemorytype)
 
<a id="hgmulticastgranularity_flags"></a>

enum [HGmulticastGranularity_flags](#hgmulticastgranularity_flags)
 
<a id="hgoccupancy_flags"></a>

enum [HGoccupancy_flags](#hgoccupancy_flags)
 
<a id="hgpointer_attribute"></a>

enum [HGpointer_attribute](#hgpointer_attribute)
 
<a id="hgprocessstate"></a>

enum [HGprocessState](#hgprocessstate)
 
<a id="hgresourceviewformat"></a>

enum [HGresourceViewFormat](#hgresourceviewformat)
 
<a id="hgresourcetype"></a>

enum [HGresourcetype](#hgresourcetype)
 
<a id="hgresult"></a>

enum [HGresult](#hgresult)
 
<a id="hgsharedmemorymode"></a>

enum [HGsharedMemoryMode](#hgsharedmemorymode)
 
<a id="hgshared_carveout"></a>

enum [HGshared_carveout](#hgshared_carveout)
 
<a id="hgsharedconfig"></a>

enum [HGsharedconfig](#hgsharedconfig)
 
<a id="hgstreamatomicreductiondatatype"></a>

enum [HGstreamAtomicReductionDataType](#hgstreamatomicreductiondatatype)
 
<a id="hgstreamatomicreductionoptype"></a>

enum [HGstreamAtomicReductionOpType](#hgstreamatomicreductionoptype)
 
<a id="hgstreambatchmemoptype"></a>

enum [HGstreamBatchMemOpType](#hgstreambatchmemoptype)
 
<a id="hgstreamcapturemode"></a>

enum [HGstreamCaptureMode](#hgstreamcapturemode)
 
<a id="hgstreamcapturestatus"></a>

enum [HGstreamCaptureStatus](#hgstreamcapturestatus)
 
<a id="hgstreammemorybarrier_flags"></a>

enum [HGstreamMemoryBarrier_flags](#hgstreammemorybarrier_flags)
 
<a id="hgstreamupdatecapturedependencies_flags"></a>

enum [HGstreamUpdateCaptureDependencies_flags](#hgstreamupdatecapturedependencies_flags)
 
<a id="hgstreamwaitvalue_flags"></a>

enum [HGstreamWaitValue_flags](#hgstreamwaitvalue_flags)
 
<a id="hgstreamwritevalue_flags"></a>

enum [HGstreamWriteValue_flags](#hgstreamwritevalue_flags)
 
<a id="hgstream_flags"></a>

enum [HGstream_flags](#hgstream_flags)
 
<a id="hgtensormapdatatype"></a>

enum [HGtensorMapDataType](#hgtensormapdatatype)
 
<a id="hgtensormapfloatoobfill"></a>

enum [HGtensorMapFloatOOBfill](#hgtensormapfloatoobfill)
 
<a id="hgtensormapim2colwidemode"></a>

enum [HGtensorMapIm2ColWideMode](#hgtensormapim2colwidemode)
 
<a id="hgtensormapinterleave"></a>

enum [HGtensorMapInterleave](#hgtensormapinterleave)
 
<a id="hgtensormapl2promotion"></a>

enum [HGtensorMapL2promotion](#hgtensormapl2promotion)
 
<a id="hgtensormapswizzle"></a>

enum [HGtensorMapSwizzle](#hgtensormapswizzle)
 
<a id="hguserobjectretain_flags"></a>

enum [HGuserObjectRetain_flags](#hguserobjectretain_flags)
 
<a id="hguserobject_flags"></a>

enum [HGuserObject_flags](#hguserobject_flags)
 
<a id="cl_context_flags"></a>

enum [cl_context_flags](#cl_context_flags)
 
<a id="cl_event_flags"></a>

enum [cl_event_flags](#cl_event_flags)

#### 5. 宏定义 (Defines) - 详细说明 {#宏定义-(Defines)---详细说明}

```c
#define HGGC_ARRAY3D_2DARRAY 0x01
```
已弃用，请使用 HGGC_ARRAY3D_LAYERED

---

```c
#define HGGC_ARRAY3D_COLOR_ATTACHMENT 0x20
```
此标志表示 HGGC 数组可以作为外部图形 API 中的颜色目标绑定

---

```c
#define HGGC_ARRAY3D_CUBEMAP 0x04
```
如果设置，HGGC 数组是六个 2D 数组的集合，代表立方体的面。此 HGGC 数组的宽度必须等于高度，深度必须为六。如果还设置了 [HGGC_ARRAY3D_LAYERED](#driver-data-types) 标志，则 HGGC 数组是立方体贴图的集合，深度必须是六的倍数。

---

```c
#define HGGC_ARRAY3D_DEFERRED_MAPPING 0x80
```
如果设置此标志，表示 HGGC 数组或 HGGC 多重映射数组将允许延迟内存映射

---

```c
#define HGGC_ARRAY3D_DEPTH_TEXTURE 0x10
```
如果设置此标志，表示 HGGC 数组是 DEPTH_TEXTURE。

---

```c
#define HGGC_ARRAY3D_LAYERED 0x01
```
如果设置，HGGC 数组是层的集合，其中每层是 1D 或 2D 数组，HGGC_ARRAY3D_DESCRIPTOR 的 Depth 成员指定层数，而不是 3D 数组的深度。

---

```c
#define HGGC_ARRAY3D_SPARSE 0x40
```
如果设置此标志，表示 HGGC 数组或 HGGC 多重映射数组分别是稀疏 HGGC 数组或 HGGC 多重映射数组

---

```c
#define HGGC_ARRAY3D_SURFACE_LDST 0x02
```
必须设置此标志才能将表面引用绑定到 HGGC 数组

---

```c
#define HGGC_ARRAY3D_TEXTURE_GATHER 0x08
```
必须设置此标志才能在 HGGC 数组上执行纹理收集操作。

---

```c
#define HGGC_ARRAY3D_VIDEO_ENCODE_DECODE 0x100
```
此标志表示 HGGC 数组将用于硬件加速的视频编码/解码操作。

---

```c
#define HGGC_COOPERATIVE_LAUNCH_MULTI_DEVICE_NO_POST_LAUNCH_SYNC 0x02
```
如果设置，作为 `hgLaunchCooperativeKernelMultiDevice` 调用参与流的任何后续推送工作将只等待对应流启动的核函数在该流对应的 PPU 上完成后才开始执行。

---

```c
#define HGGC_COOPERATIVE_LAUNCH_MULTI_DEVICE_NO_PRE_LAUNCH_SYNC 0x01
```
如果设置，作为 `hgLaunchCooperativeKernelMultiDevice` 的一部分启动的每个核函数只等待对应 PPU 流中的先前工作完成后才开始执行。

---

```c
#define HGGC_EGL_INFINITE_TIMEOUT 0xFFFFFFFF
```
此标志表示 hgEGLStreamConsumerAcquireFrame 的超时是无限的。

---

```c
#define HGGC_EXTERNAL_MEMORY_DEDICATED 0x1
```
表示外部内存对象是专用资源

---

```c
#define HGGC_EXTERNAL_SEMAPHORE_SIGNAL_SKIP_HGSCIBUF_MEMSYNC 0x01
```
当 HGGC_EXTERNAL_SEMAPHORE_SIGNAL_PARAMS 的 flags 参数包含此标志时，表示信号外部信号量对象应跳过对所有作为 [HG_EXTERNAL_MEMORY_HANDLE_TYPE_HGSCIBUF](#driver-data-types) 导入的外部内存对象执行适当的内存同步操作，否则默认执行这些操作以确保与其他 HgSciBuf 内存对象导入器的数据一致性。

---

```c
#define HGGC_EXTERNAL_SEMAPHORE_WAIT_SKIP_HGSCIBUF_MEMSYNC 0x02
```
当 HGGC_EXTERNAL_SEMAPHORE_WAIT_PARAMS 的 flags 参数包含此标志时，表示等待外部信号量对象应跳过对所有作为 [HG_EXTERNAL_MEMORY_HANDLE_TYPE_HGSCIBUF](#driver-data-types) 导入的外部内存对象执行适当的内存同步操作，否则默认执行这些操作以确保与其他 HgSciBuf 内存对象导入器的数据一致性。

---

```c
#define HGGC_HGSCISYNC_ATTR_SIGNAL 0x1
```
当 HgSciSyncAttrList 的 flags 字段设置为此值时，表示应用程序需要填充信号方特定的 HgSciSyncAttr。

---

```c
#define HGGC_HGsSCISYNC_ATTR_WAIT 0x2
```
当 HgSciSyncAttrList 的 flags 字段设置为此值时，表示应用程序需要填充等待方特定的 HgSciSyncAttr。

---

```c
#define HGGC_VERSION 13020
```
HGGC API 版本号

---

```c
#define HG_ARRAY_SPARSE_PROPERTIES_SINGLE_MIPTAIL 0x1
```
表示分层稀疏 HGGC 数组或 HGGC 多重映射数组所有层只有一个 mip tail 区域

---

```c
#define HG_DEVICE_CPU ((HGdevice)-1)
```
代表 CPU 的设备

---

```c
#define HG_DEVICE_INVALID ((HGdevice)-2)
```
代表无效设备的设备

---

```c
#define HG_GRAPH_COND_ASSIGN_DEFAULT 0x1
```
条件节点句柄标志 图启动时应用默认值。

---

```c
#define HG_GRAPH_KERNEL_NODE_PORT_DEFAULT 0
```
此端口在核函数执行完成时激活。

---

```c
#define HG_GRAPH_KERNEL_NODE_PORT_LAUNCH_ORDER 2
```
此端口在核函数的所有块开始执行时激活。另见 HG_LAUNCH_ATTRIBUTE_LAUNCH_COMPLETION_EVENT。

---

```c
#define HG_GRAPH_KERNEL_NODE_PORT_PROGRAMMATIC 1
```
此端口在核函数的所有块触发编程启动完成或终止时激活。它必须与边类型 HG_GRAPH_DEPENDENCY_TYPE_PROGRAMMATIC 一起使用。另见 HG_LAUNCH_ATTRIBUTE_PROGRAMMATIC_EVENT。

---

```c
#define HG_IPC_HANDLE_SIZE 64
```
HGGC IPC 句柄大小

---

```c
#define HG_LAUNCH_KERNEL_REQUIRED_BLOCK_DIM 1
```
使用所需的块维度启动。

---

```c
#define HG_LAUNCH_PARAM_BUFFER_POINTER
```
指示 [hgLaunchKernel](#exec-control) 的 extra 参数中的下一个值将是指向缓冲区的指针，该缓冲区包含启动核函数 f 使用的所有核函数参数。此缓冲区需要遵守所有单独参数的对齐/填充要求。如果 extra 数组中未同时指定 [HG_LAUNCH_PARAM_BUFFER_SIZE](#driver-data-types)，则 [HG_LAUNCH_PARAM_BUFFER_POINTER](#driver-data-types) 将无效。

((void*)HG_LAUNCH_PARAM_BUFFER_POINTER_AS_INT)

---

```c
#define HG_LAUNCH_PARAM_BUFFER_POINTER_AS_INT 0x01
```
HG_LAUNCH_PARAM_BUFFER_POINTER 的 C++ 编译时常量

---

```c
#define HG_LAUNCH_PARAM_BUFFER_SIZE
```
指示 [hgLaunchKernel](#exec-control) 的 extra 参数中的下一个值将是指向 size_t 的指针，其中包含由 HG_LAUNCH_PARAM_BUFFER_POINTER 指定的缓冲区大小。如果与 HG_LAUNCH_PARAM_BUFFER_SIZE 关联的值不为零，则需要在 extra 数组中同时指定 HG_LAUNCH_PARAM_BUFFER_POINTER。

值
((void*)HG_LAUNCH_PARAM_BUFFER_SIZE_AS_INT)

---

```c
#define HG_LAUNCH_PARAM_BUFFER_SIZE_AS_INT 0x02
```
HG_LAUNCH_PARAM_BUFFER_SIZE 的 C++ 编译时常量

---

```c
#define HG_LAUNCH_PARAM_END
```
hgLaunchKernel extra 参数的数组结束符

((void*)HG_LAUNCH_PARAM_END_AS_INT)

---

```c
#define HG_LAUNCH_PARAM_END_AS_INT 0x00
```
HG_LAUNCH_PARAM_END 的 C++ 编译时常量

---

```c
#define HG_MEMHOSTALLOC_DEVICEMAP 0x02
```
如果设置，主机内存映射到 HGGC 地址空间，可以对主机指针调用 hgMemHostGetDevicePointer()。hgMemHostAlloc() 的标志

---

```c
#define HG_MEMHOSTALLOC_PORTABLE 0x01
```
如果设置，主机内存在 HGGC 上下文之间可移植。hgMemHostAlloc() 的标志

---

```c
#define HG_MEMHOSTALLOC_WRITECOMBINED 0x04
```
如果设置，主机内存分配为写合并类型 - 写入快，DMA 更快，除了通过 SSE4 流加载指令 (MOVNTDQA) 外读取较慢。hgMemHostAlloc() 的标志

---

```c
#define HG_MEMHOSTREGISTER_DEVICEMAP 0x02
```
如果设置，主机内存映射到 HGGC 地址空间，可以对主机指针调用 hgMemHostGetDevicePointer()。hgMemHostRegister() 的标志

---

```c
#define HG_MEMHOSTREGISTER_IOMEMORY 0x04
```
如果设置，传递的内存指针被视为指向某些内存映射的 I/O 空间，例如属于第三方 PCIe 设备。在 Linux 上，该内存被标记为 PPU 非缓存一致性，且需要物理连续。如果以无特权用户运行可能返回 [HGGC_ERROR_NOT_PERMITTED](#driver-data-types)，在较旧的 Linux 内核版本上返回 [HGGC_ERROR_NOT_SUPPORTED](#driver-data-types)。在所有其他平台上不支持并返回 [HGGC_ERROR_NOT_SUPPORTED](#driver-data-types)。hgMemHostRegister() 的标志

---

```c
#define HG_MEMHOSTREGISTER_PORTABLE 0x01
```
如果设置，主机内存在 HGGC 上下文之间可移植。hgMemHostRegister() 的标志

---

```c
#define HG_MEMHOSTREGISTER_READ_ONLY 0x08
```
如果设置，传递的内存指针被视为指向被设备视为只读的内存。在没有 HG_DEVICE_ATTRIBUTE_PAGEABLE_MEMORY_ACCESS_USES_HOST_PAGE_TABLES 的平台上，必须设置此标志才能将映射到 CPU 的内存注册为只读。可以从设备属性 HG_DEVICE_ATTRIBUTE_READ_ONLY_HOST_REGISTER_SUPPORTED 查询对此标志的支持。在没有此属性集的设备上使用当前上下文调用 hgMemHostRegister 将导致错误 HGGC_ERROR_NOT_SUPPORTED。

---

```c
#define HG_MEM_CREATE_USAGE_HW_DECOMPRESS 0x2
```
如果设置此标志，表示该内存将用作硬件加速解压缩的缓冲区。

---

```c
#define HG_MEM_CREATE_USAGE_TILE_POOL 0x1
```
如果设置此标志，表示该内存将用作瓦片池。

---

```c
#define HG_MEM_POOL_CREATE_USAGE_HW_DECOMPRESS 0x2
```
如果设置此标志，表示该内存将用作硬件加速解压缩的缓冲区。

---

```c
#define HG_PARAM_TR_DEFAULT -1
```
对于加载到模块中的纹理引用，使用纹理引用中的默认 texunit。

---

```c
#define HG_STREAM_LEGACY ((HGstream)0x1)
```
传统流句柄

可作为 HGstream 传递以使用具有传统同步行为的隐式流。

请参阅同步行为的详细信息。

---

```c
#define HG_STREAM_PER_THREAD ((HGstream)0x2)
```
每线程流句柄

可作为 HGstream 传递以使用具有每线程同步行为的隐式流。

请参阅同步行为的详细信息。

---

```c
#define HG_TENSOR_MAP_NUM_QWORDS 16
```
张量图描述符大小

---

```c
#define HG_TRSA_OVERRIDE_FORMAT 0x01
```
覆盖 texref 格式为从数组推断的格式。hgTexRefSetArray() 的标志

---

```c
#define HG_TRSF_DISABLE_TRILINEAR_OPTIMIZATION 0x20
```
禁用任何三线性过滤优化。hgTexRefSetFlags() 和 hgTexObjectCreate() 的标志

---

```c
#define HG_TRSF_NORMALIZED_COORDINATES 0x02
```
使用范围 [0,1) 中的归一化纹理坐标，而不是 [0,dim)。hgTexRefSetFlags() 和 hgTexObjectCreate() 的标志

---

```c
#define HG_TRSF_READ_AS_INTEGER 0x01
```
将纹理作为整数读取，而不是将值提升为范围 [0,1] 的浮点数。hgTexRefSetFlags() 和 hgTexObjectCreate() 的标志

---

```c
#define HG_TRSF_SEAMLESS_CUBEMAP 0x40
```
启用无缝立方体贴图过滤。hgTexObjectCreate() 的标志

---

```c
#define HG_TRSF_SRGB 0x10
```
在纹理读取期间执行 sRGB->线性转换。hgTexRefSetFlags() 和 hgTexObjectCreate() 的标志

---

```c
#define MAX_PLANES 3
```
每帧最大平面数

---

#### 6. 类型定义 (Typedefs) - 详细说明 {#类型定义-(Typedefs)---详细说明}

```c
typedef struct HGaccessPolicyWindow_v1 HGaccessPolicyWindow
```
访问策略窗口

---

```c
typedef HGarray_st * HGarray
```
HGGC 数组

---

```c
typedef void ( *HGasyncCallback )( HGasyncNotificationInfo* info, void* userData, HGasyncCallbackHandle callback )
```
HGGC 异步通知回调

参数
- info: 描述对此通知执行哪些操作的信息。
- userData: 回调注册时提供的用户定义数据指针。
- HGasyncCallbackHandle callback

---

```c
typedef HGasyncCallbackEntry_st * HGasyncCallbackHandle
```
HGGC 异步通知回调句柄

---

```c
typedef HGctx_st * HGcontext
```
常规上下文句柄

---

```c
typedef HGdevice_v1 HGdevice
```
HGGC 设备

---

```c
typedef int HGdevice_v1
```
HGGC 设备

---

```c
typedef HGdeviceptr_v2 HGdeviceptr
```
HGGC 设备指针

---

```c
typedef unsigned int HGdeviceptr_v2
```
HGGC 设备指针。HGdeviceptr 定义为无符号整数类型，其大小与目标平台上的指针大小匹配。

---

```c
typedef HGevent_st * HGevent
```
HGGC 事件

---

```c
typedef struct HGexecAffinityParam_v1 HGexecAffinityParam
```
执行亲和参数

---

```c
typedef HGextMemory_st * HGexternalMemory
```
HGGC 外部内存

---

```c
typedef HGextSemaphore_st * HGexternalSemaphore
```
HGGC 外部信号量

---

```c
typedef HGfunc_st * HGfunction
```
HGGC 函数

---

```c
typedef HGgraph_st * HGgraph
```
HGGC 图

---

```c
typedef hguint64_t HGgraphConditionalHandle
```
HGGC 图条件句柄

---

```c
typedef HGgraphDeviceUpdatableNode_st * HGgraphDeviceNode
```
HGGC 图设备节点句柄

---

```c
typedef HGgraphExec_st * HGgraphExec
```
HGGC 可执行图

---

```c
typedef HGgraphNode_st * HGgraphNode
```
HGGC 图节点

---

```c
typedef HGgraphicsResource_st * HGgraphicsResource
```
HGGC 图形互操作资源

---

```c
typedef HGgreenCtx_st * HGgreenCtx
```
绿色上下文句柄。此句柄只能安全地同时从一个 CPU 线程使用。通过 hgGreenCtxCreate 创建

---

```c
typedef void(HGGC_CB* HGhostFn )( void* userData )
```
HGGC 主机函数

参数
- userData: 传递给函数的参数值

---

```c
typedef HGkern_st * HGkernel
```
HGGC 核函数

---

```c
typedef HGlib_st * HGlibrary
```
HGGC 库

---

```c
typedef HGmemPoolHandle_st * HGmemoryPool
```
HGGC 内存池

---

```c
typedef HGmipmappedArray_st * HGmipmappedArray
```
HGGC 多重映射数组

---

```c
typedef HGmod_st * HGmodule
```
HGGC 模块

---

```c
typedef size_t(HGGC_CB* HGoccupancyB2DSize )( int blockSize )
```
某个核函数的每块动态共享内存映射的块大小

参数
- blockSize: 核函数的块大小。

返回值
一个块所需的动态共享内存。

---

```c
typedef HGstream_st * HGstream
```
HGGC 流

---

```c
typedef void(HGGC_CB* HGstreamCallback )( HGstream hStream, HGresult status, void* userData )
```
HGGC 流回调

参数
- hStream: 回调被添加到的流，传递给 hgStreamAddCallback。可以为 NULL。
- HGresult status
- userData: 注册时提供的用户参数。

---

```c
typedef HGsurfObject_v1 HGsurfObject
```
代表 HGGC surface 对象的不透明值

---

```c
typedef unsigned long long HGsurfObject_v1
```
代表 HGGC surface 对象的不透明值

---

```c
typedef HGsurfref_st * HGsurfref
```
HGGC surface 引用

---

```c
typedef HGtexObject_v1 HGtexObject
```
代表 HGGC texture 对象的不透明值

---

```c
typedef unsigned long long HGtexObject_v1
```
代表 HGGC texture 对象的不透明值

---

```c
typedef HGtexref_st * HGtexref
```
HGGC texture 引用

---

```c
typedef HGuserObject_st * HGuserObject
```
用于图的 HGGC 用户对象

---

#### 7. 枚举类型 (Enumerations) - 详细说明 {#枚举类型-(Enumerations)---详细说明}

```text
enum HGGC_POINTER_ATTRIBUTE_ACCESS_FLAGS
```
指定当前上下文的设备对所引用内存的访问级别的访问标志。

值：

- `HG_POINTER_ATTRIBUTE_ACCESS_FLAG_NONE = 0x0` - 无访问权限，设备无法访问此内存，必须通过可访问内存进行暂存才能完成某些操作
- `HG_POINTER_ATTRIBUTE_ACCESS_FLAG_READ = 0x1` - 只读访问，对该内存的写入被视为无效访问并返回错误
- `HG_POINTER_ATTRIBUTE_ACCESS_FLAG_READWRITE = 0x3` - 读写访问，设备对该内存具有完全的读写访问权限

---

```text
enum HGGPUDirectRDMAWritesOrdering
```
GPUDirect RDMA 写入的平台原生排序。

值：

- `HG_GPU_DIRECT_RDMA_WRITES_ORDERING_NONE = 0` - 设备本身不支持远程写入的排序。
- `HG_GPU_DIRECT_RDMA_WRITES_ORDERING_OWNER = 100` - 设备本身可以一致地消费远程写入，但其他 HGGC 设备可能不行
- `HG_GPU_DIRECT_RDMA_WRITES_ORDERING_ALL_DEVICES = 200` - 系统中的任何 HGGC 设备都可以一致地消费对该设备的远程写入

---

```text
enum HGaccessProperty
```
指定与 HGaccessPolicyWindow 的 hitProp 和 missProp 成员一起使用的性能提示。

值：

- `HG_ACCESS_PROPERTY_NORMAL = 0` - 普通缓存持久性
- `HG_ACCESS_PROPERTY_STREAMING = 1` - 流式访问，不太可能从缓存中持久化
- `HG_ACCESS_PROPERTY_PERSISTING = 2` - 持久化访问，更可能缓存在缓存中

---

```text
enum HGaddress_mode
```
纹理引用寻址模式。

值：

- `HG_TR_ADDRESS_MODE_WRAP = 0` - 环绕寻址模式
- `HG_TR_ADDRESS_MODE_CLAMP = 1` - 钳制到边缘寻址模式
- `HG_TR_ADDRESS_MODE_MIRROR = 2` - 镜像寻址模式
- `HG_TR_ADDRESS_MODE_BORDER = 3` - 边界寻址模式

---

```text
enum HGarraySparseSubresourceType
```
稀疏子资源类型。

值：

- `HG_ARRAY_SPARSE_SUBRESOURCE_TYPE_SPARSE_LEVEL = 0` - 普通稀疏级别
- `HG_ARRAY_SPARSE_SUBRESOURCE_TYPE_MIPTAIL = 1` - Mip tail 级别

---

```text
enum HGarray_cubemap_face
```
立方体贴图面的数组索引。

值：

- `HG_CUBEMAP_FACE_POSITIVE_X = 0x00` - 立方体贴图的 X 正向面
- `HG_CUBEMAP_FACE_NEGATIVE_X = 0x01` - 立方体贴图的 X 负向面
- `HG_CUBEMAP_FACE_POSITIVE_Y = 0x02` - 立方体贴图的 Y 正向面
- `HG_CUBEMAP_FACE_NEGATIVE_Y = 0x03` - 立方体贴图的 Y 负向面
- `HG_CUBEMAP_FACE_POSITIVE_Z = 0x04` - 立方体贴图的 Z 正向面
- `HG_CUBEMAP_FACE_NEGATIVE_Z = 0x05` - 立方体贴图的 Z 负向面

---

```text
enum HGarray_format
```
数组格式。

值：

- `HG_AD_FORMAT_UNSIGNED_INT8 = 0x01` - 无符号 8 位整数
- `HG_AD_FORMAT_UNSIGNED_INT16 = 0x02` - 无符号 16 位整数
- `HG_AD_FORMAT_UNSIGNED_INT32 = 0x03` - 无符号 32 位整数
- `HG_AD_FORMAT_SIGNED_INT8 = 0x08` - 有符号 8 位整数
- `HG_AD_FORMAT_SIGNED_INT16 = 0x09` - 有符号 16 位整数
- `HG_AD_FORMAT_SIGNED_INT32 = 0x0a` - 有符号 32 位整数
- `HG_AD_FORMAT_HALF = 0x10` - 16 位浮点数
- `HG_AD_FORMAT_FLOAT = 0x20` - 32 位浮点数
- `HG_AD_FORMAT_NV12 = 0xb0` - 8 位 YUV 平面格式，4:2:0 采样
- `HG_AD_FORMAT_UNORM_INT8X1 = 0xc0` - 1 通道无符号 8 位归一化整数
- `HG_AD_FORMAT_UNORM_INT8X2 = 0xc1` - 2 通道无符号 8 位归一化整数
- `HG_AD_FORMAT_UNORM_INT8X4 = 0xc2` - 4 通道无符号 8 位归一化整数
- `HG_AD_FORMAT_UNORM_INT16X1 = 0xc3` - 1 通道无符号 16 位归一化整数
- `HG_AD_FORMAT_UNORM_INT16X2 = 0xc4` - 2 通道无符号 16 位归一化整数
- `HG_AD_FORMAT_UNORM_INT16X4 = 0xc5` - 4 通道无符号 16 位归一化整数
- `HG_AD_FORMAT_SNORM_INT8X1 = 0xc6` - 1 通道有符号 8 位归一化整数
- `HG_AD_FORMAT_SNORM_INT8X2 = 0xc7` - 2 通道有符号 8 位归一化整数
- `HG_AD_FORMAT_SNORM_INT8X4 = 0xc8` - 4 通道有符号 8 位归一化整数
- `HG_AD_FORMAT_SNORM_INT16X1 = 0xc9` - 1 通道有符号 16 位归一化整数
- `HG_AD_FORMAT_SNORM_INT16X2 = 0xca` - 2 通道有符号 16 位归一化整数
- `HG_AD_FORMAT_SNORM_INT16X4 = 0xcb` - 4 通道有符号 16 位归一化整数
- `HG_AD_FORMAT_BC1_UNORM = 0x91` - 4 通道无符号归一化块压缩（BC1 压缩）格式
- `HG_AD_FORMAT_BC1_UNORM_SRGB = 0x92` - 4 通道无符号归一化块压缩（BC1 压缩）格式，带 sRGB 编码
- `HG_AD_FORMAT_BC2_UNORM = 0x93` - 4 通道无符号归一化块压缩（BC2 压缩）格式
- `HG_AD_FORMAT_BC2_UNORM_SRGB = 0x94` - 4 通道无符号归一化块压缩（BC2 压缩）格式，带 sRGB 编码
- `HG_AD_FORMAT_BC3_UNORM = 0x95` - 4 通道无符号归一化块压缩（BC3 压缩）格式
- `HG_AD_FORMAT_BC3_UNORM_SRGB = 0x96` - 4 通道无符号归一化块压缩（BC3 压缩）格式，带 sRGB 编码
- `HG_AD_FORMAT_BC4_UNORM = 0x97` - 1 通道无符号归一化块压缩（BC4 压缩）格式
- `HG_AD_FORMAT_BC4_SNORM = 0x98` - 1 通道有符号归一化块压缩（BC4 压缩）格式
- `HG_AD_FORMAT_BC5_UNORM = 0x99` - 2 通道无符号归一化块压缩（BC5 压缩）格式
- `HG_AD_FORMAT_BC5_SNORM = 0x9a` - 2 通道有符号归一化块压缩（BC5 压缩）格式
- `HG_AD_FORMAT_BC6H_UF16 = 0x9b` - 3 通道无符号半浮点块压缩（BC6H 压缩）格式
- `HG_AD_FORMAT_BC6H_SF16 = 0x9c` - 3 通道有符号半浮点块压缩（BC6H 压缩）格式
- `HG_AD_FORMAT_BC7_UNORM = 0x9d` - 4 通道无符号归一化块压缩（BC7 压缩）格式
- `HG_AD_FORMAT_BC7_UNORM_SRGB = 0x9e` - 4 通道无符号归一化块压缩（BC7 压缩）格式，带 sRGB 编码
- `HG_AD_FORMAT_P010 = 0x9f` - 10 位 YUV 平面格式，4:2:0 采样
- `HG_AD_FORMAT_P016 = 0xa1` - 16 位 YUV 平面格式，4:2:0 采样
- `HG_AD_FORMAT_NV16 = 0xa2` - 8 位 YUV 平面格式，4:2:2 采样
- `HG_AD_FORMAT_P210 = 0xa3` - 10 位 YUV 平面格式，4:2:2 采样
- `HG_AD_FORMAT_P216 = 0xa4` - 16 位 YUV 平面格式，4:2:2 采样
- `HG_AD_FORMAT_YUY2 = 0xa5` - 2 通道，8 位 YUV 打包平面格式，4:2:2 采样
- `HG_AD_FORMAT_Y210 = 0xa6` - 2 通道，10 位 YUV 打包平面格式，4:2:2 采样
- `HG_AD_FORMAT_Y216 = 0xa7` - 2 通道，16 位 YUV 打包平面格式，4:2:2 采样
- `HG_AD_FORMAT_AYUV = 0xa8` - 4 通道，8 位 YUV 打包平面格式，4:4:4 采样
- `HG_AD_FORMAT_Y410 = 0xa9` - 10 位 YUV 打包平面格式，4:4:4 采样
- `HG_AD_FORMAT_Y416 = 0xb1` - 4 通道，12 位 YUV 打包平面格式，4:4:4 采样
- `HG_AD_FORMAT_Y444_PLANAR8 = 0xb2` - 3 通道 8 位 YUV 平面格式，4:4:4 采样
- `HG_AD_FORMAT_Y444_PLANAR10 = 0xb3` - 3 通道 10 位 YUV 平面格式，4:4:4 采样
- `HG_AD_FORMAT_YUV444_8bit_SemiPlanar = 0xb4` - 3 通道 8 位 YUV 半平面格式，4:4:4 采样
- `HG_AD_FORMAT_YUV444_16bit_SemiPlanar = 0xb5` - 3 通道 16 位 YUV 半平面格式，4:4:4 采样
- `HG_AD_FORMAT_UNORM_INT_101010_2 = 0x50` - 4 通道 unorm R10G10B10A2 RGB 格式
- `HG_AD_FORMAT_UINT8_PACKED_422 = 0x51` - 4 通道无符号 8 位 YUV 打包格式，4:2:2 采样
- `HG_AD_FORMAT_UINT8_PACKED_444 = 0x52` - 4 通道无符号 8 位 YUV 打包格式，4:4:4 采样
- `HG_AD_FORMAT_UINT8_SEMIPLANAR_420 = 0x53` - 3 通道无符号 8 位 YUV 半平面格式，4:2:0 采样
- `HG_AD_FORMAT_UINT16_SEMIPLANAR_420 = 0x54` - 3 通道无符号 16 位 YUV 半平面格式，4:2:0 采样
- `HG_AD_FORMAT_UINT8_SEMIPLANAR_422 = 0x55` - 3 通道无符号 8 位 YUV 半平面格式，4:2:2 采样
- `HG_AD_FORMAT_UINT16_SEMIPLANAR_422 = 0x56` - 3 通道无符号 16 位 YUV 半平面格式，4:2:2 采样
- `HG_AD_FORMAT_UINT8_SEMIPLANAR_444 = 0x57` - 3 通道无符号 8 位 YUV 半平面格式，4:4:4 采样
- `HG_AD_FORMAT_UINT16_SEMIPLANAR_444 = 0x58` - 3 通道无符号 16 位 YUV 半平面格式，4:4:4 采样
- `HG_AD_FORMAT_UINT8_PLANAR_420 = 0x59` - 3 通道无符号 8 位 YUV 平面格式，4:2:0 采样
- `HG_AD_FORMAT_UINT16_PLANAR_420 = 0x5a` - 3 通道无符号 16 位 YUV 平面格式，4:2:0 采样
- `HG_AD_FORMAT_UINT8_PLANAR_422 = 0x5b` - 3 通道无符号 8 位 YUV 平面格式，4:2:2 采样
- `HG_AD_FORMAT_UINT16_PLANAR_422 = 0x5c` - 3 通道无符号 16 位 YUV 平面格式，4:2:2 采样
- `HG_AD_FORMAT_UINT8_PLANAR_444 = 0x5d` - 3 通道无符号 8 位 YUV 平面格式，4:4:4 采样
- `HG_AD_FORMAT_UINT16_PLANAR_444 = 0x5e` - 3 通道无符号 16 位 YUV 平面格式，4:4:4 采样
- `HG_AD_FORMAT_MAX = 0x7FFFFFFF` - 最大格式值

---

```text
enum HGasyncNotificationType
```
可以发送的异步通知类型。

值：

- `HG_ASYNC_NOTIFICATION_TYPE_OVER_BUDGET = 0x1` - 当进程超出其设备内存预算时发送

---

```text
enum HGatomicOperation
```
HGGC 有效的原子操作。

值：

- `HG_ATOMIC_OPERATION_INTEGER_ADD = 0` - 整数加法
- `HG_ATOMIC_OPERATION_INTEGER_MIN = 1` - 整数最小值
- `HG_ATOMIC_OPERATION_INTEGER_MAX = 2` - 整数最大值
- `HG_ATOMIC_OPERATION_INTEGER_INCREMENT = 3` - 整数递增
- `HG_ATOMIC_OPERATION_INTEGER_DECREMENT = 4` - 整数递减
- `HG_ATOMIC_OPERATION_AND = 5` - 按位与
- `HG_ATOMIC_OPERATION_OR = 6` - 按位或
- `HG_ATOMIC_OPERATION_XOR = 7` - 按位异或
- `HG_ATOMIC_OPERATION_EXCHANGE = 8` - 交换
- `HG_ATOMIC_OPERATION_CAS = 9` - 比较并交换
- `HG_ATOMIC_OPERATION_FLOAT_ADD = 10` - 浮点数加法
- `HG_ATOMIC_OPERATION_FLOAT_MIN = 11` - 浮点数最小值
- `HG_ATOMIC_OPERATION_FLOAT_MAX = 12` - 浮点数最大值
- `HG_ATOMIC_OPERATION_MAX` - 最大操作枚举值

---

```text
enum HGatomicOperationCapability
```
HGGC 有效的原子操作能力。

值：

- `HG_ATOMIC_CAPABILITY_SIGNED = 1u<<0` - 有符号整数原子操作能力
- `HG_ATOMIC_CAPABILITY_UNSIGNED = 1u<<1` - 无符号整数原子操作能力
- `HG_ATOMIC_CAPABILITY_REDUCTION = 1u<<2` - 归约原子操作能力
- `HG_ATOMIC_CAPABILITY_SCALAR_32 = 1u<<3` - 32 位标量原子操作能力
- `HG_ATOMIC_CAPABILITY_SCALAR_64 = 1u<<4` - 64 位标量原子操作能力
- `HG_ATOMIC_CAPABILITY_SCALAR_128 = 1u<<5` - 128 位标量原子操作能力
- `HG_ATOMIC_CAPABILITY_VECTOR_32x4 = 1u<<6` - 32x4 向量原子操作能力

---

```text
enum HGclusterSchedulingPolicy
```
集群调度策略。

值：

- `HG_CLUSTER_SCHEDULING_POLICY_DEFAULT = 0` - 默认策略
- `HG_CLUSTER_SCHEDULING_POLICY_SPREAD = 1` - 在集群内的块之间均匀分散到 SM
- `HG_CLUSTER_SCHEDULING_POLICY_LOAD_BALANCING = 2` - 允许硬件在集群内的块之间进行负载均衡到 SM

---

```text
enum HGcomputemode
```
计算模式。

值：

- `HG_COMPUTEMODE_DEFAULT = 0` - 默认计算模式（允许每个设备有多个上下文）
- `HG_COMPUTEMODE_PROHIBITED = 2` - 计算禁止模式（此时无法在此设备上创建上下文）
- `HG_COMPUTEMODE_EXCLUSIVE_PROCESS = 3` - 计算独占进程模式（只有一个由单一进程使用的上下文可以存在于此设备上）

---

```text
enum HGctx_flags
```
上下文创建标志。

值：

- `HG_CTX_SCHED_AUTO = 0x00` - 自动调度模式
- `HG_CTX_SCHED_SPIN = 0x01` - 自旋调度模式
- `HG_CTX_SCHED_YIELD = 0x02` - 让步调度模式
- `HG_CTX_SCHED_BLOCKING_SYNC = 0x04` - 阻塞同步调度模式
- `HG_CTX_LAUNCH_MASK = 0x07` - 启动掩码

---

```text
enum HGdeviceNumaConfig
```
设备 NUMA 配置。

值：

- `HG_DEVICE_NUMA_CONFIG_UNKNOWN = 0` - 未知 NUMA 配置
- `HG_DEVICE_NUMA_CONFIG_NONE = 1` - 非 NUMA 配置

---

```text
enum HGdevice_P2PAttribute
```
设备 P2P（点对点）属性。

值：

- `HG_DEVICE_P2P_ATTRIBUTE_PERFORMANCE_RANK = 0` - 性能排名
- `HG_DEVICE_P2P_ATTRIBUTE_ACCESS_SUPPORTED = 1` - 是否支持 P2P 访问
- `HG_DEVICE_P2P_ATTRIBUTE_NATIVE_ATOMIC_SUPPORTED = 2` - 是否支持原生原子操作
- `HG_DEVICE_P2P_ATTRIBUTE_ACCESS_ACCESS_SUPPORTED = 3` - P2P 访问访问支持
- `HG_DEVICE_P2P_ATTRIBUTE_HGGC_ARRAY_ACCESS_SUPPORTED = 4` - HGGC 数组访问支持

---

```text
enum HGdevice_attribute
```
设备属性。

值：

- `HG_DEVICE_ATTRIBUTE_MAX_THREADS_PER_BLOCK = 1` - 每个块的最大线程数
- `HG_DEVICE_ATTRIBUTE_MAX_BLOCK_DIM_X = 2` - 块的最大 X 维度
- `HG_DEVICE_ATTRIBUTE_MAX_BLOCK_DIM_Y = 3` - 块的最大 Y 维度
- `HG_DEVICE_ATTRIBUTE_MAX_BLOCK_DIM_Z = 4` - 块的最大 Z 维度
- `HG_DEVICE_ATTRIBUTE_MAX_GRID_DIM_X = 5` - 网格的最大 X 维度
- `HG_DEVICE_ATTRIBUTE_MAX_GRID_DIM_Y = 6` - 网格的最大 Y 维度
- `HG_DEVICE_ATTRIBUTE_MAX_GRID_DIM_Z = 7` - 网格的最大 Z 维度
- `HG_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK = 8` - 每个块的最大共享内存
- `HG_DEVICE_ATTRIBUTE_TOTAL_CONSTANT_MEMORY = 9` - 总常量内存
- `HG_DEVICE_ATTRIBUTE_WARP_SIZE = 10` - Warp 大小
- `HG_DEVICE_ATTRIBUTE_MAX_PITCH = 11` - 最大内存 pitch
- `HG_DEVICE_ATTRIBUTE_MAX_REGISTERS_PER_BLOCK = 12` - 每个块的最大寄存器数
- `HG_DEVICE_ATTRIBUTE_CLOCK_RATE = 13` - 时钟频率
- `HG_DEVICE_ATTRIBUTE_TEXTURE_ALIGNMENT = 14` - 纹理对齐要求
- `HG_DEVICE_ATTRIBUTE_GPU_OVERLAP = 15` - PPU 重叠能力
- `HG_DEVICE_ATTRIBUTE_MULTIPROCESSOR_COUNT = 16` - 多处理器数量
- `HG_DEVICE_ATTRIBUTE_KERNEL_EXEC_TIMEOUT = 17` - 核函数执行超时
- `HG_DEVICE_ATTRIBUTE_INTEGRATED = 18` - 集成设备标志
- `HG_DEVICE_ATTRIBUTE_CAN_MAP_HOST_MEMORY = 19` - 可以映射主机内存
- `HG_DEVICE_ATTRIBUTE_COMPUTE_MODE = 20` - 计算模式
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURE1D_WIDTH = 21` - 最大 1D 纹理宽度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURE2D_WIDTH = 22` - 最大 2D 纹理宽度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURE2D_HEIGHT = 23` - 最大 2D 纹理高度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURE3D_WIDTH = 24` - 最大 3D 纹理宽度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURE3D_HEIGHT = 25` - 最大 3D 纹理高度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURE3D_DEPTH = 26` - 最大 3D 纹理深度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURE2D_ARRAY_WIDTH = 27` - 最大 2D 纹理数组宽度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURE2D_ARRAY_HEIGHT = 28` - 最大 2D 纹理数组高度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURE2D_ARRAY_NUMSLICES = 29` - 最大 2D 纹理数组切片数
- `HG_DEVICE_ATTRIBUTE_SURFACE_ALIGNMENT = 30` - 表面对齐要求
- `HG_DEVICE_ATTRIBUTE_CONCURRENT_KERNELS = 31` - 并发核函数支持
- `HG_DEVICE_ATTRIBUTE_ECC_ENABLED = 32` - ECC 启用
- `HG_DEVICE_ATTRIBUTE_PCI_BUS_ID = 33` - PCI 总线 ID
- `HG_DEVICE_ATTRIBUTE_PCI_DEVICE_ID = 34` - PCI 设备 ID
- `HG_DEVICE_ATTRIBUTE_MEMORY_CLOCK_RATE = 36` - 内存时钟频率
- `HG_DEVICE_ATTRIBUTE_GLOBAL_MEMORY_BUS_WIDTH = 37` - 全局内存总线宽度
- `HG_DEVICE_ATTRIBUTE_L2_CACHE_SIZE = 38` - L2 缓存大小
- `HG_DEVICE_ATTRIBUTE_MAX_THREADS_PER_MULTIPROCESSOR = 39` - 每个多处理器的最大线程数
- `HG_DEVICE_ATTRIBUTE_ASYNC_ENGINE_COUNT = 40` - 异步引擎数量
- `HG_DEVICE_ATTRIBUTE_UNIFIED_ADDRESSING = 41` - 统一寻址
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURE1D_LAYERED_WIDTH = 42` - 最大 1D 分层纹理宽度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURE1D_LAYERED_LAYERS = 43` - 最大 1D 分层纹理层数
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURE2D_GATHER_WIDTH = 45` - 最大 2D 收集纹理宽度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURE2D_GATHER_HEIGHT = 46` - 最大 2D 收集纹理高度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURE3D_WIDTH_ALT = 47` - 最大 3D 纹理宽度（备选）
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURE3D_HEIGHT_ALT = 48` - 最大 3D 纹理高度（备选）
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURE3D_DEPTH_ALT = 49` - 最大 3D 纹理深度（备选）
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURECUBEMAP_WIDTH = 50` - 最大立方体贴图纹理宽度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURECUBEMAP_LAYERED_WIDTH = 51` - 最大立方体贴图分层纹理宽度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURECUBEMAP_LAYERED_LAYERS = 52` - 最大立方体贴图分层纹理层数
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_SURFACE1D_WIDTH = 53` - 最大 1D 表面宽度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_SURFACE2D_WIDTH = 54` - 最大 2D 表面宽度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_SURFACE2D_HEIGHT = 55` - 最大 2D 表面高度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_SURFACE3D_WIDTH = 56` - 最大 3D 表面宽度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_SURFACE3D_HEIGHT = 57` - 最大 3D 表面高度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_SURFACE3D_DEPTH = 58` - 最大 3D 表面深度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_SURFACE1D_LAYERED_WIDTH = 59` - 最大 1D 分层表面宽度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_SURFACE1D_LAYERED_LAYERS = 60` - 最大 1D 分层表面层数
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_SURFACE2D_ARRAY_WIDTH = 61` - 最大 2D 数组表面宽度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_SURFACE2D_ARRAY_HEIGHT = 62` - 最大 2D 数组表面高度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_SURFACE2D_ARRAY_NUMSLICES = 63` - 最大 2D 数组表面切片数
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_SURFACECUBEMAP_WIDTH = 64` - 最大立方体表面宽度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_SURFACECUBEMAP_LAYERED_WIDTH = 65` - 最大立方体分层表面宽度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_SURFACECUBEMAP_LAYERED_LAYERS = 66` - 最大立方体分层表面层数
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURE1D_LINEAR_WIDTH = 67` - 最大 1D 线性纹理宽度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURE2D_LINEAR_WIDTH = 68` - 最大 2D 线性纹理宽度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURE2D_LINEAR_HEIGHT = 69` - 最大 2D 线性纹理高度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURE2D_LINEAR_PITCH = 70` - 最大 2D 线性纹理 pitch
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURE2D_MIPMAPPED_WIDTH = 71` - 最大 2D 多重映射纹理宽度
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURE2D_MIPMAPPED_HEIGHT = 72` - 最大 2D 多重映射纹理高度
- `HG_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MAJOR = 75` - 计算能力主版本
- `HG_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MINOR = 76` - 计算能力次版本
- `HG_DEVICE_ATTRIBUTE_MAXIMUM_TEXTURE1DMIPMAPPED_WIDTH = 78` - 最大 1D 多重映射纹理宽度
- `HG_DEVICE_ATTRIBUTE_STREAMS = 80` - 流数量
- `HG_DEVICE_ATTRIBUTE_L2_CACHE_MAX = 81` - L2 缓存最大值
- `HG_DEVICE_ATTRIBUTE_RESERVED_SHARED_MEMORY_PER_BLOCK = 82` - 每个块保留的共享内存
- `HG_DEVICE_ATTRIBUTE_SCAVE_ENABLED = 84` - SCAVE 启用
- `HG_DEVICE_ATTRIBUTE_HOST_NUMA_ID = 85` - 主机 NUMA ID
- `HG_DEVICE_ATTRIBUTE_HOST_NODE_AFFINITY = 86` - 主机节点亲和性
- `HG_DEVICE_ATTRIBUTE_DEVICE_NODE_AFFINITY = 87` - 设备节点亲和性
- `HG_DEVICE_ATTRIBUTE_CCCL_VERSION = 92` - CCCL 版本
- `HG_DEVICE_ATTRIBUTE_MAX_PERSISTING_L2_CACHE_SIZE = 95` - 最大持久化 L2 缓存大小
- `HG_DEVICE_ATTRIBUTE_MAX_ACCESS_POLICY_HOST_PAGE_SIZE = 96` - 最大主机页面访问策略大小
- `HG_DEVICE_ATTRIBUTE_VIRTUAL_ADDRESS_MANAGEMENT_SUPPORTED = 97` - 虚拟地址管理支持
- `HG_DEVICE_ATTRIBUTE_DMABUF_SUPPORTED = 98` - DMA-BUF 支持
- `HG_DEVICE_ATTRIBUTE_HOST_REGISTER_SUPPORTED = 99` - 主机注册支持
- `HG_DEVICE_ATTRIBUTE_HOST_SYNCHRONIZATION_SUPPORTED = 100` - 主机同步支持
- `HG_DEVICE_ATTRIBUTE_DIRECT_MANAGED_MEM_ACCESS_FROM_HOST_TENSOR = 101` - 主机张量直接访问托管内存
- `HG_DEVICE_ATTRIBUTE_MAX_TENSOR_MAP_MEMORY = 102` - 最大张量映射内存
- `HG_DEVICE_ATTRIBUTE_MAX_BLOCK_SM = 104` - 每个 SM 的最大块数
- `HG_DEVICE_ATTRIBUTE_MAX_PERSISTING_L2_CACHE_SIZE_ALTERNATE = 105` - 最大持久化 L2 缓存大小（备选）
- `HG_DEVICE_ATTRIBUTE_HOST_NUMA_NODE = 106` - 主机 NUMA 节点
- `HG_DEVICE_ATTRIBUTE_AVAILABLE_CLOCKS = 107` - 可用时钟频率列表
- `HG_DEVICE_ATTRIBUTE_BFLOAT16_SUPPORTED = 108` - bfloat16 支持
- `HG_DEVICE_ATTRIBUTE_DEFERRED_MAPPING_HGGC_ARRAY_SUPPORTED = 109` - 延迟映射 HGGC 数组支持
- `HG_DEVICE_ATTRIBUTE_MAX_BATCH_SIZE = 110` - 最大批量大小
- `HG_DEVICE_ATTRIBUTE_MAX_CLOCK_BANDRWIDTH = 111` - 最大时钟带宽
- `HG_DEVICE_ATTRIBUTE_MAX_STACKABLE_HOMES = 112` - 最大可堆叠 home 数

---

```text
enum HGdriverProcAddressQueryResult
```
驱动程序过程地址查询结果。

值：

- `HG_DRIVER_PROC_ADDRESS_QUERY_SUCCEEDED = 0` - 查询成功
- `HG_DRIVER_PROC_ADDRESS_QUERY_FAILED = 1` - 查询失败

---

```text
enum HGdriverProcAddress_flags
```
驱动程序过程地址标志。

值：

- `HG_DRIVER_PROC_ADDRESS_FLAGS_SYNCHRONIZATION = 1u << 0` - 同步标志

---

```text
enum HGeglColorFormat
```
颜色格式枚举。

值：

- `HG_EGL_COLOR_FORMAT_YUV4_4_4 = 0x00` - YUV 4:4:4 格式
- `HG_EGL_COLOR_FORMAT_YUV2 = 0x01` - YUV 4:2:2 格式
- `HG_EGL_COLOR_FORMAT_YVU9 = 0x02` - YVU 9 格式
- `HG_EGL_COLOR_FORMAT_YUV24 = 0x03` - YUV 4:4:4 格式
- `HG_EGL_COLOR_FORMAT_YUV420 = 0x04` - YUV 4:2:0 格式
- `HG_EGL_COLOR_FORMAT_YUV420_SEMIPLANAR = 0x05` - YUV 4:2:0 半平面格式
- `HG_EGL_COLOR_FORMAT_YVU420_SEMIPLANAR = 0x06` - YVU 4:2:0 半平面格式
- `HG_EGL_COLOR_FORMAT_YUV422_SEMIPLANAR = 0x07` - YUV 4:2:2 半平面格式
- `HG_EGL_COLOR_FORMAT_YUV422_H1V2 = 0x08` - YUV 4:2:2 格式（水平 1 垂直 2）
- `HG_EGL_COLOR_FORMAT_YUV422_H2V1 = 0x09` - YUV 4:2:2 格式（水平 2 垂直 1）
- `HG_EGL_COLOR_FORMAT_FLOAT = 0x0A` - 浮点格式
- `HG_EGL_COLOR_FORMAT_SAME = 0x0B` - 相同格式
- `HG_EGL_COLOR_FORMAT_8bit_R = 0x0C` - 8 位红色格式
- `HG_EGL_COLOR_FORMAT_16bit_R = 0x0D` - 16 位红色格式
- `HG_EGL_COLOR_FORMAT_16bit_RG = 0x0E` - 16 位红绿格式
- `HG_EGL_COLOR_FORMAT_32bit_RG = 0x0F` - 32 位红绿格式
- `HG_EGL_COLOR_FORMAT_8bit_Alpha = 0x10` - 8 位 Alpha 格式
- `HG_EGL_COLOR_FORMAT_16bit_FP16_Alpha = 0x11` - 16 位半精度浮点 Alpha 格式
- `HG_EGL_COLOR_FORMAT_16bit_FP_Alpha = 0x12` - 16 位浮点 Alpha 格式
- `HG_EGL_COLOR_FORMAT_32bit_FP_Alpha = 0x13` - 32 位浮点 Alpha 格式

---

```text
enum HGeglFrameType
```
EGL 帧类型。

值：

- `HG_EGL_FRAME_TYPE_ARRAY = 0x0` - 数组帧类型
- `HG_EGL_FRAME_TYPE_PITCH = 0x1` - Pitch 线性帧类型

---

```text
enum HGeglResourceLocationFlags
```
EGL 资源位置标志。

值：

- `HG_EGL_RESOURCE_LOCATION_SYSMEM = 0x0` - 系统内存位置
- `HG_EGL_RESOURCE_LOCATION_VIDMEM = 0x1` - 视频内存位置

---

```text
enum HGevent_flags
```
事件创建标志。

值：

- `HG_EVENT_DEFAULT = 0x0` - 默认事件标志
- `HG_EVENT_BLOCKING_SYNC = 0x1` - 阻塞同步事件
- `HG_EVENT_DISABLE_TIMING = 0x2` - 禁用计时事件
- `HG_EVENT_INTERPROCESS = 0x4` - 进程间事件

---

```text
enum HGevent_record_flags
```
事件记录标志。

值：

- `HG_EVENT_RECORD_FLAG_DEFAULT = 0x0` - 默认事件记录标志
- `HG_EVENT_RECORD_FLAG_EXTERNAL = 0x1` - 外部事件记录标志

---

```text
enum HGevent_sched_flags
```
事件调度标志。

值：

- `HG_EVENT_SCHED_FLAG_NONE = 0x0` - 无调度标志
- `HG_EVENT_SCHED_FLAG_SPIN = 0x1` - 自旋调度
- `HG_EVENT_SCHED_FLAG_YIELD = 0x2` - 让步调度
- `HG_EVENT_SCHED_FLAG_BLOCKING_SYNC = 0x4` - 阻塞同步调度

---

```text
enum HGevent_wait_flags
```
事件等待标志。

值：

- `HG_EVENT_WAIT_FLAG_NONE = 0x0` - 无等待标志

---

```text
enum HGexecAffinityType
```
执行亲和性类型。

值：

- `HG_EXEC_AFFINITY_TYPE_SM_COUNT = 0` - SM 数量执行亲和性

---

```text
enum HGexternalMemoryHandleType
```
外部内存句柄类型。

值：

- `HG_EXTERNAL_MEMORY_HANDLE_TYPE_OPAQUE_FD = 1` - 不透明文件描述符句柄类型
- `HG_EXTERNAL_MEMORY_HANDLE_TYPE_HGSCIBUF = 7` - HgSciBuf 句柄类型

---

```text
enum HGexternalSemaphoreHandleType
```
外部信号量句柄类型。

值：

- `HG_EXTERNAL_SEMAPHORE_HANDLE_TYPE_OPAQUE_FD = 1` - 不透明文件描述符句柄类型
- `HG_EXTERNAL_SEMAPHORE_HANDLE_TYPE_HGSCISYNC = 6` - HgSciSync 句柄类型
- `HG_EXTERNAL_SEMAPHORE_HANDLE_TYPE_DMABUF_FD = 7` - DMA-BUF 文件描述符句柄类型
- `HG_EXTERNAL_SEMAPHORE_HANDLE_TYPE_DMABUF_FD_PRODUCER = 8` - DMA-BUF 生产者文件描述符句柄类型
- `HG_EXTERNAL_SEMAPHORE_HANDLE_TYPE_DMABUF_FD_CONSUMER = 9` - DMA-BUF 消费者文件描述符句柄类型

---

```text
enum HGfilter_mode
```
纹理过滤模式。

值：

- `HG_TR_FILTER_MODE_POINT = 0` - 最近点采样过滤模式
- `HG_TR_FILTER_MODE_LINEAR = 1` - 线性过滤模式

---

```text
enum HGflushGPUDirectRDMAWritesOptions
```
刷新 GPUDirect RDMA 写入选项。

值：

- `HG_FLUSH_GPU_DIRECT_RDMA_WRITES_OPTIONS_DEFAULT = 0x0` - 默认选项
- `HG_FLUSH_GPU_DIRECT_RDMA_WRITES_OPTIONS_HOST_REGISTER = 1u << 0` - 主机注册选项
- `HG_FLUSH_GPU_DIRECT_RDMA_WRITES_OPTIONS_MEMOPS = 1u << 1` - 内存操作选项

---

```text
enum HGflushGPUDirectRDMAWritesScope
```
刷新 GPUDirect RDMA 写入作用域。

值：

- `HG_FLUSH_GPU_DIRECT_RDMA_WRITES_SCOPE_SYSTEM = 0` - 系统级刷新
- `HG_FLUSH_GPU_DIRECT_RDMA_WRITES_SCOPE_DEVICE = 1` - 设备级刷新

---

```text
enum HGflushGPUDirectRDMAWritesTarget
```
刷新 GPUDirect RDMA 写入目标。

值：

- `HG_FLUSH_GPU_DIRECT_RDMA_WRITES_TARGET_NONE = 0` - 无目标
- `HG_FLUSH_GPU_DIRECT_RDMA_WRITES_TARGET_CURRENT_DEVICE = 1` - 当前设备

---

```text
enum HGfunc_cache
```
函数缓存配置。

值：

- `HG_FUNC_CACHE_PREFER_NONE = 0x00` - 无偏好
- `HG_FUNC_CACHE_PREFER_SHARED = 0x01` - 偏好共享内存
- `HG_FUNC_CACHE_PREFER_L1 = 0x02` - 偏好 L1 缓存
- `HG_FUNC_CACHE_PREFER_EQUAL = 0x03` - 平等偏好

---

```text
enum HGfunction_attribute
```
函数属性。

值：

- `HG_FUNC_ATTRIBUTE_MAX_THREADS_PER_BLOCK = 0` - 每个块的最大线程数
- `HG_FUNC_ATTRIBUTE_SHARED_SIZE_BYTES = 1` - 共享内存大小（字节）
- `HG_FUNC_ATTRIBUTE_CONST_SIZE_BYTES = 2` - 常量内存大小（字节）
- `HG_FUNC_ATTRIBUTE_LOCAL_SIZE_BYTES = 3` - 本地内存大小（字节）
- `HG_FUNC_ATTRIBUTE_NUM_REGS = 4` - 寄存器数量
- `HG_FUNC_ATTRIBUTE_ASM_VERSION = 5` - ASM 规范版本
- `HG_FUNC_ATTRIBUTE_BINARY_VERSION = 6` - 二进制版本
- `HG_FUNC_ATTRIBUTE_CACHE_MODE_CA = 7` - 缓存模式 CA
- `HG_FUNC_ATTRIBUTE_MAX_DYNAMIC_SHARED_SIZE_BYTES = 8` - 最大动态共享内存大小（字节）
- `HG_FUNC_ATTRIBUTE_PREFERRED_SHARED_MEMORY_CARVEOUT = 9` - 首选共享内存分配比例
- `HG_FUNC_ATTRIBUTE_CLUSTER_SIZE_MUST_BE_SET = 10` - 必须设置集群大小
- `HG_FUNC_ATTRIBUTE_REQUIRED_CLUSTER_WIDTH = 11` - 所需集群宽度
- `HG_FUNC_ATTRIBUTE_REQUIRED_CLUSTER_HEIGHT = 12` - 所需集群高度
- `HG_FUNC_ATTRIBUTE_REQUIRED_CLUSTER_DEPTH = 13` - 所需集群深度
- `HG_FUNC_ATTRIBUTE_NON_PORTABLE_CLUSTER_SIZE_ALLOWED = 14` - 是否允许非可移植集群大小
- `HG_FUNC_ATTRIBUTE_CLUSTER_SCHEDULING_POLICY_PREFERENCE = 15` - 集群调度策略偏好
- `HG_FUNC_ATTRIBUTE_MAX = 16` - 属性枚举最大值
- `HG_FUNC_ATTRIBUTE_DISPATCH_STRATEGY = 128` - 调度策略
- `HG_FUNC_ATTRIBUTE_BLOCK_AGE_EN = 129` - 块老化机制使能
- `HG_FUNC_ATTRIBUTE_DISPATCH_MASK = 130` - 调度掩码

---

```text
enum HGgraphChildGraphNodeOwnership
```
图表子图节点所有权。

值：

- `HG_GRAPH_CHILD_GRAPH_NODE_OWNERSHIP_UNOWNED = 0` - 未拥有
- `HG_GRAPH_CHILD_GRAPH_NODE_OWNERSHIP_RETAIN_ON_RELEASE = 1` - 发布时保留
- `HG_GRAPH_CHILD_GRAPH_NODE_OWNERSHIP_TRANSFER_ON_RELEASE = 2` - 发布时转移

---

```text
enum HGgraphConditionalNodeType
```
图表条件节点类型。

值：

- `HG_GRAPH_CONDITIONAL_NODE_TYPE_IF = 0` - If 条件节点
- `HG_GRAPH_CONDITIONAL_NODE_TYPE_ELSE = 1` - Else 条件节点
- `HG_GRAPH_CONDITIONAL_NODE_TYPE_WHILE = 2` - While 循环节点
- `HG_GRAPH_CONDITIONAL_NODE_TYPE_FOR = 3` - For 循环节点

---

```text
enum HGgraphDebugDot_flags
```
图表调试点标志。

值：

- `HG_GRAPH_DEBUG_DOT_FLAGS_VERBOSE = 1u << 0` - 详细模式
- `HG_GRAPH_DEBUG_DOT_FLAGS_RUNTIME_ERRORS = 1u << 1` - 运行时错误
- `HG_GRAPH_DEBUG_DOT_FLAGS_NO_BREADTHFIRST = 1u << 2` - 不使用广度优先
- `HG_GRAPH_DEBUG_DOT_FLAGS_KERNEL_NODE_PARAMS = 1u << 3` - 核函数节点参数
- `HG_GRAPH_DEBUG_DOT_FLAGS_MEMSET_NODE_PARAMS = 1u << 4` - 内存设置节点参数
- `HG_GRAPH_DEBUG_DOT_FLAGS_MEMCPY_NODE_PARAMS = 1u << 5` - 内存复制节点参数
- `HG_GRAPH_DEBUG_DOT_FLAGS_HOST_NODE_PARAMS = 1u << 6` - 主机节点参数
- `HG_GRAPH_DEBUG_DOT_FLAGS_EVENT_NODE_PARAMS = 1u << 7` - 事件节点参数
- `HG_GRAPH_DEBUG_DOT_FLAGS_EXT_SEMAS_NODE_PARAMS = 1u << 8` - 外部信号量节点参数
- `HG_GRAPH_DEBUG_DOT_FLAGS_BATCH_MEMOP_NODE_PARAMS = 1u << 9` - 批量内存操作节点参数
- `HG_GRAPH_DEBUG_DOT_FLAGS_CONDITIONAL_NODE_PARAMS = 1u << 10` - 条件节点参数
- `HG_GRAPH_DEBUG_DOT_FLAGS_KERNEL_NODE_EXT_PARAMS = 1u << 11` - 核函数节点扩展参数
- `HG_GRAPH_DEBUG_DOT_FLAGS_HOST_NODE_EXT_PARAMS = 1u << 12` - 主机节点扩展参数
- `HG_GRAPH_DEBUG_DOT_FLAGS_BATCH_MEMOP_NODE_EXT_PARAMS = 1u << 13` - 批量内存操作节点扩展参数

---

```text
enum HGgraphDependencyType
```
图表依赖类型。

值：

 `HG_GRAPH_DEPENDENCY_TYPE_DEFAULT = 0` - 默认依赖类型
 `HG_GRAPH_DEPENDENCY_TYPE_PROGRAMMATIC = 1` - 可编程依赖类型
- `HG_GRAPH_DEPENDENCY_TYPE_SCHEDULING = 2` - 调度依赖类型

---

```text
enum HGgraphExecUpdateResult
```
图表执行更新结果。

值：

- `HG_GRAPH_EXEC_UPDATE_SUCCESS` - 更新成功
- `HG_GRAPH_EXEC_UPDATE_ERROR_TOPOLOGY_CHANGED = 1` - 拓扑已更改错误
- `HG_GRAPH_EXEC_UPDATE_ERROR_TYPE_CHANGED = 2` - 类型已更改错误
- `HG_GRAPH_EXEC_UPDATE_ERROR_FUNCTION_CHANGED = 3` - 函数已更改错误
- `HG_GRAPH_EXEC_UPDATE_ERROR_PARAMETERS_CHANGED = 4` - 参数已更改错误
- `HG_GRAPH_EXEC_UPDATE_ERROR_NOT_SUPPORTED = 5` - 不支持更新错误
- `HG_GRAPH_EXEC_UPDATE_ERROR_UNSPECIFIED = 6` - 未指定的错误
- `HG_GRAPH_EXEC_UPDATE_ERROR_STRUCTURE_CHANGED = 7` - 结构已更改错误
- `HG_GRAPH_EXEC_UPDATE_ERROR_REQUIRED_PORT_REMAPED = 8` - 所需端口重新映射错误
- `HG_GRAPH_EXEC_UPDATE_ERROR_REQUIRED_PORT_MISSING = 9` - 所需端口缺失错误

---

```text
enum HGgraphInstantiateResult
```
图表实例化结果。

值：

- `HG_GRAPH_INCARNATION_STATUS_SUCCESS = 0` - 图表实例化成功
- `HG_GRAPH_INCARNATION_STATUS_ERROR = 1` - 图表实例化错误
- `HG_GRAPH_INCARNATION_STATUS_INVALID = 2` - 图表实例化无效

---

```text
enum HGgraphInstantiate_flags
```
图表实例化标志。

值：

- `HG_GRAPH_INSTANTIATE_FLAG_AUTO_FREE_ON_LAUNCH = 1u << 0` - 启动时自动释放
- `HG_GRAPH_INSTANTIATE_FLAG_USE_NODE_PRIORITY = 1u << 1` - 使用节点优先级
- `HG_GRAPH_INSTANTIATE_FLAG_DEVICE_LAUNCH = 1u << 2` - 设备启动
- `HG_GRAPH_INSTANTIATE_FLAG_GRAPH_BUILD_AUTO_FREE_ON_LAST Launch = 1u << 3` - 最后一个启动时自动释放图表构建

---

```text
enum HGgraphNodeType
```
图表节点类型。

值：

- `HG_GRAPH_NODE_TYPE_EMPTY = 0` - 空节点
- `HG_GRAPH_NODE_TYPE_KERNEL = 1` - 核函数节点
- `HG_GRAPH_NODE_TYPE_MEMCPY = 2` - 内存复制节点
- `HG_GRAPH_NODE_TYPE_MEMSET = 3` - 内存设置节点
- `HG_GRAPH_NODE_TYPE_HOST = 4` - 主机节点
- `HG_GRAPH_NODE_TYPE_EVENT = 5` - 事件节点
- `HG_GRAPH_NODE_TYPE_EXT_SEMAS_SIGNAL = 6` - 外部信号量信号节点
- `HG_GRAPH_NODE_TYPE_EXT_SEMAS_WAIT = 7` - 外部信号量等待节点
- `HG_GRAPH_NODE_TYPE_BATCH_MEMOP = 8` - 批量内存操作节点
- `HG_GRAPH_NODE_TYPE_CONDITIONAL = 9` - 条件节点
- `HG_GRAPH_NODE_TYPE_EMPTY_V = 10` - 空节点 V
- `HG_GRAPH_NODE_TYPE_KERNEL_V = 11` - 核函数节点 V
- `HG_GRAPH_NODE_TYPE_MEMCPY_V = 12` - 内存复制节点 V
- `HG_GRAPH_NODE_TYPE_MEMSET_V = 13` - 内存设置节点 V
- `HG_GRAPH_NODE_TYPE_HOST_V = 14` - 主机节点 V
- `HG_GRAPH_NODE_TYPE_EVENT_V = 15` - 事件节点 V
- `HG_GRAPH_NODE_TYPE_EXT_SEMAS_SIGNAL_V = 16` - 外部信号量信号节点 V
- `HG_GRAPH_NODE_TYPE_EXT_SEMAS_WAIT_V = 17` - 外部信号量等待节点 V
- `HG_GRAPH_NODE_TYPE_BATCH_MEMOP_V = 18` - 批量内存操作节点 V
- `HG_GRAPH_NODE_TYPE_CONDITIONAL_V = 19` - 条件节点 V
- `HG_GRAPH_NODE_TYPE_COUNT` - 节点类型数量

---

```text
enum HGgraphicsMapResourceFlags
```
图形映射资源标志。

值：

- `HG_GRAPHICS_MAP_RESOURCE_FLAGS_NONE = 0x0` - 无标志
- `HG_GRAPHICS_MAP_RESOURCE_FLAGS_READ_ONLY = 0x1` - 只读映射
- `HG_GRAPHICS_MAP_RESOURCE_FLAGS_WRITE_DISCARD = 0x2` - 写丢弃映射

---

```text
enum HGgraphicsRegisterFlags
```
图形注册标志。

值：

- `HG_GRAPHICS_REGISTER_FLAGS_NONE = 0x0` - 无标志
- `HG_GRAPHICS_REGISTER_FLAGS_SURFACE_LOAD_STORE = 0x1` - 表面加载/存储注册
- `HG_GRAPHICS_REGISTER_FLAGS_TEXTURE_GATHER = 0x2` - 纹理收集注册

---

```text
enum HGipcMem_flags
```
IPC 内存标志。

值：

- `HG_IPC_MEM_COLLECTIVE_EXTENTS = 1u << 0` - 集合范围
- `HG_IPC_MEM_RESIZEABLE_EXTENTS = 1u << 1` - 可调整大小的范围

---

```text
enum HGjitInputType
```
JIT 编译输入类型。

值：

- `HG_JIT_INPUT_HGBIN = 0` - Hgbin 输入
- `HG_JIT_INPUT_ASM = 1` - ASM 输入
- `HG_JIT_INPUT_FATBINAR = 2` - Fatbinary 输入
- `HG_JIT_INPUT_OBJECT = 3` - 对象文件输入
- `HG_JIT_INPUT_LIBRARY = 4` - 库输入
- `HG_JIT_INPUT_HGVM = 5` - HGVM

---

```text
enum HGjit_cacheMode
```
JIT 缓存模式。

值：

- `HG_JIT_CACHE_MODE_NONE = 0` - 无缓存
- `HG_JIT_CACHE_MODE_CA = 1` - 缓存作为
- `HG_JIT_CACHE_MODE_CG = 2` - 缓存全局

---

```text
enum HGjit_fallback
```
JIT 回退策略。

值：

- `HG_PREFER_ASM = 0` - 优先使用 ASM
- `HG_PREFER_BINARY = 1` - 优先使用二进制

---

```text
enum HGjit_option
```
JIT 编译选项。

值：

- `HG_JIT_MAX_REGISTERS = 0` - 最大寄存器数
- `HG_JIT_THREADS_PER_BLOCK = 1` - 每个块的线程数
- `HG_JIT_WALL_TIME = 2` - 墙上时间
- `HG_JIT_INFO_LOG_BUFFER = 3` - 信息日志缓冲区
- `HG_JIT_INFO_LOG_BUFFER_SIZE_BYTES = 4` - 信息日志缓冲区大小（字节）
- `HG_JIT_ERROR_LOG_BUFFER = 5` - 错误日志缓冲区
- `HG_JIT_ERROR_LOG_BUFFER_SIZE_BYTES = 6` - 错误日志缓冲区大小（字节）
- `HG_JIT_OPTIMIZATION_LEVEL = 7` - 优化级别
- `HG_JIT_TARGET_FROM_HGCONTEXT = 8` - 从 HGGC 上下文获取目标
- `HG_JIT_TARGET = 9` - 目标架构
- `HG_JIT_FALLBACK_STRATEGY = 10` - 回退策略
- `HG_JIT_GENERATE_DEBUG_INFO = 11` - 生成调试信息
- `HG_JIT_LOG_VERBOSITY = 12` - 日志详细程度
- `HG_JIT_GENERATE_LINE_INFO = 13` - 生成行信息
- `HG_JIT_CACHE_MODE = 14` - 缓存模式

---

```text
enum HGjit_target
```
JIT 编译目标架构。

值：

- `HG_TARGET_COMPUTE_50 = 50` - 计算能力 5.0
- `HG_TARGET_COMPUTE_53 = 53` - 计算能力 5.3
- `HG_TARGET_COMPUTE_60 = 60` - 计算能力 6.0
- `HG_TARGET_COMPUTE_61 = 61` - 计算能力 6.1
- `HG_TARGET_COMPUTE_62 = 62` - 计算能力 6.2
- `HG_TARGET_COMPUTE_70 = 70` - 计算能力 7.0
- `HG_TARGET_COMPUTE_72 = 72` - 计算能力 7.2
- `HG_TARGET_COMPUTE_75 = 75` - 计算能力 7.5
- `HG_TARGET_COMPUTE_80 = 80` - 计算能力 8.0
- `HG_TARGET_COMPUTE_86 = 86` - 计算能力 8.6
- `HG_TARGET_COMPUTE_87 = 87` - 计算能力 8.7
- `HG_TARGET_COMPUTE_89 = 89` - 计算能力 8.9
- `HG_TARGET_COMPUTE_90 = 90` - 计算能力 9.0
- `HG_TARGET_COMPUTE_90A = 90` - 计算能力 9.0 (加速)
- `HG_TARGET_COMPUTE_100 = 100` - 计算能力 10.0
- `HG_TARGET_COMPUTE_101 = 101` - 计算能力 10.1
- `HG_TARGET_COMPUTE_102 = 102` - 计算能力 10.2
- `HG_TARGET_COMPUTE_103 = 103` - 计算能力 10.3
- `HG_TARGET_COMPUTE_110 = 110` - 计算能力 11.0
- `HG_TARGET_COMPUTE_120 = 120` - 计算能力 12.0
- `HG_TARGET_COMPUTE_120A = 120` - 计算能力 12.0 (加速)
- `HG_TARGET_COMPUTE_121 = 121` - 计算能力 12.1
- `HG_TARGET_COMPUTE_125 = 125` - 计算能力 12.5
- `HG_TARGET_COMPUTE_200 = 200` - 计算能力 20.0

---

```text
enum HGlaunchAttributeID
```
启动属性 ID。

值：

- `HG_LAUNCH_ATTRIBUTE_PRIORITY = 1` - 优先级属性
- `HG_LAUNCH_ATTRIBUTE_MEM_SYNC_DOMAIN_MAP = 2` - 内存同步域映射属性
- `HG_LAUNCH_ATTRIBUTE_MEM_SYNC_DOMAIN = 3` - 内存同步域属性
- `HG_LAUNCH_ATTRIBUTE_PORTABLE_CLUSTER_MODE = 4` - 便携式集群模式属性
- `HG_LAUNCH_ATTRIBUTE_CLUSTER_SIZE = 5` - 集群大小属性
- `HG_LAUNCH_ATTRIBUTE_HANDLES_DECOMPRESSION = 6` - 解压缩处理属性
- `HG_LAUNCH_ATTRIBUTE_ENABLE_LARGE_REGISTERS = 7` - 启用大寄存器属性
- `HG_LAUNCH_ATTRIBUTE_ACCESS_POLICY_WINDOW = 8` - 访问策略窗口属性
- `HG_LAUNCH_ATTRIBUTE_COOPERATIVE = 9` - 合作属性
- `HG_LAUNCH_ATTRIBUTE_END = 0x16` - 结束属性

---

```text
enum HGlaunchAttributePortableClusterMode
```
启动属性便携式集群模式。

值：

- `HG_LAUNCH_PORTABLE_CLUSTER_MODE_NONE = 0` - 无便携式集群
- `HG_LAUNCH_PORTABLE_CLUSTER_MODE_SINGLE = 1` - 单个便携式集群
- `HG_LAUNCH_PORTABLE_CLUSTER_MODE_MULTI = 2` - 多个便携式集群

---

```text
enum HGlaunchMemSyncDomain
```
启动内存同步域。

值：

- `HG_LAUNCH_MEM_SYNC_DOMAIN_DEFAULT = 0` - 默认内存同步域
- `HG_LAUNCH_MEM_SYNC_DOMAIN_SHARED = 1` - 共享内存同步域
- `HG_LAUNCH_MEM_SYNC_DOMAIN_GLOBAL = 2` - 全局内存同步域

---

```text
enum HGlibraryOption
```
库选项。

值：

- `HG_LIBRARY_OPTIONS_MAX` - 最大库选项

---

```text
enum HGlimit
```
资源限制。

值：

- `HG_LIMIT_STACK_SIZE = 0` - 堆栈大小限制
- `HG_LIMIT_PRINTF_FIFO_SIZE = 1` - printf FIFO 大小限制
- `HG_LIMIT_MALLOC_HEAP_SIZE = 2` - malloc 堆大小限制
- `HG_LIMIT_DEV_RUNTIME_SYNC_DEPTH = 3` - 设备运行时同步深度限制
- `HG_LIMIT_DEV_RUNTIME_PENDING_LAUNCH_COUNT = 4` - 设备运行时待启动计数限制
- `HG_LIMIT_MAX_L2_FETCH_GRANULARITY = 5` - 最大 L2 获取粒度限制
- `HG_LIMIT_TEMP_DESTROY_HEAP_SIZE = 6` - 临时销毁堆大小限制
- `HG_LIMIT_PERSISTING_L2_CACHE_SIZE = 7` - 持久化 L2 缓存大小限制
- `HG_LIMIT_MAX_INDEPENDENT_STREAMS = 8` - 最大独立流数量限制
- `HG_LIMIT_MAX_BLOCK_DIM = 9` - 最大块维度限制
- `HG_LIMIT_MAX_GRID_DIM = 10` - 最大网格维度限制
- `HG_LIMIT_MAX_WARP_NUMBER = 11` - 最大 Warp 数量限制
- `HG_LIMIT_CLUSTER_SIZE = 12` - 集群大小限制

---

```text
enum HGmemAccess_flags
```
内存访问标志。

值：

- `HG_MEM_ACCESS_FLAGS_PROT_NONE = 0` - 无访问权限
- `HG_MEM_ACCESS_FLAGS_PROT_READ = 1` - 只读访问权限
- `HG_MEM_ACCESS_FLAGS_PROT_READWRITE = 3` - 读写访问权限

---

```text
enum HGmemAllocationCompType
```
内存分配压缩类型。

值：

- `HG_MEM_ALLOCATION_COMP_NONE = 0` - 无压缩
- `HG_MEM_ALLOCATION_COMP_GENERIC = 1` - 通用压缩

---

```text
enum HGmemAllocationGranularity_flags
```
内存分配粒度标志。

值：

- `HG_MEM_ALLOCATION_GRANULARITY_MINIMUM = 0` - 最小粒度
- `HG_MEM_ALLOCATION_GRANULARITY_RECOMMENDED = 1` - 推荐粒度

---

```text
enum HGmemAllocationHandleType
```
内存分配句柄类型。

值：

- `HG_MEM_ALLOCATION_HANDLE_NONE = 0` - 无句柄
- `HG_MEM_ALLOCATION_HANDLE_POSIX_FILE_DESCRIPTOR = 1` - POSIX 文件描述符句柄
- `HG_MEM_ALLOCATION_HANDLE_TYPE_MAX` - 最大句柄类型

---

```text
enum HGmemAllocationType
```
内存分配类型。

值：

- `HG_MEM_ALLOCATION_TYPE_INVALID = 0` - 无效分配类型
- `HG_MEM_ALLOCATION_TYPE_PINNED = 1` - 固定内存分配类型
- `HG_MEM_ALLOCATION_TYPE_EVICTABLE = 2` - 可驱逐分配类型
- `HG_MEM_ALLOCATION_TYPE_MAX` - 最大分配类型

---

```text
enum HGmemAttach_flags
```
内存附加标志。

值：

- `HG_MEM_ATTACH_GLOBAL = 1` - 全局内存附加
- `HG_MEM_ATTACH_HOST = 2` - 主机内存附加
- `HG_MEM_ATTACH_SINGLE = 4` - 单设备内存附加

---

```text
enum HGmemHandleType
```
内存句柄类型。

值：

- `HG_MEM_HANDLE_TYPE_NONE = 0` - 无句柄类型
- `HG_MEM_HANDLE_TYPE_POSIX_FILE_DESCRIPTOR = 1` - POSIX 文件描述符句柄类型
- `HG_MEM_HANDLE_TYPE_MAX` - 最大句柄类型

---

```text
enum HGmemLocationType
```
内存位置类型。

值：

- `HG_MEM_LOCATION_TYPE_INVALID = 0` - 无效位置类型
- `HG_MEM_LOCATION_TYPE_HOST = 1` - 主机位置类型
- `HG_MEM_LOCATION_TYPE_DEVICE = 2` - 设备位置类型
- `HG_MEM_LOCATION_TYPE_HOST_NUMA = 3` - 主机 NUMA 位置类型
- `HG_MEM_LOCATION_TYPE_HOST_NUMA_CURRENT = 4` - 当前主机 NUMA 位置类型

---

```text
enum HGmemOperationType
```
内存操作类型。

值：

- `HG_MEM_OPERATION_TYPE_MAP = 1` - 映射操作类型
- `HG_MEM_OPERATION_TYPE_UNMAP = 2` - 取消映射操作类型

---

```text
enum HGmemPool_attribute
```
内存池属性。

值：

- `HG_MEM_POOL_ATTR_RELEASE_THRESHOLD = 1` - 释放阈值属性
- `HG_MEM_POOL_ATTR_RESERVED_SIZE_CURRENT = 2` - 当前保留大小属性
- `HG_MEM_POOL_ATTR_RESERVED_SIZE_HIGH = 3` - 高保留大小属性
- `HG_MEM_POOL_ATTR_MIN_ALLOC_SIZE = 4` - 最小分配大小属性
- `HG_MEM_POOL_ATTR_VISIBLE_MEMFD = 5` - 可见内存文件描述符属性
- `HG_MEM_POOL_ATTR_SYSMEM_CG_TYPE = 6` - 系统内存 CG 类型属性
- `HG_MEM_POOL_ATTR_SYSMEM_ALLOCATION_TYPE = 7` - 系统内存分配类型属性
- `HG_MEM_POOL_ATTR_PAGEABLE_MEMORY_ACCESS = 8` - 分页内存访问属性
- `HG_MEM_POOL_ATTR_PAGEABLE_MEMORY_ACCESS_USES_HOST_PAGE_TABLES = 9` - 分页内存访问使用主机页表属性
- `HG_MEM_POOL_ATTR_COOPERATIVE = 10` - 合作属性
- `HG_MEM_POOL_ATTR_ACCESS_SPILLING = 11` - 访问溢出属性
- `HG_MEM_POOL_ATTR_MAX_AVAILABLE_SIZE` - 最大可用大小属性

---

```text
enum HGmemRangeFlags
```
内存范围标志。

值：

- `HG_MEM_RANGE_FLAGS_NONE = 0` - 无标志
- `HG_MEM_RANGE_FLAGS_READ_MOSTLY = 1u << 0` - 读优先标志
- `HG_MEM_RANGE_FLAGS_PREFERRED_LOCATION = 1u << 1` - 首选位置标志
- `HG_MEM_RANGE_FLAGS_ALLOCATE_PREFERRED_LOCATION = 1u << 2` - 分配首选位置标志
- `HG_MEM_RANGE_FLAGS_APP_APPROPAGATE = 1u << 3` - 应用传播标志
- `HG_MEM_RANGE_FLAGS_INITIALIZE = 1u << 4` - 初始化标志
- `HG_MEM_RANGE_FLAGS_KEEP_ABOVE = 1u << 5` - 保持在上方标志
- `HG_MEM_RANGE_FLAGS_KEEP_BELOW = 1u << 6` - 保持在下方标志
- `HG_MEM_RANGE_FLAGS_EVICT_IF_AVAILABLE_POSSIBLE = 1u << 7` - 可用时驱逐标志
- `HG_MEM_RANGE_FLAGS_NON_EVICTABLE = 1u << 8` - 不可驱逐标志
- `HG_MEM_RANGE_FLAGS_MAX` - 最大标志

---

```text
enum HGmemRangeHandleType
```
内存范围句柄类型。

值：

- `HG_MEM_RANGE_HANDLE_TYPE_NONE = 0` - 无句柄类型
- `HG_MEM_RANGE_HANDLE_TYPE_POSIX_FILE_DESCRIPTOR = 1` - POSIX 文件描述符句柄类型

---

```text
enum HGmem_advise
```
内存建议。

值：

- `HG_MEM_ADVISE_SET_READ_MOSTLY = 1` - 设置读优先
- `HG_MEM_ADVISE_UNSET_READ_MOSTLY = 2` - 取消读优先
- `HG_MEM_ADVISE_SET_PREFERRED_LOCATION = 3` - 设置首选位置
- `HG_MEM_ADVISE_UNSET_PREFERRED_LOCATION = 4` - 取消首选位置
- `HG_MEM_ADVISE_SET_ACCESSED_BY = 5` - 设置被访问设备
- `HG_MEM_ADVISE_UNSET_ACCESSED_BY = 6` - 取消被访问设备
- `HG_MEM_ADVISE_SET_COHERENT = 7` - 设置一致
- `HG_MEM_ADVISE_UNSET_COHERENT = 8` - 取消一致
- `HG_MEM_ADVISE_SET_JIT_FENCED = 9` - 设置 JIT 隔离
- `HG_MEM_ADVISE_UNSET_JIT_FENCED = 10` - 取消 JIT 隔离
- `HG_MEM_ADVISE_SET_NON_EVICTABLE = 11` - 设置不可驱逐
- `HG_MEM_ADVISE_UNSET_NON_EVICTABLE = 12` - 取消不可驱逐

---

```text
enum HGmemcpy3DOperandType
```
3D 内存复制操作数类型。

值：

- `HG_MEMCPY3D_OPERAND_TYPE_1D = 0` - 1D 操作数类型
- `HG_MEMCPY3D_OPERAND_TYPE_3D = 1` - 3D 操作数类型
- `HG_MEMCPY3D_OPERAND_TYPE_MAX` - 最大操作数类型

---

```text
enum HGmemcpyFlags
```
内存复制标志。

值：

- `HG_MEMCPY_AUTO = 0` - 自动内存复制
- `HG_MEMCPY_HOST_TO_HOST = 1` - 主机到主机复制
- `HG_MEMCPY_HOST_TO_DEVICE = 2` - 主机到设备复制
- `HG_MEMCPY_DEVICE_TO_HOST = 3` - 设备到主机复制
- `HG_MEMCPY_DEVICE_TO_DEVICE = 4` - 设备到设备复制
- `HG_MEMCPY_DEFAULT = 5` - 默认内存复制

---

```text
enum HGmemcpySrcAccessOrder
```
内存复制源访问顺序。

值：

- `HG_MEMCPY_SRC_ACCESS_ORDER_PERSISTING = 0` - 持久化源访问顺序
- `HG_MEMCPY_SRC_ACCESS_ORDER_CURRENT = 1` - 当前源访问顺序

---

```text
enum HGmemorytype
```
内存类型。

值：

- `HG_MEMORYTYPE_HOST = 1` - 主机内存
- `HG_MEMORYTYPE_DEVICE = 2` - 设备内存
- `HG_MEMORYTYPE_ARRAY = 3` - 数组内存
- `HG_MEMORYTYPE_UNIFIED = 4` - 统一内存

---

```text
enum HGmulticastGranularity_flags
```
多播粒度标志。

值：

- `HG_MULTICAST_GRANULARITY_DEFAULT = 0` - 默认粒度
- `HG_MULTICAST_GRANULARITY_RECOMMENDED = 1` - 推荐粒度
- `HG_MULTICAST_GRANULARITY_MINIMUM = 2` - 最小粒度

---

```text
enum HGoccupancy_flags
```
占用率标志。

值：

- `HG_OCCUPANCY_DEFAULT = 0` - 默认占用率
- `HG_OCCUPANCY_DISABLE_CACHING = 1` - 禁用缓存
- `HG_OCCUPANCY_RESTRICTED_SHARED_SIZE = 2` - 限制共享内存大小

---

```text
enum HGpointer_attribute
```
指针属性。

值：

- `HG_POINTER_ATTRIBUTE_CONTEXT = 1` - 上下文属性
- `HG_POINTER_ATTRIBUTE_MEMORY_TYPE = 2` - 内存类型属性
- `HG_POINTER_ATTRIBUTE_DEVICE_POINTER = 3` - 设备指针属性
- `HG_POINTER_ATTRIBUTE_HOST_POINTER = 4` - 主机指针属性
- `HG_POINTER_ATTRIBUTE_P2P_TOKENS = 5` - P2P 令牌属性
- `HG_POINTER_ATTRIBUTE_SYNC_MEMOPS = 6` - 同步内存操作属性
- `HG_POINTER_ATTRIBUTE_BUFFER_ID = 7` - 缓冲区 ID 属性
- `HG_POINTER_ATTRIBUTE_IS_MANAGED = 8` - 是否托管属性
- `HG_POINTER_ATTRIBUTE_DEVICE_ACCESSIBLE = 9` - 设备可访问属性
- `HG_POINTER_ATTRIBUTE_HOST_REGISTERED = 10` - 主机注册属性
- `HG_POINTER_ATTRIBUTE_IS_LEGACY_HGGC_IPC_CAPABLE = 11` - 是否为传统 HGGC IPC 兼容属性
- `HG_POINTER_ATTRIBUTE_RANGE_START_ADDR = 12` - 范围起始地址属性
- `HG_POINTER_ATTRIBUTE_RANGE_SIZE = 13` - 范围大小属性
- `HG_POINTER_ATTRIBUTE_MAPPED = 14` - 映射属性
- `HG_POINTER_ATTRIBUTE_ALLOWED_HANDLE_TYPES = 15` - 允许的句柄类型属性
- `HG_POINTER_ATTRIBUTE_IS_GPUDirectRDMAWriteOrderingNonCoherent = 16` - 是否为 GPUDirect RDMA 写入排序非一致属性
- `HG_POINTER_ATTRIBUTE_ACCESS_FLAGS = 17` - 访问标志属性
- `HG_POINTER_ATTRIBUTE_MEMORY_TYPE = 18` - 内存类型属性（已弃用，请使用 HG_POINTER_ATTRIBUTE_MEMORY_TYPE）
- `HG_POINTER_ATTRIBUTE_PROCESS_AFFINITY = 19` - 进程亲和性属性
- `HG_POINTER_ATTRIBUTE_SYNC_MEMOPS_RANGE_COPIES_SYNCHRONOUS = 20` - 同步内存操作范围复制同步属性
- `HG_POINTER_ATTRIBUTE_MEMOPS_COPIES_SYNCHRONOUS = 21` - 内存操作复制同步属性
- `HG_POINTER_ATTRIBUTE_REQUIRE_BF16_HGGC_IPC_CAPABLE = 22` - 需要 BF16 HGGC IPC 兼容属性
- `HG_POINTER_ATTRIBUTE_IS_HGGCIPCCAPABLE = 23` - 是否为 HGGC IPC 兼容属性

---

```text
enum HGprocessState
```
进程状态。

值：

- `HG_PROCESS_STATE_DETACHED = 0` - 分离状态
- `HG_PROCESS_STATE_RUNNING = 1` - 运行状态
- `HG_PROCESS_STATE_SUSPENDED = 2` - 暂停状态

---

```text
enum HGresourceViewFormat
```
资源视图格式。

值：

- `HG_RES_VIEW_FORMAT_NONE = 0x00` - 无格式
- `HG_RES_VIEW_FORMAT_UINT_1X8 = 0x01` - 1x8 无符号整数格式
- `HG_RES_VIEW_FORMAT_UINT_2X8 = 0x02` - 2x8 无符号整数格式
- `HG_RES_VIEW_FORMAT_UINT_4X8 = 0x03` - 4x8 无符号整数格式
- `HG_RES_VIEW_FORMAT_UINT_1X16 = 0x04` - 1x16 无符号整数格式
- `HG_RES_VIEW_FORMAT_UINT_2X16 = 0x05` - 2x16 无符号整数格式
- `HG_RES_VIEW_FORMAT_UINT_4X16 = 0x06` - 4x16 无符号整数格式
- `HG_RES_VIEW_FORMAT_UINT_1X32 = 0x07` - 1x32 无符号整数格式
- `HG_RES_VIEW_FORMAT_UINT_2X32 = 0x08` - 2x32 无符号整数格式
- `HG_RES_VIEW_FORMAT_UINT_4X32 = 0x09` - 4x32 无符号整数格式
- `HG_RES_VIEW_FORMAT_SINT_1X8 = 0x10` - 1x8 有符号整数格式
- `HG_RES_VIEW_FORMAT_SINT_2X8 = 0x11` - 2x8 有符号整数格式
- `HG_RES_VIEW_FORMAT_SINT_4X8 = 0x12` - 4x8 有符号整数格式
- `HG_RES_VIEW_FORMAT_SINT_1X16 = 0x13` - 1x16 有符号整数格式
- `HG_RES_VIEW_FORMAT_SINT_2X16 = 0x14` - 2x16 有符号整数格式
- `HG_RES_VIEW_FORMAT_SINT_4X16 = 0x15` - 4x16 有符号整数格式
- `HG_RES_VIEW_FORMAT_SINT_1X32 = 0x16` - 1x32 有符号整数格式
- `HG_RES_VIEW_FORMAT_SINT_2X32 = 0x17` - 2x32 有符号整数格式
- `HG_RES_VIEW_FORMAT_SINT_4X32 = 0x18` - 4x32 有符号整数格式
- `HG_RES_VIEW_FORMAT_FLOAT_1X16 = 0x19` - 1x16 浮点格式
- `HG_RES_VIEW_FORMAT_FLOAT_2X16 = 0x1A` - 2x16 浮点格式
- `HG_RES_VIEW_FORMAT_FLOAT_4X16 = 0x1B` - 4x16 浮点格式
- `HG_RES_VIEW_FORMAT_FLOAT_1X32 = 0x1C` - 1x32 浮点格式
- `HG_RES_VIEW_FORMAT_FLOAT_2X32 = 0x1D` - 2x32 浮点格式
- `HG_RES_VIEW_FORMAT_FLOAT_4X32 = 0x1E` - 4x32 浮点格式
- `HG_RES_VIEW_FORMAT_UNORM_1X8 = 0x20` - 1x8 归一化格式
- `HG_RES_VIEW_FORMAT_UNORM_2X8 = 0x21` - 2x8 归一化格式
- `HG_RES_VIEW_FORMAT_UNORM_4X8 = 0x22` - 4x8 归一化格式
- `HG_RES_VIEW_FORMAT_UNORM_1X16 = 0x23` - 1x16 归一化格式
- `HG_RES_VIEW_FORMAT_UNORM_2X16 = 0x24` - 2x16 归一化格式
- `HG_RES_VIEW_FORMAT_UNORM_4X16 = 0x25` - 4x16 归一化格式
- `HG_RES_VIEW_FORMAT_SNORM_1X8 = 0x28` - 1x8 signed 归一化格式
- `HG_RES_VIEW_FORMAT_SNORM_2X8 = 0x29` - 2x8 signed 归一化格式
- `HG_RES_VIEW_FORMAT_SNORM_4X8 = 0x2A` - 4x8 signed 归一化格式
- `HG_RES_VIEW_FORMAT_SNORM_1X16 = 0x2B` - 1x16 signed 归一化格式
- `HG_RES_VIEW_FORMAT_SNORM_2X16 = 0x2C` - 2x16 signed 归一化格式
- `HG_RES_VIEW_FORMAT_SNORM_4X16 = 0x2D` - 4x16 signed 归一化格式

---

```text
enum HGresourcetype
```
资源类型。

值：

- `HG_RESOURCE_TYPE_NULL = 0` - 空资源类型
- `HG_RESOURCE_TYPE_LINEAR = 1` - 线性资源类型
- `HG_RESOURCE_TYPE_ARRAY = 2` - 数组资源类型
- `HG_RESOURCE_TYPE_PITCH2D = 3` - Pitch 2D 资源类型
- `HG_RESOURCE_TYPE_MIPMAPPED_ARRAY = 4` - 多重映射数组资源类型
- `HG_RESOURCE_TYPE_MIPMAPPED_ARRAY_ALT = 5` - 多重映射数组资源类型（备选）

---

```text
enum HGresult
```
HGGC 函数调用结果。

值：

- `HGGC_SUCCESS = 0` - 调用成功
- `HGGC_ERROR_INVALID_VALUE = 1` - 无效值错误
- `HGGC_ERROR_OUT_OF_MEMORY = 2` - 内存不足错误
- `HGGC_ERROR_NOT_INITIALIZED = 3` - 未初始化错误
- `HGGC_ERROR_DEINITIALIZED = 4` - 已反初始化错误
- `HGGC_ERROR_PROFILER_DISABLED = 5` - 性能分析器已禁用错误
- `HGGC_ERROR_PROFILER_NOT_INITIALIZED = 6` - 性能分析器未初始化错误
- `HGGC_ERROR_PROFILER_ALREADY_STARTED = 7` - 性能分析器已启动错误
- `HGGC_ERROR_PROFILER_ALREADY_STOPPED = 8` - 性能分析器已停止错误
- `HGGC_ERROR_STUB_LIBRARY = 34` - 加载的 HGGC 驱动为桩库错误
- `HGGC_ERROR_CALL_REQUIRES_NEWER_DRIVER = 36` - 调用需要更新版本驱动错误
- `HGGC_ERROR_DEVICE_UNAVAILABLE = 46` - 设备不可用错误
- `HGGC_ERROR_NO_DEVICE = 100` - 无设备错误
- `HGGC_ERROR_INVALID_DEVICE = 101` - 无效设备错误
- `HGGC_ERROR_DEVICE_NOT_LICENSED = 102` - 设备未获得 Grid 许可证错误
- `HGGC_ERROR_INVALID_IMAGE = 200` - 无效图像错误
- `HGGC_ERROR_INVALID_CONTEXT = 201` - 无效上下文错误
- `HGGC_ERROR_CONTEXT_ALREADY_CURRENT = 202` - 上下文已当前错误
- `HGGC_ERROR_MAP_FAILED = 205` - 映射失败错误
- `HGGC_ERROR_UNMAP_FAILED = 206` - 取消映射失败错误
- `HGGC_ERROR_ARRAY_IS_MAPPED = 207` - 数组已映射错误
- `HGGC_ERROR_ALREADY_MAPPED = 208` - 已映射错误
- `HGGC_ERROR_NO_BINARY_FOR_GPU = 209` - 无适用于 PPU 的二进制错误
- `HGGC_ERROR_ALREADY_ACQUIRED = 210` - 已获取错误
- `HGGC_ERROR_NOT_MAPPED = 211` - 未映射错误
- `HGGC_ERROR_NOT_MAPPED_AS_ARRAY = 212` - 未作为数组映射错误
- `HGGC_ERROR_NOT_MAPPED_AS_POINTER = 213` - 未作为指针映射错误
- `HGGC_ERROR_ECC_UNCORRECTABLE = 214` - 不可纠正的 ECC 错误
- `HGGC_ERROR_UNSUPPORTED_LIMIT = 215` - 不支持的限制错误
- `HGGC_ERROR_CONTEXT_ALREADY_IN_USE = 216` - 上下文已在使用错误
- `HGGC_ERROR_PEER_ACCESS_UNSUPPORTED = 217` - 设备间不支持对等访问错误
- `HGGC_ERROR_INVALID_ASM = 218` - ASM JIT 编译失败错误
- `HGGC_ERROR_INVALID_GRAPHICS_CONTEXT = 219` - 无效图形上下文错误
- `HGGC_ERROR_ICNLINK_UNCORRECTABLE = 220` - ICNLink 不可纠正错误
- `HGGC_ERROR_JIT_COMPILER_NOT_FOUND = 221` - ASM JIT 编译器未找到错误
- `HGGC_ERROR_UNSUPPORTED_ASM_VERSION = 222` - ASM 编译工具链版本不支持错误
- `HGGC_ERROR_JIT_COMPILATION_DISABLED = 223` - TIX JIT 编译已禁用错误
- `HGGC_ERROR_UNSUPPORTED_EXEC_AFFINITY = 224` - 设备不支持该执行亲和性类型错误
- `HGGC_ERROR_UNSUPPORTED_DEVSIDE_SYNC = 225` - TIX JIT 不支持设备端同步调用错误
- `HGGC_ERROR_CONTAINED = 226` - PPU 设备异常已被错误遏制容器捕获错误
- `HGGC_ERROR_INVALID_SOURCE = 300` - 无效源错误
- `HGGC_ERROR_FILE_NOT_FOUND = 301` - 文件未找到错误
- `HGGC_ERROR_SHARED_OBJECT_SYMBOL_NOT_FOUND = 302` - 共享对象符号未找到错误
- `HGGC_ERROR_SHARED_OBJECT_INIT_FAILED = 303` - 共享对象初始化失败错误
- `HGGC_ERROR_OPERATING_SYSTEM = 304` - 操作系统错误
- `HGGC_ERROR_INVALID_HANDLE = 400` - 无效句柄错误
- `HGGC_ERROR_ILLEGAL_STATE = 401` - 资源状态非法错误
- `HGGC_ERROR_LOSSY_QUERY = 402` - 有损查询错误
- `HGGC_ERROR_NOT_FOUND = 500` - 未找到错误
- `HGGC_ERROR_NOT_READY = 600` - 未就绪错误
- `HGGC_ERROR_ILLEGAL_ADDRESS = 700` - 核函数执行时访问非法内存地址错误
- `HGGC_ERROR_LAUNCH_OUT_OF_RESOURCES = 701` - 启动超出资源错误
- `HGGC_ERROR_LAUNCH_TIMEOUT = 702` - 启动超时错误
- `HGGC_ERROR_LAUNCH_INCOMPATIBLE_TEXTURING = 703` - 启动纹理不兼容错误
- `HGGC_ERROR_PEER_ACCESS_ALREADY_ENABLED = 704` - 对等访问已启用错误
- `HGGC_ERROR_PEER_ACCESS_NOT_ENABLED = 705` - 对等访问未启用错误
- `HGGC_ERROR_PRIMARY_CONTEXT_ACTIVE = 708` - 主上下文仍活跃错误
- `HGGC_ERROR_CONTEXT_IS_DESTROYED = 709` - 上下文已销毁错误
- `HGGC_ERROR_ASSERT = 710` - 断言错误
- `HGGC_ERROR_TOO_MANY_PEERS = 711` - 对等设备过多错误
- `HGGC_ERROR_HOST_MEMORY_ALREADY_REGISTERED = 712` - 主机内存已注册错误
- `HGGC_ERROR_HOST_MEMORY_NOT_REGISTERED = 713` - 主机内存未注册错误
- `HGGC_ERROR_HARDWARE_STACK_ERROR = 714` - 硬件栈错误
- `HGGC_ERROR_ILLEGAL_INSTRUCTION = 715` - 非法指令错误
- `HGGC_ERROR_MISALIGNED_ADDRESS = 716` - 地址未对齐错误
- `HGGC_ERROR_INVALID_ADDRESS_SPACE = 717` - 无效地址空间错误
- `HGGC_ERROR_INVALID_PC = 718` - 无效程序计数器错误
- `HGGC_ERROR_LAUNCH_FAILED = 719` - 启动失败错误
- `HGGC_ERROR_COOPERATIVE_LAUNCH_TOO_LARGE = 720` - 协作启动规模过大错误
- `HGGC_ERROR_TENSOR_MEMORY_LEAK = 721` - 张量内存泄漏错误
- `HGGC_ERROR_NOT_PERMITTED = 800` - 操作不允许错误
- `HGGC_ERROR_NOT_SUPPORTED = 801` - 操作不支持错误
- `HGGC_ERROR_SYSTEM_NOT_READY = 802` - 系统未就绪错误
- `HGGC_ERROR_SYSTEM_DRIVER_MISMATCH = 803` - 系统驱动版本不匹配错误
- `HGGC_ERROR_COMPAT_NOT_SUPPORTED_ON_DEVICE = 804` - 设备不支持兼容模式错误
- `HGGC_ERROR_MPS_CONNECTION_FAILED = 805` - MPS 连接失败错误
- `HGGC_ERROR_MPS_RPC_FAILURE = 806` - MPS RPC 调用失败错误
- `HGGC_ERROR_MPS_SERVER_NOT_READY = 807` - MPS 服务器未就绪错误
- `HGGC_ERROR_MPS_MAX_CLIENTS_REACHED = 808` - MPS 客户端数量已达上限错误
- `HGGC_ERROR_MPS_MAX_CONNECTIONS_REACHED = 809` - MPS 连接数量已达上限错误
- `HGGC_ERROR_MPS_CLIENT_TERMINATED = 810` - MPS 客户端已终止错误
- `HGGC_ERROR_CDP_NOT_SUPPORTED = 811` - 不支持 CDP 错误
- `HGGC_ERROR_CDP_VERSION_MISMATCH = 812` - CDP 版本不匹配错误
- `HGGC_ERROR_STREAM_CAPTURE_UNSUPPORTED = 900` - 流捕获不支持错误
- `HGGC_ERROR_STREAM_CAPTURE_INVALIDATED = 901` - 流捕获已失效错误
- `HGGC_ERROR_STREAM_CAPTURE_MERGE = 902` - 流捕获合并错误
- `HGGC_ERROR_STREAM_CAPTURE_UNMATCHED = 903` - 流捕获不匹配错误
- `HGGC_ERROR_STREAM_CAPTURE_UNJOINED = 904` - 流捕获未汇合错误
- `HGGC_ERROR_STREAM_CAPTURE_ISOLATION = 905` - 流捕获隔离错误
- `HGGC_ERROR_STREAM_CAPTURE_IMPLICIT = 906` - 隐式流捕获错误
- `HGGC_ERROR_CAPTURED_EVENT = 907` - 事件已被捕获错误
- `HGGC_ERROR_STREAM_CAPTURE_WRONG_THREAD = 908` - 流捕获线程错误
- `HGGC_ERROR_TIMEOUT = 909` - 操作超时错误
- `HGGC_ERROR_GRAPH_EXEC_UPDATE_FAILURE = 910` - 计算图执行更新失败错误
- `HGGC_ERROR_EXTERNAL_DEVICE = 911` - 外部设备错误
- `HGGC_ERROR_INVALID_CLUSTER_SIZE = 912` - 无效集群大小错误
- `HGGC_ERROR_FUNCTION_NOT_LOADED = 913` - 函数未加载错误
- `HGGC_ERROR_INVALID_RESOURCE_TYPE = 914` - 无效资源类型错误
- `HGGC_ERROR_INVALID_RESOURCE_CONFIGURATION = 915` - 无效资源配置错误
- `HGGC_ERROR_KEY_ROTATION = 916` - 密钥轮换错误
- `HGGC_ERROR_NOT_IMPLEMENTED = 998` - 功能未实现错误
- `HGGC_ERROR_UNKNOWN = 999` - 未知错误

---

```text
enum HGsharedMemoryMode
```
共享内存模式。

值：

- `HG_SHARED_MEM_CONFIG_DEFAULT_BANK_SIZE = 0` - 默认共享内存 bank 大小
- `HG_SHARED_MEM_CONFIG_4_BANK_CONFLICT = 1` - 4 bank 冲突模式
- `HG_SHARED_MEM_CONFIG_8_BANK_CONFLICT = 2` - 8 bank 冲突模式

---

```text
enum HGshared_carveout
```
共享内存 carveout 配置。

值：

- `HG_SHARED_CARVEOUT_NO_SHARED_L1 = 0` - 无共享 L1
- `HG_SHARED_CARVEOUT_SHARED_L1_PREFER_SHARED = 0x100` - 优先共享 L1
- `HG_SHARED_CARVEOUT_SHARED_L1_PREFER_CACHE = 0x200` - 优先缓存

---

```text
enum HGsharedconfig
```
共享内存配置。

值：

- `HG_SHARED_MEM_CONFIG_DEFAULT_BANK_SIZE = 0` - 默认 bank 大小
- `HG_SHARED_MEM_CONFIG_4_BANK_CONFLICT = 1` - 4 bank 冲突
- `HG_SHARED_MEM_CONFIG_8_BANK_CONFLICT = 2` - 8 bank 冲突

---

```text
enum HGstreamAtomicReductionDataType
```
流原子归约数据类型。

值：

- `HG_STREAM_REDUCTION_COMPUTE_TYPE_FP16 = 0` - FP16 归约类型
- `HG_STREAM_REDUCTION_COMPUTE_TYPE_FP32 = 1` - FP32 归约类型
- `HG_STREAM_REDUCTION_COMPUTE_TYPE_FP64 = 2` - FP64 归约类型
- `HG_STREAM_REDUCTION_COMPUTE_TYPE_INT32 = 3` - INT32 归约类型
- `HG_STREAM_REDUCTION_COMPUTE_TYPE_INT64 = 4` - INT64 归约类型
- `HG_STREAM_REDUCTION_COMPUTE_TYPE_UINT32 = 5` - UINT32 归约类型
- `HG_STREAM_REDUCTION_COMPUTE_TYPE_UINT64 = 6` - UINT64 归约类型

---

```text
enum HGstreamAtomicReductionOpType
```
流原子归约操作类型。

值：

- `HG_STREAM_REDUCTION_COMPUTE_OP_SUM = 0` - 求和归约操作
- `HG_STREAM_REDUCTION_COMPUTE_OP_MIN = 1` - 最小值归约操作
- `HG_STREAM_REDUCTION_COMPUTE_OP_MAX = 2` - 最大值归约操作

---

```text
enum HGstreamBatchMemOpType
```
流批量内存操作类型。

值：

- `HG_STREAM_BATCH_MEM_WRITE_VALUE_FLAG_NONE = 0x0` - 无标志
- `HG_STREAM_BATCH_MEM_WRITE_VALUE_FLAG_INLINE = 0x1` - 内联标志

---

```text
enum HGstreamCaptureMode
```
流捕获模式。

值：

- `HG_STREAM_CAPTURE_MODE_GLOBAL = 0` - 全局流捕获模式
- `HG_STREAM_CAPTURE_MODE_THREADLOCAL = 1` - 线程局部流捕获模式
- `HG_STREAM_CAPTURE_MODE_RELAXED = 2` - 宽松流捕获模式

---

```text
enum HGstreamCaptureStatus
```
流捕获状态。

值：

- `HG_STREAM_CAPTURE_STATUS_NONE = 0` - 无捕获状态
- `HG_STREAM_CAPTURE_STATUS_ACTIVE = 1` - 活动捕获状态
- `HG_STREAM_CAPTURE_STATUS_INVALIDATED = 2` - 已使无效捕获状态

---

```text
enum HGstreamMemoryBarrier_flags
```
流内存屏障标志。

值：

- `HG_STREAM_MEMORY_BARRIER_FLAG_NONE = 0x0` - 无屏障标志

---

```text
enum HGstreamUpdateCaptureDependencies_flags
```
流更新捕获依赖标志。

值：

- `HG_STREAM_UPDATE_CAPTURE_DEPENDENCIES_FLAG_NONE = 0x0` - 无标志
- `HG_STREAM_ADD_CAPTURE_DEPENDENCIES = 0x1` - 添加捕获依赖

---

```text
enum HGstreamWaitValue_flags
```
流等待值标志。

值：

- `HG_STREAM_WAIT_VALUE_FLAG_NONE = 0x0` - 无标志
- `HG_STREAM_WAIT_VALUE_FLAG_EQ = 0x1` - 等于标志
- `HG_STREAM_WAIT_VALUE_FLAG_NEQ = 0x2` - 不等于标志
- `HG_STREAM_WAIT_VALUE_FLAG_GT = 0x3` - 大于标志
- `HG_STREAM_WAIT_VALUE_FLAG_AND = 0x4` - 与标志
- `HG_STREAM_WAIT_VALUE_FLAG_OR = 0x5` - 或标志
- `HG_STREAM_WAIT_VALUE_FLAG_XOR = 0x6` - 异或标志

---

```text
enum HGstreamWriteValue_flags
```
流写值标志。

值：

- `HG_STREAM_WRITE_VALUE_FLAG_NONE = 0x0` - 无标志
- `HG_STREAM_WRITE_VALUE_FLAG_INLINE = 0x1` - 内联标志

---

```text
enum HGstream_flags
```
流创建标志。

值：

- `HG_STREAM_DEFAULT = 0x0` - 默认流标志
- `HG_STREAM_NON_BLOCKING = 0x1` - 非阻塞流标志

---

```text
enum HGtensorMapDataType
```
张量映射数据类型。

值：

- `HG_TENSOR_MAP_DATA_TYPE_UINT8 = 0` - UINT8 数据类型
- `HG_TENSOR_MAP_DATA_TYPE_UINT16 = 1` - UINT16 数据类型
- `HG_TENSOR_MAP_DATA_TYPE_UINT32 = 2` - UINT32 数据类型
- `HG_TENSOR_MAP_DATA_TYPE_INT32 = 3` - INT32 数据类型
- `HG_TENSOR_MAP_DATA_TYPE_UINT64 = 4` - UINT64 数据类型
- `HG_TENSOR_MAP_DATA_TYPE_INT64 = 5` - INT64 数据类型
- `HG_TENSOR_MAP_DATA_TYPE_FP16 = 6` - FP16 数据类型
- `HG_TENSOR_MAP_DATA_TYPE_FP32 = 7` - FP32 数据类型
- `HG_TENSOR_MAP_DATA_TYPE_FP64 = 8` - FP64 数据类型
- `HG_TENSOR_MAP_DATA_TYPE_BF16 = 9` - BF16 数据类型
- `HG_TENSOR_MAP_DATA_TYPE_C16 = 10` - C16 数据类型
- `HG_TENSOR_MAP_DATA_TYPE_T16 = 11` - T16 数据类型
- `HG_TENSOR_MAP_DATA_TYPE_U4 = 12` - U4 数据类型
- `HG_TENSOR_MAP_DATA_TYPE_I4 = 13` - I4 数据类型
- `HG_TENSOR_MAP_DATA_TYPE_U8 = 14` - U8 数据类型
- `HG_TENSOR_MAP_DATA_TYPE_I8 = 15` - I8 数据类型
- `HG_TENSOR_MAP_DATA_TYPE_FP8_E4M3 = 16` - FP8 E4M3 数据类型
- `HG_TENSOR_MAP_DATA_TYPE_FP8_E5M2 = 17` - FP8 E5M2 数据类型
- `HG_TENSOR_MAP_DATA_TYPE_FP8_E4M3_FNUZ = 18` - FP8 E4M3 FNUZ 数据类型
- `HG_TENSOR_MAP_DATA_TYPE_FP8_E5M2_FNUZ = 19` - FP8 E5M2 FNUZ 数据类型
- `HG_TENSOR_MAP_DATA_TYPE_BF16_FTZ = 20` - BF16 FTZ 数据类型

---

```text
enum HGtensorMapFloatOOBfill
```
张量映射浮点越界填充值。

值：

- `HG_TENSOR_MAP_FLOAT_OOB_FILL_DEFAULT = 0` - 默认越界填充

---

```text
enum HGtensorMapIm2ColWideMode
```
张量映射 Im2Col 宽模式。

值：

- `HG_TENSOR_MAP_IM2COL_WIDE_MODE_NONE = 0` - 无宽模式
- `HG_TENSOR_MAP_IM2COL_WIDE_MODE_ENABLED = 1` - 启用宽模式

---

```text
enum HGtensorMapInterleave
```
张量映射交错模式。

值：

- `HG_TENSOR_MAP_INTERLEAVE_NONE = 0` - 无交错
- `HG_TENSOR_MAP_INTERLEAVE_16B = 1` - 16 字节交错
- `HG_TENSOR_MAP_INTERLEAVE_32B = 2` - 32 字节交错
- `HG_TENSOR_MAP_INTERLEAVE_64B = 3` - 64 字节交错

---

```text
enum HGtensorMapL2promotion
```
张量映射 L2 提升模式。

值：

- `HG_TENSOR_MAP_L2_PROMOTION_NONE = 0` - 无 L2 提升
- `HG_TENSOR_MAP_L2_PROMOTION_32B = 1` - 32 字节 L2 提升
- `HG_TENSOR_MAP_L2_PROMOTION_64B = 2` - 64 字节 L2 提升
- `HG_TENSOR_MAP_L2_PROMOTION_128B = 3` - 128 字节 L2 提升

---

```text
enum HGtensorMapSwizzle
```
张量映射 Swizzle 模式。

值：

- `HG_TENSOR_MAP_SWIZZLE_NONE = 0` - 无 Swizzle
- `HG_TENSOR_MAP_SWIZZLE_32B = 1` - 32 字节 Swizzle
- `HG_TENSOR_MAP_SWIZZLE_64B = 2` - 64 字节 Swizzle
- `HG_TENSOR_MAP_SWIZZLE_128B = 3` - 128 字节 Swizzle

---

```text
enum HGuserObjectRetain_flags
```
用户对象保留标志。

值：

- `HG_USER_OBJECT_RETAIN_DEFAULT = 0` - 默认保留标志
- `HG_USER_OBJECT_RETAIN_NO_INITIAL_RETAIN = 1u << 0` - 无初始保留标志

---

```text
enum HGuserObject_flags
```
用户对象标志。

值：

- `HG_USER_OBJECT_FLAGS_NONE = 0` - 无标志
- `HG_USER_OBJECT_FLAGS_NO_DERESERVE_ON_launch = 1u << 0` - 启动时不取消保留标志

---

```text
enum cl_context_flags
```
OpenCL 上下文标志。

值：

- `CL_CONTEXT_SPM_LAUCH_CONCURRENT = 0x01` - SPM 启动并发标志

---

```text
enum cl_event_flags
```
OpenCL 事件标志。

值：

- `CL_EVENT_NO_FLAGS = 0x0` - 无标志

---

### 2.2. 全局控制 {#global-control}

本模块提供 Driver API 的**初始化与终止**接口。在使用任何 Driver API 之前，必须先调用全局控制函数。

本节介绍低级 HGGC 驱动程序应用程序编程接口的全局控制函数。

#### 1. 接口一览 {#接口一览}

| 函数 | 用途 |
|------|------|
| [hgInit](#hginit) | 初始化 HGGC 驱动程序 API。必须在调用驱动程序 API 的任何其他函数之前调用此函数。当前版本中，Flags 参数必须为 0。如果未调用 hgInit()，驱动程序 API 的任何函数都将返回 HGGC_ERROR_NOT_INITIALIZED |

---

#### 2. hgInit {#hginit}

hgInit 预加载了 JIT 编译所需的各种库。如需选择退出此行为，请设置环境变量 HGGC_FORCE_PRELOAD_LIBRARIES=0。HGGC 将按需延迟加载 JIT 库。如需完全禁用 JIT，请设置环境变量 HGGC_DISABLE_JIT=1。

```c
HGresult hgInit (unsigned int Flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| Flags | in | HGGC 的初始化标志 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_DEVICE、HGGC_ERROR_SYSTEM_DRIVER_MISMATCH、HGGC_ERROR_COMPAT_NOT_SUPPORTED_ON_DEVICE

---

### 2.3. 实用工具 {#utilities}

本模块提供**实用工具**接口，包括驱动版本查询、错误码字符串转换和驱动入口点动态获取等通用辅助功能。

#### 1. 接口一览 {#接口一览}

| 函数 | 用途 |
|------|------|
| [hgDriverGetVersion](#hgdrivergetversion) | 返回驱动程序支持的最新 HGGC 版本 |
| [hgGetErrorName](#hggeterrorname) | 获取错误码枚举名称的字符串表示形式 |
| [hgGetErrorString](#hggeterrorstring) | 获取错误码的字符串描述 |
| [hgGetProcAddress](#hggetprocaddress) | 返回请求的驱动程序 API 函数指针 |

---

#### 2. hgDriverGetVersion {#hgdrivergetversion}

在 `*driverVersion` 中返回驱动程序支持的 HGGC 版本。版本表示为 (1000 * major + 10 * minor)。

如果 `driverVersion` 为 NULL，此函数会自动返回 [HGGC_ERROR_INVALID_VALUE](#driver-data-types)。

```c
HGresult hgDriverGetVersion (int* driverVersion)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| driverVersion | out | 返回 HGGC 驱动程序版本 |

错误码：HGGC_ERROR_INVALID_VALUE

---

#### 3. hgGetErrorName {#hggeterrorname}

将 `*pStr` 设置为错误码 `error` 对应的枚举错误码名称的 NULL 终止字符串表示形式的地址。如果错误码未被识别，将返回 [HGGC_ERROR_INVALID_VALUE](#driver-data-types)，并将 `*pStr` 设置为 NULL 地址。

```c
HGresult hgGetErrorName (HGresult error, const char** pStr)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| error | in | 要转换为字符串的错误码 |
| pStr | in | 字符串指针的地址 |

错误码：HGGC_ERROR_INVALID_VALUE

---

#### 4. hgGetErrorString {#hggeterrorstring}

将 `*pStr` 设置为错误码 `error` 对应的错误描述的 NULL 终止字符串的地址。如果错误码未被识别，将返回 [HGGC_ERROR_INVALID_VALUE](#driver-data-types)，并将 `*pStr` 设置为 NULL 地址。

```c
HGresult hgGetErrorString (HGresult error, const char** pStr)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| error | in | 要转换为字符串的错误码 |
| pStr | in | 字符串指针的地址 |

错误码：HGGC_ERROR_INVALID_VALUE

---

#### 5. hgGetProcAddress {#hggetprocaddress}

在 `**pfn` 中返回请求的 HGGC 版本和标志的 HGGC 驱动程序函数的地址。

对于请求的驱动程序符号，如果指定的 HGGC 版本大于或等于引入驱动程序符号的 HGGC 版本，此 API 将返回相应版本化函数的函数指针。如果指定的 HGGC 版本大于驱动程序版本，API 将返回 [HGGC_ERROR_INVALID_VALUE](#driver-data-types)。

API 返回的指针应强制转换为与请求的驱动程序函数在 API 头文件中定义相匹配的函数指针。可以从相应的 typedef 头文件中获取函数指针 typedef。例如，hggcTypedefs.h 包含 hggc.h 中定义的驱动程序 API 的函数指针 typedef。

如果请求的驱动程序函数在平台上不受支持，不存在与指定的 `hggcVersion` ABI 兼容的驱动程序函数，或者驱动程序符号无效，API 将返回 [HGGC_SUCCESS](#driver-data-types) 并将返回的 `pfn` 设置为 NULL。

它还将可选的 `symbolStatus` 设置为以下值之一：

- [HG_GET_PROC_ADDRESS_SUCCESS](#driver-data-types)：请求的符号已成功找到
- [HG_GET_PROC_ADDRESS_SYMBOL_NOT_FOUND](#driver-data-types)：请求的符号未找到
- [HG_GET_PROC_ADDRESS_VERSION_NOT_SUFFICIENT](#driver-data-types)：请求的符号已找到但不受指定的 hggcVersion 支持

请求的标志可以是：

- [HG_GET_PROC_ADDRESS_DEFAULT](#driver-data-types)：这是默认模式。如果代码使用 --default-stream per-thread 编译标志编译或定义了宏 HGGC_API_PER_THREAD_DEFAULT_STREAM，则相当于 [HG_GET_PROC_ADDRESS_PER_THREAD_DEFAULT_STREAM](#driver-data-types)；否则相当于 [HG_GET_PROC_ADDRESS_LEGACY_STREAM](#driver-data-types)。
- [HG_GET_PROC_ADDRESS_LEGACY_STREAM](#driver-data-types)：这将启用对所有与请求的驱动程序符号名称匹配的驱动程序符号的搜索，但不包括相应的每线程版本。
- [HG_GET_PROC_ADDRESS_PER_THREAD_DEFAULT_STREAM](#driver-data-types)：这将启用对所有与请求的驱动程序符号名称匹配的驱动程序符号的搜索，包括每线程版本。如果未找到每线程版本，API 将返回驱动程序函数的旧版本。

```c
HGresult hgGetProcAddress (const char* symbol,
                           void** pfn,
                           int hggcVersion,
                           hguint64_t flags,
                           HGdriverProcAddressQueryResult* symbolStatus)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| symbol | in | 要查找的驱动程序 API 函数的基础名称。例如，对于驱动程序 API hgMemAlloc_v2，`symbol` 将是 hgMemAlloc，`hggcVersion` 将是与 _v2 变体 ABI 兼容的 HGGC 版本。 |
| pfn | out | 返回请求驱动程序函数的函数指针的位置 |
| hggcVersion | in | 查找请求驱动程序符号的 HGGC 版本 |
| flags | in | 指定搜索选项的标志 |
| symbolStatus | in | 可选位置，用于存储基于 `hggcVersion` 的 `symbol` 搜索状态。请参阅 [HGdriverProcAddressQueryResult](#driver-data-types) 了解可能的值。 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_SUPPORTED

---

比赛关联：`hgInit` 默认预加载 JIT 编译所需库，可用 `HGGC_FORCE_PRELOAD_LIBRARIES=0` 改为延迟加载、`HGGC_DISABLE_JIT=1` 完全禁用 JIT——这些是排查与压缩首次推理 TTFT 的直接环境变量手段。

---

## 3. 设备与上下文 {#device-ctx}

本节涵盖设备发现与属性查询、上下文生命周期管理以及对等设备间的直接内存访问。

---

### 3.1. 设备管理 {#device-mgmt}

本模块提供**设备管理**接口，用于枚举可用设备、查询设备属性（计算能力、显存大小等）以及选择目标设备。

本节介绍低级 HGGC 驱动程序应用程序编程接口的设备管理函数。

#### 1. 接口一览 {#接口一览}

| 函数 | 用途 |
|------|------|
| [hgDeviceGet](#hgdeviceget) | 返回计算设备的句柄 |
| [hgDeviceGetAttribute](#hgdevicegetattribute) | 返回设备的信息 |
| [hgDeviceGetCount](#hgdevicegetcount) | 返回具有计算能力的设备数量 |
| [hgDeviceGetDefaultMemPool](#hgdevicegetdefaultmempool) | 返回设备的默认内存池 |
| [hgDeviceGetLuid](#hgdevicegetluid) | 返回设备的 LUID 和设备节点掩码 |
| [hgDeviceGetMemPool](#hgdevicegetmempool) | 获取设备的当前内存池 |
| [hgDeviceGetName](#hgdevicegetname) | 返回设备的标识符字符串 |
| [hgDeviceGetUuid](#hgdevicegetuuid) | 返回设备的 UUID |
| [hgDeviceSetMemPool](#hgdevicesetmempool) | 设置设备的当前内存池 |
| [hgDeviceTotalMem](#hgdevicetotalmem) | 返回设备上的总内存量 |
| [hgDevicePrimaryCtxGetState](#hgdeviceprimaryctxgetstate) | 获取主上下文的状态 |
| [hgDevicePrimaryCtxRelease](#hgdeviceprimaryctxrelease) | 释放 PPU 上的主上下文 |
| [hgDevicePrimaryCtxReset](#hgdeviceprimaryctxreset) | 销毁所有分配并重置主上下文的所有状态 |
| [hgDevicePrimaryCtxRetain](#hgdeviceprimaryctxretain) | 保留 PPU 上的主上下文 |
| [hgDevicePrimaryCtxSetFlags](#hgdeviceprimaryctxsetflags) | 设置主上下文的标志 |

---

#### 2. hgDeviceGet {#hgdeviceget}

根据序号在 `*device` 中返回设备句柄，序号范围为 **[0, [hgDeviceGetCount()](#hgdevicegetcount)-1]**。

```c
HGresult hgDeviceGet (HGdevice* device, int ordinal)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| device | out | 返回的设备句柄 |
| ordinal | in | 要获取句柄的设备编号 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_DEVICE

---

#### 3. hgDeviceGetAttribute {#hgdevicegetattribute}

在设备 `dev` 上将属性 `attrib` 的整数值返回到 `*pi`。

```c
HGresult hgDeviceGetAttribute (int* pi, HGdevice_attribute attrib, HGdevice dev)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pi | out | 返回的设备属性值 |
| attrib | in | 要查询的设备属性 |
| dev | in | 设备句柄 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_DEVICE

---

#### 4. hgDeviceGetCount {#hgdevicegetcount}

在 `*count` 中返回可用于执行的支持计算能力大于或等于 2.0 的设备数量。如果没有此类设备，[hgDeviceGetCount()](#hgdevicegetcount) 返回 0。

```c
HGresult hgDeviceGetCount (int* count)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| count | out | 返回具有计算能力的设备数量 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

---

#### 5. hgDeviceGetDefaultMemPool {#hgdevicegetdefaultmempool}

设备的默认内存池包含来自该设备的设备内存。

```c
HGresult hgDeviceGetDefaultMemPool (HGmemoryPool* pool_out, HGdevice dev)
```

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_DEVICE、HGGC_ERROR_NOT_SUPPORTED

---

#### 6. hgDeviceGetLuid {#hgdevicegetluid}

返回用于匹配图形 API 的标识信息（`luid` 和 `deviceNodeMask`）。

```c
HGresult hgDeviceGetLuid (char* luid,
                          unsigned int* deviceNodeMask,
                          HGdevice dev)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| luid | out | 返回的 LUID |
| deviceNodeMask | out | 返回的设备节点掩码 |
| dev | in | 要获取标识符字符串的设备 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_DEVICE

---

#### 7. hgDeviceGetMemPool {#hgdevicegetmempool}

返回上次为该设备提供的 [hgDeviceSetMemPool](#hgdevicesetmempool)，或者如果从未调用过 [hgDeviceSetMemPool](#hgdevicesetmempool)，则返回设备的默认内存池。默认情况下，当前内存池是设备的默认内存池。否则，返回的池必须已通过 [hgDeviceSetMemPool](#hgdevicesetmempool) 设置。

```c
HGresult hgDeviceGetMemPool (HGmemoryPool* pool, HGdevice dev)
```

错误码：HGGC_ERROR_INVALID_VALUE

---

#### 8. hgDeviceGetName {#hgdevicegetname}

在 `name` 指向的 NULL 终止字符串中返回标识设备 `dev` 的 ASCII 字符串。`len` 指定可返回的字符串最大长度。如果 `len` 小于设备名称，则 `name` 被截断到指定长度 `len`。

```c
HGresult hgDeviceGetName (char* name, int len, HGdevice dev)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| name | out | 返回的设备标识符字符串 |
| len | in | 存储在 `name` 中的字符串最大长度 |
| dev | in | 要获取标识符字符串的设备 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_DEVICE

---

#### 9. hgDeviceGetUuid {#hgdevicegetuuid}

在 `uuid` 指向的结构中返回标识设备 `dev` 的 16 字节 UUID。如果设备处于 MIG 模式，返回其 MIG UUID，该 UUID 唯一标识订阅的 MIG 计算实例。

```c
HGresult hgDeviceGetUuid (HGuuid* uuid, HGdevice dev)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| uuid | out | 返回的 UUID |
| dev | in | 要获取标识符字符串的设备 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_DEVICE

---

#### 10. hgDeviceSetMemPool {#hgdevicesetmempool}

内存池必须本地属于指定设备。[hgMemAllocAsync](#hgmemallocasync) 从提供的流设备的当前内存池分配。默认情况下，设备的当前内存池是其默认内存池。

```c
HGresult hgDeviceSetMemPool (HGdevice dev, HGmemoryPool pool)
```

错误码：HGGC_ERROR_INVALID_VALUE

---

#### 11. hgDeviceTotalMem {#hgdevicetotalmem}

在 `*bytes` 中以字节为单位返回设备 `dev` 可用的总内存量。

```c
HGresult hgDeviceTotalMem (size_t* bytes, HGdevice dev)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| bytes | out | 返回设备上可用的内存量（字节） |
| dev | in | 设备句柄 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_DEVICE

---

#### 12. hgDevicePrimaryCtxGetState {#hgdeviceprimaryctxgetstate}

在 `*flags` 中返回设备 `dev` 的主上下文的标志，在 `*active` 中返回它是否处于激活状态。有关标志值，请参阅 [hgDevicePrimaryCtxSetFlags](#hgdeviceprimaryctxsetflags)。

```c
HGresult hgDevicePrimaryCtxGetState (HGdevice dev,
                                     unsigned int* flags,
                                     int* active)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dev | in | 获取主上下文标志的设备 |
| flags | in | 存储标志的指针 |
| active | in | 存储上下文状态的指针；0 = 未激活，1 = 已激活 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_DEVICE、HGGC_ERROR_INVALID_VALUE

---

#### 13. hgDevicePrimaryCtxRelease {#hgdeviceprimaryctxrelease}

释放设备上的主上下文互操作。一旦开发者使用完保留的上下文，应始终将其释放。最后一个对它的引用被释放后，上下文会自动重置。在这种情况下，主上下文始终保持激活状态。

释放之前未被保留的主上下文将失败并返回 [HGGC_ERROR_INVALID_CONTEXT](#driver-data-types)。

请注意，与 [hgCtxDestroy()](#hgctxdestroy) 不同，此方法在任何情况下都不会将上下文从堆栈中弹出。

```c
HGresult hgDevicePrimaryCtxRelease (HGdevice dev)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dev | in | 释放主上下文的设备 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_DEVICE、HGGC_ERROR_INVALID_CONTEXT

---

#### 14. hgDevicePrimaryCtxReset {#hgdeviceprimaryctxreset}

显式销毁并清理当前进程中当前设备的所有资源。

请注意，调用函数有责任确保进程中没有任何其他模块再使用该设备。因此，在大多数情况下应使用 [hgDevicePrimaryCtxRelease()](#hgdeviceprimaryctxrelease)。但是，即使在重置设备后，其他模块也可以安全地调用 [hgDevicePrimaryCtxRelease()](#hgdeviceprimaryctxrelease)。重置主上下文不会释放它，已保留主上下文的应用程序应明确释放其使用。

```c
HGresult hgDevicePrimaryCtxReset (HGdevice dev)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dev | in | 销毁主上下文的设备 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_DEVICE、HGGC_ERROR_PRIMARY_CONTEXT_ACTIVE

---

#### 15. hgDevicePrimaryCtxRetain {#hgdeviceprimaryctxretain}

保留设备上的主上下文。一旦开发者成功保留主上下文，主上下文将保持激活状态并可供开发者使用，直到开发者通过 [hgDevicePrimaryCtxRelease()](#hgdeviceprimaryctxrelease) 将其释放或通过 [hgDevicePrimaryCtxReset()](#hgdeviceprimaryctxreset) 将其重置。与 [hgCtxCreate()](#hgctxcreate) 不同，新保留的上下文不会被推送到堆栈上。

第一次保留主上下文时，如果设备的计算模式为 [HG_COMPUTEMODE_PROHIBITED](#driver-data-types)，将失败并返回 [HGGC_ERROR_UNKNOWN](#driver-data-types)。可以使用 [hgDeviceGetAttribute()](#hgdevicegetattribute) 与 [HG_DEVICE_ATTRIBUTE_COMPUTE_MODE](#driver-data-types) 一起确定设备的计算模式。可以使用 ppu-smi 工具设置设备的计算模式。可以通过传递 -h 选项获取 ppu-smi 的文档。

请注意，主上下文始终支持固定分配。可以通过 [hgDevicePrimaryCtxSetFlags()](#hgdeviceprimaryctxsetflags) 指定其他标志。

```c
HGresult hgDevicePrimaryCtxRetain (HGcontext* pctx, HGdevice dev)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pctx | out | 返回的新上下文句柄 |
| dev | in | 请求主上下文的设备 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_DEVICE、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_OUT_OF_MEMORY、HGGC_ERROR_UNKNOWN

---

#### 16. hgDevicePrimaryCtxSetFlags {#hgdeviceprimaryctxsetflags}

设置设备上的主上下文标志，覆盖之前设置的标志。

`flags` 参数的低三位可用于控制拥有 HGGC 上下文的 OS 线程在等待 PPU 结果时如何与 OS 调度器交互。创建上下文时只能设置一个调度标志。

- [HG_CTX_SCHED_SPIN](#driver-data-types)：指示 HGGC 在等待 PPU 结果时主动自旋。这可以减少等待时的延迟，但如果 CPU 线程与 HGGC 线程并行执行工作，可能会降低 CPU 线程的性能。

- [HG_CTX_SCHED_YIELD](#driver-data-types)：指示 HGGC 在等待 PPU 结果时让出线程。这可以增加等待时的延迟，但可以提高与 PPU 并行执行工作的 CPU 线程的性能。

- [HG_CTX_SCHED_BLOCKING_SYNC](#driver-data-types)：指示 HGGC 在等待 PPU 完成工作时在同步原语上阻塞 CPU 线程。

- [HG_CTX_SCHED_AUTO](#driver-data-types)：如果 `flags` 参数为零，则为默认值，使用基于进程中活跃 HGGC 上下文数量 C 和系统逻辑处理器数量 P 的启发式方法。如果 C > P，则 HGGC 在等待 PPU 时会让出其他 OS 线程（[HG_CTX_SCHED_YIELD](#driver-data-types)），否则 HGGC 在等待结果时不会让出，而是主动在处理器上自旋（[HG_CTX_SCHED_SPIN](#driver-data-types)）。

- [HG_CTX_LMEM_RESIZE_TO_MAX](#driver-data-types)：指示 HGGC 在调整核函数本地内存后不要减少本地内存。这可以防止在启动具有高本地内存使用的多个核函数时本地内存分配出现抖动，代价是可能增加内存使用。
  **已弃用：** 此标志已被弃用，此标志启用的行为现在是默认行为，无法禁用。

- [HG_CTX_COREDUMP_ENABLE](#driver-data-types)：如果 PPU 核心转储未通过 hgCoredumpSetAttributeGlobal 或环境变量全局启用，则可以在上下文创建期间设置此标志，以指示 HGGC 在此上下文执行期间引发异常时创建核心转储。初始设置将取自上下文创建时的全局设置。控制核心转储输出的其他设置可以通过在上下文变为当前上下文后从创建的上下文调用 hgCoredumpSetAttribute 来修改。

- [HG_CTX_USER_COREDUMP_ENABLE](#driver-data-types)：如果用户触发的 PPU 核心转储未通过 hgCoredumpSetAttributeGlobal 或环境变量全局启用，则可以在上下文创建期间设置此标志，以指示 HGGC 在向 OS 空间中存在的某个管道写入数据时创建核心转储。设置此标志意味着设置了 [HG_CTX_COREDUMP_ENABLE](#driver-data-types)。初始设置将取自上下文创建时的全局设置。控制核心转储输出的其他设置可以通过在上下文变为当前上下文后从创建的上下文调用 hgCoredumpSetAttribute 来修改。

- [HG_CTX_SYNC_MEMOPS](#driver-data-types)：确保在此上下文上发起的同步内存操作始终同步。有关同步内存操作可能表现出异步行为的更多信息，请参阅"API 同步行为"部分。

```c
HGresult hgDevicePrimaryCtxSetFlags (HGdevice dev, unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dev | in | 设置主上下文标志的设备 |
| flags | in | 设备的新标志 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_DEVICE、HGGC_ERROR_INVALID_VALUE

---

### 3.2. 上下文管理 {#ctx-mgmt}

本模块提供**上下文（Context）管理**接口。上下文是 Driver API 中所有设备资源的持有者；必须先创建/绑定上下文，才能分配内存或启动核函数。

本节介绍低级 HGGC 驱动程序应用程序编程接口的上下文管理函数。

请注意，某些函数在[主上下文管理](#device-mgmt)部分中描述。

#### 1. 接口一览 {#接口一览}

| 函数 | 用途 |
|------|------|
| [hgCtxCreate](#hgctxcreate) | 创建 HGGC 上下文 |
| [hgCtxCreate_v2](#hgctxcreate_v2) | 创建 HGGC 上下文（老版本的 API，推荐使用上面不带后缀的版本） |
| [hgCtxDestroy](#hgctxdestroy) | 销毁 HGGC 上下文 |
| [hgCtxGetApiVersion](#hgctxgetapiversion) | 获取上下文的 API 版本 |
| [hgCtxGetCacheConfig](#hgctxgetcacheconfig) | 返回当前上下文的首选缓存配置 |
| [hgCtxGetCurrent](#hgctxgetcurrent) | 返回绑定到调用 CPU 线程的 HGGC 上下文 |
| [hgCtxGetDevice](#hgctxgetdevice) | 返回当前上下文的设备句柄 |
| [hgCtxGetFlags](#hgctxgetflags) | 返回当前上下文的标志 |
| [hgCtxGetId](#hgctxgetid) | 返回与提供的上下文关联的唯一 ID |
| [hgCtxGetLimit](#hgctxgetlimit) | 返回资源限制 |
| [hgCtxGetStreamPriorityRange](#hgctxgetstreampriorityrange) | 返回对应于最小和最大流优先级的数值 |
| [hgCtxPopCurrent](#hgctxpopcurrent) | 从当前 CPU 线程弹出当前 HGGC 上下文 |
| [hgCtxPushCurrent](#hgctxpushcurrent) | 将上下文推入当前 CPU 线程 |
| [hgCtxResetPersistingL2Cache](#hgctxresetpersistingl2cache) | 将所有持久化缓存行重置为正常状态 |
| [hgCtxSetCacheConfig](#hgctxsetcacheconfig) | 设置当前上下文的首选缓存配置 |
| [hgCtxSetCurrent](#hgctxsetcurrent) | 将指定的 HGGC 上下文绑定到调用 CPU 线程 |
| [hgCtxSetFlags](#hgctxsetflags) | 设置当前上下文的标志 |
| [hgCtxSetLimit](#hgctxsetlimit) | 设置资源限制 |
| [hgCtxSynchronize](#hgctxsynchronize) | 阻塞等待当前上下文的任务完成 |

---

#### 2. hgCtxCreate {#hgctxcreate}

创建一个新的 HGGC 上下文并将其与调用线程关联。`flags` 参数说明如下。上下文的使用计数为 1，调用 [hgCtxCreate()](#hgctxcreate) 的一方必须在使用完上下文后调用 [hgCtxDestroy()](#hgctxdestroy)。如果线程中已存在一个当前上下文，则新创建的上下文将取代它，随后可以通过调用 [hgCtxPopCurrent()](#hgctxpopcurrent) 恢复。

可以通过将 `ctxCreateParams` 设置为 NULL 来创建常规 HGGC 上下文。

可以使用执行亲和性创建 HGGC 上下文。上下文可以使用的执行资源类型和数量由 `execAffinity` 中的 `paramsArray` 和 `numExecAffinityParams` 限制。`paramsArray` 是 `HGexecAffinityParam` 的数组，`numExecAffinityParams` 描述 paramsArray 的大小。如果数组中两个 `HGexecAffinityParam` 具有相同的类型，则后者的执行亲和性参数将覆盖前者的执行亲和性参数。当前支持的执行亲和性类型为：

- [HG_EXEC_AFFINITY_TYPE_SM_COUNT](#driver-data-types)：限制上下文可以使用的 SM 比例。SM 比例通过 `HGexecAffinitySmCount` 指定为 SM 数量。此限制将向上舍入到下一个硬件支持的数值。因此，必须在上下文创建后查询上下文的实际执行亲和性。

可以通过设置 `cigParams` 以 CIG（HGGC in Graphics）模式创建 HGGC 上下文。图形客户端的数据通过 `cigParams` 中的 `sharedData` 与 HGGC 共享。`execAffinityParams` 和 `cigParams` 是互斥的，不能同时为非 NULL。将两者都设置为非 NULL 值将导致未定义行为。如果 `execAffinityParams` 和 `cigParams` 都为 NULL，则将创建常规 HGGC 上下文。

`flags` 参数的低三位可用于控制拥有 HGGC 上下文的 OS 线程在等待 PPU 结果时如何与 OS 调度器交互。创建上下文时只能设置一个调度标志。

- [HG_CTX_SCHED_SPIN](#driver-data-types)：指示 HGGC 在等待 PPU 结果时主动自旋。这可以减少等待时的延迟，但如果 CPU 线程与 HGGC 线程并行执行工作，可能会降低 CPU 线程的性能。

- [HG_CTX_SCHED_YIELD](#driver-data-types)：指示 HGGC 在等待 PPU 结果时让出线程。这可以增加等待时的延迟，但可以提高与 PPU 并行执行工作的 CPU 线程的性能。

- [HG_CTX_SCHED_BLOCKING_SYNC](#driver-data-types)：指示 HGGC 在等待 PPU 完成工作时在同步原语上阻塞 CPU 线程。

- [HG_CTX_SCHED_AUTO](#driver-data-types)：如果 `flags` 参数为零，则为默认值，使用基于进程中活跃 HGGC 上下文数量 C 和系统逻辑处理器数量 P 的启发式方法。如果 C > P，则 HGGC 在等待 PPU 时会让出其他 OS 线程（[HG_CTX_SCHED_YIELD](#driver-data-types)），否则 HGGC 在等待结果时不会让出，而是主动在处理器上自旋（[HG_CTX_SCHED_SPIN](#driver-data-types)）。

- [HG_CTX_MAP_HOST](#driver-data-types)：指示 HGGC 支持映射固定分配。必须设置此标志才能分配可被 PPU 访问的固定主机内存。

- [HG_CTX_SYNC_MEMOPS](#driver-data-types)：确保在此上下文上发起的同步内存操作始终同步。

如果设备的计算模式为 [HG_COMPUTEMODE_PROHIBITED](#driver-data-types)，上下文创建将失败并返回 [HGGC_ERROR_UNKNOWN](#driver-data-types)。可以使用 [hgDeviceGetAttribute()](#hgdevicegetattribute) 与 [HG_DEVICE_ATTRIBUTE_COMPUTE_MODE](#driver-data-types) 一起确定设备的计算模式。

如果客户端传递了无效参数来创建 HGGC 上下文，则上下文创建将失败并返回 [HGGC_ERROR_INVALID_VALUE](#driver-data-types)。

如果设备或驱动程序不支持 CIG，则 CIG 模式下的上下文创建将失败并返回 [HGGC_ERROR_NOT_SUPPORTED](#driver-data-types)。

```c
HGresult hgCtxCreate (HGcontext* pctx,
                      HGctxCreateParams* ctxCreateParams,
                      unsigned int flags,
                      HGdevice dev)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pctx | out | 返回的新上下文句柄 |
| ctxCreateParams | in | 上下文创建参数。如果为 NULL，则创建常规 HGGC 上下文。详见 HGctxCreateParams。 |
| flags | in | 上下文创建标志 |
| dev | in | 创建上下文的设备 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_DEVICE、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_SUPPORTED、HGGC_ERROR_OUT_OF_MEMORY、HGGC_ERROR_UNKNOWN

---

#### 3. hgCtxCreate_v2 {#hgctxcreate_v2}

创建一个新的 HGGC 上下文并将其与调用线程关联。`flags` 参数说明如下。上下文的使用计数为 1，调用 [hgCtxCreate_v2()](#hgctxcreate_v2) 的一方必须在使用完上下文后调用 [hgCtxDestroy()](#hgctxdestroy)。如果线程中已存在一个当前上下文，则新创建的上下文将取代它，随后可以通过调用 [hgCtxPopCurrent()](#hgctxpopcurrent) 恢复。

`flags` 参数的低三位可用于控制拥有 HGGC 上下文的 OS 线程在等待 PPU 结果时如何与 OS 调度器交互。创建上下文时只能设置一个调度标志。

- [HG_CTX_SCHED_SPIN](#driver-data-types)：指示 HGGC 在等待 PPU 结果时主动自旋。这可以减少等待时的延迟，但如果 CPU 线程与 HGGC 线程并行执行工作，可能会降低 CPU 线程的性能。

- [HG_CTX_SCHED_YIELD](#driver-data-types)：指示 HGGC 在等待 PPU 结果时让出线程。这可以增加等待时的延迟，但可以提高与 PPU 并行执行工作的 CPU 线程的性能。

- [HG_CTX_SCHED_BLOCKING_SYNC](#driver-data-types)：指示 HGGC 在等待 PPU 完成工作时在同步原语上阻塞 CPU 线程。

- [HG_CTX_BLOCKING_SYNC](#driver-data-types)：指示 HGGC 在等待 PPU 完成工作时在同步原语上阻塞 CPU 线程。

- [HG_CTX_SCHED_AUTO](#driver-data-types)：如果 `flags` 参数为零，则为默认值，使用基于进程中活跃 HGGC 上下文数量 C 和系统逻辑处理器数量 P 的启发式方法。如果 C > P，则 HGGC 在等待 PPU 时会让出其他 OS 线程（[HG_CTX_SCHED_YIELD](#driver-data-types)），否则 HGGC 在等待结果时不会让出，而是主动在处理器上自旋（[HG_CTX_SCHED_SPIN](#driver-data-types)）。此外，在 Tegra 设备上，[HG_CTX_SCHED_AUTO](#driver-data-types) 使用基于平台功耗配置的启发式方法，可能会为低功耗设备选择 [HG_CTX_SCHED_BLOCKING_SYNC](#driver-data-types)。

- [HG_CTX_MAP_HOST](#driver-data-types)：指示 HGGC 支持映射固定分配。必须设置此标志才能分配可被 PPU 访问的固定主机内存。

- [HG_CTX_SYNC_MEMOPS](#driver-data-types)：确保在此上下文上发起的同步内存操作始终同步。有关同步内存操作可能表现出异步行为的情况的更多信息，请参阅“API 同步行为”部分。

如果设备的计算模式为 [HG_COMPUTEMODE_PROHIBITED](#driver-data-types)，上下文创建将失败并返回 [HGGC_ERROR_UNKNOWN](#driver-data-types)。可以使用 [hgDeviceGetAttribute()](#hgdevicegetattribute) 与 [HG_DEVICE_ATTRIBUTE_COMPUTE_MODE](#driver-data-types) 一起确定设备的计算模式。

```c
HGresult hgCtxCreate_v2 (HGcontext* pctx,
                      unsigned int flags,
                      HGdevice dev)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pctx | out | 返回的新上下文句柄 |
| flags | in | 上下文创建标志 |
| dev | in | 创建上下文的设备 |

错误码：HGGC_ERROR_SUCCESS、HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_DEVICE、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_OUT_OF_MEMORY、HGGC_ERROR_UNKNOWN

---

#### 4. hgCtxDestroy {#hgctxdestroy}

销毁由 `ctx` 指定的 HGGC 上下文。无论 `ctx` 是当前到多少个线程，都会被销毁。调用函数有责任确保在执行 [hgCtxDestroy()](#hgctxdestroy) 时没有 API 调用使用 `ctx`。

销毁并清理与上下文关联的所有资源。调用者有责任确保上下文或其资源不会在后续 API 调用中被访问或传递，否则将导致未定义行为。这些资源包括 HGGC 类型 [HGmodule](#driver-data-types)、[HGfunction](#driver-data-types)、[HGstream](#driver-data-types)、[HGevent](#driver-data-types)、[HGarray](#driver-data-types)、[HGmipmappedArray](#driver-data-types)、[HGtexObject](#driver-data-types)、[HGsurfObject](#driver-data-types)、[HGtexref](#driver-data-types)、[HGsurfref](#driver-data-types)、[HGgraphicsResource](#driver-data-types)、HGlinkState、[HGexternalMemory](#driver-data-types) 和 [HGexternalSemaphore](#driver-data-types)。这些资源还包括通过 [hgMemAlloc()](#hgmemalloc)、[hgMemAllocHost()](#hgmemallochost)、[hgMemAllocManaged()](#hgmemallocmanaged) 和 [hgMemAllocPitch()](#hgmemallocpitch) 的内存分配。

如果 `ctx` 当前绑定到调用线程，则 `ctx` 也将从当前线程的上下文堆栈中弹出（就像调用了 [hgCtxPopCurrent()](#hgctxpopcurrent) 一样）。如果 `ctx` 当前绑定到其他线程，则 `ctx` 将保持对这些线程的绑定，从这些线程访问 `ctx` 将导致错误 [HGGC_ERROR_CONTEXT_IS_DESTROYED](#driver-data-types)。

```c
HGresult hgCtxDestroy (HGcontext ctx)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| ctx | in | 要销毁的上下文 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

---

#### 5. hgCtxGetApiVersion {#hgctxgetapiversion}

在 `version` 中返回与上下文功能对应的版本号（例如 3010 或 3020），库开发者可以使用它来引导调用者到特定 API 版本。如果 `ctx` 为 NULL，则返回用于创建当前绑定上下文的 API 版本。

请注意，新 API 版本仅在上下文功能改变以破坏二进制兼容性时才会引入，因此 API 版本和驱动程序版本可能不同。例如，API 版本为 3020 而驱动程序版本为 4020 是有效的。

```c
HGresult hgCtxGetApiVersion (HGcontext ctx, unsigned int* version)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| ctx | in | 要检查的上下文 |
| version | out | 返回版本号的指针 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_UNKNOWN

---

#### 6. hgCtxGetCacheConfig {#hgctxgetcacheconfig}

在 L1 缓存和共享内存使用相同硬件资源的设备上，此函数通过 `pconfig` 返回当前上下文的首选缓存配置。这只是一个偏好。如果可能，驱动程序将使用请求的配置，但可以根据需要自由选择不同的配置来执行函数。

在 L1 缓存和共享内存大小固定的设备上，这将返回 [HG_FUNC_CACHE_PREFER_NONE](#driver-data-types)。

支持的缓存配置：

- [HG_FUNC_CACHE_PREFER_NONE](#driver-data-types)：对共享内存或 L1 无偏好（默认）
- [HG_FUNC_CACHE_PREFER_SHARED](#driver-data-types)：偏好更大的共享内存和更小的 L1 缓存
- [HG_FUNC_CACHE_PREFER_L1](#driver-data-types)：偏好更大的 L1 缓存和更小的共享内存
- [HG_FUNC_CACHE_PREFER_EQUAL](#driver-data-types)：偏好相同大小的 L1 缓存和共享内存

```c
HGresult hgCtxGetCacheConfig (HGfunc_cache* pconfig)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pconfig | out | 返回的缓存配置 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

---

#### 7. hgCtxGetCurrent {#hgctxgetcurrent}

在 `*pctx` 中返回绑定到调用 CPU 线程的 HGGC 上下文。如果没有上下文绑定到调用 CPU 线程，则 `*pctx` 设置为 NULL 并返回 [HGGC_SUCCESS](#driver-data-types)。

```c
HGresult hgCtxGetCurrent (HGcontext* pctx)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pctx | out | 返回的上下文句柄 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED

---

#### 8. hgCtxGetDevice {#hgctxgetdevice}

在 `*device` 中返回当前上下文设备的句柄。

```c
HGresult hgCtxGetDevice (HGdevice* device)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| device | out | 返回当前上下文的设备句柄 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

---

#### 9. hgCtxGetFlags {#hgctxgetflags}

在 `*flags` 中返回当前上下文的标志。请参阅 [hgCtxCreate](#hgctxcreate) 获取标志值。

```c
HGresult hgCtxGetFlags (unsigned int* flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| flags | in | 存储当前上下文标志的指针 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

---

#### 10. hgCtxGetId {#hgctxgetid}

在 `ctxId` 中返回与给定上下文关联的唯一 ID。该 ID 对于此 HGGC 实例的程序生命周期是唯一的。如果提供的上下文为 NULL 且有一个当前上下文，则返回当前上下文的 ID。

```c
HGresult hgCtxGetId (HGcontext ctx, unsigned long long* ctxId)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| ctx | in | 要获取 ID 的上下文 |
| ctxId | in | 存储上下文 ID 的指针 |

错误码：HGGC_ERROR_CONTEXT_IS_DESTROYED、HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

---

#### 11. hgCtxGetLimit {#hgctxgetlimit}

在 `*pvalue` 中返回 `limit` 的当前大小。支持的 [HGlimit](#driver-data-types) 值为：

- [HG_LIMIT_STACK_SIZE](#driver-data-types)：每个 PPU 线程的堆栈大小（字节）。
- [HG_LIMIT_PRINTF_FIFO_SIZE](#driver-data-types)：printf() 设备系统调用使用的 FIFO 大小（字节）。
- [HG_LIMIT_MALLOC_HEAP_SIZE](#driver-data-types)：malloc() 和 free() 设备系统调用使用的堆大小（字节）。
- [HG_LIMIT_DEV_RUNTIME_SYNC_DEPTH](#driver-data-types)：线程可以发出设备运行时调用 [hggcDeviceSynchronize()](04_runtime_api.md#hggcdevicesynchronize) 以等待子网格启动完成的 maximum grid depth。
- [HG_LIMIT_DEV_RUNTIME_PENDING_LAUNCH_COUNT](#driver-data-types)：可以从此上下文进行的最大未完成设备运行时启动数量。
- [HG_LIMIT_MAX_L2_FETCH_GRANULARITY](#driver-data-types)：L2 缓存获取粒度。
- [HG_LIMIT_PERSISTING_L2_CACHE_SIZE](#driver-data-types)：持久化 L2 缓存大小（字节）。

```c
HGresult hgCtxGetLimit (size_t* pvalue, HGlimit limit)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pvalue | out | 返回的限制大小 |
| limit | in | 要查询的限制 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_UNSUPPORTED_LIMIT

---

#### 12. hgCtxGetStreamPriorityRange {#hgctxgetstreampriorityrange}

在 `*leastPriority` 和 `*greatestPriority` 中分别返回对应于最小和最大流优先级的数值。流优先级遵循约定，较低的数值意味着较高的优先级。有意义的流优先级范围由 [\*greatestPriority, \*leastPriority] 给出。如果用户尝试创建超出此 API 指定的有意义范围的优先级值，则优先级会自动向下或向上分别 clamp 到 `*leastPriority` 或 `*greatestPriority`。有关创建优先级流的详细信息，请参阅 [hgStreamCreateWithPriority](#hgstreamcreatewithpriority)。如果不需要某个值，可以为 `*leastPriority` 或 `*greatestPriority` 传递 NULL。

如果当前上下文设备不支持流优先级（请参阅 [hgDeviceGetAttribute](#hgdevicegetattribute)），此函数将在 `*leastPriority` 和 `*greatestPriority` 中返回 '0'。

```c
HGresult hgCtxGetStreamPriorityRange (int* leastPriority, int* greatestPriority)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| leastPriority | in | 存储最小流优先级数值的指针 |
| greatestPriority | in | 存储最大流优先级数值的指针 |

错误码：HGGC_ERROR_INVALID_VALUE

---

#### 13. hgCtxPopCurrent {#hgctxpopcurrent}

从 CPU 线程弹出当前 HGGC 上下文，并在 `*pctx` 中传回旧的上下文句柄。该上下文随后可以通过调用 [hgCtxPushCurrent()](#hgctxpushcurrent) 成为不同 CPU 线程的当前上下文。

```c
HGresult hgCtxPopCurrent (HGcontext* pctx)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pctx | out | 返回弹出的上下文句柄 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT

---

#### 14. hgCtxPushCurrent {#hgctxpushcurrent}

将上下文 `ctx` 推入当前 CPU 线程的上下文堆栈，使 `ctx` 成为当前上下文。这会将任何先前当前上下文推入堆栈。

```c
HGresult hgCtxPushCurrent (HGcontext ctx)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| ctx | in | 要推入的上下文 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_OUT_OF_MEMORY

---

#### 15. hgCtxResetPersistingL2Cache {#hgctxresetpersistingl2cache}

将 L2 缓存中所有持久化缓存行重置为正常（可驱逐）状态。

```c
HGresult hgCtxResetPersistingL2Cache (void)
```

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

---

#### 16. hgCtxSetCacheConfig {#hgctxsetcacheconfig}

在 L1 缓存和共享内存使用相同硬件资源的设备上，此函数设置当前上下文的首选缓存配置。这只是一个偏好。如果可能，驱动程序将使用请求的配置，但可以根据需要自由选择不同的配置来执行函数。

支持的缓存配置：

- [HG_FUNC_CACHE_PREFER_NONE](#driver-data-types)：对共享内存或 L1 无偏好（默认）
- [HG_FUNC_CACHE_PREFER_SHARED](#driver-data-types)：偏好更大的共享内存和更小的 L1 缓存
- [HG_FUNC_CACHE_PREFER_L1](#driver-data-types)：偏好更大的 L1 缓存和更小的共享内存
- [HG_FUNC_CACHE_PREFER_EQUAL](#driver-data-types)：偏好相同大小的 L1 缓存和共享内存

```c
HGresult hgCtxSetCacheConfig (HGfunc_cache config)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| config | in | 新的缓存配置 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

---

#### 17. hgCtxSetCurrent {#hgctxsetcurrent}

将上下文 `ctx` 绑定到调用 CPU 线程。如果调用线程已经有一个当前上下文，则替换它。

```c
HGresult hgCtxSetCurrent (HGcontext ctx)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| ctx | in | 要绑定到调用线程的上下文 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED

---

#### 18. hgCtxSetFlags {#hgctxsetflags}

设置当前上下文的标志。请参阅 [hgCtxCreate](#hgctxcreate) 获取标志说明。

```c
HGresult hgCtxSetFlags (unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| flags | in | 上下文标志 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

---

#### 19. hgCtxSetLimit {#hgctxsetlimit}

设置 `limit` 为 `value`。支持的 [HGlimit](#driver-data-types) 值与 [hgCtxGetLimit](#hgctxgetlimit) 中记录的值相同。

```c
HGresult hgCtxSetLimit (HGlimit limit, size_t value)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| limit | in | 要设置的限制 |
| value | in | 新值 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_UNSUPPORTED_LIMIT

---

#### 20. hgCtxSynchronize {#hgctxsynchronize}

阻塞等待当前上下文的所有任务完成。

```c
HGresult hgCtxSynchronize (void)
```

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT

---

### 3.3. 对等上下文内存访问 {#p2p}

本模块提供**对等上下文内存访问（P2P）** 接口，允许一个 PPU 直接读写另一个 PPU 的设备内存。

本节介绍低级 HGGC 驱动程序应用程序编程接口的直接对等上下文内存访问函数。

#### 1. 接口一览 {#接口一览}

| 函数 | 用途 |
|------|------|
| [hgCtxDisablePeerAccess](#hgctxdisablepeeraccess) | 禁用对对等上下文内存分配的直接访问，并取消注册任何已注册的分配 |
| [hgCtxEnablePeerAccess](#hgctxenablepeeraccess) | 启用对对等上下文内存分配的直接访问 |
| [hgDeviceCanAccessPeer](#hgdevicecanaccesspeer) | 查询设备是否可以直接访问对等设备的内存 |
| [hgDeviceGetP2PAttribute](#hgdevicegetp2pattribute) | 查询两个设备之间链路的属性 |

---

#### 2. hgCtxDisablePeerAccess {#hgctxdisablepeeraccess}

如果尚未从 `peerContext` 启用到当前上下文的直接对等访问，则返回 [HGGC_ERROR_PEER_ACCESS_NOT_ENABLED](#driver-data-types)。

如果没有当前上下文，或者 `peerContext` 不是有效上下文，则返回 [HGGC_ERROR_INVALID_CONTEXT](#driver-data-types)。

```c
HGresult hgCtxDisablePeerAccess (HGcontext peerContext)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| peerContext | in | 要禁用直接访问的对等上下文 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_PEER_ACCESS_NOT_ENABLED、HGGC_ERROR_INVALID_CONTEXT

---

#### 3. hgCtxEnablePeerAccess {#hgctxenablepeeraccess}

如果当前上下文和 `peerContext` 都在支持统一寻址的设备上（可以使用 [HG_DEVICE_ATTRIBUTE_UNIFIED_ADDRESSING](#driver-data-types) 查询），并且主计算能力相同，则成功时，`peerContext` 中的所有分配将立即可被当前上下文访问。有关其他详细信息，请参阅"统一寻址"。

请注意，通过此调用授予的访问是单向的，为了从当前上下文访问 `peerContext` 中的内存，需要对 [hgCtxEnablePeerAccess()](#hgctxenablepeeraccess) 进行单独的对称调用。

请注意，根据系统配置，对等访问每个系统配置都有设备和系统范围的限制，如 HGGC 编程指南中"对等内存访问"部分所述。

如果 [hgDeviceCanAccessPeer()](#hgdevicecanaccesspeer) 指示当前上下文的 [HGdevice](#driver-data-types) 无法直接访问 `peerContext` 的 [HGdevice](#driver-data-types) 的内存，则返回 [HGGC_ERROR_PEER_ACCESS_UNSUPPORTED](#driver-data-types)。

如果已从当前上下文启用 `peerContext` 的直接访问，则返回 [HGGC_ERROR_PEER_ACCESS_ALREADY_ENABLED](#driver-data-types)。

如果由于对等访问所需的硬件资源已耗尽而无法进行直接对等访问，则返回 [HGGC_ERROR_TOO_MANY_PEERS](#driver-data-types)。

如果没有当前上下文，`peerContext` 不是有效上下文，或者当前上下文是 `peerContext`，则返回 [HGGC_ERROR_INVALID_CONTEXT](#driver-data-types)。

如果 `Flags` 不为 0，则返回 [HGGC_ERROR_INVALID_VALUE](#driver-data-types)。

```c
HGresult hgCtxEnablePeerAccess (HGcontext peerContext, unsigned int Flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| peerContext | in | 要从当前上下文启用直接访问的对等上下文 |
| Flags | in | 预留供将来使用，必须设置为 0 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_PEER_ACCESS_ALREADY_ENABLED、HGGC_ERROR_TOO_MANY_PEERS、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_PEER_ACCESS_UNSUPPORTED、HGGC_ERROR_INVALID_VALUE

---

#### 4. hgDeviceCanAccessPeer {#hgdevicecanaccesspeer}

如果 `dev` 上的上下文能够直接访问 `peerDev` 上上下文的内存，则在 `*canAccessPeer` 中返回 1，否则返回 0。如果可以建立从 `dev` 到 `peerDev` 的直接访问，则可以通过调用 [hgCtxEnablePeerAccess()](#hgctxenablepeeraccess) 在两个特定上下文上启用访问。

```c
HGresult hgDeviceCanAccessPeer (int* canAccessPeer,
                                HGdevice dev,
                                HGdevice peerDev)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| canAccessPeer | out | 返回的访问能力 |
| dev | in | 将直接访问 `peerDev` 上分配的设备 |
| peerDev | in | 分配所在设备，将由 `dev` 直接访问 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_DEVICE

---

#### 5. hgDeviceGetP2PAttribute {#hgdevicegetp2pattribute}

在 `*value` 中返回 `srcDevice` 和 `dstDevice` 之间链路请求属性 `attrib` 的值。支持的属性包括：

- [HG_DEVICE_P2P_ATTRIBUTE_PERFORMANCE_RANK](#driver-data-types)：一个相对值，指示两个设备之间链路的性能。
- [HG_DEVICE_P2P_ATTRIBUTE_ACCESS_SUPPORTED](#driver-data-types)：如果启用了 P2P 访问，则为 1。
- [HG_DEVICE_P2P_ATTRIBUTE_NATIVE_ATOMIC_SUPPORTED](#driver-data-types)：如果链路上的所有 HGGC 有效原子操作都受支持，则为 1。
- [HG_DEVICE_P2P_ATTRIBUTE_HGGC_ARRAY_ACCESS_SUPPORTED](#driver-data-types)：如果可以通过链路访问 hggcArray，则为 1。
- [HG_DEVICE_P2P_ATTRIBUTE_ONLY_PARTIAL_NATIVE_ATOMIC_SUPPORTED](#driver-data-types)：如果链路上的某些 HGGC 有效原子操作受支持，则为 1。可以使用相应接口检索有关特定操作的信息。

如果 `srcDevice` 或 `dstDevice` 无效或代表同一设备，则返回 [HGGC_ERROR_INVALID_DEVICE](#driver-data-types)。

如果 `attrib` 无效或 `value` 为空指针，则返回 [HGGC_ERROR_INVALID_VALUE](#driver-data-types)。

```c
HGresult hgDeviceGetP2PAttribute (int* value,
                                  HGdevice_P2PAttribute attrib,
                                  HGdevice srcDevice,
                                  HGdevice dstDevice)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| value | out | 返回的请求属性值 |
| attrib | in | `srcDevice` 和 `dstDevice` 之间链路的请求属性 |
| srcDevice | in | 目标链路的源设备 |
| dstDevice | in | 目标链路的目标设备 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_DEVICE、HGGC_ERROR_INVALID_VALUE

---

## 4. 模块与代码加载 {#module}

本节涵盖 PPU 可执行代码的加载、链接与符号查询。

---

### 4.1. 模块管理 {#module-mgmt}

本模块提供**模块（Module）管理**接口，用于加载/卸载 hgbin 二进制模块并从中提取函数、全局变量等符号。

本节介绍低级 HGGC 驱动程序应用程序编程接口的模块管理函数。

#### 1. 枚举 {#枚举}

<a id="hgmoduleloadingmode"></a>

enum [HGmoduleLoadingMode](#hgmoduleloadingmode)

---

#### 2. 接口一览 {#接口一览}

| 函数 | 用途 |
|------|------|
| [hgLinkAddData](#hglinkadddata) | 向待处理的链接器调用添加输入 |
| [hgLinkAddFile](#hglinkaddfile) | 向待处理的链接器调用添加文件输入 |
| [hgLinkComplete](#hglinkcomplete) | 完成待处理的链接器调用 |
| [hgLinkCreate](#hglinkcreate) | 创建待处理的 JIT 链接器调用 |
| [hgLinkDestroy](#hglinkdestroy) | 销毁 JIT 链接器调用的状态 |
| [hgModuleGetFunction](#hgmodulegetfunction) | 在 `*hfunc` 中返回位于模块 `hmod` 中名为 `name… |
| [hgModuleGetGlobal](#hgmodulegetglobal) | 从模块返回全局指针 |
| [hgModuleGetLoadingMode](#hgmodulegetloadingmode) | 查询延迟加载模式 |
| [hgModuleLoad](#hgmoduleload) | 加载计算模块 |
| [hgModuleLoadData](#hgmoduleloaddata) | 接受指针 `image`，并将对应模块 `module` 加载到当前上… |
| [hgModuleLoadDataEx](#hgmoduleloaddataex) | 使用选项加载模块的数据 |
| [hgModuleLoadFatBinary](#hgmoduleloadfatbinary) | 接受指针 `fatHgbin`，并将对应模块 `module` 加载到… |
| [hgModuleUnload](#hgmoduleunload) | 卸载模块 |
| [hgKernelGetAttribute](#hgkernelgetattribute) | 返回核函数的信息 |
| [hgKernelGetFunction](#hgkernelgetfunction) | 在 `pFunc` 中返回请求的核函数 `kernel` 和当前上下文的… |
| [hgKernelGetName](#hgkernelgetname) | 返回核函数句柄的函数名称 |
| [hgKernelSetAttribute](#hgkernelsetattribute) | 设置核函数的信息 |
| [hgKernelSetCacheConfig](#hgkernelsetcacheconfig) | 设置设备核函数的首选缓存配置 |
| [hgLibraryEnumerateKernels](#hglibraryenumeratekernels) | 检索库中的核函数句柄 |
| [hgLibraryGetGlobal](#hglibrarygetglobal) | 返回全局设备指针 |
| [hgLibraryGetKernel](#hglibrarygetkernel) | 返回核函数句柄 |
| [hgLibraryGetKernelCount](#hglibrarygetkernelcount) | 返回库中核函数的数量 |
| [hgLibraryGetManaged](#hglibrarygetmanaged) | 返回托管内存的指针 |
| [hgLibraryGetModule](#hglibrarygetmodule) | 返回模块句柄 |
| [hgLibraryLoadData](#hglibraryloaddata) | 使用指定代码和选项加载库 |
| [hgLibraryLoadFromFile](#hglibraryloadfromfile) | 使用指定文件和选项加载库 |
| [hgLibraryUnload](#hglibraryunload) | 卸载库 |

---

#### 3. hgLinkAddData {#hglinkadddata}

调用者保留 `data` 的所有权。此调用返回后，不会对任何输入保留引用。

此方法仅接受编译器选项，不接受以下任何选项：[HG_JIT_WALL_TIME](#driver-data-types)、[HG_JIT_INFO_LOG_BUFFER](#driver-data-types)、[HG_JIT_ERROR_LOG_BUFFER](#driver-data-types)、[HG_JIT_TARGET_FROM_HGCONTEXT](#driver-data-types) 或 [HG_JIT_TARGET](#driver-data-types)。

```c
HGresult hgLinkAddData (HGlinkState state,
                        HGjitInputType type,
                        void* data,
                        size_t size,
                        const char* name,
                        unsigned int numOptions,
                        HGjit_option* options,
                        void** optionValues)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| state | in | 待处理的链接器操作 |
| type | in | 输入数据的类型 |
| data | in | 输入数据 |
| size | in | 输入数据的长度 |
| name | in | 在日志消息中此输入的可选名称 |
| numOptions | in | 选项的大小 |
| options | in | 仅应用于此输入的选项（覆盖 [hgLinkCreate()](#hglinkcreate) 中的选项） |
| optionValues | in | 选项值数组，每个值转换为 void* |

错误码：HGGC_ERROR_INVALID_HANDLE、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_IMAGE、HGGC_ERROR_OUT_OF_MEMORY、HGGC_ERROR_NO_BINARY_FOR_GPU

---

#### 4. hgLinkAddFile {#hglinkaddfile}

此调用返回后，不会对任何输入保留引用。

此方法仅接受编译器选项，不接受以下任何选项：[HG_JIT_WALL_TIME](#driver-data-types)、[HG_JIT_INFO_LOG_BUFFER](#driver-data-types)、[HG_JIT_ERROR_LOG_BUFFER](#driver-data-types)、[HG_JIT_TARGET_FROM_HGCONTEXT](#driver-data-types) 或 [HG_JIT_TARGET](#driver-data-types)。

此方法等同于对文件内容调用 [hgLinkAddData()](#hglinkadddata)。

```c
HGresult hgLinkAddFile (HGlinkState state,
                        HGjitInputType type,
                        const char* path,
                        unsigned int numOptions,
                        HGjit_option* options,
                        void** optionValues)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| state | in | 待处理的链接器操作 |
| type | in | 输入数据的类型 |
| path | in | 输入文件的路径 |
| numOptions | in | 选项的大小 |
| options | in | 仅应用于此输入的选项（覆盖 [hgLinkCreate()](#hglinkcreate) 中的选项） |
| optionValues | in | 选项值数组，每个值转换为 void* |

错误码：HGGC_ERROR_FILE_NOT_FOUND、HGGC_ERROR_INVALID_HANDLE、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_IMAGE、HGGC_ERROR_OUT_OF_MEMORY、HGGC_ERROR_NO_BINARY_FOR_GPU

---

#### 5. hgLinkComplete {#hglinkcomplete}

完成待处理的链接器操作，并返回链接设备代码的 hgbin 镜像，可与 [hgModuleLoadData()](#hgmoduleloaddata) 一起使用。hgbin 由 `state` 拥有，因此应在通过 [hgLinkDestroy()](#hglinkdestroy) 销毁 `state` 之前加载。此调用不会销毁 `state`。

```c
HGresult hgLinkComplete (HGlinkState state, void** hgbinOut, size_t* sizeOut)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| state | in | 待处理的链接器调用 |
| hgbinOut | out | 成功时，指向输出镜像 |
| sizeOut | out | 可选参数，接收生成镜像的大小 |

错误码：HGGC_ERROR_INVALID_HANDLE、HGGC_ERROR_OUT_OF_MEMORY

---

#### 6. hgLinkCreate {#hglinkcreate}

如果调用成功，调用者拥有返回的 HGlinkState，最终应使用 [hgLinkDestroy()](#hglinkdestroy) 将其销毁。设备代码机器大小（32 或 64 位）将与调用应用程序匹配。

链接器和编译器选项都可以指定。选项 [HG_JIT_WALL_TIME](#driver-data-types)、[HG_JIT_INFO_LOG_BUFFER_SIZE_BYTES](#driver-data-types) 和 [HG_JIT_ERROR_LOG_BUFFER_SIZE_BYTES](#driver-data-types) 将累积数据，直到 HGlinkState 被销毁。

通过 [hgLinkAddData()](#hglinkadddata) 和 [hgLinkAddFile()](#hglinkaddfile) 传入的数据在 [hgLinkComplete()](#hglinkcomplete) 期间链接最终 hgbin 时将被视为可重定位的，并将产生与离线可重定位设备代码链接类似的后果。

如果使用输出选项，则 `optionValues` 在 HGlinkState 的生命周期内必须保持有效。此调用返回后，不会保留对输入的其他引用。

```c
HGresult hgLinkCreate (unsigned int numOptions,
                       HGjit_option* options,
                       void** optionValues,
                       HGlinkState* stateOut)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| numOptions | in | 选项数组的大小 |
| options | in | 链接器和编译器选项数组 |
| optionValues | in | 选项值数组，每个值转换为 void* |
| stateOut | out | 成功时，包含 HGlinkState，用于指定和完成此操作 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_OUT_OF_MEMORY、HGGC_ERROR_JIT_COMPILER_NOT_FOUND

---

#### 7. hgLinkDestroy {#hglinkdestroy}

销毁 JIT 链接器调用的状态。

```c
HGresult hgLinkDestroy (HGlinkState state)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| state | in | 链接器调用的状态对象 |

错误码：HGGC_ERROR_INVALID_HANDLE

---

#### 8. hgModuleGetFunction {#hgmodulegetfunction}

在 `*hfunc` 中返回位于模块 `hmod` 中名为 `name` 的函数的句柄。如果不存在该名称的函数，[hgModuleGetFunction()](#hgmodulegetfunction) 返回 [HGGC_ERROR_NOT_FOUND](#driver-data-types)。

```c
HGresult hgModuleGetFunction (HGfunction* hfunc,
                              HGmodule hmod,
                              const char* name)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hfunc | out | 返回的函数句柄 |
| hmod | in | 要从中检索函数的模块 |
| name | in | 要检索的函数的名称 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_FOUND

---

#### 9. hgModuleGetGlobal {#hgmodulegetglobal}

在 `*dptr` 和 `*bytes` 中返回位于模块 `hmod` 中名为 `name` 的全局变量的基指针和大小。如果不存在该名称的全局变量，[hgModuleGetGlobal()](#hgmodulegetglobal) 返回 [HGGC_ERROR_NOT_FOUND](#driver-data-types)。`dptr` 或 `bytes`（不能同时为 NULL）之一可以为 NULL，在这种情况下它将忽略。

```c
HGresult hgModuleGetGlobal (HGdeviceptr* dptr,
                            size_t* bytes,
                            HGmodule hmod,
                            const char* name)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dptr | out | 返回的全局设备指针 |
| bytes | out | 返回的全局大小（字节） |
| hmod | in | 要从中检索全局变量的模块 |
| name | in | 要检索的全局变量的名称 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_FOUND

---

#### 10. hgModuleGetLoadingMode {#hgmodulegetloadingmode}

返回延迟加载模式。模块加载模式由 HGGC_MODULE_LOADING 环境变量控制。

```c
HGresult hgModuleGetLoadingMode (HGmoduleLoadingMode* mode)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| mode | out | 返回延迟加载模式 |

错误码：HGGC_ERROR_INVALID_VALUE

---

#### 11. hgModuleLoad {#hgmoduleload}

接受文件名 `fname`，并将该对应模块 `module` 加载到当前上下文。HGGC 驱动程序 API 不会尝试延迟分配模块所需资源；如果无法分配模块所需函数和数据（常量和全局）的内存，[hgModuleLoad()](#hgmoduleload) 将失败。该文件应该是 hgcc 输出的 hgbin 文件，或更高版本工具链输出的 fatbin 文件，或 Tile IR 文件。

```c
HGresult hgModuleLoad (HGmodule* module, const char* fname)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| module | out | 返回的模块 |
| fname | in | 要加载的模块的文件名 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_FOUND、HGGC_ERROR_OUT_OF_MEMORY、HGGC_ERROR_FILE_NOT_FOUND、HGGC_ERROR_NO_BINARY_FOR_GPU、HGGC_ERROR_SHARED_OBJECT_SYMBOL_NOT_FOUND、HGGC_ERROR_SHARED_OBJECT_INIT_FAILED、HGGC_ERROR_JIT_COMPILER_NOT_FOUND

---

#### 12. hgModuleLoadData {#hgmoduleloaddata}

接受指针 `image`，并将对应模块 `module` 加载到当前上下文。`image` 可以是 hgcc 输出的 hgbin 或 fatbin。

```c
HGresult hgModuleLoadData (HGmodule* module, const void* image)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| module | out | 返回的模块 |
| image | in | 要加载的模块数据 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_OUT_OF_MEMORY、HGGC_ERROR_NO_BINARY_FOR_GPU、HGGC_ERROR_SHARED_OBJECT_SYMBOL_NOT_FOUND、HGGC_ERROR_SHARED_OBJECT_INIT_FAILED、HGGC_ERROR_JIT_COMPILER_NOT_FOUND

---

#### 13. hgModuleLoadDataEx {#hgmoduleloaddataex}

接受指针 `image`，并将对应模块 `module` 加载到当前上下文。`image` 可以是 hgcc 输出的 hgbin 或 fatbin。

```c
HGresult hgModuleLoadDataEx (HGmodule* module,
                             const void* image,
                             unsigned int numOptions,
                             HGjit_option* options,
                             void** optionValues)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| module | out | 返回的模块 |
| image | in | 要加载的模块数据 |
| numOptions | in | 选项数量 |
| options | in | JIT 选项 |
| optionValues | in | JIT 选项值 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_OUT_OF_MEMORY、HGGC_ERROR_NO_BINARY_FOR_GPU、HGGC_ERROR_SHARED_OBJECT_SYMBOL_NOT_FOUND、HGGC_ERROR_SHARED_OBJECT_INIT_FAILED、HGGC_ERROR_JIT_COMPILER_NOT_FOUND

---

#### 14. hgModuleLoadFatBinary {#hgmoduleloadfatbinary}

接受指针 `fatHgbin`，并将对应模块 `module` 加载到当前上下文。该指针表示一个 fat binary 对象，它是不同 hgbin 文件的集合，所有这些文件都表示相同的设备代码，但针对不同架构进行了编译和优化。

```c
HGresult hgModuleLoadFatBinary (HGmodule* module, const void* fatHgbin)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| module | out | 返回的模块 |
| fatHgbin | in | 要加载的 fat binary |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_OUT_OF_MEMORY、HGGC_ERROR_NO_BINARY_FOR_GPU、HGGC_ERROR_SHARED_OBJECT_SYMBOL_NOT_FOUND、HGGC_ERROR_SHARED_OBJECT_INIT_FAILED、HGGC_ERROR_JIT_COMPILER_NOT_FOUND

---

#### 15. hgModuleUnload {#hgmoduleunload}

从当前上下文卸载模块 `hmod`。尝试卸载从库管理 API（如 [hgLibraryGetModule](#hglibrarygetmodule)）获取的模块将返回 [HGGC_ERROR_NOT_PERMITTED](#driver-data-types)。

```c
HGresult hgModuleUnload (HGmodule hmod)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hmod | in | 要卸载的模块 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_PERMITTED

---

#### 16. hgKernelGetAttribute {#hgkernelgetattribute}

在 `*pi` 中返回请求设备 `dev` 上核函数 `kernel` 的属性 `attrib` 的整数值。支持的属性包括：

- [HG_FUNC_ATTRIBUTE_MAX_THREADS_PER_BLOCK](#driver-data-types)：每个块的最大线程数，超过该数量核函数启动将失败。此数量取决于核函数和请求的设备。
- [HG_FUNC_ATTRIBUTE_SHARED_SIZE_BYTES](#driver-data-types)：此核函数每个块所需的静态分配共享内存大小（字节）。这不包括用户在运行时动态分配的共享内存。
- [HG_FUNC_ATTRIBUTE_CONST_SIZE_BYTES](#driver-data-types)：此核函数所需的用户分配常量内存大小（字节）。
- [HG_FUNC_ATTRIBUTE_LOCAL_SIZE_BYTES](#driver-data-types)：此核函数每个线程使用的局部内存大小（字节）。
- [HG_FUNC_ATTRIBUTE_NUM_REGS](#driver-data-types)：此核函数每个线程使用的寄存器数量
- [HG_FUNC_ATTRIBUTE_BINARY_VERSION](#driver-data-types)：核函数编译的二进制架构版本。此值是主二进制版本 * 10 + 次二进制版本，因此二进制版本 1.3 的函数将返回值 13。请注意，对于没有正确编码的二进制架构版本的旧版 hgbin，将返回值 10。
- `HG_FUNC_CACHE_MODE_CA`：指示核函数是否已使用用户指定的选项 "--llvm-options -ppu-dlcm=0" 编译的属性。
- [HG_FUNC_ATTRIBUTE_MAX_DYNAMIC_SHARED_SIZE_BYTES](#driver-data-types)：动态分配共享内存的最大大小（字节）。
- [HG_FUNC_ATTRIBUTE_PREFERRED_SHARED_MEMORY_CARVEOUT](#driver-data-types)：首选共享内存-L1 缓存分割比率（占共享内存总量的百分比）。
- [HG_FUNC_ATTRIBUTE_CLUSTER_SIZE_MUST_BE_SET](#driver-data-types)：如果设置此属性，核函数必须使用有效的集群大小启动。
- [HG_FUNC_ATTRIBUTE_REQUIRED_CLUSTER_WIDTH](#driver-data-types)：所需的集群宽度（块）。
- [HG_FUNC_ATTRIBUTE_REQUIRED_CLUSTER_HEIGHT](#driver-data-types)：所需的集群高度（块）。
- [HG_FUNC_ATTRIBUTE_REQUIRED_CLUSTER_DEPTH](#driver-data-types)：所需的集群深度（块）。
- [HG_FUNC_ATTRIBUTE_NON_PORTABLE_CLUSTER_SIZE_ALLOWED](#driver-data-types)：指示函数是否可以使用非可移植集群大小启动。1 表示允许，0 表示不允许。非可移植集群大小只能在程序测试过的特定 SKU 上运行。如果程序在不同硬件平台上运行，启动可能会失败。HGGC API 提供相应接口来帮助检查当前设备是否可以启动所需大小。可移植集群大小保证在所有高于目标计算能力的计算能力上功能正常。此值可能会在未来计算能力中增加。特定硬件单元可能支持更高的集群大小，但不能保证可移植。
- [HG_FUNC_ATTRIBUTE_CLUSTER_SCHEDULING_POLICY_PREFERENCE](#driver-data-types)：函数的块调度策略。值类型为 HGclusterSchedulingPolicy。

```c
HGresult hgKernelGetAttribute (int* pi,
                               HGfunction_attribute attrib,
                               HGkernel kernel,
                               HGdevice dev)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pi | out | 返回的属性值 |
| attrib | in | 请求的属性 |
| kernel | in | 要查询属性的核函数 |
| dev | in | 要查询属性的设备 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_HANDLE、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_DEVICE

---

#### 17. hgKernelGetFunction {#hgkernelgetfunction}

在 `pFunc` 中返回请求的核函数 `kernel` 和当前上下文的函数句柄。如果找不到函数句柄，调用将返回 [HGGC_ERROR_NOT_FOUND](#driver-data-types)。

```c
HGresult hgKernelGetFunction (HGfunction* pFunc, HGkernel kernel)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pFunc | out | 返回的函数句柄 |
| kernel | in | 要检索函数的核函数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_HANDLE、HGGC_ERROR_NOT_FOUND、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_CONTEXT_IS_DESTROYED

---

#### 18. hgKernelGetName {#hgkernelgetname}

在 `**name` 中返回与核函数句柄 `hfunc` 关联的函数名称。函数名称以 NULL 终止字符串形式返回。仅当核函数句柄有效时返回的名称才有效。

```c
HGresult hgKernelGetName (const char** name, HGkernel hfunc)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| name | out | 返回的函数名称 |
| hfunc | in | 要检索名称的函数句柄 |

错误码：HGGC_ERROR_INVALID_VALUE

---

#### 19. hgKernelSetAttribute {#hgkernelsetattribute}

此调用将请求设备 `dev` 上核函数 `kernel` 的指定属性 `attrib` 的值设置为整数 `val`。如果可以成功设置属性的新值，此函数返回 HGGC_SUCCESS。如果设置失败，此调用将返回错误。并非所有属性都可以设置值。尝试设置只读属性的值将导致错误（HGGC_ERROR_INVALID_VALUE）。

请注意，使用 [hgFuncSetAttribute()](#hgfuncsetattribute) 设置的属性将覆盖此 API 设置的属性，无论 [hgFuncSetAttribute()](#hgfuncsetattribute) 的调用是在此 API 调用之前还是之后。但是，[hgKernelGetAttribute()](#hgkernelgetattribute) 将始终返回此 API 设置的属性值。

支持的属性包括：

- [HG_FUNC_ATTRIBUTE_MAX_DYNAMIC_SHARED_SIZE_BYTES](#driver-data-types)：这是动态分配共享内存的最大大小（字节）。此值应包含请求的动态分配共享内存的最大大小。此值与函数属性 [HG_FUNC_ATTRIBUTE_SHARED_SIZE_BYTES](#driver-data-types) 的和不能超过设备属性 [HG_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK_OPTIN](#driver-data-types)。可请求的动态共享内存最大大小可能因 PPU 架构而异。
- [HG_FUNC_ATTRIBUTE_PREFERRED_SHARED_MEMORY_CARVEOUT](#driver-data-types)：在 L1 缓存和共享内存使用相同硬件资源的设备上，这会设置共享内存 carveout 偏好（占共享内存总量的百分比）。请参阅 [HG_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_MULTIPROCESSOR](#driver-data-types)。这只是一个提示，如果需要执行函数，驱动程序可以选择不同的比率。
- [HG_FUNC_ATTRIBUTE_REQUIRED_CLUSTER_WIDTH](#driver-data-types)：所需的集群宽度（块）。宽度、高度和深度值必须全为 0 或全为正。集群维度的有效性在启动时检查。如果该值在编译时设置，则不能在运行时设置。在运行时设置将返回 HGGC_ERROR_NOT_PERMITTED。
- [HG_FUNC_ATTRIBUTE_REQUIRED_CLUSTER_HEIGHT](#driver-data-types)：所需的集群高度（块）。宽度、高度和深度值必须全为 0 或全为正。集群维度的有效性在启动时检查。如果该值在编译时设置，则不能在运行时设置。在运行时设置将返回 HGGC_ERROR_NOT_PERMITTED。
- [HG_FUNC_ATTRIBUTE_REQUIRED_CLUSTER_DEPTH](#driver-data-types)：所需的集群深度（块）。宽度、高度和深度值必须全为 0 或全为正。集群维度的有效性在启动时检查。如果该值在编译时设置，则不能在运行时设置。在运行时设置将返回 HGGC_ERROR_NOT_PERMITTED。
- [HG_FUNC_ATTRIBUTE_NON_PORTABLE_CLUSTER_SIZE_ALLOWED](#driver-data-types)：指示函数是否可以使用非可移植集群大小启动。1 表示允许，0 表示不允许。
- [HG_FUNC_ATTRIBUTE_CLUSTER_SCHEDULING_POLICY_PREFERENCE](#driver-data-types)：函数的块调度策略。值类型为 HGclusterSchedulingPolicy。

```c
HGresult hgKernelSetAttribute (HGfunction_attribute attrib,
                               int val,
                               HGkernel kernel,
                               HGdevice dev)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| attrib | in | 请求的属性 |
| val | in | 要设置的值 |
| kernel | in | 要设置属性的核函数 |
| dev | in | 要设置属性的设备 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_HANDLE、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_DEVICE、HGGC_ERROR_OUT_OF_MEMORY

---

#### 20. hgKernelSetCacheConfig {#hgkernelsetcacheconfig}

在 L1 缓存和共享内存使用相同硬件资源的设备上，此函数通过 `config` 设置请求设备 `dev` 上设备核函数 `kernel` 的首选缓存配置。这只是一个偏好。

支持的缓存配置：

- [HG_FUNC_CACHE_PREFER_NONE](#driver-data-types)：对共享内存或 L1 无偏好（默认）
- [HG_FUNC_CACHE_PREFER_SHARED](#driver-data-types)：偏好更大的共享内存和更小的 L1 缓存
- [HG_FUNC_CACHE_PREFER_L1](#driver-data-types)：偏好更大的 L1 缓存和更小的共享内存
- [HG_FUNC_CACHE_PREFER_EQUAL](#driver-data-types)：偏好相同大小的 L1 缓存和共享内存

```c
HGresult hgKernelSetCacheConfig (HGkernel kernel,
                                 HGfunc_cache config,
                                 HGdevice dev)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| kernel | in | 要配置缓存的核函数 |
| config | in | 请求的缓存配置 |
| dev | in | 要设置属性的设备 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_HANDLE、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_DEVICE、HGGC_ERROR_OUT_OF_MEMORY

---

#### 21. hgLibraryEnumerateKernels {#hglibraryenumeratekernels}

在 `kernels` 中返回 `lib` 中最多 `numKernels` 个核函数句柄。返回的核函数句柄在库卸载时将失效。

```c
HGresult hgLibraryEnumerateKernels (HGkernel* kernels,
                                    unsigned int numKernels,
                                    HGlibrary lib)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| kernels | out | 返回核函数句柄的缓冲区 |
| numKernels | out | 可返回的最大核函数句柄数量 |
| lib | in | 要查询的库 |

错误码：HGGC_ERROR_INVALID_HANDLE、HGGC_ERROR_INVALID_VALUE

---

#### 22. hgLibraryGetGlobal {#hglibrarygetglobal}

在 `*dptr` 和 `*bytes` 中返回请求的库 `library` 和当前上下文中名为 `name` 的全局变量的基指针和大小。如果不存在该名称的全局变量，[hgLibraryGetGlobal()](#hglibrarygetglobal) 返回 [HGGC_ERROR_NOT_FOUND](#driver-data-types)。`dptr` 或 `bytes`（不能同时为 NULL）之一可以为 NULL，在这种情况下它将忽略。

```c
HGresult hgLibraryGetGlobal (HGdeviceptr* dptr,
                             size_t* bytes,
                             HGlibrary library,
                             const char* name)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dptr | out | 返回的全局设备指针 |
| bytes | out | 返回的全局大小（字节） |
| library | in | 要从中检索全局变量的库 |
| name | in | 要检索的全局变量的名称 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_HANDLE、HGGC_ERROR_NOT_FOUND、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_CONTEXT_IS_DESTROYED

---

#### 23. hgLibraryGetKernel {#hglibrarygetkernel}

在 `pKernel` 中返回库 `library` 中名为 `name` 的核函数的句柄。如果找不到核函数句柄，调用将返回 [HGGC_ERROR_NOT_FOUND](#driver-data-types)。

```c
HGresult hgLibraryGetKernel (HGkernel* pKernel,
                             HGlibrary library,
                             const char* name)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pKernel | out | 返回的核函数句柄 |
| library | in | 要从中检索核函数的库 |
| name | in | 要检索的核函数的名称 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_HANDLE、HGGC_ERROR_NOT_FOUND

---

#### 24. hgLibraryGetKernelCount {#hglibrarygetkernelcount}

在 `count` 中返回 `lib` 中核函数的数量。

```c
HGresult hgLibraryGetKernelCount (unsigned int* count, HGlibrary lib)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| count | in | 在库中找到的核函数数量 |
| lib | in | 要查询的库 |

错误码：HGGC_ERROR_INVALID_HANDLE、HGGC_ERROR_INVALID_VALUE

---

#### 25. hgLibraryGetManaged {#hglibrarygetmanaged}

在 `*dptr` 和 `*bytes` 中返回请求的库 `library` 中名为 `name` 的托管内存的基指针和大小。如果不存在该名称的托管内存，调用将返回 [HGGC_ERROR_NOT_FOUND](#driver-data-types)。`dptr` 或 `bytes`（不能同时为 NULL）之一可以为 NULL，在这种情况下它将忽略。

```c
HGresult hgLibraryGetManaged (HGdeviceptr* dptr,
                              size_t* bytes,
                              HGlibrary library,
                              const char* name)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dptr | out | 返回的托管内存指针 |
| bytes | out | 返回的内存大小（字节） |
| library | in | 要从中检索托管内存的库 |
| name | in | 要检索的托管内存的名称 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_HANDLE、HGGC_ERROR_NOT_FOUND

---

#### 26. hgLibraryGetModule {#hglibrarygetmodule}

在 `pMod` 中返回与当前上下文关联的库 `library` 中的模块句柄。如果找不到模块句柄，调用将返回 [HGGC_ERROR_NOT_FOUND](#driver-data-types)。

```c
HGresult hgLibraryGetModule (HGmodule* pMod, HGlibrary library)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pMod | out | 返回的模块句柄 |
| library | in | 要从中检索模块的库 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_HANDLE、HGGC_ERROR_NOT_FOUND、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_CONTEXT_IS_DESTROYED

---

#### 27. hgLibraryLoadData {#hglibraryloaddata}

使用指定代码 `code` 和选项加载库。成功加载后，在 `library` 中返回库句柄。

```c
HGresult hgLibraryLoadData (HGlibrary* library,
                            const void* code,
                            HGjit_option* jitOptions,
                            void** jitOptionsValues,
                            unsigned int numJitOptions,
                            HGlibraryOption* libraryOptions,
                            void** libraryOptionValues,
                            unsigned int numLibraryOptions)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| library | out | 返回的库 |
| code | in | 要加载的代码 |
| jitOptions | in | JIT 选项 |
| jitOptionsValues | in | JIT 选项值 |
| numJitOptions | in | 选项数量 |
| libraryOptions | in | 库选项 |
| libraryOptionValues | in | 库选项值 |
| numLibraryOptions | in | 库选项数量 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_OUT_OF_MEMORY、HGGC_ERROR_NOT_FOUND、HGGC_ERROR_JIT_COMPILER_NOT_FOUND

---

#### 28. hgLibraryLoadFromFile {#hglibraryloadfromfile}

使用指定文件 `fileName` 和选项加载库。成功加载后，在 `library` 中返回库句柄。

```c
HGresult hgLibraryLoadFromFile (HGlibrary* library,
                                const char* fileName,
                                HGjit_option* jitOptions,
                                void** jitOptionsValues,
                                unsigned int numJitOptions,
                                HGlibraryOption* libraryOptions,
                                void** libraryOptionValues,
                                unsigned int numLibraryOptions)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| library | out | 返回的库 |
| fileName | in | 要加载的文件名 |
| jitOptions | in | JIT 选项 |
| jitOptionsValues | in | JIT 选项值 |
| numJitOptions | in | 选项数量 |
| libraryOptions | in | 库选项 |
| libraryOptionValues | in | 库选项值 |
| numLibraryOptions | in | 库选项数量 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_FILE_NOT_FOUND、HGGC_ERROR_OUT_OF_MEMORY、HGGC_ERROR_NOT_FOUND、HGGC_ERROR_JIT_COMPILER_NOT_FOUND

---

#### 29. hgLibraryUnload {#hglibraryunload}

卸载库 `library` 及其关联的所有核函数、函数和符号。

```c
HGresult hgLibraryUnload (HGlibrary library)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| library | in | 要卸载的库 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

---

比赛关联：通过 `hgModuleLoad`/`hgLibraryLoadFromFile` 在服务启动阶段显式预加载全部模块（而非首次调用时惰性加载，模式由环境变量 `HGGC_MODULE_LOADING` 控制），可把加载与 JIT 开销移出首请求关键路径，是 TTFT 优化的基础手段；`hgModuleUnload` + 重新加载也支持 kernel 热更新。

---

## 5. 内存管理 {#memory}

本节涵盖设备内存的分配/释放、主机-设备间数据搬运、虚拟地址空间管理以及流有序内存池。

---

### 5.1. 内存管理 {#mem-mgmt}

本模块提供**内存管理（Memory Management）** 接口，覆盖设备/主机/统一内存的分配、释放、映射以及属性查询。

本节介绍低级 HGGC 驱动程序应用程序编程接口的内存管理函数。

#### 1. 接口一览 {#接口一览}

| 函数 | 用途 |
|------|------|
| [hgMemAlloc](#hgmemalloc) | 分配设备内存 |
| [hgMemAllocHost](#hgmemallochost) | 在主机上分配 bytesize 字节的页锁定内存 |
| [hgMemAllocManaged](#hgmemallocmanaged) | 分配统一内存 |
| [hgMemAllocPitch](#hgmemallocpitch) | 分配带间距的设备内存 |
| [hgMemFree](#hgmemfree) | 释放设备内存 |
| [hgMemFreeHost](#hgmemfreehost) | 释放页锁定主机内存 |
| [hgMemGetAddressRange](#hgmemgetaddressrange) | 获取内存分配信息 |
| [hgMemGetHandleForAddressRange](#hgmemgethandleforaddressrange) | 获取地址范围的共享句柄 |
| [hgMemGetInfo](#hgmemgetinfo) | 获取可用和总内存 |
| [hgMemHostAlloc](#hgmemhostalloc) | 分配 bytesize 字节的主机内存，并返回指向所分配内存的指针 p… |
| [hgMemHostGetDevicePointer](#hgmemhostgetdevicepointer) | 返回映射页锁定内存的设备指针 |
| [hgMemHostGetFlags](#hgmemhostgetflags) | 返回页锁定内存的标志 |
| [hgMemHostRegister](#hgmemhostregister) | 注册主机内存范围 |
| [hgMemHostUnregister](#hgmemhostunregister) | 取消注册主机内存范围 |
| [hgMemAdvise](#hgmemadvise) | 为给定内存范围的使用提供建议 |
| [hgMemPrefetchAsync](#hgmemprefetchasync) | 将内存预取到指定的目标位置 |
| [hgMemRangeGetAttribute](#hgmemrangegetattribute) | 查询给定内存范围的单个属性 |
| [hgMemRangeGetAttributes](#hgmemrangegetattributes) | 查询给定内存范围的多个属性 |
| [hgPointerGetAttribute](#hgpointergetattribute) | 支持的属性包括： |
| [hgPointerGetAttributes](#hgpointergetattributes) | 支持的属性（属性说明和限制请参阅 hgPointerGetAttrib… |
| [hgPointerSetAttribute](#hgpointersetattribute) | 设置先前分配的内存区域上的属性 |
| [hgIpcGetEventHandle](#hgipcgeteventhandle) | 获取事件的进程间句柄 |
| [hgIpcOpenEventHandle](#hgipcopeneventhandle) | 打开事件的进程间句柄 |
| [hgIpcGetMemHandle](#hgipcgetmemhandle) | 获取设备内存分配的进程间句柄 |
| [hgIpcOpenMemHandle](#hgipcopenmemhandle) | 打开设备内存的进程间句柄 |
| [hgIpcCloseMemHandle](#hgipcclosememhandle) | 关闭进程间映射的设备内存 |
| [hgDeviceGetByPCIBusId](#hgdevicegetbypcibusid) | 根据 PCI 总线 ID 获取设备句柄 |
| [hgDeviceGetPCIBusId](#hgdevicegetpcibusid) | 获取设备的 PCI 总线 ID 字符串 |

---

#### 2. hgMemAlloc {#hgmemalloc}

在设备上分配 bytesize 字节的线性内存，并以 dptr 的形式返回指向所分配内存的指针。分配的内存适当对齐以用于任何类型。内存未初始化。此函数未初始化内存。分配的内存通过 hgMemFree() 释放。

```c
HGresult hgMemAlloc(HGdeviceptr* dptr, size_t bytesize)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dptr | out | 返回的设备指针 |
| bytesize | in | 要分配的字节大小 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_OUT_OF_MEMORY

另见：[hgMemAllocHost](#hgmemallochost), [hgMemAllocManaged](#hgmemallocmanaged), [hgMemAllocPitch](#hgmemallocpitch), [hgMemFree](#hgmemfree), [hgMemFreeHost](#hgmemfreehost), [hgMemHostAlloc](#hgmemhostalloc), [hgMemHostRegister](#hgmemhostregister), [hgMemHostUnregister](#hgmemhostunregister), [hggcMalloc](04_runtime_api.md)

---

#### 3. hgMemAllocHost {#hgmemallochost}

在主机上分配 bytesize 字节的页锁定内存。页锁定内存不会被操作系统分页出去，因此在对其调用 hgMemcpyHtoD、hgMemcpyDtoh、hgMemcpyDtoD、hgMemcpyDtoH、hgMemcpy2D、hgMemcpy3D 或 hgMemcpy2DAsync 时可以以更高的带宽进行 DMA 传输。分配未初始化。此函数未初始化内存。

```c
HGresult hgMemAllocHost(void** pp, size_t bytesize)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pp | out | 返回的主机指针 |
| bytesize | in | 要分配的字节大小 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_OUT_OF_MEMORY

另见：[hgMemAlloc](#hgmemalloc), [hgMemAllocManaged](#hgmemallocmanaged), [hgMemAllocPitch](#hgmemallocpitch), [hgMemFree](#hgmemfree), [hgMemFreeHost](#hgmemfreehost), [hgMemHostAlloc](#hgmemhostalloc), [hgMemHostRegister](#hgmemhostregister), [hgMemHostUnregister](#hgmemhostunregister), [hggcMallocHost](04_runtime_api.md)

---

#### 4. hgMemAllocManaged {#hgmemallocmanaged}

分配 bytesize 字节的线性统一内存，并返回指向所分配内存的指针 dptr。统一内存有一个单一的虚拟地址，CPU 和设备都可以访问。程序在统一内存上会自动进行页迁移，以将数据移动到访问它的处理器。分配的内存适当对齐以用于任何类型。内存未初始化。

flags 参数用于指定内存分配的特殊行为：
- HG_MEM_ATTACH_GLOBAL：内存分配可被所有设备上的所有流访问。这是 flags 参数的默认值。
- HG_MEM_ATTACH_HOST：内存分配将被附加到所有设备上的所有流，但只能在主机上访问。

```c
HGresult hgMemAllocManaged(HGdeviceptr* dptr,
                           size_t bytesize,
                           unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dptr | out | 返回的设备指针 |
| bytesize | in | 要分配的字节大小 |
| flags | in | 内存分配的选项 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_OUT_OF_MEMORY、HGGC_ERROR_NOT_FOUND、HGGC_ERROR_UNKNOWN

另见：[hgMemAlloc](#hgmemalloc), [hgMemAllocHost](#hgmemallochost), [hgMemAllocPitch](#hgmemallocpitch), [hgMemFree](#hgmemfree), [hgMemFreeHost](#hgmemfreehost), [hgMemHostAlloc](#hgmemhostalloc), [hgMemHostRegister](#hgmemhostregister), [hgMemHostUnregister](#hgmemhostunregister), [hggcMallocManaged](04_runtime_api.md)

---

#### 5. hgMemAllocPitch {#hgmemallocpitch}

分配带间距的设备内存。
此函数分配 WidthInBytes * Height 字节的线性内存，并返回指向所分配内存的指针 dptr（类似于 hgMemAlloc），并返回通过 pPitch 指向的设备内存中的间距（即从一行开头到下一行开头的字节数）。

如果 ElementSizeBytes 设置为 0 或 4、8 或 16 以外的任何值，则间距将保持 0。

对于二维数组，如果需要在数组中读取或写入矩阵，则间距（pitch）非常重要，因为如果允许越界访问，设备代码可能会读取或写入相邻行。由于越界读取或写入可能是灾难性的（尤其是对于二维卷积），间距提供了一种以安全方式执行二维数组内存访问的方法。间距必须由 hgMemAllocPitch 返回（而不是任意用户指定的值）才能正确执行。

```c
HGresult hgMemAllocPitch(HGdeviceptr* dptr,
                         size_t* pPitch,
                         size_t WidthInBytes,
                         size_t Height,
                         unsigned int ElementSizeBytes)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dptr | out | 返回的设备指针 |
| pPitch | out | 返回的间距 |
| WidthInBytes | in | 宽度（以字节为单位） |
| Height | in | 高度（以元素为单位） |
| ElementSizeBytes | in | 元素大小（以字节为单位） |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_OUT_OF_MEMORY

另见：[hgMemAlloc](#hgmemalloc), [hgMemAllocHost](#hgmemallochost), [hgMemAllocManaged](#hgmemallocmanaged), [hgMemFree](#hgmemfree), [hgMemFreeHost](#hgmemfreehost), [hgMemHostAlloc](#hgmemhostalloc), [hgMemHostRegister](#hgmemhostregister), [hgMemHostUnregister](#hgmemhostunregister), [hggcMallocPitch](04_runtime_api.md)

---

#### 6. hgMemFree {#hgmemfree}

释放由 hgMemAlloc 或 hgMemAllocPitch 分配的设备内存。

```c
HGresult hgMemFree(HGdeviceptr dptr)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dptr | in | 设备指针 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemAlloc](#hgmemalloc), [hgMemAllocHost](#hgmemallochost), [hgMemAllocManaged](#hgmemallocmanaged), [hgMemAllocPitch](#hgmemallocpitch), [hgMemFreeHost](#hgmemfreehost), [hgMemHostAlloc](#hgmemhostalloc), [hgMemHostRegister](#hgmemhostregister), [hgMemHostUnregister](#hgmemhostunregister), [hggcFree](04_runtime_api.md)

---

#### 7. hgMemFreeHost {#hgmemfreehost}

释放由 hgMemAllocHost 或 hgMemHostAlloc 分配的主机内存。

```c
HGresult hgMemFreeHost(void* p)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| p | in | 主机指针 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemAlloc](#hgmemalloc), [hgMemAllocHost](#hgmemallochost), [hgMemAllocManaged](#hgmemallocmanaged), [hgMemAllocPitch](#hgmemallocpitch), [hgMemFree](#hgmemfree), [hgMemHostAlloc](#hgmemhostalloc), [hgMemHostRegister](#hgmemhostregister), [hgMemHostUnregister](#hgmemhostunregister), [hggcFreeHost](04_runtime_api.md)

---

#### 8. hgMemGetAddressRange {#hgmemgetaddressrange}

返回 dptr 指向的内存分配的基础地址和大小。如果 dptr 不是由 hgMemAlloc 或 hgMemAllocPitch 分配的，则此函数将失败。如果 dptr 是由 hgMemHostAlloc 分配的，则返回的 *pbase 和 *psize 匹配传递给 hgMemHostAlloc 的参数（以及 *pp 和 *pbytesize 的对应参数）。

```c
HGresult hgMemGetAddressRange(HGdeviceptr* pbase, size_t* psize, HGdeviceptr dptr)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pbase | out | 返回的基础地址 |
| psize | out | 返回的大小 |
| dptr | in | 设备指针 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemAlloc](#hgmemalloc), [hgMemAllocHost](#hgmemallochost), [hgMemAllocManaged](#hgmemallocmanaged), [hgMemAllocPitch](#hgmemallocpitch), [hgMemFree](#hgmemfree), [hgMemFreeHost](#hgmemfreehost), [hgMemHostAlloc](#hgmemhostalloc), [hgMemHostRegister](#hgmemhostregister), [hgMemHostUnregister](#hgmemhostunregister), [hggcGetSymbolAddress](04_runtime_api.md)

---

#### 9. hgMemGetHandleForAddressRange {#hgmemgethandleforaddressrange}

返回设备内存地址范围的共享句柄。

```c
HGresult hgMemGetHandleForAddressRange(void* handle,
                                       HGdeviceptr dptr,
                                       size_t size,
                                       HGmemRangeHandleType handleType,
                                       unsigned long long flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| handle | out | 返回的句柄 |
| dptr | in | 设备指针 |
| size | in | 地址范围的大小 |
| handleType | in | 句柄类型 |
| flags | in | 标志 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_OUT_OF_MEMORY、HGGC_ERROR_INVALID_HANDLE

另见：[hgMemMap](#hgmemmap), [hgMemUnmap](#hgmemunmap), [hgMemSetAccess](#hgmemsetaccess), [hgMemGetAccess](#hgmemgetaccess)

---

#### 10. hgMemGetInfo {#hgmemgetinfo}

返回 free 和 total 设备内存总量。

```c
HGresult hgMemGetInfo(size_t* free, size_t* total)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| free | out | 返回的可用内存大小 |
| total | out | 返回的总内存大小 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemAlloc](#hgmemalloc), [hgMemAllocHost](#hgmemallochost), [hgMemAllocManaged](#hgmemallocmanaged), [hgMemAllocPitch](#hgmemallocpitch), [hgMemFree](#hgmemfree), [hgMemFreeHost](#hgmemfreehost), [hgMemHostAlloc](#hgmemhostalloc), [hgMemHostRegister](#hgmemhostregister), [hgMemHostUnregister](#hgmemhostunregister), [hggcMemGetInfo](04_runtime_api.md)

---

#### 11. hgMemHostAlloc {#hgmemhostalloc}

分配 bytesize 字节的主机内存，并返回指向所分配内存的指针 pp。

Flags 指定内存分配的特殊行为：
- HG_MEM_HOST_ALLOC_DEFAULT：内存分配的行为与 hgMemAllocHost 相同。
- HG_MEM_HOST_ALLOC_DEVICEMAP：分配主机内存后，获取设备指针（通过 hgMemHostGetDevicePointer 检索）。
- HG_MEM_HOST_ALLOC_WRITECOMBINED：将内存分配为"写组合"（write-combined）模式。如果设置此标志，则不会对主机进行缓存一致性的访问。写组合内存通过 PCI Express 执行效率更高，但如果 CPU 读取，通常会表现不佳。

```c
HGresult hgMemHostAlloc(void** pp, size_t bytesize, unsigned int Flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pp | out | 返回的主机指针 |
| bytesize | in | 要分配的字节大小 |
| Flags | in | 分配选项 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_OUT_OF_MEMORY

另见：[hgMemAlloc](#hgmemalloc), [hgMemAllocHost](#hgmemallochost), [hgMemAllocManaged](#hgmemallocmanaged), [hgMemAllocPitch](#hgmemallocpitch), [hgMemFree](#hgmemfree), [hgMemFreeHost](#hgmemfreehost), [hgMemHostGetDevicePointer](#hgmemhostgetdevicepointer), [hgMemHostGetFlags](#hgmemhostgetflags), [hgMemHostRegister](#hgmemhostregister), [hgMemHostUnregister](#hgmemhostunregister), [hggcMallocHost](04_runtime_api.md)

---

#### 12. hgMemHostGetDevicePointer {#hgmemhostgetdevicepointer}

返回与主机指针 p 对应的设备指针。如果 p 不是使用 HG_MEM_HOST_ALLOC_DEVICEMAP 标志分配的主机内存，则此函数将失败。

```c
HGresult hgMemHostGetDevicePointer(HGdeviceptr* pdptr,
                                   void* p,
                                   unsigned int Flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pdptr | out | 返回的设备指针 |
| p | in | 主机指针 |
| Flags | in | 未使用，应为 0 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_OUT_OF_MEMORY

另见：[hgMemAlloc](#hgmemalloc), [hgMemAllocHost](#hgmemallochost), [hgMemAllocManaged](#hgmemallocmanaged), [hgMemAllocPitch](#hgmemallocpitch), [hgMemFree](#hgmemfree), [hgMemFreeHost](#hgmemfreehost), [hgMemHostAlloc](#hgmemhostalloc), [hgMemHostGetFlags](#hgmemhostgetflags), [hgMemHostRegister](#hgmemhostregister), [hgMemHostUnregister](#hgmemhostunregister), [hggcHostGetDevicePointer](04_runtime_api.md)

---

#### 13. hgMemHostGetFlags {#hgmemhostgetflags}

返回与主机指针 p 对应的标志。如果 p 不是通过 hgMemHostAlloc 分配的，则此函数将失败。

```c
HGresult hgMemHostGetFlags(unsigned int* pFlags, void* p)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pFlags | out | 返回的标志 |
| p | in | 主机指针 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemHostAlloc](#hgmemhostalloc), [hggcHostGetFlags](04_runtime_api.md)

---

#### 14. hgMemHostRegister {#hgmemhostregister}

注册整个主机内存 range 以进行 DMA 传输。注册后，内存被锁定以进行 CPU 访问。与通过 hgMemHostAlloc 分配的页锁定内存一样，注册的主机内存不会被操作系统分页出去。可以通过 hgMemcpy 访问已注册的内存。Flags 参数指定内存分配的特殊行为：
- HG_MEM_HOST_REGISTER_DEFAULT：将内存注册为默认行为。
- HG_MEM_HOST_REGISTER_DEVICEMAP：将内存注册并获取设备指针。
- HG_MEM_HOST_REGISTER_WRITECOMBINED：将内存注册为"写组合"模式。

```c
HGresult hgMemHostRegister(void* p, size_t bytesize, unsigned int Flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| p | in | 主机指针 |
| bytesize | in | 主机内存的大小 |
| Flags | in | 标志 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_OUT_OF_MEMORY

另见：[hgMemAlloc](#hgmemalloc), [hgMemAllocHost](#hgmemallochost), [hgMemAllocManaged](#hgmemallocmanaged), [hgMemAllocPitch](#hgmemallocpitch), [hgMemFree](#hgmemfree), [hgMemFreeHost](#hgmemfreehost), [hgMemHostAlloc](#hgmemhostalloc), [hgMemHostGetDevicePointer](#hgmemhostgetdevicepointer), [hgMemHostGetFlags](#hgmemhostgetflags), [hgMemHostUnregister](#hgmemhostunregister), [hggcHostRegister](04_runtime_api.md)

---

#### 15. hgMemHostUnregister {#hgmemhostunregister}

取消注册之前通过 hgMemHostRegister 注册的主机内存。

```c
HGresult hgMemHostUnregister(void* p)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| p | in | 主机指针 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemAlloc](#hgmemalloc), [hgMemAllocHost](#hgmemallochost), [hgMemAllocManaged](#hgmemallocmanaged), [hgMemAllocPitch](#hgmemallocpitch), [hgMemFree](#hgmemfree), [hgMemFreeHost](#hgmemfreehost), [hgMemHostAlloc](#hgmemhostalloc), [hgMemHostGetDevicePointer](#hgmemhostgetdevicepointer), [hgMemHostGetFlags](#hgmemhostgetflags), [hgMemHostRegister](#hgmemhostregister), [hggcHostUnregister](04_runtime_api.md)

---

#### 16. hgMemAdvise {#hgmemadvise}

就给定内存范围（起始地址为 devPtr，大小为 count 字节）的使用模式向统一内存子系统提供建议。内存范围的起始地址和结束地址将分别向下舍入和向上舍入，以对齐到 CPU 页面大小后再应用建议。内存范围必须引用通过 hgMemAllocManaged 分配的由统一内存系统自动管理的内存，或通过 __managed__ 变量声明的内存。内存范围也可以引用系统分配的可分页内存，前提是它表示有效的主机可访问内存区域，并且满足 advice 指定的附加约束（见下文）。指定无效的系统分配可分页内存范围会导致返回错误。

advice 参数可以取以下值：

- HG_MEM_ADVISE_SET_READ_MOSTLY：这意味着数据大部分时间只会被读取，偶尔才会写入。从任何处理器对该区域的读取访问将在该处理器的内存中至少为已访问页面创建一个只读副本。此外，如果对该区域调用 hgMemPrefetchAsync，它将在目标处理器上创建一个只读数据副本。如果 hgMemPrefetchAsync 的目标位置是主机 NUMA 节点，并且另一个主机 NUMA 节点上已存在只读副本，则该副本将迁移到目标主机 NUMA 节点。如果任何处理器写入该区域，除写入发生的处理器外，所有对应的页面副本都将失效。如果写入处理器是 CPU 且页面的首选位置是主机 NUMA 节点，则该页面也将迁移到该主机 NUMA 节点。对于此建议，location 参数被忽略。请注意，要进行页面读复制，访问处理器必须是 CPU 或具有设备属性 HG_DEVICE_ATTRIBUTE_CONCURRENT_MANAGED_ACCESS 非零值的 PPU。此外，如果在具有设备属性 HG_DEVICE_ATTRIBUTE_CONCURRENT_MANAGED_ACCESS 未设置的设备上创建上下文，则在所有此类上下文被销毁之前，不会发生读复制。如果内存范围引用有效的系统分配的可分页内存，则访问设备必须具有设备属性 HG_DEVICE_ATTRIBUTE_PAGEABLE_MEMORY_ACCESS 的非零值，才能在该设备上创建只读副本。但是，如果访问设备还具有设备属性 HG_DEVICE_ATTRIBUTE_PAGEABLE_MEMORY_ACCESS_USES_HOST_PAGE_TABLES 的非零值，则当该设备访问此内存区域时，设置此建议不会创建只读副本。

- HG_MEM_ADVISE_UNSET_READ_MOSTLY：撤消 HG_MEM_ADVISE_SET_READ_MOSTLY 的效果，并阻止统一内存驱动程序尝试对内存范围进行启发式读复制。所有数据读复制副本将被合并为单个副本。合并副本的位置将是首选位置（如果页面有首选位置且其中一个读复制副本位于该位置）。否则，选择的位置是任意的。注意：对于此建议，location 参数被忽略。

- HG_MEM_ADVISE_SET_PREFERRED_LOCATION：此建议将数据的首选位置设置为属于 location 的内存。当 HGmemLocation::type 为 HG_MEM_LOCATION_TYPE_HOST 时，HGmemLocation::id 被忽略，首选位置设置为主机内存。要将首选位置设置为特定的主机 NUMA 节点，应用程序必须将 HGmemLocation::type 设置为 HG_MEM_LOCATION_TYPE_HOST_NUMA，并且 HGmemLocation::id 必须指定主机 NUMA 节点的 NUMA ID。如果 HGmemLocation::type 设置为 HG_MEM_LOCATION_TYPE_HOST_NUMA_CURRENT，则 HGmemLocation::id 将忽略，离调用线程 CPU 最近的主机 NUMA 节点将被用作首选位置。如果 HGmemLocation::type 是 HG_MEM_LOCATION_TYPE_DEVICE，则 HGmemLocation::id 必须是有效的设备序号，且该设备必须具有设备属性 HG_DEVICE_ATTRIBUTE_CONCURRENT_MANAGED_ACCESS 的非零值。设置首选位置不会立即导致数据迁移到该位置。相反，它在发生故障时指导迁移策略。如果数据已在首选位置且故障处理器可以在不需要数据迁移的情况下建立映射，则将避免数据迁移。另一方面，如果数据不在首选位置或者无法建立直接映射，则会将其迁移到访问它的处理器。需要注意的是，设置首选位置不会阻止使用 hgMemPrefetchAsync 进行的预取。拥有首选位置可以覆盖统一内存驱动程序中的页面抖动检测和解决逻辑。通常，如果检测到页面在主机和设备内存之间不断抖动，则统一内存驱动程序最终可能会将页面固定到主机内存。但是，如果首选位置设置为设备内存，则页面将继续无限期地抖动。如果 HG_MEM_ADVISE_SET_READ_MOSTLY 也设置在此内存区域或任何子集上，则与该建议关联的策略将覆盖此建议的策略，除非从 location 的读取访问不会在该处理器上创建只读副本（详见 HG_MEM_ADVISE_SET_READ_MOSTLY 建议的说明）。如果内存范围引用有效的系统分配的可分页内存，且 HGmemLocation::type 是 HG_MEM_LOCATION_TYPE_DEVICE，则 HGmemLocation::id 必须是具有设备属性 HG_DEVICE_ATTRIBUTE_PAGEABLE_MEMORY_ACCESS 非零值的有效设备。

- HG_MEM_ADVISE_UNSET_PREFERRED_LOCATION：撤消 HG_MEM_ADVISE_SET_PREFERRED_LOCATION 的效果，并将首选位置更改为无。对于此建议，location 参数被忽略。

- HG_MEM_ADVISE_SET_ACCESSED_BY：此建议意味着数据将被 location 处理器访问。HGmemLocation::type 必须是 HG_MEM_LOCATION_TYPE_DEVICE 且 HGmemLocation::id 代表有效的设备序号，或者是 HG_MEM_LOCATION_TYPE_HOST 且 HGmemLocation::id 将忽略。所有其他位置类型都无效。如果 HGmemLocation::id 是 PPU，则设备属性 HG_DEVICE_ATTRIBUTE_CONCURRENT_MANAGED_ACCESS 必须为非零。此建议不会导致数据迁移，也不会影响数据本身的实际位置。相反，它会导致数据始终映射在指定处理器的页表中（只要数据的位置允许建立映射）。如果因任何原因迁移了数据，映射将相应更新。适用于数据局部性不重要但需避免故障的场景。例如，考虑一个包含多个启用了点对点访问的 PPU 的系统，其中位于一个 PPU 上的数据偶尔会被对等 PPU 访问。在这种情况下，将数据迁移到其他 PPU 并不那么重要，因为访问不频繁且迁移开销可能太高。但是，防止故障仍然有助于提高性能，因此提前建立映射很有用。请注意，在 CPU 访问此数据时，数据可能会迁移到主机内存，因为 CPU 通常无法直接访问设备内存。任何已为此数据设置 HG_MEM_ADVISE_SET_ACCESSED_BY 标志的 PPU 现在都将更新其映射以指向主机内存中的页面。如果 HG_MEM_ADVISE_SET_READ_MOSTLY 也设置在此内存区域或任何子集上，则与该建议关联的策略将覆盖此建议的策略。此外，如果此内存区域或任何子集的首选位置也是 location，则 HG_MEM_ADVISE_SET_PREFERRED_LOCATION 的策略将覆盖此建议的策略。如果内存范围引用有效的系统分配的可分页内存，且 HGmemLocation::type 是 HG_MEM_LOCATION_TYPE_DEVICE，则 HGmemLocation::id 中的设备必须具有设备属性 HG_DEVICE_ATTRIBUTE_PAGEABLE_MEMORY_ACCESS 的非零值。此外，如果 HGmemLocation::id 具有设备属性 HG_DEVICE_ATTRIBUTE_PAGEABLE_MEMORY_ACCESS_USES_HOST_PAGE_TABLES 的非零值，则此调用无效。

- HG_MEM_ADVISE_UNSET_ACCESSED_BY：撤消 HG_MEM_ADVISE_SET_ACCESSED_BY 的效果。从 location 到数据的任何映射可以随时被移除，导致访问产生非致命页面故障。如果内存范围引用有效的系统分配的可分页内存，且 HGmemLocation::type 是 HG_MEM_LOCATION_TYPE_DEVICE，则 HGmemLocation::id 中的设备必须具有设备属性 HG_DEVICE_ATTRIBUTE_PAGEABLE_MEMORY_ACCESS 的非零值。此外，如果 HGmemLocation::id 具有设备属性 HG_DEVICE_ATTRIBUTE_PAGEABLE_MEMORY_ACCESS_USES_HOST_PAGE_TABLES 的非零值，则此调用无效。

```c
HGresult hgMemAdvise (HGdeviceptr devPtr,
                      size_t count,
                      HGmem_advise advice,
                      HGmemLocation location)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| devPtr | in | 要设置建议的内存指针 |
| count | in | 内存范围的大小（以字节为单位） |
| advice | in | 要应用于指定内存范围的建议 |
| location | in | 要应用建议的位置 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_DEVICE

---

#### 17. hgMemPrefetchAsync {#hgmemprefetchasync}

将内存预取到指定的目标位置。devPtr 是要预取的内存的基础设备指针，location 指定目标位置。count 指定要复制的字节数。hStream 是操作被入队的流。内存范围必须引用通过 hgMemAllocManaged、通过 hgMemAllocFromPool 从托管内存池分配的由统一内存管理的内存，或通过 __managed__ 变量声明的内存。

为 HGmemLocation::type 指定 HG_MEM_LOCATION_TYPE_DEVICE 将预取内存到 HGmemLocation::id 指定的设备序号表示的 PPU，该设备必须对设备属性 HG_DEVICE_ATTRIBUTE_CONCURRENT_MANAGED_ACCESS 具有非零值。此外，hStream 必须与对设备属性 HG_DEVICE_ATTRIBUTE_CONCURRENT_MANAGED_ACCESS 具有非零值的设备关联。将 HGmemLocation::type 指定为 HG_MEM_LOCATION_TYPE_HOST 将预取数据到主机内存。应用程序可以通过为 HGmemLocation::type 指定 HG_MEM_LOCATION_TYPE_HOST_NUMA，并在 HGmemLocation::id 中指定有效的主机 NUMA 节点 ID，来请求将内存预取到特定的主机 NUMA 节点。用户还可以通过为 HGmemLocation::type 指定 HG_MEM_LOCATION_TYPE_HOST_NUMA_CURRENT 来请求将内存预取到离当前线程 CPU 最近的主机 NUMA 节点。请注意，当 HGmemLocation::type 是 HG_MEM_LOCATION_TYPE_HOST 或 HG_MEM_LOCATION_TYPE_HOST_NUMA_CURRENT 时，HGmemLocation::id 将忽略。

内存范围的起始地址和结束地址将分别向下舍入和向上舍入，以对齐到 CPU 页面大小后再将预取操作入队到流中。

如果尚未为该区域分配物理内存，则此内存区域将被填充并映射到目标设备。如果预取所需区域没有足够的内存，统一内存驱动程序可能会从其他 hgMemAllocManaged 分配中逐出页面到主机内存以腾出空间。使用 hgMemAlloc 分配的设备内存不会被逐出。

默认情况下，迁移页面的先前位置的任何映射都被移除，仅在目标位置为新位置设置映射。但是，确切的行为还取决于通过 hgMemAdvise 应用于此内存范围的设置（见下文）：

如果对内存范围的任何子集设置了 HG_MEM_ADVISE_SET_READ_MOSTLY，则该子集将在目标位置创建页面的只读副本。但是，如果目标位置是主机 NUMA 节点，则已在另一个主机 NUMA 节点上的该子集的任何页面将被转移到目标位置。

如果对内存范围的任何子集调用了 HG_MEM_ADVISE_SET_PREFERRED_LOCATION，则即使 location 不是内存范围中任何页面的首选位置，页面也会迁移到 location。

如果对内存范围的任何子集调用了 HG_MEM_ADVISE_SET_ACCESSED_BY，则从所有适当处理器的页面对这些页面的映射将更新为指向新位置（如果可以建立此类映射）。否则，这些映射将被清除。

请注意，此 API 不需要用于功能，仅用于通过允许应用程序在访问数据之前将其迁移到合适的位置来提高性能。对此范围的内存访问始终是一致的，即使在数据被积极迁移时也允许访问。

请注意，此函数相对于主机和所有其他设备上的工作来说是异步的。

```c
HGresult hgMemPrefetchAsync (HGdeviceptr devPtr,
                             size_t count,
                             HGmemLocation location,
                             unsigned int flags,
                             HGstream hStream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| devPtr | in | 要预取的指针 |
| count | in | 大小（以字节为单位） |
| location | in | 预取到的位置 |
| flags | in | 保留供将来使用的标志，目前必须为零 |
| hStream | in | 入队预取操作的流 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_DEVICE

---

#### 18. hgMemRangeGetAttribute {#hgmemrangegetattribute}

查询从 devPtr 开始、大小为 count 字节的内存范围的属性。内存范围必须引用通过 hgMemAllocManaged 分配的由统一内存管理的内存，或通过 __managed__ 变量声明的内存。

attribute 参数可以取以下值：

- HG_MEM_RANGE_ATTRIBUTE_READ_MOSTLY：如果指定了此属性，data 将被解释为 32 位整数，且 dataSize 必须为 4。如果给定内存范围中的所有页面都启用了读复制，则返回的结果将为 1，否则为 0。

- HG_MEM_RANGE_ATTRIBUTE_PREFERRED_LOCATION：如果指定了此属性，data 将被解释为 32 位整数，且 dataSize 必须为 4。如果内存范围中的所有页面都以该 PPU 为首选位置，则返回的结果将是 PPU 设备 ID；如果所有页面都以 CPU 为首选位置，则返回 HG_DEVICE_CPU；如果并非所有页面都具有相同的首选位置，或者某些页面根本没有首选位置，则返回 HG_DEVICE_INVALID。请注意，查询时内存范围中页面的实际位置可能与首选位置不同。

- HG_MEM_RANGE_ATTRIBUTE_ACCESSED_BY：如果指定了此属性，data 将被解释为 32 位整数数组，且 dataSize 必须为 4 的非零倍数。返回的结果将是在整个内存范围内设置了 HG_MEM_ADVISE_SET_ACCESSED_BY 的设备 ID 列表。如果任何设备没有在整个内存范围内设置该建议，则该设备将不包含在内。如果 data 大于设置了该建议的设备数量，则在提供的所有额外空间中返回 HG_DEVICE_INVALID。例如，如果 dataSize 为 12（即 data 有 3 个元素）且只有设备 0 设置了该建议，则返回的结果将是 { 0, HG_DEVICE_INVALID, HG_DEVICE_INVALID }。如果 data 小于设置了该建议的设备数量，则只返回能够容纳在数组中的设备数量。不能保证会返回哪些特定设备。

- HG_MEM_RANGE_ATTRIBUTE_LAST_PREFETCH_LOCATION：如果指定了此属性，data 将被解释为 32 位整数，且 dataSize 必须为 4。返回的结果将是内存范围中所有页面通过 hgMemPrefetchAsync 显式预取到的最后一个位置。这将是 PPU ID 或 HG_DEVICE_CPU，取决于最后的预取位置是 PPU 还是 CPU。如果内存范围中的任何页面从未被显式预取过，或者并非所有页面都被预取到相同的位置，则返回 HG_DEVICE_INVALID。请注意，这只返回应用程序请求将内存范围预取到的最后一个位置。它不指示预取到该位置的操作是否已完成，甚至是否已开始。

- HG_MEM_RANGE_ATTRIBUTE_PREFERRED_LOCATION_TYPE：如果指定了此属性，data 将被解释为 HGmemLocationType，且 dataSize 必须为 sizeof(HGmemLocationType)。返回的 HGmemLocationType 将是：如果内存范围中的所有页面都以相同的 PPU 为首选位置，则为 HG_MEM_LOCATION_TYPE_DEVICE；如果所有页面都以 CPU 为首选位置，则为 HG_MEM_LOCATION_TYPE_HOST；如果内存范围中的所有页面都以相同的主机 NUMA 节点 ID 为首选位置，则为 HG_MEM_LOCATION_TYPE_HOST_NUMA；如果并非所有页面都具有相同的首选位置，或者某些页面根本没有首选位置，则为 HG_MEM_LOCATION_TYPE_INVALID。请注意，查询时内存范围中页面的实际位置类型可能与首选位置类型不同。

  - HG_MEM_RANGE_ATTRIBUTE_PREFERRED_LOCATION_ID：如果指定了此属性，data 将被解释为 32 位整数，且 dataSize 必须为 4。如果同一地址范围的 HG_MEM_RANGE_ATTRIBUTE_PREFERRED_LOCATION_TYPE 查询返回 HG_MEM_LOCATION_TYPE_DEVICE，则它将是有效的设备序号；如果返回 HG_MEM_LOCATION_TYPE_HOST_NUMA，则它将是有效的主机 NUMA 节点 ID；如果返回任何其他位置类型，则应忽略该 ID。

- HG_MEM_RANGE_ATTRIBUTE_LAST_PREFETCH_LOCATION_TYPE：如果指定了此属性，data 将被解释为 HGmemLocationType，且 dataSize 必须为 sizeof(HGmemLocationType)。返回的结果将是内存范围中所有页面通过 hgMemPrefetchAsync 显式预取到的最后一个位置的类型。返回的 HGmemLocationType 将是：如果最后的预取位置是 PPU，则为 HG_MEM_LOCATION_TYPE_DEVICE；如果是 CPU，则为 HG_MEM_LOCATION_TYPE_HOST；如果是特定的主机 NUMA 节点，则为 HG_MEM_LOCATION_TYPE_HOST_NUMA。如果内存范围中的任何页面从未被显式预取过，或者并非所有页面都被预取到相同的位置，则 HGmemLocationType 将为 HG_MEM_LOCATION_TYPE_INVALID。请注意，这只返回应用程序请求将内存范围预取到的最后一个位置类型。它不指示预取到该位置的操作是否已完成，甚至是否已开始。

  - HG_MEM_RANGE_ATTRIBUTE_LAST_PREFETCH_LOCATION_ID：如果指定了此属性，data 将被解释为 32 位整数，且 dataSize 必须为 4。如果同一地址范围的 HG_MEM_RANGE_ATTRIBUTE_LAST_PREFETCH_LOCATION_TYPE 查询返回 HG_MEM_LOCATION_TYPE_DEVICE，则它将是有效的设备序号；如果返回 HG_MEM_LOCATION_TYPE_HOST_NUMA，则它将是有效的主机 NUMA 节点 ID；如果返回任何其他位置类型，则应忽略该 ID。

```c
HGresult hgMemRangeGetAttribute (void* data,
                                 size_t dataSize,
                                 HGmem_range_attribute attribute,
                                 HGdeviceptr devPtr,
                                 size_t count)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| data | in | 指向内存位置的指针，每个属性查询的结果将被写入该位置 |
| dataSize | in | 包含数据大小的数组 |
| attribute | in | 要查询的属性 |
| devPtr | in | 要查询的范围的起始地址 |
| count | in | 要查询的范围的大小 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_DEVICE

---

#### 19. hgMemRangeGetAttributes {#hgmemrangegetattributes}

查询从 devPtr 开始、大小为 count 字节的内存范围的属性。内存范围必须引用通过 hgMemAllocManaged 分配的由统一内存管理的内存，或通过 __managed__ 变量声明的内存。attributes 数组将被解释为具有 numAttributes 个条目。dataSizes 数组也将被解释为具有 numAttributes 个条目。查询结果将存储在 data 中。

支持的属性列表如下。请参阅 hgMemRangeGetAttribute 了解属性说明和限制。

- HG_MEM_RANGE_ATTRIBUTE_READ_MOSTLY
- HG_MEM_RANGE_ATTRIBUTE_PREFERRED_LOCATION
- HG_MEM_RANGE_ATTRIBUTE_ACCESSED_BY
- HG_MEM_RANGE_ATTRIBUTE_LAST_PREFETCH_LOCATION
- HG_MEM_RANGE_ATTRIBUTE_PREFERRED_LOCATION_TYPE
- HG_MEM_RANGE_ATTRIBUTE_PREFERRED_LOCATION_ID
- HG_MEM_RANGE_ATTRIBUTE_LAST_PREFETCH_LOCATION_TYPE
- HG_MEM_RANGE_ATTRIBUTE_LAST_PREFETCH_LOCATION_ID

```c
HGresult hgMemRangeGetAttributes (void** data,
                                  size_t* dataSizes,
                                  HGmem_range_attribute* attributes,
                                  size_t numAttributes,
                                  HGdeviceptr devPtr,
                                  size_t count)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| data | in | 二维数组，包含指向内存位置的指针，每个属性查询的结果将被写入该位置 |
| dataSizes | in | 包含每个结果大小的数组 |
| attributes | in | 要查询的属性数组（numAttributes 与此数组中的属性数量应匹配） |
| numAttributes | in | 要查询的属性数量 |
| devPtr | in | 要查询的范围的起始地址 |
| count | in | 要查询的范围的大小 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_DEVICE

---

#### 20. hgPointerGetAttribute {#hgpointergetattribute}

支持的属性包括：

- HG_POINTER_ATTRIBUTE_CONTEXT：在 *data 中返回 ptr 被分配或注册/映射到的 HGcontext。data 的类型必须是 HGcontext *。如果 ptr 不是由使用统一虚拟寻址的 HGcontext 分配、映射或注册的，则返回 HGGC_ERROR_INVALID_VALUE。

- HG_POINTER_ATTRIBUTE_MEMORY_TYPE：在 *data 中返回 ptr 所指向的内存的物理内存类型，作为 HGmemorytype 枚举值。data 的类型必须是 unsigned int。如果 ptr 指向设备内存，则 *data 设置为 HG_MEMORYTYPE_DEVICE。内存所在的特定 HGdevice 是 ptr 的 HG_POINTER_ATTRIBUTE_CONTEXT 属性返回的 HGcontext 的 HGdevice。如果 ptr 指向主机内存，则 *data 设置为 HG_MEMORYTYPE_HOST。如果 ptr 不是由使用统一虚拟寻址的 HGcontext 分配、映射或注册的，则返回 HGGC_ERROR_INVALID_VALUE。如果当前 HGcontext 不支持统一虚拟寻址，则返回 HGGC_ERROR_INVALID_CONTEXT。

- HG_POINTER_ATTRIBUTE_DEVICE_POINTER：在 *data 中返回设备指针值，通过该指针值，运行在当前 HGcontext 中的核函数可以访问 ptr。data 的类型必须是 HGdeviceptr *。如果不存在当前 HGcontext 中的核函数可以通过其访问 ptr 的设备指针值，则返回 HGGC_ERROR_INVALID_VALUE。如果没有当前 HGcontext，则返回 HGGC_ERROR_INVALID_CONTEXT。除了下面讨论的例外不相交寻址情况外，*data 中返回的值将等于输入值 ptr。

- HG_POINTER_ATTRIBUTE_HOST_POINTER：在 *data 中返回主机指针值，通过该指针值，主机程序可以访问 ptr。data 的类型必须是 void **。如果不存在主机程序可以直接访问 ptr 的主机指针值，则返回 HGGC_ERROR_INVALID_VALUE。除了例外不相交寻址情况外，*data 中返回的值将等于输入值 ptr。

- HG_POINTER_ATTRIBUTE_P2P_TOKENS：在 *data 中返回两个令牌，供 nv-p2p.h Linux 内核接口使用。data 必须是类型为 HGGC_POINTER_ATTRIBUTE_P2P_TOKENS 的结构。ptr 必须是来自 hgMemAlloc() 的内存的指针。请注意，p2pToken 和 vaSpaceToken 仅在源分配的生命周期内有效。随后在同一地址的分配可能返回完全不同的令牌。查询此属性有副作用，即为 ptr 指向的内存区域设置属性 HG_POINTER_ATTRIBUTE_SYNC_MEMOPS。

- HG_POINTER_ATTRIBUTE_SYNC_MEMOPS：一个布尔属性，设置为时，确保对 ptr 指向的内存区域启动的同步内存操作始终同步。请参阅标题为"API 同步行为"的文档部分，了解有关同步内存操作何时表现出异步行为的更多信息。

- HG_POINTER_ATTRIBUTE_BUFFER_ID：在 *data 中返回一个缓冲区 ID，该 ID 在进程范围内保证是唯一的。data 必须指向 unsigned long long。ptr 必须是来自 HGGC 内存分配 API 的内存的指针。来自任何 HGGC 内存分配 API 的每次分配在进程生命周期内都将具有唯一 ID。后续分配不会重用先前释放的分配的 ID。ID 仅在单个进程范围内唯一。

- HG_POINTER_ATTRIBUTE_IS_MANAGED：在 *data 中返回一个布尔值，指示指针是否指向托管内存。如果 ptr 不是有效的 HGGC 指针，则返回 HGGC_ERROR_INVALID_VALUE。

- HG_POINTER_ATTRIBUTE_DEVICE_ORDINAL：在 *data 中返回一个整数，表示分配或注册该内存的设备的设备序号。

- HG_POINTER_ATTRIBUTE_IS_LEGACY_HGGC_IPC_CAPABLE：在 *data 中返回一个布尔值，指示此指针是否映射到适合 hggcIpcGetMemHandle 的分配。

- HG_POINTER_ATTRIBUTE_RANGE_START_ADDR：在 *data 中返回设备指针 ptr 所引用的分配的起始地址。请注意，这不一定是映射区域的地址，而是 ptr 所引用的可映射地址范围的地址（例如来自 hgMemAddressReserve）。

- HG_POINTER_ATTRIBUTE_RANGE_SIZE：在 *data 中返回设备指针 ptr 所引用的分配的大小。请注意，这不一定是映射区域的大小，而是 ptr 所引用的可映射地址范围的大小（例如来自 hgMemAddressReserve）。要检索映射区域的大小，请参阅 hgMemGetAddressRange。

- HG_POINTER_ATTRIBUTE_MAPPED：在 *data 中返回一个布尔值，指示此指针是否在映射到后备分配的有效地址范围内。

- HG_POINTER_ATTRIBUTE_ALLOWED_HANDLE_TYPES：返回分配的可允许句柄类型的位掩码，这些句柄类型可能传递给 hgMemExportToShareableHandle。

- HG_POINTER_ATTRIBUTE_MEMPOOL_HANDLE：在 *data 中返回分配所来自的内存池的句柄。

- HG_POINTER_ATTRIBUTE_IS_HW_DECOMPRESS_CAPABLE：在 *data 中返回一个布尔值，指示指针指向的内存是否能够用于硬件加速解压。

请注意，对于统一虚拟地址空间中的大多数分配，访问分配的主机指针和设备指针将是相同的。例外情况包括：

- 使用 hgMemHostRegister 注册的用户内存
- 使用 hgMemHostAlloc 和 HG_MEMHOSTALLOC_WRITECOMBINED 标志分配的主机内存

对于这些类型的分配，访问该分配将存在独立的、不相交的主机和设备地址。特别是：

- 主机地址将对应于无效的未映射设备地址（如果从设备访问将导致异常）
- 设备地址将对应于无效的未映射主机地址（如果从主机访问将导致异常）。对于这些类型的分配，查询 HG_POINTER_ATTRIBUTE_HOST_POINTER 和 HG_POINTER_ATTRIBUTE_DEVICE_POINTER 可用于从任一地址检索主机和设备地址。

```c
HGresult hgPointerGetAttribute (void* data,
                                HGpointer_attribute attribute,
                                HGdeviceptr ptr)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| data | out | 返回的指针属性值 |
| attribute | in | 要查询的指针属性 |
| ptr | in | 指针 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_DEVICE

---

#### 21. hgPointerGetAttributes {#hgpointergetattributes}

支持的属性（属性说明和限制请参阅 hgPointerGetAttribute）：

- HG_POINTER_ATTRIBUTE_CONTEXT
- HG_POINTER_ATTRIBUTE_MEMORY_TYPE
- HG_POINTER_ATTRIBUTE_DEVICE_POINTER
- HG_POINTER_ATTRIBUTE_HOST_POINTER
- HG_POINTER_ATTRIBUTE_SYNC_MEMOPS
- HG_POINTER_ATTRIBUTE_BUFFER_ID
- HG_POINTER_ATTRIBUTE_IS_MANAGED
- HG_POINTER_ATTRIBUTE_DEVICE_ORDINAL
- HG_POINTER_ATTRIBUTE_RANGE_START_ADDR
- HG_POINTER_ATTRIBUTE_RANGE_SIZE
- HG_POINTER_ATTRIBUTE_MAPPED
- HG_POINTER_ATTRIBUTE_IS_LEGACY_HGGC_IPC_CAPABLE
- HG_POINTER_ATTRIBUTE_ALLOWED_HANDLE_TYPES
- HG_POINTER_ATTRIBUTE_MEMPOOL_HANDLE
- HG_POINTER_ATTRIBUTE_IS_HW_DECOMPRESS_CAPABLE

与 hgPointerGetAttribute 不同，当遇到的 ptr 不是有效的 HGGC 指针时，此函数不会返回错误。相反，属性被分配默认的 NULL 值并返回 HGGC_SUCCESS。

如果 ptr 不是由使用 UVA（统一虚拟寻址）的 HGcontext 分配、映射或注册的，则返回 HGGC_ERROR_INVALID_CONTEXT。

```c
HGresult hgPointerGetAttributes (unsigned int numAttributes,
                                 HGpointer_attribute* attributes,
                                 void** data,
                                 HGdeviceptr ptr)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| numAttributes | in | 要查询的属性数量 |
| attributes | in | 要查询的属性数组（numAttributes 与此数组中的属性数量应匹配） |
| data | in | 二维数组，包含指向内存位置的指针，每个属性查询的结果将被写入该位置 |
| ptr | in | 要查询的指针 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_DEVICE

---

#### 22. hgPointerSetAttribute {#hgpointersetattribute}

支持的属性包括：

- HG_POINTER_ATTRIBUTE_SYNC_MEMOPS：一个布尔属性，可以设置为（1）或取消设置（0）。当设置时，保证对 ptr 指向的内存区域的同步内存操作将始终同步。如果在设置此属性时有某些先前启动的同步内存操作尚未完成，则此函数不会返回，直到这些内存操作完成。请参阅标题为"API 同步行为"的文档部分，了解有关同步内存操作何时表现出异步行为的更多信息。value 将被视为指向无符号整数的指针，该属性将设置到该指针。

```c
HGresult hgPointerSetAttribute (const void* value,
                                HGpointer_attribute attribute,
                                HGdeviceptr ptr)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| value | in | 指向包含要设置值的内存的指针 |
| attribute | in | 要设置的指针属性 |
| ptr | in | 指向使用 HGGC 内存分配 API 分配的内存区域的指针 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_DEVICE

---

#### 23. hgIpcGetEventHandle {#hgipcgeteventhandle}

获取先前已分配事件的进程间句柄。该事件必须在创建时设置了 `HG_EVENT_INTERPROCESS` 和 `HG_EVENT_DISABLE_TIMING` 标志。这一不透明句柄可以被复制到其他进程，并使用 `hgIpcOpenEventHandle` 打开，以允许在不同进程的 PPU 工作之间进行高效的硬件同步。

在导入进程中打开事件后，可在任一进程中使用 `hgEventRecord`、`hgEventSynchronize`、`hgStreamWaitEvent` 和 `hgEventQuery`。在使用 `hgEventDestroy` 释放导出端事件之后，再对导入端事件执行任何操作将导致未定义行为。

IPC 功能仅限于在 Linux 操作系统上支持统一寻址的设备。开发者可以通过使用 `HG_DEVICE_ATTRIBUTE_IPC_EVENT_SUPPORTED` 调用 `hgDeviceGetAttribute` 来测试设备的 IPC 功能。

```c
HGresult hgIpcGetEventHandle(HGipcEventHandle* pHandle, HGevent event)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pHandle | out | 指向用户分配的 `HGipcEventHandle` 的指针，用于返回不透明事件句柄 |
| event | in | 使用 `HG_EVENT_INTERPROCESS` 和 `HG_EVENT_DISABLE_TIMING` 标志分配的事件 |

错误码：HGGC_SUCCESS、HGGC_ERROR_INVALID_HANDLE、HGGC_ERROR_OUT_OF_MEMORY、HGGC_ERROR_MAP_FAILED、HGGC_ERROR_INVALID_VALUE

---

#### 24. hgIpcOpenEventHandle {#hgipcopeneventhandle}

打开从另一进程通过 `hgIpcGetEventHandle` 导出的进程间事件句柄，供当前进程使用。此函数返回一个 `HGevent`，其行为类似于使用 `HG_EVENT_DISABLE_TIMING` 标志在本地创建的事件。该事件必须使用 `hgEventDestroy` 释放。

在使用 `hgEventDestroy` 释放导出端事件之后，再对导入端事件执行任何操作将导致未定义行为。

IPC 功能仅限于在 Linux 操作系统上支持统一寻址的设备。开发者可以通过使用 `HG_DEVICE_ATTRIBUTE_IPC_EVENT_SUPPORTED` 调用 `hgDeviceGetAttribute` 来测试设备的 IPC 功能。

```c
HGresult hgIpcOpenEventHandle(HGevent* phEvent, HGipcEventHandle handle)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| phEvent | out | 返回导入的事件 |
| handle | in | 要打开的进程间句柄 |

错误码：HGGC_SUCCESS、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_MAP_FAILED、HGGC_ERROR_PEER_ACCESS_UNSUPPORTED、HGGC_ERROR_INVALID_HANDLE、HGGC_ERROR_INVALID_VALUE

---

#### 25. hgIpcGetMemHandle {#hgipcgetmemhandle}

获取已存在的设备内存分配的进程间内存句柄。接受一个指向通过 `hgMemAlloc` 创建的现有设备内存分配的基址指针，并将其导出供另一个进程使用。此操作是轻量级的，可以在同一分配上多次调用而无副作用。

如果某个内存区域被 `hgMemFree` 释放后，随后的 `hgMemAlloc` 调用返回了具有相同设备地址的内存，`hgIpcGetMemHandle` 将为新内存返回一个唯一的句柄。

IPC 功能仅限于在 Linux 操作系统上支持统一寻址的设备。开发者可以通过使用 `HG_DEVICE_ATTRIBUTE_IPC_EVENT_SUPPORTED` 调用 `hgDeviceGetAttribute` 来测试设备的 IPC 功能。

```c
HGresult hgIpcGetMemHandle(HGipcMemHandle* pHandle, HGdeviceptr dptr)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pHandle | out | 指向用户分配的 `HGipcMemHandle` 的指针，用于返回句柄 |
| dptr | in | 指向先前分配的设备内存的基址指针 |

错误码：HGGC_SUCCESS、HGGC_ERROR_INVALID_HANDLE、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_OUT_OF_MEMORY、HGGC_ERROR_MAP_FAILED、HGGC_ERROR_INVALID_VALUE

---

#### 26. hgIpcOpenMemHandle {#hgipcopenmemhandle}

打开从另一进程通过 `hgIpcGetMemHandle` 导出的进程间内存句柄，并返回可在本地进程中使用的设备指针。

将通过 `hgIpcGetMemHandle` 从另一进程导出的内存映射到当前设备的地址空间。对于不同设备上的上下文，`hgIpcOpenMemHandle` 可以尝试在设备之间启用对等访问，就像用户调用了 `hgCtxEnablePeerAccess` 一样。此行为由 `HG_IPC_MEM_LAZY_ENABLE_PEER_ACCESS` 标志控制。`hgDeviceCanAccessPeer` 可以确定是否可以进行映射。

可以打开 `HGipcMemHandles` 的上下文受到以下限制：给定进程中每个 `HGdevice` 的 `HGipcMemHandles`，对于每个其他进程中每个 `HGdevice`，只能由一个 `HGcontext` 打开。

如果当前上下文已打开该内存句柄，则句柄的引用计数增加 1，并返回现有的设备指针。

从 `hgIpcOpenMemHandle` 返回的内存必须使用 `hgIpcCloseMemHandle` 释放。在导入上下文调用 `hgIpcCloseMemHandle` 之前，对导出内存区域调用 `hgMemFree` 将导致未定义行为。

IPC 功能仅限于在 Linux 操作系统上支持统一寻址的设备。开发者可以通过使用 `HG_DEVICE_ATTRIBUTE_IPC_EVENT_SUPPORTED` 调用 `hgDeviceGetAttribute` 来测试设备的 IPC 功能。

注意：
- 不保证返回到 `*pdptr` 的地址。特别是，多个进程可能不会针对相同的 `handle` 收到相同的地址。

```c
HGresult hgIpcOpenMemHandle(HGdeviceptr* pdptr, HGipcMemHandle handle, unsigned int Flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pdptr | out | 返回的设备指针 |
| handle | in | 要打开的 `HGipcMemHandle` |
| Flags | in | 此操作的标志。必须指定为 `HG_IPC_MEM_LAZY_ENABLE_PEER_ACCESS` |

错误码：HGGC_SUCCESS、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_MAP_FAILED、HGGC_ERROR_INVALID_HANDLE、HGGC_ERROR_TOO_MANY_PEERS、HGGC_ERROR_INVALID_VALUE

---

#### 27. hgIpcCloseMemHandle {#hgipcclosememhandle}

关闭由 `hgIpcOpenMemHandle` 映射的内存。

将 `hgIpcOpenMemHandle` 返回的内存的引用计数减 1。当引用计数达到 0 时，此 API 会取消映射该内存。导出进程中的原始分配以及其他进程中导入的映射不受影响。

如果这是使用对等访问资源的最后一个映射，则用于启用对等访问的所有资源都将被释放。

IPC 功能仅限于在 Linux 操作系统上支持统一寻址的设备。开发者可以通过使用 `HG_DEVICE_ATTRIBUTE_IPC_EVENT_SUPPORTED` 调用 `hgDeviceGetAttribute` 来测试设备的 IPC 功能。

```c
HGresult hgIpcCloseMemHandle(HGdeviceptr dptr)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dptr | in | `hgIpcOpenMemHandle` 返回的设备指针 |

错误码：HGGC_SUCCESS、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_MAP_FAILED、HGGC_ERROR_INVALID_HANDLE、HGGC_ERROR_INVALID_VALUE

---

#### 28. hgDeviceGetByPCIBusId {#hgdevicegetbypcibusid}

根据给定的 PCI 总线 ID 字符串返回对应的设备句柄。

```c
HGresult hgDeviceGetByPCIBusId(HGdevice* dev, const char* pciBusId)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dev | out | 返回的设备句柄 |
| pciBusId | in | 以下格式之一的字符串：`[domain]:[bus]:[device].[function]`、`[domain]:[bus]:[device]` 或 `[bus]:[device].[function]`，其中 `domain`、`bus`、`device` 和 `function` 均为十六进制值 |

错误码：HGGC_SUCCESS、HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_DEVICE

---

#### 29. hgDeviceGetPCIBusId {#hgdevicegetpcibusid}

在 `pciBusId` 指向的以 NULL 结尾的字符串中返回一个标识设备 `dev` 的 ASCII 字符串。`len` 指定可能返回的字符串的最大长度。

```c
HGresult hgDeviceGetPCIBusId(char* pciBusId, int len, HGdevice dev)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pciBusId | out | 以下格式的设备返回标识符字符串：`[domain]:[bus]:[device].[function]`，其中 `domain`、`bus`、`device` 和 `function` 均为十六进制值。`pciBusId` 应足够大以存储 13 个字符，包括 NULL 终止符 |
| len | in | 存储到 `pciBusId` 中字符串的最大长度 |
| dev | in | 要获取标识符字符串的设备 |

错误码：HGGC_SUCCESS、HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_DEVICE

---

### 5.2. 内存复制 {#memcpy}

本模块提供**内存复制（Memory Copy）** 接口，支持主机↔设备、设备↔设备、数组↔线性内存之间的一维/二维/三维数据传输，包含同步与异步变体。

本节介绍低级 HGGC 驱动程序应用程序编程接口的内存复制函数。

#### 1. 接口一览 {#接口一览}

| 函数 | 用途 |
|------|------|
| [hgMemcpy](#hgmemcpy) | 内存复制 |
| [hgMemcpyPeer](#hgmemcpypeer) | 上下文间设备内存复制 |
| [hgMemcpyHtoD](#hgmemcpyhtod) | 主机到设备内存复制 |
| [hgMemcpyDtoH](#hgmemcpydtoh) | 设备到主机内存复制 |
| [hgMemcpyDtoD](#hgmemcpydtod) | 设备到设备内存复制 |
| [hgMemcpy2D](#hgmemcpy2d) | 二维数组内存复制 |
| [hgMemcpy2DUnaligned](#hgmemcpy2dunaligned) | 二维数组内存复制（未对齐） |
| [hgMemcpy3D](#hgmemcpy3d) | 三维数组内存复制 |
| [hgMemcpy3DPeer](#hgmemcpy3dpeer) | 上下文间三维内存复制 |
| [hgMemcpyHtoDAsync](#hgmemcpyhtodasync) | 异步主机到设备内存复制 |
| [hgMemcpyDtoHAsync](#hgmemcpydtohasync) | 异步设备到主机内存复制 |
| [hgMemcpyDtoDAsync](#hgmemcpydtodasync) | 异步设备到设备内存复制 |
| [hgMemcpy2DAsync](#hgmemcpy2dasync) | 异步二维数组内存复制 |
| [hgMemcpy3DAsync](#hgmemcpy3dasync) | 异步三维数组内存复制 |
| [hgMemcpy3DPeerAsync](#hgmemcpy3dpeerasync) | 异步上下文间三维内存复制 |
| [hgMemcpyPeerAsync](#hgmemcpypeerasync) | 异步上下文间设备内存复制 |
| [hgMemcpyAsync](#hgmemcpyasync) | 基于统一虚拟地址的异步内存复制 |

---

#### 2. hgMemcpy {#hgmemcpy}

复制设备内存。复制从源地址 srcDevice 复制 ByteCount 字节到目标地址 dstDevice。此函数同步。

```c
HGresult hgMemcpy(HGdeviceptr dstDevice,
                  HGdeviceptr srcDevice,
                  size_t ByteCount)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dstDevice | in | 目标设备指针 |
| srcDevice | in | 源设备指针 |
| ByteCount | in | 要复制的字节数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemAlloc](#hgmemalloc), [hgMemAllocHost](#hgmemallochost), [hgMemAllocManaged](#hgmemallocmanaged), [hgMemAllocPitch](#hgmemallocpitch), [hgMemFree](#hgmemfree), [hgMemFreeHost](#hgmemfreehost), [hgMemHostAlloc](#hgmemhostalloc), [hgMemHostRegister](#hgmemhostregister), [hgMemHostUnregister](#hgmemhostunregister), [hggcMemcpy](04_runtime_api.md)

---

#### 3. hgMemcpyPeer {#hgmemcpypeer}

在两个不同上下文的设备之间执行内存复制。

```c
HGresult hgMemcpyPeer(HGdeviceptr dstDevice,
                      HGcontext dstContext,
                      HGdeviceptr srcDevice,
                      HGcontext srcContext,
                      size_t ByteCount)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dstDevice | in | 目标设备指针 |
| dstContext | in | 目标上下文 |
| srcDevice | in | 源设备指针 |
| srcContext | in | 源上下文 |
| ByteCount | in | 要复制的字节数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemcpyPeerAsync](#hgmemcpypeerasync), [hggcMemcpyPeer](04_runtime_api.md)

---

#### 4. hgMemcpyHtoD {#hgmemcpyhtod}

从主机复制到设备。

```c
HGresult hgMemcpyHtoD(HGdeviceptr dstDevice,
                      const void* srcHost,
                      size_t ByteCount)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dstDevice | in | 目标设备指针 |
| srcHost | in | 源主机指针 |
| ByteCount | in | 要复制的字节数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemcpyDtoD](#hgmemcpydtod), [hgMemcpyDtoH](#hgmemcpydtoh), [hggcMemcpy](04_runtime_api.md)

---

#### 5. hgMemcpyDtoH {#hgmemcpydtoh}

从设备复制到主机。

```c
HGresult hgMemcpyDtoH(void* dstHost, HGdeviceptr srcDevice, size_t ByteCount)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dstHost | in | 目标主机指针 |
| srcDevice | in | 源设备指针 |
| ByteCount | in | 要复制的字节数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemcpyDtoD](#hgmemcpydtod), [hgMemcpyHtoD](#hgmemcpyhtod), [hggcMemcpy](04_runtime_api.md)

---

#### 6. hgMemcpyDtoD {#hgmemcpydtod}

从设备复制到设备。

```c
HGresult hgMemcpyDtoD(HGdeviceptr dstDevice,
                      HGdeviceptr srcDevice,
                      size_t ByteCount)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dstDevice | in | 目标设备指针 |
| srcDevice | in | 源设备指针 |
| ByteCount | in | 要复制的字节数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemcpyDtoH](#hgmemcpydtoh), [hgMemcpyHtoD](#hgmemcpyhtod), [hggcMemcpy](04_runtime_api.md)

---

#### 7. hgMemcpy2D {#hgmemcpy2d}

根据 pCopy 中指定的 HGGC_MEMCPY2D 结构执行二维内存复制。如果源内存类型是 HG_MEMORYTYPE_HOST 或 HG_MEMORYTYPE_DEVICE，则 srcPitch 和 dstPitch 各自指定源和目标的间距。如果源内存类型是数组，则源或目标（取决于内存类型）必须使用相应的数组创建接口创建。srcY 和 dstY 指定起始 y 坐标。srcXInBytes 和 dstXInBytes 指定起始 x 坐标（以字节为单位）。Height 指定要复制的行数。WidthInBytes 指定要复制的总字节数。

```c
HGresult hgMemcpy2D(const HGGC_MEMCPY2D* pCopy)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pCopy | in | 复制参数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemAlloc](#hgmemalloc), [hgMemAllocHost](#hgmemallochost), [hgMemAllocManaged](#hgmemallocmanaged), [hgMemAllocPitch](#hgmemallocpitch), [hgMemFree](#hgmemfree), [hgMemFreeHost](#hgmemfreehost), [hgMemHostAlloc](#hgmemhostalloc), [hgMemHostRegister](#hgmemhostregister), [hgMemHostUnregister](#hgmemhostunregister), [hggcMemcpy2D](04_runtime_api.md)

---

#### 8. hgMemcpy2DUnaligned {#hgmemcpy2dunaligned}

二维内存复制操作，不要求对齐。

```c
HGresult hgMemcpy2DUnaligned(const HGGC_MEMCPY2D* pCopy)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pCopy | in | 复制参数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemcpy2D](#hgmemcpy2d), [hggcMemcpy2D](04_runtime_api.md)

---

#### 9. hgMemcpy3D {#hgmemcpy3d}

三维内存复制操作。

```c
HGresult hgMemcpy3D(const HGGC_MEMCPY3D* pCopy)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pCopy | in | 复制参数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemAlloc](#hgmemalloc), [hgMemAllocHost](#hgmemallochost), [hgMemAllocManaged](#hgmemallocmanaged), [hgMemAllocPitch](#hgmemallocpitch), [hgMemFree](#hgmemfree), [hgMemFreeHost](#hgmemfreehost), [hgMemHostAlloc](#hgmemhostalloc), [hgMemHostRegister](#hgmemhostregister), [hgMemHostUnregister](#hgmemhostunregister), [hggcMemcpy3D](04_runtime_api.md)

---

#### 10. hgMemcpy3DPeer {#hgmemcpy3dpeer}

在两个不同上下文的设备之间执行三维内存复制。

```c
HGresult hgMemcpy3DPeer(const HGGC_MEMCPY3D_PEER* pCopy)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pCopy | in | 复制参数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemcpy3DPeerAsync](#hgmemcpy3dpeerasync), [hggcMemcpy3DPeer](04_runtime_api.md)

---

#### 11. hgMemcpyHtoDAsync {#hgmemcpyhtodasync}

异步从主机复制到设备。

```c
HGresult hgMemcpyHtoDAsync(HGdeviceptr dstDevice,
                           const void* srcHost,
                           size_t ByteCount,
                           HGstream hStream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dstDevice | in | 目标设备指针 |
| srcHost | in | 源主机指针 |
| ByteCount | in | 要复制的字节数 |
| hStream | in | 流标识符 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemcpyHtoD](#hgmemcpyhtod), [hggcMemcpyHtoDAsync](04_runtime_api.md)

---

#### 12. hgMemcpyDtoHAsync {#hgmemcpydtohasync}

异步从设备复制到主机。

```c
HGresult hgMemcpyDtoHAsync(void* dstHost,
                           HGdeviceptr srcDevice,
                           size_t ByteCount,
                           HGstream hStream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dstHost | in | 目标主机指针 |
| srcDevice | in | 源设备指针 |
| ByteCount | in | 要复制的字节数 |
| hStream | in | 流标识符 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemcpyDtoH](#hgmemcpydtoh), [hggcMemcpyDtoHAsync](04_runtime_api.md)

---

#### 13. hgMemcpyDtoDAsync {#hgmemcpydtodasync}

异步从设备复制到设备。

```c
HGresult hgMemcpyDtoDAsync(HGdeviceptr dstDevice,
                           HGdeviceptr srcDevice,
                           size_t ByteCount,
                           HGstream hStream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dstDevice | in | 目标设备指针 |
| srcDevice | in | 源设备指针 |
| ByteCount | in | 要复制的字节数 |
| hStream | in | 流标识符 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemcpyDtoD](#hgmemcpydtod), [hggcMemcpyDtoDAsync](04_runtime_api.md)

---

#### 14. hgMemcpy2DAsync {#hgmemcpy2dasync}

异步二维内存复制操作。

```c
HGresult hgMemcpy2DAsync(const HGGC_MEMCPY2D* pCopy, HGstream hStream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pCopy | in | 复制参数 |
| hStream | in | 流标识符 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemcpy2D](#hgmemcpy2d), [hggcMemcpy2DAsync](04_runtime_api.md)

---

#### 15. hgMemcpy3DAsync {#hgmemcpy3dasync}

异步三维内存复制操作。

```c
HGresult hgMemcpy3DAsync(const HGGC_MEMCPY3D* pCopy, HGstream hStream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pCopy | in | 复制参数 |
| hStream | in | 流标识符 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemcpy3D](#hgmemcpy3d), [hggcMemcpy3DAsync](04_runtime_api.md)

---

#### 16. hgMemcpy3DPeerAsync {#hgmemcpy3dpeerasync}

异步在两个不同上下文的设备之间执行三维内存复制。

```c
HGresult hgMemcpy3DPeerAsync(const HGGC_MEMCPY3D_PEER* pCopy, HGstream hStream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pCopy | in | 复制参数 |
| hStream | in | 流标识符 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemcpy3DPeer](#hgmemcpy3dpeer), [hggcMemcpy3DPeerAsync](04_runtime_api.md)

---

#### 17. hgMemcpyPeerAsync {#hgmemcpypeerasync}

异步在两个不同上下文的设备之间执行内存复制。

```c
HGresult hgMemcpyPeerAsync(HGdeviceptr dstDevice,
                           HGcontext dstContext,
                           HGdeviceptr srcDevice,
                           HGcontext srcContext,
                           size_t ByteCount,
                           HGstream hStream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dstDevice | in | 目标设备指针 |
| dstContext | in | 目标上下文 |
| srcDevice | in | 源设备指针 |
| srcContext | in | 源上下文 |
| ByteCount | in | 要复制的字节数 |
| hStream | in | 流标识符 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemcpyPeer](#hgmemcpypeer), [hggcMemcpyPeerAsync](04_runtime_api.md)

---

#### 18. hgMemcpyAsync {#hgmemcpyasync}

在两个指针之间复制数据。

`dst` 和 `src` 分别是目标和源的基址指针，`ByteCount` 指定要复制的字节数。

请注意，此函数从指针值推断传输类型（主机到主机、主机到设备、设备到设备或设备到主机）。此函数仅允许在支持统一寻址的上下文中使用。

```c
HGresult hgMemcpyAsync(HGdeviceptr dst,
                       HGdeviceptr src,
                       size_t ByteCount,
                       HGstream hStream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dst | in | 统一虚拟地址空间中的目标指针 |
| src | in | 统一虚拟地址空间中的源指针 |
| ByteCount | in | 要复制的字节数 |
| hStream | in | 流标识符 |

错误码：HGGC_SUCCESS、HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_HANDLE

---

### 5.3. 内存填充 {#memset}

本模块提供**内存填充（Memory Fill）** 接口，用于将设备内存块设置为指定值，支持 8/16/32 位宽度的一维与二维填充，以及对应的异步变体。

本节介绍低级 HGGC 驱动程序应用程序编程接口的内存填充函数。

#### 1. 接口一览 {#接口一览}

| 函数 | 用途 |
|------|------|
| [hgMemsetD8](#hgmemsetd8) | 以 8 位值填充一维设备内存 |
| [hgMemsetD16](#hgmemsetd16) | 以 16 位值填充一维设备内存 |
| [hgMemsetD32](#hgmemsetd32) | 以 32 位值填充一维设备内存 |
| [hgMemsetD2D8](#hgmemsetd2d8) | 以 8 位值填充二维设备内存 |
| [hgMemsetD2D16](#hgmemsetd2d16) | 以 16 位值填充二维设备内存 |
| [hgMemsetD2D32](#hgmemsetd2d32) | 以 32 位值填充二维设备内存 |
| [hgMemsetD8Async](#hgmemsetd8async) | 异步以 8 位值填充一维设备内存 |
| [hgMemsetD16Async](#hgmemsetd16async) | 异步以 16 位值填充一维设备内存 |
| [hgMemsetD32Async](#hgmemsetd32async) | 异步以 32 位值填充一维设备内存 |
| [hgMemsetD2D8Async](#hgmemsetd2d8async) | 异步以 8 位值填充二维设备内存 |
| [hgMemsetD2D16Async](#hgmemsetd2d16async) | 异步以 16 位值填充二维设备内存 |
| [hgMemsetD2D32Async](#hgmemsetd2d32async) | 异步以 32 位值填充二维设备内存 |

---

#### 2. hgMemsetD8 {#hgmemsetd8}

将 N 个 8 位值设置为指定值 uc。

```c
HGresult hgMemsetD8(HGdeviceptr dstDevice, unsigned char uc, size_t N)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dstDevice | in | 目标设备指针 |
| uc | in | 要设置的值 |
| N | in | 元素数量 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemsetD16](#hgmemsetd16), [hgMemsetD16Async](#hgmemsetd16async), [hgMemsetD32](#hgmemsetd32), [hgMemsetD32Async](#hgmemsetd32async), [hgMemsetD8Async](#hgmemsetd8async), [hggcMemset](04_runtime_api.md)

---

#### 3. hgMemsetD16 {#hgmemsetd16}

将 N 个 16 位值设置为指定值 us。dstDevice 指针必须两字节对齐。

```c
HGresult hgMemsetD16(HGdeviceptr dstDevice, unsigned short us, size_t N)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dstDevice | in | 目标设备指针 |
| us | in | 要设置的值 |
| N | in | 元素数量 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemsetD8](#hgmemsetd8), [hgMemsetD16Async](#hgmemsetd16async), [hgMemsetD32](#hgmemsetd32), [hggcMemset](04_runtime_api.md)

---

#### 4. hgMemsetD32 {#hgmemsetd32}

将 N 个 32 位值设置为指定值 ui。dstDevice 指针必须四字节对齐。

```c
HGresult hgMemsetD32(HGdeviceptr dstDevice, unsigned int ui, size_t N)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dstDevice | in | 目标设备指针 |
| ui | in | 要设置的值 |
| N | in | 元素数量 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemsetD8](#hgmemsetd8), [hgMemsetD16](#hgmemsetd16), [hgMemsetD16Async](#hgmemsetd16async), [hgMemsetD32Async](#hgmemsetd32async), [hggcMemset](04_runtime_api.md)

---

#### 5. hgMemsetD2D8 {#hgmemsetd2d8}

将二维内存范围的 Width 个 8 位值设置为指定值 uc。Height 指定要设置的行数，dstPitch 指定每行之间的字节数。当间距是 hgMemAllocPitch() 返回的间距时，此函数执行最快。

```c
HGresult hgMemsetD2D8(HGdeviceptr dstDevice,
                      size_t dstPitch,
                      unsigned char uc,
                      size_t Width,
                      size_t Height)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dstDevice | in | 目标设备指针 |
| dstPitch | in | 目标设备指针的间距（当 Height 为 1 时未使用） |
| uc | in | 要设置的值 |
| Width | in | 行的宽度 |
| Height | in | 行数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemsetD2D16](#hgmemsetd2d16), [hgMemsetD2D16Async](#hgmemsetd2d16async), [hgMemsetD2D32](#hgmemsetd2d32), [hgMemsetD2D32Async](#hgmemsetd2d32async), [hggcMemset2D](04_runtime_api.md)

---

#### 6. hgMemsetD2D16 {#hgmemsetd2d16}

将二维内存范围的 Width 个 16 位值设置为指定值 us。Height 指定要设置的行数，dstPitch 指定每行之间的字节数。dstDevice 指针和 dstPitch 偏移量必须两字节对齐。当间距是 hgMemAllocPitch() 返回的间距时，此函数执行最快。

```c
HGresult hgMemsetD2D16(HGdeviceptr dstDevice,
                       size_t dstPitch,
                       unsigned short us,
                       size_t Width,
                       size_t Height)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dstDevice | in | 目标设备指针 |
| dstPitch | in | 目标设备指针的间距（当 Height 为 1 时未使用） |
| us | in | 要设置的值 |
| Width | in | 行的宽度 |
| Height | in | 行数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemsetD2D8](#hgmemsetd2d8), [hgMemsetD2D16Async](#hgmemsetd2d16async), [hgMemsetD2D32](#hgmemsetd2d32), [hggcMemset2D](04_runtime_api.md)

---

#### 7. hgMemsetD2D32 {#hgmemsetd2d32}

将二维内存范围的 Width 个 32 位值设置为指定值 ui。Height 指定要设置的行数，dstPitch 指定每行之间的字节数。dstDevice 指针和 dstPitch 偏移量必须四字节对齐。当间距是 hgMemAllocPitch() 返回的间距时，此函数执行最快。

```c
HGresult hgMemsetD2D32(HGdeviceptr dstDevice,
                       size_t dstPitch,
                       unsigned int ui,
                       size_t Width,
                       size_t Height)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dstDevice | in | 目标设备指针 |
| dstPitch | in | 目标设备指针的间距（当 Height 为 1 时未使用） |
| ui | in | 要设置的值 |
| Width | in | 行的宽度 |
| Height | in | 行数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemsetD2D8](#hgmemsetd2d8), [hgMemsetD2D16](#hgmemsetd2d16), [hgMemsetD2D32Async](#hgmemsetd2d32async), [hggcMemset2D](04_runtime_api.md)

---

#### 8. hgMemsetD8Async {#hgmemsetd8async}

设置内存范围。

```c
HGresult hgMemsetD8Async(HGdeviceptr dstDevice,
                         unsigned char uc,
                         size_t N,
                         HGstream hStream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dstDevice | in | 目标设备指针 |
| uc | in | 要设置的值 |
| N | in | 元素数量 |
| hStream | in | 流标识符 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemsetD8](#hgmemsetd8), [hggcMemsetAsync](04_runtime_api.md)

---

#### 9. hgMemsetD16Async {#hgmemsetd16async}

设置内存范围。

```c
HGresult hgMemsetD16Async(HGdeviceptr dstDevice,
                          unsigned short us,
                          size_t N,
                          HGstream hStream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dstDevice | in | 目标设备指针 |
| us | in | 要设置的值 |
| N | in | 元素数量 |
| hStream | in | 流标识符 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemsetD16](#hgmemsetd16), [hggcMemsetAsync](04_runtime_api.md)

---

#### 10. hgMemsetD32Async {#hgmemsetd32async}

设置内存范围。

```c
HGresult hgMemsetD32Async(HGdeviceptr dstDevice,
                          unsigned int ui,
                          size_t N,
                          HGstream hStream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dstDevice | in | 目标设备指针 |
| ui | in | 要设置的值 |
| N | in | 元素数量 |
| hStream | in | 流标识符 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemsetD32](#hgmemsetd32), [hggcMemsetAsync](04_runtime_api.md)

---

#### 11. hgMemsetD2D8Async {#hgmemsetd2d8async}

设置二维内存范围。

```c
HGresult hgMemsetD2D8Async(HGdeviceptr dstDevice,
                           size_t dstPitch,
                           unsigned char uc,
                           size_t Width,
                           size_t Height,
                           HGstream hStream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dstDevice | in | 目标设备指针 |
| dstPitch | in | 目标设备指针的间距（当 Height 为 1 时未使用） |
| uc | in | 要设置的值 |
| Width | in | 行的宽度 |
| Height | in | 行数 |
| hStream | in | 流标识符 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemsetD2D8](#hgmemsetd2d8), [hggcMemset2DAsync](04_runtime_api.md)

---

#### 12. hgMemsetD2D16Async {#hgmemsetd2d16async}

设置二维内存范围。

```c
HGresult hgMemsetD2D16Async(HGdeviceptr dstDevice,
                            size_t dstPitch,
                            unsigned short us,
                            size_t Width,
                            size_t Height,
                            HGstream hStream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dstDevice | in | 目标设备指针 |
| dstPitch | in | 目标设备指针的间距（当 Height 为 1 时未使用） |
| us | in | 要设置的值 |
| Width | in | 行的宽度 |
| Height | in | 行数 |
| hStream | in | 流标识符 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemsetD2D16](#hgmemsetd2d16), [hggcMemset2DAsync](04_runtime_api.md)

---

#### 13. hgMemsetD2D32Async {#hgmemsetd2d32async}

设置二维内存范围。

```c
HGresult hgMemsetD2D32Async(HGdeviceptr dstDevice,
                            size_t dstPitch,
                            unsigned int ui,
                            size_t Width,
                            size_t Height,
                            HGstream hStream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dstDevice | in | 目标设备指针 |
| dstPitch | in | 目标设备指针的间距（当 Height 为 1 时未使用） |
| ui | in | 要设置的值 |
| Width | in | 行的宽度 |
| Height | in | 行数 |
| hStream | in | 流标识符 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

另见：[hgMemsetD2D32](#hgmemsetd2d32), [hggcMemset2DAsync](04_runtime_api.md)

---

### 5.4. 虚拟内存管理 {#vmm}

本模块提供**虚拟内存管理**接口，允许显式分配/释放虚拟地址范围、映射物理内存到虚拟地址、以及设置访问属性。

本节介绍低级 HGGC 驱动程序应用程序编程接口的虚拟内存管理函数。

#### 1. 接口一览 {#接口一览}

| 函数 | 用途 |
|------|------|
| [hgMemAddressFree](#hgmemaddressfree) | 释放地址范围预留 |
| [hgMemAddressReserve](#hgmemaddressreserve) | 分配地址范围预留 |
| [hgMemCreate](#hgmemcreate) | 创建表示给定大小内存分配的 HGGC 内存句柄，该大小由给定属性描述 |
| [hgMemExportToShareableHandle](#hgmemexporttoshareablehandle) | 将分配导出为请求的可共享句柄类型 |
| [hgMemGetAccess](#hgmemgetaccess) | 获取为给定 `location` 和 `ptr` 设置的访问 `flags` |
| [hgMemGetAllocationGranularity](#hgmemgetallocationgranularity) | 计算最小或推荐的粒度 |
| [hgMemGetAllocationPropertiesFromHandle](#hgmemgetallocationpropertiesfromhandle) | 检索定义此句柄属性的属性结构的内容 |
| [hgMemImportFromShareableHandle](#hgmemimportfromshareablehandle) | 从请求的可共享句柄类型导入分配 |
| [hgMemMap](#hgmemmap) | 将分配句柄映射到预留的虚拟地址范围 |
| [hgMemRelease](#hgmemrelease) | 释放表示通过 hgMemCreate 之前分配的内存分配的内存句柄 |
| [hgMemRetainAllocationHandle](#hgmemretainallocationhandle) | 给定地址 `addr`，返回支持内存分配的分配句柄 |
| [hgMemSetAccess](#hgmemsetaccess) | 为给定虚拟地址范围内的每个 `desc` 中指定的位置设置访问标志 |
| [hgMemUnmap](#hgmemunmap) | 取消映射给定地址范围的支持内存 |

---

#### 2. hgMemAddressFree {#hgmemaddressfree}

释放由 hgMemAddressReserve 预留的虚拟地址范围。`size` 必须与传递给 memAddressReserve 的大小匹配，`ptr` 必须与 memAddressReserve 返回的值匹配。

```c
HGresult hgMemAddressFree (HGdeviceptr ptr, size_t size)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| ptr | in | 要释放的虚拟地址范围起始地址 |
| size | in | 要释放的虚拟地址区域大小 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_PERMITTED、HGGC_ERROR_NOT_SUPPORTED

---

#### 3. hgMemAddressReserve {#hgmemaddressreserve}

根据给定参数预留虚拟地址范围，在 `ptr` 中返回范围的起始地址。此 API 需要支持 UVA 的系统。`size` 和 `addr` 参数必须是主机页面大小的倍数，`alignment` 必须是 2 的幂或零表示默认对齐。如果 `addr` 为 0，则驱动程序选择放置预留起始地址的位置；而当 `addr` 非零时，驱动程序将其作为放置预留位置的提示。

```c
HGresult hgMemAddressReserve (HGdeviceptr* ptr,
                              size_t size,
                              size_t alignment,
                              HGdeviceptr addr,
                              unsigned long long flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| ptr | out | 返回分配的虚拟地址范围起始指针 |
| size | in | 请求的预留虚拟地址范围大小 |
| alignment | in | 请求的预留虚拟地址范围对齐方式 |
| addr | in | 地址范围起始的提示地址 |
| flags | in | 当前未使用，必须为零 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_OUT_OF_MEMORY、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_PERMITTED、HGGC_ERROR_NOT_SUPPORTED

---

#### 4. hgMemCreate {#hgmemcreate}

在通过 `prop` 结构指定的目标设备上创建内存分配。创建的分配将没有任何设备或主机映射。可以通过 [hgMemMap](#hgmemmap) 将分配的通用内存 `handle` 映射到调用进程的地址空间。此句柄不能直接传输给其他进程（请参阅 [hgMemExportToShareableHandle](#hgmemexporttoshareablehandle)）。此分配的 `size` 必须是使用 [HG_MEM_ALLOC_GRANULARITY_MINIMUM](#driver-data-types) 标志调用 [hgMemGetAllocationGranularity](#hgmemgetallocationgranularity) 返回值的倍数。要创建不针对任何特定 NUMA 节点的 CPU 分配，应用程序必须将 HGmemAllocationProp::HGmemLocation::type 设置为 [HG_MEM_LOCATION_TYPE_HOST](#driver-data-types)。对于 HOST 分配，将忽略 HGmemAllocationProp::HGmemLocation::id。HOST 分配不支持 IPC，HGmemAllocationProp::requestedHandleTypes 必须为 0，任何其他值都将导致 [HGGC_ERROR_INVALID_VALUE](#driver-data-types)。要创建针对特定主机 NUMA 节点的 CPU 分配，应用程序必须将 HGmemAllocationProp::HGmemLocation::type 设置为 [HG_MEM_LOCATION_TYPE_HOST_NUMA](#driver-data-types) 并且 HGmemAllocationProp::HGmemLocation::id 必须指定 CPU 的 NUMA ID。在 NUMA 不可用的系统上，必须将 HGmemAllocationProp::HGmemLocation::id 设置为 0。将 [HG_MEM_LOCATION_TYPE_HOST_NUMA_CURRENT](#driver-data-types) 指定为 HGmemLocation::type 将导致 [HGGC_ERROR_INVALID_VALUE](#driver-data-types)。

打算使用 [HG_MEM_HANDLE_TYPE_FABRIC](#driver-data-types) 内存共享的应用程序必须确保：(1) alixpu-caps-imex-channels 字符设备由驱动程序创建并列入 /proc/devices (2) 启动应用程序的用户可以访问至少一个 IMEX 通道文件。

当导出方和导入方 HGGC 进程已被授予访问同一 IMEX 通道的权限时，它们可以安全地共享内存。

IMEX 通道安全模型基于每个用户工作。这意味着如果用户有权访问有效的 IMEX 通道，则该用户下的所有进程都可以共享内存。当需要多用户隔离时，每个用户需要一个单独的 IMEX 通道。

如果 HGmemAllocationProp::allocFlags::usage 包含 [HG_MEM_CREATE_USAGE_TILE_POOL](#driver-data-types) 标志，则内存分配仅旨在用作稀疏 HGGC 数组和稀疏 HGGC mipmapped 数组的备用 tile 池。

```c
HGresult hgMemCreate (HGmemGenericAllocationHandle* handle,
                      size_t size,
                      const HGmemAllocationProp* prop,
                      unsigned long long flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| handle | out | 返回的句柄值。所有对此分配的操作都将使用此句柄执行。 |
| size | in | 请求的分配大小 |
| prop | in | 要创建的分配的属性。 |
| flags | in | 供将来使用的标志，现在必须为零。 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_OUT_OF_MEMORY、HGGC_ERROR_INVALID_DEVICE、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_PERMITTED、HGGC_ERROR_NOT_SUPPORTED

---

#### 5. hgMemExportToShareableHandle {#hgmemexporttoshareablehandle}

给定 HGGC 内存句柄，创建一个可共享的内存分配句柄，可用于与其他进程共享内存。接收进程可以使用 [hgMemImportFromShareableHandle](#hgmemimportfromshareablehandle) 将可共享句柄转换回 HGGC 内存句柄，并使用 [hgMemMap](#hgmemmap) 将其映射。实现此句柄是什么以及如何传输的定义由 `handleType` 中请求的句柄类型决定。

一旦所有可共享句柄关闭且分配被释放，引用分配的已分配内存将被释放回操作系统，此后使用 HGGC 句柄将导致未定义行为。

此 API 也可与其他支持从可共享类型导入内存的 API（如 Vulkan、OpenGL）结合使用。

```c
HGresult hgMemExportToShareableHandle (void* shareableHandle,
                                       HGmemGenericAllocationHandle handle,
                                       HGmemAllocationHandleType handleType,
                                       unsigned long long flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| shareableHandle | in | 存储请求句柄类型的指针 |
| handle | in | 内存分配的 HGGC 句柄 |
| handleType | out | 请求的可共享句柄类型（定义 `shareableHandle` 输出参数的类型和大小） |
| flags | in | 预留，必须为零 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_PERMITTED、HGGC_ERROR_NOT_SUPPORTED

---

#### 6. hgMemGetAccess {#hgmemgetaccess}

获取为给定 `location` 和 `ptr` 设置的访问 `flags`。

```c
HGresult hgMemGetAccess (unsigned long long* flags,
                         const HGmemLocation* location,
                         HGdeviceptr ptr)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| flags | in | 为此位置设置的标志 |
| location | in | 要检查标志的位置 |
| ptr | in | 要检查访问标志的地址 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_DEVICE、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_PERMITTED、HGGC_ERROR_NOT_SUPPORTED

---

#### 7. hgMemGetAllocationGranularity {#hgmemgetallocationgranularity}

计算给定分配规范的最小或推荐粒度，并在 `granularity` 中返回。此粒度可用作对齐、大小或地址映射的倍数。

```c
HGresult hgMemGetAllocationGranularity (size_t* granularity,
                                        const HGmemAllocationProp* prop,
                                        HGmemAllocationGranularity_flags option)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| granularity | out | 返回的粒度。 |
| prop | in | 要确定粒度的属性 |
| option | out | 决定返回哪种粒度 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_PERMITTED、HGGC_ERROR_NOT_SUPPORTED

---

#### 8. hgMemGetAllocationPropertiesFromHandle {#hgmemgetallocationpropertiesfromhandle}

检索定义此句柄属性的属性结构的内容。

```c
HGresult hgMemGetAllocationPropertiesFromHandle (HGmemAllocationProp* prop,
                                                 HGmemGenericAllocationHandle handle)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| prop | in | 将保存此句柄信息的属性结构指针 |
| handle | in | 要执行查询的句柄 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_PERMITTED、HGGC_ERROR_NOT_SUPPORTED

---

#### 9. hgMemImportFromShareableHandle {#hgmemimportfromshareablehandle}

如果当前进程不支持此可共享句柄描述的内存，此 API 将报错为 [HGGC_ERROR_NOT_SUPPORTED](#driver-data-types)。

如果 `shHandleType` 是 [HG_MEM_HANDLE_TYPE_FABRIC](#driver-data-types) 并且导入进程未被授予与导出进程相同的 IMEX 通道访问权限，此 API 将报错为 [HGGC_ERROR_NOT_PERMITTED](#driver-data-types)。

```c
HGresult hgMemImportFromShareableHandle (HGmemGenericAllocationHandle* handle,
                                         void* osHandle,
                                         HGmemAllocationHandleType shHandleType)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| handle | in | 内存分配的 HGGC 内存句柄。 |
| osHandle | in | 要导入的表示内存分配的可共享句柄。 |
| shHandleType | in | 导出句柄的句柄类型 [HGmemAllocationHandleType](#driver-data-types)。 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_PERMITTED、HGGC_ERROR_NOT_SUPPORTED

---

#### 10. hgMemMap {#hgmemmap}

将 `handle` 表示的从字节 `offset` 开始的 `size` 字节内存映射到地址范围 [`addr`, `addr` + `size`]。此范围必须是之前用 [hgMemAddressReserve](#hgmemaddressreserve) 预留的地址预留，并且 `offset` + `size` 必须小于内存分配的大小。`ptr`、`size` 和 `offset` 都必须是使用 [HG_MEM_ALLOC_GRANULARITY_MINIMUM](#driver-data-types) 标志调用 [hgMemGetAllocationGranularity](#hgmemgetallocationgranularity) 返回值的倍数。如果 `handle` 表示多播对象，`ptr`、`size` 和 `offset` 必须对齐到使用 HG_MULTICAST_MINIMUM_GRANULARITY 标志调用 hgMulticastGetGranularity 返回的值。为获得最佳性能，将 `ptr`、`size` 和 `offset` 对齐到使用 HG_MULTICAST_RECOMMENDED_GRANULARITY 标志调用 hgMulticastGetGranularity 返回的值。

当 `handle` 表示多播对象时，如果系统配置处于非法状态，此调用可能返回 HGGC_ERROR_ILLEGAL_STATE。在这种情况下，要继续使用多播，请验证系统配置处于有效状态且所有必需的驱动程序守护进程正常运行。

请注意，调用 [hgMemMap](#hgmemmap) 不会使地址可访问，调用者需要通过调用 [hgMemSetAccess](#hgmemsetaccess) 更新连续映射 VA 范围的可达性。

一旦接收进程从 [hgMemImportFromShareableHandle](#hgmemimportfromshareablehandle) 获取可共享内存句柄，该进程必须使用 [hgMemMap](#hgmemmap) 将内存映射到其地址范围，然后才能使用 [hgMemSetAccess](#hgmemsetaccess) 设置可达性。

[hgMemMap](#hgmemmap) 只能创建对当前未映射的 VA 范围预留的映射。

```c
HGresult hgMemMap (HGdeviceptr ptr,
                   size_t size,
                   size_t offset,
                   HGmemGenericAllocationHandle handle,
                   unsigned long long flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| ptr | in | 内存将映射到的地址。 |
| size | in | 内存映射的大小。 |
| offset | in | 从中开始映射的 `handle` 表示内存的偏移量。注意：目前必须为零。 |
| handle | in | 可共享内存的句柄 |
| flags | in | 供将来使用的标志，现在必须为零。 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_DEVICE、HGGC_ERROR_OUT_OF_MEMORY、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_PERMITTED、HGGC_ERROR_NOT_SUPPORTED、HGGC_ERROR_ILLEGAL_STATE

---

#### 11. hgMemRelease {#hgmemrelease}

释放之前在设备上通过 hgMemCreate 分配的内存。

当所有对内存的未完成映射被取消映射且对句柄的所有未完成引用（包括其可共享对应项）也被释放时，内存分配将被释放。当仍有使用此句柄的未完成映射时，可以释放通用内存句柄。每次接收进程导入可共享句柄时，都需要使用相应的 `hgMemRelease` 调用配对，以便释放句柄。如果 `handle` 不是有效句柄，则行为未定义。

```c
HGresult hgMemRelease (HGmemGenericAllocationHandle handle)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| handle | out | 之前由 hgMemCreate 返回的句柄值。 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_PERMITTED、HGGC_ERROR_NOT_SUPPORTED

---

#### 12. hgMemRetainAllocationHandle {#hgmemretainallocationhandle}

保证返回的句柄与用于映射内存的句柄值相同。如果请求的地址未映射，则函数将失败。返回的句柄必须使用相应次数的 [hgMemRelease](#hgmemrelease) 调用释放。

```c
HGresult hgMemRetainAllocationHandle (HGmemGenericAllocationHandle* handle,
                                      void* addr)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| handle | in | 支持内存分配的 HGGC 内存句柄。 |
| addr | in | 要查询的内存地址，之前已映射。 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_PERMITTED、HGGC_ERROR_NOT_SUPPORTED

---

#### 13. hgMemSetAccess {#hgmemsetaccess}

给定通过 `ptr` 和 `size` 指定的虚拟地址范围，以及由 `desc` 和 `count` 给出的数组中的位置，为目标位置设置访问标志。该范围必须是一个完全映射的地址范围，包含由 `hgMemMap` / `hgMemCreate` 创建的所有分配。用户不能为使用其他位置类型创建的分配指定 `HG_MEM_LOCATION_TYPE_HOST_NUMA` 可访问性。注意：当 HGmemAccessDesc::HGmemLocation::type 是 `HG_MEM_LOCATION_TYPE_HOST_NUMA` 时，将忽略 HGmemAccessDesc::HGmemLocation::id。当为映射多播对象的虚拟地址范围设置访问标志时，`ptr` 和 `size` 必须对齐到使用 HG_MULTICAST_MINIMUM_GRANULARITY 标志调用 `hgMulticastGetGranularity` 返回的值。为获得最佳性能，将 `ptr` 和 `size` 对齐到使用 HG_MULTICAST_RECOMMENDED_GRANULARITY 标志调用 `hgMulticastGetGranularity` 返回的值。

```c
HGresult hgMemSetAccess (HGdeviceptr ptr,
                         size_t size,
                         const HGmemAccessDesc* desc,
                         size_t count)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| ptr | in | 虚拟地址范围的起始地址 |
| size | in | 虚拟地址范围的长度 |
| desc | in | 描述如何更改每个指定位置的映射的 HGmemAccessDesc 数组 |
| count | in | `desc` 中 HGmemAccessDesc 的数量 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_INVALID_DEVICE、HGGC_ERROR_NOT_SUPPORTED

---

#### 14. hgMemUnmap {#hgmemunmap}

该范围必须是映射的整个连续地址范围。换句话说，`hgMemUnmap` 不能取消映射由 `hgMemCreate` / `hgMemMap` 映射的地址范围的子范围。如果不存在现有映射且没有未释放的内存句柄，则任何支持内存分配都将被释放。

当 `hgMemUnmap` 成功返回时，地址范围将转换为地址预留，可用于将来调用 `hgMemMap`。此虚拟地址范围的任何新映射都需要通过 `hgMemSetAccess` 授予访问权限，因为所有映射开始时都没有设置可达性。

```c
HGresult hgMemUnmap (HGdeviceptr ptr, size_t size)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| ptr | in | 要取消映射的虚拟地址范围起始地址 |
| size | in | 要取消映射的虚拟地址范围大小 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_PERMITTED、HGGC_ERROR_NOT_SUPPORTED

---

### 5.5. 内存池管理 {#mempool}

本模块提供**内存池管理（Memory Pool）** 接口。分配/释放操作与流关联，可避免不必要的同步。

本节介绍低级 HGGC 驱动程序应用程序编程接口的流有序内存分配器。

#### 1. 概述 {#概述}

异步分配器允许用户按流顺序分配和释放。所有对分配内存的异步访问必须发生在分配的流执行和释放之间。如果在承诺的流顺序之外访问内存，在分配之前使用/释放后使用错误将导致未定义行为。

只要分配器能保证合规的内存访问在时间上不会重叠，它就可以重新分配内存。分配器可以参考内部流顺序以及流间依赖关系（如 HGGC 事件和空流依赖）来建立时间保证。分配器也可以插入流间依赖以建立时间保证。

#### 2. 支持的平台 {#支持的平台}

设备是否支持集成的流有序内存分配器可以通过调用 [hgDeviceGetAttribute()](#hgdevicegetattribute) 与设备属性 [HG_DEVICE_ATTRIBUTE_MEMORY_POOLS_SUPPORTED](#driver-data-types) 来查询。

#### 3. 接口一览 {#接口一览}

| 函数 | 用途 |
|------|------|
| [hgMemAllocAsync](#hgmemallocasync) | 使用流有序语义分配内存 |
| [hgMemAllocFromPoolAsync](#hgmemallocfrompoolasync) | 使用流有序语义从指定池分配内存 |
| [hgMemFreeAsync](#hgmemfreeasync) | 使用流有序语义释放内存 |
| [hgMemPoolCreate](#hgmempoolcreate) | 创建内存池 |
| [hgMemPoolDestroy](#hgmempooldestroy) | 销毁指定的内存池 |
| [hgMemPoolExportPointer](#hgmempoolexportpointer) | 导出数据以在进程之间共享内存池分配 |
| [hgMemPoolExportToShareableHandle](#hgmempoolexporttoshareablehandle) | 将内存池导出为请求的句柄类型 |
| [hgMemPoolGetAccess](#hgmempoolgetaccess) | 返回设备对池的可达性 |
| [hgMemPoolGetAttribute](#hgmempoolgetattribute) | 获取内存池的属性 |
| [hgMemPoolImportFromShareableHandle](#hgmempoolimportfromshareablehandle) | 从共享句柄导入内存池 |
| [hgMemPoolImportPointer](#hgmempoolimportpointer) | 从另一个进程导入内存池分配 |
| [hgMemPoolSetAccess](#hgmempoolsetaccess) | 控制池在设备之间的可见性 |
| [hgMemPoolSetAttribute](#hgmempoolsetattribute) | 设置内存池的属性 |
| [hgMemPoolTrimTo](#hgmempooltrimto) | 尝试将内存释放回操作系统 |

---

#### 4. hgMemAllocAsync {#hgmemallocasync}

将分配操作插入 `hStream`。分配内存的指针立即在 `*dptr` 中返回。在分配操作完成之前不得访问分配。分配来自流设备当前的内存池。

```c
HGresult hgMemAllocAsync (HGdeviceptr* dptr, size_t bytesize, HGstream hStream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dptr | out | 返回的设备指针 |
| bytesize | in | 要分配的字节数 |
| hStream | in | 建立流顺序契约的流，以及要从中分配的内存池 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_NOT_SUPPORTED、HGGC_ERROR_OUT_OF_MEMORY

---

#### 5. hgMemAllocFromPoolAsync {#hgmemallocfrompoolasync}

将分配操作插入 `hStream`。分配内存的指针立即在 `*dptr` 中返回。在分配操作完成之前不得访问分配。分配来自指定的内存池。

```c
HGresult hgMemAllocFromPoolAsync (HGdeviceptr* dptr,
                                  size_t bytesize,
                                  HGmemoryPool pool,
                                  HGstream hStream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dptr | out | 返回的设备指针 |
| bytesize | in | 要分配的字节数 |
| pool | in | 要从中分配的池 |
| hStream | in | 建立流顺序语义的流 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_NOT_SUPPORTED、HGGC_ERROR_OUT_OF_MEMORY

---

#### 6. hgMemFreeAsync {#hgmemfreeasync}

将释放操作插入 `hStream`。分配必须在流执行到达释放之后才能被访问。此 API 返回后，从后续提交到 PPU 的工作访问内存或查询其指针属性会导致未定义行为。

```c
HGresult hgMemFreeAsync (HGdeviceptr dptr, HGstream hStream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dptr | in | 要释放的内存 |
| hStream | in | 建立流顺序契约的流 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_NOT_SUPPORTED

---

#### 7. hgMemPoolCreate {#hgmempoolcreate}

创建 HGGC 内存池并在 `pool` 中返回句柄。`poolProps` 决定池的属性，如支持设备和 IPC 能力。

要创建不针对特定 NUMA 节点的 HOST 内存池，应用程序必须将 HGmemPoolProps::HGmemLocation::type 设置为 [HG_MEM_LOCATION_TYPE_HOST](#driver-data-types)。对于此类池，将忽略 HGmemPoolProps::HGmemLocation::id。使用类型 [HG_MEM_LOCATION_TYPE_HOST](#driver-data-types) 创建的池不支持 IPC，HGmemPoolProps::handleTypes 必须为 0，任何其他值都会导致 [HGGC_ERROR_INVALID_VALUE](#driver-data-types)。要创建针对特定主机 NUMA 节点的内存池，应用程序必须将 HGmemPoolProps::HGmemLocation::type 设置为 [HG_MEM_LOCATION_TYPE_HOST_NUMA](#driver-data-types)，并且 HGmemPoolProps::HGmemLocation::id 必须指定主机内存节点的 NUMA ID。将 [HG_MEM_LOCATION_TYPE_HOST_NUMA_CURRENT](#driver-data-types) 指定为 HGmemPoolProps::HGmemLocation::type 将导致 [HGGC_ERROR_INVALID_VALUE](#driver-data-types)。默认情况下，池的内存可以从分配它的设备访问。对于使用 [HG_MEM_LOCATION_TYPE_HOST_NUMA](#driver-data-types) 或 [HG_MEM_LOCATION_TYPE_HOST](#driver-data-types) 创建的池，它们的默认可达性将是主机 CPU。应用程序可以通过为 HGmemPoolProps::maxSize 指定非零值来控制池的最大大小。如果设置为 0，池的最大大小将默认为系统相关的值。

打算使用 [HG_MEM_HANDLE_TYPE_FABRIC](#driver-data-types) 进行内存共享的应用程序必须确保：(1) alixpu-caps-imex-channels 字符设备由驱动程序创建并在 /proc/devices 中列出；(2) 启动应用程序的用户可以访问至少一个 IMEX 通道文件。

当导出方和导入方 HGGC 进程已被授予访问同一 IMEX 通道的权限时，它们可以安全地共享内存。

IMEX 通道安全模型基于每个用户工作。这意味着如果用户有权访问有效的 IMEX 通道，则该用户下的所有进程都可以共享内存。当需要多用户隔离时，每个用户需要一个单独的 IMEX 通道。

要创建托管内存池，应用程序必须将 [HGmemPoolProps::HGmemAllocationType](#driver-data-types) 设置为 HG_MEM_ALLOCATION_TYPE_MANAGED。[HGmemPoolProps::HGmemAllocationHandleType](#driver-data-types) 也必须设置为 HG_MEM_HANDLE_TYPE_NONE，因为不支持 IPC。对于托管内存池，HGmemPoolProps::HGmemLocation 将被视为池创建的所有分配的首选位置。应用程序也可以设置 HG_MEM_LOCATION_TYPE_NONE 表示没有首选位置。HGmemPoolProps::maxSize 必须设置为零。对于托管内存池，系统上的所有设备必须具有非零 concurrentManagedAccess。如果没有，此调用返回 HGGC_ERROR_NOT_SUPPORTED。

```c
HGresult hgMemPoolCreate (HGmemoryPool* pool, const HGmemPoolProps* poolProps)
```

错误码：HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_OUT_OF_MEMORY、HGGC_ERROR_NOT_PERMITTED、HGGC_ERROR_NOT_SUPPORTED

---

#### 8. hgMemPoolDestroy {#hgmempooldestroy}

如果在此调用时任何从该池获取的指针尚未释放，或者池有尚未完成的释放操作，函数将立即返回，一旦没有更多未完成的分配，池关联的资源将自动释放。

销毁设备的当前内存池会将该设备的默认内存池设置为该设备的当前内存池。

```c
HGresult hgMemPoolDestroy (HGmemoryPool pool)
```

错误码：HGGC_ERROR_INVALID_VALUE

---

#### 9. hgMemPoolExportPointer {#hgmempoolexportpointer}

为从已共享内存池共享的特定分配构造 `shareData_out`。接收进程可以使用 [hgMemPoolImportPointer](#hgmempoolimportpointer) API 导入分配。该数据不是句柄，可以通过任何 IPC 机制共享。

```c
HGresult hgMemPoolExportPointer (HGmemPoolPtrExportData* shareData_out,
                                 HGdeviceptr ptr)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| shareData_out | out | 返回的导出数据 |
| ptr | in | 要导出的指针 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_OUT_OF_MEMORY

---

#### 10. hgMemPoolExportToShareableHandle {#hgmempoolexporttoshareablehandle}

给定一个支持 IPC 的内存池，创建一个 OS 句柄以与另一个进程共享池。接收进程可以使用 [hgMemPoolImportFromShareableHandle](#hgmempoolimportfromshareablehandle) 将可共享句柄转换为内存池。然后可以使用 [hgMemPoolExportPointer](#hgmempoolexportpointer) 和 [hgMemPoolImportPointer](#hgmempoolimportpointer) API 在进程之间共享各个指针。实现可共享句柄的内容以及如何传输取决于请求的句柄类型。

```c
HGresult hgMemPoolExportToShareableHandle (void* handle_out,
                                           HGmemoryPool pool,
                                           HGmemAllocationHandleType handleType,
                                           unsigned long long flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| handle_out | out | 返回的 OS 句柄 |
| pool | in | 要导出的池 |
| handleType | in | 要创建的句柄类型 |
| flags | in | 必须为 0 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_OUT_OF_MEMORY

---

#### 11. hgMemPoolGetAccess {#hgmempoolgetaccess}

返回从指定位置对池内存的可达性。

```c
HGresult hgMemPoolGetAccess (HGmemAccess_flags* flags,
                             HGmemoryPool memPool,
                             HGmemLocation* location)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| flags | in | 从指定位置对池的可达性 |
| memPool | in | 被查询的池 |
| location | in | 访问池的位置 |

---

#### 12. hgMemPoolGetAttribute {#hgmempoolgetattribute}

支持的属性包括：

- [HG_MEMPOOL_ATTR_RELEASE_THRESHOLD](#driver-data-types)：(值类型 = hguint64_t) 在尝试将内存释放回操作系统之前保留的保留内存字节数。当内存池持有的内存超过释放阈值字节数时，分配器将在下一次调用流、事件或上下文同步时尝试将内存释放回操作系统。（默认 0）
- [HG_MEMPOOL_ATTR_REUSE_FOLLOW_EVENT_DEPENDENCIES](#driver-data-types)：(值类型 = int) 允许 [hgMemAllocAsync](#hgmemallocasync) 使用在另一个流中异步释放的内存，只要分配流与释放操作之间存在流顺序依赖关系。HGGC 事件和空流交互可以创建所需的流顺序依赖关系。（默认启用）
- [HG_MEMPOOL_ATTR_REUSE_ALLOW_OPPORTUNISTIC](#driver-data-types)：(值类型 = int) 当释放和分配之间没有依赖关系时，允许重用已完成的释放。（默认启用）
- [HG_MEMPOOL_ATTR_REUSE_ALLOW_INTERNAL_DEPENDENCIES](#driver-data-types)：(值类型 = int) 允许 [hgMemAllocAsync](#hgmemallocasync) 插入新的流依赖关系，以建立重用 [hgMemFreeAsync](#hgmemfreeasync) 释放的内存所需的流顺序。（默认启用）
- [HG_MEMPOOL_ATTR_RESERVED_MEM_CURRENT](#driver-data-types)：(值类型 = hguint64_t) 当前为内存池分配的后备内存量
- [HG_MEMPOOL_ATTR_RESERVED_MEM_HIGH](#driver-data-types)：(值类型 = hguint64_t) 自上次重置以来为内存池分配的后备内存的高水位线。
- [HG_MEMPOOL_ATTR_USED_MEM_CURRENT](#driver-data-types)：(值类型 = hguint64_t) 应用程序当前使用的池内存量。
- [HG_MEMPOOL_ATTR_USED_MEM_HIGH](#driver-data-types)：(值类型 = hguint64_t) 应用程序使用的池内存量的高水位线。

```c
HGresult hgMemPoolGetAttribute (HGmemoryPool pool,
                                HGmemPool_attribute attr,
                                void* value)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pool | in | 要获取属性的内存池 |
| attr | in | 要获取的属性 |
| value | in | 检索到的值 |

错误码：HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 13. hgMemPoolImportFromShareableHandle {#hgmempoolimportfromshareablehandle}

可以使用 hgMemPoolImportPointer 从导入的池中导入特定分配。

如果 `handleType` 是 [HG_MEM_HANDLE_TYPE_FABRIC](#driver-data-types) 并且导入进程未被授予与导出进程相同的 IMEX 通道访问权限，此 API 将报错为 [HGGC_ERROR_NOT_PERMITTED](#driver-data-types)。

```c
HGresult hgMemPoolImportFromShareableHandle (HGmemoryPool* pool_out,
                                             void* handle,
                                             HGmemAllocationHandleType handleType,
                                             unsigned long long flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pool_out | out | 返回的内存池 |
| handle | in | 要打开的池的 OS 句柄 |
| handleType | in | 被导入的句柄类型 |
| flags | in | 必须为 0 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_OUT_OF_MEMORY

---

#### 14. hgMemPoolImportPointer {#hgmempoolimportpointer}

在 `ptr_out` 中返回导入内存的指针。在导出进程中分配操作完成之前，不得访问导入的内存。导入的内存必须在导出进程中释放之前从所有导入进程中释放。指针可以使用 hgMemFree 或 hgMemFreeAsync 释放。如果使用 hgMemFreeAsync，则必须在导入进程中的 hgMemFreeAsync 完成之前在导出进程中完成释放。

```c
HGresult hgMemPoolImportPointer (HGdeviceptr* ptr_out,
                                 HGmemoryPool pool,
                                 HGmemPoolPtrExportData* shareData)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| ptr_out | out | 导入的内存指针 |
| pool | in | 要从中导入的池 |
| shareData | in | 指定要导入的内存的数据 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_OUT_OF_MEMORY

---

#### 15. hgMemPoolSetAccess {#hgmempoolsetaccess}

控制池在设备之间的可见性。

```c
HGresult hgMemPoolSetAccess (HGmemoryPool pool,
                             const HGmemAccessDesc* map,
                             size_t count)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pool | in | 被修改的池 |
| map | in | 访问描述符数组。每个描述符指示要为一个 PPU 启用哪种访问。 |
| count | in | 地图数组中的描述符数量。 |

错误码：HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 16. hgMemPoolSetAttribute {#hgmempoolsetattribute}

支持的属性包括：

- [HG_MEMPOOL_ATTR_RELEASE_THRESHOLD](#driver-data-types)：(值类型 = hguint64_t) 在尝试将内存释放回操作系统之前保留的保留内存字节数。当内存池持有的内存超过释放阈值字节数时，分配器将在下一次调用流、事件或上下文同步时尝试将内存释放回操作系统。（默认 0）
- [HG_MEMPOOL_ATTR_REUSE_FOLLOW_EVENT_DEPENDENCIES](#driver-data-types)：(值类型 = int) 允许 [hgMemAllocAsync](#hgmemallocasync) 使用在另一个流中异步释放的内存，只要分配流与释放操作之间存在流顺序依赖关系。HGGC 事件和空流交互可以创建所需的流顺序依赖关系。（默认启用）
- [HG_MEMPOOL_ATTR_REUSE_ALLOW_OPPORTUNISTIC](#driver-data-types)：(值类型 = int) 当释放和分配之间没有依赖关系时，允许重用已完成的释放。（默认启用）
- [HG_MEMPOOL_ATTR_REUSE_ALLOW_INTERNAL_DEPENDENCIES](#driver-data-types)：(值类型 = int) 允许 [hgMemAllocAsync](#hgmemallocasync) 插入新的流依赖关系，以建立重用 [hgMemFreeAsync](#hgmemfreeasync) 释放的内存所需的流顺序。（默认启用）
- [HG_MEMPOOL_ATTR_RESERVED_MEM_HIGH](#driver-data-types)：(值类型 = hguint64_t) 重置跟踪为内存池分配的后备内存量的高水位线。将此属性设置为非零值是非法的。
- [HG_MEMPOOL_ATTR_USED_MEM_HIGH](#driver-data-types)：(值类型 = hguint64_t) 重置跟踪为内存池分配的使用内存量的高水位线。

```c
HGresult hgMemPoolSetAttribute (HGmemoryPool pool,
                                HGmemPool_attribute attr,
                                void* value)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pool | in | 要修改的内存池 |
| attr | in | 要修改的属性 |
| value | in | 要分配的值指针 |

错误码：HGGC_ERROR_INVALID_VALUE

---

#### 17. hgMemPoolTrimTo {#hgmempooltrimto}

将内存释放回操作系统，直到池包含少于 minBytesToKeep 保留字节，或者分配器无法安全释放更多内存。分配器无法释放支持未完成异步分配的 OS 分配。OS 分配可能与用户分配的粒度不同。

```c
HGresult hgMemPoolTrimTo (HGmemoryPool pool, size_t minBytesToKeep)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pool | in | 要修剪的内存池 |
| minBytesToKeep | in | 如果池保留的内存少于 minBytesToKeep，则 TrimTo 操作是空操作。否则，将保证池在操作后至少保留 minBytesToKeep 字节。 |

错误码：HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

比赛关联：这一组是显存优化的核心接口层——流有序内存池（`hgMemAllocAsync` + `HG_MEMPOOL_ATTR_RELEASE_THRESHOLD`/`hgMemPoolTrimTo`）可做权重/KV buffer 的池化管理、压低显存峰值与碎片；VMM（`hgMemAddressReserve`/`hgMemCreate`/`hgMemMap`/`hgMemSetAccess`）支持按需提交物理页的弹性显存策略；`hgMemAdvise`/`hgMemPrefetchAsync` 用于统一内存场景的预取与位置优化；pinned 主机内存（`hgMemHostAlloc`/`hgMemHostRegister`）是 H2D 全带宽异步传输的前提。

---

## 6. 流与事件 {#streams}

本节涵盖异步执行的核心原语：流（Stream）的创建与同步、事件（Event）的记录与等待，以及流内直接内存操作。

---

### 6.1. 资源管理 {#stream-event}

本模块提供**资源管理（Resource Management）** 接口，包含事件（Event）和流（Stream）的创建、销毁、同步与属性管理。

本节介绍低级 HGGC 驱动程序应用程序编程接口的资源管理函数。

#### 1. 接口一览 {#接口一览}

| 函数 | 用途 |
|------|------|
| [hgEventCreate](#hgeventcreate) | 创建事件 |
| [hgEventDestroy](#hgeventdestroy) | 销毁事件 |
| [hgEventElapsedTime](#hgeventelapsedtime) | 计算两个事件之间经过的时间 |
| [hgEventQuery](#hgeventquery) | 查询事件的状态 |
| [hgEventRecord](#hgeventrecord) | 在此调用时将 `hStream` 的内容捕获到 `hEvent` 中 |
| [hgEventRecordWithFlags](#hgeventrecordwithflags) | 使用指定标志记录事件 |
| [hgEventSynchronize](#hgeventsynchronize) | 等待事件完成 |
| [hgStreamAddCallback](#hgstreamaddcallback) | 向计算流添加回调 |
| [hgStreamAttachMemAsync](#hgstreamattachmemasync) | 以异步方式将内存附加到流 |
| [hgStreamBeginCapture](#hgstreambegincapture) | 在流上开始图捕获 |
| [hgStreamBeginCaptureToGraph](#hgstreambegincapturetograph) | 在流上开始图捕获，并捕获到一个已有的图中 |
| [hgStreamCopyAttributes](#hgstreamcopyattributes) | 将源流的属性复制到目标流 |
| [hgStreamCreate](#hgstreamcreate) | 创建一个流 |
| [hgStreamCreateWithPriority](#hgstreamcreatewithpriority) | 创建一个具有指定优先级的流 |
| [hgStreamDestroy](#hgstreamdestroy) | 销毁一个流 |
| [hgStreamEndCapture](#hgstreamendcapture) | 结束对流的捕获，并返回捕获到的图 |
| [hgStreamGetAttribute](#hgstreamgetattribute) | 查询流属性 |
| [hgStreamGetCaptureInfo](#hgstreamgetcaptureinfo) | 查询流的捕获状态 |
| [hgStreamGetCtx](#hgstreamgetctx) | 查询与流关联的上下文 |
| [hgStreamGetFlags](#hgstreamgetflags) | 查询给定流的标志位 |
| [hgStreamGetId](#hgstreamgetid) | 返回与所提供流句柄关联的唯一 Id |
| [hgStreamGetPriority](#hgstreamgetpriority) | 查询给定流的优先级 |
| [hgStreamIsCapturing](#hgstreamiscapturing) | 返回流的捕获状态 |
| [hgStreamQuery](#hgstreamquery) | 确定计算流的状态 |
| [hgStreamSetAttribute](#hgstreamsetattribute) | 设置流属性 |
| [hgStreamSynchronize](#hgstreamsynchronize) | 等待流中的任务完成 |
| [hgStreamUpdateCaptureDependencies](#hgstreamupdatecapturedependencies) | 更新正在捕获的流中的依赖集合 |
| [hgStreamWaitEvent](#hgstreamwaitevent) | 使计算流等待一个事件 |
| [hgThreadExchangeStreamCaptureMode](#hgthreadexchangestreamcapturemode) | 为线程交换流捕获交互模式 |

---

#### 2. hgEventCreate {#hgeventcreate}

使用通过 `Flags` 指定的标志为当前上下文创建事件 `*phEvent`。有效标志包括：

- [HG_EVENT_DEFAULT](#driver-data-types)：默认事件创建标志。
- [HG_EVENT_BLOCKING_SYNC](#driver-data-types)：指定创建的事件应使用阻塞同步。使用此标志创建的事件调用 [hgEventSynchronize()](#hgeventsynchronize) 等待的 CPU 线程将阻塞，直到事件实际被记录。
- [HG_EVENT_DISABLE_TIMING](#driver-data-types)：指定创建的事件不需要记录时间数据。使用此标志创建且未指定 [HG_EVENT_BLOCKING_SYNC](#driver-data-types) 标志的事件在与 [hgStreamWaitEvent()](#hgstreamwaitevent) 和 [hgEventQuery()](#hgeventquery) 一起使用时将提供最佳性能。
- [HG_EVENT_INTERPROCESS](#driver-data-types)：指定创建的事件可用作 [hgIpcGetEventHandle()](#mem-mgmt) 的进程间事件。[HG_EVENT_INTERPROCESS](#driver-data-types) 必须与 [HG_EVENT_DISABLE_TIMING](#driver-data-types) 一起指定。

```c
HGresult hgEventCreate (HGevent* phEvent, unsigned int Flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| phEvent | out | 返回新创建的事件 |
| Flags | in | 事件创建标志 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_OUT_OF_MEMORY

---

#### 3. hgEventDestroy {#hgeventdestroy}

销毁由 `hEvent` 指定的事件。

事件可以在完成之前销毁（即当 [hgEventQuery()](#hgeventquery) 会返回 [HGGC_ERROR_NOT_READY](#driver-data-types) 时）。在这种情况下，调用不会阻塞等待事件完成，任何相关的资源都将在完成时异步自动释放。

```c
HGresult hgEventDestroy (HGevent hEvent)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hEvent | in | 要销毁的事件 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_HANDLE

---

#### 4. hgEventElapsedTime {#hgeventelapsedtime}

计算两个事件之间经过的时间（以毫秒为单位，分辨率约为 0.5 微秒）。请注意，此 API 不保证返回待处理工作的最新错误。因此，此 API 仅用于计算经过时间，任何对要比较的事件完成状态的轮询都应改用 [hgEventQuery](#hgeventquery) 完成。

如果任一事件最后在非 NULL 流中记录，则结果时间可能大于预期（即使两者使用相同的流句柄）。这是因为 [hgEventRecord()](#hgeventrecord) 操作是异步进行的，不能保证测量的延迟实际上只是两个事件之间的时间。任意数量的其他不同流操作可能在两个被测量的事件之间执行，从而显著改变时序。

如果尚未在任一事件上调用 [hgEventRecord()](#hgeventrecord)，则返回 [HGGC_ERROR_INVALID_HANDLE](#driver-data-types)。如果已在两个事件上调用 [hgEventRecord()](#hgeventrecord)，但其中一个或两个尚未完成（即 [hgEventQuery()](#hgeventquery) 将在至少一个事件上返回 [HGGC_ERROR_NOT_READY](#driver-data-types)），则返回 [HGGC_ERROR_NOT_READY](#driver-data-types)。如果任一事件使用 [HG_EVENT_DISABLE_TIMING](#driver-data-types) 标志创建，则此函数将返回 [HGGC_ERROR_INVALID_HANDLE](#driver-data-types)。

```c
HGresult hgEventElapsedTime (float* pMilliseconds, HGevent hStart, HGevent hEnd)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pMilliseconds | out | `hStart` 和 `hEnd` 之间的时间（毫秒） |
| hStart | in | 起始事件 |
| hEnd | in | 结束事件 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_HANDLE、HGGC_ERROR_NOT_READY、HGGC_ERROR_UNKNOWN

---

#### 5. hgEventQuery {#hgeventquery}

查询 `hEvent` 当前捕获的所有工作的状态。参见 [hgEventRecord()](#hgeventrecord) 了解事件捕获的详细信息。

如果所有捕获的工作都已完成则返回 [HGGC_SUCCESS](#driver-data-types)，如果任何捕获的工作未完成则返回 [HGGC_ERROR_NOT_READY](#driver-data-types)。

就统一内存而言，返回值 [HGGC_SUCCESS](#driver-data-types) 等同于已调用 [hgEventSynchronize()](#hgeventsynchronize)。

```c
HGresult hgEventQuery (HGevent hEvent)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hEvent | in | 要查询的事件 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_HANDLE、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_READY

---

#### 6. hgEventRecord {#hgeventrecord}

在此调用时将 `hStream` 的内容捕获到 `hEvent` 中。`hEvent` 和 `hStream` 必须来自同一上下文，否则返回 [HGGC_ERROR_INVALID_HANDLE](#driver-data-types)。随后调用 [hgEventQuery()](#hgeventquery) 或 [hgStreamWaitEvent()](#hgstreamwaitevent) 将检查或等待捕获的工作完成。在此调用之后对 `hStream` 的使用不会修改 `hEvent`。有关默认情况下捕获内容的信息，请参阅默认流行为说明。

可以在同一事件上多次调用 [hgEventRecord()](#hgeventrecord)，并将覆盖先前捕获的状态。其他 API（如 [hgStreamWaitEvent()](#hgstreamwaitevent)）使用调用时最新的捕获状态，不受后续对 [hgEventRecord()](#hgeventrecord) 调用的影响。在第一次调用 [hgEventRecord()](#hgeventrecord) 之前，事件表示一个空的工作集，因此例如 [hgEventQuery()](#hgeventquery) 将返回 [HGGC_SUCCESS](#driver-data-types)。

```c
HGresult hgEventRecord (HGevent hEvent, HGstream hStream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hEvent | in | 要记录的事件 |
| hStream | in | 记录事件的流 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_HANDLE、HGGC_ERROR_INVALID_VALUE

---

#### 7. hgEventRecordWithFlags {#hgeventrecordwithflags}

在此调用时将 `hStream` 的内容捕获到 `hEvent` 中。`hEvent` 和 `hStream` 必须来自同一上下文，否则返回 [HGGC_ERROR_INVALID_HANDLE](#driver-data-types)。随后调用 [hgEventQuery()](#hgeventquery) 或 [hgStreamWaitEvent()](#hgstreamwaitevent) 将检查或等待捕获的工作完成。在此调用之后对 `hStream` 的使用不会修改 `hEvent`。有关默认情况下捕获内容的信息，请参阅默认流行为说明。

可以在同一事件上多次调用 [hgEventRecordWithFlags()](#hgeventrecordwithflags)，并将覆盖先前捕获的状态。其他 API（如 [hgStreamWaitEvent()](#hgstreamwaitevent)）使用调用时最新的捕获状态，不受后续对 [hgEventRecordWithFlags()](#hgeventrecordwithflags) 调用的影响。在第一次调用 [hgEventRecordWithFlags()](#hgeventrecordwithflags) 之前，事件表示一个空的工作集，因此例如 [hgEventQuery()](#hgeventquery) 将返回 [HGGC_SUCCESS](#driver-data-types)。

flags 包括：

- [HG_EVENT_RECORD_DEFAULT](#driver-data-types)：默认事件记录标志。
- [HG_EVENT_RECORD_EXTERNAL](#driver-data-types)：在执行流捕获时，事件在图中作为外部事件节点被捕获。此标志在流捕获之外无效。

```c
HGresult hgEventRecordWithFlags (HGevent hEvent,
                                 HGstream hStream,
                                 unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hEvent | in | 要记录的事件 |
| hStream | in | 记录事件的流 |
| flags | in | 参见 HGevent_capture_flags |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_HANDLE、HGGC_ERROR_INVALID_VALUE

---

#### 8. hgEventSynchronize {#hgeventsynchronize}

等待 `hEvent` 中当前捕获的所有工作完成。参见 [hgEventRecord()](#hgeventrecord) 了解事件捕获的详细信息。

等待使用 [HG_EVENT_BLOCKING_SYNC](#driver-data-types) 标志创建的事件将导致调用 CPU 线程阻塞，直到事件由设备完成。如果未设置 [HG_EVENT_BLOCKING_SYNC](#driver-data-types) 标志，则 CPU 线程将忙等待，直到事件由设备完成。

```c
HGresult hgEventSynchronize (HGevent hEvent)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hEvent | in | 等待的事件 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_HANDLE

---

#### 9. hgStreamAddCallback {#hgstreamaddcallback}

向计算流添加回调。

```c
HGresult hgStreamAddCallback(HGstream hStream,
                             HGstreamCallback callback,
                             void* userData,
                             unsigned int flags)
```

---

#### 10. hgStreamAttachMemAsync {#hgstreamattachmemasync}

将内存异步附加到流。

```c
HGresult hgStreamAttachMemAsync(HGstream hStream,
                                HGdeviceptr dptr,
                                size_t length,
                                unsigned int flags)
```

---

#### 11. hgStreamBeginCapture {#hgstreambegincapture}

开始流捕获。

```c
HGresult hgStreamBeginCapture(HGstream hStream, HGstreamCaptureMode mode)
```

---

#### 12. hgStreamBeginCaptureToGraph {#hgstreambegincapturetograph}

开始将图捕获到现有图。

```c
HGresult hgStreamBeginCaptureToGraph(HGstream hStream,
                                     HGgraph hGraph,
                                     const HGgraphNode* dependencies,
                                     const HGgraphEdgeData* dependencyData,
                                     size_t numDependencies,
                                     HGstreamCaptureMode mode)
```

---

#### 13. hgStreamCopyAttributes {#hgstreamcopyattributes}

将属性从源流复制到目标流。

```c
HGresult hgStreamCopyAttributes(HGstream dst, HGstream src)
```

---

#### 14. hgStreamCreate {#hgstreamcreate}

创建流。

```c
HGresult hgStreamCreate(HGstream* phStream, unsigned int Flags)
```

---

#### 15. hgStreamCreateWithPriority {#hgstreamcreatewithpriority}

创建具有给定优先级的流。

```c
HGresult hgStreamCreateWithPriority(HGstream* phStream,
                                    unsigned int flags,
                                    int priority)
```

---

#### 16. hgStreamDestroy {#hgstreamdestroy}

销毁流。

```c
HGresult hgStreamDestroy(HGstream hStream)
```

---

#### 17. hgStreamEndCapture {#hgstreamendcapture}

结束流上的捕获，返回捕获的图。

```c
HGresult hgStreamEndCapture(HGstream hStream, HGgraph* phGraph)
```

---

#### 18. hgStreamGetAttribute {#hgstreamgetattribute}

查询流属性。

```c
HGresult hgStreamGetAttribute(HGstream hStream,
                              HGstreamAttrID attr,
                              HGstreamAttrValue* value_out)
```

---

#### 19. hgStreamGetCaptureInfo {#hgstreamgetcaptureinfo}

查询流的捕获状态。

```c
HGresult hgStreamGetCaptureInfo(HGstream hStream,
                                HGstreamCaptureStatus* captureStatus_out,
                                hguint64_t* id_out,
                                HGgraph* graph_out,
                                const HGgraphNode** dependencies_out,
                                const HGgraphEdgeData** edgeData_out,
                                size_t* numDependencies_out)
```

---

#### 20. hgStreamGetCtx {#hgstreamgetctx}

查询与流关联的上下文。

```c
HGresult hgStreamGetCtx(HGstream hStream, HGcontext* pctx)
```

---

#### 21. hgStreamGetFlags {#hgstreamgetflags}

查询给定流的标志。

```c
HGresult hgStreamGetFlags(HGstream hStream, unsigned int* flags)
```

---

#### 22. hgStreamGetId {#hgstreamgetid}

返回与所提供的流句柄关联的唯一 ID。

```c
HGresult hgStreamGetId(HGstream hStream, unsigned long long* streamId)
```

---

#### 23. hgStreamGetPriority {#hgstreamgetpriority}

查询给定流的优先级。

```c
HGresult hgStreamGetPriority(HGstream hStream, int* priority)
```

---

#### 24. hgStreamIsCapturing {#hgstreamiscapturing}

返回流的捕获状态。

```c
HGresult hgStreamIsCapturing(HGstream hStream,
                             HGstreamCaptureStatus* captureStatus)
```

---

#### 25. hgStreamQuery {#hgstreamquery}

确定计算流的状态。

```c
HGresult hgStreamQuery(HGstream hStream)
```

---

#### 26. hgStreamSetAttribute {#hgstreamsetattribute}

设置流属性。

```c
HGresult hgStreamSetAttribute(HGstream hStream,
                              HGstreamAttrID attr,
                              const HGstreamAttrValue* value)
```

---

#### 27. hgStreamSynchronize {#hgstreamsynchronize}

等待流的全部任务完成。

```c
HGresult hgStreamSynchronize(HGstream hStream)
```

---

#### 28. hgStreamUpdateCaptureDependencies {#hgstreamupdatecapturedependencies}

更新捕获流的依赖集。

```c
HGresult hgStreamUpdateCaptureDependencies(HGstream hStream,
                                           HGgraphNode* dependencies,
                                           const HGgraphEdgeData* dependencyData,
                                           size_t numDependencies,
                                           unsigned int flags)
```

---

#### 29. hgStreamWaitEvent {#hgstreamwaitevent}

使计算流等待事件。

```c
HGresult hgStreamWaitEvent(HGstream hStream, HGevent hEvent, unsigned int Flags)
```

---

#### 30. hgThreadExchangeStreamCaptureMode {#hgthreadexchangestreamcapturemode}

交换线程的流捕获交互模式。

```c
HGresult hgThreadExchangeStreamCaptureMode(HGstreamCaptureMode* mode)
```

---

### 6.2. 流内存操作 {#stream-memop}

本模块提供**流内存操作（Stream Memory Operations）** 接口，允许在流中直接写入/等待 PPU 可见地址处的值，用于轻量级信号与栅栏。

本节介绍低级 HGGC 驱动程序应用程序编程接口的流内存操作函数。

支持 [HG_STREAM_WAIT_VALUE_NOR](#driver-data-types) 标志可以使用 HG_DEVICE_ATTRIBUTE_CAN_USE_STREAM_WAIT_VALUE_NOR_V2 进行查询。

支持 [hgStreamWriteValue64()](#hgstreamwritevalue64) 和 [hgStreamWaitValue64()](#hgstreamwaitvalue64) 函数，以及 [HG_STREAM_MEM_OP_WAIT_VALUE_64](#driver-data-types) 和 [HG_STREAM_MEM_OP_WRITE_VALUE_64](#driver-data-types) 标志，可以使用 [HG_DEVICE_ATTRIBUTE_CAN_USE_64_BIT_STREAM_MEM_OPS](#driver-data-types) 进行查询。

同时支持 [HG_STREAM_WAIT_VALUE_FLUSH](#driver-data-types) 和 [HG_STREAM_MEM_OP_FLUSH_REMOTE_WRITES](#driver-data-types) 需要专用平台硬件功能，可以使用 [hgDeviceGetAttribute()](#hgdevicegetattribute) 和 [HG_DEVICE_ATTRIBUTE_CAN_FLUSH_REMOTE_WRITES](#driver-data-types) 进行查询。

请注意，所有作为参数传递的内存指针都是设备指针。必要时应获取设备指针，例如使用 [hgMemHostGetDevicePointer()](#hgmemhostgetdevicepointer)。

这些操作都不接受指向 managed 内存缓冲区（[hgMemAllocManaged](#hgmemallocmanaged)）的指针。

#### 1. 接口一览 {#接口一览}

| 函数 | 用途 |
|------|------|
| [hgStreamBatchMemOp](#hgstreambatchmemop) | 通过内存操作批量同步流的操作 |
| [hgStreamWaitValue32](#hgstreamwaitvalue32) | 等待 32 位内存值满足条件 |
| [hgStreamWaitValue64](#hgstreamwaitvalue64) | 等待 64 位内存值满足条件 |
| [hgStreamWriteValue32](#hgstreamwritevalue32) | 向内存写入 32 位值 |
| [hgStreamWriteValue64](#hgstreamwritevalue64) | 向内存写入 64 位值 |

---

#### 2. hgStreamBatchMemOp {#hgstreambatchmemop}

这是 [hgStreamWaitValue32()](#hgstreamwaitvalue32) 和 [hgStreamWriteValue32()](#hgstreamwritevalue32) 的批量版本。批量操作可以避免在 API 调用和设备执行中分别添加这些操作到流时的一些性能开销。操作按照它们在数组中出现的顺序入队。

有关支持的完整操作集，请参见 [HGstreamBatchMemOpType](#driver-data-types)，并参见 [hgStreamWaitValue32()](#hgstreamwaitvalue32)、[hgStreamWaitValue64()](#hgstreamwaitvalue64)、[hgStreamWriteValue32()](#hgstreamwritevalue32) 和 [hgStreamWriteValue64()](#hgstreamwritevalue64) 了解具体操作的详细信息。

有关查询特定操作支持的更多信息，请参见相关 API。

```c
HGresult hgStreamBatchMemOp (HGstream stream,
                             unsigned int count,
                             HGstreamBatchMemOpParams* paramArray,
                             unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| stream | in | 要将操作入队的流 |
| count | in | 数组中的操作数量。必须小于 256 |
| paramArray | in | 各个操作的类型和参数 |
| flags | in | 预留供将来扩展；必须为 0 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_SUPPORTED

---

#### 3. hgStreamWaitValue32 {#hgstreamwaitvalue32}

在给定内存位置对流进行同步排队。在此操作之后排序的工作将阻塞，直到内存上满足给定条件。默认情况下，条件是等待 (int32_t)(*addr - value) >= 0，即循环大于或等于。可以通过 `flags` 指定其他条件类型。

如果内存是通过 [hgMemHostRegister()](#hgmemhostregister) 注册的，应使用 [hgMemHostGetDevicePointer()](#hgmemhostgetdevicepointer) 获取设备指针。此函数不能与 managed 内存（[hgMemAllocManaged](#hgmemallocmanaged)）一起使用。

可以使用 [hgDeviceGetAttribute()](#hgdevicegetattribute) 和 HG_DEVICE_ATTRIBUTE_CAN_USE_STREAM_WAIT_VALUE_NOR_V2 查询对 HG_STREAM_WAIT_VALUE_NOR 的支持。

```c
HGresult hgStreamWaitValue32 (HGstream stream,
                              HGdeviceptr addr,
                              hguint32_t value,
                              unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| stream | in | 在内存位置同步的流 |
| addr | in | 要等待的内存位置 |
| value | in | 与内存位置比较的值 |
| flags | in | 参见 [HGstreamWaitValue_flags](#driver-data-types) |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_SUPPORTED

---

#### 4. hgStreamWaitValue64 {#hgstreamwaitvalue64}

在给定内存位置对流进行同步排队。在此操作之后排序的工作将阻塞，直到内存上满足给定条件。默认情况下，条件是等待 (int64_t)(*addr - value) >= 0，即循环大于或等于。可以通过 `flags` 指定其他条件类型。

如果内存是通过 [hgMemHostRegister()](#hgmemhostregister) 注册的，应使用 [hgMemHostGetDevicePointer()](#hgmemhostgetdevicepointer) 获取设备指针。

可以使用 [hgDeviceGetAttribute()](#hgdevicegetattribute) 和 [HG_DEVICE_ATTRIBUTE_CAN_USE_64_BIT_STREAM_MEM_OPS](#driver-data-types) 查询对此功能的支持。

```c
HGresult hgStreamWaitValue64 (HGstream stream,
                              HGdeviceptr addr,
                              hguint64_t value,
                              unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| stream | in | 在内存位置同步的流 |
| addr | in | 要等待的内存位置 |
| value | in | 与内存位置比较的值 |
| flags | in | 参见 [HGstreamWaitValue_flags](#driver-data-types) |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_SUPPORTED

---

#### 5. hgStreamWriteValue32 {#hgstreamwritevalue32}

向内存写入一个值。

如果内存是通过 [hgMemHostRegister()](#hgmemhostregister) 注册的，应使用 [hgMemHostGetDevicePointer()](#hgmemhostgetdevicepointer) 获取设备指针。此函数不能与 managed 内存（[hgMemAllocManaged](#hgmemallocmanaged)）一起使用。

```c
HGresult hgStreamWriteValue32 (HGstream stream,
                               HGdeviceptr addr,
                               hguint32_t value,
                               unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| stream | in | 执行写入的流 |
| addr | in | 要写入的设备地址 |
| value | in | 要写入的值 |
| flags | in | 参见 [HGstreamWriteValue_flags](#driver-data-types) |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_SUPPORTED

---

#### 6. hgStreamWriteValue64 {#hgstreamwritevalue64}

向内存写入一个值。

如果内存是通过 [hgMemHostRegister()](#hgmemhostregister) 注册的，应使用 [hgMemHostGetDevicePointer()](#hgmemhostgetdevicepointer) 获取设备指针。

可以使用 [hgDeviceGetAttribute()](#hgdevicegetattribute) 和 [HG_DEVICE_ATTRIBUTE_CAN_USE_64_BIT_STREAM_MEM_OPS](#driver-data-types) 查询对此功能的支持。

```c
HGresult hgStreamWriteValue64 (HGstream stream,
                               HGdeviceptr addr,
                               hguint64_t value,
                               unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| stream | in | 执行写入的流 |
| addr | in | 要写入的设备地址 |
| value | in | 要写入的值 |
| flags | in | 参见 [HGstreamWriteValue_flags](#driver-data-types) |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_SUPPORTED

---

比赛关联：`hgStreamCreateWithPriority`、事件与 `hgStreamWaitValue*`/`hgStreamWriteValue*` 轻量级流内信号可用于 prefill/decode 双流转发的细粒度编排，避免全局同步造成的吞吐损失。

---

## 7. 执行与调度 {#exec}

本节涵盖 PPU 核函数的启动方式、函数属性查询、占用率计算，以及基于图的批量任务调度。

---

### 7.1. 执行控制 {#exec-control}

本模块提供**执行控制**接口，涵盖核函数启动（launch）、执行配置、函数/模块属性查询等。它是将 device code 调度到 PPU 上执行的核心入口。

本节介绍低级 HGGC 驱动程序应用程序编程接口的执行控制函数。

#### 1. 接口一览 {#接口一览}

| 函数 | 用途 |
|------|------|
| [hgFuncGetAttribute](#hgfuncgetattribute) | 返回有关函数的信息 |
| [hgFuncGetModule](#hgfuncgetmodule) | 返回模块句柄 |
| [hgFuncGetName](#hgfuncgetname) | 返回 HGfunction 句柄的函数名称 |
| [hgFuncSetAttribute](#hgfuncsetattribute) | 设置有关函数的信息 |
| [hgFuncSetCacheConfig](#hgfuncsetcacheconfig) | 为设备函数设置首选缓存配置 |
| [hgLaunchCooperativeKernel](#hglaunchcooperativekernel) | 启动一个 HGGC 函数 HGfunction 或 HGGC 核函数 HGkernel，其中线程块可以在执行时协作和同步 |
| [hgLaunchHostFunc](#hglaunchhostfunc) | 在流中入队一个主机函数来运行 |
| [hgLaunchKernel](#hglaunchkernel) | 启动 HGGC 函数 HGfunction 或 HGGC 核函数 HGkernel |
| [hgLaunchKernelEx](#hglaunchkernelex) | 使用启动时配置启动 HGGC 函数 HGfunction 或 HGGC 核函数 HGkernel |
| [hgOccupancyAvailableDynamicSMemPerBlock](#hgoccupancyavailabledynamicsmemperblock) | 返回在 SM 上启动 numBlocks 个块时每个块可用的动态共享内存 |
| [hgOccupancyMaxActiveBlocksPerMultiprocessor](#hgoccupancymaxactiveblockspermultiprocessor) | 在 `*numBlocks` 中返回每个流式多处理器最大活动块数 |
| [hgOccupancyMaxActiveBlocksPerMultiprocessorWithFlags](#hgoccupancymaxactiveblockspermultiprocessorwithflags) | 返回每个 SM 最大活动块数（可指定标志） |
| [hgOccupancyMaxPotentialBlockSize](#hgoccupancymaxpotentialblocksize) | 在 `*blockSize` 中返回一个可达到最大占用率（或每个多处理… |
| [hgOccupancyMaxPotentialBlockSizeWithFlags](#hgoccupancymaxpotentialblocksizewithflags) | hgOccupancyMaxPotentialBlockSize 的扩… |

---

#### 2. hgFuncGetAttribute {#hgfuncgetattribute}

返回给定核函数 `hfunc` 的属性 `attrib` 的整数值到 `*pi`。支持的属性包括：

- `HG_FUNC_ATTRIBUTE_MAX_THREADS_PER_BLOCK`：每个块的最大线程数，超过该数量启动函数将失败。此数字取决于函数和当前加载该函数的设备。
- `HG_FUNC_ATTRIBUTE_SHARED_SIZE_BYTES`：此函数每个块所需的静态分配共享内存大小（以字节为单位）。不包括用户在运行时动态分配的共享内存。
- `HG_FUNC_ATTRIBUTE_CONST_SIZE_BYTES`：此函数所需的用户分配常量内存大小（以字节为单位）。
- `HG_FUNC_ATTRIBUTE_LOCAL_SIZE_BYTES`：此函数每个线程使用的本地内存大小（以字节为单位）。
- `HG_FUNC_ATTRIBUTE_NUM_REGS`：此函数每个线程使用的寄存器数量。
- `HG_FUNC_ATTRIBUTE_BINARY_VERSION`：函数编译时针对的二进制架构版本。此值为主二进制版本 * 10 + 次二进制版本，因此二进制版本 1.3 的函数将返回值 13。请注意，对于没有正确编码的二进制架构版本的旧 hgbin，将返回值 10。
- `HG_FUNC_CACHE_MODE_CA`：指示函数是否使用用户指定选项 "--llvm-options -ppu-dlcm=0" 编译的属性。
- `HG_FUNC_ATTRIBUTE_MAX_DYNAMIC_SHARED_SIZE_BYTES`：动态分配的共享内存的最大大小（以字节为单位）。
- `HG_FUNC_ATTRIBUTE_PREFERRED_SHARED_MEMORY_CARVEOUT`：首选共享内存-L1 缓存分割比例（占总共享内存的百分比）。
- `HG_FUNC_ATTRIBUTE_CLUSTER_SIZE_MUST_BE_SET`：如果设置此属性，则必须使用有效的集群大小启动核函数。
- `HG_FUNC_ATTRIBUTE_REQUIRED_CLUSTER_WIDTH`：所需的集群宽度（以块为单位）。
- `HG_FUNC_ATTRIBUTE_REQUIRED_CLUSTER_HEIGHT`：所需的集群高度（以块为单位）。
- `HG_FUNC_ATTRIBUTE_REQUIRED_CLUSTER_DEPTH`：所需的集群深度（以块为单位）。
- `HG_FUNC_ATTRIBUTE_NON_PORTABLE_CLUSTER_SIZE_ALLOWED`：指示函数是否可以以不可移植的集群大小启动。1 表示允许，0 表示不允许。不可移植的集群大小只能在测试程序的特定 SKU 上运行。如果在不同硬件平台上运行，启动可能会失败。HGGC API 提供相应接口来帮助检查当前设备是否可以启动所需大小。可移植的集群大小保证在所有高于目标计算能力的计算能力上都能正常工作。此值可能会在未来计算能力中增加。特定硬件单元可能支持更高的集群大小，但不能保证可移植性。
- `HG_FUNC_ATTRIBUTE_CLUSTER_SCHEDULING_POLICY_PREFERENCE`：函数的块调度策略。值类型为 HGclusterSchedulingPolicy。

除了少数例外，函数属性也可以在未加载的函数句柄上查询。如果属性需要完全加载的函数但函数未加载，则返回 HGGC_ERROR_FUNCTION_NOT_LOADD。以下属性需要函数完全加载后才能查询：

- `HG_FUNC_ATTRIBUTE_MAX_THREADS_PER_BLOCK`
- `HG_FUNC_ATTRIBUTE_CONST_SIZE_BYTES`
- `HG_FUNC_ATTRIBUTE_MAX_DYNAMIC_SHARED_SIZE_BYTES`

```c
HGresult hgFuncGetAttribute(int* pi,
                            HGfunction_attribute attrib,
                            HGfunction hfunc)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pi | out | 返回的属性值 |
| attrib | in | 请求的属性 |
| hfunc | in | 要查询属性的函数 |

| 错误码 | 触发条件 |
|--------|----------|
| [HGGC_ERROR_DEINITIALIZED](#driver-data-types) | HGGC 运行时已去初始化 |
| [HGGC_ERROR_NOT_INITIALIZED](#driver-data-types) | HGGC 运行时尚未初始化 |
| [HGGC_ERROR_INVALID_CONTEXT](#driver-data-types) | 提供了无效的上下文 |
| [HGGC_ERROR_INVALID_HANDLE](#driver-data-types) | 提供了无效的句柄 |
| [HGGC_ERROR_INVALID_VALUE](#driver-data-types) | 提供的值无效 |
| [HGGC_ERROR_FUNCTION_NOT_LOADED](#driver-data-types) | 函数尚未加载 |

---

#### 3. hgFuncGetModule {#hgfuncgetmodule}

在 `*hmod` 中返回函数 `hfunc` 所在模块的句柄。模块的生存期对应于加载它的上下文的生存期，直到模块被明确卸载为止。

HGGC 运行时管理加载到主上下文中的自己的模块。如果此 API 返回的句柄引用由 HGGC 运行时加载的模块，则对这些模块调用 hgModuleUnload() 会导致未定义的行为。

```c
HGresult hgFuncGetModule(HGmodule* hmod, HGfunction hfunc)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hmod | out | 返回的模块句柄 |
| hfunc | in | 要获取其模块的函数 |

| 错误码 | 触发条件 |
|--------|----------|
| [HGGC_ERROR_DEINITIALIZED](#driver-data-types) | HGGC 运行时已去初始化 |
| [HGGC_ERROR_NOT_INITIALIZED](#driver-data-types) | HGGC 运行时尚未初始化 |
| [HGGC_ERROR_INVALID_CONTEXT](#driver-data-types) | 提供了无效的上下文 |
| [HGGC_ERROR_INVALID_VALUE](#driver-data-types) | 提供的值无效 |
| [HGGC_ERROR_NOT_FOUND](#driver-data-types) | 未找到请求的元素 |

---

#### 4. hgFuncGetName {#hgfuncgetname}

在 `**name` 中返回与函数句柄 `hfunc` 关联的函数名称。函数名称作为以 null 结尾的字符串返回。当函数句柄有效时，返回的名称才有效。如果模块被卸载或重新加载，必须再次调用此 API 以获取更新的名称。如果函数未声明为具有 C 链接，则此 API 可能返回修饰后的名称。如果 `**name` 或 `hfunc` 为 NULL，则返回 HGGC_ERROR_INVALID_VALUE。

```c
HGresult hgFuncGetName(const char** name, HGfunction hfunc)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| name | out | 返回的函数名称 |
| hfunc | in | 要检索其名称的函数句柄 |

错误码：HGGC_ERROR_INVALID_VALUE

---

#### 5. hgFuncSetAttribute {#hgfuncsetattribute}

此调用将给定核函数 `hfunc` 的指定属性 `attrib` 的值设置为整数 `val`。如果可以成功设置属性的新值，则此函数返回 HGGC_SUCCESS。如果设置失败，则此调用将返回错误。并非所有属性都可以设置值。尝试设置只读属性的值将导致错误（HGGC_ERROR_INVALID_VALUE）。

hgFuncSetAttribute 调用支持的属性：

- `HG_FUNC_ATTRIBUTE_MAX_DYNAMIC_SHARED_SIZE_BYTES`：动态分配的共享内存的最大大小（以字节为单位）。此值应包含请求的动态分配共享内存的最大大小。此值与函数属性 `HG_FUNC_ATTRIBUTE_SHARED_SIZE_BYTES` 的和不能超过设备属性 `HG_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK_OPTIN`。可请求的动态共享内存的最大大小可能因 PPU 架构而异。
- `HG_FUNC_ATTRIBUTE_PREFERRED_SHARED_MEMORY_CARVEOUT`：在 L1 缓存和共享内存使用相同硬件资源的设备上，这设置共享内存 carveout 偏好（占总共享内存的百分比）。请参见 `HG_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_MULTIPROCESSOR`。这只是一个提示，驱动程序可以根据需要选择不同的比例来执行函数。
- `HG_FUNC_ATTRIBUTE_REQUIRED_CLUSTER_WIDTH`：所需的集群宽度（以块为单位）。宽度、高度和深度值必须全为 0 或全为正。集群维度的有效性在启动时检查。如果值在编译时设置，则不能在运行时设置。在运行时设置将返回 HGGC_ERROR_NOT_PERMITTED。
- `HG_FUNC_ATTRIBUTE_REQUIRED_CLUSTER_HEIGHT`：所需的集群高度（以块为单位）。宽度、高度和深度值必须全为 0 或全为正。集群维度的有效性在启动时检查。如果值在编译时设置，则不能在运行时设置。在运行时设置将返回 HGGC_ERROR_NOT_PERMITTED。
- `HG_FUNC_ATTRIBUTE_REQUIRED_CLUSTER_DEPTH`：所需的集群深度（以块为单位）。宽度、高度和深度值必须全为 0 或全为正。集群维度的有效性在启动时检查。如果值在编译时设置，则不能在运行时设置。在运行时设置将返回 HGGC_ERROR_NOT_PERMITTED。
- `HG_FUNC_ATTRIBUTE_NON_PORTABLE_CLUSTER_SIZE_ALLOWED`：指示函数是否可以以不可移植的集群大小启动。1 表示允许，0 表示不允许。
- `HG_FUNC_ATTRIBUTE_CLUSTER_SCHEDULING_POLICY_PREFERENCE`：函数的块调度策略。值类型为 HGclusterSchedulingPolicy。

```c
HGresult hgFuncSetAttribute(HGfunction hfunc,
                            HGfunction_attribute attrib,
                            int value)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hfunc | in | 要查询属性的函数 |
| attrib | in | 请求的属性 |
| value | in | 要设置的值 |

| 错误码 | 触发条件 |
|--------|----------|
| [HGGC_ERROR_DEINITIALIZED](#driver-data-types) | HGGC 运行时已去初始化 |
| [HGGC_ERROR_NOT_INITIALIZED](#driver-data-types) | HGGC 运行时尚未初始化 |
| [HGGC_ERROR_INVALID_CONTEXT](#driver-data-types) | 提供了无效的上下文 |
| [HGGC_ERROR_INVALID_HANDLE](#driver-data-types) | 提供了无效的句柄 |
| [HGGC_ERROR_INVALID_VALUE](#driver-data-types) | 提供的值无效 |

---

#### 6. hgFuncSetCacheConfig {#hgfuncsetcacheconfig}

在 L1 缓存和共享内存使用相同硬件资源的设备上，这通过 `config` 设置设备函数 `hfunc` 的首选缓存配置。这只是一个偏好。如果可能，驱动程序将使用请求的配置，但如果有需要执行 `hfunc`，它可以自由选择不同的配置。通过 hgCtxSetCacheConfig() 设置的任何上下文范围的偏好都会被此每个函数的设置覆盖，除非每个函数的设置是 `HG_FUNC_CACHE_PREFER_NONE`。在这种情况下，将使用当前的上下文范围设置。

此设置在 L1 缓存和共享内存大小固定的设备上不起作用。

使用与最新偏好设置不同的偏好启动核函数可能会插入设备端同步点。

支持的缓存配置：

- `HG_FUNC_CACHE_PREFER_NONE`：对共享内存或 L1 没有偏好（默认）
- `HG_FUNC_CACHE_PREFER_SHARED`：偏好更大的共享内存和更小的 L1 缓存
- `HG_FUNC_CACHE_PREFER_L1`：偏好更大的 L1 缓存和更小的共享内存
- `HG_FUNC_CACHE_PREFER_EQUAL`：偏好相同大小的 L1 缓存和共享内存

```c
HGresult hgFuncSetCacheConfig(HGfunction hfunc, HGfunc_cache config)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hfunc | in | 要配置缓存的核函数 |
| config | in | 请求的缓存配置 |

| 错误码 | 触发条件 |
|--------|----------|
| [HGGC_ERROR_INVALID_VALUE](#driver-data-types) | 提供的值无效 |
| [HGGC_ERROR_DEINITIALIZED](#driver-data-types) | HGGC 运行时已去初始化 |
| [HGGC_ERROR_NOT_INITIALIZED](#driver-data-types) | HGGC 运行时尚未初始化 |
| [HGGC_ERROR_INVALID_CONTEXT](#driver-data-types) | 提供了无效的上下文 |

---

#### 7. hgLaunchCooperativeKernel {#hglaunchcooperativekernel}

在 `gridDimX` x `gridDimY` x `gridDimZ` 网格的块上调用函数 [HGfunction](#driver-data-types) 或核函数 [HGkernel](#driver-data-types) `f`。每个块包含 `blockDimX` x `blockDimY` x `blockDimZ` 个线程。

`sharedMemBytes` 设置每个线程块可用的动态共享内存量。

启动此核函数的设备必须具有设备属性 `HG_DEVICE_ATTRIBUTE_COOPERATIVE_LAUNCH` 的非零值。

启动的块总数不能超过 hgOccupancyMaxActiveBlocksPerMultiprocessor（或 hgOccupancyMaxActiveBlocksPerMultiprocessorWithFlags）返回的每个多处理器的最大块数乘以设备属性 `HG_DEVICE_ATTRIBUTE_MULTIPROCESSOR_COUNT` 指定的多处理器数量。

核函数不能使用 HGGC 动态并行性。

核函数参数必须通过 `kernelParams` 指定。如果 `f` 有 N 个参数，则 `kernelParams` 需要是一个包含 N 个指针的数组。`kernelParams`[0] 到 `kernelParams`[N-1] 中的每一个都必须指向一块内存区域，实际的核函数参数将从该区域复制。核函数参数的数量及其偏移量和大小不需要指定，因为该信息直接从核函数映像中检索。

调用 hgLaunchCooperativeKernel() 设置的持久函数状态与通过 hgLaunchKernel API 设置的函数状态相同。

当通过 hgLaunchCooperativeKernel() 启动核函数 `f` 时，与 `f` 关联的先前块形状、共享大小和参数信息将被覆盖。

请注意，要使用 hgLaunchCooperativeKernel()，核函数 `f` 必须使用工具链版本 3.2 或更高版本编译，以便包含核函数参数信息，或者没有核函数参数。如果不满足这些条件中的任何一个，则 hgLaunchCooperativeKernel() 将返回 HGGC_ERROR_INVALID_IMAGE。

请注意，该 API 也可用于启动上下文无关核函数 [HGkernel](#driver-data-types)，方法是使用 hgLibraryGetKernel() 查询句柄，然后通过强制转换为 [HGfunction](#driver-data-types) 传递给 API。在这里，启动核函数的上下文将取自指定的流 `hStream`，或者在 NULL 流的情况下取自当前上下文。

```c
HGresult hgLaunchCooperativeKernel(HGfunction f,
                                   unsigned int gridDimX,
                                   unsigned int gridDimY,
                                   unsigned int gridDimZ,
                                   unsigned int blockDimX,
                                   unsigned int blockDimY,
                                   unsigned int blockDimZ,
                                   unsigned int sharedMemBytes,
                                   HGstream hStream,
                                   void** kernelParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| f | in | 要启动的函数 [HGfunction](#driver-data-types) 或核函数 [HGkernel](#driver-data-types) |
| gridDimX | in | 网格宽度（以块为单位） |
| gridDimY | in | 网格高度（以块为单位） |
| gridDimZ | in | 网格深度（以块为单位） |
| blockDimX | in | 每个线程块的 X 维度 |
| blockDimY | in | 每个线程块的 Y 维度 |
| blockDimZ | in | 每个线程块的 Z 维度 |
| sharedMemBytes | in | 每个线程块的动态共享内存大小（字节） |
| hStream | in | 流标识符 |
| kernelParams | in | 核函数参数数组 |

| 错误码 | 触发条件 |
|--------|----------|
| [HGGC_ERROR_DEINITIALIZED](#driver-data-types) | HGGC 运行时已去初始化 |
| [HGGC_ERROR_NOT_INITIALIZED](#driver-data-types) | HGGC 运行时尚未初始化 |
| [HGGC_ERROR_INVALID_CONTEXT](#driver-data-types) | 提供了无效的上下文 |
| [HGGC_ERROR_INVALID_HANDLE](#driver-data-types) | 提供了无效的句柄 |
| [HGGC_ERROR_INVALID_IMAGE](#driver-data-types) | 无效的核函数映像 |
| [HGGC_ERROR_INVALID_VALUE](#driver-data-types) | 提供的值无效 |
| [HGGC_ERROR_LAUNCH_FAILED](#driver-data-types) | 启动失败 |
| [HGGC_ERROR_LAUNCH_OUT_OF_RESOURCES](#driver-data-types) | 启动超出资源 |
| [HGGC_ERROR_LAUNCH_TIMEOUT](#driver-data-types) | 启动超时 |
| [HGGC_ERROR_LAUNCH_INCOMPATIBLE_TEXTURING](#driver-data-types) | 启动不兼容的纹理处理 |
| [HGGC_ERROR_COOPERATIVE_LAUNCH_TOO_LARGE](#driver-data-types) | 协作启动太大 |
| [HGGC_ERROR_SHARED_OBJECT_INIT_FAILED](#driver-data-types) | 共享对象初始化失败 |
| [HGGC_ERROR_NOT_FOUND](#driver-data-types) | 未找到请求的元素 |

---

#### 8. hgLaunchHostFunc {#hglaunchhostfunc}

在流中入队一个主机函数来运行。该函数将在当前入队的工作之后调用，并将阻塞在该函数之后添加的工作。

主机函数不得调用任何 HGGC API。尝试使用 HGGC API 可能导致 HGGC_ERROR_NOT_PERMITTED，但这不是必需的。主机函数不得执行可能依赖于先前 HGGC 工作（未指定更早运行）的任何同步。没有强制顺序的主机函数（如独立流中的函数）以未定义顺序执行，可能会被序列化。

出于统一内存的目的，执行会做出一些保证：
- 在函数执行期间，流被视为空闲。因此，例如，函数始终可以使用附加到其入队流的内存。
- 函数开始执行与在同一流中函数之前记录的事件具有相同的效果。因此，它会同步在函数之前"加入"的流。
- 向任何流添加设备工作不会使流变得活跃，直到所有前面 的主机函数和流回调都已执行。因此，例如，如果工作已使用事件排在函数调用之后，则函数可能使用全局附加内存（即使工作已添加到另一个流）。
- 函数的完成不会导致流变得活跃，除非如上所述。如果函数后面没有设备工作，流将保持空闲；如果连续的主机函数或流回调之间没有设备工作，流将在它们之间保持空闲。因此，例如，可以通过在流末尾从主机函数发信号来完成流同步。

请注意，与 hgStreamAddCallback 不同，在 HGGC 上下文出错的情况下不会调用该函数。

```c
HGresult hgLaunchHostFunc(HGstream hStream, HGhostFn fn, void* userData)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hStream | in | 要入队函数调用的流 |
| fn | in | 当前面的流操作完成后要调用的函数 |
| userData | in | 要传递给函数的用户指定数据 |

| 错误码 | 触发条件 |
|--------|----------|
| [HGGC_ERROR_DEINITIALIZED](#driver-data-types) | HGGC 运行时已去初始化 |
| [HGGC_ERROR_NOT_INITIALIZED](#driver-data-types) | HGGC 运行时尚未初始化 |
| [HGGC_ERROR_INVALID_CONTEXT](#driver-data-types) | 提供了无效的上下文 |
| [HGGC_ERROR_INVALID_HANDLE](#driver-data-types) | 提供了无效的句柄 |
| [HGGC_ERROR_NOT_SUPPORTED](#driver-data-types) | 不支持该操作 |

---

#### 9. hgLaunchKernel {#hglaunchkernel}

在 `gridDimX` x `gridDimY` x `gridDimZ` 网格的块上调用函数 [HGfunction](#driver-data-types) 或核函数 [HGkernel](#driver-data-types) `f`。每个块包含 `blockDimX` x `blockDimY` x `blockDimZ` 个线程。

`sharedMemBytes` 设置每个线程块可用的动态共享内存量。

可以通过以下两种方式之一指定 `f` 的核函数参数：

1. 核函数参数可以通过 `kernelParams` 指定。如果 `f` 有 N 个参数，则 `kernelParams` 需要是一个包含 N 个指针的数组。`kernelParams`[0] 到 `kernelParams`[N-1] 中的每一个都必须指向一块内存区域，实际的核函数参数将从该区域复制。

2. 核函数参数也可以由应用程序打包成单个缓冲区，通过 `extra` 参数传递。这将应用程序需要知道每个核函数参数在缓冲区中的大小和对齐/填充的负担。以下是使用 `extra` 参数的示例：

```c
HGfunction f;
unsigned int gx, gy, gz, bx, by, bz, sh;
HGstream s;
HGresult status;
size_t argBufferSize;
char argBuffer[256];

// populate argBuffer and argBufferSize

void *config[] = {
    HG_LAUNCH_PARAM_BUFFER_POINTER, argBuffer,
    HG_LAUNCH_PARAM_BUFFER_SIZE,    &argBufferSize,
    HG_LAUNCH_PARAM_END
};
status = hgLaunchKernel(f, gx, gy, gz, bx, by, bz, sh, s, NULL, config);
```

`extra` 参数存在是为了允许 hgLaunchKernel 接受其他不太常用的参数。`extra` 指定额外设置名称及其对应值的列表。每个额外设置名称后面紧跟其对应值。列表必须以 NULL 或 `HG_LAUNCH_PARAM_END` 终止。

- `HG_LAUNCH_PARAM_END`，表示 `extra` 数组的结束；
- `HG_LAUNCH_PARAM_BUFFER_POINTER`，指定 `extra` 中的下一个值将是指向缓冲区的指针，该缓冲区包含启动核函数 `f` 的所有核函数参数；
- `HG_LAUNCH_PARAM_BUFFER_SIZE`，指定 `extra` 中的下一个值将是指向 size_t 的指针，包含使用 `HG_LAUNCH_PARAM_BUFFER_POINTER` 指定的缓冲区的大小。

如果同时使用 `kernelParams` 和 `extra` 指定核函数参数（即两者都非 NULL），则将返回错误 HGGC_ERROR_INVALID_VALUE。

调用 hgLaunchKernel() 会使通过以下已弃用 API 设置的持久函数状态失效：hgFuncSetBlockShape()、hgFuncSetSharedSize()、hgParamSetSize()、hgParamSeti()、hgParamSetf()、hgParamSetv()。

请注意，要使用 hgLaunchKernel()，核函数 `f` 必须使用工具链版本 3.2 或更高版本编译，以便包含核函数参数信息，或者没有核函数参数。如果不满足这些条件中的任何一个，则 hgLaunchKernel() 将返回 HGGC_ERROR_INVALID_IMAGE。

请注意，该 API 也可用于启动上下文无关核函数 HGkernel，方法是使用 hgLibraryGetKernel() 查询句柄，然后通过强制转换为 HGfunction 传递给 API。在这里，启动核函数的上下文将取自指定的流 `hStream`，或者在 NULL 流的情况下取自当前上下文。

```c
HGresult hgLaunchKernel(HGfunction f,
                        unsigned int gridDimX,
                        unsigned int gridDimY,
                        unsigned int gridDimZ,
                        unsigned int blockDimX,
                        unsigned int blockDimY,
                        unsigned int blockDimZ,
                        unsigned int sharedMemBytes,
                        HGstream hStream,
                        void** kernelParams,
                        void** extra)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| f | in | 要启动的函数 [HGfunction](#driver-data-types) 或核函数 [HGkernel](#driver-data-types) |
| gridDimX | in | 网格宽度（以块为单位） |
| gridDimY | in | 网格高度（以块为单位） |
| gridDimZ | in | 网格深度（以块为单位） |
| blockDimX | in | 每个线程块的 X 维度 |
| blockDimY | in | 每个线程块的 Y 维度 |
| blockDimZ | in | 每个线程块的 Z 维度 |
| sharedMemBytes | in | 每个线程块的动态共享内存大小（字节） |
| hStream | in | 流标识符 |
| kernelParams | in | 核函数参数数组 |
| extra | in | 额外选项 |

| 错误码 | 触发条件 |
|--------|----------|
| [HGGC_ERROR_DEINITIALIZED](#driver-data-types) | HGGC 运行时已去初始化 |
| [HGGC_ERROR_NOT_INITIALIZED](#driver-data-types) | HGGC 运行时尚未初始化 |
| [HGGC_ERROR_INVALID_CONTEXT](#driver-data-types) | 提供了无效的上下文 |
| [HGGC_ERROR_INVALID_HANDLE](#driver-data-types) | 提供了无效的句柄 |
| [HGGC_ERROR_INVALID_IMAGE](#driver-data-types) | 无效的核函数映像 |
| [HGGC_ERROR_INVALID_VALUE](#driver-data-types) | 提供的值无效 |
| [HGGC_ERROR_LAUNCH_FAILED](#driver-data-types) | 启动失败 |
| [HGGC_ERROR_LAUNCH_OUT_OF_RESOURCES](#driver-data-types) | 启动超出资源 |
| [HGGC_ERROR_LAUNCH_TIMEOUT](#driver-data-types) | 启动超时 |
| [HGGC_ERROR_LAUNCH_INCOMPATIBLE_TEXTURING](#driver-data-types) | 启动不兼容的纹理处理 |
| [HGGC_ERROR_SHARED_OBJECT_INIT_FAILED](#driver-data-types) | 共享对象初始化失败 |
| [HGGC_ERROR_NOT_FOUND](#driver-data-types) | 未找到请求的元素 |

---

#### 10. hgLaunchKernelEx {#hglaunchkernelex}

使用指定的启动时配置 `config` 调用函数 [HGfunction](#driver-data-types) 或核函数 [HGkernel](#driver-data-types) `f`。

HGlaunchConfig 结构定义为：

```c
typedef struct HGlaunchConfig_st {
    unsigned int gridDimX;
    unsigned int gridDimY;
    unsigned int gridDimZ;
    unsigned int blockDimX;
    unsigned int blockDimY;
    unsigned int blockDimZ;
    unsigned int sharedMemBytes;
    HGstream     hStream;
    HGlaunchAttribute *attrs;
    unsigned int numAttrs;
} HGlaunchConfig;
```

其中：
- `HGlaunchConfig::gridDimX` 是网格的宽度（以块为单位）。
- `HGlaunchConfig::gridDimY` 是网格的高度（以块为单位）。
- `HGlaunchConfig::gridDimZ` 是网格的深度（以块为单位）。
- `HGlaunchConfig::blockDimX` 是每个线程块的 X 维度。
- `HGlaunchConfig::blockDimX` 是每个线程块的 Y 维度。
- `HGlaunchConfig::blockDimZ` 是每个线程块的 Z 维度。
- `HGlaunchConfig::sharedMemBytes` 是每个线程块的动态共享内存大小（字节）。
- `HGlaunchConfig::hStream` 是执行启动的流的句柄。与此流关联的 HGGC 上下文必须与函数 f 关联的上下文匹配。
- `HGlaunchConfig::attrs` 是一个数组，包含 `HGlaunchConfig::numAttrs` 个连续的 `HGlaunchAttribute` 元素。如果 `HGlaunchConfig::numAttrs` 为零，则不考虑此指针的值。但是，在这种情况下，将指针设置为 NULL。
- `HGlaunchConfig::numAttrs` 是填充 `HGlaunchConfig::attrs` 数组第一个 `HGlaunchConfig::numAttrs` 位置的属性数量。

启动时配置通过向 `HGlaunchConfig::attrs` 添加条目来指定。每个条目是一个属性 ID 和相应的属性值。

HGlaunchAttribute 结构定义为：

```c
typedef struct HGlaunchAttribute_st {
    HGlaunchAttributeID id;
    HGlaunchAttributeValue value;
} HGlaunchAttribute;
```

其中：
- `HGlaunchAttribute::id` 是标识属性的唯一枚举。
- `HGlaunchAttribute::value` 是一个联合，用于保存属性值。

使用 `config` 参数的示例：

```c
HGlaunchAttribute coopAttr = {.id = HG_LAUNCH_ATTRIBUTE_COOPERATIVE,
                              .value = 1};
HGlaunchConfig config = {... // set block and grid dimensions
                         .attrs = &coopAttr,
                         .numAttrs = 1};

hgLaunchKernelEx(&config, kernel, NULL, NULL);
```

HGlaunchAttributeID 枚举定义为：

```c
typedef enum HGlaunchAttributeID_enum {
    HG_LAUNCH_ATTRIBUTE_IGNORE = 0,
    HG_LAUNCH_ATTRIBUTE_ACCESS_POLICY_WINDOW = 1,
    HG_LAUNCH_ATTRIBUTE_COOPERATIVE = 2,
    HG_LAUNCH_ATTRIBUTE_SYNCHRONIZATION_POLICY = 3,
    HG_LAUNCH_ATTRIBUTE_CLUSTER_DIMENSION = 4,
    HG_LAUNCH_ATTRIBUTE_CLUSTER_SCHEDULING_POLICY_PREFERENCE = 5,
    HG_LAUNCH_ATTRIBUTE_PROGRAMMATIC_STREAM_SERIALIZATION = 6,
    HG_LAUNCH_ATTRIBUTE_PROGRAMMATIC_EVENT = 7,
    HG_LAUNCH_ATTRIBUTE_PRIORITY = 8,
    HG_LAUNCH_ATTRIBUTE_MEM_SYNC_DOMAIN_MAP = 9,
    HG_LAUNCH_ATTRIBUTE_MEM_SYNC_DOMAIN = 10,
    HG_LAUNCH_ATTRIBUTE_PREFERRED_CLUSTER_DIMENSION = 11,
    HG_LAUNCH_ATTRIBUTE_LAUNCH_COMPLETION_EVENT = 12,
    HG_LAUNCH_ATTRIBUTE_DEVICE_UPDATABLE_KERNEL_NODE = 13,
} HGlaunchAttributeID;
```

相应的 HGlaunchAttributeValue 联合定义为：

```c
typedef union HGlaunchAttributeValue_union {
    HGaccessPolicyWindow accessPolicyWindow;
    int cooperative;
    HGsynchronizationPolicy syncPolicy;
    struct {
        unsigned int x;
        unsigned int y;
        unsigned int z;
    } clusterDim;
    HGclusterSchedulingPolicy clusterSchedulingPolicyPreference;
    int programmaticStreamSerializationAllowed;
    struct {
        HGevent event;
        int flags;
        int triggerAtBlockStart;
    } programmaticEvent;
    int priority;
    HGlaunchMemSyncDomainMap memSyncDomainMap;
    HGlaunchMemSyncDomain memSyncDomain;
    struct {
        unsigned int x;
        unsigned int y;
        unsigned int z;
    } preferredClusterDim;
    struct {
        HGevent event;
        int flags;
    } launchCompletionEvent;
    struct {
        int deviceUpdatable;
        HGgraphDeviceNode devNode;
    } deviceUpdatableKernelNode;
} HGlaunchAttributeValue;
```

将 `HG_LAUNCH_ATTRIBUTE_COOPERATIVE` 设置为非零值会导致核函数启动成为协作启动，其用法和语义与 hgLaunchCooperativeKernel 完全相同。

将 `HG_LAUNCH_ATTRIBUTE_PROGRAMMATIC_STREAM_SERIALIZATION` 设置为非零值会导致核函数使用编程方式解析其流依赖——使 HGGC 运行时能够在其流中先前核函数请求重叠时，机会性地允许网格的执行与该先前核函数重叠。

`HG_LAUNCH_ATTRIBUTE_PROGRAMMATIC_EVENT` 与核函数启动一起记录事件。通过此启动属性记录的事件保证仅在关联核函数中的所有块触发事件后才会触发。块可以通过 launchdep.release 或相应的 HGGC 内置函数触发事件。如果 triggerAtBlockStart 设置为非 0，也可以在每个块执行开始时插入触发器。请注意，依赖方（包括调用 hgEventSynchronize() 的 CPU 线程）不能保证在释放时精确地观察释放。例如，hgEventSynchronize() 可能只会在关联的核函数完成很长时间后才观察事件触发。此记录类型主要用于在设备任务之间建立编程依赖。提供的事件不能是进程间或互操作事件。该事件必须禁用计时（即使用 `HG_EVENT_DISABLE_TIMING` 标志创建）。

`HG_LAUNCH_ATTRIBUTE_LAUNCH_COMPLETION_EVENT` 与核函数启动一起记录事件。名义上，事件在核函数的所有块都开始执行后触发一次。当前这是尽力而为的。如果核函数 B 对核函数 A 有启动完成依赖，B 可能会等待直到 A 完成。或者，B 的块可以在 A 的所有块开始之前开始，例如：
- 如果 B 可以声明 A 不可用的执行资源，例如它们运行在不同的 PPU 上。
- 如果 B 的优先级高于 A。

如果这种顺序反转可能导致死锁，请谨慎使用。提供的事件不能是进程间或互操作事件。该事件必须禁用计时（即必须使用 `HG_EVENT_DISABLE_TIMING` 标志创建）。

将 `HG_LAUNCH_ATTRIBUTE_DEVICE_UPDATABLE_KERNEL_NODE` 设置为 1 会导致捕获的启动产生的核函数节点可由设备更新。此属性特定于图，传递给非捕获流中的启动会导致错误。传递 0 或 1 以外的值是不允许的。

成功后，将通过 `HGlaunchAttributeValue::deviceUpdatableKernelNode::devNode` 返回句柄，可将其传递给各种设备端更新函数，以从另一个核函数内更新节点的核函数参数。

可设备更新的核函数节点相比常规核函数节点有额外限制。首先，可设备更新的节点不能通过 hgGraphDestroyNode 从其图中移除。此外，一旦选择加入此功能，节点就不能选择退出，任何将属性设置为 0 的尝试都会导致错误。包含一个或多个可设备更新节点的图也不允许多次实例化。

`HG_LAUNCH_ATTRIBUTE_PREFERRED_CLUSTER_DIMENSION` 允许核函数启动指定首选替代集群维度。块可以据此属性指定的维度分组（分组为"首选替代集群"），也可以使用 `HG_LAUNCH_ATTRIBUTE_CLUSTER_DIMENSION` 属性指定的维度分组（分组为"常规集群"）。"首选替代集群"的集群维度应是常规集群维度的整数倍且大于零。设备将尽力——按最佳 effort 原则——将线程块分组为首选集群，而不是分组为常规集群。当设备认为必要时（主要是在设备暂时耗尽启动较大首选集群所需的物理资源时），设备可能会切换到启动常规集群，以尝试尽可能多地利用物理设备资源。

每种类型的集群的枚举/坐标设置就好像网格仅由其类型的集群组成。例如，如果首选替代集群维度是常规集群维度的两倍，则可能同时存在索引为 (1,0,0) 的常规集群和索引为 (1,0,0) 的首选集群。在此示例中，首选替代集群 (1,0,0) 替换了常规集群 (2,0,0) 和 (3,0,0) 并将它们的块分组。

此属性仅在指定了常规集群维度时生效。首选替代集群维度必须是常规集群维度的整数倍且大于零，并且必须能被网格整除。它也不能超过核函数 `__launch_bounds__` 中设置的 `maxBlocksPerCluster`。否则，它必须小于驱动程序可以支持的最大值。否则，允许将此属性设置为在任何特定设备上无法容纳的物理值。

其他属性的效果与其通过持久 API 设置时的效果一致。

有关以下属性，请参见 hgStreamSetAttribute：
- `HG_LAUNCH_ATTRIBUTE_ACCESS_POLICY_WINDOW`
- `HG_LAUNCH_ATTRIBUTE_SYNCHRONIZATION_POLICY`

有关以下属性，请参见 hgFuncSetAttribute：
- `HG_LAUNCH_ATTRIBUTE_CLUSTER_DIMENSION`
- `HG_LAUNCH_ATTRIBUTE_CLUSTER_SCHEDULING_POLICY_PREFERENCE`

`f` 的核函数参数可以以与使用 hgLaunchKernel 相同的方式指定。

请注意，该 API 也可用于启动上下文无关核函数 HGkernel，方法是使用 hgLibraryGetKernel() 查询句柄，然后通过强制转换为 HGfunction 传递给 API。在这里，启动核函数的上下文将取自指定的流 `HGlaunchConfig::hStream`，或者在 NULL 流的情况下取自当前上下文。

```c
HGresult hgLaunchKernelEx(const HGlaunchConfig* config,
                          HGfunction f,
                          void** kernelParams,
                          void** extra)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| config | in | 启动配置 |
| f | in | 要启动的函数 [HGfunction](#driver-data-types) 或核函数 [HGkernel](#driver-data-types) |
| kernelParams | in | 核函数参数数组 |
| extra | in | 额外选项 |

| 错误码 | 触发条件 |
|--------|----------|
| [HGGC_ERROR_DEINITIALIZED](#driver-data-types) | HGGC 运行时已去初始化 |
| [HGGC_ERROR_NOT_INITIALIZED](#driver-data-types) | HGGC 运行时尚未初始化 |
| [HGGC_ERROR_INVALID_CONTEXT](#driver-data-types) | 提供了无效的上下文 |
| [HGGC_ERROR_INVALID_HANDLE](#driver-data-types) | 提供了无效的句柄 |
| [HGGC_ERROR_INVALID_IMAGE](#driver-data-types) | 无效的核函数映像 |
| [HGGC_ERROR_INVALID_VALUE](#driver-data-types) | 提供的值无效 |
| [HGGC_ERROR_LAUNCH_FAILED](#driver-data-types) | 启动失败 |
| [HGGC_ERROR_LAUNCH_OUT_OF_RESOURCES](#driver-data-types) | 启动超出资源 |
| [HGGC_ERROR_LAUNCH_TIMEOUT](#driver-data-types) | 启动超时 |
| [HGGC_ERROR_LAUNCH_INCOMPATIBLE_TEXTURING](#driver-data-types) | 启动不兼容的纹理处理 |
| [HGGC_ERROR_COOPERATIVE_LAUNCH_TOO_LARGE](#driver-data-types) | 协作启动太大 |
| [HGGC_ERROR_SHARED_OBJECT_INIT_FAILED](#driver-data-types) | 共享对象初始化失败 |
| [HGGC_ERROR_NOT_FOUND](#driver-data-types) | 未找到请求的元素 |

---

#### 11. hgOccupancyAvailableDynamicSMemPerBlock {#hgoccupancyavailabledynamicsmemperblock}

在 `*dynamicSmemSize` 中返回允许 `numBlocks` 个块每个 SM 使用的动态共享内存的最大大小。

请注意，此 API 也可以与无上下文核函数 [HGkernel](#driver-data-types) 一起使用，方法是使用 [hgLibraryGetKernel()](#hglibrarygetkernel) 查询句柄，然后通过转换传递给 API 为 [HGfunction](#driver-data-types)。此处，用于计算上下文的是当前上下文。

!!! note
    请注意，此函数也可能返回先前异步启动的错误代码。

```c
HGresult hgOccupancyAvailableDynamicSMemPerBlock (size_t* dynamicSmemSize,
                                                  HGfunction func,
                                                  int numBlocks,
                                                  int blockSize)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dynamicSmemSize | out | 返回的最大动态共享内存大小 |
| func | in | 计算占用率的核函数 |
| numBlocks | in | 要容纳在 SM 上的块数 |
| blockSize | in | 块的大小 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_UNKNOWN

---

#### 12. hgOccupancyMaxActiveBlocksPerMultiprocessor {#hgoccupancymaxactiveblockspermultiprocessor}

在 `*numBlocks` 中返回每个流式多处理器最大活动块数。

请注意，此 API 也可以与无上下文核函数 [HGkernel](#driver-data-types) 一起使用，方法是使用 [hgLibraryGetKernel()](#hglibrarygetkernel) 查询句柄，然后通过转换传递给 API 为 [HGfunction](#driver-data-types)。此处，用于计算上下文的是当前上下文。

!!! note "请参阅"
    [hggcOccupancyMaxActiveBlocksPerMultiprocessor](04_runtime_api.md#hggcoccupancymaxactiveblockspermultiprocessor)

```c
HGresult hgOccupancyMaxActiveBlocksPerMultiprocessor (int* numBlocks,
                                                      HGfunction func,
                                                      int blockSize,
                                                      size_t dynamicSMemSize)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| numBlocks | out | 返回的占用率 |
| func | in | 计算占用率的核函数 |
| blockSize | in | 核函数打算启动的块大小 |
| dynamicSMemSize | in | 预期的每块动态共享内存使用量（字节） |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_UNKNOWN

---

#### 13. hgOccupancyMaxActiveBlocksPerMultiprocessorWithFlags {#hgoccupancymaxactiveblockspermultiprocessorwithflags}

在 `*numBlocks` 中返回每个流式多处理器最大活动块数。

`Flags` 参数控制特殊情况的处理方式。有效标志包括：

- [HG_OCCUPANCY_DEFAULT](#driver-data-types)：保持与 [hgOccupancyMaxActiveBlocksPerMultiprocessor](#hgoccupancymaxactiveblockspermultiprocessor) 相同的默认行为；
- [HG_OCCUPANCY_DISABLE_CACHING_OVERRIDE](#driver-data-types)：在全局缓存影响占用率的平台上，抑制默认行为。在此类平台上，如果启用了缓存，但每块 SM 资源使用将导致零占用率，占用率计算器将如同缓存被禁用一样计算占用率。设置 [HG_OCCUPANCY_DISABLE_CACHING_OVERRIDE](#driver-data-types) 可使占用率计算器在这种情况下返回 0。

请注意，此 API 也可以与无上下文核函数 [HGkernel](#driver-data-types) 一起使用，方法是使用 [hgLibraryGetKernel()](#hglibrarygetkernel) 查询句柄，然后通过转换传递给 API 为 [HGfunction](#driver-data-types)。此处，用于计算上下文的是当前上下文。

!!! note "请参阅"
    [hggcOccupancyMaxActiveBlocksPerMultiprocessorWithFlags](04_runtime_api.md#hggcoccupancymaxactiveblockspermultiprocessorwithflags)

```c
HGresult hgOccupancyMaxActiveBlocksPerMultiprocessorWithFlags (int* numBlocks,
                                                               HGfunction func,
                                                               int blockSize,
                                                               size_t dynamicSMemSize,
                                                               unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| numBlocks | out | 返回的占用率 |
| func | in | 计算占用率的核函数 |
| blockSize | in | 核函数打算启动的块大小 |
| dynamicSMemSize | in | 预期的每块动态共享内存使用量（字节） |
| flags | in | 请求的占用率计算器行为 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_UNKNOWN

---

#### 14. hgOccupancyMaxPotentialBlockSize {#hgoccupancymaxpotentialblocksize}

在 `*blockSize` 中返回一个可达到最大占用率（或每个多处理器最少块的最大活动线程束数）的合理块大小，在 `*minGridSize` 中返回达到最大占用率所需的最小网格大小。

如果 `blockSizeLimit` 为 0，则配置器将使用设备/函数允许的最大块大小。

如果不需要每块动态共享内存分配，则开发者应将 `blockSizeToDynamicSMemSize` 和 `dynamicSMemSize` 都保留为 0。

如果需要每块动态共享内存分配，并且动态共享内存大小是恒定的（不随块大小变化），则大小应通过 `dynamicSMemSize` 传递，`blockSizeToDynamicSMemSize` 应为 NULL。

否则，如果每块动态共享内存大小随不同块大小变化，则开发者需要通过 `blockSizeToDynamicSMemSize` 提供一个一元函数来计算 `func` 对于任何给定块大小所需的动态共享内存。`dynamicSMemSize` 被忽略。示例签名如下：

```c
// 接收块大小，返回所需的动态共享内存
size_t blockToSmem(int blockSize);
```

请注意，此 API 也可以与无上下文核函数 [HGkernel](#driver-data-types) 一起使用，方法是使用 [hgLibraryGetKernel()](#hglibrarygetkernel) 查询句柄，然后通过转换传递给 API 为 [HGfunction](#driver-data-types)。此处，用于计算上下文的是当前上下文。

!!! note "请参阅"
    [hggcOccupancyMaxPotentialBlockSize](04_runtime_api.md#hggcoccupancymaxpotentialblocksize)

```c
HGresult hgOccupancyMaxPotentialBlockSize (int* minGridSize,
                                           int* blockSize,
                                           HGfunction func,
                                           HGoccupancyB2DSize blockSizeToDynamicSMemSize,
                                           size_t dynamicSMemSize,
                                           int blockSizeLimit)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| minGridSize | out | 返回达到最大占用率所需的最小网格大小 |
| blockSize | out | 返回可达到最大占用率的最大块大小 |
| func | in | 计算启动配置的核函数 |
| blockSizeToDynamicSMemSize | in | 一个函数，根据块大小计算 `func` 使用的每块动态共享内存 |
| dynamicSMemSize | in | 预期的动态共享内存使用量（字节） |
| blockSizeLimit | in | `func` 设计处理的最大块大小 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_UNKNOWN

---

#### 15. hgOccupancyMaxPotentialBlockSizeWithFlags {#hgoccupancymaxpotentialblocksizewithflags}

[hgOccupancyMaxPotentialBlockSize](#hgoccupancymaxpotentialblocksize) 的扩展版本。除了传递给 [hgOccupancyMaxPotentialBlockSize](#hgoccupancymaxpotentialblocksize) 的参数外，[hgOccupancyMaxPotentialBlockSizeWithFlags](#hgoccupancymaxpotentialblocksizewithflags) 还接受一个 `Flags` 参数。

`Flags` 参数控制特殊情况的处理方式。有效标志包括：

- [HG_OCCUPANCY_DEFAULT](#driver-data-types)：保持与 [hgOccupancyMaxPotentialBlockSize](#hgoccupancymaxpotentialblocksize) 相同的默认行为；
- [HG_OCCUPANCY_DISABLE_CACHING_OVERRIDE](#driver-data-types)：在全局缓存影响占用率的平台上，抑制默认行为。在此类平台上，产生最大占用率的启动配置可能不支持全局缓存。设置 [HG_OCCUPANCY_DISABLE_CACHING_OVERRIDE](#driver-data-types) 可保证生成的启动配置与全局缓存兼容，但可能会牺牲占用率。

请注意，此 API 也可以与无上下文核函数 [HGkernel](#driver-data-types) 一起使用，方法是使用 [hgLibraryGetKernel()](#hglibrarygetkernel) 查询句柄，然后通过转换传递给 API 为 [HGfunction](#driver-data-types)。此处，用于计算上下文的是当前上下文。

!!! note "请参阅"
    [hggcOccupancyMaxPotentialBlockSizeWithFlags](04_runtime_api.md#hggcoccupancymaxpotentialblocksizewithflags)

```c
HGresult hgOccupancyMaxPotentialBlockSizeWithFlags (int* minGridSize,
                                                    int* blockSize,
                                                    HGfunction func,
                                                    HGoccupancyB2DSize blockSizeToDynamicSMemSize,
                                                    size_t dynamicSMemSize,
                                                    int blockSizeLimit,
                                                    unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| minGridSize | out | 返回达到最大占用率所需的最小网格大小 |
| blockSize | out | 返回可达到最大占用率的最大块大小 |
| func | in | 计算启动配置的核函数 |
| blockSizeToDynamicSMemSize | in | 一个函数，根据块大小计算 `func` 使用的每块动态共享内存 |
| dynamicSMemSize | in | 预期的动态共享内存使用量（字节） |
| blockSizeLimit | in | `func` 设计处理的最大块大小 |
| flags | in | 选项 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_UNKNOWN

---

### 7.2. 图管理 {#graph-mgmt}

本模块提供**图（Graph）管理**接口。HGGC Graph 允许将一系列操作预定义为 DAG，一次性提交以减少启动开销。

本节介绍低级 HGGC 驱动程序应用程序编程接口的图管理函数。

#### 1. 接口一览 {#接口一览}

| 函数 | 用途 |
|------|------|
| [hgDeviceGetGraphMemAttribute](#hgdevicegetgraphmemattribute) | 查询与图相关的异步分配属性 |
| [hgDeviceGraphMemTrim](#hgdevicegraphmemtrim) | 释放缓存在指定设备上供图使用的未使用内存，将其返回给操作系统 |
| [hgDeviceSetGraphMemAttribute](#hgdevicesetgraphmemattribute) | 设置与图相关的异步分配属性 |
| [hgGraphAddBatchMemOpNode](#hggraphaddbatchmemopnode) | 创建批量内存操作节点并将其添加到图中 |
| [hgGraphAddChildGraphNode](#hggraphaddchildgraphnode) | 创建子图节点并将其添加到图中 |
| [hgGraphAddDependencies](#hggraphadddependencies) | 向图中添加依赖边 |
| [hgGraphAddEmptyNode](#hggraphaddemptynode) | 创建空节点并将其添加到图中 |
| [hgGraphAddEventRecordNode](#hggraphaddeventrecordnode) | 创建事件记录节点并将其添加到图中 |
| [hgGraphAddEventWaitNode](#hggraphaddeventwaitnode) | 创建事件等待节点并将其添加到图中 |
| [hgGraphAddHostNode](#hggraphaddhostnode) | 创建主机执行节点并将其添加到图中 |
| [hgGraphAddKernelNode](#hggraphaddkernelnode) | 创建核函数执行节点并将其添加到图中 |
| [hgGraphAddMemAllocNode](#hggraphaddmemallocnode) | 创建分配节点并将其添加到图中 |
| [hgGraphAddMemFreeNode](#hggraphaddmemfreenode) | 创建内存释放节点并将其添加到图中 |
| [hgGraphAddMemcpyNode](#hggraphaddmemcpynode) | 创建内存拷贝节点并将其添加到图中 |
| [hgGraphAddMemsetNode](#hggraphaddmemsetnode) | 创建内存设置节点并将其添加到图中 |
| [hgGraphAddNode](#hggraphaddnode) | 向图中添加任意类型的节点 |
| [hgGraphBatchMemOpNodeGetParams](#hggraphbatchmemopnodegetparams) | 返回批量内存操作节点的参数 |
| [hgGraphBatchMemOpNodeSetParams](#hggraphbatchmemopnodesetparams) | 设置批量内存操作节点的参数 |
| [hgGraphChildGraphNodeGetGraph](#hggraphchildgraphnodegetgraph) | 获取子图节点嵌入图的句柄 |
| [hgGraphClone](#hggraphclone) | 克隆图 |
| [hgGraphConditionalHandleCreate](#hggraphconditionalhandlecreate) | 创建条件句柄 |
| [hgGraphCreate](#hggraphcreate) | 创建图 |
| [hgGraphDebugDotPrint](#hggraphdebugdotprint) | 编写描述图结构的 DOT 文件 |
| [hgGraphDestroy](#hggraphdestroy) | 销毁图 |
| [hgGraphDestroyNode](#hggraphdestroynode) | 从图中移除节点 |
| [hgGraphEventRecordNodeGetEvent](#hggrapheventrecordnodegetevent) | 返回与事件记录节点关联的事件 |
| [hgGraphEventRecordNodeSetEvent](#hggrapheventrecordnodesetevent) | 设置事件记录节点的事件 |
| [hgGraphEventWaitNodeGetEvent](#hggrapheventwaitnodegetevent) | 返回与事件等待节点关联的事件 |
| [hgGraphEventWaitNodeSetEvent](#hggrapheventwaitnodesetevent) | 设置事件等待节点的事件 |
| [hgGraphExecBatchMemOpNodeSetParams](#hggraphexecbatchmemopnodesetparams) | 设置给定可执行图中批量内存操作节点的参数 |
| [hgGraphExecChildGraphNodeSetParams](#hggraphexecchildgraphnodesetparams) | 更新给定可执行图中子图节点的节点参数 |
| [hgGraphExecDestroy](#hggraphexecdestroy) | 销毁可执行图 |
| [hgGraphExecEventRecordNodeSetEvent](#hggraphexeceventrecordnodesetevent) | 设置给定可执行图中事件记录节点的事件 |
| [hgGraphExecEventWaitNodeSetEvent](#hggraphexeceventwaitnodesetevent) | 设置给定可执行图中事件等待节点的事件 |
| [hgGraphExecGetFlags](#hggraphexecgetflags) | 查询可执行图的实例化标志 |
| [hgGraphExecHostNodeSetParams](#hggraphexechostnodesetparams) | 设置给定可执行图中主机节点的参数 |
| [hgGraphExecKernelNodeSetParams](#hggraphexeckernelnodesetparams) | 设置给定可执行图中核函数节点的参数 |
| [hgGraphExecMemcpyNodeSetParams](#hggraphexecmemcpynodesetparams) | 设置给定可执行图中内存拷贝节点的参数 |
| [hgGraphExecMemsetNodeSetParams](#hggraphexecmemsetnodesetparams) | 设置给定可执行图中内存设置节点的参数 |
| [hgGraphExecNodeSetParams](#hggraphexecnodesetparams) | 更新实例化图中图节点的参数 |
| [hgGraphExecUpdate](#hggraphexecupdate) | 检查可执行图是否可以使用图进行更新，并在可能的情况下执行更新 |
| [hgGraphGetEdges](#hggraphgetedges) | 返回图的依赖边 |
| [hgGraphGetNodes](#hggraphgetnodes) | 返回图的节点 |
| [hgGraphGetRootNodes](#hggraphgetrootnodes) | 返回图的根节点 |
| [hgGraphHostNodeGetParams](#hggraphhostnodegetparams) | 返回主机节点的参数 |
| [hgGraphHostNodeSetParams](#hggraphhostnodesetparams) | 设置主机节点的参数 |
| [hgGraphInstantiate](#hggraphinstantiate) | 将图 `hGraph` 实例化为可执行图 `phGraphExec` |
| [hgGraphInstantiateWithParams](#hggraphinstantiatewithparams) | 使用详细参数将图实例化为可执行图 |
| [hgGraphKernelNodeCopyAttributes](#hggraphkernelnodecopyattributes) | 将属性从源节点复制到目标节点 |
| [hgGraphKernelNodeGetAttribute](#hggraphkernelnodegetattribute) | 查询节点属性 |
| [hgGraphKernelNodeGetParams](#hggraphkernelnodegetparams) | 返回核函数节点的参数 |
| [hgGraphKernelNodeSetAttribute](#hggraphkernelnodesetattribute) | 设置节点属性 |
| [hgGraphKernelNodeSetParams](#hggraphkernelnodesetparams) | 设置核函数节点的参数 |
| [hgGraphLaunch](#hggraphlaunch) | 在流中启动可执行图 |
| [hgGraphMemAllocNodeGetParams](#hggraphmemallocnodegetparams) | 返回内存分配节点的参数 |
| [hgGraphMemFreeNodeGetParams](#hggraphmemfreenodegetparams) | 返回内存释放节点的参数 |
| [hgGraphMemcpyNodeGetParams](#hggraphmemcpynodegetparams) | 返回内存拷贝节点的参数 |
| [hgGraphMemcpyNodeSetParams](#hggraphmemcpynodesetparams) | 设置内存拷贝节点的参数 |
| [hgGraphMemsetNodeGetParams](#hggraphmemsetnodegetparams) | 返回内存设置节点的参数 |
| [hgGraphMemsetNodeSetParams](#hggraphmemsetnodesetparams) | 设置内存设置节点的参数 |
| [hgGraphNodeFindInClone](#hggraphnodefindinclone) | 查找节点的克隆版本 |
| [hgGraphNodeGetDependencies](#hggraphnodegetdependencies) | 返回节点的依赖项 |
| [hgGraphNodeGetDependentNodes](#hggraphnodegetdependentnodes) | 返回节点的依赖节点 |
| [hgGraphNodeGetType](#hggraphnodegettype) | 返回节点类型 |
| [hgGraphNodeSetParams](#hggraphnodesetparams) | 更新图节点的参数 |
| [hgGraphReleaseUserObject](#hggraphreleaseuserobject) | 从图中释放用户对象引用 |
| [hgGraphRemoveDependencies](#hggraphremovedependencies) | 从图中移除依赖边 |
| [hgGraphRetainUserObject](#hggraphretainuserobject) | 从图中保留用户对象的引用 |
| [hgGraphUpload](#hggraphupload) | 在流中上传可执行图 |
| [hgUserObjectCreate](#hguserobjectcreate) | 创建用户对象 |
| [hgUserObjectRelease](#hguserobjectrelease) | 释放用户对象的引用 |
| [hgUserObjectRetain](#hguserobjectretain) | 保留用户对象的引用 |

---

#### 2. hgDeviceGetGraphMemAttribute {#hgdevicegetgraphmemattribute}

有效的属性包括：

- [HG_GRAPH_MEM_ATTR_USED_MEM_CURRENT](#driver-data-types)：当前与图关联的内存量（字节）。
- [HG_GRAPH_MEM_ATTR_USED_MEM_HIGH](#driver-data-types)：自上次重置以来与图关联的内存高水位线（字节）。高水位线只能重置为零。
- [HG_GRAPH_MEM_ATTR_RESERVED_MEM_CURRENT](#driver-data-types)：当前分配供 HGGC 图异步分配器使用的内存量（字节）。
- [HG_GRAPH_MEM_ATTR_RESERVED_MEM_HIGH](#driver-data-types)：当前分配供 HGGC 图异步分配器使用的内存高水位线（字节）。

```c
HGresult hgDeviceGetGraphMemAttribute (HGdevice device,
                                       HGgraphMem_attribute attr,
                                       void* value)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| device | in | 指定查询的范围 |
| attr | in | 要获取的属性 |
| value | out | 返回的值 |

错误码：HGGC_ERROR_INVALID_DEVICE

---

#### 3. hgDeviceGraphMemTrim {#hgdevicegraphmemtrim}

当前未使用的且既不在执行中也不在调度执行计划中的图块将被释放回操作系统。

```c
HGresult hgDeviceGraphMemTrim (HGdevice device)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| device | in | 要释放缓存内存的设备。 |

错误码：HGGC_ERROR_INVALID_DEVICE

---

#### 4. hgDeviceSetGraphMemAttribute {#hgdevicesetgraphmemattribute}

有效的属性包括：

- [HG_GRAPH_MEM_ATTR_USED_MEM_HIGH](#driver-data-types)：自上次重置以来与图关联的内存高水位线（字节）。高水位线只能重置为零。
- [HG_GRAPH_MEM_ATTR_RESERVED_MEM_HIGH](#driver-data-types)：当前分配供 HGGC 图异步分配器使用的内存高水位线（字节）。

```c
HGresult hgDeviceSetGraphMemAttribute (HGdevice device,
                                       HGgraphMem_attribute attr,
                                       void* value)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| device | in | 指定查询的范围 |
| attr | in | 要设置的属性 |
| value | in | 要设置的值 |

错误码：HGGC_ERROR_INVALID_DEVICE

---

#### 5. hgGraphAddBatchMemOpNode {#hggraphaddbatchmemopnode}

创建新的批量内存操作节点，并使用通过 `dependencies` 指定的 `numDependencies` 个依赖项和 `nodeParams` 中指定的参数将其添加到 `hGraph`。`numDependencies` 可以为 0，此时节点将放置在图的根节点处。`dependencies` 不能包含任何重复条目。新节点的句柄将通过 `phGraphNode` 返回。

当节点被添加时，`nodeParams` 内部的 paramArray 会被复制，因此调用返回后可以释放它。

```c
HGresult hgGraphAddBatchMemOpNode (HGgraphNode* phGraphNode,
                                   HGgraph hGraph,
                                   const HGgraphNode* dependencies,
                                   size_t numDependencies,
                                   const HGGC_BATCH_MEM_OP_NODE_PARAMS* nodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| phGraphNode | out | 返回新创建的节点 |
| hGraph | in | 要添加节点的图 |
| dependencies | in | 节点的依赖项 |
| numDependencies | in | 依赖项数量 |
| nodeParams | in | 节点的参数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_NOT_SUPPORTED、HGGC_ERROR_INVALID_VALUE

---

#### 6. hgGraphAddChildGraphNode {#hggraphaddchildgraphnode}

创建新的子图节点并将其添加到 `hGraph`。`numDependencies` 可以为 0，此时节点将放置在图的根节点处。`dependencies` 不能包含任何重复条目。新节点的句柄将通过 `phGraphNode` 返回。子图通过此 API 被引用，而不是被克隆，因此对原始图的修改会影响子图节点。

```c
HGresult hgGraphAddChildGraphNode (HGgraphNode* phGraphNode,
                                   HGgraph hGraph,
                                   const HGgraphNode* dependencies,
                                   size_t numDependencies,
                                   HGgraph childGraph)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| phGraphNode | out | 返回新创建的节点 |
| hGraph | in | 要添加节点的图 |
| dependencies | in | 节点的依赖项 |
| numDependencies | in | 依赖项数量 |
| childGraph | in | 要克隆到此节点中的图 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 7. hgGraphAddDependencies {#hggraphadddependencies}

要添加的依赖项数量由 `numDependencies` 定义。`from` 和 `to` 中对应索引处的元素定义一个依赖项。`from` 和 `to` 中的每个节点必须属于 `hGraph`。

如果 `numDependencies` 为 0，则 `from` 和 `to` 中的元素将忽略。指定图中不存在的边（带有与 `edgeData` 匹配的数据）会导致错误。`edgeData` 可为空，相当于为每条边传递默认（零值）数据。

不能向包含分配或释放节点的图添加依赖项。任何此类尝试都将返回错误。

```c
HGresult hgGraphAddDependencies (HGgraph hGraph,
                                 const HGgraphNode* from,
                                 const HGgraphNode* to,
                                 const HGgraphEdgeData* edgeData,
                                 size_t numDependencies)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraph | in | 要添加依赖项的图 |
| from | in | 提供依赖项的节点数组 |
| to | in | 依赖节点数组 |
| edgeData | in | 边的可选数据数组。如果为 NULL，则假定边数据为默认（零值）。 |
| numDependencies | in | 要添加的依赖项数量 |

错误码：HGGC_ERROR_INVALID_VALUE

---

#### 8. hgGraphAddEmptyNode {#hggraphaddemptynode}

创建新的空节点并将其添加到 `hGraph`。`numDependencies` 可以为 0，此时节点将放置在图的根节点处。`dependencies` 不能包含任何重复条目。新节点的句柄将通过 `phGraphNode` 返回。

空节点可用作依赖项的占位符，在执行图时会产生 noop。

```c
HGresult hgGraphAddEmptyNode (HGgraphNode* phGraphNode,
                              HGgraph hGraph,
                              const HGgraphNode* dependencies,
                              size_t numDependencies)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| phGraphNode | out | 返回新创建的节点 |
| hGraph | in | 要添加节点的图 |
| dependencies | in | 节点的依赖项 |
| numDependencies | in | 依赖项数量 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 9. hgGraphAddEventRecordNode {#hggraphaddeventrecordnode}

创建新的事件记录节点并将其添加到 `hGraph`。`numDependencies` 可以为 0，此时节点将放置在图的根节点处。`dependencies` 不能包含任何重复条目。新节点的句柄将通过 `phGraphNode` 返回。

当执行到该节点时，`event` 会 record 到图执行所在 stream 中该节点所处的位置。

```c
HGresult hgGraphAddEventRecordNode (HGgraphNode* phGraphNode,
                                    HGgraph hGraph,
                                    const HGgraphNode* dependencies,
                                    size_t numDependencies,
                                    HGevent event)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| phGraphNode | out | 返回新创建的节点 |
| hGraph | in | 要添加节点的图 |
| dependencies | in | 节点的依赖项 |
| numDependencies | in | 依赖项数量 |
| event | in | 要 record 的事件 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 10. hgGraphAddEventWaitNode {#hggraphaddeventwaitnode}

创建新的事件等待节点并将其添加到 `hGraph`。`numDependencies` 可以为 0，此时节点将放置在图的根节点处。`dependencies` 不能包含任何重复条目。新节点的句柄将通过 `phGraphNode` 返回。

当执行到该节点时，在图执行所在的 stream 中，该节点处会等待 `event` 完成。

```c
HGresult hgGraphAddEventWaitNode (HGgraphNode* phGraphNode,
                                  HGgraph hGraph,
                                  const HGgraphNode* dependencies,
                                  size_t numDependencies,
                                  HGevent event)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| phGraphNode | out | 返回新创建的节点 |
| hGraph | in | 要添加节点的图 |
| dependencies | in | 节点的依赖项 |
| numDependencies | in | 依赖项数量 |
| event | in | 要等待的事件 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 11. hgGraphAddHostNode {#hggraphaddhostnode}

创建新的主机执行节点并将其添加到 `hGraph`。`numDependencies` 可以为 0，此时节点将放置在图的根节点处。`dependencies` 不能包含任何重复条目。新节点的句柄将通过 `phGraphNode` 返回。

当节点被添加时，`nodeParams` 内部的数据会被复制，因此调用返回后可以释放它。

```c
HGresult hgGraphAddHostNode (HGgraphNode* phGraphNode,
                             HGgraph hGraph,
                             const HGgraphNode* dependencies,
                             size_t numDependencies,
                             const HGGC_HOST_NODE_PARAMS* nodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| phGraphNode | out | 返回新创建的节点 |
| hGraph | in | 要添加节点的图 |
| dependencies | in | 节点的依赖项 |
| numDependencies | in | 依赖项数量 |
| nodeParams | in | 节点的参数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 12. hgGraphAddKernelNode {#hggraphaddkernelnode}

创建新的核函数执行节点并将其添加到 `hGraph`。`numDependencies` 可以为 0，此时节点将放置在图的根节点处。`dependencies` 不能包含任何重复条目。新节点的句柄将通过 `phGraphNode` 返回。

当节点被添加时，`nodeParams` 内部的数据会被复制，因此调用返回后可以释放它。

```c
HGresult hgGraphAddKernelNode (HGgraphNode* phGraphNode,
                               HGgraph hGraph,
                               const HGgraphNode* dependencies,
                               size_t numDependencies,
                               const HGGC_KERNEL_NODE_PARAMS* nodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| phGraphNode | out | 返回新创建的节点 |
| hGraph | in | 要添加节点的图 |
| dependencies | in | 节点的依赖项 |
| numDependencies | in | 依赖项数量 |
| nodeParams | in | 节点的参数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 13. hgGraphAddMemAllocNode {#hggraphaddmemallocnode}

创建新的内存分配节点并将其添加到 `hGraph`。`numDependencies` 可以为 0，此时节点将放置在图的根节点处。`dependencies` 不能包含任何重复条目。新节点的句柄将通过 `phGraphNode` 返回。

分配节点是 HGGC 图异步内存分配接口的一部分。它们允许图在执行时动态分配内存，而不必预先分配所有内存。分配节点应与释放节点配对以确保内存不会泄漏。

当节点被添加时，`nodeParams` 内部的数据会被复制，因此调用返回后可以释放它（除非返回值通过 `nodeParams->dptr` 传递，该值在节点执行前不会被解析）。

```c
HGresult hgGraphAddMemAllocNode (HGgraphNode* phGraphNode,
                                 HGgraph hGraph,
                                 const HGgraphNode* dependencies,
                                 size_t numDependencies,
                                 HGGC_MEM_ALLOC_NODE_PARAMS* nodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| phGraphNode | out | 返回新创建的节点 |
| hGraph | in | 要添加节点的图 |
| dependencies | in | 节点的依赖项 |
| numDependencies | in | 依赖项数量 |
| nodeParams | in | 节点的参数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 14. hgGraphAddMemFreeNode {#hggraphaddmemfreenode}

创建新的内存释放节点并将其添加到 `hGraph`。`numDependencies` 可以为 0，此时节点将放置在图的根节点处。`dependencies` 不能包含任何重复条目。新节点的句柄将通过 `phGraphNode` 返回。

释放节点应与分配节点配对以确保内存不会泄漏。

```c
HGresult hgGraphAddMemFreeNode (HGgraphNode* phGraphNode,
                                HGgraph hGraph,
                                const HGgraphNode* dependencies,
                                size_t numDependencies,
                                HGdeviceptr dptr)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| phGraphNode | out | 返回新创建的节点 |
| hGraph | in | 要添加节点的图 |
| dependencies | in | 节点的依赖项 |
| numDependencies | in | 依赖项数量 |
| dptr | in | 要释放的设备指针 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 15. hgGraphAddMemcpyNode {#hggraphaddmemcpynode}

创建新的内存复制节点并将其添加到 `hGraph`。`numDependencies` 可以为 0，此时节点将放置在图的根节点处。`dependencies` 不能包含任何重复条目。新节点的句柄将通过 `phGraphNode` 返回。

当节点被添加时，`copyParams` 内部的数据会被复制，因此调用返回后可以释放它。

```c
HGresult hgGraphAddMemcpyNode (HGgraphNode* phGraphNode,
                               HGgraph hGraph,
                               const HGgraphNode* dependencies,
                               size_t numDependencies,
                               const HGGC_MEMCPY3D* copyParams,
                               HGcontext ctx)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| phGraphNode | out | 返回新创建的节点 |
| hGraph | in | 要添加节点的图 |
| dependencies | in | 节点的依赖项 |
| numDependencies | in | 依赖项数量 |
| copyParams | in | 复制参数 |
| ctx | in | 上下文 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 16. hgGraphAddMemsetNode {#hggraphaddmemsetnode}

创建新的内存设置节点并将其添加到 `hGraph`。`numDependencies` 可以为 0，此时节点将放置在图的根节点处。`dependencies` 不能包含任何重复条目。新节点的句柄将通过 `phGraphNode` 返回。

当节点被添加时，`memsetParams` 内部的数据会被复制，因此调用返回后可以释放它。

```c
HGresult hgGraphAddMemsetNode (HGgraphNode* phGraphNode,
                               HGgraph hGraph,
                               const HGgraphNode* dependencies,
                               size_t numDependencies,
                               const HGGC_MEMSET_NODE_PARAMS* memsetParams,
                               HGcontext ctx)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| phGraphNode | out | 返回新创建的节点 |
| hGraph | in | 要添加节点的图 |
| dependencies | in | 节点的依赖项 |
| numDependencies | in | 依赖项数量 |
| memsetParams | in | memset 参数 |
| ctx | in | 上下文 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 17. hgGraphAddNode {#hggraphaddnode}

创建新节点并将其添加到 `hGraph`。`numDependencies` 可以为 0，此时节点将放置在图的根节点处。`dependencies` 不能包含任何重复条目。新节点的句柄将通过 `phGraphNode` 返回。

`nodeParams` 中指定的类型决定了要创建和添加的节点类型。

```c
HGresult hgGraphAddNode (HGgraphNode* phGraphNode,
                         HGgraph hGraph,
                         const HGgraphNode* dependencies,
                         const HGgraphEdgeData* dependencyData,
                         size_t numDependencies,
                         HGgraphNodeParams* nodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| phGraphNode | out | 返回新创建的节点 |
| hGraph | in | 要添加节点的图 |
| dependencies | in | 节点的依赖项 |
| dependencyData | in | 边的可选数据 |
| numDependencies | in | 依赖项数量 |
| nodeParams | in | 节点的参数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 18. hgGraphBatchMemOpNodeGetParams {#hggraphbatchmemopnodegetparams}

返回批量内存操作节点 `hNode` 的参数到 `nodeParams_out`。

```c
HGresult hgGraphBatchMemOpNodeGetParams (HGgraphNode hNode,
                                         HGGC_BATCH_MEM_OP_NODE_PARAMS* nodeParams_out)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 要获取参数的节点 |
| nodeParams_out | out | 返回参数的指针 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 19. hgGraphBatchMemOpNodeSetParams {#hggraphbatchmemopnodesetparams}

将批量内存操作节点 `hNode` 的参数设置为 `nodeParams`。

```c
HGresult hgGraphBatchMemOpNodeSetParams (HGgraphNode hNode,
                                         const HGGC_BATCH_MEM_OP_NODE_PARAMS* nodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 要设置参数的节点 |
| nodeParams | in | 要设置的参数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 20. hgGraphChildGraphNodeGetGraph {#hggraphchildgraphnodegetgraph}

返回子图节点 `hNode` 嵌入的图。返回的图是指向原始图的引用，而不是克隆。

```c
HGresult hgGraphChildGraphNodeGetGraph (HGgraphNode hNode, HGgraph* phGraph)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 要查询的节点 |
| phGraph | out | 返回图句柄 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 21. hgGraphClone {#hggraphclone}

创建 `originalGraph` 的克隆。新图将包含原始图中所有节点的克隆，节点类型和依赖关系保持不变。克隆后对任一图的修改不会影响另一个。

```c
HGresult hgGraphClone (HGgraph* phGraphClone, HGgraph originalGraph)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| phGraphClone | out | 返回克隆的图 |
| originalGraph | in | 要克隆的原始图 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 22. hgGraphConditionalHandleCreate {#hggraphconditionalhandlecreate}

创建与图 `hGraph` 关联的条件句柄。条件句柄用于在图执行时动态选择执行路径。

`flags` 当前必须为 0。

```c
HGresult hgGraphConditionalHandleCreate (HGgraphConditionalHandle* pHandle_out,
                                         HGgraph hGraph,
                                         HGcontext ctx,
                                         unsigned int defaultLaunchValue,
                                         unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pHandle_out | out | 返回条件句柄 |
| hGraph | in | 与此句柄关联的图 |
| ctx | in | 上下文 |
| defaultLaunchValue | in | 默认启动值 |
| flags | in | 标志 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 23. hgGraphCreate {#hggraphcreate}

创建新的空图。初始图中没有任何节点。节点和边可以通过 hgGraphAdd* 函数添加。

`flags` 当前必须为 0。

```c
HGresult hgGraphCreate (HGgraph* phGraph, unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| phGraph | out | 返回新创建的图 |
| flags | in | 标志（当前必须为 0） |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 24. hgGraphDebugDotPrint {#hggraphdebugdotprint}

将 `hGraph` 的结构以 DOT 格式输出到 `path` 指定的文件。生成的 DOT 文件可用 GraphViz 等工具可视化。

`flags` 控制输出内容，可以是以下值的组合：
- `HGGC_GRAPH_DEBUG_DOT_FLAGS_VERBOSE`：输出所有节点和边的详细信息

```c
HGresult hgGraphDebugDotPrint (HGgraph hGraph,
                               const char* path,
                               unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraph | out | 要输出的图 |
| path | out | 输出文件路径 |
| flags | out | 控制输出内容的标志 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 25. hgGraphDestroy {#hggraphdestroy}

销毁图 `hGraph`。如果图有任何未释放的用户对象引用，则此操作会失败。

```c
HGresult hgGraphDestroy (HGgraph hGraph)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraph | in | 要销毁的图 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 26. hgGraphDestroyNode {#hggraphdestroynode}

从图中移除节点 `hNode`。移除节点会自动移除该节点的所有依赖关系边。如果节点有子图，则子图不会被销毁。

```c
HGresult hgGraphDestroyNode (HGgraphNode hNode)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 要移除的节点 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 27. hgGraphEventRecordNodeGetEvent {#hggrapheventrecordnodegetevent}

返回事件记录节点 `hNode` 关联的 HGGC 事件。

```c
HGresult hgGraphEventRecordNodeGetEvent (HGgraphNode hNode, HGevent* event_out)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 事件记录节点 |
| event_out | out | 返回事件 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 28. hgGraphEventRecordNodeSetEvent {#hggrapheventrecordnodesetevent}

设置事件记录节点 `hNode` 的事件为 `event`。

```c
HGresult hgGraphEventRecordNodeSetEvent (HGgraphNode hNode, HGevent event)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 事件记录节点 |
| event | in | 要设置的事件 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 29. hgGraphEventWaitNodeGetEvent {#hggrapheventwaitnodegetevent}

返回事件等待节点 `hNode` 关联的 HGGC 事件。

```c
HGresult hgGraphEventWaitNodeGetEvent (HGgraphNode hNode, HGevent* event_out)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 事件等待节点 |
| event_out | out | 返回事件 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 30. hgGraphEventWaitNodeSetEvent {#hggrapheventwaitnodesetevent}

设置事件等待节点 `hNode` 的事件为 `event`。

```c
HGresult hgGraphEventWaitNodeSetEvent (HGgraphNode hNode, HGevent event)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 事件等待节点 |
| event | in | 要设置的事件 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 31. hgGraphExecBatchMemOpNodeSetParams {#hggraphexecbatchmemopnodesetparams}

在可执行图 `hGraphExec` 中为批量内存操作节点 `hNode` 设置参数。修改只影响未来的 `hGraphExec` 启动。当前正在执行或已排入队列的 `hGraphExec` 启动不受此调用影响。

```c
HGresult hgGraphExecBatchMemOpNodeSetParams (HGgraphExec hGraphExec,
                                             HGgraphNode hNode,
                                             const HGGC_BATCH_MEM_OP_NODE_PARAMS* nodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraphExec | in | 目标可执行图 |
| hNode | in | 要设置参数的节点 |
| nodeParams | in | 新的节点参数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 32. hgGraphExecChildGraphNodeSetParams {#hggraphexecchildgraphnodesetparams}

将 `hGraphExec` 中子图节点 `hNode` 的子图替换为 `childGraph`。

```c
HGresult hgGraphExecChildGraphNodeSetParams (HGgraphExec hGraphExec,
                                             HGgraphNode hNode,
                                             HGgraph childGraph)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraphExec | in | 目标可执行图 |
| hNode | in | 子图节点 |
| childGraph | in | 新的子图 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 33. hgGraphExecDestroy {#hggraphexecdestroy}

销毁可执行图 `hGraphExec`。如果 `hGraphExec` 当前正在执行，则此操作会阻塞直到执行完成。

```c
HGresult hgGraphExecDestroy (HGgraphExec hGraphExec)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraphExec | in | 要销毁的可执行图 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 34. hgGraphExecEventRecordNodeSetEvent {#hggraphexeceventrecordnodesetevent}

在可执行图 `hGraphExec` 中设置事件记录节点 `hNode` 的事件为 `event`。

```c
HGresult hgGraphExecEventRecordNodeSetEvent (HGgraphExec hGraphExec,
                                             HGgraphNode hNode,
                                             HGevent event)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraphExec | in | 目标可执行图 |
| hNode | in | 事件记录节点 |
| event | in | 新事件 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 35. hgGraphExecEventWaitNodeSetEvent {#hggraphexeceventwaitnodesetevent}

在可执行图 `hGraphExec` 中设置事件等待节点 `hNode` 的事件为 `event`。

```c
HGresult hgGraphExecEventWaitNodeSetEvent (HGgraphExec hGraphExec,
                                           HGgraphNode hNode,
                                           HGevent event)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraphExec | in | 目标可执行图 |
| hNode | in | 事件等待节点 |
| event | in | 新事件 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 36. hgGraphExecGetFlags {#hggraphexecgetflags}

返回可执行图 `hGraphExec` 的实例化标志。

```c
HGresult hgGraphExecGetFlags (HGgraphExec hGraphExec, hguint64_t* flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraphExec | in | 可执行图 |
| flags | out | 返回标志 |

错误码：HGGC_ERROR_INVALID_VALUE

---

#### 37. hgGraphExecHostNodeSetParams {#hggraphexechostnodesetparams}

在可执行图 `hGraphExec` 中为主机节点 `hNode` 设置参数。修改只影响未来的 `hGraphExec` 启动。当前正在执行或已排入队列的 `hGraphExec` 启动不受此调用影响。

```c
HGresult hgGraphExecHostNodeSetParams (HGgraphExec hGraphExec,
                                       HGgraphNode hNode,
                                       const HGGC_HOST_NODE_PARAMS* nodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraphExec | in | 目标可执行图 |
| hNode | in | 主机节点 |
| nodeParams | in | 新的节点参数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 38. hgGraphExecKernelNodeSetParams {#hggraphexeckernelnodesetparams}

在可执行图 `hGraphExec` 中为核函数节点 `hNode` 设置参数。修改只影响未来的 `hGraphExec` 启动。当前正在执行或已排入队列的 `hGraphExec` 启动不受此调用影响。

```c
HGresult hgGraphExecKernelNodeSetParams (HGgraphExec hGraphExec,
                                         HGgraphNode hNode,
                                         const HGGC_KERNEL_NODE_PARAMS* nodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraphExec | in | 目标可执行图 |
| hNode | in | 核函数节点 |
| nodeParams | in | 新的节点参数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 39. hgGraphExecMemcpyNodeSetParams {#hggraphexecmemcpynodesetparams}

在可执行图 `hGraphExec` 中为内存复制节点 `hNode` 设置参数。修改只影响未来的 `hGraphExec` 启动。当前正在执行或已排入队列的 `hGraphExec` 启动不受此调用影响。

```c
HGresult hgGraphExecMemcpyNodeSetParams (HGgraphExec hGraphExec,
                                         HGgraphNode hNode,
                                         const HGGC_MEMCPY3D* copyParams,
                                         HGcontext ctx)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraphExec | in | 目标可执行图 |
| hNode | in | 内存复制节点 |
| copyParams | in | 新的复制参数 |
| ctx | in | 上下文 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 40. hgGraphExecMemsetNodeSetParams {#hggraphexecmemsetnodesetparams}

在可执行图 `hGraphExec` 中为内存设置节点 `hNode` 设置参数。修改只影响未来的 `hGraphExec` 启动。当前正在执行或已排入队列的 `hGraphExec` 启动不受此调用影响。

```c
HGresult hgGraphExecMemsetNodeSetParams (HGgraphExec hGraphExec,
                                         HGgraphNode hNode,
                                         const HGGC_MEMSET_NODE_PARAMS* memsetParams,
                                         HGcontext ctx)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraphExec | in | 目标可执行图 |
| hNode | in | 内存设置节点 |
| memsetParams | in | 新的 memset 参数 |
| ctx | in | 上下文 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 41. hgGraphExecNodeSetParams {#hggraphexecnodesetparams}

在可执行图 `hGraphExec` 中为节点 `hNode` 设置参数。节点类型由 `nodeParams->type` 指定，必须与 `hNode` 的类型匹配。修改只影响未来的 `hGraphExec` 启动。当前正在执行或已排入队列的 `hGraphExec` 启动不受此调用影响。

不支持修改 HG_GRAPH_NODE_TYPE_MEM_ALLOC 和 HG_GRAPH_NODE_TYPE_MEM_FREE 节点类型的参数。

```c
HGresult hgGraphExecNodeSetParams (HGgraphExec hGraphExec,
                                   HGgraphNode hNode,
                                   HGgraphNodeParams* nodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraphExec | in | 目标可执行图 |
| hNode | in | 要设置参数的节点 |
| nodeParams | in | 新的节点参数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 42. hgGraphExecUpdate {#hggraphexecupdate}

尝试使用 `hGraph` 中的变化更新 `hGraphExec`。如果更新成功，则 `hGraphExec` 已更新。如果更新失败，`hGraphExec` 保持不变。

`resultInfo` 会返回更新的详细结果，包括失败原因（如果失败）。

此函数可用于热更新图，而无需重新实例化。

```c
HGresult hgGraphExecUpdate (HGgraphExec hGraphExec,
                            HGgraph hGraph,
                            HGgraphExecUpdateResultInfo* resultInfo)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraphExec | in | 目标可执行图 |
| hGraph | in | 更新后的图 |
| resultInfo | out | 返回更新结果信息 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 43. hgGraphGetEdges {#hggraphgetedges}

返回图 `hGraph` 中的所有依赖边。如果 `from`、`to` 或 `edgeData` 为 NULL，则此函数只返回边数。

```c
HGresult hgGraphGetEdges (HGgraph hGraph,
                          HGgraphNode* from,
                          HGgraphNode* to,
                          HGgraphEdgeData* edgeData,
                          size_t* numEdges)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraph | in | 要查询的图 |
| from | out | 返回源节点数组 |
| to | out | 返回目标节点数组 |
| edgeData | out | 返回边数据数组 |
| numEdges | out | 输入时指定数组大小，输出时返回实际边数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 44. hgGraphGetNodes {#hggraphgetnodes}

返回图 `hGraph` 中的所有节点。如果 `nodes` 为 NULL，则此函数只返回节点数。

```c
HGresult hgGraphGetNodes (HGgraph hGraph, HGgraphNode* nodes, size_t* numNodes)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraph | in | 要查询的图 |
| nodes | out | 返回节点数组 |
| numNodes | out | 输入时指定数组大小，输出时返回实际节点数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 45. hgGraphGetRootNodes {#hggraphgetrootnodes}

返回图 `hGraph` 中的所有根节点（没有依赖项的节点）。如果 `rootNodes` 为 NULL，则此函数只返回根节点数。

```c
HGresult hgGraphGetRootNodes (HGgraph hGraph,
                              HGgraphNode* rootNodes,
                              size_t* numRootNodes)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraph | in | 要查询的图 |
| rootNodes | out | 返回根节点数组 |
| numRootNodes | out | 输入时指定数组大小，输出时返回实际根节点数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 46. hgGraphHostNodeGetParams {#hggraphhostnodegetparams}

返回主机节点 `hNode` 的参数到 `nodeParams`。

`nodeParams` 中返回的任何指针指向与节点关联的驱动拥有的内存。此内存在节点销毁前保持有效。不得修改 `nodeParams` 中的任何内存。

```c
HGresult hgGraphHostNodeGetParams (HGgraphNode hNode,
                                   HGGC_HOST_NODE_PARAMS* nodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 主机节点 |
| nodeParams | out | 返回参数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 47. hgGraphHostNodeSetParams {#hggraphhostnodesetparams}

设置主机节点 `hNode` 的参数为 `nodeParams`。

```c
HGresult hgGraphHostNodeSetParams (HGgraphNode hNode,
                                   const HGGC_HOST_NODE_PARAMS* nodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 主机节点 |
| nodeParams | in | 新的参数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 48. hgGraphInstantiate {#hggraphinstantiate}

将图 `hGraph` 实例化为可执行图 `phGraphExec`。实例化过程会验证图的结构并分配执行所需的所有资源。

`flags` 控制实例化行为，可以是以下值的组合：
- `HGGC_GRAPH_INSTANTIATE_FLAG_NODE_UPDATE_NO_INSTALL_DRIVER_UPDATES`：安装新的驱动更新时不更新已实例化的图

```c
HGresult hgGraphInstantiate (HGgraphExec* phGraphExec,
                             HGgraph hGraph,
                             unsigned long long flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| phGraphExec | out | 返回新创建的可执行图 |
| hGraph | in | 要实例化的图 |
| flags | in | 实例化标志 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 49. hgGraphInstantiateWithParams {#hggraphinstantiatewithparams}

将图 `hGraph` 实例化为可执行图 `phGraphExec`。此函数允许通过 `instantiateParams` 指定更多实例化选项。

```c
HGresult hgGraphInstantiateWithParams (HGgraphExec* phGraphExec,
                                       HGgraph hGraph,
                                       HGGC_GRAPH_INSTANTIATE_PARAMS* instantiateParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| phGraphExec | out | 返回新创建的可执行图 |
| hGraph | in | 要实例化的图 |
| instantiateParams | in | 实例化参数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 50. hgGraphKernelNodeCopyAttributes {#hggraphkernelnodecopyattributes}

将节点 `src` 的属性复制到节点 `dst`。两个节点必须是相同类型的核函数节点。

```c
HGresult hgGraphKernelNodeCopyAttributes (HGgraphNode dst, HGgraphNode src)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dst | in | 目标节点 |
| src | in | 源节点 |

错误码：HGGC_ERROR_INVALID_VALUE

---

#### 51. hgGraphKernelNodeGetAttribute {#hggraphkernelnodegetattribute}

返回核函数节点 `hNode` 的属性 `attr`。

支持的属性包括：
- `HG_KERNEL_NODE_ATTR_ACCESS_POLICY_WINDOW`
- `HG_KERNEL_NODE_ATTR_COOPERATIVE`
- `HG_KERNEL_NODE_ATTR_PRIORITY`

```c
HGresult hgGraphKernelNodeGetAttribute (HGgraphNode hNode,
                                        HGkernelNodeAttrID attr,
                                        HGkernelNodeAttrValue* value_out)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 核函数节点 |
| attr | in | 属性 ID |
| value_out | out | 返回属性值 |

错误码：HGGC_ERROR_INVALID_VALUE

---

#### 52. hgGraphKernelNodeGetParams {#hggraphkernelnodegetparams}

返回核函数节点 `hNode` 的参数到 `nodeParams`。

```c
HGresult hgGraphKernelNodeGetParams (HGgraphNode hNode,
                                     HGGC_KERNEL_NODE_PARAMS* nodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 核函数节点 |
| nodeParams | out | 返回参数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 53. hgGraphKernelNodeSetAttribute {#hggraphkernelnodesetattribute}

设置核函数节点 `hNode` 的属性 `attr`。

```c
HGresult hgGraphKernelNodeSetAttribute (HGgraphNode hNode,
                                        HGkernelNodeAttrID attr,
                                        const HGkernelNodeAttrValue* value)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 核函数节点 |
| attr | in | 属性 ID |
| value | in | 属性值 |

错误码：HGGC_ERROR_INVALID_VALUE

---

#### 54. hgGraphKernelNodeSetParams {#hggraphkernelnodesetparams}

设置核函数节点 `hNode` 的参数为 `nodeParams`。

```c
HGresult hgGraphKernelNodeSetParams (HGgraphNode hNode,
                                     const HGGC_KERNEL_NODE_PARAMS* nodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 核函数节点 |
| nodeParams | in | 新的参数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 55. hgGraphLaunch {#hggraphlaunch}

在流 `hStream` 中启动可执行图 `hGraphExec`。图执行是异步的，因此一旦图被排入队列，此函数就会返回。

```c
HGresult hgGraphLaunch (HGgraphExec hGraphExec, HGstream hStream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraphExec | in | 要启动的可执行图 |
| hStream | in | 启动所在的流 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 56. hgGraphMemAllocNodeGetParams {#hggraphmemallocnodegetparams}

返回内存分配节点 `hNode` 的参数到 `params_out`。

```c
HGresult hgGraphMemAllocNodeGetParams (HGgraphNode hNode,
                                       HGGC_MEM_ALLOC_NODE_PARAMS* params_out)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 内存分配节点 |
| params_out | out | 返回参数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 57. hgGraphMemFreeNodeGetParams {#hggraphmemfreenodegetparams}

返回内存释放节点 `hNode` 要释放的设备指针。

```c
HGresult hgGraphMemFreeNodeGetParams (HGgraphNode hNode, HGdeviceptr* dptr_out)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 内存释放节点 |
| dptr_out | out | 返回设备指针 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 58. hgGraphMemcpyNodeGetParams {#hggraphmemcpynodegetparams}

返回内存复制节点 `hNode` 的参数到 `nodeParams`。

```c
HGresult hgGraphMemcpyNodeGetParams (HGgraphNode hNode,
                                     HGGC_MEMCPY3D* nodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 内存复制节点 |
| nodeParams | out | 返回参数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 59. hgGraphMemcpyNodeSetParams {#hggraphmemcpynodesetparams}

设置内存复制节点 `hNode` 的参数为 `nodeParams`。

```c
HGresult hgGraphMemcpyNodeSetParams (HGgraphNode hNode,
                                     const HGGC_MEMCPY3D* nodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 内存复制节点 |
| nodeParams | in | 新的参数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 60. hgGraphMemsetNodeGetParams {#hggraphmemsetnodegetparams}

返回内存设置节点 `hNode` 的参数到 `nodeParams`。

```c
HGresult hgGraphMemsetNodeGetParams (HGgraphNode hNode,
                                     HGGC_MEMSET_NODE_PARAMS* nodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 内存设置节点 |
| nodeParams | out | 返回参数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 61. hgGraphMemsetNodeSetParams {#hggraphmemsetnodesetparams}

设置内存设置节点 `hNode` 的参数为 `nodeParams`。

```c
HGresult hgGraphMemsetNodeSetParams (HGgraphNode hNode,
                                     const HGGC_MEMSET_NODE_PARAMS* nodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 内存设置节点 |
| nodeParams | in | 新的参数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 62. hgGraphNodeFindInClone {#hggraphnodefindinclone}

在克隆图 `hClonedGraph` 中查找 `hOriginalNode` 对应的克隆节点。

```c
HGresult hgGraphNodeFindInClone (HGgraphNode* phNode,
                                 HGgraphNode hOriginalNode,
                                 HGgraph hClonedGraph)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| phNode | out | 返回克隆的节点 |
| hOriginalNode | in | 原始节点 |
| hClonedGraph | in | 克隆的图 |

错误码：HGGC_ERROR_INVALID_VALUE

---

#### 63. hgGraphNodeGetDependencies {#hggraphnodegetdependencies}

返回图节点 `hNode` 的所有依赖节点。如果 `dependencies` 或 `edgeData` 为 NULL，则此函数只返回依赖项数。

```c
HGresult hgGraphNodeGetDependencies (HGgraphNode hNode,
                                     HGgraphNode* dependencies,
                                     HGgraphEdgeData* edgeData,
                                     size_t* numDependencies)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 要查询的节点 |
| dependencies | out | 返回依赖节点数组 |
| edgeData | out | 返回边数据数组 |
| numDependencies | out | 输入时指定数组大小，输出时返回实际依赖项数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 64. hgGraphNodeGetDependentNodes {#hggraphnodegetdependentnodes}

返回图节点 `hNode` 的所有依赖节点（以 `hNode` 为起点的边的终点）。如果 `dependentNodes` 或 `edgeData` 为 NULL，则此函数只返回依赖节点数。

```c
HGresult hgGraphNodeGetDependentNodes (HGgraphNode hNode,
                                       HGgraphNode* dependentNodes,
                                       HGgraphEdgeData* edgeData,
                                       size_t* numDependentNodes)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 要查询的节点 |
| dependentNodes | out | 返回依赖节点数组 |
| edgeData | out | 返回边数据数组 |
| numDependentNodes | out | 输入时指定数组大小，输出时返回实际依赖节点数 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 65. hgGraphNodeGetType {#hggraphnodegettype}

将 `hNode` 的节点类型返回到 `type`。

```c
HGresult hgGraphNodeGetType (HGgraphNode hNode, HGgraphNodeType* type)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 要查询的节点 |
| type | out | 返回节点类型 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 66. hgGraphNodeSetParams {#hggraphnodesetparams}

将图节点 `hNode` 的参数设置为 `nodeParams`。`nodeParams->type` 指定的节点类型必须与 `hNode` 的类型匹配。`nodeParams` 必须完全初始化，所有未使用的字节（保留字段、填充）必须置零。

不支持修改 HG_GRAPH_NODE_TYPE_MEM_ALLOC 和 HG_GRAPH_NODE_TYPE_MEM_FREE 节点类型的参数。

```c
HGresult hgGraphNodeSetParams (HGgraphNode hNode, HGgraphNodeParams* nodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 要设置参数的节点 |
| nodeParams | in | 要复制的参数 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_SUPPORTED

---

#### 67. hgGraphReleaseUserObject {#hggraphreleaseuserobject}

释放图拥有的用户对象引用。

有关用户对象的更多信息，请参阅 HGGC C++ 编程指南中的 HGGC 用户对象。

```c
HGresult hgGraphReleaseUserObject (HGgraph graph,
                                   HGuserObject object,
                                   unsigned int count)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| graph | in | 将释放引用的图 |
| object | in | 要释放引用的用户对象 |
| count | in | 要释放的引用数，通常为 1。必须非零且不大于 INT_MAX。 |

错误码：HGGC_ERROR_INVALID_VALUE

---

#### 68. hgGraphRemoveDependencies {#hggraphremovedependencies}

要移除的依赖项数量由 `numDependencies` 定义。`from` 和 `to` 中对应索引处的元素定义一个依赖项。`from` 和 `to` 中的每个节点必须属于 `hGraph`。

如果 `numDependencies` 为 0，则 `from` 和 `to` 中的元素将忽略。指定图中不存在且数据与 `edgeData` 匹配的边会导致错误。`edgeData` 可为空，相当于为每条边传递默认（零值）数据。

不能从包含分配或释放节点的图中移除依赖项。任何此类尝试都将返回错误。

```c
HGresult hgGraphRemoveDependencies (HGgraph hGraph,
                                    const HGgraphNode* from,
                                    const HGgraphNode* to,
                                    const HGgraphEdgeData* edgeData,
                                    size_t numDependencies)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraph | in | 要移除依赖项的图 |
| from | in | 提供依赖项的节点数组 |
| to | in | 依赖节点数组 |
| edgeData | in | 边的可选数据数组。如果为 NULL，则假定边数据为默认（零值）。 |
| numDependencies | in | 要移除的依赖项数量 |

错误码：HGGC_ERROR_INVALID_VALUE

---

#### 69. hgGraphRetainUserObject {#hggraphretainuserobject}

创建或移动将由 HGGC 图拥有的用户对象引用。

有关用户对象的更多信息，请参阅 HGGC C++ 编程指南中的 HGGC 用户对象。

```c
HGresult hgGraphRetainUserObject (HGgraph graph,
                                  HGuserObject object,
                                  unsigned int count,
                                  unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| graph | in | 与引用关联的图 |
| object | in | 要保留引用的用户对象 |
| count | in | 要添加到图的引用数，通常为 1。必须非零且不大于 INT_MAX。 |
| flags | in | 可选标志 [HG_GRAPH_USER_OBJECT_MOVE](#driver-data-types) 从调用线程转移引用，而不是创建新引用。传递 0 以创建新引用。 |

错误码：HGGC_ERROR_INVALID_VALUE

---

#### 70. hgGraphUpload {#hggraphupload}

将 `hGraphExec` 上传到 `hStream` 中的设备，但不执行它。同一 `hGraphExec` 的上传将被序列化。每次上传都按照 `hStream` 中先前工作的顺序和 `hGraphExec` 先前启动的顺序进行。使用 `stream` 缓存的内存来支持 `hGraphExec` 拥有的分配。

```c
HGresult hgGraphUpload (HGgraphExec hGraphExec, HGstream hStream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraphExec | in | 要上传的可执行图 |
| hStream | in | 上传图所在的流 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_VALUE

---

#### 71. hgUserObjectCreate {#hguserobjectcreate}

使用指定的销毁回调和初始引用计数创建用户对象。初始引用由调用者拥有。

销毁回调不能调用 HGGC API，应避免阻塞行为，因为它们由共享的内部线程执行。如果不阻塞通过 HGGC 调度的任务的前进，则可以向另一个线程发出信号以执行此类操作。

有关用户对象的更多信息，请参阅 HGGC C++ 编程指南中的 HGGC 用户对象。

```c
HGresult hgUserObjectCreate (HGuserObject* object_out,
                             void* ptr,
                             HGhostFn destroy,
                             unsigned int initialRefcount,
                             unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| object_out | out | 返回用户对象句柄的位置 |
| ptr | in | 要传递给销毁函数的指针 |
| destroy | in | 当用户对象不再使用时调用的回调以释放它 |
| initialRefcount | in | 创建对象时的初始引用计数，通常为 1。初始引用由调用线程拥有。 |
| flags | in | 当前必须传递 [HG_USER_OBJECT_NO_DESTRUCTOR_SYNC](#driver-data-types)，这是唯一定义的标志。这表示销毁回调不能被任何 HGGC API 等待。需要同步回调的用户应手动发出信号。 |

错误码：HGGC_ERROR_INVALID_VALUE

---

#### 72. hgUserObjectRelease {#hguserobjectrelease}

释放调用者拥有的用户对象引用。当引用计数达到零时，会调用对象的析构函数。

释放调用者不拥有的引用，或在所有引用被释放后使用用户对象句柄是未定义行为。

有关用户对象的更多信息，请参阅 HGGC C++ 编程指南中的 HGGC 用户对象。

```c
HGresult hgUserObjectRelease (HGuserObject object, unsigned int count)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| object | in | 要释放的对象 |
| count | in | 要释放的引用数，通常为 1。必须非零且不大于 INT_MAX。 |

错误码：HGGC_ERROR_INVALID_VALUE

---

#### 73. hgUserObjectRetain {#hguserobjectretain}

保留用户对象的新引用。新引用由调用者拥有。

有关用户对象的更多信息，请参阅 HGGC C++ 编程指南中的 HGGC 用户对象。

```c
HGresult hgUserObjectRetain (HGuserObject object, unsigned int count)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| object | in | 要保留的对象 |
| count | in | 要保留的引用数，通常为 1。必须非零且不大于 INT_MAX。 |

错误码：HGGC_ERROR_INVALID_VALUE

---

比赛关联：占用率查询 API（`hgOccupancyMaxActiveBlocksPerMultiprocessor` 等）用于自定算子的 block 配置调优；HGGC Graph（`hgStreamBeginCapture` 捕获 → `hgGraphInstantiate` → `hgGraphLaunch`）可把 decode 阶段每步数十次 kernel launch 合并为一次提交，配合 `hgGraphExecUpdate`/`hgGraphExecKernelNodeSetParams` 热更新参数，是降低 launch 开销、提升吞吐与压缩 TTFT 的重点方向。

---

## 8. 图像资源 {#image}

本节涵盖纹理对象与表面的创建、属性查询。

---

### 8.1. 图像资源管理 {#texture}

本模块提供**纹理对象管理**接口，用于创建/销毁纹理对象与表面对象。纹理对象是只读内存的硬件加速访问器。

本节介绍底层 HGGC 驱动程序应用程序编程接口的纹理对象管理功能。纹理对象 API 仅在计算能力 3.0 或更高版本的设备上受支持。

#### 1. 接口一览 {#接口一览}

| 函数 | 用途 |
|------|------|
| [hgTexObjectCreate](#hgtexobjectcreate) | 创建纹理对象 |
| [hgTexObjectDestroy](#hgtexobjectdestroy) | 销毁纹理对象 |

---

#### 2. hgTexObjectCreate {#hgtexobjectcreate}

使用 pResDesc 描述的资源、pTexDesc 描述的纹理采样属性，以及 pResViewDesc 描述的资源视图（如适用）创建纹理对象，并在 pTexObject 中返回该对象的句柄。pResViewDesc 为可选参数，用于为 pResDesc 所描述的数据指定替代格式，并描述纹理化时可访问的子资源区域；仅当资源类型为 HGGC 数组或 HGGC mipmap 数组时才能指定 pResViewDesc，其他情况下必须为 NULL。

```c
HGresult hgTexObjectCreate (HGtexObject* pTexObject,
                            const HGGC_RESOURCE_DESC* pResDesc,
                            const HGGC_TEXTURE_DESC* pTexDesc,
                            const HGGC_RESOURCE_VIEW_DESC* pResViewDesc)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pTexObject | out | 返回创建的纹理对象 |
| pResDesc | in | 资源的描述符 |
| pTexDesc | in | 纹理对象的描述符 |
| pResViewDesc | in | 资源视图描述符（可选），否则为 NULL |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_OUT_OF_MEMORY

---

#### 3. hgTexObjectDestroy {#hgtexobjectdestroy}

销毁纹理对象 texObject。

```c
HGresult hgTexObjectDestroy (HGtexObject texObject)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| texObject | in | 要销毁的纹理对象 |

错误码：HGGC_ERROR_DEINITIALIZED、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_INVALID_CONTEXT、HGGC_ERROR_INVALID_VALUE

---

## 9. 参考 {#reference}

本节提供 HGGC Driver API 的辅助参考索引。

---

### 9.1. 数据结构 {#data-structures-index}

本页按字母序汇总 HGGC Driver API 暴露的全部数据结构。

- HG_DEV_SM_RESOURCE_GROUP_PARAMS
- HGaccessPolicyWindow_v1
- HGarrayMapInfo_v1
- HGctxCigParam
- HGctxCreateParams
- HGGC_ARRAY3D_DESCRIPTOR_v2
- HGGC_ARRAY_DESCRIPTOR_v2
- HGGC_ARRAY_MEMORY_REQUIREMENTS_v1
- HGGC_ARRAY_SPARSE_PROPERTIES_v1
- HGGC_BATCH_MEM_OP_NODE_PARAMS_v1
- HGGC_BATCH_MEM_OP_NODE_PARAMS_v2
- HGGC_CHILD_GRAPH_NODE_PARAMS
- HGGC_CONDITIONAL_NODE_PARAMS
- HGGC_EVENT_RECORD_NODE_PARAMS
- HGGC_EVENT_WAIT_NODE_PARAMS
- HGGC_GRAPH_INSTANTIATE_PARAMS
- HGGC_HOST_NODE_PARAMS_v1
- HGGC_HOST_NODE_PARAMS_v2
- HGGC_KERNEL_NODE_PARAMS_v1
- HGGC_KERNEL_NODE_PARAMS_v2
- HGGC_KERNEL_NODE_PARAMS_v3
- HGGC_LAUNCH_PARAMS_v1
- HGGC_MEM_ALLOC_NODE_PARAMS_v1
- HGGC_MEM_ALLOC_NODE_PARAMS_v2
- HGGC_MEM_FREE_NODE_PARAMS
- HGGC_MEMCPY2D_v2
- HGGC_MEMCPY3D_PEER_v1
- HGGC_MEMCPY3D_v2
- HGGC_MEMCPY_NODE_PARAMS
- HGGC_MEMSET_NODE_PARAMS_v1
- HGGC_MEMSET_NODE_PARAMS_v2
- HGGC_POINTER_ATTRIBUTE_P2P_TOKENS_v1
- HGGC_RESOURCE_DESC_v1
- HGGC_RESOURCE_VIEW_DESC_v1
- HGGC_TEXTURE_DESC_v1
- HGdevprop_v1
- HGextent3D_v1
- HGgraphEdgeData
- HGgraphExecUpdateResultInfo_v1
- HGgraphNodeParams
- HGipcEventHandle_v1
- HGipcMemHandle_v1
- HGlaunchAttribute
- HGlaunchAttributeValue
- HGlaunchConfig
- HGlaunchMemSyncDomainMap
- HGmemAccessDesc_v1
- HGmemAllocationProp_v1
- HGmemcpy3DOperand_v1
- HGmemcpyAttributes_v1
- HGmemDecompressParams
- HGmemFabricHandle_v1
- HGmemLocation_v1
- HGmemPoolProps_v1
- HGmemPoolPtrExportData_v1
- HGoffset3D_v1
- HGstreamBatchMemOpParams_v1
- HGtensorMap

---

### 9.2. 数据字段 {#data-fields-index}

以下是所有已文档化的 struct 和 union 字段列表，每个字段都附有指向其 struct/union 文档的链接：

#### A {#A}

accessDescCount
: HGGC_MEM_ALLOC_NODE_PARAMS_v1
: HGGC_MEM_ALLOC_NODE_PARAMS_v2

accessDescs
: HGGC_MEM_ALLOC_NODE_PARAMS_v2
: HGGC_MEM_ALLOC_NODE_PARAMS_v1

accessPolicyWindow
: HGlaunchAttributeValue

addressMode
: HGGC_TEXTURE_DESC_v1

algo
: HGmemDecompressParams

alignment
: HGGC_ARRAY_MEMORY_REQUIREMENTS_v1

alloc
: HGgraphNodeParams

allocType
: HGmemPoolProps_v1

array
: HGmemcpy3DOperand_v1

arrayDesc
: HGGC_EXTERNAL_MEMORY_MIPMAPPED_ARRAY_DESC_v1

attrs
: HGlaunchConfig

#### B {#B}

base_ptr
: HGaccessPolicyWindow_v1

blockDimX
: HGGC_KERNEL_NODE_PARAMS_v1
: HGGC_KERNEL_NODE_PARAMS_v3
: HGlaunchConfig
: HGGC_KERNEL_NODE_PARAMS_v2
: HGGC_LAUNCH_PARAMS_v1

blockDimY
: HGGC_KERNEL_NODE_PARAMS_v2
: HGGC_KERNEL_NODE_PARAMS_v3
: HGlaunchConfig
: HGGC_LAUNCH_PARAMS_v1
: HGGC_KERNEL_NODE_PARAMS_v1

blockDimZ
: HGlaunchConfig
: HGGC_LAUNCH_PARAMS_v1
: HGGC_KERNEL_NODE_PARAMS_v2
: HGGC_KERNEL_NODE_PARAMS_v3
: HGGC_KERNEL_NODE_PARAMS_v1

borderColor
: HGGC_TEXTURE_DESC_v1

bytesize
: HGGC_MEM_ALLOC_NODE_PARAMS_v2
: HGGC_MEM_ALLOC_NODE_PARAMS_v1

bytesOverBudget
: HGasyncNotificationInfo

#### C {#C}

cigParams
: HGctxCreateParams

clockRate
: HGdevprop_v1

clusterDim
: HGlaunchAttributeValue

clusterSchedulingPolicyPreference
: HGlaunchAttributeValue

compressionType
: HGmemAllocationProp_v1

conditional
: HGgraphNodeParams

cooperative
: HGlaunchAttributeValue

copyCtx
: HGGC_MEMCPY_NODE_PARAMS

copyParams
: HGGC_MEMCPY_NODE_PARAMS

coscheduledSmCount
: HG_DEV_SM_RESOURCE_GROUP_PARAMS

count
: HGGC_BATCH_MEM_OP_NODE_PARAMS_v2

ctx
: HGGC_KERNEL_NODE_PARAMS_v2
: HGGC_CONDITIONAL_NODE_PARAMS
: HGGC_MEMSET_NODE_PARAMS_v2
: HGGC_KERNEL_NODE_PARAMS_v3
: HGGC_BATCH_MEM_OP_NODE_PARAMS_v2

hgFormat
: HGeglFrame_v1

#### D {#D}

default_
: HGlaunchMemSyncDomainMap

depth
: HGGC_ARRAY_SPARSE_PROPERTIES_v1
: HGeglFrame_v1

Depth
: HGGC_MEMCPY3D_v2

depth
: HGGC_RESOURCE_VIEW_DESC_v1

Depth
: HGGC_MEMCPY3D_PEER_v1
: HGGC_ARRAY3D_DESCRIPTOR_v2

device
: HGdevWorkqueueConfigResource

deviceBitMask
: HGarrayMapInfo_v1

deviceUpdatableKernelNode
: HGlaunchAttributeValue

devPtr
: HGGC_RESOURCE_DESC_v1

dptr
: HGGC_MEM_ALLOC_NODE_PARAMS_v1
: HGGC_MEM_ALLOC_NODE_PARAMS_v2
: HGGC_MEM_FREE_NODE_PARAMS

dst
: HGGC_MEMSET_NODE_PARAMS_v2
: HGmemDecompressParams
: HGGC_MEMSET_NODE_PARAMS_v1

dstActBytes
: HGmemDecompressParams

dstArray
: HGGC_MEMCPY2D_v2
: HGGC_MEMCPY3D_v2
: HGGC_MEMCPY3D_PEER_v1

dstContext
: HGGC_MEMCPY3D_PEER_v1

dstDevice
: HGGC_MEMCPY2D_v2
: HGGC_MEMCPY3D_v2
: HGGC_MEMCPY3D_PEER_v1

dstHeight
: HGGC_MEMCPY3D_PEER_v1
: HGGC_MEMCPY3D_v2

dstHost
: HGGC_MEMCPY2D_v2
: HGGC_MEMCPY3D_v2
: HGGC_MEMCPY3D_PEER_v1

dstLocHint
: HGmemcpyAttributes_v1

dstLOD
: HGGC_MEMCPY3D_v2
: HGGC_MEMCPY3D_PEER_v1

dstMemoryType
: HGGC_MEMCPY3D_v2
: HGGC_MEMCPY2D_v2
: HGGC_MEMCPY3D_PEER_v1

dstNumBytes
: HGmemDecompressParams

dstPitch
: HGGC_MEMCPY3D_PEER_v1
: HGGC_MEMCPY2D_v2
: HGGC_MEMCPY3D_v2

dstXInBytes
: HGGC_MEMCPY3D_v2
: HGGC_MEMCPY3D_PEER_v1
: HGGC_MEMCPY2D_v2

dstY
: HGGC_MEMCPY3D_v2
: HGGC_MEMCPY2D_v2
: HGGC_MEMCPY3D_PEER_v1

dstZ
: HGGC_MEMCPY3D_v2
: HGGC_MEMCPY3D_PEER_v1

#### E {#E}

eglColorFormat
: HGeglFrame_v1

elementSize
: HGGC_MEMSET_NODE_PARAMS_v1
: HGGC_MEMSET_NODE_PARAMS_v2

errorFromNode
: HGgraphExecUpdateResultInfo_v1

errorNode
: HGgraphExecUpdateResultInfo_v1

event
: HGGC_EVENT_RECORD_NODE_PARAMS
: HGGC_EVENT_WAIT_NODE_PARAMS

eventRecord
: HGgraphNodeParams

eventWait
: HGgraphNodeParams

execAffinityParams
: HGctxCreateParams

extentDepth
: HGarrayMapInfo_v1

extentHeight
: HGarrayMapInfo_v1

extentWidth
: HGarrayMapInfo_v1

extra
: HGGC_KERNEL_NODE_PARAMS_v3
: HGGC_KERNEL_NODE_PARAMS_v2
: HGGC_KERNEL_NODE_PARAMS_v1

extSemArray
: HGGC_EXT_SEM_WAIT_NODE_PARAMS_v1
: HGGC_EXT_SEM_SIGNAL_NODE_PARAMS_v1
: HGGC_EXT_SEM_WAIT_NODE_PARAMS_v2
: HGGC_EXT_SEM_SIGNAL_NODE_PARAMS_v2

extSemSignal
: HGgraphNodeParams

extSemWait
: HGgraphNodeParams

#### F {#F}

fd
: HGGC_EXTERNAL_MEMORY_HANDLE_DESC_v1
: HGGC_EXTERNAL_SEMAPHORE_HANDLE_DESC_v1

fence
: HGGC_EXTERNAL_SEMAPHORE_SIGNAL_PARAMS_v1
: HGGC_EXTERNAL_SEMAPHORE_WAIT_PARAMS_v1
: HGGC_EXTERNAL_SEMAPHORE_SIGNAL_PARAMS_v1

filterMode
: HGGC_TEXTURE_DESC_v1

firstLayer
: HGGC_RESOURCE_VIEW_DESC_v1

firstMipmapLevel
: HGGC_RESOURCE_VIEW_DESC_v1

flags
: HGGC_EXTERNAL_MEMORY_BUFFER_DESC_v1
: HGGC_EXTERNAL_SEMAPHORE_HANDLE_DESC_v1
: HGGC_BATCH_MEM_OP_NODE_PARAMS_v2
: HGGC_EXTERNAL_SEMAPHORE_SIGNAL_PARAMS_v1
: HGGC_EXTERNAL_SEMAPHORE_WAIT_PARAMS_v1
: HGGC_GRAPH_INSTANTIATE_PARAMS
: HGarrayMapInfo_v1

Flags
: HGGC_ARRAY3D_DESCRIPTOR_v2

flags
: HGmulticastObjectProp_v1
: HGGC_MEMCPY_NODE_PARAMS
: HGmemAccessDesc_v1
: HGmemcpyAttributes_v1
: HGGC_ARRAY_SPARSE_PROPERTIES_v1
: HGdevSmResource
: HG_DEV_SM_RESOURCE_GROUP_PARAMS
: HGGC_RESOURCE_DESC_v1
: HGGC_TEXTURE_DESC_v1
: HGGC_EXTERNAL_MEMORY_HANDLE_DESC_v1

flushRemoteWrites
: HGstreamBatchMemOpParams_v1

fn
: HGGC_HOST_NODE_PARAMS_v2
: HGGC_HOST_NODE_PARAMS_v1

format
: HGGC_RESOURCE_DESC_v1

Format
: HGGC_ARRAY_DESCRIPTOR_v2

format
: HGGC_RESOURCE_VIEW_DESC_v1

Format
: HGGC_ARRAY3D_DESCRIPTOR_v2

frameType
: HGeglFrame_v1

free
: HGgraphNodeParams

from_port
: HGgraphEdgeData

func
: HGGC_KERNEL_NODE_PARAMS_v2
: HGGC_KERNEL_NODE_PARAMS_v3
: HGGC_KERNEL_NODE_PARAMS_v1

function
: HGGC_LAUNCH_PARAMS_v1

#### G {#G}

graph
: HGgraphNodeParams
: HGGC_CHILD_GRAPH_NODE_PARAMS

gridDimX
: HGlaunchConfig
: HGGC_LAUNCH_PARAMS_v1
: HGGC_KERNEL_NODE_PARAMS_v1
: HGGC_KERNEL_NODE_PARAMS_v2
: HGGC_KERNEL_NODE_PARAMS_v3

gridDimY
: HGGC_KERNEL_NODE_PARAMS_v2
: HGGC_LAUNCH_PARAMS_v1
: HGGC_KERNEL_NODE_PARAMS_v1
: HGGC_KERNEL_NODE_PARAMS_v3
: HGlaunchConfig

gridDimZ
: HGGC_KERNEL_NODE_PARAMS_v3
: HGGC_KERNEL_NODE_PARAMS_v1
: HGGC_KERNEL_NODE_PARAMS_v2
: HGGC_LAUNCH_PARAMS_v1
: HGlaunchConfig

#### H {#H}

handle
: HGGC_CONDITIONAL_NODE_PARAMS
: HGGC_EXTERNAL_MEMORY_HANDLE_DESC_v1
: HGGC_EXTERNAL_SEMAPHORE_HANDLE_DESC_v1

handleTypes
: HGmulticastObjectProp_v1
: HGmemPoolProps_v1

hArray
: HGGC_RESOURCE_DESC_v1

Height
: HGGC_MEMCPY3D_v2

height
: HGGC_RESOURCE_VIEW_DESC_v1
: HGeglFrame_v1

Height
: HGGC_MEMCPY3D_PEER_v1
: HGGC_ARRAY_DESCRIPTOR_v2

height
: HGGC_RESOURCE_DESC_v1
: HGGC_ARRAY_SPARSE_PROPERTIES_v1

Height
: HGGC_ARRAY3D_DESCRIPTOR_v2

height
: HGGC_MEMSET_NODE_PARAMS_v1
: HGGC_MEMSET_NODE_PARAMS_v2

Height
: HGGC_MEMCPY2D_v2

hErrNode_out
: HGGC_GRAPH_INSTANTIATE_PARAMS

hitProp
: HGaccessPolicyWindow_v1

hitRatio
: HGaccessPolicyWindow_v1

hMipmappedArray
: HGGC_RESOURCE_DESC_v1

host
: HGgraphNodeParams

hStream
: HGlaunchConfig
: HGGC_LAUNCH_PARAMS_v1

hUploadStream
: HGGC_GRAPH_INSTANTIATE_PARAMS

#### I {#I}

id
: HGlaunchAttribute

info
: HGasyncNotificationInfo

#### K {#K}

kern
: HGGC_KERNEL_NODE_PARAMS_v2
: HGGC_KERNEL_NODE_PARAMS_v3

kernel
: HGgraphNodeParams

kernelParams
: HGGC_KERNEL_NODE_PARAMS_v1
: HGGC_KERNEL_NODE_PARAMS_v2
: HGGC_LAUNCH_PARAMS_v1
: HGGC_KERNEL_NODE_PARAMS_v3

key
: HGGC_EXTERNAL_SEMAPHORE_WAIT_PARAMS_v1
: HGGC_EXTERNAL_SEMAPHORE_SIGNAL_PARAMS_v1

keyedMutex
: HGGC_EXTERNAL_SEMAPHORE_SIGNAL_PARAMS_v1
: HGGC_EXTERNAL_SEMAPHORE_WAIT_PARAMS_v1

#### L {#L}

lastLayer
: HGGC_RESOURCE_VIEW_DESC_v1

lastMipmapLevel
: HGGC_RESOURCE_VIEW_DESC_v1

launchCompletionEvent
: HGlaunchAttributeValue

layer
: HGarrayMapInfo_v1

layerHeight
: HGmemcpy3DOperand_v1

level
: HGarrayMapInfo_v1

location
: HGmemAllocationProp_v1
: HGmemAccessDesc_v1
: HGmemPoolProps_v1

locHint
: HGmemcpy3DOperand_v1

#### M {#M}

maxAnisotropy
: HGGC_TEXTURE_DESC_v1

maxGridSize
: HGdevprop_v1

maxMipmapLevelClamp
: HGGC_TEXTURE_DESC_v1

maxSize
: HGmemPoolProps_v1

maxThreadsDim
: HGdevprop_v1

maxThreadsPerBlock
: HGdevprop_v1

memcpy
: HGgraphNodeParams

memHandleType
: HGarrayMapInfo_v1

memOp
: HGgraphNodeParams

memOperationType
: HGarrayMapInfo_v1

memoryBarrier
: HGstreamBatchMemOpParams_v1

memPitch
: HGdevprop_v1

memset
: HGgraphNodeParams

memSyncDomain
: HGlaunchAttributeValue

memSyncDomainMap
: HGlaunchAttributeValue

minMipmapLevelClamp
: HGGC_TEXTURE_DESC_v1

minSmPartitionSize
: HGdevSmResource

mipmapFilterMode
: HGGC_TEXTURE_DESC_v1

mipmapLevelBias
: HGGC_TEXTURE_DESC_v1

miptailFirstLevel
: HGGC_ARRAY_SPARSE_PROPERTIES_v1

miptailSize
: HGGC_ARRAY_SPARSE_PROPERTIES_v1

missProp
: HGaccessPolicyWindow_v1

#### N {#N}

name
: HGGC_EXTERNAL_MEMORY_HANDLE_DESC_v1
: HGGC_EXTERNAL_SEMAPHORE_HANDLE_DESC_v1

num_bytes
: HGaccessPolicyWindow_v1

numAttrs
: HGlaunchConfig

numChannels
: HGGC_RESOURCE_DESC_v1
: HGeglFrame_v1

NumChannels
: HGGC_ARRAY_DESCRIPTOR_v2
: HGGC_ARRAY3D_DESCRIPTOR_v2

numDevices
: HGmulticastObjectProp_v1

numExecAffinityParams
: HGctxCreateParams

numExtSems
: HGGC_EXT_SEM_WAIT_NODE_PARAMS_v2
: HGGC_EXT_SEM_WAIT_NODE_PARAMS_v1
: HGGC_EXT_SEM_SIGNAL_NODE_PARAMS_v2
: HGGC_EXT_SEM_SIGNAL_NODE_PARAMS_v1

numLevels
: HGGC_EXTERNAL_MEMORY_MIPMAPPED_ARRAY_DESC_v1

hgsSciBufObject
: HGGC_EXTERNAL_MEMORY_HANDLE_DESC_v1

hgSciSync
: HGGC_EXTERNAL_SEMAPHORE_WAIT_PARAMS_v1

hgSciSyncObj
: HGGC_EXTERNAL_SEMAPHORE_HANDLE_DESC_v1

#### O {#O}

offset
: HGGC_EXTERNAL_MEMORY_BUFFER_DESC_v1
: HGGC_EXTERNAL_MEMORY_MIPMAPPED_ARRAY_DESC_v1
: HGmemcpy3DOperand_v1
: HGarrayMapInfo_v1

offsetX
: HGarrayMapInfo_v1

offsetY
: HGarrayMapInfo_v1

offsetZ
: HGarrayMapInfo_v1

oldUuid
: HGcheckpointGpuPair

operation
: HGstreamBatchMemOpParams_v1

overBudget
: HGasyncNotificationInfo

ownership
: HGGC_CHILD_GRAPH_NODE_PARAMS

#### P {#P}

paramArray
: HGGC_BATCH_MEM_OP_NODE_PARAMS_v2

paramsArray
: HGGC_EXT_SEM_SIGNAL_NODE_PARAMS_v1
: HGGC_EXT_SEM_WAIT_NODE_PARAMS_v1
: HGGC_EXT_SEM_WAIT_NODE_PARAMS_v2
: HGGC_EXT_SEM_SIGNAL_NODE_PARAMS_v2

pArray
: HGeglFrame_v1

phGraph_out
: HGGC_CONDITIONAL_NODE_PARAMS

pitch
: HGGC_MEMSET_NODE_PARAMS_v1
: HGGC_MEMSET_NODE_PARAMS_v2
: HGeglFrame_v1

pitchInBytes
: HGGC_RESOURCE_DESC_v1

planeCount
: HGeglFrame_v1

poolProps
: HGGC_MEM_ALLOC_NODE_PARAMS_v1
: HGGC_MEM_ALLOC_NODE_PARAMS_v2

portableClusterSizeMode
: HGlaunchAttributeValue

pPitch
: HGeglFrame_v1

preferredClusterDim
: HGlaunchAttributeValue

preferredCoscheduledSmCount
: HG_DEV_SM_RESOURCE_GROUP_PARAMS

priority
: HGlaunchAttributeValue

programmaticEvent
: HGlaunchAttributeValue

programmaticStreamSerializationAllowed
: HGlaunchAttributeValue

ptr
: HGmemcpy3DOperand_v1

#### R {#R}

regsPerBlock
: HGdevprop_v1

remote
: HGlaunchMemSyncDomainMap

requestedHandleTypes
: HGmemAllocationProp_v1

reserved
: HGgraphEdgeData
: HGcheckpointCheckpointArgs
: HGcheckpointRestoreArgs
: HGGC_MEMCPY_NODE_PARAMS
: HGcheckpointUnlockArgs
: HGdevWorkqueueResource
: HGarrayMapInfo_v1
: HGmemPoolProps_v1

reserved0
: HGGC_MEMCPY3D_v2
: HGgraphNodeParams
: HGcheckpointLockArgs

reserved1
: HGgraphNodeParams
: HGcheckpointLockArgs
: HGcheckpointRestoreArgs
: HGGC_MEMCPY3D_v2

reserved2
: HGgraphNodeParams

resourceType
: HGarrayMapInfo_v1

resType
: HGGC_RESOURCE_DESC_v1

result
: HGgraphExecUpdateResultInfo_v1

result_out
: HGGC_GRAPH_INSTANTIATE_PARAMS

rowLength
: HGmemcpy3DOperand_v1

#### S {#S}

sharedData
: HGctxCigParam

sharedDataType
: HGctxCigParam

sharedMemBytes
: HGGC_KERNEL_NODE_PARAMS_v2
: HGGC_KERNEL_NODE_PARAMS_v3
: HGGC_KERNEL_NODE_PARAMS_v1
: HGlaunchConfig
: HGGC_LAUNCH_PARAMS_v1

sharedMemCarveout
: HGlaunchAttributeValue

sharedMemoryMode
: HGlaunchAttributeValue

sharedMemPerBlock
: HGdevprop_v1

sharingScope
: HGdevWorkqueueConfigResource

SIMDWidth
: HGdevprop_v1

size
: HGGC_EXTERNAL_MEMORY_BUFFER_DESC_v1
: HGarrayMapInfo_v1
: HGmulticastObjectProp_v1
: HGGC_CONDITIONAL_NODE_PARAMS
: HGGC_ARRAY_MEMORY_REQUIREMENTS_v1
: HGGC_EXTERNAL_MEMORY_HANDLE_DESC_v1

sizeInBytes
: HGGC_RESOURCE_DESC_v1

smCoscheduledAlignment
: HGdevSmResource

smCount
: HGexecAffinityParam_v1
: HGdevSmResource
: HG_DEV_SM_RESOURCE_GROUP_PARAMS

src
: HGmemDecompressParams

srcAccessOrder
: HGmemcpyAttributes_v1

srcArray
: HGGC_MEMCPY2D_v2
: HGGC_MEMCPY3D_v2
: HGGC_MEMCPY3D_PEER_v1

srcContext
: HGGC_MEMCPY3D_PEER_v1

srcDevice
: HGGC_MEMCPY3D_PEER_v1
: HGGC_MEMCPY2D_v2
: HGGC_MEMCPY3D_v2

srcHeight
: HGGC_MEMCPY3D_v2
: HGGC_MEMCPY3D_PEER_v1

srcHost
: HGGC_MEMCPY2D_v2
: HGGC_MEMCPY3D_v2
: HGGC_MEMCPY3D_PEER_v1

srcLocHint
: HGmemcpyAttributes_v1

srcLOD
: HGGC_MEMCPY3D_PEER_v1
: HGGC_MEMCPY3D_v2

srcMemoryType
: HGGC_MEMCPY2D_v2
: HGGC_MEMCPY3D_v2
: HGGC_MEMCPY3D_PEER_v1

srcNumBytes
: HGmemDecompressParams

srcPitch
: HGGC_MEMCPY2D_v2
: HGGC_MEMCPY3D_v2
: HGGC_MEMCPY3D_PEER_v1

srcXInBytes
: HGGC_MEMCPY3D_PEER_v1
: HGGC_MEMCPY2D_v2
: HGGC_MEMCPY3D_v2

srcY
: HGGC_MEMCPY3D_v2
: HGGC_MEMCPY2D_v2
: HGGC_MEMCPY3D_PEER_v1

srcZ
: HGGC_MEMCPY3D_PEER_v1
: HGGC_MEMCPY3D_v2

streamCigParams
: HGstreamCigCaptureParams

streamSharedData
: HGstreamCigParam

streamSharedDataType
: HGstreamCigParam

subresourceType
: HGarrayMapInfo_v1

syncMode
: HGGC_HOST_NODE_PARAMS_v2

syncPolicy
: HGlaunchAttributeValue

#### T {#T}

textureAlign
: HGdevprop_v1

timeoutMs
: HGGC_EXTERNAL_SEMAPHORE_WAIT_PARAMS_v1
: HGcheckpointLockArgs

to_port
: HGgraphEdgeData

totalConstantMemory
: HGdevprop_v1

type
: HGGC_EXTERNAL_MEMORY_HANDLE_DESC_v1
: HGexecAffinityParam_v1
: HGgraphEdgeData
: HGGC_CONDITIONAL_NODE_PARAMS
: HGasyncNotificationInfo
: HGmemLocation_v1
: HGgraphNodeParams
: HGmemAllocationProp_v1
: HGGC_EXTERNAL_SEMAPHORE_HANDLE_DESC_v1

#### U {#U}

usage
: HGmemAllocationProp_v1
: HGmemPoolProps_v1

userData
: HGGC_HOST_NODE_PARAMS_v1
: HGGC_HOST_NODE_PARAMS_v2

#### V {#V}

val
: HGexecAffinitySmCount_v1

value
: HGGC_EXTERNAL_SEMAPHORE_WAIT_PARAMS_v1
: HGGC_EXTERNAL_SEMAPHORE_SIGNAL_PARAMS_v1
: HGlaunchAttribute
: HGGC_MEMSET_NODE_PARAMS_v2
: HGGC_MEMSET_NODE_PARAMS_v1

#### W {#W}

waitValue
: HGstreamBatchMemOpParams_v1

Width
: HGGC_ARRAY_DESCRIPTOR_v2

width
: HGGC_MEMSET_NODE_PARAMS_v1
: HGGC_RESOURCE_VIEW_DESC_v1
: HGeglFrame_v1
: HGGC_MEMSET_NODE_PARAMS_v2

Width
: HGGC_ARRAY3D_DESCRIPTOR_v2

width
: HGGC_ARRAY_SPARSE_PROPERTIES_v1
: HGGC_RESOURCE_DESC_v1

WidthInBytes
: HGGC_MEMCPY2D_v2
: HGGC_MEMCPY3D_v2
: HGGC_MEMCPY3D_PEER_v1

wqConcurrencyLimit
: HGdevWorkqueueConfigResource

writeValue
: HGstreamBatchMemOpParams_v1
