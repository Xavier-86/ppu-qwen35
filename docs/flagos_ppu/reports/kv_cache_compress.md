# Task 02：DeepSeek V4 KV Cache Compression

> 最终源码：[`../src/task02_c128_256_512_compress.py`](../src/task02_c128_256_512_compress.py)

## 写在前面

该实现通过七个平台的官方正确性测试，平均加速比 **9.35×**。

| 华为昇腾 | 摩尔线程 | 天数智芯 | 平头哥 | 海光 | 沐曦 | 国际通用芯片 |
|---:|---:|---:|---:|---:|---:|---:|
| 3.46× | 7.70× | 7.11× | 8.44× | 9.16× | 16.19× | 13.39× |

算子将连续 128/256/512 个 token 压缩为一个 KV entry，随后执行 RMSNorm、分组 INT8 量化、RoPE 与分页写回。它不是 GEMM，主耗时来自长窗口上的 softmax 加权归约和不规则地址计算。

## 技术摘要

最终实现采用两阶段数据流：

1. 压缩 kernel 将每个输出的 512 维加权结果写入 fp32 临时张量；
2. 后处理 kernel 完成 RMSNorm、7 组 INT8 量化、64 维 RoPE 和分页写回。

压缩阶段按后端选择普通页表寻址、连续物理块、全局连续行或共享 score 路径；后处理阶段在多数后端融合，在沐曦和昇腾上拆分为更适合其编译器的结构。

## 题目拆解

对每个输出 `o`、维度 `d` 和压缩长度 `C`：

\[
p_{odr}=\frac{\exp(s_{odr}-m_{od})}
{\sum_{j=0}^{C-1}\exp(s_{odj}-m_{od})},
\qquad
v_{od}=\sum_{r=0}^{C-1}p_{odr}x_{odr}
\]

得到 `v[o,512]` 后计算：

\[
r_o=\left(\frac{1}{512}\sum_d v_{od}^2+\epsilon\right)^{-1/2},
\qquad n_{od}=v_{od}r_ow_d
\]

前 448 维按 64 维一组量化为 INT8，并写 7 个 exponent byte；后 64 维做 interleaved RoPE 后以 BF16 写入。输出每个 entry 占 576 个 payload 字节和 8 个 scale 字节。

## 瓶颈分析

`state_cache` 每个 token 包含 512 个 value 和 512 个 score，均为 fp32。单个输出的理论最小读取量为：

\[
B_{\text{state}}=C\times1024\times4=4096C\ \text{bytes}
\]

当 `C=512` 时，仅状态读取就约 2 MiB；最终写回只有 584 B。每个输出还需要约 `512C` 次指数运算以及同量级的乘加与归约。若暂不把 `exp` 视为多条指令，普通算术强度低于 1 op/B；即使将指数代价计入，该算子也同时受内存延迟、特殊函数吞吐和归约 occupancy 限制。

因此，关键问题不是减少最终 584 B 写回，而是：

- 每个 score/value 是否只读取一次；
- 页表翻译是否进入最内层；
- `C×BLOCK_D` 活跃张量是否造成寄存器溢出；
- softmax 数值顺序能否满足 INT8 byte 精确匹配；
- 后处理的小写入能否合并为少量 launch。

## 总体方案：长归约一次读完，后处理按编译能力分流

压缩 kernel 让一个 program 负责一个输出和一段 D tile，将整个 C 窗口的 score/value 留在片上完成 max、exp、sum 和加权和，不物化概率矩阵。只在 `tmp[o,d]` 写一次 fp32 结果。

第二阶段围绕 512 维向量完成归一化和格式转换。通用后端使用融合 kernel；沐曦将 reciprocal RMS 与 NOPE/RoPE 写回拆开；昇腾使用固定上界标量循环与显式 BF16 round-to-nearest-even，优先保证精确字节和编译稳定性。

输出直接更新调用方传入的 `kv_cache`，仅覆盖本次 `kv_slot_mapping` 指向的 payload 与 scale 区域。与先构造并清零整张同尺寸缓存相比，这一做法把写流量从 KV cache 总容量降到 `584×num_outputs` 字节量级。

## 核心技术一：连续块与全局连续行寻址

通用页表路径对窗口中每个位置计算：

