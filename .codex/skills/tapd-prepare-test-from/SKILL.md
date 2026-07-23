---
name: tapd-prepare-test-from
description: 基于已审批的 TAPD 测试用例、代码审查证据、真实只读 MySQL 数据和用户确认的测试环境，生成接口测试准备文档、不可接口测试用例、集成流程及测试数据台账。用于“准备测试数据”“生成接口测试前置条件”“把已审批用例落地为可执行接口测试”或运行五步测试流水线第四步；启动后必须执行用例审批、代码审查批次、API 平台和数据库平台人工确认 Gate。
---

# TAPD 接口测试准备

只准备测试数据和可执行测试契约，不执行接口测试，不同步 TAPD，不修改业务数据。

## 必读资源

执行前完整读取：

- [execution-workflow.md](references/execution-workflow.md)：命令顺序、路径和中间产物。
- [assessment-contract.md](references/assessment-contract.md)：模型生成的查询计划和评估数据契约。
- [configuration.md](references/configuration.md)：本地环境与凭证配置契约。

## 硬性 Gate

按顺序执行。任一 Gate 失败时立即停止，不生成最终文档，不做降级替代。

1. **能力 Gate**：确认 Python 项目环境、Playwright 浏览器能力和 `xjjk-yewu-sql` 数据库连接能力可用。
2. **输入 Gate**：确认 `execution-workflow.md` 列出的全部输入存在。
3. **审批 Gate**：运行 `validate_confirmed_input.py`。要求 `approved` 为 `true`、`test_cases.md` 哈希匹配、代码复审批次匹配且 `tapd_cases.json` 符合正式契约。
4. **API 平台 Gate**：读取 `config/environments_config.json`，展示所有环境的名称和 `api_domain`。即使只有一个环境，也要等待用户明确选择一个；批量准备时按环境分别运行，禁止默认选择或把多个域名合并到一次运行。
5. **数据库平台 Gate**：使用 `xjjk-yewu-sql` 展示所有已启用连接，只显示名称和非敏感连接标识。等待用户明确选择，禁止根据 API 平台、表名或历史记录猜测。
6. **Token Gate**：按 [configuration.md](references/configuration.md) 探测选定环境。外部请求最多尝试三次，每次失败记录结构化 Warning；401 时按配置使用 Playwright 重登。仍失败、租户歧义或缺少稳定登录定位信息时立即停止并请求用户处理。

## 数据安全

- 只使用用户确认的只读数据库连接，只执行经过校验的单条 `SELECT`。
- 正向用例必须使用真实查询记录；禁止 Mock、占位主键和凭空构造字段。
- 仅为有明确需求或代码校验证据的反向用例构造无效值、边界值或越权 ID。
- 禁止执行 `INSERT`、`UPDATE`、`DELETE`、DDL、存储过程、文件导出、锁操作或带注释的 SQL。
- 将 Token、账号和密码仅保存到 `config/credentials.local.json`。禁止写入技能目录、Markdown、JSON 中间产物、日志或 Git 跟踪文件。
- 文档中的敏感 Header 必须显示为 `***`。
- 将每条真实查询结果按 `库名:表名:【JSON】` 写入 `output/test_data_manifest.md`。

## 证据规则

- HTTP Method 只能来自控制器注解证据。
- 请求路径必须使用代码审查产物中的完整网关路径。
- DTO 字段、表名、列名和数据库断言只能来自代码审查与物理元数据。
- 每条用例必须恰好归入一个接口组或不可接口测试组。
- 缺少证据时将用例标记为 `blocked` 并说明缺失项；不得补写推测结论。
- 只有存在真实代码依赖证据时才生成核心集成流程，否则写明 `core_flow_blocker_reason`。

## 执行

严格执行 [execution-workflow.md](references/execution-workflow.md) 中的命令，不直接手写最终文档：

1. 校验确认文件并生成不可变输入快照。
2. 初始化评估壳。
3. 从已确认的表证据生成只读查询计划并执行真实查询。
4. 根据用例、接口证据、表证据和真实查询结果生成 `model_mapping.json`。
5. 合并并校验 `preparation_assessment.json`。
6. 仅在校验报告 `valid` 为 `true` 时渲染最终文档。
7. 需要交给第五步执行时，再生成 `api_execution_plan.json`；存在阻断项时不得执行接口。

## 最终产物

只在全部 Gate 和评估校验通过后生成：

- `output/interface_test_preparation.md`
- `output/non_interface_cases.md`
- `output/integration_test_flow.md`
- `output/test_data_manifest.md`

所有中间 JSON 和校验报告写入 `output/test_preparation/`。完成后报告所选平台、所选只读连接、用例覆盖数量、阻断数量和产物路径；不得报告 Token 或密码。
