# 代码源初步审查结果

## 问题清单

### 1. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\brainstorming\SKILL.md
- 行号：18
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`Every project goes through this process. A todo list, a single-function utility, a config change — all of them. "Simple" projects are where unexamined assumptions cause the most wasted work. The design can be short (a few sentences for trul`

### 2. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\brainstorming\SKILL.md
- 行号：114
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`1. **Placeholder scan:** Any "TBD", "TODO", incomplete sections, or vague requirements? Fix them.`

### 3. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\dev-diagnosis-feedback-loop\SKILL.md
- 行号：73
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`4. temporary harness that drives the affected method or service path`

### 4. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\dev-diagnosis-feedback-loop\SKILL.md
- 行号：80
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`debug against and record the rate.`

### 5. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\dev-diagnosis-feedback-loop\SKILL.md
- 行号：86
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`- approval for temporary diagnostic instrumentation`

### 6. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\dev-diagnosis-feedback-loop\SKILL.md
- 行号：97
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`6. Use a unique debug prefix, for example `[DEBUG-abc123]`.`

### 7. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\dev-diagnosis-feedback-loop\SKILL.md
- 行号：120
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`- remove all temporary debug instrumentation`

### 8. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\dev-diagnosis-feedback-loop\SKILL.md
- 行号：121
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`- grep for the debug prefix and confirm no stray logs remain`

### 9. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\dev-service-implement-from-change\SKILL.md
- 行号：253
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`2. 信号优先级：单元 / 集成测试 → service/API 脚本 → trace replay → 临时 harness → 浏览器自动化 → flaky stress loop → 结构化人工复现记录`

### 10. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\dev-service-implement-from-change\SKILL.md
- 行号：256
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`5. 一次只验证一个假设；需要日志时必须使用唯一前缀，例如 `[DEBUG-abc123]``

### 11. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\dev-service-implement-from-change\SKILL.md
- 行号：259
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`8. 结束前 grep 调试前缀并移除临时 instrumentation；临时 harness 要么删除，要么升级为明确命名的测试资产`

### 12. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\dev-service-implement-from-change\SKILL.md
- 行号：276
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`- 临时 instrumentation 前缀（如有）`

### 13. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\dev-service-implementation-design-from-change\SKILL.md
- 行号：451
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`- 使用 `TODO` / `TBD` / "视情况而定"`

### 14. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\dev-service-implementation-design-from-change\SKILL.md
- 行号：603
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`- 没有 `TODO` / `TBD` / 未解释的待确认项`

### 15. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\dev-service-implementation-design-from-change\SKILL.md
- 行号：705
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`- 不允许带着关键 `TODO` 进入实现`

### 16. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\requesting-code-review\code-reviewer.md
- 行号：35
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`Your review is read-only on this checkout. Do not mutate the working tree, the index, HEAD, or branch state in any way. Use tools like `git show`, `git diff`, and `git log` to inspect history. If you need a working copy of a different revis`

### 17. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\subagent-driven-development\SKILL.md
- 行号：60
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`"Mark task complete in todo list and progress ledger" [shape=box];`

### 18. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\subagent-driven-development\SKILL.md
- 行号：77
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`"Task reviewer reports spec ✅ and quality approved?" -> "Mark task complete in todo list and progress ledger" [label="yes"];`

### 19. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\subagent-driven-development\SKILL.md
- 行号：78
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`"Mark task complete in todo list and progress ledger" -> "More tasks remain?";`

### 20. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\systematic-debugging\defense-in-depth.md
- 行号：18
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`- Debug logging helps when other layers fail`

### 21. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\systematic-debugging\defense-in-depth.md
- 行号：72
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`### Layer 4: Debug Instrumentation`

### 22. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\systematic-debugging\defense-in-depth.md
- 行号：78
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`logger.debug('About to git init', {`

### 23. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\systematic-debugging\defense-in-depth.md
- 行号：93
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`3. **Add validation at each layer** - Entry, business, environment, debug`

### 24. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\systematic-debugging\defense-in-depth.md
- 行号：120
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`- Debug logging identified structural misuse`