\[
block=block\_table[req,\lfloor pos/B\rfloor],\quad
offset=pos\bmod B
\]

这会把整数除法、取模和间接读取带入热循环。公开 workload 的物理布局允许部分后端使用两个更短的路径：

- 连续块路径：从边界 token 推导首块，只在 block 边界更新物理块；
- 全局连续行路径：直接使用 `boundary_idx-C+1+r` 形成 flat row。

它们不改变 softmax 数学，却删除了大量地址翻译。昇腾成绩从早期约 0.5×提高到 **3.46×**，说明该平台的主要损失曾来自压缩阶段的寻址，而不只是后处理。

## 核心技术二：完整窗口片上 softmax

每个 program 加载 `[C,BLOCK_D]` score，执行：

```python
mx = tl.max(score, axis=0)
ex = tl.exp(score - mx[None, :])
den = tl.sum(ex, axis=0)
acc = tl.sum(value * ex, axis=0) / den
```

与分段 online softmax 相比，该结构不需要反复更新 `(m,l,acc)`，也不引入分段 rescale。两者读取总量相同，而本题没有需要避免物化的全局 attention matrix，因此 online 版本仅减少瞬时活跃范围，却增加算术和循环开销。实际测试中，两遍 streaming 路径平均加速比降到约 2.37×，证明“更像 FlashAttention”并不等于更适合这个归约。

## 核心技术三：按 C 与输出规模调整 D tile

寄存器占用近似正比于 `C×BLOCK_D`。最终策略让 C 越大，D tile 越小：

| 压缩长度 | 大 workload | 小 workload |
|---:|---:|---:|
| 128 | 32 | 64 |
| 256 | 16 | 32 |
| 512 | 8 | 16 |

小 workload 用更宽 D，减少 program 数；大 workload 缩窄 D，换取更多 resident program 和更好的延迟隐藏。该选择比统一 `BLOCK_D=64` 稳定，因为 C=512 时后者会同时持有 32768 个 score 元素和同规模 value。

## 核心技术四：精确量化与分平台后处理

量化必须匹配 reference 的 BF16 截断与 exponent byte。前 448 维先按 RMSNorm 得到 fp32，再显式执行 BF16 RNE 回到 fp32，随后每 64 维求：

\[
e=\left\lceil\log_2\left(\max|x|/127\right)\right\rceil,\qquad
q=\mathrm{int8}\left(\mathrm{clamp}(x2^{-e},-127,127)\right)
\]

通用融合 kernel 一次写 value、scale 和 RoPE。沐曦路径先独立计算 `rrms`，再用本地更窄的 writer，避免一个过大的融合 kernel 降低 occupancy。昇腾路径以固定 program 数循环多个输出，并用标量 byte store 避免 grouped uint8/BF16 写回的 lowering 差异。

## 其他有效优化

| 优化 | 作用 |
|---|---|
| `tmp` 使用 fp32 | 保持 softmax/RMSNorm 数值稳定 |
| KV cache 就地定点更新 | 删除整张输出缓存的分配与清零 |
| 512 维 RMSNorm 一次归约 | 避免平方和中间张量 |
| RoPE 按 32 对 interleaved pair 处理 | 连续读取 cos/sin，连续写 128 B |
| 预计算 slot/page/value base | 将分页计算移出维度循环 |
| 压缩长度与维度均 constexpr 化 | 展开静态循环，删除运行时分支 |

主要负收益来自：分段 online softmax、双输出合并到同一 program、将额外平方和写入全局内存，以及把所有后端强制合并到一个重型后处理 kernel。

其他经验：
- 先计算不可约的数据读取量，能避免把时间浪费在只减少 launch、却增加全局流量的融合上。
- online softmax 的价值取决于它是否删除了全局中间量；本题原路径已经不物化概率矩阵。
- INT8 byte 精确题必须把舍入位置视为算法的一部分，不能只比较数学公式。
- 页表算子应优先验证物理连续性，再决定是否值得为特定 workload 建立短路径。

## 最终效果

| 指标 | 结果 |
|---|---:|
| 正确性 | 7/7 平台通过 |
| 平均加速比 | **9.35×** |
| 最佳单平台 | 沐曦 **16.19×** |
