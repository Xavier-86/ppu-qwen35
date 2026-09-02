# 第 5 章 技术参考（Technical Reference） <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [5.1.1 C++11 语言支持](#511-c11-语言支持)
- [5.1.2 C++14 语言支持](#512-c14-语言支持)
- [5.1.3 C++17 语言支持](#513-c17-语言支持)
- [5.1.4 C++20 语言支持](#514-c20-语言支持)
- [5.1.5 HGGC C++ 标准库](#515-hggc-c-标准库)
- [5.1.6 C 标准库函数](#516-c-标准库函数)
  - [5.1.6.1 `clock()` 和 `clock64()`](#5161-clock-和-clock64)
  - [5.1.6.2 `printf()`](#5162-printf)
  - [5.1.6.3 `memcpy()` 和 `memset()`](#5163-memcpy-和-memset)
  - [5.1.6.4 `malloc()` 和 `free()`](#5164-malloc-和-free)
  - [5.1.6.5 `alloca()`](#5165-alloca)
- [5.1.7 Lambda 表达式](#517-lambda-表达式)
  - [5.1.7.1 Lambda 表达式和 `__global__` 函数参数](#5171-lambda-表达式和-global-函数参数)
  - [5.1.7.2 扩展 Lambda](#5172-扩展-lambda)
  - [5.1.7.3 扩展 Lambda 的类型特征](#5173-扩展-lambda-的类型特征)
  - [5.1.7.4 扩展 Lambda 限制](#5174-扩展-lambda-限制)
  - [5.1.7.5 主机-设备 Lambda 优化注意事项](#5175-主机-设备-lambda-优化注意事项)
  - [5.1.7.6 `*this` 按值捕获](#5176-this-按值捕获)
  - [5.1.7.7 参数依赖查找 (ADL)](#5177-参数依赖查找-adl)
- [5.1.8 C/C++ 语言限制](#518-cc-语言限制)
  - [5.1.8.1 预留命名空间](#5181-预留命名空间)
  - [5.1.8.2 不支持的功能](#5182-不支持的功能)
  - [5.1.8.3 指针和内存地址](#5183-指针和内存地址)
  - [5.1.8.4 变量](#5184-变量)
  - [5.1.8.5 函数](#5185-函数)
  - [5.1.8.6 类](#5186-类)
  - [5.1.8.7 模板](#5187-模板)
- [5.1.9 C++11 限制](#519-c11-限制)
  - [5.1.9.1 inline 命名空间](#5191-inline-命名空间)
  - [5.1.9.2 inline 匿名命名空间](#5192-inline-匿名命名空间)
  - [5.1.9.3 constexpr 函数](#5193-constexpr-函数)
  - [5.1.9.4 constexpr 变量](#5194-constexpr-变量)
  - [5.1.9.5 `__global__` 变参模板](#5195-global-变参模板)
  - [5.1.9.6 默认函数 `= default`](#5196-默认函数-default)
  - [5.1.9.7 `[hggc::]std::initializer_list`](#5197-hggcstdinitializerlist)
  - [5.1.9.8 `[hggc::]std::move`、`[hggc::]std::forward`](#5198-hggcstdmovehggcstdforward)
- [5.1.10 C++14 限制](#5110-c14-限制)
  - [5.1.10.1 具有自动推导返回类型的函数](#51101-具有自动推导返回类型的函数)
- [5.1.11 C++17 限制](#5111-c17-限制)
  - [5.1.11.1 inline 变量](#51111-inline-变量)
  - [5.1.11.2 结构化绑定](#51112-结构化绑定)
- [5.1.12 C++20 限制](#5112-c20-限制)
  - [5.1.12.1 三路比较运算符](#51121-三路比较运算符)
  - [5.1.12.2 consteval 函数](#51122-consteval-函数)
- [5.2.1 PPU 特有扩展](#521-ppu-特有扩展)
  - [5.2.1.1 HGGC 特定宏](#5211-hggc-特定宏)
  - [5.2.1.2 HGGC 特定函数](#5212-hggc-特定函数)
  - [5.2.1.3 编译器优化提示](#5213-编译器优化提示)
- [5.2.2 函数和变量注解](#522-函数和变量注解)
  - [5.2.2.1 执行空间说明符](#5221-执行空间说明符)
  - [5.2.2.2 内存空间说明符](#5222-内存空间说明符)
  - [5.2.2.3 内联说明符](#5223-内联说明符)
  - [5.2.2.4 `__restrict__` 指针](#5224-restrict-指针)
  - [5.2.2.5 `__grid_constant__` 参数](#5225-gridconstant-参数)
  - [5.2.2.6 注解摘要](#5226-注解摘要)
- [5.2.3 内置类型和变量](#523-内置类型和变量)
  - [5.2.3.1 主机编译器类型扩展](#5231-主机编译器类型扩展)
  - [5.2.3.2 内置变量](#5232-内置变量)
  - [5.2.3.3 内置类型（向量类型）](#5233-内置类型向量类型)
- [5.2.4 核函数配置](#524-核函数配置)
  - [5.2.4.1 启动界限 `__launch_bounds__`](#5241-启动界限-launchbounds)
  - [5.2.4.2 每线程最大寄存器数 `__maxnreg__`](#5242-每线程最大寄存器数-maxnreg)
- [5.2.5 同步与原子操作](#525-同步与原子操作)
  - [5.2.5.1 线程块同步函数](#5251-线程块同步函数)
  - [5.2.5.2 线程束同步函数](#5252-线程束同步函数)
  - [5.2.5.3 内存栅栏函数](#5253-内存栅栏函数)
  - [5.2.5.4 原子函数](#5254-原子函数)
- [5.2.6 Warp 函数](#526-warp-函数)
  - [5.2.6.1 Warp 活动掩码](#5261-warp-活动掩码)
  - [5.2.6.2 Warp 表决函数](#5262-warp-表决函数)
  - [5.2.6.3 Warp 匹配函数](#5263-warp-匹配函数)
  - [5.2.6.4 Warp 归约函数](#5264-warp-归约函数)
  - [5.2.6.5 Warp 洗牌函数](#5265-warp-洗牌函数)
  - [5.2.6.6 Warp `__sync` 内建约束](#5266-warp-sync-内建约束)
- [5.2.7 Warp 矩阵函数（awmma，Tensor Cell）](#527-warp-矩阵函数awmmatensor-cell)
  - [5.2.7.1 描述](#5271-描述)
  - [5.2.7.2 替代浮点数](#5272-替代浮点数)
  - [5.2.7.3 元素类型和矩阵大小](#5273-元素类型和矩阵大小)
  - [5.2.7.4 示例](#5274-示例)
- [5.2.8 调试和诊断](#528-调试和诊断)
  - [5.2.8.1 断言](#5281-断言)
  - [5.2.8.2 断点函数](#5282-断点函数)
- [5.3.1 设备枚举与属性](#531-设备枚举与属性)
  - [5.3.1.1 `HGGC_VISIBLE_DEVICES`](#5311-hggcvisibledevices)
- [5.3.2 执行](#532-执行)
  - [5.3.2.1 `HGGC_LAUNCH_BLOCKING`](#5321-hggclaunchblocking)
  - [5.3.2.2 `HGGC_DEVICE_MAX_CONNECTIONS`](#5322-hggcdevicemaxconnections)
- [5.3.3 模块加载](#533-模块加载)
  - [5.3.3.1 `HGGC_MODULE_LOADING`](#5331-hggcmoduleloading)
- [5.4.1 浮点简介](#541-浮点简介)
  - [5.4.1.1 浮点格式](#5411-浮点格式)
  - [5.4.1.2 正规值和非正规值](#5412-正规值和非正规值)
  - [5.4.1.3 特殊值](#5413-特殊值)
  - [5.4.1.4 舍入](#5414-舍入)
  - [5.4.1.5 浮点数据类型](#5415-浮点数据类型)
- [5.4.2 函数精度](#542-函数精度)
  - [5.4.2.1 标准函数](#5421-标准函数)
  - [5.4.2.2 内建函数](#5422-内建函数)
- [5.5.1 查询 PPU 的计算能力](#551-查询-ppu-的计算能力)
- [5.5.2 可用特性](#552-可用特性)


> 所有 API 名、枚举值、编译选项、环境变量、硬件数值均保留原文写法。
> 注意：pdftotext 提取存在断行/乱序；个别上标指数在 PDF 文本层已损坏（显示为 `10##` 等），凡推断处均已标注「（需查原文确认）」。

本章结构：

- §5.1 C++ 语言支持：各标准特性支持表、HGGC C++ 标准库、设备端 C 库函数（clock/printf/memcpy/malloc/alloca）、Lambda、语言限制
- §5.2 HGGC 语言扩展：**量化与算子优化关键参考**（执行空间/内存空间说明符、内置变量、向量类型、`__ldg`、DPX、warp 函数、**awmma 张量核**、编译器提示）
- §5.3 环境变量：`HGGC_VISIBLE_DEVICES` 等 4 个
- §5.4 数学函数：浮点类型、全部标准/内建数学函数的 ULP 误差表
- §5.5 计算能力：ppu001 / ppu0015 硬件规格

---

# 5.1 C++ 语言支持

hggc 按以下规范处理 HGGC host 和 device 代码：

| 标准 | 编译标志 |
|---|---|
| C++03 (ISO/IEC 14882:2003) | `--std=c++03` |
| C++11 (ISO/IEC 14882:2011) | `--std=c++11` |
| C++14 (ISO/IEC 14882:2014) | `--std=c++14` |
| C++17 (ISO/IEC 14882:2017) | `--std=c++17` |
| C++20 (ISO/IEC 14882:2020) | `--std=c++20` |

传递 `--std=c++<version>` 标志会启用对应版本的所有 C++ 特性，并在调用预处理器、编译器和链接器时使用相应选项。编译器支持所有 C++ 标准的语言特性，但需遵守后续章节的限制。

## 5.1.1 C++11 语言支持

下表为 HGGC **设备代码**支持的 C++11 核心语言特性（`(FTM)*` 为原文标注，表示该特性宏相关说明）：

| 功能域 | 语言特性 | 提案 | 支持 |
|---|---|---|---|
| 类型系统 | `auto` | N1984 | ✅ |
| 类型系统 | `decltype` (FTM)* | N2343, N3276 | ✅ |
| 类型系统 | `char16_t` and `char32_t` (FTM)* | N2249 | ✅ |
| 类型系统 | `long long` | N1811 | ✅ |
| 类型系统 | `nullptr` | N2431 | ✅ |
| 类型系统 | Strongly-typed enum | N2347 | ✅ |
| 类型系统 | Forward (opaque) enum declarations | N2764 | ✅ |
| 类型系统 | Compiler support for type traits | N2255, N2984, N3142 | ✅ |
| 初始化与构造 | Initializer lists (FTM)* | N2672 | ✅ |
| 初始化与构造 | Non-static data member initializers (FTM)* | N2756 | ✅ |
| 初始化与构造 | Delegating constructors (FTM)* | N1986 | ✅ |
| 初始化与构造 | Inheriting constructors (FTM)* | N2540 | ✅ |
| 模板与泛型 | Variadic templates (FTM)* | N2242, N2555 | ✅ |
| 模板与泛型 | Template aliases (FTM)* | N2258 | ✅ |
| 模板与泛型 | Right angle brackets | N1757 | ✅ |
| 模板与泛型 | `extern template` | N1987 | ✅ |
| 模板与泛型 | Expression SFINAE | N2634 | ✅ |
| 模板与泛型 | Local and unnamed types as template parameters | N2657 | ✅ |
| 函数与 Lambda | Lambda expressions (FTM)* | N2550, N2658, N2927 | ✅ |
| 函数与 Lambda | Trailing function return types | N2541 | ✅ |
| 函数与 Lambda | Explicit conversion operators | N2437 | ✅ |
| 函数与 Lambda | Rvalue references (FTM)* | N2118, N2844, CWG1138 | ✅ |
| 函数与 Lambda | ref-qualifiers (FTM)* | N2439 | ✅ |
| 控制流与异常 | Range-for loop (FTM)* | N2930, N3271 | ✅ |
| 控制流与异常 | `noexcept` | N3050 | ✅ |
| 控制流与异常 | `static_assert` (FTM)* | N1720 | ✅ |
| 控制流与异常 | `constexpr` (FTM)* | N2235 | ✅ |
| 类与对象 | Defaulted and deleted functions | N2346 | ✅ |
| 类与对象 | Defaulted move special member functions | N3053 | ✅ |
| 类与对象 | Extended friend declarations | N1791 | ✅ |
| 类与对象 | Unrestricted unions | N2544 | ✅ |
| 类与对象 | `override` and `final` | N2928, N3206, N3272 | ✅ |
| 字面量与属性 | Unicode string literals (FTM)* | N2442 | ✅ |
| 字面量与属性 | Raw string literals (FTM)* | N2442 | ✅ |
| 字面量与属性 | User-defined literals (FTM)* | N2765 | ✅ |
| 字面量与属性 | Attributes, `[[noreturn]]` (FTM)* | N2761 | ✅ |
| 字面量与属性 | `[[carries_dependency]]` | N2556, N2643 | ✅ |
| 对齐与预处理 | `alignas` | N2341 | ✅ |
| 对齐与预处理 | `alignof` | N2341 | ✅ |
| 对齐与预处理 | C99 preprocessor | N1653 | ✅ |
| 对齐与预处理 | Inline namespaces | N2535 | ✅ |
| 并发（受限） | Atomic operations | N2427 | ❌ |
| 并发（受限） | Thread-local storage | N2659 | ❌ |
| 并发（受限） | Dynamic initialization and destruction with concurrency (magic statics) (FTM)* | N2660 | ❌ |
| 并发（受限） | Garbage Collection and Reachability-Based Leak Detection | N2670 | ❌ |

## 5.1.2 C++14 语言支持

| 功能域 | 语言特性 | 提案 | 支持 |
|---|---|---|---|
| 类型推导 | `decltype(auto)`, Return type deduction for normal functions (FTM)* | N3638 | ✅ |
| Lambda 增强 | Initialized/Generalized lambda captures (init-capture) (FTM)* | N3648 | ✅ |
| Lambda 增强 | Generic lambda expressions (FTM)* | N3649 | ✅ |
| 模板与常量 | Variable templates (FTM)* | N3651 | ✅ |
| 模板与常量 | Extended constexpr (FTM)* | N3652 | ✅ |
| 初始化 | Aggregates with default member initializers (FTM)* | N3653 | ✅ |
| 转换与字面量 | Tweaked wording for contextual conversions | N3323 | ✅ |
| 转换与字面量 | Binary literals (FTM)* | N3472 | ✅ |
| 转换与字面量 | Single quote as digit separator | N3781 | ✅ |
| 内存与属性 | Omitting/extending memory allocations | N3664 | ✅ |
| 内存与属性 | `[[deprecated]]` attribute | N3760 | ✅ |
| 内存与属性 | Sized deallocation (FTM)* | N3778 | ✅ |

## 5.1.3 C++17 语言支持

| 功能域 | 语言特性 | 提案 | 支持 |
|---|---|---|---|
| 类型与初始化 | DR11: New auto rules for direct-list-initialization | N3922 | ✅ |
| 类型与初始化 | Direct-list-initialization of enumerations | P0138R2 | ✅ |
| 类型与初始化 | Structured Bindings (FTM)* | P0217R3 | ✅ |
| 类型与初始化 | Aggregate classes with base classes (FTM)* | P0017R1 | ✅ |
| 类型与初始化 | Guaranteed copy elision (FTM)* | P0135R1 | ✅ |
| 类型与初始化 | Replacement of class objects containing reference members | P0137R1 | ✅ |
| 类型与初始化 | DR11: New specification for inheriting constructors (FTM)* | P0136R1 | ✅ |
| 模板与泛型 | `typename` in a template template parameter | N4051 | ✅ |
| 模板与泛型 | Allow constant evaluation for all constant template arguments (FTM)* | N4268 | ✅ |
| 模板与泛型 | Constant template parameters with auto type (FTM)* | P0127R2 | ✅ |
| 模板与泛型 | Fold Expressions (FTM)* | N4295 | ✅ |
| 模板与泛型 | Unary fold expressions and empty parameter packs | P0036R0 | ✅ |
| 模板与泛型 | Class template argument deduction (FTM)* | P0091R3 | ✅ |
| 模板与泛型 | DR98: Matching of template template-arguments excludes compatible templates (FTM)* | P0522R0 | ✅ |
| 模板与泛型 | Pack expansions in using-declarations (FTM)* | P0195R2 | ✅ |
| Lambda | Lambda capture of `*this` (FTM)* | P0018R3 | ✅ |
| Lambda | constexpr lambda expressions (FTM)* | P0170R1 | ✅ |
| 控制流 | constexpr if statements (FTM)* | P0292R2 | ✅ |
| 控制流 | Init-statements for if and switch | P0305R1 | ✅ |
| 控制流 | Differing begin and end types in range-based for (FTM)* | P0184R0 | ✅ |
| 控制流 | Stricter expression evaluation order | P0145R3 | ✅ |
| 属性与诊断 | `[[fallthrough]]` attribute | P0188R1 | ✅ |
| 属性与诊断 | `[[nodiscard]]` attribute | P0189R1 | ✅ |
| 属性与诊断 | `[[maybe_unused]]` attribute | P0212R1 | ✅ |
| 属性与诊断 | Attributes for namespaces and enumerators (FTM)* | N4266 | ✅ |
| 属性与诊断 | Using attribute namespaces without repetition | P0028R4 | ✅ |
| 属性与诊断 | Ignore unknown attributes | P0283R2 | ✅ |
| 属性与诊断 | `static_assert` with no message | N3928 | ✅ |
| 声明与变量 | Inline variables (FTM)* | P0386R2 | ✅ |
| 声明与变量 | Nested namespace definition | N4230 | ✅ |
| 异常与内存 | Make exception specifications part of the type system (FTM)* | P0012R1 | ✅ |
| 异常与内存 | Removing dynamic exception specifications | P0003R5 | ✅ |
| 异常与内存 | Dynamic memory allocation for over-aligned data (FTM)* | P0035R4 | ✅ |
| 字面量与预处理 | u8 character literals | N4267 | ✅ |
| 字面量与预处理 | Hexadecimal floating-point literals (FTM)* | P0245R1 | ✅ |
| 字面量与预处理 | `__has_include` in preprocessor conditionals | P0061R1 | ✅ |
| 废弃与清理 | Remove deprecated use of the register keyword | P0001R1 | ✅ |
| 废弃与清理 | Remove deprecated `operator++(bool)` | P0002R1 | ✅ |
| 废弃与清理 | Removing trigraphs | N4086 | ✅ |

## 5.1.4 C++20 语言支持

**依赖：GCC 版本 ≥ 10.0，Clang 版本 ≥ 10.0**

| 功能域 | 语言特性 | 提案 | 支持 |
|---|---|---|---|
| 概念与约束 | Concepts (FTM)* | P0734R0 | ✅ |
| 概念与约束 | Yet another approach for constrained declarations | P1141R2 | ✅ |
| 常量求值 | constexpr virtual function (FTM)* | P1064R0 | ✅ |
| 常量求值 | constexpr try-catch blocks | P1002R1 | ✅ |
| 常量求值 | Immediate functions (`consteval`) (FTM)* | P1073R3 | ✅ |
| 常量求值 | `constinit` (FTM)* | P1143R2 | ✅ |
| 常量求值 | `std::is_constant_evaluated()` (FTM)* | P0595R2 | ✅ |
| 常量求值 | constexpr container operations (FTM)* | P0784R7 | ✅ |
| 常量求值 | Trivial default initialization in constexpr functions | P1331R2 | ✅ |
| 常量求值 | Unevaluated asm-declaration in constexpr functions | P1668R1 | ✅ |
| 常量求值 | Changing the active member of a union inside constexpr (FTM)* | P1330R0 | ✅ |
| 常量求值 | DR11: Specify when constexpr function definitions are needed for constant evaluation (FTM)* | P0859R0 | ✅ |
| 常量求值 | `dynamic_cast` and polymorphic `typeid` in constant expressions | P1327R1 | ✅ |
| 比较运算 | Three-way comparison operator (FTM)* | P0515R3 | ✅ |
| 比较运算 | Consistency improvements for comparisons | P1120R0 | ✅ |
| 比较运算 | `<=> != ==` | P1185R2 | ✅ |
| 比较运算 | Synthesizing Three-way comparison for specified comparison category | P1186R3 | ✅ |
| 比较运算 | Allow defaulting comparisons by value | P1946R0 | ✅ |
| 比较运算 | Remove `std::weak_equality` and `std::strong_equality` | P1959R0 | ✅ |
| Lambda | Allow Lambda capture `[=, this]` | P0409R2 | ✅ |
| Lambda | template-parameter-list for generic lambdas (FTM)* | P0428R2 | ✅ |
| Lambda | Lambdas in unevaluated contexts | P0315R4 | ✅ |
| Lambda | Default constructible and assignable stateless lambdas | P0624R2 | ✅ |
| Lambda | Pack-expansions in lambda init-captures (FTM)* | P0780R2 | ✅ |
| Lambda | DR11: Simplifying implicit lambda capture | P0588R1 | ✅ |
| Lambda | Deprecate implicit capture of this via `[=]` | P0806R2 | ✅ |
| Lambda | Lambda capture and storage class specifiers of structured bindings | P1091R3, P1381R1 | （原文未标 ✅/❌，需查原文确认） |
| 类与初始化 | Designated initializers (FTM)* | P0329R4 | ✅ |
| 类与初始化 | Default member initializers for bit-fields | P0683R1 | ✅ |
| 类与初始化 | Initializer list constructors in class template argument deduction | P0702R1 | ✅ |
| 类与初始化 | Prohibit aggregates with user-declared constructors | P1008R1 | ✅ |
| 类与初始化 | Parenthesized initialization of aggregates (FTM)* | P0960R3 | ✅ |
| 类与初始化 | Type mismatch of defaulted special member functions | P0641R2 | ✅ |
| 类与初始化 | Conditionally trivial special member functions (FTM)* | P0848R3 | ✅ |
| 类与初始化 | DR11: Implicit move for more local objects and rvalue references | P1825R0 | ✅ |
| 模板 | class template argument deduction for alias templates (FTM)* | P1814R0 | ✅ |
| 模板 | class template argument deduction for aggregates (FTM)* | P1816R0, P2082R1 | ✅ |
| 模板 | Class types in Constant template parameters | P0732R2 | ✅ |
| 模板 | Inconsistencies with constant template parameters (FTM)* | P1907R1 | ✅ |
| 模板 | Access checking on specializations | P0692R1 | ✅ |
| 结构化绑定 | DR17: Relaxing the structured bindings customization point finding rules | P0961R1 | ✅ |
| 结构化绑定 | DR17: Allow structured bindings to accessible members | P0969R0 | ✅ |
| 控制流 | init-statements for range-based for | P0614R1 | ✅ |
| 控制流 | DR11: Relaxing the range-for loop customization point finding rules | P0962R1 | ✅ |
| 属性 | Attributes `[[likely]]` and `[[unlikely]]` | P0479R5 | ✅ |
| 属性 | Attribute `[[no_unique_address]]` | P0840R2 | ✅ |
| 属性 | `[[nodiscard]]` with message | P1301R4 | ✅ |
| 属性 | DR17: `[[nodiscard]]` for constructors | P1771R1 | ✅ |
| 类型与转换 | `char8_t` (FTM)* | P0482R6 | ✅ |
| 类型与转换 | `explicit(bool)` (FTM)* | P0892R2 | ✅ |
| 类型与转换 | Signed integers are two's complement | P1236R1 | ✅ |
| 类型与转换 | const&-qualified pointers to members | P0704R1 | ✅ |
| 类型与转换 | Make typename more optional | P0634R3 | ✅ |
| 类型与转换 | Permit conversions to arrays of unknown bound | P0388R4 | ✅ |
| 类型与转换 | DR11: Converting from T* to bool should be considered narrowing | P1957R2 | ✅ |
| 预处理与字面量 | `VA_OPT` | P0306R4, P1042R1 | ✅ |
| 预处理与字面量 | Integrating feature-test macros | P0941R2 | ✅ |
| 预处理与字面量 | Stronger Unicode requirements | P1041R4, P1139R2 | ✅ |
| 声明与命名空间 | Nested inline namespaces | P1094R2 | ✅ |
| 声明与命名空间 | `using enum` (FTM)* | P1099R5 | ✅ |
| 声明与命名空间 | ADL and function templates that are not visible | P0846R0 | ✅ |
| 内存与对象 | Destroying operator delete (FTM)* | P0722R3 | ✅ |
| 内存与对象 | Deprecating some uses of `volatile` | P1152R4 | ✅ |
| 内存与对象 | DR98: Pseudo-destructors end object lifetimes | P0593R6 | ✅ |
| 内存与对象 | DR11: Array size deduction in new-expressions | P1009R2 | ✅ |
| 内存与对象 | Deprecate comma operator in subscripts | P1161R3 | ✅ |
| 并发与模块（受限） | Coroutines (FTM)* | P0912R5, LWG3393 | ❌ |
| 并发与模块（受限） | Modules (FTM)* | P1103R3 | ❌ |
| 并发与模块（受限） | DR11: Explicitly defaulted functions with different exception specifications | P1286R2 | ❌ |

## 5.1.5 HGGC C++ 标准库

HGGC 提供了一个 C++ 标准库（STL）实现，优点：

- 在主机和设备端均可用。
- 与 SAIL 工具包支持的所有 Linux 平台兼容。
- 与 SAIL 工具包支持的所有 PPU 架构兼容。
- 与前面主版本的所有 SAIL 工具包兼容。
- 提供了 C++17 的反向移植特性，并包括来自 C++20、C++23 和 C++26 的标准库特性。
- 支持扩展数据类型，例如 128 位整数（`__int128`）、半精度浮点（`__half`）和 Bfloat16（`__ppu_bfloat16`）。
- 针对设备代码高度优化。

此外还提供标准库之外的扩展功能：数学函数、内存操作、同步原语、容器扩展、HGGC 内置的高级抽象、C++ TIX 封装接口等。该标准库随 HGGC Toolkit 一并提供。

> 比赛关联：设备端 STL + 扩展类型支持意味着可以在 kernel 里直接用 `hggc::std::` 容器/算法与 `__ppu_bfloat16`，移植现有 CUDA 风格 kernel 时优先用 `hggc::std::` 替代 `std::`（见 5.1.9.3 警告）。

## 5.1.6 C 标准库函数

### 5.1.6.1 `clock()` 和 `clock64()`

```cpp
__host__ __device__ clock_t clock();
__device__ long long clock64();
```

在设备代码中执行时，返回每个计算单元（CU）计数器的当前值，该计数器以每时钟周期加一的速率递增。在核函数起始和终止位置分别记录计数器数值并取差值，可估算设备调度线程期间消耗的时钟周期总数。但该数值**不能**准确反映实际执行线程指令所需的时钟周期量，原因：

- **线程调度机制**：线程采用时间片轮转调度策略，该值显著高于实际执行周期。
- **系统空闲计数**：计数器在系统空闲状态下仍持续递增。
- **资源等待延迟**：线程因等待内存访问及其他资源被挂起期间，计数器仍在累积。

因此该测量值更适合分析**系统级调度行为**，而非精确指令执行周期统计。

> NOTE：`hggc::std::clock()` 提供在 `<hggc/std/ctime>` 头文件中；可移植的 C++ `<chrono>` 实现提供在 `<hggc/std/chrono>` 头文件中。

> 比赛关联：kernel 内 profiling（测各阶段 cycle 数，如量化反量化/GEMM/attention 各占多少周期）可用 `clock64()`，但要注意时间片调度会高估，适合做相对占比分析而非绝对延迟。

### 5.1.6.2 `printf()`

```cpp
int printf(const char *format[, arg, ...]);
```

设备端 `printf()` 允许核函数将格式化文本发送到主机端标准输出流，用法与 C 标准库基本一致。设备端多线程并行执行，每个线程独立调用 `printf()` 并使用自身局部数据格式化——所有线程都执行到 `printf()` 时，主机端输出流中会出现与活跃线程数量相同的输出行。

**返回值语义**（与 C 标准略有不同）：

- 成功 → 已解析参数个数（无参数时为 0）
- NULL 格式字符串 → `-1`
- 内部错误 → `-2`

实现细节：`printf()` 内部依赖共享数据结构管理输出缓冲区，调用了 `printf()` 的线程可能比未调用的线程花费更多时钟周期，额外开销取决于格式字符串复杂度和参数数量。HGGC 本身不保证线程间执行顺序（除非 `__syncthreads()` 等显式屏障），此行为差异不应被视为排序保证。

**格式说明符**：`%[flags][width][.precision][size]type`

- Flags：`#`, `' '`, `0`, `+`, `-`
- Width：`*`, `0-9`
- Precision：`0-9`
- Size：`h`, `l`, `ll`
- Type：`%cdiouxXpeEfgGaAs`

**限制**：

- 格式字符串最终在主机侧解析渲染，行为受主机 C 库实现影响；HGGC 覆盖主流编译器的共同子集，边界行为可能有差异。
- 设备端 `printf()` 不对标志与类型的组合做合法性校验——不合法组合原样传给主机 C 库，输出未定义。
- 单次 `printf()` 最多支持 **32 个格式化参数**（不含格式字符串本身），超出部分被静默忽略，对应占位符以字面文本出现。

> WARNING：`long` 类型在 32 位和 64 位平台宽度不同，使用 `%ld` 时必须确保编译和运行平台字长一致。

**主机端缓冲区**：HGGC 为 `printf()` 预分配固定大小的环形缓冲区（**默认 18M 字节**），输出超过容量时新内容覆盖最早数据。缓冲区不实时传输到主机，刷新时机：

| 场景分类 | 触发时机 | 相关 API |
|---|---|---|
| 核函数执行 | 核函数启动前刷新；若设置了 `LAUNCH_BLOCKING=1` 则启动后亦刷新 | `<<< >>>`、`hgLaunchKernel()` |
| 数据传输 | 阻塞式主机-设备内存拷贝完成时 | `hggcMemcpy*()` / `hgMemcpy*()` |
| 显式同步 | 调用同步 API 使主机等待设备完成时 | `hggcDeviceSynchronize()`、`hgCtxSynchronize()`、`hggcStreamSynchronize()`、`hgStreamSynchronize()`、`hggcEventSynchronize()` 的阻塞变体、`hgEventSynchronize()` |
| 资源生命周期 | 模块加载/卸载或上下文销毁时 | `hgModuleLoad()` / `hgModuleUnload()`、`hggcDeviceReset()` / `hgCtxDestroy()` |
| 主机回调 | 执行注册的主机端回调之前 | `hggcLaunchHostFunc()` / `hgLaunchHostFunc()` |

> WARNING：进程正常退出时缓冲区不会被自动刷新。退出前应显式调用同步 API。

缓冲区大小设置/查询 API（默认 18 MB）：

```cpp
hggcDeviceGetLimit(size_t* size, hggcLimitPrintfFifoSize);
hggcDeviceSetLimit(hggcLimitPrintfFifoSize, size_t size);
```

**示例 1**（二维线程索引与多种数据类型格式化输出）：

```cpp
#include <stdio.h>
__global__ void reportPosition(int width) {
    int col = threadIdx.x;
    int row = threadIdx.y;
    int gid = row * width + col;
    printf("[%d,%d] gid=%d area=%d\n", row, col, gid, width * width);
}
int main() {
    dim3 block(3, 2);
    reportPosition<<<1, block>>>(3);
    hggcDeviceSynchronize();
    return 0;
}
```

运行后产生 6 行输出（3×2 个线程各一行），顺序取决于硬件调度，例如：

```
[1,2] gid=5 area=9
[0,0] gid=0 area=9
[0,1] gid=1 area=9
[1,0] gid=3 area=9
[0,2] gid=2 area=9
[1,1] gid=4 area=9
```

**示例 2**（条件控制打印，仅每行首线程打印摘要）：

```cpp
#include <stdio.h>
__global__ void rowSummary(int width) {
    if (threadIdx.x == 0) {
        printf("Row %d: threads [0..%d]\n", threadIdx.y, width - 1);
    }
}
int main() {
    dim3 block(4, 3);
    rowSummary<<<1, block>>>(4);
    hggcDeviceSynchronize();
    return 0;
}
```

输出仅 3 行（每行对应一个 `threadIdx.y`）。

### 5.1.6.3 `memcpy()` 和 `memset()`

```cpp
__host__ __device__ void *memcpy(void *dest, const void *src, size_t size);
__host__ __device__ void *memset(void *ptr, int value, size_t size);
```

- `memcpy`：将 `size` 字节从 `src` 复制到 `dest`。
- `memset`：将 `ptr` 指向内存块的 `size` 字节设置为 `value`（当做 unsigned char）。

> NOTE：建议使用 `<hggc/std/cstring>` 中的 `hggc::std::memcpy()` 和 `hggc::std::memset()` 作为更安全的版本。

### 5.1.6.4 `malloc()` 和 `free()`

设备端动态内存管理接口统一通过**设备堆（device heap）**分配和释放：

| 功能 | C 风格 API | HGGC C++ API（`<hggc/std/cstdlib>`） | 执行空间 | 说明 |
|---|---|---|---|---|
| 分配（默认对齐） | `malloc(size)` | `hggc::std::malloc(size)` | `__host__ __device__` | 返回至少 size 字节的 **16 字节对齐**指针 |
| 零初始化分配 | — | `hggc::std::calloc(count, size)` | `__host__ __device__` | 分配并零初始化 |
| 指定对齐分配 | `__hg_aligned_device_malloc(size, align)` | `hggc::std::aligned_alloc()` | `__device__` | 对齐值须为非零的二的次幂 |
| 释放 | `free(ptr)` | `hggc::std::free(ptr)` | `__host__ __device__` | 传 NULL 安全忽略；重复释放为未定义行为 |

所有分配函数在内存不足时返回 `NULL`。

**生命周期与跨线程共享**：分配的内存在整个 HGGC 上下文生命周期内有效——不限于分配时所在核函数，后续核函数启动的线程同样可以访问和释放。任何线程都可以释放另一个线程分配的内存，但调用方须确保同一指针不被释放两次。

**堆内存配置**：设备堆容量必须在首次调用任何设备端分配函数（`malloc()`、`hggc::std::malloc()`、`new` 等）**之前**完成配置。未显式设置时，运行时默认 **8 MB** 堆大小。查询/配置接口：

| 操作 | API 层级 | API |
|---|---|---|
| 查询当前堆大小 | Runtime API | `hggcDeviceGetLimit(size_t* size, hggcLimitMallocHeapSize)` |
| 查询当前堆大小 | Driver API | `hgCtxGetLimit()` |
| 设置堆大小 | Runtime API | `hggcDeviceSetLimit(hggcLimitMallocHeapSize, size_t size)` |

`hggcDeviceSetLimit` 设置的堆大小为**下限**——实际分配的堆空间可能大于请求值。堆的物理内存在**模块加载阶段一次性分配**；若分配失败，模块加载返回 `HGGC_ERROR_SHARED_OBJECT_INIT_FAILED`。约束：

1. 模块加载完成后堆大小不可更改，运行时也不会自动扩容。
2. 设备堆占用的显存独立于主机端 `hggcMalloc` 等 API 的分配池，两者不共享配额。

**设备端与主机端内存隔离**：设备端分配的内存（`malloc()`、`hggc::std::malloc()`、`hggc::std::calloc()`、`__hg_aligned_device_malloc()`、`hggc::std::aligned_alloc()` 或 `new`）与主机端分配的内存（`hggcMalloc` 等）属于不同内存管理域，不能交叉操作——设备端内存不能用 `hggcMemcpy` 等主机 API 访问或释放，主机端内存也不能用设备端 `free()`、`hggc::std::free()` 或 `delete` 释放。

**示例 1**（每线程独立分配→写入→读回验证→释放）：

```cpp
#include <stdio.h>
#include <stdlib.h>
__global__ void perThreadAlloc() {
    int tid = threadIdx.x;
    int *buf = (int *)malloc(sizeof(int));
    if (buf == NULL) {
        printf("Thread %d: allocation failed\n", tid);
        return;
    }
    *buf = tid * tid;
    printf("Thread %d: wrote %d at %p\n", tid, *buf, buf);
    free(buf);
}
int main() {
    hggcDeviceSetLimit(hggcLimitMallocHeapSize, 64 * 1024 * 1024);
    perThreadAlloc<<<1, 4>>>();
    hggcDeviceSynchronize();
    return 0;
}
```

输出（顺序取决于硬件调度）：

```
Thread 2: wrote 4 at 0xd1c31830
Thread 0: wrote 0 at 0xd1c318b0
Thread 3: wrote 9 at 0xd1c31930
Thread 1: wrote 1 at 0xd1c319b0
```

**示例 2**（逐线程块分配，通过 `__shared__` 指针共享以保证访问合并）：

```cpp
#include <stdlib.h>
__global__ void kernel() {
    __shared__ int *data;
    // 块中的第一个线程执行分配并通过共享内存与其他所有线程共享指针，以便访问可以合并。
    if (threadIdx.x == 0) {
        size_t size = blockDim.x * 8; // 为每个线程分配 8 字节。
        data = (int *)malloc(size);
    }
    __syncthreads();
    // 检查失败。
    if (data == nullptr)
        return;
    // 线程索引到内存中，确保合并。
    for (int i = 0; i < 8; ++i)
        data[i * blockDim.x + threadIdx.x] = threadIdx.x;
    // 确保所有线程在释放前完成。
    __syncthreads();
    // 只有一个线程可以释放内存！
    if (threadIdx.x == 0)
        free(data);
}
int main() {
    // 设置 16 兆字节的堆大小。
    hggcDeviceSetLimit(hggcLimitMallocHeapSize, 16 * 1024 * 1024);
    kernel<<<10, 128>>>();
    hggcDeviceSynchronize(); // 等待 kernel 执行结束
    return 0;
}
```

**示例 3**（跨核函数启动持续存在的分配）：

```cpp
#include <stdio.h>
#include <stdlib.h>
const int NUM_BLOCKS = 2;
__device__ int *data_ptrs[NUM_BLOCKS]; // 每块指针。
__global__ void kernel() {
    // 只有块中的第一个线程执行分配，因为我们只需要对每个块进行一次分配。
    if (threadIdx.x == 0)
        data_ptrs[blockIdx.x] = (int *)malloc(blockDim.x * 4);
    __syncthreads();
    // 检查失败。
    if (data_ptrs[blockIdx.x] == nullptr)
        return;
    // 用所有线程并行清零数据。
    data_ptrs[blockIdx.x][threadIdx.x] = 0;
}
// 简单示例：将线程 ID 存储到每个元素中。
__global__ void memoryUse() {
    int *memoryPtr = data_ptrs[blockIdx.x];
    if (memoryPtr != nullptr)
        memoryPtr[threadIdx.x] += threadIdx.x;
}
// 打印缓冲区内容然后再释放它。
__global__ void memoryFree() {
    int *memoryPtr = data_ptrs[blockIdx.x];
    if (memoryPtr != nullptr)
        printf("Block %d, Thread %d: final input = %d\n", blockIdx.x, threadIdx.x,
               memoryPtr[threadIdx.x]);
    // 只在一个线程中释放！
    if (threadIdx.x == 0)
        free(memoryPtr);
}
int main() {
    hggcDeviceSetLimit(hggcLimitMallocHeapSize, 128 * 1024 * 1024);
    kernel<<<NUM_BLOCKS, 3>>>();      // 分配内存。
    memoryUse<<<NUM_BLOCKS, 3>>>();   // 使用内存。
    memoryFree<<<NUM_BLOCKS, 3>>>();  // 释放内存。
    hggcDeviceSynchronize();
    return 0;
}
```

输出：

```
Block 0, Thread 2: final input = 6
Block 0, Thread 1: final input = 3
Block 0, Thread 0: final input = 0
Block 1, Thread 2: final input = 6
Block 1, Thread 1: final input = 3
Block 1, Thread 0: final input = 0
```

> 比赛关联：设备堆可用于 kernel 内部的动态 scratch（如 beam search 中间结构、动态 KV 缓冲），但必须在模块加载前用 `hggcDeviceSetLimit(hggcLimitMallocHeapSize, ...)` 预留——这直接关系显存规划；注意设备堆与 `hggcMalloc` 池相互独立，两者都要计入显存预算。

### 5.1.6.5 `alloca()`

```cpp
__host__ __device__ void *alloca(size_t size);
```

在调用者栈内分配 `size` 字节内存。从设备代码调用时，内存起始位置 **8 字节对齐**。调用者返回时内存自动释放。

```cpp
__device__ void deviceFunction(int num_items) {
    float2 *ptr = (float2 *)alloca(num_items * sizeof(float2));
    // 使用 ptr
}
```

## 5.1.7 Lambda 表达式

编译器通过将 lambda 表达式或闭包类型（C++11）与**最内层封闭函数作用域**的执行空间相关联来确定其执行空间。没有封闭函数作用域时，执行空间为 `__host__`。也可以用扩展 lambda 语法显式指定。

```cpp
// 全局作用域：无封闭函数 → __host__
auto preprocess = [](float x) { return x / 255.0f; }; // __host__
void buildPipeline() {
    // 封闭函数为 __host__ → lambda 继承 __host__
    auto normalize = [](float x) { return (x - 0.5f) * 2.0f; }; // __host__
    [](int n) { return n * n; }; // __host__, 闭包类型
}
__device__ void cuActivation(float *buf, int idx) {
    // 封闭函数为 __device__ → lambda 继承 __device__
    auto relu = [](float v) { return v > 0.f ? v : 0.f; }; // __device__
    buf[idx] = relu(buf[idx]);
}
__global__ void inferKernel(float *data, int n) {
    // __global__ 函数体视为 __device__ 空间
    auto sigmoid = [](float x) { return 1.0f / (1.0f + expf(-x)); }; // __device__
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) data[i] = sigmoid(data[i]);
}
__host__ __device__ void quantize(float *src, int8_t *dst, int idx) {
    // 封闭函数为 __host__ __device__ → lambda 继承 __host__ __device__
    auto clampAndRound = [](float v) { return (int8_t)fminf(fmaxf(v, -128.f), 127.f); };
    dst[idx] = clampAndRound(src[idx]); // __host__ __device__
}
using ReduceFn = float (*)(float, float);
// 默认参数表达式位于全局作用域 → __host__
__device__ void treeReduce(float *buf, int n,
    ReduceFn combine = [](float a, float b) { return a + b; } /* __host__ */) {}
```

### 5.1.7.1 Lambda 表达式和 `__global__` 函数参数

只有 lambda 表达式或闭包类型的执行空间是 `__device__` 或 `__host__ __device__` 时，才能用作 `__global__` 函数的参数。**全局或命名空间范围的 lambda 不能用作 `__global__` 函数参数。**

示例（需要编译选项 `--extended-lambda`）：

```cpp
template <typename Op>
__global__ void applyElementwise(Op op, float *data, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) data[idx] = op(data[idx]);
}
__device__ void deviceLaunch(float *buf, int n) {
    // 设备端动态并行启动（需要分离编译 -rdc=true）
    applyElementwise<<<1, n>>>(
        [] __host__ __device__(float x) { return x * 0.1f; }, buf, n); // 正确, 扩展lambda
}
auto globalScaler = [] __host__ __device__(float x) { return x * 2.0f; };
void hostLaunch(float *d_buf, int n) {
    int blocks = (n + 255) / 256;
    // 正确：__device__ 扩展lambda
    applyElementwise<<<blocks, 256>>>(
        [] __device__(float x) { return fmaxf(x, 0.f); }, d_buf, n);
    // 正确：__host__ __device__ 扩展lambda
    applyElementwise<<<blocks, 256>>>(
        [] __host__ __device__(float x) { return tanhf(x); }, d_buf, n);
    // 错误：普通lambda具有 __host__ 执行空间，不能作为 __global__ 参数
    // applyElementwise<<<blocks, 256>>>([](float x) { return x; }, d_buf, n);
}
```

### 5.1.7.2 扩展 Lambda

hggc 标志 `--extended-lambda` 允许在 lambda 表达式中显式标注执行空间，标注应出现在 lambda 引入符之后、可选的 lambda 声明符之前。指定该标志时 hggc 定义宏 **`__HGGCCC_EXTENDED_LAMBDA__`**。

- 扩展 lambda 定义在 `__host__` 或 `__host__ __device__` 函数的直接或嵌套块作用域内。
- 扩展设备 lambda：用 `__device__` 关键字注释的 lambda。
- 扩展主机-设备 lambda：用 `__host__ __device__` 关键字注释的 lambda。

与标准 lambda 不同，扩展 lambda 可以用作 `__global__` 函数中的类型参数。

```cpp
void hostFunction() {
    auto lambda1 = [] {};                       // 不是扩展lambda: 没有显式执行空间注释
    auto lambda2 = [] __device__ {};            // 扩展lambda
    auto lambda3 = [] __host__ __device__ {};   // 扩展lambda
    auto lambda4 = [] __host__ {};              // 不是扩展lambda
}
__host__ __device__ void hostDeviceFunction() {
    auto lambda1 = [] {};                       // 不是扩展lambda
    auto lambda2 = [] __device__ {};            // 扩展lambda
    auto lambda3 = [] __host__ __device__ {};   // 扩展lambda
    auto lambda4 = [] __host__ {};              // 不是扩展lambda
}
__device__ void deviceFunction() {
    // 此函数内的所有lambda都不是扩展lambda，因为外层函数不是 __host__ 或 __host__ __device__ 函数。
    auto lambda1 = [] {};
    auto lambda2 = [] __device__ {};
    auto lambda3 = [] __host__ __device__ {};
    auto lambda4 = [] __host__ {};
}
auto lambda = [] __host__ __device__ {}; // 不是扩展lambda，因为它没有定义在 __host__ 或 __host__ __device__ 函数内
```

### 5.1.7.3 扩展 Lambda 的类型特征

编译器提供类型特征在编译时检测扩展 lambda 的闭包类型：

| 返回值 | 函数名 | 参数 | 说明 |
|---|---|---|---|
| `bool` | `__hg_is_extended_device_lambda_closure_type` | `type` | 若 `type` 是为扩展 `__device__` lambda 创建的闭包类，返回 `true`，否则 `false` |
| `bool` | `__hg_is_extended_device_lambda_with_preserved_return_type` | `type` | 若 `type` 是扩展 `__device__` lambda 闭包类且 lambda 以尾随返回类型定义，返回 `true`，否则 `false` |
| `bool` | `__hg_is_extended_host_device_lambda_closure_type` | `type` | 若 `type` 是为扩展 `__host__ __device__` lambda 创建的闭包类，返回 `true`，否则 `false` |

类型特征在所有编译模式中可用；扩展 lambda 模式不可用时，特征始终返回 `false`。

示例——利用类型特征实现 PPU 核函数分派器的编译期校验：

```cpp
#include <type_traits>
template <typename Fn>
__global__ void dispatchKernel(Fn op, float *data, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) data[idx] = op(data[idx]);
}
template <typename Fn>
void launchOnPPU(Fn op, float *d_buf, int n) {
    // 编译期校验：仅接受设备端可执行的扩展 lambda
    static_assert(
        __hg_is_extended_device_lambda_closure_type(Fn) ||
        __hg_is_extended_host_device_lambda_closure_type(Fn),
        "launchOnPPU 仅接受 __device__ 或 __host__ __device__ 扩展 lambda");
    int threads = 256;
    int blocks = (n + threads - 1) / threads;
    dispatchKernel<<<blocks, threads>>>(op, d_buf, n);
}
void runInference(float *d_activations, int count) {
    // 扩展设备lambda：通过类型特征校验
    auto relu = [] __device__(float x) -> float { return x > 0.f ? x : 0.f; };
    static_assert(__hg_is_extended_device_lambda_closure_type(decltype(relu)));
    static_assert(!__hg_is_extended_host_device_lambda_closure_type(decltype(relu)));
    // 带保留返回类型的扩展设备lambda
    auto scale = [] __device__(float x) -> float { return x * 0.01f; };
    static_assert(
        __hg_is_extended_device_lambda_with_preserved_return_type(decltype(scale)));
    // 扩展主机-设备lambda：主机端也可调用
    auto clamp = [] __host__ __device__(float x) -> float {
        return x < -6.f ? -6.f : (x > 6.f ? 6.f : x);
    };
    static_assert(!__hg_is_extended_device_lambda_closure_type(decltype(clamp)));
    static_assert(__hg_is_extended_host_device_lambda_closure_type(decltype(clamp)));
    // 普通lambda（无执行空间注释）：不满足校验，无法传递给 launchOnPPU
    auto hostOnly = [](float x) { return x; };
    static_assert(!__hg_is_extended_device_lambda_closure_type(decltype(hostOnly)));
    static_assert(!__hg_is_extended_host_device_lambda_closure_type(decltype(hostOnly)));
    launchOnPPU(relu, d_activations, count);
    launchOnPPU(clamp, d_activations, count);
    // launchOnPPU(hostOnly, ...); // 编译错误：static_assert 失败
}
```

### 5.1.7.4 扩展 Lambda 限制

HGGC 编译器在将代码传给主机编译器之前，会把扩展 lambda 表达式替换为**命名空间作用域的占位符类型**，占位符类型的模板参数中包含封闭函数（enclosing function）的地址——这是正确实例化以扩展 lambda 闭包类型为模板参数的 `__global__` 函数模板所必需的。

封闭函数确定规则：从扩展 lambda 所在块作用域向外查找，直到找到第一个不是 lambda `operator()` 的函数：

1. 扩展 lambda 按定义总是位于某个 `__host__` 或 `__host__ __device__` 函数的块作用域中（直接或间接）。
2. 若包含该扩展 lambda 的最内层函数不是另一个 lambda 的 `operator()`，则该函数即为封闭函数。
3. 若包含它的是嵌套 lambda 的 `operator()`，则继续向外层展开，找到最外层 lambda 所处的具名函数 `F`——`F` 即为封闭函数。
4. 若最外层 lambda 定义在全局/命名空间作用域（而非任何函数体内），则不存在封闭函数。

```cpp
void hostFunction() {
    // 情况 2：直接位于具名函数中 → 封闭函数 = hostFunction
    auto lambda1 = [] __device__ {};
    auto lambda2 = [] {
        // 情况 3：嵌套在另一个 lambda 内 → 向外找到 hostFunction
        auto lambda3 = [] __host__ __device__ {};
    };
}
// 情况 4：最外层 lambda 在全局作用域 → 无封闭函数
auto global_lambda = [] {
    auto lambda4 = [] __host__ __device__ {};
};
```

### 5.1.7.5 主机-设备 Lambda 优化注意事项

扩展主机-设备 lambda 可从主机代码调用。其占位符类型通过**间接函数调用**调用原始 lambda 的 `operator()`。间接调用可能导致主机编译器对扩展主机-设备 lambda 的优化少于隐式或显式 `__host__` lambda（后者可轻松内联 lambda 主体到调用上下文；遇到扩展主机-设备 lambda 时主机编译器可能无法内联原始 lambda 主体）。

### 5.1.7.6 `*this` 按值捕获

C++17 引入 `*this` 捕获模式：编译器复制 `*this` 表示的对象，而非按值捕获 `this` 指针（详见 P0018R3）。HGGC 支持在 `__device__` 和 `__global__` 函数内定义的 lambda 以及在主机代码中定义的**扩展设备专用 lambda**的 `*this` 捕获，前提是使用 `--extended-lambda` 标志。

```cpp
#include <cstdio>
template <typename T> __global__ void kernelFunction(T lambda) {
    printf("\n input = %d", lambda());
}
struct S {
    int var;
    __host__ __device__ S() : var(0) {};
    void run() {
        // 注意"*this"捕获规范
        auto lambda = [=, *this] __device__ {
            // 引用"var"导致'*this'表示的对象按值捕获，并且 PPU代码将访问'copy_of_star_this->var'。
            return var + 1;
        };
        // 核函数启动成功
        kernelFunction<<<1, 1>>>(lambda);
        hggcDeviceSynchronize();
    }
};
int main() {
    S s;
    s.run();
}
```

`*this` 捕获模式不允许用于主机代码中定义的非标注 lambda 或扩展主机-设备 lambda，除非所选语言方言启用 `*this` 捕获：

```cpp
struct S {
    int var;
    __host__ __device__ S() : var(10) {};
    void hostFunction() {
        // 正确，在扩展设备专用lambda中使用
        auto lambda1 = [=, *this] __device__ { return var; };
        // 在扩展主机-设备lambda中使用，如果语言方言未启用*this捕获，则出错
        auto lambda2 = [=, *this] __host__ __device__ { return var; };
        // 在主机函数中的非标注lambda中使用，如果语言方言未启用*this捕获，则出错
        auto lambda3 = [=, *this] { return var; };
    }
    __device__ void deviceFunction() {
        // 正确，在设备专用函数中定义的lambda中使用
        auto lambda1 = [=, *this] __device__ { return var; };
        auto lambda2 = [=, *this] __host__ __device__ { return var; };
        auto lambda3 = [=, *this] { return var; };
    }
    __host__ __device__ void hostDeviceFunction() {
        // 正确，在扩展设备专用lambda中使用
        auto lambda1 = [=, *this] __device__ { return var; };
        // 在扩展主机-设备lambda中使用，如果语言方言未启用*this捕获，则出错
        auto lambda2 = [=, *this] __host__ __device__ { return var; };
        auto lambda3 = [=, *this] { return var; };
    }
};
```

### 5.1.7.7 参数依赖查找 (ADL)

扩展 lambda 被替换为占位符类型后，其模板参数之一使用封装原始 lambda 的函数的地址，可能导致附加命名空间参与 ADL，使主机编译器选择错误的函数：

```cpp
namespace N1 {
struct S {};
template <typename T> void f(T){};
}; // namespace N1
namespace N2 {
template <typename T> int f(T) { return 0; };
template <typename T> void run(T lambda) { f(lambda); }
} // namespace N2
void g(N1::S s) {
    // 对于扩展设备专用lambda，发送到主机编译器的代码被替换为占位符类型实例化表达式，
    // 结果，命名空间'N1'参与了N2::run主体中"f()"调用的 ADL 查找，导致歧义。
    auto lambda = [=] __device__ {};
    N2::run(lambda);
}
```

占位符类型涉及 `N1` 命名空间，因此 `N1` 参与 `N2::run()` 中 `f(in)` 的 ADL 查找，发现 `N1::f` 和 `N2::f` 多个候选，导致主机编译失败。

## 5.1.8 C/C++ 语言限制

### 5.1.8.1 预留命名空间

`hggc::`、`hg::` 和 `cooperative_groups::` 是 HGGC 的保留顶层命名空间，开发者代码不得在其中（包括嵌套命名空间）添加任何声明或定义，否则属于未定义行为。允许在用户自定义命名空间内部创建同名嵌套命名空间。

```cpp
// ✗ 直接向保留命名空间添加符号
namespace hggc {
void myHelper(); // 未定义行为
}
// ✓ 在用户命名空间内使用同名嵌套命名空间
namespace mylib {
namespace hggc {
void myHelper(); // 合法
}
}
// ✗ using namespace 会将 mylib::hggc 的符号引入全局 hggc，效果等同于直接添加
using namespace mylib;
```

### 5.1.8.2 不支持的功能

- 运行时类型信息 (RTTI) 和异常在设备代码中不受支持：`typeid`、`dynamic_cast`、`try/catch/throw`。
- `long double` 在设备代码中不受支持。
- 三字符组 (Trigraphs) 在任何平台上都不受支持。
- 用户定义的 `operator new`、`operator new[]`、`operator delete`、`operator delete[]` 不能用来替换编译器提供的内置函数，主机和设备上均为未定义行为。

### 5.1.8.3 指针和内存地址

指针解引用（`*pointer`、`pointer->member`、`pointer[0]`）只允许在同一执行空间中进行。以下情况导致未定义行为（通常是段错误和应用终止）：

- 在主机代码上解引用指向**全局内存、共享内存或常量内存**的指针。
- 在设备代码中解引用指向主机内存的指针。

函数相关限制：

- 不允许在主机代码中获取 `__device__` 函数的地址。
- 主机代码中获取的 `__global__` 函数地址不能在设备代码中使用，反之亦然。
- 通过 `hggcGetSymbolAddress()` 获取的 `__device__` 或 `__constant__` 变量地址只能在主机代码中使用。

### 5.1.8.4 变量

#### 5.1.8.4.1 局部变量

主机上执行的函数内的非 `extern` 变量声明不允许使用 `__device__`、`__shared__`、`__managed__`、`__constant__` 内存空间说明符：

```cpp
__host__ void hostFunction() {
    __device__ int d;     // 错误
    __shared__ int s;     // 错误
    __managed__ int m;    // 错误
    __constant__ int c;   // 错误
    extern __device__ int e; // 正确，extern __device__ 变量
}
```

设备上执行的函数内既不是 `extern` 也不是 `static` 的变量声明不允许使用 `__device__`、`__constant__`、`__managed__`：

```cpp
__device__ void deviceFunction() {
    int i;                  // 正确，__device__ 变量
    __constant__ int c;     // 错误
    __managed__ int m;      // 错误
    extern __device__ int e; // 正确
}
```

#### 5.1.8.4.2 const 限定变量

全局、命名空间或类作用域中声明的没有内存空间注释（`__device__` 或 `__constant__`）的 `const` 限定变量被视为主机变量，设备代码不能包含对其的引用或取地址。

满足以下条件可直接在设备代码中使用：

- 在使用点之前已用常量表达式初始化；
- 类型不是 `volatile` 限定的；
- 类型为内置整数类型或内置浮点类型之一。

C++14 起建议用 `constexpr` 或 `inline constexpr`（C++17）代替 `const` 限定变量（`constexpr` 不受相同类型限制）。`__managed__` 变量不支持 `const` 限定类型。

```cpp
const int ConstInt = 1;
const float ConstFloat = 1.0f;
inline constexpr float Constexpr = 1.0f; // C++17
struct S {
    static const int ConstInt = 1;
    static const float ConstFloat = 1.0f;        // 错误，静态const变量不能是float
    static inline constexpr float Constexpr = 1.0f; // 正确
};
extern const int ExternVar;
__device__ void foo() {
    int array1[ConstInt];              // 正确
    int array2[S::ConstInt];           // 正确
    const float var1 = ConstFloat;     // 正确
    constexpr float var2 = Constexpr;  // 正确
    int var3 = ExternVar;              // 错误，"ExternVar"未用常量表达式初始化
    int &var4 = ConstInt;              // 错误，对主机变量的引用
    int *var5 = &ConstInt;             // 错误，主机变量的地址
}
```

#### 5.1.8.4.3 volatile 限定变量

HGGC 保留 `volatile` 仅为 ISO C++ 兼容性，在 PPU 架构上实际用途极为有限（参见 P1152R0）。对 `volatile` 对象的读写**不具有原子性**：编译器生成一条或多条带 volatile 语义的 TIX 指令，但既不保证全局可见的内存操作顺序，也不保证硬件内存事务数量与 TIX 指令数量一一对应。

**`volatile` 不适用于线程间同步**。原子内存操作不仅提供同步保证，且在 PPU 上比 volatile 性能更好。需要线程间可见性和顺序保证时应使用 `hggc::atomic_ref`、`hggc::atomic` 或传统原子函数。以下三个示例分别演示"生产者写入数据 → 消费者等待并读取"的协作模式：

```cpp
// 方式一：hggc::atomic_ref（适合已有普通变量的场景）
#include <hggc/atomic>
__global__ void producerConsumer(int *ready, int *payload) {
    // 使用device作用域的原子引用
    hggc::atomic_ref<int, hggc::thread_scope_device> status_flag{*ready};
    switch(threadIdx.x) {
    case 0: // 生产者线程
        *payload = 2048;                                          // 写入有效负载
        status_flag.store(1, hggc::memory_order_release);         // 信号发布
        break;
    case 1: // 消费者线程
        // 等待信号就绪
        while (status_flag.load(hggc::memory_order_acquire) != 1) {
            __nanosleep(100); // 添加停顿减少忙等待开销
        }
        if (*payload != 2048) {
            __trap(); // 提供更明确的内联陷阱指令
        }
        break;
    }
}
```

```cpp
// 方式二：hggc::atomic（适合变量从一开始就定义为原子类型的场景）
#include <hggc/atomic>
__global__ void atomicHandoff(
    hggc::atomic<int, hggc::thread_scope_device> *status_flag,
    int *payload) {
    switch (threadIdx.x) {
    case 0:
        *payload = 2048;
        status_flag->store(1, hggc::memory_order_release);
        break;
    case 1:
        while (status_flag->load(hggc::memory_order_acquire) != 1) {
            __nanosleep(100);
        };
        if (*payload != 2048)
            __trap();
        break;
    }
}
```

```cpp
// 方式三：传统原子函数 + __threadfence()（适合不使用 C++ 原子类型的代码）
__global__ void legacyAtomicHandoff(int *status_flag, int *payload) {
    switch (threadIdx.x) {
    case 0:
        *payload = 2048;
        __threadfence();
        atomicExch(status_flag, 1);
        break;
    case 1:
        while (atomicAdd(status_flag, 0) != 1) {
            __nanosleep(100);
        };
        __threadfence();
        if (*payload != 2048)
            __trap();
        break;
    }
}
```

> 比赛关联：自研解码调度 kernel（如 continuous batching 的设备端队列、spin-lock）必须用原子而非 volatile；`__nanosleep` 退避能降低忙等待功耗与总线争抢。

#### 5.1.8.4.4 static 变量

设备代码中允许使用 static 变量的情况：

- 在 `__global__` 或仅 `__device__` 函数内。
- 在 `__host__ __device__` 函数内：
  - 没有显式内存空间的 static 变量（自动推断）；
  - 具有显式内存空间的 static 变量（`static __device__/__constant__/__shared__/__managed__`），仅当定义了 `__HGGC_ARCH__` 时才允许。

`__host__ __device__` 函数内的 static 变量根据执行空间的不同持有不同的值。

```cpp
struct TrivialStruct { int x; };
struct NonTrivialStruct { __device__ NonTrivialStruct(int x) {} };
__device__ void deviceFunction(int x) {
    static int var1;                // 正确，隐式 __device__ 内存空间说明符
    static int var2 = 11;           // 正确
    static int var3 = x;            // 错误，不允许动态初始化
    static __managed__ int var4;    // 正确，显式
    static __device__ int var5;     // 正确，显式
    static __constant__ int var6;   // 正确，显式
    static __shared__ int var7;     // 正确，显式
    static TrivialStruct s1;        // 正确
    static TrivialStruct s2{22};    // 正确
    static TrivialStruct s3{x};     // 错误，不允许动态初始化
    static NonTrivialStruct s4{3};  // 错误，不允许动态初始化
}
__host__ __device__ void hostDeviceFunction() {
    static int var1; // 正确，隐式 __device__ 内存空间说明符
#ifdef __HGGC_ARCH__
    static __device__ int var2; // 正确，声明仅在设备编译期间可见
#else
    static int var3;            // 正确，声明仅在主机编译期间可见
#endif
}
```

主机与设备端 static 计数相互独立的示例：

```cpp
#include <cassert>
__host__ __device__ int hostDeviceFunction() {
    static int var = 0;
    var++;
    return var;
}
__global__ void kernel() {
    int ret = hostDeviceFunction(); // var = 1（设备侧副本）
    assert(ret == 4);               // 失败
}
int main() {
    hostDeviceFunction();           // var = 1（主机侧）
    hostDeviceFunction();           // var = 2
    int ret = hostDeviceFunction(); // var = 3
    assert(ret == 3);               // OK
    kernel<<<1, 1>>>();
    hggcDeviceSynchronize();
}
```

#### 5.1.8.4.5 extern 变量

非 RDC 模式下编译时，不能用 `extern` 定义具有外部链接的 `__device__`、`__shared__`、`__managed__`、`__constant__` 变量。唯一例外是动态分配的 `__shared__` 变量：

```cpp
__device__ int var1;
extern __device__ int var2; // 非 RDC 模式（Relocatable Device Code）下的报警
extern __shared__ int var3; // OK
```

### 5.1.8.5 函数

#### 5.1.8.5.1 递归

`__global__` 函数**不支持递归**；`__device__` 和 `__host__ __device__` 函数没有此限制。

#### 5.1.8.5.2 外部链接

具有外部链接的设备变量或函数需要跨多个翻译单元的分离编译模式（RDC）。

#### 5.1.8.5.3 形式参数

形式参数不允许使用 `__device__`、`__shared__`、`__managed__`、`__constant__` 内存空间说明符（但编译不会报错）：

```cpp
void deviceFunction1(__device__ int x) { } // 错误，__device__ 参数
void deviceFunction2(__shared__ int x) { } // 错误，__shared__ 参数
```

#### 5.1.8.5.4 `__global__` 函数参数

- 不能有可变数量的参数（C 的省略号 `...` 和 `va_list`）。允许 C++11 可变参数模板，但受 `__global__` 可变参数模板限制（见 5.1.9.5）。
- 函数参数通过**常量内存**传递到设备，总大小限制为 **32764 字节**。
- 参数不能按引用或右值引用传递。
- 参数不能是 `std::initializer_list` 类型。
- 多态类参数（`virtual`）是未定义行为。
- Lambda 表达式和闭包类型是允许的，但受 5.1.7.1 限制。

#### 5.1.8.5.5 `__global__` 函数参数传递

从**设备端**启动 `__global__` 函数时，所有参数必须同时满足平凡可复制（trivially copyable）和平凡可析构（trivially destructible）。

从**主机端**启动时允许非平凡类型参数，但传参机制与标准 C++ 值传递语义有两处关键差异：

**1. 参数按位拷贝传递，拷贝构造函数不会被调用。** HGGC Runtime 用 memcpy 搬运参数原始字节，用户自定义拷贝构造中的初始化逻辑和副作用均不执行。对在拷贝构造中建立自引用指针的类型尤其危险：

```cpp
#include <cassert>
struct Widget {
    int id = 1;
    int *self_ref;
    Widget() = default;
    __host__ __device__ Widget(const Widget &) { self_ref = &id; }
};
__global__ void checkWidget(Widget w) {
    // 断言失败：self_ref 仍指向主机端旧对象的 id 地址
    assert(w.self_ref == &w.id);
}
void hostCheck(Widget w) {
    assert(w.self_ref == &w.id); // 主机端正常：拷贝构造函数被调用
}
int main() {
    Widget w;
    hostCheck(w);
    checkWidget<<<1, 1>>>(w);
    hggcDeviceSynchronize();
}
```

**2. 参数的析构函数可能在核函数完成前执行。** 核函数启动是异步的，`<<<>>>` 返回后主机立即继续；参数离开作用域时主机端析构正常触发，此时设备端核函数可能尚未开始或仍在运行。对析构有共享状态副作用的类型可能引发数据竞争：

```cpp
#include <cassert>
__managed__ int counter = 0;
struct Guard {
    __host__ __device__ ~Guard() { counter = 99; }
};
__global__ void useGuard(Guard g) {
    // 可能失败：主机端析构函数已将 counter 设为 99
    assert(counter == 0);
}
int main() {
    Guard g;
    useGuard<<<1, 1>>>(g);
    // g 离开 main 作用域时析构 → counter 被主机端修改
    // 而此时 useGuard 可能仍在设备上执行
    hggcDeviceSynchronize();
}
```

### 5.1.8.6 类

#### 5.1.8.6.1 类类型变量

用 `__device__`、`__constant__`、`__managed__`、`__shared__` 说明符定义的变量，其类类型必须拥有**空构造函数和空析构函数**。"空"指平凡（trivial），或在当前翻译单元中同时满足：

| 判定对象 | 需同时满足的条件 |
|---|---|
| 空构造函数 | ➀ 构造函数有显式定义；➁ 无参数、无成员初始值列表、函数体为空 `{}`；➂ 类自身无 virtual 函数、无 virtual 基类、无非 static 数据成员的就地初始值；➃ 所有基类的默认构造函数均满足"空"条件；➄ 所有非 static 数据成员（含数组元素）的默认构造函数均满足"空"条件 |
| 空析构函数 | ➀ 析构函数有显式定义；➁ 函数体为空 `{}`；➂ 类自身无 virtual 函数、无 virtual 基类；➃ 所有基类的析构函数均满足"空"条件；➄ 所有非 static 数据成员（含数组元素）的析构函数均满足"空"条件 |

条件具有递归性。与 C++ 标准的 trivially constructible / trivially destructible 概念密切相关（[class.ctor] / [class.dtor]），具体判定以上表为准。

#### 5.1.8.6.2 数据成员

`class`、`struct`、`union` 数据成员不允许使用 `__device__`、`__shared__`、`__managed__`、`__constant__` 说明符。仅支持编译时计算的 static 数据成员（`const` 限定和 `constexpr`）：

```cpp
struct S {
    static const int var1 = 1;
    static constexpr int var2 = 1;        // C++11
    static inline constexpr int var3 = 1; // C++17
};
```

#### 5.1.8.6.3 成员函数

`__global__` 函数不能是 `struct`、`class` 或 `union` 的成员；可以在 `friend` 声明中使用，但不能定义：

```cpp
struct S {
    friend __global__ void f();   // 正确，仅友元声明
    friend __global__ void g() {} // 错误，友元定义
};
```

#### 5.1.8.6.4 隐式声明和非虚显式默认函数

隐式声明/显式默认（`= default`）的特殊成员函数包括：默认构造、拷贝构造、移动构造、拷贝赋值、移动赋值、析构。设 `F` 为首次声明时隐式声明或显式默认的非 virtual 函数，则 `F` 的执行空间说明符是**调用它的所有函数的执行空间说明符的并集**（`__global__` 调用方视为 `__device__` 调用方）：

```cpp
class TensorMeta {
    int rank;
    int dims[4];
public:
    __host__ __device__ TensorMeta() : rank(0), dims{} {}
};
class ActivationDesc : public TensorMeta { float alpha; };
class ConvConfig : public TensorMeta { int padH, padW; };
__device__ void initOnDevice(float *workspace) {
    ActivationDesc act; // 仅从 __device__ 调用
    ConvConfig conv;    // 从 __device__ 和 __host__ 都调用
}
__host__ void prepareOnHost() {
    ConvConfig conv;    // 从 __host__ 调用
}
```

此时 `ActivationDesc::ActivationDesc()` 被视为 `__device__`；`ConvConfig::ConvConfig()` 被视为 `__host__ __device__`。

若 `F` 是隐式声明的 virtual 函数（如 virtual 析构），被它重写的虚函数 `D` 不是隐式声明的，则 `D` 的执行空间会被加入 `F` 的执行空间集合：

```cpp
struct LayerBase {
    virtual __host__ __device__ ~LayerBase() {}
};
struct ReluLayer : LayerBase {}; // 隐式声明的虚析构函数
// ~ReluLayer() 具有 __host__ __device__ 执行空间说明符
struct DeviceAllocator {
    virtual __device__ ~DeviceAllocator() = default;
};
struct PoolAllocator : DeviceAllocator {}; // 隐式声明的虚析构函数
// ~PoolAllocator() 具有 __device__ 执行空间说明符
```

#### 5.1.8.6.5 多态类

多态类（有 virtual 函数、派生自多态类、或有多态数据成员）限制：

- 设备↔主机复制多态对象（包括作为 `__global__` 函数参数）是未定义行为。
- 重写的 virtual 函数执行空间必须与基类函数匹配。

```cpp
struct C {
    virtual __host__ __device__ void f() {}
};
__global__ void kernel(C c) {
    c.f(); // 未定义行为
}
int main() {
    C c;
    kernel<<<1, 1>>>(c);
    hggcDeviceSynchronize();
}
```

```cpp
struct Base {
    virtual __host__ __device__ void f() {}
};
struct Derived : Base {
    __device__ void f() override {} // 错误
};
```

### 5.1.8.7 模板

以下任一条件成立时，类型不能用作 `__global__` 函数或 `__device__/__constant__` 变量（C++14）的模板参数：

- 该类型在 `__host__` 或 `__host__ __device__` 函数作用域内定义。
- 该类型未命名（匿名结构体或 lambda 表达式），在 `__device__` 或 `__global__` 函数内部除外。
- 该类型是 private 或 protected 类成员，在 `__device__` 或 `__global__` 函数内部除外。
- 该类型由上述任何类型组合构成。

```cpp
template <typename T> __global__ void kernel() {}
template <typename T> __device__ int var; // C++14
struct { int var; } S;
void hostFunction() {
    struct LocalStruct {};
    kernel<LocalStruct><<<1, 1>>>();  // 错误，LocalStruct 在主机函数内定义
    int data = 1;
    hggcMemcpyToSymbol(var<LocalStruct>, &data, sizeof(data)); // 错误，同上
    kernel<decltype(S)><<<1, 1>>>();  // 错误，未命名类型
}
class C {
private:
    struct PrivateStruct {};
public:
    static void launch() {
        kernel<PrivateStruct><<<1, 1>>>(); // 错误，私有类型
    }
};
```

## 5.1.9 C++11 限制

### 5.1.9.1 inline 命名空间

封闭命名空间中存在同名同类型签名的实体时，不允许在 inline 命名空间内定义：`__global__` 函数；`__device__`、`__constant__`、`__managed__`、`__shared__` 变量；表面或纹理类型变量（如 `hggcSurfaceObject_t`、`hggcTextureObject_t`）。

```cpp
__device__ int var; // 全局作用域
inline namespace NS {
__device__ int var; // 命名空间作用域，编译报错
} // namespace NS
```

### 5.1.9.2 inline 匿名命名空间

以下实体不能在 inline 匿名命名空间内的命名空间作用域中声明：`__global__` 函数；`__device__`、`__constant__`、`__managed__`、`__shared__` 变量；表面或纹理类型变量（`hggcSurfaceObject_t`、`hggcTextureObject_t`）。

### 5.1.9.3 constexpr 函数

默认情况下，constexpr 函数不能从具有不兼容执行空间的函数中调用：

```cpp
constexpr __device__ int deviceFunction() { return 0; }
int main() {
    int x = deviceFunction(); // 错误，在主机代码中调用仅设备的constexpr函数
}
```

注意：即使模板函数标记了 `constexpr`，函数模板特化也可能不是 constexpr 函数。

**宽松的 constexpr 函数支持**：实验性标志 **`--expt-relaxed-constexpr`** 可放宽约束（`__global__` 函数仍不能声明为 constexpr），同时定义宏 **`__HGGCCC_RELAXED_CONSTEXPR__`**。启用后：

1. 常量求值上下文中的跨执行空间 constexpr 调用被支持：

```cpp
constexpr __host__ int hostFunction(int x) { return x; };
__global__ void kernelFunction() {
    constexpr int val = hostFunction(1); // 正确，常量求值上下文
}
constexpr __device__ int deviceFunction(int x) { return x; }
int main() {
    constexpr int val = deviceFunction(1); // 正确，常量求值上下文
}
```

2. 设备代码生成期间为仅主机 constexpr 函数体生成设备代码（未使用或仅在 constexpr 上下文中调用的除外）：

```cpp
// 注意："hostFunction"在生成的设备代码中发出，因为它在非constexpr上下文中从设备代码调用
constexpr int hostFunction(int x) { return x; }
__device__ int deviceFunction(int in) {
    return hostFunction(in); // 正确，即使参数不是常量表达式
}
```

3. 设备函数的所有代码限制也适用于从设备代码调用的仅主机 constexpr 函数，但编译器可能不会发出构建时诊断。不支持的模式（可能无编译错误）：
   - ODR-使用主机变量或仅主机非 constexpr 函数：

```cpp
int var;
constexpr int *hostFunction() { return &var; };
__device__ int deviceFunction() {
    // 错误，hostFunction()试图引用主机变量 'var'。
    return *hostFunction();
}
```

   - 使用异常 throw/catch 和 RTTI typeid/dynamic_cast：

```cpp
struct Base {};
struct Derived : public Base {};
constexpr int hostFunction(Base *memoryPtr) {
    // 错误，在 PPU 上执行的代码中使用typeid
    if (typeid(memoryPtr) == typeid(Derived))
        return 1;
    else
        throw int{1}; // 错误，在 PPU 上执行的代码中使用throw
}
__device__ void deviceFunction() {
    Derived d;
    // 错误，hostFunction()尝试使用typeid和throw()
    int val = hostFunction(&d);
}
```

4. 主机代码生成期间，仅设备 constexpr 函数体保留在送给主机编译器的代码中；若设备函数体 ODR-使用命名空间作用域设备变量或非 constexpr 设备函数，则从主机代码调用它不受支持（可能无诊断但运行时不正确）：

```cpp
__device__ int var;
constexpr __device__ int *deviceFunction() { return &var; };
int hostFunction() {
    // 错误，deviceFunction()试图引用设备变量 'var'，代码将编译，但不会正确执行。
    return *deviceFunction();
}
```

> **警告**：由于上述限制且缺少编译器诊断，建议避免从设备代码调用标准 C++ 头文件中的 `std::` 函数（其实现因主机平台而异）。**强烈建议调用 HGGC C++ 标准库中 `hggc::std::` 命名空间下的等效功能。**

### 5.1.9.4 constexpr 变量

默认 constexpr 变量不能在不兼容执行空间的函数中使用。以下情况可直接在设备代码中使用：

- C++ 标量类型（不含指针和成员指针）：`nullptr_t`、`bool`、整数类型（`char`、`signed char`、`unsigned`、`long long` 等）、浮点类型（`float`、`double`）；
- 枚举器：`enum` 和 `enum class`；
- 类类型：具有 constexpr 构造函数的 `class`、`struct`、`union`；
- 上述类型的原始数组（如 `int[]`），仅当在 `constexpr __device__` 或 `constexpr __host__ __device__` 函数内部使用时。

不允许 `constexpr __managed__` 和 `constexpr __shared__` 变量。

```cpp
constexpr int ConstexprVar = 1; // 标量类型
struct S { static constexpr int ConstexprVar = 2; };
constexpr S s = S{}; // 类类型
constexpr int array[] = {1, 2, 3};
__device__ constexpr int get(int idx) {
    return array[idx]; // 正确
}
__device__ void f(int idx) {
    int var1 = ConstexprVar;      // 正确
    int var2 = S::ConstexprVar;   // 正确
    const int &var3 = ConstexprVar; // 错误，引用主机constexpr变量
    const int *var4 = &ConstexprVar; // 错误，主机constexpr变量的地址
    int var5 = get(2);   // 正确，'get(2)'是常量表达式
    int var6 = get(idx); // 错误，'get(idx)'不是常量表达式
    int var7 = array[2]; // 错误，'array'不是标量类型
    S var8 = s;          // 正确
}
```

### 5.1.9.5 `__global__` 变参模板

- 只允许单个包参数。
- 包参数必须列在模板参数列表的最后。

```cpp
template <typename... Pack> __global__ void kernel1(); // 正确
template <typename... Pack, template T>
__global__ void kernel2(); // 错误，参数包不是最后一个参数
template <typename... Pack1, typename... Pack2>
__global__ void kernel3(); // 错误，超过一个参数包
```

### 5.1.9.6 默认函数 `= default`

HGGC 编译器推断显式默认成员函数的执行空间（同 5.1.8.6.4）。除函数在类外定义或为 virtual 的情况外，编译器**忽略**显式默认函数上的执行空间说明符：

```cpp
struct S1 { S1() = default; };
void hostFunction() { S1 s; }          // __host__ __device__ 构造函数
__device__ void deviceFunction1() { S1 s; } // __host__ __device__ 构造函数
struct S2 { __device__ S2() = default; };   // 错误，__device__ 注解被忽略
struct S3 { __host__ S3(); };
S3::S3() = default;                     // 类外定义，不被忽略
__device__ void deviceFunction2() { S3 s; } // 错误，__host__ 构造函数
struct S4 {
    // S4::~S4 具有主机执行空间，不被忽略，因为是虚函数
    virtual __host__ ~S4() = default;
};
__device__ void deviceFunction3() {
    S4 s;
    // 对's'的隐式析构函数调用：
    // 错误：从 __device__ 函数 'deviceFunction3' 到 __host__ 函数 'S4::~S4' 的调用
}
```

### 5.1.9.7 `[hggc::]std::initializer_list`

默认 HGGC 编译器隐式认为 `[hggc::]std::initializer_list` 的成员函数具有 `__host__ __device__` 执行空间，可直接从设备代码调用。标志 **`--no-host-device-initializer-list`** 禁用此行为（其成员函数视为 `__host__`）。`__global__` 函数不能有 `[hggc::]std::initializer_list` 类型参数。

```cpp
#include <initializer_list>
__device__ void f(std::initializer_list<int> in) {}
__device__ void deviceFunction() {
    f({4, 5, 6});   // (a) 仅包含常量表达式的初始化列表。
    int i = 1;
    f({i, 5, 6});   // (b) 至少有一个非常量元素的初始化列表。此形式可能比(a)有更好的性能。
}
```

### 5.1.9.8 `[hggc::]std::move`、`[hggc::]std::forward`

默认隐式认为 `std::move` 和 `std::forward` 函数模板具有 `__host__ __device__` 执行空间，可直接从设备代码调用。

> NOTE：`hggc::std::move` 和 `hggc::std::forward` 始终具有 `__host__ __device__` 执行空间。

## 5.1.10 C++14 限制

### 5.1.10.1 具有自动推导返回类型的函数

`__global__` 函数不能具有推导返回类型 `auto`。

> NOTE：HGGC 前端编译器在调用主机编译器前将函数声明更改为 void 返回类型，可能破坏主机代码中对 `__device__` 函数推导返回类型的推断，在设备函数体之外引用时可能发出编译时错误。

```cpp
// 推导返回类型 decltype(auto) 具有相同的行为
__device__ auto deviceFunction(int x) { return x; }
__global__ void kernelFunction() {
    int x = sizeof(deviceFunction(1)); // 正确
}
void hostFunction() {
    struct S {
        // 错误，在设备函数体外引用
        decltype(deviceFunction(1)) var;
        S() : var(1) {}
    };
}
```

## 5.1.11 C++17 限制

### 5.1.11.1 inline 变量

单个翻译单元中，inline 变量与常规变量相比没有额外功能或实际优势。

> NOTE：使用 gcc/g++ 主机编译器时，`__managed__` 内存空间说明符声明的 inline 变量可能对调试器不可见。

```cpp
static inline __device__ int var1;
namespace {
inline __device__ int var2;
inline __shared__ int var3;
static inline __device__ int var4;
inline __device__ int var5;
} // namespace
```

### 5.1.11.2 结构化绑定

结构化绑定不能使用内存空间说明符（`__device__`、`__shared__`、`__constant__`、`__managed__`）声明：

```cpp
struct S { int x, y; };
__device__ auto [a, b] = S{1, 2}; // 错误
```

## 5.1.12 C++20 限制

### 5.1.12.1 三路比较运算符

`<=>` 在设备代码中受支持，但某些使用隐式依赖主机实现的 C++ 标准库功能。可能需要指定 `--expt-relaxed-constexpr` 消除警告，且要求主机实现满足设备代码要求：

```cpp
#include <compare> // std::strong_ordering 实现
struct S {
    int x, y;
    auto operator<=>(const S &) const = default;          // (a)
    __host__ __device__ bool operator<=>(int) const { return false; } // (b)
};
__host__ __device__ bool hostDeviceFunction(S a, S b) {
    if (a <=> 1) // 正确，调用用户定义的主机设备重载 (b)
        return true;
    // 正确，调用隐式声明的函数 (a)
    // 注意：它需要设备兼容的std::strong_ordering在头文件<compare>中提供的实现
    return a < b;
}
```

### 5.1.12.2 consteval 函数

`consteval` 函数可以从主机和设备代码中调用，与其执行空间无关：

```cpp
consteval int hostFunction() { return 10; }
__device__ consteval int deviceFunction() { return 10; }
__device__ int f() {
    return hostFunction(); // 正确，即使从设备代码调用
}
__host__ __device__ int hostDeviceFunction() {
    return deviceFunction(); // 正确，即使从主机设备代码调用
}
```

> 比赛关联（§5.1 小结）：移植现有 C++/CUDA 风格推理代码到 HGGC 时，§5.1 的限制清单是排错手册——最常见的坑是：设备代码禁用 RTTI/异常、`__global__` 参数 ≤32764 字节且按位拷贝（含 STL 容器的结构体不能直接传）、`volatile` 不能用于同步、设备端应统一使用 `hggc::std::` 而非 `std::`。

---

# 5.2 HGGC 语言扩展

## 5.2.1 PPU 特有扩展

### 5.2.1.1 HGGC 特定宏

#### 5.2.1.1.1 `__HGGC_ARCH__`

宏 `__HGGC_ARCH__` 表示正在编译代码的 PPU 的**虚拟架构**，其值可能与设备的实际计算能力不同。可用于编写针对特定 PPU 架构的专门代码路径（获得最佳性能或使用特定架构特性和指令），也可用于区分主机代码和设备代码。

- `__HGGC_ARCH__` **仅在设备代码中定义**（即 `__device__`、`__host__ __device__`、`__global__` 函数中）。
- 宏的值与 hggc 选项 `ppu_<version>` 的关系：**`__HGGC_ARCH__ = <version> * 10`**。

示例：

```bash
hgcc --gpu-architecture ppu_10 test.hg   # 将 __HGGC_ARCH__ 定义为 100
```

**约束**：

1. 分离编译模式下，具有外部链接的函数或变量定义的存在与否不应依赖于 `__HGGC_ARCH__` 的定义或其值：

```cpp
#if !defined(__HGGC_ARCH__)
void hostFunction() { // 错误：hostFunction()的定义只在__HGGC_ARCH__未定义时存在
}
#endif
```

2. 分离编译中，`__HGGC_ARCH__` 不得在头文件中使用（防止对象具有不同行为），或者所有对象必须为同一虚拟架构编译。如果头文件中定义了弱函数或模板函数且其行为依赖 `__HGGC_ARCH__`，当对象为不同计算架构编译时，不同对象中的函数实例可能冲突。例如头文件 `a.h`：

```cpp
template <typename T> __device__ T *get() {
#if __HGGC_ARCH__ == 100
    return nullptr;
#else
    __shared__ T arr[256];
    return arr;
#endif
}
```

若 `a.hg` 和 `b.hg` 都包含 `a.h` 并对相同类型实例化 `get()`，而 `b.hg` 期望非 NULL 地址，且编译为：

```bash
hgcc --gpu-architecture ppu_10 -dc a.hg
hgcc --gpu-architecture ppu_15 -dc b.hg
hgcc --gpu-architecture ppu_15 a.o b.o
```

链接时只使用一个版本的 `get()`，行为取决于选择了哪个版本。为避免此问题：要么 `a.hg`/`b.hg` 为同一计算架构编译，要么不在共享头文件函数中使用 `__HGGC_ARCH__`。

3. 以下实体的类型签名不应依赖于 `__HGGC_ARCH__` 是否定义或其值：`__global__` 函数和函数模板；`__device__` 和 `__constant__` 变量；纹理和表面。

```cpp
#if !defined(__HGGC_ARCH__)
typedef int type;
#else
typedef double type;
#endif
__device__ type var;              // 错误：var的类型取决于__HGGC_ARCH__
__global__ void kernel(type x) {  // 错误：kernel的类型取决于__HGGC_ARCH__
    // ...
}
```

4. 若 `__global__` 函数模板从主机实例化并启动，无论 `__HGGC_ARCH__` 是否定义或其值如何，都必须使用相同的模板参数实例化：

```cpp
__device__ int result;
template <typename T> __global__ void kernelFunction(T x) { result = x; }
__host__ __device__ void hostDeviceFunction(void) {
#if !defined(__HGGC_ARCH__)
    kernelFunction<<<1, 1>>>(1); // 错误："kernelFunction<int>" 实例化只在__HGGC_ARCH__未定义时！
#endif
}
int main(void) {
    hostDeviceFunction();
    hggcDeviceSynchronize();
    return 0;
}
```

编译器不保证会为上述不支持的 `__HGGC_ARCH__` 用途生成诊断信息。

#### 5.2.1.1.2 HGGC 特性测试宏

| 宏 | 含义 | 启用方式 |
|---|---|---|
| `__HGGCCC_EXTENDED_LAMBDA__` | 支持扩展 lambda | `--expt-extended-lambda` 或 `--extended-lambda` |
| `__HGGCCC_RELAXED_CONSTEXPR__` | 支持宽松 constexpr 函数 | `--expt-relaxed-constexpr` |

### 5.2.1.2 HGGC 特定函数

#### 5.2.1.2.1 地址空间谓词函数

```cpp
__device__ unsigned __isGlobal(const void *devPtr);
__device__ unsigned __isShared(const void *devPtr);
__device__ unsigned __isConstant(const void *devPtr);
__device__ unsigned __isGridConstant(const void *devPtr);
__device__ unsigned __isLocal(const void *devPtr);
```

若 `ptr` 包含指定地址空间中对象的通用地址，返回 1，否则返回 0。参数为 NULL 指针时行为未定义。

- `__isGlobal()`：全局内存空间。
- `__isShared()`：共享内存空间。
- `__isConstant()`：常量内存空间。
- `__isGridConstant()`：使用 `__grid_constant__` 注解的核函数参数。
- `__isLocal()`：局部内存空间。

#### 5.2.1.2.2 地址空间转换函数

HGGC 指针（`T*`）是通用指针，可访问任何存储位置的对象。地址空间转换函数在通用地址和特定地址空间地址之间转换；当编译器无法确定指针地址空间时（如跨翻译单元或与 TIX 指令交互）很有用。

```cpp
// TIX: ppu.cvta.to.global
__device__ size_t __cvta_generic_to_global(const void *devPtr);
// TIX: ppu.cvta.to.shared
__device__ size_t __cvta_generic_to_shared(const void *devPtr);
// TIX: ppu.cvta.to.const
__device__ size_t __cvta_generic_to_constant(const void *devPtr);
// TIX: ppu.cvta.to.local
__device__ size_t __cvta_generic_to_local(const void *devPtr);
__device__ void *__cvta_global_to_generic(size_t rawbits);   // TIX: ppu.cvta.global
__device__ void *__cvta_shared_to_generic(size_t rawbits);   // TIX: ppu.cvta.shared
__device__ void *__cvta_constant_to_generic(size_t rawbits); // TIX: ppu.cvta.const
__device__ void *__cvta_local_to_generic(size_t rawbits);    // TIX: ppu.cvta.local
```

与 TIX 指令互操作的例子：`ppu.ld.shared.s32 r0, [ptr];` 期望 `ptr` 引用共享内存地址空间，需先通过 `__cvta_generic_to_shared` 转换：

```cpp
__shared__ int var;
var = 121;
size_t ptr = __cvta_generic_to_shared(&var);
int res;
asm volatile("ppu.ld.shared.s32 %0, [%1];"
             : "=r"(res)
             : "l"(ptr)
             : "memory");
assert(res == 121);
```

**常见优化——减小数据结构大小**：共享、局部和常量空间的地址范围小于 32 位，可存储 32 位地址而非 64 位指针以节省寄存器，且 32 位算术比 64 位更快：

```cpp
__shared__ int var;
uint32_t ptr32 = static_cast<uint32_t>(__cvta_generic_to_shared(&var));

// 恢复：零扩展回 64 位再调用转换函数
size_t ptr64 = static_cast<size_t>(ptr32); // zero-extend to 64 bits
void *ptrGeneric = __cvta_shared_to_generic(ptr64);
assert(ptrGeneric == &var);
```

> 比赛关联：寄存器压力直接影响占用率（每 CU 仅 64K VREG，见 §5.5）。把共享内存指针压成 32 位保存，是大 block kernel（如 attention/采样）省寄存器、提 occupancy 的实用手段；与 TIX 内联汇编混写时 `__cvta_*` 是必备转换。

#### 5.2.1.2.3 低级加载和存储函数

```cpp
T __ldg(const T *address);   // 只读 L1/Tex 缓存加载
T __ldcg(const T *address);
T __ldca(const T *address);
T __ldcs(const T *address);
T __ldlu(const T *address);
T __ldcv(const T *address);
void __stwb(T *address, T value);
void __stcg(T *address, T value);
void __stcs(T *address, T value);
void __stwt(T *address, T value);
```

- `__ldg()` 执行只读 L1/Tex 缓存加载；其余 `__ld*` 使用 TIX ISA 指南中指定的缓存操作符执行加载；`__st*` 使用缓存操作符执行存储。
- 支持所有 C++ 基本类型、HGGC 向量类型（3 元素除外）和扩展浮点类型：`__half`、`__half2`、`__ppu_bfloat16`、`__ppu_bfloat162`。

> 比赛关联：VLM 推理中只读且不复用的权重/激活流式访问（如 GEMM 的 B 矩阵、KV cache 读取）用 `__ldcs`（streaming）避免污染 L1；常量性输入用 `__ldg`；写回不重用输出用 `__stcs`/`__stwt` 可减少 cache 抖动，是吞吐调优的常用旋钮。

#### 5.2.1.2.4 `__trap()`

```cpp
void __trap();
```

可从任何设备线程启动陷阱操作。核函数执行被中止，并在主机程序中引发中断。调用 `__trap()` 会导致 **HGGC 上下文损坏**，后续 HGGC 调用和核函数调用失败。

#### 5.2.1.2.5 `__nanosleep()`

```cpp
__device__ void __nanosleep(unsigned ns);
```

暂停线程大约 `ns` 纳秒。最大睡眠持续时间约为 **1 毫秒**。

示例（指数退避互斥锁）：

```cpp
__device__ void mutex_lock(unsigned *mutex) {
    unsigned ns = 8;
    while (atomicCAS(mutex, 0, 1) == 1) {
        __nanosleep(ns);
        if (ns < 256) {
            ns *= 2;
        }
    }
}
__device__ void mutex_unlock(unsigned *mutex) { atomicExch(mutex, 0); }
```

#### 5.2.1.2.6 动态规划扩展 (DPX) 指令

DPX 函数集提供最多三个 16 位或 32 位有符号/无符号整数参数的查找最小值/最大值，以及融合加法和最小/最大运算，带可选 ReLU（限制到零）功能。

**比较函数**：

```cpp
// 三个参数。语义：max(a, b, c)，min(a, b, c)
int __vimax3_s32(int, int, int);
unsigned __vimax3_s16x2(unsigned, unsigned, unsigned);
unsigned __vimax3_u32(unsigned, unsigned, unsigned);
unsigned __vimax3_u16x2(unsigned, unsigned, unsigned);
int __vimin3_s32(int, int, int);
unsigned __vimin3_s16x2(unsigned, unsigned, unsigned);
unsigned __vimin3_u32(unsigned, unsigned, unsigned);
unsigned __vimin3_u16x2(unsigned, unsigned, unsigned);

// 两个参数，带 ReLU。语义：max(a, b, 0)，max(min(a, b), 0)
int __vimax_s32_relu(int, int);
unsigned __vimax_s16x2_relu(unsigned, unsigned);
int __vimin_s32_relu(int, int);
unsigned __vimin_s16x2_relu(unsigned, unsigned);

// 三个参数，带 ReLU。语义：max(a, b, c, 0)，max(min(a, b, c), 0)
int __vimax3_s32_relu(int, int, int);
unsigned __vimax3_s16x2_relu(unsigned, unsigned, unsigned);
int __vimin3_s32_relu(int, int, int);
unsigned __vimin3_s16x2_relu(unsigned, unsigned, unsigned);

// 两个参数，额外返回哪个参数较小/较大
int __vibmax_s32(int, int, bool *const pred);
unsigned __vibmax_u32(unsigned, unsigned, bool *const pred);
unsigned __vibmax_s16x2(unsigned, unsigned, bool *const pred_hi,
                        bool *const pred_lo);
unsigned __vibmax_u16x2(unsigned, unsigned, bool *const pred_hi,
                        bool *const pred_lo);
int __vibmin_s32(int, int, bool *const pred);
unsigned __vibmin_u32(unsigned, unsigned, bool *const pred);
unsigned __vibmin_s16x2(unsigned, unsigned, bool *const pred_hi,
                        bool *const pred_lo);
unsigned __vibmin_u16x2(unsigned, unsigned, bool *const pred_hi,
                        bool *const pred_lo);
```

**融合加法和最小/最大**：

```cpp
// 三个参数，将 (第一个+第二个) 与第三个比较。语义：max(a + b, c)，min(a + b, c)
int __viaddmax_s32(int, int, int);
unsigned __viaddmax_s16x2(unsigned, unsigned, unsigned);
unsigned __viaddmax_u32(unsigned, unsigned, unsigned);
unsigned __viaddmax_u16x2(unsigned, unsigned, unsigned);
int __viaddmin_s32(int, int, int);
unsigned __viaddmin_s16x2(unsigned, unsigned, unsigned);
unsigned __viaddmin_u32(unsigned, unsigned, unsigned);
unsigned __viaddmin_u16x2(unsigned, unsigned, unsigned);

// 三个参数，带 ReLU。语义：max(a + b, c, 0)，max(min(a + b, c), 0)
int __viaddmax_s32_relu(int, int, int);
unsigned __viaddmax_s16x2_relu(unsigned, unsigned, unsigned);
int __viaddmin_s32_relu(int, int, int);
unsigned __viaddmin_s16x2_relu(unsigned, unsigned, unsigned);
```

这些指令根据计算能力进行硬件加速或软件模拟（见算术指令部分）；完整 API 见 HGGC 数学 API 文档。DPX 对动态规划算法（Smith-Waterman、Needleman-Wunsch、Floyd-Warshall）非常有用。

示例：

```cpp
// 三个有符号 32 位整数的最大值，带 ReLU
int a = -1, b = 2, c = 3;
int res0 = __vimax3_s32_relu(a, b, c); // max(-1, 2, 3, 0) = 3
int d = -2, e = -3;
int res1 = __vimax3_s32_relu(a, d, e); // max(-1, -2, -3, 0) = 0

// 两个 32 位有符号整数之和、另一个 32 位有符号整数和零 (ReLU) 的最小值（原文为 viaddmax 示例）
int a = -5, b = 6, c = -2;
int res0 = __viaddmax_s32_relu(a, b, c); // max(-5 + 6, -2, 0) = 1
int d = 4;
int res1 = __viaddmax_s32_relu(a, d, c); // max(-5 + 4, -2, 0) = 0

// 两个无符号 32 位整数的最小值并确定哪个值较小
unsigned a = 9, b = 6;
bool smaller;
unsigned res = __vibmin_u32(a, b, &smaller); // res = 6, smaller = true

// 三对无符号 16 位整数的最大值
unsigned a = 0x00050002;
unsigned b = 0x00030004;
unsigned c = 0x00010006;
unsigned res = __vimax3_u16x2(a, b, c); // max(5, 3, 1) 和 max(2, 4, 6) 拼接得到 0x00050006
```

> 比赛关联：DPX 的融合 max/min+ReLU 对采样后处理（top-k/top-p 中的整数索引比较）、量化 clamp（`__vimax3_s32_relu` 一条指令替代多条）有加速价值；`s16x2` 变体还能半字并行。

### 5.2.1.3 编译器优化提示

内建函数在设备代码中始终可用；主机代码支持取决于主机编译器。

#### 5.2.1.3.1 `#pragma unroll`

编译器默认展开具有已知循环次数的小循环；`#pragma unroll` 可控制任意循环的展开，必须放在循环之前，仅适用于该循环。可选跟随一个整数常量表达式：

- 省略：若循环次数是常量，则完全展开。
- 计算为 0 或 1：不展开。
- 非正整数或大于 INT_MAX：忽略该 pragma 并报错。

```cpp
struct S { static constexpr int value = 4; };
inline constexpr int count = 4;
__device__ void foo(int *output, int *input) {
    // 未指定参数，循环将完全展开
    #pragma unroll
    for (int i = 0; i < 12; ++i)
        output[i] += input[i] * 2;
    // 展开值 = 5
    #pragma unroll(count + 1)
    for (int i = 0; i < 12; ++i)
        output[i] += input[i] * 4;
    // 展开值 = 1，循环展开禁用
    #pragma unroll 1
    for (int i = 0; i < 12; ++i)
        output[i] += input[i] * 8;
    // 展开值 = 4
    #pragma unroll(S::value)
    for (int i = 0; i < 12; ++i)
        output[i] += input[i] * 16;
    // 负值，报错
    // #pragma unroll - 1
    for (int i = 0; i < 12; ++i)
        output[i] += input[i] * 2;
}
```

#### 5.2.1.3.2 `__builtin_assume_aligned()`

```cpp
void *__builtin_assume_aligned(const void *ptr, size_t align);
void *__builtin_assume_aligned(const void *ptr, size_t align,
                               <integral type> offset);
```

使编译器假设返回的指针至少 `align` 字节对齐；三参数版本假设 `(char*) ptr - offset` 至少 `align` 字节对齐。`align` 必须是 2 的幂且为整数字面量。

```cpp
// 编译器可以假设'res1'至少是32字节对齐的
void *res1 = __builtin_assume_aligned(ptr, 32);
// 编译器可以假设'res2 = (char*) ptr - 8'至少是32字节对齐的
void *res2 = __builtin_assume_aligned(ptr, 32, 8);
```

#### 5.2.1.3.3 `__builtin_assume()`

```cpp
void __builtin_assume(bool predicate);
```

使编译器假设布尔参数为真。运行时为假则行为未定义；参数有副作用则行为不确定。

```cpp
__device__ bool is_greater_than_zero(int input) { return input > 0; }
__device__ bool f(int input) {
    __builtin_assume(input > 0);
    return is_greater_than_zero(input); // 返回true，而不评估条件
}
```

#### 5.2.1.3.4 `__builtin_expect()`

```cpp
long __builtin_expect(long input, long expected);
```

告诉编译器 `input` 预期等于 `expected` 并返回 `input` 的值，用于分支预测，行为类似 C++20 的 `[[likely]]`/`[[unlikely]]`。

```cpp
// 向编译器指示可能"var == 0"
if (__builtin_expect(var, 0))
// ...
```

#### 5.2.1.3.5 `__builtin_unreachable()`

```cpp
void __builtin_unreachable(void);
```

告诉编译器控制流永远不会到达该位置；运行到达则未定义行为。用于避免不可达分支的代码生成及禁用相关警告。

```cpp
// 向编译器指示默认情况标签不可能到达。
switch (in) {
case 1:
    return 2;
case 2:
    return 3;
default:
    __builtin_unreachable();
}
```

#### 5.2.1.3.6 `__builtin_ppu_assume_uniform()`

```cpp
void __builtin_ppu_assume_uniform(T val);
```

使编译器假设**所有线程到该处时 `val` 的值相同**；不同则行为未定义。

```cpp
__global__ void kernel(int *a) {
    int i = threadIdx.x;
    int val = a[i];
    __builtin_ppu_assume_uniform(val); // a数组中所有访问到的元素相同。
}
```

#### 5.2.1.3.7 `__builtin_ppu_to_uniform_b32()`

```cpp
int __builtin_ppu_to_uniform_b32(T val);
```

假设所有线程的 `val` 相同，并返回该值转换成的 `int`；不同则行为未定义。

```cpp
__global__ void kernel(int *a) {
    int i = threadIdx.x;
    int val = a[i];
    val = __builtin_ppu_to_uniform_b32(val); // a数组中所有访问到的元素相同。
}
```

#### 5.2.1.3.8 `__builtin_ppu_to_uniform_b64()`

```cpp
long int __builtin_ppu_to_uniform_b64(T val);
```

同上，返回转换成的 `long int`。

```cpp
__global__ void kernel(long int *a) {
    int i = threadIdx.x;
    long int val = a[i];
    val = __builtin_ppu_to_uniform_b64(val); // a数组中所有访问到的元素相同。
}
```

> 比赛关联：PPU 有 uniform（标量）通路概念。kernel 里由 blockIdx 或广播得到的"全 warp 一致"值（序列长度、stride、scale 指针）用 `__builtin_ppu_assume_uniform`/`__builtin_ppu_to_uniform_b32` 标注后可走标量寄存器与标量运算，显著降 VREG 压力——这是 PPU 特有的优化点，值得在自研 kernel 中利用。

## 5.2.2 函数和变量注解

### 5.2.2.1 执行空间说明符

`__host__`、`__device__`、`__global__` 指示函数在主机还是设备上执行：

| 执行空间说明符 | 在主机上执行 | 在设备上执行 | 从主机上调用 | 从设备上调用 | 附加约束 |
|---|:---:|:---:|:---:|:---:|---|
| `__host__`（或无说明符） | ✅ | ❌ | ✅ | ❌ | — |
| `__device__` | ❌ | ✅ | ❌ | ✅ | — |
| `__global__` | ❌ | ✅ | ✅ | ✅ | 返回类型须为 void；须为自由函数；调用时须提供执行配置（见核函数配置）；异步执行；不支持递归；参数有额外限制（见 global 函数参数） |
| `__host__ __device__` | ✅ | ✅ | ✅ | ✅ | 分别为主机和设备编译 |

`__host__ __device__` 函数为主机和设备分别编译，可用 `__HGGC_ARCH__` 区分代码路径：

```cpp
__host__ __device__ void f() {
#if defined(__HGGC_ARCH__)
    // 设备代码路径
#else
    // 主机代码路径
#endif
}
```

### 5.2.2.2 内存空间说明符

`__device__`、`__managed__`、`__constant__`、`__shared__` 指示设备上变量的存储位置：

| 内存空间说明符 | 位置 | 可使用处 | 生命周期 | 唯一实例 |
|---|---|---|---|---|
| `__device__` | 设备全局内存 | 设备线程 / HGGC 运行时 API | 程序 | 每个设备 |
| `__constant__` | 设备常量内存 | 设备线程 / HGGC 运行时 API | 程序 | 每个设备 |
| `__managed__` | 主机和设备（自动） | 主机/设备线程 | 程序 | 每个程序 |
| `__shared__` | 设备（流式多处理器） | 块线程 | 块 | 块 |
| 无说明符 | 设备（寄存器） | 单个线程 | 单个线程 | 单个线程 |

主机代码无法直接解引用 `__device__` 或 `__constant__` 变量的地址，HGGC 运行时提供符号操作 API：

| API | 功能 |
|---|---|
| `hggcGetSymbolAddress()` | 获取设备符号的设备端地址 |
| `hggcGetSymbolSize()` | 查询设备符号占用的字节数 |
| `hggcMemcpyToSymbol()` | 从主机向设备符号写入数据 |
| `hggcMemcpyFromSymbol()` | 从设备符号向主机读取数据 |

`__constant__` 变量在设备代码中仅可读取，写入只能通过上述主机端 API 完成。

```cpp
__device__ float d = 1.0f;   // 设备内存中的变量
__constant__ float c = 1.0f; // 常量内存中的变量
int main() {
    float *ptr;
    hggcGetSymbolAddress((void **)&ptr, d); // 获取d的地址
    size_t size;
    hggcGetSymbolSize(&size, d);            // 检索符号的大小（4字节）。
    float h;
    hggcMemcpyFromSymbol(&h, d, sizeof(h)); // 从设备复制到主机。
    h = 3.0f;
    hggcMemcpyToSymbol(d, &h, sizeof(h));   // 从主机复制到设备。
}
```

#### 5.2.2.2.1 `__shared__` 内存

`__shared__` 变量可有静态大小（编译时确定）或动态大小（核函数启动时确定，见核函数配置）。约束：

- 动态大小的变量必须声明为外部数组或指针。
- 静态大小的变量不能在其声明中初始化。

```cpp
extern __shared__ char ptr[];
// extern __shared__ char* ptr; 替代语法
__global__ void kernel() {      // 或 __device__ 函数
    __shared__ int var1[3];     // 静态大小
    auto var2 = (int *)ptr;     // 动态大小
}
int main() {
    size_t size = 16;
    kernel<<<1, 1, size>>>();
    hggcDeviceSynchronize();
}
```

#### 5.2.2.2.2 `__managed__` 内存

限制：

- `__managed__` 变量的地址不是常量表达式。
- `__managed__` 变量不应具有引用类型 `T&`。
- HGGC 运行时可能处于无效状态时，不得使用 `__managed__` 变量的地址或值，包括：
  - 具有 static 或 thread_local 存储持续时间的对象的静态/动态初始化或销毁期间；
  - 调用 `exit()` 后执行的代码（如 `__attribute__((destructor))` 函数）；
  - HGGC 运行时尚未初始化时执行的代码（如 `__attribute__((constructor))` 函数）。
- 一致性行为与动态分配的 managed 内存相同。
- 另参见局部变量限制。

```cpp
#include <cassert>
__device__ __managed__ int var = 1; // OK
int *ptr = &var;                    // 错误：在静态初始化中使用托管变量
struct S1 {
    int field;
    S1() : field(var){};
};
struct S2 { ~S2() { var = 1; } };
S1 s1; // 错误：在动态初始化中使用托管变量
S2 s2; // 错误：在具有静态存储持续时间的对象的析构函数中使用托管变量
__device__ __managed__ const int c = 1; // 错误：const限定类型
__device__ __managed__ int &ref = var;  // 错误：引用类型
template <int *Addr> struct S3 {};
S3<&var> s; // 错误：托管变量的地址不是常量表达式
__global__ void kernel(int *ptr) {
    assert(ptr == &var); // OK
    var = 20;            // OK
}
int main() {
    int *ptr = &var; // OK
    kernel<<<1, 1>>>(ptr);
    hggcDeviceSynchronize();
    var++; // OK
}
```

### 5.2.2.3 内联说明符

- `__noinline__`：指示 hgcc 不要内联该函数。
- `__forceinline__`：强制 hgcc 在单个翻译单元内内联该函数。
- `__inline_hint__`：在使用链接时优化（LTO）时启用跨翻译单元的激进内联。

三者互斥。

### 5.2.2.4 `__restrict__` 指针

hgcc 通过 `__restrict__` 支持受限指针。指针别名（两个或多个指针指向重叠内存区域）会阻碍代码重排和公共子表达式消除。受限指针是程序员的承诺：指针生命周期内，其所指内存只通过该指针访问。满足以下条件之一时编译器可执行更激进优化：

- 所有访问设备函数的线程都只从该指针读取数据；
- 或至多一个线程写入它，且没有其他线程从中读取。

别名问题示例——`a`、`b`、`c` 可能别名，任何通过 `c` 的写入都可能修改 `a`/`b`：`a[0] + b[1]` 在 `c[0]`、`c[1]`、`c[4]` 三处重复计算却无法缓存复用，也无法重排：

```cpp
__device__ void deviceFunction(const int *a, const int *b, int *c) {
    c[0] = a[0] + b[1];
    c[1] = a[0] + b[1] + a[2];
    c[2] = a[1] * a[2];
    c[3] = b[1] - a[1];
    c[4] = a[0] + b[1] + a[1];
    // ...
}
```

改为受限指针（**所有指针参数都必须受限，优化器才能生效**）：

```cpp
__device__ void deviceFunction(const int *__restrict__ a,
                               const int *__restrict__ b,
                               int *__restrict__ c);
```

编译器即可自由重排并做公共子表达式消除：

```cpp
__device__ void deviceFunction(const int *__restrict__ a,
                               const int *__restrict__ b,
                               int *__restrict__ c) {
    int t0 = a[0];
    int t1 = b[1];
    int t2 = a[1];
    int t3 = a[2];
    int t4 = t0 + t1;
    c[0] = t4;
    c[1] = t4 + t3;
    c[2] = t2 * t3;
    c[3] = t1 - t2;
    c[4] = t4 + t2;
    // ...
}
```

结果：减少内存访问和计算次数，平衡缓存加载与寄存器压力。**注意**：寄存器压力是许多 HGGC 代码的关键问题，受限指针可能因降低占用率而对性能产生负面影响。

`__global__` 函数 `const` 指针中标记 `__restrict__` 的访问被编译为**只读缓存加载**（类似 TIX `ppu.ld.global.nc` 或 `__ldg()`）：

```cpp
__global__ void kernel1(const int *in, int *out) {
    *out = *in; // TIX: ppu.ld.global
}
__global__ void kernel2(const int *__restrict__ in, int *out) {
    *out = *in; // TIX: ppu.ld.global.nc
}
```

> 比赛关联：对自定义推理 kernel（RMSNorm、RoPE、反量化逐元素操作）的全部指针参数加 `const __restrict__` 是零成本优化：既消除重复加载，又走只读缓存路径。

### 5.2.2.5 `__grid_constant__` 参数

`__grid_constant__` 注解 `__global__` 函数参数可防止编译器创建参数的每线程副本，网格中所有线程通过单个地址访问参数，可提高性能。属性：

- 具有核函数的生命周期。
- 单个核函数私有——对象不可被来自其他网格（包括子网格）的线程访问。
- 核函数中所有线程看到相同的地址。
- 只读。修改 `__grid_constant__` 对象或其任何子对象（包括 mutable 成员）都是未定义行为。

要求：

- 参数必须是具有 `const` 限定的非引用类型。
- 同一函数的所有声明必须对 `__grid_constant__` 参数保持一致。
- 函数模板特化与实例化必须与主模板声明保持一致。

```cpp
struct S {
    int x;
    mutable int y;
};
__device__ void externalFunction(const S &) {}
__global__ void kernel(const __grid_constant__ S s) {
    s.x++; // 编译错误：试图修改只读内存
    // 编译器将不会创建"s"的每个线程本地副本：
    externalFunction(s);
}
```

> 比赛关联：kernel 的只读配置结构体（量化参数表、LoRA 描述符、采样参数）用 `__grid_constant__` 传递可避免每线程拷贝到本地内存，省寄存器。

### 5.2.2.6 注解摘要

| 注解 | `__host__` | `__device__` | `__host__ __device__` | `__global__` |
|---|---|---|---|---|
| `__noinline__`, `__forceinline__`, `__inline_hint__` | 函数 | 函数 | 函数 | ❌ |
| `__restrict__` | 指针参数 | 指针参数 | 指针参数 | 指针参数 |
| `__grid_constant__` | ❌ | ❌ | ❌ | 参数 |
| `__launch_bounds__` | ❌ | ❌ | ❌ | 函数 |
| `__maxnreg__` | ❌ | ❌ | ❌ | 函数 |

（注：原表中 `__noinline__/__forceinline__/__inline_hint__` 行只标出 `__global__` 列为 ❌，其余为"函数"；`__restrict__` 各列均为"指针参数"。）

## 5.2.3 内置类型和变量

### 5.2.3.1 主机编译器类型扩展

只要主机编译器支持，HGGC 允许使用非标准算术类型：

- 128 位整数类型 `__int128`：当主机编译器定义了 `__SIZEOF_INT128__` 宏时支持。
- `_Complex` 类型：仅在主机代码中支持。

### 5.2.3.2 内置变量

网格/块维度值为 `dim3` 类型；块/线程索引变量为 `uint3` 类型。`dim3` 和 `uint3` 都是由 `x`、`y`、`z` 三个无符号值组成的简单结构；C++11 及以后 `dim3` 所有元素默认值为 1。

仅限设备的内置变量：

- `dim3 gridDim`：网格的尺寸，即沿 x、y、z 维度的线程块数量。
- `dim3 blockDim`：线程块的尺寸，即沿 x、y、z 维度的线程数量。
- `uint3 blockIdx`：网格内的块索引。
- `uint3 threadIdx`：块内的线程索引。
- `int warpSize`：运行时定义的值，线程束中的线程数，通常为 **32**。

### 5.2.3.3 内置类型（向量类型）

由基本整数和浮点类型派生的向量类型，主机和设备均支持：

| C++ 基本类型 | X1 | X2 | X3 | X4 |
|---|---|---|---|---|
| `signed char` | `char1` | `char2` | `char3` | `char4` |
| `unsigned char` | `uchar1` | `uchar2` | `uchar3` | `uchar4` |
| `signed short` | `short1` | `short2` | `short3` | `short4` |
| `unsigned short` | `ushort1` | `ushort2` | `ushort3` | `ushort4` |
| `signed int` | `int1` | `int2` | `int3` | `int4` |
| `unsigned` | `uint1` | `uint2` | `uint3` | `uint4` |
| `signed long` | `long1` | `long2` | `long3` | `long4`/`long4_16a`/`long4_32a` |
| `unsigned long` | `ulong1` | `ulong2` | `ulong3` | `ulong4`/`ulong4_16a`/`ulong4_32a` |
| `signed long long` | `longlong1` | `longlong2` | `longlong3` | `longlong4`/`longlong4_16a`/`longlong4_32a` |
| `unsigned long long` | `ulonglong1` | `ulonglong2` | `ulonglong3` | `ulonglong4`/`ulonglong4_16a`/`ulonglong4_32a` |
| `float` | `float1` | `float2` | `float3` | `float4` |
| `double` | `double1` | `double2` | `double3` | `double4`/`double4_16a`/`double4_32a` |

向量类型的字节大小和对齐要求：

| 类型 | 大小 | 对齐 |
|---|---:|---:|
| `char1`, `uchar1` | 1 | 1 |
| `char2`, `uchar2` | 2 | 2 |
| `char3`, `uchar3` | 3 | 1 |
| `char4`, `uchar4` | 4 | 4 |
| `short1`, `ushort1` | 2 | 2 |
| `short2`, `ushort2` | 4 | 4 |
| `short3`, `ushort3` | 6 | 2 |
| `short4`, `ushort4` | 8 | 8 |
| `int1`, `uint1` | 4 | 4 |
| `int2`, `uint2` | 8 | 8 |
| `int3`, `uint3` | 12 | 4 |
| `int4`, `uint4` | 16 | 16 |
| `long1`, `ulong1` | 8 | 8 |
| `long2`, `ulong2` | 16 | 16 |
| `long3`, `ulong3` | 24 | 8 |
| `long4`, `ulong4` | 32 | 16 |
| `long4_16a`, `ulong4_16a` | 32 | 16 |
| `long4_32a`, `ulong4_32a` | 32 | 32 |
| `longlong1`, `ulonglong1` | 8 | 8 |
| `longlong2`, `ulonglong2` | 16 | 16 |
| `longlong3`, `ulonglong3` | 24 | 8 |
| `longlong4`, `ulonglong4` | 32 | 16 |
| `longlong4_16a`, `ulonglong4_16a` | 32 | 16 |
| `longlong4_32a`, `ulonglong4_32a` | 32 | 32 |
| `float1` | 4 | 4 |
| `float2` | 8 | 8 |
| `float3` | 12 | 4 |
| `float4` | 16 | 16 |
| `double1` | 8 | 8 |
| `double2` | 16 | 16 |
| `double3` | 24 | 8 |
| `double4` | 32 | 16 |
| `double4_16a` | 32 | 16 |
| `double4_32a` | 32 | 32 |

向量类型是结构体，组件通过 `x`、`y`、`z`、`w` 字段访问：

```cpp
int sum(int4 var) { return var.x + var.y + var.z + var.w; }
```

都有 `make_<type_name>()` 形式的工厂函数：

```cpp
int4 inc(int4 var) {
    return make_int4(var.x + 1, var.y + 1, var.z + 1, var.w + 1);
}
```

若主机代码不是用 hgcc 编译的，可包含 SAIL 工具包提供的 `hggc_runtime.h` 头文件导入向量类型和相关函数。

> 比赛关联：`float4`/`int4`（16 字节）加载是 GEMM/elementwise kernel 向量化访存的基线；`*_32a` 类型提供 32 字节对齐变体，可匹配更宽的向量化 load/store。注意 `int3`/`float3` 对齐仅 4 字节且不被 `__ldg` 等低级函数支持，尽量用 4 元素类型。

## 5.2.4 核函数配置

任何对 `__global__` 函数的调用都必须指定执行配置：

```
<<<grid_dim, block_dim, dynamic_smem_bytes, stream>>>
```

- `grid_dim`：`dim3` 类型，网格的维度和大小，`grid_dim.x * grid_dim.y * grid_dim.z` 等于启动的块数。
- `block_dim`：`dim3` 类型，每块的维度和大小，`block_dim.x * block_dim.y * block_dim.z` 等于每块线程数。
- `dynamic_smem_bytes`：可选 `size_t` 参数，默认为零。指定此次调用除静态分配外每块动态分配的共享内存字节数，供 `extern __shared__` 数组使用。
- `stream`：`hggcStream_t`（指针）类型，指定关联流，可选，默认 `NULL`。

```cpp
__global__ void kernel(float *parame) {}
int main() {
    kernel<<<1, 1, 32>>>(nullptr);
    hggcDeviceSynchronize();
}
```

执行配置的参数在实际函数参数之前求值。若 `grid_dim`/`block_dim` 超过设备允许的最大尺寸（见计算能力部分），或 `dynamic_smem_bytes` 大于静态分配后可用共享内存，函数调用失败。

### 5.2.4.1 启动界限 `__launch_bounds__`

较少寄存器 → 更多线程/块驻留多处理器 → 提高性能。编译器默认用启发式最小化寄存器使用，应用可通过 `__launch_bounds__()` 提供附加信息：

```cpp
__global__ void __launch_bounds__(maxThreadsPerBlock,
                                  minBlocksPerMultiprocessor) kernel() {
    // ...
}
```

- `maxThreadsPerBlock`：启动 kernel() 时使用的每块最大线程数；编译为 `.maxntid` TIX 指令。
- `minBlocksPerMultiprocessor`：可选，所需的每个多处理器上的最少常驻块数；编译为 `.minnctapersm` TIX 指令。

指定启动界限后，编译器推导寄存器数量上限 `L`，确保 `minBlocksPerMultiprocessor` 块（未指定则为单块）的 `maxThreadsPerBlock` 线程可驻留多处理器，然后：

- 初始寄存器用量超过 `L`：减少到 ≤ L（通常导致局部内存增加和/或指令数增加）。
- 初始用量低于 `L`：
  - 只指定 `maxThreadsPerBlock`：编译器用它确定 n 和 n+1 常驻块之间转换的寄存器阈值（少用 1 个寄存器能多容纳 1 个常驻块时），然后应用常规启发式。
  - 同时指定两者：可能增加寄存器用量至 `L`，以减少指令数并更好隐藏单线程指令延迟。

以下情况核函数启动失败：每块线程数超过 `maxThreadsPerBlock`。

**前向兼容建议**：开发人员应包含单参数 `__launch_bounds__(maxThreadsPerBlock)` 指定核函数将启动的最大块大小，否则可能出现"请求的资源太多"错误。两参数版本在某些情况下可提高性能，最佳 `minBlocksPerMultiprocessor` 值应通过详细分析确定。

最佳启动界限通常因主要架构修订而异，用 `__HGGC_ARCH__` 管理：

```cpp
#if __HGGC_ARCH__ >= 100
#define MY_KERNEL_MAX_THREADS 512
#define MY_KERNEL_MIN_BLOCKS 3
#else
#define MY_KERNEL_MAX_THREADS 256
#define MY_KERNEL_MIN_BLOCKS 2
#endif
__global__ void __launch_bounds__(MY_KERNEL_MAX_THREADS, MY_KERNEL_MIN_BLOCKS)
kernel() {
    // ...
}
```

**陷阱**：主机代码中 `__HGGC_ARCH__` 未定义，下面写法会以每块 256 线程启动（走错分支）：

```cpp
// 主机代码 —— 行不通
kernel<<<blocksPerGrid, MY_KERNEL_MAX_THREADS>>>();
```

应改为：

```cpp
// 方式一：编译期使用不依赖 __HGGC_ARCH__ 的宏
kernel<<<blocksPerGrid, THREADS_PER_BLOCK>>>();

// 方式二：运行时根据计算能力确定
hggcGetDeviceProperties(&deviceProp, device);
int threadsPerBlock =
    (deviceProp.major > 8) ? 2 * THREADS_PER_BLOCK : THREADS_PER_BLOCK;
kernel<<<blocksPerGrid, threadsPerBlock>>>();
```

`--resource-usage` 编译器选项报告寄存器使用情况。

### 5.2.4.2 每线程最大寄存器数 `__maxnreg__`

```cpp
__global__ void __maxnreg__(maxNumberRegistersPerThread) kernel() {
    // ...
}
```

`maxNumberRegistersPerThread` 指定块中单线程可分配的最大寄存器数；编译为 `.maxnreg` TIX 指令。

- **不能将 `__launch_bounds__()` 和 `__maxnreg__()` 应用于同一个核函数。**
- `--maxrregcount <N>` 编译器选项可控制文件中所有 `__global__` 函数的寄存器使用；对带 `__maxnreg__` 的核函数忽略此选项。

> 比赛关联：占用率调优三件套——`--resource-usage` 看寄存器用量 → `__launch_bounds__`/`__maxnreg__` 压寄存器 → 提升每 CU 常驻 warp（ppu001 每 CU 2048 线程上限，见 §5.5）。对延迟敏感的 decode kernel 尤其有效。

## 5.2.5 同步与原子操作

### 5.2.5.1 线程块同步函数

```cpp
void __syncthreads();
int __syncthreads_count(int predicate);
int __syncthreads_and(int predicate);
int __syncthreads_or(int predicate);
```

同一线程块中多线程并行读写共享/全局内存，无显式同步点会导致数据竞争。`__syncthreads*()` 提供块内屏障：

- **屏障等待**：调用后当前线程等待，直到块内所有活跃线程到达同一调用点（已退出的线程不参与）。
- **内存排序保证**：屏障同时充当隐式内存栅栏——屏障前的内存写入对屏障后的所有参与线程可见，符合 C++ [intro.races] 的 happens-before 语义。

```cpp
// 假设 blockDim.x 是 128
__global__ void kernel(int *input, int *output) {
    __shared__ int data[128];
    data[threadIdx.x] = input[threadIdx.x];
    // 所有线程同步，保证 'data' 的所有写入操作有序
    __syncthreads();
    if (threadIdx.x == 0) {
        int sum = 0;
        for (int i = 0; i < blockDim.x; ++i) {
            sum += data[i];
        }
        output[blockIdx.x] = sum;
    }
}
```

条件分支中的 `__syncthreads*()` 合法的前提是**块内所有活跃线程对分支条件求值一致（uniform condition）**，否则死锁或未定义行为：

```cpp
// 正确：整个块线程的统一条件
if (blockIdx.x > 0) {
    __syncthreads();
    output[threadIdx.x] = data[128 - threadIdx.x];
}
```

```cpp
// 错误：非统一条件（threadIdx.x 因线程而异）——未定义行为
if (threadIdx.x > 0) {
    __syncthreads();
    ...
}
// 错误：循环内非统一条件
for (int i = 0; i < blockDim.x; ++i) {
    if (i == threadIdx.x) {
        __syncthreads(); // 未定义行为
    }
}
```

带谓词变体：

- `__syncthreads_count(predicate)`：返回块内所有未退出线程中谓词非零的线程数。
- `__syncthreads_and(predicate)`：当且仅当谓词对所有未退出线程非零时返回非零。
- `__syncthreads_or(predicate)`：当且仅当谓词对一个或多个未退出线程非零时返回非零。

### 5.2.5.2 线程束同步函数

```cpp
void __syncwarp(unsigned mask = 0xFFFFFFFF);
```

协调同一线程束内线程间通信，避免 warp 内访问相同地址时的读后写/写后读/写后写风险。`__syncwarp(mask)` 为 mask 选中的线程提供内存排序。受 Warp `__sync` 内建约束（5.2.6.6）限制。

```cpp
__global__ void kernel(int *input, int *output) {
    if (threadIdx.x < warpSize) {
        __shared__ int data[warpSize];
        data[threadIdx.x] = input[threadIdx.x];
        __syncwarp(); // 等价于 __syncwarp(0xFFFFFFFF)
        if (threadIdx.x == 0)
            output[0] = data[1];
    }
}
```

### 5.2.5.3 内存栅栏函数

HGGC 内存一致性模型基于**弱内存序（relaxed memory ordering）**：

1. **操作重排自由度**：编译器和硬件可自由重排同一线程中无数据依赖的内存操作。
2. **跨线程可见性不确定性**：线程 T# 的写入序列被另一线程观察到的顺序可能与程序顺序不同。

多线程无同步保护地并发访问同一地址行为未定义。内存栅栏在指定范围内建立顺序一致性约束，禁止栅栏前后内存操作重排，对所有内存空间（共享、全局、页锁定主机内存）统一生效。

> NOTE：出于安全性和可移植性，建议尽可能使用 libhg++ 提供的 `hggc::atomic_thread_fence`。

| 作用域 | C++ API（`<hggc/atomic>`） | 内建函数 | 排序可见范围 |
|---|---|---|---|
| 块级 | `hggc::atomic_thread_fence(hggc::memory_order_seq_cst, hggc::thread_scope_block)` | `__threadfence_block()` | 同一线程块内的所有线程 |
| 设备级 | `hggc::atomic_thread_fence(hggc::memory_order_seq_cst, hggc::thread_scope_device)` | `__threadfence()` | 同一设备上所有线程块中的线程 |
| 系统级 | `hggc::atomic_thread_fence(hggc::memory_order_seq_cst, hggc::thread_scope_system)` | `__threadfence_system()` | 设备线程 + 主机线程 + 对等设备线程 |

语义：作用域内所有观察者看来，栅栏前发出的内存操作不会与栅栏后的操作重排；区别仅在观察者范围。**应选择刚好覆盖通信线程的最小作用域。**

**栅栏效果：发布-订阅真值表**——线程 P 先写数据 `D=新值` 再设旗标 `F=1`；线程 S 先读 `F` 再读 `D`：

```cpp
#include <hggc/atomic>
__device__ int F = 0;
__device__ float D = 0.0f;
__device__ void publisher() { // 线程 P
    D = 3.14f;
    hggc::atomic_thread_fence(hggc::memory_order_seq_cst,
                              hggc::thread_scope_device);
    F = 1;
}
__device__ void subscriber() { // 线程 S
    int flag = F;
    hggc::atomic_thread_fence(hggc::memory_order_seq_cst,
                              hggc::thread_scope_device);
    float data = D;
}
```

（等价内建写法：将 `hggc::atomic_thread_fence(...)` 替换为 `__threadfence()`。）

| S 读到的 flag | S 读到的 data | 无栅栏 | 两侧均插入栅栏 | 含义 |
|---|---|:---:|:---:|---|
| 0 | 0.0 | ✓ | ✓ | S 在 P 开始发布前观察——正常 |
| 1 | 3.14 | ✓ | ✓ | S 在 P 完整发布后观察——正常 |
| 0 | 3.14 | ✓ | ✓ | 时序交错：S 先观察到 D 的更新但 F 尚未可见 |
| 1 | 0.0 | ✓ | ✗ | 违反因果序：S 看到"已就绪"旗标却读到过期数据 |

发布者侧栅栏保证 D 写在 F 写之前提交；订阅者侧栅栏保证 flag 读在 data 读之前完成，两者配合消除"旗标可见、数据不可见"。

> **排序 ≠ 可见性**：内存栅栏只影响内存操作执行的顺序，不保证对其他线程的可见性。如需确保可见性，可将目标变量声明为 `volatile`（见 volatile 限定变量）。

**实践示例：Cooperative Groups 分级树形归约**（每轮活跃块数减半，经 log₂(gridDim.x) 轮收敛；需用 Cooperative Launch API `hgLaunchCooperativeKernel` 启动以保证所有块同时驻留，这是 `grid.sync()` 正确执行的前提）：

```cpp
#include <hggc/atomic>
#include <cooperative_groups.h>
namespace cg = cooperative_groups;
__device__ float blockPartialSum(const float *input, int N) {
    extern __shared__ float smem[];
    int tid = threadIdx.x;
    int base = blockIdx.x * blockDim.x;
    float acc = 0.0f;
    for (int i = base + tid; i < N; i += gridDim.x * blockDim.x)
        acc += input[i];
    smem[tid] = acc;
    __syncthreads();
    for (int s = blockDim.x / 2; s > 0; s >>= 1) {
        if (tid < s) smem[tid] += smem[tid + s];
        __syncthreads();
    }
    return smem[0];
}
__global__ void gridTreeReduce(const float *input, int N,
                               float *workspace, float *output) {
    cg::grid_group grid = cg::this_grid();
    // 阶段 1：每个块独立计算部分和
    float ps = blockPartialSum(input, N);
    if (threadIdx.x == 0)
        workspace[blockIdx.x] = ps;
    // 阶段 2：跨块树形归约，每轮步长翻倍
    for (unsigned stride = 1; stride < gridDim.x; stride <<= 1) {
        hggc::atomic_thread_fence(hggc::memory_order_seq_cst,
                                  hggc::thread_scope_device);
        grid.sync();
        unsigned span = stride << 1;
        if (blockIdx.x % span == 0 && blockIdx.x + stride < gridDim.x) {
            if (threadIdx.x == 0)
                workspace[blockIdx.x] += workspace[blockIdx.x + stride];
        }
    }
    // 最终同步确保 workspace[0] 包含全局和
    hggc::atomic_thread_fence(hggc::memory_order_seq_cst,
                              hggc::thread_scope_device);
    grid.sync();
    if (blockIdx.x == 0 && threadIdx.x == 0)
        *output = workspace[0];
}
```

> 比赛关联：grid 级归约是单 kernel 完成全局 reduce（如整网 activation 统计、采样归一化）的范式，可避免多次 kernel launch（TTFT 收益）。栅栏作用域选错是隐蔽正确性 bug 的高发区：跨块通信必须 `thread_scope_device`，跨主机/设备才用 `thread_scope_system`。

### 5.2.5.4 原子函数

原子函数对共享数据执行读-修改-写操作，使其看起来像单步完成。HGGC 提供四种方式：

1. **扩展 HGGC C++ 原子函数**：`hggc::atomic` 和 `hggc::atomic_ref`。主机/设备均可用；遵循 C++ 标准原子操作语义；允许指定线程作用域。
2. **标准 C++ 原子函数**：`hggc::std::atomic` 和 `hggc::std::atomic_ref`。主机/设备均可用；遵循 C++ 标准语义；**不允许**指定线程作用域。
3. **编译器内置原子函数**：`__hg_atomic_<op>()`。仅设备代码；遵循 C++ 标准原子内存序语义；允许指定线程作用域；支持 `hggc::std::atomic`/`atomic_ref` 所允许数据类型的子集，128 位除外。
4. **传统原子函数**：`atomic<Op>()`。仅设备代码；仅支持 `memory_order_relaxed` 语义；可在函数名后缀中指定作用域；只保证原子性而**不引入同步点（栅栏）**；支持内置原子函数所允许类型的子集，原子 add 支持额外类型。

> NOTE：出于效率、安全性和可移植性，建议使用扩展 HGGC C++ 原子函数。

#### 5.2.5.4.1 传统原子函数

在全局或共享内存中的 32、64 或 128 位字上执行原子读-修改-写。要点：

- 只能在设备函数中使用。
- 向量类型（`__half2`、`__ppu_bfloat162`、`float2`、`float4` 等）：在向量的每个元素上分别执行读-修改-写，**不能保证整个向量作为单次访问是原子的**。
- 内存排序为 `hggc::std::memory_order_relaxed`，作用域由后缀决定：
  - 无后缀（如 `atomicAdd`）：`hggc::thread_scope_device`；
  - `_block` 后缀（如 `atomicAdd_block`）：`hggc::thread_scope_block`；
  - `_system` 后缀（如 `atomicAdd_system`）：满足特定条件时 `hggc::thread_scope_system`。

示例（CPU 和 PPU 原子地更新同一整数）：

```cpp
#include <hggc_runtime.h>
__global__ void kernel(int *addr) { atomicAdd_system(addr, 10); }
void f(int deviceID) {
    int *addr;
    hggcMallocManaged(&addr, 4);
    *addr = 0;
    hggcDeviceProp deviceProp;
    hggcGetDeviceProperties(&deviceProp, deviceID);
    if (deviceProp.concurrentManagedAccess != 1) {
        return; // 设备无法与CPU同时连贯地访问托管内存
    }
    kernel<<<1, 1>>>(addr);
    __sync_fetch_and_add(addr, 10); // CPU 原子操作
}
```

任何原子操作都可以基于 `atomicCAS()`（比较并交换）实现。

**传统原子函数清单**（均读取 address 处 old 值、计算、存回、返回 old）：

| 函数 | 原型 | 操作 | 支持类型 |
|---|---|---|---|
| `atomicAdd` | `T atomicAdd(T *address, T val)` | `old + val` | `int`, `unsigned`, `unsigned long long`, `float`, `double`, `__half2`, `__half`, `__ppu_bfloat16`, `__ppu_bfloat162` |
| `atomicSub` | `T atomicSub(T *address, T val)` | `old - val` | `int`, `unsigned` |
| `atomicInc` | `unsigned atomicInc(unsigned *address, unsigned val)` | `old >= val ? 0 : (old + 1)` | `unsigned` |
| `atomicDec` | `unsigned atomicDec(unsigned *address, unsigned val)` | `(old == 0 \|\| old > val) ? val : (old - 1)` | `unsigned` |
| `atomicAnd` | `T atomicAnd(T *address, T val)` | `old & val` | `int`, `unsigned`, `unsigned long long` |
| `atomicOr` | `T atomicOr(T *address, T val)` | `old \| val` | `int`, `unsigned`, `unsigned long long` |
| `atomicXor` | `T atomicXor(T *address, T val)` | `old ^ val` | `int`, `unsigned`, `unsigned long long` |
| `atomicMin` | `T atomicMin(T *address, T val)` | `min(old, val)` | `int`, `unsigned`, `unsigned long long`, `long long` |
| `atomicMax` | `T atomicMax(T *address, T val)` | `max(old, val)` | `int`, `unsigned`, `unsigned long long`, `long long` |
| `atomicExch` | `T atomicExch(T *address, T val)` | 存入 `val` | `int`, `unsigned`, `unsigned long long`, `float` |
| `atomicCAS` | `T atomicCAS(T *address, T compare, T val)` | `old == compare ? val : old` | `int`, `unsigned`, `unsigned long long`, `unsigned short` |

#### 5.2.5.4.2 内置原子函数

遵循 GNU 内置原子函数签名，额外带线程作用域参数。内存序与线程作用域枚举：

```cpp
// 原子内存顺序
# define __ATOMIC_RELAXED 0
# define __ATOMIC_CONSUME 1
# define __ATOMIC_ACQUIRE 2
# define __ATOMIC_RELEASE 3
# define __ATOMIC_ACQ_REL 4
# define __ATOMIC_SEQ_CST 5
// 线程作用域
# define __ATOMIC_SYSTEM 0 // 0 indicates default
# define __ATOMIC_DEVICE 1
# define __ATOMIC_BLOCK 2
# define __ATOMIC_THREAD 10
```

- 内存序对应 C++ 标准原子操作内存顺序；线程作用域遵循 `hggc::thread_scope` 定义。
- `_ATOMIC_CONSUME` 目前用更强的 `_ATOMIC_ACQUIRE` 实现。
- `__ATOMIC_THREAD` 目前用更广泛的 `__ATOMIC_BLOCK` 实现。

限制：

- 只能在设备函数中使用。
- 不能对局部内存操作。
- 函数地址不能被获取。
- `order` 和 `scope` 参数必须是**整数字面量**，不能是变量。

不支持的示例：

```cpp
#include <hggc/atomic>
// 主机函数中不允许
__host__ void bar() {
    unsigned u1 = 1, u2 = 2;
    __hg_atomic_load(&u1, &u2, __ATOMIC_RELAXED, __ATOMIC_SYSTEM); // 报错
}
// 不允许应用于局部内存
__device__ void foo() {
    unsigned a = 1, b;
    __hg_atomic_load(&a, &b, __ATOMIC_RELAXED, __ATOMIC_SYSTEM);
}
// 不允许作为模板默认参数。不能获取函数地址。
template <void *F = __hg_atomic_load_n> class X { // 报错
    void *f = F;
};
// 不允许在构造函数初始化列表中调用。
class Y {
    int a;
public:
    __device__ Y(unsigned *b)
        : a(__hg_atomic_load_n(b, __ATOMIC_RELAXED, __ATOMIC_SYSTEM)) {}
};
```

**内置原子函数清单**（`fetch_*` 变体返回 old 值；无 `fetch_` 变体无返回值）：

| 函数 | 原型 | 支持类型 | 备注 |
|---|---|---|---|
| `__hg_atomic_fetch_add` / `__hg_atomic_add` | `T (T *in1, T in2, int order, int scope)` / `void (...)` | `int`, `unsigned`, `unsigned long long`, `float`, `double` | `old + val` |
| `__hg_atomic_fetch_sub` / `__hg_atomic_sub` | 同上 | `int`, `unsigned`, `unsigned long long`, `float`, `double` | `old - val` |
| `__hg_atomic_fetch_and` / `__hg_atomic_and` | 同上 | `unsigned`, `unsigned long long` | `old & val` |
| `__hg_atomic_fetch_or` / `__hg_atomic_or` | 同上 | `unsigned`, `unsigned long long` | `old \| val` |
| `__hg_atomic_fetch_xor` / `__hg_atomic_xor` | 同上 | `unsigned`, `unsigned long long` | `old ^ val` |
| `__hg_atomic_fetch_min` / `__hg_atomic_min` | 同上 | `unsigned`, `int`, `unsigned long long`, `long long` | `min(old, val)` |
| `__hg_atomic_fetch_max` / `__hg_atomic_max` | 同上 | `unsigned`, `unsigned long long` | `max(old, val)` |
| `__hg_atomic_exchange_n` / `__hg_atomic_exchange` | `T (T *in1, T in2, int order, int scope)` / `void (...)` | `unsigned`, `unsigned long long` | `_n` 返回 old；`exchange` 将 old 存到 ret 指向位置 |
| `__hg_atomic_compare_exchange` / `__hg_atomic_compare_exchange_n` | `bool (T *in1, T *in2, T *in3, bool weak, int success_order, int fail_order, int scope)` / `bool (T *in1, T *in2, T in3, bool weak, int success_order, int fail_order, int scope)` | `unsigned`, `unsigned long long` | 相等则存 in3 返回 true，否则将 old 存入 *in2 返回 false；`weak` 被忽略，取两个 order 中较强者 |
| `__hg_atomic_load` / `__hg_atomic_load_n` | `void (T *src, T *dst, int order, int scope)` / `T (T *src, int order, int scope)` | 任意大小为 1、2、4、8 或 16 字节的 unsigned 整数类型 | `order` 不能是 `__ATOMIC_RELEASE` 或 `__ATOMIC_ACQ_REL` |
| `__hg_atomic_store` / `__hg_atomic_store_n` | `void (T *dst, T *src, int order, int scope)` / `void (T *dst, T res, int order, int scope)` | （同上 unsigned 整数） | `order` 不能是 `__ATOMIC_CONSUME`、`__ATOMIC_ACQUIRE` 或 `__ATOMIC_ACQ_REL` |
| `__hg_atomic_thread_fence` | `void (int order, int scope)` | — | 按指定内存序建立此线程内存访问排序；scope 指定可观察到排序效果的线程集合 |

> 比赛关联：无锁计数器（如 paged KV cache 的块分配器、request 完成计数）优先用 `hggc::atomic_ref`（可指定 `thread_scope_block` 降低成本）；纯累加无需顺序保证时用传统 `atomicAdd`（relaxed、无栅栏）开销最小。

## 5.2.6 Warp 函数

> NOTE：出于效率、安全性和可移植性，建议尽可能使用 **CUB（Warp-Wide 集合原语）** 执行 warp 操作。

### 5.2.6.1 Warp 活动掩码

```cpp
unsigned __activemask();
```

返回 32 位掩码表示调用 warp 中当前活动线程：第 N 个通道活动则第 N 位置 1；退出程序的线程始终标记为非活动。

> **警告**：`__activemask()` 不能用于确定哪些 warp 通道执行给定分支。它旨在用于机会主义 warp 级编程，仅提供活动线程的瞬时快照。

```cpp
// 检查是否有至少一个线程的谓词评估为真
if (pred) {
    // 无效：'at_least_one'的值是非确定性的
    // 并且可能在不同执行之间变化。
    at_least_one = __activemask() > 0;
}
```

在 `__activemask()` 调用处收敛的线程不保证后续指令处保持收敛（除非那些指令是 warp 同步原语 `__sync`）：

```cpp
unsigned mask =
    __activemask(); // 假设mask == 0xFFFFFFFF（所有位都设置，所有线程活动）
int predicate = threadIdx.x % 2 == 0; // 对偶数线程为1，对奇数线程为0
int result = __any_sync(mask, predicate); // 活动线程可能不会保留
```

### 5.2.6.2 Warp 表决函数

```cpp
int __all_sync(unsigned mask, int pred);
int __any_sync(unsigned mask, int pred);
unsigned __ballot_sync(unsigned mask, int pred);
```

- `__all_sync(mask, pred)`：mask 中所有未退出线程的 pred 全部非零则返回非零。
- `__any_sync(mask, pred)`：其中一个或多个非零则返回非零。
- `__ballot_sync(mask, pred)`：返回整数，第 N 位在 warp 第 N 个线程 pred 非零且该线程活动时置 1。

受 Warp `__sync` 内建约束限制。**这些内建函数不提供任何内存排序。**

### 5.2.6.3 Warp 匹配函数

```cpp
unsigned __match_any_sync(unsigned mask, T value);
unsigned __match_all_sync(unsigned mask, T value, int *pred);
```

- `__match_any_sync`：返回 mask 选出的未退出线程中具有相同 `value` 的线程掩码。
- `__match_all_sync`：mask 中所有未退出线程 `value` 相同则返回 mask，否则返回 0；同时 `pred` 相应置 true/false。

`T` 可以是 `int`、`unsigned`、`long`、`unsigned long`、`long long`、`unsigned long long`、`float` 或 `double`。受约束限制，不提供内存排序。

### 5.2.6.4 Warp 归约函数

> NOTE：建议尽可能使用 CUB（Warp-Wide 集合原语）执行 warp 归约。

```cpp
T __reduce_add_sync(unsigned mask, T value);
T __reduce_min_sync(unsigned mask, T value);
T __reduce_max_sync(unsigned mask, T value);
unsigned __reduce_and_sync(unsigned mask, unsigned value);
unsigned __reduce_or_sync(unsigned mask, unsigned value);
unsigned __reduce_xor_sync(unsigned mask, unsigned value);
```

- `__reduce_add_sync`/`__reduce_min_sync`/`__reduce_max_sync`：对 mask 中每个未退出线程的 `value` 做加法/最小/最大归约；`T` 可以是有符号或无符号整数。
- `__reduce_and_sync`/`__reduce_or_sync`/`__reduce_xor_sync`：按位与/或/异或归约。

受约束限制，不提供内存排序。

### 5.2.6.5 Warp 洗牌函数

```cpp
T __shfl_sync(unsigned mask, T var, int srcLane, int width = warpSize);
T __shfl_up_sync(unsigned mask, T var, unsigned delta, int width = warpSize);
T __shfl_down_sync(unsigned mask, T var, unsigned delta, int width = warpSize);
T __shfl_xor_sync(unsigned mask, T var, int laneMask, int width = warpSize);
```

在 warp 内未退出线程之间交换值，无需共享内存：

- `__shfl_sync()`：返回 `srcLane` 通道持有的值。width < warpSize 时每个子部分独立（起始逻辑通道 ID 为 0）；`srcLane` 超出 `[0, width-1]` 时取 `srcLane % width`。
- `__shfl_up_sync()`：源通道 ID = 调用者 ID − delta（值沿 warp 向上移动 delta 个通道）。源通道索引不回绕，较低 delta 通道保持不变。
- `__shfl_down_sync()`：源通道 ID = 调用者 ID + delta（值向下移动）。同样不回绕，较高 delta 通道保持不变。
- `__shfl_xor_sync()`：源通道 ID = 调用者 ID ⊕ laneMask（蝴蝶寻址，用于树形归约和广播）。width < warpSize 时每组连续 width 个线程可访问前面组的元素；尝试访问靠后组元素时返回自己的值。

`T` 可以是：

- `int`、`unsigned`、`long`、`unsigned long`、`long long`、`unsigned long long`、`float`、`double`；
- 包含 `hggc_fp16.h` 时的 `__half` 和 `__half2`；
- 包含 `hggc_bf16.h` 时的 `__ppu_bfloat16` 和 `__ppu_bfloat162`。

线程只能从活动的且参与内建函数的线程读取数据；目标线程非活动时获取值未定义。`width` 必须是 `[1, warpSize]` 中 2 的幂（1、2、4、8、16、32），其他值产生未定义结果。受 Warp `__sync` 内建约束限制。

有效用法示例：

```cpp
int laneId = threadIdx.x % warpSize;
int data = 0;
// 所有warp线程从通道0获取数据
int result = __shfl_sync(0xFFFFFFFF, data, 0);
if (laneId < 4) {
    // 通道0、1、2、3从通道1获取数据
    result = __shfl_sync(0b1111, data, 1);
}
// 通道[0 - 15]从通道0获取数据
// 通道[16 - 31]从通道16获取数据
result = __shfl_sync(0xFFFFFFFF, data, warpSize / 2);
// 每个通道从两个位置之上的通道获取数据
// 通道30、31获得它们原来的值
result = __shfl_down_sync(0xFFFFFFFF, data, 2);
```

无效用法示例：

```cpp
int laneId = threadIdx.x % warpSize;
int value = 0;
// 未定义行为：通道0没有参与调用
int result = (laneId > 0) ? __shfl_sync(0xFFFFFFFF, value, 0) : 0;
if (laneId <= 4) {
    // 未定义行为：对于通道3、4来说，目标通道5、6不活跃
    result = __shfl_down_sync(0b11111, value, 2);
}
// 未定义行为：width不是2的幂
__shfl_sync(0xFFFFFFFF, value, 0, 31);
```

> **警告**：这些内建函数不隐含内存屏障，不保证任何内存序。

**示例 1：单个值在整个 warp 中广播**：

```cpp
#include <assert.h>
__global__ void kernel(int input) {
    int laneId = threadIdx.x % 32;
    int value;
    if (laneId == 0) { // 除通道0外所有线程的未使用变量
        value = input;
    }
    // 同步warp中的所有线程，并从通道0获取"value"
    value = __shfl_sync(0xFFFFFFFF, value, 0);
    assert(value == input);
}
int main() {
    kernel<<<1, 32>>>(1234);
    hggcDeviceSynchronize();
    return 0;
}
```

**示例 2：跨 8 线程子分区的包含式前缀扫描**（建议用 `cub::WarpScan`）：

```cpp
// HGGC C++ 方式：
#include <cstdio>
#include <cub/cub.cuh>
__global__ void kernel() {
    using WarpScan = cub::WarpScan<int, 8>;
    __shared__ WarpScan::TempStorage storage;
    int laneId = threadIdx.x % 32;
    int value = 31 - laneId; // 起始累加值
    int sum;
    WarpScan(storage).InclusiveSum(value, sum);
}
int main() {
    kernel<<<1, 32>>>();
    hggcDeviceSynchronize();
    return 0;
}
```

```cpp
// 内建函数方式：
#include <stdio.h>
__global__ void kernel() {
    int laneId = threadIdx.x % 32;
    int value = 31 - laneId; // 起始累加值
    // 循环累积分区内的扫描。
    // 扫描需要log2(8) == 3步才能完成8个线程
    for (int delta = 1; delta <= 4; delta *= 2) {
        // 从laneId - delta读取
        int result = __shfl_up_sync(0xFFFFFFFF, value, delta, 8);
        int lane = laneId % 8 - delta;
        if (lane >= 0) // 'lane < 0'的通道保持其值不变
            value += result;
    }
}
int main() {
    kernel<<<1, 32>>>();
    hggcDeviceSynchronize();
    return 0;
}
```

**示例 3：跨 warp 归约**（建议用 `cub::WarpReduce`）：

```cpp
#include <stdio.h>
__global__ void kernel() {
    int laneId = threadIdx.x % 32;
    int value = 31 - laneId; // 起始累加值
    // 使用 XOR 模式执行蝶形规约
    // 完整warp规约需要log2(32) == 5步
    for (int i = 1; i <= 16; i *= 2)
        value += __shfl_xor_sync(0xFFFFFFFF, value, i);
    // "value"现在包含了所有线程的总和
}
int main() {
    kernel<<<1, 32>>>();
    hggcDeviceSynchronize();
    return 0;
}
```

### 5.2.6.6 Warp `__sync` 内建约束

适用函数：`__shfl_sync`、`__shfl_up_sync`、`__shfl_down_sync`、`__shfl_xor_sync`、`__match_any_sync`、`__match_all_sync`、`__reduce_add_sync`、`__reduce_min_sync`、`__reduce_max_sync`、`__reduce_and_sync`、`__reduce_or_sync`、`__reduce_xor_sync`、`__syncwarp`。

`mask` 参数指示哪些 warp 线程参与调用，每一位对应通道 ID（`threadIdx.x % warpSize`）；内建函数等待 mask 中指定的所有未退出线程到达调用点。必须满足：

- 每个调用线程必须在其对应的 mask 位中设置 1。
- 每个非调用线程必须在 mask 中将其对应位设置为 0；退出的线程被忽略。
- mask 中指定的所有未退出线程必须以**相同的 mask 值**执行内建函数。
- warp 线程并发调用内建函数但带不同 mask 值时，前提是这些掩码互不重叠（即使在分支控制流中也有效）。

以下情况核函数挂起或行为未定义：

- 调用线程未在 mask 中指定。
- mask 中指定的未退出线程未能最终退出或在相同程序点以相同 mask 值调用。
- 条件代码中，所有条件未在 mask 指定的所有未退出线程间求值一致。

> NOTE：mask 为 `0xFFFFFFFF`（所有 warp 线程参与）时内建函数达到最佳效率。

有效示例：

```cpp
__global__ void kernel(int pred) {
    if (threadIdx.x < 4) {
        // 线程0, 1, 2, 3是活动的
        __all_sync(0b1111, pred); // 正确，线程0, 1, 2, 3参与调用
    }
    if (threadIdx.x == 0)
        return; // 退出
    // 正确，所有未退出线程参与调用
    __all_sync(0xFFFFFFFF, pred);
}
```

不相交 mask 示例：

```cpp
__global__ void kernel(int *input, int *output) {
    if (threadIdx.x < warpSize) {
        __shared__ int data[warpSize];
        data[threadIdx.x] = input[threadIdx.x];
        unsigned mask = threadIdx.x < 16 ? 0xFFFF : 0xFFFF0000; // 正确
        __syncwarp(mask);
        if (threadIdx.x == 0 || threadIdx.x == 16)
            output[threadIdx.x] = data[threadIdx.x + 1];
    }
}
__global__ void kernel_branches(int *input, int *output) {
    if (threadIdx.x < warpSize) {
        __shared__ int data[warpSize];
        data[threadIdx.x] = input[threadIdx.x];
        if (threadIdx.x < 16) {
            unsigned mask = 0xFFFF; // 正确
            __syncwarp(mask);
            output[threadIdx.x] = data[15 - threadIdx.x];
        } else {
            unsigned mask = 0xFFFF0000; // 正确
            __syncwarp(mask);
            output[threadIdx.x] = data[31 - threadIdx.x];
        }
    }
}
```

无效示例：

```cpp
if (threadIdx.x < 4) { // 线程0, 1, 2, 3是活动的
    __all_sync(0b0000011, pred); // 错误，线程2, 3是活动的但在掩码中未设置
    __all_sync(0b0111111, pred); // 错误，线程4, 5不活动但在掩码中已设置
}
// 错误，参与线程有不同的且重叠的掩码
__all_sync(threadIdx.x == 0 ? 1 : 0xFFFFFFFF, pred);
```

> 比赛关联：softmax、RMSNorm、top-k 等 kernel 的 warp 内归约首选 `__shfl_xor_sync` 蝶形模式（免共享内存、免 `__syncthreads`）；写 mask 时牢记「调用线程必须置位、所有参与者 mask 相同、全参与用 0xFFFFFFFF 最快」三规则。

## 5.2.7 Warp 矩阵函数（awmma，Tensor Cell）

C++ warp 矩阵操作利用 **Tensor Cell** 加速 `D = A*B + C` 形式的矩阵计算，支持混合精度浮点数据。需要 warp 中所有线程合作；**只有条件求值在整个 warp 中结果完全相同时，才允许在条件代码中执行这些操作**，否则可能挂起。

### 5.2.7.1 描述

所有函数和类型都在 **`awmma`** 命名空间中定义。子字节操作是预览版功能（数据结构和 API 可能变化、与未来版本不兼容），定义在 `awmma::experimental` 命名空间中。

```cpp
template <typename Use, int m, int n, int k, typename T, typename Layout = void>
class fragment;
void load_matrix_sync(fragment<...> &a, const T *p, unsigned ldm);
void load_matrix_sync(fragment<...> &a, const T *p, unsigned ldm,
                      layout_t layout);
void store_matrix_sync(T *p, const fragment<...> &a, unsigned ldm,
                       layout_t layout);
void fill_fragment(fragment<...> &f, const T &in);
void mma_sync(fragment<...> &d, const fragment<...> &a, const fragment<...> &b,
              const fragment<...> &c, bool satf = false);
```

**fragment**：重载类，包含分布在 warp 所有线程上的矩阵部分；矩阵元素到 fragment 内存的映射未指定，未来架构可能更改。第一个模板参数 `Use` 的可接受值：

- `matrix_a`：片段用作第一个乘数 A；
- `matrix_b`：片段用作第二个乘数 B；
- `accumulator`：片段用作源/目标累加器（C 或 D）。

`m`、`n`、`k` 描述参与乘加运算的 warp-wide 矩阵块形状：`matrix_a` 块为 m×k 维，`matrix_b` 为 k×n 维，`accumulator` 为 m×n。

数据类型 `T`：用于乘数时可以是 `float`、`__half`、`__ppu_bfloat16`、`char` 或 `unsigned char`；用于累加器时可以是 `float`、`int` 或 `__half`（组合限制见 5.2.7.3）。`Layout` 必须为 `matrix_a` 和 `matrix_b` 片段指定：`row_major` 或 `col_major` 分别表示行/列元素在内存中连续；`accumulator` 的 `Layout` 保留默认 `void`，仅在加载/存储累加器时指定行/列布局。

**load_matrix_sync**：等待所有 warp 通道到达，然后从内存加载矩阵片段 `a`。
- `p` 必须是指向矩阵第一个元素的 **256 位对齐**指针。
- `ldm` 描述连续行（行优先）或列（列优先）之间的步长（以元素为单位），`__half` 元素类型必须是 **8 的倍数**，`float` 元素类型必须是 **4 的倍数**（即两种情况下都是 16 字节的倍数）。
- accumulator 片段必须指定 `layout` 为 `mem_row_major` 或 `mem_col_major`；`matrix_a`/`matrix_b` 布局由片段模板参数推断。
- `p`、`ldm`、`layout` 及所有模板参数的值在 warp 所有线程中必须相同；所有线程都必须调用，否则结果未定义。

**store_matrix_sync**：等待所有 warp 通道到达，将片段存储到内存。对齐、`ldm` 要求同 `load_matrix_sync`；输出矩阵布局必须指定为 `mem_row_major` 或 `mem_col_major`；所有参数 warp 内一致。

**fill_fragment**：用常量值 `in` 填充矩阵片段。通常由 warp 中所有线程以公共值调用。

**mma_sync**：等待所有 warp 通道到达，执行 `D = A*B + C`；也支持就地操作 `C = A*B + C`。`satf` 值和各片段模板参数必须 warp 内一致；A、B、C、D 的 m、n、k 必须匹配；必须由 warp 所有线程调用。
若 `satf`（饱和到有限值）为 true，目标累加器的额外数值属性：
- 元素结果为 +Infinity → 累加器为 +MAX_NORM
- 元素结果为 −Infinity → 累加器为 −MAX_NORM
- 元素结果为 NaN → 累加器为 +0

由于元素映射未指定，必须在 `store_matrix_sync` 后从内存访问各元素。特殊情况下（warp 所有线程统一地对所有片段元素做逐元素操作），可用 fragment 类成员直接访问：

```cpp
enum fragment<Use, m, n, k, T, Layout>::num_elements;
T fragment<Use, m, n, k, T, Layout>::x[num_elements];
```

例如将 accumulator 矩阵块元素缩小一半：

```cpp
awmma::fragment<awmma::accumulator, 16, 16, 16, float> frag;
float scale = 0.5f; // warp中所有线程的相同值
/*...*/
for (int t = 0; t < frag.num_elements; t++)
    frag.x[t] *= scale;
```

### 5.2.7.2 替代浮点数

**`__ppu_bfloat16`**：替代 fp16 的格式，与 f32 相同范围但精度降低（7 位尾数）。可直接使用 `hggc_bf16.h` 中的 `__ppu_bfloat16` 类型。其矩阵片段需要与 `float` 类型累加器组合使用；支持的形状和操作与 `__half` 相同。

**tf32**：Tensor Cell 支持的特殊浮点格式，与 f32 相同范围但精度降低（≥10 位），内部布局是实现定义的。使用方式：

- 输入矩阵必须**手动转换**为 tf32 精度；提供内置函数 `__float_to_tf32`（输入输出参数都是 `float` 类型，但输出数值上是 tf32）。该精度仅用于与 Tensor Cell 一起使用，与其他 float 操作混用时结果的精度和范围未定义。
- 输入矩阵（`matrix_a`/`matrix_b`）转换为 tf32 后，`precision::tf32` 精度的 fragment 与 `load_matrix_sync` 的 `float` 数据类型结合即可使用；累加器片段必须为 `float`。
- **唯一支持的矩阵大小是 16x16x8（m-n-k）**。
- 片段元素表示为 `float`，`element_type<T>` 到 `storage_element_type<T>` 的映射：`precision::tf32 -> float`。

### 5.2.7.3 元素类型和矩阵大小

支持的 matrix_a / matrix_b / accumulator 组合：

| 矩阵 A | 矩阵 B | 累加器 | 矩阵大小 (m-n-k) |
|---|---|---|---|
| `__half` | `__half` | `float` | 16x16x16 |
| `__half` | `__half` | `float` | 32x8x16 |
| `__half` | `__half` | `float` | 8x32x16 |
| `__half` | `__half` | `__half` | 16x16x16 |
| `__half` | `__half` | `__half` | 32x8x16 |
| `__half` | `__half` | `__half` | 8x32x16 |
| `unsigned char` | `unsigned char` | `int` | 16x16x16 |
| `unsigned char` | `unsigned char` | `int` | 32x8x16 |
| `unsigned char` | `unsigned char` | `int` | 8x32x16 |
| `signed char` | `signed char` | `int` | 16x16x16 |
| `signed char` | `signed char` | `int` | 32x8x16 |
| `signed char` | `signed char` | `int` | 8x32x16 |
| `__ppu_bfloat16` | `__ppu_bfloat16` | `float` | 16x16x16 |
| `__ppu_bfloat16` | `__ppu_bfloat16` | `float` | 32x8x16 |
| `__ppu_bfloat16` | `__ppu_bfloat16` | `float` | 8x32x16 |
| `precision::tf32` | `precision::tf32` | `float` | 16x16x8 |

（注：本章 awmma API 表未列出 FP8/FP4 的 fragment 组合——FP8/FP4 仅在 §5.5 的 Tensor Cell 硬件支持表中出现（ppu0015 支持），使用需通过内联 TIX 或 `awmma::experimental` 子字节预览功能；具体 API 需查 TIX ISA 文档（需查原文确认）。）

### 5.2.7.4 示例

单 warp 实现 16x16x16 矩阵乘法：

```cpp
#include <hggc_mma.h>
__global__ void kernel(half *a, half *b, float *c) {
    // 声明片段
    awmma::fragment<awmma::matrix_a, 16, 16, 16, half, awmma::col_major> a_frag;
    awmma::fragment<awmma::matrix_b, 16, 16, 16, half, awmma::row_major> b_frag;
    awmma::fragment<awmma::accumulator, 16, 16, 16, float> c_frag;
    // 将输出初始化为零
    awmma::fill_fragment(c_frag, 0.0f);
    // 加载输入
    awmma::load_matrix_sync(a_frag, a, 16);
    awmma::load_matrix_sync(b_frag, b, 16);
    // 执行矩阵乘法
    awmma::mma_sync(c_frag, a_frag, b_frag, c_frag);
    // 存储输出
    awmma::store_matrix_sync(c, c_frag, 16, awmma::mem_row_major);
}
```

> 比赛关联（核心）：Qwen3.5-2B 推理的 GEMM/GEMV 性能上限由 Tensor Cell 决定。要点：
> - **BF16 权重 + FP32 累加**（`__ppu_bfloat16` × `__ppu_bfloat16` → `float`）是精度保持的最佳选择，形状 16x16x16 / 32x8x16 / 8x32x16 可选——decode 阶段 M 小，8x32x16 更贴合；
> - **INT8 量化**（`signed/unsigned char` → `int`）可直接用于 W8A8 量化 GEMM；
> - tf32 仅 16x16x8 一种形状，需 `__float_to_tf32` 手动转换；
> - `ldm` 对齐（half 为 8 的倍数）与 256 位指针对齐是数据布局设计的硬约束，tiling 方案须围绕它设计；
> - ppu0015 额外支持 FP8/FP4 Tensor Cell（见 §5.5），是 FP8 量化路线的硬件基础，但 C++ awmma 层未暴露，需走 TIX 内联。

## 5.2.8 调试和诊断

### 5.2.8.1 断言

```cpp
void assert(int expression);
```

`expression` 等于零时 `assert()` 宏停止核函数执行。调试中则触发断点；否则对每个失败线程，在通过 `hggcDeviceSynchronize()`、`hggcStreamSynchronize()` 或 `hggcEventSynchronize()` 与主机同步后向 stderr 打印消息，格式：

```
<filename>:<line number> :<function> : block: [blockIdx.x,blockIdx.y,blockIdx.z], thread: [threadIdx.x,threadIdx.y,threa...
```

核函数执行被中止并在主机程序中引发中断；`assert()` 会导致 HGGC 上下文损坏，后续 HGGC 调用或核函数调用以 `hggcErrorAssert` 失败。`expression` 非零则无影响。

示例（源文件 test.hg）：

```cpp
#include <assert.h>
__global__ void kernel(void) {
    // 不会有影响
    assert(1);
    // 将停止核函数执行
    assert(0);
}
int main(void) {
    kernel<<<1, 1>>>();
    hggcDeviceSynchronize();
    return 0;
}
```

输出：

```
test.hg:6 :void kernel() : block: [0,0,0], thread: [0,0,0] Assertion `0` failed.
```

断言用于调试，可能影响性能，生产代码建议禁用：在包含 `assert.h`/`<cassert>` 前定义 `NDEBUG` 宏，或用编译器标志 `-DNDEBUG`。表达式不应有副作用，否则禁用断言会改变代码功能。

### 5.2.8.2 断点函数

```cpp
void __brkpt();
```

可从任何设备线程调用 `__brkpt()` 暂停核函数执行。

---

# 5.3 HGGC 环境变量

汇总表：

| 环境变量 | 取值 | 含义 |
|---|---|---|
| `HGGC_VISIBLE_DEVICES` | 逗号分隔的 PPU 标识符列表（整数序号 / UUID / MIG 实例）；未设置=全部可见；空字符串=屏蔽全部 | 控制应用可发现哪些 PPU 设备及枚举顺序 |
| `HGGC_LAUNCH_BLOCKING` | `0`（默认）/ `1` | `1` 强制每次核函数启动同步执行（阻塞至设备完成），用于调试 |
| `HGGC_DEVICE_MAX_CONNECTIONS` | 1 到 32，默认 8（无 MPS 模式） | 并发计算和复制引擎连接（工作队列）数量 |
| `HGGC_MODULE_LOADING` | `DEFAULT` / `1` / `2` | 控制模块加载（设备代码初始化）时机：立即全载 vs 惰性加载 |

（另：§5.1.6.2 printf 缓冲区刷新一节提到 `LAUNCH_BLOCKING=1`，与 `HGGC_LAUNCH_BLOCKING` 同义（需查原文确认前缀差异）。）

## 5.3.1 设备枚举与属性

### 5.3.1.1 `HGGC_VISIBLE_DEVICES`

精确控制应用程序能发现哪些 PPU 设备，并自定义枚举顺序。未设置时所有 PPU 均可见；设为空字符串则屏蔽全部设备。

取值格式：逗号分隔的 PPU 标识符列表，支持三种标识方式：

| 标识方式 | 格式 | 示例 |
|---|---|---|
| 整数序号 | `ppu-smi`（PPU System Management Interface）报告的从 0 开始的设备编号 | `0,2` |
| PPU UUID | `ppu-smi -L` 输出的完整或前缀 UUID | `PPU-8932f937` |
| MIG 实例 | `MIG-<UUID>/<PPU 实例 ID>/<计算实例 ID>` | `MIG-PPU-8932f937-⋯/1/2` |

- **UUID 前缀**：只要前缀在当前系统中能唯一标识目标设备，即可使用缩写形式。MIG 模式下仅支持枚举单个实例。
- **无效标识符的截断行为**：列表从左到右解析，遇到无效条目（如不存在的序号 `-1`）解析终止，后续标识符被忽略。例如 `HGGC_VISIBLE_DEVICES=0,2,-1,1` 的结果是仅设备 0 和 2 可见，设备 1 因排在无效项之后被屏蔽。
- **对 HGGC API 的影响**：设置后 `hggcGetDeviceCount()` 仅返回可见设备数量，HGGC API 中整数设备 ID 范围变为 `[0, 可见设备数−1]`，序号按列表出现顺序分配。例如 `HGGC_VISIBLE_DEVICES=2,1` 时，`hggcSetDevice(0)` 将物理设备 2 设为当前设备；`hggcGetDevice(&device_ordinal)` 返回的 0 也对应物理设备 2。

示例：

```bash
ppu-smi -L   # 查看系统中所有 PPU 及其 UUID
HGGC_VISIBLE_DEVICES=0,1
HGGC_VISIBLE_DEVICES=PPU-8932f937-d72c-4106-c12f-20bd9faed9f6
HGGC_VISIBLE_DEVICES=MIG-PPU-8932f937-d72c-4106-c12f-20bd9faed9f6/1/2
```

## 5.3.2 执行

### 5.3.2.1 `HGGC_LAUNCH_BLOCKING`

控制核函数启动是否以同步模式运行。

- 默认（`0`）：所有核函数启动异步——主机提交工作后立即继续，不等待设备完成。
- `1`：强制每次核函数启动在设备执行完毕后才返回控制权给 CPU。

主要用途是**调试**：异步模式下 HGGC API 报告的错误往往延迟到后续同步点才被捕获，难以定位出错调用；同步模式下错误在触发它的 API 调用处立即报告。注意同步模式会**显著降低吞吐量**。

```bash
HGGC_LAUNCH_BLOCKING=1
```

### 5.3.2.2 `HGGC_DEVICE_MAX_CONNECTIONS`

控制并发计算和复制引擎连接（工作队列）数量，将两者都设置为指定值。

PPU 运行时将来自不同 HGGC 流的任务分配到有限数量的硬件工作队列。活跃流数量超过可用队列时，多个流共享同一队列，原本无依赖的任务被串行执行（虚假依赖）。增大此值可降低队列共享概率，提升多流并行度。**经验法则：队列数不低于每个上下文中同时活跃的 HGGC 流数量。**

- 可选值：**1 到 32**，默认 **8**（无 MPS 模式下）。

```bash
HGGC_DEVICE_MAX_CONNECTIONS=16
```

## 5.3.3 模块加载

### 5.3.3.1 `HGGC_MODULE_LOADING`

影响 HGGC 运行时加载模块的方式（如何初始化设备代码）：

| 取值 | 行为 |
|---|---|
| `DEFAULT` | 默认行为，等效于 `1` |
| `1` | 程序初始化时完全加载 HGGC 模块和核函数：所有来自 HGBIN 或 FATBIN 文件的核函数和数据在相应 `hgModuleLoad*` 和 `hgLibraryLoad*` 驱动 API 调用时完全加载。启动时间较长，PPU 内存占用较高，核函数启动开销可预测 |
| `2` | 特定核函数的加载延迟到用 `hgModuleGetFunction()` 或 `hgKernelGetFunction()` 提取 HGGC 函数句柄 `HGfunc` 时。HGBIN 中数据在加载第一个核函数或访问第一个变量时加载；驱动在首次调用核函数时加载所需代码，后续调用无额外开销。**减少启动时间和 PPU 内存占用** |

```bash
HGGC_MODULE_LOADING=1
HGGC_MODULE_LOADING=2
```

> 比赛关联：
> - 多流流水线（prefill 计算与 H2D 权重/KV 传输重叠）需要足够的硬件队列：流数 > 8 时务必调大 `HGGC_DEVICE_MAX_CONNECTIONS`（至多 32），否则虚假依赖串行化直接吞掉吞吐收益。
> - `HGGC_MODULE_LOADING=2` 惰性加载可缩短进程启动时间、降低显存占用——对评测脚本频繁启动进程的场景（TTFT 测量不含启动的话）和显存紧张的大 batch 场景都有价值；但首次调用 kernel 有一次性加载开销，压测前需 warm-up。
> - `HGGC_LAUNCH_BLOCKING=1` 仅用于调试定位，压吞吐时必须关掉。

---

# 5.4 数学函数

## 5.4.1 浮点简介

IEEE-754 二进制浮点算术标准（1985 年采用）规定浮点算术结果应如何近似。异构计算环境中操作在不同类型硬件上执行，理解浮点行为对精度和性能都至关重要。

### 5.4.1.1 浮点格式

二进制浮点数据编码在三个字段上：**符号**（1 位）、**指数**（以 2 为基数、数值偏置编码）、**尾数**（mantissa/fraction，编码分数部分）。

- 正规值：$(-1)^{sign} \times 1.fraction \times 2^{exponent - bias}$
- 非正规值：$(-1)^{sign} \times 0.fraction \times 2^{1 - bias}$（缺少前导 1）
- 单精度和双精度指数偏置分别为 **127** 和 **1023**；分数的整数部分 `1.` 是隐含的。

例：$-192 = (-1)^1 \times 2^7 \times 1.5$，指数为 7，float 表示为位串 $7+127=134=10000110$，double 为 $7+1023=1030$；尾数 $0.5=2^{-1}$ 第一位为 1。

并非所有实数都能精确表示（如 $2/3 = 0.10101010..._2$），必须舍入。IEEE-754 规定舍入规则，最常用模式是**向最近偶数舍入**。

### 5.4.1.2 正规值和非正规值

- 指数中至少一位为 1 的值称为**正规值**。
- 最小可表示非零浮点数 FLT_MIN 与零之间存在巨大差距；**非正规数（denormals）**的指数全零、尾数至少一位为 1，允许精度逐渐损失而非突然向零舍入，是 IEEE-754 的必需部分。
- 非正规数计算成本更高。不需要严格精度的应用可通过 hgcc 选项 **`-ftz=true`**（flush-to-zero，刷新为零）禁用非正规数，该选项也包含在 **`--use_fast_math`** 中。

### 5.4.1.3 特殊值

- **零**：有 `+0` 和 `-0` 两种表示；`+0 == -0` 计算结果为 true；编码中指数和尾数全零。
- **无穷大**：浮点数行为符合饱和算术，超出可表示范围的结果为 +Infinity/−Infinity；编码中指数全 1、尾数全 0，恰好两种编码。任何将有限数应用于无穷大的算术运算都得无穷大，除以零和乘以零除外（结果为 NaN）。
- **NaN**：表示未定义或不可表示的值（如 `0.0/0.0`、`sqrt(-1.0)`、`+Inf − Inf`）；编码中指数全 1、尾数为除全零外任意位模式，共 $2^{mantissa+1} − 2$ 种可能编码。任何涉及 NaN 的算术运算得 NaN；任何涉及 NaN 的比较都得 false（包括 `NaN == NaN`，非自反）。

### 5.4.1.4 舍入

IEEE-754 要求支持加法、减法、乘法、除法、平方根、融合乘加、求余数、转换、缩放、符号和比较运算；给定格式和舍入模式下，这些运算结果在所有标准实现中保证一致。

四种舍入模式（HGGC 全部支持，默认**向最近舍入**；内建数学函数可为单个运算选择其他模式）：

| 舍入模式 | 解释 |
|---|---|
| `rn` | 向最近舍入，舍入到偶数 |
| `rz` | 向零舍入 |
| `ru` | 向 $+\infty$ 舍入 |
| `rd` | 向 $-\infty$ 舍入 |

### 5.4.1.5 浮点数据类型

HGGC 支持 Bfloat16、半精度、单精度、双精度浮点类型：

**表 4：支持的浮点类型**

| 精度/名称 | 数据类型 | IEEE-754 | 头文件/内置 | 符号位 (Sign) | 指数位 (Exponent) | 尾数位 (Mantissa) | 总位宽 |
|---|---|---|---|---:|---:|---:|---:|
| Bfloat16 | `__hg_bfloat16` | ❌ | `<hggc_bf16.h>` | 1 | 8 | 7 | 16 |
| 半精度 | `__half` | ✅ | `<hggc_fp16.h>` | 1 | 5 | 10 | 16 |
| 单精度 | `float` | ✅ | 内置 | 1 | 8 | 23 | 32 |
| 双精度 | `double` | ✅ | 内置 | 1 | 11 | 52 | 64 |

（注：此处 bf16 类型原文写作 `__hg_bfloat16`，而 §5.2 各处写作 `__ppu_bfloat16`，头文件均为 `hggc_bf16.h`——两个名称可能并存或其中一处为笔误，需查原文确认。）

**表 5：支持的浮点类型属性**（表头在 PDF 文本层已损坏，按数据规律重建为：最大值（指数/十进制两种表示）、最小正正规值（指数/十进制）、最小正非正规数、机器精度，需查原文确认）

| 精度/名称 | 最大值 | 最小正正规值 | 最小正非正规数 | 机器精度 ε |
|---|---|---|---|---|
| Bfloat16 | $\approx 2^{128}$（$\approx 3.39 \times 10^{38}$） | $2^{-126}$（$\approx 1.18 \times 10^{-38}$） | $2^{-133}$ | $2^{-7}$ |
| 半精度 | $\approx 2^{16}$（$65504$） | $2^{-14}$（$\approx 6.1 \times 10^{-5}$） | $2^{-24}$ | $2^{-10}$ |
| 单精度 | $\approx 2^{128}$（$\approx 3.39 \times 10^{38}$） | $2^{-126}$（$\approx 1.18 \times 10^{-38}$） | $2^{-149}$ | $2^{-23}$ |
| 双精度 | $\approx 2^{1024}$（$\approx 1.8 \times 10^{308}$） | $2^{-1022}$（$\approx 2.22 \times 10^{-308}$） | $2^{-1074}$ | $2^{-52}$ |

> 比赛关联：BF16 与 FP32 同范围（指数 8 位）但尾数仅 7 位——这就是 Qwen3.5-2B 用 BF16 权重不易溢出但细节精度有限的原因；FP16 尾数 10 位但最大值仅 65504，激活值大时容易溢出。量化方案选型（BF16 vs FP16 vs FP8）要对照此表评估动态范围。

## 5.4.2 函数精度

MATH 文档列出设备代码支持的所有 C/C++ 标准库数学函数及所有内建函数（仅设备代码）。下文部分函数给出以 **ULP**（Unit in the Last Place）表示的精度界限；严格定义见 Jean-Michel Muller 的研究报告 *On the definition of ulp(x)*（RR-5504, LIP RR-2005-09, INRIA, LIP, 2005, pp.16），https://hal.inria.fr/inria-00070503/document。

**设备端与主机端 math.h 的行为差异**：

| 差异项 | 主机端 (math.h) | 设备端 (HGGC) |
|---|---|---|
| 错误报告 | 通过 errno 或浮点异常通知调用方 | 既不设置 errno 也不触发异常；需调用方自行校验 |
| 指针参数校验 | 视实现而定，可能会做边界检查 | 不做校验，调用方须确保指向合法已分配内存 |
| 未初始化参数 | 同属未定义行为（UB），现代编译器可能激进优化 | 内联优化可能利用未初始化值，导致不可预测结果 |

### 5.4.2.1 标准函数

标准数学函数同时适用于主机和设备代码。表中误差界限针对设备端执行路径；主机系统不提供某函数原生实现时，HGGC 库实现也遵循相同精度范围。误差界限基于大规模随机和边界测试，覆盖面广但非穷举，应视为**经验性上界**而非数学证明。

#### 5.4.2.1.1 单精度浮点函数

基础算术（加法、乘法）严格遵循 IEEE-754，误差不超过 0.5 ulp。

> **浮点取整性能提示**：将单精度操作数舍入为整数推荐用 `rintf()` 而非 `roundf()`（结果仍为 float）。`roundf()` 在设备上映射为 **4 条指令**序列，`rintf()` 为**单条指令**；`truncf()`、`ceilf()`、`floorf()` 也都是单条指令。

**表 6：单精度数学标准库函数的最大 ULP 误差**（误差 = HGGC 库函数结果与按向最近偶数舍入正确舍入的单精度结果之差的绝对值，单位 ulp）

| 函数 | 最大 ulp 误差 |
|---|---|
| `x+y` | 0（IEEE-754 向最近偶数舍入） |
| `x*y` | 0（IEEE-754 向最近偶数舍入） |
| `x/y` | `-prec-div=true` 编译时为 0；否则 4（全范围） |
| `1/x` | `-prec-div=true` 编译时为 0；否则 1（全范围） |
| `rsqrtf(x)` | 2（全范围） |
| `1/sqrtf(x)` | 仅适用于被编译器转换为 `rsqrtf(x)` 的 `1/sqrtf(x)` |
| `sqrtf(x)` | `-prec-sqrt=true` 编译时为 0；否则 1 |
| `cbrtf(x)` | 1（全范围） |
| `rcbrtf(x)` | 1（全范围） |
| `hypotf(x,y)` | 3（全范围） |
| `rhypotf(x,y)` | 2（全范围） |
| `norm3df(x,y,z)` | 3（全范围） |
| `rnorm3df(x,y,z)` | 2（全范围） |
| `norm4df(x,y,z,t)` | 3（全范围） |
| `rnorm4df(x,y,z,t)` | 2（全范围） |
| `normf(dim,arr)` | 无法提供误差界限（快速算法，舍入导致精度损失） |
| `rnormf(dim,arr)` | 无法提供误差界限（同上） |
| `expf(x)` | 2（全范围） |
| `exp2f(x)` | 2（全范围） |
| `exp10f(x)` | 2（全范围） |
| `expm1f(x)` | 2（全范围） |
| `logf(x)` | 1（全范围） |
| `log2f(x)` | 1（全范围） |
| `log10f(x)` | 2（全范围） |
| `log1pf(x)` | 1（全范围） |
| `sinf(x)` | 2（全范围） |
| `cosf(x)` | 2（全范围） |
| `tanf(x)` | 4（全范围） |
| `sincosf(x,sptr,cptr)` | 2（全范围） |
| `sinpif(x)` | 1（全范围） |
| `cospif(x)` | 1（全范围） |
| `sincospif(x,sptr,cptr)` | 1（全范围） |
| `asinf(x)` | 4（全范围） |
| `acosf(x)` | 4（全范围） |
| `atanf(x)` | 2（全范围） |
| `atan2f(y,x)` | 3（全范围） |
| `sinhf(x)` | 3（全范围） |
| `coshf(x)` | 2（全范围） |
| `tanhf(x)` | 3（全范围） |
| `asinhf(x)` | 3（全范围） |
| `acoshf(x)` | 4（全范围） |
| `atanhf(x)` | 3（全范围） |
| `powf(x,y)` | 10（全范围） |
| `erff(x)` | 2（全范围） |
| `erfcf(x)` | 5（全范围） |
| `erfinvf(x)` | 4（全范围） |
| `erfcinvf(x)` | 5（全范围） |
| `erfcxf(x)` | 4（全范围） |
| `normcdff(x)` | 5（全范围） |
| `normcdfinvf(x)` | 5（全范围） |
| `lgammaf(x)` | 6（区间 −10.001⋯−2.264 之外；区间内更大） |
| `tgammaf(x)` | 5（全范围） |
| `fmaf(x,y,z)` | 0（全范围） |
| `frexpf(x,exp)` | 0（全范围） |
| `ldexpf(x,exp)` | 0（全范围） |
| `scalbnf(x,n)` | 0（全范围） |
| `scalblnf(x,l)` | 0（全范围） |
| `logbf(x)` | 0（全范围） |
| `ilogbf(x)` | 0（全范围） |
| `j0f(x)` | 9 当 \|x\| < 8 时；否则最大绝对误差 2.2×10⁻⁶（指数在原文损坏，按 CUDA 同构表推断，需查原文确认） |
| `j1f(x)` | 9 当 \|x\| < 8 时；否则最大绝对误差 2.2×10⁻⁶（同上） |
| `jnf(n,x)` | 当 n = 128 时，最大绝对误差 2.2×10⁻⁶（同上） |
| `y0f(x)` | 9 当 \|x\| < 8 时；否则最大绝对误差 2.2×10⁻⁶（同上） |
| `y1f(x)` | 9 当 \|x\| < 8 时；否则最大绝对误差 2.2×10⁻⁶（同上） |
| `ynf(n,x)` | ceil(2 + 2.5n) 当 \|x\| < n 时；否则最大绝对误差 2.2×10⁻⁶（同上） |
| `cyl_bessel_i0f(x)` | 8（全范围） |
| `cyl_bessel_i1f(x)` | 8（全范围） |
| `fmodf(x,y)` | 0（全范围） |
| `remainderf(x,y)` | 0（全范围） |
| `remquof(x,y,iptr)` | 0（全范围） |
| `modff(x,iptr)` | 0（全范围） |
| `fdimf(x,y)` | 0（全范围） |
| `truncf(x)` | 0（全范围） |
| `roundf(x)` | 0（全范围） |
| `rintf(x)` | 0（全范围） |
| `nearbyintf(x)` | 0（全范围） |
| `ceilf(x)` | 0（全范围） |
| `floorf(x)` | 0（全范围） |
| `lrintf(x)` | 0（全范围） |
| `lroundf(x)` | 0（全范围） |
| `llrintf(x)` | 0（全范围） |
| `llroundf(x)` | 0（全范围） |

#### 5.4.2.1.2 双精度浮点函数

双精度取整推荐 `rint()` 而非 `round()`：`round()` 映射为 **5 条指令**序列，`rint()` 为单条；`trunc()`、`ceil()`、`floor()` 也是单条。

**表 7：双精度数学标准库函数的最大 ULP 误差**

| 函数 | 最大 ulp 误差 |
|---|---|
| `x+y` | 0（IEEE-754 向最近偶数舍入） |
| `x*y` | 0（IEEE-754 向最近偶数舍入） |
| `x/y` | 0（IEEE-754 向最近偶数舍入） |
| `1/x` | 0（IEEE-754 向最近偶数舍入） |
| `sqrt(x)` | 0（IEEE-754 向最近偶数舍入） |
| `rsqrt(x)` | 1（全范围） |
| `cbrt(x)` | 1（全范围） |
| `rcbrt(x)` | 1（全范围） |
| `hypot(x,y)` | 3（全范围） |
| `rhypot(x,y)` | 2（全范围） |
| `norm3d(x,y,z)` | 2（全范围） |
| `rnorm3d(x,y,z)` | 1（全范围） |
| `norm4d(x,y,z,t)` | 2（全范围） |
| `rnorm4d(x,y,z,t)` | 1（全范围） |
| `norm(dim,arr)` | 无法提供误差界限（快速算法） |
| `rnorm(dim,arr)` | 无法提供误差界限（同上） |
| `exp(x)` | 1（全范围） |
| `exp2(x)` | 1（全范围） |
| `exp10(x)` | 1（全范围） |
| `expm1(x)` | 1（全范围） |
| `log(x)` | 1（全范围） |
| `log2(x)` | 1（全范围） |
| `log10(x)` | 1（全范围） |
| `log1p(x)` | 1（全范围） |
| `sin(x)` | 2（全范围） |
| `cos(x)` | 2（全范围） |
| `tan(x)` | 2（全范围） |
| `sincos(x,sptr,cptr)` | 2（全范围） |
| `sinpi(x)` | 2（全范围） |
| `cospi(x)` | 2（全范围） |
| `sincospi(x,sptr,cptr)` | 2（全范围） |
| `asin(x)` | 2（全范围） |
| `acos(x)` | 2（全范围） |
| `atan(x)` | 2（全范围） |
| `atan2(y,x)` | 2（全范围） |
| `sinh(x)` | 2（全范围） |
| `cosh(x)` | 2（全范围） |
| `tanh(x)` | 2（全范围） |
| `asinh(x)` | 3（全范围） |
| `acosh(x)` | 3（全范围） |
| `atanh(x)` | 2（全范围） |
| `pow(x,y)` | 2（全范围） |
| `erf(x)` | 2（全范围） |
| `erfc(x)` | 5（全范围） |
| `erfinv(x)` | 5（全范围） |
| `erfcinv(x)` | 7（全范围） |
| `erfcx(x)` | 6（全范围） |
| `normcdf(x)` | 5（全范围） |
| `normcdfinv(x)` | 9（全范围） |
| `lgamma(x)` | 4（区间 −23.0001⋯−2.2637 之外；区间内更大） |
| `tgamma(x)` | 10（全范围） |
| `fma(x,y,z)` | 0（IEEE-754 向最近偶数舍入） |
| `frexp(x,exp)` | 0（全范围） |
| `ldexp(x,exp)` | 0（全范围） |
| `scalbn(x,n)` | 0（全范围） |
| `scalbln(x,l)` | 0（全范围） |
| `logb(x)` | 0（全范围） |
| `ilogb(x)` | 0（全范围） |
| `j0(x)` | 7 当 \|x\| < 8 时；否则最大绝对误差 5×10⁻¹²（指数损坏，按 CUDA 同构表推断，需查原文确认） |
| `j1(x)` | 8 当 \|x\| < 8 时；否则最大绝对误差 5×10⁻¹²（同上） |
| `jn(n,x)` | 当 n = 128 时，最大绝对误差 5×10⁻¹²（同上） |
| `y0(x)` | 7 当 \|x\| < 8 时；否则最大绝对误差 5×10⁻¹²（同上） |
| `y1(x)` | 7 当 \|x\| < 8 时；否则最大绝对误差 5×10⁻¹²（同上） |
| `yn(n,x)` | 当 \|x\| > 1.5n 时，最大绝对误差 5×10⁻¹²（同上） |
| `cyl_bessel_i0(x)` | 8（全范围） |
| `cyl_bessel_i1(x)` | 8（全范围） |
| `fmod(x,y)` | 0（全范围） |
| `remainder(x,y)` | 0（全范围） |
| `remquo(x,y,iptr)` | 0（全范围） |
| `modf(x,iptr)` | 0（全范围） |
| `fdim(x,y)` | 0（全范围） |
| `trunc(x)` | 0（全范围） |
| `round(x)` | 0（全范围） |
| `rint(x)` | 0（全范围） |
| `nearbyint(x)` | 0（全范围） |
| `ceil(x)` | 0（全范围） |
| `floor(x)` | 0（全范围） |
| `lrint(x)` | 0（全范围） |
| `lround(x)` | 0（全范围） |
| `llrint(x)` | 0（全范围） |
| `llround(x)` | 0（全范围） |

### 5.4.2.2 内建函数

内建数学函数仅可在设备代码中调用。HGGC 为部分标准数学函数提供 `__` 前缀的内建版本（如 `__sinf(x)` 对应 `sinf(x)`），以减少原生指令数量换取更高执行速度，代价是精度降低。编译选项 **`--use_fast_math`** 会全局将下表函数替换为内建版本——这不仅影响精度，还可能改变边界条件（NaN、无穷大）的处理方式。

**建议：性能敏感代码中逐个函数评估是否切换内建版本，而非全局启用 `--use_fast_math`，以平衡速度和数值稳定性。**

**表 8：受 `--use_fast_math` 影响的函数**

| 运算符/函数 | 设备函数 |
|---|---|
| `x/y` | `__fdividef(x,y)` |
| `sinf(x)` | `__sinf(x)` |
| `cosf(x)` | `__cosf(x)` |
| `tanf(x)` | `__tanf(x)` |
| `sincosf(x,sptr,cptr)` | `__sincosf(x,sptr,cptr)` |
| `logf(x)` | `__logf(x)` |
| `log2f(x)` | `__log2f(x)` |
| `log10f(x)` | `__log10f(x)` |
| `expf(x)` | `__expf(x)` |
| `exp10f(x)` | `__exp10f(x)` |
| `powf(x,y)` | `__powf(x,y)` |
| `tanhf(x)` | `__tanhf(x)` |

#### 5.4.2.2.1 单精度浮点内建函数

- `__fadd_[rn,rz,ru,rd]()` 和 `__fmul_[rn,rz,ru,rd]()` 映射到编译器**从不合并为 FMAD** 的加法和乘法；而 `*` 和 `+` 运算符生成的加法乘法经常会被合并为 FMAD。
- 后缀：`_rn` 向最近偶数舍入；`_rz` 向零舍入；`_ru` 向上（正无穷）舍入；`_rd` 向下（负无穷）舍入。
- 浮点除法精度取决于 `-prec-div`：`-prec-div=false` 编译时，常规 `/` 与 `__fdividef(x,y)` 精度相同，但对 $2^{126} < |y| < 2^{128}$（指数损坏，按 CUDA 同构表推断，需查原文确认），`__fdividef` 返回零结果而 `/` 返回正确结果；该区间内若 x 是无穷大，`__fdividef` 返回 NaN（无穷大乘零）而 `/` 返回无穷大。`-prec-div=true` 编译或不带选项（默认 true）时 `/` 符合 IEEE。

**表 9：单精度浮点内建函数误差界限**（存疑的上标指数均以推断值给出并标注"需查原文确认"）

| 函数 | 误差界限 |
|---|---|
| `__fadd_[rn,rz,ru,rd](x,y)` | 符合 IEEE 标准 |
| `__fsub_[rn,rz,ru,rd](x,y)` | 符合 IEEE 标准 |
| `__fmul_[rn,rz,ru,rd](x,y)` | 符合 IEEE 标准 |
| `__fmaf_[rn,rz,ru,rd](x,y,z)` | 符合 IEEE 标准 |
| `__frcp_[rn,rz,ru,rd](x)` | 符合 IEEE 标准 |
| `__fsqrt_[rn,rz,ru,rd](x)` | 符合 IEEE 标准 |
| `__frsqrt_rn(x)` | 符合 IEEE 标准 |
| `__fdiv_[rn,rz,ru,rd](x,y)` | 符合 IEEE 标准 |
| `__fdividef(x,y)` | \|y\| 在 $[2^{-126}, 2^{126}]$ 范围内，最大 ulp 误差为 2（指数损坏，按 CUDA 同构表推断，需查原文确认） |
| `__expf(x)` | 最大 ulp 误差为 2 + floor(abs(1.173 * x)) |
| `__exp10f(x)` | 最大 ulp 误差为 2 + floor(abs(2.97 * x)) |
| `__logf(x)` | x 在 [0.5, 2] 内最大绝对误差 $2^{-21.41}$；否则最大 ulp 误差 3（指数推断，需查原文确认） |
| `__log2f(x)` | x 在 [0.5, 2] 内最大绝对误差 $2^{-22}$；否则最大 ulp 误差 2（同上） |
| `__log10f(x)` | x 在 [0.5, 2] 内最大绝对误差 $2^{-24}$；否则最大 ulp 误差 3（同上） |
| `__sinf(x)` | x 在 [−π, π] 内最大绝对误差 $2^{-21.41}$；否则更大（同上） |
| `__cosf(x)` | x 在 [−π, π] 内最大绝对误差 $2^{-21.19}$；否则更大（同上） |
| `__sincosf(x,sptr,cptr)` | 与 `__sinf(x)` 和 `__cosf(x)` 相同 |
| `__tanf(x)` | 源自其实现 `__sinf(x) * (1/__cosf(x))` |
| `__powf(x, y)` | 源自其实现 `exp2f(y * __log2f(x))` |
| `__tanhf(x)` | 当前实现最大相对误差 $2^{-11}$。即使 `-ftz=true`，此快速内建函数的非正规结果也不会被刷新为零（同上） |

#### 5.4.2.2.2 双精度浮点内建函数

`__dadd_rn()` 和 `__dmul_rn()` 映射到编译器从不合并为 FMAD 的加法和乘法；`*`/`+` 运算符生成的经常合并为 FMAD。

**表 10：双精度浮点内建函数**

| 函数 | 误差界限 |
|---|---|
| `__dadd_[rn,rz,ru,rd](x,y)` | 符合 IEEE 标准 |
| `__dsub_[rn,rz,ru,rd](x,y)` | 符合 IEEE 标准 |
| `__dmul_[rn,rz,ru,rd](x,y)` | 符合 IEEE 标准 |
| `__fma_[rn,rz,ru,rd](x,y,z)` | 符合 IEEE 标准 |
| `__ddiv_[rn,rz,ru,rd](x,y)` | 符合 IEEE 标准 |
| `__drcp_[rn,rz,ru,rd](x)` | 符合 IEEE 标准 |
| `__dsqrt_[rn,rz,ru,rd](x)` | 符合 IEEE 标准 |

> 比赛关联：
> - softmax 的 `expf`（2 ulp）、采样 logprob 的 `logf`（1 ulp）、GELU/SiLU 的 `tanhf`/除法是逐点热点；精度保持是评分维度，故**不建议**全局 `--use_fast_math`，可对激活函数单独换 `__expf`/`__tanhf` 并回归精度。
> - `rintf`（1 指令）替代 `roundf`（4 指令）适用于量化取整路径。
> - `__fmul_rn`/`__fadd_rn` 可阻止 FMAD 融合，用于需要与参考实现位级对齐的数值验证 kernel。
> - `-prec-div=true`（默认）保证除法 0 ulp；追求速度时 `-prec-div=false` 单精度除法 4 ulp 需评估精度影响。

---

# 5.5 计算能力

PPU 的计算能力与实际计算架构（**ppu001 / ppu0015**）相关。

## 5.5.1 查询 PPU 的计算能力

命令行通过 `ppu-smi` 查询 memory 等信息：

```bash
ppu-smi --query-ppu=timestamp,index,name,compute_mode,memory.total,memory.used --format=csv
```

运行时通过 HGGC 运行时 API `hggcDeviceGetAttribute()` 查询：

```cpp
#include <hggc_runtime_api.h>
int computeCapabilityMajor, computeCapabilityMinor;
hggcDeviceGetAttribute(&computeCapabilityMajor, hggcDevAttrComputeCapabilityMajor, device_id);
hggcDeviceGetAttribute(&computeCapabilityMinor, hggcDevAttrComputeCapabilityMinor, device_id);
```

Driver API 方式：

```cpp
#include <hggc.h>
int computeCapabilityMajor, computeCapabilityMinor;
hggcDeviceGetAttribute(&computeCapabilityMajor, HG_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MAJOR, device_id);
hggcDeviceGetAttribute(&computeCapabilityMinor, HG_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MINOR, device_id);
```

（注：第二段 driver API 示例原文函数名仍写 `hggcDeviceGetAttribute`，属性枚举为 `HG_DEVICE_ATTRIBUTE_*`，疑为 `hgDeviceGetAttribute` 笔误，需查原文确认。）

## 5.5.2 可用特性

**线程束/线程块限制**：

| 特性 | ppu001 | ppu0015 |
|---|---|---|
| 线程束 warp 大小 | 32 | 32 |
| 最大线程数/CU | 2048 | 2048 |
| 最大线程数/block | 1024 | 1024 |
| 单 block 最大 (x,y,z) 范围 | (1024,1024,128) | (1024,1024,128) |
| 单 grid 最大 (x,y,z) 范围 | (2147483647,2147483647,2147483647) | (2147483647,2147483647,2147483647) |

**片上内存容量**（全局内存容量与硬件 ARCH 和产品信息相关，下表为除全局内存外的各级片上内存）：

| 特性 | ppu001 | ppu0015 |
|---|---|---|
| VREG 总量/CU | 64K | 64K |
| 单 warp 最大 VREG 使用量 | 255 | 255 |
| 共享内存容量 | 256K | 256K |
| 共享内存 bank 数 | 32 | 32 |
| L1 缓存支持 | 是 | 是 |
| L2 缓存支持 | 是 | 是 |
| 常量内存支持 | 否 | 否 |
| LLC 缓存支持 | 是 | 是 |

**共享内存分组**（共享内存是同一线程块内所有线程共享的高速缓存内存）：

| PPU ARCH | 共享内存容量 (KB) | 共享内存分组 |
|---|---|---|
| ppu001 | 256 KB | 2 |
| ppu0015 | 256 KB | 4 |

**Tensor Cell 加速支持的输入数据类型**（Tensor Cell 功能可通过内联 TIX 的方式在 HGGC 编译工具链中利用）：

| PPU ARCH | TF32 | F32 | BF16 | FP16 | FP8 | FP4 | INT8 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| ppu001 | Yes | Yes | Yes | Yes | —（空白/不支持） | —（空白/不支持） | Yes |
| ppu0015 | Yes | Yes | Yes | Yes | Yes | Yes | Yes |

> 比赛关联（硬件预算一览，写 kernel 前先算这些数）：
> - **占用率上限**：每 CU 2048 线程 = 64 warp；单 block ≤1024 线程；每 CU 64K VREG、单 warp 最多 255 个寄存器 → 线程用 32 寄存器时可满驻留 2048 线程，用 64 寄存器则只能驻留 1024 线程（50% 占用率）。
> - **共享内存 256 KB/CU、32 bank、ppu0015 分 4 组（ppu001 分 2 组）**：bank 冲突分析与 smem tiling 按 32 bank 设计；分组数影响跨组访问的调度策略（ppu0015 更灵活）。
> - **常量内存不支持**（两代均为"否"）：`__constant__` 变量虽在语言层存在（5.2.2.2），但硬件无常量 cache——不要把频繁广播的参数指望在常量缓存上，应放共享内存或用 `__grid_constant__`/uniform 通路。
> - **数据类型路线选择**：目标 ppu001 时 FP8/FP4 无 Tensor Cell 加速，量化加速上限是 INT8；目标 ppu0015 时才可考虑 FP8/FP4（需内联 TIX）。BF16/FP16/TF32/F32/INT8 两代都支持，是稳妥主线。

---

# 附：本章关键速查

- 编译选项：`-std=c++<03/11/14/17/20>`、`--gpu-architecture ppu_10|ppu_15`、`--extended-lambda`（→ `__HGGCCC_EXTENDED_LAMBDA__`）、`--expt-relaxed-constexpr`（→ `__HGGCCC_RELAXED_CONSTEXPR__`）、`--no-host-device-initializer-list`、`--resource-usage`、`--maxrregcount <N>`、`-ftz=true`、`--use_fast_math`、`-prec-div=true/false`、`-prec-sqrt=true/false`、`-rdc=true`（分离编译）、`-DNDEBUG`。
- `__global__` 参数上限 **32764 字节**（经常量内存传递）；printf 缓冲区默认 **18 MB**；设备堆默认 **8 MB**；printf 单次最多 **32 个参数**。
- `__HGGC_ARCH__ = ppu_<version> × 10`（ppu_10 → 100，ppu_15 → 150）。
- warp = 32 线程；block ≤ 1024 线程；CU ≤ 2048 线程；VREG 64K/CU、≤255/warp；smem 256 KB、32 bank。
- Tensor Cell：BF16/FP16×FP32 累加形状 16x16x16 / 32x8x16 / 8x32x16；INT8→int 同形状；tf32 仅 16x16x8；FP8/FP4 仅 ppu0015。
