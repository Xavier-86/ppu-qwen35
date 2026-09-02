# Task 01：W4A8 Group GEMM MoE

> 最终源码：[`../src/task01_w4a8_group_gemm_moe.py`](../src/task01_w4a8_group_gemm_moe.py)

## 写在前面

该实现通过七个平台的官方正确性测试，平均加速比 **18.94×**。

| 华为昇腾 | 摩尔线程 | 天数智芯 | 平头哥 | 海光 | 沐曦 | 国际通用芯片 |
|---:|---:|---:|---:|---:|---:|---:|
| 0.52× | 4.66× | 10.78× | 20.97× | 14.25× | 46.35× | 35.03× |

这道题的关键不是写出一个通用矩阵乘，而是同时处理小批量 MoE、INT4 解包、非对称零点、分组缩放和七种后端不同的矩阵指令能力。

## 技术摘要

整体方案由四类执行路径组成：
1. NVIDIA、沐曦和平头哥采用直接读取 packed W4 的分组 GEMM；
2. 海光先将 W4 解包为 INT8，再使用 fp16 transposed-B dot；
3. 天数智芯先解包权重，再执行 unpacked GEMM；
4. 华为昇腾和摩尔线程使用有界标量/小 N-block 内核，避开不稳定的矩阵 lowering。

最大的通用收益来自重新定义并行任务：公开 workload 的 expert 行数均匀，grid 因此按 `ceil(M_total/E)` 设置每个 expert 的 M 上界，不再把每个 expert 扩展到全局 `M_total`；实际行起止地址仍由 `expert_offsets` 读取并参与 mask。

## 题目拆解

输入激活为 `x_q[M_total, K]` INT8，权重为 `w_q4_packed[E, N, K/2]`。每两个 K 元素压入一个字节。对于 expert `e`、输出行 `m` 和列 `n`：

\[
y_{mn}=s^x_m\sum_{g=0}^{G-1}s^w_{eng}\cdot
\sum_{k=gS}^{(g+1)S-1}x^q_{mk}\cdot
\left(w^4_{enk}-z_{eng}\right),
\quad G=K/S
\]

其中 `S` 为 64 或 128。实际实现中，组内点积先累加，再乘该组权重 scale，所有组求和后乘 token scale，最终写回 BF16。

官方 workload 的 `E` 为 4～64，`M_total` 为 32～1024，`N` 为 512～2048，`K` 为 512～4096。许多形状的单 expert 行数很少，因此传统大 GEMM 的 tile 假设并不成立。

## 瓶颈分析

核心整数 MAC 数为：

\[
\mathrm{MAC}=M_{\text{total}}NK
\]

按一次乘加记两次运算，计算量约为 `2M_totalNK`。理想输入输出流量至少包括：

| 数据 | 最小字节数 |
|---|---:|
| INT8 激活 | `M_total K` |
| packed INT4 权重 | `E N K / 2` |
| 权重 scale 与 zero | `5 E N K / S` |
| token scale | `4 M_total` |
| BF16 输出 | `2 M_total N` |

理论上 GEMM 具有较高算术强度，但小 expert 会破坏权重重用：若每个 expert 的 grid 都按全局 `M_total` 上界启动，会产生大量空 M tile；若边算边解包，packed 字节、zero 和 scale 又会在多个 M tile 中重复读取。真正的主导问题因此是：
- 无效 program 数量；
- W4 解包与矩阵指令之间的数据表示冲突；
- 小 M 下不足的并行度和权重重用；
- 不同后端对 INT8 dot、转置 B 和宽 tile 的支持差异。

## 总体方案：先确定工作分解，再选择权重表示

方案分两层。第一层只解决“谁计算哪一块”：利用公开 workload 的均匀 expert 分配，以 `ceil(M_total/E)` 作为 grid 上界；kernel 再从 `expert_offsets[e:e+2]` 读取真实起止位置并屏蔽尾部。第二层才决定“如何计算”：支持 packed dot 的后端直接解包到寄存器；更适合标准矩阵 operand 的后端先生成 `w_signed`，随后进入专用 GEMM；矩阵 lowering 不稳定的后端使用有界标量内核。

