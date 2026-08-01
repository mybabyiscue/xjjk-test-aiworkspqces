# 评估数据契约

模型只负责基于证据生成结构化中间数据。脚本负责校验、合并和渲染。

## 查询计划

`query_plan.json`：

```json
{
  "connection": "用户确认的连接名",
  "queries": [
    {
      "query_reference": "QRY_UNIQUE_NAME",
      "database": "真实库名",
      "table": "真实表名",
      "purpose": "关联用例和取值目的",
      "sql": "SELECT required_columns FROM real_database.real_table WHERE evidence_backed_filter LIMIT 20"
    }
  ]
}
```

每条 SQL 必须是无注释、无分号的单条 `SELECT`。禁止 `SELECT *`，只选择请求参数或断言需要的列，并使用限制返回数量的条件。

## 模型映射

`model_mapping.json` 的根结构固定为：

```json
{
  "data_preparation": {"entries": []},
  "interface_cases": [],
  "non_interface_cases": [],
  "core_flows": [],
  "core_flow_blocker_reason": "没有核心流程时填写证据不足原因；存在流程时为空字符串"
}
```

### 接口用例组

```json
{
  "interface_key": "稳定唯一键",
  "interface_evidence": {
    "service": "服务名",
    "controller_file": "Controller.java",
    "controller_method": "methodName",
    "http_method": "POST",
    "path": "/完整网关路径"
  },
  "covered_case_keys": ["case_001"],
  "request_variants": [
    {
      "name": "TC001 - 用例标题",
      "variant_type": "positive",
      "case_keys": ["case_001"],
      "validation_evidence": [],
      "headers": {"Content-Type": "application/json"},
      "authorization_header": "Authorization",
      "query": {},
      "parameters": [
        {
          "name": "id",
          "type": "Long",
          "required": true,
          "value": 1,
          "source_type": "database",
          "source_reference": "table_information.md 对应字段",
          "query_reference": "QRY_UNIQUE_NAME"
        }
      ],
      "request_body": {"id": 1},
      "expected": {
        "http_status": 200,
        "response_assertions": [
          {"path": "$.code", "operator": "equals", "value": "00000"}
        ],
        "database_assertions": []
      },
      "setup_steps": [],
      "cleanup_steps": []
    }
  ],
  "negative_variant_policy": "no_verifiable_validation_rule",
  "negative_variant_evidence": ["代码和需求未定义可验证拒绝规则"],
  "audit": {
    "status": "可审核",
    "evidence_status": "接口、用例和真实数据已绑定",
    "reason": "说明证据链",
    "reviewer": "Codex",
    "reviewed_at": "实际 ISO-8601 时间"
  }
}
```

`source_type` 只能是 `database`、`upstream_response`、`protocol_constant`、`negative_constructed` 或 `unresolved`。可执行接口中禁止 `unresolved`。`database` 必须引用 `real_data_records.json` 中存在的 `query_reference`。

反向变体必须提供非空 `validation_evidence`。没有明确反向规则时使用 `no_verifiable_validation_rule`，不得自行设计拦截断言。

### 不可接口测试用例

```json
{
  "case_key": "case_002",
  "title": "用例标题",
  "classification": "ui_only",
  "reason": "无法通过接口验证的证据原因",
  "recommended_test_type": "E2E",
  "precondition": "真实前置条件",
  "steps": ["步骤"],
  "expected_results": ["预期结果"],
  "related_interfaces": [],
  "parameter_data": [],
  "missing_evidence": [],
  "audit": {
    "status": "可审核",
    "evidence_status": "已分类",
    "reason": "说明依据",
    "reviewer": "Codex",
    "reviewed_at": "实际 ISO-8601 时间"
  }
}
```

`classification` 只能是 `ui_only` 或 `blocked`。`blocked` 必须填写 `missing_evidence`。

### 核心流程

