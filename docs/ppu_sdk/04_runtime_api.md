# SAIL HGGC Runtime API 参考 <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [概念与约束](#概念与约束)
  - [驱动 API 与运行时 API 的区别](#驱动-api-与运行时-api-的区别)
  - [API 同步行为](#api-同步行为)
  - [流同步行为](#流同步行为)
  - [图对象的线程安全性](#图对象的线程安全性)
  - [版本混用规则](#版本混用规则)
  - [HGGC 运行时 API 版本差异（hggcrt_v2 → hggcrt_v3）](#hggc-运行时-api-版本差异hggcrtv2-hggcrtv3)
- [基础与初始化](#基础与初始化)
  - [HGGC 运行时使用的数据类型](#hggc-运行时使用的数据类型)
  - [实用工具](#实用工具)
- [设备与上下文](#设备与上下文)
  - [设备管理](#设备管理)
  - [对等设备内存访问](#对等设备内存访问)
- [模块与代码加载](#模块与代码加载)
  - [模块与符号管理](#模块与符号管理)
- [内存管理](#内存管理)
  - [内存管理（分配/释放/预取/属性）](#内存管理分配释放预取属性)
  - [内存复制](#内存复制)
  - [内存填充](#内存填充)
  - [流有序内存分配器](#流有序内存分配器)
- [流与事件](#流与事件)
  - [流与事件管理](#流与事件管理)
- [执行与调度](#执行与调度)
  - [执行控制](#执行控制)
  - [图管理](#图管理)
- [互操作与扩展](#互操作与扩展)
  - [外部资源互操作](#外部资源互操作)
- [参考索引](#参考索引)
  - [数据结构索引](#数据结构索引)
  - [数据字段索引](#数据字段索引)


本文是 T-Head SAIL SDK 的 HGGC Runtime API（HGGCRT）完整参考，按模块组织：先讲使用约束与概念，再逐模块列出全部数据类型、宏、枚举、结构体与函数。API 命名遵循 CUDA Runtime 风格（`hggc` 前缀对应 `cuda`，`hg` 前缀对应 Driver API 的 `cu`），便于按 CUDA 经验迁移代码。

## 概念与约束

本节阐述 HGGC Runtime API 的核心概念与使用约束，建议在使用具体 API 前先行阅读。

### 驱动 API 与运行时 API 的区别

HGGC 提供两层主机端编程接口：**Driver API**（驱动 API）与 **Runtime API**（运行时 API）。两者覆盖的能力大体一致，互相兼容并可在同一进程中混用，但在抽象层级、可控粒度、与上下文/模块的耦合方式上存在结构性差异。

#### 抽象层级对比

| 维度 | Runtime API | Driver API |
|---|---|---|
| 上下文管理 | 隐式（自动绑定主上下文） | 显式（应用自行创建、压栈、绑定） |
| 模块加载 | 隐式（程序启动时自动加载全部 device code） | 显式（按需加载/卸载，可重复加载） |
| 核函数启动语法 | 支持三尖括号（`<<<>>>`）等语言级语法糖 | 仅显式 API，逐项指定执行配置与实参 |
| 与编程语言的耦合 | 紧耦合（依赖编译器前端） | 语言无关，仅与 hgbin 二进制对接 |
| 代码量 | 紧凑 | 偏冗长，但更可控 |

简言之：**Runtime API 牺牲控制粒度换取代码简洁；Driver API 牺牲简洁换取细粒度控制**。两者基于同一份事实接口约束，混用是显式支持的——参见下文"上下文协作"。Driver API 详见 `05_driver_api.md`。

#### 上下文协作机制

当 Runtime API 需要使用上下文时：

1. 若当前线程已通过 Driver API `hgCtxSetCurrent` 设置了上下文 → Runtime API 直接复用；
2. 否则 → Runtime API 使用主上下文（每个 (进程, 设备) 组合只有一个，引用计数管理）。

这意味着通过 Driver API 预建上下文后，Runtime API 及基于它的库（如 hgBLAS、hgFFT）会自动工作在同一上下文之上，无需额外绑定。

**典型陷阱：同进程多组件共享主上下文。** 多个独立模块（插件/SDK）默认共享主上下文。若任一方调用 `hggcDeviceReset()` 销毁主上下文，其他模块后续调用将失败。

**推荐模式**：宿主进程用 Driver API 显式建立上下文并 push 为当前上下文，各组件通过 Runtime API 协同工作于该上下文，不再依赖主上下文的隐式共享。

#### 选用建议

| 场景 | 推荐 |
|---|---|
| 应用层产品开发，对上下文/模块管理无特殊需求 | Runtime API |
| 需要按需加载/卸载 hgbin、热更新 kernel、多语言绑定 | Driver API |
| 框架/SDK 的底层运行时（如 JIT、异构调度器） | Driver API |
| 同一进程内有多个第三方插件协同 | Driver API 建上下文 + 各插件用 Runtime API 协作 |

### API 同步行为

HGGC 提供两套形态的 `memcpy` / `memset` 接口：未带 `Async` 后缀的"基础形态"与带 `Async` 后缀的"异步形态"。**接口是否阻塞主机线程，并非由名字决定**，而是取决于实参所描述的内存类型与传输方向。下表给出每一种组合下的精确行为，是性能调优与流编排的依据。

任何 HGGC 接口在内部资源紧张或资源不可用时都可能发生短暂阻塞。这类阻塞是实现细节，应用不应依赖未在文档中声明的同步语义。

#### Memcpy

**基础形态（不带 Async 后缀）**——`hggcMemcpy*` 系列在不同源/目的组合下的同步语义：

| 源 → 目的 | 主机线程是否阻塞 | 默认流上的同步 | 备注 |
|---|---|---|---|
| 可分页主机内存 → 设备 | 部分阻塞 | 复制发起前先做流同步 | 接口在数据被搬到内部 staging 缓冲后即返回；至最终目的地的 DMA 可能仍未完成 |
| 锁页主机内存 → 设备 | 完全阻塞 | 是 | 调用返回前 DMA 已完成 |
| 设备 → 可分页/锁页主机内存 | 完全阻塞 | 是 | 仅在数据复制完毕后返回 |
| 设备 → 设备 | 不阻塞主机 | 不强制主机端同步 | 仅在设备执行队列上排队 |
| 主机 → 主机 | 完全阻塞 | 是 | 行为等同同步 memcpy |

**异步形态（带 Async 后缀）**：

| 源 → 目的 | 主机线程是否阻塞 | 备注 |
|---|---|---|
| 设备 ↔ 可分页主机内存 | 可能阻塞 | 当驱动需要先把可分页内存固定到内部锁页缓冲区时，会进入流同步并完成临时拷贝 |
| 主机 → 主机 | 完全阻塞 | 异步形态此时退化为同步行为 |
| 其他所有组合 | 完全异步 | 仅在流上排队，立即返回 |

简言之：**`Async` 后缀是必要条件而非充分条件**——只有当源、目的都不涉及"可分页主机内存"或"主机到主机传输"时，调用才真正完全异步。

#### Memset

`hggcMemset*`（无 Async 后缀）相对主机为异步执行，**唯一例外**是目的地为锁页主机内存——此时调用阻塞至填充完成。

`hggcMemsetAsync` 始终相对主机异步，将填充操作排队到流后立即返回。

#### 核函数启动

核函数启动相对主机始终异步。关于并发核函数执行、与数据传输之间的重叠，请参阅 HGGC 编程指南（`../ppu_hggc/`）。

比赛关联：要让 H2D 权重/图像拷贝与 kernel 重叠，必须用锁页（pinned）主机内存 + `hggcMemcpyAsync` 非默认流组合；可分页内存会暗中退化为流同步，直接拉高 TTFT。

### 流同步行为

HGGC 的"默认流"（default stream）有**两种语义**——传统默认流（legacy）与每线程默认流（per-thread）——选哪一种取决于编译期开关。理解两者的差异，是写出正确的多流并发程序的前提。

#### 默认流的两种语义

当向 HGGC API 传入流参数 `0` 或调用未显式指定流的 API（隐式在流上操作）时，实际生效的是"默认流"。**默认流不是一个固定的流对象**，而是由编译期选项决定的一种行为模式：

| 模式 | 同步语义 | 显式句柄 |
|---|---|---|
| Legacy（传统） | 与同一上下文中的所有非阻塞流之外的流互相同步 | `HG_STREAM_LEGACY` / `hggcStreamLegacy` |
| Per-thread（每线程） | 线程局部 + 上下文局部，与其他流互不同步（行为类似显式创建的普通流） | `HG_STREAM_PER_THREAD` / `hggcStreamPerThread` |

选择哪一种由编译选项 `--default-stream` 控制，作用范围是**编译单元**——同一程序的不同 .c/.cpp 文件可以使用不同模式，且二者可以共存于同一进程。

也可以在包含任何 HGGC 头文件之前定义宏 `HGGC_API_PER_THREAD_DEFAULT_STREAM` 来启用 per-thread 模式。无论用编译选项还是宏触发，最终启用 per-thread 的编译单元中都会定义 `HGGC_API_PER_THREAD_DEFAULT_STREAM`，可以用于条件编译。

#### 传统默认流（legacy）

传统默认流是一个**隐式同步的流**：每当传统默认流上排入新操作时，运行时会让传统流先等待当前上下文中所有"阻塞"流（即非 `hggcStreamNonBlocking` 创建的流）已排入的操作完成；然后将新操作排入传统流；之后所有阻塞流再隐式等待传统流完成。

举例：

```c
k_1<<<1, 1, 0, s>>>();   // 排入流 s
k_2<<<1, 1>>>();          // 排入传统默认流
k_3<<<1, 1, 0, s>>>();   // 排入流 s
```

执行顺序约束为 `k_1 → k_2 → k_3`：传统流上的 `k_2` 等待 `k_1`，随后 `k_3` 等待 `k_2`。这等价于把传统默认流当成"全局栅栏"。

**绕过传统流同步**：用 `hggcStreamNonBlocking` 标志创建的流不参与上述同步——它既不会被传统流阻塞，也不会阻塞传统流。

**显式句柄**：在不希望依赖传 `0` 的隐式行为时，可以直接传入 `HG_STREAM_LEGACY` / `hggcStreamLegacy` 来引用传统默认流。

#### 每线程默认流（per-thread）

每线程默认流是 **(线程, 上下文) 二元组局部** 的隐式流，行为与显式创建的普通流一致：

- 不会与其他流自动同步（不再有"全局栅栏"语义）；
- 不是 `hggcStreamNonBlocking` 流；如果同一程序中既有 per-thread 编译单元、又有 legacy 编译单元，则 per-thread 默认流仍会与传统默认流互相同步（避免行为割裂）。
- 显式句柄：`HG_STREAM_PER_THREAD` / `hggcStreamPerThread`。

**何时选 per-thread**：当多个线程各自独立向设备提交工作、不希望它们因隐式默认流同步而互相阻塞时，per-thread 是更易写出高并发代码的选择。

#### 选择建议

| 场景 | 建议 |
|---|---|
| 历史代码迁移、需保留全局栅栏语义 | Legacy |
| 多线程并发、追求最大设备占用 | Per-thread |
| 同进程内既有库要求 legacy、又有库要求 per-thread | 编译期按编译单元分别设置；二者会自动同步，可正确共存 |

### 图对象的线程安全性

HGGC 的图（Graph）对象——`hggcGraph_t` / `HGgraph` 及其衍生句柄——**内部不做并发控制**。从多个线程**同时**访问同一图对象的任何 API 调用都会导致未定义行为。

#### 谁需要外部串行化

以下情形必须由调用方自己保证不会并发：

- 修改类调用：节点的增删改、边的连接/断开、属性更新等。
- **看起来是只读，实则同样需要串行化**的调用，例如：
  - `hggcGraphClone()` / `hgGraphClone()`——克隆会读取并锁定源图的内部结构；
  - `hggcGraphInstantiate()` / `hgGraphInstantiate()`——实例化过程会遍历图节点。

换言之：**没有任何一个图相关 API、也没有任何一对 API 组合**，可以保证在多线程同时访问同一图对象时是安全的。

#### 实践建议

- 把图对象视为线程不安全的容器：可以在多个线程间传递所有权，但同一时刻只允许一个线程持有；
- 如果业务确需"读多写少"的并发观测，请由调用方在外层加读写锁；
- 不同图对象之间不存在隐式锁竞争，可以并行构建/实例化。

### 版本混用规则

HGGC 在 API 演进中通过两类机制保证向前兼容：**Runtime API 的主版本绑定** 与 **Driver API 的逐函数 ABI 标签**（`_v*` 后缀）。以下归纳跨版本/跨编译单元混用时必须遵守的规则，避免在升级过程中出现 ABI 不匹配。

#### Runtime API：按主版本绑定

- Runtime 的 ABI 在每个主版本发布时整体更新；
- HGGC 定义的全部类型（包括不透明句柄与可读结构体，例如 `hggcDeviceProp`）的 ABI 与 **Runtime 主版本**绑定；
- **跨主版本边界传递这些类型是不安全的**：若函数 A 与函数 B 由不同主版本工具链编译并链接进同一可执行文件，两者之间不应直接互传 HGGC 类型。

#### Driver API：逐函数 ABI 标签

Driver API 采用更细粒度的版本标签——通过函数名的 `_v*` 后缀显式标注 ABI：

- 同一类型的不同 ABI 版本不应跨版本传递。例如：

  ```c
  HGGC_MEMCPY2D_v1 cpy1;
  hgMemcpy2D_v2(&cpy1);   // ✗ 类型版本与函数版本不匹配，行为未定义
  ```

- 始终用函数声明所要求的版本类型来构造实参。

#### 资源生命周期内不得跨版本调用

对**任何在 HGGC 中具有句柄/状态的资源**——IPC handle、device memory、stream、context、event 等——其分配 API 与释放 API 必须**版本一致**。例如：

```c
HGdeviceptr p;
hgMemAlloc_v2(&p, size);
hgMemFree(p);             // ✗ 与 _v2 分配不匹配，应使用 hgMemFree_v2
hgMemFree_v2(p);          // ✓
```

混用不同版本的 alloc / free 可能引发内部簿记错乱、内存泄漏或运行时报错。

#### 实践要点

| 检查项 | 建议 |
|---|---|
| 同一资源的 alloc/free 函数版本 | 严格一致 |
| 跨主版本工具链构建 | 不要在边界上互传 HGGC 类型；改用平台原生 POD 类型 |
| 升级到新主版本 | 全量重编译相关源文件；不要尝试只替换部分翻译单元 |
| 第三方库提供的句柄 | 调用方与库应商定使用同一主版本编译 |

### HGGC 运行时 API 版本差异（hggcrt_v2 → hggcrt_v3）

`hggcrt_v2` 是上一代运行时 API，`hggcrt_v3` 是新一代运行时 API，推荐使用 v3。升级到 v3 时源代码需做相应修改，**ABI 不向后兼容**。主要差异：

**API 与接口：**

- 带 v2 / v3 后缀的 API 升级为默认 API，之前相应的默认 API 不再暴露。
- 图（Graph）相关接口统一加入 `hggcGraphEdgeData` 参数，支持边属性。
- 移除已弃用的纹理引用绑定 API（建议改用纹理对象 API）。
- 新增内存位置（`hggcMemLocation`）感知的内存预取/池管理接口。
- 新增运行时日志（Logs）API 与原子操作能力查询 API。

**数据类型：**

- `hggcDeviceProp` 成员调整：移除时钟频率、纹理 1D linear 上限等 8 个旧字段，新增 NUMA / PCI / MPS 等 7 个字段。
- 多个外部资源/资源描述 struct 末尾追加 `reserved[]` 预留字段，用于后续扩展。
- `hggcDeviceAttr` / `hggcDeviceP2PAttr` / `hggcError` 等 enum 弃用部分旧值；`hggcMemAllocationType` / `hggcMemLocationType` 等新增枚举值。
- 移除 3 个旧版 struct（`hggcExternalSemaphoreSignalParams_v1` 等）。
- 新增 Logs 与原子能力相关的数据类型（`hggcLogIterator`、`hggcAtomicOperation`、`hggcLogsCallback_t` 等）。

#### 数据类型变更

**Struct 成员变更（9 个）：**

| Struct | v3 移除的成员 | v3 新增的成员 |
|---|---|---|
| `hggcDeviceProp` | `clockRate`、`computeMode`、`cooperativeMultiDeviceLaunch`、`deviceOverlap`、`kernelExecTimeoutEnabled`、`maxTexture1DLinear`、`memoryClockRate`、`singleToDoublePrecisionPerfRatio` | `deviceNumaConfig`、`deviceNumaId`、`gpuPciDeviceID`、`gpuPciSubsystemID`、`hostNumaId`、`hostNumaMultinodeIpcSupported`、`mpsEnabled` |
| `hggcExternalMemoryBufferDesc` | — | `reserved` |
| `hggcExternalMemoryHandleDesc` | — | `reserved` |
| `hggcExternalMemoryMipmappedArrayDesc` | — | `reserved` |
| `hggcExternalSemaphoreHandleDesc` | — | `reserved` |
| `hggcLaunchAttributeValue` | — | `icnlinkUtilCentricScheduling` |
| `hggcPointerAttributes` | — | `reserved` |
| `hggcResourceDesc` | — | `flags`、`reserved` |
| `hggcResourceViewDesc` | — | `reserved` |

> **注意**：以 `reserved` 命名的成员为预留字段，调用方在初始化时应当置零以保证 ABI 前向兼容。

**Enum 值变更（9 个）：**

| Enum | v3 移除的值 | v3 新增的值 |
|---|---|---|
| `hggcDeviceAttr` | `hggcDevAttrCooperativeMultiDeviceLaunch = 96`、`hggcDevAttrMaxTimelineSemaphoreInteropSupported = 114`、`hggcDevAttrMaxPersistentL2CacheSize = hggcDevAttrPrivateStart` | `hggcDevAttrReserved96 = 96`、`hggcDevAttrHostMemoryPoolsSupported = 144`、`hggcDevAttrReserved145 = 145`、`hggcDevAttrOnlyPartialHostNativeAtomicSupported = 147`、`hggcDevAttrMaxPersistentL2CacheSize = 200` |
| `hggcDeviceP2PAttr` | `hggcDevP2PAttrMinPath = 256`、`hggcDevP2PAttrBandWidth = 257`、`hggcDevP2PAttrIsNeighbor = 258` | `hggcDevP2PAttrOnlyPartialNativeAtomicSupported = 5` |
| `hggcCGScope` | `hggcCGScopeMultiGrid = 2` | `hggcCGScopeReserved = 2` |
| `hggcChannelFormatKind` | `hggcChannelFormatKindUnsignedNormalized1010102 = 31` | — |
| `hggcError` | `hggcErrorInvalidGraphicsContext = 219`、`hggcErrorApiFailureBase = 10000` | — |
| `hggcJit_Fallback` | `hggcPreferPtx = 0` | `hggcPreferAsm = 0` |
| `hggcLaunchAttributeID` | — | `hggcLaunchAttributeIcnlinkUtilCentricScheduling = 16` |
| `hggcMemAllocationType` | — | `hggcMemAllocationTypeManaged = 0x2` |
| `hggcMemLocationType` | — | `hggcMemLocationTypeNone = 0` |

**宏定义变更：**

| 变更 | 宏 |
|---|---|
| v3 移除 | `hggcCooperativeLaunchMultiDeviceNoPostSync`、`hggcCooperativeLaunchMultiDeviceNoPreSync`（随 `hggcLaunchCooperativeKernelMultiDevice` 一并移除） |
| v3 新增 | `hggcKernelNodeAttributeIcnlinkUtilCentricScheduling` |

**v3 中移除的 Struct（3 个）：**

| Struct | 说明 |
|---|---|
| `hggcExternalSemaphoreSignalParams_v1` | 旧版外部信号量 signal 参数，由不带 `_v1` 后缀的当前版本替代 |
| `hggcExternalSemaphoreWaitParams_v1` | 旧版外部信号量 wait 参数，由不带 `_v1` 后缀的当前版本替代 |
| `hggcLaunchParams` | 仅供已移除的 `hggcLaunchCooperativeKernelMultiDevice` 使用，随之移除 |

**v3 新增数据类型：**

新增 enum `HGGClogLevel_enum`（日志级别，供 Logs API 使用）：

```c
enum HGGClogLevel_enum {
    hggcLogLevelError = 0,
    hggcLogLevelWarning = 1,
};
```

新增 enum `hggcAtomicOperation`（原子操作类型，供原子能力查询 API 使用）：

```c
enum hggcAtomicOperation {
    hggcAtomicOperationIntegerAdd = 0,
    hggcAtomicOperationIntegerMin = 1,
    hggcAtomicOperationIntegerMax = 2,
    hggcAtomicOperationIntegerIncrement = 3,
    hggcAtomicOperationIntegerDecrement = 4,
    hggcAtomicOperationAnd = 5,
    hggcAtomicOperationOr = 6,
    hggcAtomicOperationXOR = 7,
    hggcAtomicOperationExchange = 8,
    hggcAtomicOperationCAS = 9,
    hggcAtomicOperationFloatAdd = 10,
    hggcAtomicOperationFloatMin = 11,
    hggcAtomicOperationFloatMax = 12,
};
```

新增 enum `hggcAtomicOperationCapability`（原子操作能力位掩码）：

```c
enum hggcAtomicOperationCapability {
    hggcAtomicCapabilitySigned     = 1u << 0,
    hggcAtomicCapabilityUnsigned   = 1u << 1,
    hggcAtomicCapabilityReduction  = 1u << 2,
    hggcAtomicCapabilityScalar32   = 1u << 3,
    hggcAtomicCapabilityScalar64   = 1u << 4,
    hggcAtomicCapabilityScalar128  = 1u << 5,
    hggcAtomicCapabilityVector32x4 = 1u << 6,
};
```

新增 typedef：`hggcLogIterator`（定义为 `unsigned int`，Logs API 迭代器句柄）。

新增 callback 类型（用于 `hggcLogsRegisterCallback` 注册日志回调）：

```c
typedef void (HGGCRT_CB *hggcLogsCallback_t)(
    void *data,
    hggcLogLevel logLevel,
    char *message,
    size_t length);
```

#### v2 与 v3 已有 API 差异

**函数签名变更（10 个）**——以下函数在 v2 与 v3 中名称相同但签名发生变更：

1. `hggcGraphAddDependencies`——新增 `edgeData` 参数以支持边属性：

   ```c
   // v2
   hggcError_t hggcGraphAddDependencies(
       hggcGraph_t graph,
       const hggcGraphNode_t *from,
       const hggcGraphNode_t *to,
       size_t numDependencies);
   // v3
   hggcError_t hggcGraphAddDependencies(
       hggcGraph_t graph,
       const hggcGraphNode_t *from,
       const hggcGraphNode_t *to,
       const hggcGraphEdgeData *edgeData,
       size_t numDependencies);
   ```

2. `hggcGraphAddNode`——新增 `dependencyData` 参数：

   ```c
   // v2
   hggcError_t hggcGraphAddNode(
       hggcGraphNode_t *pGraphNode,
       hggcGraph_t graph,
       const hggcGraphNode_t *pDependencies,
       size_t numDependencies,
       struct hggcGraphNodeParams *nodeParams);
   // v3
   hggcError_t hggcGraphAddNode(
       hggcGraphNode_t *pGraphNode,
       hggcGraph_t graph,
       const hggcGraphNode_t *pDependencies,
       const hggcGraphEdgeData *dependencyData,
       size_t numDependencies,
       struct hggcGraphNodeParams *nodeParams);
   ```

3. `hggcGraphGetEdges`——新增 `edgeData` 输出参数：

   ```c
   // v2
   hggcError_t hggcGraphGetEdges(
       hggcGraph_t graph,
       hggcGraphNode_t *from,
       hggcGraphNode_t *to,
       size_t *numEdges);
   // v3
   hggcError_t hggcGraphGetEdges(
       hggcGraph_t graph,
       hggcGraphNode_t *from,
       hggcGraphNode_t *to,
       hggcGraphEdgeData *edgeData,
       size_t *numEdges);
   ```

4. `hggcGraphNodeGetDependencies`——新增 `edgeData` 输出参数：

   ```c
   // v2
   hggcError_t hggcGraphNodeGetDependencies(
       hggcGraphNode_t node,
       hggcGraphNode_t *pDependencies,
       size_t *pNumDependencies);
   // v3
   hggcError_t hggcGraphNodeGetDependencies(
       hggcGraphNode_t node,
       hggcGraphNode_t *pDependencies,
       hggcGraphEdgeData *edgeData,
       size_t *pNumDependencies);
   ```

5. `hggcGraphNodeGetDependentNodes`——新增 `edgeData` 输出参数：

   ```c
   // v2
   hggcError_t hggcGraphNodeGetDependentNodes(
       hggcGraphNode_t node,
       hggcGraphNode_t *pDependentNodes,
       size_t *pNumDependentNodes);
   // v3
   hggcError_t hggcGraphNodeGetDependentNodes(
       hggcGraphNode_t node,
       hggcGraphNode_t *pDependentNodes,
       hggcGraphEdgeData *edgeData,
       size_t *pNumDependentNodes);
   ```

6. `hggcGraphRemoveDependencies`——新增 `edgeData` 参数：

   ```c
   // v2
   hggcError_t hggcGraphRemoveDependencies(
       hggcGraph_t graph,
       const hggcGraphNode_t *from,
       const hggcGraphNode_t *to,
       size_t numDependencies);
   // v3
   hggcError_t hggcGraphRemoveDependencies(
       hggcGraph_t graph,
       const hggcGraphNode_t *from,
       const hggcGraphNode_t *to,
       const hggcGraphEdgeData *edgeData,
       size_t numDependencies);
   ```

7. `hggcStreamGetCaptureInfo`——新增 `edgeData_out` 输出参数：

   ```c
   // v2
   hggcError_t hggcStreamGetCaptureInfo(
       hggcStream_t stream,
       enum hggcStreamCaptureStatus *captureStatus_out,
       unsigned long long *id_out,
       hggcGraph_t *graph_out,
       const hggcGraphNode_t **dependencies_out,
       size_t *numDependencies_out);
   // v3
   hggcError_t hggcStreamGetCaptureInfo(
       hggcStream_t stream,
       enum hggcStreamCaptureStatus *captureStatus_out,
       unsigned long long *id_out,
       hggcGraph_t *graph_out,
       const hggcGraphNode_t **dependencies_out,
       const hggcGraphEdgeData **edgeData_out,
       size_t *numDependencies_out);
   ```

8. `hggcStreamUpdateCaptureDependencies`——新增 `dependencyData` 参数：

   ```c
   // v2
   hggcError_t hggcStreamUpdateCaptureDependencies(
       hggcStream_t stream,
       hggcGraphNode_t *dependencies,
       size_t numDependencies,
       unsigned int flags);
   // v3
   hggcError_t hggcStreamUpdateCaptureDependencies(
       hggcStream_t stream,
       hggcGraphNode_t *dependencies,
       const hggcGraphEdgeData *dependencyData,
       size_t numDependencies,
       unsigned int flags);
   ```

9. `hggcMemAdvise`——设备标识由整数 `device` 改为 `hggcMemLocation` 结构体：

   ```c
   // v2
   hggcError_t hggcMemAdvise(
       const void *devPtr,
       size_t count,
       enum hggcMemoryAdvise advice,
       int device);
   // v3
   hggcError_t hggcMemAdvise(
       const void *devPtr,
       size_t count,
       enum hggcMemoryAdvise advice,
       struct hggcMemLocation location);
   ```

10. `hggcMemPrefetchAsync`——目标设备由 `int dstDevice` 改为 `hggcMemLocation`，新增 `flags` 参数：

    ```c
    // v2
    hggcError_t hggcMemPrefetchAsync(
        const void *devPtr,
        size_t count,
        int dstDevice,
        hggcStream_t stream);
    // v3
    hggcError_t hggcMemPrefetchAsync(
        const void *devPtr,
        size_t count,
        struct hggcMemLocation location,
        unsigned int flags,
        hggcStream_t stream);
    ```

**v2 中带后缀变体已合并（15 个）**——v2 中的 `_v2` / `_v3` 后缀变体在 v3 中已统一升级为不带后缀的版本；调用方应改用升级后的接口：

| v2 函数 | v3 等价 |
| --- | --- |
| `hggcEventElapsedTime_v2` | `hggcEventElapsedTime` |
| `hggcGraphAddDependencies_v2` | `hggcGraphAddDependencies` |
| `hggcGraphAddNode_v2` | `hggcGraphAddNode` |
| `hggcGraphGetEdges_v2` | `hggcGraphGetEdges` |
| `hggcGraphNodeGetDependencies_v2` | `hggcGraphNodeGetDependencies` |
| `hggcGraphNodeGetDependentNodes_v2` | `hggcGraphNodeGetDependentNodes` |
| `hggcGraphRemoveDependencies_v2` | `hggcGraphRemoveDependencies` |
| `hggcMemAdvise_v2` | `hggcMemAdvise` |
| `hggcMemPrefetchAsync_v2` | `hggcMemPrefetchAsync` |
| `hggcSignalExternalSemaphoresAsync_v2` | `hggcSignalExternalSemaphoresAsync` |
| `hggcStreamGetCaptureInfo_v2` | `hggcStreamGetCaptureInfo` |
| `hggcStreamGetCaptureInfo_v3` | `hggcStreamGetCaptureInfo` |
| `hggcStreamGetCaptureInfo_ptsz` | `hggcStreamGetCaptureInfo` |
| `hggcStreamUpdateCaptureDependencies_v2` | `hggcStreamUpdateCaptureDependencies` |
| `hggcWaitExternalSemaphoresAsync_v2` | `hggcWaitExternalSemaphoresAsync` |

> **注意**：v3 中升级后的同名接口通常采用 v2 中 `_v2`/`_v3` 变体的签名，部分接口签名变更见上文"函数签名变更"。

**v3 中移除的纹理引用绑定 API（7 个）**——以下基于纹理引用（texture reference）的 API 在 v3 中已移除，请改用纹理对象（texture object）API（见"设备管理"等章节）：

- `hggcBindTexture`
- `hggcBindTexture2D`
- `hggcBindTextureToArray`
- `hggcBindTextureToMipmappedArray`
- `hggcGetTextureAlignmentOffset`
- `hggcGetTextureReference`
- `hggcUnbindTexture`

**其他移除的 API（1 个）：**

- `hggcLaunchCooperativeKernelMultiDevice`：多设备协作核函数启动接口在 v3 中移除，使用 `hggcLaunchCooperativeKernel` 代替。

#### v3 新增 API（12 个）

**运行时日志（Logs）API（5 个）**——新增的运行时日志获取与回调机制，便于运行时诊断：

```c
hggcError_t hggcLogsCurrent(
    hggcLogIterator *iterator_out,
    unsigned int flags);

hggcError_t hggcLogsDumpToFile(
    hggcLogIterator *iterator,
    const char *pathToFile,
    unsigned int flags);

hggcError_t hggcLogsDumpToMemory(
    hggcLogIterator *iterator,
    char *buffer,
    size_t *size,
    unsigned int flags);

hggcError_t hggcLogsRegisterCallback(
    hggcLogsCallback_t callbackFunc,
    void *userData,
    hggcLogsCallbackHandle *callback_out);

hggcError_t hggcLogsUnregisterCallback(
    hggcLogsCallbackHandle callback);
```

**原子操作能力查询 API（1 个）**——host 端原子操作能力查询接口：

```c
hggcError_t hggcDeviceGetHostAtomicCapabilities(
    unsigned int *capabilities,
    const enum hggcAtomicOperation *operations,
    unsigned int count,
    int device);
```

**内存池关联 API（3 个）**——按内存位置（`hggcMemLocation`）与分配类型查询/设置内存池：

```c
hggcError_t hggcMemGetDefaultMemPool(
    hggcMemPool_t *memPool,
    struct hggcMemLocation *location,
    enum hggcMemAllocationType type);

hggcError_t hggcMemGetMemPool(
    hggcMemPool_t *memPool,
    struct hggcMemLocation *location,
    enum hggcMemAllocationType type);

hggcError_t hggcMemSetMemPool(
    struct hggcMemLocation *location,
    enum hggcMemAllocationType type,
    hggcMemPool_t memPool);
```

**批量内存预取/丢弃 API（3 个）**：

```c
hggcError_t hggcMemDiscardBatchAsync(
    void **dptrs,
    size_t *sizes,
    size_t count,
    unsigned long long flags,
    hggcStream_t stream);

hggcError_t hggcMemDiscardAndPrefetchBatchAsync(
    void **dptrs,
    size_t *sizes,
    size_t count,
    struct hggcMemLocation *prefetchLocs,
    size_t *prefetchLocIdxs,
    size_t numPrefetchLocs,
    unsigned long long flags,
    hggcStream_t stream);

hggcError_t hggcMemPrefetchBatchAsync(
    void **dptrs,
    size_t *sizes,
    size_t count,
    struct hggcMemLocation *prefetchLocs,
    size_t *prefetchLocIdxs,
    size_t numPrefetchLocs,
    unsigned long long flags,
    hggcStream_t stream);
```

## 基础与初始化

本节涵盖运行时的基础设施：数据类型定义以及通用辅助工具（版本查询、错误处理、驱动入口点访问）。

### HGGC 运行时使用的数据类型

本模块定义 HGGC Runtime API 使用的**全部公共数据类型**：枚举（错误码、设备属性标识、内存类型等）、结构体 typedef、不透明句柄、宏常量以及回调函数签名。其他模块的 API 签名均依赖此处的类型定义。

#### 数据结构清单

Runtime API 暴露的全部数据结构（struct / union / class），各字段的出现位置索引见文末"数据字段索引"：

- `__hggcOccupancyB2DHelper`（class）
- `hggcAccessPolicyWindow`
- `hggcArrayMemoryRequirements`
- `hggcArraySparseProperties`
- `hggcAsyncNotificationInfo_t`
- `hggcChildGraphNodeParams`
- `hggcConditionalNodeParams`
- `hggcDeviceProp`
- `hggcEventRecordNodeParams`
- `hggcEventWaitNodeParams`
- `hggcExtent`
- `hggcFuncAttributes`
- `hggcGraphEdgeData`
- `hggcGraphExecUpdateResultInfo`
- `hggcGraphInstantiateParams`
- `hggcGraphKernelNodeUpdate`
- `hggcGraphNodeParams`
- `hggcHostNodeParams` / `hggcHostNodeParamsV2`
- `hggcIpcEventHandle_t`
- `hggcIpcMemHandle_t`
- `hggcKernelNodeParams` / `hggcKernelNodeParamsV2`
- `hggcLaunchAttribute`
- `hggcLaunchAttributeValue`（union）
- `hggcLaunchConfig_t`
- `hggcMemAccessDesc`
- `hggcMemAllocNodeParams` / `hggcMemAllocNodeParamsV2`
- `hggcMemcpy3DOperand`
- `hggcMemcpy3DParms`
- `hggcMemcpy3DPeerParms`
- `hggcMemcpyAttributes`
- `hggcMemcpyNodeParams`
- `hggcMemFreeNodeParams`
- `hggcMemLocation`
- `hggcMemPoolProps`
- `hggcMemPoolPtrExportData`
- `hggcMemsetParams` / `hggcMemsetParamsV2`
- `hggcOffset3D`
- `hggcPitchedPtr`
- `hggcPointerAttributes`
- `hggcPos`
- `HGuuid_st`

其中 `hggcPointerAttributes` 的完整定义：

```c
struct hggcPointerAttributes {
    enum hggcMemoryType type;   // 内存类型：Unregistered / Host / Device / Managed
    int device;                 // 分配所在（或分配时的当前）设备
    void *devicePointer;        // 可在当前设备上访问该内存的设备指针别名，不可直接访问时为 NULL
    void *hostPointer;          // 可在主机上访问该内存的主机指针别名，不可直接访问时为 NULL
}
```

#### 宏定义

| 宏 | 值 | 说明 |
|---|---|---|
| `HGGC_IPC_HANDLE_SIZE` | 64 | HGGC IPC 句柄大小 |
| `hggcArrayColorAttachment` | 0x20 | 图形 API 中将 mipmapped array 用作颜色目标时，必须在 `hggcExternalMemoryGetMappedMipmappedArray` 中设置 |
| `hggcArrayCubemap` | 0x04 | 必须在 `hggcMalloc3DArray` 中设置，以创建 cubemap HGGC array |
| `hggcArrayDefault` | 0x00 | 默认的 HGGC array 分配标志 |
| `hggcArrayDeferredMapping` | 0x80 | 必须在 `hggcMallocArray`/`hggcMalloc3DArray`/`hggcMallocMipmappedArray` 中设置，创建延迟映射的 HGGC array 或 mipmapped array |
| `hggcArrayLayered` | 0x01 | 必须在 `hggcMalloc3DArray` 中设置，创建分层 HGGC array |
| `hggcArraySparse` | 0x40 | 必须在 `hggcMallocArray`/`hggcMalloc3DArray`/`hggcMallocMipmappedArray` 中设置，创建稀疏 HGGC array 或 mipmapped array |
| `hggcArraySparsePropertiesSingleMipTail` | 0x1 | 分层的稀疏 HGGC array 或 mipmapped array 在所有层上共享单个 mip tail 区域 |
| `hggcArraySurfaceLoadStore` | 0x02 | 必须在 `hggcMallocArray` 或 `hggcMalloc3DArray` 中设置，以便将 surface 绑定到 HGGC array |
| `hggcArrayTextureGather` | 0x08 | 必须在 `hggcMallocArray` 或 `hggcMalloc3DArray` 中设置，以便在 HGGC array 上执行纹理 gather 操作 |
| `hggcCpuDeviceId` | ((int)-1) | 表示 CPU 的设备 id |
| `hggcDeviceBlockingSync` | 0x04 | **废弃**，由 `hggcDeviceScheduleBlockingSync` 替代。设备标志——使用阻塞同步 |
| `hggcDeviceLmemResizeToMax` | 0x10 | 设备标志——在核函数启动后保留本地内存分配 |
| `hggcDeviceMapHost` | 0x08 | 设备标志——支持映射的 pinned 分配 |
| `hggcDeviceMask` | 0xff | 设备标志掩码 |
| `hggcDeviceScheduleAuto` | 0x00 | 设备标志——自动调度 |
| `hggcDeviceScheduleBlockingSync` | 0x04 | 设备标志——使用阻塞同步 |
| `hggcDeviceScheduleMask` | 0x07 | 设备调度标志掩码 |
| `hggcDeviceScheduleSpin` | 0x01 | 设备标志——默认采用自旋调度 |
| `hggcDeviceScheduleYield` | 0x02 | 设备标志——默认采用 yield 调度 |
| `hggcDeviceSyncMemops` | 0x80 | 设备标志——确保在该上下文上的同步内存操作会进行同步 |
| `hggcEventBlockingSync` | 0x01 | 事件使用阻塞同步 |
| `hggcEventDefault` | 0x00 | 默认事件标志 |
| `hggcEventDisableTiming` | 0x02 | 事件不会记录计时数据 |
| `hggcEventInterprocess` | 0x04 | 该事件适用于进程间使用，必须同时设置 `hggcEventDisableTiming` |
| `hggcEventRecordDefault` | 0x00 | 默认事件记录标志 |
| `hggcEventRecordExternal` | 0x01 | 执行流 capture 时，该事件会以外部事件节点的形式被捕获到图中 |
| `hggcEventWaitDefault` | 0x00 | 默认事件等待标志 |
| `hggcEventWaitExternal` | 0x01 | 执行流 capture 时，该事件会以外部事件节点的形式被捕获到图中 |
| `hggcExternalMemoryDedicated` | 0x1 | 表示该 external memory 对象是专用资源 |
| `hggcExternalSemaphoreSignalSkipHgSciBufMemSync` | 0x01 | `hggcExternalSemaphoreSignalParams::flags` 含此标志时，signal 跳过对所有以 `hggcExternalMemoryHandleTypeHgSciBuf` 导入的 external memory 对象的内存同步操作（默认执行以保证数据一致性） |
| `hggcExternalSemaphoreWaitSkipHgSciBufMemSync` | 0x02 | 同上，但用于 wait 操作 |
| `hggcGraphKernelNodePortDefault` | 0 | 当核函数执行完成时，该端口激活 |
| `hggcGraphKernelNodePortLaunchCompletion` | 2 | 当核函数的所有线程块都已开始执行时激活。另见 `hggcLaunchAttributeLaunchCompletionEvent` |
| `hggcGraphKernelNodePortProgrammatic` | 1 | 当核函数的所有线程块都已触发编程启动完成或已终止时激活。必须与边类型 `hggcGraphDependencyTypeProgrammatic` 一起使用。另见 `hggcLaunchAttributeProgrammaticEvent` |
| `hggcHostAllocDefault` | 0x00 | 默认的 page-locked 分配标志 |
| `hggcHostAllocMapped` | 0x02 | 将分配映射到设备地址空间 |
| `hggcHostAllocPortable` | 0x01 | 所有 HGGC 上下文均可访问的 pinned 内存 |
| `hggcHostAllocWriteCombined` | 0x04 | write-combined 内存 |
| `hggcHostRegisterDefault` | 0x00 | 默认的主机内存注册标志 |
| `hggcHostRegisterIoMemory` | 0x04 | 内存映射的 I/O 空间 |
| `hggcHostRegisterMapped` | 0x02 | 将已注册内存映射到设备地址空间 |
| `hggcHostRegisterPortable` | 0x01 | 所有 HGGC 上下文均可访问的 pinned 内存 |
| `hggcHostRegisterReadOnly` | 0x08 | 内存映射的只读区域 |
| `hggcInitDeviceFlagsAreValid` | 0x01 | 告知 HGGC 运行时：已设置了 DeviceFlags |
| `hggcInvalidDeviceId` | ((int)-2) | 表示无效设备的设备 id |
| `hggcIpcMemLazyEnablePeerAccess` | 0x01 | 按需自动启用远端设备之间的 peer access |
| `hggcMemAttachGlobal` | 0x01 | 任意设备上的任意流都可以访问该内存 |
| `hggcMemAttachHost` | 0x02 | 任意设备上的任意流都无法访问该内存 |
| `hggcMemAttachSingle` | 0x04 | 该内存只能被关联设备上的单个流访问 |
| `hggcMemPoolCreateUsageHwDecompress` | 0x2 | 设置后表示该内存将用作硬件加速解压缩的缓冲区 |
| `hggcHgSciSyncAttrSignal` | 0x1 | HgSciSyncAttrList 的 flags 字段设此值时，表示应用需要填充 signaler 特定的 HgSciSyncAttr |
| `hggcHgSciSyncAttrWait` | 0x2 | 同上，填充 waiter 特定的 HgSciSyncAttr |
| `hggcOccupancyDefault` | 0x00 | 占用率计算默认行为 |
| `hggcOccupancyDisableCachingOverride` | 0x01 | 假设全局缓存已启用且无法自动关闭 |
| `hggcPeerAccessDefault` | 0x00 | 默认的 peer addressing 启用标志 |
| `hggcStreamDefault` | 0x00 | 默认流标志 |
| `hggcStreamLegacy` | ((hggcStream_t)0x1) | legacy 流句柄，引用具有 legacy 同步行为的隐式流（见"流同步行为"节） |
| `hggcStreamNonBlocking` | 0x01 | 该流不会与流 0（NULL stream）同步 |
| `hggcStreamPerThread` | ((hggcStream_t)0x2) | 每线程流句柄，引用具有每线程同步行为的隐式流 |

#### 类型定义（Typedefs）

| Typedef | 定义 | 说明 |
|---|---|---|
| `hggcArray_const_t` | `hggcArray*` | HGGC 数组，用作拷贝源参数 |
| `hggcArray_t` | `hggcArray*` | HGGC 数组 |
| `hggcAsyncCallbackHandle_t` | `hggcAsyncCallbackEntry*` | HGGC 异步回调句柄 |
| `hggcError_t` | `enum hggcError` | HGGC 错误类型 |
| `hggcEvent_t` | `HGevent_st*` | HGGC 事件 |
| `hggcExternalMemory_t` | `HGexternalMemory_st*` | HGGC 外部内存 |
| `hggcExternalSemaphore_t` | `HGexternalSemaphore_st*` | HGGC 外部信号量 |
| `hggcFunction_t` | `HGfunc_st*` | HGGC 函数 |
| `hggcGraphConditionalHandle` | `unsigned long long` | 条件图节点句柄 |
| `hggcGraphDeviceNode_t` | `HGgraphDeviceUpdatableNode_st*` | 用于设备端节点更新的图设备节点句柄 |
| `hggcGraphExec_t` | `HGgraphExec_st*` | 可执行的 HGGC 图 |
| `hggcGraphNode_t` | `HGgraphNode_st*` | HGGC 图节点 |
| `hggcGraph_t` | `HGgraph_st*` | HGGC 图 |
| `hggcHostFn_t` | `void(HGGCRT_CB*)(void* userData)` | HGGC 主机函数（userData 为传入参数） |
| `hggcKernel_t` | `HGkern_st*` | HGGC 核函数 |
| `hggcMemPool_t` | `HGmemPoolHandle_st*` | HGGC 内存池 |
| `hggcMipmappedArray_const_t` | `hggcMipmappedArray*` | HGGC mipmapped array，用作源参数 |
| `hggcMipmappedArray_t` | `hggcMipmappedArray*` | HGGC mipmapped array |
| `hggcStream_t` | `HGstream_st*` | HGGC 流 |
| `hggcUserObject_t` | `HGuserObject_st*` | 用于图的 HGGC 用户对象 |

#### 枚举类型

**`enum hggcAccessProperty`**——为 `hggcAccessPolicyWindow` 的 hitProp 和 missProp 成员指定性能提示：

- `hggcAccessPropertyNormal = 0` — 普通的缓存驻留
- `hggcAccessPropertyStreaming = 1` — 流式访问更不容易在缓存中保留
- `hggcAccessPropertyLlcPersisting = 2` — 持久化访问更可能在 LLC 缓存中保留
- `hggcAccessPropertyL2Persisting = 3` — 持久化访问更可能在 L2 中保留

**`enum hggcAsyncNotificationType`**——可能发生的异步通知类型：

- `hggcAsyncNotificationTypeOverBudget = 0x1` — 当进程超过其设备内存预算时发送

**`enum hggcAtomicOperation`**——HGGC 支持的原子操作：`hggcAtomicOperationIntegerAdd = 0`（整数加法）、`hggcAtomicOperationIntegerMin = 1`（整数最小值）、`hggcAtomicOperationIntegerMax = 2`（整数最大值）、`hggcAtomicOperationIntegerIncrement = 3`（整数递增）、`hggcAtomicOperationIntegerDecrement = 4`（整数递减）、`hggcAtomicOperationAnd = 5`（按位与）、`hggcAtomicOperationOr = 6`（按位或）、`hggcAtomicOperationXOR = 7`（按位异或）、`hggcAtomicOperationExchange = 8`（交换）、`hggcAtomicOperationCAS = 9`（比较并交换）、`hggcAtomicOperationFloatAdd = 10`（浮点数加法）、`hggcAtomicOperationFloatMin = 11`（浮点数最小值）、`hggcAtomicOperationFloatMax = 12`（浮点数最大值）。

**`enum hggcAtomicOperationCapability`**——原子操作能力位掩码：`hggcAtomicCapabilitySigned = 1u<<0`（有符号整数）、`hggcAtomicCapabilityUnsigned = 1u<<1`（无符号整数）、`hggcAtomicCapabilityReduction = 1u<<2`（归约）、`hggcAtomicCapabilityScalar32 = 1u<<3`（32 位标量）、`hggcAtomicCapabilityScalar64 = 1u<<4`（64 位标量）、`hggcAtomicCapabilityScalar128 = 1u<<5`（128 位标量）、`hggcAtomicCapabilityVector32x4 = 1u<<6`（32x4 向量）。

**`enum hggcCGScope`**——cooperative group 作用域：

- `hggcCGScopeInvalid = 0` — 无效作用域
- `hggcCGScopeGrid = 1` — 由 grid_group 表示的作用域
- `hggcCGScopeReserved = 2` — 保留

**`enum hggcChannelFormatKind`**——通道格式种类：

| 值 | 含义 |
|---|---|
| `hggcChannelFormatKindSigned = 0` | 有符号通道格式 |
| `hggcChannelFormatKindUnsigned = 1` | 无符号通道格式 |
| `hggcChannelFormatKindFloat = 2` | 浮点通道格式 |
| `hggcChannelFormatKindNone = 3` | 无通道格式 |
| `hggcChannelFormatKindNV12 = 4` | 无符号 8 位整数，平面 4:2:0 YUV 格式 |
| `hggcChannelFormatKindUnsignedNormalized8X1 = 5` / `8X2 = 6` / `8X4 = 7` | 1/2/4 通道无符号 8 位归一化整数 |
| `hggcChannelFormatKindUnsignedNormalized16X1 = 8` / `16X2 = 9` / `16X4 = 10` | 1/2/4 通道无符号 16 位归一化整数 |
| `hggcChannelFormatKindSignedNormalized8X1 = 11` / `8X2 = 12` / `8X4 = 13` | 1/2/4 通道有符号 8 位归一化整数 |
| `hggcChannelFormatKindSignedNormalized16X1 = 14` / `16X2 = 15` / `16X4 = 16` | 1/2/4 通道有符号 16 位归一化整数 |
| `hggcChannelFormatKindUnsignedBlockCompressed1 = 17` | 4 通道无符号归一化块压缩（BC1） |
| `hggcChannelFormatKindUnsignedBlockCompressed1SRGB = 18` | 带 sRGB 的 BC1 |
| `hggcChannelFormatKindUnsignedBlockCompressed2 = 19` / `2SRGB = 20` | BC2 / 带 sRGB 的 BC2 |
| `hggcChannelFormatKindUnsignedBlockCompressed3 = 21` / `3SRGB = 22` | BC3 / 带 sRGB 的 BC3 |
| `hggcChannelFormatKindUnsignedBlockCompressed4 = 23` | 1 通道无符号归一化块压缩（BC4） |
| `hggcChannelFormatKindSignedBlockCompressed4 = 24` | 1 通道有符号归一化块压缩（BC4） |
| `hggcChannelFormatKindUnsignedBlockCompressed5 = 25` | 2 通道无符号归一化块压缩（BC5） |
| `hggcChannelFormatKindSignedBlockCompressed5 = 26` | 2 通道有符号归一化块压缩（BC5） |
| `hggcChannelFormatKindUnsignedBlockCompressed6H = 27` | 3 通道无符号 half-float 块压缩（BC6H） |
| `hggcChannelFormatKindSignedBlockCompressed6H = 28` | 3 通道有符号 half-float 块压缩（BC6H） |
| `hggcChannelFormatKindUnsignedBlockCompressed7 = 29` / `7SRGB = 30` | BC7 / 带 sRGB 的 BC7 |

**`enum hggcClusterSchedulingPolicy`**——Cluster 调度策略，可传递给 `hggcFuncSetAttribute`：

- `hggcClusterSchedulingPolicyDefault = 0` — 默认策略
- `hggcClusterSchedulingPolicySpread = 1` — 将 cluster 内的线程块分散到各个 SM
- `hggcClusterSchedulingPolicyLoadBalancing = 2` — 允许硬件在 cluster 内对线程块在 SM 之间进行负载均衡

**`enum hggcComputeMode`**——设备计算模式：

- `hggcComputeModeDefault = 0` — 默认计算模式
- `hggcComputeModeExclusive = 1` — 计算独占线程模式
- `hggcComputeModeProhibited = 2` — 禁止计算模式
- `hggcComputeModeExclusiveProcess = 3` — 计算独占进程模式

**`enum hggcDeviceAttr`**——设备属性（供 `hggcDeviceGetAttribute` 查询）：

| 值 | 含义 |
|---|---|
| `hggcDevAttrMaxThreadsPerBlock = 1` | 每个线程块的最大线程数 |
| `hggcDevAttrMaxBlockDimX = 2` / `Y = 3` / `Z = 4` | 线程块维度 X/Y/Z 的最大值 |
| `hggcDevAttrMaxGridDimX = 5` / `Y = 6` / `Z = 7` | grid 维度 X/Y/Z 的最大值 |
| `hggcDevAttrMaxSharedMemoryPerBlock = 8` | 每个线程块可用的最大共享内存（字节） |
| `hggcDevAttrTotalConstantMemory = 9` | 设备上可用于 `__constant__` 变量的内存（字节） |
| `hggcDevAttrWarpSize = 10` | 线程束大小（线程数） |
| `hggcDevAttrMaxPitch = 11` | 内存拷贝允许的最大步幅（字节） |
| `hggcDevAttrMaxRegistersPerBlock = 12` | 每个线程块可用的 32 位寄存器最大数量 |
| `hggcDevAttrClockRate = 13` | 峰值时钟频率（kHz） |
| `hggcDevAttrTextureAlignment = 14` | 纹理对齐要求 |
| `hggcDevAttrGpuOverlap = 15` | 设备可能可以在拷贝内存的同时并发执行核函数 |
| `hggcDevAttrMultiProcessorCount = 16` | 设备上的 multiprocessor 数量 |
| `hggcDevAttrKernelExecTimeout = 17` | 核函数是否有运行时长限制 |
| `hggcDevAttrIntegrated = 18` | 设备与主机内存集成 |
| `hggcDevAttrCanMapHostMemory = 19` | 设备可将主机内存映射到 HGGC 地址空间 |
| `hggcDevAttrComputeMode = 20` | 计算模式（hggcComputeMode） |
| `hggcDevAttrMaxTexture1DWidth = 21` | 1D 纹理最大宽度 |
| `hggcDevAttrMaxTexture2DWidth = 22` / `2DHeight = 23` | 2D 纹理最大宽度/高度 |
| `hggcDevAttrMaxTexture3DWidth = 24` / `3DHeight = 25` / `3DDepth = 26` | 3D 纹理最大宽度/高度/深度 |
| `hggcDevAttrMaxTexture2DLayeredWidth = 27` / `2DLayeredHeight = 28` / `2DLayeredLayers = 29` | 2D layered 纹理最大宽度/高度/层数 |
| `hggcDevAttrSurfaceAlignment = 30` | surface 对齐要求 |
| `hggcDevAttrConcurrentKernels = 31` | 设备可能可以并发执行多个核函数 |
| `hggcDevAttrEccEnabled = 32` | 设备已启用 ECC 支持 |
| `hggcDevAttrPciBusId = 33` | 设备的 PCI bus ID |
| `hggcDevAttrPciDeviceId = 34` | 设备的 PCI 设备 ID |
| `hggcDevAttrTccDriver = 35` | 设备正在使用 TCC 驱动模型 |
| `hggcDevAttrMemoryClockRate = 36` | 峰值显存时钟频率（kHz） |
| `hggcDevAttrGlobalMemoryBusWidth = 37` | 全局内存总线宽度（位） |
| `hggcDevAttrL2CacheSize = 38` | L2 cache 大小（字节） |
| `hggcDevAttrMaxThreadsPerMultiProcessor = 39` | 每个 multiprocessor 的最大驻留线程数 |
| `hggcDevAttrAsyncEngineCount = 40` | 异步引擎数量 |
| `hggcDevAttrUnifiedAddressing = 41` | 设备与主机共享统一地址空间 |
| `hggcDevAttrMaxTexture1DLayeredWidth = 42` / `1DLayeredLayers = 43` | 1D layered 纹理最大宽度/层数 |
| `hggcDevAttrMaxTexture2DGatherWidth = 45` / `2DGatherHeight = 46` | 设置 hggcArrayTextureGather 时 2D 纹理最大宽度/高度 |
| `hggcDevAttrMaxTexture3DWidthAlt = 47` / `3DHeightAlt = 48` / `3DDepthAlt = 49` | 备用的 3D 纹理最大宽度/高度/深度 |
| `hggcDevAttrPciDomainId = 50` | 设备的 PCI domain ID |
| `hggcDevAttrTexturePitchAlignment = 51` | 纹理的步幅对齐要求 |
| `hggcDevAttrMaxTextureCubemapWidth = 52` | cubemap 纹理的最大宽度/高度 |
| `hggcDevAttrMaxTextureCubemapLayeredWidth = 53` / `CubemapLayeredLayers = 54` | cubemap layered 纹理的最大宽度/高度/层数 |
| `hggcDevAttrMaxSurface1DWidth = 55` | 1D surface 最大宽度 |
| `hggcDevAttrMaxSurface2DWidth = 56` / `2DHeight = 57` | 2D surface 最大宽度/高度 |
| `hggcDevAttrMaxSurface3DWidth = 58` / `3DHeight = 59` / `3DDepth = 60` | 3D surface 最大宽度/高度/深度 |
| `hggcDevAttrMaxSurface1DLayeredWidth = 61` / `1DLayeredLayers = 62` | 1D layered surface 最大宽度/层数 |
| `hggcDevAttrMaxSurface2DLayeredWidth = 63` / `2DLayeredHeight = 64` / `2DLayeredLayers = 65` | 2D layered surface 最大宽度/高度/层数 |
| `hggcDevAttrMaxSurfaceCubemapWidth = 66` | cubemap surface 最大宽度 |
| `hggcDevAttrMaxSurfaceCubemapLayeredWidth = 67` / `CubemapLayeredLayers = 68` | cubemap layered surface 最大宽度/层数 |
| `hggcDevAttrMaxTexture1DLinearWidth = 69` | 1D linear 纹理最大宽度 |
| `hggcDevAttrMaxTexture2DLinearWidth = 70` / `2DLinearHeight = 71` / `2DLinearPitch = 72` | 2D linear 纹理最大宽度/高度/步幅（字节） |
| `hggcDevAttrMaxTexture2DMipmappedWidth = 73` / `2DMipmappedHeight = 74` | mipmapped 2D 纹理最大宽度/高度 |
| `hggcDevAttrComputeCapabilityMajor = 75` / `Minor = 76` | compute capability 主/次版本号 |
| `hggcDevAttrMaxTexture1DMipmappedWidth = 77` | mipmapped 1D 纹理最大宽度 |
| `hggcDevAttrStreamPrioritiesSupported = 78` | 设备支持流优先级 |
| `hggcDevAttrGlobalL1CacheSupported = 79` | 设备支持在 L1 中缓存 global |
| `hggcDevAttrLocalL1CacheSupported = 80` | 设备支持在 L1 中缓存 local |
| `hggcDevAttrMaxSharedMemoryPerMultiprocessor = 81` | 每个 multiprocessor 可用的最大共享内存（字节） |
| `hggcDevAttrMaxRegistersPerMultiprocessor = 82` | 每个 multiprocessor 可用的 32 位寄存器最大数量 |
| `hggcDevAttrManagedMemory = 83` | 设备可以在该系统上分配 managed memory |
| `hggcDevAttrIsMultiGpuBoard = 84` | 设备位于多 PPU 板卡上 |
| `hggcDevAttrMultiGpuBoardGroupID = 85` | 同一多 PPU 板卡上一组设备的唯一标识符 |
| `hggcDevAttrHostNativeAtomicSupported = 86` | 设备与主机之间的链路支持原生原子操作 |
| `hggcDevAttrSingleToDoublePrecisionPerfRatio = 87` | 单精度性能与双精度性能的比值 |
| `hggcDevAttrPageableMemoryAccess = 88` | 设备支持在不调用 hggcHostRegister 的情况下一致性访问 pageable memory |
| `hggcDevAttrConcurrentManagedAccess = 89` | 设备可与 CPU 并发一致性访问 managed memory |
| `hggcDevAttrComputePreemptionSupported = 90` | 设备支持 Compute Preemption |
| `hggcDevAttrCanUseHostPointerForRegisteredMem = 91` | 设备可在与 CPU 相同的虚拟地址处访问已注册的主机内存 |
| `hggcDevAttrReserved92 = 92` / `Reserved93 = 93` / `Reserved94 = 94` | 保留 |
| `hggcDevAttrCooperativeLaunch = 95` | 设备支持通过 hggcLaunchCooperativeKernel 启动 cooperative 核函数 |
| `hggcDevAttrReserved96 = 96` | 保留 |
| `hggcDevAttrMaxSharedMemoryPerBlockOptin = 97` | 每个线程块的最大 optin 共享内存（因芯片而异，见 hggcFuncSetAttribute） |
| `hggcDevAttrCanFlushRemoteWrites = 98` | 设备支持刷新尚未完成的 remote write |
| `hggcDevAttrHostRegisterSupported = 99` | 设备支持通过 hggcHostRegister 进行主机内存注册 |
| `hggcDevAttrPageableMemoryAccessUsesHostPageTables = 100` | 设备通过主机的页表访问 pageable memory |
| `hggcDevAttrDirectManagedMemAccessFromHost = 101` | 主机可在无需迁移的情况下直接访问设备上的 managed memory |
| `hggcDevAttrMaxBlocksPerMultiProcessor = 106` | 每个 multiprocessor 的最大线程块数 |
| `hggcDevAttrMaxPersistingL2CacheSize = 108` | L2 持久化缓存行容量设置的最大值（字节） |
| `hggcDevAttrMaxAccessPolicyWindowSize = 109` | `hggcAccessPolicyWindow::num_bytes` 的最大值 |
| `hggcDevAttrReservedSharedMemoryPerBlock = 111` | HGGC 驱动每个线程块预留的共享内存（字节） |
| `hggcDevAttrSparseHggcArraySupported = 112` | 设备支持稀疏 HGGC array 和稀疏 mipmapped array |
| `hggcDevAttrHostRegisterReadOnlySupported = 113` | 设备支持 hggcHostRegister 的 hggcHostRegisterReadOnly 标志 |
| `hggcDevAttrTimelineSemaphoreInteropSupported = 114` | 设备支持 external timeline semaphore 互操作 |
| `hggcDevAttrMemoryPoolsSupported = 115` | 设备支持 hggcMallocAsync 及 hggcMemPool 系列 API |
| `hggcDevAttrGPUDirectRDMASupported = 116` | 设备支持 GPUDirect RDMA API |
| `hggcDevAttrGPUDirectRDMAFlushWritesOptions = 117` | 返回值是位掩码，各 bit 见 hggcFlushGPUDirectRDMAWritesOptions |
| `hggcDevAttrGPUDirectRDMAWritesOrdering = 118` | 无需 flush 的消费者范围，见 hggcGPUDirectRDMAWritesOrdering |
| `hggcDevAttrMemoryPoolSupportedHandleTypes = 119` | 基于 mempool 的 IPC 支持的句柄类型 |
| `hggcDevAttrClusterLaunch = 120` | 设备支持 cluster 启动 |
| `hggcDevAttrDeferredMappingHggcArraySupported = 121` | 设备支持延迟映射的 HGGC array 和 mipmapped array |
| `hggcDevAttrReserved122 = 122` / `Reserved123 = 123` / `Reserved124 = 124` | 保留 |
| `hggcDevAttrIpcEventSupport = 125` | 设备支持 IPC 事件 |
| `hggcDevAttrMemSyncDomainCount = 126` | 设备支持的内存同步域数量 |
| `hggcDevAttrReserved127 = 127` / `Reserved128 = 128` / `Reserved129 = 129` | 保留 |
| `hggcDevAttrNumaConfig = 130` | 设备的 NUMA 配置（类型为 hggcDeviceNumaConfig） |
| `hggcDevAttrNumaId = 131` | PPU 内存的 NUMA 节点 ID |
| `hggcDevAttrReserved132 = 132` | 保留 |
| `hggcDevAttrMpsEnabled = 133` | 在该设备上创建的上下文将通过 MPS 共享 |
| `hggcDevAttrHostNumaId = 134` | 距离设备最近的主机节点的 NUMA ID；不支持 NUMA 时为 -1 |
| `hggcDevAttrVulkanCigSupported = 138` | 设备支持在 Vulkan 中使用 CIG |
| `hggcDevAttrGpuPciDeviceId = 139` | 16 位 PCI 设备 ID 与 16 位 PCI vendor ID 的组合值 |
| `hggcDevAttrGpuPciSubsystemId = 140` | 16 位 PCI subsystem ID 与 16 位 subsystem vendor ID 的组合值 |
| `hggcDevAttrReserved141 = 141` | 保留 |
| `hggcDevAttrHostNumaMemoryPoolsSupported = 142` | 设备支持在 hggcMallocAsync 与 hggcMemPool 系列 API 中使用 HOST_NUMA location |
| `hggcDevAttrHostNumaMultinodeIpcSupported = 143` | 设备支持多节点系统中节点间的 HostNuma location IPC |
| `hggcDevAttrHostMemoryPoolsSupported = 144` | 设备支持在 hgMemAllocAsync 与 hgMemPool 系列 API 中使用 HOST location |
| `hggcDevAttrReserved145 = 145` | 保留 |
| `hggcDevAttrD3D12CigSupported = 146` | 设备支持在 D3D12 中使用 CIG |
| `hggcDevAttrOnlyPartialHostNativeAtomicSupported = 147` | 设备与主机之间的链路仅支持部分原生原子操作 |
| `hggcDevAttrMax` | 枚举上限 |
| `hggcDevAttrPrivateStart = 200` | 私有属性起点 |
| `hggcDevAttrMaxPersistentL2CacheSize = hggcDevAttrPrivateStart` | 设备最大 L2 持续行容量 |
| `hggcDevAttrPpuId = 201` | 设备的 PPU ID |
| `hggcDevAttrDispatchMask = 202` | 设备调度掩码（CE 和 CU 掩码） |
| `hggcDevAttrPrivateEnd` | 私有属性终点 |

**`enum hggcDeviceNumaConfig`**——设备 NUMA 配置：

- `hggcDeviceNumaConfigNone = 0` — PPU 不是 NUMA 节点
- `hggcDeviceNumaConfigNumaNode` — PPU 是 NUMA 节点，`hggcDevAttrNumaId` 包含其 NUMA ID

**`enum hggcDeviceP2PAttr`**——设备 P2P 属性：

- `hggcDevP2PAttrPerformanceRank = 1` — 指示两个设备之间链路性能的相对值（值越低性能越好，0 为最高性能链接）
- `hggcDevP2PAttrAccessSupported = 2` — peer access 已启用
- `hggcDevP2PAttrNativeAtomicSupported = 3` — 支持通过该链路进行原生原子操作
- `hggcDevP2PAttrHggcArrayAccessSupported = 4` — 支持通过该链路访问 HGGC array
- `hggcDevP2PAttrOnlyPartialNativeAtomicSupported = 5` — 通过该链路仅支持部分 HGGC 支持的原子操作

**`enum hggcDriverEntryPointQueryResult`**——获取驱动 entry point 的状态：

- `hggcDriverEntryPointSuccess = 0` — 符号搜索找到了匹配项
- `hggcDriverEntryPointSymbolNotFound = 1` — 符号搜索未找到
- `hggcDriverEntryPointVersionNotSufficent = 2` — 符号搜索找到了，但版本不够高

**`enum hggcError`**——HGGC 错误类型（`hggcError_t`），完整取值表：

| 值 | 含义 |
|---|---|
| `hggcSuccess = 0` | API 调用未返回任何错误；对查询类调用也表示被查询操作已完成（`hggcEventQuery()`、`hggcStreamQuery()`） |
| `hggcErrorInvalidValue = 1` | 一个或多个参数不在可接受范围内 |
| `hggcErrorMemoryAllocation = 2` | 无法分配足够的内存或其他资源 |
| `hggcErrorInitializationError = 3` | 无法初始化 HGGC 驱动和运行时 |
| `hggcErrorHggcrtUnloading = 4` | 进程关闭期间、HGGC 驱动已卸载后调用运行时 API |
| `hggcErrorProfilerDisabled = 5` | 本次运行未初始化性能分析器 |
| `hggcErrorProfilerNotInitialized = 6` | 无需初始化也可启用/禁用性能分析，不再视为错误 |
| `hggcErrorProfilerAlreadyStarted = 7` | 性能分析已启用时再次启用，不再视为错误 |
| `hggcErrorProfilerAlreadyStopped = 8` | 性能分析已禁用时再次禁用，不再视为错误 |
| `hggcErrorInvalidConfiguration = 9` | 核函数启动请求了当前设备永远无法满足的资源（如共享内存超限、线程/块数过多），设备限制见 hggcDeviceProp |
| `hggcErrorVersionTranslation = 10` | 驱动版本新于运行时版本，返回了运行时无法转换的图节点参数信息 |
| `hggcErrorInvalidPitchValue = 12` | 步幅相关参数不在可接受范围内 |
| `hggcErrorInvalidSymbol = 13` | 符号名称/标识符无效 |
| `hggcErrorInvalidHostPointer = 16` | 至少一个主机指针不是有效主机指针 |
| `hggcErrorInvalidDevicePointer = 17` | 至少一个设备指针不是有效设备指针 |
| `hggcErrorInvalidTexture = 18` | 纹理无效 |
| `hggcErrorInvalidTextureBinding = 19` | 纹理绑定无效（如对未绑定纹理调用 hggcGetTextureAlignmentOffset()） |
| `hggcErrorInvalidChannelDescriptor = 20` | channel descriptor 无效（格式不属于 hggcChannelFormatKind 或维度无效） |
| `hggcErrorInvalidMemcpyDirection = 21` | memcpy 方向不属于 hggcMemcpyKind 指定的类型 |
| `hggcErrorAddressOfConstant = 22` | constant memory 变量现在可由运行时通过 hggcGetSymbolAddress() 获取地址 |
| `hggcErrorTextureFetchFailed = 23` | 无法执行纹理 fetch（曾用于设备 emulation） |
| `hggcErrorTextureNotBound = 24` | 纹理未绑定（曾用于设备 emulation） |
| `hggcErrorSynchronizationError = 25` | 某个同步操作失败（曾用于设备 emulation） |
| `hggcErrorInvalidFilterSetting = 26` | 使用线性过滤访问了非浮点纹理（不支持） |
| `hggcErrorInvalidNormSetting = 27` | 尝试以 normalized float 读取不支持的数据类型（不支持） |
| `hggcErrorMixedDeviceExecution = 28` | 不允许混合设备与设备 emulation 代码 |
| `hggcErrorNotYetImplemented = 31` | API 尚未实现（正式发布版本不会返回） |
| `hggcErrorMemoryValueTooLarge = 32` | 模拟的设备指针超过 32 位地址范围 |
| `hggcErrorStubLibrary = 34` | 应用加载的是 stub library 而非真实驱动 |
| `hggcErrorInsufficientDriver = 35` | 已安装的 HGGC 驱动版本低于运行时 library（不受支持的配置，应更新驱动） |
| `hggcErrorCallRequiresNewerDriver = 36` | 该 API 调用需要更新的 HGGC 驱动 |
| `hggcErrorInvalidSurface = 37` | surface 无效 |
| `hggcErrorDuplicateVariableName = 43` | 多个 global/constant 变量共享相同字符串名称 |
| `hggcErrorDuplicateTextureName = 44` | 多个纹理共享相同字符串名称 |
| `hggcErrorDuplicateSurfaceName = 45` | 多个 surface 共享相同字符串名称 |
| `hggcErrorDevicesUnavailable = 46` | 所有 HGGC 设备都繁忙或不可用（如 ComputeModeProhibited/ExclusiveProcess、长 kernel 占满 PPU、内存限制） |
| `hggcErrorIncompatibleDriverContext = 49` | 当前上下文与该 HGGC 运行时不兼容（驱动 API 创建的上下文版本过旧/非主上下文/已销毁） |
| `hggcErrorMissingConfiguration = 52` | 被调用的设备 function 此前未通过 hggcConfigureCall() 配置 |
| `hggcErrorPriorLaunchFailure = 53` | 先前的一次核函数启动失败（曾用于设备 emulation） |
| `hggcErrorLaunchMaxDepthExceeded = 65` | 设备运行时子 grid 深度超过最大嵌套启动数 |
| `hggcErrorLaunchFileScopedTex = 66` | 核函数使用了设备运行时不支持的 file-scoped 纹理（仅支持纹理对象 API 创建的纹理） |
| `hggcErrorLaunchFileScopedSurf = 67` | 同上，针对 surface（仅支持 Surface Object API 创建的 surface） |
| `hggcErrorSyncDepthExceeded = 68` | 设备运行时 hggcDeviceSynchronize 的 grid 深度超限；需提前用 hggcDeviceSetLimit 设置 hggcLimitDevRuntimeSyncDepth（增加深度会预留大量设备内存；仅 compute capability < 9.0 支持） |
| `hggcErrorLaunchPendingCountExceeded = 69` | 设备运行时启动超过 hggcLimitDevRuntimePendingLaunchCount 限制 |
| `hggcErrorInvalidDeviceFunction = 98` | 所请求的设备 function 不存在，或未针对正确的设备架构编译 |
| `hggcErrorNoDevice = 100` | 驱动未检测到任何支持 HGGC 的设备 |
| `hggcErrorInvalidDevice = 101` | 设备 ordinal 无效，或操作对该设备无效 |
| `hggcErrorDeviceNotLicensed = 102` | 设备没有有效的 Grid License |
| `hggcErrorSoftwareValidityNotEstablished = 103` | 运行时/驱动自检至少一项失败，无法确立有效性 |
| `hggcErrorStartupFailure = 127` | HGGC 运行时内部启动失败 |
| `hggcErrorInvalidKernelImage = 200` | 设备核函数 image 无效 |
| `hggcErrorDeviceUninitialized = 201` | 当前线程没有绑定任何上下文；或上下文句柄无效（hgCtxDestroy 后）；或混用不同 API 版本 |
| `hggcErrorMapBufferObjectFailed = 205` | 无法映射 buffer object |
| `hggcErrorUnmapBufferObjectFailed = 206` | 无法取消映射 buffer object |
| `hggcErrorArrayIsMapped = 207` | 指定的 array 当前已被映射，无法销毁 |
| `hggcErrorAlreadyMapped = 208` | 资源已被映射 |
| `hggcErrorNoKernelImageForDevice = 209` | 没有适用于该设备的可用核函数 image |
| `hggcErrorAlreadyAcquired = 210` | 资源已被获取 |
| `hggcErrorNotMapped = 211` | 资源未被映射 |
| `hggcErrorNotMappedAsArray = 212` | 已映射的资源无法作为 array 访问 |
| `hggcErrorNotMappedAsPointer = 213` | 已映射的资源无法作为指针访问 |
| `hggcErrorECHGncorrectable = 214` | 执行过程中检测到不可纠正的 ECC 错误 |
| `hggcErrorUnsupportedLimit = 215` | 传入的 hggcLimit 不被当前活动设备支持 |
| `hggcErrorDeviceAlreadyInUse = 216` | 试图访问已被其他线程使用的 exclusive-线程设备 |
| `hggcErrorPeerAccessUnsupported = 217` | 给定设备之间不支持 P2P access |
| `hggcErrorInvalidTix = 218` | TIX 编译失败 |
| `hggcErrorIcvlinkUncorrectable = 220` | 执行过程中检测到不可纠正的 ICNLink 错误 |
| `hggcErrorJitCompilerNotFound = 221` | 未找到 TIX JIT compiler library |
| `hggcErrorUnsupportedTixVersion = 222` | 提供的 TIX 使用不受支持的工具链编译 |
| `hggcErrorJitCompilationDisabled = 223` | JIT compilation 被禁用 |
| `hggcErrorUnsupportedExecAffinity = 224` | 提供的 execution affinity 不被该设备支持 |
| `hggcErrorUnsupportedDevSideSync = 225` | TIX JIT 要编译的代码包含不受支持的 hggcDeviceSynchronize 调用 |
| `hggcErrorContained = 226` | 设备上发生异常，但已被 PPU 的错误隔离能力所容纳（contained） |
| `hggcErrorInvalidSource = 300` | 设备核函数 source 无效 |
| `hggcErrorFileNotFound = 301` | 未找到指定文件 |
| `hggcErrorSharedObjectSymbolNotFound = 302` | 链接到 shared object 时解析失败 |
| `hggcErrorSharedObjectInitFailed = 303` | shared object 初始化失败 |
| `hggcErrorOperatingSystem = 304` | 某次 OS 调用失败 |
| `hggcErrorInvalidResourceHandle = 400` | 资源句柄无效 |
| `hggcErrorIllegalState = 401` | 所需资源不处于可执行所请求操作的有效状态 |
| `hggcErrorLossyQuery = 402` | 尝试以会丢弃语义上重要信息的方式对对象进行自省 |
| `hggcErrorSymbolNotFound = 500` | 未找到指定名称的符号 |
| `hggcErrorNotReady = 600` | 此前发出的异步操作尚未完成 |
| `hggcErrorIllegalAddress = 700` | 设备在无效的内存地址上执行了 load/store |
| `hggcErrorLaunchOutOfResources = 701` | 启动因资源不足而未发生 |
| `hggcErrorLaunchTimeout = 702` | 设备核函数执行时间过长 |
| `hggcErrorLaunchIncompatibleTexturing = 703` | 核函数启动使用了不兼容的 texturing 模式 |
| `hggcErrorPeerAccessAlreadyEnabled = 704` | 对已启用 peer addressing 的上下文再次调用 hggcDeviceEnablePeerAccess() |
| `hggcErrorPeerAccessNotEnabled = 705` | hggcDeviceDisablePeerAccess() 试图禁用尚未启用的 peer addressing |
| `hggcErrorSetOnActiveProcess = 708` | 在已通过非设备管理操作初始化运行时后调用 hggcSetValidDevices()/hggcSetDeviceFlags() 等；或 host 线程已有活动 HGcontext |
| `hggcErrorContextIsDestroyed = 709` | 当前上下文已被 hgCtxDestroy 销毁，或是尚未初始化的主上下文 |
| `hggcErrorAssert = 710` | 核函数执行期间设备代码触发了 assert |
| `hggcErrorTooManyPeers = 711` | 启用 peer access 所需的硬件资源已耗尽 |
| `hggcErrorHostMemoryAlreadyRegistered = 712` | 传给 hggcHostRegister() 的内存范围已经注册过 |
| `hggcErrorHostMemoryNotRegistered = 713` | 传给 hggcHostUnregister() 的指针不对应任何已注册内存区域 |
| `hggcErrorHardwareStackError = 714` | 设备在核函数执行期间的调用栈中遇到错误 |
| `hggcErrorIllegalInstruction = 715` | 设备在核函数执行期间遇到非法指令 |
| `hggcErrorMisalignedAddress = 716` | 设备在未对齐的内存地址上执行 load/store |
| `hggcErrorInvalidAddressSpace = 717` | 指令所操作的内存地址不属于允许的地址空间 |
| `hggcErrorInvalidPc = 718` | 设备遇到无效的 program counter |
| `hggcErrorLaunchFailure = 719` | 设备在执行核函数时发生异常 |
| `hggcErrorCooperativeLaunchTooLarge = 720` | cooperative 启动的线程块数超过上限（hggcOccupancyMaxActiveBlocksPerMultiprocessor × hggcDevAttrMultiProcessorCount） |
| `hggcErrorTensorMemoryLeak = 721` | 退出使用 tensor memory 的核函数时 tensor memory 未完全释放；进程进入不一致状态，必须终止重启 |
| `hggcErrorNotPermitted = 800` | 尝试的操作不被允许 |
| `hggcErrorNotSupported = 801` | 尝试的操作在当前系统或设备上不受支持 |
| `hggcErrorSystemNotReady = 802` | 系统尚未准备好开始 HGGC 工作（确认系统配置有效且所需驱动 daemon 在运行） |
| `hggcErrorSystemDriverMismatch = 803` | display 驱动与 HGGC 驱动版本不匹配 |
| `hggcErrorCompatNotSupportedOnDevice = 804` | 系统已升级支持 forward compatibility，但检测到的可见硬件不支持；可通过 HGGC_VISIBLE_DEVICES 仅暴露受支持硬件 |
| `hggcErrorMpsConnectionFailed = 805` | MPS client 无法连接到 MPS control daemon 或 MPS server |
| `hggcErrorMpsRpcFailure = 806` | MPS server 与 client 之间的 RPC 失败 |
| `hggcErrorMpsServerNotReady = 807` | MPS server 尚未准备好接收新 client（可能正在从致命故障恢复） |
| `hggcErrorMpsMaxClientsReached = 808` | 创建 MPS client 所需的硬件资源已耗尽 |
| `hggcErrorMpsMaxConnectionsReached = 809` | 设备连接所需的硬件资源已耗尽 |
| `hggcErrorMpsClientTerminated = 810` | MPS client 已被 server 终止，必须终止进程并重启 |
| `hggcErrorCdpNotSupported = 811` | 程序使用 HGGC Dynamic Parallelism，但当前配置（如 MPS）不支持 |
| `hggcErrorCdpVersionMismatch = 812` | 程序包含不同版本 Dynamic Parallelism 之间不受支持的交互 |
| `hggcErrorStreamCaptureUnsupported = 900` | 流正在 capturing 时不允许执行该操作 |
| `hggcErrorStreamCaptureInvalidated = 901` | 由于先前的错误，该流上的当前 capture sequence 已作废 |
| `hggcErrorStreamCaptureMerge = 902` | 该操作将导致合并两个独立的 capture sequence |
| `hggcErrorStreamCaptureUnmatched = 903` | capture 不是在该流中发起的 |
| `hggcErrorStreamCaptureUnjoined = 904` | capture sequence 包含一个未 join 到主流的 fork |
| `hggcErrorStreamCaptureIsolation = 905` | 将创建跨越 capture sequence 边界的依赖关系（只有隐式 in-流顺序依赖允许跨越） |
| `hggcErrorStreamCaptureImplicit = 906` | 该操作将导致从 hggcStreamLegacy 对当前 capture sequence 产生不允许的隐式依赖 |
| `hggcErrorCapturedEvent = 907` | 不允许对最后记录于 capturing 流的 event 执行该操作 |
| `hggcErrorStreamCaptureWrongThread = 908` | 未以 hggcStreamCaptureModeRelaxed 发起的 capture sequence 在不同线程中传给 hggcStreamEndCapture |
| `hggcErrorTimeout = 909` | wait 操作已超时 |
| `hggcErrorGraphExecUpdateFailure = 910` | 未执行图 update，因包含违反 instantiated 图 update 约束的更改 |
| `hggcErrorExternalDevice = 911` | PPU 之外的设备发生错误（异步错误会使进程进入不一致状态，必须终止重启） |
| `hggcErrorInvalidClusterSize = 912` | cluster 配置错误导致核函数启动出错 |
| `hggcErrorFunctionNotLoaded = 913` | 调用需要已加载函数的 API 时 function handle 尚未加载 |
| `hggcErrorInvalidResourceType = 914` | 传入的资源类型对该操作无效 |
| `hggcErrorInvalidResourceConfiguration = 915` | 资源对该操作不足或不适用 |
| `hggcErrorStreamDetached = 917` | 流处于 detached 状态（如关联的 green 上下文已销毁） |
| `hggcErrorUnknown = 999` | 未知的内部错误 |

**`enum hggcExternalMemoryHandleType`**——外部内存句柄类型：`hggcExternalMemoryHandleTypeOpaqueFd = 1`、`OpaqueWin32 = 2`、`OpaqueWin32Kmt = 3`、`D3D12Heap = 4`、`D3D12Resource = 5`、`D3D11Resource = 6`、`D3D11ResourceKmt = 7`、`HgSciBuf = 8`。

**`enum hggcExternalSemaphoreHandleType`**——外部信号量句柄类型：`hggcExternalSemaphoreHandleTypeOpaqueFd = 1`、`OpaqueWin32 = 2`、`OpaqueWin32Kmt = 3`、`D3D12Fence = 4`、`D3D11Fence = 5`、`HgSciSync = 6`、`KeyedMutex = 7`、`KeyedMutexKmt = 8`、`TimelineSemaphoreFd = 9`、`TimelineSemaphoreWin32 = 10`。

**`enum hggcFlushGPUDirectRDMAWritesOptions`**——`hggcDevAttrGPUDirectRDMAFlushWritesOptions` 的位掩码选项：`hggcFlushGPUDirectRDMAWritesOptionHost = 1`（刷新可由主机发起）、`hggcFlushGPUDirectRDMAWritesOptionMemOps = 4`（刷新可由内存操作发起）。

**`enum hggcFlushGPUDirectRDMAWritesScope`**——GPUDirect RDMA writes 的作用域：`hggcFlushGPUDirectRDMAWritesToOwner = 100`（刷新到所有者）、`hggcFlushGPUDirectRDMAWritesToAllDevices = 200`（刷新到所有设备）。

**`enum hggcFlushGPUDirectRDMAWritesTarget`**——GPUDirect RDMA writes 的目标：`hggcFlushGPUDirectRDMAWritesTargetCurrentDevice`（当前设备）。

**`enum hggcFuncAttribute`**——函数属性（供 `hggcFuncSetAttribute`）：

- `hggcFuncAttributeMaxDynamicSharedSizeBytes = 8` — 最大动态共享内存大小
- `hggcFuncAttributePreferredSharedMemoryCarveout = 9` — 首选共享内存 carveout
- `hggcFuncAttributeClusterSizeMustBeSet = 10` — cluster size 必须设置
- `hggcFuncAttributeRequiredClusterWidth = 11` / `RequiredClusterHeight = 12` / `RequiredClusterDepth = 13` — 必需的 cluster 宽度/高度/深度
- `hggcFuncAttributeNonPortableClusterSizeAllowed = 14` — 是否支持非便携式集群调度策略
- `hggcFuncAttributeClusterSchedulingPolicyPreference = 15` — 所需集群调度策略优先级
- `hggcFuncAttributeDispatchStrategy = 128` — 调度策略
- `hggcFuncAttributeBlockAgeEn = 129` — 调度扭曲时阻塞 age 优先级
- `hggcFuncAttributeDispatchMask = 130` — 调度掩码

**`enum hggcFuncCache`**——函数缓存配置：

- `hggcFuncCachePreferNone = 0` — 无偏好
- `hggcFuncCachePreferShared = 1` — 首选更大的 shared memory 和相近的 L1 cache
- `hggcFuncCachePreferL1 = 2` — 首选更大的 L1 cache 和相近的 shared memory
- `hggcFuncCachePreferEqual = 3` — 首选大小相等的 L1 cache 和 shared memory

**`enum hggcGPUDirectRDMAWritesOrdering`**——GPUDirect RDMA writes 的顺序保证：`hggcGPUDirectRDMAWritesOrderingNone = 0`（不支持原生排序）、`OrderingOwner = 100`（设备可以 GPUDirect RDMA 写入）、`OrderingAllDevices = 200`（系统中任何 HGGC 设备都可以对此设备 GPUDirect RDMA 写入）。

**`enum hggcGetDriverEntryPointFlags`**——获取驱动入口点的标志：`hggcGetDriverEntryPointDefault = 0`（默认行为）、`hggcGetDriverEntryPointLegacy = 1`（仅 legacy 入口点）、`hggcGetDriverEntryPointPerThreadDefaultStream = 2`（每线程默认流入口点）。

**`enum hggcGraphChildGraphNodeOwnership`**——图子图节点所有权：`hggcGraphChildGraphOwnershipClone = 0`（克隆子图）、`hggcGraphChildGraphOwnershipMove = 1`（移动子图所有权）。

**`enum hggcGraphConditionalNodeType`**——条件图节点类型：`hggcGraphCondTypeIf = 0`（if/else 节点）、`hggcGraphCondTypeWhile = 1`（while 节点）、`hggcGraphCondTypeSwitch = 2`（switch 节点）。

**`enum hggcGraphDebugDotFlags`**——图调试 dot 标志：`hggcGraphDebugDotFlagsVerbose = 1`（详细输出）、`KernelNodeParams = (1<<2)`、`MemcpyNodeParams = (1<<3)`、`MemsetNodeParams = (1<<4)`、`HostNodeParams = (1<<5)`、`EventNodeParams = (1<<6)`、`ExtSemasSignalNodeParams = (1<<7)`、`ExtSemasWaitNodeParams = (1<<8)`、`KernelNodeAttributes = (1<<9)`、`Handles = (1<<10)`（添加节点句柄）、`ConditionalNodeParams = (1<<15)`。

**`enum hggcGraphDependencyType`**——图依赖类型：`hggcGraphDependencyTypeDefault = 0`（默认依赖）、`hggcGraphDependencyTypeProgrammatic = 1`（Programmatic 依赖）。

**`enum hggcGraphExecUpdateResult`**——图可执行更新结果：`hggcGraphExecUpdateSuccess = 0`（更新成功）、`Error = 1`（更新失败）、`ErrorTopologyChanged = 2`（拓扑结构改变）、`ErrorNodeTypeChanged = 3`（节点类型改变）、`ErrorFunctionChanged = 4`（函数改变）、`ErrorParametersChanged = 5`（参数改变）、`ErrorNotSupported = 6`（不支持的更新）、`ErrorUnsupportedFunctionChange = 7`（不支持的核函数节点功能更改）、`ErrorAttributesChanged = 8`（不支持的节点属性更改）。

**`enum hggcGraphInstantiateFlags`**——图实例化标志：`hggcGraphInstantiateFlagAutoFreeOnLaunch = 1`（启动时自动释放）、`Upload = 2`（上传图）、`DeviceLaunch = 4`（可从设备侧启动）、`UseNodePriority = 8`（使用节点优先级）。

**`enum hggcGraphInstantiateResult`**——图实例化结果：`hggcGraphInstantiateSuccess = 0`（成功）、`Error = 1`（意外原因失败）、`InvalidStructure = 2`（结构无效，例如存在环）、`NodeOperationNotSupported = 3`（用于设备启动的实例化失败，节点操作不受支持）、`MultipleDevicesNotSupported = 4`（用于设备启动的实例化失败，节点属于不同的上下文）、`ConditionalHandleUnused = 5`（一个或多个 conditional handle 未与 conditional 节点关联）。

**`enum hggcGraphKernelNodeField`**——设备侧多节点更新时要更新的字段：`hggcGraphKernelNodeFieldInvalid = 0`（无效字段）、`GridDim`（网格维度更新）、`Param`（核函数参数更新）、`Enabled`（节点启用/禁用）。

**`enum hggcGraphMemAttributeType`**——图内存属性：`hggcGraphMemAttrUsedMemCurrent = 0x0`（hguint64_t，当前与图关联的内存量，字节）、`UsedMemHigh = 0x1`（自上次重置以来的高水位）、`ReservedMemCurrent = 0x2`（当前为图异步分配器预留的内存量）、`ReservedMemHigh = 0x3`（预留内存高水位）。

**`enum hggcGraphNodeType`**——图节点类型：`hggcGraphNodeTypeKernel = 0x00`（核函数节点）、`Memcpy = 0x01`、`Memset = 0x02`、`Host = 0x03`（Host 可执行节点）、`Graph = 0x04`（嵌入式图节点）、`Empty = 0x05`（空 no-op 节点）、`WaitEvent = 0x06`（外部 event wait 节点）、`EventRecord = 0x07`（外部 event record 节点）、`ExtSemaphoreSignal = 0x08`、`ExtSemaphoreWait = 0x09`、`MemAlloc = 0x0a`（内存分配节点）、`MemFree = 0x0b`（内存释放节点）、`Conditional = 0x0d`、`hggcGraphNodeTypeCount`。

**`enum hggcJitOption`**——在线编译器与链接器选项：`hggcJitMaxRegisters = 0`（线程可使用的最大寄存器数量）、`hggcJitThreadsPerBlock = 1`（每线程块最小线程数）、`hggcJitWallTime = 2`（编译器与链接器总墙钟时间，毫秒）、`hggcJitInfoLogBuffer = 3`（信息日志缓冲区指针）、`hggcJitInfoLogBufferSizeBytes = 4`（日志缓冲区大小）、`hggcJitErrorLogBuffer = 5`（错误日志缓冲区指针）、`hggcJitErrorLogBufferSizeBytes = 6`、`hggcJitOptimizationLevel = 7`（优化级别 0–4）、`hggcJitFallbackStrategy = 10`（回退策略）、`hggcJitGenerateDebugInfo = 11`（生成调试信息）、`hggcJitLogVerbose = 12`（详细日志）、`hggcJitGenerateLineInfo = 13`（行号信息）、`hggcJitCacheMode = 14`（缓存模式）、`hggcJitPositionIndependentCode = 30`（位置无关代码）、`hggcJitMinCtaPerSm = 31`（每个 SM 的最小 CTA 数）、`hggcJitMaxThreadsPerBlock = 32`（每线程块最大线程数）、`hggcJitOverrideDirectiveValues = 33`（覆盖 TIX 指令值）。

**`enum hggcJit_CacheMode`**——dlcm 的缓存模式：`hggcJitCacheOptionNone = 0`（不指定 -dlcm 标志）。

**`enum hggcJit_Fallback`**——hgbin 匹配回退策略：`hggcJitCacheOptionNone = 0`（编译时未指定 -dlem 标志）、`hggcJitCacheOptionCG`（编译时禁用 L1 缓存）、`hggcJitCacheOptionCA`（编译时启用 L1 缓存）。

**`enum hggcLaunchAttributeID`**——启动 attribute 枚举：`hggcLaunchAttributeIgnore = 0`（忽略条目）、`AccessPolicyWindow = 1`（访问策略窗口）、`Cooperative = 2`（Cooperative 启动）、`SynchronizationPolicy = 3`（同步策略）、`ClusterDimension = 4`（Cluster 维度）、`ClusterSchedulingPolicyPreference = 5`、`ProgrammaticStreamSerialization = 6`（Programmatic 流有序序列化）、`ProgrammaticEvent = 7`、`Priority = 8`（优先级）、`MemSyncDomainMap = 9`（内存同步域映射）、`MemSyncDomain = 10`（内存同步域）、`PreferredClusterDimension = 11`（首选 cluster 维度）、`LaunchCompletionEvent = 12`、`DeviceUpdatableKernelNode = 13`（设备可更新核函数节点）、`PreferredSharedMemoryCarveout = 14`（首选共享内存 carveout）、`IcnlinkUtilCentricScheduling = 16`（ICNlink 利用率中心调度）。

**`enum hggcLaunchMemSyncDomain`**——内存同步域：`hggcLaunchMemSyncDomainDefault = 0`（默认域）、`hggcLaunchMemSyncDomainRemote = 1`（remote 域）。

**`enum hggcLimit`**——HGGC 限制：`hggcLimitStackSize = 0x00`（PPU 线程栈大小）、`hggcLimitPrintfFifoSize = 0x01`（PPU printf FIFO 大小）、`hggcLimitMallocHeapSize = 0x02`（PPU malloc heap 大小）、`hggcLimitDevRuntimeSyncDepth = 0x03`（设备运行时同步深度）、`hggcLimitDevRuntimePendingLaunchCount = 0x04`（设备运行时待处理启动数）、`hggcLimitMaxL2FetchGranularity = 0x05`（L2 最大 fetch granularity）、`hggcLimitPersistingL2CacheSize = 0x06`（L2 persisting lines cache 大小）。

**`enum hggcMemAccessFlags`**——映射时使用的内存保护标志：`hggcMemAccessFlagsProtNone = 0`（默认：地址范围不可访问）、`ProtRead = 1`（可读）、`ProtReadWrite = 3`（可读写）。

**`enum hggcMemAllocationHandleType`**——句柄类型标志：`hggcMemHandleTypeNone = 0x0`（不允许任何导出机制）、`PosixFileDescriptor = 0x1`（允许文件描述符导出）、`Win32 = 0x2`（允许 Win32 NT handle 导出）、`Win32Kmt = 0x4`、`Fabric = 0x8`（允许 fabric handle 导出）。

**`enum hggcMemAllocationType`**——分配类型：`hggcMemAllocationTypeInvalid = 0x0`、`hggcMemAllocationTypePinned = 0x1`（pinned 分配）、`hggcMemAllocationTypeMax = 0x7FFFFFFF`。（v3 另新增 `hggcMemAllocationTypeManaged = 0x2`，见版本差异节。）

**`enum hggcMemLocationType`**——location 类型：`hggcMemLocationTypeInvalid = 0`、`hggcMemLocationTypeNone = 0`（location 未指定）、`Device = 1`（设备）、`Host = 2`（host）、`HostNuma = 3`（host NUMA 节点）、`HostNumaCurrent = 4`（距当前线程 CPU 最近的 host NUMA 节点）。

**`enum hggcMemPoolAttr`**——内存池属性：`hggcMemPoolReuseFollowEventDependencies = 0x1`（允许复用异步释放的内存）、`ReuseAllowOpportunistic = 0x2`（允许机会主义复用）、`ReuseAllowInternalDependencies = 0x3`（允许插入新的流依赖）、`hggcMemPoolAttrReleaseThreshold = 0x4`（释放阈值，字节）、`ReservedMemCurrent = 0x5`（当前预留内存量）、`ReservedMemHigh = 0x6`（预留内存高水位）、`UsedMemCurrent = 0x7`（当前使用内存量）、`UsedMemHigh = 0x8`（使用内存高水位）。

**`enum hggcMemRangeAttribute`**——范围属性：`hggcMemRangeAttributeReadMostly = 1`（该范围是否主要读取）、`PreferredLocation = 2`（首选 location）、`AccessedBy = 3`（已为指定设备设置）、`LastPrefetchLocation = 4`（最近一次 prefetch 的 location）、`PreferredLocationType = 5`、`PreferredLocationId = 6`、`LastPrefetchLocationType = 7`、`LastPrefetchLocationId = 8`。

**`enum hggcMemcpy3DOperandType`**——3D memcpy 操作数类型：`hggcMemcpyOperandTypePointer = 0x1`（操作数为有效指针）、`hggcMemcpyOperandTypeArray = 0x2`（操作数为 HGarray）、`hggcMemcpyOperandTypeMax = 0x7FFFFFFF`。

**`enum hggcMemcpyFlags`**——批内拷贝标志：`hggcMemcpyFlagDefault = 0x0`、`hggcMemcpyFlagPreferOverlapWithCompute = 0x1`（尝试将拷贝与计算工作 overlap）。

**`enum hggcMemcpyKind`**——内存拷贝类型：`hggcMemcpyHostToHost = 0`、`hggcMemcpyHostToDevice = 1`、`hggcMemcpyDeviceToHost = 2`、`hggcMemcpyDeviceToDevice = 3`、`hggcMemcpyDefault = 4`（从指针值推断方向）。

**`enum hggcMemcpySrcAccessOrder`**——memcpy 对源操作数的访问顺序约束：`hggcMemcpySrcAccessOrderInvalid = 0`（默认无效）、`Stream = 1`（必须按流顺序）、`DuringApiCall = 2`（访问可能超出流顺序，但必须在 API 调用返回前完成）、`Any = 3`（访问可在 API 调用返回后发生）、`Max = 0x7FFFFFFF`。

**`enum hggcMemoryAdvise`**——Memory Advise 取值：`hggcMemAdviseSetReadMostly = 1`（数据将主要被读取）、`UnsetReadMostly = 2`（撤销）、`SetPreferredLocation = 3`、`UnsetPreferredLocation = 4`、`SetAccessedBy = 5`（数据将被指定设备访问）、`UnsetAccessedBy = 6`（让 UM 子系统决定 page fault 策略）。

**`enum hggcMemoryType`**——内存类型：`hggcMemoryTypeUnregistered = 0`（未注册内存）、`Host = 1`（主机内存）、`Device = 2`（设备内存）、`Managed = 3`。

**`enum hggcSharedCarveout`**——共享内存 carveout 设置：`hggcSharedmemCarveoutDefault = -1`（默认）、`MaxShared = 100`（最大共享内存）、`MaxL1 = 0`（最大 L1 缓存）。

**`enum hggcSharedMemConfig`**——共享内存配置：`hggcSharedMemBankSizeDefault = 0`（默认 bank size）、`FourByte = 1`（4 字节）、`EightByte = 2`（8 字节）。

**`enum hggcStreamCaptureMode`**——流 capture 模式：`hggcStreamCaptureModeGlobal = 0`（全局）、`ThreadLocal = 1`（线程局部）、`Relaxed = 2`（宽松）。

**`enum hggcStreamCaptureStatus`**——流 capture 状态：`hggcStreamCaptureStatusNone = 0`（未 capture）、`Active = 1`（正在 capture）、`Invalidated = 2`（capture 已失效）。

**`enum hggcStreamUpdateCaptureDependenciesFlags`**——流更新 capture 依赖标志：`hggcStreamAddCaptureDependencies = 0`（添加依赖）、`hggcStreamSetCaptureDependencies = 1`（设置依赖）。

**`enum hggcUserObjectFlags`**——用户对象标志：`hggcUserObjectNoDestructorSync = 0x1`（析构函数执行不受任何 HGGC handle 同步）。

**`enum hggcUserObjectRetainFlags`**——用户对象保留标志：`hggcGraphUserObjectMove = 0x1`（从调用方转移引用，而非创建新引用）。

### 实用工具

本模块提供**错误处理、版本查询与驱动入口点访问**接口。

| 函数 | 用途 |
|------|------|
| `hggcGetErrorName` | 取错误码对应的枚举名（例如 `hggcErrorInvalidValue`） |
| `hggcGetErrorString` | 取错误码对应的人类可读描述 |
| `hggcGetLastError` | 读取并清空当前线程的最近错误 |
| `hggcPeekAtLastError` | 仅读取，不清空 |
| `hggcDriverGetVersion` | 返回驱动所支持的最新 HGGC 版本 |
| `hggcRuntimeGetVersion` | 返回 HGGC 运行时版本 |
| `hggcGetDriverEntryPoint` | 返回所请求的驱动 API 函数指针 |
| `hggcGetDriverEntryPointByVersion` | 按 HGGC 版本返回所请求的驱动 API 函数指针 |

#### hggcGetErrorName

```c
const char* hggcGetErrorName ( hggcError_t error )
```

把错误码转换为对应枚举常量的文本名称。返回以 NUL 结尾的 C 字符串；无法识别的错误码返回 `"unrecognized error code"`。返回字符串由 HGGC 运行时静态持有，调用方不应释放或修改；与 `hggcError_t` 枚举标识符严格对应，适合日志输出与跨语言桥接。取人类可读描述用 `hggcGetErrorString`，获取错误码本身用 `hggcGetLastError` / `hggcPeekAtLastError`。

#### hggcGetErrorString

```c
const char* hggcGetErrorString ( hggcError_t error )
```

把错误码转换为简短的人类可读说明。返回以 NUL 结尾的 C 字符串（静态持有）；无法识别的错误码返回 `"unrecognized error code"`。需要稳定的机器可解析标识符时用 `hggcGetErrorName`。

#### hggcGetLastError

```c
hggcError_t hggcGetLastError ( void )
```

返回当前线程上 HGGC 运行时实例最近一次产生的错误码，并把内部错误槽重置为 `hggcSuccess`。返回值为 `hggcError_t` 全量错误码集合（见数据类型节 `enum hggcError`），按类别归纳：

| 类别 | 典型错误码 |
|---|---|
| 成功 | `hggcSuccess` |
| 配置/参数类 | `hggcErrorMissingConfiguration`、`hggcErrorInvalidConfiguration`、`hggcErrorInvalidValue`、`hggcErrorInvalidPitchValue`、`hggcErrorInvalidSymbol`、`hggcErrorInvalidNormSetting`、`hggcErrorInvalidFilterSetting` |
| 设备/初始化类 | `hggcErrorInitializationError`、`hggcErrorInsufficientDriver`、`hggcErrorNoDevice`、`hggcErrorInvalidDevice`、`hggcErrorSetOnActiveProcess`、`hggcErrorStartupFailure` |
| 内存类 | `hggcErrorMemoryAllocation`、`hggcErrorInvalidDevicePointer`、`hggcErrorUnmapBufferObjectFailed` |
| 启动/执行类 | `hggcErrorLaunchFailure`、`hggcErrorLaunchTimeout`、`hggcErrorLaunchOutOfResources`、`hggcErrorInvalidDeviceFunction` |
| 资源/句柄类 | `hggcErrorInvalidResourceHandle`、`hggcErrorInvalidTexture`、`hggcErrorInvalidTextureBinding`、`hggcErrorInvalidChannelDescriptor`、`hggcErrorInvalidMemcpyDirection` |
| 二进制/JIT 类 | `hggcErrorInvalidTix`、`hggcErrorUnsupportedTixVersion`、`hggcErrorNoKernelImageForDevice`、`hggcErrorJitCompilerNotFound`、`hggcErrorJitCompilationDisabled` |
| 未知/其他 | `hggcErrorUnknown` |

行为说明：

- 调用本接口会**清空**当前线程的最近错误槽。下一次 `hggcGetLastError` 在没有新错误的前提下将返回 `hggcSuccess`。
- 静态链接 HGGC 运行时的二进制可能在同一进程内存在多个运行时实例；每个实例各自维护错误槽。
- 异步启动失败的错误码会在后续某次同步点上被本接口取出，因此本接口可能返回早先异步操作产生的错误。
- 若调用时运行时尚未初始化，可能返回 `hggcErrorInitializationError`、`hggcErrorInsufficientDriver` 或 `hggcErrorNoDevice`。
- HGGC 流回调（见 `hggcStreamAddCallback`）内禁止调用任何 HGGC 接口；若违反，本接口可能（但不保证）返回 `hggcErrorNotPermitted` 作为诊断。

需要保留错误状态以供后续多次读取时，改用 `hggcPeekAtLastError`。

#### hggcPeekAtLastError

```c
hggcError_t hggcPeekAtLastError ( void )
```

返回当前线程最近一次产生的错误码，**不**重置内部错误槽——同一错误可被多次读取。其他注意事项（多实例、异步错误延迟、流回调内禁用、运行时未初始化等）与 `hggcGetLastError` 一致。

#### hggcDriverGetVersion

通过 `driverVersion` 返回驱动所支持的最新 HGGC 版本，格式为 `(1000 × 主版本号 + 10 × 次版本号)`。未安装驱动时返回 0。`driverVersion` 为 NULL 时返回 `hggcErrorInvalidValue`。

```c
__host__ hggcError_t hggcDriverGetVersion (int* driverVersion)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| driverVersion | out | 用于返回 HGGC 驱动版本 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcRuntimeGetVersion

通过 `runtimeVersion` 返回当前 HGGC 运行时实例的版本号，格式同上。该 API 仅返回一个编译期常量，用于以上述格式表示 SAIL 工具包版本。`runtimeVersion` 为 NULL 时返回 `hggcErrorInvalidValue`。

```c
__host__ __device__ hggcError_t hggcRuntimeGetVersion (int* runtimeVersion)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| runtimeVersion | out | 用于返回 HGGC 运行时版本 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGetDriverEntryPoint

将所请求 `flags` 对应的 HGGC 驱动函数地址返回到 `**funcPtr` 中。对于所请求的驱动符号，如果该驱动符号首次引入时的 HGGC 版本小于或等于 HGGC 运行时版本，则返回指向相应带版本号驱动函数的函数指针。返回的指针应 cast 为与所请求驱动函数在 API 头文件中的定义相匹配的函数指针类型；函数指针 typedef 在对应的 typedefs 头文件中（例如 `hggcTypedefs.h` 包含在 `hggc.h` 中定义的驱动 API 的函数指针 typedef）。如果所请求的驱动函数有效且平台支持，返回 `hggcSuccess` 并设置 `funcPtr`；如果平台不支持、不存在 ABI 兼容的驱动函数、或驱动符号无效，返回 `hggcSuccess` 并将 `funcPtr` 设为 NULL。可选的 `driverStatus` 输出 `hggcDriverEntryPointQueryResult`：

- `hggcDriverEntryPointSuccess` — 已成功找到所请求符号，且 `pfn` 有效
- `hggcDriverEntryPointSymbolNotFound` — 未找到所请求符号
- `hggcDriverEntryPointVersionNotSufficent` — 已找到符号，但当前运行时版本（`HGGC_VERSION`）不支持

可选的 `flags`：

- `hggcEnableDefault`：默认模式。编译时使用 `--default-stream per-thread` 或定义了 `HGGC_API_PER_THREAD_DEFAULT_STREAM` 时等价于 `hggcEnablePerThreadDefaultStream`，否则等价于 `hggcEnableLegacyStream`。
- `hggcEnableLegacyStream`：查找所有与所请求驱动符号名匹配的驱动符号，但不包括对应的 per-thread 版本。
- `hggcEnablePerThreadDefaultStream`：查找包括 per-thread 版本在内的匹配符号；未找到 per-thread 版本时返回 legacy 版本。该 API 已废弃，应改用 `hggcGetDriverEntryPointByVersion`。

```c
hggcError_t hggcGetDriverEntryPoint (const char* symbol,
                                     void** funcPtr,
                                     unsigned long long flags,
                                     hggcDriverEntryPointQueryResult* driverStatus = NULL)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| symbol | out | 要查找的驱动 API 函数基名。例如对 `hgMemAlloc_v2`，`symbol` 应为 `"hgMemAlloc"`；API 会根据运行时版本返回 ABI 兼容的最新驱动符号地址（`hgMemAlloc` 或 `hgMemAlloc_v2`） |
| funcPtr | out | 用于返回所请求驱动函数指针的位置 |
| flags | in | 搜索选项标志 |
| driverStatus | in | 可选：保存符号查找状态，取值见 `hggcDriverEntryPointQueryResult` |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorNotSupported

#### hggcGetDriverEntryPointByVersion

将所请求 `flags` 与 HGGC 驱动版本对应的驱动函数地址返回到 `**funcPtr` 中。HGGC 版本以 `(1000 × major + 10 × minor)` 指定。指定的 HGGC 版本大于或等于符号首次引入版本时返回相应带版本号函数的指针；指定的 HGGC 版本大于驱动版本时返回 `hggcErrorInvalidValue`。指针应 cast 为匹配所请求驱动函数定义的函数指针类型；typedef 在对应 typedefs 头文件中（如 `hggcTypedefs.h`）。当请求的 HGGC 版本高于已安装 Toolkit 版本时，头文件中可能没有合适的 typedef，此时需从更高版本 toolkit 获取或自定义函数 typedef。平台不支持/无 ABI 兼容函数/符号无效时返回 `hggcSuccess` 且 `funcPtr` 为 NULL。`driverStatus` 与 `flags` 语义同 `hggcGetDriverEntryPoint`（其中 per-thread 标志未废弃）。

```c
hggcError_t hggcGetDriverEntryPointByVersion (const char* symbol,
                                              void** funcPtr,
                                              unsigned int hggcVersion,
                                              unsigned long long flags,
                                              hggcDriverEntryPointQueryResult* driverStatus = NULL)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| symbol | in | 要查找的驱动 API 函数基名（如 `"hgMemAlloc"`） |
| funcPtr | out | 用于返回所请求驱动函数指针的位置 |
| hggcVersion | in | 用于查找所请求驱动符号的 HGGC 版本 |
| flags | in | 搜索选项标志 |
| driverStatus | in | 可选：保存符号查找状态 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorNotSupported

## 设备与上下文

本节涵盖设备发现与属性查询，以及对等设备间的直接内存访问。

### 设备管理

本模块提供**设备枚举、属性查询与运行时配置**接口。应用通过它发现可用设备、获取设备能力（计算能力版本、显存大小、多处理器数等）、选择目标设备并设定缓存策略。它是所有 HGGC 程序的起始入口——在分配内存或启动核函数之前，必须先通过本模块确认硬件环境。

| 函数 | 用途 |
|------|------|
| `hggcChooseDevice` | 选择最符合指定条件的计算设备 |
| `hggcCtxResetPersistingL2Cache` | 将缓存中的所有持久化行重置为正常状态 |
| `hggcDeviceGetAttribute` | 返回设备的属性信息 |
| `hggcDeviceGetByPCIBusId` | 根据 PCI 总线 ID 获取计算设备句柄 |
| `hggcDeviceGetCacheConfig` | 返回当前设备的首选缓存配置 |
| `hggcDeviceGetHostAtomicCapabilities` | 查询设备与主机之间支持的原子操作详情 |
| `hggcDeviceGetLimit` | 返回资源限制信息 |
| `hggcDeviceGetPCIBusId` | 返回设备的 PCI 总线 ID 字符串 |
| `hggcDeviceGetStreamPriorityRange` | 返回流优先级的数值范围（最低和最高优先级） |
| `hggcDeviceReset` | 销毁当前进程中当前设备上的所有资源分配并重置所有状态 |
| `hggcDeviceSetCacheConfig` | 设置当前设备的首选缓存配置 |
| `hggcDeviceSetLimit` | 设置资源限制 |
| `hggcDeviceSynchronize` | 阻塞等待，直到计算设备完成所有任务 |
| `hggcGetDevice` | 返回当前正在使用的设备编号 |
| `hggcGetDeviceCount` | 返回具备计算能力的设备总数 |
| `hggcGetDeviceFlags` | 获取当前设备的配置标志 |
| `hggcGetDeviceProperties` | 返回计算设备的详细属性信息 |
| `hggcSetDevice` | 设置用于 PPU 执行的当前设备 |
| `hggcSetDeviceFlags` | 设置设备执行的配置标志 |
| `hggcSetValidDevices` | 设置可用于 HGGC 运行的设备列表 |

#### hggcChooseDevice

在 `*device` 中返回属性最匹配 `*prop` 的设备编号。

```c
__host__ hggcError_t hggcChooseDevice (int* device, const hggcDeviceProp* prop)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| device | out | 指向返回的最佳匹配设备编号的指针 |
| prop | in | 期望的设备属性条件 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcCtxResetPersistingL2Cache

将缓存中的所有持久化行重置为正常状态。该效果在函数返回时生效。

```c
hggcError_t hggcCtxResetPersistingL2Cache (void)
```

错误码：hggcSuccess

#### hggcDeviceGetAttribute

在 `*value` 中返回设备 `device` 的属性 `attr` 对应的整数值。可查询的属性全集见数据类型节 `enum hggcDeviceAttr`。

```c
__host__ __device__ hggcError_t hggcDeviceGetAttribute (int* value,
                                                        hggcDeviceAttr attr,
                                                        int device)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| value | out | 指向返回的设备属性值的指针 |
| attr | in | 要查询的设备属性类型 |
| device | in | 要查询的设备编号 |

错误码：hggcSuccess、hggcErrorInvalidDevice、hggcErrorInvalidValue

#### hggcDeviceGetByPCIBusId

在 `*device` 中返回与给定 PCI 总线 ID 字符串对应的设备编号。

```c
__host__ hggcError_t hggcDeviceGetByPCIBusId (int* device, const char* pciBusId)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| device | out | 指向返回的设备编号的指针 |
| pciBusId | in | PCI 总线 ID 字符串，格式为 `[domain]:[bus]:[device].[function]`、`[domain]:[bus]:[device]` 或 `[bus]:[device].[function]` 之一，`domain`/`bus`/`device`/`function` 均为十六进制值 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidDevice

#### hggcDeviceGetCacheConfig

对于 L1 缓存和共享内存共用相同硬件资源的设备，通过 `pCacheConfig` 返回当前设备的首选缓存配置。这仅为偏好设置：运行时将尽可能使用请求的配置，但若执行函数需要，也可自由选择其他配置。对于 L1 缓存和共享内存大小固定的设备，返回 `hggcFuncCachePreferNone`。支持的配置：`hggcFuncCachePreferNone`（默认，无偏好）、`hggcFuncCachePreferShared`（偏好更大共享内存）、`hggcFuncCachePreferL1`（偏好更大 L1）、`hggcFuncCachePreferEqual`（偏好相等）。

```c
__host__ __device__ hggcError_t hggcDeviceGetCacheConfig (hggcFuncCache* pCacheConfig)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pCacheConfig | out | 指向返回的缓存配置的指针 |

错误码：hggcSuccess

#### hggcDeviceGetHostAtomicCapabilities

在 `*capabilities` 中返回 `device` 与主机之间链路上所请求原子 `*operations` 的详细信息。`*operations` 和 `*capabilities` 的分配大小必须为 `count`。对每个 `hggcAtomicOperation`，对应结果是一个位掩码，指示该链路原生支持哪些 `hggcAtomicOperationCapability`。`device` 无效返回 `hggcErrorInvalidDevice`；`*capabilities` 或 `*operations` 为 NULL、`count` 为 0、或任一操作无效，返回 `hggcErrorInvalidValue`。

```c
__host__ hggcError_t hggcDeviceGetHostAtomicCapabilities (unsigned int* capabilities,
                                                          const hggcAtomicOperation* operations,
                                                          unsigned int count,
                                                          int device)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| capabilities | out | 用于返回每个请求操作的能力详细信息 |
| operations | in | 请求的操作 |
| count | in | 请求的操作数和 `capabilities` 的大小 |
| device | in | 设备句柄 |

错误码：hggcSuccess、hggcErrorInvalidDevice、hggcErrorInvalidValue

#### hggcDeviceGetLimit

在 `*pValue` 中返回 `limit` 的当前大小。支持的 `hggcLimit` 值：

- `hggcLimitStackSize` — 每个 PPU 线程的栈大小（字节）。
- `hggcLimitPrintfFifoSize` — `printf()` 设备系统调用使用的共享 FIFO 大小（字节）。
- `hggcLimitMallocHeapSize` — `malloc()`/`free()` 设备系统调用使用的堆大小（字节）。
- `hggcLimitDevRuntimeSyncDepth` — 线程可发出设备运行时 `hggcDeviceSynchronize` 等待子网格启动完成的最大网格深度。计算能力 >= 9.0 的设备上已移除，返回 `hggcErrorUnsupportedLimit`。
- `hggcLimitDevRuntimePendingLaunchCount` — 未决的设备运行时启动的最大数量。
- `hggcLimitMaxL2FetchGranularity` — L2 缓存获取粒度。
- `hggcLimitPersistingL2CacheSize` — 持久化 L2 缓存大小（字节）。

```c
__host__ __device__ hggcError_t hggcDeviceGetLimit (size_t* pValue,
                                                    hggcLimit limit)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pValue | out | 用于返回的 `limit` 大小 |
| limit | in | 要查询的 `limit` |

错误码：hggcSuccess、hggcErrorUnsupportedLimit、hggcErrorInvalidValue

#### hggcDeviceGetPCIBusId

在 `pciBusId` 指向的以 NULL 结尾的字符串中返回标识设备 `device` 的 ASCII 字符串，`len` 指定最大长度。

```c
__host__ hggcError_t hggcDeviceGetPCIBusId (char* pciBusId, int len, int device)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pciBusId | out | 格式为 `[domain]:[bus]:[device].[function]` 的标识符字符串（十六进制）；`pciBusId` 应足够大以存储 13 个字符（含 NULL 终止符） |
| len | in | 字符串最大长度 |
| device | in | 要获取标识符字符串的设备 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidDevice

#### hggcDeviceGetStreamPriorityRange

在 `*leastPriority` 和 `*greatestPriority` 中分别返回最低和最高流优先级的数值。流优先级遵循数字越小优先级越高的惯例，有效范围为 `[*greatestPriority, *leastPriority]`。创建流时优先级超出该范围会自动被钳制到边界。不需要某值时可传 NULL。当前上下文设备不支持流优先级时两者都返回 0。创建优先级流见 `hggcStreamCreateWithPriority`。

```c
__host__ hggcError_t hggcDeviceGetStreamPriorityRange (int* leastPriority,
                                                       int* greatestPriority)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| leastPriority | out | 返回最低流优先级数值 |
| greatestPriority | out | 返回最高流优先级数值 |

错误码：hggcSuccess

#### hggcDeviceReset

显式销毁并清理与当前进程中当前设备关联的所有资源。调用者有责任确保后续 API 调用不再访问这些资源，否则行为未定义。资源包括 `hggcStream_t`、`hggcEvent_t`、`hggcArray_t`、`hggcMipmappedArray_t`、`hggcPitchedPtr`、`hggcExternalMemory_t`、`hggcExternalSemaphore_t`，以及由 `hggcMalloc`、`hggcMallocHost`、`hggcMallocManaged`、`hggcMallocPitch` 分配的内存。对此设备的任何后续 API 调用都将重新初始化该设备。此函数立即重置设备；调用者有责任确保调用时进程中任何其他主机线程都没有访问该设备。

```c
__host__ hggcError_t hggcDeviceReset (void)
```

错误码：hggcSuccess

#### hggcDeviceSetCacheConfig

在 L1 缓存和共享内存共用硬件资源的设备上，设置当前设备的首选缓存配置。仅为首选项，运行时可按执行需要自由选择其他配置。通过 `hggcFuncSetCacheConfig` 设置的函数级偏好优先于此设备范围设置。设为 `hggcFuncCachePreferNone` 时后续核函数启动不更改缓存配置（除非核函数需要）。L1/共享内存大小固定的设备上此设置无效。使用与最近一次偏好不同的偏好启动核函数可能插入设备端同步点。支持的配置同 `hggcDeviceGetCacheConfig`。

```c
__host__ hggcError_t hggcDeviceSetCacheConfig (hggcFuncCache cacheConfig)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| cacheConfig | in | 请求的缓存配置 |

错误码：hggcSuccess

#### hggcDeviceSetLimit

请求将 `limit` 设置为 `value`。驱动可自由修改请求值以满足硬件要求（钳制到最小/最大值、向上舍入到元素大小等）；用 `hggcDeviceGetLimit` 查询实际生效值。各限制说明：

- `hggcLimitStackSize` — 控制每个 PPU 线程的栈大小（字节）。
- `hggcLimitPrintfFifoSize` — 控制 `printf()` 设备系统调用的共享 FIFO 大小（字节）。不得在启动任何使用 `printf()` 的核函数之后设置，否则返回 `hggcErrorInvalidValue`。
- `hggcLimitMallocHeapSize` — 控制 `malloc()`/`free()` 设备系统调用的堆大小（字节）。不得在启动任何使用 `malloc()`/`free()` 的核函数之后设置，否则返回 `hggcErrorInvalidValue`。
- `hggcLimitDevRuntimeSyncDepth` — 控制线程可安全调用 `hggcDeviceSynchronize` 的最大网格嵌套深度。必须在启动任何在高于默认同步深度（两级网格）调用 `hggcDeviceSynchronize` 的设备运行时核函数之前设置；违反时同步调用失败并返回 `hggcErrorSyncDepthExceeded`。可设为小于默认值，最高为最大启动深度 24。额外的同步深度级别需要运行时预留大量设备内存（不可用于用户分配）；预留失败时返回 `hggcErrorMemoryAllocation`，限制可重置为较低值。仅适用于计算能力 < 9.0 的设备，其他设备返回 `hggcErrorUnsupportedLimit`。
- `hggcLimitDevRuntimePendingLaunchCount` — 控制当前设备未决设备运行时启动的最大数量（网格从启动到已知完成为止都属未决）。违反时启动失败，随后 `hggcGetLastError` 返回 `hggcErrorLaunchPendingCountExceeded`。默认为 2048 次启动，可增加；同样需要预留设备内存，预留失败返回 `hggcErrorMemoryAllocation`。仅适用于计算能力 3.5 及以上，更低版本返回 `hggcErrorUnsupportedLimit`。
- `hggcLimitMaxL2FetchGranularity` — 控制 L2 缓存获取粒度，范围 0B–128B。纯性能提示，依平台可能被忽略或钳制。
- `hggcLimitPersistingL2CacheSize` — 控制可用于持久化 L2 缓存的大小（字节）。纯性能提示，依平台可能被忽略或钳制。

```c
__host__ hggcError_t hggcDeviceSetLimit (hggcLimit limit, size_t value)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| limit | in | 要设置的 `limit` |
| value | in | `limit` 的大小 |

错误码：hggcSuccess、hggcErrorUnsupportedLimit、hggcErrorInvalidValue、hggcErrorMemoryAllocation

#### hggcDeviceSynchronize

阻塞直到设备完成所有先前请求的任务。如果先前的任务之一失败，返回该错误。如果为此设备设置了 `hggcDeviceScheduleBlockingSync` 标志，主机线程将阻塞直到设备完成其工作。

```c
__host__ __device__ hggcError_t hggcDeviceSynchronize (void)
```

错误码：hggcSuccess、hggcErrorStreamCaptureUnsupported

#### hggcGetDevice

在 `*device` 中返回调用主机线程的当前设备。

```c
__host__ __device__ hggcError_t hggcGetDevice (int* device)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| device | out | 活动主机线程在其上执行设备代码的设备 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGetDeviceCount

在 `*count` 中返回计算能力大于或等于 2.0 且可用于执行的设备数量。

```c
__host__ __device__ hggcError_t hggcGetDeviceCount (int* count)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| count | out | 计算能力大于或等于 2.0 的设备数 |

错误码：hggcSuccess

#### hggcGetDeviceFlags

在 `flags` 中返回当前设备的标志。如果调用线程有当前设备，返回该设备的标志；否则返回第一个设备的标志（可能是默认标志）。通常返回的标志应匹配调用线程随后使用设备将看到的行为（前提是期间未改动标志或当前设备）。注意：设备未初始化时其他线程可能先改动其标志；使用独占模式时若此线程尚未请求特定设备，实际可能使用非第一个设备；若当前上下文由驱动 API 创建，则始终返回该上下文的标志。返回值可能明确包含 `hggcDeviceMapHost`（即使 `hggcSetDeviceFlags` 不接受它），因为该标志在运行时 API 中是隐式的，而驱动 API 创建的上下文中不是。

```c
__host__ hggcError_t hggcGetDeviceFlags (unsigned int* flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| flags | in | 用于存储设备标志的指针 |

错误码：hggcSuccess、hggcErrorInvalidDevice

#### hggcGetDeviceProperties

在 `*prop` 中返回设备 `device` 的属性（`hggcDeviceProp`，其成员字段见文末数据字段索引及版本差异节）。

```c
__host__ hggcError_t hggcGetDeviceProperties (hggcDeviceProp* prop, int device)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| prop | out | 用于返回指定设备的属性 |
| device | in | 要获取属性的设备编号 |

错误码：hggcSuccess、hggcErrorInvalidDevice

#### hggcSetDevice

将设备设置为调用主机线程的当前设备。有效设备 id 为 0 到 (`hggcGetDeviceCount` - 1)。随后此主机线程用 `hggcMalloc`、`hggcMallocPitch`、`hggcMallocArray` 分配的设备内存都物理驻留在该设备上；用 `hggcMallocHost`/`hggcHostAlloc`/`hggcHostRegister` 分配的主机内存生命周期与该设备关联；创建的流和事件与该设备关联；用 `<<<>>>` 或 `hggcLaunchKernel` 启动的核函数在该设备上执行。可从任何主机线程、在任何时间调用以连接到任何设备。此函数不与先前或新设备同步，仅在初始化运行时上下文状态时花费较多时间。此调用将指定设备的主上下文绑定到调用线程，所有后续内存分配、流/事件创建、核函数启动都与该主上下文关联，并立即初始化主上下文上的运行时状态、使其成为设备当前上下文。设备处于 `hggcComputeModeExclusiveProcess` 且被另一进程占用，或处于 `hggcComputeModeProhibited` 时，返回错误。

```c
__host__ hggcError_t hggcSetDevice (int device)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| device | in | 活动主机线程应在其上执行设备代码的设备 |

错误码：hggcSuccess、hggcErrorInvalidDevice

#### hggcSetDeviceFlags

将 `flags` 记录为当前设备的标志。若当前设备已设置且已初始化则覆盖先前标志；未初始化则用提供的标志初始化；无当前设备则选择默认设备并初始化。`flags` 的最低 3 个有效位控制等待设备结果时 CPU 线程与 OS 调度程序的交互：

- `hggcDeviceScheduleAuto` — 默认值（flags 为 0 时）：基于活动 HGGC 上下文数 C 与逻辑处理器数 P 启发式判断。C > P 时等待设备将让出给其他 OS 线程，否则主动自旋。
- `hggcDeviceScheduleSpin` — 等待设备结果时主动自旋。可降低等待延迟，但 CPU 线程并行工作时可能降低其性能。
- `hggcDeviceScheduleYield` — 等待时让出线程。可能增加等待延迟，但可提高并行 CPU 线程性能。
- `hggcDeviceScheduleBlockingSync` — 等待设备完成工作时将 CPU 线程阻塞在同步原语上。
- `hggcDeviceBlockingSync` — 同上，已由 `hggcDeviceScheduleBlockingSync` 替代。
- `hggcDeviceMapHost` — 启用对设备可访问的固定主机内存的分配。对运行时隐式，但驱动 API 创建的上下文中可能不存在。未设置时 `hggcHostGetDevicePointer` 将始终返回失败。
- `hggcDeviceLmemResizeToMax` — 为核函数调整本地内存后不减少本地内存，以防止频繁启动高本地内存核函数时的分配抖动（代价是内存占用增加）。**[已弃用]**：该行为现在是默认行为且无法禁用。
- `hggcDeviceSyncMemops` — 确保此上下文中启动的同步内存操作始终同步（见"API 同步行为"节）。

```c
__host__ hggcError_t hggcSetDeviceFlags (unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| flags | in | 设备操作的参数 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcSetValidDevices

使用 `device_arr` 按优先级顺序为 HGGC 执行设置设备列表，`len` 指定元素数。HGGC 按顺序尝试设备直到找到可正常工作的设备。未调用或 `len` 为 0 时恢复默认行为（按顺序尝试系统所有可用设备）。列表中设备 ID 不存在返回 `hggcErrorInvalidDevice`；`len` 非 0 而 `device_arr` 为 NULL，或 `len` 超过系统设备数，返回 `hggcErrorInvalidValue`。

```c
__host__ hggcError_t hggcSetValidDevices (int* device_arr, int len)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| device_arr | in | 要尝试的设备列表 |
| len | in | 列表中的设备数 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidDevice

比赛关联：`hggcDevAttrMultiProcessorCount`、`hggcDevAttrMaxSharedMemoryPerBlock(Optin)`、`hggcDevAttrL2CacheSize`、`hggcDevAttrMemoryPoolsSupported` 等属性是估算 batch 能力、KV cache 容量与占用率的第一手数据；`hggcSetDeviceFlags(hggcDeviceScheduleSpin)` 可降低同步等待延迟，对压 TTFT 有帮助。

### 对等设备内存访问

本模块提供**对等设备（Peer-to-Peer）内存访问**接口，可在多 PPU 环境中实现设备间直接内存互访、查询对等连接属性与原子操作支持情况。

| 函数 | 用途 |
|------|------|
| `hggcDeviceCanAccessPeer` | 查询某个设备是否可以直接访问对等设备的内存 |
| `hggcDeviceDisablePeerAccess` | 禁用对等设备上内存分配的直接访问 |
| `hggcDeviceEnablePeerAccess` | 启用对等设备上内存分配的直接访问 |
| `hggcDeviceGetP2PAttribute` | 查询两个设备之间连接链路的属性 |

#### hggcDeviceCanAccessPeer

如果设备能够直接访问 `peerDevice` 的内存，则在 `*canAccessPeer` 中返回 1，否则返回 0。如果可以直接访问，可调用 `hggcDeviceEnablePeerAccess()` 启用。

```c
hggcError_t hggcDeviceCanAccessPeer (int* canAccessPeer,
                                     int device,
                                     int peerDevice)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| canAccessPeer | out | 用于返回访问能力 |
| device | in | 要从该设备直接访问 `peerDevice` 上分配的内存 |
| peerDevice | in | 被直接访问的分配所在的设备 |

错误码：hggcSuccess、hggcErrorInvalidDevice

#### hggcDeviceDisablePeerAccess

如果尚未从当前设备启用对 `peerDevice` 内存的直接访问，则返回 `hggcErrorPeerAccessNotEnabled`。

```c
hggcError_t hggcDeviceDisablePeerAccess (int peerDevice)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| peerDevice | in | 要禁用直接访问的对等设备 |

错误码：hggcSuccess、hggcErrorPeerAccessNotEnabled、hggcErrorInvalidDevice

#### hggcDeviceEnablePeerAccess

成功时，`peerDevice` 上的所有分配立即可被当前设备访问，直到通过 `hggcDeviceDisablePeerAccess()` 显式禁用，或通过 `hggcDeviceReset()` 重置任一设备。

注意：该调用授予的访问是**单向**的——若要从 `peerDevice` 访问当前设备内存，需另行对称调用 `hggcDeviceEnablePeerAccess()`。

注意：存在设备级与系统级限制（详见 HGGC 编程指南的 P2P Memory Access 章节）。`hggcDeviceCanAccessPeer()` 表明不能访问时返回 `hggcErrorInvalidDevice`；已启用过时返回 `hggcErrorPeerAccessAlreadyEnabled`；`flags` 非 0 返回 `hggcErrorInvalidValue`。

```c
hggcError_t hggcDeviceEnablePeerAccess (int peerDevice, unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| peerDevice | in | 从当前设备启用对该对等设备的直接访问 |
| flags | in | 保留字段，必须设为 0 |

错误码：hggcSuccess、hggcErrorInvalidDevice、hggcErrorPeerAccessAlreadyEnabled、hggcErrorInvalidValue

#### hggcDeviceGetP2PAttribute

在 `*value` 中返回 `srcDevice` 和 `dstDevice` 之间链路的属性 `attr`。支持的属性：

- `hggcDevP2PAttrPerformanceRank` — 链路性能相对值，较低值表示更好性能（0 为最高性能链接）。
- `hggcDevP2PAttrAccessSupported` — 已启用 peer access 则为 1。
- `hggcDevP2PAttrNativeAtomicSupported` — 支持该链路上所有原生原子操作则为 1。
- `hggcDevP2PAttrHggcArrayAccessSupported` — 支持通过该链路访问 HGGC 数组则为 1。
- `hggcDevP2PAttrOnlyPartialNativeAtomicSupported` — 支持该链路上部分 HGGC 有效原子操作则为 1（可用相应接口获取特定操作信息）。

`srcDevice` 或 `dstDevice` 无效或相同，返回 `hggcErrorInvalidDevice`；`attr` 无效或 `value` 为空指针，返回 `hggcErrorInvalidValue`。

```c
__host__ hggcError_t hggcDeviceGetP2PAttribute (int* value,
                                                hggcDeviceP2PAttr attr,
                                                int srcDevice,
                                                int dstDevice)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| value | out | 用于返回请求属性的值 |
| attr | in | 要查询的 P2P 属性 |
| srcDevice | in | 目标链接的源设备 |
| dstDevice | in | 目标链接的目标设备 |

错误码：hggcSuccess、hggcErrorInvalidDevice、hggcErrorInvalidValue

## 模块与代码加载

### 模块与符号管理

本模块提供**模块加载与符号查询**接口：获取设备端函数句柄、查询全局符号地址与大小。

| 函数 | 用途 |
|------|------|
| `hggcGetFuncBySymbol` | 获取与入口函数 `symbolPtr` 匹配的设备入口函数指针 |
| `hggcGetKernel` | 获取与入口函数 `entryFuncAddr` 匹配的设备核函数指针 |
| `hggcGetSymbolAddress` | 在 *devPtr 中返回设备上符号 symbol 的地址 |
| `hggcGetSymbolSize` | 在 *size 中返回符号 symbol 的大小 |

#### hggcGetFuncBySymbol

在 `functionPtr` 中返回与符号 `symbolPtr` 对应的设备入口函数。

```c
hggcError_t hggcGetFuncBySymbol (hggcFunction_t* functionPtr,
                                 const void* symbolPtr)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| functionPtr | out | 用于返回设备入口函数 |
| symbolPtr | in | 要查找的设备入口函数指针 |

错误码：hggcSuccess

#### hggcGetKernel

在 `kernelPtr` 中返回与入口函数 `entryFuncAddr` 对应的设备核函数。注意：可能存在属于不同翻译单元、但具有相同 `entryFuncAddr` 的多个符号被注册到该 HGGC 运行时，翻译单元的加载注册顺序可能导致返回指针不同。唯一性保证方法：在相应翻译单元中使用 `static` 或 `hidden` 可见性属性限制 `__global__` 设备函数的可见性。

```c
hggcError_t hggcGetKernel (hggcKernel_t* kernelPtr, const void* entryFuncAddr)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| kernelPtr | out | 用于返回设备核函数 |
| entryFuncAddr | in | 用于查找核函数的设备入口函数地址 |

错误码：hggcSuccess

#### hggcGetSymbolAddress

在 *devPtr 中返回设备上符号 symbol 的地址。symbol 可以是位于全局或常量内存空间中的变量。找不到 symbol 或未声明在全局/常量内存空间中时，*devPtr 保持不变并返回 `hggcErrorInvalidSymbol`。注意：也可能返回先前异步启动的错误码；触发 HGGC RT 内部初始化时可能返回 `hggcErrorInitializationError`/`hggcErrorInsufficientDriver`/`hggcErrorNoDevice`；`hggcStreamAddCallback` 回调内禁止调用任何 HGGC 函数，违规可能（不保证）返回 `hggcErrorNotPermitted`。

```c
template < class T > hggcError_t hggcGetSymbolAddress (void** devPtr,
                                                       const T& symbol)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| devPtr | out | 返回与符号关联的设备指针 |
| symbol | in | 设备符号引用 |

错误码：hggcSuccess、hggcErrorInvalidSymbol、hggcErrorNoKernelImageForDevice

#### hggcGetSymbolSize

在 *size 中返回符号 symbol 的大小。symbol 必须是位于全局或常量内存空间中的变量；找不到或空间不符时 *size 保持不变并返回 `hggcErrorInvalidSymbol`。通用注意事项同 `hggcGetSymbolAddress`。

```c
template < class T > hggcError_t hggcGetSymbolSize (size_t* size,
                                                    const T& symbol)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| size | in | 与符号关联对象的大小 |
| symbol | in | 设备符号引用 |

错误码：hggcSuccess、hggcErrorInvalidSymbol、hggcErrorNoKernelImageForDevice

## 内存管理

本节涵盖设备内存的分配/释放、主机-设备间数据搬运、内存填充以及流有序内存池。

> **通用注意事项**（适用于本节后述所有内存、复制、填充、内存池及图管理函数，正文不再逐条重复）：(1) 这些函数也可能返回先前异步启动产生的错误码；(2) 若调用触发 HGGC RT 内部状态初始化，还可能返回 `hggcErrorInitializationError`、`hggcErrorInsufficientDriver` 或 `hggcErrorNoDevice`；(3) 按 `hggcStreamAddCallback` 的规定，流回调内禁止调用任何 HGGC 函数，违规时可能（但不保证）返回 `hggcErrorNotPermitted` 作为诊断。带 Async 后缀的函数均采用标准的默认流语义（见"流同步行为"节）。

### 内存管理（分配/释放/预取/属性）

本模块覆盖设备内存分配/释放、主机锁页内存分配、托管内存（managed memory）、进程间内存共享（IPC）、属性查询及阵列（array）操作。

| 函数 | 用途 |
|------|------|
| `hggcFree` | 释放设备上的内存 |
| `hggcFreeHost` | 释放由 hggcMallocHost / hggcHostAlloc 分配的页锁定主机内存 |
| `hggcHostAlloc` | 在主机上分配带行为标志的页锁定内存（可选映射到设备地址空间） |
| `hggcHostGetDevicePointer` | 获取已映射的页锁定主机内存对应的设备指针 |
| `hggcHostGetFlags` | 查询已分配页锁定主机内存的分配标志 |
| `hggcHostRegister` | 将已存在的主机内存范围注册为页锁定供 HGGC 使用 |
| `hggcHostUnregister` | 取消由 hggcHostRegister 注册的内存范围 |
| `hggcIpcCloseMemHandle` | 关闭通过 `hggcIpcOpenMemHandle` 映射的进程间内存句柄 |
| `hggcIpcGetMemHandle` | 获取现有设备内存分配的进程间内存句柄 |
| `hggcIpcOpenMemHandle` | 打开从其他进程导出的进程间内存句柄，返回本地进程可用的设备指针 |
| `hggcMalloc` | 在设备上分配指定字节数的线性内存 |
| `hggcMalloc3D` | 在设备上分配逻辑 1D、2D 或 3D 内存对象 |
| `hggcMalloc3DArray` | 分配三维 HGGC 数组 |
| `hggcMallocArray` | 分配一维/二维 HGGC 数组 |
| `hggcMallocHost` | 在主机上分配页锁定内存 |
| `hggcMallocManaged` | 分配将由 Unified Memory 系统自动管理的内存 |
| `hggcMallocMipmappedArray` | 在设备上分配映射（mipmap）数组 |
| `hggcMallocPitch` | 在设备上分配带间距（pitched）的内存 |
| `hggcMemAdvise` | 提供关于给定内存范围使用的建议 |
| `hggcMemDiscardAndPrefetchBatchAsync` | 异步执行批量内存丢弃和预取 |
| `hggcMemDiscardBatchAsync` | 异步执行批量内存丢弃 |
| `hggcMemGetInfo` | 获取可用和总设备内存 |
| `hggcMemPrefetchAsync` | 将内存预取到指定的目标位置 |
| `hggcMemPrefetchBatchAsync` | 异步执行批量内存预取 |
| `hggcMemRangeGetAttribute` | 查询内存范围的某个属性 |
| `hggcMemRangeGetAttributes` | 查询内存范围的多个属性 |
| `hggcPointerGetAttributes` | 查询指针的属性 |

#### hggcFree

释放由 devPtr 指向的内存空间，该空间必须由以下分配 API 之一返回：`hggcMalloc()`、`hggcMallocPitch()`、`hggcMallocManaged()`、`hggcMallocAsync()`、`hggcMallocFromPoolAsync()`。

- 指针来自 `hggcMallocAsync`/`hggcMallocFromPoolAsync` 时，此 API **不做任何隐式同步**——调用方必须确保调用 `hggcFree` 前对这些指针的所有访问均已完成。为获得最佳性能和内存复用，应使用 `hggcFreeAsync` 释放流顺序分配器分配的内存。其他指针此 API 可能执行隐式同步。
- 重复 `hggcFree(devPtr)` 返回错误；devPtr 为 0 时不执行任何操作；失败时返回 hggcErrorValue。
- `hggcFree` 的设备版本不能用于 host API 分配的 *devPtr，反之亦然。

```c
hggcError_t hggcFree (void* devPtr)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| devPtr | in | 要释放的设备内存指针 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcFreeHost

释放由 `hggcMallocHost()` 或 `hggcHostAlloc()` 分配的页锁定主机内存。重复调用返回错误；ptr 为 NULL 时不动作。不能用于释放 `hggcMalloc()` 等设备端分配的指针，也不能用于 `hggcHostRegister()` 注册的内存（后者用 `hggcHostUnregister()`）。

```c
hggcError_t hggcFreeHost (void* ptr)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| ptr | in | 待释放的页锁定主机内存指针 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcHostAlloc

在主机端分配 size 字节的页锁定（page-locked / pinned）内存，通过 *pHost 返回主机指针。该内存被锁定不可换出，可被设备通过 DMA 高带宽访问；与可分页内存相比，主机-设备拷贝带宽更高。flags 可按位组合（彼此正交）：

- `hggcHostAllocDefault`：默认行为，等价于不带附加属性的页锁定分配。
- `hggcHostAllocPortable`：分配出的内存对所有 HGGC 上下文均视为 pinned。
- `hggcHostAllocMapped`：映射到设备地址空间，设备端可直接访问；设备指针通过 `hggcHostGetDevicePointer()` 获取。
- `hggcHostAllocWriteCombined`：write-combined（WC）分配，适用于 CPU 写入、设备读取的暂存缓冲区；CPU 读 WC 内存效率低，慎用于读多场景。

`hggcHostAllocMapped` 生效需当前上下文支持 `hggcDeviceMapHost`（运行时 API 创建的上下文隐式启用）。设备不支持映射固定内存时分配仍可成功，错误延迟到 `hggcHostGetDevicePointer()` 时上报。分配的内存必须用 `hggcFreeHost()` 释放。

```c
hggcError_t hggcHostAlloc (void** pHost,
                           size_t size,
                           unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pHost | out | 指向已分配主机内存的指针 |
| size | in | 申请分配的大小（字节） |
| flags | in | 行为标志，`hggcHostAlloc*` 常量的按位组合 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorMemoryAllocation

#### hggcHostGetDevicePointer

返回已映射页锁定主机内存对应的设备端指针。该内存必须经 `hggcHostAlloc()` 以 `hggcHostAllocMapped` 分配，或经 `hggcHostRegister()` 以 `hggcHostRegisterMapped` 注册。上下文未启用 `hggcDeviceMapHost` 或设备不支持映射固定内存时调用失败。UVA 启用且 `hggcDevAttrCanUseHostPointerForRegisteredMem` 非零的设备上，返回的设备指针可能与主机指针 pHost 相同；否则不同但在所有支持设备上有效——同一块内存不应混用主机指针与设备指针并发访问。flags 预留，必须为 0。

```c
hggcError_t hggcHostGetDevicePointer (void** pDevice,
                                      void* pHost,
                                      unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pDevice | out | 返回的设备端指针 |
| pHost | in | 已映射的主机端指针 |
| flags | in | 预留，必须为 0 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorMemoryAllocation

#### hggcHostGetFlags

返回 pHost 所指页锁定主机内存分配时的行为标志（写入 *pFlags）。pHost 必须由 `hggcHostAlloc()` 返回；对 `hggcMallocHost()`、可分页内存或未注册指针调用返回 `hggcErrorInvalidValue`。

```c
hggcError_t hggcHostGetFlags (unsigned int* pFlags, void* pHost)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pFlags | out | 返回的分配行为标志（`hggcHostAlloc*` 常量按位组合） |
| pHost | in | 由 `hggcHostAlloc()` 返回的主机指针 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcHostRegister

将一段已存在的主机内存范围 ([ptr, ptr+size)) 注册为页锁定，使其可被设备 DMA 高带宽访问。常用于让 malloc/系统分配的缓冲区不复制即接入 HGGC 数据通路。flags（正交，可按位组合）：

- `hggcHostRegisterDefault`：默认行为，仅页锁定。
- `hggcHostRegisterPortable`：注册结果对所有 HGGC 上下文可见为 pinned。
- `hggcHostRegisterMapped`：映射到设备地址空间；设备指针经 `hggcHostGetDevicePointer()` 获取。
- `hggcHostRegisterIoMemory`：将指针视为指向 I/O 内存（非系统 RAM）。
- `hggcHostRegisterReadOnly`：声明为设备只读；缺乏 `hggcDevAttrPageableMemoryAccessUsesHostPageTables` 支持的平台上，映射到 CPU 的内存注册为只读时需此标志。支持性可用 `hggcDevAttrHostRegisterReadOnlySupported` 查询，不支持的设备使用此标志返回 hggcErrorNotSupported。

注册的内存必须用 `hggcHostUnregister()` 取消注册。

```c
hggcError_t hggcHostRegister (void* ptr,
                              size_t size,
                              unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| ptr | in | 待注册的主机内存起始指针 |
| size | in | 待注册区域大小（字节） |
| flags | in | 注册行为标志，`hggcHostRegister*` 常量按位组合 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorMemoryAllocation、hggcErrorHostMemoryAlreadyRegistered、hggcErrorNotSupported

#### hggcHostUnregister

取消 `hggcHostRegister()` 注册的内存范围，解除页锁定与可能的设备映射。ptr 必须与注册时的起始指针严格一致（不允许区域内偏移）。返回后该内存不再适合作为 HGGC DMA 对端。指针从未注册或已取消注册时返回 `hggcErrorHostMemoryNotRegistered`。不适用于 `hggcHostAlloc()`/`hggcMallocHost()` 分配的内存（那些用 `hggcFreeHost()`）。

```c
hggcError_t hggcHostUnregister (void* ptr)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| ptr | in | 待取消注册的主机内存起始指针，需与原注册指针一致 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorHostMemoryNotRegistered

#### hggcIpcCloseMemHandle

将 `hggcIpcOpenMemHandle` 返回的内存引用计数减 1；计数到 0 时取消映射该内存。导出进程中的原始分配及其他进程导入的映射不受影响；若为最后一个映射，将释放用于启用对等访问的资源。可用 `hggcDevAttrIpcEventSupport` 调用 `hggcDeviceGetAttribute` 测试设备 IPC 能力。

```c
__host__ hggcError_t hggcIpcCloseMemHandle (void* devPtr)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| devPtr | out | `hggcIpcOpenMemHandle` 返回的设备指针 |

错误码：hggcSuccess、hggcErrorMapBufferObjectFailed、hggcErrorNotSupported、hggcErrorInvalidValue

#### hggcIpcGetMemHandle

将 `hggcMalloc` 创建的设备内存分配基址导出供另一进程使用。轻量级操作，可在同一分配上多次调用。若内存经 `hggcFree` 释放后又有 `hggcMalloc` 返回相同设备地址，`hggcIpcGetMemHandle` 将为新内存返回唯一句柄。IPC 能力测试同上。

```c
__host__ hggcError_t hggcIpcGetMemHandle (hggcIpcMemHandle_t* handle,
                                          void* devPtr)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| handle | out | 用户分配的 `hggcIpcMemHandle`，用于返回句柄 |
| devPtr | in | 先前分配的设备内存基址指针 |

错误码：hggcSuccess、hggcErrorMemoryAllocation、hggcErrorMapBufferObjectFailed、hggcErrorNotSupported、hggcErrorInvalidValue

#### hggcIpcOpenMemHandle

将另一进程 `hggcIpcGetMemHandle` 导出的内存映射到当前设备地址空间。对不同设备上的上下文，可尝试启用设备间对等访问（如同调用 `hggcDeviceEnablePeerAccess`），由 `hggcIpcMemLazyEnablePeerAccess` 标志控制；`hggcDeviceCanAccessPeer` 可确定能否映射。可打开对调用进程不可见设备的句柄。限制：给定进程中每个设备的 `hggcIpcMemHandle` 只能由其他进程中每个设备的每一个上下文打开一次；当前上下文已打开时引用计数加 1 并返回现有设备指针。返回的内存必须用 `hggcIpcCloseMemHandle` 释放；在导入上下文调用 `hggcIpcCloseMemHandle` 之前对导出内存调用 `hggcFree` 行为未定义。IPC 能力测试同上。

```c
__host__ hggcError_t hggcIpcOpenMemHandle (void** devPtr,
                                           hggcIpcMemHandle_t handle,
                                           unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| devPtr | out | 用于返回的设备指针 |
| handle | in | 要打开的 `hggcIpcMemHandle` |
| flags | in | 必须指定为 `hggcIpcMemLazyEnablePeerAccess` |

错误码：hggcSuccess、hggcErrorMapBufferObjectFailed、hggcErrorInvalidResourceHandle、hggcErrorDeviceUninitialized、hggcErrorTooManyPeers、hggcErrorNotSupported、hggcErrorInvalidValue

#### hggcMalloc

在设备全局内存中分配 size 字节的线性内存，通过 *devPtr 返回设备指针。内存对任意类型变量均有合适对齐，**不会清零**。size 为 0 返回 `hggcErrorInvalidValue`；分配失败返回 `hggcErrorMemoryAllocation`。指针仅适用于当前上下文关联的设备；是纯设备端内存，主机代码不能直接解引用，与主机的数据交换需用 `hggcMemcpy` 系列。序列布局场景用本函数；需要 2D/3D 对齐的场景优先 `hggcMallocPitch()`/`hggcMalloc3D()`。分配的内存必须用 `hggcFree()` 释放。

```c
hggcError_t hggcMalloc (void** devPtr, size_t size)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| devPtr | out | 指向已分配设备内存的指针 |
| size | in | 申请分配的大小（字节） |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorMemoryAllocation

#### hggcMalloc3D

在设备上分配至少 width × height × depth 字节的线性内存，返回 `hggcPitchedPtr`：ptr 指向所分配内存；可能对分配填充以满足硬件对齐；pitch 字段为该分配宽度（字节）；xsize/ysize 为逻辑宽度与高度（等于分配时的 width/height）。2D/3D 对象分配用本函数或 `hggcMallocPitch()` 可保证硬件对齐，对后续 2D/3D 内存复制尤为重要。

```c
hggcError_t hggcMalloc3D (hggcPitchedPtr* pitchedDevPtr, hggcExtent extent)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pitchedDevPtr | in | 指向已分配的 pitched 设备内存的指针 |
| extent | in | 申请分配的大小（width） |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorMemoryAllocation

#### hggcMalloc3DArray

分配一个 HGGC 数组，在 *array 中返回句柄。可分配的形态：

- height 和 depth 的 extent 均为零 → 1D 数组。
- 仅 depth 的 extent 为零 → 2D 数组。
- 三个 extent 均非零 → 3D 数组。
- 仅 height 为零且设 `hggcArrayLayered` → 1D 分层数组（每层一个 1D 数组，层数由 depth extent 决定）。
- 三个 extent 非零且设 `hggcArrayLayered` → 2D 分层数组。
- 三个 extent 非零且设 `hggcArrayCubemap` → cubemap 数组（width 必须等于 height，depth 必须为 6）。
- 三个 extent 非零且同时设 `hggcArrayCubemap` + `hggcArrayLayered` → cubemap 分层数组（width == height，depth 为 6 的倍数）。

flags 选项：

- `hggcArrayDefault`（= 0）：默认数组分配。
- `hggcArrayLayered`：分层数组，depth extent 指示层数。
- `hggcArrayCubemap`：cubemap 数组（约束同上）。
- `hggcArraySurfaceLoadStore`：可通过 surface reference 读写的数组。
- `hggcArrayTextureGather`：将对数组执行纹理 gather 操作（仅 2D 数组）。
- `hggcArraySparse`：不带物理后备内存的稀疏数组，子区域随后可经内存映射接口映射到物理内存。
- `hggcArrayDeferredMapping`：不带物理后备内存，整个数组随后可一次性映射到物理内存。

width、height、depth 的 extent 必须满足特定尺寸要求，所有值以元素为单位。

```c
hggcError_t hggcMalloc3DArray (hggcArray_t* array,
                               const void* desc,
                               hggcExtent extent,
                               unsigned int flags = 0)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| array | in | 指向设备内存中已分配数组的指针 |
| desc | in | 请求的通道格式 |
| extent | in | 申请分配的大小（width） |
| flags | in | 扩展标志 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorMemoryAllocation

#### hggcMallocArray

分配一维/二维 HGGC 数组，在 *array 中返回句柄。flags 选项：`hggcArrayDefault`（= 0，默认分配）、`hggcArraySurfaceLoadStore`（可经 surface reference 读写）、`hggcArraySparse`（无物理后备内存）、`hggcArrayDeferredMapping`（无物理后备内存，整体后映射）。width 和 height 的尺寸要求见 `hggcMalloc3DArray()`。

```c
hggcError_t hggcMallocArray (hggcArray_t* array,
                             const void* desc,
                             size_t width,
                             size_t height = 0,
                             unsigned int flags = 0)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| array | in | 指向设备内存中已分配数组的指针 |
| desc | in | 请求的通道格式 |
| width | in | 请求的数组分配宽度 |
| height | in | 请求的数组分配高度 |
| flags | in | 请求的已分配数组属性 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorMemoryAllocation

#### hggcMallocHost

分配 size 字节的页锁定主机内存，设备可访问。驱动跟踪该虚拟内存范围并自动加速 `hggcMemcpy*()` 等调用；相较可分页内存带宽更高。在 pageableMemoryAccessUsesHostPageTables 为 true 的系统上可能不做页锁定。页锁定过量内存会减少系统可分页内存、降低系统性能——适合用作主机-设备数据交换暂存区，不宜过量。

```c
hggcError_t hggcMallocHost (void** ptr, size_t size)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| ptr | in | 指向已分配主机内存的指针 |
| size | in | 申请分配的大小（字节） |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorMemoryAllocation、hggcErrorExternalDevice

#### hggcMallocManaged

在设备上分配 size 字节的 managed memory，*devPtr 返回指针。设备不支持 managed memory 时返回 `hggcErrorNotSupported`（可用 `hggcDevAttrManagedMemory` 查询）。内存对任意类型有合适对齐，不清零；size 为 0 返回 `hggcErrorInvalidValue`。指针在 CPU 及系统中所有支持 managed memory 的 PPU 上均有效，所有访问须遵循 Unified Memory 编程模型。flags 指定默认流关联，必须为 `hggcMemAttachGlobal`（默认：任意设备任意流可访问）或 `hggcMemAttachHost`（不应从 `hggcDevAttrConcurrentManagedAccess` 为零的设备访问；需显式 `hggcStreamAttachMemAsync` 才能在这类设备上启用访问）。分配的内存用 `hggcFree` 释放。`hggcDevAttrConcurrentManagedAccess` 非零的 PPU 上可能发生设备内存超额订阅（oversubscription），UM 驱动可能随时将 managed memory 逐出到主机内存。

```c
hggcError_t hggcMallocManaged (void** devPtr,
                               size_t size,
                               unsigned int flags = hggcMemAttachGlobal)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| devPtr | in | 指向已分配设备内存的指针 |
| size | in | 申请分配的大小（字节） |
| flags | in | `hggcMemAttachGlobal` 或 `hggcMemAttachHost`（默认前者） |

错误码：hggcSuccess、hggcErrorMemoryAllocation、hggcErrorNotSupported、hggcErrorInvalidValue

#### hggcMallocMipmappedArray

分配 HGGC mipmap 数组，*mipmappedArray 返回句柄。numLevels 指定 mipmap 级别数，会被钳制到 [1, 1 + floor(log2(max(width, height, depth)))]。可分配形态：1D / 2D / 3D mipmap 数组（规则同 `hggcMalloc3DArray`）、1D/2D 分层 mipmap 数组（设 `hggcArrayLayered`）、cubemap mipmap 数组（设 `hggcArrayCubemap`）。flags 选项：`hggcArrayDefault`（= 0）、`hggcArrayLayered`、`hggcArrayCubemap`、`hggcArraySurfaceLoadStore`（各级可经 surface reference 读写）、`hggcArrayTextureGather`、`hggcArraySparse`、`hggcArrayDeferredMapping`。extent 尺寸要求同上，以元素为单位。

```c
hggcError_t hggcMallocMipmappedArray (hggcMipmappedArray_t* mipmappedArray,
                                      const void* desc,
                                      hggcExtent extent,
                                      unsigned int numLevels,
                                      unsigned int flags = 0)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| mipmappedArray | in | 指向设备内存中已分配 mipmap 数组的指针 |
| desc | in | 请求的通道格式 |
| extent | in | 申请分配的大小（width） |
| numLevels | in | 要分配的 mipmap 级别数量 |
| flags | in | 扩展标志 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorMemoryAllocation

#### hggcMallocPitch

在设备上分配至少 width（字节）× height 字节的线性内存，*devPtr 返回指针。可能对分配填充，以保证任意给定行的对应指针在行间更新时仍满足合并访问（coalescing）对齐要求。*pitch 返回的步幅为该分配宽度（字节），预期用法是作为独立参数计算 2D 数组内地址：

```cpp
T* pElement = (T*)((char*)BaseAddress + Row * pitch) + Column;
```

2D 数组分配用本函数可保证硬件步幅对齐，对 2D 内存复制尤为重要。

```c
hggcError_t hggcMallocPitch (void** devPtr,
                             size_t* pitch,
                             size_t width,
                             size_t height)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| devPtr | in | 指向已分配的 pitched 设备内存的指针 |
| pitch | in | 分配得到的步幅 |
| width | in | 请求的 pitched 分配宽度（字节） |
| height | in | 请求的 pitched 分配高度 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorMemoryAllocation

#### hggcMemAdvise

向 Unified Memory 子系统提供建议，描述从 devPtr 开始、count 字节内存范围的使用模式。范围起止地址分别向下/向上取整对齐到 CPU 页大小。范围必须指向 `hggcMallocManaged` 分配的托管内存或 `__managed__` 变量声明的内存，也可以指向系统分配的可分页内存（须为有效且主机可访问区域）。advice 取值：

- `hggcMemAdviseSetReadMostly`：数据主要用于读取、偶尔写入；任意处理器的读访问都会在该处理器内存中创建至少含所访问页的只读副本。
- `hggcMemAdviseUnsetReadMostly`：撤销上述效果。
- `hggcMemAdviseSetPreferredLocation`：将数据首选位置设为 location 所属内存。
- `hggcMemAdviseUnsetPreferredLocation`：撤销上述效果。
- `hggcMemAdviseSetAccessedBy`：数据将被处理器 location 访问。
- `hggcMemAdviseUnsetAccessedBy`：撤销上述效果。

此函数在大多数使用场景下表现为异步行为，使用标准默认流语义。

```c
hggcError_t hggcMemAdvise (const void* devPtr,
                           size_t count,
                           hggcMemoryAdvise advice,
                           hggcMemLocation location)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| devPtr | in | 要设置建议的内存指针 |
| count | in | 内存范围的大小（字节） |
| advice | in | 要应用的建议 |
| location | in | 建议应用到的 location |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidDevice

#### hggcMemDiscardAndPrefetchBatchAsync

执行一批内存丢弃操作，随后执行预取。整个批次按流顺序执行，但批次内各操作不保证特定顺序。系统中所有设备的 `hggcDevAttrConcurrentManagedAccess` 都必须非零，否则返回错误。语义等价于先 `hggcMemDiscardBatchAsync` 再 `hggcMemPrefetchBatchAsync`，但更高效。

注意：对内存范围任意部分的读、写或预取若与此组合操作同时发生，行为未定义。

```c
hggcError_t hggcMemDiscardAndPrefetchBatchAsync (void** dptrs,
                                                 size_t* sizes,
                                                 size_t count,
                                                 hggcMemLocation* prefetchLocs,
                                                 size_t* prefetchLocIdxs,
                                                 size_t numPrefetchLocs,
                                                 unsigned long long flags,
                                                 hggcStream_t stream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dptrs | in | 要丢弃的指针数组 |
| sizes | in | 内存丢弃操作的大小数组 |
| count | in | dptrs 和 sizes 数组的大小 |
| prefetchLocs | in | 要预取到的位置数组 |
| prefetchLocIdxs | in | 索引数组，指定 prefetchLocs 各条目适用于哪些操作数 |
| numPrefetchLocs | in | prefetchLocs 和 prefetchLocIdxs 数组的大小 |
| flags | in | 预留，必须为零 |
| stream | in | 流标识符 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcMemDiscardBatchAsync

执行一批内存丢弃操作。整个批次按流顺序执行，批次内顺序不保证。所有设备的 `hggcDevAttrConcurrentManagedAccess` 都必须非零。丢弃告知驱动该范围内容不再有用，可使驱动优化数据迁移并降低内存压力。对该范围写入，或经 `hggcMemPrefetchAsync`/`hggcMemPrefetchBatchAsync` 预取，可撤销丢弃。

注意：与丢弃同时发生的读/写/预取行为未定义。

```c
hggcError_t hggcMemDiscardBatchAsync (void** dptrs,
                                      size_t* sizes,
                                      size_t count,
                                      unsigned long long flags,
                                      hggcStream_t stream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dptrs | in | 要丢弃的指针数组 |
| sizes | in | 丢弃操作的大小数组 |
| count | in | dptrs 和 sizes 数组的大小 |
| flags | in | 预留，必须为零 |
| stream | in | 流标识符 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcMemGetInfo

在 *total 中返回当前上下文可用内存总量，*free 中返回按操作系统统计的设备空闲内存量。HGGC 不保证能分配 OS 报告为可用的全部内存；多租户场景下 free 估计值易受竞争条件影响。

```c
hggcError_t hggcMemGetInfo (size_t* free, size_t* total)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| free | out | 返回的空闲内存（字节） |
| total | out | 返回的总内存（字节） |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorLaunchFailure

#### hggcMemPrefetchAsync

将内存预取到指定目标 location。devPtr 为基址设备指针，count 为字节数，stream 为入队流。范围必须指向 `hggcMallocManaged` 托管内存或 `__managed__` 变量，或托管内存池分配的内存，或在 `hggcDevAttrPageableMemoryAccess` 非零的系统上指向系统分配内存。大多数场景下表现为异步行为，使用标准默认流语义。

```c
hggcError_t hggcMemPrefetchAsync (const void* devPtr,
                                  size_t count,
                                  hggcMemLocation location,
                                  unsigned int flags,
                                  hggcStream_t stream = 0)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| devPtr | in | 要预取的指针 |
| count | in | 大小（字节） |
| location | in | 要预取到的 location |
| flags | in | 预留，目前必须为 0 |
| stream | in | 入队预取操作的流 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidDevice

#### hggcMemPrefetchBatchAsync

执行一批内存预取操作。整个批次按流顺序执行，批次内顺序不保证。所有设备的 `hggcDevAttrConcurrentManagedAccess` 都必须非零。单个预取操作语义同 `hggcMemPrefetchAsync`。

```c
hggcError_t hggcMemPrefetchBatchAsync (void** dptrs,
                                       size_t* sizes,
                                       size_t count,
                                       hggcMemLocation* prefetchLocs,
                                       size_t* prefetchLocIdxs,
                                       size_t numPrefetchLocs,
                                       unsigned long long flags,
                                       hggcStream_t stream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dptrs | in | 要预取的指针数组 |
| sizes | in | 预取操作的大小数组 |
| count | in | dptrs 和 sizes 数组的大小 |
| prefetchLocs | in | 要预取到的位置数组 |
| prefetchLocIdxs | in | 索引数组，指定 prefetchLocs 各条目适用于哪些操作数 |
| numPrefetchLocs | in | prefetchLocs 和 prefetchLocIdxs 数组的大小 |
| flags | in | 预留，必须为零 |
| stream | in | 流标识符 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcMemRangeGetAttribute

查询从 devPtr 开始、count 字节内存范围的某个属性。范围必须指向托管内存或 `__managed__` 变量。attribute 取值：

- `hggcMemRangeAttributeReadMostly`：范围内所有页面均启用读取复制（read-duplication）则返回 1，否则 0。
- `hggcMemRangeAttributePreferredLocation`：返回首选位置的 PPU 设备 id 或 hggcCpuDeviceId。
- `hggcMemRangeAttributeAccessedBy`：返回对整个范围设置了 hggcMemAdviceSetAccessedBy 的设备 id 列表。
- `hggcMemRangeAttributeLastPrefetchLocation`：返回所有页面最近一次被显式预取到的位置。
- `hggcMemRangeAttributePreferredLocationType`：返回首选位置的类型。
- `hggcMemRangeAttributePreferredLocationId`：返回首选位置的 ID。
- `hggcMemRangeAttributeLastPrefetchLocationType`：返回最近一次预取的位置类型。
- `hggcMemRangeAttributeLastPrefetchLocationId`：返回最近一次预取的位置 ID。

```c
hggcError_t hggcMemRangeGetAttribute (void* data,
                                      size_t dataSize,
                                      hggcMemRangeAttribute attribute,
                                      const void* devPtr,
                                      size_t count)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| data | in | 属性查询结果写入位置 |
| dataSize | in | data 的大小（字节） |
| attribute | in | 要查询的属性 |
| devPtr | in | 查询范围的起始地址 |
| count | in | 查询范围的大小 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcMemRangeGetAttributes

查询内存范围的多个属性。范围要求与支持的属性列表同 `hggcMemRangeGetAttribute`。

```c
hggcError_t hggcMemRangeGetAttributes (void** data,
                                       size_t* dataSizes,
                                       hggcMemRangeAttribute* attributes,
                                       size_t numAttributes,
                                       const void* devPtr,
                                       size_t count)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| data | in | 二维数组，指向各属性结果写入位置 |
| dataSizes | in | 每个结果的大小数组 |
| attributes | in | 要查询的属性数组 |
| numAttributes | in | 要查询的属性数量 |
| devPtr | in | 查询范围的起始地址 |
| count | in | 查询范围的大小 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcPointerGetAttributes

```c
hggcError_t hggcPointerGetAttributes ( hggcPointerAttributes* attributes, const void* ptr )
```

在 `*attributes` 中返回指针 `ptr` 的属性。指针不是在支持统一寻址的上下文中分配、映射或注册的，返回 `hggcErrorInvalidValue`。注：传入主机指针时 `hggcPointerAttributes::type` 返回 `hggcMemoryTypeUnregistered`，且调用返回 `hggcSuccess`。结构体字段（完整定义见数据类型节）：`type` 标识内存类型（Unregistered/Host/Device/Managed）；`device` 对 Device 类型标识物理驻留设备、对 Host 类型标识分配时的当前设备；`devicePointer` 为当前设备可访问的设备指针别名（不可直接访问为 NULL）；`hostPointer` 为主机指针别名（不可直接访问为 NULL）。

错误码：hggcSuccess、hggcErrorInvalidDevice、hggcErrorInvalidValue

### 内存复制

本模块提供**内存复制（memcpy）**接口，支持一维/二维/三维、同步/异步、主机-设备/设备-设备间的数据拷贝。各方向的精确阻塞语义见"API 同步行为"节。

| 函数 | 用途 |
|------|------|
| `hggcMemcpy` | 1D 拷贝（同步） |
| `hggcMemcpyAsync` | 1D 拷贝（异步） |
| `hggcMemcpy2D` | 2D 矩阵拷贝（同步） |
| `hggcMemcpy2DAsync` | 2D 矩阵拷贝（异步） |
| `hggcMemcpy2DArrayToArray` | HGGC 数组到数组的 2D 拷贝 |
| `hggcMemcpy2DFromArrayAsync` | 从 HGGC 数组异步拷贝 2D 矩阵 |
| `hggcMemcpy2DToArrayAsync` | 从内存异步拷贝 2D 矩阵到 HGGC 数组 |
| `hggcMemcpy3D` | 两个 3D 对象间拷贝（同步） |
| `hggcMemcpy3DAsync` | 两个 3D 对象间拷贝（异步） |
| `hggcMemcpy3DPeer` | 设备间 3D 拷贝 |
| `hggcMemcpy3DPeerAsync` | 设备间异步 3D 拷贝 |
| `hggcMemcpyFromSymbol` | 从设备符号拷贝（同步） |
| `hggcMemcpyFromSymbolAsync` | 从设备符号异步拷贝 |
| `hggcMemcpyPeer` | 两个设备间拷贝（同步） |
| `hggcMemcpyPeerAsync` | 两个设备间异步拷贝 |
| `hggcMemcpyToSymbol` | 拷贝到设备符号（同步） |
| `hggcMemcpyToSymbolAsync` | 异步拷贝到设备符号 |
| `hggcMemcpyArrayToArray` | 两个 HGGC 数组之间拷贝 |
| `hggcMemcpyFromArrayAsync` | 从 HGGC 数组异步拷贝到内存 |
| `hggcMemcpyToArrayAsync` | 内存数据异步拷贝到 HGGC 数组 |

#### hggcMemcpy

将 src 的 count 字节复制到 dst。kind 指定方向，必须为 `hggcMemcpyHostToHost`/`HostToDevice`/`DeviceToHost`/`DeviceToDevice`/`Default` 之一。`hggcMemcpyDefault` 按指针值自动推断方向，但仅允许在支持统一虚拟寻址的系统上使用。请求的内存区域必须要么完全注册到 HGGC，要么（主机可分页传输）完全未注册。大多数用例表现为同步行为。

```c
hggcError_t hggcMemcpy (void* dst,
                        const void* src,
                        size_t count,
                        hggcMemcpyKind kind)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dst | in | 目标内存地址 |
| src | in | 源内存地址 |
| count | in | 要复制的大小（字节） |
| kind | in | 传输类型 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidMemcpyDirection

#### hggcMemcpy2D

将矩阵（height, width）从 src 复制到 dst。dpitch/spitch 是 dst/src 2D 数组在内存中的宽度（字节，含行尾填充）。内存区域不得重叠，width 不得超过 dpitch 或 spitch。注册要求同上。

```c
hggcError_t hggcMemcpy2D (void* dst,
                          size_t dpitch,
                          const void* src,
                          size_t spitch,
                          size_t width,
                          size_t height,
                          hggcMemcpyKind kind)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dst | in | 目标内存地址 |
| dpitch | in | 目标内存的步幅 |
| src | in | 源内存地址 |
| spitch | in | 源内存的步幅 |
| width | in | 矩阵传输宽度（列，字节） |
| height | in | 矩阵传输高度（行） |
| kind | in | 传输类型 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidPitchValue、hggcErrorInvalidMemcpyDirection

#### hggcMemcpy2DArrayToArray

从 HGGC 数组 src 左上角起 hOffsetSrc 行、wOffsetSrc 字节处，将矩阵（height, width）复制到 HGGC 数组 dst 的 hOffsetDst 行、wOffsetDst 字节处。wOffsetDst + width 不得超过 dst 宽度；wOffsetSrc + width 不得超过 src 宽度。大多数用例表现为同步行为。

```c
hggcError_t hggcMemcpy2DArrayToArray (hggcArray_t dst,
                                      size_t wOffsetDst,
                                      size_t hOffsetDst,
                                      hggcArray_const_t src,
                                      size_t wOffsetSrc,
                                      size_t hOffsetSrc,
                                      size_t width,
                                      size_t height,
                                      hggcMemcpyKind kind = hggcMemcpyDeviceToDevice)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dst | in | 目标内存地址 |
| wOffsetDst | in | 目标起始 X 偏移（列，字节） |
| hOffsetDst | in | 目标起始 Y 偏移（行） |
| src | in | 源内存地址 |
| wOffsetSrc | in | 源起始 X 偏移（列，字节） |
| hOffsetSrc | in | 源起始 Y 偏移（行） |
| width | in | 矩阵传输宽度（列，字节） |
| height | in | 矩阵传输高度（行） |
| kind | in | 传输类型 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidMemcpyDirection

#### hggcMemcpy2DAsync

`hggcMemcpy2D` 的异步形态：相对主机异步，可能在复制完成前返回；可经非零流参数关联到流。设备版本仅处理设备到设备复制，不能传 local 或 shared 指针。注册要求同 `hggcMemcpy`。

```c
hggcError_t hggcMemcpy2DAsync (void* dst,
                               size_t dpitch,
                               const void* src,
                               size_t spitch,
                               size_t width,
                               size_t height,
                               hggcMemcpyKind kind,
                               hggcStream_t stream = 0)
```

参数同 `hggcMemcpy2D`，另加 `stream`（in，流标识符）。

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidPitchValue、hggcErrorInvalidMemcpyDirection

#### hggcMemcpy2DFromArrayAsync

从 HGGC 数组 src 的 hOffset 行、wOffset 字节处复制矩阵（height, width）到 dst。相对主机异步，可关联到流。注册要求同上。

```c
hggcError_t hggcMemcpy2DFromArrayAsync (void* dst,
                                        size_t dpitch,
                                        hggcArray_const_t src,
                                        size_t wOffset,
                                        size_t hOffset,
                                        size_t width,
                                        size_t height,
                                        hggcMemcpyKind kind,
                                        hggcStream_t stream = 0)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dst | in | 目标内存地址 |
| dpitch | in | 目标内存的步幅 |
| src | in | 源内存地址 |
| wOffset | in | 源起始 X 偏移（列，字节） |
| hOffset | in | 源起始 Y 偏移（行） |
| width | in | 矩阵传输宽度（列，字节） |
| height | in | 矩阵传输高度（行） |
| kind | in | 传输类型 |
| stream | in | 流标识符 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidPitchValue、hggcErrorInvalidMemcpyDirection

#### hggcMemcpy2DToArrayAsync

从 src 复制矩阵（height, width）到 HGGC 数组 dst 的 hOffset 行、wOffset 字节处。相对主机异步，可关联到流。注册要求同上。

```c
hggcError_t hggcMemcpy2DToArrayAsync (hggcArray_t dst,
                                      size_t wOffset,
                                      size_t hOffset,
                                      const void* src,
                                      size_t spitch,
                                      size_t width,
                                      size_t height,
                                      hggcMemcpyKind kind,
                                      hggcStream_t stream = 0)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dst | in | 目标内存地址 |
| wOffset | in | 目标起始 X 偏移（列，字节） |
| hOffset | in | 目标起始 Y 偏移（行） |
| src | in | 源内存地址 |
| spitch | in | 源内存的步幅 |
| width | in | 矩阵传输宽度（列，字节） |
| height | in | 矩阵传输高度（行） |
| kind | in | 传输类型 |
| stream | in | 流标识符 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidPitchValue、hggcErrorInvalidMemcpyDirection

#### hggcMemcpy3D

在两个 3D 对象之间复制数据。源/目标可位于主机内存、设备内存或 HGGC 数组，由 `hggcMemcpy3DParms` 结构体指定（使用前应初始化为 0）。结构体必须在 srcArray 与 srcPtr 中二选一、dstArray 与 dstPtr 中二选一；传入多个非零源或目标将返回错误。大多数场景表现为同步行为。

```c
hggcError_t hggcMemcpy3D (const hggcMemcpy3DParms* p)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| p | in | 3D 内存复制参数 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidPitchValue、hggcErrorInvalidMemcpyDirection

#### hggcMemcpy3DAsync

`hggcMemcpy3D` 的异步形态，可关联到流。设备版本仅处理设备到设备拷贝，不能传 local 或 shared 指针。

```c
hggcError_t hggcMemcpy3DAsync (const hggcMemcpy3DParms* p,
                               hggcStream_t stream = 0)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| p | in | 3D 内存复制参数 |
| stream | in | 流标识符 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidPitchValue、hggcErrorInvalidMemcpyDirection

#### hggcMemcpy3DPeer

根据 p 中指定的参数执行 3D 内存拷贝。注意：只有当传输的源或目标为主机内存时，此函数相对主机才是同步的。

```c
hggcError_t hggcMemcpy3DPeer (const hggcMemcpy3DPeerParms* p)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| p | in | 内存复制参数 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidDevice、hggcErrorInvalidPitchValue

#### hggcMemcpy3DPeerAsync

按 p 中参数执行一次 3D 内存拷贝（异步形态，标准默认流语义）。

```c
hggcError_t hggcMemcpy3DPeerAsync (const hggcMemcpy3DPeerParms* p,
                                   hggcStream_t stream = 0)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| p | in | 内存复制参数 |
| stream | in | 流标识符 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidDevice、hggcErrorInvalidPitchValue

#### hggcMemcpyAsync

`hggcMemcpy` 的异步形态：相对主机异步，可能在拷贝完成前返回；可关联到流。设备版本仅处理设备到设备拷贝，不能传 local 或 shared 指针。注册要求同 `hggcMemcpy`。

```c
hggcError_t hggcMemcpyAsync (void* dst,
                             const void* src,
                             size_t count,
                             hggcMemcpyKind kind,
                             hggcStream_t stream = 0)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dst | in | 目标内存地址 |
| src | in | 源内存地址 |
| count | in | 要复制的大小（字节） |
| kind | in | 传输类型 |
| stream | in | 流标识符 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidMemcpyDirection

#### hggcMemcpyFromSymbol

从 symbol 起始偏移 offset 字节处复制 count 字节到 dst。源与目标不得重叠。symbol 是全局或常量内存空间变量。kind 可为 `hggcMemcpyDeviceToHost`/`DeviceToDevice`/`Default`。大多数场景表现为同步行为。

```c
hggcError_t hggcMemcpyFromSymbol (void* dst,
                                  const void* symbol,
                                  size_t count,
                                  size_t offset = 0,
                                  hggcMemcpyKind kind = hggcMemcpyDeviceToHost)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dst | in | 目标内存地址 |
| symbol | in | 设备符号地址 |
| count | in | 要复制的大小（字节） |
| offset | in | 相对 symbol 起始处的偏移（字节） |
| kind | in | 传输类型 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidSymbol、hggcErrorInvalidMemcpyDirection、hggcErrorNoKernelImageForDevice

#### hggcMemcpyFromSymbolAsync

`hggcMemcpyFromSymbol` 的异步形态，可关联到流。

```c
hggcError_t hggcMemcpyFromSymbolAsync (void* dst,
                                       const void* symbol,
                                       size_t count,
                                       size_t offset,
                                       hggcMemcpyKind kind,
                                       hggcStream_t stream = 0)
```

参数同 `hggcMemcpyFromSymbol`，另加 `stream`（in，流标识符）。

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidSymbol、hggcErrorInvalidMemcpyDirection、hggcErrorNoKernelImageForDevice

#### hggcMemcpyPeer

将一个设备上的内存复制到另一个设备。大多数场景表现为同步行为。

```c
hggcError_t hggcMemcpyPeer (void* dst,
                            int dstDevice,
                            const void* src,
                            int srcDevice,
                            size_t count)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dst | in | 目标设备指针 |
| dstDevice | in | 目标设备 |
| src | in | 源设备指针 |
| srcDevice | in | 源设备 |
| count | in | 内存复制大小（字节） |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidDevice

#### hggcMemcpyPeerAsync

`hggcMemcpyPeer` 的异步形态：相对主机以及其他设备上的所有工作都是异步的，标准默认流语义。

```c
hggcError_t hggcMemcpyPeerAsync (void* dst,
                                 int dstDevice,
                                 const void* src,
                                 int srcDevice,
                                 size_t count,
                                 hggcStream_t stream = 0)
```

参数同 `hggcMemcpyPeer`，另加 `stream`（in，流标识符）。

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidDevice

#### hggcMemcpyToSymbol

从 src 复制 count 字节到 symbol 起始偏移 offset 字节处。源与目标不得重叠。symbol 是全局或常量内存空间变量。大多数场景表现为同步行为。

```c
hggcError_t hggcMemcpyToSymbol (const void* symbol,
                                const void* src,
                                size_t count,
                                size_t offset = 0,
                                hggcMemcpyKind kind = hggcMemcpyHostToDevice)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| symbol | in | 设备符号地址 |
| src | in | 源内存地址 |
| count | in | 要复制的大小（字节） |
| offset | in | 相对 symbol 起始处的偏移（字节） |
| kind | in | 传输类型 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidSymbol、hggcErrorInvalidMemcpyDirection、hggcErrorNoKernelImageForDevice

#### hggcMemcpyToSymbolAsync

`hggcMemcpyToSymbol` 的异步形态。

```c
hggcError_t hggcMemcpyToSymbolAsync (const void* symbol,
                                     const void* src,
                                     size_t count,
                                     size_t offset,
                                     hggcMemcpyKind kind,
                                     hggcStream_t stream = 0)
```

参数同 `hggcMemcpyToSymbol`，另加 `stream`（in，流标识符）。

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidSymbol、hggcErrorInvalidMemcpyDirection、hggcErrorNoKernelImageForDevice

#### hggcMemcpyArrayToArray

从 HGGC 数组 src 的 hOffsetSrc 行、wOffsetSrc 字节处，向 HGGC 数组 dst 的 hOffsetDst 行、wOffsetDst 字节处复制 count 个元素。kind 取值与 `hggcMemcpyDefault` 约束同 `hggcMemcpy`。

```c
hggcError_t hggcMemcpyArrayToArray (hggcArray_t dst,
                                    size_t wOffsetDst,
                                    size_t hOffsetDst,
                                    hggcArray_const_t src,
                                    size_t wOffsetSrc,
                                    size_t hOffsetSrc,
                                    size_t count,
                                    hggcMemcpyKind kind = hggcMemcpyDeviceToDevice)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dst | in | 目标数组 |
| wOffsetDst | in | 目标起始 X 偏移（列，字节） |
| hOffsetDst | in | 目标起始 Y 偏移（行） |
| src | in | 源数组 |
| wOffsetSrc | in | 源起始 X 偏移（列，字节） |
| hOffsetSrc | in | 源起始 Y 偏移（行） |
| count | in | 要复制的元素数量 |
| kind | in | 传输类型 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidMemcpyDirection

#### hggcMemcpyFromArrayAsync

从 HGGC 数组 src 的 hOffset 行、wOffset 字节处，向 dst 复制 count 个元素。相对主机异步，可关联到流；kind 为 `hggcMemcpyHostToDevice` 或 `hggcMemcpyDeviceToHost` 且流非零时，该拷贝可能与其他流中的操作并发执行。kind 取值约束同 `hggcMemcpy`。

```c
hggcError_t hggcMemcpyFromArrayAsync (void* dst,
                                      hggcArray_const_t src,
                                      size_t wOffset,
                                      size_t hOffset,
                                      size_t count,
                                      hggcMemcpyKind kind,
                                      hggcStream_t stream = 0)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dst | in | 目标内存地址 |
| src | in | 源数组 |
| wOffset | in | 源起始 X 偏移（列，字节） |
| hOffset | in | 源起始 Y 偏移（行） |
| count | in | 要复制的元素数量 |
| kind | in | 传输类型 |
| stream | in | 流标识符 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidMemcpyDirection

#### hggcMemcpyToArrayAsync

从 src 向 HGGC 数组 dst 的 hOffset 行、wOffset 字节处复制 count 个元素。相对主机异步，可关联到流；kind 为 `hggcMemcpyHostToDevice` 或 `hggcMemcpyDeviceToHost` 且流非零时，可能与其他流并发执行。

```c
hggcError_t hggcMemcpyToArrayAsync (hggcArray_t dst,
                                    size_t wOffset,
                                    size_t hOffset,
                                    const void* src,
                                    size_t count,
                                    hggcMemcpyKind kind,
                                    hggcStream_t stream = 0)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dst | in | 目标数组 |
| wOffset | in | 目标起始 X 偏移（列，字节） |
| hOffset | in | 目标起始 Y 偏移（行） |
| src | in | 源内存地址 |
| count | in | 要复制的元素数量 |
| kind | in | 传输类型 |
| stream | in | 流标识符 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidMemcpyDirection

### 内存填充

本模块提供**内存填充（memset）**接口，支持一维/二维/三维设备内存的同步与异步填充。

| 函数 | 用途 |
|------|------|
| `hggcMemset` | 用常量字节值填充内存前 count 字节 |
| `hggcMemset2D` | 将矩阵（height, width）设为指定值 |
| `hggcMemset2DAsync` | 异步填充二维设备内存 |
| `hggcMemset3D` | 将 3D 数组每个元素初始化为指定值 |
| `hggcMemset3DAsync` | 异步填充三维设备内存 |
| `hggcMemsetAsync` | 异步以字节值填充设备内存 |

#### hggcMemset

用常量字节值 value 填充 devPtr 的前 count 字节。注意：除非 devPtr 指向页锁定主机内存，否则此函数相对主机是异步的（同步细节见"API 同步行为"节）。

```c
hggcError_t hggcMemset (void* devPtr, int value, size_t count)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| devPtr | in | 指向设备内存的指针 |
| value | in | 每个字节要设置的值 |
| count | in | 要设置的大小（字节） |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcMemset2D

将 devPtr 指向的矩阵（height, width）设为 value。pitch 为 2D 数组字节宽度（含行尾填充）；pitch 取 `hggcMallocPitch()` 返回的值时性能最佳。

```c
hggcError_t hggcMemset2D (void* devPtr,
                          size_t pitch,
                          int value,
                          size_t width,
                          size_t height)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| devPtr | in | 指向 2D 设备内存的指针 |
| pitch | in | 2D 设备内存的步幅（字节） |
| value | in | 每个字节要设置的值 |
| width | in | 矩阵设置宽度（列，字节） |
| height | in | 矩阵设置高度（行） |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcMemset2DAsync

`hggcMemset2D` 的异步形态：相对主机异步，可关联到流。设备版本仅处理设备到设备操作，不能传 local 或 shared 指针。

```c
hggcError_t hggcMemset2DAsync (void* devPtr,
                               size_t pitch,
                               int value,
                               size_t width,
                               size_t height,
                               hggcStream_t stream = 0)
```

参数同 `hggcMemset2D`，另加 `stream`（in，流标识符）。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcMemset3D

将 3D 数组每个元素初始化为 value，对象由 pitchedDevPtr 定义：pitch 字段为 3D 数组内存宽度（字节，含行尾填充）；xsize 为每行逻辑宽度（字节）；ysize 为每个 2D 切片高度（行）。pitchedDevPtr 由 `hggcMalloc3D()` 分配时性能最佳。

```c
hggcError_t hggcMemset3D (hggcPitchedPtr pitchedDevPtr,
                          int value,
                          hggcExtent extent)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pitchedDevPtr | in | 指向 pitched 设备内存的指针 |
| value | in | 每个字节要设置的值 |
| extent | in | 设备内存设置范围参数 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcMemset3DAsync

`hggcMemset3D` 的异步形态：相对主机异步，可关联到流。设备版本限制同 `hggcMemset2DAsync`。

```c
hggcError_t hggcMemset3DAsync (hggcPitchedPtr pitchedDevPtr,
                               int value,
                               hggcExtent extent,
                               hggcStream_t stream = 0)
```

参数同 `hggcMemset3D`，另加 `stream`（in，流标识符）。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcMemsetAsync

`hggcMemset` 的异步形态：始终相对主机异步，可关联到流。设备版本限制同上。

```c
hggcError_t hggcMemsetAsync (void* devPtr,
                             int value,
                             size_t count,
                             hggcStream_t stream = 0)
```

参数同 `hggcMemset`，另加 `stream`（in，流标识符）。

错误码：hggcSuccess、hggcErrorInvalidValue

### 流有序内存分配器

本模块提供**流有序内存池（Memory Pool）**接口。内存池允许在流中异步分配和释放设备内存，避免传统 malloc/free 的同步开销，提升高频分配场景下的性能。

| 函数 | 用途 |
|------|------|
| `hggcDeviceGetDefaultMemPool` | 返回设备的默认内存池 |
| `hggcDeviceGetMemPool` | 获取设备当前使用的内存池 |
| `hggcDeviceSetMemPool` | 设置设备当前使用的内存池 |
| `hggcFreeAsync` | 以流顺序语义释放内存 |
| `hggcMallocAsync` | 以流顺序语义分配内存 |
| `hggcMallocFromPoolAsync` | 以流顺序语义从指定内存池分配内存 |
| `hggcMemGetDefaultMemPool` | 返回给定位置和分配类型的默认内存池 |
| `hggcMemGetMemPool` | 获取给定内存位置和分配类型的当前内存池 |
| `hggcMemPoolCreate` | 创建内存池 |
| `hggcMemPoolDestroy` | 销毁指定的内存池 |
| `hggcMemPoolExportPointer` | 导出数据以便进程间共享内存池分配 |
| `hggcMemPoolExportToShareableHandle` | 将内存池导出为请求的句柄类型 |
| `hggcMemPoolGetAccess` | 返回某设备对该内存池的可访问性 |
| `hggcMemPoolGetAttribute` | 获取内存池的属性 |
| `hggcMemPoolImportFromShareableHandle` | 从共享句柄导入内存池 |
| `hggcMemPoolImportPointer` | 从其他进程导入一个内存池分配 |
| `hggcMemPoolSetAccess` | 控制设备之间对内存池的可见性 |
| `hggcMemPoolSetAttribute` | 设置内存池的属性 |
| `hggcMemPoolTrimTo` | 尝试将内存释放回操作系统 |
| `hggcMemSetMemPool` | 为内存位置和分配类型设置当前内存池 |

#### hggcDeviceGetDefaultMemPool

返回设备的默认内存池（包含来自该设备的设备内存）。

```c
__host__ hggcError_t hggcDeviceGetDefaultMemPool (hggcMemPool_t* memPool,
                                                  int device)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| memPool | out | 用于返回的内存池 |
| device | in | 设备编号 |

错误码：hggcSuccess、hggcErrorInvalidDevice、hggcErrorInvalidValue、hggcErrorNotSupported

#### hggcDeviceGetMemPool

返回提供给此设备的 `hggcDeviceSetMemPool` 的最后一个池；从未调用过则返回设备默认内存池。默认情况下当前内存池即默认内存池，否则返回的池必须经 `hgDeviceSetMemPool` 或 `hggcDeviceSetMemPool` 设置。

```c
__host__ hggcError_t hggcDeviceGetMemPool (hggcMemPool_t* memPool, int device)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| memPool | out | 用于返回的内存池 |
| device | in | 设备编号 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorNotSupported

#### hggcDeviceSetMemPool

内存池必须对指定设备是局部的。除非 `hggcMallocAsync` 调用中显式指定内存池，否则它从所提供流之设备的当前内存池分配。默认当前内存池即设备默认内存池。

```c
__host__ hggcError_t hggcDeviceSetMemPool (int device, hggcMemPool_t memPool)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| device | in | 设备编号 |
| memPool | in | 内存池 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidDevice、hggcErrorNotSupported

#### hggcFreeAsync

在 `hStream` 中插入一次释放操作。流执行到该释放操作之后不得再访问该分配；该 API 返回后再访问该内存（PPU 启动或其他操作）行为未定义。流捕获期间此函数创建释放节点，必须传入图分配的地址。

```c
hggcError_t hggcFreeAsync (void* devPtr, hggcStream_t hStream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| devPtr | in | 要释放的设备指针 |
| hStream | in | 用于建立流顺序承诺的流 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorNotSupported

#### hggcMallocAsync

在 `hStream` 中插入一次分配操作。指针立即经 `*devPtr` 返回，但分配操作完成前不得访问。分配来自与该流所关联设备对应的内存池：

- 设备默认内存池包含来自该设备的设备内存。
- 基本流顺序允许后续提交到同一流的工作使用该分配；跨流可用流查询、流同步及 HGGC 事件保证分配先于其他流的工作完成。
- 流捕获期间创建分配节点：分配由图而非内存池持有，内存池属性用于设置节点创建参数。

```c
hggcError_t hggcMallocAsync (void** devPtr, size_t size, hggcStream_t hStream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| devPtr | out | 用于返回的设备指针 |
| size | in | 要分配的字节数 |
| hStream | in | 建立流顺序契约并指定分配所用内存池的流 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorNotSupported

#### hggcMallocFromPoolAsync

在 `stream` 中插入一次分配操作，从**指定**内存池分配。指针立即返回，分配完成前不得访问。内存池可来自与 `stream` 不同的设备。流顺序与流捕获语义同 `hggcMallocAsync`。

```c
hggcError_t hggcMallocFromPoolAsync (void** ptr,
                                     size_t size,
                                     hggcMemPool_t memPool,
                                     hggcStream_t stream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| ptr | out | 用于返回的设备指针 |
| size | in | 要分配的字节数 |
| memPool | in | 要从中分配的内存池 |
| stream | in | 建立流顺序语义的流 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorNotSupported

#### hggcMemGetDefaultMemPool

返回给定位置和分配类型的默认内存池。location 可为 `hggcMemLocationTypeDevice`/`Host`/`HostNuma`；type 可为 `hggcMemAllocationTypePinned`/`Managed`。type 为 `Managed` 时 location 类型也可为 `hggcMemLocationTypeNone`（托管内存池无首选位置）。其他组合返回 `hggcErrorInvalidValue`。

```c
hggcError_t hggcMemGetDefaultMemPool (hggcMemPool_t* memPool,
                                      hggcMemLocation* location,
                                      hggcMemAllocationType type)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| memPool | out | 用于返回的内存池 |
| location | in | 内存位置 |
| type | in | 分配类型 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorNotSupported

#### hggcMemGetMemPool

location/type 的合法组合同 `hggcMemGetDefaultMemPool`，其他组合返回 `hggcErrorInvalidValue`。返回此前经 `hggcMemSetMemPool` 或 `hggcDeviceSetMemPool` 为该位置与分配类型设置的最后一个内存池；从未设置则返回该位置的默认内存池（设备位置可经 `hggcMemGetDefaultMemPool` 获取，否则必须已经 `hggcDeviceSetMemPool` 设置）。

```c
hggcError_t hggcMemGetMemPool (hggcMemPool_t* memPool,
                               hggcMemLocation* location,
                               hggcMemAllocationType type)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| memPool | out | 用于返回的内存池 |
| location | in | 内存位置 |
| type | in | 分配类型 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcMemPoolCreate

创建 HGGC 内存池，在 `memPool` 返回句柄。`poolProps` 决定内存池属性（后备设备与 IPC 能力等）：

- 不针对特定 NUMA 节点的主机内存池：`hggcMemPoolProps::location::type` 设为 `hggcMemLocationTypeHost`，`location::id` 被忽略；此类池不支持 IPC，`handleTypes` 必须为 0，否则返回 `hggcErrorInvalidValue`。
- 针对特定主机 NUMA 节点：`location::type` 设为 `hggcMemLocationTypeHostNuma` 且 `location::id` 指定 NUMA 节点 ID。使用 `hggcMemLocationTypeHostNumaCurrent` 返回 `hggcErrorInvalidValue`。
- 默认可访问性：设备内存池可从其分配所在设备访问；Host/HostNuma 池默认可访问性来自主机 CPU。
- `hggcMemPoolProps::maxSize` 非零可控制池最大大小；为 0 时默认与系统相关的值。
- 使用 fabric 句柄共享内存须确保：(1) 驱动创建的字符设备已列于 `/proc/devices`；(2) 启动应用的用户至少可访问一个 IMEX channel 文件。导出方与导入方进程被授予同一 IMEX channel 时可安全共享内存。IMEX channel 安全模型以用户为单位（用户可访问一个有效 channel，则该用户所有进程可共享）。此时 `handleTypes` 必须设为 `hggcMemHandleTypeNone`。
- 托管内存池：`location` 视为所有分配的首选位置，也可设 `hggcMemLocationTypeNone` 表示无首选位置；`maxSize` 必须为 0；`usage` 应为 0（不支持托管内存解压）；系统中所有设备 `concurrentManagedAccess` 必须非零，否则返回 `hggcErrorNotSupported`。

```c
hggcError_t hggcMemPoolCreate (hggcMemPool_t* memPool,
                               const hggcMemPoolProps* poolProps)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| memPool | out | 用于返回的内存池 |
| poolProps | in | 内存池属性 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorNotSupported

#### hggcMemPoolDestroy

若该池尚有未释放的指针或调用时存在未完成的释放操作，函数立即返回，资源在不再存在未完成分配后自动释放。销毁设备当前内存池会将设备默认池设为当前池。设备默认内存池不能被销毁。

```c
hggcError_t hggcMemPoolDestroy (hggcMemPool_t memPool)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| memPool | in | 要销毁的内存池 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcMemPoolExportPointer

构造 `exportData`，用于从已共享的内存池中共享某个特定分配。接收进程用 `hggcMemPoolImportPointer` 导入。该数据不是句柄，可通过任何 IPC 机制共享。

```c
hggcError_t hggcMemPoolExportPointer (hggcMemPoolPtrExportData* exportData,
                                      void* ptr)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| exportData | out | 用于返回的导出数据 |
| ptr | in | 指向正在导出的内存的指针 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcMemPoolExportToShareableHandle

对具备 IPC 能力的内存池，创建操作系统句柄以便与另一进程共享。接收进程用 `hggcMemPoolImportFromShareableHandle` 转换为内存池，随后可用 `hggcMemPoolExportPointer`/`hggcMemPoolImportPointer` 共享单个指针。句柄形式与传输方式由句柄类型定义。要创建 IPC 能力的内存池，创建时 `hggcMemAllocationHandleType` 须不为 `hggcMemHandleTypeNone`。

```c
hggcError_t hggcMemPoolExportToShareableHandle (void* shareableHandle,
                                                hggcMemPool_t memPool,
                                                hggcMemAllocationHandleType handleType,
                                                unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| shareableHandle | out | 用于返回的共享句柄 |
| memPool | in | 要导出的内存池 |
| handleType | in | 要创建的句柄类型 |
| flags | in | 必须为 0 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcMemPoolGetAccess

返回从指定位置访问该内存池内存的可访问性。

```c
hggcError_t hggcMemPoolGetAccess (hggcMemAccessFlags* flags,
                                  hggcMemPool_t memPool,
                                  hggcMemLocation* location)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| flags | out | 从指定位置访问该内存池的可访问性 |
| memPool | in | 被查询的内存池 |
| location | in | 访问该内存池的位置 |

#### hggcMemPoolGetAttribute

支持的属性：

- `hggcMemPoolAttrReleaseThreshold`（= `uint64_t`）：尝试将内存释放回操作系统之前保留的预留内存量（字节）。池内存超过该阈值时，分配器在下一次对流/事件/上下文同步的调用时尝试释放回 OS。（默认 0）
- `hggcMemPoolReuseFollowEventDependencies`（= `int`）：允许 `hggcMallocAsync` 使用另一流中异步释放的内存，只要分配流对释放操作存在流顺序依赖（HGGC 事件和空流交互可创建所需依赖）。（默认启用）
- `hggcMemPoolReuseAllowOpportunistic`（= `int`）：释放与分配之间无依赖时，允许复用已完成的释放。（默认启用）
- `hggcMemPoolReuseAllowInternalDependencies`（= `int`）：允许 `hggcMallocAsync` 插入新的流依赖以建立复用 `hggcFreeAsync` 内存所需的流顺序。（默认启用）
- `hggcMemPoolAttrReservedMemCurrent`（= `uint64_t`）：池当前已分配的后备内存量。
- `hggcMemPoolAttrReservedMemHigh`（= `uint64_t`）：自上次重置以来后备内存高水位。
- `hggcMemPoolAttrUsedMemCurrent`（= `uint64_t`）：应用当前正在使用的池内存量。
- `hggcMemPoolAttrUsedMemHigh`（= `uint64_t`）：自上次重置以来使用量高水位。

以下属性也可在导入的内存池和默认内存池上查询：

- `hggcMemPoolAttrAllocationType`（= `hggcMemAllocationType`）：池的分配类型。
- `hggcMemPoolAttrExportHandleTypes`（= `hggcMemAllocationHandleType`）：可用的导出句柄类型；导入的池始终为 `hggcMemHandleTypeNone`（无法再导出）。
- `hggcMemPoolAttrLocationId`（= `int`）：位置 ID；位置类型为 `hggcMemLocationTypeInvisible` 时为 `hggcInvalidDeviceId`。
- `hggcMemPoolAttrLocationType`（= `hggcMemLocationType`）：位置类型；设备对导入进程不可见或经 fabric 句柄跨节点导入的池为 `hggcMemLocationTypeInvisible`。
- `hggcMemPoolAttrMaxPoolSize`（= `uint64_t`）：池最大大小（字节）；因对齐可能高于创建时传入值，0 表示无上限；`hggcMemAllocationTypeManaged` 和 IPC 导入的池该值取决于系统。
- `hggcMemPoolAttrHwDecompressEnabled`（= `int`）：是否启用硬件解压缩。

```c
hggcError_t hggcMemPoolGetAttribute (hggcMemPool_t memPool,
                                     hggcMemPoolAttr attr,
                                     void* value)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| memPool | in | 内存池 |
| attr | in | 要获取的属性 |
| value | in | 取回的值 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcMemPoolImportFromShareableHandle

从共享句柄导入内存池。可用 `hggcMemPoolImportPointer` 从导入的池中导入特定分配。导入的池不支持创建新分配，因此不能用于 `hggcDeviceSetMemPool` 或 `hggcMallocFromPoolAsync`。

```c
hggcError_t hggcMemPoolImportFromShareableHandle (hggcMemPool_t* memPool,
                                                  void* shareableHandle,
                                                  hggcMemAllocationHandleType handleType,
                                                  unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| memPool | out | 用于返回的内存池 |
| shareableHandle | in | 共享句柄 |
| handleType | in | 要导入的句柄类型 |
| flags | in | 必须为 0 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcMemPoolImportPointer

在 `*ptr` 中返回导入内存的指针。导出进程中的分配完成前不得访问导入内存；导出进程释放之前，所有导入进程须先释放该导入内存。指针可用 `hggcFree` 或 `hggcFreeAsync` 释放；用 `hggcFreeAsync` 时，导出进程执行释放前导入进程上的释放必须完成。只要导出进程用于 `hggcFreeAsync` 的流对导入进程的 `hggcFreeAsync` 存在流依赖，导出进程可在其流中 `hggcFreeAsync` 完成前调用 `hggcFreeAsync` API。

```c
hggcError_t hggcMemPoolImportPointer (void** ptr,
                                      hggcMemPool_t memPool,
                                      hggcMemPoolPtrExportData* exportData)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| ptr | out | 用于返回的导入指针 |
| memPool | in | 导入的内存池 |
| exportData | in | 导出数据 |

错误码：HGGC_ERROR_INVALID_VALUE、HGGC_ERROR_NOT_INITIALIZED、HGGC_ERROR_OUT_OF_MEMORY

#### hggcMemPoolSetAccess

设置内存池的访问规则。

```c
hggcError_t hggcMemPoolSetAccess (hggcMemPool_t memPool,
                                  const hggcMemAccessDesc* descList,
                                  size_t count)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| memPool | in | 内存池 |
| descList | in | 访问描述符数组 |
| count | in | 描述符数量 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcMemPoolSetAttribute

支持的属性（`ReleaseThreshold` 与三个 `Reuse*` 语义同 `hggcMemPoolGetAttribute`，均可写）：

- `hggcMemPoolAttrReleaseThreshold`（= `uint64_t`）：释放阈值（默认 0）。
- `hggcMemPoolReuseFollowEventDependencies`（= `int`）：默认启用。
- `hggcMemPoolReuseAllowOpportunistic`（= `int`）：默认启用。
- `hggcMemPoolReuseAllowInternalDependencies`（= `int`）：默认启用。
- `hggcMemPoolAttrReservedMemHigh`（= `uint64_t`）：重置后备内存高水位；设为非零值非法。
- `hggcMemPoolAttrUsedMemHigh`（= `uint64_t`）：重置已用内存高水位；设为非零值非法。

```c
hggcError_t hggcMemPoolSetAttribute (hggcMemPool_t memPool,
                                     hggcMemPoolAttr attr,
                                     void* value)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| memPool | in | 内存池 |
| attr | in | 要修改的属性 |
| value | in | 指向要赋值的值的指针 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcMemPoolTrimTo

将内存释放回操作系统，直到池预留字节数少于 `minBytesToKeep`，或分配器已没有可安全释放的内存。分配器不能释放为未完成异步分配提供后备的 OS 分配；OS 分配粒度可能与用户分配不同。尚未释放的分配计为未完成；已异步释放但完成情况尚未在主机端观测到（如经同步）的分配也可计为未完成。

```c
hggcError_t hggcMemPoolTrimTo (hggcMemPool_t memPool, size_t minBytesToKeep)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| memPool | in | 内存池 |
| minBytesToKeep | in | 池预留内存少于此值时 TrimTo 为空操作；否则操作后保证至少预留此字节数 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcMemSetMemPool

为内存位置和分配类型设置当前内存池。location/type 合法组合同 `hggcMemGetDefaultMemPool`。`location` 应与该池的位置相同（类型或索引不匹配返回 `hggcErrorInvalidValue`）；池类型也应与 `type` 匹配，否则返回 `hggcErrorInvalidValue`。

```c
hggcError_t hggcMemSetMemPool (hggcMemLocation* location,
                               hggcMemAllocationType type,
                               hggcMemPool_t memPool)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| location | in | 内存位置 |
| type | in | 分配类型 |
| memPool | in | 内存池 |

错误码：hggcSuccess、hggcErrorInvalidValue

比赛关联：KV cache、激活缓冲等高频分配场景用 `hggcMallocAsync`/`hggcFreeAsync` 消除同步 malloc/free 的隐式同步开销；配合 `hggcMemPoolAttrReleaseThreshold` 调高阈值可避免内存反复归还 OS 造成的抖动，直接利好吞吐与 TTFT 稳定性。

## 流与事件

本节涵盖异步执行的核心原语：流（Stream）的创建与同步、事件（Event）的记录与等待。流是 HGGC 中的异步执行队列——同一流中的操作按 FIFO 顺序执行，不同流中的操作可并行；事件是轻量级同步原语，用于标记流中的时间点、测量 PPU 操作耗时、建立流间依赖关系。

### 流与事件管理

| 函数 | 用途 |
|------|------|
| `hggcEventCreate` | 创建一个事件对象 |
| `hggcEventCreateWithFlags` | 使用指定的标志创建一个事件对象 |
| `hggcEventDestroy` | 销毁一个事件对象 |
| `hggcEventElapsedTime` | 计算两个事件之间经过的时间 |
| `hggcEventQuery` | 查询事件的状态 |
| `hggcEventRecord` | 在调用此函数时捕获流的内容到 `event` 中 |
| `hggcEventRecordWithFlags` | 使用指定标志记录事件 |
| `hggcEventSynchronize` | 等待一个事件完成 |
| `hggcIpcGetEventHandle` | 获取已分配事件的进程间句柄 |
| `hggcIpcOpenEventHandle` | 打开进程间事件句柄以供当前进程使用 |
| `hggcStreamAddCallback` | 向计算流添加回调 |
| `hggcStreamAttachMemAsync` | 异步地将内存附加到流 |
| `hggcStreamBeginCapture` | 开始在流上捕获图 |
| `hggcStreamBeginCaptureToGraph` | 开始在流上捕获图到现有图中 |
| `hggcStreamCopyAttributes` | 将属性从源流复制到目标流 |
| `hggcStreamCreate` | 在调用主机线程的当前上下文中创建一个新的异步流 |
| `hggcStreamCreateWithFlags` | 使用指定标志创建异步流 |
| `hggcStreamCreateWithPriority` | 以指定的优先级创建异步流 |
| `hggcStreamDestroy` | 销毁并清理异步流 |
| `hggcStreamEndCapture` | 结束流上的捕获，返回捕获的图 |
| `hggcStreamGetAttribute` | 查询流属性 |
| `hggcStreamGetCaptureInfo` | 查询流的捕获状态 |
| `hggcStreamGetFlags` | 查询流的标志 |
| `hggcStreamGetId` | 查询流的 ID |
| `hggcStreamGetPriority` | 查询流的优先级 |
| `hggcStreamIsCapturing` | 返回流的捕获状态 |
| `hggcStreamQuery` | 查询异步流的完成状态 |
| `hggcStreamSetAttribute` | 设置流属性 |
| `hggcStreamSynchronize` | 等待流任务完成 |
| `hggcStreamUpdateCaptureDependencies` | 更新正在捕获的流中的依赖项集合 |
| `hggcStreamWaitEvent` | 使计算流等待事件 |
| `hggcThreadExchangeStreamCaptureMode` | 交换线程的流捕获交互模式 |

#### hggcEventCreate

使用 `hggcEventDefault` 为当前设备创建一个事件对象。

```c
hggcError_t hggcEventCreate (hggcEvent_t* event)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| event | in | 新创建的事件 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorLaunchFailure、hggcErrorMemoryAllocation

#### hggcEventCreateWithFlags

使用指定标志为当前设备创建事件对象。有效标志：

- `hggcEventDefault`：默认事件创建标志。
- `hggcEventBlockingSync`：事件使用阻塞同步。用 `hggcEventSynchronize()` 等待此类事件的主机线程将阻塞到事件实际完成。
- `hggcEventDisableTiming`：事件不记录计时数据。与 `hggcStreamWaitEvent()`、`hggcEventQuery()` 配合时，指定此标志（且不指定 `hggcEventBlockingSync`）的事件提供最佳性能。
- `hggcEventInterprocess`：事件可被 `hggcIpcGetEventHandle()` 用作进程间事件，必须与 `hggcEventDisableTiming` 一起指定。

```c
hggcError_t hggcEventCreateWithFlags (hggcEvent_t* event, unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| event | in | 新创建的事件 |
| flags | in | 新事件的标志 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorLaunchFailure、hggcErrorMemoryAllocation

#### hggcEventDestroy

销毁事件。事件可在完成之前销毁（`hggcEventQuery()` 返回 `hggcErrorNotReady` 时）——调用不阻塞，关联资源在完成时自动异步释放。

```c
hggcError_t hggcEventDestroy (hggcEvent_t event)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| event | in | 要销毁的事件 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidResourceHandle、hggcErrorLaunchFailure

#### hggcEventElapsedTime

计算两个事件之间经过的时间（毫秒，分辨率约 0.5 微秒）。此 API 不保证返回待处理工作的最新错误，仅用于计算时间；轮询事件完成应改用 `hggcEventQuery`。若任一事件最后记录在非 NULL 流中，测得时间可能大于预期（即使使用相同流句柄）——`hggcEventRecord()` 是异步的，两个被测事件之间可能插入任意数量的其他流操作。任一事件尚未调用 `hggcEventRecord()` 时返回 `hggcErrorInvalidResourceHandle`；已记录但未完成（`hggcEventQuery()` 返回 `hggcErrorNotReady`）时返回 `hggcErrorNotReady`；任一事件以 `hggcEventDisableTiming` 创建时返回 `hggcErrorInvalidResourceHandle`。

```c
hggcError_t hggcEventElapsedTime (float* ms, hggcEvent_t start, hggcEvent_t end)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| ms | in | 开始和结束之间的时间（毫秒） |
| start | in | 开始事件 |
| end | in | 结束事件 |

错误码：hggcSuccess、hggcErrorNotReady、hggcErrorInvalidValue、hggcErrorInvalidResourceHandle、hggcErrorLaunchFailure、hggcErrorUnknown

#### hggcEventQuery

查询事件当前捕获的所有工作的状态。全部完成返回 `hggcSuccess`；有未完成返回 `hggcErrorNotReady`。就统一内存而言，返回 `hggcSuccess` 等同于已调用 `hggcEventSynchronize()`。

```c
hggcError_t hggcEventQuery (hggcEvent_t event)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| event | in | 要查询的事件 |

错误码：hggcSuccess、hggcErrorNotReady、hggcErrorInvalidValue、hggcErrorInvalidResourceHandle、hggcErrorLaunchFailure

#### hggcEventRecord

在调用时捕获流的内容到 `event` 中。`event` 与流必须在同一 HGGC 上下文。`hggcEventQuery()`、`hggcStreamWaitEvent()` 等随后检查/等待捕获的工作完成；此调用后对流的使用不会修改 `event`。捕获内容的默认行为见"流同步行为"节。可在同一事件上多次调用，覆盖先前捕获的状态；其他 API（如 `hggcStreamWaitEvent()`）在调用时使用最近捕获的状态，不受后续 `hggcEventRecord()` 影响。首次调用 `hggcEventRecord()` 之前事件代表空工作集，例如 `hggcEventQuery()` 将返回 `hggcSuccess`。

```c
hggcError_t hggcEventRecord (hggcEvent_t event, hggcStream_t stream = 0)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| event | in | 要记录的事件 |
| stream | in | 记录事件的流 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidResourceHandle、hggcErrorLaunchFailure

#### hggcEventRecordWithFlags

`hggcEventRecord` 的带标志形态，捕获语义相同。flags：

- `hggcEventRecordDefault`：默认事件记录标志。
- `hggcEventRecordExternal`：执行流捕获时，事件作为外部事件节点捕获在图中。

```c
hggcError_t hggcEventRecordWithFlags (hggcEvent_t event,
                                      hggcStream_t stream = 0,
                                      unsigned int flags = 0)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| event | in | 要记录的事件 |
| stream | in | 记录事件的流 |
| flags | in | 操作参数（见上文） |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidResourceHandle、hggcErrorLaunchFailure

#### hggcEventSynchronize

等待直到事件当前捕获的所有工作完成。等待 `hggcEventBlockingSync` 标志创建的事件时，CPU 线程阻塞直到设备完成；未设该标志时 CPU 线程自旋等待（spin-wait）。

```c
hggcError_t hggcEventSynchronize (hggcEvent_t event)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| event | in | 要等待的事件 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidResourceHandle、hggcErrorLaunchFailure

#### hggcIpcGetEventHandle

将先前分配的事件导出为进程间句柄。事件必须以 `hggcEventInterprocess` + `hggcEventDisableTiming` 标志创建。句柄可复制到其他进程并用 `hggcIpcOpenEventHandle` 打开，实现不同进程 PPU 工作间的高效硬件同步。导入进程打开后，任一进程可用 `hggcEventRecord`、`hggcEventSynchronize`、`hggcStreamWaitEvent`、`hggcEventQuery`。导出事件经 `hggcEventDestroy` 释放后再操作导入事件，行为未定义。可用 `hggcDevAttrIpcEventSupport` 调用 `hggcDeviceGetAttribute` 测试 IPC 能力。

```c
__host__ hggcError_t hggcIpcGetEventHandle (hggcIpcEventHandle_t* handle,
                                            hggcEvent_t event)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| handle | out | 用户分配的 `hggcIpcEventHandle`，返回不透明事件句柄 |
| event | in | 以 `hggcEventInterprocess` 和 `hggcEventDisableTiming` 标志分配的事件 |

错误码：hggcSuccess、hggcErrorInvalidResourceHandle、hggcErrorMemoryAllocation、hggcErrorMapBufferObjectFailed、hggcErrorNotSupported、hggcErrorInvalidValue

#### hggcIpcOpenEventHandle

打开另一进程 `hggcIpcGetEventHandle` 导出的事件句柄。返回的 `hggcEvent_t` 行为类似以 `hggcEventDisableTiming` 本地创建的事件，必须用 `hggcEventDestroy` 释放。导出事件被释放后操作导入事件行为未定义。

```c
__host__ hggcError_t hggcIpcOpenEventHandle (hggcEvent_t* event,
                                             hggcIpcEventHandle_t handle)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| event | out | 用于返回导入的事件 |
| handle | in | 要打开的进程间句柄 |

错误码：hggcSuccess、hggcErrorMapBufferObjectFailed、hggcErrorNotSupported、hggcErrorInvalidValue、hggcErrorDeviceUninitialized

#### hggcStreamAddCallback

注意：此函数计划最终弃用并移除。不要求在设备错误时执行回调的话，改用 `hggcLaunchHostFunc`；此外本函数不支持与 `hggcStreamBeginCapture`/`hggcStreamEndCapture` 一起使用。

在流中当前排队的所有项目完成后，添加一个在主机上调用的回调。每次调用回调精确执行一次；回调完成前流中后续工作被阻塞。回调可能被传入 `hggcSuccess` 或错误码；发生设备错误时所有随后执行的回调都收到相应 `hggcError_t`。**回调不得进行任何 HGGC API 调用**（尝试可能导致 `hggcErrorNotPermitted`），也不得执行任何依赖于尚未完成之设备工作或未要求提前运行之回调的同步。无指定顺序的回调（独立流中）以未定义顺序执行且可能被序列化。

统一内存相关保证：

- 回调执行期间回调流视为空闲，回调始终可使用附加到该流的内存。
- 回调开始执行的效果等同于同步一个紧接之前在同一流记录的事件——即同步了此前已"加入（joined）"的流。
- 所有前面的回调执行完毕之前，向任何流添加设备工作都不会使该流变为活动状态；因此若回调已与事件正确排序，即使已向另一流添加工作，也可使用全局附加内存。
- 除上述情况外，回调完成不使流变为活动状态；没有设备工作紧随其后时流保持空闲，连续回调之间也保持空闲。因此可经流末尾的回调发出信号来做流同步。

```c
hggcError_t hggcStreamAddCallback (hggcStream_t stream,
                                   hggcStreamCallback_t callback,
                                   void* userData,
                                   unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| stream | in | 要添加回调的流 |
| callback | in | 前面流操作完成后调用的函数 |
| userData | in | 传给回调的用户数据 |
| flags | in | 保留，必须为 0 |

错误码：hggcSuccess、hggcErrorInvalidResourceHandle、hggcErrorInvalidValue、hggcErrorNotSupported

#### hggcStreamAttachMemAsync

在流中排队一个操作，指定从 `devPtr` 开始 `length` 字节内存的流关联。这是流排序操作：依赖流中先前工作完成，仅在先前工作完成时生效；任何以前的关联被自动替换。

`devPtr` 必须指向以下之一：

- `__managed__` 声明或 `hggcMallocManaged` 分配的托管内存。
- 系统分配可分页内存的有效主机可访问区域——仅当流关联设备的 `hggcDevAttrPageableMemoryAccess` 非零时可用。

托管分配的 `length` 必须为零或整个分配大小（只能更改整个分配的关联，无法只改一部分）；可分页分配 `length` 必须非零。`flags` 指定流关联，必须为 `hggcMemAttachGlobal`/`hggcMemAttachHost`/`hggcMemAttachSingle` 之一（默认 `hggcMemAttachSingle`）：

- `hggcMemAttachGlobal`：内存可由任何设备上的任何流访问。
- `hggcMemAttachHost`：程序保证不从 `hggcDevAttrConcurrentManagedAccess` 为零的设备上的任何流访问该内存。
- `hggcMemAttachSingle`：流关联到 `hggcDevAttrConcurrentManagedAccess` 为零的设备时，程序保证只从该流访问。

将内存单独附加到 NULL 流是非法的（NULL 流是虚拟全局流），返回错误。内存与单个流关联时，只要该流所有操作完成，UM 系统即允许 CPU 访问此区域，无论其他流是否活动——这把活动 PPU 对托管内存的独占所有权从整个 PPU 活动缩小到逐流活动。从不相关的流访问设备上的该内存结果未定义；UM 系统不做检查，程序须通过事件、同步等对 `hggcStreamAttachMemAsync` 调用排序。关联更改后的所有核函数，数据可见性和一致性都会相应更改。流在关联期间被销毁则关联删除，恢复为 `hggcMallocManaged` 指定的默认可见性；`__managed__` 变量默认关联始终为 `hggcMemAttachGlobal`。注意销毁流是异步操作，默认关联的更改要到流中所有工作完成才发生。

```c
hggcError_t hggcStreamAttachMemAsync (hggcStream_t stream,
                                      void* devPtr,
                                      size_t length = 0,
                                      unsigned int flags = hggcMemAttachSingle)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| stream | in | 排队附加操作的流 |
| devPtr | in | 指向内存的指针（托管内存，或系统分配内存的有效主机可访问区域） |
| length | in | 内存长度（默认为零） |
| flags | in | `hggcMemAttachGlobal`/`hggcMemAttachHost`/`hggcMemAttachSingle` 之一（默认 Single） |

错误码：hggcSuccess、hggcErrorNotReady、hggcErrorInvalidValue、hggcErrorInvalidResourceHandle

#### hggcStreamBeginCapture

开始在流上捕获图。捕获模式下推送到流中的操作不执行，而是被捕获到图中，经 `hggcStreamEndCapture` 返回。`hggcStreamLegacy` 上不能启动捕获。必须在启动捕获的同一流上结束捕获，且只能在流未处于捕获模式时启动。捕获状态可用 `hggcStreamIsCapturing` 查询；捕获序列唯一 ID 可用 `hggcStreamGetCaptureInfo` 查询。模式非 `hggcStreamCaptureModeRelaxed` 时，必须在同一线程调用 `hggcStreamEndCapture`。

```c
hggcError_t hggcStreamBeginCapture (hggcStream_t stream,
                                    hggcStreamCaptureMode mode)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| stream | in | 启动捕获的流 |
| mode | in | 控制捕获序列与其他可能不安全 API 调用的交互（详见 `hggcThreadExchangeStreamCaptureMode`） |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcStreamBeginCaptureToGraph

开始在流上捕获图到**现有图**中。与 `hggcStreamBeginCapture` 类似，但允许指定初始依赖项并将节点添加到现有图。

```c
hggcError_t hggcStreamBeginCaptureToGraph (hggcStream_t stream,
                                           hggcGraph_t graph,
                                           const hggcGraphNode_t* dependencies,
                                           const hggcGraphEdgeData* dependencyData,
                                           size_t numDependencies,
                                           hggcStreamCaptureMode mode)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| stream | in | 启动捕获的流 |
| graph | in | 捕获到的图 |
| dependencies | in | 流中捕获的第一个节点的依赖项；`numDependencies` 为 0 时可为 NULL |
| dependencyData | in | 与每个依赖项关联的可选数据数组 |
| numDependencies | in | 依赖项数量 |
| mode | in | 捕获交互模式（同上） |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcStreamCopyAttributes

将属性从源流 `src` 复制到目标流 `dst`。两个流必须在同一上下文。属性见 `hggcStreamAttrID`。

```c
hggcError_t hggcStreamCopyAttributes (hggcStream_t dst, hggcStream_t src)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dst | in | 目标流 |
| src | in | 源流 |

错误码：hggcSuccess、hggcErrorNotSupported

#### hggcStreamCreate

在调用主机线程的当前上下文中创建新的异步流。若调用线程没有当前上下文，则选择设备主上下文、使其成为当前并初始化后创建流。

```c
hggcError_t hggcStreamCreate (hggcStream_t* pStream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pStream | out | 指向新流标识符的指针 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorExternalDevice

#### hggcStreamCreateWithFlags

带标志创建异步流（上下文行为同上）。`flags` 有效值：

- `hggcStreamDefault` — 默认流创建标志。
- `hggcStreamNonBlocking` — 该流中的工作可与流 0（NULL stream）并发运行，不与流 0 隐式同步。

```c
hggcError_t hggcStreamCreateWithFlags (hggcStream_t* pStream,
                                       unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pStream | out | 指向新流标识符的指针 |
| flags | in | 流创建的参数 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorExternalDevice

#### hggcStreamCreateWithPriority

以指定优先级创建异步流（上下文行为同上）。优先级是调度提示：尽可能先运行高优先级工作，但不抢占已运行的工作，不提供其他顺序保证。数字越小优先级越高，"0"为默认优先级。有效范围用 `hggcDeviceGetStreamPriorityRange` 查询；超范围自动钳制。

```c
hggcError_t hggcStreamCreateWithPriority (hggcStream_t* pStream,
                                          unsigned int flags,
                                          int priority)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pStream | out | 指向新流标识符的指针 |
| flags | in | 流创建标志（见 `hggcStreamCreateWithFlags`） |
| priority | in | 流的优先级 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorExternalDevice

#### hggcStreamDestroy

销毁并清理异步流。调用时设备仍在执行流中工作的，函数立即返回，资源在流中所有工作完成后自动释放。

```c
hggcError_t hggcStreamDestroy (hggcStream_t stream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| stream | in | 流标识符 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidResourceHandle、hggcErrorExternalDevice

#### hggcStreamEndCapture

结束流上的捕获，经 `pGraph` 返回捕获的图。捕获必须经 `hggcStreamBeginCapture` 启动。捕获因违反规则而失效时返回 NULL 图。`hggcStreamBeginCapture` 的 mode 非 `hggcStreamCaptureModeRelaxed` 时，此调用必须来自同一线程。

```c
hggcError_t hggcStreamEndCapture (hggcStream_t stream, hggcGraph_t* pGraph)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| stream | in | 要查询的流 |
| pGraph | out | 捕获的图 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorStreamCaptureWrongThread

#### hggcStreamGetAttribute

查询 `hStream` 的属性 `attr`，存入 `value_out` 的相应成员。

```c
hggcError_t hggcStreamGetAttribute (hggcStream_t hStream,
                                    hggcStreamAttrID attr,
                                    hggcStreamAttrValue* value_out)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hStream | in | 流句柄 |
| attr | in | 要查询的属性 |
| value_out | out | 用于返回的属性值 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidResourceHandle

#### hggcStreamGetCaptureInfo

查询流捕获相关状态。在非 `hggcStreamNonBlocking` 创建的流正在捕获时，于 `hggcStreamLegacy`（"null stream"）上调用返回 `hggcErrorStreamCaptureImplicit`。

仅当以下两项都为真时才返回有效数据（捕获状态除外）：调用返回 `hggcSuccess`；返回的捕获状态为 `hggcStreamCaptureStatusActive`。

`edgeData_out` 非 NULL 时 `dependencies_out` 也必须非 NULL。`dependencies_out` 非 NULL 而 `edgeData_out` 为 NULL，但当前流的一个或多个依赖项存在非零边数据时，返回 `hggcErrorLossyQuery`。

```c
hggcError_t hggcStreamGetCaptureInfo (hggcStream_t stream,
                                      hggcStreamCaptureStatus ** captureStatus_out,
                                      unsigned long long* id_out = 0,
                                      hggcGraph_t* graph_out = 0,
                                      const hggcGraphNode_t** dependencies_out = 0,
                                      const hggcGraphEdgeData** edgeData_out = 0,
                                      size_t* numDependencies_out = 0)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| stream | in | 要查询的流 |
| captureStatus_out | out | 返回流捕获状态；必填 |
| id_out | out | 可选：返回捕获序列 ID（进程生命周期内唯一） |
| graph_out | out | 可选：返回正在捕获到的图。捕获期间允许对图做除销毁和节点移除外的所有操作；API 不转移图所有权（`hggcStreamEndCapture` 时转移或销毁）；某些错误可能使图句柄在捕获结束前失效；因直接操作图而变得无法从原始流到达的节点不触发 `hggcErrorStreamCaptureUnjoined` |
| dependencies_out | in | 可选：返回指向节点数组的指针——流中下一个被捕获节点将依赖这组节点（event wait）。数组指针在下一次操作流的 API 调用前或捕获终止前有效；节点句柄可复制，复制后在节点或图销毁前有效；驱动拥有的数组也可直接传给图 API 而无需复制 |
| edgeData_out | in | 可选：返回边数据数组指针，与 `dependencies_out` 平行——下一个添加的节点对 `dependencies_out[i]` 的边带注释 `edgeData_out[i]`。有效期同上 |
| numDependencies_out | out | 可选：返回 `dependencies_out` 数组大小 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorStreamCaptureImplicit、hggcErrorLossyQuery

#### hggcStreamGetFlags

查询流的标志（取值见 `hggcStreamCreateWithFlags`）。

```c
hggcError_t hggcStreamGetFlags (hggcStream_t hStream, unsigned int* flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hStream | in | 要查询的流的句柄 |
| flags | out | 返回流标志 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidResourceHandle

#### hggcStreamGetId

查询流的唯一 ID。

```c
hggcError_t hggcStreamGetId (hggcStream_t hStream, unsigned long long* streamId)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hStream | in | 要查询的流的句柄 |
| streamId | out | 返回流 ID |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidResourceHandle

#### hggcStreamGetPriority

查询流的优先级。

```c
hggcError_t hggcStreamGetPriority (hggcStream_t hStream, int* priority)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hStream | in | 要查询的流的句柄 |
| priority | out | 返回流优先级 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidResourceHandle

#### hggcStreamIsCapturing

查询流的捕获状态（`hggcStreamCaptureStatus`）。

```c
hggcError_t hggcStreamIsCapturing (hggcStream_t stream,
                                   hggcStreamCaptureStatus* pCaptureStatus)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| stream | in | 要查询的流 |
| pCaptureStatus | out | 返回流捕获状态 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcStreamQuery

查询流中之前所有操作的完成状态：全部完成返回 `hggcSuccess`，否则返回 `hggcErrorNotReady`。

```c
hggcError_t hggcStreamQuery (hggcStream_t stream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| stream | in | 要查询的流 |

错误码：hggcSuccess、hggcErrorInvalidResourceHandle、hggcErrorNotReady

#### hggcStreamSetAttribute

设置 `hStream` 的属性 `attr`。

```c
hggcError_t hggcStreamSetAttribute (hggcStream_t hStream,
                                    hggcStreamAttrID attr,
                                    const hggcStreamAttrValue* value)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hStream | in | 流句柄 |
| attr | in | 要设置的属性 |
| value | in | 指向要设置的值的指针 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidResourceHandle

#### hggcStreamSynchronize

阻塞主机线程，直到流中之前所有操作完成。使用标准同步行为。

```c
hggcError_t hggcStreamSynchronize (hggcStream_t stream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| stream | in | 要等待的流 |

错误码：hggcSuccess、hggcErrorInvalidResourceHandle、hggcErrorUnknown

#### hggcStreamUpdateCaptureDependencies

更新正在捕获的流中的依赖项集合，替换之前经 `hggcStreamBeginCapture`/`hggcStreamBeginCaptureToGraph` 设置的依赖项。

```c
hggcError_t hggcStreamUpdateCaptureDependencies (hggcStream_t stream,
                                                 hggcGraphNode_t* dependencies,
                                                 const hggcGraphEdgeData* dependencyData,
                                                 size_t numDependencies,
                                                 unsigned int flags = 0)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| stream | in | 正在捕获的流 |
| dependencies | in | 新的依赖项节点数组 |
| dependencyData | in | 与每个依赖项关联的可选数据数组 |
| numDependencies | in | 依赖项数量 |
| flags | in | 保留，必须为 0 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcStreamWaitEvent

使 `stream` 等待 `event` 完成。轻量级操作，可在同一流中多次调用以等待同一事件。

```c
hggcError_t hggcStreamWaitEvent (hggcStream_t stream,
                                 hggcEvent_t event,
                                 unsigned int flags = 0)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| stream | in | 要等待事件的流 |
| event | in | 要等待的事件 |
| flags | in | 保留，必须为 0 |

错误码：hggcSuccess、hggcErrorInvalidResourceHandle、hggcErrorInvalidValue

#### hggcThreadExchangeStreamCaptureMode

将调用线程的流捕获交互模式设为 `*mode`，并在 `*mode` 返回之前的模式。可用于临时更改线程捕获模式，以便与可能不安全的 API 调用交互。

```c
hggcError_t hggcThreadExchangeStreamCaptureMode (hggcStreamCaptureMode* mode)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| mode | out | 指向新的捕获模式，同时用于返回之前的模式 |

错误码：hggcSuccess、hggcErrorInvalidValue

比赛关联：多流 + `hggcStreamWaitEvent` 是把权重 H2D、图像预处理与 decode 计算重叠起来的基础手段（吞吐与 TTFT 双赢）；`hggcEventElapsedTime`（约 0.5 µs 分辨率）是设备侧分段计时、定位 TTFT 瓶颈的标准工具——注意计时事件不能用 `hggcEventDisableTiming` 创建。

## 执行与调度

本节涵盖 PPU 核函数的启动方式、函数属性查询、占用率计算，以及基于图的批量任务调度。

### 执行控制

本模块提供**核函数启动、执行配置与占用率查询**接口，涵盖启动参数设置、缓存偏好配置、函数属性查询、协作启动（cooperative launch）、簇级启动（cluster launch）及占用率（occupancy）计算。

| 函数 | 用途 |
|------|------|
| `hggcFuncGetAttributes` | 获取给定函数的属性 |
| `hggcFuncGetName` | 返回设备入口函数指针的函数名称 |
| `hggcFuncSetAttribute` | 设置给定函数的属性 |
| `hggcFuncSetCacheConfig` | 为设备函数设置首选缓存配置 |
| `hggcGetParameterBuffer` | 获取参数缓冲区 |
| `hggcLaunchCooperativeKernel` | 启动线程块可协作和同步的设备函数 |
| `hggcLaunchHostFunc` | 在流中排队运行一个主机函数 |
| `hggcLaunchKernel` | 启动设备函数 |
| `hggcLaunchKernelExC` | 使用启动时配置启动 HGGC 函数 |
| `hggcOccupancyAvailableDynamicSMemPerBlock` | 返回 SM 上启动 `numBlocks` 个线程块时每块可用的动态共享内存 |
| `hggcOccupancyMaxActiveBlocksPerMultiprocessor` | 返回设备函数的占用率 |
| `hggcOccupancyMaxActiveBlocksPerMultiprocessorWithFlags` | 带标志的占用率查询 |
| `hggcOccupancyMaxPotentialBlockSize` | 返回达到最大潜在 occupancy 的 grid 与线程块尺寸 |
| `hggcOccupancyMaxPotentialBlockSizeVariableSMem` | 动态共享内存由函数计算的版本 |
| `hggcOccupancyMaxPotentialBlockSizeVariableSMemWithFlags` | 上述版本的带标志形态 |
| `hggcOccupancyMaxPotentialBlockSizeWithFlags` | 带标志的最大潜在块尺寸计算 |

#### hggcFuncGetAttributes

获取 `func` 指定的函数属性，写入 `attr`。`func` 是设备函数符号，必须声明为 `__global__` 函数。指定函数不存在时假定其为 `hggcKernel_t` 并按原样使用。模板函数按 `func_name<template_arg_0,...,template_arg_N>` 形式传入。某些属性（如 `maxThreadsPerBlock`）可能随当前设备变化。

```c
hggcError_t hggcFuncGetAttributes (hggcFuncAttributes* attr, const void* func)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| attr | out | 指向返回函数属性的指针 |
| func | in | 设备函数符号 |

错误码：hggcSuccess、hggcErrorInvalidDeviceFunction

#### hggcFuncGetName

在 `*name` 中返回与符号 `func` 关联的函数名（NUL 结尾字符串）。函数未声明为 C 链接时可能返回名称修饰（mangled）后的名称。`*name` 为 NULL 返回 `hggcErrorInvalidValue`。`func` 不是设备入口函数时假定其为 `hggcKernel_t`。

```c
hggcError_t hggcFuncGetName (const char** name, const void* func)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| name | out | 用于返回的函数名称 |
| func | in | 要检索其名称的函数指针 |

错误码：hggcSuccess、hggcErrorInvalidValue、hggcErrorInvalidDeviceFunction

#### hggcFuncSetAttribute

设置 `func`（`__global__` 设备函数）的属性 `attr` 为 `value`。函数不存在时按 `hggcKernel_t` 处理。属性不可写或 `value` 不正确返回 `hggcErrorInvalidValue`。`attr` 有效值：

- `hggcFuncAttributeMaxDynamicSharedMemorySize` — 请求的动态分配共享内存最大字节数。与函数属性 `sharedSizeBytes` 之和不得超过 `hggcDevAttrMaxSharedMemoryPerBlockOptin`。可请求上限随 PPU 架构而异。
- `hggcFuncAttributePreferredSharedMemoryCarveout` — L1/共享内存共用硬件的设备上，设置共享内存切分首选项（占总共享内存百分比，见 `hggcDevAttrMaxSharedMemoryPerMultiprocessor`）。仅为提示，驱动可选不同比例。
- `hggcFuncAttributeRequiredClusterWidth` / `RequiredClusterHeight` / `RequiredClusterDepth` — 所需簇宽/高/深（以块为单位）。三者必须全为 0 或全为正数；有效性在启动时检查；编译时已设置则运行时不能再设（返回 `hggcErrorNotPermitted`）。
- `hggcFuncAttributeNonPortableClusterSizeAllowed` — 是否允许以非便携式簇大小启动（1 允许，0 禁止）。
- `hggcFuncAttributeClusterSchedulingPolicyPreference` — 函数的块调度策略，值类型为 `hggcClusterSchedulingPolicy`。

```c
hggcError_t hggcFuncSetAttribute (const void* func,
                                  hggcFuncAttribute attr,
                                  int value)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| func | in | 要设置其属性的函数 |
| attr | in | 要设置的属性 |
| value | in | 要设置的值 |

错误码：hggcSuccess、hggcErrorInvalidDeviceFunction、hggcErrorInvalidValue

#### hggcFuncSetCacheConfig

在 L1/共享内存共用硬件的设备上，为 `func`（`__global__` 函数符号，模板函数传参形式同上）设置首选缓存配置。仅为首选项；L1/共享内存大小固定的设备上无效。使用与最近一次偏好不同的偏好启动核函数可能插入设备端同步点。配置选项：`hggcFuncCachePreferNone`（默认）、`hggcFuncCachePreferShared`、`hggcFuncCachePreferL1`、`hggcFuncCachePreferEqual`。

```c
hggcError_t hggcFuncSetCacheConfig (const void* func, hggcFuncCache cacheConfig)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| func | in | 设备函数符号 |
| cacheConfig | in | 请求的缓存配置 |

错误码：hggcSuccess、hggcErrorInvalidDeviceFunction

#### hggcGetParameterBuffer

获取一个可填充核函数启动参数的参数缓冲区。低级 API，只能从并行线程执行（TIX）访问；HGGC 用户代码应使用 `<<< >>>` 启动核函数。

| 参数 | 方向 | 说明 |
|------|------|------|
| alignment | in | 参数缓冲区的对齐要求 |
| size | in | 大小要求（字节） |

#### hggcLaunchCooperativeKernel

在 `gridDim` 网格上调用核函数 `func`，每块 `blockDim` 个线程，线程块在执行时可协作和同步。设备属性 `hggcDevAttrCooperativeLaunch` 必须非零。启动的线程块总数不得超过 `hggcOccupancyMaxActiveBlocksPerMultiprocessor`（或带 Flags 版本）× `hggcDevAttrMultiProcessorCount`。核函数不能使用 HGGC 动态并行（dynamic parallelism）。`args` 指向含 N 个指针的数组，每个指针指向对应实参将被复制的内存区域；模板函数符号传参形式同前。`sharedMem` 设置每块动态共享内存量；`stream` 指定关联流。

```c
hggcError_t hggcLaunchCooperativeKernel (const void* func,
                                         dim3 gridDim,
                                         dim3 blockDim,
                                         void** args,
                                         size_t sharedMem,
                                         hggcStream_t stream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| func | in | 设备函数符号 |
| gridDim | in | Grid 维度 |
| blockDim | in | 线程块维度 |
| args | in | 参数 |
| sharedMem | in | 共享内存 |
| stream | in | 流标识符 |

错误码：hggcSuccess、hggcErrorInvalidDeviceFunction、hggcErrorInvalidConfiguration、hggcErrorLaunchFailure、hggcErrorLaunchTimeout、hggcErrorLaunchOutOfResources、hggcErrorCooperativeLaunchTooLarge、hggcErrorSharedObjectInitFailed

#### hggcLaunchHostFunc

在流中排队运行一个主机函数。该函数在当前排队工作之后调用，并阻塞其后添加的工作。主机函数**不得进行任何 HGGC API 调用**（尝试可能导致 `hggcErrorNotPermitted`，但非强制）；不得执行任何依赖于未要求提前运行之待处理 HGGC 工作的同步。无强制顺序的主机函数（如独立流中）按未定义顺序执行且可能被序列化。

统一内存相关保证：

- 函数执行期间流视为空闲，函数始终可使用附加到其入队流的内存。
- 函数开始执行的效果等同于同步一个紧接之前在同一流记录的事件——即同步了此前已"加入"的流。
- 所有前面的主机函数和流回调执行完毕之前，向任何流添加设备工作不使该流变为活动状态；因此若工作已通过事件排在函数调用之后，即使已向另一流添加工作，函数也可使用全局附加内存。
- 除上述情况外，函数完成不使流变为活动状态；没有设备工作紧随其后时流保持空闲，连续主机函数/流回调之间也保持空闲。可经流末尾的主机函数发信号做流同步。

注意：与 `hgStreamAddCallback` 不同，HGGC 上下文发生错误时该函数不会被调用。

```c
hggcError_t hggcLaunchHostFunc (hggcStream_t stream,
                                hggcHostFn_t fn,
                                void* userData)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| stream | in | 流 |
| fn | in | 前面流操作完成后调用的函数 |
| userData | in | 传给函数的应用数据 |

错误码：hggcSuccess、hggcErrorInvalidResourceHandle、hggcErrorInvalidValue、hggcErrorNotSupported

#### hggcLaunchKernel

在 `gridDim` 网格上调用核函数 `func`，每块 `blockDim` 个线程。`args` 指向含 N 个指针的数组，每个指针指向对应实参将被复制的内存区域；模板函数符号传参形式同前。`sharedMem` 设置每块动态共享内存量；`stream` 指定关联流。

```c
hggcError_t hggcLaunchKernel (const void* func,
                              dim3 gridDim,
                              dim3 blockDim,
                              void** args,
                              size_t sharedMem,
                              hggcStream_t stream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| func | in | 设备函数符号 |
| gridDim | in | Grid 维度 |
| blockDim | in | 线程块维度 |
| args | in | 参数 |
| sharedMem | in | 共享内存 |
| stream | in | 流标识符 |

错误码：hggcSuccess、hggcErrorInvalidDeviceFunction、hggcErrorInvalidConfiguration、hggcErrorLaunchFailure、hggcErrorLaunchTimeout、hggcErrorLaunchOutOfResources、hggcErrorSharedObjectInitFailed、hggcErrorInvalidTix、hggcErrorUnsupportedTixVersion、hggcErrorNoKernelImageForDevice、hggcErrorJitCompilerNotFound、hggcErrorJitCompilationDisabled

#### hggcLaunchKernelExC

在 `config->gridDim` 网格上调用核函数 `func`，每块 `config->blockDim` 个线程。`config->dynamicSmemBytes` 设置每块动态共享内存量，`config->stream` 指定关联流。额外配置经 `config` 的两个字段提供：`config->attrs` 为含 `config->numAttrs` 个连续 `hggcLaunchAttribute` 元素的数组（`numAttrs` 为零时忽略指针，但应置 NULL）；`numAttrs` 为填充在 `attrs` 数组前部的属性数量。`args` 的实参指针数组语义同 `hggcLaunchKernel`。

```c
hggcError_t hggcLaunchKernelExC (const hggcLaunchConfig_t* config,
                                 const void* func,
                                 void** args)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| config | in | 启动配置 |
| func | in | 要启动的核函数 |
| args | in | 指向核函数参数的指针数组 |

错误码：同 `hggcLaunchKernel`

#### hggcOccupancyAvailableDynamicSMemPerBlock

在 `*dynamicSmemSize` 中返回允许每个 SM 容纳 `numBlocks` 个线程块的最大动态共享内存大小。

```c
hggcError_t hggcOccupancyAvailableDynamicSMemPerBlock (size_t* dynamicSmemSize,
                                                       const void* func,
                                                       int numBlocks,
                                                       int blockSize)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| dynamicSmemSize | out | 返回的最大动态共享内存 |
| func | in | 用于计算占用率的核函数 |
| numBlocks | in | 容纳在 SM 上的线程块数量 |
| blockSize | in | 线程块大小 |

错误码：hggcSuccess、hggcErrorInvalidDevice、hggcErrorInvalidDeviceFunction、hggcErrorInvalidValue、hggcErrorUnknown

#### hggcOccupancyMaxActiveBlocksPerMultiprocessor

在 `*numBlocks` 中返回设备函数每个流式多处理器（SM）的最大活跃线程块数。

```c
hggcError_t hggcOccupancyMaxActiveBlocksPerMultiprocessor (int* numBlocks,
                                                           const void* func,
                                                           int blockSize,
                                                           size_t dynamicSMemSize)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| numBlocks | out | 返回的占用率 |
| func | in | 用于计算占用率的核函数 |
| blockSize | in | 预期的启动线程块大小 |
| dynamicSMemSize | in | 每块预期的动态共享内存使用量（字节） |

错误码：hggcSuccess、hggcErrorInvalidDevice、hggcErrorInvalidDeviceFunction、hggcErrorInvalidValue、hggcErrorUnknown

#### hggcOccupancyMaxActiveBlocksPerMultiprocessorWithFlags

同上，`flags` 控制特殊情况处理：

- `hggcOccupancyDefault`：与无 Flags 版本相同的默认行为。
- `hggcOccupancyDisableCachingOverride`：在全局缓存影响占用率的平台上抑制默认行为——此类平台上若启用缓存会导致零占用，占用率计算器默认按禁用缓存计算；设置此标志则在此类情况下返回 0。

```c
hggcError_t hggcOccupancyMaxActiveBlocksPerMultiprocessorWithFlags (int* numBlocks,
                                                                    const void* func,
                                                                    int blockSize,
                                                                    size_t dynamicSMemSize,
                                                                    unsigned int flags)
```

参数同上，另加 `flags`（in，占用率计算器的请求行为）。

错误码：hggcSuccess、hggcErrorInvalidDevice、hggcErrorInvalidDeviceFunction、hggcErrorInvalidValue、hggcErrorUnknown

#### hggcOccupancyMaxPotentialBlockSize

基于核函数、动态共享内存大小和可选的线程块大小限制，返回能达到最大潜在 occupancy 的最小网格大小和线程块大小。注意：也可能返回之前异步启动的错误码。

```c
template < class T > hggcError_t hggcOccupancyMaxPotentialBlockSize (int* minGridSize,
                                                                     int* blockSize,
                                                                     T func,
                                                                     size_t dynamicSMemSize = 0,
                                                                     int blockSizeLimit = 0)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| minGridSize | out | 返回的最小网格大小 |
| blockSize | out | 返回的线程块大小 |
| func | in | 设备函数 |
| dynamicSMemSize | in | 动态共享内存大小（字节） |
| blockSizeLimit | in | 线程块大小限制 |

错误码：hggcSuccess、hggcErrorInvalidDeviceFunction、hggcErrorInvalidValue

#### hggcOccupancyMaxPotentialBlockSizeVariableSMem

同上，但动态共享内存大小通过函数计算。

```c
template < typename UnaryFunction, class T > hggcError_t hggcOccupancyMaxPotentialBlockSizeVariableSMem (int* minGridSize,
                                                                                                         int* blockSize,
                                                                                                         T func,
                                                                                                         UnaryFunction blockSizeToDynamicSMemSize,
                                                                                                         int blockSizeLimit = 0)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| minGridSize | out | 返回的最小网格大小 |
| blockSize | out | 返回的线程块大小 |
| func | in | 设备函数 |
| blockSizeToDynamicSMemSize | in | 将线程块大小映射到动态共享内存大小的函数 |
| blockSizeLimit | in | 线程块大小限制 |

错误码：hggcSuccess、hggcErrorInvalidDeviceFunction、hggcErrorInvalidValue

#### hggcOccupancyMaxPotentialBlockSizeVariableSMemWithFlags

上述版本的带标志形态。

```c
template < typename UnaryFunction, class T > hggcError_t hggcOccupancyMaxPotentialBlockSizeVariableSMemWithFlags (int* minGridSize,
                                                                                                                  int* blockSize,
                                                                                                                  T func,
                                                                                                                  UnaryFunction blockSizeToDynamicSMemSize,
                                                                                                                  int blockSizeLimit = 0,
                                                                                                                  unsigned int flags = 0)
```

参数同上，另加 `flags`（in，占用率计算标志）。

错误码：hggcSuccess、hggcErrorInvalidDeviceFunction、hggcErrorInvalidValue

#### hggcOccupancyMaxPotentialBlockSizeWithFlags

`hggcOccupancyMaxPotentialBlockSize` 的带标志形态。

```c
template < class T > hggcError_t hggcOccupancyMaxPotentialBlockSizeWithFlags (int* minGridSize,
                                                                              int* blockSize,
                                                                              T func,
                                                                              size_t dynamicSMemSize = 0,
                                                                              int blockSizeLimit = 0,
                                                                              unsigned int flags = 0)
```

参数同 `hggcOccupancyMaxPotentialBlockSize`，另加 `flags`（in，占用率计算标志）。

错误码：hggcSuccess、hggcErrorInvalidDeviceFunction、hggcErrorInvalidValue

### 图管理

本模块提供**图（Graph）管理**接口。HGGC Graph 允许将一系列操作（核函数启动、内存拷贝、事件等待等）预定义为有向无环图（DAG），一次性提交以减少启动开销。涵盖图创建/销毁、节点与边的增删改查、图实例化（instantiate）与执行、克隆与更新。

**注意：图对象不是线程安全的**——同一图对象上的任何并发访问（包括 `hggcGraphClone`、`hggcGraphInstantiate` 这类"看似只读"的调用）都需要调用方外部串行化，详见"图对象的线程安全性"节。正文不再逐条重复该提示。内存管理节首的"通用注意事项"同样适用于本模块全部函数。

| 函数 | 用途 |
|------|------|
| `hggcDeviceGetGraphMemAttribute` | 查询与图相关的异步分配属性 |
| `hggcDeviceGraphMemTrim` | 将指定设备上为图使用而缓存的未使用内存释放回操作系统 |
| `hggcDeviceSetGraphMemAttribute` | 设置与图相关的异步分配属性 |
| `hggcGetCurrentGraphExec` | 获取当前正在运行的设备端图 ID |
| `hggcGraphAddChildGraphNode` | 创建子图节点并添加到图中 |
| `hggcGraphAddDependencies` | 向图中添加依赖边 |
| `hggcGraphAddEmptyNode` | 创建空节点并添加到图中 |
| `hggcGraphAddEventRecordNode` | 创建事件记录节点并添加到图中 |
| `hggcGraphAddEventWaitNode` | 创建事件等待节点并添加到图中 |
| `hggcGraphAddHostNode` | 创建主机执行节点并添加到图中 |
| `hggcGraphAddKernelNode` | 创建核函数执行节点并添加到图中 |
| `hggcGraphAddMemAllocNode` | 创建内存分配节点并添加到图中 |
| `hggcGraphAddMemFreeNode` | 创建内存释放节点并添加到图中 |
| `hggcGraphAddMemcpyNode` | 创建 memcpy 节点并添加到图中 |
| `hggcGraphAddMemcpyNode1D` | 创建一维 memcpy 节点并添加到图中 |
| `hggcGraphAddMemcpyNodeFromSymbol` | 创建从设备端符号复制的 memcpy 节点 |
| `hggcGraphAddMemcpyNodeToSymbol` | 创建向设备端符号复制的 memcpy 节点 |
| `hggcGraphAddMemsetNode` | 创建 memset 节点并添加到图中 |
| `hggcGraphAddNode` | 向图中添加任意类型的节点 |
| `hggcGraphChildGraphNodeGetGraph` | 获取子图节点中嵌入图的句柄 |
| `hggcGraphClone` | 克隆一个图 |
| `hggcGraphConditionalHandleCreate` | 创建用于控制条件图执行的条件句柄 |
| `hggcGraphCreate` | 创建一个图 |
| `hggcGraphDebugDotPrint` | 写入描述图结构的 DOT 文件 |
| `hggcGraphDestroy` | 销毁一个图 |
| `hggcGraphDestroyNode` | 从图中移除一个节点 |
| `hggcGraphEventRecordNodeGetEvent` | 返回与事件记录节点关联的事件 |
| `hggcGraphEventRecordNodeSetEvent` | 设置事件记录节点的事件 |
| `hggcGraphEventWaitNodeGetEvent` | 返回与事件等待节点关联的事件 |
| `hggcGraphEventWaitNodeSetEvent` | 设置事件等待节点的事件 |
| `hggcGraphExecChildGraphNodeSetParams` | 更新 graphExec 中子图节点的节点参数 |
| `hggcGraphExecDestroy` | 销毁可执行图 |
| `hggcGraphExecEventRecordNodeSetEvent` | 在 graphExec 中为事件记录节点设置事件 |
| `hggcGraphExecEventWaitNodeSetEvent` | 在 graphExec 中为事件等待节点设置事件 |
| `hggcGraphExecHostNodeSetParams` | 在 graphExec 中设置主机节点参数 |
| `hggcGraphExecKernelNodeSetParams` | 在 graphExec 中设置核函数节点参数 |
| `hggcGraphExecMemcpyNodeSetParams` | 在 graphExec 中设置 memcpy 节点参数 |
| `hggcGraphExecMemcpyNodeSetParams1D` | 同上，改为一维拷贝 |
| `hggcGraphExecMemcpyNodeSetParamsFromSymbol` | 同上，改为从符号拷贝 |
| `hggcGraphExecMemcpyNodeSetParamsToSymbol` | 同上，改为向符号拷贝 |
| `hggcGraphExecMemsetNodeSetParams` | 在 graphExec 中设置 memset 节点参数 |
| `hggcGraphExecNodeSetParams` | 在已实例化图中更新任意节点参数 |
| `hggcGraphExecUpdate` | 检查并执行可执行图的整体更新 |
| `hggcGraphGetEdges` | 返回图的依赖边 |
| `hggcGraphGetNodes` | 返回图的节点 |
| `hggcGraphGetRootNodes` | 返回图的根节点 |
| `hggcGraphHostNodeGetParams` | 返回主机节点的参数 |
| `hggcGraphHostNodeSetParams` | 设置主机节点的参数 |
| `hggcGraphInstantiate` | 将图实例化为可执行图 |
| `hggcGraphInstantiateWithFlags` | 使用指定标志实例化 |
| `hggcGraphKernelNodeCopyAttributes` | 将属性从源节点复制到目标节点 |
| `hggcGraphKernelNodeGetAttribute` | 查询节点属性 |
| `hggcGraphKernelNodeGetParams` | 返回核函数节点的参数 |
| `hggcGraphKernelNodeSetAttribute` | 设置节点属性 |
| `hggcGraphKernelNodeSetParams` | 设置核函数节点的参数 |
| `hggcGraphLaunch` | 在流中启动可执行图 |
| `hggcGraphMemAllocNodeGetParams` | 返回内存分配节点的参数 |
| `hggcGraphMemFreeNodeGetParams` | 返回内存释放节点的参数 |
| `hggcGraphMemcpyNodeGetParams` | 返回 memcpy 节点的参数 |
| `hggcGraphMemcpyNodeSetParams` | 设置 memcpy 节点的参数 |
| `hggcGraphMemcpyNodeSetParams1D` | 同上，改为一维拷贝 |
| `hggcGraphMemcpyNodeSetParamsFromSymbol` | 同上，改为从符号拷贝 |
| `hggcGraphMemcpyNodeSetParamsToSymbol` | 同上，改为向符号拷贝 |
| `hggcGraphMemsetNodeGetParams` | 返回 memset 节点的参数 |
| `hggcGraphMemsetNodeSetParams` | 设置 memset 节点的参数 |
| `hggcGraphNodeFindInClone` | 查找某个节点的克隆版本 |
| `hggcGraphNodeGetDependencies` | 返回节点的依赖项 |
| `hggcGraphNodeGetDependentNodes` | 返回依赖于该节点的节点 |
| `hggcGraphNodeGetType` | 返回节点类型 |
| `hggcGraphNodeSetParams` | 更新图节点的参数 |
| `hggcGraphReleaseUserObject` | 从图中释放对用户对象的引用 |
| `hggcGraphRemoveDependencies` | 从图中移除依赖边 |
| `hggcGraphRetainUserObject` | 从图中保留对用户对象的引用 |
| `hggcGraphUpload` | 在流中上传可执行图 |
| `hggcUserObjectCreate` | 创建用户对象 |
| `hggcUserObjectRelease` | 释放对用户对象的一个引用 |
| `hggcUserObjectRetain` | 保留对用户对象的一个引用 |

#### hggcDeviceGetGraphMemAttribute

查询与图相关的异步分配属性。有效属性：

- `hggcGraphMemAttrUsedMemCurrent`：当前与图关联的内存量（字节）。
- `hggcGraphMemAttrUsedMemHigh`：自上次重置以来的高水位（字节，只能重置为零）。
- `hggcGraphMemAttrReservedMemCurrent`：当前为图异步分配器分配的内存量（字节）。
- `hggcGraphMemAttrReservedMemHigh`：上述分配的高水位（字节）。

```c
hggcError_t hggcDeviceGetGraphMemAttribute (int device,
                                            hggcGraphMemAttributeType attr,
                                            void* value)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| device | in | 指定查询的作用域 |
| attr | in | 要获取的属性 |
| value | out | 返回的值 |

错误码：hggcSuccess、hggcErrorInvalidDevice

#### hggcDeviceGraphMemTrim

将指定设备上未被当前正在执行或已计划执行的图使用的内存块释放回操作系统。

```c
hggcError_t hggcDeviceGraphMemTrim (int device)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| device | in | 要释放其缓存内存的设备 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcDeviceSetGraphMemAttribute

设置与图相关的异步分配属性。有效属性：`hggcGraphMemAttrUsedMemHigh`（重置高水位，只能重置为零）、`hggcGraphMemAttrReservedMemHigh`（同上）。

```c
hggcError_t hggcDeviceSetGraphMemAttribute (int device,
                                            hggcGraphMemAttributeType attr,
                                            void* value)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| device | in | 指定设置的作用域 |
| attr | in | 要设置的属性 |
| value | in | 指向要设置的值的指针 |

错误码：hggcSuccess、hggcErrorInvalidDevice

#### hggcGetCurrentGraphExec

获取当前正在运行的设备端图 ID。

#### hggcGraphAddChildGraphNode

创建执行嵌入图的新节点并添加到图；依赖数量为 numDependencies，由 pDependencies 指定，可为 0（置于图的根部）；pDependencies 不得含重复条目。新节点句柄经 pGraphNode 返回。childGraph 含分配节点、释放节点或条件节点时返回错误。此调用会**克隆**该子图。

```c
hggcError_t hggcGraphAddChildGraphNode (hggcGraphNode_t* pGraphNode,
                                        hggcGraph_t graph,
                                        const hggcGraphNode_t* pDependencies,
                                        size_t numDependencies,
                                        hggcGraph_t childGraph)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pGraphNode | out | 返回新创建的节点 |
| graph | in | 要将节点添加到的图 |
| pDependencies | in | 节点的依赖项 |
| numDependencies | in | 依赖数量 |
| childGraph | in | 要克隆进该节点的图 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphAddDependencies

向图中添加依赖边。pFrom 与 pTo 对应索引的元素共同定义一条依赖；两数组中每个节点都必须属于图。numDependencies 为 0 时忽略 pFrom/pTo。指定已存在的依赖返回错误。

```c
hggcError_t hggcGraphAddDependencies (hggcGraph_t graph,
                                      const hggcGraphNode_t* from,
                                      const hggcGraphNode_t* to,
                                      const hggcGraphEdgeData* edgeData,
                                      size_t numDependencies)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| graph | in | 要添加依赖的图 |
| from | in | 提供依赖的节点数组 |
| to | in | 依赖节点数组 |
| edgeData | in | 可选的边数据数组；为 NULL 时使用默认（全 0）边数据 |
| numDependencies | in | 要添加的依赖数量 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphAddEmptyNode

创建不执行任何操作的空节点并添加到图（依赖语义同上）。空节点可用于传递式排序：例如两组各 n 个节点之间有一道屏障的分阶段图，可用一个空节点加 2n 条依赖边表示，而不是 n² 条边。

```c
hggcError_t hggcGraphAddEmptyNode (hggcGraphNode_t* pGraphNode,
                                   hggcGraph_t graph,
                                   const hggcGraphNode_t* pDependencies,
                                   size_t numDependencies)
```

参数同常规 Add 节点系列（pGraphNode/graph/pDependencies/numDependencies）。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphAddEventRecordNode

创建事件记录节点并添加到 hGraph（依赖语义同上）。每次启动该图都会记录 event，以捕获该节点依赖项的执行。这些节点不能用于循环或条件结构中。

```c
hggcError_t hggcGraphAddEventRecordNode (hggcGraphNode_t* pGraphNode,
                                         hggcGraph_t graph,
                                         const hggcGraphNode_t* pDependencies,
                                         size_t numDependencies,
                                         hggcEvent_t event)
```

常规参数另加 `event`（in，节点使用的事件）。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphAddEventWaitNode

创建事件等待节点并添加到 hGraph。该节点等待 event 中捕获的所有工作完成（捕获内容见 `hgEventRecord()`）；适用时同步以设备端高效方式执行。event 可来自与启动流不同的上下文或设备。不能用于循环或条件结构中。

```c
hggcError_t hggcGraphAddEventWaitNode (hggcGraphNode_t* pGraphNode,
                                       hggcGraph_t graph,
                                       const hggcGraphNode_t* pDependencies,
                                       size_t numDependencies,
                                       hggcEvent_t event)
```

参数同 `hggcGraphAddEventRecordNode`。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphAddHostNode

创建主机函数执行节点。节点执行时调用指定的主机函数；**主机函数不得进行任何 HGGC API 调用**。

```c
hggcError_t hggcGraphAddHostNode (hggcGraphNode_t* pGraphNode,
                                  hggcGraph_t graph,
                                  const hggcGraphNode_t* pDependencies,
                                  size_t numDependencies,
                                  const hggcHostNodeParams* pNodeParams)
```

常规参数另加 `pNodeParams`（in，节点参数）。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphAddKernelNode

创建核函数执行节点。节点执行时启动指定的核函数。

```c
hggcError_t hggcGraphAddKernelNode (hggcGraphNode_t* pGraphNode,
                                    hggcGraph_t graph,
                                    const hggcGraphNode_t* pDependencies,
                                    size_t numDependencies,
                                    const hggcKernelNodeParams* pNodeParams)
```

常规参数另加 `pNodeParams`（in，节点参数）。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphAddMemAllocNode

创建内存分配节点。节点执行时从图的内存池分配指定大小的内存，地址经 `nodeParams->dptr` 返回。

```c
hggcError_t hggcGraphAddMemAllocNode (hggcGraphNode_t* pGraphNode,
                                      hggcGraph_t graph,
                                      const hggcGraphNode_t* pDependencies,
                                      size_t numDependencies,
                                      hggcMemAllocNodeParams* nodeParams)
```

常规参数另加 `nodeParams`（in，节点参数）。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphAddMemFreeNode

创建内存释放节点。节点执行时释放之前经内存分配节点分配的内存。

```c
hggcError_t hggcGraphAddMemFreeNode (hggcGraphNode_t* pGraphNode,
                                     hggcGraph_t graph,
                                     const hggcGraphNode_t* pDependencies,
                                     size_t numDependencies,
                                     void* dptr)
```

常规参数另加 `dptr`（in，要释放的设备指针）。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphAddMemcpyNode

创建内存拷贝节点。节点执行时执行指定的内存拷贝操作。

```c
hggcError_t hggcGraphAddMemcpyNode (hggcGraphNode_t* pGraphNode,
                                    hggcGraph_t graph,
                                    const hggcGraphNode_t* pDependencies,
                                    size_t numDependencies,
                                    const hggcMemcpy3DParms* pCopyParams)
```

常规参数另加 `pCopyParams`（in，拷贝参数）。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphAddMemcpyNode1D

创建一维内存拷贝节点（`hggcGraphAddMemcpyNode` 的简化版本）。

```c
hggcError_t hggcGraphAddMemcpyNode1D (hggcGraphNode_t* pGraphNode,
                                      hggcGraph_t graph,
                                      const hggcGraphNode_t* pDependencies,
                                      size_t numDependencies,
                                      void* dst,
                                      const void* src,
                                      size_t count,
                                      hggcMemcpyKind kind)
```

常规参数另加 `dst`（目标地址）、`src`（源地址）、`count`（拷贝字节数）、`kind`（拷贝类型），均 in。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphAddMemcpyNodeFromSymbol

创建从设备端符号拷贝的内存拷贝节点。

```c
hggcError_t hggcGraphAddMemcpyNodeFromSymbol (hggcGraphNode_t* pGraphNode,
                                              hggcGraph_t graph,
                                              const hggcGraphNode_t* pDependencies,
                                              size_t numDependencies,
                                              void* dst,
                                              const void* symbol,
                                              size_t count,
                                              size_t offset,
                                              hggcMemcpyKind kind)
```

常规参数另加 `dst`、`symbol`（设备端符号）、`count`、`offset`（符号中偏移量）、`kind`，均 in。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphAddMemcpyNodeToSymbol

创建向设备端符号拷贝的内存拷贝节点。

```c
hggcError_t hggcGraphAddMemcpyNodeToSymbol (hggcGraphNode_t* pGraphNode,
                                            hggcGraph_t graph,
                                            const hggcGraphNode_t* pDependencies,
                                            size_t numDependencies,
                                            const void* symbol,
                                            const void* src,
                                            size_t count,
                                            size_t offset,
                                            hggcMemcpyKind kind)
```

常规参数另加 `symbol`、`src`、`count`、`offset`、`kind`，均 in。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphAddMemsetNode

创建内存填充节点。节点执行时用指定值填充内存区域。

```c
hggcError_t hggcGraphAddMemsetNode (hggcGraphNode_t* pGraphNode,
                                    hggcGraph_t graph,
                                    const hggcGraphNode_t* pDependencies,
                                    size_t numDependencies,
                                    const hggcMemsetParams* pMemsetParams)
```

常规参数另加 `pMemsetParams`（in，memset 参数）。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphAddNode

通用函数：向图中添加任意类型的节点，节点类型由 `nodeParams->type` 指定。

```c
hggcError_t hggcGraphAddNode (hggcGraphNode_t* pGraphNode,
                              hggcGraph_t graph,
                              const hggcGraphNode_t* pDependencies,
                              const hggcGraphEdgeData* dependencyData,
                              size_t numDependencies,
                              hggcGraphNodeParams* nodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pGraphNode | out | 返回新创建的节点 |
| graph | in | 要将节点添加到的图 |
| pDependencies | in | 节点的依赖项 |
| dependencyData | in | 可选的边数据 |
| numDependencies | in | 依赖数量 |
| nodeParams | in | 节点参数（包含节点类型和特定参数） |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphChildGraphNodeGetGraph

获取与子图节点关联的嵌入图的句柄。

```c
hggcError_t hggcGraphChildGraphNodeGetGraph (hggcGraphNode_t node,
                                             hggcGraph_t* pGraph)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| node | in | 子图节点 |
| pGraph | out | 返回嵌入图的句柄 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphClone

创建图及其所有节点的副本。节点句柄不会保留，必须用 `hggcGraphNodeFindInClone` 从原始节点映射到克隆节点。

```c
hggcError_t hggcGraphClone (hggcGraph_t* pGraphClone, hggcGraph_t originalGraph)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pGraphClone | out | 返回克隆的图 |
| originalGraph | in | 要克隆的原始图 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphConditionalHandleCreate

创建用于控制条件图执行的条件句柄。

```c
hggcError_t hggcGraphConditionalHandleCreate (hggcGraphConditionalHandle* pHandle_out,
                                              hggcGraph_t graph,
                                              unsigned int defaultLaunchValue = 0,
                                              unsigned int flags = 0)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pHandle_out | out | 返回的条件句柄 |
| graph | in | 包含条件节点的图 |
| defaultLaunchValue | in | 默认启动值 |
| flags | in | 标志位 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphCreate

创建一个空图，之后可向其中添加节点。

```c
hggcError_t hggcGraphCreate (hggcGraph_t* pGraph, unsigned int flags = 0)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pGraph | out | 返回创建的图 |
| flags | in | 创建标志 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphDebugDotPrint

将图的依赖关系导出为 Graphviz DOT 格式文件，可用于可视化图结构。

```c
hggcError_t hggcGraphDebugDotPrint (hggcGraph_t graph,
                                    const char* path,
                                    unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| graph | in | 要导出的图 |
| path | out | 输出文件路径 |
| flags | out | 控制输出内容的标志（见 `hggcGraphDebugDotFlags`） |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphDestroy

销毁图并释放相关资源。

```c
hggcError_t hggcGraphDestroy (hggcGraph_t graph)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| graph | in | 要销毁的图 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphDestroyNode

从图中移除指定节点及其相关的依赖边。

```c
hggcError_t hggcGraphDestroyNode (hggcGraphNode_t node)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| node | in | 要移除的节点 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphEventRecordNodeGetEvent

获取与事件记录节点关联的事件句柄。

```c
hggcError_t hggcGraphEventRecordNodeGetEvent (hggcGraphNode_t node,
                                              hggcEvent_t* event_out)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| node | in | 事件记录节点 |
| event_out | out | 返回关联的事件 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphEventRecordNodeSetEvent

更改事件记录节点使用的事件。

```c
hggcError_t hggcGraphEventRecordNodeSetEvent (hggcGraphNode_t node,
                                              hggcEvent_t event)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| node | in | 事件记录节点 |
| event | in | 要设置的事件 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphEventWaitNodeGetEvent

获取与事件等待节点关联的事件句柄。

```c
hggcError_t hggcGraphEventWaitNodeGetEvent (hggcGraphNode_t node,
                                            hggcEvent_t* event_out)
```

参数同 `hggcGraphEventRecordNodeGetEvent`。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphEventWaitNodeSetEvent

更改事件等待节点使用的事件。

```c
hggcError_t hggcGraphEventWaitNodeSetEvent (hggcGraphNode_t node,
                                            hggcEvent_t event)
```

参数同 `hggcGraphEventRecordNodeSetEvent`。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphExecChildGraphNodeSetParams

更新可执行图中子图节点的子图。

```c
hggcError_t hggcGraphExecChildGraphNodeSetParams (hggcGraphExec_t hGraphExec,
                                                  hggcGraphNode_t node,
                                                  hggcGraph_t childGraph)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraphExec | in | 可执行图 |
| node | in | 要更新的子图节点 |
| childGraph | in | 新的子图 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphExecDestroy

销毁可执行图并释放相关资源。注意：此调用之后使用句柄是未定义行为。

```c
hggcError_t hggcGraphExecDestroy (hggcGraphExec_t graphExec)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| graphExec | in | 要销毁的可执行图 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphExecEventRecordNodeSetEvent

更改可执行图中事件记录节点使用的事件。

```c
hggcError_t hggcGraphExecEventRecordNodeSetEvent (hggcGraphExec_t hGraphExec,
                                                  hggcGraphNode_t hNode,
                                                  hggcEvent_t event)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraphExec | in | 可执行图 |
| hNode | in | 事件记录节点 |
| event | in | 要设置的事件 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphExecEventWaitNodeSetEvent

更改可执行图中事件等待节点使用的事件。

```c
hggcError_t hggcGraphExecEventWaitNodeSetEvent (hggcGraphExec_t hGraphExec,
                                                hggcGraphNode_t hNode,
                                                hggcEvent_t event)
```

参数同上（hNode 为事件等待节点）。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphExecHostNodeSetParams

更新可执行图中主机节点的参数。

```c
hggcError_t hggcGraphExecHostNodeSetParams (hggcGraphExec_t hGraphExec,
                                            hggcGraphNode_t node,
                                            const hggcHostNodeParams* pNodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraphExec | in | 可执行图 |
| node | in | 主机节点 |
| pNodeParams | in | 新的节点参数 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphExecKernelNodeSetParams

更新可执行图中核函数节点的参数，包括核函数、网格/块维度和共享内存大小。

```c
hggcError_t hggcGraphExecKernelNodeSetParams (hggcGraphExec_t hGraphExec,
                                              hggcGraphNode_t node,
                                              const hggcKernelNodeParams* pNodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraphExec | in | 可执行图 |
| node | in | 核函数节点 |
| pNodeParams | in | 新的节点参数 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphExecMemcpyNodeSetParams

更新可执行图中 memcpy 节点的参数。

```c
hggcError_t hggcGraphExecMemcpyNodeSetParams (hggcGraphExec_t hGraphExec,
                                              hggcGraphNode_t node,
                                              const hggcMemcpy3DParms* pNodeParams)
```

参数同上（pNodeParams 为新的拷贝参数）。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphExecMemcpyNodeSetParams1D

更新可执行图中 memcpy 节点的参数为一维拷贝。

```c
hggcError_t hggcGraphExecMemcpyNodeSetParams1D (hggcGraphExec_t hGraphExec,
                                                hggcGraphNode_t node,
                                                void* dst,
                                                const void* src,
                                                size_t count,
                                                hggcMemcpyKind kind)
```

参数：hGraphExec、node（memcpy 节点）、dst、src、count、kind，均 in。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphExecMemcpyNodeSetParamsFromSymbol

更新可执行图中 memcpy 节点的参数为从符号拷贝。

```c
hggcError_t hggcGraphExecMemcpyNodeSetParamsFromSymbol (hggcGraphExec_t hGraphExec,
                                                        hggcGraphNode_t node,
                                                        void* dst,
                                                        const void* symbol,
                                                        size_t count,
                                                        size_t offset,
                                                        hggcMemcpyKind kind)
```

参数：hGraphExec、node、dst、symbol、count、offset、kind，均 in。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphExecMemcpyNodeSetParamsToSymbol

更新可执行图中 memcpy 节点的参数为向符号拷贝。

```c
hggcError_t hggcGraphExecMemcpyNodeSetParamsToSymbol (hggcGraphExec_t hGraphExec,
                                                      hggcGraphNode_t node,
                                                      const void* symbol,
                                                      const void* src,
                                                      size_t count,
                                                      size_t offset,
                                                      hggcMemcpyKind kind)
```

参数：hGraphExec、node、symbol、src、count、offset、kind，均 in。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphExecMemsetNodeSetParams

更新可执行图中 memset 节点的参数。

```c
hggcError_t hggcGraphExecMemsetNodeSetParams (hggcGraphExec_t hGraphExec,
                                              hggcGraphNode_t node,
                                              const hggcMemsetParams* pNodeParams)
```

参数同上（pNodeParams 为新的 memset 参数）。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphExecNodeSetParams

更新可执行图中任意类型节点的参数。

```c
hggcError_t hggcGraphExecNodeSetParams (hggcGraphExec_t graphExec,
                                        hggcGraphNode_t node,
                                        hggcGraphNodeParams* nodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| graphExec | in | 可执行图 |
| node | in | 要更新的节点 |
| nodeParams | in | 新的节点参数 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphExecUpdate

尝试将可执行图更新为使用新图的参数。拓扑兼容则执行更新，否则返回错误详情（`hggcGraphExecUpdateResultInfo`，结果取值见 `hggcGraphExecUpdateResult`）。

```c
hggcError_t hggcGraphExecUpdate (hggcGraphExec_t hGraphExec,
                                 hggcGraph_t hGraph,
                                 hggcGraphExecUpdateResultInfo* resultInfo)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hGraphExec | in | 要更新的可执行图 |
| hGraph | in | 提供新参数的源图 |
| resultInfo | out | 返回更新结果信息 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphGetEdges

获取图中所有依赖边的列表。

```c
hggcError_t hggcGraphGetEdges (hggcGraph_t graph,
                               hggcGraphNode_t* from,
                               hggcGraphNode_t* to,
                               hggcGraphEdgeData* edgeData,
                               size_t* numEdges)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| graph | in | 要查询的图 |
| from | out | 返回边的起始节点数组 |
| to | out | 返回边的目标节点数组 |
| edgeData | out | 返回的边数据数组 |
| numEdges | out | 输入/输出：边的数量 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphGetNodes

获取图中所有节点的列表。

```c
hggcError_t hggcGraphGetNodes (hggcGraph_t graph,
                               hggcGraphNode_t* nodes,
                               size_t* numNodes)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| graph | in | 要查询的图 |
| nodes | out | 返回的节点数组 |
| numNodes | out | 输入/输出：节点数量 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphGetRootNodes

获取图中没有依赖项的根节点列表。

```c
hggcError_t hggcGraphGetRootNodes (hggcGraph_t graph,
                                   hggcGraphNode_t* pRootNodes,
                                   size_t* pNumRootNodes)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| graph | in | 要查询的图 |
| pRootNodes | out | 返回的根节点数组 |
| pNumRootNodes | out | 输入/输出：根节点数量 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphHostNodeGetParams

获取主机节点的当前参数。

```c
hggcError_t hggcGraphHostNodeGetParams (hggcGraphNode_t node,
                                        hggcHostNodeParams* pNodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| node | in | 主机节点 |
| pNodeParams | out | 返回的节点参数 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphHostNodeSetParams

更新主机节点的参数。

```c
hggcError_t hggcGraphHostNodeSetParams (hggcGraphNode_t node,
                                        const hggcHostNodeParams* pNodeParams)
```

参数同上（pNodeParams 为 in）。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphInstantiate

将图实例化为可执行图，可在流中多次启动。

```c
hggcError_t hggcGraphInstantiate (hggcGraphExec_t* pGraphExec,
                                  hggcGraph_t graph,
                                  unsigned long long flags = 0)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pGraphExec | out | 返回的可执行图 |
| graph | in | 要实例化的图 |
| flags | in | 实例化标志（见 `hggcGraphInstantiateFlags`） |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphInstantiateWithFlags

使用指定标志将图实例化为可执行图。

```c
hggcError_t hggcGraphInstantiateWithFlags (hggcGraphExec_t* pGraphExec,
                                           hggcGraph_t graph,
                                           unsigned long long flags = 0)
```

参数同上。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphKernelNodeCopyAttributes

将核函数节点的所有属性从源节点复制到目标节点。

```c
hggcError_t hggcGraphKernelNodeCopyAttributes (hggcGraphNode_t hDst,
                                               hggcGraphNode_t hSrc)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hDst | in | 目标节点 |
| hSrc | in | 源节点 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphKernelNodeGetAttribute

获取核函数节点的指定属性值。

```c
hggcError_t hggcGraphKernelNodeGetAttribute (hggcGraphNode_t hNode,
                                             hggcKernelNodeAttrID attr,
                                             hggcKernelNodeAttrValue* value_out)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 核函数节点 |
| attr | in | 要查询的属性 ID |
| value_out | out | 返回的属性值 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphKernelNodeGetParams

获取核函数节点的当前参数。

```c
hggcError_t hggcGraphKernelNodeGetParams (hggcGraphNode_t node,
                                          hggcKernelNodeParams* pNodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| node | in | 核函数节点 |
| pNodeParams | out | 返回的节点参数 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphKernelNodeSetAttribute

设置核函数节点的指定属性值。

```c
hggcError_t hggcGraphKernelNodeSetAttribute (hggcGraphNode_t hNode,
                                             hggcKernelNodeAttrID attr,
                                             const hggcKernelNodeAttrValue* value)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| hNode | in | 核函数节点 |
| attr | in | 要设置的属性 ID |
| value | in | 属性值 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphKernelNodeSetParams

更新核函数节点的所有参数。

```c
hggcError_t hggcGraphKernelNodeSetParams (hggcGraphNode_t node,
                                          const hggcKernelNodeParams* pNodeParams)
```

参数同上（pNodeParams 为 in）。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphLaunch

在指定流中启动可执行图。使用标准的默认流语义。

```c
hggcError_t hggcGraphLaunch (hggcGraphExec_t graphExec, hggcStream_t stream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| graphExec | in | 要启动的可执行图 |
| stream | in | 启动图的流 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphMemAllocNodeGetParams

获取内存分配节点的当前参数。

```c
hggcError_t hggcGraphMemAllocNodeGetParams (hggcGraphNode_t node,
                                            hggcMemAllocNodeParams* params_out)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| node | in | 内存分配节点 |
| params_out | out | 返回的节点参数 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphMemFreeNodeGetParams

获取内存释放节点的当前参数。

```c
hggcError_t hggcGraphMemFreeNodeGetParams (hggcGraphNode_t node, void* dptr_out)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| node | in | 内存释放节点 |
| dptr_out | out | 返回的设备指针 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphMemcpyNodeGetParams

获取 memcpy 节点的当前参数。

```c
hggcError_t hggcGraphMemcpyNodeGetParams (hggcGraphNode_t node,
                                          hggcMemcpy3DParms* pNodeParams)
```

参数同上（pNodeParams out）。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphMemcpyNodeSetParams

更新 memcpy 节点的参数。

```c
hggcError_t hggcGraphMemcpyNodeSetParams (hggcGraphNode_t node,
                                          const hggcMemcpy3DParms* pNodeParams)
```

参数同上（pNodeParams in）。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphMemcpyNodeSetParams1D

更新 memcpy 节点参数为一维拷贝。

```c
hggcError_t hggcGraphMemcpyNodeSetParams1D (hggcGraphNode_t node,
                                            void* dst,
                                            const void* src,
                                            size_t count,
                                            hggcMemcpyKind kind)
```

参数：node、dst、src、count、kind，均 in。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphMemcpyNodeSetParamsFromSymbol

更新 memcpy 节点参数为从符号拷贝。

```c
hggcError_t hggcGraphMemcpyNodeSetParamsFromSymbol (hggcGraphNode_t node,
                                                    void* dst,
                                                    const void* symbol,
                                                    size_t count,
                                                    size_t offset,
                                                    hggcMemcpyKind kind)
```

参数：node、dst、symbol、count、offset、kind，均 in。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphMemcpyNodeSetParamsToSymbol

更新 memcpy 节点参数为向符号拷贝。

```c
hggcError_t hggcGraphMemcpyNodeSetParamsToSymbol (hggcGraphNode_t node,
                                                  const void* symbol,
                                                  const void* src,
                                                  size_t count,
                                                  size_t offset,
                                                  hggcMemcpyKind kind)
```

参数：node、symbol、src、count、offset、kind，均 in。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphMemsetNodeGetParams

获取 memset 节点的当前参数。

```c
hggcError_t hggcGraphMemsetNodeGetParams (hggcGraphNode_t node,
                                          hggcMemsetParams* pNodeParams)
```

参数同上（pNodeParams out）。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphMemsetNodeSetParams

更新 memset 节点的参数。

```c
hggcError_t hggcGraphMemsetNodeSetParams (hggcGraphNode_t node,
                                          const hggcMemsetParams* pNodeParams)
```

参数同上（pNodeParams in）。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphNodeFindInClone

在克隆图中查找对应于原始节点的克隆节点。

```c
hggcError_t hggcGraphNodeFindInClone (hggcGraphNode_t* pNode,
                                      hggcGraphNode_t originalNode,
                                      hggcGraph_t clonedGraph)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| pNode | out | 返回克隆节点句柄 |
| originalNode | in | 原始节点 |
| clonedGraph | in | 克隆的图 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphNodeGetDependencies

获取节点的所有前置依赖节点。

```c
hggcError_t hggcGraphNodeGetDependencies (hggcGraphNode_t node,
                                          hggcGraphNode_t* pDependencies,
                                          hggcGraphEdgeData* edgeData,
                                          size_t* pNumDependencies)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| node | in | 要查询的节点 |
| pDependencies | out | 返回的依赖节点数组 |
| edgeData | out | 返回的边数据数组 |
| pNumDependencies | out | 输入/输出：依赖数量 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphNodeGetDependentNodes

获取所有依赖于此节点的节点列表。

```c
hggcError_t hggcGraphNodeGetDependentNodes (hggcGraphNode_t node,
                                            hggcGraphNode_t* pDependentNodes,
                                            hggcGraphEdgeData* edgeData,
                                            size_t* pNumDependentNodes)
```

参数同上（pDependentNodes 为返回的依赖节点数组，pNumDependentNodes 为依赖节点数量）。

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphNodeGetType

获取图节点的类型（`hggcGraphNodeType`：核函数、memcpy、memset 等）。

```c
hggcError_t hggcGraphNodeGetType (hggcGraphNode_t node,
                                  hggcGraphNodeType * pType)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| node | in | 图节点 |
| pType | out | 返回的节点类型 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphNodeSetParams

更新图中节点的参数（通用形态，按 `nodeParams->type` 解释）。

```c
hggcError_t hggcGraphNodeSetParams (hggcGraphNode_t node,
                                    hggcGraphNodeParams* nodeParams)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| node | in | 图节点 |
| nodeParams | in | 新的节点参数 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphReleaseUserObject

释放图对用户对象的引用。引用计数到零时调用销毁回调。

```c
hggcError_t hggcGraphReleaseUserObject (hggcGraph_t graph,
                                        hggcUserObject_t object,
                                        unsigned int count = 1)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| graph | in | 图 |
| object | in | 用户对象 |
| count | in | 要释放的引用数量 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphRemoveDependencies

从图中移除指定的依赖边。

```c
hggcError_t hggcGraphRemoveDependencies (hggcGraph_t graph,
                                         const hggcGraphNode_t* from,
                                         const hggcGraphNode_t* to,
                                         const hggcGraphEdgeData* edgeData,
                                         size_t numDependencies)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| graph | in | 要移除依赖的图 |
| from | in | 提供依赖的节点数组 |
| to | in | 依赖节点数组 |
| edgeData | in | 可选的边数据数组 |
| numDependencies | in | 要移除的依赖数量 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphRetainUserObject

增加图对用户对象的引用计数。

```c
hggcError_t hggcGraphRetainUserObject (hggcGraph_t graph,
                                       hggcUserObject_t object,
                                       unsigned int count = 1,
                                       unsigned int flags = 0)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| graph | in | 图 |
| object | in | 用户对象 |
| count | in | 要保留的引用数量 |
| flags | in | 标志位（见 `hggcUserObjectRetainFlags`） |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcGraphUpload

将可执行图的代码和数据上传到 PPU。可选调用：在启动前预热以减少首次启动延迟。

```c
hggcError_t hggcGraphUpload (hggcGraphExec_t graphExec, hggcStream_t stream)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| graphExec | in | 可执行图 |
| stream | in | 上传操作的流 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcUserObjectCreate

创建一个用户对象，可被图保留和释放。引用计数到零时调用销毁回调。

```c
hggcError_t hggcUserObjectCreate (hggcUserObject_t* object_out,
                                  void* ptr,
                                  hggcHostFn_t destroy,
                                  unsigned int initialRefcount,
                                  unsigned int flags)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| object_out | out | 返回的用户对象句柄 |
| ptr | in | 用户数据指针 |
| destroy | in | 销毁回调函数 |
| initialRefcount | in | 初始引用计数 |
| flags | in | 创建标志（见 `hggcUserObjectFlags`） |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcUserObjectRelease

减少用户对象的引用计数。计数到零时调用销毁回调。

```c
hggcError_t hggcUserObjectRelease (hggcUserObject_t object,
                                   unsigned int count = 1)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| object | in | 用户对象 |
| count | in | 要释放的引用数量 |

错误码：hggcSuccess、hggcErrorInvalidValue

#### hggcUserObjectRetain

增加用户对象的引用计数。

```c
hggcError_t hggcUserObjectRetain (hggcUserObject_t object,
                                  unsigned int count = 1)
```

参数同上。

错误码：hggcSuccess、hggcErrorInvalidValue

比赛关联：HGGC Graph 是压 TTFT 的重磅手段——把 decode 迭代中固定的 kernel 序列经 `hggcStreamBeginCapture`/`hggcStreamEndCapture` 捕获为图后 `hggcGraphLaunch` 重放，消除逐 kernel 启动开销；`hggcGraphUpload` 预热 + `hggcGraphExecKernelNodeSetParams` 就地改参（换 KV cache 指针、seq len）可避免重复实例化。注意图更新受拓扑兼容约束（见 `hggcGraphExecUpdateResult`）。

## 互操作与扩展

本节涵盖与外部图形/计算 API 之间的资源共享机制，包括外部内存与信号量的导入导出。

### 外部资源互操作

| 函数 | 用途 |
|------|------|
| `hggcSignalExternalSemaphoresAsync` | 向一组外部信号量对象发送信号 |
| `hggcWaitExternalSemaphoresAsync` | 等待一组外部信号量对象 |

#### hggcSignalExternalSemaphoresAsync

在指定流中对一组外部分配的信号量对象排队信号操作。当流中所有先前的操作完成时执行。发送信号的确切语义取决于对象类型：

- 信号量对象为 `hggcExternalSemaphoreHandleTypeOpaqueFd`、`OpaqueWin32`、`OpaqueWin32Kmt` 之一时，发送信号使其进入已发信号（signaled）状态。
- 对象为 `hggcExternalSemaphoreHandleTypeHgSciSync` 类型时，此 API 将 `params::hgSciSync::fence` 设置为一个值，供同一 HgSciSync 对象的后续等待者按顺序排列与当前提交到流中的操作；此更新覆盖 fence 之前的内容。

默认情况下，发送信号会导致对所有以 `hggcExternalMemoryHandleTypeHgSciBuf` 导入的外部内存对象执行适当的内存同步操作，确保同一组 HgSciBuf 内存对象的其他导入者的后续访问一致。指定 `hggcExternalSemaphoreSignalSkipHgSciBufMemSync` 标志可跳过这些操作——不需要数据一致性时是性能优化；需要一致性时指定此标志行为未定义。

此外，`hggcExternalSemaphoreHandleTypeHgSciSync` 类型的对象，若创建 HgSciSyncObj 的 HgSciSyncAttrList 未在 flags 字段设置 `hggcHgSciSyncAttrSignal`，此 API 返回 `hggcErrorNotSupported`。

`hggcExternalSemaphoreHandleTypeHgSciSync` 类型对象的 `params::hgSciSync::fence` 可以是**确定性的（deterministic）**：创建信号量对象的 HgSciSyncAttrList 须将 `HgSciSyncAttrKey_RequireDeterministicFences` 键设为 true。确定性 fence 允许用户甚至在排队相应信号之前就对信号量对象排队等待。HGGC 保证每次信号操作将 fence 值增加 1；用户应跟踪排队的信号计数并相应插入等待。从多个流向此类对象发送信号时，因流的并发执行，信号顺序可能不确定，可能导致等待者被错误地取消阻塞——用户应避免在不同流中使用启用了确定性 fence 的同一信号量对象，或在流之间添加显式依赖以保证按顺序发送信号。

fence 也可以**启用时间戳（timestamp enabled）**：创建对象的 HgSciSyncAttrList 须将 `HgSciSyncAttrKey_WaiterRequireTimestamps` 键设为 true。时间戳由 PPU 异步发出，HGGC 在 PPU 发出信号时将 PPU 时间戳保存在相应的 HgSciSyncFence 中。用户应使用适当的缩放函数将 PPU 时钟转换为 CPU 时钟；应在等待 fence 完成后再用适当的 HgSciSync API 提取时间戳。任何时间点每个 HGGC-HgSciSync 对象只能有一个未处理的启用时间戳的 fence，否则行为未定义；在相应信号发出前提取时间戳行为未定义。提取的时间戳单位为微秒。

```c
hggcError_t hggcSignalExternalSemaphoresAsync (const hggcExternalSemaphore_t* extSemArray,
                                               const hggcExternalSemaphoreSignalParams* paramsArray,
                                               unsigned int numExtSems,
                                               hggcStream_t stream = 0)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| extSemArray | in | 要发送信号的外部信号量集合 |
| paramsArray | in | 信号量参数数组 |
| numExtSems | in | 要发送信号的信号量数量 |
| stream | in | 排队信号操作的流 |

错误码：hggcSuccess、hggcErrorInvalidResourceHandle

#### hggcWaitExternalSemaphoresAsync

在指定流中对一组外部分配的信号量对象排队等待操作。当流中所有先前的操作完成时执行。等待语义取决于对象类型：

- `hggcExternalSemaphoreHandleTypeOpaqueFd`/`OpaqueWin32`/`OpaqueWin32Kmt`：等待直到信号量达到已发信号状态，然后重置为未发信号状态——每个信号操作只能有一个等待操作。
- `hggcExternalSemaphoreHandleTypeHgSciSync`：等待直到与该对象关联的 HgSciSyncObj 的发送者发出了 `params::hgSciSync::fence` 信号。

默认情况下，等待会导致对所有以 `hggcExternalMemoryHandleTypeHgSciBuf` 导入的外部内存对象执行适当的内存同步操作（保证一致性）；指定 `hggcExternalSemaphoreWaitSkipHgSciBufMemSync` 标志可跳过（语义与注意事项同上）。`hggcExternalSemaphoreHandleTypeHgSciSync` 类型对象，若创建时 HgSciSyncAttrList 未设 `hggcHgSciSyncAttrWait`，返回 `hggcErrorNotSupported`。

```c
hggcError_t hggcWaitExternalSemaphoresAsync (const hggcExternalSemaphore_t* extSemArray,
                                             const hggcExternalSemaphoreWaitParams* paramsArray,
                                             unsigned int numExtSems,
                                             hggcStream_t stream = 0)
```

| 参数 | 方向 | 说明 |
|------|------|------|
| extSemArray | in | 要等待的外部信号量集合 |
| paramsArray | in | 信号量参数数组 |
| numExtSems | in | 要等待的信号量数量 |
| stream | in | 排队等待操作的流 |

错误码：hggcSuccess、hggcErrorInvalidResourceHandle、hggcErrorTimeout

## 参考索引

本节提供 HGGC Runtime API 的辅助参考索引：数据结构清单（按字母序）与数据字段索引（按字段名字母序，标注每个字段出现在哪些类型中）。

### 数据结构索引

按字母序汇总 Runtime API 暴露的全部数据结构（含 struct、union、class）。各类型字段含义与使用约束见相应 API 章节及数据类型节。

- `__hggcOccupancyB2DHelper`
- `hggcAccessPolicyWindow`
- `hggcArrayMemoryRequirements`
- `hggcArraySparseProperties`
- `hggcAsyncNotificationInfo_t`
- `hggcChildGraphNodeParams`
- `hggcConditionalNodeParams`
- `hggcDeviceProp`
- `hggcEventRecordNodeParams`
- `hggcEventWaitNodeParams`
- `hggcExtent`
- `hggcFuncAttributes`
- `hggcGraphEdgeData`
- `hggcGraphExecUpdateResultInfo`
- `hggcGraphInstantiateParams`
- `hggcGraphKernelNodeUpdate`
- `hggcGraphNodeParams`
- `hggcHostNodeParams`
- `hggcHostNodeParamsV2`
- `hggcIpcEventHandle_t`
- `hggcIpcMemHandle_t`
- `hggcKernelNodeParams`
- `hggcKernelNodeParamsV2`
- `hggcLaunchAttribute`
- `hggcLaunchAttributeValue`（union）
- `hggcLaunchConfig_t`
- `hggcMemAccessDesc`
- `hggcMemAllocNodeParams`
- `hggcMemAllocNodeParamsV2`
- `hggcMemFreeNodeParams`
- `hggcMemLocation`
- `hggcMemPoolProps`
- `hggcMemPoolPtrExportData`
- `hggcMemcpy3DOperand`
- `hggcMemcpy3DParms`
- `hggcMemcpy3DPeerParms`
- `hggcMemcpyAttributes`
- `hggcMemcpyNodeParams`
- `hggcMemsetParams`
- `hggcMemsetParamsV2`
- `hggcOffset3D`
- `hggcPitchedPtr`
- `hggcPointerAttributes`
- `hggcPos`
- `HGuuid_st`

### 数据字段索引

按字母序列出各数据结构的字段，每个字段标注它出现在哪些类型中（`字段 — 类型1、类型2`）：

**A**

- accessDescCount — `hggcMemAllocNodeParams`、`hggcMemAllocNodeParamsV2`
- accessDescs — `hggcMemAllocNodeParams`、`hggcMemAllocNodeParamsV2`
- accessPolicyMaxWindowSize — `hggcDeviceProp`
- accessPolicyWindow — `hggcLaunchAttributeValue`
- alignment — `hggcArrayMemoryRequirements`
- alloc — `hggcGraphNodeParams`
- allocType — `hggcMemPoolProps`
- array — `hggcMemcpy3DOperand`
- asyncEngineCount — `hggcDeviceProp`
- attrs — `hggcLaunchConfig_t`

**B**

- base_ptr — `hggcAccessPolicyWindow`
- binaryVersion — `hggcFuncAttributes`
- blockDim — `hggcKernelNodeParams`、`hggcKernelNodeParamsV2`、`hggcLaunchConfig_t`
- bytes — `HGuuid_st`
- bytesize — `hggcMemAllocNodeParams`、`hggcMemAllocNodeParamsV2`
- bytesOverBudget — `hggcAsyncNotificationInfo_t`

**C**

- cacheModeCA — `hggcFuncAttributes`
- canMapHostMemory — `hggcDeviceProp`
- canUseHostPointerForRegisteredMem — `hggcDeviceProp`
- clusterDim — `hggcLaunchAttributeValue`
- clusterDimMustBeSet — `hggcFuncAttributes`
- clusterLaunch — `hggcDeviceProp`
- clusterSchedulingPolicyPreference — `hggcFuncAttributes`、`hggcLaunchAttributeValue`
- computePreemptionSupported — `hggcDeviceProp`
- concurrentKernels — `hggcDeviceProp`
- concurrentManagedAccess — `hggcDeviceProp`
- conditional — `hggcGraphNodeParams`
- constSizeBytes — `hggcFuncAttributes`
- cooperative — `hggcLaunchAttributeValue`
- cooperativeLaunch — `hggcDeviceProp`
- copyParams — `hggcMemcpyNodeParams`
- hgFunc — `hggcKernelNodeParamsV2`

**D**

- deferredMappingHggcArraySupported — `hggcDeviceProp`
- depth — `hggcArraySparseProperties`、`hggcExtent`
- device — `hggcPointerAttributes`
- deviceNumaConfig — `hggcDeviceProp`
- deviceNumaId — `hggcDeviceProp`
- devicePointer — `hggcPointerAttributes`
- deviceUpdatableKernelNode — `hggcLaunchAttributeValue`
- directManagedMemAccessFromHost — `hggcDeviceProp`
- dptr — `hggcMemAllocNodeParams`、`hggcMemAllocNodeParamsV2`、`hggcMemFreeNodeParams`
- dst — `hggcMemsetParams`、`hggcMemsetParamsV2`
- dstArray — `hggcMemcpy3DParms`、`hggcMemcpy3DPeerParms`
- dstDevice — `hggcMemcpy3DPeerParms`
- dstLocHint — `hggcMemcpyAttributes`
- dstPos — `hggcMemcpy3DParms`、`hggcMemcpy3DPeerParms`
- dstPtr — `hggcMemcpy3DParms`、`hggcMemcpy3DPeerParms`
- dynamicSmemBytes — `hggcLaunchConfig_t`

**E**

- ECCEnabled — `hggcDeviceProp`
- elementSize — `hggcMemsetParams`、`hggcMemsetParamsV2`
- errNode_out — `hggcGraphInstantiateParams`
- errorFromNode — `hggcGraphExecUpdateResultInfo`
- errorNode — `hggcGraphExecUpdateResultInfo`
- event — `hggcEventRecordNodeParams`、`hggcEventWaitNodeParams`
- eventRecord — `hggcGraphNodeParams`
- eventWait — `hggcGraphNodeParams`
- extent — `hggcMemcpy3DParms`、`hggcMemcpy3DPeerParms`
- extra — `hggcKernelNodeParams`、`hggcKernelNodeParamsV2`
- extSemSignal — `hggcGraphNodeParams`
- extSemWait — `hggcGraphNodeParams`

**F**

- field — `hggcGraphKernelNodeUpdate`
- flags — `hggcMemcpyAttributes`、`hggcExternalSemaphoreWaitParams`、`hggcArraySparseProperties`、`hggcMemAccessDesc`、`hggcGraphInstantiateParams`、`hggcMemcpyNodeParams`
- fn — `hggcHostNodeParams`、`hggcHostNodeParamsV2`
- formatDesc — （独立字段项）
- free — `hggcGraphNodeParams`
- from_port — `hggcGraphEdgeData`
- func — `hggcKernelNodeParams`、`hggcKernelNodeParamsV2`
- functionType — `hggcKernelNodeParamsV2`

**G**

- globalL1CacheSupported — `hggcDeviceProp`
- gpuDirectRDMAFlushWritesOptions — `hggcDeviceProp`
- gpuDirectRDMASupported — `hggcDeviceProp`
- gpuDirectRDMAWritesOrdering — `hggcDeviceProp`
- gpuPciDeviceID — `hggcDeviceProp`
- gpuPciSubsystemID — `hggcDeviceProp`
- graph — `hggcGraphNodeParams`、`hggcChildGraphNodeParams`
- gridDim — `hggcKernelNodeParams`、`hggcKernelNodeParamsV2`、`hggcGraphKernelNodeUpdate`、`hggcLaunchConfig_t`

**H**

- handle — `hggcConditionalNodeParams`
- handleTypes — `hggcMemPoolProps`
- height — `hggcMemsetParams`、`hggcMemsetParamsV2`、`hggcArraySparseProperties`、`hggcExtent`
- hitProp — `hggcAccessPolicyWindow`
- hitRatio — `hggcAccessPolicyWindow`
- host — `hggcGraphNodeParams`
- hostNativeAtomicSupported — `hggcDeviceProp`
- hostNumaId — `hggcDeviceProp`
- hostNumaMultinodeIpcSupported — `hggcDeviceProp`
- hostPointer — `hggcPointerAttributes`
- hostRegisterReadOnlySupported — `hggcDeviceProp`
- hostRegisterSupported — `hggcDeviceProp`

**I**

- id — `hggcMemLocation`、`hggcLaunchAttribute`
- info — `hggcAsyncNotificationInfo_t`
- integrated — `hggcDeviceProp`
- ipcEventSupported — `hggcDeviceProp`
- isEnabled — `hggcGraphKernelNodeUpdate`
- isMultiGpuBoard — `hggcDeviceProp`

**K**

- kern — `hggcKernelNodeParamsV2`
- kernel — `hggcGraphNodeParams`
- kernelParams — `hggcKernelNodeParams`
- kind — `hggcMemcpy3DParms`

**L**

- l2CacheSize — `hggcDeviceProp`
- launchCompletionEvent — `hggcLaunchAttributeValue`
- layerHeight — `hggcMemcpy3DOperand`
- localL1CacheSupported — `hggcDeviceProp`
- localSizeBytes — `hggcFuncAttributes`
- location — `hggcMemPoolProps`、`hggcMemAccessDesc`
- locHint — `hggcMemcpy3DOperand`
- luid — `hggcDeviceProp`
- luidDeviceNodeMask — `hggcDeviceProp`

**M**

- major — `hggcDeviceProp`
- managedMemory — `hggcDeviceProp`
- maxBlocksPerMultiProcessor — `hggcDeviceProp`
- maxDynamicSharedSizeBytes — `hggcFuncAttributes`
- maxGridSize — `hggcDeviceProp`
- maxSize — `hggcMemPoolProps`
- maxSurface1D — `hggcDeviceProp`
- maxSurface1DLayered — `hggcDeviceProp`
- maxSurface2D — `hggcDeviceProp`
- maxSurface2DLayered — `hggcDeviceProp`
- maxSurface3D — `hggcDeviceProp`
- maxSurfaceCubemap — `hggcDeviceProp`
- maxSurfaceCubemapLayered — `hggcDeviceProp`
- maxTexture1D — `hggcDeviceProp`
- maxTexture1DLayered — `hggcDeviceProp`
- maxTexture1DMipmap — `hggcDeviceProp`
- maxTexture2D — `hggcDeviceProp`
- maxTexture2DGather — `hggcDeviceProp`
- maxTexture2DLayered — `hggcDeviceProp`
- maxTexture2DLinear — `hggcDeviceProp`
- maxTexture2DMipmap — `hggcDeviceProp`
- maxTexture3D — `hggcDeviceProp`
- maxTexture3DAlt — `hggcDeviceProp`
- maxTextureCubemap — `hggcDeviceProp`
- maxTextureCubemapLayered — `hggcDeviceProp`
- maxThreadsDim — `hggcDeviceProp`
- maxThreadsPerBlock — `hggcFuncAttributes`、`hggcDeviceProp`
- maxThreadsPerMultiProcessor — `hggcDeviceProp`
- memcpy — `hggcGraphNodeParams`
- memoryBusWidth — `hggcDeviceProp`
- memoryPoolsSupported — `hggcDeviceProp`
- memoryPoolSupportedHandleTypes — `hggcDeviceProp`
- memPitch — `hggcDeviceProp`
- memset — `hggcGraphNodeParams`
- memSyncDomain — `hggcLaunchAttributeValue`
- memSyncDomainMap — `hggcLaunchAttributeValue`
- minor — `hggcDeviceProp`
- miptailFirstLevel — `hggcArraySparseProperties`
- miptailSize — `hggcArraySparseProperties`
- missProp — `hggcAccessPolicyWindow`
- mpsEnabled — `hggcDeviceProp`
- multiGpuBoardGroupID — `hggcDeviceProp`
- multiProcessorCount — `hggcDeviceProp`

**N**

- name — `hggcDeviceProp`
- node — `hggcGraphKernelNodeUpdate`
- nonPortableClusterSizeAllowed — `hggcFuncAttributes`
- num_bytes — `hggcAccessPolicyWindow`
- numAttrs — `hggcLaunchConfig_t`
- numLevels — （独立字段项）
- numRegs — `hggcFuncAttributes`
- icnlinkUtilCentricScheduling — `hggcLaunchAttributeValue`

**O**

- offset — `hggcGraphKernelNodeUpdate`
- overBudget — `hggcAsyncNotificationInfo_t`
- ownership — `hggcChildGraphNodeParams`

**P**

- pageableMemoryAccess — `hggcDeviceProp`
- pageableMemoryAccessUsesHostPageTables — `hggcDeviceProp`
- param — `hggcGraphKernelNodeUpdate`
- pciBusID — `hggcDeviceProp`
- pciDeviceID — `hggcDeviceProp`
- pciDomainID — `hggcDeviceProp`
- persistingL2CacheMaxSize — `hggcDeviceProp`
- phGraph_out — `hggcConditionalNodeParams`
- pitch — `hggcMemsetParams`、`hggcMemsetParamsV2`、`hggcPitchedPtr`
- poolProps — `hggcMemAllocNodeParams`、`hggcMemAllocNodeParamsV2`
- portableClusterSizeMode — `hggcLaunchAttributeValue`
- preferredClusterDim — `hggcLaunchAttributeValue`
- preferredShmemCarveout — `hggcFuncAttributes`
- priority — `hggcLaunchAttributeValue`
- programmaticEvent — `hggcLaunchAttributeValue`
- programmaticStreamSerializationAllowed — `hggcLaunchAttributeValue`
- ptr — `hggcPitchedPtr`、`hggcMemcpy3DOperand`
- tixVersion — `hggcFuncAttributes`
- pValue — `hggcGraphKernelNodeUpdate`

**R**

- regsPerBlock — `hggcDeviceProp`
- regsPerMultiprocessor — `hggcDeviceProp`
- requiredClusterWidth — `hggcFuncAttributes`
- reserved — `hggcPointerAttributes`、`hggcGraphEdgeData`、`hggcFuncAttributes`、`hggcMemPoolProps`、`hggcDeviceProp`、`hggcMemcpyNodeParams`
- reserved0 — `hggcGraphNodeParams`
- reserved1 — `hggcGraphNodeParams`
- reserved2 — `hggcGraphNodeParams`
- reservedSharedMemPerBlock — `hggcDeviceProp`
- result — `hggcGraphExecUpdateResultInfo`
- result_out — `hggcGraphInstantiateParams`
- rowLength — `hggcMemcpy3DOperand`

**S**

- sharedMemBytes — `hggcKernelNodeParams`、`hggcKernelNodeParamsV2`
- sharedMemCarveout — `hggcLaunchAttributeValue`
- sharedMemPerBlock — `hggcDeviceProp`
- sharedMemPerBlockOptin — `hggcDeviceProp`
- sharedMemPerMultiprocessor — `hggcDeviceProp`
- sharedSizeBytes — `hggcFuncAttributes`
- size — `hggcArrayMemoryRequirements`、`hggcConditionalNodeParams`、`hggcGraphKernelNodeUpdate`
- sparseHggcArraySupported — `hggcDeviceProp`
- srcAccessOrder — `hggcMemcpyAttributes`
- srcArray — `hggcMemcpy3DParms`、`hggcMemcpy3DPeerParms`
- srcDevice — `hggcMemcpy3DPeerParms`
- srcLocHint — `hggcMemcpyAttributes`
- srcPos — `hggcMemcpy3DParms`、`hggcMemcpy3DPeerParms`
- srcPtr — `hggcMemcpy3DParms`、`hggcMemcpy3DPeerParms`
- stream — `hggcLaunchConfig_t`
- streamPrioritiesSupported — `hggcDeviceProp`
- surfaceAlignment — `hggcDeviceProp`
- syncMode — `hggcHostNodeParamsV2`
- syncPolicy — `hggcLaunchAttributeValue`

**T**

- tccDriver — `hggcDeviceProp`
- textureAlignment — `hggcDeviceProp`
- texturePitchAlignment — `hggcDeviceProp`
- timelineSemaphoreInteropSupported — `hggcDeviceProp`
- timeoutMs — `hggcExternalSemaphoreWaitParams`
- to_port — `hggcGraphEdgeData`
- totalConstMem — `hggcDeviceProp`
- totalGlobalMem — `hggcDeviceProp`
- type — `hggcMemLocation`、`hggcPointerAttributes`、`hggcGraphNodeParams`、`hggcConditionalNodeParams`

**U**

- unifiedAddressing — `hggcDeviceProp`
- unifiedFunctionPointers — `hggcDeviceProp`
- updateData — `hggcGraphKernelNodeUpdate`
- uploadStream — `hggcGraphInstantiateParams`
- usage — `hggcMemPoolProps`
- userData — `hggcHostNodeParams`、`hggcHostNodeParamsV2`
- uuid — `hggcDeviceProp`

**V**

- val — `hggcLaunchAttribute`
- value — `hggcExternalSemaphoreWaitParams`、`hggcMemsetParams`、`hggcMemsetParamsV2`

**W**

- warpSize — `hggcDeviceProp`
- width — `hggcArraySparseProperties`、`hggcExtent`、`hggcMemsetParams`、`hggcMemsetParamsV2`
- win32SecurityAttributes — `hggcMemPoolProps`

**X**

- x — `hggcPos`
- xsize — `hggcPitchedPtr`

**Y**

- y — `hggcPos`
- ysize — `hggcPitchedPtr`

**Z**

- z — `hggcPos`