这种拆分使专家调度、权重表示和后端指令选择互不混淆，也让每个平台只承担自身必要的代价。

## 核心技术一：用均匀 expert 上界消除空 tile

朴素 grid 若使用全局 M：

\[
P_{\text{naive}}=E\left\lceil\frac{M_{\text{total}}}{B_M}\right\rceil\cdot
\left\lceil\frac{N}{B_N}\right\rceil
\]

真实需要的 program 数则为：

\[
P_{\text{uniform}}=E
\left\lceil\frac{\lceil M_{\text{total}}/E\rceil}{B_M}\right\rceil\cdot
\left\lceil\frac{N}{B_N}\right\rceil
\]

例如 `E=64, M_total=512, BM=16`，M 方向的系数从 `64×32=2048` 降为 `64×1=64`，理论上删除了 96.875% 的空 M tile。`expert_offsets` 仍决定每个 tile 的真实行地址与尾部 mask。这个工作分解变化与矩阵化 dot 一起，是早期成绩从约 5×跃升到 17×以上的主要来源。

## 核心技术二：packed 直算与预解包双路径

直接路径在 K tile 内完成：

1. 通过 `k//2` 定位 packed 字节；
2. 根据 K 奇偶选择低/高 4 bit；
3. 减去对应 group zero；
4. 与 INT8 激活做点积；
5. 乘 group scale 并累加。

它不写中间权重，节省 `ENK` 字节的 INT8 临时写回与后续读取，适合矩阵 lowering 成熟且寄存器容量足够的后端。

预解包路径使用独立二维 kernel 将 packed W4 转成连续 `w_signed[E,N,K]`。虽然增加一次全局写读，但换来了规则的矩阵 operand、连续访存和更稳定的编译。海光、天数智芯上，这个交换是正收益。

## 核心技术三：海光 fp16 transposed-B dot

海光路径先加载 `A[BM,BK]` 与 `B[BN,BK]`，将解包后的 INT8 转为 fp16，然后使用：

```python
acc += tl.dot(a, tl.trans(b))
```

与直接构造 `[BK,BN]` 相比，`B[BN,BK]` 的 K 维连续，加载更自然，也更符合该后端已验证的 dot lowering。分组 scale 在每个 K group 完成后应用，保持原始数学顺序。最终版本在海光达到 **14.25×**。

## 核心技术四：昇腾固定上界循环与摩尔小 N-block

昇腾路径使用固定 program 上界，由 kernel 内部循环领取工作，避免 Python 侧产生大量小 launch，也避免依赖后端不稳定的通用矩阵 lowering。每个 program 只处理很窄的 N，并以 `BK=128` 顺序扫 K。

摩尔线程则采用小 `N_BLOCK=4`。这牺牲一部分向量宽度，却显著降低寄存器压力，使更多 program 常驻。两条路径说明：在多后端题目中，稳定可编译的受控并行度比统一的大 tile 更重要。

## 其他有效优化

| 优化 | 作用 |
|---|---|
| group_size 作为 `tl.constexpr` | 固化组边界，删除运行时除法与分支 |
| K 维按量化组对齐 | scale/zero 每组只读取一次 |
| token scale 延迟到最终累加 | 减少内层乘法 |
| N/K tile 分平台设置 | 平衡矩阵吞吐、寄存器压力和 occupancy |
| BF16 仅在最终写回转换 | 保持 fp32 累加精度 |

没有保留的尝试主要包括：统一大 tile、让所有平台共用 packed dot，以及按全局 M 启动 expert grid。它们分别受制于编译能力、寄存器压力和空 program。

其他经验：
- MoE 算子的第一优化对象应是有效工作量，而不是 tile 参数。
- INT4 解包是否融合没有统一答案，应与后端矩阵 operand 的最佳布局一起决定。
- 多后端调优必须保存每个平台的稳定路径；一次看似通用的重构可能改变所有后端的 lowering。
- 每次只修改一个后端分支，并保留可回滚版本，远比同时调整多个常量更容易定位真实收益。

## 最终效果

| 指标 | 结果 |
|---|---:|
| 正确性 | 7/7 平台通过 |
| 平均加速比 | **18.94×** |
| 最佳单平台 | 沐曦 **46.35×** |
