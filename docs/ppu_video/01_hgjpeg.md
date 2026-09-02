# hgJPEG 与视频图像硬件加速 <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [1. 视频图像硬件加速概述](#1-视频图像硬件加速概述)
  - [1.1. 综述](#11-综述)
  - [1.2. 发布说明](#12-发布说明)
  - [1.3. 编译运行](#13-编译运行)
  - [1.4. 详细规格](#14-详细规格)
  - [1.5. 真武 PPU 特定功能说明](#15-真武-ppu-特定功能说明)
  - [1.6. 已知问题](#16-已知问题)
- [2. hgJPEG 编程指南](#2-hgjpeg-编程指南)
  - [2.1. 引言](#21-引言)
  - [2.2. JPEG 解码](#22-jpeg-解码)
  - [2.3. JPEG 编码](#23-jpeg-编码)
  - [2.4. JPEG 转码](#24-jpeg-转码)
  - [2.5. 已弃用的 API 列表](#25-已弃用的-api-列表)


本文涵盖真武 PPU 视频/图像硬件加速能力总览（视频编解码、JPEG 编解码、2D 图像后处理）以及 hgJPEG 硬件 JPEG 编解码库的完整编程指南。

## 1. 视频图像硬件加速概述

### 1.1. 综述

真武 PPU 上支持视频编解码、图像编解码和 2D 图像后处理的硬件加速，主要有以下模块：

- Video Codec SDK：提供 HGDEC（HeteroGeneous hardware-based video decode）和 HGENC（HeteroGeneous hardware-based video encode）的硬件视频编解码加速支持。
- hgJPEG（HeteroGeneous hardware-based JPEG）：提供 JPEG decode 和 JPEG encode 硬件加速支持。
- HGPP（HeteroGeneous 2D Image and Signal Processing Performance Primitives）：提供 2D 图像后处理的硬件加速支持。

支持真武 810E、真武 M890 等平台。

### 1.2. 发布说明

- v2.1 release：支持 video optimize mode。
- v2.0 release：
  - VideoDecoder 支持 async memory allocation/free 提升性能。
  - 修复有关 decode timeout and abort 的 false alarm。
- v1.7 release：
  - hgJPEG 支持 `device memory` 作为输入的 `bitstream`。
  - 修复有限色彩空间下 RGB 输出视频范围的问题。
  - 解码性能提升。
- v1.5 release：
  - support ffmpeg -crf option in one-pass encode。

### 1.3. 编译运行

Hg Video Samples 包括 HgVideo samples 和 HgJPEG samples，代码以 HgVideoSamples 压缩包形式打包发布。

#### 1.3.1. HgVideo samples

HgVideo samples 依赖于 ffmpeg 提供 demux 能力，所以需要预先安装 FFmpeg，可以直接安装开源版本的 FFmpeg。假设 ffmpeg 安装目录为 `FFMPEG_PATH`。

> **注意**：如果编译时不指定，默认为 `/usr/local` 目录，否则为指定目录。ffmpeg 的 lib、include、bin 内容会被拷贝到对应目录的 include、lib 和 bin 子目录中。

执行以下命令可以显示版本号：

```bash
pkg-config --modversion libavcodec
```

如果不显示版本号，可以尝试先设置环境变量：

```bash
export PKG_CONFIG_PATH=$FFMPEG_PATH/lib/pkgconfig:$PKG_CONFIG_PATH
```

然后再执行 `pkg-config` 指令试试。

指定 `PPU_PATH`：

```bash
export CMAKE_LIBRARY_PATH=${PPU_HOME}/lib64
```

这里 `PPU_HOME` 指向 T-Head SAIL SDK 目录下的 `PPU_SDK`。

**编译**：

```bash
cd HgVideoSamples
bash build.sh
```

该命令会编译 HgVideoSamples 下的所有 app，包括 HgJPEG samples。

**运行**：

```bash
# 解码，同时运行12个线程可以打满性能
./build/HgVideo/HgDecode/HgDecPerfApp/AppDecPerf -thread 12 -i 1920x1080_yuv420p_50fps_h264.mp4

# 编码，同时运行4个线程可以打满性能
./build/HgVideo/HgEncode/HgEncPerfApp/AppEncPerf -i crowd_run_1920x1088_nv12_8bit_50.0fps_n500.yuv -s 1920x1088 -if nv12 -fps 30  -preset p4 -gop 60 -rc cbr -bitrate 10000000 -codec h265 -thread 4
```

**说明**：

真武 810 有 12 个 `video decode core`（真武 810E 是 10 个，真武 M890 是 4 个），理论上 12 个线程可以达到最佳性能，继续增加线程可能会稍许提升性能，但不会有较大提升。

7 个以内的真武 PPU 进程可以达到理想性能，使用真武 PPU 的进程数量超过 7 个性能不再会提升。

真武 810 和真武 810E 有 4 个 `video encode core`（真武 M890 是 2 个），所以理论上 4 个线程可以达到最佳性能。

#### 1.3.2. HgJPEG samples

**编译**：解码在 HgJPEGDecoder 目录，编码在 HgJPEGEncoder 目录。

```bash
cd HgVideoSamples
bash build.sh
```

**运行**：

```bash
# 解码，假设jpeg图片集在1080P目录下，batch size是128
./build/HgJPEG/HgJPEGDecoder/HgJPEGDecoder -i 1080p/ -b 128

# 编码（sample实际是先解码再编码）
./build/HgJPEG/HgJPEGEncoder/HgJPEGEncoder -i input.jpg  -o output.jpg
```

**说明**：

真武 810 和真武 810E 有 4 个 jpeg encode core（真武 M890 有 2 个），所以理论上 4 个线程可以达到最佳性能；真武 810 和真武 810E 有 8 个 jpeg decode core（真武 M890 有 4 个），batch 模式会自动内部 enable 8 个线程以达到最佳性能。

### 1.4. 详细规格

#### 1.4.1. 视频解码

Codec 格式支持：

- HEVC (H.265) - ITU-T Rec. H.265 (04/2013), ISO/IEC 23008-2：
  - Main Profile, Level 5.1, High Tier
  - Main10 Profile, Level 5.1, High Tier
  - Main Still Profile
- VP9 - vp9-bitstream-specification-v0.6-20160331-draft：
  - Profile 0, 8-bit
  - Profile 2, 10-bit
- AVC (H.264) - ITU-T Rec. H.264 (03/2010) / ISO/IEC 14496-10：
  - Main Profile, levels 1 - 5.2
  - High Profile, levels 1 - 5.2
  - High 10 Profile, levels 1 - 5.2
  - Baseline Profile, levels 1 - 5.2
- AV1 Bitstream & Decoding Process Specification Version 1.0.0 with Errata 1：
  - Main Profile, Level 5.1
- AVS2

分辨率最高支持 8192x8192；性能最高到 FHD 192 streams。

#### 1.4.2. 视频编码

Codec 格式支持：

- AVC (H.264)：Spec Version 12: ISO/IEC 14496-10 / ITU-T Rec. H.264 (03/2010)
  - Baseline Profile, levels 1 – 5.2
  - Main Profile, levels 1 - 5.2
  - High Profile, levels 1 – 5.2
  - High 10 Profile, levels 1 - 5.2
- HEVC (H.265)：ITU-T Rec. H.265 (04/2013), ISO/IEC 23008-2
  - Main Profile, Level 5.1, High Tier
  - Main10 profile, Level 5.1, High Tier
  - Main Still Profile
- AV1 Bitstream Specification Version 1.0.0 with Errata 1
  - Main Profile, Level 5.1

其他特性：

- 分辨率最高支持 4K。
- 支持 RGB 格式的输入（converted to YUV420 via inlinePP）。
- 通过 inlinePP 支持 crop、scale、rotate。
- 性能最高到 HD 32 streams。

#### 1.4.3. JPEG 编解码

- 分辨率最高支持到 32Kx32K。
- 通过 inlinePP 支持 RGB 格式的输入和输出。
- 通过 inlinePP 支持 crop、scale、rotate。
- 解码性能最高到 UHD 1500 FPS / 1080P 5430 FPS。
- 编码性能最高到 UHD 400 FPS / 1080P 1500 FPS。

#### 1.4.4. 性能规格

|  | 真武 810 | 真武 810E | 真武 M890 |
| --- | --- | --- | --- |
| 视频解码 | FHD 192 streams | FHD 160 streams | FHD 64 streams |
| 视频编码 | FHD 32 streams | FHD 32 streams | FHD 16 streams |
| Jpeg 解码 | UHD 960FPS | UHD 960FPS | UHD 480FPS |

#### 1.4.5. 性能实测数据

以下数据的指标为 fps，测试流的分辨率为 4K。

|  | 真武 810 | 真武 810E | 真武 M890 |
| --- | --- | --- | --- |
| H264 Decode | 1733 | 1444 | 715 |
| H265 Decode | 2160 | 1799 | 870 |
| Jpeg Decode | 1354 | 1354 | 862 |
| H264 Encode | 366 | 366 | 193 |
| HEVC Encode | 409 | 409 | 208 |

### 1.5. 真武 PPU 特定功能说明

video optimize mode：真武 PPU 支持 video optimize mode，使能方法：

```bash
export VIDEO_MEMORY_OPTIMIZE=1
```

最佳预期：峰值真武 PPU `device memory` 占用下降 37%，性能下降 13%，实际具体的优化效果和码流格式有关。适用场景：需要极致增加 batch size，对性能不是特别敏感。

### 1.6. 已知问题

**视频解码**：

- 不支持 MPEG1、MPEG2、MPEG4、VC1、VP8 等 legacy 格式。

**视频编码**：

- 不支持 YUV444 12bits。

**JPEG**：

- 不支持 lossless。
- 不支持 JPEG2000。

**2D Image**：

- hgpp 只支持 Image Process 接口，不支持 Signal Process 接口。

比赛关联：VLM 推理中图像预处理（JPEG 解码 + resize/crop）是 TTFT 的组成部分，hgJPEG 的 8 个硬件解码核（1080P 最高 5430 FPS）可把图像解码从 Host CPU offload 到 PPU 专用硬件；`VIDEO_MEMORY_OPTIMIZE=1` 还能在批处理场景下压低峰值显存，腾给 KV cache。

## 2. hgJPEG 编程指南

### 2.1. 引言

#### 2.1.1. hgJPEG 解码器

HeteroGeneous hardware-based JPEG (hgJPEG) 库为深度学习和超大规模多媒体应用中常用的图像格式提供高性能、真武 PPU 加速的 JPEG 解码功能。该库提供单个和批量 JPEG 解码功能，可有效利用可用的真武 PPU 资源以获得最佳性能；并为用户提供管理解码所需内存分配的灵活性。

hgJPEG 库支持以下功能：使用 JPEG 图像数据流作为输入；从数据流中检索图像的宽度和高度，并使用此检索到的信息管理真武 PPU 内存分配和解码。提供了专用的 API 用于从原始 JPEG 图像数据流中检索图像信息。

> **注意**：在整个文档中，术语 "CPU" 和 "Host" 同义使用。同样，术语 "真武 PPU" 和 "Device" 同义使用。

hgJPEG 库支持以下功能：

**JPEG 选项：**

- 基线和渐进式 JPEG 解码/编码。
- 每像素 8 位。
- Huffman 位流解码。
- 最多 4 通道 JPEG 位流。
- 8 位和 16 位量化表。

**以下 3 个颜色通道 Y、Cb、Cr（Y、U、V）的色度子采样：**

- 4:4:4
- 4:2:2
- 4:2:0
- 4:4:0
- 4:1:1
- 4:1:0

**功能：**

- 单个和批量图像解码。
- 用于解码的灵活内存管理。
- 从 JPEG 位流中提取图像信息。
- 支持多种输出格式（YUV、RGB、BGR 等）。
- 硬件加速解码（在支持的真武 PPU 上）。

#### 2.1.2. hgJPEG 编码器

hgJPEG 库提供真武 PPU 加速的 JPEG 编码功能，支持将图像数据编码为 JPEG 格式。编码器支持多种输入格式和色度子采样选项。

#### 2.1.3. 线程安全性

hgJPEG 库设计为线程安全，允许多个线程并发使用。但是，某些对象（如库句柄和状态对象）需要在每个线程中单独创建和管理。

#### 2.1.4. 多真武 PPU 支持

hgJPEG 库支持在多真武 PPU 系统上使用。每个真武 PPU 需要单独的库句柄，并且内存分配需要针对每个真武 PPU 设备进行。

#### 2.1.5. 硬件加速

**硬件加速 JPEG 解码**在以下真武 PPU 架构上可用：

- 真武 810E
- 真武 810
- 真武 610E
- 真武 610
- 真武 M890

**支持硬件加速 JPEG 解码的平台：**

- Linux（x86_64、ARM64）

### 2.2. JPEG 解码

#### 2.2.1. 使用 JPEG 解码

hgJPEG 库提供单个图像解码和多个图像批量解码的功能。

##### 2.2.1.1. 单个图像解码

对于单个图像解码，您提供数据大小和指向文件数据的指针，解码后的图像将放置在输出缓冲区中。

要使用 hgJPEG 库，首先调用辅助函数进行初始化：

1. 使用以下辅助函数之一创建 hgJPEG 库句柄：
   - `hgjpegCreateSimple()`
   - `hgjpegCreateEx()`
2. 使用辅助函数 `hgjpegJpegStateCreate()` 创建 JPEG 状态。

**可用的辅助函数：**

```c
hgjpegStatus_t
hgjpegGetProperty(libraryPropertyType type, int *value);
[已弃用]

hgjpegStatus_t
hgjpegCreate(hgjpegBackend_t backend, hgjpegHandle_t *handle, hgjpeg_dev_allocator allocator);

hgjpegStatus_t
hgjpegCreateSimple(hgjpegHandle_t *handle);

hgjpegStatus_t
hgjpegCreateEx(hgjpegBackend_t backend, hgjpegDevAllocator_t *dev_allocator, hgjpegPinnedAllocator_t *pinned_allocator, unsigned int flags, hgjpegHandle_t *handle);

hgjpegStatus_t
hgjpegDestroy(hgjpegHandle_t handle);

hgjpegStatus_t
hgjpegJpegStateCreate(hgjpegHandle_t handle, hgjpegJpegState_t *jpeg_handle);

hgjpegStatus_t
hgjpegJpegStateDestroy(hgjpegJpegState_t handle);
```

其他辅助函数如 `hgjpegSet*()` 和 `hgjpegGet*()` 可用于在每个句柄的基础上配置库功能。

通过 `hgjpegGetImageInfo()` 函数从 JPEG 编码图像中检索宽度和高度信息：

```c
hgjpegStatus_t
hgjpegGetImageInfo(
    hgjpegHandle_t handle,
    const unsigned char *data,
    size_t length,
    int *nComponents,
    hgjpegChromaSubsampling_t *subsampling,
    int *widths,
    int *heights
);
```

您可以使用检索到的参数 `widths`、`heights` 和 `nComponents` 来计算输出缓冲区所需的大小，无论是单个解码的 JPEG 还是批量中的每个解码的 JPEG。

##### 2.2.1.2. 批量图像解码

批量解码允许同时解码多个 JPEG 图像，提高吞吐量。

```c
hgjpegStatus_t
hgjpegDecodeBatched(
    hgjpegHandle_t handle,
    hgjpegJpegState_t jpeg_handle,
    const unsigned char *const *data,
    const size_t *lengths,
    hgjpegImage_t *destinations,
    hgjpegOutputFormat_t output_format,
    hggcStream_t stream
);
```

比赛关联：`hgjpegDecodeBatched()` 是 VLM 图像预处理 offload 的核心入口——批量解码直接把 RGB/BGR 结果落在 device 显存中，省掉 Host 解码 + H2D 拷贝两段开销，可显著降低多图请求的 TTFT；batch 模式内部自动启用 8 线程打满 8 个 JPEG 解码核。

#### 2.2.2. 数据类型和枚举

##### 2.2.2.1. hgjpegStatus_t

API 返回类型，表示操作状态。

```c
typedef enum {
    HGJPEG_STATUS_SUCCESS = 0,
    HGJPEG_STATUS_NOT_INITIALIZED,
    HGJPEG_STATUS_INVALID_PARAMETER,
    HGJPEG_STATUS_BAD_JPEG,
    HGJPEG_STATUS_JPEG_NOT_SUPPORTED,
    HGJPEG_STATUS_ALLOCATOR_FAILURE,
    HGJPEG_STATUS_EXECUTION_FAILED,
    HGJPEG_STATUS_ARCH_MISMATCH,
    HGJPEG_STATUS_INTERNAL_ERROR
} hgjpegStatus_t;
```

##### 2.2.2.2. hgjpegBackend_t

后端类型枚举。

```c
typedef enum {
    HGJPEG_BACKEND_DEFAULT = 0,
    HGJPEG_BACKEND_HYBRID = 1,
    HGJPEG_BACKEND_PPU_HYBRID = 2,
    HGJPEG_BACKEND_CPU = 3,
    HGJPEG_BACKEND_LOSSLESS_JPEG = 4
} hgjpegBackend_t;
```

##### 2.2.2.3. hgjpegOutputFormat_t

输出格式枚举。

```c
typedef enum {
    HGJPEG_OUTPUT_Y = 0,
    HGJPEG_OUTPUT_YUV = 1,
    HGJPEG_OUTPUT_NV12 = 2,
    HGJPEG_OUTPUT_YUY2 = 3,
    HGJPEG_OUTPUT_RGB = 4,
    HGJPEG_OUTPUT_BGR = 5,
    HGJPEG_OUTPUT_RGBI = 6,
    HGJPEG_OUTPUT_BGRI = 7,
    HGJPEG_OUTPUT_UNCHANGED = 8,
    HGJPEG_OUTPUT_UNCHANGEDI_U16 = 9
} hgjpegOutputFormat_t;
```

##### 2.2.2.4. hgjpegChromaSubsampling_t

色度子采样枚举。

```c
typedef enum {
    HGJPEG_CSS_UNKNOWN = 0,
    HGJPEG_CSS_GRAY = 1,
    HGJPEG_CSS_420 = 2,
    HGJPEG_CSS_422 = 3,
    HGJPEG_CSS_440 = 4,
    HGJPEG_CSS_444 = 5,
    HGJPEG_CSS_411 = 6,
    HGJPEG_CSS_410 = 7
} hgjpegChromaSubsampling_t;
```

##### 2.2.2.5. hgjpegImage_t

图像结构体。

```c
typedef struct {
    unsigned char *channel[HGJPEG_MAX_COMPONENT];
    size_t pitch[HGJPEG_MAX_COMPONENT];
} hgjpegImage_t;
```

##### 2.2.2.6. hgjpeg 解码器句柄

```c
struct hgjpegJpegDecoder;
typedef struct hgjpegJpegDecoder *hgjpegJpegDecoder_t;
```

此解码器句柄存储中间解码器数据，在解码阶段之间共享。

##### 2.2.2.7. hgjpeg 主机固定内存分配器接口

```c
typedef int (*tPinnedMalloc)(void **, size_t, unsigned int flags);
typedef int (*tPinnedFree)(void *);

typedef struct {
    tPinnedMalloc pinned_malloc;
    tPinnedFree pinned_free;
} hgjpegPinnedAllocator_t;
```

##### 2.2.2.8. hgjpeg 扩展主机页锁定内存（host pinned memory）分配器接口

```c
typedef int (*tPinnedMallocV2)(void *ctx, void **ptr, size_t size, hggcStream_t stream);
typedef int (*tPinnedFreeV2)(void *ctx, void *ptr, size_t size, hggcStream_t stream);

typedef struct {
    tPinnedMallocV2 pinned_malloc;
    tPinnedFreeV2 pinned_free;
    void *pinned_ctx;
} hgjpegPinnedAllocatorV2_t;
```

##### 2.2.2.9. hgjpeg 设备内存（device memory）分配器接口

```c
typedef int (*tDeviceMalloc)(void **, size_t);
typedef int (*tDeviceFree)(void *);

typedef struct {
    tDeviceMalloc device_malloc;
    tDeviceFree device_free;
} hgjpegDevAllocator_t;
```

#### 2.2.3. API 参考

##### 2.2.3.1. 辅助 API

###### hgjpegGetProperty()

[已弃用] 获取库属性。

```c
hgjpegStatus_t
hgjpegGetProperty(libraryPropertyType type, int *value);
```

| 参数 | 输入/输出 | 内存 | 描述 |
|:------|:-----------:|:------:|:------|
| libraryPropertyType type | 输入 | 主机 | 属性类型 |
| int *value | 输出 | 主机 | 属性值 |

**返回值：** `hgjpegStatus_t` - 如 API 返回代码中指定的错误代码。

###### hgjpegCreate()

分配并初始化库句柄。

```c
hgjpegStatus_t
hgjpegCreate(hgjpegBackend_t backend, hgjpegDevAllocator_t *allocator, hgjpegHandle_t *handle);
```

| 参数 | 输入/输出 | 内存 | 描述 |
|:------|:-----------:|:------:|:------|
| hgjpegBackend_t backend | 输入 | 主机 | 后端参数 |
| hgjpegDevAllocator_t *allocator | 输入 | 主机 | 设备内存分配器。如果提供 NULL，则使用默认的 HGGC 运行时 `hgMalloc()` 和 `hgFree()` 函数 |
| hgjpegHandle_t *handle | 输入/输出 | 主机 | 库句柄 |

**返回值：** `hgjpegStatus_t` - 错误代码。

###### hgjpegCreateSimple()

分配并初始化库句柄，使用库选择的默认编解码器实现和默认内存分配器。

```c
hgjpegStatus_t
hgjpegCreateSimple(hgjpegHandle_t *handle);
```

| 参数 | 输入/输出 | 内存 | 描述 |
|:------|:-----------:|:------:|:------|
| hgjpegHandle_t *handle | 输入/输出 | 主机 | 库句柄 |

**返回值：** `hgjpegStatus_t` - 错误代码。

###### hgjpegCreateEx()

使用自定义分配器分配并初始化库句柄。

```c
hgjpegStatus_t
hgjpegCreateEx(
    hgjpegBackend_t backend,
    hgjpegDevAllocator_t *dev_allocator,
    hgjpegPinnedAllocator_t *pinned_allocator,
    unsigned int flags,
    hgjpegHandle_t *handle
);
```

| 参数 | 输入/输出 | 内存 | 描述 |
|:------|:-----------:|:------:|:------|
| hgjpegBackend_t backend | 输入 | 主机 | 后端类型 |
| hgjpegDevAllocator_t *dev_allocator | 输入 | 主机 | 设备内存分配器 |
| hgjpegPinnedAllocator_t *pinned_allocator | 输入 | 主机 | 主机固定内存分配器 |
| unsigned int flags | 输入 | 主机 | 标志位 |
| hgjpegHandle_t *handle | 输入/输出 | 主机 | 库句柄 |

**返回值：** `hgjpegStatus_t` - 错误代码。

###### hgjpegDestroy()

销毁库句柄。

```c
hgjpegStatus_t
hgjpegDestroy(hgjpegHandle_t handle);
```

| 参数 | 输入/输出 | 内存 | 描述 |
|:------|:-----------:|:------:|:------|
| hgjpegHandle_t handle | 输入 | 主机 | 库句柄 |

**返回值：** `hgjpegStatus_t` - 错误代码。

###### hgjpegJpegStateCreate()

创建 JPEG 状态句柄。

```c
hgjpegStatus_t
hgjpegJpegStateCreate(hgjpegHandle_t handle, hgjpegJpegState_t *jpeg_handle);
```

| 参数 | 输入/输出 | 内存 | 描述 |
|:------|:-----------:|:------:|:------|
| hgjpegHandle_t handle | 输入 | 主机 | 库句柄 |
| hgjpegJpegState_t *jpeg_handle | 输入/输出 | 主机 | JPEG 状态句柄 |

**返回值：** `hgjpegStatus_t` - 错误代码。

###### hgjpegJpegStateDestroy()

销毁 JPEG 状态句柄。

```c
hgjpegStatus_t
hgjpegJpegStateDestroy(hgjpegJpegState_t jpeg_handle);
```

| 参数 | 输入/输出 | 内存 | 描述 |
|:------|:-----------:|:------:|:------|
| hgjpegJpegState_t jpeg_handle | 输入 | 主机 | JPEG 状态句柄 |

**返回值：** `hgjpegStatus_t` - 错误代码。

###### hgjpegGetImageInfo()

从 JPEG 编码图像中检索图像信息。

```c
hgjpegStatus_t
hgjpegGetImageInfo(
    hgjpegHandle_t handle,
    const unsigned char *data,
    size_t length,
    int *nComponents,
    hgjpegChromaSubsampling_t *subsampling,
    int *widths,
    int *heights
);
```

| 参数 | 输入/输出 | 内存 | 描述 |
|:------|:-----------:|:------:|:------|
| hgjpegHandle_t handle | 输入 | 主机 | 库句柄 |
| const unsigned char *data | 输入 | 主机 | JPEG 数据指针 |
| size_t length | 输入 | 主机 | 数据长度 |
| int *nComponents | 输出 | 主机 | 组件数量 |
| hgjpegChromaSubsampling_t *subsampling | 输出 | 主机 | 色度子采样 |
| int *widths | 输出 | 主机 | 每个组件的宽度数组 |
| int *heights | 输出 | 主机 | 每个组件的高度数组 |

**返回值：** `hgjpegStatus_t` - 错误代码。

###### hgjpegDecode()

解码单个 JPEG 图像。

```c
hgjpegStatus_t
hgjpegDecode(
    hgjpegHandle_t handle,
    hgjpegJpegState_t jpeg_handle,
    const unsigned char *data,
    size_t length,
    hgjpegImage_t *destination,
    hgjpegOutputFormat_t output_format,
    hggcStream_t stream
);
```

| 参数 | 输入/输出 | 内存 | 描述 |
|:------|:-----------:|:------:|:------|
| hgjpegHandle_t handle | 输入 | 主机 | 库句柄 |
| hgjpegJpegState_t jpeg_handle | 输入 | 主机 | JPEG 状态句柄 |
| const unsigned char *data | 输入 | 主机 | JPEG 数据指针 |
| size_t length | 输入 | 主机 | 数据长度 |
| hgjpegImage_t *destination | 输出 | 设备 | 输出图像 |
| hgjpegOutputFormat_t output_format | 输入 | 主机 | 输出格式 |
| hggcStream_t stream | 输入 | 主机 | HGGC 流 |

**返回值：** `hgjpegStatus_t` - 错误代码。

###### hgjpegDecodeBatched()

批量解码多个 JPEG 图像。

```c
hgjpegStatus_t
hgjpegDecodeBatched(
    hgjpegHandle_t handle,
    hgjpegJpegState_t jpeg_handle,
    const unsigned char *const *data,
    const size_t *lengths,
    hgjpegImage_t *destinations,
    hgjpegOutputFormat_t output_format,
    hggcStream_t stream
);
```

| 参数 | 输入/输出 | 内存 | 描述 |
|:------|:-----------:|:------:|:------|
| hgjpegHandle_t handle | 输入 | 主机 | 库句柄 |
| hgjpegJpegState_t jpeg_handle | 输入 | 主机 | JPEG 状态句柄 |
| const unsigned char *const *data | 输入 | 主机 | JPEG 数据指针数组 |
| const size_t *lengths | 输入 | 主机 | 数据长度数组 |
| hgjpegImage_t *destinations | 输出 | 设备 | 输出图像数组 |
| hgjpegOutputFormat_t output_format | 输入 | 主机 | 输出格式 |
| hggcStream_t stream | 输入 | 主机 | HGGC 流 |

**返回值：** `hgjpegStatus_t` - 错误代码。

###### hgjpegJpegStreamCreate()

创建用于解析 JPEG 比特流的 jpeg_stream 句柄。

```c
hgjpegStatus_t
hgjpegJpegStreamCreate(hgjpegHandle_t handle, hgjpegJpegStream_t *jpeg_stream);
```

| 参数 | 输入/输出 | 内存 | 描述 |
|:------|:-----------:|:------:|:------|
| hgjpegHandle_t handle | 输入 | 主机 | 库句柄 |
| hgjpegJpegStream_t *jpeg_stream | 输入 | 主机 | 位流句柄 |

**返回值：** `hgjpegStatus_t` - 错误代码。

###### hgjpegJpegStreamDestroy()

销毁 jpeg_stream 结构。

```c
hgjpegStatus_t
hgjpegJpegStreamDestroy(hgjpegJpegStream_t *jpeg_stream);
```

| 参数 | 输入/输出 | 内存 | 描述 |
|:------|:-----------:|:------:|:------|
| hgjpegJpegStream_t *jpeg_stream | 输入 | 主机 | 位流句柄 |

**返回值：** `hgjpegStatus_t` - 错误代码。

###### hgjpegBufferPinnedCreate()

创建固定缓冲区句柄。

```c
hgjpegStatus_t
hgjpegBufferPinnedCreate(
    hgjpegHandle_t handle,
    hgjpegPinnedAllocator_t *allocator,
    hgjpegBufferPinned_t *buffer
);
```

| 参数 | 输入/输出 | 内存 | 描述 |
|:------|:-----------:|:------:|:------|
| hgjpegHandle_t handle | 输入 | 主机 | 库句柄 |
| hgjpegPinnedAllocator_t *allocator | 输入 | 主机 | 固定内存分配器 |
| hgjpegBufferPinned_t *buffer | 输入/输出 | 主机 | 缓冲区句柄 |

**返回值：** `hgjpegStatus_t` - 错误代码。

###### hgjpegBufferPinnedDestroy()

销毁固定缓冲区句柄。

```c
hgjpegStatus_t
hgjpegBufferPinnedDestroy(hgjpegBufferPinned_t buffer);
```

| 参数 | 输入/输出 | 内存 | 描述 |
|:------|:-----------:|:------:|:------|
| hgjpegBufferPinned_t buffer | 输入 | 主机 | 缓冲区句柄 |

**返回值：** `hgjpegStatus_t` - 错误代码。

###### hgjpegBufferDeviceCreate()

创建设备缓冲区句柄。

```c
hgjpegStatus_t
hgjpegBufferDeviceCreate(
    hgjpegHandle_t handle,
    hgjpegDevAllocator_t *allocator,
    hgjpegBufferDevice_t *buffer
);
```

| 参数 | 输入/输出 | 内存 | 描述 |
|:------|:-----------:|:------:|:------|
| hgjpegHandle_t handle | 输入 | 主机 | 库句柄 |
| hgjpegDevAllocator_t *allocator | 输入 | 主机 | 设备内存分配器 |
| hgjpegBufferDevice_t *buffer | 输入/输出 | 主机 | 缓冲区句柄 |

**返回值：** `hgjpegStatus_t` - 错误代码。

###### hgjpegBufferDeviceDestroy()

销毁设备缓冲区句柄。

```c
hgjpegStatus_t
hgjpegBufferDeviceDestroy(hgjpegBufferDevice_t buffer);
```

| 参数 | 输入/输出 | 内存 | 描述 |
|:------|:-----------:|:------:|:------|
| hgjpegBufferDevice_t buffer | 输入 | 主机 | 缓冲区句柄 |

**返回值：** `hgjpegStatus_t` - 错误代码。

###### hgjpegJpegStreamParse()

解析 JPEG 比特流。

```c
hgjpegStatus_t
hgjpegJpegStreamParse(
    hgjpegHandle_t handle,
    const unsigned char *data,
    size_t length,
    int copy_data,
    int preload,
    hgjpegJpegStream_t jpeg_stream
);
```

| 参数 | 输入/输出 | 内存 | 描述 |
|:------|:-----------:|:------:|:------|
| hgjpegHandle_t handle | 输入 | 主机 | 库句柄 |
| const unsigned char *data | 输入 | 主机 | JPEG 数据指针 |
| size_t length | 输入 | 主机 | 数据长度 |
| int copy_data | 输入 | 主机 | 是否复制数据 |
| int preload | 输入 | 主机 | 是否预加载 |
| hgjpegJpegStream_t jpeg_stream | 输入 | 主机 | 位流句柄 |

**返回值：** `hgjpegStatus_t` - 错误代码。

###### hgjpegJpegStreamGetFrameDimensions()

从 jpeg_stream 获取帧尺寸。

```c
hgjpegStatus_t
hgjpegJpegStreamGetFrameDimensions(
    hgjpegJpegStream_t jpeg_stream,
    int *widths,
    int *heights
);
```

| 参数 | 输入/输出 | 内存 | 描述 |
|:------|:-----------:|:------:|:------|
| hgjpegJpegStream_t jpeg_stream | 输入 | 主机 | 位流句柄 |
| int *widths | 输出 | 主机 | 宽度数组 |
| int *heights | 输出 | 主机 | 高度数组 |

**返回值：** `hgjpegStatus_t` - 错误代码。

###### hgjpegJpegStreamGetChromaSubsampling()

从 jpeg_stream 获取色度子采样。

```c
hgjpegStatus_t
hgjpegJpegStreamGetChromaSubsampling(
    hgjpegJpegStream_t jpeg_stream,
    hgjpegChromaSubsampling_t *chroma_subsampling
);
```

| 参数 | 输入/输出 | 内存 | 描述 |
|:------|:-----------:|:------:|:------|
| hgjpegJpegStream_t jpeg_stream | 输入 | 主机 | 位流句柄 |
| hgjpegChromaSubsampling_t *chroma_subsampling | 输出 | 主机 | 色度子采样 |

**返回值：** `hgjpegStatus_t` - 错误代码。

###### hgjpegJpegStreamGetJpegEncoding()

从 jpeg_stream 获取 JPEG 编码类型。

```c
hgjpegStatus_t
hgjpegJpegStreamGetJpegEncoding(
    hgjpegJpegStream_t jpeg_stream,
    hgjpegJpegEncoding_t *jpeg_encoding
);
```

| 参数 | 输入/输出 | 内存 | 描述 |
|:------|:-----------:|:------:|:------|
| hgjpegJpegStream_t jpeg_stream | 输入 | 主机 | 位流句柄 |
| hgjpegJpegEncoding_t *jpeg_encoding | 输出 | 主机 | JPEG 编码类型 |

**返回值：** `hgjpegStatus_t` - 错误代码。

##### 2.2.3.2. 解码参数 API

###### hgjpegDecodeParamsCreate()

创建解码参数句柄。

```c
hgjpegStatus_t
hgjpegDecodeParamsCreate(
    hgjpegHandle_t handle,
    hgjpegDecodeParams_t *decode_params
);
```

###### hgjpegDecodeParamsDestroy()

销毁解码参数句柄。

```c
hgjpegStatus_t
hgjpegDecodeParamsDestroy(hgjpegDecodeParams_t decode_params);
```

###### hgjpegDecodeParamsSetOutputFormat()

设置解码输出格式。

```c
hgjpegStatus_t
hgjpegDecodeParamsSetOutputFormat(
    hgjpegDecodeParams_t decode_params,
    hgjpegOutputFormat_t output_format
);
```

###### hgjpegDecodeParamsSetAllowCMYK()

设置是否允许 CMYK 输出。

```c
hgjpegStatus_t
hgjpegDecodeParamsSetAllowCMYK(
    hgjpegDecodeParams_t decode_params,
    int allow_cmyk
);
```

###### hgjpegDecodeParamsSetScaleFactor()

设置解码输出的缩放因子。

```c
hgjpegStatus_t
hgjpegDecodeParamsSetScaleFactor(
    hgjpegDecodeParams_t decode_params,
    hgjpegScaleFactor_t scale_factor
);
```

比赛关联：`hgjpegDecodeParamsSetScaleFactor()` 可在硬件解码阶段直接缩放输出——VLM 视觉编码器通常只需 448/336 等小分辨率输入，解码时一步降采样可省掉独立的 resize kernel，进一步压缩预处理耗时。

### 2.3. JPEG 编码

#### 2.3.1. 使用 JPEG 编码

hgJPEG 库提供真武 PPU 加速的 JPEG 编码功能。

##### 2.3.1.1. 初始化编码

1. 创建库句柄（使用 `hgjpegCreateEx()` 并指定 `HGJPEG_BACKEND_PPU_HYBRID`）。
2. 创建编码器状态：`hgjpegEncoderStateCreate()`。
3. 创建编码器参数：`hgjpegEncoderParamsCreate()`。
4. 创建位流：`hgjpegJpegStreamCreate()`。

##### 2.3.1.2. 编码图像

```c
hgjpegStatus_t
hgjpegEncode(
    hgjpegHandle_t handle,
    hgjpegEncoderState_t encoder_state,
    hgjpegEncoderParams_t encoder_params,
    const hgjpegImage_t *source,
    hgjpegJpegStream_t jpeg_stream,
    hggcStream_t stream
);
```

#### 2.3.2. 编码 API 参考

##### hgjpegEncoderStateCreate()

创建编码器状态句柄。

```c
hgjpegStatus_t
hgjpegEncoderStateCreate(
    hgjpegHandle_t handle,
    hgjpegEncoderState_t *encoder_state,
    hgjpegDevAllocator_t *allocator
);
```

##### hgjpegEncoderStateDestroy()

销毁编码器状态句柄。

```c
hgjpegStatus_t
hgjpegEncoderStateDestroy(hgjpegEncoderState_t encoder_state);
```

##### hgjpegEncoderParamsCreate()

创建编码器参数句柄。

```c
hgjpegStatus_t
hgjpegEncoderParamsCreate(
    hgjpegHandle_t handle,
    hgjpegEncoderParams_t *encoder_params
);
```

##### hgjpegEncoderParamsDestroy()

销毁编码器参数句柄。

```c
hgjpegStatus_t
hgjpegEncoderParamsDestroy(hgjpegEncoderParams_t encoder_params);
```

##### hgjpegEncoderParamsSetQuality()

设置编码质量。

```c
hgjpegStatus_t
hgjpegEncoderParamsSetQuality(
    hgjpegEncoderParams_t encoder_params,
    int quality,
    hgjpegChromaSubsampling_t chroma_subsampling
);
```

| 参数 | 输入/输出 | 内存 | 描述 |
|:------|:-----------:|:------:|:------|
| encoder_params | 输入/输出 | 主机 | 编码器参数句柄 |
| quality | 输入 | 主机 | 质量级别（1-100） |
| chroma_subsampling | 输入 | 主机 | 色度子采样 |

##### hgjpegEncoderParamsSetOptimizedHuffman()

设置是否使用优化的 Huffman 表。

```c
hgjpegStatus_t
hgjpegEncoderParamsSetOptimizedHuffman(
    hgjpegEncoderParams_t encoder_params,
    int optimized
);
```

##### hgjpegEncoderParamsSetEncodingSpeed()

设置编码速度级别。

```c
hgjpegStatus_t
hgjpegEncoderParamsSetEncodingSpeed(
    hgjpegEncoderParams_t encoder_params,
    int speed
);
```

##### hgjpegEncoderParamsSetRestartInterval()

设置重启间隔。

```c
hgjpegStatus_t
hgjpegEncoderParamsSetRestartInterval(
    hgjpegEncoderParams_t encoder_params,
    unsigned int restart_interval,
    hggcStream_t stream
);
```

#### 2.3.3. hgJPEG 编码器 API 参考

##### hgjpegEncodeImage()

编码单个图像。

```c
hgjpegStatus_t
hgjpegEncodeImage(
    hgjpegHandle_t handle,
    hgjpegEncoderState_t encoder_state,
    hgjpegEncoderParams_t encoder_params,
    const hgjpegImage_t *source,
    hgjpegChromaSubsampling_t chroma_subsampling,
    hgjpegJpegStream_t jpeg_stream,
    hggcStream_t stream
);
```

##### hgjpegJpegStreamWrite()

将编码后的数据写入比特流。

```c
hgjpegStatus_t
hgjpegJpegStreamWrite(
    hgjpegJpegStream_t jpeg_stream,
    unsigned char *data,
    size_t *length
);
```

### 2.4. JPEG 转码

#### 2.4.1. 使用 JPEG 转码

转码允许在不进行完全解码和重新编码的情况下修改 JPEG 图像。

转码操作：

- 旋转
- 裁剪
- 质量调整

```c
hgjpegStatus_t
hgjpegTranscode(
    hgjpegHandle_t handle,
    hgjpegJpegStream_t input_stream,
    hgjpegEncoderParams_t encoder_params,
    hgjpegJpegStream_t output_stream,
    hggcStream_t stream
);
```

### 2.5. 已弃用的 API 列表

以下 API 已被标记为弃用，不建议在新代码中使用：

```c
hgjpegStatus_t hgjpegEncoderParamsCopyHuffmanTables(
    hgjpegEncoderState_t encoder_state,
    hgjpegEncoderParams_t encode_params,
    hgjpegJpegStream_t jpeg_stream,
    hggcStream_t stream
);

hgjpegStatus_t hgjpegCreate(
    hgjpegBackend_t backend, 
    hgjpegHandle_t *handle, 
    hgjpeg_dev_allocator allocator
);
```
