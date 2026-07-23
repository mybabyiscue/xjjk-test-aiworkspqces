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
      "headers": {"Authorization": "${authorization}"},
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

核心流程对象包含 `flow_key`、`name`、`case_keys`、非空 `evidence_references` 和至少两个 `steps`。每个步骤复用接口证据、Header、参数、请求体和结构化断言，并额外提供：

- `parameter_dependencies`
- `interrupt_condition`
- `cleanup_steps`

不存在真实调用依赖证据时保持 `core_flows` 为空，并填写 `core_flow_blocker_reason`。

## 覆盖与真实性

- 使用评估壳中的 `case_key`，不得按标题重新排序或重新编号。
- 每个 `case_key` 必须恰好出现于一个 `interface_cases.covered_case_keys` 或一个 `non_interface_cases.case_key`。
- HTTP 状态、响应字段、提示文案和数据库断言必须有需求或代码证据。
- Header 中只能保存变量引用，禁止保存真实 Token。