### 25. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\systematic-debugging\root-cause-tracing.md
- 行号：74
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`console.error('DEBUG git init:', {`

### 26. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\systematic-debugging\root-cause-tracing.md
- 行号：89
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`npm test 2>&1 | grep 'DEBUG git init'`

### 27. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\systematic-debugging\test-pressure-2.md
- 行号：22
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`5. Added debug logging - shows payment processes, status not updating`

### 28. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\systematic-debugging\test-pressure-2.md
- 行号：39
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`- Add comment: "TODO: investigate why status update is slow"`

### 29. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\using-superpowers\SKILL.md
- 行号：24
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`Then announce "Using [skill] to [purpose]" and follow the skill exactly. If it has a checklist, create a todo per item.`

### 30. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\using-superpowers\references\antigravity-tools.md
- 行号：3
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`Skills speak in actions ("dispatch a subagent", "create a todo", "read a file"). On the Antigravity CLI (`agy`) these resolve to the tools below.`

### 31. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\using-superpowers\references\antigravity-tools.md
- 行号：8
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`| Task tracking ("create a todo", "mark complete") | a **task artifact** — `write_to_file` with `IsArtifact: true` and `ArtifactType: "task"` (see [Task tracking](#task-tracking)). **Not** `manage_task`, which manages background processes. `

### 32. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\using-superpowers\references\antigravity-tools.md
- 行号：12
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`Antigravity has **no todo tool** (`manage_task` manages background`

### 33. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\using-superpowers\references\antigravity-tools.md
- 行号：14
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`skill says to create a todo list or track tasks, maintain a **task artifact**: a`

### 34. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\using-superpowers\references\pi-tools.md
- 行号：3
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`Skills speak in actions ("dispatch a subagent", "create a todo", "read a file"). On Pi these resolve to the tools below.`

### 35. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\using-superpowers\references\pi-tools.md
- 行号：8
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`| Task tracking ("create a todo", "mark complete") | Use an installed todo/task tool if available, otherwise track tasks in the plan or `TODO.md` |`

### 36. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\using-superpowers\references\pi-tools.md
- 行号：16
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`Pi core does not ship a standard task-list tool. If a todo/task extension is installed, use its documented tool. Otherwise use Superpowers plan files, checklists in Markdown, or a repo-local `TODO.md` for task tracking. Older Superpowers do`

### 37. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\writing-plans\SKILL.md
- 行号：131
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`- "TBD", "TODO", "implement later", "fill in details"`

### 38. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\writing-skills\persuasion-principles.md
- 行号：83
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`✅ Checklists without todo tracking = steps get skipped. Every time.`

### 39. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\writing-skills\persuasion-principles.md
- 行号：84
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`❌ Some people find a todo list helpful for checklists.`

### 40. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\writing-skills\SKILL.md
- 行号：629
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`**IMPORTANT: Create a todo for EACH checklist item below.**`

### 41. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\.codex\skills\writing-skills\examples\CLAUDE_MD_TESTING.md
- 行号：12
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`You need to debug a failing authentication service.`

### 42. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\openspec\changes\prd-20260615-group-course-link-attribution\implementation-card.md
- 行号：130
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`- 临时 instrumentation：无。`

### 43. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\openspec\changes\prd-20260701-private-live-view-reward-limit\implementation-card.md
- 行号：65
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`- 临时 instrumentation：无。`

### 44. [P1] 疑似敏感信息硬编码

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\constants\RedisConstants.java
- 行号：157
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`public static final String FEI_SHU_TENANT_ACCESS_TOKEN = \"***\";`

### 45. [P1] 疑似拼接 SQL

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\dao\live\LiveJoinExitStatisticsMapper.java
- 行号：64
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`select sum(viewing_duration_seconds+record_duration_seconds) from live_join_exit_statistics`

### 46. [P1] 疑似拼接 SQL

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\dao\live\LiveJoinExitStatisticsMapper.java
- 行号：84
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`select sum(viewing_duration_seconds+record_duration_seconds) from live_join_exit_statistics`

### 47. [P2] 疑似敏感日志输出

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\feign\service\FeiShuFeignService.java
- 行号：63
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`log.info("飞书tenant_access_token命中缓存, accountId: {}, appId: {}", accountId, appId);`

