# Holmes 推理引擎 <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [1. 概述](#1-概述)
  - [1.1. Holmes SDK 简介](#11-holmes-sdk-简介)
  - [1.2. 使用方式](#12-使用方式)
  - [1.3. 关键组件](#13-关键组件)
  - [1.4. 核心技术优势](#14-核心技术优势)
- [2. 获取与安装](#2-获取与安装)
  - [2.1. 使用 Holmes 镜像](#21-使用-holmes-镜像)
  - [2.2. pip 安装 holmes](#22-pip-安装-holmes)
- [3. 快速入门](#3-快速入门)
  - [3.1. 环境配置](#31-环境配置)
  - [3.2. ResNet50 端到端示例](#32-resnet50-端到端示例)
  - [3.3. 进一步阅读](#33-进一步阅读)
- [4. Holmes-Frontend](#4-holmes-frontend)
  - [4.1. 概述](#41-概述)
  - [4.2. 安装](#42-安装)
  - [4.3. 命令行工具](#43-命令行工具)
  - [4.4. 支持的模型格式总结](#44-支持的模型格式总结)
- [5. Holmes-Compile](#5-holmes-compile)
  - [5.1. 概述](#51-概述)
  - [5.2. 基本用法和参数说明](#52-基本用法和参数说明)
  - [5.3. 辅助工具](#53-辅助工具)
  - [5.4. 完整编译流程示例](#54-完整编译流程示例)
- [6. Holmes-Runtime](#6-holmes-runtime)
  - [6.1. 概述](#61-概述)
  - [6.2. 安装](#62-安装)
  - [6.3. C++ 接口](#63-c-接口)
  - [6.4. 运行时特性](#64-运行时特性)
  - [6.5. 命令行工具](#65-命令行工具)



## 1. 概述

### 1.1. Holmes SDK 简介

Holmes SDK（命名取自 Sherlock Holmes）是面向平头哥真武 PPU 芯片的深度学习推理加速软件栈，支持对 PyTorch/TensorFlow/ONNX 等主流深度学习框架导出的模型进行解析、优化与高效部署。

Holmes 推理引擎以 MLIR（Multi-Level Intermediate Representation）作为统一的编译器基础设施，并基于开源项目 IREE 进行架构演进与深度定制开发。

### 1.2. 使用方式

使用 Holmes SDK 进行模型编译与部署，主要工作流程如下：

![component](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125003941/b5175dbf1b8418e2f710a14f7b91ca5b/workflow.png)

由框架导出的模型，首先经 Holmes Frontend 解析为 StableHLO MLIR 表示的高层计算图；随后由 Holmes Compiler 完成图优化、算子 lowering 与代码生成，产出可直接部署的模型 Engine；最终在生产环境中由 Holmes Runtime 加载模型 Engine 并执行高效推理。

### 1.3. 关键组件

- `Holmes Frontend`：负责从主流深度学习框架导入模型，解析其高层计算图并导出为 StableHLO MLIR。
- `Holmes Compiler`：负责模型编译优化全流程，涵盖计算图优化、算子融合、kernel 调优、代码生成、存算资源管理与执行调度，最终生成可直接部署的模型 Engine。
- `Holmes Runtime`：轻量级运行时模块，提供 C++/Python API，支持加载模型 engine 并在真武 PPU 上执行高效推理。

### 1.4. 核心技术优势

- 广泛的框架与算子支持：支持 PyTorch/TensorFlow/ONNX 等主流深度学习框架导出的模型格式，全面覆盖 CV、NLP、推荐等多领域模型的部署需求。
- Holmes Compiler 支持 dynamic shape 场景推理，单次编译即可覆盖多种输入尺寸，避免重复编译，降低部署与维护成本。
- 基于 MLIR 的渐进式 lowering 特性，实现多层次 IR 抽象与编译信息的高效复用，在确保高度可扩展性与模块化的同时，提升编译优化决策的准确性。下图展示了 Holmes Compiler 整体的编译路线：

![IR_lowering](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125002750/071fd043beb0511cfe949ac8e288b9ac/IR_lowering.png)

- 多面体编译调度：Holmes Compiler 使用自研的轻量级多面体调度器对循环进行分析和调度变换，实现自动循环融合、并行性提取与数据局部性优化，无需手工调优即可自动生成高性能循环调度。下图展示了基于 pluto 算法的多面体编译工作流：

![component](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125003499/7e5fef6755794901aebfb5f7fcacb37e/affine_poly.png)

- 基于仿射变换的自动代码生成：利用 affine 方言的精确依赖分析与多面体调度能力，对 kernel 执行高层变换，并逐步 lower 至硬件特化操作，最终映射到真武 PPU 硬件原语，充分发挥算子性能。下图展示了 kernel 变换的主要处理过程：

![affine_pipeline](https://thead-marketing-public.oss-cn-hangzhou.aliyuncs.com/1784125003123/10f3cf0a1e800dbe6a7b45a5dcd7bbe5/affine_pipeline.png)

比赛关联：Holmes 是 PPU 上官方推理链路，将 Qwen3.5-2B 经 Frontend→Compiler→Runtime 部署是最可能的官方评测路径；dynamic shape 单次编译特性对变长文本/图像输入的部署成本影响直接。

## 2. 获取与安装

### 2.1. 使用 Holmes 镜像

镜像下载网址：待发布。

### 2.2. pip 安装 holmes

pip 安装方法，源地址通过环境变量 `t_head_pip_source` 配置、Holmes 版本通过环境变量 `holmes_version` 配置（本文其它章节的 pip 命令均使用这两个变量）：

```bash
export t_head_pip_source="T-HEAD 发布源"
export holmes_version="Holmes 发布版本"

pip install holmes==${holmes_version} -i ${t_head_pip_source}
pip install holmes-frontend==${holmes_version} -i ${t_head_pip_source}
```

Holmes 制品列表：

| 模块名称 | 版本 |
| :------- | :--- |
| holmes | 待发布 |
| holmes-frontend | 待发布 |

注：`holmes` 包内含有 holmes runtime/compile 两个模块功能。

## 3. 快速入门

本章以 ResNet50 为例，介绍如何通过 **Holmes Pipeline**（`holmes-import-torch` + `holmes-compile`）将模型编译为 VMFB，并使用 **Holmes Runtime C++ API** 加载 VMFB 并完成端到端推理。

### 3.1. 环境配置

#### 3.1.1. 使用预编译的 docker

拉取 Holmes Docker image，启动 Docker container。

```bash
# RC 版本 docker
image_name=具体发布的 docker
container_name="holmes_0.10.0"

docker pull ${image_name}
docker run --privileged --name ${container_name} -it -d -e EXEC_BASH=1 -e HOST_PERMS="$(id -u):$(id -g)" --net=host -e EXEC_BASH=1 -w /root --pid=host ${image_name} /bin/bash
docker exec -it ${container_name} bash
```

#### 3.1.2. 采用 pip 安装 holmes

在真武 PPU Docker 内采用 pip 安装 Holmes。

```bash
export t_head_pip_source="T-HEAD 对外发布源"
export holmes_version="Holmes 发布版本"

pip install holmes_compiler==${holmes_version} -i ${t_head_pip_source}
pip install holmes_frontend==${holmes_version} -i ${t_head_pip_source}
```

以上 pip 包提供 **Holmes Pipeline**（模型导入与编译）能力。本章 3.3 的 C++ 推理示例还需获取 **Holmes Runtime C++ SDK（Native Package）**，获取方式与集成细节参见 [Holmes-Runtime](#6-holmes-runtime)。

### 3.2. ResNet50 端到端示例

整体流程，以 Torch 为例：

```text
                    holmes-import-torch
ResNet50 (Torch)  ─────────────────────▶  resnet50.mlir (StableHLO)
                                                    │
                                                    │ holmes-compile
                                                    ▼
                                              resnet50.vmfb
                                                    │
                                                    │ Runtime::deserializeEngine
                                                    ▼
                                    ExecutionContext::enqueue （Holmes Runtime C++ API）
```

#### 3.2.1. 导出 ResNet50 FX/ONNX 模型

```python
import torch
import torchvision

model = torchvision.models.resnet50(pretrained=True).eval()
example = torch.zeros(1, 3, 224, 224)

model_fx = torch.export.export(model, (example,))

# export FX format model
torch.export.save(model_fx, './resnet50.pt2')

# export ONNX model
torch.onnx.export(
    model,                  # model to export
    (example,),             # inputs of the model,
    "resnet50.onnx",        # filename of the ONNX model
    input_names=["input"],  # Rename inputs for the ONNX model
    dynamo=True             # True or False to select the exporter to use
)
```

#### 3.2.2. Holmes Pipeline 编译

**Step 1：Torch 模型转 StableHLO MLIR**

```bash
holmes-import-torch resnet50.pt2 -o resnet50.mlir
```

**Step 2：MLIR 编译为 VMFB**

```bash
holmes-compile resnet50.mlir -o resnet50.vmfb
```

#### 3.2.3. Holmes Runtime C++ API 推理示例

下面的示例使用 **Holmes Runtime C++ API** 加载 VMFB 并执行推理。其中**推理调度**（引擎反序列化、shape 推断、执行下发）由 Holmes Runtime 负责，而 **stream 与显存等资源**直接使用真武 PPU API（`hggcStreamCreate` / `hggcMalloc` / `hggcMemcpy`）创建与管理，逻辑清晰、易于集成到现有 PPU 部署环境。

Holmes Runtime 的核心对象只有三个：

- `Runtime`：运行时实例，负责设备初始化与引擎加载。
- `Engine`：由 VMFB 反序列化得到的模型，描述输入/输出张量信息。
- `ExecutionContext`：一次推理的执行上下文，负责 shape 绑定、地址绑定与执行下发。

```cpp
#include <cstdio>
#include <vector>

#include <hggc_runtime.h>
#include "iree/interfaces/runtime.h"

int main() {
  // 1. 初始化 Holmes Runtime（自动选择并绑定推理设备）
  holmes::Runtime runtime = holmes::createRuntime();

  // 2. 使用 PPU API 创建推理所用的 stream
  hggcStream_t stream;
  hggcStreamCreate(&stream);

  // 3. 反序列化编译产物 vmfb，得到 Engine（"forward" 为模型入口函数名）
  holmes::Engine engine = runtime.deserializeEngine("resnet50.vmfb", "forward");

  // 4. 创建 ExecutionContext，并绑定 stream 与优化配置（profile 0）
  holmes::ExecutionContext context = engine.createExecutionContext();
  context.setOptimizationProfileAsync(0, stream);

  // 5. 设置输入 shape，并由 Runtime 推断输出 shape
  const char* inputName = engine.getIOTensorNamePtr(0);
  const char* outputName = engine.getIOTensorNamePtr(1);

  holmes::Dims inputShape{4, {1, 3, 224, 224}};
  context.setInputShape(inputName, inputShape);

  std::vector<std::string> missing;
  if (context.inferShapes(1, missing)) {
    printf("input shape not specified: %s\n", missing[0].c_str());
    return 1;
  }
  holmes::Dims outputShape = context.getTensorShape(outputName);

  // 6. 计算张量元素个数（ResNet50：输入 1x3x224x224，输出 1x1000，均为 f32）
  auto numElements = [](const holmes::Dims& d) {
    int64_t n = 1;
    for (int i = 0; i < d.nbDims; ++i) n *= d.d[i];
    return n;
  };
  size_t inputBytes = numElements(inputShape) * sizeof(float);
  size_t outputBytes = numElements(outputShape) * sizeof(float);

  // 7. 使用 PPU API 分配显存，并拷入输入数据（此处以全 0 输入为例）
  void* dInput = nullptr;
  void* dOutput = nullptr;
  hggcMalloc(&dInput, inputBytes);
  hggcMalloc(&dOutput, outputBytes);

  std::vector<float> hInput(numElements(inputShape), 0.0f);
  hggcMemcpy(dInput, hInput.data(), inputBytes, hggcMemcpyHostToDevice);

  // 8. 绑定输入/输出显存地址
  //    （输出已由编译选项 --holmes-externalize-outputs=true 外置，由用户自行分配与绑定）
  context.setTensorAddress(inputName, dInput);
  context.setTensorAddress(outputName, dOutput);

  // 9. 下发推理到 stream 并同步等待完成
  context.enqueue(stream);
  hggcStreamSynchronize(stream);

  // 10. 将输出从显存拷回 host 并打印前 10 个结果
  std::vector<float> hOutput(numElements(outputShape));
  hggcMemcpy(hOutput.data(), dOutput, outputBytes, hggcMemcpyDeviceToHost);
  printf("holmes output[:10]:");
  for (int i = 0; i < 10; ++i) printf(" %.4f", hOutput[i]);
  printf("\n");

  // 11. 释放资源
  hggcFree(dInput);
  hggcFree(dOutput);
  hggcStreamDestroy(stream);
  return 0;
}
```

编译与链接：示例需要包含 Holmes Runtime C++ SDK 头文件并链接 Holmes Runtime 与真武 PPU 运行时库，完整的头文件/库路径、构建方式与更多 API 说明参见 [Holmes-Runtime](#6-holmes-runtime)。

#### 3.2.4. 运行结果

编译运行上述程序，得到类似如下输出（张量数值在不同硬件上略有差异属正常现象），即表示 **Holmes Pipeline + Holmes Runtime C++ API** 链路已打通。

```text
holmes output[:10]: -0.4471 0.3182 -1.3304 -1.5183 -0.6098 0.3264 -2.4833 -1.1193 -2.1276 -0.4156
```

### 3.3. 进一步阅读

- [Holmes-Frontend](#4-holmes-frontend)：`holmes-import-torch` / `holmes-import-onnx` / `holmes-import-tf` 用法详解。
- [Holmes-Compile](#5-holmes-compile)：`holmes-compile` 参数与编译流程。
- [Holmes-Runtime](#6-holmes-runtime)：Holmes Runtime C++ / Python API 列表、集成方式与执行模型说明。

比赛关联：这条 "导出 → holmes-import-* → holmes-compile → Runtime C++ 推理" 的链路可直接套用到 Qwen3.5-2B；显存与 stream 均走 hggc API，便于与比赛 wrapper 中的资源管理对接。

## 4. Holmes-Frontend

### 4.1. 概述

Holmes-Frontend 是 Holmes SDK 的前端转换工具集，负责将不同框架的模型转换为 MLIR 中间表示：

- **Torch 模型**（FX / TorchScript）→ StableHLO MLIR。
- **ONNX 模型** → Stablehlo MLIR。
- **TF SavedModel** → Stablehlo MLIR。

转换后的 MLIR 文件可以通过 `holmes-compile` 编译为 VMFB 格式进行推理。

### 4.2. 安装

通过 pip 安装：

```bash
export t_head_pip_source="T-HEAD 对外发布源"
export holmes_version="Holmes 发布版本"

pip install holmes_frontend==${holmes_version} -i ${t_head_pip_source}
```

### 4.3. 命令行工具

#### 4.3.1. holmes-import-torch

基于 torch-mlir 开发，增强了 Torch ATen op 和模型的覆盖度。支持 TorchScript 和 FX Graph 模型的导入。

**用法：**

```bash
holmes-import-torch <model_path> -o <output.mlir> [options]
```

注：TorchScript 模型需要 **-i** 参数输入 shape。

**参数说明：**

| 参数 | 说明 |
| :----- | :----- |
| `model_path` | Torch 模型路径（.pt2 / .pt） |
| `-o, --output` | 输出 MLIR 文件路径 |
| `-i, --input` | 输入 shape 信息，格式如 `1x3x224x224xf32`，多个输入用空格分隔 |
| `-n, --names` | 输入参数名称 |
| `--to-onnx` | 将模型转为 ONNX 格式 |
| `--print_ir` | 打印 MLIR（默认在所有 pass 之后打印） |

**示例：**

```bash
# FX 格式
holmes-import-torch resnet50.pt2 -o resnet50.mlir

# TorchScript 多输入模型
holmes-import-torch model.pt -o model.mlir -i 1x2xf32 2x3xi32
```

#### 4.3.2. holmes-import-onnx

基于 onnx-mlir 开发，增强了 ONNX op 和模型的覆盖度。

**用法：**

```bash
holmes-import-onnx <model.onnx> -o <output.mlir> [options]
```

**参数说明：**

| 参数 | 说明 |
| :----- | :----- |
| `model_path` | ONNX 模型路径（.onnx） |
| `-o, --output` | 输出 MLIR 文件路径 |
| `-i, --input` | 输入 shape 信息，格式如 `1x3x224x224xf32` |
| `-p, --plugin` | plugin 动态库路径（用于 Custom Op） |
| `--shape-inference` | 启用 shape inference |
| `--optimize-onnx` | 启用 shape inference 和 runtime 优化 |
| `--load-large-model` | 支持加载模型权重大于 2G 的 ONNX 模型 |
| `--disable-version-converter` | 禁用 opset version 转换 |
| `--target-version` | 目标 opset 版本 |

**动态 Shape 参数：**

| 参数 | 说明 |
| :----- | :----- |
| `--min-shapes` | 最小 shape，格式如 `func_name:{input_1:1x1,input_2:2x2}` |
| `--max-shapes` | 最大 shape |
| `--opt-shapes` | 最优 shape |
| `--dynamic-shape-symbol` | 动态 shape 符号，格式如 `forward:{0:{0:bs:2k}}{1:{0:bs}{2:2k}}` |

**示例：**

```bash
# 基本转换
holmes-import-onnx resnet50.onnx -o resnet50.mlir -i 1x3x224x224xf32

# 带 Custom Op Plugin
holmes-import-onnx model.onnx -o model.mlir -i 1x512x1024xf32 -p ./libgelu_plugins.so

# 权重大于 2G 的模型
holmes-import-onnx large_model.onnx -o model.mlir -i 1x3x224x224xf32 --load-large-model

# 动态 shape 编译
holmes-import-onnx model.onnx -o model.mlir \
    --min-shapes "forward:{input:1x3x224x224}" \
    --max-shapes "forward:{input:32x3x224x224}" \
    --opt-shapes "forward:{input:8x3x224x224}"
```

#### 4.3.3. holmes-import-tf

将 TensorFlow SavedModel/GraphDef 转换为 MLIR。

**用法：**

```bash
holmes-import-tf <saved_model_dir> [options] -o <output.mlir>
```

**参数说明：**

| 参数 | 说明 |
| :----- | :----- |
| `<saved_model_dir>` | SavedModel 目录路径 |
| `-o` | 输出 MLIR 文件路径 |
| `--tf-import-type` | 导入类型：`savedmodel_v2`、`savedmodel_v1`、`pbtxt`、`pb` |
| `--tf-savedmodel-exported-names` | 导出的函数名，逗号分隔 |
| `--tf-savedmodel-tags` | MetaGraphDef 的 tags |
| `--save-temp-tf-input=<path>` | 保存 TF pipeline 输入的中间文件 |

**GraphDef 格式专用参数：**

| 参数 | 说明 |
| :----- | :----- |
| `--tf-input-arrays` | 输入节点名，逗号分隔 |
| `--tf-input-dtypes` | 输入数据类型，如 `DT_FLOAT,DT_FLOAT` |
| `--tf-input-shapes` | 输入 shape，如 `1x224x224x3`，多个用 `:` 分隔 |
| `--tf-output-arrays` | 输出节点名 |

**示例：**

```bash
# SavedModel V1 转换
holmes-import-tf \
  ./saved_model \
  --tf-import-type=savedmodel_v1 \
  -o=./resnet50.linalg.mlir

# SavedModel V2 转换
holmes-import-tf \
  ./saved_model_v2 \
  --tf-import-type=savedmodel_v2 \
  -o=./model.mlir

# GraphDef (pb) 转换
holmes-import-tf \
  ./frozen_graph.pb \
  --tf-import-type=pb \
  --tf-input-arrays=input \
  --tf-input-dtypes=DT_FLOAT \
  --tf-input-shapes=1x224x224x3 \
  --tf-output-arrays=output \
  -o=./model.mlir
```

### 4.4. 支持的模型格式总结

| 源格式 | 工具 |
| :----- | :----- |
| TorchScript (.pt) | holmes-import-torch |
| FX Graph（.pt2） | holmes-import-torch |
| ONNX (.onnx) | holmes-import-onnx |
| TF SavedModel | holmes-import-tf |
| TF GraphDef (.pb/.pbtxt) | holmes-import-tf |

比赛关联：Qwen3.5-2B 属 PyTorch 模型，首选 `torch.export` 导出 `.pt2` 后走 `holmes-import-torch`；`--min/max/opt-shapes` 动态 shape 参数可用于覆盖比赛评测中不同 batch/序列长度，避免多次编译。

## 5. Holmes-Compile

### 5.1. 概述

Holmes-Compile 是 Holmes SDK 的后端编译工具，负责将 StableHLO 方言表示的高层计算图，通过图优化、算子融合、kernel 调优以及代码生成等优化手段，最终生成 Holmes Runtime 可直接加载的模型 Engine 产物。该工具基于 IREE 编译框架并针对真武 PPU 硬件进行了深度定制开发。

### 5.2. 基本用法和参数说明

```bash
holmes-compile <input.mlir> -o <output.vmfb> [options]
```

#### 5.2.1. 输入/输出参数

| 参数 | 说明 |
| :----- | :----- |
| `<input.mlir>` | 输入 MLIR 文件路径，或 `-` 表示从 stdin 读取输入 |
| `-o <output.vmfb>` | 输出 VMFB 文件路径 |

#### 5.2.2. IO/datatype 相关参数

| 参数 | 说明 |
| :----- | :----- |
| `--holmes-flow-demote-f32-to-f16` | 将所有 f32 计算降级为 f16 |
| `--holmes-externalize-outputs` | 将模型输出 tensor 显式外部化（常用于框架集成使用场景） |

### 5.3. 辅助工具

Holmes SDK 中还提供了以下相关命令行工具：

| 工具 | 说明 |
| :----- | :----- |
| `holmes-run-module` | 加载执行编译生成的 VMFB 文件 |
| `holmes-benchmark-module` | 对编译生成的 VMFB 文件进行性能 benchmark |
| `holmes-run-mlir` | 直接运行 MLIR 文件 |
| `holmes-opt` | MLIR pass 调试工具 |
| `holmes-dump-module` | 查看 VMFB 中的具体模块信息 |
| `holmes-check-module` | 测试验证 VMFB 执行结果 |

### 5.4. 完整编译流程示例

以 resnet50 为例，展示从 PyTorch 模型转换为 VMFB 并执行推理的完整流程：

```bash
# Step 1: 前端转换（Torch -> StableHLO MLIR）
holmes-import-torch resnet50.pt2 -o resnet50.mlir

# Step 2: 后端编译（StableHLO MLIR -> vmfb）
holmes-compile resnet50.mlir -o resnet50.vmfb

# Step 3: 执行推理
holmes-run-module --module_file=resnet50.vmfb --entry_function=forward --function_input=1x3x224x224xf32
```

比赛关联：`--holmes-flow-demote-f32-to-f16` 是无需改模型即可做的精度/速度权衡开关（半精度直接降显存、提吞吐）；`holmes-benchmark-module` 与 `holmes-check-module` 分别对应压测取证与精度保持验证。

## 6. Holmes-Runtime

### 6.1. 概述

Holmes-Runtime 是 Holmes SDK 的推理运行时，负责加载 `holmes-compile` 的编译产物 **VMFB** 并在 PPU 上高效执行推理。

#### 6.1.1. 核心对象

Runtime 由三个核心类层层派生：

| 对象 | 职责 |
| :--- | :--- |
| `Runtime` | 运行时实例：初始化设备并从 VMFB 反序列化 `Engine`（进程级，通常一个） |
| `Engine` | VMFB 反序列化得到的模型：描述 IO 张量的名称、类型、shape 与优化配置；可创建多个 `ExecutionContext` |
| `ExecutionContext` | 一次推理的上下文：持有 workspace 与 IO 绑定状态，负责 shape/地址绑定与执行下发；每路并发一个 |

#### 6.1.2. 关键概念

| 概念 | 说明 |
| :--- | :--- |
| IO 张量模式（`TensorIOMode`） | `kINPUT` 输入、`kOUTPUT` 输出、`kINOUTPUT` 外置输出（由用户绑定地址） |
| 动态 shape | 维度中 `-1` 表示动态，执行前通过 `setInputShape` 绑定实际值、`inferShapes` 推断输出；static shape 可跳过 |
| 优化配置（Profile） | Engine 可含多个按 shape 区间调优的 profile，通过 `setOptimizationProfileAsync` 选定；单 profile 用 `0` |
| 外置输出 | 编译时加 `--holmes-externalize-outputs=true`，输出转 `kINOUTPUT`，由用户分配显存并 `setTensorAddress` 绑定；未开启时输出由 Runtime 管理，经 `getOutputTensorAddress` 取回 |

#### 6.1.3. 使用流程

1. 创建 `Runtime` → 反序列化得到 `Engine` → 由 Engine 创建 `ExecutionContext`；
2. `setOptimizationProfileAsync` 选定 profile 并绑定 stream（单 profile 传 `0`）；
3. `setInputShape` + `inferShapes` 绑定输入、推断输出 shape（static shape 可跳过）；
4. `hggcMalloc` 分配显存并 `setTensorAddress` 绑定（输入与外置输出）；
5. `enqueue` 下发推理、`hggcStreamSynchronize` 同步；
6. 取回输出（`getOutputTensorAddress` / D2H）并 `hggcFree` 释放。

### 6.2. 安装

通过 pip 安装 Python 运行时：

```bash
export t_head_pip_source="T-HEAD 对外发布源"
pip install holmes==${holmes_version} -i ${t_head_pip_source}
```

### 6.3. C++ 接口

使用 C++ 接口，建议先熟悉 6.3.1 端到端用例，再按需回查 6.3.3 API 参考。

#### 6.3.1. 端到端用例

```cpp
#include <cstdio>
#include <string>
#include <vector>

#include <hggc_runtime.h>
#include "iree/interfaces/runtime.h"

int main() {
  // 1. 初始化 Runtime 与 PPU stream
  holmes::Runtime runtime = holmes::createRuntime();
  hggcStream_t stream;
  hggcStreamCreate(&stream);

  // 2. 加载引擎并创建执行上下文
  //    "forward" 为编译时确定的入口函数名，可用 engine.getAllFuncNames() 列出
  holmes::Engine engine = runtime.deserializeEngine("model.vmfb", "forward");
  holmes::ExecutionContext context = engine.createExecutionContext();
  //    profile 0 为默认优化配置；数量可用 engine.getNbOptimizationProfiles() 查询
  IREE_CHECK_OK(context.setOptimizationProfileAsync(0, stream));

  // 3. 绑定动态输入 shape（static shape 模型可跳过），并推断输出 shape
  //    Dims{nbDims, {d0, d1, ...}}：nbDims 为维度数，d[] 为各维长度
  IREE_CHECK_OK(context.setInputShape("input_0", holmes::Dims{4, {1, 3, 224, 224}}));
  std::vector<std::string> missing;
  if (context.inferShapes(1, missing)) {
    printf("missing input shape: %s\n", missing[0].c_str());
    return 1;
  }

  // 张量字节数 = 元素个数 × 单元素字节数（按真实 dtype 计算，勿硬编码 sizeof(float)）
  auto byteSize = [&](const char* name) -> size_t {
    holmes::Dims d = context.getTensorShape(name);
    int64_t n = 1;
    for (int i = 0; i < d.nbDims; ++i) n *= d.d[i];
    return (size_t)n * iree_hal_element_dense_byte_count(engine.getTensorDataType(name));
  };

  // 4. 为每个需绑定的 IO 张量分配显存并绑定地址（输入 / 外置输出）
  std::vector<void*> buffers;
  void* inputPtr = nullptr;
  for (int i = 0; i < engine.getNbIOTensors(); ++i) {
    const char* name = engine.getIOTensorNamePtr(i);
    // 非外置输出（kOUTPUT）由 Runtime 内部管理，执行后经 getOutputTensorAddress 取回
    if (engine.getTensorIOMode(name) == holmes::TensorIOMode::kOUTPUT) continue;
    void* ptr = nullptr;
    hggcMalloc(&ptr, byteSize(name));
    IREE_CHECK_OK(context.setTensorAddress(name, ptr));
    buffers.push_back(ptr);
    if (std::string(name) == "input_0") inputPtr = ptr;
  }

  // 5. 拷入输入数据（H2D，此处以全 0 输入为例），下发推理并同步
  std::vector<float> hInput(1 * 3 * 224 * 224, 0.0f);
  // 输入为 f32，故用 sizeof(float)；其他 dtype 请用 byteSize("input_0") 计算
  hggcMemcpy(inputPtr, hInput.data(), hInput.size() * sizeof(float), hggcMemcpyHostToDevice);
  IREE_CHECK_OK(context.enqueue(stream));
  hggcStreamSynchronize(stream);

  // 6. 取回输出（D2H）
  size_t outBytes = byteSize("output_0");
  const void* outDev = context.getOutputTensorAddress("output_0");
  std::vector<char> hOutput(outBytes);
  hggcMemcpy(hOutput.data(), outDev, outBytes, hggcMemcpyDeviceToHost);

  // 7. 释放资源
  for (void* p : buffers) hggcFree(p);
  hggcStreamDestroy(stream);
  return 0;
}
```

#### 6.3.2. 构建与链接

pip 安装后，头文件与动态库位于包目录下：

```text
$(python3 -c "import holmes.runtime; print(holmes.runtime.__path__[0])")/
├── include/       # 头文件（iree/interfaces/runtime.h 等）
└── lib/           # 动态库（libiree_holmes_runtime.so）
```

编译示例：

```bash
HOLMES_SDK=$(python3 -c "import holmes.runtime; print(holmes.runtime.__path__[0])")

g++ infer.cc -o infer -std=c++17 \
    -I${HOLMES_SDK}/include -I${PPU_SDK}/include \
    -L${HOLMES_SDK}/lib -liree_holmes_runtime \
    -L${PPU_SDK}/lib -lhggcrt
```

#### 6.3.3. API 参考

**关键类型**

| 类型 | 说明 |
| :--- | :--- |
| `holmes::Dims` | 张量维度描述，`nbDims` 为维数、`d[]` 为各维长度（`-1` 表示动态），如 `Dims{4, {1,3,224,224}}` |
| `iree_status_t` | 接口返回值，`IREE_CHECK_OK(expr)` 快速失败，`iree_status_is_ok(status)` 优雅处理 |
| `iree_hal_element_type_t` | 张量数据类型（f32 / f16 / bf16 / i8 …），通过 `iree_hal_element_dense_byte_count(type)` 换算字节数 |

**`holmes::Runtime`**

| 接口 | 说明 |
| :--- | :--- |
| `Runtime createRuntime(bool useStream = false)` | 创建 Runtime。`useStream` 选择执行载体：`false`（默认）Graph 模式，`true` Stream 模式（见 6.4.2） |
| `Engine deserializeEngine(std::string engineFile, std::string funcName, iree_file_read_flags_t readFlag = IREE_FILE_READ_FLAG_MMAP)` | 从 VMFB 文件反序列化引擎。`funcName` 为入口函数名；`readFlag` 默认 MMAP 读取，小内存/网络文件系统可改用 `IREE_FILE_READ_FLAG_PRELOAD` |
| `Engine deserializeEngine(void const* data, size_t size, std::string funcName)` | 从内存缓冲区反序列化引擎 |

**`holmes::Engine`**

| 接口 | 说明 |
| :--- | :--- |
| `ExecutionContext createExecutionContext()` | 创建执行上下文 |
| `int32_t getNbIOTensors() const` | IO 张量总数 |
| `int32_t getNbOptimizationProfiles() const` | 优化配置数量 |
| `std::string getIOTensorName(int32_t index) const` | 按索引获取 IO 张量名称 |
| `char const* getIOTensorNamePtr(int32_t index) const` | 同上，返回 C 字符串指针 |
| `TensorIOMode getTensorIOMode(char const* name) const` | 张量模式（输入/输出/外置输出） |
| `iree_hal_element_type_t getTensorDataType(char const* name) const` | 张量数据类型 |
| `Dims getTensorShape(char const* name) const` | 张量声明 shape（动态维度为 `-1`） |
| `std::vector<std::string> getAllFuncNames()` | 列出所有可调用的入口函数名 |

**`holmes::ExecutionContext`**

| 接口 | 说明 |
| :--- | :--- |
| `iree_status_t setOptimizationProfileAsync(int32_t profileIndex, void* stream)` | 选定优化配置并绑定执行 stream（异步执行） |
| `iree_status_t setOptimizationProfile(int32_t profileIndex)` | 选定优化配置 |
| `int32_t getOptimizationProfile() const` | 获取当前优化配置索引 |
| `iree_status_t setInputShape(char const* name, Dims const& dims)` | 绑定输入张量的具体 shape（动态 shape 场景） |
| `int32_t inferShapes(int32_t nbMaxNames, std::vector<std::string>& names)` | 根据输入 shape 推断输出 shape；返回未绑定的输入张量个数，`names` 回填其名称 |
| `Dims getTensorShape(char const* name) const` | 获取推断后的张量 shape |
| `iree_status_t setTensorAddress(char const* name, void const* data)` | 绑定输入 / 外置输出张量的显存地址 |
| `void const* getTensorAddress(char const* name) const` | 获取已绑定的张量显存地址 |
| `void const* getOutputTensorAddress(char const* name) const` | 获取输出张量显存地址（含 Runtime 内部管理的非外置输出） |
| `iree_status_t enqueue(void* stream)` | 将一次推理下发到指定 stream |

### 6.4. 运行时特性

#### 6.4.1. 并发与部署

单个 `ExecutionContext` 非线程安全（workspace 在多次推理间复用），同一 Context 的调用须串行化。如需并发推理，为每路创建独立的 `ExecutionContext`：

| 场景 | 方式 |
| :--- | :--- |
| 并发 / 高吞吐 | 每路推理各持一个独立 Context + 独立 stream，可真正并行执行 |
| 单路 / 显存受限 | 复用同一个 Context 串行推理 |

#### 6.4.2. 执行模式

Runtime 支持两种执行模式：

- **Graph 模式**（默认）：将整次推理录制为设备计算图并整体重放，kernel launch 开销低，适合 static shape 稳定负载。
- **Stream 模式**：在 stream 上逐条下发 kernel，更灵活，支持动态 shape。

通过 `createRuntime(useStream)` 设置：`false`（默认）为 Graph 模式，`true` 为 Stream 模式。

比赛关联：Graph 模式重放降低 kernel launch 开销，直接利好 TTFT；并发方案（每路独立 Context+stream）是吞吐压测的官方推荐姿势；注意 Context 非线程安全，压测代码必须按此约束设计。

### 6.5. 命令行工具

#### 6.5.1. holmes-run-module

运行一次推理，并可打印或保存输出，用于快速验证 vmfb。

**用法：**

```bash
holmes-run-module --module_file=<vmfb> --entry_function=<name> --function_input=<输入> [选项]
```

**参数：**

| 参数 | 说明 |
| :--- | :--- |
| `--module_file` | VMFB 文件路径（`-` 表示从 stdin 读取） |
| `--device` | 设备 / 驱动，如 `hggc` |
| `--entry_function` | 入口函数名，如 `forward` |
| `--function_input` | 输入张量，格式 `[shape]x[type][=值]`（如 `1x3x224x224xf32`）；多输入重复指定，也可用 `@file.npy` 提供数据 |
| `--active_optimization_profile` | 选用的优化配置索引（默认 `0`） |
| `--output` | 输出处理：留空忽略、`-` 打印到 stdout、`@out.npy` 写入 npy 文件；多输出可重复指定 |

**示例：**

```bash
holmes-run-module --device=hggc --module_file=model.vmfb \
    --entry_function=forward --function_input=1x3x224x224xf32
```

#### 6.5.2. holmes-benchmark-module

对模块做性能压测，测量吞吐与时延。

**用法：**

```bash
holmes-benchmark-module --module_file=<vmfb> --entry_function=<name> --function_input=<输入> [选项]
```

**参数：**

| 参数 | 说明 |
| :--- | :--- |
| `--module_file` | VMFB 文件路径（`-` 表示从 stdin 读取） |
| `--device` | 设备 / 驱动，如 `hggc` |
| `--entry_function` | 入口函数名，如 `forward` |
| `--function_input` | 输入张量，格式 `[shape]x[type][=值]`（如 `1x3x224x224xf32`）；多输入重复指定，也可用 `@file.npy` 提供数据 |
| `--active_optimization_profile` | 选用的优化配置索引（默认 `0`） |
| `--average` | 取平均的运行次数（默认 `10`） |
| `--threads` | 并发线程数（默认 `1`） |

**示例：**

```bash
holmes-benchmark-module --device=hggc --module_file=model.vmfb \
    --entry_function=forward --function_input=1x3x224x224xf32
```

比赛关联：`holmes-benchmark-module --threads` 提供官方吞吐/时延压测手段，可作为比赛提交前 TTFT 与吞吐量指标的取证工具；`holmes-check-module` 用于对比编译前后数值，验证精度保持。
