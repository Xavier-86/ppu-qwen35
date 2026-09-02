# ACK 与 PPU 比赛集群操作 <span style="float: right;"><a href="../../README.md">目录</a></span>

## 目录

- [概念](#概念)
- [发现比赛集群](#发现比赛集群)
- [获取短期 KubeConfig](#获取短期-kubeconfig)
- [确认上下文与权限](#确认上下文与权限)
- [检查 PPU 节点](#检查-ppu-节点)
- [检查比赛工作负载](#检查比赛工作负载)
- [日志与现场排查](#日志与现场排查)
- [进入容器、传文件与端口转发](#进入容器传文件与端口转发)
- [受控更新工作负载](#受控更新工作负载)
- [速查表](#速查表)

## 概念

ACK 是阿里云容器服务 Kubernetes 版。阿里云 CLI 负责发现集群、查询云侧节点和签发 KubeConfig；`kubectl` 负责操作 Kubernetes 资源。

| 层级 | 工具 | 权限来源 | 典型对象 |
| --- | --- | --- | --- |
| 阿里云资源层 | `aliyun cs` | RAM 策略 | 集群、节点池、ECS 关联资源、KubeConfig 签发 |
| Kubernetes 层 | `kubectl` | 集群 RBAC | Namespace、Pod、Deployment、Service、PVC |
| PPU 设备层 | 容器内 `ppu-smi`、Asight | Pod 设备分配和宿主机驱动 | PPU 卡、显存、XID/ECC、性能指标 |

## 发现比赛集群

先确认身份和地域：

```bash
aliyun sts get-caller-identity
aliyun cs describe-regions
```

列出指定地域的集群：

```bash
aliyun cs describe-clusters-v1 \
  --biz-region-id <地域ID> \
  --page-size 100
```

取得集群 ID 后查询详情、节点池、节点和关联云资源：

```bash
aliyun cs describe-cluster-detail --cluster-id <集群ID>
aliyun cs describe-cluster-node-pools --cluster-id <集群ID>
aliyun cs describe-cluster-nodes \
  --cluster-id <集群ID> \
  --state running \
  --page-size 100
aliyun cs describe-cluster-resources --cluster-id <集群ID>
```

这些命令是只读操作。记录比赛所需的地域、集群 ID、命名空间、节点池 ID 和 VPC ID，但不要把 KubeConfig 或凭证记入仓库。

## 获取短期 KubeConfig

KubeConfig 含认证材料。优先申请 15～60 分钟的短期配置，并写到仓库之外：

```bash
mkdir -p ~/.kube
aliyun cs describe-cluster-user-kubeconfig \
  --cluster-id <集群ID> \
  --private-ip-address false \
  --temporary-duration-minutes 60 \
  | jq -r '.config' > ~/.kube/ppu-competition.yaml
chmod 600 ~/.kube/ppu-competition.yaml
```

连接方式按执行位置选择：

| 位置 | `--private-ip-address` | 说明 |
| --- | --- | --- |
| 本地电脑 | `false` | 需要集群开启公网 API Server，并受白名单限制 |
| 同 VPC 的 ECS/跳板机 | `true` | 优先走内网，不暴露公网入口 |

如果 API 返回 `config` 为空或 `Forbidden`，需要 ACK 管理员给当前 RAM 用户签发 KubeConfig 并授予 Kubernetes RBAC。不要向他人索要并共用管理员 KubeConfig。

后续命令显式指定文件，避免误用其他集群：

```bash
kubectl --kubeconfig ~/.kube/ppu-competition.yaml config current-context
kubectl --kubeconfig ~/.kube/ppu-competition.yaml cluster-info
```

## 确认上下文与权限

每次做写操作前执行：

```bash
kubectl --kubeconfig ~/.kube/ppu-competition.yaml config current-context
kubectl --kubeconfig ~/.kube/ppu-competition.yaml get namespace
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  auth can-i --list -n <比赛命名空间>
```

云侧也可查看当前用户在集群中可访问的命名空间：

```bash
aliyun cs describe-user-cluster-namespaces --cluster-id <集群ID>
```

只验证某个动作时，用 `can-i`，不要直接尝试写操作：

```bash
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  auth can-i create pods -n <比赛命名空间>
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  auth can-i update deployments.apps -n <比赛命名空间>
```

## 检查 PPU 节点

先看节点、标签、污点和可分配资源：

```bash
kubectl --kubeconfig ~/.kube/ppu-competition.yaml get nodes -o wide
kubectl --kubeconfig ~/.kube/ppu-competition.yaml get nodes --show-labels
kubectl --kubeconfig ~/.kube/ppu-competition.yaml describe node <PPU节点名>
```

重点检查：

- 节点是否 `Ready`，是否存在 `MemoryPressure`、`DiskPressure`、`PIDPressure`。
- `Capacity`/`Allocatable` 中 PPU 扩展资源的名称和数量。
- 节点标签是否标明 810E/PPU 型号、节点池和可用区。
- 节点污点是否要求 Pod 配置对应 toleration。
- `Allocated resources` 是否已经被其他 Pod 占用。

设备资源名由集群设备插件定义，不要假定一定叫 `nvidia.com/gpu`。从节点描述和已有比赛 Pod 的 YAML 中确认实际键名：

```bash
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  -n <比赛命名空间> get pod <已有PPU-Pod> -o yaml
```

若已安装 metrics-server，可观察 CPU/内存；PPU 指标仍以 `ppu-smi` 和 Asight 为准：

```bash
kubectl --kubeconfig ~/.kube/ppu-competition.yaml top nodes
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  -n <比赛命名空间> top pods
```

## 检查比赛工作负载

```bash
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  -n <比赛命名空间> get deploy,statefulset,job,pod,svc,pvc -o wide
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  -n <比赛命名空间> get pod <Pod名> -o yaml
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  -n <比赛命名空间> describe pod <Pod名>
```

部署前核对：

| 项目 | 原因 |
| --- | --- |
| 镜像使用唯一 Tag 或 digest | 避免节点继续使用旧的 `latest` 缓存 |
| PPU 资源 requests/limits | 决定设备是否分配，以及能拿到几张卡 |
| nodeSelector/affinity/tolerations | 决定是否调度到 PPU 节点 |
| PVC 与 mountPath | 模型权重、数据集和结果是否可见 |
| command/args/env | 推理入口、batch、精度和并行参数是否正确 |
| readiness/liveness probe | 模型加载较慢时避免被误判失败或过早接流量 |
| Service/端口 | benchmark 是否访问了正确容器和端口 |

## 日志与现场排查

```bash
# 当前日志；多容器 Pod 追加 -c <容器名>
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  -n <比赛命名空间> logs <Pod名> --tail=200

# 容器重启前一次的日志
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  -n <比赛命名空间> logs <Pod名> --previous --tail=200

# 按时间查看集群事件
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  -n <比赛命名空间> get events --sort-by=.lastTimestamp

# 实时观察 Pod 状态
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  -n <比赛命名空间> get pods -w
```

| 状态 | 优先检查 |
| --- | --- |
| `Pending` | `describe pod` 的 Events、PPU 资源是否足够、污点/亲和性、PVC 是否绑定 |
| `ImagePullBackOff` | 镜像地址/Tag、ACR 网络入口、imagePullSecret、RAM/仓库权限 |
| `CrashLoopBackOff` | `logs --previous`、启动参数、模型路径、共享内存和容器内存限制 |
| `OOMKilled` | Pod memory limit、主机内存；PPU 显存 OOM 通常在应用日志中 |
| 已运行但无 PPU | Pod requests/limits 键名、设备插件、容器内 `/dev/alixpu*` |
| 性能抖动 | 节点上其他 Pod、CPU/NUMA、频率、PPU 温度/ECC、PVC I/O 和镜像冷启动 |

进入容器后按 [../ppu_platform/01_guide.md](../ppu_platform/01_guide.md) 和 [../ppu_platform/03_driver.md](../ppu_platform/03_driver.md) 检查 `ppu-smi`、设备节点、XID/ECC。

## 进入容器、传文件与端口转发

```bash
# 进入容器
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  -n <比赛命名空间> exec -it <Pod名> -- /bin/bash

# 只传小文件；大模型和数据集应使用镜像、NAS/CPFS 或对象存储
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  -n <比赛命名空间> cp ./local-file <Pod名>:/workspace/local-file

# 将本地 8000 转发到 Service 8000，适合临时 benchmark
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  -n <比赛命名空间> port-forward service/<服务名> 8000:8000
```

`kubectl cp` 依赖容器内的 `tar`。不要用它同步几十 GB 的模型权重，也不要把运行中的容器当作唯一存储位置。

## 受控更新工作负载

写操作前先保存当前声明，并用服务端 dry-run 验证新配置：

```bash
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  -n <比赛命名空间> get deployment <Deployment名> -o yaml \
  > /tmp/ppu-deployment-before.yaml

kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  -n <比赛命名空间> apply --dry-run=server -f <部署文件.yaml>
```

确认 context、namespace 和 diff 后再应用并观察：

```bash
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  -n <比赛命名空间> diff -f <部署文件.yaml>
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  -n <比赛命名空间> apply -f <部署文件.yaml>
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  -n <比赛命名空间> rollout status deployment/<Deployment名> --timeout=15m
```

如果 rollout 失败，先看新 Pod 的事件和日志；是否回滚取决于比赛平台约定和数据兼容性，不要在未核对影响时删除 Pod、PVC、节点或集群。

## 速查表

| 目的 | 命令 |
| --- | --- |
| 查集群 | `aliyun cs describe-clusters-v1 --biz-region-id <地域ID>` |
| 查节点 | `aliyun cs describe-cluster-nodes --cluster-id <集群ID> --state running --page-size 100` |
| 查 K8s 命名空间权限 | `aliyun cs describe-user-cluster-namespaces --cluster-id <集群ID>` |
| 当前 context | `kubectl config current-context` |
| 权限自检 | `kubectl auth can-i --list -n <命名空间>` |
| Pod 全景 | `kubectl get pods -A -o wide` |
| 最近事件 | `kubectl get events -A --sort-by=.lastTimestamp` |
| 当前/前次日志 | `kubectl logs <Pod> --tail=200`、`kubectl logs <Pod> --previous --tail=200` |
| 镜像确认 | `kubectl get pod <Pod> -o jsonpath='{.status.containerStatuses[*].imageID}'` |