### 48. [P2] 疑似敏感日志输出

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\feign\service\FeiShuFeignService.java
- 行号：136
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`log.info("开始调用飞书tenant_access_token接口, appId: {}", appId);`

### 49. [P2] 疑似敏感日志输出

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\feign\service\FeiShuFeignService.java
- 行号：140
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`log.error("调用飞书tenant_access_token接口失败, appId: {}", appId, e);`

### 50. [P2] 疑似敏感日志输出

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\feign\service\FeiShuFeignService.java
- 行号：147
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`log.info("飞书tenant_access_token接口返回, appId: {}, code: {}, msg: {}, expire: {}",`

### 51. [P2] 疑似敏感日志输出

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\feign\service\FeiShuFeignService.java
- 行号：151
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`log.info("获取飞书tenant_access_token失败, appId: {}, code: {}, msg: {}",`

### 52. [P2] 疑似敏感日志输出

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\feign\service\FeiShuFeignService.java
- 行号：232
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`log.info("开始调用飞书新建文件夹接口, name: {}, parentFolderToken: {}",`

### 53. [P2] 疑似敏感日志输出

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\feign\service\FeiShuFeignService.java
- 行号：244
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`log.info("飞书新建文件夹接口返回, name: {}, code: {}, msg: {}, folderToken: {}",`

### 54. [P2] 疑似敏感日志输出

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\feign\service\FeiShuFeignService.java
- 行号：320
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`log.info("开始调用飞书删除文件夹接口, folderToken: {}", folderToken);`

### 55. [P1] 疑似敏感信息硬编码

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\feign\service\FeiShuFeignService.java
- 行号：323
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`throwIfRateLimited("删除文件夹", "folderToken=" + folderToken, e);`

### 56. [P2] 疑似敏感日志输出

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\feign\service\FeiShuFeignService.java
- 行号：324
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`log.warn("调用飞书删除文件夹接口失败, folderToken: {}", folderToken, e);`

### 57. [P2] 疑似敏感日志输出

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\feign\service\FeiShuFeignService.java
- 行号：331
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`log.info("飞书删除文件夹接口返回, folderToken: {}, code: {}, msg: {}",`

### 58. [P1] 疑似敏感信息硬编码

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\feign\service\FeiShuFeignService.java
- 行号：334
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`throwIfRateLimited("删除文件夹", "folderToken=" + folderToken, response.getCode(), response.getMsg());`

### 59. [P2] 疑似敏感日志输出

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\feign\service\FeiShuFeignService.java
- 行号：556
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`log.info("开始调用飞书更新云文档权限接口, token: {}, type: {}, externalAccessEntity: {}, linkShareEntity: {}",`

### 60. [P1] 疑似敏感信息硬编码

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\feign\service\FeiShuFeignService.java
- 行号：560
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`throwIfRateLimited("更新云文档权限", "token=\"***\", type=" + type, e);`

### 61. [P2] 疑似敏感日志输出

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\feign\service\FeiShuFeignService.java
- 行号：561
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`log.warn("调用飞书更新云文档权限接口失败, token: {}, type: {}", token, type, e);`

### 62. [P2] 疑似敏感日志输出

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\feign\service\FeiShuFeignService.java
- 行号：568
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`log.info("飞书更新云文档权限接口返回, token: {}, type: {}, code: {}, msg: {}",`

### 63. [P1] 疑似敏感信息硬编码

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\feign\service\FeiShuFeignService.java
- 行号：571
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`throwIfRateLimited("更新云文档权限", "token=\"***\", type=" + type,`

### 64. [P2] 疑似敏感日志输出

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\feign\service\FeiShuFeignService.java
- 行号：573
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`log.info("更新飞书云文档权限失败, token: {}, type: {}, code: {}, msg: {}",`

### 65. [P2] 疑似敏感日志输出

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\feign\service\UserFeignService.java
- 行号：125
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`//        log.info("当前token用户信息：{}",currentUserDTO);`

### 66. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\model\dto\live\TrendQueryDTO.java
- 行号：25
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`//todo 待删除`

