---
name: tapd-testcase-generation
description: 读取已通过需求分析的 output/requirement.md，执行输入门禁、需求疑问点隔离、BLAST 测试点矩阵规划和 BDD Given-When-Then 用例生成，输出 test_cases.md、questions.md 与 tapd_cases.json。用于 TAPD 需求完成质量审计后生成测试用例，或结合 review_history.md 修订用例；不用于需求分析、代码审查、数据库查询、TAPD 同步或最终审批。
---

# TAPD 测试用例生成

## 核心原则

- 只基于 `output/requirement.md` 中的原文证据、BDD 验收标准和用户已确认信息生成断言。
- 不推测 HTTP Method、接口字段、数据库字段、提示文案、状态码、锁机制、缓存策略或第三方降级行为。
- 一个用例只覆盖一个独立测试目的和一个 Given-When-Then 闭环；允许在同一闭环中列出直接相关的多个可观察结果。
- 将信息不足、相互矛盾或尚未确认的场景写入 `output/questions.md`，不得替产品经理作决定。
- 不查询数据库，不读取业务源码，不上传 TAPD，不创建 `testcase_confirmation.json`，不修改知识库经验条目。

开始执行前，完整读取：

- [BLAST 执行协议](references/blast-protocol.md)
- [用例与产物契约](references/authoring-rules.md)

## 输入与硬性门禁

### 必需输入

- `output/requirement.md`

### 可选输入

- `output/review_history.md`
- `knowledge/index.json`

### 门禁检查

按顺序执行以下检查，任一检查失败时立即停止，不生成或覆盖任何用例产物：

1. 确认 `output/requirement.md` 存在、可读且非空。
2. 确认包含需求来源、需求基础信息、需求质量评估、核心功能点、关键业务流程、BDD 验收标准和需求疑问点。
3. 确认质量得分存在且可解析。若文档带有低于 80 分或关键缺陷的放行警告，只能为证据充分的功能点生成用例，其余内容转入 `questions.md`。
4. 确认来源类型为 TAPD，并能从需求文档中的真实 TAPD 来源信息取得 `workspace_id`、完整需求 `id`、需求 `short_id` 和原始需求标题。缺失任何标识时停止，不得构造占位值。
5. 确认 BDD 章节不是整体“未提供”。若没有任何可断言的验收标准，停止并报告缺失信息。
6. 读取第十四章需求疑问点。疑问涉及的功能点不得生成断言，除非文档或用户已明确销号并记录结论。

失败信息必须包含缺失或非法项目、输入路径、发现的实际内容以及可执行修复建议。

## 知识库加载

1. 若工作区不存在 `knowledge/index.json`，将本技能 `resources/knowledge_seeds/` 中的种子索引和经验文件复制到工作区 `knowledge/`，并告知用户已初始化。
2. 若索引存在，验证其为合法 JSON 对象且 `entries` 为数组。
3. 只读取关键词命中的经验文件。经验只能补充测试设计方法，不能成为业务规则、提示文案或技术实现的证据。
4. 索引或命中文件非法时明确失败，不静默跳过。

## 唯一执行流程

### 1. 建立证据清单

- 提取需求标识、原始标题、质量得分、功能点、角色、业务规则、主流程、异常流程、边界条件、BDD 验收标准和疑问点。
- 为每个候选测试点记录其需求章节或 BDD 场景来源。
- 将没有直接证据支持的候选场景移入 `questions.md`。

### 2. 生成 BLAST 测试点矩阵

- 按 `references/blast-protocol.md` 生成原子测试点矩阵。
- 识别实际受影响层级：UI、API/业务逻辑、第三方集成、数据迁移、回归、安全隔离、观测性。
- 仅激活需求证据明确涉及的层级。
- 在对话中声明复杂等级：模块/系统级、功能级或修补/微调级。数量区间只用于评估，不作为凑数指标。

### 3. 生成三个产物

严格按 `references/authoring-rules.md` 生成：

- `output/test_cases.md`
- `output/questions.md`
- `output/tapd_cases.json`

同时生成 `output/agent2_prompt.md`，记录输入路径、输入摘要、质量门禁结果、复杂等级、已加载经验文件和生成时间。不得写入凭证或需求正文之外的推断。

### 4. 分级

- Happy Path 默认 P0。
- Alternative/Error 默认 P1。
- Edge Cases/Compatibility 默认 P2。
- 资金、权限或越权、数据一致性相关场景一律为 P0，并在备注中写明上浮原因。
- 不得仅因用例数量分布不均而调整优先级。

### 5. 确定性校验

从工作区根目录执行：

```powershell
python .codex/skills/tapd-testcase-generation/scripts/validate_outputs.py output
```

校验失败时，根据具体错误修改产物后重试，最多重试 2 次。第 3 次仍失败时停止，报告失败字段和用例编号，并将无法自动修正的需求问题写入 `questions.md`。不得降低校验标准或删除有效测试点以通过校验。

### 6. 展示摘要并移交

展示以下信息：

- P0、P1、P2 数量；
- Happy Path、Alternative/Error、Edge Cases、Compatibility 覆盖数量；
- 需求功能点覆盖数、总数和未覆盖功能点；
- `questions.md` 中各问题类型数量；
- 输出校验结果。

标记用例为“待代码证据复查”，下一步移交 `tapd-code-source-review`。该技能完成代码证据审查并获得用户明确批准后，才可生成 `output/latest/testcase_confirmation.json` 和沉淀知识。

## 修订用例

用户要求修订时：

1. 要求或读取明确的被拒绝用例、原因和期望方向。
2. 按 `references/authoring-rules.md` 追加到 `output/review_history.md`。
3. 重新读取需求、评审历史和命中的经验文件。
4. 重新生成三个产物并执行确定性校验。
5. 不重复已记录的相同错误。

## 完成条件

- 输入门禁通过，所有测试点均可追溯到需求证据。
- 疑问范围与已确认范围严格隔离。
- 三个产物符合唯一契约并通过 `validate_outputs.py`。
- Markdown 与 JSON 的用例编号、数量、标题顺序、优先级和核心字段一致。
- 已展示覆盖摘要并明确移交 `tapd-code-source-review`。
- 未执行数据库查询、源码推断、TAPD 同步、最终审批或知识沉淀。
