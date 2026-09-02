# 比赛镜像与共享存储 <span style="float: right;"><a href="../../README.md">目录</a></span>

## 目录

- [概念](#概念)
- [查询 ACR 资源](#查询-acr-资源)
- [登录镜像仓库](#登录镜像仓库)
- [构建与推送比赛镜像](#构建与推送比赛镜像)
- [排查镜像拉取](#排查镜像拉取)
- [查询 NAS 与 CPFS](#查询-nas-与-cpfs)
- [容器内检查存储](#容器内检查存储)
- [比赛数据分层建议](#比赛数据分层建议)
- [速查表](#速查表)

## 概念

比赛运行环境通常把不同内容放在不同层：

| 内容 | 推荐位置 | 原因 |
| --- | --- | --- |
| Python/C++ 代码、依赖、SAIL 运行库 | ACR 容器镜像 | 环境可复现，部署快 |
| Qwen3.5-2B 权重、数据集 | NAS/CPFS PVC 或平台指定共享盘 | 体积大，多 Pod 复用，避免反复构建镜像 |
| 编译缓存、预热产物 | 可持久化高速盘或镜像层 | 减少冷启动；需验证与驱动/SDK/模型版本兼容 |
| benchmark 临时输出 | 独立结果目录 | 避免覆盖基线，便于优化前后对比 |
| AccessKey、KubeConfig、镜像密码 | 不进入上述任一持久产物 | 使用短期凭证或 Kubernetes Secret，并限制权限 |

ACR 是云侧镜像仓库，Docker/BuildKit 负责构建和推送，Kubernetes 负责在节点上拉取镜像。NAS/CPFS 则通过挂载点或 PVC 提供共享文件系统。

## 查询 ACR 资源

先列出指定地域的 ACR 企业版实例：

```bash
aliyun cr list-instance --region <地域ID> --page-size 100
```

取得实例 ID 后查询仓库和 Tag：

```bash
aliyun cr list-repository \
  --region <地域ID> \
  --instance-id <ACR实例ID> \
  --page-size 100

aliyun cr list-repo-tag \
  --region <地域ID> \
  --instance-id <ACR实例ID> \
  --repo-id <仓库ID> \
  --page-size 100
```

查看实例访问入口，确认本机/集群使用公网还是 VPC 地址：

```bash
aliyun cr list-instance-endpoint \
  --region <地域ID> \
  --instance-id <ACR实例ID> \
  --module-name Registry
```

## 登录镜像仓库

获取临时用户名、密码和过期时间：

```bash
aliyun cr get-authorization-token \
  --region <地域ID> \
  --instance-id <ACR实例ID>
```

该命令输出的 `AuthorizationToken` 是敏感信息。不要复制到文档、Issue 或 shell 脚本；使用交互式登录并在提示时输入临时密码：

```bash
docker login <ACR域名> --username <临时用户名>
```

登录后检查 Docker 配置文件权限。共享服务器上完成推送后退出：

```bash
docker logout <ACR域名>
```

## 构建与推送比赛镜像

使用能追溯到 Git 提交的不可变 Tag，不使用 `latest` 作为比赛复现实验的唯一标识：

```bash
git rev-parse --short HEAD
docker build \
  --label org.opencontainers.image.revision=<Git短提交> \
  -t <ACR域名>/<命名空间>/<仓库>:<Git短提交> \
  .
docker push <ACR域名>/<命名空间>/<仓库>:<Git短提交>
```

推送后记录 digest：

```bash
docker image inspect \
  <ACR域名>/<命名空间>/<仓库>:<Git短提交> \
  --format '{{json .RepoDigests}}'
```

为避免架构不匹配，构建前确认比赛节点 CPU 架构：

```bash
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  get nodes -o custom-columns=NAME:.metadata.name,ARCH:.status.nodeInfo.architecture,OS:.status.nodeInfo.osImage
```

需要跨架构构建时明确指定目标平台，并在推送前确认基础镜像、SAIL SDK 和 PPU 用户态库支持该架构：

```bash
docker buildx build \
  --platform linux/<目标架构> \
  -t <ACR域名>/<命名空间>/<仓库>:<Git短提交> \
  --push \
  .
```

不要把模型权重、数据集、AccessKey 或 KubeConfig 通过 `COPY` 写入镜像。检查 `.dockerignore` 是否覆盖这些内容。

## 排查镜像拉取

先从 Pod 事件确认错误类型：

```bash
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  -n <比赛命名空间> describe pod <Pod名>
```

| 错误 | 重点检查 |
| --- | --- |
| `manifest unknown` | Tag 拼写、仓库路径、目标架构 manifest |
| `unauthorized` / `denied` | imagePullSecret、ACR 仓库权限、临时密码是否过期 |
| `i/o timeout` | 节点到 ACR 域名的网络、VPC 访问入口、DNS |
| 拉到旧镜像 | 是否重复使用可变 Tag、`imagePullPolicy`、实际 image digest |
| 启动时报 SAIL/驱动不兼容 | 镜像用户态 SDK 与宿主机 KMD/设备插件版本 |

查看工作负载声明的镜像和实际运行 digest：

```bash
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  -n <比赛命名空间> get deployment <Deployment名> \
  -o jsonpath='{.spec.template.spec.containers[*].image}{"\n"}'
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  -n <比赛命名空间> get pod <Pod名> \
  -o jsonpath='{.status.containerStatuses[*].imageID}{"\n"}'
```

## 查询 NAS 与 CPFS

列出文件系统：

```bash
aliyun nas describe-file-systems \
  --region <地域ID> \
  --file-system-type all \
  --page-size 100
```

取得文件系统 ID 后查询挂载点和权限组：

```bash
aliyun nas describe-mount-targets \
  --region <地域ID> \
  --file-system-id <文件系统ID> \
  --page-size 100
aliyun nas describe-access-groups --region <地域ID>
```

重点核对：

- 文件系统与比赛集群是否在兼容的地域/VPC。
- 挂载点状态、协议和权限组是否允许节点网段。
- PVC/PV 是否引用正确的文件系统和挂载点。
- 模型目录是只读共享还是允许写入；多进程是否会同时更新缓存。

查询不会改变资源。创建/删除文件系统、挂载点、权限规则和快照会影响费用或数据，本目录不提供快捷操作；应由平台管理员按比赛方案配置。

## 容器内检查存储

Kubernetes 层先看 PVC：

```bash
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  -n <比赛命名空间> get pvc
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  -n <比赛命名空间> describe pvc <PVC名>
kubectl --kubeconfig ~/.kube/ppu-competition.yaml \
  -n <比赛命名空间> describe pod <Pod名>
```

容器内检查挂载类型、容量、inode 和模型文件可读性：

```bash
df -hT
df -ih
mount
ls -lah <模型目录>
```

性能测试不要直接覆盖模型目录。先在专用临时目录做顺序读写测试，并确认平台允许产生测试数据；压测结束后保留吞吐、延迟、文件大小、并发度和测试位置等记录。

## 比赛数据分层建议

| 层 | 放什么 | 注意事项 |
| --- | --- | --- |
| 镜像只读层 | 代码、固定依赖、小型配置 | Tag/digest 可追溯，避免放权重和秘密 |
| NAS/CPFS 共享层 | 模型、公开数据集、公共编译产物 | 防止多任务争抢 I/O 或并发改写缓存 |
| 容器临时盘 | 解压缓存、单次运行中间文件 | Pod 重建后丢失，先确认容量和 eviction 风险 |
| 结果持久层 | benchmark JSON/日志摘要/Asight 报告 | 按提交、参数、时间分目录，避免覆盖基线 |

建议结果目录至少记录：Git commit、镜像 digest、模型版本、SDK/驱动版本、PPU 拓扑、命令参数和原始指标。这样才能把云侧部署变化与代码优化收益区分开。

## 速查表

| 目的 | 命令 |
| --- | --- |
| ACR 实例 | `aliyun cr list-instance --region <地域ID>` |
| 镜像仓库 | `aliyun cr list-repository --instance-id <实例ID> --region <地域ID>` |
| 镜像 Tag | `aliyun cr list-repo-tag --instance-id <实例ID> --repo-id <仓库ID> --region <地域ID>` |
| 临时登录凭证 | `aliyun cr get-authorization-token --instance-id <实例ID> --region <地域ID>` |
| 文件系统 | `aliyun nas describe-file-systems --region <地域ID>` |
| NAS 挂载点 | `aliyun nas describe-mount-targets --file-system-id <文件系统ID> --region <地域ID>` |
| PVC | `kubectl -n <命名空间> get pvc` |
| 实际镜像 digest | `kubectl -n <命名空间> get pod <Pod> -o jsonpath='{.status.containerStatuses[*].imageID}'` |
