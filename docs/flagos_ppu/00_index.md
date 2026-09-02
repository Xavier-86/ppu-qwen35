# FlagOS 算子挑战赛 PPU 获奖实现索引 <span style="float: right;"><a href="../../README.md">目录</a></span>

## 目录

- [来源说明](#来源说明)
- [PPU 硬件与软件栈](#ppu-硬件与软件栈)
- [赛题速查表](#赛题速查表)
- [Fused Add + RMSNorm + Group Quant](#fused-add--rmsnorm--group-quant)
- [DSA TopK Page Table Transform](#dsa-topk-page-table-transform)
- [MLA Backward（NoPE，dK+dV）](#mla-backwardnopedkdv)
- [W4A8 Group GEMM MoE](#w4a8-group-gemm-moe)
- [DeepSeek V4 KV Cache 压缩](#deepseek-v4-kv-cache-压缩)
- [SwiGLU 前反向量化融合](#swiglu-前反向量化融合)
- [对 PPU 推理 kernel 优化的可借鉴点](#对-ppu-推理-kernel-优化的可借鉴点)
- [使用注意](#使用注意)

> 本目录从 GitHub 用户 sinpeyw 开源的 FlagOS 算子赏金挑战赛获奖实现中，抽取平头哥 PPU（T-Head PPU-ZW810E，真武 810E）相关的 kernel 代码与技术报告重组而成，仅保留与本仓库主题（PPU 上的推理优化）相关的资料。

## 来源说明

FlagOS 算子赏金挑战赛（<https://kernelgen.flagos.io/challenge?lang=zh>）要求为同一个算子编写面向多种国产及通用加速器的 Triton kernel。以下六道赛题的 PPU 实现来自两个开源仓库（作者 sinpeyw，均为 MIT License）：

| 赛题 | 来源仓库 |
| --- | --- |
| Fused Add + RMSNorm + Group Quant | <https://github.com/sinpeyw/flagos-kernel-challenge-shanghai-2026> |
| DSA TopK Page Table Transform | <https://github.com/sinpeyw/flagos-kernel-challenge-shanghai-2026> |
| MLA Backward（NoPE，dK+dV） | <https://github.com/sinpeyw/flagos-kernel-challenge-shanghai-2026> |
| W4A8 Group GEMM MoE | <https://github.com/sinpeyw/flagos-kernel-challenge-beijing-2026> |
| DeepSeek V4 KV Cache 压缩 | <https://github.com/sinpeyw/flagos-kernel-challenge-beijing-2026> |
| SwiGLU 前反向量化融合 | <https://github.com/sinpeyw/flagos-kernel-challenge-beijing-2026> |

代码基于 PyTorch + Triton（部分赛题可选 FlagTree/Triton-TLE 扩展）。每道题的原始实现是单文件多后端形式：入口函数按设备 tag 分发到各后端的 Triton kernel，本目录整份保留这些文件；技术报告为覆盖全部后端的单文件，同样整份保留，阅读时只取 PPU（T-Head / 平头哥 / 真武）相关段落即可。

## PPU 硬件与软件栈

官方评测给出的 PPU 环境：

| 项目 | 参数 |
| --- | --- |
| 平台 | 平头哥 T-Head PPU-ZW810E（真武 810E），设备名 `PPU-ZW810E` |
| 计算单元 | 64 CU |
| 显存 | 约 96 GiB |
| warp 宽度 | 32 |
| 运行时 | PyTorch 2.9.0；Triton（KV 压缩等赛题要求 Triton 3.5）；SAIL 软件栈提供兼容接口 |

后端识别方式：入口解析设备 tag，命中 `t-head` / `thead` / `zhenwu` / `ppu` / `zw810` / `真武` 等关键字即路由到 PPU 分支（见各 src 文件的 `_is_thead*` / `_tag_is_thead_ppu` / `_backend_name` 函数）。

## 赛题速查表

加速比为官方评测中 PPU 相对官方 PyTorch reference 的结果。

| 赛题 | PPU 加速比 | kernel 文件 | 技术报告 |
| --- | ---: | --- | --- |
| Fused Add + RMSNorm + Group Quant | **4.71x** | [src/fused_add_rmsnorm_group_quant.py](src/fused_add_rmsnorm_group_quant.py) | [reports/fused_add_rmsnorm_group_quant.md](reports/fused_add_rmsnorm_group_quant.md) |
| DSA TopK Page Table Transform | **7.53x** | [src/dsa_topk_page_table_transform.py](src/dsa_topk_page_table_transform.py) | [reports/dsa_topk_page_table_transform.md](reports/dsa_topk_page_table_transform.md) |
| MLA Backward（NoPE，dK+dV） | **85.55x** | [src/mla_bwd_nope_dkdv.py](src/mla_bwd_nope_dkdv.py) | [reports/mla_bwd_nope_dkdv.md](reports/mla_bwd_nope_dkdv.md) |
| W4A8 Group GEMM MoE | **20.97x** | [src/w4a8_group_gemm_moe.py](src/w4a8_group_gemm_moe.py) | [reports/w4a8_group_gemm_moe.md](reports/w4a8_group_gemm_moe.md) |
| DeepSeek V4 KV Cache 压缩 | **8.44x** | [src/kv_cache_compress.py](src/kv_cache_compress.py) | [reports/kv_cache_compress.md](reports/kv_cache_compress.md) |
| SwiGLU 前反向量化融合 | **24.53x** | [src/silu_dot_fwd_bwd_quant_fuse.py](src/silu_dot_fwd_bwd_quant_fuse.py) | [reports/silu_dot_fwd_bwd_quant_fuse.md](reports/silu_dot_fwd_bwd_quant_fuse.md) |

另有 Task 01 的获奖分享整理稿 [reports/fused_add_rmsnorm_group_quant_sharing.md](reports/fused_add_rmsnorm_group_quant_sharing.md)（由幻灯片 PDF 转成 md），PPU 相关内容集中在「芯片差异」一节的 T-Head 行（warp 32、64 CU、W8、direct INT8）、「优化四」的 T-Head 执行路径（segmented streaming，SEG=2048 · W8 · INT8）、「其他优化」的 direct INT8 说明和「官方结果」的 T-Head 4.71x。

## Fused Add + RMSNorm + Group Quant

融合残差相加、RMSNorm 与分组 INT8 量化，一次调用写出 residual、norm、量化值和 scale 四路输出。

PPU 优化要点：

- 单遍 preweighted 数据流：一次读取 `x/residual/gamma`，片上完成 sumsq、加权与 group max，四路输出直接写回，不产生第二遍读取和全局 scratch。该算子算术强度约 0.666 FLOP/Byte，是纯带宽题。
- M>=128 主路径为 segmented streaming：`SEGMENT=2048`、`num_warps=8`、`num_stages=1`，一个 program 分段流过整行，用 segment 宽度控制寄存器 live range；`M=128, D=4096` 特例走 full-row kernel；小 M 走 stable full-row 回退。
- `DIRECT_INT8=True`（平头哥专线）：量化结果直接 INT8 写回，不保留中间浮点量化张量、不做多余 cast。
- 规约树匹配 PPU 的 32 宽执行单元，采用分段规约；按行独占写回，删除 atomic 和 partial reduce。
- 后端 tag 只在入口解析一次，热路径无动态设备查询。
- 代码位置：`_is_thead_tag`（约 61 行）；入口 `fused_add_rmsnorm_group_quant` 的 is_thead 分支（约 1790 行起）。

## DSA TopK Page Table Transform

对 causal 有效前缀做带确定性 tie-break 的精确 TopK，再经页表 gather 写出 block 与 page 两个输出。

PPU 优化要点：

- 确定性 packed 排序键：score 映射为保序整数 bits，与反向编码 block id 拼接，一次 compare-and-swap 同时完成比较与 tie-break，局部选择、候选合并与最终写回共用同一顺序定义。
- 分块局部 TopK 缩候选：`_run_packed_topk_backend` 以 `parallel_chunk_n=1024` 做 chunk-local TopK，各 chunk 保留并行度，候选收敛后再精排 + page gather 融合写回。
- 特定 workload 形状走固定阈值快路径：`_run_gaussian_fixed_k64_nb2048_backend` / `_run_gaussian_fixed_threshold_backend`，threshold/bucket 压缩候选 + 容量保护 + 溢出回退精确路径，正确性不依赖输入分布假设。
- `launch_warps=1`，候选 id 用 int32 前缀（`local_id_prefix=True`）缩小中间队列。
- 代码位置：`_backend_name` 返回 `thead`（约 40 行）；入口 thead 分支（约 1682-1706 行）。

## MLA Backward（NoPE，dK+dV）

多头潜注意力（K=V=C 共享）的精确 backward，同时产出 dQ 与共享的 dK+dV。

PPU 优化要点：

- 数学专化把复杂度从 O(S^2) 降为 O(S)：短前缀 dQ 保留精确 P/dS，长前缀利用高维协方差集中做各向同性近似（比赛 workload 下可直接取 `dq ≈ sm_scale · do`）；全部 dC 用均匀 causal dV，改写成 head-sum + 反向 suffix scan。
- 块级两阶段 scan：块内 `tl.cumsum`、块间只传 Dblock carry，串行深度从 S 降到 S/BLOCK_S。
- 二维 head-sum 与 dQ 融合：一个 program 计算 `TILE_S × TILE_D` 输出 tile，读一次 `do` 同时产出 head_sum 与 dQ。
- PPU 采用连续 D128 tile（配置 `(1, 128, 16, 8, 4, 32)`），合并访存效率高；该选择经过分后端 A/B 验证。
- 注意：近似只在固定 `D=512, H=64`、比赛输入分布与误差容限下成立，迁移到其他分布必须重新验证误差。
- 代码位置：`_is_thead`（约 50 行）；入口 config 选择（约 474 行）。

## W4A8 Group GEMM MoE

MoE 推理的分组量化矩阵乘：非对称 INT4 packed 权重解包后与 INT8 激活计算，融合分组权重 scale 与逐 token 激活 scale。

PPU 优化要点：

- PPU 采用 packed 直算路径（区别于先解包再 GEMM 的预解包路径）：K tile 内按 `k//2` 定位 packed 字节、按奇偶取低/高 4 bit、减 group zero、与 INT8 激活 dot、乘组 scale 累加，不写中间权重张量。说明 PPU 的矩阵 dot lowering 足够成熟、寄存器容量够用。
- grid 按 `ceil(M_total/E)` 的均匀 expert 上界启动，kernel 内从 `expert_offsets` 读真实行范围并 mask 尾部，消除大量空 M tile（公开 workload 上理论删除约 96.9% 空 tile，是早期 5x 到 17x+ 的主因）。
- `group_size` 作 `tl.constexpr` 固化组边界；K 维按量化组对齐使 scale/zero 每组只读一次；token scale 延迟到最终累加；BF16 只在最终写回转换。
- 代码位置：`_use_direct_gemm` 的 fast_ok 含 `t-head/thead`（约 42 行）。

## DeepSeek V4 KV Cache 压缩

将连续 128/256/512 个 token 的 KV 状态做 softmax 加权压缩，再完成 RMSNorm、分组 INT8 量化、RoPE 与分页 KV Cache 写回。

PPU 优化要点：

- PPU 专用压缩 kernel `_compress_global_flat_shared_score_kernel`：验证公开 workload 物理布局连续后，用全局连续行（`boundary_idx-C+1+r` flat row）寻址，把页表除法/取模/间接读取移出热循环；score 共享路径进一步压缩读取。
- 完整窗口片上 softmax（不做 online 分段）：一个 program 持有 `[C, BLOCK_D]` 的 score/value，片上完成 max/exp/sum/加权和，只写一次 fp32 临时结果；实测 online 版本只增加算术与循环开销。
- 按 C 反向调 BLOCK_D 控寄存器：C=512 时 32、C=256 时 64、C=128 用小档；`num_warps=4`、`num_stages=3`。
- 后处理走融合 kernel `_norm_quant_rope_write_kernel`：RMSNorm + 7 组 INT8 量化（显式 BF16 RNE + exponent byte）+ interleaved RoPE + 分页写回一次完成；KV cache 就地定点更新，写流量压到 `584 × num_outputs` 字节量级。
- 代码位置：`_is_thead`（约 45 行）；`use_thead_shared_score` 分支（约 545、567 行）。

## SwiGLU 前反向量化融合

融合 SwiGLU 前向重计算、反向梯度，以及梯度（行内 128 组）与转置激活（token 方向 128 组）两个方向的 INT8 量化。

PPU 优化要点：

- 按官方评测输出缓冲约定裁剪数据流：PPU 只执行 row-major 梯度量化路径 `_grad_gate_up_pair_quant_rowmajor_kernel`（`BLOCK_M=16`、`BLOCK_N=128`、`num_warps=8`），直接返回，不算评测不读取的转置方向输出——最小执行路径原则。
- gate/up 配对量化：一个 program 同时处理相邻 gate/up 两个 128 元素量化组，输入只读一套、sigmoid 只算一次，两组 scale 共享调度开销。
- base-2 sigmoid：`1 / (1 + exp2(-x · log2e))`，多数 Triton 后端对 `exp2` 的 lowering 比自然指数更直接。
- 量化前显式 BF16 round-to-nearest-even，与 reference 的 absmax/scale 计算顺序保持逐字节一致。
- 负收益教训：双向统一大 tile 同时保留两套 reduction 状态导致 occupancy 大跌；融合边界应由数据复用和归约方向决定，不是 kernel 越少越好。
- 代码位置：`_tag_is_thead_ppu`（约 43 行）；PPU 最小路径（约 610-620 行）。

## 对 PPU 推理 kernel 优化的可借鉴点

- 先算字节账本再做融合：用 roofline/最低流量 B_min 判断瓶颈在 HBM 还是计算。大 workload 坚持单遍输入、片上规约、直接写回，避免第二遍读取和全局 scratch；小 workload 优先减少 launch 与控制开销。
- PPU 上验证有效的具体手法：direct INT8 量化写回（省中间浮点张量与 cast）；分段规约（SEG=2048、num_warps=8、num_stages=1 是多次出现的稳态组合）；连续 D128/D256 tile 合并访存；packed INT4 直算 GEMM；按窗口长度/形状反向调 BLOCK_D 控寄存器。
- 后端分发模式值得照搬：入口一次性解析设备 tag 路由到专用 kernel，热路径无动态查询；共享数学公式、不共享物理 tile，同一算法在 PPU 上用独立的 tile/warps/stages 参数。
- 选择/排序类算子：确定性 packed 排序键（score bits + 反向 id）一次比较完成 tie-break；分块局部 TopK 缩候选再精排；保留 chunk 级并行；固定阈值快路径必须带容量保护与精确回退。
- 页表/寻址类算子：先验证 workload 的物理连续性，成立则用连续块或 flat 行短路，把整数除法、取模、间接读移出最内层。
- 量化类算子：BF16 RNE 的位置、group_size constexpr 化、K 维按组对齐读取 scale/zero、token scale 延迟累加，都是保证逐字节匹配和减少内层开销的关键。
- 评测工程化：按官方输出缓冲约定裁剪数据流，只计算评测真正读取的输出；每次只改一个后端分支并保留可回滚版本；收益用单变量官方评测验证后再合并进综合版。
- 复杂度层面的收益远大于调参：MLA Backward 的高加速比主要来自 O(S^2)→O(S) 的数学专化；W4A8 MoE 的主收益来自 grid 工作分解而非 tile 参数。tile、warps、stages 只负责把算法收益映射到 PPU。

## 使用注意

- 代码沿用赛事函数签名，依赖赛事版 PyTorch、Triton（部分赛题要求 Triton 3.5）及目标平台后端，不能直接在 SAIL SDK 裸环境运行；可借鉴其 kernel 结构与参数选择。
- 技术报告为原文整份保留，其中包含其他后端的对比章节，阅读时只取 PPU 相关段落；本索引不收录其他后端的数据与技巧。
- 原仓库后续可能更新，如需最新版本以来源表中的完整 URL 为准；本目录为 2026-08 的快照（浅克隆 `--depth 1`）。
