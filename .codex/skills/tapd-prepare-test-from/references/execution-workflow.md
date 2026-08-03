# 执行工作流

从工作区根目录运行全部命令。以下示例使用 PowerShell；将尖括号值替换为用户明确确认的单个 API 环境和数据库连接。

## 1. 前置输入

确认以下文件全部存在：

- `output/test_cases.md`
- `output/tapd_cases.json`
- `output/latest/testcase_confirmation.json`
- `output/code_review/latest/evidence_index.json`
- `output/code_review/latest/unit_test_interfaces.md`
- `output/code_review/latest/table_information.md`
- `output/code_review/latest/core_process_interfaces.md`
- `output/code_review/latest/source_manifest.json`
- `config/environments_config.json`
- `config/connections.json`

不要用根目录下的兼容副本替代 `output/code_review/latest/` 证据。

## 2. Token Gate

用户确认单个 API 环境后执行。脚本只按环境具备的 `token_probe` 或登录字段选择能力，不按名称、域名或业务码分支：

```powershell
$skillPath = Resolve-Path '.codex/skills/tapd-prepare-test-from'
python "$skillPath/scripts/validate_environment_token.py" `
  --config 'config/environments_config.json' `
  --environment-name '<用户确认的环境名>' `
  --request-timeout-seconds 10 `
  --retry-count 3 `
  --browser-timeout-ms 30000
```

此命令失败时停止。不得把 `api_domain` 根地址当作探测端点，不得猜测响应业务码、登录定位信息或 Token 格式。脚本成功续期时只原子更新所选环境的 `authorization`。

## 3. 确认输入快照

```powershell
$skillPath = Resolve-Path '.codex/skills/tapd-prepare-test-from'
$preparationPath = 'output/test_preparation'
New-Item -ItemType Directory -Force -Path $preparationPath | Out-Null
python "$skillPath/scripts/validate_confirmed_input.py" `
  --confirmation 'output/latest/testcase_confirmation.json' `
  --test-cases 'output/test_cases.md' `
  --tapd-cases 'output/tapd_cases.json' `
  --evidence-index 'output/code_review/latest/evidence_index.json' `
  --unit-interface-evidence 'output/code_review/latest/unit_test_interfaces.md' `
  --core-interface-evidence 'output/code_review/latest/core_process_interfaces.md' `
  --table-evidence 'output/code_review/latest/table_information.md' `
  --code-evidence 'output/code_review/latest/source_manifest.json' `
  --environment-name '<用户确认的环境名>' `
  --api-domain '<该环境的 api_domain>' `
  --output "$preparationPath/confirmed_input_snapshot.json"
```

此命令失败时停止。脚本会将三份当前代码审查证据与 `evidence_index.json.artifacts` 逐一核对，并把证据索引本身纳入不可变快照；不得跳过哈希、审批或 schema 错误。

## 4. 初始化评估壳

```powershell
python "$skillPath/scripts/initialize_preparation_assessment.py" `
  --snapshot "$preparationPath/confirmed_input_snapshot.json" `
  --tapd-cases 'output/tapd_cases.json' `
  --output "$preparationPath/preparation_assessment_shell.json"
```

## 5. 生成并执行只读查询计划

按照 [assessment-contract.md](assessment-contract.md) 生成 `$preparationPath/query_plan.json`。每个表和字段必须来自 `table_information.md`，查询目的必须关联用例。禁止执行未经用户确认数据库平台的查询。

```powershell
python "$skillPath/scripts/execute_read_query_plan.py" `
  --connections 'config/connections.json' `
  --connection-name '<用户确认的只读连接名>' `
  --plan "$preparationPath/query_plan.json" `
  --output "$preparationPath/real_data_records.json" `
  --manifest 'output/test_data_manifest.md'
```

真实查询没有返回正向用例所需记录时，禁止构造假记录。按以下顺序处理：

1. 使用有源码证据的真实业务 API 生成 `api_create` setup，并提供对应 HTTP 或受控 SQL cleanup。
2. 没有稳定 API 且直接写入不绕过被测行为时，使用用户另行确认的 `controlled-write` 测试连接生成参数化单条 `sql_insert` setup 和按 `TEST_` 标识清理的 `sql_delete` cleanup。
3. 无法自动创建时输出 `manual_create` 步骤；人工完成后重新运行只读查询，只有查询返回真实记录才能继续。
4. 只有数据无法安全创建、无法清理或缺少接口/表证据时才标记 `blocked`。

禁止任何 Mock、Fake、Stub 或 Mock seed。新增功能测试不得预创建本次要由被测接口创建的目标对象，只准备真实上游依赖；更新、删除和状态流转用例应创建隔离的真实目标对象。

## 6. 生成评估映射

读取评估壳、用例、全部代码审查证据和真实查询记录，按照 [assessment-contract.md](assessment-contract.md) 生成 `$preparationPath/model_mapping.json`。不从 URL 名称猜测 HTTP Method，不新增需求或代码中不存在的断言。

```powershell
python "$skillPath/scripts/build_assessment_from_model.py" `
  --assessment-shell "$preparationPath/preparation_assessment_shell.json" `
  --model-mapping "$preparationPath/model_mapping.json" `
  --real-data "$preparationPath/real_data_records.json" `
  --output "$preparationPath/preparation_assessment.json"
```

## 7. 校验并渲染

```powershell
python "$skillPath/scripts/validate_preparation_assessment.py" `
  --assessment "$preparationPath/preparation_assessment.json" `
  --snapshot "$preparationPath/confirmed_input_snapshot.json" `
  --tapd-cases 'output/tapd_cases.json' `
  --report "$preparationPath/preparation_validation_report.json"
```

只有报告中的 `valid` 为 `true` 才运行：

```powershell
python "$skillPath/scripts/render_three_documents.py" `
  --assessment "$preparationPath/preparation_assessment.json" `
  --snapshot "$preparationPath/confirmed_input_snapshot.json" `
  --output-dir 'output'
```

## 8. 生成唯一执行计划

准备产物要移交第五步接口执行时，直接生成执行器消费的唯一计划：

```powershell
python "$skillPath/scripts/build_api_execution_plan.py" `
  --assessment "$preparationPath/preparation_assessment.json" `
  --plan "output/test_execution/execution_plan.json" `
  --report "$preparationPath/api_execution_plan_report.json"
```

生成器必须把 `preparation_assessment.json` 原始文件 SHA-256、`testcase_hash` 和 `code_review_run_id` 写入计划来源块，并把结构化真实数据 setup/cleanup 写入同一计划。命令返回非零或报告 `ready` 不为 `true` 时，不得调用接口。

第五步必须直接消费该 `execution_plan.json`，并使用同一构建函数从当前 assessment 重建规范计划后完整比较；不得从 Markdown、评估包或聊天上下文生成另一份计划，也不得修补不一致字段。
