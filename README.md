# XJJK Test AI Workspace

这是一个独立的测试 AI 工作区。远程 `aiworkspace` 仓库仅用于参考目录组织，本工作区不与其同步，也不向其提交代码。

## 工作流

```text
tapd-requirement-analysis
  -> tapd-testcase-generation
  -> tapd-code-source-review
  -> tapd-prepare-test-from
  -> test-execute-from-tapd
```

`xjjk-yewu-sql` 为代码审查、测试准备和测试执行提供 MySQL 元数据能力。

## 目录

```text
config/              本地凭证、环境和数据库连接配置
.codex/skills/       项目内 skill 副本
output/              当前需求的阶段产物
scratch/             测试执行期间的临时脚本和快照
services/            可选的后端代码工作目录
frontends/           可选的前端代码工作目录
system-context/      可复用的业务与系统上下文
```

## 初次配置

1. 在 `config/credentials.local.json` 中维护 TAPD 配置。
2. 在 `config/environments_config.json` 中维护测试平台和数据库配置。
3. 使用 `xjjk-yewu-sql` 的命令登记只读数据库连接；连接信息保存在 `config/connections.json`，该文件不会提交。
4. 安装项目依赖：`python -m pip install -r requirements-workflow.txt`。

敏感配置、数据库缓存、执行输出和临时代码均由 `.gitignore` 排除。
