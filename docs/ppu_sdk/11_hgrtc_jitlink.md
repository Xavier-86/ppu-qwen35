# 运行时编译与 JIT 链接（HGRTC + hgJitLink） <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [第 1 章 T-Head SAIL HGRTC](#第-1-章-t-head-sail-hgrtc)
  - [1.1. 概述](#11-概述)
  - [1.2. 开始](#12-开始)
  - [1.3. 用户接口](#13-用户接口)
  - [1.4. 支持的编译选项](#14-支持的编译选项)
  - [1.5. 语法](#15-语法)
  - [1.6. 编译缓存](#16-编译缓存)
- [第 2 章 T-Head SAIL hgJitLink](#第-2-章-t-head-sail-hgjitlink)
  - [2.1. 概述](#21-概述)
  - [2.2. 开始](#22-开始)
  - [2.3. 用户接口](#23-用户接口)
  - [2.4. 支持的链接选项](#24-支持的链接选项)
  - [2.5. 数据类型](#25-数据类型)


## 第 1 章 T-Head SAIL HGRTC

### 1.1. 概述
T-Head SAIL HG Runtime Compilation（以下简称 HGRTC）是面向真武 PPU（以下简称 PPU）异构计算架构的运行时编译库，隶属于 T-Head SAIL SDK 工具链。它接收字符串形式的 HGGC（HeteroGeneous General-purpose Computing）设备源代码，在应用程序运行期间即时生成可执行的 HGGC 二进制代码。生成的二进制代码可通过 HGGC Driver API 加载并运行。

与离线编译（即使用 clang 或 hgcc 预先编译）方式相比，运行时编译具备以下优势：

- 简化部署：最终交付物只需包含 T-Head SAIL SDK 运行时库，无须附带完整编译工具链。
- 降低延迟：编译过程不会产生单独的进程，没有额外的磁盘 I/O 开销。

以下为运行时编译技术的一般性应用场景说明（示意性列举，不构成官方推荐）：

| 场景 | 说明 |
| :--- | :--- |
| 高性能计算库 | 根据开发者传入的矩阵、数据类型生成最优 kernel |
| 深度学习框架 | 动态融合连续算子以减少设备内存访问 |
| 科学仿真 | 根据物理方程参数在运行时生成专用 kernel |

### 1.2. 开始
#### 1.2.1. 系统要求
| 项目 | 要求 |
| :--- | :--- |
| 操作系统 | Linux |
| 硬件 | PPU |
| 软件 | T-Head SAIL SDK Toolkit 及驱动 |

#### 1.2.2. 安装
HGRTC 随 T-Head SAIL SDK 一并安装，无需额外操作，SDK 部署后可在以下路径找到相应文件：

| 文件 | 用途 |
| :--- | :--- |
| `include/hgrtc.h` | C/C++ 头文件，包含全部 API 声明 |
| `lib/libhgrtc.so` | 动态链接库 |

#### 1.2.3. 工作流程
HGRTC 的使用遵循"创建 → 编译 → 提取 → 销毁"的生命周期模型：

```
源码字符串 ──► hgrtcCreateProgram ──► hgrtcCompileProgram ──► hgrtcGetHGBIN ──► hgrtcDestroyProgram
                   │                         │                       │
                   │                         │                       └─► 通过 Driver API 加载执行
                   │                         └─► 可选：获取编译日志、LTO IR（Link-Time Optimization Intermediate Representation）
                   └─► 可选：注册符号名表达式（hgrtcAddNameExpression）
```

#### 1.2.4. 第一个程序：SAXPY
本节将通过一个完整的 SAXPY(Single-Precision α·X Plus Y) 示例，展示 HGRTC 从源码编译到 kernel 执行的完整工作流。

第一步：编写设备端 kernel。

```cpp
const char *saxpySource =
    "extern \"C\" __global__                                             \n"
    "void saxpy(float alpha, float *x, float *y, float *out, size_t n)   \n"
    "{                                                                   \n"
    "    size_t idx = blockIdx.x * blockDim.x + threadIdx.x;             \n"
    "    if (idx < n) {                                                  \n"
    "        out[idx] = alpha * x[idx] + y[idx];                         \n"
    "    }                                                               \n"
    "}                                                                    \n";
```

第二步：创建编译单元并执行编译。

```cpp
hgrtcProgram prog;
// 构造编译单元，无额外头文件依赖
hgrtcCreateProgram(&prog,
                   saxpySource,  // 设备端源码
                   "saxpy.hg",   // 源文件标识
                   0,            // numHeaders
                   NULL,         // headers
                   NULL);        // includeNames
// 编译，选择 --fmad=false 选项
const char *opts[] = {"--fmad=false"};
hgrtcResult compileResult = hgrtcCompileProgram(prog, 1, opts);
```

第三步：获取编译产物和日志。

```cpp
// 获取编译日志
size_t logSize;
hgrtcGetProgramLogSize(prog, &logSize);
char *log = new char[logSize];
hgrtcGetProgramLog(prog, log);
// 获取二进制产物
size_t binSize = 0;
hgrtcGetHGBINSize(prog, &binSize);
char *hgBin = new char[binSize];
hgrtcGetHGBIN(prog, hgBin);
// 编译单元使用完毕后应立即释放
hgrtcDestroyProgram(&prog);
```

第四步：加载并执行 kernel。

```cpp
HGdevice hgDevice;
HGcontext context;
HGmodule module;
HGfunction kernel;
hgInit(0);
hgDeviceGet(&hgDevice, 0);
// V2: hgCtxCreate(&context, 0, hgDevice);
// V3: 新增第2参数 HGctxCreateParams*，传 NULL 表示创建常规上下文
hgCtxCreate(&context, NULL, 0, hgDevice);
hgModuleLoadData(&module, hgBin);
hgModuleGetFunction(&kernel, module, "saxpy");
// 准备输入数据
size_t n = NUM_THREADS * NUM_BLOCKS;
size_t bufferSize = n * sizeof(float);
float alpha = 2.5f;
float *inputX = new float[n], *inputY = new float[n], *result = new float[n];
for (size_t i = 0; i < n; ++i) {
    inputX[i] = 0.5f * i + 1.0f;
    inputY[i] = 0.3f * i + 2.0f;
}
// 分配设备内存并拷贝数据
HGdeviceptr dX, dY, dOut;
hgMemAlloc(&dX, bufferSize);
hgMemAlloc(&dY, bufferSize);
hgMemAlloc(&dOut, bufferSize);
hgMemcpyHtoD(dX, inputX, bufferSize);
hgMemcpyHtoD(dY, inputY, bufferSize);
// 启动 kernel
void *args[] = { &alpha, &dX, &dY, &dOut, &n };
hgLaunchKernel(kernel,
               NUM_BLOCKS, 1, 1,
               NUM_THREADS, 1, 1,
               0, NULL,
               args, 0);
hgCtxSynchronize();
// 取回结果
hgMemcpyDtoH(result, dOut, bufferSize);
// 释放资源
hgMemFree(dX);
hgMemFree(dY);
hgMemFree(dOut);
hgModuleUnload(module);
hgCtxDestroy(context);
delete[] inputX;
delete[] inputY;
delete[] result;
delete[] hgBin;
```

### 1.3. 用户接口
#### 1.3.1. 类型
核心类型 `hgrtcProgram` 是编译操作的载体，表示一个独立的编译单元。每个编译单元封装了源码、编译选项和编译产物，彼此互不干扰。

```cpp
typedef struct _hgrtcProgram *hgrtcProgram
```

`hgrtcProgram` 是编译单元的不透明句柄（opaque handle）。使用前须通过 `hgrtcCreateProgram` 创建，使用完毕后须通过 `hgrtcDestroyProgram` 释放。

#### 1.3.2. 编译接口
##### 1.3.2.1. 创建与销毁接口

**hgrtcCreateProgram**

从源码字符串构造一个编译单元。如果源码引用了额外头文件，需将头文件内容及名称一并传入；否则 `numHeaders` 置 0、`headers`/`includeNames` 传 `NULL`。

```cpp
hgrtcResult hgrtcCreateProgram(hgrtcProgram* prog, const char* src,
                               const char* name, int numHeaders,
                               const char * const *headers,
                               const char * const *includeNames)
```

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `prog` | [out] | 创建成功后写入新编译单元的句柄 |
| `src` | [in] | 设备源代码的 C 字符串 |
| `name` | [in] | 源文件标识名；传 `NULL` 或空串时使用 `"default_program"` |
| `numHeaders` | [in] | 附加头文件数量，≥ 0 |
| `headers` | [in] | 头文件内容数组；`numHeaders` 为 0 时可传 `NULL` |
| `includeNames` | [in] | 头文件名称数组；`numHeaders` 为 0 时可传 `NULL` |

典型场景：程序初始化阶段，将动态拼接好的 kernel 源码封装为编译单元。
注意事项：头文件名须与源码中的 `#include` 语句精确匹配。
可能的返回值：`HGRTC_SUCCESS`、`HGRTC_ERROR_OUT_OF_MEMORY`、`HGRTC_ERROR_PROGRAM_CREATION_FAILURE`、`HGRTC_ERROR_INVALID_INPUT`、`HGRTC_ERROR_INVALID_PROGRAM`。

**hgrtcDestroyProgram**

释放编译单元持有的全部资源，包括编译产物和符号名映射表。

```cpp
hgrtcResult hgrtcDestroyProgram(hgrtcProgram* prog)
```

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `prog` | [in] | 待释放的编译单元句柄指针；调用后 `*prog` 不再有效 |

典型场景：提取完二进制产物后释放编译单元以回收内存。
注意事项：释放后，此前通过 `hgrtcGetLoweredName` 获取的指针也随之失效。
可能的返回值：`HGRTC_SUCCESS`、`HGRTC_ERROR_INVALID_PROGRAM`。

##### 1.3.2.2. 编译与产物获取

**hgrtcCompileProgram**

提交编译请求并同步执行。编译选项通过 C 字符串数组传入，无选项时 `options` 可为 `NULL`。编译结果保留在编译单元内部，通过后续查询接口获取。

```cpp
hgrtcResult hgrtcCompileProgram(hgrtcProgram prog, int numOptions, const char * const *options)
```

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `prog` | [in] | 待编译的编译单元 |
| `numOptions` | [in] | 编译选项数量 |
| `options` | [in] | 编译选项的 C 字符串数组；数量为 0 时可传 `NULL` |

典型场景：设置好目标架构和优化参数后，触发实际编译流程。
注意事项：支持的编译选项详见第 1.4 节。
可能的返回值：`HGRTC_SUCCESS`、`HGRTC_ERROR_OUT_OF_MEMORY`、`HGRTC_ERROR_INVALID_INPUT`、`HGRTC_ERROR_INVALID_PROGRAM`、`HGRTC_ERROR_INVALID_OPTION`、`HGRTC_ERROR_COMPILATION`、`HGRTC_ERROR_BUILTIN_OPERATION_FAILURE`。

**hgrtcGetHGBINSize / hgrtcGetHGBIN**

两步获取编译产物：先用 `hgrtcGetHGBINSize` 查询字节数并分配缓冲区，再用 `hgrtcGetHGBIN` 获取二进制数据。

```cpp
hgrtcResult hgrtcGetHGBINSize(hgrtcProgram prog, size_t* hgbinSizeRet)
hgrtcResult hgrtcGetHGBIN(hgrtcProgram prog, char* hgbin)
```

hgrtcGetHGBINSize 参数：

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `prog` | [in] | 已完成编译的编译单元 |
| `hgbinSizeRet` | [out] | 写入二进制产物的字节数 |

hgrtcGetHGBIN 参数：

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `prog` | [in] | 已完成编译的编译单元 |
| `hgbin` | [out] | 调用者分配的缓冲区，大小不小于 `hgrtcGetHGBINSize` 返回的值 |

典型场景：编译成功后获取 HGBIN（HGGC Binary，HGGC 二进制代码）以供 `hgModuleLoadData` 或 `hgModuleLoadDataEx` 加载。
可能的返回值：`HGRTC_SUCCESS`、`HGRTC_ERROR_INVALID_INPUT`、`HGRTC_ERROR_INVALID_PROGRAM`。

**hgrtcGetLTOIRSize / hgrtcGetLTOIR**

获取 LTO IR。使用方式与 hgbin 获取相同——先查询大小，再拷贝数据。配合 `-dlto` 选项编译时使用。

```cpp
hgrtcResult hgrtcGetLTOIRSize(hgrtcProgram prog, size_t* LTOIRSizeRet)
hgrtcResult hgrtcGetLTOIR(hgrtcProgram prog, char* LTOIR)
```

hgrtcGetLTOIRSize 参数：

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `prog` | [in] | 已完成编译的编译单元 |
| `LTOIRSizeRet` | [out] | 写入 LTO IR 的字节数 |

hgrtcGetLTOIR 参数：

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `prog` | [in] | 已完成编译的编译单元 |
| `LTOIR` | [out] | 调用者分配的缓冲区 |

典型场景：跨模块链接时优化场景下，获取中间产物用于后续 link 操作。
可能的返回值：`HGRTC_SUCCESS`、`HGRTC_ERROR_INVALID_INPUT`、`HGRTC_ERROR_INVALID_PROGRAM`。

**hgrtcGetTIXSize / hgrtcGetTIX**

获取编译出的 TIX（T-Head Instruction eXtension）。使用方式与 hgbin 获取相同——先查询大小，再拷贝数据。

```cpp
hgrtcResult hgrtcGetTIXSize(hgrtcProgram prog, size_t *tixSizeRet)
hgrtcResult hgrtcGetTIX(hgrtcProgram prog, char *tix)
```

hgrtcGetTIXSize 参数：

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `prog` | [in] | 已完成编译的编译单元 |
| `tixSizeRet` | [out] | 写入 TIX 的字节数 |

hgrtcGetTIX 参数：

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `prog` | [in] | 已完成编译的编译单元 |
| `tix` | [out] | 调用者分配的缓冲区 |

典型场景：编译成功后获取 TIX。
可能的返回值：`HGRTC_SUCCESS`、`HGRTC_ERROR_INVALID_INPUT`、`HGRTC_ERROR_INVALID_PROGRAM`。

**hgrtcGetProgramLogSize / hgrtcGetProgramLog**

获取最近一次编译生成的诊断日志（含警告和错误信息）。日志字符串以 NULL 结尾，查询到的大小已包含该终止符。

```cpp
hgrtcResult hgrtcGetProgramLogSize(hgrtcProgram prog, size_t* logSizeRet)
hgrtcResult hgrtcGetProgramLog(hgrtcProgram prog, char* log)
```

hgrtcGetProgramLogSize 参数：

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `prog` | [in] | 编译单元 |
| `logSizeRet` | [out] | 日志字节数（含末尾 NULL） |

hgrtcGetProgramLog 参数：

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `prog` | [in] | 编译单元 |
| `log` | [out] | 调用者分配的缓冲区 |

典型场景：编译失败时检索诊断信息；编译成功时获取优化建议或警告。
可能的返回值：`HGRTC_SUCCESS`、`HGRTC_ERROR_INVALID_INPUT`、`HGRTC_ERROR_INVALID_PROGRAM`。

##### 1.3.2.3. 符号名查询
C++ 编译器会对 `__global__` 函数和 `__device__`/`__constant__` 变量名称进行修饰（name mangling）。在通过 Driver API 加载模块后按名称查找 kernel 时，需要知道修饰后的名称。HGRTC 提供了注册 → 编译 → 查询的三步机制来解决此问题。

**hgrtcAddNameExpression**

在编译之前注册一个符号名表达式。编译完成后可通过 `hgrtcGetLoweredName` 查询该表达式对应的底层名称。

```cpp
hgrtcResult hgrtcAddNameExpression(hgrtcProgram prog, const char * const name_expression)
```

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `prog` | [in] | 尚未编译的编译单元 |
| `name_expression` | [in] | 表示 `__global__` 函数或 `__device__`/`__constant__` 变量地址的常量表达式 |

典型场景：需要在运行时通过 Driver API 按名称定位 kernel 函数或设备变量。
注意事项：必须在 `hgrtcCompileProgram` 之前调用；编译后再调用将返回错误。
可能的返回值：`HGRTC_SUCCESS`、`HGRTC_ERROR_NO_NAME_EXPRESSIONS_AFTER_COMPILATION`。

**hgrtcGetLoweredName**

查询编译器为指定符号生成的底层名称（C++ name mangling 后的结果）。调用前须通过 `hgrtcAddNameExpression` 注册同一表达式，且编译已完成。

```cpp
hgrtcResult hgrtcGetLoweredName(hgrtcProgram prog, const char * const name_expression, const char** lowered_name)
```

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `prog` | [in] | 已完成编译的编译单元 |
| `name_expression` | [in] | 先前注册过的符号名表达式（字符串须完全一致） |
| `lowered_name` | [out] | 函数将此指针指向修饰后的名称字符串 |

典型场景：编译完成后，查询 kernel 函数的修饰名以传给 `hgModuleGetFunction`。
注意事项：返回的指针生命周期与编译单元绑定——`hgrtcDestroyProgram` 调用后该指针失效。传入的 `name_expression` 必须与注册时的字符串逐字符相同。
可能的返回值：`HGRTC_SUCCESS`、`HGRTC_ERROR_NO_LOWERED_NAMES_BEFORE_COMPILATION`、`HGRTC_ERROR_NAME_EXPRESSION_NOT_VALID`。

#### 1.3.3. 基础信息查询

**hgrtcGetErrorString**

将状态码转换为人类可读的诊断字符串。

```cpp
const char* hgrtcGetErrorString(hgrtcResult result)
```

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `result` | [in] | 任意 HGRTC API 返回的状态码 |

返回值：对应状态码的可读字符串指针（静态存储，无须释放）。

**hgrtcVersion**

查询当前链接的 HGRTC 库的主版本号和次版本号。建议在程序初始化阶段调用以确认 SDK 版本。

```cpp
hgrtcResult hgrtcVersion(int *major, int *minor)
```

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `major` | [out] | 主版本号 |
| `minor` | [out] | 次版本号 |

可能的返回值：`HGRTC_SUCCESS`、`HGRTC_ERROR_INVALID_INPUT`。

**hgrtcGetNumSupportedArchs**

查询 HGRTC 所支持的 PPU 架构数量。常与 `hgrtcGetSupportedArchs` 配合使用——先获取数量以分配数组，再填充具体架构值。

```cpp
hgrtcResult hgrtcGetNumSupportedArchs(int* numArchs)
```

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `numArchs` | [out] | 支持的架构数量 |

可能的返回值：`HGRTC_SUCCESS`、`HGRTC_ERROR_INVALID_INPUT`。

**hgrtcGetSupportedArchs**

将 HGRTC 支持的全部 PPU 架构写入调用者提供的数组。数组大小应不小于 `hgrtcGetNumSupportedArchs` 返回的数量。

```cpp
hgrtcResult hgrtcGetSupportedArchs(int* supportedArchs)
```

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `supportedArchs` | [out] | 调用者分配的整型数组 |

可能的返回值：`HGRTC_SUCCESS`、`HGRTC_ERROR_INVALID_INPUT`。

#### 1.3.4. 错误处理
HGRTC 的每个 API 函数（除 `hgrtcGetErrorString` 外）均返回 `hgrtcResult` 枚举值。可在每次调用后检查返回值，失败时获取编译日志以辅助定位问题。以下为典型的错误处理示例：

```cpp
hgrtcResult res = hgrtcCompileProgram(prog, numOpts, opts);
if (res != HGRTC_SUCCESS) {
    size_t logSize;
    hgrtcGetProgramLogSize(prog, &logSize);
    char *log = new char[logSize];
    hgrtcGetProgramLog(prog, log);
    // 处理错误：打印日志、通知上层...
    delete[] log;
}
```

全部状态码的含义和常见触发场景如下。

```cpp
typedef enum hgrtcResult {
    HGRTC_SUCCESS                                     = 0,
    HGRTC_ERROR_OUT_OF_MEMORY                         = 1,
    HGRTC_ERROR_PROGRAM_CREATION_FAILURE              = 2,
    HGRTC_ERROR_INVALID_INPUT                         = 3,
    HGRTC_ERROR_INVALID_PROGRAM                       = 4,
    HGRTC_ERROR_INVALID_OPTION                        = 5,
    HGRTC_ERROR_COMPILATION                           = 6,
    HGRTC_ERROR_BUILTIN_OPERATION_FAILURE             = 7,
    HGRTC_ERROR_NO_NAME_EXPRESSIONS_AFTER_COMPILATION = 8,
    HGRTC_ERROR_NO_LOWERED_NAMES_BEFORE_COMPILATION   = 9,
    HGRTC_ERROR_NAME_EXPRESSION_NOT_VALID             = 10,
    HGRTC_ERROR_INTERNAL_ERROR                        = 11,
    HGRTC_ERROR_NO_PCH_CREATE_ATTEMPTED               = 12,
    HGRTC_ERROR_PCH_CREATE                            = 13
} hgrtcResult;
```

| 状态码 | 数值 | 含义 | 常见触发场景 |
| :--- | :--- | :--- | :--- |
| `HGRTC_SUCCESS` | 0 | 操作成功 | — |
| `HGRTC_ERROR_OUT_OF_MEMORY` | 1 | 内存分配失败 | 编译大型程序时系统内存不足 |
| `HGRTC_ERROR_PROGRAM_CREATION_FAILURE` | 2 | 编译单元创建失败 | 源码格式异常 |
| `HGRTC_ERROR_INVALID_INPUT` | 3 | 参数不合法 | 传入 `NULL` 指针或无效参数 |
| `HGRTC_ERROR_INVALID_PROGRAM` | 4 | 编译单元句柄无效 | 使用已销毁或未初始化的句柄 |
| `HGRTC_ERROR_INVALID_OPTION` | 5 | 编译选项无法识别 | 拼写错误或使用不支持的选项 |
| `HGRTC_ERROR_COMPILATION` | 6 | 编译失败 | 源码存在语法或语义错误 |
| `HGRTC_ERROR_BUILTIN_OPERATION_FAILURE` | 7 | 内置操作失败 | 内部编译流水线异常 |
| `HGRTC_ERROR_NO_NAME_EXPRESSIONS_AFTER_COMPILATION` | 8 | 编译后不可注册符号 | 在 `hgrtcCompileProgram` 之后调用 `hgrtcAddNameExpression` |
| `HGRTC_ERROR_NO_LOWERED_NAMES_BEFORE_COMPILATION` | 9 | 编译前不可查询底层名 | 在 `hgrtcCompileProgram` 之前调用 `hgrtcGetLoweredName` |
| `HGRTC_ERROR_NAME_EXPRESSION_NOT_VALID` | 10 | 符号表达式无效 | 传入的表达式无法解析为合法符号 |
| `HGRTC_ERROR_INTERNAL_ERROR` | 11 | 库内部异常 | 内部处理异常 |
| `HGRTC_ERROR_NO_PCH_CREATE_ATTEMPTED` | 12 | 未尝试创建 PCH | 未启用 PCH 功能或编译器决定不创建 |
| `HGRTC_ERROR_PCH_CREATE` | 13 | PCH 创建失败 | 源码在头文件截止点前存在错误 |

#### 1.3.5. Host 侧函数

**hgrtcGetTypeName**

在主机获取模板类型参数 `T` 的源码级名称字符串，用于构造 `hgrtcAddNameExpression` 所需的名称表达式。

```cpp
template<typename T>
inline hgrtcResult hgrtcGetTypeName(std::string *result)
```

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `result` | [out] | 指向 `std::string` 对象的指针，函数成功后写入类型名称 |

典型场景：需要从主机模板参数推导设备端 kernel 模板实例化名称时使用。例如：

```cpp
std::string typeName;
hgrtcGetTypeName<float>(&typeName);
std::string expr = std::string("myKernel<") + typeName + ">";
hgrtcAddNameExpression(prog, expr.c_str());
```

注意事项：仅当宏 `HGRTC_GET_TYPE_NAME` 定义为非零值时可用。
可能的返回值：`HGRTC_SUCCESS`、`HGRTC_ERROR_INTERNAL_ERROR`。

### 1.4. 支持的编译选项
HGRTC 编译选项分为以下几类：目标架构与编译模式、代码生成与数学精度、调试、预处理、语言标准等。

#### 1.4.1. 选项格式
编译选项分为长格式和短格式两种写法。长格式以双横线 `--` 起始，短格式以单横线 `-` 起始，二者等价。

传递选项值的方式有三种：

| 写法 | 示例 | 适用范围 |
| :--- | :--- | :--- |
| 等号连接 | `--ftz=true` | 所有带参选项 |
| 空格分隔 | `--ftz true` | 所有带参选项 |
| 直接拼接 | `-DFOO`、`-I/usr/include` | 仅限 `-D`、`-U`、`-I` 等单字母选项 |

#### 1.4.2. 目标架构
| 选项 | 短格式 | 说明 |
| :--- | :--- | :--- |
| `--ppu-arch=<value>` | 无 | 指定目标 PPU 架构。可选值：`ppu001`、`ppu0015`。HGRTC 不支持在单次编译中生成多架构混合产物 |

#### 1.4.3. 编译模式
| 选项 | 短格式 | 说明 |
| :--- | :--- | :--- |
| `--device-c` | `-dc` | 启用可重定位代码生成，编译产物可与其他可重定位目标链接。等同于 `--relocatable-device-code=true` |
| `--device-w` | `-dw` | 生成不可重定位代码。等同于 `--relocatable-device-code=false` |
| `--relocatable-device-code={true\|false}` | `-rdc` | 显式控制是否生成可重定位代码。默认 `false` |
| `--dlink-time-opt` | `-dlto` | 生成 LTO IR，隐含 `-rdc=true`。使用此选项后应通过 `hgrtcGetLTOIR` 获取产物 |

#### 1.4.4. 代码生成
| 选项 | 短格式 | 说明 | 默认值 |
| :--- | :--- | :--- | :--- |
| `--opt-level` | `-O` | 设备代码优化级别 | -O3 |
| `--maxrregcount=<N>` | `-maxrregcount` | 指定 PPU 函数可使用的最大寄存器数量。如果未指定，则不设最大值 | 无限制 |
| `--dopt={true\|false}` | `-dopt` | 启用设备代码优化。与 `-G` 联合使用时生成有限调试信息（行号）的优化代码 | `false` |

#### 1.4.5. 数学运算精度
| 选项 | 短格式 | 说明 | 默认值 |
| :--- | :--- | :--- | :--- |
| `--ftz={true\|false}` | `-ftz` | 控制单精度浮点运算中非规格化数的处理方式。`=true` 清零以获得更高性能；`=false` 保留以确保精度 | `false` |
| `--prec-sqrt={true\|false}` | `-prec-sqrt` | 选择单精度平方根的计算策略。`=true` 遵循 IEEE 754 就近舍入；`=false` 使用近似指令换取更高性能 | `true` |
| `--prec-div={true\|false}` | `-prec-div` | 选择单精度除法和倒数的计算策略。`=true` 遵循 IEEE 754；`=false` 使用近似计算 | `true` |
| `--fmad={true\|false}` | `-fmad` | 控制是否将浮点乘法与加（减）法合并为乘加融合指令 | `true` |
| `--use_fast_math` | `-use_fast_math` | 全局快速数学模式，等效于同时设置 `--ftz=true --prec-div=false --prec-sqrt=false --fmad=true` | `false`  |
| `--math_custom_cfg=<value>` | 无 | 自定义数学库配置，具体取值参见数学库文档（06_math_api.md） | 无 |

#### 1.4.6. 调试
| 选项 | 短格式 | 说明 |
| :--- | :--- | :--- |
| `--device-debug` | `-G` | 生成完整调试信息。若未同时指定 `--dopt`，将关闭全部优化 |
| `--generate-line-info` | `-lineinfo` | 仅生成行号映射信息，不影响优化 |
| `--time=<file-name>` | `-time` | 记录每个编译阶段耗时，并追加到选项参数指定的文件末尾。文件名为 `-` 时将计时数据写入编译日志 |
| `--disable-warnings` | `-w` | 屏蔽所有警告信息 |

#### 1.4.7. 预处理
| 选项 | 短格式 | 说明 | 默认值 |
| :--- | :--- | :--- | :--- |
| `--define-macro=<def>` | `-D` | 定义预处理宏。`-Dname` 等价于 `#define name 1`；`-Dname=definition` 等价于 `#define name definition`，内嵌换行符会截断定义 | 无 |
| `--undefine-macro=<def>` | `-U` | 取消先前的宏定义 | 无 |
| `--include-path=<dir>` | `-I` | 将目录加入头文件搜索路径 | 无 |
| `--pre-include=<header>` | `-include` | 在预处理阶段包含指定头文件 | 无 |
| `--no-source-include` | `-no-source-include` | 禁止预处理器自动将源文件所在目录添加到 include 路径 | 无 |

#### 1.4.8. 语言标准
| 选项 | 短格式 | 说明 | 默认值 |
| :--- | :--- | :--- | :--- |
| `--std={c++11,c++14,c++17}` | `-std` | 指定设备代码遵循的 C++ 语言标准 | `c++17` |
| `--builtin-move-forward={true\|false}` | `-builtin-move-forward` | 选用 C++11 及以上标准时，提供 `std::move` 和 `std::forward` 的内置实现 | `true` |
| `--builtin-initializer-list={true\|false}` | `-builtin-initializer-list` | 选用 C++11 及以上标准时，提供 `std::initializer_list` 的内置实现 | `true` |

#### 1.4.9. 其他
| 选项 | 短格式 | 说明 |
| :--- | :--- | :--- |
| `--device-as-default-execution-space` | `-default-device` | 将源码中无执行空间标注的实体视为 `__device__` 实体 |
| `--device-int128` | `-device-int128` | 允许在设备代码中使用 `__int128` 类型 |
| `--output-file` | `-o` | 指定输出文件名；不设置时默认与输入文件同名 |
| `--no-cache` | `-no-cache` | 禁用本次编译的缓存读写 |

比赛关联：如果需要在 PPU 上手工编写/调优融合算子 kernel，`--maxrregcount`、`--use_fast_math`、`--ppu-arch` 等选项与离线编译参数语义一致，可用于寄存器占用与数学精度的权衡实验（注意精度类选项可能影响精度保持评分，需实测）。

### 1.5. 语法
HGRTC 仅处理设备代码，不接受主机代码或主机编译器扩展语法。

#### 1.5.1. Include 规则
当调用 `hgrtcCreateProgram` 传入文件名时，预处理器会默认将文件目录添加到头文件搜索路径中，因此通过 `#include "..."` 形式包含的头文件能够被正确解析。此行为可通过 `--no-source-include` 选项禁用。

此外，可通过 `hgrtcCreateProgram` 的 `headers`/`includeNames` 参数直接提供头文件内容，或通过 `-I` 选项指定额外的头文件搜索目录。

#### 1.5.2. 预定义宏与类型
编译环境检测宏：
可通过检查 `__HGGCCC_RTC__` 宏是否已定义来区分离线编译与运行时编译。此宏仅在 HGRTC 运行时编译环境中定义。

其他预定义宏：

| 宏 | 用途 |
| :--- | :--- |
| `__HGGC_ARCH__` | 目标架构标识，与离线编译时的语义一致 |
| `__cplusplus` | 当前选定的 C++ 语言标准 |
| `NULL` | 空指针常量 |

预定义基本类型：`clock_t`、`size_t`、`ptrdiff_t`。

#### 1.5.3. 注意事项
- HGRTC 仅处理设备代码，不接受主机代码。可通过 `--device-as-default-execution-space` 选项将无执行空间标注的代码实体视为 `__device__` 实体。
- 运行时编译环境中默认语言标准为 C++17；可通过 `--std` 选项调整。

### 1.6. 编译缓存
#### 1.6.1. 编译缓存
HGRTC 内置编译缓存机制，对相同源码在编译命令、相关环境变量和 SDK 版本等条件均一致的前提下，将会自动复用首次编译的产物，避免重复编译以节省时间。

缓存命中条件：源码内容、源文件标识、前端编译选项、SDK 版本、HGRTC 版本时间戳均须一致。对于 hgbin 产物，还需后端编译选项和 `HGGC_OPTIONS_FOR_BACKEND_TUNING` 环境变量一致。
缓存失效行为：当任一条件变化时，缓存自动失效，系统将执行全量编译并生成新缓存。
关闭方式：设置环境变量 `HGRTC_CACHE_DISABLE=1`，或在编译选项中添加 `-no-cache`。

##### 1.6.1.1. 缓存相关环境变量
| 环境变量 | 默认值 | 说明 |
| :--- | :--- | :--- |
| `HGRTC_CACHE_DISABLE` | `0`（开启） | 设为 `1` 关闭缓存读写 |
| `HGRTC_CACHE_MAXSIZE` | 1 GB（单位：字节） | 缓存容量上限，超限后逐出最旧文件；设为 `0` 等效于关闭缓存 |
| `HGRTC_CACHE_PRUN_INTERVAL_SECONDS` | `0` | 容量超限检查的最小时间间隔（秒），可根据 I/O 敏感度调整 |
| `HGRTC_CACHE_PATH` | `$HOME/.hg/ComputeCache/` | 缓存文件存储目录。当默认路径位于网络文件系统时，建议重定向到本地磁盘以降低访问延迟 |

##### 1.6.1.2. 缓存文件类型
| 文件 | 对应 API | 额外条件 |
| :--- | :--- | :--- |
| `nameExpressionsMap.txt` | `hgrtcGetLoweredName()` | 除基本条件外，还需 `hgrtcAddNameExpression()` 的输入一致 |
| LTO IR | `hgrtcGetLTOIR()` | 基本条件一致即可 |
| TIX | `hgrtcGetTIX()` | 基本条件一致即可 |
| HGBIN | `hgrtcGetHGBIN()` | 还需后端选项和 `HGGC_OPTIONS_FOR_BACKEND_TUNING` 一致 |

#### 1.6.2. 预编译头
预编译头（Precompiled Header，以下简称 PCH）是用于优化编译耗时的特性。当多次编译任务 `#include "..."` 头文件语句相同时，HGRTC 可将首次解析的头文件状态保存为 PCH 文件，后续编译直接复用，从而加速编译过程。

##### 1.6.2.1. PCH 工作流程
```
首次编译：源码 ──► 解析头文件 ──► 到达截止点 ──► 保存 PCH ──► 继续编译
后续编译：源码 ──► 检测到可用 PCH ──► 跳过头文件解析 ──► 继续编译（节省时间）
```

PCH 文件的兼容性取决于：头文件包含顺序、编译选项、SDK 版本均须与创建时一致。

##### 1.6.2.2. PCH 使用模式
| 模式 | 选项 | 说明 |
| :--- | :--- | :--- |
| 自动模式 | `-pch` | 编译器自动创建和复用 PCH 文件，无须人工管理 |
| 手动创建 | `--create-pch=<filename>` | 将 PCH 文件输出到指定路径，由用户管理生命周期 |
| 手动使用 | `--use-pch=<filename>` | 指定使用已有的 PCH 文件进行编译 |

##### 1.6.2.3. PCH 相关编译选项
| 选项 | 默认值 | 说明 |
| :--- | :--- | :--- |
| `--pch-dir=<directory>` | 无 | 自动模式下指定 PCH 查找和创建目录；手动模式下作为非绝对路径的前缀 |
| `--pch-verbose={true\|false}` | `true` | 自动模式下，输出 PCH 文件不兼容的原因 |
| `--pch-messages={true\|false}` | `true` | 输出 PCH 文件的创建或复用信息 |
| `--instantiate-templates-in-pch={true\|false}` | `true` | 在 PCH 中预实例化模板。开启时 PCH 体积增大，但后续编译更快 |

##### 1.6.2.4. PCH 源码控制指令
| Pragma | 作用域 | 说明 |
| :--- | :--- | :--- |
| `#pragma hg_hdrstop` | 源文件 | 标记 PCH 内容的截止点——此行之前的头文件包含将纳入 PCH |
| `#pragma hg_no_pch` | 源文件 | 即使编译选项启用了 PCH，本文件也不生成或使用 PCH |

示例：

```cpp
#include "common_headers.h"
#pragma hg_hdrstop          // 截止点：以上头文件可被预编译
#include "module_specific.h" // 此头文件不纳入 PCH
__global__ void compute(float *data) { /* ... */ }
```

##### 1.6.2.5. 查询 PCH 创建状态

**hgrtcGetPCHCreateStatus**

查询最近一次编译中 PCH 文件的创建状态。

```cpp
hgrtcResult hgrtcGetPCHCreateStatus(hgrtcProgram prog)
```

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `prog` | [in] | 已完成编译的编译单元 |

可能的返回值：

| 状态码 | 含义 |
| :--- | :--- |
| `HGRTC_SUCCESS` | PCH 创建成功 |
| `HGRTC_ERROR_NO_PCH_CREATE_ATTEMPTED` | 未尝试创建 PCH（未启用 PCH 功能或编译器决定不创建） |
| `HGRTC_ERROR_PCH_CREATE` | 创建失败（源码在截止点前存在错误） |
| `HGRTC_ERROR_INVALID_INPUT` | 参数无效 |
| `HGRTC_ERROR_INVALID_PROGRAM` | 编译单元无效 |

##### 1.6.2.6. 预留接口
目前使用 PCH 功能无需开辟堆空间。

```cpp
hgrtcResult hgrtcGetPCHHeapSize(size_t *ret)
hgrtcResult hgrtcGetPCHHeapSizeRequired(hgrtcProgram prog, size_t* size)
hgrtcResult hgrtcSetPCHHeapSize(size_t size)
```

比赛关联：若比赛中采用运行时编译自定义 kernel（如融合量化 dequant、算子融合），编译缓存与 PCH 可显著缩短首次之后的编译耗时；但需确认比赛规则是否允许跨运行持久化缓存，评测环境下应评估 `HGRTC_CACHE_PATH` 位置与缓存命中对 TTFT 的影响。

## 第 2 章 T-Head SAIL hgJitLink

### 2.1. 概述
hgJitLink 为真武 PPU（以下简称 PPU）平台提供运行时设备代码链接能力。在某些应用场景中，设备代码模块需要在程序运行过程中动态组合——例如根据运行时条件选择不同的 kernel 实现，或将分离编译的多个设备代码片段合并为可执行的二进制。hgJitLink 便用于为此类场景提供支持。

该库支持多种输入格式，包括主机目标文件（host objects）、主机库（host libraries）、fatbin、device hgbin 以及 LTO（Link-Time Optimization） IR。链接完成后输出可直接加载的 hgbin 二进制，通过 HGGC（HeteroGeneous General-purpose Computing）Driver API 即可将其载入设备执行。对于包含 LTO IR 的输入，hgJitLink 还支持在链接阶段执行链接时优化。

### 2.2. 开始
#### 2.2.1. 系统要求

| 项目 | 要求 |
| :--- | :--- |
| 操作系统 | Linux |
| 硬件 | PPU |
| 软件 | T-Head SAIL SDK Toolkit 及驱动 |

#### 2.2.2. 安装
hgJitLink 随 T-Head SAIL SDK 一并安装，无需额外操作，SDK 部署后可在以下路径找到相应文件：

| 文件 | 路径 |
| :--- | :--- |
| 头文件 | `include/hgJitLink.h` |
| 动态链接库 | `lib/libhgJitLink.so` |

#### 2.2.3. 基本用法

以下代码展示了 hgJitLink 的基本使用流程：创建会话、追加设备代码、执行链接、提取产物并加载到设备。

```cpp
hgJitLinkHandle link_session;
hgJitLinkResult result;
const char* link_opts[] = {"-arch=ppu001"};

// 创建会话，指定目标架构
result = hgJitLinkCreate(&link_session, 1, link_opts);
if (result != HGJITLINK_SUCCESS) {
    return result;  // 选项不合法或架构未指定等
}

// 追加一段 LTO IR 格式的设备代码
result = hgJitLinkAddData(link_session, HGJITLINK_INPUT_LTOIR,
                          ltoir_code, ltoir_size, "my_kernel");
if (result != HGJITLINK_SUCCESS) {
    hgJitLinkDestroy(&link_session);
    return result;
}

// 将所有已添加的输入合并为目标二进制
result = hgJitLinkComplete(link_session);
if (result != HGJITLINK_SUCCESS) {
    // 链接失败时可通过 hgJitLinkGetErrorLog 查看错误细节
    hgJitLinkDestroy(&link_session);
    return result;
}

// 提取链接产物
size_t binary_size;
hgJitLinkGetLinkedHgbinSize(link_session, &binary_size);
void* device_binary = malloc(binary_size);
hgJitLinkGetLinkedHgbin(link_session, device_binary);

// 通过 Driver API 将二进制加载到设备
HGmodule module;
hgModuleLoadData(&module, device_binary);

// 释放会话及缓冲区
hgJitLinkDestroy(&link_session);
free(device_binary);
```

### 2.3. 用户接口

#### 2.3.1. 创建与销毁

**hgJitLinkCreate**

```cpp
hgJitLinkResult hgJitLinkCreate(hgJitLinkHandle *handle, uint32_t numOptions, const char **options)
```

创建一个新的会话。调用方需传入配置选项（如目标架构），创建成功后函数会通过 `handle` 输出一个可用的会话句柄。此句柄将在后续所有操作中标识该会话，直到通过 `hgJitLinkDestroy` 释放。

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | out | 接收新建会话句柄的指针 |
| `numOptions` | in | `options` 数组的元素个数 |
| `options` | in | 配置选项的字符串数组，每个元素为一条选项（如 `"-arch=ppu001"`） |

可能的返回值：

| 返回值 | 含义 |
| :--- | :--- |
| `HGJITLINK_SUCCESS` | 会话创建成功 |
| `HGJITLINK_ERROR_UNRECOGNIZED_OPTION` | 选项字符串无法识别 |
| `HGJITLINK_ERROR_MISSING_ARCH` | 未通过 `-arch` 指定目标架构 |
| `HGJITLINK_ERROR_INVALID_INPUT` | 参数不合法（如空指针） |
| `HGJITLINK_ERROR_INTERNAL` | 库内部异常 |

**hgJitLinkDestroy**

```cpp
hgJitLinkResult hgJitLinkDestroy(hgJitLinkHandle *handle)
```

终止会话并释放与该句柄关联的内存。调用完成后，`*handle` 将被置为 `NULL`，后续不得再使用该句柄。

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | in | 待释放的会话句柄的地址 |

可能的返回值：

| 返回值 | 含义 |
| :--- | :--- |
| `HGJITLINK_SUCCESS` | 资源已回收 |
| `HGJITLINK_ERROR_INVALID_INPUT` | 句柄无效 |
| `HGJITLINK_ERROR_INTERNAL` | 库内部异常 |

#### 2.3.2. 添加输入

**hgJitLinkAddData**

```cpp
hgJitLinkResult hgJitLinkAddData(hgJitLinkHandle handle, hgJitLinkInputType inputType, const void *data, size_t size, const char *name)
```

向当前会话追加一段内存中的设备代码。

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | in | 当前会话的句柄 |
| `inputType` | in | 数据格式标识，取值见 `hgJitLinkInputType` |
| `data` | in | 指向设备代码数据的内存缓冲区 |
| `size` | in | 缓冲区数据的字节数 |
| `name` | in | 输入对象名称 |

可能的返回值：

| 返回值 | 含义 |
| :--- | :--- |
| `HGJITLINK_SUCCESS` | 数据已成功追加 |
| `HGJITLINK_ERROR_INVALID_INPUT` | 数据内容或参数不合法 |
| `HGJITLINK_ERROR_INTERNAL` | 库内部异常 |

**hgJitLinkAddFile**

```cpp
hgJitLinkResult hgJitLinkAddFile(hgJitLinkHandle handle, hgJitLinkInputType inputType, const char *fileName)
```

向当前会话添加一段文件中的设备代码。

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | in | 当前会话的句柄 |
| `inputType` | in | 文件内容的格式标识，取值见 `hgJitLinkInputType` |
| `fileName` | in | 文件路径 |

可能的返回值：

| 返回值 | 含义 |
| :--- | :--- |
| `HGJITLINK_SUCCESS` | 文件已成功读取并追加 |
| `HGJITLINK_ERROR_INVALID_INPUT` | 文件路径无效或内容不合法 |
| `HGJITLINK_ERROR_INTERNAL` | 库内部异常 |

#### 2.3.3. 链接执行

**hgJitLinkComplete**

```cpp
hgJitLinkResult hgJitLinkComplete(hgJitLinkHandle handle)
```

对当前会话中已添加的全部输入进行链接，生成最终的目标二进制。链接完成后，可通过结果获取接口提取产物。

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | in | 当前会话的句柄 |

可能的返回值：

| 返回值 | 含义 |
| :--- | :--- |
| `HGJITLINK_SUCCESS` | 链接成功完成 |
| `HGJITLINK_ERROR_INVALID_INPUT` | 会话状态不合法 |
| `HGJITLINK_ERROR_INTERNAL` | 库内部异常 |

#### 2.3.4. 获取产物

**hgJitLinkGetLinkedHgbin**

```cpp
hgJitLinkResult hgJitLinkGetLinkedHgbin(hgJitLinkHandle handle, void *hgbin)
```

将链接产生的 hgbin 文件写入调用方提供的缓冲区。使用前需先调用 `hgJitLinkGetLinkedHgbinSize` 获取所需的缓冲区大小，并分配足够的空间。

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | in | 已完成链接的会话句柄 |
| `hgbin` | out | 接收 hgbin 二进制的缓冲区，大小不小于 `hgJitLinkGetLinkedHgbinSize` 返回的值 |

可能的返回值：

| 返回值 | 含义 |
| :--- | :--- |
| `HGJITLINK_SUCCESS` | hgbin 已写入缓冲区 |
| `HGJITLINK_ERROR_INVALID_INPUT` | 句柄或缓冲区无效 |
| `HGJITLINK_ERROR_INTERNAL` | 库内部异常 |

**hgJitLinkGetLinkedHgbinSize**

```cpp
hgJitLinkResult hgJitLinkGetLinkedHgbinSize(hgJitLinkHandle handle, size_t *size)
```

查询链接完成后生成的 hgbin 二进制的字节数。该值用于在调用 `hgJitLinkGetLinkedHgbin` 前分配用于接收二进制的缓冲区。

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | in | 已完成链接的会话句柄 |
| `size` | out | 接收 hgbin 字节数的指针 |

可能的返回值：

| 返回值 | 含义 |
| :--- | :--- |
| `HGJITLINK_SUCCESS` | 查询成功 |
| `HGJITLINK_ERROR_INVALID_INPUT` | 句柄或指针无效 |
| `HGJITLINK_ERROR_INTERNAL` | 库内部异常 |

**hgJitLinkGetLinkedTIX**

```cpp
hgJitLinkResult hgJitLinkGetLinkedTIX(hgJitLinkHandle handle, char *tix)
```

将链接产生的 TIX（T-Head Instruction eXtension）文本写入调用方提供的缓冲区。使用前需先调用 `hgJitLinkGetLinkedTIXSize` 获取所需的缓冲区大小，并分配足够的空间。

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | in | 已完成链接的会话句柄 |
| `tix` | out | 接收 TIX 文本的缓冲区，大小不小于 `hgJitLinkGetLinkedTIXSize` 返回的值 |

可能的返回值：

| 返回值 | 含义 |
| :--- | :--- |
| `HGJITLINK_SUCCESS` | TIX 已写入缓冲区 |
| `HGJITLINK_ERROR_INVALID_INPUT` | 句柄或缓冲区无效 |
| `HGJITLINK_ERROR_INTERNAL` | 库内部异常 |

**hgJitLinkGetLinkedTIXSize**

```cpp
hgJitLinkResult hgJitLinkGetLinkedTIXSize(hgJitLinkHandle handle, size_t *size)
```

查询链接完成后生成的 TIX 文本的字节数。该值用于在调用 `hgJitLinkGetLinkedTIX` 前分配接收缓冲区。

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | in | 已完成链接的会话句柄 |
| `size` | out | 接收 TIX 字节数的指针 |

可能的返回值：

| 返回值 | 含义 |
| :--- | :--- |
| `HGJITLINK_SUCCESS` | 查询成功 |
| `HGJITLINK_ERROR_INVALID_INPUT` | 句柄或指针无效 |
| `HGJITLINK_ERROR_INTERNAL` | 库内部异常 |

#### 2.3.5. 日志与诊断

链接过程中产生的诊断信息分为两类：**错误日志**（Error Log）记录导致链接失败的具体问题，**信息日志**（Info Log）记录警告、统计或详细过程信息。两者均通过"先查询大小、再提取内容"的模式获取。

**hgJitLinkGetErrorLog**

```cpp
hgJitLinkResult hgJitLinkGetErrorLog(hgJitLinkHandle handle, char *log)
```

将错误日志内容写入调用方提供的缓冲区。使用前需先调用 `hgJitLinkGetErrorLogSize` 获取所需的缓冲区大小，并分配足够的空间。

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | in | 当前会话的句柄 |
| `log` | out | 接收错误日志文本的缓冲区，大小不小于 `hgJitLinkGetErrorLogSize` 返回的值 |

可能的返回值：

| 返回值 | 含义 |
| :--- | :--- |
| `HGJITLINK_SUCCESS` | 日志已写入 |
| `HGJITLINK_ERROR_INVALID_INPUT` | 句柄或缓冲区无效 |
| `HGJITLINK_ERROR_INTERNAL` | 库内部异常 |

**hgJitLinkGetErrorLogSize**

```cpp
hgJitLinkResult hgJitLinkGetErrorLogSize(hgJitLinkHandle handle, size_t *size)
```

查询当前会话中错误日志的字节数，用于分配接收缓冲区。

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | in | 当前会话的句柄 |
| `size` | out | 接收字节数的指针 |

可能的返回值：

| 返回值 | 含义 |
| :--- | :--- |
| `HGJITLINK_SUCCESS` | 查询成功 |
| `HGJITLINK_ERROR_INVALID_INPUT` | 句柄或指针无效 |
| `HGJITLINK_ERROR_INTERNAL` | 库内部异常 |

**hgJitLinkGetInfoLog**

```cpp
hgJitLinkResult hgJitLinkGetInfoLog(hgJitLinkHandle handle, char *log)
```

将信息日志内容写入调用方提供的缓冲区。使用前需先调用 `hgJitLinkGetInfoLogSize` 获取所需的缓冲区大小，并分配足够的空间。信息日志中可能包含 `--verbose` 和 `--time` 选项产生的输出。

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | in | 当前会话的句柄 |
| `log` | out | 接收信息日志文本的缓冲区，大小不小于 `hgJitLinkGetInfoLogSize` 返回的值 |

可能的返回值：

| 返回值 | 含义 |
| :--- | :--- |
| `HGJITLINK_SUCCESS` | 日志已写入 |
| `HGJITLINK_ERROR_INVALID_INPUT` | 句柄或缓冲区无效 |
| `HGJITLINK_ERROR_INTERNAL` | 库内部异常 |

**hgJitLinkGetInfoLogSize**

```cpp
hgJitLinkResult hgJitLinkGetInfoLogSize(hgJitLinkHandle handle, size_t *size)
```

查询当前会话中信息日志的字节数，用于分配接收缓冲区。

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | in | 当前会话的句柄 |
| `size` | out | 接收字节数的指针 |

可能的返回值：

| 返回值 | 含义 |
| :--- | :--- |
| `HGJITLINK_SUCCESS` | 查询成功 |
| `HGJITLINK_ERROR_INVALID_INPUT` | 句柄或指针无效 |
| `HGJITLINK_ERROR_INTERNAL` | 库内部异常 |

#### 2.3.6. 版本查询

**hgJitLinkVersion**

```cpp
hgJitLinkResult hgJitLinkVersion(const char **version)
```

获取当前 hgJitLink 库的版本标识字符串。

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `version` | out | 接收版本字符串指针的地址 |

可能的返回值：

| 返回值 | 含义 |
| :--- | :--- |
| `HGJITLINK_SUCCESS` | 查询成功 |
| `HGJITLINK_ERROR_INVALID_INPUT` | 传入了空指针 |
| `HGJITLINK_ERROR_INTERNAL` | 库内部异常 |

### 2.4. 支持的链接选项

通过 `hgJitLinkCreate` 传入的选项可对链接行为进行控制。选项名以单横线 `-` 或双横线 `--` 开头，带值的选项使用 `=` 连接选项和值（中间不含空格），中间不含空格，如 `-arch=ppu001`。

#### 2.4.1. 架构选项

指定链接目标的 PPU 架构。

| 选项 | 别名 | 说明 | 默认值 | 示例 |
| :--- | :--- | :--- | :--- | :--- |
| `-arch <arch>` | 无 | 指定目标 PPU 架构型号，如 `ppu001`、`ppu0015` | `ppu001` | `-arch=ppu001` |

#### 2.4.2. 优化选项

控制链接阶段的代码优化行为。

| 选项 | 别名 | 说明 | 默认值 | 示例 |
| :--- | :--- | :--- | :--- | :--- |
| `-O<n>` | 无 | 设置优化级别，`n` 取值 0–3；级别越高优化越激进 | `-O3` | `-O2` |
| `--link-time-opt` | `-lto`, `--dlto` | 执行链接时优化 | 未启用 | `--link-time-opt` |
| `-ftz=<n>` | 无 | 控制非规格化浮点数是否刷为零（Flush to Zero） | `-ftz=0` | `-ftz=1` |
| `-prec-div=<n>` | 无 | 控制浮点除法的精度模式 | `-prec-div=0` | `-prec-div=1` |
| `-prec-sqrt=<n>` | 无 | 控制浮点平方根计算的精度模式 | `-prec-sqrt=0` | `-prec-sqrt=1` |
| `-fma=<n>` | 无 | 控制是否生成融合乘加（Fused Multiply-Add）指令 | `-fma=0` | `-fma=1` |

#### 2.4.3. 调试选项

用于生成调试符号和链接过程的运行信息。

| 选项 | 别名 | 说明 | 默认值 | 示例 |
| :--- | :--- | :--- | :--- | :--- |
| `-g` | 无 | 在输出二进制中嵌入调试信息 | 未启用 | `-g` |
| `--verbose` | `-v` | 在信息日志中输出链接过程的详细信息 | 未启用 | `--verbose` |
| `--time` | `-time` | 在信息日志中输出链接各阶段的耗时统计 | 未启用 | `--time` |

#### 2.4.4. 符号裁剪选项

通过声明实际使用的 kernel 和变量，允许链接器移除未被引用的代码和数据，从而减小输出体积。

| 选项 | 别名 | 说明 | 默认值 | 示例 |
| :--- | :--- | :--- | :--- | :--- |
| `-kernels-used=<name>` | 无 | 声明被引用的 kernel 名称；未列出的 kernel 可能在优化中被移除。可多次指定以声明多个 kernel | 无 | `-kernels-used=my_kernel` |
| `-variables-used=<name>` | 无 | 声明被引用的设备变量名称；未列出的变量可能在优化中被移除。可多次指定以声明多个变量 | 无 | `-variables-used=my_var` |
| `-optimize-unused-variables` | 无 | 启用后，若某变量未在设备代码中被引用，则可能被移除。通常设备代码优化会因不确定主机代码的引用情况而保守处理，该选项将解除此限制 | 未启用 | `-optimize-unused-variables` |

### 2.5. 数据类型

#### 2.5.1. hgJitLinkHandle

```cpp
typedef void* hgJitLinkHandle
```

`hgJitLinkHandle` 是 hgJitLink 的不透明句柄（opaque handle），表示一个正在被链接的目标程序。使用前须通过 `hgJitLinkCreate()` 创建；使用完毕后须通过 `hgJitLinkDestroy()` 释放，不可遗漏。

典型生命周期：通过 `hgJitLinkCreate` 创建 → 通过 `hgJitLinkAddData` / `hgJitLinkAddFile` 添加输入 → 调用 `hgJitLinkComplete` 执行链接 → 通过 `hgJitLinkGetLinkedHgbin` 等接口提取结果 → 调用 `hgJitLinkDestroy` 释放资源。

#### 2.5.2. hgJitLinkResult 错误码

`hgJitLinkResult` 枚举定义了所有 API 函数的返回状态，调用方应在每次 API 调用后检查该值以确认操作是否成功。

```cpp
typedef enum hgJitLinkResult {
  HGJITLINK_SUCCESS = 0,
  HGJITLINK_ERROR_UNRECOGNIZED_OPTION = 1,
  HGJITLINK_ERROR_MISSING_ARCH = 2,
  HGJITLINK_ERROR_INVALID_INPUT = 3,
  HGJITLINK_ERROR_TIX_COMPILE = 4,
  HGJITLINK_ERROR_HGVM_COMPILE = 5,
  HGJITLINK_ERROR_INTERNAL = 6,
  HGJITLINK_ERROR_THREADPOOL = 7,
  HGJITLINK_ERROR_UNRECOGNIZED_INPUT = 8,
  HGJITLINK_ERROR_NULL_INPUT = 9,
  HGJITLINK_ERROR_INCOMPATIBLE_OPTIONS = 10,
  HGJITLINK_ERROR_INCORRECT_INPUT_TYPE = 11,
  HGJITLINK_ERROR_ARCH_MISMATCH = 12,
  HGJITLINK_ERROR_OUTDATED_LIBRARY = 13,
  HGJITLINK_ERROR_MISSING_FATBIN = 14
} hgJitLinkResult;
```

以下按错误类别对各枚举值进行分组说明。

##### 2.5.2.1. 成功状态

| 枚举值 | 数值 | 触发场景 |
| :--- | :--- | :--- |
| `HGJITLINK_SUCCESS` | 0 | API 调用正常完成，无异常 |

##### 2.5.2.2. 输入与参数错误

| 枚举值 | 数值 | 触发场景 |
| :--- | :--- | :--- |
| `HGJITLINK_ERROR_UNRECOGNIZED_OPTION` | 1 | 传入了 hgJitLink 不支持的选项字符串 |
| `HGJITLINK_ERROR_MISSING_ARCH` | 2 | 调用 `hgJitLinkCreate` 时未通过 `-arch` 指定目标 PPU 架构 |
| `HGJITLINK_ERROR_INVALID_INPUT` | 3 | 传入的数据内容、文件路径或参数值不合法 |
| `HGJITLINK_ERROR_UNRECOGNIZED_INPUT` | 8 | 输入数据的二进制格式无法被识别 |
| `HGJITLINK_ERROR_NULL_INPUT` | 9 | 必要参数为空指针 |
| `HGJITLINK_ERROR_INCOMPATIBLE_OPTIONS` | 10 | 同时指定了互相冲突的选项组合 |
| `HGJITLINK_ERROR_INCORRECT_INPUT_TYPE` | 11 | `inputType` 参数声明的格式与实际数据内容不一致 |
| `HGJITLINK_ERROR_ARCH_MISMATCH` | 12 | 输入中的设备代码所针对的架构与 `-arch` 指定的目标架构不一致 |
| `HGJITLINK_ERROR_MISSING_FATBIN` | 14 | 链接过程所需的 fatbin 数据未包含在输入中 |

##### 2.5.2.3. 编译错误

| 枚举值 | 数值 | 触发场景 |
| :--- | :--- | :--- |
| `HGJITLINK_ERROR_TIX_COMPILE` | 4 | 在处理 TIX 格式输入时编译阶段发生错误 |
| `HGJITLINK_ERROR_HGVM_COMPILE` | 5 | HGVM（HG Virtual Machine）编译期间出现错误 |

##### 2.5.2.4. 运行时与内部错误

| 枚举值 | 数值 | 触发场景 |
| :--- | :--- | :--- |
| `HGJITLINK_ERROR_INTERNAL` | 6 | 库内部发生预期外的异常 |
| `HGJITLINK_ERROR_THREADPOOL` | 7 | 内部线程池相关问题 |
| `HGJITLINK_ERROR_OUTDATED_LIBRARY` | 13 | 当前库版本过低 |

#### 2.5.3. hgJitLinkInputType 输入类型

`hgJitLinkInputType` 枚举列出了可传递给 `hgJitLinkAddData` 和 `hgJitLinkAddFile` 的所有输入格式标识。

```cpp
typedef enum hgJitLinkInputType {
  HGJITLINK_INPUT_NONE = 0,
  HGJITLINK_INPUT_HGBIN = 1,
  HGJITLINK_INPUT_TIX = 2,
  HGJITLINK_INPUT_LTOIR = 3,
  HGJITLINK_INPUT_FATBIN = 4,
  HGJITLINK_INPUT_OBJECT = 5,
  HGJITLINK_INPUT_LIBRARY = 6,
  HGJITLINK_INPUT_ANY = 10
} hgJitLinkInputType;
```

| 枚举值 | 数值 | 适用场景 |
| :--- | :--- | :--- |
| `HGJITLINK_INPUT_NONE` | 0 | 无效类型标识，不对应任何有效的输入格式 |
| `HGJITLINK_INPUT_HGBIN` | 1 | 已编译的 HGGC 设备二进制（hgbin） |
| `HGJITLINK_INPUT_TIX` | 2 | HGGC TIX 格式的设备代码 |
| `HGJITLINK_INPUT_LTOIR` | 3 | LTO 中间表示（LTO IR） |
| `HGJITLINK_INPUT_FATBIN` | 4 | fatbin 格式 |
| `HGJITLINK_INPUT_OBJECT` | 5 | 未链接的主机目标文件（host object） |
| `HGJITLINK_INPUT_LIBRARY` | 6 | 主机库（host library） |
| `HGJITLINK_INPUT_ANY` | 10 | 在有效类型中动态选择实际格式 |

比赛关联：HGRTC + hgJitLink 组合是"自定义算子"路线的完整工具链——HGRTC 的 `-dlto` 产物可直接喂给 hgJitLink 做跨模块链接时优化（LTO），`-kernels-used`/`-variables-used` 还能裁剪未引用代码减小二进制体积，适合将自写融合 kernel（如量化 GEMM、KV-cache 管理）以最小开销注入推理流水线。