### 67. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\mq\listener\AbstractRocketMQListener.java
- 行号：26
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`log.debug("MQ ProcessorListener: {}", messageStr);`

### 68. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\mq\util\RocketMqUtil.java
- 行号：41
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`log.debug("sendAsyncMsg 发送成功: {}", sendResult);`

### 69. [P1] 疑似拼接 SQL

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\service\column\impl\SpecialColumnAdminServiceImpl.java
- 行号：837
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`String chapterSql = "SELECT id FROM special_column_chapter WHERE tenant_id = " + currentTenantId()`

### 70. [P1] 疑似拼接 SQL

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\service\column\impl\SpecialColumnAdminServiceImpl.java
- 行号：843
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`String chapterSql = "SELECT id FROM special_column_chapter WHERE tenant_id = " + currentTenantId()`

### 71. [P1] 疑似拼接 SQL

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\service\live\impl\LiveStatisticsOverviewServiceImpl.java
- 行号：584
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`System.err.println("Failed to delete temp file: " + tempFile);`

### 72. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\service\project\course\impl\ProjectRedPackageAccountServiceImpl.java
- 行号：137
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`//        // todo privilegeService  createSourceDTO`

### 73. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\service\project\course\impl\ProjectRedPackageAccountServiceImpl.java
- 行号：149
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`////          todo orgPageInfo`

### 74. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\service\project\course\impl\ProjectRedPackageAccountServiceImpl.java
- 行号：188
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`////        todo`

### 75. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\service\project\course\impl\ProjectRedPackageAccountServiceImpl.java
- 行号：255
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`////            todo`

### 76. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\service\project\course\impl\ProjectRedPackageAccountServiceImpl.java
- 行号：281
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`//            // todo`

### 77. [P2] 疑似敏感日志输出

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\service\project\course\impl\ProjectWxWorkRelationWxProgramServiceImpl.java
- 行号：764
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`log.info("飞书看课文件夹创建成功, tenantId={}, appId={}, folderId={}, folderName={}, parentId={}, level={}, folderToken={}",`

### 78. [P2] 疑似敏感日志输出

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\service\project\course\impl\ProjectWxWorkRelationWxProgramServiceImpl.java
- 行号：1290
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`log.info("飞书文档创建 feiShuAccountId：{}，folderToken：{} start", feiShuAccountId, folderToken);`

### 79. [P2] 疑似敏感日志输出

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\service\project\course\impl\ProjectWxWorkRelationWxProgramServiceImpl.java
- 行号：1310
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`log.info("飞书文档创建 feiShuAccountId：{}，folderToken：{} end", feiShuAccountId, folderToken);`

### 80. [P2] 存在 TODO/FIXME/临时代码

- 服务：course / course
- 文件：output\code_sources\cache\course\src\main\java\com\mall4j\cloud\course\utils\RedisLock.java
- 行号：180
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`log.debug("【Redis分布式锁】解锁失败（锁已过期/非当前线程持有），key={}, 唯一值={}", key, uniqueLockValue);`

### 81. [P2] 存在 TODO/FIXME/临时代码

- 服务：operations / operations
- 文件：output\code_sources\cache\operations\PROJECT-CAPABILITY-INDEX.md
- 行号：39
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`| `shopMange` | `/shopMange` | `apps/web-ele/src/views/_core/authentication/shopInfo.vue` | 登录后租户选择 | 临时 token | `shell-access` | implemented |`

### 82. [P2] 存在 TODO/FIXME/临时代码

- 服务：operations / operations
- 文件：output\code_sources\cache\operations\PROJECT-CAPABILITY-INDEX.md
- 行号：143
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`| 租户选择 | 店铺 / 租户选择 | `/shopMange` | 临时 token | 登录后或切换租户进入 |`

### 83. [P2] 存在 TODO/FIXME/临时代码

- 服务：operations / operations
- 文件：output\code_sources\cache\operations\PROJECT-CAPABILITY-INDEX.md
- 行号：180
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`| `shopMange` | `/shopMange` | 租户管理 | 选择店铺并换取租户 token | `shopInfo.vue` | 临时 token | 租户列表 / refresh token，待登记 capability |`

