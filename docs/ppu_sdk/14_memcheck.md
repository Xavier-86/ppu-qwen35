# HGGC Memcheck 显存错误检查工具 <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [1. 概述](#1-概述)
- [2. 使用介绍](#2-使用介绍)
  - [2.1. 命令行参数](#21-命令行参数)
- [3. Memcheck 工具](#3-memcheck-工具)
  - [3.1. 支持的错误种类](#31-支持的错误种类)
  - [3.2. Memcheck 使用](#32-memcheck-使用)
  - [3.3. Memcheck 报错格式说明](#33-memcheck-报错格式说明)
  - [3.4. HGGC API 错误检查](#34-hggc-api-错误检查)
  - [3.5. Padding（Redzone）](#35-paddingredzone)
- [4. Racecheck 工具](#4-racecheck-工具)
  - [4.1. 数据冒险种类](#41-数据冒险种类)
  - [4.2. Racecheck 使用](#42-racecheck-使用)
  - [4.3. Racecheck 报错示例](#43-racecheck-报错示例)
- [5. Initcheck 工具](#5-initcheck-工具)
  - [5.1. Initcheck 使用](#51-initcheck-使用)
- [6. Synccheck 工具](#6-synccheck-工具)
  - [6.1. Synccheck 使用](#61-synccheck-使用)
- [7. 使用示例](#7-使用示例)
  - [7.1. Memcheck 使用示例](#71-memcheck-使用示例)
  - [7.2. Racecheck 使用示例](#72-racecheck-使用示例)
  - [7.3. Initcheck 使用示例](#73-initcheck-使用示例)
  - [7.4. Synccheck 使用示例](#74-synccheck-使用示例)
  - [7.5. coredump 使用示例](#75-coredump-使用示例)
- [8. 已知问题](#8-已知问题)
- [9. 常见问题](#9-常见问题)


## 1. 概述

T-Head SAIL HGGC Memcheck 是一套运行时功能正确性检查工具，用于对 HGGC 应用程序进行多种类型的正确性检测。

HGGC Memcheck 工具套件包含以下四个子工具：

| 子工具      | 功能                                                                    |
| ----------- | ----------------------------------------------------------------------- |
| `memcheck`  | 检测 global、local、shared 内存的越界访问与非对齐访问，以及设备内存泄漏 |
| `racecheck` | 检测 shared memory 上不同 warp 间的数据冒险（data hazards）             |
| `initcheck` | 检测对未初始化 global memory 的读取操作                                 |
| `synccheck` | 检测 `__syncwarp()` 的不正确使用                                        |

**快速上手**：编译用户程序后，使用如下命令即可进行基础的访存越界检查：

```bash
hggc-memcheck ./your_app
```

如需切换检查工具，使用 `--tool` 选项指定（详见第 2.1 节）。

## 2. 使用介绍

### 2.1. 命令行参数

下表列出 `hggc-memcheck` 支持的所有命令行参数及其说明。

*表 1：hggc-memcheck 命令行参数*

| 选项                        | 取值                                      | 默认值    | 说明                                                                                                                                                                                                          |
| :-------------------------- | :---------------------------------------- | :-------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| coredump-name               |                                           |           | 指定 core dump 文件的名称                                                                                                                                                                                     |
| demangle                    | full, simple, no                          | full      | 控制报告中函数名的解码方式。`full`：解码为包含参数列表的完整函数签名；`simple`：仅解码 kernel 入口函数名；`no`：保留编译器生成的修饰名称（mangled name）。                                                      |
| -e, destroy-on-device-error | context, kernel                           | context   | 控制检测到设备错误后的处理策略。`context`：HGGC 上下文以错误终止；`kernel`：仅终止发生错误的 kernel，后续 kernel 仍可继续启动。                                                                                 |
| filter                      | -                                         | -         | 设置 kernel 过滤条件，仅对匹配的 kernel 执行检查。支持多个 `filter` 选项叠加使用（匹配任一条件即生效）。过滤条件以键值对形式指定，键之间用 `,` 分隔。可用键：`kernel_name`（简写 `kne`）指定 kernel 的完整 mangled 名称；`kernel_substring`（简写 `kns`）指定 kernel mangled 名称中的子串。`kernel_name` 与 `kernel_substring` 不可同时使用。 |
| force-blocking-launches     | yes, no                                   | no        | 强制所有 kernel launch 采用阻塞方式执行。启用后每次 launch 都会等待 kernel 完成，可有效减少工具运行时的设备内存占用（详见第 9 节），但会增加同步开销。                                                           |
| force-synchronization-limit | { number }                                | 0         | 在同一 stream 上，累计指定次数的 launch 后自动插入一次同步。用于限制工具对设备内存的峰值占用，代价是额外的同步开销。`0` 表示不限制。                                                                              |
| generate-coredump           | yes, no                                   | no        | 设为 `yes` 时，在检测到首个错误后生成 coredump 文件并停止程序执行。coredump 文件保存在运行 `hggc-memcheck` 的当前目录下（详见第 7.5 节）。                                                                        |
| -h, help                    |                                           |           | 显示帮助信息。                                                                                                                                                                                                  |
| -c, launch-count            | { number }                                | 0         | 限制要检查的 kernel 启动总次数。仅统计匹配 `filter` 条件的启动。`0` 表示不限制。                                                                                                                                |
| -s, launch-skip             | { number }                                | 0         | 跳过前 N 次匹配 `filter` 条件的 kernel 启动，从第 N+1 次开始执行检查。                                                                                                                                          |
| log-file                    | -                                         | -         | 将 `hggc-memcheck` 的所有文本输出重定向至指定文件。未指定时输出到标准输出（`stdout`）。                                                                                                                         |
| prefix                      | { string }                                | ========= | 自定义 `hggc-memcheck` 输出信息的行前缀字符串。                                                                                                                                                                 |
| print-limit                 | { number }                                | 10000     | 设置错误输出的数量上限。达到该值后不再输出新的错误信息。设为 `0` 表示不限制输出数量。                                                                                                                           |
| report-api-errors           | all, explicit, no                         | explicit  | 控制 HGGC API 调用失败时的报告行为。`all`：报告所有 API 错误，包括运行时隐式调用的内部 API；`explicit`：仅报告开发者代码中显式调用的 API 错误；`no`：关闭 API 错误报告。                                         |
| show-backtrace              | yes, no                                   | yes       | 控制错误信息中是否包含主机端调用栈回溯。`no`：不显示回溯；`yes`：在每条错误信息后附加主机端调用栈。                                                                                                             |
| tool                        | memcheck, initcheck, synccheck, racecheck | memcheck  | 选择要使用的检查工具。                                                                                                                                                                                          |
| -v, version                 |                                           |           | 显示版本信息。                                                                                                                                                                                                  |
| [memcheck 专用选项]         |                                           |           |                                                                                                                                                                                                               |
| leak-check                  | full, no                                  | no        | 启用设备内存泄漏检测。设为 `full` 时，在 HGGC context 销毁阶段扫描所有通过 `hggcMalloc` 接口分配但未释放的内存块，并报告泄漏详情（地址、大小及分配时的调用栈）。                                                  |
| padding                     | { number }                                | 0         | 设置每次 `hggcMalloc` 分配时在内存块前后添加的 redzone 大小（单位：字节），实际大小会向上对齐到 4 的倍数。更大的 redzone 可检测到跨度更大的越界访问，但会增加设备内存消耗。从主机端对 redzone 区域执行 `memcpy` 不会触发报错。 |
| track-stream-ordered-races  | all, use-before-alloc, use-after-free, no | no        | 跟踪并报告 stream-ordered（异步）内存分配相关的竞争访问。`all`：跟踪并报告全部；`use-before-alloc`：仅报告分配完成前的使用；`use-after-free`：仅报告释放后的使用；`no`：关闭检测。                                 |
| [racecheck 专用选项]        |                                           |           |                                                                                                                                                                                                               |
| racecheck-detect-level      | warn, error                               | warn      | 设置要检测的数据冒险的最低级别。                                                                                                                                                                                |
| [initcheck 专用选项]        |                                           |           |                                                                                                                                                                                                               |
| track-unused-memory         | yes, no                                   | no        | 检查已分配但从未被任何 kernel 访问的内存块。                                                                                                                                                                    |
| check-uninit-shared         | yes, no                                   | no        | 检测对未初始化 shared memory 的读取使用。                                                                                                                                                                       |
| unused-memory-threshold     | { number }                                | 0         | 未使用内存的报告阈值（百分比）。若某块内存的未使用比例低于该阈值，则不会被报告。例如设为 50 时，仅报告未使用比例 ≥ 50% 的内存分配。                                                                               |

## 3. Memcheck 工具

`memcheck` 工具用于在 HGGC 应用运行时检测 device 端的内存访问错误。它能够精确定位 global、local、shared 三种地址空间中的越界访问和非对齐访问，同时支持检测通过 `hggcMalloc` 分配的设备内存是否存在泄漏。

### 3.1. 支持的错误种类

`memcheck` 工具能够检测以下三类错误：

*表 2：Memcheck 检测的错误类型*

| 错误类型          | 说明                                                | 检测位置与精度    | 典型触发场景                                     |
| :---------------- | :-------------------------------------------------- | :---------------- | :----------------------------------------------- |
| 访存越界 / 非对齐 | global、local、shared 内存的越界或非对齐访问        | Device 端精确检测 | 数组索引超出分配范围；结构体成员未按对齐要求访问 |
| HGGC API 调用失败 | HGGC 运行时 API 返回错误码                          | Host 端精确检测   | 传入非法参数、设备资源不足等                     |
| 设备内存泄漏      | 通过 `hggcMalloc` 分配的内存在 context 销毁前未释放 | Host 端精确检测   | 程序退出前未调用 `hggcFree` 释放对应内存         |

### 3.2. Memcheck 使用

`memcheck` 是 `hggc-memcheck` 的默认检查工具，也可通过 `--tool` 选项显式指定：

```bash
hggc-memcheck --tool memcheck [memcheck options] user_app [user_app options]
```

### 3.3. Memcheck 报错格式说明

`hggc-memcheck` 的错误输出由行前缀（可通过 `--prefix` 自定义）引导，每条错误包含多个信息字段。以下使用 `--prefix "[HGGC-MC]"` 展示各类错误的输出格式。

#### 3.3.1. 访存错误（Memory access error）

访存错误的报告包含四个关键信息段：

```text
[HGGC-MC] Invalid __global__ write of size 4          ← ① 地址空间 + 操作类型 + 数据宽度
[HGGC-MC]     at: 0x00800120 in compute(float*)        ← ② 指令地址与所在函数
[HGGC-MC]     by thread (128,0,0) in block (0,0,0)     ← ③ 触发线程与线程块编号
[HGGC-MC]     Address 0x60a80200 is out of bounds       ← ④ 访问地址与错误类别
```

各信息段说明：

- **① 错误概要**：标明访问的地址空间（`__global__`、`__shared__`、`__private__`）、操作类型（`read`、`write`、`atomic`）以及访问的数据宽度（字节数）。
- **② 出错位置**：显示设备端指令的 PC 值和所在函数名。若编译时保留了行号信息（`-gline-tables-only`），还会显示对应的源文件名和行号。
- **③ 线程坐标**：造成错误的线程和线程块的三维编号。
- **④ 错误详情**：实际访问的地址以及错误类别——`out of bounds`（越界）或 `misaligned`（非对齐）。

#### 3.3.2. 内存泄漏（Leak error）

```text
[HGGC-MC] Leaked 256 bytes at 0x60c40000
```

当通过 `hggcMalloc` 分配的内存在所属 HGGC context 销毁时仍未释放，`memcheck` 将报告泄漏的内存首地址和分配大小。需要启用 `--leak-check full` 选项。

#### 3.3.3. API 调用错误（HGGC API error）

```text
[HGGC-MC] Program hit hggcErrorInvalidValue (error 1) due to "invalid argument" on HGGC API call to hggcLaunchKernel.
```

当 HGGC API 返回失败时，报告中包含 API 名称、错误码及错误原因描述。

### 3.4. HGGC API 错误检查

`hggc-memcheck` 会监控用户程序对 HGGC API 的调用结果。当 API 返回失败时，`hggc-memcheck` 输出对应的错误信息，但不会终止用户进程，也不会执行额外的干预操作。

以下返回值属于正常的运行时状态，不会被报告为错误：

| 被排除的返回值                      | 涉及 API                            | 排除理由                                         |
| :---------------------------------- | :---------------------------------- | :----------------------------------------------- |
| `hggcErrorNotReady`                 | `hggcEventQuery`、`hggcStreamQuery` | 正常的异步查询结果，表示操作尚未完成，非错误状态 |
| `hggcErrorPeerAccessAlreadyEnabled` | `hggcDeviceEnablePeerAccess`        | 重复启用属于幂等操作，不影响程序正确性           |
| `hggcErrorPeerAccessNotEnabled`     | `hggcDeviceDisablePeerAccess`       | 对未启用的对等访问执行禁用操作属于空操作         |

### 3.5. Padding（Redzone）

`hggc-memcheck` 可以在通过 `hggcMalloc` 分配的内存块前后添加 padding 区域（即 redzone）。若未启用 padding，当越界访问恰好落入相邻的合法内存区域时，工具将无法检测到该错误。

通过 `--padding` 选项可指定 padding 的大小（单位：字节），实际大小会自动向上对齐到 4 的整数倍。分配内存时，会在内存块的起始端和末尾端各添加指定大小的 redzone。更大的 padding 能够捕获跨度更大的越界访问，但会增加设备内存的消耗。

![memcheck redzone illustration](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125164982/c73c3559f894408a30e4c1490d15b8e2/memcheck_redzone.png)

比赛关联：为比赛编写自定义量化 kernel（如 INT4/INT8 解量化、融合 GEMM、KV cache 管理）时，越界与非对齐错误是最常见的崩溃与精度异常根源；`memcheck` 能精确到指令 PC 和线程坐标定位问题，`--padding` 则可揪出落在相邻合法区域里的"隐性"越界。

## 4. Racecheck 工具

`racecheck` 工具用于在 HGGC 程序运行时检测 shared memory 上的数据冒险。当同一 block 内的多个线程对同一块 shared memory 进行读写，且缺乏正确的同步机制时，程序的执行结果可能依赖于不确定的线程调度顺序，从而产生数据冒险。

> 注：目前，`racecheck` 仅对来自不同 warp 中线程之间的数据冒险进行检测。同一 warp 内的线程不在检测范围内。

### 4.1. 数据冒险种类

**数据冒险**（Data Hazard）是指同一 block 内不同 warp 的线程在缺乏显式同步的情况下，对同一 shared memory 地址执行了顺序相关的操作，导致最终结果依赖于不确定的执行顺序。`racecheck` 检测以下三类冒险：

- **先写后读冒险**（Read-After-Write, RAW）：线程 A 写入某地址后，线程 B 读取同一地址，但两者之间缺少同步屏障，线程 B 可能读到过期值。
- **先写后写冒险**（Write-After-Write, WAW）：线程 A 和线程 B 均写入同一地址，两者之间无同步保证，最终存储的值取决于执行顺序。
- **先读后写冒险**（Write-After-Read, WAR）：线程 A 读取某地址后，线程 B 覆盖写入同一地址，若执行顺序发生反转，线程 A 将读到线程 B 的新值而非预期的旧值。

### 4.2. Racecheck 使用

通过 `--tool racecheck` 选项启动数据冒险检测：

```bash
hggc-memcheck --tool racecheck [options] user_app [user_app options]
```

检测到 data hazards 后，用户通常可以在两个冲突操作之间的适当位置插入 `__syncthreads()` 来保证操作顺序，从而消除冒险。

> 警告：使用 `racecheck` 时不会执行内存越界检测。建议先使用 `memcheck` 工具确保程序没有非法的内存访问，再使用 `racecheck` 检测数据冒险。

### 4.3. Racecheck 报错示例

以下是使用 `--prefix "[HGGC-MC]"` 时的报错格式：

```text
[HGGC-MC] Error: Race reported between Write access at 0x7c000058 in source.hg:12:compute(int*, int*)
[HGGC-MC]     and Read access at 0x7c000070 in source.hg:18:compute(int*, int*) [48 hazards]
```

报告中列出产生冲突的两个操作：其中必然包含一个写操作，以及与之发生冒险的另一个操作（读或写）。每个操作附带设备端指令 PC；若编译时保留了行号信息，还会显示对应的源文件位置。方括号内的数字表示在该地址对上检测到的冒险总数。

比赛关联：自定义归约、attention 等使用 shared memory 的高吞吐算子，在优化时容易为追求性能删掉同步屏障；`racecheck` 能发现这类只在特定调度下偶发的精度漂移（表现为评测分数不稳定），这是排查"吞吐优化后精度掉点"类问题的关键工具。

## 5. Initcheck 工具

`initcheck` 工具用于在运行时检测 device 端对未初始化 global memory 的读取操作。当 kernel 读取了通过 `hggcMalloc` 分配但未经 `hggcMemset` 或 `hggcMemcpy` 初始化的内存区域时，`initcheck` 将报告错误。

### 5.1. Initcheck 使用

通过 `--tool initcheck` 选项启动未初始化内存检测：

```bash
hggc-memcheck --tool initcheck [options] user_app [user_app options]
```

当 kernel 在 device 端读取了未初始化的 global memory 时，`initcheck` 将触发报错。

> 警告：`initcheck` 不会对内存越界进行检查。使用前需确保程序没有越界访问，建议先运行 `memcheck` 工具进行验证。

## 6. Synccheck 工具

`synccheck` 工具用于在运行时检测 `__syncwarp()` 指令的不正确使用。当实际执行 `__syncwarp(mask)` 的线程超出 `mask` 参数指定的范围时，`synccheck` 将报告错误。

### 6.1. Synccheck 使用

通过 `--tool synccheck` 选项启动同步指令检测：

```bash
hggc-memcheck --tool synccheck [options] user_app [user_app options]
```

## 7. 使用示例

> 注：以下示例中使用 `--prefix "[HGGC-MC]"` 选项自定义输出前缀，以便于与其他工具的输出区分。开发者可通过 `--prefix` 选项设置任意前缀字符串（默认为 `=========`）。

### 7.1. Memcheck 使用示例

以下程序包含 global 内存越界、shared 内存越界、local 内存越界以及非对齐访问四种典型错误场景：

```c
#include <stdio.h>

// 场景1：向量缩放 — global 内存越界
// 当线程总数超过数组长度时，越界线程将读写未分配的内存
__global__ void scale_vector(float *dst, const float *src, float factor, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    dst[idx] = src[idx] * factor;
}

// 场景2：分块归约求和 — shared 内存越界
// 当 blockDim 超过分配的共享内存元素数时，越界线程写入 shared memory 之外
__global__ void block_reduce(const int *input, int *partial_sums) {
    extern __shared__ int sdata[];
    int tid = threadIdx.x;
    int gid = blockIdx.x * blockDim.x + tid;
    sdata[tid] = input[gid];
    __syncthreads();
    for (int stride = blockDim.x / 2; stride > 0; stride >>= 1) {
        if (tid < stride)
            sdata[tid] += sdata[tid + stride];
        __syncthreads();
    }
    if (tid == 0) partial_sums[blockIdx.x] = sdata[0];
}

// 场景3：数据填充 — local 内存（栈数组）越界
__device__ __noinline__ void fill_slot(int *addr, int val) {
    *addr = val;
}

__global__ void stack_overrun_demo(int offset) {
    int local_buf[8];
    fill_slot(&local_buf[offset], 99);
}

// 场景4：紧凑结构体 — 非对齐访问
struct __attribute__((packed)) SensorReading {
    char sensor_id;
    int value;       // 偏移量为 1 字节，不满足 4 字节对齐要求
};

__global__ void process_readings(SensorReading *readings) {
    readings[threadIdx.x].value = threadIdx.x * 10;
}

int main() {
    // 场景1：200 个元素的向量，使用 256 个线程 — 线程 200~255 将越界
    const int N = 200;
    float *d_src, *d_dst;
    hggcMalloc((void **)&d_src, N * sizeof(float));
    hggcMalloc((void **)&d_dst, N * sizeof(float));
    float h_data[200];
    for (int i = 0; i < N; i++) h_data[i] = (float)i;
    hggcMemcpy(d_src, h_data, N * sizeof(float), hggcMemcpyHostToDevice);
    scale_vector<<<1, 256>>>(d_dst, d_src, 2.0f, N);
    hggcDeviceSynchronize();

    // 场景2：64 个线程的归约，但只分配了 32 个 int 的 shared memory
    int *d_input, *d_partial;
    hggcMalloc((void **)&d_input, 64 * sizeof(int));
    hggcMalloc((void **)&d_partial, sizeof(int));
    int h_input[64];
    for (int i = 0; i < 64; i++) h_input[i] = 1;
    hggcMemcpy(d_input, h_input, 64 * sizeof(int), hggcMemcpyHostToDevice);
    block_reduce<<<1, 64, 32 * sizeof(int)>>>(d_input, d_partial);
    hggcDeviceSynchronize();

    // 场景3：栈数组越界 — offset=8 时写入 local_buf[8]，超出长度 8 的数组
    stack_overrun_demo<<<1, 1>>>(8);
    hggcDeviceSynchronize();

    // 场景4：紧凑结构体的 int 字段未对齐
    SensorReading *d_readings;
    hggcMalloc((void **)&d_readings, 4 * sizeof(SensorReading));
    process_readings<<<1, 4>>>(d_readings);
    hggcDeviceSynchronize();

    hggcFree(d_src); hggcFree(d_dst);
    hggcFree(d_input); hggcFree(d_partial);
    // 此处故意未释放 d_readings，用于后续演示泄漏检测
    return 0;
}
```

使用如下命令编译并运行 `memcheck` 工具：

```bash
hgcc memcheck_demo.hg
hggc-memcheck --prefix "[HGGC-MC]" --destroy-on-device-error kernel ./a.out
```

输出结果（节选）：

```text
[HGGC-MC] Invalid __global__ read of size 4
[HGGC-MC]     at: 0x7a0000c8 in scale_vector(float*, float const*, float, int)
[HGGC-MC]     by thread (200,0,0) in block (0,0,0)
[HGGC-MC]     Address 0x69e80320 is out of bounds
[HGGC-MC]     Saved host backtrace up to driver entry point at kernel launch time
[HGGC-MC]     Host Frame: (hgLaunchKernel + 0xad6) [0x7f2c935da766 ]
[HGGC-MC]     Host Frame: (hggcapiLaunchKernel + 0xad) [0x7f2c92f8c00d ]
[HGGC-MC]     Host Frame: (hggcLaunchKernel + 0x3e8) [0x7f2c930be6c8 ]
[HGGC-MC]     Host Frame: (_Z12scale_vectorPfPKffi + 0x90) [0x400b10 ]
[HGGC-MC]     Host Frame: (main + 0x12c) [0x400d8c ]
[HGGC-MC]     Host Frame: (__libc_start_main + 0xe7) [0x7f2c9224cc87 ]
[HGGC-MC]     Host Frame: (_start + 0x2a) [0x40089a ]
[HGGC-MC]
[HGGC-MC] Invalid __shared__ write of size 4
[HGGC-MC]     at: 0x7a000180 in block_reduce(int const*, int*)
[HGGC-MC]     by thread (32,0,0) in block (0,0,0)
[HGGC-MC]     Address 0x00000080 is out of bounds
[HGGC-MC]     Saved host backtrace up to driver entry point at kernel launch time
[HGGC-MC]     Host Frame: (hgLaunchKernel + 0xad6) [0x7f2c935da766 ]
......
[HGGC-MC]
[HGGC-MC] Invalid __private__ write of size 4
[HGGC-MC]     at: 0x7a000240 in fill_slot(int*, int)
[HGGC-MC]     by thread (0,0,0) in block (0,0,0)
[HGGC-MC]     Address 0x00000024 is out of bounds
[HGGC-MC]     Saved host backtrace up to driver entry point at kernel launch time
[HGGC-MC]     Host Frame: (hgLaunchKernel + 0xad6) [0x7f2c935da766 ]
......
[HGGC-MC]
[HGGC-MC] Invalid __global__ write of size 4
[HGGC-MC]     at: 0x7a000310 in process_readings(SensorReading*)
[HGGC-MC]     by thread (0,0,0) in block (0,0,0)
[HGGC-MC]     Address 0x69f00001 is misaligned
[HGGC-MC]     Saved host backtrace up to driver entry point at kernel launch time
[HGGC-MC]     Host Frame: (hgLaunchKernel + 0xad6) [0x7f2c935da766 ]
......
[HGGC-MC]
[HGGC-MC] ERROR SUMMARY: 60 errors
```

> 注：`ERROR SUMMARY` 中的错误计数取决于 `--destroy-on-device-error` 的设置以及运行时的线程调度情况，实际运行时的数值可能与上述示例不同。

添加 `-gline-tables-only` 编译选项可在报错中显示源文件行号：

```bash
hgcc memcheck_demo.hg -lineinfo
hggc-memcheck --prefix "[HGGC-MC]" --destroy-on-device-error kernel ./a.out
```

此时错误位置行将包含文件名和行号：

```text
[HGGC-MC] Invalid __global__ read of size 4
[HGGC-MC]     at: 0x7a0000c8 in memcheck_demo.hg:7:scale_vector(float*, float const*, float, int)
[HGGC-MC]     by thread (200,0,0) in block (0,0,0)
[HGGC-MC]     Address 0x69e80320 is out of bounds
......
```

#### 7.1.1. 内存泄漏检测

通过 `--leak-check full` 选项可在 HGGC context 销毁时检查未释放的设备内存。上述代码中未释放 `d_readings`，执行如下命令：

```bash
hggc-memcheck --prefix "[HGGC-MC]" --destroy-on-device-error kernel --leak-check full ./a.out
```

除常规的访存错误外，还会输出泄漏报告，包含泄漏的大小、地址以及在 host 端调用 `hggcMalloc` 分配时保存的调用栈：

```text
[HGGC-MC] Leaked 20 bytes at 0x6a100000
[HGGC-MC]     Saved host backtrace up to driver entry point at hggcMalloc time
[HGGC-MC]     Host Frame: (hggcapiMalloc + 0x64) [0x7f2c92f42b74 ]
[HGGC-MC]     Host Frame: (hggcMalloc + 0x2cb) [0x7f2c92fc251b ]
[HGGC-MC]     Host Frame: (main + 0x298) [0x400ef8 ]
[HGGC-MC]     Host Frame: (__libc_start_main + 0xe7) [0x7f2c9224cc87 ]
[HGGC-MC]     Host Frame: (_start + 0x2a) [0x40089a ]
[HGGC-MC]
[HGGC-MC] LEAK SUMMARY: 20 bytes leaked in 1 allocations
```

### 7.2. Racecheck 使用示例

以下程序演示了 shared memory 上的数据冒险场景——多个线程在无同步保护的情况下对同一 shared memory 地址进行读写：

```c
#define THREADS 128

__shared__ int smem[THREADS];

__global__
void sumKernel(int *data_in, int *sum_out)
{
    int tx = threadIdx.x;
    smem[tx] = data_in[tx] + tx; // 每个thread初始化自己的smem

    //没有进行同步，直接由thread直接进行累加
    if (tx == 0) {
        *sum_out = 0;
        for (int i = 0; i < THREADS; ++i)
            *sum_out += smem[i];
    }
}

int main(int argc, char **argv)
{
    int *data_in = NULL;
    int *sum_out = NULL;

    hggcMalloc((void**)&data_in, sizeof(int) * THREADS);
    hggcMalloc((void**)&sum_out, sizeof(int));
    hggcMemset(data_in, 0, sizeof(int) * THREADS);

    sumKernel<<<1, THREADS>>>(data_in, sum_out);
    hggcDeviceSynchronize();

    hggcFree(data_in);
    hggcFree(sum_out);
    return 0;
}
```

上述程序中，128 个线程分属 4 个 warp（128 / 32 = 4）。第 9 行的 `smem[tx] = data_in[tx] + tx` 每个thread初始化自己的smem，此时没有race。但是，第 15 行的读取只由thread 0进行，与第 9 行的写入之间缺少 `__syncthreads()`，会触发跨 warp 的 RAW 冒险。

编译并运行：

```bash
hgcc racecheck_example.hg -G
hggc-memcheck --prefix "[HGGC-MC]" --tool racecheck ./a.out
```

输出结果：

```text
[HGGC-MC] Error: Race reported between Write access at 0x48 in racecheck_example.hg:9:sumKernel(int*, int*)
[HGGC-MC]     and Read access at 0xb8 in racecheck_example.hg:14:sumKernel(int*, int*) [508 hazards]
[HGGC-MC]
[HGGC-MC] RACECHECK SUMMARY: 1 hazard(s) displayed (1 error, 0 warning)
```

> 注：方括号中的冒险计数取决于实际的 warp 调度与内存访问模式，不同运行环境下数值可能有所差异。

### 7.3. Initcheck 使用示例

以下程序演示了对未初始化设备内存的读取——通过 `hggcMalloc` 分配的内存未经初始化即被 kernel 读取使用：

```c
#define BLOCKS 2
#define THREADS 64

__global__ void square_elements(float *data) {
    int idx = threadIdx.x + blockDim.x * blockIdx.x;
    data[idx] = data[idx] * data[idx];
}

int main() {
    float *d_buf = NULL;
    hggcMalloc((void **)&d_buf, sizeof(float) * BLOCKS * THREADS);
    // 未对 d_buf 执行初始化（缺少 hggcMemcpy 或 hggcMemset 调用）

    square_elements<<<BLOCKS, THREADS>>>(d_buf);
    hggcDeviceSynchronize();

    hggcFree(d_buf);
    return 0;
}
```

上述程序在第 11 行通过 `hggcMalloc` 分配了设备内存，但未执行任何初始化操作即在第 14 行传入 kernel。kernel 第 6 行读取 `data[idx]` 时，访问的是未初始化的内存区域。

编译并运行：

```bash
hgcc initcheck_demo.hg
hggc-memcheck --prefix "[HGGC-MC]" --tool initcheck ./a.out
```

部分报错信息如下：

```text
[HGGC-MC] Uninitialized __global__ memory read of size 4
[HGGC-MC]     at: 0x00000130 in square_elements(float*)
[HGGC-MC]     by thread (0,0,0) in block (0,0,0)
[HGGC-MC]     Address 0x62a80000
[HGGC-MC]     Saved host backtrace up to driver entry point at kernel launch time
[HGGC-MC]     Host Frame: (hggcapiLaunchKernel + 0xa8) [0x7fc237b3cee8 ]
......
```

### 7.4. Synccheck 使用示例

以下程序演示了 `__syncwarp()` 的不正确使用——实际到达同步点的线程超出了 mask 指定的范围：

```c
#define BLOCK_SIZE 32

__shared__ int workspace[BLOCK_SIZE];

__global__ void warp_prefix_sum(int *result) {
    int tid = threadIdx.x;
    workspace[tid] = tid + 1;

    // __ballot_sync 统计满足条件的线程，返回对应 mask
    unsigned mask = __ballot_sync(0xffffffff, tid < 24);
    // 此时 mask = 0x00ffffff（低 24 位为 1）

    if (tid <= 24) {
        // 错误：25 个线程（tid 0~24）执行了 __syncwarp(mask)，
        // 但 mask 仅包含 24 个线程（tid 0~23），tid=24 不在 mask 中
        __syncwarp(mask);

        if (tid < 24)
            result[tid] = workspace[tid];
    }
    __syncthreads();
}

int main() {
    int *d_result;
    hggcMalloc((void **)&d_result, 24 * sizeof(int));
    warp_prefix_sum<<<1, BLOCK_SIZE>>>(d_result);
    hggcDeviceSynchronize();
    hggcFree(d_result);
    return 0;
}
```

上述程序中，`__ballot_sync` 返回的 mask 为 `0x00ffffff`（对应 tid 0~23），但 `if (tid <= 24)` 使得 tid=24 的线程也执行了 `__syncwarp(mask)`。由于 tid=24 不在 mask 的有效位中，`synccheck` 将报告同步错误。

编译并运行：

```bash
hgcc synccheck_demo.hg
hggc-memcheck --prefix "[HGGC-MC]" --tool synccheck ./a.out
```

部分报错信息如下：

```text
[HGGC-MC] Barrier error detected. Invalid arguments
[HGGC-MC]     at 0x000001a0 in warp_prefix_sum(int*)
[HGGC-MC]     by thread (24,0,0) in block (0,0,0)
[HGGC-MC]     Saved host backtrace up to driver entry point at kernel launch time
[HGGC-MC]     Host Frame: (hggcapiLaunchKernel + 0xa8) [0x7f83c41a1ee8 ]
[HGGC-MC]     Host Frame: (hggcLaunchKernel + 0x267) [0x7f83c41ca6a7 ]
......
```

### 7.5. coredump 使用示例

`memcheck` 支持在检测到越界时生成 coredump 文件，帮助用户借助调试器精确定位 kernel 代码中的越界指令。

```c
__global__ void foo(int *a) {
    a[threadIdx.x] = 0;
}

int main() {
    int *a;
    hggcMalloc((void **)&a, 32 * sizeof(int));
    foo<<<1, 33>>>(a);
    return 0;
}
```

上面是一个简单的越界写入示例——为 32 个 `int` 分配内存但启动了 33 个线程。运行如下命令生成 coredump：

```bash
# -G 选项生成完整调试信息，包含行号表（-lineinfo 的超集）
hgcc test.hg -G
hggc-memcheck --prefix "[HGGC-MC]" --generate-coredump yes --coredump-name hggc.core a.out
```

运行报错后，会产生名为 hggc.core 的 coredump 文件，使用 [ppu-gdb](13_ppu_gdb.md) 加载 coredump，可以直接定位到产生越界的源代码位置：

```text
#0  0x00000000b2000038 in foo (a=0xb1800000) at test.hg:2
2         a[threadIdx.x] = 0;
```

比赛关联：`--generate-coredump yes` + [ppu-gdb](13_ppu_gdb.md) 是"崩溃即定位"的完整链路——比赛调试期自研 kernel 在评测机上挂掉时，可凭 coredump 直接落到出错源码行，避免盲猜。

## 8. 已知问题

1. 当使用 HGGC graph 方式启动 kernel 时，`hggc-memcheck` 会强制使用 dynamic graph 形式执行。
2. 多线程环境下使用 HGGC graph 时，若多个线程同时启动的 graph 中包含多个 kernel node，可能出现运行错误或死锁。
3. 使用 `racecheck` 检查 async copy（即通过 vmem load 指令将数据加载到 TSM 共享内存的操作）时，仅能准确检测通过 commit group 进行同步的 async copy。对于通过 mbar（memory barrier）同步的 async copy，可能存在误报。

## 9. 常见问题

- **Q：程序运行退出时显示 "Error: process didn't terminate successfully"**

    A：该提示表明用户进程未正常退出，通常是因为发生了 segmentation fault。

- **Q：程序运行退出时显示 "Internal Sanitizer Error: an uncaught error occurred..."**

    A：通常是因为 `hggc-memcheck` 无法分配出足够的内存。`hggc-memcheck` 在运行时需要额外分配大量的内存，当分配失败时，工具将放弃之后的所有检查（但不会阻止用户进程继续运行）。可尝试通过 `--force-blocking-launches yes` 或 `--force-synchronization-limit` 选项，强制在指定 launch 次数后进行同步，来减少 `hggc-memcheck` 的内存占用。

比赛关联：工具本身要吃额外显存，在 32 GB 级显存上跑满 batch 的 VLM 推理时检查可能因内存不足而中断；调小并发并用 `--force-blocking-launches yes` / `--force-synchronization-limit` 限制工具内存占用，是让检查跑完的实用手段。另外注意 graph 启动会被强制走 dynamic graph，性能结论与真实评测路径有差异。
