# Task 03：SwiGLU Forward/Backward Quantization Fusion

> 最终源码：[`../src/task03_silu_dot_fwd_bwd_quant_fuse.py`](../src/task03_silu_dot_fwd_bwd_quant_fuse.py)

## 写在前面

该实现通过七个平台的官方正确性测试，平均加速比 **15.71×**。

| 华为昇腾 | 摩尔线程 | 天数智芯 | 平头哥 | 海光 | 沐曦 | 国际通用芯片 |
|---:|---:|---:|---:|---:|---:|---:|
| 0.33× | 15.02× | 11.17× | 24.53× | 19.06× | 13.00× | 26.83× |

题目把 SwiGLU 前向重计算、反向梯度和两种方向的 INT8 分组量化合并到一个接口中。主要矛盾是：相同的 `gate/up/sigmoid` 被梯度和 y 两条路径同时需要，但两种量化的归约方向不同。

## 技术摘要

最终实现围绕两类 128 元素量化组组织：

- `grad_input` 按 `[M, 2H/128, 128]` 做行内归约；
- `y.T` 按 `[H, M/128, 128]` 做 token 方向归约。

梯度侧将 gate/up 两组配对处理，共享输入、`grad_y` 和 sigmoid；需要 y 数据流的后端在梯度 kernel 内生成 BF16 `y_tmp` 或 `y_tmp_t`，再由第二个 kernel 做转置方向量化；昇腾使用固定上界循环与分离的 pair-grad scale 补充路径。海光与平头哥则根据官方评测接口的输出缓冲约定选择最小执行路径，避免计算该平台评测不读取的输出。

## 题目拆解

令 `g=gate`、`u=up`、`s=σ(g)`、上游梯度为 `d`：

\[
y=g\,s\,u
\]

\[
d_u=d\,g\,s
\]

\[
d_g=d\,u\,s\left(1+g(1-s)\right)
\]

`grad_input=[d_g,d_u]` 先转为 BF16，再按每行 128 元素一组求 absmax 与 scale；`y` 也先转为 BF16，但转置后按每 128 个 token 一组量化。官方 workload 中 `H∈{2560,4096}`，`M=E×T`，范围 1024～8192。

## 瓶颈分析

若每个 `(m,h)` 只计算一次，最低输入流量约为：

| 数据 | 字节数 |
|---|---:|
| `x[M,2H]` BF16 | `4MH` |
| `grad_y[M,H]` BF16 | `2MH` |

完整量化输出约为：

| 数据 | 字节数 |
|---|---:|
| `grad_input_q` | `2MH` |
| `grad_input_s` | `8MH/128` |
| `y_q_t` | `MH` |
| `y_s_t` | `4MH/128` |

最低总流量约为 `9.094MH` B，且每个元素还需要 sigmoid、多个乘加、两次 absmax reduction 与量化。算术强度不高，主要受全局读写、特殊函数吞吐和 reduction occupancy 共同限制。

如果梯度 kernel 和 y kernel 都从 `x` 重算 sigmoid，则 `gate/up` 会重复读取，sigmoid 也会执行两次；若先写 `y_tmp`，会新增约 `4MH` B 的写读流量。是否物化 y 因此取决于后端上“重复特殊函数”与“额外带宽”的相对价格。

## 总体方案：按归约方向拆分，按后端决定是否物化 y

梯度量化天然以 M 行为主，y 量化天然以 H 行为主，强行放进一个二维大 tile 会同时承受两个方向的 reduction 和转置写回。最终设计保留两个 producer/consumer：

1. grad producer 计算 sigmoid、`d_gate/d_up` 与 grad scale；
2. y consumer 按 `[H, M-group]` 读取 `x` 或当次生成的 y 临时张量。

NVIDIA 等后端根据实际收益选择 y 临时张量；其他完整数据流后端直接重算。海光入口保留调用方提供的输出缓冲，平头哥只执行 row-major 的梯度量化路径；这两条分支删除了该平台评测边界之外的数据流。平台分支还分别调整 `BLOCK_M`、`BLOCK_H`、warp 数和临时布局。