### 84. [P2] 存在 TODO/FIXME/临时代码

- 服务：operations / operations
- 文件：output\code_sources\cache\operations\.codex\skills\generate-frontend-context\SKILL.md
- 行号：336
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`- 没有 `TODO` / `TBD` 留在关键字段`

### 85. [P2] 存在 TODO/FIXME/临时代码

- 服务：operations / operations
- 文件：output\code_sources\cache\operations\.codex\skills\shell-access-frontend-skill\SKILL.md
- 行号：51
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`| `shopMange` | `/shopMange` | 租户管理 | 选择店铺并换取租户 token | `shopInfo.vue` | 临时 token |`

### 86. [P2] 存在 TODO/FIXME/临时代码

- 服务：operations / operations
- 文件：output\code_sources\cache\operations\apps\web-ele\src\utils\excelRequest.js
- 行号：34
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`console.log(error) // for debug`

### 87. [P2] 存在 TODO/FIXME/临时代码

- 服务：operations / operations
- 文件：output\code_sources\cache\operations\internal\lint-configs\eslint-config\src\configs\unicorn.ts
- 行号：21
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`'unicorn/expiring-todo-comments': 'off',`

### 88. [P2] 存在 TODO/FIXME/临时代码

- 服务：operations / operations
- 文件：output\code_sources\cache\operations\internal\vite-config\src\plugins\importmap.ts
- 行号：14
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`debug?: boolean;`

### 89. [P2] 存在 TODO/FIXME/临时代码

- 服务：operations / operations
- 文件：output\code_sources\cache\operations\internal\vite-config\src\plugins\importmap.ts
- 行号：57
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`debug: false,`

### 90. [P2] 存在 TODO/FIXME/临时代码

- 服务：operations / operations
- 文件：output\code_sources\cache\operations\internal\vite-config\src\plugins\importmap.ts
- 行号：70
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`if (options?.debug) {`

### 91. [P2] 存在 TODO/FIXME/临时代码

- 服务：operations / operations
- 文件：output\code_sources\cache\operations\packages\effects\common-ui\src\ui\dashboard\workbench\index.ts
- 行号：4
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`export { default as WorkbenchTodo } from './workbench-todo.vue';`

### 92. [P1] 疑似敏感信息硬编码

- 服务：furnish / furnish
- 文件：output\code_sources\cache\furnish\temp.d.ts
- 行号：2
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`const temp_token = \"***\" || '';`

### 93. [P2] 存在 TODO/FIXME/临时代码

- 服务：furnish / furnish
- 文件：output\code_sources\cache\furnish\.codex\skills\brainstorming\SKILL.md
- 行号：18
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`Every project goes through this process. A todo list, a single-function utility, a config change — all of them. "Simple" projects are where unexamined assumptions cause the most wasted work. The design can be short (a few sentences for trul`

### 94. [P2] 存在 TODO/FIXME/临时代码

- 服务：furnish / furnish
- 文件：output\code_sources\cache\furnish\.codex\skills\brainstorming\SKILL.md
- 行号：119
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`1. **Placeholder scan:** Any "TBD", "TODO", incomplete sections, or vague requirements? Fix them.`

### 95. [P2] 存在 TODO/FIXME/临时代码

- 服务：furnish / furnish
- 文件：output\code_sources\cache\furnish\.codex\skills\generate-frontend-context\SKILL.md
- 行号：338
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`- 没有 `TODO` / `TBD` 留在关键字段`

### 96. [P2] 存在 TODO/FIXME/临时代码

- 服务：furnish / furnish
- 文件：output\code_sources\cache\furnish\.codex\skills\systematic-debugging\defense-in-depth.md
- 行号：18
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`- Debug logging helps when other layers fail`

### 97. [P2] 存在 TODO/FIXME/临时代码

- 服务：furnish / furnish
- 文件：output\code_sources\cache\furnish\.codex\skills\systematic-debugging\defense-in-depth.md
- 行号：72
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`### Layer 4: Debug Instrumentation`

### 98. [P2] 存在 TODO/FIXME/临时代码

