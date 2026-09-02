# T-Head SAIL acBLAS <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [1. 快速上手 {#1-快速上手}](#1-快速上手-1-快速上手)
  - [1.1. 数据布局与索引约定 {#11-数据布局与索引约定}](#11-数据布局与索引约定-11-数据布局与索引约定)
  - [1.2. 示例：1-based 索引 {#12-示例1-based-索引}](#12-示例1-based-索引-12-示例1-based-索引)
  - [1.3. 示例：0-based 索引 {#13-示例0-based-索引}](#13-示例0-based-索引-13-示例0-based-索引)
  - [1.4. 基本概念 {#14-基本概念}](#14-基本概念-14-基本概念)
- [2. 编程模型 {#2-编程模型}](#2-编程模型-2-编程模型)
  - [2.1. 句柄与上下文 {#21-句柄与上下文}](#21-句柄与上下文-21-句柄与上下文)
  - [2.2. Stream 管理 {#22-stream-管理}](#22-stream-管理-22-stream-管理)
  - [2.3. 标量参数与指针模式 {#23-标量参数与指针模式}](#23-标量参数与指针模式-23-标量参数与指针模式)
  - [2.4. 数学模式与精度控制 {#24-数学模式与精度控制}](#24-数学模式与精度控制-24-数学模式与精度控制)
  - [2.5. 结果可重现性 {#25-结果可重现性}](#25-结果可重现性-25-结果可重现性)
  - [2.6. Kernel 批处理与缓存 {#26-kernel-批处理与缓存}](#26-kernel-批处理与缓存-26-kernel-批处理与缓存)
  - [2.7. HGGC 计算图支持 {#27-hggc-graph-支持}](#27-hggc-计算图支持-27-hggc-graph-支持)
  - [2.8. 错误状态 {#28-错误状态}](#28-错误状态-28-错误状态)
- [3. 标准 BLAS 函数 {#3-标准-blas-函数}](#3-标准-blas-函数-3-标准-blas-函数)
  - [3.1. Level-1（向量运算） {#31-level-1向量运算}](#31-level-1向量运算-31-level-1向量运算)
  - [3.2. Level-2（矩阵-向量运算） {#32-level-2矩阵-向量运算}](#32-level-2矩阵-向量运算-32-level-2矩阵-向量运算)
  - [3.3. Level-3（矩阵-矩阵运算） {#33-level-3矩阵-矩阵运算}](#33-level-3矩阵-矩阵运算-33-level-3矩阵-矩阵运算)
- [4. BLAS 扩展 {#4-blas-扩展}](#4-blas-扩展-4-blas-扩展)
  - [4.1. 矩阵运算扩展 {#41-矩阵运算扩展}](#41-矩阵运算扩展-41-矩阵运算扩展)
  - [4.2. 批处理线性方程组求解 {#42-批处理线性方程组求解}](#42-批处理线性方程组求解-42-批处理线性方程组求解)
  - [4.3. 混合精度 GEMM {#43-混合精度-gemm}](#43-混合精度-gemm-43-混合精度-gemm)
  - [4.4. 扩展 Level-1 函数 {#44-扩展-level-1-函数}](#44-扩展-level-1-函数-44-扩展-level-1-函数)
- [5. acblasLt 轻量矩阵乘法 {#5-acblaslt-轻量矩阵乘法}](#5-acblaslt-轻量矩阵乘法-5-acblaslt-轻量矩阵乘法)
  - [5.1. 编程模型 {#51-编程模型}](#51-编程模型-51-编程模型)
  - [5.2. 描述符与布局类型 {#52-描述符与布局类型}](#52-描述符与布局类型-52-描述符与布局类型)
  - [5.3. API 函数 {#53-api-函数}](#53-api-函数-53-api-函数)
- [6. 类型与枚举 {#6-类型与枚举}](#6-类型与枚举-6-类型与枚举)
  - [6.1. 状态码 acblasStatus_t {#61-状态码-acblasstatus_t}](#61-状态码-acblasstatust-61-状态码-acblasstatust)
  - [6.2. acblasHandle_t {#62-acblashandle_t}](#62-acblashandlet-62-acblashandlet)
  - [6.3. 运算与填充枚举 {#63-运算与填充枚举}](#63-运算与填充枚举-63-运算与填充枚举)
  - [6.4. HGGC 数据类型 {#64-hggc-数据类型}](#64-hggc-数据类型-64-hggc-数据类型)
  - [6.5. 辅助函数 {#65-辅助函数}](#65-辅助函数-65-辅助函数)


T-Head SAIL acBLAS（以下简称 acBLAS）库用户指南。acBLAS 库是在真武 PPU 运行时之上实现的 BLAS（基本线性代数子程序）库。

acBLAS 提供两套并列的 API，使用场景各有侧重：

| API | 定位 | 适用场景 |
| :--- | :--- | :--- |
| **acBLAS API** | 标准 BLAS 实现 | Level-1 / Level-2 / Level-3 例程，覆盖向量/矩阵的通用线性代数运算 |
| **acblasLt API** | 轻量级 GEMM 专用接口 | 矩阵-矩阵乘法（GEMM），需要在数据布局、输入/计算类型、算法选择上做精细调优时使用 |

**acBLAS API 的典型使用流程**

1. 在真武 PPU 设备内存中分配所需的矩阵与向量；
2. 通过库提供的辅助函数把主机数据上传到设备；
3. 依次调用对应的 acBLAS 例程完成计算；
4. 把计算结果从设备内存回传到主机。

**acblasLt 的设计思路**

acblasLt 把"GEMM 该怎么做"和"GEMM 该用什么数据"解耦：开发者先围绕一次 GEMM 配置好矩阵布局、输入数据类型、计算数据类型、算法选择以及启发式参数，得到一组可复用的描述符；之后对形状、类型一致的不同输入可反复调用该配置而无需重新设置。整体使用模式与 acFFT 的「先建 plan，再多次执行」一致。

## 1. 快速上手 {#1-快速上手}

### 1.1. 数据布局与索引约定 {#11-数据布局与索引约定}

acBLAS 沿用列优先的内存模型，以最大程度兼容现有 BLAS 生态：

| 存储顺序 | 索引基准 |
| :--- | :--- |
| 列优先（column-major） | 1-based |

由于 C/C++ 默认以行优先方式访问二维数组，要让 C/C++ 代码直接对接 acBLAS， 不可依赖 `a[i][j]` 这种原生语法，需将矩阵视为一段连续的一维内存，并通过宏或内联函数手工计算下标。**前导维度 `ld`** （leading dimension）指的是这段一维内存中、相邻两列起点的间距；在列优先布局下，它等于矩阵实际分配的行数，即使后续只访问子矩阵，`ld` 仍保留为原始行数。

以下两种宏对应两种常见的索引基准，按代码来源选择：

| 索引基准 | 适用场景 | 元素 `(i, j)` 的线性下标 |
| :--- | :--- | :--- |
| 1-based | 希望保留原循环范围的代码 | `IDX2F(i, j, ld) = ((j) - 1) * (ld) + ((i) - 1)` |
| 0-based | 原生 C/C++ 代码 | `IDX2C(i, j, ld) = (j) * (ld) + (i)` |

对应的宏定义：

```cpp
#define IDX2F(i, j, ld)  ((((j) - 1) * (ld)) + ((i) - 1))
#define IDX2C(i, j, ld)  (((j) * (ld)) + (i))
```

以下两段完整示例分别演示了 1-based 与 0-based 两种索引风格，调用了 `acblasCreate` / `acblasSetMatrix` / `acblasSscal` / `acblasGetMatrix` / `acblasDestroy` 完整流程，可作为快速上手的模板。

### 1.2. 示例：1-based 索引 {#12-示例1-based-索引}

```cpp
// 示例 1. 使用 C 和 acBLAS 的应用程序：基于1的索引
// ----------------------------------------------------------
#include <hggc_runtime.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#include "acblas_v2.h"

// 列主序、1-based 的二维寻址宏
#define IDX_1B(i, j, ld) ((((j) - 1) * (ld)) + ((i) - 1))

enum { ROWS = 6, COLS = 5 };

// 对 (p,q) 起的子区域分别沿行、列两个方向调用 Sscal 做缩放
static inline void scale_block(acblasHandle_t h,
                               float *mat, int ld, int n,
                               int p, int q,
                               float row_scale, float col_scale)
{
    acblasSscal(h, n  - q + 1, &row_scale, &mat[IDX_1B(p, q, ld)], ld);
    acblasSscal(h, ld - p + 1, &col_scale, &mat[IDX_1B(p, q, ld)], 1);
}

int main(void)
{
    const size_t bytes = (size_t)ROWS * COLS * sizeof(float);

    // 1) 主机端矩阵分配并按 1-based 索引填充：a(i,j) = (i-1)*COLS + j
    float *hostMat = (float *)malloc(bytes);
    if (hostMat == NULL) {
        fprintf(stderr, "host memory allocation failed\n");
        return EXIT_FAILURE;
    }
    for (int col = 1; col <= COLS; ++col) {
        for (int row = 1; row <= ROWS; ++row) {
            hostMat[IDX_1B(row, col, ROWS)] = (float)((row - 1) * COLS + col);
        }
    }

    // 2) 设备端矩阵分配
    float *deviceMat = NULL;
    if (hggcMalloc((void **)&deviceMat, bytes) != hggcSuccess) {
        fprintf(stderr, "device memory allocation failed\n");
        free(hostMat);
        return EXIT_FAILURE;
    }

    // 3) 创建 acBLAS 上下文
    acblasHandle_t handle = NULL;
    if (acblasCreate(&handle) != ACBLAS_STATUS_SUCCESS) {
        fprintf(stderr, "ACBLAS initialization failed\n");
        hggcFree(deviceMat);
        free(hostMat);
        return EXIT_FAILURE;
    }

    // 4) Host -> Device 上传
    acblasStatus_t st = acblasSetMatrix(ROWS, COLS, sizeof(float),
                                        hostMat, ROWS, deviceMat, ROWS);
    if (st != ACBLAS_STATUS_SUCCESS) {
        fprintf(stderr, "H2D transfer failed\n");
        acblasDestroy(handle);
        hggcFree(deviceMat);
        free(hostMat);
        return EXIT_FAILURE;
    }

    // 5) 在设备上对子区域做缩放
    scale_block(handle, deviceMat, ROWS, COLS,
                /*p=*/2, /*q=*/3,
                /*row_scale=*/16.0f, /*col_scale=*/12.0f);

    // 6) Device -> Host 回拷
    st = acblasGetMatrix(ROWS, COLS, sizeof(float),
                         deviceMat, ROWS, hostMat, ROWS);
    if (st != ACBLAS_STATUS_SUCCESS) {
        fprintf(stderr, "D2H transfer failed\n");
        acblasDestroy(handle);
        hggcFree(deviceMat);
        free(hostMat);
        return EXIT_FAILURE;
    }

    // 7) 释放设备资源
    acblasDestroy(handle);
    hggcFree(deviceMat);

    // 8) 打印结果（按列遍历，每行输出一列）
    for (int col = 1; col <= COLS; ++col) {
        for (int row = 1; row <= ROWS; ++row) {
            printf("%7.0f", hostMat[IDX_1B(row, col, ROWS)]);
        }
        printf("\n");
    }

    free(hostMat);
    return EXIT_SUCCESS;
}
```

### 1.3. 示例：0-based 索引 {#13-示例0-based-索引}

```cpp
// 示例 2. 使用 C 和 acBLAS 的应用程序：基于0的索引
// ----------------------------------------------------------
#include <hggc_runtime.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#include "acblas_v2.h"

// 列主序、0-based 的二维寻址宏
#define IDX_0B(i, j, ld) (((j) * (ld)) + (i))

enum { ROWS = 6, COLS = 5 };

// 对 (p,q) 起的子区域分别沿行、列两个方向调用 Sscal 做缩放
static inline void scale_block(acblasHandle_t h,
                               float *mat, int ld, int n,
                               int p, int q,
                               float row_scale, float col_scale)
{
    // 沿行方向走 n-q 个元素，步长为 ld
    acblasSscal(h, n  - q, &row_scale, &mat[IDX_0B(p, q, ld)], ld);
    // 沿列方向走 ld-p 个元素，步长为 1
    acblasSscal(h, ld - p, &col_scale, &mat[IDX_0B(p, q, ld)], 1);
}

int main(void)
{
    const size_t bytes = (size_t)ROWS * COLS * sizeof(float);

    // 主机矩阵：使用 0-based 索引初始化 a(i,j) = i*COLS + j + 1
    float *host = (float *)malloc(bytes);
    if (host == NULL) {
        fprintf(stderr, "host memory allocation failed\n");
        return EXIT_FAILURE;
    }
    for (int j = 0; j < COLS; ++j) {
        for (int i = 0; i < ROWS; ++i) {
            host[IDX_0B(i, j, ROWS)] = (float)(i * COLS + j + 1);
        }
    }

    // 设备矩阵
    float *device = NULL;
    if (hggcMalloc((void **)&device, bytes) != hggcSuccess) {
        fprintf(stderr, "device memory allocation failed\n");
        free(host);
        return EXIT_FAILURE;
    }

    // acBLAS 上下文
    acblasHandle_t handle;
    if (acblasCreate(&handle) != ACBLAS_STATUS_SUCCESS) {
        fprintf(stderr, "ACBLAS initialization failed\n");
        hggcFree(device);
        free(host);
        return EXIT_FAILURE;
    }

    // H -> D
    if (acblasSetMatrix(ROWS, COLS, sizeof(float),
                        host, ROWS, device, ROWS) != ACBLAS_STATUS_SUCCESS) {
        fprintf(stderr, "H2D transfer failed\n");
        acblasDestroy(handle);
        hggcFree(device);
        free(host);
        return EXIT_FAILURE;
    }

    // 在设备上做缩放：注意 p=1, q=2 是 0-based 行/列下标
    scale_block(handle, device, ROWS, COLS, 1, 2, 16.0f, 12.0f);

    // D -> H
    if (acblasGetMatrix(ROWS, COLS, sizeof(float),
                        device, ROWS, host, ROWS) != ACBLAS_STATUS_SUCCESS) {
        fprintf(stderr, "D2H transfer failed\n");
        acblasDestroy(handle);
        hggcFree(device);
        free(host);
        return EXIT_FAILURE;
    }

    // 清理设备侧
    acblasDestroy(handle);
    hggcFree(device);

    // 打印结果
    for (int j = 0; j < COLS; ++j) {
        for (int i = 0; i < ROWS; ++i) {
            printf("%7.0f", host[IDX_0B(i, j, ROWS)]);
        }
        printf("\n");
    }

    free(host);
    return EXIT_SUCCESS;
}
```

### 1.4. 基本概念 {#14-基本概念}

| 概念 | 说明 |
| :--- | :--- |
| **列优先存储** | 所有矩阵均按列优先方式连续存储，前导维度 `ld` 表示相邻两列在内存中的跨距 |
| **句柄 (`acblasHandle_t`)** | 每个 acBLAS 调用都需要一个上下文句柄；句柄绑定到一个真武 PPU 设备，内部持有 stream、指针模式等状态 |
| **指针模式** | `HOST`，标量参数在主机内存；`DEVICE`，标量参数在设备内存（gemv 仅支持 HOST） |
| **数学模式** | 控制是否允许 Tensor Cell 加速及精度降级策略 |
| **标准 BLAS Level** | Level-1（向量-向量）/ Level-2（矩阵-向量）/ Level-3（矩阵-矩阵） |
| **acblasLt** | 轻量级 GEMM 专用接口，用描述符-plan 模式做精细调优 |

## 2. 编程模型 {#2-编程模型}

本章描述 acBLAS 的编程模型与上下文管理细节。

### 2.1. 句柄与上下文 {#21-句柄与上下文}

acBLAS 把所有运行时状态封装在一个**句柄（handle）** 里，库的使用流程围绕句柄展开：

| 阶段 | 操作 | 说明 |
| :--- | :--- | :--- |
| 创建 | `acblasCreate()` | 分配上下文资源，返回 `acblasHandle_t` |
| 使用 | 任意 acBLAS 函数 | 把句柄作为第一个参数显式传入 |
| 销毁 | `acblasDestroy()` | 释放与句柄关联的所有资源 |

**多设备 / 多线程使用模式**

借助句柄机制，应用可以将"各线程运行于哪个设备"显式表达出来：先在某个主机线程里调用 `hggcSetDevice()` 选择目标设备，再在该线程中调用 `acblasCreate()` 创建专属句柄，之后该线程后续调用 acBLAS 时只要传入对应句柄，计算就会被自动派发到正确的设备上。

**生命周期约束**

- 句柄绑定的设备在 `acblasCreate()` 和 `acblasDestroy()` 之间不可变更。要换设备，必须先 `hggcSetDevice()` 再创建一个新句柄；
- 句柄同时与 `acblasCreate()` 调用时的 HGGC 上下文紧绑定，多 HGGC 上下文场景下，每个 HGGC 上下文都需要单独的 acBLAS 句柄，且 HGGC 上下文不可先于对应的 acBLAS 句柄销毁。

### 2.2. Stream 管理 {#22-stream-管理}

当应用包含多个互相独立的计算任务时，可借助 HGGC stream 让它们在真武 PPU 上自动重叠。一般的实现思路是把"任务"和"stream"一一对应：

1. 用 `hggcStreamCreate()` 为每个任务创建一个 stream；
2. 在调用 acBLAS 例程前用 `acblasSetStream()` 把句柄切到目标 stream；
3. 不同 stream 上的计算会被真武 PPU 调度为并发执行，单任务规模不足以填满真武 PPU 时收益最明显。

!!! warning
    `acblasSetStream()` 会把用户提供的工作空间重置回默认工作空间池，需要时请在切 stream 之后重新调用 `acblasSetWorkspace()`。

为获得最大重叠度，建议配套使用设备指针模式传递标量（[参见 2.3](#23-标量参数与指针模式)）。Stream 的典型用例之一是把大量小 kernel 批处理调度，[详见 2.6](#26-kernel-批处理与缓存)。

### 2.3. 标量参数与指针模式 {#23-标量参数与指针模式}

涉及标量的 acBLAS 函数按用途分为两类：

| 类别 | 标量含义 | 代表函数 |
| :--- | :--- | :--- |
| 输入缩放 | 通过引用传入 `alpha` / `beta` | `gemm` 等所有 Level-2/3 例程（gemv 仅支持 HOST 模式） |
| 输出标量 | 把计算结果以标量形式返回 | `amax()`、`amin()`、`asum()`、`rotg()`、`rotmg()`、`dot()`、`nrm2()` |

两类函数对标量地址的处理都受 `acblasPointerMode_t` 控制：

**第一类（输入缩放）**

| 指针模式 | 标量位置 | 释放/同步约束 |
| :--- | :--- | :--- |
| `ACBLAS_POINTER_MODE_HOST` | 栈或堆（**不可** 放在 managed memory） | Kernel 启动时读取 `alpha` / `beta` 的当前值，因此函数返回后即可释放 |
| `ACBLAS_POINTER_MODE_DEVICE` | 设备内存 | Kernel 完成前不得修改其内容。`hggcFree()` 会隐式 `hggcDeviceSynchronize()`，但这样做与异步初衷相违背 |

**第二类（输出标量）**

| 指针模式 | 调用行为 |
| :--- | :--- |
| `ACBLAS_POINTER_MODE_HOST` | 阻塞调用，真武 PPU 完成后把结果复制回主机才返回 |
| `ACBLAS_POINTER_MODE_DEVICE` | 立即返回，结果驻留设备，需自行同步后再从主机读取 |

`ACBLAS_POINTER_MODE_DEVICE` 让 acBLAS 调用完全异步于主机，即便 `alpha` / `beta` 是由先前的 kernel 在设备上算出来的也无需先回 CPU。这一点在线性系统、特征值问题的迭代求解中尤为关键。注意 gemv 不支持 `DEVICE` 模式，仅支持 `HOST` 模式。

### 2.4. 数学模式与精度控制 {#24-数学模式与精度控制}

部分 GEMM 实现会**沿 K 维度切分计算** 以提升真武 PPU 占用率，特别是 K 远大于 M、N 时。无论这种切分是由 acBLAS 启发式自动选择，还是由开发者显式指定，各分块结果会以确定的顺序累加进结果矩阵，保证可重现性。

需特别注意 `acblasSgemmEx` 与 `acblasGemmEx()` 在「计算精度高于输出精度」时的行为：分块结果先转换、再相加可能在中间步骤溢出，而把所有点积都在 compute 精度下累加完再转换则不会。最常见的触发组合是 `computeType = HGGC_R_32F` 而 `Atype = Btype = Ctype = HGGC_R_16F`。如需禁止这种"先降精度再求和"，可通过 `acblasSetMathMode()` 选择 `ACBLAS_MATH_DISALLOW_REDUCED_PRECISION_REDUCTION`。

**Tensor Cell 的使用**

默认情况下 acBLAS 会自动使用 Tensor Cell，只要库内部判定它能带来更优性能。如需强制关闭，通过 `acblasSetMathMode()` 选择严格计算模式即可（见 [`acblasMath_t`](#637-acblasmath_t)）。

**对齐建议**

除 FP8 之外，矩阵维度和内存对齐已不再是 Tensor Cell 的硬性约束；但满足下表所有条件时仍能取得最佳性能：

| 维度方向 | 表达式 | 约束 |
| :--- | :--- | :--- |
| A 行/列方向 | `(op_A == ACBLAS_OP_N ? m : k) * AtypeSize` | `% 16 == 0` |
| B 行/列方向 | `(op_B == ACBLAS_OP_N ? k : n) * BtypeSize` | `% 16 == 0` |
| C 行方向 | `m * CtypeSize` | `% 16 == 0` |
| A 前导维度 | `lda * AtypeSize` | `% 16 == 0` |
| B 前导维度 | `ldb * BtypeSize` | `% 16 == 0` |
| C 前导维度 | `ldc * CtypeSize` | `% 16 == 0` |
| A/B/C 起始指针 | `intptr_t(A)`， `intptr_t(B)`， `intptr_t(C)` | `% 16 == 0` |

!!! warning
    使用 FP8 数据类型时（参见 [8 位浮点数据类型（FP8） 使用](#512-8-位浮点数据类型fp8使用)），上述所有对齐要求都从"建议"升级为"必须"。

比赛关联：Tensor Cell 是 PPU 上 GEMM 吞吐的关键，维度与指针满足 16 字节对齐表中的所有条件才能拿到最佳性能；FP8 量化路径下对齐从"建议"变为"必须"，做 FP8/INT8 量化推理时必须先在内存分配层保证对齐。

### 2.5. 结果可重现性 {#25-结果可重现性}

| 条件 | 是否保证位级一致 |
| :--- | :--- |
| 相同 toolkit 版本 + 相同架构 + 相同处理器核心数 + 单一活动 stream | 保证 |
| 跨 toolkit 版本 | 不保证（内部实现可能演进） |
| 多 stream 并发共用同一句柄（默认） | 不保证（库会按总体性能动态选择内部实现） |

> 多 stream 下出现的非确定性，根源是 acBLAS 为并发函数选择内部工作空间时的优化策略。

**在多 Stream 场景下恢复确定性** ，可任选下列一种方式：

| 方案 | 说明 |
| :--- | :--- |
| 显式工作空间 | 对每个 stream 调用 `acblasSetWorkspace()` 提供独立工作空间 |
| 一 stream 一句柄 | 每个 stream 配对一个 `acblasHandle_t` |
| 使用 acblasLtMatmul | 替换 GEMM 函数族，自行提供工作空间 |
| 环境变量 `ACBLAS_WORKSPACE_CONFIG` | 设为 `:16:8`（可能牺牲性能）或 `:4096:8`（真武 PPU 内存占用约增加 24 MiB） |

### 2.6. Kernel 批处理与缓存 {#26-kernel-批处理与缓存}

对密集矩阵执行大量**小规模独立矩阵乘法** 是 Stream 批处理的典型场景。

规模差距如下：单次 $n \times n$ GEMM 在 $n^2$ 数据上执行 $n^3$ 次乘加；而 $1024$ 次 $\tfrac{n}{32} \times \tfrac{n}{32}$ 的 GEMM 在同等数据量上只执行 $1024 \cdot (\tfrac{n}{32})^3 = \tfrac{n^3}{32}$ 次乘加，理论上小矩阵无法达到大矩阵的 GFLOPS 峰值。即便如此，把这些小矩阵并发起来仍远好于串行执行。

由于真武 PPU 架构支持多 kernel 并发，批处理的做法是：用 `hggcStreamCreate()` 创建 N 个 stream（如示例中的 1024 个），每次调用 `acblas<t>gemm()` 前 `acblasSetStream()` 切换到对应 stream。这样独立 GEMM 就会在硬件允许的范围内并发执行。

| 项 | 限制 |
| :--- | :--- |
| 可创建的 stream 数 | 实际无硬上限 |
| 同时并发执行的 kernel 数 | 最多**32** |

!!! warning
    同样注意 `acblasSetStream()` 会重置工作空间，[参见 2.2](#22-stream-管理) 中的提示。

**缓存配置**

部分设备上**L1 cache 与 shared memory 共享同一硬件资源** ，调整两者的切分比例可能影响 acBLAS 函数性能。

| 操作 | 接口 |
| :--- | :--- |
| 设备级缓存配置 | `hggcDeviceSetCacheConfig` |
| 单函数级缓存配置 | `hggcFuncSetCacheConfig` |

acBLAS 自身不设置缓存偏好，而是沿用当前配置，目的是避免在 Kernel 切换时频繁切换配置而抑制 Kernel 并发性。但部分 acBLAS 函数（尤其是 Level-3）对 shared memory 的容量敏感，需要时由调用方按场景调优。详细语义参见 [HGGC Runtime API 文档](04_runtime_api.md)。

比赛关联：小矩阵 GEMM 批量并发（多 stream + `acblasSetStream`）是提升 decode 阶段小 batch 吞吐的手段之一，但注意同硬件最多 32 个 kernel 并发、且切 stream 会重置工作空间；L1/shared memory 切分（`hggcFuncSetCacheConfig`）也可作为 Level-3 算子调优的旋钮。

### 2.7. HGGC 计算图支持 {#27-hggc-graph-支持}

绝大多数 acBLAS 函数都可以无限制地被 HGGC 计算图流捕获。规则汇总如下：

| 元素 | HOST 指针模式 | DEVICE 指针模式 |
| :--- | :--- | :--- |
| 标量输入（`alpha` / `beta`） | 值在捕获时被固化到图中 | 图执行时按设备指针读取 |
| 标量输出函数（如 `acblas<t>dot`） | **不可捕获** ：会强制触发同步 | 可捕获 |

!!! tip
    **关于工作空间内存节点** ：捕获期间 acBLAS 可借助 Stream-ordered 分配 API `hggcMallocAsync` / `hggcFreeAsync` 创建内存节点，但子计算图与设备侧启动的 graph 不支持内存节点，可能导致捕获失败。规避方式是预先通过 `acblasSetWorkspace()` 提供开发者自有工作空间。

### 2.8. 错误状态 {#28-错误状态}

acBLAS 中**所有** 对外 API 调用都通过返回值 `acblasStatus_t` 报告执行结果，调用方应在每次调用后检查该返回码，详细取值参见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

## 3. 标准 BLAS 函数 {#3-标准-blas-函数}

### 3.1. Level-1（向量运算） {#31-level-1向量运算}

Level-1 BLAS（BLAS1）针对标量与向量进行运算。后续小节遵循以下统一约定，以避免重复说明：

**类型代号** ：函数原型用 `<type>` 占位元素类型，`<t>` 占位首字母。

| `<type>` | `<t>` | 数学含义 |
| :--- | :--- | :--- |
| `float` | `s` / `S` | 实数单精度 |
| `double` | `d` / `D` | 实数双精度 |
| `cuComplex` | `c` / `C` | 复数单精度 |
| `cuDoubleComplex` | `z` / `Z` | 复数双精度 |

> 当输入类型与输出类型不一致时（如 `dot`、`asum` 等），原型里会同时出现两套字母。

**索引基准** ：所有 Level-1 函数都沿用 1-based 下标。下文公式中出现的 `j = 1 + (i-1)*incx` 即此约定，后续不再单独标注。

**符号习惯** ：标量用小写希腊字母（α、β），向量用粗体小写英文字母（**x** 、**y** ），矩阵用大写英文字母（A、B、C）。

#### 3.1.1. acblas&lt;t&gt;amax() {#311-acblaslttgtamax}

```cpp
acblasStatus_t
acblasIsamax(acblasHandle_t handle, int n,
             const float *x, int incx, int *result)
acblasStatus_t
acblasIdamax(acblasHandle_t handle, int n,
             const double *x, int incx, int *result)
```

返回向量**x** 中绝对值最大的元素的索引。具体地，找出最早使 $|x[j]|$ 取得最大值的 $i \in [1, n]$，其中 $j = 1 + (i-1)\,\text{incx}$。

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle` | | 输入 | acBLAS 上下文 |
| `n` | | 输入 | `x` 的元素数 |
| `x` | device | 输入 | `<type>` 向量 |
| `incx` | | 输入 | `x` 相邻元素的步幅 |
| `result` | host / device | 输出 | 命中的索引；当 `n <= 0` 或 `incx <= 0` 时为 `0` |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_ALLOC_FAILED`：归约缓冲区分配失败。
- `ACBLAS_STATUS_EXECUTION_FAILED`：真武 PPU Kernel 启动失败。
- `ACBLAS_STATUS_INVALID_VALUE`：`result` 为 NULL。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 3.1.2. acblas&lt;t&gt;amin() {#312-acblaslttgtamin}

```cpp
acblasStatus_t
acblasIsamin(acblasHandle_t handle, int n,
             const float *x, int incx, int *result)
acblasStatus_t
acblasIdamin(acblasHandle_t handle, int n,
             const double *x, int incx, int *result)
```

`acblas<t>amax()` 的"最小值"对偶：返回最早让 $|x[j]|$ 取得最小值的下标 $i$。参数列表与返回码均同 3.1.1。

#### 3.1.3. acblas&lt;t&gt;asum() {#313-acblaslttgtasum}

```cpp
acblasStatus_t
acblasSasum(acblasHandle_t handle, int n,
            const float *x, int incx, float *result)
acblasStatus_t
acblasDasum(acblasHandle_t handle, int n,
            const double *x, int incx, double *result)
```

逐元素绝对值求和：

$$\text{result} = \sum_{i=1}^{n}|x[j]|,\quad j = 1 + (i-1)\,\text{incx}$$

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle` | | 输入 | acBLAS 上下文 |
| `n` | | 输入 | `x` 的元素数 |
| `x` | device | 输入 | `<type>` 向量 |
| `incx` | | 输入 | `x` 相邻元素的步幅 |
| `result` | host / device | 输出 | 绝对值之和；当 `n <= 0` 或 `incx <= 0` 时为 `0.0` |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_ALLOC_FAILED`：归约缓冲区分配失败。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。
- `ACBLAS_STATUS_INVALID_VALUE`：`result == NULL`。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 3.1.4. acblas&lt;t&gt;axpy() {#314-acblaslttgtaxpy}

```cpp
acblasStatus_t
acblasSaxpy(acblasHandle_t handle, int n,
            const float *alpha,
            const float *x, int incx,
            float *y, int incy)
acblasStatus_t
acblasDaxpy(acblasHandle_t handle, int n,
            const double *alpha,
            const double *x, int incx,
            double *y, int incy)
```

经典的 SAXPY/DAXPY：用 $\alpha$ 缩放**x** 后累加到**y** ，结果**原地** 写回**y** ：

$$\mathbf{y}[j]\mathrel{+}=\alpha\cdot\mathbf{x}[k],\qquad k = 1+(i-1)\,\text{incx},\ j = 1+(i-1)\,\text{incy}$$

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle` | | 输入 | acBLAS 上下文 |
| `alpha` | host / device | 输入 | `<type>` 缩放因子 |
| `n` | | 输入 | `x`、`y` 的元素数 |
| `x` | device | 输入 | 长度为 `n` 的 `<type>` 向量 |
| `incx` | | 输入 | `x` 相邻元素的步幅 |
| `y` | device | 输入/输出 | 长度为 `n` 的 `<type>` 向量 |
| `incy` | | 输入 | `y` 相邻元素的步幅 |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 3.1.5. acblas&lt;t&gt;copy() {#315-acblaslttgtcopy}

```cpp
acblasStatus_t
acblasScopy(acblasHandle_t handle, int n,
            const float *x, int incx,
            float *y, int incy)
acblasStatus_t
acblasDcopy(acblasHandle_t handle, int n,
            const double *x, int incx,
            double *y, int incy)
```

按步幅把**x** 拷贝到**y** ：$\mathbf{y}[j] = \mathbf{x}[k]$，下标定义同 `axpy`。

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle` | | 输入 | acBLAS 上下文 |
| `n` | | 输入 | `x`、`y` 的元素数 |
| `x` | device | 输入 | 长度为 `n` 的 `<type>` 向量 |
| `incx` | | 输入 | `x` 相邻元素的步幅 |
| `y` | device | 输出 | 长度为 `n` 的 `<type>` 向量 |
| `incy` | | 输入 | `y` 相邻元素的步幅 |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 3.1.6. acblas&lt;t&gt;dot() {#316-acblaslttgtdot}

```cpp
acblasStatus_t
acblasSdot(acblasHandle_t handle, int n,
           const float *x, int incx,
           const float *y, int incy,
           float *result)
acblasStatus_t
acblasDdot(acblasHandle_t handle, int n,
           const double *x, int incx,
           const double *y, int incy,
           double *result)
```

向量点积：

$$\text{result} = \sum_{i=1}^{n} \mathbf{x}[k]\cdot\mathbf{y}[j],\qquad k = 1+(i-1)\,\text{incx},\ j = 1+(i-1)\,\text{incy}$$

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle` | | 输入 | acBLAS 上下文 |
| `n` | | 输入 | `x`、`y` 的元素数 |
| `x` | device | 输入 | 长度为 `n` 的 `<type>` 向量 |
| `incx` | | 输入 | `x` 相邻元素的步幅 |
| `y` | device | 输入 | 长度为 `n` 的 `<type>` 向量 |
| `incy` | | 输入 | `y` 相邻元素的步幅 |
| `result` | host / device | 输出 | 点积值；`n <= 0` 时为 `0.0` |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_ALLOC_FAILED`：内存分配失败。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 3.1.7. acblas&lt;t&gt;nrm2() {#317-acblaslttgtnrm2}

```cpp
acblasStatus_t
acblasSnrm2(acblasHandle_t handle, int n,
            const float *x, int incx, float *result)
acblasStatus_t
acblasDnrm2(acblasHandle_t handle, int n,
            const double *x, int incx, double *result)
```

向量**x** 的欧几里得范数。为防止中间累加上/下溢，内部采用**分阶段累加** 实现，数学结果等价于：

$$\text{result} = \sqrt{\sum_{i=1}^{n} \mathbf{x}[j]^2},\qquad j = 1+(i-1)\,\text{incx}$$

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle` | | 输入 | acBLAS 上下文 |
| `n` | | 输入 | `x` 的元素数 |
| `x` | device | 输入 | 长度为 `n` 的 `<type>` 向量 |
| `incx` | | 输入 | `x` 相邻元素的步幅 |
| `result` | host / device | 输出 | 范数；`n <= 0` 或 `incx <= 0` 时为 `0.0` |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_ALLOC_FAILED`：内存分配失败。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。
- `ACBLAS_STATUS_INVALID_VALUE`：`result == NULL`。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 3.1.8. acblas&lt;t&gt;rot() {#318-acblaslttgtrot}

```cpp
acblasStatus_t
acblasSrot(acblasHandle_t handle, int n,
           float *x, int incx,
           float *y, int incy,
           const float *c, const float *s)
acblasStatus_t
acblasDrot(acblasHandle_t handle, int n,
           double *x, int incx,
           double *y, int incy,
           const double *c, const double *s)
```

把 Givens 旋转

$$G = \begin{pmatrix} c & s \\ -s & c \end{pmatrix}$$

逐对地作用到 (**x**, **y**) 上，即把 x-y 平面内的逆时针旋转应用到向量配对，其中 $c = \cos\alpha$、$s = \sin\alpha$：

$$
\begin{aligned}
\mathbf{x}[k] &\gets c\,\mathbf{x}[k] + s\,\mathbf{y}[j] \\
\mathbf{y}[j] &\gets -s\,\mathbf{x}[k] + c\,\mathbf{y}[j]
\end{aligned}
$$

下标 $k = 1+(i-1)\,\text{incx}$、$j = 1+(i-1)\,\text{incy}$。

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle` | | 输入 | acBLAS 上下文 |
| `n` | | 输入 | 向量长度 |
| `x` | device | 输入/输出 | 长度为 `n` 的 `<type>` 向量 |
| `incx` | | 输入 | `x` 步幅 |
| `y` | device | 输入/输出 | 长度为 `n` 的 `<type>` 向量 |
| `incy` | | 输入 | `y` 步幅 |
| `c` | host / device | 输入 | 旋转矩阵的余弦分量 |
| `s` | host / device | 输入 | 旋转矩阵的正弦分量 |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 3.1.9. acblas&lt;t&gt;rotg() {#319-acblaslttgtrotg}

```cpp
acblasStatus_t
acblasSrotg(acblasHandle_t handle,
            float *a, float *b,
            float *c, float *s)
acblasStatus_t
acblasDrotg(acblasHandle_t handle,
            double *a, double *b,
            double *c, double *s)
```

为给定的 $2\times 1$ 向量 $(a, b)^T$ 构造 Givens 旋转矩阵 $G$，使其作用后第二分量归零：

$$G = \begin{pmatrix} c & s \\ -s & c \end{pmatrix},\qquad
G\begin{pmatrix} a\\ b \end{pmatrix} = \begin{pmatrix} r\\ 0 \end{pmatrix}$$

**实数情形** ：满足 $c^2 + s^2 = 1$、$r = \pm\sqrt{a^2+b^2}$。函数返回时，`a` 被 $r$ 覆盖、`b` 被一个辅助量 $z$ 覆盖。$z$ 设计成可仅凭它一个值还原 $(c, s)$：

$$
(c, s) = \begin{cases}
(\sqrt{1-z^2},\ z) & |z| < 1 \\
(0,\ 1) & |z| = 1 \\
(1/z,\ \sqrt{1-z^2}) & |z| > 1
\end{cases}
$$

其中

$$r = \begin{cases}
\dfrac{a}{|a|}\,\bigl\lVert (a, b)^T \bigr\rVert_2 & a \ne 0 \\
b & a = 0
\end{cases},\qquad \bigl\lVert (a, b)^T \bigr\rVert_2 = \sqrt{|a|^2 + |b|^2}$$

函数返回时同样把 `a` 覆盖为 $r$。

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle` | | 输入 | acBLAS 上下文 |
| `a` | host / device | 输入/输出 | `<type>` 标量；返回时被 $r$ 覆盖 |
| `b` | host / device | 输入/输出 | `<type>` 标量；返回时被 $z$ 覆盖 |
| `c` | host / device | 输出 | 余弦分量 |
| `s` | host / device | 输出 | 正弦分量 |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 3.1.10. acblas&lt;t&gt;rotm() {#3110-acblaslttgtrotm}

```cpp
acblasStatus_t
acblasSrotm(acblasHandle_t handle, int n,
            float *x, int incx,
            float *y, int incy, const float *param)
acblasStatus_t
acblasDrotm(acblasHandle_t handle, int n,
            double *x, int incx,
            double *y, int incy, const double *param)
```

把**修正 Givens 变换** $H$ 逐对作用到 (**x**, **y**)：

$$H = \begin{pmatrix} h_{11} & h_{12} \\ h_{21} & h_{22} \end{pmatrix},\qquad
\begin{aligned}
\mathbf{x}[k] &\gets h_{11}\mathbf{x}[k] + h_{12}\mathbf{y}[j] \\
\mathbf{y}[j] &\gets h_{21}\mathbf{x}[k] + h_{22}\mathbf{y}[j]
\end{aligned}$$

下标定义同 `rot`。$H$ 的四个非平凡分量按 `param[1..4]` 顺序存储；`flag = param[0]` 决定哪些分量是常数、哪些从 `param` 读取：

| `flag` | 矩阵 $H$ |
| :--- | :--- |
| `-1.0` | $\begin{pmatrix} h_{11} & h_{12} \\ h_{21} & h_{22} \end{pmatrix}$ |
| `0.0` | $\begin{pmatrix} 1.0 & h_{12} \\ h_{21} & 1.0 \end{pmatrix}$ |
| `1.0` | $\begin{pmatrix} h_{11} & 1.0 \\ -1.0 & h_{22} \end{pmatrix}$ |
| `-2.0` | $\begin{pmatrix} 1.0 & 0.0 \\ 0.0 & 1.0 \end{pmatrix}$（恒等矩阵） |

> 由 `flag` 隐含的 `-1.0`、`0.0`、`1.0` 不保存在 `param` 中。

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle` | | 输入 | acBLAS 上下文 |
| `n` | | 输入 | 向量长度 |
| `x` | device | 输入/输出 | 长度为 `n` 的 `<type>` 向量 |
| `incx` | | 输入 | `x` 步幅 |
| `y` | device | 输入/输出 | 长度为 `n` 的 `<type>` 向量 |
| `incy` | | 输入 | `y` 步幅 |
| `param` | host / device | 输入 | 5 元素 `<type>` 数组：`param[0] = flag`，`param[1..4] = h_{ij}` |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 3.1.11. acblas&lt;t&gt;rotmg() {#3111-acblaslttgtrotmg}

```cpp
acblasStatus_t
acblasSrotmg(acblasHandle_t handle,
             float *d1, float *d2,
             float *x1, const float *y1,
             float *param)
acblasStatus_t
acblasDrotmg(acblasHandle_t handle,
             double *d1, double *d2,
             double *x1, const double *y1,
             double *param)
```

为输入 $(d_1, d_2, x_1, y_1)$ 构造修正 Givens 变换 $H$，使其作用于 $\bigl(\sqrt{d_1}\,x_1,\ \sqrt{d_2}\,y_1\bigr)^T$ 后第二分量归零；`flag = param[0]` 与对应 $H$ 的关系同 3.1.10。

> `flag` 隐含的 `-1.0`、`0.0`、`1.0` 不写入 `param`。

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle` | | 输入 | acBLAS 上下文 |
| `d1` | host / device | 输入/输出 | `<type>` 标量；返回时覆盖原值 |
| `d2` | host / device | 输入/输出 | `<type>` 标量；返回时覆盖原值 |
| `x1` | host / device | 输入/输出 | `<type>` 标量；返回时覆盖原值 |
| `y1` | host / device | 输入 | `<type>` 标量 |
| `param` | host / device | 输出 | 5 元素 `<type>` 数组：`param[0]=flag`，`param[1..4]=h_{ij}` |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 3.1.12. acblas&lt;t&gt;scal() {#3112-acblaslttgtscal}

```cpp
acblasStatus_t
acblasSscal(acblasHandle_t handle, int n,
            const float *alpha,
            float *x, int incx)
acblasStatus_t
acblasDscal(acblasHandle_t handle, int n,
            const double *alpha,
            double *x, int incx)
```

原地缩放：$\mathbf{x}[j] \gets \alpha\,\mathbf{x}[j]$，$j = 1 + (i-1)\,\text{incx}$。

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle` | | 输入 | acBLAS 上下文 |
| `alpha` | host / device | 输入 | `<type>` 缩放因子 |
| `n` | | 输入 | `x` 的元素数 |
| `x` | device | 输入/输出 | 长度为 `n` 的 `<type>` 向量 |
| `incx` | | 输入 | `x` 步幅 |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 3.1.13. acblas&lt;t&gt;swap() {#3113-acblaslttgtswap}

```cpp
acblasStatus_t
acblasSswap(acblasHandle_t handle, int n,
            float *x, int incx,
            float *y, int incy)
acblasStatus_t
acblasDswap(acblasHandle_t handle, int n,
            double *x, int incx,
            double *y, int incy)
```

按步幅交换**x** 与**y** 的元素：$\mathbf{x}[k] \leftrightarrow \mathbf{y}[j]$，下标定义同 `axpy`。

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle` | | 输入 | acBLAS 上下文 |
| `n` | | 输入 | 向量长度 |
| `x` | device | 输入/输出 | 长度为 `n` 的 `<type>` 向量 |
| `incx` | | 输入 | `x` 步幅 |
| `y` | device | 输入/输出 | 长度为 `n` 的 `<type>` 向量 |
| `incy` | | 输入 | `y` 步幅 |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

### 3.2. Level-2（矩阵-向量运算） {#32-level-2矩阵-向量运算}

Level-2 BLAS（BLAS2）覆盖矩阵—向量级别的运算。本节沿用 3.1 节关于类型代号、1-based 索引的统一约定。

#### 3.2.1. acblas&lt;t&gt;gemv() {#321-acblaslttgtgemv}

```cpp
acblasStatus_t
acblasSgemv(acblasHandle_t handle, acblasOperation_t trans,
            int m, int n,
            const float *alpha,
            const float *A, int lda,
            const float *x, int incx,
            const float *beta,
            float *y, int incy)
acblasStatus_t
acblasDgemv(acblasHandle_t handle, acblasOperation_t trans,
            int m, int n,
            const double *alpha,
            const double *A, int lda,
            const double *x, int incx,
            const double *beta,
            double *y, int incy)
```

矩阵—向量乘法 $\mathbf{y} \gets \alpha \,\text{op}(A)\,\mathbf{x} + \beta\,\mathbf{y}$，其中 $A$ 为 $m \times n$ 矩阵，$\text{op}(A)$ 由 `trans` 决定：

| `trans` | $\text{op}(A)$ |
| :--- | :--- |
| `ACBLAS_OP_N` | $A$ |
| `ACBLAS_OP_T` | $A^{\!T}$ |

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle` | | 输入 | acBLAS 上下文 |
| `trans` | | 输入 | $\text{op}(A)$ 选择项 |
| `m`， `n` | | 输入 | $A$ 的行数 / 列数 |
| `alpha` | host | 输入 | `<type>` 缩放因子 |
| `A` | device | 输入 | `<type>` 数组，维度 `lda × n`，`lda ≥ max(1, m)`；调用前需在前导 `m × n` 区域填好系数；本函数不修改 |
| `lda` | | 输入 | 前导维度，`≥ max(1, m)` |
| `x` | device | 输入 | `<type>` 向量；`trans == ACBLAS_OP_N` 时至少 `1+(n-1)*\|incx\|` 个元素，否则至少 `1+(m-1)*\|incx\|` 个 |
| `incx` | | 输入 | `x` 步幅 |
| `beta` | host | 输入 | `<type>` 缩放因子；为 `0` 时 `y` 无须为有效输入 |
| `y` | device | 输入/输出 | `<type>` 向量；`ACBLAS_OP_N` 时至少 `1+(m-1)*\|incy\|` 个元素，否则至少 `1+(n-1)*\|incy\|` 个 |
| `incy` | | 输入 | `y` 步幅 |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_INVALID_VALUE`：`m, n < 0` 或 `incx, incy == 0`。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 3.2.2. acblas&lt;t&gt;ger() {#322-acblaslttgtger}

```cpp
acblasStatus_t
acblasSger(acblasHandle_t handle, int m, int n,
           const float *alpha,
           const float *x, int incx,
           const float *y, int incy,
           float *A, int lda)
acblasStatus_t
acblasDger(acblasHandle_t handle, int m, int n,
           const double *alpha,
           const double *x, int incx,
           const double *y, int incy,
           double *A, int lda)
```

外积秩-1 更新，把 $\alpha\,\mathbf{x}\mathbf{y}^{T}$ 加到 $A$ 上：

$$
A \gets A + \alpha\,\mathbf{x}\,\mathbf{y}^{T}
$$

$A$ 是 $m \times n$ 列优先矩阵，**x** 、**y** 为向量，$\alpha$ 为标量。

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle` | | 输入 | acBLAS 上下文 |
| `m`， `n` | | 输入 | $A$ 的行数 / 列数 |
| `alpha` | host / device | 输入 | `<type>` 缩放因子 |
| `x` | device | 输入 | 长度为 `m` 的 `<type>` 向量 |
| `incx` | | 输入 | `x` 步幅 |
| `y` | device | 输入 | 长度为 `n` 的 `<type>` 向量 |
| `incy` | | 输入 | `y` 步幅 |
| `A` | device | 输入/输出 | 维度 `lda × n` 的 `<type>` 数组，`lda ≥ max(1, m)` |
| `lda` | | 输入 | $A$ 的前导维度 |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_INVALID_VALUE`：`m < 0`、`n < 0`、`incx = 0`、`incy = 0`、`alpha = NULL` 或 `lda < max(1, m)`。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 3.2.3. acblas&lt;t&gt;spr() {#323-acblaslttgtspr}

```cpp
acblasStatus_t
acblasSspr(acblasHandle_t handle, acblasFillMode_t uplo,
           int n, const float *alpha,
           const float *x, int incx, float *AP)
acblasStatus_t
acblasDspr(acblasHandle_t handle, acblasFillMode_t uplo,
           int n, const double *alpha,
           const double *x, int incx, double *AP)
```

**压缩** 对称秩-1 更新：$A \gets A + \alpha\,\mathbf{x}\mathbf{x}^{T}$，其中 $A$ 为以**压缩** 格式存放的 $n \times n$ 对称阵，只保留三角区域、按列依次紧排，因此整阵只占 $n(n+1)/2$ 个元素。

`uplo` 决定保留哪一侧三角，对应的元素 $A(i, j)$ 在 `AP` 中的下标如下：

| `uplo` | 元素位置 | 取值范围 |
| :--- | :--- | :--- |
| `ACBLAS_FILL_MODE_LOWER` | $\text{AP}\bigl[i + \tfrac{(2n - j + 1)\,j}{2}\bigr]$ | $j = 1..n,\ i \ge j$ |
| `ACBLAS_FILL_MODE_UPPER` | $\text{AP}\bigl[i + \tfrac{j(j+1)}{2}\bigr]$ | $j = 1..n,\ i \le j$ |

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle` | | 输入 | acBLAS 上下文 |
| `uplo` | | 输入 | 选择保留下/上三角；另一侧由对称性推得 |
| `n` | | 输入 | $A$ 的阶数 |
| `alpha` | host / device | 输入 | `<type>` 缩放因子 |
| `x` | device | 输入 | 长度为 `n` 的 `<type>` 向量 |
| `incx` | | 输入 | `x` 步幅 |
| `AP` | device | 输入/输出 | $A$ 的压缩存储数组 |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_INVALID_VALUE`：`n < 0`、`incx = 0`、`uplo` 不在 `LOWER`/`UPPER` 之列、`alpha = NULL`。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 3.2.4. acblas&lt;t&gt;spr2() {#324-acblaslttgtspr2}

```cpp
acblasStatus_t
acblasSspr2(acblasHandle_t handle, acblasFillMode_t uplo,
            int n, const float *alpha,
            const float *x, int incx,
            const float *y, int incy, float *AP)
acblasStatus_t
acblasDspr2(acblasHandle_t handle, acblasFillMode_t uplo,
            int n, const double *alpha,
            const double *x, int incx,
            const double *y, int incy, double *AP)
```

`spr` 的「秩-2」对偶，把对称外积叠加到压缩矩阵：

$$A \gets A + \alpha\,\bigl(\mathbf{x}\mathbf{y}^{T} + \mathbf{y}\mathbf{x}^{T}\bigr)$$

存储约定与下标公式同 3.2.3，不再赘述。

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle` | | 输入 | acBLAS 上下文 |
| `uplo` | | 输入 | 三角侧选择 |
| `n` | | 输入 | $A$ 的阶数 |
| `alpha` | host / device | 输入 | `<type>` 缩放因子 |
| `x` | device | 输入 | 长度为 `n` 的 `<type>` 向量 |
| `incx` | | 输入 | `x` 步幅 |
| `y` | device | 输入 | 长度为 `n` 的 `<type>` 向量 |
| `incy` | | 输入 | `y` 步幅 |
| `AP` | device | 输入/输出 | $A$ 的压缩存储数组 |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_INVALID_VALUE`：`n < 0`、`incx = 0`、`incy = 0`、`uplo` 不在合法集、`alpha = NULL`。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 3.2.5. acblas&lt;t&gt;syr() {#325-acblaslttgtsyr}

```cpp
acblasStatus_t
acblasSsyr(acblasHandle_t handle, acblasFillMode_t uplo,
           int n, const float *alpha,
           const float *x, int incx, float *A, int lda)
acblasStatus_t
acblasDsyr(acblasHandle_t handle, acblasFillMode_t uplo,
           int n, const double *alpha,
           const double *x, int incx, double *A, int lda)
```

对称秩-1 更新，和 `spr` 同形：$A \gets A + \alpha\,\mathbf{x}\mathbf{x}^{T}$。区别在于 $A$ 此处为普通列优先的 $n \times n$ 对称阵（不压缩），仅 `uplo` 指定的那一侧会被读写。

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle` | | 输入 | acBLAS 上下文 |
| `uplo` | | 输入 | 三角侧选择；不引用另一侧 |
| `n` | | 输入 | $A$ 的阶数 |
| `alpha` | host / device | 输入 | `<type>` 缩放因子 |
| `x` | device | 输入 | 长度为 `n` 的 `<type>` 向量 |
| `incx` | | 输入 | `x` 步幅 |
| `A` | device | 输入/输出 | 维度 `lda × n` 的 `<type>` 数组，`lda ≥ max(1, n)` |
| `lda` | | 输入 | $A$ 的前导维度 |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_INVALID_VALUE`：`n < 0`、`incx = 0`、`uplo` 非法、`lda < max(1, n)`、`alpha = NULL`。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 3.2.6. acblas&lt;t&gt;syr2() {#326-acblaslttgtsyr2}

```cpp
acblasStatus_t
acblasSsyr2(acblasHandle_t handle, acblasFillMode_t uplo, int n,
            const float *alpha, const float *x, int incx,
            const float *y, int incy, float *A, int lda)
acblasStatus_t
acblasDsyr2(acblasHandle_t handle, acblasFillMode_t uplo, int n,
            const double *alpha, const double *x, int incx,
            const double *y, int incy, double *A, int lda)
```

对称秩-2 更新（非压缩存储下的 `spr2`）：

$$A \gets A + \alpha\,\bigl(\mathbf{x}\mathbf{y}^{T} + \mathbf{y}\mathbf{x}^{T}\bigr)$$

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle` | | 输入 | acBLAS 上下文 |
| `uplo` | | 输入 | 三角侧选择；不引用另一侧 |
| `n` | | 输入 | $A$ 的阶数 |
| `alpha` | host / device | 输入 | `<type>` 缩放因子 |
| `x` | device | 输入 | 长度为 `n` 的 `<type>` 向量 |
| `incx` | | 输入 | `x` 步幅 |
| `y` | device | 输入 | 长度为 `n` 的 `<type>` 向量 |
| `incy` | | 输入 | `y` 步幅 |
| `A` | device | 输入/输出 | 维度 `lda × n` 的 `<type>` 数组，`lda ≥ max(1, n)` |
| `lda` | | 输入 | $A$ 的前导维度 |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_INVALID_VALUE`：`n < 0`、`incx/incy = 0`、`uplo` 非法、`alpha = NULL`、`lda < max(1, n)`。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

### 3.3. Level-3（矩阵-矩阵运算） {#33-level-3矩阵-矩阵运算}

Level-3 BLAS（BLAS3）针对矩阵—矩阵运算。除特别说明外，本节函数遵循以下统一约定：

- **存储** ：所有矩阵以**列优先** 布局存放，前导维度即「整体分配的行数」。
- **`op(M)` 转置选项** ：函数原型里出现的 `transX` 参数控制矩阵 `X` 是否转置，详见下表。

    | 取值 | $\text{op}(X)$ |
    |:--|:--|
    | `ACBLAS_OP_N` | $X$ |
    | `ACBLAS_OP_T` | $X^{\!T}$ |

- **索引基准** ：与 Level-1/2 一致，公式按 1-based 写出。

#### 3.3.1. acblas&lt;t&gt;gemm() {#331-acblaslttgtgemm}

```cpp
acblasStatus_t
acblasSgemm(acblasHandle_t handle,
            acblasOperation_t transa, acblasOperation_t transb,
            int m, int n, int k,
            const float *alpha,
            const float *A, int lda,
            const float *B, int ldb,
            const float *beta,
            float *C, int ldc)
acblasStatus_t
acblasDgemm(acblasHandle_t handle,
            acblasOperation_t transa, acblasOperation_t transb,
            int m, int n, int k,
            const double *alpha,
            const double *A, int lda,
            const double *B, int ldb,
            const double *beta,
            double *C, int ldc)
acblasStatus_t
acblasHgemm(acblasHandle_t handle,
            acblasOperation_t transa, acblasOperation_t transb,
            int m, int n, int k,
            const __half *alpha,
            const __half *A, int lda,
            const __half *B, int ldb,
            const __half *beta,
            __half *C, int ldc)
```

通用矩阵—矩阵乘法（GEMM）：

$$C \gets \alpha \cdot \text{op}(A)\,\text{op}(B) + \beta\,C$$

形状关系：$\text{op}(A) \in \mathbb{R}^{m \times k}$、$\text{op}(B) \in \mathbb{R}^{k \times n}$、$C \in \mathbb{R}^{m \times n}$。`transa`、`transb` 的语义见本节开头。

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle` | | 输入 | acBLAS 上下文 |
| `transa` | | 输入 | `op(A)` 的选择，含义见 `acblasOperation_t`。 |
| `transb` | | 输入 | `op(B)` 的选择，含义见 `acblasOperation_t`。 |
| `m` | | 输入 | `op(A)` 和 C 的行数。 |
| `n` | | 输入 | `op(B)` 和 C 的列数。 |
| `k` | | 输入 | `op(A)` 的列数和 `op(B)` 的行数。 |
| `alpha` | host 或 device | 输入 | `<type>` 用于乘法的标量。 |
| `A` | device | 输入 | `<type>` 维度为 `lda x k` 的数组，若 `transa == ACBLAS_OP_N` 则 `lda>=max(1, m)`，否则 `lda x m` 且 `lda>=max(1, k)`。 |
| `lda` | | 输入 | `A` 的前导维度。 |
| `B` | device | 输入 | `<type>` 维度为 `ldb x n` 的数组，若 `transb == ACBLAS_OP_N` 则 `ldb>=max(1, k)`，否则 `ldb x k` 且 `ldb>=max(1, n)`。 |
| `ldb` | | 输入 | `B` 的前导维度。 |
| `beta` | host 或 device | 输入 | `<type>` 用于乘法的标量。若 `beta==0`，则 C 不必是有效输入。 |
| `C` | device | 输入/输出 | `<type>` 维度为 `ldc x n` 的数组，`ldc>=max(1, m)`。 |
| `ldc` | | 输入 | `C` 的前导维度。 |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_INVALID_VALUE`：`m, n, k < 0 或 transa/transb 不为 ACBLAS_OP_N/C/T 或 lda/ldb/ldc 不满足要求或 alpha/beta = NULL 或 C = NULL(需缩放时)`。
- `ACBLAS_STATUS_ARCH_MISMATCH`：对于 `acblasHgemm()`，设备不支持半精度数学运算。
- `ACBLAS_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 3.3.2. acblas&lt;t&gt;gemmBatched() {#332-acblaslttgtgemmbatched}

```cpp
acblasStatus_t
acblasHgemmBatched(acblasHandle_t handle,
                  acblasOperation_t transa,
                  acblasOperation_t transb,
                  int m, int n, int k,
                  const __half *alpha,
                  const __half * const Aarray[], int lda,
                  const __half * const Barray[], int ldb,
                  const __half *beta,
                  __half * const Carray[], int ldc,
                  int batchCount)
acblasStatus_t
acblasSgemmBatched(acblasHandle_t handle,
                  acblasOperation_t transa,
                  acblasOperation_t transb,
                  int m, int n, int k,
                  const float *alpha,
                  const float * const Aarray[], int lda,
                  const float * const Barray[], int ldb,
                  const float *beta,
                  float * const Carray[], int ldc,
                  int batchCount)
acblasStatus_t
acblasDgemmBatched(acblasHandle_t handle,
                  acblasOperation_t transa,
                  acblasOperation_t transb,
                  int m, int n, int k,
                  const double *alpha,
                  const double * const Aarray[], int lda,
                  const double * const Barray[], int ldb,
                  const double *beta,
                  double * const Carray[], int ldc,
                  int batchCount)
```

`gemm` 的"统一批量"版：一次提交 `batchCount` 个独立的 GEMM 实例，所有实例共享相同的维度 $(m, n, k)$、前导维度 $(\text{lda}, \text{ldb}, \text{ldc})$ 与转置选择 $(\text{transa}, \text{transb})$；每个实例的 $A$、$B$、$C$ 由用户传入的**指针数组** 逐一指明。

$$C[i] \gets \alpha\,\text{op}(A[i])\,\text{op}(B[i]) + \beta\,C[i],\qquad i \in [0,\ \text{batchCount}-1]$$

形状仍是 $\text{op}(A[i]) \in \mathbb{R}^{m \times k}$、$\text{op}(B[i]) \in \mathbb{R}^{k \times n}$、$C[i] \in \mathbb{R}^{m \times n}$；$\text{op}(\cdot)$ 含义 [见 3.3](#33-level-3矩阵-矩阵运算) 节首。

!!! warning
    各 $C[i]$ 占用的内存区域**不得** 互相重叠，即各个 GEMM 必须可独立计算，否则行为未定义。

!!! tip
    对部分问题规模，将多个 `acblas<t>gemm` 派发到不同 HGGC stream 上执行反而更为高效，可以与此 API 实测对比。

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle` | | 输入 | acBLAS 上下文 |
| `transa` | | 输入 | 操作 `op(A[i])`，非转置或转置。 |
| `transb` | | 输入 | 操作 `op(B[i])`，非转置或转置。 |
| `m` | | 输入 | `op(A[i])` 和 `C[i]` 的行数。 |
| `n` | | 输入 | `op(B[i])` 和 `C[i]` 的列数。 |
| `k` | | 输入 | `op(A[i])` 的列数和 `op(B[i])` 的行数。 |
| `alpha` | host 或 device | 输入 | `<type>` 用于乘法的标量。 |
| `Aarray` | device | 输入 | 指向 `<type>` 数组的指针数组，每个数组维度为 `lda x k`，若 `transa==ACBLAS_OP_N` 则 `lda>=max(1, m)`，否则 `lda x m` 且 `lda>=max(1, k)`。所有指针必须满足某些对齐条件。详情请见下文。 |
| `lda` | | 输入 | 每个 `A[i]` 的前导维度。 |
| `Barray` | device | 输入 | 指向 `<type>` 数组的指针数组，每个数组维度为 `ldb x n`，若 `transb==ACBLAS_OP_N` 则 `ldb>=max(1, k)`，否则 `ldb x k` 且 `ldb>=max(1, n)`。所有指针必须满足某些对齐条件。详情请见下文。 |
| `ldb` | | 输入 | 每个 `B[i]` 的前导维度。 |
| `beta` | host 或 device | 输入 | `<type>` 用于乘法的标量。若 `beta == 0`，则 C 不必是有效输入。 |
| `Carray` | device | 输入/输出 | 指向 `<type>` 数组的指针数组。维度为 `ldc x n`，`ldc>=max(1, m)`。矩阵 `C[i]` 不应重叠；否则，预期会出现未定义行为。所有指针必须满足某些对齐条件。详情请见下文。 |
| `ldc` | | 输入 | 每个 `C[i]` 的前导维度。 |
| `batchCount` | | 输入 | Aarray、Barray 和 Carray 中包含的指针数量。 |

若在使用 `acblasSgemmBatched()` 时数学模式启用快速数学模式，则真武 PPU 内存中的指针（非指针数组）必须正确对齐以避免未对齐内存访问错误。理想情况下，所有指针至少对齐到 16 字节，否则建议满足以下规则：

- 若 k%4==0 则确保 intptr_t(ptr) % 16 == 0。

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_INVALID_VALUE`：`若 m, n, k, batchCount < 0 或 transa, transb != ACBLAS_OP_N, ACBLAS_OP_C, ACBLAS_OP_T 或 lda < max(1, m)(若 transa == ACBLAS_OP_N)否则 lda < max(1, k) 或 ldb < max(1, k)(若 transb == ACBLAS_OP_N)否则 ldb < max(1, n) 或 ldc < max(1, m)`。
- `ACBLAS_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。
- `ACBLAS_STATUS_ARCH_MISMATCH`：架构不匹配。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 3.3.3. acblas&lt;t&gt;gemmStridedBatched() {#333-acblaslttgtgemmstridedbatched}

```cpp
acblasStatus_t
acblasHgemmStridedBatched(acblasHandle_t handle,
                          acblasOperation_t transa,
                          acblasOperation_t transb,
                          int m, int n, int k,
                          const __half *alpha,
                          const __half *A, int lda,
                          long long int strideA,
                          const __half *B, int ldb,
                          long long int strideB,
                          const __half *beta,
                          __half *C, int ldc,
                          long long int strideC,
                          int batchCount)
acblasStatus_t
acblasSgemmStridedBatched(acblasHandle_t handle,
                          acblasOperation_t transa,
                          acblasOperation_t transb,
                          int m, int n, int k,
                          const float *alpha,
                          const float *A, int lda,
                          long long int strideA,
                          const float *B, int ldb,
                          long long int strideB,
                          const float *beta,
                          float *C, int ldc,
                          long long int strideC,
                          int batchCount)
acblasStatus_t
acblasDgemmStridedBatched(acblasHandle_t handle,
                          acblasOperation_t transa,
                          acblasOperation_t transb,
                          int m, int n, int k,
                          const double *alpha,
                          const double *A, int lda,
                          long long int strideA,
                          const double *B, int ldb,
                          long long int strideB,
                          const double *beta,
                          double *C, int ldc,
                          long long int strideC,
                          int batchCount)
```

`gemmBatched` 的"等距步进"版本。它取代指针数组，改用单个起点指针加固定元素步幅 (`strideA`、`strideB`、`strideC`) 推算出每个实例的 $A$、$B$、$C$ 位置：

$$C + i\cdot\text{strideC} \;\gets\; \alpha\,\text{op}(A + i\cdot\text{strideA})\,\text{op}(B + i\cdot\text{strideB}) + \beta\,(C + i\cdot\text{strideC}),\qquad i \in [0,\ \text{batchCount}-1]$$

各实例统一具有维度 $(m, n, k)$、前导维度 $(\text{lda}, \text{ldb}, \text{ldc})$ 和转置选择 $(\text{transa}, \text{transb})$；$\text{op}(\cdot)$ 含义 [见 3.3](#33-level-3矩阵-矩阵运算) 节首；形状关系同 `gemmBatched`。

!!! warning
    各 $C[i]$ 不得相互重叠（同 `gemmBatched`）。

!!! tip
    对某些问题规模，把多个 `acblas<t>gemm` 派发到不同 HGGC stream 反而更优，建议实测对比。

!!! note
    后续表格用 $A[i]$、$B[i]$、$C[i]$ 简记每个批次实例的矩阵。它们隐式相对前一实例偏移 `strideA`、`strideB`、`strideC` 个元素。偏移以元素为单位，**必须非零** 。

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle` | | 输入 | acBLAS 上下文 |
| `transa` | | 输入 | 操作 `op(A[i])`，非转置或转置。 |
| `transb` | | 输入 | 操作 `op(B[i])`，非转置或转置。 |
| `m` | | 输入 | `op(A[i])` 和 `C[i]` 的行数。 |
| `n` | | 输入 | `op(B[i])` 和 `C[i]` 的列数。 |
| `k` | | 输入 | `op(A[i])` 的列数和 `op(B[i])` 的行数。 |
| `alpha` | host 或 device | 输入 | `<type>` 用于乘法的标量。 |
| `A` | device | 输入 | `<type>` 指针，指向对应于批次第一个实例的 A 矩阵的指针，维度为 `lda x k`，若 `transa==ACBLAS_OP_N` 则 `lda>=max(1, m)`，否则 `lda x m` 且 `lda>=max(1, k)`。 |
| `lda` | | 输入 | 每个 `A[i]` 的前导维度。 |
| `strideA` | | 输入 | `long long int` 类型值，表示 `A[i]` 和 `A[i+1]` 之间的元素偏移量。 |
| `B` | device | 输入 | `<type>` 指针，指向批次第一个实例的 B 矩阵指针，维度为 `ldb x n`，若 `transb==ACBLAS_OP_N` 则 `ldb>=max(1, k)`，否则 `ldb x k` 且 `ldb>=max(1, n)`。 |
| `ldb` | | 输入 | 每个 `B[i]` 的前导维度。 |
| `strideB` | | 输入 | `long long int` 类型值，表示 `B[i]` 和 `B[i+1]` 之间的元素偏移量。 |
| `beta` | host 或 device | 输入 | `<type>` 用于乘法的标量。若 `beta == 0`，则 C 不必是有效输入。 |
| `C` | device | 输入/输出 | `<type>` 指针，指向对应于批次第一个实例的 C 矩阵的指针，维度为 `ldc x n`，`ldc>=max(1, m)`。矩阵 `C[i]` 不应重叠；否则，预期会出现未定义行为。 |
| `ldc` | | 输入 | 每个 `C[i]` 的前导维度。 |
| `strideC` | | 输入 | `long long int` 类型值，表示 `C[i]` 和 `C[i+1]` 之间的元素偏移量。 |
| `batchCount` | | 输入 | 批次中要执行的 GEMM 数量。 |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_INVALID_VALUE`：`若 m, n, k, batchCount < 0 或 transa, transb != ACBLAS_OP_N, ACBLAS_OP_C, ACBLAS_OP_T 或 lda < max(1, m)(若 transa == ACBLAS_OP_N)否则 lda < max(1, k) 或 ldb < max(1, k)(若 transb == ACBLAS_OP_N)否则 ldb < max(1, n) 或 ldc < max(1, m)`。
- `ACBLAS_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。
- `ACBLAS_STATUS_ARCH_MISMATCH`：架构不匹配。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 3.3.4. acblas&lt;t&gt;trsm() {#334-acblaslttgttrsm}

```cpp
acblasStatus_t
acblasStrsm(acblasHandle_t handle,
            acblasSideMode_t side, acblasFillMode_t uplo,
            acblasOperation_t trans, acblasDiagType_t diag,
            int m, int n,
            const float *alpha,
            const float *A, int lda,
            float *B, int ldb)
acblasStatus_t
acblasDtrsm(acblasHandle_t handle,
            acblasSideMode_t side, acblasFillMode_t uplo,
            acblasOperation_t trans, acblasDiagType_t diag,
            int m, int n,
            const double *alpha,
            const double *A, int lda,
            double *B, int ldb)
```

求解带多右侧项的三角线性系统，`side` 决定 $A$ 出现在 $X$ 的哪一侧：

$$
\begin{cases}
\text{op}(A)\,X = \alpha\,B & \texttt{side} = \texttt{ACBLAS\_SIDE\_LEFT} \\
X\,\text{op}(A) = \alpha\,B & \texttt{side} = \texttt{ACBLAS\_SIDE\_RIGHT}
\end{cases}
$$

$A$ 是上/下三角矩阵（含或不含单位对角），$X$、$B$ 都是 $m \times n$ 矩阵，$\alpha$ 是标量。$\text{op}(A)$ 的取值由 `trans` 决定，含义同 3.3 节首。函数返回时，**解 $X$ 原地写回 $B$** 。

!!! warning
    本函数不做奇异 / 近奇异性检测，需要时由调用方自行处理。

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle` | | 输入 | acBLAS 上下文 |
| `side` | | 输入 | 指示矩阵 A 是在 X 的左侧还是右侧。 |
| `uplo` | | 输入 | 指示矩阵 A 的下部或上部已存储，不引用另一部分，由存储的元素推断。 |
| `trans` | | 输入 | `op(A)` 的选择，含义见 `acblasOperation_t`。 |
| `diag` | | 输入 | 指示矩阵 A 主对角线上的元素是否为单位 1 且不应访问。 |
| `m` | | 输入 | 矩阵 B 的行数，矩阵 A 的尺寸相应确定。 |
| `n` | | 输入 | 矩阵 B 的列数，矩阵 A 的尺寸相应确定。 |
| `alpha` | host 或 device | 输入 | `<type>` 用于乘法的标量，若 `alpha==0` 则不引用 A 且 B 不必是有效输入。 |
| `A` | device | 输入 | `<type>` 维度为 `lda x m` 的数组，若 `side == ACBLAS_SIDE_LEFT` 则 `lda>=max(1, m)`，否则 `lda x n` 且 `lda>=max(1, n)`。 |
| `lda` | | 输入 | `A` 的前导维度。 |
| `B` | device | 输入/输出 | `<type>` 数组。维度为 `ldb x n`，`ldb>=max(1, m)`。 |
| `ldb` | | 输入 | `B` 的前导维度。 |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_INVALID_VALUE`：`若 m < 0 或 n < 0 或 trans != ACBLAS_OP_N, ACBLAS_OP_C, ACBLAS_OP_T 或 uplo != ACBLAS_FILL_MODE_LOWER, ACBLAS_FILL_MODE_UPPER 或 side != ACBLAS_SIDE_LEFT, ACBLAS_SIDE_RIGHT 或 diag != ACBLAS_DIAG_NON_UNIT, ACBLAS_DIAG_UNIT 或 lda < max(1, m)(若 side == ACBLAS_SIDE_LEFT)否则 lda < max(1, n) 或 ldb < max(1, m) 或 alpha == NULL`。
- `ACBLAS_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 3.3.5. acblas&lt;t&gt;trsmBatched() {#335-acblaslttgttrsmbatched}

```cpp
acblasStatus_t
acblasStrsmBatched(acblasHandle_t handle,
                   acblasSideMode_t side,
                   acblasFillMode_t uplo,
                   acblasOperation_t trans,
                   acblasDiagType_t diag,
                   int m,
                   int n,
                   const float *alpha,
                   const float* const A[],
                   int lda,
                   float * const B[],
                   int ldb,
                   int batchCount);
acblasStatus_t
acblasDtrsmBatched(acblasHandle_t handle,
                   acblasSideMode_t side,
                   acblasFillMode_t uplo,
                   acblasOperation_t trans,
                   acblasDiagType_t diag,
                   int m,
                   int n,
                   const double *alpha,
                   const double * const A[],
                   int lda,
                   double * const B[],
                   int ldb,
                   int batchCount);
```

`trsm` 的批量版：一次求解 `batchCount` 组结构相同的三角线性系统，每组各自独立：

$$
\begin{cases}
\text{op}(A[i])\,X[i] = \alpha\,B[i] & \texttt{side} = \texttt{ACBLAS\_SIDE\_LEFT} \\
X[i]\,\text{op}(A[i]) = \alpha\,B[i] & \texttt{side} = \texttt{ACBLAS\_SIDE\_RIGHT}
\end{cases}
$$

各 $A[i]$ 为上/下三角矩阵（含或不含单位对角），$X[i]$、$B[i]$ 为 $m \times n$ 矩阵，$\alpha$ 为标量；$\text{op}(\cdot)$ 含义 [见 3.3](#33-level-3矩阵-矩阵运算) 节首。函数返回时 $X[i]$ 写回到 $B[i]$。

!!! warning
    不做奇异 / 近奇异性检测。

!!! tip
    此 API 主要为「小矩阵 + 启动开销显著」的场景设计；当矩阵较大时，将 `batchCount` 次 `trsm` 派发到一组 stream 上反而更为高效。

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle` | | 输入 | acBLAS 上下文 |
| `side` | | 输入 | 指示矩阵 A[i] 位于方程左侧还是右侧。 |
| `uplo` | | 输入 | 指示矩阵 A[i] 存储的是上三角还是下三角部分，不引用未存储部分，但可从对称性推断。 |
| `trans` | | 输入 | 对 A[i] 执行的操作 `op(A[i])`，可选非转置或转置。 |
| `diag` | | 输入 | 指示矩阵 A[i] 的主对角线元素是否为单位 1，若是则不应访问这些元素。 |
| `m` | | 输入 | 矩阵 B[i] 的行数，矩阵 A[i] 的维度据此确定。 |
| `n` | | 输入 | 矩阵 B[i] 的列数，矩阵 A[i] 的维度据此确定。 |
| `alpha` | host 或 device | 输入 | 用于乘法的 `<type>` 标量。若 `alpha==0`，则不引用 A[i]，B[i] 也不必是有效输入。 |
| `A` | device | 输入 | 指向 `<type>` 数组的指针数组。若 `side == ACBLAS_SIDE_LEFT`，各数组维度为 `lda x m`（`lda >= max(1,m)`）；否则为 `lda x n`（`lda >= max(1,n)`）。 |
| `lda` | | 输入 | 存储矩阵 A[i] 的二维数组的前导维度。 |
| `B` | device | 输入/输出 | 指向 `<type>` 数组的指针数组，各数组维度为 `ldb x n`（`ldb >= max(1,m)`）。矩阵 B[i] 间不应重叠，否则行为未定义。 |
| `ldb` | | 输入 | 存储矩阵 B[i] 的二维数组的前导维度。 |
| `batchCount` | | 输入 | A 和 B 中包含的指针数量。 |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_INVALID_VALUE`：`若 m < 0 或 n < 0 或 batchCount < 0 或 trans 不为 ACBLAS_OP_N/C/T 或 uplo 不为 ACBLAS_FILL_MODE_LOWER/UPPER 或 side 不为 ACBLAS_SIDE_LEFT/RIGHT 或 diag 不为 ACBLAS_DIAG_NON_UNIT/UNIT 或若 side == ACBLAS_SIDE_LEFT 则 lda < max(1, m) 否则 lda < max(1, n) 或 ldb < max(1, m)`。
- `ACBLAS_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

## 4. BLAS 扩展 {#4-blas-扩展}

### 4.1. 矩阵运算扩展 {#41-矩阵运算扩展}

#### 4.1.1. acblas&lt;t&gt;geam() {#411-acblaslttgtgeam}

```cpp
acblasStatus_t
acblasSgeam(acblasHandle_t handle,
            acblasOperation_t transa, acblasOperation_t transb,
            int m, int n,
            const float *alpha,
            const float *A, int lda,
            const float *beta,
            const float *B, int ldb,
            float *C, int ldc)
acblasStatus_t
acblasDgeam(acblasHandle_t handle,
            acblasOperation_t transa, acblasOperation_t transb,
            int m, int n,
            const double *alpha,
            const double *A, int lda,
            const double *beta,
            const double *B, int ldb,
            double *C, int ldc)
```

在矩阵层面做加权和（含可选转置）：

$$C \gets \alpha\,\text{op}(A) + \beta\,\text{op}(B)$$

$\text{op}(\cdot)$ 含义 [见 3.3](#33-level-3矩阵-矩阵运算) 节首。$A$、$B$、$C$ 列优先存储，$\alpha$、$\beta$ 为标量。

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle` | | 输入 | acBLAS 上下文 |
| `transa` | | 输入 | 对矩阵 A 执行的操作 `op(A)`，可以是非转置或转置。 |
| `transb` | | 输入 | 对矩阵 B 执行的操作 `op(B)`，可以是非转置或转置。 |
| `m` | | 输入 | 矩阵 `op(A)` 和 `op(B)` 的行数。 |
| `n` | | 输入 | 矩阵 `op(A)` 和 `op(B)` 的列数。 |
| `alpha` | host 或 device | 输入 | 用于乘法的 `<type>` 标量。 |
| `A` | device | 输入 | `<type>` 数组，维度为 `lda x n` (若 transa==ACBLAS_OP_N) 或 `lda x m` (否则)。 |
| `lda` | | 输入 | `A` 的前导维度。 |
| `beta` | host 或 device | 输入 | 用于乘法的 `<type>` 标量。 |
| `B` | device | 输入 | `<type>` 数组，维度为 `ldb x n` (若 transb==ACBLAS_OP_N) 或 `ldb x m` (否则)。 |
| `ldb` | | 输入 | `B` 的前导维度。 |
| `C` | device | 输入/输出 | `<type>` 数组，维度为 `ldc x n`。 |
| `ldc` | | 输入 | `C` 的前导维度。 |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_INVALID_VALUE`：`若 m < 0 或 n < 0 或 transa != ACBLAS_OP_N, ACBLAS_OP_C, ACBLAS_OP_T 或 transb != ACBLAS_OP_N, ACBLAS_OP_C, ACBLAS_OP_T 或 lda < max(1, m)(若 transa == ACBLAS_OP_N)否则 lda < max(1, n) 或 ldb < max(1, m)(若 transb == ACBLAS_OP_N)否则 ldb < max(1, n) 或 ldc < max(1, m) 或 A == C 且 ((ACBLAS_OP_N != transa))`。
- `ACBLAS_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

### 4.2. 批处理线性方程组求解 {#42-批处理线性方程组求解}

以下函数以批处理方式实现 LU 分解、三角求解、求逆、QR 分解和最小二乘等线性代数操作。

#### 4.2.1. acblas&lt;t&gt;getrfBatched() {#421-acblaslttgtgetrfbatched}

```cpp
acblasStatus_t
acblasSgetrfBatched(acblasHandle_t handle,
                    int n,
                    float * const Aarray[],
                    int lda,
                    int *PivotArray,
                    int *infoArray,
                    int batchSize);
acblasStatus_t
acblasDgetrfBatched(acblasHandle_t handle,
                    int n,
                    double * const Aarray[],
                    int lda,
                    int *PivotArray,
                    int *infoArray,
                    int batchSize);
```

Aarray 是以列优先格式存储的矩阵指针数组，维度为 n×n，前导维度为 lda。
对每个 Aarray[i]（i = 0, …， batchSize-1）执行 LU 分解：
$$
P \cdot A_{\text{array}}[i] = L \cdot U
$$

其中 $P$ 是表示部分主元选择中行交换的置换矩阵。$L$ 是单位下三角矩阵，$U$ 是上三角矩阵。

形式上，$P$ 可写为置换矩阵 $P_j$（$j = 1, 2, \dots, n$）的乘积，即 $P = P_1 * P_2 * P_3 * \dots * P_n$。$P_j$ 是执行 $P_j \cdot \mathbf{x}$ 时交换向量 $\mathbf{x}$ 两行的置换矩阵。可通过 `PivotArray[i]` 的第 $j$ 个元素按以下 Matlab 代码构造 $P_j$：

```text
% 在 Matlab 中 PivotArray[i] 是基于1的数组。
% 在 C 中，PivotArray[i] 是基于0的。
Pj = eye(n);
swap Pj(j,:) and Pj(PivotArray[i][j], :)
```

L 和 U 写回原始矩阵 A，丢弃 L 的对角线元素。可通过以下 Matlab 代码重构 L 和 U：
```text
% A 是 getrf 之后的 nxn 矩阵。
L = eye(n);
for j = 1:n
    L(j+1:n, j) = A(j+1:n, j)
end
U = zeros(n);
for i = 1:n
    U(i, i:n) = A(i, i:n)
end
```

若矩阵 A(=Aarray[i]) 奇异，getrf 仍可正常执行，info(=infoArray[i]) 的值报告 LU 分解无法继续的首个行索引。若 info 为 k，则 U(k,k) 为零。方程 P*A=L*U 仍成立，但重构 L 和 U 需要不同的 Matlab 代码，如下所示：
```text
% A 是 getrf 之后的 nxn 矩阵。
% info 是 k，表示 U(k,k) 为零。
L = eye(n);
for j = 1:k-1
    L(j+1:n, j) = A(j+1:n, j)
end
U = zeros(n);
for i = 1:k-1
    U(i, i:n) = A(i, i:n)
end
for i = k:n
    U(i, k:n) = A(i, k:n)
end
```

专为小尺寸矩阵设计，启动开销在小矩阵上更为显著。

若 PivotArray 为 NULL，`acblas<t>getrfBatched` 支持无主元的 LU 分解。

`acblas<t>getrfBatched` 支持任意维度。

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle`     |        | 输入  | acBLAS 上下文。                                      |
| `n`          |        | 输入  | 矩阵 `Aarray[i]` 的行数和列数。                              |
| `Aarray`     | device | 输入/输出 | 指向 `<type>` 数组的指针数组。 每个数组的维度为 `n x n` (其中 `lda >= max(1, n)`)。 矩阵 `Aarray[i]` 之间不应重叠，否则行为未定义。 |
| `lda`        |        | 输入  | 每个 `Aarray[i]` 的前导维度。          |
| `PivotArray` | device | 输出 | 大小为 `n x batchSize` 的数组，以线性方式存储了每个 `Aarray[i]` 分解的主元序列。 若 `PivotArray` 为 NULL，则禁用主元选择。 |
| `infoArray`  | device | 输出 | 大小为 `batchSize` 的数组，其中 `info(=infoArray[i])` 包含了 `Aarray[i]` 分解的信息。 •**info = 0**： 执行成功。 •**info = -j**： 第 j 个参数值非法。 •**info = k**： U(k,k) 为 0。分解已完成，但 U 是奇异矩阵。 |
| `batchSize`  |        | 输入  | `Aarray` 中包含的指针数量。                                  |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_INVALID_VALUE`：`参数 n, batchSize, lda < 0`。
- `ACBLAS_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 4.2.2. acblas&lt;t&gt;getrsBatched() {#422-acblaslttgtgetrsbatched}

```cpp
acblasStatus_t
acblasSgetrsBatched(acblasHandle_t handle,
                    acblasOperation_t trans,
                    int n,
                    int nrhs,
                    const float* const Aarray[],
                    int lda,
                    const int *devIpiv,
                    float * const Barray[],
                    int ldb,
                    int *info,
                    int batchSize);

acblasStatus_t
acblasDgetrsBatched(acblasHandle_t handle,
                    acblasOperation_t trans,
                    int n,
                    int nrhs,
                    const double * const Aarray[],
                    int lda,
                    const int *devIpiv,
                    double * const Barray[],
                    int ldb,
                    int *info,
                    int batchSize);
```

求解以下形式的线性方程组数组：

$$
\text{op}(A[i]) X[i] = B[i]
$$

其中 $A[i]$ 是已经过带主元选择的 LU 分解的矩阵，$X[i]$ 和 $B[i]$ 是 $n \times \text{nrhs}$ 矩阵。

此外，对于矩阵 $A$：

$$
\text{op}(A[i]) =
\begin{cases}
A[i]      & \text{若 } \texttt{trans} == \texttt{ACBLAS\_OP\_N} \\
A^T[i]    & \text{若 } \texttt{trans} == \texttt{ACBLAS\_OP\_T} \\
A^H[i]    & \text{若 } \texttt{trans} == \texttt{ACBLAS\_OP\_C}
\end{cases}
$$

专为小尺寸矩阵设计，启动开销在小矩阵上更为显著。

> `acblas<t>getrsBatched` 若 `devIpiv` 为 NULL，则支持无主元选择的 LU 分解。
> `acblas<t>getrsBatched` 支持任意维度。

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle`    |        | 输入        | acBLAS 上下文。                        |
| `trans`     |        | 输入        | op(`A`) 的选择，含义见 `acblasOperation_t`。         |
| `n`         |        | 输入        | `Aarray[i]` 的行数和列数。                   |
| `nrhs`      |        | 输入        | `Barray[i]` 的列数。                            |
| `Aarray`    | device | 输入        | 指向 `<type>` 数组的指针数组，每个数组维度为 `n x n`，`lda>=max(1, n)`。 |
| `lda`       |        | 输入        | 每个 `Aarray[i]` 的前导维度。 |
| `devIpiv`   | device | 输入        | 大小为 `n x batchSize` 的数组，以线性方式存储每个 `Aarray[i]` 分解的主元序列。若 `devIpiv` 为 NULL，则忽略所有 `Aarray[i]` 的主元选择。 |
| `Barray`    | device | 输入/输出 | 指向 `<type>` 数组的指针数组，每个数组维度为 `n x nrhs`，`ldb>=max(1, n)`。矩阵 `Barray[i]` 不应重叠；否则，预期会出现未定义行为。 |
| `ldb`       |        | 输入        | 用于存储每个解矩阵 `Barray[i]` 的二维数组的前导维度。 |
| `info`      | host   | 输出       | 若 info=0，执行成功。若 info = -j，第 j 个参数值非法。 |
| `batchSize` |        | 输入        | A 中包含的指针数量                            |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_INVALID_VALUE`：`若 n < 0 或 nrhs < 0 或 trans != ACBLAS_OP_N, ACBLAS_OP_C, ACBLAS_OP_T 或 lda < max(1, n) 或 ldb < max(1, n)`。
- `ACBLAS_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 4.2.3. acblasSgetriBatched() {#423-acblassgetribatched}

```cpp
acblasStatus_t
acblasSgetriBatched(acblasHandle_t handle,
                    int n,
                    const float* const Aarray[],
                    int lda,
                    const int *PivotArray,
                    float * const Carray[],
                    int ldc,
                    int *infoArray,
                    int batchSize);
```

!!! note
    当前仅提供单精度（`S`）版本，无双精度（`D`）变体。

Aarray 和 Carray 是以列优先格式存储的矩阵指针数组，维度为 n×n，前导维度分别为 lda 和 ldc。

对矩阵 A[i]（i = 0, …， batchSize-1）执行求逆运算。
在调用 `acblasSgetriBatched` 之前，必须先用 `acblasSgetrfBatched` 对矩阵 A[i] 进行分解。调用 `acblasSgetrfBatched` 后，Aarray[i] 指向的矩阵将包含 A[i] 的 LU 因子，(PivotArray+i) 指向的向量将包含主元序列。

LU 分解完成后，`acblasSgetriBatched` 使用前向和后向三角求解器完成对矩阵 A[i]（i = 0, …， batchSize-1）的求逆。求逆为异址操作，因此 Carray[i] 的内存空间不可与 Aarray[i] 的内存空间重叠。

通常，`acblasSgetrfBatched` 的所有参数都会传递给 `acblasSgetriBatched`。例如：
```cpp
// 步骤 1：执行原地 LU 分解，P*A = L*U。
//         Aarray[i] 是 n×n 矩阵 A[i]
    acblasSgetrfBatched(handle, n, Aarray, lda, PivotArray, infoArray, batchSize);
//         检查 infoArray[i] 以查看 A[i] 的分解是否成功。
//         Aarray[i] 包含 A[i] 的 LU 分解

// 步骤 2：执行异址求逆，Carray[i] = inv(A[i])
    acblasSgetriBatched(handle, n, Aarray, lda, PivotArray, Carray, ldc, infoArray,
                        batchSize);
//         检查 infoArray[i] 以查看 A[i] 的求逆是否成功。

```

开发者可通过 `acblasSgetrfBatched` 或 `acblasSgetriBatched` 检测奇异性。
专为小尺寸设计，启动开销在小矩阵上更为显著。
若 `acblasSgetrfBatched` 以无主元方式执行，则 `acblasSgetriBatched` 的 PivotArray 应为 NULL。
`acblasSgetriBatched` 支持任意维度。

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle`     |        | 输入  | acBLAS 上下文。                        |
| `n`          |        | 输入  | `Aarray[i]` 的行数和列数。                   |
| `Aarray`     | device | 输入  | 指向 `<type>` 数组的指针数组，每个数组维度为 `n×n`，`lda>=max(1, n)`。 |
| `lda`        |        | 输入  | 每个 `Aarray[i]` 的前导维度。 |
| `PivotArray` | device | 输出 | 大小为 `n*batchSize` 的数组，以线性方式存储每个 `Aarray[i]` 分解的主元序列。若 `PivotArray` 为 NULL，则禁用主元选择。 |
| `Carray`     | device | 输出 | 指向 `<type>` 数组的指针数组，每个数组维度为 `n×n`，`ldc>=max(1, n)`。矩阵 `Carray[i]` 不应重叠；否则，预期会出现未定义行为。 |
| `ldc`        |        | 输入  | 每个 `Carray[i]` 的前导维度。 |
| `infoArray`  | device | 输出 | 大小为 `batchSize` 的数组，info(=infoArray[i]) 包含 `A[i]` 求逆的信息。若 info=0，执行成功。若 info = k，U(k,k) 为 0。U 是完全奇异的，求逆失败。 |
| `batchSize`  |        | 输入  | A 中包含的指针数量                            |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_INVALID_VALUE`：`若 n < 0 或 lda < 0 或 ldc < 0 或 batchSize < 0 或 lda < n 或 ldc < n`。
- `ACBLAS_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 4.2.4. acblas&lt;t&gt;geqrfBatched() {#424-acblaslttgtgeqrfbatched}

```cpp
acblasStatus_t
acblasSgeqrfBatched(acblasHandle_t handle,
                    int m,
                    int n,
                    float * const Aarray[],
                    int lda,
                    float * const TauArray[],
                    int *info,
                    int batchSize);
acblasStatus_t
acblasDgeqrfBatched(acblasHandle_t handle,
                    int m,
                    int n,
                    double * const Aarray[],
                    int lda,
                    double * const TauArray[],
                    int *info,
                    int batchSize);
```

Aarray 是以列优先格式存储的矩阵指针数组，维度为 m×n，前导维度为 lda。TauArray 是向量指针数组，各向量维度至少为 max(1, min(m, n))。
使用 Householder 反射对每个 Aarray[i]（i = 0, ...,batchSize-1）执行 QR 分解。每个矩阵 Q[i] 可表示为基本反射器的乘积，并存储于各 Aarray[i] 的下三角部分，如下所示：

$Q[j] = H[j][1]\,H[j][2] \dots H[j][k]$，其中 $k = \min(m,n)$。

每个 $H[j][i]$ 具有以下形式：

$H[j][i] = I - tau[j] * v * v'$

其中 tau[j] 为实标量，v 为实向量，v(1:i-1) = 0 且 v(i) = 1；v(i+1:m) 函数返回时存储于 Aarray[j][i+1:m,i] 中，tau 存储于 TauArray[j][i] 中。
专为小尺寸矩阵设计，启动开销在小矩阵上更为显著。

`acblas<t>geqrfBatched` 支持任意维度。

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle`    |        | 输入  | acBLAS 上下文。                        |
| `m`         |        | 输入  | `Aarray[i]` 的行数。                                  |
| `n`         |        | 输入  | `Aarray[i]` 的列数。                            |
| `Aarray`    | device | 输入  | 指向 `<type>` 数组的指针数组，每个数组维度为 `m×n`，`lda>=max(1, m)`。 |
| `lda`       |        | 输入  | 每个 `Aarray[i]` 的前导维度。 |
| `TauArray`  | device | 输出 | 指向 `<type>` 向量的指针数组，每个向量维度为 `max(1,min(m,n))`。 |
| `info`      | host   | 输出 | 若 info=0，传递给函数的参数有效。若 info<0，位置 -info 处的参数无效。 |
| `batchSize` |        | 输入  | A 中包含的指针数量                            |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_INVALID_VALUE`：`若 m < 0 或 n < 0 或 batchSize < 0 或 lda < max(1, m)`。
- `ACBLAS_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 4.2.5. acblas&lt;t&gt;gelsBatched() {#425-acblaslttgtgelsbatched}

```cpp
acblasStatus_t
acblasSgelsBatched(acblasHandle_t handle,
                    acblasOperation_t trans,
                    int m,
                    int n,
                    int nrhs,
                    float * const Aarray[],
                    int lda,
                    float * const Carray[],
                    int ldc,
                    int *info,
                    int *devInfoArray,
                    int batchSize );

acblasStatus_t
acblasDgelsBatched(acblasHandle_t handle,
                    acblasOperation_t trans,
                    int m,
                    int n,
                    int nrhs,
                    double * const Aarray[],
                    int lda,
                    double * const Carray[],
                    int ldc,
                    int *info,
                    int *devInfoArray,
                    int batchSize );
```

Aarray 是以列优先格式存储的矩阵指针数组。Carray 是以列优先格式存储的矩阵指针数组。

求解一批超定系统的最小二乘解：对每个 i = 0, ...,batchSize-1，求解如下最小二乘问题：

最小化 `|| Carray[i] - Aarray[i]*Xarray[i] ||`

函数返回时，每个 Aarray[i] 被其 QR 分解覆盖，每个 Carray[i] 被最小二乘解覆盖。

仅支持非转置操作，且仅求解超定系统 (m >= n)。

专为小尺寸矩阵设计，启动开销在小矩阵上更为显著。

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `handle`       |        | 输入        | acBLAS 上下文。                        |
| `trans`        |        | 输入        | 操作 op(`Aarray[i]`)，非转置或转置。目前仅支持非转置操作。 |
| `m`            |        | 输入        | 若 `trans == ACBLAS_OP_N`，则为每个 `Aarray[i]` 和 `Carray[i]` 的行数，否则为每个 `Aarray[i]` 的列数（目前不支持）。 |
| `n`            |        | 输入        | 若 `trans == ACBLAS_OP_N`，则为每个 `Aarray[i]` 的列数，否则为每个 `Aarray[i]` 和 `Carray[i]` 的行数（目前不支持）。 |
| `nrhs`         |        | 输入        | 每个 `Carray[i]` 的列数。                       |
| `Aarray`       | device | 输入/输出 | 指向 `<type>` 数组的指针数组，若 `trans == ACBLAS_OP_N`，则每个数组维度为 `m×n`，`lda>=max(1, m)`，否则为 `n x m`，`lda>=max(1, n)`（目前不支持）。矩阵 `Aarray[i]` 不应重叠；否则，预期会出现未定义行为。 |
| `lda`          |        | 输入        | 每个 `Aarray[i]` 的前导维度。 |
| `Carray`       | device | 输入/输出 | 指向 `<type>` 数组的指针数组，若 `trans == ACBLAS_OP_N`，则每个数组维度为 `m×nrhs`，`ldc>=max(1, m)`，否则为 `n x nrhs`，`ldc>=max(1, n)`（目前不支持）。矩阵 `Carray[i]` 不应重叠；否则，预期会出现未定义行为。 |
| `ldc`          |        | 输入        | 每个 `Carray[i]` 的前导维度。 |
| `info`         | host   | 输出       | 若 info=0，传递给函数的参数有效。若 info<0，位置 -info 处的参数无效。 |
| `devInfoArray` | device | 输出       | 可选的 batchSize 维整数数组。若非空，每个元素 devInfoArray[i] 包含一个值 V，含义如下：V = 0：第 i 个问题成功求解；V > 0：Aarray[i] 的第 V 个对角元素为零。Aarray[i] 没有满秩。 |
| `batchSize`    |        | 输入        | Aarray 和 Carray 中包含的指针数量            |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_INVALID_VALUE`：`若 m < 0、n < 0、nrhs < 0、batchSize < 0、lda < max(1, m) 或 ldc < max(1, m)`。
- `ACBLAS_STATUS_NOT_SUPPORTED`：参数 `m < n`，或 `trans` 不是"非转置"。
- `ACBLAS_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

### 4.3. 混合精度 GEMM {#43-混合精度-gemm}

支持不同精度输入/输出组合的矩阵乘法函数。

#### 4.3.1. acblasSgemmEx() {#431-acblassgemmex}

```cpp
acblasStatus_t
acblasSgemmEx(acblasHandle_t handle,
                acblasOperation_t transa,
                acblasOperation_t transb,
                int m,
                int n,
                int k,
                const float *alpha,
                const void *A,
                hggcDataType Atype,
                int lda,
                const void *B,
                hggcDataType Btype,
                int ldb,
                const float *beta,
                void *C,
                hggcDataType Ctype,
                int ldc)
```

`acblas<t>gemm` 的混精扩展版：`A` / `B` / `C` 允许各自带不同的低精度数据类型（通过 `Atype`、`Btype`、`Ctype` 指定），但**累加仍按 `float` 精度** 进行。计算式与 `gemm` 完全一致：

$$C \leftarrow \alpha\,\text{op}(A)\cdot\text{op}(B) + \beta\,C$$

| 元素 | 形状 | 说明 |
| :--- | :--- | :--- |
| $\text{op}(A)$ | $m\times k$ | `transa` 选 `OP_N`/`OP_T`/`OP_C` 分别对应 $A$、$A^{T}$、$A^{H}$ |
| $\text{op}(B)$ | $k\times n$ | 同上，由 `transb` 决定 |
| $C$ | $m\times n$ | 列优先 |

`Atype` / `Btype` / `Ctype` 当前允许的组合：

| `Ctype` | `Atype` 与 `Btype` 允许取值 |
| :--- | :--- |
| `HGGC_R_16BF` | `HGGC_R_16BF` |
| `HGGC_R_16F`  | `HGGC_R_16F` |
| `HGGC_R_32F`  | `HGGC_R_8I` / `HGGC_R_16BF` / `HGGC_R_16F` / `HGGC_R_32F` |

**参数清单** （带 *device* 标记的指针指向真武 PPU 端内存；其他不带标记的均为按值传入的 host 端整数 / 枚举）：

- `handle`：acBLAS 上下文。
- `transa` / `transb`：选择 op(`A`) / op(`B`)，详见 `acblasOperation_t`。
- `m`、`n`、`k`：op(`A`) 行 / op(`B`) 列 / 公共维度。
- `alpha`、`beta`（host 或 device）：标量；`beta == 0` 时 `C` 可不必为有效输入。
- `A`（device）`Atype`、`lda`：op(`A`) 的存储起点、元素类型与前导维度。形状视 `transa`：`OP_N` 时按 `lda × k` 存（`lda ≥ max(1, m)`），否则 `lda × m`（`lda ≥ max(1, k)`）。
- `B`（device）`Btype`、`ldb`：同理，由 `transb` 决定形状。
- `C`（device）`Ctype`、`ldc`：输出矩阵；形状固定为 `ldc × n`，`ldc ≥ max(1, m)`。

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_ARCH_MISMATCH`：设备不支持所需硬件特性。
- `ACBLAS_STATUS_NOT_SUPPORTED`：`Atype`/`Btype`/`Ctype` 组合不在上表。
- `ACBLAS_STATUS_INVALID_VALUE`：`m`/`n`/`k` < 0，或 `lda`/`ldb`/`ldc` 不满足上文约束，或 `transa`/`transb` 不在合法枚举内。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

> 不同 GEMM 内部算法在数值上的细微差异，[参见 2.4](#24-数学模式与精度控制)。

#### 4.3.2. acblasGemmEx() {#432-acblasgemmex}

```cpp
acblasStatus_t
acblasGemmEx(acblasHandle_t handle,
            acblasOperation_t transa,
            acblasOperation_t transb,
            int m,
            int n,
            int k,
            const void *alpha,
            const void *A,
            hggcDataType Atype,
            int lda,
            const void *B,
            hggcDataType Btype,
            int ldb,
            const void *beta,
            void *C,
            hggcDataType Ctype,
            int ldc,
            acblasComputeType_t computeType,
            acblasGemmAlgo_t algo)

#if defined(__cplusplus)
acblasStatus_t
acblasGemmEx(acblasHandle_t handle,
            acblasOperation_t transa,
            acblasOperation_t transb,
            int m,
            int n,
            int k,
            const void *alpha,
            const void *A,
            hggcDataType Atype,
            int lda,
            const void *B,
            hggcDataType Btype,
            int ldb,
            const void *beta,
            void *C,
            hggcDataType Ctype,
            int ldc,
            hggcDataType computeType,
            acblasGemmAlgo_t algo)
#endif
```

`acblas<t>gemm` 的**最通用** 扩展，允许调用方独立指定：

- `A`、`B`、`C` 三者各自的数据类型（`Atype` / `Btype` / `Ctype`）
- 累加 / 缩放使用的计算精度（`computeType`）
- 内部 GEMM 算法的具体实现（`algo`）

合法的"计算精度 × 矩阵类型"组合详见下表。计算式仍为标准 GEMM：

$$C \leftarrow \alpha\,\text{op}(A)\cdot\text{op}(B) + \beta\,C$$

其中 op(·) 的取值与转置约定与 `acblas<t>gemm` 一致；$\text{op}(A)$、$\text{op}(B)$、$C$ 的形状依次为 $m\times k$、$k\times n$、$m\times n$，均列优先。

!!! warning
    **签名重载注意** ：本函数有两版 C++ 重载，`computeType` 取 `acblasComputeType_t`（新接口）或 `hggcDataType`（向后兼容 C++ 老代码）。C 调用者只能用第一版（新接口），编译器会自动选择匹配的重载版本。

**参数清单** ：

- `handle` — acBLAS 上下文。
- `transa` / `transb` — 选 op(`A`) / op(`B`)，含义见 `acblasOperation_t`。
- `m`、`n`、`k` — 三个公共维度，含义同 `gemm`。
- `alpha` / `beta`（host 或 device）— 缩放因子。其精度由 `computeType` 与 `Ctype` 共同决定（见下表）。`beta == 0` 时 `C` 可不必为有效输入。
- `A`（device）/ `Atype` / `lda` — op(`A`) 的设备指针、元素类型、前导维度。`transa == OP_N` 时按 `lda × k` 存（`lda ≥ max(1, m)`）；其他取值按 `lda × m` 存（`lda ≥ max(1, k)`）。
- `B`（device）/ `Btype` / `ldb` — 同理，对应 `transb`。
- `C`（device）/ `Ctype` / `ldc` — 输出矩阵，形状 `ldc × n`，`ldc ≥ max(1, m)`。
- `computeType` — 见下表的"计算类型"列；对 `acblasComputeType_t` 取值 [见 6.3.8](#638-acblascomputetype_t)（acblasComputeType_t）。
- `algo` — 选具体算法实现，见 `acblasGemmAlgo_t`；通常用 `ACBLAS_GEMM_DEFAULT` 由库自动选择即可。

`acblasGemmEx()` 支持以下计算类型、缩放类型、Atype/Btype 和 Ctype 组合：

| 计算类型                                                 | 缩放类型 (alpha 和 beta) | Atype/Btype   | Ctype         |
| :--- | :--- | :--- | :--- |
| `ACBLAS_COMPUTE_16F` 或 `ACBLAS_COMPUTE_16F_PEDANTIC`         | `HGGC_R_16F`                | `HGGC_R_16F`  | `HGGC_R_16F`  |
| `ACBLAS_COMPUTE_32I` 或 `ACBLAS_COMPUTE_32I_PEDANTIC`         | `HGGC_R_32I`                | `HGGC_R_8I`   | `HGGC_R_32I`  |
| `ACBLAS_COMPUTE_32F` 或 `ACBLAS_COMPUTE_32F_PEDANTIC`         | `HGGC_R_32F`                | `HGGC_R_16BF` | `HGGC_R_16BF` |
|                                                              |                             | `HGGC_R_16F`  | `HGGC_R_16F`  |
|                                                              |                             | `HGGC_R_8I`   | `HGGC_R_32F`  |
|                                                              |                             | `HGGC_R_16BF` | `HGGC_R_32F`  |
|                                                              |                             | `HGGC_R_16F`  | `HGGC_R_32F`  |
|                                                              |                             | `HGGC_R_32F`  | `HGGC_R_32F`  |
| `ACBLAS_COMPUTE_32F_FAST_16F` 或 `ACBLAS_COMPUTE_32F_FAST_16BF` 或 `ACBLAS_COMPUTE_32F_FAST_TF32` | `HGGC_R_32F`                | `HGGC_R_32F`  | `HGGC_R_32F`  |
| `ACBLAS_COMPUTE_64F` 或 `ACBLAS_COMPUTE_64F_PEDANTIC`         | `HGGC_R_64F`                | `HGGC_R_64F`  | `HGGC_R_64F`  |

!!! note
    `ACBLAS_COMPUTE_32I` 和 `ACBLAS_COMPUTE_32I_PEDANTIC` 计算类型仅在 A、B 为 4 字节对齐且 lda、ldb 为 4 的倍数时受支持。为了获得更好的性能，还建议满足此处列出的 IMMA kernel 对规则数据排序的要求。

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_ARCH_MISMATCH`：设备无所需硬件特性（如混精）。
- `ACBLAS_STATUS_NOT_SUPPORTED`：`Atype`/`Btype`/`Ctype`/`algo` 组合不在上表。
- `ACBLAS_STATUS_INVALID_VALUE`：维度或 `lda`/`ldb`/`ldc` 不满足上文约束，或 `transa`/`transb` 不在合法枚举内。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 4.3.3. acblasGemmBatchedEx() {#433-acblasgemmbatchedex}

```cpp
acblasStatus_t
acblasGemmBatchedEx(acblasHandle_t handle,
                    acblasOperation_t transa,
                    acblasOperation_t transb,
                    int m,
                    int n,
                    int k,
                    const void *alpha,
                    const void * const Aarray[],
                    hggcDataType Atype,
                    int lda,
                    const void * const Barray[],
                    hggcDataType Btype,
                    int ldb,
                    const void *beta,
                    void * const Carray[],
                    hggcDataType Ctype,
                    int ldc,
                    int batchCount,
                    acblasComputeType_t computeType,
                    acblasGemmAlgo_t algo)

#if defined(__cplusplus)
acblasStatus_t
acblasGemmBatchedEx(acblasHandle_t handle,
                    acblasOperation_t transa,
                    acblasOperation_t transb,
                    int m,
                    int n,
                    int k,
                    const void *alpha,
                    const void * const Aarray[],
                    hggcDataType Atype,
                    int lda,
                    const void * const Barray[],
                    hggcDataType Btype,
                    int ldb,
                    const void *beta,
                    void * const Carray[],
                    hggcDataType Ctype,
                    int ldc,
                    int batchCount,
                    hggcDataType computeType,
                    acblasGemmAlgo_t algo)
#endif
```

`acblasGemmEx` 的批处理版，一次完成"同形批"：所有实例共用 $(m,n,k)$、$(\text{lda},\text{ldb},\text{ldc})$ 和 $(\text{transa},\text{transb})$，**只有** 每个实例的 `A`、`B`、`C` 指针不同。调用方把这些指针放进三个长度均为 `batchCount` 的**设备端** 指针数组（`Aarray` / `Barray` / `Carray`）传入。

对每个 $i \in [0,\,\text{batchCount}-1]$：

$$C[i] \leftarrow \alpha\,\text{op}(A[i])\cdot\text{op}(B[i]) + \beta\,C[i]$$

转置与形状语义与 `acblasGemmEx` 一致。

**参数清单** ：

- `handle` — acBLAS 上下文。
- `transa` / `transb` — 选 op(`A[i]`) / op(`B[i]`)，含义见 `acblasOperation_t`。
- `m`、`n`、`k` — 每个实例的形状。
- `alpha` / `beta`（host 或 device）— 标量；精度由 `computeType` / `Ctype` 共同决定（详见下表）。`beta == 0` 时各 `C[i]` 可无需为有效输入。
- `Aarray` / `Atype` / `lda`（device）— 指向矩阵 A[i] 的指针数组、元素类型与前导维度。每个 `A[i]` 形状视 `transa`：`OP_N` 时按 `lda × k`（`lda ≥ max(1, m)`），否则 `lda × m`（`lda ≥ max(1, k)`）。指针对齐见下方"使用约束"。
- `Barray` / `Btype` / `ldb`（device）— 同理，由 `transb` 决定形状。
- `Carray` / `Ctype` / `ldc`（device）— 输出指针数组；每个 `C[i]` 形状固定 `ldc × n`（`ldc ≥ max(1, m)`）。**各 `C[i]` 在设备内存中不得互相重叠**，任意两个 GEMM 必须能独立完成，否则结果不可预测。
- `batchCount` — 三个数组各自的元素数（即实例总数）。
- `computeType` / `algo` — 含义与 `acblasGemmEx` 相同。

**使用约束** ：

- 实践经验：当每个实例已经"足够大"（如 m, n, k ≥ 256），分别在多个 Stream 上调用 `acblas<t>gemm` 可能比此 batched API 更具优势，后者的目标是小规模、大数量的工作负载。
- **指针对齐** ：当 `Atype` / `Btype` 是 `HGGC_R_16F` / `HGGC_R_16BF`、或 `computeType` 选了任何 `FAST_*`、或经由 math mode 启用了 fast math 时，`Aarray` / `Barray` / `Carray` 数组中指向真武 PPU 矩阵的指针本身（不是指针数组）应满足：

  | 条件 | 对齐要求 |
  |---|---|
  | 推荐通用 | 至少**16 字节** |
  | `k % 8 == 0` | 至少 16 字节 |
  | `k % 2 == 0` | 至少 4 字节 |

`acblasGemmBatchedEx()` 支持以下计算类型、缩放类型、Atype/Btype 和 Ctype：

| 计算类型                                                 | 缩放类型 (alpha 和 beta) | Atype/Btype   | Ctype         |
| :--- | :--- | :--- | :--- |
| `ACBLAS_COMPUTE_16F` 或 `ACBLAS_COMPUTE_16F_PEDANTIC`         | `HGGC_R_16F`                | `HGGC_R_16F`  | `HGGC_R_16F`  |
| `ACBLAS_COMPUTE_32I` 或 `ACBLAS_COMPUTE_32I_PEDANTIC`         | `HGGC_R_32I`                | `HGGC_R_8I`   | `HGGC_R_32I`  |
| `ACBLAS_COMPUTE_32F` 或 `ACBLAS_COMPUTE_32F_PEDANTIC`         | `HGGC_R_32F`                | `HGGC_R_16BF` | `HGGC_R_16BF` |
|                                                              |                             | `HGGC_R_16F`  | `HGGC_R_16F`  |
|                                                              |                             | `HGGC_R_8I`   | `HGGC_R_32F`  |
|                                                              |                             | `HGGC_R_16BF` | `HGGC_R_32F`  |
|                                                              |                             | `HGGC_R_16F`  | `HGGC_R_32F`  |
|                                                              |                             | `HGGC_R_32F`  | `HGGC_R_32F`  |
| `ACBLAS_COMPUTE_32F_FAST_16F` 或 `ACBLAS_COMPUTE_32F_FAST_16BF` 或 `ACBLAS_COMPUTE_32F_FAST_TF32` | `HGGC_R_32F`                | `HGGC_R_32F`  | `HGGC_R_32F`  |
| `ACBLAS_COMPUTE_64F` 或 `ACBLAS_COMPUTE_64F_PEDANTIC`         | `HGGC_R_64F`                | `HGGC_R_64F`  | `HGGC_R_64F`  |

!!! note
    `ACBLAS_COMPUTE_32I` / `ACBLAS_COMPUTE_32I_PEDANTIC` 计算类型还有额外要求：所有 `A[i]`、`B[i]` 指针 4 字节对齐，`lda`、`ldb` 必须是 4 的倍数。性能上建议同时满足 IMMA kernel 对规则数据排序的要求。

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_ARCH_MISMATCH`：架构不匹配。
- `ACBLAS_STATUS_NOT_SUPPORTED`：`Atype`/`Btype`/`Ctype`/`algo` 组合不在上表。
- `ACBLAS_STATUS_INVALID_VALUE`：维度或 lda/ldb/ldc 不满足约束，或 `transa`/`transb` 不在合法枚举内。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 4.3.4. acblasGemmStridedBatchedEx() {#434-acblasgemmstridedbatchedex}

```cpp
acblasStatus_t
acblasGemmStridedBatchedEx(acblasHandle_t handle,
                            acblasOperation_t transa,
                            acblasOperation_t transb,
                            int m,
                            int n,
                            int k,
                            const void *alpha,
                            const void *A,
                            hggcDataType Atype,
                            int lda,
                            long long int strideA,
                            const void *B,
                            hggcDataType Btype,
                            int ldb,
                            long long int strideB,
                            const void *beta,
                            void *C,
                            hggcDataType Ctype,
                            int ldc,
                            long long int strideC,
                            int batchCount,
                            acblasComputeType_t computeType,
                            acblasGemmAlgo_t algo)

#if defined(__cplusplus)
acblasStatus_t
acblasGemmStridedBatchedEx(acblasHandle_t handle,
                            acblasOperation_t transa,
                            acblasOperation_t transb,
                            int m,
                            int n,
                            int k,
                            const void *alpha,
                            const void *A,
                            hggcDataType Atype,
                            int lda,
                            long long int strideA,
                            const void *B,
                            hggcDataType Btype,
                            int ldb,
                            long long int strideB,
                            const void *beta,
                            void *C,
                            hggcDataType Ctype,
                            int ldc,
                            long long int strideC,
                            int batchCount,
                            hggcDataType computeType,
                            acblasGemmAlgo_t algo)
#endif
```

`acblasGemmBatchedEx` 的"等间隔"变体，同形批，但不需要传指针数组：每个实例的 `A[i]` / `B[i]` / `C[i]` 都位于**前一实例的固定元素偏移处** ，由 `strideA` / `strideB` / `strideC` 三个 `long long int` 直接给出。调用方只传首实例的指针，库内部计算其余实例的位置。

!!! warning "签名重载"
    本函数同样有两版 C++ 重载——一版用 `acblasComputeType_t`（新接口，C/C++ 均推荐），一版用 `hggcDataType`（C++ 老代码向后兼容）。C 调用者只能用第一版。

对每个 $i \in [0,\,\text{batchCount}-1]$，地址按等差数列计算：

$$C + i\cdot\text{strideC} \;\leftarrow\; \alpha\,\text{op}(A + i\cdot\text{strideA})\cdot\text{op}(B + i\cdot\text{strideB}) + \beta\,(C + i\cdot\text{strideC})$$

形状和转置约定与 `acblasGemmEx` 一致；下文用 $A[i]$、$B[i]$、$C[i]$ 简写表示第 $i$ 个实例（即由对应 stride 偏移定位的子矩阵），三个 stride 的单位都是**元素数** 且必须非零。

**参数清单** ：

- `handle` — acBLAS 上下文。
- `transa` / `transb` — 选 op(`A[i]`) / op(`B[i]`)。
- `m`、`n`、`k` — 每个实例的形状。
- `alpha` / `beta`（host 或 device）— 标量。
- `A` / `Atype` / `lda`（device）— 首实例的设备指针、元素类型、前导维度。`A[i]` 形状视 `transa`：`OP_N` 时 `lda × k`（`lda ≥ max(1, m)`），否则 `lda × m`（`lda ≥ max(1, k)`）。
- `strideA`（`long long int`）— `A[i]` 与 `A[i+1]` 之间的元素偏移。
- `B` / `Btype` / `ldb` / `strideB` — 同理。
- `C` / `Ctype` / `ldc` / `strideC`（device）— 输出首实例的指针、元素类型、前导维度与等差跨度；`C[i]` 形状 `ldc × n`（`ldc ≥ max(1, m)`）。**各 `C[i]` 在设备内存中不得互相重叠** ，否则结果不可预测。
- `batchCount` — 总实例数。
- `computeType` / `algo` — 含义与 `acblasGemmEx` 相同。

`acblasGemmStridedBatchedEx()` 支持以下计算类型、缩放类型、Atype/Btype 和 Ctype：

| 计算类型                                                 | 缩放类型 (alpha 和 beta) | Atype/Btype   | Ctype         |
| :--- | :--- | :--- | :--- |
| `ACBLAS_COMPUTE_16F` 或 `ACBLAS_COMPUTE_16F_PEDANTIC`         | `HGGC_R_16F`                | `HGGC_R_16F`  | `HGGC_R_16F`  |
| `ACBLAS_COMPUTE_32I` 或 `ACBLAS_COMPUTE_32I_PEDANTIC`         | `HGGC_R_32I`                | `HGGC_R_8I`   | `HGGC_R_32I`  |
| `ACBLAS_COMPUTE_32F` 或 `ACBLAS_COMPUTE_32F_PEDANTIC`         | `HGGC_R_32F`                | `HGGC_R_16BF` | `HGGC_R_16BF` |
|                                                              |                             | `HGGC_R_16F`  | `HGGC_R_16F`  |
|                                                              |                             | `HGGC_R_8I`   | `HGGC_R_32F`  |
|                                                              |                             | `HGGC_R_16BF` | `HGGC_R_32F`  |
|                                                              |                             | `HGGC_R_16F`  | `HGGC_R_32F`  |
|                                                              |                             | `HGGC_R_32F`  | `HGGC_R_32F`  |
| `ACBLAS_COMPUTE_32F_FAST_16F` 或 `ACBLAS_COMPUTE_32F_FAST_16BF` 或 `ACBLAS_COMPUTE_32F_FAST_TF32` | `HGGC_R_32F`                | `HGGC_R_32F`  | `HGGC_R_32F`  |
| `ACBLAS_COMPUTE_64F` 或 `ACBLAS_COMPUTE_64F_PEDANTIC`         | `HGGC_R_64F`                | `HGGC_R_64F`  | `HGGC_R_64F`  |

!!! note
    `ACBLAS_COMPUTE_32I` / `ACBLAS_COMPUTE_32I_PEDANTIC` 还要求所有 `A[i]`、`B[i]` 指针 4 字节对齐，`lda`、`ldb` 必须是 4 的倍数。

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_ARCH_MISMATCH`：架构不匹配。
- `ACBLAS_STATUS_NOT_SUPPORTED`：`Atype`/`Btype`/`Ctype`/`algo` 组合不在上表。
- `ACBLAS_STATUS_INVALID_VALUE`：维度或 lda/ldb/ldc 不满足约束，或 `transa`/`transb` 不在合法枚举内。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

比赛关联：`acblasGemmEx` 系列是 INT8（`HGGC_R_8I` + `ACBLAS_COMPUTE_32I`）、FP16/BF16 混精、TF32 快速路径的入口，量化推理时按组合表选择 computeType；`ACBLAS_COMPUTE_32F_FAST_16F/16BF/TF32` 可在精度损失可控时换取吞吐。批处理变体适合 MoE/多头场景的同形小 GEMM。

### 4.4. 扩展 Level-1 函数 {#44-扩展-level-1-函数}

标准 Level-1 BLAS 函数的扩展版本，支持混合精度与自定义计算类型。

#### 4.4.1. acblasNrm2Ex() {#441-acblasnrm2ex}

```cpp
acblasStatus_t
acblasNrm2Ex(acblasHandle_t handle,
            int n,
            const void *x,
            hggcDataType xType,
            int incx,
            void *result,
            hggcDataType resultType,
            hggcDataType executionType)
```

`acblas<t>nrm2` 的泛化版，`x`、`result`、内部累加这三处的精度可以**各自独立** 指定（分别由 `xType`、`resultType`、`executionType` 给出）。计算的仍是欧氏范数；为避免中间下溢/上溢，库内部采用多阶段累加，等价于：

$$\|\mathbf{x}\|_2 \;=\; \sqrt{\sum_{i=1}^{n} \mathbf{x}[j]^{2}},\qquad j = 1 + (i-1)\cdot\text{incx}$$

下标采用 1-based 是为了与 BLAS 标准保持一致。

**参数：**

- `handle`、`n`、`x`、`incx` — 与 `<t>nrm2` 完全一致。
- `xType`（输入）— `x` 的元素类型。
- `result`（host 或 device，输出）— 范数值写入处；`n` 或 `incx ≤ 0` 时返回 `0.0`。
- `resultType`（输入）— `*result` 的元素类型。
- `executionType`（输入）— 内部累加所用精度。

当前允许的精度组合：

| `xType` | `resultType` | `executionType` |
| :--- | :--- | :--- |
| `HGGC_R_32F` | `HGGC_R_32F` | `HGGC_R_32F` |
| `HGGC_R_64F` | `HGGC_R_64F` | `HGGC_R_64F` |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_ALLOC_FAILED`：归约缓冲分配失败。
- `ACBLAS_STATUS_NOT_SUPPORTED`：三种类型组合不在上表。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。
- `ACBLAS_STATUS_INVALID_VALUE`：类型不合法或 `result` 为 NULL。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 4.4.2. acblasAxpyEx() {#442-acblasaxpyex}

```cpp
acblasStatus_t
acblasAxpyEx(acblasHandle_t handle,
            int n,
            const void *alpha,
            hggcDataType alphaType,
            const void *x,
            hggcDataType xType,
            int incx,
            void *y,
            hggcDataType yType,
            int incy,
            hggcDataType executionType);
```

`acblas<t>axpy` 的泛化版，`alpha`、`x`、`y`、内部累加四者的精度可分别由 `alphaType`、`xType`、`yType`、`executionType` 指定。计算式仍是经典 AXPY，**原地** 写回 `y`：

$$\mathbf{y}[j] \mathrel{+}= \alpha \cdot \mathbf{x}[k],\qquad k = 1 + (i-1)\cdot\text{incx},\quad j = 1 + (i-1)\cdot\text{incy}$$

**参数：**

- `handle`、`n`、`incx`、`incy` — 与 `<t>axpy` 同义。
- `alpha`（host 或 device）`alphaType` — 标量值与精度。
- `x`（device）`xType` — 输入向量与精度。
- `y`（device，原地读写）`yType` — 输出向量与精度。
- `executionType` — 内部累加精度。

当前允许的精度组合：

| `alphaType` | `xType` | `yType` | `executionType` |
| :--- | :--- | :--- | :--- |
| `HGGC_R_32F` | `HGGC_R_32F` | `HGGC_R_32F` | `HGGC_R_32F` |
| `HGGC_R_64F` | `HGGC_R_64F` | `HGGC_R_64F` | `HGGC_R_64F` |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_NOT_SUPPORTED`：不支持。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。
- `ACBLAS_STATUS_INVALID_VALUE`：任一 `*Type` 不合法。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 4.4.3. acblasDotEx() {#443-acblasdotex}

```cpp
acblasStatus_t
acblasDotEx(acblasHandle_t handle,
            int n,
            const void *x,
            hggcDataType xType,
            int incx,
            const void *y,
            hggcDataType yType,
            int incy,
            void *result,
            hggcDataType resultType,
            hggcDataType executionType);
```

`acblas<t>dot` 的泛化版，`x`、`y`、`result`、内部累加四处的精度由 `xType`、`yType`、`resultType`、`executionType` 分别指定。

$$\text{result} \;=\; \sum_{i=1}^{n} \mathbf{x}[k]\cdot\mathbf{y}[j],\qquad k = 1 + (i-1)\cdot\text{incx},\quad j = 1 + (i-1)\cdot\text{incy}$$

**参数：**

- `handle`、`n`、`incx`、`incy` — 与 `<t>dot` 同义。
- `x`（device）`xType`、`y`（device）`yType` — 输入向量与精度。
- `result`（host 或 device，输出）`resultType` — 点积结果；`n ≤ 0` 时返回 `0.0`。
- `executionType` — 内部累加精度。

当前允许的精度组合：

| `xType` | `yType` | `resultType` | `executionType` |
| :--- | :--- | :--- | :--- |
| `HGGC_R_32F` | `HGGC_R_32F` | `HGGC_R_32F` | `HGGC_R_32F` |
| `HGGC_R_64F` | `HGGC_R_64F` | `HGGC_R_64F` | `HGGC_R_64F` |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_ALLOC_FAILED`：内存分配失败。
- `ACBLAS_STATUS_NOT_SUPPORTED`：不支持。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。
- `ACBLAS_STATUS_INVALID_VALUE`：参数无效。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 4.4.4. acblasRotEx() {#444-acblasrotex}

```cpp
acblasStatus_t
acblasRotEx(acblasHandle_t handle,
            int n,
            void *x,
            hggcDataType xType,
            int incx,
            void *y,
            hggcDataType yType,
            int incy,
            const void *c, /* host or device pointer */
            const void *s,
            hggcDataType csType,
            hggcDataType executionType);
```

`acblas<t>rot` 的泛化版，`x`/`y` 的精度、(`c`,`s`) 标量对的精度、以及内部累加精度都可分别指定。对每对 (`x[k]`， `y[j]`) 施加由 $c = \cos\alpha$、$s = \sin\alpha$ 给出的 Givens 旋转：

$$\begin{pmatrix}\mathbf{x}[k]\\ \mathbf{y}[j]\end{pmatrix} \;\leftarrow\; \begin{pmatrix}c & s \\ -s & c\end{pmatrix} \begin{pmatrix}\mathbf{x}[k]\\ \mathbf{y}[j]\end{pmatrix},\qquad k = 1 + (i-1)\cdot\text{incx},\quad j = 1 + (i-1)\cdot\text{incy}$$

`x` 与 `y` 都**原地** 更新。

**参数：**

- `handle`、`n`、`incx`、`incy` — 与 `<t>rot` 同义。
- `x` / `xType`、`y` / `yType`（device，原地读写）— 两向量及各自精度。
- `c`、`s`（host 或 device）`csType` — 旋转矩阵的余弦 / 正弦元素与精度。
- `executionType` — 内部累加精度。

当前允许的精度组合：

| `executionType` | `xType` / `yType` | `csType` |
| :--- | :--- | :--- |
| `HGGC_R_32F` | `HGGC_R_32F` | `HGGC_R_32F` |
| `HGGC_R_64F` | `HGGC_R_64F` | `HGGC_R_64F` |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 4.4.5. acblasScalEx() {#445-acblasscalex}

```cpp
acblasStatus_t  acblasScalEx(acblasHandle_t handle,
                             int n,
                             const void *alpha,
                             hggcDataType alphaType,
                             void *x,
                             hggcDataType xType,
                             int incx,
                             hggcDataType executionType);
```

`acblas<t>scal` 的泛化版，`alpha`、`x`、内部累加三者的精度独立指定。**原地** 缩放：

$$\mathbf{x}[j] \mathrel{\ast}= \alpha,\qquad j = 1 + (i-1)\cdot\text{incx}$$

**参数：**

- `handle`、`n`、`incx` — 与 `<t>scal` 同义。
- `alpha`（host 或 device）`alphaType` — 标量值与精度。
- `x`（device，原地读写）`xType` — 输入向量与精度。
- `executionType` — 内部累加精度。

当前允许的精度组合：

| `alphaType` | `xType` | `executionType` |
| :--- | :--- | :--- |
| `HGGC_R_32F` | `HGGC_R_32F` | `HGGC_R_32F` |
| `HGGC_R_64F` | `HGGC_R_64F` | `HGGC_R_64F` |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_NOT_SUPPORTED`：不支持。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。
- `ACBLAS_STATUS_INVALID_VALUE`：参数无效。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

## 5. acblasLt 轻量矩阵乘法 {#5-acblaslt-轻量矩阵乘法}

### 5.1. 编程模型 {#51-编程模型}

acblasLt 是一套轻量级的 GEMM 专用接口，提供的 API 较 acBLAS API 更细粒度，把矩阵布局、输入数据类型、计算数据类型、算法实现、启发式参数等一一开放给用户配置。配置完成后，**同一组描述符可以在形状/类型一致的不同输入上反复使用** ，与 acFFT/FFTW「先建 plan，再多次执行」的模式一致。

#### 5.1.1. 问题大小限制 {#511-问题大小限制}

acblasLt 的尺寸上限源自底层 HGGC grid 的维度限制。最典型的几条硬约束：

| 维度 | 上限来源 | 影响 |
| :--- | :--- | :--- |
| batch | grid 的 z 维度 | 多数 kernel 不支持 batch > 65535 |
| `m`、`n` | grid 维度 | 单 kernel 处理范围有限，更大需切分 |

当目标问题无法在单个 Kernel 内一次执行完时，acblasLt 会尝试将其**自动拆解** 为多个子问题、由多个 Kernel 协同完成。但内部拆解机制有以下约束：

| 限制项 | 必须满足的条件 |
| :--- | :--- |
| Amax 计算 | 不支持。`ACBLASLT_MATMUL_DESC_AMAX_D_POINTER`、`ACBLASLT_MATMUL_DESC_EPILOGUE_AUX_AMAX_POINTER` 必须保持未设置（见 [`acblasLtMatmulDescAttributes_t`](#524-acblasltmatmuldescattributes_t)） |
| 矩阵布局 | 所有矩阵的 `ACBLASLT_MATRIX_LAYOUT_ORDER` 必须为 `ACBLASLT_ORDER_COL`（见 [`acblasLtOrder_t`](#5212-acblasltorder_t)） |
| Epilogue + n 方向 | 当 `ACBLASLT_MATMUL_DESC_EPILOGUE` 为 `ACBLASLT_EPILOGUE_DRELU_BGRAD` 或 `ACBLASLT_EPILOGUE_DGELU_BGRAD` 时，acblasLt **不会** 沿 n 方向切分（见 [`acblasLtEpilogue_t`](#521-acblasltepilogue_t)） |

如需绕过上述限制，可由调用方自行切分问题，分别启动 kernel 并按需做归约合并。

<a id="fp8_usage"></a>

#### 5.1.2. 8 位浮点数据类型（FP8）使用 {#512-8-位浮点数据类型fp8使用}

FP8 用于进一步压缩存储与计算开销、加速矩阵乘。库提供两种 FP8 格式：

| 类型 | 位宽分布 | 目标场景 |
| :--- | :--- | :--- |
| `HGGC_R_8F_E4M3` | 4-bit 指数 + 3-bit 尾数 | 动态范围较 half 更小，但精度更高 |
| `HGGC_R_8F_E5M2` | 5-bit 指数 + 2-bit 尾数 | 动态范围接近 half |

> 文档中后续出现的**FP8** ，若无另行说明，同时指代上述两种格式。

**带缩放因子的矩阵乘**

为了在 FP8 精度下保留数值动态范围，acblasLt 将原生 FP8 GEMM 定义为：

$$D = \text{scale}_D \cdot \big(\alpha \cdot \text{scale}_A \cdot \text{scale}_B \cdot \text{op}(A)\,\text{op}(B) + \beta \cdot \text{scale}_C \cdot C\big)$$

各量含义：

| 量 | 角色 |
| :--- | :--- |
| $A$, $B$, $C$ | 输入矩阵 |
| $\alpha$, $\beta$ | 标量加权 |
| $\text{scale}_A$, $\text{scale}_B$, $\text{scale}_C$ | 反量化（dequant）因子 |
| $\text{scale}_D$ | 量化（quant）因子 |

> 所有缩放因子均以**乘法** 方式参与运算。根据应用上下文，有时需要传入原值、有时需要传入其倒数。完整说明参见 [`acblasLtMatmul()`](#533-acblasltmatmul) 与 `acblasLtMatmulDescAttributes_t`。

**Epilogue 与 amax 的计算**

带 epilogue 与 $\text{amax}_D$ 的 FP8 矩阵乘可拆解为：

$$\begin{split}
D_{\text{temp}}, \text{Aux}_{\text{temp}} & = \text{Epilogue}\big(\alpha \cdot \text{scale}_A \cdot \text{scale}_B \cdot \text{op}(A)\,\text{op}(B) + \beta \cdot \text{scale}_C \cdot C\big) \\
\text{amax}_D & = \text{absmax}(D_{\text{temp}}) \\
\text{amax}_{\text{Aux}} & = \text{absmax}(\text{Aux}_{\text{temp}}) \\
D & = \text{scale}_D \cdot D_{\text{temp}} \\
\text{Aux} & = \text{scale}_{\text{Aux}} \cdot \text{Aux}_{\text{temp}}
\end{split}$$

其中 $\text{Aux}$ 为 GELU 等 epilogue 函数的辅助输出；$\text{scale}_{\text{Aux}}$ 是作用于 $\text{Aux}$ 的可选缩放因子；$\text{amax}_{\text{Aux}}$ 为缩放前 $\text{Aux}$ 的最大绝对值。具体属性键参见 `acblasLtMatmulDescAttributes_t` 中的 `ACBLASLT_MATMUL_DESC_AMAX_D_POINTER` 与 `ACBLASLT_MATMUL_DESC_EPILOGUE_AUX_AMAX_POINTER`。

比赛关联：FP8（E4M3/E5M2）是比赛量化方向的核心路径：per-tensor 缩放因子（`A/B/C/D_SCALE_POINTER`）+ `AMAX_D_POINTER` 正好支撑动态量化校准；`FAST_ACCUM` 可在精度与速度间权衡。

#### 5.1.3. 原子同步 {#513-原子同步}

原子同步让 `acblasLtMatmul()` 与另一并发 Kernel 之间通过**32 位整数计数器数组** 建立生产者-消费者通道，从而以更细粒度重叠 matmul 与通信/前序计算。

**两种角色**

| 模式 | 切分方向 | 说明 |
| :--- | :--- | :--- |
| 消费者 | A 按行 / B 按列分块 | 计数器归 0 才允许读取并参与当前块计算；生产者侧需配合 memory fence，确保写入对 matmul kernel 可见 |
| 生产者 | C（或异址模式的 D）按行/列分块 | 块计算完成后将计数器置 0；kernel 运行前所有计数器必须初始化为 1 |

**配置入口**

| 属性键 | 用途 |
| :--- | :--- |
| `ACBLASLT_MATMUL_DESC_ATOMIC_SYNC_IN_COUNTERS_POINTER` | 消费者模式：输入计数器数组指针 |
| `ACBLASLT_MATMUL_DESC_ATOMIC_SYNC_OUT_COUNTERS_POINTER` | 生产者模式：输出计数器数组指针 |
| `ACBLASLT_MATMUL_DESC_ATOMIC_SYNC_NUM_CHUNKS_D_ROWS` | 行方向分块数（须 > 0） |
| `ACBLASLT_MATMUL_DESC_ATOMIC_SYNC_NUM_CHUNKS_D_COLS` | 列方向分块数（须 > 0） |

只有同时为 ROWS 和 COLS 设置大于 0 的值，原子同步特性才会启用，计数器数组的元素数需足够覆盖所有块。

**块数取值范围**

对**列优先** 布局：

$$
0 \leq \text{NUM\_CHUNKS\_ROWS} \leq \left\lfloor \frac{M}{\text{TILE\_SIZE\_M} \times \text{CLUSTER\_SHAPE\_M}} \right\rfloor
$$

$$
0 \leq \text{NUM\_CHUNKS\_COLS} \leq \left\lfloor \frac{N}{\text{TILE\_SIZE\_N} \times \text{CLUSTER\_SHAPE\_N}} \right\rfloor
$$

对**行优先** 布局，把上式中 M ↔ N、对应 tile 与 cluster 形状一起交换即可。
TILE_SIZE 与 CLUSTER_SHAPE 在编译期确定，当前版本的 algo 选择由库内部自动完成。

以下伪代码演示列优先 + TN 配置下"按行分块"的工作方式（行优先 / 按列分块同理，仅偏移量公式不同；真实实现保留对块计算顺序与各种优化的自由）：

```cpp
// 以下代码展示列优先布局和 TN 情况下按行划分的操作。
//
// 按列划分或行优先情况的处理方式类似，
// 主要区别是偏移量计算。
//
// 请注意，实际实现不保证块的计算顺序，
// 并且可能采用各种优化来提高整体性能。
//
// 这里：
//   - A, B, C -- 列优先布局中的输入矩阵
//   - lda -- 矩阵 A 的前导维度
//   - M, N, K -- 原始问题维度
//   - counters_in[] 和 counters_out[] -- 输入和输出原子计数器数组
//
for (int i = 0; i < NUM_CHUNKS_ROWS; i++) {
  // 消费者：等待输入计数器变为 0
  if (consumer) {
    while (counters_in[i] != 0); // 自旋
  }

  // 计算块维度
  chunk_m_begin = floor((double)M / NUM_CHUNKS_ROWS * i);
  chunk_m_end = floor((double)M / NUM_CHUNKS_ROWS * (i + 1));
  chunk_m = chunk_m_end - chunk_m_begin;

  // 计算当前块
  matmul(chunk_m, N, K,
         A[chunk_m_begin * lda], // A 是列优先转置
         B, // B 未被划分
         C[chunk_m_begin] // C 是列优先非转置
         );

  // 生产者：完成后将计数器设置为 0
  if (producer) {
    counters_out[i] = 0;
    // 使写入的值对消费者 kernel 可见
    memory_fence();
  }
}
```

### 5.2. 描述符与布局类型 {#52-描述符与布局类型}

本节集中说明 acblasLt API 涉及的所有类型与枚举：上下文/算法/矩阵/前置 (preference) 描述符，及其支持的属性键、tile/stage 编码、布尔位掩码等。

#### 5.2.1. acblasLtEpilogue_t {#521-acblasltepilogue_t}

`acblasLtEpilogue_t` 用于声明 `acblasLtMatmul()` 末尾要执行的**后处理（epilogue）** 。所有取值都由若干基础位组合而成（如 `RELU_BIAS = RELU | BIAS`），下面按功能划分为五组。

**A. 基础变换 / 偏置**

| 枚举值 | 公式 / 说明 |
| :--- | :--- |
| `ACBLASLT_EPILOGUE_DEFAULT = 1` | 无特殊后处理，仅按需缩放/量化 |
| `ACBLASLT_EPILOGUE_RELU = 2`    | `x := max(x, 0)` |
| `ACBLASLT_EPILOGUE_GELU = 32`   | `x := GELU(x)` |
| `ACBLASLT_EPILOGUE_BIAS = 4`    | 广播加偏置：偏置向量长度等于矩阵 D 的行数、必须紧凑存储（stride = 1），在最终后处理前广播到所有列 |

**B. 变换 + 偏置组合（前向）**

| 枚举值 | 含义 |
| :--- | :--- |
| `ACBLASLT_EPILOGUE_RELU_BIAS = RELU \| BIAS` | 先加偏置，再 ReLU |
| `ACBLASLT_EPILOGUE_GELU_BIAS = GELU \| BIAS` | 先加偏置，再 GELU |

**C. 带 AUX 输出的前向（用于训练）**

下列模式额外产出辅助张量到 `ACBLASLT_MATMUL_DESC_EPILOGUE_AUX_POINTER`：

| 枚举值 | AUX 内容 |
| :--- | :--- |
| `ACBLASLT_EPILOGUE_RELU_AUX = RELU \| 128` | ReLU 位掩码 |
| `ACBLASLT_EPILOGUE_RELU_AUX_BIAS = RELU_AUX \| BIAS` | 偏置 + ReLU 位掩码 |
| `ACBLASLT_EPILOGUE_GELU_AUX = GELU \| 128` | GELU 的输入矩阵 |
| `ACBLASLT_EPILOGUE_GELU_AUX_BIAS = GELU_AUX \| BIAS` | 偏置 + GELU 输入矩阵 |

**D. 反向梯度（消费 AUX 输入）**

下列模式从 `ACBLASLT_MATMUL_DESC_EPILOGUE_AUX_POINTER` 读取前向时存下的 AUX，并把激活梯度写回输出矩阵：

| 枚举值 | 输出位置 |
| :--- | :--- |
| `ACBLASLT_EPILOGUE_DRELU = 8 \| 128`               | ReLU 梯度 → 输出矩阵 |
| `ACBLASLT_EPILOGUE_DRELU_BGRAD = DRELU \| 16`      | ReLU 梯度 → 输出矩阵；偏置梯度 → 偏置缓冲区（`ACBLASLT_MATMUL_DESC_BIAS_POINTER`） |
| `ACBLASLT_EPILOGUE_DGELU = 64 \| 128`              | GELU 梯度 → 输出矩阵 |
| `ACBLASLT_EPILOGUE_DGELU_BGRAD = DGELU \| 16`      | GELU 梯度 → 输出矩阵；偏置梯度 → 偏置缓冲区 |

**E. 偏置梯度（沿 K 归约）**

| 枚举值 | 偏置长度 | 归约方向 |
| :--- | :--- | :--- |
| `ACBLASLT_EPILOGUE_BGRADA = 256` | 等于 D 的行数 | GEMM 的 k 维度 |
| `ACBLASLT_EPILOGUE_BGRADB = 512` | 等于 D 的列数 | GEMM 的 k 维度 |

输出都写入 `ACBLASLT_MATMUL_DESC_BIAS_POINTER`。

#### 5.2.2. acblasLtHandle_t {#522-acblaslthandle_t}

`acblasLtHandle_t` 是 acblasLt 库上下文的不透明指针。

| 阶段 | 接口 |
| :--- | :--- |
| 创建 | `acblasLtCreate()` |
| 销毁 | `acblasLtDestroy()` |

!!! tip
    `acblasHandle_t` 在内部封装了 `acblasLtHandle_t`，**任何有效的 `acblasHandle_t` 可直接通过类型转换当作 `acblasLtHandle_t` 使用** 。需要注意：与 `acblasHandle_t` 不同，`acblasLtHandle_t` 不绑定任何特定的 HGGC 上下文。


#### 5.2.3. acblasLtMatmulDesc_t {#523-acblasltmatmuldesc_t}

`acblasLtMatmulDesc_t` 是一次 `acblasLtMatmul()` 调用所需「**计算方式** 」的描述符。

| 阶段 | 接口 |
| :--- | :--- |
| 创建 | `acblasLtMatmulDescCreate()` |
| 销毁 | `acblasLtMatmulDescDestroy()` |

具体可配置的属性键 [见 5.2.4](#524-acblasltmatmuldescattributes_t)。

#### 5.2.4. acblasLtMatmulDescAttributes_t {#524-acblasltmatmuldescattributes_t}

`acblasLtMatmulDescAttributes_t` 罗列了 `acblasLtMatmulDesc_t` 可设置的所有属性键，涵盖计算/缩放类型、指针模式、矩阵转置、epilogue、偏置、FP8 缩放因子、原子同步等。读/写分别通过 `acblasLtMatmulDescGetAttribute()` 与 `acblasLtMatmulDescSetAttribute()`。

| **属性名称**                                      | **描述**                                              | **数据类型**                 |
| :--- | :--- | :--- |
| `ACBLASLT_MATMUL_DESC_COMPUTE_TYPE`                     | 计算类型。定义用于乘法和累加操作的数据类型，以及矩阵乘法期间的累加器。参见 `acblasComputeType_t`。 | int32_t                       |
| `ACBLASLT_MATMUL_DESC_SCALE_TYPE`                       | 缩放类型。定义缩放因子 `alpha` 和 `beta` 的数据类型。累加器值和矩阵 C 的值通常在最终缩放之前转换为缩放类型。然后该值在存储到内存之前从缩放类型转换为矩阵 D 的类型。默认值与 ACBLASLT_MATMUL_DESC_COMPUTE_TYPE 对齐。参见 `hggcDataType_t`。 | int32_t                       |
| `ACBLASLT_MATMUL_DESC_POINTER_MODE`                     | 指定 `alpha` 和 `beta` 通过引用传递，它们是 host 上的标量还是 device 上的标量，或者是 device 向量。默认值：`ACBLASLT_POINTER_MODE_HOST`（即在 host 上）。参见 `acblasLtPointerMode_t`。 | int32_t                       |
| `ACBLASLT_MATMUL_DESC_TRANSA`                           | 指定应对矩阵 A 执行的变换操作类型。默认值：`ACBLAS_OP_N`（即非转置操作）。参见 `acblasOperation_t`。 | int32_t                       |
| `ACBLASLT_MATMUL_DESC_TRANSB`                           | 指定应对矩阵 B 执行的变换操作类型。默认值：`ACBLAS_OP_N`（即非转置操作）。参见 `acblasOperation_t`。 | int32_t                       |
| `ACBLASLT_MATMUL_DESC_TRANSC`                           | 指定应对矩阵 C 执行的变换操作类型。目前仅支持 `ACBLAS_OP_N`。默认值：`ACBLAS_OP_N`（即非转置操作）。参见 `acblasOperation_t`。 | int32_t                       |
| `ACBLASLT_MATMUL_DESC_FILL_MODE`                        | 指示稠密矩阵的下部或上部是否已填充，因此应由函数使用。默认值：`ACBLAS_FILL_MODE_FULL`。参见 `acblasFillMode_t`。 | int32_t                       |
| `ACBLASLT_MATMUL_DESC_EPILOGUE`                         | Epilogue 函数。参见 `acblasLtEpilogue_t`。默认值：`ACBLASLT_EPILOGUE_DEFAULT`。 | uint32_t                      |
| `ACBLASLT_MATMUL_DESC_BIAS_POINTER`                     | device 内存中的偏置或偏置梯度向量指针。当使用以下 epilogue 之一时，输入向量长度与矩阵 D 的行数匹配：`ACBLASLT_EPILOGUE_BIAS`、`ACBLASLT_EPILOGUE_RELU_BIAS`、`ACBLASLT_EPILOGUE_RELU_AUX_BIAS`、`ACBLASLT_EPILOGUE_GELU_BIAS`、`ACBLASLT_EPILOGUE_GELU_AUX_BIAS`。当使用以下 epilogue 之一时，输出向量长度与矩阵 D 的行数匹配：`ACBLASLT_EPILOGUE_DRELU_BGRAD`、`ACBLASLT_EPILOGUE_DGELU_BGRAD`、`ACBLASLT_EPILOGUE_BGRADA`。当使用以下 epilogue 之一时，输出向量长度与矩阵 D 的列数匹配：`ACBLASLT_EPILOGUE_BGRADB`。当矩阵 D 数据类型为 `HGGC_R_8I` 时，偏置向量元素与 `alpha` 和 `beta` 类型相同（参见本表中的 `ACBLASLT_MATMUL_DESC_SCALE_TYPE`），否则与矩阵 D 数据类型相同。有关详细映射，请参见 `acblasLtMatmul()` 下的数据类型表。默认值：NULL。 | void * / const void *         |
| `ACBLASLT_MATMUL_DESC_BIAS_BATCH_STRIDE`                | 步长批量操作中下一个偏置或偏置梯度向量的步幅（以元素为单位）。默认值为 0。 | int64_t                       |
| `ACBLASLT_MATMUL_DESC_EPILOGUE_AUX_POINTER`             | epilogue 辅助缓冲区指针。当使用 `ACBLASLT_EPILOGUE_RELU_AUX` 或 `ACBLASLT_EPILOGUE_RELU_AUX_BIAS` epilogue 时，前向传播中 ReLU 位掩码的输出向量。当使用 `ACBLASLT_EPILOGUE_DRELU` 或 `ACBLASLT_EPILOGUE_DRELU_BGRAD` epilogue 时，反向传播中 ReLU 位掩码的输入向量。当使用 `ACBLASLT_EPILOGUE_GELU_AUX_BIAS` epilogue 时，前向传播中 GELU 输入矩阵的输出。当使用 `ACBLASLT_EPILOGUE_DGELU` 或 `ACBLASLT_EPILOGUE_DGELU_BGRAD` epilogue 时，反向传播中 GELU 输入矩阵的输入。有关辅助数据类型，请参见 `ACBLASLT_MATMUL_DESC_EPILOGUE_AUX_DATA_TYPE`。不解引用此指针的函数依赖其值来确定预期的指针对齐。需要设置 `ACBLASLT_MATMUL_DESC_EPILOGUE_AUX_LD` 属性。 | void * / const void *         |
| `ACBLASLT_MATMUL_DESC_EPILOGUE_AUX_LD`                  | epilogue 辅助缓冲区的前导维度。当使用 `ACBLASLT_EPILOGUE_RELU_AUX`、`ACBLASLT_EPILOGUE_RELU_AUX_BIAS`、`ACBLASLT_EPILOGUE_DRELU` 或 `ACBLASLT_EPILOGUE_DRELU_BGRAD` epilogue 时，ReLU 位掩码矩阵的前导维度（以元素为单位，即位）。必须能被 128 整除且不小于输出矩阵的行数。当使用 `ACBLASLT_EPILOGUE_GELU_AUX_BIAS`、`ACBLASLT_EPILOGUE_DGELU` 或 `ACBLASLT_EPILOGUE_DGELU_BGRAD` epilogue 时，GELU 输入矩阵的前导维度（以元素为单位）。必须能被 8 整除且不小于输出矩阵的行数。 | int64_t                       |
| `ACBLASLT_MATMUL_DESC_EPILOGUE_AUX_BATCH_STRIDE`        | epilogue 辅助缓冲区的批量步幅。当使用 `ACBLASLT_EPILOGUE_RELU_AUX`、`ACBLASLT_EPILOGUE_RELU_AUX_BIAS` 或 `ACBLASLT_EPILOGUE_DRELU_BGRAD` epilogue 时，ReLU 位掩码矩阵的批量步幅（以元素为单位，即位）。必须能被 128 整除。当使用 `ACBLASLT_EPILOGUE_GELU_AUX_BIAS`、`ACBLASLT_EPILOGUE_DGELU` 或 `ACBLASLT_EPILOGUE_DGELU_BGRAD` epilogue 时，GELU 输入矩阵的批量步幅（以元素为单位）。必须能被 8 整除。默认值：0。 | int64_t                       |
| `ACBLASLT_MATMUL_DESC_ALPHA_VECTOR_BATCH_STRIDE`        | alpha 向量的批量步幅。当矩阵 D 的 `ACBLASLT_MATRIX_LAYOUT_BATCH_COUNT` 大于 1 时，与 `ACBLASLT_POINTER_MODE_ALPHA_DEVICE_VECTOR_BETA_HOST` 一起使用。若设置了 `ACBLASLT_POINTER_MODE_ALPHA_DEVICE_VECTOR_BETA_ZERO`，则 `ACBLASLT_MATMUL_DESC_ALPHA_VECTOR_BATCH_STRIDE` 必须设置为 0，因为此模式不支持批量 alpha 向量。默认值：0。 | int64_t                       |
| `ACBLASLT_MATMUL_DESC_SM_COUNT_TARGET`                  | 用于并行执行的处理器核心数量目标。当开发者期望并发 stream 使用部分 device 资源时，优化在不同数量核心上执行的启发式算法。默认值：0。 | int32_t                       |
| `ACBLASLT_MATMUL_DESC_A_SCALE_POINTER`                  | 指向缩放因子值的 device 指针，该值将矩阵 A 中的数据转换为计算数据类型范围。缩放因子必须与计算类型具有相同的类型。若未指定或设置为 NULL，则假定缩放因子为 1。若为不支持的矩阵数据、缩放和计算类型组合设置，调用 acblasLtMatmul() 将返回 `ACBLAS_STATUS_INVALID_VALUE`。默认值：NULL | const void*                   |
| `ACBLASLT_MATMUL_DESC_B_SCALE_POINTER`                  | 矩阵 B 的等效于 `ACBLASLT_MATMUL_DESC_A_SCALE_POINTER`。默认值：NULL | const void*                   |
| `ACBLASLT_MATMUL_DESC_C_SCALE_POINTER`                  | 矩阵 C 的等效于 `ACBLASLT_MATMUL_DESC_A_SCALE_POINTER`。默认值：NULL | const void*                   |
| `ACBLASLT_MATMUL_DESC_D_SCALE_POINTER`                  | 矩阵 D 的等效于 `ACBLASLT_MATMUL_DESC_A_SCALE_POINTER`。默认值：NULL | const void*                   |
| `ACBLASLT_MATMUL_DESC_AMAX_D_POINTER`                   | 指向内存位置的 device 指针，完成时该位置将设置为输出矩阵中绝对值的最大值。计算值与计算类型具有相同的类型。若未指定或设置为 NULL，则不计算最大绝对值。若为不支持的矩阵数据、缩放和计算类型组合设置，调用 acblasLtMatmul() 将返回 `ACBLAS_STATUS_INVALID_VALUE`。默认值：NULL | void *                        |
| `ACBLASLT_MATMUL_DESC_EPILOGUE_AUX_DATA_TYPE`           | 将存储在 `ACBLASLT_MATMUL_DESC_EPILOGUE_AUX_POINTER` 中的数据类型。若未设置（或设置为默认值 -1），则数据类型设置为输出矩阵元素数据类型（DType），但有一些例外：ReLU 使用位掩码。对于输出类型（DType）为 `HGGC_R_8F_E4M3` 的 FP8 kernel，若满足以下条件，数据类型可以设置为非默认值：A 类型和 B 类型为 `HGGC_R_8F_E4M3`。偏置类型为 `HGGC_R_16F`。C 类型为 `HGGC_R_16BF` 或 `HGGC_R_16F`。`ACBLASLT_MATMUL_DESC_EPILOGUE` 设置为 `ACBLASLT_EPILOGUE_GELU_AUX`。当 C 类型为 `HGGC_R_16BF` 时，数据类型可以设置为 `HGGC_R_16BF` 或 `HGGC_R_8F_E4M3`。当 C 类型为 `HGGC_R_16F` 时，数据类型可以设置为 `HGGC_R_16F`。否则，数据类型应保持未设置或设置为默认值 -1。若为不支持的矩阵数据、缩放和计算类型组合设置，调用 acblasLtMatmul() 将返回 `ACBLAS_STATUS_INVALID_VALUE`。默认值：-1 | int32_t based on hggcDataType |
| `ACBLASLT_MATMUL_DESC_EPILOGUE_AUX_SCALE_POINTER`       | 指向缩放因子值的 device 指针，用于将结果从计算类型数据范围转换为通过 `ACBLASLT_MATMUL_DESC_EPILOGUE_AUX_POINTER` 设置的辅助矩阵中的存储数据范围。缩放因子值必须与计算类型具有相同的类型。若未指定或设置为 NULL，则假定缩放因子为 1。若为不支持的矩阵数据、缩放和计算类型组合设置，调用 acblasLtMatmul() 将返回 `ACBLAS_STATUS_INVALID_VALUE`。默认值：NULL | void *                        |
| `ACBLASLT_MATMUL_DESC_EPILOGUE_AUX_AMAX_POINTER`        | 指向内存位置的 device 指针，完成时该位置将设置为通过 `ACBLASLT_MATMUL_DESC_EPILOGUE_AUX_POINTER` 设置的缓冲区中绝对值的最大值。计算值与计算类型具有相同的类型。若未指定或设置为 NULL，则不计算最大绝对值。若为不支持的矩阵数据、缩放和计算类型组合设置，调用 acblasLtMatmul() 将返回 ACBLAS_STATUS_INVALID_VALUE。默认值：NULL | void *                        |
| `ACBLASLT_MATMUL_DESC_FAST_ACCUM`                       | 管理 FP8 快速累加模式的标志。启用时，问题执行可能更快，但代价是精度降低，因为中间结果不会定期提升到更高精度。默认值：0 - 快速累加模式被禁用 | int8_t                        |
| `ACBLASLT_MATMUL_DESC_BIAS_DATA_TYPE`                   | device 内存中偏置或偏置梯度向量的类型。偏置情况：参见 `ACBLASLT_EPILOGUE_BIAS`。若未设置（或设置为默认值 -1），则偏置向量元素与输出矩阵（Dtype）的元素类型相同，但有以下例外：computeType=`HGGC_R_32I` 且 `Ctype=HGGC_R_8I` 的 IMMA kernel，其中偏置向量元素与 alpha、beta 类型相同（`ACBLASLT_MATMUL_DESC_SCALE_TYPE=HGGC_R_32F`）。输出类型为 `HGGC_R_32F`、`HGGC_R_8F_E4M3` 或 `HGGC_R_8F_E5M2` 的 FP8 kernel。有关更多详细信息，请参见 `acblasLtMatmul()`。默认值：-1 | int32_t based on hggcDataType |
| `ACBLASLT_MATMUL_DESC_ATOMIC_SYNC_IN_COUNTERS_POINTER`  | 指向 matmul 消耗的输入原子计数器 device 数组的指针。当计数器达到零时，允许开始计算输出张量的相应块。默认值：NULL。  | int32_t *                     |
| `ACBLASLT_MATMUL_DESC_ATOMIC_SYNC_OUT_COUNTERS_POINTER` | 指向 matmul 产生的输出原子计数器 device 数组的指针。当输出张量相应块的计算完成时，matmul kernel 将计数器设置为零。在运行 matmul kernel 之前，所有计数器必须初始化为 1。默认值：NULL。参见[原子同步](#513-原子同步)。 | int32_t *                     |
| `ACBLASLT_MATMUL_DESC_ATOMIC_SYNC_NUM_CHUNKS_D_ROWS`    | 输出矩阵 D 行维度中的原子同步块数。每个块对应一个原子计数器。默认值：0（原子同步禁用）。 | int32_t                       |
| `ACBLASLT_MATMUL_DESC_ATOMIC_SYNC_NUM_CHUNKS_D_COLS`    | 输出矩阵 D 列维度中的原子同步块数。每个块对应一个原子计数器。默认值：0（原子同步禁用）。 | int32_t                       |
| `ACBLASLT_MATMUL_DESC_A_SCALE_MODE`                     | 矩阵 A 缩放因子的解释模式。默认值：0。 | int32_t                       |
| `ACBLASLT_MATMUL_DESC_B_SCALE_MODE`                     | 矩阵 B 缩放因子的解释模式。默认值：0。 | int32_t                       |
| `ACBLASLT_MATMUL_DESC_C_SCALE_MODE`                     | 矩阵 C 缩放因子的解释模式。默认值：0。 | int32_t                       |
| `ACBLASLT_MATMUL_DESC_D_SCALE_MODE`                     | 矩阵 D 缩放因子的解释模式。默认值：0。 | int32_t                       |
| `ACBLASLT_MATMUL_DESC_EPILOGUE_AUX_SCALE_MODE`          | 辅助矩阵（epilogue auxiliary）缩放因子的解释模式。默认值：0。 | int32_t                       |
| `ACBLASLT_MATMUL_DESC_D_OUT_SCALE_POINTER`              | 指向用于将矩阵 D 中的数据转换为计算数据类型范围的缩放因子的 device 指针。缩放因子值类型由 `ACBLASLT_MATMUL_DESC_D_OUT_SCALE_MODE` 定义。默认值：NULL。 | void *                        |
| `ACBLASLT_MATMUL_DESC_D_OUT_SCALE_MODE`                 | 输出矩阵 D 缩放因子的解释模式。默认值：0。 | int32_t                       |


#### 5.2.5. acblasLtMatmulTile_t {#525-acblasltmatmultile_t}

声明 matmul kernel 的 tile 尺寸（行 × 列）。命名规则：`ACBLASLT_MATMUL_TILE_<rows>x<cols>`。`ACBLASLT_MATMUL_TILE_UNDEFINED` 表示"由库自动决定"。

合法尺寸按面积分组列出（便于按算力 / 共享内存预算选择）：

| 类型 | 可用尺寸（行×列） |
| :--- | :--- |
| 未定义 | `UNDEFINED` |
| ≤ 64 元素 | `8x8` |
| 65–256 | `8x16`， `16x8`， `8x32`， `16x16`， `32x8` |
| 257–1024 | `8x64`， `16x32`， `32x16`， `64x8`， `32x32`， `32x64`， `64x32`， `64x64`， `64x96`， `96x64` |
| 1025–4096 | `32x128`， `128x32`， `64x128`， `128x64`， `96x128`， `128x128`， `128x160`， `160x128`， `192x128` |
| ≥ 4097 | `64x256`， `256x64`， `64x512`， `128x256`， `256x128`， `512x64` |

#### 5.2.6. acblasLtMatmulStages_t {#526-acblasltmatmulstages_t}

声明 stage 大小及对应的共享内存缓冲区数量，后者也就是 Kernel 的**流水线深度** 。命名规则：`ACBLASLT_MATMUL_STAGES_<size>x<count>`，`size` 是 stage 字节大小，`count` 是流水线深度。`UNDEFINED` 表示"由库自动决定"。

| Stage size | 可选深度 |
| :--- | :--- |
| 未定义 | `UNDEFINED` |
| 8   | `8x4`， `8x5` |
| 16  | `16x1`， `16x2`， `16x3`， `16x4`， `16x5`， `16x6`， `16x10`， `16x80` |
| 32  | `32x1`， `32x2`， `32x3`， `32x4`， `32x5`， `32x6`， `32x10` |
| 64  | `64x1`， `64x2`， `64x3`， `64x4`， `64x5`， `64x6`， `64x80` |
| 128 | `128x1`， `128x2`， `128x3`， `128x4`， `128x5`， `128x6` |

#### 5.2.7. acblasLtNumericalImplFlags_t {#527-acblasltnumericalimplflags_t}

`acblasLtNumericalImplFlags_t` 是一组**位标志** ，描述特定实现的数值行为细节。多个标志可通过位或运算符 `|` 组合使用。按维度分组如下。

**乘加指令家族**

| 枚举值 | 含义 |
| :--- | :--- |
| `ACBLASLT_NUMERICAL_IMPL_FLAGS_FMA`            | 实现基于 FMA（融合乘加） |
| `ACBLASLT_NUMERICAL_IMPL_FLAGS_HMMA`           | 基于 HMMA（半精度张量操作） |
| `ACBLASLT_NUMERICAL_IMPL_FLAGS_IMMA`           | 基于 IMMA（整数张量操作） |
| `ACBLASLT_NUMERICAL_IMPL_FLAGS_DMMA`           | 基于 DMMA（双精度张量操作） |
| `ACBLASLT_NUMERICAL_IMPL_FLAGS_TENSOR_OP_MASK` | 过滤掩码：包含上述任意张量操作的实现 |
| `ACBLASLT_NUMERICAL_IMPL_FLAGS_OP_TYPE_MASK`   | 过滤掩码：按乘加指令家族过滤 |

**累加器精度**

| 枚举值 | 含义 |
| :--- | :--- |
| `ACBLASLT_NUMERICAL_IMPL_FLAGS_ACCUMULATOR_16F`       | 半精度累加器 |
| `ACBLASLT_NUMERICAL_IMPL_FLAGS_ACCUMULATOR_32F`       | 单精度累加器 |
| `ACBLASLT_NUMERICAL_IMPL_FLAGS_ACCUMULATOR_64F`       | 双精度累加器 |
| `ACBLASLT_NUMERICAL_IMPL_FLAGS_ACCUMULATOR_32I`       | 32-bit 有符号整数累加器 |
| `ACBLASLT_NUMERICAL_IMPL_FLAGS_ACCUMULATOR_TYPE_MASK` | 过滤掩码：按累加器类型过滤 |

**点积输入精度**

| 枚举值 | 含义 |
| :--- | :--- |
| `ACBLASLT_NUMERICAL_IMPL_FLAGS_INPUT_16F`          | 半精度输入 |
| `ACBLASLT_NUMERICAL_IMPL_FLAGS_INPUT_16BF`         | bfloat16 输入 |
| `ACBLASLT_NUMERICAL_IMPL_FLAGS_INPUT_TF32`         | TF32 输入 |
| `ACBLASLT_NUMERICAL_IMPL_FLAGS_INPUT_32F`          | 单精度输入 |
| `ACBLASLT_NUMERICAL_IMPL_FLAGS_INPUT_64F`          | 双精度输入 |
| `ACBLASLT_NUMERICAL_IMPL_FLAGS_INPUT_8I`           | 8-bit 整数输入 |
| `ACBLASLT_NUMERICAL_IMPL_FLAGS_OP_INPUT_TYPE_MASK` | 过滤掩码：按点积输入类型过滤 |

#### 5.2.8. acblasLtMatrixLayout_t {#528-acblasltmatrixlayout_t}

`acblasLtMatrixLayout_t` 是矩阵布局描述符的不透明指针。

| 阶段 | 接口 |
| :--- | :--- |
| 创建 | `acblasLtMatrixLayoutCreate()` |
| 销毁 | `acblasLtMatrixLayoutDestroy()` |

可设置的属性键 [见 5.2.9](#529-acblasltmatrixlayoutattribute_t)。

#### 5.2.9. acblasLtMatrixLayoutAttribute_t {#529-acblasltmatrixlayoutattribute_t}

`acblasLtMatrixLayoutAttribute_t` 列出矩阵布局描述符可读/写的所有属性键。读/写分别通过 `acblasLtMatrixLayoutGetAttribute()` 与 `acblasLtMatrixLayoutSetAttribute()`。

| **属性名称**                          | **描述**                                              | **数据类型** |
| :--- | :--- | :--- |
| ACBLASLT_MATRIX_LAYOUT_TYPE                 | 指定数据精度类型。 | uint32_t      |
| ACBLASLT_MATRIX_LAYOUT_ORDER                | 指定矩阵数据的内存顺序。默认值为 ACBLASLT_ORDER_COL。参见 `acblasLtOrder_t`。 | int32_t       |
| ACBLASLT_MATRIX_LAYOUT_ROWS                 | 描述矩阵中的行数。通常仅支持可以表示为 `int32_t` 的值。 | uint64_t      |
| ACBLASLT_MATRIX_LAYOUT_COLS                 | 描述矩阵中的列数。通常仅支持可以表示为 `int32_t` 的值。 | uint64_t      |
| ACBLASLT_MATRIX_LAYOUT_LD                   | 矩阵的前导维度。对于 ACBLASLT_ORDER_COL，这是矩阵列的步幅（以元素为单位）。另请参见 `acblasLtOrder_t`。目前仅支持非负值。必须足够大以确保矩阵内存位置不重叠（例如，在 ACBLASLT_ORDER_COL 情况下大于或等于 ACBLASLT_MATRIX_LAYOUT_ROWS）。 | int64_t       |
| ACBLASLT_MATRIX_LAYOUT_BATCH_COUNT          | 要在批量中执行的 matmul 操作数量。默认值为 1。 | int32_t       |
| ACBLASLT_MATRIX_LAYOUT_STRIDED_BATCH_OFFSET | 步长批量操作中下一个矩阵的步幅（以元素为单位）。默认值为 0。 | int64_t       |

#### 5.2.10. acblasLtMatrixTransformDesc_t {#5210-acblasltmatrixtransformdesc_t}

`acblasLtMatrixTransformDesc_t` 是矩阵变换（`acblasLtMatrixTransform`）描述符的不透明指针。

| 阶段 | 接口 |
| :--- | :--- |
| 创建 | `acblasLtMatrixTransformDescCreate()` |
| 销毁 | `acblasLtMatrixTransformDescDestroy()` |

可设置的属性键 [见 5.2.11](#5211-acblasltmatrixtransformdescattributes_t)。

#### 5.2.11. acblasLtMatrixTransformDescAttributes_t {#5211-acblasltmatrixtransformdescattributes_t}

`acblasLtMatrixTransformDescAttributes_t` 列出矩阵变换描述符的所有可配置属性键，主要用于约定缩放类型、指针模式、对矩阵 A/B 的转置操作。读/写分别通过 `acblasLtMatrixTransformDescGetAttribute()` 与 `acblasLtMatrixTransformDescSetAttribute()`。

| **变换属性名称**                | **描述**                                              | **数据类型** |
| :--- | :--- | :--- |
| ACBLASLT_MATRIX_TRANSFORM_DESC_SCALE_TYPE   | 缩放类型。输入被转换为缩放类型以进行缩放和求和，然后将结果转换为输出类型以存储在内存中。有关支持的数据类型，请参见 `hggcDataType_t`。 | int32_t       |
| ACBLASLT_MATRIX_TRANSFORM_DESC_POINTER_MODE | 指定标量 alpha 和 beta 是通过引用传递的，无论是在 host 还是 device 上。默认值为：ACBLASLT_POINTER_MODE_HOST（即在 host 上）。参见 `acblasLtPointerMode_t`。 | int32_t       |
| ACBLASLT_MATRIX_TRANSFORM_DESC_TRANSA       | 指定应对矩阵 A 执行的操作类型。默认值为：ACBLAS_OP_N（即非转置操作）。参见 `acblasOperation_t`。 | int32_t       |
| ACBLASLT_MATRIX_TRANSFORM_DESC_TRANSB       | 指定应对矩阵 B 执行的操作类型。默认值为：ACBLAS_OP_N（即非转置操作）。参见 `acblasOperation_t`。 | int32_t       |

#### 5.2.12. acblasLtOrder_t {#5212-acblasltorder_t}

矩阵在内存中的数据排序方式。除了常规的列/行优先，还提供几种针对 Tensor Cell 优化的 tiled 布局。

| 枚举值 | 排序方式 | 前导维度（`ld`） |
| :--- | :--- | :--- |
| `ACBLASLT_ORDER_COL`          | 列优先 | 到下一列起点的元素步幅 |
| `ACBLASLT_ORDER_ROW`          | 行优先 | 到下一行起点的元素步幅 |
| `ACBLASLT_ORDER_COL32`        | 以 32 列为一个 tile 的列优先 tile 排列 | 到下一组 32 列起点的元素步幅；例：33 列 × 2 行 ⇒ `ld ≥ 32 × 2 = 64` |
| `ACBLASLT_ORDER_COL4_4R2_8C`  | 32 列 × 8 行复合 tile 的列优先排列；每个 tile 内由 4 列 × 4 行交错的次级 tile 构成（按奇偶行交替） | 到下一个 32 列 × 8 行 tile 起点的元素步幅；例：33 列 × 1 行 ⇒ `ld ≥ 32 × 8 × 1 = 256` |
| `ACBLASLT_ORDER_COL32_2R_4R4` | 32 列 × 32 行复合 tile 的列优先排列；tile 内元素偏移 = `(((row%8)/2*4 + row/8) * 2 + row%2) * 32 + col` | 到下一个 32 列 × 32 行 tile 起点的元素步幅；例：33 列 × 1 行 ⇒ `ld ≥ 32 × 32 × 1 = 1024` |

#### 5.2.13. acblasLtPointerMode_t {#5213-acblasltpointermode_t}

`alpha` / `beta` 指针在主机/设备上的传递方式，比基础的 `acblasPointerMode_t` 多了 device 向量、零值等组合，便于支持每行不同缩放因子的 GEMM。

| 枚举值 | 数值 | `alpha` | `beta` |
| :--- | :--- | :--- | :--- |
| `ACBLASLT_POINTER_MODE_HOST`                       | = `ACBLAS_POINTER_MODE_HOST` | host 单值 | host 单值 |
| `ACBLASLT_POINTER_MODE_DEVICE`                     | = `ACBLAS_POINTER_MODE_DEVICE` | device 单值 | device 单值 |
| `ACBLASLT_POINTER_MODE_DEVICE_VECTOR`              | 2 | device 向量（长度 = D 行数） | device 向量 |
| `ACBLASLT_POINTER_MODE_ALPHA_DEVICE_VECTOR_BETA_ZERO` | 3 | device 向量 | 固定为 0 |
| `ACBLASLT_POINTER_MODE_ALPHA_DEVICE_VECTOR_BETA_HOST` | 4 | device 向量 | host 单值 |

#### 5.2.14. acblasLtPointerModeMask_t {#5214-acblasltpointermodemask_t}

与 `acblasLtPointerMode_t` 一一对应的位掩码版本，用于在能力查询/搜索时**声明或过滤** 支持的指针模式集合。

| 枚举值 | 数值 | 对应 `acblasLtPointerMode_t` |
| :--- | :--- | :--- |
| `ACBLASLT_POINTER_MODE_MASK_HOST`                       | 1  | `ACBLASLT_POINTER_MODE_HOST` |
| `ACBLASLT_POINTER_MODE_MASK_DEVICE`                     | 2  | `ACBLASLT_POINTER_MODE_DEVICE` |
| `ACBLASLT_POINTER_MODE_MASK_DEVICE_VECTOR`              | 4  | `ACBLASLT_POINTER_MODE_DEVICE_VECTOR` |
| `ACBLASLT_POINTER_MODE_MASK_ALPHA_DEVICE_VECTOR_BETA_ZERO` | 8  | `ACBLASLT_POINTER_MODE_ALPHA_DEVICE_VECTOR_BETA_ZERO` |
| `ACBLASLT_POINTER_MODE_MASK_ALPHA_DEVICE_VECTOR_BETA_HOST` | 16 | `ACBLASLT_POINTER_MODE_ALPHA_DEVICE_VECTOR_BETA_HOST` |

#### 5.2.15. acblasLtReductionScheme_t {#5215-acblasltreductionscheme_t}

控制 split-K 模式下分块结果的**归约方式** 。

| 枚举值 | 归约位置 | 累加精度 | 工作空间占用 |
| :--- | :--- | :--- | :--- |
| `ACBLASLT_REDUCTION_SCHEME_NONE`         | 无归约 | — | — |
| `ACBLASLT_REDUCTION_SCHEME_INPLACE`      | 输出缓冲区原地累加 | 输出类型 | 仅顺序保证计数器 |
| `ACBLASLT_REDUCTION_SCHEME_COMPUTE_TYPE` | 用户工作空间中外置归约 | 计算类型 | 必须显式提供工作空间 |
| `ACBLASLT_REDUCTION_SCHEME_OUTPUT_TYPE`  | 用户工作空间中外置归约 | 输出类型 | 必须显式提供工作空间 |
| `ACBLASLT_REDUCTION_SCHEME_MASK`         | — | — | 表示「允许所有归约方案」的掩码 |

### 5.3. API 函数 {#53-api-函数}

#### 5.3.1. acblasLtCreate() {#531-acblasltcreate}

```cpp
acblasStatus_t
acblasLtCreate(acblasLtHandle_t* lightHandle)
```

初始化 acblasLt 库，创建 library context 句柄。在 host 和 device 上分配轻量级硬件资源，必须在任何其他 acblasLt 调用之前调用。

acblasLt 库上下文与当前 HGGC device 绑定。要在多个 device 上使用库，应为每个 device 创建一个 acblasLt 句柄。

**参数：**

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `lightHandle`   |            | 输出             | 指向为创建的 acblasLt 上下文分配的 acblasLt 句柄的指针。 |

**返回：**
返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_ALLOC_FAILED`：内存分配失败。
- `ACBLAS_STATUS_INVALID_VALUE`：参数无效。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 5.3.2. acblasLtDestroy() {#532-acblasltdestroy}

```cpp
acblasStatus_t
acblasLtDestroy(acblasLtHandle_t lightHandle)
```

释放 acblasLt 库使用的硬件资源。通常是该句柄的最后一次调用；释放过程隐式调用 `hggcDeviceSynchronize()`，建议尽量减少 Create / Destroy 的调用频次。

**参数：**
| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `lightHandle`   |            | 输入              | 指向要销毁的 acblasLt 句柄的指针。 |

**返回：**

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：acblasLt 库未初始化。
- `ACBLAS_STATUS_INVALID_VALUE`：`lightHandle` == NULL。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 5.3.3. acblasLtMatmul() {#533-acblasltmatmul}

```cpp
acblasStatus_t
acblasLtMatmul(
                acblasLtHandle_t lightHandle,
                acblasLtMatmulDesc_t computeDesc,
                const void *alpha,
                const void *A,
                acblasLtMatrixLayout_t Adesc,
                const void *B,
                acblasLtMatrixLayout_t Bdesc,
                const void *beta,
                const void *C,
                acblasLtMatrixLayout_t Cdesc,
                void *D,
                acblasLtMatrixLayout_t Ddesc,
                const void *algo,
                void *workspace,
                size_t workspaceSizeInBytes,
                hggcStream_t stream);
```

计算矩阵乘法，生成输出矩阵 D：

$$D = \alpha \cdot (A \cdot B) + \beta \cdot C$$

其中 A、B 和 C 为输入矩阵，alpha 和 beta 为输入标量。

!!! note
    支持原地（C == D 且 Cdesc == Ddesc）和异址（C != D，须相同数据类型、行列数、批量大小与内存顺序）两种模式。异址情况下，C 的前导维度可与 D 不同，具体而言，C 的前导维度可为 0 以实现行或列广播。若省略 C desc，则默认与 D desc 相同。

工作空间指针须至少对齐到 256 字节边界。关于 workspaceSizeInBytes 的建议与 `acblasSetWorkspace()` 部分所述相同。

`acblasLtMatmul()` 支持以下 computeType、scaleType、Atype/Btype 和 Ctype。

**表 1：当 A、B、C 和 D 为常规列主序或行主序矩阵时**

| **计算类型** | **缩放类型** | **A 类型/B 类型** | **C 类型** | **偏置类型** |
| :--- | :--- | :--- | :--- | :--- |
| ACBLAS_COMPUTE_16F 或 ACBLAS_COMPUTE_16F_PEDANTIC | HGGC_R_16F | HGGC_R_16F | HGGC_R_16F | HGGC_R_16F |
| ACBLAS_COMPUTE_32I 或 ACBLAS_COMPUTE_32I_PEDANTIC | HGGC_R_32I | HGGC_R_8I | HGGC_R_32I | 不支持 epilogue |
| ACBLAS_COMPUTE_32I 或 ACBLAS_COMPUTE_32I_PEDANTIC | HGGC_R_32F | HGGC_R_8I | HGGC_R_8I | 不支持 epilogue |
| ACBLAS_COMPUTE_32F 或 ACBLAS_COMPUTE_32F_PEDANTIC | HGGC_R_32F | HGGC_R_16BF | HGGC_R_16BF | HGGC_R_16BF |
| ACBLAS_COMPUTE_32F 或 ACBLAS_COMPUTE_32F_PEDANTIC | HGGC_R_16F | HGGC_R_16F | HGGC_R_16F | HGGC_R_16F |
| ACBLAS_COMPUTE_32F 或 ACBLAS_COMPUTE_32F_PEDANTIC | HGGC_R_32F | HGGC_R_8I | HGGC_R_32F | 不支持 epilogue |
| ACBLAS_COMPUTE_32F 或 ACBLAS_COMPUTE_32F_PEDANTIC | HGGC_R_32F | HGGC_R_16BF | HGGC_R_32F | HGGC_R_32F |
| ACBLAS_COMPUTE_32F 或 ACBLAS_COMPUTE_32F_PEDANTIC | HGGC_R_32F | HGGC_R_16F | HGGC_R_32F | HGGC_R_32F |
| ACBLAS_COMPUTE_32F 或 ACBLAS_COMPUTE_32F_PEDANTIC | HGGC_R_32F | HGGC_R_32F | HGGC_R_32F | HGGC_R_32F |
| ACBLAS_COMPUTE_32F_FAST_16F 或 ACBLAS_COMPUTE_32F_FAST_16BF 或 ACBLAS_COMPUTE_32F_FAST_TF32 | HGGC_R_32F | HGGC_R_32F | HGGC_R_32F | HGGC_R_32F |
| ACBLAS_COMPUTE_64F 或 ACBLAS_COMPUTE_64F_PEDANTIC | HGGC_R_64F | HGGC_R_64F | HGGC_R_64F | HGGC_R_64F |

!!! note
    偏置类型仅适用于启用偏置的 epilogue（如 ACBLASLT_EPILOGUE_BIAS 及其变体）。

要使用 IMMA kernel，须满足以下要求集之一，首选第一个：

**1. 使用常规数据排序：**

- 所有矩阵指针须 4 字节对齐。为获得更佳性能，建议使用 16 字节对齐。
- 矩阵 A、B、C 的前导维度须为 4 的倍数。
- 仅支持 "TN" 格式 - A 必须转置，B 不转置。
- 指针模式可以是 ACBLASLT_POINTER_MODE_HOST、ACBLASLT_POINTER_MODE_DEVICE 或 ACBLASLT_POINTER_MODE_ALPHA_DEVICE_VECTOR_BETA_HOST。使用后一种模式时，kernel 支持 ACBLASLT_MATMUL_DESC_ALPHA_VECTOR_BATCH_STRIDE 属性。
- 维度 m 和 k 必须是 4 的倍数。

**2. 使用 IMMA 特定的数据排序** - 矩阵 A、C、D 使用 ACBLASLT_ORDER_COL32，矩阵 B 使用 ACBLASLT_ORDER_COL4_4R2_8C 或 ACBLASLT_ORDER_COL32_2R_4R4：

- 矩阵 A、B、C 的前导维度必须满足内存排序特定的条件（参见 `acblasLtOrder_t`）。

- Matmul 描述符必须在矩阵 B 上指定 `ACBLAS_OP_T`，在矩阵 A 和 C 上指定 `ACBLAS_OP_N`（默认值）。

- 若使用 scaleType HGGC_R_32I，则 alpha 和 beta 唯一支持的值为 0 或 1。

- 指针模式可以是 ACBLASLT_POINTER_MODE_HOST、ACBLASLT_POINTER_MODE_DEVICE、ACBLASLT_POINTER_MODE_DEVICE_VECTOR 或 ACBLASLT_POINTER_MODE_ALPHA_DEVICE_VECTOR_BETA_ZERO。这些 kernel 不支持 ACBLASLT_MATMUL_DESC_ALPHA_VECTOR_BATCH_STRIDE。

- 仅支持 "NT" 格式 - A 不转置（N），B 必须转置（T）。

**当 A、B、C 和 D 使用 IMMA 布局时**
| 计算类型                                      | 缩放类型  | A 类型/B 类型 | C 类型      | 偏置类型                           |
| :--- | :--- | :--- | :--- | :--- |
| ACBLAS_COMPUTE_32I 或 ACBLAS_COMPUTE_32I_PEDANTIC | HGGC_R_32I | HGGC_R_8I   | HGGC_R_32I | 不支持非默认 epilogue |
| ACBLAS_COMPUTE_32I 或 ACBLAS_COMPUTE_32I_PEDANTIC | HGGC_R_32F | HGGC_R_8I   | HGGC_R_8I  | HGGC_R_32F                         |

要使用 FP8 kernel，必须满足以下要求集：

- 所有矩阵维度必须满足张量单元使用中列出的最佳要求（即指针和矩阵维度必须支持 16 字节对齐）。

- A 必须转置，B 不转置（"TN" 格式）。

- 计算类型必须是 `ACBLAS_COMPUTE_32F`。

- 缩放类型必须是 HGGC_R_32F。

使用 FP8 kernel 时请参见下表：

**表 2：当 A、B、C 和 D 使用 FP8 布局时**

| **A 类型** | **B 类型** | **C 类型** | **D 类型** | **偏置类型** |
| :--- | :--- | :--- | :--- | :--- |
| HGGC_R_8F_E4M3 | HGGC_R_8F_E4M3 | HGGC_R_16BF | HGGC_R_16BF    | HGGC_R_16BF |
| HGGC_R_8F_E4M3 | HGGC_R_8F_E4M3 | HGGC_R_16BF | HGGC_R_8F_E4M3 | HGGC_R_16BF |
| HGGC_R_8F_E4M3 | HGGC_R_8F_E4M3 | HGGC_R_16BF | HGGC_R_8F_E5M2 | HGGC_R_16BF |
| HGGC_R_8F_E4M3 | HGGC_R_8F_E4M3 | HGGC_R_16F  | HGGC_R_16F     | HGGC_R_16F  |
| HGGC_R_8F_E4M3 | HGGC_R_8F_E4M3 | HGGC_R_16F  | HGGC_R_8F_E4M3 | HGGC_R_16F  |
| HGGC_R_8F_E4M3 | HGGC_R_8F_E4M3 | HGGC_R_16F  | HGGC_R_8F_E5M2 | HGGC_R_16F  |
| HGGC_R_8F_E4M3 | HGGC_R_8F_E4M3 | HGGC_R_32F  | HGGC_R_32F     | HGGC_R_16BF |
| HGGC_R_8F_E5M2 | HGGC_R_8F_E4M3 | HGGC_R_16BF | HGGC_R_16BF    | HGGC_R_16BF |
| HGGC_R_8F_E5M2 | HGGC_R_8F_E4M3 | HGGC_R_16BF | HGGC_R_8F_E4M3 | HGGC_R_16BF |
| HGGC_R_8F_E5M2 | HGGC_R_8F_E4M3 | HGGC_R_16BF | HGGC_R_8F_E5M2 | HGGC_R_16BF |
| HGGC_R_8F_E5M2 | HGGC_R_8F_E4M3 | HGGC_R_16F  | HGGC_R_16F     | HGGC_R_16F  |
| HGGC_R_8F_E5M2 | HGGC_R_8F_E4M3 | HGGC_R_16F  | HGGC_R_8F_E4M3 | HGGC_R_16F  |
| HGGC_R_8F_E5M2 | HGGC_R_8F_E4M3 | HGGC_R_16F  | HGGC_R_8F_E5M2 | HGGC_R_16F  |
| HGGC_R_8F_E5M2 | HGGC_R_8F_E4M3 | HGGC_R_32F  | HGGC_R_32F     | HGGC_R_16BF |
| HGGC_R_8F_E4M3 | HGGC_R_8F_E5M2 | HGGC_R_16BF | HGGC_R_16BF    | HGGC_R_16BF |
| HGGC_R_8F_E4M3 | HGGC_R_8F_E5M2 | HGGC_R_16BF | HGGC_R_8F_E4M3 | HGGC_R_16BF |
| HGGC_R_8F_E4M3 | HGGC_R_8F_E5M2 | HGGC_R_16BF | HGGC_R_8F_E5M2 | HGGC_R_16BF |
| HGGC_R_8F_E4M3 | HGGC_R_8F_E5M2 | HGGC_R_16F  | HGGC_R_16F     | HGGC_R_16F  |
| HGGC_R_8F_E4M3 | HGGC_R_8F_E5M2 | HGGC_R_16F  | HGGC_R_8F_E4M3 | HGGC_R_16F  |
| HGGC_R_8F_E4M3 | HGGC_R_8F_E5M2 | HGGC_R_16F  | HGGC_R_8F_E5M2 | HGGC_R_16F  |
| HGGC_R_8F_E4M3 | HGGC_R_8F_E5M2 | HGGC_R_32F  | HGGC_R_32F     | HGGC_R_16BF |

!!! note
    - 仅支持 (A, B) 为 (E4M3, E4M3)、(E5M2, E4M3)、(E4M3, E5M2) 三种组合；不支持 B = E5M2 与 A = E5M2 同时出现。
    - C 类型为 `HGGC_R_32F` 时，D 类型仅支持 `HGGC_R_32F`，且偏置类型为 `HGGC_R_16BF`。
    - C 类型为 `HGGC_R_16BF` 或 `HGGC_R_16F` 时，D 类型可为对应的 16 位类型或所选 FP8 类型（E4M3 / E5M2）。

**参数：**

| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `lightHandle`             |                | 输入              | 指向为 acblasLt 上下文分配的 acblasLt 句柄的指针。参见 `acblasLtHandle_t`。 |
| `computeDesc`             |                | 输入              | 指向先前创建的 `acblasLtMatmulDesc_t` 类型矩阵乘法描述符的句柄。 |
| `alpha`， `beta`             | host 或 device | 输入              | 指向乘法中使用的标量的指针。          |
| `A`， `B`， `C`             | device         | 输入              | 指向与相应描述符 `Adesc`、`Bdesc` 和 `Cdesc` 关联的真武 PPU 内存的指针。 |
| `Adesc`， `Bdesc`， `Cdesc` |                | 输入              | 指向先前创建的 `acblasLtMatrixLayout_t` 类型描述符的句柄。 |
| `D`                       | device         | 输出             | 指向与描述符 `Ddesc` 关联的真武 PPU 内存的指针。 |
| `Ddesc`                   |                | 输入              | 指向先前创建的 `acblasLtMatrixLayout_t` 类型描述符的句柄。 |
| `algo`                    |                | 输入              | 当前版本应传 NULL，由库内部自动选择实现。 |
| `workspace`               | device         | 输入              | 指向在真武 PPU 内存中分配的工作空间缓冲区的指针。必须 256B 对齐（即地址的最低 8 位必须为 0）。 |
| `workspaceSizeInBytes`    |                | 输入              | 工作空间的大小。                                       |
| `stream`                  | host           | 输入              | 将提交所有真武 PPU 工作的 HGGC stream。    |

**返回：**

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_INVALID_VALUE`：参数无效。
- `ACBLAS_STATUS_NOT_SUPPORTED`：不支持。
- `ACBLAS_STATUS_ARCH_MISMATCH`：架构不匹配。
- `ACBLAS_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 5.3.4. acblasLtMatmulDescCreate() {#534-acblasltmatmuldesccreate}

```cpp
acblasStatus_t
acblasLtMatmulDescCreate(acblasLtMatmulDesc_t *matmulDesc,
                            acblasComputeType_t computeType,
                            hggcDataType_t scaleType);
```

分配并创建矩阵乘法描述符（不透明结构）。

**参数：**
| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `matmulDesc`    |            | 输出             | 指向保存所创建的矩阵乘法描述符的结构体的指针。参见 `acblasLtMatmulDesc_t`。 |
| `computeType`   |            | 输入              | 指定所创建的矩阵乘法描述符的数据精度的枚举值。参见 `acblasComputeType_t`。 |
| `scaleType`     |            | 输入              | 指定所创建的矩阵乘法描述符的缩放类型精度的枚举值。参见 `hggcDataType`。 |

**返回：**
返回码：

- `ACBLAS_STATUS_ALLOC_FAILED`：内存无法分配。
- `ACBLAS_STATUS_SUCCESS`：操作成功。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 5.3.5. acblasLtMatmulDescInit() {#535-acblasltmatmuldescinit}

```cpp
acblasStatus_t
acblasLtMatmulDescInit(acblasLtMatmulDesc_t matmulDesc,
                        acblasComputeType_t computeType,
                        hggcDataType_t scaleType);
```

在已分配的矩阵乘法描述符中执行初始化。

**参数：**
| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `matmulDesc`    |            | 输出             | 指向保存所初始化的矩阵乘法描述符的结构体的指针。参见 `acblasLtMatmulDesc_t`。 |
| `computeType`   |            | 输入              | 指定所初始化的矩阵乘法描述符的数据精度的枚举值。参见 `acblasComputeType_t`。 |
| `scaleType`     |            | 输入              | 指定所初始化的矩阵乘法描述符的缩放类型精度的枚举值。参见 `hggcDataType`。 |

**返回：**
返回码：

- `ACBLAS_STATUS_ALLOC_FAILED`：内存无法分配。
- `ACBLAS_STATUS_SUCCESS`：操作成功。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 5.3.6. acblasLtMatmulDescDestroy() {#536-acblasltmatmuldescdestroy}

```cpp
acblasStatus_t
acblasLtMatmulDescDestroy(
                            acblasLtMatmulDesc_t matmulDesc);
```

销毁先前创建的矩阵乘法描述符。

**参数：**
| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `matmulDesc`    |            | 输入              | 指向保存待销毁的矩阵乘法描述符的结构体的指针。参见 `acblasLtMatmulDesc_t`。 |

**返回：**
返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 5.3.7. acblasLtMatmulDescGetAttribute() {#537-acblasltmatmuldescgetattribute}

```cpp
acblasStatus_t
acblasLtMatmulDescGetAttribute(
                                acblasLtMatmulDesc_t matmulDesc,
                                acblasLtMatmulDescAttributes_t attr,
                                void *buf,
                                size_t sizeInBytes,
                                size_t *sizeWritten);
```

查询矩阵乘法描述符的属性值。

**参数：**
| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `matmulDesc`    |            | 输入              | 指向保存待查询的矩阵乘法描述符的结构体的指针。参见 `acblasLtMatmulDesc_t`。 |
| `attr`          |            | 输入              | 待检索的属性。参见 `acblasLtMatmulDescAttributes_t`。 |
| `buf`           |            | 输出             | 包含检索到的属性值的内存地址。 |
| `sizeInBytes`   |            | 输入              | 用于验证的 `buf` 缓冲区大小（以字节为单位）。            |
| `sizeWritten`   |            | 输出             | 仅当返回值为 ACBLAS_STATUS_SUCCESS 时有效。若 `sizeInBytes` 非零：则 `sizeWritten` 是实际写入的字节数；若 `sizeInBytes` 为 0：则 `sizeWritten` 是写入完整内容所需的字节数。 |

**返回：**
返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_INVALID_VALUE`：参数无效。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 5.3.8. acblasLtMatmulDescSetAttribute() {#538-acblasltmatmuldescsetattribute}

```cpp
acblasStatus_t
acblasLtMatmulDescSetAttribute(
                                acblasLtMatmulDesc_t matmulDesc,
                                acblasLtMatmulDescAttributes_t attr,
                                const void *buf,
                                size_t sizeInBytes);

```

为矩阵乘法描述符设置指定属性值（属性键来自 `acblasLtMatmulDescAttributes_t`）。

**参数：**
| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `matmulDesc`    |            | 输入              | 指向保存待设置的矩阵乘法描述符的结构体的指针。参见 `acblasLtMatmulDesc_t`。 |
| `attr`          |            | 输入              | 待设置的属性。参见 `acblasLtMatmulDescAttributes_t`。 |
| `buf`           |            | 输入              | 指定属性应设置的值。    |
| `sizeInBytes`   |            | 输入              | 用于验证的 `buf` 缓冲区大小（以字节为单位）。            |

**返回：**
返回码：

- `ACBLAS_STATUS_INVALID_VALUE`：`buf` 为 NULL 或 `sizeInBytes` 与所选属性的内部存储大小不匹配。
- `ACBLAS_STATUS_SUCCESS`：操作成功。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 5.3.9. acblasLtMatrixLayoutCreate() {#539-acblasltmatrixlayoutcreate}

```cpp
acblasStatus_t
acblasLtMatrixLayoutCreate(acblasLtMatrixLayout_t *matLayout,
                            hggcDataType type,
                            uint64_t rows,
                            uint64_t cols,
                            int64_t ld);
```

分配并创建矩阵布局描述符（不透明结构）。

**参数：**
| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `matLayout`     |            | 输出             | 指向保存所创建的矩阵布局描述符的结构体的指针。参见 `acblasLtMatrixLayout_t`。 |
| `type`          |            | 输入              | 指定所创建的矩阵布局描述符的数据精度的枚举值。参见 `hggcDataType`。 |
| `rows, cols`    |            | 输入              | 矩阵的行数和列数。                    |
| `ld`            |            | 输入              | 矩阵的前导维度。在列优先布局中，这是跳转到下一列的元素数。因此 ld >= m（行数）。 |

**返回：**
返回码：

- `ACBLAS_STATUS_ALLOC_FAILED`：内存无法分配。
- `ACBLAS_STATUS_SUCCESS`：操作成功。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 5.3.10. acblasLtMatrixLayoutInit() {#5310-acblasltmatrixlayoutinit}

```cpp
acblasStatus_t
acblasLtMatrixLayoutInit(acblasLtMatrixLayout_t matLayout,
                        hggcDataType type,
                        uint64_t rows,
                        uint64_t cols,
                        int64_t ld);
```

在已分配的描述符中执行矩阵布局初始化。

**参数：**
| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `matLayout`     |            | 输出             | 指向保存所初始化的矩阵布局描述符的结构体的指针。参见 `acblasLtMatrixLayout_t`。 |
| `type`          |            | 输入              | 指定所初始化的矩阵布局描述符的数据精度的枚举值。参见 `hggcDataType`。 |
| `rows, cols`    |            | 输入              | 矩阵的行数和列数。                    |
| `ld`            |            | 输入              | 矩阵的前导维度。在列优先布局中，这是跳转到下一列的元素数。因此 ld >= m（行数）。 |

**返回：**
返回码：

- `ACBLAS_STATUS_ALLOC_FAILED`：内存无法分配。
- `ACBLAS_STATUS_SUCCESS`：操作成功。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 5.3.11. acblasLtMatrixLayoutDestroy() {#5311-acblasltmatrixlayoutdestroy}

```cpp
acblasStatus_t
acblasLtMatrixLayoutDestroy(
                            acblasLtMatrixLayout_t matLayout);
```

销毁先前创建的矩阵布局描述符。

**参数：**
| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `matLayout`     |            | 输入              | 指向保存待销毁的矩阵布局描述符的结构体的指针。参见 `acblasLtMatrixLayout_t`。 |

**返回：**

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 5.3.12. acblasLtMatrixLayoutGetAttribute() {#5312-acblasltmatrixlayoutgetattribute}

```cpp
acblasStatus_t
acblasLtMatrixLayoutGetAttribute(
                                acblasLtMatrixLayout_t matLayout,
                                acblasLtMatrixLayoutAttribute_t attr,
                                void *buf,
                                size_t sizeInBytes,
                                size_t *sizeWritten);
```

查询矩阵布局描述符的属性值。

**参数：**
| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `matLayout`     |            | 输入              | 指向保存待查询的矩阵布局描述符的结构体的指针。参见 `acblasLtMatrixLayout_t`。 |
| `attr`          |            | 输入              | 正在查询的属性。参见 `acblasLtMatrixLayoutAttribute_t`。 |
| `buf`           |            | 输出             | 返回的属性值。               |
| `sizeInBytes`   |            | 输入              | 用于验证的 `buf` 缓冲区大小（以字节为单位）。            |
| `sizeWritten`   |            | 输出             | 仅当返回值为 ACBLAS_STATUS_SUCCESS 时有效。若 `sizeInBytes` 非零：则 `sizeWritten` 是实际写入的字节数；若 `sizeInBytes` 为 0：则 `sizeWritten` 是写入完整内容所需的字节数。 |

**返回：**
返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_INVALID_VALUE`：参数无效。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 5.3.13. acblasLtMatrixLayoutSetAttribute() {#5313-acblasltmatrixlayoutsetattribute}

```cpp
acblasStatus_t
acblasLtMatrixLayoutSetAttribute(
                                acblasLtMatrixLayout_t matLayout,
                                acblasLtMatrixLayoutAttribute_t attr,
                                const void *buf,
                                size_t sizeInBytes);
```

为矩阵布局描述符设置指定属性值。

**参数：**
| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `matLayout`     |            | 输入              | 指向保存待设置的矩阵布局描述符的结构体的指针。参见 `acblasLtMatrixLayout_t`。 |
| `attr`          |            | 输入              | 待设置的属性。参见 `acblasLtMatrixLayoutAttribute_t`。 |
| `buf`           |            | 输入              | 指定属性应设置的值。    |
| `sizeInBytes`   |            | 输入              | `buf` 属性缓冲区的大小。                         |

**返回：**
返回码：

- `ACBLAS_STATUS_INVALID_VALUE`：`buf` 为 NULL 或 `sizeInBytes` 与所选属性的内部存储大小不匹配。
- `ACBLAS_STATUS_SUCCESS`：操作成功。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 5.3.14. acblasLtMatrixTransform() {#5314-acblasltmatrixtransform}

```cpp
acblasStatus_t acblasLtMatrixTransform(
      acblasLtHandle_t lightHandle,
      acblasLtMatrixTransformDesc_t transformDesc,
      const void *alpha,
      const void *A,
      acblasLtMatrixLayout_t Adesc,
      const void *beta,
      const void *B,
      acblasLtMatrixLayout_t Bdesc,
      void *C,
      acblasLtMatrixLayout_t Cdesc,
      hggcStream_t stream);
```

对矩阵 A 和 B 执行变换操作，生成输出矩阵 C：

$$C = \alpha \cdot \text{transformation}(A) + \beta \cdot \text{transformation}(B)$$

其中 A、B 为输入矩阵，$\alpha$ 和 $\beta$ 为输入标量。变换操作由 transformDesc 指针定义。可用于更改数据的内存顺序或进行缩放和位移。

**参数：**
| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `lightHandle`             |                | 输入              | 指向为 acblasLt 上下文分配的 acblasLt 句柄的指针。参见 `acblasLtHandle_t`。 |
| `transformDesc`           |                | 输入              | 指向保存矩阵变换操作的不透明描述符的指针。参见 `acblasLtMatrixTransformDesc_t`。 |
| `alpha`， `beta`             | host 或 device | 输入              | 指向乘法中使用的标量的指针。          |
| `A`， `B`                    | device         | 输入              | 指向与相应描述符 `Adesc`、`Bdesc` 关联的真武 PPU 内存的指针。 |
| `C`                       | device         | 输出              | 指向与描述符 `Cdesc` 关联的真武 PPU 内存的指针。 |
| `Adesc`， `Bdesc`， `Cdesc`  |                | 输入              | 指向先前创建的 `acblasLtMatrixLayout_t` 类型描述符的句柄。若相应指针为 NULL 且相应标量为零，则 `Adesc` 或 `Bdesc` 可以为 NULL。 |
| `stream`                  | host           | 输入              | 将提交所有真武 PPU 工作的 HGGC stream。    |

**返回：**
返回码：

- `ACBLAS_STATUS_NOT_INITIALIZED`：acblasLt 句柄未初始化。
- `ACBLAS_STATUS_INVALID_VALUE`：参数冲突或处于不可能的配置中。例如，当 `A` 不为 NULL，但 `Adesc` 为 NULL。
- `ACBLAS_STATUS_NOT_SUPPORTED`：所选 device 上的当前实现不支持配置的操作。
- `ACBLAS_STATUS_ARCH_MISMATCH`：配置的操作无法使用所选 device 运行。
- `ACBLAS_STATUS_EXECUTION_FAILED`：HGGC 报告了来自 device 的执行错误。
- `ACBLAS_STATUS_SUCCESS`：操作成功。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 5.3.15. acblasLtMatrixTransformDescCreate() {#5315-acblasltmatrixtransformdesccreate}

```cpp
acblasStatus_t
acblasLtMatrixTransformDescCreate(
                                    acblasLtMatrixTransformDesc_t *transformDesc,
                                    hggcDataType scaleType);
```

分配并创建矩阵变换描述符（不透明结构）。

**参数：**
| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `transformDesc` |            | 输出             | 指向保存所创建的矩阵变换描述符的结构体的指针。参见 `acblasLtMatrixTransformDesc_t`。 |
| `scaleType`     |            | 输入              | 指定所创建的矩阵变换描述符的缩放类型精度的枚举值。参见 `hggcDataType`。 |

**返回：**
返回码：

- `ACBLAS_STATUS_ALLOC_FAILED`：内存无法分配。
- `ACBLAS_STATUS_SUCCESS`：操作成功。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 5.3.16. acblasLtMatrixTransformDescDestroy() {#5316-acblasltmatrixtransformdescdestroy}

```cpp
acblasStatus_t
acblasLtMatrixTransformDescDestroy(
                                    acblasLtMatrixTransformDesc_t transformDesc);
```

销毁先前创建的矩阵变换描述符。

**参数：**
| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `transformDesc` |            | 输入              | 指向保存待销毁的矩阵变换描述符的结构体的指针。参见 `acblasLtMatrixTransformDesc_t`。 |

**返回：**
返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 5.3.17. acblasLtMatrixTransformDescGetAttribute() {#5317-acblasltmatrixtransformdescgetattribute}

```cpp
acblasStatus_t
acblasLtMatrixTransformDescGetAttribute(
                                        acblasLtMatrixTransformDesc_t transformDesc,
                                        acblasLtMatrixTransformDescAttributes_t attr,
                                        void *buf,
                                        size_t sizeInBytes,
                                        size_t *sizeWritten);
```

查询矩阵变换描述符的属性值。

**参数：**
| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `transformDesc` |            | 输入              | 指向保存待查询的矩阵变换描述符的结构体的指针。参见 `acblasLtMatrixTransformDesc_t`。 |
| `attr`          |            | 输入              | 待检索的属性。参见 `acblasLtMatrixTransformDescAttributes_t`。 |
| `buf`           |            | 输出             | 包含检索到的属性值的内存地址。 |
| `sizeInBytes`   |            | 输入              | 用于验证的 `buf` 缓冲区大小（以字节为单位）。            |
| `sizeWritten`   |            | 输出             | 仅当返回值为 ACBLAS_STATUS_SUCCESS 时有效。若 `sizeInBytes` 非零：则 `sizeWritten` 是实际写入的字节数；若 `sizeInBytes` 为 0：则 `sizeWritten` 是写入完整内容所需的字节数。 |

**返回：**

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_INVALID_VALUE`：参数无效。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 5.3.18. acblasLtMatrixTransformDescSetAttribute() {#5318-acblasltmatrixtransformdescsetattribute}

```cpp
acblasStatus_t
acblasLtMatrixTransformDescSetAttribute(
                                        acblasLtMatrixTransformDesc_t transformDesc,
                                        acblasLtMatrixTransformDescAttributes_t attr,
                                        const void *buf,
                                        size_t sizeInBytes);
```

为矩阵变换描述符设置指定属性值。

**参数：**
| 参数 | 内存 | 输入/输出 | 说明 |
| :--- | :--- | :--- | :--- |
| `transformDesc` |            | 输入              | 指向保存待设置的矩阵变换描述符的结构体的指针。参见 `acblasLtMatrixTransformDesc_t`。 |
| `attr`          |            | 输入              | 待设置的属性。参见 `acblasLtMatrixTransformDescAttributes_t`。 |
| `buf`           |            | 输入              | 指定属性应设置的值。    |
| `sizeInBytes`   |            | 输入              | 用于验证的 `buf` 缓冲区大小（以字节为单位）。            |

**返回：**

返回码：

- `ACBLAS_STATUS_SUCCESS`：属性设置成功。
- `ACBLAS_STATUS_INVALID_VALUE`：`buf` 为 NULL 或 `sizeInBytes` 与所选属性的内部存储大小不匹配。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

比赛关联：`acblasLtMatmul()` 是 GEMM 精细调优的主入口——epilogue 融合（BIAS/GELU，对应 LLM 的 MLP 层）、INT8 IMMA 与 FP8 kernel 的完整精度组合表、tile/stage 选择都集中在本章；描述符可复用的 plan 模式意味着同一形状的 GEMM 只需配置一次，直接利好 TTFT 与 decode 吞吐。注意 IMMA 要求 TN/NT 特定转置组合、4 字节对齐与 ld 为 4 的倍数，FP8 要求 TN 格式 + 16 字节对齐。

## 6. 类型与枚举 {#6-类型与枚举}

本章集中列出 acBLAS 使用的所有数据类型、枚举和辅助函数。

### 6.1. 状态码 acblasStatus_t {#61-状态码-acblasstatus_t}

所有 acBLAS 例程统一通过 `acblasStatus_t` 返回执行状态。常见取值与排查建议汇总如下：

| 状态码 | 含义 | 常见原因 / 排查方向 |
| :--- | :--- | :--- |
| `ACBLAS_STATUS_SUCCESS` | 调用成功 | — |
| `ACBLAS_STATUS_NOT_INITIALIZED` | 库未初始化 | 先调用 `acblasCreate()`；同时确认硬件、驱动版本、acBLAS 库已正确安装 |
| `ACBLAS_STATUS_ALLOC_FAILED` | 内部资源分配失败 | 由 `hggcMalloc()` 失败引发；调用前尽量释放无用内存 |
| `ACBLAS_STATUS_INVALID_VALUE` | 参数非法 | 如向量长度为负；检查所有入参取值是否合法 |
| `ACBLAS_STATUS_ARCH_MISMATCH` | 所需特性当前架构不支持 | 通常出现在低版本架构的设备上；在合适设备上编译运行 |
| `ACBLAS_STATUS_MAPPING_ERROR` |真武 PPU 内存空间访问失败 | 一般由纹理绑定失败引起；调用前先解绑遗留纹理 |
| `ACBLAS_STATUS_EXECUTION_FAILED` |真武 PPU kernel 执行失败 | 原因多样；检查硬件 / 驱动 / 库的版本与安装 |
| `ACBLAS_STATUS_INTERNAL_ERROR` | 内部操作失败 | 多由 `hggcMemcpyAsync()` 失败导致；同时核查入参指向的内存是否在调用过程中被提前释放 |
| `ACBLAS_STATUS_NOT_SUPPORTED` | 所请求的功能不支持 | — |
| `ACBLAS_STATUS_LICENSE_ERROR` | 许可证检查失败 | 许可证缺失/过期，或相关环境变量未配置 |

### 6.2. acblasHandle_t {#62-acblashandle_t}

不透明指针，指向 acBLAS 库的上下文结构。

| 操作 | 接口 |
| :--- | :--- |
| 创建 | `acblasCreate()` |
| 使用 | 作为第一个参数显式传给所有 acBLAS 例程 |
| 销毁 | `acblasDestroy()` |

### 6.3. 运算与填充枚举 {#63-运算与填充枚举}

#### 6.3.1. acblasOperation_t {#631-acblasoperation_t}

指明对稠密矩阵执行的变换形式，对应传统 BLAS 字符参数 `'N'` / `'T'` / `'C'`。

| 枚举值 | 字符 | 含义 |
| :--- | :--- | :--- |
| `ACBLAS_OP_N` | `'N'` / `'n'` | 非转置 |
| `ACBLAS_OP_T` | `'T'` / `'t'` | 转置 |
| `ACBLAS_OP_C` | `'C'` / `'c'` | 共轭转置 |

#### 6.3.2. acblasFillMode_t {#632-acblasfillmode_t}

声明稠密矩阵中**有效数据** 所在的三角区域，对应字符 `'L'` / `'U'`。

| 枚举值 | 字符 | 含义 |
| :--- | :--- | :--- |
| `ACBLAS_FILL_MODE_LOWER` | `'L'` / `'l'` | 仅下三角有效 |
| `ACBLAS_FILL_MODE_UPPER` | `'U'` / `'u'` | 仅上三角有效 |
| `ACBLAS_FILL_MODE_FULL`  | — | 整矩阵均有效 |

#### 6.3.3. acblasDiagType_t {#633-acblasdiagtype_t}

声明矩阵主对角线是否被视为「单位元素」。值为 unit 时函数不会读取或写入对角线，对应字符 `'N'` / `'U'`。

| 枚举值 | 字符 | 含义 |
| :--- | :--- | :--- |
| `ACBLAS_DIAG_NON_UNIT` | `'N'` / `'n'` | 对角线元素为普通值 |
| `ACBLAS_DIAG_UNIT`     | `'U'` / `'u'` | 对角线元素视为 1，且不被触及 |

#### 6.3.4. acblasSideMode_t {#634-acblassidemode_t}

用于矩阵方程求解类例程（如 `trsm`），声明三角/稠密矩阵位于方程哪一侧，对应字符 `'L'` / `'R'`。

| 枚举值 | 字符 | 含义 |
| :--- | :--- | :--- |
| `ACBLAS_SIDE_LEFT`  | `'L'` / `'l'` | 矩阵位于方程左侧 |
| `ACBLAS_SIDE_RIGHT` | `'R'` / `'r'` | 矩阵位于方程右侧 |

#### 6.3.5. acblasPointerMode_t {#635-acblaspointermode_t}

控制标量值（`alpha` / `beta`、标量返回结果）的**指针寄存位置** 。同一函数调用内的所有标量必须遵循相同的模式。可通过 `acblasSetPointerMode()` / `acblasGetPointerMode()` 设置与查询。

| 枚举值 | 标量驻留位置 |
| :--- | :--- |
| `ACBLAS_POINTER_MODE_HOST`   | 主机内存 |
| `ACBLAS_POINTER_MODE_DEVICE` | 设备内存 |

详细的使用约束 [参见 2.3](#23-标量参数与指针模式) 标量参数。

#### 6.3.6. acblasGemmAlgo_t {#636-acblasgemmalgo_t}

GEMM 算法选择枚举。

!!! warning
    仅在低版本真武 PPU 架构上生效；高版本架构会忽略该枚举值。

| 枚举值 | 含义 |
| :--- | :--- |
| `ACBLAS_GEMM_DEFAULT` | 由库内部启发式自动选择算法 |
| `ACBLAS_GEMM_ALGO0` ~ `ACBLAS_GEMM_ALGO23` | 显式选用编号为 0–23 的算法 |
| `ACBLAS_GEMM_DEFAULT_TENSOR_OP` | 启发式选择 + 允许使用 `ACBLAS_COMPUTE_32F_FAST_16F` 降精度 kernel（向后兼容用途） |

#### 6.3.7. acblasMath_t {#637-acblasmath_t}

`acblasSetMathMode()` 接受的精度模式枚举，**不直接控制** Tensor Cell 是否启用。

| 枚举值 | 含义 |
| :--- | :--- |
| `ACBLAS_DEFAULT_MATH`       | 默认、最高性能。计算与中间存储精度至少不低于用户请求；尽可能使用 Tensor Cell |
| `ACBLAS_TF32_TENSOR_OP_MATH`| 在单精度路径上启用 TF32 Tensor Cell 加速 |
| `ACBLAS_TENSOR_OP_MATH`     | 允许使用 Tensor Cell；单精度 GEMM 退化为 `ACBLAS_COMPUTE_32F_FAST_16F` |
| `ACBLAS_MATH_DISALLOW_REDUCED_PRECISION_REDUCTION` | 禁止在归约运算中使用降低精度的累加（可与上述枚举位或组合使用） |

#### 6.3.8. acblasComputeType_t {#638-acblascomputetype_t}

`acblasGemmEx()` / `acblasLtMatmul()`（含所有 batched、strided-batched 变体）使用的计算精度枚举。

**浮点路径**

| 枚举值 | 计算精度 | 是否启用 Tensor Cell / 说明 |
| :--- | :--- | :--- |
| `ACBLAS_COMPUTE_16F`            | 16-bit 半精度 | 默认；尽可能用 Tensor Cell |
| `ACBLAS_COMPUTE_16F_PEDANTIC`   | 16-bit 半精度（标准算术） | **禁用** Tensor Cell；用于数值鲁棒性研究、测试、调试 |
| `ACBLAS_COMPUTE_32F`            | 至少 32-bit 单精度 | 默认 |
| `ACBLAS_COMPUTE_32F_PEDANTIC`   | 32-bit 单精度（标准算术） | 禁用高斯复杂度归约 (3M) 等算法优化 |
| `ACBLAS_COMPUTE_32F_FAST_16F`   | 32-bit 输入 / 16-bit 计算 | Tensor Cell，自动降精度转换 |
| `ACBLAS_COMPUTE_32F_FAST_16BF`  | 32-bit 输入 / bfloat16 计算 | Tensor Cell，自动降精度转换 |
| `ACBLAS_COMPUTE_32F_FAST_TF32`  | 32-bit 输入 / TF32 计算 | Tensor Cell |
| `ACBLAS_COMPUTE_64F`            | 至少 64-bit 双精度 | 默认 |
| `ACBLAS_COMPUTE_64F_PEDANTIC`   | 64-bit 双精度（标准算术） | 禁用 3M 等算法优化 |

**整数路径**

| 枚举值 | 计算精度 | 说明 |
| :--- | :--- | :--- |
| `ACBLAS_COMPUTE_32I`          | 至少 32-bit 整数 | 默认 |
| `ACBLAS_COMPUTE_32I_PEDANTIC` | 32-bit 整数（标准算术） | — |

### 6.4. HGGC 数据类型 {#64-hggc-数据类型}

本节列出由多个 HGGC 库共享、定义在头文件 `library_types.h` 中的通用数据类型。

#### 6.4.1. hggcDataType_t {#641-hggcdatatype_t}

`hggcDataType_t` 在数据引用本身不带类型信息时（最典型的就是 `void *`）用来显式指明元素精度，例如 `acblasSgemmEx()` 的参数中就会用到。枚举值按精度组织如下：

**浮点类型（IEEE 754 与变体）**

| 精度 / 格式 | 枚举值 |
| :--- | :--- |
| 16-bit half | `HGGC_R_16F`   |
| 16-bit bfloat16 | `HGGC_R_16BF`  |
| 32-bit single | `HGGC_R_32F`   |
| 64-bit double | `HGGC_R_64F`   |

**FP8（8-bit 浮点，仅实数）**

| 枚举值 | 格式 |
| :--- | :--- |
| `HGGC_R_8F_E4M3` | E4M3 |
| `HGGC_R_8F_E5M2` | E5M2 |

**整数类型**

| 位宽 / 符号 | 枚举值 |
| :--- | :--- |
| 8-bit signed   | `HGGC_R_8I`   |
| 8-bit unsigned | `HGGC_R_8U`   |
| 32-bit signed  | `HGGC_R_32I`  |

#### 6.4.2. hggcLibraryPropertyType {#642-hggclibrarypropertytype}

`acblasGetProperty()` 用此枚举指定要查询的属性。

| 枚举值 | 含义 |
| :--- | :--- |
| `HGGC_MAJOR_VERSION` | 主版本号 |
| `HGGC_MINOR_VERSION` | 次版本号 |
| `HGGC_PATCH_LEVEL`   | 补丁级别 |

### 6.5. 辅助函数 {#65-辅助函数}

按用途，本节函数可大致分为四类：句柄生命周期、库信息查询、运行时配置（stream / 工作空间 / 指针模式 / 数学模式）以及主机—设备的数据搬运。

#### 6.5.1. acblasCreate() {#651-acblascreate}

```cpp
acblasStatus_t
acblasCreate(acblasHandle_t *handle)
```

初始化 acBLAS 库，并把承载上下文的不透明句柄通过 `*handle` 返回给调用方。它会在主机端和设备端各自分配硬件资源，**必须先于其他任何 acBLAS 例程调用** 。

要点速览：

- **设备绑定** ：句柄绑定调用时刻的当前 HGGC 设备；多设备应用应在每次 `hggcSetDevice()` 之后再 create。
- **同设备多句柄** ：同一设备允许并存多个配置不同的句柄。
- **配对销毁的代价** ：与之配对的 `acblasDestroy()` 在释放资源时会隐式触发 `hggcDeviceSynchronize()`，因此尽量减少 create/destroy 次数。
- **多线程范式** ：每个线程持有一个独立句柄并贯穿其生命周期，是最简洁的并发模型。

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：HGGC Runtime 初始化失败。
- `ACBLAS_STATUS_ALLOC_FAILED`：资源分配失败。
- `ACBLAS_STATUS_INVALID_VALUE`：`handle` 为 NULL。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 6.5.2. acblasDestroy() {#652-acblasdestroy}

```cpp
acblasStatus_t
acblasDestroy(acblasHandle_t handle)
```

释放与某个 acBLAS 句柄关联的全部硬件资源。一般是该句柄上的最后一次调用。函数返回前会隐式 `hggcDeviceSynchronize()`，详见 `acblasCreate()` 中关于 create/destroy 频次的说明。

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 6.5.3. acblasGetVersion() {#653-acblasgetversion}

```cpp
acblasStatus_t
acblasGetVersion(int *version)
```

读取当前 acBLAS 库版本号写入 `*version`。允许传入 NULL 句柄。这一特性使得调用方在尚未初始化任何上下文时也能获取版本信息。同样的版本信息亦可经 `acblasGetProperty()` 获取。

#### 6.5.4. acblasGetProperty() {#654-acblasgetproperty}

```cpp
acblasStatus_t
acblasGetProperty(hggcLibraryPropertyType type, int *value)
```

按 `type`（取值见 `hggcLibraryPropertyType`）查询库属性，结果写入 `*value`。

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_INVALID_VALUE`：`type` 非法或 `value` 为 NULL。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 6.5.5. acblasGetStatusString() {#655-acblasgetstatusstring}

```cpp
const char *
acblasGetStatusString(acblasStatus_t status)
```

把状态码翻译成可读字符串，返回值是 NUL 结尾的常量字符串，便于直接 `printf` / 日志拼接。

#### 6.5.6. acblasSetStream() {#656-acblassetstream}

```cpp
acblasStatus_t
acblasSetStream(acblasHandle_t handle, hggcStream_t streamId)
```

把句柄后续要使用的 HGGC stream 切换为 `streamId`；不设置时一律使用默认 NULL stream。常见用法是为不同 kernel 切换 stream，或在某段计算之后把 stream 重置回 NULL。

!!! warning
    **副作用** ：本调用会无条件地把库工作空间重置回内置的默认池。若此前曾通过 `acblasSetWorkspace()` 提供过自有工作空间，需要在切完 Stream 之后重新设置。

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 6.5.7. acblasSetWorkspace() {#657-acblassetworkspace}

```cpp
acblasStatus_t
acblasSetWorkspace(acblasHandle_t handle,
                   void *workspace,
                   size_t workspaceSizeInBytes)
```

把库使用的工作空间替换为调用方提供的设备端缓冲区。设置生效后，**当前 Stream 上** 之后发起的 acBLAS 调用都会使用它；未设置时则使用 create 阶段分配的默认池。

约束与建议：

| 项 | 要求 |
| :--- | :--- |
| 指针对齐 | 至少 256 字节，否则返回 `ACBLAS_STATUS_INVALID_VALUE` |
| 容量下限 | 不足以承载某次 kernel 时返回 `ACBLAS_STATUS_ALLOC_FAILED`，或带来明显性能下降 |
| 推荐容量 | ≥ 16 KiB 即可避免 `ACBLAS_STATUS_ALLOC_FAILED`；某些 GEMM 在更大工作空间下能选出更优算法 |
| 是否覆盖默认池 | 调用本函数（即便 `workspaceSizeInBytes == 0`）即视为「禁用默认工作空间」 |
| 与 stream 的关系 | `acblasSetStream()` 会无条件清掉这次设置 |

> 当 stream 为 `hggcStreamPerThread` 且多线程共用同一句柄时，自有工作空间容易引入竞争。这种场景下要么让上层做好同步，要么直接回退到默认池（默认池本身保证线程安全）。

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_INVALID_VALUE`：指针未满足 256 字节对齐。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 6.5.8. acblasGetStream() {#658-acblasgetstream}

```cpp
acblasStatus_t
acblasGetStream(acblasHandle_t handle, hggcStream_t *streamId)
```

读出当前句柄正在使用的 stream（未设置时返回 NULL stream）。

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_INVALID_VALUE`：`streamId` 为 NULL。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 6.5.9. acblasGetPointerMode() {#659-acblasgetpointermode}

```cpp
acblasStatus_t
acblasGetPointerMode(acblasHandle_t handle, acblasPointerMode_t *mode)
```

读取当前句柄所采用的指针模式（取值含义见 `acblasPointerMode_t`）。

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_INVALID_VALUE`：`mode` 为 NULL。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 6.5.10. acblasSetPointerMode() {#6510-acblassetpointermode}

```cpp
acblasStatus_t
acblasSetPointerMode(acblasHandle_t handle, acblasPointerMode_t mode)
```

切换标量参数（`alpha` / `beta` 等）所在的内存空间。不设置时默认行为是「主机引用传递」。`mode` 必须是 `ACBLAS_POINTER_MODE_HOST` 或 `ACBLAS_POINTER_MODE_DEVICE` 之一，含义见 `acblasPointerMode_t`。

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。
- `ACBLAS_STATUS_INVALID_VALUE`：`mode` 既非 HOST 也非 DEVICE。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 6.5.11. acblasSetVector() {#6511-acblassetvector}

```cpp
acblasStatus_t
acblasSetVector(int n, int elemSize,
                const void *x, int incx,
                void *y, int incy)
```

把主机内存中向量 `x` 的 `n` 个元素拷贝到真武 PPU 端向量 `y`。元素大小由 `elemSize`（字节）描述；源/目的步幅分别由 `incx`、`incy` 指定。

由于库内一律以**列优先** 视角处理矩阵，若向量是某矩阵的一段，则：

| 步幅取值 | 等价语义 |
| :--- | :--- |
| `inc = 1` | 访问矩阵的（部分）列 |
| `inc = ld`（前导维度） | 访问矩阵的（部分）行 |

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_INVALID_VALUE`：`incx`、`incy` 或 `elemSize` ≤ 0。
- `ACBLAS_STATUS_MAPPING_ERROR`：访问真武 PPU 内存时出错。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 6.5.12. acblasGetVector() {#6512-acblasgetvector}

```cpp
acblasStatus_t
acblasGetVector(int n, int elemSize,
                const void *x, int incx,
                void *y, int incy)
```

`acblasSetVector()` 的反向操作：把真武 PPU 内存中向量 `x` 的 `n` 个元素回拷到主机端向量 `y`。`incx` / `incy` / `elemSize` 的语义、步幅与列/行视图的对应关系同上。

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_INVALID_VALUE`：`incx`、`incy` 或 `elemSize` ≤ 0。
- `ACBLAS_STATUS_MAPPING_ERROR`：访问真武 PPU 内存时出错。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 6.5.13. acblasSetMatrix() {#6513-acblassetmatrix}

```cpp
acblasStatus_t
acblasSetMatrix(int rows, int cols, int elemSize,
                const void *A, int lda,
                void *B, int ldb)
```

主机 → 设备的矩阵块拷贝：把主机端矩阵 `A` 中 `rows × cols` 大小的子块写到真武 PPU 端矩阵 `B`。两矩阵均按**列优先** 存储，每元素 `elemSize` 字节，前导维度分别为 `lda`、`ldb`，即便实际只用子矩阵，前导维度仍取「整体分配的行数」。

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_INVALID_VALUE`：`rows < 0`、`cols < 0`，或 `elemSize`、`lda`、`ldb` ≤ 0。
- `ACBLAS_STATUS_MAPPING_ERROR`：访问真武 PPU 内存时出错。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 6.5.14. acblasGetMatrix() {#6514-acblasgetmatrix}

```cpp
acblasStatus_t
acblasGetMatrix(int rows, int cols, int elemSize,
                const void *A, int lda,
                void *B, int ldb)
```

`acblasSetMatrix()` 的反向操作：把真武 PPU 端矩阵 `A` 的 `rows × cols` 子块拷回主机端矩阵 `B`。元素布局、`lda`/`ldb` 含义同上。

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_INVALID_VALUE`：`rows < 0`、`cols < 0`，或 `elemSize`、`lda`、`ldb` ≤ 0。
- `ACBLAS_STATUS_MAPPING_ERROR`：访问真武 PPU 内存时出错。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 6.5.15. acblasSetMathMode() {#6515-acblassetmathmode}

```cpp
acblasStatus_t
acblasSetMathMode(acblasHandle_t handle, acblasMath_t mode)
```

设置精度模式（取值见 `acblasMath_t`）。`mode` 支持位或组合，如：

```cpp
acblasSetMathMode(handle,
    ACBLAS_DEFAULT_MATH | ACBLAS_MATH_DISALLOW_REDUCED_PRECISION_REDUCTION);
```

不设置时使用 `ACBLAS_DEFAULT_MATH`。矩阵/计算精度组合详见 [acblasGemmEx()](#432-acblasgemmex)、[acblasGemmBatchedEx()](#433-acblasgemmbatchedex)、[acblasGemmStridedBatchedEx()](#434-acblasgemmstridedbatchedex)、[acblasLtMatmul()](#533-acblasltmatmul) 各函数小节。

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_INVALID_VALUE`：`mode` 不在合法集合内。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

#### 6.5.16. acblasGetMathMode() {#6516-acblasgetmathmode}

```cpp
acblasStatus_t
acblasGetMathMode(acblasHandle_t handle, acblasMath_t *mode)
```

读出当前句柄正在使用的数学模式。

返回码：

- `ACBLAS_STATUS_SUCCESS`：操作成功。
- `ACBLAS_STATUS_INVALID_VALUE`：`mode` 为 NULL。
- `ACBLAS_STATUS_NOT_INITIALIZED`：未初始化。

详见 [`acblasStatus_t`](#61-状态码-acblasstatus_t)。

