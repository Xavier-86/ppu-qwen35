# HGCC 编译器驱动程序 <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [1. 概述](#1-概述)
  - [1.1. hgcc 简介](#11-hgcc-简介)
  - [1.2. 编程模型](#12-编程模型)
  - [1.3. 源文件结构与编译方式](#13-源文件结构与编译方式)
- [2. 快速上手](#2-快速上手)
  - [2.1. 单文件编译](#21-单文件编译)
  - [2.2. 多文件分离编译（RDC）](#22-多文件分离编译rdc)
  - [2.3. 指定目标架构](#23-指定目标架构)
- [3. 编译流程与阶段](#3-编译流程与阶段)
  - [3.1. 编译流程](#31-编译流程)
  - [3.2. 编译阶段](#32-编译阶段)
  - [3.3. 输入文件类型](#33-输入文件类型)
  - [3.4. 编译阶段选项](#34-编译阶段选项)
- [4. 主机编译器要求](#4-主机编译器要求)
- [5. 命令行选项](#5-命令行选项)
  - [5.1. 选项语法](#51-选项语法)
  - [5.2. 选项列表](#52-选项列表)
  - [5.3. 环境变量](#53-环境变量)
  - [5.4. 目标架构（`--gpu-architecture`）](#54-目标架构-gpu-architecture)
- [6. 预定义宏](#6-预定义宏)
- [7. 分离编译](#7-分离编译)
  - [7.1. 使用方法](#71-使用方法)
  - [7.2. 库的链接](#72-库的链接)
  - [7.3. 链接时优化](#73-链接时优化)
  - [7.4. 注意事项](#74-注意事项)
- [8. 使用示例](#8-使用示例)
  - [8.1. 编译可执行文件](#81-编译可执行文件)
  - [8.2. RDC 编译](#82-rdc-编译)
- [9. 常见问题](#9-常见问题)
  - [9.1. hgcc报错：invalid value XXX for option -YYY, valid values are: AAA, BBB](#91-hgcc报错invalid-value-xxx-for-option-yyy-valid-values-are-aaa-bbb)
  - [9.2. hgcc报错：missing value for -XXX](#92-hgcc报错missing-value-for-xxx)
  - [9.3. hgcc报错：broken installation of hgcc](#93-hgcc报错broken-installation-of-hgcc)
  - [9.4. hgcc报错：don't know what to do with: XXX](#94-hgcc报错dont-know-what-to-do-with-xxx)


## 1. 概述

### 1.1. hgcc 简介

T-Head SAIL（以下简称 SAIL）`hgcc` 是 HGGC（HeteroGeneous General-purpose Computing）的编译驱动程序。它将 HGGC 源文件的多阶段编译过程封装为统一的命令行接口：开发者只需向 `hgcc` 传递常规编译选项（宏定义、头文件路径、库路径等），`hgcc` 负责在内部协调设备端编译和主机端编译。对于非 HGGC 的编译步骤，`hgcc` 会委派给系统 C++ 编译器处理，并自动将相关选项映射为该编译器可识别的命令行参数。

### 1.2. 编程模型

HGGC 面向如下应用：其控制部分运行在通用计算设备上，并使用一个或多个真武 PPU（以下简称 PPU）作为协处理器，以加速单程序多数据（SPMD）并行任务。

开发者调用设备端函数时，在常规 C++ 函数调用语法基础上附加参数，指定并行执行所需的 PPU 线程矩阵。主机端可在程序运行过程中多次下发并行计算任务。PPU 上的任务是自包含的——一旦下发，即由一组线程独立完成，无需主机端干预。设备端代码使用 C++ 扩展语法编写，通过注解区分函数的执行位置（主机端或设备端）以及数据的存储空间。

### 1.3. 源文件结构与编译方式

HGGC 源文件（通常以 `.hg` 为后缀）将主机代码和设备代码写在同一个文件中。`hgcc` 在编译时会自动完成两侧代码的分离和分别编译：

- **设备代码**：由 PPU 专有编译器和汇编器编译，最终打包进 fatbinary 文件
- **主机代码**：交由系统 C++ 编译器处理，fatbinary 映像会被嵌入到生成的主机目标文件中

链接阶段，`hgcc` 会自动链入 HGGC 运行时库。该库提供主机与 PPU 之间的交互能力，包括 PPU 内存缓冲区的分配、主机-设备间的数据传输，以及远程 SPMD 过程调用的支持。

## 2. 快速上手

### 2.1. 单文件编译

将单个 `.hg` 源文件编译为可执行文件：

```bash
hgcc my_file.hg -o my_file.out
```

### 2.2. 多文件分离编译（RDC）

当设备代码分布在多个源文件时，使用可重定位设备代码（RDC）模式：

```bash
hgcc -c -rdc true a.hg -o a.o
hgcc -c -rdc true b.hg -o b.o
hgcc a.o b.o -o final.out
```

### 2.3. 指定目标架构

通过 `--gpu-architecture`（`-arch`）选项指定目标 PPU 架构：

```bash
hgcc --gpu-architecture=ppu_10 my_file.hg -o my_file.out
```

更多编译模式和选项请参阅后续章节。

## 3. 编译流程与阶段

### 3.1. 编译流程

下图展示了 `hgcc` 从源文件到可执行文件的完整编译管线：

<figure style="text-align: center;">
  <img src="https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125155273/64b333933ae8a0620007c1fc4a807fc3/compile_pipeline.svg" alt="HGCC 编译流程图">
  <figcaption>HGCC 编译流程图</figcaption>
</figure>

编译过程分为以下几个阶段：

1. **设备端编译**：对输入源文件中的设备代码进行预处理，编译为 HGGC 二进制代码（hgbin）和/或 LLVM（Low Level Virtual Machine）bitcode，并打包进 fatbinary
2. **主机端编译**：对源文件进行主机端预处理，将 HGGC 特有的 C++ 扩展转换为标准 C++ 语法，同时嵌入上一步生成的 fatbinary
3. **主机目标文件生成**：由主机编译器将嵌入了 fatbinary 的主机代码编译为 `.o` 文件
4. **链接**：将主机目标文件与 HGGC 运行时库链接为最终可执行文件

程序运行时，HGGC 运行时会从 fatbinary 中提取与当前 PPU 架构匹配的设备代码。

默认的全程序编译模式要求所有设备代码位于同一编译单元中。若需跨文件引用设备符号，请参见 [第 7 节 分离编译](#7-分离编译)。

### 3.2. 编译阶段

开发者通过命令行选项和输入文件后缀名来选择 `hgcc` 的**编译阶段**（compilation phase）。`hgcc` 根据输入文件的后缀名判断待处理的文件类型，并根据用户指定的编译选项确定输出产物，两者共同确定 `hgcc` 应执行的阶段。

`hgcc --dryrun` 可以显示当前编译实际执行的内部步骤，用于调试目的。需要注意的是，`hgcc` 该输出仅用于调试参考，具体步骤可能随版本迭代变化，不应对其有任何依赖，比如，不应被直接将 `--dryrun` 的输出写入构建脚本——构建脚本应基于阶段级别的选项来驱动编译。

### 3.3. 输入文件类型

下表列出了 `hgcc` 根据文件后缀名识别的输入文件类型：

*表 1：hgcc 支持的输入文件类型*

| 后缀名    | 文件类型                      |
| :-------- | :---------------------------- |
| .hg       | HGGC source file              |
| .hggci    | HGGC device preprocess output |
| .o        | Object file                   |
| .a        | Library file                  |
| .cpp/.cxx | C++ source file               |
| .c        | C source file                 |
| .so       | Shared object file            |

### 3.4. 编译阶段选项

下表列出了各编译阶段对应的命令行选项及默认输出文件名（以输入文件 `a.hg` 为例）：

*表 2：hgcc 编译阶段选项*

| HGCC Option Name       |                | **Compile Phase**                                        | **Output File Name**         |
| :--------------------- | :------------- | :------------------------------------------------------- | :--------------------------- |
| **Long Name**          | **Short Name** |                                                          |                              |
| --hggc                 | -hggc          | HGGC compilation to C/C++ source file                    | a-hggc-ppu-{ppu-arch}.hggci  |
| --preprocess           | -E             | C/C++ preprocessing                                      | a.hggci                      |
| --compile              | -c             | C/C++ compilation to object file                         | a.o                          |
| --hgbin                | -hgbin         | hgbin generation from HGGC source files                  | a.hgbin                      |
| --fatbin               | -fatbin        | Fatbinary generation from source or hgbin files          | a.fatbin                     |
| --device-link          | -dlink         | Linking relocatable device code.                         | a-dlink.o                    |
| --device-link --hgbin  | -dlink -hgbin  | hgbin generation from linked relocatable device code.    | a-hggc-ppu-{ppu-arch}.out    |
| --device-link --fatbin | -dlink -fatbin | Fatbinary generation from linked relocatable device code | a-dlink.hgfb                 |
|                        |                | Linking an executable                                    | a.out                        |
| --lib                  | -lib           | Constructing an object file archive, or library          | a.a                          |
| --bc                   | -bc            | Compile all .hg source files to LLVM bitcode             | a-hggc-ppu-{ppu-arch}.bc     |
| --opt-bc               | -opt-bc        | Compile all .hg source files to optimized LLVM bitcode   | a-hggc-ppu-opt-{ppu-arch}.bc |

## 4. 主机编译器要求

`hgcc` 的编译流程依赖主机 C++ 编译器，既用于主机代码的编译和预处理，也用于执行非 HGGC 阶段的编译任务（运行阶段除外）。当前支持的主机编译器及版本范围如下：

| 编译器 | 支持版本   |
| :----- | :--------- |
| GCC    | 5.x – 15.x |
| Clang  | 9.x – 21.x |

`hgcc` 默认使用系统 PATH 中的 `gcc` / `g++`（其余平台暂未支持）。若主机编译器未安装在标准位置，需通过 `--compiler-bindir` 指定编译器路径，并确保相关环境配置正确。

!!! note
    `hgcc` 不支持超过操作系统最大路径长度限制的文件路径。

## 5. 命令行选项

### 5.1. 选项语法

`hgcc` 的命令行选项均提供长名称（双连字符前缀，如 `--compile`）和短名称（单连字符前缀，如 `-c`）两种等价写法。

按参数类型可分为三类：

- **布尔选项**：无需参数，出现即生效。例如 `--verbose`
- **单值选项**：接受一个参数值，仅可指定一次。例如 `--output-file <name>`
- **列表选项**：接受一个或多个参数值，可重复指定或用逗号分隔。例如 `--gpu-architecture ppu_10,ppu_15`

参数值可通过空格或等号（如 `-std=c++17`）与选项名分隔。对于 `-I`、`-l`、`-L` 等单字符选项，参数值可直接紧跟其后（如 `-I/usr/include`）。

### 5.2. 选项列表

*表 3：hgcc 命令行选项*

| 长选项                                           | 短名称                           | 参数/可选值                                                              | 说明                                                                                 |
| :----------------------------------------------- | :------------------------------- | :----------------------------------------------------------------------- | :----------------------------------------------------------------------------------- |
| `--archive-options`                              | `-Xarchive`                      |                                                                          | 将指定选项直接传递给主机端静态库打包工具                                             |
| `--archiver-binary`                              | `-arbin`                         | `<path>`                                                                 | 指定创建静态库时使用的归档工具路径，未指定时使用平台默认值                           |
| `--bc`                                           | `-bc`                            |                                                                          | 将 `.hg` 源文件编译为 LLVM bitcode                                                   |
| `--ccbin`                                        | `-ccbin`                         |                                                                          | `--compiler-bindir` 的别名                                                           |
| `--clean-targets`                                | `-clean`                         |                                                                          | 删除 hgcc 产生的非临时输出文件后退出                                                 |
| `--compile`                                      | `-c`                             |                                                                          | 将输入文件编译为目标文件（`.o`）                                                     |
| `--compile-as-tools-patch`                       | `-astoolspatch`                  |                                                                          | 以工具补丁模式编译，同时启用 `--keep-device-functions`                               |
| `--compiler-bindir`                              | `-compiler-bindir`               | `<path>`                                                                 | 指定主机编译器的路径或可执行文件名                                                   |
| `--compiler-options`                             | `-Xcompiler`                     | `<options>,...`                                                          | 透传选项给主机编译器/预处理器                                                        |
| `--compress-mode`                                | `-compress-mode`                 | `balance/default/none/size/speed`                                        | 控制 fatbinary 中设备代码的压缩策略                                                  |
| `--debug`                                        | `-g`                             |                                                                          | 在主机代码中插入调试信息                                                             |
| `--default-stream`                               |                                  | `legacy/per-thread`                                                      | 设置 HGGC 操作的默认 stream 行为                                                     |
| `--define-macro`                                 | `-D`                             | `<def>`                                                                  | 定义预处理宏                                                                         |
| `--dependency-output`                            | `-dependency-output`             | `<file>`                                                                 | 将依赖信息写入指定文件                                                               |
| `--dependency-target-name`                       | `-dependency-target-name`        | `<name>`                                                                 | 覆盖依赖规则中的目标名称                                                             |
| `--device-c`                                     | `-dc`                            |                                                                          | 编译为可重定位设备代码                                                               |
| `--device-debug`                                 | `-G`                             |                                                                          | 在设备代码中插入调试信息                                                             |
| `--device-entity-has-hidden-visibility`          |                                  | `false/true`                                                             | 隐式为设备实体添加 hidden 可见性属性                                                 |
| `--device-link`                                  | `-dlink`                         |                                                                          | 对可重定位设备代码执行设备端链接                                                     |
| `--disable-warnings`                             | `-w`                             |                                                                          | 关闭所有编译警告                                                                     |
| `--dlink-time-opt`                               | `-dlto`                          |                                                                          | 执行设备代码的链接时优化                                                             |
| `--dont-use-profile`                             | `-noprof`                        |                                                                          | 编译时不使用 hgcc.profiles 配置文件                                                  |
| `--dopt`                                         |                                  | `0/1/2/3`                                                                | 设置设备代码的优化等级                                                               |
| `--dryrun`                                       | `-dryrun`                        |                                                                          | 打印编译步骤但不实际执行                                                             |
| `--expt-extended-lambda`                         | `-extended-lambda`               |                                                                          | 启用在 lambda 表达式上使用 `__host__`/`__device__` 注解                              |
| `--expt-relaxed-constexpr`                       |                                  |                                                                          | 放宽 constexpr 函数的跨端调用限制                                                    |
| `--extended_lambda`                              |                                  |                                                                          | `--expt-extended-lambda` 的别名                                                      |
| `--fatbin`                                       | `-fatbin`                        |                                                                          | 从源文件或 hgbin 文件生成 fatbin                                                     |
| `--fdelayed-template-parsing`                    | `-fdelayed-template-parsing`     |                                                                          | 延迟到翻译单元末尾解析模板函数定义                                                   |
| `--fmad`                                         | `-fmad`                          | `false/true`                                                             | 是否将浮点乘加合并为融合乘加（FMA）指令                                              |
| `--forward-unknown-to-host-compiler`             | `-forward-unknown-to-host-compiler` |                                                                       | 将 hgcc 无法识别的选项转发给主机编译器                                               |
| `--forward-unknown-to-host-linker`               | `-forward-unknown-to-host-linker`   |                                                                       | 将 hgcc 无法识别的选项转发给主机链接器                                               |
| `--ftemplate-backtrace-limit`                    | `-ftemplate-backtrace-limit`     | `<limit>`                                                                | 限制模板实例化回溯的显示条数，0 为不限制                                             |
| `--ftemplate-depth`                              | `-ftemplate-depth`               | `<limit>`                                                                | 模板递归实例化的最大嵌套深度                                                         |
| `--ftz`                                          | `-ftz`                           | `false/true`                                                             | 是否将非正规浮点数（denormals）直接置零                                              |
| `--generate-dependencies`                        | `-M`                             |                                                                          | 仅生成头文件依赖信息并输出到 stdout                                                  |
| `--generate-dependencies-with-compile`           | `-MD`                            |                                                                          | 在编译的同时生成头文件依赖信息                                                       |
| `--generate-dependency-targets`                  | `-MP`                            |                                                                          | 为每个依赖项生成空目标规则                                                           |
| `--generate-line-info`                           | `-lineinfo`                      |                                                                          | 为设备代码生成行号信息                                                               |
| `--generate-nonsystem-dependencies`              | `-MM`                            |                                                                          | 同 `-M`，但排除系统头文件                                                            |
| `--generate-nonsystem-dependencies-with-compile` | `-MMD`                           |                                                                          | 同 `-MD`，但排除系统头文件                                                           |
| `--gpu-architecture`                             | `-arch`                          | `all/all-ppu/all-vm/ppu_10/ppu_15/vm_10/vm_15`                          | 指定目标 PPU 架构                                                                    |
| `--help`                                         | `-h`                             |                                                                          | 显示帮助信息                                                                         |
| `--hgbin`                                        | `-hgbin`                         |                                                                          | 从源文件生成 hgbin 设备二进制                                                        |
| `--hgfatbinary-options`                          | `-Xhgfatbin`                     | `<options>`                                                              | 透传选项给 fatbinary 打包工具                                                        |
| `--hggc`                                         | `-hggc`                          |                                                                          | 将 `.hg` 文件编译为 `.hggci` 输出                                                    |
| `--hggcfrontend-options`                         | `-Xhggcfe`                       | `<options>`                                                              | 透传选项给 hggc 前端                                                                 |
| `--hglink-options`                               | `-Xhglink`                       | `<options>`                                                              | 透传选项给设备链接器                                                                 |
| `--host-relocatable-link`                        | `-r`                             |                                                                          | 执行主机端可重定位链接                                                               |
| `--include-path`                                 | `-I`                             | `<path>,...`                                                             | 添加头文件搜索路径                                                                   |
| `--keep`                                         | `-keep`                          |                                                                          | 保留所有编译中间文件                                                                 |
| `--keep-device-functions`                        | `-keep-device-functions`         |                                                                          | 即使外部设备函数未被引用也保留其定义                                                 |
| `--keep-dir`                                     |                                  | `<directory>`                                                            | 将编译中间文件保存到指定目录                                                         |
| `--lib`                                          | `-lib`                           |                                                                          | 将输入编译并打包为静态库（`.a`）                                                     |
| `--library`                                      | `-l`                             | `<library>,...`                                                          | 链接指定的库（使用库名，不含 `lib` 前缀和后缀）                                      |
| `--library-path`                                 | `-L`                             | `<path>,...`                                                             | 添加库文件搜索路径                                                                   |
| `--libdevice-directory`                          | `-ldir`                          | `<path>`                                                                 | 指定 libdevice 库文件所在目录                                                        |
| `--linker-options`                               | `-Xlinker`                       | `<options>`                                                              | 透传选项给主机链接器                                                                 |
| `--list-gpu-arch`                                | `-arch-ls`                       |                                                                          | 列出所有支持的虚拟架构后退出                                                         |
| `--list-gpu-code`                                | `-code-ls`                       |                                                                          | 列出所有支持的物理架构后退出                                                         |
| `--llvm-options`                                 | `-Xllvm`                         | `<options>`                                                              | 透传选项给 LLVM 后端                                                                 |
| `--lto`                                          | `-lto`                           |                                                                          | `--dlink-time-opt` 的别名                                                            |
| `--m64`                                          |                                  |                                                                          | 等价于 `--machine=64`                                                                |
| `--machine`                                      | `-m`                             | `64`                                                                     | 指定目标机器字长                                                                     |
| `--maxrregcount`                                 | `-maxrregcount`                  | `<amount>`                                                               | 限制每个设备函数可使用的寄存器数量上限                                               |
| `--MF`                                           | `-MF`                            |                                                                          | `--dependency-output` 的别名                                                         |
| `--mllvm`                                        | `-mllvm`                         |                                                                          | `--llvm-options` 的别名                                                              |
| `--MT`                                           | `-MT`                            |                                                                          | `--dependency-target-name` 的别名                                                    |
| `--no-compress`                                  | `-no-compress`                   |                                                                          | 禁用 fatbinary 中的代码压缩                                                          |
| `--no-device-link`                               | `-nodlink`                       |                                                                          | 链接时跳过设备端链接步骤                                                             |
| `--no-exceptions`                                | `-noeh`                          |                                                                          | 在主机代码中禁用 C++ 异常处理                                                        |
| `--no-simt`                                     | `-no-simt`                       |                                                                          | 禁用 PPU 的 SIMT 分支                                                                |
| `--opt-bc`                                       | `-opt-bc`                        |                                                                          | 将 `.hg` 源文件编译为优化后的 LLVM bitcode                                           |
| `--optimize`                                     | `-O`                             | `0/1/2/3`                                                                | 设置主机代码的优化等级                                                               |
| `--options-file`                                 | `-optf`                          | `<file>,...`                                                             | 从文件中读取附加的命令行选项                                                         |
| `--output-directory`                             | `-odir`                          | `<directory>`                                                            | 指定输出文件所在目录                                                                 |
| `--output-file`                                  | `-o`                             | `<file name>`                                                            | 指定输出文件的路径和名称                                                             |
| `--pre-include`                                  | `-include`                       | `<file>,...`                                                             | 在编译前强制包含指定头文件                                                           |
| `--prec-div`                                     | `-prec-div`                      | `false/true`                                                             | 单精度除法是否遵循 IEEE 舍入规则                                                     |
| `--prec-sqrt`                                    | `-prec-sqrt`                     | `false/true`                                                             | 单精度平方根是否遵循 IEEE 舍入规则                                                   |
| `--preprocess`                                   | `-E`                             |                                                                          | 仅执行预处理，不编译                                                                 |
| `--preprocess-options`                           | `-Xpreprocess`                   | `<options>`                                                              | 透传选项给预处理器                                                                   |
| `--profile`                                      | `-pg`                            |                                                                          | 生成用于 gprof 的性能分析信息                                                        |
| `--relocatable-device-code`                      | `-rdc`                           | `false/true`                                                             | 控制是否生成可重定位设备代码                                                         |
| `--resource-usage`                               | `-res-usage`                     |                                                                          | 报告设备代码的寄存器和内存占用情况                                                   |
| `--restrict`                                     | `-restrict`                      |                                                                          | 将所有 kernel 的指针参数视为 restrict 指针                                           |
| `--run`                                          | `-run`                           |                                                                          | 编译、链接后立即运行生成的可执行文件                                                 |
| `--run-args`                                     |                                  | `<arguments>,...`                                                        | 配合 `--run` 使用，传递程序运行参数                                                  |
| `--save_temps`                                   | `-save_temps`                    |                                                                          | `--keep` 的别名                                                                      |
| `--shared`                                       | `-shared`                        |                                                                          | 链接时生成动态共享库                                                                 |
| `--static-global-template-stub`                  | `-static-global-template-stub`   | `false/true`                                                             | 控制是否使用静态全局模板桩（stub）                                                   |
| `--std`                                          | `-std`                           | `<value>`                                                                | 指定 C++ 语言标准（如 `c++17`）                                                      |
| `--system-include`                               | `-isystem`                       | `<path>,...`                                                             | 添加系统头文件搜索路径                                                               |
| `--threads`                                      | `-t`                             | `<number>`                                                               | 编译时使用的最大并行线程数                                                           |
| `--time`                                         | `-time`                          | `<file>`                                                                 | 生成各编译阶段耗时的 CSV 报表                                                        |
| `--undefine-macro`                               | `-U`                             | `<u>`                                                                    | 取消已定义的预处理宏                                                                 |
| `--use-fast-math`                                | `-use-fast-math`                 |                                                                          | 启用快速数学运算，等价于 `--ftz=true --prec-div=false --prec-sqrt=false --fmad=true` |
| `--verbose`                                      | `-v`                             |                                                                          | 打印编译器驱动执行的每条命令                                                         |
| `--version`                                      | `-V`                             |                                                                          | 打印版本信息                                                                         |
| `--Wdefault-stream-launch`                       | `-Wdefault-stream-launch`        |                                                                          | kernel launch 未指定 stream 时产生警告                                               |
| `--Werror`                                       | `-Werror`                        | `all-warnings/default-stream-launch/missing-launch-bounds/reorder`       | 将指定类型的警告提升为错误                                                           |
| `--Wmissing-launch-bounds`                       | `-Wmissing-launch-bounds`        |                                                                          | `__global__` 函数缺少 `__launch_bounds__` 注解时产生警告                             |
| `--Wreorder`                                     | `-Wreorder`                      |                                                                          | 成员初始化顺序与声明顺序不一致时产生警告                                             |
| `--x`                                            | `-x`                             | `c/c++/cu/hg`                                                            | 强制指定输入文件的语言类型                                                           |

比赛关联：性能敏感的自定义算子（如量化 GEMM、decode 路径 kernel）应重点关注 `--dopt`（设备优化等级）、`--fmad`/`--ftz`/`--prec-div`/`--prec-sqrt`/`--use-fast-math`（浮点快速数学）、`--maxrregcount`（寄存器压力与 occupancy）、`--restrict` 和 `--no-simt`；`--compress-mode`/`--no-compress` 影响 fatbinary 体积与加载时间，进而影响 TTFT。

### 5.3. 环境变量

`hgcc` 支持两个环境变量，用于在不修改构建脚本的前提下向所有编译命令注入全局选项：

- **`HGCC_PREPEND_FLAGS`**：其中的选项会被插入到正常 `hgcc` 命令行参数前。
- **`HGCC_APPEND_FLAGS`**：其中的选项会被追加到正常 `hgcc` 命令行参数后。

**示例**：在不修改构建脚本的前提下，统一注入全局编译参数：

```bash
export HGCC_PREPEND_FLAGS='-G -keep -arch=ppu_10'
export HGCC_APPEND_FLAGS='-DNAME=" foo "'
```

此后，执行 `hgcc foo.hg -o foo` 时，实际生效的命令行为：

```
hgcc -G -keep -arch=ppu_10 foo.hg -o foo -DNAME=" foo "
```

### 5.4. 目标架构（`--gpu-architecture`）

`--gpu-architecture`（`-arch`）选项指定编译目标的 PPU 架构。`hgcc` 支持两类架构标识：

| 类型                | 架构标识 | 含义                                                                      |
| ------------------- | -------- | ------------------------------------------------------------------------- |
| 真实架构（real）    | `ppu_XX` | 编译为目标硬件可直接执行的 hgbin 二进制代码                               |
| 虚拟架构（virtual） | `vm_XX`  | 编译为 LLVM bitcode 中间表示，运行时由驱动程序 JIT 编译为目标硬件的 hgbin |

真实架构用于已知目标硬件的场景，生成的代码性能最优但仅能在对应架构上运行。虚拟架构生成的 LLVM bitcode 具有前向兼容性，可在未来的 PPU 架构上通过 JIT 编译执行，但首次加载时存在编译开销。

#### 与 Clang `--ppu-arch` 选项的对应关系

| hgcc `-arch` | clang `--ppu-arch` | 说明                |
| :----------- | :----------------- | :------------------ |
| `ppu_10`     | `ppu001`           | 第一代真武 PPU 架构 |
| `ppu_15`     | `ppu0015`          | 第二代真武 PPU 架构 |

比赛关联：已知比赛服务器 PPU 型号时应直接编译真实架构（如 `ppu_10`/`ppu_15`），避免虚拟架构 JIT 的首次加载开销（直接影响 TTFT）；若需兼容多代硬件，可用 `-arch ppu_10,ppu_15` 或 `all-ppu` 打包多个 hgbin 进同一 fatbinary。

## 6. 预定义宏

`hgcc` 编译 HGGC 源文件时会自动定义以下预处理宏，可用于条件编译：

| 宏名称                         | 定义条件                                                                                       |
| :----------------------------- | :--------------------------------------------------------------------------------------------- |
| `__HGGC__`                     | 编译 C/C++/HGGC 源文件时定义                                                                   |
| `__HGGCCC__`                   | 编译 HGGC 源文件时定义                                                                         |
| `__HGGCCC_RDC__`               | 以可重定位设备代码模式编译时定义（参见 [第 7 节 分离编译](#7-分离编译)）                       |
| `__HGGCCC_RELAXED_CONSTEXPR__` | 使用 `--expt-relaxed-constexpr` 选项时定义（详见 [HGGC C++ Programming Guide](../ppu_hggc/)）  |
| `__HGGCCC_EXTENDED_LAMBDA__`   | 使用 `--expt-extended-lambda` 或 `--extended-lambda` 时定义（详见 [HGGC C++ Programming Guide](../ppu_hggc/)） |
| `__HGGCCC_VER_MAJOR__`         | `hgcc` 主版本号（整数）                                                                        |
| `__HGGCCC_VER_MINOR__`         | `hgcc` 次版本号（整数）                                                                        |
| `__HGGCCC_VER_BUILD__`         | `hgcc` 构建版本号（整数）                                                                      |


## 7. 分离编译

默认的全程序编译模式要求所有设备代码位于同一个源文件中。当项目规模增大、需要将设备代码分散到多个源文件中时，可以使用**分离编译**（Separate Compilation）模式。

### 7.1. 使用方法

启用分离编译需在编译阶段和链接阶段分别指定相关参数。

**编译阶段**：使用 `--device-c`（或等价的 `--relocatable-device-code=true --compile`）将源文件编译为包含可重定位设备代码的目标文件：

```bash
hgcc --device-c a.hg -o a.o
hgcc --device-c b.hg -o b.o
```

**链接阶段**：将目标文件交给 `hgcc` 完成设备链接和主机链接：

```bash
hgcc a.o b.o -o output
```

`hgcc` 会自动调用设备链接器（`hglink`）合并所有可重定位设备代码，再由主机链接器完成最终链接。如果没有检测到可重定位设备代码，设备链接器不会执行任何操作。

如需单独执行设备链接步骤，可使用 `--device-link` 选项，其输出是一个包含可执行设备代码的主机目标文件，后续仍需交给主机链接器处理：

```bash
hgcc --device-link a.o b.o -o dlink.o
```

分离编译模式下，`hgcc` 将可重定位设备代码（而非可执行设备代码）嵌入到主机目标文件中。设备端符号的可见性遵循 C++ 的 `extern` / `static` 规则——`extern` 符号可跨文件引用，`static` 符号仅在当前编译单元可见，因此不同文件中可以定义同名的 `static` 设备端符号。

生成可重定位设备代码还是可执行设备代码，由 `--relocatable-device-code` 选项控制。

### 7.2. 库的链接

设备链接器能够读取静态库（`.a`），但会忽略动态库（`.so`）。

使用 `--library` 和 `--library-path` 向设备链接器和主机链接器同时指定库：

```bash
hgcc --gpu-architecture=ppu_10 a.o b.o --library-path=<path> --library=foo
```

!!! note
    设备链接器会跳过不包含可重定位设备代码的目标文件。

### 7.3. 链接时优化

分离编译产生的代码可能因跨文件内联受限而损失部分性能。如需优化，可通过 `--dlink-time-opt`（或 `-dlto`）选项启用**链接时优化**（Link-Time Optimization, LTO）：

```bash
hgcc --device-c -dlto a.hg -o a.o
hgcc --device-c -dlto b.hg -o b.o
hgcc -dlto a.o b.o -o output
```

`-dlto` 选项在编译和链接阶段均需指定。支持部分文件使用 `-dlto`：带此选项的文件将被统一优化，其余文件按常规方式链接。

启用 LTO 后，部分优化工作从编译阶段转移到链接阶段，大规模代码库可能出现链接耗时增加的情况。

比赛关联：大型推理工程把设备 kernel 拆到多个编译单元时应启用 RDC，并用 `-dlto` 找回跨文件内联损失的性能，避免 kernel 吞吐受损。

### 7.4. 注意事项

#### 7.4.1. 目标文件兼容性

可重定位设备代码的链接需满足：

- 所有目标文件使用相同的 ABI 版本
- 目标 PPU 架构一致
- 链接器的 toolkit 版本不低于目标文件的 toolkit 版本

使用 `-dlto` 时，LTO IR 中间表示仅在同一主版本号内兼容。

通过 `launch_bounds` 或 `--maxrregcount` 限制了寄存器数量的 kernel，其调用的所有函数也必须遵守该限制，否则会产生链接错误。

## 8. 使用示例

### 8.1. 编译可执行文件

```bash
hgcc my_file.hg -o my_file.out
```

### 8.2. RDC 编译

在有多个编译单元，并且多个编译单元中的设备端代码也需要进行链接时，可以使用`rdc`的编译方式，如下是一种典型的使用方法

```bash
hgcc -c -rdc true a.hg -o a.o
hgcc -c -rdc true b.hg -o b.o
hgcc a.o b.o -o final.out
```

## 9. 常见问题

### 9.1. hgcc报错：invalid value XXX for option -YYY, valid values are: AAA, BBB

传给 YYY 选项的值非法，合法值在 AAA，BBB 中

### 9.2. hgcc报错：missing value for -XXX

XXX 选项是个需要值的选项，用户使用时未对该选项赋值

### 9.3. hgcc报错：broken installation of hgcc

`hgcc`无法定位部分必要组件，请确认`SAIL`的`clang`和`libppudevice`存在于`PPU_SDK`环境变量指向的路径中

### 9.4. hgcc报错：don't know what to do with: XXX

未通过`-x`指定文件类型时，`hgcc`会默认通过文件的后缀名来判断如何编译当前文件。假设输入的文件名不是以`.cpp/.c/.o/.hggci/.hg`结尾，`hgcc`就会报错。
