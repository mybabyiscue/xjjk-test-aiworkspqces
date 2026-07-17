---
name: tapd-code-source-review
description: 拉取并门禁审查代码源：根据用户提供的 Git/ZIP 地址与分支，拉取代码并完成用例代码审查前的准入校验。
---

# TAPD 代码源准备与审查

## 1. 核心角色与职责

* **角色**：代码拉取小助手。
* **强约束门禁**：本技能必须在启动时由用户提供至少一个或多个 `http://` 或 `https://` 的 Git 仓库或 ZIP 源码包路径，以及对应的分支。
  * **未提供路径时判定**：如果输入参数没有代码路径，本技能必须**立即报错并停止运行**，不得执行后续的任何操作。
  * **支持多仓库与分支输入格式**：支持以逗号、分号或空格分隔的多个“仓库URL+对应分支名称”解析。例如：
    `https://cnb.cool/services/course.git#feature-20260624-1060777, https://cnb.cool/presentation/operations.git#feature-20260624-1060777`
    或自然文本形式：
    `https://cnb.cool/services/course/  feature-xxx分支， https://cnb.cool/presentation/operations/  feature-xxx分支`
* **核心定位**：专职执行单/多源码仓库的拉取、缓存隔离、疑问销号审计、以及基于 PRD 需求的业务代码合规性审查。

---

## 2. 职责范围与输入输出

* **输入依赖**：
  1. 用户提供的单/多个源码仓库路径及分支（`--code-url` 命令行参数）。
  2. `output/requirement.md`（产品总监生成的结构化需求文档）。
  3. `output/questions.md`（上一阶段遗留的需求疑问点与漏洞追踪清单）。
  4. `output/review_history.md`（若存在，代表之前的迭代记录）。
* **输出文件**：
  1. `output/code_sources/runs/<source_run_id>/`（保存当前批次源码缓存与审查痕迹）。
  2. `output/code_sources/latest/`（存放最新版本的源码配置文件及主审查报告）。
  3. `output/code_sources/cache/<repo_name>/`：**多仓库隔离存放区**。将拉取到的多个服务源码分目录存放（如 `course/` 和 `operations/`），避免文件覆盖与命名冲突。
  4. `output/code_sources/latest/code_review_report.md`：三层架构代码审查总报告。
  5. `output/code_sources/latest/code_source_confirmation.json`：人工确认门禁状态描述。
* **禁止事项**：
  * 严禁修改拉取到的业务代码。
  * 严禁在代码中硬编码访问令牌或密码，所有拉取所需的凭证必须从 `config/credentials.local.json` 或环境变量读取。

---

## 3. 工作流程与控制门禁 (Workflow & Stop-Loss Gate)

本技能的运行流程遵循严格的逻辑控制。若前置门禁不通过，流程必须立刻中断挂起。

### 第一步：前置校验与多库安全拉取 (Check & Multiple Fetch)
1. **参数解析**：检查用户提供的 `--code-url`。通过正则提取出每一个 `(URL, 分支)` 键值对，若无任何有效路径，报错终止。
2. **隔离克隆**：针对提取出的每个仓库：
   - 提取其服务名称作为子文件夹名（例如 `course` 或 `operations`）。
   - 在本地 `output/code_sources/cache/<repo_name>` 执行 `git clone -b <分支> --single-branch <URL>`。
   - 若本地缓存已存在该服务文件夹，则安全执行 `git fetch && git checkout <分支> && git pull` 更新。
3. **记录元数据**：在 `source_manifest.json` 中完整载入每个被激活仓库的服务名称、URL、分支以及对应的 Commit ID，并记录在 `code_fetch_result.md` 中。

### 第二步：疑问销号与中断门禁 (Questions Resolution & Halt Gate)
代码拉取成功后，智能体必须**优先解决 `output/questions.md` 中列出的悬案**：
1. **跨仓库印证**：智能体遍历 `questions.md` 的所有条目，在已下载的 `output/code_sources/cache/` 下的所有服务目录中交叉检索寻找实现证据（例如在后端 `course` 中寻找 API 锁，在前端 `operations` 中寻找组件回弹）。
2. **状态更新**：
   * 如果在代码中找到了对应的安全逻辑或业务实现，则在该问题状态后标记 `[已解决 (代码层已实现，代码位置：[服务名]/filename.js#L10)]`（标记在 `code_review_report.md` 中，但不得改写原始 `questions.md`，保持历史记录纯洁）。
   * 如果代码中确认逻辑确实不存在，或存在明显业务缺口与逻辑矛盾：标记为 `[待确认]` 或 `[疑似逻辑缺陷]`。
3. **熔断判定 (Halt Gate)**：
   * **如果存在任何无法在代码中闭环、代码逻辑缺失、或属于疑似Bug的问题**，本技能必须**立即中止运行（Halt）**。
   * 在对话中将这些问题高亮打印出来呈报给用户，提示：
     > “*检测到以下需求疑问在代码中无法解决（可能属于代码逻辑缺失或需求未对齐），流程已自动挂起：*
     > * *[问题编号] - [问题名称] - [代码层扫描结果]*
     > *请给出指示：A. 忽略此问题并继续；B. 研发已修复，我已更新代码，请重新拉取。*”
   * 智能体必须在此静默等待用户的显式指令，在用户回复“继续”或“已更新”前，**绝对不允许**往下执行第三步。

