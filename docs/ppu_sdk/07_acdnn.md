# T-Head SAIL acDNN <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [1. 概述 {#1-概述}](#1-概述-1-概述)
  - [1.1. 库架构与模块关系 {#11-库架构与模块关系}](#11-库架构与模块关系-11-库架构与模块关系)
  - [1.2. 快速入门 {#12-快速入门}](#12-快速入门-12-快速入门)
- [2. 基础运算 {#2-基础运算}](#2-基础运算-2-基础运算)
  - [2.1. 数据类型与描述符 {#21-数据类型与描述符}](#21-数据类型与描述符-21-数据类型与描述符)
  - [2.2. 推理 API {#22-推理-api}](#22-推理-api-22-推理-api)
  - [2.3. 训练 API {#23-训练-api}](#23-训练-api-23-训练-api)
- [3. 卷积网络 {#3-卷积网络}](#3-卷积网络-3-卷积网络)
  - [3.1. 数据类型与算法枚举 {#31-数据类型与算法枚举}](#31-数据类型与算法枚举-31-数据类型与算法枚举)
  - [3.2. 训练数据类型 {#32-训练数据类型}](#32-训练数据类型-32-训练数据类型)
  - [3.3. 训练 API {#33-训练-api}](#33-训练-api-33-训练-api)
- [4. 高级网络结构 {#4-高级网络结构}](#4-高级网络结构-4-高级网络结构)
  - [4.1. 推理数据类型与描述符 {#41-推理数据类型与描述符}](#41-推理数据类型与描述符-41-推理数据类型与描述符)
  - [4.2. 推理 API {#42-推理-api}](#42-推理-api-42-推理-api)
  - [4.3. 训练数据类型 {#43-训练数据类型}](#43-训练数据类型-43-训练数据类型)
  - [4.4. 训练 API {#44-训练-api}](#44-训练-api-44-训练-api)
- [5. Graph API {#5-graph-api}](#5-graph-api-5-graph-api)
  - [5.1. 数据类型 {#51-数据类型}](#51-数据类型-51-数据类型)
  - [5.2. API 函数 {#52-api-函数}](#52-api-函数-52-api-函数)
  - [5.3. 描述符类型 {#53-描述符类型}](#53-描述符类型-53-描述符类型)
  - [5.4. 用例 {#54-用例}](#54-用例-54-用例)
- [6. 类型与枚举速查 {#6-类型与枚举速查}](#6-类型与枚举速查-6-类型与枚举速查)


## 1. 概述 {#1-概述}

T-Head SAIL acDNN（以下简称 acDNN）库用户指南。acDNN 库是一套基于上下文的 API，提供多线程编程支持及与 HGGC Stream 的互操作性，涵盖 Batch Normalization、Softmax、Dropout、CNN、RNN、CTC Loss、Multi-Head Attention 等常见机器学习算子的推理与训练功能。

### 1.1. 库架构与模块关系 {#11-库架构与模块关系}

acDNN 按**功能域** 组织为以下模块，每个模块既包含推理路径也包含对应的训练路径：

| 功能域 | 覆盖算子 | 对应子库 |
| :--- | :--- | :--- |
| **基础运算** | 上下文管理、张量描述符、Batch Normalization、Softmax、Dropout 等 | `acdnn_ops_infer` + `acdnn_ops_train` |
| **卷积网络** | 卷积、池化、归一化、激活融合等 CNN 算子 | `acdnn_cnn_infer` + `acdnn_cnn_train` |
| **高级网络结构** | RNN、Multi-Head Attention、CTC Loss 等 | `acdnn_adv_infer` + `acdnn_adv_train` |
| **Graph API** | 后端描述符体系：统一描述算子实现、属性键、合法值 | `acdnnBackend` |
| **适配层** | 运行时按需为 API 动态加载对应 `.so` | `acdnn` |

> 本手册按功能域组织：每章同时包含推理与训练 API，无需在多个章节之间跳转。

### 1.2. 快速入门 {#12-快速入门}

最小使用流程：

```c
#include <acdnn.h>

// 1. 创建句柄
acdnnHandle_t handle;
acdnnCreate(&handle);

// 2. 创建张量描述符
acdnnTensorDescriptor_t desc;
acdnnCreateTensorDescriptor(&desc);
acdnnSetTensor4dDescriptor(desc, ACDNN_TENSOR_NCHW, ACDNN_DATA_FLOAT, 1, 3, 224, 224);

// 3. 调用算子（示例：softmax Forward）
float alpha = 1.0f, beta = 0.0f;
acdnnSoftmaxForward(handle, ACDNN_SOFTMAX_ACCURATE, ACDNN_SOFTMAX_MODE_CHANNEL,
                    &alpha, desc, x, &beta, desc, y);

// 4. 清理
acdnnDestroyTensorDescriptor(desc);
acdnnDestroy(handle);
```

## 2. 基础运算 {#2-基础运算}

本章覆盖 acDNN 的上下文管理、张量描述符以及 Batch Normalization / Softmax / Dropout 等基础算子，同时包含推理与训练两个方向的 API。

### 2.1. 数据类型与描述符 {#21-数据类型与描述符}

按用途，本节涉及的数据类型分为两组：2.1.1 列出 12 个描述符指针（即「需要先 create、再 set、用完 destroy」的对象），2.1.2 列出 21 个枚举类型。

#### 2.1.1. 不透明结构体指针类型 {#211-不透明结构体指针类型}

acDNN 中所有「描述符（descriptor）」类型都是**opaque struct 的指针**，库内部维护具体字段，调用方只通过约定的 `Create / Set / Get / Destroy` 例程操作。下表汇总本节涉及的 12 个描述符指针，及其完整生命周期；指针本身的语义在表后逐一展开。

| 描述符指针类型 | 用途 | Create | Set / 初始化 | Destroy |
| :--- | :--- | :--- | :--- | :--- |
| `acdnnActivationDescriptor_t` | 激活函数（activation）描述 | `acdnnCreateActivationDescriptor()` | `acdnnSetActivationDescriptor()` | `acdnnDestroyActivationDescriptor()` |
| `acdnnCTCLossDescriptor_t` | CTC Loss 描述 | `acdnnCreateCTCLossDescriptor()` | `acdnnSetCTCLossDescriptor()` | `acdnnDestroyCTCLossDescriptor()` |
| `acdnnDropoutDescriptor_t` | Dropout 描述（含 RNG state） | `acdnnCreateDropoutDescriptor()` | `acdnnSetDropoutDescriptor()` | `acdnnDestroyDropoutDescriptor()` |
| `acdnnFilterDescriptor_t` | 滤波器数据集描述 | `acdnnCreateFilterDescriptor()` | `acdnnSetFilter4dDescriptor()` / `acdnnSetFilterNdDescriptor()` | `acdnnDestroyFilterDescriptor()` |
| `acdnnHandle_t` | acDNN 库上下文（绑定真武 PPU 设备） | `acdnnCreate()` | — | `acdnnDestroy()` |
| `acdnnLRNDescriptor_t` | 局部响应归一化（LRN，Local Response Normalization）参数 | `acdnnCreateLRNDescriptor()` | `acdnnSetLRNDescriptor()` | `acdnnDestroyLRNDescriptor()` |
| `acdnnOpTensorDescriptor_t` | 张量逐点运算（add/mul/min/…）描述 | `acdnnCreateOpTensorDescriptor()` | `acdnnSetOpTensorDescriptor()` | `acdnnDestroyOpTensorDescriptor()` |
| `acdnnPoolingDescriptor_t` | 池化操作描述 | `acdnnCreatePoolingDescriptor()` | `acdnnSetPoolingNdDescriptor()` / `acdnnSetPooling2dDescriptor()` | `acdnnDestroyPoolingDescriptor()` |
| `acdnnReduceTensorDescriptor_t` | 张量归约描述 | `acdnnCreateReduceTensorDescriptor()` | `acdnnSetReduceTensorDescriptor()` | `acdnnDestroyReduceTensorDescriptor()` |
| `acdnnSpatialTransformerDescriptor_t` | 空间变换网络（STN）描述 | `acdnnCreateSpatialTransformerDescriptor()` | `acdnnSetSpatialTransformerNdDescriptor()` | `acdnnDestroySpatialTransformerDescriptor()` |
| `acdnnTensorDescriptor_t` | 通用 n 维张量描述 | `acdnnCreateTensorDescriptor()` | `acdnnSetTensorNdDescriptor()` / `acdnnSetTensor4dDescriptor()` / `acdnnSetTensor4dDescriptorEx()` | `acdnnDestroyTensorDescriptor()` |
| `acdnnTensorTransformDescriptor_t` | 张量布局变换描述 | `acdnnCreateTensorTransformDescriptor()` | `acdnnSetTensorTransformDescriptor()` | `acdnnDestroyTensorTransformDescriptor()` |

以下为各类型的补充说明（仅在和上表外信息有关时给出）：

##### 2.1.1.1. acdnnActivationDescriptor_t {#2111-acdnnactivationdescriptor_t}

承载一次激活操作的全部参数：函数类型（Sigmoid / ReLU / Tanh / Clipped ReLU / ELU / Identity / Swish）、上限阈值、NaN 传播策略等。

##### 2.1.1.2. acdnnCTCLossDescriptor_t {#2112-acdnnctclossdescriptor_t}

CTC Loss 操作所需的运行时参数容器，与下游 `acdnnCTCLoss()` 配合使用。

##### 2.1.1.3. acdnnDropoutDescriptor_t {#2113-acdnndropoutdescriptor_t}

不仅描述 dropout 比例，还内嵌随机数发生器状态。除标准生命周期外还提供两条额外接口： `acdnnGetDropoutDescriptor()` 查询已初始化字段， `acdnnRestoreDropoutDescriptor()` 用于把描述符恢复到先前保存的状态。

##### 2.1.1.4. acdnnFilterDescriptor_t {#2114-acdnnfilterdescriptor_t}

描述滤波器数据集的形状、数据类型与布局；4D 与 N-D 两套初始化接口对应不同维数。

##### 2.1.1.5. acdnnHandle_t {#2115-acdnnhandle_t}

acDNN 库上下文的不透明指针，是几乎所有 API 的第一个参数。**生命周期约束** ：

- 与**单个真武 PPU 设备** 绑定（`acdnnCreate()` 调用时刻的当前设备）；
- 同一设备上**允许并存** 多个句柄，可分别绑定不同的 Stream 或数学模式；
- 切换设备前要先 `hggcSetDevice()`，再创建新的句柄。

##### 2.1.1.6. acdnnLRNDescriptor_t {#2116-acdnnlrndescriptor_t}

承载局部响应归一化（Local Response Normalization）的参数：邻域窗口长度、α、β、k 等。

##### 2.1.1.7. acdnnOpTensorDescriptor_t {#2117-acdnnoptensordescriptor_t}

`acdnnOpTensor()` 的运算配置，选择具体的逐点运算（add / mul / min / max / sqrt / not）、数据类型与 NaN 传播。

##### 2.1.1.8. acdnnPoolingDescriptor_t {#2118-acdnnpoolingdescriptor_t}

池化算子的窗口尺寸、步长、填充、模式等。 `acdnnSetPooling2dDescriptor()` 适用于 4D 张量； `acdnnSetPoolingNdDescriptor()` 用于一般情形。

##### 2.1.1.9. acdnnReduceTensorDescriptor_t {#2119-acdnnreducetensordescriptor_t}

`acdnnReduceTensor()` 的归约配置：归约函数、是否计算 indices、indices 的数据类型等。

##### 2.1.1.10. acdnnSpatialTransformerDescriptor_t {#21110-acdnnspatialtransformerdescriptor_t}

空间变换网络（spatial transformer）的目标输出形状、采样器类型等。

##### 2.1.1.11. acdnnTensorDescriptor_t {#21111-acdnntensordescriptor_t}

最常用的描述符，描述任意 n 维张量。库内部按需做尺寸/步幅推导；用 4D / 4DEx / N-D 三套初始化接口覆盖不同入参形态。

##### 2.1.1.12. acdnnTensorTransformDescriptor_t {#21112-acdnntensortransformdescriptor_t}

描述一次张量布局变换：源/目标填充、folding 方向、目标布局等，配合 `acdnnTransformTensor()` 等使用。

#### 2.1.2. 枚举类型 {#212-枚举类型}

以下为 acdnn_ops_infer.so 库中的枚举类型。

##### 2.1.2.1. acdnnActivationMode_t {#2121-acdnnactivationmode_t}

`acdnnActivationMode_t` 是用于选择激活函数类型的枚举类型，适用于 `acdnnActivationForward()`、`acdnnActivationBackward()` 和 `acdnnConvolutionBiasActivationForward()`。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_ACTIVATION_SIGMOID`| 选择 S 形函数（Sigmoid）。 |
| `ACDNN_ACTIVATION_RELU`| 选择修正线性单元函数（ReLU）。 |
| `ACDNN_ACTIVATION_TANH`| 选择双曲正切函数（Tanh）。 |
| `ACDNN_ACTIVATION_CLIPPED_RELU`| 选择带上限的修正线性单元函数（Clipped ReLU）。 |
| `ACDNN_ACTIVATION_ELU`| 选择指数线性单元函数（ELU）。 |
| `ACDNN_ACTIVATION_IDENTITY`| 选择恒等函数（Identity），用于 `acdnnConvolutionBiasActivationForward()` 中跳过激活步骤，此时卷积算法须为 `ACDNN_CONVOLUTION_FWD_ALGO_IMPLICIT_PRECOMP_GEMM`，不适用于 `acdnnActivationForward()` 或 `acdnnActivationBackward()`。 |
| `ACDNN_ACTIVATION_GELU`| 选择高斯误差线性单元函数（GELU）。 |
| `ACDNN_ACTIVATION_PRELU`| 选择参数化修正线性单元函数（PReLU）。 |
| `ACDNN_ACTIVATION_LEAKYRELU`| 选择带泄漏的修正线性单元函数（Leaky ReLU）。 |

##### 2.1.2.2. acdnnBatchNormMode_t {#2122-acdnnbatchnormmode_t}

`acdnnBatchNormMode_t` 是用于指定 `acdnnBatchNormalizationForwardInference()`、`acdnnBatchNormalizationForwardTraining()`、`acdnnBatchNormalizationBackward()` 和 `acdnnDeriveBNTensorDescriptor()` 函数中操作模式的枚举类型。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_BATCHNORM_SPATIAL`| 对 N 个或更多空间维度（spatial dimensions）执行归一化，此模式适用于卷积层之后（需要空间不变性时）。在此模式下，bnBias 和 bnScale 的张量维度为 1 × C × 1 × 1。 |
| `ACDNN_BATCHNORM_SPATIAL_PERSISTENT`| 与 `ACDNN_BATCHNORM_SPATIAL` 功能相同，但在部分场景下性能更优。<br>对于 `ACDNN_DATA_FLOAT` 和 `ACDNN_DATA_HALF` 类型， `acdnnBatchNormalizationForwardTraining()` 和 `acdnnBatchNormalizationBackward()` 可能选择优化路径。使用 `acdnnBatchNormalizationBackward()` 时， `savedMean` 和 `savedInvVariance` 参数不可为 NULL。<br>对于 `NCHW`（Batch×Channel×Height×Width）数据格式，此模式可能使用缩放原子整数归约，计算结果是确定性的，但对输入数据范围有更严格的限制。<br>**注意** ：当输入值有限但非常大时，由于动态范围较低，可能比 `ACDNN_BATCHNORM_SPATIAL` 更频繁地产生 NaN/Inf 溢出。当输入数据本身包含 Inf/NaN 时，输出与纯浮点实现一致。 |

##### 2.1.2.3. acdnnBatchNormOps_t {#2123-acdnnbatchnormops_t}

`acdnnBatchNormOps_t` 是用于指定 `acdnnGetBatchNormalizationForwardTrainingExWorkspaceSize()`、`acdnnBatchNormalizationForwardTrainingEx()`、`acdnnGetBatchNormalizationBackwardExWorkspaceSize()`、`acdnnBatchNormalizationBackwardEx()` 和 `acdnnGetBatchNormalizationTrainingExReserveSpaceSize()` 函数中操作模式的枚举类型。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_BATCHNORM_OPS_BN`| 仅执行批量归一化（Batch Normalization），按逐激活单元（per-activation）模式处理。 |
| `ACDNN_BATCHNORM_OPS_BN_ACTIVATION`| 先执行批量归一化（Batch Normalization），再执行激活（Activation）。 |
| `ACDNN_BATCHNORM_OPS_BN_ADD_ACTIVATION`| 依次执行批量归一化（Batch Normalization）、逐元素相加（element-wise addition）和激活（Activation）操作。 |

##### 2.1.2.4. acdnnCTCLossAlgo_t {#2124-acdnnctclossalgo_t}

`acdnnCTCLossAlgo_t` 是一个枚举类型，列出了执行 CTC（Connectionist Temporal Classification）Loss 操作时可用的不同算法。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_CTC_LOSS_ALGO_DETERMINISTIC`| 结果保证可重现（deterministic）。 |
| `ACDNN_CTC_LOSS_ALGO_NON_DETERMINISTIC`| 结果不保证可重现。 |

##### 2.1.2.5. acdnnDataType_t {#2125-acdnndatatype_t}

`acdnnDataType_t` 是指示张量描述符或滤波器描述符所引用数据类型的枚举类型。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_DATA_FLOAT`| 数据为 32 位单精度浮点数（float）。 |
| `ACDNN_DATA_DOUBLE`| 数据为 64 位双精度浮点数（double）。 |
| `ACDNN_DATA_HALF`| 数据为 16 位半精度浮点数（half）。 |
| `ACDNN_DATA_INT8`| 数据为 8 位有符号整数。 |
| `ACDNN_DATA_INT32`| 数据为 32 位有符号整数。 |
| `ACDNN_DATA_INT8x4`| 数据为 32 位元素，每个元素由 4 个 8 位有符号整数组成。此数据类型仅支持张量格式 `ACDNN_TENSOR_NCHW_VECT_C`。 |
| `ACDNN_DATA_UINT8`| 数据为 8 位无符号整数。 |
| `ACDNN_DATA_UINT8x4`| 数据为 32 位元素，每个元素由 4 个 8 位无符号整数组成。此数据类型仅支持张量格式 `ACDNN_TENSOR_NCHW_VECT_C`。 |
| `ACDNN_DATA_INT8x32`| 数据为 32 元素向量，每个元素为 8 位有符号整数。此数据类型仅支持张量格式 `ACDNN_TENSOR_NCHW_VECT_C`。此外，此数据类型仅支持与算法 1（即 `ACDNN_CONVOLUTION_FWD_ALGO_IMPLICIT_PRECOMP_GEMM`）配合使用。更多信息请参阅 `acdnnConvolutionFwdAlgo_t`。 |
| `ACDNN_DATA_INT16`| 数据为 16 位有符号整数。 |
| `ACDNN_DATA_BF16`| 数据为 16 位格式，包含 7 位尾数（mantissa）、8 位指数（exponent）和 1 位符号位（sign）。 |
| `ACDNN_DATA_TF32`| 数据为 TensorFloat-32 格式，包含 10 位尾数、8 位指数和 1 位符号位。 |
| `ACDNN_DATA_INT64`| 数据为 64 位有符号整数。 |
| `ACDNN_DATA_BOOL`| 数据为布尔值（bool）。**注意** ：对于 `ACDNN_DATA_BOOL` 类型，元素采用"打包"（packed）格式：即一个字节包含 8 个 `ACDNN_DATA_BOOL` 类型的元素。在每个字节内，元素从最低有效位（LSB，Least Significant Bit）到最高有效位（MSB，Most Significant Bit）索引。例如，包含二进制 01001111 的 8 元素一维张量，元素 0 到 3 的值为 1，元素 4 和 5 的值为 0，元素 6 的值为 1，元素 7 的值为 0。超过 8 个元素的张量将使用更多字节，顺序同样从最低有效字节到最高有效字节，此外，HGGC 采用小端序（little-endian），即最低有效字节的内存地址较低。例如，对于 16 个元素 01001111 11111100，元素 0 到 3 的值为 1，元素 4 和 5 的值为 0，元素 6 的值为 1，元素 7 的值为 0，元素 8 和 9 的值为 0，元素 10 到 15 的值为 1。 |

##### 2.1.2.6. acdnnDeterminism_t {#2126-acdnndeterminism_t}

`acdnnDeterminism_t` 是用于指示计算结果是否具有确定性（deterministic，即可重现）的枚举类型。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_NON_DETERMINISTIC`| 结果不保证可重现。 |
| `ACDNN_DETERMINISTIC`| 结果保证可重现。 |

##### 2.1.2.7. acdnnFoldingDirection_t {#2127-acdnnfoldingdirection_t}

`acdnnFoldingDirection_t` 是用于选择折叠（folding）方向的枚举类型。更多信息请参阅 `acdnnTensorTransformDescriptor_t`。
**数据成员**

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_TRANSFORM_FOLD` = 0U | 选择折叠（fold）。 |
| `ACDNN_TRANSFORM_UNFOLD` = 1U | 选择展开（unfold）。 |

##### 2.1.2.8. acdnnIndicesType_t {#2128-acdnnindicestype_t}

`acdnnIndicesType_t` 是用于指示 `acdnnReduceTensor()` 函数计算的索引（indices）数据类型的枚举类型，此枚举类型用作 `acdnnReduceTensorDescriptor_t` 描述符的字段。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_32BIT_INDICES`| 计算 unsigned int 类型索引。 |
| `ACDNN_64BIT_INDICES`| 计算 unsigned long 类型索引。 |
| `ACDNN_16BIT_INDICES`| 计算 unsigned short 类型索引。 |
| `ACDNN_8BIT_INDICES`| 计算 unsigned char 类型索引。 |

##### 2.1.2.9. acdnnLRNMode_t {#2129-acdnnlrnmode_t}

`acdnnLRNMode_t` 是用于指定 `acdnnLRNCrossChannelForward()` 和 `acdnnLRNCrossChannelBackward()` 中操作模式的枚举类型。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_LRN_CROSS_CHANNEL_DIM1`| LRN 计算跨张量的维度 dimA[1] 执行。 |

##### 2.1.2.10. acdnnMathType_t {#21210-acdnnmathtype_t}

`acdnnMathType_t` 是用于指示在给定库函数中是否允许使用 Tensor 操作的枚举类型。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_DEFAULT_MATH`| 允许 Tensor 单元 TF32 操作。 |
| `ACDNN_TENSOR_OP_MATH`| 允许使用 Tensor 单元操作，但不会主动对张量进行数据类型降级（downcast）以利用 Tensor 单元。 |
| `ACDNN_TENSOR_OP_MATH_ALLOW_CONVERSION`| 允许使用 Tensor 单元操作，并将主动对张量进行数据类型降级以利用 Tensor 单元。 |
| `ACDNN_FMA_MATH`| 仅限于使用 FMA（Fused Multiply-Add）指令的 Kernel。 |
| `ACDNN_SPTENSOR_OP_MATH`| 允许使用稀疏 Tensor 单元操作（Sparse Tensor Op）。 |

##### 2.1.2.11. acdnnNanPropagation_t {#21211-acdnnnanpropagation_t}

`acdnnNanPropagation_t` 是用于指示给定函数是否应传播 NaN（Not-a-Number）值的枚举类型，此枚举类型用作 `acdnnActivationDescriptor_t` 描述符和 `acdnnPoolingDescriptor_t` 描述符的字段。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_NOT_PROPAGATE_NAN`| 不传播 NaN 值。 |
| `ACDNN_PROPAGATE_NAN`| 传播 NaN 值。 |

##### 2.1.2.12. acdnnOpTensorOp_t {#21212-acdnnoptensorop_t}

`acdnnOpTensorOp_t` 是用于指示 `acdnnOpTensor()` 函数使用的张量操作（Tensor 操作）类型的枚举类型，此枚举类型用作 `acdnnOpTensorDescriptor_t` 描述符的字段。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_OP_TENSOR_ADD`| 执行加法操作。 |
| `ACDNN_OP_TENSOR_MUL`| 执行乘法操作。 |
| `ACDNN_OP_TENSOR_MIN`| 执行最小值比较操作。 |
| `ACDNN_OP_TENSOR_MAX`| 执行最大值比较操作。 |
| `ACDNN_OP_TENSOR_SQRT`| 执行平方根操作，仅对张量 A 执行。 |
| `ACDNN_OP_TENSOR_NOT`| 执行取反操作，仅对张量 A 执行。 |

##### 2.1.2.13. acdnnPoolingMode_t {#21213-acdnnpoolingmode_t}

`acdnnPoolingMode_t` 是传递给 `acdnnSetPooling2dDescriptor()` 以选择 `acdnnPoolingForward()` 和 `acdnnPoolingBackward()` 使用的池化方法的枚举类型。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_POOLING_MAX`| 使用池化窗口内的最大值（Max 池化）。 |
| `ACDNN_POOLING_AVERAGE_COUNT_INCLUDE_PADDING`| 对池化窗口内的值求平均（Average 池化）。用于计算平均值的元素数量包括落在填充区域的空间位置。 |
| `ACDNN_POOLING_AVERAGE_COUNT_EXCLUDE_PADDING`| 对池化窗口内的值求平均。用于计算平均值的元素数量不包括落在填充区域的空间位置。 |
| `ACDNN_POOLING_MAX_DETERMINISTIC`| 使用池化窗口内的最大值。使用的算法是确定性的（deterministic）。 |
| `ACDNN_POOLING_ADAPTIVE_MAX`| 自适应最大池化（Adaptive Max Pooling），根据输出尺寸自动确定池化窗口大小。 |
| `ACDNN_POOLING_AVG`| 平均池化，与 `ACDNN_POOLING_AVERAGE_COUNT_INCLUDE_PADDING` 等效。 |
| `ACDNN_POOLING_ADAPTIVE_AVG`| 自适应平均池化（Adaptive Average Pooling），根据输出尺寸自动确定池化窗口大小。 |

##### 2.1.2.14. acdnnReduceTensorIndices_t {#21214-acdnnreducetensorindices_t}

`acdnnReduceTensorIndices_t` 是用于指示是否由 `acdnnReduceTensor()` 函数计算索引（indices）的枚举类型，此枚举类型用作 `acdnnReduceTensorDescriptor_t` 描述符的字段。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_REDUCE_TENSOR_NO_INDICES`| 不计算索引。 |
| `ACDNN_REDUCE_TENSOR_FLATTENED_INDICES`| 计算索引。生成的索引是相对索引且已展平（flattened）。 |

##### 2.1.2.15. acdnnReduceTensorOp_t {#21215-acdnnreducetensorop_t}

`acdnnReduceTensorOp_t` 是用于指示 `acdnnReduceTensor()` 函数使用的归约操作类型的枚举类型，此枚举类型用作 `acdnnReduceTensorDescriptor_t` 描述符的字段。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_REDUCE_TENSOR_ADD`| 执行加法归约。 |
| `ACDNN_REDUCE_TENSOR_MUL`| 执行乘法归约。 |
| `ACDNN_REDUCE_TENSOR_MIN`| 执行最小值归约。 |
| `ACDNN_REDUCE_TENSOR_MAX`| 执行最大值归约。 |
| `ACDNN_REDUCE_TENSOR_AMAX`| 执行绝对值最大值归约。 |
| `ACDNN_REDUCE_TENSOR_AVG`| 执行平均值归约。 |
| `ACDNN_REDUCE_TENSOR_NORM1`| 执行 L1 范数归约（绝对值之和）。 |
| `ACDNN_REDUCE_TENSOR_NORM2`| 执行 L2 范数归约（平方和的平方根）。 |

##### 2.1.2.16. acdnnRNNAlgo_t {#21216-acdnnrnnalgo_t}

`acdnnRNNAlgo_t` 是用于指定 `acdnnRNNForwardInference()`、`acdnnRNNForwardTraining()`、`acdnnRNNBackwardData()` 和 `acdnnRNNBackwardWeights()` 函数中使用的算法的枚举类型。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_RNN_ALGO_STANDARD`| 每个 RNN 层作为一系列操作序列执行。该算法预期在广泛的网络参数范围内具有稳健的性能表现。 |

##### 2.1.2.17. acdnnSamplerType_t {#21217-acdnnsamplertype_t}

`acdnnSamplerType_t` 是传递给 `acdnnSetSpatialTransformerNdDescriptor()` 以选择 `acdnnSpatialTfSamplerForward()` 和 `acdnnSpatialTfSamplerBackward()` 使用的采样器（Sampler）类型的枚举类型。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_SAMPLER_BILINEAR`| 选择双线性采样器（Bilinear Sampler）。 |

##### 2.1.2.18. acdnnSoftmaxAlgorithm_t {#21218-acdnnsoftmaxalgorithm_t}

`acdnnSoftmaxAlgorithm_t` 用于选择 `acdnnSoftmaxForward()` 和 `acdnnSoftmaxBackward()` 中使用的归一化指数（Softmax）函数实现方式。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_SOFTMAX_ACCURATE`| 此实现通过将 Softmax 输入域的每个点按其最大值进行缩放，以避免 Softmax 计算中潜在的浮点数溢出。 |
| `ACDNN_SOFTMAX_LOG`| 此实现执行 Log Softmax 运算，通过如 `ACDNN_SOFTMAX_ACCURATE` 中所述缩放输入域中的每个点来避免溢出。 |

##### 2.1.2.19. acdnnSoftmaxMode_t {#21219-acdnnsoftmaxmode_t}

`acdnnSoftmaxMode_t` 用于指定 `acdnnSoftmaxForward()` 和 `acdnnSoftmaxBackward()` 在哪些数据维度上计算其结果。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_SOFTMAX_MODE_INSTANCE`| Softmax 操作按样本（N）跨维度 C、H、W 计算。 |
| `ACDNN_SOFTMAX_MODE_CHANNEL`| Softmax 操作按每个样本（N）的每个空间位置（H、W）跨维度 C 计算。 |

##### 2.1.2.20. acdnnStatus_t {#21220-acdnnstatus_t}

`acdnnStatus_t` 是用于函数状态返回的枚举类型。所有 acDNN 库函数返回其执行状态，可以是以下值之一：

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_STATUS_SUCCESS`| 操作成功完成。 |
| `ACDNN_STATUS_NOT_INITIALIZED`| acDNN 库未正确初始化。此错误通常在调用 `acdnnCreate()` 失败时，或在调用其他 acDNN 函数之前未调用 `acdnnCreate()` 时返回。在前一种情况下，通常是由于 `acdnnCreate()` 调用中的 HGGC Runtime API 错误或硬件配置问题。 |
| `ACDNN_STATUS_ALLOC_FAILED`| acDNN 库内部资源分配失败。这通常由内部 hggcMalloc() 调用失败引起。解决方法：在函数调用前，尽可能释放先前分配的内存。 |
| `ACDNN_STATUS_BAD_PARAM`| 向函数传递了无效的值或参数。解决方法：确保所有传递的参数均具有有效值。 |
| `ACDNN_STATUS_ARCH_MISMATCH`| 当前真武 PPU 架构不受支持。 |
| `ACDNN_STATUS_MAPPING_ERROR`| 访问真武 PPU 内存空间失败，通常由纹理（Texture）绑定失败引起。解决方法：在函数调用前，解绑任何先前绑定的 Texture。否则，这可能表示库内部存在错误或缺陷。 |
| `ACDNN_STATUS_INTERNAL_ERROR`| acDNN 内部操作失败。 |
| `ACDNN_STATUS_INVALID_VALUE`| 提供了无效的指针或参数。 |
| `ACDNN_STATUS_EXECUTION_FAILED`| 在真武 PPU 上启动函数 / kernel 失败。 |
| `ACDNN_STATUS_NOT_SUPPORTED`| acDNN 当前不支持所请求的功能。 |
| `ACDNN_STATUS_LICENSE_ERROR`| 请求的功能需要特定许可证，在尝试验证当前许可证时检测到错误。如果许可证不存在、已过期，或环境变量 `PTG_LICENSE_FILE` 未正确设置，可能会发生此错误。 |
| `ACDNN_STATUS_RUNTIME_PREREQUISITE_MISSING`| 在预定义的搜索路径中找不到 acDNN 所需的 Runtime 库： `libhggc.so` 和 `libhgrtc.so`。 |
| `ACDNN_STATUS_RUNTIME_IN_PROGRESS`| User Stream 中的部分任务尚未完成。 |
| `ACDNN_STATUS_RUNTIME_FP_OVERFLOW`|真武 PPU Kernel 执行期间发生数值溢出。 |

##### 2.1.2.21. acdnnTensorFormat_t {#21221-acdnntensorformat_t}

`acdnnTensorFormat_t` 是 `acdnnSetTensor4dDescriptor()` 使用的枚举类型，用于创建具有预定义布局的张量。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_TENSOR_NCHW` | 此张量格式指定数据按以下顺序排列：批量大小、Channel（特征图）、Height（行）、Width（列）。步幅以隐式方式定义，使得数据在内存中连续，在 N、C、H、W 维度之间没有填充；W 是最内层维度，N 是最外层维度。 |
| `ACDNN_TENSOR_NHWC` | 此张量格式指定数据按以下顺序排列：批量大小、Height（行）、Width（列）、Channel（特征图）。步幅以隐式方式定义，使得数据在内存中连续，在 N、H、W、C 维度之间没有填充；C 是最内层维度，N 是最外层维度。 |
| `ACDNN_TENSOR_NCHW_VECT_C` | 此张量格式指定数据按以下顺序排列：批量大小、Channel（特征图）、Height（行）、Width（列）。但是，张量的每个元素是多个 Channel 的向量。向量的长度由张量的数据类型决定。步幅以隐式方式定义，使得数据在内存中连续，在 N、C、H、W 维度之间没有填充；W 是最内层维度，N 是最外层维度，此格式仅支持数据类型 `ACDNN_DATA_INT8x4`、`ACDNN_DATA_INT8x32` 和 `ACDNN_DATA_UINT8x4`。 `ACDNN_TENSOR_NCHW_VECT_C` 也可以按以下方式理解： `NCHW` `INT8x32` 格式实际上是 $\mathsf{N} \times (\mathsf{C} / 32) \times \mathsf{H} \times \mathsf{W} \times 32$（每个 W 位置有 32 个 C），就像 `NCHW` `INT8x4` 格式是 $\mathsf{N} \times (\mathsf{C} / 4) \times \mathsf{H} \times \mathsf{W} \times 4$（每个 W 位置有 4 个 C）。因此，VECT_C 名称的含义是：每个 W 位置存储一个 C 的向量（长度为 4 或 32）。 |

### 2.2. 推理 API {#22-推理-api}

`acdnn_ops_infer.so` 提供的所有公开 API。许多算子的输出按 `dst = α·result + β·priorDst` 与目标张量的先前值混合。下文中提到 `alpha` / `beta` 时即此语义，不再每次重述。

#### 2.2.1. acdnnActivationForward() {#221-acdnnactivationforward}

```cpp
acdnnStatus_t acdnnActivationForward(
    acdnnHandle_t handle,
    acdnnActivationDescriptor_t activationDesc,
    const void *alpha,
    const acdnnTensorDescriptor_t xDesc, const void *x,
    const void *beta,
    const acdnnTensorDescriptor_t yDesc, void *y);
```

逐元素地把 `activationDesc` 指定的激活函数施加到 `x`，结果按 `α·activation(x) + β·prevY` 写入 `y`。

**形状与性能要点**

- 支持所有 4D / 5D 张量格式；超过 5D 的张量需要其空间维度已 packing。
- `xDesc` 与 `yDesc` 的步幅一致且 HW 维度 packing 时性能最佳。
- 支持原地（in-place）操作，但要求 `x == y` 时两描述符必须**完全一致** （包括步幅）。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文（`acdnnHandle_t`） |
| `activationDesc` | 输入 | 激活配置（`acdnnActivationDescriptor_t`） |
| `alpha` / `beta` | 输入 | host 端混合系数： `dst = alpha[0]*result + beta[0]*priorDst`。当前版本仅支持 alpha=1, beta=0 |
| `xDesc` / `x` | 输入 | 输入张量描述符 / device 数据指针 |
| `yDesc` / `y` | 输入 / 输出 | 输出张量描述符 / device 数据指针 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：不支持该入参组合。
- `ACDNN_STATUS_BAD_PARAM`：满足以下任一：mode 枚举非法； `x` / `y` 张量的 NCHW 维不一致；数据类型不一致； `x == y` 但步幅不匹配。
- `ACDNN_STATUS_EXECUTION_FAILED`：真武 PPU kernel 启动失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 2.2.2. acdnnAddTensor() {#222-acdnnaddtensor}

```cpp
acdnnStatus_t acdnnAddTensor(
    acdnnHandle_t handle,
    const void *alpha,
    const acdnnTensorDescriptor_t aDesc, const void *A,
    const void *beta,
    const acdnnTensorDescriptor_t cDesc, void *C);
```

把缩放后的 bias 张量 `A` 累加到目标张量 `C` 上： `C ← α·A + β·C`。 `A` 的每一维或与 `C` 对应维相等，或为 1（即沿该维做广播）。

**形状约束** ：仅支持 4D / 5D 张量；不支持其他维数。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `alpha` / `beta` | 输入 | host 端混合系数： `dst = alpha[0]*src + beta[0]*priorDst` |
| `aDesc` / `A` | 输入 | bias 张量的描述符 / device 数据指针 |
| `cDesc` / `C` | 输入 / 输出 | 目标张量的描述符 / device 数据指针 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：入参组合不支持。
- `ACDNN_STATUS_BAD_PARAM`：bias 形状与 `C` 不兼容，或两描述符的 `dataType` 不一致。
- `ACDNN_STATUS_EXECUTION_FAILED`：真武 PPU kernel 启动失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 2.2.3. acdnnBatchNormalizationForwardInference() {#223-acdnnbatchnormalizationforwardinference}

```cpp
acdnnStatus_t acdnnBatchNormalizationForwardInference(
    acdnnHandle_t handle,
    acdnnBatchNormMode_t mode,
    const void *alpha, const void *beta,
    const acdnnTensorDescriptor_t xDesc, const void *x,
    const acdnnTensorDescriptor_t yDesc, void *y,
    const acdnnTensorDescriptor_t bnScaleBiasMeanVarDesc,
    const void *bnScale, const void *bnBias,
    const void *estimatedMean, const void *estimatedVariance,
    double epsilon);
```

推理阶段的批归一化前向算子，源自论文《Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift》。等价计算式：

```text
y = β·y + α · [bnBias + bnScale · (x - estimatedMean) / sqrt(estimatedVariance + epsilon)]
```

> 训练阶段的对偶实现见 `acdnnBatchNormalizationForwardTraining()`； `bnScaleBiasMeanVarDesc` 可借助 `acdnnDeriveBNTensorDescriptor()` 派生。

**形状与性能要点**

- 仅支持 4D / 5D 张量；
- `x` 与 `dx` 都使用 HW packing 张量时性能更佳。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `mode` | 输入 | Spatial 或 Per-Activation（`acdnnBatchNormMode_t`） |
| `alpha` / `beta` | 输入 | host 端混合系数： `dst = alpha[0]*result + beta[0]*priorDst`。当前版本仅支持 alpha=1, beta=0 |
| `xDesc` / `x` | 输入 | 层输入数据的描述符 / device 数据指针 |
| `yDesc` / `y` | 输入 / 输出 | 层输出数据的描述符 / device 数据指针 |
| `bnScaleBiasMeanVarDesc` | 输入 | scale / bias / mean / variance 共用的张量描述符 |
| `bnScale` / `bnBias` | 输入 | BN 的 scale（论文 γ）与 bias（论文 β），device 内存 |
| `estimatedMean` / `estimatedVariance` | 输入 | 训练阶段从 `acdnnBatchNormalizationForwardTraining()` 累积而来的 `resultRunningMean` / `resultRunningVariance` |
| `epsilon` | 输入 | BN 公式中的 ε，需 ≥ `ACDNN_BN_MIN_EPSILON`（在 `acdnn.h` 中定义） |

**支持的数据类型组合**

| 配置代号 | `xDesc` | `bnScaleBiasMeanVar` | `alpha, beta` | `yDesc` |
| :--- | :--- | :--- | :--- | :--- |
| `INT8_CONFIG` | `ACDNN_DATA_INT8` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_INT8` |
| `PSEUDO_HALF_CONFIG` | `ACDNN_DATA_HALF` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_HALF` |
| `FLOAT_CONFIG` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` |
| `DOUBLE_CONFIG` | `ACDNN_DATA_DOUBLE` | `ACDNN_DATA_DOUBLE` | `ACDNN_DATA_DOUBLE` | `ACDNN_DATA_DOUBLE` |
| `BFLOAT16_CONFIG` | `ACDNN_DATA_BF16` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_BF16` |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：不支持该入参组合。
- `ACDNN_STATUS_BAD_PARAM`：满足以下任一： `alpha` / `beta` / `x` / `y` / `bnScale` / `bnBias` / `estimatedMean` / `estimatedVariance` 之一为 NULL；或 `xDesc` / `yDesc` 的维度数不在 [4,5] 范围内（仅支持 4D 和 5D 张量）。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 2.2.4. acdnnCreate() {#224-acdnncreate}

```cpp
acdnnStatus_t acdnnCreate(acdnnHandle_t *handle);
```

初始化 acDNN 库，并通过 `*handle` 把上下文句柄返回给调用方。Host / device 端硬件资源在此分配，**必须先于其他任何 acDNN 例程调用** 。

**生命周期与并发**

- **设备绑定** ：句柄绑定调用时刻的当前 HGGC 设备；多设备应用应在每次切换 `hggcSetDevice()` 之后再 create。
- **同设备多句柄** ：同一设备允许并存多个配置不同的句柄（如不同的 Stream）。
- **create / destroy 频次** ： `acdnnDestroy()` 释放资源时会隐式 `hggcDeviceSynchronize()`，因此应放在性能关键路径之外。
- **多线程范式** ：每个线程持有自己的句柄、贯穿其生命周期，是最简洁的并发模型。

**参数**

- `handle` —*输出*：接收新分配的 acDNN 句柄。

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`handle` 为 NULL。
- `ACDNN_STATUS_NOT_INITIALIZED`：找不到兼容的真武 PPU、HGGC Driver 未装或被禁用、HGGC Runtime 初始化失败。
- `ACDNN_STATUS_ARCH_MISMATCH`：真武 PPU 架构版本过旧。
- `ACDNN_STATUS_ALLOC_FAILED`：Host 端内存分配失败。
- `ACDNN_STATUS_INTERNAL_ERROR`：HGGC 资源分配失败。
- `ACDNN_STATUS_LICENSE_ERROR`：acDNN 许可证校验失败（仅在启用该功能时触发）。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

> **关于下述 `Create*Descriptor()` 系列** ：以下 10 个函数都遵循同一模式，分配并返回一个未初始化的描述符对象指针，后续需用对应的 `Set*Descriptor()` 进行实际配置。除特别注明外，可能的返回码统一为： `ACDNN_STATUS_SUCCESS`（创建成功）/ `ACDNN_STATUS_ALLOC_FAILED`（资源分配失败）；少数函数还会在传入空指针时返回 `ACDNN_STATUS_BAD_PARAM`。每个描述符的语义和初始化函数已在 2.1.1 表中给出。

#### 2.2.5. acdnnCreateActivationDescriptor() {#225-acdnncreateactivationdescriptor}

```cpp
acdnnStatus_t acdnnCreateActivationDescriptor(
    acdnnActivationDescriptor_t *activationDesc);
```

为 `acdnnActivationDescriptor_t` 分配存储。

#### 2.2.6. acdnnCreateDropoutDescriptor() {#226-acdnncreatedropoutdescriptor}

```cpp
acdnnStatus_t acdnnCreateDropoutDescriptor(
    acdnnDropoutDescriptor_t *dropoutDesc);
```

为 `acdnnDropoutDescriptor_t` 分配存储。

#### 2.2.7. acdnnCreateFilterDescriptor() {#227-acdnncreatefilterdescriptor}

```cpp
acdnnStatus_t acdnnCreateFilterDescriptor(
    acdnnFilterDescriptor_t *filterDesc);
```

为 `acdnnFilterDescriptor_t` 分配存储。

#### 2.2.8. acdnnCreateLRNDescriptor() {#228-acdnncreatelrndescriptor}

```cpp
acdnnStatus_t acdnnCreateLRNDescriptor(
    acdnnLRNDescriptor_t *lrnDesc);
```

为 `acdnnLRNDescriptor_t` 分配存储，可同时承载 LRN 与 `DivisiveNormalization` 层（前向 / 后向）所需的运行时参数。

#### 2.2.9. acdnnCreateOpTensorDescriptor() {#229-acdnncreateoptensordescriptor}

```cpp
acdnnStatus_t acdnnCreateOpTensorDescriptor(
    acdnnOpTensorDescriptor_t *opTensorDesc);
```

为 `acdnnOpTensorDescriptor_t` 分配存储；除常规返回码外，传入无效指针时会得到 `ACDNN_STATUS_BAD_PARAM`。

- `opTensorDesc` —*输出*：指向张量逐点运算描述符（如加法、乘法等）的指针的指针。

#### 2.2.10. acdnnCreatePoolingDescriptor() {#2210-acdnncreatepoolingdescriptor}

```cpp
acdnnStatus_t acdnnCreatePoolingDescriptor(
    acdnnPoolingDescriptor_t *poolingDesc);
```

为 `acdnnPoolingDescriptor_t` 分配存储。

#### 2.2.11. acdnnCreateReduceTensorDescriptor() {#2211-acdnncreatereducetensordescriptor}

```cpp
acdnnStatus_t acdnnCreateReduceTensorDescriptor(
    acdnnReduceTensorDescriptor_t *reduceTensorDesc);
```

为 `acdnnReduceTensorDescriptor_t` 分配存储； `reduceTensorDesc == NULL` 时返回 `ACDNN_STATUS_BAD_PARAM`。

#### 2.2.12. acdnnCreateSpatialTransformerDescriptor() {#2212-acdnncreatespatialtransformerdescriptor}

```cpp
acdnnStatus_t acdnnCreateSpatialTransformerDescriptor(
    acdnnSpatialTransformerDescriptor_t *stDesc);
```

为 `acdnnSpatialTransformerDescriptor_t` 分配存储。

#### 2.2.13. acdnnCreateTensorDescriptor() {#2213-acdnncreatetensordescriptor}

```cpp
acdnnStatus_t acdnnCreateTensorDescriptor(
    acdnnTensorDescriptor_t *tensorDesc);
```

为 `acdnnTensorDescriptor_t` 分配存储；内部数据初始化为全零。返回码额外包含 `ACDNN_STATUS_BAD_PARAM`（参数无效）。

- `tensorDesc` —*输出*：指向新分配的张量描述符句柄的指针。

#### 2.2.14. acdnnCreateTensorTransformDescriptor() {#2214-acdnncreatetensortransformdescriptor}

```cpp
acdnnStatus_t acdnnCreateTensorTransformDescriptor(
    acdnnTensorTransformDescriptor_t *transformDesc);
```

为 `acdnnTensorTransformDescriptor_t` 分配存储；返回时内部数据为零，需后续调用 `acdnnSetTensorTransformDescriptor()` 完成初始化。 `transformDesc == NULL` 时返回 `ACDNN_STATUS_BAD_PARAM`。

- `transformDesc` —*输出*：指向尚未初始化的张量变换描述符的指针。

#### 2.2.15. acdnnDeriveBNTensorDescriptor() {#2215-acdnnderivebntensordescriptor}

从 x 数据描述符派生批归一化辅助张量描述符（`Scale` / `invVariance` / `bnBias` / `bnScale`）。

```cpp
acdnnStatus_t acdnnDeriveBNTensorDescriptor(
    acdnnTensorDescriptor_t derivedBnDesc,
    const acdnnTensorDescriptor_t xDesc,
    acdnnBatchNormMode_t mode);
```

生成的张量描述符用作 `acdnnBatchNormalizationForwardInference()` 和 `acdnnBatchNormalizationForwardTraining()` 函数的 `bnScaleBiasMeanVarDesc` 参数，以及 `acdnnBatchNormalizationBackward()` 函数中的 `bnScaleBiasDiffDesc` 参数。

生成的维度将为：
- 对于 `ACDNN_BATCHNORM_SPATIAL`：4D 为 1xCx1x1，5D 为 1xCx1x1x1。

对于 HALF 输入数据类型，生成的张量描述符将具有 FLOAT 类型。对于其他数据类型，它将具有与输入数据相同的类型。

!!! note
    - 仅支持 4D 和 5D Tensor。
    - `derivedBnDesc` 应首先使用 `acdnnCreateTensorDescriptor()` 创建。
    - `xDesc` 是层的 x 数据的描述符，在调用此函数之前必须已设置好正确的维度。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `derivedBnDesc` | 输出 | 指向已创建的张量描述符的句柄 |
| `xDesc` | 输入 | 指向已创建和初始化的层的 x 数据描述符的句柄 |
| `mode` | 输入 | 批归一化层的操作模式 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：无效的批归一化模式。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.16. acdnnDestroy() {#2216-acdnndestroy}

```cpp
acdnnStatus_t acdnnDestroy(acdnnHandle_t handle);
```

释放 acDNN 句柄关联的全部资源。通常是该句柄上的最后一次调用。函数返回前会隐式 `hggcDeviceSynchronize()`，详见 `acdnnCreate()` 中关于 create / destroy 频次的建议。

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | 待销毁的 acDNN 句柄 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`handle` 为 NULL。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

> **关于下述 `Destroy*Descriptor()` 系列** ：以下 10 个函数都对应 2.2.5–2.2.14 创建出的描述符，释放内部资源；除非另有说明，参数即「待销毁的描述符指针」，传入 NULL 视为无操作，返回码统一为 `ACDNN_STATUS_SUCCESS`。

#### 2.2.17. acdnnDestroyActivationDescriptor() {#2217-acdnndestroyactivationdescriptor}

```cpp
acdnnStatus_t acdnnDestroyActivationDescriptor(
    acdnnActivationDescriptor_t activationDesc);
```

释放 `acdnnActivationDescriptor_t`。

#### 2.2.18. acdnnDestroyDropoutDescriptor() {#2218-acdnndestroydropoutdescriptor}

```cpp
acdnnStatus_t acdnnDestroyDropoutDescriptor(
    acdnnDropoutDescriptor_t dropoutDesc);
```

释放 `acdnnDropoutDescriptor_t`。

#### 2.2.19. acdnnDestroyFilterDescriptor() {#2219-acdnndestroyfilterdescriptor}

```cpp
acdnnStatus_t acdnnDestroyFilterDescriptor(
    acdnnFilterDescriptor_t filterDesc);
```

释放 `acdnnFilterDescriptor_t`。

#### 2.2.20. acdnnDestroyLRNDescriptor() {#2220-acdnndestroylrndescriptor}

```cpp
acdnnStatus_t acdnnDestroyLRNDescriptor(acdnnLRNDescriptor_t lrnDesc);
```

释放 `acdnnLRNDescriptor_t`。

#### 2.2.21. acdnnDestroyOpTensorDescriptor() {#2221-acdnndestroyoptensordescriptor}

```cpp
acdnnStatus_t acdnnDestroyOpTensorDescriptor(
    acdnnOpTensorDescriptor_t opTensorDesc);
```

释放 `acdnnOpTensorDescriptor_t`。

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `opTensorDesc` | 输入 | 要销毁的张量逐点运算描述符 |

#### 2.2.22. acdnnDestroyPoolingDescriptor() {#2222-acdnndestroypoolingdescriptor}

```cpp
acdnnStatus_t acdnnDestroyPoolingDescriptor(
    acdnnPoolingDescriptor_t poolingDesc);
```

释放 `acdnnPoolingDescriptor_t`。

#### 2.2.23. acdnnDestroyReduceTensorDescriptor() {#2223-acdnndestroyreducetensordescriptor}

```cpp
acdnnStatus_t acdnnDestroyReduceTensorDescriptor(
    acdnnReduceTensorDescriptor_t tensorDesc);
```

释放 `acdnnReduceTensorDescriptor_t`； `tensorDesc == NULL` 时为空操作。

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `tensorDesc` | 输入 | 要销毁的张量归约描述符 |

#### 2.2.24. acdnnDestroySpatialTransformerDescriptor() {#2224-acdnndestroyspatialtransformerdescriptor}

```cpp
acdnnStatus_t acdnnDestroySpatialTransformerDescriptor(
    acdnnSpatialTransformerDescriptor_t stDesc);
```

释放 `acdnnSpatialTransformerDescriptor_t`。

#### 2.2.25. acdnnDestroyTensorDescriptor() {#2225-acdnndestroytensordescriptor}

```cpp
acdnnStatus_t acdnnDestroyTensorDescriptor(
    acdnnTensorDescriptor_t tensorDesc);
```

释放 `acdnnTensorDescriptor_t`； `tensorDesc == NULL` 时为空操作。

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `tensorDesc` | 输入 | 要销毁的张量描述符 |

#### 2.2.26. acdnnDestroyTensorTransformDescriptor() {#2226-acdnndestroytensortransformdescriptor}

```cpp
acdnnStatus_t acdnnDestroyTensorTransformDescriptor(
    acdnnTensorTransformDescriptor_t transformDesc);
```

释放 `acdnnTensorTransformDescriptor_t`。

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `transformDesc` | 输入 | 要销毁的张量变换描述符 |

#### 2.2.27. acdnnDropoutForward() {#2227-acdnndropoutforward}

对 x 执行前向 Dropout，约 `dropout` 比例的值置零，其余值缩放 `1/(1-dropout)` 倍，结果写入 y。不可与另一个共享相同 states 的 Dropout 并发运行。

```cpp
acdnnStatus_t acdnnDropoutForward(
acdnnHandle_t handle,
const acdnnDropoutDescriptor_t dropoutDesc,
const acdnnTensorDescriptor_t xDesc,
const void *x,
const acdnnTensorDescriptor_t yDesc,
void *y,
void *reserveSpace,
size_t reserveSpaceSizeInBytes);
```

!!! note
    - 对于完全 Packing 的 Tensor 可获得更好的性能。
    - 此函数不应在推理期间调用。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | 指向已创建的 acDNN 上下文的句柄 |
| `dropoutDesc` | 输入 | 先前创建的 Dropout 描述符对象 |
| `xDesc` | 输入 | 指向已初始化的张量描述符的句柄 |
| `x` | 输入 | 指向由 `xDesc` 描述符描述的 Tensor 数据的指针 |
| `yDesc` | 输入 | 指向已初始化的张量描述符的句柄 |
| `y` | 输出 | 指向由 `yDesc` 描述符描述的 Tensor 数据的指针 |
| `reserveSpace` | 输出 | 指向用户分配的真武 PPU 内存的指针，此函数使用。预期 `reserveSpace` 的内容在 `acdnnDropoutForward()` 和 `acdnnDropoutBackward()` 调用之间保持不变 |
| `reserveSpaceSizeInBytes` | 输入 | 指定为预留空间提供的内存大小（以字节为单位） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：函数不支持提供的配置。
- `ACDNN_STATUS_BAD_PARAM`：满足以下至少一个条件：
  - 输入 Tensor 和输出 Tensor 的元素数量不同
  - 输入 Tensor 和输出 Tensor 的数据类型不匹配
  - 提供的指针之一为 NULL
- `ACDNN_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.28. acdnnDropoutGetReserveSpaceSize() {#2228-acdnndropoutgetreservespacesize}

查询给定 `xDesc` 运行 Dropout 所需的 reserve space 大小。该空间需在前向与 Backward 之间保持不变。

```cpp
acdnnStatus_t acdnnDropoutGetReserveSpaceSize(
    acdnnTensorDescriptor_t xDesc,
    size_t *sizeInBytes);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `xDesc` | 输入 | 指向已初始化的张量描述符的句柄，描述 Dropout 操作的输入 |
| `sizeInBytes` | 输出 | 作为预留空间所需的真武 PPU 内存大小，以便能够使用 `xDesc` 指定的输入张量描述符运行 Dropout |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`xDesc` 是 NULL 指针。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.29. acdnnDropoutGetStatesSize() {#2229-acdnndropoutgetstatessize}

查询存储随机数生成器状态所需的设备内存大小。

```cpp
acdnnStatus_t acdnnDropoutGetStatesSize(
    acdnnHandle_t handle,
    size_t *sizeInBytes);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | 指向已创建的 acDNN 上下文的句柄 |
| `sizeInBytes` | 输出 | 存储随机数生成器状态所需的真武 PPU 内存大小 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.30. acdnnGetActivationDescriptor() {#2230-acdnngetactivationdescriptor}

查询已初始化的激活描述符。

```cpp
acdnnStatus_t acdnnGetActivationDescriptor(
const acdnnActivationDescriptor_t activationDesc,
acdnnActivationMode_t *mode,
acdnnNanPropagation_t *reluNanOpt,
double *coef);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `activationDesc` | 输入 | 指向已创建的激活描述符的句柄 |
| `mode` | 输出 | 指定激活模式的枚举值 |
| `reluNanOpt` | 输出 | 指定 NaN 传播模式的枚举值 |
| `coef` | 输出 | 当激活模式设置为 `ACDNN_ACTIVATION_CLIPPED_RELU` 时，指定裁剪阈值的浮点数；或当激活模式设置为 `ACDNN_ACTIVATION_ELU` 时，指定 Alpha 系数的浮点数 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.31. acdnnGetDropoutDescriptor() {#2231-acdnngetdropoutdescriptor}

查询已初始化的 Dropout 描述符的字段。

```cpp
acdnnStatus_t acdnnGetDropoutDescriptor(
  acdnnDropoutDescriptor_t dropoutDesc,
  acdnnHandle_t handle,
  float *dropout,
  void **states,
  unsigned long long *seed);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `dropoutDesc` | 输入 | 已初始化的 Dropout 描述符 |
| `handle` | 输入 | 指向已创建的 acDNN 上下文的句柄 |
| `dropout` | 输出 | 在 Dropout 层期间将输入值设置为 0 的概率 |
| `states` | 输出 | 指向用户分配的真武 PPU 内存的指针，该内存保存随机数生成器状态 |
| `seed` | 输出 | 用于初始化随机数生成器状态的种子值 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：一个或多个参数是无效指针。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.32. acdnnGetErrorString() {#2232-acdnngeterrorstring}

```cpp
const char *acdnnGetErrorString(acdnnStatus_t status);
```

把状态码翻译成 NUL 结尾的静态字符串。例如 `ACDNN_STATUS_SUCCESS` ⇒ `"ACDNN_STATUS_SUCCESS"`。传入未知状态值时返回描述性字符串。返回的指针指向库内只读静态区，可直接 `printf` 或日志拼接。

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `status` | 输入 | 要查询的 acDNN 状态枚举值 |

#### 2.2.33. acdnnGetFilter4dDescriptor() {#2233-acdnngetfilter4ddescriptor}

查询已初始化的 4D 滤波器描述符参数。

```cpp
acdnnStatus_t acdnnGetFilter4dDescriptor(
const acdnnFilterDescriptor_t filterDesc,
acdnnDataType_t *dataType,
acdnnTensorFormat_t *format,
int *k,
int *c,
int *h,
int *w);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `filterDesc` | 输入 | 指向已创建的滤波器描述符的句柄 |
| `dataType` | 输出 | 数据类型 |
| `format` | 输出 | 格式类型 |
| `k` | 输出 | 输出特征图的数量 |
| `c` | 输出 | 输入特征图的数量 |
| `h` | 输出 | 每个滤波器的高度 |
| `w` | 输出 | 每个滤波器的宽度 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.34. acdnnGetFilterNdDescriptor() {#2234-acdnngetfilternddescriptor}

查询已初始化的 Nd 滤波器描述符参数。

```cpp
acdnnStatus_t acdnnGetFilterNdDescriptor(
    const acdnnFilterDescriptor_t wDesc,
    int nbDimsRequested,
    acdnnDataType_t *dataType,
    acdnnTensorFormat_t *format,
    int *nbDims,
    int filterDimA[]);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `wDesc` | 输入 | 指向已初始化的滤波器描述符的句柄 |
| `nbDimsRequested` | 输入 | 期望的滤波器描述符的维度数。它也是数组 `filterDimA` 能够保存结果的最小大小 |
| `dataType` | 输出 | 数据类型 |
| `format` | 输出 | 格式类型 |
| `nbDims` | 输出 | 滤波器的实际维度数 |
| `filterDimA` | 输出 | 大小至少为 `nbDimsRequested` 的维度数组，将使用提供的滤波器描述符中的滤波器参数填充 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：参数 `nbDimsRequested` 为负数。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.35. acdnnGetFilterSizeInBytes() {#2235-acdnngetfiltersizeinbytes}

根据描述符返回滤波器张量的设备内存占用（字节）。

```cpp
acdnnStatus_t acdnnGetFilterSizeInBytes(
    const acdnnFilterDescriptor_t filterDesc,
    size_t *size);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `filterDesc` | 输入 | 指向已初始化的滤波器描述符的句柄 |
| `size` | 输出 | 在真武 PPU 内存中保存 Tensor 所需的字节大小 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`filterDesc` 无效。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.36. acdnnGetLRNDescriptor() {#2236-acdnngetlrndescriptor}

检索已初始化的 LRN 描述符中存储的参数值。

```cpp
acdnnStatus_t acdnnGetLRNDescriptor(
    acdnnLRNDescriptor_t normDesc,
    unsigned *lrnN,
    double *lrnAlpha,
    double *lrnBeta,
    double *lrnK);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `normDesc` | 输入 | 指向已创建的局部响应归一化描述符的句柄 |
| `lrnN`,`lrnAlpha`,`lrnBeta`,`lrnK` | 输出 | 接收存储在描述符对象中的参数值的指针，这些指针中的任何一个都可以为 NULL（不返回相应参数的值） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.37. acdnnGetOpTensorDescriptor() {#2237-acdnngetoptensordescriptor}

返回张量逐点运算描述符的配置。

```cpp
acdnnStatus_t acdnnGetOpTensorDescriptor(
    const acdnnOpTensorDescriptor_t opTensorDesc,
    acdnnOpTensorOp_t *opTensorOp,
    acdnnDataType_t *opTensorCompType,
    acdnnNanPropagation_t *opTensorNanOpt);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `opTensorDesc` | 输入 | 张量逐点运算描述符，用于从中获取配置 |
| `opTensorOp` | 输出 | 指向与此张量逐点运算描述符关联的逐点运算类型的指针 |
| `opTensorCompType` | 输出 | 指向与此张量逐点运算描述符关联的 acDNN 数据类型的指针 |
| `opTensorNanOpt` | 输出 | 指向与此张量逐点运算描述符关联的 NaN 传播选项的指针 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：传入的输入张量逐点运算描述符无效。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.38. acdnnGetPooling2dForwardOutputDim() {#2238-acdnngetpooling2dforwardoutputdim}

计算 2D 池化后张量的输出维度。

```cpp
acdnnStatus_t acdnnGetPooling2dForwardOutputDim(
    const acdnnPoolingDescriptor_t poolingDesc,
    const acdnnTensorDescriptor_t inputDesc,
    int *outN,
    int *outC,
    int *outH,
    int *outW);
```

输出图像的每个维度 h 和 w 计算如下：

```cpp
outputDim = 1 + (inputDim + 2*padding - windowDim)/poolingStride;
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `poolingDesc` | 输入 | 指向已初始化的池化描述符的句柄 |
| `inputDesc` | 输入 | 指向已初始化的输入张量描述符的句柄 |
| `outN` | 输出 | 输出中的图像数量 |
| `outC` | 输出 | 输出中的通道数量 |
| `outH` | 输出 | 输出中图像的高度 |
| `outW` | 输出 | 输出中图像的宽度 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：满足以下至少一个条件：
  - `poolingDesc` 尚未初始化
  - `poolingDesc` 或 `inputDesc` 的维度数无效（分别需要 2 和 4）

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.39. acdnnGetPoolingNdForwardOutputDim() {#2239-acdnngetpoolingndforwardoutputdim}

计算 Nd 池化后张量的输出维度。

```cpp
acdnnStatus_t acdnnGetPoolingNdForwardOutputDim(
    const acdnnPoolingDescriptor_t poolingDesc,
    const acdnnTensorDescriptor_t inputDesc,
    int nbDims,
    int outDimA[]);
```

输出 Tensor 的空间维度（共 nbDims-2 维）按以下公式逐维计算：

```cpp
outputDim = 1 + (inputDim + 2*padding - windowDim)/poolingStride;
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `poolingDesc` | 输入 | 指向已初始化的池化描述符的句柄 |
| `inputDesc` | 输入 | 指向已初始化的输入张量描述符的句柄 |
| `nbDims` | 输入 | 要应用池化的维度数量 |
| `outDimA` | 输出 | 包含 `nbDims` 个输出维度的数组 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：满足以下至少一个条件：
  - `poolingDesc` 尚未初始化
  - `nbDims` 的值与 `poolingDesc` 和 `inputDesc` 的维度不一致

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.40. acdnnGetProperty() {#2240-acdnngetproperty}

将 acDNN 库版本号的指定部分写入 host 端存储。

```cpp
acdnnStatus_t acdnnGetProperty(
    hggcLibraryPropertyType type,
    int *value);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `type` | 输入 | 枚举类型，指示函数报告 acDNN 主版本号、次版本号或补丁级别的数值，具体取决于 `type` 设置为 `HGGC_MAJOR_VERSION`、`HGGC_MINOR_VERSION` 还是 `HGGC_PATCH_LEVEL` |
| `value` | 输出 | 应写入版本信息的主机指针 |

返回码：

- `ACDNN_STATUS_INVALID_VALUE`：`type` 参数值无效。
- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.41. acdnnGetReduceTensorDescriptor() {#2241-acdnngetreducetensordescriptor}

查询已初始化的张量归约描述符。

```cpp
acdnnStatus_t acdnnGetReduceTensorDescriptor(
    const acdnnReduceTensorDescriptor_t reduceTensorDesc,
    acdnnReduceTensorOp_t *reduceTensorOp,
    acdnnDataType_t *reduceTensorCompType,
    acdnnNanPropagation_t *reduceTensorNanOpt,
    acdnnReduceTensorIndices_t *reduceTensorIndices,
    acdnnIndicesType_t *reduceTensorIndicesType);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `reduceTensorDesc` | 输入 | 指向已初始化的张量归约描述符对象的指针 |
| `reduceTensorOp` | 输出 | 指定归约运算的枚举值 |
| `reduceTensorCompType` | 输出 | 指定归约计算数据类型的枚举值 |
| `reduceTensorNanOpt` | 输出 | 指定 NaN 传播模式的枚举值 |
| `reduceTensorIndices` | 输出 | 指定归约索引的枚举值 |
| `reduceTensorIndicesType` | 输出 | 指定 Reduce Tensor 索引类型的枚举值 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`reduceTensorDesc` 为 NULL。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.42. acdnnGetReductionIndicesSize() {#2242-acdnngetreductionindicessize}

这是一个辅助函数，用于根据输入和输出 Tensor 返回传递给归约的索引空间的最小大小。

```cpp
acdnnStatus_t acdnnGetReductionIndicesSize(
    acdnnHandle_t handle,
    const acdnnReduceTensorDescriptor_t reduceDesc,
    const acdnnTensorDescriptor_t aDesc,
    const acdnnTensorDescriptor_t cDesc,
    size_t *sizeInBytes);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | 指向已创建的 acDNN 库描述符的句柄 |
| `reduceDesc` | 输入 | 指向已初始化的张量归约描述符对象的指针 |
| `aDesc` | 输入 | 指向输入张量描述符的指针 |
| `cDesc` | 输入 | 指向输出张量描述符的指针 |
| `sizeInBytes` | 输出 | 传递给归约的索引空间的最小大小 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.43. acdnnGetReductionWorkspaceSize() {#2243-acdnngetreductionworkspacesize}

这是一个辅助函数，用于根据输入和输出 Tensor 返回传递给归约的工作空间的最小大小。

```cpp
acdnnStatus_t acdnnGetReductionWorkspaceSize(
    acdnnHandle_t handle,
    const acdnnReduceTensorDescriptor_t reduceDesc,
    const acdnnTensorDescriptor_t aDesc,
    const acdnnTensorDescriptor_t cDesc,
    size_t *sizeInBytes);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | 指向已创建的 acDNN 库描述符的句柄 |
| `reduceDesc` | 输入 | 指向已初始化的张量归约描述符对象的指针 |
| `aDesc` | 输入 | 指向输入张量描述符的指针 |
| `cDesc` | 输入 | 指向输出张量描述符的指针 |
| `sizeInBytes` | 输出 | 传递给归约的工作空间的最小大小 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.44. acdnnGetStream() {#2244-acdnngetstream}

检索 acDNN 句柄中绑定的用户 HGGC Stream。未设置时报告空 Stream。

```cpp
acdnnStatus_t acdnnGetStream(
    acdnnHandle_t handle,
    hggcStream_t *streamId);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | 指向 acDNN 句柄的指针 |
| `streamId` | 输出 | 应存储来自 acDNN 句柄的当前 HGGC Stream 的指针 |

返回码：

- `ACDNN_STATUS_BAD_PARAM`：无效（NULL）句柄。
- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.45. acdnnGetTensor4dDescriptor() {#2245-acdnngettensor4ddescriptor}

查询已初始化的 4D 张量描述符参数。

```cpp
acdnnStatus_t acdnnGetTensor4dDescriptor(
const acdnnTensorDescriptor_t tensorDesc,
acdnnDataType_t *dataType,
int *n,
int *c,
int *h,
int *w,
int *nStride,
int *cStride,
int *hStride,
int *wStride);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `tensorDesc` | 输入 | 指向已初始化的张量描述符的句柄 |
| `dataType` | 输出 | 数据类型 |
| `n` | 输出 | 图像数量 |
| `c` | 输出 | 每个图像的特征图数量 |
| `h` | 输出 | 每个特征图的高度 |
| `w` | 输出 | 每个特征图的宽度 |
| `nStride` | 输出 | 两个连续图像之间的步幅 |
| `cStride` | 输出 | 两个连续特征图之间的步幅 |
| `hStride` | 输出 | 两连续行之间的步幅 |
| `wStride` | 输出 | 两连续列之间的步幅 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.46. acdnnGetTensorNdDescriptor() {#2246-acdnngettensornddescriptor}

检索已初始化的 Nd 张量描述符中存储的值。

```cpp
acdnnStatus_t acdnnGetTensorNdDescriptor(
    const acdnnTensorDescriptor_t tensorDesc,
    int nbDimsRequested,
    acdnnDataType_t *dataType,
    int *nbDims,
    int dimA[],
    int strideA[]);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `tensorDesc` | 输入 | 指向已初始化的张量描述符的句柄 |
| `nbDimsRequested` | 输入 | 期望提取的维度数量（`dimA` 和 `strideA` 数组的最小长度） |
| `dataType` | 输出 | 数据类型 |
| `nbDims` | 输出 | Tensor 的实际维度数量将返回在 `nbDims[0]` 中 |
| `dimA` | 输出 | 大小至少为 `nbDimsRequested` 的维度数组，将使用提供的张量描述符中的维度填充 |
| `strideA` | 输出 | 大小至少为 `nbDimsRequested` 的步幅数组，将使用提供的张量描述符中的步幅填充 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`tensorDesc` 或 `nbDims` 指针为 NULL。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.47. acdnnGetTensorSizeInBytes() {#2247-acdnngettensorsizeinbytes}

根据描述符返回张量的设备内存占用（字节）。

```cpp
acdnnStatus_t acdnnGetTensorSizeInBytes(
    const acdnnTensorDescriptor_t tensorDesc,
    size_t *size);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `tensorDesc` | 输入 | 指向已初始化的张量描述符的句柄 |
| `size` | 输出 | 在真武 PPU 内存中保存 Tensor 所需的字节大小 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.48. acdnnGetTensorTransformDescriptor() {#2248-acdnngettensortransformdescriptor}

返回已初始化的张量变换描述符中存储的值。

```cpp
acdnnStatus_t acdnnGetTensorTransformDescriptor(
acdnnTensorTransformDescriptor_t transformDesc, uint32_t nbDimsRequested, acdnnTensorFormat_t *destFormat, int32_t padBeforeA[], int32_t padAfterA[], uint32_t foldA[], acdnnFoldingDirection_t *direction);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `transformDesc` | 输入 | 已初始化的张量变换描述符 |
| `nbDimsRequested` | 输入 | 要考虑的维度数量 |
| `destFormat` | 输出 | 将返回的目标格式 |
| `padBeforeA[]` | 输出 | 填充了在每个维度之前要添加的填充量的数组。此 `padBeforeA[]` 参数的维度等于 `nbDimsRequested` |
| `padAfterA[]` | 输出 | 填充了在每个维度之后要添加的填充量的数组。此 `padAfterA[]` 参数的维度等于 `nbDimsRequested` |
| `foldA[]` | 输出 | 填充了每个空间维度的折叠参数的数组。此 `foldA[]` 数组的维度是 `nbDimsRequested-2` |
| `direction` | 输出 | 选择 Fold 或 Unfold 的设置 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：如果 `transformDesc` 为 NULL 或 `nbDimsRequested` 小于 3 或大于 `ACDNN_DIM_MAX`。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.49. acdnnGetVersion() {#2249-acdnngetversion}

返回 acDNN 库版本号（`acdnn.h` 中定义的 `ACDNN_VERSION`），可用于运行时识别库版本。定义的 `ACDNN_VERSION` 可用于使用条件编译语句使同一应用程序链接到不同的 acDNN 版本。

```cpp
size_t acdnnGetVersion(void);
```

该函数无参数。返回值为 `size_t` 类型的版本号。

#### 2.2.50. acdnnInitTransformDest() {#2250-acdnninittransformdest}

初始化并返回张量变换操作的目标张量描述符 `destDesc`。初始化使用 Transform 描述符 `acdnnTensorDescriptor_t` 中描述的所需参数完成。

```cpp
acdnnStatus_t acdnnInitTransformDest(
const acdnnTensorTransformDescriptor_t transformDesc,
const acdnnTensorDescriptor_t srcDesc,
acdnnTensorDescriptor_t destDesc,
size_t *destSizeInBytes);
```

!!! note
    返回的张量描述符将是 Packed 的。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `transformDesc` | 输入 | 指向已初始化的张量变换描述符的句柄 |
| `srcDesc` | 输入 | 指向已初始化的张量描述符的句柄 |
| `destDesc` | 输出 | 待初始化并返回的张量描述符句柄 |
| `destSizeInBytes` | 输出 | 保存新 Tensor 大小（字节）的指针 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：如果 `srcDesc` 或 `destDesc` 为 NULL，或者张量描述符的 `nbDims` 不正确。更多信息，请参阅张量描述符。
- `ACDNN_STATUS_NOT_SUPPORTED`：如果提供的配置不是 4D。
- `ACDNN_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.51. acdnnLRNCrossChannelForward() {#2251-acdnnlrncrosschannelforward}

执行前向 LRN 层计算。

```cpp
acdnnStatus_t acdnnLRNCrossChannelForward(
    acdnnHandle_t handle,
    acdnnLRNDescriptor_t normDesc,
    acdnnLRNMode_t lrnMode,
    const void *alpha,
    const acdnnTensorDescriptor_t xDesc,
    const void *x,
    const void *beta,
    const acdnnTensorDescriptor_t yDesc,
    void *y);
```

!!! note
    支持的格式为：4D `x` 和 `y` 的正步幅、NCHW 和 NHWC，以及仅 5D 的 NCDHW DHW Packed（对于 `x` 和 `y` 都适用）。仅支持不重叠的 4D 和 5D 张量。为了性能，首选 NCHW 布局。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | 指向已创建的 acDNN 库描述符的句柄 |
| `normDesc` | 输入 | 指向已初始化的局部响应归一化参数描述符的句柄 |
| `lrnMode` | 输入 | LRN 层操作模式。目前仅实现 `ACDNN_LRN_CROSS_CHANNEL_DIM1`。Normalization 沿 Tensor 的 `dimA[1]` 执行 |
| `alpha`,`beta` | 输入 | 指向缩放因子（位于主机内存）的指针，用于将层输出值与目标 Tensor 中的先前值进行混合，计算方式如下： `dst = alpha[0] * result + beta[0] * priorDst` |
| `xDesc`,`yDesc` | 输入 | 输入和输出 Tensor 的张量描述符对象 |
| `x` | 输入 | 设备内存中的输入 Tensor 数据指针 |
| `y` | 输出 | 设备内存中的输出 Tensor 数据指针 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：满足以下至少一个条件：
  - Tensor 指针 `x`、`y` 之一为 NULL
  - 输入 Tensor 维度数为 2 或更少
  - LRN 描述符参数超出其有效范围
  - Tensor 参数之一为 5D 但不是 NCDHW DHW-packed 格式
- `ACDNN_STATUS_NOT_SUPPORTED`：函数不支持提供的配置。请参阅以下不支持的配置示例：
  - 任何输入 Tensor 数据类型与任何输出 Tensor 数据类型不相同

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.52. acdnnOpsInferVersionCheck() {#2252-acdnnopsinferversioncheck}

检查当前模块动态库与 acDNN 库版本是否一致（系列检查函数之一）。

```cpp
acdnnStatus_t acdnnOpsInferVersionCheck(void);
```

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.53. acdnnOpTensor() {#2253-acdnnoptensor}

实现 `C = op(alpha1[0] * A, alpha2[0] * B) + beta[0] * C`，给定张量 A、B、C 以及缩放因子 alpha1、alpha2 和 beta。要使用的 op 由张量操作描述符（Op 张量描述符） `acdnnOpTensorDescriptor_t`（即 `opTensorDesc` 的类型）指示。当前支持的 op 由 `acdnnOpTensorOp_t` 枚举列出。

```cpp
acdnnStatus_t acdnnOpTensor(
    acdnnHandle_t handle,
    const acdnnOpTensorDescriptor_t opTensorDesc,
    const void *alpha1,
    const acdnnTensorDescriptor_t aDesc,
    const void *A,
    const void *alpha2,
    const acdnnTensorDescriptor_t bDesc,
    const void *B,
    const void *beta,
    const acdnnTensorDescriptor_t cDesc,
    void *C);
```

以下限制适用于输入和目标 Tensor：
- 输入 Tensor A 的每个维度必须与目标 Tensor C 的相应维度匹配，输入 Tensor B 的每个维度必须与目标 Tensor C 的相应维度匹配或必须等于 1。在后一种情况下，将使用输入 Tensor B 中那些维度的相同值混合到 C Tensor 中。

输入 Tensor A 和 B 以及目标 Tensor C 的数据类型必须满足：

**表 `acdnnOpTensor()` 支持的数据类型**

| opTensorDesc 中的 opTensorCompType | A | B | C（目标） |
| :--- | :--- | :--- | :--- |
| `FLOAT` | `FLOAT` | `FLOAT` | `FLOAT` |
| `FLOAT` | `INT8` | `INT8` | `FLOAT` |
| `FLOAT` | `HALF` | `HALF` | `FLOAT` |
| `FLOAT` | `BFLOAT16` | `BFLOAT16` | `FLOAT` |
| `DOUBLE` | `DOUBLE` | `DOUBLE` | `DOUBLE` |
| `FLOAT` | `FLOAT` | `FLOAT` | `HALF` |
| `FLOAT` | `HALF` | `HALF` | `HALF` |
| `FLOAT` | `INT8` | `INT8` | `INT8` |
| `FLOAT` | `FLOAT` | `FLOAT` | `INT8` |
| `FLOAT` | `FLOAT` | `FLOAT` | `BFLOAT16` |
| `FLOAT` | `BFLOAT16` | `BFLOAT16` | `BFLOAT16` |

!!! note
    `ACDNN_TENSOR_NCHW_VECT_C` 不作为输入张量格式支持。支持最多五（5）维的所有 Tensor。超出这些维度的格式不受支持。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | 指向已创建的 acDNN 上下文的句柄 |
| `opTensorDesc` | 输入 | 指向已初始化的张量操作描述符（Op 张量描述符）的句柄 |
| `alpha1`,`alpha2`,`beta` | 输入 | 指向缩放因子（位于主机内存）的指针，用于将源值与目标张量中的先前值进行混合，计算方式如下： `dst = alpha[0] * result + beta[0] * priorDst` |
| `aDesc`,`bDesc`,`cDesc` | 输入 | 指向已初始化的张量描述符的句柄 |
| `A`,`B` | 输入 | 分别指向由 `aDesc` 和 `bDesc` 描述符描述的 Tensor 数据的指针 |
| `C` | 输入/输出 | 指向由 `cDesc` 描述符描述的 Tensor 数据的指针 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：函数不支持提供的配置。请参阅以下不支持的配置示例：
  - 偏置 Tensor 和输出 Tensor 的维度超过 5
  - `opTensorCompType` 未按上述规定设置
- `ACDNN_STATUS_BAD_PARAM`：目标 Tensor C 的数据类型无法识别，或不满足上述对输入和目标 Tensor 的限制。
- `ACDNN_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.54. acdnnPoolingForward() {#2254-acdnnpoolingforward}

计算池化（相邻值的 Max 或 Average），生成空间尺寸缩小的输出。

```cpp
acdnnStatus_t acdnnPoolingForward(
    acdnnHandle_t handle,
    const acdnnPoolingDescriptor_t poolingDesc,
    const void *alpha,
    const acdnnTensorDescriptor_t xDesc,
    const void *x,
    const void *beta,
    const acdnnTensorDescriptor_t yDesc,
    void *y);
```

支持所有张量格式，使用 HW 打包张量时预期性能最佳。仅允许 2 和 3 个空间维度。仅当向量化张量具有 2 个空间维度时才支持。

输出 Tensor `yDesc` 的维度可以小于或大于函数 `acdnnGetPooling2dForwardOutputDim()` 或 `acdnnGetPoolingNdForwardOutputDim()` 建议的维度。

对于 Average 池化，即使是整数输入和输出数据类型，Compute Type 也是 Float。输出 Round 模式为 Nearest-even，如果超出范围则 Clamp 到该 Type 的最负或最正值。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | 指向已创建的 acDNN 上下文的句柄 |
| `poolingDesc` | 输入 | 指向已初始化的池化描述符的句柄 |
| `alpha`,`beta` | 输入 | 指向缩放因子（位于主机内存）的指针，用于将计算结果与输出层中的先前值进行混合，计算方式如下： `dst = alpha[0] * result + beta[0] * priorDst` |
| `xDesc` | 输入 | 指向已初始化的输入张量描述符的句柄。必须是 `FLOAT`、`DOUBLE`、`HALF`、`INT8`、`INT8x4`、`INT8x32` 或 `BFLOAT16` 类型 |
| `x` | 输入 | 与张量描述符 `xDesc` 关联的真武 PPU 内存数据指针 |
| `yDesc` | 输入 | 指向已初始化的输出张量描述符的句柄。必须是 `FLOAT`、`DOUBLE`、`HALF`、`INT8`、`INT8x4`、`INT8x32` 或 `BFLOAT16` 类型 |
| `y` | 输出 | 与输出张量描述符 `yDesc` 关联的真武 PPU 内存数据指针 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：满足以下至少一个条件：
  - 输入 Tensor 和输出 Tensor 的维度 n、c 不同
  - 输入 Tensor 和输出 Tensor 的数据类型不同
- `ACDNN_STATUS_NOT_SUPPORTED`：函数不支持提供的配置。
- `ACDNN_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.55. acdnnReduceTensor() {#2255-acdnnreducetensor}

实现 `C = alpha * reduce_op(A) + beta * C`，对张量 A 沿指定维度归约。给定张量 A、C 以及缩放系数 alpha 和 beta。

要使用的归约 Op 由描述符 `reduceTensorDesc` 指示。当前支持的 op 由 `acdnnReduceTensorOp_t` 枚举列出。

```cpp
acdnnStatus_t acdnnReduceTensor(
acdnnHandle_t handle,
const acdnnReduceTensorDescriptor_t reduceTensorDesc,
void *indices,
size_t indicesSizeInBytes,
void *workspace,
size_t workspaceSizeInBytes,
const void *alpha,
const acdnnTensorDescriptor_t aDesc,
const void *A,
const void *beta,
const acdnnTensorDescriptor_t cDesc,
void *C);
```

输出 Tensor C 的每个维度必须与输入 Tensor A 的相应维度匹配或必须等于 1。等于 1 的维度指示要 Reduce 的 A 的维度。

实现将仅为 Min 和 Max Op 生成 Indices，如 `reduceTensorDesc` 的 `acdnnReduceTensorIndices_t` 枚举所示。请求其他归约 Op 的 Indices 会导致错误。Indices 的数据类型由 `acdnnIndicesType_t` 枚举指示；目前仅支持 32 位（`unsigned int`）类型。

实现返回的 Indices 不是绝对 Indices，而是相对于被 Reduce 的维度。Indices 也是 Flattened 的，即不是坐标元组。

如果 Tensor A 和 C 的数据类型为 Double，则必须匹配。在这种情况下，alpha 和 beta 以及 `reduceTensorDesc` 的 Computation Enum 都假定为 Double 类型。

HALF 和 INT8 数据类型可以与 FLOAT 数据类型混合。在这些情况下， `reduceTensorDesc` 的 Computation Enum 必须为 FLOAT 类型。

!!! note
    最多支持 8 维，支持所有张量格式。超出这些维度不受支持。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | 指向已创建的 acDNN 上下文的句柄 |
| `reduceTensorDesc` | 输入 | 指向已初始化的张量归约描述符的句柄 |
| `indices` | 输出 | 指向先前分配的用于写入 Indices 的空间的句柄 |
| `indicesSizeInBytes` | 输入 | 上述先前分配的空间的大小 |
| `workspace` | 输入 | 指向先前分配的用于归约实现的空间的句柄 |
| `workspaceSizeInBytes` | 输入 | 上述先前分配的空间的大小 |
| `alpha`,`beta` | 输入 | 指向缩放因子（位于主机内存）的指针，用于将源值与目标张量中的先前值进行混合，计算方式如下： `dst = alpha[0] * result + beta[0] * priorDst` |
| `aDesc`,`cDesc` | 输入 | 指向已初始化的张量描述符的句柄 |
| `A` | 输入 | 指向由 `aDesc` 描述符描述的 Tensor 数据的指针 |
| `C` | 输入/输出 | 指向由 `cDesc` 描述符描述的 Tensor 数据的指针 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：配置不支持，如输入/输出张量维度 > 8，或 `reduceTensorIndices` 与 `Indices`/`indicesType` 不兼容。
- `ACDNN_STATUS_BAD_PARAM`：输入/输出张量维度不匹配，或违反前文形状约束。
- `ACDNN_STATUS_INVALID_VALUE`：`Indices` 或 `Workspace` 容量不足。
- `ACDNN_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.56. acdnnRestoreDropoutDescriptor() {#2256-acdnnrestoredropoutdescriptor}

将 Dropout 描述符恢复到先前保存的状态。

```cpp
acdnnStatus_t acdnnRestoreDropoutDescriptor(
    acdnnDropoutDescriptor_t dropoutDesc,
    acdnnHandle_t handle,
    float dropout,
    void *states,
    size_t stateSizeInBytes,
    unsigned long long seed);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `dropoutDesc` | 输入/输出 | 先前创建的 Dropout 描述符 |
| `handle` | 输入 | 指向已创建的 acDNN 上下文的句柄 |
| `dropout` | 输入 | 执行 Dropout 时将输入 Tensor 中的值设置为 0 的概率 |
| `states` | 输入 | 指向真武 PPU 内存的指针，该内存保存由先前调用 `acdnnSetDropoutDescriptor()` 初始化的随机数生成器状态 |
| `stateSizeInBytes` | 输入 | 保存随机数生成器状态的缓冲区的字节大小 |
| `seed` | 输入 | 在先前调用 `acdnnSetDropoutDescriptor()` 中初始化状态缓冲区时使用的种子值。使用与此不同的种子值没有效果。可以通过调用 `acdnnSetDropoutDescriptor()` 来实现种子值的更改以及随后对随机数生成器状态的更新 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_INVALID_VALUE`：状态缓冲区大小（如 `stateSizeInBytes` 所示）太小。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.57. acdnnScaleTensor() {#2257-acdnnscaletensor}

按给定缩放因子对张量的所有元素做原地缩放。

```cpp
acdnnStatus_t acdnnScaleTensor(
    acdnnHandle_t handle,
    const acdnnTensorDescriptor_t yDesc,
    void *y,
    const void *alpha);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | 指向已创建的 acDNN 上下文的句柄 |
| `yDesc` | 输入 | 指向已初始化的张量描述符的句柄 |
| `y` | 输入/输出 | 指向由 `yDesc` 描述符描述的 Tensor 数据的指针 |
| `alpha` | 输入 | 主机内存中指向单个值的指针，Tensor 的所有元素将按此值缩放 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：函数不支持提供的配置。
- `ACDNN_STATUS_BAD_PARAM`：提供的指针之一为 NULL。
- `ACDNN_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.58. acdnnSetActivationDescriptor() {#2258-acdnnsetactivationdescriptor}

初始化先前创建的激活描述符。

```cpp
acdnnStatus_t acdnnSetActivationDescriptor(
    acdnnActivationDescriptor_t activationDesc,
    acdnnActivationMode_t mode,
    acdnnNanPropagation_t reluNanOpt,
    double coef);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `activationDesc` | 输入/输出 | 指向已创建的激活描述符的句柄 |
| `mode` | 输入 | 指定激活模式的枚举值 |
| `reluNanOpt` | 输入 | 指定 NaN 传播模式的枚举值 |
| `coef` | 输入 | 浮点数。当激活模式（请参阅 `acdnnActivationMode_t`）设置为 `ACDNN_ACTIVATION_CLIPPED_RELU` 时，此输入指定裁剪阈值；当激活模式设置为 `ACDNN_ACTIVATION_RELU` 时，此输入指定上限值 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`mode` 或 `reluNanOpt` 具有无效的枚举值。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.59. acdnnSetDropoutDescriptor() {#2259-acdnnsetdropoutdescriptor}

初始化先前创建的 Dropout 描述符。若 `states` 为 NULL，则不会初始化随机数生成器状态，只会设置 Dropout 值。开发者在计算期间不应更改 `states` 指向的内存。

```cpp
acdnnStatus_t acdnnSetDropoutDescriptor(
  acdnnDropoutDescriptor_t dropoutDesc,
  acdnnHandle_t handle,
  float dropout,
  void *states,
  size_t stateSizeInBytes,
  unsigned long long seed);
```

当 `states` 参数不为 NULL 时， `acdnnSetDropoutDescriptor()` 会调用 acRAND 初始化 Kernel。该 Kernel 需要大量的真武 PPU 内存用于 Stack。Kernel 完成后自动释放内存。当没有足够的可用内存用于真武 PPU Stack 时，将返回 `ACDNN_STATUS_ALLOC_FAILED` 状态。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `dropoutDesc` | 输入/输出 | 先前创建的 Dropout 描述符对象 |
| `handle` | 输入 | 指向已创建的 acDNN 上下文的句柄 |
| `dropout` | 输入 | 在 Dropout 层期间将输入值设置为零的概率 |
| `states` | 输出 | 指向用户分配的真武 PPU 内存的指针，该内存将保存随机数生成器状态 |
| `stateSizeInBytes` | 输入 | 指定为 States 提供的内存的字节大小 |
| `seed` | 输入 | 用于初始化随机数生成器状态的种子值 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_INVALID_VALUE`：`stateSizeInBytes` 参数小于 `acdnnDropoutGetStatesSize()` 返回的值。
- `ACDNN_STATUS_ALLOC_FAILED`：函数未能临时扩展真武 PPU Stack。
- `ACDNN_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。
- `ACDNN_STATUS_INTERNAL_ERROR`：库内部实现返回错误状态。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.60. acdnnSetFilter4dDescriptor() {#2260-acdnnsetfilter4ddescriptor}

将已创建的滤波器描述符初始化为 4D 滤波器（内存布局须连续）。

```cpp
acdnnStatus_t acdnnSetFilter4dDescriptor(
    acdnnFilterDescriptor_t filterDesc,
    acdnnDataType_t dataType,
    acdnnTensorFormat_t format,
    int k,
    int c,
    int h,
    int w);
```

张量格式 `ACDNN_TENSOR_NHWC` 在 `acdnnConvolutionForward()`、`acdnnConvolutionBackwardData()` 和 `acdnnConvolutionBackwardFilter()` 中支持有限。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `filterDesc` | 输入/输出 | 指向已创建的滤波器描述符的句柄 |
| `dataType` | 输入 | 数据类型 |
| `format` | 输入 | 滤波器布局 Format 的类型。设为 `ACDNN_TENSOR_NCHW` 时布局为 KCRS（K=输出特征图数， C=输入特征图数， R=行数， S=列数）；设为 `ACDNN_TENSOR_NHWC` 时布局为 KRSC。参见 [`acdnnTensorFormat_t`](#21221-acdnntensorformat_t) |
| `k` | 输入 | 输出特征图的数量 |
| `c` | 输入 | 输入特征图的数量 |
| `h` | 输入 | 每个滤波器的高度 |
| `w` | 输入 | 每个滤波器的宽度 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：参数 k、c、h、w 中至少有一个为负数，或 `dataType` 或 `format` 具有无效的枚举值。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.61. acdnnSetFilterNdDescriptor() {#2261-acdnnsetfilternddescriptor}

初始化已创建的 Nd 滤波器描述符（内存布局须连续）。

```cpp
acdnnStatus_t acdnnSetFilterNdDescriptor(
    acdnnFilterDescriptor_t filterDesc,
    acdnnDataType_t dataType,
    acdnnTensorFormat_t format,
    int nbDims,
const int filterDimA[]);
```

张量格式 `ACDNN_TENSOR_NHWC` 在 `acdnnConvolutionForward()`、`acdnnConvolutionBackwardData()` 和 `acdnnConvolutionBackwardFilter()` 中支持有限。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `filterDesc` | 输入/输出 | 指向已创建的滤波器描述符的句柄 |
| `dataType` | 输入 | 数据类型 |
| `format` | 输入 | 滤波器布局 Format 的类型。 `ACDNN_TENSOR_NCHW` 时：4D 布局为 KCRS（K=输出特征图数， C=输入特征图数， R=行数， S=列数），3D 省略 S，5D+ 高维紧跟 RS 之后。 `ACDNN_TENSOR_NHWC` 时：4D 布局为 KRSC，3D 省略 S 且 C 紧跟 R，5D+ 高维插入在 S 和 C 之间。参见 [`acdnnTensorFormat_t`](#21221-acdnntensorformat_t) |
| `nbDims` | 输入 | 滤波器的维度数 |
| `filterDimA` | 输入 | 维度为 `nbDims` 的数组，包含每个维度的滤波器大小 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：数组 `filterDimA` 的元素中至少有一个为负数，或 `dataType` 或 `format` 具有无效的枚举值。
- `ACDNN_STATUS_NOT_SUPPORTED`：参数 `nbDims` 超过 `ACDNN_DIM_MAX`。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.62. acdnnSetLRNDescriptor() {#2262-acdnnsetlrndescriptor}

初始化已创建的 LRN 描述符。

```cpp
acdnnStatus_t acdnnSetLRNDescriptor(
    acdnnLRNDescriptor_t normDesc,
    unsigned lrnN,
    double lrnAlpha,
    double lrnBeta,
    double lrnK);
```

!!! note
    `acdnn.h` 中定义的宏 `ACDNN_LRN_MIN_N`、`ACDNN_LRN_MAX_N`、`ACDNN_LRN_MIN_K`、`ACDNN_LRN_MIN_BETA` 指定参数的有效范围。Double 参数的值在计算期间将被强制转换为 Tensor 数据类型。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `normDesc` | 输出 | 指向已创建的局部响应归一化描述符的句柄 |
| `lrnN` | 输入 | 归一化窗口宽度（以元素为单位）。LRN 层使用窗口 `[center - lookBehind, center + lookAhead]`，其中 lookBehind = ⌊(lrnN - 1) / 2⌋ 且 lookAhead = lrnN - lookBehind - 1。例如，当 n=10 时，窗口跨度为 `[k-4, ..., k, ..., k+5]`，总共包含 10 个样本。对于 DivisiveNormalization 层，窗口在所有空间维度（`dimA[2]`、`dimA[3]`、`dimA[4]`）上具有相同的范围。默认情况下， `lrnN` 在 `acdnnCreateLRNDescriptor()` 中设置为 5 |
| `lrnAlpha` | 输入 | 归一化公式中 Alpha 方差缩放参数的值。在库代码内部，此值对于 LRN 除以窗口宽度，对于 DivisiveNormalization 除以（窗口宽度）^#空间维度数。默认情况下，此值在 `acdnnCreateLRNDescriptor()` 中设置为 1e-4 |
| `lrnBeta` | 输入 | 归一化公式中 Beta 幂参数的值。默认情况下，此值在 `acdnnCreateLRNDescriptor()` 中设置为 0.75 |
| `lrnK` | 输入 | 归一化公式中 K 参数的值。默认情况下，此值设置为 2.0 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：输入参数之一超出上述有效范围。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.63. acdnnSetOpTensorDescriptor() {#2263-acdnnsetoptensordescriptor}

初始化张量逐点运算描述符。

```cpp
acdnnStatus_t acdnnSetOpTensorDescriptor(
    acdnnOpTensorDescriptor_t opTensorDesc,
    acdnnOpTensorOp_t opTensorOp,
    acdnnDataType_t opTensorCompType,
    acdnnNanPropagation_t opTensorNanOpt);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `opTensorDesc` | 输出 | 指向保存张量逐点运算描述符的结构体的指针 |
| `opTensorOp` | 输入 | 张量逐点数学运算描述符的运算类型 |
| `opTensorCompType` | 输入 | 张量逐点数学运算描述符的计算数据类型 |
| `opTensorNanOpt` | 输入 | NaN 传播策略 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：传递的输入参数中至少有一个无效。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.64. acdnnSetPooling2dDescriptor() {#2264-acdnnsetpooling2ddescriptor}

将已创建的池化描述符初始化为 2D 配置。

```cpp
acdnnStatus_t acdnnSetPooling2dDescriptor(
    acdnnPoolingDescriptor_t poolingDesc,
    acdnnPoolingMode_t mode,
    acdnnNanPropagation_t maxpoolingNanOpt,
    int windowHeight,
    int windowWidth,
    int verticalPadding,
    int horizontalPadding,
    int verticalStride,
    int horizontalStride);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `poolingDesc` | 输入/输出 | 指向已创建池化描述符的句柄 |
| `mode` | 输入 | 指定池化模式的枚举值 |
| `maxpoolingNanOpt` | 输入 | 指定 NaN 传播模式的枚举值。当前版本仅支持 `ACDNN_NOT_PROPAGATE_NAN` |
| `windowHeight` | 输入 | 池化窗口的高度 |
| `windowWidth` | 输入 | 池化窗口的宽度 |
| `verticalPadding` | 输入 | 垂直填充大小 |
| `horizontalPadding` | 输入 | 水平填充大小 |
| `verticalStride` | 输入 | 池化垂直步幅 |
| `horizontalStride` | 输入 | 池化水平步幅 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：参数 `windowHeight`、`windowWidth`、`verticalStride`、`horizontalStride` 中至少有一个为负数，或 `mode` 或 `maxpoolingNanOpt` 具有无效的枚举值。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.65. acdnnSetPoolingNdDescriptor() {#2265-acdnnsetpoolingnddescriptor}

初始化已创建的 Nd 池化描述符。

```cpp
acdnnStatus_t acdnnSetPoolingNdDescriptor(
    acdnnPoolingDescriptor_t poolingDesc,
    const acdnnPoolingMode_t mode,
    const acdnnNanPropagation_t maxpoolingNanOpt,
    int nbDims,
    const int windowDimA[],
    const int paddingA[],
    const int strideA[]);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `poolingDesc` | 输入/输出 | 指向已创建池化描述符的句柄 |
| `mode` | 输入 | 指定池化模式的枚举值 |
| `maxpoolingNanOpt` | 输入 | 指定 NaN 传播模式的枚举值。当前版本仅支持 `ACDNN_NOT_PROPAGATE_NAN` |
| `nbDims` | 输入 | 池化运算的维度数，须大于零 |
| `windowDimA` | 输入 | 维度为 `nbDims` 的数组，包含各维度的窗口大小。数组元素值须大于零 |
| `paddingA` | 输入 | 维度为 `nbDims` 的数组，包含各维度的填充大小。允许负填充 |
| `strideA` | 输入 | 维度为 `nbDims` 的数组，包含各维度的步幅大小。数组元素值须大于零（即不允许负步幅） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：`如果（nbDims > ACDNN_DIM_MAX-2）`。
- `ACDNN_STATUS_BAD_PARAM`：`nbDims` 或数组 `windowDimA` 或 `strideA` 的元素中至少有一个为负数，或 `mode` 或 `maxpoolingNanOpt` 具有无效的枚举值。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.66. acdnnSetReduceTensorDescriptor() {#2266-acdnnsetreducetensordescriptor}

初始化已创建的张量归约描述符。

```cpp
acdnnStatus_t acdnnSetReduceTensorDescriptor(
  acdnnReduceTensorDescriptor_t reduceTensorDesc,
  acdnnReduceTensorOp_t reduceTensorOp,
  acdnnDataType_t reduceTensorCompType,
  acdnnNanPropagation_t reduceTensorNanOpt,
  acdnnReduceTensorIndices_t reduceTensorIndices,
  acdnnIndicesType_t reduceTensorIndicesType);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `reduceTensorDesc` | 输入/输出 | 指向已创建归约张量描述符的句柄 |
| `reduceTensorOp` | 输入 | 指定归约张量运算的枚举值 |
| `reduceTensorCompType` | 输入 | 指定归约计算数据类型的枚举值 |
| `reduceTensorNanOpt` | 输入 | 指定 NaN 传播模式的枚举值 |
| `reduceTensorIndices` | 输入 | 指定归约张量索引的枚举值 |
| `reduceTensorIndicesType` | 输入 | 指定归约张量索引类型的枚举值 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`reduceTensorDesc` 为 NULL（`reduceTensorOp`、`reduceTensorCompType`、`reduceTensorNanOpt`、`reduceTensorIndices` 或 `reduceTensorIndicesType` 具有无效的枚举值）。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.67. acdnnSetSpatialTransformerNdDescriptor() {#2267-acdnnsetspatialtransformernddescriptor}

初始化已创建的空间变换器描述符。

```cpp
acdnnStatus_t acdnnSetSpatialTransformerNdDescriptor(
  acdnnSpatialTransformerDescriptor_t stDesc,
  acdnnSamplerType_t samplerType,
  acdnnDataType_t dataType,
  const int nbDims,
  const int dimA[]);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `stDesc` | 输入/输出 | 已创建的空间变换器描述符对象 |
| `samplerType` | 输入 | 指定采样器类型的枚举值 |
| `dataType` | 输入 | 数据类型 |
| `nbDims` | 输入 | 变换后张量的维度数 |
| `dimA` | 输入 | 维度为 `nbDims` 的数组，包含变换后张量各维度的大小 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：满足以下至少一个条件：
  - `stDesc` 或 `dimA` 为 NULL
  - `dataType` 或 `samplerType` 具有无效的枚举值

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.68. acdnnSetStream() {#2268-acdnnsetstream}

为 acDNN 句柄绑定用户 HGGC Stream。后续 kernel 将在此 stream 上启动，或在内部 stream 启动时与之同步。若未设置 acDNN 库 Stream，则所有 Kernel 使用默认（NULL）Stream。在 acDNN 句柄中设置用户 Stream 可确保 acDNN 调用与同一 Stream 中启动的其他真武 PPU Kernel 按提交顺序执行。

```cpp
acdnnStatus_t acdnnSetStream(
    acdnnHandle_t handle,
    hggcStream_t streamId);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | 指向 acDNN 句柄的指针 |
| `streamId` | 输入 | 要写入 acDNN 句柄的新 HGGC Stream |

返回码：

- `ACDNN_STATUS_BAD_PARAM`：无效（NULL）句柄。
- `ACDNN_STATUS_MAPPING_ERROR`：用户 Stream 与 acDNN 句柄上下文不匹配。
- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.69. acdnnSetTensor4dDescriptor() {#2269-acdnnsettensor4ddescriptor}

将已创建的张量描述符初始化为 4D 张量，步幅从 `format` 推断，确保数据在内存中连续、维度间无填充。

```cpp
acdnnStatus_t acdnnSetTensor4dDescriptor(
  acdnnTensorDescriptor_t tensorDesc,
  acdnnTensorFormat_t format,
  acdnnDataType_t dataType,
  int n,
  int c,
  int h,
  int w);
```

张量的总大小（包括维度间的潜在填充）限制为 20 亿个数据类型的元素。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `tensorDesc` | 输入/输出 | 指向已创建张量描述符的句柄 |
| `format` | 输入 | 格式类型 |
| `dataType` | 输入 | 数据类型 |
| `n` | 输入 | 图像数量 |
| `c` | 输入 | 每张图像的特征图数量 |
| `h` | 输入 | 每个特征图的高度 |
| `w` | 输入 | 每个特征图的宽度 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：参数 n、c、h、w 中至少有一个为负数，或 `format` 具有无效的枚举值，或 `dataType` 具有无效的枚举值。
- `ACDNN_STATUS_NOT_SUPPORTED`：张量描述符的总大小超过 20 亿个元素的最大限制。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.70. acdnnSetTensor4dDescriptorEx() {#2270-acdnnsettensor4ddescriptorex}

将已创建的张量描述符初始化为 4D 张量（类似 `acdnnSetTensor4dDescriptor()` 但步幅显式传入）。可用于任意顺序布局 4D 张量，或仅定义维度间的间隔。

```cpp
acdnnStatus_t acdnnSetTensor4dDescriptorEx(
    acdnnTensorDescriptor_t tensorDesc,
    acdnnDataType_t dataType,
    int n,
    int c,
    int h,
    int w,
    int nStride,
    int cStride,
    int hStride,
    int wStride);
```

目前，某些 acDNN 函数对步幅的支持有限。若使用具有不受支持步幅的 4D 张量对象，这些函数将返回 `ACDNN_STATUS_NOT_SUPPORTED`。可使用 `acdnnTransformTensor()` 将数据转换为受支持的布局。

张量的总大小（包括维度间的潜在填充）限制为 20 亿个数据类型的元素。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `tensorDesc` | 输入/输出 | 指向已创建的张量描述符的句柄 |
| `dataType` | 输入 | 数据类型 |
| `n` | 输入 | 图像数量 |
| `c` | 输入 | 每个图像的特征图数量 |
| `h` | 输入 | 每个特征图的高度 |
| `w` | 输入 | 每个特征图的宽度 |
| `nStride` | 输入 | 两张连续图像间的步幅 |
| `cStride` | 输入 | 两个连续特征图间的步幅 |
| `hStride` | 输入 | 两连续行间的步幅 |
| `wStride` | 输入 | 两连续列间的步幅 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：参数 n、c、h、w 或 `nStride`、`cStride`、`hStride`、`wStride` 中至少有一个为负数，或 `dataType` 具有无效的枚举值。
- `ACDNN_STATUS_NOT_SUPPORTED`：张量描述符的总大小超过 20 亿个元素的最大限制。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.71. acdnnSetTensorNdDescriptor() {#2271-acdnnsettensornddescriptor}

初始化已创建的 Nd 张量描述符。

```cpp
acdnnStatus_t acdnnSetTensorNdDescriptor(
    acdnnTensorDescriptor_t tensorDesc,
    acdnnDataType_t dataType,
    int nbDims,
    const int dimA[],
    const int strideA[]);

```

Tensor 的总大小（包括维度之间的潜在填充）限制为 20 亿个数据类型的元素。Tensor 至少为 4 维，最多 `ACDNN_DIM_MAX` 维（在 `acdnn.h` 中定义）。当处理低维数据时，建议开发者创建 4D Tensor，并将未使用维度的大小设置为 1。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `tensorDesc` | 输入/输出 | 指向已创建的张量描述符的句柄 |
| `dataType` | 输入 | 数据类型 |
| `nbDims` | 输入 | 张量的维度数 |
| `dimA` | 输入 | 维度为 `nbDims` 的数组，包含每个维度的 Tensor 大小。沿未使用维度的大小应设置为 1。按照惯例，数组中维度的顺序遵循 Format - [N, C, D, H, W]，其中 W 占据数组中的最小索引 |
| `strideA` | 输入 | 维度为 `nbDims` 的数组，包含每个维度的 Tensor 步幅。按照惯例，数组中步幅的顺序遵循 Format - [Nstride, Cstride, Dstride, Hstride, Wstride]，其中 Wstride 占据数组中的最小索引 |

!!! note
    勿使用 2 维（历史原因：滤波器描述符最小维度数为 3）。

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：数组 `dimA` 的元素中至少有一个为负数或零，或 `dataType` 具有无效的枚举值。
- `ACDNN_STATUS_NOT_SUPPORTED`：参数 `nbDims` 超出范围 [4, `ACDNN_DIM_MAX`]，或张量描述符的总大小超过 20 亿个元素的最大限制。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.72. acdnnSetTensorNdDescriptorEx() {#2272-acdnnsettensornddescriptorex}

初始化 Nd 张量描述符（显式设置步幅）。

```cpp
acdnnStatus_t acdnnSetTensorNdDescriptorEx(
    acdnnTensorDescriptor_t tensorDesc,
    acdnnTensorFormat_t format,
    acdnnDataType_t dataType,
    int nbDims,
    const int dimA[]);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `tensorDesc` | 输出 | 指向要初始化的张量描述符结构体的指针 |
| `format` | 输入 | 张量格式 |
| `dataType` | 输入 | 张量数据类型 |
| `nbDims` | 输入 | 张量的维度数 |
| `dimA` | 输入 | 包含各维度大小的数组 |

!!! note
    勿使用 2 维（历史原因：滤波器描述符最小维度数为 3）。

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：张量描述符未正确分配；或输入参数设置不正确。
- `ACDNN_STATUS_NOT_SUPPORTED`：请求的维度大小大于支持的最大维度大小。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.73. acdnnSetTensorTransformDescriptor() {#2273-acdnnsettensortransformdescriptor}

初始化先前创建的张量变换描述符。

```cpp
acdnnStatus_t acdnnSetTensorTransformDescriptor(
    acdnnTensorTransformDescriptor_t transformDesc,
    const uint32_t nbDims,
    const acdnnTensorFormat_t destFormat,
    const int32_t padBeforeA[],
    const int32_t padAfterA[],
    const uint32_t foldA[],
    const acdnnFoldingDirection_t direction);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `transformDesc` | 输出 | 要初始化的张量变换描述符 |
| `nbDims` | 输入 | 变换操作数的维度数，须大于 2 |
| `destFormat` | 输入 | 期望的目标格式 |
| `padBeforeA[]` | 输入 | 包含各维度前应添加的填充量的数组。设为 NULL 表示无填充 |
| `padAfterA[]` | 输入 | 包含各维度后应添加的填充量的数组。设为 NULL 表示无填充 |
| `foldA[]` | 输入 | 包含各空间维度（维度 2 及以上）折叠参数的数组。设为 NULL 表示无折叠 |
| `direction` | 输入 | 选择折叠或展开。当折叠参数均 `<= 1` 时，此输入无效 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：参数 `transformDesc` 为 `NULL`，或 `direction` 无效，或 `nbDims <= 2`。
- `ACDNN_STATUS_NOT_SUPPORTED`：如果请求的维度大小大于支持的最大维度大小（即 `nbDims` 之一大于 `ACDNN_DIM_MAX`），或 `destFormat` 不是 `NCHW` 或 `NHWC`。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.74. acdnnSoftmaxForward() {#2274-acdnnsoftmaxforward}

计算 Softmax。

```cpp
acdnnStatus_t acdnnSoftmaxForward(
    acdnnHandle_t handle,
    acdnnSoftmaxAlgorithm_t algorithm,
    acdnnSoftmaxMode_t mode,
    const void *alpha,
    const acdnnTensorDescriptor_t xDesc,
    const void *x,
    const void *beta,
    const acdnnTensorDescriptor_t yDesc,
    void *y);
```

所有模式和算法的 4D 和 5D 张量均支持所有张量格式。使用 NCHW 完全打包张量时性能最佳。对于超过 5 维的张量，须在空间维度上进行打包。

**支持的数据类型**

支持以下数据类型：

- `ACDNN_DATA_FLOAT`
- `ACDNN_DATA_DOUBLE`
- `ACDNN_DATA_HALF`
- `ACDNN_DATA_BF16`
- `ACDNN_DATA_INT8`

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | 指向已创建 acDNN 上下文的句柄 |
| `algorithm` | 输入 | 指定 Softmax 算法的枚举值 |
| `mode` | 输入 | 指定 Softmax 模式的枚举值 |
| `alpha`,`beta` | 输入 | 指向主机内存中缩放因子的指针，用于将计算结果与输出层中的先前值混合，计算方式如下： `dst = alpha[0]*result + beta[0]*priorDst` |
| `xDesc` | 输入 | 指向已初始化输入张量描述符的句柄 |
| `x` | 输入 | 与张量描述符 `xDesc` 关联的真武 PPU 内存数据指针 |
| `yDesc` | 输入 | 指向已初始化输出张量描述符的句柄 |
| `y` | 输出 | 与输出张量描述符 `yDesc` 关联的真武 PPU 内存数据指针 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：函数不支持提供的配置。
- `ACDNN_STATUS_BAD_PARAM`：满足以下至少一个条件：
  - 输入 Tensor 和输出 Tensor 的维度 n、c、h、w 不同
  - 输入 Tensor 和输出 Tensor 的数据类型不同
  - 参数 `algorithm` 或 `mode` 具有无效的枚举值
- `ACDNN_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.75. acdnnSpatialTfGridGeneratorForward() {#2275-acdnnspatialtfgridgeneratorforward}

根据仿射变换参数 theta 生成空间变换的坐标网格。

```cpp
acdnnStatus_t acdnnSpatialTfGridGeneratorForward(
    acdnnHandle_t handle,
    const acdnnSpatialTransformerDescriptor_t stDesc,
    const void *theta,
    void *grid);
```

仅支持 2D 变换。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | 指向已创建 acDNN 上下文的句柄 |
| `stDesc` | 输入 | 已创建的空间变换器描述符对象 |
| `theta` | 输入 | 仿射变换矩阵。对于 2D 变换，其大小应为 n*2*3，其中 n 是 `stDesc` 中指定的图像数量 |
| `grid` | 输出 | 坐标网格。对于 2D 变换，其大小为 n*h*w*2，其中 n、h、w 在 `stDesc` 中指定。在第 4 维中，第一个坐标是 x，第二个坐标是 y |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：满足以下至少一个条件：
  - `handle` 为 NULL
  - 参数 `grid` 或 `theta` 之一为 NULL
- `ACDNN_STATUS_NOT_SUPPORTED`：函数不支持提供的配置。请参阅以下不支持的配置示例：
  - `stDesc` 中指定的 Transform 后 Tensor 的维度 > 4
- `ACDNN_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.76. acdnnSpatialTfSamplerForward() {#2276-acdnnspatialtfsamplerforward}

使用网格生成器产出的坐标网格对输入张量执行采样，生成输出张量。

```cpp
acdnnStatus_t acdnnSpatialTfSamplerForward(
    acdnnHandle_t handle,
    const acdnnSpatialTransformerDescriptor_t stDesc,
    const void *alpha,
    const acdnnTensorDescriptor_t xDesc,
    const void *x,
    const void *grid,
    const void *beta,
    const acdnnTensorDescriptor_t yDesc,
    void *y);
```

仅支持 2D 变换。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | 指向已创建 acDNN 上下文的句柄 |
| `stDesc` | 输入 | 已创建的空间变换器描述符对象 |
| `alpha`,`beta` | 输入 | 指向主机内存中缩放因子的指针，用于将源值与目标张量中的先前值混合，计算方式如下： `dst = alpha[0]*src + beta[0]*priorDst` |
| `xDesc` | 输入 | 指向已初始化输入张量描述符的句柄 |
| `x` | 输入 | 与张量描述符 `xDesc` 关联的真武 PPU 内存数据指针 |
| `grid` | 输入 | 由 `acdnnSpatialTfGridGeneratorForward()` 生成的坐标网格 |
| `yDesc` | 输入 | 指向已初始化输出张量描述符的句柄 |
| `y` | 输出 | 与输出张量描述符 `yDesc` 关联的真武 PPU 内存数据指针 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：满足以下至少一个条件：
  - `handle` 为 NULL
  - 参数 `x`、`y` 或 `grid` 之一为 NULL
- `ACDNN_STATUS_NOT_SUPPORTED`：函数不支持提供的配置。请参阅以下不支持的配置示例：Transform 后 Tensor 的 `维度 > 4`。
- `ACDNN_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.77. acdnnTransformFilter() {#2277-acdnntransformfilter}

在不同格式、数据类型或维度之间转换滤波器，可将不受支持的布局格式转换为受支持的格式。

```cpp
acdnnStatus_t acdnnTransformFilter(
    acdnnHandle_t handle,
    const acdnnTensorTransformDescriptor_t transDesc,
    const void *alpha,
    const acdnnFilterDescriptor_t srcDesc,
    const void *srcData,
    const void *beta,
    const acdnnFilterDescriptor_t destDesc,
    void *destData);
```

将缩放后的数据从输入滤波器 `srcDesc` 复制到不同布局的输出 `destDesc`。若 `srcDesc` 和 `destDesc` 的滤波器描述符具有不同的维度，它们须与 `transDesc` 中指定的折叠和填充量及顺序一致。

`srcDesc` 和 `destDesc` 张量不得以任何方式重叠（即，张量不可进行原地变换）。

!!! note
    执行折叠变换或零填充变换时，缩放因子（alpha, beta）应设置为（1, 0）。但，展开变换支持任意（alpha, beta）值，此函数是线程安全的。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | 指向已创建的 acDNN 上下文的句柄 |
| `transDesc` | 输入 | 包含请求的滤波器变换详细信息的描述符 |
| `alpha`,`beta` | 输入 | 主机内存中指向缩放因子的指针，用于缩放输入张量 `srcDesc` 中的数据。beta 用于缩放目标张量，而 alpha 用于缩放源张量 |
| `srcDesc`,`destDesc` | 输入 | 指向已初始化的滤波器描述符的句柄。 `srcDesc` 和 `destDesc` 不得重叠 |
| `srcData` | 输入 | 主机内存中指向由 `srcDesc` 描述的张量数据的指针 |
| `destData` | 输出 | 主机内存中指向由 `destDesc` 描述的张量数据的指针 |

在折叠和零填充情况下，beta 缩放值将被忽略。展开支持任何（alpha, beta）。

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：参数未初始化或初始化不正确，或 `srcDesc` 和 `destDesc` 之间的维度数不同。
- `ACDNN_STATUS_NOT_SUPPORTED`：函数不支持提供的配置，此外，在折叠和填充路径中，除 A = 1 和 B = 0 之外的任何值都将导致 `ACDNN_STATUS_NOT_SUPPORTED`。
- `ACDNN_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.78. acdnnTransformTensor() {#2278-acdnntransformtensor}

将缩放后的数据从一个张量复制到不同布局的另一个张量。描述符须具有相同的维度，但不要求相同的步幅。输入和输出张量不得以任何方式重叠（即，张量不可进行原地变换）。此函数可用于将具有不受支持格式的张量转换为受支持的格式。

```cpp
acdnnStatus_t acdnnTransformTensor(
    acdnnHandle_t handle,
    const void *alpha,
    const acdnnTensorDescriptor_t xDesc,
    const void *x,
    const void *beta,
    const acdnnTensorDescriptor_t yDesc,
    void *y);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | 指向已创建的 acDNN 上下文的句柄 |
| `alpha`,`beta` | 输入 | 指向缩放因子（位于主机内存）的指针，用于将源值与目标张量中的先前值进行混合，计算方式如下： `dst = alpha[0]*src + beta[0]*priorDst` |
| `xDesc` | 输入 | 指向已初始化的张量描述符的句柄 |
| `x` | 输入 | 指向由 `xDesc` 描述符描述的 Tensor 数据的指针 |
| `yDesc` | 输入 | 指向已初始化的张量描述符的句柄 |
| `y` | 输出 | 指向由 `yDesc` 描述符描述的 Tensor 数据的指针 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：函数不支持提供的配置。
- `ACDNN_STATUS_BAD_PARAM`：两个张量描述符的维度 n、c、h、w 或 `dataType` 不同。
- `ACDNN_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 2.2.79. acdnnTransformTensorEx() {#2279-acdnntransformtensorex}

在不同格式之间转换张量布局，可将不受支持的布局格式转换为受支持的布局 Format 的 Tensor。

```cpp
acdnnStatus_t acdnnTransformTensorEx(
    acdnnHandle_t handle,
    const acdnnTensorTransformDescriptor_t transDesc,
    const void *alpha,
    const acdnnTensorDescriptor_t srcDesc,
    const void *srcData,
    const void *beta,
    const acdnnTensorDescriptor_t destDesc,
    void *destData);
```

将缩放后的数据从输入张量 `srcDesc` 复制到不同布局的输出张量 `destDesc`。 `srcDesc` 和 `destDesc` 的张量描述符应具有相同的维度，但不需要具有相同的步幅。

`srcDesc` 和 `destDesc` 张量不得以任何方式重叠（即，张量不可进行原地变换）。

!!! note
    执行折叠变换或零填充变换时，缩放因子（alpha, beta）应设置为（1, 0）。但，展开变换支持任意（alpha, beta）值，此函数是线程安全的。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | 指向已创建的 acDNN 上下文的句柄 |
| `transDesc` | 输入 | 包含请求的张量变换详细信息的描述符 |
| `alpha`,`beta` | 输入 | 主机内存中指向缩放因子的指针，用于缩放输入张量 `srcDesc` 中的数据。beta 用于缩放目标张量，而 alpha 用于缩放源张量 |
| `srcDesc`,`destDesc` | 输入 | 指向已初始化的张量描述符的句柄。 `srcDesc` 和 `destDesc` 不得重叠 |
| `srcData` | 输入 | 主机内存中指向由 `srcDesc` 描述的张量数据的指针 |
| `destData` | 输出 | 主机内存中指向由 `destDesc` 描述的张量数据的指针 |

在折叠和零填充情况下，beta 缩放值将被忽略。展开支持任何（alpha, beta）。

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：参数未初始化或初始化不正确，或 `srcDesc` 和 `destDesc` 之间的维度数不同。
- `ACDNN_STATUS_NOT_SUPPORTED`：函数不支持提供的配置，此外，在折叠和填充路径中，除 A = 1 和 B = 0 之外的任何值都将导致 `ACDNN_STATUS_NOT_SUPPORTED`。
- `ACDNN_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

### 2.3. 训练 API {#23-训练-api}

`acdnn_ops_train.so` 的完整公开 API。多数反向算子的输出都按 `dst = α·result + β·priorDst` 混合。下文凡出现 `alpha` / `beta` 均隐含此语义，不再逐一重述。

#### 2.3.1. acdnnActivationBackward() {#231-acdnnactivationbackward}

```cpp
acdnnStatus_t acdnnActivationBackward(
    acdnnHandle_t handle,
    acdnnActivationDescriptor_t activationDesc,
    const void *alpha,
    const acdnnTensorDescriptor_t yDesc,
    const void *y,
    const acdnnTensorDescriptor_t dyDesc,
    const void *dy,
    const acdnnTensorDescriptor_t xDesc,
    const void *x,
    const void *beta,
    const acdnnTensorDescriptor_t dxDesc,
    void *dx);
```

激活函数 `acdnnActivationForward()` 的反向。根据前向输出 `y`、前向输入 `x` 以及上层梯度 `dy` 计算输入梯度 `dx`，按 `α·grad + β·prevDx` 写回。

**形状与性能要点**

- 支持所有 4D / 5D 张量格式；超过 5D 须空间维 packing。
- `yDesc` 与 `xDesc` 步幅一致且 HW 维 packing 时性能最佳。
- 支持原地（`dy == dx`），但要求两描述符完全一致（含步幅）。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `activationDesc` | 输入 | 激活配置（`acdnnActivationDescriptor_t`） |
| `alpha` / `beta` | 输入 | 主机端混合系数 |
| `yDesc` / `y` | 输入 | 前向输出张量描述符 / 设备数据指针 |
| `dyDesc` / `dy` | 输入 | 上层梯度张量描述符 / 设备数据指针 |
| `xDesc` / `x` | 输入 | 前向输入张量描述符 / 设备数据指针 |
| `dxDesc` / `dx` | 输入/输出 | 输出梯度张量描述符 / 设备数据指针 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：输入/输出微分张量步幅不匹配、维度不一致等。
- `ACDNN_STATUS_NOT_SUPPORTED`：入参组合不支持，如输入/输出维度不一致。
- `ACDNN_STATUS_EXECUTION_FAILED`：真武 PPU kernel 启动失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 2.3.2. acdnnBatchNormalizationBackward() {#232-acdnnbatchnormalizationbackward}

```cpp
acdnnStatus_t acdnnBatchNormalizationBackward(
    acdnnHandle_t handle,
    acdnnBatchNormMode_t mode,
    const void *alphaDataDiff,
    const void *betaDataDiff,
    const void *alphaParamDiff,
    const void *betaParamDiff,
    const acdnnTensorDescriptor_t xDesc,
    const void *x,
    const acdnnTensorDescriptor_t dyDesc,
    const void *dy,
    const acdnnTensorDescriptor_t dxDesc,
    void *dx,
    const acdnnTensorDescriptor_t bnScaleBiasDiffDesc,
    const void *bnScale,
    void *resultBnScaleDiff,
    void *resultBnBiasDiff,
    double epsilon,
    const void *savedMean,
    const void *savedInvVariance);
```

批归一化的反向。根据前向输入 `x` 和上层梯度 `dy`，计算输入梯度 `dx` 以及 scale / bias 的梯度 `resultBnScaleDiff` / `resultBnBiasDiff`。对应论文 *批归一化：Accelerating Deep 网络训练 by Reducing Internal Covariate Shift*。

**形状与性能要点**

- 仅支持 4D / 5D 张量。
- `x`、`dy`、`dx` 均使用 HW packing 时性能更佳。
- 训练、反向传播和推理中 `epsilon` 须保持一致。
- `bnScaleBiasDiffDesc` 可通过 `acdnnDeriveBNTensorDescriptor()` 派生。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `mode` | 输入 | Spatial 或 Per-Activation（`acdnnBatchNormMode_t`） |
| `alphaDataDiff` / `betaDataDiff` | 输入 | `dx` 的主机端混合系数： `dx = αD·grad + βD·prevDx`。当前版本仅支持 alpha=1, beta=0 |
| `alphaParamDiff` / `betaParamDiff` | 输入 | scale/bias 梯度的主机端混合系数。当前版本仅支持 alpha=1, beta=0 |
| `xDesc` / `x` | 输入 | 前向输入张量描述符 / 设备数据指针 |
| `dyDesc` / `dy` | 输入 | 上层梯度张量描述符 / 设备数据指针 |
| `dxDesc` / `dx` | 输入/输出 | 输出梯度张量描述符 / 设备数据指针 |
| `bnScaleBiasDiffDesc` | 输入 | scale / bias / mean / variance 梯度的共享张量描述符（FP16/FP32 输入时须 Float，FP64 输入时须 Double） |
| `bnScale` | 输入 | BN 的 scale 参数（论文 γ），设备内存；反向不需要 `bnBias` |
| `resultBnScaleDiff` | 输出 | scale 梯度，设备内存 |
| `resultBnBiasDiff` | 输出 | bias 梯度，设备内存 |
| `epsilon` | 输入 | BN 公式中的 ε，须 ≥ `ACDNN_BN_MIN_EPSILON` |
| `savedMean` / `savedInvVariance` | 输入 | 前向保存的中间统计量（可选缓存，均可为 NULL 但须同时为 NULL；使用缓存可加速反向） |

**支持的数据类型组合**

| 配置代号 | `xDesc` | `bnScaleBiasMeanVar` | `alpha, beta` | `dxDesc` |
| :--- | :--- | :--- | :--- | :--- |
| `PSEUDO_HALF_CONFIG` | `ACDNN_DATA_HALF` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_HALF` |
| `FLOAT_CONFIG` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` |
| `DOUBLE_CONFIG` | `ACDNN_DATA_DOUBLE` | `ACDNN_DATA_DOUBLE` | `ACDNN_DATA_DOUBLE` | `ACDNN_DATA_DOUBLE` |
| `PSEUDO_BFLOAT16_CONFIG` | `ACDNN_DATA_BF16` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_BF16` |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：入参组合不支持。
- `ACDNN_STATUS_BAD_PARAM`：必要指针为 NULL、描述符维度不匹配等。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 2.3.3. acdnnBatchNormalizationBackwardEx() {#233-acdnnbatchnormalizationbackwardex}

扩展反向 BN：支持融合 BN+Activation 或 BN+Add+Activation 的反向，并可启用 NHWC 半持久化快速路径。

```cpp
acdnnStatus_t acdnnBatchNormalizationBackwardEx(
acdnnHandle_t handle,
  acdnnBatchNormMode_t mode,
  acdnnBatchNormOps_t bnOps,
  const void *alphaDataDiff,
  const void *betaDataDiff,
  const void *alphaParamDiff,
  const void *betaParamDiff,
  const acdnnTensorDescriptor_t xDesc,
  const void *xData,
  const acdnnTensorDescriptor_t yDesc,
  const void *yData,
  const acdnnTensorDescriptor_t dyDesc,
  const void *dyData,
  const acdnnTensorDescriptor_t dzDesc,
  void *dzData,
  const acdnnTensorDescriptor_t dxDesc,
  void *dxData,
  const acdnnTensorDescriptor_t dBnScaleBiasDesc,
  const void *bnScaleData,
  const void *bnBiasData,
  void *dBnScaleData,
  void *dBnBiasData,
  double epsilon,
  const void *savedMean,
  const void *savedInvVariance,
  const acdnnActivationDescriptor_t activationDesc,
  void *workspace,
  size_t workspaceSizeInBytes,
  void *reserveSpace,
  size_t reserveSpaceSizeInBytes);
```

**形状与性能要点**

- 仅支持 4D / 5D 张量；前向、反向、推理须用相同 ε。
- `bnOps` 控制融合范围：仅 BN / BN+Activation / BN+Add+Activation。
- 当 `workspace = NULL` 且 `workspaceSizeInBytes = 0` 时，退化为 `acdnnBatchNormalizationBackward()`。
- 触发 NHWC 半持久化快速路径的条件：全部张量 NHWC 全打包 + `ACDNN_DATA_HALF` + `SPATIAL_PERSISTENT` 模式 + 工作空间足够大 + reserveSpace 足够大；若 `bnOps=BN_ADD_ACTIVATION`，C 维须为 4 的倍数。
- NCHW 布局下对 x/dy/dx 使用 HW 打包可提升性能。
- `reserveSpace` 须保留前向 `acdnnBatchNormalizationForwardTrainingEx()` 写入的内容；工作空间无需跨 pass 保持。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `mode` | 输入 | 归一化模式（`acdnnBatchNormMode_t`） |
| `bnOps` | 输入 | 融合操作选择（`acdnnBatchNormOps_t`） |
| `alphaDataDiff` / `betaDataDiff` | 输入 | 主机端混合系数，用于 `dx`： `dx = α·grad + β·priorDx` |
| `alphaParamDiff` / `betaParamDiff` | 输入 | 主机端混合系数，用于 `dBnScale` / `dBnBias` |
| `xDesc` / `xData` | 输入 | 前向输入张量描述符 / 设备指针 |
| `yDesc` / `yData` | 输入 | 前向输出张量； `bnOps=BN` 时可传 NULL |
| `dyDesc` / `dyData` | 输入 | 上游梯度张量 |
| `dzDesc` / `dzData` | 输出 | 中间梯度输出； `bnOps` 为 BN 或 BN_ACTIVATION 时可传 NULL |
| `dxDesc` / `dxData` | 输出 | 输入梯度输出 |
| `dBnScaleBiasDesc` | 输入 | scale/bias/mean/invVar 的共享描述符（FP16/FP32→Float，FP64→Double；由 `acdnnDeriveBNTensorDescriptor()` 生成） |
| `bnScaleData` | 输入 | BN scale 参数（γ），设备内存 |
| `bnBiasData` | 输入 | BN bias 参数（β），仅融合激活时使用 |
| `dBnScaleData` / `dBnBiasData` | 输出 | scale 和 bias 的梯度，设备内存 |
| `epsilon` | 输入 | BN 公式 ε，须 ≥ `ACDNN_BN_MIN_EPSILON`，前向反向须一致 |
| `savedMean` / `savedInvVariance` | 输入 | 前向缓存的均值/逆方差（可选；均可 NULL 但须同时为 NULL） |
| `activationDesc` | 输入 | 激活描述符； `bnOps` 未融合激活时可传 NULL |
| `workspace` | 输入 | 设备工作空间指针（NULL 时退化为非扩展版本） |
| `workspaceSizeInBytes` | 输入 | 工作空间字节数（须 ≥ `acdnnGetBatchNormalizationBackwardExWorkspaceSize()` 返回值） |
| `reserveSpace` | 输入 | 预留空间指针（须保留前向写入内容） |
| `reserveSpaceSizeInBytes` | 输入 | 预留空间字节数（须 ≥ `acdnnGetBatchNormalizationTrainingExReserveSpaceSize()` 返回值） |

**支持的数据类型组合**

| 配置代号 | `xDesc` | `bnScaleBiasMeanVar` | `alpha, beta` | `yDesc` |
| :--- | :--- | :--- | :--- | :--- |
| `PSEUDO_HALF_CONFIG` | `ACDNN_DATA_HALF` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_HALF` |
| `FLOAT_CONFIG` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` |
| `DOUBLE_CONFIG` | `ACDNN_DATA_DOUBLE` | `ACDNN_DATA_DOUBLE` | `ACDNN_DATA_DOUBLE` | `ACDNN_DATA_DOUBLE` |
| `PSEUDO_BFLOAT16_CONFIG` | `ACDNN_DATA_BF16` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_BF16` |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：配置不支持。
- `ACDNN_STATUS_BAD_PARAM`：必要指针为 NULL、维度不匹配等。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 2.3.4. acdnnBatchNormalizationForwardTraining() {#234-acdnnbatchnormalizationforwardtraining}

前向训练阶段的批归一化：计算当前 mini-batch 的均值/方差并输出归一化结果，同时更新移动平均统计量。

```cpp
acdnnStatus_t acdnnBatchNormalizationForwardTraining(
    acdnnHandle_t handle,
    acdnnBatchNormMode_t mode,
    const void *alpha,
    const void *beta,
    const acdnnTensorDescriptor_t xDesc,
    const void *x,
    const acdnnTensorDescriptor_t yDesc,
    void *y,
    const acdnnTensorDescriptor_t bnScaleBiasMeanVarDesc,
    const void *bnScale,
    const void *bnBias,
    double exponentialAverageFactor,
    void *resultRunningMean,
    void *resultRunningVariance,
    double epsilon,
    void *resultSaveMean,
    void *resultSaveInvVariance);
```

**形状与性能要点**

- 仅支持 4D / 5D 张量；ε 须在训练、反向、推理三阶段保持一致。
- 推理阶段应改用 `acdnnBatchNormalizationForwardInference()`。
- x / y 均使用 HW 打包布局可提升性能。
- 辅助描述符由 `acdnnDeriveBNTensorDescriptor()` 生成。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `mode` | 输入 | 归一化模式（`acdnnBatchNormMode_t`） |
| `alpha` / `beta` | 输入 | 主机端混合系数： `y = α·result + β·priorY`。当前版本仅支持 alpha=1, beta=0 |
| `xDesc` / `x` | 输入 | 输入张量描述符 / 设备指针 |
| `yDesc` / `y` | 输入/输出 | 输出张量描述符 / 设备指针 |
| `bnScaleBiasMeanVarDesc` | 输入 | scale/bias/mean/var 共享描述符（维度取决于 mode） |
| `bnScale` / `bnBias` | 输入 | BN scale（γ）和 bias（β），设备内存； `bnBias` 可替代前层 bias 以减少一次加法 |
| `exponentialAverageFactor` | 输入 | 移动平均因子 f： `runningMean = (1-f)·old + f·new`；使用 f=1/(1+N) 可得到累积均值 |
| `resultRunningMean` / `resultRunningVariance` | 输入/输出 | 移动平均统计量（与 scale/bias 同描述符）；均可 NULL 但须同时为 NULL；首次调用前须初始化（0 或合理值） |
| `epsilon` | 输入 | BN 公式 ε，须 ≥ `ACDNN_BN_MIN_EPSILON` |
| `resultSaveMean` / `resultSaveInvVariance` | 输出 | 可选前向缓存，传给反向函数可避免重算统计量（均可 NULL 但须同时为 NULL） |

**支持的数据类型组合**

| 配置代号 | `xDesc` | `bnScaleBiasMeanVar` | `alpha, beta` | `yDesc` |
| :--- | :--- | :--- | :--- | :--- |
| `PSEUDO_HALF_CONFIG` | `ACDNN_DATA_HALF` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_HALF` |
| `FLOAT_CONFIG` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` |
| `DOUBLE_CONFIG` | `ACDNN_DATA_DOUBLE` | `ACDNN_DATA_DOUBLE` | `ACDNN_DATA_DOUBLE` | `ACDNN_DATA_DOUBLE` |
| `PSEUDO_BFLOAT16_CONFIG` | `ACDNN_DATA_BF16` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_BF16` |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：配置不支持。
- `ACDNN_STATUS_BAD_PARAM`：必要指针为 NULL 等。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 2.3.5. acdnnBatchNormalizationForwardTrainingEx() {#235-acdnnbatchnormalizationforwardtrainingex}

扩展前向训练 BN：支持融合 BN+Activation 或 BN+Add+Activation，并可启用 NHWC 半持久化快速路径。

```cpp
acdnnStatus_t acdnnBatchNormalizationForwardTrainingEx(
    acdnnHandle_t handle,
    acdnnBatchNormMode_t mode,
    acdnnBatchNormOps_t bnOps,
    const void *alpha,
    const void *beta,
    const acdnnTensorDescriptor_t xDesc,
    const void *xData,
    const acdnnTensorDescriptor_t zDesc,
    const void *zData,
    const acdnnTensorDescriptor_t yDesc,
    void *yData,
    const acdnnTensorDescriptor_t bnScaleBiasMeanVarDesc,
    const void *bnScaleData,
    const void *bnBiasData,
    double exponentialAverageFactor,
    void *resultRunningMeanData,
    void *resultRunningVarianceData,
    double epsilon,
    void *saveMean,
    void *saveInvVariance,
    const acdnnActivationDescriptor_t activationDesc,
    void *workspace,
    size_t workspaceSizeInBytes,
    void *reserveSpace,
    size_t reserveSpaceSizeInBytes);
```

**形状与性能要点**

- 仅支持 4D / 5D 张量；ε 须在训练、反向、推理三阶段保持一致。
- `bnOps` 控制融合范围：仅 BN / BN+Activation / BN+Add+Activation。
- 当 `workspace = NULL` 且 `workspaceSizeInBytes = 0` 时退化为 `acdnnBatchNormalizationForwardTraining()`。
- NHWC 半持久化快速路径触发条件：全部张量 NHWC 全打包 + `ACDNN_DATA_HALF` + `SPATIAL_PERSISTENT` + 工作空间/reserveSpace 足够大； `BN_ADD_ACTIVATION` 时 C 须为 4 的倍数。
- NCHW 布局下 HW 打包可提升性能。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `mode` | 输入 | 归一化模式（`acdnnBatchNormMode_t`） |
| `bnOps` | 输入 | 融合操作选择（`acdnnBatchNormOps_t`） |
| `alpha` / `beta` | 输入 | 主机端混合系数： `y = α·result + β·priorY`。当前版本仅支持 alpha=1, beta=0 |
| `xDesc` / `xData` | 输入 | 输入张量描述符 / 设备指针 |
| `zDesc` / `zData` | 输入 | 残差加法张量；仅 `BN_ADD_ACTIVATION` 时使用，否则传 NULL；维度须与 x/y 一致 |
| `yDesc` / `yData` | 输入/输出 | 输出张量描述符 / 设备指针 |
| `bnScaleBiasMeanVarDesc` | 输入 | scale/bias/mean/var 共享描述符（维度取决于 mode） |
| `bnScaleData` / `bnBiasData` | 输入 | BN scale（γ）和 bias（β），设备内存 |
| `exponentialAverageFactor` | 输入 | 移动平均因子 f： `running = (1-f)·old + f·new`；f=1/(1+N) 得累积均值 |
| `resultRunningMeanData` / `resultRunningVarianceData` | 输入/输出 | 移动平均统计量；均可 NULL 但须同时为 NULL |
| `epsilon` | 输入 | BN 公式 ε，须 ≥ `ACDNN_BN_MIN_EPSILON` |
| `saveMean` / `saveInvVariance` | 输出 | 可选前向缓存，传给反向可避免重算（均可 NULL 但须同时为 NULL） |
| `activationDesc` | 输入 | 激活描述符； `bnOps` 未融合激活时可传 NULL |
| `workspace` / `workspaceSizeInBytes` | 输入 | 设备工作空间指针及字节数（NULL 时退化为非扩展版本） |
| `reserveSpace` / `reserveSpaceSizeInBytes` | 输入 | 预留空间指针及字节数（须 ≥ `acdnnGetBatchNormalizationTrainingExReserveSpaceSize()` 返回值） |

**支持的数据类型组合**

| 配置代号 | `xDesc` | `bnScaleBiasMeanVar` | `alpha, beta` | `yDesc` |
| :--- | :--- | :--- | :--- | :--- |
| `PSEUDO_HALF_CONFIG` | `ACDNN_DATA_HALF` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_HALF` |
| `FLOAT_CONFIG` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` |
| `DOUBLE_CONFIG` | `ACDNN_DATA_DOUBLE` | `ACDNN_DATA_DOUBLE` | `ACDNN_DATA_DOUBLE` | `ACDNN_DATA_DOUBLE` |
| `PSEUDO_BFLOAT16_CONFIG` | `ACDNN_DATA_BF16` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_BF16` |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：配置不支持。
- `ACDNN_STATUS_BAD_PARAM`：必要指针为 NULL 等。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 2.3.6. acdnnDropoutBackward() {#236-acdnndropoutbackward}

反向 Dropout：将前向传播中未被置零的梯度原样传回，被置零的位置梯度置 0。

```cpp
acdnnStatus_t acdnnDropoutBackward(
acdnnHandle_t handle,
const acdnnDropoutDescriptor_t dropoutDesc,
const acdnnTensorDescriptor_t dyDesc,
const void *dy,
const acdnnTensorDescriptor_t dxDesc,
void *dx,
void *reserveSpace,
size_t reserveSpaceSizeInBytes);
```

全打包张量可获得更高性能。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `dropoutDesc` | 输入 | 已创建的 Dropout 描述符 |
| `dyDesc` / `dy` | 输入 | 上游梯度张量描述符 / 设备指针 |
| `dxDesc` / `dx` | 输出 | 输出梯度张量描述符 / 设备指针 |
| `reserveSpace` | 输入 | 前向 `acdnnDropoutForward()` 写入的预留空间（内容须保持不变） |
| `reserveSpaceSizeInBytes` | 输入 | 预留空间字节数 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：配置不支持。
- `ACDNN_STATUS_BAD_PARAM`：输入/输出元素数不同或类型不匹配等。
- `ACDNN_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 2.3.7. acdnnGetBatchNormalizationBackwardExWorkspaceSize() {#237-acdnngetbatchnormalizationbackwardexworkspacesize}

查询 `acdnnBatchNormalizationBackwardEx()` 所需的工作空间字节数。

```cpp
acdnnStatus_t acdnnGetBatchNormalizationBackwardExWorkspaceSize(
    acdnnHandle_t handle,
    acdnnBatchNormMode_t mode,
    acdnnBatchNormOps_t bnOps,
    const acdnnTensorDescriptor_t xDesc,
    const acdnnTensorDescriptor_t yDesc,
    const acdnnTensorDescriptor_t dyDesc,
    const acdnnTensorDescriptor_t dzDesc,
    const acdnnTensorDescriptor_t dxDesc,
    const acdnnTensorDescriptor_t dBnScaleBiasDesc,
    const acdnnActivationDescriptor_t activationDesc,
    size_t *sizeInBytes);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `mode` | 输入 | 归一化模式 |
| `bnOps` | 输入 | 融合操作选择 |
| `xDesc` / `yDesc` / `dyDesc` / `dzDesc` / `dxDesc` | 输入 | 各张量描述符 |
| `dBnScaleBiasDesc` | 输入 | scale/bias 共享描述符（FP16/FP32→Float，FP64→Double） |
| `activationDesc` | 输入 | 激活描述符；未融合激活时传 NULL |
| `sizeInBytes` | 输出 | 所需工作空间字节数 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：配置不支持。
- `ACDNN_STATUS_BAD_PARAM`：张量维度不在 [4,5] 范围内等。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 2.3.8. acdnnGetBatchNormalizationForwardTrainingExWorkspaceSize() {#238-acdnngetbatchnormalizationforwardtrainingexworkspacesize}

查询 `acdnnBatchNormalizationForwardTrainingEx()` 所需的工作空间字节数。

```cpp
acdnnStatus_t acdnnGetBatchNormalizationForwardTrainingExWorkspaceSize(
    acdnnHandle_t handle,
    acdnnBatchNormMode_t mode,
    acdnnBatchNormOps_t bnOps,
    const acdnnTensorDescriptor_t xDesc,
    const acdnnTensorDescriptor_t zDesc,
    const acdnnTensorDescriptor_t yDesc,
    const acdnnTensorDescriptor_t bnScaleBiasMeanVarDesc,
    const acdnnActivationDescriptor_t activationDesc,
    size_t *sizeInBytes);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `mode` | 输入 | 归一化模式 |
| `bnOps` | 输入 | 融合操作选择 |
| `xDesc` / `zDesc` / `yDesc` | 输入 | 输入、可选残差、输出张量描述符； `zDesc` 仅 `BN_ADD_ACTIVATION` 时需要，否则传 NULL |
| `bnScaleBiasMeanVarDesc` | 输入 | scale/bias 共享描述符 |
| `activationDesc` | 输入 | 激活描述符；未融合激活时传 NULL |
| `sizeInBytes` | 输出 | 所需工作空间字节数 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：配置不支持。
- `ACDNN_STATUS_BAD_PARAM`：张量维度不在 [4,5] 范围内等。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 2.3.9. acdnnGetBatchNormalizationTrainingExReserveSpaceSize() {#239-acdnngetbatchnormalizationtrainingexreservespacesize}

查询扩展 BN 前向/反向共用的预留空间字节数。与工作空间不同，预留空间须在前向与反向之间保持内容不变。

```cpp
acdnnStatus_t acdnnGetBatchNormalizationTrainingExReserveSpaceSize(
    acdnnHandle_t handle,
    acdnnBatchNormMode_t mode,
    acdnnBatchNormOps_t bnOps,
    const acdnnActivationDescriptor_t activationDesc,
    const acdnnTensorDescriptor_t xDesc,
    size_t *sizeInBytes);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `mode` | 输入 | 归一化模式 |
| `bnOps` | 输入 | 融合操作选择 |
| `activationDesc` | 输入 | 激活描述符；未融合激活时传 NULL |
| `xDesc` | 输入 | 输入张量描述符 |
| `sizeInBytes` | 输出 | 所需预留空间字节数 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：配置不支持。
- `ACDNN_STATUS_BAD_PARAM`：张量维度不在 [4,5] 范围内。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 2.3.10. acdnnOpsTrainVersionCheck() {#2310-acdnnopstrainversioncheck}

检查 `acdnn_ops_train` 子库版本是否与其他 acDNN 子库一致。

```cpp
acdnnStatus_t acdnnOpsTrainVersionCheck(void);
```

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 2.3.11. acdnnPoolingBackward() {#2311-acdnnpoolingbackward}

反向池化：根据前向输出和上游梯度计算输入梯度 `dx`。

```cpp
acdnnStatus_t acdnnPoolingBackward(
    acdnnHandle_t handle,
    const acdnnPoolingDescriptor_t poolingDesc,
    const void *alpha,
    const acdnnTensorDescriptor_t yDesc,
    const void *y,
    const acdnnTensorDescriptor_t dyDesc,
    const void *dy,
    const acdnnTensorDescriptor_t xDesc,
    const void *xData,
    const void *beta,
    const acdnnTensorDescriptor_t dxDesc,
    void *dx);
```

**形状与性能要点**

- 仅支持 2D / 3D 空间维度；不支持张量向量化。
- HW 打包张量性能最优。
- 确定性算法（通过 `poolingDesc` 池化模式选择）可能比传统最大池化反向慢 ≤50% 或快 ≤20%。
- 平均池化时 `xDesc`/`x`/`yDesc`/`y` 均可传 NULL（节省内存和带宽）。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `poolingDesc` | 输入 | 池化描述符 |
| `alpha` / `beta` | 输入 | 主机端混合系数： `dx = α·grad + β·priorDx` |
| `yDesc` / `y` | 输入 | 前向输出张量（平均池化时可 NULL） |
| `dyDesc` / `dy` | 输入 | 上游梯度张量（须为 FLOAT/DOUBLE/HALF/BFLOAT16） |
| `xDesc` / `xData` | 输入 | 前向输入张量（平均池化时可 NULL） |
| `dxDesc` / `dx` | 输出 | 输入梯度张量（须为 FLOAT/DOUBLE/HALF/BFLOAT16） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：描述符维度不匹配等。
- `ACDNN_STATUS_NOT_SUPPORTED`：`wStride`≠1 等。
- `ACDNN_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 2.3.12. acdnnSoftmaxBackward() {#2312-acdnnsoftmaxbackward}

反向 Softmax：基于前向输出 `y` 和上游梯度 `dy` 计算输入梯度 `dx`。

```cpp
acdnnStatus_t acdnnSoftmaxBackward(
acdnnHandle_t handle,
acdnnSoftmaxAlgorithm_t algorithm,
acdnnSoftmaxMode_t mode,
const void *alpha,
const acdnnTensorDescriptor_t yDesc,
const void *yData,
const acdnnTensorDescriptor_t dyDesc,
const void *dy,
const void *beta,
const acdnnTensorDescriptor_t dxDesc,
void *dx);
```

**形状与性能要点**

- 支持 4D/5D 张量（所有模式和算法）；>5D 时空间维度须打包。
- NCHW 全打包性能最优。
- 支持原地： `dy` 与 `dx` 可指向同一内存（须 `dyDesc`=`dxDesc` 且步幅相同）。
- 支持类型：FLOAT / DOUBLE / HALF / BFLOAT16。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `algorithm` | 输入 | Softmax 算法枚举 |
| `mode` | 输入 | Softmax 模式枚举 |
| `alpha` / `beta` | 输入 | 主机端混合系数： `dx = α·grad + β·priorDx` |
| `yDesc` / `yData` | 输入 | 前向输出张量描述符 / 设备指针 |
| `dyDesc` / `dy` | 输入 | 上游梯度张量描述符 / 设备指针 |
| `dxDesc` / `dx` | 输出 | 输入梯度张量描述符 / 设备指针 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：配置不支持。
- `ACDNN_STATUS_BAD_PARAM`：描述符维度不匹配等。
- `ACDNN_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 2.3.13. acdnnSpatialTfGridGeneratorBackward() {#2313-acdnnspatialtfgridgeneratorbackward}

反向网格生成：根据网格梯度 `dgrid` 计算变换参数梯度 `dtheta`。仅支持 2D 变换。

```cpp
acdnnStatus_t acdnnSpatialTfGridGeneratorBackward(
    acdnnHandle_t handle,
    const acdnnSpatialTransformerDescriptor_t stDesc,
    const void *dgrid,
    void *dtheta);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `stDesc` | 输入 | 空间变换器描述符 |
| `dgrid` | 输入 | 网格梯度，设备内存 |
| `dtheta` | 输出 | 变换参数梯度，设备内存 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：指针为 NULL 等。
- `ACDNN_STATUS_NOT_SUPPORTED`：变换后`张量维度 > 4` 等。
- `ACDNN_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 2.3.14. acdnnSpatialTfSamplerBackward() {#2314-acdnnspatialtfsamplerbackward}

反向采样：根据输出梯度 `dy` 和坐标网格计算输入梯度 `dx` 及网格梯度 `dgrid`。仅支持 2D 变换。

```cpp
acdnnStatus_t acdnnSpatialTfSamplerBackward(
acdnnHandle_t handle,
const acdnnSpatialTransformerDescriptor_t stDesc,
const void *alpha,
const acdnnTensorDescriptor_t xDesc,
const void *x,
const void *beta,
const acdnnTensorDescriptor_t dxDesc,
void *dx,
const void *alphaDgrid,
const acdnnTensorDescriptor_t dyDesc,
const void *dy,
const void *grid,
const void *betaDgrid,
void *dgrid);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `stDesc` | 输入 | 空间变换器描述符 |
| `alpha` / `beta` | 输入 | 主机端混合系数（用于 `dx`） |
| `xDesc` / `x` | 输入 | 前向输入张量描述符 / 设备指针 |
| `dxDesc` / `dx` | 输出 | 输入梯度张量描述符 / 设备指针 |
| `alphaDgrid` / `betaDgrid` | 输入 | 主机端混合系数（用于 `dgrid`） |
| `dyDesc` / `dy` | 输入 | 上游梯度张量描述符 / 设备指针 |
| `grid` | 输入 | 由 `acdnnSpatialTfGridGeneratorForward()` 生成的坐标网格 |
| `dgrid` | 输出 | 网格梯度，设备内存 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：指针为 NULL 等。
- `ACDNN_STATUS_NOT_SUPPORTED`：变换后`张量维度 > 4` 等。
- `ACDNN_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

**比赛关联：** 本章基础算子是 VLM 推理的基本积木——`acdnnDataType_t` 明确了 BF16/FP16/INT8 支持范围（量化选型依据），`acdnnMathType_t` 控制 Tensor 单元 TF32/降级转换（吞吐与精度的权衡开关）；Softmax、激活（GELU/Swish）直接对应 LLM 解码路径。注意当前版本多数算子仅支持 alpha=1、beta=0，融合规划时不能依赖 α/β 混合。

## 3. 卷积网络 {#3-卷积网络}

本章覆盖卷积神经网络相关的全部算子，卷积、池化、归一化、激活融合等，同时包含前向推理与反向训练。

### 3.1. 数据类型与算法枚举 {#31-数据类型与算法枚举}

本节涉及三类对象：唯一的不透明描述符 `acdnnConvolutionDescriptor_t`、两个性能/启发式结果的结构体（`*AlgoPerf_t`），以及一组列出可选算法和卷积模式的枚举类型。

#### 3.1.1. 指向不透明结构体类型的指针 {#311-指向不透明结构体类型的指针}

##### 3.1.1.1. acdnnConvolutionDescriptor_t {#3111-acdnnconvolutiondescriptor_t}

承载一次卷积运算所需配置（填充、步幅、扩张、模式、数据类型等）的不透明描述符。完整生命周期：

| 阶段 | 接口 |
| :--- | :--- |
| 创建 | `acdnnCreateConvolutionDescriptor()` |
| 初始化 | `acdnnSetConvolution2dDescriptor()` / `acdnnSetConvolutionNdDescriptor()` |
| 销毁 | `acdnnDestroyConvolutionDescriptor()` |

#### 3.1.2. 结构体类型 {#312-结构体类型}

两个 `*AlgoPerf_t` 结构体形态完全一致，分别承载前向 / 后向数据卷积的算法性能或启发式结果，由 `Find*Algorithm()` 与 `Get*Algorithm_v7()` 返回。共同字段如下：

| 字段 | 类型 | 描述 |
| :--- | :--- | :--- |
| `algo` | 算法枚举（`acdnnConvolutionFwdAlgo_t` / `acdnnConvolutionBwdDataAlgo_t`） | 实际运行（或被启发式选中）的算法 |
| `status` | `acdnnStatus_t` | 运行结果，见下文 |
| `time` | `float` | 运行耗时（毫秒） |
| `memory` | `size_t` | 该算法所需工作空间字节数 |
| `determinism` | `acdnnDeterminism_t` | 算法是否可复现 |
| `mathType` | `acdnnMathType_t` | 算法实际选用的精度模式 |
| `reserved[3]` | — | 未来扩展保留 |

`status` 字段的含义按调用上下文区分：

- 工作空间分配出错或工作空间不足 ⇒ `ACDNN_STATUS_ALLOC_FAILED`
- 计时或工作空间释放阶段出错 ⇒ `ACDNN_STATUS_INTERNAL_ERROR`
- 其他情况 ⇒ 直接复用对应卷积函数（`acdnnConvolutionForward()` / `acdnnConvolutionBackwardData()`）的返回值。

##### 3.1.2.1. acdnnConvolutionBwdDataAlgoPerf_t {#3121-acdnnconvolutionbwddataalgoperf_t}

后向数据卷积版本，与上面通用描述对齐，由 `acdnnFindConvolutionBackwardDataAlgorithm()` 或 `acdnnGetConvolutionBackwardDataAlgorithm_v7()` 填充。

##### 3.1.2.2. acdnnConvolutionFwdAlgoPerf_t {#3122-acdnnconvolutionfwdalgoperf_t}

前向卷积版本，由 `acdnnFindConvolutionForwardAlgorithm()` 或 `acdnnGetConvolutionForwardAlgorithm_v7()` 填充。

#### 3.1.3. 枚举类型 {#313-枚举类型}

##### 3.1.3.1. acdnnConvolutionBwdDataAlgo_t {#3131-acdnnconvolutionbwddataalgo_t}

列出反向数据卷积可选算法。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_CONVOLUTION_BWD_DATA_ALGO_0` | 隐式矩阵乘积之和（原子加法，不可复现） |
| `ACDNN_CONVOLUTION_BWD_DATA_ALGO_1` | 隐式矩阵乘积（可复现） |
| `ACDNN_CONVOLUTION_BWD_DATA_ALGO_FFT` | FFT 方法；需要大量工作空间；可复现 |
| `ACDNN_CONVOLUTION_BWD_DATA_ALGO_DIRECT` | 直接方法（当前实现与 FFT 等效）；可复现 |
| `ACDNN_CONVOLUTION_BWD_DATA_ALGO_FFT_TILING` | FFT 分块方法；大图比 FFT 省内存；可复现 |
| `ACDNN_CONVOLUTION_BWD_DATA_ALGO_WINOGRAD` | Winograd 变换；工作空间适中；可复现 |
| `ACDNN_CONVOLUTION_BWD_DATA_ALGO_WINOGRAD_NONFUSED` | Winograd 非融合变换；可能需要较大工作空间；可复现 |

##### 3.1.3.2. acdnnConvolutionBwdFilterAlgo_t {#3132-acdnnconvolutionbwdfilteralgo_t}

列出反向滤波器卷积可选算法。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_CONVOLUTION_BWD_FILTER_ALGO_0` | 隐式矩阵乘积之和（原子加法，不可复现） |
| `ACDNN_CONVOLUTION_BWD_FILTER_ALGO_1` | 隐式矩阵乘积（可复现） |
| `ACDNN_CONVOLUTION_BWD_FILTER_ALGO_FFT` | FFT 方法；需要大量工作空间；可复现 |
| `ACDNN_CONVOLUTION_BWD_FILTER_ALGO_3` | 类似 ALGO_0 但预计算索引（少量工作空间，不可复现） |
| `ACDNN_CONVOLUTION_BWD_FILTER_ALGO_DIRECT` | 直接方法（当前实现与 FFT 等效）；可复现 |
| `ACDNN_CONVOLUTION_BWD_FILTER_ALGO_WINOGRAD` | Winograd 变换（当前版本未实现） |
| `ACDNN_CONVOLUTION_BWD_FILTER_ALGO_WINOGRAD_NONFUSED` | Winograd 非融合变换；可能需要较大工作空间；可复现 |
| `ACDNN_CONVOLUTION_BWD_FILTER_ALGO_FFT_TILING` | FFT 分块方法；可复现 |

##### 3.1.3.3. acdnnConvolutionFwdAlgo_t {#3133-acdnnconvolutionfwdalgo_t}

列出前向卷积可选算法。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_CONVOLUTION_FWD_ALGO_IMPLICIT_GEMM` | 隐式 GEMM（不显式构建输入矩阵） |
| `ACDNN_CONVOLUTION_FWD_ALGO_IMPLICIT_PRECOMP_GEMM` | 隐式 GEMM + 预计算索引（需少量工作空间） |
| `ACDNN_CONVOLUTION_FWD_ALGO_GEMM` | 显式 GEMM（需要大量工作空间存储展开矩阵） |
| `ACDNN_CONVOLUTION_FWD_ALGO_DIRECT` | 直接卷积（无矩阵乘法） |
| `ACDNN_CONVOLUTION_FWD_ALGO_FFT` | FFT 方法；需要大量工作空间 |
| `ACDNN_CONVOLUTION_FWD_ALGO_FFT_TILING` | FFT 分块方法；大图比 FFT 省内存 |
| `ACDNN_CONVOLUTION_FWD_ALGO_WINOGRAD` | Winograd 变换；工作空间适中 |
| `ACDNN_CONVOLUTION_FWD_ALGO_WINOGRAD_NONFUSED` | Winograd 非融合变换；可能需要较大工作空间 |

##### 3.1.3.4. acdnnConvolutionMode_t {#3134-acdnnconvolutionmode_t}

卷积描述符使用的运算模式。

| 值 | 描述 |
| :--- | :--- |
| `ACDNN_CONVOLUTION` | 数学卷积（等价于滤波器旋转 180° 后做互相关） |
| `ACDNN_CROSS_CORRELATION` | 互相关（深度学习中常用的"卷积"） |

#### 3.1.4. acdnnConvolutionBackwardData() {#314-acdnnconvolutionbackwarddata}

```cpp
acdnnStatus_t acdnnConvolutionBackwardData(
    acdnnHandle_t handle,
    const void *alpha,
    const acdnnFilterDescriptor_t wDesc, const void *w,
    const acdnnTensorDescriptor_t dyDesc, const void *dy,
    const acdnnConvolutionDescriptor_t convDesc,
    acdnnConvolutionBwdDataAlgo_t algo,
    void *workspace, size_t workspaceSizeInBytes,
    const void *beta,
    const acdnnTensorDescriptor_t dxDesc, void *dx);
```

`acdnnConvolutionForward()` 的反向数据梯度，给定上层梯度 `dy`，结合滤波器 `w` 计算输入梯度 `dx`，按 `α·result + β·prevDx` 写回。 `algo` 指定使用的算法（参见 `acdnnConvolutionBwdDataAlgo_t`）。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `alpha` / `beta` | 输入 | 主机端混合系数： `dx = α·result + β·priorDx` |
| `wDesc` / `w` | 输入 | 滤波器描述符 / 设备指针 |
| `dyDesc` / `dy` | 输入 | 输出梯度张量描述符 / 设备指针 |
| `convDesc` | 输入 | 卷积描述符 |
| `algo` | 输入 | 算法选择（`acdnnConvolutionBwdDataAlgo_t`） |
| `workspace` / `workspaceSizeInBytes` | 输入 | 工作空间指针及字节数（不需要时可 NULL/0） |
| `dxDesc` / `dx` | 输入/输出 | 输入梯度张量描述符 / 设备指针 |

**支持的数据类型组合**

| 数据类型组合 | `wDesc`、`dyDesc` 和 `dxDesc` 数据类型 | `convDesc` 数据类型 |
| :--- | :--- | :--- |
| `TRUE_HALF_CONFIG` | `ACDNN_DATA_HALF` | `ACDNN_DATA_HALF` |
| `PSEUDO_HALF_CONFIG` | `ACDNN_DATA_HALF` | `ACDNN_DATA_FLOAT` |
| `PSEUDO_BFLOAT16_CONFIG` | `ACDNN_DATA_BF16` | `ACDNN_DATA_FLOAT` |
| `FLOAT_CONFIG` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` |
| `DOUBLE_CONFIG` | `ACDNN_DATA_DOUBLE` | `ACDNN_DATA_DOUBLE` |

**支持的算法**

!!! note
    指定单独的算法可能会导致性能、支持和计算确定性的变化。请参阅以下内容以获取算法选项列表及其各自支持的参数和确定性行为。

下表显示了支持的 2D 和 3D 卷积列表。首先描述 2D 卷积，其次描述 3D 卷积。

为了简洁起见，对于以下术语，在下表中使用括号中显示的简写形式：

- `ACDNN_CONVOLUTION_BWD_DATA_ALGO_0`（`_ALGO_0`）
- `ACDNN_CONVOLUTION_BWD_DATA_ALGO_1`（`_ALGO_1`）
- `ACDNN_CONVOLUTION_BWD_DATA_ALGO_FFT`（`_FFT`）
- `ACDNN_CONVOLUTION_BWD_DATA_ALGO_FFT_TILING`（`_FFT_TILING`）
- `ACDNN_CONVOLUTION_BWD_DATA_ALGO_WINOGRAD`（`_WINOGRAD`）
- `ACDNN_CONVOLUTION_BWD_DATA_ALGO_WINOGRAD_NONFUSED`（`_WINOGRAD_NONFUSED`）
- `ACDNN_TENSOR_NCHW`（`_NCHW`）
- `ACDNN_TENSOR_NHWC`（`_NHWC`）
- `ACDNN_TENSOR_NCHW_VECT_C`（`_NCHW_VECT_C`）

**表 `acdnnConvolutionBackwardData()` 2D 卷积支持的算法：wDesc: _NHWC**

| 算法名称 | 确定性（是或否） | `dyDesc` 支持的张量格式 | `dxDesc` 支持的张量格式 | 支持的数据类型配置 | 重要事项 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `_ALGO_0` | 否 | `NHWC` `HWC-packed` | `NHWC` `HWC-packed` | `TRUE_HALF_CONFIG` | |
| `_ALGO_1` | 是 | `NHWC` `HWC-packed` | `NHWC` `HWC-packed` | `PSEUDO_HALF_CONFIG` | |
| `_ALGO_1` | 是 | `NHWC` `HWC-packed` | `NHWC` `HWC-packed` | `PSEUDO_BFLOAT16_CONFIG` | |
| `_ALGO_1` | 是 | `NHWC` `HWC-packed` | `NHWC` `HWC-packed` | `FLOAT_CONFIG` | |

**表 `acdnnConvolutionBackwardData()` 2D 卷积支持的算法：wDesc: _NCHW**

| 算法名称 | 确定性（是或否） | `dyDesc` 支持的张量格式 | `dxDesc` 支持的张量格式 | 支持的数据类型配置 | 重要事项 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `_ALGO_0` | 否 | `NCHW` `CHW-packed` | 除 `_NCHW_VECT_C` 外的所有格式 | `TRUE_HALF_CONFIG`<br>`PSEUDO_HALF_CONFIG`<br>`PSEUDO_BFLOAT16_CONFIG`<br>`FLOAT_CONFIG`<br>`DOUBLE_CONFIG` | 扩张：所有维度大于 0<br>`convDesc` 分组数支持：大于 0 |
| `_ALGO_1` | 是 | `NCHW` `CHW-packed` | 除 `_NCHW_VECT_C` 外的所有格式 | `TRUE_HALF_CONFIG`<br>`PSEUDO_HALF_CONFIG`<br>`PSEUDO_BFLOAT16_CONFIG`<br>`FLOAT_CONFIG`<br>`DOUBLE_CONFIG` | 扩张：所有维度大于 0<br>`convDesc` 分组数支持：大于 0 |
| `_FFT` | 是 | `NCHW` `CHW-packed` | `NCHW` HW-packed | `PSEUDO_HALF_CONFIG` | 扩张：所有维度为 1<br>`convDesc` 分组数支持：大于 0<br>`dxDesc` 特征图高度 + 2 * `convDesc` 零填充高度必须等于或小于 256<br>`dxDesc` 特征图宽度 + 2 * `convDesc` 零填充宽度必须等于或小于 256<br>`convDesc` 垂直和水平滤波器步幅必须等于 1<br>`wDesc` 滤波器高度必须大于 `convDesc` 零填充高度<br>`wDesc` 滤波器宽度必须大于 `convDesc` 零填充宽度 |
| `_FFT_TILING` | 是 | `NCHW` `CHW-packed` | `NCHW` HW-packed | `PSEUDO_HALF_CONFIG`<br>`FLOAT_CONFIG`<br>`DOUBLE_CONFIG`（当任务可由 1D FFT 处理时也支持，即滤波器维度之一（宽度或高度）为 1） | 扩张：所有维度为 1<br>`convDesc` 分组数支持：大于 0<br>当 `wDesc` 滤波器维度都不是 1 时，滤波器宽度和高度不得大于 32<br>当 `wDesc` 滤波器维度之一为 1 时，最大滤波器维度不应超过 256<br>当滤波器宽度或滤波器高度为 1 时，`convDesc` 垂直和水平滤波器步幅必须等于 1，否则步幅可以为 1 或 2<br>`wDesc` 滤波器高度必须大于 `convDesc` 零填充高度<br>`wDesc` 滤波器宽度必须大于 `convDesc` 零填充宽度 |
| `_WINOGRAD` | 是 | `NCHW` `CHW-packed` | 除 `_NCHW_VECT_C` 外的所有格式 | `PSEUDO_HALF_CONFIG`<br>`FLOAT_CONFIG` | 扩张：所有维度为 1<br>`convDesc` 分组数支持：大于 0<br>`convDesc` 垂直和水平滤波器步幅必须等于 1<br>`wDesc` 滤波器高度必须为 3<br>`wDesc` 滤波器宽度必须为 3 |
| `_WINOGRAD_NONFUSED` | 是 | `NCHW` `CHW-packed` | 除 `_NCHW_VECT_C` 外的所有格式 | `TRUE_HALF_CONFIG`<br>`PSEUDO_HALF_CONFIG`<br>`PSEUDO_BFLOAT16_CONFIG`<br>`FLOAT_CONFIG` | 扩张：所有维度为 1<br>`convDesc` 分组数支持：大于 0<br>`convDesc` 滤波器高度必须为 3<br>`wDesc` 滤波器宽度必须为 3 |

**表 `acdnnConvolutionBackwardData()` 3D 卷积支持的算法：wDesc: _NCHW**

| 算法名称 | 确定性（是或否） | `dyDesc` 支持的张量格式 | `dxDesc` 支持的张量格式 | 支持的数据类型配置 | 重要事项 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `_ALGO_0` | 是 | `NCDHW` CDHW-packed | 除 `_NCHW_VECT_C` 外的所有格式 | `PSEUDO_HALF_CONFIG`<br>`PSEUDO_BFLOAT16_CONFIG`<br>`FLOAT_CONFIG`<br>`DOUBLE_CONFIG` | 扩张：所有维度大于 0<br>`convDesc` 分组数支持：大于 0 |
| `_ALGO_1` | 是 | `NCDHW` CDHW-packed | `NCDHW` CDHW-packed | `TRUE_HALF_CONFIG`<br>`PSEUDO_BFLOAT16_CONFIG`<br>`PSEUDO_HALF_CONFIG`<br>`FLOAT_CONFIG`<br>`DOUBLE_CONFIG` | 扩张：所有维度为 1<br>`convDesc` 分组数支持：大于 0 |
| `_FFT_TILING` | 是 | `NCDHW` CDHW-packed | `NCDHW` DHW-packed | `PSEUDO_HALF_CONFIG`<br>`FLOAT_CONFIG`<br>`DOUBLE_CONFIG` | 扩张：所有维度为 1<br>`convDesc` 分组数支持：大于 0<br>`wDesc` 滤波器高度必须等于或小于 16<br>`wDesc` 滤波器宽度必须等于或小于 16<br>`convDesc` 必须所有滤波器步幅等于 1<br>`wDesc` 滤波器高度必须大于 `convDesc` 零填充高度<br>`wDesc` 滤波器宽度必须大于 `convDesc` 零填充宽度<br>`wDesc` 滤波器深度必须大于 `convDesc` 零填充深度 |

**表 `acdnnConvolutionBackwardData()` 3D 卷积支持的算法：wDesc: _NHWC**

| 算法名称（3D 卷积） | 确定性（是或否） | `dyDesc` 支持的张量格式 | `dxDesc` 支持的张量格式 | 支持的数据类型配置 | 重要事项 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `_ALGO_1` | 是 | `NDHWC` | `NDHWC` | `TRUE_HALF_CONFIG` | 扩张：所有维度大于 0<br>`convDesc` 分组数支持：大于 0 |
| `_ALGO_1` | 是 | `DHWC-packed` | `DHWC-packed` | `PSEUDO_HALF_CONFIG` | 扩张：所有维度大于 0<br>`convDesc` 分组数支持：大于 0 |
| `_ALGO_1` | 是 | `DHWC-packed` | `DHWC-packed` | `PSEUDO_BFLOAT16_CONFIG` | 扩张：所有维度大于 0<br>`convDesc` 分组数支持：大于 0 |
| `_ALGO_1` | 是 | `DHWC-packed` | `DHWC-packed` | `FLOAT_CONFIG` | 扩张：所有维度大于 0<br>`convDesc` 分组数支持：大于 0 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：满足以下至少一个条件：
  - 以下至少一个为 NULL： `handle`、`dyDesc`、`wDesc`、`convDesc`、`dxDesc`、`dy`、`w`、`dx`、`alpha`、`beta`
  - `wDesc` 和 `dyDesc` 的维度数不匹配
  - `wDesc` 和 `dxDesc` 的维度数不匹配
  - `wDesc` 的维度数少于三
  - `wDesc`、`dxDesc` 和 `dyDesc` 的数据类型不匹配
  - `wDesc` 和 `dxDesc` 的每幅图像（或分组卷积情况下的组）输入特征图数量不匹配
  - `dyDesc` 的空间尺寸与 `acdnnGetConvolutionNdForwardOutputDim` 确定的预期尺寸不匹配
- `ACDNN_STATUS_NOT_SUPPORTED`：满足以下至少一个条件：
  - `dyDesc` 或 `dxDesc` 具有负的张量步幅
  - `dyDesc`、`wDesc` 或 `dxDesc` 的维度数不是 4 或 5
  - 所选算法不支持所提供的参数
  - `dyDesc` 或 `wDesc` 指示的输出通道数不是组数的倍数
- `ACDNN_STATUS_MAPPING_ERROR`：在与滤波器数据或输入微分张量数据关联的纹理对象创建过程中发生纹理绑定错误。
- `ACDNN_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 3.1.5. acdnnConvolutionBiasActivationForward() {#315-acdnnconvolutionbiasactivationforward}

```cpp
acdnnStatus_t acdnnConvolutionBiasActivationForward(
    acdnnHandle_t handle,
    const void *alpha1,
    const acdnnTensorDescriptor_t xDesc, const void *x,
    const acdnnFilterDescriptor_t wDesc, const void *w,
    const acdnnConvolutionDescriptor_t convDesc,
    acdnnConvolutionFwdAlgo_t algo,
    void *workspace, size_t workSpaceInBytes,
    const void *alpha2,
    const acdnnTensorDescriptor_t zDesc, const void *z,
    const acdnnTensorDescriptor_t biasDesc, const void *bias,
    const acdnnActivationDescriptor_t activationDesc,
    const acdnnTensorDescriptor_t yDesc, void *y);
```

把 `acdnnConvolutionForward()`、bias、activation 三步**融合** 为一次 Kernel 启动：

$$y = \text{act}\bigl(\alpha_1 \cdot \text{conv}(x) + \alpha_2 \cdot z + \text{bias}\bigr)$$

`activationDesc` 选择激活函数； `zDesc` / `z` 提供与卷积输出相加的 side input（无需要时令 `α₂ = 0`、`z` 与 `y` 同形即可）。

`yDesc` 的形状可借助 `acdnnGetConvolution2dForwardOutputDim()` 或 `acdnnGetConvolutionNdForwardOutputDim()` 推算。使用 `ACDNN_ACTIVATION_IDENTITY` 时 `algo` 必须为 `IMPLICIT_PRECOMP_GEMM`。 `z` 和 `y` 可同缓冲区，但 `x` 不可与 `z`/`y` 重叠。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `alpha1` / `alpha2` | 输入 | 主机端系数： `y = act(α1·conv(x) + α2·z + bias)` |
| `xDesc` / `x` | 输入 | 输入张量描述符 / 设备指针 |
| `wDesc` / `w` | 输入 | 滤波器描述符 / 设备指针 |
| `convDesc` | 输入 | 卷积描述符 |
| `algo` | 输入 | 前向算法（`acdnnConvolutionFwdAlgo_t`） |
| `workspace` / `workSpaceInBytes` | 输入 | 工作空间指针及字节数 |
| `zDesc` / `z` | 输入 | side input 张量（无需时令 α2=0） |
| `biasDesc` / `bias` | 输入 | 偏置张量 |
| `activationDesc` | 输入 | 激活描述符（`IDENTITY` 时须用 `IMPLICIT_PRECOMP_GEMM`） |
| `yDesc` / `y` | 输入/输出 | 输出张量（`z` 和 `y` 可同缓冲区， `x` 不可） |

卷积步骤数据类型同 `acdnnConvolutionForward()`。下表为融合 bias+activation 的类型组合。

**表 `acdnnConvolutionBiasActivationForward()` 支持的数据类型组合（X = ACDNN_DATA）**

| x | w | `convDesc` | y 和 z | bias | `alpha1`/`alpha2` |
| :--- | :--- | :--- | :--- | :--- | :--- |
| X_Double | X_Double | X_Double | X_Double | X_Double | X_Double |
| `X_FLOAT` | `X_FLOAT` | `X_FLOAT` | `X_FLOAT` | `X_FLOAT` | `X_FLOAT` |
| `X_HALF` | `X_HALF` | `X_FLOAT` | `X_HALF` | `X_HALF` | `X_FLOAT` |
| `X_BFLOAT16` | `X_BFLOAT16` | `X_FLOAT` | `X_BFLOAT16` | `X_BFLOAT16` | `X_FLOAT` |
| `X_INT8` | `X_INT8` | `X_INT32` | `X_INT8` | `X_FLOAT` | `X_FLOAT` |
| `X_INT8` | `X_INT8` | `X_INT32` | `X_FLOAT` | `X_FLOAT` | `X_FLOAT` |
| X_INT8x4 | X_INT8x4 | `X_INT32` | X_INT8x4 | `X_FLOAT` | `X_FLOAT` |
| X_INT8x4 | X_INT8x4 | `X_INT32` | `X_FLOAT` | `X_FLOAT` | `X_FLOAT` |
| `X_UINT8` | `X_UINT8` | `X_INT32` | `X_UINT8` | `X_FLOAT` | `X_FLOAT` |
| `X_UINT8` | `X_UINT8` | `X_INT32` | `X_FLOAT` | `X_FLOAT` | `X_FLOAT` |
| X_UINT8x4 | X_UINT8x4 | `X_INT32` | X_INT8x4 | `X_FLOAT` | `X_FLOAT` |
| X_UINT8x4 | X_UINT8x4 | `X_INT32` | `X_FLOAT` | `X_FLOAT` | `X_FLOAT` |
| X_INT8x32 | X_INT8x32 | `X_INT32` | X_INT8x32 | `X_FLOAT` | `X_FLOAT` |

除了 `acdnnConvolutionForward()` 文档列出的错误值之外，此函数返回的可能错误值及其含义如下所列。

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：满足以下至少一个条件：
  - 以下至少一个为 NULL： `handle`、`xDesc`、`wDesc`、`convDesc`、`yDesc`、`zDesc`、`biasDesc`、`activationDesc`、`xData`、`wData`、`yData`、`zData`、`bias`、`alpha1`、`alpha2`
  - `xDesc`、`wDesc`、`yDesc` 和 `zDesc` 的维度数不等于 `convDesc` 的数组长度 + 2
- `ACDNN_STATUS_NOT_SUPPORTED`：函数不支持提供的配置。以下是一些不支持的配置示例：
  - `activationDesc` 的模式不是 `ACDNN_ACTIVATION_RELU` 或 `ACDNN_ACTIVATION_IDENTITY`
  - `activationDesc` 的 `reluNanOpt` 不是 `ACDNN_NOT_PROPAGATE_NAN`
  - `biasDesc` 的第二步幅不等于 1
  - `biasDesc` 的第一维度不等于 1
  - `biasDesc` 的第二维度与 `filterDesc` 的第一维度不相等
  - `biasDesc` 的数据类型与 `yDesc` 的数据类型不对应
  - `zDesc` 和 `destDesc` 不匹配
- `ACDNN_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.1.6. acdnnConvolutionForward() {#316-acdnnconvolutionforward}

```cpp
acdnnStatus_t acdnnConvolutionForward(
    acdnnHandle_t handle,
    const void *alpha,
    const acdnnTensorDescriptor_t xDesc, const void *x,
    const acdnnFilterDescriptor_t wDesc, const void *w,
    const acdnnConvolutionDescriptor_t convDesc,
    acdnnConvolutionFwdAlgo_t algo,
    void *workspace, size_t workspaceSizeInBytes,
    const void *beta,
    const acdnnTensorDescriptor_t yDesc, void *y);
```

用滤波器 `w` 对输入 `x` 执行卷积（或互相关，取决于 `convDesc` 中的 mode），结果按 `α·result + β·prevY` 写入 `y`。 `yDesc` 的形状可借助 `acdnnGetConvolution2dForwardOutputDim()` 或 `acdnnGetConvolutionNdForwardOutputDim()` 推算。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `alpha` / `beta` | 输入 | 主机端缩放系数： `y = α·conv(x) + β·prevY` |
| `xDesc` / `x` | 输入 | 输入张量描述符 / 设备指针 |
| `wDesc` / `w` | 输入 | 滤波器描述符 / 设备指针 |
| `convDesc` | 输入 | 卷积描述符（`acdnnConvolutionDescriptor_t`） |
| `algo` | 输入 | 前向算法（`acdnnConvolutionFwdAlgo_t`） |
| `workspace` / `workspaceSizeInBytes` | 输入 | 工作空间设备指针及字节数；不需要时可为 NULL |
| `yDesc` / `y` | 输入/输出 | 输出张量描述符 / 设备指针 |

**支持的配置**

**表 `acdnnConvolutionForward()` 支持的配置**

| 数据类型组合 | `xDesc` 和 `wDesc` | `convDesc` | `yDesc` |
| :--- | :--- | :--- | :--- |
| `TRUE_HALF_CONFIG` | `ACDNN_DATA_HALF` | `ACDNN_DATA_HALF` | `ACDNN_DATA_HALF` |
| `PSEUDO_HALF_CONFIG` | `ACDNN_DATA_HALF` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_HALF` |
| `PSEUDO_BFLOAT16_CONFIG`| `ACDNN_DATA_BF16` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_BF16` |
| `FLOAT_CONFIG` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` |
| `DOUBLE_CONFIG` | `ACDNN_DATA_DOUBLE` | `ACDNN_DATA_DOUBLE` | `ACDNN_DATA_DOUBLE` |
| `INT8_CONFIG` | `ACDNN_DATA_INT8` | `ACDNN_DATA_INT32` | `ACDNN_DATA_INT8` |
| `INT8_EXT_CONFIG` | `ACDNN_DATA_INT8` | `ACDNN_DATA_INT32` | `ACDNN_DATA_FLOAT` |
| `INT8x4_CONFIG` | `ACDNN_DATA_INT8x4` | `ACDNN_DATA_INT32` | `ACDNN_DATA_INT8x4` |
| `INT8x4_EXT_CONFIG` | `ACDNN_DATA_INT8x4` | `ACDNN_DATA_INT32` | `ACDNN_DATA_FLOAT` |
| `UINT8_CONFIG` | `xDesc`: `ACDNN_DATA_UINT8`<br>`wDesc`: `ACDNN_DATA_INT8` | `ACDNN_DATA_INT32` | `ACDNN_DATA_INT8` |
| `UINT8x4_CONFIG` | `xDesc`: `ACDNN_DATA_UINT8x4`<br>`wDesc`: `ACDNN_DATA_INT8x4` | `ACDNN_DATA_INT32` | `ACDNN_DATA_INT8` |
| `UINT8_EXT_CONFIG` | `xDesc`: `ACDNN_DATA_UINT8`<br>`wDesc`: `ACDNN_DATA_INT8` | `ACDNN_DATA_INT32` | `ACDNN_DATA_FLOAT` |
| `UINT8x4_EXT_CONFIG` | `xDesc`: `ACDNN_DATA_UINT8x4`<br>`wDesc`: `ACDNN_DATA_INT8x4` | `ACDNN_DATA_INT32` | `ACDNN_DATA_FLOAT` |
| `INT8x32_CONFIG` | `ACDNN_DATA_INT8x32` | `ACDNN_DATA_INT32` | `ACDNN_DATA_INT8x32` |

**支持的算法**

!!! note
    对于此函数，所有算法都执行确定性计算。指定单独的算法可能会导致性能和支持的变化。

下表显示了支持的 2D 和 3D 卷积列表。首先描述 2D 卷积，其次描述 3D 卷积。

为了简洁起见，对于以下术语，在下表中使用括号中显示的简写形式：

- `ACDNN_CONVOLUTION_FWD_ALGO_IMPLICIT_GEMM`（`_IMPLICIT_GEMM`）
- `ACDNN_CONVOLUTION_FWD_ALGO_IMPLICIT_PRECOMP_GEMM`（`_IMPLICIT_PRECOMP_GEMM`）
- `ACDNN_CONVOLUTION_FWD_ALGO_GEMM`（`_GEMM`）
- `ACDNN_CONVOLUTION_FWD_ALGO_DIRECT`（`_DIRECT`）
- `ACDNN_CONVOLUTION_FWD_ALGO_FFT`（`_FFT`）
- `ACDNN_CONVOLUTION_FWD_ALGO_FFT_TILING`（`_FFT_TILING`）
- `ACDNN_CONVOLUTION_FWD_ALGO_WINOGRAD`（`_WINOGRAD`）
- `ACDNN_CONVOLUTION_FWD_ALGO_WINOGRAD_NONFUSED`（`_WINOGRAD_NONFUSED`）
- `ACDNN_TENSOR_NCHW`（`_NCHW`）
- `ACDNN_TENSOR_NHWC`（`_NHWC`）
- `ACDNN_TENSOR_NCHW_VECT_C`（`_NCHW_VECT_C`）

**表 `acdnnConvolutionForward()` 2D 卷积支持的算法：wDesc: _NCHW**

**滤波器描述符 `wDesc: _NCHW`**
*（请参阅 `acdnnTensorFormat_t`。convDesc 分组数支持：所有 Algorithm 均 > 0。）*

| 算法名称 | `xDesc` 支持的张量格式 | `yDesc` 支持的张量格式 | 支持的数据类型配置 | 重要事项 |
| :--- | :--- | :--- | :--- | :--- |
| `_IMPLICIT_GEMM` | 除 `_NCHW_VECT_C` 外的所有格式 | 除 `_NCHW_VECT_C` 外的所有格式 | `TRUE_HALF_CONFIG`、`PSEUDO_HALF_CONFIG`、`PSEUDO_BFLOAT16_CONFIG`、`FLOAT_CONFIG`、`DOUBLE_CONFIG` | 扩张：所有维度 > 0 |
| `_IMPLICIT_PRECOMP_GEMM` | 除 `_NCHW_VECT_C` 外的所有格式 | 除 `_NCHW_VECT_C` 外的所有格式 | `TRUE_HALF_CONFIG`、`PSEUDO_HALF_CONFIG`、`PSEUDO_BFLOAT16_CONFIG`、`FLOAT_CONFIG`、`DOUBLE_CONFIG` | 扩张：所有维度为 1 |
| `_GEMM` | 除 `_NCHW_VECT_C` 外的所有格式 | 除 `_NCHW_VECT_C` 外的所有格式 | `PSEUDO_HALF_CONFIG`、`FLOAT_CONFIG`、`DOUBLE_CONFIG` | 扩张：所有维度为 1 |
| `_FFT` | `NCHW`、`HW-packed` | `NCHW`、`HW-packed` | `PSEUDO_HALF_CONFIG`、`FLOAT_CONFIG` | 扩张：1<br>`xDesc` 高度 + 2×pad_h ≤ 256<br>`xDesc` 宽度 + 2×pad_w ≤ 256<br>步幅 = 1<br>滤波器 h/w > 零填充 h/w |
| `_FFT_TILING` | - | - | `PSEUDO_HALF_CONFIG`、`FLOAT_CONFIG`、`DOUBLE_CONFIG`<br>（当任务可由 1D FFT 处理时也支持，即一个滤波器维度 = 1） | 扩张：1<br>如果没有维度 = 1：滤波器 w/h ≤ 32<br>如果任何维度 = 1：最大维度 ≤ 256<br>步幅 = 1（如果滤波器 w/h = 1 则为 1/2）<br>滤波器 h/w > 零填充 h/w |
| `_WINOGRAD` | 除 `_NCHW_VECT_C` 外的所有格式 | 除 `_NCHW_VECT_C` 外的所有格式 | `PSEUDO_HALF_CONFIG`、`FLOAT_CONFIG` | 扩张：1<br>步幅 = 1<br>滤波器 h = 3，滤波器 w = 3 |
| `_WINOGRAD_NONFUSED` | - | - | `TRUE_HALF_CONFIG`、`PSEUDO_HALF_CONFIG`、`PSEUDO_BFLOAT16_CONFIG`、`FLOAT_CONFIG` | 扩张：1<br>步幅 = 1<br>滤波器（h,w）=（3,3）或（5,5）<br>如果为（5,5），不支持 `TRUE_HALF_CONFIG` |
| `_DIRECT` | 当前未在 acDNN 中实现。 | - | - | - |

**表 `acdnnConvolutionForward()` 2D 卷积支持的算法：wDesc: _NCHWC**

| 算法名称 | `xDesc` | `yDesc` | 支持的数据类型配置 | 重要事项 |
| :--- | :--- | :--- | :--- | :--- |
| `_IMPLICIT_GEMM` | `_NCHW_VECT_C` | `_NCHW_VECT_C` | INT8x4_CONFIG | 扩张：所有维度为 1 |
| `_IMPLICIT_PRECOMP_GEMM` | `_NCHW_VECT_C` | `_NCHW_VECT_C` | UINT8x4_CONFIG | |
| `_IMPLICIT_PRECOMP_NCHW_VECT_C` | `_NCHW_VECT_C` | `_NCHW_VECT_C` | INT8x32_CONFIG | 扩张：所有维度为 1 |

**表 `acdnnConvolutionForward()` 2D 卷积支持的算法：wDesc: _NHWC**

| 算法名称 | `xDesc` | `yDesc` | 支持的数据类型配置 | 重要事项 |
| :--- | :--- | :--- | :--- | :--- |
| `_IMPLICIT_GEMM` | `NHWC` 全打包 | `NHWC` 全打包 | `INT8_CONFIG` | 扩张：所有维度为 1 |
| `_IMPLICIT_PRECOMP_GEMM` | `NHWC` 全打包 | `NHWC` 全打包 | `INT8_EXT_CONFIG` | 输入和输出特征图必须是 4 的倍数。在 `INT8_EXT_CONFIG` 或 `UINT8_EXT_CONFIG` 的情况下，输出特征图可以不是倍数 |
| `_IMPLICIT_GEMM` | `NHWC` `HWC-packed` | `NHWC` `HWC-packed` | `TRUE_HALF_CONFIG` | |
| `_IMPLICIT_PRECOMP_GEMM` | `NHWC` `HWC-packed` | `NCHW` `CHW-packed` | `PSEUDO_HALF_CONFIG` | |
| `_IMPLICIT_PRECOMP_GEMM` | `NHWC` `HWC-packed` | `NCHW` `CHW-packed` | `PSEUDO_BFLOAT16_CONFIG` | |
| `_IMPLICIT_PRECOMP_GEMM` | `NHWC` `HWC-packed` | `NCHW` `CHW-packed` | `FLOAT_CONFIG` | |
| `_IMPLICIT_PRECOMP_GEMM` | `NHWC` `HWC-packed` | `NCHW` `CHW-packed` | `DOUBLE_CONFIG` | |

**表 `acdnnConvolutionForward()` 3D 卷积支持的算法：wDesc: _NCHW**

| 算法名称 | `xDesc` | `yDesc` | 支持的数据类型配置 | 重要事项 |
| :--- | :--- | :--- | :--- | :--- |
| `_IMPLICIT_GEMM` | 除 `_NCHW_VECT_C` 外的所有格式 | 除 `_NCHW_VECT_C` 外的所有格式 | `PSEUDO_HALF_CONFIG` | 扩张：所有维度大于 0 |
| `_IMPLICIT_PRECOMP_GEMM` | 除 `_NCHW_VECT_C` 外的所有格式 | 除 `_NCHW_VECT_C` 外的所有格式 | `PSEUDO_BFLOAT16_CONFIG` | 扩张：所有维度大于 0 |
| `_IMPLICIT_PRECOMP_GEMM` | 除 `_NCHW_VECT_C` 外的所有格式 | 除 `_NCHW_VECT_C` 外的所有格式 | `FLOAT_CONFIG` | 扩张：所有维度大于 0 |
| `_IMPLICIT_PRECOMP_GEMM` | 除 `_NCHW_VECT_C` 外的所有格式 | 除 `_NCHW_VECT_C` 外的所有格式 | `DOUBLE_CONFIG` | 扩张：所有维度大于 0 |
| `_FFT_TILING` | `NCDHW` DHW-packed | `NCDHW` DHW-packed | `DOUBLE_CONFIG` | 扩张：所有维度为 1<br>`wDesc` 滤波器高度 ≤ 16<br>`wDesc` 滤波器宽度 ≤ 16<br>`wDesc` 滤波器深度 ≤ 16<br>`convDesc` 所有滤波器步幅 = 1<br>`wDesc` 滤波器高度 > `convDesc` 零填充高度<br>`wDesc` 滤波器宽度 > `convDesc` 零填充宽度<br>`wDesc` 滤波器深度 > `convDesc` 零填充深度 |

**表 `acdnnConvolutionForward()` 3D 卷积支持的算法：wDesc: _NHWC**

| 算法名称 | `xDesc` | `yDesc` | 支持的数据类型配置 | 重要事项 |
| :--- | :--- | :--- | :--- | :--- |
| `_IMPLICIT_PRECOMP_GEMM` | `NDHWC` | `NDHWC` | `PSEUDO_HALF_CONFIG` | 扩张：所有维度大于 0 |
| `_IMPLICIT_PRECOMP_GEMM` | `DHWC-packed` | `DHWC-packed` | `PSEUDO_BFLOAT16_CONFIG` | 扩张：所有维度大于 0 |

!!! note
    Tensor 可以使用 `acdnnTransformTensor()` 转换为 `ACDNN_TENSOR_NCHW_VECT_C` 格式或从该格式转换。

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：满足以下至少一个条件：
  - 以下至少一个为 NULL： `handle`、`xDesc`、`wDesc`、`convDesc`、`yDesc`、`xData`、`w`、`yData`、`alpha`、`beta`
  - `xDesc` 和 `yDesc` 的维度数不匹配
  - `xDesc` 和 `wDesc` 的维度数不匹配
  - `xDesc` 的维度数少于三
  - `xDesc` 的维度数不等于 `convDesc` 的数组长度 + 2
  - `xDesc` 和 `wDesc` 的每幅图像（或分组卷积情况下的组）输入特征图数量不匹配
  - `yDesc` 或 `wDesc` 指示的输出通道数不是组数的倍数
  - `xDesc`、`wDesc` 和 `yDesc` 的数据类型不匹配
  - 对于某些空间维度， `wDesc` 的空间尺寸大于输入空间尺寸（包括零填充尺寸）
- `ACDNN_STATUS_NOT_SUPPORTED`：满足以下至少一个条件：
  - `xDesc` 或 `yDesc` 具有负的张量步幅
  - `xDesc`、`wDesc` 或 `yDesc` 的维度数不是 4 或 5
  - `yDesc` 的空间尺寸与 `acdnnGetConvolutionNdForwardOutputDim()` 确定的预期尺寸不匹配
  - 所选算法不支持所提供的参数
- `ACDNN_STATUS_MAPPING_ERROR`：在与滤波器数据关联的纹理对象创建期间发生错误。
- `ACDNN_STATUS_EXECUTION_FAILED`：函数在真武 PPU 上启动失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.1.7. acdnnCreateConvolutionDescriptor() {#317-acdnncreateconvolutiondescriptor}

```cpp
acdnnStatus_t acdnnCreateConvolutionDescriptor(
    acdnnConvolutionDescriptor_t *convDesc);
```

为 `acdnnConvolutionDescriptor_t` 分配存储；返回时内部为零，需后续 `Set*` 完成实际配置。返回 `ACDNN_STATUS_SUCCESS` 表示创建成功， `ACDNN_STATUS_ALLOC_FAILED` 表示资源不足。


#### 3.1.8. acdnnDestroyConvolutionDescriptor() {#318-acdnndestroyconvolutiondescriptor}

```cpp
acdnnStatus_t acdnnDestroyConvolutionDescriptor(
    acdnnConvolutionDescriptor_t convDesc);
```

释放上面创建的卷积描述符。统一返回 `ACDNN_STATUS_SUCCESS`。


#### 3.1.9. acdnnFindConvolutionBackwardDataAlgorithm() {#319-acdnnfindconvolutionbackwarddataalgorithm}

遍历 `acdnnConvolutionBackwardData()` 的全部可用算法并按耗时升序返回性能指标。同时尝试 `convDesc` 指定的 MathType 和 `ACDNN_DEFAULT_MATH`。内存由 `hggcMalloc()` 分配。

```cpp
acdnnStatus_t acdnnFindConvolutionBackwardDataAlgorithm(
    acdnnHandle_t handle,
    const acdnnFilterDescriptor_t wDesc,
    const acdnnTensorDescriptor_t dyDesc,
    const acdnnConvolutionDescriptor_t convDesc,
    const acdnnTensorDescriptor_t dxDesc,
    const int requestedAlgoCount,
    int *returnedAlgoCount,
    acdnnConvolutionBwdDataAlgoPerf_t *perfResults);
```

!!! note
    此函数会阻塞主机。建议在分配层数据之前调用，以免因资源占用限制算法选项。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `wDesc` | 输入 | 滤波器描述符 |
| `dyDesc` | 输入 | 输入微分张量描述符 |
| `convDesc` | 输入 | 卷积描述符 |
| `dxDesc` | 输入 | 输出张量描述符 |
| `requestedAlgoCount` | 输入 | `perfResults` 中的最大元素数 |
| `returnedAlgoCount` | 输出 | 实际返回的元素数 |
| `perfResults` | 输出 | 按耗时升序排列的性能指标数组 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：描述符未正确分配。
- `ACDNN_STATUS_ALLOC_FAILED`：内存不足。
- `ACDNN_STATUS_INTERNAL_ERROR`：计时对象分配/释放失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.1.10. acdnnFindConvolutionBackwardDataAlgorithmEx() {#3110-acdnnfindconvolutionbackwarddataalgorithmex}

与 3.1.9 功能相同，但使用用户提供的实际张量数据进行基准测试（而非内部分配）。工作空间大小决定可用算法范围。

```cpp
acdnnStatus_t acdnnFindConvolutionBackwardDataAlgorithmEx(
    acdnnHandle_t handle,
    const acdnnFilterDescriptor_t wDesc,
    const void *w,
    const acdnnTensorDescriptor_t dyDesc,
    const void *dy,
    const acdnnConvolutionDescriptor_t convDesc,
    const acdnnTensorDescriptor_t dxDesc,
    void *dx,
    const int requestedAlgoCount,
    int *returnedAlgoCount,
    acdnnConvolutionBwdDataAlgoPerf_t *perfResults,
    void *workspace,
    size_t workspaceSizeInBytes);
```

!!! note
    此函数会阻塞主机。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `wDesc` / `w` | 输入 | 滤波器描述符 / 设备指针 |
| `dyDesc` / `dy` | 输入 | 输入微分张量描述符 / 设备指针 |
| `convDesc` | 输入 | 卷积描述符 |
| `dxDesc` / `dx` | 输入/输出 | 输出张量描述符 / 设备指针（内容会被覆写） |
| `requestedAlgoCount` | 输入 | `perfResults` 中的最大元素数 |
| `returnedAlgoCount` | 输出 | 实际返回的元素数 |
| `perfResults` | 输出 | 按耗时升序排列的性能指标数组 |
| `workspace` / `workspaceSizeInBytes` | 输入 | 工作空间设备指针及字节数；NULL 视为 0 字节 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：描述符未正确分配。
- `ACDNN_STATUS_INTERNAL_ERROR`：计时对象分配/释放失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.1.11. acdnnFindConvolutionForwardAlgorithm() {#3111-acdnnfindconvolutionforwardalgorithm}

遍历 `acdnnConvolutionForward()` 的全部可用算法并按耗时升序返回性能指标。同时尝试 `convDesc` 指定的 MathType 和 `ACDNN_DEFAULT_MATH`。内存由 `hggcMalloc()` 分配。

```cpp
acdnnStatus_t acdnnFindConvolutionForwardAlgorithm(
    acdnnHandle_t handle,
    const acdnnTensorDescriptor_t xDesc,
    const acdnnFilterDescriptor_t wDesc,
    const acdnnConvolutionDescriptor_t convDesc,
    const acdnnTensorDescriptor_t yDesc,
    const int requestedAlgoCount,
    int *returnedAlgoCount,
    acdnnConvolutionFwdAlgoPerf_t *perfResults);
```

!!! note
    此函数会阻塞主机。建议在分配层数据之前调用，以免因资源占用限制算法选项。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `xDesc` | 输入 | 输入张量描述符 |
| `wDesc` | 输入 | 滤波器描述符 |
| `convDesc` | 输入 | 卷积描述符 |
| `yDesc` | 输入 | 输出张量描述符 |
| `requestedAlgoCount` | 输入 | `perfResults` 中的最大元素数 |
| `returnedAlgoCount` | 输出 | 实际返回的元素数 |
| `perfResults` | 输出 | 按耗时升序排列的性能指标数组 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：描述符未正确分配。
- `ACDNN_STATUS_ALLOC_FAILED`：内存不足。
- `ACDNN_STATUS_INTERNAL_ERROR`：计时对象分配/释放失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.1.12. acdnnFindConvolutionForwardAlgorithmEx() {#3112-acdnnfindconvolutionforwardalgorithmex}

与 3.1.11 功能相同，但使用用户提供的实际张量数据进行基准测试。工作空间大小决定可用算法范围。

```cpp
acdnnStatus_t acdnnFindConvolutionForwardAlgorithmEx(
    acdnnHandle_t handle,
    const acdnnTensorDescriptor_t xDesc,
    const void *x,
    const acdnnFilterDescriptor_t wDesc,
    const void *w,
    const acdnnConvolutionDescriptor_t convDesc,
    const acdnnTensorDescriptor_t yDesc,
    void *y,
    const int requestedAlgoCount,
    int *returnedAlgoCount,
    acdnnConvolutionFwdAlgoPerf_t *perfResults,
    void *workspace,
    size_t workspaceSizeInBytes);
```

!!! note
    此函数会阻塞主机。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `xDesc` / `x` | 输入 | 输入张量描述符 / 设备指针 |
| `wDesc` / `w` | 输入 | 滤波器描述符 / 设备指针 |
| `convDesc` | 输入 | 卷积描述符 |
| `yDesc` / `y` | 输入/输出 | 输出张量描述符 / 设备指针（内容会被覆写） |
| `requestedAlgoCount` | 输入 | `perfResults` 中的最大元素数 |
| `returnedAlgoCount` | 输出 | 实际返回的元素数 |
| `perfResults` | 输出 | 按耗时升序排列的性能指标数组 |
| `workspace` / `workspaceSizeInBytes` | 输入 | 工作空间设备指针及字节数；NULL 视为 0 字节 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：描述符未正确分配。
- `ACDNN_STATUS_INTERNAL_ERROR`：计时对象分配/释放失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.1.13. acdnnGetConvolution2dDescriptor() {#3113-acdnngetconvolution2ddescriptor}

查询先前初始化的 2D 卷积描述符。

```cpp
acdnnStatus_t acdnnGetConvolution2dDescriptor(
    const acdnnConvolutionDescriptor_t convDesc,
    int *pad_h,
    int *pad_w,
    int *u,
    int *v,
    int *dilation_h,
    int *dilation_w,
    acdnnConvolutionMode_t *mode,
    acdnnDataType_t *computeType);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `convDesc` | 输入 | 卷积描述符 |
| `pad_h` / `pad_w` | 输出 | 零填充高度 / 宽度 |
| `u` / `v` | 输出 | 垂直 / 水平滤波器步幅 |
| `dilation_h` / `dilation_w` | 输出 | 高度 / 宽度扩张系数 |
| `mode` | 输出 | 卷积模式 |
| `computeType` | 输出 | 计算精度 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`convDesc` 为 NULL。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.1.14. acdnnGetConvolution2dForwardOutputDim() {#3114-acdnngetconvolution2dforwardoutputdim}

根据卷积配置、输入张量和滤波器推算 2D 卷积输出的 4D 维度（用于提前分配内存）。

```cpp
acdnnStatus_t acdnnGetConvolution2dForwardOutputDim(
    const acdnnConvolutionDescriptor_t convDesc,
    const acdnnTensorDescriptor_t inputTensorDesc,
    const acdnnFilterDescriptor_t filterDesc,
    int *n,
    int *c,
    int *h,
    int *w);
```

各空间维度计算公式：

```cpp
outputDim = 1 + (inputDim + 2*pad - (((filterDim-1)*dilation) + 1)) / convolutionStride;
```

!!! note
    调用 `acdnnConvolutionForward()` 或 `acdnnConvolutionBackwardData()` 时必须严格使用此函数返回的维度。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `convDesc` | 输入 | 卷积描述符 |
| `inputTensorDesc` | 输入 | 输入张量描述符 |
| `filterDesc` | 输入 | 滤波器描述符 |
| `n` | 输出 | 输出图像数量 |
| `c` | 输出 | 输出特征图数量 |
| `h` | 输出 | 输出特征图高度 |
| `w` | 输出 | 输出特征图宽度 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：描述符无效或特征图数量不匹配。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.1.15. acdnnGetConvolutionBackwardDataAlgorithmMaxCount() {#3115-acdnngetconvolutionbackwarddataalgorithmmaxcount}

返回 Find/Get 反向数据算法接口可能返回的最大算法数（含 Tensor 单元变体）。

```cpp
acdnnStatus_t acdnnGetConvolutionBackwardDataAlgorithmMaxCount(
    acdnnHandle_t handle,
    int *count);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `count` | 输出 | 最大算法数量 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`handle` 无效。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.1.16. acdnnGetConvolutionBackwardDataAlgorithm_v7() {#3116-acdnngetconvolutionbackwarddataalgorithm_v7}

基于启发式为 `acdnnConvolutionBackwardData()` 推荐最佳算法（按预估性能降序）。如需实测排名请用 `acdnnFindConvolutionBackwardDataAlgorithm()`。

```cpp
acdnnStatus_t acdnnGetConvolutionBackwardDataAlgorithm_v7(
    acdnnHandle_t handle,
    const acdnnFilterDescriptor_t wDesc,
    const acdnnTensorDescriptor_t dyDesc,
    const acdnnConvolutionDescriptor_t convDesc,
    const acdnnTensorDescriptor_t dxDesc,
    const int requestedAlgoCount,
    int *returnedAlgoCount,
    acdnnConvolutionBwdDataAlgoPerf_t *perfResults);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `wDesc` | 输入 | 滤波器描述符 |
| `dyDesc` | 输入 | 输入微分张量描述符 |
| `convDesc` | 输入 | 卷积描述符 |
| `dxDesc` | 输入 | 输出张量描述符 |
| `requestedAlgoCount` | 输入 | `perfResults` 中的最大元素数 |
| `returnedAlgoCount` | 输出 | 实际返回的元素数 |
| `perfResults` | 输出 | 按预估性能降序排列的算法数组 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：必要参数为 NULL 或无效。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.1.17. acdnnGetConvolutionBackwardDataWorkspaceSize() {#3117-acdnngetconvolutionbackwarddataworkspacesize}

查询指定算法执行 `acdnnConvolutionBackwardData()` 所需的工作空间大小（字节）。

```cpp
acdnnStatus_t acdnnGetConvolutionBackwardDataWorkspaceSize(
    acdnnHandle_t handle,
    const acdnnFilterDescriptor_t wDesc,
    const acdnnTensorDescriptor_t dyDesc,
    const acdnnConvolutionDescriptor_t convDesc,
    const acdnnTensorDescriptor_t dxDesc,
    acdnnConvolutionBwdDataAlgo_t algo,
    size_t *sizeInBytes);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `wDesc` | 输入 | 滤波器描述符 |
| `dyDesc` | 输入 | 输入微分张量描述符 |
| `convDesc` | 输入 | 卷积描述符 |
| `dxDesc` | 输入 | 输出张量描述符 |
| `algo` | 输入 | 所选算法 |
| `sizeInBytes` | 输出 | 所需工作空间字节数 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：描述符不匹配。
- `ACDNN_STATUS_NOT_SUPPORTED`：指定算法不支持当前配置。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.1.18. acdnnGetConvolutionForwardAlgorithmMaxCount() {#3118-acdnngetconvolutionforwardalgorithmmaxcount}

返回 Find/Get 前向算法接口可能返回的最大算法数（含 Tensor 单元变体）。

```cpp
acdnnStatus_t acdnnGetConvolutionForwardAlgorithmMaxCount(
    acdnnHandle_t handle,
    int *count);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `count` | 输出 | 最大算法数量 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`handle` 无效。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.1.19. acdnnGetConvolutionForwardAlgorithm_v7() {#3119-acdnngetconvolutionforwardalgorithm_v7}

基于启发式为 `acdnnConvolutionForward()` 推荐最佳算法（按预估性能降序）。如需实测排名请用 `acdnnFindConvolutionForwardAlgorithm()`。

```cpp
acdnnStatus_t acdnnGetConvolutionForwardAlgorithm_v7(
    acdnnHandle_t handle,
    const acdnnTensorDescriptor_t xDesc,
    const acdnnFilterDescriptor_t wDesc,
    const acdnnConvolutionDescriptor_t convDesc,
    const acdnnTensorDescriptor_t yDesc,
    const int requestedAlgoCount,
    int *returnedAlgoCount,
    acdnnConvolutionFwdAlgoPerf_t *perfResults);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `xDesc` | 输入 | 输入张量描述符 |
| `wDesc` | 输入 | 滤波器描述符 |
| `convDesc` | 输入 | 卷积描述符 |
| `yDesc` | 输入 | 输出张量描述符 |
| `requestedAlgoCount` | 输入 | `perfResults` 中的最大元素数 |
| `returnedAlgoCount` | 输出 | 实际返回的元素数 |
| `perfResults` | 输出 | 按预估性能降序排列的算法数组 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：必要参数为 NULL 或无效。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.1.20. acdnnGetConvolutionForwardWorkspaceSize() {#3120-acdnngetconvolutionforwardworkspacesize}

查询指定算法执行 `acdnnConvolutionForward()` 所需的工作空间大小（字节）。

```cpp
acdnnStatus_t acdnnGetConvolutionForwardWorkspaceSize(
    acdnnHandle_t handle,
    const acdnnTensorDescriptor_t xDesc,
    const acdnnFilterDescriptor_t wDesc,
    const acdnnConvolutionDescriptor_t convDesc,
    const acdnnTensorDescriptor_t yDesc,
    acdnnConvolutionFwdAlgo_t algo,
    size_t *sizeInBytes);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `xDesc` | 输入 | 输入张量描述符 |
| `wDesc` | 输入 | 滤波器描述符 |
| `convDesc` | 输入 | 卷积描述符 |
| `yDesc` | 输入 | 输出张量描述符 |
| `algo` | 输入 | 所选算法 |
| `sizeInBytes` | 输出 | 所需工作空间字节数 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：必要参数为 NULL。
- `ACDNN_STATUS_NOT_SUPPORTED`：指定算法不支持当前配置。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.1.21. acdnnGetConvolutionGroupCount() {#3121-acdnngetconvolutiongroupcount}

获取卷积描述符中的分组数。

```cpp
acdnnStatus_t acdnnGetConvolutionGroupCount(
    acdnnConvolutionDescriptor_t convDesc,
    int *groupCount);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `convDesc` | 输入 | 已初始化的卷积描述符 |
| `groupCount` | 输出 | 卷积的 Group 数量 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`convDesc` 无效。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.1.22. acdnnGetConvolutionMathType() {#3122-acdnngetconvolutionmathtype}

获取卷积描述符中的 Math Type。

```cpp
acdnnStatus_t acdnnGetConvolutionMathType(
    acdnnConvolutionDescriptor_t convDesc,
    acdnnMathType_t *mathType);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `convDesc` | 输入 | 已初始化的卷积描述符 |
| `mathType` | 输出 | 卷积使用的 Math Type（`acdnnMathType_t`） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`convDesc` 无效。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.1.23. acdnnGetConvolutionNdDescriptor() {#3123-acdnngetconvolutionnddescriptor}

查询先前初始化的 Nd 卷积描述符。

```cpp
acdnnStatus_t acdnnGetConvolutionNdDescriptor(
    const acdnnConvolutionDescriptor_t convDesc,
    int arrayLengthRequested,
    int *arrayLength,
    int padA[],
    int filterStrideA[],
    int dilationA[],
    acdnnConvolutionMode_t *mode,
    acdnnDataType_t *dataType);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `convDesc` | 输入 | 卷积描述符 |
| `arrayLengthRequested` | 输入 | 请求的维度数（也是 `padA` 等数组的最小长度） |
| `arrayLength` | 输出 | 实际维度数 |
| `padA` | 输出 | 各维度填充 |
| `filterStrideA` | 输出 | 各维度滤波器步幅 |
| `dilationA` | 输出 | 各维度扩张 |
| `mode` | 输出 | 卷积模式 |
| `dataType` | 输出 | 计算数据类型 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`convDesc` 为 NULL 或 `arrayLengthRequested` 为负。
- `ACDNN_STATUS_NOT_SUPPORTED`：超过 `ACDNN_DIM_MAX-2`。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.1.24. acdnnGetConvolutionNdForwardOutputDim() {#3124-acdnngetconvolutionndforwardoutputdim}

推算 Nd 卷积输出张量的各维度大小（用于提前分配内存）。

```cpp
acdnnStatus_t acdnnGetConvolutionNdForwardOutputDim(
    const acdnnConvolutionDescriptor_t convDesc,
    const acdnnTensorDescriptor_t inputTensorDesc,
    const acdnnFilterDescriptor_t filterDesc,
    int nbDims,
    int tensorOutDimA[]);
```

各空间维度计算公式：

```cpp
outputDim = 1 + (inputDim + 2*pad - (((filterDim-1)*dilation) + 1)) / convolutionStride;
```

!!! note
    调用 `acdnnConvolutionForward()` 或 `acdnnConvolutionBackwardData()` 时必须严格使用此函数返回的维度。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `convDesc` | 输入 | 卷积描述符 |
| `inputTensorDesc` | 输入 | 输入张量描述符 |
| `filterDesc` | 输入 | 滤波器描述符 |
| `nbDims` | 输入 | 输出张量维度数 |
| `tensorOutDimA` | 输出 | 长度为 `nbDims` 的数组，存放输出各维度大小 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：描述符为 NULL 或维度不匹配。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.1.25. acdnnGetFoldedConvBackwardDataDescriptors() {#3125-acdnngetfoldedconvbackwarddatadescriptors}

计算后向数据梯度的 Folding 描述符，输出可直接用于 Folding Transform。

```cpp
acdnnStatus_t acdnnGetFoldedConvBackwardDataDescriptors(
    const acdnnHandle_t handle,
    const acdnnFilterDescriptor_t filterDesc,
    const acdnnTensorDescriptor_t diffDesc,
    const acdnnConvolutionDescriptor_t convDesc,
    const acdnnTensorDescriptor_t gradDesc,
    const acdnnTensorFormat_t transformFormat,
    acdnnFilterDescriptor_t foldedFilterDesc,
    acdnnTensorDescriptor_t paddedDiffDesc,
    acdnnConvolutionDescriptor_t foldedConvDesc,
    acdnnTensorDescriptor_t foldedGradDesc,
    acdnnTensorTransformDescriptor_t filterFoldTransDesc,
    acdnnTensorTransformDescriptor_t diffPadTransDesc,
    acdnnTensorTransformDescriptor_t gradFoldTransDesc,
    acdnnTensorTransformDescriptor_t gradUnfoldTransDesc);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `filterDesc` | 输入 | Folding 前的滤波器描述符 |
| `diffDesc` | 输入 | Folding 前的 Diff 描述符 |
| `convDesc` | 输入 | Folding 前的卷积描述符 |
| `gradDesc` | 输入 | Folding 前的 Gradient 描述符 |
| `transformFormat` | 输入 | 折叠使用的目标格式 |
| `foldedFilterDesc` | 输出 | Folded 滤波器描述符 |
| `paddedDiffDesc` | 输出 | Padded Diff 描述符 |
| `foldedConvDesc` | 输出 | Folded 卷积描述符 |
| `foldedGradDesc` | 输出 | Folded Gradient 描述符 |
| `filterFoldTransDesc` | 输出 | 滤波器的 Folding Transform 描述符 |
| `diffPadTransDesc` | 输出 | Diff 的 Folding Transform 描述符 |
| `gradFoldTransDesc` | 输出 | Gradient 的 Folding Transform 描述符 |
| `gradUnfoldTransDesc` | 输出 | Folded Gradient 的 Unfolding Transform 描述符 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：输入为 NULL 或维度超过 4。
- `ACDNN_STATUS_EXECUTION_FAILED`：计算失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.1.26. acdnnSetConvolution2dDescriptor() {#3126-acdnnsetconvolution2ddescriptor}

初始化 2D 卷积描述符。同一描述符前向/后向可复用（对应同一层时）。

```cpp
acdnnStatus_t acdnnSetConvolution2dDescriptor(
    acdnnConvolutionDescriptor_t convDesc,
    int pad_h,
    int pad_w,
    int u,
    int v,
    int dilation_h,
    int dilation_w,
    acdnnConvolutionMode_t mode,
    acdnnDataType_t computeType);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `convDesc` | 输入/输出 | 待初始化的卷积描述符 |
| `pad_h` / `pad_w` | 输入 | 零填充高度 / 宽度 |
| `u` / `v` | 输入 | 垂直 / 水平滤波器步幅 |
| `dilation_h` / `dilation_w` | 输入 | 高度 / 宽度扩张 |
| `mode` | 输入 | `ACDNN_CONVOLUTION` 或 `ACDNN_CROSS_CORRELATION` |
| `computeType` | 输入 | 计算精度 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`convDesc` 为 NULL 或填充为负。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.1.27. acdnnSetConvolutionGroupCount() {#3127-acdnnsetconvolutiongroupcount}

设置卷积描述符中的 Group 数量。

```cpp
acdnnStatus_t acdnnSetConvolutionGroupCount(
    acdnnConvolutionDescriptor_t convDesc,
    int groupCount);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `convDesc` | 输入 / 输出 | 已初始化的卷积描述符 |
| `groupCount` | 输入 | 卷积的 Group 数量 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`convDesc` 无效。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.1.28. acdnnSetConvolutionMathType() {#3128-acdnnsetconvolutionmathtype}

设置卷积描述符的 Math Type（是否允许 Tensor 单元运算）。

```cpp
acdnnStatus_t acdnnSetConvolutionMathType(
    acdnnConvolutionDescriptor_t convDesc,
    acdnnMathType_t mathType);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `convDesc` | 输入 / 输出 | 已初始化的卷积描述符 |
| `mathType` | 输入 | Math Type 枚举值（`acdnnMathType_t`） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`convDesc` 或 `mathType` 无效。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.1.29. acdnnSetConvolutionNdDescriptor() {#3129-acdnnsetconvolutionnddescriptor}

初始化 Nd 卷积描述符。同一描述符前向/后向可复用。计算在 `dataType` 指定的精度下进行（可与输入/输出 Tensor 类型不同）。

```cpp
acdnnStatus_t acdnnSetConvolutionNdDescriptor(
    acdnnConvolutionDescriptor_t convDesc,
    int arrayLength,
    const int padA[],
    const int filterStrideA[],
    const int dilationA[],
    acdnnConvolutionMode_t mode,
    acdnnDataType_t dataType);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `convDesc` | 输入/输出 | 待初始化的卷积描述符 |
| `arrayLength` | 输入 | 卷积维度数 |
| `padA` | 输入 | 各维度零填充 |
| `filterStrideA` | 输入 | 各维度滤波器步幅 |
| `dilationA` | 输入 | 各维度扩张 Factor |
| `mode` | 输入 | `ACDNN_CONVOLUTION` 或 `ACDNN_CROSS_CORRELATION` |
| `dataType` | 输入 | 计算数据类型 |

!!! note
    在 `acdnnSetConvolutionNdDescriptor()` 中使用 `ACDNN_DATA_HALF` 和 `HALF_CONVOLUTION_BWD_FILTER` 不推荐，因为已知它对训练的任何实际用例都没有用。建议在 `acdnnSetTensorNdDescriptor()` 中为输入 Tensor 使用 `ACDNN_DATA_HALF`，在 `acdnnSetConvolutionNdDescriptor()` 中使用 `ACDNN_DATA_FLOAT` 和 `HALF_CONVOLUTION_BWD_FILTER`，这在许多知名的深度学习框架中与自动混合精度（AMP）训练一起使用。

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：满足以下至少一个条件：
  - 描述符 `convDesc` 为 NULL
  - `arrayLengthRequested` 为负数
  - 枚举值 `mode` 具有无效值
  - 枚举值 `dataType` 具有无效值
  - `padA` 的某个元素为严格负数
  - `strideA` 的某个元素为负数或零
  - `dilationA` 的某个元素为负数或零
- `ACDNN_STATUS_NOT_SUPPORTED`：满足以下至少一个条件：
  - `arrayLengthRequested` 大于 `ACDNN_DIM_MAX`

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

### 3.2. 训练数据类型 {#32-训练数据类型}

#### 3.2.1. 结构体类型 {#321-结构体类型}

##### 3.2.1.1. acdnnConvolutionBwdFilterAlgoPerf_t {#3211-acdnnconvolutionbwdfilteralgoperf_t}

承载 `acdnnFindConvolutionBackwardFilterAlgorithm()` 或 `acdnnGetConvolutionBackwardFilterAlgorithm_v7()` 返回的每条算法性能记录。

| 字段 | 类型 | 描述 |
| :--- | :--- | :--- |
| `status` | `acdnnStatus_t` | 该算法的执行状态（`ACDNN_STATUS_ALLOC_FAILED` / `ACDNN_STATUS_INTERNAL_ERROR` / 等） |
| `time` | `float` | 执行耗时（ms） |
| `memory` | `size_t` | 所需工作空间（字节） |
| `determinism` | `acdnnDeterminism_t` | 是否确定性 |
| `mathType` | `acdnnMathType_t` | 数学精度 |
| `reserved` | `int[3]` | 保留 |

### 3.3. 训练 API {#33-训练-api}

#### 3.3.1. acdnnCnnTrainVersionCheck() {#331-acdnncnntrainversioncheck}

检查 `acdnn_cnn_train` 子库版本是否与其他 acDNN 子库一致。

```cpp
acdnnStatus_t acdnnCnnTrainVersionCheck(void);
```

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.3.2. acdnnConvolutionBackwardFilter() {#332-acdnnconvolutionbackwardfilter}

根据前向输入 `x` 和输出梯度 `dy` 计算卷积滤波器梯度 `dw`，使用指定算法 `algo`。

```cpp

acdnnStatus_t acdnnConvolutionBackwardFilter(
    acdnnHandle_t handle,
    const void *alpha,
    const acdnnTensorDescriptor_t xDesc,
    const void *x,
    const acdnnTensorDescriptor_t dyDesc,
    const void *dy,
    const acdnnConvolutionDescriptor_t convDesc,
    const acdnnConvolutionBwdFilterAlgo_t algo,
    void *workspace,
    size_t workspaceSizeInBytes,
    const void *beta,
    const acdnnFilterDescriptor_t dwDesc,
    void *dw);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `alpha` / `beta` | 输入 | 主机端混合系数： `dw = α·grad + β·priorDw` |
| `xDesc` / `x` | 输入 | 前向输入张量描述符 / 设备指针 |
| `dyDesc` / `dy` | 输入 | 输出梯度张量描述符 / 设备指针 |
| `convDesc` | 输入 | 卷积描述符（`acdnnConvolutionDescriptor_t`） |
| `algo` | 输入 | 算法选择（`acdnnConvolutionBwdFilterAlgo_t`） |
| `workspace` / `workspaceSizeInBytes` | 输入 | 工作空间指针及字节数（不需要时可传 NULL / 0） |
| `dwDesc` / `dw` | 输入/输出 | 滤波器梯度描述符 / 设备指针 |

**支持的数据类型组合**

**`acdnnConvolutionBackwardFilter()` 数据类型配置**

| 数据类型组合 | `xDesc`、`dyDesc` 和 dwDesc 数据类型 | `convDesc` 数据类型 |
| :--- | :--- | :--- |
| `TRUE_HALF_CONFIG`| `ACDNN_DATA_HALF` | `ACDNN_DATA_HALF` |
| `PSEUDO_HALF_CONFIG` | `ACDNN_DATA_HALF` | `ACDNN_DATA_FLOAT` |
| `PSEUDO_BFLOAT16_CONFIG` | `ACDNN_DATA_BF16` | `ACDNN_DATA_FLOAT` |
| `FLOAT_CONFIG` | `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` |
| `DOUBLE_CONFIG` | `ACDNN_DATA_DOUBLE` | `ACDNN_DATA_DOUBLE` |

**支持的算法**

下表列出 2D / 3D 卷积各算法的布局、类型及约束。表中缩写：`_ALGO_0` = `ACDNN_CONVOLUTION_BWD_FILTER_ALGO_0`，依此类推；`_NCHW` = `ACDNN_TENSOR_NCHW`，`_NHWC` = `ACDNN_TENSOR_NHWC`，`_NCHW_VECT_C` = `ACDNN_TENSOR_NCHW_VECT_C`。

**2D 卷积 · dwDesc: NHWC**

| 算法名称 | 确定性（是或否） | `dyDesc` 支持的张量格式 | `dxDesc` 支持的张量格式 | 支持的数据类型配置 | 重要事项 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `_ALGO_0` 和 `_ALGO_1` | | `NHWC` `HWC-packed` | `NHWC` `HWC-packed` | `PSEUDO_HALF_CONFIG`<br>`PSEUDO_BFLOAT16_CONFIG`<br>`FLOAT_CONFIG` | |

**2D 卷积 · dwDesc: NCHW**

| 算法名称 | 确定性（是或否） | `dyDesc` 支持的张量格式 | `dxDesc` 支持的张量格式 | 支持的数据类型配置 | 重要事项 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `_ALGO_0` | 否 | 除 `_NCHW_VECT_C` 外的所有格式 | `NCHW` `CHW-packed` | `PSEUDO_HALF_CONFIG`<br>`PSEUDO_BFLOAT16_CONFIG`<br>`FLOAT_CONFIG`<br>`DOUBLE_CONFIG` | 扩张：所有维度大于 0<br>`convDesc` 分组数支持：大于 0 |
| `_ALGO_1` | 是 | 除 `_NCHW_VECT_C` 外的所有格式 | `NCHW` `CHW-packed` | `PSEUDO_HALF_CONFIG`<br>`TRUE_HALF_CONFIG`<br>`PSEUDO_BFLOAT16_CONFIG`<br>`FLOAT_CONFIG`<br>`DOUBLE_CONFIG` | 扩张：所有维度大于 0<br>`convDesc` 分组数支持：大于 0 |
| `_FFT` | 是 | `NCHW` `CHW-packed` | `NCHW` `CHW-packed` | `PSEUDO_HALF_CONFIG` | 扩张：所有维度为 1<br>`convDesc` 分组数支持：大于 0<br>`xDesc` 特征图高度 + 2*`convDesc` 零填充高度必须等于或小于 256<br>`xDesc` 特征图宽度 + 2*`convDesc` 零填充宽度必须等于或小于 256<br>`convDesc` 垂直和水平滤波器步幅必须等于 1<br>dwDesc 滤波器高度必须大于 `convDesc` 零填充高度<br>dwDesc 滤波器宽度必须大于 `convDesc` 零填充宽度 |
| `_ALGO_3` | 否 | 除 `_NCHW_VECT_C` 外的所有格式 | `NCHW` `CHW-packed` | `PSEUDO_HALF_CONFIG`<br>`PSEUDO_BFLOAT16_CONFIG`<br>`FLOAT_CONFIG` | 扩张：所有维度为 1<br>`convDesc` 分组数支持：大于 0 |
| `_WINOGRAD_NONFUSED` | 是 | 除 `_NCHW_VECT_C` 外的所有格式 | `NCHW` `CHW-packed` | `TRUE_HALF_CONFIG`<br>`PSEUDO_HALF_CONFIG`<br>`PSEUDO_BFLOAT16_CONFIG`<br>`FLOAT_CONFIG` | 扩张：所有维度为 1<br>`convDesc` 垂直和水平滤波器步幅必须等于 1<br>`convDesc` 分组数支持：大于 0<br>`convDesc` 滤波器（高度， 宽度）必须为（3,3）或（5,5）<br>如果 dwDesc 滤波器（高度， 宽度）为（5,5），则不支持数据类型 Config `TRUE_HALF_CONFIG` |
| `_FFT_TILING` | 是 | `NCHW` `CHW-packed` | `NCHW` `CHW-packed` | `PSEUDO_HALF_CONFIG`<br>`DOUBLE_CONFIG` | 扩张：所有维度为 1<br>`convDesc` 分组数支持：大于 0<br>`dyDesc` 宽度或高度必须等于 1（与 `xDesc` 中的维度相同）。另一个维度必须小于或等于 256，即当前支持的最大 1D Tile 大小<br>`convDesc` 垂直和水平滤波器步幅必须等于 1<br>dwDesc 滤波器高度必须大于 `convDesc` 零填充高度<br>dwDesc 滤波器宽度必须大于 `convDesc` 零填充宽度 |

**3D 卷积 · dwDesc: NCHW**

| 算法名称（3D 卷积） | 确定性（是或否） | `dyDesc` 支持的张量格式 | `dxDesc` 支持的张量格式 | 支持的数据类型配置 | 重要事项 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `_ALGO_0` | 否 | 除 `_NCHW_VECT_C` 外的所有格式 | `NCDHW` CDHW-packed<br>`NCDHW` W-packed<br>`NDHWC` | `PSEUDO_HALF_CONFIG`<br>`PSEUDO_BFLOAT16_CONFIG`<br>`FLOAT_CONFIG`<br>`DOUBLE_CONFIG` | 扩张：所有维度大于 0<br>`convDesc` 分组数支持：大于 0 |
| `_ALGO_1` | 否 | 除 `_NCHW_VECT_C` 外的所有格式 | `NCDHW` CDHW-packed<br>`NCDHW` W-packed<br>`NDHWC` | `PSEUDO_HALF_CONFIG`<br>`PSEUDO_BFLOAT16_CONFIG`<br>`FLOAT_CONFIG`<br>`DOUBLE_CONFIG` | 扩张：所有维度大于 0<br>`convDesc` 分组数支持：大于 0 |
| `_ALGO_3` | 否 | `NCDHW` 全打包 | `NCDHW` 全打包 | `PSEUDO_HALF_CONFIG`<br>`PSEUDO_BFLOAT16_CONFIG`<br>`FLOAT_CONFIG`<br>`DOUBLE_CONFIG` | 扩张：所有维度大于 0<br>`convDesc` 分组数支持：大于 0 |

**3D 卷积 · dwDesc: NHWC**

| 算法名称（3D 卷积） | 确定性（是或否） | `xDesc` 支持的张量格式 | `dyDesc` 支持的张量格式 | 支持的数据类型配置 | 重要事项 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `_ALGO_1` | 是 | `NDHWC` `HWC-packed` | `NDHWC` `HWC-packed` | `PSEUDO_HALF_CONFIG`<br>`PSEUDO_BFLOAT16_CONFIG`<br>`FLOAT_CONFIG`<br>`TRUE_HALF_CONFIG` | 扩张：所有维度大于 0<br>分组数支持：大于 0 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：必要指针为 NULL 等。
- `ACDNN_STATUS_NOT_SUPPORTED`：负步幅、不支持的组合等。
- `ACDNN_STATUS_MAPPING_ERROR`：内存映射错误。
- `ACDNN_STATUS_EXECUTION_FAILED`：执行失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.3.3. acdnnFindConvolutionBackwardFilterAlgorithmEx() {#333-acdnnfindconvolutionbackwardfilteralgorithmex}

实际运行所有可用算法并按耗时排序返回性能记录（阻塞调用）。同时尝试 `convDesc` 配置的 MathType 和 `ACDNN_DEFAULT_MATH`。

```cpp
acdnnStatus_t acdnnFindConvolutionBackwardFilterAlgorithmEx(
    acdnnHandle_t handle,
    const acdnnTensorDescriptor_t xDesc,
    const void *x,
    const acdnnTensorDescriptor_t dyDesc,
    const void *dy,
    const acdnnConvolutionDescriptor_t convDesc,
    const acdnnFilterDescriptor_t dwDesc,
    void *dw,
    const int requestedAlgoCount,
    int *returnedAlgoCount,
    acdnnConvolutionBwdFilterAlgoPerf_t *perfResults,
    void *workspace,
    size_t workspaceSizeInBytes);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `xDesc` / `x` | 输入 | 输入张量描述符 / 设备指针 |
| `dyDesc` / `dy` | 输入 | 输出梯度张量描述符 / 设备指针 |
| `convDesc` | 输入 | 卷积描述符 |
| `dwDesc` / `dw` | 输入/输出 | 滤波器描述符 / 设备指针（内容会被覆写） |
| `requestedAlgoCount` | 输入 | `perfResults` 最大容量 |
| `returnedAlgoCount` | 输出 | 实际返回的算法数 |
| `perfResults` | 输出 | 按耗时升序排列的性能记录数组 |
| `workspace` / `workspaceSizeInBytes` | 输入 | 工作空间指针及字节数（决定可用算法范围；NULL 视为 0 字节） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：描述符未正确分配等。
- `ACDNN_STATUS_INTERNAL_ERROR`：计时对象分配/释放失败等。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.3.4. acdnnGetConvolutionBackwardFilterAlgorithmMaxCount() {#334-acdnngetconvolutionbackwardfilteralgorithmmaxcount}

查询 Find/Get 系列 API 可返回的最大算法数量。

```cpp
acdnnStatus_t acdnnGetConvolutionBackwardFilterAlgorithmMaxCount(
    acdnnHandle_t handle, int *count);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `count` | 输出 | 最大算法条目数 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：参数无效。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.3.5. acdnnGetConvolutionBackwardFilterAlgorithm_v7() {#335-acdnngetconvolutionbackwardfilteralgorithm_v7}

基于启发式为给定层规格返回所有适用算法，按预估性能降序排列（不实际运行）。需要精确排序时改用 `FindAlgorithmEx()`。

```cpp
acdnnStatus_t acdnnGetConvolutionBackwardFilterAlgorithm_v7(
    acdnnHandle_t handle,
    const acdnnTensorDescriptor_t xDesc,
    const acdnnTensorDescriptor_t dyDesc,
    const acdnnConvolutionDescriptor_t convDesc,
    const acdnnFilterDescriptor_t dwDesc,
    const int requestedAlgoCount,
    int *returnedAlgoCount,
    acdnnConvolutionBwdFilterAlgoPerf_t *perfResults);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `xDesc` | 输入 | 输入张量描述符 |
| `dyDesc` | 输入 | 输出梯度张量描述符 |
| `convDesc` | 输入 | 卷积描述符 |
| `dwDesc` | 输入 | 滤波器描述符 |
| `requestedAlgoCount` | 输入 | `perfResults` 最大容量 |
| `returnedAlgoCount` | 输出 | 实际返回的算法数 |
| `perfResults` | 输出 | 启发式性能记录数组 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：描述符为 NULL 等。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 3.3.6. acdnnGetConvolutionBackwardFilterWorkspaceSize() {#336-acdnngetconvolutionbackwardfilterworkspacesize}

查询指定算法所需的工作空间字节数。

```cpp
acdnnStatus_t acdnnGetConvolutionBackwardFilterWorkspaceSize(
    acdnnHandle_t handle,
    const acdnnTensorDescriptor_t xDesc,
    const acdnnTensorDescriptor_t dyDesc,
    const acdnnConvolutionDescriptor_t convDesc,
    const acdnnFilterDescriptor_t dwDesc,
    const acdnnConvolutionBwdFilterAlgo_t algo,
    size_t *sizeInBytes);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `xDesc` | 输入 | 输入张量描述符 |
| `dyDesc` | 输入 | 输出梯度张量描述符 |
| `convDesc` | 输入 | 卷积描述符 |
| `dwDesc` | 输入 | 滤波器描述符 |
| `algo` | 输入 | 所选算法枚举 |
| `sizeInBytes` | 输出 | 所需工作空间字节数 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：特征图数量不匹配等。
- `ACDNN_STATUS_NOT_SUPPORTED`：指定算法不支持当前描述符组合。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

**比赛关联：** 卷积章对比赛的价值在三点：一是 `acdnnConvolutionBiasActivationForward()` 把 conv+bias(+residual)+activation 融合为一次 kernel 启动，是减少 kernel 数、压 TTFT 的官方手段；二是 INT8/INT8x4/INT8x32 全套数据类型组合表是 ViT 视觉编码器 INT8 量化的能力边界（注意 NHWC 全打包、通道数为 4 的倍数等约束）；三是 `Find*Algorithm`（实测）与 `Get*Algorithm_v7`（启发式）+ 工作空间查询构成卷积自动调优闭环，预热阶段跑 Find、稳态用最优算法可直接提吞吐。

## 4. 高级网络结构 {#4-高级网络结构}

本章覆盖 RNN、Multi-Head Attention、CTC Loss 等高级网络结构的全部算子，推理与训练合并呈现。

### 4.1. 推理数据类型与描述符 {#41-推理数据类型与描述符}

`acdnn_adv_infer.so` 引入 4 个不透明描述符指针（4.1.1）和 10 个枚举（4.1.2），前者覆盖 Attention 与 RNN 两类高阶算子的运行时配置，后者列出 RNN 模式 / 方向 / 数据布局等可选项。

#### 4.1.1. 指向不透明结构体类型的指针 {#411-指向不透明结构体类型的指针}

四个描述符的生命周期都遵循「Create → Set → 用 → Destroy」四步走：

| 描述符指针 | 用途 | Create | Set / 初始化 | Destroy |
| :--- | :--- | :--- | :--- | :--- |
| `acdnnAttnDescriptor_t` | Multi-head Attention 层的全部静态参数 | `acdnnCreateAttnDescriptor()` | `acdnnSetAttnDescriptor()` | `acdnnDestroyAttnDescriptor()` |
| `acdnnRNNDataDescriptor_t` | 单个 RNN 数据集（输入/输出张量）的形状与布局 | `acdnnCreateRNNDataDescriptor()` | `acdnnSetRNNDataDescriptor()` | `acdnnDestroyRNNDataDescriptor()` |
| `acdnnRNNDescriptor_t` | 一次 RNN 运算的网络结构（cell 类型、层数、双向与否……） | `acdnnCreateRNNDescriptor()` | `acdnnSetRNNDescriptor_v8()` 或 `_v6` | `acdnnDestroyRNNDescriptor()` |
| `acdnnSeqDataDescriptor_t` | Multi-head Attention 用的序列容器 |（由 `acdnnCreate*` 系列创建） | `acdnnSetSeqDataDescriptor()` | `acdnnDestroySeqDataDescriptor()` |

##### 4.1.1.1. acdnnAttnDescriptor_t {#4111-acdnnattndescriptor_t}

承载一次 Multi-head Attention 的全部"先设置好就不再变"的参数，主要包括：

- **形状类** ：weight / bias 张量在 linear projection 前后的向量长度；
- **常量类** ：head 数量、softmax smoothing / sharpening 系数；
- **辅助类** ：用于推算临时 buffer 容量的额外设置。

##### 4.1.1.2. acdnnRNNDataDescriptor_t {#4112-acdnnrnndatadescriptor_t}

描述一份**单个** RNN 输入或输出张量的形状、填充、布局，是 `acdnnRNNForward()` 等 API 中"x / y / hx / cx / hy / cy"参数的元数据。

##### 4.1.1.3. acdnnRNNDescriptor_t {#4113-acdnnrnndescriptor_t}

承载一次 RNN 运算的**整体配置** ：cell 类型（RNN / LSTM / GRU）、层数、双向与否、bias 模式、数学模式、projection layers 等。需以 `_v8`（推荐）或 `_v6`（旧）系列 set 函数初始化，[参见 4.2.36](#4236-acdnnsetrnndescriptor_v6) / [4.2.37](#4237-acdnnsetrnndescriptor_v8)。

##### 4.1.1.4. acdnnSeqDataDescriptor_t {#4114-acdnnseqdatadescriptor_t}

描述一个**序列数据**，专供 Multi-head Attention API 使用。底层模型如下：

- VECT 维度承载固定长度的向量；
- 这些向量排列在 TIME / BATCH / BEAM 三个维度上；
- 容器整体**全打包** （fully packed），三轴的相对内外顺序可任选，共有 6 种合法布局。

每个描述符里保存：

| 信息 | 含义 |
| :--- | :--- |
| 数据类型 | 单个向量元素的精度 |
| TIME / BATCH / BEAM / VECT 四维大小 | 形状 |
| 数据布局 | 三个外层轴的内外顺序（共 6 种） |
| 序列长度数组 | 沿 TIME 方向每个 sequence 的实际长度（≤ TIME 维大小） |
| 填充值（可选） | 输出填充向量要写入的常量 |

#### 4.1.2. 枚举类型 {#412-枚举类型}

以下为 `acdnn_adv_infer.so` 库中的枚举类型。

##### 4.1.2.1. acdnnDirectionMode_t {#4121-acdnndirectionmode_t}

`acdnnDirectionMode_t` 是一种枚举类型，用于在 `acdnnRNNForwardInference()`、`acdnnRNNForwardTraining()`、`acdnnRNNBackwardData()` 和 `acdnnRNNBackwardWeights()` 函数中指定循环模式。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_UNIDIRECTIONAL` | 网络从第一个输入到最后一个输入进行循环迭代。 |
| `ACDNN_BIDIRECTIONAL` | 网络的每一层从第一个输入到最后一个输入进行循环迭代，并分别从最后一个输入到第一个输入进行迭代。两者的输出在每次迭代时连接，给出层的输出。 |

##### 4.1.2.2. acdnnForwardMode_t {#4122-acdnnforwardmode_t}

`acdnnForwardMode_t` 是一种枚举类型，用于在 RNN API 中指定推理或训练模式，此参数允许 acDNN Library 更精确地调整工作空间缓冲区的大小，该大小在推理和训练 Regimen 中可能不同。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_FWD_MODE_INFERENCE` | 选择推理模式。 |
| `ACDNN_FWD_MODE_TRAINING` | 选择训练模式。 |

##### 4.1.2.3. acdnnMultiHeadAttnWeightKind_t {#4123-acdnnmultiheadattnweightkind_t}

`acdnnMultiHeadAttnWeightKind_t` 是一种枚举类型，用于在 `acdnnGetMultiHeadAttnWeights()` 函数中指定一组权重或偏置。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_MH_ATTN_Q_WEIGHTS` | 选择 Queries 的输入投影权重。 |
| `ACDNN_MH_ATTN_K_WEIGHTS` | 选择 Keys 的输入投影权重。 |
| `ACDNN_MH_ATTN_V_WEIGHTS` | 选择 Values 的输入投影权重。 |
| `ACDNN_MH_ATTN_O_WEIGHTS` | 选择输出投影权重。 |
| `ACDNN_MH_ATTN_Q_BIASES` | 选择 Queries 的输入投影偏置。 |
| `ACDNN_MH_ATTN_K_BIASES` | 选择 Keys 的输入投影偏置。 |
| `ACDNN_MH_ATTN_V_BIASES` | 选择 Values 的输入投影偏置。 |
| `ACDNN_MH_ATTN_O_BIASES` | 选择输出投影偏置。 |

##### 4.1.2.4. acdnnRNNBiasMode_t {#4124-acdnnrnnbiasmode_t}

`acdnnRNNBiasMode_t` 是一种枚举类型，用于指定 RNN 函数的偏置向量数量。有关基于偏置模式的每个单元类型的方程式，请参阅 `acdnnRNNMode_t` 枚举类型的描述。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_RNN_NO_BIAS` | 应用不使用偏置的 RNN 单元公式。当前版本不支持 |
| `ACDNN_RNN_SINGLE_INP_BIAS` | 应用在输入 GEMM 中使用一个输入偏置向量的 RNN 单元公式。当前版本不支持 |
| `ACDNN_RNN_DOUBLE_BIAS` | 应用使用两个偏置向量的 RNN 单元公式。 |
| `ACDNN_RNN_SINGLE_REC_BIAS` | 应用在循环 GEMM 中使用一个 Recurrent 偏置向量的 RNN 单元公式。当前版本不支持 |

##### 4.1.2.5. acdnnRNNClipMode_t {#4125-acdnnrnnclipmode_t}

`acdnnRNNClipMode_t` 是一种枚举类型，用于选择 LSTM 单元裁剪模式。它与 `acdnnRNNSetClip()`、`acdnnRNNGetClip()` 函数一起使用，并在 LSTM 单元内部使用。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_RNN_CLIP_NONE` | 禁用 LSTM 单元裁剪。 |
| `ACDNN_RNN_CLIP_MINMAX` | 启用 LSTM 单元裁剪。 |

##### 4.1.2.6. acdnnRNNDataLayout_t {#4126-acdnnrnndatalayout_t}

`acdnnRNNDataLayout_t` 是一种枚举类型，用于选择 RNN 数据布局。它在 API 调用 `acdnnGetRNNDataDescriptor()` 和 `acdnnSetRNNDataDescriptor()` 中使用。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_RNN_DATA_LAYOUT_SEQ_MAJOR_UNPACKED` | 数据布局已填充，具有从一个时间步到下一个时间步的外部步幅。 |
| `ACDNN_RNN_DATA_LAYOUT_SEQ_MAJOR_PACKED` | 序列长度已排序并 Packed，如基本 RNN API 中所示。 |
| `ACDNN_RNN_DATA_LAYOUT_BATCH_MAJOR_UNPACKED` | 数据布局已填充，具有从一个 Batch 到下一个 Batch 的外部步幅。 |

##### 4.1.2.7. acdnnRNNInputMode_t {#4127-acdnnrnninputmode_t}

`acdnnRNNInputMode_t` 是一种枚举类型，用于在 `acdnnRNNForwardInference()`、`acdnnRNNForwardTraining()`、`acdnnRNNBackwardData()` 和 `acdnnRNNBackwardWeights()` 函数中指定第一个层的行为。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_LINEAR_INPUT` | 在第一个循环层的输入处执行有偏矩阵乘法。 |
| `ACDNN_SKIP_INPUT` | 在第一个循环层的输入处不执行任何操作。如果使用 `ACDNN_SKIP_INPUT`，则输入张量的主导维度必须等于网络的隐藏状态大小。 |

##### 4.1.2.8. acdnnRNNMode_t {#4128-acdnnrnnmode_t}

`acdnnRNNMode_t` 是一种枚举类型，用于在 `acdnnRNNForwardInference`、`acdnnRNNForwardTraining`、`acdnnRNNBackwardData` 和 `acdnnRNNBackwardWeights` 函数中指定使用的网络 Type。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_RNN_RELU` | 具有 ReLU 激活函数的单门控循环神经网络。在前向传递中，对于给定迭代的输出 $h_{t}$ 可以从循环输入 $h_{t-1}$ 和前一层输入 $x_{t}$ 计算得出，给定矩阵 W、R 和偏置向量，其中 $\text{ReLU}(x) = \max(x, 0)$。如果 `rnnDesc` 中的 `acdnnRNNBiasMode_t` `biasMode` 为 `ACDNN_RNN_DOUBLE_BIAS`（默认模式），则应用以下带有偏置 $b_{W}$ 和 $b_{R}$ 的方程式：$h_{t} = \text{ReLU}(W_{i} x_{t} + R_{i} h_{t-1} + b_{Wi} + b_{Ri})$<br>如果 `rnnDesc` 中的 `acdnnRNNBiasMode_t` `biasMode` 为 `ACDNN_RNN_SINGLE_INP_BIAS` 或 `ACDNN_RNN_SINGLE_REC_BIAS`，则应用以下带有偏置的方程式：$h_{t} = \text{ReLU}(W_{i} x_{t} + R_{i} h_{t-1} + b_{i})$<br>如果 `rnnDesc` 中的 `acdnnRNNBiasMode_t` `biasMode` 为 `ACDNN_RNN_NO_BIAS`，则应用以下方程式：$h_{t} = \text{ReLU}(W_{i} x_{t} + R_{i} h_{t-1})$ |
| `ACDNN_RNN_TANH` | 具有 Tanh 激活函数的单门控循环神经网络。在前向传递中，对于给定迭代的输出 $h_{t}$ 可以从循环输入 $h_{t-1}$ 和前一层输入 $x_{t}$ 计算得出，给定矩阵 W、R 和偏置向量，其中 Tanh 是双曲正切函数。如果 `rnnDesc` 中的 `acdnnRNNBiasMode_t` `biasMode` 为 `ACDNN_RNN_DOUBLE_BIAS`（默认模式），则应用以下带有偏置 $b_{W}$ 和 $b_{R}$ 的方程式：$h_{t} = \tanh(W_{i} x_{t} + R_{i} h_{t-1} + b_{Wi} + b_{Ri})$<br>如果 `rnnDesc` 中的 `acdnnRNNBiasMode_t` `biasMode` 为 `ACDNN_RNN_SINGLE_INP_BIAS` 或 `ACDNN_RNN_SINGLE_REC_BIAS`，则应用以下带有偏置的方程式：$h_{t} = \tanh(W_{i} x_{t} + R_{i} h_{t-1} + b_{i})$<br>如果 `rnnDesc` 中的 `acdnnRNNBiasMode_t` `biasMode` 为 `ACDNN_RNN_NO_BIAS`，则应用以下方程式：$h_{t} = \tanh(W_{i} x_{t} + R_{i} h_{t-1})$ |
| `ACDNN_LSTM` | 没有窥孔连接的四门控 Long Short-Term 内存 (LSTM) 网络。在前向传递中，对于给定迭代的输出 $h_{t}$ 和单元输出 $c_{t}$ 可以从循环输入 $h_{t-1}$、单元输入 $c_{t-1}$ 和前一层输入 $x_{t}$ 计算得出，给定矩阵 W、R 和偏置向量，此外，以下适用：$\sigma$ 是 Sigmoid 算子，使得：$\sigma(x) = 1 / (1 + e^{-x})$，$\circ$ 表示逐元素乘法，Tanh 是双曲正切函数，$i_{t}$、$f_{t}$、$o_{t}$、$c'_{t}$ 分别表示输入、Forget、输出和 New 门控。如果 `rnnDesc` 中的 `acdnnRNNBiasMode_t` `biasMode` 为 `ACDNN_RNN_DOUBLE_BIAS`（默认模式），则应用以下带有偏置 $b_{W}$ 和 $b_{R}$ 的方程式：$i_{t} = \sigma(W_{i} x_{t} + R_{i} h_{t-1} + b_{Wi} + b_{Ri})$，$f_{t} = \sigma(W_{f} x_{t} + R_{f} h_{t-1} + b_{Wf} + b_{Rf})$，$o_{t} = \sigma(W_{o} x_{t} + R_{o} h_{t-1} + b_{Wo} + b_{Ro})$，$c'_{t} = \tanh(W_{c} x_{t} + R_{c} h_{t-1} + b_{Wc} + b_{Rc})$，$c_{t} = f_{t} \circ c_{t-1} + i_{t} \circ c'_{t}$，$h_{t} = o_{t} \circ \tanh(c_{t})$<br>如果 `rnnDesc` 中的 `acdnnRNNBiasMode_t` `biasMode` 为 `ACDNN_RNN_SINGLE_INP_BIAS` 或 `ACDNN_RNN_SINGLE_REC_BIAS`，则应用以下带有偏置的方程式：$i_{t} = \sigma(W_{i} x_{t} + R_{i} h_{t-1} + b_{i})$，$f_{t} = \sigma(W_{f} x_{t} + R_{f} h_{t-1} + b_{f})$，$o_{t} = \sigma(W_{o} x_{t} + R_{o} h_{t-1} + b_{o})$，$c'_{t} = \tanh(W_{c} x_{t} + R_{c} h_{t-1} + b_{c})$，$c_{t} = f_{t} \circ c_{t-1} + i_{t} \circ c'_{t}$，$h_{t} = o_{t} \circ \tanh(c_{t})$<br>如果 `rnnDesc` 中的 `acdnnRNNBiasMode_t` `biasMode` 为 `ACDNN_RNN_NO_BIAS`，则应用以下方程式：$i_{t} = \sigma(W_{i} x_{t} + R_{i} h_{t-1})$，$f_{t} = \sigma(W_{f} x_{t} + R_{f} h_{t-1})$，$o_{t} = \sigma(W_{o} x_{t} + R_{o} h_{t-1})$，$c'_{t} = \tanh(W_{c} x_{t} + R_{c} h_{t-1})$，$c_{t} = f_{t} \circ c_{t-1} + i_{t} \circ c'_{t}$，$h_{t} = o_{t} \circ \tanh(c_{t})$ |
| `ACDNN_GRU` | 由门控循环单元组成的三门控网络。在前向传递中，对于给定迭代的输出 $h_{t}$ 可以从循环输入 $h_{t-1}$ 和前一层输入 $x_{t}$ 计算得出，给定矩阵 W、R 和偏置向量，此外，以下适用：$\sigma$ 是 Sigmoid 算子，使得：$\sigma(x) = 1 / (1 + e^{-x})$，$\circ$ 表示逐元素乘法，Tanh 是双曲正切函数，$i_{t}$、$r_{t}$、$h'_{t}$ 分别表示输入、Reset 和 New 门控。如果 `rnnDesc` 中的 `acdnnRNNBiasMode_t` `biasMode` 为 `ACDNN_RNN_DOUBLE_BIAS`（默认模式），则应用以下带有偏置 $b_{W}$ 和 $b_{R}$ 的方程式：$i_{t} = \sigma(W_{i} x_{t} + R_{i} h_{t-1} + b_{Wi} + b_{Ri})$，$r_{t} = \sigma(W_{r} x_{t} + R_{r} h_{t-1} + b_{Wr} + b_{Rr})$，$h'_{t} = \tanh(W_{h} x_{t} + r_{t} \circ (R_{h} h_{t-1} + b_{Rh}) + b_{Wh})$，$h_{t} = (1 - i_{t}) \circ h'_{t} + i_{t} \circ h_{t-1}$<br>如果 `rnnDesc` 中的 `acdnnRNNBiasMode_t` `biasMode` 为 `ACDNN_RNN_SINGLE_INP_BIAS`，则应用以下带有偏置的方程式：$i_{t} = \sigma(W_{i} x_{t} + R_{i} h_{t-1} + b_{i})$，$r_{t} = \sigma(W_{r} x_{t} + R_{r} h_{t-1} + b_{r})$，$h'_{t} = \tanh(W_{h} x_{t} + r_{t} \circ (R_{h} h_{t-1}) + b_{Wh})$，$h_{t} = (1 - i_{t}) \circ h'_{t} + i_{t} \circ h_{t-1}$<br>如果 `rnnDesc` 中的 `acdnnRNNBiasMode_t` `biasMode` 为 `ACDNN_RNN_SINGLE_REC_BIAS`，则应用以下带有偏置的方程式：$i_{t} = \sigma(W_{i} x_{t} + R_{i} h_{t-1} + b_{i})$，$r_{t} = \sigma(W_{r} x_{t} + R_{r} h_{t-1} + b_{r})$，$h'_{t} = \tanh(W_{h} x_{t} + r_{t} \circ (R_{h} h_{t-1} + b_{Rh}))$，$h_{t} = (1 - i_{t}) \circ h'_{t} + i_{t} \circ h_{t-1}$<br>如果 `rnnDesc` 中的 `acdnnRNNBiasMode_t` `biasMode` 为 `ACDNN_RNN_NO_BIAS`，则应用以下方程式：$i_{t} = \sigma(W_{i} x_{t} + R_{i} h_{t-1})$，$r_{t} = \sigma(W_{r} x_{t} + R_{r} h_{t-1})$，$h'_{t} = \tanh(W_{h} x_{t} + r_{t} \circ (R_{h} h_{t-1}))$，$h_{t} = (1 - i_{t}) \circ h'_{t} + i_{t} \circ h_{t-1}$ |

##### 4.1.2.9. acdnnRNNPaddingMode_t {#4129-acdnnrnnpaddingmode_t}

`acdnnRNNPaddingMode_t` 是一种枚举类型，用于启用或禁用填充输入/输出。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_RNN_PADDED_IO_DISABLED` | 禁用填充输入/输出。 |
| `ACDNN_RNN_PADDED_IO_ENABLED` | 启用填充输入/输出。 |

##### 4.1.2.10. acdnnSeqDataAxis_t {#41210-acdnnseqdataaxis_t}

`acdnnSeqDataAxis_t` 是一种枚举类型，用于索引传递给 `acdnnSetSeqDataDescriptor()` 函数以配置 `acdnnSeqDataDescriptor_t` Type 的序列数据描述符的 `dimA[]` 参数中的有效维度。

`acdnnSeqDataAxis_t` 常量还在 `acdnnSetSeqDataDescriptor()` 调用的 `axis[]` 参数中用于定义序列数据缓冲区在内存中的布局。

有关如何使用 `acdnnSeqDataAxis_t` 枚举类型的详细说明，请参阅 `acdnnSetSeqDataDescriptor()`。

`ACDNN_SEQDATA_DIM_COUNT` 宏定义 `acdnnSeqDataAxis_t` 枚举类型中常量的数量。此值当前设置为 4。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_SEQDATA_TIME_DIM` | 标识 TIME（序列长度）维度或指定数据布局中的 TIME。 |
| `ACDNN_SEQDATA_BATCH_DIM` | 标识 BATCH 维度或指定数据布局中的 BATCH。 |
| `ACDNN_SEQDATA_BEAM_DIM` | 标识 BEAM 维度或指定数据布局中的 BEAM。 |
| `ACDNN_SEQDATA_VECT_DIM` | 标识 VECT（向量）维度或指定数据布局中的 VECT。 |

### 4.2. 推理 API {#42-推理-api}

`acdnn_adv_infer.so` 导出的全部公开 API，按功能可大致分四组：版本检查、`Create / Set / Get / Destroy` 系列描述符接口、RNN 正向计算（Forward / ForwardInference）、Multi-Head Attention 正向计算与权重定位（`MultiHeadAttnForward` / `GetMultiHeadAttnWeights` 等）。

#### 4.2.1. acdnnAdvInferVersionCheck() {#421-acdnnadvinferversioncheck}

```cpp
acdnnStatus_t acdnnAdvInferVersionCheck(void);
```

校验当前 `acdnn_adv_infer` 子库的版本是否与其他 acDNN 子库吻合。

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

> **关于下述 `Create*Descriptor()`（4.2.2–4.2.4）** ：分配主机内存并把所有字段初始化为缺省值；输出指针为 NULL 时返回 `ACDNN_STATUS_BAD_PARAM`，资源不足时返回 `ACDNN_STATUS_ALLOC_FAILED`，成功为 `ACDNN_STATUS_SUCCESS`。

#### 4.2.2. acdnnCreateAttnDescriptor() {#422-acdnncreateattndescriptor}

```cpp
acdnnStatus_t acdnnCreateAttnDescriptor(acdnnAttnDescriptor_t *attnDesc);
```

为 `acdnnAttnDescriptor_t` 分配存储；分配失败时把 `*attnDesc` 写为 NULL。需用 `acdnnSetAttnDescriptor()` 完成实际配置，用 `acdnnDestroyAttnDescriptor()` 释放。

- `attnDesc` —*输出*：用于接收新 Attention 描述符地址的指针。

#### 4.2.3. acdnnCreateRNNDataDescriptor() {#423-acdnncreaternndatadescriptor}

```cpp
acdnnStatus_t acdnnCreateRNNDataDescriptor(
    acdnnRNNDataDescriptor_t *RNNDataDesc);
```

为 `acdnnRNNDataDescriptor_t` 分配存储。

- `RNNDataDesc` —*输出*：用于接收新 RNN 数据描述符地址的指针。

#### 4.2.4. acdnnCreateRNNDescriptor() {#424-acdnncreaternndescriptor}

```cpp
acdnnStatus_t acdnnCreateRNNDescriptor(
    acdnnRNNDescriptor_t *rnnDesc);
```

为 `acdnnRNNDescriptor_t` 分配存储。

- `rnnDesc` —*输出*：用于接收新 RNN 描述符地址的指针。

> **关于下述 `Destroy*Descriptor()`（4.2.5–4.2.8）** ：释放对应描述符的内存，传入 NULL 是 NOP，参数若不是来自配套 `Create*` 的指针（或被重复销毁），行为未定义。统一返回 `ACDNN_STATUS_SUCCESS`。

#### 4.2.5. acdnnDestroyAttnDescriptor() {#425-acdnndestroyattndescriptor}

```cpp
acdnnStatus_t acdnnDestroyAttnDescriptor(acdnnAttnDescriptor_t attnDesc);
```

释放 `acdnnAttnDescriptor_t`。

- `attnDesc` —*输入*：要销毁的 Attention 描述符。

#### 4.2.6. acdnnDestroyRNNDataDescriptor() {#426-acdnndestroyrnndatadescriptor}

```cpp
acdnnStatus_t acdnnDestroyRNNDataDescriptor(
    acdnnRNNDataDescriptor_t RNNDataDesc);
```

释放 `acdnnRNNDataDescriptor_t`。

- `RNNDataDesc` —*输入*：要销毁的 RNN 数据描述符。

#### 4.2.7. acdnnDestroyRNNDescriptor() {#427-acdnndestroyrnndescriptor}

```cpp
acdnnStatus_t acdnnDestroyRNNDescriptor(
    acdnnRNNDescriptor_t rnnDesc);
```

释放 `acdnnRNNDescriptor_t`。

- `rnnDesc` —*输入*：要销毁的 RNN 描述符。

#### 4.2.8. acdnnDestroySeqDataDescriptor() {#428-acdnndestroyseqdatadescriptor}

```cpp
acdnnStatus_t acdnnDestroySeqDataDescriptor(
    acdnnSeqDataDescriptor_t seqDataDesc);
```

释放 `acdnnSeqDataDescriptor_t`。

- `seqDataDesc` —*输入*：要销毁的序列数据描述符。


#### 4.2.9. acdnnGetAttnDescriptor() {#429-acdnngetattndescriptor}

从先前创建的 Attention 描述符中检索设置。不需要检索的值时可为除 `attnDesc` 之外的任何指针传 NULL。

```cpp
acdnnStatus_t acdnnGetAttnDescriptor(
    acdnnAttnDescriptor_t attnDesc,
    unsigned *attnMode,
    int *nHeads,
    double *smScaler,
    acdnnDataType_t *dataType,
    acdnnDataType_t *computePrec,
    acdnnMathType_t *mathType,
    acdnnDropoutDescriptor_t *attnDropoutDesc,
    acdnnDropoutDescriptor_t *postDropoutDesc,
    int *qSize,
    int *kSize,
    int *vSize,
    int *qProjSize,
    int *kProjSize,
    int *vProjSize,
    int *oProjSize,
    int *qoMaxSeqLength,
    int *kvMaxSeqLength,
    int *maxBatchSize,
    int *maxBeamSize);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `attnDesc` | 输入 | Attention 描述符 |
| `attnMode` | 输出 | 存储二进制注意力标志的指针 |
| `nHeads` | 输出 | 存储注意力头数量的指针 |
| `smScaler` | 输出 | 存储 Softmax 平滑/锐化系数的指针 |
| `dataType` | 输出 | Attention 权重、序列数据输入/输出的数据类型 |
| `computePrec` | 输出 | 存储计算精度的指针 |
| `mathType` | 输出 | Tensor Cell 设置 |
| `attnDropoutDesc` | 输出 | 应用于 Softmax 输出的 Dropout 描述符 |
| `postDropoutDesc` | 输出 | 应用于 Multi-head Attention 输出的 Dropout 描述符 |
| `qSize` / `kSize` / `vSize` | 输出 | Q、K、V 嵌入向量长度 |
| `qProjSize` / `kProjSize` / `vProjSize` | 输出 | 输入投影后的 Q、K、V 嵌入向量长度 |
| `oProjSize` | 输出 | 投影后输出向量长度 |
| `qoMaxSeqLength` | 输出 | Q/O 相关序列数据描述符的最大序列长度 |
| `kvMaxSeqLength` | 输出 | K/V 相关序列数据描述符的最大序列长度 |
| `maxBatchSize` | 输出 | `acdnnSeqDataDescriptor_t` 容器的最大批量大小 |
| `maxBeamSize` | 输出 | `acdnnSeqDataDescriptor_t` 容器的最大束大小 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：无效输入参数。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.10. acdnnGetMultiHeadAttnWeights() {#4210-acdnngetmultiheadattnweights}

获取权重或偏置 Tensor 的形状，并检索位于权重缓冲区中的张量数据起始地址。通过 `wKind` 选择特定 Tensor（参见 `acdnnMultiHeadAttnWeightKind_t`）。

```cpp
acdnnStatus_t acdnnGetMultiHeadAttnWeights(
    acdnnHandle_t handle,
    const acdnnAttnDescriptor_t attnDesc,
    acdnnMultiHeadAttnWeightKind_t wKind,
    size_t weightSizeInBytes,
    const void *weights,
    acdnnTensorDescriptor_t wDesc,
    void **wAddr);
```

当在 Attention 描述符中设置了 `ACDNN_ATTN_ENABLE_PROJ_BIASES` 标志时，输入和输出投影将使用偏置。有关控制投影偏置的标志说明，请参阅 `acdnnSetAttnDescriptor()`。当相应的权重或偏置 Tensor 不存在时，函数会将 NULL 写入 `wAddr` 指向的存储位置，并在 `wDesc` 张量描述符中返回零维度的描述，此时， `acdnnGetMultiHeadAttnWeights()` 函数仍返回 `ACDNN_STATUS_SUCCESS` 状态。

acDNN multiHeadAttention 示例代码演示了如何访问多头注意力权重。虽然包含权重和偏置的缓冲区应在真武 PPU 内存中分配，但开发者可将其复制到主机内存，并使用主机权重地址调用 `acdnnGetMultiHeadAttnWeights()` 函数，以获取主机内存中的张量指针。此方案允许开发者直接在 CPU 内存中检查可训练参数。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `attnDesc` | 输入 | 先前配置的 Attention 描述符 |
| `wKind` | 输入 | 指定应检索哪个权重/偏置 Tensor 的枚举值 |
| `weightSizeInBytes` | 输入 | 所有 Multi-head Attention 权重和偏置的缓冲区大小 |
| `weights` | 输入 | 主机或设备内存中权重缓冲区的指针 |
| `wDesc` | 输出 | 权重/偏置 Tensor 形状描述符。权重： `dimA[] = {nHeads, projectedSize, originalSize}`；偏置： `dimA[] = {nHeads, projectedSize, 1}`。 `strideA[]` 描述内存布局 |
| `wAddr` | 输出 | 请求 Tensor 起始地址的指针；投影被禁用时为 NULL |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：无效或不兼容的输入参数，如 `wKind` 无效或 `weightSizeInBytes` 太小。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.11. acdnnGetRNNBiasMode() {#4211-acdnngetrnnbiasmode}

请使用 `acdnnGetRNNDescriptor_v8()` 代替 `acdnnGetRNNBiasMode()`。

```cpp
acdnnStatus_t acdnnGetRNNBiasMode(
    acdnnRNNDescriptor_t rnnDesc,
    acdnnRNNBiasMode_t *biasMode);
```

检索由 `acdnnSetRNNBiasMode()` 配置的 RNN 偏置模式。 `acdnnCreateRNNDescriptor()` 后默认值为 `ACDNN_RNN_DOUBLE_BIAS`。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `rnnDesc` | 输入 | 先前创建的 RNN 描述符 |
| `biasMode` | 输出 | 保存 RNN 偏置模式的指针 |

返回码：

- `ACDNN_STATUS_BAD_PARAM`：`rnnDesc` 或 `*biasMode` 为 NULL。
- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.12. acdnnGetRNNDataDescriptor() {#4212-acdnngetrnndatadescriptor}

检索先前创建的 RNN 数据描述符对象的设置。

```cpp
acdnnStatus_t acdnnGetRNNDataDescriptor(
    acdnnRNNDataDescriptor_t RNNDataDesc,
    acdnnDataType_t *dataType,
    acdnnRNNDataLayout_t *layout,
    int *maxSeqLength,
    int *batchSize,
    int *vectorSize,
    int arrayLengthRequested,
    int seqLengthArray[],
    void *paddingFill);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `RNNDataDesc` | 输入 | 先前创建并初始化的 RNN 数据描述符 |
| `dataType` | 输出 | 主机内存指针，保存 RNN 数据 Tensor 的数据类型 |
| `layout` | 输出 | 主机内存指针，保存 RNN 数据 Tensor 的内存布局 |
| `maxSeqLength` | 输出 | 最大序列长度（含填充向量） |
| `batchSize` | 输出 | 小批量中的序列数量 |
| `vectorSize` | 输出 | 每个时间步的向量长度（嵌入大小） |
| `arrayLengthRequested` | 输入 | 用户为 `seqLengthArray` 申请的元素数量 |
| `seqLengthArray` | 输出 | 主机内存指针，保存各序列长度； `arrayLengthRequested` 为 0 时可为 NULL |
| `paddingFill` | 输出 | 主机内存指针，保存用户定义的填充 Symbol（与数据 Tensor 同类型） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：必要指针为 NULL 或描述符无效。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.13. acdnnGetRNNDescriptor_v6() {#4213-acdnngetrnndescriptor_v6}

请使用 `acdnnGetRNNDescriptor_v8()` 代替 `acdnnGetRNNDescriptor_v6()`。

```cpp
acdnnStatus_t acdnnGetRNNDescriptor_v6(
    acdnnHandle_t handle,
    acdnnRNNDescriptor_t rnnDesc,
    int *hiddenSize,
    int *numLayers,
    acdnnDropoutDescriptor_t *dropoutDesc,
    acdnnRNNInputMode_t *inputMode,
    acdnnDirectionMode_t *direction,
    acdnnRNNMode_t *cellMode,
    acdnnRNNAlgo_t *algo,
    acdnnDataType_t *mathPrec);
```

检索由 `acdnnSetRNNDescriptor_v6()` 配置的 RNN 网络参数。所有指针均不得为 NULL，否则返回 `ACDNN_STATUS_BAD_PARAM`。不检查检索到的参数的有效性。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `rnnDesc` | 输入 | 先前创建并初始化的 RNN 描述符 |
| `hiddenSize` | 输出 | 隐藏状态大小（各层相同） |
| `numLayers` | 输出 | RNN 层数量 |
| `dropoutDesc` | 输出 | 先前配置的 Dropout 描述符句柄 |
| `inputMode` | 输出 | 第一个 RNN 层的输入模式 |
| `direction` | 输出 | 单向/双向模式 |
| `cellMode` | 输出 | RNN 单元类型 |
| `algo` | 输出 | RNN 算法类型 |
| `mathPrec` | 输出 | 数学精度 Type |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：至少一个指针为 NULL。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.14. acdnnGetRNNDescriptor_v8() {#4214-acdnngetrnndescriptor_v8}

检索由 `acdnnSetRNNDescriptor_v8()` 配置的 RNN 网络参数。不需要的值可为除 `rnnDesc` 之外的任何指针传 NULL。不检查检索到的参数的有效性。

```cpp
acdnnStatus_t acdnnGetRNNDescriptor_v8(
    acdnnRNNDescriptor_t rnnDesc,
    acdnnRNNAlgo_t *algo,
    acdnnRNNMode_t *cellMode,
    acdnnRNNBiasMode_t *biasMode,
    acdnnDirectionMode_t *dirMode,
    acdnnRNNInputMode_t *inputMode,
    acdnnDataType_t *dataType,
    acdnnDataType_t *mathPrec,
    acdnnMathType_t *mathType,
    int32_t *inputSize,
    int32_t *hiddenSize,
    int32_t *projSize,
    int32_t *numLayers,
    acdnnDropoutDescriptor_t *dropoutDesc,
    uint32_t *auxFlags);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `rnnDesc` | 输入 | 先前创建并初始化的 RNN 描述符 |
| `algo` | 输出 | RNN 算法类型 |
| `cellMode` | 输出 | RNN 单元类型 |
| `biasMode` | 输出 | RNN 偏置模式（`acdnnRNNBiasMode_t`） |
| `dirMode` | 输出 | 单向/双向模式 |
| `inputMode` | 输出 | 第一个 RNN 层的输入模式 |
| `dataType` | 输出 | RNN 权重/偏置的数据类型 |
| `mathPrec` | 输出 | 数学精度 Type |
| `mathType` | 输出 | Tensor 单元首选选项 |
| `inputSize` | 输出 | 输入向量大小 |
| `hiddenSize` | 输出 | 隐藏状态大小（各层相同） |
| `projSize` | 输出 | 循环投影后的 LSTM 单元输出大小 |
| `numLayers` | 输出 | RNN 层数量 |
| `dropoutDesc` | 输出 | 先前配置的 Dropout 描述符句柄 |
| `auxFlags` | 输出 | 各种 RNN 选项标志 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`rnnDesc` 为 NULL。
- `ACDNN_STATUS_NOT_INITIALIZED`：使用旧版 `acdnnSetRNNDescriptor_v6()` 配置。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.15. acdnnGetRNNLinLayerBiasParams() {#4215-acdnngetrnnlinlayerbiasparams}

请使用 `acdnnGetRNNWeightParams()` 代替 `acdnnGetRNNLinLayerBiasParams()`。

```cpp
acdnnStatus_t acdnnGetRNNLinLayerBiasParams(
    acdnnHandle_t handle,
    const acdnnRNNDescriptor_t rnnDesc,
    const int pseudoLayer,
    const acdnnTensorDescriptor_t xDesc,
    const acdnnFilterDescriptor_t wDesc,
    const void *w,
    const int linLayerID,
    acdnnFilterDescriptor_t linLayerBiasDesc,
    void **linLayerBias);
```

获取由 `rnnDesc` 定义的循环网络中每个伪层内每个 RNN 偏置列向量的指针和描述符。函数以行和列两个维度返回偏置向量大小。

由于历史原因，滤波器描述符中的最小维度数量为三。
```cpp
filterDimA[0] = total_size,
filterDimA[1] = 1,
filterDimA[2] = 1;
```

在 acDNN 7.1.1 中格式更改为（参见 `acdnnGetFilterNdDescriptor()`）：

```cpp
filterDimA[0] = 1,
filterDimA[1] = rows,
filterDimA[2] = 1;  // 列数
```

两种情况下均应忽略滤波器描述符的 Format 字段。

acDNN 的 RNN 在单元非线性函数之前使用两个偏置向量（方程式参见 `acdnnRNNMode_t`）。若 `linLayerID` 引用不存在的偏置，则 `linLayerBiasDesc` 设为清零的滤波器描述符：

```cpp
filterDimA[0] = 0,
filterDimA[1] = 0,
filterDimA[2] = 2;
```

并将 `linLayerBias` 设为 NULL。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `rnnDesc` | 输入 | 先前初始化的 RNN 描述符 |
| `pseudoLayer` | 输入 | 要查询的伪层（见下方说明） |
| `xDesc` | 输入 | 全打包张量描述符，描述一次循环迭代的输入 |
| `wDesc` | 输入 | 描述 RNN 权重的滤波器描述符 |
| `w` | 输入 | `wDesc` 关联的设备内存数据指针 |
| `linLayerID` | 输入 | 偏置向量的 Linear ID 索引（见下方说明） |
| `linLayerBiasDesc` | 输出 | 滤波器描述符句柄 |
| `linLayerBias` | 输出 | `linLayerBiasDesc` 关联的设备内存数据指针 |

**pseudo 层说明** ：Unidirectional RNN 中伪层等同于物理层（0=输入层， 1=第一隐藏层）。双向 RNN 中数量翻倍：0=前向输入， 1=Backward 输入， 2=前向 Hidden，依此类推。

**lin 层 ID 含义** （取决于 `cellMode`）：
- `ACDNN_RNN_RELU` / `ACDNN_RNN_TANH`：0=前层输入权重， 1=前时间步隐藏状态权重。
- `ACDNN_LSTM`：0-3=前层输入， 4-7=前时间步隐藏状态， 8=投影矩阵。门控映射：0/4=输入， 1/5=遗忘， 2/6=新单元， 3/7=输出。
- `ACDNN_GRU`：0-2=前层输入， 3-5=前时间步隐藏状态。门控映射：0/3=重置， 1/4=更新， 2/5=新隐藏。

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：不支持的配置。
- `ACDNN_STATUS_BAD_PARAM`：必要指针为 NULL。
- `ACDNN_STATUS_INVALID_VALUE`：元素超出 `w` 缓冲区边界。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.16. acdnnGetRNNLinLayerMatrixParams() {#4216-acdnngetrnnlinlayermatrixparams}

请使用 `acdnnGetRNNWeightParams()` 代替 `acdnnGetRNNLinLayerMatrixParams()`。

```cpp
acdnnStatus_t acdnnGetRNNLinLayerMatrixParams(
    acdnnHandle_t handle,
    const acdnnRNNDescriptor_t rnnDesc,
    const int pseudoLayer,
    const acdnnTensorDescriptor_t xDesc,
    const acdnnFilterDescriptor_t wDesc,
    const void *w,
    const int linLayerID,
    acdnnFilterDescriptor_t linLayerMatDesc,
    void **linLayerMat);
```

获取由 `rnnDesc` 定义的循环网络中每个伪层内每个 RNN 权重矩阵的指针和描述符。

!!! note
    该函数不在 `linLayerMatDesc` 滤波器描述符中报告每个权重矩阵中的元素总数，而是以两个维度返回矩阵大小：行和列，此外，当权重矩阵不存在时（例如，由于 `ACDNN_SKIP_INPUT` 模式），该函数在 `linLayerMat` 中返回 NULL，并且 `linLayerMatDesc` 的所有字段都为零。

函数以行和列两个维度返回矩阵大小，方便打印和初始化。元素按行主序排列。由于历史原因滤波器描述符最小维度为三；检索时应忽略 "format" 字段。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `rnnDesc` | 输入 | 先前初始化的 RNN 描述符 |
| `pseudoLayer` | 输入 | 要查询的伪层（规则同 4.2.15） |
| `xDesc` | 输入 | 全打包张量描述符，描述一次循环迭代的输入 |
| `wDesc` | 输入 | 描述 RNN 权重的滤波器描述符 |
| `w` | 输入 | `wDesc` 关联的设备内存数据指针 |
| `linLayerID` | 输入 | Linear 层 ID（含义取决于 `mode`，见下方说明） |
| `linLayerMatDesc` | 输出 | 滤波器描述符句柄；Matrix 不存在时所有字段为零 |
| `linLayerMat` | 输出 | 设备内存数据指针；Matrix 不存在时为 NULL |

**lin 层 ID 含义** （取决于 `mode`，详见 [`acdnnRNNMode_t`](#4128-acdnnrnnmode_t)）：
- `ACDNN_RNN_RELU` / `ACDNN_RNN_TANH`：0=前层输入偏置， 1=循环输入偏置。
- `ACDNN_LSTM`：0-3=前层输入偏置， 4-7=循环输入偏置。门控映射：0/4=输入， 1/5=遗忘， 2/6=新记忆， 3/7=输出。
- `ACDNN_GRU`：0-2=前层输入偏置， 3-5=循环输入偏置。门控映射：0/3=重置， 1/4=更新， 2/5=新记忆。

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：不支持的配置。
- `ACDNN_STATUS_BAD_PARAM`：必要指针为 NULL。
- `ACDNN_STATUS_INVALID_VALUE`：元素超出 `w` 缓冲区边界。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.17. acdnnGetRNNMatrixMathType() {#4217-acdnngetrnnmatrixmathtype}

请使用 `acdnnGetRNNDescriptor_v8()` 代替 `acdnnGetRNNMatrixMathType()`。

```cpp
acdnnStatus_t acdnnGetRNNMatrixMathType(
acdnnRNNDescriptor_t rnnDesc,
acdnnMathType_t *mType);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `rnnDesc` | 输入 | 先前创建并初始化的 RNN 描述符 |
| `mType` | 输出 | 存储首选 Tensor 单元设置的地址 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`rnnDesc` 或 `mType` 为 NULL。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.18. acdnnGetRNNParamsSize() {#4218-acdnngetrnnparamssize}

请使用 `acdnnGetRNNWeightSpaceSize()` 代替 `acdnnGetRNNParamsSize()`。

```cpp
acdnnStatus_t acdnnGetRNNParamsSize(
    acdnnHandle_t handle,
    const acdnnRNNDescriptor_t rnnDesc,

    const acdnnTensorDescriptor_t xDesc,
    size_t *sizeInBytes,
    acdnnDataType_t dataType);
```

查询执行由 `rnnDesc` 描述的 RNN 所需的参数空间量（输入维度由 `xDesc` 定义）。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `rnnDesc` | 输入 | 先前已初始化的 RNN 描述符 |
| `xDesc` | 输入 | 全打包张量描述符，描述单次循环迭代的输入 |
| `sizeInBytes` | 输出 | 执行 RNN 所需的最小设备内存量（字节） |
| `dataType` | 输入 | 参数的数据类型 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：描述符无效。
- `ACDNN_STATUS_NOT_SUPPORTED`：不支持 RNN/张量描述符组合。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.19. acdnnGetRNNProjectionLayers() {#4219-acdnngetrnnprojectionlayers}

!!! note
    请使用 `acdnnGetRNNDescriptor_v8()` 替代 `acdnnGetRNNProjectionLayers()`。

```cpp
acdnnStatus_t acdnnGetRNNProjectionLayers(
    acdnnHandle_t handle,
    const acdnnRNNDescriptor_t rnnDesc,
    int *recProjSize,
    int *outProjSize);
```

检索当前 RNN 投影参数。默认投影禁用，返回 `recProjSize == hiddenSize`、`outProjSize == 0`。用 `acdnnSetRNNProjectionLayers()` 启用。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `rnnDesc` | 输入 | 先前创建并初始化的 RNN 描述符 |
| `recProjSize` | 输出 | 循环投影大小 |
| `outProjSize` | 输出 | 输出投影大小 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：传递了 NULL 指针。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.20. acdnnGetRNNTempSpaceSizes() {#4220-acdnngetrnntempspacesizes}

根据 `rnnDesc` 中的网络 Geometry、`fMode` 指定的用途（推理/训练）及 `xDesc` 的数据维度计算工作空间和预留空间缓冲区大小。数据维度变化时须重新调用（缓冲区大小并非单调递增）。

```cpp
acdnnStatus_t acdnnGetRNNTempSpaceSizes(
    acdnnHandle_t handle,
    acdnnRNNDescriptor_t rnnDesc,
    acdnnForwardMode_t fMode,
    acdnnRNNDataDescriptor_t xDesc,
    size_t *workspaceSize,
    size_t *reserveSpaceSize);
```

不需要的值可为 `workspaceSize` 或 `reserveSpaceSize` 传 NULL。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `rnnDesc` | 输入 | 先前已初始化的 RNN 描述符 |
| `fMode` | 输入 | 推理或训练模式。推理时预留空间大小返回零 |
| `xDesc` | 输入 | RNN 数据描述符，指定 `maxSeqLength` 和 `batchSize` |
| `workspaceSize` | 输出 | 工作空间缓冲区所需最小设备内存（字节）；用作临时 Read/Write 缓冲区 |
| `reserveSpaceSize` | 输出 | 预留空间缓冲区所需最小设备内存（字节）；用于向 Backward 函数传递中间结果 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：无效输入参数。
- `ACDNN_STATUS_NOT_SUPPORTED`：不兼容的参数组合。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.21. acdnnGetRNNTrainingReserveSize() {#4221-acdnngetrnntrainingreservesize}

!!! note
    请使用 `acdnnGetRNNTempSpaceSizes()` 替代 `acdnnGetRNNTrainingReserveSize()`。

```cpp
acdnnStatus_t acdnnGetRNNTrainingReserveSize(
    acdnnHandle_t handle,
    const acdnnRNNDescriptor_t rnnDesc,
    const int seqLength,
    const acdnnTensorDescriptor_t *xDesc,
    size_t *sizeInBytes);
```

查询训练 RNN 所需的 Reserved Space 量。同一缓冲区须传递给 `acdnnRNNForwardTraining()`、`acdnnRNNBackwardData()` 和 `acdnnRNNBackwardWeights()`。每次调用会覆盖内容，但可在调用间备份恢复。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `rnnDesc` | 输入 | 先前已初始化的 RNN 描述符 |
| `seqLength` | 输入 | Unroll 的迭代数量；不得超过 `acdnnGetRNNWorkspaceSize()` 中使用的值 |
| `xDesc` | 输入 | 张量描述符数组（每迭代一个）；批量大小可递减但不可递增，向量长度须一致 |
| `sizeInBytes` | 输出 | 预留空间所需的最小设备内存量（字节） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：描述符无效。
- `ACDNN_STATUS_NOT_SUPPORTED`：数据类型不支持。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.22. acdnnGetRNNWeightParams() {#4222-acdnngetrnnweightparams}

获取循环网络中每个伪层内每个 RNN 权重矩阵和偏置向量的起始地址和形状。

```cpp
acdnnStatus_t acdnnGetRNNWeightParams(
    acdnnHandle_t handle,
    acdnnRNNDescriptor_t rnnDesc,
    int32_t pseudoLayer,
    size_t weightSpaceSize,
    const void *weightSpace,
    int32_t linLayerID,
    acdnnTensorDescriptor_t mDesc,
    void **mAddr,
    acdnnTensorDescriptor_t bDesc,
    void **bAddr);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `rnnDesc` | 输入 | 先前已初始化的 RNN 描述符 |
| `pseudoLayer` | 输入 | 要查询的伪层（规则同 4.2.15） |
| `weightSpaceSize` | 输入 | 权重空间缓冲区大小（字节） |
| `weightSpace` | 输入 | 权重空间缓冲区指针 |
| `linLayerID` | 输入 | 权重矩阵 / 偏置向量的 Linear ID（见下方说明） |
| `mDesc` | 输出 | 权重矩阵形状描述符： `dimA[3] = {1, rows, cols}`；不存在时维度数量为零 |
| `mAddr` | 输出 | 权重矩阵起始地址；不存在时为 NULL |
| `bDesc` | 输出 | 偏置向量形状描述符： `dimA[3] = {1, rows, 1}`；不存在时维度数量为零 |
| `bAddr` | 输出 | 偏置向量起始地址；不存在时为 NULL |

**lin 层 ID 含义** （取决于 `cellMode`，详见 [`acdnnRNNMode_t`](#4128-acdnnrnnmode_t)）：
- `ACDNN_RNN_RELU` / `ACDNN_RNN_TANH`：0=前层输入， 1=前时间步隐藏状态。
- `ACDNN_LSTM`：0-3=前层输入， 4-7=前时间步隐藏状态， 8=投影矩阵（无偏置）。门控映射：0/4=输入， 1/5=遗忘， 2/6=新单元状态， 3/7=输出。
- `ACDNN_GRU`：0-2=前层输入， 3-5=前时间步隐藏状态。门控映射：0/3=重置， 1/4=更新， 2/5=新隐藏状态。

权重矩阵不存在的情况：选择 `ACDNN_SKIP_INPUT` 时第一层输入 GEMM 矩阵；LSTM 投影功能禁用时。

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`pseudoLayer` 超范围或 `linLayerID < 0` 或 `> 8`。
- `ACDNN_STATUS_INVALID_VALUE`：元素超出缓冲区边界。
- `ACDNN_STATUS_NOT_INITIALIZED`：使用旧版 `acdnnSetRNNDescriptor_v6()` 配置。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.23. acdnnGetRNNWeightSpaceSize() {#4223-acdnngetrnnweightspacesize}

报告权重空间缓冲区所需大小（字节），用于保存所有 RNN 权重矩阵和偏置向量。

```cpp
acdnnStatus_t acdnnGetRNNWeightSpaceSize(
    acdnnHandle_t handle,
    acdnnRNNDescriptor_t rnnDesc,
    size_t *weightSpaceSize);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `rnnDesc` | 输入 | 先前已初始化的 RNN 描述符 |
| `weightSpaceSize` | 输出 | 所有可训练参数所需的最小设备内存（字节） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：任何输入参数为 NULL。
- `ACDNN_STATUS_NOT_INITIALIZED`：使用旧版 `acdnnSetRNNDescriptor_v6()` 配置。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.24. acdnnGetRNNWorkspaceSize() {#4224-acdnngetrnnworkspacesize}

!!! note
    请使用 `acdnnGetRNNTempSpaceSizes()` 替代 `acdnnGetRNNWorkspaceSize()`。

```cpp
acdnnStatus_t acdnnGetRNNWorkspaceSize(
    acdnnHandle_t handle,
    const acdnnRNNDescriptor_t rnnDesc,
    const int seqLength,
    const acdnnTensorDescriptor_t *xDesc,
    size_t *sizeInBytes);
```

查询执行 RNN 所需的工作空间量（输入维度由 `xDesc` 定义）。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `rnnDesc` | 输入 | 先前已初始化的 RNN 描述符 |
| `seqLength` | 输入 | Unroll 的迭代数量；分配的工作空间不可用于更长序列 |
| `xDesc` | 输入 | 张量描述符数组（每迭代一个）；批量大小可递减不可递增，向量长度须一致 |
| `sizeInBytes` | 输出 | 工作空间所需最小设备内存量（字节） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：描述符无效。
- `ACDNN_STATUS_NOT_SUPPORTED`：数据类型不支持。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.25. acdnnGetSeqDataDescriptor() {#4225-acdnngetseqdatadescriptor}

从先前创建的序列数据描述符检索设置。不需要的值可为除 `seqDataDesc` 之外的任何指针传 NULL。 `nbDimsRequested` 同时适用于 `dimA[]` 和 `axes[]`；对应数组为 NULL 时正值将被忽略。

```cpp
acdnnStatus_t acdnnGetSeqDataDescriptor(
    const acdnnSeqDataDescriptor_t seqDataDesc,
    acdnnDataType_t *dataType,
    int *nbDims,
    int nbDimsRequested,
    int dimA[],
    acdnnSeqDataAxis_t axes[],
    size_t *seqLengthArraySize,
    size_t seqLengthSizeRequested,
    int seqLengthArray[],
    void *paddingFill);
```

`acdnnGetSeqDataDescriptor()` 函数不报告序列数据缓冲区中的实际步幅，这些步幅在计算到任何序列数据元素的 Offset 时非常有用。开发者必须基于 `acdnnGetSeqDataDescriptor()` 函数报告的 `axes[]` 和 `dimA[]` 数组预先计算步幅。以下是执行此任务的示例代码：

```cpp
// 保存 Seq Data Stride 的Array
size_t strA[ACDNN_SEQDATA_DIM_COUNT] = {0};
// 从 Dim 和 Order Array计算 Stride
size_t stride = 1;
for (int i = nbDims - 1; i >= 0; i--) {
    int j = int(axes[i]);
    if (unsigned(j) < ACDNN_SEQDATA_DIM_COUNT - 1 && strA[j] == 0) {
        strA[j] = stride;
        stride *= dimA[j];
    } else {
        fprintf(stderr, "ERROR: invalid axes[%d]=%d\n\n", i, j);
        abort();
    }
}
```

`strA[]` 数组可用于计算到任何序列数据元素的索引，示例如下：

```cpp
// 使用四个索引（batch, beam, time, vect），范围已检查
size_t base = strA[ACDNN_SEQDATA_BATCH_DIM] * batch + strA[ACDNN_SEQDATA_BEAM_DIM] * beam + strA[ACDNN_SEQDATA_TIME_DIM] * time;
val = seqDataPtr[base + vect];
```

上述代码假设所有四个索引（batch、beam、time、vect）均小于 `dimA[]` 数组中的相应值。示例代码还省略了 `strA[ACDNN_SEQDATA_VECT_DIM]` 步幅，因为其值始终为 1，表示一个向量的元素占据连续的内存块。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `seqDataDesc` | 输入 | 序列数据描述符 |
| `dataType` | 输出 | 序列数据缓冲区的数据类型 |
| `nbDims` | 输出 | `dimA[]` / `axes[]` 中有效维度数量 |
| `nbDimsRequested` | 输入 | 写入 `dimA[]` / `axes[]` 的最大元素数（推荐 `ACDNN_SEQDATA_DIM_COUNT`） |
| `dimA[]` | 输出 | 序列数据维度数组 |
| `axes[]` | 输出 | 定义内存布局的 `acdnnSeqDataAxis_t` 数组 |
| `seqLengthArraySize` | 输出 | `seqLengthArray[]` 保存所有序列长度所需元素数 |
| `seqLengthSizeRequested` | 输入 | 写入 `seqLengthArray[]` 的最大元素数 |
| `seqLengthArray[]` | 输出 | 序列长度数组 |
| `paddingFill` | 输出 | 填充向量的填充值指针；不需要时为 NULL |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：无效输入参数。
- `ACDNN_STATUS_INTERNAL_ERROR`：内部状态不一致。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.26. acdnnMultiHeadAttnForward() {#4226-acdnnmultiheadattnforward}

```cpp
acdnnStatus_t acdnnMultiHeadAttnForward(
    acdnnHandle_t handle,
    const acdnnAttnDescriptor_t attnDesc,
    int currIdx,
    const int loWinIdx[], const int hiWinIdx[],
    const int devSeqLengthsQO[], const int devSeqLengthsKV[],
    const acdnnSeqDataDescriptor_t qDesc, const void *queries,
    const void *residuals,
    const acdnnSeqDataDescriptor_t kDesc, const void *keys,
    const acdnnSeqDataDescriptor_t vDesc, const void *values,
    const acdnnSeqDataDescriptor_t oDesc, void *out,
    size_t weightSizeInBytes, const void *weights,
    size_t workSpaceSizeInBytes, void *workspace,
    size_t reserveSpaceSizeInBytes, void *reserveSpace);
```

计算 Multi-head Attention 层的前向输出。**模式判定** 取决于最后两个参数： `reserveSpaceSizeInBytes = 0` 且 `reserveSpace = NULL` 视为 inference（不会再做 backward），否则视为 training。

在推理模式中， `currIdx` 用于指定要处理的嵌入向量的时间步或序列索引。在此模式下，开发者可以为时间步零（`currIdx = 0`）执行一次迭代，随后更新 Q、K、V 向量和注意力窗口，并执行下一步（`currIdx = 1`）。该迭代过程可对所有时间步重复执行。

当所有 Q 时间步都可用时（例如，在训练模式或 Self-attention 中 Encoder 侧的推理模式），开发者可以为 `currIdx` 赋负值，此时 `acdnnMultiHeadAttnForward()` API 将自动遍历所有 Q 时间步。

`loWinIdx[]` 和 `hiWinIdx[]` Host 数组用于为每个 Q 时间步指定注意力窗口大小。在典型的 Self-attention 场景下，开发者必须包含所有先前访问的嵌入向量，但不包括当前或未来的向量，此时，开发者应设置：

```cpp
currIdx=0: loWinIdx[0]=0; hiWinIdx[0]=0; // 初始 时间步，无 注意力窗口
currIdx=1: loWinIdx[1]=0; hiWinIdx[1]=1; // 注意力窗口 跨越一个 Vector
currIdx=2: loWinIdx[2]=0; hiWinIdx[2]=2; // 注意力窗口 跨越两个 Vector
...
```

当 `acdnnMultiHeadAttnForward()` 中的 `currIdx` 为负数时， `loWinIdx[]` 和 `hiWinIdx[]` 数组必须为所有时间步完全初始化。当使用 `currIdx = 0`、`currIdx = 1`、`currIdx = 2` 等调用 `acdnnMultiHeadAttnForward()` 时，开发者可以在调用前向响应函数之前仅更新 `loWinIdx[currIdx]` 和 `hiWinIdx[currIdx]` 元素，此时， `loWinIdx[]` 和 `hiWinIdx[]` 数组中的所有其他元素将不会被访问。通过这种方式可以实现任意 Adaptive 注意力窗口 Scheme。

当注意力窗口应设为最大时（例如，在 Cross-attention 中），请使用以下配置：

```cpp
currIdx=0: loWinIdx[0]=0; hiWinIdx[0]=maxSeqLenK;
currIdx=1: loWinIdx[1]=0; hiWinIdx[1]=maxSeqLenK;
currIdx=2: loWinIdx[2]=0; hiWinIdx[2]=maxSeqLenK;
...
```

上述 `maxSeqLenK` 值应等于或大于 `kDesc` 描述符中的 `dimA[ACDNN_SEQDATA_TIME_DIM]`。建议设为 `maxSeqLenK = INT_MAX`（定义于 `limits.h`）。

!!! note
    `acdnnSetSeqDataDescriptor()` 中 `seqLengthArray[]` 定义的任何 K 序列的实际长度可以短于 `maxSeqLenK`。Effective 注意力窗口 Span 基于 K 序列描述符中存储的 `seqLengthArray[]` 以及 `loWinIdx[]` 和 `hiWinIdx[]` 数组中保存的索引进行计算。

`devSeqLengthsQO[]` 和 `devSeqLengthsKV[]` 是指向 Device（而非 Host）数组的指针，该数组包含 Q、O 和 K、V 的序列长度。请注意，相同的信息也在 Host 侧通过 `acdnnSeqDataDescriptor_t` 类型的相应描述符传递。需要额外 Device 数组的原因在于 acDNN 调用的异步性质，以及专用于真武 PPU Kernel Argument 的 Constant 内存大小有限。当 `acdnnMultiHeadAttnForward()` API 返回时，可以立即修改描述符中存储的序列长度数组以用于下一次迭代。然而，此时前向调用启动的真武 PPU Kernel 可能尚未开始执行。因此，需要在 Device 侧保存序列数组的副本，以便真武 PPU Kernel 直接访问。对于非常大的 K、V 输入，若不在 `acdnnMultiHeadAttnForward()` 函数内部创建这些副本，则需要进行设备内存分配和 HGGC Stream 同步。

为了降低 `acdnnMultiHeadAttnForward()` API 的开销，该函数不验证 `devSeqLengthsQO[]` 和 `devSeqLengthsKV[]` Device 数组是否包含与序列数据描述符中 `seqLengthArray[]` 相同的设置。

`kDesc` 和 `vDesc` 描述符中的序列长度必须相同。类似地， `qDesc` 和 `oDesc` 描述符中的序列长度也应匹配。开发者可以在 `qDesc`、`kDesc`、`vDesc` 和 `oDesc` 描述符中定义六种不同的数据布局。有关这些布局的详细说明，请参阅 `acdnnSetSeqDataDescriptor()` 函数。所有 Multi-head Attention API 调用要求在所有序列数据描述符中使用一致的布局。

在 Transformer 模型中，多头注意力块通常与层归一化和残差连接紧密耦合。虽然 `acdnnMultiHeadAttnForward()` 不包含层归一化，但它可以用于处理残差连接，如下图所示。

**图：Multi-Head Attention Block 与层归一化和残差连接的紧密耦合**

在 `acdnnMultiHeadAttnForward()` 中，Queries 和 Residuals 共享相同的 `qDesc` 描述符。

![Multi-Head Attention 模块结构](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125140508/4ce588da686726f56bebd1967ab66148/mha_block.svg)

![MHA 中 QKV 投影与残差连接](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125140734/477664eb63ec1b02d730733275b629a1/mha_qkv_residual.svg)

当残差连接被禁用时， `residuals` 指针应为 NULL。当启用残差连接时， `qDesc` 中的向量长度应与 `oDesc` 描述符中指定的向量长度匹配，以确保向量加法操作可行。

即使当 K 和 V 为相同的输入，或者 Q、K、V 均为相同的输入时， `queries`、`keys` 和 `values` 指针也不允许为 NULL。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `attnDesc` | 输入 | 先前已初始化的 Attention 描述符 |
| `currIdx` | 输入 | 要处理的 Q 时间步；负数时处理所有 Q 时间步；非负时仅处理选定时间步（仅推理） |
| `loWinIdx[]` / `hiWinIdx[]` | 输入 | 主机整数数组，指定每个 Q 时间步的注意力窗口起始/结束索引（起始包含，结束排除） |
| `devSeqLengthsQO[]` | 输入 | 设备数组，Q/残差/输出的序列长度 |
| `devSeqLengthsKV[]` | 输入 | 设备数组，K/V 的序列长度 |
| `qDesc` | 输入 | Query / 残差序列数据描述符 |
| `queries` | 输入 | Queries 设备内存指针 |
| `residuals` | 输入 | 残差设备内存指针；不需要残差连接时为 NULL |
| `kDesc` | 输入 | Keys 序列数据描述符 |
| `keys` | 输入 | Keys 设备内存指针 |
| `vDesc` | 输入 | Values 序列数据描述符 |
| `values` | 输入 | Values 设备内存指针 |
| `oDesc` | 输入 | 输出序列数据描述符 |
| `out` | 输出 | 输出设备内存指针 |
| `weightSizeInBytes` | 输入 | 权重缓冲区大小（字节） |
| `weights` | 输入 | 权重缓冲区设备内存指针 |
| `workSpaceSizeInBytes` | 输入 | 工作空间缓冲区大小（字节） |
| `workspace` | 输入/输出 | 工作空间设备内存指针 |
| `reserveSpaceSizeInBytes` | 输入 | Reserve-space 缓冲区大小（字节）；推理=0, 训练>0 |
| `reserveSpace` | 输入/输出 | Reserve-space 设备内存指针；推理=NULL, 训练≠NULL |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：无效或不兼容的输入参数。
- `ACDNN_STATUS_EXECUTION_FAILED`：真武 PPU Kernel 启动失败。
- `ACDNN_STATUS_INTERNAL_ERROR`：内部状态不一致。
- `ACDNN_STATUS_NOT_SUPPORTED`：不支持的选项组合。
- `ACDNN_STATUS_ALLOC_FAILED`：Shared 内存不足。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.27. acdnnRNNForward() {#4227-acdnnrnnforward}

计算由 `rnnDesc` 描述的 RNN 的前向响应。输入来自 `x`/`hx`/`cx`，权重/偏置来自 `weightSpace`，输出写入 `y`/`hy`/`cy`。内部信号（时间步间和层间）不向开发者公开。

```cpp
acdnnStatus_t acdnnRNNForward(
    acdnnHandle_t handle,
    acdnnRNNDescriptor_t rnnDesc,
    acdnnForwardMode_t fwdMode,
    const int32_t *devSeqLengths,
    acdnnRNNDataDescriptor_t xDesc,
    const void *x,
    acdnnRNNDataDescriptor_t yDesc,
    void *y,
    acdnnTensorDescriptor_t hDesc,
    const void *hx,
    void *hy,
    acdnnTensorDescriptor_t cDesc,
    const void *cx,
    void *cy,
    size_t weightSpaceSize,
    const void *weightSpace,
    size_t workSpaceSize,
    void *workSpace,
    size_t reserveSpaceSize,
    void *reserveSpace);
```

**图：多层 RNN 模型中 x、y、hx、cx、hy 和 cy 信号的位置**

![多层 RNN 信号流向](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125141238/2e0ff135afd53813eeb8f4ef2b0bb6c9/rnn_multilayer_signals.svg)

当 RNN 模型为双向时，每个物理层由两个连续的伪层组成，每个伪层均拥有自己的权重、偏置、初始隐藏状态 `hx`，对于 LSTM 还有初始单元状态 `cx`。

偶数伪层 0、2、4 从左到右（前向，F）方向处理输入向量。奇数伪层 1、3、5 从右到左（反向，R）方向处理输入向量。两个连续的伪层对相同的输入向量进行操作，只是顺序不同。伪层 0 和 1 访问存储在 `x` 缓冲区中的原始序列。F 和 R 单元的输出被连接，因此馈送到下两个伪层的向量长度为 2x `hiddenSize` 或 2x `projSize`。后续伪层中的输入 GEMM 将向量长度调整为 1x `hiddenSize`。

当 `fwdMode` 参数设置为 `ACDNN_FWD_MODE_TRAINING` 时， `acdnnRNNForward()` 函数在预留空间缓冲区中存储计算一阶导数所需的中间数据。工作空间和预留空间缓冲区大小应由 `acdnnGetRNNTempSpaceSizes()` 函数计算，使用与 `acdnnRNNForward()` 调用中相同的 `fwdMode` 设置。

必须在 `xDesc` 和 `yDesc` 描述符中指定相同的布局 Type。必须在 `xDesc`、`yDesc` 和 Device 数组 `devSeqLengths` 中配置相同的序列长度。从 acDNN 8.9.1 开始，不再需要 `devSeqLengths` 参数，可以将其设置为 NULL。Variable 序列长度 Array 由 `acdnnRNNForward()` 函数自动传输到真武 PPU 内存。

`acdnnRNNForward()` 函数不验证真武 PPU 内存中存储在 `devSeqLengths` 中的序列长度是否与 CPU 内存中 `xDesc` 和 `yDesc` 描述符中的相同。但是，会检查来自 `xDesc` 和 `yDesc` 描述符的序列长度 Array 的一致性。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `rnnDesc` | 输入 | 先前已初始化的 RNN 描述符 |
| `fwdMode` | 输入 | `ACDNN_FWD_MODE_INFERENCE` 或 `ACDNN_FWD_MODE_TRAINING`；训练时中间数据存入预留空间 |
| `devSeqLengths` | 输入 | 设备内存中 `seqLengthArray` 副本（真武 PPU Kernel 异步访问） |
| `xDesc` | 输入 | RNN Primary 输入描述符； `vectorSize` 须匹配 `inputSize` |
| `x` | 输入 | 与 `xDesc` 关联的设备内存数据指针；须密集打包 |
| `yDesc` | 输入 | RNN 输出描述符； `vectorSize` 取决于投影 / 双向设置（Uni=`hiddenSize`，Bi=2x，Proj=`projSize`） |
| `y` | 输出 | 与 `yDesc` 关联的设备内存数据指针 |
| `hDesc` | 输入 | 隐藏状态张量描述符（全打包）。dim[0]=`numLayers`(Uni) 或 2x`numLayers`(Bi)，dim[1]=`batchSize`，dim[2]=`hiddenSize` 或 `projSize`(LSTM+Proj) |
| `hx` | 输入 | 初始隐藏状态设备指针；NULL 则初始化为零 |
| `hy` | 输出 | 最终隐藏状态设备指针；NULL 则不保存 |
| `cDesc` | 输入 | 仅 LSTM：单元 State 张量描述符。dim 规则同 `hDesc`，但 dim[2] 始终为 `hiddenSize` |
| `cx` | 输入 | 仅 LSTM：初始单元状态设备指针；NULL 则初始化为零 |
| `cy` | 输出 | 仅 LSTM：最终单元状态设备指针；NULL 则不保存 |
| `weightSpaceSize` | 输入 | 权重空间缓冲区大小（字节） |
| `weightSpace` | 输入 | 权重空间缓冲区设备地址 |
| `workSpaceSize` | 输入 | 工作空间缓冲区大小（字节） |
| `workSpace` | 输入/输出 | 工作空间缓冲区设备地址 |
| `reserveSpaceSize` | 输入 | Reserve-space 缓冲区大小（字节） |
| `reserveSpace` | 输入/输出 | Reserve-space 缓冲区设备地址 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：不支持的 Algorithm/配置。
- `ACDNN_STATUS_BAD_PARAM`：描述符为 NULL 或参数不兼容。
- `ACDNN_STATUS_EXECUTION_FAILED`：真武 PPU Kernel 启动失败。
- `ACDNN_STATUS_ALLOC_FAILED`：无法分配内存。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.28. acdnnRNNForwardInference() {#4228-acdnnrnnforwardinference}

!!! note
    请使用 `acdnnRNNForward()` 替代 `acdnnRNNForwardInference()`。

```cpp
acdnnStatus_t acdnnRNNForwardInference(
    acdnnHandle_t handle,
    const acdnnRNNDescriptor_t rnnDesc,
    const int seqLength,
    const acdnnTensorDescriptor_t *xDesc,
    const void *x,
    const acdnnTensorDescriptor_t hxDesc,
    const void *hx,
    const acdnnTensorDescriptor_t cxDesc,
    const void *cx,
    const acdnnFilterDescriptor_t wDesc,
    const void *w,
    const acdnnTensorDescriptor_t *yDesc,
    void *y,
    const acdnnTensorDescriptor_t hyDesc,
    void *hy,
    const acdnnTensorDescriptor_t cyDesc,
    void *cy,
    void *workspace,
    size_t workspaceSizeInBytes);
```

执行 RNN 推理（不保存训练所需的中间数据；如需训练应使用 `acdnnRNNForwardTraining()`）。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `rnnDesc` | 输入 | 先前已初始化的 RNN 描述符 |
| `seqLength` | 输入 | Unroll 迭代数量；不得超过 `acdnnGetRNNWorkspaceSize()` 中使用的值 |
| `xDesc` | 输入 | `seqLength` 个全打包张量描述符数组（3D：Batch x input 大小 x 1）；批量大小可递减不可递增。步幅： `{`inputSize`， 1, 1}` |
| `x` | 输入 | 输入设备内存指针；所有时间步向量须连续 Packed |
| `hxDesc` | 输入 | 初始隐藏状态的全打包张量描述符。dim[0]=`numLayers`(Uni)/2x(Bi)， dim[1]=Batch, dim[2]=`hiddenSize` |
| `hx` | 输入 | 初始隐藏状态设备指针；NULL 则初始化为零 |
| `cxDesc` | 输入 | 仅 LSTM：初始单元状态张量描述符（dim 规则同 `hxDesc`） |
| `cx` | 输入 | 仅 LSTM：初始单元状态设备指针；NULL 则初始化为零 |
| `wDesc` | 输入 | 描述 RNN 权重的滤波器描述符 |
| `w` | 输入 | `wDesc` 关联的设备内存数据指针 |
| `yDesc` | 输入 | 输出张量描述符数组；dim[1]=`hiddenSize`(Uni)/2x(Bi) |
| `y` | 输出 | 输出设备内存指针；连续 Packed |
| `hyDesc` | 输入 | 最终隐藏状态张量描述符（dim 规则同 `hxDesc`） |
| `hy` | 输出 | 最终隐藏状态设备指针；NULL 则不保存 |
| `cyDesc` | 输入 | 仅 LSTM：最终单元状态张量描述符（dim 规则同 `hxDesc`） |
| `cy` | 输出 | 仅 LSTM：最终单元状态设备指针；NULL 则不保存 |
| `workspace` | 输入 | 工作空间设备内存指针 |
| `workspaceSizeInBytes` | 输入 | 工作空间大小（字节） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：不支持的配置。
- `ACDNN_STATUS_BAD_PARAM`：描述符无效。
- `ACDNN_STATUS_EXECUTION_FAILED`：真武 PPU 启动失败。
- `ACDNN_STATUS_ALLOC_FAILED`：无法分配内存。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.29. acdnnRNNGetClip() {#4229-acdnnrnngetclip}

!!! note
    请使用 `acdnnRNNGetClip_v8()` 替代 `acdnnRNNGetClip()`。

```cpp
acdnnStatus_t acdnnRNNGetClip(
    acdnnHandle_t handle,
    acdnnRNNDescriptor_t rnnDesc,
    acdnnRNNClipMode_t *clipMode,
    acdnnNanPropagation_t *clipNanOpt,
    double *lclip,
    double *rclip);
```

检索当前 LSTM 单元裁剪参数。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 库上下文句柄。 |
| `rnnDesc` | 输入 | 先前已初始化的 RNN 描述符。 |
| `clipMode` | 输出 | `ACDNN_RNN_CLIP_NONE`（不裁剪）或 `ACDNN_RNN_CLIP_MINMAX`（启用裁剪） |
| `lclip` / `rclip` | 输出 | LSTM 单元裁剪 Range `[lclip, rclip]` |
| `clipNanOpt` | 输出 | NaN 传播设置 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：任何指针为 NULL。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.30. acdnnRNNGetClip_v8() {#4230-acdnnrnngetclip_v8}

检索当前 LSTM 单元裁剪参数。不需要的值可为除 `rnnDesc` 之外的任何指针传 NULL。

```cpp
acdnnStatus_t acdnnRNNGetClip_v8(
    acdnnRNNDescriptor_t rnnDesc,
    acdnnRNNClipMode_t *clipMode,
    acdnnNanPropagation_t *clipNanOpt,
    double *lclip,
    double *rclip);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `rnnDesc` | 输入 | 先前已初始化的 RNN 描述符 |
| `clipMode` | 输出 | `ACDNN_RNN_CLIP_NONE` 或 `ACDNN_RNN_CLIP_MINMAX` |
| `clipNanOpt` | 输出 | `acdnnNanPropagation_t` 值 |
| `lclip` / `rclip` | 输出 | LSTM 单元裁剪 Range `[lclip, rclip]` |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`rnnDesc` 为 NULL。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.31. acdnnRNNSetClip() {#4231-acdnnrnnsetclip}

!!! note
    请使用 `acdnnRNNSetClip_v8()` 替代 `acdnnRNNSetClip()`。

```cpp
acdnnStatus_t acdnnRNNSetClip(
    acdnnHandle_t handle,
    acdnnRNNDescriptor_t rnnDesc,
    acdnnRNNClipMode_t clipMode,
    acdnnNanPropagation_t clipNanOpt,
    double lclip,
    double rclip);
```

设置 LSTM 单元裁剪模式。默认禁用；启用时裁剪应用于所有层。可多次调用。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 库上下文句柄。 |
| `rnnDesc` | 输入 | 先前已初始化的 RNN 描述符。 |
| `clipMode` | 输入 | `ACDNN_RNN_CLIP_NONE`（禁用）或 `ACDNN_RNN_CLIP_MINMAX`（启用裁剪） |
| `lclip` / `rclip` | 输入 | 裁剪 Range `[lclip, rclip]` |
| `clipNanOpt` | 输入 | `ACDNN_PROPAGATE_NAN` 时 NaN 传播；否则可设为边界值（`acdnnNanPropagation_t`） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`lclip > rclip` 或值为 NaN。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.32. acdnnRNNSetClip_v8() {#4232-acdnnrnnsetclip_v8}

设置 LSTM 单元裁剪模式。默认禁用；启用时裁剪应用于所有层。不影响缓冲区大小，可多次调用。

```cpp
acdnnStatus_t acdnnRNNSetClip_v8(
    acdnnRNNDescriptor_t rnnDesc,
    acdnnRNNClipMode_t clipMode,
    acdnnNanPropagation_t clipNanOpt,
    double lclip,
    double rclip);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `rnnDesc` | 输入 | 先前已初始化的 RNN 描述符 |
| `clipMode` | 输入 | `ACDNN_RNN_CLIP_NONE`（禁用）或 `ACDNN_RNN_CLIP_MINMAX`（启用） |
| `clipNanOpt` | 输入 | NaN 传播模式（`acdnnNanPropagation_t`） |
| `lclip` / `rclip` | 输入 | 裁剪 Range `[lclip, rclip]` |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`rnnDesc` 为 NULL、`lclip > rclip` 或值为 NaN。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.33. acdnnSetAttnDescriptor() {#4233-acdnnsetattndescriptor}

配置先前用 `acdnnCreateAttnDescriptor()` 创建的 Multi-head Attention 描述符。设置的参数用于计算内部缓冲区大小、权重/偏置 Tensor 维度及选择优化代码路径。

```cpp
acdnnStatus_t acdnnSetAttnDescriptor(
    acdnnAttnDescriptor_t attnDesc,
    unsigned attnMode,
    int nHeads,
    double smScaler,
    acdnnDataType_t dataType,
    acdnnDataType_t computePrec,
    acdnnMathType_t mathType,
    acdnnDropoutDescriptor_t attnDropoutDesc,
    acdnnDropoutDescriptor_t postDropoutDesc,
    int qSize,
    int kSize,
    int vSize,
    int qProjSize,
    int kProjSize,
    int vProjSize,
    int oProjSize,
    int qoMaxSeqLength,
    int kvMaxSeqLength,
    int maxBatchSize,
    int maxBeamSize);
```

`acdnnMultiHeadAttnForward()` 中的输入序列数据描述符会根据 Attention 描述符中存储的配置参数进行检查。某些参数必须完全匹配，而 `maxBatchSize` 或 `qoMaxSeqLength` 等 max 参数则为相应的维度建立上限。

Multi-head Attention 模式可以用以下方程式描述：

$$
\mathbf{h}_{j} = \left(\mathbf{W}_{V,j} \mathbf{V}\right) \operatorname{softmax}\left(\operatorname{smScaler} \left(\mathbf{K}^{T} \mathbf{W}_{K,j}^{T}\right) \left(\mathbf{W}_{Q,j} \mathbf{q}\right)\right)， \text{for } j = 0 \dots nHeads - 1
$$

$$
\text{MultiHeadAttn}(\mathbf{q}, \mathbf{K}, \mathbf{V}, \mathbf{W}_{Q}, \mathbf{W}_{K}, \mathbf{W}_{V}, \mathbf{W}_{O}) = \sum_{j=0}^{\mathrm{nHeads}-1} \mathbf{W}_{O,j} \mathbf{h}_{j}
$$

其中：
- $nHeads$ 是评估向量的独立注意力头的数量。
- $\mathbf{q}$ 是 Primary 输入，单个 Query 列向量。
- $\mathbf{K}, \mathbf{V}$ 是 Key 和值列向量的两个矩阵。

为便于理解，上述方程式使用单个嵌入向量表示，但 acDNN API 可以处理 Beam Search Scheme 中的多个候选项，处理捆绑到 Batch 中的来自多个序列的向量，或自动迭代序列的所有嵌入向量（时间步）。因此，输入通常是带有额外信息的 Tensor，例如每个序列的有效 Length 或如何保存未使用的填充向量。

在某些出版物中，$\mathbf{W}_{O,j}$ 矩阵合并为一个输出投影矩阵，$\mathbf{h}_{j}$ 向量显式合并为单个向量，这是等效的表示法。在 acDNN Library 中，$\mathbf{W}_{O,j}$ 矩阵在概念上与 $\mathbf{W}_{Q,j}$、$\mathbf{W}_{K,j}$ 或 $\mathbf{W}_{V,j}$ 输入投影权重的处理方式相同。有关更多详细信息，请参阅 `acdnnGetMultiHeadAttnWeights()` 函数的描述。

权重矩阵 $\mathbf{W}_{Q,j}$、$\mathbf{W}_{K,j}$、$\mathbf{W}_{V,j}$ 和 $\mathbf{W}_{O,j}$ 发挥类似的作用，调整输入和 Multi-head Attention Final 输出中的向量长度。开发者可以通过将 $qProj$ 大小、$kProj$ 大小、$vProj$ 大小或 $oProj$ 大小参数设置为零来禁用任何或所有投影。

Query、Key 和值的嵌入向量大小以及投影后的向量长度必须选择为使上述矩阵乘法可行。否则， `acdnnSetAttnDescriptor()` 函数将返回 `ACDNN_STATUS_BAD_PARAM`。

当需要保持 $\mathbf{W}_{KQ,j} = \mathbf{W}_{K,j}^{T} \mathbf{W}_{Q,j}$ 或 $\mathbf{W}_{OV,j} = \mathbf{W}_{O,j} \mathbf{W}_{V,j}$ 矩阵中的秩亏缺时，会使用所有四个权重矩阵。这在每个 Head 内的线性变换期间消除一个或多个维度，作为一种特征提取形式。在这种情况下，Projected 大小小于原始向量长度。

对于每个注意力头，权重矩阵维度定义如下：
- $\mathbf{W}_{Q,j}$：索引 $j = 0 \dots \text{nHeads}-1$。
- $\mathbf{W}_{K,j}$：索引 $j = 0 \dots \text{nHeads}-1$（约束： `kProjSize == qProjSize`）
- $\mathbf{W}_{V,j}$：索引 $j = 0 \dots \text{nHeads}-1$。
- $\mathbf{W}_{O,j}$：大小由 `(oProjSize > 0) ? vProjSize : vSize` 确定，其中 $j = 0 \dots \text{nHeads}-1$。

当禁用输出投影（`oProjSize == 0`）时，输出向量长度默认为完整的拼接大小，意味着输出只是所有 $\mathbf{h}_{j}$ 向量的拼接。在此解释下，拼接矩阵 $\mathbf{W}_{O} = [\mathbf{W}_{O,0}, \mathbf{W}_{O,1}, \mathbf{W}_{O,2}, \dots]$ 有效地形成恒等映射。

Softmax 是一个归一化的指数向量 Function，接受并输出相同大小的向量。Multi-head Attention API 使用 `ACDNN_SOFTMAX_ACCURATE` Type 的 Softmax 来降低 Floating-point Overflow 的可能性。

`smScaler` 参数是 Softmax Sharpening/Smoothing Coefficient。当 `smScaler=1.0` 时，Softmax 使用自然指数函数 $\exp(x)$ 或 $2.7183^{x}$。当 `smScaler<1.0` 时，例如 `smScaler=0.2`，Softmax Block 使用的函数增长不会如此快，因为 $\exp(0.2 \times x) \approx 1.2214^{x}$。

可以调整 `smScaler` 参数来处理馈送到 Softmax 的更大范围的值。当范围太大（或对于给定范围 `smScaler` 不够小）时，Softmax Block 的输出向量变为 Categorical，意味着一个向量元素接近 1.0，其他输出为零或非常接近零。当这种情况发生时，Softmax Block 的 Jacobian Matrix 也接近零，因此 Delta 在训练期间不会从输出反向传播到输入，除非通过残差连接（如果启用了这些连接）。开发者可以将 `smScaler` 设置为任何正 Floating-point 值，甚至为零。 `smScaler` 参数不可训练。

`qoMaxSeqLength`、`kvMaxSeqLength`、`maxBatchSize` 和 `maxBeamSize` 参数分别在 `acdnnSeqDataDescriptor_t` 容器中声明最大序列长度、最大批量大小和最大束大小。馈送到前向和 Backward（Gradient）API 函数的实际维度不应超过 max 限制。应仔细设置 max 参数，因为太大的值会由于过大的工作空间和预留空间缓冲区而导致过多的内存使用。

`attnMode` 参数作为二进制掩码，其中设置了各种开关选项，这些选项可以影响内部缓冲区大小、强制执行某些参数检查、选择优化的代码执行路径，或启用不需要额外数值参数的注意力变体。此类选项的示例是在输入和输出投影中包含偏置。

`attnDropoutDesc` 和 `postDropoutDesc` 参数是定义训练模式中激活的两个 Dropout 层的描述符。由 `attnDropoutDesc` 定义的第一个 Dropout 操作直接应用于 Softmax 输出。由 `postDropoutDesc` 指定的第二个 Dropout 操作更改 Multi-head Attention 输出，就在添加残差连接之前。

!!! note
    `acdnnSetAttnDescriptor()` 函数对 `attnDropoutDesc` 和 `postDropoutDesc` 执行浅拷贝，意味着两个 Dropout 描述符的地址存储在 Attention 描述符中，而不是整个结构。因此，开发者应在 Attention 描述符的整个生命周期内保留 Dropout 描述符。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `attnDesc` | 输出 | 要配置的 Attention 描述符 |
| `attnMode` | 输入 | 按位 OR 的 Attention 选项标志（见下表） |
| `nHeads` | 输入 | 注意力头数量 |
| `smScaler` | 输入 | Softmax Coefficient（$\geq 0$；$\leq 1.0$ 为 Smoothing，$> 1.0$ 为 Sharpening） |
| `dataType` | 输入 | 输入 / 权重 / 输出的数据类型 |
| `computePrec` | 输入 | 计算精度 |
| `mathType` | 输入 | Tensor Cell 设置 |
| `attnDropoutDesc` | 输入 | 应用于 Softmax 输出的 Dropout 描述符 |
| `postDropoutDesc` | 输入 | 应用于 Attention 输出（残差之前）的 Dropout 描述符 |
| `qSize` / `kSize` / `vSize` | 输入 | Q、K、V 嵌入向量长度 |
| `qProjSize` / `kProjSize` / `vProjSize` | 输入 | 投影后的 Q、K、V 向量长度；零=禁用相应投影 |
| `oProjSize` | 输入 | 输出投影后向量长度；零=禁用 |
| `qoMaxSeqLength` | 输入 | Q/残差/输出序列数据的最大序列长度 |
| `kvMaxSeqLength` | 输入 | K/V 序列数据的最大序列长度 |
| `maxBatchSize` | 输入 | `acdnnSeqDataDescriptor_t` 的最大批量大小 |
| `maxBeamSize` | 输入 | `acdnnSeqDataDescriptor_t` 的最大束大小 |

**支持的 attn 模式标志**

| Enum 值 | 描述 |
| :--- | :--- |
| `ACDNN_ATTN_QUERYMAP_ALL_TO_ONE` | 当输入中的束大小大于 1 时，Query 和 Key 向量之间的映射的前向声明。来自同一 Beam Bundle 的多个向量映射到同一 Target 向量。这意味着映射集中的 Effective 束大小减少为 1。 |
| `ACDNN_ATTN_QUERYMAP_ONE_TO_ONE` | 当输入中的束大小大于 1 时，Query 和 Key 向量之间的映射的前向声明。来自同一 Beam Bundle 的多个向量映射到不同的 Target 向量。这要求输出集中的束大小与输入中的束大小匹配。 |
| `ACDNN_ATTN_DISABLE_PROJ_BIASES` | 禁用 Attention 输入投影和输出投影中的偏置 Term。 |
| `ACDNN_ATTN_ENABLE_PROJ_BIASES` | 在 Attention 输入和输出投影中使用额外的偏置。在这种情况下，Projected 向量计算为 $\overline{\mathbf{K}}_{j} = \mathbf{W}_{K,j} \mathbf{K} + \mathbf{b} \times [1, 1, \dots, 1]_{1 \times n}$，其中 $n$ 是矩阵中的列数。换言之，在权重矩阵乘法之后，相同的列向量被添加到所有列。 |

**支持的 dataType、computePrec 和 mathType 组合**

**表 `acdnnSetAttnDescriptor()` 支持的组合**

| dataType | computePrec | mathType |
| :--- | :--- | :--- |
| `ACDNN_DATA_DOUBLE` | `ACDNN_DATA_DOUBLE` | `ACDNN_DEFAULT_MATH` |
| `ACDNN_DATA_FLOAT` | `ACDNN_DATA_FLOAT` | `ACDNN_DEFAULT_MATH`， `ACDNN_TENSOR_OP_MATH_ALLOW_CONVERSION` |
| `ACDNN_DATA_HALF` | `ACDNN_DATA_HALF`， `ACDNN_DATA_FLOAT` | `ACDNN_DEFAULT_MATH`， `ACDNN_TENSOR_OP_MATH`， `ACDNN_TENSOR_OP_MATH_ALLOW_CONVERSION` |

**不支持的功能**

`acdnnSeqDataDescriptor_t` 中的 `paddingFill` 参数当前被所有 Multi-head Attention Function 忽略。

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：无效输入参数，如投影大小不一致等。
- `ACDNN_STATUS_NOT_SUPPORTED`：不支持的选项组合。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.34. acdnnSetRNNBiasMode() {#4234-acdnnsetrnnbiasmode}

!!! note
    请使用 `acdnnSetRNNDescriptor_v8()` 替代 `acdnnSetRNNBiasMode()`。

```cpp
acdnnStatus_t acdnnSetRNNBiasMode(
    acdnnRNNDescriptor_t rnnDesc,
    acdnnRNNBiasMode_t biasMode);
```

设置 RNN 描述符的偏置向量数量。默认值为 `ACDNN_RNN_DOUBLE_BIAS`。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `rnnDesc` | 输入/输出 | 先前创建的 RNN 描述符 |
| `biasMode` | 输入 | 偏置向量数量（`acdnnRNNBiasMode_t`） |

返回码：

- `ACDNN_STATUS_BAD_PARAM`：`rnnDesc` 为 NULL 或无效枚举。
- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：非默认偏置模式应用于非 STANDARD 算法。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.35. acdnnSetRNNDataDescriptor() {#4235-acdnnsetrnndatadescriptor}

初始化先前创建的 RNN 数据描述符 Object。支持 Unpacked（Padded）和 Packed（Unpadded）两种布局。

```cpp
acdnnStatus_t acdnnSetRNNDataDescriptor(
    acdnnRNNDataDescriptor_t RNNDataDesc,
    acdnnDataType_t dataType,
    acdnnRNNDataLayout_t layout,
    int maxSeqLength,
    int batchSize,
    int vectorSize,
    const int seqLengthArray[],
    void *paddingFill);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `RNNDataDesc` | 输入/输出 | 先前创建的 RNN 数据描述符（`acdnnRNNDataDescriptor_t`） |
| `dataType` | 输入 | 数据类型（`acdnnDataType_t`） |
| `layout` | 输入 | 内存布局 |
| `maxSeqLength` | 输入 | 最大序列长度（Unpacked 时含填充；Packed 时等于 `seqLengthArray` 最大值） |
| `batchSize` | 输入 | 小批量中序列数量 |
| `vectorSize` | 输入 | 每时间步的向量长度（嵌入大小） |
| `seqLengthArray` | 输入 | `batchSize` 元素的整数数组，各序列长度（0 ~ `maxSeqLength`）；Packed 布局时须降序 |
| `paddingFill` | 输入 | 主机内存中的填充值（仅 Unpacked 输出有效）；NULL 则填充未定义 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：不支持的 `dataType`。
- `ACDNN_STATUS_BAD_PARAM`：NULL 描述符或无效维度参数。
- `ACDNN_STATUS_ALLOC_FAILED`：内部存储分配失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.36. acdnnSetRNNDescriptor_v6() {#4236-acdnnsetrnndescriptor_v6}

!!! note
    请使用 `acdnnSetRNNDescriptor_v8()` 替代 `acdnnSetRNNDescriptor_v6()`。

```cpp
acdnnStatus_t acdnnSetRNNDescriptor_v6(
    acdnnHandle_t handle,
    acdnnRNNDescriptor_t rnnDesc,
    const int hiddenSize,
    const int numLayers,
    acdnnDropoutDescriptor_t dropoutDesc,
    acdnnRNNInputMode_t inputMode,
    acdnnDirectionMode_t direction,
    acdnnRNNMode_t mode,
    acdnnRNNAlgo_t algo,
    acdnnDataType_t mathPrec);
```

初始化先前创建的 RNN 描述符。较大网络（更长序列 / 更多层）通常效率更高。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `rnnDesc` | 输入/输出 | 先前创建的 RNN 描述符 |
| `hiddenSize` | 输入 | 每层隐藏状态大小 |
| `numLayers` | 输入 | 堆叠层数量 |
| `dropoutDesc` | 输入 | Dropout 描述符（应用于层间；单层不 Dropout） |
| `inputMode` | 输入 | 第一层输入行为 |
| `direction` | 输入 | 循环模式（Unidirectional / 双向） |
| `mode` | 输入 | RNN 单元类型 |
| `algo` | 输入 | RNN Algorithm。当前版本仅支持 `ACDNN_RNN_ALGO_STANDARD` |
| `mathPrec` | 输入 | 数学精度。当前版本仅支持 FP16 和 FP32 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`hiddenSize`/`numLayers` 为零或负数，或枚举无效。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.37. acdnnSetRNNDescriptor_v8() {#4237-acdnnsetrnndescriptor_v8}

初始化先前创建的 RNN 描述符。v8 版本可存储计算模式中 Adjustable 权重/偏置总数所需的全部信息。

```cpp
acdnnStatus_t acdnnSetRNNDescriptor_v8(
    acdnnRNNDescriptor_t rnnDesc,
    acdnnRNNAlgo_t algo,
    acdnnRNNMode_t cellMode,
    acdnnRNNBiasMode_t biasMode,
    acdnnDirectionMode_t dirMode,
    acdnnRNNInputMode_t inputMode,
    acdnnDataType_t dataType,
    acdnnDataType_t mathPrec,
    acdnnMathType_t mathType,
    int32_t inputSize,
    int32_t hiddenSize,
    int32_t projSize,
    int32_t numLayers,
    acdnnDropoutDescriptor_t dropoutDesc,
    uint32_t auxFlags);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `rnnDesc` | 输入 | 先前创建的 RNN 描述符 |
| `algo` | 输入 | RNN Algorithm。当前版本仅支持 `ACDNN_RNN_ALGO_STANDARD` |
| `cellMode` | 输入 | RNN 单元类型（RELU / TANH / LSTM / GRU） |
| `biasMode` | 输入 | 偏置数量。当前版本仅支持 `ACDNN_RNN_DOUBLE_BIAS` |
| `dirMode` | 输入 | `ACDNN_UNIDIRECTIONAL` 或 `ACDNN_BIDIRECTIONAL` |
| `inputMode` | 输入 | `ACDNN_LINEAR_INPUT`（乘权重矩阵）或 `ACDNN_SKIP_INPUT`（直接使用） |
| `dataType` | 输入 | 权重/偏置和输入/输出的数据类型 |
| `mathPrec` | 输入 | 计算精度。当前版本仅支持 FP16 和 FP32 |
| `mathType` | 输入 | Tensor 单元设置（建议性；FP16→DEFAULT/TENSOR_OP，FP32→DEFAULT/ALLOW_CONVERSION，FP64→DEFAULT） |
| `inputSize` | 输入 | 输入向量大小（`SKIP_INPUT` 时须等于 `hiddenSize`） |
| `hiddenSize` | 输入 | 隐藏状态向量大小（各层相同） |
| `projSize` | 输入 | LSTM 投影后输出大小（≤`hiddenSize`；等于时投影禁用；仅 LSTM+STANDARD） |
| `numLayers` | 输入 | Stacked 物理层数量 |
| `dropoutDesc` | 输入 | Dropout 描述符（层间应用；单层不 Dropout；仅训练） |
| `auxFlags` | 输入 | 按位 OR 的 Switch；当前用于 Padded I/O（`ACDNN_RNN_PADDED_IO_ENABLED` / `DISABLED`） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：无效输入参数。
- `ACDNN_STATUS_NOT_SUPPORTED`：不兼容的维度。
- `ACDNN_STATUS_EXECUTION_FAILED`：不兼容的参数组合。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.38. acdnnSetRNNMatrixMathType() {#4238-acdnnsetrnnmatrixmathtype}

!!! note
    请使用 `acdnnSetRNNDescriptor_v8()` 替代 `acdnnSetRNNMatrixMathType()`。

```cpp
acdnnStatus_t acdnnSetRNNMatrixMathType(
    acdnnRNNDescriptor_t rnnDesc,
    acdnnMathType_t mType);
```

设置 RNN GEMM 的 Tensor 单元选项。 `ACDNN_TENSOR_OP_MATH` 时在 HALF/FLOAT 权重上尝试使用 Tensor 单元（FLOAT 权重会先 Downconvert 为 HALF）。此选项为建议性。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `rnnDesc` | 输入 | 先前创建并初始化的 RNN 描述符 |
| `mType` | 输入 | RNN GEMM 首选 Compute 选项（建议性，Tensor 单元不一定被利用） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：无效输入参数。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.39. acdnnSetRNNProjectionLayers() {#4239-acdnnsetrnnprojectionlayers}

!!! note
    请使用 `acdnnSetRNNDescriptor_v8()` 替代 `acdnnSetRNNProjectionLayers()`。

```cpp
acdnnStatus_t acdnnSetRNNProjectionLayers(
    acdnnHandle_t handle,
    acdnnRNNDescriptor_t rnnDesc,
    const int recProjSize,
    const int outProjSize);
```

在 LSTM 网络中启用循环投影：将隐藏状态 $h_t$ 经矩阵 $W_r$（`recProjSize` x `hiddenSize`）投影为更小的 $r_t = W_r h_t$。仅适用于 LSTM 单元 + `ACDNN_RNN_ALGO_STANDARD`。 `recProjSize` 等于 `hiddenSize` 时投影禁用。输出投影当前未实现。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `rnnDesc` | 输入 | 先前创建并初始化的 RNN 描述符 |
| `recProjSize` | 输入 | 投影后 LSTM 输出大小（≤ `hiddenSize`） |
| `outProjSize` | 输入 | 当前须为零（未实现） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：NULL 句柄或负值参数。
- `ACDNN_STATUS_NOT_SUPPORTED`：非 LSTM 或非 STANDARD 算法。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.2.40. acdnnSetSeqDataDescriptor() {#4240-acdnnsetseqdatadescriptor}

初始化先前创建的序列数据描述符，定义四维 Tensor 的维度（`dimA`）和数据布局（`axes`）。

```cpp
acdnnStatus_t acdnnSetSeqDataDescriptor(
    acdnnSeqDataDescriptor_t seqDataDesc,
    acdnnDataType_t dataType,
    int nbDims,
    const int dimA[],
    const acdnnSeqDataAxis_t axes[],
    size_t seqLengthArraySize,
    const int seqLengthArray[],
    void *paddingFill);
```

序列数据描述符的所有四个维度都有唯一标识符，可用于索引 `dimA[]` 数组：
- `ACDNN_SEQDATA_TIME_DIM`
- `ACDNN_SEQDATA_BATCH_DIM`
- `ACDNN_SEQDATA_BEAM_DIM`
- `ACDNN_SEQDATA_VECT_DIM`

例如，要表达序列数据缓冲区中的向量长度为五个元素，需在 `dimA[]` 数组中赋值 `dimA[ACDNN_SEQDATA_VECT_DIM] = 5`。

`dimA[]` 和 `axes[]` 数组中有效维度的数量由 `nbDims` 参数定义。当前，此参数的值应为四。 `dimA[]` 和 `axes[]` 数组的实际大小应使用 `ACDNN_SEQDATA_DIM_COUNT` 宏声明。

`acdnnSeqDataDescriptor_t` 容器视为固定长度向量的集合，这些向量形成序列，类似于构建句子的单词（字符向量）。TIME 维度跨越序列长度。不同的序列捆绑在一起形成 Batch。Batch 可以是一组单独的序列或 Beam。Beam 是替代序列或候选项的集群。在考虑 Beam 时，请考虑从一种语言到另一种语言的翻译任务。可能需要保留并尝试原始句子的几个翻译版本，然后再选择最佳版本。保留的候选项数量就是束大小。

每个序列可以具有不同的长度，即使在同一 Beam 内也是如此，因此序列末端的向量可能只是填充。 `paddingFill` 参数指定如何在输出序列数据缓冲区中写入填充向量。 `paddingFill` 参数指向一个 `dataType` Type 的值，该值应复制到填充向量中的所有元素。当前， `paddingFill` 唯一支持的值是 NULL，这意味着应忽略此选项。在这种情况下，输出缓冲区中填充向量的元素将具有未定义的值。

假设非空序列始终从 Time 索引零开始。 `seqLengthArray[]` 必须指定容器中的所有序列长度，因此，该数组的总大小应为 `dimA[ACDNN_SEQDATA_BATCH_DIM] * dimA[ACDNN_SEQDATA_BEAM_DIM]`。 `seqLengthArray[]` 数组的每个元素应具有非负值，小于或等于 `dimA[ACDNN_SEQDATA_TIME_DIM]`（最大序列长度）。 `seqLengthArray[]` 中的元素始终按相同的 Batch-major Order 排列，意味着在考虑 BEAM 和 BATCH 维度时，BATCH 是外部或较慢变化的索引，按地址升序遍历数组时。使用一个简单的示例， `seqLengthArray[]` 数组应按以下顺序保存序列长度：
- `{batchIdx=0`,`beamIdx=0}`
- `{batchIdx=0`,`beamIdx=1}`
- `{batchIdx=1`,`beamIdx=0}`
- `{batchIdx=1`,`beamIdx=1}`
- `{batchIdx=2`,`beamIdx=0}`
- `{batchIdx=2`,`beamIdx=1}`

当 `dimA[ACDNN_SEQDATA_BATCH_DIM] = 3` 且 `dimA[ACDNN_SEQDATA_BEAM_DIM] = 2` 时。

存储在 `acdnnSeqDataDescriptor_t` 容器中的数据必须符合以下约束：
- 所有数据都是全打包的。各个向量元素或连续向量之间没有未使用的空间或间隙。
- 容器的最内层维度是向量。换言之，第一组连续的 `dimA[ACDNN_SEQDATA_VECT_DIM]` 个元素属于第一个向量，其次是第二个向量的元素，依此类推。

`acdnnSetSeqDataDescriptor()` 函数中的 `axes` 参数略为复杂，此数组应具有与 `dimA[]` 相同的容量。 `axes[]` 数组指定真武 PPU 内存中的实际数据布局。在此函数中，布局按以下方式描述：在内存中通过递增元素指针从向量的一个元素移动到另一个元素时，所遇到的 VECT、TIME、BATCH 和 BEAM 维度的顺序是什么。假设需定义如下数据布局，对应 Tensor 维度：

```cpp
int dimA[ACDNN_SEQDATA_DIM_COUNT];
dimA[ACDNN_SEQDATA_TIME_DIM] = 4;
dimA[ACDNN_SEQDATA_BATCH_DIM] = 3;
dimA[ACDNN_SEQDATA_BEAM_DIM] = 2;
dimA[ACDNN_SEQDATA_VECT_DIM] = 5;
```

初始化 `axes[]` 数组。请注意，最内层维度由 `axes[]` 的最后一个有效元素描述，此处仅有一个有效配置，由于始终首先遍历完整的向量，因此需在 `axes[]` 的最后一个有效元素中写入 `ACDNN_SEQDATA_VECT_DIM`。

```cpp
acdnnSeqDataAxis_t axes[ACDNN_SEQDATA_DIM_COUNT];
axes[3] = ACDNN_SEQDATA_VECT_DIM; // 3 = nbDims-1;
```

处理 `axes[]` 的其余三个元素。到达第一个向量的末尾时，跳转至下一个 Beam，因此：

```cpp
axes[2] = ACDNN_SEQDATA_BEAM_DIM;
```

到达第二个向量的末尾时，移动至下一个 Batch，因此：

```cpp
axes[1] = ACDNN_SEQDATA_BATCH_DIM;
```

最后一个（最外层）维度是 TIME：

```cpp
axes[0] = ACDNN_SEQDATA_TIME_DIM;
```

`axes[]` 数组的四个值完全描述了上述数据布局。

序列数据描述符允许开发者选择 $3! = 6$ 种不同的数据布局或 BEAM、BATCH 和 TIME 维度的排列。Multi-head Attention API 支持所有六种布局。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `seqDataDesc` | 输出 | 先前创建的序列数据描述符 |
| `dataType` | 输入 | 数据类型（HALF / FLOAT / DOUBLE） |
| `nbDims` | 输入 | 须为 4； `dimA[]` 和 `axes[]` 的有效维度数量 |
| `dimA[]` | 输入 | 序列数据维度数组；用 `acdnnSeqDataAxis_t` 枚举索引 |
| `axes[]` | 输入 | 定义内存布局的 `acdnnSeqDataAxis_t` 数组（`axes[0]`=最外层， `axes[nbDims-1]`=最内层） |
| `seqLengthArraySize` | 输入 | `seqLengthArray[]` 元素数量 |
| `seqLengthArray[]` | 输入 | 所有序列长度的整数数组 |
| `paddingFill` | 输入 | 当前须为 NULL（填充值；非 NULL 尚不支持） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：NULL 描述符或无效数据类型等。
- `ACDNN_STATUS_NOT_SUPPORTED`：`nbDims` ≠ 4 或 `paddingFill` 非 NULL。
- `ACDNN_STATUS_ALLOC_FAILED`：无法分配存储。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

### 4.3. 训练数据类型 {#43-训练数据类型}

#### 4.3.1. 枚举类型 {#431-枚举类型}

##### 4.3.1.1. acdnnLossNormalizationMode_t {#4311-acdnnlossnormalizationmode_t}

控制 CTC Loss 输入归一化模式的枚举，可与 `acdnnSetCTCLossDescriptorEx()` 配合使用。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_LOSS_NORMALIZATION_NONE` | `acdnnCTCLoss()` 函数的输入概率值预期为归一化概率，输出梯度是关于未归一化概率的损失梯度。 |
| `ACDNN_LOSS_NORMALIZATION_SOFTMAX` | `acdnnCTCLoss()` 函数的输入概率值预期为来自前一层的未归一化激活值，输出梯度是关于激活值的梯度。在内部，概率值通过 Softmax 归一化计算。 |

##### 4.3.1.2. acdnnWgradMode_t {#4312-acdnnwgradmode_t}

选择权重梯度累积模式的枚举，覆盖写入或累加至已有梯度。

| **值** | **描述** |
| :--- | :--- |
| `ACDNN_WGRAD_MODE_ADD` | 对应于新 Batch 输入的权重 Gradient Component 被添加到先前评估的权重 Gradient 中。在使用此模式之前，保存权重 Gradient 的缓冲区应初始化为零。或者，输出到未初始化缓冲区的第一个 API 调用应使用 `ACDNN_WGRAD_MODE_SET` 选项。 |
| `ACDNN_WGRAD_MODE_SET` | 对应于新 Batch 输入的权重 Gradient Component 覆盖输出缓冲区中先前存储的权重 Gradient。 |

### 4.4. 训练 API {#44-训练-api}

#### 4.4.1. acdnnAdvTrainVersionCheck() {#441-acdnnadvtrainversioncheck}

校验 AdvTrain 子库版本是否与其他 acDNN 子库一致。

```cpp
acdnnStatus_t acdnnAdvTrainVersionCheck(void);
```

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.4.2. acdnnCreateCTCLossDescriptor() {#442-acdnncreatectclossdescriptor}

创建 CTC Loss 描述符对象。

```cpp
acdnnStatus_t acdnnCreateCTCLossDescriptor(
    acdnnCTCLossDescriptor_t* ctcLossDesc);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `ctcLossDesc` | 输出 | 待创建的 CTC Loss 描述符（`acdnnCTCLossDescriptor_t`） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：描述符指针无效。
- `ACDNN_STATUS_ALLOC_FAILED`：内存分配失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.4.3. acdnnCTCLoss() {#443-acdnnctcloss}

根据概率和标签计算 CTC 代价及梯度。

```cpp
acdnnStatus_t acdnnCTCLoss(
    acdnnHandle_t handle,
    const acdnnTensorDescriptor_t probsDesc,
    const void *probs,
    const int hostLabels[],
    const int hostLabelLengths[],
    const int hostInputLengths[],
    void *costs,
    const acdnnTensorDescriptor_t gradientsDesc,
    void *gradients,
    acdnnCTCLossAlgo_t algo,
    acdnnCTCLossDescriptor_t ctcLossDesc,
    void *workspace,
    size_t workSpaceSizeInBytes);
```

!!! note
    根据 `acdnnLossNormalizationMode_t`（通过 `acdnnSetCTCLossDescriptorEx()` 绑定），输入/输出语义可能不一致。 `ACDNN_LOSS_NORMALIZATION_NONE` 时， `probs` 为 Softmax 归一化概率，但 `gradients` 输出关于未归一化激活； `ACDNN_LOSS_NORMALIZATION_SOFTMAX` 时接口一致。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文（`acdnnHandle_t`） |
| `probsDesc` | 输入 | 概率张量描述符（`acdnnTensorDescriptor_t`） |
| `probs` | 输入 | 经 Softmax 归一化的概率张量，设备内存 |
| `hostLabels` | 输入 | 标签列表，主机内存 |
| `hostLabelLengths` | 输入 | 各标签长度列表，主机内存 |
| `hostInputLengths` | 输入 | 各 Batch 时间步长度列表，主机内存 |
| `costs` | 输出 | 计算得到的 CTC 代价 |
| `gradientsDesc` | 输入 | 梯度张量描述符 |
| `gradients` | 输出 | CTC 梯度（关于未归一化激活） |
| `algo` | 输入 | CTC Loss 算法枚举（`acdnnCTCLossAlgo_t`） |
| `ctcLossDesc` | 输入 | CTC Loss 描述符（`acdnnCTCLossDescriptor_t`） |
| `workspace` | 输入 | 算法所需工作空间，设备内存 |
| `workSpaceSizeInBytes` | 输入 | 工作空间大小（字节） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`probsDesc` 与 `gradientsDesc` 维度不匹配等。
- `ACDNN_STATUS_NOT_SUPPORTED`：数据类型非 FLOAT 或未知算法。
- `ACDNN_STATUS_EXECUTION_FAILED`：真武 PPU kernel 启动失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.4.4. acdnnCTCLoss_v8() {#444-acdnnctcloss_v8}

v8 版 CTC Loss，标签与输入数据通过设备内存传递，支持 HGGC 计算图。需使用 `acdnnSetCTCLossDescriptor_v8()` 配置描述符。

```cpp
acdnnStatus_t acdnnCTCLoss_v8(
    acdnnHandle_t handle,
    acdnnCTCLossAlgo_t algo,
    const acdnnCTCLossDescriptor_t ctcLossDesc,
    const acdnnTensorDescriptor_t probsDesc,
    const void *probs,
    const int labels[],
    const int labelLengths[],
    const int inputLengths[],
    void *costs,
    const acdnnTensorDescriptor_t gradientsDesc,
    const void *gradients,
    size_t workSpaceSizeInBytes,
    void *workspace);
```

!!! note
    根据 `acdnnLossNormalizationMode_t`（通过 `acdnnSetCTCLossDescriptorEx()` 绑定），输入/输出语义可能不一致。 `ACDNN_LOSS_NORMALIZATION_NONE` 时， `probs` 为 Softmax 归一化概率，但 `gradients` 输出关于未归一化激活； `ACDNN_LOSS_NORMALIZATION_SOFTMAX` 时接口一致。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文（`acdnnHandle_t`） |
| `algo` | 输入 | CTC Loss 算法枚举（`acdnnCTCLossAlgo_t`） |
| `ctcLossDesc` | 输入 | CTC Loss 描述符，须通过 `acdnnSetCTCLossDescriptor_v8()` 设置（`acdnnCTCLossDescriptor_t`） |
| `probsDesc` | 输入 | 概率张量描述符（`acdnnTensorDescriptor_t`） |
| `probs` | 输入 | 经 Softmax 归一化的概率张量，设备内存 |
| `labels` | 输入 | 标签列表，设备内存 |
| `labelLengths` | 输入 | 各标签长度列表，设备内存 |
| `inputLengths` | 输入 | 各 Batch 时间步长度列表，设备内存 |
| `costs` | 输出 | 计算得到的 CTC 代价 |
| `gradientsDesc` | 输入 | 梯度张量描述符 |
| `gradients` | 输出 | CTC 梯度（关于未归一化激活） |
| `workSpaceSizeInBytes` | 输入 | 工作空间大小（字节） |
| `workspace` | 输入 | 算法所需工作空间，设备内存 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`probsDesc` 与 `gradientsDesc` 维度不匹配等。
- `ACDNN_STATUS_NOT_SUPPORTED`：数据类型非 FLOAT 或未知算法。
- `ACDNN_STATUS_EXECUTION_FAILED`：真武 PPU kernel 启动失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.4.5. acdnnDestroyCTCLossDescriptor() {#445-acdnndestroyctclossdescriptor}

销毁 CTC Loss 描述符对象。

```cpp
acdnnStatus_t acdnnDestroyCTCLossDescriptor(
    acdnnCTCLossDescriptor_t ctcLossDesc);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `ctcLossDesc` | 输入 | 待销毁的 CTC Loss 描述符 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.4.6. acdnnGetCTCLossDescriptor() {#446-acdnngetctclossdescriptor}

查询 CTC Loss 描述符的当前配置。

```cpp
acdnnStatus_t acdnnGetCTCLossDescriptor(
    acdnnCTCLossDescriptor_t ctcLossDesc,
    acdnnDataType_t* compType);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `ctcLossDesc` | 输入 | 待查询的 CTC Loss 描述符 |
| `compType` | 输出 | 关联的计算数据类型 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`ctcLossDesc` 无效。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.4.7. acdnnGetCTCLossDescriptorEx() {#447-acdnngetctclossdescriptorex}

查询 CTC Loss 描述符的扩展配置（含归一化模式和 NaN 传播类型）。

```cpp
acdnnStatus_t acdnnGetCTCLossDescriptorEx(
    acdnnCTCLossDescriptor_t ctcLossDesc,
    acdnnDataType_t *compType,
    acdnnLossNormalizationMode_t *normMode,
    acdnnNanPropagation_t *gradMode);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `ctcLossDesc` | 输入 | 待查询的 CTC Loss 描述符 |
| `compType` | 输出 | 计算数据类型 |
| `normMode` | 输出 | 输入归一化类型（`acdnnLossNormalizationMode_t`） |
| `gradMode` | 输出 | NaN 传播类型 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`ctcLossDesc` 无效。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.4.8. acdnnGetCTCLossDescriptor_v8() {#448-acdnngetctclossdescriptor_v8}

查询 v8 版 CTC Loss 描述符配置（含最大标签长度）。

```cpp
acdnnStatus_t acdnnGetCTCLossDescriptor_v8(
    acdnnCTCLossDescriptor_t ctcLossDesc,
    acdnnDataType_t *compType,
    acdnnLossNormalizationMode_t *normMode,
    acdnnNanPropagation_t *gradMode,
    int *maxLabelLength);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `ctcLossDesc` | 输入 | 待查询的 CTC Loss 描述符 |
| `compType` | 输出 | 计算数据类型 |
| `normMode` | 输出 | 输入归一化类型（`acdnnLossNormalizationMode_t`） |
| `gradMode` | 输出 | NaN 传播类型 |
| `maxLabelLength` | 输出 | 最大标签长度 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`ctcLossDesc` 无效。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.4.9. acdnnGetCTCLossWorkspaceSize() {#449-acdnngetctclossworkspacesize}

查询调用 `acdnnCTCLoss()` 所需的工作空间大小。

```cpp
acdnnStatus_t acdnnGetCTCLossWorkspaceSize(
    acdnnHandle_t handle,
    const acdnnTensorDescriptor_t probsDesc,
    const acdnnTensorDescriptor_t gradientsDesc,
    const int *labels,
    const int *labelLengths,
    const int *inputLengths,
    acdnnCTCLossAlgo_t algo,
    acdnnCTCLossDescriptor_t ctcLossDesc,
    size_t *sizeInBytes);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `probsDesc` | 输入 | 概率张量描述符 |
| `gradientsDesc` | 输入 | 梯度张量描述符 |
| `labels` | 输入 | 标签列表 |
| `labelLengths` | 输入 | 各标签长度列表 |
| `inputLengths` | 输入 | 各 Batch 时间步长度列表 |
| `algo` | 输入 | CTC Loss 算法枚举值 |
| `ctcLossDesc` | 输入 | CTC Loss 描述符 |
| `sizeInBytes` | 输出 | 所需工作空间大小（字节） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`probsDesc` 与 `gradientsDesc` 维度不匹配等。
- `ACDNN_STATUS_NOT_SUPPORTED`：数据类型非 FLOAT 或未知算法。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.4.10. acdnnGetCTCLossWorkspaceSize_v8() {#4410-acdnngetctclossworkspacesize_v8}

查询调用 `acdnnCTCLoss_v8()` 所需的工作空间大小。

```cpp
acdnnStatus_t acdnnGetCTCLossWorkspaceSize_v8(
    acdnnHandle_t handle,
    acdnnCTCLossAlgo_t algo,
    const acdnnCTCLossDescriptor_t ctcLossDesc,
    const acdnnTensorDescriptor_t probsDesc,
    const acdnnTensorDescriptor_t gradientsDesc,
    size_t *sizeInBytes);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `algo` | 输入 | CTC Loss 算法枚举值 |
| `ctcLossDesc` | 输入 | CTC Loss 描述符 |
| `probsDesc` | 输入 | 概率张量描述符 |
| `gradientsDesc` | 输入 | 梯度张量描述符 |
| `sizeInBytes` | 输出 | 所需工作空间大小（字节） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`probsDesc` 与 `gradientsDesc` 维度不匹配。
- `ACDNN_STATUS_NOT_SUPPORTED`：数据类型非 FLOAT 或未知算法。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.4.11. acdnnRNNBackwardData() {#4411-acdnnrnnbackwarddata}

!!! note
    请使用 `acdnnRNNBackwardData_v8()` 替代 `acdnnRNNBackwardData()`。

```cpp
acdnnStatus_t acdnnRNNBackwardData(
    acdnnHandle_t handle,
    const acdnnRNNDescriptor_t rnnDesc,
    const int seqLength,
    const acdnnTensorDescriptor_t *yDesc,
    const void *y,
    const acdnnTensorDescriptor_t *dyDesc,
    const void *dy,
    const acdnnTensorDescriptor_t dhyDesc,
    const void *dhy,
    const acdnnTensorDescriptor_t dcyDesc,
    const void *dcy,
    const acdnnFilterDescriptor_t wDesc,
    const void *w,
    const acdnnTensorDescriptor_t hxDesc,
    const void *hx,
    const acdnnTensorDescriptor_t cxDesc,
    const void *cx,
    const acdnnTensorDescriptor_t *dxDesc,
    void *dx,
    const acdnnTensorDescriptor_t dhxDesc,
    void *dhx,
    const acdnnTensorDescriptor_t dcxDesc,
    void *dcx,
    void *workspace,
    size_t workSpaceSizeInBytes,
    void *reserveSpace,
    size_t reserveSpaceSizeInBytes);
```

执行由 `rnnDesc` 描述的 RNN 反向数据传播，根据输出梯度 `dy`/`dhy`/`dcy` 和权重 `w` 计算输入梯度 `dx`/`dhx`/`dcx`。 `reserveSpace` 中的数据须由前序 `acdnnRNNForwardTraining()` 生成，且后续 `acdnnRNNBackwardWeights()` 调用须使用相同的 `reserveSpace`。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文（`acdnnHandle_t`） |
| `rnnDesc` | 输入 | RNN 描述符（`acdnnRNNDescriptor_t`） |
| `seqLength` | 输入 | 展开的迭代次数，不得超过 `acdnnGetRNNWorkspaceSize()` 中使用的值 |
| `yDesc` | 输入 | 输出张量描述符数组（每时间步一个）。第二维：单向=`hiddenSize`，双向=`2*hiddenSize` |
| `y` | 输入 | 输出数据，设备内存 |
| `dyDesc` | 输入 | 输出梯度张量描述符数组。维度要求同 `yDesc` |
| `dy` | 输入 | 输出梯度，设备内存 |
| `dhyDesc` | 输入 | 最终隐藏状态梯度张量描述符（全打包） |
| `dhy` | 输入 | 最终隐藏状态梯度，设备内存；NULL 则初始化为零 |
| `dcyDesc` | 输入 | 最终单元状态梯度张量描述符（仅 LSTM，全打包） |
| `dcy` | 输入 | 最终单元状态梯度，设备内存；NULL 则初始化为零 |
| `wDesc` | 输入 | 权重滤波器描述符（`acdnnFilterDescriptor_t`） |
| `w` | 输入 | 权重数据，设备内存 |
| `hxDesc` | 输入 | 初始隐藏状态张量描述符（全打包） |
| `hx` | 输入 | 初始隐藏状态，设备内存；NULL 则初始化为零 |
| `cxDesc` | 输入 | 初始单元状态张量描述符（仅 LSTM，全打包） |
| `cx` | 输入 | 初始单元状态，设备内存；NULL 则初始化为零 |
| `dxDesc` | 输入 | 输入梯度张量描述符数组。批量大小可递减 |
| `dx` | 输出 | 输入梯度，设备内存 |
| `dhxDesc` | 输入 | 初始隐藏状态梯度张量描述符（全打包） |
| `dhx` | 输出 | 初始隐藏状态梯度，设备内存；NULL 则不写入 |
| `dcxDesc` | 输入 | 初始单元状态梯度张量描述符（仅 LSTM，全打包） |
| `dcx` | 输出 | 初始单元状态梯度，设备内存；NULL 则不写入 |
| `workspace` | 输入 | 工作空间，设备内存 |
| `workSpaceSizeInBytes` | 输入 | 工作空间大小（字节） |
| `reserveSpace` | 输入/输出 | 预留空间，设备内存 |
| `reserveSpaceSizeInBytes` | 输入 | 预留空间大小（字节） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：不支持。
- `ACDNN_STATUS_BAD_PARAM`：参数无效。
- `ACDNN_STATUS_INVALID_VALUE`：参数无效。
- `ACDNN_STATUS_MAPPING_ERROR`：内存映射错误。
- `ACDNN_STATUS_EXECUTION_FAILED`：执行失败。
- `ACDNN_STATUS_ALLOC_FAILED`：内存分配失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.4.12. acdnnRNNBackwardData_v8() {#4412-acdnnrnnbackwarddata_v8}

计算 RNN 模型关于输入 `x`、`hx`（LSTM 含 `cx`）的精确一阶导数。设 $O = [y, hy, cy] = F(x, hx, cx) = F(z)$ 为整个 RNN 模型的向量函数，本函数计算 $(\partial O_i / \partial z_j)^T \delta_{out}$，其中 $\delta_{out}$ 通过 `dy`、`dhy`、`dcy` 提供，结果写入 `dx`、`dhx`、`dcx`。

```cpp
acdnnStatus_t acdnnRNNBackwardData_v8(
    acdnnHandle_t handle,
    acdnnRNNDescriptor_t rnnDesc,
    const int32_t devSeqLengths[],
    acdnnRNNDataDescriptor_t yDesc,
    const void *y,
    const void *dy,
    acdnnRNNDataDescriptor_t xDesc,
    void *dx,
    acdnnTensorDescriptor_t hDesc,
    const void *hx,
    const void *dhy,
    void *dhx,
    acdnnTensorDescriptor_t cDesc,
    const void *cx,
    const void *dcy,
    void *dcx,
    size_t weightSpaceSize,
    const void *weightSpace,
    size_t workSpaceSize,
    void *workspace,
    size_t reserveSpaceSize,
    void *reserveSpace);
```

**图：多层 RNN 模型中 x、y、hx、cx、hy、cy、dx、dy、dhx、dcx、dhy 和 dcy 信号的位置**

![RNN 反向传播信号](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125141020/85311e60c21b31a59ccec6844a7e8e9e/rnn_backward_signals.svg)

**使用要点**

- `y` 和 `hx`/`cx` 须指向前序 `acdnnRNNForward()` 调用中相同的数据。 `dy`、`dx` 不可为 NULL。
- `dhy`/`dcy` 为 NULL 时假设为零； `dhx`/`dcx` 为 NULL 时不写入对应结果。
- 当 `hx`、`dhy`、`dhx` 均为 NULL 时， `hDesc` 也可为 NULL（`cx`/`dcy`/`dcx` 与 `cDesc` 同理）。
- 支持 Padded 布局（`ACDNN_RNN_DATA_LAYOUT_SEQ_MAJOR_UNPACKED`、`ACDNN_RNN_DATA_LAYOUT_BATCH_MAJOR_UNPACKED`）及 Packed 布局（`ACDNN_RNN_DATA_LAYOUT_SEQ_MAJOR_PACKED`）。
- `xDesc` 和 `yDesc` 须使用相同布局 Type 和 `seqLengthArray`。从 acDNN 8.9.1 起 `devSeqLengths` 可设为 NULL。
- 须在 `acdnnRNNForward()`（`fwdMode=ACDNN_FWD_MODE_TRAINING`）之后调用。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `rnnDesc` | 输入 | RNN 描述符 |
| `devSeqLengths` | 输入 | 序列长度数组副本，设备内存（acDNN 8.9.1+ 可为 NULL） |
| `yDesc` | 输入 | RNN 输出数据描述符 |
| `y` | 输入 | RNN 主输出，设备内存（由前序 `acdnnRNNForward()` 生成） |
| `dy` | 输入 | 输出梯度，设备内存（不可为 NULL） |
| `xDesc` | 输入 | 输入梯度的 RNN 数据描述符（`dataType`/`layout`/`batchSize` 等须与 `yDesc` 匹配） |
| `dx` | 输出 | 输入梯度，设备内存（不可为 NULL） |
| `hDesc` | 输入 | 初始隐藏状态张量描述符（第一维：单向=`numLayers`，双向=`2*numLayers`；第二维=`batchSize`；第三维=`hiddenSize` 或 `projSize`） |
| `hx` / `dhy` | 输入 | 初始隐藏状态 / 最终隐藏状态梯度，设备内存；NULL 视为零 |
| `dhx` | 输出 | 初始隐藏状态梯度，设备内存；NULL 则不写入 |
| `cDesc` | 输入 | 初始单元状态张量描述符（仅 LSTM） |
| `cx` / `dcy` | 输入 | 初始单元状态 / 最终单元状态梯度，设备内存；NULL 视为零 |
| `dcx` | 输出 | 初始单元状态梯度，设备内存；NULL 则不写入 |
| `weightSpaceSize` | 输入 | 权重空间大小（字节） |
| `weightSpace` | 输入 | 权重空间，设备内存 |
| `workSpaceSize` | 输入 | 工作空间大小（字节） |
| `workspace` | 输入/输出 | 工作空间，设备内存 |
| `reserveSpaceSize` | 输入 | 预留空间大小（字节） |
| `reserveSpace` | 输入/输出 | 预留空间，设备内存 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：不支持。
- `ACDNN_STATUS_BAD_PARAM`：参数无效。
- `ACDNN_STATUS_MAPPING_ERROR`：内存映射错误。
- `ACDNN_STATUS_EXECUTION_FAILED`：执行失败。
- `ACDNN_STATUS_ALLOC_FAILED`：内存分配失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.4.13. acdnnRNNBackwardWeights() {#4413-acdnnrnnbackwardweights}

!!! note
    请使用 `acdnnRNNBackwardWeights_v8()` 替代 `acdnnRNNBackwardWeights()`。

```cpp
acdnnStatus_t acdnnRNNBackwardWeights(
    acdnnHandle_t handle,
    const acdnnRNNDescriptor_t rnnDesc,
    const int seqLength,
    const acdnnTensorDescriptor_t *xDesc,
    const void *x,
    const acdnnTensorDescriptor_t hxDesc,
    const void *hx,
    const acdnnTensorDescriptor_t *yDesc,
    const void *y,
    const void *workspace,
    size_t workSpaceSizeInBytes,
    const acdnnFilterDescriptor_t dwDesc,
    void *dw,
    const void *reserveSpace,
    size_t reserveSpaceSizeInBytes);
```

累加 RNN 权重梯度 `dw`，以 Additive 模式将本次计算的梯度加到 `dw` 已有值上。 `reserveSpace` 须由前序 `acdnnRNNForwardTraining()` 生成。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `rnnDesc` | 输入 | RNN 描述符 |
| `seqLength` | 输入 | 序列长度 |
| `xDesc` | 输入 | 输入数据的张量描述符数组，长度为 `seqLength` |
| `x` | 输入 | 指向输入数据的 Device 内存指针 |
| `hxDesc` | 输入 | 初始隐藏状态的张量描述符 |
| `hx` | 输入 | 指向初始隐藏状态的 Device 内存指针，可为 NULL |
| `yDesc` | 输入 | 输出数据的张量描述符数组，长度为 `seqLength` |
| `y` | 输入 | 指向输出数据的 Device 内存指针 |
| `workspace` | 输入 | 指向工作空间的 Device 内存指针 |
| `workSpaceSizeInBytes` | 输入 | 工作空间大小（字节） |
| `dwDesc` | 输入 | 权重梯度的滤波器描述符 |
| `dw` | 输入/输出 | 指向权重梯度的 Device 内存指针（累加模式） |
| `reserveSpace` | 输入 | 由 `acdnnRNNForwardTraining()` 生成的 Reserved Space |
| `reserveSpaceSizeInBytes` | 输入 | Reserved Space 大小（字节） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：不支持。
- `ACDNN_STATUS_BAD_PARAM`：参数无效。
- `ACDNN_STATUS_EXECUTION_FAILED`：执行失败。
- `ACDNN_STATUS_ALLOC_FAILED`：内存分配失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.4.14. acdnnRNNBackwardWeights_v8() {#4414-acdnnrnnbackwardweights_v8}

计算 RNN 模型相对于所有可训练参数（权重和偏置）的精确一阶导数。设 $O = [y, hy, cy] = F(w)$，本函数计算 $(\partial O_i / \partial w_j)^T \delta_{out}$，结果写入 `dweightSpace`（布局同 `weightSpace`）。

```cpp
acdnnStatus_t acdnnRNNBackwardWeights_v8(
    acdnnHandle_t handle,
    acdnnRNNDescriptor_t rnnDesc,
    acdnnWgradMode_t addGrad,
    const int32_t devSeqLengths[],
    acdnnRNNDataDescriptor_t xDesc,
    const void *x,
    acdnnTensorDescriptor_t hDesc,
    const void *hx,
    acdnnRNNDataDescriptor_t yDesc,
    const void *y,
    size_t weightSpaceSize,
    void *dweightSpace,
    size_t workSpaceSize,
    void *workspace,
    size_t reserveSpaceSize,
    void *reserveSpace);
```

**使用要点**

- 目前仅支持 `ACDNN_WGRAD_MODE_ADD`，首次调用前须将 `dweightSpace` 清零。
- `xDesc` 和 `devSeqLengths` 须指定相同的序列长度。从 acDNN 8.9.1 起 `devSeqLengths` 可设为 NULL。
- 须在 `acdnnRNNBackwardData()` 之后调用。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `rnnDesc` | 输入 | RNN 描述符 |
| `addGrad` | 输入 | 梯度输出模式（`acdnnWgradMode_t`），目前仅支持 `ACDNN_WGRAD_MODE_ADD` |
| `devSeqLengths` | 输入 | 序列长度数组，设备内存（acDNN 8.9.1+ 可为 NULL） |
| `xDesc` | 输入 | 输入 RNN 数据描述符（同前序 `acdnnRNNForward()` / `acdnnRNNBackwardData_v8()`） |
| `x` | 输入 | RNN 主输入，设备内存 |
| `hDesc` | 输入 | 初始隐藏状态张量描述符 |
| `hx` | 输入 | 初始隐藏状态，设备内存 |
| `yDesc` | 输入 | 输出 RNN 数据描述符 |
| `y` | 输出 | 前序 `acdnnRNNForward()` 生成的主输出，设备内存 |
| `weightSpaceSize` | 输入 | 权重空间大小（字节） |
| `dweightSpace` | 输出 | 权重梯度空间，设备内存 |
| `workSpaceSize` | 输入 | 工作空间大小（字节） |
| `workspace` | 输入/输出 | 工作空间，设备内存 |
| `reserveSpaceSize` | 输入 | 预留空间大小（字节） |
| `reserveSpace` | 输入/输出 | 预留空间，设备内存 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：不支持。
- `ACDNN_STATUS_BAD_PARAM`：参数无效。
- `ACDNN_STATUS_EXECUTION_FAILED`：执行失败。
- `ACDNN_STATUS_ALLOC_FAILED`：内存分配失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.4.15. acdnnRNNForwardTraining() {#4415-acdnnrnnforwardtraining}

!!! note
    请使用 `acdnnRNNForward()` 代替 `acdnnRNNForwardTraining()`。

```cpp
acdnnStatus_t acdnnRNNForwardTraining(
    acdnnHandle_t handle,
    const acdnnRNNDescriptor_t rnnDesc,
    const int seqLength,
    const acdnnTensorDescriptor_t *xDesc,
    const void *x,
    const acdnnTensorDescriptor_t hxDesc,
    const void *hx,
    const acdnnTensorDescriptor_t cxDesc,
    const void *cx,
    const acdnnFilterDescriptor_t wDesc,
    const void *w,
    const acdnnTensorDescriptor_t *yDesc,
    void *y,
    const acdnnTensorDescriptor_t hyDesc,
    void *hy,
    const acdnnTensorDescriptor_t cyDesc,
    void *cy,
    void *workspace,
    size_t workSpaceSizeInBytes,
    void *reserveSpace,
    size_t reserveSpaceSizeInBytes);
```

执行由 `rnnDesc` 描述的 RNN 前向训练。 `reserveSpace` 存储反向传播所需的中间数据，后续 `acdnnRNNBackwardData()` 和 `acdnnRNNBackwardWeights()` 须使用相同的 `reserveSpace`。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 上下文 |
| `rnnDesc` | 输入 | RNN 描述符 |
| `seqLength` | 输入 | 展开的迭代次数 |
| `xDesc` | 输入 | 输入张量描述符数组（每时间步一个，3D，批量大小可递减）。步幅： `[`inputSize`， 1, 1]` |
| `x` | 输入 | 输入数据（各时间步连续打包），设备内存 |
| `hxDesc` | 输入 | 初始隐藏状态张量描述符（全打包） |
| `hx` | 输入 | 初始隐藏状态，设备内存；NULL 则初始化为零 |
| `cxDesc` | 输入 | 初始单元状态张量描述符（仅 LSTM，全打包） |
| `cx` | 输入 | 初始单元状态，设备内存；NULL 则初始化为零 |
| `wDesc` | 输入 | 权重滤波器描述符 |
| `w` | 输入 | 权重数据，设备内存 |
| `yDesc` | 输入 | 输出张量描述符数组。第二维：单向=`hiddenSize`，双向=`2*hiddenSize` |
| `y` | 输出 | 输出数据，设备内存 |
| `hyDesc` | 输入 | 最终隐藏状态张量描述符（全打包） |
| `hy` | 输出 | 最终隐藏状态，设备内存；NULL 则不保存 |
| `cyDesc` | 输入 | 最终单元状态张量描述符（仅 LSTM，全打包） |
| `cy` | 输出 | 最终单元状态，设备内存；NULL 则不保存 |
| `workspace` | 输入 | 工作空间，设备内存 |
| `workSpaceSizeInBytes` | 输入 | 工作空间大小（字节） |
| `reserveSpace` | 输入/输出 | 预留空间，设备内存 |
| `reserveSpaceSizeInBytes` | 输入 | 预留空间大小（字节） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：参数无效。
- `ACDNN_STATUS_INVALID_VALUE`：参数无效。
- `ACDNN_STATUS_EXECUTION_FAILED`：执行失败。
- `ACDNN_STATUS_ALLOC_FAILED`：内存分配失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.4.16. acdnnSetCTCLossDescriptor() {#4416-acdnnsetctclossdescriptor}

设置 CTC Loss 描述符的基本配置。等效于 `acdnnSetCTCLossDescriptorEx(*, ACDNN_LOSS_NORMALIZATION_NONE, ACDNN_NOT_PROPAGATE_NAN)`。

```cpp
acdnnStatus_t acdnnSetCTCLossDescriptor(
    acdnnCTCLossDescriptor_t ctcLossDesc,
    acdnnDataType_t compType);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `ctcLossDesc` | 输出 | 待设置的 CTC Loss 描述符 |
| `compType` | 输入 | 计算数据类型 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：参数无效。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.4.17. acdnnSetCTCLossDescriptorEx() {#4417-acdnnsetctclossdescriptorex}

设置 CTC Loss 描述符的扩展配置，额外指定输入归一化模式和 NaN 传播类型。

```cpp
acdnnStatus_t acdnnSetCTCLossDescriptorEx(
    acdnnCTCLossDescriptor_t ctcLossDesc,
    acdnnDataType_t compType,
    acdnnLossNormalizationMode_t normMode,
    acdnnNanPropagation_t gradMode);
```

当 `normMode=ACDNN_LOSS_NORMALIZATION_NONE` 且 `gradMode=ACDNN_NOT_PROPAGATE_NAN` 时等同于 `acdnnSetCTCLossDescriptor()`。

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `ctcLossDesc` | 输出 | 待设置的 CTC Loss 描述符 |
| `compType` | 输入 | 计算数据类型 |
| `normMode` | 输入 | 输入归一化类型（`acdnnLossNormalizationMode_t`） |
| `gradMode` | 输入 | NaN 传播类型。 `ACDNN_PROPAGATE_NAN` 时对满足 $L + R > T$ 的样本保留梯度缓冲区当前值； `ACDNN_NOT_PROPAGATE_NAN` 时将其置零以保证梯度有限（`acdnnNanPropagation_t`） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：参数无效。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。


#### 4.4.18. acdnnSetCTCLossDescriptor_v8() {#4418-acdnnsetctclossdescriptor_v8}

v8 版 CTC Loss 描述符设置，新增 `maxLabelLength` 参数，因标签数据存于设备内存无法自动获取其长度信息。

```cpp
acdnnStatus_t acdnnSetCTCLossDescriptor_v8(
    acdnnCTCLossDescriptor_t ctcLossDesc,
    acdnnDataType_t compType,
    acdnnLossNormalizationMode_t normMode,
    acdnnNanPropagation_t gradMode,
    int maxLabelLength);
```

**参数**

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `ctcLossDesc` | 输出 | 待设置的 CTC Loss 描述符 |
| `compType` | 输入 | 计算数据类型 |
| `normMode` | 输入 | 输入归一化类型（`acdnnLossNormalizationMode_t`） |
| `gradMode` | 输入 | NaN 传播类型。 `ACDNN_PROPAGATE_NAN` 时对满足 $L + R > T$ 的样本保留梯度缓冲区当前值； `ACDNN_NOT_PROPAGATE_NAN` 时将其置零（`acdnnNanPropagation_t`） |
| `maxLabelLength` | 输入 | 标签数据中的最大标签长度 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：参数无效。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

**比赛关联：** `acdnnMultiHeadAttnForward()` 是本章对比赛最关键的 API：它原生支持增量解码（`currIdx` 逐时间步调用）、`loWinIdx`/`hiWinIdx` 因果注意力窗口、KV 序列长度设备侧数组（避免每步 host-device 同步）以及 beam search（BEAM 维），逐条对应自回归解码的 TTFT 与吞吐优化点；`smScaler` 即 softmax 缩放系数。`acdnnSetAttnDescriptor()` 的 HALF+TENSOR_OP_MATH 组合表也是半精度 attention 可行性的直接依据。

## 5. Graph API {#5-graph-api}

acDNN 的 Graph API（即后端描述符体系）提供了一套统一的接口来描述算子实现。与前几章的“句柄 + 描述符 + 直接调用”模型不同，Graph API 采用先描述、再执行的声明式范式：开发者组装一张算子图（graph），由运行时选择最优实现并执行。

### 5.1. 数据类型 {#51-数据类型}

这些是 acDNN Backend API 的数据类型引用。

#### 5.1.1. 枚举类型 {#511-枚举类型}

这些是 acDNN Backend API 的枚举类型。

##### 5.1.1.1. acdnnBackendAttributeName_t {#5111-acdnnbackendattributename_t}

`acdnnBackendAttributeName_t` 是一个枚举类型，表示可以使用 `acdnnBackendSetAttribute()` 和 `acdnnBackendGetAttribute()` 函数设置或获取的后端描述符属性。属性所属的后端描述符由属性名称的前缀标识。

```cpp
typedef enum{
ACDNN_ATTR_POINTWISE_MODE = 0,
ACDNN_ATTR_POINTWISE_MATH_PREC = 1,
ACDNN_ATTR_POINTWISE_NAN_PROPAGATION = 2,
ACDNN_ATTR_POINTWISE_RELU_LOWER_CLIP = 3,
ACDNN_ATTR_POINTWISE_RELU_UPPER_CLIP = 4,
ACDNN_ATTR_POINTWISE_RELU_LOWER_CLIP_SLOPE = 5,
ACDNN_ATTR_POINTWISE_ELU_ALPHA = 6,
ACDNN_ATTR_POINTWISE_SOFTPLUS_BETA = 7,
ACDNN_ATTR_CONVOLUTION_COMP_TYPE = 100,
ACDNN_ATTR_CONVOLUTION_CONV_MODE = 101,
ACDNN_ATTR_CONVOLUTION_DILATIONS = 102,
ACDNN_ATTR_CONVOLUTION_FILTER_STRIDES = 103,
ACDNN_ATTR_CONVOLUTION_POST_PADDINGS = 104,
ACDNN_ATTR_CONVOLUTION_PRE_PADDINGS = 105,
ACDNN_ATTR_CONVOLUTION_SPATIAL_DIMS = 106,
ACDNN_ATTR_ENGINEHEUR_MODE = 200,
ACDNN_ATTR_ENGINEHEUR_OPERATION_GRAPH = 201,
ACDNN_ATTR_ENGINEHEUR_RESULTS = 202,
ACDNN_ATTR_ENGINECFG_ENGINE = 300,
ACDNN_ATTR_ENGINECFG_INTERMEDIATE_INFO = 301,
ACDNN_ATTR_ENGINECFG_KNOB_CHOICES = 302,
ACDNN_ATTR_EXECUTION_PLAN_HANDLE = 400,
ACDNN_ATTR_EXECUTION_PLAN_ENGINE_CONFIG = 401,
ACDNN_ATTR_EXECUTION_PLAN_WORKSPACE_SIZE = 402,
ACDNN_ATTR_EXECUTION_PLAN_COMPUTED_INTERMEDIATE_UIDS = 403,
ACDNN_ATTR_EXECUTION_PLAN_RUN_ONLY_INTERMEDIATE_UIDS = 404,
ACDNN_ATTR_INTERMEDIATE_INFO_UNIQUE_ID = 500,
ACDNN_ATTR_INTERMEDIATE_INFO_SIZE = 501,
ACDNN_ATTR_INTERMEDIATE_INFO_DEPENDENT_DATA_UIDS = 502,
ACDNN_ATTR_INTERMEDIATE_INFO_DEPENDENT_ATTRIBUTES = 503,
ACDNN_ATTR_KNOB_CHOICE_KNOB_TYPE = 600,
ACDNN_ATTR_KNOB_CHOICE_KNOB_VALUE = 601,
ACDNN_ATTR_OPERATION_CONVOLUTION_FORWARD_ALPHA = 700,
ACDNN_ATTR_OPERATION_CONVOLUTION_FORWARD_BETA = 701,
ACDNN_ATTR_OPERATION_CONVOLUTION_FORWARD_CONV_DESC = 702,
ACDNN_ATTR_OPERATION_CONVOLUTION_FORWARD_W = 703,
ACDNN_ATTR_OPERATION_CONVOLUTION_FORWARD_X = 704,
ACDNN_ATTR_OPERATION_CONVOLUTION_FORWARD_Y = 705,
ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_DATA_ALPHA = 706,
ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_DATA_BETA = 707,
ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_DATA_CONV_DESC = 708,
ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_DATA_W = 709,
ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_DATA_DX = 710,
ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_DATA_DY = 711,
ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_FILTER_ALPHA = 712,
ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_FILTER_BETA = 713,
ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_FILTER_CONV_DESC = 714,
ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_FILTER_DW = 715,
ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_FILTER_X = 716,
ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_FILTER_DY = 717,
ACDNN_ATTR_OPERATION_POINTWISE_PW_DESCRIPTOR = 750,
ACDNN_ATTR_OPERATION_POINTWISE_XDESC = 751,
ACDNN_ATTR_OPERATION_POINTWISE_BDESC = 752,
ACDNN_ATTR_OPERATION_POINTWISE_YDESC = 753,
ACDNN_ATTR_OPERATION_POINTWISE_ALPHA1 = 754,
ACDNN_ATTR_OPERATION_POINTWISE_ALPHA2 = 755,
ACDNN_ATTR_OPERATION_POINTWISE_DXDESC = 756,
ACDNN_ATTR_OPERATION_POINTWISE_DYDESC = 757,
ACDNN_ATTR_OPERATION_POINTWISE_TDESC = 758,
ACDNN_ATTR_OPERATION_GENSTATS_MODE = 770,
ACDNN_ATTR_OPERATION_GENSTATS_MATH_PREC = 771,
ACDNN_ATTR_OPERATION_GENSTATS_XDESC = 772,
ACDNN_ATTR_OPERATION_GENSTATS_SUMDESC = 773,
ACDNN_ATTR_OPERATION_GENSTATS_SQSUMDESC = 774,
ACDNN_ATTR_OPERATION_BN_FINALIZE_STATS_MODE = 780,
ACDNN_ATTR_OPERATION_BN_FINALIZE_MATH_PREC = 781,
ACDNN_ATTR_OPERATION_BN_FINALIZE_Y_SUM_DESC = 782,
ACDNN_ATTR_OPERATION_BN_FINALIZE_Y_SQ_SUM_DESC = 783,
ACDNN_ATTR_OPERATION_BN_FINALIZE_SCALE_DESC = 784,
ACDNN_ATTR_OPERATION_BN_FINALIZE_BIAS_DESC = 785,
ACDNN_ATTR_OPERATION_BN_FINALIZE_PREV_RUNNING_MEAN_DESC = 786,
ACDNN_ATTR_OPERATION_BN_FINALIZE_PREV_RUNNING_VAR_DESC = 787,
ACDNN_ATTR_OPERATION_BN_FINALIZE_UPDATED_RUNNING_MEAN_DESC = 788,
ACDNN_ATTR_OPERATION_BN_FINALIZE_UPDATED_RUNNING_VAR_DESC = 789,
ACDNN_ATTR_OPERATION_BN_FINALIZE_SAVED_MEAN_DESC = 790,
ACDNN_ATTR_OPERATION_BN_FINALIZE_SAVED_INV_STD_DESC = 791,
ACDNN_ATTR_OPERATION_BN_FINALIZE_EQ_SCALE_DESC = 792,
ACDNN_ATTR_OPERATION_BN_FINALIZE_EQ_BIAS_DESC = 793,
ACDNN_ATTR_OPERATION_BN_FINALIZE_ACCUM_COUNT_DESC = 794,
ACDNN_ATTR_OPERATION_BN_FINALIZE_EPSILON_DESC = 795,
ACDNN_ATTR_OPERATION_BN_FINALIZE_EXP_AVERATE_FACTOR_DESC = 796,
ACDNN_ATTR_OPERATIONGRAPH_HANDLE = 800,
ACDNN_ATTR_OPERATIONGRAPH_OPS = 801,
ACDNN_ATTR_OPERATIONGRAPH_ENGINE_GLOBAL_COUNT = 802,
ACDNN_ATTR_TENSOR_BYTE_ALIGNMENT = 900,
ACDNN_ATTR_TENSOR_DATA_TYPE = 901,
ACDNN_ATTR_TENSOR_DIMENSIONS = 902,
ACDNN_ATTR_TENSOR_STRIDES = 903,
ACDNN_ATTR_TENSOR_VECTOR_COUNT = 904,
ACDNN_ATTR_TENSOR_VECTORIZED_DIMENSION = 905,
ACDNN_ATTR_TENSOR_UNIQUE_ID = 906,
ACDNN_ATTR_TENSOR_IS_VIRTUAL = 907,
ACDNN_ATTR_TENSOR_IS_BY_VALUE = 908,
ACDNN_ATTR_TENSOR_REORDERING_MODE = 909,
ACDNN_ATTR_VARIANT_PACK_UNIQUE_IDS = 1000,
ACDNN_ATTR_VARIANT_PACK_DATA_POINTERS = 1001,
ACDNN_ATTR_VARIANT_PACK_INTERMEDIATES = 1002,
ACDNN_ATTR_VARIANT_PACK_WORKSPACE = 1003,
ACDNN_ATTR_VARIANT_PACK_WORKSPACE_SIZE = 9000,
ACDNN_ATTR_LAYOUT_INFO_TENSOR_UID = 1100,
ACDNN_ATTR_LAYOUT_INFO_TYPES = 1101,
ACDNN_ATTR_KNOB_INFO_TYPE = 1200,
ACDNN_ATTR_KNOB_INFO_MAXIMUM_VALUE = 1201,
ACDNN_ATTR_KNOB_INFO_MINIMUM_VALUE = 1202,
ACDNN_ATTR_KNOB_INFO_STRIDE = 1203,
ACDNN_ATTR_ENGINE_OPERATION_GRAPH = 1300,
ACDNN_ATTR_ENGINE_GLOBAL_INDEX = 1301,
ACDNN_ATTR_ENGINE_KNOB_INFO = 1302,
ACDNN_ATTR_ENGINE_NUMERICAL_NOTE = 1303,
ACDNN_ATTR_ENGINE_LAYOUT_INFO = 1304,
ACDNN_ATTR_ENGINE_BEHAVIOR_NOTE = 1305,
ACDNN_ATTR_MATMUL_COMP_TYPE = 1500,
ACDNN_ATTR_OPERATION_MATMUL_ADESC = 1520,
ACDNN_ATTR_OPERATION_MATMUL_BDESC = 1521,
ACDNN_ATTR_OPERATION_MATMUL_CDESC = 1522,
ACDNN_ATTR_OPERATION_MATMUL_DESC = 1523,
ACDNN_ATTR_OPERATION_MATMUL_IRREGULARLY_STRIDED_BATCH_COUNT = 1524,
ACDNN_ATTR_REDUCTION_OPERATOR = 1600,
ACDNN_ATTR_REDUCTION_COMP_TYPE = 1601,
ACDNN_ATTR_OPERATION_REDUCTION_XDESC = 1610,
ACDNN_ATTR_OPERATION_REDUCTION_YDESC = 1611,
ACDNN_ATTR_OPERATION_REDUCTION_DESC = 1612,
ACDNN_ATTR_OPERATION_BN_BWD_WEIGHTS_MATH_PREC = 1620,
ACDNN_ATTR_OPERATION_BN_BWD_WEIGHTS_MEAN_DESC = 1621,
ACDNN_ATTR_OPERATION_BN_BWD_WEIGHTS_INVSTD_DESC = 1622,
ACDNN_ATTR_OPERATION_BN_BWD_WEIGHTS_BN_SCALE_DESC = 1623,
ACDNN_ATTR_OPERATION_BN_BWD_WEIGHTS_X_DESC = 1624,
ACDNN_ATTR_OPERATION_BN_BWD_WEIGHTS_DY_DESC = 1625,
ACDNN_ATTR_OPERATION_BN_BWD_WEIGHTS_DBN_SCALE_DESC = 1626,
ACDNN_ATTR_OPERATION_BN_BWD_WEIGHTS_DBN_BIAS_DESC = 1627,
ACDNN_ATTR_OPERATION_BN_BWD_WEIGHTS_EQ_DY_SCALE_DESC = 1628,
ACDNN_ATTR_OPERATION_BN_BWD_WEIGHTS_EQ_X_SCALE_DESC = 1629,
ACDNN_ATTR_OPERATION_BN_BWD_WEIGHTS_EQ_BIAS = 1630,
ACDNN_ATTR_RESAMPLE_MODE = 1700,
ACDNN_ATTR_RESAMPLE_COMP_TYPE = 1701,
ACDNN_ATTR_RESAMPLE_SPATIAL_DIMS = 1702,
ACDNN_ATTR_RESAMPLE_POST_PADDINGS = 1703,
ACDNN_ATTR_RESAMPLE_PRE_PADDINGS = 1704,
ACDNN_ATTR_RESAMPLE_STRIDES = 1705,
ACDNN_ATTR_RESAMPLE_WINDOW_DIMS = 1706,
ACDNN_ATTR_RESAMPLE_NAN_PROPAGATION = 1707,
ACDNN_ATTR_RESAMPLE_PADDING_MODE = 1708,
ACDNN_ATTR_OPERATION_RESAMPLE_FWD_XDESC = 1710,
ACDNN_ATTR_OPERATION_RESAMPLE_FWD_YDESC = 1711,
ACDNN_ATTR_OPERATION_RESAMPLE_FWD_IDXDESC = 1712,
ACDNN_ATTR_OPERATION_RESAMPLE_FWD_ALPHA = 1713,
ACDNN_ATTR_OPERATION_RESAMPLE_FWD_BETA = 1714,
ACDNN_ATTR_OPERATION_RESAMPLE_FWD_DESC = 1716,
ACDNN_ATTR_OPERATION_RESAMPLE_BWD_DXDESC = 1720,
ACDNN_ATTR_OPERATION_RESAMPLE_BWD_DYDESC = 1721,
ACDNN_ATTR_OPERATION_RESAMPLE_BWD_IDXDESC = 1722,
ACDNN_ATTR_OPERATION_RESAMPLE_BWD_ALPHA = 1723,
ACDNN_ATTR_OPERATION_RESAMPLE_BWD_BETA = 1724,
ACDNN_ATTR_OPERATION_RESAMPLE_BWD_DESC = 1725
} acdnnBackendAttributeName_t;
```

##### 5.1.1.2. acdnnBackendAttributeType_t {#5112-acdnnbackendattributetype_t}

枚举类型 `acdnnBackendAttributeType_t` 指定 acDNN 后端描述符属性的数据类型。它用于指定 `acdnnBackendSetAttribute()` 和 `acdnnBackendGetAttribute()` 的 `void *arrayOfElements` 参数指向的数据类型。

```cpp
typedef enum{
ACDNN_TYPE_HANDLE = 0,
ACDNN_TYPE_DATA_TYPE,
ACDNN_TYPE_BOOLEAN,
ACDNN_TYPE_INT64,
ACDNN_TYPE_FLOAT,
ACDNN_TYPE_DOUBLE,
ACDNN_TYPE_VOID_PTR,
ACDNN_TYPE_CONVOLUTION_MODE,
ACDNN_TYPE_HEUR_MODE,
ACDNN_TYPE_KNOB_TYPE,
ACDNN_TYPE_NAN_PROPOGATION,
ACDNN_TYPE_NUMERICAL_NOTE,
ACDNN_TYPE_LAYOUT_TYPE,
ACDNN_TYPE_ATTRIB_NAME,
ACDNN_TYPE_POINTWISE_MODE,
ACDNN_TYPE_BACKEND_DESCRIPTOR,
ACDNN_TYPE_GENSTATS_MODE,
ACDNN_TYPE_BN_FINALIZE_STATS_MODE,
ACDNN_TYPE_REDUCTION_OPERATOR_TYPE,
ACDNN_TYPE_BEHAVIOR_NOTE,
ACDNN_TYPE_TENSOR_REORDERING_MODE,
ACDNN_TYPE_RESAMPLE_MODE,
ACDNN_TYPE_PADDING_MODE,
ACDNN_TYPE_INT32
} acdnnBackendAttributeType_t;
```

`acdnnBackendAttributeType_t` 的属性类型

| `acdnnBackendAttributeType_t` | 属性类型 |
| :--- | :--- |
| `ACDNN_TYPE_HANDLE` | `acdnnHandle_t` |
| `ACDNN_TYPE_DATA_TYPE` | `acdnnDataType_t` |
| `ACDNN_TYPE_BOOLEAN` | `bool` |
| `ACDNN_TYPE_INT64` | `int64_t` |
| `ACDNN_TYPE_FLOAT` | `float` |
| `ACDNN_TYPE_DOUBLE` | `double` |
| `ACDNN_TYPE_VOID_PTR` | `void *` |
| `ACDNN_TYPE_CONVOLUTION_MODE` | `acdnnConvolutionMode_t` |
| `ACDNN_TYPE_HEUR_MODE` | `acdnnBackendHeurMode_t` |
| `ACDNN_TYPE_KNOB_TYPE` | `acdnnBackendKnobType_t` |
| `ACDNN_TYPE_NAN_PROPOGATION` | `acdnnNanPropagation_t` |
| `ACDNN_TYPE_NUMERICAL_NOTE` | `acdnnBackendNumericalNote_t` |
| `ACDNN_TYPE_LAYOUT_TYPE` | `acdnnBackendLayoutType_t` |
| `ACDNN_TYPE_ATTRIB_NAME` | `acdnnBackendAttributeName_t` |
| `ACDNN_TYPE_POINTWISE_MODE` | `acdnnPointwiseMode_t` |
| `ACDNN_TYPE_BACKEND_DESCRIPTOR` | `acdnnBackendDescriptor_t` |
| `ACDNN_TYPE_GENSTATS_MODE` | `acdnnGenStatsMode_t` |
| `ACDNN_TYPE_BN_FINALIZE_STATS_MODE` | `acdnnBnFinalizeStatsMode_t` |
| `ACDNN_TYPE_REDUCTION_OPERATOR_TYPE` | `acdnnReduceTensorOp_t` |
| `ACDNN_TYPE_BEHAVIOR_NOTE` | `acdnnBackendBehaviorNote_t` |
| `ACDNN_TYPE_TENSOR_REORDERING_MODE` | `acdnnBackendTensorReordering_t` |
| `ACDNN_TYPE_RESAMPLE_MODE` | `acdnnResampleMode_t` |
| `ACDNN_TYPE_PADDING_MODE` | `acdnnPaddingMode_t` |
| `ACDNN_TYPE_INT32` | `int32_t` |

##### 5.1.1.3. acdnnBackendBehaviorNote_t {#5113-acdnnbackendbehaviornote_t}

`acdnnBackendBehaviorNote_t` 是一个枚举类型，表示引擎的可查询行为说明。开发者可以使用 `acdnnBackendGetAttribute()` 函数从 `ACDNN_BACKEND_ENGINE_DESC` 查询行为说明数组。

```cpp
typedef enum {
ACDNN_BEHAVIOR_NOTE_RUNTIME_COMPILATION = 0,
ACDNN_BEHAVIOR_NOTE_REQUIRES_FILTER_INT8x32_REORDER = 1,
ACDNN_BEHAVIOR_NOTE_REQUIRES_BIAS_INT8x32_REORDER = 2,
ACDNN_BEHAVIOR_NOTE_TYPE_COUNT,
} acdnnBackendBehaviorNote_t;
```

##### 5.1.1.4. acdnnBackendDescriptorType_t {#5114-acdnnbackenddescriptortype_t}

`acdnnBackendDescriptorType_t` 是一个枚举类型，表示后端描述符的类型。开发者通过将来自此枚举的值传递给 `acdnnBackendCreateDescriptor()` 函数来创建特定类型的后端描述符。

```cpp
typedef enum {
ACDNN_BACKEND_POINTWISE_DESCRIPTOR = 0,
ACDNN_BACKEND_CONVOLUTION_DESCRIPTOR,
ACDNN_BACKEND_ENGINE_DESCRIPTOR,
ACDNN_BACKEND_ENGINECFG_DESCRIPTOR,
ACDNN_BACKEND_ENGINEHEUR_DESCRIPTOR,
ACDNN_BACKEND_EXECUTION_PLAN_DESCRIPTOR,
ACDNN_BACKEND_INTERMEDIATE_INFO_DESCRIPTOR,
ACDNN_BACKEND_KNOB_CHOICE_DESCRIPTOR,
ACDNN_BACKEND_KNOB_INFO_DESCRIPTOR,
ACDNN_BACKEND_LAYOUT_INFO_DESCRIPTOR,
ACDNN_BACKEND_OPERATION_CONVOLUTION_FORWARD_DESCRIPTOR,
ACDNN_BACKEND_OPERATION_CONVOLUTION_BACKWARD_FILTER_DESCRIPTOR,
ACDNN_BACKEND_OPERATION_CONVOLUTION_BACKWARD_DATA_DESCRIPTOR,
ACDNN_BACKEND_OPERATION_POINTWISE_DESCRIPTOR,
ACDNN_BACKEND_OPERATION_GEN_STATS_DESCRIPTOR,
ACDNN_BACKEND_OPERATIONGRAPH_DESCRIPTOR,
ACDNN_BACKEND_VARIANT_PACK_DESCRIPTOR,
ACDNN_BACKEND_TENSOR_DESCRIPTOR,
ACDNN_BACKEND_MATMUL_DESCRIPTOR,
ACDNN_BACKEND_OPERATION_MATMUL_DESCRIPTOR,
ACDNN_BACKEND_OPERATION_BN_FINALIZE_STATISTICS_DESCRIPTOR,
ACDNN_BACKEND_REDUCTION_DESCRIPTOR,
ACDNN_BACKEND_OPERATION_REDUCTION_DESCRIPTOR,
ACDNN_BACKEND_OPERATION_BN_BWD_WEIGHTS_DESCRIPTOR,
ACDNN_BACKEND_RESAMPLE_DESCRIPTOR,
ACDNN_BACKEND_OPERATION_RESAMPLE_FWD_DESCRIPTOR,
ACDNN_BACKEND_OPERATION_RESAMPLE_BWD_DESCRIPTOR
} acdnnBackendDescriptorType_t;
```

##### 5.1.1.5. acdnnBackendHeurMode_t {#5115-acdnnbackendheurmode_t}

`acdnnBackendHeurMode_t` 是一个枚举类型，表示 `ACDNN_BACKEND_ENGINEHEUR_DESCRIPTOR` 的操作模式。

```cpp
typedef enum {
ACDNN_HEUR_MODE_INSTANT = 0,
ACDNN_HEUR_MODE_B = 1,
ACDNN_HEUR_MODE_FALLBACK = 2,
ACDNN_HEUR_MODE_A = 3,
ACDNN_HEUR_MODES_COUNT = 4
} acdnnBackendHeurMode_t;
```

| 值 | 描述 |
| :--- | :--- |
| `ACDNN_HEUR_MODE_A` / `ACDNN_HEUR_MODE_INSTANT` | `ACDNN_HEUR_MODE_A` 提供与 `ACDNN_HEUR_MODE_INSTANT` 完全相同的功能。此重命名的目的是更好地匹配 `ACDNN_HEUR_MODE_B` 的命名。|
| `ACDNN_HEUR_MODE_B` | 可以利用基于神经网络的启发式（Heuristics）来提高与 `ACDNN_HEUR_MODE_INSTANT` 相比的泛化性能。在使用神经网络的情况下，CPU 上的推理时间将比 `ACDNN_HEUR_MODE_INSTANT` 增加 10-100 倍。以下情况不支持这些神经网络启发式：<br>- 3D 卷积<br>- 分组卷积（groupCount 大于 1）<br>- 扩张卷积（任何空间维度的扩张大于 1）<br><br>此外，仅在 acDNN 在真武 PPU 上运行时，神经网络才在 x86 平台上启用。在不支持神经网络的情况下， `ACDNN_HEUR_MODE_B` 也将回退到 `ACDNN_HEUR_MODE_INSTANT`。在预计 `ACDNN_HEUR_MODE_B` 的开销会降低整体网络性能的情况下， `ACDNN_HEUR_MODE_B` 将回退到 `ACDNN_HEUR_MODE_INSTANT`。 |
| `ACDNN_HEUR_MODE_FALLBACK` | 此启发式模式旨在用于查找提供功能支持的回退选项（不期望提供最优的真武 PPU 性能）。 |

##### 5.1.1.6. acdnnBackendKnobType_t {#5116-acdnnbackendknobtype_t}

`acdnnBackendKnobType_t` 是一个枚举类型，表示性能调优旋钮（Performance Knobs）的类型。性能调优旋钮是引擎的运行时设置，会影响其性能。开发者可以使用 `acdnnBackendGetAttribute()` 函数从 `ACDNN_BACKEND_ENGINE_DESCRIPTOR` 查询性能调优旋钮数组及其有效值范围。开发者可以使用 `ACDNN_BACKEND_KNOB_CHOICE_DESCRIPTOR` 描述符通过 `acdnnBackendSetAttribute()` 函数设置每个旋钮的选项。

```cpp
typedef enum {
ACDNN_KNOB_TYPE_SPLIT_K = 0,
ACDNN_KNOB_TYPE_SWIZZLE = 1,
ACDNN_KNOB_TYPE_TILE_SIZE = 2,
ACDNN_KNOB_TYPE_USE_TEX = 3,
ACDNN_KNOB_TYPE_EDGE = 4,
ACDNN_KNOB_TYPE_KBLOCK = 5,
ACDNN_KNOB_TYPE_LDGA = 6,
ACDNN_KNOB_TYPE_LDGB = 7,
ACDNN_KNOB_TYPE_CHUNK_K = 8,
ACDNN_KNOB_TYPE_SPLIT_H = 9,
ACDNN_KNOB_TYPE_WINO_TILE = 10,
ACDNN_KNOB_TYPE_MULTIPLY = 11,
ACDNN_KNOB_TYPE_SPLIT_K_BUF = 12,
ACDNN_KNOB_TYPE_TILEK = 13,
ACDNN_KNOB_TYPE_STAGES = 14,
ACDNN_KNOB_TYPE_REDUCTION_MODE = 15,
ACDNN_KNOB_TYPE_CTA_SPLIT_K_MODE = 16,
ACDNN_KNOB_TYPE_SPLIT_K_SLC = 17,
ACDNN_KNOB_TYPE_IDX_MODE = 18,
ACDNN_KNOB_TYPE_SLICED = 19,
ACDNN_KNOB_TYPE_SPLIT_RS = 20,
ACDNN_KNOB_TYPE_SINGLEBUFFER = 21,
ACDNN_KNOB_TYPE_LDGC = 22,
ACDNN_KNOB_TYPE_SPECFILT = 23,
ACDNN_KNOB_TYPE_KERNEL_CFG = 24,
ACDNN_KNOB_TYPE_COUNTS = 25,
} acdnnBackendKnobType_t;
```

##### 5.1.1.7. acdnnBackendLayoutType_t {#5117-acdnnbackendlayouttype_t}

`acdnnBackendLayoutType_t` 是一个枚举类型，表示引擎的可查询布局要求。开发者可以使用 `acdnnBackendGetAttribute()` 函数从 `ACDNN_BACKEND_ENGINE_DESC` 描述符查询布局要求。

```cpp
typedef enum {
ACDNN_LAYOUT_TYPE_PREFERRED_NCHW = 0,
ACDNN_LAYOUT_TYPE_PREFERRED_NHWC = 1,
ACDNN_LAYOUT_TYPE_PREFERRED_PAD4CK = 2,
ACDNN_LAYOUT_TYPE_PREFERRED_PAD8CK = 3,
ACDNN_LAYOUT_TYPE_COUNT = 4,
} acdnnBackendLayoutType_t;
```

##### 5.1.1.8. acdnnBackendNumericalNote_t {#5118-acdnnbackendnumericalnote_t}

`acdnnBackendNumericalNote_t` 是一个枚举类型，表示引擎的可查询数值属性。开发者可以使用 `acdnnBackendGetAttribute()` 函数从 `ACDNN_BACKEND_ENGINE_DESC` 查询数值属性数组。

```cpp
typedef enum {
ACDNN_NUMERICAL_NOTE_TENSOR_CORE = 0,
ACDNN_NUMERICAL_NOTE_DOWN_CONVERT_INPUTS,
ACDNN_NUMERICAL_NOTE_REDUCED_PRECISION_REDUCTION,
ACDNN_NUMERICAL_NOTE_FFT,
ACDNN_NUMERICAL_NOTE_NONDETERMINISTIC,
ACDNN_NUMERICAL_NOTE_WINOGRAD,
ACDNN_NUMERICAL_NOTE_WINOGRAD_TILE_4x4,
ACDNN_NUMERICAL_NOTE_WINOGRAD_TILE_6x6,
ACDNN_NUMERICAL_NOTE_WINOGRAD_TILE_13x13,
ACDNN_NUMERICAL_NOTE_TYPE_COUNT,
} acdnnBackendNumericalNote_t;
```

##### 5.1.1.9. acdnnBackendTensorReordering_t {#5119-acdnnbackendtensorreordering_t}

`acdnnBackendTensorReordering_t` 是一个枚举类型，表示张量重排（Tensor Reordering）作为张量描述符的属性。开发者可以通过 `acdnnBackendSetAttribute()` 和 `acdnnBackendGetAttribute()` 函数在 `ACDNN_BACKEND_TENSOR_DESCRIPTOR` 中获取和设置此属性。

```cpp
typedef enum {
ACDNN_TENSOR_REORDERING_NONE = 0,
ACDNN_TENSOR_REORDERING_INT8x32 = 1
} acdnnBackendTensorReordering_t;
```

##### 5.1.1.10. acdnnBnFinalizeStatsMode_t {#51110-acdnnbnfinalizestatsmode_t}

`acdnnBnFinalizeStatsMode_t` 是一个枚举类型，公开了不同的数学运算模式，这些模式将批归一化统计量和训练后的缩放和偏置转换为等效的缩放和偏置，以在推理和训练用例的下一个归一化阶段应用。

```cpp
typedef enum {
ACDNN_BN_FINALIZE_STATISTICS_TRAINING = 0,
ACDNN_BN_FINALIZE_STATISTICS_INFERENCE = 1,
} acdnnBnFinalizeStatsMode_t;
```

`acdnnBnFinalizeStatsMode_t` 的批归一化统计模式

| 批归一化统计模式 | 描述 |
| :--- | :--- |
| `ACDNN_BN_FINALIZE_STATISTICS_TRAINING` | 从 ySum、ySqSum 以及学习到的缩放、偏置计算等效的缩放和偏置。可选地，更新运行统计量并生成已保存统计量以与 `acdnnBatchNormalizationBackward()`、`acdnnBatchNormalizationBackwardEx()` 互操作。 |
| `ACDNN_BN_FINALIZE_STATISTICS_INFERENCE` | 从学习到的运行统计量以及学习到的缩放、偏置计算等效的缩放和偏置。 |

##### 5.1.1.11. acdnnGenStatsMode_t {#51111-acdnngenstatsmode_t}

`acdnnGenStatsMode_t` 是一个枚举类型，用于指示后端统计生成操作中的统计模式。

| 值 | 描述 |
| :--- | :--- |
| `ACDNN_GENSTATS_SUM_SQSUM` | 在此模式下，计算输入张量沿指定维度的和与平方和并写出。目前支持的归约维度仅限于逐通道，但可以根据请求添加额外支持。 |

##### 5.1.1.12. acdnnPaddingMode_t {#51112-acdnnpaddingmode_t}

`acdnnPaddingMode_t` 是一个枚举类型，用于指示后端重采样操作中的填充。

```cpp
typedef enum {
ACDNN_ZERO_PAD = 0,
ACDNN_NEG_INF_PAD = 1,
ACDNN_EDGE_VAL_PAD = 2,
} acdnnPaddingMode_t;
```

##### 5.1.1.13. acdnnPointwiseMode_t {#51113-acdnnpointwisemode_t}

`acdnnPointwiseMode_t` 是一个枚举类型，用于指示后端逐点运算描述符中预期的逐点数学运算。

| 值 | 描述 |
| :--- | :--- |
| `ACDNN_POINTWISE_ADD` | 在此模式下，计算两个张量之间的逐点加法。 |
| `ACDNN_POINTWISE_ADD_SQUARE` | 在此模式下，计算第一个张量与第二个张量的平方之间的逐点加法。 |
| `ACDNN_POINTWISE_DIV` | 在此模式下，计算第一个张量除以第二个张量的逐点真除法。 |
| `ACDNN_POINTWISE_MAX` | 在此模式下，在两个张量之间取逐点最大值。 |
| `ACDNN_POINTWISE_MIN` | 在此模式下，在两个张量之间取逐点最小值。 |
| `ACDNN_POINTWISE_MOD` | 在此模式下，计算第一个张量除以第二个张量的逐点浮点余数。 |
| `ACDNN_POINTWISE_MUL` | 在此模式下，计算两个张量之间的逐点乘法。 |
| `ACDNN_POINTWISE_POW` | 在此模式下，计算第一个张量的第二个张量次幂的逐点值。 |
| `ACDNN_POINTWISE_SUB` | 在此模式下，计算两个张量之间的逐点减法。 |
| `ACDNN_POINTWISE_ABS` | 在此模式下，计算输入张量的逐点绝对值。 |
| `ACDNN_POINTWISE_CEIL` | 在此模式下，计算输入张量的逐点向上取整。 |
| `ACDNN_POINTWISE_COS` | 在此模式下，计算输入张量的逐点三角余弦。 |
| `ACDNN_POINTWISE_EXP` | 在此模式下，计算输入张量的逐点指数。 |
| `ACDNN_POINTWISE_FLOOR` | 在此模式下，计算输入张量的逐点向下取整。 |
| `ACDNN_POINTWISE_LOG` | 在此模式下，计算输入张量的逐点自然对数。 |
| `ACDNN_POINTWISE_NEG` | 在此模式下，计算输入张量的逐点数值取负。 |
| `ACDNN_POINTWISE_RSQRT` | 在此模式下，计算输入张量平方根的逐点倒数。 |
| `ACDNN_POINTWISE_SIN` | 在此模式下，计算输入张量的逐点三角正弦。 |
| `ACDNN_POINTWISE_SQRT` | 在此模式下，计算输入张量的逐点平方根。 |
| `ACDNN_POINTWISE_TAN` | 在此模式下，计算输入张量的逐点三角正切。 |
| `ACDNN_POINTWISE_IDENTITY_FWD` | 在此模式下，不执行任何计算。与其他逐点模式一样，此模式通过指定输入张量的数据类型为一种类型，输出张量的数据类型为另一种类型来提供隐式转换。 |
| `ACDNN_POINTWISE_LEAKYRELU_FWD` | 在此模式下，计算输入张量的逐点 Leaky ReLU 激活函数。 |
| `ACDNN_POINTWISE_CLIP_RELU_FWD` | 在此模式下，计算输入张量的逐点 Clipped ReLU 激活函数。 |
| `ACDNN_POINTWISE_PRELU_FWD` | 在此模式下，计算输入张量的逐点 Parametric ReLU 激活函数。 |
| `ACDNN_POINTWISE_HSWISH_FWD` | 在此模式下，计算输入张量的逐点 Hard Swish 激活函数。 |
| `ACDNN_POINTWISE_HSIGMOID_FWD` | 在此模式下，计算输入张量的逐点 Hard Sigmoid 激活函数。 |
| `ACDNN_POINTWISE_RELU_FWD` | 在此模式下，计算输入张量的逐点修正线性（Rectified Linear）激活函数。 |
| `ACDNN_POINTWISE_TANH_FWD` | 在此模式下，计算输入张量的逐点 Tanh 激活函数。 |
| `ACDNN_POINTWISE_SIGMOID_FWD` | 在此模式下，计算输入张量的逐点 Sigmoid 激活函数。 |
| `ACDNN_POINTWISE_ELU_FWD` | 在此模式下，计算输入张量的逐点指数线性单元（ELU）激活函数。 |
| `ACDNN_POINTWISE_GELU_FWD` | 在此模式下，计算输入张量的逐点高斯误差线性单元（GELU）激活函数。 |
| `ACDNN_POINTWISE_SOFTPLUS_FWD` | 在此模式下，计算输入张量的逐点 Softplus 激活函数。 |
| `ACDNN_POINTWISE_GELU_APPROX_TANH_FWD` | 在此模式下，计算输入张量的高斯误差线性单元激活函数的逐点 Tanh 近似。Tanh GELU 近似的计算公式为 $0.5 \times (1 + \tanh[\sqrt{2/\pi}(x + 0.044715x^3)])$。有关更多信息，请参阅 GAUSSIAN ERROR LINEAR UNIT (GELUS) 论文。 |
| `ACDNN_POINTWISE_RELU_BWD` | 在此模式下，计算输入张量的修正线性激活的逐点一阶导数。 |
| `ACDNN_POINTWISE_TANH_BWD` | 在此模式下，计算输入张量的 Tanh 激活的逐点一阶导数。 |
| `ACDNN_POINTWISE_SIGMOID_BWD` | 在此模式下，计算输入张量的 Sigmoid 激活的逐点一阶导数。 |
| `ACDNN_POINTWISE_ELU_BWD` | 在此模式下，计算输入张量的指数线性单元激活的逐点一阶导数。 |
| `ACDNN_POINTWISE_GELU_BWD` | 在此模式下，计算输入张量的高斯误差线性单元激活的逐点一阶导数。 |
| `ACDNN_POINTWISE_SOFTPLUS_BWD` | 在此模式下，计算输入张量的 Softplus 激活的逐点一阶导数。 |
| `ACDNN_POINTWISE_GELU_APPROX_TANH_BWD` | 在此模式下，计算输入张量的高斯误差线性单元激活的 Tanh 近似的逐点一阶导数。计算公式为 $0.5(1 + \tanh(b(x + cx^3)) + bx\text{sech}^2(b(cx^3 + x))(3cx^2 + 1))d$，其中 $b$ 为 $\sqrt{\frac{2}{\pi}}$，$c$ 为 $0.044715$。 |
| `ACDNN_POINTWISE_CMP_EQ` | 在此模式下，计算第一个张量等于第二个张量的逐点真值。 |
| `ACDNN_POINTWISE_CMP_NEQ` | 在此模式下，计算第一个张量不等于第二个张量的逐点真值。 |
| `ACDNN_POINTWISE_CMP_GT` | 在此模式下，计算第一个张量大于第二个张量的逐点真值。 |
| `ACDNN_POINTWISE_CMP_GE` | 在此模式下，计算第一个张量大于等于第二个张量的逐点真值。 |
| `ACDNN_POINTWISE_CMP_LT` | 在此模式下，计算第一个张量小于第二个张量的逐点真值。 |
| `ACDNN_POINTWISE_CMP_LE` | 在此模式下，计算第一个张量小于等于第二个张量的逐点真值。 |
| `ACDNN_POINTWISE_LOGICAL_AND` | 在此模式下，计算第一个张量逻辑 AND 第二个张量的逐点真值。 |
| `ACDNN_POINTWISE_LOGICAL_OR` | 在此模式下，计算第一个张量逻辑 OR 第二个张量的逐点真值。 |
| `ACDNN_POINTWISE_LOGICAL_NOT` | 在此模式下，计算输入张量的逻辑 NOT 的逐点真值。 |

##### 5.1.1.14. acdnnResampleMode_t {#51114-acdnnresamplemode_t}

`acdnnResampleMode_t` 是一个枚举类型，用于指示后端重采样操作中的重采样模式（Resample 模式）。

```cpp
typedef enum {
ACDNN_RESAMPLE_NEAREST = 0,
ACDNN_RESAMPLE_BILINEAR = 1,
ACDNN_RESAMPLE_AVGPOOL = 2,
ACDNN_RESAMPLE_MAXPOOL = 3,
} acdnnResampleMode_t;
```

#### 5.1.2. acdnn_backend.h 中的数据类型 {#512-acdnn_backendh-中的数据类型}

这些是在 `acdnn_backend.h` 中找到的数据类型。

##### 5.1.2.1. acdnnBackendDescriptor_t {#5121-acdnnbackenddescriptor_t}

`acdnnBackendDescriptor_t` 是一个 typedef void 指针，指向许多不透明的描述符结构之一。它指向的结构类型由使用 `acdnnBackendCreateDescriptor()` 为不透明结构分配内存时的参数决定。

描述符的属性可以使用 `acdnnBackendSetAttribute()` 设置。在设置描述符的所有必需属性后，可以通过 `acdnnBackendFinalize()` 定型描述符。从已定型的描述符中，可以使用 `acdnnBackendGetAttribute()` 查询其可查询属性。最后，可以使用 `acdnnBackendDestroyDescriptor()` 释放为描述符分配的内存。

### 5.2. API 函数 {#52-api-函数}

Backend API 共 7 个公开函数，按用途分三组：

- **生命周期** ： `Create / Initialize / Destroy`，分别是新分配 / 在已分配内存上原位初始化 / 销毁。
- **属性读写** ： `SetAttribute / GetAttribute`，前者只在 finalize 之前可用，后者只在 finalize 之后可用。
- **执行** ： `Finalize / Execute`，前者对描述符的设置进行定型，后者在执行计划 + 变体包上启动实际计算。

#### 5.2.1. acdnnBackendCreateDescriptor() {#521-acdnnbackendcreatedescriptor}

```cpp
acdnnStatus_t acdnnBackendCreateDescriptor(
    acdnnBackendDescriptorType_t descriptorType,
    acdnnBackendDescriptor_t *descriptor);
```

按 `descriptorType` 分配并返回一个新的后端描述符实例（`acdnnBackendDescriptor_t` 实质是 `void *`）。

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `descriptorType` | 输入 | 来自 `acdnnBackendDescriptorType_t` 的枚举值 |
| `descriptor` | 输出 | 用于接收新描述符的指针 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：不支持该描述符类型。
- `ACDNN_STATUS_ALLOC_FAILED`：内存分配失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.2.2. acdnnBackendDestroyDescriptor() {#522-acdnnbackenddestroydescriptor}

```cpp
acdnnStatus_t acdnnBackendDestroyDescriptor(
    acdnnBackendDescriptor_t descriptor);
```

销毁由 `acdnnBackendCreateDescriptor()` 创建的描述符实例。返回后该指针所指内容**未定义** 。

!!! note
    Create 与 Destroy 之间若直接修改了描述符指向的字节，行为未定义。

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_ALLOC_FAILED`：销毁失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.2.3. acdnnBackendExecute() {#523-acdnnbackendexecute}

```cpp
acdnnStatus_t acdnnBackendExecute(
    acdnnHandle_t handle,
    acdnnBackendDescriptor_t executionPlan,
    acdnnBackendDescriptor_t variantPack);
```

在已定型（finalized）的 `executionPlan` 上启动一次实际计算。所有运行期可变信息（每个非虚张量的指针、工作空间缓冲区）都封装在 `variantPack` 里。

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `handle` | 输入 | acDNN 句柄 |
| `executionPlan` | 输入 | 已定型（finalized）的执行计划 |
| `variantPack` | 输入 | 已定型的变体包：含每个非虚张量的设备数据指针，以及 ≥ `ACDNN_ATTR_EXECUTION_PLAN_WORKSPACE_SIZE` 大小的工作空间指针 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：入参不合法（例如必填指针为 NULL）。
- `ACDNN_STATUS_INTERNAL_ERROR`：内部错误。
- `ACDNN_STATUS_EXECUTION_FAILED`：真武 PPU 上启动 / 执行失败。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.2.4. acdnnBackendFinalize() {#524-acdnnbackendfinalize}

```cpp
acdnnStatus_t acdnnBackendFinalize(
    acdnnBackendDescriptor_t descriptor);
```

对描述符在 Create / Initialize 之后所设的属性集**整体校验并定型** 。具体定型逻辑取决于描述符的类型。

定型成功后，描述符的已定型（finalized）状态变为 `true`：

- 之后**不再允许** 调用 `SetAttribute`；
- 之前**也不允许** 调用 `GetAttribute`，只有定型后才能查属性。

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：属性值非法或互相冲突。
- `ACDNN_STATUS_NOT_SUPPORTED`：当前 acDNN 版本不支持该属性组合。
- `ACDNN_STATUS_INTERNAL_ERROR`：内部错误。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.2.5. acdnnBackendGetAttribute() {#525-acdnnbackendgetattribute}

```cpp
acdnnStatus_t acdnnBackendGetAttribute(
    acdnnBackendDescriptor_t descriptor,
    acdnnBackendAttributeName_t attributeName,
    acdnnBackendAttributeType_t attributeType,
    int64_t requestedElementCount,
    int64_t *elementCount,
    void *arrayOfElements);
```

从已定型的描述符中读出指定属性。 未定型直接返回 `ACDNN_STATUS_NOT_INITIALIZED`。

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `descriptor` | 输入 | 待查描述符 |
| `attributeName` | 输入 | 属性键 |
| `attributeType` | 输入 | 属性类型，必须与 `attributeName` 在 `acdnnBackendAttributeType_t` 表中规定的类型一致 |
| `requestedElementCount` | 输入 | `arrayOfElements` 的容量 |
| `elementCount` | 输出 | 该属性实际存有的元素数；函数实际写入 `min(requestedElementCount, elementCount)` 个 |
| `arrayOfElements` | 输出 | 接收元素的数组（属性是单值时也可传指向单个变量的指针） |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：例如 `attributeName` 不属于该描述符、或 `attributeType` 不匹配。
- `ACDNN_STATUS_NOT_INITIALIZED`：描述符尚未通过 `acdnnBackendFinalize()` 定型。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.2.6. acdnnBackendInitialize() {#526-acdnnbackendinitialize}

```cpp
acdnnStatus_t acdnnBackendInitialize(
    acdnnBackendDescriptor_t descriptor);
```

初始化一个已由 `acdnnBackendCreateDescriptor()` 创建的后端描述符，将其内部状态重置为初始值。返回后描述符的已定型（finalized）状态为 `false`。

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `descriptor` | 输入 | 由 `acdnnBackendCreateDescriptor()` 创建的描述符 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_BAD_PARAM`：`descriptor` 无效。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.2.7. acdnnBackendSetAttribute() {#527-acdnnbackendsetattribute}

```cpp
acdnnStatus_t acdnnBackendSetAttribute(
    acdnnBackendDescriptor_t descriptor,
    acdnnBackendAttributeName_t attributeName,
    acdnnBackendAttributeType_t attributeType,
    int64_t elementCount,
    const void *arrayOfElements);
```

向描述符写入一个属性值。 已定型的描述符直接返回 `ACDNN_STATUS_NOT_INITIALIZED`。

| 参数 | 方向 | 说明 |
| :--- | :--- | :--- |
| `descriptor` | 输入 | 目标描述符 |
| `attributeName` | 输入 | 属性键 |
| `attributeType` | 输入 | 属性类型，须匹配 `attributeName` |
| `elementCount` | 输入 | `arrayOfElements` 中的元素个数 |
| `arrayOfElements` | 输入 | 元素值数组，元素类型由 `attributeType` 决定 |

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_INITIALIZED`：描述符已定型。
- `ACDNN_STATUS_BAD_PARAM`：属性键非法、类型不匹配、`elementCount` 不符或 `arrayOfElements` 中含非法值。
- `ACDNN_STATUS_NOT_SUPPORTED`：当前 acDNN 版本不支持设置该值。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

### 5.3. 描述符类型 {#53-描述符类型}

下文按"每节一个描述符类型"组织，每节给出该描述符的创建调用、用途、可配置/可读取的属性表，以及定型时常见的返回码。属性表按"必需 / 可选"和"可读 / 只读"两个维度区分。可与 5.4 用例中的端到端示例对照阅读。

#### 5.3.1. ACDNN_BACKEND_CONVOLUTION_DESCRIPTOR {#531-acdnn_backend_convolution_descriptor}

通过以下方式创建：
```cpp
acdnnBackendCreateDescriptor(ACDNN_BACKEND_CONVOLUTION_DESCRIPTOR, &desc);
```

acDNN 后端卷积描述符指定用于前向和反向传播的卷积算子的参数：计算数据类型、卷积模式、滤波器扩张和步幅，以及两侧的填充。

**属性**

acDNN 后端卷积描述符的属性是枚举类型 `acdnnBackendAttributeName_t` 的值，前缀为 `ACDNN_ATTR_CONVOLUTION_`：

| 值 | 描述 |
| :--- | :--- |
| `ACDNN_ATTR_CONVOLUTION_COMP_TYPE` | 卷积算子的计算类型。<br>**类型** ： `ACDNN_TYPE_DATA_TYPE`；一个元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_CONVOLUTION_CONV_MODE` | 卷积或互相关模式。<br>**类型** ： `ACDNN_TYPE_CONVOLUTION_MODE`；一个元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_CONVOLUTION_DILATIONS` | 滤波器扩张。<br>**类型** ： `ACDNN_TYPE_INT64`；一个或多个元素，但元素数受限于库支持的最大维度数。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_CONVOLUTION_FILTER_STRIDES` | 滤波器步幅。<br>**类型** ： `ACDNN_TYPE_INT64`；一个或多个元素，但元素数受限于库支持的最大维度数。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_CONVOLUTION_PRE_PADDINGS` | 每个空间维度开头的填充。<br>**类型** ： `ACDNN_TYPE_INT64`；一个或多个元素，但元素数受限于库支持的最大维度数。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_CONVOLUTION_POST_PADDINGS` | 每个空间维度末尾的填充。<br>**类型** ： `ACDNN_TYPE_INT64`；一个或多个元素，但元素数受限于库支持的最大维度数。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_CONVOLUTION_SPATIAL_DIMS` | 卷积中的空间维度数量。<br>**类型** ： `ACDNN_TYPE_INT64`，一个元素。<br>**要求** ：必需属性。 |

**定型**

使用 `ACDNN_BACKEND_CONVOLUTION_DESCRIPTOR` 调用 `acdnnBackendFinalize()` 可能返回以下值：

返回码：

- `ACDNN_STATUS_BAD_PARAM`：设置 `ACDNN_ATTR_CONVOLUTION_DILATIONS`、`ACDNN_ATTR_CONVOLUTION_FILTER_STRIDES`、`ACDNN_ATTR_CONVOLUTION_PRE_PADDINGS` 和 `ACDNN_ATTR_CONVOLUTION_POST_PADDINGS` 的 `elemCount` 参数不等于为 `ACDNN_ATTR_CONVOLUTION_SPATIAL_DIMS` 设置的值。
- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.3.2. ACDNN_BACKEND_ENGINE_DESCRIPTOR {#532-acdnn_backend_engine_descriptor}

使用描述符类型值 `ACDNN_BACKEND_ENGINE_DESCRIPTOR` 创建，acDNN 后端引擎描述符描述用于计算操作图的引擎。引擎是具有相似计算和数值属性的核函数分组。

**属性**

引擎属性（`ACDNN_ATTR_ENGINE_*`）

acDNN 后端引擎描述符的属性是枚举类型 `acdnnBackendAttributeName_t` 的值，前缀为 `ACDNN_ATTR_ENGINE_`。

| 属性名称 | 类型 | 描述和约束 | 要求 |
| :--- | :--- | :--- | :--- |
| `ACDNN_ATTR_ENGINE_OPERATION_GRAPH` | `ACDNN_TYPE_BACKEND_DESCRIPTOR`（1 个 `ACDNN_BACKEND_OPERATIONGRAPH_DESCRIPTOR` 元素） | 要计算的操作图。 | 必需 |
| `ACDNN_ATTR_ENGINE_GLOBAL_INDEX` | `ACDNN_TYPE_INT64`（1 个元素） | 引擎的索引。<br>有效范围：`0` ~ `ACDNN_ATTR_OPERATIONGRAPH_ENGINE_GLOBAL_COUNT - 1` | 必需 |
| `ACDNN_ATTR_ENGINE_KNOB_INFO` | `ACDNN_TYPE_BACKEND_DESCRIPTOR`（1 个 `ACDNN_BACKEND_KNOB_INFO_DESCRIPTOR` 元素） | 引擎的性能调优旋钮的描述符。 | 只读 |
| `ACDNN_ATTR_ENGINE_NUMERICAL_NOTE` | `ACDNN_TYPE_NUMERICAL_NOTE`（0 个或多个元素） | 引擎的数值属性。 | 只读 |
| `ACDNN_ATTR_ENGINE_LAYOUT_INFO` | `ACDNN_TYPE_BACKEND_DESCRIPTOR`（1 个 `ACDNN_BACKEND_LAYOUT_INFO_DESCRIPTOR` 元素） | 引擎的首选张量布局。 | 只读 |

**定型返回值**

对此描述符调用 `acdnnBackendFinalize()` 时，可能返回以下状态码：

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：当前 acDNN 版本不支持该属性集；例如： `ACDNN_ATTR_ENGINE_GLOBAL_INDEX` 超出有效范围。
- `ACDNN_STATUS_BAD_PARAM`：属性集不一致或处于意外状态；例如：操作图描述符为 null、未初始化或包含冲突的属性。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.3.3. ACDNN_BACKEND_ENGINECFG_DESCRIPTOR {#533-acdnn_backend_enginecfg_descriptor}

通过以下方式创建：
```cpp
acdnnBackendCreateDescriptor(ACDNN_BACKEND_ENGINECFG_DESCRIPTOR, &desc);
```

acDNN 后端引擎配置描述符由一个引擎描述符和一个旋钮选项描述符数组组成。开发者可以从引擎配置中查询关于中间结果的信息：可以在执行之间重用的计算中间结果。

**属性**

| 属性名称 | 描述和约束 |
| :--- | :--- |
| `ACDNN_ATTR_ENGINECFG_ENGINE` | 后端引擎。<br>**类型** ： `ACDNN_TYPE_BACKEND_DESCRIPTOR`：一个元素，类型为 `ACDNN_BACKEND_ENGINE_DESCRIPTOR` 的后端描述符。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_ENGINECFG_KNOB_CHOICES` | 引擎调优旋钮和选项。<br>**类型** ： `ACDNN_TYPE_BACKEND_DESCRIPTOR`：零个或多个元素，类型为 `ACDNN_BACKEND_KNOB_CHOICE_DESCRIPTOR` 的后端描述符。 |
| `ACDNN_ATTR_ENGINECFG_INTERMEDIATE_INFO` | 此引擎配置的计算中间结果的信息。<br>**类型** ： `ACDNN_TYPE_BACKEND_DESCRIPTOR`：一个元素，类型为 `ACDNN_BACKEND_INTERMEDIATE_INFO_DESCRIPTOR` 的后端描述符。<br>**要求** ：只读属性。当前不受支持：为将来实现预留的占位符。 |

**定型**

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。
- `ACDNN_STATUS_NOT_SUPPORTED`：当前版本的 acDNN 不支持描述符属性集。例如：旋钮值无效。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.3.4. ACDNN_BACKEND_ENGINEHEUR_DESCRIPTOR {#534-acdnn_backend_engineheur_descriptor}

通过以下方式创建：
```cpp
acdnnBackendCreateDescriptor(ACDNN_BACKEND_ENGINEHEUR_DESCRIPTOR, &desc);
```

acDNN 后端引擎启发式描述符允许开发者获取操作图的引擎配置描述符，这些描述符根据 acDNN 的启发式按性能排名。

**属性**

| 属性名称 | 描述和约束 |
| :--- | :--- |
| `ACDNN_ATTR_ENGINEHEUR_OPERATION_GRAPH` | 查询启发式结果的操作图。<br>**类型** ： `ACDNN_TYPE_BACKEND_DESCRIPTOR`；一个元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_ENGINEHEUR_MODE` | 查询结果的启发式模式。<br>**类型** ： `ACDNN_TYPE_HEUR_MODE`；一个元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_ENGINEHEUR_RESULTS` | 启发式查询的结果。<br>**类型** ： `ACDNN_TYPE_BACKEND_DESCRIPTOR`；零个或多个 `ACDNN_BACKEND_ENGINECFG_DESCRIPTOR` 类型的描述符。<br>**要求** ：只获取属性。 |

**定型**

`acdnnBackendFinalize(desc)` 的返回值，其中 `desc` 是 acDNN 后端引擎启发式描述符：

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.3.5. ACDNN_BACKEND_EXECUTION_PLAN_DESCRIPTOR {#535-acdnn_backend_execution_plan_descriptor}

通过以下方式创建：
```cpp
acdnnBackendCreateDescriptor(ACDNN_BACKEND_EXECUTION_PLAN_DESCRIPTOR, &desc);
```

acDNN 后端执行计划描述符允许开发者指定执行计划，由 acDNN 句柄、引擎配置和可选的要计算的中间结果数组组成。

**属性**

| 属性名称 | 描述和约束 |
| :--- | :--- |
| `ACDNN_ATTR_EXECUTION_PLAN_HANDLE` | acDNN 句柄。<br>**类型** ： `ACDNN_TYPE_HANDLE`；一个元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_EXECUTION_PLAN_ENGINE_CONFIG` | 要执行的引擎配置。<br>**类型** ： `ACDNN_BACKEND_ENGINECFG_DESCRIPTOR`；一个元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_EXECUTION_PLAN_RUN_ONLY_INTERMEDIATE_UIDS` | 要计算的中间结果的唯一标识符。<br>**类型** ： `ACDNN_TYPE_INT64`；零个或多个元素。<br>**要求** ：可选属性。如果设置，执行计划将仅计算指定的中间结果，而不计算引擎配置中操作图的任何输出张量。 |
| `ACDNN_ATTR_EXECUTION_PLAN_COMPUTED_INTERMEDIATE_UIDS` | 预计算的中间结果的唯一标识符。<br>**类型** ： `ACDNN_TYPE_INT64`；零个或多个元素。<br>**要求** ：可选属性。如果设置，计划将在执行期间期望并使用变体包描述符中每个中间结果的指针。当前不受支持：为将来实现预留的占位符。 |
| `ACDNN_ATTR_EXECUTION_PLAN_WORKSPACE_SIZE` | 执行此计划所需的工作空间缓冲区大小。<br>**类型** ： `ACDNN_TYPE_INT64`；一个元素。<br>**要求** ：只读属性。 |

**定型**

`acdnnBackendFinalize(desc)` 的返回值，其中 `desc` 是 acDNN 后端执行计划描述符：

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.3.6. ACDNN_BACKEND_INTERMEDIATE_INFO_DESCRIPTOR {#536-acdnn_backend_intermediate_info_descriptor}

通过以下方式创建：
```cpp
acdnnBackendCreateDescriptor(ACDNN_BACKEND_INTERMEDIATE_INFO_DESCRIPTOR, &desc);
```

acDNN 后端中间结果描述符是只读描述符，包含关于执行中间结果的信息。执行中间结果是引擎配置在设备内存中的一些中间计算，可以在计划执行之间重用以分摊核函数开销。每个中间结果由唯一标识符标识。开发者可以查询中间结果的设备内存大小。中间结果可以依赖于由张量唯一标识符标识的一个或多个张量的数据，或者操作图的一个或多个属性。

这是只读描述符。开发者无法设置描述符属性或定型描述符。开发者从引擎配置描述符查询已定型的描述符。

**属性**

| 属性名称 | 描述和约束 |
| :--- | :--- |
| `ACDNN_ATTR_INTERMEDIATE_INFO_UNIQUE_ID` | 中间结果的唯一标识符。<br>**类型** ： `ACDNN_TYPE_INT64`；一个元素。<br>**要求** ：只读属性。 |
| `ACDNN_ATTR_INTERMEDIATE_INFO_SIZE` | 中间结果所需的设备内存大小。<br>**类型** ： `ACDNN_TYPE_INT64`；一个元素。<br>**要求** ：只读属性。 |
| `ACDNN_ATTR_INTERMEDIATE_INFO_DEPENDENT_DATA_UIDS` | 中间结果依赖的张量的唯一标识符。<br>**类型** ： `ACDNN_TYPE_INT64`；零个或多个元素。<br>**要求** ：只读属性。 |
| `ACDNN_ATTR_INTERMEDIATE_INFO_DEPENDENT_ATTRIBUTES` | 为将来实现预留的占位符。 |

**定型**

开发者不定型此描述符。使用后端中间结果描述符调用 `acdnnBackendFinalize(desc)` 返回 `ACDNN_STATUS_NOT_SUPPORTED`。

#### 5.3.7. ACDNN_BACKEND_KNOB_CHOICE_DESCRIPTOR {#537-acdnn_backend_knob_choice_descriptor}

通过以下方式创建：
```cpp
acdnnBackendCreateDescriptor(ACDNN_BACKEND_KNOB_CHOICE_DESCRIPTOR, &desc);
```

acDNN 后端旋钮选项描述符由要设置的旋钮的类型和旋钮设置的值组成。

**属性**

| 属性名称 | 描述和约束 |
| :--- | :--- |
| `ACDNN_ATTR_KNOB_CHOICE_KNOB_TYPE` | 要设置的旋钮的类型。<br>**类型** ： `ACDNN_TYPE_KNOB_TYPE`：一个元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_KNOB_CHOICE_KNOB_VALUE` | 旋钮的值。<br>**类型** ： `ACDNN_TYPE_INT64`：一个元素。<br>**要求** ：必需属性。 |

**定型**

`acdnnBackendFinalize(desc)` 的返回值，其中 `desc` 是 acDNN 后端旋钮选项描述符：

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.3.8. ACDNN_BACKEND_KNOB_INFO_DESCRIPTOR {#538-acdnn_backend_knob_info_descriptor}

通过以下方式创建：
```cpp
acdnnBackendCreateDescriptor(ACDNN_BACKEND_KNOB_INFO_DESCRIPTOR, &desc);
```

acDNN 后端旋钮信息描述符由引擎性能调优旋钮的类型和有效值范围组成。有效值范围以有效值的最小值、最大值和步幅给出，这是纯粹的信息性描述符类型。不支持设置描述符属性。开发者从已定型的后端描述符获取已定型的描述符数组，每个旋钮类型一个。

**属性**

| 属性名称 | 描述和约束 |
| :--- | :--- |
| `ACDNN_ATTR_KNOB_INFO_TYPE` | 性能调优旋钮的类型。<br>**类型** ： `ACDNN_TYPE_KNOB_TYPE`：一个元素。<br>**要求** ：只读属性。 |
| `ACDNN_ATTR_KNOB_INFO_MINIMUM_VALUE` | 此旋钮的最小有效选项值。<br>**类型** ： `ACDNN_TYPE_INT64`：一个元素。<br>**要求** ：只读属性。 |
| `ACDNN_ATTR_KNOB_INFO_MAXIMUM_VALUE` | 此旋钮的最大有效选项值。<br>**类型** ： `ACDNN_TYPE_INT64`：一个元素。<br>**要求** ：只读属性。 |
| `ACDNN_ATTR_KNOB_INFO_STRIDE` | 此旋钮的有效选项值的步幅。<br>**类型** ： `ACDNN_TYPE_INT64`：一个元素。<br>**要求** ：只读属性。 |

**定型**

此描述符是只读的；它从 acDNN 后端引擎配置描述符检索并定型。开发者无法设置或定型。

#### 5.3.9. ACDNN_BACKEND_LAYOUT_INFO_DESCRIPTOR {#539-acdnn_backend_layout_info_descriptor}

使用描述符类型值 `ACDNN_BACKEND_LAYOUT_INFO_DESCRIPTOR` 创建，acDNN 后端布局信息描述符提供张量的首选布局信息。

**属性**

| 属性名称 | 描述和约束 |
| :--- | :--- |
| `ACDNN_ATTR_LAYOUT_INFO_TENSOR_UID` | 张量的唯一标识符。<br>**类型** ： `ACDNN_TYPE_INT64`；一个元素。<br>**要求** ：只读属性。 |
| `ACDNN_ATTR_LAYOUT_INFO_TYPES` | 张量的首选布局。<br>**类型** ： `ACDNN_TYPE_LAYOUT_TYPE`：零个或多个 `acdnnBackendLayoutType_t` 元素。<br>**要求** ：只读属性。 |

**定型**

此描述符是只读的；它从 acDNN 后端引擎配置描述符检索并定型。开发者无法设置其属性或定型。

#### 5.3.10. ACDNN_BACKEND_MATMUL_DESCRIPTOR {#5310-acdnn_backend_matmul_descriptor}

通过以下方式创建：
```cpp
acdnnBackendCreateDescriptor(ACDNN_BACKEND_MATMUL_DESCRIPTOR, &desc);
```

acDNN 后端矩阵乘法描述符指定矩阵乘法操作所需的任何元数据。

**属性**

| 属性名称 | 描述和约束 |
| :--- | :--- |
| `ACDNN_ATTR_MATMUL_COMP_TYPE` | 用于矩阵乘法操作的计算精度。<br>**类型** ： `ACDNN_TYPE_DATA_TYPE`；一个元素。<br>**要求** ：必需属性。 |

**定型**

`acdnnBackendFinalize(desc)` 的返回值，其中 `desc` 是 acDNN 后端矩阵乘法描述符：

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.3.11. ACDNN_BACKEND_OPERATION_CONVOLUTION_BACKWARD_DATA_DESCRIPTOR {#5311-acdnn_backend_operation_convolution_backward_data_descriptor}

通过以下方式创建：
```cpp
acdnnBackendCreateDescriptor(ACDNN_BACKEND_OPERATION_CONVOLUTION_BACKWARD_DATA_DESCRIPTOR, &desc);
```

acDNN 后端卷积反向数据操作描述符指定用于卷积反向数据的操作节点，以使用滤波器张量和响应梯度来计算输入数据的梯度，输出带有 $\alpha$ 缩放并进行 $\beta$ 缩放的残差加法。即方程 $dx = \alpha(w \star^{-} dy) + \beta dx$，其中 $\star^{-}$ 表示卷积反向数据算子。

**属性**

acDNN 后端卷积反向数据操作描述符的属性是枚举类型 `acdnnBackendAttributeName_t` 的值，前缀为 `ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_DATA`：

| 属性名称 | 描述 | 类型 | 要求 |
| :--- | :--- | :--- | :--- |
| `ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_DATA_ALPHA` | Alpha 值。 | `ACDNN_TYPE_FLOAT` 或 `ACDNN_TYPE_DOUBLE`（≥1 个元素） | 必需 |
| `ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_DATA_BETA` | Beta 值。 | `ACDNN_TYPE_FLOAT` 或 `ACDNN_TYPE_DOUBLE`（≥1 个元素） | 必需 |
| `ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_DATA_CONV_DESC` | 卷积算子描述符。 | `ACDNN_TYPE_BACKEND_DESCRIPTOR`（1 个 `ACDNN_BACKEND_CONVOLUTION_DESCRIPTOR` 元素） | 必需 |
| `ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_DATA_W` | 卷积滤波器张量描述符。 | `ACDNN_TYPE_BACKEND_DESCRIPTOR`（1 个 `ACDNN_BACKEND_TENSOR_DESCRIPTOR` 元素） | 必需 |
| `ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_DATA_DX` | 图像梯度张量描述符。 | `ACDNN_TYPE_BACKEND_DESCRIPTOR`（1 个 `ACDNN_BACKEND_TENSOR_DESCRIPTOR` 元素） | 必需 |
| `ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_DATA_DY` | 响应梯度张量描述符。 | `ACDNN_TYPE_BACKEND_DESCRIPTOR`（1 个 `ACDNN_BACKEND_TENSOR_DESCRIPTOR` 元素） | 必需 |

**定型**

在定型卷积操作时，张量 DX、W 和 DY 的张量维度基于与 `ACDNN_BACKEND_OPERATION_CONVOLUTION_FORWARD_DESCRIPTOR` 部分中描述的 X、W 和 Y 张量维度相同的解释进行绑定。

使用 `ACDNN_BACKEND_OPERATION_CONVOLUTION_BACKWARD_DATA_DESCRIPTOR` 调用 `acdnnBackendFinalize()` 可能返回以下值：

返回码：

- `ACDNN_STATUS_BAD_PARAM`：遇到无效或不一致的属性值。可能的原因：在卷积算子下，DX、W 和 DY 张量不构成有效的卷积运算。
- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.3.12. ACDNN_BACKEND_OPERATION_CONVOLUTION_BACKWARD_FILTER_DESCRIPTOR {#5312-acdnn_backend_operation_convolution_backward_filter_descriptor}

通过以下方式创建：
```cpp
acdnnBackendCreateDescriptor(ACDNN_BACKEND_OPERATION_CONVOLUTION_BACKWARD_FILTER_DESCRIPTOR, &desc);
```

acDNN 后端卷积反向滤波器操作描述符指定用于卷积反向滤波器的操作节点，以使用图像张量和响应梯度来计算滤波器的梯度，输出带有 $\alpha$ 缩放并进行 $\beta$ 缩放的残差加法。即方程：$dw = \alpha(x^{\star\sim} dy) + \beta dw$，其中 $\star^{\sim}$ 表示卷积反向滤波器算子。

**属性**

acDNN 后端卷积反向滤波器操作描述符的属性是枚举类型 `acdnnBackendAttributeName_t` 的值，前缀为 `ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_FILTER_`：

| 属性名称 | 描述 | 类型 | 要求 |
| :--- | :--- | :--- | :--- |
| `ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_FILTER_ALPHA` | Alpha 值。 | `ACDNN_TYPE_FLOAT` 或 `ACDNN_TYPE_DOUBLE`（≥1 个元素） | 必需。必须在定型之前设置。 |
| `ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_FILTER_BETA` | Beta 值。 | `ACDNN_TYPE_FLOAT` 或 `ACDNN_TYPE_DOUBLE`（≥1 个元素） | 必需。必须在定型之前设置。 |
| `ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_FILTER_CONV_DESC` | 卷积算子描述符。 | `ACDNN_TYPE_BACKEND_DESCRIPTOR`（1 个 `ACDNN_BACKEND_CONVOLUTION_DESCRIPTOR` 元素） | 必需。必须在定型之前设置。 |
| `ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_FILTER_DW` | 卷积滤波器张量描述符。 | `ACDNN_TYPE_BACKEND_DESCRIPTOR`（1 个 `ACDNN_BACKEND_TENSOR_DESCRIPTOR` 元素） | 必需。必须在定型之前设置。 |
| `ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_FILTER_X` | 图像梯度张量描述符。 | `ACDNN_TYPE_BACKEND_DESCRIPTOR`（1 个 `ACDNN_BACKEND_TENSOR_DESCRIPTOR` 元素） | 必需。必须在定型之前设置。 |
| `ACDNN_ATTR_OPERATION_CONVOLUTION_BWD_FILTER_DY` | 响应梯度张量描述符。 | `ACDNN_TYPE_BACKEND_DESCRIPTOR`（1 个 `ACDNN_BACKEND_TENSOR_DESCRIPTOR` 元素） | 必需。必须在定型之前设置。 |

**定型**

在定型卷积操作时，张量 X、DW 和 DY 的张量维度基于与 `ACDNN_BACKEND_OPERATION_CONVOLUTION_FORWARD_DESCRIPTOR` 部分中描述的 X、W 和 Y 张量维度相同的解释进行绑定。

使用 `ACDNN_BACKEND_OPERATION_CONVOLUTION_BACKWARD_FILTER_DESCRIPTOR` 调用 `acdnnBackendFinalize()` 可能返回以下值：

返回码：

- `ACDNN_STATUS_BAD_PARAM`：遇到无效或不一致的属性值。可能的原因：在卷积算子下，X、DW 和 DY 张量不构成有效的卷积运算。
- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.3.13. ACDNN_BACKEND_OPERATION_CONVOLUTION_FORWARD_DESCRIPTOR {#5313-acdnn_backend_operation_convolution_forward_descriptor}

通过以下方式创建：
```cpp
acdnnBackendCreateDescriptor(ACDNN_BACKEND_OPERATION_CONVOLUTION_FORWARD_DESCRIPTOR, &desc);
```

acDNN 后端卷积前向操作描述符指定用于前向卷积的操作节点，以计算图像张量与滤波器张量卷积的响应张量，输出带有 $\alpha$ 缩放并进行 $\beta$ 缩放的残差加法。即方程 $y = \alpha(w \star x) + \beta y$，其中 $\star$ 是前向方向的卷积算子。

**属性**

acDNN 后端卷积前向操作描述符的属性是枚举类型 `acdnnBackendAttributeName_t` 的值，前缀为 `ACDNN_ATTR_OPERATION_CONVOLUTION_FORWARD_`：

| 属性名称 | 描述 | 类型 | 要求 |
| :--- | :--- | :--- | :--- |
| `ACDNN_ATTR_OPERATION_CONVOLUTION_FORWARD_ALPHA` | Alpha 值。 | `ACDNN_TYPE_FLOAT` 或 `ACDNN_TYPE_DOUBLE`（≥1 个元素） | 必需。必须在定型之前设置。 |
| `ACDNN_ATTR_OPERATION_CONVOLUTION_FORWARD_BETA` | Beta 值。 | `ACDNN_TYPE_FLOAT` 或 `ACDNN_TYPE_DOUBLE`（≥1 个元素） | 必需。必须在定型之前设置。 |
| `ACDNN_ATTR_OPERATION_CONVOLUTION_FORWARD_CONV_DESC` | 卷积算子描述符。 | `ACDNN_TYPE_BACKEND_DESCRIPTOR`（1 个 `ACDNN_BACKEND_CONVOLUTION_DESCRIPTOR` 元素） | 必需。必须在定型之前设置。 |
| `ACDNN_ATTR_OPERATION_CONVOLUTION_FORWARD_W` | 卷积滤波器张量描述符。 | `ACDNN_TYPE_BACKEND_DESCRIPTOR`（1 个 `ACDNN_BACKEND_TENSOR_DESCRIPTOR` 元素） | 必需。必须在定型之前设置。 |
| `ACDNN_ATTR_OPERATION_CONVOLUTION_FORWARD_X` | 输入张量描述符。 | `ACDNN_TYPE_BACKEND_DESCRIPTOR`（1 个 `ACDNN_BACKEND_TENSOR_DESCRIPTOR` 元素） | 必需。必须在定型之前设置。 |
| `ACDNN_ATTR_OPERATION_CONVOLUTION_FORWARD_Y` | 输出张量描述符。 | `ACDNN_TYPE_BACKEND_DESCRIPTOR`（1 个 `ACDNN_BACKEND_TENSOR_DESCRIPTOR` 元素） | 必需。必须在定型之前设置。 |

**定型**

在定型卷积操作时，张量 X、W 和 Y 的张量维度基于以下解释进行绑定：

`ACDNN_ATTR_OPERATION_CONVOLUTION_FORWARD_CONV_DESC` 的 `ACDNN_ATTR_CONVOLUTION_SPATIAL_DIMS` 属性是卷积的空间维度数量。张量 X、W 和 Y 的维度数量必须比空间维度数量大 2 或 3，具体取决于开发者选择如何指定卷积张量。

如果张量维度数量是空间维度数量加 2：
- X 张量维度和步幅数组为 `[N, GC, ...]`
- W 张量维度和步幅数组为 `[KG, C, ...]`
- Y 张量维度和步幅数组为 `[N, GK, ...]`

其中省略号 `...` 是每个张量的空间维度的简写，G 是卷积组的数量，C 和 K 是每个组的输入和输出特征图数量。在此解释中，假设每个组的内存布局是紧凑排列的。 `acdnnBackendFinalize()` 断言张量维度和步幅与此解释一致，否则返回 `ACDNN_STATUS_BAD_PARAM`。

如果张量维度数量是空间维度数量加 3：
- X 张量维度和步幅数组为 `[N, G, C, ...]`
- W 张量维度和步幅数组为 `[G, K, C, ...]`
- Y 张量维度和步幅数组为 `[N, G, K, ...]`

其中省略号 `...` 是每个张量的空间维度的简写，G 是卷积组的数量，C 和 K 是每个组的输入和输出特征图数量。在此解释中，开发者可以指定非紧凑的组步幅。 `acdnnBackendFinalize()` 断言张量维度和步幅与此解释一致，否则返回 `ACDNN_STATUS_BAD_PARAM`。

使用 `ACDNN_BACKEND_OPERATION_CONVOLUTION_FORWARD_DESCRIPTOR` 调用 `acdnnBackendFinalize()` 可能返回以下值：

返回码：

- `ACDNN_STATUS_BAD_PARAM`：遇到无效或不一致的属性值。可能的原因：在卷积算子下，X、W 和 Y 张量不构成有效的卷积运算。
- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.3.14. ACDNN_BACKEND_OPERATION_GEN_STATS_DESCRIPTOR {#5314-acdnn_backend_operation_gen_stats_descriptor}

表示将生成逐通道统计量的操作。将生成的具体统计量取决于描述符中的 `ACDNN_ATTR_OPERATION_GENSTATS_MODE` 属性。目前， `ACDNN_ATTR_OPERATION_GENSTATS_MODE` 仅支持 `ACDNN_GENSTATS_SUM_SQSUM`。它将生成输入张量 X 的逐通道元素的和与平方和。输出维度应除 C 维度外全为 1。此外，输出的 C 维度应等于输入的 C 维度。此不透明结构体可以通过 `acdnnBackendCreateDescriptor(ACDNN_BACKEND_OPERATION_GEN_STATS_DESCRIPTOR)` 创建。

**属性**

| 属性名称 | 描述 |
| :--- | :--- |
| `ACDNN_ATTR_OPERATION_GENSTATS_MODE` | 设置操作的 `ACDNN_TYPE_GENSTATS_MODE`。此属性是必需的。 |
| `ACDNN_ATTR_OPERATION_GENSTATS_MATH_PREC` | 计算的数学精度，此属性是必需的。 |
| `ACDNN_ATTR_OPERATION_GENSTATS_XDESC` | 设置输入张量 X 的描述符，此属性是必需的。 |
| `ACDNN_ATTR_OPERATION_GENSTATS_SUMDESC` | 设置输出张量 Sum 的描述符，此属性是必需的。 |
| `ACDNN_ATTR_OPERATION_GENSTATS_SQSUMDESC` | 设置输出张量 Quadratic Sum 的描述符，此属性是必需的。 |

**定型**

在定型阶段，交叉检查属性以确保没有冲突。可能返回以下状态：

返回码：

- `ACDNN_STATUS_BAD_PARAM`：遇到无效或不一致的属性值。可能的原因包括：输入和输出张量之间的维度数量不匹配；输入/输出张量维度与上述描述不一致。
- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.3.15. ACDNN_BACKEND_OPERATION_MATMUL_DESCRIPTOR {#5315-acdnn_backend_operation_matmul_descriptor}

通过以下方式创建：
```cpp
acdnnBackendCreateDescriptor(ACDNN_BACKEND_OPERATION_MATMUL_DESCRIPTOR, &desc);
```

acDNN 后端矩阵乘法操作描述符指定用于矩阵乘法的操作节点，通过将矩阵 A 和矩阵 B 相乘来计算矩阵乘积 C，如以下方程所示：$C = AB$

使用矩阵乘法操作时，矩阵预期至少是秩-2 张量。最后两个维度预期对应于 M、K 或 N。所有前面的维度都被解释为批次维度。如果有零个批次维度，则要求如下：

**零批次维度的 `ACDNN_BACKEND_OPERATION_MATMUL_DESCRIPTOR`**

| 情况 | Matrix A | Matrix B | Matrix C |
| :--- | :--- | :--- | :--- |
| 单次矩阵乘法 | M x K | K x N | M x N |

**单个批次维度的 `ACDNN_BACKEND_OPERATION_MATMUL_DESCRIPTOR`**

| 情况 | Matrix A | Matrix B | Matrix C |
| :--- | :--- | :--- | :--- |
| 单次矩阵乘法 | 1 x M x K | 1 x K x N | 1 x M x N |
| 批次矩阵乘法 | B x M x K | B x K x N | B x M x N |
| 广播 A | 1 x M x K | B x K x N | B x M x N |
| 广播 B | B x M x K | 1 x K x N | B x M x N |

- B 表示批次大小。
- M 是矩阵 A 的行数。
- K 是输入矩阵 A 的列数（与输入矩阵 B 的行数相同）
- N 是输入矩阵 B 的列数。

如果矩阵 A 或 B 的批次大小设置为 1，则表示该矩阵将在批次矩阵乘法中进行广播。生成的输出矩阵 C 将是 B x M x N 的张量。

上述广播约定扩展到所有批次维度。具体来说，对于具有三个批次维度的张量：

**三个批次维度的 `ACDNN_BACKEND_OPERATION_MATMUL_DESCRIPTOR`**

| 情况 | Matrix A | Matrix B | Matrix C |
| :--- | :--- | :--- | :--- |
| 多次批次矩阵乘法 | B1 x 1 x B3 x M x K | 1 x B2 x B3 x K x N | B1 x B2 x B3 x M x N |

具有多个批次维度的功能允许开发者拥有批次不以单个步幅紧凑排列的布局。这种情况特别在多头注意力（Multi-head Attention）中见到。

可以使用张量描述符中的步幅指定给定张量的矩阵元素的寻址。步幅表示每个张量维度的元素之间的间距。考虑具有步幅 `[BS, MS, NS]` 的矩阵张量 A $(B \times M \times N)$，它表示实际的矩阵元素 A[x, y, z] 在为张量 A 分配的线性内存空间中的位置为 (A_base_address + x * BS + y * MS + z * NS)。根据当前的支持，最内层的维度必须是紧凑排列的，这要求 MS = 1 或 NS = 1。否则，关于如何在张量描述符中指定步幅没有其他技术约束，因为它应遵循上述寻址公式和用户指定的步幅。

此表示法提供了一些常见用法的支持，例如前导维度和矩阵转置，以下示例将对此进行说明。

1. 最基本的情况是完全紧凑排列的行主序批次矩阵，不考虑前导维度或转置。在这种情况下，BS = M * N，MS = N，NS = 1。

2. 可以通过使用步幅交换内部和外部维度来实现矩阵转置。即：

   a) 指定非转置矩阵：BS = M * N，MS = N，NS = 1
   b) 指定矩阵转置：BS = M * N，MS = 1，NS = M

3. 前导维度是类 BLAS 接口中广泛使用的概念，描述 2D 数组内存分配的内部维度（与概念上的矩阵维度相对）。其在一定程度上类似于步幅，因为它定义了外部维度中元素之间的间距。它与矩阵内部维度显示出差异的最典型用例是：矩阵只是分配的内存中的部分数据、寻址子矩阵或从对齐内存分配寻址矩阵。因此，列主序矩阵 A 中的前导维度 LDA 必须满足 LDA >= M，而在行主序矩阵 A 中，必须满足 LDA >= N。要从前导维度概念过渡到使用步幅，这意味着 MS >= N 且 NS = 1，或 MS = 1 且 NS >= M。请记住，虽然这些是一些实际用例，但这些不等式不会对步幅的可接受规范施加技术约束。

其他常用的 GEMM 功能（例如 Alpha/Beta 输出混合）也可以结合此矩阵乘法操作和其他逐点运算来实现。

**属性**

acDNN 后端矩阵乘法描述符的属性是枚举类型 `acdnnBackendAttributeName_t` 的值，前缀为 `ACDNN_ATTR_OPERATION_MATMUL_`：

| 属性名称 | 描述 |
| :--- | :--- |
| `ACDNN_ATTR_OPERATION_MATMUL_ADESC` | 矩阵 A 描述符。<br>**类型** ： `ACDNN_TYPE_BACKEND_DESCRIPTOR`；一个 `ACDNN_BACKEND_TENSOR_DESCRIPTOR` 类型的描述符元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_OPERATION_MATMUL_BDESC` | 矩阵 B 描述符。<br>**类型** ： `ACDNN_TYPE_BACKEND_DESCRIPTOR`；一个 `ACDNN_BACKEND_TENSOR_DESCRIPTOR` 类型的描述符元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_OPERATION_MATMUL_CDESC` | 矩阵 C 描述符。<br>**类型** ： `ACDNN_TYPE_BACKEND_DESCRIPTOR`；一个 `ACDNN_BACKEND_TENSOR_DESCRIPTOR` 类型的描述符元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_OPERATION_MATMUL_IRREGULARLY_STRIDED_BATCH_COUNT` | 要在批次中对矩阵执行的矩阵乘法操作数量。默认值 = 1<br>**类型** ： `ACDNN_TYPE_INT64`；一个元素。默认值为 1。 |
| `ACDNN_ATTR_OPERATION_MATMUL_DESC` | 矩阵乘法操作描述符。<br>**类型** ： `ACDNN_TYPE_BACKEND_DESCRIPTOR`；一个 `ACDNN_BACKEND_MATMUL_DESCRIPTOR` 类型的描述符元素。<br>**要求** ：必需属性。 |

**定型**

在矩阵乘法操作的定型中，将检查矩阵 A、B 和 C 的张量维度，以确保它们满足矩阵乘法的要求：

使用 `ACDNN_BACKEND_OPERATION_MATMUL_DESCRIPTOR` 调用 `acdnnBackendFinalize()` 可能返回以下值：

返回码：

- `ACDNN_STATUS_NOT_SUPPORTED`：遇到不受支持的属性值。可能的原因：矩阵 A、B 和 C 并非全部至少是秩-2 张量。
- `ACDNN_STATUS_BAD_PARAM`：遇到无效或不一致的属性值。可能的原因： `ACDNN_ATTR_OPERATION_MATMUL_IRREGULARLY_STRIDED_BATCH_COUNT` 与张量维度不一致。
- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.3.16. ACDNN_BACKEND_OPERATION_POINTWISE_DESCRIPTOR {#5316-acdnn_backend_operation_pointwise_descriptor}

表示实现方程 $Y = op(alpha1 \times X)$ 的逐点运算，具体取决于操作类型。上面 op() 表示的实际操作类型取决于描述符中的 `ACDNN_ATTR_OPERATION_POINTWISE_PW_DESCRIPTOR` 属性，此操作描述符支持单输入单输出的运算。

有关受支持的运算列表，请参阅 `acdnnPointwiseMode_t` 部分。

对于双输入逐点运算，当一个张量的某个张量维度为 1 而另一个张量的对应维度不为 1 时，假定进行广播。
对于三输入单输出逐点运算，不支持任何张量的广播。
此不透明结构体可以通过 `acdnnBackendCreateDescriptor(ACDNN_BACKEND_OPERATION_POINTWISE_DESCRIPTOR)` 创建。

**属性**

| 属性名称 | 描述 |
| :--- | :--- |
| `ACDNN_ATTR_OPERATION_POINTWISE_PW_DESCRIPTOR` | 设置包含逐点运算的数学设置的描述符，此属性是必需的。 |
| `ACDNN_ATTR_OPERATION_POINTWISE_XDESC` | 设置输入张量的描述符，此属性对于逐点数学函数或激活前向传播计算是必需的。 |
| `ACDNN_ATTR_OPERATION_POINTWISE_BDESC` | 如果操作需要 2 个输入（如加法或乘法），则此属性设置第二个输入张量 $\beta$。如果操作仅需要 1 个输入，则不使用此字段，不应设置。 |
| `ACDNN_ATTR_OPERATION_POINTWISE_YDESC` | 设置输出张量的描述符，此属性对于逐点数学函数或激活前向传播计算是必需的。 |
| `ACDNN_ATTR_OPERATION_POINTWISE_TDESC` | 设置张量 T 的描述符。当逐点运算需要第三个输入张量时使用此属性，充当掩码或辅助输入。 |
| `ACDNN_ATTR_OPERATION_POINTWISE_ALPHA1` | 设置方程中的标量值。可以是浮点或半精度，此属性是可选的，如果未设置，默认值为 1.0。当前版本仅支持默认值 1.0。 |
| `ACDNN_ATTR_OPERATION_POINTWISE_ALPHA2` | 如果操作需要两个输入（如加法或乘法），则此属性设置方程中的标量值。可以是浮点或半精度，此属性是可选的，如果未设置，默认值为 1.0。如果操作仅需要 1 个输入，则不使用此字段，不应设置。当前版本仅支持默认值 1.0。 |
| `ACDNN_ATTR_OPERATION_POINTWISE_DXDESC` | 设置输出张量的描述符，此属性对于逐点激活反向传播计算是必需的。 |
| `ACDNN_ATTR_OPERATION_POINTWISE_DYDESC` | 设置输入张量的描述符，此属性对于逐点激活反向传播计算是必需的。 |

**定型**

在定型阶段，交叉检查属性以确保没有冲突。可能返回以下状态：

返回码：

- `ACDNN_STATUS_BAD_PARAM`：遇到无效或不一致的属性值。可能的原因包括：输入和输出张量之间的维度数量不匹配；输入/输出张量的数据类型不兼容。
- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.3.17. ACDNN_BACKEND_OPERATION_REDUCTION_DESCRIPTOR {#5317-acdnn_backend_operation_reduction_descriptor}

acDNN 后端归约操作描述符表示一个操作节点，该节点实现在一个或多个维度中归约输入张量 X 的值以获取输出张量 Y。用于归约张量值的数学运算和计算数据类型通过 `ACDNN_ATTR_OPERATION_REDUCTION_DESC` 指定。

此操作描述符可以通过以下方式创建：

```cpp
acdnnBackendCreateDescriptor(ACDNN_BACKEND_OPERATION_REDUCTION_DESCRIPTOR, &desc);
```

输出张量 Y 的大小应与输入张量 X 相同，除非其大小为 1 的维度。

**属性**

acDNN 后端归约描述符的属性是枚举类型 `acdnnBackendAttributeName_t` 的值，前缀为 `ACDNN_ATTR_OPERATION_REDUCTION_`：

| 属性名称 | 描述 |
| :--- | :--- |
| `ACDNN_ATTR_OPERATION_REDUCTION_XDESC` | 矩阵 X 描述符。<br>**类型** ： `ACDNN_TYPE_BACKEND_DESCRIPTOR`，一个 `ACDNN_BACKEND_TENSOR_DESCRIPTOR` 类型的描述符元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_OPERATION_REDUCTION_YDESC` | 矩阵 Y 描述符。<br>**类型** ： `ACDNN_TYPE_BACKEND_DESCRIPTOR`，一个 `ACDNN_BACKEND_TENSOR_DESCRIPTOR` 类型的描述符元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_OPERATION_REDUCTION_DESC` | 归约操作描述符。<br>**类型** ： `ACDNN_TYPE_BACKEND_DESCRIPTOR`，一个 `ACDNN_BACKEND_REDUCTION_DESCRIPTOR` 类型的描述符元素。<br>**要求** ：必需属性。 |

**定型**

在归约操作的定型中，检查张量 X 和 Y 的维度，以确保它们满足归约操作的要求。

使用 `ACDNN_BACKEND_OPERATION_REDUCTION_DESCRIPTOR` 调用 `acdnnBackendFinalize()` 可能返回以下值：

返回码：

- `ACDNN_STATUS_BAD_PARAM`：遇到无效或不一致的属性值。可能的原因：张量 X 和 Y 的维度不满足归约操作的要求。
- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.3.18. ACDNN_BACKEND_OPERATION_RESAMPLE_BWD_DESCRIPTOR {#5318-acdnn_backend_operation_resample_bwd_descriptor}

通过以下方式创建：
```cpp
acdnnBackendCreateDescriptor(ACDNN_BACKEND_OPERATION_RESAMPLE_BWD_DESCRIPTOR, &desc);
```

acDNN 后端重采样反向操作描述符指定用于反向重采样的操作节点。它从输出张量梯度计算输入张量梯度，反向重采样根据 `ACDNN_ATTR_RESAMPLE_MODE` 进行，输出带有 $\alpha$ 缩放并进行 $\beta$ 缩放的残差加法。

**属性**

| 属性名称 | 描述 |
| :--- | :--- |
| `ACDNN_ATTR_OPERATION_RESAMPLE_BWD_DESC` | 重采样操作描述符（`ACDNN_BACKEND_RESAMPLE_DESCRIPTOR`）实例，包含有关操作的元数据。<br>**类型** ： `ACDNN_TYPE_BACKEND_DESCRIPTOR`；一个 `ACDNN_BACKEND_RESAMPLE_DESCRIPTOR` 类型的描述符元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_OPERATION_RESAMPLE_BWD_DXDESC` | 输入张量梯度描述符。<br>**类型** ： `ACDNN_TYPE_BACKEND_DESCRIPTOR`；一个 `ACDNN_BACKEND_TENSOR_DESCRIPTOR` 类型的描述符元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_OPERATION_RESAMPLE_BWD_DYDESC` | 输出张量梯度描述符。<br>**类型** ： `ACDNN_TYPE_BACKEND_DESCRIPTOR`；一个 `ACDNN_BACKEND_TENSOR_DESCRIPTOR` 类型的描述符元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_OPERATION_RESAMPLE_BWD_IDXDESC` | 包含要在反向传播中使用的最大池化或最近邻重采样索引的张量。<br>**类型** ： `ACDNN_TYPE_BACKEND_DESCRIPTOR`；一个 `ACDNN_BACKEND_TENSOR_DESCRIPTOR` 类型的描述符元素。<br>**要求** ：可选属性。 |
| `ACDNN_ATTR_OPERATION_RESAMPLE_BWD_ALPHA` | 设置用于混合的 Alpha 参数。<br>**类型** ： `ACDNN_TYPE_DOUBLE` 或 `ACDNN_TYPE_FLOAT`；一个元素。<br>**要求** ：可选属性。默认值为 1.0。 |
| `ACDNN_ATTR_OPERATION_RESAMPLE_BWD_BETA` | 设置用于混合的 Beta 参数。<br>**类型** ： `ACDNN_TYPE_DOUBLE` 或 `ACDNN_TYPE_FLOAT`；一个元素。<br>**要求** ：可选属性。默认值为 0.0。 |
| `ACDNN_ATTR_OPERATION_RESAMPLE_BWD_XDESC` | 输入张量 X 描述符。<br>**类型** ： `ACDNN_TYPE_BACKEND_DESCRIPTOR`；一个 `ACDNN_BACKEND_TENSOR_DESCRIPTOR` 类型的描述符元素。<br>**要求** ：可选属性。 `NCHW` 布局必需。 |
| `ACDNN_ATTR_OPERATION_RESAMPLE_BWD_YDESC` | 输入张量 Y 描述符。<br>**类型** ： `ACDNN_TYPE_BACKEND_DESCRIPTOR`；一个 `ACDNN_BACKEND_TENSOR_DESCRIPTOR` 类型的描述符元素。<br>**要求** ：可选属性。 `NCHW` 布局必需。 |

**定型**

在定型阶段，交叉检查属性以确保没有冲突。可能返回以下状态：

返回码：

- `ACDNN_STATUS_BAD_PARAM`：遇到无效或不一致的属性值。可能的原因包括：基于填充和步幅计算的输出形状与给定的输出张量维度不匹配。
- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.3.19. ACDNN_BACKEND_OPERATION_RESAMPLE_FWD_DESCRIPTOR {#5319-acdnn_backend_operation_resample_fwd_descriptor}

通过以下方式创建：
```cpp
acdnnBackendCreateDescriptor(ACDNN_BACKEND_OPERATION_RESAMPLE_FWD_DESCRIPTOR, &desc);
```

acDNN 后端重采样前向操作描述符指定用于前向重采样的操作节点。它根据 `ACDNN_ATTR_RESAMPLE_MODE` 对图像张量进行重采样计算输出张量，输出带有 $\alpha$ 缩放并进行 $\beta$ 缩放的残差加法。

重采样模式在每个空间维度上独立运行。对于空间维度 $i$，可以通过组合输入图像的空间维度大小 $x_i$、后填充 $post_i$、前填充 $pre_i$、步幅 $s_i$、窗口大小 $w_i$ 来计算输出空间维度大小 $y_i$：

$$y_i = \lfloor (x_i + post_i + pre_i - w_i) / s_i \rfloor + 1$$

**属性**

| 属性名称 | 描述 |
| :--- | :--- |
| `ACDNN_ATTR_OPERATION_RESAMPLE_FWD_DESC` | 重采样操作描述符（`ACDNN_BACKEND_RESAMPLE_DESCRIPTOR`）实例，包含有关操作的元数据。<br>**类型** ： `ACDNN_TYPE_BACKEND_DESCRIPTOR`；一个 `ACDNN_BACKEND_RESAMPLE_DESCRIPTOR` 类型的描述符元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_OPERATION_RESAMPLE_FWD_XDESC` | 输入张量描述符。<br>**类型** ： `ACDNN_TYPE_BACKEND_DESCRIPTOR`；一个 `ACDNN_BACKEND_TENSOR_DESCRIPTOR` 类型的描述符元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_OPERATION_RESAMPLE_FWD_YDESC` | 输出张量描述符。<br>**类型** ： `ACDNN_TYPE_BACKEND_DESCRIPTOR`；一个 `ACDNN_BACKEND_TENSOR_DESCRIPTOR` 类型的描述符元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_OPERATION_RESAMPLE_FWD_IDXDESC` | 包含要在反向传播中使用的最大池化或最近邻重采样索引的张量。<br>**类型** ： `ACDNN_TYPE_BACKEND_DESCRIPTOR`；一个 `ACDNN_BACKEND_TENSOR_DESCRIPTOR` 类型的描述符元素。<br>**要求** ：可选属性（主要用于涉及训练的用例）。 |
| `ACDNN_ATTR_OPERATION_RESAMPLE_FWD_ALPHA` | 设置用于混合的 Alpha 参数。<br>**类型** ： `ACDNN_TYPE_DOUBLE` 或 `ACDNN_TYPE_FLOAT`；一个元素。<br>**要求** ：可选属性。默认值为 1.0。 |
| `ACDNN_ATTR_OPERATION_RESAMPLE_FWD_BETA` | 设置用于混合的 Beta 参数。<br>**类型** ： `ACDNN_TYPE_DOUBLE` 或 `ACDNN_TYPE_FLOAT`；一个元素。<br>**要求** ：可选属性。默认值为 0.0。 |

**定型**

在定型阶段，交叉检查属性以确保没有冲突。可能返回以下状态：

返回码：

- `ACDNN_STATUS_BAD_PARAM`：遇到无效或不一致的属性值。可能的原因包括：基于填充和步幅计算的输出形状与给定的输出张量维度不匹配。
- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.3.20. ACDNN_BACKEND_OPERATIONGRAPH_DESCRIPTOR {#5320-acdnn_backend_operationgraph_descriptor}

使用描述符类型值 `ACDNN_BACKEND_OPERATIONGRAPH_DESCRIPTOR` 创建，acDNN 后端操作图描述符描述一个操作图，一个由一个或多个通过虚拟张量连接的操作组成的小型网络。操作图定义开发者希望计算的计算用例或数学表达式。

**属性**

acDNN 后端操作图描述符的属性是枚举类型 `acdnnBackendAttributeName_t` 的值，前缀为 `ACDNN_ATTR_OPERATIONGRAPH_`：

| 属性名称 | 描述 |
| :--- | :--- |
| `ACDNN_ATTR_OPERATIONGRAPH_HANDLE` | acDNN 句柄。<br>**类型** ： `ACDNN_TYPE_HANDLE`；一个元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_OPERATIONGRAPH_OPS` | 形成操作图的操作节点。<br>**类型** ： `ACDNN_TYPE_BACKEND_DESCRIPTOR`；一个或多个 `ACDNN_BACKEND_OPERATION_*_DESCRIPTOR` 类型的描述符元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_OPERATIONGRAPH_ENGINE_GLOBAL_COUNT` | 支持操作图的引擎数量。<br>**类型** ： `ACDNN_TYPE_INT64`；一个元素。<br>**要求** ：只读属性。 |

**定型**

返回码：

- `ACDNN_STATUS_BAD_PARAM`：遇到无效的属性值。例如： `ACDNN_ATTR_OPERATIONGRAPH_OPS` 中的一个后端描述符未定型； `ACDNN_ATTR_OPERATIONGRAPH_HANDLE` 的值不是有效的 acDNN 句柄。
- `ACDNN_STATUS_NOT_SUPPORTED`：遇到不受支持的属性值。例如： `ACDNN_ATTR_OPERATIONGRAPH_OPS` 属性的操作组合不受支持。
- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.3.21. ACDNN_BACKEND_POINTWISE_DESCRIPTOR {#5321-acdnn_backend_pointwise_descriptor}

通过以下方式创建：
```cpp
acdnnBackendCreateDescriptor(ACDNN_BACKEND_POINTWISE_DESCRIPTOR, &desc);
```

acDNN 后端逐点运算描述符指定逐点运算算子的参数，如模式、数学精度、NaN 传播等。

**属性**

acDNN 后端逐点运算描述符的属性是枚举类型 `acdnnBackendAttributeName_t` 的值，前缀为 `ACDNN_ATTR_POINTWISE_`：

| 属性名称 | 描述 |
| :--- | :--- |
| `ACDNN_ATTR_POINTWISE_MODE` | 逐点运算的模式。<br>**类型** ： `ACDNN_TYPE_POINTWISE_MODE`；一个元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_POINTWISE_MATH_PREC` | 计算的数学精度。<br>**类型** ： `ACDNN_TYPE_DATA_TYPE`；一个元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_POINTWISE_NAN_PROPAGATION` | 指定传播 NaN 的方法。仅适用于基于比较的逐点模式（如 ReLU）。当前支持仅包括枚举值 `ACDNN_PROPAGATE_NAN`。默认值： `ACDNN_NOT_PROPAGATE_NAN`。<br>**类型** ： `ACDNN_TYPE_NAN_PROPOGATION`；一个元素。 |
| `ACDNN_ATTR_POINTWISE_RELU_LOWER_CLIP` | 设置 ReLU 的下裁剪值。如果 `value < lower_clip`，则 `value = lower_clip + lower_clip_slope * (value - lower_clip)`。<br>**类型** ： `ACDNN_TYPE_DOUBLE` / `ACDNN_TYPE_FLOAT`；一个元素。默认值：0.0f。 |
| `ACDNN_ATTR_POINTWISE_RELU_UPPER_CLIP` | 设置 ReLU 的上裁剪值。如果 (value > upper_clip)，则 value = upper_clip。<br>**类型** ： `ACDNN_TYPE_DOUBLE` / `ACDNN_TYPE_FLOAT`；一个元素。默认值：Numeric limit max。 |
| `ACDNN_ATTR_POINTWISE_RELU_LOWER_CLIP_SLOPE` | 设置 ReLU 的下裁剪斜率值。如果 `value < lower_clip`，则 `value = lower_clip + lower_clip_slope * (value - lower_clip)`。<br>**类型** ： `ACDNN_TYPE_DOUBLE` / `ACDNN_TYPE_FLOAT`；一个元素。默认值：0.0f。 |
| `ACDNN_ATTR_POINTWISE_ELU_ALPHA` | 设置 ELU 的 Alpha 值。如果 `value < 0.0`，则 `value = alpha * (e^value - 1.0)`。<br>**类型** ： `ACDNN_TYPE_DOUBLE` / `ACDNN_TYPE_FLOAT`；一个元素。默认值：1.0f。 |
| `ACDNN_ATTR_POINTWISE_SOFTPLUS_BETA` | 设置 Softplus 的 Beta 值。value = log(1 + e^(beta * value)) / beta。<br>**类型** ： `ACDNN_TYPE_DOUBLE` / `ACDNN_TYPE_FLOAT`；一个元素。默认值：1.0f。 |

**定型**

使用 `ACDNN_BACKEND_POINTWISE_DESCRIPTOR` 调用 `acdnnBackendFinalize()` 可能返回以下值：

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.3.22. ACDNN_BACKEND_REDUCTION_DESCRIPTOR {#5322-acdnn_backend_reduction_descriptor}

通过以下方式创建：
```cpp
acdnnBackendCreateDescriptor(ACDNN_BACKEND_REDUCTION_DESCRIPTOR, &desc);
```

acDNN 后端归约描述符指定归约操作所需的任何元数据，包括数学运算和计算数据类型。

**属性**

| 属性名称 | 描述 |
| :--- | :--- |
| `ACDNN_ATTR_REDUCTION_OPERATOR` | 用于归约操作的数学运算。<br>**类型** ： `ACDNN_TYPE_REDUCTION_OPERATOR_TYPE`；一个元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_REDUCTION_COMP_TYPE` | 用于归约操作的计算精度。<br>**类型** ： `ACDNN_TYPE_DATA_TYPE`；一个元素。<br>**要求** ：必需属性。 |

**定型**

`acdnnBackendFinalize(desc)` 的返回值，其中 desc 是 `ACDNN_BACKEND_REDUCTION_DESCRIPTOR`：

返回码：

- `ACDNN_STATUS_NOT_SUPPORTED`：遇到不受支持的属性值。可能的原因包括： `ACDNN_ATTR_REDUCTION_OPERATOR` 未设置为 `ACDNN_REDUCE_TENSOR_ADD`、`ACDNN_REDUCE_TENSOR_MUL`、`ACDNN_REDUCE_TENSOR_MIN` 或 `ACDNN_REDUCE_TENSOR_MAX`。
- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.3.23. ACDNN_BACKEND_RESAMPLE_DESCRIPTOR {#5323-acdnn_backend_resample_descriptor}

通过以下方式创建：
```cpp
acdnnBackendCreateDescriptor(ACDNN_BACKEND_RESAMPLE_DESCRIPTOR, &desc);
```

acDNN 后端重采样描述符指定用于前向和反向传播中重采样操作（上采样或下采样）的参数。

**属性**

| 属性名称 | 描述 |
| :--- | :--- |
| `ACDNN_ATTR_RESAMPLE_MODE` | 指定重采样的模式，例如平均池化、最近邻等。<br>**类型** ： `ACDNN_TYPE_RESAMPLE_MODE`；一个元素。默认值为 `ACDNN_RESAMPLE_NEAREST`。 |
| `ACDNN_ATTR_RESAMPLE_COMP_TYPE` | 重采样算子的计算数据类型。<br>**类型** ： `ACDNN_TYPE_DATA_TYPE`；一个元素。默认值为 `ACDNN_DATA_FLOAT`。 |
| `ACDNN_ATTR_RESAMPLE_NAN_PROPAGATION` | 指定传播 NaN 的方法。<br>**类型** ： `ACDNN_TYPE_NAN_PROPOGATION`；一个元素。默认值为 `ACDNN_NOT_PROPAGATE_NAN`。 |
| `ACDNN_ATTR_RESAMPLE_SPATIAL_DIMS` | 指定执行重采样的空间维度数量。<br>**类型** ： `ACDNN_TYPE_INT64`；一个元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_RESAMPLE_PADDING_MODE` | 指定用于填充的值。<br>**类型** ： `ACDNN_TYPE_PADDING_MODE`；一个元素。默认值为 `ACDNN_ZERO_PAD`。 |
| `ACDNN_ATTR_RESAMPLE_STRIDES` | 核函数/滤波器在每个维度中的步幅。<br>**类型** ： `ACDNN_TYPE_INT64`；受限于库支持的最大空间维度数。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_RESAMPLE_PRE_PADDINGS` | 在每个维度中添加到输入张量开头的填充。<br>**类型** ： `ACDNN_TYPE_INT64`；受限于库支持的最大空间维度数。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_RESAMPLE_POST_PADDINGS` | 在每个维度中添加到输入张量末尾的填充。<br>**类型** ： `ACDNN_TYPE_INT64`；受限于库支持的最大空间维度数。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_RESAMPLE_WINDOW_DIMS` | 滤波器的空间维度。<br>**类型** ： `ACDNN_TYPE_INT64`；受限于库支持的最大空间维度数。<br>**要求** ：必需属性。 |

**定型**

使用 `ACDNN_BACKEND_RESAMPLE_DESCRIPTOR` 调用 `acdnnBackendFinalize()` 的返回值：

返回码：

- `ACDNN_STATUS_NOT_SUPPORTED`：遇到不受支持的属性值。可能的原因包括：设置 `ACDNN_ATTR_RESAMPLE_WINDOW_DIMS`、`ACDNN_ATTR_RESAMPLE_STRIDES`、`ACDNN_ATTR_RESAMPLE_PRE_PADDINGS` 和 `ACDNN_ATTR_RESAMPLE_POST_PADDINGS` 的 `elemCount` 参数不等于为 `ACDNN_ATTR_RESAMPLE_SPATIAL_DIMS` 设置的值； `ACDNN_ATTR_RESAMPLE_MODE` 设置为 `ACDNN_RESAMPLE_BILINEAR` 且任何 `ACDNN_ATTR_RESAMPLE_WINDOW_DIMS` 未设置为 2。
- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.3.24. ACDNN_BACKEND_TENSOR_DESCRIPTOR {#5324-acdnn_backend_tensor_descriptor}

通过以下方式创建：
```cpp
acdnnBackendCreateDescriptor(ACDNN_BACKEND_TENSOR_DESCRIPTOR, &desc);
```

acDNN 后端张量（Tensor）允许开发者指定通用张量的内存存储。张量由唯一标识符标识，并通过其数据类型、数据字节对齐要求以及其维度的范围和步幅进行描述。可选地，张量元素可以是其某个维度中的向量。当张量是计算图中的中间变量且未映射到物理全局内存存储时，也可以将其设置为虚拟。

**属性**

acDNN 后端张量描述符的属性是枚举类型 `acdnnBackendAttributeName_t` 的值，前缀为 `ACDNN_ATTR_TENSOR_`：

| 属性名称 | 描述 |
| :--- | :--- |
| `ACDNN_ATTR_TENSOR_UNIQUE_ID` | 唯一标识张量的整数。<br>**类型** ： `ACDNN_TYPE_INT64`；一个元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_TENSOR_DATA_TYPE` | 张量的数据类型。<br>**类型** ： `ACDNN_TYPE_DATA_TYPE`；一个元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_TENSOR_DIMENSIONS` | 张量各维度的范围。<br>**类型** ： `ACDNN_TYPE_INT64`；元素数等于维数。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_TENSOR_STRIDES` | 张量各维度的步幅。<br>**类型** ： `ACDNN_TYPE_INT64`；元素数等于维数。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_TENSOR_BYTE_ALIGNMENT` | 数据字节对齐要求。<br>**类型** ： `ACDNN_TYPE_INT64`；一个元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_TENSOR_IS_VIRTUAL` | 标记张量是否为虚拟（不映射到物理全局内存）。<br>**类型** ： `ACDNN_TYPE_BOOLEAN`；一个元素。<br>**要求** ：可选属性，默认 false。 |
| `ACDNN_ATTR_TENSOR_VECTOR_COUNT` | 向量化维度的向量数量。<br>**类型** ： `ACDNN_TYPE_INT64`；一个元素。<br>**要求** ：可选属性，默认 1。 |
| `ACDNN_ATTR_TENSOR_VECTORIZED_DIMENSION` | 向量化的维度索引。<br>**类型** ： `ACDNN_TYPE_INT64`；一个元素。<br>**要求** ：仅在 `VECTOR_COUNT` > 1 时必需。 |
| `ACDNN_ATTR_TENSOR_REORDERING_MODE` | 张量的重排模式。<br>**类型** ： `ACDNN_TYPE_TENSOR_REORDERING_MODE`；一个元素。<br>**要求** ：可选属性。 |

返回码：

- `ACDNN_STATUS_BAD_PARAM`：遇到无效的属性值。例如：任何 Tensor 维度或步幅不是正数；Tensor Alignment 属性的值无法被数据类型的大小整除。
- `ACDNN_STATUS_NOT_SUPPORTED`：遇到不受支持的属性值。例如：数据类型属性是 `ACDNN_DATA_INT8x4`、`ACDNN_DATA_UINT8x4` 或 `ACDNN_DATA_INT8x32`；数据类型属性是 `ACDNN_DATA_INT8` 且 `ACDNN_ATTR_TENSOR_VECTOR_COUNT` 的值不是 1、4 或 32。
- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

#### 5.3.25. ACDNN_BACKEND_VARIANT_PACK_DESCRIPTOR {#5325-acdnn_backend_variant_pack_descriptor}

通过以下方式创建：
```cpp
acdnnBackendCreateDescriptor(ACDNN_BACKEND_VARIANT_PACK_DESCRIPTOR, &desc);
```

acDNN 后端变体包（Variant Pack）允许开发者设置指向操作图的各种非虚拟张量的设备缓冲区的指针，这些张量由唯一标识符、工作空间和计算中间结果标识。

**属性**

| 属性名称 | 描述 |
| :--- | :--- |
| `ACDNN_ATTR_VARIANT_PACK_UNIQUE_IDS` | 每个数据指针的张量唯一标识符。<br>**类型** ： `ACDNN_TYPE_INT64`；零个或多个元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_VARIANT_PACK_DATA_POINTERS` | 张量数据设备指针。<br>**类型** ： `ACDNN_TYPE_VOID_PTR`；零个或多个元素。<br>**要求** ：必需属性。 |
| `ACDNN_ATTR_VARIANT_PACK_INTERMEDIATES` | 中间结果设备指针。<br>**类型** ： `ACDNN_TYPE_VOID_PTR`；零个或多个元素。设置属性不受支持。占位符，将在未来版本中添加支持。 |
| `ACDNN_ATTR_VARIANT_PACK_WORKSPACE` | 工作空间设备指针。<br>**类型** ： `ACDNN_TYPE_VOID_PTR`；一个元素。<br>**要求** ：必需属性。 |

**定型**

使用 acDNN 后端变体包描述符调用 `acdnnBackendFinalize()` 的返回值：

返回码：

- `ACDNN_STATUS_SUCCESS`：操作成功。

详见 [`acdnnStatus_t`](#21220-acdnnstatus_t)。

### 5.4. 用例 {#54-用例}

本节用一个完整的分组 3D 卷积例子，串联后端 API 从「描述模型 → 选择引擎 → 构建执行计划 → 实际执行」的全过程，可以与 5.2 API 函数 / 5.3 描述符类型对照阅读。整体步骤如下：

1. **构建操作图** ，把所有输入 / 输出张量描述完毕，关联至一个卷积前向操作，再放进只有一个节点的操作图里（5.4.1）。
2. **选择引擎 + 配置引擎配置**，指定要用哪个引擎（按 `ACDNN_ATTR_ENGINE_GLOBAL_INDEX`），并按需调整性能调优旋钮（5.4.2）。
3. **组装执行计划 + 变体包并执行**，基于引擎配置定型一个计划、查询工作空间大小、把实际数据指针写入变体包，最后调用 `acdnnBackendExecute()`（5.4.3）。

#### 5.4.1. 为分组卷积设置操作图 {#541-为分组卷积设置操作图}

以下示例中，操作图仅挂载一个分组 3D 卷积前向操作；流程是：先建好输入 / 输出张量的描述符，再把它们绑定到一个卷积前向操作描述符上，最后用这一个操作组成操作图。

**1. 创建张量描述符。**

```cpp
acdnnBackendDescriptor_t xDesc;
acdnnBackendCreateDescriptor(ACDNN_BACKEND_TENSOR_DESCRIPTOR, &xDesc);
acdnnDataType_t dtype = ACDNN_DATA_FLOAT;
acdnnBackendSetAttribute(xDesc, ACDNN_ATTR_TENSOR_DATA_TYPE, ACDNN_TYPE_DATA_TYPE, 1, &dtype);
int64_t xDim[] = {n, g, c, d, h, w};
int64_t xStr[] = {g * c * d * h * w, c * d * h * w, d * h * w, h * w, w, 1};
int64_t xUi = 'x';
int64_t alignment = 4;
acdnnBackendSetAttribute(xDesc, ACDNN_ATTR_TENSOR_DIMENSIONS, ACDNN_TYPE_INT64, 6, xDim);
acdnnBackendSetAttribute(xDesc, ACDNN_ATTR_TENSOR_STRIDES, ACDNN_TYPE_INT64, 6, xStr);
acdnnBackendSetAttribute(xDesc, ACDNN_ATTR_TENSOR_UNIQUE_ID, ACDNN_TYPE_INT64, 1, &xUi);
acdnnBackendSetAttribute(xDesc, ACDNN_ATTR_TENSOR_BYTE_ALIGNMENT, ACDNN_TYPE_INT64, 1, &alignment);
acdnnBackendFinalize(xDesc);
```

**2. 对卷积滤波器和输出张量描述符重复上述步骤。**

六个滤波器张量维度分别为 [g, k, c, t, r, s]，六个输出张量维度分别为 [n, g, k, o, p, q]。在定型绑定张量的卷积算子时，将检查维度一致性，这意味着三个张量共享的所有 n、g、c、k 值必须相同。否则，返回 `ACDNN_STATUS_BAD_PARAM` 状态。

为了与 `acdnnTensorDescriptor_t` 中指定张量并在卷积 API 中使用的方式向后兼容，也可以指定具有以下维度的 5D 张量：
- 图像： [n, g*c, d, h, w]。
- 滤波器： [g*k, c, t, r, s]。
- 响应： [n, g*k, o, p, q]。

在此格式中，在定型绑定张量的卷积算子描述符时，将执行类似的一致性检查。

**3. 创建、设置并定型卷积算子描述符。**

```cpp
acdnnBackendDescriptor_t convDesc;
acdnnBackendCreateDescriptor(ACDNN_BACKEND_CONVOLUTION_DESCRIPTOR, &convDesc);
acdnnConvolutionMode_t mode = ACDNN_CROSS_CORRELATION;
acdnnBackendSetAttribute(convDesc, ACDNN_ATTR_CONVOLUTION_COMP_TYPE, ACDNN_TYPE_DATA_TYPE, 1, &dtype);
acdnnBackendSetAttribute(convDesc, ACDNN_ATTR_CONVOLUTION_CONV_MODE, ACDNN_TYPE_CONVOLUTION_MODE, 1, &mode);
int64_t nbDims = 3;
acdnnBackendSetAttribute(convDesc, ACDNN_ATTR_CONVOLUTION_SPATIAL_DIMS, ACDNN_TYPE_INT64, 1, &nbDims);
int64_t pad[] = {0, 0, 0}, stride[] = {1, 1, 1}, dilation[] = {1, 1, 1};
acdnnBackendSetAttribute(convDesc, ACDNN_ATTR_CONVOLUTION_PRE_PADDINGS, ACDNN_TYPE_INT64, nbDims, pad);
acdnnBackendSetAttribute(convDesc, ACDNN_ATTR_CONVOLUTION_POST_PADDINGS, ACDNN_TYPE_INT64, nbDims, pad);
acdnnBackendSetAttribute(convDesc, ACDNN_ATTR_CONVOLUTION_DILATIONS, ACDNN_TYPE_INT64, nbDims, dilation);
acdnnBackendSetAttribute(convDesc, ACDNN_ATTR_CONVOLUTION_FILTER_STRIDES, ACDNN_TYPE_INT64, nbDims, stride);
acdnnBackendFinalize(convDesc);

acdnnBackendDescriptor_t opDesc;
acdnnBackendCreateDescriptor(ACDNN_BACKEND_OPERATION_CONVOLUTION_FORWARD_DESCRIPTOR, &opDesc);
acdnnBackendSetAttribute(opDesc, ACDNN_ATTR_OPERATION_CONVOLUTION_FORWARD_X, ACDNN_TYPE_BACKEND_DESCRIPTOR, 1, &xDesc);
acdnnBackendSetAttribute(opDesc, ACDNN_ATTR_OPERATION_CONVOLUTION_FORWARD_W, ACDNN_TYPE_BACKEND_DESCRIPTOR, 1, &wDesc);
acdnnBackendSetAttribute(opDesc, ACDNN_ATTR_OPERATION_CONVOLUTION_FORWARD_Y, ACDNN_TYPE_BACKEND_DESCRIPTOR, 1, &yDesc);
acdnnBackendSetAttribute(opDesc, ACDNN_ATTR_OPERATION_CONVOLUTION_FORWARD_CONV_DESC, ACDNN_TYPE_BACKEND_DESCRIPTOR, 1, &convDesc);
float alpha = 1.0f, beta = 0.0f;
acdnnBackendSetAttribute(opDesc, ACDNN_ATTR_OPERATION_CONVOLUTION_FORWARD_ALPHA, ACDNN_TYPE_FLOAT, 1, &alpha);
acdnnBackendSetAttribute(opDesc, ACDNN_ATTR_OPERATION_CONVOLUTION_FORWARD_BETA, ACDNN_TYPE_FLOAT, 1, &beta);
acdnnBackendFinalize(opDesc);
```

**4. 用操作组建操作图。**

```cpp
acdnnBackendDescriptor_t opGraph;
acdnnBackendCreateDescriptor(ACDNN_BACKEND_OPERATIONGRAPH_DESCRIPTOR, &opGraph);
acdnnBackendSetAttribute(opGraph, ACDNN_ATTR_OPERATIONGRAPH_OPS, ACDNN_TYPE_BACKEND_DESCRIPTOR, 1, &opDesc);
acdnnBackendSetAttribute(opGraph, ACDNN_ATTR_OPERATIONGRAPH_HANDLE, ACDNN_TYPE_HANDLE, 1, &handle);
acdnnBackendFinalize(opGraph);
```

#### 5.4.2. 设置引擎配置 {#542-设置引擎配置}

承接 5.4.1 已定型的操作图，本节给出最简形态的引擎配置：选 `ACDNN_ATTR_ENGINE_GLOBAL_INDEX = 0` 的引擎， 不修改任何性能调优旋钮。如需调优，可在定型引擎之后用 `acdnnBackendGetAttribute()` 列出可用旋钮、再以 `acdnnBackendSetAttribute()` 写入选择。

**1. 创建、设置并定型引擎描述符。**

```cpp
acdnnBackendDescriptor_t engine;
acdnnBackendCreateDescriptor(ACDNN_BACKEND_ENGINE_DESCRIPTOR, &engine);
acdnnBackendSetAttribute(engine, ACDNN_ATTR_ENGINE_OPERATION_GRAPH, ACDNN_TYPE_BACKEND_DESCRIPTOR, 1, &opGraph);
int64_t gidx = 0;
acdnnBackendSetAttribute(engine, ACDNN_ATTR_ENGINE_GLOBAL_INDEX, ACDNN_TYPE_INT64, 1, &gidx);
acdnnBackendFinalize(engine);
```

开发者可以使用 `acdnnBackendGetAttribute()` API 调用查询已定型的引擎描述符的属性，包括它具有的性能调优旋钮。为简单起见，此用例跳过此步骤，并假设开发者正在设置引擎配置描述符，而不需要对性能调优旋钮进行任何更改。

**2. 创建、设置并定型引擎配置描述符。**

```cpp
acdnnBackendDescriptor_t engcfg;
acdnnBackendCreateDescriptor(ACDNN_BACKEND_ENGINECFG_DESCRIPTOR, &engcfg);
acdnnBackendSetAttribute(engcfg, ACDNN_ATTR_ENGINECFG_ENGINE, ACDNN_TYPE_BACKEND_DESCRIPTOR, 1, &engine);
acdnnBackendFinalize(engcfg);
```

#### 5.4.3. 设置并执行计划 {#543-设置并执行计划}

最后一步，从 5.4.2 的引擎配置出发，定型一个执行计划、查询工作空间大小、将数据指针写入变体包，再启动一次实际执行。

**1. 创建、设置并定型执行计划描述符。获取要分配的工作空间大小。**

```cpp
acdnnBackendDescriptor_t plan;
acdnnBackendCreateDescriptor(ACDNN_BACKEND_EXECUTION_PLAN_DESCRIPTOR, &plan);
acdnnBackendSetAttribute(plan, ACDNN_ATTR_EXECUTION_PLAN_ENGINE_CONFIG, ACDNN_TYPE_BACKEND_DESCRIPTOR, 1, &engcfg);
acdnnBackendFinalize(plan);
int64_t workspaceSize;
acdnnBackendGetAttribute(plan, ACDNN_ATTR_EXECUTION_PLAN_WORKSPACE_SIZE, ACDNN_TYPE_INT64, 1, NULL, &workspaceSize);
```

**2. 创建、设置并定型变体包描述符。**

```cpp
void *devPtrs[3] = {xData, wData, yData}; // device pointer
int64_t uids[3] = {'x', 'w', 'y'};
void *workspace;
acdnnBackendDescriptor_t varpack;
acdnnBackendCreateDescriptor(ACDNN_BACKEND_VARIANT_PACK_DESCRIPTOR, &varpack);
acdnnBackendSetAttribute(varpack, ACDNN_ATTR_VARIANT_PACK_DATA_POINTERS, ACDNN_TYPE_VOID_PTR, 3, devPtrs);
acdnnBackendSetAttribute(varpack, ACDNN_ATTR_VARIANT_PACK_UNIQUE_IDS, ACDNN_TYPE_INT64, 3, uids);
acdnnBackendSetAttribute(varpack, ACDNN_ATTR_VARIANT_PACK_WORKSPACE, ACDNN_TYPE_VOID_PTR, 1, &workspace);
acdnnBackendFinalize(varpack);
```

**3. 使用变体包执行计划。**

```cpp
acdnnBackendExecute(handle, plan, varpack);
```

**比赛关联：** Graph API 是 acDNN 侧"算子融合 + 自动调优"的深水区：把 conv/pointwise/matmul/reduction 等节点组成操作图后，由引擎启发式（`ACDNN_HEUR_MODE_*`）挑选实现，还可用 `acdnnBackendKnobType_t`（SPLIT_K、TILE_SIZE、SWIZZLE 等 25 种旋钮）做细粒度性能调优——这是评分中"系统级优化深度"可写入的方案；执行计划定型一次、变体包反复执行的模式也适合压每次迭代的 host 侧开销。

## 6. 类型与枚举速查 {#6-类型与枚举速查}

本章集中索引 acDNN 各功能域使用的核心类型与枚举，方便按名称快速定位。

| 类型名 | 所属功能域 | 定义位置 |
| :--- | :--- | :--- |
| `acdnnHandle_t` | 基础运算 | 2.1 |
| `acdnnStatus_t` | 基础运算 | 2.1 |
| `acdnnDataType_t` | 基础运算 | 2.1 |
| `acdnnTensorDescriptor_t` | 基础运算 | 2.1 |
| `acdnnTensorFormat_t` | 基础运算 | 2.1 |
| `acdnnTensorTransformDescriptor_t` | 基础运算 | 2.1 |
| `acdnnFilterDescriptor_t` | 基础运算 | 2.1 |
| `acdnnActivationDescriptor_t` | 基础运算 | 2.1 |
| `acdnnActivationMode_t` | 基础运算 | 2.1 |
| `acdnnPoolingDescriptor_t` | 基础运算 | 2.1 |
| `acdnnPoolingMode_t` | 基础运算 | 2.1 |
| `acdnnDropoutDescriptor_t` | 基础运算 | 2.1 |
| `acdnnLRNDescriptor_t` | 基础运算 | 2.1 |
| `acdnnOpTensorDescriptor_t` | 基础运算 | 2.1 |
| `acdnnReduceTensorDescriptor_t` | 基础运算 | 2.1 |
| `acdnnSpatialTransformerDescriptor_t` | 基础运算 | 2.1 |
| `acdnnBatchNormMode_t` | 基础运算 | 2.1 |
| `acdnnBatchNormOps_t` | 基础运算 | 2.1 |
| `acdnnMathType_t` | 基础运算 | 2.1 |
| `acdnnNanPropagation_t` | 基础运算 | 2.1 |
| `acdnnSoftmaxAlgorithm_t` | 基础运算 | 2.1 |
| `acdnnSoftmaxMode_t` | 基础运算 | 2.1 |
| `acdnnDeterminism_t` | 基础运算 | 2.1 |
| `acdnnConvolutionDescriptor_t` | 卷积网络 | 3.1 |
| `acdnnConvolutionMode_t` | 卷积网络 | 3.1 |
| `acdnnConvolutionFwdAlgo_t` | 卷积网络 | 3.1 |
| `acdnnConvolutionBwdDataAlgo_t` | 卷积网络 | 3.1 |
| `acdnnConvolutionBwdFilterAlgo_t` | 卷积网络 | 3.1 |
| `acdnnRNNDescriptor_t` | 高级网络 | 4.1 |
| `acdnnRNNDataDescriptor_t` | 高级网络 | 4.1 |
| `acdnnRNNMode_t` | 高级网络 | 4.1 |
| `acdnnRNNAlgo_t` | 高级网络 | 4.1 |
| `acdnnRNNInputMode_t` | 高级网络 | 4.1 |
| `acdnnRNNDataLayout_t` | 高级网络 | 4.1 |
| `acdnnDirectionMode_t` | 高级网络 | 4.1 |
| `acdnnAttnDescriptor_t` | 高级网络 | 4.1 |
| `acdnnSeqDataDescriptor_t` | 高级网络 | 4.1 |
| `acdnnCTCLossDescriptor_t` | 高级网络 | 4.1 |
| `acdnnCTCLossAlgo_t` | 高级网络 | 4.1 |
| `acdnnWgradMode_t` | 高级网络 | 4.1 |
| `acdnnBackendDescriptor_t` | Graph API | 5.1 |
| `acdnnBackendDescriptorType_t` | Graph API | 5.1 |
| `acdnnBackendAttributeName_t` | Graph API | 5.1 |
| `acdnnBackendAttributeType_t` | Graph API | 5.1 |


