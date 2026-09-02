# 阿里云比赛运维速查 <span style="float: right;"><a href="../../README.md">目录</a></span>

> 面向复赛阶段：使用 RAM 用户、阿里云 CLI 和 `kubectl` 定位比赛资源，连接 ACK 集群，检查 PPU 节点，并管理比赛镜像与共享存储。

## 目录

- [文件](#文件)
- [推荐流程](#推荐流程)
- [安全边界](#安全边界)
- [命令速查](#命令速查)

## 文件

| 文件 | 内容 | 什么时候用 |
| --- | --- | --- |
| [01_cli_ram.md](01_cli_ram.md) | CLI 3.3+ 安装、OAuth/AccessKey/RAM 角色选择、Profile、插件、身份与权限排查 | 第一次配置本机，或遇到 `Forbidden`、身份/地域不对时 |
| [02_ack_ppu.md](02_ack_ppu.md) | 查询 ACK 集群、获取短期 KubeConfig、检查命名空间/RBAC、PPU 节点、Pod、日志和端口转发 | 登录比赛集群、部署前检查、任务异常排查时 |
| [03_image_storage.md](03_image_storage.md) | ACR 镜像仓库、Docker 构建/推送、工作负载镜像确认、NAS/CPFS 查询与挂载检查 | 发布比赛镜像、排查拉取失败、确认模型和数据存储时 |

## 推荐流程

```text
确认 CLI/Profile/身份
        ->
确认地域与 ACK 集群
        ->
获取短期 KubeConfig，检查 RBAC
        ->
确认 PPU 节点、命名空间和已有工作负载
        ->
构建并推送不可变镜像 Tag
        ->
部署、观察事件与日志、执行 benchmark
        ->
保存代码、配置摘要和性能结果，不保存凭证
```

比赛资源通常由组织账号统一创建。RAM 权限和 Kubernetes RBAC 是两层独立权限：阿里云 API 能列出 ACK 集群，不代表 `kubectl` 可以访问所有命名空间；反过来也一样。

## 安全边界

| 对象或操作 | 风险 | 约定 |
| --- | --- | --- |
| AccessKey Secret、STS Token、OAuth Token | 可调用云 API | 不写入仓库、聊天、终端历史或截图；优先使用 OAuth、RAM 角色或短期 STS |
| KubeConfig | 内含集群地址和认证材料 | 使用短有效期，权限设为 `600`，不放在仓库目录中 |
| ACR 临时密码 | 可拉取或推送镜像 | 使用 `docker login --password-stdin` 或交互输入，不写入脚本 |
| `kubectl apply`、扩缩容、重启 | 改变比赛工作负载 | 操作前确认 context、namespace、资源名，操作后检查 rollout 和事件 |
| 删除集群、释放节点、删除 NAS/镜像 | 可能造成不可恢复的数据或资源损失 | 本目录不提供快捷命令；需要时先在控制台核对资源归属并获得管理员确认 |
| 安全组 `0.0.0.0/0` 放行 | 暴露服务或 SSH | 不作为默认方案；优先使用专有网络、白名单或 `kubectl port-forward` |

提交前检查可能误入仓库的敏感文件：

```bash
git status --short
git diff --check
rg -n --hidden --glob '!*.tsv' \
  '(AccessKeySecret|access_key_secret|AuthorizationToken|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|client-key-data:|token:)' .
```

上面的扫描仅用于提示，出现匹配后仍需人工判断；文档中的字段名称也可能被匹配。

## 命令速查

| 目的 | 命令 |
| --- | --- |
| 查看 CLI 版本 | `aliyun version` |
| 查看当前 Profile | `aliyun configure list` |
| 确认调用身份 | `aliyun sts get-caller-identity` |
| 查看已安装插件 | `aliyun plugin list` |
| 列出 ACK 集群 | `aliyun cs describe-clusters-v1 --biz-region-id <地域ID>` |
| 查看 ACK 节点 | `aliyun cs describe-cluster-nodes --cluster-id <集群ID> --state running --page-size 100` |
| 查看 Kubernetes 当前上下文 | `kubectl config current-context` |
| 检查本人权限 | `kubectl auth can-i --list -n <命名空间>` |
| 查看 PPU 节点和 Pod | `kubectl get nodes -o wide`、`kubectl get pods -A -o wide` |
| 查看 ACR 实例 | `aliyun cr list-instance --region <地域ID>` |
| 查看 NAS/CPFS | `aliyun nas describe-file-systems --region <地域ID> --page-size 100` |