- 服务：furnish / furnish
- 文件：output\code_sources\cache\furnish\.codex\skills\systematic-debugging\defense-in-depth.md
- 行号：78
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`logger.debug('About to git init', {`

### 99. [P2] 存在 TODO/FIXME/临时代码

- 服务：furnish / furnish
- 文件：output\code_sources\cache\furnish\.codex\skills\systematic-debugging\defense-in-depth.md
- 行号：93
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`3. **Add validation at each layer** - Entry, business, environment, debug`

### 100. [P2] 存在 TODO/FIXME/临时代码

- 服务：furnish / furnish
- 文件：output\code_sources\cache\furnish\.codex\skills\systematic-debugging\defense-in-depth.md
- 行号：120
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`- Debug logging identified structural misuse`

### 101. [P2] 存在 TODO/FIXME/临时代码

- 服务：furnish / furnish
- 文件：output\code_sources\cache\furnish\.codex\skills\systematic-debugging\root-cause-tracing.md
- 行号：74
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`console.error('DEBUG git init:', {`

### 102. [P2] 存在 TODO/FIXME/临时代码

- 服务：furnish / furnish
- 文件：output\code_sources\cache\furnish\.codex\skills\systematic-debugging\root-cause-tracing.md
- 行号：89
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`npm test 2>&1 | grep 'DEBUG git init'`

### 103. [P2] 存在 TODO/FIXME/临时代码

- 服务：furnish / furnish
- 文件：output\code_sources\cache\furnish\.codex\skills\systematic-debugging\test-pressure-2.md
- 行号：22
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`5. Added debug logging - shows payment processes, status not updating`

### 104. [P2] 存在 TODO/FIXME/临时代码

- 服务：furnish / furnish
- 文件：output\code_sources\cache\furnish\.codex\skills\systematic-debugging\test-pressure-2.md
- 行号：39
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`- Add comment: "TODO: investigate why status update is slow"`

### 105. [P2] 存在 TODO/FIXME/临时代码

- 服务：furnish / furnish
- 文件：output\code_sources\cache\furnish\.codex\skills\using-superpowers\SKILL.md
- 行号：58
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`"Create TodoWrite todo per item" [shape=box];`

### 106. [P2] 存在 TODO/FIXME/临时代码

- 服务：furnish / furnish
- 文件：output\code_sources\cache\furnish\.codex\skills\using-superpowers\SKILL.md
- 行号：72
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`"Has checklist?" -> "Create TodoWrite todo per item" [label="yes"];`

### 107. [P2] 存在 TODO/FIXME/临时代码

- 服务：furnish / furnish
- 文件：output\code_sources\cache\furnish\.codex\skills\using-superpowers\SKILL.md
- 行号：74
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`"Create TodoWrite todo per item" -> "Follow skill exactly";`

### 108. [P2] 存在 TODO/FIXME/临时代码

- 服务：furnish / furnish
- 文件：output\code_sources\cache\furnish\.codex\skills\writing-plans\SKILL.md
- 行号：109
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`- "TBD", "TODO", "implement later", "fill in details"`

### 109. [P2] 存在 TODO/FIXME/临时代码

- 服务：furnish / furnish
- 文件：output\code_sources\cache\furnish\.codex\skills\writing-skills\examples\CLAUDE_MD_TESTING.md
- 行号：12
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`You need to debug a failing authentication service.`

### 110. [P1] 疑似敏感信息硬编码

- 服务：furnish / furnish
- 文件：output\code_sources\cache\furnish\src\utils\api-request.ts
- 行号：46
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`config.url = config.url + symbol + 'token=' + temp_data.default.temp_token;`

### 111. [P1] 疑似敏感信息硬编码

- 服务：furnish / furnish
- 文件：output\code_sources\cache\furnish\src\utils\api-request.ts
- 行号：51
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`config.url = config.url + '&token=\"***\"null' ? JSON.parse(cookie)?.token : '');`

### 112. [P1] 疑似敏感信息硬编码

- 服务：furnish / furnish
- 文件：output\code_sources\cache\furnish\src\utils\index-request.ts
- 行号：46
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`config.url = config.url + symbol + 'token=' + temp_data.default.temp_token;`

