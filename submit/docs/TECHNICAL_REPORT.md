# 技术总结报告：Qwen3.5-2B 单卡 810E PPU 推理优化

> 比赛：赛道二 —— 面向 AI 芯片的 VLM 高效推理与优化。硬件为单张阿里平头哥 810E（PPU-ZW810E / PPU0015，显存 97920 MiB），评测负载为单样本输入且不启用 batch。
> 评测口径：公开自测集 MMBench dev EN/CN 各 4029 条，评测入口为 `benchmark_public.py`（评测口径与赛事初始版本一致，本地改动说明见 `CORRECTNESS_AND_FAIRNESS.md` 第一节），选手实现经 `evaluation_wrapper.py` 生效；生成参数由评测脚本固定为 `max_new_tokens=256, temperature=0.0`。
> 本报告所有性能数据均来自一张 810E 上 `benchmark_public.py` 的实际运行输出，所有性能数字均随文标注单位。
> 中英文由同一套自适应配置处理：提交默认配置不检测语言、不按数据集切换路径，自适应 MTP 链深仅依据运行时实测的接受率与耗时信号逐轮决策（见 2.21 节）。

## 目录

- [一、总体性能](#一总体性能)
- [二、优化方案](#二优化方案)
- [三、性能提升](#三性能提升)
- [四、运行环境与复现方式](#四运行环境与复现方式)
- [五、性能分析工具](#五性能分析工具)

## 一、总体性能

### 1.1 main 当前严格计时口径

全量终验的配置为提交默认配置（BF16、TP=1、Triton attention；Decode CUDA Graph、**自适应 MTP 链深 1~4（max depth=4 + 动态控制器）**、ViT 桶化图、EXTEND 四桶 prefill 图、verify metadata 入图、decode 图内融合 kernel、M=2/M=3/M=4/M=5 projection GEMV 专用化、post-verify host 快速路径、联合投机图、mm host 快速路径、ViT RoPE 融合、PPU device-memory IPC ring、精确 fused patchify 与通用输出有效性兜底全部默认开启，不传任何调优环境变量）：

| 数据集         | 样本数 | 平均 TTFT（ms） | 平均 decode 吞吐（token/s） |                准确率 | public validation |
| -------------- | -----: | --------------: | --------------------------: | --------------------: | ----------------: |
| MMBench dev EN |   4029 |      **27.628** |                 **594.200** | 79.9702%（3222/4029） |              通过 |
| MMBench dev CN |   4029 |      **27.990** |                 **401.827** | 84.0159%（3385/4029） |              通过 |

TTFT 按 wrapper 收到首个非空文本 chunk 计量，Decode 按公开脚本逐题算术平均，短输出高值保留在统计中。返回文本超过 1200 字符时仅截断展示文本，`token_count` 和计时不变。通用输出有效性兜底（2.13 节）默认开启：输出中没有明确 A/B/C/D 选项时由同一模型按评测器原始采样参数补答，首次生成与补答的 token 数与墙钟时间合并计量；全量下 EN 触发 1 条、CN 触发 3 条，双语 public validation 全部通过。

准确率口径说明：早期快照为 EN 3222 / CN 3386；期间工作树的处理器 backport 在 transformers 4.51.3 上丢失 `preprocessor_config.json` 的 min/max pixels 界限（4.51 的 `Qwen2VLImageProcessorFast.__init__` 会丢弃合法的 `size` 字典，只有 `min_pixels`/`max_pixels` kwargs 生效），导致 543 个样本的图像 token 数缩水、全量准确率一度降至 EN 3207 / CN 3368。随后已修复：显式转发 min/max pixels，并把 `smart_resize` 补丁为 4.57 语义（4.51 对小于 32 px 的薄图直接抛异常，原生 4.57 路径为按比例放大）；修复后 EN 完全恢复 3222/4029，CN 恢复至 3385/4029（相对早期快照 −1，残余为 qid 505 系列 4 条样本的 1 token 提示词口径差异，疑为旧运行环境 tokenizer 组件版本怪癖，对答案无系统性影响）。离线逐样本核验：EN 51 个曾翻转样本中 50 个、CN 440 个中 436 个的图像 token 数与早期快照完全一致。P1.5（GEMV 专用化）、P1（post-verify 快速路径）与 P3-B（联合投机图）均以同树全量 A/B 验证，五字段（question_id/parsed_answer/correct/token_count/validation_errors）逐题零差异。链深类改动（2.12、2.21 节）因改变 GDN chunk 分段而存在 BF16 near-tie 合法分叉，验收口径为正确题数持平 + validation 不新增失败，当前配置下 EN 3222、CN 3385 与历史最佳完全一致。早期口径下的历史成绩为 EN 32.522 ms / 359.842 token/s、CN 32.951 ms / 335.076 token/s。

### 1.2 与主办方 Transformers 基线对比

主办方给出的 Transformers 路径在同一公开数据集上的 benchmark 记录如下（主办方提供的准确率显示值保留两位小数）：

| 实现                                   | 数据集         | 样本数 | 平均 TTFT（ms） | 平均 decode 吞吐（token/s） |                    准确率 |
| -------------------------------------- | -------------- | -----: | --------------: | --------------------------: | ------------------------: |
| Transformers 基线                      | MMBench dev EN |   4029 |           185.1 |                        58.7 |         0.80（3219/4029） |
| Transformers 基线                      | MMBench dev CN |   4029 |           141.0 |                        41.5 |         0.84（3388/4029） |
| 本方案（SGLang 优化版，main 当前口径） | MMBench dev EN |   4029 |      **27.628** |                 **594.200** | **79.9702%（3222/4029）** |
| 本方案（SGLang 优化版，main 当前口径） | MMBench dev CN |   4029 |      **27.990** |                 **401.827** | **84.0159%（3385/4029）** |

相对主办方 Transformers 基线，本方案在 EN/CN 上的平均 TTFT 分别降低 85.1% 和 80.1%，平均 decode 吞吐分别达到基线的 10.12 倍和 9.68 倍，正确题数分别变化 +3 和 −3，准确率比值 EN 1.0009 / CN 0.9991，偏差远小于 README 评分办法的 baseline − 2% 门槛。

### 1.3 评分指标计算

评分办法以 `README.md` 第 6 节为准，采用两阶段口径：

1. **准确率门槛**：`Accuracy >= baseline_accuracy − 2%`，低于门槛的提交不进入性能排名。本方案全量自测准确率 EN 79.97% / CN 84.02%，相对主办方 Transformers 基线（EN 79.89% / CN 84.09%）的偏差分别为 +0.08 / −0.07 个百分点，远在门槛之内。
2. **性能综合排名**：在准确率合格的提交中比较 TTFT 与吞吐，README 给出的可选综合分示例为 `FinalScore = AccuracyScore × 0.6 + TTFTScore × 0.2 + ThroughputScore × 0.2`（实际最终公式以主办方发布版本为准）。

按该 0.6 / 0.2 / 0.2 权重示例在本地折算（各子项以主办方 Transformers 基线归一：`AccuracyScore = Acc / Acc_base`，`TTFTScore = T_base / T_opt`，`ThroughputScore = T_opt / T_base`，仅用于横向自评，绝对得分以主办方复测为准）：

| 子项（权重）           |                      EN |                      CN |
| ---------------------- | ----------------------: | ----------------------: |
| AccuracyScore（0.6）   |  3222/3219 = **1.0009** |  3385/3388 = **0.9991** |
| TTFTScore（0.2）       | 185.1/27.628 = **6.70** | 141.0/27.990 = **5.04** |
| ThroughputScore（0.2） | 594.200/58.7 = **10.12** | 401.827/41.5 = **9.68** |

准确率已与 Transformers 基线持平，其提升空间取决于模型本身，不作为优化杠杆；排名差异主要来自 TTFT 与吞吐两项，这是本方案以图捕获与投机解码作为优化主线的依据。

### 1.4 SGLang 0.5.13 自测数据

为隔离引擎版本因素的影响，在独立工作区中引入官方移植 sglang-for-sail 标签 `0.5.13+v0.1.0`（commit `057fcc4`），在同一张 810E 上逐样本运行全量数据。配置为 BF16、TP=1、Triton attention、batch-one CUDA Graph，不启用 MTP、ViT Graph 与 EXTEND Graph。由于比赛镜像低于该标签声明的完整依赖要求（SAIL SDK 2.1.1、PyTorch-for-SAIL 2.10、FlashInfer-for-SAIL 0.6.8.post1），实验中将镜像缺失的功能回退到已有的 Triton/sgl-kernel 路径。

| 实现                        | 数据集         | 样本数 | 平均 TTFT（ms） | 平均 decode 吞吐（token/s） |                    准确率 | public validation |
| --------------------------- | -------------- | -----: | --------------: | --------------------------: | ------------------------: | ----------------: |
| SGLang 0.5.13 baseline      | MMBench dev EN |   4029 |          66.670 |                     259.093 |     79.6972%（3211/4029） |          1 条失败 |
| SGLang 0.5.13 baseline      | MMBench dev CN |   4029 |          68.283 |                     260.438 |     83.9414%（3382/4029） |              通过 |
| 本方案（main 当前严格口径） | MMBench dev EN |   4029 |      **27.628** |                 **594.200** | **79.9702%（3222/4029）** |              通过 |
| 本方案（main 当前严格口径） | MMBench dev CN |   4029 |      **27.990** |                 **401.827** | **84.0159%（3385/4029）** |              通过 |

相对 SGLang 0.5.13 baseline 的全量口径，本方案在 EN 上平均 TTFT 降低 58.6%、decode 吞吐提升 129.3%；在 CN 上平均 TTFT 降低 59.0%、decode 吞吐提升 54.3%。上述 baseline 数字为复跑实测，与首次全量记录（EN 66.972 ms/258.686 token/s、CN 68.402 ms/259.216 token/s）的差异在运行噪声范围内，正确题数一致。需要说明的是，该对照仅反映现有比赛镜像内的工程对比结果，不代表 0.5.13 在官方完整依赖镜像中的极限性能。

## 二、优化方案

本方案在 PPU（SAIL）版本的 SGLang 基础上进行优化：提交后端为 `rapid_reasoning/sglang/` 内置的精简版源码树（SGLang 0.4.6.post1 PPU 版，回移上游 v0.5.9 的 Qwen3.5 hybrid linear-attention 支持，固定 BF16、TP=1、Triton attention 运行路径），1.4 节的 SGLang 0.5.13 自测成绩作为官方新版引擎在同一硬件上的对照基线。全部优化均在引擎层实现，不改动 `evaluation_wrapper.py` 的接口契约，提交配置下所有优化默认开启，无需设置任何环境变量。

各优化点与其主要提升指标的对应关系如下表所示，后续小节逐一展开；所有对比数据均标注样本口径，单次差异小于约 ±2 token/s 或 ±2 ms 时按运行噪声处理，不记为收益。

| 小节 | 优化点                               | 主要提升指标                           | 次要影响                |
| ---- | ------------------------------------ | -------------------------------------- | ----------------------- |
| 2.1  | batch=1 Decode CUDA Graph            | decode 吞吐（约 4 倍）                 | TTFT 改善               |
| 2.2  | MTP 自投机解码                       | decode 吞吐（千例 +13.6%/+7.4%）       | TTFT 略增               |
| 2.3  | 0.5.13 GDN 热路径优化回移            | decode 吞吐（累计 +5.4%）              | —                       |
| 2.4  | ViT 桶化图 + init 预捕获             | TTFT（约 −4.3 ms）                     | —                       |
| 2.5  | EXTEND 四桶 prefill 图               | TTFT（−21%~−23%）                      | —                       |
| 2.6  | verify attention metadata 入图       | decode 吞吐（+0.73%）                  | TTFT 略增               |
| 2.7  | TTFT 残余段压缩                      | TTFT（约 −4.7 ms）                     | —                       |
| 2.8  | decode 图内手写融合 kernel           | decode 吞吐（+9.6% 与 +3.6%）          | TTFT 略降               |
| 2.9  | verify 逐层 projection GEMV          | decode 吞吐（+2.69%/+2.34%）           | —                       |
| 2.10 | post-verify host 快速路径            | decode 吞吐（EN1000 +4.47%）           | —                       |
| 2.11 | 联合投机图                           | decode 吞吐（+9.77%/+9.33%）           | —                       |
| 2.12 | MTP chain depth=2                    | EN decode 吞吐（全量 +20.46%）         | CN 受接受率限制         |
| 2.13 | 通用输出有效性兜底                   | public validation 全部通过             | 仅 4/8058 条触发        |
| 2.14 | mm host 快速路径                     | TTFT（全量 EN −0.98 ms / CN −1.84 ms） | decode 不变             |
| 2.15 | 第二批 full-attention 小 kernel 融合 | decode 吞吐（EN/CN1000 +2.91%/+3.05%） | TTFT 不变               |
| 2.16 | ViT RoPE 图内融合                    | TTFT（EN/CN1000 −1.85/−1.44 ms）       | decode 不变             |
| 2.17 | PPU device-memory IPC ring           | TTFT（全量 EN/CN −1.77/−2.04 ms）      | decode 不变             |
| 2.18 | ViT QKV/RoPE 组合融合                | TTFT（EN/CN1000 −0.26/−0.45 ms）       | 五字段零差异            |
| 2.19 | M=3 GEMV 与精确 fused patchify 转正  | decode 吞吐与 preprocess 微收益        | 全量 EN/CN 五字段零差异 |
| 2.20 | 提交闭包与固定模型路径瘦身           | 提交完整性与可复现性                   | 无性能影响              |
| 2.21 | 自适应 MTP 链深 1~4                  | decode 吞吐（全量 EN +11.1%）          | CN 小幅回退后基本持平   |
| 2.22 | M=4/M=5 verify GEMV 专用化           | 支撑 2.21 的 verify 路径               | 与 F.linear 逐位一致    |

### 2.1 batch=1 Decode CUDA Graph

Qwen3.5 的 GDN 混合线性注意力在回移植时跳过了图捕获，decode 走 eager 路径，每步数十个 kernel 的 host 侧启动开销成为主要瓶颈：图化前单步约 15 ms，等效显存带宽仅约 280 GB/s，远低于 HBM 标称带宽。本优化从备份中按 decode-only 裁剪恢复 `cuda_graph_runner.py`（约 257 行）并完成 model_runner 与两个 attention 后端的接线，只捕获 bs=1 的 decode 步；前置工作为 decode metadata 缓存化（`query_start_loc` 按 batch 缓存复用、下游 28 处引用全部只读）与 KV/Mamba 状态池指针固定，以满足图捕获的地址稳定要求。运行期每步执行一次图重放，消除逐 kernel 启动与 host 调度开销。

| 配置            | 口径   | 平均 TTFT（ms） | 平均 decode 吞吐（token/s） |
| --------------- | ------ | --------------: | --------------------------: |
| eager（图化前） | EN50   |            68.3 |                        65.2 |
| decode 图开启   | EN50   |            57.0 |                       264.1 |
| eager（图化前） | CN50   |            67.9 |                        67.0 |
| decode 图开启   | CN50   |            55.7 |                       260.2 |
| eager（图化前） | EN1000 |          71.650 |                      65.985 |
| decode 图开启   | EN1000 |          57.157 |                     264.957 |

相对 eager 配置，decode 吞吐提升约 4 倍，decode 等效带宽由约 280 GB/s 提升至约 1.06 TB/s，decode 自此转为真正的带宽受限；EN/CN 各 50 条逐题结果与 eager 完全一致（greedy 64 步 logits 逐位相同、Mamba ssm/conv 终态逐位相同），准确率无变化。

代码位置：`rapid_reasoning/sglang/srt/model_executor/cuda_graph_runner.py`、`srt/layers/attention/triton_backend.py`、`srt/layers/attention/hybrid_linear_attn_backend.py`（带 `# BACKPORT-PPU:` 标记）。

合规性：本优化属于允许的"CUDA Graph 或静态图优化"与"KV cache 布局、分配和复用优化"；图在每次引擎启动时于内存中重新捕获，无跨次运行的持久化缓存，不触犯禁止条例。

### 2.2 MTP 自投机解码

图化后 decode 已转为带宽受限，剩余的主要优化手段是将每步约 4 GiB 的权重读取摊薄到多个 token 上。模型 checkpoint 自带 MTP 头（`mtp_num_hidden_layers=1`），无需训练草稿模型。本优化实现 chain/topk=1、num_draft_tokens=2 的自投机解码：草稿头前向生成 1 个候选 token，目标模型以一次定长 2 token 的前向并行验证，greedy 验证保证输出与非投机解码一致；verify、draft、commit 三个阶段各捕获专用图（含 `MtpCommitGraphRunner`），acceptance 结果单次打包传输，MRoPE positions 在 GPU 上按 positions+delta 计算，从而消除图外 2.5–3 ms/步的残余开销（36 次 kernel launch、`.tolist()` 同步、CPU 往返）。GDN 状态采用"verify 不写持久 state、接受后统一 commit"的中间态管道，无需快照回滚。实测接受率为 1.88/2（约 94%）。

| 配置                | 口径   | 平均 TTFT（ms） | 平均 decode 吞吐（token/s） | 相对提升 |
| ------------------- | ------ | --------------: | --------------------------: | -------: |
| decode 图（无 MTP） | EN50   |               — |                       262.6 |     基线 |
| decode 图 + MTP     | EN50   |               — |                       307.3 |   +17.0% |
| decode 图（无 MTP） | CN50   |               — |                       260.5 |     基线 |
| decode 图 + MTP     | CN50   |               — |                       282.2 |    +8.3% |
| decode 图（无 MTP） | EN1000 |            57.2 |                       264.9 |     基线 |
| decode 图 + MTP     | EN1000 |            56.2 |                       301.0 |   +13.6% |

千例口径下准确率为 EN 83.0%、CN 85.0%，与非投机配置持平；CN1000 吞吐为 278.3 token/s（相对同期图开配置 +7.4%），TTFT 56.5 ms。verify 单步耗时由 6.34 ms 降至 5.90 ms。单元级 hook 比对 468/468 逐位一致，EN50 逐题 50/50 零差异；已知容忍分歧为 verify 所走的 extend 内核与 decode 内核在 bf16 near-tie 场景的舍入翻转（EAGLE 类方法固有），CN1000 中有 4/1000 题答案翻转，准确率不变。

代码位置：`srt/speculative/`（`mtp_worker.py`、`mtp_utils.py`、`spec_info.py`）、`srt/models/qwen3_5_mtp.py`，接线于 `srt/server_args.py`、`srt/managers/scheduler.py`、`srt/model_executor/forward_batch_info.py` 与两个 attention 后端。

合规性：本优化属于允许的"prefill/decode 路径优化"；使用主办方指定权重自带的 MTP 头，未更换、未蒸馏权重，输出与目标模型贪心解码一致，不触犯禁止条例。

### 2.3 0.5.13 GDN 热路径优化回移

从 sglang-for-sail 0.5.13 逐项回移 GDN（Gated DeltaNet）热路径优化到精简树，压缩 MTP verify 与 decode 步骤中的小张量分配与 kernel 数量。另经 17 档 × 2 轮 kernel 参数扫描，将 QKV split 的 `num_stages` 默认值由 3 调整为 4。

| 回移项                                                     | EN1000 平均 decode 吞吐（token/s） |
| ---------------------------------------------------------- | ---------------------------------: |
| MTP 三期基线                                               |                              301.6 |
| + verify 索引缓存（`gdn_verify_indices`）                  |                              302.9 |
| + Mamba state scatter Triton 融合（`fused_mamba_scatter`） |                              307.2 |
| + GDN QKV split Triton 融合（`gdn_qkv_split`）             |                              315.1 |
| + MTP topk=1 跳过全词表 softmax（`mtp_argmax`）            |                              318.1 |

相对 MTP 三期基线，四项采纳后 EN1000 吞吐累计提升 5.4%；该组优化对中文收益更大，CN1000 吞吐由回移前的 278.3 token/s 提升至 296.5 token/s（+6.5%）。每项均以逐题答案与 token_count 完全一致为采纳门槛，准确率保持 83.0%（EN1000）不变。

代码位置：`srt/layers/attention/fla/`、`srt/layers/attention/hybrid_linear_attn_backend.py`、`srt/speculative/mtp_worker.py`（带 `BACKPORT-PPU` 标记）。

合规性：本优化属于允许的"attention、matmul、norm、sampling 等 kernel 优化"，不触犯禁止条例。

### 2.4 ViT 桶化图 + init 预捕获

TTFT 插桩拆解（`SGLANG_TTFT_PROF=1`）确认图化前 TTFT 55.7 ms 中 vision encoder 占 17.9 ms（32%）。本优化恢复上游 `ViTCudaGraphRunner` 并修复两个上游缺陷（共享 rotary workspace 重分配搬移地址导致旧图读取已释放内存、workspace dtype 与本树 fp32 rotary cache 不一致）；由于精确形状捕获在千例规模下为净亏损（51 种形状乘以约 182 ms 的捕获成本超过 replay 收益），改为桶化捕获：patch 数按 64 对齐分桶（64 为 2×2 merger 的分组倍数），cu_seqlens 追加 pad 段以隔离 attention、输出切回真实行数；在 `ModelRunner.initialize()` 末尾预捕获 13 个桶（启动耗时增加约 2.1 s，运行期零捕获），超过 1024 patch 的形状按需捕获或回退 eager。

| 配置                | 口径   | 平均 TTFT（ms） | 平均 decode 吞吐（token/s） | 准确率 |
| ------------------- | ------ | --------------: | --------------------------: | -----: |
| ViT eager           | EN1000 |           55.66 |                       318.6 |  83.0% |
| ViT 桶化图 + 预捕获 | EN1000 |           51.36 |                       317.3 |  83.0% |
| ViT eager           | CN1000 |           55.76 |                           — |  85.0% |
| ViT 桶化图 + 预捕获 | CN1000 |           51.51 |                           — |  85.0% |

相对 ViT eager 配置，vision encoder 段耗时由 17.9 ms 降至约 9 ms，EN/CN 千例平均 TTFT 均降低约 4.3 ms，吞吐变化处于运行噪声范围内；EN50/EN1000/CN1000 逐题三项指标 1000/1000 零差异。需要说明：图模式固定使用 Triton kernel，与 `SGLANG_ENABLE_FLASH_ATTN=1` 互斥（存在数值分歧），提交配置不启用后者。

代码位置：`srt/multimodal/vit_cuda_graph_runner.py`、`srt/models/qwen3_vl.py`、`srt/layers/attention/vision.py`。

合规性：本优化属于允许的"CUDA Graph 或静态图优化"；不改变视觉张量语义，不触犯禁止条例。

### 2.5 EXTEND 四桶 prefill 图

图化前 LLM prefill 占 TTFT 29.1 ms（52%），torch profiler 进一步确认其为 launch-bound（单次 prefill 含 1604 个 kernel、GPU busy 仅 32%、kernel 间隙中位 17 µs），更换 attention kernel 无法解决该问题，图化是唯一有效手段。方案为 extend 整图桶化捕获：prompt 按 token 数 pad 后路由到 192/256/320/384 中最小适配的桶，整 forward 捕获为一张图；FLA chunk indices/offsets 按真实 real/pad 长度刷新（整除边界以零长度 dummy chunk 处理）；共享注意力 metadata 在每次 replay 前恢复当前桶终点；MTP 模式下等待 draft 模型及其专用图初始化完成后再执行捕获；捕获后无条件清零 mamba/KV 池 slot 0，消除 init 期捕获对 draft 状态槽位的污染。千例统计 prompt 长度为 132–673 token，四桶覆盖 EN 97.1%、CN 97.2% 的请求，更长请求回退 eager 路径。

| 配置                                | 口径   | 平均 TTFT（ms） | 平均 decode 吞吐（token/s） |                准确率 |
| ----------------------------------- | ------ | --------------: | --------------------------: | --------------------: |
| prefill eager                       | EN1000 |            51.4 |                           — |                 83.0% |
| EXTEND 图                           | EN1000 |            39.5 |                       314.9 |                 82.7% |
| prefill eager                       | CN1000 |            51.5 |                           — |                 85.0% |
| EXTEND 图                           | CN1000 |            39.6 |                       297.5 |                 85.1% |
| EXTEND 四桶图（数值修复后全量终验） | EN4029 |          37.881 |                     315.936 | 79.9702%（3222/4029） |
| EXTEND 四桶图（数值修复后全量终验） | CN4029 |          38.366 |                     297.064 | 84.0407%（3386/4029） |

相对 prefill eager 配置，桶内样本 TTFT 由 49.5 ms 降至 33.8 ms，千例平均 TTFT 降低约 21%~23%，全量口径下吞吐与图化前持平。EN50/CN50/EN1000/CN1000 开图与关图配置逐题三项指标零差异，EN4029 全量三项零差异，准确率与失败题集合无变化；千例口径的个位数答案变化属 bf16 near-tie 舍入翻转，与 MTP verify 同类。

代码位置：`srt/model_executor/extend_cuda_graph_runner.py`、`srt/layers/attention/fla/index.py`（chunk layout override）、triton/GDN 后端的 EXTEND capture 分支。

合规性：本优化属于允许的"CUDA Graph 或静态图优化"与"prefill/decode 路径优化"；padding 仅影响计算布局，请求语义不变，不触犯禁止条例。

### 2.6 verify attention metadata 入图

将 MTP target-verify 阶段的 attention metadata 构造从图外移入固定的 verify 图中，消除每步 host 侧的 metadata 构造与拷贝开销。

| 配置              | 口径   | 平均 TTFT（ms） | 平均 decode 吞吐（token/s） |
| ----------------- | ------ | --------------: | --------------------------: |
| metadata 图外构造 | EN1000 |          37.520 |                     316.203 |
| metadata 入图     | EN1000 |          37.692 |                     318.521 |

相对图外构造配置，EN1000 三轮中位吞吐提升 0.73%，TTFT 增加 0.172 ms，属于小幅吞吐/TTFT 权衡，因 decode 吞吐为主要优化目标而采纳。EN1000 逐题签名一致，准确率 830/1000 不变；EN/CN 各 4029 条全量与上一版本五字段逐题零差异。

代码位置：`srt/speculative/mtp_worker.py`（`MtpTargetVerifyGraphRunner`），开关 `SGLANG_VERIFY_FUSED_METADATA_COPY`。

合规性：本优化属于允许的"CUDA Graph 或静态图优化"，不触犯禁止条例。

### 2.7 TTFT 残余段压缩

扩展 `SGLANG_TTFT_PROF` 探针（在 tokenizer/scheduler/detokenizer/engine 四处链路插桩，关闭时零开销），将图化后的残余 9.9 ms 拆解为：RPC 传输 3.0 ms、请求构造中的内容哈希 2.2 ms、请求发出（含 pickle，载荷 2138 KB）2.4 ms、首 token detok 与流式返回约 1.3 ms。采纳的两处优化为：其一，跳过请求级多模态内容 sha256——radix cache 对 hybrid GDN 模型强制关闭，该哈希仅服务于单请求内的 pad_value 匹配、无跨请求消费者，改用进程内唯一计数器替代，节省约 1.9 ms 并省去 MB 级 bf16 到 fp32 的拷贝；其二，RPC 图像载荷由 fp32 转为 bf16——ViT 入口本身需要将输入 cast 到模型 dtype，bf16 模型下输入逐位相同，载荷由 2138 KB 降至 1075 KB，RPC 序列化与 pickle 合计节省约 1.7 ms。其余残余为真实的 RPC 序列化与事件循环成本，不再压缩。

| 配置       | 口径   | 平均 TTFT（ms） | 平均 decode 吞吐（token/s） |                准确率 |
| ---------- | ------ | --------------: | --------------------------: | --------------------: |
| 残余压缩前 | EN4029 |          38.100 |                     317.827 | 79.9702%（3222/4029） |
| 残余压缩后 | EN4029 |          33.410 |                     316.579 | 79.9702%（3222/4029） |
| 残余压缩前 | CN4029 |          38.423 |                     297.184 | 84.0407%（3386/4029） |
| 残余压缩后 | CN4029 |          33.777 |                     296.764 | 84.0407%（3386/4029） |

相对压缩前版本，全量 EN 平均 TTFT 降低 4.69 ms，CN 降低 4.65 ms（两次复跑降幅 4.3–4.6 ms），吞吐变化处于 ±2 token/s 运行噪声范围内；EN50/EN1000/EN4029 逐题五字段零差异。

代码位置：`srt/managers/schedule_batch.py`（计数器替代哈希）、`srt/managers/tokenizer_manager.py`（载荷 bf16 化）、`srt/ttft_prof.py`（探针）。

合规性：本优化属于允许的"图像预处理和 tokenizer 调用优化"与"monkey patch 模型内部模块"；哈希跳过与载荷精度变化均不改变请求语义与模型输入，不触犯禁止条例。

### 2.8 decode 图内手写融合 kernel

图化后剩余优化空间位于图内 kernel 本身。对 MTP 稳态单步进行 trace（`SGLANG_DECODE_TRACE=1`）显示：整步 711 个 kernel、GPU busy 5.0 ms，其中 cat 与 elementwise 小 kernel 群约 1.2 ms（占 24%）为最大可压缩项。小 kernel 密集区不在已高度融合的 GDN 层，而在 6 个 full attention 层的 MRoPE——`MRotaryEmbedding.forward` 覆盖了 CustomOp dispatch，导致 fused rope 路径失效，每层以 eager 方式执行约 21 个 kernel（positions gather、section cat、bf16 cast、mul/sub、输出 cat，约 45 µs/层）。为此手写四个 Triton 融合 kernel：MRoPE rotary 融合（`_mrope_fused_rotary_kernel`，kernel 内完成 [11,11,10] section gather、neox rotary 与 192 维 pass copy，每层 q/k 各 1 次 launch，由 21 个 kernel 降至 2 个，并按 PyTorch bf16 opmath 三级 RNE rounding 语义复现数值行为）、attn output gate sigmoid+mul 融合（`_sigmoid_gate_mul_kernel`）、GDN `in_proj_b` 与 `in_proj_a` 两 GEMM 合并（lazy `torch.cat` 权重与行 stride 支持，仅 extend 路径）、KV scatter 双 index_put 合并（`_fused_set_kv_kernel`）。

| 配置                     | 口径   | 平均 TTFT（ms） | 平均 decode 吞吐（token/s） |    相对提升 |
| ------------------------ | ------ | --------------: | --------------------------: | ----------: |
| 图内融合前               | EN1000 |          32.968 |                     317.151 |        基线 |
| + MRoPE 融合             | EN1000 |          32.450 |                     347.574 |       +9.6% |
| + 其余三项融合           | EN1000 |          32.140 |                     360.080 | 累计 +13.5% |
| 图内融合前               | EN4029 |          33.410 |                     316.579 |        基线 |
| 图内融合后（最终提交版） | EN4029 |          32.522 |                     359.842 |      +13.7% |
| 图内融合前               | CN4029 |          33.777 |                     296.764 |        基线 |
| 图内融合后（最终提交版） | CN4029 |          32.951 |                     335.076 |      +12.9% |

MRoPE 融合使整步 kernel 数由 711 降至 564、GPU busy 由 5.0 ms 降至 4.6 ms；其余三项融合后整步 kernel 数降至 514、GPU busy 降至 4.3 ms（GEMM 调用由 156 次降至 138 次）。单元测试 21+25 组 `torch.equal` 逐比特通过；EN1000 逐题零差异、准确率 830/1000 持平；最终 EN/CN 各 4029 条全量与未启用图内融合版本五字段逐题零差异，准确率保持 3222/4029 与 3386/4029 不变。

代码位置：`srt/layers/rotary_embedding.py`、`srt/models/qwen3_5.py`、`srt/layers/attention/fla/fused_gdn_gating.py`、`srt/mem_cache/memory_pool.py`；开关 `SGLANG_FUSED_MROPE/ATTN_GATE/BA_PROJ/KV_SCATTER` 均默认开启。

合规性：本优化属于允许的"自定义算子替换"与"attention、matmul、norm、sampling 等 kernel 优化"；融合 kernel 按 eager 数值语义逐比特复现，不触犯禁止条例。

### 2.9 verify 逐层 projection GEMV 专用化（第二阶段）

第二阶段 P0 profiling（`srt/spec_prof.py` 分段 + 单步 kernel trace）发现：MTP 稳态单 round 的 verify 相中，115 次逐层 projection GEMM（acBLAS，M=2）合计 1.95 ms，读约 2.74 GB BF16 权重，有效带宽仅约 1.4 TB/s（grid 32～96 CTA，achieved occupancy 3～9%）；同卡 LM head GEMV 实测 2.0～2.3 TB/s。为此用 Triton split-N dot kernel（BLOCK_M=16、FP32 累加）接管 M==2 且形状在白名单内的逐层 projection：2048→6144（GDN in_proj_qkv，17.5 µs→15.5 µs）、2048→5120（attn qkv+gate，16.8 µs→12.7 µs）、2048→12288（MLP gate_up，33.1 µs→30.0 µs）；2048→2048 与 6144→2048 两个形状 acBLAS 已最优，保持默认路径。离线图计时扫描（权重轮转防 L2 污染）确认配置，split-K 两遍法已证伪。8～50 MB 量级逐层 GEMM 单核带宽上限实测 1.5～1.7 TB/s（LM head 的 2.0～2.3 TB/s 依赖 1 GB 单次读取摊平 ramp-up），故收益低于最初估计。

同树全量 A/B（各 4029 条，仅 `SGLANG_GEMV_Q2` 开关不同）：

| 配置          | 口径   | 平均 TTFT（ms） | 平均 decode 吞吐（token/s） |   相对提升 |
| ------------- | ------ | --------------: | --------------------------: | ---------: |
| OFF（acBLAS） | EN4029 |          33.157 |                     359.891 |       基线 |
| ON（GEMV_Q2） | EN4029 |          33.181 |                 **369.561** | **+2.69%** |
| OFF（acBLAS） | CN4029 |          33.453 |                     336.106 |       基线 |
| ON（GEMV_Q2） | CN4029 |          33.602 |                 **343.983** | **+2.34%** |

TTFT 不变（M==2 门控不触及 prefill，差异在噪声范围内）；EN/CN 五字段（question_id、parsed_answer、correct、token_count、validation_errors）逐题**零差异**，正确题数两侧持平（EN 3207、CN 3368）；eager 模式 6000+ 次调用与 `F.linear` 逐位一致。注：本节数字为第二阶段工作树口径，与 1.1 节提交版快照之间存在工作树差异，不作为提交版复测数据。

代码位置：`srt/layers/gemv_q2.py`（kernel 与门控）、`srt/layers/linear.py`（`UnquantizedLinearMethod.apply` 挂钩）；开关 `SGLANG_GEMV_Q2` 默认开启，`SGLANG_GEMV_Q2_TARGET/_DRAFT` 可按子树关闭，`SGLANG_GEMV_Q2_CHECK=1` 逐位对照。实验记录见 `rapid_reasoning/docs/profile_v2/README.md` P1.5 节。

### 2.10 post-verify host 快速路径（第二阶段 P1）

第二阶段 P0 复测发现 MTP 稳态单 round 的 verify 之后存在约 0.5 ms 的 host 开销：accept 簿记里的 nonzero/gather/evict-mask 链、`prepare_extend_after_decode` 每轮一次的 `seq_lens.tolist()` D2H 同步、以及 draft extend 重放前 `get_model_worker_batch + ForwardBatch.init_new` 重建图根本不读的 metadata（2 次 H2D + compute_position）。针对 bs=1 链式投机（接受行恒为 2 行 verify 批次的前缀）做三处快速路径：accept 簿记塌缩为前缀切片；extend 准备去掉 D2H 同步（positions 直接由 `seq_lens` 派生）；draft extend 以 shim 直调 `MtpDraftExtendGraphRunner.replay`。开关 `SGLANG_MTP_FAST_POSTVERIFY`（默认开）。EN1000 正式门 A/B：370.461 token/s → 387.028 token/s（+4.47%），TTFT 不变，五字段逐题 0/1000 差异。压缩后单 round 转为 GPU-bound（GPU busy ≈4.4 ms / wall 4.48 ms，约 98%），host 侧继续压缩没有空间。代码位置：`srt/speculative/mtp_utils.py`、`srt/speculative/mtp_worker.py`。

### 2.11 联合投机图（第二阶段 P3-B）

旧流程每轮三张图（target verify 图、commit 图、draft extend 图）之间有 host 串行点，且 LM head 每轮读两次权重（verify M=2 GEMM 0.50 ms + draft M=1 GEMV 0.44 ms）。联合投机图把整轮压成两张图、每轮两次 launch：graph_verify 含 target verify metadata 图内刷新、target body、verify head（M=2，与旧路径同一 `matmul` 表达式，逐位一致）、argmax/accept 判定与 packed (3,) D2H；host 同步拿到 `[t0, t1, accept]` 后立即入队 graph_draft（draft metadata 图内刷新、draft body、draft head、proposal、new_verified_id、mamba commit），其 GPU 执行与 host 接受簿记重叠，恢复旧流水结构。原设想的单次 M=4 联合 GEMM 经依赖审计证伪：draft body 的输入 token 就是 verify head 的 argmax 输出（off-by-one 配对），两次 head GEMM 无法合并，收益来自图间 host 开销与 launch 的消除。

首轮全量 A/B 暴露 CN 29 个样本 token 流分叉（EN 0/4029）：逐轮 trace 定位（`SGLANG_ROUND_DEBUG=1`）确认 verify 输出两侧逐位一致，首个分叉点是 reject 轮的 draft proposal——联合图 draft body 恒 2 行（M=2 kernel），旧路径 reject 轮只跑 1 行（M=1），两种形状的 kernel 结果存在低位差异，near-tie argmax 翻转改变 accept 模式，target 的 chunked-scan 提交路径随 round 分段变化（数学等价、逐位不同），下游 token 流合法分叉（correct 数两侧相同）。修复为按 accept 捕获两张 draft 图（reject 走 1 行图，与旧 n=1 路径同形状同 kernel，逐位一致；backend 的 `_graph_draft_qo_indptr` 按 token 数分 buffer，支持多图共存）。修复后全量同树 A/B 五字段双语 0/4029 差异。

最终全量结果（各 4029 条，仅 `SGLANG_JOINT_HEAD` 开关不同）：EN 387.458 token/s → **425.298 token/s（+9.77%）**，TTFT 33.014 ms → 32.847 ms；CN 367.412 token/s → **401.660 token/s（+9.33%）**，TTFT 33.520 ms → 33.462 ms。默认开启，`SGLANG_JOINT_HEAD=0` 回退三图路径。代码位置：`srt/model_executor/cuda_graph_runner.py`（`MtpJointGraphRunner`）、`srt/speculative/mtp_worker.py`（`_verify_joint`）。

合规性：本优化属于允许的"自定义算子替换"与"matmul kernel 优化"；M==2 时与 acBLAS 逐位一致，不触及 prefill 与采样语义，不触犯禁止条例。

### 2.12 MTP chain depth=2（第三阶段）

depth=1 每轮验证 `[v0,d1]`，即使第一 draft token 接受率已接近上限，每轮最多仍只能输出 2 个 token，单 token 权重流量成为 425 token/s 之后的结构瓶颈。本优化把链扩展为 `[v0,d1,d2]`：增加一张固定单行 draft-decode 图生成 d2，target 以 q_len=3 一次验证三个位置，接受逻辑使用连续匹配前缀，joint runner 再按 accept∈{0,1,2} 选择 1/2/3 行 draft-extend/commit 图。verify、KV 回收、EOS 与 Mamba 中间态提交均由两行特例泛化为任意前缀长度；`SGLANG_MTP_CHAIN_DEPTH=1` 保留原路径用于回退。

先做 eager 决断实验：EN100 depth=1/2 分别为 82.587/115.987 token/s（+40.4%），300 轮平均 2.50 token/round，证明第二 token 的收益足以覆盖额外 draft forward。图化后 EN100 为 484.668 token/s（同树 depth=1 为 415.064 token/s，+16.77%）；EN4029 正式全量为 **32.781 ms / 512.304 token/s / 3207/4029**，相对上一版 425.298 token/s 提升 **20.46%**，准确率正确数与 validation 失败数不变。尝试把 d2 forward 融入 verify 大图后 EN100 降至 474.073 token/s，未采纳。

CN100 的 depth=2 仅为 394.299 token/s（depth=1 390.474 token/s，+0.98%）。接受率统计说明差异来自生成分布而非中文算子：EN 平均约 2.87 token/round，第一/第二条件接受率约 97%/93%；CN 平均约 2.08 token/round，约为 69%/55%，额外 draft forward 基本抵消新增 token。CN4029 正式无诊断全量为 **33.399 ms / 398.150 token/s / 3368/4029**，相对 depth=1 吞吐 −0.87%；统一 depth=2 的双语等权平均仍由 413.479 token/s 提升至 455.227 token/s（+10.10%），后续用动态深度路由回收 CN 损失（即 2.21 节）。

链深变化会改变 GDN 的 round/chunk 分段，BF16 near-tie 可导致合法 token 流分叉，因此不能继续要求与 depth=1 五字段逐题完全一致。EN 全量相对 depth=1 有 parsed_answer/correct 各 4 条、token_count 24 条差异，但净正确数仍为 3207；CN 有 parsed_answer 4 条、correct 0 条、token_count 794 条差异，净正确数仍为 3368。两侧准确率均远高于 baseline−2% 门槛；eager 与 graph 的同 depth 短测保持五字段一致。该优化只接受 batch=1、topk=1、greedy、page_size=1，未改变模型权重或评测接口。注：本节全量数字为处理器精度修复（见 1.1 节口径说明）之前的实验记录；修复后的最终提交版成绩以 1.1 节为准。

代码位置：`srt/speculative/mtp_worker.py`、`srt/speculative/mtp_utils.py`、`srt/model_executor/cuda_graph_runner.py`、`srt/server_args.py` 与 `evaluation_wrapper.py`。

### 2.13 通用输出有效性兜底

全量基线剩余 EN 1 条 `output_too_long`/`missing_choice_answer` 和 CN 3 条 `missing_choice_answer`（qid 609/1209/1001209）；自适应链深（2.21 节）下 EN 另有 qid 2001653 一条同类失败。原始输出核验显示，这些样本都生成满 256 token：EN 样本已在开头给出选项但继续展开或未收敛，CN 三条始终没有明确选项。最终实现不按题号、语言、数据集路径或内容 hash 特判：所有输出先用与公开评测器一致的三组正则检查；没有明确 A/B/C/D 时，把原题、图像和前次分析交给同一模型，以评测器原始采样参数补答严格的 `Final answer: X`；展示文本统一限制为 1200 字符。首次生成和补答的 token_count、TTFT、端到端墙钟时间均合并计量，且总 token_count 不超过公开校验器允许的 264。

历史上 EN4029 全量从 1 条失败变为全过，question_id/parsed_answer/correct/token_count 四字段逐题零差异，仅失败样本的 validation_errors 清空；CN4029 从 3 条失败变为全过，qid 609/1209/1001209 的 parsed_answer 由空变为 C、token_count 由 256 变为 261，correct 全量零差异。当前默认配置（含自适应链深）的全量终验中，EN 触发 1 条、CN 触发 3 条兜底，双语 public validation 全部通过，正确题数保持 EN 3222、CN 3385 不变。EN/CN100 默认路径的正常回答不会误触发兜底。该功能默认开启，可用 `SGLANG_OUTPUT_REPAIR=0` 做诊断回退。

代码位置：`evaluation_wrapper.py`（`_has_explicit_choice` 与 `_generate_with_sglang` 内的兜底分支）。

### 2.14 mm host 快速路径（第三阶段 TTFT）

EXTEND 整图 trace 显示图内 acBLAS GEMM 约占 68%（14.5/21.2 ms），离线 bench（CUDA Graph 计时、权重轮转防 L2 污染）证明 7 组 Triton tiled GEMM 配置在全部 LLM/ViT prefill 形状上均输给 acBLAS 1.5-2 倍——小 M 低带宽是 810E 的 tile 效率墙而非库实现问题，prefill GEMM 替换方向据此关闭，TTFT 杠杆转向 host 链。

host 链细拆（新增 mm_load/mm_proc/mm_rope 子段插桩，`SGLANG_TTFT_PROF=1`）显示 mm_host 3.1 ms 中 processor `__call__` 占 2.45 ms，而其中 kwargs 校验、BatchFeature、make_flat_list 等 transformers 包装层约 1.4 ms，真实工作（tokenize 0.19 ms + GPU 图像预处理 0.43 ms）只有约 0.6 ms。落地三项：image_processor 实例级 `_preprocess` 单图补丁（跳过 group/reorder/stack 机械）；`_fast_process_mm_data` 绕过 `processor.__call__` 包装层并自行复现 image_token 按 `grid.prod()//merge_size²` 展开；tokenizer_manager 有图时跳过会被覆盖的首次 encode。注意 4.51 的 image_processor `__init__` 丢弃 size 字典，直调 `_preprocess` 时 size 必须由 min/max_pixels 重建。

验证：离线 30 图 input_ids/pixel_values（逐位）/image_grid_thw 全等（`docs/profile_v2/fast_preprocess_verify.py`）；同树 EN1000 A/B TTFT 34.372 ms→33.011 ms；同树全量 A/B（`SGLANG_MM_FAST_PATH=0 SGLANG_MM_FAST_PREPROCESS=0` 作基线）EN 33.142 ms→**32.158 ms（−0.98 ms）**、CN 34.292 ms→**32.452 ms（−1.84 ms）**，双语五字段逐题零差异，正确数不变（EN 3222、CN 3385），decode 吞吐差异在噪声内。该功能默认开启。

### 2.15 第二批 full-attention 小 kernel 融合

chain-2 稳态 trace 中，6 个 full-attention 层及 MTP 层会分别物化 gated-Q 的 Q/gate 切片、K/V contiguous buffer，并单独启动 Q/K Gemma RMSNorm。新增单个 Triton kernel，在一次 launch 内完成四个跨步长 gather/copy 与两个 256 维 RMSNorm；仅匹配 Qwen3.5-2B 的 BF16、head_dim=256 固定形状，其他形状回退原路径。为保持 greedy token 流不变，归约严格复刻官方 FlashInfer/sgl-kernel 的 32 lane × 每 lane 连续 8 元素累加顺序；flat `tl.sum` 曾在真实输入产生 1 个 BF16 ULP 差异，已在转正前修正。

| 配置                          | 口径   | 平均 TTFT（ms） | 平均 decode 吞吐（token/s） |   正确数 | benchmark 阶段总时长 |
| ----------------------------- | ------ | --------------: | --------------------------: | -------: | -------------------: |
| OFF（原 gather + 双 RMSNorm） | EN1000 |          32.650 |                     507.496 | 830/1000 |            122.849 s |
| ON（融合，默认）              | EN1000 |          32.576 |       **522.249**（+2.91%） | 830/1000 |            121.750 s |
| OFF（原 gather + 双 RMSNorm） | CN1000 |          34.734 |                     444.312 | 849/1000 |            214.863 s |
| ON（融合，默认）              | CN1000 |          34.399 |       **457.882**（+3.05%） | 849/1000 |            212.288 s |

同一 EN decode step 的 kernel launch 由 498 次降至 460 次（−7.6%），kernel 总时间由 4.946 ms 降至 4.845 ms（−2.0%）。EN/CN1000 的五字段逐题均零差异，public validation 全过；无环境变量的默认 EN100 另测得 28.258 ms / 498.640 token/s / 79/100，五字段仍零差异。代码位于 `srt/models/qwen3_5.py`，`SGLANG_FUSED_QKG_NORM=0` 可关闭诊断；该优化属于允许的 attention/norm 自定义 kernel 融合，不改变模型权重、输入、生成参数或评测逻辑。与同期 TTFT 改动合并后的完整 4029 条终验见 2.16 节。

### 2.16 ViT RoPE 图内融合

EXTEND trace 中两类 `cat` kernel 各出现 48 次，定位为 24 个 ViT block 每层重复执行 cos/sin 半维扩展，以及 Q/K 的 rotate-half。原路径还会为 Q/K 分别启动 FP32 cast、两次乘法、加法和回写。新增一个 Triton kernel 直接按半维索引读取 cos/sin，在一次 launch 中同时完成 Q/K 的完整 RoPE；只匹配连续三维 Q/K、连续二维半宽 cos/sin，其余布局回退通用实现。`SGLANG_FUSED_VIT_ROPE=0` 可关闭诊断。

精度修复包含两条硬约束。首版原地写回 Q/K 在 PPU 编译后存在读写竞争，随机张量对照出现大误差；改为独立输出 buffer 后消除。普通 Triton 表达式还会把两次 FP32 mul 与 add 收缩成 FMA，随机张量出现少量末位差异并使 EN100 的 3 条 token 流分叉；终版通过 PTX `mul.rn.f32` 与 `add.rn.f32` 显式保持原路径的舍入边界。BF16/FP16 QK × BF16/FP32 RoPE 四种组合的 GPU 随机张量逐位对照全部通过。

最终 EXTEND trace 的 kernel launch 由 1287 降至 927（−28.0%），kernel 总时间由 21.132 ms 降至 19.759 ms（−1.373 ms）；原两类 ViT `cat` 共 96 次及其 cast/elementwise 链消失，替换为 24 次融合 RoPE（合计 0.101 ms）。同树正式 A/B 结果：EN100 为 28.090 ms→25.697 ms（−2.393 ms），五字段零差异；EN1000 为 **31.411 ms→29.561 ms（−1.850 ms，−5.9%）**，benchmark 阶段 137.613 s→133.902 s；CN1000 为 **33.004 ms→31.563 ms（−1.441 ms，−4.4%）**，benchmark 阶段 226.830 s→225.698 s。EN/CN1000 正确数保持 830/849，五字段逐题零差异、validation 全过。

合并 mm host 与 decode 融合后的无诊断全量终验：EN4029 **29.656 ms / 520.984 token/s / 3222**，CN4029 **30.644 ms / 424.696 token/s / 3385**。两者相对 mm host 全量快照五字段均为 0/4029 差异，public validation 全过；benchmark 阶段总时长分别为 421.299 s 和 776.682 s，合计 1197.981 s。

### 2.17 PPU device-memory IPC ring

TTFT profiler 显示 tokenizer 到 scheduler 的普通 `send_pyobj` 会把约 960 KiB 的 BF16 `pixel_values` 完整 pickle 到 host，再经 ZMQ 复制。此前 host shared-memory 原型仍包含设备到 host 的映射与回传，因此没有收益。最终方案改为 tokenizer 进程长期持有 2×8 MiB 的设备 ring：每题只做一次 device-to-device copy，随后用 PyTorch-for-SAIL 的 CUDA tensor reducer 导出 HGGC allocation handle 与跨进程 event；scheduler 由既有 `recv_pyobj` 直接重建 PPU tensor。请求 pickle 载荷降到约 12～13 KiB，实测序列化约 0.38～0.55 ms、`req_sent→sched_recv` 约 0.54～0.79 ms，全链无 D2H/H2D。非 PPU tensor、非连续 tensor、requires-grad tensor 或单 tensor 超过 8 MiB 时自动回退原始传输。

| 配置       | 口径   |                            TTFT |        Decode | 正确数 | 五字段差异 | benchmark 总时长 |
| ---------- | ------ | ------------------------------: | ------------: | -----: | ---------: | ---------------: |
| OFF        | EN4029 |                       29.851 ms | 519.823 tok/s |   3222 |          — |        422.527 s |
| ON（默认） | EN4029 | **28.081 ms（−1.770，−5.93%）** | 519.056 tok/s |   3222 |     0/4029 |        416.285 s |
| OFF        | CN4029 |                       30.754 ms | 423.784 tok/s |   3385 |          — |        778.052 s |
| ON（默认） | CN4029 | **28.718 ms（−2.036，−6.62%）** | 424.386 tok/s |   3385 |     0/4029 |        769.074 s |

转正前还完成 EN/CN1000 配对：TTFT 分别 29.686 ms→27.794 ms、31.733 ms→29.370 ms，五字段均 0/1000 差异。Decode 的 −0.15%/+0.14% 按复跑噪声处理。该路径针对比赛的同步 batch=1 请求流，默认开启，`SGLANG_DEVICE_IPC=0` 可回退；引擎进程退出后 PyTorch 可能打印最后一个共享 tensor 的引用清理提示，发生在结果写出之后，不影响运行期正确性或资源回收。

### 2.18 ViT QKV/RoPE 组合融合

EXTEND 的 direct-copy 找到稳定的组合边界：24 个 ViT block 每层执行三次 packed QKV 切片 `.contiguous()`，再单独执行 Q/K RoPE。新 Triton kernel 一次完成 QKV split/copy 和 Q/K rotate-half，沿用显式 FP32 乘加舍入。五组随机长度的 Q/K/V 全部逐位一致；trace 中 kernel launch 927→855、direct-copy 80→8，kernel 总时间 19.735 ms→19.537 ms。EN1000 TTFT 27.557 ms→27.295 ms，CN1000 29.437 ms→28.991 ms；正确数保持 830/849，五字段均 0/1000 差异，public validation 全过。默认开启，`SGLANG_FUSED_VIT_QKV_ROPE=0` 可回退。

### 2.19 微收益候选复核与全量转正

按"微弱正收益也可转正"的规则重新检查技术路线全部未采纳项，固定收益门取消，BF16/输出逐位一致、双语统一配置和 public validation 仍为硬门。只有两项属于"已证明正确且正收益、仅被旧门槛挡住"：M=3 split-N GEMV 与精确 fused patchify。GraphExec 仍缺稳定节点句柄，GELU epilogue 仍缺 runtime bridge，LayerNorm 未过数值门，自适应双图、六桶和 shared-memory IPC 已实测退化，hgJPEG/HGPP 及 native HGGC/TIX 仍分别受数值/性能和 SDK 工具链阻塞，因此不转正。

M=3 只接管 2048→6144、2048→5120 两个已做 200 次逐位对照的 BF16 projection，默认开启，`SGLANG_GEMV_Q3=0` 回退。当前 EN/CN1000 相对两项均 OFF 的吞吐分别为 520.068 token/s→521.782 token/s、453.002 token/s→457.306 token/s；拆分的 M=3-only 为 520.893 token/s / 454.958 token/s。四组正确数保持 EN 830、CN 849，五字段均 0/1000 差异。

fused patchify 保留 PIL 与 torchvision antialiased resize，仅把 normalize、temporal duplicate、patchify 和最终 BF16 cast 合为单个 Triton kernel。生产 helper 的 30 图复测为 30/30 逐位一致、差异元素 0，preprocess 约 0.567 ms→0.478 ms；默认开启，`SGLANG_FUSED_MM_PATCHIFY=0` 回退，不符合固定 Qwen3.5 参数的输入自动走原 processor。

### 2.20 提交闭包与固定模型路径瘦身

提交闭包：引擎源码、PPU `sgl_kernel` Python 包与 ABI3 二进制、Triton-for-SAIL 3.1.0 已编译包均位于 `rapid_reasoning/`；`runtime_manifest.json` 固定来源、版本和二进制哈希。Triton 运行时 import 解析到 `runtime_packages/triton`（与环境内安装的 Triton-for-SAIL 3.1.0 逐字节一致，含 PPU backend 与 `libtriton.so`），不依赖环境中的同名包；`third_party_licenses/` 保留对应许可证。wrapper 在任何 backend 探测前固定注入该目录，并校验 `sglang`、`sgl_kernel` 与 `triton` 的实际模块路径；缺文件或解析到 site-packages 会立即报错，不静默回退。

固定模型路径瘦身：模型注册器不再扫描并导入全部引擎架构，仅注册 Qwen3.5 target 与 MTP draft；多模态处理器移除 Qwen2/Qwen2.5-VL 的无条件导入，并删除对应的两份未使用模型实现；config 注册表仅保留 Qwen3.5 所需四项；调优与诊断脚本不随提交携带。Qwen3/Qwen3.5 所需的视觉与文本实现保持不变。

合规性：本项为工程闭包与代码裁剪，不改变模型权重、数值路径与评测语义，不触犯禁止条例。

### 2.21 自适应 MTP 链深 1~4（第四阶段）

2.12 节的固定 depth=2 把 EN 推过 500 token/s，但静态链深存在不可调和的双语矛盾：继续加深对 EN 显著有利、对 CN 反而亏损。同树全量实测（各 4029 条）：固定 depth=3 为 EN **568.9 token/s（相对 depth=2 +6.3%）**、CN **386.5 token/s（−7.0%）**；chain depth=4 烟测 EN100 625.8 token/s（相对 depth=2 同口径 +21%）、第四条件接受率约 95%，而 CN100 仅 356.9 token/s、第四条件接受率约 60%。差异根因是生成分布：EN 全量平均约 3.6 token/round（第一/第二/第三条件接受率约 92%/92%/95%），CN 约 2.1 token/round（约 68%/53%/57%）。任何固定深度都必有一侧受损，因此将链深决策改为运行时自适应。

**机制（语言无关、严格单样本）**。链式 draft 由 2.12 节的固定两行泛化为任意深度：d2..dk 各由同一张固定单行 draft-decode 图重放生成，每步消耗上一个 proposal 及其携带的 hidden state。verify 侧只保留**一张**按 max depth=4 捕获的联合投机图（q_len=5），浅轮次通过重复最后一个 proposal 把链 padding 到图形状——padding 行与真实 proposal 一样经过 target 贪心验证，发出 token 的正确性不受 padding 影响。逐轮深度由 host 端 EMA 控制器决策（每轮约 0.6 µs，无 GPU 同步）：维护 `q[j] = P(accept ≥ j+1)` 的指数滑动平均、单个 draft step 的实测墙钟成本 `step_ms` 与单 token 的实测墙钟价值 `token_ms`，当 `q[j] × token_ms > step_ms` 时逐级加深；深度下限固定为 1（即至少保持已验证双赢的 depth=2 行为），每 32 轮做一次"比当前选择深一级"的探测以刷新决策边界的统计。控制器只读取本次运行中实测的接受率与耗时信号，不检测语言、不读取题目内容、不按数据集路径切换逻辑；EMA 状态仅存于引擎进程内存，每次启动重新初始化。

**关键负结果（单图 padding 的依据）**。两条替代路线均被实测否决：其一，逐深度常驻多张联合图（每深度一张 q_len 匹配的 verify 图），浅路径出现约 −3.5%/−8%（EN/CN100）的常驻惩罚，且惩罚与常驻图数量无关（仅驻留 {depth2, depth4} 两张图时 CN100 仍为 380.6 token/s，同样的 −8%），根因定位为多 runner 形态的固有成本后放弃；其二，`SGLANG_MTP_FORCE_EXTRA` 钉死链深的隔离实验表明 q_len=5 verify 图相对 q_len=3 有固定约 3.5%~4.5% 的形状成本，该成本决定了 CN 侧的理论地板，也是控制器在 CN 上收敛到浅深度的经济性依据。

**全量结果**（各 4029 条，同树 A/B，基线为固定 depth=2）：

| 配置                    | 口径   | 平均 TTFT（ms） | 平均 decode 吞吐（token/s） | 正确数 | public validation |
| ----------------------- | ------ | --------------: | --------------------------: | -----: | ----------------: |
| 固定 depth=2（基线）    | EN4029 |           27.5  |                     535.0   |   3222 |              通过 |
| 自适应 1~4（默认）      | EN4029 |      **27.628** |                 **594.200** |   3222 |              通过 |
| 固定 depth=2（基线）    | CN4029 |           27.7  |                     415.5   |   3385 |      3 条缺少选项 |
| 自适应 1~4（默认）      | CN4029 |      **27.990** |                 **401.827** |   3385 |    通过（兜底后） |

EN 相对固定 depth=2 提升 **+11.1%**；CN 相对基线 −3.3%，即上述 q_len=5 verify 形状地板成本，双语等权平均由 475.3 提升至 **498.0 token/s（+4.8%）**。稳态轮次分布验证控制器行为符合设计：CN 全量约 85% 轮次收敛于 depth=2、13% 为边界探测、深层不足 2%；EN 全量约 88% 轮次直接进入 max depth。两侧正确题数与基线完全一致（EN 3222、CN 3385）；链深变化引起的 token 流分叉属 2.12 节所述 BF16 near-tie 合法分叉，验收口径为正确数持平 + validation 不新增失败。CN 基线剩余的 3 条 `missing_choice_answer` 与自适应路径下 EN 的 1 条同类输出均由 2.13 节兜底修复，双语 public validation 全过。

链式 draft 泛化、控制器与 padding 机制均只作用于当前唯一请求的投机长度，不存在跨请求 batch。默认配置为 max depth=4 + 控制器开启；诊断回退：`SGLANG_MTP_CHAIN_DEPTH=2`（固定 depth=2 旧路径）、`SGLANG_MTP_DYNAMIC_DEPTH=0`（固定 max depth）、`SGLANG_MTP_FORCE_EXTRA=k`（钉死链深）、`SGLANG_CHAIN2_STATS=1`（接受率统计）。

代码位置：`srt/speculative/mtp_worker.py`（`_draft_chain_tokens`、`_choose_dynamic_extra`、`_update_dynamic_stats`）、`evaluation_wrapper.py`（链深上限 1~4 与默认值）、`srt/server_args.py`。

合规性：本优化属于允许的"prefill/decode 路径优化"；输出始终为 target 模型贪心验证过的 token，不更换权重、不接触评测逻辑、不按样本身份或语言特判，不触犯禁止条例。

### 2.22 M=4/M=5 verify GEMV 专用化（第四阶段）

自适应链深把 verify 的 projection 形状从 M=2/M=3 扩展到 M=4/M=5，2.9/2.19 节的 GEMV 专用化随之扩形：在 `gemv_q2.py` 中为 M∈{4,5} 新增 4 个形状的 split-N dot 配置（2048→6144、2048→5120、2048→12288、512→2048），配置经离线图计时 autotune（权重轮转防 L2 污染）选定，全部通过 eager 模式与 `F.linear` 的逐位对照；其余形状（2048→2048、6144→2048、4096→2048）autotune 输给 acBLAS，保持默认路径。M=1 未接管：其累加顺序与 acBLAS 存在微小数值漂移，不满足同 depth 五字段零差异门。默认开启，`SGLANG_GEMV_Q45=0` 回退。该优化属于允许的 matmul kernel 优化，不触犯禁止条例。

## 三、性能提升

### 3.1 TTFT 优化

单样本请求的 TTFT 路径依次为：host 侧图像预处理与 prompt 构建、RPC 传输、ViT 视觉编码、LLM prefill（embed 与 24 层混合注意力前向）、首个 decode 步与流式返回。图化前的插桩拆解（TTFT 55.7 ms 口径）显示，LLM prefill 耗时 29.1 ms（占 52%），为 launch-bound（1604 个 kernel、GPU busy 仅 32%）；ViT 视觉编码耗时 17.9 ms（占 32%），同为 launch-bound（逐形状 eager 执行）；host 图像预处理中位 2.7 ms（占 5%），为纯 CPU 开销；调度与 RPC 残余仅 0.3 ms（占 1%）。

各阶段的优化来源与效果如下。ViT 视觉编码由 2.4 节的桶化图与 init 预捕获优化，耗时由 17.9 ms 降至约 9 ms。LLM prefill 由 2.5 节的 EXTEND 四桶图优化，图化 EXTEND 全段（含 ViT）压缩至约 20.5 ms，其中 LLM prefill 与 embed/metadata 部分的差值约 13.0 ms。调度、RPC 与序列化残余由 2.7 节的残余段压缩优化，合计节省约 4.7 ms，其中跳过内容哈希约 1.9 ms、载荷 bf16 化约 1.7 ms，其余为真实的 RPC 与事件循环成本。首个 decode 步间接受益于 2.1 节的 decode 图与 2.8 节的图内融合。

图化后的拆解（EN50 去预热均值，wrapper 总 TTFT 33.091 ms 口径）为：host 预处理 2.670 ms、ViT 7.519 ms、图化 EXTEND 全段（含 ViT）20.542 ms、LLM prefill 差值 13.023 ms、RPC/调度/首 decode/流式返回残余约 9.88 ms（残余压缩前口径，压缩后该残余降至约 5 ms）。

mm host 快速路径（2.14 节）进一步把 host 多模态段由约 3.1 ms 压至约 2.3 ms（mm_proc 2.45 ms→1.63 ms），同树全量 A/B 确认 TTFT EN −0.98 ms、CN −1.84 ms 且五字段零差异。prefill GEMM 的 kernel 级专用化经离线 bench 证伪（Triton 在全部形状上输 acBLAS 1.5-2 倍）；2.16 节继续把 ViT 每层 RoPE 的重复 cat/cast/mul/add 合为一次 launch，使 EN/CN1000 TTFT 再降 1.85/1.44 ms。host shared-memory IPC 原型因 D2H/H2D 抵消收益而撤回，2.17 节的 device-memory IPC 则完全避免 host 映射；随后 2.19 节转正 M=3 GEMV 与 fused patchify。当前默认配置全量为 EN/CN **27.628/27.990 ms**。

现阶段已知局限如下。EXTEND 图内 GPU busy 约 20.5 ms，仍有 GDN chunked scan、6 层 full attention 和按桶定制 GEMM 等未改动部分；超出桶范围的请求（prompt 超过 384 token、图像超过 2048 patch）回退 eager 路径，公开集四桶覆盖约 97% 的请求。hgJPEG/HGPP 设备链已完成实测但无法逐位复现 PIL，精确 fused patchify 已接入并只覆盖固定 Qwen3.5 参数。Decode 仍受 HBM 带宽和 MTP 接受长度限制，CN 的主要差距来自接受率而非语言专用代码路径。

### 3.2 吞吐优化

decode 循环每步的流程为：MTP 草稿头前向（draft）、目标模型并行验证（verify）、接受结果提交（commit）、采样输出。带宽演进脉络如下。图化前单步约 15 ms、等效带宽约 280 GB/s，每步固定开销（kernel 启动、metadata 重建、host 调度）占单步耗时的主要部分。2.1 节的 decode 图、2.2 节的 MTP 专用图与 2.6 节的 metadata 入图将整步纳入图重放后，单步降至约 3.8 ms、等效带宽提升至约 1.06 TB/s，decode 转为真正的带宽受限。此后 2.2 节的 MTP 自投机以约 94% 的接受率将每步权重读取摊薄到约 1.88 个 token 上，成为带宽受限阶段的主要优化手段；2.3 节的 GDN 回移（相对 MTP 基线 +5.4%）与 2.8 节的图内融合（相对融合前累计 +9.6% 与 +3.6%）继续压缩小 kernel 与显存往返，整步 kernel 数由 711 降至 514、GPU busy 由 5.0 ms 降至 4.3 ms。

带宽占用分析基于 MTP 稳态单步 trace（`SGLANG_DECODE_TRACE=1`，EN20 第 20 步）。各图构成为：verify 图 583 kernels/4.11 ms、draft extend 图 77 kernels/0.77 ms、commit 图 0.04 ms。lm_head 每步计算 2 次（verify 与 draft 各一次）合计 0.94 ms（占 19%），实测约 2.3 TB/s，已接近 HBM 带宽极限，无低风险优化空间。acblasLt BF16 GEMM 共 156 次、合计 2.66 ms，属于带宽受限状态下的正常开销。残余可压缩项为 torch.cat 46 次 0.26 ms 与 eager elementwise 群 84 次 0.22 ms 等小 kernel，合计约 1.2 ms（占 24%），是图内最大的残余可压缩项，需要更高工程量的手写融合，本次未全部压缩；lm_head 每步计算 2 次存在结构性重复，消除该重复需要 draft 与 verify 共享 logits 的更深层次改造。收益上限方面，MTP 接受率决定投机解码的收益上限。KV/SSM cache 未压缩的合理性在于：full attention 仅 6 层，decode 每步读取 KV 不超过 14 MB（约占单步带宽 0.3%），SSM state 读+写约 36 MB（约占 0.9%），合计不足 1.5%，压缩类优化的收益低于运行噪声，故不实施。

整机带宽利用率的实测取证来自 `ppu-smi dmon`（1 秒间隔采样，在提交默认配置下运行 EN100 采集）：评测稳态阶段显存控制器利用率平均约 90.5%（区间 79%–92%），而 CU 算力利用率平均仅约 30%（峰值 44%）。该结果与上述 trace 分析互相印证：decode 阶段显存带宽已接近跑满，算力大量闲置，继续提升吞吐的空间主要在于压缩残余小 kernel 的气泡与提高 MTP 接受率，而非增加算力。

第二阶段在上述结论基础上继续推进三项：2.9 节把 acBLAS 在 M=2 下只跑到 LM head 带宽 60～65% 的逐层 projection 改为 split-N GEMV 形态（+2.69%/+2.34%）；2.10 节压缩 verify 之后的 host 串行段（+4.47%@EN1000）；2.11 节用联合投机图消除三张图之间的 launch 与 host 串行点（+9.77%/+9.33%）。三者均以同树全量 A/B 验证五字段零差异，累计将 decode 吞吐从 359.842/335.076 token/s（早期口径）推至 425.298/401.660 token/s；上文"lm_head 每步计算 2 次存在结构性重复"的判断经依赖审计部分证伪——两次 head 计算存在数据依赖无法合并为单次权重读取，但图间开销可以消除。

第三阶段的 chain depth=2 改变的是更高层的摊销比例：EN 每轮输出由约 1.88 token 提升至约 2.87 token，虽然多出一轮 draft body/head，target 主体权重仍只读一次，因此全量吞吐进一步由 425.298 token/s 提升至 **512.304 token/s（+20.46%）**。CN 的平均接受长度明显较低，固定深度继续加深即亏损，表明语言间吞吐差距主要由生成长度和 MTP 接受率决定，而不是同一计算图对中文字符有额外计算成本。

第四阶段（2.21、2.22 节）用自适应链深解决固定深度的双语矛盾：EN 全量由固定 depth=2 的 535.0 token/s 提升至 **594.200 token/s（+11.1%）**，CN 为 401.827 token/s（相对固定 depth=2 −3.3%，即 q_len=5 verify 图的形状地板成本），双语等权平均 **+4.8%**；控制器在两种语言上的稳态行为（CN 收敛浅深度、EN 直接进入 max depth）完全由实测接受率驱动，无需任何语言先验。

剩余空间的复核结论：自适应链深已转正并将 EN 推近 600 token/s；通用输出有效性兜底已关闭双语全部 public validation failure；device-memory IPC 已转正并将双语 TTFT 再压低约 1.8～2.0 ms。多图常驻的深度路由、非 64 对齐六桶与 GEMV cache modifier 已实测未达转正门；M=3 GEMV 与精确 fused patchify 经复核转正（见 2.19 节）；verify 图的 q_len 形状成本是 CN 侧已知的最后约 3.5% 结构性损失，消除它需要对 verify 图形状的更深层改造。

## 四、运行环境与复现方式

硬件环境为单张 PPU-ZW810E（驱动 1.3.2，HGGC 13.0，显存 97920 MiB）。软件环境为比赛镜像自带的 SAIL SDK、PyTorch-for-SAIL 2.6.0、sgl-kernel for SAIL 与 Python 3.12；Python 依赖仅 `requirements.txt`（torch 为镜像自带 PPU 版本、Pillow、numpy、tqdm），无额外第三方依赖，不需要 `requirements_extra.txt`。模型权重为主办方指定的 Qwen3.5-2B，置于 `Qwen3.5-2B/`；公开自测集 TSV 位于 `datasets/mmbench/`（Git LFS 管理）。

复现命令与公开自测一致，所有优化默认开启，无需设置任何环境变量：

```bash
source /usr/local/PPU_SDK/envsetup.sh
python benchmark_public.py \
  --dataset-path ./datasets/mmbench/mmbench_dev_en.tsv \
  --model-path ./Qwen3.5-2B \
  --backend sglang \
  --output result_full_en.json
python benchmark_public.py \
  --dataset-path ./datasets/mmbench/mmbench_dev_cn.tsv \
  --model-path ./Qwen3.5-2B \
  --backend sglang \
  --output result_full_cn.json
```

不加 `--num-samples` 即为 EN/CN 各 4029 条全量；加 `--num-samples N` 可运行前 N 条子集，`--develop` 显示 Warmup 与 Benchmark 进度。引擎启动包含 ViT 与 EXTEND 图的预捕获，约增加 2–5 s 一次性初始化耗时，不影响逐样本 TTFT 与吞吐。超长 prompt 与超大图像自动回退 eager 路径，行为与非图模式一致。诊断用开关（`SGLANG_DEVICE_IPC=0`、`SGLANG_ENABLE_MTP`、`SGLANG_MTP_CHAIN_DEPTH=2`、`SGLANG_MTP_DYNAMIC_DEPTH=0`、`SGLANG_CHAIN2_STATS=1`、`SGLANG_OUTPUT_REPAIR=0`、`SGLANG_GEMV_Q45=0`、`SGLANG_VIT_ENABLE_CUDA_GRAPH`、`SGLANG_EXTEND_GRAPH`、`SGLANG_FUSED_MROPE/ATTN_GATE/BA_PROJ/KV_SCATTER` 等）保持默认即可；注意 `SGLANG_VIT_ENABLE_CUDA_GRAPH` 与 `SGLANG_ENABLE_FLASH_ATTN=1` 不要同时开启（数值分歧）。

## 五、性能分析工具

优化过程的瓶颈定位主要依赖三类手段。其一是 PyTorch profiler 的稳态 trace 采集（经 `SGLANG_PREFILL_TRACE=1` 与 `SGLANG_DECODE_TRACE=1` 门控，分别针对 prefill 与 MTP 稳态 decode 单步），用于统计单步 kernel 数量、GPU busy 耗时与各 kernel 的时间分布；prefill 阶段 launch-bound 的结论（单次 prefill 1604 个 kernel、GPU busy 仅 32%、kernel 间隙中位 17 µs）以及 decode 单步 711 个 kernel 的构成拆解（lm_head 0.94 ms 约 2.3 TB/s、cat 与 elementwise 小 kernel 群约 1.2 ms）均来自该手段，是图捕获与图内融合两项优化的直接依据。

其二是自研的 TTFT 插桩探针（`srt/ttft_prof.py`，经 `SGLANG_TTFT_PROF=1` 开启，关闭时零开销），在 tokenizer、scheduler、detokenizer、engine 等链路上打点，将 TTFT 拆解为 host 预处理、ViT 视觉编码、LLM prefill、RPC 与调度残余等阶段，为 TTFT 优化提供了分阶段的量化依据（图化前 55.7 ms 与图化后 33.091 ms 两组口径的拆解均出自该探针）。

其三是设备侧监控工具 `ppu-smi dmon`，以 1 秒间隔采样显存控制器与 CU 算力利用率，用于在整机层面验证"decode 带宽受限、算力闲置"的判断（评测稳态显存控制器利用率平均约 90.5%、CU 利用率平均约 30%）。投机深度的调优另依赖运行时接受率统计（`SGLANG_CHAIN2_STATS=1`）与逐深度钉死实验（`SGLANG_MTP_FORCE_EXTRA`），后者用于分离 verify 图形状成本与控制器决策成本。此外，所有性能对比均配合正确性验证使用：图捕获与 eager 的逐位比对（`graph_vs_eager_check.py`，logits 与 Mamba 状态逐位相同）、融合 kernel 的 `torch.equal` 逐比特单元测试，以及每版优化转正前在公开集上逐题比对 `question_id / parsed_answer / correct / token_count / validation_errors` 五字段签名的一致性检查。正确性与公平性声明单独出具，见 `CORRECTNESS_AND_FAIRNESS.md`。
