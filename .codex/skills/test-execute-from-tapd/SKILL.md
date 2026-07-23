---
name: test-execute-from-tapd
description: 执行由 tapd-prepare-test-from 生成并审核通过的单接口与核心流程测试计划，验证真实 HTTP 响应和只读数据库断言，生成接口报告、流程报告及可追溯数据台账。用于用户要求运行 TAPD 接口测试、执行已准备测试、验证接口与数据库实际变动或生成执行报告时；缺少审批、平台确认、结构化计划或真实数据证据时必须阻断。
---

# 执行 TAPD 接口测试

仅执行经过审批、证据完整且机器可判定的结构化测试计划。不要从 Markdown 猜测 HTTP 方法、接口路径、字段、SQL、租户或测试数据。

## 前置 Gate

按顺序完成以下检查，任一失败立即停止，不生成执行报告：

1. 确认以下文件存在：
   - `output/interface_test_preparation.md`
   - `output/integration_test_flow.md`
   - `output/test_data_manifest.md`
   - `output/test_preparation/preparation_assessment.json`
   - `output/latest/testcase_confirmation.json`
   - `environments_config.json`
2. 校验 `output/latest/testcase_confirmation.json` 的 `approved` 严格等于 `true`。
3. 读取 `environments_config.json`，向用户展示全部平台的 `name` 和 `api_domain`。即使只有一个平台，也必须等待用户明确选择；不得默认选择。
4. 确认准备评估包不存在 `unresolved` 参数，所有接口审核状态允许执行，所有响应和数据库断言均可机器判定。
5. 校验结构化执行计划中的测试用例哈希与审批文件一致。

Token 失效或租户/平台选择有歧义时立即 Halt：

- 执行器返回退出码 `10` 时，向用户索要新 Token。只更新用户明确指定的本地凭证文件，不在源码、计划、日志或报告中写入 Token。
- 平台未确认或出现多个同名候选时，不启动执行器。不得使用权重、列表顺序或历史值自动选择。

## 构建执行计划

读取 [execution-plan-contract.md](references/execution-plan-contract.md)，基于已验证的 `preparation_assessment.json` 生成 `output/test_execution/execution_plan.json`。

计划必须满足：

- HTTP 方法和路径逐项来自 `interface_evidence` 源码证据。
- 正向数据逐项引用准备阶段的真实查询记录；反向值仅来自已审批的 `negative_constructed` 参数。
- Header 中不得保存 Token、Cookie、密码或 Secret。只用 `authorization_header` 声明运行时注入 Token 的 Header 名。
- 数据库断言只能使用带参数的只读 `SELECT`，并明确数据库、表、字段路径、操作符和预期值。
- 核心流程按上游 `core_flows.steps` 顺序展开；跨步骤参数必须声明来源步骤、响应路径和目标路径。
- 不增加自动自愈、数据替换、租户降级、Fallback ID 或业务特例。

若无法从证据构造完整计划，将缺失项写入 `output/questions.md` 并停止。不要运行部分计划。

## 执行

从当前工作区运行 bundled script，不生成第二份临时执行器：

```powershell
python .codex/skills/test-execute-from-tapd/scripts/run_test_execution.py `
  --workspace . `
  --plan output/test_execution/execution_plan.json `
  --confirmation output/latest/testcase_confirmation.json `
  --environment-config environments_config.json `
  --environment-name "<用户确认的平台名称>" `
  --output-dir output `
  --manifest output/test_data_manifest.md
```

执行器必须：

- 对网络错误、HTTP 429 和 5xx 最多执行三次请求，每次重试输出结构化 Warning，最终失败保留状态码和 Response Body。
- 将 401、403 或已声明的 Token 失效业务码识别为退出码 `10`，不得吞错或改写成 500。
- 单接口用例互相独立执行；核心流程任一步失败后立即中止该流程，并将后续步骤标记为未执行。
- 只执行计划登记的 SQL，不改写 SQL，不扫描其他表，不执行写 SQL。
- 对数据库断言实际读取的每一行，追加到 `test_data_manifest.md`，格式严格为 `库名:表名:【JSON】`。
- 对报告中的 Authorization、Cookie、Token、密码和 Secret 统一脱敏。

## 产出

成功完成执行后生成：

- `output/interface_test_execution_report.md`
- `output/core_flow_test_execution_report.md`
- 更新后的 `output/test_data_manifest.md`

报告必须区分 `PASS`、`FAIL`、`EXECUTION_ERROR`、`NOT_EXECUTED`，并记录实际状态码、脱敏请求、Response Body、断言结果、数据库查询来源和流程中断位置。通过率只统计实际执行且产生断言结果的用例。

## 禁止行为

- 不运行未审批用例，不绕过平台确认。
- 不硬编码或推测接口、主键、Token、域名、租户、表、字段和 SQL。
- 不因断言失败自动替换业务数据后重试。
- 不修改请求契约以适配单租户或多租户系统。
- 不将凭证或执行结果提交到远端 Git。
