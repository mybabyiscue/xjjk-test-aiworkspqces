---
name: tapd-prepare-test-from
description: 基于已审批的 TAPD 测试用例、代码审查证据、真实 MySQL 数据和用户确认的测试环境，优先复用现有真实数据，无可用数据时规划真实 API 创建、受控 SQL 写入或人工创建及清理，并生成可追溯执行计划。用于“准备测试数据”“生成接口测试前置条件”“把已审批用例落地为可执行接口测试”或运行五步测试流水线第四步；启动后必须执行用例审批、代码审查批次、API 平台和数据库平台人工确认 Gate，禁止 Mock、Fake、Stub 和 Mock seed。
---

# TAPD 接口测试准备

只生成真实测试数据的查询、创建、验证和清理契约，不执行正式测试，不同步 TAPD。人工创建可在本阶段完成并重新查询确认；自动 HTTP/SQL 写入由第五步严格按防篡改计划执行。

## 必读资源

执行前完整读取：

- [execution-workflow.md](references/execution-workflow.md)：命令顺序、路径和中间产物。
- [assessment-contract.md](references/assessment-contract.md)：模型生成的查询计划和评估数据契约。
- [configuration.md](references/configuration.md)：本地环境与凭证配置契约。

## 硬性 Gate

按顺序执行。任一 Gate 失败时立即停止，不生成最终文档，不做降级替代。

1. **能力 Gate**：确认 Python 项目环境、Playwright 浏览器能力和工作区 `config/connections.json` 数据库连接能力可用。
2. **输入 Gate**：确认 `execution-workflow.md` 列出的全部输入存在。
3. **审批 Gate**：运行 `validate_confirmed_input.py`。要求 `approved` 为 `true`、`test_cases.md` 哈希匹配、代码复审批次匹配且 `tapd_cases.json` 符合正式契约。
4. **API 平台 Gate**：读取 `config/environments_config.json`，展示所有环境的名称和 `api_domain`。即使只有一个环境，也要等待用户明确选择一个；批量准备时按环境分别运行，禁止默认选择或把多个域名合并到一次运行。
5. **数据库平台 Gate**：读取工作区 `config/connections.json` 展示所有已启用连接，只显示名称和非敏感连接标识。等待用户明确选择，禁止根据 API 平台、表名或历史记录猜测。该文件是本独立工作区的唯一数据库连接来源，不读取技能目录或用户目录中的同名注册表。
6. **Token Gate**：按 [configuration.md](references/configuration.md) 探测选定环境。外部请求最多尝试三次，每次失败记录结构化 Warning；401 时按配置使用 Playwright 重登。仍失败、租户歧义或缺少稳定登录定位信息时立即停止并请求用户处理。

## 数据安全

- 优先使用用户确认的只读连接执行单条 `SELECT` 并复用现有真实记录；查不到时不得直接标记 `blocked`，应依次评估真实业务 API、受控 SQL 和人工创建。
- 正向用例只允许真实查询或真实创建的数据；禁止 Mock、Fake、Stub、Mock seed、占位主键和凭空构造字段。
- 仅为有明确需求或代码校验证据的反向用例构造无效值、边界值或越权 ID。
- 自动创建优先使用有源码证据的真实业务 API。无稳定 API 且不绕过被测行为时，允许用户单独确认的 `controlled-write` 测试连接执行显式列、参数化单条 `INSERT`；清理只允许按 `TEST_` 标识精确或前缀匹配的参数化单条 `DELETE`。
- 禁止 `UPDATE`、DDL、存储过程、`TRUNCATE`、无界 `DELETE`、文件导出、锁操作、注释 SQL 和生产环境写入。
- 每个自动创建动作必须有一一对应的清理动作；测试失败、Token 失效或部分准备失败时也必须反向清理。清理失败必须登记残留数据并返回失败。
- 将 API Token、账号和密码仅保存到 `config/credentials.local.json`；数据库连接凭证仅保存到已被 Git 忽略的 `config/connections.json`。禁止写入技能目录、Markdown、JSON 中间产物、日志或 Git 跟踪文件。
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
4. 按“复用 -> 真实 API -> 受控 SQL -> 人工创建后复查”的顺序生成 `data_preparation` 和 `model_mapping.json`。新增功能只准备真实上游依赖，不预创建被测目标对象；更新、删除和状态流转用例可先创建真实目标对象。
5. 合并并校验 `preparation_assessment.json`。
6. 仅在校验报告 `valid` 为 `true` 时渲染最终文档。
7. 需要交给第五步执行时，生成唯一的 `output/test_execution/execution_plan.json`，写入 assessment SHA-256、用例哈希、代码复审批次以及结构化 setup/cleanup；第五步直接消费并按当前 assessment 规范重建比较，不得重新生成或修补计划。存在阻断项时不得执行接口。

## 最终产物

只在全部 Gate 和评估校验通过后生成：

- `output/interface_test_preparation.md`
- `output/non_interface_cases.md`
- `output/integration_test_flow.md`
- `output/test_data_manifest.md`

所有中间 JSON 和校验报告写入 `output/test_preparation/`。完成后报告所选平台、所选只读连接、需要时另行确认的受控写连接、用例覆盖数量、阻断数量和产物路径；不得报告 Token 或密码。

`output/test_execution/execution_plan.json` 是准备阶段移交执行阶段的唯一例外，它是正式执行输入，不属于临时中间产物。
