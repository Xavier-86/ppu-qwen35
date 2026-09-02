# DeepEP-for-sail 与 sailbandwidth <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [第一章 DeepEP-for-sail](#第一章-deepep-for-sail)
  - [1. 项目概述](#1-项目概述)
  - [2. 功能扩展和优化](#2-功能扩展和优化)
  - [3. API 指南](#3-api-指南)
  - [4. 环境变量](#4-环境变量)
  - [5. 示例](#5-示例)
- [第二章 sailbandwidth 使用指南](#第二章-sailbandwidth-使用指南)
  - [1. 概述](#1-概述)
  - [2. 参数介绍](#2-参数介绍)
  - [3. 示例](#3-示例)


## 第一章 DeepEP-for-sail

DeepEP-for-sail 是针对平头哥 PPU 架构的专家并行（Expert Parallelism, EP）通信库，基于 DeepSeek 开源项目 DeepEP 二次开发，主要面向 MoE 模型的训练与推理场景。

### 1. 项目概述

#### 1.1. 项目简介

DeepEP-for-sail 项目是基于 DeepSeek 开源项目 DeepEP 进行的二次开发，针对平头哥 PPU 架构以及指令特点进行了相应的适配以及优化，并进行了功能扩展以及性能优化。项目也会随着社区的演进而不断更新，同时计划未来开源到 GitHub 社区。

#### 1.2. 适用范围说明

- **支持硬件卡**：仅支持平头哥自研真武 610、真武 610E、真武 805、真武 810、真武 810E 以及真武 M890 类型。
- **机内卡间通信协议**：仅支持平头哥自研的 PPU 卡之间的通信协议，即 ICN Link。
- **机间卡间通信协议**：支持 `Mellanox CX6/CX7` 标准 RDMA 网卡（若使用阿里云自研高性能网卡 `EIC`，请联系阿里云获取相应支持）；自真武 M890 起，支持 ICN Link 跨 ICN Switch 的自研通信协议。
- **量化类型支持**：全系产品都支持 INT8 量化，只有真武 M890 类型支持 FP8 和 MXFP4 类型。

#### 1.3. 核心功能扩展及优化

参考下文「[功能扩展和优化](#2-功能扩展和优化)」章节。

#### 1.4. 技术架构

##### 1.4.1. 核心组件

1. **Buffer 类**：核心的专家并行通信缓冲区。
   - 支持高吞吐量节点内全对全（使用 ICN Link）。
   - 支持高吞吐量节点间全对全（使用 RDMA 和 ICN Link）。
   - 支持低延迟全对全（使用 RDMA）。

2. **Config 类**：性能调优配置。
   - 为不同规模的 EP 组提供推荐配置参数。

3. **EventOverlap 类**：HGGC 事件管理。
   - 提供更好的计算与通信重叠便利性。

##### 1.4.2. 主要接口

训练和推理预填充阶段：

```python
# 初始化缓冲区
buffer = Buffer(group, num_nvl_bytes, num_rdma_bytes)

# 分发前向传播
recv_x, recv_topk_idx, recv_topk_weights, num_recv_tokens_per_expert_list, handle, event =\
    buffer.dispatch(x, topk_idx=topk_idx, topk_weights=topk_weights, ...)

# 合并前向传播
combined_x, event = buffer.combine(x, handle, ...)

# 分发反向传播
combined_grad_x, combined_grad_recv_topk_weights, event =\
    buffer.combine(grad_recv_x, handle, topk_weights=grad_recv_topk_weights, ...)

# 合并反向传播
grad_x, event = buffer.dispatch(grad_combined_x, handle, ...)
```

推理解码阶段：

```python
# 初始化低延迟缓冲区
buffer = Buffer(group, 0, num_rdma_bytes, low_latency_mode=True, num_qps_per_rank=num_experts // group.size())

# 低延迟分发
recv_hidden_states, recv_expert_count, handle, event, hook =\
    buffer.low_latency_dispatch(hidden_states, topk_idx, num_max_dispatch_tokens_per_rank, num_experts, ...)

# 低延迟合并
combined_hidden_states, event_overlap, hook =\
    buffer.low_latency_combine(hidden_states, topk_idx, topk_weights, handle, ...)
```

#### 1.5. 安装要求

硬件依赖：

- PPU 架构。
- ICN Link 用于节点内通信。
- RDMA 网络用于节点间通信。

软件依赖：

- Python 3.8 及以上版本。
- PyTorch 2.1 及以上版本。

#### 1.6. 安装使用示例

从官方 Release 渠道获取操作系统以及其他版本匹配的 whl 安装包：

```bash
pip install deep_ep-2.1.0+0e10010-cp312-cp312-linux_x86_64.whl
```

然后在 Python 项目中导入 `deep_ep` 即可使用。

#### 1.7. 发展路线

- [x] ICN Link 全互联超节点支持。
- [x] 支持 Dispatch INT8 group / channel 量化, FP8 channel 量化。
- [x] 支持 MXFP4 Dispatch，以及 Combine FP8/INT8 量化。
- [ ] 优化 Dispatch & Combine 计算资源,根据 TopK workload 动态分配，加速算子执行流程
- [ ] 支持 Intranode 多机走 ICN Link
- [ ] 支持 DeepEPv2 版本

### 2. 功能扩展和优化

#### 2.1. 功能扩展

##### 2.1.1. 灵活支持通信规模

- **单机最大卡数**：

    当前社区 DeepEP 版本固定了单机最大卡数为 8，也就是定义了 `NUM_MAX_NVL_PEERS` 为 `8`。平头哥的硬件系列之间会有差异，相关配置也有差异，比如真武 810 单机为 8 卡，而真武 810E 单机会有 16 卡，因此需要支持最大单机 16 卡规模。

- **单机通信卡数定制**：

    目前社区 DeepEP 版本对于多机场景下，单机参与的卡数固定为 `NUM_MAX_NVL_PEERS`。比如对于 Low Latency 多机通信场景，用户可以灵活指定单机实际参与卡的数量，比如 2 机 8 卡，每台机器 4 张卡等等。

- **ICN64 超节点**：

    平头哥的产品自真武 M890 起，开始支持 ICN Switch，包括单机内部 PPU 卡之间通过 Switch 互联，不同机器的 PPU 卡之间也可以通过 ICN Switch 互联。目前可以支持真武 M890 8 机 64 张卡全 ICN 互联的 Topology 集群。

##### 2.1.2. 丰富的量化功能

对于 Low Latency Dispatch 和 Combine 算子，提供了丰富的量化功能，在精度可控制的范围内，大幅提升了 Decode 阶段的吞吐能力。社区 DeepEP 目前仅支持 Dispatch 阶段的量化操作，并且仅支持 FP8 数据类型，平头哥进行了扩展，不仅扩展了数据类型，而且也扩展支持 Combine 阶段的量化能力，在牺牲一定精度的情况下，通过减少通信数据量，大幅降低通信 Latency。

- **量化模式**：

    目前社区 DeepEP 仅支持 Group Wise 量化规模，也就是 128 长度规模出一个 scaler 因子，比如以 Hidden size 7168 为例，会量化出 56 个 scaler 数据。当然对于 MXFP4 类型，由于硬件设计考虑，目前仅支持 group 大小为 32 的规模。还支持 Channel Wise 量化规模，也就是整个 Hidden Size 出一个 scaler。

- **量化数据类型**：

    目前社区 DeepEP 仅支持 FP8 量化数据类型，平头哥会根据硬件支持情况，分别扩展支持了 INT8 和 MXFP4，同时也都支持上面所说的 Group 和 Channel 量化模式，其中 MXFP4 由于硬件设计原因，目前仅支持 Group 量化。平头哥真武 M890 支持全部的数类型，包括 INT8, FP8 和 MXFP4，而其他产品，比如真武 810 和 810E 目前仅支持 INT8。

##### 2.1.3. 集成 SBO (Single Batch Overlap) 功能

该功能集成自 DeepEP 社区 AntGroup-Opt 分支，开源主线并没有合入。SBO 功能通过信号机制将 Down GEMM 计算与 Combine Send 通信以 `block_m`（Token 数量，GEMM 每次计算处理的 Token 数量）为粒度进行重叠，以降低推理解码阶段的端到端延迟。该功能需配合 DeepGEMM 使用。

##### 2.1.4. 支持通信算子超时时间定制

在实际的模型推理场景下，各个通信的卡在 WarmUp 阶段耗时差异比较大，导致部分卡先下发的算子在执行时等待时间超过固定时长而报错。为此新增了 API `set_timeout_seconds()` 方便用户根据自身硬件和软件环境设置合适的超时时间，避免模型实际运行场景下的互相依赖等待过长导致的 timeout 错误。

##### 2.1.5. 增强 Low Latency 性能 Torch Profiler 工具

当用户使用和测试 low latency 脚本 `test_low_latency.py` 时，可以通过增加测试参数来进行性能 Profiler，它会生成对应的 json profile 文件，最后使用 Perfetto UI 非常直观地分析相关性能问题。

测试脚本使能 Torch Profiler：

```bash
python ./tests/test_low_latency.py --trace
```

合并所有卡的报告。Profile 完之后，可以看到当前目录下每个 PPU 卡的进程生成了一份各自的 json 文件：

```bash
ls -l ./
-rw-r--r--  1 root root    711239 Jul  3 16:12 profiler_trace_rank-0_BF16__0.json
-rw-r--r--  1 root root    723223 Jul  3 16:12 profiler_trace_rank-1_BF16__0.json
-rw-r--r--  1 root root    723232 Jul  3 16:12 profiler_trace_rank-2_BF16__0.json
-rw-r--r--  1 root root    723217 Jul  3 16:12 profiler_trace_rank-3_BF16__0.json
-rw-r--r--  1 root root    723216 Jul  3 16:12 profiler_trace_rank-4_BF16__0.json
-rw-r--r--  1 root root    711244 Jul  3 16:12 profiler_trace_rank-5_BF16__0.json
-rw-r--r--  1 root root    723219 Jul  3 16:12 profiler_trace_rank-6_BF16__0.json
-rw-r--r--  1 root root    723221 Jul  3 16:12 profiler_trace_rank-7_BF16__0.json
```

使用以下命令对齐时间戳之后，合并生成一个统一的文件，方便对齐查看同一个时间点所有卡的运行情况：

```bash
python ./tests/deep_ep_merge_json.py
```

合并为一个统一的 json 文件：`merged_profile.json`。

使用 Perfetto UI 打开合并后的 Json 文件：

![性能 Benchmark](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784124972931/9e68cc6b5be815e525e06b1c6ae5eb3c/low_latency_trace.png)

#### 2.2. 性能优化

- **不同 Hidden Size 优化**：优化原有代码对于 Hidden Size 7168 的处理，提升其他不同 Hidden Size 的处理性能。

    在数据的发送或者接收过程中，通过 UNROLL 大小来增加指令密度以达到打满底层通信物理链路带宽。当前社区 DeepEP 指定的 `UNROLL_FACTOR` 大小为 7，主要是适配 Hidden Size 7168，结合 BF16 数据类型，每个采用 V4 指令的 Warp 线程刚好只需要 4 轮操作即可完成一个 token 的数据传输。但是其他 Hidden Size 在使用 `UNROLL_FACTOR` 大小为 7 的参数时，比如 `3072` 会导致数据大小 Stride 不满足大小要求，被强制走到实际并没有 UNROLL 的流程，导致性能下降比较明显。

- **Internode 多 QP 优化**：通过增加连接的 QP 数量，进一步提升网络通信性能。

    由于目前的网卡都是 Bond 网卡，底层物理实际上有两个通道，单个 QP 无法有效利用完整的网卡带宽，此时通过增加每个链接的 QP 数量，可以大幅提升网卡通信带宽。

- **PPU 网卡亲和性自动检查**：通过自动搜索和绑定亲和性网卡，提升网络通信性能。

    目前的 PPU 物理机型通常都没有给每一个 PPU 卡配置对应的网卡，再加之 PCIe Switch 虚拟化之后，导致部分 PPU 卡无法正确识别临近的网卡，一旦无法使用最佳临近网卡，就会导致数据的通信能力大幅下降。目前通过自动搜索，匹配亲和性网卡，让 PPU 正确识别到自己临近的最佳网卡，能大幅提升网络通信能力。

平台扩展关联：DeepEP dispatch/combine 面向多卡 MoE/EP，不属于本次单卡 Qwen3.5-2B 比赛路径；`--trace` + Perfetto 流程仅作通用通信压测参考。

### 3. API 指南

DeepEP-for-sail 在保留了一部分开源版本提供的 API 基础上，也对 API 层面做了扩展以支持新开发的功能。

#### 3.1. 核心 API 更改

##### 3.1.1. 低延迟操作

**low_latency_dispatch**

```python
def low_latency_dispatch(self, x: torch.Tensor, topk_idx: torch.Tensor,
                         num_max_dispatch_tokens_per_rank: int, num_experts: int,
                         cumulative_local_expert_recv_stats: Optional[torch.Tensor] = None,
                         dispatch_wait_recv_cost_stats: Optional[torch.Tensor] = None,
                         use_fp8: bool = False, round_scale: bool = False,
                         use_ue8m0: bool = False, use_mxfp4: bool = False,
                         async_finish: bool = False, return_recv_hook: bool = False,
                         use_int8: bool = False, quant_size: int = 128) ->\
    Tuple[Tuple[torch.Tensor, torch.Tensor], torch.Tensor, Tuple, EventOverlap, Callable]
```

低延迟分发实现。

原始保留参数：

- `x`: 形状为 `[num_tokens, hidden]` 的 tensor。
- `topk_idx`: 形状为 `[num_tokens, num_topk]` 的 tensor。
- `num_max_dispatch_tokens_per_rank`: 每个 rank 的最大分发 token 数。
- `num_experts`: 专家总数。
- `cumulative_local_expert_recv_stats`: 累积专家计数统计。
- `dispatch_wait_recv_cost_stats`: 等待接收成本统计。
- `use_fp8`: 是否启用 FP8 转换。目前仅在真武 M890 上面支持。
- `round_scale`: 是否将缩放因子四舍五入为 2 的幂。
- `use_ue8m0`: 是否使用 UE8M0 作为缩放因子格式。
- `async_finish`: 如果设置，当前流不会等待通信内核完成。
- `return_recv_hook`: 是否返回接收钩子。

PPU 扩展参数说明：

- `use_int8`：用来指定本次 dispatch 操作是否使用 INT8 量化数据类型，目前所有 PPU 产品均支持。
- `use_mxfp4`：用来指定本次 dispatch 操作是否使用 MXFP4 量化数据类型，目前仅支持真武 M890 产品。
- `quant_size`：用来指定量化组大小，目前 INT8 和 FP8 同时支持 quant_size 为 128 的 group 量化模式，和 Hidden size 大小，也就是 Per Token 大小的量化模式，而 MXFP4 由于硬件特性，仅支持 quant_size 为 32 的 group 量化模式。

返回值：

- `recv_x`: 每个专家接收到的 token。
- `recv_count`: 每个专家接收到的 token 数。
- `handle`: 通信句柄。
- `event`: 执行内核后的事件。
- `hook`: 接收钩子函数。

**low_latency_combine**

```python
def low_latency_combine(self, x: torch.Tensor, topk_idx: torch.Tensor,
                        topk_weights: torch.Tensor,
                        handle: tuple, overlap: bool = False,
                        packed_recv_count: torch.Tensor = None,
                        comp_signal: torch.Tensor = None, block_m: int = 64,
                        threshold: int = 0,
                        num_sms: int = 3, zero_copy: bool = False,
                        async_finish: bool = False,
                        return_recv_hook: bool = False,
                        out: Optional[torch.Tensor] = None,
                        combine_wait_recv_cost_stats: Optional[torch.Tensor] = None,
                        use_fp8: bool = False, round_scale: bool = False,
                        use_int8: bool = False, quant_size: int = 128) ->\
    Tuple[torch.Tensor, EventOverlap, Callable]
```

低延迟合并实现。

原始保留参数：

- `x`: 形状为 `[num_local_experts, num_max_dispatch_tokens_per_rank * num_ranks, hidden]` 的 tensor。
- `topk_idx`: 形状为 `[num_combined_tokens, num_topk]` 的 tensor。
- `topk_weights`: 形状为 `[num_combined_tokens, num_topk]` 的 tensor。
- `handle`: 分发函数给出的通信句柄。
- `overlap`: 是否与 combine 发送阶段重叠 down gemm。
- `packed_recv_count`: 每个专家接收到的 token 数。
- `comp_signal`: DeepGEMM 的处理进度信号。
- `block_m`: 由 DeepGEMM 设置。
- `threshold`: 由 DeepGEMM 设置。
- `num_sms`: low_latency_combine 发送使用的 sm 数量。
- `zero_copy`: 张量是否已复制到 RDMA 缓冲区。
- `async_finish`: 如果设置，当前流不会等待通信内核完成。
- `return_recv_hook`: 是否返回接收钩子。
- `out`: 输出 tensor。
- `combine_wait_recv_cost_stats`: 等待接收成本统计。

PPU 扩展参数说明：

- `use_int8`：用来指定本次 combine 操作是否使用 INT8 量化数据类型，目前所有 PPU 产品均支持。
- `use_fp8`：用来指定本次 combine 操作是否使用 FP8 量化数据类型，目前仅支持真武 M890 产品。
- `quant_size`：用来指定量化组大小，目前 INT8 和 FP8 同时支持 `quant_size` 为 128 或者 512 的 group 量化模式，以及 Hidden size 大小，也就是 Per Token 大小的量化模式。
- `round_scale`: 是否将缩放因子四舍五入为 2 的幂。

返回值：

- `combined_x`: 归约的 token tensor。
- `event`: 执行内核后的事件。
- `hook`: 接收钩子函数。

##### 3.1.2. 辅助功能

**barrier**

```python
def barrier(self)
```

主要用于 Benchmark 时能通过 barrier 操作消除 Topk 导致的 workload 不均衡引起的 PPU 卡之间的 Desync 行为。传统的 `dist.barrier()` 操作主要是基于 `Ring` 算法实现的，在 `barrier` 这种数据量极小的操作，卡之间，特别是多机场景下，它们退出时间依然会有可能出现比较大的时间差，不是一个非常可靠的 `barrier` 操作。本 `barrier` 由内部实现，既避免了 `dist.barrier()` 复杂的 Host 多线程调用流程，又解决了 `Ring` 方式存在的 gap 问题，相比而言更加轻量级，而且同步稳定性更好。

**get_next_low_latency_combine_buffer**

```python
def get_next_low_latency_combine_buffer(self, handle: object, dtype: torch.dtype = torch.bfloat16, quant_size: int = 128) -> torch.Tensor
```

获取下一个低延迟合并的原始注册 RDMA 缓冲区 tensor，主要用于支持 Zero Copy 的功能特性，减少一次 RDMA 传输时的拷贝操作。由于支持 Combine 操作的量化功能，所以在不同数据类型以及量化模式下，对 Buffer 大小的需求是不一样的，所以需要扩展参数支持具体的数据类型 `dtype` 和量化大小 `quant_size`。

参数：

- `handle`: 分发函数给出的通信句柄。
- `dtype`: 指定分发的数据类型。
- `quant_size`: 如果分发数据类型是 INT8 or FP8 量化，额外指定量化大小。

返回值：

- `buffer`: 原始 RDMA 低延迟缓冲区。

**set_timeout_seconds**

```python
def set_timeout_seconds(self, timeout_secs: int = 100)
```

设置通信算子执行过程中等待的超时秒数。

参数：

- `timeout_secs`: 分发和合并使用的超时秒数。

#### 3.2. 使用示例

训练和推理预填充：

```python
import torch
import torch.distributed as dist
from typing import List, Tuple, Optional, Union

from deep_ep import Buffer, EventOverlap

# 通信缓冲区（将在运行时分配）
_buffer: Optional[Buffer] = None

# 设置要使用的SM数量
Buffer.set_num_sms(24)

# 框架初始化时调用此函数
def get_buffer(group: dist.ProcessGroup, hidden_bytes: int) -> Buffer:
    global _buffer

    # 获取推荐配置
    num_nvl_bytes, num_rdma_bytes = 0, 0
    for config in (Buffer.get_dispatch_config(group.size()), Buffer.get_combine_config(group.size())):
        num_nvl_bytes = max(config.get_nvl_buffer_size_hint(hidden_bytes, group.size()), num_nvl_bytes)
        num_rdma_bytes = max(config.get_rdma_buffer_size_hint(hidden_bytes, group.size()), num_rdma_bytes)

    # 如果缓冲区不存在或大小不足则分配新缓冲区
    if _buffer is None or _buffer.group != group or _buffer.num_nvl_bytes < num_nvl_bytes or _buffer.num_rdma_bytes < num_rdma_bytes:
        _buffer = Buffer(group, num_nvl_bytes, num_rdma_bytes)
    return _buffer

def get_hidden_bytes(x: torch.Tensor) -> int:
    t = x[0] if isinstance(x, tuple) else x
    return t.size(1) * max(t.element_size(), 2)

def dispatch_forward(x: Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]],
                     topk_idx: torch.Tensor, topk_weights: torch.Tensor,
                     num_experts: int, previous_event: Optional[EventOverlap] = None) ->\
        Tuple[Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]], torch.Tensor, torch.Tensor, List, Tuple, EventOverlap]:

    global _buffer

    # 计算分发前的实际布局
    num_tokens_per_rank, num_tokens_per_rdma_rank, num_tokens_per_expert, is_token_in_rank, previous_event =\
        _buffer.get_dispatch_layout(topk_idx, num_experts,
                                    previous_event=previous_event, async_finish=True,
                                    allocate_on_comm_stream=previous_event is not None)

    # 执行MoE分发
    recv_x, recv_topk_idx, recv_topk_weights, num_recv_tokens_per_expert_list, handle, event =\
        _buffer.dispatch(x, topk_idx=topk_idx, topk_weights=topk_weights,
                         num_tokens_per_rank=num_tokens_per_rank,
                         num_tokens_per_rdma_rank=num_tokens_per_rdma_rank,
                         is_token_in_rank=is_token_in_rank,
                         num_tokens_per_expert=num_tokens_per_expert,
                         previous_event=previous_event, async_finish=True,
                         allocate_on_comm_stream=True)

    return recv_x, recv_topk_idx, recv_topk_weights, num_recv_tokens_per_expert_list, handle, event

def dispatch_backward(grad_recv_x: torch.Tensor, grad_recv_topk_weights: torch.Tensor, handle: Tuple) ->\
        Tuple[torch.Tensor, torch.Tensor, EventOverlap]:
    global _buffer

    # MoE分发的反向过程实际上是合并
    combined_grad_x, combined_grad_recv_topk_weights, event =\
        _buffer.combine(grad_recv_x, handle, topk_weights=grad_recv_topk_weights, async_finish=True)

    return combined_grad_x, combined_grad_recv_topk_weights, event

def combine_forward(x: torch.Tensor, handle: Tuple, previous_event: Optional[EventOverlap] = None) ->\
        Tuple[torch.Tensor, EventOverlap]:
    global _buffer

    # 执行MoE合并
    combined_x, _, event = _buffer.combine(x, handle, async_finish=True, previous_event=previous_event,
                                           allocate_on_comm_stream=previous_event is not None)

    return combined_x, event

def combine_backward(grad_combined_x: Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]],
                     handle: Tuple, previous_event: Optional[EventOverlap] = None) ->\
        Tuple[Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]], EventOverlap]:
    global _buffer

    # MoE合并的反向过程实际上是分发
    grad_x, _, _, _, _, event = _buffer.dispatch(grad_combined_x, handle=handle, async_finish=True,
                                                 previous_event=previous_event,
                                                 allocate_on_comm_stream=previous_event is not None)

    return grad_x, event
```

推理解码：

```python
import torch
import torch.distributed as dist
from typing import Tuple, Optional

from deep_ep import Buffer

# 通信缓冲区（将在运行时分配）
# NOTES: 低延迟模式没有SM控制API
_buffer: Optional[Buffer] = None

# 框架初始化时调用此函数
def get_buffer(group: dist.ProcessGroup, num_max_dispatch_tokens_per_rank: int,
               hidden: int, num_experts: int) -> Buffer:
    # NOTES: 低延迟模式将消耗比正常模式更多的空间
    # 因此我们推荐num_max_dispatch_tokens_per_rank（解码引擎中的实际批处理大小）应小于256
    global _buffer
    num_rdma_bytes = Buffer.get_low_latency_rdma_size_hint(num_max_dispatch_tokens_per_rank,
                                                          hidden, group.size(), num_experts)

    # 如果缓冲区不存在或大小不足则分配新缓冲区
    if _buffer is None or _buffer.group != group or not _buffer.low_latency_mode or _buffer.num_rdma_bytes < num_rdma_bytes:
        # NOTES: 为获得最佳性能，QP数量**必须**等于本地专家数量
        assert num_experts % group.size() == 0
        _buffer = Buffer(group, 0, num_rdma_bytes, low_latency_mode=True,
                        num_qps_per_rank=num_experts // group.size())
    return _buffer

def low_latency_dispatch(hidden_states: torch.Tensor, topk_idx: torch.Tensor,
                         num_max_dispatch_tokens_per_rank: int, num_experts: int):
    global _buffer

    # 执行MoE分发，与HGGC图兼容
    recv_hidden_states, recv_expert_count, handle, event, hook =\
        _buffer.low_latency_dispatch(hidden_states, topk_idx,
                                    num_max_dispatch_tokens_per_rank, num_experts,
                                    async_finish=False, return_recv_hook=True)

    # NOTES: 只有在调用hook()后才会接收到实际的tensor，
    # 这对于双批次重叠很有用，但**不占用任何GPU SM**
    # 如果不想重叠，请设置return_recv_hook=False
    # 之后可以使用我们的GEMM库以这种特定格式进行计算

    return recv_hidden_states, recv_expert_count, handle, event, hook

def low_latency_combine(hidden_states: torch.Tensor,
                        topk_idx: torch.Tensor, topk_weights: torch.Tensor, handle: Tuple):
    global _buffer

    # 执行MoE合并，与HGGC图兼容
    combined_hidden_states, event_overlap, hook =\
        _buffer.low_latency_combine(hidden_states, topk_idx, topk_weights, handle,
                                    async_finish=False, return_recv_hook=True)

    # NOTES: 行为与分发内核中描述的相同
    return combined_hidden_states, event_overlap, hook
```

### 4. 环境变量

DeepEP-for-sail 使用多种环境变量来控制其构建过程、运行时行为、性能调优和调试功能。这些环境变量可以帮助用户根据具体的硬件环境和应用需求来优化通信的性能。以下详细介绍 DeepEP 中定制化的、与 PPU 相关的环境变量。

#### 4.1. 运行时环境变量

**DEEPEP_INTERNODE_TRANSPORT_MODE**

- 作用：设置节点间传输模式。
- 默认值：`1`。
- 可选值：
  - `0`: DeepEP 定义的 IBGDA。
  - `1`: sailSHMEM IBRC。
  - `2`: sailSHMEM IBGDA。
- 说明：控制节点间通信使用的传输模式。

**DEEPEP_DISABLE_NETWORK**

- 作用：禁用网络功能以及初始化操作。
- 默认值：`0`（不禁用）。
- 可选值：`0`（不禁用）或 `1`（禁用）。
- 说明：设置该环境变量为 `1`，DeepEP 会直接跳过网络相关的初始化以及功能调用。适用于 PPU 集群下面网卡或者网络环境有故障时，保证 ICN 互联的 case 依然可以正常运行。比如 ICN 64 全互联集群环境下，如果网卡出现故障，或者网络不通，甚至物理上都没有配置网卡时，设置该环境变量，依然可以运行 ICN 相关的用例。

**DEEPEP_TIMEOUT_SECONDS**

- 作用：设置超时时间（秒）。
- 默认值：无。
- 说明：设置分发和合并 Kernel 操作的等待超时时间。如果设置为 `-1`，则永不超时。

**DEEPEP_NUM_MAX_ICN_PEERS**

- 作用：设置单机内部 ICN 连接的最大 Peer Ranks 数量。
- 默认值：系统检测值。
- 说明：设置单节点内 ICN 连接的最大 Peer 数量。在多机场景下，如果你希望每台机器上面使用的 PPU 卡数量不为实际单机最大卡数，可以通过设置这个环境变量来指定。主要原因是，上层框架在构建 DeepEP Buffer 对象时，需要提前获知 RDMA 或者 NVLink 域内的缓冲区大小，这个时候 DeepEP 本身还没有进行任何初始化，只能通过提前通过环境变量来获取通信卡数量，进而用来分配合适的缓冲区大小。

#### 4.2. 使用示例

基本运行示范：

```bash
# 设置分布式训练环境变量，以两机 internode 场景为例
MASTER_ADDR="$master" MASTER_PORT=12345 WORLD_SIZE=2 RANK=0 python tests/test_internode.py --num-pernode 8
MASTER_ADDR="$master" MASTER_PORT=12345 WORLD_SIZE=2 RANK=1 python tests/test_internode.py --num-pernode 8

# 使用 pytorch 自带的 torchrun 运行多机测试，以两机 low latency 场景为例
torchrun --master_addr $master --master_port 45678 --nnodes 2 --node_rank 0 --nproc_per_node 1 ./tests/test_low_latency.py
torchrun --master_addr $master --master_port 45678 --nnodes 2 --node_rank 1 --nproc_per_node 1 ./tests/test_low_latency.py

# 单机 Low Latency，跳过网络相关的初始化配置
DEEPEP_DISABLE_NETWORK=1 python tests/test_low_latency.py --num-pernode 8

# 查看各种运行参数配置
python tests/test_intranode.py --help
```

#### 4.3. 注意事项

1. **环境变量优先级**：某些环境变量在代码中有默认值，通过环境变量设置可以覆盖这些默认值。
2. **依赖关系**：某些环境变量之间存在依赖关系，例如启用 IBGDA 需要正确设置相关的 NIC 处理器和队列对参数。
3. **硬件兼容性**：不同的环境变量设置可能对特定硬件配置有要求，请根据实际硬件环境进行调整。
4. **性能影响**：修改环境变量可能会显著影响性能，请在生产环境中谨慎调整。
5. **调试建议**：在遇到问题时，可以逐步启用相关的调试环境变量来定位问题根源。

### 5. 示例

本章节通过测试用例来介绍 DeepEP-for-sail 的几个不同 Kernel 的使用方法。

#### 5.1. Intranode 功能

Intranode 主要是用于单机情况下，通过 ICN Link 互联的 PPU 之间的通信。它通常用于模型训练，或者推理中的 Prefill 阶段，主要是满足大数据量的通信需求。

##### 5.1.1. 初始化

```python
import torch
import torch.distributed as dist
from typing import List, Tuple, Optional, Union

from deep_ep import Buffer, EventOverlap

# Communication buffer (will allocate at runtime)
_buffer: Optional[Buffer] = None

# Set the number of SMs to use
# NOTES: this is a static variable
Buffer.set_num_sms(24)


# You may call this function at the framework initialization
def get_buffer(group: dist.ProcessGroup, hidden_bytes: int) -> Buffer:
    global _buffer

    # NOTES: you may also replace `get_*_config` with your auto-tuned results via all the tests
    num_nvl_bytes, num_rdma_bytes = 0, 0
    for config in (Buffer.get_dispatch_config(group.size()), Buffer.get_combine_config(group.size())):
        num_nvl_bytes = max(config.get_nvl_buffer_size_hint(hidden_bytes, group.size()), num_nvl_bytes)
        num_rdma_bytes = max(config.get_rdma_buffer_size_hint(hidden_bytes, group.size()), num_rdma_bytes)

    # Allocate a buffer if not existed or not enough buffer size
    if _buffer is None or _buffer.group != group or _buffer.num_nvl_bytes < num_nvl_bytes or _buffer.num_rdma_bytes < num_rdma_bytes:
        _buffer = Buffer(group, num_nvl_bytes, num_rdma_bytes)
    return _buffer
```

##### 5.1.2. Dispatch 和 Combine 接口调用

进行实际场景下的 dispatch 和 combine 通信操作。

```python
def dispatch_forward(x: Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]],
                     topk_idx: torch.Tensor, topk_weights: torch.Tensor,
                     num_experts: int, previous_event: Optional[EventOverlap] = None) ->\
        Tuple[Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]], torch.Tensor, torch.Tensor, List, Tuple, EventOverlap]:
    # NOTES: an optional `previous_event` means a HGGC event captured that you want to make it as a dependency
    # of the dispatch kernel, it may be useful with communication-computation overlap. For more information, please
    # refer to the docs of `Buffer.dispatch`
    global _buffer

    # Calculate layout before actual dispatch
    num_tokens_per_rank, num_tokens_per_rdma_rank, num_tokens_per_expert, is_token_in_rank, previous_event =\
        _buffer.get_dispatch_layout(topk_idx, num_experts,
                                    previous_event=previous_event, async_finish=True,
                                    allocate_on_comm_stream=previous_event is not None)
    # Do MoE dispatch
    # NOTES: the CPU will wait for GPU's signal to arrive, so this is not compatible with HGGC graph
    # Unless you specify `num_worst_tokens`, but this flag is for intranode only
    # For more advanced usages, please refer to the docs of the `dispatch` function
    recv_x, recv_topk_idx, recv_topk_weights, num_recv_tokens_per_expert_list, handle, event =\
        _buffer.dispatch(x, topk_idx=topk_idx, topk_weights=topk_weights,
                         num_tokens_per_rank=num_tokens_per_rank, num_tokens_per_rdma_rank=num_tokens_per_rdma_rank,
                         is_token_in_rank=is_token_in_rank, num_tokens_per_expert=num_tokens_per_expert,
                         previous_event=previous_event, async_finish=True,
                         allocate_on_comm_stream=True)
    # For event management, please refer to the docs of the `EventOverlap` class
    return recv_x, recv_topk_idx, recv_topk_weights, num_recv_tokens_per_expert_list, handle, event


def dispatch_backward(grad_recv_x: torch.Tensor, grad_recv_topk_weights: torch.Tensor, handle: Tuple) -> \
        Tuple[torch.Tensor, torch.Tensor, EventOverlap]:
    global _buffer

    # The backward process of MoE dispatch is actually a combine
    # For more advanced usages, please refer to the docs of the `combine` function
    combined_grad_x, combined_grad_recv_topk_weights, event =\
        _buffer.combine(grad_recv_x, handle, topk_weights=grad_recv_topk_weights, async_finish=True)

    # For event management, please refer to the docs of the `EventOverlap` class
    return combined_grad_x, combined_grad_recv_topk_weights, event


def combine_forward(x: torch.Tensor, handle: Tuple, previous_event: Optional[EventOverlap] = None) ->\
        Tuple[torch.Tensor, EventOverlap]:
    global _buffer

    # Do MoE combine
    # For more advanced usages, please refer to the docs of the `combine` function
    combined_x, _, event = _buffer.combine(x, handle, async_finish=True, previous_event=previous_event,
                                           allocate_on_comm_stream=previous_event is not None)

    # For event management, please refer to the docs of the `EventOverlap` class
    return combined_x, event


def combine_backward(grad_combined_x: Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]],
                     handle: Tuple, previous_event: Optional[EventOverlap] = None) ->\
        Tuple[Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]], EventOverlap]:
    global _buffer

    # The backward process of MoE combine is actually a dispatch
    # For more advanced usages, please refer to the docs of the `dispatch` function
    grad_x, _, _, _, _, event = _buffer.dispatch(grad_combined_x, handle=handle, async_finish=True,
                                                 previous_event=previous_event,
                                                 allocate_on_comm_stream=previous_event is not None)

    # For event management, please refer to the docs of the `EventOverlap` class
    return grad_x, event
```

##### 5.1.3. Benchmark 测试介绍

DeepEP 自带的 Benchmark 测试脚本使用方法：

```bash
python tests/test_intranode.py --num-pernode 8 --num-experts 256 --num-topk 8 --hidden-size 7168 --num-tokens 4096

-n , --num-pernode    configure ppu num per node; default is 16.
-e , --num-experts    configure number of experts; default is 256.
-k , --num-topk       configure number of topk; default is 8.
--hidden-size         configure hidden size
-t , --num-tokens     configure dispatch or combine token number

更多参数以及说明，可以使用 python tests/test_intranode.py --help 来查询
```

#### 5.2. Internode 功能

Internode 主要是用于多机情况下，单机内 PPU 通过 ICN Link 互联，机器之间通过 RDMA 网卡互联通信的集群架构。它通常用于模型训练，或者推理中的 Prefill 阶段，主要是满足大数据量的通信需求。

##### 5.2.1. 初始化

```python
import torch
import torch.distributed as dist
from typing import List, Tuple, Optional, Union

from deep_ep import Buffer, EventOverlap

# Communication buffer (will allocate at runtime)
_buffer: Optional[Buffer] = None

# Set the number of SMs to use
# NOTES: this is a static variable
Buffer.set_num_sms(24)


# You may call this function at the framework initialization
def get_buffer(group: dist.ProcessGroup, hidden_bytes: int) -> Buffer:
    global _buffer

    # NOTES: you may also replace `get_*_config` with your auto-tuned results via all the tests
    num_nvl_bytes, num_rdma_bytes = 0, 0
    for config in (Buffer.get_dispatch_config(group.size()), Buffer.get_combine_config(group.size())):
        num_nvl_bytes = max(config.get_nvl_buffer_size_hint(hidden_bytes, group.size()), num_nvl_bytes)
        num_rdma_bytes = max(config.get_rdma_buffer_size_hint(hidden_bytes, group.size()), num_rdma_bytes)

    # Allocate a buffer if not existed or not enough buffer size
    if _buffer is None or _buffer.group != group or _buffer.num_nvl_bytes < num_nvl_bytes or _buffer.num_rdma_bytes < num_rdma_bytes:
        _buffer = Buffer(group, num_nvl_bytes, num_rdma_bytes)
    return _buffer
```

##### 5.2.2. Dispatch 和 Combine 接口调用

进行实际场景下的 dispatch 和 combine 通信操作。

```python
def dispatch_forward(x: Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]],
                     topk_idx: torch.Tensor, topk_weights: torch.Tensor,
                     num_experts: int, previous_event: Optional[EventOverlap] = None) ->\
        Tuple[Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]], torch.Tensor, torch.Tensor, List, Tuple, EventOverlap]:
    # NOTES: an optional `previous_event` means a HGGC event captured that you want to make it as a dependency
    # of the dispatch kernel, it may be useful with communication-computation overlap. For more information, please
    # refer to the docs of `Buffer.dispatch`
    global _buffer

    # Calculate layout before actual dispatch
    num_tokens_per_rank, num_tokens_per_rdma_rank, num_tokens_per_expert, is_token_in_rank, previous_event =\
        _buffer.get_dispatch_layout(topk_idx, num_experts,
                                    previous_event=previous_event, async_finish=True,
                                    allocate_on_comm_stream=previous_event is not None)
    # Do MoE dispatch
    # NOTES: the CPU will wait for GPU's signal to arrive, so this is not compatible with HGGC graph
    # Unless you specify `num_worst_tokens`, but this flag is for intranode only
    # For more advanced usages, please refer to the docs of the `dispatch` function
    recv_x, recv_topk_idx, recv_topk_weights, num_recv_tokens_per_expert_list, handle, event =\
        _buffer.dispatch(x, topk_idx=topk_idx, topk_weights=topk_weights,
                         num_tokens_per_rank=num_tokens_per_rank, num_tokens_per_rdma_rank=num_tokens_per_rdma_rank,
                         is_token_in_rank=is_token_in_rank, num_tokens_per_expert=num_tokens_per_expert,
                         previous_event=previous_event, async_finish=True,
                         allocate_on_comm_stream=True)
    # For event management, please refer to the docs of the `EventOverlap` class
    return recv_x, recv_topk_idx, recv_topk_weights, num_recv_tokens_per_expert_list, handle, event


def dispatch_backward(grad_recv_x: torch.Tensor, grad_recv_topk_weights: torch.Tensor, handle: Tuple) ->\
        Tuple[torch.Tensor, torch.Tensor, EventOverlap]:
    global _buffer

    # The backward process of MoE dispatch is actually a combine
    # For more advanced usages, please refer to the docs of the `combine` function
    combined_grad_x, combined_grad_recv_topk_weights, event =\
        _buffer.combine(grad_recv_x, handle, topk_weights=grad_recv_topk_weights, async_finish=True)

    # For event management, please refer to the docs of the `EventOverlap` class
    return combined_grad_x, combined_grad_recv_topk_weights, event


def combine_forward(x: torch.Tensor, handle: Tuple, previous_event: Optional[EventOverlap] = None) ->\
        Tuple[torch.Tensor, EventOverlap]:
    global _buffer

    # Do MoE combine
    # For more advanced usages, please refer to the docs of the `combine` function
    combined_x, _, event = _buffer.combine(x, handle, async_finish=True, previous_event=previous_event,
                                           allocate_on_comm_stream=previous_event is not None)

    # For event management, please refer to the docs of the `EventOverlap` class
    return combined_x, event


def combine_backward(grad_combined_x: Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]],
                     handle: Tuple, previous_event: Optional[EventOverlap] = None) ->\
        Tuple[Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]], EventOverlap]:
    global _buffer

    # The backward process of MoE combine is actually a dispatch
    # For more advanced usages, please refer to the docs of the `dispatch` function
    grad_x, _, _, _, _, event = _buffer.dispatch(grad_combined_x, handle=handle, async_finish=True,
                                                 previous_event=previous_event,
                                                 allocate_on_comm_stream=previous_event is not None)

    # For event management, please refer to the docs of the `EventOverlap` class
    return grad_x, event
```

##### 5.2.3. Benchmark 测试介绍

DeepEP 自带的 Benchmark 测试脚本使用方法：

```bash
# 设置分布式训练环境变量，以两机 internode 场景为例
MASTER_ADDR="$master" MASTER_PORT=12345 WORLD_SIZE=2 RANK=0 python tests/test_internode.py --num-pernode 8 --num-experts 256 --num-topk 8 --hidden-size 7168 --num-tokens 4096
MASTER_ADDR="$master" MASTER_PORT=12345 WORLD_SIZE=2 RANK=1 python tests/test_internode.py --num-pernode 8 --num-experts 256 --num-topk 8 --hidden-size 7168 --num-tokens 4096

# 也使用 pytorch 自带的 torchrun 运行多机测试，以两机 internode 场景为例
torchrun --master_addr $master --master_port 45678 --nnodes 2 --node_rank 0 --nproc_per_node 1 ./tests/test_internode.py --num-pernode 8 --num-experts 256 --num-topk 8 --hidden-size 7168 --num-tokens 4096
torchrun --master_addr $master --master_port 45678 --nnodes 2 --node_rank 1 --nproc_per_node 1 ./tests/test_internode.py --num-pernode 8 --num-experts 256 --num-topk 8 --hidden-size 7168 --num-tokens 4096

-n , --num-pernode    configure ppu num per node; default is 16.
-e , --num-experts    configure number of experts; default is 256.
-k , --num-topk       configure number of topk; default is 8.
--hidden-size         configure hidden size
-t , --num-tokens     configure dispatch or combine token number

#更多参数以及说明，可以使用 python tests/test_internode.py --help 来查询
```

#### 5.3. Low Latency 功能

Low Latency 主要是用于模型推理的 Decoding 场景，适用场景比较灵活，包括单机内 PPU 通过 ICN Link 或者 RDMA 互联，或者是机器之间通过 RDMA 网卡互联通信的集群架构。

##### 5.3.1. 初始化

```python
import torch
import torch.distributed as dist
from typing import Tuple, Optional

from deep_ep import Buffer

# Communication buffer (will allocate at runtime)
# NOTES: there is no SM control API for the low-latency kernels
_buffer: Optional[Buffer] = None


# You may call this function at the framework initialization
def get_buffer(group: dist.ProcessGroup, num_max_dispatch_tokens_per_rank: int, hidden: int, num_experts: int) -> Buffer:
    # NOTES: the low-latency mode will consume much more space than the normal mode
    # So we recommend that `num_max_dispatch_tokens_per_rank` (the actual batch size in the decoding engine) should be less than 256
    global _buffer
    num_rdma_bytes = Buffer.get_low_latency_rdma_size_hint(num_max_dispatch_tokens_per_rank, hidden, group.size(), num_experts)

    # Allocate a buffer if not existed or not enough buffer size
    if _buffer is None or _buffer.group != group or not _buffer.low_latency_mode or _buffer.num_rdma_bytes < num_rdma_bytes:
        # NOTES: for the best performance, the QP number **must** be equal to the number of the local experts
        assert num_experts % group.size() == 0
        _buffer = Buffer(group, 0, num_rdma_bytes, low_latency_mode=True, num_qps_per_rank=num_experts // group.size())
    return _buffer
```

##### 5.3.2. Dispatch 和 Combine 接口调用

进行实际场景下的 dispatch 和 combine 通信操作。

```python
def low_latency_dispatch(hidden_states: torch.Tensor, topk_idx: torch.Tensor, num_max_dispatch_tokens_per_rank: int, num_experts: int):
    global _buffer

    # Do MoE dispatch, compatible with HGGC graph (but you may restore some buffer status once you replay)
    recv_hidden_states, recv_expert_count, handle, event, hook =\
        _buffer.low_latency_dispatch(hidden_states, topk_idx, num_max_dispatch_tokens_per_rank, num_experts,
                                     async_finish=False, return_recv_hook=True)

    # NOTES: the actual tensor will not be received only if you call `hook()`,
    # it is useful for double-batch overlapping, but **without any SM occupation**
    # If you don't want to overlap, please set `return_recv_hook=False`
    # Later, you can use our GEMM library to do the computation with this specific format
    return recv_hidden_states, recv_expert_count, handle, event, hook


def low_latency_combine(hidden_states: torch.Tensor,
                        topk_idx: torch.Tensor, topk_weights: torch.Tensor, handle: Tuple):
    global _buffer

    # Do MoE combine, compatible with HGGC graph (but you may restore some buffer status once you replay)
    combined_hidden_states, event_overlap, hook =\
        _buffer.low_latency_combine(hidden_states, topk_idx, topk_weights, handle,
                                    async_finish=False, return_recv_hook=True)

    # NOTES: the same behavior as described in the dispatch kernel
    return combined_hidden_states, event_overlap, hook
```

##### 5.3.3. Benchmark 测试介绍

DeepEP 自带的 Benchmark 测试脚本使用方法：

```bash
# 设置分布式训练环境变量，以两机场景为例
MASTER_ADDR="$master" MASTER_PORT=12345 WORLD_SIZE=2 RANK=0 python ./tests/test_low_latency.py --num-pernode 8 --num-experts 256 --num-topk 8 --hidden-size 7168 --num-tokens 128
MASTER_ADDR="$master" MASTER_PORT=12345 WORLD_SIZE=2 RANK=1 python ./tests/test_low_latency.py --num-pernode 8 --num-experts 256 --num-topk 8 --hidden-size 7168 --num-tokens 128

# 也使用 pytorch 自带的 torchrun 运行多机测试，以两机场景为例
torchrun --master_addr $master --master_port 45678 --nnodes 2 --node_rank 0 --nproc_per_node 1 ./tests/test_low_latency.py --num-pernode 8 --num-experts 256 --num-topk 8 --hidden-size 7168 --num-tokens 128
torchrun --master_addr $master --master_port 45678 --nnodes 2 --node_rank 1 --nproc_per_node 1 ./tests/test_low_latency.py --num-pernode 8 --num-experts 256 --num-topk 8 --hidden-size 7168 --num-tokens 128

-n , --num-pernode    configure ppu num per node; default is 16.
-e , --num-experts    configure number of experts; default is 256.
-k , --num-topk       configure number of topk; default is 8.
--hidden-size         configure hidden size
-t , --num-tokens     configure dispatch or combine token number
--ll-with-icn {0,1}   enable ICN Link for low latency kernel
--allow-mnnvl         Allow Multi-Node ICN Link for communication
--use-fabric          Enable fabric mode
--use-fp8             use fp8 data type to dispatch; default is false.
--use-int8            use int8 quant data type to dispatch; default is false.
--use-mxfp4           use mxfp4 quant data type to dispatch; default is false.

#更多参数以及说明，可以使用 python ./tests/test_low_latency.py --help 来查询
```

平台扩展关联：这些 benchmark 参数面向多卡 EP 部署，不属于本次单卡、单样本、无 batch 的比赛路径。

## 第二章 sailbandwidth 使用指南

### 1. 概述

sailbandwidth 是一个用于测试和评估 PPU 设备间带宽性能的诊断工具。该工具针对真武 810、真武 810E 等平头哥自研 PPU 机型的硬件特性进行了深度优化，支持多种带宽测试场景，可帮助用户全面了解系统的带宽性能。

sailbandwidth 支持以下主要测试场景：

- **H2D（Host to Device）**：测试从 CPU 内存到 PPU 设备内存的数据传输带宽。
- **D2H（Device to Host）**：测试从 PPU 设备内存到 CPU 内存的数据传输带宽。
- **D2D（Device to Device）**：测试不同 PPU 设备之间的数据传输带宽。
- **H2ALL（Host to All）**：测试从 CPU 到所有 PPU 设备的并行传输带宽。
- **ALL2H（All to Host）**：测试从所有 PPU 设备到 CPU 的并行传输带宽。
- **ALL2D（All to Device）**：测试从所有 PPU 设备向单个设备的并行传输带宽。
- **D2ALL（Device to All）**：测试从单个 PPU 设备向所有设备的并行传输带宽。

下面各章节将详细介绍工具的参数配置及常见测试用例的使用方法。文中所附的性能数据仅供参考，实际性能数据需根据具体的机器环境、带宽配置及 T-Head SAIL SDK 版本而定。

### 2. 参数介绍

可以使用 `./sailbandwidth -h` 查询全部参数信息。

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `-h`, `--help` | - | 显示帮助信息 |
| `-b`, `--bufferSize` | 512 | 内存拷贝缓冲区大小（单位：MiB） |
| `-l`, `--list` | - | 列出所有可用的测试用例 |
| `-t`, `--testcase` | - | 指定要运行的测试用例（按名称或索引） |
| `-p`, `--testcasePrefixes` | - | 指定要运行的测试用例前缀 |
| `-v`, `--verbose` | False | 详细输出模式 |
| `-s`, `--skipVerification` | False | 是否跳过数据传输后的数据校验 |
| `-d`, `--disableAffinity` | False | 是否禁用自动 CPU 亲和性控制 |
| `-i`, `--testSamples` | 3 | 基准测试迭代次数 |
| `-m`, `--useMean` | False | 是否使用平均值而非中位数计算结果 |
| `-j`, `--json` | False | 是否以 JSON 格式输出结果 |
| `--useNormalCopy` | False | SM 测试中是否使用普通传输模式 |
| `--nBlocks` | -1 | 指定 SM 测试的 block 数量（-1 表示自动） |
| `--nThreads` | -1 | 指定 SM 测试的线程数量（-1 表示自动） |
| `--isSingleDie` | False | CE 测试中是否使用单 die 模式 |
| `--testLocalCopy` | False | 在 D2D 测试中是否开启 Local 测试 |
| `--displayUR` | False | 在 D2D 测试中是否显示带宽利用率矩阵 |
| `--disableVm` | False | 是否禁用虚拟内存模式 |

### 3. 示例

#### 3.1. Copy Engine (CE) Copy

Copy Engine (CE) Copy 也称为 DMA Copy，是通过 PPU 硬件 DMA 引擎执行的数据传输操作。CE Copy 不占用 SM 计算资源，适合在后台进行大规模数据搬运，是最高效的数据传输方式。

当前支持的 CE Copy 测试类型：

| 测试类型 | 说明 |
|---------|------|
| `host_to_device_memcpy_ce` | CPU 到 PPU 单向传输 |
| `device_to_host_memcpy_ce` | PPU 到 CPU 单向传输 |
| `host_to_device_bidirectional_memcpy_ce` | CPU 与 PPU 双向传输 |
| `device_to_host_bidirectional_memcpy_ce` | PPU 与 CPU 双向传输 |
| `device_to_device_memcpy_read_ce` | PPU 间 Read 单向传输 |
| `device_to_device_memcpy_write_ce` | PPU 间 Write 单向传输 |
| `device_to_device_bidirectional_memcpy_read_ce` | PPU 间 Read 双向传输 |
| `device_to_device_bidirectional_memcpy_write_ce` | PPU 间 Write 双向传输 |
| `all_to_host_memcpy_ce` | 所有 PPU 到 CPU 并行传输 |
| `all_to_host_bidirectional_memcpy_ce` | 所有 PPU 与 CPU 双向并行传输 |
| `host_to_all_memcpy_ce` | CPU 到所有 PPU 并行传输 |
| `host_to_all_bidirectional_memcpy_ce` | CPU 与所有 PPU 双向并行传输 |
| `all_to_one_write_ce` | 所有 PPU 向单个 PPU 写入 |
| `all_to_one_read_ce` | 单个 PPU 从所有 PPU 读取 |
| `one_to_all_write_ce` | 单个 PPU 向所有 PPU 写入 |
| `one_to_all_read_ce` | 单个 PPU 从所有 PPU 读取 |

##### 3.1.1. D2D 单向 Read 带宽测试

```bash
./sailbandwidth -t device_to_device_memcpy_read_ce
```

```text
Running device_to_device_memcpy_read_ce.
memcpy CE PPU(row) -> PPU(column) bandwidth (GB/s)
         0        1         2         3         4         5         6         7
0       N/A     48.87     47.22     47.69     48.43     45.11     45.07     48.22
1     45.19       N/A     48.92     46.46     45.00     45.28     47.31     47.39
2     48.88     45.62       N/A     45.38     48.48     47.57     48.86     46.14
3     46.03     44.84     46.26       N/A     45.27     48.70     46.56     45.29
4     45.36     45.93     44.87     48.00       N/A     46.31     44.95     44.84
5     48.88     47.64     45.81     48.76     48.21       N/A     45.84     44.99
6     46.01     48.87     47.93     48.47     45.44     45.17       N/A     45.59
7     45.57     46.83     48.56     47.71     47.64     47.62     48.88       N/A
SUM device_to_device_memcpy_read_ce 2620.72
```

##### 3.1.2. D2D 单向 Write 带宽测试

```bash
./sailbandwidth -t device_to_device_memcpy_write_ce
```

```text
Running device_to_device_memcpy_write_ce.
memcpy CE PPU(row) <- PPU(column) bandwidth (GB/s)
         0        1         2         3         4         5         6         7
0       N/A     46.11     46.97     48.07     96.90     97.65     48.60     95.29
1     46.44       N/A     46.67     46.85     94.09     94.44     94.85     47.58
2     45.82     46.94       N/A     48.38     48.90     95.74     94.97     93.26
3     46.10     48.78     45.99       N/A     90.39     46.81     97.31     95.06
4     93.30     90.51     46.70     97.19       N/A     45.79     46.20     48.26
5     91.44     90.75     90.36     44.99     45.77       N/A     46.84     48.17
6     46.54     94.74     95.56     96.83     48.88     47.58       N/A     46.38
7     90.39     44.84     90.40     90.32     44.92     44.99     45.06       N/A

SUM device_to_device_memcpy_write_ce 3748.65
```

#### 3.2. Streaming Multiprocessor (SM) Copy

Streaming Multiprocessor (SM) Copy 也称为 Kernel Copy，是通过在 PPU SM 上执行计算核函数来实现的数据传输操作。SM Copy 利用 SM 的计算能力进行数据搬运，适用于需要在传输过程中进行数据处理的场景，同时也可用于测试延迟性能。

当前支持的 SM Copy 测试类型：

| 测试类型 | 说明 |
|---------|------|
| `host_device_latency_sm` | CPU 与 PPU 间延迟测试 |
| `device_to_device_latency_sm` | PPU 间延迟测试 |
| `host_to_device_memcpy_sm` | CPU 到 PPU 单向传输 |
| `device_to_host_memcpy_sm` | PPU 到 CPU 单向传输 |
| `host_to_device_bidirectional_memcpy_sm` | CPU 与 PPU 双向传输 |
| `device_to_host_bidirectional_memcpy_sm` | PPU 与 CPU 双向传输 |
| `device_to_device_memcpy_read_sm` | PPU 间 Read 单向传输 |
| `device_to_device_memcpy_write_sm` | PPU 间 Write 单向传输 |
| `device_to_device_bidirectional_memcpy_read_sm` | PPU 间 Read 双向传输 |
| `device_to_device_bidirectional_memcpy_write_sm` | PPU 间 Write 双向传输 |
| `all_to_host_memcpy_sm` | 所有 PPU 到 CPU 并行传输 |
| `all_to_host_bidirectional_memcpy_sm` | 所有 PPU 与 CPU 双向并行传输 |
| `host_to_all_memcpy_sm` | CPU 到所有 PPU 并行传输 |
| `host_to_all_bidirectional_memcpy_sm` | CPU 与所有 PPU 双向并行传输 |
| `all_to_one_write_sm` | 所有 PPU 向单个 PPU 写入 |
| `all_to_one_read_sm` | 单个 PPU 从所有 PPU 读取 |
| `one_to_all_write_sm` | 单个 PPU 向所有 PPU 写入 |
| `one_to_all_read_sm` | 单个 PPU 从所有 PPU 读取 |

##### 3.2.1. D2D 单向 Read 带宽测试

```bash
./sailbandwidth -t device_to_device_memcpy_read_sm
```

```text
Running device_to_device_memcpy_read_sm.
memcpy SM PPU(row) -> PPU(column) bandwidth (GB/s)
         0        1         2         3         4         5         6         7
0       N/A     48.17     48.17     48.17     96.31     96.31     48.17     96.31
1     48.17       N/A     48.17     48.17     96.31     96.31     96.31     48.17
2     48.17     48.17       N/A     48.17     48.17     96.31     96.31     96.31
3     48.17     48.17     48.17       N/A     96.31     48.17     96.31     96.31
4     96.31     96.31     48.17     96.31       N/A     48.17     48.17     48.17
5     96.31     96.31     96.31     48.17     48.17       N/A     48.17     48.17
6     48.17     96.31     96.31     96.31     48.17     48.17       N/A     48.17
7     96.31     48.17     96.31     96.31     48.17     48.17     48.17       N/A

SUM device_to_device_memcpy_read_sm 3852.87
```

##### 3.2.2. D2D 单向 Write 带宽测试

```bash
./sailbandwidth -t device_to_device_memcpy_write_sm
```

```text
Running device_to_device_memcpy_write_sm.
memcpy SM PPU(row) <- PPU(column) bandwidth (GB/s)
         0        1         2         3         4         5         6         7
0       N/A     46.80     46.80     46.80     93.25     93.23     46.80     93.25
1     46.80       N/A     46.80     46.80     93.24     93.25     93.25     46.80
2     46.80     46.80       N/A     46.80     46.80     93.25     93.24     93.25
3     46.80     46.80     46.80       N/A     93.25     46.80     93.23     93.24
4     93.24     93.26     46.80     93.24       N/A     46.80     46.80     46.80
5     93.24     93.25     93.24     46.80     46.80       N/A     46.80     46.80
6     46.80     93.25     93.25     93.23     46.80     46.80       N/A     46.80
7     93.25     46.80     93.25     93.25     46.80     46.80     46.80       N/A

SUM device_to_device_memcpy_write_sm 3735.50
```

比赛关联：sailbandwidth 是部署前的硬件体检工具——用 H2D/D2H/D2D 测试确认 PPU 机器各链路带宽达标（CE vs SM、Read vs Write 差异明显，D2D 约 45-48 GB/s 或 90-96 GB/s 两档，反映拓扑分组），`-j` JSON 输出可直接作为压测取证数据；权重加载（H2D）路径的带宽直接影响模型冷启动时间。
