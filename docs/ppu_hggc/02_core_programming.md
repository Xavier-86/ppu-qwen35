# 第 2 章 核心编程（HGGC） <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [2.1 用 C++ 编写 HGGC 程序](#21-用-c-编写-hggc-程序)
  - [2.1.1 使用 hgcc 编译](#211-使用-hgcc-编译)
  - [2.1.2 核函数程序](#212-核函数程序)
  - [2.1.3 PPU 计算中的内存](#213-ppu-计算中的内存)
  - [2.1.4 同步 CPU 与 PPU](#214-同步-cpu-与-ppu)
  - [2.1.5 组合使用（完整示例代码）](#215-组合使用完整示例代码)
  - [2.1.6 Runtime 初始化](#216-runtime-初始化)
  - [2.1.7 HGGC 中的错误检查](#217-hggc-中的错误检查)
  - [2.1.8 Device 与 Host 函数](#218-device-与-host-函数)
  - [2.1.9 变量限定符](#219-变量限定符)
- [2.2 编写 HGGC SIMT 核函数程序](#22-编写-hggc-simt-核函数程序)
  - [2.2.1 SIMT 基础](#221-simt-基础)
  - [2.2.2 线程层次结构](#222-线程层次结构)
  - [2.2.3 PPU 设备内存空间](#223-ppu-设备内存空间)
  - [2.2.4 原子操作](#224-原子操作)
  - [2.2.5 协作组](#225-协作组)
  - [2.2.6 核函数启动和占用率](#226-核函数启动和占用率)
  - [2.2.7 PPU 内存](#227-ppu-内存)
- [2.3 异步编程模式](#23-异步编程模式)
  - [2.3.1 异步执行基础](#231-异步执行基础)
  - [2.3.2 流与事件](#232-流与事件)
  - [2.3.3 来自流的回调函数](#233-来自流的回调函数)
  - [2.3.4 高级流管理与核函数配置](#234-高级流管理与核函数配置)
  - [2.3.5 从流到图——HGGC 图简介](#235-从流到图hggc-图简介)
  - [2.3.6 异步编程小结](#236-异步编程小结)
- [2.4 统一和系统内存](#24-统一和系统内存)
  - [2.4.1 统一虚拟地址空间](#241-统一虚拟地址空间)
  - [2.4.2 统一内存](#242-统一内存)
  - [2.4.3 页锁定主机内存](#243-页锁定主机内存)
  - [2.4.4 总结](#244-总结)
- [2.5 hgcc：HGGC 编译器](#25-hgcchggc-编译器)
  - [2.5.1 HGGC 源文件和头文件](#251-hggc-源文件和头文件)
  - [2.5.2 hgcc 编译工作流程](#252-hgcc-编译工作流程)
  - [2.5.3 hgcc 基本用法](#253-hgcc-基本用法)
  - [2.5.4 常见编译器选项](#254-常见编译器选项)


> 本章涵盖：
> - §2.1 用 C++ 编写 HGGC 程序（hgcc 编译、核函数指定/启动、内置索引、内存管理、错误检查）
> - §2.2 编写 HGGC SIMT 核函数程序（线程层次、内存空间、原子操作、协作组、占用率）
> - §2.3 异步编程模式（流、事件、同步、回调、HGGC 图、流优先级、环境变量）
> - §2.4 统一和系统内存（统一虚拟地址空间、统一内存模式、页锁定/映射内存）
> - §2.5 hgcc 编译器（编译流程、编译选项）
> 所有 API 名、参数、枚举值、硬件数值均保留原文写法。

---

## 2.1 用 C++ 编写 HGGC 程序

本章通过介绍如何在 C++ 中使用 HGGC 的核心特性来展示 HGGC 并行编程的实践方法。本编程指南重点关注 **HGGC 运行时 API（Runtime API）**——它是使用 C++ 编写 HGGC 代码最常用的方式，并且构建于底层的 **HGGC 驱动程序 API（Driver API）** 之上。

- 1.4.2.1 节讨论了 Runtime API 与 Driver API 的区别；
- 3.1.4 节讨论了混合使用这两种 API 的编码方法（互操作性）。

前提假设：已安装 SAIL 工具包和 HGGC 驱动程序，并且存在支持的 PPU。

### 2.1.1 使用 hgcc 编译

用 C++ 编写的 PPU 代码通过特有的 HGGC 编译器 **hgcc** 进行编译。hgcc 是一个**编译器驱动程序（compiler driver）**，它提供简洁且风格熟悉的命令行选项，简化 C++ 代码的编译过程，并通过调用实现不同编译阶段的一系列工具来执行它们。第二章的 hgcc 部分涵盖常见用例，完整文档由《T-Head SAIL HGCC 用户手册》提供。

### 2.1.2 核函数程序

在 PPU 上执行并且可以从主机（host）调用的函数称为**核函数（kernel）**。核函数程序被设计成可以同时由许多并行线程运行。

#### 2.1.2.1 核函数指定方式

在 HGGC C++ 中，通过 **`__global__`** 限定符标记一个函数为核函数入口。编译器据此将函数编译为可在 PPU 上并行执行的设备代码。

- 核函数是**返回类型为 `void`** 的函数。
- 核函数启动（launch）是一种使核函数开始运行的操作，通常从 CPU 发起。

```cpp
// 核函数定义：逐元素 ReLU 激活
__global__ void relu_activate(const float* input, float* output, int len)
{
    int tid = threadIdx.x + blockDim.x * blockIdx.x;
    if (tid < len) {
        output[tid] = (input[tid] > 0.0f) ? input[tid] : 0.0f;
    }
}
```

#### 2.1.2.2 核函数的启动

核函数启动期间决定执行该核函数程序的线程数量，这也被称为**执行配置（execution configuration）**。同一个核函数的不同调用可能使用不同的执行配置（不同线程数或线程块数）。

目前有两种从 CPU host 代码启动核函数的方法：

1. **三重尖括号（triple chevron）符号法**——最常用的方法，本节介绍；
2. **`hggcLaunchKernelEx` 函数法**——示例在 2.3.4.1 节详细展示和讨论。

##### 2.1.2.2.1 三重尖括号表示法

三重尖括号是 HGGC C++ 语言扩展，用于启动核函数。它使用三个尖括号字符封装核函数启动的执行配置，即 `<<<>>>`。执行配置参数以逗号分隔列表的形式在尖括号内指定，类似于函数调用的参数。

完整可运行示例：

```cpp
__global__ void relu_activate(const float* input, float* output, int len)
{
    int tid = threadIdx.x + blockDim.x * blockIdx.x;
    if (tid < len) {
        output[tid] = (input[tid] > 0.0f) ? input[tid] : 0.0f;
    }
}

int main()
{
    int len = 1024;
    // ... 分配并初始化 d_input, d_output ...
    int threadsPerBlock = 256;
    int blocksPerGrid = (len + threadsPerBlock - 1) / threadsPerBlock;
    relu_activate<<<blocksPerGrid, threadsPerBlock>>>(d_input, d_output, len);
    // ...
}
```

要点：

- `<<<>>>` 中的参数以逗号分隔，**前两个参数分别是网格（grid）维度和线程块（block）维度**。当使用一维线程块或网格时，可以使用整数指定维度。
- 上述代码启动 4 个线程块，每块 256 个线程，共 1024 个线程并行执行 ReLU 操作。每个线程根据其全局索引 `tid` 处理数组中的一个元素。
- **线程块的大小受 CU 物理资源约束**：同一块的全部线程在同一 CU 上执行，并必须共享该 CU 的资源。**在当前 PPU 上，一个线程块最多可包含 1024 个线程**。如果资源允许，可以在一个 CU 上同时调度多个线程块。
- **核函数启动相对于 host 主机线程是异步的**：host 下发核函数后在 PPU 上启动执行，但 host 主机代码不会等待核函数完成（下发甚至无需感知核函数开始执行）就继续前进。这种异步执行方式需要某种形式的 PPU 与 CPU 之间的同步。

当使用 2 维或 3 维网格或线程块时，HGGC 上网格和线程块维度都使用 **`dim3`**（三维）类型表示。以下代码片段展示了使用 16×16 线程块网格启动二维矩阵逐元素求和核函数的情况，每个线程块是 8×8：

```cpp
int main()
{
    ...
    dim3 grid(16,16);
    dim3 block(8,8);
    elementwise_add_2d<<<grid, block>>>(A, B, C);
    ...
}
```

#### 2.1.2.3 线程和网格索引内置函数

在核函数代码内部，HGGC 提供了访问执行配置参数和线程或块索引的内置函数（内置变量）：

| 内置变量 | 描述 |
|---|---|
| `threadIdx` | 提供线程在其线程块内的索引。线程块中的每个线程都会有不同的索引。 |
| `blockDim` | 提供线程块的尺寸，这是在核函数启动的执行配置中指定的。 |
| `blockIdx` | 提供线程块在网格中的索引。每个线程块都会有不同的索引。 |
| `gridDim` | 提供网格的尺寸，这是在核函数启动时执行配置中指定的。 |

- 这些内置变量都是具有 `.x`、`.y` 和 `.z` 成员的**三维向量**。未经启动配置指定的维度默认为 1。
- `threadIdx` 和 `blockIdx` 是**从零开始索引**的：
  - `threadIdx.x` 的值范围从 0 到包括 `blockDim.x-1`；`.y` 和 `.z` 在其各自维度中同样工作；
  - `blockIdx.x` 的值范围从 0 到包括 `gridDim.x-1`，`.y`、`.z` 维度同理。
- 这些允许单个线程确定应执行的工作。

回到 `relu_activate` 核函数：它接受输入数组、输出数组和长度三个参数，对输入数组执行逐元素 ReLU 激活并将结果写入输出数组。每个线程计算自己的全局索引 `tid`，从而确定其负责处理的数据位置：

```cpp
__global__ void relu_activate(const float* input, float* output, int len)
{
    // 计算此线程的全局索引
    int tid = threadIdx.x + blockDim.x * blockIdx.x;
    if (tid < len) {
        output[tid] = (input[tid] > 0.0f) ? input[tid] : 0.0f;
    }
}

int main()
{
    // input 和 output 是长度为 len 的向量
    int len = 1024;
    int threadsPerBlock = 256;
    int blocksPerGrid = (len + threadsPerBlock - 1) / threadsPerBlock;
    relu_activate<<<blocksPerGrid, threadsPerBlock>>>(d_input, d_output, len);
}
```

在这个例子中，使用 4 个线程块（`blocksPerGrid = 4`），每块 256 个线程来处理长度为 1024 的向量：

- 第一个线程块中 `blockIdx.x = 0`，每个线程的 `tid` 就是它的 `threadIdx.x`（范围 0–255）；
- 第二个线程块中 `blockIdx.x = 1`，`tid = threadIdx.x + 256`（范围 256–511）；
- 以此类推，第四个线程块中 `tid` 的范围为 768–1023。

##### 2.1.2.3.1 边界检查

在 `relu_activate` 示例中，边界检查已经内嵌在核函数逻辑中（`if (tid < len)`）。这是因为启动的线程总数（`blocksPerGrid * threadsPerBlock`）通常会向上取整到线程块大小的倍数，当数组长度不是线程块大小的整数倍时，最后一个线程块中会有部分线程的 `tid` 超出有效范围。

- 边界检查确保这些"超额"线程不会执行越界内存访问。
- 虽然启动少量不做工作的线程并不会产生显著的性能开销，但**应当避免启动整块都无工作可做的线程块**。
- 通常，所需线程块数量可以通过将数据长度除以线程块大小并向上取整得到。常见写法：

```cpp
blocksPerGrid = (len + threadsPerBlock - 1) / threadsPerBlock;
```

比赛关联：Qwen3.5-2B 的激活函数（SwiGLU/GELU）、RoPE、RMSNorm 等逐元素 kernel 都遵循这一"全局索引 + 边界检查"范式；`1024` 线程块上限是确定 kernel 启动配置时的硬约束。

### 2.1.3 PPU 计算中的内存

为了使用 `relu_activate` 核函数，输入和输出数组必须位于 PPU 可访问的内存中。有几种不同的方法可以做到这一点，这里演示其中两种（Unified Memory 与显式内存管理）。

#### 2.1.3.1 Unified Memory

Unified memory 是 HGGC runtime 的一个特性，它让 HGGC Driver 管理 host 与 device(s) 之间的数据移动。

- 内存通过 **`hggcMallocManaged`** API 分配，或通过 **`__managed__`** 标识符声明变量。
- HGGC Driver 会确保当 PPU 或 CPU 任一方尝试访问时，这段内存对其可访问。
- `hggcMallocManaged` 分配的 buffer 可被 CPU 或 PPU 访问，使用 **`hggcFree`** 释放。

```cpp
void unified_memory_example(int len)
{
    float* input = nullptr;
    float* output = nullptr;
    float* expected = (float*)malloc(len * sizeof(float));
    hggcMallocManaged(&input, len * sizeof(float));
    hggcMallocManaged(&output, len * sizeof(float));

    // 在主机端填充测试数据
    fill_random(input, len);
    // 启动核函数
    int threadsPerBlock = 256;
    int blocksPerGrid = (len + threadsPerBlock - 1) / threadsPerBlock;
    relu_activate<<<blocksPerGrid, threadsPerBlock>>>(input, output, len);
    hggcDeviceSynchronize();
    // 主机端参考计算
    cpu_relu(input, expected, len);
    // 比较结果
    if (arrays_match(output, expected, len)) {
        printf("Unified Memory: 结果一致\n");
    } else {
        printf("Unified Memory: 结果不一致\n");
    }
    hggcFree(input);
    hggcFree(output);
    free(expected);
}
```

- Unified memory 在 HGGC 支持的所有操作系统和 PPU 上都受支持，但具体支持程度取决于硬件能力和驱动版本（参见"统一内存模式"）。
- 在一些 Linux 系统上（例如具备"统一和系统内存"的系统），所有系统内存会自动成为 unified memory，无需使用 `hggcMallocManaged` 或 `__managed__` 标识符。

#### 2.1.3.2 显式内存管理

显式管理内存分配以及在不同内存空间之间的数据迁移可以帮助提升应用性能，但也会使代码更冗长。下面的代码使用 **`hggcMalloc`** 在 PPU 上显式分配内存。PPU 上的内存使用与前一个 unified memory 示例相同的 `hggcFree` API 释放。

```cpp
void explicit_memory_example(int len)
{
    size_t bytes = len * sizeof(float);
    // 主机端缓冲区
    float* h_input = nullptr;
    float* h_output = nullptr;
    float* expected = (float*)malloc(bytes);
    // 设备端缓冲区
    float* d_input = nullptr;
    float* d_output = nullptr;
    // 集中完成所有主机端分配
    hggcMallocHost(&h_input, bytes);
    hggcMallocHost(&h_output, bytes);
    // 初始化输入数据
    fill_random(h_input, len);
    // 集中完成所有设备端分配
    hggcMalloc(&d_input, bytes);
    hggcMalloc(&d_output, bytes);
    // 集中完成所有 H2D 拷贝
    hggcMemcpy(d_input, h_input, bytes, hggcMemcpyDefault);
    hggcMemset(d_output, 0, bytes);
    // 启动核函数
    int threadsPerBlock = 256;
    int blocksPerGrid = (len + threadsPerBlock - 1) / threadsPerBlock;
    relu_activate<<<blocksPerGrid, threadsPerBlock>>>(d_input, d_output, len);
    hggcDeviceSynchronize();
    // 将结果拷回主机
    hggcMemcpy(h_output, d_output, bytes, hggcMemcpyDefault);
    // 主机端参考计算
    cpu_relu(h_input, expected, len);
    // 验证结果
    if (arrays_match(h_output, expected, len)) {
        printf("Explicit Memory: 结果一致\n");
    } else {
        printf("Explicit Memory: 结果不一致\n");
    }
    // 释放资源
    hggcFree(d_input);
    hggcFree(d_output);
    hggcFreeHost(h_input);
    hggcFreeHost(h_output);
    free(expected);
}
```

关键点：

- HGGC API **`hggcMemcpy`** 用于将数据在 CPU buffer 与 PPU buffer 之间复制。除 destination pointer、source pointer 和以字节为单位的大小之外，`hggcMemcpy` 的最后一个参数是 **`hggcMemcpyKind_t`**，可取值：
  - `hggcMemcpyHostToDevice`（从 CPU 到 PPU 的复制）
  - `hggcMemcpyDeviceToHost`（从 PPU 到 CPU 的复制）
  - `hggcMemcpyDeviceToDevice`（在 PPU 内或 PPU 间的复制）
  - `hggcMemcpyDefault`：HGGC 使用 source 和 destination pointer 的值来确定要执行的 copy 类型。
- `hggcMemcpy` API 是**同步的**：直到 copy 完成才返回。异步 copy 在"在 HGGC 流中启动内存传输"中介绍。
- 代码使用 **`hggcMallocHost`** 在 CPU 上分配内存。这会在 host 上分配 **page-locked memory（页锁定内存）**，可以提升 copy 性能，并且对 **asynchronous memory transfers（异步内存传输）是必要的**。
- 最佳实践：只对将用于向 PPU 发送或从 PPU 接收数据的 buffer 进行 page-lock；如果 page-locked 的 host 内存过多，某些系统上性能可能会下降。

#### 2.1.3.3 内存管理与应用性能

- 显式内存管理更冗长，需要程序员显式指定 host 与 device 之间的 copy。这既是优势也是劣势：它提供了更强的控制能力——控制数据何时在 host 与 device 之间复制、内存驻留在何处、以及到底分配了哪些内存在何处。显式内存管理可以通过控制 memory transfers 并将其与其他计算重叠，从而带来性能机会。
- 使用 unified memory 时，也有 HGGC APIs（将在"Memory Advise and Prefetch"中覆盖），用于向管理内存的 HGGC driver 提供提示，从而在使用 unified memory 时也能获得一些类似显式内存管理的性能收益。

比赛关联：VLM 推理中图像预处理 H2D、KV cache 管理、logits D2H 都是热点。显式内存管理 + pinned memory + 异步拷贝是降低 TTFT 的标准手段；比赛服务器若只支持有限统一内存（见 §2.4.2.3），就更应使用显式管理。

### 2.1.4 同步 CPU 与 PPU

kernel launches 相对于调用它们的 CPU thread 是**异步的**：CPU thread 的控制流会在 kernel 完成之前继续执行，甚至可能在 kernel 还未 launch 之前就继续执行。为了保证在 host code 继续执行之前 kernel 已完成执行，需要某种同步机制。

- 同步 PPU 与 host thread 的最简单方式是使用 **`hggcDeviceSynchronize`**，它会阻塞 host thread，直到 PPU 上此前提交的**所有**工作都完成。
- 在更大的应用中，可能有多个 streams 在 PPU 上执行工作，而 `hggcDeviceSynchronize` 会等待所有 stream 中的工作完成。在这些应用中，推荐使用 **Stream Synchronization APIs** 仅与特定 stream 同步，或使用 **HGGC Event**（见"异步执行"章节）。

### 2.1.5 组合使用（完整示例代码）

下面给出本章引入的 ReLU 激活核函数的全部代码，以及所有 host code 与用于验证结果正确性的 utility functions。示例默认使用 1024 的数组长度，也接受通过可执行文件命令行参数传入不同的长度。

**Unified Memory 完整版本：**

```cpp
#include <hggc_runtime_api.h>
#include <memory.h>
#include <cstdlib>
#include <ctime>
#include <stdio.h>

__global__ void relu_activate(const float* input, float* output, int len)
{
    int tid = threadIdx.x + blockIdx.x * blockDim.x;
    if (tid < len)
    {
        output[tid] = (input[tid] > 0.0f) ? input[tid] : 0.0f;
    }
}

void fill_random(float* arr, int length)
{
    std::srand(std::time({}));
    for (int i = 0; i < length; i++)
    {
        arr[i] = (rand() / (float)RAND_MAX) * 2.0f - 1.0f;
    }
}

void cpu_relu(const float* input, float* output, int length)
{
    for (int i = 0; i < length; i++)
    {
        output[i] = (input[i] > 0.0f) ? input[i] : 0.0f;
    }
}

bool arrays_match(const float* a, const float* b, int length, float epsilon=0.00001f)
{
    for (int i = 0; i < length; i++)
    {
        if (fabs(a[i] - b[i]) > epsilon)
        {
            printf("Index %d mismatch: %f != %f", i, a[i], b[i]);
            return false;
        }
    }
    return true;
}

void unified_memory_example(int len)
{
    float* input = nullptr;
    float* output = nullptr;
    float* expected = (float*)malloc(len * sizeof(float));
    hggcMallocManaged(&input, len * sizeof(float));
    hggcMallocManaged(&output, len * sizeof(float));
    fill_random(input, len);
    int threadsPerBlock = 256;
    int blocksPerGrid = (len + threadsPerBlock - 1) / threadsPerBlock;
    relu_activate<<<blocksPerGrid, threadsPerBlock>>>(input, output, len);
    hggcDeviceSynchronize();
    cpu_relu(input, expected, len);
    if (arrays_match(output, expected, len))
    {
        printf("Unified Memory: 结果一致\n");
    }
    else
    {
        printf("Unified Memory: 结果不一致\n");
    }
    hggcFree(input);
    hggcFree(output);
    free(expected);
}

int main(int argc, char** argv)
{
    int len = 1024;
    if (argc >= 2)
    {
        len = std::atoi(argv[1]);
    }
    unified_memory_example(len);
    return 0;
}
```

**Explicit Memory Management 完整版本：**

```cpp
#include <hggc_runtime_api.h>
#include <memory.h>
#include <cstdlib>
#include <ctime>
#include <stdio.h>

__global__ void relu_activate(const float* input, float* output, int len)
{
    int tid = threadIdx.x + blockIdx.x * blockDim.x;
    if (tid < len)
    {
        output[tid] = (input[tid] > 0.0f) ? input[tid] : 0.0f;
    }
}

void fill_random(float* arr, int length)
{
    std::srand(std::time({}));
    for (int i = 0; i < length; i++)
    {
        arr[i] = (rand() / (float)RAND_MAX) * 2.0f - 1.0f;
    }
}

void cpu_relu(const float* input, float* output, int length)
{
    for (int i = 0; i < length; i++)
    {
        output[i] = (input[i] > 0.0f) ? input[i] : 0.0f;
    }
}

bool arrays_match(const float* a, const float* b, int length, float epsilon=0.00001f)
{
    for (int i = 0; i < length; i++)
    {
        if (fabs(a[i] - b[i]) > epsilon)
        {
            printf("Index %d mismatch: %f != %f", i, a[i], b[i]);
            return false;
        }
    }
    return true;
}

void explicit_memory_example(int len)
{
    size_t bytes = len * sizeof(float);
    float* h_input = nullptr;
    float* h_output = nullptr;
    float* expected = (float*)malloc(bytes);
    float* d_input = nullptr;
    float* d_output = nullptr;
    hggcMallocHost(&h_input, bytes);
    hggcMallocHost(&h_output, bytes);
    fill_random(h_input, len);
    hggcMalloc(&d_input, bytes);
    hggcMalloc(&d_output, bytes);
    hggcMemcpy(d_input, h_input, bytes, hggcMemcpyDefault);
    hggcMemset(d_output, 0, bytes);
    int threadsPerBlock = 256;
    int blocksPerGrid = (len + threadsPerBlock - 1) / threadsPerBlock;
    relu_activate<<<blocksPerGrid, threadsPerBlock>>>(d_input, d_output, len);
    hggcDeviceSynchronize();
    hggcMemcpy(h_output, d_output, bytes, hggcMemcpyDefault);
    cpu_relu(h_input, expected, len);
    if (arrays_match(h_output, expected, len))
    {
        printf("Explicit Memory: 结果一致\n");
    }
    else
    {
        printf("Explicit Memory: 结果不一致\n");
    }
    hggcFree(d_input);
    hggcFree(d_output);
    hggcFreeHost(h_input);
    hggcFreeHost(h_output);
    free(expected);
}

int main(int argc, char** argv)
{
    int len = 1024;
    if (argc >= 2)
    {
        len = std::atoi(argv[1]);
    }
    explicit_memory_example(len);
    return 0;
}
```

**线程协作与 `__syncthreads()`：**

- 在这些示例中，所有 threads 都在做彼此独立的工作，不需要彼此协调或同步。很多情况下，threads 需要协作并与其他 threads 通信以完成工作。一个 block 内的 threads 可以通过**共享内存**共享数据并同步，以协调内存访问。
- 在 block 层面最基本的同步机制是 **`__syncthreads()`** intrinsic，它充当一个 barrier：block 中的所有 threads 都必须在此等待，直到所有 threads 都到达之后才允许继续执行。
- 为了高效协作，shared memory 预计是靠近每个处理器核心的低延迟内存（很像 L1 cache），而 `__syncthreads()` 预计是轻量的。
- `__syncthreads()` **只同步单个 thread block 内的 threads**。HGGC programming model **不支持 block 间同步**。**协作组（Cooperative Groups）** 提供了将同步域设置为非单个 thread block 的机制。
- 最佳性能通常在同步限制在一个 thread block 内时获得。thread blocks 仍然可以使用 **atomic function** 来共同处理共享结果。

### 2.1.6 Runtime 初始化

HGGC runtime 采用**按需初始化策略**：每个 PPU 设备对应一个 **primary context**，该 context 在首次被任何 runtime API 实际使用时完成创建，并在进程内所有 host 线程间共享。

- **`hggcInitDevice`** 和 **`hggcSetDevice`** 调用会初始化 runtime 以及与指定 device 关联的 primary context。如果这些调用发生之前就出现 runtime API 请求，runtime 将隐式使用 device 0 并按需自初始化以处理这些请求。这在对 runtime function 调用进行计时时、以及解释第一次进入 runtime 的调用返回的错误码时很重要。

> **NOTE**：`hggcSetDevice` 在切换当前设备后会触发目标设备的 runtime 初始化（如果尚未完成）。之前的版本会延迟新设备上的 runtime 初始化，直到 `hggcSetDevice` 之后的第一次 runtime 调用。因此**务必检查其返回值**以捕获初始化错误。

- **`hggcDeviceReset`** 会销毁当前 device 的 primary context。如果在 primary context 被销毁之后仍调用 HGGC 运行时 APIs，则会为该 device 创建一个新的 primary context。

> **NOTE**：HGGC 运行时依赖进程级全局状态，该状态在 `main` 函数执行前的 C++ 静态初始化阶段尚未就绪，在 `main` 返回后的析构阶段也可能已被销毁。**在 `main` 之前或 `main` 之后的程序启动/终止阶段（隐式或显式）调用 HGGC API 会导致未定义行为。** 参考手册中错误处理与版本管理相关的函数属于例外——它们不会触发 runtime 初始化。

### 2.1.7 HGGC 中的错误检查

每个 HGGC API 都返回一个枚举类型 **`hggcError_t`** 的值。当没有错误时，返回值为 **`hggcSuccess`**。在示例代码中这些错误通常不被检查；在生产应用中，最佳实践是始终检查并处理每个 HGGC API 调用的返回值。许多应用选择实现如下所示的 utility macro：

```cpp
#define HGGC_CHECK(expr_to_check) do { \
    hggcError_t result = expr_to_check; \
    if(result != hggcSuccess) \
    { \
        fprintf(stderr, \
            "HGGC Runtime Error: %s:%i:%d = %s\n", \
            __FILE__, \
            __LINE__, \
            result,\
            hggcGetErrorString(result)); \
    } \
} while(0)
```

该 macro 使用 **`hggcGetErrorString`** API，它返回描述特定 `hggcError_t` 值含义的人类可读字符串。使用方式：

```cpp
HGGC_CHECK(hggcMalloc(&devA, vectorLength*sizeof(float)));
HGGC_CHECK(hggcMalloc(&devB, vectorLength*sizeof(float)));
HGGC_CHECK(hggcMalloc(&devC, vectorLength*sizeof(float)));
```

如果这些调用中任意一个检测到错误，该 macro 会把错误打印到 `stderr`。该 macro 在小型项目中很常见，但在大型应用中也可以适配到日志系统或其他错误处理机制中。

> **NOTE**：任何 HGGC API 调用返回的错误状态也可能表示**先前发出的异步操作的错误**（见"异步错误处理"）。

#### 2.1.7.1 错误状态

- HGGC runtime 为每个 host thread 维护一个 `hggcError_t` 状态。其默认值为 `hggcSuccess`，并在发生错误时被覆盖。
- **`hggcGetLastError`** 返回当前错误状态，然后将其重置为 `hggcSuccess`。
- **`hggcPeekAtLastError`** 返回错误状态但不重置。
- 使用三重尖括号的 kernel launches **不返回 `hggcError_t`**。最佳实践是在 kernel launch 之后立即检查错误状态，以检测 kernel launch 的即时错误或 kernel launch 之前的异步错误。在 kernel launch 后立即检查错误状态得到 `hggcSuccess` **并不意味着 kernel 已成功执行，甚至不意味着它已开始执行**——这只验证传递给 runtime 的 kernel launch 参数和执行配置没有触发任何错误，并且错误状态不是 kernel 开始前的历史或异步错误。

推荐的错误检查模式：

```cpp
relu_activate<<<blocksPerGrid, threadsPerBlock>>>(d_input, d_output, len);
// check error state after kernel launch
HGGC_CHECK(hggcGetLastError());
// wait for kernel execution to complete
// The HGGC_CHECK will report errors that occurred during execution of the kernel
HGGC_CHECK(hggcDeviceSynchronize());
```

#### 2.1.7.2 异步错误

- HGGC kernel launches 和许多运行时 APIs 都是异步的。HGGC error state 在发生错误时会设置并覆盖。这意味着在异步操作执行期间发生的错误，只有在下次检查错误状态时才会被报告（`hggcGetLastError`、`hggcPeekAtLastError`，或任何返回 `hggcError_t` 的 HGGC API）。
- 当 HGGC 运行时 API functions 返回错误时，**错误状态不会被清除**。这意味着来自异步错误（例如 kernel 的非法内存访问）的错误码，会被每个 HGGC 运行时 API 返回，直到通过调用 `hggcGetLastError` 清除了错误状态。

> **NOTE**：`hggcError_t` 值 **`hggcErrorNotReady`**（可能由 `hggcStreamQuery` 和 `hggcEventQuery` 返回）**不被视为错误**，且不会被 `hggcPeekAtLastError` 或 `hggcGetLastError` 报告。

### 2.1.8 Device 与 Host 函数

- **`__global__`** 标识符用于指示 kernel 的入口点，即一个会在 PPU 上被并行执行调用的函数。
- **`__device__`** 表示一个函数应为 PPU 编译，并可从其他 `__device__` 或 `__global__` functions 调用。
- 一个函数（包括 class member functions、functors 和 lambdas）可以同时指定为 **`__device__` 与 `__host__`**。

### 2.1.9 变量限定符

HGGC C++ 中提供的变量限定符：

| 限定符 | 声明位置/含义 |
|---|---|
| `__device__` | 声明全局内存空间中的变量 |
| `__constant__` | 声明常量内存空间中的变量 |
| `__managed__` | 声明统一内存空间中的变量 |
| `__shared__` | 声明共享内存空间中的变量 |

- 如果一个变量没有使用变量限定符，而被声明在 `__device__` 或 `__global__` **内**的，一般被认为是**局部变量**；而声明在 `__device__` 或 `__global__` **外**的，被认为是存于**系统内存**中。

#### 2.1.9.1 检测设备编译

当函数被指定为 `__host__ __device__` 时，编译器会为该函数同时生成 PPU 和 CPU 版本的代码。在此类函数中，往往需要利用预处理器来指定仅适用于 PPU device 或 CPU host 版本函数的代码。

---

## 2.2 编写 HGGC SIMT 核函数程序

编写 HGGC C++ 核函数程序可以像为特定问题编写传统 CPU 代码的方式一样进行。然而，PPU 有一些独特的特性可用于提高性能。了解 PPU 上的线程是如何调度的、它们如何访问内存以及其执行过程如何推进，可以帮助开发人员编写能最大化利用可用计算资源的核函数程序。

### 2.2.1 SIMT 基础

- 从开发者的角度来看，HGGC Thread 线程是并行性的基本单位。**SIMT 模型允许每个线程维护自己的状态和控制流**。从功能的角度来看，每个线程都可以执行一个独立的代码路径。
- **性能优化要点**：通过注意让核函数代码在执行同一线程束（**warp**）中的线程时，**尽量不发生分叉执行或者分叉执行情况尽可能少**，可以获得显著的性能提升。

比赛关联：写 attention/采样/量化 kernel 时，warp 内分支分叉（divergence）是首要避免项——例如让同一 warp 的线程处理相同形状的分支、用掩码代替 if-else。

### 2.2.2 线程层次结构

组织结构：线程被组织成 **线程块（Thread Blocks）→ 网格（Grid）**。网格可以是一维、二维或三维的，线程块也可以是一维、二维或三维的。

关键内置变量：

| 变量 | 描述 |
|---|---|
| `gridDim.[x\|y\|z]` | 分别表示 x、y 和 z 维度上网格的大小（核函数启动时设置） |
| `blockDim.[x\|y\|z]` | 分别表示 x、y 和 z 维度上线程块的大小（核函数启动时设置） |
| `blockIdx.[x\|y\|z]` | 分别表示 x、y 和 z 维度上线程块的索引（根据正在执行的线程块变化） |
| `threadIdx.[x\|y\|z]` | 分别表示 x、y 和 z 维度上线程的索引（根据正在执行的线程变化） |

**多维线程布局说明**：多维线程块和网格仅是为了方便起见，**不会影响性能**。线程块中的线程以可预测的方式线性化：

- 第一个索引 `x` 移动最快，其次是 `y`，最后是 `z`；
- 连续的 `threadIdx.x` 值表示连续的线程；
- `threadIdx.y` 有 `blockDim.x` 的步长；
- `threadIdx.z` 有 `blockDim.x * blockDim.y` 的步长。

这会影响线程分配给 warp 的方式。

### 2.2.3 PPU 设备内存空间

HGGC 设备提供多种内存空间供线程在核函数中访问：

| 内存类型 | 范围 | 生命周期 | 物理位置 |
|---|---|---|---|
| Global 全局 | Grid 网格 | 应用程序 | device 设备 |
| shared 共享 | Block 块 | 核函数 | 计算单元（CU） |
| local 局部 | Thread 线程 | 核函数 | device 设备 |
| Register 寄存器 | Thread 线程 | 核函数 | 计算单元（CU） |

#### 2.2.3.1 全局内存

全局内存（也称为设备内存）是主要的内存空间，存储核函数中所有线程可访问的数据，类似于 CPU 系统的 RAM。

特点：

- **持久化存储**：分配及其中数据会一直存在直到释放或应用程序终止。
- 全局内存使用 HGGC API 调用分配，例如 `hggcMalloc` 和 `hggcMallocManaged`；可以使用 `hggcMemcpy` 将数据从 CPU 内存复制到全局内存；使用 `hggcFree` 释放。
- 在核函数启动之前，全局内存由 HGGC API 调用分配和初始化。核函数执行期间，HGGC 线程可以从全局内存读取数据，执行结果可以写回全局内存。核函数完成后，写入全局内存的结果可以复制回主机或由 PPU 上的其他核函数使用。
- 由于全局内存可供网格中的所有线程访问，**必须注意避免线程之间的数据竞争**。
- 由于从主机启动的 HGGC 核函数返回类型为 `void`，**核函数计算的数值结果返回给主机的唯一方法是将这些结果写入全局内存**。
- 虽然运算单元可以直接使用全局内存，但是并不能直接访问到全局内容，需要经过缓存：

```
graph LR
A[global memory] --> B[LLC]
B --> C[L2 cache]
C --> D[L1 cache]
D --> E[Register]
```

#### 2.2.3.2 共享内存

共享内存是一种高速缓存内存，由同一线程块内的所有线程共享。由于共享内存比全局内存快得多，因此经常用于实现协作算法，如归约（reduction）操作。与全局内存相比，共享内存还**支持原子操作**，并且对相同地址的并发读取能够**广播**到请求的线程。

使用共享内存的例子（block 内归约求和）：

```cpp
#define BLOCK_SIZE 512 // 必须满足2的幂
__global__ void sumReduction(float* d_in, float* d_out) {
    // 1. block内声明共享内存
    __shared__ float sdata[BLOCK_SIZE];
    unsigned int tid = threadIdx.x;
    unsigned int i = blockIdx.x * (blockDim.x * 2) + threadIdx.x;
    // 2. 将数据从全局内存加载到共享内存中
    sdata[tid] = d_in[i] + d_in[i + blockDim.x];
    __syncthreads(); // Ensure all loads are complete
    // 3. 在共享内存中执行规约操作
    for (unsigned int s = blockDim.x / 2; s > 0; s >>= 1) {
        if (tid < s) {
            sdata[tid] += sdata[tid + s];
        }
        // 4. 每次执行后同步所有线程
        __syncthreads();
    }
    // 5. 数据从共享内存写回到全局内存中
    if (tid == 0) d_out[blockIdx.x] = sdata[0];
}
```

- 共享内存的大小因使用的 PPU 架构而异，每一代 PPU 都有对应的共享内存大小配置。
- HGGC 运行时 API 提供函数来查询**基于 CU** 和**基于线程块**的共享内存大小：使用 **`hggcDeviceGetAttribute`** 函数查询 **`hggcDevAttrSharedMemPerMultiprocessor`** 和 **`hggcDevAttrSharedMemPerBlock`** 设备属性。
- 共享内存既可以静态分配，也可以动态分配。

##### 2.2.3.2.1 共享内存的静态分配

要静态分配共享内存，程序员必须在核函数内部使用 `__shared__` 说明符声明一个变量。该变量将在共享内存中分配，并在整个核函数执行期间持续存在。以这种方式声明的共享内存的大小**必须在编译时指定**。例如，以下代码片段位于核函数主体中，声明了一个 float 类型的包含 1024 个元素的共享内存数组：

```cpp
__shared__ float sharedArray[1024];
```

在此声明后，线程块中的所有线程都将有权访问这个共享内存数组。需要注意避免同一线程块中线程之间的数据竞争，通常使用 `__syncthreads()`。

##### 2.2.3.2.2 共享内存的动态分配

要动态分配共享内存，程序员可以在三重尖括号符号中作为**第三个（也是可选的）参数**指定每个线程块所需的共享内存量（以字节为单位）：

```cpp
functionName<<<grid, block, sharedMemoryBytes>>>();
```

然后，在核函数内部，程序员可以使用 `extern __shared__` 说明符来声明一个将在核函数启动时动态分配的变量：

```cpp
extern __shared__ float sharedArray[];
```

注意事项：如果想要多个动态分配的共享内存数组，则单个 `extern __shared__` 声明只能处理一种数组类型，需要其他方法来处理多种类型的动态共享内存。

比赛关联：归约模板（如上面的 sumReduction）可直接套用到 RMSNorm、Softmax、Logits 求 max 等 LLM kernel；动态共享内存第三参数是写可配置 tile 大小 GEMM/attention kernel 的必备语法。

#### 2.2.3.3 寄存器

- 寄存器是最快速度的内存形式，直接集成在 CU 中。寄存器是本地线程范围的，只有创建它的线程才能访问它。
- 寄存器的数量有限，当核函数使用超过可用数量时，可能会发生**寄存器溢出到局部内存（local memory）**。
- 在 PPU 中，物理存在两种寄存器：
  - **向量寄存器（VREG，Vector Register）**：warp 内每个 thread 都有自己存储空间的寄存器；
  - **标量寄存器（SREG，Scalar Register）**：整个 warp 内所有 thread 共享的寄存器。
- 寄存器被 hgcc 编译器分配和使用。**合理搭配使用 VREG 和 SREG 数量，可以使 Kernel 程序执行更加高效。**

#### 2.2.3.4 局部内存

局部内存是每个线程专用的内存区域。虽然名为"局部"，但它实际上**驻留在全局内存中**，只是作用域限制在单个线程内。局部内存主要用于存储不适合放入寄存器的大型或复杂变量，如大数组或未展开的循环变量。访问局部内存的速度与访问全局内存相似，因此应尽量减少对局部内存的访问。

编译器很可能将其分配至局部存储器（Local Memory）的自动变量包括：

- 编译器无法确定其索引是否为常量的数组；
- 体积过大、会占用过多寄存器空间的大型结构体或数组；
- 当核函数所需的寄存器数量超过可用数量时，任何受此影响的变量（即发生"寄存器溢出"现象时的变量）。

由于局部存储空间位于全局设备存储器中，因此对局部存储器的访问具有与全局存储器访问相同的延迟和带宽。**一般核函数程序中少出现或者不出现局部内存，会是程序优化的一个手段。** 但是局部变量静态的多或者少，并不能决定程序执行效率的高低。

#### 2.2.3.5 缓存

PPU 设备有多级缓存结构，包括 L2 和 L1 缓存、LLC 缓存：

- **LLC（Last Level Cache）** 位于设备上，由所有 CE 共享，提供上层访问到 HBM 的最后一级缓存。
- **L2 缓存** 位于设备上，由 CE 内的所有 CU 共享。L2 缓存的大小可以通过 `hggcDeviceGetAttribute` 函数查询 **`hggcDevAttrL2CacheSize`** 设备属性。
- **L1 缓存** 物理上位于每个 CU 上。
- L2 和 L1 缓存可通过函数进行控制，这些函数允许开发者指定各种缓存行为（详细信息见"配置 hgcc 指令配置表"）。如果不使用这些函数/提示，编译器和运行时将尽力高效地利用缓存。

### 2.2.4 原子操作

原子操作是这样的一组函数：它们在一个内存位置上执行**读-修改-写（read-modify-write）**操作，而不受其他线程可能也在访问同一内存位置的影响。当多个线程试图同时更新相同的数据位置时，原子操作非常重要。

hggc 提供的原子操作函数包括：

| 类别 | 函数 |
|---|---|
| 算术 | `atomicAdd`、`atomicSub`、`atomicInc`、`atomicDec`、`atomicMin`、`atomicMax` |
| 交换/CAS | `atomicExch`、`atomicCAS` |
| 位运算 | `atomicAnd`、`atomicOr`、`atomicXor` |
| 新接口（可指定线程范围） | `hggc::atomic`、`hggc::atomic_ref` |

以下是一个使用 `hggc::atomic_ref` 执行设备范围内原子加法的示例，其中 `array` 是一个浮点数组，`result` 是指向全局内存中某个位置的浮点指针，该位置是要存储数组之和的地方：

```cpp
__global__ void sumReduction(int n, float *array, float *result) {
    ...
    tid = threadIdx.x + blockIdx.x * blockDim.x;
    hggc::atomic_ref<float, hggc::thread_scope_device> result_ref(result);
    result_ref.fetch_add(array[tid]);
    ...
}
```

**应谨慎使用原子函数**，因为它们强制执行线程同步，可能会影响性能。

比赛关联：split-K GEMM、streaming softmax 的部分和累加、采样时的全局计数器都可用 `hggc::atomic_ref<float, hggc::thread_scope_device>`；但高竞争原子操作会成为吞吐瓶颈，优先考虑 warp/block 内归约后再做一次原子加。

### 2.2.5 协作组

协作组（Cooperative Groups）是 HGGC C++ 中可用的一种软件工具，允许应用程序定义一组可以相互同步的线程，即使该组线程跨越多个线程块、单个 PPU 上的多个网格，甚至跨多个 PPU 也是如此。

- 一般而言，HGGC 编程模型允许线程块内的线程有效同步，但没有提供指定小于线程块的线程组的机制；同样也没有提供跨线程块同步的机制或保证。
- 协作组通过软件提供这两种能力。协作组允许应用程序创建跨越线程块和簇边界的线程组，尽管这样做会带来一些语义限制和性能影响。

### 2.2.6 核函数启动和占用率

- 启动 HGGC 核函数时，HGGC 线程根据执行配置被分组为线程块和网格。一旦核函数启动，调度程序将线程块分配给 CU。**哪些线程块被安排在哪些 CU 上执行的细节无法由应用程序控制或查询，调度程序也不做任何排序保证**，因此程序不能依赖于特定的调度顺序或方案来进行正确执行。
- 可以安排在 CU 上的块数取决于给定线程块所需的硬件资源以及 CU 上可用的硬件资源。调度过程：核函数首次启动时，调度程序开始将线程块分配给 CU；只要 CU 有空闲的硬件资源不受其他线程块占用，就继续分配；如果没有 CU 有能力接受另一个线程块，调度程序将等待 CUs 完成先前分配的线程块；此过程持续到所有线程块都被调度和执行完毕。
- **占用率（Occupancy）** 是衡量活跃 warp 数占 CU 最大潜在 warp 数比例的指标。高占用率有助于掩盖内存延迟，但并非总是最佳选择，因为它可能导致更多的寄存器压力和共享内存争用。**占用率计算器（occupancy calculator）** 可帮助确定理论占用率，并建议调整块大小（block dimensions）或共享内存使用量以提高占用率。
- **寄存器使用量直接影响占用率**：每个 CU 上有固定数量的寄存器，如果一个核函数每个线程使用大量寄存器，那么在任何时间点可以活动的线程数就会减少。程序员可以通过 hgcc 的 **`--maxrregcount`** 选项指定每个线程的最大寄存器数。如果核函数需要的寄存器数量超过了指定的数量，核函数很可能会溢出到局部内存，这将改变核函数的性能特征。在某些情况下，即使发生了溢出，限制寄存器也能允许多个线程块被调度，从而增加占用率，可能导致净性能提升。
- 通常 kernel 核函数程序占用率可以通过 HGGC 提供的 API 和 PPU 提供的软件工具 **Asight** 工具采集得到。

真实用例中 Asight 工具采集到的信息（日常开发可通过相关字段和提示信息进行分析）：

| 指标类别 | 数值 | 资源限制 | 值 |
|---|---|---|---|
| Theoretical Occupancy[%] | 100 | Block Limit Registers [block] | 32 |
| TheoreticalActive WarpsperCU[warp/cycle] | 64 | Block Limit Shared Mem [block] | 64 |
| Achieved Occupancy [%] | 0.09 | Block Limit Warps[block] | 16 |
| Achieved Active WarpsPer CU [warp/cycle] | 0.06 | Block Limit CU [block] | 64 |

比赛关联：`--maxrregcount` + Asight 占用率分析是 kernel 调优的闭环：先看 Achieved Occupancy 与 Theoretical 的差距，再判断瓶颈是寄存器、共享内存还是 warp 数限制，对应调整 block size 或寄存器上限。上表"理论 100% vs 实际 0.09%"说明实测值可能远低于理论值，必须实测。

### 2.2.7 PPU 内存

#### 2.2.7.1 异构系统中的 DRAM 内存

- PPU 和 CPU 都配有直连的 DRAM 芯片。在拥有多个 PPU 的系统中，每个 PPU 都有自己的内存。
- 从设备代码的角度，连接到 PPU 的 DRAM 被称为**全局内存（global memory）**，因为它可以被 PPU 中的所有 CU 访问（不意味着在整个系统中都能访问）。连接到 CPU 的 DRAM 被称为**系统内存（system memory）或宿主内存（host memory）**。
- 与 CPU 类似，PPU 使用虚拟内存寻址。在所有当前支持的系统中，**CPU 和 PPU 使用统一的虚拟内存空间（virtual memory space）**。系统中每个 PPU 的虚拟内存地址范围都是唯一且与其他 CPU 及其他 PPU 不同的。对于给定的虚拟内存地址，可以确定该地址位于 PPU 内存还是系统内存中，以及在多 PPU 系统中哪个 PPU 内存包含了该地址。
- HGGC API 可以用于分配 PPU 内存、CPU 内存，以及在 CPU 和 PPU 之间、PPU 内部或者多 PPU 系统的 PPU 之间复制内存。统一内存（Unified Memory）允许自动处理内存放置，由 HGGC 运行时或系统硬件自动管理。

#### 2.2.7.2 PPU 中的片上内存

- 除了全局内存之外，每个 PPU 还有一些片上内存。**每个 CU 都有自己的寄存器文件（register file）和共享内存（shared memory）**。这些内存是 CU 的一部分，可以从在 CU 内执行的线程非常快速地访问，但无法被在其他 CU 中运行的线程访问。
- 寄存器文件存储线程局部变量，通常由编译器分配。共享内存可供线程块的所有线程访问，用于在线程块的线程之间交换数据。
- CU 中的寄存器文件和数据缓存大小有限。CU 的寄存器文件大小、统一数据缓存以及共享内存大小可在"计算能力"一节中找到。寄存器文件、共享内存空间和 L1 缓存由线程块中的所有线程共享。
- **要将线程块调度到 CU，每个线程所需的寄存器总数乘以线程块中的线程数必须小于或等于 CU 中的可用寄存器数。** 如果线程块所需的寄存器数超过了寄存器文件的大小，则核函数无法启动，必须减少线程块中的线程数才能使其能够启动。
- **共享内存分配是以线程块级别进行的**——与按线程分配的寄存器不同，共享内存的分配是整个线程块共有的。

##### 2.2.7.2.1 缓存

- 除了可编程内存，PPU 还有 L1、L2、LLC 缓存。
- 离寄存器文件最近的是 **CU 独有的 L1 缓存**。
- 较大的 **L2 缓存由 CE（Compute Engine，CU 的上一层硬件结构）内的所有 CU 共享**。
- L2 之下还有一层 **LLC 缓存**，负责 DDR 通道的 global memory 和 L2 之间进行缓存数据，进一步缓解各层带宽的速度不匹配问题。

#### 2.2.7.3 统一内存

- 当应用程序明确在 PPU 或 CPU 上分配内存时，该内存只能被运行在该设备上的代码访问。CPU 内存只能从 CPU 代码访问，PPU 内存只能从在 PPU 上运行的核函数访问。HGGC API 用于在适当的时间显式地将数据复制到正确的内存中。
- 统一内存（unified memory）允许应用程序进行内存分配，以便可以从 CPU 或 PPU 访问。HGGC 运行时或底层硬件启用访问或在需要时重新定位数据。
- 即使有了统一内存，**最优性能仍然是通过最小化内存迁移并尽可能多地从直接连接到内存所在的处理器访问数据来实现的**。
- 系统的硬件特性决定了内存空间之间数据访问和交换的实现方式。

---

## 2.3 异步编程模式

### 2.3.1 异步执行基础

HGGC 允许并发（或重叠）执行多个任务，具体包括：

- 主机上的计算
- 设备上的计算
- 从主机到设备的内存传输
- 从设备到主机的内存传输
- 在给定设备内存内部的内存传输
- 设备之间的内存传输

并发通过异步接口表达，其中调度函数调用或核函数启动会立即返回。异步调用通常在所调度的操作完成之前就返回了，甚至可能在异步操作开始之前就返回了。然后应用程序可以自由地执行其他任务，同时执行最初调度的操作。当需要初始调度操作的最终结果时，应用程序必须执行某种形式的同步。一个典型的并发执行模式是**将主机和设备内存传输与计算重叠**，从而减少或消除其开销。

异步接口提供三种主要的同步方式：

| 同步方式 | 说明 |
|---|---|
| 阻塞方式 | 应用程序调用一个阻塞（或等待）直到操作完成的函数 |
| 非阻塞方式（轮询方式） | 应用程序调用一个立即返回并提供操作状态信息的函数 |
| 回调方式 | 当操作完成时执行预注册的函数 |

虽然编程接口是异步的，但实际执行各种并发操作的能力将取决于 HGGC 的版本和硬件的计算能力（参见"计算能力"）。

- `hggcDeviceSynchronize()` 是一个阻塞调用，会等待所有先前发出的工作完成。需要它的原因是核函数启动是异步的、会立即返回。HGGC 为同步提供了阻塞和非阻塞两种方式的 API，甚至支持使用主机端回调函数。
- HGGC 中异步执行的核心 API 组件是 **HGGC 流（Stream）** 和 **HGGC 事件（Event）**。
- 相关主题：**HGGC 图（Graph）**，允许预先定义异步操作图，然后以最小的开销重复执行（在"使用流捕获介绍 HGGC 图"入门介绍，在"HGGC 图"更全面讨论）。

### 2.3.2 流与事件

#### 2.3.2.1 流的创建与基本使用

- **HGGC 流是一种允许程序员表达操作序列的抽象**。流就像一个工作队列，程序可以向其中添加操作（如内存复制或核函数启动），并按顺序执行。给定流的队列前端的操作执行后出队，允许下一个排队的操作来到前端并被考虑执行。**流中操作的执行顺序是顺序的，操作按其入队的顺序执行。**
- 应用程序可以同时使用多个流。在这种情况下，运行时将根据 PPU 资源的状态从有可用工作的流中选择要执行的任务。**流可以被分配优先级**，作为提示来影响运行时调度，但不保证特定的执行顺序。
- 在流中操作的 API 函数调用和核函数启动相对于主机线程是异步的。应用程序可以等待流中的任务全部完成来与流同步，也可以在设备级别进行同步。
- HGGC 有一个**默认流**，没有指定特定流的操作和核函数启动会被加入这个默认流。

HGGC 流可以使用 `hggcStreamCreate()` 函数创建。该函数调用初始化流句柄，后续函数调用可以使用该句柄来标识流：

```cpp
// 创建流、使用流、销毁流的基本流程
hggcStream_t stream;
hggcStreamCreate(&stream);
// 在流上提交操作（核函数启动、内存传输等）
// ...
// 流使用完毕后销毁
hggcStreamDestroy(stream);
```

如果在应用程序调用 `hggcStreamDestroy()` 时设备仍在流 stream 中执行工作，**流将在被销毁之前完成流中的所有工作**。

启动核函数通常使用的三尖括号语法也可以用于将核函数启动到特定流中。流作为核函数启动的额外（第 4 个）参数指定：

```cpp
kernel<<<grid, block, shared_mem_size, stream>>>(...);
```

核函数启动是异步的，函数调用立即返回。假设核函数启动成功，核函数将在流 stream 中执行，应用程序可以自由地在核函数执行期间在 CPU 上或其他流中执行其他任务。

要将内存传输启动到流中，可以使用 **`hggcMemcpyAsync()`** 函数。该函数类似于 `hggcMemcpy()`，但需要一个额外参数来指定用于内存传输的流：

```cpp
// PPU 异步数据搬运：使用 pinned memory 配合 AIU 实现传输与计算重叠
float *src;
hggcMallocHost(&src, size); // 分配 pinned memory（页锁定主机内存）
float *dst;
hggcMalloc(&dst, size);     // 分配设备内存

// AIU 异步传输：在流 stream 中执行，与后续核函数可并行
hggcMemcpyAsync(dst, src, size, hggcMemcpyHostToDevice, stream);
```

- 与其他异步函数调用一样，此函数调用立即返回，而 `hggcMemcpy()` 会阻塞直到内存传输完成。为了安全访问传输的结果，应用程序必须使用某种形式的同步来确定操作已完成。
- 其他 HGGC 内存传输函数（如 `hggcMemcpy2D()`）也有异步变体。

> **NOTE**：为了使涉及 CPU 内存的内存复制能够异步执行，**主机缓冲区必须是固定的且被页锁定的**。如果使用未固定和未页锁定的主机内存，`hggcMemcpyAsync()` 将正常工作，但它会恢复为同步行为，不会与其他工作重叠，这会抑制使用异步内存传输的性能优势。建议程序使用 `hggcMallocHost()` 分配将用于向 PPU 发送或从 PPU 接收数据的缓冲区。

#### 2.3.2.2 事件与依赖跟踪

- **HGGC 事件是一种向 HGGC 流中插入标记的机制**。它们本质上是示踪粒子，可用于跟踪流中任务的进度。例如向一个流中启动两个核函数：没有跟踪事件时，只能确定流是否为空；在两个核函数之间插入事件后，可以等待事件到达流的前端，从而知道第一个核函数已完成但第二个尚未开始，可以安全地启动依赖操作。
- 以这种方式使用 HGGC 事件可以**构建操作和流之间的依赖图**（该图类比直接转化到 HGGC 图的讨论中）。
- HGGC 事件还**保留时间信息**，可用于计时核函数启动和内存传输。

HGGC 事件可以使用 `hggcEventCreate()` 和 `hggcEventDestroy()` 函数创建和销毁：

```cpp
hggcEvent_t inferenceEvent;
// 创建事件
hggcEventCreate(&inferenceEvent);
// 使用事件跟踪推理流水线进度
// ...
// 事件不再需要时销毁
hggcEventDestroy(inferenceEvent);
```

应用程序负责在不再需要事件时销毁它们。

可以使用 **`hggcEventRecord(hggcEvent_t event, hggcStream_t stream)`** 函数将事件记录到指定流中，第一个参数为要记录的事件对象，第二个参数为目标流：

```cpp
hggcEvent_t stageComplete;
hggcStream_t stream;
// 创建事件
hggcEventCreate(&stageComplete);
// 将事件插入流中，标记当前阶段完成
hggcEventRecord(stageComplete, stream);
```

**事件计时**：HGGC 事件可用于对包括核函数在内的各种流操作进行计时。当事件到达流的前端时，它会记录一个时间戳。通过在流中用两个事件包围目标操作，可以获得精确的执行耗时：

```cpp
// 使用事件计时测量 PPU 核函数与数据传输的执行耗时
// 假设 kernel 已定义为执行目标计算的 __global__ 函数
hggcStream_t stream;
hggcStreamCreate(&stream);
hggcEvent_t kernelStart, kernelEnd;
hggcEvent_t memcpyStart, memcpyEnd;
// 创建计时事件
hggcEventCreate(&kernelStart);
hggcEventCreate(&kernelEnd);
hggcEventCreate(&memcpyStart);
hggcEventCreate(&memcpyEnd);
// 阶段1：测量数据传输耗时
hggcEventRecord(memcpyStart, stream);
hggcMemcpyAsync(d_input, h_input, dataSize, hggcMemcpyHostToDevice, stream);
hggcEventRecord(memcpyEnd, stream);
// 阶段2：测量核函数执行耗时
hggcEventRecord(kernelStart, stream);
kernel<<<grid, block, 0, stream>>>(d_input, d_output, numElements);
hggcEventRecord(kernelEnd, stream);
// 同步并获取计时结果
hggcStreamSynchronize(stream);
float memcpyTime, kernelTime;
hggcEventElapsedTime(&memcpyTime, memcpyStart, memcpyEnd);
hggcEventElapsedTime(&kernelTime, kernelStart, kernelEnd);
// 清理
hggcEventDestroy(kernelStart);
hggcEventDestroy(kernelEnd);
hggcEventDestroy(memcpyStart);
hggcEventDestroy(memcpyEnd);
hggcStreamDestroy(stream);
```

**阻塞式事件同步 `hggcEventSynchronize()`**：阻塞直到事件完成。下面的代码片段向一个流中启动一个核函数，然后是一个事件，然后是第二个核函数；等待第一个核函数之后的事件完成，原则上可以立即启动依赖任务（可能在 kernel2 完成之前）：

```cpp
// PPU 推理流水线中使用事件同步
hggcEvent_t inferEvent;
hggcStream_t pipeline;
// 创建流和事件
hggcStreamCreate(&pipeline);
hggcEventCreate(&inferEvent);
// 向流中启动推理预处理核函数
preprocess_kernel<<<grid, block, 0, pipeline>>>(d_input, d_prepared);
// 在第一个核函数之后插入事件
hggcEventRecord(inferEvent, pipeline);
// 向流中启动推理核函数
inference_kernel<<<grid, block, 0, pipeline>>>(d_prepared, d_output);
// 等待事件完成——此时第一个核函数已完成
// 可以安全地启动依赖于预处理结果的 CPU 任务
hggcEventSynchronize(inferEvent);
dependentCPUtask();
// 等待流中所有工作完成
hggcStreamSynchronize(pipeline);
// 清理
hggcEventDestroy(inferEvent);
hggcStreamDestroy(pipeline);
```

**非阻塞式事件查询 `hggcEventQuery()`**：以非阻塞方式检查事件完成状态。下面的示例向一个流中启动 2 个核函数：kernel1 生成一些数据希望复制到主机，但也有 CPU 端的工作要做。在流 stream1 中入队 kernel1，然后是事件 event，然后是 kernel2；然后进入 CPU 工作循环，偶尔查看事件是否已完成（表示 kernel1 已完成），如果是，就在流 stream2 中启动主机到设备的复制。这种方法允许 CPU 工作与 PPU 核函数执行以及设备到主机复制重叠：

```cpp
// PPU 训练场景：CPU 端数据预处理与 PPU 计算重叠
hggcEvent_t computeDone;
hggcStream_t computeStream, transferStream;
hggcStreamCreate(&computeStream);
hggcStreamCreate(&transferStream);
hggcEventCreate(&computeDone);
float *d_batchA, *d_batchB, *d_grad;
float *h_nextBatch;
hggcMalloc(&d_batchA, batchSize);
hggcMalloc(&d_batchB, batchSize);
hggcMalloc(&d_grad, gradSize);
hggcMallocHost(&h_nextBatch, batchSize);
bool transferStarted = false;
// 在 computeStream 中启动当前批次的前向+反向传播
forward_kernel<<<grid, block, 0, computeStream>>>(d_batchA, d_grad);
backward_kernel<<<grid, block, 0, computeStream>>>(d_grad, d_batchA);
hggcEventRecord(computeDone, computeStream);
// CPU 端：准备下一批数据（数据增强、归一化等）
// 同时轮询 PPU 计算是否完成
while (!allPreprocessingDone()) {
    preprocessNextSample(h_nextBatch);
    // 非阻塞检查 PPU 计算是否完成
    if (!transferStarted && hggcEventQuery(computeDone) == hggcSuccess) {
        // PPU 计算完成，立即启动下一批数据传输
        hggcMemcpyAsync(d_batchB, h_nextBatch, batchSize,
                        hggcMemcpyHostToDevice, transferStream);
        transferStarted = true;
    }
}
// 确保传输完成
if (!transferStarted) {
    hggcEventSynchronize(computeDone);
    hggcMemcpyAsync(d_batchB, h_nextBatch, batchSize,
                    hggcMemcpyHostToDevice, transferStream);
}
hggcStreamSynchronize(transferStream);
hggcStreamSynchronize(computeStream);
hggcEventDestroy(computeDone);
hggcStreamDestroy(computeStream);
hggcStreamDestroy(transferStream);
hggcFree(d_batchA);
hggcFree(d_batchB);
hggcFree(d_grad);
hggcFreeHost(h_nextBatch);
```

#### 2.3.2.3 流/事件的同步策略

与流同步的最简单方法是等待流中的任务全部完成。这可以通过两种方式完成：使用 `hggcStreamSynchronize()` 函数或 `hggcStreamQuery()` 函数。

**`hggcStreamSynchronize()`** 将阻塞直到流中的所有工作完成：

```cpp
// 等待流中的所有操作完成
hggcStreamSynchronize(stream);
// 此时流已完成
// 可以安全地访问流操作的结果
```

如果不想阻塞，只想快速检查流是否为空，可以使用 **`hggcStreamQuery()`**：

```cpp
// 非阻塞查询流状态
// 如果流为空则返回 hggcSuccess
// 如果流不为空则返回 hggcErrorNotReady
hggcError_t status = hggcStreamQuery(stream);
switch (status) {
case hggcSuccess:
    // 流中所有操作已完成
    break;
case hggcErrorNotReady:
    // 仍有操作在执行
    break;
default:
    // 发生错误——应进行错误处理
    break;
};
```

**显式同步 API 对照表：**

| API | 同步范围 | 阻塞行为 | 典型用途 |
|---|---|---|---|
| `hggcDeviceSynchronize()` | 所有主机线程的所有流 | 阻塞至全部完成 | 全局同步，通常用于调试或程序结束前 |
| `hggcStreamSynchronize()` | 指定的单个流 | 阻塞至该流完成 | 仅等待特定流完成，不影响其他流继续执行 |
| `hggcStreamWaitEvent()` | 跨流依赖 | 非阻塞（向流中插入等待点） | 建立流间执行顺序——使目标流后续命令等待指定事件完成（事件相关说明见 HGGC 事件） |
| `hggcStreamQuery()` | 指定的单个流 | 非阻塞（立即返回状态） | 轮询检查流中所有先前命令是否已完成 |

**隐式同步**：除显式同步外，NULL 流（默认流）上的操作还会引入隐式的序列化约束。具体而言：当两个分属不同流的操作之间插入了一次 NULL 流上的提交，这两个操作将无法并发执行。此约束**不适用于以 `hggcStreamNonBlocking` 标志创建的非阻塞流**——非阻塞流不受 NULL 流的序列化影响。

为最大化核函数的并发执行潜力，建议在实践中注意以下两点：

- 优先提交不存在数据依赖的操作，将有依赖关系的操作排在后面；
- 将同步点尽量推迟到真正需要结果的时刻。

**阻塞和非阻塞流与默认流**——HGGC 中的流按其与默认流（NULL 流）的同步关系分为两类：

| 流类型 | 创建方式 | 与默认流的关系 |
|---|---|---|
| 阻塞流 | `hggcStreamCreate()` | 与默认流互相等待——默认流上的操作会等待所有阻塞流排空，反之亦然 |
| 非阻塞流 | `hggcStreamCreateWithFlags(&s, hggcStreamNonBlocking)` | 与默认流互不干扰，各自独立调度 |

"阻塞"一词容易引起歧义——它并不意味着流本身是同步的，而仅描述该流是否参与默认流的全局屏障行为。两种流的销毁方式相同，均使用 `hggcStreamDestroy()`。

**传统默认流**：当未显式指定流时（如 `kernel<<<grid, block>>>(...)` 或阻塞式 `hggcMemcpy()`），HGGC 会将操作提交到传统默认流（NULL 流，流 ID 为 0）。该流在进程内所有主机线程间共享，并具有**全局屏障语义**：任何提交到默认流的操作都会隐式等待所有阻塞流中先前的操作完成，同时阻塞流中后续提交的操作也会等待默认流上的操作完成。

下面的示例展示了这一串行化效应：

```cpp
hggcStream_t work_stream_a, work_stream_b;
hggcStreamCreate(&work_stream_a); // 默认为阻塞流
hggcStreamCreate(&work_stream_b);
kernel1<<<grid, block, 0, work_stream_a>>>(...);
kernel2<<<grid, block>>>(...); // 提交到默认流
kernel3<<<grid, block, 0, work_stream_b>>>(...);
hggcDeviceSynchronize();
```

由于 kernel2 使用默认流，它会等待 kernel1（阻塞流上的操作）完成；而 kernel3 又必须等待默认流上的 kernel2 完成。**最终三个核函数被迫串行执行，尽管它们之间并无数据依赖。**

将 work_stream_a 和 work_stream_b 改为非阻塞流即可消除这种不必要的序列化——三个核函数可自由并发。代价是开发者需要通过事件或显式同步 API 来保证正确的执行顺序：

```cpp
hggcStream_t work_stream_a, work_stream_b;
hggcStreamCreateWithFlags(&work_stream_a, hggcStreamNonBlocking);
hggcStreamCreateWithFlags(&work_stream_b, hggcStreamNonBlocking);
kernel1<<<grid, block, 0, work_stream_a>>>(...);
kernel2<<<grid, block>>>(...);
kernel3<<<grid, block, 0, work_stream_b>>>(...);
hggcDeviceSynchronize();
```

**每线程默认流**：传统默认流是全局共享的，当多线程程序的不同主机线程同时向默认流提交工作时，会因序列化而降低并发度。HGGC 提供了"每线程默认流"模式来解决这一问题：在此模式下，每个主机线程拥有各自独立的默认流，线程之间不再因共享默认流而相互阻塞。

启用方式（二选一）：

- 编译选项：`hgcc --default-stream per-thread`
- 预处理器宏：在包含 HGGC 头文件之前定义 `HGGC_API_PER_THREAD_DEFAULT_STREAM`

启用后，"传统默认流示例"将表现出与"非阻塞流示例"相同的同步行为。

**HGGC 流顺序**：考虑异步操作在流中的顺序语义很重要。最重要的是，**HGGC 流是有序流（ordered stream）**：流中操作的执行顺序与这些操作入队的顺序相同，流中的操作不能跳过其他操作。内存操作（如复制）由运行时跟踪，并且始终会在顺序上下一个操作之前完成，以允许依赖的核函数安全访问正在传输的数据。（在某些特殊情况下这些语义可能会放宽以实现性能优化，例如编程式依赖核函数启动场景。）

比赛关联：VLM 推理服务化时，图像编码（ViT）与文本 prefill 可用两条非阻塞流并发；流式输出时用事件串联逐 token 解码与 D2H 拷贝。切记避免误用默认流造成隐式串行——这是吞吐量损失最常见的隐形来源。

### 2.3.3 来自流的回调函数

HGGC 提供了一种机制，可以从流内启动主机上的函数。目前有两个函数可用于此目的：**`hggcLaunchHostFunc()`** 和 **`hggcAddCallback()`**。但是 `hggcAddCallback()` 计划弃用，因此应用程序应该使用 `hggcLaunchHostFunc()`。

#### 2.3.3.1 使用 hggcLaunchHostFunc()

`hggcLaunchHostFunc()` 函数的签名如下：

```cpp
hggcError_t hggcLaunchHostFunc(hggcStream_t stream, void (*func)(void *), void *data);
```

其中：

- `stream`：要将回调函数启动到的流
- `func`：要启动的回调函数
- `data`：要传递给回调函数的数据指针

主机函数本身是一个简单的 C 函数，签名为：

```cpp
void hostFunction(void *data);
```

其中 `data` 参数指向用户定义的数据结构，函数可以解释它。

**注意事项：主机函数不能调用任何 HGGC API。**

在统一内存场景下，主机函数的执行遵循以下语义保证：

| 保证项 | 含义 | 实际影响 |
|---|---|---|
| 函数执行期间流视为空闲 | 运行时不会在函数执行时向同一流提交新的设备工作 | 函数内可安全访问绑定到该流的托管内存 |
| 函数启动等效于一次事件记录 | 函数开始执行时，所有在此之前"加入"该流的其他流均已完成 | 可依赖函数启动点作为跨流同步屏障 |
| 设备工作需等待所有先前主机函数和流回调完成后才激活流 | 即使新的设备工作被排入其他流，只要通过事件排序在主机函数和流回调之后，流仍不会进入活动状态 | 函数执行期间全局附加内存仍可安全使用 |
| 函数完成本身不激活流 | 如果后续没有设备工作跟随，流将保持空闲；如果在连续的主机函数或流回调之间没有设备工作，流将保持空闲 | 可在流末尾通过主机函数发出同步信号 |

#### 2.3.3.2 使用 hggcStreamAddCallback()

> **NOTE**：`hggcStreamAddCallback()` 函数计划弃用和移除，在此讨论是为了完整起见，因为它可能仍出现在现有代码中。应用程序应该使用或切换到使用 `hggcLaunchHostFunc()`。

`hggcStreamAddCallback()` 函数的签名如下：

```cpp
hggcError_t hggcStreamAddCallback(hggcStream_t stream, hggcStreamCallback_t callback,
                                  void* userData, unsigned int flags);
```

其中：

- `stream`：要将回调函数启动到的流
- `callback`：要启动的回调函数
- `userData`：要传递给回调函数的数据指针
- `flags`：目前，此参数必须为 0 以保持未来兼容性

回调函数的签名与 `hggcLaunchHostFunc()` 的情况略有不同。在这种情况下，回调函数是一个 C 函数，签名为：

```cpp
void callbackFunction(hggcStream_t stream, hggcError_t status, void *userData);
```

函数现在接收：

- `stream`：从中启动回调函数的流句柄
- `status`：触发回调的流操作的状态
- `userData`：传递给回调函数的数据指针

特别地，`status` 参数将包含流的当前错误状态（可能由先前的操作设置）。与 `hggcLaunchHostFunc()` 的情况类似，在主机函数完成之前，流不会处于活动状态并推进到任务，并且**不能从回调函数内调用任何 HGGC 函数**。

#### 2.3.3.3 异步错误处理

在 HGGC 流中，错误可能来自流中的任何操作，包括核函数启动和内存传输。这些错误可能在运行时不会传播回开发者，直到流被同步（例如，通过等待事件或调用 `hggcStreamSynchronize()`）。有两种方法可以发现流中可能发生的错误：

- **`hggcGetLastError()`** —— 返回并**清除**当前上下文中任何流中遇到的最后一个错误。如果在两次调用之间没有发生其他错误，立即第二次调用 `hggcGetLastError()` 将返回 `hggcSuccess`。
- **`hggcPeekAtLastError()`** —— 返回当前上下文中的最后一个错误，但**不会清除**它。

这两个函数都返回一个类型为 `hggcError_t` 的错误值。可以使用函数 **`hggcGetErrorName()`** 和 **`hggcGetErrorString()`** 生成错误的人类可读名称。

清单 1. 使用 `hggcGetLastError()` 和 `hggcPeekAtLastError()` 的示例：

```cpp
// 一些工作在流中发生
hggcStreamSynchronize(stream);
// 查看最后一个错误但不清除它
hggcError_t err = hggcPeekAtLastError();
if (err != hggcSuccess) {
    printf("Error with name: %s\n", hggcGetErrorName(err));
    printf("Error description: %s\n", hggcGetErrorString(err));
}
// 查看最后一个错误并清除它
hggcError_t err2 = hggcGetLastError();
if (err2 != hggcSuccess) {
    printf("Error with name: %s\n", hggcGetErrorName(err2));
    printf("Error description: %s\n", hggcGetErrorString(err2));
}
if (err2 != err) {
    printf("As expected, hggcPeekAtLastError() did not clear the error\n");
}
// 再次检查
hggcError_t err3 = hggcGetLastError();
if (err3 == hggcSuccess) {
    printf("As expected, hggcGetLastError() cleared the error\n");
}
```

> **NOTE**：当在同步时出现错误时，特别是在有许多操作的流中，通常很难精确定位错误可能发生在流中的哪个位置。调试这种情况时，一个有用的技巧是设置环境变量 **`HGGC_LAUNCH_BLOCKING=1`**，然后运行应用程序。此环境变量的作用是在**每个单个核函数启动后同步**，可以帮助追踪是哪个核函数或传输导致了错误。同步可能很昂贵；设置此环境变量后，应用程序可能会运行得慢很多。

### 2.3.4 高级流管理与核函数配置

本节介绍更高级的 HGGC API 和功能。这些主题涉及的技术或功能通常不需要修改 HGGC 核函数（Kernel），但仍能从宿主（Host）端影响应用程序层面的行为，包括 PPU 任务执行、性能以及 CPU 端的性能。

#### 2.3.4.1 hggcLaunchKernelEx

当三尖括号语法在 HGGC 的早期版本中引入时，核函数的核函数配置仅有四个可编程参数：

1. 线程块维度（Thread block dimensions）
2. 网格维度（Grid dimensions）
3. 动态共享内存（可选，未指定则为 0）
4. 流（Stream，未指定则使用默认流）

某些 HGGC 功能可以受益于核函数启动时提供的额外属性和提示。**`hggcLaunchKernelEx`** 允许程序通过 **`hggcLaunchConfig_t`** 结构体设置上述执行配置参数。此外，`hggcLaunchConfig_t` 结构体还允许程序传入零个或多个 **`hggcLaunchAttributes`**，以控制或建议核函数启动的其他参数。

#### 2.3.4.2 流（Streams）与事件（Events）进阶

- 默认情况下，提交给特定 HGGC 流的操作是序列化的：前一个操作未完成前，下一个操作无法开始执行。拥有多个 HGGC 流是实现并发执行的一种方式；另一种方式是使用 HGGC 图（Graphs）。这两种方法也可以结合使用。
- 在特定情况下，提交到不同 HGGC 流的任务可以并发执行，例如：不存在事件依赖关系、不存在隐式同步、拥有充足的资源等。
- 除非是"非阻塞（non-blocking）"HGGC 流，否则如果两个独立 HGGC 流的操作之间插入了对 NULL 流的 HGGC 操作，它们将无法并发运行。非阻塞流通过运行时 API **`hggcStreamCreateWithFlags()`** 并设置 **`hggcStreamNonBlocking`** 标志创建。**为了提高 PPU 任务并发执行的可能性，建议用户创建非阻塞 HGGC 流。**
- 同时建议用户为解决问题**选择粒度最细的同步选项**。例如：如果需求是让 CPU 等待（阻塞）特定 HGGC 流上的所有任务完成，使用 `hggcStreamSynchronize()` 优于 `hggcDeviceSynchronize()`；如果需求是让 CPU 在不阻塞的情况下等待，那么在轮询循环中使用 `hggcStreamQuery()` 并检查其返回值可能更合适。类似的同步效果也可以通过 HGGC 事件实现：在流上记录一个事件，并调用 `hggcEventSynchronize()` 以阻塞方式等待该事件所捕获的任务完成；调用 `hggcEventQuery()` 并检查返回值（如在轮询循环中）则是一种非阻塞的替代方案。

**表 1：宿主显式同步选项总结**

| | 等待特定流 | 等待特定事件 | 等待设备上所有任务 |
|---|---|---|---|
| 非阻塞（需配合轮询循环） | `hggcStreamQuery()` | `hggcEventQuery()` | 不适用 |
| 阻塞 | `hggcStreamSynchronize()` | `hggcEventSynchronize()` | `hggcDeviceSynchronize()` |

- 对于 HGGC 流之间的同步（即表达依赖关系），建议使用**非计时类（non-timing）的 HGGC 事件**。开发者可以调用 **`hggcStreamWaitEvent()`** 来强制特定流上后续提交的操作等待先前记录的事件（例如在另一个流上的事件）完成。注意，对于任何等待或查询事件的 HGGC API，开发者有责任确保已调用 `hggcEventRecord` API，因为**未记录的事件总是会返回成功**。
- HGGC 事件默认携带计时信息，可用于 `hggcEventElapsedTime()` API 调用。然而，仅用于跨流表达依赖关系的 HGGC 事件不需要计时信息。对于此类情况，**建议在创建事件时禁用计时功能以提升性能**，这可以通过使用 **`hggcEventCreateWithFlags()`** API 并设置 **`hggcEventDisableTiming`** 标志来实现。

##### 2.3.4.2.1 流优先级

PPU 采用**基于队列的派发模型**：每条 HGGC 流维护一条独立的任务队列，调度器在执行单元出现空闲时，从所有就绪流中挑选下一个待派发的任务。流优先级正是作用于这一任务挑选环节——它向调度器提供一个排序提示，用于在多条流的就绪任务之间打破平局，但并不改变 PPU 的派发与执行机制本身。

基于这一调度模型，流优先级具有以下行为约束：

- **仅在派发时刻生效**：当调度器需要选取下一个待派发任务时，高优先级流中处于就绪状态的任务优先于低优先级流中的任务进入执行单元。
- **不具备抢占语义**：任务一旦被派发到执行单元上运行，将持续执行至完成；即便此后有更高优先级的任务进入就绪队列，也不会中断当前正在执行的工作。
- **运行期不重估**：PPU 在任务执行过程中不会重新审视各队列的状态。运行中调用 API 提升某条流的优先级，对已在执行的任务没有任何影响，仅会改变后续派发的选择顺序。
- **属于调度提示而非时序契约**：优先级表达的是"倾向"而非"承诺"，不应作为构造任务依赖的手段；如需严格的执行顺序，应通过 HGGC 事件、`hggcStreamWaitEvent()` 等机制显式建立依赖。

在 API 层面，流的优先级在创建时通过 **`hggcStreamCreateWithPriority()`** 传入一个整数值指定，其有效区间需先通过 **`hggcDeviceGetStreamPriorityRange()`** 查询。该函数以 **[最低优先级, 最高优先级]** 的顺序返回端点，**整数值越小代表优先级越高**；不同设备所支持的优先级层级数可能不同，超出范围的取值会被钳制到端点。

下例先在当前设备上获取允许的优先级区间，再据此创建一对非阻塞流——其一承载延迟敏感的关键路径任务，其二承载可被延后的吞吐型后台任务：

```cpp
// 查询当前设备支持的流优先级区间，约定：数值越小，优先级越高
int lowestPrio = 0;
int highestPrio = 0;
hggcDeviceGetStreamPriorityRange(&lowestPrio, &highestPrio);
// 关键路径流：使用最高优先级，承载对延迟敏感的任务
hggcStream_t criticalStream;
hggcStreamCreateWithPriority(&criticalStream,
    hggcStreamNonBlocking,
    highestPrio);
// 后台流：使用最低优先级，承载可被延后的吞吐型任务
hggcStream_t backgroundStream;
hggcStreamCreateWithPriority(&backgroundStream,
    hggcStreamNonBlocking,
    lowestPrio);
```

##### 2.3.4.2.2 显式同步

显式同步 API 的详细说明（含同步范围、阻塞行为和典型用途对照表）参见第 2.3.2.3 节"流/事件的同步策略"。

##### 2.3.4.2.3 隐式同步

如果主机线程在两个不同流的命令之间执行了以下任何操作，则它们无法并发运行：

- 页锁定（page-locked）主机内存分配
- 设备内存分配
- 设备内存设置（memory set）
- 同一设备内存中两个地址之间的内存拷贝
- 任何发送到 NULL 流的 HGGC 命令
- L1/共享内存配置的切换

需要进行依赖检查的操作包括：正在检查的启动命令所在流中的任何其他命令，以及对该流的任何 `hggcStreamQuery()` 调用。因此，应用程序应遵循以下准则以提高并发核函数执行的可能性：

- 所有独立操作应在依赖操作之前提交；
- 任何形式的同步都应尽可能推迟。

#### 2.3.4.3 环境变量

HGGC 提供了各种环境变量（请参阅"环境变量"章节），这些变量会影响执行和性能。如果未明确设置，HGGC 会使用合理的默认值，但在某些情况下，例如为了调试目的或为了获得更好的性能，可能需要进行特殊处理。

| 环境变量 | 作用 | 备注 |
|---|---|---|
| `HGGC_DEVICE_MAX_CONNECTIONS` | 增加其值可减少来自不同 HGGC 流的独立任务因虚假依赖而被序列化的可能性（当使用相同的底层资源时，可能会引入此类虚假依赖） | 建议先使用默认值，仅在遇到性能问题时（如无法归因于可用 CU 资源不足的跨流独立任务的意外序列化）才探讨该变量的影响。在使用 MPS 的情况下，该环境变量具有不同（更低）的默认值 |
| `HGGC_MODULE_LOADING` | 设置为 `EAGER` 可将模块加载引起的所有开销转移到应用程序的初始化阶段，从而避开其关键执行阶段 | 当前的默认模式是**延迟模块加载**。在默认模式下，通过在应用程序的初始化阶段添加各种核函数的"预热"调用，可以达到与立即模块加载类似的效果，从而强制模块更早地加载 |
| `HGGC_LAUNCH_BLOCKING=1` | 在每个单个核函数启动后同步，帮助追踪是哪个核函数或传输导致了错误 | 同步很昂贵，设置后应用可能运行得慢很多（见 2.3.3.3） |

建议在启动应用程序之前将环境变量设置为新值；在应用程序内部设置它们可能不会产生任何效果。

比赛关联：`HGGC_MODULE_LOADING=EAGER` 或预热调用直接关联 TTFT 指标——把模块加载开销移出首 token 的关键路径；`HGGC_DEVICE_MAX_CONNECTIONS` 是多流并发调优的排查项。

### 2.3.5 从流到图——HGGC 图简介

- HGGC 流允许程序指定操作、核函数或内存复制的序列操作。使用多个流和通过 `hggcStreamWaitEvent` 的跨流依赖，应用程序可以指定一个完整的操作有向无环图（DAG）。
- 某些应用程序可能有一系列或 DAG 操作，需要在执行过程中多次运行。对于这种情况，HGGC 提供了一个称为 **HGGC 图** 的功能。
- 捕获或创建图可以帮助**减少从主机线程重复调用相同 API 链的延迟和 CPU 开销**：指定图操作的 API 可以调用一次，然后生成的图可以执行多次。

HGGC 图的工作方式：

1. **图被应用程序捕获**：此步骤在第一次执行图时完成一次。也可以使用 HGGC 图 API 手动组合图。
2. **图被实例化**：此步骤在图被捕获后完成一次。此步骤可以设置执行图所需的所有各种运行时结构，以尽可能快地启动其组件。
3. **预实例化的图根据需要执行多次**：由于执行图操作所需的所有运行时结构已就位，图执行的 CPU 开销被最小化。

清单 2. 使用 HGGC 图捕获、实例化和执行简单线性图的阶段：

```cpp
// PPU 推理引擎：将推理流水线捕获为图以减少启动开销
#define INPUT_SIZE (224 * 224 * 3)
__global__ void normalize_kernel(float *dst, const float *src, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) dst[idx] = src[idx] / 255.0f;
}

bool graphCaptured = false;
hggcGraph_t inferenceGraph;
hggcGraphExec_t inferenceExec;
for (int req = 0; req < totalRequests; req++) {
    if (!graphCaptured) {
        // 首次请求：捕获推理流水线为图
        hggcStreamBeginCapture(inferStream, hggcStreamCaptureModeGlobal);
        // 阶段1：输入归一化
        normalize_kernel<<<(INPUT_SIZE+255)/256, 256, 0, inferStream>>>(
            d_normalized, d_rawInput, INPUT_SIZE);
        // 阶段2：推理计算（各层核函数已在别处定义）
        layer1_kernel<<<grid1, block1, 0, inferStream>>>(d_normalized, d_hidden1);
        layer2_kernel<<<grid2, block2, 0, inferStream>>>(d_hidden1, d_hidden2);
        output_kernel<<<grid3, block3, 0, inferStream>>>(d_hidden2, d_output);
        hggcStreamEndCapture(inferStream, &inferenceGraph);
        hggcGraphInstantiate(&inferenceExec, inferenceGraph, NULL, NULL, 0);
        graphCaptured = true;
    }
    // 后续请求：直接启动预实例化的图
    hggcGraphLaunch(inferenceExec, inferStream);
    hggcStreamSynchronize(inferStream);
}
```

相关 API：`hggcStreamBeginCapture`（模式如 `hggcStreamCaptureModeGlobal`）、`hggcStreamEndCapture`、`hggcGraphInstantiate`、`hggcGraphLaunch`；类型 `hggcGraph_t`、`hggcGraphExec_t`。

比赛关联：这是**降低 TTFT 与逐 token 解码 CPU 开销最有力的机制**——LLM 每层 kernel 链固定，用流捕获把整个 decode step 固化为图，后续每次 `hggcGraphLaunch` 一次调用即可，极大减少每 token 的 host 端启动开销。

### 2.3.6 异步编程小结

本节的关键点：

- 异步 API 允许我们表达任务的并发执行，提供表达各种操作重叠的方式。实际达到的并发度取决于可用的硬件资源和计算能力。
- HGGC 中异步执行的关键抽象是**流、事件和回调函数**。
- 同步可以在事件、流和设备级别进行。
- 默认流是阻塞流，与所有其他阻塞流同步，但不与非阻塞流同步。
- 可以通过使用 `--default-stream per-thread` 编译器选项或 `HGGC_API_PER_THREAD_DEFAULT_STREAM` 预处理器宏的每线程默认流来避免默认流行为。
- 流可以创建时带有不同的优先级，这是对运行时的提示，对于内存传输可能不会遵循。
- HGGC 提供 API 函数来减少或重叠核函数启动和内存传输的开销，如 **HGGC 图、批量内存传输和编程式依赖核函数启动**。

---

## 2.4 统一和系统内存

PPU 异构系统中存在多层物理内存——CPU 侧的主机 DRAM 和每个 PPU 设备自带的显存。数据在哪一侧的内存中，直接决定了访问延迟和带宽。前文介绍的显式内存管理给予了开发者完整的控制权，但也带来了分配、拷贝、同步等大量样板代码。为此 HGGC 提供了统一内存和系统内存等自动化数据放置与迁移机制，力求在编程便利性与性能之间取得平衡。

统一内存的具体行为取决于操作系统版本、HGGC 驱动版本以及 PPU 硬件能力。**我们目前只支持有限统一内存。**

### 2.4.1 统一虚拟地址空间

在单个操作系统进程中，**单个虚拟地址空间**用于所有主机内存和系统中所有 PPU 上的所有全局内存。主机和所有设备上的所有内存分配都位于这个虚拟地址空间中。无论分配是通过 HGGC API（如 `hggcMalloc`、`hggcMallocHost`）还是通过系统分配 API（如 `new`、`malloc`、`mmap`）进行的，都是如此。CPU 和每个 PPU 在统一虚拟地址空间中有唯一的范围。

统一虚拟地址空间为开发者带来两个关键便利：

1. **指针归属查询**：对于任意指针，调用 **`hggcPointerGetAttributes()`** 即可判断其背后的物理内存归属于 CPU 还是某个 PPU，无需开发者手动跟踪分配来源。
2. **自动推断拷贝方向**：在调用 `hggcMemcpy*()` 系列函数时，将 `hggcMemcpyKind` 设为 **`hggcMemcpyDefault`** 即可让运行时根据源和目标指针所在的地址范围自动选择正确的传输路径，省去显式指定方向的步骤。

### 2.4.2 统一内存

统一内存是一种 HGGC 内存功能，允许从在 CPU 或 PPU 上运行的代码访问称为**托管内存（managed memory）**的内存分配。统一内存在 HGGC 支持的所有系统上都可用。

在某些系统上，托管内存必须显式分配。在 HGGC 中可以通过几种不同的方式显式分配托管内存：

- HGGC API **`hggcMallocManaged`**
- HGGC API **`hggcMallocFromPoolAsync`**，其中池的 `allocType` 设置为 **`hggcMemAllocationTypeManaged`**
- 具有 **`__managed__`** 说明符的全局变量（参见"内存空间说明符"）

#### 2.4.2.1 统一内存模式

统一内存的功能和行为因操作系统、Linux 上的内核版本、PPU 硬件和 PPU-CPU 互连而异。可以使用 `hggcDeviceGetAttribute` 查询几个属性来确定可用的统一内存形式：

| 设备属性 | 取值含义 |
|---|---|
| `hggcDevAttrConcurrentManagedAccess` | 1 表示完整统一内存支持，0 表示有限支持 |
| `hggcDevAttrPageableMemoryAccess` | 1 表示所有系统内存都是完全支持的统一内存，0 表示只有显式分配为托管内存的才是完全支持的统一内存 |
| `hggcDevAttrPageableMemoryAccessUsesHostPageTables` | 指示 CPU/PPU 一致性的机制：1 是硬件，0 是软件 |

#### 2.4.2.2 完整统一内存功能支持

- 大多数 Linux 系统具有完整的统一内存支持。如果设备属性 `hggcDevAttrPageableMemoryAccess` 为 1，则**所有系统内存**（无论是通过 HGGC API 还是系统 API 分配）都作为具有完全功能支持的统一内存运行，包括使用 `mmap` 创建的文件支持的内存分配。
- 如果 `hggcDevAttrPageableMemoryAccess` 为 0，则只有通过 HGGC 分配为托管内存的内存才作为统一内存运行。通过系统 API 分配的内存不是托管的，不一定可以从 PPU 核函数访问。

对于具有完全支持的统一分配：

| 特征 | 说明 |
|---|---|
| 首次访问放置 | 托管内存通常分配在首次访问它的处理器的内存空间中 |
| 按需迁移 | 当托管内存被当前驻留所在处理器以外的处理器使用时，通常会发生迁移 |
| 迁移粒度 | 托管内存以内存页（软件一致性）或缓存行（硬件一致性）的粒度迁移或访问 |
| 超额订阅 | 允许超额订阅：应用程序可以分配比 PPU 物理可用更多的托管内存 |

分配和迁移行为可能与上述有所不同。这可以通过程序员使用"提示和预取"来影响。

#### 2.4.2.3 有限统一内存支持

有限模式下，统一内存的行为受以下约束：

| 约束 | 说明 |
|---|---|
| 初始放置 | 托管内存始终首先分配在 CPU 物理内存中 |
| 迁移粒度 | 以大于虚拟内存页的块为单位批量迁移 |
| 迁移时机 | PPU 核函数启动时整体迁入 PPU，PPU 同步完成后整体迁回 CPU |
| 独占访问 | PPU 执行期间 CPU 不得访问托管内存 |
| 无超额订阅 | 托管内存总量不得超过 PPU 物理显存 |
| 显式分配 | 仅通过 HGGC API 显式分配为托管内存的区域才具有统一语义 |

#### 2.4.2.4 内存建议和预取

程序员可以向管理统一内存的驱动程序提供提示，以帮助其最大化应用程序性能：

- HGGC API **`hggcMemAdvise`** 允许程序员指定影响分配放置位置以及从另一个设备访问时内存是否迁移的属性。
- **`hggcMemPrefetchAsync`** 允许程序员建议开始将特定分配异步迁移到不同位置。常见用法是**在核函数启动之前启动核函数将使用的数据传输**——这允许在其他 PPU 核函数执行时进行数据复制。

比赛关联：比赛平台当前只支持**有限统一内存**——托管内存在 kernel 启动时整体迁入、同步后整体迁回，PPU 执行期间 CPU 不得访问。这意味着 VLM 推理热路径（逐 token 解码）绝不应依赖托管内存隐式迁移（每次 kernel 启动都触发整批搬迁会严重拉高延迟），权重和 KV cache 应用 `hggcMalloc` 显式驻留显存；`hggcMemPrefetchAsync` 可用于预取下一批输入。

### 2.4.3 页锁定主机内存

- 在介绍性代码示例中，`hggcMallocHost` 用于在 CPU 上分配内存。这会在主机上分配**页锁定内存（也称为固定内存，pinned memory）**。通过传统分配机制（如 `malloc`、`new` 或 `mmap`）进行的主机分配不是页锁定的，这意味着它们可能被操作系统交换到磁盘或物理重新定位。
- **页锁定主机内存是 CPU 和 PPU 之间的异步复制所必需的**，也提高了同步复制的性能。页锁定内存可以映射到 PPU 以便从 PPU 核函数直接访问。

HGGC 运行时提供 API 来分配页锁定主机内存或对现有分配进行页锁定：

| API | 作用 |
|---|---|
| `hggcMallocHost` | 分配页锁定主机内存 |
| `hggcHostAlloc` | 默认为与 `hggcMallocHost` 相同的行为，但也接受标志来指定其他内存参数 |
| `hggcFreeHost` | 释放使用 `hggcMallocHost` 或 `hggcHostAlloc` 分配的内存 |
| `hggcHostRegister` | 对通过 HGGC API 外部分配的范围进行页锁定，如使用 `malloc` 或 `mmap` |

`hggcHostRegister` 使由第三方库或其他开发人员控制之外的代码分配的主机内存能够被页锁定，以便用于异步复制或映射。

> **NOTE**：页锁定主机内存可用于系统中所有 PPU 的异步复制和映射内存。

#### 2.4.3.1 映射内存

以下代码示例将说明数组复制核函数直接操作映射的主机内存：

```cpp
__global__ void copyKernel(float* a, float* b) {
    int idx = threadIdx.x + blockDim.x * blockIdx.x;
    a[idx] = b[idx];
}
```

虽然映射内存在某些情况下可能很有用（某些不会被复制到 PPU 的数据需要从核函数访问），但**在核函数中访问映射内存需要通过 CPU-PPU 互连（PCIe 或 Icnlink C2C）进行事务处理**。与访问设备内存相比，这些操作具有更高的延迟和更低的带宽。对于大多数核函数的内存需求，**映射内存不应被视为统一内存或显式内存管理的高性能替代方案**。

##### 2.4.3.1.1 hggcMallocHost 和 hggcHostAlloc

使用 `hggcMallocHost` 或 `hggcHostAlloc` 分配的主机内存会**自动映射**。这些 API 返回的指针可以直接在核函数代码中使用以访问主机上的内存。主机内存通过 CPU-PPU 互连访问。

```cpp
// hggcMallocHost
void usingMallocHost() {
    float* a = nullptr;
    float* b = nullptr;
    HGGC_CHECK(hggcMallocHost(&a, vLen * sizeof(float)));
    HGGC_CHECK(hggcMallocHost(&b, vLen * sizeof(float)));
    initVector(b, vLen);
    memset(a, 0, vLen * sizeof(float));
    int threads = 256;
    int blocks = vLen / threads;
    copyKernel<<<blocks, threads>>>(a, b);
    HGGC_CHECK(hggcGetLastError());
    HGGC_CHECK(hggcDeviceSynchronize());
    printf("Using hggcMallocHost: ");
    checkAnswer(a, b);
}

// hggcHostAlloc
void usinghggcHostAlloc() {
    float* a = nullptr;
    float* b = nullptr;
    HGGC_CHECK(hggcHostAlloc(&a, vLen * sizeof(float), hggcHostAllocMapped));
    HGGC_CHECK(hggcHostAlloc(&b, vLen * sizeof(float), hggcHostAllocMapped));
    initVector(b, vLen);
    memset(a, 0, vLen * sizeof(float));
    int threads = 256;
    int blocks = vLen / threads;
    copyKernel<<<blocks, threads>>>(a, b);
    HGGC_CHECK(hggcGetLastError());
    HGGC_CHECK(hggcDeviceSynchronize());
    printf("Using hggcHostAlloc: ");
    checkAnswer(a, b);
}
```

（注：`hggcHostAlloc` 使用标志 `hggcHostAllocMapped`。）

##### 2.4.3.1.2 hggcHostRegister

系统分配器进行的分配可以使用 `hggcHostRegister` 映射以便直接从 PPU 核函数访问。然而，与使用 HGGC API 创建的内存不同，**内存不能使用主机指针从核函数访问**。必须使用 **`hggcHostGetDevicePointer()`** 获得设备内存区域中的指针，并且必须使用该指针进行核函数代码中的访问。

```cpp
void usingRegister() {
    float* a = nullptr;
    float* b = nullptr;
    float* devA = nullptr;
    float* devB = nullptr;
    a = (float*)malloc(vLen * sizeof(float));
    b = (float*)malloc(vLen * sizeof(float));
    HGGC_CHECK(hggcHostRegister(a, vLen * sizeof(float), 0));
    HGGC_CHECK(hggcHostRegister(b, vLen * sizeof(float), 0));
    HGGC_CHECK(hggcHostGetDevicePointer((void**)&devA, (void*)a, 0));
    HGGC_CHECK(hggcHostGetDevicePointer((void**)&devB, (void*)b, 0));
    initVector(b, vLen);
    memset(a, 0, vLen * sizeof(float));
    int threads = 256;
    int blocks = vLen / threads;
    copyKernel<<<blocks, threads>>>(devA, devB);
    HGGC_CHECK(hggcGetLastError());
    HGGC_CHECK(hggcDeviceSynchronize());
    printf("Using hggcHostRegister: ");
    checkAnswer(a, b);
}
```

##### 2.4.3.1.3 比较统一内存和映射内存

- 映射内存使 CPU 内存可从 PPU 访问，但**不保证所有类型的访问（例如原子操作）在所有系统上都受支持**。统一内存保证所有访问类型都受支持。
- 映射内存保留在 CPU 内存中，这意味着所有 PPU 访问都必须通过 CPU 和 PPU 之间的连接（PCIe 或 Icnlink）进行。通过这些链接访问的延迟明显高于访问 PPU 内存的延迟，可用的总带宽也更低。因此，对所有核函数内存访问使用映射内存不太可能充分利用 PPU 计算资源。
- 统一内存最常迁移到访问它的处理器的物理内存。第一次迁移后，核函数对相同内存页或缓存行的重复访问可以利用完整的 PPU 内存带宽。

> **NOTE**：映射内存在早期文档中曾被称为"零拷贝内存"（Zero-Copy Memory）。自 HGGC 引入统一虚拟地址空间后，内存映射功能默认启用，不再需要通过 `hggcSetDeviceFlags` 显式设置 `hggcDeviceMapHost` 标志。

PPU 对映射到主机的内存提供以下访问原子性保证：

| 访问宽度 | 对齐要求 | 可见性保证 |
|---|---|---|
| 1 / 2 / 4 / 8 / 16 字节 | 自然对齐 | 对主机及其他设备表现为不可分割的单次访问 |

需要注意的是，原子操作（如 `atomicAdd`）在部分互连拓扑下可能被硬件拆分为独立的加载与存储操作；拆分后的子操作同样要求上（述对齐要求）（原文此处截断，需查原文确认）。

### 2.4.4 总结

在 Linux 平台上，必须使用 HGGC 分配托管内存：

- `hggcMallocManaged`，或
- `hggcMallocFromPoolAsync`，其中池的 `allocType=hggcMemAllocationTypeManaged`
- 具有 `__managed__` 说明符的全局变量

---

## 2.5 hgcc：HGGC 编译器

hgcc 编译器是平头哥提供的用于编译 HGGC C/C++ 的工具链。该工具链是 T-Head SAIL Toolkit 的一部分，包含多个工具，包括编译器、链接器以及 HGbin 汇编器。顶层的 hgcc 工具协调编译过程，在编译的每个阶段调用适当的工具。

- hgcc 驱动**离线编译** HGGC 代码，与之相对的是由 HGGC 运行时编译器 **hgrtc（HG Runtime Compilation）** 驱动的**在线或即时（JIT）编译**。
- 本章涵盖构建应用程序所需的 hgcc 最常用用途和详细信息；hgcc 的全面覆盖可以在 hgcc 文档中找到。

### 2.5.1 HGGC 源文件和头文件

使用 hgcc 编译的源文件可能包含主机（host）代码（在 CPU 上执行）和设备（device）代码（在 PPU 上执行）的组合。hgcc 接受常见的 C/C++ 源文件扩展名 `.c`、`.cpp`、`.cc`、`.cxx` 表示纯主机代码，而 **`.hg` 扩展名表示包含设备代码或主机和设备代码混合的文件**。

| 文件扩展名 | 描述 | 内容 |
|---|---|---|
| `.c` | C 源文件 | 纯主机代码 |
| `.cpp`, `.cxx` | C++ 源文件 | 纯主机代码 |
| `.h`, `.hpp`, `.hh`, `.hxx` | C/C++ 头文件 | 设备代码、主机代码、主/设备代码混合 |
| `.hg` | HGGC 源文件 | 设备代码、主机代码、主/设备代码混合 |

### 2.5.2 hgcc 编译工作流程

- 在初始阶段，hgcc 将设备代码与主机代码分离，并分别将它们的编译调度到 PPU device 编译器和主机编译器。
- **host 端编译器支持情况**：gcc host compiler 的版本支持范围在 **[5.5 - 14.2]**；clang host compiler 的支持范围在 **[clang 9 - clang 18]**。
- 只包含主机代码的文件可以使用 hgcc 或直接使用主机编译器构建。生成的目标文件可以在链接时与包含 PPU 代码的目标文件结合。
- T-Head SAIL 编译器将 C/C++ 设备代码编译为 **BC 二进制中间代码**。用户针对用户指定的 **ppu-arch** 编译对应版本的 PPU **hgbin** 代码。可以将多个 bc 中间代码和 hgbin 目标嵌入到单个二进制 **hgfatbin** 容器中的应用程序或库中，以便单个二进制文件可以支持多个 PPU 硬件 arch ISA。上述工具的调用和协调由 hgcc 自动完成。
- **`-v` 选项**可用于显示完整的编译工作流程和工具调用。**`-keep` 选项**可用于保存当前目录中或 `--keep-dir` 指定目录中编译过程中生成的中间文件。

示例 HGGC 源文件 `example.hg` 的编译工作流程：

```cpp
// ----- example.hg -----
#include <stdio.h>
__global__ void kernel() {
    printf("Hello from kernel\n");
}
void kernel_launcher() {
    kernel<<<1, 1>>>();
    hggcDeviceSynchronize();
}
int main() {
    kernel_launcher();
    return 0;
}
```

（原文此处附有"hgcc 的基础编译流程"图。）

### 2.5.3 hgcc 基本用法

使用 hgcc 编译 HGGC 源文件的基本命令是：

```bash
hgcc <source_file>.hg -o <output_file>
```

hgcc 接受用于指定包含目录 `-I <path>` 和库路径 `-L <path>`、链接其他库 `-l<library>` 以及定义宏 `-D<macro>=<value>` 的通用编译器标志：

```bash
hgcc example.hg -I path_to_include/ -L path_to_library/ -lacblas -o <output_file>
```

#### 2.5.3.1 hgcc 中间表示和 hgbin 生成

hgcc 通过使用 **`--gpu-architecture=<value>`** 来指定要编译的 PPU 编译产物：

| 选项 | 产物 |
|---|---|
| `--gpu-architecture=ppu_10` | 只编译 arch ppu001 系列编译产物 |
| `--gpu-architecture=ppu_15` | 只编译 arch ppu0015 系列编译产物 |
| `--gpu-architecture=ppu_10 --gpu-architecture=ppu_15` | 编译 arch ppu001 和 arch ppu0015 全系列的混合编译产物 |

ppu arch 可以通过传递多个 `--gpu-architecture` option 提供全系列支持的混合编译产物。

下表指定了支持的编译阶段，以及 hgcc 对该阶段的执行，还列出了此阶段生成的输出文件的默认名称（当未使用选项明确指定输出文件名称时生效）（根据原文断行文本整理，个别选项拼接处需查原文确认）：

| 主机/设备端 | 编译阶段 | T-Head SAIL 编译器工具链 | 选项 | 阶段输出文件名后缀 |
|---|---|---|---|---|
| 设备端 | 预编译 | clang++ | `-E -triple ppu` | `-hggc-ppu-ppu.hggci` |
| 设备端 | 编译 | clang++ | `-x hggc-cpp-out` | `-hggc-ppu-ppu.bc` |
| 设备端 | 优化 | opt | `-march=ppu` | `-hggc-ppu-ppu-opt.bc` |
| 设备端 | 后端优化 | llc | `-march=ppu` | `-hggc-ppu-ppu-llc.o` |
| 设备端 | 链接 | lld | | `-hggc-ppu-ppu.out` |
| 设备端 | fatbin 生成 | hgfatbinary | | `.hgfb` |
| 主机端 | 预编译 | host 编译器 | `-E -triple` | `host.hggci` |
| 主机端 | 编译 | host 编译器 | `-cc1as` | `.o` |

#### 2.5.3.2 主机代码编译注意事项

- 编译单元（源文件及其头文件）如果不包含设备代码或符号，则可以直接使用主机编译器进行编译。**hgcc 默认会为用户链接 HGGC 运行时库**，使得编译程序中可以使用 HGGC 运行时 API 函数。
- hgcc 允许通过 **`-ccbin <compiler>`** 参数指定用于主机函数的主机编译器。hgcc 的 **`-Xcompiler`** 参数将参数传递给主机编译器。例如，下面的示例中 `-O3` 参数由 hgcc 传递给主机编译器：

```bash
hgcc example.hg -ccbin=clang++ -Xcompiler -O3
```

#### 2.5.3.3 PPU 代码的分离编译

- hgcc 默认采用**全程序编译**，期望在使用它们的编译单元中存在所有的 PPU 代码和符号。
- HGGC 设备函数可以调用在其他编译单元中定义的设备函数或访问设备变量，但在 hgcc 命令行上必须指定 **`-rdc=true`** 或其别名 **`-dc`** 标志，以启用从不同编译单元链接设备代码。从不同编译单元链接设备代码和符号的能力称为**分离编译（separate compilation）**。
- 分离编译允许更灵活的代码组织，可以改善编译时间，并可能导致更小的二进制文件。与全程序编译相比，分离编译可能涉及一些构建时复杂性。由于设备代码链接的使用可能会影响性能，这就是为什么它不是默认使用的。**链接时优化（LTO）** 可以帮助减少分离编译的性能开销。

分离编译需要满足以下条件：

- 在一个编译单元中定义的非 const device 变量必须在其他编译单元中使用 `extern` 关键字引用。
- 所有 HGGC 源文件 `.hg` 必须使用 `-dc` 或 `-rdc=true` 标志进行编译。

### 2.5.4 常见编译器选项

本节介绍 hgcc 中可使用的最重要编译器选项，涵盖语言特性、优化、调试、分析和构建方面。所有选项的完整描述可在 hgcc 文档中找到。

#### 2.5.4.1 语言特性选项

hgcc 支持 C++ 核心语言特性，从 C++03 到 C++20。

| 选项 | 说明 |
|---|---|
| `--std={c++03\|c++11\|c++14\|c++17\|c++20}` | 指定要使用的语言标准 |
| `-restrict` | 断言所有核函数指针参数都是 restrict 指针 |
| `-extended-lambda` | 允许在 lambda 声明中使用 host、device 注解 |
| `-expt-relaxed-constexpr` | （实验性标志）允许主机代码调用 device constexpr 函数，设备代码调用 host constexpr 函数 |
| `--default-stream per-thread` | 启用每线程默认流（见 2.3.2.3） |

#### 2.5.4.2 调试选项

| 选项 | 说明 |
|---|---|
| `-g` | 为主机代码生成调试信息。gdb/lldb 和类似工具依赖此类信息进行主机代码调试 |
| `-G` | 为设备代码生成调试信息。T-Head SAIL PPU-GDB（PPU GNU Debugger）依赖此类信息进行设备代码调试。该标志还定义了 `__HGGCCC_DEBUG__` 宏 |
| `-lineinfo` | 为设备代码生成行号信息。此选项不影响执行性能，与 asight 工具一起使用对跟踪核函数执行很有用 |
| `-DNDEBUG` | 禁用运行时断言（断言可能减慢执行速度） |

补充说明：

- hgcc **默认为 PPU 代码使用最高优化级别 `-O3`**。
- 调试标志 `-G` 阻止某些编译器优化，因此调试代码的性能预期低于非调试代码。

#### 2.5.4.3 优化选项

| 选项 | 说明 |
|---|---|
| `-extra-device-vectorization` | 启用更积极的设备代码矢量化 |
| `-res-usage` | 编译后打印资源使用报告。它包括为每个核函数分配的寄存器数量、共享内存和局部内存使用情况 |
| `-Xllvmb --ppu-warn-lmem-usage` | 如果使用局部内存则发出警告 |
| `-Xllvmb --ppu-warn-spills` | 如果寄存器溢出到局部内存则发出警告 |
| `--maxrregcount` | 指定每个线程的最大寄存器数（见 2.2.6，影响占用率） |
| （浮点控制标志） | 提供对浮点行为细粒度控制的附加标志在"浮点计算"部分和 hgcc 文档中有介绍 |

#### 2.5.4.4 链接时优化（LTO）

- 由于跨文件优化机会有限，分离编译可能导致比全程序编译更低的性能。**链接时优化（LTO）** 通过在链接时对单独编译的文件执行优化来解决这个问题，代价是增加了编译时间。LTO 可以恢复大部分全程序编译的性能，同时保持分离编译的灵活性。
- hgcc 需要 **`-dlto`** 标志链接时优化目标来启用 LTO。

#### 2.5.4.5 分析选项

无需在编译过程中添加额外标志，即可直接使用 **Asight** 工具分析 HGGC 应用程序。然而，hgcc 生成的附加信息可以通过将源文件与生成的代码相关联来辅助分析：

| 选项 | 说明 |
|---|---|
| `-lineinfo` | 为设备代码生成行号信息；这允许在分析工具中查看源代码。分析工具要求原始源代码在编译位置可用 |

#### 2.5.4.6 HGFatbin 压缩

hgcc **默认压缩**存储在应用程序或库二进制文件中的 hgfatbin。HGFatbin 压缩可以使用以下选项控制：

| 选项 | 说明 |
|---|---|
| `--no-compress` | 禁用 fatbin 压缩 |
| `--compress-mode={default\|size\|speed\|balance\|none}` | 设置压缩策略 |

#### hgcc 选项速查总表（本章出现的全部选项）

| 选项 | 类别 | 说明 |
|---|---|---|
| `-o <file>` | 通用 | 指定输出文件 |
| `-I <path>` | 通用 | 指定包含目录 |
| `-L <path>` | 通用 | 指定库路径 |
| `-l<library>` | 通用 | 链接其他库 |
| `-D<macro>=<value>` | 通用 | 定义宏 |
| `-v` | 通用 | 显示完整的编译工作流程和工具调用 |
| `-keep` / `--keep-dir <dir>` | 通用 | 保存编译过程中生成的中间文件（当前目录或指定目录） |
| `--gpu-architecture={ppu_10\|ppu_15}` | 架构 | 指定 PPU 编译产物；可多次指定生成混合产物 |
| `-ccbin <compiler>` | 主机编译 | 指定主机编译器 |
| `-Xcompiler <args>` | 主机编译 | 将参数传递给主机编译器 |
| `-rdc=true` / `-dc` | 编译模型 | 启用分离编译（不同编译单元链接设备代码） |
| `-dlto` | 优化 | 启用链接时优化（LTO） |
| `--std={c++03..c++20}` | 语言 | 指定 C++ 语言标准 |
| `-restrict` | 语言 | 断言核函数指针参数均为 restrict 指针 |
| `-extended-lambda` | 语言 | lambda 中允许 host/device 注解 |
| `-expt-relaxed-constexpr` | 语言 | （实验性）host/device constexpr 互调 |
| `--default-stream per-thread` | 语言/流 | 启用每线程默认流 |
| `-g` | 调试 | 主机代码调试信息 |
| `-G` | 调试 | 设备代码调试信息（定义 `__HGGCCC_DEBUG__`） |
| `-lineinfo` | 调试/分析 | 设备代码行号信息，不影响性能，配合 Asight |
| `-DNDEBUG` | 调试 | 禁用运行时断言 |
| `-extra-device-vectorization` | 优化 | 更积极的设备代码矢量化 |
| `-res-usage` | 优化 | 打印每核函数寄存器/共享内存/局部内存使用报告 |
| `-Xllvmb --ppu-warn-lmem-usage` | 优化 | 使用局部内存时警告 |
| `-Xllvmb --ppu-warn-spills` | 优化 | 寄存器溢出时警告 |
| `--maxrregcount <n>` | 优化 | 每线程最大寄存器数 |
| `--no-compress` | 构建 | 禁用 fatbin 压缩 |
| `--compress-mode={default\|size\|speed\|balance\|none}` | 构建 | 设置 fatbin 压缩策略 |

比赛关联：kernel 调优的标准编译组合是 `--gpu-architecture=ppu_15`（按比赛服务器实际 arch）+ `-res-usage` + `-Xllvmb --ppu-warn-spills` + `-lineinfo`：先用资源报告和溢出警告定位占用率瓶颈，再用 Asight 做源码级性能分析；`-restrict` 可让编译器对 GEMM 类 kernel 做更激进的别名优化。交付前去掉 `-G`、视情况加 `-DNDEBUG`。
