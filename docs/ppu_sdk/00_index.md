# T-Head SAIL SDK v2.1.1 · 比赛参考手册索引 <span style="float: right;"><a href="../../README.md">目录</a></span>

## 目录

- [手册结构](#手册结构)
- [按比赛评分维度的使用路线](#按比赛评分维度的使用路线)
  - [1. 精度保持](#1-精度保持)
  - [2. TTFT 优化](#2-ttft-优化)
  - [3. 吞吐量提升](#3-吞吐量提升)
  - [4. 系统级优化深度](#4-系统级优化深度)
  - [部署（复赛 PPU 服务器）](#部署复赛-ppu-服务器)
- [使用注意](#使用注意)


> 面向比赛：基于 Qwen3.5-2B 的 VLM 在阿里平头哥 PPU 服务器上的高效推理优化。
> 本套手册与 [../ppu_hggc/00_index.md](../ppu_hggc/00_index.md)（HGGC 编程指南笔记）配套使用。

## 手册结构

| 文件 | 内容 | 规模 |
| --- | --- | --- |
| [01_overview_install.md](01_overview_install.md) | SDK 概览、Release Notes（v2.1.1 功能与已知问题）、安装指南（系统要求/Runfile 安装/验证） | ~34 KB |
| [02_tix_programming.md](02_tix_programming.md) | **TIX 编程指南**（PPU 指令集/虚拟 ISA：全部指令、Tensor Cell MMA、AIU 异步拷贝、内联汇编） | ~397 KB |
| [03_hggc_samples.md](03_hggc_samples.md) | HGGC 官方示例程序（59 个：Tensor Cell GEMM、Graph、内存策略、性能微基准） | ~74 KB |
| [04_runtime_api.md](04_runtime_api.md) | HGGC Runtime API 完整参考（30 篇子文档合并，236 个函数） | ~305 KB |
| [05_driver_api.md](05_driver_api.md) | HGGC Driver API 完整参考（33 篇子文档合并：VMM、模块加载、Graph 72 函数） | ~452 KB |
| [06_math_api.md](06_math_api.md) | Math API（812 个函数：FP8/half/bf16 内建、单双精度、快速/精确对照、SIMD 内建） | ~85 KB |
| [07_acdnn.md](07_acdnn.md) | acDNN 深度学习库（对标 cuDNN：卷积、**MultiHeadAttn**、RNN、Graph API、融合算子） | ~432 KB |
| [08_acblas.md](08_acblas.md) | acBLAS（对标 cuBLAS：GEMM 全精度组合表、acblasLt epilogue 融合、FP8/IMMA） | ~204 KB |
| [09_acsparse.md](09_acsparse.md) | acSPARSE 稀疏矩阵库（CSR/BSR/Blocked-ELL、SpMV/SpMM/SpGEMM，剪枝相关） | ~255 KB |
| [10_hgcc.md](10_hgcc.md) | hgcc 编译器手册（104 项编译选项全表、多架构编译、RDC+LTO） | ~45 KB |
| [11_hgrtc_jitlink.md](11_hgrtc_jitlink.md) | HGRTC 运行时编译 + hgJitLink JIT 链接（自定义算子运行时注入路径） | ~52 KB |
| [12_binary_utilities.md](12_binary_utilities.md) | 二进制工具（hgobjdump 反汇编/资源信息、hgbat CFG/寄存器活跃区间、hgprune、hgFatbinary） | ~50 KB |
| [13_ppu_gdb.md](13_ppu_gdb.md) | PPU-GDB 调试器（kernel 断点/单步、寄存器查看、autostep、核心转储、36 条异常代码表） | ~30 KB |
| [14_memcheck.md](14_memcheck.md) | HGGC Memcheck（memcheck/racecheck/initcheck/synccheck 四工具与全部示例） | ~36 KB |
| [15_ppu_smi_mps.md](15_ppu_smi_mps.md) | PPU-SMI 设备管理监控 + MPS 多进程服务（时钟锁定、stats/dmon、MIG、拓扑） | ~135 KB |

未收录（与比赛关系不大）：acFFT、acSOLVER、acRAND、libHGVM、libPPUDevice、Sanitizer API。HGGC 编程指南（chapterId=196）已单独整理于 [../ppu_hggc/](../ppu_hggc/00_index.md)。

## 按比赛评分维度的使用路线

### 1. 精度保持

- **量化精度组合**：acBLAS 的 GemmEx/IMMA/FP8 三张精度组合表 → 08；INT8x4/INT8x32 与数据类型边界 → 07 §2.1.2.5；FP8 e4m3/e5m2/e8m0 转换与饱和语义 → 06 第 2 章。
- **精度陷阱**：acBLAS Gemm 默认 FP32 Tensor Cell 与 FMA 精度不匹配，用 `PPU_FP32_TENSOR_OVERRIDE=0` 对齐 → 01 Release Notes。
- **逐算子精度-速度取舍**：快速/精确数学函数对照表（`__expf` vs `expf` 等）→ 06 第 5.2 章；ULP 误差另见 ../ppu_hggc/05 §5.4。

### 2. TTFT 优化

- **真正的异步 H2D**：只有"锁页内存 + Async + 非默认流"才真异步（全组合表）→ 04 概念节。
- **模块预加载**：`hgModuleLoad`/`hgLibraryLoadFromFile` 启动期预加载，`HGGC_MODULE_LOADING`/`HGGC_DISABLE_JIT`/`HGGC_FORCE_PRELOAD_LIBRARIES` 控制 JIT 时机 → 05 §4；编译期直接生成真实架构 hgbin（`-arch ppu_15`）避免 JIT 首载 → 10 §5.4。
- **Graph 预热**：`hggcGraphUpload` + 实例化复用 → 04 图管理节；decode 参数热更新范式 → 03 §2.4 Graph 示例。
- **MHA 库算子**：`acdnnMultiHeadAttnForward` 原生增量解码（currIdx、设备侧序列长度、因果窗口）→ 07 §4.2.26。

### 3. 吞吐量提升

- **MPS 多进程**：2B 小模型单请求算力低，MPS 多 client 并行提升计算单元利用率（上限 7 进程，`UMD_MPS_ACTIVE_CE_COUNT` 调份额；与 ICN 多卡互斥）→ 15 第 16 章。
- **acblasLt epilogue 融合**：BIAS/GELU_BIAS 融进 GEMM，plan 复用零重配置 → 08 第 5 章。
- **Tensor Cell GEMM 范式**：bf16/tf32/imma 三个官方 GEMM 示例 + AIU swizzle 搬运 → 03 §2.4；TIX MMA fragment 全表 → 02 第 9 章。
- **稀疏加速**：Blocked-ELL + Tensor Cell 是稀疏 SpMM 最高吞吐通道（行块差异 <30%、block 64）→ 09 第 5/8 章。
- **时钟锁定**：`ppu-smi -lpc/-ac` 锁频 + 排查降频原因，保证压测可复现 → 15 第 4 章。

### 4. 系统级优化深度

- **指令集优化**：TIX 全部指令（cp.async/AIU、awbar、dp4a、warp redux）→ 02；`hgobjdump -i=all` 看寄存器/TSM 占用、`hgbat -r/-c` 做寄存器活跃区间与 CFG 分析 → 12。
- **显存管理**：流有序内存池 + `HG_MEMPOOL_ATTR_RELEASE_THRESHOLD` → 04/05 内存节；VMM 按需提交物理页 → 05 §5。
- **运行时注入自定义算子**：HGRTC `-dlto` → hgJitLink LTO 链路；符号裁剪减小 hgbin → 11。
- **调试排错**：memcheck 定位越界（指令 PC + 线程坐标）、racecheck 查精度漂移、PPU-GDB autostep 与 36 条异常代码表 → 13/14。
- **监控取证**：`ppu-smi stats/dmon` + 选择性查询 CSV 输出，留档设备侧证据 → 15 第 3/5/6 章。

### 部署（复赛 PPU 服务器）

- 安装与验证流程（Runfile、`envsetup.sh`、`ppu-smi` 验证）→ 01 安装指南；KMD/SDK 版本兼容性 → 01 Release Notes。

## 使用注意

- 各文件中的"比赛关联："注记为整理时所加，其余内容均保真自官方文档。
- 官方文档中的少量笔误（如错误码拼写）按保真原则原样保留。
- PPU-GDB 尚未随 SAIL SDK v2.1.1 发布（后续版本推出），使用前需确认比赛环境是否可用 → 13。
