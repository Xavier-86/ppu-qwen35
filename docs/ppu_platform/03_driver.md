# PPU 内核驱动安装与故障排查 <span style="float: right;"><a href="00_index.md">目录</a></span>

## 目录

- [内核驱动安装指南](#内核驱动安装指南)
  - [概述](#概述)
  - [下载与安装](#下载与安装)
  - [KMD 升级/安装常见错误处理和故障排查指南](#kmd-升级安装常见错误处理和故障排查指南)
- [XID 说明](#xid-说明)
- [PPU XID 定义（PPU001）](#ppu-xid-定义ppu001)
  - [简介](#简介)
  - [处理 Xid Error](#处理-xid-error)
  - [Xid Error 列表](#xid-error-列表)
  - [常见 XID Error](#常见-xid-error)
- [PPU XID 定义（PPU0015）](#ppu-xid-定义ppu0015)
  - [简介](#简介-1)
  - [处理 XID Error](#处理-xid-error-1)
  - [XID Error 列表](#xid-error-列表-1)
  - [常见 XID Error](#常见-xid-error-1)
- [ECC 处理流程](#ecc-处理流程)
  - [ECC 介绍](#ecc-介绍)
  - [ECC 发生监控](#ecc-发生监控)
  - [ECC 现场处理](#ecc-现场处理)



## 内核驱动安装指南

### 概述

本文主要介绍用户如何下载/安装 PPU 内核驱动。PPU 内核驱动采用 runfile 包的安装形式，runfile 包中包含了部分依赖 linux 内核的源文件，需要在用户本地环境中进行编译之后再进行安装，因此可适配常用的 ubuntu、centos、alios、alinux 等系统以及不同的 Linux 内核版本。

### 下载与安装

> **注意（关于驱动安装包获取）**
>
> 驱动安装包正在准备中，将于近期在官网开放下载。安装包发布后，即可从官网获取对应版本（`ppu-driver-xxx.run`，其中 xxx 代表驱动的版本号），再按下述步骤在本地编译并安装。

> 本步骤以 KMD v2.1.1 版本为例

#### 内核驱动安装

> 内核驱动安装需要用户账号为 root 或者具有 sudo 权限。

**安装前提条件：**

runfile 包会在本地编译内核模块后再安装，安装前请确认已满足以下条件：

- **root 或 sudo 权限**：安装过程需向 `/lib/modules`、`/usr`、`/etc` 等系统目录写入文件。
- **与当前内核匹配的内核头文件/devel 包**：编译需要 `/lib/modules/$(uname -r)/build` 目录存在。
    - Ubuntu/Debian：`apt install linux-headers-$(uname -r)`
    - CentOS/AliOS/Alinux（RHEL 系）：`yum install kernel-devel-$(uname -r) kernel-headers-$(uname -r)`
- **编译工具链**：`gcc`、`make`（建议与编译当前内核所用 gcc 版本一致）。
- **elfutils-libelf 开发包（推荐）**：用于内核 `CONFIG_STACK_VALIDATION`，否则编译时会打印相应告警。
    - Ubuntu/Debian：`apt install libelf-dev`
    - RHEL 系：`yum install elfutils-libelf-devel`
- **MLNX_OFED（可选，仅 RDMA peer memory 场景）**：`alixpu_peermem` peer memory 模块依赖 MLNX_OFED；未安装时该模块会缺少 `ib_register_peer_memory_client` / `ib_unregister_peer_memory_client` 符号（不影响主驱动 `alixpu` / `alipci`，仅影响 RDMA peer memory 功能）。

> 若内核 build 目录不在默认位置，可通过环境变量 `KERNELDIR` 指定，例如：`sudo KERNELDIR=/path/to/kernel/build ./ppu-driver-xxx.run`。

##### runfile

```bash
#举例
chmod +x ppu-driver-xxx.run
sudo ./ppu-driver-xxx.run
```

**结果判定：**

> 如果结果为 run succeed，说明安装成功。

```bash
#sudo ./ppu-driver-xxx.run
/tmp/kmd_setup/drm/alipci/pre_make.sh 2.1.1 rbd225061717
KERNELDIR=/lib/modules/4.18.0-15-generic/build /bin/sh conftest.sh /lib/modules/4.18.0-15-generic/build
#### conftest.h does not exist ####
'kallsyms_lookup_name is available'
'__mod_lruvec_page_state is not available'
'find_module is available'
'pci_enable_pcie_error_reporting is available'
make  -C /lib/modules/4.18.0-15-generic/build M=/tmp/kmd_setup/drm/alipci modules
make[1]: Entering directory '/usr/src/linux-headers-4.18.0-15-generic'
Makefile:970: "Cannot use CONFIG_STACK_VALIDATION=y, please install libelf-dev, libelf-devel or elfutils-libelf-devel"
  CC [M]  /tmp/kmd_setup/drm/alipci/alipci_drv.o
...
make[1]: Leaving directory '/usr/src/linux-headers-4.18.0-15-generic'
/tmp/kmd_setup/drm/make_ptg.sh VERSION=2.1.1 COMMIT_ID=rbd225061717 USEPTGBINARY=1 ICN=1 HBM_PHY=1 PALLADIUM=1
/tmp/kmd_setup/drm/pre_make.sh 2.1.1 rbd225061717
make  -C /lib/modules/4.18.0-15-generic/build M=/tmp/kmd_setup/drm modules
make[1]: Entering directory '/usr/src/linux-headers-4.18.0-15-generic'
Makefile:970: "Cannot use CONFIG_STACK_VALIDATION=y, please install libelf-dev, libelf-devel or elfutils-libelf-devel"
  CC [M]  /tmp/kmd_setup/drm/alixpu_bitmap.o
  CC [M]  /tmp/kmd_setup/drm/alixpu_stackdepot.o
...
make[1]: Leaving directory '/usr/src/linux-headers-4.18.0-15-generic'
Fri Apr 24 17:05:28 CST 2026 - [PPU-DRIVER][INFO] step: rmmod alixpu
rmmod alixpu
rmmod alipci
Fri Apr 24 17:05:28 CST 2026 - [PPU-DRIVER][INFO] step: depmod
Fri Apr 24 17:05:29 CST 2026 - [PPU-DRIVER][INFO] step: sync
Fri Apr 24 17:05:29 CST 2026 - [PPU-DRIVER][INFO] step: modprobe alixpu
insmod /lib/modules/4.18.0-15-generic/updates/alipci.ko
insmod /lib/modules/4.18.0-15-generic/updates/alixpu.ko
install succeed
```

##### dmesg 日志

runfile 包安装过程中的 dmesg 日志如下所示：

```text
[Fri Apr 24 07:32:45 2026] [alixpu] PPU0015 ppuid:15, target ppu:0, icl:0x19, mini_path:3
[Fri Apr 24 07:32:45 2026] [alixpu] PPU0015 ppuid:15, target ppu:1, icl:0x53, mini_path:4
[Fri Apr 24 07:32:45 2026] [alixpu] PPU0015 ppuid:15, target ppu:2, icl:0x41, mini_path:2
[Fri Apr 24 07:32:45 2026] [alixpu] PPU0015 ppuid:15, target ppu:3, icl:0x71, mini_path:4
[Fri Apr 24 07:32:45 2026] [alixpu] PPU0015 ppuid:15, target ppu:4, icl:0x48, mini_path:2
[Fri Apr 24 07:32:45 2026] [alixpu] PPU0015 ppuid:15, target ppu:5, icl:0x42, mini_path:2
[Fri Apr 24 07:32:45 2026] [alixpu] PPU0015 ppuid:15, target ppu:6, icl:0x40, mini_path:1
[Fri Apr 24 07:32:45 2026] [alixpu] PPU0015 ppuid:15, target ppu:7, icl:0x60, mini_path:2
[Fri Apr 24 07:32:45 2026] [alixpu] PPU0015 ppuid:15, target ppu:8, icl:0x13, mini_path:3
[Fri Apr 24 07:32:45 2026] [alixpu] PPU0015 ppuid:15, target ppu:9, icl:0x9, mini_path:2
[Fri Apr 24 07:32:45 2026] [alixpu] PPU0015 ppuid:15, target ppu:10, icl:0x21, mini_path:2
[Fri Apr 24 07:32:45 2026] [alixpu] PPU0015 ppuid:15, target ppu:11, icl:0x11, mini_path:2
[Fri Apr 24 07:32:45 2026] [alixpu] PPU0015 ppuid:15, target ppu:12, icl:0x6, mini_path:2
[Fri Apr 24 07:32:45 2026] [alixpu] PPU0015 ppuid:15, target ppu:13, icl:0x8, mini_path:1
[Fri Apr 24 07:32:45 2026] [alixpu] PPU0015 ppuid:15, target ppu:14, icl:0x20, mini_path:1
[Fri Apr 24 07:32:45 2026] [alixpu] PPU0015 ppuid:15, target ppu:15, icl:0x0, mini_path:0
[Fri Apr 24 07:32:46 2026] [alixpu] total 16 devices in ICN topo!
```

#### 版本确认

运行 ppu-smi 工具，会打印出对应的 PPU 信息，其中 Driver Version 是对应的 PPU 内核驱动版本信息，如下所示：

```bash
$ ppu-smi
Fri Apr 24 17:12:12 2026
+-------------------------------------------------------------------------------+
| PPU-SMI 1.17          Driver Version: 2.1.1-rbd225  HGGC Version: N/A         |
+---------------------------------+----------------------+----------------------+
| PPU  Name        Persistence M. | Bus-Id               | Volatile Uncorr. ECC |
| Fan  Temp  Perf   Pwr:Usage/Cap | Memory-Usage         | PPU-Util  Compute M. |
|                                 |                      |               MIG M. |
+=================================+======================+======================+
| 0  PPU-ZW810E        N/A        | 00000000:00:11.0     |                    0 |
| N/A  26C   N/A       57W / 400W | 2MiB / 98304MiB      |   0%        Default  |
|                                 |                      |             Disabled |
+---------------------------------+----------------------+----------------------+

+-------------------------------------------------------------------------------+
| Processes:                                                                    |
| PPU    GI   CI   PID      Type  Process name                       PPU Memory |
|        ID   ID                                                     Usage      |
+===============================================================================+
| No running processes found                                                    |
+-------------------------------------------------------------------------------+
```

比赛关联：复赛部署的第一步就是用 runfile 装好 KMD 并用 `ppu-smi` 确认 Driver Version；`KERNELDIR` 环境变量和 runfile 日志样例可用于快速判断安装是否成功。

### KMD 升级/安装常见错误处理和故障排查指南

本章节介绍在安装或升级 PPU 内核驱动（KMD）过程中可能遇到的常见问题及其解决方案。

#### PPU 设备占用导致安装驱动报错

**问题现象：**

在安装或升级驱动时，系统提示卸载失败或设备占用错误。典型错误输出如下：

```text
make[1]: Leaving directory '/usr/src/kernels/5.10.134-010.ali5000.pro.al8.x86_64'
modprobe: FATAL: Module alixpu is in use.
[PPU-DRIVER][ERROR] Error: rmmod alixpu failed, error_code: 1
install failed
```

**根因分析：**

该报错表示系统中仍有任务或进程正在使用 PPU 设备，导致驱动卸载失败。

**解决方案：**

在升级 PPU 驱动之前，必须确保系统中没有任何进程还在使用 PPU 设备。

1. 查看哪些进程正在使用 PPU：

```bash
sudo lsof /dev/alixpu
```

2. 推荐的处理方案：

```bash
# 杀掉占用 PPU设备的进程并重置
sudo kill -9 $(sudo lsof /dev/alixpu | awk 'NR!=1 {print $2}')
sudo ppu-smi -r

# 杀掉相关的监控和插件进程
sudo pkill -9 -f "pg-exporter|dcgm-exporter|ppu-device-plug"
```

3. 执行完上述命令后应立即更新驱动，否则这些进程可能会自动重启。

4. 确认安装版本：

```bash
dmesg | grep -n "XPU Driver Initialization with version"
```

#### 安装驱动报错 Failed to create /dev/alixpu mode

**问题现象：**

安装驱动时报错：`Failed to create /dev/alixpu mode, Init HGML error: driver is not loaded`

典型错误输出如下：

```bash
Alibaba Cloud Linux 3.2104 U10 (Pro Edition)
Kernel 5.10.134-010.ali5000.al8.x86_64 on an x86_64

[root@localhost ~]# ppu-smi
[ALINPU WARNING]: [../ppu_interface.cpp:654]Failed to open /dev/alixpu
init HGML error: driver is not loaded

[root@localhost ~]# modprobe alixup
modprobe: FATAL: Module alixup not found in directory /lib/modules/5.10.134-010.ali5000.al8.x86_64
```

**解决方案：**

1. 解压驱动包，找到 `updates` 目录：

```bash
[root@localhost updates]# pwd
/lib/modules/5.10.134-010.ali5000.al8.x86_64/updates
[root@localhost updates]# ll
total 3492
-rwxr-xr-x 1 root root   52976 Feb 11 11:47 alipci.ko
-rwxr-xr-x 1 root root 3501080 Feb 11 11:47 alixpu.ko
-rwxr-xr-x 1 root root  177704 Feb 11 11:47 alixpu_peermem.ko
```

2. 进入 `updates` 目录，手动加载内核模块：

```bash
insmod alipci.ko
insmod alixpu.ko
insmod alixpu_peermem.ko
```

**原因分析：**

通常安装驱动的步骤是先将三个 `.ko` 文件解压到指定目录，然后执行 `depmod` 让系统可以找到这些模块，最后通过 `modprobe alixpu` 让系统自动加载。如果系统找不到模块，可能与重命名文件夹或 `depmod` 执行失败有关。此时手动到目录下加载模块是可行的解决方案。如需进一步排查，需要检查系统为何无法自动找到模块。

#### vfio-pci 占用 PPU 设备

**问题现象：**

按照上节的方法仍然无法安装驱动，可能是 PPU 设备被 vfio-pci 驱动占用。

**诊断步骤：**

1. 查询 PPU 设备状态：

```bash
lspci | grep -i ali | grep 3D
```

输出示例：

```text
0000:08:00.0 3D controller: Alibaba (China) Co., Ltd. Device 6001 (rev 01)
0000:09:00.0 3D controller: Alibaba (China) Co., Ltd. Device 6001 (rev 01)
...
```

2. 检查设备的 driver_override 设置：

```bash
cat /sys/bus/pci/devices/0001\:c9\:00.0/driver_override
```

如果输出为 `vfio-pci`，表示设备已被其他应用（如 runD 容器）占用。

**正常状态：**

正常的 PPU 设备 driver_override 应该设置为 `(null)`：

```bash
cat /sys/bus/pci/devices/0001\:c9\:00.0/driver_override
# 输出: (null)
```

**解决方案：**

批量清除 vfio-pci 占用：

```bash
# 查看所有PPU设备的driver_override状态
lspci | grep -i ali | grep 3D | awk '{print "/sys/bus/pci/devices/" $1 "/driver_override"}' | xargs -I {} cat {}

# 清除所有vfio-pci占用
lspci | grep -i ali | grep 3D | awk '{print "/sys/bus/pci/devices/" $1 "/driver_override"}' | xargs -I {} sh -c 'echo "" > {}'

# 验证清除结果
lspci | grep -i ali | grep 3D | awk '{print "/sys/bus/pci/devices/" $1 "/driver_override"}' | xargs -I {} cat {}
```

清除占用后，重新安装驱动。

> **注意事项**
>
> 如果系统中有 runD 容器正在运行，驱动可能已被 runD 使用，导致无法安装或升级驱动。需要先停止相关容器。
>
> 检查 runD 进程：
>
> ```bash
> [root@ppu810e-tcxehttm-0000 updates]# ps -aux | grep rund
> root     261539  1.9  0.0 3427896 147736 ?  Ssl  Jul17 785:13 /koordlet --addr=:8999 ... --collect-rund=true ...
> root     311901  0.0  0.0  19728  3236 ?    Ss   Aug01   0:00 bash /home/admin/device-plugins/bin/start-device-plugins ... --collect-rund=true ...
> ...
> root     3718493  0.0  0.0 221528  2412 pts/1 S+   10:23   0:00 grep --color=auto rund
> ```

#### 驱动版本重启后回退

**问题现象：**

PPU 驱动升级完成后显示新版本，但系统重启后驱动版本回退到旧版本。

**根因分析：**

在操作系统启动时，alixpu 模块的加载顺序如下：

1. 首先检查当前启动镜像 initramfs 内是否有 `alixpu.ko`，如果有，直接加载该模块。
2. 如果启动镜像里未找到，则根据 `/etc/modules-load.d/` 目录下所有 `.conf` 后缀的文件加载模块。如果安装了 KMD 安装包，该目录下会有一个 `alixpu.conf` 文件，告诉系统需要加载 alixpu，系统会去 `/lib/modules/$(uname -r)/` 目录下找到对应的模块加载。

目前 KMD 安装包只会将 `.ko` 文件放在 `/lib/modules/$(uname -r)/updates/` 目录下。因此，每次升级 KMD 后，在启动时加载的仍然是旧版本的 alixpu，原因是旧版本的 alixpu 在存在时被强制打包到了 initramfs 中。

当启动镜像被强制打包后，每次 boot 时总会加载旧的 alixpu 模块，表现为即使卸载掉系统中当前的 alixpu，重启时仍会加载旧版本。

**解决方案：**

1. 首先将系统内 alixpu 卸载干净（runfile 安装包通过专用的 `ppu-uninstall` 工具卸载）：

```bash
sudo ppu-uninstall
```

2. 解绑定系统中 alixpu 的依赖关系：

```bash
depmod
```

3. 强制重新打包启动镜像，此次打包会使用不包含 alixpu 的 initramfs 覆盖带 alixpu 的 initramfs：

```bash
dracut -f
```

4. 重启系统，然后即可正常安装 alixpu：

```bash
reboot
```

重启后，按照正常流程安装新版本的 KMD 驱动即可。

比赛关联：复赛服务器上跑压测/取数前，务必确认驱动安装干净、无残留进程占用（`lsof /dev/alixpu`）、无 vfio-pci/runD 抢占，否则 benchmark 会直接起不来或结果失真。

## XID 说明

XID 消息是 PPU 驱动上报的错误事件，用于帮助系统管理员、开发人员和 FAE 分析和定位 PPU 相关问题。不同产品在硬件模块和 XID 编码上存在差异，本手册按产品分别提供对应的 XID 说明：

- [PPU XID 定义（PPU001）](#ppu-xid-定义ppu001)：适用产品为真武 810、真武 810E、真武 805、真武 610、真武 610E，提供常见 XID Error 的详细解释与修复策略。
- [PPU XID 定义（PPU0015）](#ppu-xid-定义ppu0015)：适用产品为真武 M890，提供常见 XID Error 的详细解释与修复策略。

## PPU XID 定义（PPU001）

### 简介

本文档解释了什么是 Xid 消息，旨在帮助系统管理员、开发人员和 FAE 理解这些消息背后的含义，以帮助分析和解决 PPU 相关的问题。

#### 什么是 Xid 消息

Xid 消息是来自 PPU 驱动程序的错误报告，打印到操作系统的内核日志或事件日志中。Xid 消息指示发生了一般的 PPU 错误，最常见的原因是驱动程序对 PPU 编程不正确或发送到 PPU 的命令损坏。这些消息可能表示硬件问题、T-Head 软件问题或用户应用程序问题。

这些消息提供诊断信息，用户和 T-Head 都可以使用这些信息来帮助调试上报的问题。

每个消息的含义在不同的驱动程序版本中是一致的。

#### 如何使用 Xid 消息

Xid 消息旨在用作调试指南。因为许多问题可能有多个可能的根本原因，所以仅从 Xid 值来理解每个问题并不总是可行的。

例如，Xid Error 可能表示用户程序试图访问无效内存。但是，理论上，由于 PCIE 或帧缓冲区（"Frame Buffer[FB]"）问题导致的内存损坏可能会损坏任何驱动向硬件下发的命令，从而导致可以产生几乎任何错误。通常，以下列出的 Xid 分类应作为进一步调查每个问题的起点。

以下手册为调试 PPU 问题提供了额外的指导，包括解释 Xid 的建议，并为处理常见 Xid 的后续步骤提供了指导。

### 处理 Xid Error

#### 分析 Xid Error

下表列出了针对遇到的各种问题建议采取的措施。

| **问题** | **建议措施** |
| --- | --- |
| Suspected User Programming Issues | 运行调试工具。请参阅 memcheck 工具和 ppu-gdb 文档。 |
| Suspected Hardware Problems | 请联系硬件供应商。他们可以运行其硬件诊断过程。 |
| Suspected Driver Problems | 向 T-Head 提交错误报告，包括 ppu-bug-report.sh 命令的输出结果。有关收集附加信息以提供给 T-Head 以及常见 Xid 原因故障排除的指导，请参阅该文档。 |

### Xid Error 列表

下表列出了 Xid Error 以及每个错误的潜在原因。

| **XID** | **CLIENT_ID** | **EVENT_ID** | **故障** | **硬件错误** | **驱动错误** | **用户程序错误** | **系统内存损坏** | **总线错误** | **散热问题** | **FB 损坏** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 384 | CP=1 | 128 | invalid command |  | X |  | X | X |  | X |
| 385 |  | 129 | preempt_fail |  | X |  |  |  |  |  |
| 641 | CHUB=2 | 129 | invalid_pa |  | X | X |  |  |  |  |
| 642 |  | 130 | ecc_error | X |  |  |  |  | X |  |
| 643 |  | 131 | invalid_page |  | X | X |  |  |  | X |
| 644 |  | 132 | tlb_xnack |  | X | X |  |  |  |  |
| 896 | GD=3 | 128 | fatal_error |  | X | X |  |  |  | X |
| 1153 | L1=4 | 129 | invalid_pa |  | X | X |  |  |  |  |
| 1154 |  | 130 | ecc_error | X |  |  |  |  | X |  |
| 1155 |  | 131 | invalid_page |  | X | X |  |  |  | X |
| 1156 |  | 132 | tlb_xnack |  | X | X |  |  |  |  |
| 1664 | MMU=6 | 128 | invalid_page |  | X |  |  |  |  | X |
| 1665 |  | 129 | ecc_error_page | X |  |  |  |  | X |  |
| 1666 |  | 130 | invalid_va |  | X | X |  |  |  |  |
| 1667 |  | 131 | invalid_pa |  | X |  |  |  |  | X |
| 1920 | TLBV=7 | 128 | xnack |  | X | X |  |  |  | X |
| 1921 |  | 129 | invalid_page |  | X | X |  |  |  |  |
| 1922 |  | 130 | ecc_error_page | X |  |  |  |  | X |  |
| 1923 |  | 131 | invalid_pa |  | X |  |  |  |  | X |
| 2713 | PHUB=10 | 153 | err_icn_inst_inv_vppuid |  | X |  |  |  |  |  |
| 2712 |  | 152 | err_icn_cmd_inv_vppuid |  | X |  |  |  |  |  |
| 2711 |  | 151 | err_remote_store_rsp | X |  |  |  |  |  |  |
| 2710 |  | 150 | err_tlbp_c2ceg_invpa |  | X |  |  |  |  |  |
| 2709 |  | 149 | err_tlbp_c2cig_invpa |  | X |  |  |  |  |  |
| 2707 |  | 147 | err_icn_fence_invpa |  | X |  |  |  |  |  |
| 2706 |  | 146 | err_icn_fence_ecc | X |  |  |  |  | X |  |
| 2705 |  | 145 | err_tlbp_dmafs_invp_xnack |  | X |  |  |  |  |  |
| 2704 |  | 144 | fatal_icn_inst_nopath |  | X |  |  |  |  |  |
| 2703 |  | 143 | err_fb_req_to | X |  |  |  |  |  |  |
| 2702 |  | 142 | err_icn_req_to | X |  |  |  |  |  |  |
| 2701 |  | 141 | err_icn_local_fence_inv_pa |  | X |  |  |  |  |  |
| 2700 |  | 140 | err_icn_local_fence_ecc | X |  |  |  |  | X |  |
| 2698 |  | 138 | fatal_icn_rt_nopath |  | X |  |  |  |  |  |
| 2699 |  | 139 | err_icn_inv_cmd |  | X |  | X | X |  |  |
| 2697 |  | 137 | err_icn_inv_pa |  | X |  |  |  |  | X |
| 2696 |  | 136 | err_icn_ecc_data | X |  |  |  |  | X |  |
| 2695 |  | 135 | err_icn_dst_invpa |  | X |  |  |  |  |  |
| 2694 |  | 134 | err_icn_dst_mem | X |  |  |  |  |  |  |
| 2693 |  | 133 | err_tlbp_c2cig_xnack |  | X |  |  |  |  |  |
| 2692 |  | 132 | err_tlbp_c2cig_invalid_page |  | X |  |  |  |  |  |
| 2691 |  | 131 | err_tlbp_c2ceg_xnack |  | X |  |  |  |  |  |
| 2690 |  | 130 | err_tlbp_c2ceg_invalid_page |  | X |  |  |  |  |  |
| 2689 |  | 129 | err_tlbp_phub_xnack |  | X |  |  |  |  |  |
| 2688 |  | 128 | err_tlbp_phub_invalid_page |  | X |  |  |  |  |  |
| 2944 | REGFAB=11 | 128 | illegal register access |  | X |  |  |  |  |  |
| 2945 |  | 129 | read register timeout | X |  |  |  |  |  |  |
| 2946 |  | 130 | vf accessed during live migration |  | X |  |  |  |  |  |
| 2947 |  | 131 | driver programming error |  | X |  |  |  |  |  |
| 2948 |  | 132 | accessed reserved reg address |  | X |  |  |  |  |  |
| 4224 | SWITCH=16 | 128 | rt_nopath |  | X |  |  |  |  |  |
| 4225 |  | 129 | rt_lppath |  | X |  |  |  |  |  |
| 4226 |  | 130 | rx_port_en |  | X |  |  |  |  |  |
| 4227 |  | 131 | bm_overflow | X |  |  |  |  |  |  |
| 4480 | PRC=17 | 128 | icn_c2c_tx | X |  |  |  | X |  |  |
| 4481 |  | 129 | ppuid_disc_fail | X |  |  |  | X |  |  |
| 4996 | HBM=19 | 132 | PS0 1bit ecc error count over set threshold | X |  |  |  | X | X |  |
| 4997 |  | 133 | PS0 2-bit uncorrected ECC error detected | X |  |  |  | X | X |  |
| 5004 |  | 140 | PS1 1bit ecc error count over set threshold | X |  |  |  | X | X |  |
| 5005 |  | 141 | PS1 2-bit uncorrected ECC error detected | X |  |  |  | X | X |  |
| 5008 |  | 144 | AC parity error detected | X |  |  |  | X | X |  |
| 8576 | VCP=33 | 128 | invalid command |  | X |  | X | X |  | X |
| 8833 | VHUB=34 | 129 | vhub ECC error detected | X |  |  |  |  | X |  |
| 8834 |  | 130 | vhub invalid PA address | X |  |  |  | X |  |  |
| 8835 |  | 131 | vhub atomic error | X |  |  |  | X |  |  |
| 9088 | VSYNC=35 | 128 | vsync ip abnormal | X |  |  |  |  |  |  |
| 16257 | KERNEL=63 | 129 | device lost | X |  |  |  |  | X |  |
| 16256 |  | 128 | kill overtime |  | X | X |  |  |  |  |
| 16258 |  | 130 | launch abort |  | X | X |  |  |  |  |

### 常见 XID Error

本节提供了有关一些常见 Xid Error 的更多信息。

#### XID 384:8576: CP/VCP: Invalid CMD Error

收到该事件表明驱动程序代码故障。通常这可能是用户态驱动（umd）或者有小概率是内核态驱动（kmd）向硬件发送了非法命令。在某些情况下，它也可能是由系统内存不稳定引起的。

当记录到此事件时，T-Head 建议如下：

1. 使用 ppu-smi -r 进行复位操作。
2. 如果上述 1.未纠正错误，重新启动将解决此问题。

#### XID 9088: VSYNC: vsync ip abnormal

该事件由视频 IP 异常中断触发。通常有两个原因：

1. 超时中断：视频 IP 无法在指定时间内完成解码/编码/后处理，IP 将触发超时中断和内部复位。
2. 错误比特流：输入比特流有错误，视频解码会触发错误比特流中断，但会完成解码（尽量使错误隐藏起来）。

#### XID 4224: ICN-SWITCH: routine no path

当路由表中 dst ppu 条目的所有位都为 0 或 MinLink=0 时，会触发该事件。

#### XID 4225: ICN-SWITCH: routine loop path

当 dst ppu 等于 src ppu 时会触发该事件，这意味着：

- 路由表出错
- 将 local DMA copy 命令发送到了 ICN ring。

#### XID 4226: ICN-SWITCH: rx_port_en

当 rx_data 有效但 rx_port_en 为 0 时会触发该事件，这将丢弃数据包。

#### XID 2712, 2713: ICN-PHUB: err_icn_inst[cmd]_inv_vppuid

只有当 vppuid 无效（即 > 136）时才会触发该事件，可通过 instruction level 或 cmd level 触发。

- 2712：通过 cmd level 触发。
- 2713：通过 instruction level 触发。

#### XID 2695, 2697: ICN-PHUB: Invalid PA

只有当 pa 超出范围时才会触发该事件，这可能在 icn 命令 read/write/fence 访问 fabric 期间从 src/dst ppu 发生。

- 2695：发生于 dst ppu。
- 2697：发生于 src ppu。

#### XID 2688, 2689, 2690, 2691, 2692, 2693: ICN-PHUB

只有当页表 attribute 验证失败时才会触发该事件。

#### XID 2699: ICN-PHUB: Invalid Command

当 icn ring 收到无效的 cmd 时会触发该事件，可能是 FB 错误或驱动程序问题。

#### XID 2698, 2704: ICN-PHUB: routine table no path

例程表禁用时会触发该事件。

- 2698：通过 cmd level 触发。
- 2704：通过 instruction level 触发。

#### XID 2702, 2703: ICN-PHUB: request timeout

禁用与 MAC DB 的物理链接时，会触发该事件。

- 2702：通过 cmd level 触发。
- 2703：通过 instruction level 触发。

#### XID 2705: ICN-PHUB: tlbp dmafs xnack

当 DMA fence 没有页表项 pte 或检测到非法的物理地址 pa 时会触发该事件，在这种情况下，tlbp 将返回 xnack。

#### XID 2707: ICN-PHUB: icn fence invalid pa

对于 icn-fence 命令，从远端 PPU 上的 Fabric 返回非法 pa 错误时会触发该事件。

#### XID 2701: ICN-PHUB: icn local fence invalid pa

当 local fence 地址超出本地 hbm 范围或具有意外的 ppuid 时，会触发该事件。

#### XID 2709, 2710: ICN-PHUB: tlbp c2cig[c2ceg] invalid pa

该事件在以下情况下触发：

1. TLBP-C2CEG[C2CIG]转换后的物理地址中携带的 ppuid 不等于 src vppuid。
2. TLBP-C2CEG[C2CIG]转换后的 pte 中携带的 system bit 为 1。

#### XID 4480: ICN-PRC: icn c2c tx

当接收方没有响应请求时将触发该事件（重试 4 次后失败，默认重试 8 次，可配置）。

TxPPU 的 PRC 检测到此错误并引发异常。

#### XID 4481: ICN-PRC: ppuid discovery fail

当 ppuid 发现超时且未收到响应时，将触发该事件。

> PPUID 发现 Tx/Rx 超时并失败。CFG_ppuid 和 CFG_ppuid_vld 必须先由 SW 设置。切换 CFG_ppuid_disc_en 以再次触发发现数据包。这是在内核模式驱动程序加载期间完成的，如果尝试了几次但仍然发现失败，报告错误，硬件团队将对其进行诊断。

#### XID 4997, 5005: HBM: UECC

当发生 2 位不可校正 ECC 时将触发该事件，请注意，这同样会导致其他 source 模块报告 ECC 错误：如 642、1154、1665、1922...，但带有额外的错误信息。

#### XID 4996, 5004: HBM: CECC counter overflow

对于可纠正的 ECC（1bit），通常它已经被硬件纠正了，没有数据损坏，我们不会通过 Xid 报告这些信息。但是当发生太多 1bit ECC 时，一定是设备出了问题，需要做额外的硬件检测，在这种情况下，我们很可能会从 ps0/ps1 收到这 2 个 Xid。

#### XID 16256: KERNEL: Kill over time

进程 kill 失败主要是由于任务依赖关系不正确造成的。当收到此 id 时，需要进行设备复位（使用 ppu-smi -r）。

#### XID 16258: KERNEL: Launch abort

进程 kill 的过程当中驱动检测到多个进程上往硬件提交的任务间依赖有死锁的可能性，一般由 ICN 相关使用导致。内核驱动会主动让死锁关联进程对应的任务停止，并报该 Xid。

- 当仅收到此 id 时，只需重新拉起业务进程即可。
- 若收到此 id 后，并伴随有收到 XID 16256，则按照 Kill over time 的处理流程，进行设备复位（使用 ppu-smi -r）。

#### 其他 XID

该事件仅在硬件错误发生时触发，需要硬件团队调查问题。

#### XID 修复策略

| **类型** | **修复策略** | **XID** |
| --- | --- | --- |
| Invalid CMD | 设备复位（`ppu-smi -r`） | 384、2699、8576 |
| Kill 超时失败 | 设备复位（`ppu-smi -r`） | 16256 |
| ICN Link 错误 | 热重启（`os reboot`） | 4480、4481、4224、4225、4226、4227、2711、2702、2703 |
| ECC | 策略 1：退出所有用户进程，重新拉起业务即可（部分显存被屏蔽，用户可使用显存量变小）<br>策略 2：如多次发生 UECC，推荐做一次设备复位或热重启 | 642、1154、1665、1922、2706、2700、2696、4997、5005 |
| 掉卡 | 冷重启（BMC 下电重启） | 16257 |
| 其它 | 当前业务中断，无需修复，重新拉起业务即可 |  |

## PPU XID 定义（PPU0015）

### 简介

本文档解释了什么是 XID 消息，旨在帮助系统管理员、开发人员和 FAE 理解这些消息背后的含义，以帮助分析和解决 PPU 相关的问题。

#### 什么是 XID 消息

XID 消息是来自 PPU 驱动程序的错误报告，打印到操作系统的内核日志或事件日志中。XID 消息指示发生了一般的 PPU 错误，最常见的原因是驱动程序对 PPU 编程不正确或发送到 PPU 的命令损坏。这些消息可能表示硬件问题、T-Head 软件问题或用户应用程序问题。

这些消息提供诊断信息，用户和 T-Head 都可以使用这些信息来帮助调试上报的问题。

每个消息的含义在不同的驱动程序版本中是一致的。

#### 如何使用 XID 消息

XID 消息旨在用作调试指南。因为许多问题可能有多个可能的根本原因，所以仅从 XID 值来理解每个问题并不总是可行的。

例如，XID Error 可能表示用户程序试图访问无效内存。但是，理论上，由于 PCIE 或帧缓冲区（"Frame Buffer[FB]"）问题导致的内存损坏可能会损坏任何驱动向硬件下发的命令，从而导致可以产生几乎任何错误。通常，以下列出的 XID 分类应作为进一步调查每个问题的起点。

以下手册为调试 PPU 问题提供了额外的指导，包括解释 XID 的建议，并为处理常见 XID 的后续步骤提供了指导。

### 处理 XID Error

#### 分析 XID Error

下表列出了针对遇到的各种问题建议采取的措施。

| **问题** | **建议措施** |
| --- | --- |
| 疑似用户编程问题 | 运行调试工具。请参阅 `memcheck` 工具和 `ppu-gdb` 文档。 |
| 疑似硬件问题 | 请联系硬件供应商。他们可以运行其硬件诊断过程。 |
| 疑似驱动问题 | 向 T-Head 提交错误报告，包括 `ppu-bug-report.sh` 命令的输出结果。有关收集附加信息以提供给 T-Head 以及常见 XID 原因故障排除的指导，请参阅该文档。 |

### XID Error 列表

下表列出了 XID Error 以及每个错误的潜在原因。

| **XID** | **CLIENT_ID** | **EVENT_ID** | **故障** | **硬件错误** | **驱动错误** | **用户程序错误** | **系统内存损坏** | **总线错误** | **散热问题** | **FB 损坏** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 384 | CP=1 | 128 | invalid command |  | X |  | X | X |  | X |
| 385 |  | 129 | preempt_fail |  | X |  |  |  |  |  |
| 386 |  | 130 | icn_disabled_err | X | X |  |  |  |  |  |
| 641 | CHUB=2 | 129 | invalid_pa |  | X | X |  |  |  |  |
| 642 |  | 130 | ecc_error | X |  |  |  |  | X |  |
| 643 |  | 131 | invalid_page |  | X | X |  |  |  | X |
| 644 |  | 132 | tlb_xnack |  | X | X |  |  |  |  |
| 896 | GD=3 | 128 | fatal_error |  | X | X |  |  |  | X |
| 1153 | L1=4 | 129 | invalid_pa |  | X | X |  |  |  |  |
| 1154 |  | 130 | ecc_error | X |  |  |  |  | X |  |
| 1155 |  | 131 | invalid_page |  | X | X |  |  |  | X |
| 1156 |  | 132 | tlb_xnack |  | X | X |  |  |  |  |
| 1157 |  | 133 | icn_unreach_err | X | X |  |  |  |  |  |
| 1664 | MMU=6 | 128 | invalid_page |  | X |  |  |  |  | X |
| 1665 |  | 129 | ecc_error_page | X |  |  |  |  | X |  |
| 1666 |  | 130 | invalid_va |  | X | X |  |  |  |  |
| 1667 |  | 131 | invalid_pa |  | X |  |  |  |  | X |
| 1669 |  | 133 | invalid_page_normal |  | X | X |  |  |  | X |
| 1920 | TLBV=7 | 128 | xnack |  | X | X |  |  |  | X |
| 1921 |  | 129 | invalid_page |  | X | X |  |  |  |  |
| 1922 |  | 130 | ecc_error_page | X |  |  |  |  | X |  |
| 1923 |  | 131 | invalid_pa |  | X |  |  |  |  | X |
| 2944 | REGFAB=11 | 128 | illegal register access |  | X |  |  |  |  |  |
| 2945 |  | 129 | read register timeout | X |  |  |  |  |  |  |
| 2947 |  | 131 | driver programming error |  | X |  |  |  |  |  |
| 2948 |  | 132 | accessed reserved reg address |  | X |  |  |  |  |  |
| 3483 | PHUB=13 | 155 | err_req_unreach | X | X |  |  |  |  |  |
| 3482 |  | 154 | err_tbfence_cnt_out | X | X |  |  |  |  |  |
| 3481 |  | 153 | err_icn_inst_inv_vppuid |  | X |  |  |  |  |  |
| 3480 |  | 152 | err_icn_cmd_inv_vppuid |  | X |  |  |  |  |  |
| 3479 |  | 151 | err_remote_store_rsp | X |  |  |  |  |  |  |
| 3478 |  | 150 | err_tlbp_c2ceg_invpa |  | X |  |  |  |  |  |
| 3477 |  | 149 | err_tlbp_c2cig_invpa |  | X |  |  |  |  |  |
| 3473 |  | 145 | err_tlbp_dmafs_invp_xnack |  | X |  |  |  |  |  |
| 3472 |  | 144 | fatal_icn_inst_nopath |  | X |  |  |  |  |  |
| 3471 |  | 143 | err_fb_req_to | X |  |  |  |  |  |  |
| 3470 |  | 142 | err_icn_req_to | X |  |  |  |  |  |  |
| 3469 |  | 141 | err_icn_local_fence_inv_pa |  | X |  |  |  |  |  |
| 3468 |  | 140 | err_icn_local_fence_ecc | X |  |  |  |  | X |  |
| 3467 |  | 139 | err_icn_inv_cmd |  | X |  | X | X |  |  |
| 3466 |  | 138 | fatal_icn_rt_nopath |  | X |  |  |  |  |  |
| 3465 |  | 137 | err_icn_inv_pa |  | X |  |  |  |  | X |
| 3464 |  | 136 | err_icn_ecc_data | X |  |  |  |  | X |  |
| 3463 |  | 135 | err_icn_dst_invpa |  | X |  |  |  |  |  |
| 3462 |  | 134 | err_icn_dst_mem | X |  |  |  |  |  |  |
| 3461 |  | 133 | err_tlbp_c2cig_xnack |  | X |  |  |  |  |  |
| 3460 |  | 132 | err_tlbp_c2cig_invalid_page |  | X |  |  |  |  |  |
| 3459 |  | 131 | err_tlbp_c2ceg_xnack |  | X |  |  |  |  |  |
| 3458 |  | 130 | err_tlbp_c2ceg_invalid_page |  | X |  |  |  |  |  |
| 3457 |  | 129 | err_tlbp_phub_xnack |  | X |  |  |  |  |  |
| 3456 |  | 128 | err_tlbp_phub_invalid_page |  | X |  |  |  |  |  |
| 3712 | C2CDMA=14 | 128 | err_icn_atomic_invpa |  | X |  |  |  |  | X |
| 3713 |  | 129 | err_icn_atomic_ecc | X |  |  |  |  | X | X |
| 3714 |  | 130 | err_gid_atomic_invpa |  | X |  |  |  |  |  |
| 3715 |  | 131 | err_gid_atomic_ecc | X |  |  |  |  | X |  |
| 3716 |  | 132 | err_icn_fence_invpa |  | X |  |  |  |  |  |
| 3717 |  | 133 | err_icn_fence_ecc | X |  |  |  |  | X |  |
| 3718 |  | 134 | err_icn_fence_req_unreach |  | X |  |  |  |  |  |
| 3719 |  | 135 | err_icn_atomic_req_unreach |  | X |  |  |  |  |  |
| 3720 |  | 136 | err_gid_atomic_atmerr |  |  |  |  | X |  | X |
| 3968 | PKTE=15 | 128 | err_resp_req |  | X |  |  |  |  |  |
| 3969 |  | 129 | err_resp_ack |  | X |  |  |  |  |  |
| 3970 |  | 130 | err_resp_ud |  | X |  |  |  |  |  |
| 3971 |  | 131 | die_id_unmatch |  | X |  |  |  |  |  |
| 3972 |  | 132 | rcv_pkt_sts_err |  | X |  |  |  |  |  |
| 4224 | SWITCH=16 | 128 | rt_nopath |  | X |  |  |  |  |  |
| 4225 |  | 129 | rt_lppath |  | X |  |  |  |  |  |
| 4226 |  | 130 | rx_port_en |  | X |  |  |  |  |  |
| 4227 |  | 131 | bm_overflow | X |  |  |  |  |  |  |
| 4228 |  | 132 | dst_not_match |  | X |  |  |  |  |  |
| 4480 | PRC=17 | 128 | icn_c2c_tx | X |  |  |  | X |  |  |
| 4481 |  | 129 | ppuid_disc_fail | X |  |  |  | X |  |  |
| 4482 |  | 130 | prc_rxdrop_smp | X | X |  |  |  |  |  |
| 4996 | HBM=19 | 132 | PS0 1bit ecc error count over set threshold | X |  |  |  | X | X |  |
| 4997 |  | 133 | PS0 2-bit uncorrected ECC error detected | X |  |  |  | X | X |  |
| 5004 |  | 140 | PS1 1bit ecc error count over set threshold | X |  |  |  | X | X |  |
| 5005 |  | 141 | PS1 2-bit uncorrected ECC error detected | X |  |  |  | X | X |  |
| 5008 |  | 144 | AC parity error detected | X |  |  |  | X | X |  |
| 8576 | VCP=33 | 128 | invalid command |  | X |  | X | X |  | X |
| 8833 | VHUBPKTEB=34 | 129 | vhub ECC error detected | X |  |  |  |  | X |  |
| 8834 |  | 130 | vhub invalid PA address | X |  |  |  | X |  |  |
| 8835 |  | 131 | vhub atomic error | X |  |  |  | X |  |  |
| 9088 | VSYNC=35 | 128 | vsync ip abnormal | X | X | X |  |  |  |  |
| 16256 | KERNEL=63 | 128 | kill overtime |  | X | X |  |  |  |  |
| 16257 |  | 129 | device lost | X |  |  |  |  | X |  |
| 16258 |  | 130 | launch abort |  | X | X |  |  |  |  |
| 16259 |  | 131 | shared tlb invalidation timeout |  | X | X |  |  |  |  |

### 常见 XID Error

本节提供了有关一些常见 XID Error 的更多信息。

#### XID 384:8576: CP/VCP: Invalid CMD Error

收到该事件表明驱动程序代码故障。通常这可能是用户态驱动（umd）或者有小概率是内核态驱动（kmd）向硬件发送了非法命令。在某些情况下，它也可能是由系统内存不稳定引起的。

当记录到此事件时，T-Head 建议如下：

1. 使用 `ppu-smi -r` 进行复位操作。
2. 如果上述步骤 1 仍未纠正错误，重新启动将解决此问题。

#### XID 9088: VSYNC: vsync ip abnormal

该事件由视频 IP 异常中断触发。通常有三个原因：

1. 超时中断：视频 IP 无法在指定时间内完成解码/编码/后处理，IP 将触发超时中断和内部复位。
2. 错误比特流：输入比特流有错误，视频解码会触发错误比特流中断，但会完成解码（尽量使错误隐藏起来）。
3. 错误 vcmd 命令：主要是 vcmd 命令中的寄存器存在错误，主要是 video sdk 导致。

#### XID 4224: ICN-SWITCH: routine no path

当路由表中 dst ppu 条目的所有位都为 0 或 MinLink=0 时，会触发该事件。

#### XID 4225: ICN-SWITCH: routine loop path

当 dst ppu 等于 src ppu 时会触发该事件，这意味着：

- 路由表出错
- 将 local DMA copy 命令发送到了 ICN ring。

#### XID 4226: ICN-SWITCH: rx_port_en

当 rx_data 有效但 rx_port_en 为 0 时会触发该事件，这将丢弃数据包。

#### XID 3481, 3480: ICN-PHUB: err_icn_inst[cmd]_inv_vppuid

只有当 vppuid 无效（即 > 136）时才会触发该事件，可通过 instruction level 或 cmd level 触发。

- 3480：通过 cmd level 触发。
- 3481：通过 instruction level 触发。

#### XID 3463, 3465: ICN-PHUB: Invalid PA

只有当 pa 超出范围时才会触发该事件，这可能在 icn 命令 read/write/fence 访问 fabric 期间从 src/dst ppu 发生。

- 3463：发生于 dst ppu。
- 3465：发生于 src ppu。

#### XID 3456, 3457, 3458, 3459, 3460, 3461: ICN-PHUB

只有当页表 attribute 验证失败时才会触发该事件。

#### XID 3467: ICN-PHUB: Invalid Command

当 icn ring 收到无效的 cmd 时会触发该事件，可能是 FB 错误或驱动程序问题。

#### XID 3466, 3472: ICN-PHUB: routine table no path

routine table 禁用时会触发该事件。

- 3466：通过 cmd level 触发。
- 3472：通过 instruction level 触发。

#### XID 3470, 3471: ICN-PHUB: request timeout

禁用与 MAC DB 的物理链接时，会触发该事件。

- 3470：通过 cmd level 触发。
- 3471：通过 instruction level 触发。

#### XID 3473: ICN-PHUB: tlbp dmafs xnack

当 DMA fence 没有页表项 pte 或检测到非法的物理地址 pa 时会触发该事件，在这种情况下，tlbp 将返回 xnack。

#### XID 3716, 3712: ICN-C2CDMA: icn fence[atomic] invalid pa

对于 icn-fence/icn-atomic 命令，从远端 PPU 上的 Fabric 返回非法 pa 错误时会触发该事件。

#### XID 3717, 3713: ICN-C2CDMA: icn fence[atomic] ecc

对于 icn-fence/icn-atomic 命令，远端地址发生 UECC 时触发。

#### XID 3469: ICN-PHUB: icn local fence invalid pa

当 local fence 地址超出本地 hbm 范围或具有意外的 ppuid 时，会触发该事件。

#### XID 3477, 3478: ICN-PHUB: tlbp c2cig[c2ceg] invalid pa

该事件在以下情况下触发：

1. TLBP-C2CEG[C2CIG] 转换后的物理地址中携带的 ppuid 不等于 src vppuid。
2. TLBP-C2CEG[C2CIG] 转换后的 pte 中携带的 system bit 为 1。

#### XID 4480: ICN-PRC: icn c2c tx

当接收方没有响应请求时将触发该事件（重试 4 次后失败，默认重试 8 次，可配置）。

TxPPU 的 PRC 检测到此错误并引发异常。

#### XID 4481: ICN-PRC: ppuid discovery fail

当 ppuid 发现超时且未收到响应时，将触发该事件。

> ppuid 发现 Tx/Rx 超时并失败。CFG_ppuid 和 CFG_ppuid_vld 必须先由 SW 设置。切换 CFG_ppuid_disc_en 以再次触发发现数据包。这是在内核模式驱动程序加载期间完成的，如果尝试了几次但仍然发现失败，报告错误，硬件团队将对其进行诊断。

#### XID 4997, 5005: HBM: UECC

当发生 2 位不可校正 ECC 时将触发该事件，请注意，这同样会导致其他 source 模块报告 ECC 错误：如 642、1154、1665、1922...，但带有额外的错误信息。

#### XID 4996, 5004: HBM: CECC counter overflow

对于可纠正的 ECC（1bit），通常它已经被硬件纠正了，没有数据损坏，我们不会通过 XID 报告这些信息。但是当发生太多 1bit ECC 时，一定是设备出了问题，需要做额外的硬件检测，在这种情况下，我们很可能会从 ps0/ps1 收到这 2 个 XID。

#### XID 16256: KERNEL: Kill over time

进程 kill 失败主要是由于任务依赖关系不正确造成的。当收到此 id 时，需要进行设备复位（使用 `ppu-smi -r`）。

#### XID 16258: KERNEL: Launch abort

进程 kill 的过程当中驱动检测到多个进程上往硬件提交的任务间依赖有死锁的可能性，一般由 ICN 相关使用导致。内核驱动会主动让死锁关联进程对应的任务停止，并报该 XID。

- 当仅收到此 id 时，只需重新拉起业务进程即可。
- 若收到此 id 后，并伴随有收到 XID 16256，则按照 Kill over time 的处理流程，进行设备复位（使用 `ppu-smi -r`）。

#### XID 386: CP: ICN Disabled Error

该异常通常由 CP 执行 ICN 命令发送到被 DISABLE 的 ICN 导致，遇到该问题会导致应用程序 hang。

- kill 该进程并使用 `ppu-smi -r` 进行复位操作。
- 若复位无法解决问题，可以提交问题给 T-Head 团队进行调查。

#### XID 1157: L1: ICN Unreach Error

该异常是由于 switch network 问题，导致 switch 在检测到一笔 L1 的读写远端的请求时，发现目标 PPU 无法访问，从而返回 dummy response 并上报该异常。

#### XID 3718, 3719: ICN-C2CDMA: icn fence[atomic] req unreach

由于 switch network 问题，icn-fence/icn-atomic 请求无法抵达目标 PPU。

#### XID 3971, 3972: ICN-PKTE: die id unmatch/receive pkt sts err

接收到的 UD 包中：

- 3971：die id 不匹配。
- 3972：ack_sts 位非 0。

#### 其他 XID

该事件仅在硬件错误发生时触发，需要硬件团队调查问题。

#### XID 修复策略

| **类型** | **修复策略** | **XID** |
| --- | --- | --- |
| Invalid CMD | 设备复位（`ppu-smi -r`） | 384、3467、8576 |
| Kill 超时失败 | 设备复位（`ppu-smi -r`） | 16256 |
| CP ICN disabled | 设备复位（`ppu-smi -r`） | 386 |
| ICN Link 错误 | 热重启（`os reboot`） | 1157、4480、4481、4224、4225、4226、4227、3479、3470、3471、3718、3719、3971、3972 |
| ECC | 策略 1：退出所有用户进程，重新拉起业务即可（部分显存被屏蔽，用户可使用显存量变小）<br>策略 2：如多次发生 UECC，推荐做一次设备复位或热重启 | 642、1154、1665、1922、3713、3717、3468、3464、4997、5005 |
| 掉卡 | 冷重启（BMC 下电重启） | 16257 |
| 其它 | 当前业务中断，无需修复，重新拉起业务即可 |  |

比赛关联：复赛压测中若 benchmark 进程挂死或精度异常，先用 `dmesg` 对照 XID 表区分是用户程序错误（自己代码问题）、驱动错误还是硬件/链路问题，并按修复策略表决定复位、重启还是拉起进程；XID 16258（launch abort，多进程任务依赖死锁）在多实例并发压测时尤其常见。

## ECC 处理流程

### ECC 介绍

ECC 全称是 Error Correct Code，是一种硬件数据校验算法。相比奇偶校验，ECC 可以实现 single bit 错误的自动纠正，以及 double bit 错误的上报。后面我们把 single bit ECC 简称为 CECC（correctable ECC），double bit ECC 简称为 UECC（uncorrectable ECC）。

PPU HBM 有多种校验方式：

- 数据：ECC 校验（已默认打开），校验失败上报 ECC exception（only read 触发）。
- 地址和命令：奇偶校验（已默认打开），校验失败上报 parity exception（read write 都会校验）。

### ECC 发生监控

当监控到 ECC 发生之后，应当立刻参考"ECC 现场处理"一节进行现场处理。

在 dmesg 中看到 exception，使用下面命令如果可以搜索到证明发生了 UECC。

```bash
dmesg | grep "uncorrected ECC error detected"
```

通过 ECC counter 查询是否发生 UECC：

```bash
ppu-smi -q -d ECC
```

当看到 Volatile DRAM Uncorrectable 的数字大于零，证明此时发生了 UECC。

Aggregate 的数量包含这颗芯片从出厂到当前发生过的总次数，所以通常 reboot 之后 Aggregate 可能会大于零。

如果是通过 k8s 监控组件，可以直接调用 `hgmlDeviceGetTotalEccErrors` 接口来查询 UECC 的信息。当查询到 count 大于零证明发生了 UECC。

### ECC 现场处理

#### UECC 发生之后，处理流程

当检测到 UECC 发生之后，第一步需要检查是否还有残留的用户进程需要尽快 kill 掉。

所有进程退出的时候，驱动会把出错的 PPU page 做屏蔽，用户会发现 PPU device memory 有减少，不需要做 PPU reset 或者重启，重新拉起用户进程可以继续使用。

如果多次发生 UECC，PPU device memory 减少数量过多可能会影响用户正常使用，推荐尽快做一次 PPU reset 或者重启修复 UECC。

驱动在重启的过程中会对之前发生 UECC 的 memory page 进行 repair（memory cell replace）和 retirement 操作（加入黑名单），确保这次驱动加载以后用户不会再碰到这些发生过 UECC 的显存区域。

#### CECC 发生之后，处理流程

CECC 发生用户不会感知到，但是大量 CECC 发生之后驱动也会做 retirement，这个时候用户会发现 PPU device memory 有所减少。

不需要 PPU reset 或者重启，用户进程可以继续正常执行。

比赛关联：UECC 会导致驱动屏蔽出错显存页、可用显存变小，直接影响大 batch 吞吐实验的显存预算；跑压测前后用 `ppu-smi -q -d ECC` 检查 Volatile DRAM Uncorrectable 计数，排除硬件劣化对性能数据的干扰。