核心流程对象包含 `flow_key`、`name`、`case_keys`、非空 `evidence_references` 和至少两个 `steps`。每个步骤复用接口证据、Header、授权 Header、查询参数、参数、请求体和结构化断言，并额外提供：

- `step_key`：流程内唯一且稳定的步骤键
- `case_keys`
- `variant_type`
- `parameter_dependencies`
- `interrupt_condition`
- `cleanup_steps`

`parameter_dependencies` 每项必须包含 `source_step`、`source_path`、`target` 和 `target_path`。`source_step` 只能引用更早的 `step_key`；`target` 只能是 `body` 或 `query`。

不存在真实调用依赖证据时保持 `core_flows` 为空，并填写 `core_flow_blocker_reason`。

## 真实数据准备

评估根对象必须包含 `data_preparation.entries`。每个需要真实数据的用例按以下策略登记：

```json
{
  "data_preparation": {
    "entries": [
      {
        "id": "target_resource",
        "case_keys": ["case_001"],
        "strategy": "api_create",
        "evidence_references": ["unit_test_interfaces.md#真实创建接口"],
        "verification_query_reference": "QRY_TARGET_RESOURCE",
        "isolation_prefix": "TEST_REQ_",
        "setup": {
          "id": "create_target_resource",
          "type": "http",
          "evidence_reference": "Controller.java#create",
          "method": "POST",
          "path": "/gateway/resource/create",
          "headers": {"Content-Type": "application/json"},
          "authorization_header": "Authorization",
          "query": {},
          "body": {"name": "TEST_REQ_RESOURCE_001"},
          "expected": {
            "http_status": 200,
            "response_assertions": [{"path": "$.code", "operator": "equals", "value": 0}]
          },
          "manifest": {
            "database": "test_database",
            "table": "resource",
            "record": {"name": "TEST_REQ_RESOURCE_001"}
          }
        },
        "cleanup": {
          "id": "delete_target_resource",
          "type": "sql_delete",
          "evidence_reference": "table_information.md#resource.test_code",
          "database": "test_database",
          "table": "resource",
          "sql": "DELETE FROM test_database.resource WHERE test_code = %s",
          "parameters": ["TEST_REQ_RESOURCE_001"],
          "expected_affected_rows": 1,
          "manifest": {
            "database": "test_database",
            "table": "resource",
            "record": {"test_code": "TEST_REQ_RESOURCE_001"}
          }
        }
      }
    ]
  }
}
```

`strategy` 只允许：

- `reuse`：只复用只读查询已返回的真实记录，`setup` 和 `cleanup` 必须为 `null`。
- `api_create`：使用有源码证据的真实业务 API，必须提供 setup 和 cleanup。
- `sql_insert`：无稳定 API 且不绕过被测行为时使用受控写连接，setup 只允许显式列、参数化单条 `INSERT`，cleanup 只允许单一 `TEST_` 标识的参数化 `DELETE`。
- `manual_create`：人工完成后必须重新只读查询；`verification_query_reference` 对应记录数大于 0 才能继续，`setup` 和 `cleanup` 为 `null`。

禁止 Mock、Fake、Stub、Mock seed、`UPDATE`、DDL、存储过程、`TRUNCATE` 和无界 `DELETE`。自动创建策略的 `isolation_prefix` 必须以 `TEST_` 开头，setup/cleanup ID 必须全局唯一且一一对应。

## 覆盖与真实性

- 使用评估壳中的 `case_key`，不得按标题重新排序或重新编号。
- 每个 `case_key` 必须恰好出现于一个 `interface_cases.covered_case_keys` 或一个 `non_interface_cases.case_key`。
- HTTP 状态、响应字段、提示文案和数据库断言必须有需求或代码证据。
- `headers` 中禁止保存 Authorization、Cookie、Token 或其他敏感 Header；需要运行时注入 Token 时只填写 `authorization_header` 的 Header 名称，不需要鉴权时填写空字符串。
- 查询参数必须明确写入 `query`，禁止根据 `parameters` 或 HTTP Method 推断参数位置。
