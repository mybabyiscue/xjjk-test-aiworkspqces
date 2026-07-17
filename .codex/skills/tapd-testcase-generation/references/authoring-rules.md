# Authoring Rules (Testcase Generation)

## Testcase Output

`test_cases.md` must contain:
- `# 测试用例`
- `## 一、P0 核心用例`
- `## 二、P1 重要分支和异常用例`
- `## 三、P2 边界兼容和低频用例`

Each case must use a `### TCxxx` heading and include:
- 用例名称
- 用例目录
- 需求ID
- 用例类型
- 用例状态
- 用例等级
- 所属端/角色/系统
- 功能模块
- 前置条件
- 测试步骤
- 预期结果
- 关联需求点
- 备注

Use fine-grained cases. Avoid one case validating unrelated assertions.

Cover success paths, failure paths, boundaries, permissions, state changes, data consistency, external dependencies, idempotency, concurrency, timeout, partial failure, logging, and audit when relevant.

## Questions Output

`questions.md` must contain:
- `# 需求疑问点和阻塞项`
- `## 一、需求疑问点`
- `## 二、阻塞项`
- `## 三、建议补充信息`
- Table header: `| 编号 | 模块 | 疑问点 | 影响 |`

If no questions exist, keep the structure and write `无`.

## TAPD Payload Output

`tapd_cases.json` must include:
- `story.workspace_id`
- `story.id`
- `story.short_id`
- `story.name`
- `cases[]`

Each case must include:
- `title`
- `directory`
- `requirement_id`
- `precondition`
- `steps`
- `expected_results`
- `case_type`
- `case_status`
- `priority`

Allowed `case_type`: `功能测试`, `性能测试`, `安全性测试`.

Allowed `priority`: `P0`, `P1`, `P2`.

`test_cases.md` and `tapd_cases.json` must have the same case count and the same case title order.

## Review Rules

After every generation, show the coverage summary and hand the cases to `tapd-testcase-code-review` for code evidence analysis.

If the user asks to revise the generated cases:
- Ask for concrete feedback.
- Append the feedback to `review_history.md`.
- Regenerate using requirement content, review history, and the experience library.

Do not write `testcase_confirmation.json` and do not update the experience library from this skill. Final approval and knowledge deposition happen only after `tapd-testcase-code-review` produces code evidence and the user explicitly approves the reviewed result.
