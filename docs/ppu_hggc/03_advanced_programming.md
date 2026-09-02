# 第 3 章 进阶编程 <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [3.1 HGGC 底层驱动接口](#31-hggc-底层驱动接口)
  - [3.1.0 驱动 API 的基本形态](#310-驱动-api-的基本形态)
  - [3.1.0.1 驱动 API 使用流程（完整主机端示例）](#3101-驱动-api-使用流程完整主机端示例)
  - [3.1.1 上下文 (Context)](#311-上下文-context)
  - [3.1.2 模块 (Module)](#312-模块-module)
  - [3.1.3 核函数执行 (Kernel Execution)](#313-核函数执行-kernel-execution)
  - [3.1.4 运行时 API 与驱动程序 API 之间的互操作性](#314-运行时-api-与驱动程序-api-之间的互操作性)
- [3.2 多设备协同编程](#32-多设备协同编程)
  - [3.2.0 多 PPU 编程的常见方式](#320-多-ppu-编程的常见方式)
  - [3.2.0.1 统一虚拟寻址与 IPC](#3201-统一虚拟寻址与-ipc)
  - [3.2.1 多设备上下文与执行管理](#321-多设备上下文与执行管理)
  - [3.2.2 多设备点对点（Peer-to-Peer）传输与内存访问](#322-多设备点对点peer-to-peer传输与内存访问)
- [本章要点速查](#本章要点速查)


> 本章涵盖两大部分：
> - **§3.1 HGGC 底层驱动接口**：驱动 API 的初始化、Context、Module、核函数执行、与运行时 API 的互操作。
> - **§3.2 多设备协同编程**：设备枚举与选择、多设备流/事件行为、P2P 传输与访问、多卡一致性、IOMMU 注意事项。

---

## 3.1 HGGC 底层驱动接口

本指南的前几节涵盖了 HGGC 运行时（Runtime）。如"HGGC 运行时 API"和"HGGC 驱动程序 API"中所述，**HGGC 运行时是在底层的 HGGC 驱动程序 API 之上构建的**。本节介绍 HGGC 运行时与驱动程序 API 之间的区别，以及如何混合使用它们。

- 大多数应用程序**无需与驱动程序 API 交互**即可实现全性能运行。
- 然而，**驱动程序 API 有时会比运行时 API 更早提供新的接口**——需要新特性时可以直接用驱动 API。

### 3.1.0 驱动 API 的基本形态

- 驱动程序 API 实现在 **hggc 动态库（`hggc.so`）** 中，该库在安装设备驱动程序时被复制到系统中。
- 其所有入口点都以 **`hg` 为前缀**。
- 它是一个**基于句柄的命令式 API**：大多数对象通过不透明句柄进行引用，这些句柄可以传递给函数以操作相应的对象。

#### 表 2：HGGC 驱动程序 API 中可用的对象

| 对象 | 句柄 | 描述 |
|---|---|---|
| 设备 (Device) | `HGdevice` | 支持 HGGC 的设备 |
| 上下文 (Context) | `HGcontext` | 大致等同于一个 CPU 进程 |
| 模块 (Module) | `HGmodule` | 大致等同于一个动态库 |
| 函数 (Function) | `HGfunction` | 核函数 (Kernel) |
| 堆内存 (Heap memory) | `HGdeviceptr` | 指向设备内存的指针 |
| HGGC 数组 (HGGC array) | `HGarray` | 设备上一维或二维数据的不透明容器，可通过纹理或表面引用读取 |
| 纹理对象 (Texture object) | `HGtexref` | 描述如何解释纹理内存数据的对象 |
| 流 (Stream) | `HGstream` | 描述 HGGC 流的对象 |
| 事件 (Event) | `HGevent` | 描述 HGGC 事件的对象 |

### 3.1.0.1 驱动 API 使用流程（完整主机端示例）

在调用驱动程序 API 的任何函数之前，必须先用 **`hgInit()`** 初始化驱动程序 API。随后必须创建一个 HGGC 上下文，将其附加到特定设备，并使其成为当前调用主机线程的上下文。

在 HGGC 上下文中，核函数由主机代码作为**二进制对象显式加载**（见"模块"部分）。因此，用 C++ 编写的核函数必须**单独编译为二进制对象**。核函数通过 API 入口点启动。

以下是使用驱动程序 API 编写的核函数示例代码的主机部分（照录原文，含 V2/V3 接口差异注释）：

```cpp
int main()
{
    int numElements = ...;
    size_t bufBytes = numElements * sizeof(float);
    // 在主机端准备输入数据
    float* hostInput = (float*)malloc(bufBytes);
    float* hostOutput = (float*)malloc(bufBytes);
    // 填充 hostInput ...
    // 初始化驱动程序 API
    hgInit(0);
    // 枚举可用设备
    int devCount = 0;
    hgDeviceGetCount(&devCount);
    if (devCount == 0) {
        printf("No HGGC‑capable device found.\n");
        exit(0);
    }
    // 选取第一个设备并创建上下文
    HGdevice dev;
    hgDeviceGet(&dev, 0);
    HGcontext ctx;
    // V2: hgCtxCreate(&ctx, 0, dev);
    // V3: 新增第2参数 HGctxCreateParams*，传 NULL 表示创建常规上下文
    hgCtxCreate(&ctx, NULL, 0, dev);
    // 加载预编译的 HGBIN 模块
    HGmodule mod;
    hgModuleLoadData(&mod, "relu_activate.hgbin");
    // 分配设备内存
    HGdeviceptr devIn, devOut;
    hgMemAlloc(&devIn, bufBytes);
    hgMemAlloc(&devOut, bufBytes);
    // 传输输入数据到设备
    hgMemcpyHtoD(devIn, hostInput, bufBytes);
    // 获取核函数句柄
    HGfunction reluKernel;
    hgModuleGetFunction(&reluKernel, mod, "relu_activate");
    // 配置并启动核函数
    int blockDim = 256;
    int gridDim = (numElements + blockDim ‑ 1) / blockDim;
    void* kernelArgs[] = { &devIn, &devOut, &numElements };
    hgLaunchKernel(reluKernel,
        gridDim, 1, 1, blockDim, 1, 1,
        0, 0, kernelArgs, 0);

    // 取回结果
    hgMemcpyDtoH(hostOutput, devOut, bufBytes);

}

// 清理资源 ...
```

涉及的驱动 API 一览（按出现顺序）：

| API | 作用 |
|---|---|
| `hgInit(0)` | 初始化驱动程序 API（任何驱动 API 调用之前必须调用） |
| `hgDeviceGetCount(&devCount)` | 枚举可用设备数量 |
| `hgDeviceGet(&dev, 0)` | 获取第 0 个设备的句柄 |
| `hgCtxCreate(&ctx, NULL, 0, dev)` | 创建上下文（V3 签名，第 2 参数为 `HGctxCreateParams*`，`NULL` 表示常规上下文；V2 签名为 `hgCtxCreate(&ctx, 0, dev)`） |
| `hgModuleLoadData(&mod, "...hgbin")` | 加载预编译的 HGBIN 模块 |
| `hgMemAlloc(&devPtr, bytes)` | 分配设备内存 |
| `hgMemcpyHtoD(dst, src, bytes)` | 主机→设备传输 |
| `hgModuleGetFunction(&func, mod, "name")` | 按符号名获取核函数句柄 |
| `hgLaunchKernel(...)` | 配置 grid/block 维度并启动核函数 |
| `hgMemcpyDtoH(dst, src, bytes)` | 设备→主机传输 |

**比赛关联**：驱动 API 比运行时 API 更早暴露新接口，且去掉了运行时层的间接开销。比赛中若要压榨 TTFT（如把 kernel 启动路径上的开销降到最低）、或做自定义的 module 预加载（把量化 GEMM/Attention kernel 预编成 `.hgbin` 提前加载，避免运行时 JIT 成本），都需要走驱动 API 这条路径。

---

### 3.1.1 上下文 (Context)

在 HGGC 驱动程序 API 中，**上下文（Context）是驱动程序为单个 PPU 设备维护的运行环境**，承载着该设备上的：

- 地址空间
- 已加载模块
- 内存分配
- 执行状态

可以将其理解为 **PPU 侧的"进程"**——资源隔离于不同上下文之间，销毁上下文时其名下的资源会被**自动回收**。

**地址空间隔离**：除模块、纹理和表面引用等全局符号外，各上下文拥有独立的地址空间，因此**来自不同上下文的 `HGdeviceptr` 值引用的是不同的内存位置**。

#### 线程与上下文的绑定

- 驱动程序 API 要求**每个主机线程在调用大多数 API 之前先拥有一个"当前上下文"**。
- `hgCtxCreate()` 会为指定设备创建新上下文，并**自动将其设为调用线程的当前上下文**。
- 若线程无当前上下文，依赖上下文的 API 调用将返回 **`HGGC_ERROR_INVALID_CONTEXT`**。

#### 上下文栈机制

- HGGC 为**每个主机线程维护一个上下文栈**。
- `hgCtxCreate()` 会将新上下文**压栈**。
- `hgCtxPopCurrent()` **弹出栈顶上下文**并恢复前一个上下文（如有）。
- 被弹出的上下文进入"**浮动**"状态——它不再绑定到任何线程，但仍可通过 `hgCtxPushCurrent()` 被任意线程重新采用。
- 这一机制使得上下文能够**在线程之间灵活迁移**。

#### 引用计数与生命周期

- 每个上下文维护一个**使用计数**。
- `hgCtxCreate()` 创建时计数初始化为 **1**。
- `hgCtxAttach()` 递增、`hgCtxDetach()` 递减。
- 当 `hgCtxDetach()` 或 `hgCtxDestroy()` 使计数**降为零**时，上下文被销毁。

这种引用计数设计的主要价值在于**支持多个库共享同一上下文**：每个库在初始化时调用 `hgCtxAttach()` 获取引用，清理时调用 `hgCtxDetach()` 释放引用，无需了解其他库是否仍在使用该上下文。

对于需要创建私有上下文但不希望影响调用方上下文状态的库，可使用 `hgCtxPushCurrent()` / `hgCtxPopCurrent()` 进行**透明切换**。

#### 与运行时的互操作

驱动程序 API 可与运行时共存。运行时管理的 **primary context** 可通过 **`hgDevicePrimaryCtxRetain()`** 获取（详见"运行时初始化"章节），使得同一应用中混合使用两套 API 成为可能。

**比赛关联**：在推理框架（如自研 serving 层）中，多线程 worker 各自 push/pop 上下文即可安全地共享同一设备，不必每线程建 context（建 context 开销大）。写 C++ 扩展库时用 `hgCtxAttach`/`hgCtxDetach` 引用计数模式，可避免与宿主进程（如 Python 运行时持有 primary context）互相销毁资源——这是把 PPU kernel 嵌入现有 VLM 推理 pipeline 的关键机制。

---

### 3.1.2 模块 (Module)

在 HGGC 驱动程序 API 中，**模块（Module）是封装设备端可执行代码与数据的动态加载单元**。

- `hgcc` 支持将代码编译成 **hgbin**，或者将多个 hgbin 打包成 **fatbin**（参见"HGbins and HGFatbins"章节）。
- 运行时通过 **`hgModuleLoad()`** 或 **`hgModuleLoadData()`** 将这些载荷加载到当前上下文中，即可获得对其中**核函数、全局变量以及纹理/表面引用**的访问。

**符号作用域隔离**：模块内的符号名称遵循**模块级作用域隔离**。这意味着由不同团队或第三方独立编写的多个模块可以同时加载到同一个上下文中，彼此的符号互不冲突——开发者通过 `hgModuleGetFunction()` 等 API **显式指定模块与符号名**来获取句柄。

以下示例展示了如何从预编译的 HGBIN 文件中加载模块并获取核函数句柄（照录原文）：

```cpp
HGmodule mod;
hgModuleLoad(&mod, "image_processing.hgbin");
HGfunction filterFunc;
hgModuleGetFunction(&filterFunc, mod, "apply_filter");
```

**比赛关联**：把优化过的 kernel（如 W4A16 量化 GEMM、融合 RoPE+Attention 的 kernel）离线用 `hgcc` 编成 hgbin/fatbin，服务启动时一次性 `hgModuleLoad`，之后 `hgModuleGetFunction` 拿句柄直接 `hgLaunchKernel`——绕过运行时的即时编译/加载路径，是压低首 token 延迟（TTFT）和冷启动时间的直接手段。模块级符号隔离也意味着可以安全混用自家 kernel 与第三方库。

---

### 3.1.3 核函数执行 (Kernel Execution)

驱动程序 API 通过 **`hgLaunchKernel()`** 启动核函数。调用者需要在启动时提供：

- **网格与线程块维度**（执行配置）
- 核函数所需的**全部参数**

#### 两种参数传递方式

1. **指针数组方式**（大多数场景用这个即可）：在 `hgLaunchKernel()` 的**倒数第二个参数**中传入一个 `void*` 数组，数组中**第 n 个元素指向第 n 个核函数参数在主机内存中的副本**。

2. **紧凑缓冲区方式**（高级场景：参数个数或类型在编译期未知、需要在运行时动态构造参数列表）：通过最后一个参数中的 **`HG_LAUNCH_PARAM_BUFFER_POINTER`** 选项，将所有参数**按照设备端对齐要求**依次排列在一个连续缓冲区中。

#### 紧凑缓冲区的对齐规则（重要）

- `HGdeviceptr` 语义上表示设备指针，其对齐要求为 **`__alignof(void*)`**。
- 大多数基本类型的**设备端对齐与主机端一致**，可通过 `__alignof()` 查询。
- 内置向量类型的对齐要求详见"向量要求"章节。
- **常见陷阱**：`double` 和 `long long`（64 位系统上还包括 `long`）——**PPU 设备代码中这些类型始终按双字（8 字节）对齐**，但某些主机编译器配置（如 `gcc -mno-align-double`）可能将其按单字对齐，从而导致主机端与设备端的对齐要求不一致——**构建参数缓冲区时务必以设备端对齐为准**。

#### 示例：构建符合对齐要求的参数缓冲区

通过两个辅助模板函数 `align_offset()` 和 `append_param()` 封装对齐计算与参数追加逻辑，示例涵盖六种不同对齐需求的参数类型（照录原文）：

```cpp
inline size_t align_offset(size_t offset, size_t alignment) {
    return (offset + alignment ‑ 1) & ~(alignment ‑ 1);
}
template<typename T>
void append_param(char* buffer, size_t& offset, const T& value, size_t alignment) {
    offset = align_offset(offset, alignment);
    memcpy(buffer + offset, &value, sizeof(T));
    offset += sizeof(T);
}
char paramBuf[1024];
size_t offset = 0;

float threshold = 0.5f;
append_param(paramBuf, offset, threshold, __alignof(float));
int2 gridCoords = {8, 16};
append_param(paramBuf, offset, gridCoords, 8); // int2 对齐要求为 8 字节
HGdeviceptr inputPtr;
append_param(paramBuf, offset, inputPtr, __alignof(void*));
int iterations = 100;
append_param(paramBuf, offset, iterations, __alignof(int));
float4 scale = {1.0f, 2.0f, 3.0f, 4.0f};
append_param(paramBuf, offset, scale, 16); // float4 对齐要求为 16 字节
short mode = 1;
append_param(paramBuf, offset, mode, __alignof(short));
void* extra[] = {
    HG_LAUNCH_PARAM_BUFFER_POINTER, paramBuf,
    HG_LAUNCH_PARAM_BUFFER_SIZE, &offset,
    HG_LAUNCH_PARAM_END
};
hgLaunchKernel(hgFunction,
    blockWidth, blockHeight, blockDepth,
    gridWidth, gridHeight, gridDepth,
    0, 0, 0, extra);
```

要点摘录：

| 类型 | 对齐要求 |
|---|---|
| `float` | `__alignof(float)`（4 字节） |
| `int2` | **8 字节** |
| `HGdeviceptr` | `__alignof(void*)` |
| `int` | `__alignof(int)`（4 字节） |
| `float4` | **16 字节** |
| `short` | `__alignof(short)`（2 字节） |

`extra[]` 数组以 `HG_LAUNCH_PARAM_BUFFER_POINTER` + 缓冲区指针、`HG_LAUNCH_PARAM_BUFFER_SIZE` + 大小指针、`HG_LAUNCH_PARAM_END` 结尾的形式传给 `hgLaunchKernel()` 的最后一个参数。

#### 结构体跨主机/设备传递的对齐差异

在 PPU 编程中，当结构体在主机代码与设备代码之间传递时，开发者需要特别关注**对齐差异**：

- 结构体的**整体对齐取决于其成员中对齐要求最高的那个字段**。
- 对于含有**内置向量类型、`HGdeviceptr`，或者未按默认规则对齐的 `double` / `long long`** 的结构体，主机编译器和设备编译器可能采用不同的对齐策略，从而导致 **padding 布局不一致**。

示例：在主机端 `val` 字段紧随 `id` 之后、无额外填充；但在设备端，`float4` 要求 16 字节对齐，编译器会在 `id` 之后插入 **12 字节的填充**以满足 `val` 的对齐约束（照录原文）：

```cpp
typedef struct {
    int id;
    float4 val;
} AlignExample;
```

（即：主机端布局 `id@0, val@4`；设备端布局 `id@0, [12 字节 padding], val@16`——跨端传递这种结构体必须统一对齐策略。）

**比赛关联**：写自定义 kernel 并用驱动 API 启动时，参数布局错误是最隐蔽的 bug 来源——轻则数据错位、重则显存越界，且往往不报错只表现为精度下降。比赛做算子融合（如把 QKV projection + RoPE + KV-cache 写入融成一个 kernel，参数动辄十几个，含 `float4` 向量与设备指针混合）时，必须严格按设备端对齐构建参数；用指针数组方式（`kernelArgs`）可以躲开大部分手工对齐坑。

---

### 3.1.4 运行时 API 与驱动程序 API 之间的互操作性

应用程序可以将运行时 API 代码与驱动程序 API 代码**混合使用**。

- 如果通过驱动程序 API 创建并设置了当前上下文，**后续的运行时调用将使用此上下文，而不会创建新的上下文**。
- 如果运行时已经初始化，可以使用 **`hgCtxGetCurrent()`** 来检索初始化期间创建的上下文。此上下文可用于后续的驱动程序 API 调用。
- 由运行时隐式创建的上下文称为**主上下文（primary context）**。

设备内存可以使用**任一 API** 进行分配和释放。`HGdeviceptr` 可以转换为常规指针，反之亦然（照录原文）：

```cpp
HGdeviceptr devPtr;
float* d_data;
// 使用驱动程序 API 分配
hgMemAlloc(&devPtr, size);
d_data = (float*)devPtr;
// 使用运行时 API 分配
hggcMalloc(&d_data, size);
devPtr = (HGdeviceptr)d_data;
```

**比赛关联**：这意味着可以在 sglang/PyTorch 管理内存和主上下文的同时，用驱动 API 加载自研 hgbin kernel 并直接操作框架分配的显存指针（`hggcMalloc` 的指针直接强转 `HGdeviceptr` 即可用）。不用重写整套内存管理就能插入自定义算子——这是比赛中"系统级优化"与现有推理栈共存的最实用路径。

---

## 3.2 多设备协同编程

多 PPU 编程通过利用多 PPU 系统所提供的**更大的整体算术性能、内存容量和内存带宽**，使应用程序能够处理更大的问题规模，并达到单 PPU 无法实现的性能水平。

HGGC 通过主机 API、驱动基础设施以及支持性的 PPU 硬件技术来支持多 PPU 编程，包括：

- 主机线程的 HGGC 上下文管理
- 面向系统中所有处理器的**统一内存寻址** —— PPU 之间的点对点大块内存传输
- **细粒度的点对点 PPU 负载/存储内存访问**
- 更高层级的抽象以及支持性的系统软件，例如 **HGGC 进程间通信**、使用 **PCCL** 的并行归约，以及通过 **ICNLink** 和/或 **Direct RDMA** 进行通信

### 3.2.0 多 PPU 编程的常见方式

在最基本的层面上，多 PPU 编程要求应用程序同时管理多个活动的 HGGC 上下文，将数据分发到各个 PPU，在 PPU 上启动核函数以完成工作，并通信或收集结果，以便应用程序对其进行处理。具体实现方式会因应用算法的最有效映射方式、可用并行性以及现有代码结构如何适配某种多 PPU 编程方法而有所不同。常见的多 PPU 编程方式包括：

1. 一个主机线程驱动多个 PPU
2. 多个主机线程，每个线程驱动各自的 PPU
3. 多个单线程主机进程，每个进程驱动各自的 PPU
4. 多个主机进程，每个进程包含多个线程，每个线程驱动各自的 PPU
5. 通过 **ICNLink** 连接的多节点集群，PPU 由跨越集群节点内多个操作系统实例运行的线程和进程驱动

PPU 可以通过**设备内存之间的内存传输**和**点对点访问**相互通信，这覆盖了上面列出的所有多设备工作分配方式。通过查询并启用点对点 PPU 内存访问，以及利用 **ICNLink** 实现设备之间更高带宽的传输和更细粒度的 load/store 操作，可以支持高性能、低延迟的 PPU 通信。

### 3.2.0.1 统一虚拟寻址与 IPC

- HGGC 的**统一虚拟寻址（unified virtual addressing）**允许**同一主机进程中的多个 PPU** 之间进行通信，只需进行极少的额外步骤即可查询并启用高性能的点对点内存访问和传输，例如通过 ICNLink 实现。
- 由**不同主机进程**管理的多个 PPU 之间的通信，可通过**进程间通信（IPC）**和**虚拟内存管理（VMM）API** 来支持：
  - 高层次 IPC 概念和节点内 HGGC IPC API：见"进程间通信"章节。
  - 高级 VMM API 同时支持**节点内和跨节点** IPC，允许按**单次分配粒度**控制 IPC 共享内存缓冲区的方式：见"虚拟内存管理"章节。
- HGGC 本身提供了在一组 PPU 内实现集合操作所需的 API（可能也包括主机），但它**并不直接提供高层次的多 PPU 集合通信 API**。多 PPU 集合通信由更高抽象层的 HGGC 通信库提供，例如 **PCCL**。

**平台扩展关联**：每进程一卡、张量并行、PCCL/P2P 和 ICNLink 都面向多卡 serving，不属于本次单卡、单样本、无 batch 的比赛路径。

---

### 3.2.1 多设备上下文与执行管理

应用程序要使用多个 PPU，首先需要做的几步是：

1. **枚举**可用的 PPU 设备；
2. 根据**硬件属性、CPU 亲和性以及与其他设备的连接性**，从可用设备中进行合适的选择；
3. 为应用程序将要使用的每个设备**创建 HGGC 上下文**。

#### 3.2.1.1 设备枚举

下面的代码示例展示了如何查询支持 HGGC 的设备数量、枚举每个设备，并查询其属性（照录原文）：

```cpp
int deviceCount;
hggcGetDeviceCount(&deviceCount);
int device;
for (device = 0; device < deviceCount; ++device) {
    int major, minor;
    hggcDeviceGetAttribute(&major, hggcDevAttrComputeCapabilityMajor, device);
    hggcDeviceGetAttribute(&minor, hggcDevAttrComputeCapabilityMinor, device);
    printf("Device %d has compute capability %d.%d.\n",
        device, major, minor);
}
```

关键 API / 属性：

- `hggcGetDeviceCount(&deviceCount)` —— 查询设备数量。
- `hggcDeviceGetAttribute(&value, attr, device)` —— 查询设备属性。
- `hggcDevAttrComputeCapabilityMajor` / `hggcDevAttrComputeCapabilityMinor` —— 计算能力主/次版本号属性。

#### 3.2.1.2 设备选择

- 主机线程可以通过调用 **`hggcSetDevice()`**，随时设置它当前正在操作的设备。
- **设备内存分配和核函数启动都会在当前设备上执行**；**流和事件会创建在当前设置的设备上**。
- 在主机线程调用 `hggcSetDevice()` 之前，**当前设备默认是设备 0**。

下面的代码示例说明了设置当前设备如何影响后续的内存分配和核函数执行操作（照录原文）：

```cpp
size_t bufSize = 4096 * sizeof(float);
hggcSetDevice(0);                // 将设备 0 设为当前设备
float* devA_data;
hggcMalloc(&devA_data, bufSize); // 在设备 0 上分配内存
ComputeKernel<<<512, 256>>>(devA_data); // 在设备 0 上启动核函数
hggcSetDevice(1);                // 将设备 1 设为当前设备
float* devB_data;
hggcMalloc(&devB_data, bufSize); // 在设备 1 上分配内存
ComputeKernel<<<512, 256>>>(devB_data); // 在设备 1 上启动核函数
```

#### 3.2.1.3 多设备流、事件与内存拷贝行为

在多设备环境中，各 API 的跨设备行为汇总如下表（原文表格）：

| 操作 | 跨设备条件 | 结果 | 补充说明 |
|---|---|---|---|
| 核函数启动 | 流不属于当前设备 | **失败** | — |
| 内存拷贝 | 流不属于当前设备 | 成功 | — |
| `hggcEventRecord()` | 事件与流属于不同设备 | **失败** | — |
| `hggcEventElapsedTime()` | 两个事件属于不同设备 | **失败** | — |
| `hggcEventSynchronize()` | 事件关联设备与当前设备不同 | 成功 | — |
| `hggcEventQuery()` | 事件关联设备与当前设备不同 | 成功 | — |
| `hggcStreamWaitEvent()` | 流与事件关联到不同设备 | 成功 | **可用于使多个设备彼此同步** |

（注：原文表格中操作与条件行的对应关系因排版有交错，上表按语义整理：`hggcEventSynchronize()` / `hggcEventQuery()` 对应"事件关联设备与当前设备不同→成功"，`hggcStreamWaitEvent()` 对应"流与事件关联到不同设备→成功，可用于多设备同步"。需查原文确认精确对应。）

**默认流的并发性**：每个设备都有自己的默认流，因此，发往某个设备默认流的命令，相对于发往其他任何设备默认流的命令，**可能会乱序执行，或并发执行**。

以下代码展示了跨设备流操作的典型模式（照录原文）：

```cpp
hggcSetDevice(0);                    // 将设备 0 设为当前设备
hggcStream_t streamOnDev0;
hggcStreamCreate(&streamOnDev0);     // 在设备 0 上创建流
WorkKernel<<<64, 128, 0, streamOnDev0>>>(); // 在设备 0 的流上启动核函数
hggcSetDevice(1);                    // 将设备 1 设为当前设备
hggcStream_t streamOnDev1;
hggcStreamCreate(&streamOnDev1);     // 在设备 1 上创建流
WorkKernel<<<64, 128, 0, streamOnDev1>>>(); // 在设备 1 的流上启动核函数
// 以下启动会失败——streamOnDev0 不属于当前设备 1：
WorkKernel<<<64, 128, 0, streamOnDev0>>>();
```

**平台扩展关联**：本节的跨设备流和 event 用于多卡 serving，不属于本次单卡比赛路径。比赛计时只在目标 810E 上进行；`hggcEventElapsedTime()` 的两个事件必须同属该设备。

---

### 3.2.2 多设备点对点（Peer-to-Peer）传输与内存访问

#### 3.2.2.1 点对点内存传输

HGGC 可以在设备之间执行内存传输，并且在**支持点对点内存访问时，会利用专门的拷贝引擎和 ICNLink 硬件来最大化性能**。

- `hggcMemcpy` 可以通过拷贝类型 **`hggcMemcpyDeviceToDevice`** 或 **`hggcMemcpyDefault`** 来使用。
- 否则，必须使用 **`hggcMemcpyPeer()`**、**`hggcMemcpyPeerAsync()`**、**`hggcMemcpy3DPeer()`** 或 **`hggcMemcpy3DPeerAsync()`** 进行拷贝，如下面的代码示例所示（照录原文）：

```cpp
size_t tensorBytes = 2048 * sizeof(float);
hggcSetDevice(0);
float* srcTensor;
hggcMalloc(&srcTensor, tensorBytes);  // 在设备 0 分配源张量

hggcSetDevice(1);
float* dstTensor;
hggcMalloc(&dstTensor, tensorBytes);  // 在设备 1 分配目标张量

hggcSetDevice(0);
ComputeKernel<<<256, 256>>>(srcTensor); // 在设备 0 上计算

hggcSetDevice(1);
hggcMemcpyPeer(dstTensor, 1, srcTensor, 0, tensorBytes); // 跨设备传输
ComputeKernel<<<256, 256>>>(dstTensor); // 在设备 1 上处理传输后的数据
```

`hggcMemcpyPeer(dst, dstDevice, src, srcDevice, bytes)` 参数语义：目标指针、目标设备号、源指针、源设备号、字节数。

**（隐式 NULL 流中的）跨设备拷贝的同步语义**：

- 在两个设备上**之前发布的所有命令执行完毕之前，拷贝操作不会开始**。
- **在拷贝操作完成后，后续发布到任一设备的命令才能开始执行**（参见"异步执行"部分）。
- 与流的常规行为一致，两个设备内存之间的**异步拷贝可以与另一个流中的拷贝或核函数执行重叠**。

**性能要点**：如果两个设备之间启用了点对点访问（见下节），则这两个设备之间的点对点内存拷贝**不再需要通过主机（Host）进行中转，因此速度更快**。

#### 3.2.2.2 点对点内存访问

根据系统属性，设备能够**寻址彼此的内存**（即在一个设备上执行的核函数可以**解引用指向另一个设备内存的指针**）。

- 如果对于指定的设备调用 **`hggcDeviceCanAccessPeer()`** 返回 `true`，则支持这两个设备之间的点对点内存访问。
- 必须通过调用 **`hggcDeviceEnablePeerAccess()`** 在两个设备之间启用点对点内存访问，如下面的代码示例所示。
- 两个设备均使用**统一虚拟地址空间**（参见"统一虚拟地址空间"章节），因此**可以使用相同的指针来寻址两个设备的内存**，如下面的代码示例所示（照录原文）：

```cpp
hggcSetDevice(0);
float* modelWeights;
size_t weightBytes = 4096 * sizeof(float);
hggcMalloc(&modelWeights, weightBytes);
InitWeights<<<32, 128>>>(modelWeights, 4096); // 在设备 0 上初始化模型权重
hggcSetDevice(1);
hggcDeviceEnablePeerAccess(0, 0);  // 启用对设备 0 的点对点访问

// 设备 1 直接读取设备 0 上的权重数据，无需显式拷贝
InferenceKernel<<<64, 256>>>(modelWeights, 4096);
```

`hggcDeviceEnablePeerAccess(peerDevice, flags)` 参数语义：对等设备号、标志（示例中传 0）。

> **NOTE（原文注意事项，重要）**
> 使用 `hggcDeviceEnablePeerAccess()` 启用点对点内存访问会**全局作用于该对等设备上之前及之后的所有 PPU 内存分配**。通过 `hggcDeviceEnablePeerAccess()` 启用对设备的点对点访问会**增加在该对等设备上进行内存分配操作的运行时开销**，因为需要使这些分配对于当前设备以及其他已启用访问的对等设备**立即可见**，这会带来**随着对等设备数量增加而累积的额外开销**。
> 一种比为所有设备内存分配启用点对点内存访问**更具扩展性的替代方案**是：利用 HGGC **虚拟内存管理（VMM）API**，在分配时**仅按需显式分配可被点对点访问的内存区域**。通过在内存分配时显式请求点对点可访问性，内存分配的运行时成本不会影响那些无需被对等设备访问的内存，且点对点可访问的数据结构范围界定更清晰，从而改进了软件调试和可靠性（参见"虚拟内存管理"相关章节）。

#### 3.2.2.3 点对点内存一致性

- **必须使用同步操作**来确保跨多个设备分布的网格（Grid）中并发执行线程对内存访问的**顺序和正确性**。
- 跨设备同步的线程操作运行在 **`thread_scope_system`** 同步作用域内。同样，内存操作也处于 **`thread_scope_system`** 内存同步域内。
- 当仅由单个 PPU 访问对象时，HGGC **原子函数（Atomic Functions）** 可以对位于**对等设备内存**中的对象执行**读-改-写**操作。（有关对等原子操作的要求和限制，见原子函数相关章节。）

#### 3.2.2.4 多设备统一内存（Managed Memory）

在支持点对点通信的多 PPU 系统上可以使用**统一内存（Managed Memory）**。有关并发多设备统一内存访问的详细要求，以及用于获取统一内存 PPU 独占访问权限的 API（见统一内存相关章节）。

#### 3.2.2.5 主机 IOMMU 硬件、PCI 访问控制服务与虚拟机

特别是在 Linux 系统上：

- HGGC 和显示驱动程序**不支持在启用 IOMMU 的裸机（Bare-metal）环境下进行 PCIe 点对点内存传输**。
- 但是，HGGC 和显示驱动程序确实**支持通过虚拟机透传（Pass-through）方式使用 IOMMU**。
- **在裸机系统上运行 Linux 时，必须禁用 IOMMU**，以防止**静默的设备内存损坏**。
- 相反，**对于虚拟机，应启用 IOMMU 并使用 VFIO 驱动程序**进行 PCIe 透传。

**平台扩展关联**：本节全部是跨卡 P2P 约束，不属于本次单卡比赛路径。比赛进程不要初始化 peer access；IOMMU、跨设备原子与同步规则仅在后续通用多卡部署时使用。

---

## 本章要点速查

| 主题 | 关键 API / 概念 |
|---|---|
| 驱动 API 初始化 | `hgInit(0)`、`hgDeviceGetCount`、`hgDeviceGet`、`hgCtxCreate`（V3 多一个 `HGctxCreateParams*` 参数） |
| 上下文管理 | `hgCtxCreate` / `hgCtxDestroy` / `hgCtxAttach` / `hgCtxDetach` / `hgCtxPushCurrent` / `hgCtxPopCurrent` / `hgCtxGetCurrent` / `hgDevicePrimaryCtxRetain` |
| 模块加载 | `hgModuleLoad` / `hgModuleLoadData` / `hgModuleGetFunction`（hgbin、fatbin） |
| 核函数启动 | `hgLaunchKernel`；参数两种传法：`void*` 指针数组 / `HG_LAUNCH_PARAM_BUFFER_POINTER` 紧凑缓冲区 |
| 对齐陷阱 | `double`/`long long`/64 位 `long` 设备端恒 8 字节对齐；`int2`=8B、`float4`=16B；结构体跨端 padding 可能不同 |
| 设备枚举/选择 | `hggcGetDeviceCount`、`hggcDeviceGetAttribute`（`hggcDevAttrComputeCapabilityMajor/Minor`）、`hggcSetDevice` |
| 跨设备行为 | kernel launch 用他设备流→失败；memcpy 用他设备流→成功；`hggcStreamWaitEvent` 跨设备→成功（多设备同步原语） |
| P2P 传输 | `hggcMemcpyPeer` / `hggcMemcpyPeerAsync` / `hggcMemcpy3DPeer` / `hggcMemcpy3DPeerAsync`；`hggcMemcpyDeviceToDevice` / `hggcMemcpyDefault` |
| P2P 访问 | `hggcDeviceCanAccessPeer` / `hggcDeviceEnablePeerAccess`；UVA 下同指针寻址两卡内存；VMM API 按需开启更优 |
| 一致性 | 跨设备同步/内存操作处于 `thread_scope_system` 作用域 |
| 环境 | 裸机 Linux 必须禁用 IOMMU（否则 PCIe P2P 静默损坏内存）；虚拟机则启用 IOMMU + VFIO 透传 |