### 第三步：多层代码审查与对齐 (Multi-Layer Code Audit)
当疑问销号门禁通过（所有问题已被代码印证，或用户确认可跳过）后，智能体结合 `requirement.md` 对源码展开多维度代码审查：

#### 层级 1：业务逻辑与 BDD 规则印证 (Business BDD Alignment)
* 读取 `requirement.md` 中各个 Story 下的 BDD 验收标准（Given-When-Then）。
* 在源码中找出这些功能对应的 Controller、Service 或前端逻辑，验证开发的代码分支是否完全覆盖了 PRD 所约定的场景（如完播率结算、状态机流转等）。

#### 层级 2：代码卫生与安全审计 (Security & Hygiene - 兼容 `agent-skills`)
* 检查源码中是否包含硬编码的系统密码、API Token 或外部凭证。
* 检查 SQL 语句（如 JPA, MyBatis XML, 裸 SQL）中是否存在 SQL 注入风险（必须参数化）。
* 检查涉及敏感数据读取的接口是否进行了 SaaS Tenant 级别鉴权，防止越权跨租户访问。

#### 层级 3：设计质量与坏味道审计 (Design Quality & Smells - 兼容 `mattpocock/skills`)
* 检查在关键业务路径（如进度结算比例、发红包限额）中是否使用了未定义的魔数（Magic Number），建议提取为常量。
* 检查关键异步服务调用（如领奖发券、支付状态同步）是否包含可靠的 Try-Catch 捕获和日志记录。

### 第四步：后续流程指引与用户交互提醒 (Post-Completion Reminder Gate)
在完成所有多层代码审计并成功更新门禁状态为已批准（`approved: true`）后，智能体**必须在输出结束时，显式提示用户后续的可选分支，并询问以下决策**：
1. **是否审批测试用例**：如果用户确认需求对齐与代码审查结论满意，提醒用户可启动测试用例审批与代码关联（推荐调用下游 `tapd-testcase-code-review` 技能）。
2. **是否更新测试用例**：如果本次审计发现了代码实现与 PRD 需求的偏离或卡点，提醒用户是否需要对 `test_cases.md` 的范围进行追加/细化调整。
* **交互示范**：
  > “*代码审计已全部完成。代码源已获批准（approved: true）。根据当前的审计结论，请问您接下来需要执行什么操作？*
  > * *[1] (推荐) 审批测试用例：直接进入用例代码证据关联阶段（启动 tapd-testcase-code-review）*
  > * *[2] 更新测试用例：针对审计发现的业务缺口/带病卡点更新当前用例设计*
  > *请回复对应序号或直接指示您的下一步动作。*”

---

## 4. 输出格式契约 (Output Contract)

### 4.1 `code_review_report.md` 报告结构

所有阶段完成后，在 `output/code_sources/latest/code_review_report.md` 输出中文报告，结构规范如下：

```markdown
# 鲨域专栏课多模块代码审计报告

## 一、 需求疑问 (questions.md) 销号跟踪
| 问题ID | 问题名称 | 状态 | 代码印证证据说明 / 人工干预备注 |
|---|---|---|---|
| Q001 | [名称] | 已解决 / 确认为缺陷 / 人工忽略 | 在 [[服务名] - 文件绝对路径#行号](file:///绝对路径#L行号) 处发现 [实现逻辑] |

## 二、 业务逻辑合规度 (BDD 验收对齐)
* **[BDD-001] [验收场景名称]**
  - **合规度**：合规 / 存在缺口
  - **代码证据**：[[服务名] - filename.js#L12](file:///path/to/file#L12)
  - **审计描述**：开发代码逻辑与 PRD 第X章要求一致，完播百分比计算及状态机流转边界对齐。

## 三、 代码卫生与安全审计 (兼容 agent-skills 规范)
* **敏感令牌扫描**：[未见泄露 / 发现以下硬编码 Token]
* **SQL 注入风险**：[未见注入风险 / 发现 MyBatis 中使用 $ 拼接，存在漏洞风险]
* **SaaS 隔离与越权**：[已包含 tenant_id 安全过滤 / 发现越权缺陷]

## 四、 架构合理性与坏味道审计 (兼容 mattpocock/skills 规范)
* **魔数检查**：[合规 / 发现多处配置硬编码，建议提取]
* **容错捕获与日志**：[异常调用包含合理try-catch及Logger记录 / 缺乏异常处理]
```

### 4.2 `code_source_confirmation.json` 门禁描述

初始被挂起时写入：
```json
{
  "approved": false,
  "reason": "存在待确认的未决需求问题，代码层无法闭环，流程已挂起等待人工指令。"
}
```

只有当所有未决问题被印证解决、或经由用户显式批准跳过，且审计完成后写入：
```json
{
  "approved": true,
  "reason": "代码源已就绪，疑问点已销号/人工确认忽略，多层代码审计已完成，允许进入测试用例代码证据分析。"
}
```

---

## 5. 完成定义

* 已执行多仓库参数解析并隔离克隆/拉取代码缓存。
* 已对比 `questions.md` 并在多服务代码目录中为问题销号；若有代码层不可闭环的问题，已执行流程中止并呈报用户。
* 门禁通过后，已基于 `requirement.md` 对源码进行业务 BDD 逻辑、安全卫生、以及代码坏味道三层审计。
* 已输出详细的中文 `code_review_report.md` 并更新 `code_source_confirmation.json` 状态。
* **已输出下一步流转选项提醒，询问用户是否审批或更新测试用例。**
