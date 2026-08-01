# 本地配置契约

所有真实配置都放在工作区 `config/` 目录。该目录中的以下文件已被 `.gitignore` 排除，禁止复制到技能目录或 `output/`：

- `config/environments_config.json`：不含凭证的 API 环境元数据。
- `config/credentials.local.json`：账号、密码和 Token。
- `config/connections.json`：本工作区数据库连接的唯一注册表。

禁止读取 `.codex/skills/*/state/connections.json` 或用户目录下的同名文件作为替代。这些文件可能属于其他工作区或存在过期副本。

## API 环境

`config/environments_config.json` 使用以下结构：

```json
{
  "environments": [
    {
      "name": "环境显示名称",
      "api_domain": "https://api.example.test",
      "environment_type": "test",
      "allow_test_data_mutation": true,
      "healthcheck_url": "https://api.example.test/verified-health-endpoint",
      "healthcheck_headers": {"sysType": "1"},
      "healthcheck_success_code": "00000",
      "healthcheck_unauthorized_codes": ["A00004"],
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

只有 `environment_type` 严格为 `test` 且 `allow_test_data_mutation` 严格为 `true` 时才允许 HTTP/SQL 数据变更；缺失、为其他值或生产环境均立即阻断。`healthcheck_url` 必须是已知会校验鉴权且无业务副作用的具体端点，不能只填写不校验鉴权的 `api_domain` 根地址。禁止猜测健康检查路径。端点所需的非敏感固定 Header 写入 `healthcheck_headers`，且必须有前端请求拦截器或后端契约证据；禁止在其中保存 Authorization、Cookie 或其他凭证。若网关以 HTTP 2xx 包装业务错误，必须配置 `healthcheck_success_code` 和 `healthcheck_unauthorized_codes`；登录控件只接受 Stable ID、Test ID 或 Accessibility ID。

## 本地凭证

`config/credentials.local.json` 可保留其他工具使用的 `platforms` 和 `databases` 节点；本技能读取 `environments` 节点：

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
2. 同时校验 HTTP 状态和应用响应码。只有 2xx 且响应码等于 `healthcheck_success_code` 时继续；HTTP 401 或响应码命中 `healthcheck_unauthorized_codes` 时启动 Playwright。其他最终错误必须包含环境名、URL、HTTP 状态、脱敏响应体和修复建议。
3. 使用配置的稳定定位信息完成登录，从明确的响应 Header 或 `token_storage_key` 读取 Token。
4. 使用新 Token 再次探测。成功后只写回 `config/credentials.local.json`。
5. 缺少端点、定位信息、凭证，或三次尝试后仍失败时立即停止。

## 数据库连接

只使用工作区 `config/connections.json`。先展示已启用连接并等待用户确认，然后将确认的只读连接名传给 `execute_read_query_plan.py --connection-name`。受控 SQL 写入必须再次单独确认连接名，禁止根据只读连接、环境、表名或历史记录自动选择。

```json
{
  "connections": [
    {
      "name": "测试只读",
      "host": "LOCAL_ONLY",
      "port": 3306,
      "username": "LOCAL_ONLY",
      "password": "LOCAL_ONLY",
      "enabled": true,
      "access_mode": "read-only"
    },
    {
      "name": "测试受控写入",
      "host": "LOCAL_ONLY",
      "port": 3306,
      "username": "LOCAL_ONLY",
      "password": "LOCAL_ONLY",
      "enabled": true,
      "access_mode": "controlled-write",
      "environment_name": "环境显示名称",
      "allowed_databases": ["真实测试库"],
      "allowed_tables": ["允许构造数据的表"]
    }
  ]
}
```

数据库凭证保存在该 Git 忽略文件中，不复制到技能目录或输出产物。只读连接必须声明 `access_mode=read-only`；写连接必须声明 `access_mode=controlled-write`、绑定同一测试环境并限定库表白名单，否则立即停止。
