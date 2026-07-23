# 本地配置契约

所有真实配置都放在工作区 `config/` 目录。该目录中的以下文件已被 `.gitignore` 排除，禁止复制到技能目录或 `output/`：

- `config/environments_config.json`：不含凭证的 API 环境元数据。
- `config/credentials.local.json`：账号、密码和 Token。
- `config/connections.json`：仅在未使用 `xjjk-yewu-sql` 注册表时使用；本技能默认不读取该文件。

## API 环境

`config/environments_config.json` 使用以下结构：

```json
{
  "environments": [
    {
      "name": "环境显示名称",
      "api_domain": "https://api.example.test",
      "healthcheck_url": "https://api.example.test/verified-health-endpoint",
      "login_url": "https://console.example.test/login",
      "credentials_ref": "environments.example-test",
      "login_controls": {
        "account_test_id": "login-account",
        "password_test_id": "login-password",
        "submit_test_id": "login-submit",
        "token_storage_key": "authorization"
      }
    }
  ]
}
```

`healthcheck_url` 必须是已知会校验鉴权且无业务副作用的端点。禁止猜测健康检查路径。登录控件只接受 Stable ID、Test ID 或 Accessibility ID。

## 本地凭证

`config/credentials.local.json` 使用以下结构：

```json
{
  "environments": {
    "example-test": {
      "account": "LOCAL_ONLY",
      "password": "LOCAL_ONLY",
      "authorization": "LOCAL_ONLY"
    }
  }
}
```

读取 `credentials_ref` 指向的对象。Token 续期成功后只原子更新对应 `authorization`；不得改动其他环境，不得在对话、日志或产物中回显值。

## Token 校验与续期

1. 使用当前 Token 请求 `healthcheck_url`，最多尝试三次，并记录不含凭证的结构化 Warning。
2. 返回 2xx 时继续；401 时启动 Playwright；其他最终错误必须包含环境名、URL、HTTP 状态、脱敏响应体和修复建议。
3. 使用配置的稳定定位信息完成登录，从明确的响应 Header 或 `token_storage_key` 读取 Token。
4. 使用新 Token 再次探测。成功后只写回 `config/credentials.local.json`。
5. 缺少端点、定位信息、凭证，或三次尝试后仍失败时立即停止。

## 数据库连接

使用 `xjjk-yewu-sql` 的 `.codex/skills/xjjk-yewu-sql/state/connections.json`。先展示已启用连接并等待用户确认，然后将确认的连接名传给 `execute_read_query_plan.py --connection-name`。该脚本要求注册表字段为 `connections[].name/host/port/username/password/enabled`。

默认选择只读账号。无法证明账号只读时立即停止，不执行查询。
