# 使用指南：Qwen3.5-2B 单卡 PPU 推理优化提交版

本目录为比赛提交版本，包含评测入口、选手 wrapper、推理引擎源码闭包与模型权重，开箱即可在单张 810E PPU 服务器上运行公开数据集自测。在统一评测条件下（单张 810E、单样本、固定 `Qwen3.5-2B` 权重、`benchmark_public.py` 入口），通过推理后端替换与图优化提升 TTFT 与 decode 吞吐，模型权重、评测接口与输出语义均未改动。

如有测试性能与报告自测性能有较大差距，或对代码有质疑，请联系项目组负责人（联系方式随提交单独提供）。

性能数据、优化点与分阶段分析详见技术报告：[docs/TECHNICAL_REPORT.md](docs/TECHNICAL_REPORT.md)；

正确性与公平性声明见 [docs/CORRECTNESS_AND_FAIRNESS.md](docs/CORRECTNESS_AND_FAIRNESS.md)。

## 环境要求

- 建议使用默认镜像 `ppu-training:2.0.0-pytorch2.6.0ray2.55.1sglang0.4.6.post1-ppu-py312-cu128-ubuntu24.04`。镜像仅提供 SAIL SDK、PyTorch-for-SAIL 等基础平台组件；运行时实际使用的推理引擎是本目录 `rapid_reasoning/` 内置的修改版 SGLang，不依赖镜像或环境中安装的 SGLang 包。
- 需要将 Qwen3.5-2B 权重放至 Qwen3.5-2B/ 文件夹中（权重不随仓库分发）。
- MMBench 公开自测 TSV 不随仓库分发，请从主办方渠道获取 `mmbench_dev_en.tsv` 与 `mmbench_dev_cn.tsv` 后放入 `datasets/mmbench/`。

## 目录内容

```text
benchmark_public.py       # 主办方评测入口（仅本地自测用改动，见声明文件）
evaluation_wrapper.py     # 选手 wrapper（接口契约不变）
Qwen3.5-2B/               # 主办方指定模型权重（BF16 原样加载，需自行放入）
datasets/mmbench/         # 公开自测数据目录（TSV 不随仓库分发，需自行放入）
rapid_reasoning/          # 推理引擎源码与已编译运行时闭包
runtime_manifest.json     # 代码闭包、平台 ABI 与哈希清单
submission_check.py       # 提交完整性与模块来源检查
requirements.txt          # 已验证的 Python 依赖锁
tests/                    # 本地 A/B 测试产物与逐题比对脚本（非评测必需）
docs/TECHNICAL_REPORT.md  # 技术报告（优化点、性能与分阶段分析）
docs/CORRECTNESS_AND_FAIRNESS.md # 正确性与公平性声明
```

## 快速开始

1. 运行提交完整性检查：

```bash
python submission_check.py
```

该脚本验证 `rapid_reasoning/` 内的 SGLang、`runtime_packages/sgl_kernel` 与 `runtime_packages/triton` 是否完整，并确认实际 import 未落到环境中的同名包。

2. 运行英文公开集自测：

```bash
python benchmark_public.py \
  --dataset-path ./datasets/mmbench/mmbench_dev_en.tsv \
  --model-path ./Qwen3.5-2B \
  --backend sglang \
  --output result_dev_en.json
```

3. 中文公开集将数据集路径换成 `./datasets/mmbench/mmbench_dev_cn.tsv` 即可。调试时可用 `--num-samples 20` 限定样本数；正式自测建议全量（各 4029 条有效样本）。

## 参考成绩

公开集全量自测（提交默认配置，不传任何调优环境变量）：

| 数据集         | 平均 TTFT | 平均 decode 吞吐 | 准确率 | public validation |
| -------------- | --------: | ---------------: | -----: | ----------------: |
| MMBench dev EN |   27.6 ms |        594 tok/s | 79.97% |              通过 |
| MMBench dev CN |   28.0 ms |        402 tok/s | 84.02% |              通过 |

对照主办方 Transformers 基准（EN 185.1 ms / 58.7 tok/s，CN 141.0 ms / 41.5 tok/s）：TTFT 降低约 85% / 80%，decode 吞吐约 10.1× / 9.7×，正确题数 +3 / −3，无实质准确率退化。