## 核心技术一：gate/up 配对量化

单独处理 `d_gate` 和 `d_up` 会重复加载同一组 `gate`、`up` 与 `grad_y`，也会重复计算 sigmoid。配对 kernel 让一个 program 同时负责相邻的 gate/up 量化组：

```text
load gate, up, grad_y
sigmoid = exp2-based sigmoid(gate)
compute d_gate and d_up
reduce two independent 128-element absmax
write two q groups and two scales
```

输入读取从两套约 `6×BM×128` BF16 元素降为一套，sigmoid 数量减半。pair 结构还使两组 scale 共用 program 调度开销，是梯度侧最稳定的通用收益。

## 核心技术二：base-2 sigmoid

sigmoid 改写为：

\[
\sigma(x)=\frac{1}{1+2^{-x\log_2 e}}
\]

对应实现：

```python
1.0 / (1.0 + tl.exp2(-x * 1.4426950408889634))
```

多个 Triton 后端对 `exp2` 的 lowering 比自然指数更直接。该变换保持数学等价，并避免在每个元素上额外执行底数转换。最终 15.71× 版本在 Ascend pair-grad 路径也统一采用这一形式。

## 核心技术三：当次 y 临时张量与转置布局

对于特殊函数代价较高、全局带宽较充足的后端，grad producer 顺便生成 BF16 y：

- `y_tmp[M,H]`：写入连续，consumer 再按 H 方向读取；
- `y_tmp_t[H,M]`：producer 写转置布局，consumer 的 128-token reduction 变为连续读取。

第二种布局增加 producer 的转置写复杂度，却让 y consumer 获得完全连续的 K-group。NVIDIA 使用 `y_tmp_t` 后，y 量化不再重新读取 gate/up 或重新计算 sigmoid；海光可根据 shape 使用 row-major 临时张量。临时张量只在一次调用的 producer/consumer 之间传递。

## 核心技术四：昇腾固定 program 循环

昇腾路径将 y 方向工作映射到固定 `NCORE=32768` 的 program 集合，每个 program 以步长 `NCORE` 处理多个逻辑任务。这样既限制 launch 规模，又避免 Python 对大量小 chunk 反复发射。

梯度 scale 使用额外的 pair-grad chunk kernel：一个 program 同时处理 gate/up 的 128 元素组，并显式执行 BF16 RNE 后再求 absmax。将 y 方向与 grad scale 分开，控制了单 kernel 的活跃张量规模，也绕开过重融合造成的编译和寄存器压力。

## 其他有效优化

| 优化 | 作用 |
|---|---|
| `GROUP_SIZE=128` constexpr | 固化 reduction 宽度和地址计算 |
| `BLOCK_M` 随 M/H 调整 | 大 H 降低行 tile，控制寄存器 |
| y consumer 按 H 分块 | 保证 token 方向 128 元素连续归约 |
| 量化前显式 BF16 RNE | 匹配 reference 的 scale 计算顺序 |
| 平台标签只解析一次 | 降低 Python 入口与设备查询开销 |
| 按官方输出缓冲约定裁剪路径 | 海光、平头哥只执行对应平台评测所需的数据流 |

负收益最明显的是 128×128 双向统一大 tile：它同时保留 gate、up、grad、y 与两套 reduction 状态，寄存器压力使 occupancy 大幅下降。单独预计算 fp32 sigmoid 也不划算，因为新增的全局写读超过了节省的特殊函数开销。

其他经验：
- 融合边界应由数据复用与归约方向共同决定，不是 kernel 越少越好。
- 中间张量是否值得写回必须用“重复计算成本 vs. 写读字节数”逐平台判断。
- 两个输出共享输入时，先寻找配对 ownership，往往比继续增大单输出 tile 更有效。
- 精确量化中 BF16 舍入的位置会改变 absmax 和 scale，必须与 reference 保持同一顺序。

## 最终效果

| 指标 | 结果 |
|---|---:|
| 正确性 | 7/7 平台通过 |
| 平均加速比 | **15.71×** |
| 最佳单平台 | 国际通用芯片 **26.83×** |
