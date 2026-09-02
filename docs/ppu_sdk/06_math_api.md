# SAIL HGGC 数学函数库参考（Math API） <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [1. 数据结构](#1-数据结构)
- [2. FP8 内建函数](#2-fp8-内建函数)
  - [2.1. 枚举类型](#21-枚举类型)
  - [2.2. Typedef](#22-typedef)
  - [2.3. 转换函数](#23-转换函数)
  - [2.4. FP8 标量类型构造与转换运算符](#24-fp8-标量类型构造与转换运算符)
  - [2.5. FP8x2 / FP8x4 矢量类型构造与转换运算符](#25-fp8x2-fp8x4-矢量类型构造与转换运算符)
- [3. Half 精度内建函数](#3-half-精度内建函数)
  - [3.1. 宏定义](#31-宏定义)
  - [3.2. Half 算术函数](#32-half-算术函数)
  - [3.3. Half 比较函数](#33-half-比较函数)
  - [3.4. Half 数学函数](#34-half-数学函数)
  - [3.5. Half 转换函数](#35-half-转换函数)
  - [3.6. Half2 算术函数](#36-half2-算术函数)
  - [3.7. Half2 比较函数](#37-half2-比较函数)
  - [3.8. Half2 数学函数](#38-half2-数学函数)
- [4. Bfloat16 精度内建函数](#4-bfloat16-精度内建函数)
  - [4.1. 宏定义](#41-宏定义)
  - [4.2. Bfloat16 算术函数](#42-bfloat16-算术函数)
  - [4.3. Bfloat16 比较函数](#43-bfloat16-比较函数)
  - [4.4. Bfloat16 数学函数](#44-bfloat16-数学函数)
  - [4.5. Bfloat16 转换函数](#45-bfloat16-转换函数)
  - [4.6. Bfloat162 算术函数](#46-bfloat162-算术函数)
  - [4.7. Bfloat162 比较函数](#47-bfloat162-比较函数)
  - [4.8. Bfloat162 数学函数](#48-bfloat162-数学函数)
- [5. 单精度函数](#5-单精度函数)
  - [5.1. 单精度数学函数](#51-单精度数学函数)
  - [5.2. 单精度内建函数（快速/显式舍入版本）](#52-单精度内建函数快速显式舍入版本)
- [6. 双精度函数](#6-双精度函数)
  - [6.1. 双精度数学函数](#61-双精度数学函数)
  - [6.2. 双精度内建函数（显式舍入版本）](#62-双精度内建函数显式舍入版本)
- [7. 类型转换函数](#7-类型转换函数)
- [8. 整数函数](#8-整数函数)
  - [8.1. 整数数学函数](#81-整数数学函数)
  - [8.2. 整数内建函数](#82-整数内建函数)
- [9. SIMD 内建函数](#9-simd-内建函数)


本章覆盖 HGGC 设备端数学内建函数：FP8/FP16/BF16 低精度类型及其转换、单/双精度数学函数、整数函数与 SIMD 内建函数。函数如无特别说明均为 `__device__`；标注 `__host__ __device__` 的在主机端同样可用。舍入模式缩写：`rn`=向最近偶数舍入，`rd`=向下（向负无穷）舍入，`ru`=向上（向正无穷）舍入，`rz`=向零舍入。

## 1. 数据结构

| 类型 | 说明 |
|---|---|
| `__hg_fp8_e4m3` | 存储 e4m3 类 fp8 浮点数：1 位符号、4 位指数、1 位隐式 + 3 位显式尾数。编码不支持“无穷大”，NaN 仅限 0x7F 或 0xFF。 |
| `__hg_fp8_e5m2` | 存储 e5m2 类 fp8 浮点数：1 位符号、5 位指数、1 位隐式 + 2 位显式尾数。 |
| `__hg_fp8_e8m0` | 存储 e8m0 类型，即 8 bit 缩放因子（带偏移指数的二次幂）；偏移量 127，数值 0~254 代表 2^-127 ~ 2^127，0xFF 表示 NaN。 |
| `__hg_fp8x2_e4m3` / `__hg_fp8x2_e5m2` / `__hg_fp8x2_e8m0` | 存储及操作由两个对应 fp8 数值组成的矢量。 |
| `__hg_fp8x4_e4m3` / `__hg_fp8x4_e5m2` / `__hg_fp8x4_e8m0` | 存储及操作由四个对应 fp8 数值组成的矢量。 |
| `__half` | 半精度浮点类型，实现赋值、算术、比较算符及类型转换。共 16 位：1 符号、5 指数、10 尾数；总精度 11 位。区间 [0.0, 1.0] 内共有 15361 个可表示数字（含端点），约 log10(2^11) ≈ 3.311 位十进制精度。 |
| `__half2` | 存储两个半精度浮点数的类型。 |
| `__half_raw` | 按位字段表示 `short` 中的数值，而非转换为 `__half`。该表示方式将在未来 HGGC 版本中弃用。公共成员：`unsigned short x`（保存 half 浮点数的二进制位表示）。 |
| `__half2_raw` | `__half2` 的位字段表示形式，非从 `short2` 转换而来；将在未来 HGGC 版本中弃用。公共成员：`unsigned short x`（低半部分位信息）、`unsigned short y`（高半部分位信息）。 |
| `__ppu_bfloat16` | 存储 bfloat16 浮点数，支持赋值运算及类型转换。共 16 位：1 符号、8 指数、7 尾数；总精度 8 位。 |
| `__ppu_bfloat162` | 存储两个 `__ppu_bfloat16` 浮点数的类型。 |
| `__ppu_bfloat16_raw` | `__ppu_bfloat16` 的位域表示，非 `short` 转换而来；将在未来 HGGC 版本中弃用。公共成员：`unsigned short x`。 |
| `__ppu_bfloat162_raw` | `__ppu_bfloat162` 的位字段表示形式；将在未来 HGGC 版本中弃用。公共成员：`unsigned short x`（低半部分）、`unsigned short y`（高半部分）。 |

## 2. FP8 内建函数

### 2.1. 枚举类型

- `enum __hg_fp8_interpretation_t`
    - `__HG_E4M3`：代表 e4m3 的 fp8 数值。
    - `__HG_E5M2`：代表 e5m2 的 fp8 数值。
- `enum __hg_saturation_t`
    - `__HG_NOSAT`：转换结果超出目标数据类型范围并需舍入时，不对有限数值做饱和处理。
      注：对 e4m3 格式，转换结果超过该格式最大有限值时，结果被置为 NaN。
    - `__HG_SATFINITE`：输入值大于可表达的最大有限值时，舍入到最大有限值，符号与输入保持一致。
- `enum hggcRoundMode`
    - `hggcRoundNearest`：舍入到最近可表示值。
    - `hggcRoundZero`：向零舍入。
    - `hggcRoundPosInf`：向正无穷舍入。
    - `hggcRoundMinInf`：向负无穷舍入。

### 2.2. Typedef

| Typedef | 说明 |
|---|---|
| `typedef unsigned char __hg_fp8_storage_t` | 8 位无符号整数抽象，用于 FP8 浮点数存储。 |
| `typedef unsigned short int __hg_fp8x2_storage_t` | 16 位无符号整数抽象，用于存储 FP8 浮点数对。 |
| `typedef unsigned int __hg_fp8x4_storage_t` | 32 位无符号整数抽象，用于存储 FP8 浮点数四元组。 |

### 2.3. 转换函数

除特殊说明外均为 `__host__ __device__`；转换为 e4m3/e5m2 时使用最近偶数舍入和 `saturate` 参数指定的饱和模式；转换为 e8m0 时使用 `rounding`（hggcRoundMode）指定的舍入模式和 `saturate` 指定的饱和模式。

| 函数签名 | 说明 |
|---|---|
| `__hg_fp8x2_storage_t __hg_cvt_bfloat16raw2_to_fp8x2(const __ppu_bfloat162_raw x, const __hg_saturation_t saturate, const __hg_fp8_interpretation_t fp8_interpretation)` | 将打包的两个 `__ppu_bfloat16` 输入向量转换为 `fp8_interpretation` 指定类型的两个 fp8 值向量。 |
| `__hg_fp8_storage_t __hg_cvt_bfloat16raw_to_fp8(const __ppu_bfloat16_raw x, const __hg_saturation_t saturate, const __hg_fp8_interpretation_t fp8_interpretation)` | 将单个 `__ppu_bfloat16` 输入转换为指定类型 fp8。 |
| `__hg_fp8x2_storage_t __hg_cvt_bfloat162raw_to_e8m0x2(const __ppu_bfloat162_raw x, const __hg_saturation_t saturate, const enum hggcRoundMode rounding)` | 将两个 `__ppu_bfloat16` 输入向量转换为两个 e8m0 值向量。 |
| `__hg_fp8_storage_t __hg_cvt_bfloat16raw_to_e8m0(const __ppu_bfloat16_raw x, const __hg_saturation_t saturate, const enum hggcRoundMode rounding)` | 将单个 `__ppu_bfloat16` 输入转换为 e8m0。 |
| `__hg_fp8x2_storage_t __hg_cvt_double2_to_e8m0x2(const double2 x, const __hg_saturation_t saturate, const enum hggcRoundMode rounding)` | 将 `double2` 中两个双精度数转换为两个 e8m0 值向量。 |
| `__hg_fp8_storage_t __hg_cvt_double_to_e8m0(const double x, const __hg_saturation_t saturate, const enum hggcRoundMode rounding)` | 将双精度 x 转换为 e8m0。 |
| `__ppu_bfloat16_raw __hg_cvt_e8m0_to_bf16raw(const __hg_fp8_storage_t x)` | 将 e8m0 转换为 `__ppu_bfloat16`。e8m0 仅含指数位，转换为 bfloat16 是精确映射，无需舍入。 |
| `__ppu_bfloat162_raw __hg_cvt_e8m0x2_to_bf162raw(const __hg_fp8x2_storage_t x)` | 将两个 e8m0 值向量转换为 `__ppu_bfloat162_raw` 打包的两个 `__ppu_bfloat16` 值；精确映射，无需舍入。 |
| `__hg_fp8x2_storage_t __hg_cvt_float2_to_e8m0x2(const float2 x, const __hg_saturation_t saturate, const enum hggcRoundMode rounding)` | 将 `float2` 中两个单精度数转换为两个 e8m0 值向量。 |
| `__hg_fp8_storage_t __hg_cvt_float_to_e8m0(const float x, const __hg_saturation_t saturate, const enum hggcRoundMode rounding)` | 将单精度 x 转换为 e8m0。 |
| `__hg_fp8x2_storage_t __hg_cvt_double2_to_fp8x2(const double2 x, const __hg_saturation_t saturate, const __hg_fp8_interpretation_t fp8_interpretation)` | 将 `double2` 中两个双精度数转换为指定类型的两个 fp8 值向量。 |
| `__hg_fp8_storage_t __hg_cvt_double_to_fp8(const double x, const __hg_saturation_t saturate, const __hg_fp8_interpretation_t fp8_interpretation)` | 将双精度 x 转换为指定类型 fp8。 |
| `__hg_fp8x2_storage_t __hg_cvt_float2_to_fp8x2(const float2 x, const __hg_saturation_t saturate, const __hg_fp8_interpretation_t fp8_interpretation)` | 将 `float2` 中两个单精度数转换为指定类型的两个 fp8 值向量。 |
| `__hg_fp8_storage_t __hg_cvt_float_to_fp8(const float x, const __hg_saturation_t saturate, const __hg_fp8_interpretation_t fp8_interpretation)` | 将单精度 x 转换为指定类型 fp8。 |
| `__half_raw __hg_cvt_fp8_to_halfraw(const __hg_fp8_storage_t x, const __hg_fp8_interpretation_t fp8_interpretation)` | 将指定类型的 fp8 输入转换为 half 精度。 |
| `__half2_raw __hg_cvt_fp8x2_to_halfraw2(const __hg_fp8x2_storage_t x, const __hg_fp8_interpretation_t fp8_interpretation)` | 将两个指定类型 fp8 值向量转换为 `__half2_raw` 打包的两个 half 值。 |
| `__hg_fp8x2_storage_t __hg_cvt_halfraw2_to_fp8x2(const __half2_raw x, const __hg_saturation_t saturate, const __hg_fp8_interpretation_t fp8_interpretation)` | 将 `__half2_raw` 中两个半精度数转换为指定类型的两个 fp8 值向量。 |
| `__hg_fp8_storage_t __hg_cvt_halfraw_to_fp8(const __half_raw x, const __hg_saturation_t saturate, const __hg_fp8_interpretation_t fp8_interpretation)` | 将单个半精度输入转换为指定类型 fp8。 |

### 2.4. FP8 标量类型构造与转换运算符

`__hg_fp8_e4m3`、`__hg_fp8_e5m2`、`__hg_fp8_e8m0` 三个标量类型的接口完全一致：

- 构造函数（均 `__host__ __device__`，除默认构造外，对超出范围的值依赖 `__HG_SATFINITE` 行为）：
  - 默认构造：`__hg_fp8_e4m3() = default`（e5m2、e8m0 同）
  - 从以下类型构造：`int`、`unsigned int`、`short int`、`unsigned short int`、`long int`、`unsigned long int`、`long long int`、`unsigned long long int`、`float`、`double`、`__half`、`__ppu_bfloat16`。
  - 注：`__hg_fp8_e5m2` 从 `short int` 构造的条目未标注 `__HG_SATFINITE` 行为。
- 转换运算符（均 `__host__ __device__ ... () const`）：
  - `operator __half()`、`operator __ppu_bfloat16()`、`operator bool()`、`operator char()`（实现定义）、`operator double()`、`operator float()`、`operator int()`、`operator long int()`、`operator long long int()`、`operator short int()`、`operator signed char()`、`operator unsigned char()`、`operator unsigned int()`、`operator unsigned long int()`、`operator unsigned long long int()`、`operator unsigned short int()`。

### 2.5. FP8x2 / FP8x4 矢量类型构造与转换运算符

`__hg_fp8x2_e4m3`、`__hg_fp8x2_e5m2`、`__hg_fp8x2_e8m0` 接口一致：

- 构造函数（均 `__host__ __device__`，超范围值依赖 `__HG_SATFINITE`）：
  - 默认构造 `() = default`；
  - `__hg_fp8x2_X(const __ppu_bfloat162 f)`、`(const double2 f)`、`(const __half2 f)`、`(const float2 f)`。
- 转换运算符：`operator __half2() const`、`operator float2() const`。

`__hg_fp8x4_e4m3`、`__hg_fp8x4_e5m2`、`__hg_fp8x4_e8m0` 接口一致：

- 构造函数（均 `__host__ __device__`，超范围值依赖 `__HG_SATFINITE`）：
  - 默认构造 `() = default`；
  - `__hg_fp8x4_X(const __ppu_bfloat162 flo, const __ppu_bfloat162 fhi)`（从一对 `__ppu_bfloat162` 构造）；
  - `(const double4 f)`、`(const float4 f)`、`(const __half2 flo, const __half2 fhi)`（从一对 `__half2` 构造）。
- 转换运算符：`operator float4() const`。

比赛关联：FP8（e4m3/e5m2/e8m0）是量化压缩权重与 KV cache 的候选精度。e8m0 对应 MX 格式的 per-block 二次幂缩放因子，与 bf16 之间是精确映射；写自定义量化 kernel 时用 `__hg_cvt_*` 系列转换并注意 `__HG_SATFINITE` 与 e4m3 溢出变 NaN 的行为差异，直接影响精度保持得分。

## 3. Half 精度内建函数

### 3.1. 宏定义

| 宏 | 值 | 说明 |
|---|---|---|
| `HGGCRT_INF_FP16` | `__ushort_as_half((unsigned short)0x7C00U)` | 半精度浮点正无穷。 |
| `HGGCRT_MAX_NORMAL_FP16` | `__ushort_as_half((unsigned short)0x7BFFU)` | 半精度最大可表示值。 |
| `HGGCRT_MIN_DENORM_FP16` | `__ushort_as_half((unsigned short)0x0001U)` | 半精度最小可表示（非归一化）值。 |
| `HGGCRT_NAN_FP16` | `__ushort_as_half((unsigned short)0x7FFFU)` | 半精度典型 NaN。 |
| `HGGCRT_NEG_ZERO_FP16` | `__ushort_as_half((unsigned short)0x8000U)` | 半精度负零。 |
| `HGGCRT_ONE_FP16` | `__ushort_as_half((unsigned short)0x3C00U)` | 半精度 1.0。 |
| `HGGCRT_ZERO_FP16` | `__ushort_as_half((unsigned short)0x0000U)` | 半精度正零。 |

### 3.2. Half 算术函数

除 `__hfma*` 为 `__device__` 外均为 `__host__ __device__`。均以向最近偶数舍入模式计算。

| 函数 | 签名 | 说明 |
|---|---|---|
| `__habs` | `__half __habs(const __half a)` | 绝对值。`__habs(±0)=+0`，`__habs(±∞)=+∞`，`__habs(NaN)=NaN`。 |
| `__hadd` | `__half __hadd(const __half a, const __half b)` | 加法。 |
| `__hadd_rn` | `__half __hadd_rn(const __half a, const __half b)` | 加法；防止 mul+add 收缩为 fma。 |
| `__hadd_sat` | `__half __hadd_sat(const __half a, const __half b)` | 加法并饱和到 [0.0, 1.0]；NaN 结果刷新为 +0.0。 |
| `__hdiv` | `__half __hdiv(const __half a, const __half b)` | 除法 a/b。 |
| `__hfma` | `__half __hfma(const __half a, const __half b, const __half c)` | 融合乘加 a*b+c，结果只舍入一次。 |
| `__hfma_relu` | `__half __hfma_relu(const __half a, const __half b, const __half c)` | 融合乘加后负结果钳为 0；NaN 结果转换为规范 NaN。 |
| `__hfma_sat` | `__half __hfma_sat(const __half a, const __half b, const __half c)` | 融合乘加并饱和到 [0.0, 1.0]；NaN 结果刷新为 +0.0。 |
| `__hmul` | `__half __hmul(const __half a, const __half b)` | 乘法。 |
| `__hmul_rn` | `__half __hmul_rn(const __half a, const __half b)` | 乘法；防止 mul+add 或 sub 收缩为 fma。 |
| `__hmul_sat` | `__half __hmul_sat(const __half a, const __half b)` | 乘法并饱和到 [0.0, 1.0]；NaN 结果刷新为 +0.0。 |
| `__hneg` | `__half __hneg(const __half a)` | 取负。`__hneg(±0)=∓0`，`__hneg(±∞)=∓∞`，`__hneg(NaN)=NaN`。 |
| `__hsub` | `__half __hsub(const __half a, const __half b)` | 减法。 |
| `__hsub_rn` | `__half __hsub_rn(const __half a, const __half b)` | 减法（rn）。 |
| `__hsub_sat` | `__half __hsub_sat(const __half a, const __half b)` | 减法并饱和到 [0.0, 1.0]；NaN 结果刷新为 +0.0。 |
| `atomicAdd` | `__device__ __half atomicAdd(__half *const address, const __half val)` | 将 val 原子加到全局或共享内存 address 处，返回旧值。address 必须在全局或共享内存，否则未定义行为。详见 HGGC C++ 编程指南原子函数部分。 |

算术运算符重载（均 `__host__ __device__`）：

| 运算符 | 签名 | 说明 |
|---|---|---|
| `operator*` | `__half operator*(const __half &lh, const __half &rh)` | 乘法。 |
| `operator*=` | `__half & operator*=(__half &lh, const __half &rh)` | 复合赋值乘法。 |
| `operator+` | `__half operator+(const __half &h)` | 一元加，返回输入值。 |
| `operator+` | `__half operator+(const __half &lh, const __half &rh)` | 加法。 |
| `operator++` | `__half & operator++(__half &h)` | 前缀自增。 |
| `operator++` | `__half operator++(__half &h, const int ignored)` | 后缀自增。 |
| `operator+=` | `__half & operator+=(__half &lh, const __half &rh)` | 复合赋值加法。 |
| `operator-` | `__half operator-(const __half &lh, const __half &rh)` | 减法。 |
| `operator-` | `__half operator-(const __half &h)` | 一元减。 |
| `operator--` | `__half operator--(__half &h, const int ignored)` | 后缀自减。 |
| `operator--` | `__half & operator--(__half &h)` | 前缀自减。 |
| `operator-=` | `__half & operator-=(__half &lh, const __half &rh)` | 复合赋值减法。 |
| `operator/` | `__half operator/(const __half &lh, const __half &rh)` | 除法。 |
| `operator/=` | `__half & operator/=(__half &lh, const __half &rh)` | 复合赋值除法。 |

### 3.3. Half 比较函数

均 `__host__ __device__`，参数 `(const __half a, const __half b)`（`__hisinf`/`__hisnan` 为单参数）。

| 函数 | 返回 | 说明 |
|---|---|---|
| `__heq` | bool | 相等比较；NaN 输入生成 false。 |
| `__hequ` | bool | 无序相等比较；NaN 输入生成 true。 |
| `__hge` | bool | 大于等于；NaN → false。 |
| `__hgeu` | bool | 无序大于等于；NaN → true。 |
| `__hgt` | bool | 大于；NaN → false。 |
| `__hgtu` | bool | 无序大于；NaN → true。 |
| `__hisinf` | int | 是否无穷大：-∞ 返回 -1，+∞ 返回 1，否则 0。 |
| `__hisnan` | bool | 是否为 NaN。 |
| `__hle` | bool | 小于等于；NaN → false。 |
| `__hleu` | bool | 无序小于等于；NaN → true。 |
| `__hlt` | bool | 小于；NaN → false。 |
| `__hltu` | bool | 无序小于；NaN → true。 |
| `__hmax` | `__half` | max(a,b) = (a>b)?a:b。任一输入 NaN 返回另一个；都 NaN 返回规范 NaN；两输入均 0.0 时 +0.0 > -0.0。 |
| `__hmax_nan` | `__half` | 同上但 NaN 传递：任一输入 NaN 返回规范 NaN。 |
| `__hmin` | `__half` | min(a,b) = (a<b)?a:b；NaN 行为同 `__hmax`。 |
| `__hmin_nan` | `__half` | 同上但 NaN 传递。 |
| `__hne` | bool | 不等比较；NaN → false。 |
| `__hneu` | bool | 无序不等比较；NaN → true。 |

比较运算符重载（均 `__host__ __device__ bool`，参数 `(const __half &lh, const __half &rh)`）：`operator!=`（无序不等）、`operator<`（有序小于）、`operator<=`（有序小于等于）、`operator==`（有序相等）、`operator>`（有序大于）、`operator>=`（有序大于等于）。

### 3.4. Half 数学函数

均 `__device__`，单参数 `__half`。

| 函数 | 说明 | 特殊值 |
|---|---|---|
| `hceil(h)` | 上取整 | `hceil(±0)=±0`，`hceil(±∞)=±∞`，NaN→NaN |
| `hcos(a)` | 余弦（rn） | `hcos(±0)=1`，`hcos(±∞)=NaN`，NaN→NaN |
| `hexp(a)` | 自然指数 e^a（rn） | `hexp(±0)=1`，`hexp(−∞)=+0`，`hexp(+∞)=+∞`，NaN→NaN |
| `hexp10(a)` | 十进制指数 10^a（rn） | 同 hexp 的特殊值 |
| `hexp2(a)` | 二进制指数 2^a（rn） | 同 hexp 的特殊值 |
| `hfloor(h)` | 下取整 | `hfloor(±0)=±0`，`hfloor(±∞)=±∞`，NaN→NaN |
| `hlog(a)` | 自然对数 ln(a)（rn） | `hlog(±0)=−∞`，`hlog(1)=+0`，x<0 →NaN，`hlog(+∞)=+∞`，NaN→NaN |
| `hlog10(a)` | 十进制对数 log10(a)（rn） | 同 hlog 的特殊值 |
| `hlog2(a)` | 二进制对数 log2(a)（rn） | 同 hlog 的特殊值 |
| `hrcp(a)` | 倒数 1/a（rn） | `hrcp(±0)=±∞`，`hrcp(±∞)=±0`，NaN→NaN |
| `hrint(h)` | 舍入到最近整数（中间情况舍入到偶整数） | `hrint(±0)=±0`，`hrint(±∞)=±∞`，NaN→NaN |
| `hrsqrt(a)` | 平方根倒数 1/√a（rn） | `hrsqrt(±0)=±∞`，`hrsqrt(+∞)=+0`，x<0→NaN，NaN→NaN |
| `hsin(a)` | 正弦（rn） | `hsin(±0)=±0`，`hsin(±∞)=NaN`，NaN→NaN |
| `hsqrt(a)` | 平方根 √a（rn） | `hsqrt(+∞)=+∞`，`hsqrt(±0)=±0`，x<0→NaN，NaN→NaN |
| `htrunc(h)` | 截断为整数部分（幅度不超过 h 的最大整数） | `htrunc(±0)=±0`，`htrunc(±∞)=±∞`，NaN→NaN |

### 3.5. Half 转换函数

#### 3.5.1. float/double → half

| 函数 | 签名 | 说明 |
|---|---|---|
| `__double2half` | `__half __double2half(const double a)` | double→half（rn）。`±0→±0`，`±∞→±∞`，NaN→NaN。 |
| `__float22half2_rn` | `__half2 __float22half2_rn(const float2 a)` | float2 两分量→half2（rn）。低 16 位对应 a.x，高 16 位对应 a.y。 |
| `__float2half` | `__half __float2half(const float a)` | float→half（rn）。 |
| `__float2half2_rn` | `__half2 __float2half2_rn(const float a)` | float→half 并填充 half2 两个半部（rn）。 |
| `__float2half_rd` / `__float2half_rn` / `__float2half_ru` / `__float2half_rz` | `__half __float2half_XX(const float a)` | float→half，分别向下/最近偶数/向上/向零舍入。`±0→±0`，`±∞→±∞`，NaN→NaN。 |
| `__floats2half2_rn` | `__half2 __floats2half2_rn(const float a, const float b)` | 两个 float→half2（rn）。低 16 位对应 a，高 16 位对应 b。 |
| `__half22float2` | `float2 __half22float2(const __half2 a)` | half2 两个 half→float2。 |
| `__half2float` | `float __half2float(const __half a)` | half→float。`±0→±0`，`±∞→±∞`，NaN→NaN。 |
| `__half2half2` | `__half2 __half2half2(const __half a)` | 返回两个半部都等于 a 的 half2。 |

#### 3.5.2. half ↔ 整数

half→整数时 NaN 输入转换为 0（ll/ull 系列 NaN 返回 0x8000000000000000）。

| 函数 | 返回类型 | 舍入 | 饱和行为 |
|---|---|---|---|
| `__half2char_rz` | signed char | rz | ±0→0；x>127→SCHAR_MAX=0x7F；x<−128→SCHAR_MIN=0x80；NaN→0 |
| `__half2int_rd` / `__half2int_rn` / `__half2int_ru` / `__half2int_rz` | int | rd/rn/ru/rz | ±0→0；+∞→INT_MAX=0x7FFFFFFF；−∞→INT_MIN=0x80000000；NaN→0 |
| `__half2ll_rd` / `__half2ll_rn` / `__half2ll_ru` / `__half2ll_rz` | long long int | rd/rn/ru/rz | ±0→0；+∞→LLONG_MAX=0x7FFFFFFFFFFFFFFF；−∞→LLONG_MIN=0x8000000000000000；NaN→0x8000000000000000 |
| `__half2short_rd` / `__half2short_rn` / `__half2short_ru` / `__half2short_rz` | short int | rd/rn/ru/rz | ±0→0；x>32767→SHRT_MAX=0x7FFF；x<−32768→SHRT_MIN=0x8000；NaN→0 |
| `__half2uchar_rz` | unsigned char | rz | ±0→0；x>255→UCHAR_MAX=0xFF；x<0→0；NaN→0 |
| `__half2uint_rd` / `__half2uint_rn` / `__half2uint_ru` / `__half2uint_rz` | unsigned int | rd/rn/ru/rz | ±0→0；+∞→UINT_MAX=0xFFFFFFFF；x<0→0；NaN→0 |
| `__half2ull_rd` / `__half2ull_rn` / `__half2ull_ru` / `__half2ull_rz` | unsigned long long int | rd/rn/ru/rz | ±0→0；+∞→ULLONG_MAX=0xFFFFFFFFFFFFFFFF；x<0→0；NaN→0x8000000000000000 |
| `__half2ushort_rd` / `__half2ushort_rn` / `__half2ushort_ru` / `__half2ushort_rz` | unsigned short int | rd/rn/ru/rz | ±0→0；+∞→USHRT_MAX=0xFFFF；x<0→0；NaN→0 |
| `__half_as_short` | short int | — | 位重新解释（bit reinterpret）。 |
| `__half_as_ushort` | unsigned short int | — | 位重新解释。 |

整数→half（参数均为对应整型 `i`，返回 `__half`）：

| 函数 | 输入类型 | 舍入 |
|---|---|---|
| `__int2half_rd` / `__int2half_rn` / `__int2half_ru` / `__int2half_rz` | int | rd/rn/ru/rz |
| `__ll2half_rd` / `__ll2half_rn` / `__ll2half_ru` / `__ll2half_rz` | long long int | rd/rn/ru/rz |
| `__short2half_rd` / `__short2half_rn` / `__short2half_ru` / `__short2half_rz` | short int | rd/rn/ru/rz |
| `__short_as_half` | short int | 位重新解释 |
| `__uint2half_rd` / `__uint2half_rn` / `__uint2half_ru` / `__uint2half_rz` | unsigned int | rd/rn/ru/rz |
| `__ull2half_rd` / `__ull2half_rn` / `__ull2half_ru` / `__ull2half_rz` | unsigned long long int | rd/rn/ru/rz |
| `__ushort2half_rd` / `__ushort2half_rn` / `__ushort2half_ru` / `__ushort2half_rz` | unsigned short int | rd/rn/ru/rz |
| `__ushort_as_half` | unsigned short int | 位重新解释 |

以上整数→half 与位重解释函数均 `__host__ __device__`；half→int 系列中 `_rd/_rn/_ru` 为 `__device__`，`_rz` 为 `__host__ __device__`。

#### 3.5.3. half2 打包/拆包

| 函数 | 签名 | 说明 |
|---|---|---|
| `__halves2half2` | `__half2 __halves2half2(const __half a, const __half b)` | 组合两个 half 为 half2；a 存低 16 位，b 存高 16 位。 |
| `__high2float` | `float __high2float(const __half2 a)` | 高 16 位→float。 |
| `__high2half` | `__half __high2half(const __half2 a)` | 返回高 16 位。 |
| `__high2half2` | `__half2 __high2half2(const __half2 a)` | 提取高 16 位并复制到两半部。 |
| `__highs2half2` | `__half2 __highs2half2(const __half2 a, const __half2 b)` | 各取高 16 位组合；a 高部位→结果低 16 位，b 高部位→结果高 16 位。 |
| `__low2float` | `float __low2float(const __half2 a)` | 低 16 位→float。 |
| `__low2half` | `__half __low2half(const __half2 a)` | 返回低 16 位。 |
| `__low2half2` | `__half2 __low2half2(const __half2 a)` | 提取低 16 位并复制到两半部。 |
| `__lowhigh2highlow` | `__half2 __lowhigh2highlow(const __half2 a)` | 交换两个半部。 |
| `__lows2half2` | `__half2 __lows2half2(const __half2 a, const __half2 b)` | 各取低 16 位组合；a 低部位→结果低 16 位，b 低部位→结果高 16 位。 |
| `make_half2` | `__half2 make_half2(const __half x, const __half y)` | 组合为 half2；x 存低 16 位，y 存高 16 位。 |

#### 3.5.4. 缓存修饰加载/存储

均 `__device__`，`ptr` 为内存位置；加载类返回 ptr 指向的值，存储类 `void __stXX(T *const ptr, const T value)`。每个函数都有 `__half` 与 `__half2` 两个重载。

| 函数 | 生成指令 |
|---|---|
| `__ldca` | ld.global.ca |
| `__ldcg` | ld.global.cg |
| `__ldcs` | ld.global.cs |
| `__ldcv` | ld.global.cv |
| `__ldg` | ld.global.nc |
| `__ldlu` | ld.global.lu |
| `__stcg` | st.global.cg |
| `__stcs` | st.global.cs |
| `__stwb` | st.global.wb |
| `__stwt` | st.global.wt |

#### 3.5.5. Warp Shuffle（half/half2）

均 `__device__`。每个函数有 `__half`（返回 2 字节字）和 `__half2`（返回 4 字节字）两个重载。通用参数约束：`mask` 指示参与调用的线程，每个参与线程必须设置自己 lane id 对应的位；mask 中所有未退出线程必须以相同 mask 执行相同内在函数，否则结果未定义。线程只能从积极参与 `__shfl_*_sync()` 的另一个线程读取数据；目标线程不活动时检索值未定义。

| 函数 | 签名 | 说明 |
|---|---|---|
| `__shfl_down_sync` | `T __shfl_down_sync(const unsigned int mask, const T var, const unsigned int delta, const int width=warpSize)` | 从更高 ID 线程复制（源 = 调用者+delta），相当于 var 向下移动 delta 个线程。width < warpSize 时每个子部分独立（起始逻辑线程 ID 为 0）；源线程 ID 不回绕，上部 delta 线程保持不变。 |
| `__shfl_sync` | `T __shfl_sync(const unsigned int mask, const T var, const int srcLane, const int width=warpSize)` | 直接从 srcLane 指定的线程复制。srcLane 超出 [0:width-1] 时取 srcLane 模 width。width 必须为 2 的幂且不大于 warpSize，否则结果未定义。 |
| `__shfl_up_sync` | `T __shfl_up_sync(const unsigned int mask, const T var, const unsigned int delta, const int width=warpSize)` | 从更低 ID 线程复制（源 = 调用者-delta），var 向上移动 delta 个线程。源索引不回绕，较低 delta 线程保持不变。width 约束同上。 |
| `__shfl_xor_sync` | `T __shfl_xor_sync(const unsigned int mask, const T var, const int laneMask, const int width=warpSize)` | 源 = 调用者线程 ID 与 laneMask 按位 XOR，实现蝴蝶寻址模式（用于树归约和广播）。width < warpSize 时每组 width 个连续线程可访问早期线程组元素，访问后期线程组元素则返回自己的 var。 |

#### 3.5.6. `__half` / `__half2` 类构造与赋值

`__half`：

- 构造函数（均 `__host__ __device__`，数值输入使用默认最近偶数舍入）：
  - `constexpr __half(const __half_raw &hr)`：从 `__half_raw` 构造；
  - 从 `float`、`double`、`int`、`unsigned int`、`short`、`unsigned short`、`long`、`unsigned long`、`long long`、`unsigned long long`、`__ppu_bfloat16` 构造；
  - `__half() = default`。
- 转换运算符：`operator __half_raw() const`、`operator __half_raw() const volatile`；以及 `operator bool()`（constexpr）、`char`、`float`、`int`、`long`、`long long`、`short`、`signed char`、`unsigned char`、`unsigned int`、`unsigned long`、`unsigned long long`、`unsigned short`，均 `() const`。
- 赋值运算符 `operator=`：从 `float`、`double`、`int`、`unsigned int`、`short`、`unsigned short`、`long long`、`unsigned long long`、`__half_raw` 赋值（数值类型使用默认最近偶数舍入）；volatile 变体：`volatile __half & operator=(const __half_raw &hr) volatile`、`volatile __half & operator=(const volatile __half_raw &hr) volatile`。

`__half2`：

- 构造函数：`__half2(const __half2_raw &h2r)`；`constexpr __half2(const __half &a, const __half &b)`；移动构造 `__half2(const __half2 &&src)`（C++11+）；拷贝构造 `__half2(const __half2 &src)`；`__half2() = default`。
- 转换运算符：`operator __half2_raw() const`。
- 赋值运算符：`operator=(const __half2_raw &h2r)`；移动赋值 `operator=(const __half2 &&src)`（C++11+）；拷贝赋值 `operator=(const __half2 &src)`。

### 3.6. Half2 算术函数

除 `__hcmadd`/`__hfma2*` 为 `__device__` 外均 `__host__ __device__`。均以向最近偶数舍入模式逐元素计算。

| 函数 | 签名 | 说明 |
|---|---|---|
| `__h2div` | `__half2 __h2div(const __half2 a, const __half2 b)` | 逐元素除法。 |
| `__habs2` | `__half2 __habs2(const __half2 a)` | 两个半部取绝对值。 |
| `__hadd2` | `__half2 __hadd2(const __half2 a, const __half2 b)` | 向量加法。 |
| `__hadd2_rn` | `__half2 __hadd2_rn(const __half2 a, const __half2 b)` | 向量加法；防止 mul+add 收缩为 fma。 |
| `__hadd2_sat` | `__half2 __hadd2_sat(const __half2 a, const __half2 b)` | 向量加法并饱和到 [0.0, 1.0]；NaN 刷新为 +0.0。 |
| `__hcmadd` | `__half2 __hcmadd(const __half2 a, const __half2 b, const __half2 c)` | 快速复数乘加。将 half2 解释为复数 (a.x+I·a.y) 等，计算 a*b+c，数值上等同于：`result.x = __hfma(-a.y, b.y, __hfma(a.x, b.x, c.x))`；`result.y = __hfma(a.y, b.x, __hfma(a.x, b.y, c.y))`。 |
| `__hfma2` | `__half2 __hfma2(const __half2 a, const __half2 b, const __half2 c)` | 逐元素融合乘加，结果只舍入一次。 |
| `__hfma2_relu` | `__half2 __hfma2_relu(const __half2 a, const __half2 b, const __half2 c)` | 融合乘加后负结果钳为 0；NaN 转规范 NaN。 |
| `__hfma2_sat` | `__half2 __hfma2_sat(const __half2 a, const __half2 b, const __half2 c)` | 融合乘加并饱和到 [0.0, 1.0]；NaN 刷新为 +0.0。 |
| `__hmul2` | `__half2 __hmul2(const __half2 a, const __half2 b)` | 逐元素乘法。 |
| `__hmul2_rn` | `__half2 __hmul2_rn(const __half2 a, const __half2 b)` | 逐元素乘法（rn）。 |
| `__hmul2_sat` | `__half2 __hmul2_sat(const __half2 a, const __half2 b)` | 逐元素乘法并饱和到 [0.0, 1.0]；NaN 刷新为 +0.0。 |
| `__hneg2` | `__half2 __hneg2(const __half2 a)` | 两个半部取负。 |
| `__hsub2` | `__half2 __hsub2(const __half2 a, const __half2 b)` | 向量减法。 |
| `__hsub2_rn` | `__half2 __hsub2_rn(const __half2 a, const __half2 b)` | 向量减法；防止 mul+sub 收缩为 fma。 |
| `__hsub2_sat` | `__half2 __hsub2_sat(const __half2 a, const __half2 b)` | 向量减法并饱和到 [0.0, 1.0]；NaN 刷新为 +0.0。 |
| `atomicAdd` | `__device__ __half2 atomicAdd(__half2 *const address, const __half2 val)` | 原子加，返回旧值。原子性仅对两个 `__half` 元素分别保证；整个 `__half2` 不保证作为单个 32 位访问的原子性。address 必须在全局或共享内存。详见 HGGC C++ 编程指南原子函数部分。 |

运算符重载（均 `__host__ __device__`，packed `__half` 语义，等价于对应 `__hmul2/__hadd2/__hsub2/__h2div/__hneg2/__hbneu2` 等函数）：`operator*`、`operator*=`、`operator+`（一元与二元）、`operator++`（前缀/后缀）、`operator+=`、`operator-`（一元与二元）、`operator--`（前缀/后缀）、`operator-=`、`operator/`、`operator/=`。

### 3.7. Half2 比较函数

均 `__host__ __device__`，参数 `(const __half2 a, const __half2 b)`。`__hb*2` 系列返回 bool（仅当两个 half 比较都为 true 时返回 true）；`__h*2` 系列返回 half2（对应 half 结果置 1.0 表示 true、0.0 表示 false）。

| 函数 | 返回 | 说明 |
|---|---|---|
| `__hbeq2` | bool | 向量相等（两个 half 都为 true 才为 true）；NaN → false。 |
| `__hbequ2` | bool | 无序向量相等；NaN → true。 |
| `__hbge2` / `__hbgeu2` | bool | 向量大于等于 / 无序；NaN → false / true。 |
| `__hbgt2` / `__hbgtu2` | bool | 向量大于 / 无序；NaN → false / true。 |
| `__hble2` / `__hbleu2` | bool | 向量小于等于 / 无序；NaN → false / true。 |
| `__hblt2` / `__hbltu2` | bool | 向量小于 / 无序；NaN → false / true。 |
| `__hbne2` / `__hbneu2` | bool | 向量不等 / 无序；NaN → false / true。 |
| `__heq2` / `__hequ2` | `__half2` | 逐元素相等 / 无序（1.0/0.0）；NaN → false / true。 |
| `__hge2` / `__hgeu2` | `__half2` | 逐元素大于等于 / 无序；NaN → false / true。 |
| `__hgt2` / `__hgtu2` | `__half2` | 逐元素大于 / 无序；NaN → false / true。 |
| `__hisnan2` | `__half2` | 判断每个 half 是否 NaN：是则对应位置 1.0，否则 0.0。 |
| `__hle2` / `__hleu2` | `__half2` | 逐元素小于等于 / 无序；NaN → false / true。 |
| `__hlt2` / `__hltu2` | `__half2` | 逐元素小于 / 无序；NaN → false / true。 |
| `__hmax2` | `__half2` | 逐元素 max，(a>b)?a:b；任一输入 NaN 返回另一个，都 NaN 返回规范 NaN；两输入均 0.0 时 +0.0 > -0.0。 |
| `__hmax2_nan` | `__half2` | 同上但 NaN 传递（任一 NaN 返回规范 NaN）。 |
| `__hmin2` | `__half2` | 逐元素 min，(a<b)?a:b；NaN 行为同 `__hmax2`。 |
| `__hmin2_nan` | `__half2` | 同上但 NaN 传递。 |
| `__hne2` / `__hneu2` | `__half2` | 逐元素不等 / 无序；NaN → false / true。 |

比较运算符重载（均 `__host__ __device__ bool`，参数 `(const __half2 &lh, const __half2 &rh)`）：`operator!=`（无序不等，见 `__hbneu2`）、`operator<`（有序小于，见 `__hblt2`）、`operator<=`（见 `__hble2`）、`operator==`（见 `__hbeq2`）、`operator>`（见 `__hbgt2`）、`operator>=`（见 `__hbge2`）。

### 3.8. Half2 数学函数

均 `__device__`，参数 `const __half2`，返回 `__half2`，逐元素以向最近偶数舍入模式计算，语义与对应标量 half 数学函数一致：

| 函数 | 对应标量 | 函数 | 对应标量 |
|---|---|---|---|
| `h2ceil` | hceil（上取整） | `h2log2` | hlog2（log2） |
| `h2cos` | hcos | `h2rcp` | hrcp（倒数） |
| `h2exp` | hexp | `h2rint` | hrint（最近整数舍入） |
| `h2exp10` | hexp10 | `h2rsqrt` | hrsqrt（平方根倒数） |
| `h2exp2` | hexp2 | `h2sin` | hsin |
| `h2floor` | hfloor | `h2sqrt` | hsqrt |
| `h2log` | hlog | `h2trunc` | htrunc（截断） |
| `h2log10` | hlog10 | | |

比赛关联：half/half2 是 VLM 推理主计算精度之一。写自定义 kernel 时注意三点：`_rn` 后缀版本可阻止编译器把 mul+add 收缩成 fma（保证与参考实现逐位一致的精度）；`_sat`/`_relu` 变体可融合激活裁剪；`__ldg/__ldca/__ldcs` 等缓存修饰加载用于权重与 KV 读路径的缓存控制，`__stwt/__stcg` 用于流式写出，直接影响吞吐。

## 4. Bfloat16 精度内建函数

接口与 Half 系列完全平行，类型换为 `__ppu_bfloat16` / `__ppu_bfloat162`。

### 4.1. 宏定义

| 宏 | 值 | 说明 |
|---|---|---|
| `HGGCRT_INF_BF16` | `__ushort_as_bfloat16((unsigned short)0x7F80U)` | bfloat16 浮点正无穷。 |
| `HGGCRT_MAX_NORMAL_BF16` | `__ushort_as_bfloat16((unsigned short)0x7F7FU)` | bfloat16 最大可表示值。 |
| `HGGCRT_MIN_DENORM_BF16` | `__ushort_as_bfloat16((unsigned short)0x0001U)` | bfloat16 最小可表示（非归一化）值。 |
| `HGGCRT_NAN_BF16` | `__ushort_as_bfloat16((unsigned short)0x7FFFU)` | bfloat16 典型 NaN。 |
| `HGGCRT_NEG_ZERO_BF16` | `__ushort_as_bfloat16((unsigned short)0x8000U)` | bfloat16 负零。 |
| `HGGCRT_ONE_BF16` | `__ushort_as_bfloat16((unsigned short)0x3F80U)` | bfloat16 1.0。 |
| `HGGCRT_ZERO_BF16` | `__ushort_as_bfloat16((unsigned short)0x0000U)` | bfloat16 正零。 |

### 4.2. Bfloat16 算术函数

与 Half 算术函数（3.2 节）语义一致，参数/返回类型为 `__ppu_bfloat16`：

| 函数 | 签名 | 说明 |
|---|---|---|
| `__habs` | `__ppu_bfloat16 __habs(const __ppu_bfloat16 a)` | 绝对值。`±0→+0`，`±∞→+∞`，NaN→NaN。 |
| `__hadd` / `__hadd_rn` / `__hadd_sat` | `(const __ppu_bfloat16 a, const __ppu_bfloat16 b)` | 加法；`_rn` 防止 mul+add 收缩为 fma；`_sat` 饱和到 [0.0,1.0]，NaN 刷新为 +0.0。 |
| `__hdiv` | 同上参数 | 除法 a/b（rn）。 |
| `__hfma` / `__hfma_relu` / `__hfma_sat` | `(a, b, c)`（`__device__`） | 融合乘加（rn，结果舍入一次）；`_relu` 负结果钳 0、NaN 转规范 NaN；`_sat` 饱和 [0.0,1.0]、NaN 刷新 +0.0。 |
| `__hmul` / `__hmul_rn` / `__hmul_sat` | `(a, b)` | 乘法；`_rn` 防止收缩为 fma；`_sat` 饱和 [0.0,1.0]。 |
| `__hneg` | `(a)` | 取负。 |
| `__hsub` / `__hsub_rn` / `__hsub_sat` | `(a, b)` | 减法；`_rn` 防止 mul+sub 收缩；`_sat` 饱和 [0.0,1.0]。 |
| `atomicAdd` | `__device__ __ppu_bfloat16 atomicAdd(__ppu_bfloat16 *const address, const __ppu_bfloat16 val)` | 原子加，返回旧值；address 必须在全局或共享内存。详见 HGGC C++ 编程指南原子函数部分。 |

运算符重载与 Half 相同集合（`operator*`、`*=`、`+`（一元/二元）、`++`（前/后缀）、`+=`、`-`（一元/二元）、`--`（前/后缀）、`-=`、`/`、`/=`），类型为 `__ppu_bfloat16`，均 `__host__ __device__`。

### 4.3. Bfloat16 比较函数

与 Half 比较函数（3.3 节）语义一致：

- bool 返回：`__heq`（NaN→false）、`__hequ`（NaN→true）、`__hge`/`__hgeu`、`__hgt`/`__hgtu`、`__hle`/`__hleu`、`__hlt`/`__hltu`、`__hne`/`__hneu`（无序版 NaN→true，有序版 NaN→false）。
- `int __hisinf(const __ppu_bfloat16 a)`：-∞→-1，+∞→1，否则 0。
- `bool __hisnan(const __ppu_bfloat16 a)`：是否 NaN。
- `__ppu_bfloat16 __hmax/__hmin(a,b)`：(a>b)?a:b / (a<b)?a:b；任一输入 NaN 返回另一个，都 NaN 返回规范 NaN；两输入均 0.0 时 +0.0 > -0.0。
- `__hmax_nan/__hmin_nan`：NaN 传递（任一 NaN 返回规范 NaN）。
- 运算符：`operator!=`（无序不等，见 `__hneu`）、`operator<`（有序，见 `__hlt`）、`operator<=`（见 `__hle`）、`operator==`（见 `__heq`）、`operator>`（见 `__hgt`）、`operator>=`（见 `__hge`），均 `__host__ __device__ bool`，参数 `(const __ppu_bfloat16 &lh, const __ppu_bfloat16 &rh)`。

### 4.4. Bfloat16 数学函数

均 `__device__`，单参数 `__ppu_bfloat16`，以向最近偶数舍入模式计算，函数集与 Half 数学函数（3.4 节）相同：`hceil`、`hcos`、`hexp`、`hexp10`、`hexp2`、`hfloor`、`hlog`、`hlog10`、`hlog2`、`hrcp`、`hrint`（中间情况舍入到偶整数）、`hrsqrt`、`hsin`、`hsqrt`、`htrunc`。

注意：`hcos` 的实现调用 `cosf(float)`，`hsin` 的实现调用 `sinf(float)`，受编译器优化影响——`--use_fast_math` 标志会将其替换为准确性较低的内在函数 `__cosf(float)` / `__sinf(float)`。

### 4.5. Bfloat16 转换函数

#### 4.5.1. float/double ↔ bfloat16

| 函数 | 签名 | 说明 |
|---|---|---|
| `__bfloat1622float2` | `float2 __bfloat1622float2(const __ppu_bfloat162 a)` | bfloat162 两半部→float2。 |
| `__bfloat162bfloat162` | `__ppu_bfloat162 __bfloat162bfloat162(const __ppu_bfloat16 a)` | 返回两个半部都等于 a 的 bfloat162。 |
| `__bfloat162float` | `float __bfloat162float(const __ppu_bfloat16 a)` | bfloat16→float。`±0→±0`，`±∞→±∞`，NaN→NaN。 |
| `__double2bfloat16` | `__ppu_bfloat16 __double2bfloat16(const double a)` | double→bfloat16（rn）。`±0→±0`，`±∞→±∞`，NaN→NaN。 |
| `__float22bfloat162_rn` | `__ppu_bfloat162 __float22bfloat162_rn(const float2 a)` | float2 两分量→bfloat162（rn）。低 16 位对应 a.x，高 16 位对应 a.y。 |
| `__float2bfloat16` | `__ppu_bfloat16 __float2bfloat16(const float a)` | float→bfloat16（rn）。 |
| `__float2bfloat162_rn` | `__ppu_bfloat162 __float2bfloat162_rn(const float a)` | float→bfloat16 并填充两半部（rn）。 |
| `__float2bfloat16_rd` / `__float2bfloat16_rn` / `__float2bfloat16_ru` / `__float2bfloat16_rz` | `__ppu_bfloat16 __float2bfloat16_XX(const float a)` | 分别向下/最近偶数/向上/向零舍入。`±0→±0`，`±∞→±∞`，NaN→NaN。 |
| `__floats2bfloat162_rn` | `__ppu_bfloat162 __floats2bfloat162_rn(const float a, const float b)` | 两个 float→bfloat162（rn）。低 16 位对应 a，高 16 位对应 b。 |

#### 4.5.2. bfloat16 ↔ 整数

bfloat16→整数时 NaN 输入转换为 0（ll/ull 系列 NaN 返回 0x8000000000000000）。

| 函数 | 返回类型 | 舍入 | 饱和行为 |
|---|---|---|---|
| `__bfloat162char_rz` | signed char | rz | ±0→0；x>127→SCHAR_MAX=0x7F；x<−128→SCHAR_MIN=0x80；NaN→0 |
| `__bfloat162int_rd` / `__bfloat162int_rn` / `__bfloat162int_ru` / `__bfloat162int_rz` | int | rd/rn/ru/rz | ±0→0；x>INT_MAX→0x7FFFFFFF；x<INT_MIN→0x80000000；NaN→0 |
| `__bfloat162ll_rd` / `__bfloat162ll_rn` / `__bfloat162ll_ru` / `__bfloat162ll_rz` | long long int | rd/rn/ru/rz | NaN→0x8000000000000000 |
| `__bfloat162short_rd` / `__bfloat162short_rn` / `__bfloat162short_ru` / `__bfloat162short_rz` | short int | rd/rn/ru/rz | ±0→0；x>32767→SHRT_MAX=0x7FFF；x<−32768→SHRT_MIN=0x8000；NaN→0 |
| `__bfloat162uchar_rz` | unsigned char | rz | ±0→0；x>255→UCHAR_MAX=0xFF；x<0→0；NaN→0 |
| `__bfloat162uint_rd` / `__bfloat162uint_rn` / `__bfloat162uint_ru` / `__bfloat162uint_rz` | unsigned int | rd/rn/ru/rz | NaN→0 |
| `__bfloat162ull_rd` / `__bfloat162ull_rn` / `__bfloat162ull_ru` / `__bfloat162ull_rz` | unsigned long long int | rd/rn/ru/rz | NaN→0x8000000000000000 |
| `__bfloat162ushort_rd` / `__bfloat162ushort_rn` / `__bfloat162ushort_ru` / `__bfloat162ushort_rz` | unsigned short int | rd/rn/ru/rz | NaN→0 |
| `__bfloat16_as_short` / `__bfloat16_as_ushort` | short / unsigned short | — | 位重新解释。 |

整数→bfloat16（参数为对应整型 `i`，返回 `__ppu_bfloat16`）：

| 函数 | 输入类型 | 舍入 |
|---|---|---|
| `__int2bfloat16_rd` / `__int2bfloat16_rn` / `__int2bfloat16_ru` / `__int2bfloat16_rz` | int | rd/rn/ru/rz |
| `__ll2bfloat16_rd` / `__ll2bfloat16_rn` / `__ll2bfloat16_ru` / `__ll2bfloat16_rz` | long long int | rd/rn/ru/rz |
| `__short2bfloat16_rd` / `__short2bfloat16_rn` / `__short2bfloat16_ru` / `__short2bfloat16_rz` | short int | rd/rn/ru/rz |
| `__short_as_bfloat16` | short int | 位重新解释 |
| `__uint2bfloat16_rd` / `__uint2bfloat16_rn` / `__uint2bfloat16_ru` / `__uint2bfloat16_rz` | unsigned int | rd/rn/ru/rz |
| `__ull2bfloat16_rd` / `__ull2bfloat16_rn` / `__ull2bfloat16_ru` / `__ull2bfloat16_rz` | unsigned long long int | rd/rn/ru/rz |
| `__ushort2bfloat16_rd` / `__ushort2bfloat16_rn` / `__ushort2bfloat16_ru` / `__ushort2bfloat16_rz` | unsigned short int | rd/rn/ru/rz |
| `__ushort_as_bfloat16` | unsigned short int | 位重新解释 |

其中 `_rn` 与位重解释函数为 `__host__ __device__`，`_rd/_ru/_rz` 多数为 `__device__`。

#### 4.5.3. bfloat162 打包/拆包

| 函数 | 签名 | 说明 |
|---|---|---|
| `__halves2bfloat162` | `__ppu_bfloat162 __halves2bfloat162(const __ppu_bfloat16 a, const __ppu_bfloat16 b)` | 组合两个 bfloat16；a 存低 16 位，b 存高 16 位。 |
| `__high2bfloat16` | `__ppu_bfloat16 __high2bfloat16(const __ppu_bfloat162 a)` | 返回高 16 位。 |
| `__high2bfloat162` | `__ppu_bfloat162 __high2bfloat162(const __ppu_bfloat162 a)` | 提取高 16 位并复制到两半部。 |
| `__high2float` | `float __high2float(const __ppu_bfloat162 a)` | 高 16 位→float。 |
| `__highs2bfloat162` | `__ppu_bfloat162 __highs2bfloat162(const __ppu_bfloat162 a, const __ppu_bfloat162 b)` | 各取高 16 位组合（a 高位→结果低 16 位，b 高位→结果高 16 位）。 |
| `__low2bfloat16` | `__ppu_bfloat16 __low2bfloat16(const __ppu_bfloat162 a)` | 返回低 16 位。 |
| `__low2bfloat162` | `__ppu_bfloat162 __low2bfloat162(const __ppu_bfloat162 a)` | 提取低 16 位并复制到两半部。 |
| `__low2float` | `float __low2float(const __ppu_bfloat162 a)` | 低 16 位→float。 |
| `__lowhigh2highlow` | `__ppu_bfloat162 __lowhigh2highlow(const __ppu_bfloat162 a)` | 交换两个半部。 |
| `__lows2bfloat162` | `__ppu_bfloat162 __lows2bfloat162(const __ppu_bfloat162 a, const __ppu_bfloat162 b)` | 各取低 16 位组合。 |
| `make_bfloat162` | `__ppu_bfloat162 make_bfloat162(const __ppu_bfloat16 x, const __ppu_bfloat16 y)` | 组合为 bfloat162；x 存低 16 位，y 存高 16 位。 |

#### 4.5.4. 缓存修饰加载/存储

与 Half 相同（3.5.4 节），`__half`/`__half2` 换为 `__ppu_bfloat16`/`__ppu_bfloat162`：`__ldca`（ld.global.ca）、`__ldcg`（ld.global.cg）、`__ldcs`（ld.global.cs）、`__ldcv`（ld.global.cv）、`__ldg`（ld.global.nc）、`__ldlu`（ld.global.lu）、`__stcg`（st.global.cg）、`__stcs`（st.global.cs）、`__stwb`（st.global.wb）、`__stwt`（st.global.wt），各有标量与 2 元向量两个重载，均 `__device__`。

#### 4.5.5. Warp Shuffle（bfloat16/bfloat162）

与 Half 相同（3.5.5 节）的四个函数 `__shfl_down_sync`、`__shfl_sync`、`__shfl_up_sync`、`__shfl_xor_sync`，各有 `__ppu_bfloat16`（2 字节）与 `__ppu_bfloat162`（4 字节）重载，参数与 width/mask 语义相同。详见 HGGC C++ 编程指南 Warp Shuffle 函数部分。

#### 4.5.6. `__ppu_bfloat16` / `__ppu_bfloat162` 类构造与赋值

`__ppu_bfloat16`：

- 构造函数（均 `__host__ __device__`，数值输入使用默认最近偶数舍入）：
  - `constexpr __ppu_bfloat16(const __ppu_bfloat16_raw &hr)`；
  - 从 `float`、`double`、`int`、`unsigned int`、`short`、`unsigned short`、`long`、`unsigned long`、`long long`、`unsigned long long`、`__half` 构造；
  - `__ppu_bfloat16() = default`。
- 转换运算符：`operator __ppu_bfloat16_raw() const`、`operator __ppu_bfloat16_raw() const volatile`；以及 `operator bool()`（constexpr）、`char`、`float`、`int`、`long`、`long long`、`short`、`signed char`、`unsigned char`、`unsigned int`、`unsigned long`、`unsigned long long`、`unsigned short`。
- 赋值运算符 `operator=`：从 `float`、`double`、`int`、`unsigned int`、`short`、`unsigned short`、`long long`、`unsigned long long`、`__ppu_bfloat16_raw` 赋值；volatile 变体：`volatile __ppu_bfloat16 & operator=(const __ppu_bfloat16_raw &hr) volatile`、`volatile __ppu_bfloat16 & operator=(const volatile __ppu_bfloat16_raw &hr) volatile`。

`__ppu_bfloat162`：

- 构造函数：`__ppu_bfloat162(const __ppu_bfloat162_raw &h2r)`；`constexpr __ppu_bfloat162(const __ppu_bfloat16 &a, const __ppu_bfloat16 &b)`；移动构造（C++11+）；拷贝构造；`__ppu_bfloat162() = default`。
- 转换运算符：`operator __ppu_bfloat162_raw() const`。
- 赋值运算符：`operator=(const __ppu_bfloat162 &src)`、`operator=(const __ppu_bfloat162_raw &h2r)`、移动赋值 `operator=(__ppu_bfloat162 &&src)`（C++11+）。

### 4.6. Bfloat162 算术函数

与 Half2 算术函数（3.6 节）语义一致，类型为 `__ppu_bfloat162`：`__h2div`、`__habs2`、`__hadd2`、`__hadd2_rn`（防 fma 收缩）、`__hadd2_sat`、`__hcmadd`（复数乘加 a*b+c）、`__hfma2`、`__hfma2_relu`、`__hfma2_sat`、`__hmul2`、`__hmul2_rn`、`__hmul2_sat`、`__hneg2`、`__hsub2`、`__hsub2_rn`、`__hsub2_sat`、`atomicAdd`（`__device__`，原子性仅对两个元素分别保证，不保证整个 32 位访问原子性）。运算符重载与 Half2 相同集合（`*`、`*=`、`+`、`++`、`+=`、`-`、`--`、` -=`、`/`、`/=`）。

### 4.7. Bfloat162 比较函数

与 Half2 比较函数（3.7 节）语义一致：

- bool 返回：`__hbeq2`/`__hbequ2`、`__hbge2`/`__hbgeu2`、`__hbgt2`/`__hbgtu2`、`__hble2`/`__hbleu2`、`__hblt2`/`__hbltu2`、`__hbne2`/`__hbneu2`（两个元素比较都为 true 才返回 true；无序版 NaN→true，有序版 NaN→false）。
- 向量返回（对应元素置 1.0/0.0）：`__heq2`/`__hequ2`、`__hge2`/`__hgeu2`、`__hgt2`/`__hgtu2`、`__hle2`/`__hleu2`、`__hlt2`/`__hltu2`、`__hne2`/`__hneu2`、`__hisnan2`。
- 最值：`__hmax2`/`__hmax2_nan`、`__hmin2`/`__hmin2_nan`（NaN 行为同 Half2 对应函数）。
- 运算符重载：`operator!=`（见 `__hbneu2`）、`operator<`（见 `__hblt2`）、`operator<=`（见 `__hble2`）、`operator==`（见 `__hbeq2`）、`operator>`（见 `__hbgt2`）、`operator>=`（见 `__hbge2`）。

### 4.8. Bfloat162 数学函数

均 `__device__`，参数 `const __ppu_bfloat162`，返回 `__ppu_bfloat162`，逐元素 rn 计算，函数集与 Half2 数学函数（3.8 节）相同：`h2ceil`、`h2cos`、`h2exp`、`h2exp10`、`h2exp2`、`h2floor`、`h2log`、`h2log10`、`h2log2`、`h2rcp`、`h2rint`、`h2rsqrt`、`h2sin`、`h2sqrt`、`h2trunc`。同样注意 `h2cos`/`h2sin` 经 `cosf`/`sinf` 实现，受 `--use_fast_math` 影响。

## 5. 单精度函数

### 5.1. 单精度数学函数

均 `__device__ float`（除特别注明）。标注 [fast-math] 的函数受 `--use_fast_math` 编译器标志影响（受影响函数完整列表见 HGGC C++ 编程指南数学函数附录内在函数部分）。

| 函数 | 说明 / 特殊值 |
|---|---|
| `acosf(x)` | 反余弦，区间 [0,π]，x∈[-1,+1]。acosf(1)=+0；x 超界→NaN；NaN→NaN。 |
| `acoshf(x)` | 非负反双曲余弦，区间 [0,+∞]。acoshf(1)=0；x∈[−∞,1)→NaN；+∞→+∞；NaN→NaN。 |
| `asinf(x)` | 反正弦，区间 [-π/2,+π/2]。asinf(±0)=±0；x 超界→NaN；NaN→NaN。 |
| `asinhf(x)` | 反双曲正弦。±0→±0；±∞→±∞；NaN→NaN。 |
| `atan2f(y, x)` | y/x 的反正切主值，区间 [-π,+π]，象限由符号确定。atan2f(±0,-0)=±π；(±0,+0)=±0；(±0,x<0)=±π；(±0,x>0)=±0；(y<0,±0)=-π/2；(y>0,±0)=π/2；(±y,-∞)=±π；(±y,+∞)=±0（有限 y>0）；(±∞, 有限 x)=±π/2；(±∞,-∞)=±3π/4；(±∞,+∞)=±π/4；任一 NaN→NaN。 |
| `atanf(x)` | 反正切，区间 [-π/2,+π/2]。±0→±0；±∞→±π/2；NaN→NaN。 |
| `atanhf(x)` | 反双曲正切。±0→±0；±1→±∞；x 超出 [-1,1]→NaN；NaN→NaN。 |
| `cbrtf(x)` | 立方根 x^(1/3)。±0→±0；±∞→±∞；NaN→NaN。 |
| `ceilf(x)` | 上取整 ⌈x⌉。±0→±0；±∞→±∞；NaN→NaN。 |
| `copysignf(x, y)` | 幅值取 x、符号取 y。copysignf(NaN, y) 返回带 y 符号的 NaN。 |
| `cosf(x)` [fast-math] | 余弦（弧度）。cosf(±0)=1；±∞→NaN；NaN→NaN。 |
| `coshf(x)` | 双曲余弦。coshf(±0)=1；±∞→+∞；NaN→NaN。 |
| `cospif(x)` | cos(x·π)。cospif(±0)=1；±∞→NaN；NaN→NaN。 |
| `cyl_bessel_i0f(x)` | 0 阶正则修正柱贝塞尔函数 I0(x)。±0→+1；±∞→+∞；NaN→NaN。 |
| `cyl_bessel_i1f(x)` | 1 阶正则修正柱贝塞尔函数 I1(x)。±0→±0；±∞→±∞；NaN→NaN。 |
| `erfcf(x)` | 互补误差函数 1-erf(x)。erfcf(−∞)=2；+∞→+0；NaN→NaN。 |
| `erfcinvf(x)` | 反互补误差函数 erfc⁻¹(x)，x∈[0,2]。±0→+∞；2→−∞；超界→NaN；NaN→NaN。 |
| `erfcxf(x)` | 缩放互补误差函数 e^(x²)·erfc(x)。−∞→+∞；+∞→+0；NaN→NaN。 |
| `erff(x)` | 误差函数。erff(±0)=±0；±∞→±1；NaN→NaN。 |
| `erfinvf(x)` | 反误差函数 erf⁻¹(x)，x∈[-1,1]。±0→±0；1→+∞；-1→−∞；超界→NaN；NaN→NaN。 |
| `exp10f(x)` [fast-math] | 10^x。±0→1；−∞→+0；+∞→+∞；NaN→NaN。 |
| `exp2f(x)` | 2^x。特殊值同 exp10f。 |
| `expf(x)` [fast-math] | e^x。特殊值同 exp10f。 |
| `expm1f(x)` | e^x - 1。±0→±0；−∞→-1；+∞→+∞；NaN→NaN。 |
| `fabsf(x)` | 绝对值。±∞→+∞；±0→+0；NaN→未指定 NaN。 |
| `fdimf(x, y)` | 正差值：x>y 时 x-y，否则 +0；任一 NaN→NaN。 |
| `fdividef(x, y)` [fast-math] | x/y。指定 -use_fast_math 且未显式 -prec_div=true 时使用 `__fdividef()` 以获得更高性能。 |
| `floorf(x)` | 下取整 ⌊x⌋。±∞→±∞；±0→±0；NaN→NaN。 |
| `fmaf(x, y, z)` | x·y+z 作为单个运算，无限精度后按 ties-to-even 舍入一次。fmaf(±∞,±0,z)=NaN；(±0,±∞,z)=NaN；(x,y,−∞) 当 x·y 恰为 +∞ 时 NaN；(x,y,+∞) 当 x·y 恰为 −∞ 时 NaN；(x,y,±0) 当 x·y 恰为 ±0 时 ±0；(x,y,∓0) 当 x·y 恰为 ±0 时 +0；x·y+z 恰为零且 z≠0 时 +0；任一 NaN→NaN。 |
| `fmaxf(x, y)` / `fminf(x, y)` | 最大/最小值；NaN 视为缺失数据，一个参数 NaN 时取数值参数，都 NaN 时返回 NaN。 |
| `fmodf(x, y)` | x/y 的浮点余数 x-n·y（n 为 x/y 截断），与 x 同号、幅值小于 y。fmodf(±0,y≠0)=±0；(有限 x,±∞)=x；x=±∞ 或 y=0 →NaN；任一 NaN→NaN。 |
| `frexpf(x, int *nptr)` | 分解为 m·2^n，|m|∈[0.5,1) 或 0，n 存入 nptr。±0→±0 且存 0；±∞→±∞ 且存未指定值；NaN→NaN 且存未指定值。 |
| `hypotf(x, y)` | √(x²+y²)，不会过度溢出/下溢。hypotf(x,y)=hypotf(y,x)=hypotf(x,-y)；(x,±0)=fabsf(x)；(±∞,y)=+∞ 即使 y 为 NaN；(NaN,y≠±∞)→NaN。 |
| `ilogbf(x)` | 无偏整数指数（不考虑 FP_ILOGB0/FP_ILOGBNAN）。±0→INT_MIN；NaN→INT_MIN；±∞→INT_MAX。 |
| `isfinite(a)` → bool | 是否为有限值（零、次正规、或正规且非无穷/NaN）。 |
| `isinf(a)` → bool | 是否为无穷大。 |
| `isnan(a)` → bool | 是否为 NaN。 |
| `j0f(x)` | 0 阶第一类贝塞尔函数 J0(x)。±∞→+0；NaN→NaN。 |
| `j1f(x)` | 1 阶第一类贝塞尔函数 J1(x)。±0→±0；±∞→±0；NaN→NaN。 |
| `jnf(n, x)` | n 阶第一类贝塞尔函数 Jn(x)。n<0→NaN；+∞→+0；NaN→NaN。 |
| `ldexpf(x, exp)` | x·2^exp；等价于 scalbnf(x, exp)。 |
| `lgammaf(x)` | ln\|Γ(x)\|。lgammaf(1)=lgammaf(2)=+0；x≤0 且为整数→+∞；±∞→+∞；NaN→NaN。 |
| `llrintf(x)` → long long | 舍入到最近整数（中间情况向偶）；超范围行为未定义。 |
| `llroundf(x)` → long long | 舍入到最近整数（中间情况远离零）；超范围未定义。可能比 llrintf 慢。 |
| `log10f(x)` [fast-math] | log10(x)。±0→−∞；1→+0；x<0→NaN；+∞→+∞；NaN→NaN。 |
| `log1pf(x)` | log_e(1+x)。±0→±0；-1→−∞；x<-1→NaN；+∞→+∞；NaN→NaN。 |
| `log2f(x)` [fast-math] | log2(x)。特殊值同 log10f。 |
| `logbf(x)` | 指数的浮点表示。±0→−∞；±∞→+∞；NaN→NaN。 |
| `logf(x)` [fast-math] | ln(x)。特殊值同 log10f。 |
| `lrintf(x)` → long | 舍入到最近整数（中间情况向偶）；超范围未定义。 |
| `lroundf(x)` → long | 舍入到最近整数（中间情况远离零）；超范围未定义。可能比 lrintf 慢。 |
| `max(a, b)` | 两个 float 的最大值。 |
| `min(a, b)` | 两个 float 的最小值。 |
| `modff(x, float *iptr)` | 分解为小数与整数部分，整数部分存 iptr，两部分与 x 同号。±∞→返回 ±0 并存 ±∞；NaN→存 NaN 并返回 NaN。 |
| `nanf(tagp)` | 返回 quiet NaN，tagp 选择表示之一。 |
| `nearbyintf(x)` | 舍入到最近整数（中间情况向偶）。±0→±0；±∞→±∞；NaN→NaN。 |
| `nextafterf(x, y)` | y 方向上紧随 x 的下一个可表示值。x==y 时返回 y；任一 NaN→NaN。 |
| `norm3df(a, b, c)` | √(a²+b²+c²)，不会过度溢出/下溢。存在精确无穷大坐标→+∞（即使有 NaN）；全 ±0→+0；有 NaN 且无穷大→NaN。 |
| `norm4df(a, b, c, d)` | 4D 版本，同上。 |
| `normcdff(x)` | 标准正态累积分布 Φ(x)。+∞→1；−∞→+0；NaN→NaN。 |
| `normcdfinvf(x)` | Φ⁻¹(x)，定义域 (0,1)。±0→−∞；1→+∞；不在 [0,1]→NaN；NaN→NaN。 |
| `normf(dim, p)` | 任意维 √(∑pᵢ²)，不会过度溢出/下溢；特殊值同 norm3df。 |
| `powf(x, y)` [fast-math] | x^y。powf(±0, y)：y 为小于 0 的奇整数→±∞；y<0 非奇整数→+∞；y 为大于 0 的奇整数→±0；y>0 非奇整数→+0。powf(-1,±∞)=1；powf(+1, 任何 y)=1（即使 NaN）；powf(x,±0)=1（即使 NaN）；x 有限负且 y 有限非整数→NaN；powf(x,−∞)：\|x\|<1→+∞，\|x\|>1→+0；powf(x,+∞)：\|x\|<1→+0，\|x\|>1→+∞；powf(−∞,y)：y 为小于 0 的奇整数→-0；y<0 非奇整数→+0；y 为大于 0 的奇整数→−∞；y>0 非奇整数→+∞；powf(+∞,y<0)=+0；(+∞,y>0)=+∞；NaN 情形（x≠+1 且 y≠±0）→NaN。 |
| `rcbrtf(x)` | 反立方根 1/x^(1/3)。±0→±∞；±∞→±0；NaN→NaN。 |
| `remainderf(x, y)` | 余数 r=x−ny，n 取最接近 x/y 的整数（|n−x/y|=1/2 时取偶数）。y=±0→NaN；x=±∞→NaN；(有限 x,±∞)=x；任一 NaN→NaN。 |
| `remquof(x, y, int *quo)` | 同 remainderf，并返回部分商 quo（与 x·y 同号，低 3 位与精确商一致）。异常时返回 NaN 且 quo 存未指定值；(有限 x,±∞) 返回 x 且 quo 存 0。 |
| `rhypotf(x, y)` | 1/√(x²+y²)。对称性同 hypotf。(±∞,y)=+0 即使 y 为 NaN；(±0,±0)=+∞；(NaN,y≠±∞)→NaN。 |
| `rintf(x)` | 舍入到最近整数（中间情况向偶）。±0→±0；±∞→±∞；NaN→NaN。 |
| `rnorm3df(a, b, c)` | 1/√(a²+b²+c²)。存在精确无穷大坐标→+0（即使有 NaN）；全 ±0→+∞；有 NaN 且无穷大→NaN。 |
| `rnorm4df(a, b, c, d)` | 4D 版本，同上。 |
| `rnormf(dim, p)` | 任意维倒数长度，同上。 |
| `roundf(x)` | 舍入到最近整数（中间情况远离零）。±0→±0；±∞→±∞；NaN→NaN。可能比 rintf 慢。 |
| `rsqrtf(x)` | 1/√x。+∞→+0；±0→±∞；x<0→NaN；NaN→NaN。 |
| `scalblnf(x, n)`（n 为 long） | x·2^n，高效操作指数。±0→±0；n=0→x；±∞→±∞；NaN→NaN。 |
| `scalbnf(x, n)`（n 为 int） | 同上。 |
| `signbit(a)` → bool | 符号位（包括无穷大、零、NaN）；a 为负时 true。 |
| `sincosf(x, sptr, cptr)` [fast-math] | 同时计算 sin 与 cos，分别写入 sptr/cptr。 |
| `sincospif(x, sptr, cptr)` | 同时计算 sin(x·π) 与 cos(x·π)。 |
| `sinf(x)` [fast-math] | 正弦（弧度）。±0→±0；±∞→NaN；NaN→NaN。 |
| `sinhf(x)` | 双曲正弦。±0→±0；±∞→±∞；NaN→NaN。 |
| `sinpif(x)` | sin(x·π)。±0→±0；±∞→NaN；NaN→NaN。 |
| `sqrtf(x)` | √x。±0→±0；+∞→+∞；x<0→NaN；NaN→NaN。 |
| `tanf(x)` [fast-math] | 正切（弧度）。±0→±0；±∞→NaN；NaN→NaN。 |
| `tanhf(x)` | 双曲正切。±0→±0；±∞→±1；NaN→NaN。 |
| `tgammaf(x)` | Γ(x)。±0→±∞；x<0 且为整数→NaN；−∞→NaN；+∞→+∞；NaN→NaN。 |
| `truncf(x)` | 截断为整数部分。±0→±0；±∞→±∞；NaN→NaN。 |
| `y0f(x)` | 0 阶第二类贝塞尔函数 Y0(x)。±0→−∞；x<0→NaN；+∞→+0；NaN→NaN。 |
| `y1f(x)` | 1 阶第二类贝塞尔函数 Y1(x)。特殊值同 y0f。 |
| `ynf(n, x)` | n 阶第二类贝塞尔函数 Yn(x)。n<0→NaN；其余同 y0f。 |

### 5.2. 单精度内建函数（快速/显式舍入版本）

均 `__device__`。这是与 5.1 节精确版本对应的快速近似或显式舍入版本，精度/速度取舍对照见本节末的比赛关联。

快速近似版本（精度低于对应精确版本）：

| 函数 | 对应精确版本 | 说明 |
|---|---|---|
| `__cosf(x)` | cosf | 快速近似余弦。 |
| `__exp10f(x)` | exp10f | 快速近似 10^x。 |
| `__expf(x)` | expf | 快速近似 e^x。 |
| `__fdividef(x, y)` | fdividef / `__fdiv_rn` | 快速近似除法 x/y。`__fdividef(∞, y)` 对 2^126<\|y\|<2^128 返回 NaN；`__fdividef(x, y)` 对 2^126<\|y\|<2^128 且有限 x 返回 0。 |
| `__log10f(x)` | log10f | 快速近似 log10。 |
| `__log2f(x)` | log2f | 快速近似 log2。 |
| `__logf(x)` | logf | 快速近似 ln。 |
| `__powf(x, y)` | powf | 快速近似 x^y。 |
| `__saturatef(x)` | — | 钳制到 [+0.0, 1.0]：x≤0→+0；x≥1→1；0<x<1→x；NaN→+0。 |
| `__sincosf(x, sptr, cptr)` | sincosf | 快速近似正弦+余弦；非规格化输入/输出刷新为保留符号的 0.0。 |
| `__sinf(x)` | sinf | 快速近似正弦；非规格化输出刷新为保留符号的 0.0。 |
| `__tanf(x)` | tanf | 快速近似正切；按 `__sinf/__cosf` 快速除法计算，非规格化输出刷新为保留符号的 0.0。 |

显式舍入算术（`__fadd_*`/`__fmul_*`/`__fsub_*` 永不合并为单个乘加指令）：

| 函数 | 说明 |
|---|---|
| `__fadd_rd` / `__fadd_rn` / `__fadd_ru` / `__fadd_rz` (x, y) | x+y。交换律成立；(x,±∞)→±∞（有限 x）；(±∞,±∞)→±∞；(±∞,∓∞)→NaN；(±0,±0)→±0；(x,-x)→+0（`_rd` 为 −0）；NaN→NaN。 |
| `__fdiv_rd` / `__fdiv_rn` / `__fdiv_ru` / `__fdiv_rz` (x, y) | x/y。商符号为 x、y 符号异或；(±0,±0)→NaN；(±∞,±∞)→NaN；(x,±∞)→适当符号 0；(±∞,y)→适当符号 ∞；(x≠0,±0)→适当符号 ∞；(±0,y≠0)→适当符号 0；NaN→NaN。 |
| `__fmul_rd` / `__fmul_rn` / `__fmul_ru` / `__fmul_rz` (x, y) | x·y。积符号为异或；交换律成立；(x≠0,±∞)→适当符号 ∞；(±0,±∞)→NaN；(±0, 有限 y)→适当符号 0；NaN→NaN。 |
| `__fsub_rd` / `__fsub_rn` / `__fsub_ru` / `__fsub_rz` (x, y) | x−y。(±∞, 有限 y)→±∞；(有限 x,±∞)→∓∞；(±∞,±∞)→NaN；(±∞,∓∞)→±∞；(±0,∓0)→±0；(x,x)→+0（`_rd` 为 −0）；NaN→NaN。 |
| `__frcp_rd` / `__frcp_rn` / `__frcp_ru` / `__frcp_rz` (x) | 1/x。±0→±∞；±∞→±0；NaN→NaN。 |
| `__frsqrt_rn(x)` | 1/√x（rn）。±0→±∞；+∞→+0；x<0→NaN；NaN→NaN。 |
| `__fsqrt_rd` / `__fsqrt_rn` / `__fsqrt_ru` / `__fsqrt_rz` (x) | √x。±0→±0；+∞→+∞；x<0→NaN；NaN→NaN。 |
| `__fmaf_rd` / `__fmaf_rn` / `__fmaf_ru` / `__fmaf_rz` (x, y, z) | x·y+z 单运算，按指定模式舍入一次。(±∞,±0,z)→NaN；(±0,±∞,z)→NaN；(x,y,−∞) 当 x·y 恰为 +∞ 时 NaN；(x,y,+∞) 当 x·y 恰为 −∞ 时 NaN；(x,y,±0) 当 x·y 恰为 ±0 时 ±0；(x,y,∓0) 当 x·y 恰为 ±0 时 +0（`_rd` 为 −0）；x·y+z 恰为零且 z≠0 时 +0（`_rd` 为 −0）；NaN→NaN。 |
| `__fmaf_ieee_rd` / `__fmaf_ieee_rn` / `__fmaf_ieee_ru` / `__fmaf_ieee_rz` (x, y, z) | 同对应 `__fmaf_*`，但处理非规格化输入/输出时忽略（使无效）`-ftz=true` 编译器标志。 |

比赛关联：这是“精度保持 vs 速度”的核心对照表。softmax（exp）、RMSNorm（rsqrt）、GELU/SiLU（tanh、除法）等逐元素算子换用 `__expf`/`__frsqrt_rn`/`__fdividef` 或打开 `--use_fast_math` 可明显提速，但快速版本精度下降且非规格化数被刷新为零，可能影响精度得分——建议逐算子替换并对照 benchmark 精度，而非全局开 fast-math。需要与参考实现逐位一致时用 `__fadd_rn`/`__fmul_rn` 阻止 fma 收缩。

## 6. 双精度函数

### 6.1. 双精度数学函数

均 `__device__ double`（除特别注明）。语义与对应单精度函数（5.1 节）一致，下表保留全部函数与特殊值：

| 函数 | 说明 / 特殊值 |
|---|---|
| `acos(x)` | 反余弦，[0,π]，x∈[-1,+1]。acos(1)=+0；超界→NaN；NaN→NaN。 |
| `acosh(x)` | 非负反双曲余弦，[0,+∞]。acosh(1)=0；x∈[−∞,1)→NaN；+∞→+∞；NaN→NaN。 |
| `asin(x)` | 反正弦，[-π/2,+π/2]。±0→±0；超界→NaN；NaN→NaN。 |
| `asinh(x)` | 反双曲正弦。±0→±0；±∞→±∞；NaN→NaN。 |
| `atan(x)` | 反正切，[-π/2,+π/2]。±0→±0；±∞→±π/2；NaN→NaN。 |
| `atan2(y, x)` | y/x 反正切主值，[-π,+π]。特殊值集合与 atan2f 相同。 |
| `atanh(x)` | 反双曲正切。±0→±0；±1→±∞；超出 [-1,1]→NaN；NaN→NaN。 |
| `cbrt(x)` | 立方根。±0→±0；±∞→±∞；NaN→NaN。 |
| `ceil(x)` | 上取整。±0→±0；±∞→±∞；NaN→NaN。 |
| `copysign(x, y)` | 幅值取 x、符号取 y；copysign(NaN, y) 返回带 y 符号的 NaN。 |
| `cos(x)` | 余弦。±0→1；±∞→NaN；NaN→NaN。 |
| `cosh(x)` | 双曲余弦。±0→1；±∞→+∞；NaN→NaN。 |
| `cospi(x)` | cos(x·π)。±0→1；±∞→NaN；NaN→NaN。 |
| `cyl_bessel_i0(x)` | I0(x)。±0→+1；±∞→+∞；NaN→NaN。 |
| `cyl_bessel_i1(x)` | I1(x)。±0→±0；±∞→±∞；NaN→NaN。 |
| `erf(x)` | 误差函数。±0→±0；±∞→±1；NaN→NaN。 |
| `erfc(x)` | 1-erf(x)。−∞→2；+∞→+0；NaN→NaN。 |
| `erfcinv(x)` | erfc⁻¹(x)，x∈[0,2]。±0→+∞；2→−∞；超界→NaN；NaN→NaN。 |
| `erfcx(x)` | e^(x²)·erfc(x)。−∞→+∞；+∞→+0；NaN→NaN。 |
| `erfinv(x)` | erf⁻¹(x)，x∈[-1,1]。±0→±0；1→+∞；-1→−∞；超界→NaN；NaN→NaN。 |
| `exp(x)` | e^x。±0→1；−∞→+0；+∞→+∞；NaN→NaN。 |
| `exp10(x)` | 10^x。特殊值同 exp。 |
| `exp2(x)` | 2^x。特殊值同 exp。 |
| `expm1(x)` | e^x-1。±0→±0；−∞→-1；+∞→+∞；NaN→NaN。 |
| `fabs(x)` | 绝对值。±∞→+∞；±0→+0；NaN→未指定 NaN。 |
| `fdim(x, y)` | 正差值：x>y 时 x-y，否则 +0；NaN→NaN。 |
| `floor(x)` | 下取整。±∞→±∞；±0→±0；NaN→NaN。 |
| `fma(x, y, z)` | x·y+z 单运算，无限精度后 ties-to-even 舍入一次。特殊值集合与 fmaf 相同。 |
| `fmax(x, y)` / `fmin(x, y)` | 最大/最小值；NaN 视为缺失数据。 |
| `fmod(x, y)` | x/y 余数，与 x 同号。±0,y≠0→±0；(有限 x,±∞)→x；x=±∞ 或 y=0→NaN；NaN→NaN。 |
| `frexp(x, int *nptr)` | 分解为 m·2^n。特殊值同 frexpf。 |
| `hypot(x, y)` | √(x²+y²)。特殊值同 hypotf。 |
| `ilogb(x)` → int | 无偏指数（不考虑 FP_ILOGB0/FP_ILOGBNAN）。±0→INT_MIN；NaN→INT_MIN；±∞→INT_MAX。 |
| `isfinite(a)` / `isinf(a)` / `isnan(a)` → bool | 有限/无穷/NaN 判定。 |
| `j0(x)` | J0(x)。±∞→+0；NaN→NaN。 |
| `j1(x)` | J1(x)。±0→±0；±∞→±0；NaN→NaN。 |
| `jn(n, x)` | Jn(x)。n<0→NaN；+∞→+0；NaN→NaN。 |
| `ldexp(x, exp)` | x·2^exp；等价 scalbn。 |
| `lgamma(x)` | ln\|Γ(x)\|。1、2→+0；x≤0 整数→+∞；±∞→+∞；NaN→NaN。 |
| `llrint(x)` → long long | 最近整数舍入（向偶）；超范围未定义。 |
| `llround(x)` → long long | 最近整数舍入（远离零）；超范围未定义；可能比 llrint 慢。 |
| `log(x)` | ln(x)。±0→−∞；1→+0；x<0→NaN；+∞→+∞；NaN→NaN。 |
| `log10(x)` | log10(x)。特殊值同 log。 |
| `log1p(x)` | ln(1+x)。±0→±0；-1→−∞；x<-1→NaN；+∞→+∞；NaN→NaN。 |
| `log2(x)` | log2(x)。特殊值同 log。 |
| `logb(x)` | 指数浮点表示。±0→−∞；±∞→+∞；NaN→NaN。 |
| `lrint(x)` → long | 最近整数舍入（向偶）；超范围未定义。 |
| `lround(x)` → long | 最近整数舍入（远离零）；超范围未定义；可能比 lrint 慢。 |
| `max` 重载 | `max(float, double)`、`max(double, float)`、`max(double, double)` → double。 |
| `min` 重载 | `min(float, double)`、`min(double, double)`、`min(double, float)` → double。 |
| `modf(x, double *iptr)` | 分解小数/整数部分；±∞→±0 且存 ±∞；NaN→存 NaN 返回 NaN。 |
| `nan(tagp)` | 返回 quiet NaN。 |
| `nearbyint(x)` | 最近整数舍入（向偶）。±0→±0；±∞→±∞；NaN→NaN。 |
| `nextafter(x, y)` | y 方向下一可表示值。x==y→y；NaN→NaN。 |
| `norm(dim, p)` | 任意维 √(∑pᵢ²)。特殊值同 normf。 |
| `norm3d(a, b, c)` | √(a²+b²+c²)。特殊值同 norm3df。 |
| `norm4d(a, b, c, d)` | 4D 版本。 |
| `normcdf(x)` | Φ(x)。+∞→1；−∞→+0；NaN→NaN。 |
| `normcdfinv(x)` | Φ⁻¹(x)，定义域 (0,1)。±0→−∞；1→+∞；不在 [0,1]→NaN；NaN→NaN。 |
| `pow(x, y)` | x^y。特殊值集合与 powf 相同。 |
| `rcbrt(x)` | 反立方根。±0→±∞；±∞→±0；NaN→NaN。 |
| `remainder(x, y)` | 余数 r=x−ny，n 最近 x/y（平局取偶）。y=±0→NaN；x=±∞→NaN；(有限 x,±∞)→x；NaN→NaN。 |
| `remquo(x, y, int *quo)` | 同 remainder，返回部分商 quo（低 3 位与精确商一致）。 |
| `rhypot(x, y)` | 1/√(x²+y²)。特殊值同 rhypotf。 |
| `rint(x)` | 最近整数舍入（向偶）。±0→±0；±∞→±∞；NaN→NaN。 |
| `rnorm(dim, p)` | 任意维倒数长度。特殊值同 rnormf。 |
| `rnorm3d(a, b, c)` | 1/√(a²+b²+c²)。 |
| `rnorm4d(a, b, c, d)` | 4D 版本。 |
| `round(x)` | 最近整数舍入（远离零）。±0→±0；±∞→±∞；NaN→NaN；可能比 rint 慢。 |
| `rsqrt(x)` | 1/√x。+∞→+0；±0→±∞；x<0→NaN；NaN→NaN。 |
| `scalbln(x, n)`（n 为 long） | x·2^n。±0→±0；n=0→x；±∞→±∞；NaN→NaN。 |
| `scalbn(x, n)`（n 为 int） | 同上。 |
| `signbit(a)` → bool | 符号位；a 为负时 true。 |
| `sin(x)` | 正弦。±0→±0；±∞→NaN；NaN→NaN。 |
| `sincos(x, sptr, cptr)` | 同时计算 sin/cos。 |
| `sincospi(x, sptr, cptr)` | 同时计算 sin(x·π)/cos(x·π)。 |
| `sinh(x)` | 双曲正弦。±0→±0；±∞→±∞；NaN→NaN。 |
| `sinpi(x)` | sin(x·π)。±0→±0；±∞→NaN；NaN→NaN。 |
| `sqrt(x)` | √x。±0→±0；+∞→+∞；x<0→NaN；NaN→NaN。 |
| `tan(x)` | 正切。±0→±0；±∞→NaN；NaN→NaN。 |
| `tanh(x)` | 双曲正切。±0→±0；±∞→±1；NaN→NaN。 |
| `tgamma(x)` | Γ(x)。±0→±∞；x<0 整数→NaN；−∞→NaN；+∞→+∞；NaN→NaN。 |
| `trunc(x)` | 截断为整数部分。±0→±0；±∞→±∞；NaN→NaN。 |
| `y0(x)` | Y0(x)。±0→−∞；x<0→NaN；+∞→+0；NaN→NaN。 |
| `y1(x)` | Y1(x)。特殊值同 y0。 |
| `yn(n, x)` | Yn(x)。n<0→NaN；其余同 y0。 |

### 6.2. 双精度内建函数（显式舍入版本）

均 `__device__ double`。`__dadd_*`/`__dsub_*` 永不合并为单个乘加指令。

| 函数 | 说明 |
|---|---|
| `__dadd_rd` / `__dadd_rn` / `__dadd_ru` / `__dadd_rz` (x, y) | x+y。特殊值同 `__fadd_*`（(x,-x)：`_rd`→−0，其余→+0）。 |
| `__ddiv_rd` / `__ddiv_rn` / `__ddiv_ru` / `__ddiv_rz` (x, y) | x/y。特殊值同 `__fdiv_*`。 |
| `__dmul_rd` / `__dmul_rn` / `__dmul_ru` / `__dmul_rz` (x, y) | x·y。特殊值同 `__fmul_*`。 |
| `__drcp_rd` / `__drcp_rn` / `__drcp_ru` / `__drcp_rz` (x) | 1/x。 |
| `__dsqrt_rd` / `__dsqrt_rn` / `__dsqrt_ru` / `__dsqrt_rz` (x) | √x。 |
| `__dsub_rd` / `__dsub_rn` / `__dsub_ru` / `__dsub_rz` (x, y) | x−y。特殊值同 `__fsub_*`（(x,x)：`_rd`→−0，其余→+0）。 |
| `__fma_rd` / `__fma_rn` / `__fma_ru` / `__fma_rz` (x, y, z) | x·y+z 单运算，按指定模式（向下/最近偶数/向上/向零）舍入一次。特殊值同 `__fmaf_*`（`_rd` 版本 (x,y,∓0) 与恰好为零时返回 −0，其余 +0）。 |

## 7. 类型转换函数

均 `__device__`。舍入模式缩写同前。

| 函数 | 签名 | 说明 |
|---|---|---|
| `__double2float_rd` / `__double2float_rn` / `__double2float_ru` / `__double2float_rz` | `float __double2float_XX(double x)` | double→float，按指定模式舍入。 |
| `__double2hiint` | `int __double2hiint(double x)` | double 高 32 位重新解释为 signed int。 |
| `__double2int_rd` / `__double2int_rn` / `__double2int_ru` / `__double2int_rz` | `int __double2int_XX(double x)` | double→signed int。 |
| `__double2ll_rd` / `__double2ll_rn` / `__double2ll_ru` / `__double2ll_rz` | `long long int __double2ll_XX(double x)` | double→signed 64-bit int。 |
| `__double2loint` | `int __double2loint(double x)` | double 低 32 位重新解释为 signed int。 |
| `__double2uint_rd` / `__double2uint_rn` / `__double2uint_ru` / `__double2uint_rz` | `unsigned int __double2uint_XX(double x)` | double→unsigned int。 |
| `__double2ull_rd` / `__double2ull_rn` / `__double2ull_ru` / `__double2ull_rz` | `unsigned long long int __double2ull_XX(double x)` | double→unsigned 64-bit int。 |
| `__double_as_longlong` | `long long int __double_as_longlong(double x)` | double 位重新解释为 64-bit signed int。 |
| `__float2int_rd` / `__float2int_rn` / `__float2int_ru` / `__float2int_rz` | `int __float2int_XX(float x)` | float→signed int。 |
| `__float2ll_rd` / `__float2ll_rn` / `__float2ll_ru` / `__float2ll_rz` | `long long int __float2ll_XX(float x)` | float→signed 64-bit int。 |
| `__float2uint_rd` / `__float2uint_rn` / `__float2uint_ru` / `__float2uint_rz` | `unsigned int __float2uint_XX(float x)` | float→unsigned int。 |
| `__float2ull_rd` / `__float2ull_rn` / `__float2ull_ru` / `__float2ull_rz` | `unsigned long long int __float2ull_XX(float x)` | float→unsigned 64-bit int。 |
| `__float_as_int` | `int __float_as_int(float x)` | float 位重新解释为 signed int。 |
| `__float_as_uint` | `unsigned int __float_as_uint(float x)` | float 位重新解释为 unsigned int。 |
| `__hiloint2double` | `double __hiloint2double(int hi, int lo)` | 高/低 32 位整数重新解释为 double。 |
| `__int2double_rn` | `double __int2double_rn(int x)` | signed int→double。 |
| `__int2float_rd` / `__int2float_rn` / `__int2float_ru` / `__int2float_rz` | `float __int2float_XX(int x)` | signed int→float。 |
| `__int_as_float` | `float __int_as_float(int x)` | int 位重新解释为 float。 |
| `__ll2double_rd` / `__ll2double_rn` / `__ll2double_ru` / `__ll2double_rz` | `double __ll2double_XX(long long int x)` | signed 64-bit int→double。 |
| `__ll2float_rd` / `__ll2float_rn` / `__ll2float_ru` / `__ll2float_rz` | `float __ll2float_XX(long long int x)` | signed 64-bit int→float。 |
| `__longlong_as_double` | `double __longlong_as_double(long long int x)` | 64-bit signed int 位重新解释为 double。 |
| `__uint2double_rn` | `double __uint2double_rn(unsigned int x)` | unsigned int→double。 |
| `__uint2float_rd` / `__uint2float_rn` / `__uint2float_ru` / `__uint2float_rz` | `float __uint2float_XX(unsigned int x)` | unsigned int→float。 |
| `__uint_as_float` | `float __uint_as_float(unsigned int x)` | unsigned int 位重新解释为 float。 |
| `__ull2double_rd` / `__ull2double_rn` / `__ull2double_ru` / `__ull2double_rz` | `double __ull2double_XX(unsigned long long int x)` | unsigned 64-bit int→double。 |
| `__ull2float_rd` / `__ull2float_rn` / `__ull2float_ru` / `__ull2float_rz` | `float __ull2float_XX(unsigned long long int x)` | unsigned 64-bit int→float。 |

## 8. 整数函数

### 8.1. 整数数学函数

均 `__device__`。

| 函数 | 签名 | 说明 |
|---|---|---|
| `abs` | `int abs(int a)` / `long int abs(long int a)` / `long long int abs(long long int a)` | 绝对值。abs(INT_MIN)/abs(LONG_MIN)/abs(LLONG_MIN) 未定义。 |
| `labs` | `long int labs(long int a)` | 绝对值；labs(LONG_MIN) 未定义。 |
| `llabs` | `long long int llabs(long long int a)` | 绝对值；llabs(LLONG_MIN) 未定义。 |
| `llmax` / `llmin` | `(const long long int a, const long long int b)` | long long 最大/最小值。 |
| `ullmax` / `ullmin` | `(const unsigned long long int a, const unsigned long long int b)` | unsigned long long 最大/最小值。 |
| `umax` / `umin` | `(const unsigned int a, const unsigned int b)` | unsigned int 最大/最小值。 |
| `max` 重载 | 12 个重载：`max(long, unsigned long)→unsigned long`、`max(ull, ull)→ull`、`max(uint, int)→uint`、`max(ll, ull)→ull`、`max(ulong, ulong)→ulong`、`max(ll, ll)→ll`、`max(ull, ll)→ull`、`max(ulong, long)→ulong`、`max(long, long)→long`、`max(int, int)→int`、`max(uint, uint)→uint`、`max(int, uint)→uint` | 对应类型最大值。 |
| `min` 重载 | 12 个重载：`min(long, ulong)→ulong`、`min(ull, ull)→ull`、`min(ull, ll)→ull`、`min(int, int)→int`、`min(uint, int)→uint`、`min(ll, ull)→ull`、`min(ll, ll)→ll`、`min(int, uint)→uint`、`min(long, long)→long`、`min(uint, uint)→uint`、`min(ulong, long)→ulong`、`min(ulong, ulong)→ulong` | 对应类型最小值。 |

### 8.2. 整数内建函数

均 `__device__`。

| 函数 | 签名 | 说明 |
|---|---|---|
| `__brev` | `unsigned int __brev(unsigned int x)` | 32 位位反转：返回值第 N 位 = x 第 31-N 位。 |
| `__brevll` | `unsigned long long int __brevll(unsigned long long int x)` | 64 位位反转。 |
| `__byte_perm` | `unsigned int __byte_perm(unsigned int x, unsigned int y, unsigned int s)` | 从 {x,y} 组成的 8 字节源中选 4 字节：tmp64=(y<<32)\|x；selectorK=(s>>4K)&0x7；res[8K+7:8K]=tmp64[selectorK]，K=0..3。 |
| `__clz` | `int __clz(int x)` | 32 位连续高位零位数，0~32。 |
| `__clzll` | `int __clzll(long long int x)` | 64 位连续高位零位数，0~64。 |
| `__dp2a_hi` | 4 个重载：`int(int srcA, int srcB, int c)`、`unsigned(uint,uint,uint)`、`unsigned(ushort2, uchar4, uint)`、`int(short2, char4, int)` | 双向 int16×int8 点积 + 32 位累加，取 srcB 高半 16 位：两个成对 8×16 乘积加到 c。 |
| `__dp2a_lo` | 同上 4 个重载 | 同上，取 srcB 低半 16 位。 |
| `__dp4a` | 4 个重载：`unsigned(uchar4, uchar4, uint)`、`unsigned(uint, uint, uint)`、`int(int, int, int)`、`int(char4, char4, int)` | 四向 int8 点积 + 32 位累加：四对字节乘积加到 c。 |
| `__ffs` | `int __ffs(int x)` | 最低有效 1 位位置（最低位为 1），0~32；`__ffs(0)=0`。 |
| `__ffsll` | `int __ffsll(long long int x)` | 64 位版本，0~64；`__ffsll(0)=0`。 |
| `__fns` | `unsigned __fns(unsigned mask, unsigned base, int offset)` | 从 base 位起查找 mask 中第 n（offset）个 1 位位置；base 必须 ≤31 否则未定义；未找到返回 0xFFFFFFFF。 |
| `__funnelshift_l` | `unsigned __funnelshift_l(unsigned lo, unsigned hi, unsigned shift)` | 拼接 hi:lo 左移 (shift & 31) 位，返回最高 32 位。 |
| `__funnelshift_lc` | 同上 | 左移 min(shift, 32) 位（钳制），返回最高 32 位。 |
| `__funnelshift_r` | 同上 | 右移 (shift & 31) 位，返回最低 32 位。 |
| `__funnelshift_rc` | 同上 | 右移 min(shift, 32) 位（钳制），返回最低 32 位。 |
| `__hadd` | `int __hadd(int x, int y)` | 有符号平均 (x+y)>>1，避免中间和溢出。 |
| `__mul24` | `int __mul24(int x, int y)` | 低 24 位乘积的低 32 位；高 8 位忽略。 |
| `__mul64hi` | `long long int __mul64hi(long long int x, long long int y)` | 128 位乘积的高 64 位。 |
| `__mulhi` | `int __mulhi(int x, int y)` | 64 位乘积的高 32 位。 |
| `__popc` | `int __popc(unsigned int x)` | 32 位中 1 的个数，0~32。 |
| `__popcll` | `int __popcll(unsigned long long int x)` | 64 位中 1 的个数，0~64。 |
| `__rhadd` | `int __rhadd(int x, int y)` | 有符号舍入平均 (x+y+1)>>1，避免溢出。 |
| `__sad` | `unsigned int __sad(int x, int y, unsigned int z)` | \|x−y\|+z。 |
| `__uhadd` | `unsigned int __uhadd(unsigned int x, unsigned int y)` | 无符号平均 (x+y)>>1，避免溢出。 |
| `__umul24` | `unsigned int __umul24(unsigned int x, unsigned int y)` | 无符号低 24 位乘积的低 32 位。 |
| `__umul64hi` | `unsigned long long int __umul64hi(unsigned long long int x, unsigned long long int y)` | 无符号 128 位乘积的高 64 位。 |
| `__umulhi` | `unsigned int __umulhi(unsigned int x, unsigned int y)` | 无符号 64 位乘积的高 32 位。 |
| `__urhadd` | `unsigned int __urhadd(unsigned int x, unsigned int y)` | 无符号舍入平均 (x+y+1)>>1。 |
| `__usad` | `unsigned int __usad(unsigned int x, unsigned int y, unsigned int z)` | \|x−y\|+z（无符号）。 |

比赛关联：`__dp4a`/`__dp2a_hi`/`__dp2a_lo` 是 INT8/INT16 量化推理的核心硬件点积指令，自写 INT8 反量化+GEMV kernel 时可直接利用；`__funnelshift_*` 常用于低比特（INT4/FP8）解包；`__mulhi`/`__umulhi` 用于快速定点缩放。

## 9. SIMD 内建函数

把 32 位寄存器拆成 2 个半字（x2 系列）或 4 个字节（x4 系列）做并行整数运算；除标注 `__host__ __device__` 者外均 `__device__`。通用语义：对对应部分计算后重新组合，作为 unsigned int 返回。

| 函数 | 签名 | 说明 |
|---|---|---|
| `__vabs2` / `__vabs4` | `(unsigned a)` | 每半字 / 每字节绝对值。 |
| `__vabsdiffs2` / `__vabsdiffs4` | `(unsigned a, unsigned b)` | 有符号每半字 / 每字节绝对差。 |
| `__vabsdiffu2` / `__vabsdiffu4` | 同上 | 无符号每半字 / 每字节绝对差 \|a−b\|。 |
| `__vabsss2` / `__vabsss4` | `(unsigned a)` | 带符号饱和的每半字 / 每字节绝对值。 |
| `__vadd2` / `__vadd4` | `(unsigned a, unsigned b)` | 每半字 / 每字节加法（环绕，忽略溢出）。 |
| `__vaddss2` / `__vaddss4` | 同上 | 带符号饱和加法。 |
| `__vaddus2` / `__vaddus4` | 同上 | 带无符号饱和加法。 |
| `__vavgs2` / `__vavgs4` | 同上 | 有符号舍入平均值。 |
| `__vavgu2` / `__vavgu4` | 同上 | 无符号舍入平均值。 |
| `__vcmpeq2` / `__vcmpeq4` | 同上 | 相等比较，命中部分置 0xffff / 0xff，否则 0。例：`__vcmpeq2(0x1234aba5, 0x1234aba6)=0xffff0000`；`__vcmpeq4` 同例返回 0xffffff00。 |
| `__vcmpges2` / `__vcmpges4` | 同上 | 有符号 a≥b 比较，置 0xffff / 0xff。例同 → 0xffff0000 / 0xffffff00。 |
| `__vcmpgeu2` / `__vcmpgeu4` | 同上 | 无符号 a≥b 比较。例同上。 |
| `__vcmpgts2` / `__vcmpgts4` | 同上 | 有符号 a>b 比较。例同 → 0x00000000。 |
| `__vcmpgtu2` / `__vcmpgtu4` | 同上 | 无符号 a>b 比较。例同上。 |
| `__vcmples2` / `__vcmples4` | 同上 | 有符号 a≤b 比较。例同 → 0xffffffff。 |
| `__vcmpleu2` / `__vcmpleu4` | 同上 | 无符号 a≤b 比较。例同上。 |
| `__vcmplts2` / `__vcmplts4` | 同上 | 有符号 a<b 比较。例同 → 0x0000ffff / 0x000000ff。 |
| `__vcmpltu2` / `__vcmpltu4` | 同上 | 无符号 a<b 比较。例同上。 |
| `__vcmpne2` / `__vcmpne4` | 同上 | 不等比较，置 0xffff / 0xff。例同 → 0x0000ffff / 0x000000ff。 |
| `__vhaddu2` / `__vhaddu4` | 同上 | 无符号平均值。 |
| `__viaddmax_s16x2` | `__host__ __device__ (unsigned a, unsigned b, unsigned c)` | 每半字 max(a+b, c)（有符号 short 解释）。 |
| `__viaddmax_s16x2_relu` | 同上 | 每半字 max(max(a+b, c), 0)。 |
| `__viaddmax_s32` | `__host__ __device__ (int a, int b, int c)` | max(a+b, c)。 |
| `__viaddmax_s32_relu` | 同上 | max(max(a+b, c), 0)。 |
| `__viaddmax_u16x2` | `__host__ __device__ (unsigned a, unsigned b, unsigned c)` | 每半字 max(a+b, c)（无符号 short）。 |
| `__viaddmax_u32` | `__host__ __device__ (unsigned a, unsigned b, unsigned c)` | max(a+b, c)（无符号）。 |
| `__viaddmin_s16x2` | 同签名 | 每半字 min(a+b, c)。 |
| `__viaddmin_s16x2_relu` | 同上 | 每半字 max(min(a+b, c), 0)。 |
| `__viaddmin_s32` | `(int a, int b, int c)` | min(a+b, c)。 |
| `__viaddmin_s32_relu` | 同上 | max(min(a+b, c), 0)。 |
| `__viaddmin_u16x2` | `(unsigned a, unsigned b, unsigned c)` | 每半字 min(a+b, c)（无符号 short）。 |
| `__viaddmin_u32` | 同上 | min(a+b, c)（无符号）。 |
| `__vibmax_s16x2` | `__host__ __device__ (unsigned a, unsigned b, bool *const pred_hi, bool *const pred_lo)` | 每半字 max(a,b)，同时 pred_hi/pred_lo 置为各半字 (a≥b) 的结果。 |
| `__vibmax_s32` | `(int a, int b, bool *const pred)` | max(a,b)，pred 置 (a≥b)。 |
| `__vibmax_u16x2` | 同 `_s16x2` 签名 | 无符号版本。 |
| `__vibmax_u32` | `(unsigned a, unsigned b, bool *const pred)` | 无符号版本。 |
| `__vibmin_s16x2` | 同 `__vibmax_s16x2` 签名 | 每半字 min(a,b)，pred_hi/pred_lo 置 (a≤b)。 |
| `__vibmin_s32` | `(int a, int b, bool *const pred)` | min(a,b)，pred 置 (a≤b)。 |
| `__vibmin_u16x2` | 同签名 | 无符号版本。 |
| `__vibmin_u32` | 同签名 | 无符号版本。 |
| `__vimax3_s16x2` | `__host__ __device__ (unsigned a, unsigned b, unsigned c)` | 每半字 max(max(a,b),c)。 |
| `__vimax3_s16x2_relu` | 同上 | 每半字 max(max(a,b),c,0)。 |
| `__vimax3_s32` | `(int a, int b, int c)` | 三路 max。 |
| `__vimax3_s32_relu` | 同上 | 三路 max 后小于 0 返回 0。 |
| `__vimax3_u16x2` | `(unsigned a, unsigned b, unsigned c)` | 无符号每半字三路 max。 |
| `__vimax3_u32` | 同上 | 无符号三路 max。 |
| `__vimax_s16x2_relu` | `__host__ __device__ (unsigned a, unsigned b)` | 每半字 max(max(a,b),0)。 |
| `__vimax_s32_relu` | `(int a, int b)` | max(max(a,b),0)。 |
| `__vimin3_s16x2` | `(unsigned a, unsigned b, unsigned c)` | 每半字 min(min(a,b),c)。 |
| `__vimin3_s16x2_relu` | 同上 | 每半字 max(min(min(a,b),c),0)。 |
| `__vimin3_s32` | `(int a, int b, int c)` | 三路 min。 |
| `__vimin3_s32_relu` | 同上 | 三路 min 后小于 0 返回 0。 |
| `__vimin3_u16x2` | `(unsigned a, unsigned b, unsigned c)` | 无符号每半字三路 min。 |
| `__vimin3_u32` | 同上 | 无符号三路 min。 |
| `__vimin_s16x2_relu` | `__host__ __device__ (unsigned a, unsigned b)` | 每半字 max(min(a,b),0)。 |
| `__vimin_s32_relu` | `(int a, int b)` | max(min(a,b),0)。 |
| `__vmaxs2` / `__vmaxs4` | `__device__ (unsigned a, unsigned b)` | 有符号每半字 / 每字节最大值。 |
| `__vmaxu2` / `__vmaxu4` | 同上 | 无符号最大值。 |
| `__vmins2` / `__vmins4` | 同上 | 有符号最小值。 |
| `__vminu2` / `__vminu4` | 同上 | 无符号最小值。 |
| `__vneg2` / `__vneg4` | `(unsigned a)` | 每半字 / 每字节取负。 |
| `__vnegss2` / `__vnegss4` | 同上 | 带符号饱和取负。 |
| `__vsads2` / `__vsads4` | `(unsigned a, unsigned b)` | 有符号绝对差之和。 |
| `__vsadu2` / `__vsadu4` | 同上 | 无符号绝对差之和。 |
| `__vseteq2` / `__vseteq4` | 同上 | 每部分 a==b 比较，两个条件都满足返回 1 否则 0。 |
| `__vsetges2` / `__vsetges4` | 同上 | a≥b（有符号），都满足返回 1。 |
| `__vsetgeu2` / `__vsetgeu4` | 同上 | a≥b（无符号），都满足返回 1。 |
| `__vsetgts2` / `__vsetgts4` | 同上 | a>b（有符号），都满足返回 1。 |
| `__vsetgtu2` / `__vsetgtu4` | 同上 | a>b（无符号），都满足返回 1。 |
| `__vsetles2` / `__vsetles4` | 同上 | a≤b，都满足返回 1。 |
| `__vsetleu2` / `__vsetleu4` | 同上 | a≤b（无符号），都满足返回 1。 |
| `__vsetlts2` / `__vsetlts4` | 同上 | a<b（有符号），都满足返回 1。 |
| `__vsetltu2` / `__vsetltu4` | 同上 | a<b（无符号），都满足返回 1。 |
| `__vsetne2` / `__vsetne4` | 同上 | a!=b，两个条件都满足返回 1。 |
| `__vsub2` / `__vsub4` | 同上 | 每半字 / 每字节减法。 |
| `__vsubss2` / `__vsubss4` | 同上 | 带符号饱和减法。 |
| `__vsubus2` / `__vsubus4` | 同上 | 带无符号饱和减法。 |
