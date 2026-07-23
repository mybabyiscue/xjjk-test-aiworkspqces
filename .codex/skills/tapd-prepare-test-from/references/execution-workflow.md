# 执行工作流

从工作区根目录运行全部命令。以下示例使用 PowerShell；将尖括号值替换为用户明确确认的单个 API 环境和数据库连接。

## 1. 前置输入

确认以下文件全部存在：

- `output/test_cases.md`
- `output/tapd_cases.json`
- `output/latest/testcase_confirmation.json`
- `output/code_review/latest/evidence_index.json`
- `output/code_review/latest/related_interfaces.md`
- `output/code_review/latest/related_tables.md`
- `output/code_review/latest/unit_test_interfaces.md`
- `output/code_review/latest/table_information.md`
- `output/code_review/latest/core_process_interfaces.md`
- `output/code_review/latest/source_manifest.json`
- `config/environments_config.json`
- `config/credentials.local.json`
- `.codex/skills/xjjk-yewu-sql/state/connections.json`

不要用根目录下的兼容副本替代 `output/code_review/latest/` 证据。

## 2. 确认输入快照

```powershell
$skillPath = Resolve-Path '.codex/skills/tapd-prepare-test-from'
$preparationPath = 'output/test_preparation'
New-Item -ItemType Directory -Force -Path $preparationPath | Out-Null
python "$skillPath/scripts/validate_confirmed_input.py" `
  --confirmation 'output/latest/testcase_confirmation.json' `
  --test-cases 'output/test_cases.md' `
  --tapd-cases 'output/tapd_cases.json' `
  --evidence-index 'output/code_review/latest/evidence_index.json' `
  --related-interfaces 'output/code_review/latest/related_interfaces.md' `
  --related-tables 'output/code_review/latest/related_tables.md' `
  --interface-evidence 'output/code_review/latest/unit_test_interfaces.md' `
  --table-evidence 'output/code_review/latest/table_information.md' `
  --code-evidence 'output/code_review/latest/source_manifest.json' `
  --environment-name '<用户确认的环境名>' `
  --api-domain '<该环境的 api_domain>' `
  --output "$preparationPath/confirmed_input_snapshot.json"
```

此命令失败时停止。不得跳过哈希、审批或 schema 错误。

## 3. 初始化评估壳

```powershell
python "$skillPath/scripts/initialize_preparation_assessment.py" `
  --snapshot "$preparationPath/confirmed_input_snapshot.json" `
  --tapd-cases 'output/tapd_cases.json' `
  --output "$preparationPath/preparation_assessment_shell.json"
```

## 4. 生成并执行只读查询计划

按照 [assessment-contract.md](assessment-contract.md) 生成 `$preparationPath/query_plan.json`。每个表和字段必须来自 `table_information.md` 或 `related_tables.md`，查询目的必须关联用例。禁止执行未经用户确认数据库平台的查询。

```powershell
python "$skillPath/scripts/execute_read_query_plan.py" `
  --connections '.codex/skills/xjjk-yewu-sql/state/connections.json' `
  --connection-name '<用户确认的只读连接名>' `
  --plan "$preparationPath/query_plan.json" `
  --output "$preparationPath/real_data_records.json" `
  --manifest 'output/test_data_manifest.md'
```

真实查询没有返回正向用例所需记录时，将对应用例标记为 `blocked`，不得构造假记录。

## 5. 生成评估映射

读取评估壳、用例、全部代码审查证据和真实查询记录，按照 [assessment-contract.md](assessment-contract.md) 生成 `$preparationPath/model_mapping.json`。不从 URL 名称猜测 HTTP Method，不新增需求或代码中不存在的断言。

```powershell
python "$skillPath/scripts/build_assessment_from_model.py" `
  --assessment-shell "$preparationPath/preparation_assessment_shell.json" `
  --model-mapping "$preparationPath/model_mapping.json" `
  --real-data "$preparationPath/real_data_records.json" `
  --output "$preparationPath/preparation_assessment.json"
```

## 6. 校验并渲染

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

## 7. 可选执行计划

仅在准备产物要移交第五步接口执行时运行：

```powershell
python "$skillPath/scripts/build_api_execution_plan.py" `
  --assessment "$preparationPath/preparation_assessment.json" `
  --plan "$preparationPath/api_execution_plan.json" `
  --report "$preparationPath/api_execution_plan_report.json"
```

命令返回非零或报告 `ready` 不为 `true` 时，不得调用接口。
