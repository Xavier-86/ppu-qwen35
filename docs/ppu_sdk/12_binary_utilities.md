# 二进制工具与 hgFatbinary <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [1. 二进制工具概述](#1-二进制工具概述)
  - [1.1 PPU Binary](#11-ppu-binary)
  - [1.2 二进制工具对比](#12-二进制工具对比)
  - [1.3 快速入门](#13-快速入门)
- [2. hgobjdump](#2-hgobjdump)
  - [2.1 简介](#21-简介)
  - [2.2 使用方式](#22-使用方式)
  - [2.3 命令行参数](#23-命令行参数)
  - [2.4 示例](#24-示例)
- [3. hgbat](#3-hgbat)
  - [3.1 简介](#31-简介)
  - [3.2 使用方式](#32-使用方式)
  - [3.3 命令行参数](#33-命令行参数)
  - [3.4 示例](#34-示例)
- [4. hgprune](#4-hgprune)
  - [4.1 简介](#41-简介)
  - [4.2 使用方式](#42-使用方式)
  - [4.3 命令行参数](#43-命令行参数)
- [5. hgFatbinary 概述](#5-hgfatbinary-概述)
  - [5.1 核心功能](#51-核心功能)
  - [5.2 工作流程](#52-工作流程)
  - [5.3 使用简介](#53-使用简介)
- [6. hgfatbinary 命令行工具](#6-hgfatbinary-命令行工具)
  - [6.1 命令行选项](#61-命令行选项)
  - [6.2 命令行使用示例](#62-命令行使用示例)
- [7. libhgfatbin 使用说明](#7-libhgfatbin-使用说明)
  - [7.1 libhgfatbin API](#71-libhgfatbin-api)
  - [7.2 libhgfatbin 错误码](#72-libhgfatbin-错误码)
  - [7.3 API 调用示例](#73-api-调用示例)


T-Head SAIL（以下简称 SAIL）SDK 提供了一系列二进制工具，用于 PPU 平台的二进制分析与处理。工具包括：

- **hgobjdump**：解析 HGGC 格式的 Binary，提取 Device 端信息并以可读形式展示
- **hgbat**：对 Device 端代码进行静态分析，支持反汇编、控制流图生成和寄存器生命周期分析
- **hgprune**：裁剪可重定位二进制文件或静态库，移除不需要的 PPU target
- **hgfatbinary**：fatbinary 构建工具，将不同 PPU 架构的设备代码打包到单一文件中

## 1. 二进制工具概述

### 1.1 PPU Binary

T-Head SAIL SDK 编译工具链生成的二进制文件（包括可执行文件和动态链接库）同时包含运行于 CPU 的 Host 代码以及运行于真武 PPU（以下统称 PPU）的 Device 代码。因此，从逻辑结构上看，编译产物由 Host Binary 和 Device Binary 两部分组成，二者共同构成完整的 PPU Binary。

PPU Binary 采用通用 ELF（Executable and Linkable Format）格式，并在整体格式上与 64 位 x86_64 ELF 保持兼容。为支持在 Host Binary 中嵌入 Device Binary，文件中新增了 .hggc_fatbin 段，用于存放 Device Binary 数据。独立的 Device Binary 同样采用 ELF 格式，其大部分段的定义和使用方式与标准 ELF 保持一致；与此同时，还引入了若干 hggc_info 类型的 section，用于保存运行时所需的元数据信息。其中，全局信息保存在 .hg_info 段中，各个 kernel 对应的信息分别保存在各自的 .hg_info.<name> 段中，其中后缀 <name> 为对应 kernel 的 mangled name。

### 1.2 二进制工具对比

下表列出 `hgobjdump` 和 `hgbat` 的功能对比，按 PPU 平台特色功能优先排列：

*表 1. hgobjdump 和 hgbat 的功能对比*

| 功能                     | hgobjdump | hgbat | 备注                                        |
| ------------------------ | :-------: | :---: | ------------------------------------------- |
| 寄存器生命周期分析       |     —     | 支持  | 支持 sreg/vreg 分别展示，可按需隐藏任一类型 |
| 控制流图生成（DOT 格式） |     —     | 支持  | 可配合 Graphviz 生成可视化图形              |
| 反汇编 HGBIN             |   支持    | 支持  |                                             |
| 从主机文件提取 HGBIN/BC  |   支持    |   —   | 支持 ELF 可执行文件、.so、.a 等格式         |
| 符号表查询               |   支持    |   —   | 按 ELF 文件索引输出                         |
| 资源用量查询             |   支持    |   —   | 输出 kernel 级寄存器数、共享内存等信息      |

### 1.3 快速入门

根据使用场景选择对应工具：

- **查看 Binary 中包含哪些 device function**：使用 `hgobjdump -l`
- **反汇编查看指令**：使用 `hgobjdump --isa`（ISA，Instruction Set Architecture）（支持主机文件）或 `hgbat -i`（独立 HGBIN）
- **从可执行文件/动态库中提取独立 HGBIN**：使用 `hgobjdump -x`
- **生成控制流图进行结构分析**：使用 `hgbat -c`，结合 `dot` 工具可视化
- **分析寄存器压力与活跃区间**：使用 `hgbat -r`，配合 `--live-range-mode` 选择输出粒度
- **裁剪库中不需要的 PPU target**：使用 `hgprune`

## 2. hgobjdump

### 2.1 简介

`hgobjdump` 可以从 PPU Binary 中获取信息，并以清晰易读的格式输出其中的信息。`hgobjdump` 的输出包括：每一个 kernel function 的汇编代码、resource usage、symbol table 等，并且可以从打包好的可执行文件提取出独立的 PPU Binary，该独立 Binary 也可以直接用 GNU Binary Utilities 进行分析。

适用输入包括：

- ELF 可执行文件
- 目标文件 `.o`
- 静态库 `.a`
- 共享库 `.so`
- 其他包含 PPU 二进制代码（HGBIN）嵌入段的 HOST 二进制文件

### 2.2 使用方式

每次调用 `hgobjdump` 时指定一个输入文件即可，命令格式为：

```bash
hgobjdump [options] <input object file>
```

以下按操作类型分组说明常见用法。

#### 2.2.1. 查询类操作

列出文件中包含的 ELF 文件及其 device function 列表：

```bash
hgobjdump -l hggc.out
```

同时显示函数的 demangled name：

```bash
hgobjdump -l --demangle hggc.out
```

查看某个函数的资源使用信息（需使用 mangled name），或查看全部函数的资源信息：

```bash
hgobjdump -i=_Z4MathPfS_ hggc.out
hgobjdump -i=all hggc.out
```

查看某个 ELF 文件的符号表（通过索引指定），或查看全部符号表：

```bash
hgobjdump -s=1 hggc.out
hgobjdump -s=0 hggc.out
```

#### 2.2.2. 提取类操作

从主机文件中提取指定索引的独立 ELF（可先用 `-l` 查看索引），或提取全部：

```bash
hgobjdump -x=1 hggc.out
hgobjdump -x=0 hggc.out
```

#### 2.2.3. 反汇编操作

反汇编文件中所有 Device 代码（输出 ISA 汇编）：

```bash
hgobjdump --isa hggc.out
```

仅反汇编指定函数（需使用 mangled name）：

```bash
hgobjdump --func=_Z4MathPfS_ hggc.out
```

### 2.3 命令行参数

下表包含了支持的 `hgobjdump` 命令行选项，以及每个选项功能的描述。每个选项都有一个长名称和至少一个短名称，可以互换使用。

| 长选项                                   | 短选项             | 说明                                                                                                    |
| --------------------------------------- | ------------------ | ------------------------------------------------------------------------------------------------------ |
| `--list-elf`                            | `-l`               | 列出 fatbin 中包含的所有 ELF 文件以及其中可用的 kernel function。                                         |
| `--list-all`                            | `--lall`           | 列出 fatbin 中所有可用的 device function。该选项隐含启用 `list elf`。                                     |
| `--list-bc`                             | `--lbc`, `-b`      | 列出 fatbin 中所有可用的 device function。                                                               |
| `--extract-elf=<elf idx>`               | `-x`               | 根据文件索引提取 ELF 文件并保存。使用 `0` 表示提取所有文件。可先通过 `-l` 获取 ELF 文件列表。                 |
| `--extract-bc=<bc idx>`                 | `--xbc`            | 根据文件索引提取 llvm-bc 文件并保存。使用 `0` 表示提取所有 bc 文件。可先通过 `--lbc` 获取 bc 文件列表。       |
| `--dump-elf`                            | `-e`               | 输出 ELF 对象中的函数段内容。                                                                             |
| `--dump-isa`                            | `--isa`, `-a`      | 输出单个 hgbin 文件或二进制中嵌入的所有 hgbin 文件的汇编代码。                                              |
| `--dump-function=<function name>`       | `--func`, `-f`     | 输出指定函数的内容（必须使用 mangled name）。                                                             |
| `--line-numbers`                        | `--line`, `-n`     | 在反汇编结果中显示源代码行号。该选项隐含启用 ISA 反汇编。                                                   |
| `--dump-resource-usage=<function name>` | `--res-usage`, `-i`| 输出指定函数（必须使用 mangled name）的资源使用信息。使用 `all` 表示输出所有函数的资源使用信息。              |
| `--dump-elf-symbols=<elf idx>`          | `--symbols`, `-s`  | 根据 ELF 文件索引输出其符号表名称。使用 `0` 表示输出所有文件。可先通过 `-lelf` 获取 ELF 文件列表。            |
| `--demangle`                            | `-d`               | 对 `--list-elf` 输出的函数名进行反修饰显示。                                                              |
| `--help`                                | `-h`               | 打印该工具的帮助信息。                                                                                   |

### 2.4 示例

```bash
$ hgobjdump -l hggc.out
hggc.out:    file format elf64-x86-64

ELF FILE 1 (PPU 1.0) (SIMT):
Func 1: _Z4MathPfS_
```
```bash
$ hgobjdump -l --demangle hggc.out
hggc.out:    file format elf64-x86-64

ELF FILE 1 (PPU 1.0) (SIMT):
Func 1: Math(float*, float*)
```
```bash
$ hgobjdump --isa hggc.out
hggc.out:    file format elf64-x86-64

ELF FILE 1 (PPU 1.0) (SIMT):

Disassembly of section .text:

0000000000000110 _Z4MathPfS_:
     110: 00 00 00 00 00 00 f1 08          s.wait    pipe_flush
     118: 00 00 00 00 20 08 88 56          v.mov.alllane.b32    vreg32, 0x0
     120: 00 00 00 00 60 48 08 50          v.mov.b32    vreg33, 0x0
     128: ff 0f 00 00 20 09 00 26          s.and.b32    sreg0, sreg36, 0xfff
     130: 00 00 00 00 00 09 c0 57          v.tid.init    vreg0, sreg[36:37]
     ...
```
```bash
$ hgobjdump -x=1 libacompute.so
libacompute.so:    file format elf64-x86-64

ELF FILE 1 (PPU 1.0) (SIMT):
Extract File: libacompute.so_ELF_File_1_PPU10
```
```bash
$ hgobjdump -l libacompute.so_ELF_File_1_PPU10
libacompute.so_ELF_File_1_PPU10:    file format ELF64-ppu
Func 1: _Z11mm_kernelTTIdddEvPKPT0_PKPKT_S8_iiiff
Func 2: _Z11mm_kernelNTIdddEvPKPT0_PKPKT_S8_iiiff
Func 3: _Z11mm_kernelNNIfffEvPKPT0_PKPKT_S8_iiiff
```
```bash
$ hgobjdump --func=_Z11mm_kernelTTIdddEvPKPT0_PKPKT_S8_iiiff libacompute.so_ELF_File_1_PPU10
libacompute.so_ELF_File_1_PPU10:    file format ELF64-ppu

Disassembly of section .text:

00000000000036c8 _Z11mm_kernelTTIdddEvPKPT0_PKPKT_S8_iiiff:
    36c8: 00 00 00 00 20 00 04 50          v.mov.b32    vreg16, 0x0
    36d0: 00 00 00 00 20 80 04 50          v.mov.b32    vreg18, 0x0
    36d8: 00 00 00 00 20 40 04 50          v.mov.b32    vreg17, 0x0
    36e0: 00 00 00 00 20 40 01 50          v.mov.b32    vreg5, 0x0
    36e8: 00 00 00 00 00 00 f1 08          s.wait    pipe_flush
    36f0: 00 00 00 00 20 00 88 56          v.mov.alllane.b32    vreg32, 0x0
    ...
```
```bash
$ hgobjdump -i=_Z11mm_kernelTTIdddEvPKPT0_PKPKT_S8_iiiff libacompute.so_ELF_File_1_PPU10
libacompute.so_ELF_File_1_PPU10:    file format ELF64-ppu

RESOURCE INFO:
SHADER ABI KERNEL CONTROL:
grid_dim_x_en:1
grid_dim_y_en:1
grid_dim_z_en:1
block_dim_en:1
block_idx_x_en:1
block_idx_y_en:1
block_idx_z_en:1
start_thread_idx_en:1
user_sreg_num:32
pri:0
fwd_progress:0
private_en:1
cu_disp_en:0
block_age_en:0

SHADER ABI KERNEL MODE:
fp_rndmode:0
i_rndmode:0
fp_denorm_flush:0
saturation:0
exception_en:0
relu:0
nan:0
vmem_ooo:0
saturation_fp64:0
trap_exception:0
debug_en:0
trap_en:0
perf_cnt_en:0
kp_modify_en:0
sw_defined_mode:0

SHADER ABI KERNEL RESOURCE:
vreg_number:34
sreg_number:48
shared_memory_size:130
treg_en:0

STACK SIZE:0

ARGUMENT:
ARG0 INDEX:hidden        TYPE:uint64        KIND:hidden.gm.base     sreg[0:1]
ARG1 INDEX:hidden        TYPE:uint64        KIND:hidden.env.base    sreg[2:3]
ARG2 INDEX:hidden        TYPE:uint64        KIND:hidden.km.base     sreg[4:5]
ARG3 INDEX:hidden        TYPE:uint32        KIND:hidden.pm.size     sreg6
ARG4 INDEX:hidden        TYPE:uint32        KIND:hidden.tsm.size    sreg7
```
```bash
$ hgobjdump -s=0 test_hggc-math.math.float_math_op1_expf
test_hggc-math.math.float_math_op1_expf:        file format elf64-x86-64
ELF FILE 1 (PPU 1.0) (SIMT):
SYMBOL TABLE:
00000000000001c0 l     O .data  00000030 _ZN13heapallocatorL9heapAllocE.13
00000000000001a8 l     O .data  00000018 _ZN13heapallocatorL8heapPropE.12
0000000000001d38 g     F .text  00000020 __ppumath_fma_rtp_f32
00000000000000a0 l     O .data  00000010 _ZN13heapallocatorL8hashPropE
```

比赛关联：`hgobjdump -i=all` 给出的 vreg/sreg 数量、shared_memory_size、STACK SIZE 直接决定 kernel 的 occupancy 与显存占用，是自研算子（如量化 GEMM、attention kernel）调优时检查寄存器压力的第一手数据；`--isa` 反汇编可核对编译器是否生成了预期的向量/张量指令。

## 3. hgbat

### 3.1 简介

`hgbat` 是 HGBIN 的静态分析工具，通过该工具，可以自动提取并理解 PPU Binary Device 端代码的结构与行为，包括其中的指令集架构（ISA），并生成相应的控制流图（CFG）和寄存器的活跃范围（register live range）。它目前只接受独立的 PPU Binary，适合进行二进制分析、调试和性能研究。

### 3.2 使用方式

基本用法如下：

```bash
hgbat [options] <executable>
```

其中：

- `<executable>` 表示待分析的可执行文件
- `[options]` 表示命令行参数，用于控制输出内容和分析方式

列出可执行文件中的所有 device function

```bash
hgbat --list-elf a.out
```

或：

```bash
hgbat -l a.out
```

输出所有汇编代码

```bash
hgbat --dump-isa a.out
```

或：

```bash
hgbat -i a.out
```

输出控制流图

```bash
hgbat --dump-cfg a.out
```

输出某个函数的信息

```bash
hgbat --dump-function --function=_Z4MathPfS_ a.out
```

输出寄存器活跃区间信息

```bash
hgbat --dump-live-range a.out
```

或：

```bash
hgbat -r a.out
```

以 wide 格式输出寄存器活跃区间

```bash
hgbat --dump-live-range --live-range-mode=wide a.out
```

输出寄存器活跃区间时不显示 `sreg`

```bash
hgbat --dump-live-range --no-print-sreg a.out
```

输出寄存器活跃区间时不显示 `vreg`

```bash
hgbat --dump-live-range --no-print-vreg a.out
```

输出全部分析信息

```bash
hgbat --dump-all a.out
```

或：

```bash
hgbat -a a.out
```

### 3.3 命令行参数

| 长选项                       | 短选项 / 别名   | 说明                                                                     |
| ---------------------------- | --------------- | ------------------------------------------------------------------------ |
| `--dump-all`                 | `-a`, `--all`   | 输出单个 hgbin 文件或二进制中嵌入的所有 hgbin 文件的全部信息。           |
| `--dump-cfg`                 | `-c`, `--cfg`   | 输出单个 hgbin 文件或二进制中嵌入的所有 hgbin 文件的控制流图（CFG）。    |
| `--dump-isa`                 | `-i`, `--isa`   | 输出单个 hgbin 文件或二进制中嵌入的所有 hgbin 文件的汇编代码。           |
| `--dump-live-range`          | `-r`, `--range` | 输出单个 hgbin 文件或二进制中嵌入的所有 hgbin 文件的寄存器活跃区间信息。 |
| `--dump-function`            | `-f`, `--func`  | 指定输出某一个函数的信息。                                               |
| `--function=<string>`        |                 | 指定函数名进行输出，必须使用 **mangled name（修饰名）**。                |
| `--list-elf`                 | `-l`, `--lelf`  | 列出 fatbin 中所有可用的 device function。                               |
| `--live-range-mode=<string>` | `--lrm`         | 控制寄存器活跃区间信息的输出格式。可选值见下方说明。                     |
| `--no-print-sreg`            | `--nps`         | 在输出寄存器活跃区间时，不显示 `sreg` 信息。                             |
| `--no-print-vreg`            | `--npv`         | 在输出寄存器活跃区间时，不显示 `vreg` 信息。                             |
| `--print-all-options`        |                 | 在命令行解析完成后，打印所有选项的取值。                                 |
| `--print-options`            |                 | 在命令行解析完成后，仅打印非默认选项的取值。                             |
| `--help`                     | `-h`            | 显示帮助信息。                                                           |
| `--help-hidden`              |                 | 显示所有可用帮助信息，包括隐藏选项。                                     |
| `--help-list`                |                 | 显示可用选项列表。                                                       |
| `--help-list-hidden`         |                 | 显示所有可用选项列表，包括隐藏选项。                                     |
| `--version`                  |                 | 显示程序版本信息。                                                       |

备注：

`--live-range-mode=<string>` 用于控制寄存器活跃区间信息的输出样式，可选值如下：

| 取值     | 说明                                                        |
| -------- | ----------------------------------------------------------- |
| `count`  | 不详细展示寄存器活跃区间，仅保留 `#` 列（活跃寄存器数量）。 |
| `narrow` | 每个寄存器使用一个字符宽度显示，节省表格宽度。默认模式。    |
| `wide`   | 以更宽松的列宽显示，便于阅读。                              |

### 3.4 示例

```bash
$ hgbat -i ppu_binary.o
...
HGBAT-INFO: Func 1 (device): _Z5funcCi
HGBAT-INFO: Func 2 (device): _Z5funcBi
HGBAT-INFO: Func 3 (kernel): _Z4funcPiS_PFiiE

HGBAT-INFO: Binary Function "_Z5funcCi" after disassembly {
  Number      : 1
  Address     : 0x0
  Size        : 0x2b0
  MaxSize     : 0x2b0
  Section     : .text
  BB Count    : 0

  _Z5funcCi:
      00000000:     s.wait    pipe_flush
      00000008:     s.wait    vldcnt(0), vstcnt(0), sldcnt(0), sstcnt(0), tsmcnt(0)
      ...
```
```bash
$ hgbat -c ppu_binary.o
$ dot _Z4funcPiS_PFiiE.dot -o _Z4funcPiS_PFiiE.png -Tpng
```

![输出示意图](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125155755/f5befa6528dd2f335113bfe8f295d9bf/hgbat_cfg.png)

```bash
$ hgbat -r ppu_binary.o
...
HGBAT-INFO: "_Z5funcCi" Live Range Analysis {
                                                                    //   #  s:0000000000111111111122 |   #  v:000000000011111
                                                                    //        0123456789012345678901 |        012345678901234
  _Z5funcCi:
    s.wait  pipe_flush                                              //   1  s:-------------------9-- |   6  v:0-2345--8------
    s.wait  vldcnt(0), vstcnt(0), sldcnt(0), sstcnt(0), tsmcnt(0)   //   1  s:-------------------9-- |   6  v:0-2345--8------
    v.madl.i32  vreg14, c0x1, vreg3, c0x0
    v.madl.i32  vreg3, c0x1, vreg2, c0x0                            //   1  s:-------------------9-- |   6  v:0-2-45--8-----4
    v.madl.i32  vreg6, c0x1, vreg8, c0x0                            //   1  s:-------------------9-- |   6  v:0---456-8-----4
    v.cmp.ne.i32  sreg15, vreg6.reuse, 0x0                          //   2  s:---------------5---9-- |   5  v:0---456-------4
    s.mov.b32  sreg18, 0xffffffff                                   //   3  s:---------------5--89-- |   5  v:0---456-------4
    v.mov.b32  vreg9, 0x0                                           //   3  s:---------------5--89-- |   6  v:0---456--9----4
    v.mov.b32  vreg7, vreg6                                         //   3  s:---------------5--89-- |   7  v:0---4567-9----4
    simt.rcbr.n  sreg15, 0x40                                       //   3  s:---------------5--89-- |   7  v:0---4567-9----4
  .LBB1:
    v.mov.b32  vreg7, vreg6                                         //   2  s:------------------89-- |   7  v:0---4567-9----4
    v.cmp.lt.u32  sreg15, vreg9, vreg7                              //   3  s:---------------5--89-- |   6  v:0---45-7-9----4
    s.mov.b32  sreg20, 0xffffffff                                   //   4  s:---------------5--890- |   6  v:0---45-7-9----4
    ...
```

比赛关联：`hgbat -r` 的寄存器活跃区间分析能定位 kernel 内寄存器压力峰值点，指导重排计算/拆分 kernel 以降低寄存器占用、提高并发 block 数（吞吐量）；`-c` 生成的 CFG 可检查热点循环结构是否被编译器异常拆分，是深度算子优化的主要分析手段。

## 4. hgprune

### 4.1 简介

`hgprune` 是 T-Head SAIL SDK 裁剪工具，用于从 relocatable binary 或 static library 中移除不需要的 PPU target，从而精简库文件的体积。

### 4.2 使用方式

```
hgprune [options] -o <outfile> <infile>
```

`hgprune` 接受一个输入文件，对该输入文件裁剪后，产生一个输出文件。

输入文件必须是 relocatable binary 或者 static library（.a），输出文件和输入文件格式相同。

必须通过 `--arch` 或 `--generate-code` 指定要保留的 PPU target。其他所有 PPU target 的 device code 将会在输出文件中被删除。

```bash
hgprune --arch hggc-ppu-ppu001 libac_base.a -o libac_base_pruned.a
```

上面的命令只保留 libac_base.a 中属于 ppu001 的 ELF，ppu001 的 BC 以及其它 PPU target 的 device code 会在输出文件中删除。

### 4.3 命令行参数

| 长选项                       | 短选项   | 说明                                                                                                                                               |
| ---------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--arch=<string>`            |          | 指定在输出文件中保留的 PPU target binary。可选的 target 为：<br>1. `hggc-ppu-ppu001`，对应 ppu001 ELF<br>2. `hgvm-ppu-ppu001`，对应 ppu001 BC file |
| `--generate-code=<string>`   |          | 以 key=value 格式指定要保留的 PPU target（功能同 `--arch`，语法不同）。可选的 key 为 code、arch，只有 code 会被解析，用来匹配 PPU target           |
| `--no-relocatable-elf`       |          | 删除所有 relocatable ELF                                                                                                                           |
| `--output-file=<string>`     | `-o`     | 输出文件路径                                                                                                                                       |
| `--verbose`                  | `-v`     | 输出详细信息                                                                                                                                       |
| `--version`                  |          | 输出版本信息                                                                                                                                       |
| `--help`                     | `-h`     | 输出帮助信息                                                                                                                                       |

## 5. hgFatbinary 概述

T-Head SAIL hgFatbinary（以下简称 hgfatbinary）是 fatbinary 构建工具。fatbinary 是一种多架构设备代码打包格式，hgfatbinary 可以将真武 PPU（以下简称 PPU）不同架构的设备代码打包到单一文件中，驱动程序根据 PPU 硬件架构自动加载对应的设备代码。

### 5.1 核心功能

- **多架构打包**：支持将不同 PPU 硬件架构编译出来的设备代码打包到同一文件中，无需为每种目标设备单独分发二进制文件，简化部署。
- **运行时自动选择**：驱动程序在启动时检测当前 PPU 硬件型号，从 fatbinary 中提取对应架构的设备代码进行加载。
- **数据压缩**：内置 ZSTD 压缩算法，可在打包时对设备代码进行压缩以减小最终设备代码体积。

hgfatbinary 支持打包如下格式的设备代码：

| 格式 | 文件名后缀 | 设备代码类型 | 说明 |
|------|-----|------------|------|
| hgbin | .hgbin | hggc | PPU 设备二进制（DeviceBinary），驱动直接加载运行的二进制文件 |
| LLVM IR | .bc | hgvm | LLVM bitcode，包含了 PPU 设备代码中间表示 |

其中，hggc（HeteroGeneous General-purpose Computing）是 PPU 通用编程模型，hgbin 是其典型编译产物；hgvm (HG Virtual Machine)，是 PPU 后端即时编译库，它主要接受 IR 作为输入。

### 5.2 工作流程

1. T-Head SAIL SDK 编译器为每个目标 PPU 架构分别生成 hgbin、LTO IR、RDC IR 等格式的设备代码。
2. `hgfatbinary` 工具将这些设备代码打包为 fatbinary 格式。
3. 链接器将 fatbinary 嵌入到主机可执行文件中。
4. 驱动程序解析 fatbinary 结构，根据当前 PPU 架构提取对应的设备代码并加载。

### 5.3 使用简介

hgfatbinary 提供了两种使用方式：

- `hgfatbinary` 命令行工具，支持完整的选项集，通过命令行方式打包 fatbinary
- `libhgfatbin` 静态库和动态库，提供 C API，应用程序通过调用 API 方式打包 fatbinary

以下详细介绍这两种使用方式。

## 6. hgfatbinary 命令行工具

### 6.1 命令行选项

| 选项 | 参数 | 描述 | 默认值/说明 |
| --- | --- | --- | --- |
| `--device-c` | 无 | 指定该二进制文件包含可重定位代码 | 可选 |
| `--create` | `<file name>` | 指定 fatbinary 文件名 |  |
| `--embedded-fatbin` | `<file name>` | 指定一个 C 文件名，该文件用于嵌入 fatbinary 二进制数据 |  |
| `--register-link-binaries` | `<file name>` | RDC 模式下使用，指定 hggcRegister stub 文件名，该文件包含链接输入文件的 hggcRegister stub 信息 |  |
| `--image3` | `file=<path>,kind=<type>,mcpu=<arch>` | 指定输入文件信息，包含其类型及编译该输入文件的架构版本。该选项允许使用的关键字为：<br> - `file`：目标文件路径（.hgbin, .bc）<br> - `kind`：代码类型（hggc, hgvm 等）<br> - `mcpu`：目标 PPU 架构型号（ppu001, ppu0015 等） | |
| `--compress-all` | 无 | 压缩 fatbinary 中的所有输入文件 | 可选 |
| `--compress` | `true` / `false` | 压缩 fatbinary 中除二进制文件以外的其他输入文件 | `true` |
| `--compress-mode` | `speed` / `balance` / `default` / `size` / `none` | 指定压缩模式：<br> - `speed`：优先速度<br> - `balance`：平衡模式<br> - `default`：默认（同 speed）<br> - `size`：优先体积<br> - `none`：不压缩 | `default` |
| `--help` / `-h` | 无 | 打印帮助信息 | |
| `--version` / `-V` | 无 | 打印版本信息 | |

### 6.2 命令行使用示例

#### 6.2.1 创建 fatbinary

```bash
hgfatbinary --create=/tmp/vector_add-7019ef.hgfb \
  --image3=file=/tmp/vector_add-76beaa.bc,kind=hgvm,mcpu=ppu001 \
  --image3=file=/tmp/vector_add-3c1b8b.out,kind=hggc,mcpu=ppu001
```

#### 6.2.2 创建 fatbinary，并生成 C 嵌入文件

```bash
hgfatbinary -create=/tmp/vector_add-i1TmCb.hgfb -image3=file=/tmp/vector_add-hggc-ppu-llc-ppu001-1PSyTl.out,kind=hggc,mcpu=ppu001 \
  --embedded-fatbin=/tmp/vector_add-TYfYMI.hgfb.c
```

#### 6.2.3 创建 fatbinary，并开启压缩

```bash
hgfatbinary --create=/tmp/vector_add-7019ef.hgfb --compress-all --compress-mode=speed \
  --image3=file=/tmp/vector_add-76beaa.bc,kind=hgvm,mcpu=ppu001 \
  --image3=file=/tmp/vector_add-3c1b8b.out,kind=hggc,mcpu=ppu001
```

## 7. libhgfatbin 使用说明

本章描述 libhgfatbin 提供的全部接口，包括函数原型、参数约定和返回值定义。所有 API 均返回 `hgFatbinResult`，`HGFATBIN_SUCCESS`（值为 0）表示成功，非零值表示错误，可通过 `hgFatbinGetErrorString` 获取错误码描述信息。

### 7.1 libhgfatbin API

#### 7.1.1 hgFatbinCreate

**功能**：创建一个新的 hgFatbin 句柄，作为后续所有操作的上下文。

**原型**：

```cpp
hgFatbinResult hgFatbinCreate(hgFatbinHandle *handle, const char **argv, size_t argc);
```

**参数说明**：

- [out] `handle`：返回创建成功后的 hgFatbin 句柄地址。
- [in] `argv`：创建 fatbinary 的选项字符串数组。每个字符串包含一个选项（如 `"--device-c"`、`"--compress-all"`）。
- [in] `argc`：`options` 字符串数组的元素个数。

**返回值**：

- `HGFATBIN_SUCCESS`：句柄创建成功。
- `HGFATBIN_ERR_NULL_ARG`：传入的参数为空指针（NULL）。
- `HGFATBIN_ERR_UNKNOWN_OPTION`：`options` 传入了当前库版本不支持的命令选项。
- `HGFATBIN_ERR_INTERNAL_FAULT`：发生未预期的异常或错误。

#### 7.1.2 hgFatbinDestroy

**功能**：销毁指定的 hgFatbin 句柄并释放所有关联资源。

**原型**：

```cpp
hgFatbinResult hgFatbinDestroy(hgFatbinHandle *handle);
```

**参数说明**：

- [in] `handle`：指向待销毁 hgFatbin 句柄的指针。

**返回值**：

- `HGFATBIN_SUCCESS`：句柄销毁成功。
- `HGFATBIN_ERR_NULL_ARG`：`handle` 句柄为空。
- `HGFATBIN_ERR_INTERNAL_FAULT`：发生未预期的异常或错误。

#### 7.1.3 hgFatbinAddHgbin

**功能**：将一份设备二进制（hgbin）代码添加到 fatbinary 中。

**原型**：

```cpp
hgFatbinResult hgFatbinAddHgbin(hgFatbinHandle handle, const void *code, size_t size, const char *arch, const char *identifier);
```

**参数说明**：

- [in] `handle`：hgFatbin 句柄。
- [in] `code`：指向 hgbin 二进制数据的指针。
- [in] `size`：hgbin 数据的字节长度。
- [in] `arch`：目标 PPU 架构标识符（如 `"ppu001"`）。
- [in] `identifier`：该条目的名称标识，在使用工具提取 fatbin 内容时用于区分各条目。

**返回值**：

- `HGFATBIN_SUCCESS`：添加成功。
- `HGFATBIN_ERR_INVALID_TARGET`：`arch` 不是有效的架构标识符。
- `HGFATBIN_ERR_ELF_ARCH_MISMATCH`：hgbin 内部架构字段与 `arch` 不一致。
- `HGFATBIN_ERR_ELF_SIZE_INVALID`：hgbin 实际长度与传入的 `size` 声明不一致。
- `HGFATBIN_ERR_NULL_INPUT`：`code` 为空或 `size` 为零。
- `HGFATBIN_ERR_COMPRESS_FAILURE`：数据压缩过程中发生错误。
- `HGFATBIN_ERR_COMPRESS_TOO_BIG`：压缩后的数据体积超过了允许的最大限制。
- `HGFATBIN_ERR_UNKNOWN_OPTION`：传入了当前不支持的命令选项。
- `HGFATBIN_ERR_INTERNAL_FAULT`：发生未预期的异常或错误。

#### 7.1.4 hgFatbinAddTIX

**功能**：将一份 TIX 中间表示添加到 fatbinary 中。

**原型**：

```cpp
hgFatbinResult hgFatbinAddTIX(hgFatbinHandle handle, const char *code, size_t size, const char *arch, const char *identifier, const char *optionsCmdLine);
```

**参数说明**：

- [in] `handle`：hgFatbin 句柄。
- [in] `code`：指向 TIX 中间表示数据的指针。
- [in] `size`：TIX 中间表示数据的字节长度（含终止符 `'\0'`）。
- [in] `arch`：目标 PPU 架构标识符（如 `"ppu001"`）。
- [in] `identifier`：该条目的名称标识，在使用工具提取 fatbin 内容时用于区分各条目。
- [in] `optionsCmdLine`：运行时编译所使用的编译选项。

**返回值**：

- `HGFATBIN_SUCCESS`：添加成功。
- `HGFATBIN_ERR_NULL_ARG`：传入的必要指针参数为空（NULL）。
- `HGFATBIN_ERR_NULL_INPUT`：`code` 为空或 `size` 为零。
- `HGFATBIN_ERR_INVALID_TARGET`：`arch` 不是有效的架构标识符。
- `HGFATBIN_ERR_TIX_ARCH_MISMATCH`：TIX 内部架构标注与 `arch` 参数不一致。
- `HGFATBIN_ERR_TIX_VERSION_NO_FOUND`：TIX 代码中缺少版本指令。
- `HGFATBIN_ERR_TIX_ARCH_NO_FOUND`：TIX 代码中缺少架构指令。
- `HGFATBIN_ERR_COMPRESS_FAILURE`：压缩过程失败。
- `HGFATBIN_ERR_COMPRESS_TOO_BIG`：压缩输出超过最大尺寸限制。
- `HGFATBIN_ERR_UNKNOWN_OPTION`：`optionsCmdLine` 中包含不支持的选项。
- `HGFATBIN_ERR_INTERNAL_FAULT`：发生未预期的异常或错误。

#### 7.1.5 hgFatbinAddCompressed

**功能**：将一份已压缩的 HGGC 二进制代码添加到 fatbinary 中。与 `hgFatbinAddHgbin` 不同，本函数接收的是预先压缩过的数据。

**原型**：

```cpp
hgFatbinResult hgFatbinAddCompressed(hgFatbinHandle handle, const void *code, size_t size);
```

**参数说明**：

- [in] `handle`：hgFatbin 句柄。
- [in] `code`：指向已压缩二进制数据的指针。
- [in] `size`：压缩数据的字节长度。

**返回值**：

- `HGFATBIN_SUCCESS`：添加成功。
- `HGFATBIN_ERR_INVALID_TARGET`：数据中标识的架构不合法。
- `HGFATBIN_ERR_ELF_ARCH_MISMATCH`：数据内部架构字段与预期不一致。
- `HGFATBIN_ERR_ELF_SIZE_INVALID`：数据实际长度与其头部声明不一致。
- `HGFATBIN_ERR_NULL_INPUT`：`code` 为空或 `size` 为零。
- `HGFATBIN_ERR_COMPRESS_FAILURE`：压缩过程失败。
- `HGFATBIN_ERR_COMPRESS_TOO_BIG`：数据超过最大尺寸限制。
- `HGFATBIN_ERR_UNKNOWN_OPTION`：全局选项中存在不支持的选项。
- `HGFATBIN_ERR_INTERNAL_FAULT`：发生未预期的异常或错误。

#### 7.1.6 hgFatbinAddLTOIR

**功能**：将一份链接时优化中间表示（Link-Time Optimization IR）添加到 fatbinary 中，LTO IR 用于跨模块链接优化场景。

**原型**：

```cpp
hgFatbinResult hgFatbinAddLTOIR(hgFatbinHandle handle, const void *code, size_t size, const char *arch, const char *identifier, const char *optionsCmdLine);
```

**参数说明**：

- [in] `handle`：hgFatbin 句柄。
- [in] `code`：指向 LTO IR 数据的指针。
- [in] `size`：LTO IR 数据的字节长度。
- [in] `arch`：目标 PPU 架构标识符（如 `"ppu001"`）。
- [in] `identifier`：该条目的名称标识，在使用工具提取 fatbin 内容时用于区分各条目。
- [in] `optionsCmdLine`：运行时 JIT 编译所使用的编译选项。

**返回值**：

- `HGFATBIN_SUCCESS`：添加成功。
- `HGFATBIN_ERR_NULL_ARG`：传入的必要指针参数为空（NULL）。
- `HGFATBIN_ERR_INVALID_TARGET`：`arch` 不是有效的架构标识符。
- `HGFATBIN_ERR_NULL_INPUT`：`code` 为空或 `size` 为零。
- `HGFATBIN_ERR_COMPRESS_FAILURE`：压缩过程失败。
- `HGFATBIN_ERR_COMPRESS_TOO_BIG`：压缩输出超过最大尺寸限制。
- `HGFATBIN_ERR_UNKNOWN_OPTION`：`optionsCmdLine` 中包含不支持的选项。
- `HGFATBIN_ERR_INTERNAL_FAULT`：发生未预期的异常或错误。

#### 7.1.7 hgFatbinAddRDCIR

**功能**：将一份可重定位设备代码中间表示（Relocatable Device Code IR）添加到 fatbinary 中，RDC IR 用于支持设备代码的分离编译与链接。

**原型**：

```cpp
hgFatbinResult hgFatbinAddRDCIR(hgFatbinHandle handle, const void *code, size_t size, const char *arch, const char *identifier, const char *optionsCmdLine);
```

**参数说明**：

- [in] `handle`：hgFatbin 句柄。
- [in] `code`：指向 RDC IR 数据的指针。
- [in] `size`：RDC IR 数据的字节长度。
- [in] `arch`：目标 PPU 架构标识符（如 `"ppu001"`）。
- [in] `identifier`：该条目的名称标识，在使用工具提取 fatbin 内容时用于区分各条目。
- [in] `optionsCmdLine`：运行时 JIT 编译所使用的编译选项。

**返回值**：

- `HGFATBIN_SUCCESS`：添加成功。
- `HGFATBIN_ERR_NULL_ARG`：传入的必要指针参数为空（NULL）。
- `HGFATBIN_ERR_INVALID_TARGET`：`arch` 不是有效的架构标识符。
- `HGFATBIN_ERR_NULL_INPUT`：`code` 为空或 `size` 为零。
- `HGFATBIN_ERR_COMPRESS_FAILURE`：压缩过程失败。
- `HGFATBIN_ERR_COMPRESS_TOO_BIG`：压缩输出超过最大尺寸限制。
- `HGFATBIN_ERR_UNKNOWN_OPTION`：`optionsCmdLine` 中包含不支持的选项。
- `HGFATBIN_ERR_INTERNAL_FAULT`：发生未预期的异常或错误。

#### 7.1.8 hgFatbinSize

**功能**：查询当前 fatbinary 的最终数据大小（字节数）。此函数应在 `hgFatbinGet` 之前调用。

**原型**：

```cpp
hgFatbinResult hgFatbinSize(hgFatbinHandle handle, size_t *size);
```

**参数说明**：

- [in] `handle`：hgFatbin 句柄。
- [out] `size`：接收 fatbinary 数据大小的指针。

**返回值**：

- `HGFATBIN_SUCCESS`：查询成功。
- `HGFATBIN_ERR_NULL_ARG`：`handle` 或 `size` 为空。
- `HGFATBIN_ERR_INTERNAL_FAULT`：发生未预期的异常或错误。

#### 7.1.9 hgFatbinGet

**功能**：将已构建的 fatbinary 数据写入调用方提供的缓冲区。

**原型**：

```cpp
hgFatbinResult hgFatbinGet(hgFatbinHandle handle, void *buffer);
```

**参数说明**：

- [in] `handle`：hgFatbin 句柄。
- [out] `buffer`：接收 fatbinary 数据的内存缓冲区。

**返回值**：

- `HGFATBIN_SUCCESS`：导出成功。
- `HGFATBIN_ERR_NULL_ARG`：`handle` 或 `buffer` 为空。
- `HGFATBIN_ERR_INTERNAL_FAULT`：发生未预期的异常或错误。

**使用步骤**：
1. 先调用 `hgFatbinSize` 获取所需缓冲区大小。
2. 分配不小于该大小的内存。
3. 将缓冲区指针传入 `hgFatbinGet`。

若未事先调用 `hgFatbinSize`，本函数将返回错误码。

#### 7.1.10 hgFatbinEmbeddedSize

**功能**：查询嵌入式 fatbinary 的数据大小（字节数）。此函数应在 `hgFatbinEmbeddedGet` 之前调用。

**原型**：

```cpp
hgFatbinResult hgFatbinEmbeddedSize(hgFatbinHandle handle, size_t *size);
```

**参数说明**：

- [in] `handle`：hgFatbin 句柄。
- [out] `size`：接收嵌入式 fatbinary 数据大小的指针。

**返回值**：

- `HGFATBIN_SUCCESS`：查询成功。
- `HGFATBIN_ERR_NULL_ARG`：`handle` 或 `size` 为空。
- `HGFATBIN_ERR_INTERNAL_FAULT`：发生未预期的异常或错误。

#### 7.1.11 hgFatbinEmbeddedGet

**功能**：将已构建的嵌入式 fatbinary 数据写入调用方提供的缓冲区。

**原型**：

```cpp
hgFatbinResult hgFatbinEmbeddedGet(hgFatbinHandle handle, void *buffer);
```

**参数说明**：

- [in] `handle`：hgFatbin 句柄。
- [out] `buffer`：接收嵌入式 fatbinary 数据的内存缓冲区。

**返回值**：

- `HGFATBIN_SUCCESS`：导出成功。
- `HGFATBIN_ERR_NULL_ARG`：`handle` 或 `buffer` 为空。
- `HGFATBIN_ERR_INTERNAL_FAULT`：发生未预期的异常或错误。

**使用步骤**：
1. 先调用 `hgFatbinEmbeddedSize` 获取所需缓冲区大小。
2. 分配不小于该大小的内存。
3. 将缓冲区指针传入 `hgFatbinEmbeddedGet`。

若未事先调用 `hgFatbinEmbeddedSize`，本函数将返回错误码。

#### 7.1.12 hgFatbinUncompress

**功能**：对 fatbinary 中的压缩数据执行解压。解压完成后，可通过 `hgFatbinGetUncompressSize` 和 `hgFatbinGetUncompressBuffer` 获取解压结果。

**原型**：

```cpp
hgFatbinResult hgFatbinUncompress(hgFatbinHandle handle);
```

**参数说明**：

- [in] `handle`：hgFatbin 句柄。

**返回值**：

- `HGFATBIN_SUCCESS`：解压成功。
- `HGFATBIN_ERR_NULL_ARG`：`handle` 为空。
- `HGFATBIN_ERR_INTERNAL_FAULT`：发生未预期的异常或错误。

#### 7.1.13 hgFatbinGetUncompressSize

**功能**：查询解压后设备代码数据的大小（字节数）。此函数应在 `hgFatbinGetUncompressBuffer` 之前调用。

**原型**：

```cpp
hgFatbinResult hgFatbinGetUncompressSize(hgFatbinHandle handle, size_t *uncompressSize);
```

**参数说明**：

- [in] `handle`：hgFatbin 句柄。
- [out] `uncompressSize`：接收解压后数据大小的指针。

**返回值**：

- `HGFATBIN_SUCCESS`：查询成功。
- `HGFATBIN_ERR_NULL_ARG`：`handle` 或 `uncompressSize` 为空。
- `HGFATBIN_ERR_INTERNAL_FAULT`：发生未预期的异常或错误。

#### 7.1.14 hgFatbinGetUncompressBuffer

**功能**：将解压后的设备代码数据写入调用方提供的缓冲区。

**原型**：

```cpp
hgFatbinResult hgFatbinGetUncompressBuffer(hgFatbinHandle handle, void* uncompressBuf);
```

**参数说明**：

- [in] `handle`：hgFatbin 句柄。
- [out] `uncompressBuf`：接收解压数据的内存缓冲区。

**返回值**：

- `HGFATBIN_SUCCESS`：导出成功。
- `HGFATBIN_ERR_NULL_ARG`：`handle` 或 `uncompressBuf` 为空。
- `HGFATBIN_ERR_INTERNAL_FAULT`：发生未预期的异常或错误。

**使用步骤**：
1. 先调用 `hgFatbinGetUncompressSize` 获取解压后的数据大小。
2. 分配不小于该大小的内存。
3. 将缓冲区指针传入 `hgFatbinGetUncompressBuffer`。

若未事先调用 `hgFatbinGetUncompressSize`，本函数将返回错误码。

#### 7.1.15 hgFatbinVersion

**功能**：查询当前 hgFatbin 库的版本号。

**原型**：

```cpp
hgFatbinResult hgFatbinVersion(const char** version);
```

**参数说明**：

- [out] `version`：接收版本字符串指针的地址。

**返回值**：

- `HGFATBIN_SUCCESS`：查询成功。
- `HGFATBIN_ERR_NULL_ARG`：`version` 为空。
- `HGFATBIN_ERR_INTERNAL_FAULT`：发生未预期的异常或错误。

#### 7.1.16 hgFatbinGetErrorString

**功能**：获取错误码对应的描述字符串，便于日志输出和问题诊断。

**原型**：

```cpp
const char *hgFatbinGetErrorString(hgFatbinResult result);
```

**参数说明**：

- [in] `result`：需要查询描述信息的错误码。

**返回值**：

返回对应错误码的描述字符串。

### 7.2 libhgfatbin 错误码

**enum hgFatbinResult**

`hgFatbinResult` 枚举定义了所有 API 的返回错误码。

```cpp
enum hgFatbinResult {
    HGFATBIN_SUCCESS = 0,
    HGFATBIN_ERR_INTERNAL_FAULT,
    HGFATBIN_ERR_ELF_ARCH_MISMATCH,
    HGFATBIN_ERR_ELF_SIZE_INVALID,
    HGFATBIN_ERR_TIX_VERSION_NO_FOUND,
    HGFATBIN_ERR_NULL_ARG,
    HGFATBIN_ERR_COMPRESS_FAILURE,
    HGFATBIN_ERR_COMPRESS_TOO_BIG,
    HGFATBIN_ERR_UNKNOWN_OPTION,
    HGFATBIN_ERR_INVALID_TARGET,
    HGFATBIN_ERR_INVALID_HGVM,
    HGFATBIN_ERR_NULL_INPUT,
    HGFATBIN_ERR_TIX_ARCH_NO_FOUND,
    HGFATBIN_ERR_TIX_ARCH_MISMATCH,
    HGFATBIN_ERR_FATBIN_NOT_FOUND,
    HGFATBIN_ERR_INVALID_INDEX_INPUT,
    HGFATBIN_ERR_IDENTIFIER_DUPLICATION,
    HGFATBIN_ERR_UNKNOWN_TIX_OPTION,
    HGFATBIN_ERROR_UNCOMPRESSED_IMAGE = 1 << 10
};
```

| 错误码 | 描述说明 |
|--------|----------|
| `HGFATBIN_ERR_INTERNAL_FAULT` | 发生未预期的异常或错误 |
| `HGFATBIN_ERR_ELF_ARCH_MISMATCH` | 设备二进制代码 ARCH 信息与预期不匹配 |
| `HGFATBIN_ERR_ELF_SIZE_INVALID` | 设备二进制代码文件的大小和实际大小不符（文件可能损坏） |
| `HGFATBIN_ERR_TIX_VERSION_NO_FOUND` | TIX 中间表示中缺失必要的版本标识指令 |
| `HGFATBIN_ERR_NULL_ARG` | 传入的必要指针参数为空（NULL） |
| `HGFATBIN_ERR_COMPRESS_FAILURE` | 数据压缩过程中发生错误 |
| `HGFATBIN_ERR_COMPRESS_TOO_BIG` | 压缩后的数据体积超过了允许的最大限制 |
| `HGFATBIN_ERR_UNKNOWN_OPTION` | 传入了当前不支持的命令选项 |
| `HGFATBIN_ERR_INVALID_TARGET` | 指定的目标 PPU 架构无效（例如架构名称拼写错误或不受支持） |
| `HGFATBIN_ERR_INVALID_HGVM` | 输入的中间表示层的代码格式错误或校验失败 |
| `HGFATBIN_ERR_NULL_INPUT` | 输入设备代码数据缓冲区为空，或指定的数据长度为 0 |
| `HGFATBIN_ERR_TIX_ARCH_NO_FOUND` | TIX 中间表示中缺失必要的架构标识指令 |
| `HGFATBIN_ERR_TIX_ARCH_MISMATCH` | TIX 中间表示内部标记的架构与传入的架构参数不匹配 |
| `HGFATBIN_ERR_FATBIN_NOT_FOUND` | 未找到主机代码 fatbinary 文件或数据 |
| `HGFATBIN_ERR_INVALID_INDEX_INPUT` | 传入了非法索引文件 |
| `HGFATBIN_ERR_IDENTIFIER_DUPLICATION` | 标识符重复（ID 冲突） |
| `HGFATBIN_ERR_UNKNOWN_TIX_OPTION` | 传入了非法或平台保留的 TIX 编译选项 |
| `HGFATBIN_ERROR_UNCOMPRESSED_IMAGE` | 解压异常或错误 |

### 7.3 API 调用示例

#### 7.3.1 构建并导出 fatbinary

本示例展示了使用 hgFatbin API 在运行时创建 fatbinary 的完整流程：从创建句柄、添加设备二进制、导出数据到最终释放资源。

```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include "hgFatbin.h"

bool readBinaryFile(const std::string& filename, std::vector<unsigned char>& buffer) {
    std::ifstream file(filename, std::ios::binary | std::ios::ate);
    if (!file.is_open()) {
        std::cerr << "无法打开文件: " << filename << std::endl;
        return false;
    }

    std::streamsize fileSize = file.tellg();
    file.seekg(0, std::ios::beg);

    buffer.resize(static_cast<size_t>(fileSize));
    if (buffer.size() != static_cast<size_t>(fileSize)) {
        std::cerr << "分配内存失败" << std::endl;
        return false;
    }

    if (!file.read(reinterpret_cast<char*>(buffer.data()), fileSize)) {
        std::cerr << "读取文件失败" << std::endl;
        return false;
    }

    return true;
}

int main() {
    hgFatbinHandle handle = nullptr;
    const char* options[] = {};
    size_t numOptions = 0;

    // 1. 创建句柄
    hgFatbinResult result = hgFatbinCreate(&handle, options, numOptions);
    if (result != HGFATBIN_SUCCESS || handle == nullptr) {
        std::cerr << "hgFatbinCreate 失败: " << hgFatbinGetErrorString(result) << std::endl;
        return 1;
    }

    std::cout << "hgFatbinCreate 成功！handle: " << handle << std::endl;

    // 2. 读取 hgbin 文件
    std::string hgbinFilename = "test.hgbin";
    std::vector<unsigned char> hgbinData;
    if (!readBinaryFile(hgbinFilename, hgbinData)) {
        std::cerr << "读取 hgbin 文件失败" << std::endl;
        hgFatbinDestroy(&handle);
        return 1;
    }

    // 3. 添加 hgbin 到 fatbinary
    result = hgFatbinAddHgbin(handle, hgbinData.data(), hgbinData.size(),
                              "ppu001", "my_test");
    if (result != HGFATBIN_SUCCESS) {
        std::cerr << "hgFatbinAddHgbin 失败: " << hgFatbinGetErrorString(result) << std::endl;
        hgFatbinDestroy(&handle);
        return 1;
    }

    std::cout << "hgbin 添加成功！" << std::endl;

    // 4. 查询 fatbinary 大小
    size_t fatbinSize = 0;
    result = hgFatbinSize(handle, &fatbinSize);
    if (result != HGFATBIN_SUCCESS || fatbinSize == 0) {
        std::cerr << "获取 fatbinary 大小失败: " << hgFatbinGetErrorString(result) << std::endl;
        hgFatbinDestroy(&handle);
        return 1;
    }

    std::cout << "fatbinary 大小为: " << fatbinSize << " 字节" << std::endl;

    // 5. 分配缓冲区并导出 fatbinary
    std::vector<unsigned char> fatbinBuffer(fatbinSize);
    result = hgFatbinGet(handle, fatbinBuffer.data());
    if (result != HGFATBIN_SUCCESS) {
        std::cerr << "导出 fatbinary 失败: " << hgFatbinGetErrorString(result) << std::endl;
        hgFatbinDestroy(&handle);
        return 1;
    }

    std::cout << "fatbinary 导出成功！" << std::endl;

    // 可选：将 fatbinary 写入文件
    std::ofstream output("output.fatbin", std::ios::binary | std::ios::out);
    if (output.is_open()) {
        output.write(reinterpret_cast<const char*>(fatbinBuffer.data()), fatbinSize);
        output.close();
        std::cout << "fatbinary 已写入文件 output.fatbin" << std::endl;
    } else {
        std::cerr << "无法创建输出文件 output.fatbin" << std::endl;
    }

    // 6. 释放资源
    result = hgFatbinDestroy(&handle);
    if (result != HGFATBIN_SUCCESS) {
        std::cerr << "hgFatbinDestroy 失败: " << hgFatbinGetErrorString(result) << std::endl;
        return 1;
    }

    std::cout << "资源已释放。" << std::endl;

    return 0;
}
```

编译运行：

```bash
g++ test.cpp -o test -lhgfatbin \
  -I /usr/local/PPU_SDK/targets/x86_64-linux/include/

./test
hgFatbinCreate 成功！
hgbin 添加成功！
fatbinary 大小为: 9616 字节
fatbinary 导出成功！
fatbinary 已写入文件 output.fatbin
资源已释放。
```

#### 7.3.2 多格式打包：同时添加 hgbin 与 TIX

以下代码片段展示如何为同一架构同时打包设备二进制和 TIX 文本表示。

```cpp
hgFatbinHandle handle = nullptr;
const char* opts[] = {"--compress-all"};
hgFatbinCreate(&handle, opts, 1);

// 添加 ppu001 架构的设备二进制
hgFatbinAddHgbin(handle, hgbin_data, hgbin_size, "ppu001", "kernel");

// 添加 ppu001 架构的 TIX
hgFatbinAddTIX(handle, tix_code, tix_size, "ppu001", "kernel.tix", /*optionsCmdLine=*/"");

// 导出 fatbinary
size_t outSize = 0;
hgFatbinSize(handle, &outSize);
std::vector<unsigned char> outBuf(outSize);
hgFatbinGet(handle, outBuf.data());

hgFatbinDestroy(&handle);
```

#### 7.3.3 导出 C 嵌入的 fatbinary

以下代码片段展示如何导出可嵌入主机程序的 fatbinary 数据。

```cpp
// 假设 handle 已创建并添加了内容

// 获取嵌入式 fatbinary
size_t embeddedSize = 0;
hgFatbinResult result = hgFatbinEmbeddedSize(handle, &embeddedSize);
if (result == HGFATBIN_SUCCESS && embeddedSize > 0) {
    std::vector<unsigned char> embeddedBuf(embeddedSize);
    result = hgFatbinEmbeddedGet(handle, embeddedBuf.data());
    if (result == HGFATBIN_SUCCESS) {
        // embeddedBuf 中包含可嵌入主机可执行文件的 fatbinary 数据
        std::cout << "嵌入 fatbinary 大小: " << embeddedSize << " 字节" << std::endl;
    }
}
```

#### 7.3.4 解压 fatbinary 数据

以下代码片段展示如何对压缩的 fatbinary 数据进行解压。

```cpp
// 假设 handle 指向一个已加载的、含压缩数据的 fatbinary

// 执行解压
hgFatbinResult result = hgFatbinUncompress(handle);
if (result != HGFATBIN_SUCCESS) {
    std::cerr << "解压失败: " << hgFatbinGetErrorString(result) << std::endl;
    return;
}

// 查询解压后大小
size_t uncompSize = 0;
hgFatbinGetUncompressSize(handle, &uncompSize);

// 导出解压数据
std::vector<unsigned char> uncompBuf(uncompSize);
hgFatbinGetUncompressBuffer(handle, uncompBuf.data());

std::cout << "解压完成，数据大小: " << uncompSize << " 字节" << std::endl;
```

比赛关联：自研 kernel 若需在运行期通过 JIT 方式（配合 hgrtc，见 11_hgrtc_jitlink.md）注入并打包进 fatbinary，libhgfatbin 的 C API 是唯一入口；`--compress-all --compress-mode=speed` 可减小部署二进制体积而不明显牺牲加载速度，对缩短模型/算子加载时间（间接影响 TTFT）有帮助。