### 113. [P1] 疑似敏感信息硬编码

- 服务：furnish / furnish
- 文件：output\code_sources\cache\furnish\src\utils\index-request.ts
- 行号：51
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`config.url = config.url + '&token=\"***\"null' ? JSON.parse(cookie)?.token : '');`

### 114. [P2] 存在 TODO/FIXME/临时代码

- 服务：miniapp / miniapp
- 文件：output\code_sources\cache\miniapp\FRONTEND-README.md
- 行号：78
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`| 待确认鉴权服务 | `utils/login.js` 中的登录、临时登录、临时 key 请求 | 微信 / App 登录，写入 `authInfo` 与 `key` | 登录失败弹窗；临时登录兜底 |`

### 115. [P2] 存在 TODO/FIXME/临时代码

- 服务：miniapp / miniapp
- 文件：output\code_sources\cache\miniapp\.codex\skills\generate-frontend-context\SKILL.md
- 行号：336
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`- 没有 `TODO` / `TBD` 留在关键字段`

### 116. [P2] 存在 TODO/FIXME/临时代码

- 服务：miniapp / miniapp
- 文件：output\code_sources\cache\miniapp\.codex\skills\member-account-settings-frontend-skill\SKILL.md
- 行号：91
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`| `login` | 微信 / App 登录、临时登录、临时 key 请求 | 待确认 | 真实接口提供方未命中注册表；敏感配置不得写入文档 |`

### 117. [P2] 存在 TODO/FIXME/临时代码

- 服务：miniapp / miniapp
- 文件：output\code_sources\cache\miniapp\components\hot-zone\index.js
- 行号：83
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`// console.log('debug', { hasClient, rawX, rawY, tapX, tapY, rect, relX, relY, scrollTop: this.data.pageScrollTop });`

### 118. [P2] 存在 TODO/FIXME/临时代码

- 服务：miniapp / miniapp
- 文件：output\code_sources\cache\miniapp\pages\order\order-detail\index.js
- 行号：174
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`invoiceStatus: this.datermineInvoiceStatus(order), //todo`

### 119. [P2] 存在 TODO/FIXME/临时代码

- 服务：miniapp / miniapp
- 文件：output\code_sources\cache\miniapp\pages\order\order-list\index.js
- 行号：110
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`id: goods.skuId, ///  todo  id 接口没有，需要的话再找`

### 120. [P2] 疑似敏感日志输出

- 服务：miniapp / miniapp
- 文件：output\code_sources\cache\miniapp\utils\http.js
- 行号：68
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`console.log('只剩7天到期，续期Token', authInfo);`

### 121. [P2] 存在 TODO/FIXME/临时代码

- 服务：miniapp / miniapp
- 文件：output\code_sources\cache\miniapp\utils\login.js
- 行号：36
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`url: `${envInfo.api}/auth/ua/social/temporary/app`,`

### 122. [P2] 存在 TODO/FIXME/临时代码

- 服务：miniapp / miniapp
- 文件：output\code_sources\cache\miniapp\utils\login.js
- 行号：56
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`url: `${envInfo.api}/auth/ua/get/temporary/app?deviceId=${wx.getStorageSync('deviceId')}&key=${wx.getStorageSync('key')}`,`

### 123. [P2] 疑似敏感日志输出

- 服务：miniapp / miniapp
- 文件：output\code_sources\cache\miniapp\utils\login.js
- 行号：76
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`console.log('refresh token',res)`

### 124. [P2] 疑似敏感日志输出

- 服务：miniapp / miniapp
- 文件：output\code_sources\cache\miniapp\utils\login.js
- 行号：81
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：`console.log('refresh token result',authInfo)`

### 125. [P2] 存在 TODO/FIXME/临时代码

- 服务：miniapp / miniapp
- 文件：output\code_sources\cache\miniapp\utils\userInfo.js
- 行号：25
- 风险影响：该问题可能影响后续代码证据分析或测试验证，需要人工确认。
- 建议处理：请开发确认是否为真实风险；如涉及敏感信息或临时代码，应先修复后再确认代码源。
- 证据摘要：``/wx/mp/app/check/debug/user`,`
