# 阿里云 CLI 与 RAM 凭证 <span style="float: right;"><a href="../../README.md">目录</a></span>

## 目录

- [概念](#概念)
- [安装与升级](#安装与升级)
- [配置凭证](#配置凭证)
- [管理 Profile](#管理-profile)
- [安装比赛相关插件](#安装比赛相关插件)
- [验证身份与权限](#验证身份与权限)
- [常见问题](#常见问题)
- [速查表](#速查表)
- [官方文档](#官方文档)

## 概念

阿里云 CLI 使用凭证调用 OpenAPI，不使用 RAM 用户的控制台登录密码。常见凭证按比赛环境的推荐顺序如下：

| 凭证 | 适用场景 | 特点 |
| --- | --- | --- |
| OAuth | 有浏览器的个人开发机 | 推荐；用 RAM 用户网页登录，CLI 自动刷新短期令牌，不保存长期 AccessKey |
| EcsRamRole | CLI 运行在已绑定实例 RAM 角色的 ECS/比赛节点上 | 推荐；不落盘长期密钥，权限由实例角色决定 |
| RamRoleArn / STS | 临时提权、跨账号或自动化任务 | 使用短期凭证，需管理员预先配置角色和信任策略 |
| AccessKey | 无浏览器终端、现有平台只发放 AK | 长期有效，泄露风险最高；只使用 RAM 用户 AK，不使用主账号 AK |

RAM 用户还需要管理员授予资源权限。例如，能成功认证但执行 `aliyun cs ...` 返回 `Forbidden`，通常是缺少容器服务权限，而不是密码错误。

## 安装与升级

CLI 3.3.0 起采用插件化架构，比赛环境应使用 3.3.0 或更高版本：

```bash
aliyun version
```

Linux 可使用官方安装脚本：

```bash
/bin/bash -c "$(curl -fsSL https://aliyuncli.alicdn.com/install.sh)"
```

已有新版本 CLI 时可尝试：

```bash
aliyun upgrade
```

macOS、Windows、离线安装和历史版本见文末官方安装文档。

## 配置凭证

### OAuth：个人开发机首选

```bash
aliyun configure --mode OAuth --profile ppu
```

浏览器中使用完整 RAM 登录名完成认证。RAM 管理员需要先安装官方 CLI OAuth 应用，并把该 RAM 用户分配给应用；否则会提示调用未授权。

### ECS RAM 角色：比赛服务器首选

先由管理员给 ECS/节点绑定最小权限的实例 RAM 角色，再在实例内执行：

```bash
aliyun configure --mode EcsRamRole --profile ppu-ecs
```

按提示填写角色名和默认地域。不要为了省事在共享服务器上复制个人 AccessKey。

### AccessKey：仅在必要时使用

向管理员申请该 RAM 用户的 AccessKey ID、AccessKey Secret 和最小权限策略，然后交互式配置：

```bash
aliyun configure --mode AK --profile ppu-ak
```

不要把密钥直接写在命令参数中，因为命令可能进入 shell 历史和进程列表。不要在开启 `set -x` 的脚本中处理凭证。

## 管理 Profile

为比赛、个人实验和生产环境使用不同的 Profile：

```bash
# 查看全部 Profile；星号表示默认项
aliyun configure list

# 查看非敏感配置时仍需留意输出，不要把完整结果贴到公开渠道
aliyun configure get --profile ppu

# 切换默认 Profile
aliyun configure switch --profile ppu

# 单次命令显式指定 Profile 和地域
aliyun sts get-caller-identity --profile ppu --region <地域ID>
```

不再使用某个本地 Profile 时，可以移除本机配置：

```bash
aliyun configure delete --profile <待删除Profile>
```

这只删除本地 Profile，不会禁用云端 AccessKey。若怀疑 AK 泄露，应立即让管理员在 RAM 控制台禁用或删除对应 AK。

## 安装比赛相关插件

查看本机和远端插件：

```bash
aliyun plugin list
aliyun plugin list-remote
```

按需安装，不需要一次安装所有云产品：

```bash
aliyun plugin install --names sts cs cr nas
```

| 插件 | 用途 |
| --- | --- |
| `sts` | 确认当前调用身份、获取临时角色凭证 |
| `cs` | 查询 ACK 集群、节点、权限和 KubeConfig |
| `cr` | 查询 ACR 实例、仓库和镜像 Tag，获取临时登录凭证 |
| `nas` | 查询 NAS/CPFS 文件系统和挂载点 |
| `ecs` | 查询比赛节点对应的 ECS 实例；生命周期操作需额外谨慎 |
| `vpc`、`slb` | 排查集群网络、VPC 和负载均衡关联资源 |

每层命令均可使用 `--help`，以本机版本输出为准：

```bash
aliyun --help
aliyun cs --help
aliyun cs describe-cluster-nodes --help
```

## 验证身份与权限

先确认身份，避免在错误账号或 Profile 下操作：

```bash
aliyun sts get-caller-identity --profile ppu
```

重点核对返回的账号 ID、RAM 用户/角色 ARN 与预期是否一致。然后执行只读请求：

```bash
aliyun cs describe-regions --profile ppu
aliyun cs describe-clusters-v1 --biz-region-id <地域ID> --profile ppu
```

若命令支持 JMESPath，可用 `--cli-query` 缩小输出。例如只查看集群 ID、名称和状态：

```bash
aliyun cs describe-clusters-v1 \
  --biz-region-id <地域ID> \
  --profile ppu \
  --cli-query '[].{id:cluster_id,name:name,state:state}'
```

不同 API 的字段名可能随返回结构不同；查询表达式为空时先去掉 `--cli-query` 查看原始 JSON。

## 常见问题

| 现象 | 常见原因 | 处理 |
| --- | --- | --- |
| `InvalidAccessKeyId.NotFound` | AK 填错、被删除或账号站点不匹配 | 核对 Profile 和 AK 状态，必要时重新配置 |
| `SignatureDoesNotMatch` | Secret 错误、请求时间偏差较大 | 重新配置 Secret，并同步系统时间 |
| `Forbidden` / `NoPermission` | 身份有效但缺少 RAM 权限 | 保留 RequestId 和完整错误码，请管理员按最小权限补授权 |
| 返回空列表 | 地域或 Profile 不对，或资源不在当前账号 | 先查身份，再显式传 `--region`/业务地域参数 |
| OAuth“调用未被授权” | 管理员未安装 CLI OAuth 应用或未分配该用户 | 联系 RAM 管理员完成应用与身份分配 |
| 插件命令不存在 | CLI 低于 3.3.0 或未安装对应插件 | 升级 CLI，并用 `aliyun plugin install --name <插件>` 安装 |
| `kubectl` 无权限 | Kubernetes RBAC 未授予 | 这不是 RAM API 权限问题；让 ACK 管理员授予集群或命名空间权限 |

排障时可以临时提高日志级别，但日志可能包含请求元数据，不要直接公开：

```bash
aliyun cs describe-clusters-v1 --biz-region-id <地域ID> --log-level DEBUG
```

## 速查表

| 目的 | 命令 |
| --- | --- |
| 版本 | `aliyun version` |
| Profile 列表 | `aliyun configure list` |
| 切换 Profile | `aliyun configure switch --profile ppu` |
| 身份自检 | `aliyun sts get-caller-identity --profile ppu` |
| 已装插件 | `aliyun plugin list` |
| 安装单个插件 | `aliyun plugin install --name cs` |
| 查看产品命令 | `aliyun cs --help` |
| 查看 API 参数 | `aliyun cs describe-clusters-v1 --help` |

## 官方文档

- [阿里云 CLI 文档中心](https://help.aliyun.com/zh/cli/)
- [安装/更新阿里云 CLI](https://help.aliyun.com/zh/cli/install-cli-on-linux)
- [快速使用阿里云 CLI](https://help.aliyun.com/zh/cli/quickly-start-using-alibaba-cloud-cli)
- [配置与管理身份凭证](https://help.aliyun.com/zh/cli/configure-credentials/)
- [配置 OAuth 凭证](https://help.aliyun.com/zh/cli/oauth-credentials)
- [配置 AccessKey 凭证](https://help.aliyun.com/zh/cli/ak-credential)
- [CLI 错误排查](https://help.aliyun.com/zh/cli/cli-troubleshooting)
