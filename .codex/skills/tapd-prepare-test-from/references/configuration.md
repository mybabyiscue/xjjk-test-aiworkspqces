# 本地配置契约

所有真实配置都放在工作区 `config/` 目录，并由 `.gitignore` 排除：

- `config/environments_config.json`：API 环境、账号、密码和 Token 的唯一来源。
- `config/connections.json`：本工作区数据库连接的唯一注册表。

禁止读取技能目录、用户目录或其他工作区中的同名文件作为替代。

## API 环境

每个环境必须直接提供 `name`、`api_domain` 和 `authorization`。Skill 原样使用 `authorization`，禁止自动添加或删除认证方案前缀。登录能力由完整的 `login_url`、`account`、`password` 字段组声明；三项必须同时存在或同时不存在。

```json
{
  "environments": [
    {
      "name": "环境显示名称",
      "api_domain": "https://api.example.test",
      "environment_type": "test",
      "allow_test_data_mutation": true,
      "login_url": "https://console.example.test/login",
      "account": "LOCAL_ONLY",
      "password": "LOCAL_ONLY",
      "authorization": "LOCAL_ONLY",
      "token_probe": {
        "url": "https://api.example.test/verified-read-only-endpoint",
        "headers": {"X-System": "test"},
        "response_code_path": "$.code",
        "success_codes": ["SUCCESS"],
        "unauthorized_codes": ["TOKEN_EXPIRED"]
      }
    }
  ]
}
```

忽略与本技能无关的额外字段，但拒绝旧的 `credentials_ref`、`healthcheck_success_code` 和 `healthcheck_unauthorized_codes`，避免配置看似生效而实际未被消费。禁止按环境名称、域名、路径或业务码在脚本中创建特殊分支。

Token Gate 通过不代表允许数据变更。只有 `environment_type` 严格为 `test` 且 `allow_test_data_mutation` 严格为 `true` 时，后续阶段才允许 HTTP 或受控 SQL 写入；字段缺失或值不匹配时必须阻断写入。

## Token 探测

`token_probe` 是可选的数据驱动规则。存在时必须完整提供：

- `url`：已知会校验鉴权且无业务副作用的具体端点，禁止使用 `api_domain` 根地址。
- `headers`：有代码或接口契约证据的固定非敏感 Header；禁止 Authorization、Cookie 或其他凭证。
- `response_code_path`：应用响应码的 JSONPath；不需要应用码时使用空字符串。
- `success_codes`：允许继续的应用码；不使用应用码时使用空数组。
- `unauthorized_codes`：表示 Token 失效的应用码；不使用应用码时使用空数组。

代码只解释这些通用字段。任何具体业务码只能出现在被 Git 忽略的环境配置中，禁止写入 Skill、脚本或测试。

## Token Gate

1. 有 `token_probe` 时，使用当前 `authorization` 原值请求探测端点。最多尝试指定次数，每次失败输出不含凭证的结构化 Warning。
2. HTTP 401/403 或应用码命中 `unauthorized_codes` 时判定 Token 失效；2xx 且应用码命中 `success_codes` 时判定有效。未配置应用码路径时只按 HTTP 状态判断。
3. Token 有效时继续，不执行登录。
4. Token 失效且登录字段完整时，使用 Playwright 打开 `login_url`。先检查页面 DOM，只使用唯一的 Stable ID、Test ID 或 Accessibility ID 定位账号框、密码框和提交控件。
5. 登录后只接受发往同一 `api_domain` 的真实请求所携带的新 Authorization；出现多个不同 Token、验证码、租户歧义或缺少稳定定位信息时立即停止。
6. 有探测规则时使用新 Token 再次探测。成功后只原子更新所选环境的 `authorization`。
7. 没有探测规则但登录字段完整时主动登录，并以登录后发往同一 `api_domain` 的新鉴权请求作为续期证据。
8. Token 失效但没有完整登录能力，或既无探测能力也无登录能力时立即停止，不提供降级替代。

## 敏感信息

- `config/environments_config.json` 必须被 Git 忽略；未被忽略时立即停止。
- 对话、日志、异常、Markdown 和中间 JSON 不得回显 `account`、`password`、`authorization`、Cookie 或其他 Token。
- 结构化 Warning 仅包含环境名、脱敏 URL、HTTP 状态、脱敏响应体、尝试次数和修复建议。
- Token 续期写回必须使用同目录临时文件和原子替换，不得改动其他环境。

## 数据库连接

只使用工作区 `config/connections.json`。先展示已启用连接并等待用户确认，然后将确认的只读连接名传给 `execute_read_query_plan.py --connection-name`。受控 SQL 写入必须再次单独确认连接名，禁止根据只读连接、环境、表名或历史记录自动选择。

数据库连接凭证不得复制到技能目录或输出产物。只读连接必须声明 `access_mode=read-only`；写连接必须声明 `access_mode=controlled-write`、绑定同一测试环境并限定库表白名单，否则立即停止。
