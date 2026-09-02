# HGPP 编程指南 <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [1. 概述](#1-概述)
  - [1.1. 文件](#11-文件)
  - [1.2. 编译示例](#12-编译示例)
  - [1.3. 通用约定](#13-通用约定)
  - [1.4. 图像处理约定](#14-图像处理约定)
  - [1.5. 其他重要说明](#15-其他重要说明)
- [2. 数据类型、结构体、枚举和常量](#2-数据类型结构体枚举和常量)
  - [2.1. 基本数据类型](#21-基本数据类型)
  - [2.2. 复数类型](#22-复数类型)
  - [2.3. 几何结构](#23-几何结构)
  - [2.4. 插值模式](#24-插值模式)
  - [2.5. 边界类型](#25-边界类型)
  - [2.6. 舍入模式](#26-舍入模式)
  - [2.7. 错误码](#27-错误码)
  - [2.8. 其他枚举](#28-其他枚举)
  - [2.9. 批处理结构](#29-批处理结构)
  - [2.10. 其他结构](#210-其他结构)
- [3. 辅助函数](#3-辅助函数)
  - [3.1. hgppGetLibVersion](#31-hgppgetlibversion)
- [4. 内存管理函数](#4-内存管理函数)
  - [4.1. 内存分配与步幅](#41-内存分配与步幅)
  - [4.2. 内存分配函数族](#42-内存分配函数族)
  - [4.3. 内存释放函数](#43-内存释放函数)
  - [4.4. 使用说明](#44-使用说明)
- [5. 算术和逻辑运算](#5-算术和逻辑运算)
  - [5.1. 算术运算](#51-算术运算)
  - [5.2. 逻辑运算](#52-逻辑运算)
  - [5.3. Alpha 合成](#53-alpha-合成)
  - [5.4. 错误码](#54-错误码)
- [6. 图像颜色转换](#6-图像颜色转换)
  - [6.1. RGB↔YUV 转换](#61-rgbyuv-转换)
  - [6.2. RGB↔YCbCr 转换](#62-rgbycbcr-转换)
  - [6.3. RGB↔HSV/HLS](#63-rgbhsvhls)
  - [6.4. RGB↔Lab/Luv 转换](#64-rgblabluv-转换)
  - [6.5. YUV 采样格式](#65-yuv-采样格式)
  - [6.6. ColorTwist](#66-colortwist)
  - [6.7. 批量转换](#67-批量转换)
  - [6.8. Debayer 去马赛克](#68-debayer-去马赛克)
  - [6.9. Gamma 校正](#69-gamma-校正)
  - [6.10. LUT 操作](#610-lut-操作)
  - [6.11. Alpha 合成](#611-alpha-合成)
  - [6.12. CompColorKey](#612-compcolorkey)
  - [6.13. JPEG 颜色转换](#613-jpeg-颜色转换)
  - [6.14. 其他转换](#614-其他转换)
  - [6.15. 错误码汇总](#615-错误码汇总)
- [7. 数据交换与初始化](#7-数据交换与初始化)
  - [7.1. 像素设置](#71-像素设置)
  - [7.2. 掩码设置](#72-掩码设置)
  - [7.3. 通道设置](#73-通道设置)
  - [7.4. 图像拷贝](#74-图像拷贝)
  - [7.5. 掩码拷贝](#75-掩码拷贝)
  - [7.6. 通道拷贝](#76-通道拷贝)
  - [7.7. 提取通道](#77-提取通道)
  - [7.8. 插入通道](#78-插入通道)
  - [7.9. Packet 到 Planar](#79-packet-到-planar)
  - [7.10. Planar 到 Packet](#710-planar-到-packet)
  - [7.11. 常量边界](#711-常量边界)
  - [7.12. 复制边界](#712-复制边界)
  - [7.13. 包裹边界](#713-包裹边界)
  - [7.14. 子像素拷贝](#714-子像素拷贝)
  - [7.15. 位深度转换](#715-位深度转换)
  - [7.16. 位深度缩放](#716-位深度缩放)
  - [7.17. 通道复制](#717-通道复制)
  - [7.18. 转置](#718-转置)
  - [7.19. 通道交换](#719-通道交换)
  - [7.20. 错误码](#720-错误码)
- [8. 图像滤波函数](#8-图像滤波函数)
  - [8.1. 一维线性滤波](#81-一维线性滤波)
  - [8.2. 二维卷积](#82-二维卷积)
  - [8.3. 固定线性滤波](#83-固定线性滤波)
  - [8.4. Rank 滤波](#84-rank-滤波)
  - [8.5. 距离变换](#85-距离变换)
  - [8.6. 计算机视觉滤波](#86-计算机视觉滤波)
  - [8.7. Flood Fill （洪水填充）](#87-flood-fill-洪水填充)
  - [8.8. Label Markers （标记）](#88-label-markers-标记)
  - [8.9. Bound Segments （边界段）](#89-bound-segments-边界段)
  - [8.10. Watershed Segmentation （分水岭分割）](#810-watershed-segmentation-分水岭分割)
  - [8.11. 错误码](#811-错误码)
- [9. 图像几何变换](#9-图像几何变换)
  - [9.1. 几何变换特性](#91-几何变换特性)
  - [9.2. Resize 缩放](#92-resize-缩放)
  - [9.3. Remap 重映射](#93-remap-重映射)
  - [9.4. Rotate 旋转](#94-rotate-旋转)
  - [9.5. Mirror 镜像](#95-mirror-镜像)
  - [9.6. 仿射变换](#96-仿射变换)
  - [9.7. 透视变换](#97-透视变换)
  - [9.8. 反向仿射变换](#98-反向仿射变换)
  - [9.9. 基于四边形的仿射变换](#99-基于四边形的仿射变换)
  - [9.10. 反向透视变换](#910-反向透视变换)
  - [9.11. 基于四边形的透视变换](#911-基于四边形的透视变换)
  - [9.12. 批处理](#912-批处理)
  - [9.13. 错误码汇总](#913-错误码汇总)
- [10. 图像线性变换函数](#10-图像线性变换函数)
  - [10.1. 傅里叶变换](#101-傅里叶变换)
  - [10.2. 通用参数说明](#102-通用参数说明)
- [11. 图像形态学操作](#11-图像形态学操作)
  - [11.1. 膨胀函数（Dilation Functions）](#111-膨胀函数dilation-functions)
  - [11.2. 腐蚀函数（Erosion Functions）](#112-腐蚀函数erosion-functions)
  - [11.3. 复杂形态学操作](#113-复杂形态学操作)
  - [11.4. 附录：错误码](#114-附录错误码)
- [12. 统计函数](#12-统计函数)
  - [12.1. 求和](#121-求和)
  - [12.2. 最小值](#122-最小值)
  - [12.3. 最大值](#123-最大值)
  - [12.4. 最小值/最大值](#124-最小值最大值)
  - [12.5. 均值/标准差](#125-均值标准差)
  - [12.6. 范数](#126-范数)
  - [12.7. 点积](#127-点积)
  - [12.8. 范围内计数](#128-范围内计数)
  - [12.9. 逐元素极值](#129-逐元素极值)
  - [12.10. 积分图](#1210-积分图)
  - [12.11. 直方图](#1211-直方图)
  - [12.12. 接近度](#1212-接近度)
  - [12.13. 平方距离](#1213-平方距离)
  - [12.14. 互相关](#1214-互相关)
  - [12.15. 平方距离](#1215-平方距离)
  - [12.16. 质量指数](#1216-质量指数)
  - [12.17. 误差计算](#1217-误差计算)
  - [12.18. 图像质量评估（IQA）](#1218-图像质量评估iqa)
  - [12.19. 批量质量评估（统一 ROI）](#1219-批量质量评估统一-roi)
  - [12.20. 批量质量评估高级版（独立 ROI）](#1220-批量质量评估高级版独立-roi)
  - [12.21. 错误码](#1221-错误码)
- [13. 阈值与比较操作](#13-阈值与比较操作)
  - [13.1. 图像阈值操作](#131-图像阈值操作)
  - [13.2. 图像比较操作](#132-图像比较操作)
  - [13.3. 阈值类型](#133-阈值类型)
  - [13.4. 错误码](#134-错误码)


HeteroGeneous 2D Image Processing Performance Primitives (HGPP) 是一个支持使用 真武 PPU 进行硬件加速的二维图像处理函数库，使用 真武 PPU 的通用计算资源完成计算任务。

## 1. 概述
### 1.1. 文件
HGPP API 在以下头文件中定义：

| 头文件 | 说明 |
|--------|------|
| `hgpp.h` | 主头文件 |
| `hgppdefs.h` | 数据类型和定义 |
| `hgppcore.h` | 核心函数 |
| `hgppi.h` | 图像处理函数 |
| `hgpps.h` | 信号处理函数 |

HGPP 的功能分为 3 个独立的库组：

| 库 | 说明 | 头文件 |
|----|------|--------|
| **HGPPC** (核心库) | 基本功能及其他库通用功能 | `hgpp.h` |
| **HGPPI** (图像处理库) | 图像处理函数 | `hgppi.h` 及 `hgppi_xxx.h` |
| **HGPPS** (信号处理库) | 信号处理函数（目前不支持） | `hgpps.h` |

> **注意：**
> 当前版本仅支持 HGPPC （颜色转换）和 HGPPI （图像处理）模块。 HGPPS （信号处理）模块尚未实现，相关头文件仅作接口预留。

HGPPI 子库按照头文件的拆分方式进行划分：

| 子库 | 功能 | 头文件 |
|------|------|--------|
| **HGPPC** | HGPP 核心库（必须链接） | `hgppCore.h` |
| **HGPPIAL** | 算术和逻辑运算 | `hgppi_arithmetic_and_logical_operations.h` |
| **HGPPICC** | 颜色转换和采样 | `hgppi_color_conversion.h` |
| **HGPPIDEI** | 数据交换和初始化 | `hgppi_data_exchange_and_initialization.h` |
| **HGPPIF** | 滤波和计算机视觉 | `hgppi_filtering_functions.h` |
| **HGPPIG** | 几何变换 | `hgppi_geometry_transforms.h` |
| **HGPPIM** | 形态学运算 | `hgppi_morphological_operations.h` |
| **HGPPIST** | 统计和线性变换 | `hgppi_statistics_functions.h`, `hgppi_linear_transforms.h` |
| **HGPPISU** | 内存支持 | `hgppi_support_functions.h` |
| **HGPPITC** | 阈值和比较运算 | `hgppi_threshold_and_compare_operations.h` |

### 1.2. 编译示例
**Linux 动态库**:
```bash
hgcc foo.c -lhgppc -lhgppicc -o foo
```

**Linux 静态库**:
```bash
hgcc foo.c -lhgppc_static -lhgppicc_static -o foo
```

**使用原生 C++ 编译器（Linux）**:
```bash
g++ foo.c -lhgppc_static -lhgppicc_static -lhggcrt_static -lpthread -ldl \
  -I <hggc-toolkit-path>/include -L <hggc-toolkit-path>/lib64 -o foo
```

### 1.3. 通用约定
#### 1.3.1. 内存管理
**注意**: **所有 HGPP 函数中的指针参数没有特别说明默认是设备指针**。

这一设计使开发者能够：
- 最小化内存传输次数
- 灵活选择 HGGC 运行时提供的各种内存传输机制（同步/异步、零拷贝、固定内存等）。

##### 1.3.1.1. 基本使用步骤
```text
1. 使用 hggcMemcpy() 将输入数据从主机传输到设备
2. 使用 HGPP 函数或自定义 HGGC 内核处理数据
3. 使用 hggcMemcpy() 将结果数据从设备传输回主机
```

##### 1.3.1.2. 临时缓冲区
某些计算（如信号和图像归约运算）需要额外的设备内存缓冲区。

**特点**:
- 分配和释放由用户负责。
- 内存是非结构化的，可在未初始化状态下传递。
- 可在多个计算之间重用（只要大小足够）
- 缓冲区大小通过辅助函数获取（如 `hgppsSumGetBufferSize_32f_Ctx()`）。

**示例**:
```cpp
// 计算所需临时缓冲区大小
size_t nBufferSize;
hgppsSumGetBufferSize_32f_Ctx(nLength, &nBufferSize, hgppStreamCtx);

// 分配临时缓冲区
hggcMalloc((void **)(&pDeviceBuffer), nBufferSize);

// 使用临时缓冲区调用接口
hgppsSum_32f_Ctx(pSrc, nLength, pSum, pDeviceBuffer, hgppStreamCtx);

// 释放
hggcFree(pDeviceBuffer);
```

#### 1.3.2. 函数命名
HGPP 使用以下命名约定（C 语言 API，不支持函数重载）：

```text
hgpp<模块信息><接口名称>_<数据类型信息>[_<附加变体信息>](<参数列表>)
```

**前缀**:
- `hgpp`: 所有 HGPP 函数。
- `hgppi`: 图像处理模块
- `hgpps`: 信号处理模块

**数据类型**: 使用与 HGPP 基本数据类型相同的名称（如 `8u` 表示 `HGpp8u`）。

**示例**: `hgppiAdd_8u_C1R_Ctx` 表示处理 8 位无符号单通道图像的加法函数。

#### 1.3.3. 整数结果缩放
HGPP 经常操作定点小数表示的物理量（如亮度）。数值运算（加法、乘法）可能产生超出原始定点范围的结果。包含 **"Sfs"** 后缀的接口会提供 `nScaleFactor` 参数控制缩放量。

**缩放公式**:
$$\text{最终结果} = \text{运算结果} \times 2^{-\text{nScaleFactor}}$$

**示例**: `hgppsSqr_8u_Sfs_Ctx()` 计算 8 位值的平方。

- 最大值 255 的平方：$255^2 = 65025$（超出 8 位范围 255）
- 使用缩放因子 8：$255^2 \times 2^{-8} = 254.00390625 ≈ 254$。
- 中等值 128：$128^2 \times 2^{-8} = 64$。

#### 1.3.4. 舍入模式
**默认舍入模式**: `HGPP_RND_FINANCIAL`

| 模式 | 说明 | 示例 |
|------|------|------|
| `HGPP_RND_NEAR` | 四舍五入到最近的偶数 | round(0.5)=0, round(1.5)=2 |
| `HGPP_RND_FINANCIAL` | 金融舍入（.5 向远离零方向） | round(0.5)=1, round(-1.5)=-2 |
| `HGPP_RND_ZERO` | 向零舍入（截断） | round(1.9)=1, round(-2.5)=-2 |

### 1.4. 图像处理约定
#### 1.4.1. 函数命名后缀
| 后缀 | 说明 |
|------|------|
| **A** | 4 通道图像的 alpha 通道不受影响 |
| **Cn** | n 通道像素（n=1,2,3,4） |
| **Pn** | n 个独立图像 Planar （n=1,2,3,4） |
| **C** | 仅操作感兴趣通道（COI） |
| **I** | 原图像操作（pSrcDst） |
| **M** | 掩码操作 |
| **R** | ROI 操作 |
| **Sfs** | 结果缩放和饱和 |

**后缀按字母顺序排列**，例如：`AC4IMRSfs`

#### 1.4.2. 图像数据传递
图像数据通过**指针 + 行步长 Step**传递：

1. **指向底层像素数据类型的指针**
2. **以字节为单位的行步长 Step （行跨度）**

##### 1.4.2.1. 行步长（Step/Stride）
一行中**包括填充在内的**字节数，即连续行第一个像素之间的字节数。允许奇数大小图像的行在对齐良好的地址上开始，优化内存访问模式。

**注意**: 行步长**始终以字节为单位**，不是像素。

##### 1.4.2.2. 图像数据参数名称
| 情况 | 参数名 | 说明 |
|------|--------|------|
| 源图像指针 | `pSrc`, `pSrc1`, `pSrc2`... | 常量指针 |
| 源批量指针 | `pSrcBatchList` | `HgppiImageDescriptor*` 类型 |
| 源图像指针数组 | `pSrc[]` | 每个指针指向不同 Planar |
| 目标图像指针 | `pDst`, `pDst1`, `pDst2`... | - |
| 原图像操作指针 | `pSrcDst` | 同时作为源和目标 |
| 掩码图像指针 | `pMask` | 布尔图像（0=假，非 0=真） |

##### 1.4.2.3. 行步长 Step 参数
| 情况 | 参数名 |
|------|--------|
| 源图像行步长 | `nSrcStep`, `nSrcStep1`, `nSrcStep2`... |
| 目标图像行步长 | `nDstStep`, `nDstStep1`, `nDstStep2`... |
| 原图像行步长 | `nSrcDstStep` |
| 掩码图像行步长 | `nMaskStep` |

#### 1.4.3. 图像数据对齐要求
**2 通道和 4 通道图像**:
```c
data_pointer % (#channels * sizeof(channel type)) == 0
```

**示例**: 4 通道 8 位图像（`HGpp8u`）要求所有像素落在 4 的倍数地址上。

**1 通道和 3 通道图像**:
```c
data_pointer % sizeof(data type) == 0
```

**错误码**:
- `HGPP_ALIGNMENT_ERROR`: 2/4 通道图像指针地址不是像素大小的倍数。
- `HGPP_NOT_EVEN_STEP_ERROR`: 2/4 通道图像行步长 Step 不是像素大小的倍数。

#### 1.4.4. 感兴趣区域（ROI）
感兴趣的图像的矩形子区域。支持 ROI 的接口后缀标有 **"R"**。通过 `HgppiSize` 结构（宽度，高度），起始像素由图像数据指针隐式给出。

**指针偏移计算**:
```cpp
// ROI 起始像素位于位置 (x, y)
pSrcOffset = pSrc + y * nSrcStep + x * PixelSize;
// PixelSize = NumberOfColorChannels * sizeof(PixelDataType)
```

**示例**: 对于 `hgppiSet_16s_C4R_Ctx()`
- `NumberOfColorChannels = 4`
- `sizeof(Hgpp16s) = 2`
- `PixelSize = 4 * 2 = 8`

**错误码**:
- `HGPP_SIZE_ERROR`: ROI 宽度或高度为负。
- `HGPP_STEP_ERROR`: ROI 宽度超过图像行步长 Step。

#### 1.4.5. 掩码操作
后缀 **"M"** 表示掩码操作。

**掩码解释**: `HGpp8u` 类型的布尔图像。
- `0`: 假（不处理）
- 非 `0`: 真（处理）

**处理规则**: 仅在空间对应的掩码像素为真（非零）的像素上执行操作。

#### 1.4.6. 感兴趣通道（COI）
用字母 **"C"** 作为后缀（如 `hgppiCopy_8u_C3CR_Ctx()`）。

**选择方式**:
1. **指针偏移**: 将图像数据指针偏移到直接指向感兴趣通道。
2. **通道编号**: 通过整数 `nCOI` 指定（1, 2, 或 3）。

**示例**:
```cpp
// 将三通道图像的第二个通道复制到目标图像的第一个通道
hgppiCopy_8u_C3CR_Ctx(pSrc + 1, nSrcStep, pDst, nDstStep, oSizeROI);

// 使用通道编号（图像统计函数）
hgppiMean_StdDev_8u_C3CR_Ctx(pSrc, nSrcStep, oSizeROI, nCOI, ...);
```

#### 1.4.7. 源图像采样
##### 1.4.7.1. 逐点操作
每个输出像素恰好需要读取一个输入像素。

**示例**: `hgppiAddC_8u_C1RSfs_Ctx()`

##### 1.4.7.2. 邻域操作
**定义**: 需要从源图像中读取一组像素（邻域）才能产生单个输出。

**示例**: `hgppiFilterBox_8u_C1R_Ctx()`

**相关参数**:
- `oMaskSize`: 邻域大小（`HgppiSize` 类型）
- `oAnchor`: 邻域相对位置（`HgppiPoint` 类型）

##### 1.4.7.3. 掩模大小参数
假设掩模锚定在 (0, 0) 且大小为 (w, h)：

$$
\begin{array}{llll}
S_{i,j} & S_{i,j+1} & \ldots & S_{i,j+w-1} \\
S_{i+1,j} & S_{i+1,j+1} & \ldots & S_{i+1,j+w-1} \\
\vdots & \vdots & \ddots & \vdots \\
S_{i+h-1,j} & S_{i+h-1,j+1} & \ldots & S_{i+h-1,j+w-1}
\end{array}
$$

##### 1.4.7.4. 锚点参数
使用锚点 (a, b) 选择掩模相对于当前像素的位置：

$$
\begin{array}{llll}
S_{i-a,j-b} & S_{i-a,j-b+1} & \ldots & S_{i-a,j-b+w-1} \\
S_{i-a+1,j-b} & S_{i-a+1,j-b+1} & \ldots & S_{i-a+1,j-b+w-1} \\
\vdots & \vdots & \ddots & \vdots \\
S_{i-a+h-1,j-b} & S_{i-a+h-1,j-b+1} & \ldots & S_{i-a+h-1,j-b+w-1}
\end{array}
$$

##### 1.4.7.5. 超出图像边界的采样
**问题**: 邻域操作可能超出源图像边界。

**解决方案**:
1. **缩小目标 ROI**: 使扩展后的源 ROI 不超出源图像大小。
2. **使用 Border 版本函数**: 如 `hgppiFilterBoxBorder_8u_C1R_Ctx()`
3. **使用边界扩展 Copy 接口**:
   - `hgppiCopyConstBorder_8u_C1R_Ctx()`
   - `hgppiCopyReplicateBorder_8u_C1R_Ctx()`
   - `hgppiCopyWrapBorder_8u_C1R_Ctx()`

### 1.5. 其他重要说明
- 可创建多个流上下文，每个对应特定的流和/或 真武 PPU 设备。
- 建议将流上下文数量限制为正在使用的 真武 PPU 数量。
- 所有 HGPP 函数都是**线程安全**的。

比赛关联：所有 HGPP 调用都经 `HgppStreamContext` 提交到 HGGC 流，这意味着图像预处理（resize/normalize）可以和 LLM 推理排在同一流或并行流上异步执行——是降低 VLM 流水线 TTFT 的关键挂接点。

## 2. 数据类型、结构体、枚举和常量
> **文件**: `hgppdefs.h` 
> **功能**: 定义 HGPP 库使用的所有基本数据类型、结构体、枚举和常量。

### 2.1. 基本数据类型
#### 2.1.1. 整数类型
| 类型别名 | 实际类型 | 说明 | 最小值 | 最大值 |
|----------|----------|------|--------|--------|
| `HGpp8u` | `unsigned char` | 8 位无符号 | 0 | 255 |
| `Hgpp8s` | `signed char` | 8 位有符号 | -128 | 127 |
| `Hgpp16u` | `unsigned short` | 16 位无符号 | 0 | 65535 |
| `Hgpp16s` | `short` | 16 位有符号 | -32768 | 32767 |
| `Hgpp32u` | `unsigned int` | 32 位无符号 | 0 | 2³²-1 |
| `Hgpp32s` | `int` | 32 位有符号 | -2³¹ | 2³¹-1 |
| `Hgpp64u` | `unsigned long long` | 64 位无符号 | 0 | 2⁶⁴-1 |
| `Hgpp64s` | `long long` | 64 位有符号 | -2⁶³ | 2⁶³-1 |

#### 2.1.2. 浮点类型
| 类型别名 | 实际类型 | 说明 |
|----------|----------|------|
| `Hgpp16f` | `struct Hgpp16f` | 16 位半精度浮点（fp16） |
| `Hgpp32f` | `float` | 32 位单精度浮点（IEEE 754） |
| `Hgpp64f` | `double` | 64 位双精度浮点 |

### 2.2. 复数类型
所有复数类型都包含 `re`（实部）和 `im`（虚部）两个成员。

| 类型别名 | 实部/虚部类型 | 说明 |
|----------|--------------|------|
| `HGpp8uc` | `HGpp8u` | 8 位无符号复数 |
| `Hgpp16uc` | `Hgpp16u` | 16 位无符号复数 |
| `Hgpp16sc` | `Hgpp16s` | 16 位有符号复数 |
| `Hgpp32uc` | `Hgpp32u` | 32 位无符号复数 |
| `Hgpp32sc` | `Hgpp32s` | 32 位有符号复数 |
| `Hgpp32fc` | `Hgpp32f` | 32 位浮点复数 |
| `Hgpp64sc` | `Hgpp64s` | 64 位有符号复数 |
| `Hgpp64fc` | `Hgpp64f` | 64 位浮点复数 |

### 2.3. 几何结构
#### 2.3.1. HgppiPoint （二维点）
```cpp
struct HgppiPoint {
    int x;  // x 坐标
    int y;  // y 坐标
};
```

**变体**:
- `HgppiPoint32f`: 32 位浮点坐标。
- `HgppiPoint64f`: 64 位浮点坐标。
- `HgppPointPolar`: 极坐标 (rho, theta)

#### 2.3.2. HgppiSize （二维尺寸）
```cpp
struct HgppiSize {
    int width;   // 矩形宽度
    int height;  // 矩形高度
};
```

#### 2.3.3. HgppiRect （二维矩形）
```cpp
struct HgppiRect {
    int x;      // 左上角 x 坐标（最低内存地址）
    int y;      // 左上角 y 坐标（最低内存地址）
    int width;  // 矩形宽度
    int height; // 矩形高度
};
```

### 2.4. 插值模式
#### 2.4.1. HgppiInterpolationMode
滤波方法枚举，按速度从快到慢、质量从低到高排序：

| 枚举值 | 说明 | 适用场景 |
|--------|------|----------|
| `HGPPI_INTER_NN` | 最近邻插值 | 速度优先，质量要求低 |
| `HGPPI_INTER_LINEAR` | 线性插值 | 平衡速度和质量 |
| `HGPPI_INTER_CUBIC` | 三次插值 | 质量要求较高 |
| `HGPPI_INTER_CUBIC2P_BSPLINE` | 双参数三次 (B=1, C=0) | B 样条插值 |
| `HGPPI_INTER_CUBIC2P_CATMULLROM` | 双参数三次 (B=0, C=1/2) | Catmull-Rom 插值 |
| `HGPPI_INTER_CUBIC2P_B05C03` | 双参数三次 (B=1/2, C=3/10) | 自定义参数 |
| `HGPPI_INTER_SUPER` | 超采样 | 缩小操作，质量很高 |
| `HGPPI_INTER_LANCZOS` | Lanczos 滤波 | 质量要求最高 |
| `HGPPI_INTER_LANCZOS3_ADVANCED` | 3 阶 Lanczos | 高级 Lanczos 滤波 |
| `HGPPI_SMOOTH_EDGE` | 平滑边缘滤波 | 边缘平滑处理 |

### 2.5. 边界类型
#### 2.5.1. HgppiBorderType
支持的图像边界模式：

| 枚举值 | 说明 | 图示 |
|--------|------|------|
| `HGPP_BORDER_UNDEFINED` | 未定义 | - |
| `HGPP_BORDER_NONE` | 无边界处理 | - |
| `HGPP_BORDER_CONSTANT` | 常量值填充 | `AAAAA\|ABCD\|AAAAA` |
| `HGPP_BORDER_REPLICATE` | 复制边缘像素 | `AAAAA\|ABCD\|DDDDD` |
| `HGPP_BORDER_WRAP` | 环绕边界 | `CDABCD\|ABCD\|ABCDAB` |
| `HGPP_BORDER_MIRROR` | 镜像边界 | `DCBA\|ABCD\|DCBA` |

### 2.6. 舍入模式
#### 2.6.1. HgppRoundMode
HGPP 支持的舍入模式（基于 IEEE-754 标准）：

| 枚举值 | 别名 | 说明 | 示例 |
|--------|------|------|------|
| `HGPP_RND_NEAR` | `HGPP_ROUND_NEAREST_TIES_TO_EVEN` | 四舍五入到最近的偶数 | round(0.5)=0, round(1.5)=2 |
| `HGPP_RND_FINANCIAL` | `HGPP_ROUND_NEAREST_TIES_AWAY_FROM_ZERO` | 金融舍入（.5 向远离零方向） | round(0.5)=1, round(-1.5)=-2 |
| `HGPP_RND_ZERO` | `HGPP_ROUND_TOWARD_ZERO` | 向零舍入（截断） | round(1.9)=1, round(-2.5)=-2 |

**默认舍入模式**: `HGPP_RND_FINANCIAL`

### 2.7. 错误码
#### 2.7.1. HgppStatus
几乎所有 HGPP 函数都使用这些返回码来返回错误状态信息。

**返回码规则**:
- **负值**: 错误
- **正值**: 警告
- **0**: 成功 (`HGPP_NO_ERROR` = `HGPP_SUCCESS`)

#### 2.7.2. 常见错误码
| 错误码 | 说明 |
|--------|------|
| `HGPP_NO_ERROR` / `HGPP_SUCCESS` | 操作成功 |
| `HGPP_NULL_POINTER_ERROR` | 空指针错误 |
| `HGPP_STEP_ERROR` | 步幅错误（≤0） |
| `HGPP_SIZE_ERROR` | ROI 尺寸错误 |
| `HGPP_ALIGNMENT_ERROR` | 内存对齐错误 |
| `HGPP_NOT_EVEN_STEP_ERROR` | 步幅不是像素整数倍（2/4 通道图像） |
| `HGPP_INTERPOLATION_ERROR` | 非法的插值模式 |
| `HGPP_RESIZE_FACTOR_ERROR` | 缩放因子 ≤ 0 |
| `HGPP_DIVISOR_ERROR` | 除数为零 |
| `HGPP_MASK_SIZE_ERROR` | 掩码尺寸错误 |
| `HGPP_ANCHOR_ERROR` | 锚点在掩码外部 |
| `HGPP_CHANNEL_ERROR` | 非法的通道索引 |
| `HGPP_NUMBER_OF_CHANNELS_ERROR` | 不支持的通道数 |
| `HGPP_SCALE_RANGE_ERROR` | 缩放范围错误（nMax ≤ nMin） |
| `HGPP_OVERFLOW_ERROR` | 数值溢出 |
| `HGPP_DIVIDE_BY_ZERO_ERROR` | 除以零错误 |
| `HGPP_MEMORY_ALLOCATION_ERR` | 内存分配失败 |
| `HGPP_NO_MEMORY_ERROR` | 内存不足 |
| `HGPP_NOT_IMPLEMENTED_ERROR` | 功能未实现 |

#### 2.7.3. 警告码
| 警告码 | 说明 |
|--------|------|
| `HGPP_NO_OPERATION_WARNING` | 未执行任何操作 |
| `HGPP_AFFINE_QUAD_INCORRECT_WARNING` | 四边形不符合仿射变换属性（使用前 3 个顶点） |
| `HGPP_WRONG_INTERSECTION_ROI_WARNING` | ROI 与源/目标 ROI 无交集 |
| `HGPP_WRONG_INTERSECTION_QUAD_WARNING` | 四边形与源/目标 ROI 无交集 |
| `HGPP_DOUBLE_SIZE_WARNING` | 图像大小不是 2 的倍数（422/411/420 采样） |
| `HGPP_MISALIGNED_DST_ROI_WARNING` | 非合并内存访问导致速度降低 |

### 2.8. 其他枚举
#### 2.8.1. HgppiBayerGridPosition （Bayer 网格位置）
| 枚举值 | 说明 |
|--------|------|
| `HGPPI_BAYER_BGGR` | 默认注册位置 BGGR |
| `HGPPI_BAYER_RGGB` | 注册位置 RGGB |
| `HGPPI_BAYER_GBRG` | 注册位置 GBRG |
| `HGPPI_BAYER_GRBG` | 注册位置 GRBG |

#### 2.8.2. HgppiMaskSize （固定滤波器核大小）
| 枚举值 | 掩码尺寸 |
|--------|----------|
| `HGPP_MASK_SIZE_1_X_3` | 1×3 |
| `HGPP_MASK_SIZE_1_X_5` | 1×5 |
| `HGPP_MASK_SIZE_3_X_1` | 3×1 |
| `HGPP_MASK_SIZE_5_X_1` | 5×1 |
| `HGPP_MASK_SIZE_3_X_3` | 3×3 |
| `HGPP_MASK_SIZE_5_X_5` | 5×5 |
| `HGPP_MASK_SIZE_7_X_7` | 7×7 |
| `HGPP_MASK_SIZE_9_X_9` | 9×9 |
| `HGPP_MASK_SIZE_11_X_11` | 11×11 |
| `HGPP_MASK_SIZE_13_X_13` | 13×13 |
| `HGPP_MASK_SIZE_15_X_15` | 15×15 |

#### 2.8.3. HgppiDifferentialKernel （微分滤波器类型）
| 枚举值 | 说明 |
|--------|------|
| `HGPP_FILTER_SOBEL` | Sobel 微分核 |
| `HGPP_FILTER_SCHARR` | Scharr 微分核 |

#### 2.8.4. HgppCmpOp （像素比较操作）
| 枚举值 | 说明 |
|--------|------|
| `HGPP_CMP_LESS` | 小于阈值 |
| `HGPP_CMP_LESS_EQ` | 小于或等于阈值 |
| `HGPP_CMP_EQ` | 等于阈值 |
| `HGPP_CMP_GREATER_EQ` | 大于或等于阈值 |
| `HGPP_CMP_GREATER` | 大于阈值 |

#### 2.8.5. HgppiAlphaOp （Alpha 合成模式）
| 枚举值 | 说明 |
|--------|------|
| `HGPPI_OP_ALPHA_OVER` | Alpha over 操作 |
| `HGPPI_OP_ALPHA_IN` | Alpha in 操作 |
| `HGPPI_OP_ALPHA_OUT` | Alpha out 操作 |
| `HGPPI_OP_ALPHA_ATOP` | Alpha atop 操作 |
| `HGPPI_OP_ALPHA_XOR` | Alpha xor 操作 |
| `HGPPI_OP_ALPHA_PLUS` | Alpha plus 操作 |
| `*_PREMUL` 变体 | 预乘 Alpha 版本 |

#### 2.8.6. HgppHintAlgorithm （算法提示）
| 枚举值 | 说明 |
|--------|------|
| `HGPP_ALG_HINT_NONE` | 无提示 |
| `HGPP_ALG_HINT_FAST` | 快速提示（目前被忽略） |
| `HGPP_ALG_HINT_ACCURATE` | 精确提示（目前被忽略） |

### 2.9. 批处理结构
#### 2.9.1. HgppiResizeBatchCXR
批量 Resize 操作的数据结构。

| 成员 | 类型 | 说明 |
|------|------|------|
| `pSrc` | const void* | 源图像设备内存指针 |
| `nSrcStep` | int | 源图像每行字节数 |
| `pDst` | void* | 目标图像设备内存指针 |
| `nDstStep` | int | 目标图像每行字节数 |

#### 2.9.2. HgppiResizeBatchROI_Advanced
可变 ROI 图像批量缩放的数据结构。

| 成员 | 类型 | 说明 |
|------|------|------|
| `oSrcRectROI` | HgppiRect | 每个源图像的矩形参数 |
| `oDstRectROI` | HgppiRect | 每个目标图像的矩形参数 |

#### 2.9.3. HgppiMirrorBatchCXR
批量 Mirror 操作的数据结构。

| 成员 | 类型 | 说明 |
|------|------|------|
| `pSrc` | const void* | 源图像设备内存指针 |
| `nSrcStep` | int | 源图像每行字节数 |
| `pDst` | void* | 目标图像设备内存指针 |
| `nDstStep` | int | 目标图像每行字节数 |

#### 2.9.4. HgppiWarpAffineBatchCXR
批量仿射变换的数据结构。

| 成员 | 类型 | 说明 |
|------|------|------|
| `pSrc` | const void* | 源图像设备内存指针 |
| `nSrcStep` | int | 源图像每行字节数 |
| `pDst` | void* | 目标图像设备内存指针 |
| `nDstStep` | int | 目标图像每行字节数 |
| `pCoeffs` | Hgpp64f* | 变换系数矩阵（设备内存） |
| `aTransformedCoeffs` | Hgpp64f[2][3] | 内部使用，勿初始化 |

#### 2.9.5. HgppiWarpPerspectiveBatchCXR
批量透视变换的数据结构。

| 成员 | 类型 | 说明 |
|------|------|------|
| `pSrc` | const void* | 源图像设备内存指针 |
| `nSrcStep` | int | 源图像每行字节数 |
| `pDst` | void* | 目标图像设备内存指针 |
| `nDstStep` | int | 目标图像每行字节数 |
| `pCoeffs` | Hgpp64f* | 变换系数矩阵（设备内存） |
| `aTransformedCoeffs` | Hgpp64f[3][3] | 内部使用，勿初始化 |

#### 2.9.6. HgppiColorTwistBatchCXR
批量颜色扭曲的数据结构。

| 成员 | 类型 | 说明 |
|------|------|------|
| `pSrc` | const void* | 源图像设备内存指针 |
| `nSrcStep` | int | 源图像每行字节数 |
| `pDst` | void* | 目标图像设备内存指针 |
| `nDstStep` | int | 目标图像每行字节数 |
| `pTwist` | Hgpp32f* | 颜色扭曲系数矩阵（设备内存） |

### 2.10. 其他结构
#### 2.10.1. HgppLibraryVersion
HGPP 库版本信息。

| 成员 | 类型 | 说明 |
|------|------|------|
| `major` | int | 主版本号 |
| `minor` | int | 次版本号 |
| `build` | int | 构建号（基于夜间构建） |

#### 2.10.2. HgppStreamContext
应用程序管理流上下文。

| 成员 | 类型 | 说明 |
|------|------|------|
| `hStream` | hggcStream_t | HGGC 流 ID |
| `nHggcDeviceId` | int | HGGC 设备 ID |
| `nMultiProcessorCount` | int | 多处理器数量 |
| `nMaxThreadsPerMultiProcessor` | int | 每多处理器最大线程数 |
| `nMaxThreadsPerBlock` | int | 每块最大线程数 |
| `nSharedMemPerBlock` | size_t | 每块共享内存大小 |
| `nHggcDevAttrComputeCapabilityMajor` | int | 计算能力主版本 |
| `nHggcDevAttrComputeCapabilityMinor` | int | 计算能力次版本 |
| `nStreamFlags` | unsigned int | 流标志 |

#### 2.10.3. HgppiHOGConfig
HOG 描述符配置参数。

| 成员 | 类型 | 说明 |
|------|------|------|
| `cellSize` | int | 方形单元格大小（像素） |
| `histogramBlockSize` | int | 方形直方图块大小（像素） |
| `nHistogramBins` | int | 直方图分组数 |
| `detectionWindowSize` | HgppiSize | 检测窗口大小（像素） |

#### 2.10.4. HgppiConnectedRegion
连通像素区域信息。

| 成员 | 类型 | 说明 |
|------|------|------|
| `oBoundingBox` | HgppiRect | 边界框 (左，上，右，下) |
| `nConnectedPixelCount` | Hgpp32u | 连通区域总像素数 |
| `aSeedPixelValue` | Hgpp32u[3] | 种子像素原始值（1 或 3 通道） |

## 3. 辅助函数
### 3.1. hgppGetLibVersion
获取 HGPP 库版本信息。

**返回值**: `HgppLibraryVersion` 结构体，包含：
- `major`: 主版本号
- `minor`: 次版本号
- `build`: 构建号

## 4. 内存管理函数
用于分配和释放带步幅的图像存储的例程。

### 4.1. 内存分配与步幅
**步幅（Step/Stride）** 是一行中**包括填充在内的**字节数。行填充允许奇数大小图像的行在对齐良好的地址上开始，优化内存访问模式。

**注意**：
- 这些分配器返回的内存行步幅已针对性能优化。
- 使用这些分配器**非强制性**，任何有效的 HGGC 设备内存指针都可被 HGPP 接口使用。
- 缺少填充可能导致与正确填充的图像相比性能严重下降。
- 分配失败时返回 `0`（内存不足或碎片化）。

### 4.2. 内存分配函数族
以下函数按数据类型和通道数分组，所有函数具有相同的参数结构：

#### 4.2.1. 通用参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `nWidthPixels` | int | 图像宽度（像素） |
| `nHeightPixels` | int | 图像高度（像素） |
| `pStepBytes` | int* | 输出参数：行步幅（字节） |

**返回值**: 指向新图像数据的指针（失败时返回 0）。

#### 4.2.2. 函数列表（按数据类型分组）
##### 4.2.2.1. 8 位无符号整数（HGpp8u）
```c
HGpp8u* hgppiMalloc_8u_C1(...)   // 单通道
HGpp8u* hgppiMalloc_8u_C2(...)   // 2 通道
HGpp8u* hgppiMalloc_8u_C3(...)   // 3 通道
HGpp8u* hgppiMalloc_8u_C4(...)   // 4 通道
```

##### 4.2.2.2. 16 位无符号整数（Hgpp16u）
```c
Hgpp16u* hgppiMalloc_16u_C1(...)
Hgpp16u* hgppiMalloc_16u_C2(...)
Hgpp16u* hgppiMalloc_16u_C3(...)
Hgpp16u* hgppiMalloc_16u_C4(...)
```

##### 4.2.2.3. 16 位有符号整数（Hgpp16s）
```c
Hgpp16s* hgppiMalloc_16s_C1(...)
Hgpp16s* hgppiMalloc_16s_C2(...)
Hgpp16s* hgppiMalloc_16s_C4(...)   // 注意：无 C3
```

##### 4.2.2.4. 16 位有符号复数（Hgpp16sc）
```c
Hgpp16sc* hgppiMalloc_16sc_C1(...)
Hgpp16sc* hgppiMalloc_16sc_C2(...)
Hgpp16sc* hgppiMalloc_16sc_C3(...)
Hgpp16sc* hgppiMalloc_16sc_C4(...)
```

##### 4.2.2.5. 32 位有符号整数（Hgpp32s）
```c
Hgpp32s* hgppiMalloc_32s_C1(...)
Hgpp32s* hgppiMalloc_32s_C3(...)
Hgpp32s* hgppiMalloc_32s_C4(...)
```

##### 4.2.2.6. 32 位整数复数（Hgpp32sc）
```c
Hgpp32sc* hgppiMalloc_32sc_C1(...)
Hgpp32sc* hgppiMalloc_32sc_C2(...)
Hgpp32sc* hgppiMalloc_32sc_C3(...)
Hgpp32sc* hgppiMalloc_32sc_C4(...)
```

##### 4.2.2.7. 32 位浮点数（Hgpp32f）
```c
Hgpp32f* hgppiMalloc_32f_C1(...)
Hgpp32f* hgppiMalloc_32f_C2(...)
Hgpp32f* hgppiMalloc_32f_C3(...)
Hgpp32f* hgppiMalloc_32f_C4(...)
```

##### 4.2.2.8. 32 位浮点复数（Hgpp32fc）
```c
Hgpp32fc* hgppiMalloc_32fc_C1(...)
Hgpp32fc* hgppiMalloc_32fc_C2(...)
Hgpp32fc* hgppiMalloc_32fc_C3(...)
Hgpp32fc* hgppiMalloc_32fc_C4(...)
```

### 4.3. 内存释放函数
#### 4.3.1. hgppiFree
释放使用 hgppiMalloc 系列函数分配的内存。

**参数**:
| 参数 | 说明 |
|------|------|
| `pData` | 使用 hgppiMalloc_<modifier> 分配的内存指针 |

> **注意：**
> 必须使用 `hgppiFree` 释放，**不能**使用 `hggcFree`。

### 4.4. 使用说明
#### 4.4.1. 内存分配示例
```c
int nStep;
HGpp8u* pImage = hgppiMalloc_8u_C3(width, height, &nStep);
if (pImage == 0) {
    // 内存分配失败
}
// ... 使用图像 ...
hgppiFree(pImage);
```

#### 4.4.2. 注意事项
1. **分配失败**: 所有分配器返回 `0` 表示失败（内存不足或碎片化）。
2. **性能优化**: 返回的行步幅已针对性能优化。
3. **自定义指针**: 可以使用自定义 HGGC 设备指针，不一定使用 HGPP 分配器。
4. **释放内存**: 必须使用 `hgppiFree`，不能使用 `hggcFree`。

比赛关联：`hgppiMalloc_*` 返回按性能优化过的行步幅，且任何 HGGC 设备指针都可直接喂给 HGPP——预处理缓冲区可在多次推理间复用，避免每帧分配/拷贝，直接省显存和 H2D 传输时间。

## 5. 算术和逻辑运算
函数位于 `hgppial` 库中。
同类函数没有全部列出，完整函数定义请参考头文件 `hgppial.h`。

### 5.1. 算术运算
#### 5.1.1. 功能介绍
算术运算函数对图像执行基本的数学运算，包括加法、减法、乘法、除法、平方、平方根、指数、对数等。所有运算都支持饱和处理，防止溢出。

> **注意：**
> 如果使用**设备常量版本**的函数（如 `AddDeviceC`、`MulDeviceC` 等），且生成该设备常量的函数在前，**必须**在调用设备常量函数之前调用 `hggcStreamSynchronize()` 或 `hggcDeviceSynchronize()`。

#### 5.1.2. 完整参数说明
##### 5.1.2.1. Add / AddC 通用参数（加法）
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc1` | 设备指针 | [in] | **源图像指针** - 第一个输入图像 |
| `nSrc1Step` | int | [in] | **源图像行步幅**（字节），必须 ≥ 0 |
| `pSrc2` | 设备指针 | [in] | **源图像指针** - 第二个输入图像（图像加法使用） |
| `nSrc2Step` | int | [in] | **源图像行步幅**（字节） |
| `nConstant` / `aConstants[]` | 数据类型 | [in] | **常数值** - 主机内存常量（单通道用 `nConstant`，多通道用 `aConstants` 数组，每个通道一个值） |
| `pConstant` / `pConstants` | 设备指针 | [in] | **设备常量指针** - 指向设备内存中的常量值 |
| `pDst` | 设备指针 | [out] | **目标图像指针** - 输出图像 |
| `nDstStep` | int | [in] | **目标图像行步幅**（字节），必须 ≥ 0 |
| `pSrcDst` | 设备指针 | [in,out] | **原图像操作指针** - 输入输出为同一地址 |
| `nSrcDstStep` | int | [in] | **原图像操作行步幅**（字节） |
| `oSizeROI` | HgppiSize | [in] | **感兴趣区域** - ROI 宽度和高度（像素），必须 > 0 |
| `nScaleFactor` | int | [in] | **整数结果缩放因子** - 结果乘以 2^(-nScaleFactor)，用于防止溢出，通常设为 0 表示不缩放 |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** - 应用程序管理的 HGGC 流上下文 |

**运算公式：**
- **AddC （加常数）：** $\text{dstPixel} = \text{sat}((\text{srcPixel} + \text{constant}) \times 2^{-\text{scaleFactor}})$。
- **Add （图像加法）：** $\text{dstPixel} = \text{sat}((\text{src1Pixel} + \text{src2Pixel}) \times 2^{-\text{scaleFactor}})$。

**返回值：** `HgppStatus` - 图像数据相关错误码、 ROI 相关错误码。

**错误码说明：**
- `HGPP_NULL_POINTER_ERROR` - pSrc、 pDst 或关键参数指针为 NULL。
- `HGPP_STEP_ERROR` - nSrcStep 或 nDstStep ≤ 0。
- `HGPP_SIZE_ERROR` - oSizeROI 宽度或高度 < 0。
- `HGPP_OVERFLOW_ERROR` - 结果溢出数据类型的表示范围。

##### 5.1.2.2. Sub / SubC 通用参数（减法）
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc1` | 设备指针 | [in] | **源图像指针** - 被减数图像 |
| `nSrc1Step` | int | [in] | **源图像行步幅** |
| `pSrc2` | 设备指针 | [in] | **源图像指针** - 减数图像 |
| `nSrc2Step` | int | [in] | **源图像行步幅** |
| `nConstant` / `aConstants[]` | 数据类型 | [in] | **常数值** - 减数 |
| `pConstant` / `pConstants` | 设备指针 | [in] | **设备常量指针** |
| `pDst` | 设备指针 | [out] | **目标图像指针** |
| `nDstStep` | int | [in] | **目标图像行步幅** |
| `pSrcDst` | 设备指针 | [in,out] | **图像指针** |
| `nSrcDstStep` | int | [in] | **图像行步幅** |
| `oSizeROI` | HgppiSize | [in] | **感兴趣区域** |
| `nScaleFactor` | int | [in] | **整数结果缩放因子** |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

**运算公式：**
- **SubC （减常数）：** $\text{dstPixel} = \text{sat}((\text{srcPixel} - \text{constant}) \times 2^{-\text{scaleFactor}})$。
- **Sub （图像减法）：** $\text{dstPixel} = \text{sat}((\text{src1Pixel} - \text{src2Pixel}) \times 2^{-\text{scaleFactor}})$。

##### 5.1.2.3. Mul / MulC 通用参数（乘法）
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc1` | 设备指针 | [in] | **源图像指针** |
| `nSrc1Step` | int | [in] | **源图像行步幅** |
| `pSrc2` | 设备指针 | [in] | **源图像指针**（图像乘法使用） |
| `nSrc2Step` | int | [in] | **源图像行步幅** |
| `nConstant` / `aConstants[]` | 数据类型 | [in] | **常数值** |
| `pConstant` / `pConstants` | 设备指针 | [in] | **设备常量指针** |
| `pDst` | 设备指针 | [out] | **目标图像指针** |
| `nDstStep` | int | [in] | **目标图像行步幅** |
| `pSrcDst` | 设备指针 | [in,out] | **图像指针** |
| `nSrcDstStep` | int | [in] | **图像行步幅** |
| `oSizeROI` | HgppiSize | [in] | **感兴趣区域** |
| `nScaleFactor` | int | [in] | **整数结果缩放因子** |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

**运算公式：**
- **MulC （乘常数）：** $\text{dstPixel} = \text{sat}((\text{srcPixel} \times \text{constant}) \times 2^{-\text{scaleFactor}})$。
- **Mul （图像乘法）：** $\text{dstPixel} = \text{sat}((\text{src1Pixel} \times \text{src2Pixel}) \times 2^{-\text{scaleFactor}})$。

##### 5.1.2.4. Div / DivC 通用参数（除法）
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc1` | 设备指针 | [in] | **源图像指针** - 被除数图像 |
| `nSrc1Step` | int | [in] | **源图像行步幅** |
| `pSrc2` | 设备指针 | [in] | **源图像指针** - 除数图像 |
| `nSrc2Step` | int | [in] | **源图像行步幅** |
| `nConstant` / `aConstants[]` | 数据类型 | [in] | **常数值** - 除数 |
| `pConstant` / `pConstants` | 设备指针 | [in] | **设备常量指针** |
| `pDst` | 设备指针 | [out] | **目标图像指针** |
| `nDstStep` | int | [in] | **目标图像行步幅** |
| `pSrcDst` | 设备指针 | [in,out] | **图像指针** |
| `nSrcDstStep` | int | [in] | **图像行步幅** |
| `oSizeROI` | HgppiSize | [in] | **感兴趣区域** |
| `nScaleFactor` | int | [in] | **整数结果缩放因子** |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

**运算公式：**
- **DivC （除常数）：** $\text{dstPixel} = \text{sat}((\text{srcPixel} / \text{constant}) \times 2^{-\text{scaleFactor}})$。
- **Div （图像除法）：** $\text{dstPixel} = \text{sat}((\text{src1Pixel} / \text{src2Pixel}) \times 2^{-\text{scaleFactor}})$。

> **注意：**
> 除数为零时结果未定义，可能导致错误。

#### 5.1.3. 函数列表
##### 5.1.3.1. 加法运算
**8 位无符号整数**

```c
// 单通道 - 加常数（主机常量）
HgppStatus hgppiAddC_8u_C1RSfs_Ctx(const HGpp8u *pSrc1, int nSrc1Step, const HGpp8u nConstant,
                                    HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                    int nScaleFactor, HgppStreamContext hgppStreamCtx)

// 单通道 - 加常数（设备常量）注意：需要 hggcStreamSynchronize
HgppStatus hgppiAddDeviceC_8u_C1RSfs_Ctx(const HGpp8u *pSrc1, int nSrc1Step, const HGpp8u *pConstant,
                                          HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                          int nScaleFactor, HgppStreamContext hgppStreamCtx)

// 单通道 - 原图像加常数（主机常量）
HgppStatus hgppiAddC_8u_C1IRSfs_Ctx(const HGpp8u nConstant, HGpp8u *pSrcDst, int nSrcDstStep,
                                     HgppiSize oSizeROI, int nScaleFactor, HgppStreamContext hgppStreamCtx)

// 单通道 - 原图像加常数（设备常量）注意：需要 hggcStreamSynchronize
HgppStatus hgppiAddDeviceC_8u_C1IRSfs_Ctx(const HGpp8u *pConstant, HGpp8u *pSrcDst, int nSrcDstStep,
                                           HgppiSize oSizeROI, int nScaleFactor, HgppStreamContext hgppStreamCtx)

// 三通道 - 加常数（每通道一个值）
HgppStatus hgppiAddC_8u_C3RSfs_Ctx(const HGpp8u *pSrc1, int nSrc1Step, const HGpp8u aConstants[3],
                                    HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                    int nScaleFactor, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiAddDeviceC_8u_C3RSfs_Ctx(...)
HgppStatus hgppiAddC_8u_C3IRSfs_Ctx(const HGpp8u aConstants[3], HGpp8u *pSrcDst, int nSrcDstStep,
                                     HgppiSize oSizeROI, int nScaleFactor, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiAddDeviceC_8u_C3IRSfs_Ctx(...)

// 四通道（忽略 Alpha）
HgppStatus hgppiAddC_8u_AC4RSfs_Ctx(...)
HgppStatus hgppiAddDeviceC_8u_AC4RSfs_Ctx(...)
HgppStatus hgppiAddC_8u_AC4IRSfs_Ctx(...)
HgppStatus hgppiAddDeviceC_8u_AC4IRSfs_Ctx(...)

// 四通道
HgppStatus hgppiAddC_8u_C4RSfs_Ctx(const HGpp8u *pSrc1, int nSrc1Step, const HGpp8u aConstants[4],
                                    HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                    int nScaleFactor, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiAddDeviceC_8u_C4RSfs_Ctx(...)
HgppStatus hgppiAddC_8u_C4IRSfs_Ctx(...)
HgppStatus hgppiAddDeviceC_8u_C4IRSfs_Ctx(...)

// 图像加法（两幅图像相加）
HgppStatus hgppiAdd_8u_C1RSfs_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                   const HGpp8u *pSrc2, int nSrc2Step,
                                   HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                   int nScaleFactor, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiAdd_8u_C1IRSfs_Ctx(...)
HgppStatus hgppiAdd_8u_C3RSfs_Ctx(...)
HgppStatus hgppiAdd_8u_AC4RSfs_Ctx(...)
HgppStatus hgppiAdd_8u_C4RSfs_Ctx(...)
```

**16 位无符号/有符号整数**

```c
// 16 位无符号
HgppStatus hgppiAddC_16u_C1RSfs_Ctx(...)
HgppStatus hgppiAddDeviceC_16u_C1RSfs_Ctx(...)
HgppStatus hgppiAddC_16u_C3RSfs_Ctx(...)
HgppStatus hgppiAddC_16u_AC4RSfs_Ctx(...)
HgppStatus hgppiAddC_16u_C4RSfs_Ctx(...)
HgppStatus hgppiAdd_16u_C1RSfs_Ctx(...)
HgppStatus hgppiAdd_16u_C3RSfs_Ctx(...)
HgppStatus hgppiAdd_16u_AC4RSfs_Ctx(...)
HgppStatus hgppiAdd_16u_C4RSfs_Ctx(...)

// 16 位有符号
HgppStatus hgppiAddC_16s_C1RSfs_Ctx(...)
HgppStatus hgppiAddDeviceC_16s_C1RSfs_Ctx(...)
HgppStatus hgppiAddC_16s_C3RSfs_Ctx(...)
HgppStatus hgppiAddC_16s_AC4RSfs_Ctx(...)
HgppStatus hgppiAddC_16s_C4RSfs_Ctx(...)
HgppStatus hgppiAdd_16s_C1RSfs_Ctx(...)
HgppStatus hgppiAdd_16s_C3RSfs_Ctx(...)
HgppStatus hgppiAdd_16s_AC4RSfs_Ctx(...)
HgppStatus hgppiAdd_16s_C4RSfs_Ctx(...)
```

**32 位有符号整数**

```c
HgppStatus hgppiAddC_32s_C1RSfs_Ctx(...)
HgppStatus hgppiAddDeviceC_32s_C1RSfs_Ctx(...)
HgppStatus hgppiAddC_32s_C3RSfs_Ctx(...)
HgppStatus hgppiAddC_32s_C4RSfs_Ctx(...)
HgppStatus hgppiAdd_32s_C1RSfs_Ctx(...)
HgppStatus hgppiAdd_32s_C3RSfs_Ctx(...)
HgppStatus hgppiAdd_32s_C4RSfs_Ctx(...)
```

**32 位浮点数（无缩放）**

```c
HgppStatus hgppiAddC_32f_C1R_Ctx(const Hgpp32f *pSrc1, int nSrc1Step, const Hgpp32f nConstant,
                                  Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI,
                                  HgppStreamContext hgppStreamCtx)
HgppStatus hgppiAddDeviceC_32f_C1R_Ctx(...)
HgppStatus hgppiAddC_32f_C3R_Ctx(...)
HgppStatus hgppiAddDeviceC_32f_C3R_Ctx(...)
HgppStatus hgppiAddC_32f_C4R_Ctx(...)
HgppStatus hgppiAddDeviceC_32f_C4R_Ctx(...)
HgppStatus hgppiAdd_32f_C1R_Ctx(...)
HgppStatus hgppiAdd_32f_C3R_Ctx(...)
HgppStatus hgppiAdd_32f_C4R_Ctx(...)
```

##### 5.1.3.2. 加法组合运算（AddProduct / AddWeighted / AddSquare）

> **提示：**
> 这些是加法的组合运算，将乘法/平方/加权与加法组合在单个函数中，提高效率。

**AddProduct （乘法后加法）**

```c
// 运算公式：dstPixel = sat(src1Pixel × src2Pixel + src3Pixel)

// 8 位无符号版本
HgppStatus hgppiAddProduct_8u_C1RSfs_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                          const HGpp8u *pSrc2, int nSrc2Step,
                                          const HGpp8u *pSrc3, int nSrc3Step,
                                          HGpp8u *pDst, int nDstStep,
                                          HgppiSize oSizeROI,
                                          int nScaleFactor,
                                          HgppStreamContext hgppStreamCtx)

HgppStatus hgppiAddProduct_8u_C3RSfs_Ctx(...)

// 16 位无符号版本
HgppStatus hgppiAddProduct_16u_C1RSfs_Ctx(...)

// 32 位浮点版本
HgppStatus hgppiAddProduct_32f_C1R_Ctx(const Hgpp32f *pSrc1, int nSrc1Step,
                                        const Hgpp32f *pSrc2, int nSrc2Step,
                                        const Hgpp32f *pSrc3, int nSrc3Step,
                                        Hgpp32f *pDst, int nDstStep,
                                        HgppiSize oSizeROI,
                                        HgppStreamContext hgppStreamCtx)
```

**AddWeighted （加权加法）**

```c
// 运算公式：dstPixel = sat(src1Pixel × weight1 + src2Pixel × weight2)

// 8 位无符号版本
HgppStatus hgppiAddWeighted_8u_C1RSfs_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                           const HGpp8u nWeight1,
                                           const HGpp8u *pSrc2, int nSrc2Step,
                                           const HGpp8u nWeight2,
                                           HGpp8u *pDst, int nDstStep,
                                           HgppiSize oSizeROI,
                                           int nScaleFactor,
                                           HgppStreamContext hgppStreamCtx)

HgppStatus hgppiAddWeighted_8u_C3RSfs_Ctx(...)

// 16 位/32 位版本
HgppStatus hgppiAddWeighted_16u_C1RSfs_Ctx(...)
HgppStatus hgppiAddWeighted_32f_C1R_Ctx(...)
```

**AddSquare （平方后加法）**

```c
// 运算公式：dstPixel = sat(src1Pixel² + src2Pixel²)

// 8 位无符号版本
HgppStatus hgppiAddSquare_8u_C1RSfs_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                         const HGpp8u *pSrc2, int nSrc2Step,
                                         HGpp8u *pDst, int nDstStep,
                                         HgppiSize oSizeROI,
                                         int nScaleFactor,
                                         HgppStreamContext hgppStreamCtx)

HgppStatus hgppiAddSquare_8u_C3RSfs_Ctx(...)

// 16 位/32 位版本
HgppStatus hgppiAddSquare_16u_C1RSfs_Ctx(...)
HgppStatus hgppiAddSquare_32f_C1R_Ctx(...)
```

> **提示：**
> - **AddProduct**：矩阵乘法、滤波运算。
> - **AddWeighted**：图像混合、 alpha 混合、淡入淡出。
> - **AddSquare**：梯度幅值计算、能量计算。

> **注意：**
> 本章仅列出常用的加法函数变体。完整的加法函数系列包括：
> - **Add/AddC**： 62+63=125 个函数（8u/8s/16u/16s/16sc/32u/32s/32sc/32f/32fc/64f， C1/C2/C3/C4/AC4 等）
> - **AddDeviceC**： 42 个函数（设备常量版本）
> - **AddProduct**： 7 个函数。
> - **AddWeighted**： 6 个函数。
> - **AddSquare**： 6 个函数。
> - 完整的 GetBufferHostSize 变体。

**请参考头文件 `hgppial.h` 获取完整的函数列表。**

##### 5.1.3.3. 减法运算
**8 位无符号整数**

```c
// 减常数
HgppStatus hgppiSubC_8u_C1RSfs_Ctx(const HGpp8u *pSrc1, int nSrc1Step, const HGpp8u nConstant,
                                    HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                    int nScaleFactor, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSubC_8u_C1IRSfs_Ctx(...)
HgppStatus hgppiSubC_8u_C3RSfs_Ctx(...)
HgppStatus hgppiSubC_8u_AC4RSfs_Ctx(...)
HgppStatus hgppiSubC_8u_C4RSfs_Ctx(...)

// 图像减法
HgppStatus hgppiSub_8u_C1RSfs_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                   const HGpp8u *pSrc2, int nSrc2Step,
                                   HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                   int nScaleFactor, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSub_8u_C1IRSfs_Ctx(...)
HgppStatus hgppiSub_8u_C3RSfs_Ctx(...)
HgppStatus hgppiSub_8u_AC4RSfs_Ctx(...)
HgppStatus hgppiSub_8u_C4RSfs_Ctx(...)
```

**16 位/32 位**

```c
// 16 位无符号/有符号
HgppStatus hgppiSubC_16u_C1RSfs_Ctx(...)
HgppStatus hgppiSubC_16s_C1RSfs_Ctx(...)
HgppStatus hgppiSubC_16u_C3RSfs_Ctx(...)
HgppStatus hgppiSubC_16s_C3RSfs_Ctx(...)
HgppStatus hgppiSub_16u_C1RSfs_Ctx(...)
HgppStatus hgppiSub_16s_C1RSfs_Ctx(...)

// 32 位有符号
HgppStatus hgppiSubC_32s_C1RSfs_Ctx(...)
HgppStatus hgppiSubC_32s_C3RSfs_Ctx(...)
HgppStatus hgppiSubC_32s_C4RSfs_Ctx(...)
HgppStatus hgppiSub_32s_C1RSfs_Ctx(...)

// 32 位浮点
HgppStatus hgppiSubC_32f_C1R_Ctx(...)
HgppStatus hgppiSubC_32f_C3R_Ctx(...)
HgppStatus hgppiSubC_32f_C4R_Ctx(...)
HgppStatus hgppiSub_32f_C1R_Ctx(...)
```

##### 5.1.3.4. 乘法运算
**8 位无符号整数**

```c
// 乘常数
HgppStatus hgppiMulC_8u_C1RSfs_Ctx(const HGpp8u *pSrc1, int nSrc1Step, const HGpp8u nConstant,
                                    HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                    int nScaleFactor, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiMulDeviceC_8u_C1RSfs_Ctx(...)  // 注意：设备常量需要 hggcStreamSynchronize
HgppStatus hgppiMulC_8u_C1IRSfs_Ctx(...)
HgppStatus hgppiMulDeviceC_8u_C1IRSfs_Ctx(...)
HgppStatus hgppiMulC_8u_C3RSfs_Ctx(...)
HgppStatus hgppiMulC_8u_AC4RSfs_Ctx(...)
HgppStatus hgppiMulC_8u_C4RSfs_Ctx(...)

// 图像乘法
HgppStatus hgppiMul_8u_C1RSfs_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                   const HGpp8u *pSrc2, int nSrc2Step,
                                   HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                   int nScaleFactor, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiMul_8u_C1IRSfs_Ctx(...)
HgppStatus hgppiMul_8u_C3RSfs_Ctx(...)
```

**16 位无符号/有符号/复数**

```c
// 16 位无符号
HgppStatus hgppiMulC_16u_C1RSfs_Ctx(...)
HgppStatus hgppiMulC_16u_C3RSfs_Ctx(...)
HgppStatus hgppiMulC_16u_AC4RSfs_Ctx(...)
HgppStatus hgppiMulC_16u_C4RSfs_Ctx(...)
HgppStatus hgppiMul_16u_C1RSfs_Ctx(...)

// 16 位有符号
HgppStatus hgppiMulC_16s_C1RSfs_Ctx(...)
HgppStatus hgppiMulC_16s_C3RSfs_Ctx(...)
HgppStatus hgppiMulC_16s_AC4RSfs_Ctx(...)
HgppStatus hgppiMulC_16s_C4RSfs_Ctx(...)
HgppStatus hgppiMul_16s_C1RSfs_Ctx(...)

// 16 位复数
HgppStatus hgppiMulC_16sc_C1RSfs_Ctx(...)  // 16 位复数单通道
HgppStatus hgppiMulC_16sc_C3RSfs_Ctx(...)  // 16 位复数三通道
```

**32 位有符号/复数**

```c
// 32 位有符号
HgppStatus hgppiMulC_32s_C1RSfs_Ctx(...)
HgppStatus hgppiMulC_32s_C3RSfs_Ctx(...)
HgppStatus hgppiMulC_32s_C4RSfs_Ctx(...)
HgppStatus hgppiMul_32s_C1RSfs_Ctx(...)

// 32 位复数
HgppStatus hgppiMulC_32sc_C1RSfs_Ctx(...)  // 32 位复数单通道
HgppStatus hgppiMulC_32sc_C3RSfs_Ctx(...)  // 32 位复数三通道
```

**16 位浮点数**

```c
HgppStatus hgppiMulC_16f_C1R_Ctx(const Hgpp16f *pSrc1, int nSrc1Step, const Hgpp32f nConstant,
                                  Hgpp16f *pDst, int nDstStep, HgppiSize oSizeROI,
                                  HgppStreamContext hgppStreamCtx)
HgppStatus hgppiMulDeviceC_16f_C1R_Ctx(...)  // 注意：设备常量需要 hggcStreamSynchronize
HgppStatus hgppiMulC_16f_C1IR_Ctx(...)
HgppStatus hgppiMulDeviceC_16f_C1IR_Ctx(...)
HgppStatus hgppiMulC_16f_C3R_Ctx(...)
HgppStatus hgppiMulDeviceC_16f_C3R_Ctx(...)
HgppStatus hgppiMulC_16f_C3IR_Ctx(...)
HgppStatus hgppiMulDeviceC_16f_C3IR_Ctx(...)
```

##### 5.1.3.5. 除法运算
**8 位无符号整数**

```c
// 除常数
HgppStatus hgppiDivC_8u_C1RSfs_Ctx(const HGpp8u *pSrc1, int nSrc1Step, const HGpp8u nConstant,
                                    HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                    int nScaleFactor, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiDivC_8u_C1IRSfs_Ctx(...)
HgppStatus hgppiDivC_8u_C3RSfs_Ctx(...)
HgppStatus hgppiDivC_8u_AC4RSfs_Ctx(...)
HgppStatus hgppiDivC_8u_C4RSfs_Ctx(...)

// 图像除法
HgppStatus hgppiDiv_8u_C1RSfs_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                   const HGpp8u *pSrc2, int nSrc2Step,
                                   HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                   int nScaleFactor, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiDiv_8u_C1IRSfs_Ctx(...)
HgppStatus hgppiDiv_8u_C3RSfs_Ctx(...)
```

**16 位/32 位**

```c
// 16 位无符号
HgppStatus hgppiDivC_16u_C1RSfs_Ctx(...)
HgppStatus hgppiDiv_16u_C1RSfs_Ctx(...)

// 32 位有符号
HgppStatus hgppiDivC_32s_C1RSfs_Ctx(...)
HgppStatus hgppiDiv_32s_C1RSfs_Ctx(...)

// 32 位浮点
HgppStatus hgppiDivC_32f_C1R_Ctx(...)
HgppStatus hgppiDiv_32f_C1R_Ctx(...)
```

##### 5.1.3.6. DivRound （带舍入的除法）

> **提示：**
> DivRound 在除法运算后执行舍入操作，而不是简单的截断。适用于需要精确除法结果的场景。

**运算公式：**
- **DivC_Round （除常数 + 舍入）：** $\text{dstPixel} = \text{round}(\text{srcPixel} / \text{constant})$。
- **Div_Round （图像除法 + 舍入）：** $\text{dstPixel} = \text{round}(\text{src1Pixel} / \text{src2Pixel})$。

**8 位无符号版本**

```c
// 除常数 + 舍入
HgppStatus hgppiDivC_Round_8u_C1RSfs_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                          const HGpp8u nConstant,
                                          HGpp8u *pDst, int nDstStep,
                                          HgppiSize oSizeROI,
                                          int nScaleFactor,
                                          HgppStreamContext hgppStreamCtx)

HgppStatus hgppiDivC_Round_8u_C1IRSfs_Ctx(...)
HgppStatus hgppiDivC_Round_8u_C3RSfs_Ctx(...)
HgppStatus hgppiDivC_Round_8u_AC4RSfs_Ctx(...)
HgppStatus hgppiDivC_Round_8u_C4RSfs_Ctx(...)

// 图像除法 + 舍入
HgppStatus hgppiDiv_Round_8u_C1RSfs_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                         const HGpp8u *pSrc2, int nSrc2Step,
                                         HGpp8u *pDst, int nDstStep,
                                         HgppiSize oSizeROI,
                                         int nScaleFactor,
                                         HgppStreamContext hgppStreamCtx)

HgppStatus hgppiDiv_Round_8u_C1IRSfs_Ctx(...)
HgppStatus hgppiDiv_Round_8u_C3RSfs_Ctx(...)
HgppStatus hgppiDiv_Round_8u_AC4RSfs_Ctx(...)
HgppStatus hgppiDiv_Round_8u_C4RSfs_Ctx(...)
```

**16 位无符号版本**

```c
// 除常数 + 舍入
HgppStatus hgppiDivC_Round_16u_C1RSfs_Ctx(const Hgpp16u *pSrc, int nSrcStep,
                                           const Hgpp16u nConstant,
                                           Hgpp16u *pDst, int nDstStep,
                                           HgppiSize oSizeROI,
                                           int nScaleFactor,
                                           HgppStreamContext hgppStreamCtx)

HgppStatus hgppiDivC_Round_16u_C1IRSfs_Ctx(...)
HgppStatus hgppiDivC_Round_16u_C3RSfs_Ctx(...)
HgppStatus hgppiDivC_Round_16u_AC4RSfs_Ctx(...)
HgppStatus hgppiDivC_Round_16u_C4RSfs_Ctx(...)

// 图像除法 + 舍入
HgppStatus hgppiDiv_Round_16u_C1RSfs_Ctx(const Hgpp16u *pSrc1, int nSrc1Step,
                                          const Hgpp16u *pSrc2, int nSrc2Step,
                                          Hgpp16u *pDst, int nDstStep,
                                          HgppiSize oSizeROI,
                                          int nScaleFactor,
                                          HgppStreamContext hgppStreamCtx)

HgppStatus hgppiDiv_Round_16u_C1IRSfs_Ctx(...)
HgppStatus hgppiDiv_Round_16u_C3RSfs_Ctx(...)
HgppStatus hgppiDiv_Round_16u_AC4RSfs_Ctx(...)
HgppStatus hgppiDiv_Round_16u_C4RSfs_Ctx(...)
```

**16 位有符号版本**

```c
// 除常数 + 舍入
HgppStatus hgppiDivC_Round_16s_C1RSfs_Ctx(const Hgpp16s *pSrc, int nSrcStep,
                                           const Hgpp16s nConstant,
                                           Hgpp16s *pDst, int nDstStep,
                                           HgppiSize oSizeROI,
                                           int nScaleFactor,
                                           HgppStreamContext hgppStreamCtx)

HgppStatus hgppiDivC_Round_16s_C1IRSfs_Ctx(...)
HgppStatus hgppiDivC_Round_16s_C3RSfs_Ctx(...)
HgppStatus hgppiDivC_Round_16s_AC4RSfs_Ctx(...)
HgppStatus hgppiDivC_Round_16s_C4RSfs_Ctx(...)

// 图像除法 + 舍入
HgppStatus hgppiDiv_Round_16s_C1RSfs_Ctx(const Hgpp16s *pSrc1, int nSrc1Step,
                                          const Hgpp16s *pSrc2, int nSrc2Step,
                                          Hgpp16s *pDst, int nDstStep,
                                          HgppiSize oSizeROI,
                                          int nScaleFactor,
                                          HgppStreamContext hgppStreamCtx)

HgppStatus hgppiDiv_Round_16s_C1IRSfs_Ctx(...)
HgppStatus hgppiDiv_Round_16s_C3RSfs_Ctx(...)
HgppStatus hgppiDiv_Round_16s_AC4RSfs_Ctx(...)
HgppStatus hgppiDiv_Round_16s_C4RSfs_Ctx(...)
```

> **注意：**
> - DivRound 使用银行家舍入法（四舍六入五成双）。
> - 与标准除法相比， DivRound 提供更精确的结果。
> - 适用于需要保持数值精度的场景，如图像处理中的缩放、归一化。
>
> **Div vs DivRound 对比：**

| 特性 | Div （标准除法） | DivRound （舍入除法） |
|------|----------------|---------------------|
| **舍入方式** | 截断（向零） | 舍入到最近整数 |
| **精度** | 较低 | 更高 |
| **速度** | 更快 | 稍慢 |
| **应用场景** | 一般整数除法 | 需要精确结果的场景 |

##### 5.1.3.7. 乘法缩放（MulScale / MulCScale / MulDeviceCScale）

> **提示：**
> 乘法缩放组合运算，用于防止乘法结果溢出。支持图像×图像、图像×常量、设备常量×图像三种模式。

**MulScale （图像×图像 + 缩放）**

```c
// 8 位无符号版本
HgppStatus hgppiMulScale_8u_C1R_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                     const HGpp8u *pSrc2, int nSrc2Step,
                                     HGpp8u *pDst, int nDstStep,
                                     HgppiSize oSizeROI,
                                     int nScaleFactor,
                                     HgppStreamContext hgppStreamCtx)

HgppStatus hgppiMulScale_8u_C3R_Ctx(...)
HgppStatus hgppiMulScale_8u_C4R_Ctx(...)

// 16 位无符号版本
HgppStatus hgppiMulScale_16u_C1R_Ctx(const Hgpp16u *pSrc1, int nSrc1Step,
                                      const Hgpp16u *pSrc2, int nSrc2Step,
                                      Hgpp16u *pDst, int nDstStep,
                                      HgppiSize oSizeROI,
                                      int nScaleFactor,
                                      HgppStreamContext hgppStreamCtx)

HgppStatus hgppiMulScale_16u_C3R_Ctx(...)
HgppStatus hgppiMulScale_16s_C1R_Ctx(...)
HgppStatus hgppiMulScale_32s_C1R_Ctx(...)

// 32 位浮点版本（无缩放）
HgppStatus hgppiMulScale_32f_C1R_Ctx(const Hgpp32f *pSrc1, int nSrc1Step,
                                      const Hgpp32f *pSrc2, int nSrc2Step,
                                      Hgpp32f *pDst, int nDstStep,
                                      HgppiSize oSizeROI,
                                      HgppStreamContext hgppStreamCtx)

HgppStatus hgppiMulScale_32f_C3R_Ctx(...)
```

**MulCScale （图像×常量 + 缩放）**

```c
// 8 位无符号版本
HgppStatus hgppiMulCScale_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                      const HGpp8u nConstant,
                                      HGpp8u *pDst, int nDstStep,
                                      HgppiSize oSizeROI,
                                      int nScaleFactor,
                                      HgppStreamContext hgppStreamCtx)

HgppStatus hgppiMulCScale_8u_C3R_Ctx(...)
HgppStatus hgppiMulCScale_8u_AC4R_Ctx(...)

// 16 位无符号版本
HgppStatus hgppiMulCScale_16u_C1R_Ctx(const Hgpp16u *pSrc, int nSrcStep,
                                       const Hgpp16u nConstant,
                                       Hgpp16u *pDst, int nDstStep,
                                       HgppiSize oSizeROI,
                                       int nScaleFactor,
                                       HgppStreamContext hgppStreamCtx)

HgppStatus hgppiMulCScale_16u_C3R_Ctx(...)
HgppStatus hgppiMulCScale_16s_C1R_Ctx(...)

// 32 位浮点版本
HgppStatus hgppiMulCScale_32f_C1R_Ctx(const Hgpp32f *pSrc, int nSrcStep,
                                       const Hgpp32f nConstant,
                                       Hgpp32f *pDst, int nDstStep,
                                       HgppiSize oSizeROI,
                                       HgppStreamContext hgppStreamCtx)

HgppStatus hgppiMulCScale_32f_C3R_Ctx(...)
```

**MulDeviceCScale （图像×设备常量 + 缩放）**

```c
// 8 位无符号版本
HgppStatus hgppiMulDeviceCScale_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                            const HGpp8u *pConstant,
                                            HGpp8u *pDst, int nDstStep,
                                            HgppiSize oSizeROI,
                                            int nScaleFactor,
                                            HgppStreamContext hgppStreamCtx)

HgppStatus hgppiMulDeviceCScale_8u_C3R_Ctx(...)

// 16 位/32 位版本
HgppStatus hgppiMulDeviceCScale_16u_C1R_Ctx(...)
HgppStatus hgppiMulDeviceCScale_16s_C1R_Ctx(...)
HgppStatus hgppiMulDeviceCScale_32f_C1R_Ctx(...)
```

**运算公式：**
- **MulScale：** $\text{dstPixel} = \text{sat}(\text{src1Pixel} \times \text{src2Pixel} \times 2^{-\text{scaleFactor}})$。
- **MulCScale：** $\text{dstPixel} = \text{sat}(\text{srcPixel} \times \text{constant} \times 2^{-\text{scaleFactor}})$。
- **MulDeviceCScale：** $\text{dstPixel} = \text{sat}(\text{srcPixel} \times \text{deviceConstant} \times 2^{-\text{scaleFactor}})$。

> **注意：**
> - 设备常量版本需要先创建设备常量，并确保 hggcStreamSynchronize 已调用。
> - 缩放因子用于防止乘法结果溢出，通常设为 0-8。

> **注意：**
> 本章仅列出常用的乘法函数变体。完整的乘法函数系列包括：
> - **Mul/MulC**： 62+63=125 个函数（8u/8s/16u/16s/16sc/32u/32s/32sc/32f/32fc/64f， C1/C2/C3/C4/AC4 等）
> - **MulDeviceC**： 42 个函数（设备常量版本）
> - **MulScale**： 16 个函数。
> - **MulCScale**： 16 个函数。
> - **MulDeviceCScale**： 16 个函数。
> - 完整的 GetBufferHostSize 变体。

**请参考头文件 `hgppial.h` 获取完整的函数列表。**

##### 5.1.3.8. 平方与平方根
**Sqr （平方）**

```c
HgppStatus hgppiSqr_8u_C1RSfs_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                   HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                   int nScaleFactor, HgppStreamContext hgppStreamCtx)
// 运算公式：dstPixel = sat(srcPixel² × 2^(-scaleFactor))

HgppStatus hgppiSqr_16u_C1RSfs_Ctx(...)
HgppStatus hgppiSqr_32s_C1RSfs_Ctx(...)
HgppStatus hgppiSqr_32f_C1R_Ctx(...)  // 32f 无缩放
```

**Sqrt （平方根）**

```c
HgppStatus hgppiSqrt_8u_C1RSfs_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                    HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                    int nScaleFactor, HgppStreamContext hgppStreamCtx)
// 运算公式：dstPixel = √srcPixel × 2^(-scaleFactor)

HgppStatus hgppiSqrt_16u_C1RSfs_Ctx(...)
HgppStatus hgppiSqrt_32f_C1R_Ctx(...)
```

##### 5.1.3.9. 指数对数幂
**Exp （指数）**

```c
HgppStatus hgppiExp_32f_C1R_Ctx(const Hgpp32f *pSrc, int nSrcStep,
                                 Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI,
                                 HgppStreamContext hgppStreamCtx)
// 运算公式：dstPixel = e^srcPixel
```

**Ln （自然对数）**

```c
// 32 位浮点版本
HgppStatus hgppiLn_32f_C1R_Ctx(const Hgpp32f *pSrc, int nSrcStep,
                                Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI,
                                HgppStreamContext hgppStreamCtx)

HgppStatus hgppiLn_32f_C1IR_Ctx(Hgpp32f *pSrcDst, int nSrcDstStep,
                                 HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

HgppStatus hgppiLn_32f_C3R_Ctx(...)
HgppStatus hgppiLn_32f_C3IR_Ctx(...)

// 16 位浮点版本
HgppStatus hgppiLn_16f_C1R_Ctx(const Hgpp16f *pSrc, int nSrcStep,
                                Hgpp16f *pDst, int nDstStep, HgppiSize oSizeROI,
                                HgppStreamContext hgppStreamCtx)

HgppStatus hgppiLn_16f_C1IR_Ctx(...)
HgppStatus hgppiLn_16f_C3R_Ctx(...)
HgppStatus hgppiLn_16f_C3IR_Ctx(...)

// 16 位无符号版本（带缩放）
HgppStatus hgppiLn_16u_C1R_Ctx(const Hgpp16u *pSrc, int nSrcStep,
                                Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI,
                                HgppStreamContext hgppStreamCtx)

HgppStatus hgppiLn_16u_C1IRSfs_Ctx(Hgpp16u *pSrcDst, int nSrcDstStep,
                                    HgppiSize oSizeROI, int nScaleFactor,
                                    HgppStreamContext hgppStreamCtx)

HgppStatus hgppiLn_16u_C3R_Ctx(...)
HgppStatus hgppiLn_16u_C3IRSfs_Ctx(...)

// 16 位有符号版本（带缩放）
HgppStatus hgppiLn_16s_C1R_Ctx(const Hgpp16s *pSrc, int nSrcStep,
                                Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI,
                                HgppStreamContext hgppStreamCtx)

HgppStatus hgppiLn_16s_C1IRSfs_Ctx(...)
HgppStatus hgppiLn_16s_C3R_Ctx(...)
HgppStatus hgppiLn_16s_C3IRSfs_Ctx(...)

// 8 位无符号版本（带缩放）
HgppStatus hgppiLn_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                               HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                               HgppStreamContext hgppStreamCtx)

HgppStatus hgppiLn_8u_C1IRSfs_Ctx(...)
HgppStatus hgppiLn_8u_C3R_Ctx(...)
HgppStatus hgppiLn_8u_C3IRSfs_Ctx(...)
```

**运算公式：** $\text{dstPixel} = \ln(\text{srcPixel})$（自然对数，底数为 e）

> **注意：**
> - srcPixel 必须 > 0 （对数定义域）。
> - 整数版本（8u/16u/16s）支持缩放因子防止溢出。
> - 原图像操作版本（IR）输入输出为同一图像。

> **注意：**
> 本章仅列出常用的指数对数函数变体。完整的指数对数函数系列包括：
> - **Exp （指数）**： 16 个函数（32f， C1/C3/C4/AC4 等）
> - **Ln （自然对数）**： 20 个函数（16f/16u/16s/32f， C1/C3， R/IR，带缩放版本）
> - 完整的 GetBufferHostSize 变体。

**请参考头文件 `hgppial.h` 获取完整的函数列表。**

##### 5.1.3.10. 其他算术运算
**Abs （绝对值）**

```c
HgppStatus hgppiAbs_16s_C1R_Ctx(const Hgpp16s *pSrc, int nSrcStep,
                                 Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI,
                                 HgppStreamContext hgppStreamCtx)
// 运算公式：dstPixel = |srcPixel|

HgppStatus hgppiAbs_32s_C1R_Ctx(...)
```

**AbsDiff （绝对差 - 图像减图像）**

```c
// 8 位无符号版本
HgppStatus hgppiAbsDiff_8u_C1R_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                    const HGpp8u *pSrc2, int nSrc2Step,
                                    HGpp8u *pDst, int nDstStep,
                                    HgppiSize oSizeROI,
                                    HgppStreamContext hgppStreamCtx)

HgppStatus hgppiAbsDiff_8u_C3R_Ctx(...)
HgppStatus hgppiAbsDiff_8u_C4R_Ctx(...)

// 16 位无符号版本
HgppStatus hgppiAbsDiff_16u_C1R_Ctx(const Hgpp16u *pSrc1, int nSrc1Step,
                                     const Hgpp16u *pSrc2, int nSrc2Step,
                                     Hgpp16u *pDst, int nDstStep,
                                     HgppiSize oSizeROI,
                                     HgppStreamContext hgppStreamCtx)

HgppStatus hgppiAbsDiff_16u_C3R_Ctx(...)

// 32 位浮点版本
HgppStatus hgppiAbsDiff_32f_C1R_Ctx(const Hgpp32f *pSrc1, int nSrc1Step,
                                     const Hgpp32f *pSrc2, int nSrc2Step,
                                     Hgpp32f *pDst, int nDstStep,
                                     HgppiSize oSizeROI,
                                     HgppStreamContext hgppStreamCtx)

HgppStatus hgppiAbsDiff_16f_C1R_Ctx(...)
```

**AbsDiffC （绝对差 - 图像减常量）**

```c
// 8 位无符号版本
HgppStatus hgppiAbsDiffC_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                     const HGpp8u nConstant,
                                     HGpp8u *pDst, int nDstStep,
                                     HgppiSize oSizeROI,
                                     HgppStreamContext hgppStreamCtx)

HgppStatus hgppiAbsDiffC_8u_C3R_Ctx(...)

// 16 位无符号版本
HgppStatus hgppiAbsDiffC_16u_C1R_Ctx(const Hgpp16u *pSrc, int nSrcStep,
                                      const Hgpp16u nConstant,
                                      Hgpp16u *pDst, int nDstStep,
                                      HgppiSize oSizeROI,
                                      HgppStreamContext hgppStreamCtx)

// 32 位浮点版本
HgppStatus hgppiAbsDiffC_32f_C1R_Ctx(const Hgpp32f *pSrc, int nSrcStep,
                                      const Hgpp32f nConstant,
                                      Hgpp32f *pDst, int nDstStep,
                                      HgppiSize oSizeROI,
                                      HgppStreamContext hgppStreamCtx)
```

**AbsDiffDeviceC （绝对差 - 图像减设备常量）**

```c
// 8 位无符号版本
HgppStatus hgppiAbsDiffDeviceC_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                           const HGpp8u *pConstant,
                                           HGpp8u *pDst, int nDstStep,
                                           HgppiSize oSizeROI,
                                           HgppStreamContext hgppStreamCtx)

HgppStatus hgppiAbsDiffDeviceC_8u_C3R_Ctx(...)

// 16 位/32 位版本
HgppStatus hgppiAbsDiffDeviceC_16u_C1R_Ctx(...)
HgppStatus hgppiAbsDiffDeviceC_32f_C1R_Ctx(...)
```

**运算公式：**
- **AbsDiff：** $\text{dstPixel} = |\text{src1Pixel} - \text{src2Pixel}|$。
- **AbsDiffC：** $\text{dstPixel} = |\text{srcPixel} - \text{constant}|$。
- **AbsDiffDeviceC：** $\text{dstPixel} = |\text{srcPixel} - \text{deviceConstant}|$。

### 5.2. 逻辑运算
#### 5.2.1. 功能介绍
逻辑运算函数对图像执行位级逻辑操作，包括与 (AND)、或 (OR)、异或 (XOR)、非 (NOT)、左移、右移等。**仅适用于整数类型**。

#### 5.2.2. 完整参数说明
##### 5.2.2.1. And / AndC 通用参数（逻辑与）
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc1` | 设备指针 | [in] | **源图像指针** |
| `nSrc1Step` | int | [in] | **源图像行步幅** |
| `pSrc2` | 设备指针 | [in] | **源图像指针**（图像与运算使用） |
| `nSrc2Step` | int | [in] | **源图像行步幅** |
| `nConstant` / `aConstants[]` | 数据类型 | [in] | **常数值**（单通道用 `nConstant`，多通道用 `aConstants` 数组） |
| `pDst` | 设备指针 | [out] | **目标图像指针** |
| `nDstStep` | int | [in] | **目标图像行步幅** |
| `pSrcDst` | 设备指针 | [in,out] | **图像指针** |
| `nSrcDstStep` | int | [in] | **图像行步幅** |
| `oSizeROI` | HgppiSize | [in] | **感兴趣区域** |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

**运算公式：**
- **AndC （与常数）：** $\text{dstPixel} = \text{srcPixel} \ \& \ \text{constant}$。
- **And （图像与）：** $\text{dstPixel} = \text{src1Pixel} \ \& \ \text{src2Pixel}$。

##### 5.2.2.2. Or / OrC 通用参数（逻辑或）
**运算公式：**
- **OrC （或常数）：** $\text{dstPixel} = \text{srcPixel} \ | \ \text{constant}$。
- **Or （图像或）：** $\text{dstPixel} = \text{src1Pixel} \ | \ \text{src2Pixel}$。

##### 5.2.2.3. Xor / XorC 通用参数（逻辑异或）
**运算公式：**
- **XorC （异或常数）：** $\text{dstPixel} = \text{srcPixel} \ \text{xor} \ \text{constant}$。
- **Xor （图像异或）：** $\text{dstPixel} = \text{src1Pixel} \ \text{xor} \ \text{src2Pixel}$。

##### 5.2.2.4. Not 通用参数（逻辑非）
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | **源图像指针** |
| `nSrcStep` | int | [in] | **源图像行步幅** |
| `pDst` | 设备指针 | [out] | **目标图像指针** |
| `nDstStep` | int | [in] | **目标图像行步幅** |
| `oSizeROI` | HgppiSize | [in] | **感兴趣区域** |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

**运算公式：** $\text{dstPixel} = \sim\text{srcPixel}$（按位取反）

##### 5.2.2.5. Shift 通用参数（移位）
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | **源图像指针** |
| `nSrcStep` | int | [in] | **源图像行步幅** |
| `nConstant` | int | [in] | **移位数** - 正数表示移位位数 |
| `pDst` | 设备指针 | [out] | **目标图像指针** |
| `nDstStep` | int | [in] | **目标图像行步幅** |
| `oSizeROI` | HgppiSize | [in] | **感兴趣区域** |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

**运算公式：**
- **LShiftC （左移）：** $\text{dstPixel} = \text{srcPixel} \ll \text{shift}$。
- **RShiftC （右移）：** $\text{dstPixel} = \text{srcPixel} \gg \text{shift}$。

#### 5.2.3. 函数列表
##### 5.2.3.1. 逻辑与
**8 位无符号整数**

```c
// 与常数 - 单通道
HgppStatus hgppiAndC_8u_C1R_Ctx(const HGpp8u *pSrc1, int nSrc1Step, const HGpp8u nConstant,
                                 HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                 HgppStreamContext hgppStreamCtx)

// 与常数 - 原图像操作单通道
HgppStatus hgppiAndC_8u_C1IR_Ctx(const HGpp8u nConstant, HGpp8u *pSrcDst, int nSrcDstStep,
                                  HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

// 与常数 - 三通道（每通道一个值）
HgppStatus hgppiAndC_8u_C3R_Ctx(const HGpp8u *pSrc1, int nSrc1Step, const HGpp8u aConstants[3],
                                 HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                 HgppStreamContext hgppStreamCtx)
HgppStatus hgppiAndC_8u_C3IR_Ctx(const HGpp8u aConstants[3], HGpp8u *pSrcDst, int nSrcDstStep,
                                  HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

// 与常数 - 四通道（忽略 Alpha）
HgppStatus hgppiAndC_8u_AC4R_Ctx(...)
HgppStatus hgppiAndC_8u_AC4IR_Ctx(...)

// 与常数 - 四通道
HgppStatus hgppiAndC_8u_C4R_Ctx(const HGpp8u *pSrc1, int nSrc1Step, const HGpp8u aConstants[4],
                                 HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                 HgppStreamContext hgppStreamCtx)
HgppStatus hgppiAndC_8u_C4IR_Ctx(...)

// 图像与
HgppStatus hgppiAnd_8u_C1R_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                const HGpp8u *pSrc2, int nSrc2Step,
                                HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                HgppStreamContext hgppStreamCtx)
HgppStatus hgppiAnd_8u_C1IR_Ctx(...)
HgppStatus hgppiAnd_8u_C3R_Ctx(...)
```

**16 位无符号整数**

```c
HgppStatus hgppiAndC_16u_C1R_Ctx(...)
HgppStatus hgppiAndC_16u_C1IR_Ctx(...)
HgppStatus hgppiAndC_16u_C3R_Ctx(...)
HgppStatus hgppiAndC_16u_C3IR_Ctx(...)
HgppStatus hgppiAndC_16u_AC4R_Ctx(...)
HgppStatus hgppiAndC_16u_AC4IR_Ctx(...)
HgppStatus hgppiAndC_16u_C4R_Ctx(...)
HgppStatus hgppiAndC_16u_C4IR_Ctx(...)
HgppStatus hgppiAnd_16u_C1R_Ctx(...)
```

**32 位有符号整数**

```c
HgppStatus hgppiAndC_32s_C1R_Ctx(...)
HgppStatus hgppiAndC_32s_C1IR_Ctx(...)
HgppStatus hgppiAndC_32s_C3R_Ctx(...)
HgppStatus hgppiAndC_32s_C3IR_Ctx(...)
HgppStatus hgppiAndC_32s_AC4R_Ctx(...)
HgppStatus hgppiAndC_32s_AC4IR_Ctx(...)
HgppStatus hgppiAndC_32s_C4R_Ctx(...)
HgppStatus hgppiAndC_32s_C4IR_Ctx(...)
HgppStatus hgppiAnd_32s_C1R_Ctx(...)
```

##### 5.2.3.2. 逻辑或
**8 位无符号整数**

```c
// 或常数
HgppStatus hgppiOrC_8u_C1R_Ctx(const HGpp8u *pSrc1, int nSrc1Step, const HGpp8u nConstant,
                                HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                HgppStreamContext hgppStreamCtx)
HgppStatus hgppiOrC_8u_C1IR_Ctx(...)
HgppStatus hgppiOrC_8u_C3R_Ctx(...)
HgppStatus hgppiOrC_8u_C3IR_Ctx(...)
HgppStatus hgppiOrC_8u_AC4R_Ctx(...)
HgppStatus hgppiOrC_8u_AC4IR_Ctx(...)
HgppStatus hgppiOrC_8u_C4R_Ctx(...)
HgppStatus hgppiOrC_8u_C4IR_Ctx(...)

// 图像或
HgppStatus hgppiOr_8u_C1R_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                               const HGpp8u *pSrc2, int nSrc2Step,
                               HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                               HgppStreamContext hgppStreamCtx)
HgppStatus hgppiOr_8u_C1IR_Ctx(...)
HgppStatus hgppiOr_8u_C3R_Ctx(...)
```

**16 位/32 位**

```c
HgppStatus hgppiOrC_16u_C1R_Ctx(...)
HgppStatus hgppiOrC_32s_C1R_Ctx(...)
HgppStatus hgppiOr_16u_C1R_Ctx(...)
HgppStatus hgppiOr_32s_C1R_Ctx(...)
```

##### 5.2.3.3. 逻辑异或
**8 位无符号整数**

```c
// 异或常数
HgppStatus hgppiXorC_8u_C1R_Ctx(const HGpp8u *pSrc1, int nSrc1Step, const HGpp8u nConstant,
                                 HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                 HgppStreamContext hgppStreamCtx)
HgppStatus hgppiXorC_8u_C1IR_Ctx(...)
HgppStatus hgppiXorC_8u_C3R_Ctx(...)
HgppStatus hgppiXorC_8u_C3IR_Ctx(...)

// 图像异或
HgppStatus hgppiXor_8u_C1R_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                const HGpp8u *pSrc2, int nSrc2Step,
                                HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                HgppStreamContext hgppStreamCtx)
HgppStatus hgppiXor_8u_C1IR_Ctx(...)
HgppStatus hgppiXor_8u_C3R_Ctx(...)
```

**16 位/32 位**

```c
HgppStatus hgppiXorC_16u_C1R_Ctx(...)
HgppStatus hgppiXorC_32s_C1R_Ctx(...)
HgppStatus hgppiXor_16u_C1R_Ctx(...)
HgppStatus hgppiXor_32s_C1R_Ctx(...)
```

##### 5.2.3.4. 逻辑非
```c
HgppStatus hgppiNot_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                HgppStreamContext hgppStreamCtx)
HgppStatus hgppiNot_8u_C1IR_Ctx(...)
HgppStatus hgppiNot_16u_C1R_Ctx(...)
HgppStatus hgppiNot_32s_C1R_Ctx(...)
```

##### 5.2.3.5. 移位运算
**左移**

```c
HgppStatus hgppiLShiftC_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, int nConstant,
                                      HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                      HgppStreamContext hgppStreamCtx)
HgppStatus hgppiLShiftC_8u_C1IR_Ctx(...)
HgppStatus hgppiLShiftC_16u_C1R_Ctx(...)
HgppStatus hgppiLShiftC_32s_C1R_Ctx(...)
```

**右移**

```c
HgppStatus hgppiRShiftC_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, int nConstant,
                                       HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                       HgppStreamContext hgppStreamCtx)
HgppStatus hgppiRShiftC_8u_C1IR_Ctx(...)
HgppStatus hgppiRShiftC_16u_C1R_Ctx(...)
HgppStatus hgppiRShiftC_32s_C1R_Ctx(...)
```

> **注意：**
> 本章仅列出常用的逻辑运算函数变体。完整的逻辑运算函数系列包括：
> - **And/AndC**： 24+24=48 个函数（8u/16u/32s， C1/C3/C4/AC4 等）
> - **Or/OrC**： 24+24=48 个函数。
> - **Xor/XorC**： 24+24=48 个函数。
> - **Not**： 8 个函数
> - **LShiftC**： 24 个函数（左移常量）
> - **RShiftC**： 40 个函数（右移常量）
> - 完整的 GetBufferHostSize 变体。

**请参考头文件 `hgppial.h` 获取完整的函数列表。**

### 5.3. Alpha 合成
#### 5.3.1. 功能介绍
Alpha 合成函数使用 alpha 透明度值对图像进行混合操作。支持多种混合模式（AlphaOp），包括 OVER、 IN、 OUT、 ATOP、 XOR、 PLUS 等。

#### 5.3.2. 完整参数说明
##### 5.3.2.1. AlphaCompC 通用参数（常量 Alpha 合成）
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc1` | 设备指针 | [in] | **源图像指针** - 第一个输入图像 |
| `nSrc1Step` | int | [in] | **源图像行步幅** |
| `nAlpha1` | 数据类型 | [in] | **Alpha 不透明度** - 图像 1 的 alpha 值（整数类型： 0 到最大通道像素值，浮点类型： 0.0-1.0） |
| `pSrc2` | 设备指针 | [in] | **源图像指针** - 第二个输入图像 |
| `nSrc2Step` | int | [in] | **源图像行步幅** |
| `nAlpha2` | 数据类型 | [in] | **Alpha 不透明度** - 图像 2 的 alpha 值 |
| `pDst` | 设备指针 | [out] | **目标图像指针** |
| `nDstStep` | int | [in] | **目标图像行步幅** |
| `oSizeROI` | HgppiSize | [in] | **感兴趣区域** |
| `eAlphaOp` | HgppiAlphaOp | [in] | **Alpha 混合操作** - 混合模式枚举值（见下表） |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

**AlphaOp 模式说明：**

| 模式 | 说明 | 运算公式 |
|------|------|----------|
| `HGPP_OP_ALPHA_OVER` | A over B | $\text{dst} = \alpha_A \times A + (1-\alpha_A) \times B$ |
| `HGPP_OP_ALPHA_IN` | A in B | $\text{dst} = \alpha_B \times A$ |
| `HGPP_OP_ALPHA_OUT` | A out B | $\text{dst} = (1-\alpha_B) \times A$ |
| `HGPP_OP_ALPHA_ATOP` | A atop B | $\text{dst} = \alpha_B \times A + (1-\alpha_A) \times B$ |
| `HGPP_OP_ALPHA_XOR` | A xor B | $\text{dst} = (1-\alpha_B) \times A + (1-\alpha_A) \times B$ |
| `HGPP_OP_ALPHA_PLUS` | A plus B | $\text{dst} = A + B$ |
| `HGPP_OP_ALPHA_PREMUL` | 预乘 | $\text{dst} = \alpha \times A$ |

##### 5.3.2.2. AlphaPremulC 通用参数（Alpha 预乘）
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc1` | 设备指针 | [in] | **源图像指针** |
| `nSrc1Step` | int | [in] | **源图像行步幅** |
| `nAlpha1` | 数据类型 | [in] | **Alpha 不透明度** |
| `pDst` | 设备指针 | [out] | **目标图像指针** |
| `nDstStep` | int | [in] | **目标图像行步幅** |
| `pSrcDst` | 设备指针 | [in,out] | **图像指针** |
| `nSrcDstStep` | int | [in] | **图像行步幅** |
| `oSizeROI` | HgppiSize | [in] | **感兴趣区域** |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

**运算公式：** $\text{dstPixel} = \text{srcPixel} \times \alpha$。

##### 5.3.2.3. AlphaUnpremulC 通用参数（Alpha 去预乘）
**运算公式：** $\text{dstPixel} = \text{srcPixel} / \alpha$（如果 $\alpha > 0$）

> **注意：**
> 当 $\alpha = 0$ 时结果未定义。

#### 5.3.3. 函数列表
##### 5.3.3.1. AlphaCompC （常量 Alpha 合成）
**8 位无符号整数**

```c
// 单通道
HgppStatus hgppiAlphaCompC_8u_C1R_Ctx(const HGpp8u *pSrc1, int nSrc1Step, HGpp8u nAlpha1,
                                       const HGpp8u *pSrc2, int nSrc2Step, HGpp8u nAlpha2,
                                       HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                       HgppiAlphaOp eAlphaOp, HgppStreamContext hgppStreamCtx)

// 三通道
HgppStatus hgppiAlphaCompC_8u_C3R_Ctx(const HGpp8u *pSrc1, int nSrc1Step, HGpp8u nAlpha1,
                                       const HGpp8u *pSrc2, int nSrc2Step, HGpp8u nAlpha2,
                                       HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                       HgppiAlphaOp eAlphaOp, HgppStreamContext hgppStreamCtx)

// 四通道
HgppStatus hgppiAlphaCompC_8u_C4R_Ctx(const HGpp8u *pSrc1, int nSrc1Step, HGpp8u nAlpha1,
                                       const HGpp8u *pSrc2, int nSrc2Step, HGpp8u nAlpha2,
                                       HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                       HgppiAlphaOp eAlphaOp, HgppStreamContext hgppStreamCtx)

// 四通道（带 Alpha 通道）
HgppStatus hgppiAlphaCompC_8u_AC4R_Ctx(const HGpp8u *pSrc1, int nSrc1Step, HGpp8u nAlpha1,
                                        const HGpp8u *pSrc2, int nSrc2Step, HGpp8u nAlpha2,
                                        HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                        HgppiAlphaOp eAlphaOp, HgppStreamContext hgppStreamCtx)
```

**16 位无符号/有符号整数**

```c
HgppStatus hgppiAlphaCompC_16u_C1R_Ctx(...)
HgppStatus hgppiAlphaCompC_16u_C3R_Ctx(...)
HgppStatus hgppiAlphaCompC_16u_C4R_Ctx(...)
HgppStatus hgppiAlphaCompC_16u_AC4R_Ctx(...)
HgppStatus hgppiAlphaCompC_16s_C1R_Ctx(...)
```

**32 位无符号/有符号/浮点数**

```c
HgppStatus hgppiAlphaCompC_32u_C1R_Ctx(...)
HgppStatus hgppiAlphaCompC_32s_C1R_Ctx(...)

// 32 位浮点（alpha 值范围 0.0-1.0）（注意）
HgppStatus hgppiAlphaCompC_32f_C1R_Ctx(const Hgpp32f *pSrc1, int nSrc1Step, Hgpp32f nAlpha1,
                                        const Hgpp32f *pSrc2, int nSrc2Step, Hgpp32f nAlpha2,
                                        Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI,
                                        HgppiAlphaOp eAlphaOp, HgppStreamContext hgppStreamCtx)
```

##### 5.3.3.2. AlphaPremulC （Alpha 预乘）
**8 位无符号整数**

```c
// 单通道
HgppStatus hgppiAlphaPremulC_8u_C1R_Ctx(const HGpp8u *pSrc1, int nSrc1Step, HGpp8u nAlpha1,
                                         HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                         HgppStreamContext hgppStreamCtx)

// 原图像操作单通道
HgppStatus hgppiAlphaPremulC_8u_C1IR_Ctx(HGpp8u nAlpha1, HGpp8u *pSrcDst, int nSrcDstStep,
                                          HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

// 三通道
HgppStatus hgppiAlphaPremulC_8u_C3R_Ctx(...)
HgppStatus hgppiAlphaPremulC_8u_C3IR_Ctx(...)

// 四通道
HgppStatus hgppiAlphaPremulC_8u_C4R_Ctx(...)
HgppStatus hgppiAlphaPremulC_8u_C4IR_Ctx(...)

// 四通道（带 Alpha）
HgppStatus hgppiAlphaPremulC_8u_AC4R_Ctx(...)
HgppStatus hgppiAlphaPremulC_8u_AC4IR_Ctx(...)
```

**16 位无符号整数**

```c
HgppStatus hgppiAlphaPremulC_16u_C1R_Ctx(...)
HgppStatus hgppiAlphaPremulC_16u_C1IR_Ctx(...)
HgppStatus hgppiAlphaPremulC_16u_C3R_Ctx(...)
HgppStatus hgppiAlphaPremulC_16u_C3IR_Ctx(...)
HgppStatus hgppiAlphaPremulC_16u_C4R_Ctx(...)
HgppStatus hgppiAlphaPremulC_16u_C4IR_Ctx(...)
HgppStatus hgppiAlphaPremulC_16u_AC4R_Ctx(...)
HgppStatus hgppiAlphaPremulC_16u_AC4IR_Ctx(...)
```

##### 5.3.3.3. AlphaUnpremulC （Alpha 去预乘）
```c
HgppStatus hgppiAlphaUnpremulC_8u_C1R_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                           HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                           HgppStreamContext hgppStreamCtx)
HgppStatus hgppiAlphaUnpremulC_8u_C1IR_Ctx(HGpp8u *pSrcDst, int nSrcDstStep,
                                            HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiAlphaUnpremulC_16u_C1R_Ctx(...)
HgppStatus hgppiAlphaUnpremulC_32f_C1R_Ctx(...)
```

> **注意：**
> 本章仅列出常用的 Alpha 合成函数变体。完整的 Alpha 合成函数系列包括：
> - **AlphaComp/AlphaCompC**： 12+13=25 个函数（8u/16u/32f， C1/C3/C4/AC4 等）
> - **AlphaPremul/AlphaPremulC**： 4+16=20 个函数。
> - **AlphaUnpremulC**： 16 个函数。
> - 完整的 GetBufferHostSize 变体。

**请参考头文件 `hgppial.h` 获取完整的函数列表。**

### 5.4. 错误码
| 错误码 | 说明 |
|--------|------|
| `HGPP_NULL_POINTER_ERROR` | 空指针错误 - pSrc、 pDst 或关键参数指针为 NULL |
| `HGPP_STEP_ERROR` | 步幅错误 - nSrcStep 或 nDstStep ≤ 0 |
| `HGPP_SIZE_ERROR` | ROI 尺寸错误 - oSizeROI 宽度或高度 < 0 |
| `HGPP_DIVISOR_ERROR` | 除数为零错误 - 除法运算中除数为 0 |
| `HGPP_SCALE_RANGE_ERROR` | 缩放因子范围错误 - nScaleFactor 超出有效范围 |
| `HGPP_OVERFLOW_ERROR` | 数值溢出错误 - 结果超出数据类型的表示范围 |
| `HGPP_DATA_TYPE_ERROR` | 数据类型错误 - 不支持的数据类型 |
| `HGPP_ALPHA_OP_ERROR` | 不支持的 Alpha 操作 - eAlphaOp 值无效 |

## 6. 图像颜色转换
函数定义于 `hgppi_cc.h`, 位于 `hgppicc` 库中。
同类函数没有全部列出，完整函数定义请参考头文件。

### 6.1. RGB↔YUV 转换
#### 6.1.1. 颜色空间标准详解
##### 6.1.1.1. BT.601 （ITU-R BT.601）- 标清电视（SDTV）
BT.601 是 ITU 于 1982 年发布的标清数字电视标准，用于 525 行（NTSC）和 625 行（PAL/SECAM）系统。

**BT.601 转换系数（8 位， TV Range）：**

| 系数 | 值 |
|------|-----|
| Kr | 0.299 |
| Kg | 0.587 |
| Kb | 0.114 |

**RGB→YUV （BT.601， TV Range）：**

$$
\begin{aligned}
Y &= 0.299 \times R + 0.587 \times G + 0.114 \times B \\
U &= 0.492 \times (B - Y) + 128 = -0.147 \times R - 0.289 \times G + 0.436 \times B + 128 \\
V &= 0.877 \times (R - Y) + 128 = 0.615 \times R - 0.515 \times G - 0.100 \times B + 128
\end{aligned}
$$

**YUV→RGB （BT.601， TV Range）：**

$$
\begin{aligned}
R &= Y + 1.402 \times (V - 128) \\
G &= Y - 0.344 \times (U - 128) - 0.714 \times (V - 128) \\
B &= Y + 1.772 \times (U - 128)
\end{aligned}
$$

**有效范围（8 位 TV Range）：**

| 分量 | 有效范围 | 说明 |
|------|----------|------|
| Y | 16-235 | 黑电平=16，白电平=235 |
| U/Cb | 16-240 | 中心值=128 |
| V/Cr | 16-240 | 中心值=128 |

##### 6.1.1.2. BT.709 （ITU-R BT.709）- 高清电视（HDTV）
BT.709 是 1990 年发布的高清电视标准，用于 720p、 1080i、 1080p 等高清格式。

**BT.709 转换系数：**

| 系数 | 值 |
|------|-----|
| Kr | 0.2126 |
| Kg | 0.7152 |
| Kb | 0.0722 |

**RGB→YUV （BT.709， TV Range）：**

$$
\begin{aligned}
Y &= 0.2126 \times R + 0.7152 \times G + 0.0722 \times B \\
U &= 0.539 \times (B - Y) + 128 = -0.114 \times R - 0.385 \times G + 0.499 \times B + 128 \\
V &= 0.635 \times (R - Y) + 128 = 0.499 \times R - 0.454 \times G - 0.045 \times B + 128
\end{aligned}
$$

**YUV→RGB （BT.709， TV Range）：**

$$
\begin{aligned}
R &= Y + 1.5748 \times (V - 128) \\
G &= Y - 0.1873 \times (U - 128) - 0.4681 \times (V - 128) \\
B &= Y + 1.8556 \times (U - 128)
\end{aligned}
$$

##### 6.1.1.3. BT.2020 （ITU-R BT.2020）- 超高清电视（UHDTV）
BT.2020 是 2012 年发布的超高清电视标准，用于 4K UHDTV 和 8K UHDTV。

**BT.2020 转换系数：**

| 系数 | 值 |
|------|-----|
| Kr | 0.2627 |
| Kg | 0.6780 |
| Kb | 0.0593 |

**RGB→YUV （BT.2020， TV Range）：**

$$
\begin{aligned}
Y &= 0.2627 \times R + 0.6780 \times G + 0.0593 \times B \\
U &= 0.559 \times (B - Y) + 128 \\
V &= 0.787 \times (R - Y) + 128
\end{aligned}
$$

**YUV→RGB （BT.2020， TV Range）：**

$$
\begin{aligned}
R &= Y + 1.4746 \times (V - 128) \\
G &= Y - 0.1646 \times (U - 128) - 0.5714 \times (V - 128) \\
B &= Y + 1.8814 \times (U - 128)
\end{aligned}
$$

##### 6.1.1.4. JPEG 标准 - 全范围（Full Range）
JPEG 使用全范围（Full Range） YCbCr， Y、 Cb、 Cr 都使用完整的 [0..255] 范围。

**JPEG 转换系数（与 BT.601 相同）：**

| 系数 | 值 |
|------|-----|
| Kr | 0.299 |
| Kg | 0.587 |
| Kb | 0.114 |

**RGB→YCbCr （JPEG， Full Range）：**

$$
\begin{aligned}
Y &= 0.299 \times R + 0.587 \times G + 0.114 \times B \\
Cb &= -0.168736 \times R - 0.331264 \times G + 0.5 \times B + 128 \\
Cr &= 0.5 \times R - 0.418688 \times G - 0.081312 \times B + 128
\end{aligned}
$$

**YCbCr→RGB （JPEG， Full Range）：**

$$
\begin{aligned}
R &= Y + 1.402 \times (Cr - 128) \\
G &= Y - 0.344136 \times (Cb - 128) - 0.714136 \times (Cr - 128) \\
B &= Y + 1.772 \times (Cb - 128)
\end{aligned}
$$

**有效范围（8 位 Full Range）：**

| 分量 | 有效范围 | 说明 |
|------|----------|------|
| Y | 0-255 | 黑电平=0，白电平=255 |
| Cb | 0-255 | 中心值=128 |
| Cr | 0-255 | 中心值=128 |

#### 6.1.2. TV Range vs Full Range 对比
| 特性 | TV Range (BT.601/709/2020) | Full Range (JPEG) |
|------|---------------------------|-------------------|
| **Y 范围** | 16-235 | 0-255 |
| **Cb/Cr 范围** | 16-240 | 0-255 |
| **黑电平** | 16 | 0 |
| **白电平** | 235 | 255 |
| **应用场景** | 广播电视、视频编码 | JPEG 图像、计算机图形 |

> **注意：**
> 错误地将 TV Range 内容当作 Full Range 显示会导致黑色发灰（16 被显示为暗灰而非纯黑），白色过曝（235 被拉伸到 255）。反之， Full Range 内容在 TV Range 设备上显示会导致黑色被削波（0-15 丢失）和白色过曝（236-255 削波）。

#### 6.1.3. 完整参数说明
##### 6.1.3.1. RGBToYUV / YUVToRGB 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | **源图像指针** - Packet （C3）或 Planar 指针数组（P3） |
| `nSrcStep` | int | [in] | **源图像行步幅**（字节）， Packet 格式使用 |
| `aSrcStep[]` | int 数组 | [in] | **源图像步幅数组** - Planar 格式使用，每个元素对应一个 Planar |
| `pDst` | 设备指针 | [out] | **目标图像指针** - Packet 格式或 Planar 指针数组 |
| `nDstStep` | int | [in] | **目标图像行步幅**（字节）， Packet 格式使用 |
| `aDstStep[]` | int 数组 | [in] | **目标图像步幅数组** - Planar 格式使用 |
| `oSizeROI` | HgppiSize | [in] | **感兴趣区域** - ROI 宽度和高度（像素） |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

#### 6.1.4. 函数列表
##### 6.1.4.1. RGBToYUV （Packet→Packet）
**8 位无符号整数**

```c
// 三通道Packet RGB → 三通道Packet YUV
HgppStatus hgppiRGBToYUV_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                     HGpp8u *pDst, int nDstStep,
                                     HgppiSize oSizeROI,
                                     HgppStreamContext hgppStreamCtx)

// 四通道Packet RGB（带 Alpha）→ 四通道Packet YUV（不影响 Alpha）
HgppStatus hgppiRGBToYUV_8u_AC4R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                      HGpp8u *pDst, int nDstStep,
                                      HgppiSize oSizeROI,
                                      HgppStreamContext hgppStreamCtx)
```

##### 6.1.4.2. RGBToYUV （Packet→Planar）
```c
// 三通道Packet RGB → 三通道Planar YUV
HgppStatus hgppiRGBToYUV_8u_C3P3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                       HGpp8u *pDst[3], int nDstStep,
                                       HgppiSize oSizeROI,
                                       HgppStreamContext hgppStreamCtx)

// 四通道Packet RGB（带 Alpha）→ 四通道Planar YUV（带 Alpha）
HgppStatus hgppiRGBToYUV_8u_AC4P4R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                        HGpp8u *pDst[4], int nDstStep,
                                        HgppiSize oSizeROI,
                                        HgppStreamContext hgppStreamCtx)
```

##### 6.1.4.3. RGBToYUV （Planar→Planar）
```c
// 三通道Planar RGB → 三通道Planar YUV
HgppStatus hgppiRGBToYUV_8u_P3R_Ctx(const HGpp8u *const pSrc[3], int nSrcStep,
                                     HGpp8u *pDst[3], int nDstStep,
                                     HgppiSize oSizeROI,
                                     HgppStreamContext hgppStreamCtx)
```

###### 16 位无符号版本
```c
HgppStatus hgppiRGBToYUV_16u_C3R_Ctx(...)
HgppStatus hgppiRGBToYUV_16u_AC4R_Ctx(...)
HgppStatus hgppiRGBToYUV_16u_C3P3R_Ctx(...)
HgppStatus hgppiRGBToYUV_16u_P3R_Ctx(...)
```

###### 32 位浮点版本
```c
HgppStatus hgppiRGBToYUV_32f_C3R_Ctx(...)
HgppStatus hgppiRGBToYUV_32f_C3P3R_Ctx(...)
HgppStatus hgppiRGBToYUV_32f_P3R_Ctx(...)
```

##### 6.1.4.4. YUVToRGB （逆转换）
**8 位无符号整数**

```c
// 三通道Packet YUV → 三通道Packet RGB
HgppStatus hgppiYUVToRGB_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                     HGpp8u *pDst, int nDstStep,
                                     HgppiSize oSizeROI,
                                     HgppStreamContext hgppStreamCtx)

// 四通道Packet YUV（带 Alpha）→ 四通道Packet RGB（不影响 Alpha）
HgppStatus hgppiYUVToRGB_8u_AC4R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                      HGpp8u *pDst, int nDstStep,
                                      HgppiSize oSizeROI,
                                      HgppStreamContext hgppStreamCtx)

// 三通道Planar YUV → 三通道Planar RGB
HgppStatus hgppiYUVToRGB_8u_P3R_Ctx(const HGpp8u *const pSrc[3], int nSrcStep,
                                     HGpp8u *pDst[3], int nDstStep,
                                     HgppiSize oSizeROI,
                                     HgppStreamContext hgppStreamCtx)

// 三通道Planar YUV → 三通道Packet RGB
HgppStatus hgppiYUVToRGB_8u_P3C3R_Ctx(const HGpp8u *const pSrc[3], int nSrcStep,
                                       HGpp8u *pDst, int nDstStep,
                                       HgppiSize oSizeROI,
                                       HgppStreamContext hgppStreamCtx)
```

**16 位/32 位版本**

```c
HgppStatus hgppiYUVToRGB_16u_C3R_Ctx(...)
HgppStatus hgppiYUVToRGB_16u_P3R_Ctx(...)
HgppStatus hgppiYUVToRGB_16u_P3C3R_Ctx(...)

HgppStatus hgppiYUVToRGB_32f_C3R_Ctx(...)
HgppStatus hgppiYUVToRGB_32f_P3R_Ctx(...)
HgppStatus hgppiYUVToRGB_32f_P3C3R_Ctx(...)
```

### 6.2. RGB↔YCbCr 转换
#### 6.2.1. 功能介绍
RGB 到 YCbCr 颜色空间转换。 YCbCr 是 YUV 的数字版本，广泛用于 JPEG 和 MPEG 视频压缩标准。

> **注意：**
> - YCbCr 与 YUV 类似，但使用不同的缩放因子。
> - Cb 和 Cr 分量也需要加上 128 的偏置值。

#### 6.2.2. 完整参数说明
参数与 RGB↔YUV 转换相同，见上方参数表。

#### 6.2.3. 函数列表
##### 6.2.3.1. RGBToYCbCr
**8 位无符号整数**

```c
// 三通道Packet RGB → 三通道Packet YCbCr
HgppStatus hgppiRGBToYCbCr_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                       HGpp8u *pDst, int nDstStep,
                                       HgppiSize oSizeROI,
                                       HgppStreamContext hgppStreamCtx)

// 四通道Packet RGB（带 Alpha）→ 四通道Packet YCbCr（不影响 Alpha）
HgppStatus hgppiRGBToYCbCr_8u_AC4R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                        HGpp8u *pDst, int nDstStep,
                                        HgppiSize oSizeROI,
                                        HgppStreamContext hgppStreamCtx)

// 三通道Packet RGB → 三通道Planar YCbCr
HgppStatus hgppiRGBToYCbCr_8u_C3P3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                         HGpp8u *pDst[3], int nDstStep,
                                         HgppiSize oSizeROI,
                                         HgppStreamContext hgppStreamCtx)

// 三通道Planar RGB → 三通道Planar YCbCr
HgppStatus hgppiRGBToYCbCr_8u_P3R_Ctx(const HGpp8u *const pSrc[3], int nSrcStep,
                                       HGpp8u *pDst[3], int nDstStep,
                                       HgppiSize oSizeROI,
                                       HgppStreamContext hgppStreamCtx)
```

**16 位/32 位版本**

```c
HgppStatus hgppiRGBToYCbCr_16u_C3R_Ctx(...)
HgppStatus hgppiRGBToYCbCr_16u_AC4R_Ctx(...)
HgppStatus hgppiRGBToYCbCr_16u_C3P3R_Ctx(...)
HgppStatus hgppiRGBToYCbCr_16u_P3R_Ctx(...)

HgppStatus hgppiRGBToYCbCr_32f_C3R_Ctx(...)
HgppStatus hgppiRGBToYCbCr_32f_C3P3R_Ctx(...)
HgppStatus hgppiRGBToYCbCr_32f_P3R_Ctx(...)
```

##### 6.2.3.2. YCbCrToRGB （逆转换）
```c
// 三通道Packet YCbCr → 三通道Packet RGB
HgppStatus hgppiYCbCrToRGB_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                       HGpp8u *pDst, int nDstStep,
                                       HgppiSize oSizeROI,
                                       HgppStreamContext hgppStreamCtx)

// 三通道Planar YCbCr → 三通道Packet RGB
HgppStatus hgppiYCbCrToRGB_8u_P3C3R_Ctx(const HGpp8u *const pSrc[3], int nSrcStep,
                                         HGpp8u *pDst, int nDstStep,
                                         HgppiSize oSizeROI,
                                         HgppStreamContext hgppStreamCtx)

// 三通道Planar YCbCr → 三通道Planar RGB
HgppStatus hgppiYCbCrToRGB_8u_P3R_Ctx(const HGpp8u *const pSrc[3], int nSrcStep,
                                       HGpp8u *pDst[3], int nDstStep,
                                       HgppiSize oSizeROI,
                                       HgppStreamContext hgppStreamCtx)
```

**16 位/32 位版本**

```c
HgppStatus hgppiYCbCrToRGB_16u_C3R_Ctx(...)
HgppStatus hgppiYCbCrToRGB_16u_P3C3R_Ctx(...)
HgppStatus hgppiYCbCrToRGB_16u_P3R_Ctx(...)

HgppStatus hgppiYCbCrToRGB_32f_C3R_Ctx(...)
HgppStatus hgppiYCbCrToRGB_32f_P3C3R_Ctx(...)
HgppStatus hgppiYCbCrToRGB_32f_P3R_Ctx(...)
```

### 6.3. RGB↔HSV/HLS
#### 6.3.1. 功能介绍
RGB 与 HSV （色相 - 饱和度 - 明度）和 HLS （色相 - 亮度 - 饱和度）颜色空间转换。这些颜色空间更符合人类对颜色的感知。

#### 6.3.2. HSV 颜色空间（色相 - 饱和度 - 明度）
**HSV 几何模型 - 圆锥体：**

```text
                    V (明度/Value)
                    ↑
                   /|\
                  / | \
                 /  |  \
                /   |   \      S=100% (边缘：纯色)
               /    |    \
              /     |     \
             /      |      \
            /_______|_______\
           /        |        \
          /         |         \
         /          |          \
        /___________|___________\
       ↙            |            ↘
      S=0% (中心轴：灰色)         H (色相：绕轴角度)

V=0 (底部顶点)：黑色
V=100%, S=0 (顶部中心)：白色
```

**HSV 三个分量的物理意义：**

| 分量 | 英文 | 范围 | 几何意义 | 视觉效果 |
|------|------|------|----------|----------|
| **H** | Hue | 0°-360° | 绕中心轴的角度 | 颜色类型（红橙黄绿青蓝紫） |
| **S** | Saturation | 0-100% | 距中心轴的距离 | 颜色纯度（0=灰， 100%=鲜艳） |
| **V** | Value/Brightness | 0-100% | 高度（从底部到顶部） | 亮度（0=黑， 100%=最亮） |

**HSV 色轮（H 分量）：**
```text
          0° (红)
           ↑
          / \
         /   \
        /     \
  270° (蓝)   120° (绿)
      ↖       ↗
       \     /
        \   /
         \ /
          ↓
       180° (青)

完整色轮：0°红 → 60°黄 → 120°绿 → 180°青 → 240°蓝 → 300°品红 → 360°红
```

**HSV 应用场景：**
- **图像分割**：基于颜色阈值分割（如检测红色物体）。
- **颜色调整**：单独调整饱和度或亮度。
- **计算机视觉**：颜色特征提取。
- **艺术工具**：调色板、颜色选择器。

#### 6.3.3. HLS 颜色空间（色相 - 亮度 - 饱和度）
**HLS 几何模型 - 双圆锥体：**

```text
                    L=100% (白)
                       ●
                      / \
                     /   \
                    /     \
                   /       \
                  /    L=50% (纯色平面)
                 /    S=100% (边缘)
                /           \
               /             \
              /               \
             /                 \
            /                   \
           /                     \
          /                       \
         ●_________________________●
      L=0% (黑)                H (色相)
```

**HLS 三个分量的物理意义：**

| 分量 | 英文 | 范围 | 几何意义 | 视觉效果 |
|------|------|------|----------|----------|
| **H** | Hue | 0°-360° | 绕中心轴的角度 | 同 HSV |
| **L** | Lightness | 0-100% | 高度（双圆锥） | 0=黑， 50%=纯色， 100%=白 |
| **S** | Saturation | 0-100% | 距中心轴的距离 | 同 HSV，但在 L=50% 时最敏感 |

**HLS vs HSV 关键区别：**

| 特性 | HSV | HLS |
|------|-----|-----|
| **白色位置** | V=100%, S=0 （顶部中心） | L=100%（顶部顶点） |
| **纯色位置** | V=100%, S=100%（顶部边缘） | L=50%, S=100%（中间平面边缘） |
| **黑色位置** | V=0 （底部顶点） | L=0 （底部顶点） |
| **灰色轴** | S=0 （中心轴） | S=0 （中心轴） |
| **感知均匀性** | 一般 | 更好（L=50% 对应纯色） |

**HLS 应用场景：**
- **图像增强**：调整亮度而不影响颜色。
- **颜色量化**：基于亮度的颜色分组。
- **医学影像**：组织对比度增强。
- **遥感**：地物分类

#### 6.3.4. HGPP 中的 HSV/HLS 表示

> **注意：**
> - HSV 的 V=0 时总是黑色，无论 H 和 S。
> - HLS 的 L=0 时是黑色， L=100% 时是白色， L=50% 时是纯色。
> - **HGPP 使用归一化范围**：
> - H=[0,255] 对应 0°-360°（8 位图像）
> - S/V/L=[0,255] 对应 0%-100%（8 位图像）
> - 对于 16 位图像： H=[0,65535]， S/V/L=[0,65535]
> - 对于 32 位浮点： H=[0,1]， S/V/L=[0,1]
>
> **HGPP 归一化公式：**

$$
H_{8u} = H_{degrees} \times \frac{255}{360}, \quad S_{8u} = S_{percent} \times \frac{255}{100}, \quad V_{8u} = V_{percent} \times \frac{255}{100}
$$

**常见颜色的 HSV 值（8 位表示）：**

| 颜色 | H (0-255) | S (0-255) | V (0-255) | 说明 |
|------|-----------|-----------|-----------|------|
| **纯红** | 0 | 255 | 255 | H=0° |
| **纯黄** | 42 | 255 | 255 | H=60° |
| **纯绿** | 85 | 255 | 255 | H=120° |
| **纯青** | 128 | 255 | 255 | H=180° |
| **纯蓝** | 170 | 255 | 255 | H=240° |
| **纯品红** | 213 | 255 | 255 | H=300° |
| **白色** | 0 | 0 | 255 | S=0 （无饱和度） |
| **灰色** | 0 | 0 | 128 | S=0, V=50% |
| **黑色** | 0 | 0 | 0 | V=0 |

#### 6.3.5. RGB→HSV 转换公式
**步骤 1：归一化 RGB 到 [0,1]**

$$
R' = R/255, \quad G' = G/255, \quad B' = B/255
$$

**步骤 2：计算最大值和最小值**

$$
C_{max} = \max(R', G', B'), \quad C_{min} = \min(R', G', B'), \quad \Delta = C_{max} - C_{min}
$$

**步骤 3：计算色相 H**

$$
H = \begin{cases}
0° & \text{if } \Delta = 0 \\
60° \times \left(\frac{G' - B'}{\Delta} \mod 6\right) & \text{if } C_{max} = R' \\
60° \times \left(\frac{B' - R'}{\Delta} + 2\right) & \text{if } C_{max} = G' \\
60° \times \left(\frac{R' - G'}{\Delta} + 4\right) & \text{if } C_{max} = B'
\end{cases}
$$

**步骤 4：计算饱和度 S**

$$
S = \begin{cases}
0 & \text{if } C_{max} = 0 \\
\Delta / C_{max} & \text{if } C_{max} \neq 0
\end{cases}
$$

**步骤 5：计算明度 V**

$$
V = C_{max}
$$

#### 6.3.6. HSV→RGB 逆转换公式
**步骤 1：计算中间值**

$$
C = V \times S, \quad X = C \times (1 - |(H/60°) \mod 2 - 1|), \quad m = V - C
$$

**步骤 2：根据 H 的范围计算 (R', G', B')**

| H 范围 | (R', G', B') |
|--------|-------------|
| 0° ≤ H < 60° | (C, X, 0) |
| 60° ≤ H < 120° | (X, C, 0) |
| 120° ≤ H < 180° | (0, C, X) |
| 180° ≤ H < 240° | (0, X, C) |
| 240° ≤ H < 300° | (X, 0, C) |
| 300° ≤ H < 360° | (C, 0, X) |

**步骤 3：还原到 [0,255]**

$$
R = (R' + m) \times 255, \quad G = (G' + m) \times 255, \quad B = (B' + m) \times 255
$$

#### 6.3.7. RGB→HLS 转换公式
**步骤 1-2：同 HSV （计算 Cmax, Cmin, Δ）**

**步骤 3：计算亮度 L**

$$
L = (C_{max} + C_{min}) / 2
$$

**步骤 4：计算饱和度 S**

$$
S = \begin{cases}
0 & \text{if } \Delta = 0 \\
\Delta / (1 - |2L - 1|) & \text{if } \Delta \neq 0
\end{cases}
$$

**步骤 5：色相 H 计算同 HSV**

#### 6.3.8. HLS→RGB 逆转换公式
**步骤 1：计算中间值**

$$
\text{如果 } L < 0.5: \quad C = (1 - |2L - 1|) \times S \\
\text{如果 } L \geq 0.5: \quad C = (1 - |2L - 1|) \times S \\
X = C \times (1 - |(H/60°) \mod 2 - 1|), \quad m = L - C/2
$$

**步骤 2-3：同 HSV**

#### 6.3.9. 函数列表
##### 6.3.9.1. RGBToHSV
```c
// 三通道Packet RGB → 三通道Packet HSV
HgppStatus hgppiRGBToHSV_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                     HGpp8u *pDst, int nDstStep,
                                     HgppiSize oSizeROI,
                                     HgppStreamContext hgppStreamCtx)

// 三通道Planar RGB → 三通道Planar HSV
HgppStatus hgppiRGBToHSV_8u_P3R_Ctx(const HGpp8u *const pSrc[3], int nSrcStep,
                                     HGpp8u *pDst[3], int nDstStep,
                                     HgppiSize oSizeROI,
                                     HgppStreamContext hgppStreamCtx)
```

##### 6.3.9.2. HSVToRGB （逆转换）
```c
// 三通道Packet HSV → 三通道Packet RGB
HgppStatus hgppiHSVToRGB_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                     HGpp8u *pDst, int nDstStep,
                                     HgppiSize oSizeROI,
                                     HgppStreamContext hgppStreamCtx)

// 三通道Planar HSV → 三通道Planar RGB
HgppStatus hgppiHSVToRGB_8u_P3R_Ctx(const HGpp8u *const pSrc[3], int nSrcStep,
                                     HGpp8u *pDst[3], int nDstStep,
                                     HgppiSize oSizeROI,
                                     HgppStreamContext hgppStreamCtx)
```

##### 6.3.9.3. RGBToHLS / HLSToRGB
```c
HgppStatus hgppiRGBToHLS_8u_C3R_Ctx(...)
HgppStatus hgppiHLSToRGB_8u_C3R_Ctx(...)
HgppStatus hgppiRGBToHLS_8u_P3R_Ctx(...)
HgppStatus hgppiHLSToRGB_8u_P3R_Ctx(...)
```

**16 位/32 位版本**

```c
HgppStatus hgppiRGBToHSV_16u_C3R_Ctx(...)
HgppStatus hgppiHSVToRGB_16u_C3R_Ctx(...)
HgppStatus hgppiRGBToHSV_32f_C3R_Ctx(...)
HgppStatus hgppiHSVToRGB_32f_C3R_Ctx(...)
```

### 6.4. RGB↔Lab/Luv 转换
#### 6.4.1. 功能介绍
RGB 与 CIE Lab 和 CIE Luv 颜色空间转换。这些是感知均匀的颜色空间，设计为与人眼感知一致。

#### 6.4.2. 为什么需要 Lab/Luv？—— RGB 的局限性
**RGB 颜色空间的问题：**
- **设备依赖**：不同显示器的 RGB 值产生不同颜色。
- **感知不均匀**： RGB 值变化相同，人眼感知的颜色变化不同。
- **色差不直观**：无法直接用 RGB 值计算两种颜色的"距离"。

**CIE 的解决方案：**
1931 年， CIE （国际照明委员会）定义了基于人眼感知的颜色空间，目标是：
- **设备无关**：描述颜色本身，而非显示方式。
- **感知均匀**：数值变化与人眼感知成正比。
- **可计算色差**：用欧几里得距离表示颜色差异。

#### 6.4.3. CIE XYZ 颜色空间（中间空间）
**XYZ 是 Lab/Luv 的基础，所有颜色转换都要经过 XYZ。**

**XYZ 三刺激值：**
- **X**：近似红色响应（但非纯红）
- **Y**：亮度（与人眼亮度敏感度一致）
- **Z**：近似蓝色响应（但非纯蓝）

**XYZ 色度图（CIE 1931）：**
```text
                    520nm (绿)
                      ●
                     / \
                    /   \
                   /     \
                  /       \
                 /  白光   \
                /   (D65)  \
               /     ●     \
              /             \
             /               \
            /                 \
           /                   \
          /                     \
         /                       \
        ●_________________________\●
    700nm (红)                400nm (蓝)

马蹄形曲线：光谱轨迹（纯光谱色）
内部区域：人眼可见的所有颜色
D65 白点：日光标准（x=0.3127, y=0.3290）
```

**RGB→XYZ 转换矩阵（sRGB D65）：**

$$
\begin{bmatrix} X \\ Y \\ Z \end{bmatrix} = \begin{bmatrix}
0.4124 & 0.3576 & 0.1805 \\
0.2126 & 0.7152 & 0.0722 \\
0.0193 & 0.1192 & 0.9505
\end{bmatrix} \begin{bmatrix} R_{linear} \\ G_{linear} \\ B_{linear} \end{bmatrix}
$$

**常见光源的参考白点：**

| 光源 | 名称 | 色温 | Xn | Yn | Zn | 应用场景 |
|------|------|------|----|----|----|----------|
| **D65** | 日光 | 6500K | 0.95047 | 1.00000 | 1.08883 | sRGB、 HDTV、标准观察条件 |
| **D50** | 日光 | 5000K | 0.96422 | 1.00000 | 0.82521 | 印刷、摄影 |
| **A** | 白炽灯 | 2856K | 1.09850 | 1.00000 | 0.35585 | 室内照明 |
| **C** | 平均日光 | 6774K | 0.98074 | 1.00000 | 1.18232 | 旧标准（已弃用） |

#### 6.4.4. CIE Lab 颜色空间（CIELAB, L*a*b*）
**Lab 几何模型 - 三维直角坐标系：**

```text
                    L* (亮度)
                    ↑
                    |  L*=100 (白)
                    |
                    |
        b* (蓝←→黄) | a* (绿←→红)
           ←--------●--------→
         -b*       /|\       +a*
        (蓝)      / | \      (红)
                 /  |  \
                /   |   \
               /    |    \
              /     |     \
             /      |      \
            /       |       \
           /        |        \
          /         |         \
         /          |          \
        /___________|___________\
       -a* (绿)    |           +b* (黄)
                   |
                   |
                   |
                   L*=0 (黑)
```

**Lab 三个分量的物理意义：**

| 分量 | 范围 | 0 值含义 | 正值含义 | 负值含义 |
|------|------|----------|----------|----------|
| **L*** | 0-100 | - | 更亮 | 更暗 |
| **a*** | -128~+127 | 中性灰 | 红色品红 | 绿色 |
| **b*** | -128~+127 | 中性灰 | 黄色 | 蓝色青色 |

**Lab 颜色示例：**

| 颜色 | L* | a* | b* | 说明 |
|------|----|----|----|------|
| **白色** | 100 | 0 | 0 | 最亮，无色彩 |
| **黑色** | 0 | 0 | 0 | 最暗，无色彩 |
| **中灰** | 50 | 0 | 0 | 中等亮度，无色彩 |
| **纯红** | 53 | 80 | 67 | 高亮度，强红黄 |
| **纯绿** | 88 | -86 | 83 | 很高亮度，强绿黄 |
| **纯蓝** | 32 | 79 | -108 | 低亮度，红蓝（品蓝） |
| **黄色** | 97 | -15 | 94 | 很高亮度，强黄 |
| **肤色** | 70-80 | 5-15 | 15-25 | 中等偏高亮度，微红黄 |

**Lab 的应用场景：**
- **色差计算**：ΔE 公式直接计算颜色差异。
- **图像增强**：单独调整 L*（亮度）不影响颜色。
- **颜色校正**：基于感知的颜色调整。
- **印刷行业**：油墨配色、颜色匹配。
- **质量控制**：产品颜色一致性检测。

#### 6.4.5. CIE Luv 颜色空间（CIELUV）
**Luv 与 Lab 的区别：**

| 特性 | Lab | Luv |
|------|-----|-----|
| **设计目的** | 印刷、反射表面 | 显示设备、发射光源 |
| **均匀性** | 整体均匀 | 在低饱和度区域更均匀 |
| **计算复杂度** | 较高（立方根） | 较低（线性比） |
| **色差精度** | 更好（ΔE*ab） | 稍差（ΔE*uv） |
| **应用场景** | 印刷、摄影、涂料 | 电视、显示器、 LED |

**Luv 三个分量的物理意义：**

| 分量 | 范围 | 说明 |
|------|------|------|
| **L*** | 0-100 | 亮度（同 Lab） |
| **u*** | -100~+100 | 红↔绿轴（基于 XYZ 的 u' 色度坐标） |
| **v*** | -100~+100 | 黄↔蓝轴（基于 XYZ 的 v' 色度坐标） |

**Luv 的应用场景：**
- **显示器校准**： RGB→Luv→调整→RGB。
- **视频编码**：基于感知的颜色量化。
- **LED 配色**：光源颜色匹配。
- **色度分析**：光谱功率分布分析。

#### 6.4.6. 色差计算（ΔE - Delta E）
**色差是 Lab/Luv 最重要的应用之一，用于量化两种颜色的差异。**

**CIE76 色差公式（欧几里得距离）：**

$$
\Delta E^*_{ab} = \sqrt{(L^*_2 - L^*_1)^2 + (a^*_2 - a^*_1)^2 + (b^*_2 - b^*_1)^2}
$$

**CIE94 色差公式：**

$$
\Delta E^*_{94} = \sqrt{\left(\frac{\Delta L^*}{k_L S_L}\right)^2 + \left(\frac{\Delta C^*_{ab}}{k_C S_C}\right)^2 + \left(\frac{\Delta H^*_{ab}}{k_H S_H}\right)^2}
$$

其中：
- $\Delta C^*_{ab}$ = 彩度差。
- $\Delta H^*_{ab}$ = 色相差。
- $k_L, k_C, k_H$ = 应用相关参数。
- $S_L, S_C, S_H$ = 权重函数。

**CIEDE2000：**

在 CIE94 基础上进一步改进，考虑了：
- 彩度依赖的权重。
- 色相依赖的权重。
- 彩度 - 色相交互作用

**ΔE 感知阈值：**

| ΔE 范围 | 感知程度 | 应用场景 |
|---------|----------|----------|
| **ΔE < 1.0** | 人眼无法察觉 | 高端印刷、专业摄影 |
| **ΔE = 1.0-2.0** | 仔细观察可察觉 | 质量控制、颜色匹配 |
| **ΔE = 2.0-3.5** | 明显可察觉 | 一般印刷、显示 |
| **ΔE = 3.5-5.0** | 明显不同 | 可接受的产品色差 |
| **ΔE > 5.0** | 完全不同颜色 | 不合格品 |
| **ΔE > 10.0** | 截然不同的颜色 | 明显错误 |

> **注意：**
> - Lab 和 Luv 转换需要先将 RGB 转换到 XYZ 颜色空间。
> - HGPP 使用 **D65 标准光源** 作为参考白点（日光，色温 6500K）。
> - Lab 更适合色差计算（ΔE）， Luv 更适合显示设备校准。
> - **归一化范围**： HGPP 中 L*=[0,255] 对应 0-100， a*/b*=[0,255] 对应 -128 到 +127 （8 位图像）。

#### 6.4.7. RGB→XYZ 转换（D65 参考白点）
**步骤 1：归一化并线性化 RGB （sRGB 伽马校正逆运算）**

对于每个通道（R、 G、 B），归一化到 [0,1] 并应用逆 sRGB 伽马：

$$
C_{linear} = \begin{cases}
C_{sRGB} / 12.92 & \text{if } C_{sRGB} \leq 0.04045 \\
((C_{sRGB} + 0.055) / 1.055)^{2.4} & \text{if } C_{sRGB} > 0.04045
\end{cases}
$$

其中 $C_{sRGB} = R/255, G/255, B/255$。

**步骤 2： RGB→XYZ 矩阵变换（sRGB D65）**

$$
\begin{bmatrix} X \\ Y \\ Z \end{bmatrix} = \begin{bmatrix}
0.4124 & 0.3576 & 0.1805 \\
0.2126 & 0.7152 & 0.0722 \\
0.0193 & 0.1192 & 0.9505
\end{bmatrix} \begin{bmatrix} R_{linear} \\ G_{linear} \\ B_{linear} \end{bmatrix}
$$

**参考白点（D65）：** $X_n = 0.95047, \quad Y_n = 1.00000, \quad Z_n = 1.08883$。

#### 6.4.8. XYZ→Lab 转换公式
**步骤 1：归一化 XYZ**

$$
x_r = X/X_n, \quad y_r = Y/Y_n, \quad z_r = Z/Z_n
$$

**步骤 2：应用立方根函数**

$$
f(t) = \begin{cases}
t^{1/3} & \text{if } t > 0.008856 \\
(903.3 \times t + 16) / 116 & \text{if } t \leq 0.008856
\end{cases}
$$

**步骤 3：计算 Lab**

$$
\begin{aligned}
L^* &= 116 \times f(y_r) - 16 \\
a^* &= 500 \times [f(x_r) - f(y_r)] \\
b^* &= 200 \times [f(y_r) - f(z_r)]
\end{aligned}
$$

#### 6.4.9. Lab→XYZ 逆转换公式
**步骤 1：从 L* 计算 fy**

$$
f_y = (L^* + 16) / 116
$$

**步骤 2：计算 fx 和 fz**

$$
f_x = a^*/500 + f_y, \quad f_z = f_y - b^*/200
$$

**步骤 3：逆立方根函数**

$$
t = \begin{cases}
f(t)^3 & \text{if } f(t) > 0.206893 \\
(f(t) - 16/116) / 7.787 & \text{if } f(t) \leq 0.206893
\end{cases}
$$

**步骤 4：计算 XYZ**

$$
X = X_n \times x_r, \quad Y = Y_n \times y_r, \quad Z = Z_n \times z_r
$$

#### 6.4.10. XYZ→Luv 转换公式
**步骤 1：计算中间值**

$$
\begin{aligned}
u' &= \frac{4X}{X + 15Y + 3Z}, \quad v' = \frac{9Y}{X + 15Y + 3Z} \\
u'_n &= \frac{4X_n}{X_n + 15Y_n + 3Z_n}, \quad v'_n = \frac{9Y_n}{X_n + 15Y_n + 3Z_n}
\end{aligned}
$$

**步骤 2：计算 Luv**

$$
\begin{aligned}
L^* &= \begin{cases}
116 \times (Y/Y_n)^{1/3} - 16 & \text{if } Y/Y_n > 0.008856 \\
903.3 \times (Y/Y_n) & \text{if } Y/Y_n \leq 0.008856
\end{cases} \\
u^* &= 13 \times L^* \times (u' - u'_n) \\
v^* &= 13 \times L^* \times (v' - v'_n)
\end{aligned}
$$

#### 6.4.11. 色差计算（ΔE）
**CIE76 色差公式（欧几里得距离）：**

$$
\Delta E^*_{ab} = \sqrt{(L^*_2 - L^*_1)^2 + (a^*_2 - a^*_1)^2 + (b^*_2 - b^*_1)^2}
$$

**感知阈值：**
- ΔE < 1：人眼无法察觉
- ΔE = 1-2：仔细观察可察觉。
- ΔE = 2-10：明显可察觉。
- ΔE > 10：明显不同颜色

#### 6.4.12. 函数列表
##### 6.4.12.1. RGBToLab
```c
// 三通道Packet RGB → 三通道Packet Lab
HgppStatus hgppiRGBToLab_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                     HGpp8u *pDst, int nDstStep,
                                     HgppiSize oSizeROI,
                                     HgppStreamContext hgppStreamCtx)

// 三通道Planar RGB → 三通道Planar Lab
HgppStatus hgppiRGBToLab_8u_P3R_Ctx(const HGpp8u *const pSrc[3], int nSrcStep,
                                     HGpp8u *pDst[3], int nDstStep,
                                     HgppiSize oSizeROI,
                                     HgppStreamContext hgppStreamCtx)
```

##### 6.4.12.2. LabToRGB （逆转换）
```c
// 三通道Packet Lab → 三通道Packet RGB
HgppStatus hgppiLabToRGB_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                     HGpp8u *pDst, int nDstStep,
                                     HgppiSize oSizeROI,
                                     HgppStreamContext hgppStreamCtx)

// 三通道Planar Lab → 三通道Planar RGB
HgppStatus hgppiLabToRGB_8u_P3R_Ctx(const HGpp8u *const pSrc[3], int nSrcStep,
                                     HGpp8u *pDst[3], int nDstStep,
                                     HgppiSize oSizeROI,
                                     HgppStreamContext hgppStreamCtx)
```

##### 6.4.12.3. RGBToLuv / LuvToRGB
```c
HgppStatus hgppiRGBToLuv_8u_C3R_Ctx(...)
HgppStatus hgppiLuvToRGB_8u_C3R_Ctx(...)
HgppStatus hgppiRGBToLuv_8u_P3R_Ctx(...)
HgppStatus hgppiLuvToRGB_8u_P3R_Ctx(...)
```

**16 位/32 位版本**

```c
HgppStatus hgppiRGBToLab_16u_C3R_Ctx(...)
HgppStatus hgppiLabToRGB_16u_C3R_Ctx(...)
HgppStatus hgppiRGBToLab_32f_C3R_Ctx(...)
HgppStatus hgppiLabToRGB_32f_C3R_Ctx(...)
```

### 6.5. YUV 采样格式
#### 6.5.1. 功能介绍
YUV 采样格式转换函数，用于在不同 YUV 子采样格式之间转换，如 YUV420、 YUV422、 YUV411、 NV12、 NV21 等。

**YUV 采样基础知识：**

YUV 使用亮度（Y）和色度（UV）分离的方式表示颜色。由于人眼对亮度更敏感，色度可以进行子采样以节省带宽和存储空间。

**采样格式命名规则（J: a: b）：**
- **J** = 水平采样参考（通常为 4）
- **a** = 第一行的色度采样数。
- **b** = 第二行的色度采样数（与第一行相同则为 0）

| 格式 | J: a: b | 色度采样 | 带宽占比 | 应用场景 |
|------|-------|----------|----------|----------|
| **YUV444** | 4:4:4 | 无色度采样 | 100% | 高端视频、后期制作 |
| **YUV422** | 4:2:2 | 水平减半 | 67% | 专业视频、广播 |
| **YUV420** | 4:2:0 | 水平和垂直都减半 | 50% | 蓝光、 H.264/265、网络视频 |
| **YUV411** | 4:1:1 | 水平减为 1/4 | 50% | DV 摄像机 |
| **YUV410** | 4:1:0 | 水平和垂直都减为 1/4 | 37.5% | 早期视频压缩 |

#### 6.5.2. YUV 格式详解与示意图
##### 6.5.2.1. YUV444 （4:4:4）- 无色度采样
**特点：** Y、 U、 V 三个分量都是全分辨率，无压缩。

**内存布局（Planar 格式）：**
```text
Y Planar（全分辨率）：    U Planar（全分辨率）：    V Planar（全分辨率）：
Y00 Y01 Y02 Y03        U00 U01 U02 U03        V00 V01 V02 V03
Y10 Y11 Y12 Y13        U10 U11 U12 U13        V10 V11 V12 V13
Y20 Y21 Y22 Y23        U20 U21 U22 U23        V20 V21 V22 V23
Y30 Y31 Y32 Y33        U30 U31 U32 U33        V30 V31 V32 V33

每个像素：1 个 Y + 1 个 U + 1 个 V = 3 字节/像素
```

##### 6.5.2.2. YUV422 （4:2:2）- 水平色度减半
**特点：** Y 分量全分辨率， U 和 V 分量水平方向减半，垂直方向全分辨率。

**Planar 格式示意图：**
```text
原始像素网格（4×4）：
Y00 U00 Y01 V00 Y02 U01 Y03 V01    ← 第 0 行：U/V 水平减半
Y10 U10 Y11 V10 Y12 U11 Y13 V11    ← 第 1 行：U/V 水平减半
Y20 U20 Y21 V20 Y22 U21 Y23 V21    ← 第 2 行：U/V 水平减半
Y30 U30 Y31 V30 Y32 U31 Y33 V31    ← 第 3 行：U/V 水平减半

Y Planar（4×4 全分辨率）：    U Planar（4×2 水平减半）：   V Planar（4×2 水平减半）：
Y00 Y01 Y02 Y03            U00 U01                    V00 V01
Y10 Y11 Y12 Y13            U10 U11                    V10 V11
Y20 Y21 Y22 Y23            U20 U21                    V20 V21
Y30 Y31 Y32 Y33            U30 U31                    V30 V31

每个像素：1 个 Y + 0.5 个 U + 0.5 个 V = 2 字节/像素
```

**Packet 格式（UYVY/YUY2）：**
```text
UYVY Packet（每 4 字节 = 2 像素）：
[U00 Y00 V00 Y01]  [U10 Y10 V10 Y11]  [U20 Y20 V20 Y21]  [U30 Y30 V30 Y31]
  ↑    ↑    ↑    ↑
  U    Y    V    Y   ← U/V 被两个 Y 像素共享

内存布局：U0 Y0 V0 Y1 | U1 Y2 V1 Y3 | U2 Y4 V2 Y5 | U3 Y6 V3 Y7
```

##### 6.5.2.3. YUV420 （4:2:0）- 水平和垂直色度都减半
**特点：** Y 分量全分辨率， U 和 V 分量水平和垂直方向都减半。

**Planar 格式（I420）示意图：**
```text
原始像素网格（4×4）：
Y00 .  Y01 .  Y02 .  Y03 .      ← 第 0 行：有 Y，U/V 采样
.  .  .  .  .  .  .  .          ← 第 1 行：有 Y，无 U/V 采样
Y10 .  Y11 .  Y12 .  Y13 .      ← 第 2 行：有 Y，U/V 采样
.  .  .  .  .  .  .  .          ← 第 3 行：有 Y，无 U/V 采样

Y Planar（4×4 全分辨率）：    U Planar（2×2 都减半）：      V Planar（2×2 都减半）：
Y00 Y01 Y02 Y03            U00 U01                  V00 V01
Y10 Y11 Y12 Y13            U10 U11                  V10 V11
Y20 Y21 Y22 Y23
Y30 Y31 Y32 Y33

I420 内存布局：[Y Planar] + [U Planar] + [V Planar]
              16 字节      4 字节      4 字节     = 24 字节（4×4 图像）

每个像素：1 个 Y + 0.25 个 U + 0.25 个 V = 1.5 字节/像素
```

**NV12 格式（Y Planar + UV 交错）：**
```text
NV12 内存布局：
[Y Planar（全分辨率）]  [UV 交错Planar（半分辨率）]
Y00 Y01 Y02 Y03      U00 V00 U01 V01
Y10 Y11 Y12 Y13      U10 V10 U11 V11
Y20 Y21 Y22 Y23
Y30 Y31 Y32 Y33

UV Planar中，U 和 V 交错存储：U0 V0 U1 V1 ...
```

**NV21 格式（Y Planar + VU 交错）：**
```text
NV21 内存布局（与 NV12 相比，UV 顺序相反）：
[Y Planar（全分辨率）]  [VU 交错Planar（半分辨率）]
Y00 Y01 Y02 Y03      V00 U00 V01 U01
Y10 Y11 Y12 Y13      V10 U10 V11 U11
Y20 Y21 Y22 Y23
Y30 Y31 Y32 Y33

VU Planar中，V 在前，U 在后：V0 U0 V1 U1 ...
```

##### 6.5.2.4. YUV411 （4:1:1）- 水平色度减为 1/4
**特点：** Y 分量全分辨率， U 和 V 分量水平方向减为 1/4，垂直方向全分辨率。

**Planar 格式示意图：**
```text
原始像素网格（8×2）：
Y00 .  .  .  Y01 .  .  .  Y02 .  .  .  Y03 .  .  .    ← 每 4 个 Y 共享 1 个 U/V
Y10 .  .  .  Y11 .  .  .  Y12 .  .  .  Y13 .  .  .

Y Planar（8×2 全分辨率）：    U Planar（2×2 水平 1/4）：    V Planar（2×2 水平 1/4）：
Y00 Y01 Y02 Y03 Y04 Y05    U00 U01                    V00 V01
Y10 Y11 Y12 Y13 Y14 Y15    U10 U11                    V10 V11

每个像素：1 个 Y + 0.25 个 U + 0.25 个 V = 1.5 字节/像素
```

##### 6.5.2.5. YUV410 （4:1:0）- 水平和垂直色度都减为 1/4
**特点：** Y 分量全分辨率， U 和 V 分量水平和垂直方向都减为 1/4。

**Planar 格式示意图：**
```text
原始像素网格（8×4）：
Y00 .  .  .  Y01 .  .  .  Y02 .  .  .  Y03 .  .  .    ← 第 0 行：有 U/V
.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .        ← 第 1 行：无 U/V
.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .        ← 第 2 行：无 U/V
.  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .        ← 第 3 行：无 U/V
Y10 .  .  .  Y11 .  .  .  Y12 .  .  .  Y13 .  .  .    ← 第 4 行：有 U/V

Y Planar（8×4 全分辨率）：    U Planar（2×1 都减 1/4）：     V Planar（2×1 都减 1/4）：
Y00 Y01 Y02 Y03 Y04 Y05    U00 U01                    V00 V01
Y10 Y11 Y12 Y13 Y14 Y15
Y20 Y21 Y22 Y23 Y24 Y25
Y30 Y31 Y32 Y33 Y34 Y35

每个像素：1 个 Y + 0.0625 个 U + 0.0625 个 V = 1.125 字节/像素
```

#### 6.5.3. Packet 格式 vs Planar 格式
| 特性 | Packet 格式（Packed） | Planar 格式（Planar） |
|------|-------------------|-------------------|
| **存储方式** | YUV 交错存储 | Y、 U、 V 分别存储 |
| **示例** | YUY2, UYVY, YVYU, VYUY | I420, I422, I444, NV12, NV21 |
| **优点** | 内存访问局部性好 | 便于单独处理 Y 分量（如灰度处理） |
| **缺点** | 色度抽取较复杂 | 需要多个内存 Planar |
| **应用场景** | 视频采集卡、 DirectShow | 视频编码（H.264/265）、 OpenGL 纹理 |

**Packet 格式示例（YUY2）：**
```text
Y0 U0 Y1 V0  |  Y2 U1 Y3 V1  |  Y4 U2 Y5 V2  |  Y6 U3 Y7 V3
↑  ↑  ↑  ↑     ↑  ↑  ↑  ↑
Y  U  Y  V     Y  U  Y  V
像素 0,1       像素 2,3
```

**Planar 格式示例（I420）：**
```text
[Y Planar：全部 Y 像素]  [U Planar：全部 U 像素]  [V Planar：全部 V 像素]
YYYYYYYYYYYYYYY       UUUUUUUU            VVVVVVVV
```

#### 6.5.4. HGPP 支持的 YUV 格式汇总
| HGPP 函数前缀 | 格式 | 说明 |
|--------------|------|------|
| `YCbCr420` | I420/NV12 | 4:2:0 Planar 或 Semi Planar 格式 |
| `YCbCr422` | I422/YUY2 | 4:2:2 Planar 或 Packet 格式 |
| `YCbCr411` | 4:1:1 | 4:1:1 Planar 格式 |
| `NV12` | NV12 | Y Planar + UV 交错 |
| `NV21` | NV21 | Y Planar + VU 交错 |

> **注意：**
> - **YUV420**： Y 分量全分辨率， U 和 V 分量水平和垂直都减半（4:2:0）
> - **YUV422**： Y 分量全分辨率， U 和 V 分量水平减半（4:2:2）
> - **YUV411**： Y 分量全分辨率， U 和 V 分量水平减为 1/4 （4:1:1）
> - **NV12**： Y Planar + UV 交错 Planar （半分辨率）
> - **NV21**： Y Planar + VU 交错 Planar （半分辨率， UV 顺序与 NV12 相反）

#### 6.5.5. 完整参数说明
##### 6.5.5.1. YUV 采样格式转换通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | **源图像指针** - Packet 格式或 Planar 指针数组 |
| `nSrcStep` | int | [in] | **源图像行步幅**（字节）， Packet 格式使用 |
| `aSrcStep[]` | int 数组 | [in] | **源图像步幅数组** - Planar 格式使用 |
| `pDst` | 设备指针 | [out] | **目标图像指针** - Packet 格式或 Planar 指针数组 |
| `nDstStep` | int | [in] | **目标图像行步幅**（字节）， Packet 格式使用 |
| `aDstStep[]` | int 数组 | [in] | **目标图像步幅数组** - Planar 格式使用 |
| `oSizeROI` | HgppiSize | [in] | **感兴趣区域** - ROI 宽度和高度（像素） |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

**返回值：** `HgppStatus` - 图像数据相关错误码、 ROI 相关错误码。

#### 6.5.6. 函数列表
##### 6.5.6.1. YUV420 ↔ YUV422
```c
// YCbCr420 Planar → YCbCr422 Planar
HgppStatus hgppiYCbCr420ToYCbCr422_8u_P3R_Ctx(const HGpp8u *const pSrc[3], int aSrcStep[3],
                                               HGpp8u *pDst[3], int aDstStep[3],
                                               HgppiSize oSizeROI,
                                               HgppStreamContext hgppStreamCtx)

// YCbCr422 Planar → YCbCr420 Planar
HgppStatus hgppiYCbCr422ToYCbCr420_8u_P3R_Ctx(const HGpp8u *const pSrc[3], int aSrcStep[3],
                                               HGpp8u *pDst[3], int aDstStep[3],
                                               HgppiSize oSizeROI,
                                               HgppStreamContext hgppStreamCtx)

// YCbCr422 Packet → YCbCr420 Planar
HgppStatus hgppiYCbCr422ToYCbCr420_8u_C2P3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                                 HGpp8u *pDst[3], int aDstStep[3],
                                                 HgppiSize oSizeROI,
                                                 HgppStreamContext hgppStreamCtx)
```

##### 6.5.6.2. YUV422 ↔ YUV411
```c
// YCbCr422 Planar → YCbCr411 Planar
HgppStatus hgppiYCbCr422ToYCbCr411_8u_P3R_Ctx(const HGpp8u *const pSrc[3], int aSrcStep[3],
                                               HGpp8u *pDst[3], int aDstStep[3],
                                               HgppiSize oSizeROI,
                                               HgppStreamContext hgppStreamCtx)

// YCbCr420 Planar → YCbCr411 Planar
HgppStatus hgppiYCbCr420ToYCbCr411_8u_P3P2R_Ctx(const HGpp8u *const pSrc[3], int aSrcStep[3],
                                                 HGpp8u *pDstY, int nDstYStep,
                                                 HGpp8u *pDstCbCr, int nDstCbCrStep,
                                                 HgppiSize oSizeROI,
                                                 HgppStreamContext hgppStreamCtx)
```

##### 6.5.6.3. Packet↔Planar 转换
```c
// YCbCr422 Packet → YCbCr422 Planar
HgppStatus hgppiYCbCr422_8u_C2P3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                       HGpp8u *pDst[3], int aDstStep[3],
                                       HgppiSize oSizeROI,
                                       HgppStreamContext hgppStreamCtx)

// YCbCr422 Planar → YCbCr422 Packet
HgppStatus hgppiYCbCr422_8u_P3C2R_Ctx(const HGpp8u *const pSrc[3], int aSrcStep[3],
                                       HGpp8u *pDst, int nDstStep,
                                       HgppiSize oSizeROI,
                                       HgppStreamContext hgppStreamCtx)
```

##### 6.5.6.4. NV12/NV21 转换
```c
// RGB → NV12
HgppStatus hgppiRGBToNV12_8u_C3P2R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                        HGpp8u *pDst[2], int aDstStep[2],
                                        HgppiSize oSizeROI,
                                        HgppStreamContext hgppStreamCtx)

// RGB Planar → NV12
HgppStatus hgppiRGBToNV12_8u_P3P2R_Ctx(const HGpp8u *const pSrc[3], int aSrcStep[3],
                                        HGpp8u *pDst[2], int aDstStep[2],
                                        HgppiSize oSizeROI,
                                        HgppStreamContext hgppStreamCtx)

// NV12 → RGB
HgppStatus hgppiNV12ToRGB_8u_P2C3R_Ctx(const HGpp8u *const pSrc[2], int aSrcStep[2],
                                        HGpp8u *pDst, int nDstStep,
                                        HgppiSize oSizeROI,
                                        HgppStreamContext hgppStreamCtx)

// NV12 → RGB Planar
HgppStatus hgppiNV12ToRGB_8u_P2P3R_Ctx(const HGpp8u *const pSrc[2], int aSrcStep[2],
                                        HGpp8u *pDst[3], int aDstStep[3],
                                        HgppiSize oSizeROI,
                                        HgppStreamContext hgppStreamCtx)
```

**16 位版本**

```c
HgppStatus hgppiYCbCr420ToYCbCr422_16u_P3R_Ctx(...)
HgppStatus hgppiYCbCr422ToYCbCr420_16u_P3R_Ctx(...)
HgppStatus hgppiYCbCr422ToYCbCr411_16u_P3R_Ctx(...)
HgppStatus hgppiRGBToNV12_16u_C3P2R_Ctx(...)
HgppStatus hgppiNV12ToRGB_16u_P2C3R_Ctx(...)
```

### 6.6. ColorTwist
#### 6.6.1. 功能介绍
ColorTwist （颜色扭曲）函数在颜色空间转换的同时应用用户提供的 3×4 系数矩阵进行颜色校正。这允许在转换过程中进行精确的颜色空间算术。

> **注意：**
> - ColorTwist 是 3 通道操作，通常应用于 RGB 数据。
> - 系数矩阵为 3×4 浮点矩阵，第 4 列是偏移量。
> - 正向变换（RGB→YUV）：先应用 3×3 矩阵，然后加上偏移量。
> - 逆向变换（YUV→RGB）：**先加上偏移量**，然后应用 3×3 逆矩阵。

#### 6.6.2. ColorTwist 矩阵说明
**正向变换（RGB→YUV420/YUV422/NV12）：**

$$
\begin{aligned}
\text{dst}[0] &= aTwist[0][0] \times \text{src}[0] + aTwist[0][1] \times \text{src}[1] + aTwist[0][2] \times \text{src}[2] + aTwist[0][3] \\
\text{dst}[1] &= aTwist[1][0] \times \text{src}[0] + aTwist[1][1] \times \text{src}[1] + aTwist[1][2] \times \text{src}[2] + aTwist[1][3] \\
\text{dst}[2] &= aTwist[2][0] \times \text{src}[0] + aTwist[2][1] \times \text{src}[1] + aTwist[2][2] \times \text{src}[2] + aTwist[2][3]
\end{aligned}
$$

**逆向变换（YUV420/YUV422/NV12→RGB）：**

> **注意：**
> 偏移量（第 4 列）**先应用**，然后应用 3×3 矩阵。

$$
\begin{aligned}
\text{src}[0]' &= \text{src}[0] + aTwist[0][3] \\
\text{src}[1]' &= \text{src}[1] + aTwist[1][3] \\
\text{src}[2]' &= \text{src}[2] + aTwist[2][3] \\
\text{dst}[0] &= aTwist[0][0] \times \text{src}[0]' + aTwist[0][1] \times \text{src}[1]' + aTwist[0][2] \times \text{src}[2]' \\
\text{dst}[1] &= aTwist[1][0] \times \text{src}[0]' + aTwist[1][1] \times \text{src}[1]' + aTwist[1][2] \times \text{src}[2]' \\
\text{dst}[2] &= aTwist[2][0] \times \text{src}[0]' + aTwist[2][1] \times \text{src}[1]' + aTwist[2][2] \times \text{src}[2]'
\end{aligned}
$$

> **注意：**
> - 对于 16u 图像，偏移量使用 ±16384 （而 8u 图像使用 ±128）。
> - 这是因为 16 位图像的数值范围是 8 位图像的 256 倍。

#### 6.6.3. 完整参数说明
##### 6.6.3.1. ColorTwist 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | **源图像指针** - Packet 格式或 Planar 指针数组 |
| `nSrcStep` | int | [in] | **源图像行步幅**（字节）， Packet 格式使用 |
| `aSrcStep[]` | int 数组 | [in] | **源图像步幅数组** - Planar 格式使用 |
| `pDst` | 设备指针 | [out] | **目标图像指针** - Packet 格式或 Planar 指针数组 |
| `nDstStep` | int | [in] | **目标图像行步幅**（字节）， Packet 格式使用 |
| `aDstStep[]` | int 数组 | [in] | **目标图像步幅数组** - Planar 格式使用 |
| `oSizeROI` | HgppiSize | [in] | **感兴趣区域** - ROI 宽度和高度（像素） |
| `aTwist` | float[3][4] | [in] | **颜色扭曲矩阵** - 3×4 浮点系数矩阵 |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

**返回值：** `HgppStatus` - 图像数据相关错误码、 ROI 相关错误码。

#### 6.6.4. 函数列表
##### 6.6.4.1. RGBToYUV420_ColorTwist
**8 位无符号整数**

```c
// Planar RGB → Planar YUV420（带 ColorTwist）
HgppStatus hgppiRGBToYUV420_8u_ColorTwist32f_P3R_Ctx(const HGpp8u *const pSrc[3], int aSrcStep[3],
                                                      HGpp8u *pDst[3], int aDstStep[3],
                                                      HgppiSize oSizeROI,
                                                      const Hgpp32f aTwist[3][4],
                                                      HgppStreamContext hgppStreamCtx)

// Packet RGB → Planar YUV420（带 ColorTwist）
HgppStatus hgppiRGBToYUV420_8u_ColorTwist32f_C3P3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                                        HGpp8u *pDst[3], int aDstStep[3],
                                                        HgppiSize oSizeROI,
                                                        const Hgpp32f aTwist[3][4],
                                                        HgppStreamContext hgppStreamCtx)
```

**16 位无符号整数**

```c
HgppStatus hgppiRGBToYUV420_16u_ColorTwist32f_P3R_Ctx(...)
HgppStatus hgppiRGBToYUV420_16u_ColorTwist32f_C3P3R_Ctx(...)
```

##### 6.6.4.2. RGBToYUV422_ColorTwist
```c
// Planar RGB → Planar YUV422（带 ColorTwist）
HgppStatus hgppiRGBToYUV422_8u_ColorTwist32f_P3R_Ctx(const HGpp8u *const pSrc[3], int aSrcStep[3],
                                                      HGpp8u *pDst[3], int aDstStep[3],
                                                      HgppiSize oSizeROI,
                                                      const Hgpp32f aTwist[3][4],
                                                      HgppStreamContext hgppStreamCtx)

// Packet RGB → Packet YUV422（带 ColorTwist）
HgppStatus hgppiRGBToYUV422_8u_ColorTwist32f_C3C2R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                                        HGpp8u *pDst, int nDstStep,
                                                        HgppiSize oSizeROI,
                                                        const Hgpp32f aTwist[3][4],
                                                        HgppStreamContext hgppStreamCtx)

// Packet RGB → Planar YUV422（带 ColorTwist）
HgppStatus hgppiRGBToYUV422_8u_ColorTwist32f_C3P3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                                        HGpp8u *pDst[3], int aDstStep[3],
                                                        HgppiSize oSizeROI,
                                                        const Hgpp32f aTwist[3][4],
                                                        HgppStreamContext hgppStreamCtx)
```

**16 位版本**

```c
HgppStatus hgppiRGBToYUV422_16u_ColorTwist32f_P3R_Ctx(...)
HgppStatus hgppiRGBToYUV422_16u_ColorTwist32f_C3C2R_Ctx(...)
HgppStatus hgppiRGBToYUV422_16u_ColorTwist32f_C3P3R_Ctx(...)
```

##### 6.6.4.3. RGBToNV12_ColorTwist
```c
// Packet RGB → Planar NV12（带 ColorTwist）
HgppStatus hgppiRGBToNV12_8u_ColorTwist32f_C3P2R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                                      HGpp8u *pDst[2], int aDstStep[2],
                                                      HgppiSize oSizeROI,
                                                      const Hgpp32f aTwist[3][4],
                                                      HgppStreamContext hgppStreamCtx)

// Planar RGB → Planar NV12（带 ColorTwist）
HgppStatus hgppiRGBToNV12_8u_ColorTwist32f_P3P2R_Ctx(const HGpp8u *const pSrc[3], int aSrcStep[3],
                                                      HGpp8u *pDst[2], int aDstStep[2],
                                                      HgppiSize oSizeROI,
                                                      const Hgpp32f aTwist[3][4],
                                                      HgppStreamContext hgppStreamCtx)
```

**16 位版本**

```c
HgppStatus hgppiRGBToNV12_16u_ColorTwist32f_C3P2R_Ctx(...)
HgppStatus hgppiRGBToNV12_16u_ColorTwist32f_P3P2R_Ctx(...)
```

##### 6.6.4.4. YUV420ToRGB_ColorTwist （逆向）
```c
// Planar YUV420 → Planar RGB（带逆向 ColorTwist）
HgppStatus hgppiYUV420ToRGB_8u_ColorTwist32f_P3R_Ctx(const HGpp8u *const pSrc[3], int aSrcStep[3],
                                                      HGpp8u *pDst[3], int aDstStep[3],
                                                      HgppiSize oSizeROI,
                                                      const Hgpp32f aTwist[3][4],
                                                      HgppStreamContext hgppStreamCtx)
```

**16 位版本**

```c
HgppStatus hgppiYUV420ToRGB_16u_ColorTwist32f_P3R_Ctx(...)
```

##### 6.6.4.5. YUV422ToRGB_ColorTwist （逆向）
```c
// Planar YUV422 → Planar RGB（带逆向 ColorTwist）
HgppStatus hgppiYUV422ToRGB_8u_ColorTwist32f_P3R_Ctx(const HGpp8u *const pSrc[3], int aSrcStep[3],
                                                      HGpp8u *pDst[3], int aDstStep[3],
                                                      HgppiSize oSizeROI,
                                                      const Hgpp32f aTwist[3][4],
                                                      HgppStreamContext hgppStreamCtx)

// Packet YUV422 → Packet RGB（带逆向 ColorTwist）
HgppStatus hgppiYUV422ToRGB_8u_ColorTwist32f_C2C3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                                        HGpp8u *pDst, int nDstStep,
                                                        HgppiSize oSizeROI,
                                                        const Hgpp32f aTwist[3][4],
                                                        HgppStreamContext hgppStreamCtx)
```

**16 位版本**

```c
HgppStatus hgppiYUV422ToRGB_16u_ColorTwist32f_P3R_Ctx(...)
HgppStatus hgppiYUV422ToRGB_16u_ColorTwist32f_C2C3R_Ctx(...)
```

##### 6.6.4.6. NV12ToRGB_ColorTwist （逆向）
```c
// Planar NV12 → Packet RGB（带逆向 ColorTwist）
HgppStatus hgppiNV12ToRGB_8u_ColorTwist32f_P2C3R_Ctx(const HGpp8u *const pSrc[2], int aSrcStep[2],
                                                      HGpp8u *pDst, int nDstStep,
                                                      HgppiSize oSizeROI,
                                                      const Hgpp32f aTwist[3][4],
                                                      HgppStreamContext hgppStreamCtx)

// Planar NV12 → Planar RGB（带逆向 ColorTwist）
HgppStatus hgppiNV12ToRGB_8u_ColorTwist32f_P2P3R_Ctx(const HGpp8u *const pSrc[2], int aSrcStep[2],
                                                      HGpp8u *pDst[3], int aDstStep[3],
                                                      HgppiSize oSizeROI,
                                                      const Hgpp32f aTwist[3][4],
                                                      HgppStreamContext hgppStreamCtx)
```

**16 位版本**

```c
HgppStatus hgppiNV12ToRGB_16u_ColorTwist32f_P2C3R_Ctx(...)
HgppStatus hgppiNV12ToRGB_16u_ColorTwist32f_P2P3R_Ctx(...)
```

### 6.7. 批量转换
#### 6.7.1. 功能介绍
批量转换函数允许同时处理多幅图像，提高 真武 PPU 资源利用率。适用于批量处理较小图像的场景。

> **注意：**
> - 批处理不推荐用于非常大的图像，可能没有足够资源同时处理多幅大图像。
> - **ROI 使用方式因函数类型而异**——有些函数共用统一 ROI，有些函数每个图像可以有自己的 ROI。

#### 6.7.2. ROI 使用方式对比
| 函数类型 | ROI 使用方式 | 说明 |
|----------|-------------|------|
| **YUVToRGBBatch （标准版）** | 统一 ROI | 单个 `oSizeROI` 应用于批处理中的所有图像对 |
| **YUVToRGBBatch_Advanced** | 每图像独立 ROI | 每个图像对可以有自己的 `oSizeROI` |

#### 6.7.3. 完整参数说明
##### 6.7.3.1. YUVToRGBBatch （标准版 - 统一 ROI）
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrcBatchList` | 设备指针 | [in] | **源批处理图像列表** - `HgppiImageDescriptor` 结构数组（设备内存） |
| `pDstBatchList` | 设备指针 | [in] | **目标批处理图像列表** - `HgppiImageDescriptor` 结构数组（设备内存） |
| `nBatchSize` | int | [in] | **批处理大小** - 处理的图像对数量（必须 > 1） |
| `oSizeROI` | HgppiSize | [in] | **统一 ROI** - **单个 ROI 应用于所有图像对**（不能超出任何图像的边界） |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

> **注意：**
> - **单个 `oSizeROI` 应用于批处理中的所有图像对**
> - 用户必须确保提供的 ROI 不超出任何提供图像的边界。
> - `pSrcBatchList` 和 `pDstBatchList` 必须在设备内存中。

##### 6.7.3.2. YUVToRGBBatch_Advanced （每图像独立 ROI）
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrcBatchList` | 设备指针 | [in] | **源批处理图像列表** - `HgppiImageDescriptor` 结构数组（设备内存） |
| `pDstBatchList` | 设备指针 | [in] | **目标批处理图像列表** - `HgppiImageDescriptor` 结构数组（设备内存） |
| `pBatchROI` | 设备指针 | [in] | **每图像 ROI 列表** - `HgppiSize` 结构数组（设备内存），**每个图像对可以有自己的 ROI** |
| `nBatchSize` | int | [in] | **批处理大小** - 图像对数量 |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

> **注意：**
> - **每个图像对可以有自己的 `oSizeROI`**，通过 `pBatchROI` 数组传递。
> - `pSrcBatchList`、`pDstBatchList`、`pBatchROI` 都必须在设备内存中。
> - 用户需要初始化这些结构并复制到设备内存。

#### 6.7.4. 函数列表
##### 6.7.4.1. YUVToRGBBatch （标准版 - 统一 ROI）
**8 位无符号整数**

```c
// 三通道Packet YUV → 三通道Packet RGB（统一 ROI）
HgppStatus hgppiYUVToRGBBatch_8u_C3R_Ctx(const HgppiImageDescriptor *pSrcBatchList,
                                          HgppiImageDescriptor *pDstBatchList,
                                          int nBatchSize, HgppiSize oSizeROI,
                                          HgppStreamContext hgppStreamCtx)

// 三通道Planar YUV → 三通道Packet RGB（统一 ROI）
HgppStatus hgppiYUVToRGBBatch_8u_P3C3R_Ctx(const HgppiImageDescriptor *const pSrcBatchList[3],
                                            HgppiImageDescriptor *pDstBatchList,
                                            int nBatchSize, HgppiSize oSizeROI,
                                            HgppStreamContext hgppStreamCtx)
```

**参数说明：**
- `pSrcBatchList` - 源批处理图像指针数组（对于 Planar 格式，每个元素是一个通道 planar）
- `pDstBatchList` - 目标批处理图像指针。
- `nBatchSize` - 处理的 `HgppiImageDescriptor` 结构数量（必须 > 1）
- `oSizeROI` - **单个 ROI 应用于所有图像对**。

##### 6.7.4.2. YUVToRGBBatch_Advanced （每图像独立 ROI）
**8 位无符号整数**

```c
// 三通道Packet YUV → 三通道Packet RGB（每图像独立 ROI）
HgppStatus hgppiYUVToRGBBatch_8u_C3R_Advanced_Ctx(const HgppiImageDescriptor *pSrcBatchList,
                                                   HgppiImageDescriptor *pDstBatchList,
                                                   const HgppiSize *pBatchROI,
                                                   int nBatchSize,
                                                   HgppStreamContext hgppStreamCtx)

// 三通道Planar YUV → 三通道Packet RGB（每图像独立 ROI）
HgppStatus hgppiYUVToRGBBatch_8u_P3C3R_Advanced_Ctx(const HgppiImageDescriptor *const pSrcBatchList[3],
                                                     HgppiImageDescriptor *pDstBatchList,
                                                     const HgppiSize *pBatchROI,
                                                     int nBatchSize,
                                                     HgppStreamContext hgppStreamCtx)
```

**参数说明：**
- `pBatchROI` - **每图像 ROI 数组**（设备内存），每个元素对应一个图像对的 ROI。

**16 位/32 位版本**

```c
HgppStatus hgppiYUVToRGBBatch_16u_C3R_Ctx(...)
HgppStatus hgppiYUVToRGBBatch_16u_P3C3R_Ctx(...)
HgppStatus hgppiYUVToRGBBatch_16u_C3R_Advanced_Ctx(...)
HgppStatus hgppiYUVToRGBBatch_16u_P3C3R_Advanced_Ctx(...)

HgppStatus hgppiYUVToRGBBatch_32f_C3R_Ctx(...)
HgppStatus hgppiYUVToRGBBatch_32f_P3C3R_Ctx(...)
HgppStatus hgppiYUVToRGBBatch_32f_C3R_Advanced_Ctx(...)
HgppStatus hgppiYUVToRGBBatch_32f_P3C3R_Advanced_Ctx(...)
```

### 6.8. Debayer 去马赛克
#### 6.8.1. 功能介绍
Debayer （去马赛克）函数将 Bayer 格式的单通道 CFA （Color Filter Array，颜色滤波阵列）图像转换为三通道 RGB 图像。这是数码相机和图像传感器的标准处理流程。

**Bayer 模式基础知识：**

Bayer 滤镜是一种马赛克式的颜色滤波阵列，每个像素只捕获一种颜色（R、 G 或 B）。典型的 Bayer 排列如下：

```text
Bayer 网格模式（2×2 重复单元）：

RGGB 模式（最常见）：    BGGR 模式：
R G R G R G            B G B G B G
G B G B G B            G R G R G R
R G R G R G            B G B G B G
G B G B G B            G R G R G R

GBRG 模式：            GRBG 模式：
G B G B G B            G R G R G R
R G R G R G            B G B G G B
G B G B G B            G R G R G R
R G R G R G            B G B G B G
```

**Bayer 网格位置枚举（HgppiBayerGridPosition）：**

| 值 | 说明 | 左上角像素 |
|------|------|------------|
| `HGPP_BAYER_BGGR` | BGGR 模式 | B （蓝色） |
| `HGPP_BAYER_RGGB` | RGGB 模式 | R （红色） |
| `HGPP_BAYER_GBRG` | GBRG 模式 | G （绿色，下方是 B） |
| `HGPP_BAYER_GRBG` | GRBG 模式 | G （绿色，下方是 R） |

> **注意：**
> - Debayer 需要知道 Bayer 网格的起始位置（Grid Position）。
> - 去马赛克算法通过插值从相邻像素恢复缺失的颜色分量。
> - HGPP 提供多种插值算法：最近邻、双线性、自适应等。

#### 6.8.2. Debayer 算法原理
**1. 双线性插值（Bilinear Interpolation）：**

最简单的去马赛克算法，使用相邻像素的线性加权平均。

```text
对于 G 像素（已有 G，需要 R 和 B）：
R = (R_left + R_right) / 2
B = (B_top + B_bottom) / 2

对于 R 像素（已有 R，需要 G 和 B）：
G = (G_top + G_bottom + G_left + G_right) / 4
B = (B_top-left + B_top-right + B_bottom-left + B_bottom-right) / 4
```

**2. 自适应梯度插值（Adaptive Gradient）：**

检测边缘方向，沿边缘方向进行插值以避免伪影。

```text
计算水平和垂直梯度：
grad_h = |R_left - R_right| + |B_top - B_bottom|
grad_v = |R_top - R_bottom| + |B_left - B_right|

如果 grad_h < grad_v：沿水平方向插值
如果 grad_v < grad_h：沿垂直方向插值
```

#### 6.8.3. 完整参数说明
##### 6.8.3.1. Debayer 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | **源 CFA 图像指针** - 单通道 8u/16u Bayer 图像 |
| `nSrcStep` | int | [in] | **源图像行步幅**（字节） |
| `pDst` | 设备指针 | [out] | **目标 RGB 图像指针** - 三通道 Packet 或 Planar 格式 |
| `nDstStep` | int | [in] | **目标图像行步幅**（字节） |
| `oSizeROI` | HgppiSize | [in] | **感兴趣区域** - ROI 宽度和高度（像素） |
| `nBayerPhase` | int | [in] | **Bayer 相位** - 0=BGGR, 1=RGGB, 2=GBRG, 3=GRBG |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

**返回值：** `HgppStatus` - 图像数据相关错误码、 ROI 相关错误码。

#### 6.8.4. 函数列表
##### 6.8.4.1. CFAToRGB （双线性插值）
**8 位无符号整数**

```c
// 单通道 CFA → 三通道Packet RGB（双线性）
HgppStatus hgppiCFAToRGB_8u_C1C3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                       HGpp8u *pDst, int nDstStep,
                                       HgppiSize oSizeROI,
                                       int nBayerPhase,
                                       HgppStreamContext hgppStreamCtx)

// 单通道 CFA → 三通道Planar RGB（双线性）
HgppStatus hgppiCFAToRGB_8u_C1P3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                       HGpp8u *pDst[3], int nDstStep,
                                       HgppiSize oSizeROI,
                                       int nBayerPhase,
                                       HgppStreamContext hgppStreamCtx)
```

**16 位无符号整数**

```c
HgppStatus hgppiCFAToRGB_16u_C1C3R_Ctx(const Hgpp16u *pSrc, int nSrcStep,
                                        Hgpp16u *pDst, int nDstStep,
                                        HgppiSize oSizeROI,
                                        int nBayerPhase,
                                        HgppStreamContext hgppStreamCtx)

HgppStatus hgppiCFAToRGB_16u_C1P3R_Ctx(const Hgpp16u *pSrc, int nSrcStep,
                                        Hgpp16u *pDst[3], int nDstStep,
                                        HgppiSize oSizeROI,
                                        int nBayerPhase,
                                        HgppStreamContext hgppStreamCtx)
```

### 6.9. Gamma 校正
#### 6.9.1. 功能介绍
Gamma 校正函数对图像进行伽马校正，调整图像的亮度响应曲线。 Gamma 校正是显示设备和图像编码中的标准操作。

**Gamma 基础知识：**

Gamma （γ）描述了输入信号与输出亮度之间的非线性关系：

$$
\text{输出} = \text{输入}^{\gamma}
$$

**常见 Gamma 值：**

| 标准 | Gamma 值 | 应用场景 |
|------|----------|----------|
| **sRGB** | ~2.2 | 计算机显示器、网络图像 |
| **BT.709** | 2.2 | HDTV |
| **BT.2020** | 2.2 | UHDTV |
| **DCI-P3** | 2.6 | 数字影院 |
| **Linear** | 1.0 | 线性光空间（渲染、合成） |

> **注意：**
> - Gamma < 1：提亮图像（压缩高光，扩展暗部）
> - Gamma > 1：压暗图像（扩展高光，压缩暗部）
> - sRGB 实际使用分段曲线：线性段（0-0.04045）+ 幂函数段（>0.04045）。

#### 6.9.2. sRGB 转换公式
**sRGB 编码（线性→sRGB）：**

$$
V_{sRGB} = \begin{cases}
12.92 \times V_{linear} & \text{if } V_{linear} \leq 0.0031308 \\
1.055 \times V_{linear}^{1/2.4} - 0.055 & \text{if } V_{linear} > 0.0031308
\end{cases}
$$

**sRGB 解码（sRGB→线性）：**

$$
V_{linear} = \begin{cases}
V_{sRGB} / 12.92 & \text{if } V_{sRGB} \leq 0.04045 \\
((V_{sRGB} + 0.055) / 1.055)^{2.4} & \text{if } V_{sRGB} > 0.04045
\end{cases}
$$

#### 6.9.3. 完整参数说明
##### 6.9.3.1. Gamma 校正通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | **源图像指针** - 单通道或多通道 |
| `nSrcStep` | int | [in] | **源图像行步幅**（字节） |
| `pDst` | 设备指针 | [out] | **目标图像指针** |
| `nDstStep` | int | [in] | **目标图像行步幅**（字节） |
| `oSizeROI` | HgppiSize | [in] | **感兴趣区域** - ROI 宽度和高度 |
| `nGamma` | float | [in] | **Gamma 值** - 通常 0.1-5.0 |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

**返回值：** `HgppStatus`

#### 6.9.4. 函数列表
##### 6.9.4.1. Gamma 校正
**8 位无符号整数**

```c
// 单通道 Gamma 校正
HgppStatus hgppiGamma_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                  HGpp8u *pDst, int nDstStep,
                                  HgppiSize oSizeROI,
                                  float nGamma,
                                  HgppStreamContext hgppStreamCtx)

// 三通道 Gamma 校正
HgppStatus hgppiGamma_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                  HGpp8u *pDst, int nDstStep,
                                  HgppiSize oSizeROI,
                                  float nGamma,
                                  HgppStreamContext hgppStreamCtx)

// 四通道 Gamma 校正（不影响 Alpha）
HgppStatus hgppiGamma_8u_AC4R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                   HGpp8u *pDst, int nDstStep,
                                   HgppiSize oSizeROI,
                                   float nGamma,
                                   HgppStreamContext hgppStreamCtx)
```

**16 位/32 位版本**

```c
HgppStatus hgppiGamma_16u_C1R_Ctx(...)
HgppStatus hgppiGamma_16u_C3R_Ctx(...)
HgppStatus hgppiGamma_32f_C1R_Ctx(...)
HgppStatus hgppiGamma_32f_C3R_Ctx(...)
```

### 6.10. LUT 操作
#### 6.10.1. 功能介绍
LUT （Look-Up Table，查找表）操作提供高效的颜色映射和转换。 HGPP 支持 5 种 LUT 相关操作。

**LUT 基础知识：**

LUT 是一个预计算的数组，将输入值直接映射到输出值，避免复杂的逐像素计算。

```text
8 位 LUT 示例（256 项）：
输入值：0   1   2   ...  127  128  ...  255
        ↓   ↓   ↓        ↓    ↓       ↓
输出值：LUT[0], LUT[1], LUT[2], ..., LUT[255]
```

#### 6.10.2. 5 种 LUT 操作
| 操作 | 说明 | 应用场景 |
|------|------|----------|
| **LUT** | 单通道查找表 | 颜色映射、对比度调整 |
| **LUT 三通道** | 三通道独立 LUT | RGB 分别调整 |
| **LUT 索引** | 使用索引 LUT | 调色板、伪彩色 |
| **LUT 插值** | 带插值的 LUT | 平滑渐变 |
| **LUT 批量** | 多图像批量 LUT | 批处理 |

#### 6.10.3. 完整参数说明
##### 6.10.3.1. LUT 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | **源图像指针** |
| `nSrcStep` | int | [in] | **源图像行步幅** |
| `pDst` | 设备指针 | [out] | **目标图像指针** |
| `nDstStep` | int | [in] | **目标图像行步幅** |
| `oSizeROI` | HgppiSize | [in] | **感兴趣区域** |
| `pLUT` | 设备指针 | [in] | **LUT 指针** - 设备内存中的查找表 |
| `nLUTSize` | int | [in] | **LUT 大小** - 通常 256 （8 位）或 65536 （16 位） |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

#### 6.10.4. 函数列表
##### 6.10.4.1. LUT （单通道）
```c
// 8 位单通道 LUT
HgppStatus hgppiLUT_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                HGpp8u *pDst, int nDstStep,
                                HgppiSize oSizeROI,
                                const HGpp8u *pLUT,
                                HgppStreamContext hgppStreamCtx)

// 16 位单通道 LUT
HgppStatus hgppiLUT_16u_C1R_Ctx(const Hgpp16u *pSrc, int nSrcStep,
                                 Hgpp16u *pDst, int nDstStep,
                                 HgppiSize oSizeROI,
                                 const Hgpp16u *pLUT,
                                 HgppStreamContext hgppStreamCtx)
```

##### 6.10.4.2. LUT 三通道（独立 LUT）
```c
// 8 位三通道，每通道独立 LUT
HgppStatus hgppiLUT_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                HGpp8u *pDst, int nDstStep,
                                HgppiSize oSizeROI,
                                const HGpp8u *pLUT[3],
                                HgppStreamContext hgppStreamCtx)

// 8 位三通道，共享 LUT
HgppStatus hgppiLUT_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                HGpp8u *pDst, int nDstStep,
                                HgppiSize oSizeROI,
                                const HGpp8u *pLUT,
                                HgppStreamContext hgppStreamCtx)
```

##### 6.10.4.3. LUT 索引（伪彩色）
```c
// 8 位索引 → 三通道 RGB（伪彩色）
HgppStatus hgppiLUTPalette_8u_C1C3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                         HGpp8u *pDst, int nDstStep,
                                         HgppiSize oSizeROI,
                                         const HGpp8u *pLUT,
                                         int nLUTSize,
                                         HgppStreamContext hgppStreamCtx)
```

##### 6.10.4.4. LUT 插值（平滑）
```c
// 32 位浮点 LUT 插值
HgppStatus hgppiLUTInterpolate_32f_C1R_Ctx(const Hgpp32f *pSrc, int nSrcStep,
                                            Hgpp32f *pDst, int nDstStep,
                                            HgppiSize oSizeROI,
                                            const Hgpp32f *pLUT,
                                            int nLUTSize,
                                            HgppStreamContext hgppStreamCtx)
```

##### 6.10.4.5. LUT 批量
```c
// 批量 LUT 处理多幅图像
HgppStatus hgppiLUTBatch_8u_C1R_Ctx(const HgppiImageDescriptor *pBatchList,
                                     int nBatchSize,
                                     const HGpp8u *pLUT,
                                     HgppStreamContext hgppStreamCtx)
```

> **提示：**
> ```c
> // 创建 8 位反色 LUT。
> HGpp8u pInvertLUT[256];
> for (int i = 0; i < 256; i++) {
> pInvertLUT[i] = 255 - i;
> }
> ```

### 6.11. Alpha 合成
#### 6.11.1. 功能介绍
Alpha 合成函数实现两个图像的混合，支持多种合成模式。 Alpha 通道表示像素的不透明度。

**Alpha 基础知识：**

- **Alpha = 0**：完全透明。
- **Alpha = 255 （8 位）**：完全不透明。
- **预乘 Alpha**：颜色值已乘以 Alpha （R×A, G×A, B×A）

#### 6.11.2. AlphaOp 合成模式详解
**HgppiAlphaOp 枚举定义了 14 种合成模式：**

| 模式 | 公式 | 说明 |
|------|------|------|
| `HGPP_OP_ALPHA_OVER` | `D = S + (1-αs)×D` | 标准 Over （源在上） |
| `HGPP_OP_ALPHA_IN` | `D = αd×S` | 源在目标内 |
| `HGPP_OP_ALPHA_OUT` | `D = (1-αd)×S` | 源在目标外 |
| `HGPP_OP_ALPHA_ATOP` | `D = αd×S + (1-αs)×D` | 源在目标上，但只显示目标区域 |
| `HGPP_OP_ALPHA_XOR` | `D = (1-αd)×S + (1-αs)×D` | 异或（只显示不重叠部分） |
| `HGPP_OP_ALPHA_PLUS` | `D = S + D` | 加法混合（可能过曝） |
| `HGPP_OP_ALPHA_OVER_PREMUL` | `D = S + (1-αs)×D` | Over （源已预乘） |
| `HGPP_OP_ALPHA_IN_PREMUL` | `D = αd×S` | In （源已预乘） |
| `HGPP_OP_ALPHA_OUT_PREMUL` | `D = (1-αd)×S` | Out （源已预乘） |
| `HGPP_OP_ALPHA_ATOP_PREMUL` | `D = αd×S + (1-αs)×D` | Atop （源已预乘） |
| `HGPP_OP_ALPHA_XOR_PREMUL` | `D = (1-αd)×S + (1-αs)×D` | Xor （源已预乘） |
| `HGPP_OP_ALPHA_PLUS_PREMUL` | `D = S + D` | Plus （源已预乘） |
| `HGPP_OP_ALPHA_PREMUL` | `D = α×S` | 预乘 Alpha |

**符号说明：**
- `S` = 源颜色值（可能已预乘）
- `D` = 目标颜色值（输出）
- `αs` = 源 Alpha （0-1 归一化）
- `αd` = 目标 Alpha

#### 6.11.3. 完整参数说明
##### 6.11.3.1. AlphaComp 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc1` | 设备指针 | [in] | **源图像 1 指针** - 四通道（带 Alpha） |
| `nSrc1Step` | int | [in] | **源图像 1 行步幅** |
| `nAlpha1` | HGpp8u | [in] | **源 1 全局 Alpha** - 0-255，与像素 Alpha 相乘 |
| `pSrc2` | 设备指针 | [in] | **源图像 2 指针** |
| `nSrc2Step` | int | [in] | **源图像 2 行步幅** |
| `nAlpha2` | HGpp8u | [in] | **源 2 全局 Alpha** |
| `pDst` | 设备指针 | [out] | **目标图像指针** |
| `nDstStep` | int | [in] | **目标图像行步幅** |
| `oSizeROI` | HgppiSize | [in] | **感兴趣区域** |
| `hgppAlphaOp` | HgppiAlphaOp | [in] | **Alpha 操作模式** - 见上方表格 |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

#### 6.11.4. 函数列表
##### 6.11.4.1. AlphaComp （带全局 Alpha）
**8 位无符号整数**

```c
// 四通道 Alpha 合成（带全局 Alpha）
HgppStatus hgppiAlphaComp_8u_AC4R_Ctx(const HGpp8u *pSrc1, int nSrc1Step, HGpp8u nAlpha1,
                                       const HGpp8u *pSrc2, int nSrc2Step, HGpp8u nAlpha2,
                                       HGpp8u *pDst, int nDstStep,
                                       HgppiSize oSizeROI,
                                       HgppiAlphaOp hgppAlphaOp,
                                       HgppStreamContext hgppStreamCtx)
```

##### 6.11.4.2. AlphaBlend （标准混合）
```c
// 四通道 Alpha 混合（使用像素 Alpha）
HgppStatus hgppiAlphaBlend_8u_AC4R_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                        const HGpp8u *pSrc2, int nSrc2Step,
                                        HGpp8u *pDst, int nDstStep,
                                        HgppiSize oSizeROI,
                                        HgppStreamContext hgppStreamCtx)
```

**16 位/32 位版本**

```c
HgppStatus hgppiAlphaComp_16u_AC4R_Ctx(...)
HgppStatus hgppiAlphaBlend_16u_AC4R_Ctx(...)
HgppStatus hgppiAlphaComp_32f_AC4R_Ctx(...)
HgppStatus hgppiAlphaBlend_32f_AC4R_Ctx(...)
```

> **提示：**
> ```c
> // 将 src1（前景）合成到 src2（背景）上。
> hgppiAlphaComp_8u_AC4R_Ctx(pSrc1, nSrc1Step, 255,  // 前景，完全不透明。
> pSrc2, nSrc2Step, 255,  // 背景。
> pDst, nDstStep,
> oSizeROI,
> HGPP_OP_ALPHA_OVER,
> hgppStreamCtx);
> ```

### 6.12. CompColorKey
#### 6.12.1. 功能介绍
CompColorKey （颜色键合成）函数基于颜色键值进行图像合成，常用于绿幕/蓝幕抠像。

**颜色键基础知识：**

颜色键合成通过指定一个"键颜色"（通常是绿色或蓝色），将接近该颜色的区域设为透明。

```text
颜色键合成流程：
1. 计算每个像素与键颜色的距离
2. 如果距离 < 阈值，设为透明
3. 否则，保留原像素或进行 Alpha 混合
```

#### 6.12.2. 完整参数说明
##### 6.12.2.1. CompColorKey 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | **源图像指针** - 三通道或四通道 |
| `nSrcStep` | int | [in] | **源图像行步幅** |
| `pDst` | 设备指针 | [out] | **目标图像指针** |
| `nDstStep` | int | [in] | **目标图像行步幅** |
| `oSizeROI` | HgppiSize | [in] | **感兴趣区域** |
| `nColorKey` | Hgpp32u | [in] | **颜色键值** - RGB 值（如 0x00FF00=绿色） |
| `nTolerance` | HGpp8u | [in] | **容差** - 0-255，决定颜色匹配范围 |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

#### 6.12.3. 函数列表
##### 6.12.3.1. CompColorKey
**8 位无符号整数**

```c
// 三通道颜色键合成
HgppStatus hgppiCompColorKey_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                         HGpp8u *pDst, int nDstStep,
                                         HgppiSize oSizeROI,
                                         Hgpp32u nColorKey,
                                         HGpp8u nTolerance,
                                         HgppStreamContext hgppStreamCtx)

// 四通道颜色键合成（输出带 Alpha）
HgppStatus hgppiCompColorKey_8u_C3AC4R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                            HGpp8u *pDst, int nDstStep,
                                            HgppiSize oSizeROI,
                                            Hgpp32u nColorKey,
                                            HGpp8u nTolerance,
                                            HgppStreamContext hgppStreamCtx)
```

> **提示：**
> ```c
> // 绿色键值（RGB = 0, 255, 0）
> Hgpp32u greenKey = 0x00FF00;
> HGpp8u tolerance = 50;  // 容差。
>
> hgppiCompColorKey_8u_C3AC4R_Ctx(pSrc, nSrcStep,
>                              pDst, nDstStep,
>                              oSizeROI,
>                              greenKey, tolerance,
>                              hgppStreamCtx);
> ```

### 6.13. JPEG 颜色转换
#### 6.13.1. 功能介绍
JPEG 标准专用的颜色转换函数，支持 CMYK 和 YCCK 颜色空间与 RGB/BGR 之间的转换。

**JPEG 颜色空间基础知识：**

| 颜色空间 | 说明 | 应用场景 |
|----------|------|----------|
| **RGB** | 红绿蓝 | 标准显示 |
| **CMYK** | 青品黄黑 | 印刷、 JPEG 扩展 |
| **YCCK** | YCbCr + K | JPEG 彩色印刷（YCbCr 带黑版） |

> **注意：**
> - JPEG 使用 Full Range YCbCr （0-255），不是 TV Range
> - CMYK/YCCK 转换通常用于印刷行业。
> - JPEG 标准使用 BT.601 系数进行 RGB↔YCbCr 转换。

#### 6.13.2. JPEG RGB↔YCbCr 转换公式
**RGB→YCbCr （JPEG）：**

$$
\begin{aligned}
Y &= 0.299 \times R + 0.587 \times G + 0.114 \times B \\
Cb &= -0.168736 \times R - 0.331264 \times G + 0.5 \times B + 128 \\
Cr &= 0.5 \times R - 0.418688 \times G - 0.081312 \times B + 128
\end{aligned}
$$

**YCbCr→RGB （JPEG）：**

$$
\begin{aligned}
R &= Y + 1.402 \times (Cr - 128) \\
G &= Y - 0.344136 \times (Cb - 128) - 0.714136 \times (Cr - 128) \\
B &= Y + 1.772 \times (Cb - 128)
\end{aligned}
$$

#### 6.13.3. CMYK↔RGB 转换公式
**CMYK→RGB：**

$$
\begin{aligned}
R &= 255 \times (1 - C) \times (1 - K) \\
G &= 255 \times (1 - M) \times (1 - K) \\
B &= 255 \times (1 - Y) \times (1 - K)
\end{aligned}
$$

**RGB→CMYK：**

$$
\begin{aligned}
K &= 1 - \max(R', G', B') \quad \text{其中 } R'=R/255, G'=G/255, B'=B/255 \\
C &= (1 - R' - K) / (1 - K) \\
M &= (1 - G' - K) / (1 - K) \\
Y &= (1 - B' - K) / (1 - K)
\end{aligned}
$$

#### 6.13.4. 完整参数说明
##### 6.13.4.1. JPEG 颜色转换通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | **源图像指针** - Planar 格式（CMYK/YCCK 为 4 通道） |
| `nSrcStep` | int | [in] | **源图像行步幅** |
| `pDst` | 设备指针 | [out] | **目标图像指针** - Packet 或 Planar RGB/BGR |
| `nDstStep` | int | [in] | **目标图像行步幅** |
| `oSizeROI` | HgppiSize | [in] | **感兴趣区域** |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

#### 6.13.5. 函数列表
##### 6.13.5.1. CMYK/YCCK → RGB
**8 位无符号整数**

```c
// CMYK/YCCK Planar → RGB Planar。
HgppStatus hgppiCMYKOrYCCKToRGB_JPEG_8u_P4P3R_Ctx(const HGpp8u *pSrc[4], int nSrcStep,
                                                   HGpp8u *pDst[3], int nDstStep,
                                                   HgppiSize oSizeROI,
                                                   HgppStreamContext hgppStreamCtx)

// CMYK/YCCK Planar → RGB Packet。
HgppStatus hgppiCMYKOrYCCKToRGB_JPEG_8u_P4C3R_Ctx(const HGpp8u *pSrc[4], int nSrcStep,
                                                   HGpp8u *pDst, int nDstStep,
                                                   HgppiSize oSizeROI,
                                                   HgppStreamContext hgppStreamCtx)

// CMYK/YCCK Planar → BGR Planar。
HgppStatus hgppiCMYKOrYCCKToBGR_JPEG_8u_P4P3R_Ctx(const HGpp8u *pSrc[4], int nSrcStep,
                                                   HGpp8u *pDst[3], int nDstStep,
                                                   HgppiSize oSizeROI,
                                                   HgppStreamContext hgppStreamCtx)

// CMYK/YCCK Planar → BGR Packet。
HgppStatus hgppiCMYKOrYCCKToBGR_JPEG_8u_P4C3R_Ctx(const HGpp8u *pSrc[4], int nSrcStep,
                                                   HGpp8u *pDst, int nDstStep,
                                                   HgppiSize oSizeROI,
                                                   HgppStreamContext hgppStreamCtx)
```

##### 6.13.5.2. RGB → CMYK/YCCK
```c
// RGB Packet → YCCK Planar。
HgppStatus hgppiRGBToYCCK_JPEG_8u_C3P4R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                             HGpp8u *pDst[4], int nDstStep,
                                             HgppiSize oSizeROI,
                                             HgppStreamContext hgppStreamCtx)

// RGB Planar → YCCK Planar。
HgppStatus hgppiRGBToYCCK_JPEG_8u_P3P4R_Ctx(const HGpp8u *const pSrc[3], int nSrcStep,
                                             HGpp8u *pDst[4], int nDstStep,
                                             HgppiSize oSizeROI,
                                             HgppStreamContext hgppStreamCtx)
```

> **提示：**
> - JPEG 解码时通常使用 `hgppiCMYKOrYCCKToRGB_JPEG_8u_P4C3R_Ctx`
> - JPEG 编码时通常使用 `hgppiRGBToYCCK_JPEG_8u_C3P4R_Ctx`
> - 确保输入输出步幅正确对齐（4 字节边界）。

### 6.14. 其他转换
#### 6.14.1. BGR 相关转换

> **提示：**
> BGR 只是 RGB 的通道顺序相反，常用于 OpenCV 和 Windows BMP 格式。

```c
// RGB ↔ BGR（三通道Packet，8 位）
HgppStatus hgppiRGBToBGR_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                     HGpp8u *pDst, int nDstStep,
                                     HgppiSize oSizeROI,
                                     HgppStreamContext hgppStreamCtx)

HgppStatus hgppiBGRToRGB_8u_C3R_Ctx(...)

// 16 位/32 位版本。
HgppStatus hgppiRGBToBGR_16u_C3R_Ctx(...)
HgppStatus hgppiRGBToBGR_32f_C3R_Ctx(...)

// BGR → YCbCr420。
HgppStatus hgppiBGRToYCbCr420_8u_C3P3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                            HGpp8u *pDst[3], int aDstStep[3],
                                            HgppiSize oSizeROI,
                                            HgppStreamContext hgppStreamCtx)

// BGR → HLS。
HgppStatus hgppiBGRToHLS_8u_C3P3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                       HGpp8u *pDst[3], int nDstStep,
                                       HgppiSize oSizeROI,
                                       HgppStreamContext hgppStreamCtx)

// BGR → Lab。
HgppStatus hgppiBGRToLab_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                     HGpp8u *pDst, int nDstStep,
                                     HgppiSize oSizeROI,
                                     HgppStreamContext hgppStreamCtx)
```

#### 6.14.2. YCbCr420/422 → BGR
```c
// YCbCr420 Planar → BGR Packet。
HgppStatus hgppiYCbCr420ToBGR_8u_P3C3R_Ctx(const HGpp8u *const pSrc[3], int aSrcStep[3],
                                            HGpp8u *pDst, int nDstStep,
                                            HgppiSize oSizeROI,
                                            HgppStreamContext hgppStreamCtx)

// YCbCr422 Packet → BGR Packet。
HgppStatus hgppiYCbCr422ToBGR_8u_C2C3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                            HGpp8u *pDst, int nDstStep,
                                            HgppiSize oSizeROI,
                                            HgppStreamContext hgppStreamCtx)
```

#### 6.14.3. HLSToRGB / HLSToBGR
```c
// HLS → RGB。
HgppStatus hgppiHLSToRGB_8u_P3C3R_Ctx(const HGpp8u *const pSrc[3], int nSrcStep,
                                       HGpp8u *pDst, int nDstStep,
                                       HgppiSize oSizeROI,
                                       HgppStreamContext hgppStreamCtx)

// HLS → BGR。
HgppStatus hgppiHLSToBGR_8u_P3C3R_Ctx(const HGpp8u *const pSrc[3], int nSrcStep,
                                       HGpp8u *pDst, int nDstStep,
                                       HgppiSize oSizeROI,
                                       HgppStreamContext hgppStreamCtx)
```

#### 6.14.4. ColorToGray （多数据类型）

> **提示：**
> 支持 8u/16u/16s/32f 和三通道/四通道配置。

```c
// 8 位版本。
HgppStatus hgppiColorToGray_8u_C3C1R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                          HGpp8u *pDst, int nDstStep,
                                          HgppiSize oSizeROI,
                                          HgppStreamContext hgppStreamCtx)

HgppStatus hgppiColorToGray_8u_C4C1R_Ctx(...)
HgppStatus hgppiColorToGray_8u_AC4C1R_Ctx(...)

// 16 位无符号版本。
HgppStatus hgppiColorToGray_16u_C3C1R_Ctx(...)
HgppStatus hgppiColorToGray_16u_C4C1R_Ctx(...)
HgppStatus hgppiColorToGray_16u_AC4C1R_Ctx(...)

// 16 位有符号版本。
HgppStatus hgppiColorToGray_16s_C3C1R_Ctx(...)
HgppStatus hgppiColorToGray_16s_C4C1R_Ctx(...)
HgppStatus hgppiColorToGray_16s_AC4C1R_Ctx(...)

// 32 位浮点版本。
HgppStatus hgppiColorToGray_32f_C3C1R_Ctx(...)
HgppStatus hgppiColorToGray_32f_C4C1R_Ctx(...)
HgppStatus hgppiColorToGray_32f_AC4C1R_Ctx(...)
```

#### 6.14.5. GammaFwd / GammaInv （正向/逆向 Gamma）

> **提示：**
> GammaFwd 用于编码（应用 Gamma）， GammaInv 用于解码（逆 Gamma）。

```c
// Gamma 正向（应用 Gamma）
HgppStatus hgppiGammaFwd_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                     HGpp8u *pDst, int nDstStep,
                                     HgppiSize oSizeROI,
                                     HgppStreamContext hgppStreamCtx)

HgppStatus hgppiGammaFwd_8u_AC4R_Ctx(...)

// Gamma 逆向（逆 Gamma）
HgppStatus hgppiGammaInv_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                     HGpp8u *pDst, int nDstStep,
                                     HgppiSize oSizeROI,
                                     HgppStreamContext hgppStreamCtx)

HgppStatus hgppiGammaInv_8u_AC4R_Ctx(...)

// 16 位/32 位版本。
HgppStatus hgppiGammaFwd_16u_C3R_Ctx(...)
HgppStatus hgppiGammaInv_16u_C3R_Ctx(...)
HgppStatus hgppiGammaFwd_32f_C3R_Ctx(...)
HgppStatus hgppiGammaInv_32f_C3R_Ctx(...)
```

#### 6.14.6. LUTPalette （伪彩色映射）

> **提示：**
> 将单通道索引图像转换为三通道伪彩色图像。

```c
// 8 位索引 → 三通道 RGB。
HgppStatus hgppiLUTPalette_8u_C1C3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                         HGpp8u *pDst, int nDstStep,
                                         HgppiSize oSizeROI,
                                         const HGpp8u *pLUT,
                                         HgppStreamContext hgppStreamCtx)

// 8 位索引 → 四通道 RGBA。
HgppStatus hgppiLUTPalette_8u_C1C4R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                         HGpp8u *pDst, int nDstStep,
                                         HgppiSize oSizeROI,
                                         const HGpp8u *pLUT,
                                         HgppStreamContext hgppStreamCtx)

// 16 位索引 → 三通道 RGB。
HgppStatus hgppiLUTPalette_16u_C1C3R_Ctx(const Hgpp16u *pSrc, int nSrcStep,
                                          Hgpp16u *pDst, int nDstStep,
                                          HgppiSize oSizeROI,
                                          const Hgpp16u *pLUT,
                                          HgppStreamContext hgppStreamCtx)
```

#### 6.14.7. YCrCb 相关转换

> **提示：**
> YCrCb 与 YCbCr 的区别在于 Cr/Cb 的顺序（Cr 在前， Cb 在后）。

```c
// YCrCb420 → RGB。
HgppStatus hgppiYCrCb420ToRGB_8u_P3R_Ctx(const HGpp8u *const pSrc[3], int aSrcStep[3],
                                          HGpp8u *pDst[3], int aDstStep[3],
                                          HgppiSize oSizeROI,
                                          HgppStreamContext hgppStreamCtx)

// YCrCb420 → BGR。
HgppStatus hgppiYCrCb420ToBGR_8u_P3C3R_Ctx(const HGpp8u *const pSrc[3], int aSrcStep[3],
                                            HGpp8u *pDst, int nDstStep,
                                            HgppiSize oSizeROI,
                                            HgppStreamContext hgppStreamCtx)

// RGB → YCrCb420。
HgppStatus hgppiRGBToYCrCb420_8u_C3P3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                            HGpp8u *pDst[3], int aDstStep[3],
                                            HgppiSize oSizeROI,
                                            HgppStreamContext hgppStreamCtx)
```

#### 6.14.8. CFAToRGBA （带 Alpha 的去马赛克）
```c
// CFA → RGBA（8 位）
HgppStatus hgppiCFAToRGBA_8u_C1AC4R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                         HGpp8u *pDst, int nDstStep,
                                         HgppiSize oSizeROI,
                                         int nBayerPhase,
                                         HgppStreamContext hgppStreamCtx)

// CFA → RGBA（16 位）
HgppStatus hgppiCFAToRGBA_16u_C1AC4R_Ctx(const Hgpp16u *pSrc, int nSrcStep,
                                          Hgpp16u *pDst, int nDstStep,
                                          HgppiSize oSizeROI,
                                          int nBayerPhase,
                                          HgppStreamContext hgppStreamCtx)
```

### 6.15. 错误码汇总
| 错误码 | 说明 | 适用章节 |
|--------|------|----------|
| `HGPP_NULL_POINTER_ERROR` | 空指针错误 - pSrc、 pDst 或关键参数指针为 NULL | 全部 |
| `HGPP_STEP_ERROR` | 步幅错误 - nSrcStep 或 nDstStep ≤ 0 | 全部 |
| `HGPP_SIZE_ERROR` | ROI 尺寸错误 - oSizeROI 宽度或高度 < 0 | 全部 |
| `HGPP_INTERPOLATION_ERROR` | 插值模式值非法 | 不适用（颜色转换不使用插值） |
| `HGPP_COEFFICIENT_ERROR` | 颜色扭曲系数值无效 | ColorTwist |
| `HGPP_ALPHA_OP_ERROR` | 不支持的 Alpha 操作 | Alpha 合成 |
| `HGPP_CHANNEL_ORDER_ERROR` | 通道顺序错误 | 颜色转换 |
| `HGPP_DATA_TYPE_ERROR` | 不支持的数据类型 | 全部 |

比赛关联：VLM 视觉侧预处理链（BGR→RGB 通道交换、RGB↔YUV/NV12 转换、归一化减均值除方差可用第 5 章 SubC/MulC、ColorTwist 一次完成矩阵化颜色校正）都能整体 offload 到 PPU，把 CPU 从逐帧预处理中解放出来。

## 7. 数据交换与初始化
> **库名称**: `hgppidei` 
> **功能**: 用于初始化、复制和转换图像数据的函数。
> **说明**: 同类函数没有全部列出，完整函数定义请参考头文件。

### 7.1. 像素设置
将 ROI 内所有像素设置为特定值。

#### 7.1.1. 通用参数
| 参数 | 类型 | 说明 | 注意事项 |
|------|------|------|----------|
| `nValue` | 对应数据类型 | 要设置的像素值（单通道） | - |
| `aValue[N]` | 对应数据类型数组 | 要设置的像素值数组（多通道） | 数组大小必须与通道数匹配 |
| `pDst` | 指针 | 目标图像指针 | 不能为空指针 |
| `nDstStep` | int | 目标图像行步幅（字节数） | 必须 ≥ ROI 宽度 × 像素字节数 |
| `oSizeROI` | HgppiSize | 感兴趣区域 (ROI) | 宽度和高度必须 > 0 |
| `hgppStreamCtx` | HgppStreamContext | 应用程序管理流上下文 | - |

#### 7.1.2. 函数列表
##### 7.1.2.1. 8 位有符号/无符号 (8s, 8u)
```c
HgppStatus hgppiSet_8s_C1R_Ctx(const Hgpp8s nValue, Hgpp8s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_8s_C2R_Ctx(const Hgpp8s aValue[2], Hgpp8s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_8s_C3R_Ctx(const Hgpp8s aValue[3], Hgpp8s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_8s_C4R_Ctx(const Hgpp8s aValue[4], Hgpp8s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_8s_AC4R_Ctx(const Hgpp8s aValue[3], Hgpp8s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

HgppStatus hgppiSet_8u_C1R_Ctx(const HGpp8u nValue, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_8u_C2R_Ctx(const HGpp8u aValue[2], HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_8u_C3R_Ctx(const HGpp8u aValue[3], HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_8u_C4R_Ctx(const HGpp8u aValue[4], HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_8u_AC4R_Ctx(const HGpp8u aValue[3], HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
```

##### 7.1.2.2. 16 位有符号/无符号/复数 (16s, 16u, 16sc)
```c
HgppStatus hgppiSet_16s_C1R_Ctx(const Hgpp16s nValue, Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_16s_C2R_Ctx(const Hgpp16s aValue[2], Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_16s_C3R_Ctx(const Hgpp16s aValue[3], Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_16s_C4R_Ctx(const Hgpp16s aValue[4], Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_16s_AC4R_Ctx(const Hgpp16s aValue[3], Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

HgppStatus hgppiSet_16u_C1R_Ctx(const Hgpp16u nValue, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_16u_C2R_Ctx(const Hgpp16u aValue[2], Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_16u_C3R_Ctx(const Hgpp16u aValue[3], Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_16u_C4R_Ctx(const Hgpp16u aValue[4], Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_16u_AC4R_Ctx(const Hgpp16u aValue[3], Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

HgppStatus hgppiSet_16sc_C1R_Ctx(const Hgpp16sc oValue, Hgpp16sc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_16sc_C2R_Ctx(const Hgpp16sc aValue[2], Hgpp16sc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_16sc_C3R_Ctx(const Hgpp16sc aValue[3], Hgpp16sc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_16sc_C4R_Ctx(const Hgpp16sc aValue[4], Hgpp16sc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_16sc_AC4R_Ctx(const Hgpp16sc aValue[3], Hgpp16sc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
```

##### 7.1.2.3. 32 位有符号/无符号/复数 (32s, 32u, 32sc)
```c
HgppStatus hgppiSet_32s_C1R_Ctx(const Hgpp32s nValue, Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32s_C2R_Ctx(const Hgpp32s aValue[2], Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32s_C3R_Ctx(const Hgpp32s aValue[3], Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32s_C4R_Ctx(const Hgpp32s aValue[4], Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32s_AC4R_Ctx(const Hgpp32s aValue[3], Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

HgppStatus hgppiSet_32u_C1R_Ctx(const Hgpp32u nValue, Hgpp32u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32u_C2R_Ctx(const Hgpp32u aValue[2], Hgpp32u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32u_C3R_Ctx(const Hgpp32u aValue[3], Hgpp32u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32u_C4R_Ctx(const Hgpp32u aValue[4], Hgpp32u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32u_AC4R_Ctx(const Hgpp32u aValue[3], Hgpp32u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

HgppStatus hgppiSet_32sc_C1R_Ctx(const Hgpp32sc oValue, Hgpp32sc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32sc_C2R_Ctx(const Hgpp32sc aValue[2], Hgpp32sc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32sc_C3R_Ctx(const Hgpp32sc aValue[3], Hgpp32sc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32sc_C4R_Ctx(const Hgpp32sc aValue[4], Hgpp32sc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32sc_AC4R_Ctx(const Hgpp32sc aValue[3], Hgpp32sc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
```

##### 7.1.2.4. 16 位/32 位浮点 (16f, 32f, 32fc)
```c
// 16f: nValue 是 32 位浮点数，会被转换为 16 位。
// 注意：16f 类型的指针和步幅最好至少 16 字节对齐。
HgppStatus hgppiSet_16f_C1R_Ctx(const Hgpp32f nValue, Hgpp16f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_16f_C2R_Ctx(const Hgpp32f aValues[2], Hgpp16f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_16f_C3R_Ctx(const Hgpp32f aValues[3], Hgpp16f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_16f_C4R_Ctx(const Hgpp32f aValues[4], Hgpp16f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

HgppStatus hgppiSet_32f_C1R_Ctx(const Hgpp32f nValue, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32f_C2R_Ctx(const Hgpp32f aValue[2], Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32f_C3R_Ctx(const Hgpp32f aValue[3], Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32f_C4R_Ctx(const Hgpp32f aValue[4], Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32f_AC4R_Ctx(const Hgpp32f aValue[3], Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

HgppStatus hgppiSet_32fc_C1R_Ctx(const Hgpp32fc oValue, Hgpp32fc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32fc_C2R_Ctx(const Hgpp32fc aValue[2], Hgpp32fc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32fc_C3R_Ctx(const Hgpp32fc aValue[3], Hgpp32fc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32fc_C4R_Ctx(const Hgpp32fc aValue[4], Hgpp32fc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32fc_AC4R_Ctx(const Hgpp32fc aValue[3], Hgpp32fc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
```

**命名规则**: `_C1R/C2R/C3R/C4R` = 通道数，`_AC4R` = 4 通道忽略 Alpha，`_Ctx` = 需要流上下文

### 7.2. 掩码设置
掩码控制 ROI 内哪些像素被设置（掩码值≠0 时设置，=0 时不修改）。

#### 7.2.1. 通用参数
| 参数 | 类型 | 说明 | 注意事项 |
|------|------|------|----------|
| `nValue` | 对应数据类型 | 要设置的像素值（单通道） | - |
| `aValue` | 对应数据类型数组 | 要设置的像素值（多通道） | 数组大小必须与通道数匹配 |
| `pDst` | 指针 | 目标图像指针 | 不能为空指针 |
| `nDstStep` | int | 目标图像行步幅 | 必须 ≥ ROI 宽度 × 像素字节数 |
| `oSizeROI` | HgppiSize | 感兴趣区域 (ROI) | 宽度和高度必须 > 0 |
| `pMask` | const HGpp8u* | 掩码图像指针 | 8 位单通道图像 |
| `nMaskStep` | int | 掩码图像行步幅 | 必须 ≥ ROI 宽度 |
| `hgppStreamCtx` | HgppStreamContext | 应用程序管理流上下文 | - |

#### 7.2.2. 函数列表
##### 7.2.2.1. 8 位无符号 (8u)
```c
HgppStatus hgppiSet_8u_C1MR_Ctx(HGpp8u nValue, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_8u_C3MR_Ctx(const HGpp8u aValue[3], HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_8u_C4MR_Ctx(const HGpp8u aValue[4], HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_8u_AC4MR_Ctx(const HGpp8u aValue[3], HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
```

##### 7.2.2.2. 16 位无符号/有符号 (16u, 16s)
```c
HgppStatus hgppiSet_16u_C1MR_Ctx(Hgpp16u nValue, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_16u_C3MR_Ctx(const Hgpp16u aValue[3], Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_16u_C4MR_Ctx(const Hgpp16u aValue[4], Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_16u_AC4MR_Ctx(const Hgpp16u aValue[3], Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)

HgppStatus hgppiSet_16s_C1MR_Ctx(Hgpp16s nValue, Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_16s_C3MR_Ctx(const Hgpp16s aValue[3], Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_16s_C4MR_Ctx(const Hgpp16s aValue[4], Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_16s_AC4MR_Ctx(const Hgpp16s aValue[3], Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
```

##### 7.2.2.3. 32 位有符号/浮点 (32s, 32f)
```c
HgppStatus hgppiSet_32s_C1MR_Ctx(Hgpp32s nValue, Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32s_C3MR_Ctx(const Hgpp32s aValue[3], Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32s_C4MR_Ctx(const Hgpp32s aValue[4], Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32s_AC4MR_Ctx(const Hgpp32s aValue[3], Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)

HgppStatus hgppiSet_32f_C1MR_Ctx(Hgpp32f nValue, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32f_C3MR_Ctx(const Hgpp32f aValue[3], Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32f_C4MR_Ctx(const Hgpp32f aValue[4], Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32f_AC4MR_Ctx(const Hgpp32f aValue[3], Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
```

**未列出的函数**: 
- 完整函数列表请参考头文件 `hgppidei.h`。

### 7.3. 通道设置
设置多通道图像中的单个颜色通道。

#### 7.3.1. 通用参数
| 参数 | 类型 | 说明 | 注意事项 |
|------|------|------|----------|
| `nValue` | 对应数据类型 | 要设置的像素值 | - |
| `pDst` | 指针 | 选择通道目标图像指针 | 指针应指向要设置的通道 |
| `nDstStep` | int | 目标图像行步幅 | - |
| `oSizeROI` | HgppiSize | 感兴趣区域 (ROI) | - |
| `hgppStreamCtx` | HgppStreamContext | 应用程序管理流上下文 | - |

#### 7.3.2. 函数列表
```c
// 8 位无符号。
HgppStatus hgppiSet_8u_C3CR_Ctx(HGpp8u nValue, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_8u_C4CR_Ctx(HGpp8u nValue, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

// 16 位无符号/有符号。
HgppStatus hgppiSet_16u_C3CR_Ctx(Hgpp16u nValue, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_16u_C4CR_Ctx(Hgpp16u nValue, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_16s_C3CR_Ctx(Hgpp16s nValue, Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_16s_C4CR_Ctx(Hgpp16s nValue, Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

// 32 位有符号/浮点。
HgppStatus hgppiSet_32s_C3CR_Ctx(Hgpp32s nValue, Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32s_C4CR_Ctx(Hgpp32s nValue, Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32f_C3CR_Ctx(Hgpp32f nValue, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSet_32f_C4CR_Ctx(Hgpp32f nValue, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
```

**未列出的函数**: 
- 完整函数列表请参考头文件 `hgppidei.h`。

### 7.4. 图像拷贝
将源图像像素复制到目标图像。

#### 7.4.1. 通用参数
| 参数 | 类型 | 说明 | 注意事项 |
|------|------|------|----------|
| `pSrc` | const 指针 | 源图像指针 | 不能为空指针 |
| `nSrcStep` | int | 源图像行步幅 | 必须 ≥ ROI 宽度 × 像素字节数 |
| `pDst` | 指针 | 目标图像指针 | 不能为空指针 |
| `nDstStep` | int | 目标图像行步幅 | 必须 ≥ ROI 宽度 × 像素字节数 |
| `oSizeROI` | HgppiSize | 感兴趣区域 (ROI) | 宽度和高度必须 > 0 |
| `hgppStreamCtx` | HgppStreamContext | 应用程序管理流上下文 | - |

#### 7.4.2. 函数列表
##### 7.4.2.1. 8 位有符号/无符号 (8s, 8u)
```c
HgppStatus hgppiCopy_8s_C1R_Ctx(const Hgpp8s *pSrc, int nSrcStep, Hgpp8s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_8s_C2R_Ctx(const Hgpp8s *pSrc, int nSrcStep, Hgpp8s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_8s_C3R_Ctx(const Hgpp8s *pSrc, int nSrcStep, Hgpp8s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_8s_C4R_Ctx(const Hgpp8s *pSrc, int nSrcStep, Hgpp8s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_8s_AC4R_Ctx(const Hgpp8s *pSrc, int nSrcStep, Hgpp8s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

HgppStatus hgppiCopy_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_8u_C4R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_8u_AC4R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
```

##### 7.4.2.2. 16 位有符号/无符号/复数 (16s, 16u, 16sc)
```c
HgppStatus hgppiCopy_16s_C1R_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16s_C3R_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16s_C4R_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16s_AC4R_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

HgppStatus hgppiCopy_16u_C1R_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16u_C3R_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16u_C4R_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16u_AC4R_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

HgppStatus hgppiCopy_16sc_C1R_Ctx(const Hgpp16sc *pSrc, int nSrcStep, Hgpp16sc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16sc_C2R_Ctx(const Hgpp16sc *pSrc, int nSrcStep, Hgpp16sc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16sc_C3R_Ctx(const Hgpp16sc *pSrc, int nSrcStep, Hgpp16sc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16sc_C4R_Ctx(const Hgpp16sc *pSrc, int nSrcStep, Hgpp16sc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16sc_AC4R_Ctx(const Hgpp16sc *pSrc, int nSrcStep, Hgpp16sc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
```

##### 7.4.2.3. 32 位有符号/复数 (32s, 32sc)
```c
HgppStatus hgppiCopy_32s_C1R_Ctx(const Hgpp32s *pSrc, int nSrcStep, Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32s_C3R_Ctx(const Hgpp32s *pSrc, int nSrcStep, Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32s_C4R_Ctx(const Hgpp32s *pSrc, int nSrcStep, Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32s_AC4R_Ctx(const Hgpp32s *pSrc, int nSrcStep, Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

HgppStatus hgppiCopy_32sc_C1R_Ctx(const Hgpp32sc *pSrc, int nSrcStep, Hgpp32sc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32sc_C2R_Ctx(const Hgpp32sc *pSrc, int nSrcStep, Hgpp32sc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32sc_C3R_Ctx(const Hgpp32sc *pSrc, int nSrcStep, Hgpp32sc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32sc_C4R_Ctx(const Hgpp32sc *pSrc, int nSrcStep, Hgpp32sc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32sc_AC4R_Ctx(const Hgpp32sc *pSrc, int nSrcStep, Hgpp32sc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
```

##### 7.4.2.4. 16 位/32 位浮点 (16f, 32f, 32fc)
```c
HgppStatus hgppiCopy_16f_C1R_Ctx(const Hgpp16f *pSrc, int nSrcStep, Hgpp16f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16f_C3R_Ctx(const Hgpp16f *pSrc, int nSrcStep, Hgpp16f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16f_C4R_Ctx(const Hgpp16f *pSrc, int nSrcStep, Hgpp16f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

HgppStatus hgppiCopy_32f_C1R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32f_C3R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32f_C4R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32f_AC4R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

HgppStatus hgppiCopy_32fc_C1R_Ctx(const Hgpp32fc *pSrc, int nSrcStep, Hgpp32fc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32fc_C2R_Ctx(const Hgpp32fc *pSrc, int nSrcStep, Hgpp32fc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32fc_C3R_Ctx(const Hgpp32fc *pSrc, int nSrcStep, Hgpp32fc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32fc_C4R_Ctx(const Hgpp32fc *pSrc, int nSrcStep, Hgpp32fc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32fc_AC4R_Ctx(const Hgpp32fc *pSrc, int nSrcStep, Hgpp32fc *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
```

**未列出的函数**: 
- 32u (32 位无符号整数) 复制函数未列出，请参考头文件 `hgppidei.h`。

### 7.5. 掩码拷贝
使用掩码控制哪些像素被复制（掩码值≠0 时复制，=0 时不修改）。

#### 7.5.1. 通用参数
| 参数 | 类型 | 说明 | 注意事项 |
|------|------|------|----------|
| `pSrc` | const 指针 | 源图像指针 | - |
| `nSrcStep` | int | 源图像行步幅 | - |
| `pDst` | 指针 | 目标图像指针 | - |
| `nDstStep` | int | 目标图像行步幅 | - |
| `pMask` | const HGpp8u* | 掩码图像指针 | 8 位单通道图像 |
| `nMaskStep` | int | 掩码图像行步幅 | 必须 ≥ ROI 宽度 |
| `oSizeROI` | HgppiSize | 感兴趣区域 (ROI) | - |
| `hgppStreamCtx` | HgppStreamContext | 应用程序管理流上下文 | - |

#### 7.5.2. 函数列表
##### 7.5.2.1. 8 位无符号 (8u)
```c
HgppStatus hgppiCopy_8u_C1MR_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_8u_C3MR_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_8u_C4MR_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_8u_AC4MR_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
```

##### 7.5.2.2. 16 位无符号/有符号 (16u, 16s)
```c
HgppStatus hgppiCopy_16u_C1MR_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16u_C3MR_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16u_C4MR_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16u_AC4MR_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)

HgppStatus hgppiCopy_16s_C1MR_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16s_C3MR_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16s_C4MR_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16s_AC4MR_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
```

##### 7.5.2.3. 32 位有符号/浮点 (32s, 32f)
```c
HgppStatus hgppiCopy_32s_C1MR_Ctx(const Hgpp32s *pSrc, int nSrcStep, Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32s_C3MR_Ctx(const Hgpp32s *pSrc, int nSrcStep, Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32s_C4MR_Ctx(const Hgpp32s *pSrc, int nSrcStep, Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32s_AC4MR_Ctx(const Hgpp32s *pSrc, int nSrcStep, Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)

HgppStatus hgppiCopy_32f_C1MR_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32f_C3MR_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32f_C4MR_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32f_AC4MR_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, const HGpp8u *pMask, int nMaskStep, HgppStreamContext hgppStreamCtx)
```

**未列出的函数**: 
- 完整函数列表请参考头文件 `hgppidei.h`。

### 7.6. 通道拷贝
复制多通道图像中的单个颜色通道。

#### 7.6.1. 通用参数
| 参数 | 类型 | 说明 | 注意事项 |
|------|------|------|----------|
| `pSrc` | const 指针 | 选择通道源图像指针 | 指针应指向要复制的通道 |
| `nSrcStep` | int | 源图像行步幅 | - |
| `pDst` | 指针 | 选择通道目标图像指针 | 指针应指向要粘贴的通道 |
| `nDstStep` | int | 目标图像行步幅 | - |
| `oSizeROI` | HgppiSize | 感兴趣区域 (ROI) | - |
| `hgppStreamCtx` | HgppStreamContext | 应用程序管理流上下文 | - |

#### 7.6.2. 函数列表
```c
// 8 位无符号。
HgppStatus hgppiCopy_8u_C3CR_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_8u_C4CR_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

// 16 位无符号/有符号。
HgppStatus hgppiCopy_16u_C3CR_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16u_C4CR_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16s_C3CR_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16s_C4CR_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

// 32 位有符号/浮点。
HgppStatus hgppiCopy_32s_C3CR_Ctx(const Hgpp32s *pSrc, int nSrcStep, Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32s_C4CR_Ctx(const Hgpp32s *pSrc, int nSrcStep, Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32f_C3CR_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32f_C4CR_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
```

**未列出的函数**: 
- 完整函数列表请参考头文件 `hgppidei.h`。

### 7.7. 提取通道
从多通道图像提取单个颜色通道到单通道图像。

#### 7.7.1. 通用参数
| 参数 | 类型 | 说明 | 注意事项 |
|------|------|------|----------|
| `pSrc` | const 指针 | 选择通道源图像指针 | - |
| `nSrcStep` | int | 源图像行步幅 | - |
| `pDst` | 指针 | 目标图像指针（单通道） | - |
| `nDstStep` | int | 目标图像行步幅 | - |
| `oSizeROI` | HgppiSize | 感兴趣区域 (ROI) | - |
| `hgppStreamCtx` | HgppStreamContext | 应用程序管理流上下文 | - |

#### 7.7.2. 函数列表
```c
// 8 位无符号。
HgppStatus hgppiCopy_8u_C3C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_8u_C4C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

// 16 位无符号/有符号。
HgppStatus hgppiCopy_16u_C3C1R_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16u_C4C1R_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16s_C3C1R_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16s_C4C1R_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

// 32 位有符号。
HgppStatus hgppiCopy_32s_C3C1R_Ctx(const Hgpp32s *pSrc, int nSrcStep, Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32s_C4C1R_Ctx(const Hgpp32s *pSrc, int nSrcStep, Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

// 32 位浮点（包含 C2 变体）
HgppStatus hgppiCopy_32f_C2C1R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32f_C3C1R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32f_C4C1R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
```

**未列出的函数**: 
- 完整函数列表请参考头文件 `hgppidei.h`。

### 7.8. 插入通道
将单通道图像复制到多通道图像中的一个颜色通道。

#### 7.8.1. 通用参数
| 参数 | 类型 | 说明 | 注意事项 |
|------|------|------|----------|
| `pSrc` | const 指针 | 源图像指针（单通道） | - |
| `nSrcStep` | int | 源图像行步幅 | - |
| `pDst` | 指针 | 选择通道目标图像指针 | - |
| `nDstStep` | int | 目标图像行步幅 | - |
| `oSizeROI` | HgppiSize | 感兴趣区域 (ROI) | - |
| `hgppStreamCtx` | HgppStreamContext | 应用程序管理流上下文 | - |

#### 7.8.2. 函数列表
```c
// 8 位无符号。
HgppStatus hgppiCopy_8u_C1C3R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_8u_C1C4R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

// 16 位无符号/有符号。
HgppStatus hgppiCopy_16u_C1C3R_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16u_C1C4R_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16s_C1C3R_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16s_C1C4R_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

// 32 位有符号。
HgppStatus hgppiCopy_32s_C1C3R_Ctx(const Hgpp32s *pSrc, int nSrcStep, Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32s_C1C4R_Ctx(const Hgpp32s *pSrc, int nSrcStep, Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

// 32 位浮点（包含 C2 变体）
HgppStatus hgppiCopy_32f_C1C2R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32f_C1C3R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32f_C1C4R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
```

**未列出的函数**: 
- 完整函数列表请参考头文件 `hgppidei.h`。

### 7.9. Packet 到 Planar
将 Packet 格式的多通道图像拆分为多个单通道 Planar 图像。

#### 7.9.1. 通用参数
| 参数 | 类型 | 说明 | 注意事项 |
|------|------|------|----------|
| `pSrc` | const 指针 | 源图像指针（Packet 格式） | - |
| `nSrcStep` | int | 源图像行步幅 | - |
| `aDst` | 指针数组 | 目标图像指针数组 | 数组大小必须与通道数匹配 |
| `nDstStep` | int | 目标图像行步幅 | 所有平面使用相同步幅 |
| `oSizeROI` | HgppiSize | 感兴趣区域 (ROI) | - |
| `hgppStreamCtx` | HgppStreamContext | 应用程序管理流上下文 | - |

#### 7.9.2. 函数列表
```c
// 8 位无符号。
HgppStatus hgppiCopy_8u_C3P3R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *const aDst[3], int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_8u_C4P4R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *const aDst[4], int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

// 16 位无符号/有符号。
HgppStatus hgppiCopy_16u_C3P3R_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *const aDst[3], int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16u_C4P4R_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *const aDst[4], int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16s_C3P3R_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *const aDst[3], int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16s_C4P4R_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *const aDst[4], int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

// 32 位有符号/浮点。
HgppStatus hgppiCopy_32s_C3P3R_Ctx(const Hgpp32s *pSrc, int nSrcStep, Hgpp32s *const aDst[3], int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32s_C4P4R_Ctx(const Hgpp32s *pSrc, int nSrcStep, Hgpp32s *const aDst[4], int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32f_C3P3R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *const aDst[3], int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32f_C4P4R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *const aDst[4], int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
```

**未列出的函数**: 
- 完整函数列表请参考头文件 `hgppidei.h`。

### 7.10. Planar 到 Packet
将多个单通道合并为 Packet 格式的多通道图像。

#### 7.10.1. 通用参数
| 参数 | 类型 | 说明 | 注意事项 |
|------|------|------|----------|
| `aSrc` | const 指针数组 | 源图像指针数组 | 数组大小必须与通道数匹配 |
| `nSrcStep` | int | 源图像行步幅 | 所有平面使用相同步幅 |
| `pDst` | 指针 | 目标图像指针（Packet 格式） | - |
| `nDstStep` | int | 目标图像行步幅 | - |
| `oSizeROI` | HgppiSize | 感兴趣区域 (ROI) | - |
| `hgppStreamCtx` | HgppStreamContext | 应用程序管理流上下文 | - |

#### 7.10.2. 函数列表
```c
// 8 位无符号。
HgppStatus hgppiCopy_8u_P3C3R_Ctx(const HGpp8u *const aSrc[3], int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_8u_P4C4R_Ctx(const HGpp8u *const aSrc[4], int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

// 16 位无符号/有符号。
HgppStatus hgppiCopy_16u_P3C3R_Ctx(const Hgpp16u *const aSrc[3], int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16u_P4C4R_Ctx(const Hgpp16u *const aSrc[4], int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16s_P3C3R_Ctx(const Hgpp16s *const aSrc[3], int nSrcStep, Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_16s_P4C4R_Ctx(const Hgpp16s *const aSrc[4], int nSrcStep, Hgpp16s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

// 32 位有符号/浮点。
HgppStatus hgppiCopy_32s_P3C3R_Ctx(const Hgpp32s *const aSrc[3], int nSrcStep, Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32s_P4C4R_Ctx(const Hgpp32s *const aSrc[4], int nSrcStep, Hgpp32s *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32f_P3C3R_Ctx(const Hgpp32f *const aSrc[3], int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopy_32f_P4C4R_Ctx(const Hgpp32f *const aSrc[4], int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
```

**未列出的函数**: 
- 完整函数列表请参考头文件 `hgppidei.h`。

### 7.11. 常量边界
复制图像并使用用户指定的常量颜色填充边界。

#### 7.11.1. 边界计算
```text
nBottomBorderHeight = oDstSizeROI.height - nTopBorderHeight - oSrcSizeROI.height
nRightBorderWidth = oDstSizeROI.width - nLeftBorderWidth - oSrcSizeROI.width
```

#### 7.11.2. 通用参数
| 参数 | 类型 | 说明 | 注意事项 |
|------|------|------|----------|
| `pSrc` | const 指针 | 源图像指针 | - |
| `nSrcStep` | int | 源图像行步幅 | - |
| `oSrcSizeROI` | HgppiSize | 源 ROI 尺寸 | 源图像中要复制的区域 |
| `pDst` | 指针 | 目标图像指针 | - |
| `nDstStep` | int | 目标图像行步幅 | - |
| `oDstSizeROI` | HgppiSize | 目标 ROI 尺寸 | 包含源图像区域 + 边界 |
| `nTopBorderHeight` | int | 上边界高度（像素） | 必须 ≥ 0 |
| `nLeftBorderWidth` | int | 左边界宽度（像素） | 必须 ≥ 0 |
| `nValue` | 对应数据类型 | 边界像素值（单通道） | - |
| `aValue` | 对应数据类型数组 | 边界像素值数组（多通道） | RGBA 值 |
| `hgppStreamCtx` | HgppStreamContext | 应用程序管理流上下文 | - |

#### 7.11.3. 函数列表
##### 7.11.3.1. 8 位无符号 (8u)
```c
HgppStatus hgppiCopyConstBorder_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, HgppiSize oSrcSizeROI, HGpp8u *pDst, int nDstStep, HgppiSize oDstSizeROI, int nTopBorderHeight, int nLeftBorderWidth, HGpp8u nValue, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopyConstBorder_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep, HgppiSize oSrcSizeROI, HGpp8u *pDst, int nDstStep, HgppiSize oDstSizeROI, int nTopBorderHeight, int nLeftBorderWidth, const HGpp8u aValue[3], HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopyConstBorder_8u_C4R_Ctx(const HGpp8u *pSrc, int nSrcStep, HgppiSize oSrcSizeROI, HGpp8u *pDst, int nDstStep, HgppiSize oDstSizeROI, int nTopBorderHeight, int nLeftBorderWidth, const HGpp8u aValue[4], HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopyConstBorder_8u_AC4R_Ctx(const HGpp8u *pSrc, int nSrcStep, HgppiSize oSrcSizeROI, HGpp8u *pDst, int nDstStep, HgppiSize oDstSizeROI, int nTopBorderHeight, int nLeftBorderWidth, const HGpp8u aValue[3], HgppStreamContext hgppStreamCtx)
```

##### 7.11.3.2. 16 位/32 位 (16u, 16s, 32s, 32f)
```c
// 16u, 16s, 32s, 32f 类似，提供 C1R, C3R, C4R, AC4R 变体。
HgppStatus hgppiCopyConstBorder_16u_C1R_Ctx(const Hgpp16u *pSrc, int nSrcStep, HgppiSize oSrcSizeROI, Hgpp16u *pDst, int nDstStep, HgppiSize oDstSizeROI, int nTopBorderHeight, int nLeftBorderWidth, Hgpp16u nValue, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopyConstBorder_16u_C3R_Ctx(const Hgpp16u *pSrc, int nSrcStep, HgppiSize oSrcSizeROI, Hgpp16u *pDst, int nDstStep, HgppiSize oDstSizeROI, int nTopBorderHeight, int nLeftBorderWidth, const Hgpp16u aValue[3], HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopyConstBorder_16u_C4R_Ctx(const Hgpp16u *pSrc, int nSrcStep, HgppiSize oSrcSizeROI, Hgpp16u *pDst, int nDstStep, HgppiSize oDstSizeROI, int nTopBorderHeight, int nLeftBorderWidth, const Hgpp16u aValue[4], HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopyConstBorder_16u_AC4R_Ctx(const Hgpp16u *pSrc, int nSrcStep, HgppiSize oSrcSizeROI, Hgpp16u *pDst, int nDstStep, HgppiSize oDstSizeROI, int nTopBorderHeight, int nLeftBorderWidth, const Hgpp16u aValue[3], HgppStreamContext hgppStreamCtx)

// 16s, 32s, 32f 类似...
```

**未列出的函数**: 
- 完整函数列表请参考头文件 `hgppidei.h`。

### 7.12. 复制边界
复制图像并使用最近源图像像素颜色复制填充边界。

#### 7.12.1. 通用参数
| 参数 | 类型 | 说明 | 注意事项 |
|------|------|------|----------|
| `pSrc` | const 指针 | 源图像指针 | - |
| `nSrcStep` | int | 源图像行步幅 | - |
| `oSrcSizeROI` | HgppiSize | 源 ROI 尺寸 | - |
| `pDst` | 指针 | 目标图像指针 | - |
| `nDstStep` | int | 目标图像行步幅 | - |
| `oDstSizeROI` | HgppiSize | 目标 ROI 尺寸 | - |
| `nTopBorderHeight` | int | 上边界高度（像素） | - |
| `nLeftBorderWidth` | int | 左边界宽度（像素） | - |
| `hgppStreamCtx` | HgppStreamContext | 应用程序管理流上下文 | - |

#### 7.12.2. 函数列表
##### 7.12.2.1. 8 位无符号 (8u)
```c
HgppStatus hgppiCopyReplicateBorder_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, HgppiSize oSrcSizeROI, HGpp8u *pDst, int nDstStep, HgppiSize oDstSizeROI, int nTopBorderHeight, int nLeftBorderWidth, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopyReplicateBorder_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep, HgppiSize oSrcSizeROI, HGpp8u *pDst, int nDstStep, HgppiSize oDstSizeROI, int nTopBorderHeight, int nLeftBorderWidth, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopyReplicateBorder_8u_C4R_Ctx(const HGpp8u *pSrc, int nSrcStep, HgppiSize oSrcSizeROI, HGpp8u *pDst, int nDstStep, HgppiSize oDstSizeROI, int nTopBorderHeight, int nLeftBorderWidth, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopyReplicateBorder_8u_AC4R_Ctx(const HGpp8u *pSrc, int nSrcStep, HgppiSize oSrcSizeROI, HGpp8u *pDst, int nDstStep, HgppiSize oDstSizeROI, int nTopBorderHeight, int nLeftBorderWidth, HgppStreamContext hgppStreamCtx)
```

##### 7.12.2.2. 16 位/32 位 (16u, 16s, 32s, 32f)
```c
// 16u, 16s, 32s, 32f 类似，提供 C1R, C3R, C4R, AC4R 变体。
HgppStatus hgppiCopyReplicateBorder_16u_C1R_Ctx(const Hgpp16u *pSrc, int nSrcStep, HgppiSize oSrcSizeROI, Hgpp16u *pDst, int nDstStep, HgppiSize oDstSizeROI, int nTopBorderHeight, int nLeftBorderWidth, HgppStreamContext hgppStreamCtx)
// ... 其他变体类似。
```

**未列出的函数**: 
- 完整函数列表请参考头文件 `hgppidei.h`。

### 7.13. 包裹边界
复制图像并使用包裹复制的源图像像素颜色填充边界（周期性重复）。

#### 7.13.1. 通用参数
| 参数 | 类型 | 说明 | 注意事项 |
|------|------|------|----------|
| `pSrc` | const 指针 | 源图像指针 | - |
| `nSrcStep` | int | 源图像行步幅 | - |
| `oSrcSizeROI` | HgppiSize | 源 ROI 尺寸 | - |
| `pDst` | 指针 | 目标图像指针 | - |
| `nDstStep` | int | 目标图像行步幅 | - |
| `oDstSizeROI` | HgppiSize | 目标 ROI 尺寸 | - |
| `nTopBorderHeight` | int | 上边界高度（像素） | - |
| `nLeftBorderWidth` | int | 左边界宽度（像素） | - |
| `hgppStreamCtx` | HgppStreamContext | 应用程序管理流上下文 | - |

#### 7.13.2. 函数列表
##### 7.13.2.1. 8 位无符号 (8u)
```c
HgppStatus hgppiCopyWrapBorder_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, HgppiSize oSrcSizeROI, HGpp8u *pDst, int nDstStep, HgppiSize oDstSizeROI, int nTopBorderHeight, int nLeftBorderWidth, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopyWrapBorder_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep, HgppiSize oSrcSizeROI, HGpp8u *pDst, int nDstStep, HgppiSize oDstSizeROI, int nTopBorderHeight, int nLeftBorderWidth, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopyWrapBorder_8u_C4R_Ctx(const HGpp8u *pSrc, int nSrcStep, HgppiSize oSrcSizeROI, HGpp8u *pDst, int nDstStep, HgppiSize oDstSizeROI, int nTopBorderHeight, int nLeftBorderWidth, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopyWrapBorder_8u_AC4R_Ctx(const HGpp8u *pSrc, int nSrcStep, HgppiSize oSrcSizeROI, HGpp8u *pDst, int nDstStep, HgppiSize oDstSizeROI, int nTopBorderHeight, int nLeftBorderWidth, HgppStreamContext hgppStreamCtx)
```

##### 7.13.2.2. 16 位/32 位 (16u, 16s, 32s, 32f)
```c
// 16u, 16s, 32s, 32f 类似，提供 C1R, C3R, C4R, AC4R 变体。
HgppStatus hgppiCopyWrapBorder_16u_C1R_Ctx(const Hgpp16u *pSrc, int nSrcStep, HgppiSize oSrcSizeROI, Hgpp16u *pDst, int nDstStep, HgppiSize oDstSizeROI, int nTopBorderHeight, int nLeftBorderWidth, HgppStreamContext hgppStreamCtx)
// ... 其他变体类似。
```

**未列出的函数**: 
- 完整函数列表请参考头文件 `hgppidei.h`。

### 7.14. 子像素拷贝
使用线性插值复制源图像的子像素坐标图像。

#### 7.14.1. 双线性插值公式
```text
dst(x, y) = lerp(lerp(src(x0, y0), src(x1, y0), dx),
                 lerp(src(x0, y1), src(x1, y1), dx), dy)
```

其中：
- `x0 = floor(x)`, `x1 = x0 + 1`
- `y0 = floor(y)`, `y1 = y0 + 1`
- `dx = x - x0`, `dy = y - y0`
- `lerp(a, b, t) = a * (1-t) + b * t`

#### 7.14.2. 通用参数
| 参数 | 类型 | 说明 | 注意事项 |
|------|------|------|----------|
| `pSrc` | const 指针 | 源图像指针 | - |
| `nSrcStep` | int | 源图像行步幅 | - |
| `pDst` | 指针 | 目标图像指针 | - |
| `nDstStep` | int | 目标图像行步幅 | - |
| `oDstSizeROI` | HgppiSize | 目标 ROI 尺寸 | 源 ROI 假定与目标 ROI 相同 |
| `nDx` | Hgpp32f | 源图像 X 坐标的小数部分 | 范围：[0, 1) |
| `nDy` | Hgpp32f | 源图像 Y 坐标的小数部分 | 范围：[0, 1) |
| `hgppStreamCtx` | HgppStreamContext | 应用程序管理流上下文 | - |

#### 7.14.3. 函数列表
##### 7.14.3.1. 8 位无符号 (8u)
```c
HgppStatus hgppiCopySubpix_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oDstSizeROI, Hgpp32f nDx, Hgpp32f nDy, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopySubpix_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oDstSizeROI, Hgpp32f nDx, Hgpp32f nDy, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopySubpix_8u_C4R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oDstSizeROI, Hgpp32f nDx, Hgpp32f nDy, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiCopySubpix_8u_AC4R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oDstSizeROI, Hgpp32f nDx, Hgpp32f nDy, HgppStreamContext hgppStreamCtx)
```

##### 7.14.3.2. 16 位/32 位 (16u, 16s, 32s, 32f)
```c
// 16u, 16s, 32s, 32f 类似，提供 C1R, C3R, C4R, AC4R 变体。
HgppStatus hgppiCopySubpix_16u_C1R_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oDstSizeROI, Hgpp32f nDx, Hgpp32f nDy, HgppStreamContext hgppStreamCtx)
// ... 其他变体类似。
```

**未列出的函数**: 
- 完整函数列表请参考头文件 `hgppidei.h`。

### 7.15. 位深度转换
#### 7.15.1. Convert To Increased Bit Depth （增加位深度转换）
整数转换方法不涉及缩放。

**注意事项**
- 当将整数（如 `Hgpp32u`）转换为浮点数（如 `Hgpp32f`）时，无法精确表示的整数值会舍入到最接近的浮点值。
- 当将有符号整数转换为无符号整数时，所有负值会丢失（饱和到 0）。
- 16f (`Hgpp16f`) 数据类型的指针和步幅最好至少 16 字节对齐以获得最佳性能

#### 7.15.2. 通用参数
| 参数 | 类型 | 说明 | 注意事项 |
|------|------|------|----------|
| `pSrc` | const 指针 | 源图像指针 | - |
| `nSrcStep` | int | 源图像行步幅 | - |
| `pDst` | 指针 | 目标图像指针 | - |
| `nDstStep` | int | 目标图像行步幅 | - |
| `oSizeROI` | HgppiSize | 感兴趣区域 (ROI) | - |
| `hgppStreamCtx` | HgppStreamContext | 应用程序管理流上下文 | - |

#### 7.15.3. 函数列表（部分）
```c
// 8u → 16u/16s/32s/32f。
HgppStatus hgppiConvert_8u16u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiConvert_8u16u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiConvert_8u16u_C4R_Ctx(const HGpp8u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiConvert_8u16u_AC4R_Ctx(const HGpp8u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

HgppStatus hgppiConvert_8u32f_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiConvert_8u32f_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiConvert_8u32f_C4R_Ctx(const HGpp8u *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiConvert_8u32f_AC4R_Ctx(const HGpp8u *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

// 16s/16u → 32s/32f, 16f → 32f。
HgppStatus hgppiConvert_16s32f_C1R_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiConvert_16f32f_C1R_Ctx(const Hgpp16f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

// 32s/32u → 32f。
HgppStatus hgppiConvert_32s32f_C1R_Ctx(const Hgpp32s *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiConvert_32u32f_C1R_Ctx(const Hgpp32u *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

// 带饱和的转换 (Rs)
HgppStatus hgppiConvert_8s8u_C1Rs_Ctx(const Hgpp8s *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
```

**未列出的函数**: 
- 完整转换函数定义（如 8s→16s/32s、 16s→32s 等）请参考头文件 `hgppidei.h`。

#### 7.15.4. Convert To Decreased Bit Depth （降低位深度转换）
**注意事项**
- 所有转换后的值都会饱和到目标类型的范围。
- 将浮点值转换为整数还涉及舍入，丢失所有小数值信息。
- 16f (`Hgpp16f`) 数据类型的指针和步幅最好至少 16 字节对齐以获得最佳性能

#### 7.15.5. 通用参数
| 参数 | 类型 | 说明 | 注意事项 |
|------|------|------|----------|
| `pSrc` | const 指针 | 源图像指针 | - |
| `nSrcStep` | int | 源图像行步幅 | - |
| `pDst` | 指针 | 目标图像指针 | - |
| `nDstStep` | int | 目标图像行步幅 | - |
| `oSizeROI` | HgppiSize | 感兴趣区域 (ROI) | - |
| `eRoundMode` | HgppRoundMode | 舍入模式参数 | 仅浮点到整数转换需要 |
| `nScaleFactor` | int | 整数结果缩放 | 部分函数需要 |
| `hgppStreamCtx` | HgppStreamContext | 应用程序管理流上下文 | - |

#### 7.15.6. 函数列表（部分）
```c
// 16u/16s/32s → 8u/8s。
HgppStatus hgppiConvert_16u8u_C1R_Ctx(const Hgpp16u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiConvert_32s8u_C1R_Ctx(const Hgpp32s *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

// 32f → 8u/8s/16u/16s/16f (需要舍入模式)
HgppStatus hgppiConvert_32f8u_C1R_Ctx(const Hgpp32f *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppRoundMode eRoundMode, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiConvert_32f16f_C1R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp16f *pDst, int nDstStep, HgppiSize oSizeROI, HgppRoundMode eRoundMode, HgppStreamContext hgppStreamCtx)

// 带缩放的转换 (RSfs)
HgppStatus hgppiConvert_32f8u_C1RSfs_Ctx(const Hgpp32f *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppRoundMode eRoundMode, int nScaleFactor, HgppStreamContext hgppStreamCtx)
```

**未列出的函数**: 
- 完整转换函数定义（如 32u→8u/16u/16s/32s 等）请参考头文件 `hgppidei.h`。

### 7.16. 位深度缩放
#### 7.16.1. Scale To Higher Bit Depth （缩放到位深度更高）
**缩放公式**

```text
dstPixelValue = dstMinRangeValue + scaleFactor * (srcPixelValue - srcMinRangeValue)
```
其中 `scaleFactor = (dstMaxRangeValue - dstMinRangeValue) / (srcMaxRangeValue - srcMinRangeValue)`

#### 7.16.2. 通用参数
| 参数 | 类型 | 说明 | 注意事项 |
|------|------|------|----------|
| `pSrc` | const 指针 | 源图像指针 | - |
| `nSrcStep` | int | 源图像行步幅 | - |
| `pDst` | 指针 | 目标图像指针 | - |
| `nDstStep` | int | 目标图像行步幅 | - |
| `oSizeROI` | HgppiSize | 感兴趣区域 (ROI) | - |
| `nMin` | Hgpp32f | 最小饱和值 | 浮点转换需要 |
| `nMax` | Hgpp32f | 最大饱和值 | 浮点转换需要 |
| `hgppStreamCtx` | HgppStreamContext | 应用程序管理流上下文 | - |

#### 7.16.3. 函数列表（部分）
```c
// 8u → 16u/16s/32s (整数范围映射)
HgppStatus hgppiScale_8u16u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiScale_8u16u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiScale_8u16u_C4R_Ctx(const HGpp8u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiScale_8u16u_AC4R_Ctx(const HGpp8u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, HgppStreamContext hgppStreamCtx)

// 8u → 32f (需要 nMin, nMax)
HgppStatus hgppiScale_8u32f_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, Hgpp32f nMin, Hgpp32f nMax, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiScale_8u32f_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, Hgpp32f nMin, Hgpp32f nMax, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiScale_8u32f_C4R_Ctx(const HGpp8u *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, Hgpp32f nMin, Hgpp32f nMax, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiScale_8u32f_AC4R_Ctx(const HGpp8u *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, Hgpp32f nMin, Hgpp32f nMax, HgppStreamContext hgppStreamCtx)
```

**未列出的函数**: 
- 16s/16u/32s → 32f 等缩放函数未列出，请参考头文件 `hgppidei.h`。

#### 7.16.4. Scale To Lower Bit Depth （缩放到位深度更低）
#### 7.16.5. 通用参数
| 参数 | 类型 | 说明 | 注意事项 |
|------|------|------|----------|
| `pSrc` | const 指针 | 源图像指针 | - |
| `nSrcStep` | int | 源图像行步幅 | - |
| `pDst` | 指针 | 目标图像指针 | - |
| `nDstStep` | int | 目标图像行步幅 | - |
| `oSizeROI` | HgppiSize | 感兴趣区域 (ROI) | - |
| `hint` | HgppHintAlgorithm | 算法性能/精度选择器 | 当前被忽略 |
| `nMin` | Hgpp32f | 最小饱和值 | 浮点→整数转换需要 |
| `nMax` | Hgpp32f | 最大饱和值 | 浮点→整数转换需要 |
| `hgppStreamCtx` | HgppStreamContext | 应用程序管理流上下文 | - |

#### 7.16.6. 函数列表（部分）
```c
// 16u/16s/32s → 8u (整数范围映射)
HgppStatus hgppiScale_16u8u_C1R_Ctx(const Hgpp16u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppHintAlgorithm hint, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiScale_16u8u_C3R_Ctx(const Hgpp16u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppHintAlgorithm hint, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiScale_16u8u_C4R_Ctx(const Hgpp16u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppHintAlgorithm hint, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiScale_16u8u_AC4R_Ctx(const Hgpp16u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, HgppHintAlgorithm hint, HgppStreamContext hgppStreamCtx)

// 32f → 8u (需要 nMin, nMax)
HgppStatus hgppiScale_32f8u_C1R_Ctx(const Hgpp32f *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, Hgpp32f nMin, Hgpp32f nMax, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiScale_32f8u_C3R_Ctx(const Hgpp32f *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, Hgpp32f nMin, Hgpp32f nMax, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiScale_32f8u_C4R_Ctx(const Hgpp32f *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, Hgpp32f nMin, Hgpp32f nMax, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiScale_32f8u_AC4R_Ctx(const Hgpp32f *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, Hgpp32f nMin, Hgpp32f nMax, HgppStreamContext hgppStreamCtx)
```

**未列出的函数**: 
- 16s/32s → 8s 等缩放函数未列出，请参考头文件 `hgppidei.h`。

### 7.17. 通道复制
将单通道图像复制到多通道图像的所有通道。

#### 7.17.1. 通用参数
| 参数 | 类型 | 说明 | 注意事项 |
|------|------|------|----------|
| `pSrc` | const 指针 | 源图像指针（单通道） | - |
| `nSrcStep` | int | 源图像行步幅 | - |
| `pDst` | 指针 | 目标图像指针（多通道） | - |
| `nDstStep` | int | 目标图像行步幅 | - |
| `oDstSizeROI` | HgppiSize | 目标 ROI 尺寸 | 源 ROI 假定与目标 ROI 相同 |
| `hgppStreamCtx` | HgppStreamContext | 应用程序管理流上下文 | - |

#### 7.17.2. 函数列表
```c
// 8 位无符号。
HgppStatus hgppiDup_8u_C1C3R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oDstSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiDup_8u_C1C4R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oDstSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiDup_8u_C1AC4R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oDstSizeROI, HgppStreamContext hgppStreamCtx)

// 16 位无符号/有符号。
HgppStatus hgppiDup_16u_C1C3R_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oDstSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiDup_16u_C1C4R_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oDstSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiDup_16u_C1AC4R_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oDstSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiDup_16s_C1C3R_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *pDst, int nDstStep, HgppiSize oDstSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiDup_16s_C1C4R_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *pDst, int nDstStep, HgppiSize oDstSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiDup_16s_C1AC4R_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *pDst, int nDstStep, HgppiSize oDstSizeROI, HgppStreamContext hgppStreamCtx)

// 32 位有符号/浮点。
HgppStatus hgppiDup_32s_C1C3R_Ctx(const Hgpp32s *pSrc, int nSrcStep, Hgpp32s *pDst, int nDstStep, HgppiSize oDstSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiDup_32s_C1C4R_Ctx(const Hgpp32s *pSrc, int nSrcStep, Hgpp32s *pDst, int nDstStep, HgppiSize oDstSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiDup_32s_C1AC4R_Ctx(const Hgpp32s *pSrc, int nSrcStep, Hgpp32s *pDst, int nDstStep, HgppiSize oDstSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiDup_32f_C1C3R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oDstSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiDup_32f_C1C4R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oDstSizeROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiDup_32f_C1AC4R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oDstSizeROI, HgppStreamContext hgppStreamCtx)
```

### 7.18. 转置
沿对角线（左上到右下）镜像图像。

#### 7.18.1. 通用参数
| 参数 | 类型 | 说明 | 注意事项 |
|------|------|------|----------|
| `pSrc` | const 指针 | 源图像指针 | - |
| `nSrcStep` | int | 源图像行步幅 | - |
| `pDst` | 指针 | 目标图像指针 | - |
| `nDstStep` | int | 目标图像行步幅 | - |
| `oSrcROI` | HgppiSize | 源 ROI 尺寸 | - |
| `hgppStreamCtx` | HgppStreamContext | 应用程序管理流上下文 | - |

#### 7.18.2. 函数列表
```c
// 8 位无符号。
HgppStatus hgppiTranspose_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSrcROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiTranspose_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSrcROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiTranspose_8u_C4R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSrcROI, HgppStreamContext hgppStreamCtx)

// 16 位无符号/有符号。
HgppStatus hgppiTranspose_16u_C1R_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSrcROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiTranspose_16u_C3R_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSrcROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiTranspose_16u_C4R_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSrcROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiTranspose_16s_C1R_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *pDst, int nDstStep, HgppiSize oSrcROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiTranspose_16s_C3R_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *pDst, int nDstStep, HgppiSize oSrcROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiTranspose_16s_C4R_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *pDst, int nDstStep, HgppiSize oSrcROI, HgppStreamContext hgppStreamCtx)

// 32 位有符号/浮点。
HgppStatus hgppiTranspose_32s_C1R_Ctx(const Hgpp32s *pSrc, int nSrcStep, Hgpp32s *pDst, int nDstStep, HgppiSize oSrcROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiTranspose_32s_C3R_Ctx(const Hgpp32s *pSrc, int nSrcStep, Hgpp32s *pDst, int nDstStep, HgppiSize oSrcROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiTranspose_32s_C4R_Ctx(const Hgpp32s *pSrc, int nSrcStep, Hgpp32s *pDst, int nDstStep, HgppiSize oSrcROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiTranspose_32f_C1R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSrcROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiTranspose_32f_C3R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSrcROI, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiTranspose_32f_C4R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSrcROI, HgppStreamContext hgppStreamCtx)
```

**未列出的函数**: 
- 8s、 16sc、 32sc、 32u、 16f、 32fc 类型的转置函数未列出

### 7.19. 通道交换
交换多通道图像中的通道顺序。

#### 7.19.1. aDstOrder 参数
`aDstOrder` 数组描述通道置换：第 n 个元素表示输出图像第 n 通道存储的输入通道号。

**示例**:
- RGB 图像，`aDstOrder = [2,1,0]` → BGR
- ARGB 图像，`aDstOrder = [3,2,1,0]` → BGRA

#### 7.19.2. 通用参数
| 参数 | 类型 | 说明 | 注意事项 |
|------|------|------|----------|
| `pSrc` | const 指针 | 源图像指针 | 部分函数为原图像操作 |
| `nSrcStep` | int | 源图像行步幅 | 原图像操作时为 nSrcDstStep |
| `pDst` | 指针 | 目标图像指针 | 部分函数不需要 |
| `nDstStep` | int | 目标图像行步幅 | - |
| `oSizeROI` | HgppiSize | 感兴趣区域 (ROI) | - |
| `aDstOrder` | const int[] | 通道置换数组 | 大小为 3 或 4 |
| `nValue` | 对应数据类型 | 常量值（C3C4R 需要） | aDstOrder 值=3 时输出 |
| `hgppStreamCtx` | HgppStreamContext | 应用程序管理流上下文 | - |

#### 7.19.3. 函数列表
##### 7.19.3.1. 8 位无符号 (8u)
```c
// C3R: 3 通道 → 3 通道。
HgppStatus hgppiSwapChannels_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, const int aDstOrder[3], HgppStreamContext hgppStreamCtx)

// C3IR: 3 通道，原图像操作。
HgppStatus hgppiSwapChannels_8u_C3IR_Ctx(HGpp8u *pSrcDst, int nSrcDstStep, HgppiSize oSizeROI, const int aDstOrder[3], HgppStreamContext hgppStreamCtx)

// C4C3R: 4 通道 → 3 通道。
HgppStatus hgppiSwapChannels_8u_C4C3R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, const int aDstOrder[3], HgppStreamContext hgppStreamCtx)

// C4R: 4 通道 → 4 通道。
HgppStatus hgppiSwapChannels_8u_C4R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, const int aDstOrder[4], HgppStreamContext hgppStreamCtx)

// C4IR: 4 通道，原图像操作。
HgppStatus hgppiSwapChannels_8u_C4IR_Ctx(HGpp8u *pSrcDst, int nSrcDstStep, HgppiSize oSizeROI, const int aDstOrder[4], HgppStreamContext hgppStreamCtx)

// C3C4R: 3 通道 → 4 通道（需要 nValue 填充第 4 通道）
HgppStatus hgppiSwapChannels_8u_C3C4R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, const int aDstOrder[4], const HGpp8u nValue, HgppStreamContext hgppStreamCtx)

// AC4R: 4 通道 → 4 通道（Alpha 不受影响）
HgppStatus hgppiSwapChannels_8u_AC4R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI, const int aDstOrder[3], HgppStreamContext hgppStreamCtx)
```

##### 7.19.3.2. 16 位/32 位 (16u, 16s, 32s, 32f)
```c
// 16u, 16s, 32s, 32f 类似，提供 C3R, C3IR, C4C3R, C4R, C4IR, C3C4R, AC4R 变体。
HgppStatus hgppiSwapChannels_16u_C3R_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, const int aDstOrder[3], HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSwapChannels_16u_C4R_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep, HgppiSize oSizeROI, const int aDstOrder[4], HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSwapChannels_32f_C3R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, const int aDstOrder[3], HgppStreamContext hgppStreamCtx)
HgppStatus hgppiSwapChannels_32f_C4R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep, HgppiSize oSizeROI, const int aDstOrder[4], HgppStreamContext hgppStreamCtx)
// ... 其他变体类似。
```

**aDstOrder 说明**:
- 值 = 3：输出 nValue 到该通道（C3C4R）
- 值 > 3：该目标通道值不变

**未列出的函数**: 
- 8s、 16sc、 32sc、 32u、 16f、 32fc 类型的通道交换函数未列出

### 7.20. 错误码
| 错误码 | 说明 |
|--------|------|
| `HGPP_NULL_POINTER_ERROR` | 空指针 |
| `HGPP_STEP_ERROR` | 步幅错误 |
| `HGPP_SIZE_ERROR` | ROI 尺寸错误 |
| `HGPP_ALIGNMENT_ERROR` | 对齐错误 |
| `HGPP_CHANNEL_ORDER_ERROR` | 通道顺序错误 |
| `HGPP_NOT_EVEN_STEP_ERROR` | 步幅不是像素倍数 |
| `HGPP_COI_ERROR` | 感兴趣通道无效 |
| `HGPP_SCALE_RANGE_ERROR` | 缩放范围错误 (nMax ≤ nMin) |

## 8. 图像滤波函数
函数定义于 `hgppi_f.h`，位于 `hgppif` 库中。
同类函数没有全部列出，完整函数定义请参考头文件。

### 8.1. 一维线性滤波
#### 8.1.1. FilterColumn （列滤波）
使用用户指定的一维权重列应用卷积滤波。

**运算公式：**

$$
\text{dstPixel} = \frac{1}{\text{nDivisor}} \sum_{i=0}^{\text{nMaskSize}-1} \text{pKernel}[i] \times \text{srcPixel}[y + i - \text{nAnchor}]
$$

##### 8.1.1.1. 通用参数
| 参数 | 说明 |
|------|------|
| `pSrc` | 源图像指针 |
| `nSrcStep` | 源图像行步幅 |
| `pDst` | 目标图像指针 |
| `nDstStep` | 目标图像行步幅 |
| `oROI` | 感兴趣区域 (ROI) |
| `pKernel` | 内核系数数组的起始地址指针（系数期望以相反顺序存储） |
| `nMaskSize` | 线性内核数组的长度 |
| `nAnchor` | 内核原点参考帧相对于源像素的 Y 偏移 |
| `nDivisor` | 滤波操作的卷积和被除的因子。如果等于系数之和，这将保持最大结果值在全量程内 |
| `hgppStreamCtx` | 应用程序管理流上下文 |

**返回值：** 图像数据相关错误码、 ROI 相关错误码

##### 8.1.1.2. 函数列表
**8 位无符号整数**

```c
HgppStatus hgppiFilterColumn_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep,
                                         HgppiSize oROI, const int *pKernel, int nMaskSize, int nAnchor, int nDivisor, HgppStreamContext hgppStreamCtx)
// 8 位无符号单通道 1D 列卷积。

HgppStatus hgppiFilterColumn_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep,
                                         HgppiSize oROI, const int *pKernel, int nMaskSize, int nAnchor, int nDivisor, HgppStreamContext hgppStreamCtx)
// 8 位无符号三通道 1D 列卷积。

HgppStatus hgppiFilterColumn_8u_C4R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep,
                                         HgppiSize oROI, const int *pKernel, int nMaskSize, int nAnchor, int nDivisor, HgppStreamContext hgppStreamCtx)
// 8 位无符号四通道 1D 列卷积。

HgppStatus hgppiFilterColumn_8u_AC4R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep,
                                          HgppiSize oROI, const int *pKernel, int nMaskSize, int nAnchor, int nDivisor, HgppStreamContext hgppStreamCtx)
// 8 位无符号四通道 1D 列卷积，忽略 alpha 通道。
```

**16 位无符号整数**

```c
HgppStatus hgppiFilterColumn_16u_C1R_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep,
                                          HgppiSize oROI, const int *pKernel, int nMaskSize, int nAnchor, int nDivisor, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiFilterColumn_16u_C3R_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep,
                                          HgppiSize oROI, const int *pKernel, int nMaskSize, int nAnchor, int nDivisor, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiFilterColumn_16u_C4R_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep,
                                          HgppiSize oROI, const int *pKernel, int nMaskSize, int nAnchor, int nDivisor, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiFilterColumn_16u_AC4R_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp16u *pDst, int nDstStep,
                                           HgppiSize oROI, const int *pKernel, int nMaskSize, int nAnchor, int nDivisor, HgppStreamContext hgppStreamCtx)
```

**16 位有符号整数**

```c
HgppStatus hgppiFilterColumn_16s_C1R_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *pDst, int nDstStep,
                                          HgppiSize oROI, const int *pKernel, int nMaskSize, int nAnchor, int nDivisor, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiFilterColumn_16s_C3R_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *pDst, int nDstStep,
                                          HgppiSize oROI, const int *pKernel, int nMaskSize, int nAnchor, int nDivisor, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiFilterColumn_16s_C4R_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *pDst, int nDstStep,
                                          HgppiSize oROI, const int *pKernel, int nMaskSize, int nAnchor, int nDivisor, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiFilterColumn_16s_AC4R_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp16s *pDst, int nDstStep,
                                           HgppiSize oROI, const int *pKernel, int nMaskSize, int nAnchor, int nDivisor, HgppStreamContext hgppStreamCtx)
```

**32 位浮点数**

```c
HgppStatus hgppiFilterColumn_32f_C1R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep,
                                          HgppiSize oROI, const float *pKernel, int nMaskSize, int nAnchor, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiFilterColumn_32f_C3R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep,
                                          HgppiSize oROI, const float *pKernel, int nMaskSize, int nAnchor, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiFilterColumn_32f_C4R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep,
                                          HgppiSize oROI, const float *pKernel, int nMaskSize, int nAnchor, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiFilterColumn_32f_AC4R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pDst, int nDstStep,
                                           HgppiSize oROI, const float *pKernel, int nMaskSize, int nAnchor, HgppStreamContext hgppStreamCtx)
```

**64 位浮点数**

```c
HgppStatus hgppiFilterColumn_64f_C1R_Ctx(const Hgpp64f *pSrc, int nSrcStep, Hgpp64f *pDst, int nDstStep,
                                          HgppiSize oROI, const double *pKernel, int nMaskSize, int nAnchor, HgppStreamContext hgppStreamCtx)
// 64 位浮点单通道 1D 列卷积。
```

#### 8.1.2. FilterColumnBorder （带边界控制的列滤波）
通用一维卷积列滤波，带边界控制。

如果掩码的任何部分与源图像边界重叠，则对落在源图像之外的所有掩码像素应用请求的边界类型操作。

目前仅支持 `HGPP_BORDER_REPLICATE` 边界类型操作。

##### 8.1.2.1. 通用参数
| 参数 | 说明 |
|------|------|
| `pSrc` | 源图像指针 |
| `nSrcStep` | 源图像行步幅 |
| `oSrcSize` | 源图像宽度和高度（像素） |
| `oSrcOffset` | pSrc 相对于源图像原点的像素偏移 |
| `pDst` | 目标图像指针 |
| `nDstStep` | 目标图像行步幅 |
| `oSizeROI` | 感兴趣区域 (ROI) |
| `pKernel` | 内核系数数组指针 |
| `nMaskSize` | 内核宽度 |
| `nAnchor` | 内核原点参考帧相对于源像素的 X 偏移 |
| `nDivisor` | 除数因子 |
| `eBorderType` | 要在源图像边界应用的边界类型操作 |
| `hgppStreamCtx` | 应用程序管理流上下文 |

##### 8.1.2.2. 函数列表
```c
HgppStatus hgppiFilterColumnBorder_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, HgppiSize oSrcSize, HgppiPoint oSrcOffset,
                                               HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                               const int *pKernel, int nMaskSize, int nAnchor, int nDivisor,
                                               HgppiBorderType eBorderType, HgppStreamContext hgppStreamCtx)
// 单通道 8 位无符号 1D 列卷积滤波，带边界控制。

HgppStatus hgppiFilterColumnBorder_8u_C3R_Ctx(...)  // 三通道。
HgppStatus hgppiFilterColumnBorder_8u_C4R_Ctx(...)  // 四通道。
HgppStatus hgppiFilterColumnBorder_8u_AC4R_Ctx(...) // 四通道，忽略 alpha。

HgppStatus hgppiFilterColumnBorder_16u_C1R_Ctx(...)  // 16 位无符号。
HgppStatus hgppiFilterColumnBorder_16u_C3R_Ctx(...)
HgppStatus hgppiFilterColumnBorder_16u_C4R_Ctx(...)
HgppStatus hgppiFilterColumnBorder_16u_AC4R_Ctx(...)

HgppStatus hgppiFilterColumnBorder_16s_C1R_Ctx(...)  // 16 位有符号。
HgppStatus hgppiFilterColumnBorder_16s_C3R_Ctx(...)
HgppStatus hgppiFilterColumnBorder_16s_C4R_Ctx(...)
HgppStatus hgppiFilterColumnBorder_16s_AC4R_Ctx(...)

HgppStatus hgppiFilterColumnBorder_32f_C1R_Ctx(...)  // 32 位浮点。
HgppStatus hgppiFilterColumnBorder_32f_C3R_Ctx(...)
HgppStatus hgppiFilterColumnBorder_32f_C4R_Ctx(...)
HgppStatus hgppiFilterColumnBorder_32f_AC4R_Ctx(...)
```

#### 8.1.3. FilterRow （行滤波）
使用用户指定的一维权重行应用卷积滤波。

##### 8.1.3.1. 函数列表
```c
HgppStatus hgppiFilterRow_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep,
                                      HgppiSize oROI, const int *pKernel, int nMaskSize, int nAnchor, int nDivisor, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiFilterRow_8u_C3R_Ctx(...)
HgppStatus hgppiFilterRow_8u_C4R_Ctx(...)
HgppStatus hgppiFilterRow_8u_AC4R_Ctx(...)

HgppStatus hgppiFilterRow_16u_C1R_Ctx(...)
HgppStatus hgppiFilterRow_16u_C3R_Ctx(...)
HgppStatus hgppiFilterRow_16u_C4R_Ctx(...)
HgppStatus hgppiFilterRow_16u_AC4R_Ctx(...)

HgppStatus hgppiFilterRow_16s_C1R_Ctx(...)
HgppStatus hgppiFilterRow_16s_C3R_Ctx(...)
HgppStatus hgppiFilterRow_16s_C4R_Ctx(...)
HgppStatus hgppiFilterRow_16s_AC4R_Ctx(...)

HgppStatus hgppiFilterRow_32f_C1R_Ctx(...)
HgppStatus hgppiFilterRow_32f_C3R_Ctx(...)
HgppStatus hgppiFilterRow_32f_C4R_Ctx(...)
HgppStatus hgppiFilterRow_32f_AC4R_Ctx(...)
```

#### 8.1.4. FilterRowBorder （带边界控制的行滤波）
```c
HgppStatus hgppiFilterRowBorder_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, HgppiSize oSrcSize, HgppiPoint oSrcOffset,
                                            HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                            const int *pKernel, int nMaskSize, int nAnchor, int nDivisor,
                                            HgppiBorderType eBorderType, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiFilterRowBorder_8u_C3R_Ctx(...)
HgppStatus hgppiFilterRowBorder_8u_C4R_Ctx(...)
HgppStatus hgppiFilterRowBorder_8u_AC4R_Ctx(...)

HgppStatus hgppiFilterRowBorder_16u_C1R_Ctx(...)
HgppStatus hgppiFilterRowBorder_16u_C3R_Ctx(...)
HgppStatus hgppiFilterRowBorder_16u_C4R_Ctx(...)
HgppStatus hgppiFilterRowBorder_16u_AC4R_Ctx(...)

HgppStatus hgppiFilterRowBorder_32f_C1R_Ctx(...)
HgppStatus hgppiFilterRowBorder_32f_C3R_Ctx(...)
HgppStatus hgppiFilterRowBorder_32f_C4R_Ctx(...)
HgppStatus hgppiFilterRowBorder_32f_AC4R_Ctx(...)
```

### 8.2. 二维卷积
#### 8.2.1. Filter （二维卷积）
应用二维卷积滤波。

**运算公式：**

$$
\text{dstPixel} = \frac{1}{\text{nDivisor}} \sum_{i=0}^{\text{maskH}-1} \sum_{j=0}^{\text{maskW}-1} \text{pKernel}[i \times \text{maskW} + j] \times \text{srcPixel}[x+j-\text{anchorX}, y+i-\text{anchorY}]
$$

##### 8.2.1.1. 通用参数
| 参数 | 说明 |
|------|------|
| `pSrc` | 源图像指针 |
| `nSrcStep` | 源图像行步幅 |
| `pDst` | 目标图像指针 |
| `nDstStep` | 目标图像行步幅 |
| `oROI` | 感兴趣区域 (ROI) |
| `pKernel` | 内核系数数组指针（期望以相反顺序存储） |
| `oMaskSize` | 内核宽度和高度 |
| `oAnchor` | 内核原点参考帧相对于源像素的 X 和 Y 偏移 |
| `nDivisor` | 除数因子 |
| `hgppStreamCtx` | 应用程序管理流上下文 |

##### 8.2.1.2. 函数列表
**8 位无符号整数**

```c
HgppStatus hgppiFilter_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep,
                                   HgppiSize oROI, const int *pKernel, HgppiSize oMaskSize, HgppiPoint oAnchor, int nDivisor, HgppStreamContext hgppStreamCtx)
// 8 位无符号单通道 2D 卷积。

HgppStatus hgppiFilter_8u_C3R_Ctx(...)  // 三通道。
HgppStatus hgppiFilter_8u_C4R_Ctx(...)  // 四通道。
HgppStatus hgppiFilter_8u_AC4R_Ctx(...) // 四通道，忽略 alpha。
```

**16 位无符号/有符号整数**

```c
HgppStatus hgppiFilter_16u_C1R_Ctx(...)
HgppStatus hgppiFilter_16u_C3R_Ctx(...)
HgppStatus hgppiFilter_16u_C4R_Ctx(...)
HgppStatus hgppiFilter_16u_AC4R_Ctx(...)

HgppStatus hgppiFilter_16s_C1R_Ctx(...)
HgppStatus hgppiFilter_16s_C3R_Ctx(...)
HgppStatus hgppiFilter_16s_C4R_Ctx(...)
HgppStatus hgppiFilter_16s_AC4R_Ctx(...)
```

**32 位浮点数**

```c
HgppStatus hgppiFilter_32f_C1R_Ctx(...)
HgppStatus hgppiFilter_32f_C3R_Ctx(...)
HgppStatus hgppiFilter_32f_C4R_Ctx(...)
HgppStatus hgppiFilter_32f_AC4R_Ctx(...)
```

#### 8.2.2. FilterBorder （带边界控制的二维卷积）
```c
HgppStatus hgppiFilterBorder_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, HgppiSize oSrcSize, HgppiPoint oSrcOffset,
                                         HGpp8u *pDst, int nDstStep, HgppiSize oROI,
                                         const int *pKernel, HgppiSize oMaskSize, HgppiPoint oAnchor, int nDivisor,
                                         HgppiBorderType eBorderType, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiFilterBorder_8u_C3R_Ctx(...)
HgppStatus hgppiFilterBorder_8u_C4R_Ctx(...)
HgppStatus hgppiFilterBorder_8u_AC4R_Ctx(...)

HgppStatus hgppiFilterBorder_16u_C1R_Ctx(...)
HgppStatus hgppiFilterBorder_16u_C3R_Ctx(...)
HgppStatus hgppiFilterBorder_16u_C4R_Ctx(...)
HgppStatus hgppiFilterBorder_16u_AC4R_Ctx(...)

HgppStatus hgppiFilterBorder_16s_C1R_Ctx(...)
HgppStatus hgppiFilterBorder_16s_C3R_Ctx(...)
HgppStatus hgppiFilterBorder_16s_C4R_Ctx(...)
HgppStatus hgppiFilterBorder_16s_AC4R_Ctx(...)

HgppStatus hgppiFilterBorder_32f_C1R_Ctx(...)
HgppStatus hgppiFilterBorder_32f_C3R_Ctx(...)
HgppStatus hgppiFilterBorder_32f_C4R_Ctx(...)
HgppStatus hgppiFilterBorder_32f_AC4R_Ctx(...)
```

### 8.3. 固定线性滤波
**固定滤波（Fixed Filters）**指使用预定义的固定核矩阵进行卷积运算，与用户自定义核的卷积不同。

**通用卷积公式：**

对于图像 $I$ 和核 $K$，卷积运算定义为：

$$
(I * K)(x, y) = \sum_{i=-a}^{a} \sum_{j=-b}^{b} K(i, j) \cdot I(x-i, y-j)
$$

其中 $(a, b)$ 是核的锚点位置。

#### 8.3.1. 数学原理
##### 8.3.1.1. Box Filter （盒式滤波）
盒式滤波使用均匀权重的矩形核，核内所有系数相等：

$$
K_{box}(i, j) = \frac{1}{w \times h}, \quad -\frac{w}{2} \leq i \leq \frac{w}{2}, -\frac{h}{2} \leq j \leq \frac{h}{2}
$$

**运算公式：**

$$
\text{dst}(x, y) = \frac{1}{w \times h} \sum_{i=-w/2}^{w/2} \sum_{j=-h/2}^{h/2} \text{src}(x-i, y-j)
$$

**特性：**
- 低通滤波器，平滑图像
- 所有像素权重相同
- 计算简单，可分离为两个 1D 卷积

##### 8.3.1.2. Gaussian Filter （高斯滤波）
高斯核基于二维高斯函数（正态分布）：

$$
G(x, y) = \frac{1}{2\pi\sigma^2} e^{-\frac{x^2+y^2}{2\sigma^2}}
$$

其中 $\sigma$ 是标准差，控制平滑程度。

**离散化核：**

对于 $(2k+1) \times (2k+1)$ 的核：

$$
K_{gauss}(i, j) = \frac{1}{2\pi\sigma^2} e^{-\frac{i^2+j^2}{2\sigma^2}}, \quad -k \leq i, j \leq k
$$

**归一化：**

$$
\sum_{i=-k}^{k} \sum_{j=-k}^{k} K_{gauss}(i, j) = 1
$$

**特性：**
- 最优低通滤波器（频域无振铃）
- 可分离为两个 1D 高斯卷积
- 旋转对称

##### 8.3.1.3. Laplacian Filter （拉普拉斯滤波）
拉普拉斯算子是二阶微分算子：

$$
\Delta f = \frac{\partial^2 f}{\partial x^2} + \frac{\partial^2 f}{\partial y^2}
$$

**离散近似：**

$$
\Delta f(x, y) \approx f(x+1, y) + f(x-1, y) + f(x, y+1) + f(x, y-1) - 4f(x, y)
$$

**3×3 核：**

$$
K_{laplace} = \begin{bmatrix} 0 & -1 & 0 \\ -1 & 4 & -1 \\ 0 & -1 & 0 \end{bmatrix} \quad \text{或} \quad \begin{bmatrix} -1 & -1 & -1 \\ -1 & 8 & -1 \\ -1 & -1 & -1 \end{bmatrix}
$$

**特性：**
- 二阶微分，对边缘响应强。
- 各向同性（旋转不变）
- 对噪声敏感

##### 8.3.1.4. Sobel Filter （索贝尔滤波）
Sobel 算子结合高斯平滑和一阶微分：

**水平梯度（检测垂直边缘）：**

$$
G_x = \begin{bmatrix} -1 & 0 & +1 \\ -2 & 0 & +2 \\ -1 & 0 & +1 \end{bmatrix} * I
$$

**垂直梯度（检测水平边缘）：**

$$
G_y = \begin{bmatrix} -1 & -2 & -1 \\ 0 & 0 & 0 \\ +1 & +2 & +1 \end{bmatrix} * I
$$

**梯度幅值：**

$$
|\nabla I| = \sqrt{G_x^2 + G_y^2}
$$

**梯度方向：**

$$
\theta = \arctan\left(\frac{G_y}{G_x}\right)
$$

**特性：**
- 一阶微分算子
- 结合平滑，抗噪声
- 边缘定位准确

##### 8.3.1.5. Prewitt Filter （普鲁维特滤波）
Prewitt 算子是简化版的 Sobel，权重均匀：

**水平梯度：**

$$
G_x = \begin{bmatrix} -1 & 0 & +1 \\ -1 & 0 & +1 \\ -1 & 0 & +1 \end{bmatrix} * I
$$

**垂直梯度：**

$$
G_y = \begin{bmatrix} -1 & -1 & -1 \\ 0 & 0 & 0 \\ +1 & +1 & +1 \end{bmatrix} * I
$$

**特性：**
- 计算比 Sobel 简单。
- 抗噪声能力稍弱
- 边缘检测效果类似

##### 8.3.1.6. Scharr Filter （谢尔滤波）
Scharr 算子是 Sobel 的优化版本，提供更准确的旋转不变性：

**水平梯度：**

$$
G_x = \begin{bmatrix} -3 & 0 & +3 \\ -10 & 0 & +10 \\ -3 & 0 & +3 \end{bmatrix} * I
$$

**垂直梯度：**

$$
G_y = \begin{bmatrix} -3 & -10 & -3 \\ 0 & 0 & 0 \\ +3 & +10 & +3 \end{bmatrix} * I
$$

**特性：**
- 优化的系数，减少旋转误差。
- 比 Sobel 更准确
- 计算复杂度相同

##### 8.3.1.7. Roberts Filter （罗伯茨交叉滤波）
Roberts 算子使用 2×2 交叉核，检测对角边缘：

**交叉差分：**

$$
G_1 = \begin{bmatrix} +1 & 0 \\ 0 & -1 \end{bmatrix} * I, \quad G_2 = \begin{bmatrix} 0 & +1 \\ -1 & 0 \end{bmatrix} * I
$$

**梯度幅值：**

$$
|\nabla I| = \sqrt{G_1^2 + G_2^2}
$$

**特性：**
- 最小尺寸（2×2）的边缘检测核
- 对噪声非常敏感
- 边缘定位精确

#### 8.3.2. 函数支持
##### 8.3.2.1. Box Filter （盒式滤波）
```c
HgppStatus hgppiFilterBox_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep,
                                      HgppiSize oROI, HgppiSize oMaskSize, HgppiPoint oAnchor, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiFilterBox_8u_C3R_Ctx(...)
HgppStatus hgppiFilterBox_16u_C1R_Ctx(...)
HgppStatus hgppiFilterBox_32f_C1R_Ctx(...)
```

##### 8.3.2.2. Gaussian Filter （高斯滤波）
**高斯核公式：**

$$
G(x, y) = \frac{1}{2\pi\sigma^2} e^{-\frac{x^2+y^2}{2\sigma^2}}
$$

```c
HgppStatus hgppiFilterGaussian_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep,
                                           HgppiSize oROI, HgppiSize oMaskSize, HgppiPoint oAnchor, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiFilterGaussian_8u_C3R_Ctx(...)
HgppStatus hgppiFilterGaussian_16u_C1R_Ctx(...)
HgppStatus hgppiFilterGaussian_32f_C1R_Ctx(...)
```

###### 1. Gaussian Filter Advanced （高斯滤波高级版）

> **提示：**
> Advanced 版本允许用户提供自定义高斯核，而不是使用内置的标准高斯核。

```c
// FilterGaussAdvanced - 用户自定义高斯核。
HgppStatus hgppiFilterGaussAdvanced_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                                HGpp8u *pDst, int nDstStep,
                                                HgppiSize oROI,
                                                const Hgpp32f *pGaussKernel,
                                                int nKernelSize,
                                                HgppStreamContext hgppStreamCtx)

HgppStatus hgppiFilterGaussAdvanced_8u_C3R_Ctx(...)
HgppStatus hgppiFilterGaussAdvanced_16u_C1R_Ctx(...)
HgppStatus hgppiFilterGaussAdvanced_32f_C1R_Ctx(...)

// FilterGaussAdvancedBorder - 带边界控制的自定义高斯滤波。
HgppStatus hgppiFilterGaussAdvancedBorder_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                                      HGpp8u *pDst, int nDstStep,
                                                      HgppiSize oROI,
                                                      const Hgpp32f *pGaussKernel,
                                                      int nKernelSize,
                                                      HgppiBorderType eBorderType,
                                                      HgppStreamContext hgppStreamCtx)

HgppStatus hgppiFilterGaussAdvancedBorder_8u_C3R_Ctx(...)
HgppStatus hgppiFilterGaussAdvancedBorder_16u_C1R_Ctx(...)
HgppStatus hgppiFilterGaussAdvancedBorder_32f_C1R_Ctx(...)
```

###### 2. Box Filter Border Advanced （盒式滤波边界高级版）

> **提示：**
> Advanced Border 版本提供边界控制和优化的内存管理。

```c
// 需要先调用 GetDeviceBufferSize 获取缓冲区大小。
HgppStatus hgppiFilterBoxBorderAdvancedGetDeviceBufferSize(HgppiSize oROI,
                                                            int nMaskSize,
                                                            size_t *pBufferSize)

// Box Filter Border Advanced。
HgppStatus hgppiFilterBoxBorderAdvanced_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                                    HGpp8u *pDst, int nDstStep,
                                                    HgppiSize oROI,
                                                    HgppiSize oMaskSize,
                                                    HgppiBorderType eBorderType,
                                                    HGpp8u *pDeviceBuffer,
                                                    HgppStreamContext hgppStreamCtx)

HgppStatus hgppiFilterBoxBorderAdvanced_8u_C3R_Ctx(...)
HgppStatus hgppiFilterBoxBorderAdvanced_16u_C1R_Ctx(...)
HgppStatus hgppiFilterBoxBorderAdvanced_32f_C1R_Ctx(...)
```

##### 8.3.2.3. Laplacian Filter （拉普拉斯滤波）
**拉普拉斯算子：**

$$
\Delta f = \frac{\partial^2 f}{\partial x^2} + \frac{\partial^2 f}{\partial y^2}
$$

```c
HgppStatus hgppiFilterLaplacian_8u_C1R_Ctx(...)
HgppStatus hgppiFilterLaplacian_8u_C3R_Ctx(...)
HgppStatus hgppiFilterLaplacian_16u_C1R_Ctx(...)
HgppStatus hgppiFilterLaplacian_32f_C1R_Ctx(...)
```

##### 8.3.2.4. Sobel Filter （Sobel 滤波）
**Sobel 算子：**

$$
G_x = \begin{bmatrix} -1 & 0 & +1 \\ -2 & 0 & +2 \\ -1 & 0 & +1 \end{bmatrix} * \text{image}
$$

$$
G_y = \begin{bmatrix} -1 & -2 & -1 \\ 0 & 0 & 0 \\ +1 & +2 & +1 \end{bmatrix} * \text{image}
$$

$$
\text{gradient} = \sqrt{G_x^2 + G_y^2}
$$

```c
// 水平 Sobel。
HgppStatus hgppiFilterSobelHoriz_8u_C1R_Ctx(...)
HgppStatus hgppiFilterSobelHoriz_16u_C1R_Ctx(...)
HgppStatus hgppiFilterSobelHoriz_32f_C1R_Ctx(...)

// 垂直 Sobel。
HgppStatus hgppiFilterSobelVert_8u_C1R_Ctx(...)
HgppStatus hgppiFilterSobelVert_16u_C1R_Ctx(...)
HgppStatus hgppiFilterSobelVert_32f_C1R_Ctx(...)
```

##### 8.3.2.5. Scharr Filter （Scharr 滤波）
```c
HgppStatus hgppiFilterScharrHoriz_8u_C1R_Ctx(...)
HgppStatus hgppiFilterScharrVert_8u_C1R_Ctx(...)
HgppStatus hgppiFilterScharrHoriz_16u_C1R_Ctx(...)
HgppStatus hgppiFilterScharrVert_16u_C1R_Ctx(...)
```

##### 8.3.2.6. Prewitt Filter （Prewitt 滤波）
```c
HgppStatus hgppiFilterPrewittHoriz_8u_C1R_Ctx(...)
HgppStatus hgppiFilterPrewittVert_8u_C1R_Ctx(...)
HgppStatus hgppiFilterPrewittHoriz_16u_C1R_Ctx(...)
HgppStatus hgppiFilterPrewittVert_16u_C1R_Ctx(...)
```

### 8.4. Rank 滤波
#### 8.4.1. FilterMax （最大值滤波）
结果像素值是矩形掩码区域下像素值的最大值。

##### 8.4.1.1. 函数列表
```c
HgppStatus hgppiFilterMax_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep,
                                      HgppiSize oSizeROI, HgppiSize oMaskSize, HgppiPoint oAnchor, HgppStreamContext hgppStreamCtx)
// 单通道 8 位无符号最大值滤波。

HgppStatus hgppiFilterMax_8u_C3R_Ctx(...)  // 三通道。
HgppStatus hgppiFilterMax_8u_C4R_Ctx(...)  // 四通道。
HgppStatus hgppiFilterMax_8u_AC4R_Ctx(...) // 四通道，忽略 alpha。

HgppStatus hgppiFilterMax_16u_C1R_Ctx(...)  // 16 位无符号。
HgppStatus hgppiFilterMax_16u_C3R_Ctx(...)
HgppStatus hgppiFilterMax_16u_C4R_Ctx(...)
HgppStatus hgppiFilterMax_16u_AC4R_Ctx(...)

HgppStatus hgppiFilterMax_16s_C1R_Ctx(...)  // 16 位有符号。
HgppStatus hgppiFilterMax_16s_C3R_Ctx(...)
HgppStatus hgppiFilterMax_16s_C4R_Ctx(...)
HgppStatus hgppiFilterMax_16s_AC4R_Ctx(...)

HgppStatus hgppiFilterMax_32f_C1R_Ctx(...)  // 32 位浮点。
HgppStatus hgppiFilterMax_32f_C3R_Ctx(...)
HgppStatus hgppiFilterMax_32f_C4R_Ctx(...)
HgppStatus hgppiFilterMax_32f_AC4R_Ctx(...)
```

#### 8.4.2. FilterMaxBorder （带边界控制的最大值滤波）
```c
HgppStatus hgppiFilterMaxBorder_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, HgppiSize oSrcSize, HgppiPoint oSrcOffset,
                                            HGpp8u *pDst, int nDstStep, HgppiSize oSizeROI,
                                            HgppiSize oMaskSize, HgppiPoint oAnchor,
                                            HgppiBorderType eBorderType, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiFilterMaxBorder_8u_C3R_Ctx(...)
HgppStatus hgppiFilterMaxBorder_8u_C4R_Ctx(...)
HgppStatus hgppiFilterMaxBorder_8u_AC4R_Ctx(...)

HgppStatus hgppiFilterMaxBorder_16u_C1R_Ctx(...)
HgppStatus hgppiFilterMaxBorder_16u_C3R_Ctx(...)
HgppStatus hgppiFilterMaxBorder_16u_C4R_Ctx(...)
HgppStatus hgppiFilterMaxBorder_16u_AC4R_Ctx(...)

HgppStatus hgppiFilterMaxBorder_16s_C1R_Ctx(...)
HgppStatus hgppiFilterMaxBorder_16s_C3R_Ctx(...)
HgppStatus hgppiFilterMaxBorder_16s_C4R_Ctx(...)
HgppStatus hgppiFilterMaxBorder_16s_AC4R_Ctx(...)

HgppStatus hgppiFilterMaxBorder_32f_C1R_Ctx(...)
HgppStatus hgppiFilterMaxBorder_32f_C3R_Ctx(...)
HgppStatus hgppiFilterMaxBorder_32f_C4R_Ctx(...)
HgppStatus hgppiFilterMaxBorder_32f_AC4R_Ctx(...)
```

#### 8.4.3. FilterMin （最小值滤波）
结果像素值是矩形掩码区域下像素值的最小值。

```c
HgppStatus hgppiFilterMin_8u_C1R_Ctx(...)
HgppStatus hgppiFilterMin_8u_C3R_Ctx(...)
HgppStatus hgppiFilterMin_8u_C4R_Ctx(...)
HgppStatus hgppiFilterMin_8u_AC4R_Ctx(...)

HgppStatus hgppiFilterMin_16u_C1R_Ctx(...)
HgppStatus hgppiFilterMin_16u_C3R_Ctx(...)
HgppStatus hgppiFilterMin_16u_C4R_Ctx(...)
HgppStatus hgppiFilterMin_16u_AC4R_Ctx(...)

HgppStatus hgppiFilterMin_16s_C1R_Ctx(...)
HgppStatus hgppiFilterMin_16s_C3R_Ctx(...)
HgppStatus hgppiFilterMin_16s_C4R_Ctx(...)
HgppStatus hgppiFilterMin_16s_AC4R_Ctx(...)

HgppStatus hgppiFilterMin_32f_C1R_Ctx(...)
HgppStatus hgppiFilterMin_32f_C3R_Ctx(...)
HgppStatus hgppiFilterMin_32f_C4R_Ctx(...)
HgppStatus hgppiFilterMin_32f_AC4R_Ctx(...)
```

#### 8.4.4. FilterMinBorder （带边界控制的最小值滤波）
```c
HgppStatus hgppiFilterMinBorder_8u_C1R_Ctx(...)
HgppStatus hgppiFilterMinBorder_8u_C3R_Ctx(...)
HgppStatus hgppiFilterMinBorder_8u_C4R_Ctx(...)
HgppStatus hgppiFilterMinBorder_8u_AC4R_Ctx(...)

HgppStatus hgppiFilterMinBorder_16u_C1R_Ctx(...)
HgppStatus hgppiFilterMinBorder_16u_C3R_Ctx(...)
HgppStatus hgppiFilterMinBorder_16u_C4R_Ctx(...)
HgppStatus hgppiFilterMinBorder_16u_AC4R_Ctx(...)

HgppStatus hgppiFilterMinBorder_16s_C1R_Ctx(...)
HgppStatus hgppiFilterMinBorder_16s_C3R_Ctx(...)
HgppStatus hgppiFilterMinBorder_16s_C4R_Ctx(...)
HgppStatus hgppiFilterMinBorder_16s_AC4R_Ctx(...)

HgppStatus hgppiFilterMinBorder_32f_C1R_Ctx(...)
HgppStatus hgppiFilterMinBorder_32f_C3R_Ctx(...)
HgppStatus hgppiFilterMinBorder_32f_C4R_Ctx(...)
HgppStatus hgppiFilterMinBorder_32f_AC4R_Ctx(...)
```

#### 8.4.5. FilterMedian （中值滤波）
```c
HgppStatus hgppiFilterMedian_3x3_8u_C1R_Ctx(...)  // 3x3 掩码。
HgppStatus hgppiFilterMedian_3x3_8u_C3R_Ctx(...)
HgppStatus hgppiFilterMedian_5x5_8u_C1R_Ctx(...)  // 5x5 掩码。
HgppStatus hgppiFilterMedian_8u_C1R_Ctx(...)      // 通用掩码。
```

### 8.5. 距离变换
**距离变换（Distance Transform）**计算图像中每个像素到最近特征点（通常是前景像素）的距离。

#### 8.5.1. 数学原理
##### 8.5.1.1. 距离定义
**欧几里得距离：**

对于像素 $(x_1, y_1)$ 和 $(x_2, y_2)$：

$$
d_E((x_1, y_1), (x_2, y_2)) = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}
$$

**曼哈顿距离（城市街区距离）：**

$$
d_M((x_1, y_1), (x_2, y_2)) = |x_2 - x_1| + |y_2 - y_1|
$$

**棋盘距离：**

$$
d_C((x_1, y_1), (x_2, y_2)) = \max(|x_2 - x_1|, |y_2 - y_1|)
$$

##### 8.5.1.2. 距离变换公式
**输入：** 二值图像 $I(x, y)$，其中前景像素值为 1，背景为 0。

**输出：** 距离图 $D(x, y)$，每个像素值为到最近前景像素的距离。

$$
D(x, y) = \min_{(x', y') \in \text{Foreground}} d((x, y), (x', y'))
$$

其中 $d$ 是选用的距离度量（欧几里得、曼哈顿或棋盘距离）。

##### 8.5.1.3. Parallel Banding Algorithm (PBA)
PBA 是一种高效的并行距离变换算法，时间复杂度为 $O(1)$（每个像素）。

**核心思想：**
1. 将图像分割为多个带状区域（bands）
2. 每个带状区域独立计算距离。
3. 合并相邻带状区域的结果。

**一维距离变换：**

对于一维信号 $f[i]$，距离变换为：

$$
D[i] = \min_{j} (f[j] + |i - j|^2)
$$

**优化：** 使用下包络（lower envelope）技术，将复杂度从 $O(n^2)$ 降低到 $O(n)$。

**二维扩展：**

二维距离变换可分解为两个一维变换：

$$
D(x, y) = \min_{x'} (D_x(x', y) + (x - x')^2)
$$

其中 $D_x$ 是垂直方向的一维距离变换。

##### 8.5.1.4. Voronoi 图
**Voronoi 区域：**

对于前景点集 $S = \{s_1, s_2, \ldots, s_n\}$，每个点 $s_i$ 的 Voronoi 区域为：

$$
V(s_i) = \{p \mid d(p, s_i) \leq d(p, s_j) \forall j \neq i\}
$$

**Voronoi 图输出：**

距离变换同时生成：
1. **距离图** $D(x, y)$ - 每个像素到最近前景点的距离
2. **Voronoi 索引图** $I(x, y)$ - 每个像素所属的 Voronoi 区域索引
3. **相对距离图** - 相对于 Voronoi 中心的相对坐标

#### 8.5.2. Distance Transform 函数支持
使用 Parallel Banding Algorithm (PBA+) 执行精确欧几里得距离变换。

```c
// 计算缓冲区大小。
HgppStatus hgppiDistanceTransformPBAGetBufferSize(HgppiSize oSizeROI, size_t *hpBufferSize)
HgppStatus hgppiDistanceTransformPBAGetAntialiasingBufferSize(HgppiSize oSizeROI, size_t *hpAntialiasingBufferSize)

// 距离变换函数。
HgppStatus hgppiDistanceTransformPBA_8u16u_C1R_Ctx(HGpp8u *pSrc, int nSrcStep,
                                                    HGpp8u nMinSiteValue, HGpp8u nMaxSiteValue,
                                                    Hgpp16s *pDstVoronoi, int nDstVoronoiStep,
                                                    Hgpp16s *pDstVoronoiIndices, int nDstVoronoiIndicesStep,
                                                    Hgpp16s *pDstVoronoiRelativeManhattanDistances, int nDstVoronoiRelativeManhattanDistancesStep,
                                                    Hgpp16u *pDstTransform, int nDstTransformStep,
                                                    HgppiSize oSizeROI, HGpp8u *pDeviceBuffer, HgppStreamContext hgppStreamCtx)
```

### 8.6. 计算机视觉滤波
#### 8.6.1. 数学原理
##### 8.6.1.1. Canny 边缘检测
Canny 算法是最优边缘检测算法，包含 5 个步骤：

**步骤 1：高斯平滑**

$$
I_{smooth} = G_\sigma * I
$$

**步骤 2：计算梯度**

使用 Sobel 算子计算梯度幅值和方向：

$$
|\nabla I| = \sqrt{G_x^2 + G_y^2}, \quad \theta = \arctan\left(\frac{G_y}{G_x}\right)
$$

**步骤 3：非极大值抑制**

沿梯度方向抑制非局部最大值：

$$
M(x, y) = \begin{cases} |\nabla I(x, y)| & \text{if } |\nabla I(x, y)| \text{ is local maximum} \\ 0 & \text{otherwise} \end{cases}
$$

**步骤 4：双阈值检测**

使用高阈值 $T_{high}$ 和低阈值 $T_{low}$：

$$
E(x, y) = \begin{cases} \text{强边缘} & \text{if } M(x, y) \geq T_{high} \\ \text{弱边缘} & \text{if } T_{low} \leq M(x, y) < T_{high} \\ \text{非边缘} & \text{if } M(x, y) < T_{low} \end{cases}
$$

**步骤 5：边缘连接（滞后阈值）**

弱边缘仅当连接到强边缘时保留：

$$
E_{final}(x, y) = \begin{cases} 1 & \text{if } E(x, y) = \text{强边缘} \\ 1 & \text{if } E(x, y) = \text{弱边缘 且 连接到强边缘} \\ 0 & \text{otherwise} \end{cases}
$$

##### 8.6.1.2. Hough 线检测
Hough 变换将图像空间的直线映射到参数空间。

**直线参数化：**

使用极坐标表示直线：

$$
\rho = x \cos\theta + y \sin\theta
$$

其中：
- $\rho$：原点到直线的垂直距离
- $\theta$：垂线与 x 轴的夹角

**投票机制：**

对于每个边缘点 $(x_i, y_i)$，在参数空间 $(\rho, \theta)$ 中投票：

$$
H(\rho, \theta) = \sum_{i} \delta(\rho - x_i \cos\theta - y_i \sin\theta)
$$

**检测直线：**

查找累加器中的局部最大值：

$$
(\rho^*, \theta^*) = \arg\max_{\rho, \theta} H(\rho, \theta)
$$

##### 8.6.1.3. Harris 角点检测
Harris 角点检测基于局部自相关矩阵。

**自相关矩阵：**

$$
M = \sum_{x, y} w(x, y) \begin{bmatrix} I_x^2 & I_x I_y \\ I_x I_y & I_y^2 \end{bmatrix}
$$

其中 $I_x, I_y$ 是图像梯度，$w(x, y)$ 是窗口函数（通常为高斯窗口）。

**角点响应函数：**

$$
R = \det(M) - k \cdot \text{trace}(M)^2
$$

其中：
- $\det(M) = \lambda_1 \lambda_2$
- $\text{trace}(M) = \lambda_1 + \lambda_2$
- $\lambda_1, \lambda_2$ 是 $M$ 的特征值
- $k$ 是灵敏度参数（通常 0.04-0.06）

**角点判定：**

$$
\text{角点} = \begin{cases} R > \text{threshold} & \text{角点} \\ R \leq \text{threshold} & \text{非角点} \end{cases}
$$

**特征值分析：**
- $|\lambda_1| \approx |\lambda_2|$ 且都大 → 角点
- $|\lambda_1| \gg |\lambda_2|$ 或反之 → 边缘
- $|\lambda_1| \approx |\lambda_2| \approx 0$ → 平坦区域

##### 8.6.1.4. Non-Maximum Suppression （非极大值抑制）
NMS 用于细化边缘，保留梯度方向的局部最大值。

**梯度方向量化：**

将梯度方向 $\theta$ 量化为 4 个方向：

$$
\theta_{quant} = \begin{cases} 0^\circ & \text{if } \theta \in [-22.5^\circ, 22.5^\circ] \cup [157.5^\circ, 202.5^\circ] \\ 45^\circ & \text{if } \theta \in [22.5^\circ, 67.5^\circ] \cup [-157.5^\circ, -112.5^\circ] \\ 90^\circ & \text{if } \theta \in [67.5^\circ, 112.5^\circ] \cup [-112.5^\circ, -67.5^\circ] \\ 135^\circ & \text{if } \theta \in [112.5^\circ, 157.5^\circ] \cup [-67.5^\circ, -22.5^\circ] \end{cases}
$$

**抑制非极大值：**

对于每个像素 $(x, y)$，比较梯度方向上的相邻像素：

$$
M_{nms}(x, y) = \begin{cases} |\nabla I(x, y)| & \text{if } |\nabla I(x, y)| \geq |\nabla I(x', y')| \text{ for neighbors} \\ 0 & \text{otherwise} \end{cases}
$$

#### 8.6.2. 函数支持
##### 8.6.2.1. Canny Edge Detection （Canny 边缘检测）
```c
HgppStatus hgppiFilterCanny_8u_C1R_Ctx(...)
HgppStatus hgppiFilterCanny_16u_C1R_Ctx(...)
```

##### 8.6.2.2. Hough Line Detection （Hough 线检测）
```c
HgppStatus hgppiFilterHoughLine_8u_C1R_Ctx(...)
```

##### 8.6.2.3. Harris Corner Detection （Harris 角点检测）
```c
HgppStatus hgppiFilterHarrisResponse_32f_C1R_Ctx(...)
HgppStatus hgppiFilterHarrisCorner_32f_C1R_Ctx(...)
```

### 8.7. Flood Fill （洪水填充）
**洪水填充（Flood Fill）**是从种子点开始，填充连通区域的算法。

#### 8.7.1. 数学原理
##### 8.7.1.1. 连通性定义
**4 连通（4-Way Connectivity）：**

从种子点 $(x_0, y_0)$ 开始，递归访问：

$$
(x, y) \in \text{Region} \iff \begin{cases} (x, y) = (x_0, y_0) & \text{种子点} \\ \text{或 } \exists (x', y') \in \text{Region} \cap N_4(x, y) & \text{连通} \\ \text{且 } |\text{color}(x, y) - \text{color}(x_0, y_0)| \leq \text{tolerance} & \text{颜色匹配} \end{cases}
$$

**8 连通（8-Way Connectivity）：**

使用 8 邻域 $N_8(x, y)$ 替代 $N_4(x, y)$。

##### 8.7.1.2. 颜色匹配条件
**精确匹配：**

$$
\text{color}(x, y) = \text{color}(x_0, y_0)
$$

**容差匹配：**

对于每个通道 $c$：

$$
|\text{color}_c(x, y) - \text{color}_c(x_0, y_0)| \leq \text{tolerance}
$$

**上下界匹配：**

$$
\text{loDiff}_c \leq \text{color}_c(x, y) - \text{color}_c(x_0, y_0) \leq \text{upDiff}_c
$$

##### 8.7.1.3. 填充算法
**递归实现：**

```text
FloodFill(x, y, targetColor, replacementColor):
    if color(x, y) ≠ targetColor: return
    color(x, y) ← replacementColor
    FloodFill(x+1, y, ...)
    FloodFill(x-1, y, ...)
    FloodFill(x, y+1, ...)
    FloodFill(x, y-1, ...)
```

**迭代实现（使用栈）：**

$$
S = \{(x_0, y_0)\} \\
\text{while } S \neq \emptyset: \\
\quad (x, y) \leftarrow S.\text{pop}() \\
\quad \text{if } \text{color}(x, y) = \text{targetColor}: \\
\quad\quad \text{color}(x, y) \leftarrow \text{replacementColor} \\
\quad\quad S.\text{push}(N(x, y))
$$

##### 8.7.1.4. 边界控制
**带边界的填充：**

$$
(x, y) \in \text{Region} \iff \begin{cases} (x, y) \text{ 与种子点连通} \\ \text{color}(x, y) \neq \text{boundaryColor} \end{cases}
$$

#### 8.7.2. 函数支持
##### 8.7.2.1. Flood Fill 4-Way
```c
HgppStatus hgppiFloodFill4Way_8u_C1R_Ctx(...)
```

##### 8.7.2.2. Flood Fill 8-Way
```c
HgppStatus hgppiFloodFill8Way_8u_C1R_Ctx(...)
```

##### 8.7.2.3. Flood Fill （通用）
```c
HgppStatus hgppiFloodFill_8u_C1R_Ctx(...)
HgppStatus hgppiFloodFill_8u_C3R_Ctx(...)
HgppStatus hgppiFloodFill_32f_C1R_Ctx(...)
```

### 8.8. Label Markers （标记）
#### 8.8.1. 数学原理
**连通区域标记（Connected Component Labeling）**将二值图像中的连通像素区域标记为唯一标识符。

##### 8.8.1.1. Union-Find 算法原理
**数据结构：**

使用并查集（Union-Find）数据结构管理等价类：

$$
\text{parent}[i] = \begin{cases} i & \text{if } i \text{ is root} \\ \text{parent of } i & \text{otherwise} \end{cases}
$$

**Find 操作（查找根节点）：**

$$
\text{find}(i) = \begin{cases} i & \text{if } \text{parent}[i] = i \\ \text{find}(\text{parent}[i]) & \text{otherwise} \end{cases}
$$

**路径压缩优化：**

$$
\text{parent}[i] \leftarrow \text{find}(\text{parent}[i])
$$

**Union 操作（合并集合）：**

$$
\text{union}(i, j): \text{parent}[\text{find}(i)] \leftarrow \text{find}(j)
$$

**按秩合并优化：**

$$
\text{if } \text{rank}[i] < \text{rank}[j]: \text{parent}[i] \leftarrow j \\
\text{else if } \text{rank}[i] > \text{rank}[j]: \text{parent}[j] \leftarrow i \\
\text{else}: \text{parent}[j] \leftarrow i, \text{rank}[i] \leftarrow \text{rank}[i] + 1
$$

**时间复杂度：**
- 单次操作：$O(\alpha(n))$，其中 $\alpha$ 是反阿克曼函数（几乎为常数）
- 总复杂度：$O(n \cdot \alpha(n)) \approx O(n)$

##### 8.8.1.2. 连通性定义
**4 连通：**

像素 $(x, y)$ 的 4 邻域：

$$
N_4(x, y) = \{(x+1, y), (x-1, y), (x, y+1), (x, y-1)\}
$$

**8 连通：**

像素 $(x, y)$ 的 8 邻域：

$$
N_8(x, y) = N_4(x, y) \cup \{(x+1, y+1), (x+1, y-1), (x-1, y+1), (x-1, y-1)\}
$$

##### 8.8.1.3. 标记压缩
**稀疏标记问题：**

Union-Find 可能产生不连续的标记编号（稀疏）。

**压缩公式：**

$$
\text{new\_label}[i] = \begin{cases} 0 & \text{if } i = 0 \\ \text{new\_label}[\text{parent}[i-1]] + 1 & \text{if } \text{parent}[i] \neq \text{parent}[i-1] \\ \text{new\_label}[\text{parent}[i-1]] & \text{otherwise} \end{cases}
$$

#### 8.8.2. 1 Label Markers UF （Union-Find 标记）
```c
HgppStatus hgppiLabelMarkersUF_8u_32s_C1R_Ctx(...)
HgppStatus hgppiLabelMarkersUF_16u_32s_C1R_Ctx(...)
```

#### 8.8.3. 2 Compressed Label Markers UF （压缩标记）
```c
HgppStatus hgppiCompressedLabelMarkersUF_8u_32s_C1R_Ctx(...)
```

#### 8.8.4. 3 Label Markers Info （标记信息）
```c
HgppStatus hgppiCompressedMarkerLabelsUFInfo_32s_C1R_Ctx(...)
```

### 8.9. Bound Segments （边界段）
#### 8.9.1. Bound Segments
```c
HgppStatus hgppiBoundSegments_32s_C1R_Ctx(...)
```

#### 8.9.2. Contour Geometry （轮廓几何）

> **提示：**
> 轮廓几何函数用于提取和分析连通区域的轮廓信息。

```c
// Contour Pixel Geometry Info - 轮廓像素几何信息。
HgppStatus hgppiContourPixelGeometryInfo_32s_C1R_Ctx(const Hgpp32s *pSrc, int nSrcStep,
                                                      HgppiContourPixelGeometryInfo *pContoursDirectionImageDev,
                                                      int nContoursDirectionImageStep,
                                                      HgppiContourPixelGeometryInfo *pContoursPixelGeometryListsDev,
                                                      HgppiContourPixelGeometryInfo *pContoursPixelGeometryListsHost,
                                                      HgppiPoint32f *pContoursInterpolatedGeometryListsDev,
                                                      Hgpp32u *pContoursPixelsFoundListHost,
                                                      Hgpp32u *pContoursPixelsStartingOffsetDev,
                                                      Hgpp32u *pContoursPixelsStartingOffsetHost,
                                                      Hgpp32u nTotalImagePixelContourCount,
                                                      Hgpp32u nMaxMarkerLabelID,
                                                      Hgpp32u nFirstContourGeometryListID,
                                                      Hgpp32u nLastContourGeometryListID,
                                                      HgppiContourBlockSegment *pContoursBlockSegmentListDev,
                                                      HgppiContourBlockSegment *pContoursBlockSegmentListHost,
                                                      HgppiSize oSizeROI,
                                                      HgppStreamContext hgppStreamCtx)

// Contours Image Marching Squares Interpolation - 行进立方轮廓插值。
HgppStatus hgppiContoursImageMarchingSquaresInterpolation_32f_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                                                       Hgpp32f *pDst, int nDstStep,
                                                                       HgppiSize oSizeROI,
                                                                       Hgpp32f nThreshold,
                                                                       HgppStreamContext hgppStreamCtx)

HgppStatus hgppiContoursImageMarchingSquaresInterpolation_64f_C1R_Ctx(...)

// Compressed Marker Labels UF Info - 压缩标记信息。
HgppStatus hgppiCompressedMarkerLabelsUFInfo_32s_C1R_Ctx(const Hgpp32s *pSrc, int nSrcStep,
                                                          HgppiCompressedMarkerLabelsInfo *pMarkerLabelsInfo,
                                                          HgppiSize oSizeROI,
                                                          HgppStreamContext hgppStreamCtx)

// Compress Marker Labels UF - 压缩标记。
HgppStatus hgppiCompressMarkerLabelsUF_32s_C1IR_Ctx(Hgpp32s *pSrcDst, int nSrcDstStep,
                                                     HgppiSize oSizeROI,
                                                     HgppStreamContext hgppStreamCtx)
```

**轮廓几何结构体：**

```c
// 轮廓像素几何信息。
typedef struct {
    HgppiPoint oContourOrderedGeometryLocation;  // 有序几何位置。
    HgppiPoint oContourPrevPixelLocation;        // 上一个轮廓像素。
    HgppiPoint oContourCenterPixelLocation;      // 中心轮廓像素。
    HgppiPoint oContourNextPixelLocation;        // 下一个轮廓像素。
    Hgpp32s nOrderIndex;                          // 逆时针顺序索引。
    Hgpp32s nReverseOrderIndex;                   // 顺时针顺序索引。
    Hgpp32u nFirstIndex;                          // 子组第一个索引。
    Hgpp32u nLastIndex;                           // 子组最后一个索引。
    Hgpp32u nNextContourPixelIndex;               // 下一个轮廓像素索引。
    Hgpp32u nPrevContourPixelIndex;               // 上一个轮廓像素索引。
    HGpp8u nPixelAlreadyUsed;                     // 像素已使用标志。
    HGpp8u nAlreadyLinked;                        // 已链接标志。
    HGpp8u nAlreadyOutput;                        // 已输出标志。
    HGpp8u nContourInteriorDirection;             // 轮廓内部方向。
} HgppiContourPixelGeometryInfo;

// 压缩标记标签信息。
typedef struct {
    Hgpp32u nMarkerLabelPixelCount;        // 标记像素总数。
    Hgpp32u nContourPixelCount;            // 轮廓像素总数。
    Hgpp32u nContourPixelsFound;           // 找到的轮廓像素数。
    HgppiPoint oContourFirstPixelLocation; // 轮廓第一个像素位置。
    HgppiRect oMarkerLabelBoundingBox;     // 标记边界框。
} HgppiCompressedMarkerLabelsInfo;
```

### 8.10. Watershed Segmentation （分水岭分割）
#### 8.10.1. 数学原理
**分水岭分割（Watershed Segmentation）**是一种基于拓扑理论的形态学分割方法。

##### 8.10.1.1. 地形模型
**图像作为地形：**

将灰度图像 $I(x, y)$ 视为地形表面：

$$
z = I(x, y)
$$

其中 $z$ 是高度（灰度值）。

**局部最小值（集水盆地）：**

$$
(x_0, y_0) \text{ is local minimum} \iff \forall (x, y) \in N(x_0, y_0): I(x, y) \geq I(x_0, y_0)
$$

##### 8.10.1.2. 浸水过程
**水平面高度 $h$：**

对于高度 $h$，定义淹没区域：

$$
R(h) = \{(x, y) \mid I(x, y) < h\}
$$

**集水盆地：**

对于每个局部最小值 $m_i$，定义其集水盆地：

$$
B_i(h) = \{(x, y) \in R(h) \mid \text{water from } (x, y) \text{ flows to } m_i\}
$$

**分水岭（分割边界）：**

$$
W = \{(x, y) \mid (x, y) \notin \bigcup_i B_i(h) \text{ for any } h\}
$$

##### 8.10.1.3. 标记控制分水岭
**标记图像 $M(x, y)$：**

$$
M(x, y) = \begin{cases} i > 0 & \text{前景区域 } i \\ 0 & \text{不确定区域} \\ -i < 0 & \text{背景区域 } i \end{cases}
$$

**标记梯度：**

$$
G_M(x, y) = \begin{cases} 0 & \text{if } M(x, y) > 0 \\ |\nabla I(x, y)| & \text{otherwise} \end{cases}
$$

**分水岭变换：**

$$
\text{WS}(I, M) = \text{watershed transform of } I \text{ constrained by markers } M
$$

##### 8.10.1.4. 轮廓几何（Contour Geometry）
**Marching Squares 算法：**

用于提取等值线（轮廓）的算法。

**2×2 网格配置：**

对于 2×2 网格的 4 个顶点，每个顶点有两种状态（高于/低于阈值），共 $2^4 = 16$ 种配置。

**配置编码：**

$$
\text{config} = \sum_{i=0}^{3} b_i \cdot 2^i
$$

其中 $b_i = 1$ 如果顶点 $i$ 高于阈值，否则 $b_i = 0$。

**轮廓插值：**

对于边上的两个顶点 $(x_1, y_1, v_1)$ 和 $(x_2, y_2, v_2)$，等值点位置：

$$
t = \frac{T - v_1}{v_2 - v_1}
$$

$$
(x, y) = (x_1 + t(x_2 - x_1), y_1 + t(y_2 - y_1))
$$

其中 $T$ 是阈值。

##### 8.10.1.5. 轮廓像素几何信息
**轮廓像素方向：**

对于轮廓像素 $(x, y)$，定义 8 个方向：

$$
D = \{E, NE, N, NW, W, SW, S, SE\}
$$

**方向编码：**

$$
\text{direction}(x, y) = \arg\min_{d \in D} \text{distance to contour in direction } d
$$

**轮廓几何列表：**

$$
\text{ContourGeometry} = \{(x_i, y_i, \text{prev}_i, \text{next}_i, \text{order}_i) \mid i = 1, \ldots, n\}
$$

其中：
- $(x_i, y_i)$：轮廓像素坐标
- $\text{prev}_i$：上一个轮廓像素索引
- $\text{next}_i$：下一个轮廓像素索引
- $\text{order}_i$：逆时针顺序索引

##### 8.10.1.6. 压缩标记标签
**稀疏标记问题：**

Union-Find 产生的标记可能不连续。

**压缩映射：**

$$
f: \{0, 1, \ldots, N\} \to \{0, 1, \ldots, M\}, \quad M \leq N
$$

$$
f(i) = \begin{cases} 0 & \text{if } i = 0 \\ f(\text{parent}(i-1)) + 1 & \text{if } \text{parent}(i) \neq \text{parent}(i-1) \\ f(\text{parent}(i-1)) & \text{otherwise} \end{cases}
$$

**标记信息结构：**

$$
\text{MarkerInfo}_i = (\text{pixel\_count}_i, \text{contour\_count}_i, \text{bounding\_box}_i)
$$

#### 8.10.2. 1 Watershed Segmentation
```c
HgppStatus hgppiWatershedSegmentation_8u_C1R_Ctx(...)
HgppStatus hgppiWatershedSegmentation_16u_C1R_Ctx(...)
HgppStatus hgppiWatershedSegmentation_32f_C1R_Ctx(...)
```

#### 8.10.3. 2 Watershed Markers （分水岭标记）
```c
HgppStatus hgppiWatershedMarkerImage_32s_C1R_Ctx(...)
```

### 8.11. 错误码
| 错误码 | 说明 |
|--------|------|
| `HGPP_NULL_POINTER_ERROR` | 空指针 |
| `HGPP_STEP_ERROR` | 步幅错误 |
| `HGPP_SIZE_ERROR` | ROI 尺寸错误 |
| `HGPP_MASK_SIZE_ERROR` | 掩码尺寸错误 |
| `HGPP_ANCHOR_ERROR` | 锚点错误 |
| `HGPP_DIVISOR_ERROR` | 除数为零 |
| `HGPP_THRESHOLD_ERROR` | 阈值错误 |
| `HGPP_HISTOGRAM_NUMBER_OF_LEVELS_ERROR` | 直方图级别数 < 2 |
| `HGPP_ALIGNMENT_ERROR` | 对齐错误 |
| `HGPP_NOT_EVEN_STEP_ERROR` | 步幅不是像素倍数 |

## 9. 图像几何变换
这些函数位于 `hgppig` 库中。
同类函数没有全部列出，完整函数定义请参考头文件。

### 9.1. 几何变换特性
#### 9.1.1. ROI 处理
几何变换操作于源和目标 ROI。**仅处理变换后的源 ROI 与目标 ROI 交集内的像素**。

**处理流程：**
1. 将矩形源 ROI 变换到目标图像空间，得到四边形
2. 仅写入变换后的源 ROI 与目标 ROI 交集内的像素。

#### 9.1.2. 像素插值模式
| 模式 | 速度 | 质量 | 说明 |
|------|------|------|------|
| `HGPP_INTER_NN` | 最快 | 最低 | 最近邻插值 |
| `HGPP_INTER_LINEAR` | 快 | 中 | 线性插值 |
| `HGPP_INTER_CUBIC` | 中 | 高 | 立方卷积插值 |
| `HGPP_INTER_CUBIC2P_BSPLINE` | 中 | 高 | 双参数立方滤波 (B=1, C=0) |
| `HGPP_INTER_CUBIC2P_CATMULLROM` | 中 | 高 | 双参数立方滤波 (B=0, C=1/2) |
| `HGPP_INTER_CUBIC2P_B05C03` | 中 | 高 | 双参数立方滤波 (B=1/2, C=3/10) |
| `HGPP_INTER_SUPER` | 慢 | 很高 | 超采样插值 |
| `HGPP_INTER_LANCZOS` | 最慢 | 最高 | Lanczos 窗口函数插值 |

> **注意：**
> - ResizeSqrPixel 支持所有插值模式。
> - Remap 不支持 `HGPP_INTER_SUPER`
> - 超采样仅适用于缩小操作（downscaling）。

#### 9.1.3. 通用错误码
| 错误码 | 说明 |
|--------|------|
| `HGPP_WRONG_INTERSECTION_ROI_ERROR` | srcROIRect 与源图像无交集 |
| `HGPP_RESIZE_NO_OPERATION_ERROR` | 目标 ROI 宽度或高度 < 1 像素 |
| `HGPP_RESIZE_FACTOR_ERROR` | nXFactor 或 nYFactor ≤ 0，或超采样模式下不是双缩小 |
| `HGPP_INTERPOLATION_ERROR` | eInterpolation 值非法 |
| `HGPP_SIZE_ERROR` | 源尺寸宽度或高度 < 2 像素 |
| `HGPP_RECTANGLE_ERROR` | ROI 与源图像交集的宽度或高度 ≤ 1 |
| `HGPP_WRONG_INTERSECTION_QUAD_WARNING` | 变换后的源 ROI 与目标 ROI 无交集（警告） |
| `HGPP_COEFFICIENT_ERROR` | 变换系数无效 |
| `HGPP_MIRROR_FLIP_ERROR` | flip 轴值非法 |
| `HGPP_AFFINE_QUAD_INCORRECT_WARNING` | 四边形不符合变换属性（仿射变换警告） |

### 9.2. Resize 缩放
#### 9.2.1. 功能介绍
Resize 函数调整图像尺寸，支持放大和缩小操作。使用缩放公式选择源像素进行插值。

> **注意：**
> - ResizeSqrPixel 使用缩放公式选择源像素，近似表示目标像素中心。
> - 源像素分数坐标必须在源 ROI 范围内才会被采样。

#### 9.2.2. 完整参数说明
##### 9.2.2.1. ResizeSqrPixel 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | **源图像指针** - Packet 格式图像 |
| `pSrc[]` | 主机指针数组 | [in] | **源图像指针数组** - 平面格式（planar）图像，每个元素指向一个通道平面 |
| `oSrcSize` | HgppiSize | [in] | **源图像尺寸** - 源图像的宽度和高度（像素） |
| `nSrcStep` | int | [in] | **源图像行步幅**（字节），必须 ≥ 0 |
| `oSrcROI` | HgppiRect | [in] | **源 ROI** - 源图像中的感兴趣区域（x, y, width, height） |
| `pDst` | 设备指针 | [out] | **目标图像指针** - Packet 格式 |
| `pDst[]` | 主机指针数组 | [out] | **目标图像指针数组** - Planar 格式 |
| `nDstStep` | int | [in] | **目标图像行步幅**（字节） |
| `oDstROI` | HgppiRect | [in] | **目标 ROI** - 目标图像中的感兴趣区域 |
| `nXFactor` | double | [in] | **X 方向缩放因子** - 必须 > 0，> 1 表示放大，< 1 表示缩小 |
| `nYFactor` | double | [in] | **Y 方向缩放因子** - 必须 > 0 |
| `nXShift` | double | [in] | **X 方向源像素偏移** - 用于微调采样位置 |
| `nYShift` | double | [in] | **Y 方向源像素偏移** |
| `eInterpolation` | int | [in] | **插值模式** - 见上方插值模式表 |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

**缩放公式：**

$$
\begin{aligned}
nAdjustedXFactor &= 1.0 / nXFactor \\
nAdjustedYFactor &= 1.0 / nYFactor \\
nAdjustedXShift &= nXShift \times nAdjustedXFactor + ((1.0 - nAdjustedXFactor) \times 0.5) \\
nAdjustedYShift &= nYShift \times nAdjustedYFactor + ((1.0 - nAdjustedYFactor) \times 0.5) \\
nSrcX &= nAdjustedXFactor \times nDstX - nAdjustedXShift \\
nSrcY &= nAdjustedYFactor \times nDstY - nAdjustedYShift
\end{aligned}
$$

**返回值：** `HgppStatus` - 图像数据相关错误码、 ROI 相关错误码、 Resize 错误码

##### 9.2.2.2. GetResizeRect 工具函数
```c
HgppStatus hgppiGetResizeRect(HgppiRect oSrcROI, HgppiRect *pDstRect, 
                               double nXFactor, double nYFactor, 
                               double nXShift, double nYShift, 
                               int eInterpolation)
```

**参数说明：**

| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `oSrcROI` | HgppiRect | [in] | **源 ROI** - 源图像中的感兴趣区域 |
| `pDstRect` | HgppiRect 指针 | [out] | **目标矩形** - 用户提供的宿主内存指针，将被填充为目标 ROI 的偏移和尺寸 |
| `nXFactor` | double | [in] | **X 方向缩放因子** |
| `nYFactor` | double | [in] | **Y 方向缩放因子** |
| `nXShift` | double | [in] | **X 方向源像素偏移** |
| `nYShift` | double | [in] | **Y 方向源像素偏移** |
| `eInterpolation` | int | [in] | **插值模式** |

**功能说明：** 返回由源 ROI 按指定缩放因子和偏移调整后生成的目标矩形的偏移和尺寸。

#### 9.2.3. 函数列表
##### 9.2.3.1. ResizeSqrPixel （Packet 格式）
**8 位无符号整数**

```c
// 单通道。
HgppStatus hgppiResizeSqrPixel_8u_C1R_Ctx(const HGpp8u *pSrc, HgppiSize oSrcSize, int nSrcStep,
                                           HgppiRect oSrcROI, HGpp8u *pDst, int nDstStep,
                                           HgppiRect oDstROI, double nXFactor, double nYFactor,
                                           double nXShift, double nYShift, int eInterpolation,
                                           HgppStreamContext hgppStreamCtx)

// 三通道。
HgppStatus hgppiResizeSqrPixel_8u_C3R_Ctx(const HGpp8u *pSrc, HgppiSize oSrcSize, int nSrcStep,
                                           HgppiRect oSrcROI, HGpp8u *pDst, int nDstStep,
                                           HgppiRect oDstROI, double nXFactor, double nYFactor,
                                           double nXShift, double nYShift, int eInterpolation,
                                           HgppStreamContext hgppStreamCtx)

// 四通道。
HgppStatus hgppiResizeSqrPixel_8u_C4R_Ctx(const HGpp8u *pSrc, HgppiSize oSrcSize, int nSrcStep,
                                           HgppiRect oSrcROI, HGpp8u *pDst, int nDstStep,
                                           HgppiRect oDstROI, double nXFactor, double nYFactor,
                                           double nXShift, double nYShift, int eInterpolation,
                                           HgppStreamContext hgppStreamCtx)

// 四通道（不影响 Alpha）
HgppStatus hgppiResizeSqrPixel_8u_AC4R_Ctx(const HGpp8u *pSrc, HgppiSize oSrcSize, int nSrcStep,
                                            HgppiRect oSrcROI, HGpp8u *pDst, int nDstStep,
                                            HgppiRect oDstROI, double nXFactor, double nYFactor,
                                            double nXShift, double nYShift, int eInterpolation,
                                            HgppStreamContext hgppStreamCtx)
```

**16 位无符号/有符号整数**

```c
// 16 位无符号。
HgppStatus hgppiResizeSqrPixel_16u_C1R_Ctx(...)
HgppStatus hgppiResizeSqrPixel_16u_C3R_Ctx(...)
HgppStatus hgppiResizeSqrPixel_16u_C4R_Ctx(...)
HgppStatus hgppiResizeSqrPixel_16u_AC4R_Ctx(...)

// 16 位有符号。
HgppStatus hgppiResizeSqrPixel_16s_C1R_Ctx(...)
HgppStatus hgppiResizeSqrPixel_16s_C3R_Ctx(...)
HgppStatus hgppiResizeSqrPixel_16s_C4R_Ctx(...)
HgppStatus hgppiResizeSqrPixel_16s_AC4R_Ctx(...)
```

**32 位浮点数**

```c
HgppStatus hgppiResizeSqrPixel_32f_C1R_Ctx(...)
HgppStatus hgppiResizeSqrPixel_32f_C3R_Ctx(...)
HgppStatus hgppiResizeSqrPixel_32f_C4R_Ctx(...)
HgppStatus hgppiResizeSqrPixel_32f_AC4R_Ctx(...)
```

##### 9.2.3.2. ResizeSqrPixel （Planar 格式）
```c
// 8 位无符号三通道Planar格式。
HgppStatus hgppiResizeSqrPixel_8u_P3R_Ctx(const HGpp8u *const pSrc[3], HgppiSize oSrcSize, int nSrcStep,
                                           HgppiRect oSrcROI, HGpp8u *pDst[3], int nDstStep,
                                           HgppiRect oDstROI, double nXFactor, double nYFactor,
                                           double nXShift, double nYShift, int eInterpolation,
                                           HgppStreamContext hgppStreamCtx)

// 8 位无符号四通道Planar格式。
HgppStatus hgppiResizeSqrPixel_8u_P4R_Ctx(const HGpp8u *const pSrc[4], HgppiSize oSrcSize, int nSrcStep,
                                           HgppiRect oSrcROI, HGpp8u *pDst[4], int nDstStep,
                                           HgppiRect oDstROI, double nXFactor, double nYFactor,
                                           double nXShift, double nYShift, int eInterpolation,
                                           HgppStreamContext hgppStreamCtx)

// 16 位/32 位Planar格式。
HgppStatus hgppiResizeSqrPixel_16u_P3R_Ctx(...)
HgppStatus hgppiResizeSqrPixel_16u_P4R_Ctx(...)
HgppStatus hgppiResizeSqrPixel_16s_P3R_Ctx(...)
HgppStatus hgppiResizeSqrPixel_16s_P4R_Ctx(...)
HgppStatus hgppiResizeSqrPixel_32f_P3R_Ctx(...)
HgppStatus hgppiResizeSqrPixel_32f_P4R_Ctx(...)
```

##### 9.2.3.3. GetResizeRect 工具函数
```c
HgppStatus hgppiGetResizeRect(HgppiRect oSrcROI, HgppiRect *pDstRect, 
                               double nXFactor, double nYFactor, 
                               double nXShift, double nYShift, 
                               int eInterpolation)
// 计算缩放后的目标矩形偏移和尺寸。
```

### 9.3. Remap 重映射
#### 9.3.1. 功能介绍
Remap 函数使用显式提供的 2D 设备内存图像数组（pXMap 和 pYMap）中的像素坐标进行重映射。 pXMap 数组包含 X 坐标， pYMap 数组包含 Y 坐标，用于选择对应的源图像像素。这些坐标是浮点格式，因此可以使用分数像素位置。

> **注意：**
> - Remap 不支持 `HGPP_INTER_SUPER`（超采样）插值模式。
> - 源像素分数坐标必须在源 ROI 范围内才会被采样。

#### 9.3.2. 完整参数说明
##### 9.3.2.1. Remap 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | **源图像指针** - Packet 格式 |
| `pSrc[]` | 主机指针数组 | [in] | **源图像指针数组** - Planar 格式 |
| `oSrcSize` | HgppiSize | [in] | **源图像尺寸**（像素） |
| `nSrcStep` | int | [in] | **源图像行步幅** |
| `oSrcROI` | HgppiRect | [in] | **源 ROI** |
| `pXMap` | 设备指针 | [in] | **X 坐标映射表** - 32 位浮点 2D 图像数组，包含采样源图像时使用的 X 坐标值 |
| `nXMapStep` | int | [in] | **pXMap 行步幅**（字节） |
| `pYMap` | 设备指针 | [in] | **Y 坐标映射表** - 32 位浮点 2D 图像数组，包含采样源图像时使用的 Y 坐标值 |
| `nYMapStep` | int | [in] | **pYMap 行步幅**（字节） |
| `pDst` | 设备指针 | [out] | **目标图像指针** - Packet 格式 |
| `pDst[]` | 主机指针数组 | [out] | **目标图像指针数组** - Planar 格式 |
| `nDstStep` | int | [in] | **目标图像行步幅** |
| `oDstSizeROI` | HgppiSize | [in] | **目标 ROI 尺寸** - 目标图像中的感兴趣区域尺寸 |
| `eInterpolation` | int | [in] | **插值模式** - NN/LINEAR/CUBIC/LANCZOS 等（不支持 SUPER） |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

**坐标选择公式：**

$$
\begin{aligned}
nSrcX &= pXMap[nDstX, nDstY] \\
nSrcY &= pYMap[nDstX, nDstY]
\end{aligned}
$$

**返回值：** `HgppStatus` - 图像数据相关错误码、 ROI 相关错误码

#### 9.3.3. 函数列表
##### 9.3.3.1. Remap （Packet 格式）
**8 位无符号整数**

```c
// 单通道。
HgppStatus hgppiRemap_8u_C1R_Ctx(const HGpp8u *pSrc, HgppiSize oSrcSize, int nSrcStep,
                                  HgppiRect oSrcROI, const Hgpp32f *pXMap, int nXMapStep,
                                  const Hgpp32f *pYMap, int nYMapStep,
                                  HGpp8u *pDst, int nDstStep, HgppiSize oDstSizeROI,
                                  int eInterpolation, HgppStreamContext hgppStreamCtx)

// 三通道。
HgppStatus hgppiRemap_8u_C3R_Ctx(const HGpp8u *pSrc, HgppiSize oSrcSize, int nSrcStep,
                                  HgppiRect oSrcROI, const Hgpp32f *pXMap, int nXMapStep,
                                  const Hgpp32f *pYMap, int nYMapStep,
                                  HGpp8u *pDst, int nDstStep, HgppiSize oDstSizeROI,
                                  int eInterpolation, HgppStreamContext hgppStreamCtx)

// 四通道。
HgppStatus hgppiRemap_8u_C4R_Ctx(...)

// 四通道（不影响 Alpha）
HgppStatus hgppiRemap_8u_AC4R_Ctx(...)
```

**16 位无符号/有符号**

```c
HgppStatus hgppiRemap_16u_C1R_Ctx(...)
HgppStatus hgppiRemap_16u_C3R_Ctx(...)
HgppStatus hgppiRemap_16u_C4R_Ctx(...)
HgppStatus hgppiRemap_16u_AC4R_Ctx(...)

HgppStatus hgppiRemap_16s_C1R_Ctx(...)
HgppStatus hgppiRemap_16s_C3R_Ctx(...)
HgppStatus hgppiRemap_16s_C4R_Ctx(...)
HgppStatus hgppiRemap_16s_AC4R_Ctx(...)
```

**32 位/64 位浮点数**

```c
HgppStatus hgppiRemap_32f_C1R_Ctx(...)
HgppStatus hgppiRemap_32f_C3R_Ctx(...)
HgppStatus hgppiRemap_32f_C4R_Ctx(...)
HgppStatus hgppiRemap_32f_AC4R_Ctx(...)

HgppStatus hgppiRemap_64f_C1R_Ctx(...)
HgppStatus hgppiRemap_64f_C3R_Ctx(...)
HgppStatus hgppiRemap_64f_C4R_Ctx(...)
HgppStatus hgppiRemap_64f_AC4R_Ctx(...)
```

##### 9.3.3.2. Remap （Planar 格式）
```c
// 8 位无符号三通道Planar格式。
HgppStatus hgppiRemap_8u_P3R_Ctx(const HGpp8u *const pSrc[3], HgppiSize oSrcSize, int nSrcStep,
                                  HgppiRect oSrcROI, const Hgpp32f *pXMap, int nXMapStep,
                                  const Hgpp32f *pYMap, int nYMapStep,
                                  HGpp8u *pDst[3], int nDstStep, HgppiSize oDstSizeROI,
                                  int eInterpolation, HgppStreamContext hgppStreamCtx)

// 8 位无符号四通道Planar格式。
HgppStatus hgppiRemap_8u_P4R_Ctx(const HGpp8u *const pSrc[4], HgppiSize oSrcSize, int nSrcStep,
                                  HgppiRect oSrcROI, const Hgpp32f *pXMap, int nXMapStep,
                                  const Hgpp32f *pYMap, int nYMapStep,
                                  HGpp8u *pDst[4], int nDstStep, HgppiSize oDstSizeROI,
                                  int eInterpolation, HgppStreamContext hgppStreamCtx)

// 16 位/32 位/64 位Planar格式。
HgppStatus hgppiRemap_16u_P3R_Ctx(...)
HgppStatus hgppiRemap_16u_P4R_Ctx(...)
HgppStatus hgppiRemap_16s_P3R_Ctx(...)
HgppStatus hgppiRemap_16s_P4R_Ctx(...)
HgppStatus hgppiRemap_32f_P3R_Ctx(...)
HgppStatus hgppiRemap_32f_P4R_Ctx(...)
HgppStatus hgppiRemap_64f_P3R_Ctx(...)
HgppStatus hgppiRemap_64f_P4R_Ctx(...)
```

### 9.4. Rotate 旋转
#### 9.4.1. 功能介绍
Rotate 函数将图像绕原点 (0,0) 旋转指定角度，然后进行平移。

#### 9.4.2. 完整参数说明
##### 9.4.2.1. Rotate 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | **源图像指针** |
| `oSrcSize` | HgppiSize | [in] | **源图像尺寸**（像素） |
| `nSrcStep` | int | [in] | **源图像行步幅** |
| `oSrcROI` | HgppiRect | [in] | **源 ROI** |
| `pDst` | 设备指针 | [out] | **目标图像指针** |
| `nDstStep` | int | [in] | **目标图像行步幅** |
| `oDstROI` | HgppiRect | [in] | **目标 ROI** |
| `nAngle` | double | [in] | **旋转角度**（度）- 正值表示逆时针旋转 |
| `nShiftX` | double | [in] | **X 方向平移** - 旋转后的水平平移量 |
| `nShiftY` | double | [in] | **Y 方向平移** - 旋转后的垂直平移量 |
| `eInterpolation` | int | [in] | **插值模式** |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

**返回值：** `HgppStatus` - 图像数据相关错误码、 ROI 相关错误码、 Rotate 错误码

##### 9.4.2.2. Rotate 工具函数
**GetRotateQuad**

```c
HgppStatus hgppiGetRotateQuad(HgppiRect oSrcROI, double aQuad[4][2], 
                               double nAngle, double nShiftX, double nShiftY)
```

| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `oSrcROI` | HgppiRect | [in] | **源 ROI** |
| `aQuad` | double[4][2] | [out] | **旋转后四边形** - 2D 点数组，包含旋转 ROI 的四个角点位置 |
| `nAngle` | double | [in] | **旋转角度** |
| `nShiftX` | double | [in] | **旋转后 X 方向平移** |
| `nShiftY` | double | [in] | **旋转后 Y 方向平移** |

**功能说明：** 计算旋转图像的形状（四边形角点）。

**GetRotateBound**

```c
HgppStatus hgppiGetRotateBound(HgppiRect oSrcROI, double aBoundingBox[2][2], 
                                double nAngle, double nShiftX, double nShiftY)
```

| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `oSrcROI` | HgppiRect | [in] | **源 ROI** |
| `aBoundingBox` | double[2][2] | [out] | **包围盒** - 两个 2D 点，表示旋转图像的轴对齐包围盒 |
| `nAngle` | double | [in] | **旋转角度** |
| `nShiftX` | double | [in] | **旋转后 X 方向平移** |
| `nShiftY` | double | [in] | **旋转后 Y 方向平移** |

**功能说明：** 计算旋转图像的包围盒（轴对齐矩形）。`hgppiGetRotateQuad` 的所有四个角点都包含在这两个点张成的轴对齐矩形内。

#### 9.4.3. 函数列表
##### 9.4.3.1. Rotate
**8 位无符号整数**

```c
// 单通道。
HgppStatus hgppiRotate_8u_C1R_Ctx(const HGpp8u *pSrc, HgppiSize oSrcSize, int nSrcStep,
                                   HgppiRect oSrcROI, HGpp8u *pDst, int nDstStep,
                                   HgppiRect oDstROI, double nAngle, double nShiftX, double nShiftY,
                                   int eInterpolation, HgppStreamContext hgppStreamCtx)

// 三通道。
HgppStatus hgppiRotate_8u_C3R_Ctx(const HGpp8u *pSrc, HgppiSize oSrcSize, int nSrcStep,
                                   HgppiRect oSrcROI, HGpp8u *pDst, int nDstStep,
                                   HgppiRect oDstROI, double nAngle, double nShiftX, double nShiftY,
                                   int eInterpolation, HgppStreamContext hgppStreamCtx)

// 四通道。
HgppStatus hgppiRotate_8u_C4R_Ctx(...)

// 四通道（忽略 Alpha）
HgppStatus hgppiRotate_8u_AC4R_Ctx(...)
```

**16 位无符号/32 位浮点**

```c
HgppStatus hgppiRotate_16u_C1R_Ctx(...)
HgppStatus hgppiRotate_16u_C3R_Ctx(...)
HgppStatus hgppiRotate_16u_C4R_Ctx(...)
HgppStatus hgppiRotate_16u_AC4R_Ctx(...)

HgppStatus hgppiRotate_32f_C1R_Ctx(...)
HgppStatus hgppiRotate_32f_C3R_Ctx(...)
HgppStatus hgppiRotate_32f_C4R_Ctx(...)
HgppStatus hgppiRotate_32f_AC4R_Ctx(...)
```

##### 9.4.3.2. Rotate 工具函数
```c
// 计算旋转后四边形角点。
HgppStatus hgppiGetRotateQuad(HgppiRect oSrcROI, double aQuad[4][2], 
                               double nAngle, double nShiftX, double nShiftY)

// 计算旋转后包围盒。
HgppStatus hgppiGetRotateBound(HgppiRect oSrcROI, double aBoundingBox[2][2], 
                                double nAngle, double nShiftX, double nShiftY)
```

### 9.5. Mirror 镜像
#### 9.5.1. 功能介绍
Mirror 函数将图像沿水平轴、垂直轴或对角线进行镜像翻转。

#### 9.5.2. 完整参数说明
##### 9.5.2.1. Mirror 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | **源图像指针** |
| `nSrcStep` | int | [in] | **源图像行步幅** |
| `pDst` | 设备指针 | [out] | **目标图像指针** |
| `nDstStep` | int | [in] | **目标图像行步幅** |
| `pSrcDst` | 设备指针 | [in,out] | **图像指针** |
| `nSrcDstStep` | int | [in] | **图像行步幅** |
| `oROI` | HgppiSize | [in] | **ROI** - 感兴趣区域尺寸（**原图像操作时宽度和高度必须是偶数**） |
| `flip` | HgppiAxis | [in] | **镜像轴** - 指定图像绕哪个轴镜像（见下表） |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

**Mirror 轴选项：**

| 值 | 说明 | 效果 |
|------|------|------|
| `HGPP_HORIZONTAL_AXIS` | 水平轴 | 上下翻转 |
| `HGPP_VERTICAL_AXIS` | 垂直轴 | 左右翻转 |
| `HGPP_BOTH_AXIS` | 双轴 | 对角线翻转（水平 + 垂直） |

> **注意：**
> - **原图像操作（In-place）时， ROI 宽度和高度必须是偶数**，否则返回 `HGPP_SIZE_ERROR`。
>
> **返回值：** `HgppStatus` - 图像数据相关错误码、 ROI 相关错误码、 Mirror 错误码

#### 9.5.3. 函数列表
##### 9.5.3.1. Mirror
**8 位无符号整数**

```c
// 单通道。
HgppStatus hgppiMirror_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep,
                                   HgppiSize oROI, HgppiAxis flip, HgppStreamContext hgppStreamCtx)

// 三通道。
HgppStatus hgppiMirror_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pDst, int nDstStep,
                                   HgppiSize oROI, HgppiAxis flip, HgppStreamContext hgppStreamCtx)

// 四通道。
HgppStatus hgppiMirror_8u_C4R_Ctx(...)

// 四通道（不影响 Alpha）
HgppStatus hgppiMirror_8u_AC4R_Ctx(...)
```

##### 9.5.3.2. Mirror （原图像操作）
```c
// 单通道。
HgppStatus hgppiMirror_8u_C1IR_Ctx(HGpp8u *pSrcDst, int nSrcDstStep,
                                    HgppiSize oROI, HgppiAxis flip,
                                    HgppStreamContext hgppStreamCtx)

// 三通道。
HgppStatus hgppiMirror_8u_C3IR_Ctx(HGpp8u *pSrcDst, int nSrcDstStep,
                                    HgppiSize oROI, HgppiAxis flip,
                                    HgppStreamContext hgppStreamCtx)

// 四通道。
HgppStatus hgppiMirror_8u_C4IR_Ctx(...)

// 四通道（不影响 Alpha）
HgppStatus hgppiMirror_8u_AC4IR_Ctx(...)
```

**16 位/32 位**

```c
// 16 位无符号。
HgppStatus hgppiMirror_16u_C1R_Ctx(...)
HgppStatus hgppiMirror_16u_C1IR_Ctx(...)
HgppStatus hgppiMirror_16u_C3R_Ctx(...)
HgppStatus hgppiMirror_16u_C3IR_Ctx(...)
HgppStatus hgppiMirror_16u_C4R_Ctx(...)
HgppStatus hgppiMirror_16u_C4IR_Ctx(...)
HgppStatus hgppiMirror_16u_AC4R_Ctx(...)
HgppStatus hgppiMirror_16u_AC4IR_Ctx(...)

// 16 位有符号。
HgppStatus hgppiMirror_16s_C1R_Ctx(...)
HgppStatus hgppiMirror_16s_C1IR_Ctx(...)
HgppStatus hgppiMirror_16s_C3R_Ctx(...)
HgppStatus hgppiMirror_16s_C3IR_Ctx(...)
HgppStatus hgppiMirror_16s_C4R_Ctx(...)
HgppStatus hgppiMirror_16s_C4IR_Ctx(...)
HgppStatus hgppiMirror_16s_AC4R_Ctx(...)
HgppStatus hgppiMirror_16s_AC4IR_Ctx(...)

// 32 位有符号。
HgppStatus hgppiMirror_32s_C1R_Ctx(...)
HgppStatus hgppiMirror_32s_C1IR_Ctx(...)
HgppStatus hgppiMirror_32s_C3R_Ctx(...)
HgppStatus hgppiMirror_32s_C3IR_Ctx(...)
HgppStatus hgppiMirror_32s_C4R_Ctx(...)
HgppStatus hgppiMirror_32s_C4IR_Ctx(...)
HgppStatus hgppiMirror_32s_AC4R_Ctx(...)
HgppStatus hgppiMirror_32s_AC4IR_Ctx(...)

// 32 位浮点。
HgppStatus hgppiMirror_32f_C1R_Ctx(...)
HgppStatus hgppiMirror_32f_C1IR_Ctx(...)
HgppStatus hgppiMirror_32f_C3R_Ctx(...)
HgppStatus hgppiMirror_32f_C3IR_Ctx(...)
HgppStatus hgppiMirror_32f_C4R_Ctx(...)
HgppStatus hgppiMirror_32f_C4IR_Ctx(...)
HgppStatus hgppiMirror_32f_AC4R_Ctx(...)
HgppStatus hgppiMirror_32f_AC4IR_Ctx(...)
```

### 9.6. 仿射变换
#### 9.6.1. 功能介绍
仿射变换函数基于仿射变换矩阵对图像进行变换（变形）。仿射变换可以理解为线性变换（传统矩阵乘法）和平移操作的组合。

**仿射变换矩阵：**

仿射变换由 2×3 矩阵 C 给出。源图像中的像素位置 (x, y) 映射到目标图像中的位置 (x', y')。目标图像坐标计算如下：

$$
\begin{aligned}
x' &= c_{00} \times x + c_{01} \times y + c_{02} \\
y' &= c_{10} \times x + c_{11} \times y + c_{12}
\end{aligned}
$$

$$
C = \begin{bmatrix} c_{00} & c_{01} & c_{02} \\ c_{10} & c_{11} & c_{12} \end{bmatrix}
$$

**线性变换部分：**
$$
L = \begin{bmatrix} c_{00} & c_{01} \\ c_{10} & c_{11} \end{bmatrix}
$$

**平移向量：**
$$
v = \begin{bmatrix} c_{02} \\ c_{12} \end{bmatrix}
$$

> **注意：**
> - 仿射变换仅支持 NN、 LINEAR、 CUBIC 三种插值模式。
> - 系数无效时返回 `HGPP_COEFFICIENT_ERROR`。
> - 四边形不符合变换属性时返回警告 `HGPP_AFFINE_QUAD_INCORRECT_WARNING`。

#### 9.6.2. 完整参数说明
##### 9.6.2.1. WarpAffine 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | **源图像指针** - Packet 格式 |
| `pSrc[]` | 主机指针数组 | [in] | **源图像指针数组** - Planar 格式 |
| `oSrcSize` | HgppiSize | [in] | **源图像尺寸**（像素） |
| `nSrcStep` | int | [in] | **源图像行步幅** |
| `oSrcROI` | HgppiRect | [in] | **源 ROI** |
| `pDst` | 设备指针 | [out] | **目标图像指针** - Packet 格式 |
| `pDst[]` | 主机指针数组 | [out] | **目标图像指针数组** - Planar 格式 |
| `nDstStep` | int | [in] | **目标图像行步幅** |
| `oDstROI` | HgppiRect | [in] | **目标 ROI** |
| `aCoeffs` | double[2][3] | [in] | **仿射变换系数** - 2×3 仿射变换矩阵 |
| `eInterpolation` | int | [in] | **插值模式** - NN/LINEAR/CUBIC |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

**返回值：** `HgppStatus` - 图像数据相关错误码、 ROI 相关错误码、仿射变换错误码

##### 9.6.2.2. 仿射变换工具函数
**GetAffineTransform**

```c
HgppStatus hgppiGetAffineTransform(HgppiRect oSrcROI, const double aQuad[4][2], double aCoeffs[2][3])
```

| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `oSrcROI` | HgppiRect | [in] | **源 ROI** - 需要有至少 1 像素宽度和高度 |
| `aQuad` | const double[4][2] | [in] | **目标四边形** - 四个目标角点坐标 |
| `aCoeffs` | double[2][3] | [out] | **仿射变换系数** - 计算得到的 2×3 仿射变换矩阵 |

**功能说明：** 基于源 ROI 和目标四边形计算仿射变换系数。仿射变换在 2D 中由三个顶点的映射完全确定。此函数仅使用前三个顶点确定系数，如果目标四边形无法用仿射变换映射，返回警告。

**GetAffineQuad**

```c
HgppStatus hgppiGetAffineQuad(HgppiRect oSrcROI, double aQuad[4][2], const double aCoeffs[2][3])
```

| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `oSrcROI` | HgppiRect | [in] | **源 ROI** |
| `aQuad` | double[4][2] | [out] | **目标四边形** - 源 ROI 经仿射变换后在目标图像中的四边形位置 |
| `aCoeffs` | const double[2][3] | [in] | **仿射变换系数** |

**功能说明：** 计算源 ROI 经仿射变换后在目标图像中形成的四边形。

**GetAffineBound**

```c
HgppStatus hgppiGetAffineBound(HgppiRect oSrcROI, double aBound[2][2], const double aCoeffs[2][3])
```

| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `oSrcROI` | HgppiRect | [in] | **源 ROI** |
| `aBound` | double[2][2] | [out] | **包围盒** - 变换后源 ROI 的轴对齐包围盒 |
| `aCoeffs` | const double[2][3] | [in] | **仿射变换系数** |

**功能说明：** 计算变换后源 ROI 的包围盒（轴对齐矩形）。

#### 9.6.3. 函数列表
##### 9.6.3.1. WarpAffine （Packet 格式）
**8 位无符号整数**

```c
// 单通道。
HgppStatus hgppiWarpAffine_8u_C1R_Ctx(const HGpp8u *pSrc, HgppiSize oSrcSize, int nSrcStep,
                                       HgppiRect oSrcROI, HGpp8u *pDst, int nDstStep,
                                       HgppiRect oDstROI, const double aCoeffs[2][3],
                                       int eInterpolation, HgppStreamContext hgppStreamCtx)

// 三通道。
HgppStatus hgppiWarpAffine_8u_C3R_Ctx(const HGpp8u *pSrc, HgppiSize oSrcSize, int nSrcStep,
                                       HgppiRect oSrcROI, HGpp8u *pDst, int nDstStep,
                                       HgppiRect oDstROI, const double aCoeffs[2][3],
                                       int eInterpolation, HgppStreamContext hgppStreamCtx)

// 四通道。
HgppStatus hgppiWarpAffine_8u_C4R_Ctx(...)

// 四通道（忽略 Alpha）
HgppStatus hgppiWarpAffine_8u_AC4R_Ctx(...)
```

**16 位/32 位/64 位**

```c
// 16 位无符号。
HgppStatus hgppiWarpAffine_16u_C1R_Ctx(...)
HgppStatus hgppiWarpAffine_16u_C3R_Ctx(...)
HgppStatus hgppiWarpAffine_16u_C4R_Ctx(...)
HgppStatus hgppiWarpAffine_16u_AC4R_Ctx(...)

// 32 位有符号。
HgppStatus hgppiWarpAffine_32s_C1R_Ctx(...)
HgppStatus hgppiWarpAffine_32s_C3R_Ctx(...)
HgppStatus hgppiWarpAffine_32s_C4R_Ctx(...)
HgppStatus hgppiWarpAffine_32s_AC4R_Ctx(...)

// 32 位浮点。
HgppStatus hgppiWarpAffine_32f_C1R_Ctx(...)
HgppStatus hgppiWarpAffine_32f_C3R_Ctx(...)
HgppStatus hgppiWarpAffine_32f_C4R_Ctx(...)
HgppStatus hgppiWarpAffine_32f_AC4R_Ctx(...)

// 64 位浮点。
HgppStatus hgppiWarpAffine_64f_C1R_Ctx(...)
HgppStatus hgppiWarpAffine_64f_C3R_Ctx(...)
HgppStatus hgppiWarpAffine_64f_C4R_Ctx(...)
HgppStatus hgppiWarpAffine_64f_AC4R_Ctx(...)
```

##### 9.6.3.2. WarpAffine （Planar 格式）
```c
// 8 位无符号三通道Planar格式。
HgppStatus hgppiWarpAffine_8u_P3R_Ctx(const HGpp8u *pSrc[3], HgppiSize oSrcSize, int nSrcStep,
                                       HgppiRect oSrcROI, HGpp8u *pDst[3], int nDstStep,
                                       HgppiRect oDstROI, const double aCoeffs[2][3],
                                       int eInterpolation, HgppStreamContext hgppStreamCtx)

// 8 位无符号四通道Planar格式。
HgppStatus hgppiWarpAffine_8u_P4R_Ctx(const HGpp8u *pSrc[4], HgppiSize oSrcSize, int nSrcStep,
                                       HgppiRect oSrcROI, HGpp8u *pDst[4], int nDstStep,
                                       HgppiRect oDstROI, const double aCoeffs[2][3],
                                       int eInterpolation, HgppStreamContext hgppStreamCtx)

// 16 位/32 位/64 位Planar格式。
HgppStatus hgppiWarpAffine_16u_P3R_Ctx(...)
HgppStatus hgppiWarpAffine_16u_P4R_Ctx(...)
HgppStatus hgppiWarpAffine_32s_P3R_Ctx(...)
HgppStatus hgppiWarpAffine_32s_P4R_Ctx(...)
HgppStatus hgppiWarpAffine_32f_P3R_Ctx(...)
HgppStatus hgppiWarpAffine_32f_P4R_Ctx(...)
HgppStatus hgppiWarpAffine_64f_P3R_Ctx(...)
HgppStatus hgppiWarpAffine_64f_P4R_Ctx(...)
```

##### 9.6.3.3. 仿射变换工具函数
```c
// 基于源 ROI 和目标四边形计算仿射变换系数。
HgppStatus hgppiGetAffineTransform(HgppiRect oSrcROI, const double aQuad[4][2], double aCoeffs[2][3])

// 计算变换后四边形。
HgppStatus hgppiGetAffineQuad(HgppiRect oSrcROI, double aQuad[4][2], const double aCoeffs[2][3])

// 计算变换后包围盒。
HgppStatus hgppiGetAffineBound(HgppiRect oSrcROI, double aBound[2][2], const double aCoeffs[2][3])
```

### 9.7. 透视变换
#### 9.7.1. 功能介绍
透视变换函数基于 3×3 透视变换矩阵对图像进行 3D 透视投影变换。

> **注意：**
> - 透视变换仅支持 NN、 LINEAR、 CUBIC 三种插值模式。
> - 透视变换系数为 3×3 矩阵，最后一行通常为 [0, 0, 1]

#### 9.7.2. 完整参数说明
##### 9.7.2.1. WarpPerspective 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | **源图像指针** - Packet 格式 |
| `pSrc[]` | 主机指针数组 | [in] | **源图像指针数组** - Planar 格式 |
| `oSrcSize` | HgppiSize | [in] | **源图像尺寸**（像素） |
| `nSrcStep` | int | [in] | **源图像行步幅** |
| `oSrcROI` | HgppiRect | [in] | **源 ROI** |
| `pDst` | 设备指针 | [out] | **目标图像指针** - Packet 格式 |
| `pDst[]` | 主机指针数组 | [out] | **目标图像指针数组** - Planar 格式 |
| `nDstStep` | int | [in] | **目标图像行步幅** |
| `oDstROI` | HgppiRect | [in] | **目标 ROI** |
| `aCoeffs` | double[3][3] | [in] | **透视变换系数** - 3×3 透视变换矩阵 |
| `eInterpolation` | int | [in] | **插值模式** - NN/LINEAR/CUBIC |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

**返回值：** `HgppStatus` - 图像数据相关错误码、 ROI 相关错误码、透视变换错误码

#### 9.7.3. 函数列表
##### 9.7.3.1. WarpPerspective （Packet 格式）
**8 位无符号整数**

```c
// 单通道。
HgppStatus hgppiWarpPerspective_8u_C1R_Ctx(const HGpp8u *pSrc, HgppiSize oSrcSize, int nSrcStep,
                                            HgppiRect oSrcROI, HGpp8u *pDst, int nDstStep,
                                            HgppiRect oDstROI, const double aCoeffs[3][3],
                                            int eInterpolation, HgppStreamContext hgppStreamCtx)

// 三通道。
HgppStatus hgppiWarpPerspective_8u_C3R_Ctx(const HGpp8u *pSrc, HgppiSize oSrcSize, int nSrcStep,
                                            HgppiRect oSrcROI, HGpp8u *pDst, int nDstStep,
                                            HgppiRect oDstROI, const double aCoeffs[3][3],
                                            int eInterpolation, HgppStreamContext hgppStreamCtx)

// 四通道。
HgppStatus hgppiWarpPerspective_8u_C4R_Ctx(...)

// 四通道（忽略 Alpha）
HgppStatus hgppiWarpPerspective_8u_AC4R_Ctx(...)
```

**16 位/32 位/64 位**

```c
// 16 位无符号。
HgppStatus hgppiWarpPerspective_16u_C1R_Ctx(...)
HgppStatus hgppiWarpPerspective_16u_C3R_Ctx(...)
HgppStatus hgppiWarpPerspective_16u_C4R_Ctx(...)
HgppStatus hgppiWarpPerspective_16u_AC4R_Ctx(...)

// 32 位有符号。
HgppStatus hgppiWarpPerspective_32s_C1R_Ctx(...)
HgppStatus hgppiWarpPerspective_32s_C3R_Ctx(...)
HgppStatus hgppiWarpPerspective_32s_C4R_Ctx(...)
HgppStatus hgppiWarpPerspective_32s_AC4R_Ctx(...)

// 32 位浮点。
HgppStatus hgppiWarpPerspective_32f_C1R_Ctx(...)
HgppStatus hgppiWarpPerspective_32f_C3R_Ctx(...)
HgppStatus hgppiWarpPerspective_32f_C4R_Ctx(...)
HgppStatus hgppiWarpPerspective_32f_AC4R_Ctx(...)

// 64 位浮点。
HgppStatus hgppiWarpPerspective_64f_C1R_Ctx(...)
HgppStatus hgppiWarpPerspective_64f_C3R_Ctx(...)
HgppStatus hgppiWarpPerspective_64f_C4R_Ctx(...)
HgppStatus hgppiWarpPerspective_64f_AC4R_Ctx(...)
```

##### 9.7.3.2. WarpPerspective （Planar 格式）
```c
// 8 位无符号三通道Planar格式。
HgppStatus hgppiWarpPerspective_8u_P3R_Ctx(const HGpp8u *pSrc[3], HgppiSize oSrcSize, int nSrcStep,
                                            HgppiRect oSrcROI, HGpp8u *pDst[3], int nDstStep,
                                            HgppiRect oDstROI, const double aCoeffs[3][3],
                                            int eInterpolation, HgppStreamContext hgppStreamCtx)

// 8 位无符号四通道Planar格式。
HgppStatus hgppiWarpPerspective_8u_P4R_Ctx(const HGpp8u *pSrc[4], HgppiSize oSrcSize, int nSrcStep,
                                            HgppiRect oSrcROI, HGpp8u *pDst[4], int nDstStep,
                                            HgppiRect oDstROI, const double aCoeffs[3][3],
                                            int eInterpolation, HgppStreamContext hgppStreamCtx)

// 16 位/32 位/64 位Planar格式。
HgppStatus hgppiWarpPerspective_16u_P3R_Ctx(...)
HgppStatus hgppiWarpPerspective_16u_P4R_Ctx(...)
HgppStatus hgppiWarpPerspective_32s_P3R_Ctx(...)
HgppStatus hgppiWarpPerspective_32s_P4R_Ctx(...)
HgppStatus hgppiWarpPerspective_32f_P3R_Ctx(...)
HgppStatus hgppiWarpPerspective_32f_P4R_Ctx(...)
HgppStatus hgppiWarpPerspective_64f_P3R_Ctx(...)
HgppStatus hgppiWarpPerspective_64f_P4R_Ctx(...)
```

### 9.8. 反向仿射变换
基于仿射变换矩阵的**反向**图像变换（warp）。

**反向仿射变换公式**

仿射变换由 2×3 矩阵 C 给出。源图像中的像素位置 (x, y) 映射到目标图像中的位置 (x', y')：

```text
x' = c00*x + c01*y + c02
y' = c10*x + c11*y + c12

C = [c00 c01 c02]
    [c10 c11 c12]
```

反向变换使用逆矩阵 C^(-1) = M：

```text
x = m00*x' + m01*y' + m02
y = m10*x' + m11*y' + m12
```

#### 9.8.1. 通用参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `pSrc` | const 指针 | 源图像指针（Packet 格式） |
| `pSrc[]` | 主机指针数组 | 源图像指针数组 |
| `oSrcSize` | HgppiSize | 源图像尺寸（像素） |
| `nSrcStep` | int | 源图像行步幅 |
| `oSrcROI` | HgppiRect | 源 ROI |
| `pDst` | 指针 | 目标图像指针（Packet 格式） |
| `pDst[]` | 主机指针数组 | 目标图像指针数组 |
| `nDstStep` | int | 目标图像行步幅 |
| `oDstROI` | HgppiRect | 目标 ROI |
| `aCoeffs` | const double[2][3] | 仿射变换系数矩阵 |
| `eInterpolation` | int | 插值模式： NN/LINEAR/CUBIC |
| `hgppStreamCtx` | HgppStreamContext | 流上下文 |

#### 9.8.2. 函数列表
##### 9.8.2.1. 8 位无符号整数
```c
HgppStatus hgppiWarpAffineBack_8u_C1R_Ctx(const HGpp8u *pSrc, HgppiSize oSrcSize, int nSrcStep,
                                           HgppiRect oSrcROI, HGpp8u *pDst, int nDstStep,
                                           HgppiRect oDstROI, const double aCoeffs[2][3],
                                           int eInterpolation, HgppStreamContext hgppStreamCtx)
// 单通道 8 位无符号反向仿射变换。

HgppStatus hgppiWarpAffineBack_8u_C3R_Ctx(...)  // 三通道。
HgppStatus hgppiWarpAffineBack_8u_C4R_Ctx(...)  // 四通道。
HgppStatus hgppiWarpAffineBack_8u_AC4R_Ctx(...) // 四通道（不影响 Alpha）
```

##### 9.8.2.2. 16 位/32 位
```c
// 16u, 16s, 32f 类似，提供 C1R, C3R, C4R, AC4R 变体。
HgppStatus hgppiWarpAffineBack_32f_C1R_Ctx(const Hgpp32f *pSrc, HgppiSize oSrcSize, int nSrcStep,
                                            HgppiRect oSrcROI, Hgpp32f *pDst, int nDstStep,
                                            HgppiRect oDstROI, const double aCoeffs[2][3],
                                            int eInterpolation, HgppStreamContext hgppStreamCtx)
// ... 其他变体类似。
```

### 9.9. 基于四边形的仿射变换
基于四边形到四边形映射的仿射变换。

**四边形仿射变换**

仿射变换由 3 个离散点的映射完全确定。此函数计算将源四边形的**前三个角点**映射到目标四边形**前三个顶点**的仿射变换矩阵。

> **注意：**
> 如果第四个顶点不匹配变换，将返回 `HGPP_AFFINE_QUAD_INCORRECT_WARNING` 警告。

#### 9.9.1. 通用参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `pSrc` | const 指针 | 源图像指针 |
| `oSrcSize` | HgppiSize | 源图像尺寸 |
| `nSrcStep` | int | 源图像行步幅 |
| `oSrcROI` | HgppiRect | 源 ROI |
| `aSrcQuad` | const double[4][2] | 源四边形顶点坐标 |
| `pDst` | 指针 | 目标图像指针 |
| `nDstStep` | int | 目标图像行步幅 |
| `oDstROI` | HgppiRect | 目标 ROI |
| `aDstQuad` | const double[4][2] | 目标四边形顶点坐标 |
| `eInterpolation` | int | 插值模式： NN/LINEAR/CUBIC |
| `hgppStreamCtx` | HgppStreamContext | 流上下文 |

#### 9.9.2. 函数列表
##### 9.9.2.1. 8 位无符号整数
```c
HgppStatus hgppiWarpAffineQuad_8u_C1R_Ctx(const HGpp8u *pSrc, HgppiSize oSrcSize, int nSrcStep,
                                           HgppiRect oSrcROI, const double aSrcQuad[4][2],
                                           HGpp8u *pDst, int nDstStep, HgppiRect oDstROI,
                                           const double aDstQuad[4][2], int eInterpolation,
                                           HgppStreamContext hgppStreamCtx)
// 单通道 8 位无符号四边形仿射变换。

HgppStatus hgppiWarpAffineQuad_8u_C3R_Ctx(...)  // 三通道。
HgppStatus hgppiWarpAffineQuad_8u_C4R_Ctx(...)  // 四通道。
HgppStatus hgppiWarpAffineQuad_8u_AC4R_Ctx(...) // 四通道（不影响 Alpha）
```

##### 9.9.2.2. 16 位/32 位
```c
// 16u, 16s, 32f 类似，提供 C1R, C3R, C4R, AC4R 变体。
HgppStatus hgppiWarpAffineQuad_32f_C1R_Ctx(const Hgpp32f *pSrc, HgppiSize oSrcSize, int nSrcStep,
                                            HgppiRect oSrcROI, const double aSrcQuad[4][2],
                                            Hgpp32f *pDst, int nDstStep, HgppiRect oDstROI,
                                            const double aDstQuad[4][2], int eInterpolation,
                                            HgppStreamContext hgppStreamCtx)
// ... 其他变体类似。
```

### 9.10. 反向透视变换
基于透视变换矩阵的**反向**图像变换（warp）。

**反向透视变换公式**

透视变换由 3×3 矩阵 C 给出：

```text
x' = (c00*x + c01*y + c02) / (c20*x + c21*y + c22)
y' = (c10*x + c11*y + c12) / (c20*x + c21*y + c22)

C = [c00 c01 c02]
    [c10 c11 c12]
    [c20 c21 c22]
```

反向变换使用逆矩阵 C^(-1) = M。

#### 9.10.1. 通用参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `pSrc` | const 指针 | 源图像指针（Packet 格式） |
| `pSrc[]` | 主机指针数组 | 源图像指针数组 |
| `oSrcSize` | HgppiSize | 源图像尺寸（像素） |
| `nSrcStep` | int | 源图像行步幅 |
| `oSrcROI` | HgppiRect | 源 ROI |
| `pDst` | 指针 | 目标图像指针（Packet 格式） |
| `pDst[]` | 主机指针数组 | 目标图像指针数组 |
| `nDstStep` | int | 目标图像行步幅 |
| `oDstROI` | HgppiRect | 目标 ROI |
| `aCoeffs` | const double[3][3] | 透视变换系数矩阵 |
| `eInterpolation` | int | 插值模式： NN/LINEAR/CUBIC |
| `hgppStreamCtx` | HgppStreamContext | 流上下文 |

#### 9.10.2. 函数列表
##### 9.10.2.1. 8 位无符号整数
```c
HgppStatus hgppiWarpPerspectiveBack_8u_C1R_Ctx(const HGpp8u *pSrc, HgppiSize oSrcSize, int nSrcStep,
                                                HgppiRect oSrcROI, HGpp8u *pDst, int nDstStep,
                                                HgppiRect oDstROI, const double aCoeffs[3][3],
                                                int eInterpolation, HgppStreamContext hgppStreamCtx)
// 单通道 8 位无符号反向透视变换。

HgppStatus hgppiWarpPerspectiveBack_8u_C3R_Ctx(...)  // 三通道。
HgppStatus hgppiWarpPerspectiveBack_8u_C4R_Ctx(...)  // 四通道。
HgppStatus hgppiWarpPerspectiveBack_8u_AC4R_Ctx(...) // 四通道（不影响 Alpha）
```

##### 9.10.2.2. 16 位/32 位
```c
// 16u, 16s, 32f 类似，提供 C1R, C3R, C4R, AC4R 变体。
HgppStatus hgppiWarpPerspectiveBack_32f_C1R_Ctx(const Hgpp32f *pSrc, HgppiSize oSrcSize, int nSrcStep,
                                                 HgppiRect oSrcROI, Hgpp32f *pDst, int nDstStep,
                                                 HgppiRect oDstROI, const double aCoeffs[3][3],
                                                 int eInterpolation, HgppStreamContext hgppStreamCtx)
// ... 其他变体类似。
```

### 9.11. 基于四边形的透视变换
基于四边形到四边形映射的透视变换。

**四边形透视变换**

透视变换将源图像空间中的四边形映射到目标图像空间中的四边形。

#### 9.11.1. 通用参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `pSrc` | const 指针 | 源图像指针 |
| `oSrcSize` | HgppiSize | 源图像尺寸 |
| `nSrcStep` | int | 源图像行步幅 |
| `oSrcROI` | HgppiRect | 源 ROI |
| `aSrcQuad` | const double[4][2] | 源四边形顶点坐标 |
| `pDst` | 指针 | 目标图像指针 |
| `nDstStep` | int | 目标图像行步幅 |
| `oDstROI` | HgppiRect | 目标 ROI |
| `aDstQuad` | const double[4][2] | 目标四边形顶点坐标 |
| `eInterpolation` | int | 插值模式： NN/LINEAR/CUBIC |
| `hgppStreamCtx` | HgppStreamContext | 流上下文 |

#### 9.11.2. 函数列表
##### 9.11.2.1. 8 位无符号整数
```c
HgppStatus hgppiWarpPerspectiveQuad_8u_C1R_Ctx(const HGpp8u *pSrc, HgppiSize oSrcSize, int nSrcStep,
                                                HgppiRect oSrcROI, const double aSrcQuad[4][2],
                                                HGpp8u *pDst, int nDstStep, HgppiRect oDstROI,
                                                const double aDstQuad[4][2], int eInterpolation,
                                                HgppStreamContext hgppStreamCtx)
// 单通道 8 位无符号四边形透视变换。

HgppStatus hgppiWarpPerspectiveQuad_8u_C3R_Ctx(...)  // 三通道。
HgppStatus hgppiWarpPerspectiveQuad_8u_C4R_Ctx(...)  // 四通道。
HgppStatus hgppiWarpPerspectiveQuad_8u_AC4R_Ctx(...) // 四通道（不影响 Alpha）
```

##### 9.11.2.2. 16 位/32 位
```c
// 16u, 16s, 32f 类似，提供 C1R, C3R, C4R, AC4R 变体。
HgppStatus hgppiWarpPerspectiveQuad_32f_C1R_Ctx(const Hgpp32f *pSrc, HgppiSize oSrcSize, int nSrcStep,
                                                 HgppiRect oSrcROI, const double aSrcQuad[4][2],
                                                 Hgpp32f *pDst, int nDstStep, HgppiRect oDstROI,
                                                 const double aDstQuad[4][2], int eInterpolation,
                                                 HgppStreamContext hgppStreamCtx)
// ... 其他变体类似。
```

### 9.12. 批处理
#### 9.12.1. 功能介绍
批处理函数允许同时处理多幅图像，提高 真武 PPU 资源利用率。适用于批量处理较小图像的场景。

> **注意：**
> - 批处理不推荐用于非常大的图像，可能没有足够资源同时处理多幅大图像。
> - 所有批处理参数都在设备内存中传递。
> - **ROI 使用方式因函数类型而异**——有些函数共用统一 ROI，有些函数每个图像可以有自己的 ROI。

#### 9.12.2. ROI 使用方式对比
| 函数类型 | ROI 使用方式 | 说明 |
|----------|-------------|------|
| **ResizeBatch （标准版）** | 统一 ROI | 单个 `oSrcRectROI` 和 `oDstRectROI` 应用于批处理中的所有图像 |
| **ResizeBatch_Advanced** | 每图像独立 ROI | 每个图像可以有自己的 `oSrcRectROI` 和 `oDstRectROI` |
| **WarpAffineBatch** | 统一 ROI | 单个 `oSrcRectROI` 和 `oDstRectROI` 应用于批处理中的所有图像 |
| **WarpAffineBatch_Advanced** | 每图像独立 ROI | 每个图像可以有自己的 ROI 和变换系数 |
| **WarpPerspectiveBatch** | 统一 ROI | 单个 `oSrcRectROI` 和 `oDstRectROI` 应用于批处理中的所有图像 |

#### 9.12.3. ResizeBatch
##### 9.12.3.1. ResizeBatch （标准版 - 统一 ROI）
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `oSmallestSrcSize` | HgppiSize | [in] | **最小源图像尺寸** - 批处理中所有源图像的最小宽度和高度（可能来自不同图像） |
| `oSrcRectROI` | HgppiRect | [in] | **统一源 ROI** - **单个 ROI 应用于所有源图像**（可以超出源图像尺寸） |
| `oSmallestDstSize` | HgppiSize | [in] | **最小目标图像尺寸** - 批处理中所有目标图像的最小宽度和高度 |
| `oDstRectROI` | HgppiRect | [in] | **统一目标 ROI** - **单个 ROI 应用于所有目标图像**（可以超出目标图像尺寸） |
| `eInterpolation` | int | [in] | **插值模式** - NN/LINEAR/CUBIC/SUPER，应用于所有图像 |
| `pBatchList` | 设备指针 | [in] | **批处理参数列表** - 指向设备内存中的 `HgppiResizeBatchCXR` 结构数组（nBatchSize 个实例） |
| `nBatchSize` | int | [in] | **批处理大小** - 处理的图像数量（必须 > 1） |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

> **注意：**
> - **单个 `oSrcRectROI` 和 `oDstRectROI` 应用于批处理中的每幅图像**
> - 源图像和目标图像尺寸可以不同，但 `oSmallestSrcSize` 和 `oSmallestDstSize` 必须设置为批处理中的最小值。
> - `HgppiResizeBatchCXR` 结构数组必须在设备内存中。

##### 9.12.3.2. ResizeBatch_Advanced （每图像独立 ROI）
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `nMaxWidth` | int | [in] | **最大目标 ROI 宽度** - 所有目标 ROI 的最大宽度 |
| `nMaxHeight` | int | [in] | **最大目标 ROI 高度** - 所有目标 ROI 的最大高度 |
| `pBatchSrc` | 设备指针 | [in] | **源图像描述符列表** - `HgppiImageDescriptor` 结构数组（设备内存） |
| `pBatchDst` | 设备指针 | [in] | **目标图像描述符列表** - `HgppiImageDescriptor` 结构数组（设备内存） |
| `pBatchROI` | 设备指针 | [in] | **每图像 ROI 列表** - `HgppiResizeBatchROI_Advanced` 结构数组（设备内存），**每个图像可以有自己的源 ROI 和目标 ROI** |
| `nBatchSize` | int | [in] | **批处理大小** - 图像数量 |
| `eInterpolation` | int | [in] | **插值模式** - 应用于所有图像 |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

> **注意：**
> - **每个图像可以有自己的 `oSrcRectROI` 和 `oDstRectROI`**，通过 `pBatchROI` 数组传递。
> - `pBatchSrc`、`pBatchDst`、`pBatchROI` 都必须在设备内存中。
> - 用户需要初始化这些结构并复制到设备内存。

##### 9.12.3.3. 函数列表
##### 9.12.3.4. ResizeBatch （标准版 - 统一 ROI）
**8 位无符号整数**

```c
// 单通道。
HgppStatus hgppiResizeBatch_8u_C1R_Ctx(HgppiSize oSmallestSrcSize, HgppiRect oSrcRectROI,
                                        HgppiSize oSmallestDstSize, HgppiRect oDstRectROI,
                                        int eInterpolation, HgppiResizeBatchCXR *pBatchList,
                                        unsigned int nBatchSize, HgppStreamContext hgppStreamCtx)

// 三通道。
HgppStatus hgppiResizeBatch_8u_C3R_Ctx(HgppiSize oSmallestSrcSize, HgppiRect oSrcRectROI,
                                        HgppiSize oSmallestDstSize, HgppiRect oDstRectROI,
                                        int eInterpolation, HgppiResizeBatchCXR *pBatchList,
                                        unsigned int nBatchSize, HgppStreamContext hgppStreamCtx)

// 四通道。
HgppStatus hgppiResizeBatch_8u_C4R_Ctx(HgppiSize oSmallestSrcSize, HgppiRect oSrcRectROI,
                                        HgppiSize oSmallestDstSize, HgppiRect oDstRectROI,
                                        int eInterpolation, HgppiResizeBatchCXR *pBatchList,
                                        unsigned int nBatchSize, HgppStreamContext hgppStreamCtx)

// 四通道（不影响 Alpha）
HgppStatus hgppiResizeBatch_8u_AC4R_Ctx(HgppiSize oSmallestSrcSize, HgppiRect oSrcRectROI,
                                         HgppiSize oSmallestDstSize, HgppiRect oDstRectROI,
                                         int eInterpolation, HgppiResizeBatchCXR *pBatchList,
                                         unsigned int nBatchSize, HgppStreamContext hgppStreamCtx)
```

**32 位浮点数**

```c
HgppStatus hgppiResizeBatch_32f_C1R_Ctx(HgppiSize oSmallestSrcSize, HgppiRect oSrcRectROI,
                                         HgppiSize oSmallestDstSize, HgppiRect oDstRectROI,
                                         int eInterpolation, HgppiResizeBatchCXR *pBatchList,
                                         unsigned int nBatchSize, HgppStreamContext hgppStreamCtx)
HgppStatus hgppiResizeBatch_32f_C3R_Ctx(...)
HgppStatus hgppiResizeBatch_32f_C4R_Ctx(...)
HgppStatus hgppiResizeBatch_32f_AC4R_Ctx(...)
```

##### 9.12.3.5. ResizeBatch_Advanced （每图像独立 ROI）
**8 位无符号整数**

```c
// 单通道 - 可变 ROI。
HgppStatus hgppiResizeBatch_8u_C1R_Advanced_Ctx(int nMaxWidth, int nMaxHeight,
                                                 HgppiImageDescriptor *pBatchSrc,
                                                 HgppiImageDescriptor *pBatchDst,
                                                 HgppiResizeBatchROI_Advanced *pBatchROI,
                                                 unsigned int nBatchSize, int eInterpolation,
                                                 HgppStreamContext hgppStreamCtx)

// 三通道 - 可变 ROI。
HgppStatus hgppiResizeBatch_8u_C3R_Advanced_Ctx(int nMaxWidth, int nMaxHeight,
                                                 HgppiImageDescriptor *pBatchSrc,
                                                 HgppiImageDescriptor *pBatchDst,
                                                 HgppiResizeBatchROI_Advanced *pBatchROI,
                                                 unsigned int nBatchSize, int eInterpolation,
                                                 HgppStreamContext hgppStreamCtx)

// 四通道 - 可变 ROI。
HgppStatus hgppiResizeBatch_8u_C4R_Advanced_Ctx(...)

// 四通道 - 可变 ROI（不影响 Alpha）
HgppStatus hgppiResizeBatch_8u_AC4R_Advanced_Ctx(...)
```

**16 位/32 位浮点**

```c
// 16 位浮点 - 可变 ROI。
HgppStatus hgppiResizeBatch_16f_C1R_Advanced_Ctx(...)
HgppStatus hgppiResizeBatch_16f_C3R_Advanced_Ctx(...)
HgppStatus hgppiResizeBatch_16f_C4R_Advanced_Ctx(...)

// 32 位浮点 - 可变 ROI。
HgppStatus hgppiResizeBatch_32f_C1R_Advanced_Ctx(...)
HgppStatus hgppiResizeBatch_32f_C3R_Advanced_Ctx(...)
HgppStatus hgppiResizeBatch_32f_C4R_Advanced_Ctx(...)
HgppStatus hgppiResizeBatch_32f_AC4R_Advanced_Ctx(...)
```

#### 9.12.4. 仿射变换批处理
##### 9.12.4.1. 功能介绍
WarpAffineBatch 函数批量执行仿射变换。**标准版使用统一 ROI， Advanced 版支持每图像独立 ROI**。

> **注意：**
> - 必须在使用前调用 `hgppiWarpAffineBatchInit_Ctx` 初始化 `aTransformedCoeffs` 数组。
> - 当批处理列表中任何变换矩阵改变时，必须重新调用初始化函数。
> - 初始化函数的批处理大小必须与对应的仿射变换批处理函数匹配。

##### 9.12.4.2. WarpAffineBatch 参数说明（标准版 - 统一 ROI）
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `oSmallestSrcSize` | HgppiSize | [in] | **最小源图像尺寸** - 批处理中所有源图像的最小宽度和高度 |
| `oSrcRectROI` | HgppiRect | [in] | **统一源 ROI** - **单个 ROI 应用于所有源图像** |
| `oDstRectROI` | HgppiRect | [in] | **统一目标 ROI** - **单个 ROI 应用于所有目标图像** |
| `eInterpolation` | int | [in] | **插值模式** - NN/LINEAR/CUBIC，应用于所有图像 |
| `pBatchList` | 设备指针 | [in] | **批处理参数列表** - `HgppiWarpAffineBatchCXR` 结构数组（设备内存） |
| `nBatchSize` | int | [in] | **批处理大小** - 必须 > 1 |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

##### 9.12.4.3. WarpAffineBatchInit 初始化函数
```c
HgppStatus hgppiWarpAffineBatchInit_Ctx(HgppiWarpAffineBatchCXR *pBatchList,
                                         unsigned int nBatchSize,
                                         HgppStreamContext hgppStreamCtx)
```

| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pBatchList` | 设备指针 | [in,out] | **批处理参数列表** - 设备内存中的 `HgppiWarpAffineBatchCXR` 结构数组 |
| `nBatchSize` | unsigned int | [in] | **批处理大小** - 必须与对应的仿射变换批处理函数匹配 |
| `hgppStreamCtx` | HgppStreamContext | [in] | **流上下文** |

**功能说明：** 初始化 `pBatchList` 中每个图像的 `aTransformedCoeffs` 数组。**必须在调用仿射变换批处理函数之前调用**，特别是当列表中的任何变换矩阵发生改变时。

##### 9.12.4.4. WarpAffineBatch 函数列表（标准版 - 统一 ROI）
**8 位无符号整数**

```c
// 单通道。
HgppStatus hgppiWarpAffineBatch_8u_C1R_Ctx(HgppiSize oSmallestSrcSize, HgppiRect oSrcRectROI,
                                            HgppiRect oDstRectROI, int eInterpolation,
                                            HgppiWarpAffineBatchCXR *pBatchList,
                                            unsigned int nBatchSize,
                                            HgppStreamContext hgppStreamCtx)

// 三通道。
HgppStatus hgppiWarpAffineBatch_8u_C3R_Ctx(HgppiSize oSmallestSrcSize, HgppiRect oSrcRectROI,
                                            HgppiRect oDstRectROI, int eInterpolation,
                                            HgppiWarpAffineBatchCXR *pBatchList,
                                            unsigned int nBatchSize,
                                            HgppStreamContext hgppStreamCtx)

// 四通道。
HgppStatus hgppiWarpAffineBatch_8u_C4R_Ctx(...)

// 四通道（不影响 Alpha）
HgppStatus hgppiWarpAffineBatch_8u_AC4R_Ctx(...)
```

**16 位/32 位浮点**

```c
HgppStatus hgppiWarpAffineBatch_16f_C1R_Ctx(...)
HgppStatus hgppiWarpAffineBatch_16f_C3R_Ctx(...)
HgppStatus hgppiWarpAffineBatch_16f_C4R_Ctx(...)

HgppStatus hgppiWarpAffineBatch_32f_C1R_Ctx(...)
HgppStatus hgppiWarpAffineBatch_32f_C3R_Ctx(...)
HgppStatus hgppiWarpAffineBatch_32f_C4R_Ctx(...)
HgppStatus hgppiWarpAffineBatch_32f_AC4R_Ctx(...)
```

#### 9.12.5. 透视变换批处理
批量处理多幅图像的透视变换。

**批处理操作**

- 批处理函数对多幅图像执行相同的透视变换操作。
- 所有图像使用**最小的源图像和目标图像尺寸**。
- 每幅图像可以有自己的变换系数。
- 支持 C1R, C3R, C4R, AC4R 通道配置。

##### 9.12.5.1. 通用参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `oSmallestSrcSize` | HgppiSize | 批次中最小的源图像尺寸 |
| `oSrcRectROI` | HgppiRect | 源 ROI （所有图像统一） |
| `oDstRectROI` | HgppiRect | 目标 ROI （所有图像统一） |
| `aCoeffs` | const double[3][3] | 透视变换系数 |
| `eInterpolation` | int | 插值模式： NN/LINEAR/CUBIC |
| `pBatchList` | HgppiWarpPerspectiveBatchCXR* | 批处理列表（设备内存） |
| `nBatchSize` | unsigned int | 批次大小（必须 > 1） |
| `hgppStreamCtx` | HgppStreamContext | 流上下文 |

##### 9.12.5.2. WarpPerspectiveBatch 函数列表
###### 8 位无符号整数
```c

HgppStatus hgppiWarpPerspectiveBatch_8u_C1R_Ctx(HgppiSize oSmallestSrcSize, HgppiRect oSrcRectROI,
                                                 HgppiRect oDstRectROI, const double aCoeffs[3][3],
                                                 int eInterpolation,
                                                 HgppiWarpPerspectiveBatchCXR *pBatchList,
                                                 unsigned int nBatchSize,
                                                 HgppStreamContext hgppStreamCtx)
// 单通道 8 位无符号透视变换批处理。

HgppStatus hgppiWarpPerspectiveBatch_8u_C3R_Ctx(...)  // 三通道。
HgppStatus hgppiWarpPerspectiveBatch_8u_C4R_Ctx(...)  // 四通道。
HgppStatus hgppiWarpPerspectiveBatch_8u_AC4R_Ctx(...) // 四通道（不影响 Alpha）
```

###### 16 位/32 位
```c

// 16u, 16s, 32f 类似，提供 C1R, C3R, C4R, AC4R 变体。
HgppStatus hgppiWarpPerspectiveBatch_32f_C1R_Ctx(HgppiSize oSmallestSrcSize, HgppiRect oSrcRectROI,
                                                  HgppiRect oDstRectROI, const double aCoeffs[3][3],
                                                  int eInterpolation,
                                                  HgppiWarpPerspectiveBatchCXR *pBatchList,
                                                  unsigned int nBatchSize,
                                                  HgppStreamContext hgppStreamCtx)
// ... 其他变体类似。
```

### 9.13. 错误码汇总
| 错误码 | 说明 | 适用章节 |
|--------|------|----------|
| `HGPP_WRONG_INTERSECTION_ROI_ERROR` | srcROIRect 与源图像无交集 | Resize/Remap/Rotate/Affine/Perspective |
| `HGPP_RESIZE_NO_OPERATION_ERROR` | 目标 ROI 宽度或高度 < 1 像素 | Resize |
| `HGPP_RESIZE_FACTOR_ERROR` | nXFactor 或 nYFactor ≤ 0，或超采样模式下不是双缩小 | Resize |
| `HGPP_INTERPOLATION_ERROR` | eInterpolation 值非法 | 全部 |
| `HGPP_SIZE_ERROR` | 源尺寸宽度或高度 < 2 像素，或原图像操作 Mirror ROI 不是偶数 | Resize/Mirror |
| `HGPP_RECTANGLE_ERROR` | ROI 与源图像交集的宽度或高度 ≤ 1 | Rotate/Affine/Perspective |
| `HGPP_WRONG_INTERSECTION_QUAD_WARNING` | 变换后的源 ROI 与目标 ROI 无交集（警告） | Rotate/Affine/Perspective |
| `HGPP_COEFFICIENT_ERROR` | 变换系数无效 | Affine/Perspective |
| `HGPP_MIRROR_FLIP_ERROR` | flip 轴值非法 | Mirror |
| `HGPP_AFFINE_QUAD_INCORRECT_WARNING` | 四边形不符合变换属性（仿射变换警告） | Affine |

比赛关联：本章是 VLM 图像预处理 offload 的核心——`hgppiResizeSqrPixel_*` 把任意尺寸输入图缩放到视觉编码器要求的分辨率（注意 LINEAR/CUBIC 与 PIL/torch 参考实现的像素差异，关乎精度保持）；`ResizeBatch`/`ResizeBatch_Advanced` 适合多图 batch 推理场景提升吞吐。插值模式选择和 CPU 参考不一致是精度掉分的常见原因。

## 10. 图像线性变换函数
> **库名称**: `hgppist` 
> **功能**: 线性图像变换（傅里叶变换相关）  

### 10.1. 傅里叶变换
#### 10.1.1. 幅值计算
将复数像素图像转换为单通道实数图像。

##### 10.1.1.1. 复数幅值
对于复数 $z = a + bi$：

**幅值（Magnitude）**:
$$|z| = \sqrt{a^2 + b^2}$$

**平方幅值（Magnitude Squared）**:
$$|z|^2 = a^2 + b^2$$

**性能**: 
- 平方幅值计算比实际幅值更快（无需开方运算）。
- 如果幅值仅用于**排序或比较**，建议使用平方幅值函数进行性能优化。

#### 10.1.2. 函数列表
##### 10.1.2.1. hgppiMagnitude_32fc32f_C1R_Ctx
复数 → 幅值转换。

```cpp
HgppStatus hgppiMagnitude_32fc32f_C1R_Ctx(
    const Hgpp32fc *pSrc,    // 源图像指针（32 位复数）
    int nSrcStep,            // 源图像行步长。
    Hgpp32f *pDst,           // 目标图像指针（32 位浮点）
    int nDstStep,            // 目标图像行步长。
    HgppiSize oSizeROI,      // 感兴趣区域。
    HgppStreamContext hgppStreamCtx  // 流上下文。
)
```

**功能**: 将复数像素图像转换为单通道图像，计算结果像素为复数值的幅值。

**计算**: `dst = sqrt(re² + im²)`

##### 10.1.2.2. hgppiMagnitudeSqr_32fc32f_C1R_Ctx
复数 → 平方幅值转换。

```cpp
HgppStatus hgppiMagnitudeSqr_32fc32f_C1R_Ctx(
    const Hgpp32fc *pSrc,    // 源图像指针（32 位复数）
    int nSrcStep,            // 源图像行步长。
    Hgpp32f *pDst,           // 目标图像指针（32 位浮点）
    int nDstStep,            // 目标图像行步长。
    HgppiSize oSizeROI,      // 感兴趣区域。
    HgppStreamContext hgppStreamCtx  // 流上下文。
)
```

**功能**: 将复数像素图像转换为单通道图像，计算结果像素为复数值的平方幅值。

**计算**: `dst = re² + im²`

**性能优化建议**: 
- 平方幅值是计算幅值过程中的中间结果。
- 如果幅值仅用于**排序或比较**，使用此函数代替 `hgppiMagnitude_32fc32f_C1R_Ctx` 可获得更好的性能。

### 10.2. 通用参数说明
| 参数 | 类型 | 说明 | 注意事项 |
|------|------|------|----------|
| `pSrc` | const Hgpp32fc* | 源图像指针（32 位复数） | 不能为空指针 |
| `nSrcStep` | int | 源图像行步长（字节） | 必须 ≥ ROI 宽度 × 8 字节 |
| `pDst` | Hgpp32f* | 目标图像指针（32 位浮点） | 不能为空指针 |
| `nDstStep` | int | 目标图像行步长（字节） | 必须 ≥ ROI 宽度 × 4 字节 |
| `oSizeROI` | HgppiSize | 感兴趣区域 | 宽度和高度必须 > 0 |
| `hgppStreamCtx` | HgppStreamContext | 应用程序管理流上下文 | - |

## 11. 图像形态学操作
> **库名称**: `hgppim` 
> **功能**: 形态学图像处理操作（邻域操作）  

### 11.1. 膨胀函数（Dilation Functions）
#### 11.1.1. 图像膨胀（Image Dilate）
##### 11.1.1.1. 膨胀原理
膨胀将输出像素计算为掩码下像素值的**最大值**。对应掩码值为零的像素不参与最大值搜索。

> **注意：**
> 用户有责任避免超出图像边界的采样。

##### 11.1.1.2. 通用参数
所有 `hgppiDilate` 系列函数共享以下参数：

| 参数 | 说明 |
|------|------|
| `pSrc` | 源图像指针 |
| `nSrcStep` | 源图像行步幅（字节） |
| `pDst` | 目标图像指针 |
| `nDstStep` | 目标图像行步幅（字节） |
| `oSizeROI` | 感兴趣区域（ROI） |
| `pMask` | 掩码数组起始地址指针 |
| `oMaskSize` | 掩码数组的宽度和高度 |
| `oAnchor` | 掩码原点相对于源像素的 X 和 Y 偏移 |
| `hgppStreamCtx` | 应用程序管理流上下文 |

##### 11.1.1.3. 函数列表
**8 位无符号整数膨胀：**

```c
HgppStatus hgppiDilate_8u_C1R_Ctx(...)   // 单通道。
HgppStatus hgppiDilate_8u_C3R_Ctx(...)   // 三通道。
HgppStatus hgppiDilate_8u_C4R_Ctx(...)   // 四通道。
HgppStatus hgppiDilate_8u_AC4R_Ctx(...)  // 四通道（忽略 Alpha）
```

**16 位无符号整数膨胀：**

```c
HgppStatus hgppiDilate_16u_C1R_Ctx(...)   // 单通道。
HgppStatus hgppiDilate_16u_C3R_Ctx(...)   // 三通道。
HgppStatus hgppiDilate_16u_C4R_Ctx(...)   // 四通道。
HgppStatus hgppiDilate_16u_AC4R_Ctx(...)  // 四通道（忽略 Alpha）
```

**32 位浮点膨胀：**

```c
HgppStatus hgppiDilate_32f_C1R_Ctx(...)   // 单通道。
HgppStatus hgppiDilate_32f_C3R_Ctx(...)   // 三通道。
HgppStatus hgppiDilate_32f_C4R_Ctx(...)   // 四通道。
HgppStatus hgppiDilate_32f_AC4R_Ctx(...)  // 四通道（忽略 Alpha）
```

> **说明**：以上函数族具有相同的参数结构，仅数据类型和通道数不同。详细参数描述见上方"通用参数"节。

#### 11.1.2. 带边界控制的膨胀（Image Dilate Border）
##### 11.1.2.1. 带边界控制的膨胀原理
膨胀计算输出像素为掩码下像素的最大值。对于灰度膨胀，掩码包含有符号值，在确定最大值之前先加到对应源图像样本值上（钳位后）。

如果掩码的任何部分与源图像边界重叠，则对所有落在源图像外的掩码像素应用请求的边界类型操作。

> **注意：**
> `HGPP_BORDER_REPLICATE` 边界类型。

##### 11.1.2.2. 通用参数（Border 版本）
| 参数 | 说明 |
|------|------|
| `pSrc` | 源图像指针 |
| `nSrcStep` | 源图像行步幅 |
| `oSrcSize` | 源图像宽度和高度（像素） |
| `oSrcOffset` | 源图像相对于 pSrc 的起始点 |
| `pDst` | 目标图像指针 |
| `nDstStep` | 目标图像行步幅 |
| `oSizeROI` | 感兴趣区域 |
| `pMask` | 掩码数组指针 |
| `oMaskSize` | 掩码尺寸 |
| `oAnchor` | 掩码原点偏移 |
| `eBorderType` | 边界类型操作 |
| `hgppStreamCtx` | 流上下文 |

##### 11.1.2.3. 函数列表
**8 位无符号整数膨胀（带边界）：**
```c
HgppStatus hgppiDilateBorder_8u_C1R_Ctx(...)
HgppStatus hgppiDilateBorder_8u_C3R_Ctx(...)
HgppStatus hgppiDilateBorder_8u_C4R_Ctx(...)
HgppStatus hgppiDilateBorder_8u_AC4R_Ctx(...)  // 忽略 Alpha。
```

**16 位无符号整数膨胀（带边界）：**
```c
HgppStatus hgppiDilateBorder_16u_C1R_Ctx(...)
HgppStatus hgppiDilateBorder_16u_C3R_Ctx(...)
HgppStatus hgppiDilateBorder_16u_C4R_Ctx(...)
HgppStatus hgppiDilateBorder_16u_AC4R_Ctx(...)  // 忽略 Alpha。
```

**32 位浮点膨胀（带边界）：**
```c
HgppStatus hgppiDilateBorder_32f_C1R_Ctx(...)
HgppStatus hgppiDilateBorder_32f_C3R_Ctx(...)
HgppStatus hgppiDilateBorder_32f_C4R_Ctx(...)
HgppStatus hgppiDilateBorder_32f_AC4R_Ctx(...)  // 忽略 Alpha。
```

**灰度膨胀（带边界）：**
```c
HgppStatus hgppiGrayDilateBorder_8u_C1R_Ctx(...)   // 8 位灰度。
HgppStatus hgppiGrayDilateBorder_32f_C1R_Ctx(...)  // 32 位浮点灰度。
```

#### 11.1.3. 3x3 膨胀（Image Dilate 3x3）
##### 11.1.3.1. 原理
使用 3x3 掩码进行膨胀，锚点位于中心像素。

> **注意：**
> 用户有责任避免超出图像边界的采样。

##### 11.1.3.2. 通用参数
| 参数 | 说明 |
|------|------|
| `pSrc` | 源图像指针 |
| `nSrcStep` | 源图像行步幅 |
| `pDst` | 目标图像指针 |
| `nDstStep` | 目标图像行步幅 |
| `oSizeROI` | ROI |
| `hgppStreamCtx` | 流上下文 |

##### 11.1.3.3. 函数列表
```c
// 8 位无符号。
HgppStatus hgppiDilate3x3_8u_C1R_Ctx(...)
HgppStatus hgppiDilate3x3_8u_C3R_Ctx(...)
HgppStatus hgppiDilate3x3_8u_C4R_Ctx(...)
HgppStatus hgppiDilate3x3_8u_AC4R_Ctx(...)  // 忽略 Alpha。

// 16 位无符号。
HgppStatus hgppiDilate3x3_16u_C1R_Ctx(...)
HgppStatus hgppiDilate3x3_16u_C3R_Ctx(...)
HgppStatus hgppiDilate3x3_16u_C4R_Ctx(...)
HgppStatus hgppiDilate3x3_16u_AC4R_Ctx(...)  // 忽略 Alpha。

// 32 位浮点。
HgppStatus hgppiDilate3x3_32f_C1R_Ctx(...)
HgppStatus hgppiDilate3x3_32f_C3R_Ctx(...)
HgppStatus hgppiDilate3x3_32f_C4R_Ctx(...)
HgppStatus hgppiDilate3x3_32f_AC4R_Ctx(...)  // 忽略 Alpha。

// 64 位浮点。
HgppStatus hgppiDilate3x3_64f_C1R_Ctx(...)  // 仅单通道。
```

#### 11.1.4. 带边界控制的 3x3 膨胀（Image Dilate 3x3 Border）
##### 11.1.4.1. 原理
使用 3x3 掩码进行膨胀，锚点位于中心像素，带边界控制。

如果掩码与源图像边界重叠，对落在源图像外的掩码像素应用边界类型操作。

> **注意：**
> `HGPP_BORDER_REPLICATE`。

##### 11.1.4.2. 函数列表
```c
// 8 位无符号。
HgppStatus hgppiDilate3x3Border_8u_C1R_Ctx(...)
HgppStatus hgppiDilate3x3Border_8u_C3R_Ctx(...)
HgppStatus hgppiDilate3x3Border_8u_C4R_Ctx(...)
HgppStatus hgppiDilate3x3Border_8u_AC4R_Ctx(...)

// 16 位无符号。
HgppStatus hgppiDilate3x3Border_16u_C1R_Ctx(...)
HgppStatus hgppiDilate3x3Border_16u_C3R_Ctx(...)
HgppStatus hgppiDilate3x3Border_16u_C4R_Ctx(...)
HgppStatus hgppiDilate3x3Border_16u_AC4R_Ctx(...)

// 32 位浮点。
HgppStatus hgppiDilate3x3Border_32f_C1R_Ctx(...)
HgppStatus hgppiDilate3x3Border_32f_C3R_Ctx(...)
HgppStatus hgppiDilate3x3Border_32f_C4R_Ctx(...)
HgppStatus hgppiDilate3x3Border_32f_AC4R_Ctx(...)
```

### 11.2. 腐蚀函数（Erosion Functions）
#### 11.2.1. 图像腐蚀（Image Erode）
##### 11.2.1.1. 腐蚀原理
腐蚀将输出像素计算为掩码下像素值的**最小值**。对应掩码值为零的像素不参与最小值搜索。

> **注意：**
> 用户有责任避免超出图像边界的采样。

##### 11.2.1.2. 通用参数
与膨胀函数相同（见 11.1.1.2 节“通用参数”）。

##### 11.2.1.3. 函数列表
```c
// 8 位无符号腐蚀。
HgppStatus hgppiErode_8u_C1R_Ctx(...)
HgppStatus hgppiErode_8u_C3R_Ctx(...)
HgppStatus hgppiErode_8u_C4R_Ctx(...)
HgppStatus hgppiErode_8u_AC4R_Ctx(...)  // 忽略 Alpha。

// 16 位无符号腐蚀。
HgppStatus hgppiErode_16u_C1R_Ctx(...)
HgppStatus hgppiErode_16u_C3R_Ctx(...)
HgppStatus hgppiErode_16u_C4R_Ctx(...)
HgppStatus hgppiErode_16u_AC4R_Ctx(...)  // 忽略 Alpha。

// 32 位浮点腐蚀。
HgppStatus hgppiErode_32f_C1R_Ctx(...)
HgppStatus hgppiErode_32f_C3R_Ctx(...)
HgppStatus hgppiErode_32f_C4R_Ctx(...)
HgppStatus hgppiErode_32f_AC4R_Ctx(...)  // 忽略 Alpha。
```

#### 11.2.2. 带边界控制的腐蚀（Image Erode Border）
##### 11.2.2.1. 原理
腐蚀计算输出像素为掩码下像素的最小值。对于灰度腐蚀，掩码包含有符号值，在确定最小值之前先加到对应源图像样本值上（钳位后）。

> **注意：**
> `HGPP_BORDER_REPLICATE`。

##### 11.2.2.2. 函数列表
```c
// 8 位无符号腐蚀（带边界）
HgppStatus hgppiErodeBorder_8u_C1R_Ctx(...)
HgppStatus hgppiErodeBorder_8u_C3R_Ctx(...)
HgppStatus hgppiErodeBorder_8u_C4R_Ctx(...)
HgppStatus hgppiErodeBorder_8u_AC4R_Ctx(...)

// 16 位无符号腐蚀（带边界）
HgppStatus hgppiErodeBorder_16u_C1R_Ctx(...)
HgppStatus hgppiErodeBorder_16u_C3R_Ctx(...)
HgppStatus hgppiErodeBorder_16u_C4R_Ctx(...)
HgppStatus hgppiErodeBorder_16u_AC4R_Ctx(...)

// 32 位浮点腐蚀（带边界）
HgppStatus hgppiErodeBorder_32f_C1R_Ctx(...)
HgppStatus hgppiErodeBorder_32f_C3R_Ctx(...)
HgppStatus hgppiErodeBorder_32f_C4R_Ctx(...)
HgppStatus hgppiErodeBorder_32f_AC4R_Ctx(...)

// 灰度腐蚀（带边界）
HgppStatus hgppiGrayErodeBorder_8u_C1R_Ctx(...)
HgppStatus hgppiGrayErodeBorder_32f_C1R_Ctx(...)
```

#### 11.2.3. 3x3 腐蚀（Image Erode 3x3）
##### 11.2.3.1. 原理
使用 3x3 掩码进行腐蚀，锚点位于中心像素。

##### 11.2.3.2. 函数列表
```c
// 8 位无符号。
HgppStatus hgppiErode3x3_8u_C1R_Ctx(...)
HgppStatus hgppiErode3x3_8u_C3R_Ctx(...)
HgppStatus hgppiErode3x3_8u_C4R_Ctx(...)
HgppStatus hgppiErode3x3_8u_AC4R_Ctx(...)

// 16 位无符号。
HgppStatus hgppiErode3x3_16u_C1R_Ctx(...)
HgppStatus hgppiErode3x3_16u_C3R_Ctx(...)
HgppStatus hgppiErode3x3_16u_C4R_Ctx(...)
HgppStatus hgppiErode3x3_16u_AC4R_Ctx(...)

// 32 位浮点。
HgppStatus hgppiErode3x3_32f_C1R_Ctx(...)
HgppStatus hgppiErode3x3_32f_C3R_Ctx(...)
HgppStatus hgppiErode3x3_32f_C4R_Ctx(...)
HgppStatus hgppiErode3x3_32f_AC4R_Ctx(...)

// 64 位浮点。
HgppStatus hgppiErode3x3_64f_C1R_Ctx(...)  // 仅单通道。
```

#### 11.2.4. 带边界控制的 3x3 腐蚀（Image Erode 3x3 Border）
##### 11.2.4.1. 函数列表
```c
// 8 位无符号。
HgppStatus hgppiErode3x3Border_8u_C1R_Ctx(...)
HgppStatus hgppiErode3x3Border_8u_C3R_Ctx(...)
HgppStatus hgppiErode3x3Border_8u_C4R_Ctx(...)
HgppStatus hgppiErode3x3Border_8u_AC4R_Ctx(...)

// 16 位无符号。
HgppStatus hgppiErode3x3Border_16u_C1R_Ctx(...)
HgppStatus hgppiErode3x3Border_16u_C3R_Ctx(...)
HgppStatus hgppiErode3x3Border_16u_C4R_Ctx(...)
HgppStatus hgppiErode3x3Border_16u_AC4R_Ctx(...)

// 32 位浮点。
HgppStatus hgppiErode3x3Border_32f_C1R_Ctx(...)
HgppStatus hgppiErode3x3Border_32f_C3R_Ctx(...)
HgppStatus hgppiErode3x3Border_32f_C4R_Ctx(...)
HgppStatus hgppiErode3x3Border_32f_AC4R_Ctx(...)
```

### 11.3. 复杂形态学操作
#### 11.3.1. 缓冲区大小计算
在调用任何 `MorphXXXBorder` 函数之前，应用程序需要先调用对应的 `MorphGetBufferSize` 函数来确定需要分配多少设备内存作为工作缓冲区。

##### 11.3.1.1. 通用参数
| 参数 | 说明 |
|------|------|
| `oSizeROI` | ROI |
| `hpBufferSize` | 所需缓冲区大小（字节） |

##### 11.3.1.2. 函数列表
```c
HgppStatus hgppiMorphGetBufferSize_8u_C1R(...)   // 8 位单通道。
HgppStatus hgppiMorphGetBufferSize_8u_C3R(...)   // 8 位三通道。
HgppStatus hgppiMorphGetBufferSize_8u_C4R(...)   // 8 位四通道。
HgppStatus hgppiMorphGetBufferSize_16u_C1R(...)  // 16 位无符号单通道。
HgppStatus hgppiMorphGetBufferSize_16s_C1R(...)  // 16 位有符号单通道。
HgppStatus hgppiMorphGetBufferSize_32f_C1R(...)  // 32 位浮点单通道。
HgppStatus hgppiMorphGetBufferSize_32f_C3R(...)  // 32 位浮点三通道。
HgppStatus hgppiMorphGetBufferSize_32f_C4R(...)  // 32 位浮点四通道。
```

#### 11.3.2. 形态学闭运算（Morph Close Border）
##### 11.3.2.1. 原理
**膨胀后跟腐蚀**，带边界控制。

形态学闭运算计算：
1. 第一遍：输出像素为掩码下像素的最大值（膨胀）。
2. 第二遍：使用第一遍结果作为输入，输出掩码下像素的最小值（腐蚀）。

对应掩码值为零的像素不参与最大值或最小值搜索。

> **注意：**
> `HGPP_BORDER_REPLICATE`。

##### 11.3.2.2. 通用参数
| 参数 | 说明 |
|------|------|
| `pSrc` | 源图像指针 |
| `nSrcStep` | 源图像行步幅 |
| `oSrcSize` | 源图像尺寸 |
| `oSrcOffset` | 源图像偏移 |
| `pDst` | 目标图像指针 |
| `nDstStep` | 目标图像行步幅 |
| `oSizeROI` | ROI |
| `pMask` | 掩码指针 |
| `oMaskSize` | 掩码尺寸 |
| `oAnchor` | 锚点 |
| `pBuffer` | 设备内存 scratch 缓冲区指针（大小至少为对应 MorphGetBufferSize 返回值） |
| `eBorderType` | 边界类型 |
| `hgppStreamCtx` | 流上下文 |

##### 11.3.2.3. 函数列表
```c
// 8 位无符号。
HgppStatus hgppiMorphCloseBorder_8u_C1R_Ctx(...)
HgppStatus hgppiMorphCloseBorder_8u_C3R_Ctx(...)
HgppStatus hgppiMorphCloseBorder_8u_C4R_Ctx(...)

// 16 位。
HgppStatus hgppiMorphCloseBorder_16u_C1R_Ctx(...)  // 无符号。
HgppStatus hgppiMorphCloseBorder_16s_C1R_Ctx(...)  // 有符号。

// 32 位浮点。
HgppStatus hgppiMorphCloseBorder_32f_C1R_Ctx(...)
HgppStatus hgppiMorphCloseBorder_32f_C3R_Ctx(...)
HgppStatus hgppiMorphCloseBorder_32f_C4R_Ctx(...)
```

#### 11.3.3. 形态学开运算（Morph Open Border）
##### 11.3.3.1. 原理
**腐蚀后跟膨胀**，带边界控制。

形态学开运算计算：
1. 第一遍：输出像素为掩码下像素的最小值（腐蚀）。
2. 第二遍：使用第一遍结果作为输入，输出掩码下像素的最大值（膨胀）。

##### 11.3.3.2. 函数列表
```c
// 8 位无符号。
HgppStatus hgppiMorphOpenBorder_8u_C1R_Ctx(...)
HgppStatus hgppiMorphOpenBorder_8u_C3R_Ctx(...)
HgppStatus hgppiMorphOpenBorder_8u_C4R_Ctx(...)

// 16 位。
HgppStatus hgppiMorphOpenBorder_16u_C1R_Ctx(...)  // 无符号。
HgppStatus hgppiMorphOpenBorder_16s_C1R_Ctx(...)  // 有符号。

// 32 位浮点。
HgppStatus hgppiMorphOpenBorder_32f_C1R_Ctx(...)
HgppStatus hgppiMorphOpenBorder_32f_C3R_Ctx(...)
HgppStatus hgppiMorphOpenBorder_32f_C4R_Ctx(...)
```

#### 11.3.4. 形态学顶帽变换（Morph Top Hat Border）
##### 11.3.4.1. 原理
**源像素减去形态学开运算结果**，带边界控制。

公式：
```text
输出 = 源像素 - 开运算结果
```

##### 11.3.4.2. 函数列表
```c
// 8 位无符号。
HgppStatus hgppiMorphTopHatBorder_8u_C1R_Ctx(...)
HgppStatus hgppiMorphTopHatBorder_8u_C3R_Ctx(...)
HgppStatus hgppiMorphTopHatBorder_8u_C4R_Ctx(...)

// 16 位。
HgppStatus hgppiMorphTopHatBorder_16u_C1R_Ctx(...)  // 无符号。
HgppStatus hgppiMorphTopHatBorder_16s_C1R_Ctx(...)  // 有符号。

// 32 位浮点。
HgppStatus hgppiMorphTopHatBorder_32f_C1R_Ctx(...)
HgppStatus hgppiMorphTopHatBorder_32f_C3R_Ctx(...)
HgppStatus hgppiMorphTopHatBorder_32f_C4R_Ctx(...)
```

#### 11.3.5. 形态学黑帽变换（Morph Black Hat Border）
##### 11.3.5.1. 原理
**形态学闭运算结果减去源像素**，带边界控制。

公式：
```text
输出 = 闭运算结果 - 源像素
```

##### 11.3.5.2. 函数列表
```c
// 8 位无符号。
HgppStatus hgppiMorphBlackHatBorder_8u_C1R_Ctx(...)
HgppStatus hgppiMorphBlackHatBorder_8u_C3R_Ctx(...)
HgppStatus hgppiMorphBlackHatBorder_8u_C4R_Ctx(...)

// 16 位。
HgppStatus hgppiMorphBlackHatBorder_16u_C1R_Ctx(...)  // 无符号。
HgppStatus hgppiMorphBlackHatBorder_16s_C1R_Ctx(...)  // 有符号。

// 32 位浮点。
HgppStatus hgppiMorphBlackHatBorder_32f_C1R_Ctx(...)
HgppStatus hgppiMorphBlackHatBorder_32f_C3R_Ctx(...)
HgppStatus hgppiMorphBlackHatBorder_32f_C4R_Ctx(...)
```

#### 11.3.6. 形态学梯度（Morph Gradient Border）
##### 11.3.6.1. 原理
**膨胀结果减去腐蚀结果**，带边界控制。

公式：
```text
输出 = 膨胀结果 - 腐蚀结果
```

##### 11.3.6.2. 函数列表
```c
// 8 位无符号。
HgppStatus hgppiMorphGradientBorder_8u_C1R_Ctx(...)
HgppStatus hgppiMorphGradientBorder_8u_C3R_Ctx(...)
HgppStatus hgppiMorphGradientBorder_8u_C4R_Ctx(...)

// 16 位。
HgppStatus hgppiMorphGradientBorder_16u_C1R_Ctx(...)  // 无符号。
HgppStatus hgppiMorphGradientBorder_16s_C1R_Ctx(...)  // 有符号。

// 32 位浮点。
HgppStatus hgppiMorphGradientBorder_32f_C1R_Ctx(...)
HgppStatus hgppiMorphGradientBorder_32f_C3R_Ctx(...)
HgppStatus hgppiMorphGradientBorder_32f_C4R_Ctx(...)
```

### 11.4. 附录：错误码
#### 11.4.1. 图像数据相关错误码
- `HGPP_STEP_ERROR`：步幅为 0 或负数
- `HGPP_NOT_EVEN_STEP_ERROR`： 2 和 4 通道图像的行步幅不是像素大小的倍数
- `HGPP_NULL_POINTER_ERROR`：图像数据指针为 NULL
- `HGPP_ALIGNMENT_ERROR`：图像数据指针地址不是像素大小的倍数

#### 11.4.2. ROI 相关错误码
- `HGPP_SIZE_ERROR`： ROI 宽度或高度为负数
- `HGPP_STEP_ERROR`： ROI 宽度超过图像行步幅。

## 12. 统计函数
用于计算图像统计特性的接口。

某些统计接口在计算过程中需要 scratch 缓冲区。

这些函数位于 `hgppist` 库中。
同类函数没有全部列出，完整函数定义请参考头文件 `hgppist.h`。

### 12.1. 求和
**求和（Sum）** 是最基本的图像统计运算，计算图像 ROI 区域内所有像素值的总和。

**运算公式：**

$$
\text{Sum} = \sum_{y=0}^{H-1} \sum_{x=0}^{W-1} I(x, y)
$$

其中 $H$ 和 $W$ 分别是 ROI 的高度和宽度。

**应用说明：**
- 用于计算图像总亮度。
- 作为其他统计量（如均值）的基础。
- 多通道图像返回每个通道的独立求和结果。
- 数据类型： 8u/16u/16s 输入 → 64f 或 64s 输出（防止溢出）。

#### 12.1.1. 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | 源图像指针 |
| `nSrcStep` | int | [in] | 源图像行步幅（字节） |
| `pSum` / `aSum[]` | 设备指针 | [out] | 求和结果（单通道用 pSum，多通道用 aSum 数组） |
| `oSizeROI` | HgppiSize | [in] | 感兴趣区域（宽度和高度） |
| `pDeviceBuffer` | 设备指针 | [in] | 临时缓冲区（需要预先分配） |
| `hgppStreamCtx` | HgppStreamContext | [in] | 流上下文 |

> **注意：**
> - 需要预先调用 `GetBufferHostSize` 获取缓冲区大小。
> - 多通道结果存储在数组中：`aSum[0]` = 通道 0，`aSum[1]` = 通道 1，...
> - AC4 版本忽略 Alpha 通道，只计算 3 个颜色通道。
> - 整数版本（8u64s）返回整数结果，浮点版本（64f）返回浮点结果。

#### 12.1.2. 函数列表
##### 12.1.2.1. 8 位无符号整数
```c
// 单通道 - 结果为 64f。
HgppStatus hgppiSum_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, Hgpp64f *pSum,
                                HgppiSize oSizeROI, HGpp8u *pDeviceBuffer,
                                HgppStreamContext hgppStreamCtx)

// 单通道 - 结果为 64s（整数）
HgppStatus hgppiSum_8u64s_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, Hgpp64s *pSum,
                                   HgppiSize oSizeROI, HGpp8u *pDeviceBuffer,
                                   HgppStreamContext hgppStreamCtx)

// 三通道 - aSum[3]
HgppStatus hgppiSum_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep, Hgpp64f aSum[3],
                                HgppiSize oSizeROI, HGpp8u *pDeviceBuffer,
                                HgppStreamContext hgppStreamCtx)

// 四通道 - aSum[4]
HgppStatus hgppiSum_8u_C4R_Ctx(const HGpp8u *pSrc, int nSrcStep, Hgpp64f aSum[4],
                                HgppiSize oSizeROI, HGpp8u *pDeviceBuffer,
                                HgppStreamContext hgppStreamCtx)

// 四通道（忽略 Alpha）- aSum[3]
HgppStatus hgppiSum_8u_AC4R_Ctx(const HGpp8u *pSrc, int nSrcStep, Hgpp64f aSum[3],
                                 HgppiSize oSizeROI, HGpp8u *pDeviceBuffer,
                                 HgppStreamContext hgppStreamCtx)
```

##### 12.1.2.2. 16 位无符号/有符号整数
```c
// 16 位无符号 - 结果为 64f。
HgppStatus hgppiSum_16u_C1R_Ctx(const Hgpp16u *pSrc, int nSrcStep, Hgpp64f *pSum, ...)
HgppStatus hgppiSum_16u_C3R_Ctx(...)  // aSum[3]
HgppStatus hgppiSum_16u_C4R_Ctx(...)  // aSum[4]
HgppStatus hgppiSum_16u_AC4R_Ctx(...)  // aSum[3]

// 16 位有符号 - 结果为 64f。
HgppStatus hgppiSum_16s_C1R_Ctx(const Hgpp16s *pSrc, int nSrcStep, Hgpp64f *pSum, ...)
HgppStatus hgppiSum_16s_C3R_Ctx(...)  // aSum[3]
HgppStatus hgppiSum_16s_C4R_Ctx(...)  // aSum[4]
HgppStatus hgppiSum_16s_AC4R_Ctx(...)  // aSum[3]
```

##### 12.1.2.3. 32 位浮点数
```c
// 32 位浮点 - 结果为 32f。
HgppStatus hgppiSum_32f_C1R_Ctx(const Hgpp32f *pSrc, int nSrcStep, Hgpp32f *pSum, ...)
HgppStatus hgppiSum_32f_C3R_Ctx(...)  // aSum[3]
HgppStatus hgppiSum_32f_C4R_Ctx(...)  // aSum[4]
HgppStatus hgppiSum_32f_AC4R_Ctx(...)  // aSum[3]
```

> **注意：**
> 本章仅列出常用的 Sum 函数变体。完整的 Sum 函数还包括：
> - 更多数据类型： 64s、 64f 等
> - 更多通道组合： C2、 P3 （Planar 格式）等
> - 设备常量版本： SumDeviceC 等

**请参考头文件 `hgppist.h` 获取完整的函数列表。**

##### 12.1.2.4. GetBufferHostSize （获取缓冲区大小）

> **提示：**
> 调用 Sum 函数前必须先调用 GetBufferHostSize 获取所需的临时缓冲区大小。

```c
// 8 位无符号单通道。
HgppStatus hgppiSumGetBufferHostSize_8u_C1R_Ctx(HgppiSize oSizeROI, size_t *hpBufferSize)
HgppStatus hgppiSumGetBufferHostSize_8u64s_C1R_Ctx(HgppiSize oSizeROI, size_t *hpBufferSize)

// 8 位无符号三通道。
HgppStatus hgppiSumGetBufferHostSize_8u_C3R_Ctx(HgppiSize oSizeROI, size_t *hpBufferSize)

// 8 位无符号四通道。
HgppStatus hgppiSumGetBufferHostSize_8u_C4R_Ctx(HgppiSize oSizeROI, size_t *hpBufferSize)
HgppStatus hgppiSumGetBufferHostSize_8u64s_C4R_Ctx(HgppiSize oSizeROI, size_t *hpBufferSize)

// 8 位无符号四通道（忽略 Alpha）
HgppStatus hgppiSumGetBufferHostSize_8u_AC4R_Ctx(HgppiSize oSizeROI, size_t *hpBufferSize)

// 16 位无符号。
HgppStatus hgppiSumGetBufferHostSize_16u_C1R_Ctx(HgppiSize oSizeROI, size_t *hpBufferSize)
HgppStatus hgppiSumGetBufferHostSize_16u_C3R_Ctx(...)
HgppStatus hgppiSumGetBufferHostSize_16u_C4R_Ctx(...)
HgppStatus hgppiSumGetBufferHostSize_16u_AC4R_Ctx(...)

// 16 位有符号。
HgppStatus hgppiSumGetBufferHostSize_16s_C1R_Ctx(HgppiSize oSizeROI, size_t *hpBufferSize)
HgppStatus hgppiSumGetBufferHostSize_16s_C3R_Ctx(...)
HgppStatus hgppiSumGetBufferHostSize_16s_C4R_Ctx(...)
HgppStatus hgppiSumGetBufferHostSize_16s_AC4R_Ctx(...)

// 32 位浮点。
HgppStatus hgppiSumGetBufferHostSize_32f_C1R_Ctx(HgppiSize oSizeROI, size_t *hpBufferSize)
HgppStatus hgppiSumGetBufferHostSize_32f_C3R_Ctx(...)
HgppStatus hgppiSumGetBufferHostSize_32f_C4R_Ctx(...)
HgppStatus hgppiSumGetBufferHostSize_32f_AC4R_Ctx(...)
```

**使用示例：**

```c
// 1. 先获取缓冲区大小。
size_t nBufferSize;
hgppiSumGetBufferHostSize_8u_C1R_Ctx(oSizeROI, &nBufferSize);

// 2. 分配设备缓冲区。
HGpp8u *pDeviceBuffer;
hggcMalloc(&pDeviceBuffer, nBufferSize);

// 3. 调用 Sum 函数。
Hgpp64f nSum;
hgppiSum_8u_C1R_Ctx(pSrc, nSrcStep, &nSum, oSizeROI, pDeviceBuffer, hgppStreamCtx);

// 4. 释放缓冲区。
hggcFree(pDeviceBuffer);
```

### 12.2. 最小值
查找图像 ROI 区域内的最小像素值，可选返回最小值的位置坐标。

**运算公式：**

$$
\text{Min} = \min_{x,y} I(x, y)
$$

**最小值索引：**

$$
(x_{min}, y_{min}) = \arg\min_{x,y} I(x, y)
$$

**应用说明：**
- 用于查找图像暗区域。
- 索引版本返回最小值在 ROI 中的相对位置。
- 多通道图像返回每个通道的最小值。
- 常用于图像增强、阈值计算等预处理。

#### 12.2.1. 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | 源图像指针 |
| `nSrcStep` | int | [in] | 源图像行步幅 |
| `pMin` / `aMin[]` | 设备指针 | [out] | 最小值（单通道用 pMin，多通道用 aMin 数组） |
| `pMinIndex` | 设备指针 | [out] | 最小值位置（x, y 坐标，可选） |
| `oSizeROI` | HgppiSize | [in] | 感兴趣区域 |
| `pDeviceBuffer` | 设备指针 | [in] | 临时缓冲区 |
| `hgppStreamCtx` | HgppStreamContext | [in] | 流上下文 |

> **注意：**
> - 多通道图像返回每个通道的最小值。
> - 索引版本返回最小值的位置坐标（相对于 ROI 左上角）。
> - 需要预先分配临时缓冲区。
> - 如果有多个相同的最小值，返回第一个找到的位置。

#### 12.2.2. 函数列表
##### 12.2.2.1. 8 位无符号整数
```c
// 单通道。
HgppStatus hgppiMin_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pMin,
                                HgppiSize oSizeROI, HGpp8u *pDeviceBuffer,
                                HgppStreamContext hgppStreamCtx)

// 单通道（带索引）
HgppStatus hgppiMinIndex_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pMin,
                                     HgppiPoint *pMinIndex, HgppiSize oSizeROI,
                                     HGpp8u *pDeviceBuffer, HgppStreamContext hgppStreamCtx)

// 三通道 - aMin[3]
HgppStatus hgppiMin_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u aMin[3],
                                HgppiSize oSizeROI, HGpp8u *pDeviceBuffer,
                                HgppStreamContext hgppStreamCtx)
```

##### 12.2.2.2. 16 位/32 位版本
```c
// 16 位无符号。
HgppStatus hgppiMin_16u_C1R_Ctx(...)
HgppStatus hgppiMinIndex_16u_C1R_Ctx(...)

// 32 位浮点。
HgppStatus hgppiMin_32f_C1R_Ctx(...)
HgppStatus hgppiMinIndex_32f_C1R_Ctx(...)
```

##### 12.2.2.3. GetBufferHostSize （获取缓冲区大小）
```c
// 8 位无符号单通道。
HgppStatus hgppiMinGetBufferHostSize_8u_C1R_Ctx(HgppiSize oSizeROI,
                                                 size_t *hpBufferSize)

// 8 位无符号单通道（带索引）
HgppStatus hgppiMinIndexGetBufferHostSize_8u_C1R_Ctx(HgppiSize oSizeROI,
                                                      size_t *hpBufferSize)

// 8 位无符号三通道。
HgppStatus hgppiMinGetBufferHostSize_8u_C3R_Ctx(HgppiSize oSizeROI,
                                                 size_t *hpBufferSize)

// 16 位/32 位版本。
HgppStatus hgppiMinGetBufferHostSize_16u_C1R_Ctx(...)
HgppStatus hgppiMinGetBufferHostSize_16s_C1R_Ctx(...)
HgppStatus hgppiMinGetBufferHostSize_32f_C1R_Ctx(...)
HgppStatus hgppiMinIndexGetBufferHostSize_16u_C1R_Ctx(...)
HgppStatus hgppiMinIndexGetBufferHostSize_16s_C1R_Ctx(...)
HgppStatus hgppiMinIndexGetBufferHostSize_32f_C1R_Ctx(...)
```

> **注意：**
> 本章仅列出常用的 Min 函数变体。完整的 Min 函数还包括：
> - 更多数据类型： 64s、 64f 等
> - 更多通道组合： C4、 AC4、 P3 （Planar 格式）等
> - 完整的 GetBufferHostSize 变体：每个数据类型和通道组合都有对应的版本。

**请参考头文件 `hgppist.h` 获取完整的函数列表。**

### 12.3. 最大值
查找图像 ROI 区域内的最大像素值，可选返回最大值的位置坐标。

**运算公式：**

$$
\text{Max} = \max_{x,y} I(x, y)
$$

**最大值索引：**

$$
(x_{max}, y_{max}) = \arg\max_{x,y} I(x, y)
$$

**应用说明：**
- 用于查找图像亮区域。
- 与最小值一起计算图像对比度。
- 索引版本返回最大值在 ROI 中的相对位置。
- 常用于自动曝光、动态范围调整等。

#### 12.3.1. 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | 源图像指针 |
| `nSrcStep` | int | [in] | 源图像行步幅 |
| `pMax` / `aMax[]` | 设备指针 | [out] | 最大值 |
| `pMaxIndex` | 设备指针 | [out] | 最大值位置（可选） |
| `oSizeROI` | HgppiSize | [in] | 感兴趣区域 |
| `pDeviceBuffer` | 设备指针 | [in] | 临时缓冲区 |
| `hgppStreamCtx` | HgppStreamContext | [in] | 流上下文 |

#### 12.3.2. 函数列表
##### 12.3.2.1. 8 位无符号整数
```c
// 单通道。
HgppStatus hgppiMax_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pMax,
                                HgppiSize oSizeROI, HGpp8u *pDeviceBuffer,
                                HgppStreamContext hgppStreamCtx)

// 单通道（带索引）
HgppStatus hgppiMaxIndex_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u *pMax,
                                     HgppiPoint *pMaxIndex, HgppiSize oSizeROI,
                                     HGpp8u *pDeviceBuffer, HgppStreamContext hgppStreamCtx)

// 三通道。
HgppStatus hgppiMax_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep, HGpp8u aMax[3],
                                HgppiSize oSizeROI, HGpp8u *pDeviceBuffer,
                                HgppStreamContext hgppStreamCtx)
```

##### 12.3.2.2. 16 位/32 位版本
```c
HgppStatus hgppiMax_16u_C1R_Ctx(...)
HgppStatus hgppiMaxIndex_16u_C1R_Ctx(...)
HgppStatus hgppiMax_32f_C1R_Ctx(...)
HgppStatus hgppiMaxIndex_32f_C1R_Ctx(...)
```

##### 12.3.2.3. GetBufferHostSize （获取缓冲区大小）
```c
// 8 位无符号单通道。
HgppStatus hgppiMaxGetBufferHostSize_8u_C1R_Ctx(HgppiSize oSizeROI,
                                                 size_t *hpBufferSize)

// 8 位无符号单通道（带索引）
HgppStatus hgppiMaxIndexGetBufferHostSize_8u_C1R_Ctx(HgppiSize oSizeROI,
                                                      size_t *hpBufferSize)

// 8 位无符号三通道。
HgppStatus hgppiMaxGetBufferHostSize_8u_C3R_Ctx(HgppiSize oSizeROI,
                                                 size_t *hpBufferSize)

// 16 位/32 位版本。
HgppStatus hgppiMaxGetBufferHostSize_16u_C1R_Ctx(...)
HgppStatus hgppiMaxGetBufferHostSize_16s_C1R_Ctx(...)
HgppStatus hgppiMaxGetBufferHostSize_32f_C1R_Ctx(...)
HgppStatus hgppiMaxIndexGetBufferHostSize_16u_C1R_Ctx(...)
HgppStatus hgppiMaxIndexGetBufferHostSize_16s_C1R_Ctx(...)
HgppStatus hgppiMaxIndexGetBufferHostSize_32f_C1R_Ctx(...)
```

### 12.4. 最小值/最大值
同时计算图像 ROI 区域的最小值和最大值。

**运算公式：**

$$
\text{MinMax} = (\min_{x,y} I(x, y), \max_{x,y} I(x, y))
$$

**应用说明：**
- 单次遍历同时获得两个值，比分别调用 Min 和 Max 更高效。
- 用于快速计算图像动态范围。
- 可选返回最小值和最大值的位置坐标。
- 常用于自动对比度增强、直方图拉伸等。

#### 12.4.1. 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | 源图像指针 |
| `nSrcStep` | int | [in] | 源图像行步幅 |
| `pMin` / `aMin[]` | 设备指针 | [out] | 最小值 |
| `pMax` / `aMax[]` | 设备指针 | [out] | 最大值 |
| `pMinIndex` | 设备指针 | [out] | 最小值位置（可选） |
| `pMaxIndex` | 设备指针 | [out] | 最大值位置（可选） |
| `oSizeROI` | HgppiSize | [in] | 感兴趣区域 |
| `pDeviceBuffer` | 设备指针 | [in] | 临时缓冲区 |
| `hgppStreamCtx` | HgppStreamContext | [in] | 流上下文 |

#### 12.4.2. 函数列表
```c
// 8 位无符号单通道。
HgppStatus hgppiMinMax_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                   HGpp8u *pMin, HGpp8u *pMax,
                                   HgppiSize oSizeROI, HGpp8u *pDeviceBuffer,
                                   HgppStreamContext hgppStreamCtx)

// 8 位无符号单通道（带索引）
HgppStatus hgppiMinMaxIndex_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                        HGpp8u *pMin, HgppiPoint *pMinIndex,
                                        HGpp8u *pMax, HgppiPoint *pMaxIndex,
                                        HgppiSize oSizeROI, HGpp8u *pDeviceBuffer,
                                        HgppStreamContext hgppStreamCtx)

// 16 位/32 位版本。
HgppStatus hgppiMinMax_16u_C1R_Ctx(...)
HgppStatus hgppiMinMax_32f_C1R_Ctx(...)
```

##### 12.4.2.1. GetBufferHostSize （获取缓冲区大小）
```c
// 8 位无符号单通道。
HgppStatus hgppiMinMaxGetBufferHostSize_8u_C1R_Ctx(HgppiSize oSizeROI,
                                                    size_t *hpBufferSize)

// 8 位无符号单通道（带索引）
HgppStatus hgppiMinMaxIndexGetBufferHostSize_8u_C1R_Ctx(HgppiSize oSizeROI,
                                                         size_t *hpBufferSize)

// 16 位/32 位版本。
HgppStatus hgppiMinMaxGetBufferHostSize_16u_C1R_Ctx(...)
HgppStatus hgppiMinMaxGetBufferHostSize_32f_C1R_Ctx(...)
```

### 12.5. 均值/标准差
计算图像 ROI 区域内像素值的算术平均值，反映图像的平均亮度水平。

**运算公式：**

$$
\mu = \frac{1}{N} \sum_{y=0}^{H-1} \sum_{x=0}^{W-1} I(x, y)
$$

其中 $N = W \times H$ 是像素总数。

**标准差（Standard Deviation）** 衡量像素值相对于均值的离散程度，反映图像的对比度。

**运算公式：**

$$
\sigma = \sqrt{\frac{1}{N} \sum_{y=0}^{H-1} \sum_{x=0}^{W-1} (I(x, y) - \mu)^2}
$$

**优化计算公式（单次遍历）：**

$$
\sigma = \sqrt{\frac{1}{N} \sum_{x,y} I(x, y)^2 - \mu^2}
$$

**应用说明：**
- 均值反映图像平均亮度
- 标准差反映图像对比度（标准差大 = 对比度高）
- 通常一起计算（更高效）。
- 多通道返回每个通道的统计值。
- 用于图像质量评估、自动曝光控制等。

#### 12.5.1. 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | 源图像指针 |
| `nSrcStep` | int | [in] | 源图像行步幅 |
| `pMean` / `aMean[]` | 设备指针 | [out] | 均值（64f） |
| `pStdDev` / `aStdDev[]` | 设备指针 | [out] | 标准差（64f） |
| `oSizeROI` | HgppiSize | [in] | 感兴趣区域 |
| `pDeviceBuffer` | 设备指针 | [in] | 临时缓冲区 |
| `hgppStreamCtx` | HgppStreamContext | [in] | 流上下文 |

> **注意：**
> - 均值和标准差通常一起计算（更高效）。
> - 多通道返回每个通道的统计值。
> - 需要临时缓冲区。
> - 结果为 64f 浮点数（保证精度）

#### 12.5.2. 函数列表
##### 12.5.2.1. Mean （均值）
```c
// 8 位无符号。
HgppStatus hgppiMean_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, Hgpp64f *pMean,
                                 HgppiSize oSizeROI, HGpp8u *pDeviceBuffer,
                                 HgppStreamContext hgppStreamCtx)

HgppStatus hgppiMean_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep, Hgpp64f aMean[3],
                                 HgppiSize oSizeROI, HGpp8u *pDeviceBuffer,
                                 HgppStreamContext hgppStreamCtx)

HgppStatus hgppiMean_8u_AC4R_Ctx(...)  // 忽略 Alpha。

// 16 位/32 位版本。
HgppStatus hgppiMean_16u_C1R_Ctx(...)
HgppStatus hgppiMean_32f_C1R_Ctx(...)
```

> **注意：**
> 本章仅列出常用的 Mean/StdDev 函数变体。完整的 Mean/StdDev 函数还包括：
> - 更多数据类型： 16s、 64s、 64f 等
> - 更多通道组合： C4、 P3 （Planar 格式）等
> - Mean_StdDev 完整版本：所有数据类型和通道组合。
> - 完整的 GetBufferHostSize 变体

**请参考头文件 `hgppist.h` 获取完整的函数列表。**

##### 12.5.2.2. StandardDeviation （标准差）
```c
HgppStatus hgppiStandardDeviation_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                              Hgpp64f *pStdDev,
                                              HgppiSize oSizeROI,
                                              HGpp8u *pDeviceBuffer,
                                              HgppStreamContext hgppStreamCtx)

HgppStatus hgppiStandardDeviation_16u_C1R_Ctx(...)
HgppStatus hgppiStandardDeviation_32f_C1R_Ctx(...)
```

##### 12.5.2.3. Mean_StdDev （均值和标准差）
```c
// 8 位无符号。
HgppStatus hgppiMean_StdDev_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                        Hgpp64f *pMean, Hgpp64f *pStdDev,
                                        HgppiSize oSizeROI, HGpp8u *pDeviceBuffer,
                                        HgppStreamContext hgppStreamCtx)

HgppStatus hgppiMean_StdDev_8u_C3R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                        Hgpp64f aMean[3], Hgpp64f aStdDev[3],
                                        HgppiSize oSizeROI, HGpp8u *pDeviceBuffer,
                                        HgppStreamContext hgppStreamCtx)

// 16 位/32 位版本。
HgppStatus hgppiMean_StdDev_16u_C1R_Ctx(...)
HgppStatus hgppiMean_StdDev_32f_C1R_Ctx(...)
```

### 12.6. 范数
范数（Norm）是向量或矩阵大小的度量，在图像处理中用于衡量图像的能量或幅度。

**L1 范数（曼哈顿范数）：** 所有像素绝对值之和。

$$
||I||_1 = \sum_{y=0}^{H-1} \sum_{x=0}^{W-1} |I(x, y)|
$$

**L2 范数（欧几里得范数）：** 像素值平方和的平方根，表示图像的总能量。

$$
||I||_2 = \sqrt{\sum_{y=0}^{H-1} \sum_{x=0}^{W-1} I(x, y)^2}
$$

**L∞ 范数（最大范数）：** 像素绝对值的最大值。

$$
||I||_\infty = \max_{x,y} |I(x, y)|
$$

**范数比值（NormRel）：** 两个图像的相对差异。

$$
\text{NormRel}(I_1, I_2) = \frac{||I_1 - I_2||}{||I_2||}
$$

**范数差（NormDiff）：** 两个图像的绝对差异。

$$
\text{NormDiff}(I_1, I_2) = ||I_1 - I_2||
$$

**应用说明：**
- L1 范数：稀疏性度量、压缩感知
- L2 范数：能量计算、信号处理。
- L∞ 范数：峰值检测、误差界限。
- 范数比值：图像相似度评估
- 范数差：图像差异度量

#### 12.6.1. 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | 源图像指针 |
| `nSrcStep` | int | [in] | 源图像行步幅 |
| `pNorm` | 设备指针 | [out] | 范数结果（64f） |
| `oSizeROI` | HgppiSize | [in] | 感兴趣区域 |
| `eNorm` | HgppiNorm | [in] | 范数类型（HGPP_NORM_L1/L2/INF） |
| `pDeviceBuffer` | 设备指针 | [in] | 临时缓冲区 |
| `hgppStreamCtx` | HgppStreamContext | [in] | 流上下文 |

#### 12.6.2. 函数列表
```c
// 8 位无符号。
HgppStatus hgppiNorm_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep, Hgpp64f *pNorm,
                                 HgppiSize oSizeROI, HgppiNorm eNorm,
                                 HGpp8u *pDeviceBuffer, HgppStreamContext hgppStreamCtx)

// 16 位/32 位版本。
HgppStatus hgppiNorm_16u_C1R_Ctx(...)
HgppStatus hgppiNorm_32f_C1R_Ctx(...)
```

##### 12.6.2.1. GetBufferHostSize （获取缓冲区大小）
```c
// 8 位无符号单通道。
HgppStatus hgppiNormGetBufferHostSize_8u_C1R_Ctx(HgppiSize oSizeROI,
                                                  size_t *hpBufferSize)

// 16 位/32 位版本。
HgppStatus hgppiNormGetBufferHostSize_16u_C1R_Ctx(...)
HgppStatus hgppiNormGetBufferHostSize_32f_C1R_Ctx(...)

// NormRel（范数比值）
HgppStatus hgppiNormRelGetBufferHostSize_8u_C1R_Ctx(...)
HgppStatus hgppiNormRelGetBufferHostSize_16u_C1R_Ctx(...)
HgppStatus hgppiNormRelGetBufferHostSize_32f_C1R_Ctx(...)

// NormDiff（范数差）
HgppStatus hgppiNormDiffGetBufferHostSize_8u_C1R_Ctx(...)
HgppStatus hgppiNormDiffGetBufferHostSize_16u_C1R_Ctx(...)
HgppStatus hgppiNormDiffGetBufferHostSize_32f_C1R_Ctx(...)
```

> **注意：**
> 本章仅列出常用的 Norm 函数变体。完整的 Norm 函数系列包括：
> - **Norm （范数）**： 73 个函数（L1/L2/Inf， 8u/16u/16s/32f， C1/C3/C4/AC4 等）
> - **NormRel （范数比值）**： 72 个函数（两图像相对差异）
> - **NormDiff （范数差）**： 72 个函数（两图像绝对差异）
> - 完整的 GetBufferHostSize 变体（70+ 个）

**请参考头文件 `hgppist.h` 获取完整的函数列表。**

### 12.7. 点积
点积（Dot Product）计算两个图像对应像素乘积的和，是向量内积在图像上的扩展。

**运算公式：**

$$
I_1 \cdot I_2 = \sum_{y=0}^{H-1} \sum_{x=0}^{W-1} I_1(x, y) \cdot I_2(x, y)
$$

**应用说明：**
- **相似度计算**：点积越大，两图像越相似
- **投影运算**：将图像投影到特定方向
- **相关性分析**：衡量两图像的线性相关性
- **模板匹配**：计算模板与图像的匹配程度。
- 结果为 64f 浮点数（保证精度）

#### 12.7.1. 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc1` | 设备指针 | [in] | 第一个源图像 |
| `nSrc1Step` | int | [in] | 源图像 1 行步幅 |
| `pSrc2` | 设备指针 | [in] | 第二个源图像 |
| `nSrc2Step` | int | [in] | 源图像 2 行步幅 |
| `pDotProd` | 设备指针 | [out] | 点积结果（64f） |
| `oSizeROI` | HgppiSize | [in] | 感兴趣区域 |
| `pDeviceBuffer` | 设备指针 | [in] | 临时缓冲区 |
| `hgppStreamCtx` | HgppStreamContext | [in] | 流上下文 |

#### 12.7.2. 函数列表
```c
// 8 位无符号（结果为 64f）
HgppStatus hgppiDotProd_8u_64f_C1R_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                        const HGpp8u *pSrc2, int nSrc2Step,
                                        Hgpp64f *pDotProd, HgppiSize oSizeROI,
                                        HGpp8u *pDeviceBuffer,
                                        HgppStreamContext hgppStreamCtx)

// 16 位/32 位版本。
HgppStatus hgppiDotProd_16u_64f_C1R_Ctx(...)
HgppStatus hgppiDotProd_32f_C1R_Ctx(...)
```

> **注意：**
> 本章仅列出常用的 DotProd 函数变体。完整的 DotProd 函数还包括：
> - 更多数据类型组合： 8u_32f、 16s_64f、 32s_64f 等。
> - 更多通道组合： C3、 C4、 AC4 等
> - 完整的 GetBufferHostSize 变体（28 个）

**请参考头文件 `hgppist.h` 获取完整的函数列表。**

### 12.8. 范围内计数
范围内计数（Count In Range）统计图像 ROI 区域内像素值在指定范围内的像素数量。

**运算公式：**

$$
\text{Count} = \sum_{y=0}^{H-1} \sum_{x=0}^{W-1} [\text{low} \leq I(x, y) \leq \text{high}]
$$

其中 $[condition]$ 是指示函数（条件为真时值为 1，否则为 0）。

**应用说明：**
- 统计特定亮度范围的像素数量。
- 直方图分析的替代方法
- 阈值分割效果评估
- 图像质量分析（如过曝/欠曝像素统计）
- 结果为 64s 整数（可处理大图像）

#### 12.8.1. 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | 源图像指针 |
| `nSrcStep` | int | [in] | 源图像行步幅 |
| `pCount` | 设备指针 | [out] | 计数结果（64s） |
| `nLowerBound` | 数据类型 | [in] | 下界 |
| `nUpperBound` | 数据类型 | [in] | 上界 |
| `oSizeROI` | HgppiSize | [in] | 感兴趣区域 |
| `hgppStreamCtx` | HgppStreamContext | [in] | 流上下文 |

#### 12.8.2. 函数列表
```c
// 8 位无符号。
HgppStatus hgppiCountInRange_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                         Hgpp64s *pCount,
                                         HGpp8u nLowerBound, HGpp8u nUpperBound,
                                         HgppiSize oSizeROI,
                                         HgppStreamContext hgppStreamCtx)

// 16 位/32 位版本。
HgppStatus hgppiCountInRange_16u_C1R_Ctx(...)
HgppStatus hgppiCountInRange_32f_C1R_Ctx(...)
```

##### 12.8.2.1. GetBufferHostSize （获取缓冲区大小）
```c
// 8 位无符号单通道。
HgppStatus hgppiCountInRangeGetBufferHostSize_8u_C1R_Ctx(HgppiSize oSizeROI,
                                                          size_t *hpBufferSize)

// 16 位/32 位版本。
HgppStatus hgppiCountInRangeGetBufferHostSize_16u_C1R_Ctx(...)
HgppStatus hgppiCountInRangeGetBufferHostSize_32f_C1R_Ctx(...)
```

### 12.9. 逐元素极值
逐元素最小值（MinEvery） 和 逐元素最大值（MaxEvery）对两个图像的对应像素进行逐点比较，返回每个位置的最小值或最大值。

**逐元素最小值：**

$$
\text{dst}(x, y) = \min(I_1(x, y), I_2(x, y))
$$

**逐元素最大值：**

$$
\text{dst}(x, y) = \max(I_1(x, y), I_2(x, y))
$$

**应用说明：**
- 图像融合（取最亮/最暗部分）
- 多曝光图像合成
- 形态学操作的基础
- 异常值去除
- 两幅图像必须具有相同的尺寸和 ROI。

#### 12.9.1. 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc1` | 设备指针 | [in] | 第一个源图像 |
| `nSrc1Step` | int | [in] | 源图像 1 行步幅 |
| `pSrc2` | 设备指针 | [in] | 第二个源图像 |
| `nSrc2Step` | int | [in] | 源图像 2 行步幅 |
| `pDst` | 设备指针 | [out] | 目标图像 |
| `nDstStep` | int | [in] | 目标图像行步幅 |
| `oSizeROI` | HgppiSize | [in] | 感兴趣区域 |
| `hgppStreamCtx` | HgppStreamContext | [in] | 流上下文 |

#### 12.9.2. 函数列表
```c
// 8 位无符号。
HgppStatus hgppiMinEvery_8u_C1R_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                     const HGpp8u *pSrc2, int nSrc2Step,
                                     HGpp8u *pDst, int nDstStep,
                                     HgppiSize oSizeROI,
                                     HgppStreamContext hgppStreamCtx)

HgppStatus hgppiMaxEvery_8u_C1R_Ctx(...)

// 16 位/32 位版本。
HgppStatus hgppiMinEvery_16u_C1R_Ctx(...)
HgppStatus hgppiMaxEvery_32f_C1R_Ctx(...)
```

### 12.10. 积分图
积分图（Integral Image）也称为累加和表，是一种快速计算图像任意矩形区域和的数据结构。

**定义：**

积分图在位置 $(x, y)$ 的值是原图像中所有左上角像素的和：

$$
II(x, y) = \sum_{y'=0}^{y} \sum_{x'=0}^{x} I(x', y')
$$

**递归计算（高效实现）：**

$$
II(x, y) = I(x, y) + II(x-1, y) + II(x, y-1) - II(x-1, y-1)
$$

**矩形区域和（O(1) 复杂度）：**

$$
\text{Sum}(x_1, y_1, x_2, y_2) = II(x_2, y_2) - II(x_1-1, y_2) - II(x_2, y_1-1) + II(x_1-1, y_1-1)
$$

**平方积分图（Square Integral）：**

$$
II_2(x, y) = \sum_{y'=0}^{y} \sum_{x'=0}^{x} I(x', y')^2
$$

用于快速计算方差：$\sigma^2 = \frac{II_2}{N} - \mu^2$

**应用说明：**
- **快速区域求和**：任意矩形区域 O(1) 复杂度
- **Haar 特征计算**：人脸检测等应用
- **快速均值/方差计算**：结合平方积分图
- **自适应阈值**：局部区域统计。
- 输出数据类型通常为 64s 或 64f （防止溢出）。
- 积分图通常比原图像大一个像素（顶部和左侧补 0）

#### 12.10.1. 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | 源图像指针 |
| `nSrcStep` | int | [in] | 源图像行步幅 |
| `pDst` | 设备指针 | [out] | 目标积分图（64s 或 64f） |
| `nDstStep` | int | [in] | 目标图像行步幅 |
| `oSizeROI` | HgppiSize | [in] | 感兴趣区域 |
| `hgppStreamCtx` | HgppStreamContext | [in] | 流上下文 |

> **注意：**
> - 积分图通常比原图像大一个像素（顶部和左侧补 0）
> - 输出数据类型通常为 64s 或 64f （防止溢出）。
> - 平方积分图用于快速计算方差。

#### 12.10.2. 函数列表
##### 12.10.2.1. Integral （积分图）
```c
// 8 位无符号 → 64 位有符号。
HgppStatus hgppiIntegral_8u_64s_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                         Hgpp64s *pDst, int nDstStep,
                                         HgppiSize oSizeROI,
                                         HgppStreamContext hgppStreamCtx)

// 16 位无符号 → 64 位有符号。
HgppStatus hgppiIntegral_16u_64s_C1R_Ctx(...)

// 32 位浮点 → 64 位浮点。
HgppStatus hgppiIntegral_32f_64f_C1R_Ctx(...)
```

##### 12.10.2.2. SquareIntegral （平方积分图）
```c
// 8 位无符号 → 64 位有符号（平方和）
HgppStatus hgppiSqrIntegral_8u_64s_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                            Hgpp64s *pDst, int nDstStep,
                                            HgppiSize oSizeROI,
                                            HgppStreamContext hgppStreamCtx)

// 32 位浮点 → 64 位浮点。
HgppStatus hgppiSqrIntegral_32f_64f_C1R_Ctx(...)
```

### 12.11. 直方图
直方图（Histogram）统计图像中每个灰度级（或颜色值）出现的频率，是图像分析的基础工具。

**定义：**

$$
H(k) = \sum_{y=0}^{H-1} \sum_{x=0}^{W-1} \delta(I(x, y) - k)
$$

其中 $\delta$ 是狄拉克δ函数（离散情况下为克罗内克δ）。

**等距直方图（Histogram Even）：**

将值域等分为 $n$ 个区间（bin）：

$$
\text{bin}_i = \{k \mid k_{min} + i \cdot \Delta \leq k < k_{min} + (i+1) \cdot \Delta\}
$$

其中 $\Delta = \frac{k_{max} - k_{min}}{n}$ 是每个 bin 的宽度。

**范围直方图（Histogram Range）：**

使用自定义的边界值数组：

$$
\text{bin}_i = \{k \mid \text{boundaries}[i] \leq k < \text{boundaries}[i+1]\}
$$

允许非均匀的 bin 分布，适用于特殊应用。

**应用说明：**
- **图像分析**：亮度分布、对比度评估
- **图像增强**：直方图均衡化、匹配。
- **图像分割**：阈值选择（如 Otsu 方法）。
- **特征提取**：颜色直方图、纹理分析
- `nLevels` 必须 ≥ 2
- Range 版本需要预先分配并初始化 `pLevels` 数组。
- 需要临时缓冲区。

#### 12.11.1. 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | 源图像指针 |
| `nSrcStep` | int | [in] | 源图像行步幅 |
| `pHistogram` | 设备指针 | [out] | 直方图数组（设备内存， 32s） |
| `nLevels` | int | [in] | 直方图级别数（bin 数量） |
| `nLowerBound` | 数据类型 | [in] | 下界（Even 版本） |
| `nUpperBound` | 数据类型 | [in] | 上界（Even 版本） |
| `pLevels` | 设备指针 | [in] | 边界值数组（Range 版本） |
| `oSizeROI` | HgppiSize | [in] | 感兴趣区域 |
| `pDeviceBuffer` | 设备指针 | [in] | 临时缓冲区 |
| `hgppStreamCtx` | HgppStreamContext | [in] | 流上下文 |

> **注意：**
> - `nLevels` 必须 ≥ 2
> - Range 版本需要预先分配并初始化 `pLevels` 数组。
> - 需要临时缓冲区。
> - 直方图数组大小为 `nLevels`

#### 12.11.2. 函数列表
##### 12.11.2.1. HistogramEven （等距直方图）
```c
// 8 位无符号。
HgppStatus hgppiHistogramEven_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                          Hgpp32s *pHistogram,
                                          int nLevels,
                                          HGpp8u nLowerBound, HGpp8u nUpperBound,
                                          HgppiSize oSizeROI,
                                          HGpp8u *pDeviceBuffer,
                                          HgppStreamContext hgppStreamCtx)

// 16 位/32 位版本。
HgppStatus hgppiHistogramEven_16u_C1R_Ctx(...)
HgppStatus hgppiHistogramEven_32f_C1R_Ctx(...)
```

##### 12.11.2.2. HistogramRange （范围直方图）
```c
// 8 位无符号。
HgppStatus hgppiHistogramRange_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                           Hgpp32s *pHistogram,
                                           int nLevels,
                                           const Hgpp32f *pLevels,
                                           HgppiSize oSizeROI,
                                           HGpp8u *pDeviceBuffer,
                                           HgppStreamContext hgppStreamCtx)

// 16 位/32 位版本。
HgppStatus hgppiHistogramRange_16u_C1R_Ctx(...)
HgppStatus hgppiHistogramRange_32f_C1R_Ctx(...)
```

### 12.12. 接近度
接近度（Proximity）计算图像中与指定参考值接近的像素，生成接近度图。

**运算公式：**

$$
\text{dst}(x, y) = \begin{cases} 255 & \text{if } |I(x, y) - \text{value}| \leq \text{tolerance} \\ 0 & \text{otherwise} \end{cases}
$$

**应用说明：**
- 颜色分割（提取特定颜色区域）
- 阈值分割的推广
- 目标检测（查找与模板接近的区域）
- 图像分析（统计特定亮度区域）
- 容差参数控制匹配的严格程度。

#### 12.12.1. 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc` | 设备指针 | [in] | 源图像指针 |
| `nSrcStep` | int | [in] | 源图像行步幅 |
| `pDst` | 设备指针 | [out] | 目标图像（接近度图， 0 或 255） |
| `nValue` | 数据类型 | [in] | 参考值 |
| `nTolerance` | 数据类型 | [in] | 容差 |
| `oSizeROI` | HgppiSize | [in] | 感兴趣区域 |
| `hgppStreamCtx` | HgppStreamContext | [in] | 流上下文 |

#### 12.12.2. 函数列表
```c
// 8 位无符号。
HgppStatus hgppiProximity_8u_C1R_Ctx(const HGpp8u *pSrc, int nSrcStep,
                                      HGpp8u *pDst, int nDstStep,
                                      HGpp8u nValue, HGpp8u nTolerance,
                                      HgppiSize oSizeROI,
                                      HgppStreamContext hgppStreamCtx)

// 16 位/32 位版本。
HgppStatus hgppiProximity_16u_C1R_Ctx(...)
HgppStatus hgppiProximity_32f_C1R_Ctx(...)
```

### 12.13. 平方距离
**平方距离（Square Distance）** 计算模板图像与目标图像之间的平方误差，常用于模板匹配。

**运算公式：**

$$
\text{SqrDistance}(u, v) = \sum_{y=0}^{H-1} \sum_{x=0}^{W-1} (I_1(x, y) - I_2(x+u, y+v))^2
$$

其中 $I_1$ 是模板图像，$I_2$ 是目标图像，$(u, v)$ 是模板在目标中的位置。

**三种模式：**

| 模式 | 输出尺寸 | 说明 |
|------|----------|------|
| **Full** | $(W_1 + W_2 - 1) \times (H_1 + H_2 - 1)$ | 完整卷积，模板中心遍历目标所有位置 |
| **Same** | $W_1 \times H_1$ | 取 Full 的中心部分，输出与模板同尺寸 |
| **Valid** | $(W_1 - W_2 + 1) \times (H_1 - H_2 + 1)$ | 只计算完全重叠区域，无边界填充 |

**应用说明：**
- **模板匹配**：寻找目标图像中与模板最相似的区域
- **运动估计**：视频压缩中的帧间预测
- **图像配准**：对齐多幅图像
- 平方距离越小，匹配度越高。
- 归一化版本（Norm）输出范围为 [0, 1]。

#### 12.13.1. 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc1` | 设备指针 | [in] | 第一个源图像（模板） |
| `nSrc1Step` | int | [in] | 源图像 1 行步幅 |
| `pSrc2` | 设备指针 | [in] | 第二个源图像（目标） |
| `nSrc2Step` | int | [in] | 源图像 2 行步幅 |
| `pDst` | 设备指针 | [out] | 目标图像（距离图， 32f） |
| `nDstStep` | int | [in] | 目标图像行步幅 |
| `oSizeROI` | HgppiSize | [in] | 感兴趣区域 |
| `pDeviceBuffer` | 设备指针 | [in] | 临时缓冲区 |
| `hgppStreamCtx` | HgppStreamContext | [in] | 流上下文 |

#### 12.13.2. 函数列表
```c
// 8 位无符号（结果为 32f）
HgppStatus hgppiSqrDistanceFull_Norm_8u_32f_C1R_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                                     const HGpp8u *pSrc2, int nSrc2Step,
                                                     Hgpp32f *pDst, int nDstStep,
                                                     HgppiSize oSizeROI,
                                                     HGpp8u *pDeviceBuffer,
                                                     HgppStreamContext hgppStreamCtx)

HgppStatus hgppiSqrDistanceSame_Norm_8u_32f_C1R_Ctx(...)
HgppStatus hgppiSqrDistanceValid_Norm_8u_32f_C1R_Ctx(...)

// 32 位浮点版本。
HgppStatus hgppiSqrDistanceFull_Norm_32f_C1R_Ctx(...)
HgppStatus hgppiSqrDistanceSame_Norm_32f_C1R_Ctx(...)
HgppStatus hgppiSqrDistanceValid_Norm_32f_C1R_Ctx(...)
```

### 12.14. 互相关
互相关（Cross-Correlation）衡量两个图像在不同位移下的相似程度，是模板匹配的核心运算。

**定义：**

$$
(I_1 \star I_2)(u, v) = \sum_{y=0}^{H-1} \sum_{x=0}^{W-1} I_1(x, y) \cdot I_2(x+u, y+v)
$$

**归一化互相关：**

为了消除亮度变化的影响，使用归一化互相关：

$$
\text{NormCorr}(u, v) = \frac{\sum_{x,y} I_1(x, y) \cdot I_2(x+u, y+v)}{\sqrt{\sum_{x,y} I_1(x, y)^2 \cdot \sum_{x,y} I_2(x+u, y+v)^2}}
$$

归一化后输出范围为 [-1, 1]， 1 表示完全正相关，-1 表示完全负相关。

**三种模式：**

| 模式 | 输出尺寸 | 说明 |
|------|----------|------|
| **Full** | $(W_1 + W_2 - 1) \times (H_1 + H_2 - 1)$ | 完整互相关，模板中心遍历目标所有位置 |
| **Same** | $W_1 \times H_1$ | 取 Full 的中心部分，输出与模板同尺寸 |
| **Valid** | $(W_1 - W_2 + 1) \times (H_1 - H_2 + 1)$ | 只计算完全重叠区域，无边界填充 |

**应用说明：**
- **模板匹配**：寻找目标图像中与模板最相似的区域
- **运动估计**：视频压缩中的帧间预测
- **图像配准**：对齐多幅图像
- **特征匹配**：立体视觉中的视差计算。
- 归一化版本对亮度变化不敏感
- 互相关值越大，匹配度越高。

#### 12.14.1. 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc1` | 设备指针 | [in] | 第一个源图像（模板） |
| `nSrc1Step` | int | [in] | 源图像 1 行步幅 |
| `pSrc2` | 设备指针 | [in] | 第二个源图像（目标） |
| `nSrc2Step` | int | [in] | 源图像 2 行步幅 |
| `pDst` | 设备指针 | [out] | 目标图像（相关图， 32f） |
| `nDstStep` | int | [in] | 目标图像行步幅 |
| `oSizeROI` | HgppiSize | [in] | 感兴趣区域 |
| `pDeviceBuffer` | 设备指针 | [in] | 临时缓冲区 |
| `hgppStreamCtx` | HgppStreamContext | [in] | 流上下文 |

#### 12.14.2. 函数列表
##### 12.14.2.1. CrossCorrValid （有效互相关）
```c
// 8 位无符号（结果为 32f）
HgppStatus hgppiCrossCorrValid_Norm_8u_32f_C1R_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                                    const HGpp8u *pSrc2, int nSrc2Step,
                                                    Hgpp32f *pDst, int nDstStep,
                                                    HgppiSize oSizeROI,
                                                    HGpp8u *pDeviceBuffer,
                                                    HgppStreamContext hgppStreamCtx)

// 32 位浮点版本。
HgppStatus hgppiCrossCorrValid_Norm_32f_C1R_Ctx(...)
HgppStatus hgppiCrossCorrValid_32f_C1R_Ctx(...)  // 非归一化版本。
```

##### 12.14.2.2. CrossCorrSame （同互相关）
```c
HgppStatus hgppiCrossCorrSame_Norm_8u_32f_C1R_Ctx(...)
HgppStatus hgppiCrossCorrSame_Norm_32f_C1R_Ctx(...)
```

##### 12.14.2.3. CrossCorrFull （全互相关）
```c
HgppStatus hgppiCrossCorrFull_Norm_8u_32f_C1R_Ctx(...)
HgppStatus hgppiCrossCorrFull_Norm_32f_C1R_Ctx(...)
```

##### 12.14.2.4. GetBufferHostSize （获取缓冲区大小）
```c
// CrossCorrValid。
HgppStatus hgppiCrossCorrValid_NormGetBufferHostSize_8u_32f_C1R_Ctx(HgppiSize oSizeROI,
                                                                     size_t *hpBufferSize)

HgppStatus hgppiCrossCorrValid_NormGetBufferHostSize_32f_C1R_Ctx(...)

// CrossCorrSame。
HgppStatus hgppiCrossCorrSame_NormGetBufferHostSize_8u_32f_C1R_Ctx(HgppiSize oSizeROI,
                                                                    size_t *hpBufferSize)

HgppStatus hgppiCrossCorrSame_NormGetBufferHostSize_32f_C1R_Ctx(...)

// CrossCorrFull。
HgppStatus hgppiCrossCorrFull_NormGetBufferHostSize_8u_32f_C1R_Ctx(HgppiSize oSizeROI,
                                                                    size_t *hpBufferSize)

HgppStatus hgppiCrossCorrFull_NormGetBufferHostSize_32f_C1R_Ctx(...)
```

> **注意：**
> 本章仅列出常用的 CrossCorr 函数变体。完整的 CrossCorr 函数系列包括：
> - **CrossCorrValid**： 68 个函数（Valid 模式， 8u/32f， C1/C3 等）
> - **CrossCorrSame**： 63 个函数（Same 模式）
> - **CrossCorrFull**： 63 个函数（Full 模式）
> - 完整的 GetBufferHostSize 变体（60+ 个）

**请参考头文件 `hgppist.h` 获取完整的函数列表。**

### 12.15. 平方距离
**平方距离（Square Distance）** 计算模板图像与目标图像之间的平方误差，常用于模板匹配。

**运算公式：**

$$
\text{SqrDistance}(u, v) = \sum_{y=0}^{H-1} \sum_{x=0}^{W-1} (I_1(x, y) - I_2(x+u, y+v))^2
$$

其中 $I_1$ 是模板图像，$I_2$ 是目标图像，$(u, v)$ 是模板在目标中的位置。

**三种模式：**

| 模式 | 输出尺寸 | 说明 |
|------|----------|------|
| **Full** | $(W_1 + W_2 - 1) \times (H_1 + H_2 - 1)$ | 完整卷积，模板中心遍历目标所有位置 |
| **Same** | $W_1 \times H_1$ | 取 Full 的中心部分，输出与模板同尺寸 |
| **Valid** | $(W_1 - W_2 + 1) \times (H_1 - H_2 + 1)$ | 只计算完全重叠区域，无边界填充 |

**应用说明：**
- **模板匹配**：寻找目标图像中与模板最相似的区域
- **运动估计**：视频压缩中的帧间预测
- **图像配准**：对齐多幅图像
- 平方距离越小，匹配度越高。
- 归一化版本（Norm）输出范围为 [0, 1]。

#### 12.15.1. 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc1` | 设备指针 | [in] | 第一个源图像（模板） |
| `nSrc1Step` | int | [in] | 源图像 1 行步幅 |
| `pSrc2` | 设备指针 | [in] | 第二个源图像（目标） |
| `nSrc2Step` | int | [in] | 源图像 2 行步幅 |
| `pDst` | 设备指针 | [out] | 目标图像（距离图， 32f） |
| `nDstStep` | int | [in] | 目标图像行步幅 |
| `oSizeROI` | HgppiSize | [in] | 感兴趣区域 |
| `pDeviceBuffer` | 设备指针 | [in] | 临时缓冲区 |
| `hgppStreamCtx` | HgppStreamContext | [in] | 流上下文 |

#### 12.15.2. 函数列表
```c
// 8 位无符号（结果为 32f）
HgppStatus hgppiSqrDistanceFull_Norm_8u_32f_C1R_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                                     const HGpp8u *pSrc2, int nSrc2Step,
                                                     Hgpp32f *pDst, int nDstStep,
                                                     HgppiSize oSizeROI,
                                                     HGpp8u *pDeviceBuffer,
                                                     HgppStreamContext hgppStreamCtx)

HgppStatus hgppiSqrDistanceSame_Norm_8u_32f_C1R_Ctx(...)
HgppStatus hgppiSqrDistanceValid_Norm_8u_32f_C1R_Ctx(...)

// 32 位浮点版本。
HgppStatus hgppiSqrDistanceFull_Norm_32f_C1R_Ctx(...)
HgppStatus hgppiSqrDistanceSame_Norm_32f_C1R_Ctx(...)
HgppStatus hgppiSqrDistanceValid_Norm_32f_C1R_Ctx(...)
```

##### 12.15.2.1. GetBufferHostSize （获取缓冲区大小）
```c
// SqrDistanceFull。
HgppStatus hgppiSqrDistanceFull_NormGetBufferHostSize_8u_32f_C1R_Ctx(HgppiSize oSizeROI,
                                                                      size_t *hpBufferSize)

HgppStatus hgppiSqrDistanceFull_NormGetBufferHostSize_32f_C1R_Ctx(...)

// SqrDistanceSame。
HgppStatus hgppiSqrDistanceSame_NormGetBufferHostSize_8u_32f_C1R_Ctx(HgppiSize oSizeROI,
                                                                      size_t *hpBufferSize)

HgppStatus hgppiSqrDistanceSame_NormGetBufferHostSize_32f_C1R_Ctx(...)

// SqrDistanceValid。
HgppStatus hgppiSqrDistanceValid_NormGetBufferHostSize_8u_32f_C1R_Ctx(HgppiSize oSizeROI,
                                                                       size_t *hpBufferSize)

HgppStatus hgppiSqrDistanceValid_NormGetBufferHostSize_32f_C1R_Ctx(...)
```

### 12.16. 质量指数
质量指数（Quality Index）也称为结构相似性指数（SSIM， Structural Similarity Index），用于评估两幅图像的相似度和质量。

**运算公式：**

$$
\text{QI} = \frac{(2\mu_1\mu_2 + C_1)(2\sigma_{12} + C_2)}{(\mu_1^2 + \mu_2^2 + C_1)(\sigma_1^2 + \sigma_2^2 + C_2)}
$$

其中：
- $\mu_1, \mu_2$：两幅图像的局部均值
- $\sigma_1^2, \sigma_2^2$：两幅图像的局部方差
- $\sigma_{12}$：两幅图像的协方差
- $C_1, C_2$：稳定常数（防止分母为零）

**取值范围：**
- QI ∈ [-1, 1]
- QI = 1：两幅图像完全相同
- QI = -1：两幅图像完全负相关
- QI 越接近 1，图像质量越好

**应用说明：**
- **图像质量评估**：评估压缩、传输等处理后的图像质量。
- **图像恢复**：评估去噪、超分辨率等算法效果
- **视频质量监测**：实时监测视频传输质量
- 比传统的 PSNR 更符合人眼感知
- 局部计算（滑动窗口），反映空间变化。
- 需要临时缓冲区。

#### 12.16.1. 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc1` | 设备指针 | [in] | 第一个源图像（参考图像） |
| `nSrc1Step` | int | [in] | 源图像 1 行步幅 |
| `pSrc2` | 设备指针 | [in] | 第二个源图像（测试图像） |
| `nSrc2Step` | int | [in] | 源图像 2 行步幅 |
| `pQualityIndex` | 设备指针 | [out] | 质量指数图（32f） |
| `oSizeROI` | HgppiSize | [in] | 感兴趣区域 |
| `pDeviceBuffer` | 设备指针 | [in] | 临时缓冲区 |
| `hgppStreamCtx` | HgppStreamContext | [in] | 流上下文 |

> **注意：**
> - 需要预先调用 `QualityIndexGetBufferHostSize` 获取缓冲区大小。
> - 结果为 32f 浮点数，范围 [-1, 1]
> - 多通道版本对每个通道独立计算。

#### 12.16.2. 函数列表
##### 12.16.2.1. 8 位无符号整数
```c
// 单通道。
HgppStatus hgppiQualityIndex_8u32f_C1R_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                            const HGpp8u *pSrc2, int nSrc2Step,
                                            Hgpp32f *pQualityIndex,
                                            HgppiSize oSizeROI,
                                            HGpp8u *pDeviceBuffer,
                                            HgppStreamContext hgppStreamCtx)

// 获取缓冲区大小。
HgppStatus hgppiQualityIndexGetBufferHostSize_8u32f_C1R_Ctx(HgppiSize oSizeROI,
                                                             size_t *hpBufferSize)

// 三通道。
HgppStatus hgppiQualityIndex_8u32f_C3R_Ctx(...)

// 四通道（忽略 Alpha）
HgppStatus hgppiQualityIndex_8u32f_AC4R_Ctx(...)
```

##### 12.16.2.2. 16 位/32 位版本
```c
HgppStatus hgppiQualityIndex_16u32f_C1R_Ctx(...)
HgppStatus hgppiQualityIndex_32f_C1R_Ctx(...)
HgppStatus hgppiQualityIndex_16u32f_C3R_Ctx(...)
HgppStatus hgppiQualityIndex_32f_C3R_Ctx(...)
```

##### 12.16.2.3. GetBufferHostSize （获取缓冲区大小）- MSE/PSNR/SSIM
```c
// MSE。
HgppStatus hgppiMSEGetBufferHostSize_8u_C1R_Ctx(HgppiSize oSizeROI,
                                                 size_t *hpBufferSize)

HgppStatus hgppiMSEGetBufferHostSize_8u_C3R_Ctx(...)
HgppStatus hgppiMSEGetBufferHostSize_16u_C1R_Ctx(...)
HgppStatus hgppiMSEGetBufferHostSize_32f_C1R_Ctx(...)

// PSNR。
HgppStatus hgppiPSNRGetBufferHostSize_8u_C1R_Ctx(HgppiSize oSizeROI,
                                                  size_t *hpBufferSize)

HgppStatus hgppiPSNRGetBufferHostSize_8u_C3R_Ctx(...)
HgppStatus hgppiPSNRGetBufferHostSize_16u_C1R_Ctx(...)
HgppStatus hgppiPSNRGetBufferHostSize_32f_C1R_Ctx(...)

// SSIM。
HgppStatus hgppiSSIMGetBufferHostSize_8u_C1R_Ctx(HgppiSize oSizeROI,
                                                  size_t *hpBufferSize)

HgppStatus hgppiSSIMGetBufferHostSize_8u_C3R_Ctx(...)
HgppStatus hgppiSSIMGetBufferHostSize_16u_C1R_Ctx(...)
HgppStatus hgppiSSIMGetBufferHostSize_32f_C1R_Ctx(...)

// MS-SSIM。
HgppStatus hgppiMSSSIMGetBufferHostSize_8u_C1R_Ctx(HgppiSize oSizeROI,
                                                    size_t *hpBufferSize)

HgppStatus hgppiMSSSIMGetBufferHostSize_8u_C3R_Ctx(...)

// WMSSSIM。
HgppStatus hgppiWMSSSIMGetBufferHostSize_8u_C1R_Ctx(HgppiSize oSizeROI,
                                                     size_t *hpBufferSize)

HgppStatus hgppiWMSSSIMGetBufferHostSize_8u_C3R_Ctx(...)
```

> **注意：**
> 本章仅列出常用的 IQA 函数变体。完整的图像质量评估函数系列包括：
> - **MSE （均方误差）**： 20+ 个函数（8u/16u/32f， C1/C3/C4/AC4 等）
> - **PSNR （峰值信噪比）**： 20+ 个函数
> - **SSIM （结构相似性）**： 20+ 个函数
> - **MS-SSIM （多尺度 SSIM）**： 10+ 个函数
> - **WMSSSIM （加权多尺度 SSIM）**： 10+ 个函数
> - 完整的 GetBufferHostSize 变体（80+ 个）

**请参考头文件 `hgppist.h` 获取完整的函数列表。**

### 12.17. 误差计算
误差计算用于量化两幅图像之间的差异，是图像质量评估的基础。

**最大误差（Maximum Error）：**

$$
E_{max} = \max_{x,y} |I_1(x, y) - I_2(x, y)|
$$

反映最坏情况下的误差。

**平均误差（Average Error）：**

$$
E_{avg} = \frac{1}{N} \sum_{y=0}^{H-1} \sum_{x=0}^{W-1} |I_1(x, y) - I_2(x, y)|
$$

反映平均误差水平。

**最大相对误差（Maximum Relative Error）：**

$$
E_{max\_rel} = \max_{x,y} \frac{|I_1(x, y) - I_2(x, y)|}{|I_2(x, y)|}
$$

反映相对于原图的最大误差比例。

**平均相对误差（Average Relative Error）：**

$$
E_{avg\_rel} = \frac{1}{N} \sum_{y=0}^{H-1} \sum_{x=0}^{W-1} \frac{|I_1(x, y) - I_2(x, y)|}{|I_2(x, y)|}
$$

反映平均误差比例。

**应用说明：**
- **图像质量评估**：评估压缩、传输等处理后的图像质量。
- **算法比较**：比较不同图像处理算法的效果。
- **误差分析**：量化数值计算的精度。
- 相对误差版本需要 $I_2(x, y) \neq 0$
- 结果为 64f 浮点数（保证精度）
- 需要临时缓冲区。

#### 12.17.1. 通用参数
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc1` | 设备指针 | [in] | 第一个源图像 |
| `nSrc1Step` | int | [in] | 源图像 1 行步幅 |
| `pSrc2` | 设备指针 | [in] | 第二个源图像 |
| `nSrc2Step` | int | [in] | 源图像 2 行步幅 |
| `pError` | 设备指针 | [out] | 误差结果（64f） |
| `oSizeROI` | HgppiSize | [in] | 感兴趣区域 |
| `pDeviceBuffer` | 设备指针 | [in] | 临时缓冲区 |
| `hgppStreamCtx` | HgppStreamContext | [in] | 流上下文 |

> **注意：**
> - 相对误差版本需要 $I_2(x, y) \neq 0$
> - 需要临时缓冲区。
> - 结果为 64f 浮点数

#### 12.17.2. 函数列表
##### 12.17.2.1. MaximumError （最大误差）
```c
// 8 位无符号。
HgppStatus hgppiMaximumError_8u_C1R_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                         const HGpp8u *pSrc2, int nSrc2Step,
                                         Hgpp64f *pError, HgppiSize oSizeROI,
                                         HGpp8u *pDeviceBuffer,
                                         HgppStreamContext hgppStreamCtx)

// 16 位/32 位版本。
HgppStatus hgppiMaximumError_16u_C1R_Ctx(...)
HgppStatus hgppiMaximumError_32f_C1R_Ctx(...)
```

##### 12.17.2.2. AverageError （平均误差）
```c
HgppStatus hgppiAverageError_8u_C1R_Ctx(...)
HgppStatus hgppiAverageError_16u_C1R_Ctx(...)
HgppStatus hgppiAverageError_32f_C1R_Ctx(...)
```

##### 12.17.2.3. MaximumRelativeError （最大相对误差）
```c
HgppStatus hgppiMaximumRelativeError_8u_C1R_Ctx(...)
HgppStatus hgppiMaximumRelativeError_16u_C1R_Ctx(...)
HgppStatus hgppiMaximumRelativeError_32f_C1R_Ctx(...)
```

##### 12.17.2.4. AverageRelativeError （平均相对误差）
```c
HgppStatus hgppiAverageRelativeError_8u_C1R_Ctx(...)
HgppStatus hgppiAverageRelativeError_16u_C1R_Ctx(...)
HgppStatus hgppiAverageRelativeError_32f_C1R_Ctx(...)
```

##### 12.17.2.5. GetBufferHostSize （获取缓冲区大小）
```c
// MaximumError。
HgppStatus hgppiMaximumErrorGetBufferHostSize_8u_C1R_Ctx(HgppiSize oSizeROI,
                                                          size_t *hpBufferSize)

HgppStatus hgppiMaximumErrorGetBufferHostSize_16u_C1R_Ctx(...)
HgppStatus hgppiMaximumErrorGetBufferHostSize_32f_C1R_Ctx(...)

// AverageError。
HgppStatus hgppiAverageErrorGetBufferHostSize_8u_C1R_Ctx(HgppiSize oSizeROI,
                                                          size_t *hpBufferSize)

HgppStatus hgppiAverageErrorGetBufferHostSize_16u_C1R_Ctx(...)
HgppStatus hgppiAverageErrorGetBufferHostSize_32f_C1R_Ctx(...)

// MaximumRelativeError。
HgppStatus hgppiMaximumRelativeErrorGetBufferHostSize_8u_C1R_Ctx(HgppiSize oSizeROI,
                                                                  size_t *hpBufferSize)

HgppStatus hgppiMaximumRelativeErrorGetBufferHostSize_16u_C1R_Ctx(...)
HgppStatus hgppiMaximumRelativeErrorGetBufferHostSize_32f_C1R_Ctx(...)

// AverageRelativeError。
HgppStatus hgppiAverageRelativeErrorGetBufferHostSize_8u_C1R_Ctx(HgppiSize oSizeROI,
                                                                  size_t *hpBufferSize)

HgppStatus hgppiAverageRelativeErrorGetBufferHostSize_16u_C1R_Ctx(...)
HgppStatus hgppiAverageRelativeErrorGetBufferHostSize_32f_C1R_Ctx(...)
```

### 12.18. 图像质量评估（IQA）
图像质量评估（Image Quality Assessment, IQA）用于量化评估两幅图像之间的质量差异，常用的指标包括 MSE、 PSNR、 SSIM 和 MS-SSIM。

**MSE （均方误差， Mean Squared Error）：**

$$
\text{MSE} = \frac{1}{N} \sum_{y=0}^{H-1} \sum_{x=0}^{W-1} (I_1(x, y) - I_2(x, y))^2
$$

MSE 值越小，两幅图像越相似。

**PSNR （峰值信噪比， Peak Signal-to-Noise Ratio）：**

$$
\text{PSNR} = 10 \cdot \log_{10}\left(\frac{\text{MAX}^2}{\text{MSE}}\right) = 20 \cdot \log_{10}\left(\frac{\text{MAX}}{\sqrt{\text{MSE}}}\right)
$$

其中 MAX 是像素值的最大值（如 8 位图像为 255）。 PSNR 值越大，图像质量越好。

**SSIM （结构相似性， Structural Similarity Index）：**

$$
\text{SSIM}(I_1, I_2) = \frac{(2\mu_1\mu_2 + C_1)(2\sigma_{12} + C_2)}{(\mu_1^2 + \mu_2^2 + C_1)(\sigma_1^2 + \sigma_2^2 + C_2)}
$$

其中：
- $\mu_1, \mu_2$：两幅图像的局部均值
- $\sigma_1^2, \sigma_2^2$：两幅图像的局部方差
- $\sigma_{12}$：两幅图像的协方差
- $C_1, C_2$：稳定常数（防止分母为零）

SSIM 值范围为 [-1, 1]， 1 表示两幅图像完全相同。

**MS-SSIM （多尺度 SSIM， Multi-Scale SSIM）：**

在不同尺度上计算 SSIM 并加权组合，更符合人眼感知特性。

**应用说明：**
- **图像压缩质量评估**：评估压缩算法对图像质量的影响。
- **图像恢复评估**：评估去噪、超分辨率等算法效果
- **视频质量监测**：实时监测视频传输质量
- **算法比较**：比较不同图像处理算法的性能。
- MSE/PSNR 计算简单，但不符合人眼感知
- SSIM/MS-SSIM 更符合人眼感知，但计算复杂度较高

#### 12.18.1. 通用参数（MSE/PSNR/SSIM）
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc1` | 设备指针 | [in] | 第一个源图像（参考图像） |
| `nSrc1Step` | int | [in] | 源图像 1 行步幅 |
| `pSrc2` | 设备指针 | [in] | 第二个源图像（测试图像） |
| `nSrc2Step` | int | [in] | 源图像 2 行步幅 |
| `pMSE` / `pPSNR` / `pSSIM` | 设备指针 | [out] | 计算结果（32f） |
| `oSizeROI` | HgppiSize | [in] | 感兴趣区域 |
| `pDeviceBuffer` | 设备指针 | [in] | 临时缓冲区 |
| `hgppStreamCtx` | HgppStreamContext | [in] | 流上下文 |

> **注意：**
> - 需要预先调用 `GetBufferHostSize` 获取缓冲区大小。
> - 结果为 32f 浮点数
> - 多通道版本对每个通道独立计算。
> - MS-SSIM 需要更大的临时缓冲区。

#### 12.18.2. 函数列表
##### 12.18.2.1. MSE （均方误差）
```c
// 8 位无符号单通道。
HgppStatus hgppiMSE_8u_C1R_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                const HGpp8u *pSrc2, int nSrc2Step,
                                HgppiSize oSizeROI,
                                Hgpp32f *pMSE,
                                HGpp8u *pDeviceBuffer,
                                HgppStreamContext hgppStreamCtx)

// 8 位无符号三通道。
HgppStatus hgppiMSE_8u_C3R_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                const HGpp8u *pSrc2, int nSrc2Step,
                                HgppiSize oSizeROI,
                                Hgpp32f *pMSE,
                                HGpp8u *pDeviceBuffer,
                                HgppStreamContext hgppStreamCtx)

// 获取缓冲区大小。
HgppStatus hgppiMSEGetBufferHostSize_8u_C1R_Ctx(HgppiSize oSizeROI,
                                                 size_t *hpBufferSize)

// 16 位/32 位版本。
HgppStatus hgppiMSE_16u_C1R_Ctx(...)
HgppStatus hgppiMSE_32f_C1R_Ctx(...)
```

##### 12.18.2.2. PSNR （峰值信噪比）
```c
// 8 位无符号单通道。
HgppStatus hgppiPSNR_8u_C1R_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                 const HGpp8u *pSrc2, int nSrc2Step,
                                 HgppiSize oSizeROI,
                                 Hgpp32f *pPSNR,
                                 HGpp8u *pDeviceBuffer,
                                 HgppStreamContext hgppStreamCtx)

// 8 位无符号三通道。
HgppStatus hgppiPSNR_8u_C3R_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                 const HGpp8u *pSrc2, int nSrc2Step,
                                 HgppiSize oSizeROI,
                                 Hgpp32f *pPSNR,
                                 HGpp8u *pDeviceBuffer,
                                 HgppStreamContext hgppStreamCtx)

// 获取缓冲区大小。
HgppStatus hgppiPSNRGetBufferHostSize_8u_C1R_Ctx(HgppiSize oSizeROI,
                                                  size_t *hpBufferSize)

// 16 位/32 位版本。
HgppStatus hgppiPSNR_16u_C1R_Ctx(...)
HgppStatus hgppiPSNR_32f_C1R_Ctx(...)
```

##### 12.18.2.3. SSIM （结构相似性）
```c
// 8 位无符号单通道。
HgppStatus hgppiSSIM_8u_C1R_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                 const HGpp8u *pSrc2, int nSrc2Step,
                                 HgppiSize oSizeROI,
                                 Hgpp32f *pSSIM,
                                 HGpp8u *pDeviceBuffer,
                                 HgppStreamContext hgppStreamCtx)

// 8 位无符号三通道。
HgppStatus hgppiSSIM_8u_C3R_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                 const HGpp8u *pSrc2, int nSrc2Step,
                                 HgppiSize oSizeROI,
                                 Hgpp32f *pSSIM,
                                 HGpp8u *pDeviceBuffer,
                                 HgppStreamContext hgppStreamCtx)

// 获取缓冲区大小。
HgppStatus hgppiSSIMGetBufferHostSize_8u_C1R_Ctx(HgppiSize oSizeROI,
                                                  size_t *hpBufferSize)

// 16 位/32 位版本。
HgppStatus hgppiSSIM_16u_C1R_Ctx(...)
HgppStatus hgppiSSIM_32f_C1R_Ctx(...)
```

##### 12.18.2.4. MS-SSIM （多尺度 SSIM）
```c
// 8 位无符号单通道。
HgppStatus hgppiMSSSIM_8u_C1R_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                   const HGpp8u *pSrc2, int nSrc2Step,
                                   HgppiSize oSizeROI,
                                   Hgpp32f *pMSSSIM,
                                   HGpp8u *pDeviceBuffer,
                                   HgppStreamContext hgppStreamCtx)

// 8 位无符号三通道。
HgppStatus hgppiMSSSIM_8u_C3R_Ctx(...)

// 获取缓冲区大小。
HgppStatus hgppiMSSSIMGetBufferHostSize_8u_C1R_Ctx(HgppiSize oSizeROI,
                                                    size_t *hpBufferSize)
```

##### 12.18.2.5. WMSSSIM （加权多尺度 SSIM）
```c
// 8 位无符号单通道。
HgppStatus hgppiWMSSSIM_8u_C1R_Ctx(const HGpp8u *pSrc1, int nSrc1Step,
                                    const HGpp8u *pSrc2, int nSrc2Step,
                                    HgppiSize oSizeROI,
                                    Hgpp32f *pWMSSSIM,
                                    HGpp8u *pDeviceBuffer,
                                    HgppStreamContext hgppStreamCtx)

// 8 位无符号三通道。
HgppStatus hgppiWMSSSIM_8u_C3R_Ctx(...)
```

> **注意：**
> 本章仅列出常用的误差计算函数变体。完整的误差计算函数系列包括：
> - **MaximumError （最大误差）**： 44 个函数（8u/8s/16u/16s/16sc/32u/32s/32sc/32f/32fc/64f， C1/C2/C3/C4 等）
> - **AverageError （平均误差）**： 44 个函数
> - **MaximumRelativeError （最大相对误差）**： 44 个函数
> - **AverageRelativeError （平均相对误差）**： 44 个函数
> - 完整的 GetBufferHostSize 变体（170+ 个）

**请参考头文件 `hgppist.h` 获取完整的函数列表。**

### 12.19. 批量质量评估（统一 ROI）
批量质量评估（Batch Quality Assessment）用于同时评估多对图像的质量，所有图像对使用统一的 ROI。

**运算公式：**

与单幅图像的 IQA 公式相同，但对多对图像并行计算：

$$
\text{MSE}_i = \frac{1}{N} \sum_{y=0}^{H-1} \sum_{x=0}^{W-1} (I_{1,i}(x, y) - I_{2,i}(x, y))^2
$$

其中 $i = 1, \ldots, \text{nBatchSize}$ 是批处理中的第 $i$ 对图像。

**应用说明：**
- **批量图像处理**：同时评估多幅图像的质量
- **视频质量监测**：实时监测视频帧序列质量
- **大规模图像分析**：高效处理大量图像数据。
- **统一 ROI**：所有图像对使用相同的 ROI 尺寸。
- **性能优势**：比逐个调用单幅图像函数更高效。
- 需要预先分配 `HgppiImageDescriptor` 数组。
- 需要预先分配 `HgppiBufferDescriptor` 数组（每图像一个缓冲区）。

#### 12.19.1. 通用参数（Batch 统一 ROI）
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc1BatchList` | 设备指针 | [in] | 第一个源图像批处理列表（`HgppiImageDescriptor` 数组） |
| `pSrc2BatchList` | 设备指针 | [in] | 第二个源图像批处理列表（`HgppiImageDescriptor` 数组） |
| `nBatchSize` | int | [in] | 批处理大小（图像对数量，必须 > 1） |
| `oSizeROI` | HgppiSize | [in] | **统一 ROI** - 所有图像对的 ROI 宽度和高度 |
| `pMSE` / `pPSNR` / `pSSIM` | 设备指针 | [out] | 输出数组（大小为 `nBatchSize * nChannels`） |
| `pDeviceBufferList` | 设备指针 | [in] | 缓冲区描述符列表（`HgppiBufferDescriptor` 数组） |
| `hgppStreamCtx` | HgppStreamContext | [in] | 流上下文 |

> **注意：**
> - `nBatchSize` 必须 > 1
> - `pSrc1BatchList` 和 `pSrc2BatchList` 必须是设备内存指针。
> - 每个图像的 `HgppiImageDescriptor` 必须预先初始化（`pData`, `nStep`, `oSize`）。
> - `oSizeROI` 对所有图像对必须有效（不能超出任何图像的边界）。
> - `pDeviceBufferList` 必须预先通过 `GetBufferHostSize` 分配
> - 输出数组大小为 `nBatchSize * sizeof(Hgpp32f) * nChannels`

#### 12.19.2. 函数列表
##### 12.19.2.1. MSEBatch （批量均方误差）
```c
// 8 位无符号单通道。
HgppStatus hgppiMSEBatch_8u_C1R_Ctx(const HgppiImageDescriptor *pSrc1BatchList,
                                     const HgppiImageDescriptor *pSrc2BatchList,
                                     int nBatchSize,
                                     HgppiSize oSizeROI,
                                     Hgpp32f *pMSE,
                                     HgppiBufferDescriptor *pDeviceBufferList,
                                     HgppStreamContext hgppStreamCtx)

// 8 位无符号三通道。
HgppStatus hgppiMSEBatch_8u_C3R_Ctx(const HgppiImageDescriptor *pSrc1BatchList,
                                     const HgppiImageDescriptor *pSrc2BatchList,
                                     int nBatchSize,
                                     HgppiSize oSizeROI,
                                     Hgpp32f *pMSE,
                                     HgppiBufferDescriptor *pDeviceBufferList,
                                     HgppStreamContext hgppStreamCtx)

// 获取缓冲区大小。
HgppStatus hgppiMSEBatchGetBufferHostSize_8u_C1R_Ctx(int nBatchSize,
                                                      HgppiSize oSizeROI,
                                                      size_t *hpBufferSize)

HgppStatus hgppiMSEBatchGetBufferHostSize_8u_C3R_Ctx(...)
```

##### 12.19.2.2. PSNRBatch （批量峰值信噪比）
```c
// 8 位无符号单通道。
HgppStatus hgppiPSNRBatch_8u_C1R_Ctx(const HgppiImageDescriptor *pSrc1BatchList,
                                      const HgppiImageDescriptor *pSrc2BatchList,
                                      int nBatchSize,
                                      HgppiSize oSizeROI,
                                      Hgpp32f *pPSNR,
                                      HgppiBufferDescriptor *pDeviceBufferList,
                                      HgppStreamContext hgppStreamCtx)

// 8 位无符号三通道。
HgppStatus hgppiPSNRBatch_8u_C3R_Ctx(...)

// 获取缓冲区大小。
HgppStatus hgppiPSNRBatchGetBufferHostSize_8u_C1R_Ctx(int nBatchSize,
                                                       HgppiSize oSizeROI,
                                                       size_t *hpBufferSize)

HgppStatus hgppiPSNRBatchGetBufferHostSize_8u_C3R_Ctx(...)
```

##### 12.19.2.3. SSIMBatch （批量结构相似性）
```c
// 8 位无符号单通道。
HgppStatus hgppiSSIMBatch_8u_C1R_Ctx(const HgppiImageDescriptor *pSrc1BatchList,
                                      const HgppiImageDescriptor *pSrc2BatchList,
                                      int nBatchSize,
                                      HgppiSize oSizeROI,
                                      Hgpp32f *pSSIM,
                                      HgppiBufferDescriptor *pDeviceBufferList,
                                      HgppStreamContext hgppStreamCtx)

// 8 位无符号三通道。
HgppStatus hgppiSSIMBatch_8u_C3R_Ctx(...)

// 获取缓冲区大小。
HgppStatus hgppiSSIMBatchGetBufferHostSize_8u_C1R_Ctx(int nBatchSize,
                                                       HgppiSize oSizeROI,
                                                       size_t *hpBufferSize)

HgppStatus hgppiSSIMBatchGetBufferHostSize_8u_C3R_Ctx(...)
```

##### 12.19.2.4. MSSSIMBatch （批量多尺度 SSIM）
```c
// 8 位无符号单通道。
HgppStatus hgppiMSSSIMBatch_8u_C1R_Ctx(const HgppiImageDescriptor *pSrc1BatchList,
                                        const HgppiImageDescriptor *pSrc2BatchList,
                                        int nBatchSize,
                                        HgppiSize oSizeROI,
                                        Hgpp32f *pMSSSIM,
                                        HgppiBufferDescriptor *pDeviceBufferList,
                                        HgppStreamContext hgppStreamCtx)

// 获取缓冲区大小。
HgppStatus hgppiMSSSIMBatchGetBufferHostSize_8u_C1R_Ctx(int nBatchSize,
                                                         HgppiSize oSizeROI,
                                                         size_t *hpBufferSize)
```

### 12.20. 批量质量评估高级版（独立 ROI）
批量质量评估高级版（Advanced Batch Quality Assessment）允许每对图像使用独立的 ROI，提供更大的灵活性。

**与标准 Batch 的区别：**

| 特性 | 标准 Batch | Advanced Batch |
|------|------------|----------------|
| **ROI** | 统一 ROI （所有图像对相同） | 每图像独立 ROI |
| **参数** | `oSizeROI` | `oMaxSizeROI`（最大 ROI） |
| **灵活性** | 低 | 高 |
| **性能** | 稍高 | 稍低 |

**应用说明：**
- **不同尺寸图像**：批处理中的图像对可以有不同的尺寸。
- **不同关注区域**：每对图像可以评估不同的 ROI。
- **视频质量监测**：每帧可以有不同的感兴趣区域。
- **灵活性强**：适用于复杂的批处理场景。
- `oMaxSizeROI` 是所有图像对 ROI 的最大值
- 每图像的 ROI 通过 `HgppiImageDescriptor` 中的 `oSize` 指定。
- WMSSSIM 要求**：每图像 ROI 尺寸必须 ≥ 16×16 像素。

#### 12.20.1. 通用参数（Advanced Batch 独立 ROI）
| 参数 | 类型 | 方向 | 说明 |
|------|------|------|------|
| `pSrc1BatchList` | 设备指针 | [in] | 第一个源图像批处理列表（`HgppiImageDescriptor` 数组） |
| `pSrc2BatchList` | 设备指针 | [in] | 第二个源图像批处理列表（`HgppiImageDescriptor` 数组） |
| `nBatchSize` | int | [in] | 批处理大小（图像对数量，必须 > 1） |
| `oMaxSizeROI` | HgppiSize | [in] | **最大 ROI** - 所有图像对 ROI 的最大宽度和高度 |
| `pMSE` / `pPSNR` / `pSSIM` | 设备指针 | [out] | 输出数组（大小为 `nBatchSize * nChannels`） |
| `pDeviceBufferList` | 设备指针 | [in] | 缓冲区描述符列表（`HgppiBufferDescriptor` 数组） |
| `hgppStreamCtx` | HgppStreamContext | [in] | 流上下文 |

> **注意：**
> - `nBatchSize` 必须 > 1
> - 每个图像的 `HgppiImageDescriptor` 必须预先初始化（`pData`, `nStep`, `oSize`）。
> - `oMaxSizeROI` 是所有图像对 ROI 的最大值
> - 每图像的实际 ROI 由 `HgppiImageDescriptor.oSize` 指定。
> - **WMSSSIM 特殊要求**：每图像 ROI 尺寸必须 ≥ 16×16 像素，否则行为未定义。
> - `pDeviceBufferList` 必须预先通过 `GetBufferHostSize` 分配

#### 12.20.2. 函数列表
##### 12.20.2.1. MSEBatchAdvanced （批量均方误差高级版）
```c
// 8 位无符号单通道。
HgppStatus hgppiMSEBatch_8u_C1R_Advanced_Ctx(const HgppiImageDescriptor *pSrc1BatchList,
                                              const HgppiImageDescriptor *pSrc2BatchList,
                                              int nBatchSize,
                                              HgppiSize oMaxSizeROI,
                                              Hgpp32f *pMSE,
                                              HgppiBufferDescriptor *pDeviceBufferList,
                                              HgppStreamContext hgppStreamCtx)

// 8 位无符号三通道。
HgppStatus hgppiMSEBatch_8u_C3R_Advanced_Ctx(const HgppiImageDescriptor *pSrc1BatchList,
                                              const HgppiImageDescriptor *pSrc2BatchList,
                                              int nBatchSize,
                                              HgppiSize oMaxSizeROI,
                                              Hgpp32f *pMSE,
                                              HgppiBufferDescriptor *pDeviceBufferList,
                                              HgppStreamContext hgppStreamCtx)
```

##### 12.20.2.2. PSNRBatchAdvanced （批量峰值信噪比高级版）
```c
// 8 位无符号单通道。
HgppStatus hgppiPSNRBatch_8u_C1R_Advanced_Ctx(const HgppiImageDescriptor *pSrc1BatchList,
                                               const HgppiImageDescriptor *pSrc2BatchList,
                                               int nBatchSize,
                                               HgppiSize oMaxSizeROI,
                                               Hgpp32f *pPSNR,
                                               HgppiBufferDescriptor *pDeviceBufferList,
                                               HgppStreamContext hgppStreamCtx)

// 8 位无符号三通道。
HgppStatus hgppiPSNRBatch_8u_C3R_Advanced_Ctx(...)
```

##### 12.20.2.3. SSIMBatchAdvanced （批量结构相似性高级版）
```c
// 8 位无符号单通道。
HgppStatus hgppiSSIMBatch_8u_C1R_Advanced_Ctx(const HgppiImageDescriptor *pSrc1BatchList,
                                               const HgppiImageDescriptor *pSrc2BatchList,
                                               int nBatchSize,
                                               HgppiSize oMaxSizeROI,
                                               Hgpp32f *pSSIM,
                                               HgppiBufferDescriptor *pDeviceBufferList,
                                               HgppStreamContext hgppStreamCtx)

// 8 位无符号三通道。
HgppStatus hgppiSSIMBatch_8u_C3R_Advanced_Ctx(...)
```

##### 12.20.2.4. WMSSSIMBatchAdvanced （批量加权多尺度 SSIM 高级版）
```c
// 8 位无符号单通道。
HgppStatus hgppiWMSSSIMBatch_8u_C1R_Advanced_Ctx(const HgppiImageDescriptor *pSrc1BatchList,
                                                  const HgppiImageDescriptor *pSrc2BatchList,
                                                  int nBatchSize,
                                                  HgppiSize oMaxSizeROI,
                                                  Hgpp32f *pWMSSSIM,
                                                  HgppiBufferDescriptor *pDeviceBufferList,
                                                  HgppStreamContext hgppStreamCtx)

// 8 位无符号三通道。
HgppStatus hgppiWMSSSIMBatch_8u_C3R_Advanced_Ctx(const HgppiImageDescriptor *pSrc1BatchList,
                                                  const HgppiImageDescriptor *pSrc2BatchList,
                                                  int nBatchSize,
                                                  HgppiSize oMaxSizeROI,
                                                  Hgpp32f *pWMSSSIM,
                                                  HgppiBufferDescriptor *pDeviceBufferList,
                                                  HgppStreamContext hgppStreamCtx)
```

> **注意：**
> - 每图像 ROI 尺寸必须 ≥ 16×16 像素。
> - 小于 16×16 像素的 ROI 会导致未定义行为。
> - 这是因为多尺度计算需要足够的图像尺寸。

##### 12.20.2.5. GetBufferHostSize （获取缓冲区大小）
```c
// MSEBatchAdvanced。
HgppStatus hgppiMSEBatchGetBufferHostSize_8u_C1R_Advanced_Ctx(int nBatchSize,
                                                               HgppiSize oMaxSizeROI,
                                                               size_t *hpBufferSize)

HgppStatus hgppiMSEBatchGetBufferHostSize_8u_C3R_Advanced_Ctx(...)

// PSNRBatchAdvanced。
HgppStatus hgppiPSNRBatchGetBufferHostSize_8u_C1R_Advanced_Ctx(int nBatchSize,
                                                                HgppiSize oMaxSizeROI,
                                                                size_t *hpBufferSize)

HgppStatus hgppiPSNRBatchGetBufferHostSize_8u_C3R_Advanced_Ctx(...)

// SSIMBatchAdvanced。
HgppStatus hgppiSSIMBatchGetBufferHostSize_8u_C1R_Advanced_Ctx(int nBatchSize,
                                                                HgppiSize oMaxSizeROI,
                                                                size_t *hpBufferSize)

HgppStatus hgppiSSIMBatchGetBufferHostSize_8u_C3R_Advanced_Ctx(...)

// WMSSSIMBatchAdvanced。
HgppStatus hgppiWMSSSIMBatchGetBufferHostSize_8u_C1R_Advanced_Ctx(int nBatchSize,
                                                                   HgppiSize oMaxSizeROI,
                                                                   size_t *hpBufferSize)

HgppStatus hgppiWMSSSIMBatchGetBufferHostSize_8u_C3R_Advanced_Ctx(...)
```

> **注意：**
> 本章仅列出常用的 Batch 函数变体。完整的批量质量评估函数系列包括：
> - **Batch （统一 ROI）**： 80+ 个函数（MSE/PSNR/SSIM/MSSSIM， 8u/16u/32f， C1/C3 等）
> - **Batch Advanced （独立 ROI）**： 60+ 个函数（MSE/PSNR/SSIM/WMSSSIM， 8u， C1/C3 等）
> - 完整的 GetBufferHostSize 变体（50+ 个）

**请参考头文件 `hgppist.h` 获取完整的函数列表。**

### 12.21. 错误码
| 错误码 | 说明 |
|--------|------|
| `HGPP_NULL_POINTER_ERROR` | 空指针错误 |
| `HGPP_STEP_ERROR` | 步幅错误 |
| `HGPP_SIZE_ERROR` | ROI 尺寸错误 |
| `HGPP_HISTOGRAM_NUMBER_OF_LEVELS_ERROR` | 直方图级别数 < 2 |
| `HGPP_DIVISOR_ERROR` | 除数为零 |
| `HGPP_QUALITY_INDEX_ERROR` | 图像像素为常数（无法计算质量指数） |
| `HGPP_MOMENT_00_ZERO_ERROR` | 零阶矩为零 |

比赛关联：MSE/PSNR/SSIM 及批量版本（MSEBatch/PSNRBatch/SSIMBatch）可直接在设备上量化"HGPP offload 预处理 vs CPU 参考预处理"的像素级差异，是精度保持取证和压测报告的现成工具。

## 13. 阈值与比较操作
> **库名称**: `hgppitc` 
> **功能**: 像素级阈值和比较操作方法  

### 13.1. 图像阈值操作
#### 13.1.1. 阈值原理
阈值操作根据比较结果设置像素值：

**对于非原图像操作：**
$$
\text{dstPixel} = \begin{cases} 
nThreshold & \text{if } (\text{sourcePixel } \text{OP } nThreshold) = \text{true} \\
\text{sourcePixel} & \text{otherwise}
\end{cases}
$$

**对于原图像操作：**
$$
\text{srcDstPixel} = \begin{cases} 
nThreshold & \text{if } (\text{sourcePixel } \text{OP } nThreshold) = \text{true} \\
\text{sourcePixel} & \text{otherwise}
\end{cases}
$$

其中 OP 是比较操作（`HGPP_CMP_LESS` 或 `HGPP_CMP_GREATER`）。

#### 13.1.2. 通用参数
| 参数 | 说明 |
|------|------|
| `pSrc` | 源图像指针 |
| `nSrcStep` | 源图像行步幅 |
| `pDst` | 目标图像指针 |
| `nDstStep` | 目标图像行步幅 |
| `pSrcDst` | 原图像操作 |
| `nSrcDstStep` | 原图像操作行步幅 |
| `oSizeROI` | 感兴趣区域 |
| `nThreshold` | 阈值 |
| `eComparisonOperation` | 比较操作类型（仅支持 `HGPP_CMP_LESS` 和 `HGPP_CMP_GREATER`） |
| `hgppStreamCtx` | 流上下文 |

#### 13.1.3. 函数列表
##### 13.1.3.1. 单通道阈值
```c
// 8 位无符号。
HgppStatus hgppiThreshold_8u_C1R_Ctx(...)
HgppStatus hgppiThreshold_8u_C1IR_Ctx(...)

// 16 位无符号。
HgppStatus hgppiThreshold_16u_C1R_Ctx(...)
HgppStatus hgppiThreshold_16u_C1IR_Ctx(...)

// 16 位有符号。
HgppStatus hgppiThreshold_16s_C1R_Ctx(...)
HgppStatus hgppiThreshold_16s_C1IR_Ctx(...)

// 32 位浮点。
HgppStatus hgppiThreshold_32f_C1R_Ctx(...)
HgppStatus hgppiThreshold_32f_C1IR_Ctx(...)
```

##### 13.1.3.2. 三通道阈值
```c
// 8 位无符号。
HgppStatus hgppiThreshold_8u_C3R_Ctx(...)    // rThresholds[3]
HgppStatus hgppiThreshold_8u_C3IR_Ctx(...)

// 16 位无符号。
HgppStatus hgppiThreshold_16u_C3R_Ctx(...)
HgppStatus hgppiThreshold_16u_C3IR_Ctx(...)

// 16 位有符号。
HgppStatus hgppiThreshold_16s_C3R_Ctx(...)
HgppStatus hgppiThreshold_16s_C3IR_Ctx(...)

// 32 位浮点。
HgppStatus hgppiThreshold_32f_C3R_Ctx(...)
HgppStatus hgppiThreshold_32f_C3IR_Ctx(...)
```

##### 13.1.3.3. 四通道阈值（不影响 Alpha）
```c
// 8 位无符号。
HgppStatus hgppiThreshold_8u_AC4R_Ctx(...)   // rThresholds[3]
HgppStatus hgppiThreshold_8u_AC4IR_Ctx(...)

// 16 位无符号。
HgppStatus hgppiThreshold_16u_AC4R_Ctx(...)
HgppStatus hgppiThreshold_16u_AC4IR_Ctx(...)

// 16 位有符号。
HgppStatus hgppiThreshold_16s_AC4R_Ctx(...)
HgppStatus hgppiThreshold_16s_AC4IR_Ctx(...)

// 32 位浮点。
HgppStatus hgppiThreshold_32f_AC4R_Ctx(...)
HgppStatus hgppiThreshold_32f_AC4IR_Ctx(...)
```

> **注意：**
> 多通道函数的阈值参数为数组 `rThresholds[3]`，每个通道一个阈值。

### 13.2. 图像比较操作
#### 13.2.1. 比较原理
比较操作对两个图像的像素进行比较：

$$
\text{dstPixel} = \begin{cases} 
nValue & \text{if } (\text{src1Pixel } \text{OP } \text{src2Pixel}) = \text{true} \\
0 & \text{otherwise}
\end{cases}
$$

其中 OP 可以是：
- `HGPP_CMP_LESS`（小于）
- `HGPP_CMP_LESS_EQ`（小于等于）
- `HGPP_CMP_EQ`（等于）
- `HGPP_CMP_GREATER_EQ`（大于等于）
- `HGPP_CMP_GREATER`（大于）

#### 13.2.2. 通用参数（比较操作）
| 参数 | 说明 |
|------|------|
| `pSrc1` | 源图像 1 指针 |
| `nSrc1Step` | 源图像 1 行步幅 |
| `pSrc2` | 源图像 2 指针 |
| `nSrc2Step` | 源图像 2 行步幅 |
| `pDst` | 目标图像指针 |
| `nDstStep` | 目标图像行步幅 |
| `oSizeROI` | ROI |
| `eComparisonOperation` | 比较操作类型 |
| `hgppStreamCtx` | 流上下文 |

#### 13.2.3. 函数列表
##### 13.2.3.1. 单通道比较
```c
// 8 位无符号。
HgppStatus hgppiCompare_8u_C1R_Ctx(...)

// 16 位无符号。
HgppStatus hgppiCompare_16u_C1R_Ctx(...)

// 16 位有符号。
HgppStatus hgppiCompare_16s_C1R_Ctx(...)

// 32 位浮点。
HgppStatus hgppiCompare_32f_C1R_Ctx(...)
```

##### 13.2.3.2. 多通道比较
```c
// 3 通道 8 位。
HgppStatus hgppiCompare_8u_C3R_Ctx(...)

// 4 通道 8 位。
HgppStatus hgppiCompare_8u_C4R_Ctx(...)

// 3 通道 16 位。
HgppStatus hgppiCompare_16u_C3R_Ctx(...)
HgppStatus hgppiCompare_16s_C3R_Ctx(...)

// 3 通道 32 位浮点。
HgppStatus hgppiCompare_32f_C3R_Ctx(...)
```

### 13.3. 阈值类型
**二值阈值（Binary Threshold）**

$$
\text{dstPixel} = \begin{cases} 
maxVal & \text{if } \text{srcPixel} > threshold \\
0 & \text{otherwise}
\end{cases}
$$

**截断阈值（Truncate Threshold）**

$$
\text{dstPixel} = \begin{cases} 
threshold & \text{if } \text{srcPixel} > threshold \\
\text{srcPixel} & \text{otherwise}
\end{cases}
$$

**反向二值阈值（Inverse Binary Threshold）**

$$
\text{dstPixel} = \begin{cases} 
0 & \text{if } \text{srcPixel} > threshold \\
maxVal & \text{otherwise}
\end{cases}
$$

### 13.4. 错误码
| 错误码 | 说明 |
|--------|------|
| `HGPP_NOT_SUPPORTED_MODE_ERROR` | 不支持的比较操作类型 |
| `HGPP_NULL_POINTER_ERROR` | 空指针 |
| `HGPP_STEP_ERROR` | 步幅错误 |
| `HGPP_SIZE_ERROR` | ROI 尺寸错误 |

