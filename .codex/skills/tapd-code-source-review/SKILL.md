---
name: tapd-code-source-review
description: 作为一个代码拉取、疑问销号、业务多层审计与测试用例证据提取的一站式助手。包含基于测试用例的参数提取及过滤、平台数据库表元数据（/xjjk-yewu-sql）绑定，生成单元测试接口、核心流程接口与表信息 3 大定制文档，并负责测试用例最终审批与知识沉淀。
---

# TAPD 代码源审查与测试用例证据分析 (重构合并版)

## 1. 核心角色与职责

*   **角色**：代码拉取、疑问审计与用例证据闭环确认的超级助手。
*   **强约束门禁**：本技能在启动时必须满足：
    1.  **代码路径**：由用户提供至少一个或多个 `http://` 或 `https://` 的 Git 仓库或 ZIP 源码包路径，以及对应的分支（使用 `--code-url` 命令行参数）。如无代码路径，**立即报错并停止运行**。
    2.  **前置用例**：本地工作区必须已生成结构化测试用例文档 `output/test_cases.md`。如缺失，**立即报错熔断**。
*   **核心定位**：专职执行单/多源码仓库的拉取隔离、疑问销号、基于用例关键字及物理平台元数据的库表与接口强过滤扫描、分类生成 3 大证据文档、用例最终确认以及经验知识库沉淀。

---

## 2. 职责范围与输入输出

*   **输入依赖**：
    1.  用户提供的单/多个源码仓库路径及分支（`--code-url` 命令行参数）。
    2.  `output/requirement.md`（结构化需求文档）。
    3.  `output/questions.md`（需求疑问追踪清单）。
    5.  `/xjjk-yewu-sql` 的缓存元数据文件 `state/documents/metadata_document.json` **[必须]**。
    6.  微服务网关配置文件（如 `bootstrap.yml`, 网关模块 `.yml`）或前端 API 请求管理器 **[可选，若多微服务架构则推荐]**。
*   **输出产物**：
    1.  `output/code_sources/cache/<repo_name>/`（多仓库隔离代码缓存）。
    2.  `output/code_review/runs/<review_run_id>/`（保存当前批次的代码审计及证据提取产物）。
    3.  `output/code_review/latest/`（存放最新版本的分析结果报告）：
        *   unit_test_interfaces.md：**单元测试与接口测试映射文档**（将每个结构化测试用例映射到真实的后端 API 接口，输出包含 DTO 请求体字段在内的详细参数说明，并单独归纳无法进行接口测试的纯前端/播放器交互测试点，用于开发单测和接口测试对齐）。
        *   `core_process_interfaces.md`：**核心流程接口文档**（包含业务核心步骤说明，且已强过滤去除外部 Mock、Maven 及参数为“无”的辅助接口，仅列出真实后端含参数 API 与 DTO 递归属性）。
        *   `table_information.md`：**表信息文档**（强关联测试用例，完全来自 `/xjjk-yewu-sql` 所选平台缓存元数据中得到的库名、表名、表物理注释与字段级别详情说明）。
        *   `code_review_findings.md`：扫描出的硬编码/坏味道缺陷清单。
        *   `issue_tracking.md`：代码缺陷闭环跟踪状态。
        *   `incremental_plan.md`：增量/全量扫描计划。
        *   `change_summary.md`：服务代码变更摘要。
    4.  `output/latest/testcase_confirmation.json`：测试用例与证据最终确认门禁状态（在用户最终审批通过后生成）。
    5.  工作区 `knowledge/EXP-xxx.md` 与 `knowledge/index.json`：测试经验模式沉淀（用户明确通过后生成）。

---

## 3. 工作流程与控制门禁

本技能遵循严格的步骤与挂起门禁：

### 第一步：前置校验与拉取 (Check & Fetch)
1.  **参数与文件校验**：检查是否有 `--code-url`。检查 `output/test_cases.md` 是否存在。若不通过，报错中止。
2.  **隔离克隆与网关路由侦测**：在 `output/code_sources/cache/<repo_name>/` 安全拉取并更新各个仓库代码。在 `source_manifest.json` 中载入每个仓库的服务名称、URL、分支及 Commit ID。
        *   **网关前缀探测**：自动检索网关配置模块（如 `gateway`）或微服务的路由配置文件，解析出每个微服务绑定的**网关请求前缀**（如 `/course/mp`），并将其回写至 `source_manifest.json` 中的 `gateway_prefix` 字段。

### 第二步：所属平台确认 (Platform Selector Gate)
1.  **列出平台与微服务**：读取 `/xjjk-yewu-sql` 的 `metadata_document.json` 获取所有可用数据库连接。列出检测到的所有微服务。
2.  **提问交互 (极简模式)**：在对话中提供清晰的选择题或选项提示用户：
    *   **选项 A (推荐)**：所有服务共用同一个数据库连接（如“鲨域测试”）。
    *   **选项 B (多分流)**：服务连接不同的数据库，由用户用自然语言告知映射关系（如“course用鲨域测试，member用丝路测试”）。
3.  **自动更新 Manifest**：根据用户的对话反馈，AI 代理自动在后台解析并更新 `source_manifest.json` 中各个服务的 `platform` 属性，无需用户手动在命令行传入。后续表结构提取将严格以此绑定进行库表过滤。

### 第三步：疑问销号与中断门禁 (Questions Halt Gate)
1.  优先遍历 `output/questions.md` 里的所有条目，在克隆出的代码目录下检索对应安全逻辑或业务实现证据。
2.  **熔断判定**：如果存在任何代码逻辑缺失或疑似逻辑缺陷的问题，**必须立即中止运行（Halt）**，在对话中高亮打印这些问题，并等待用户给出指示（如 A. 忽略继续；B. 重新拉取）。在用户明确指示前，**绝对不允许**往下执行。

### 第四步：用例证据提取与三大文档生成 (Evidence Scan)
疑问销号通过（或用户忽略）后，执行以下步骤：
1.  **用例特征提取**：读取并解析 `test_cases.md` 得到用例步骤中的 URL、路径段与核心中英文业务词。
2.  **执行扫描提取与路由拼接**：运行扫描脚本，将用户指定的 **平台名称** 和 **用例特征白名单** 作为过滤参数：
        *   **强关联过滤**：抛弃任何与测试用例、核心需求无直接关系的其他模块接口与库表，确保接口与表“不要出现不符合本次需求的项目”。
        *   **网关路由完整拼接**：解析出的控制器 API 路径必须**强制与第一步中侦测到的网关前缀（`gateway_prefix`）进行拼接**，形成用于测试的完整路径（例如，把 `@PostMapping("/live/goods/save")` 拼装为 `/course/mp/live/goods/save`），禁止漏掉网关前缀。
        *   **接口请求方法（HTTP Method）的唯一判定标准**：必须且只能通过解析 Java 源代码中对应的 Spring Web 注解确定。**严禁根据接口路径包含 "delete", "save" 或业务意图主观推测 HTTP 方法。**
            *   若注解为 `@GetMapping` -> 必须为 `GET`；
            *   若注解为 `@PostMapping` -> 必须为 `POST`；
            *   若注解为 `@PutMapping` -> 必须为 `PUT`；
            *   若注解为 `@DeleteMapping` -> 必须为 `DELETE`；
            *   若注解为 `@RequestMapping` -> 根据其 `method` 属性进行解析，如无则默认支持全部。
        *   **公共必填 Header 提取**：扫描前端网络拦截器（如 `request.ts`, `http.js`），自动抓取鉴权之外的自定义必填头（例如 `sysType`）及动态签名规则，标注在接口文档的 Header 部分。
        *   **接口参数详细解析**：对扫描到的接口，解析其参数位置（Query/Path/Body/Header）、必填状态、Swagger（@ApiParam/@Schema）或 Javadoc 中的 `@param` 描述。
        *   **RequestBody DTO 展开**：如果参数是 `@RequestBody` 复杂对象，自动在代码库中定位其 DTO 类定义，将 DTO 的各个字段及描述作为子参数树状列出。
 3.  **生成 3 个文档**：分类写出 `unit_test_interfaces.md` (单测接口 - 使用拼接后的完整路由)、`core_process_interfaces.md` (生产核心接口 - 包含真实路由与必填 Headers，需在头部追加核心业务步骤，且强过滤去除无参数与Mock接口)、`table_information.md` (物理库表结构)。
4.  **生成辅助文档**：同步输出 `incremental_plan.md`、`code_review_findings.md` 等缺陷文件。

### 第五步：多层代码与设计质量审计 (Hygiene & Smells Audit)
结合需求文档对源码进行“业务逻辑 BDD 验收对齐”、“安全卫生硬编码扫描”与“设计坏味道审计”，并在最终的主代码审查报告（`output/code_review/latest/code_review_report.md`）中进行归纳描述。

### 第六步：用例最终审批与知识库沉淀 (Approval & Knowledge Sink)
1.  **展示审批摘要**：在对话中展示本次审计结果摘要、强关联的数据库表和 API 接口统计，并附上生成的三个定制文档的本地文件链接。
2.  **申请最终审批**：暂停并显式提示用户对其进行审批确认。
3.  **生成确认与沉淀**：只有在用户确认“通过”后，自动生成 `output/latest/testcase_confirmation.json`，并将满足可复用提取条件的测试模式沉淀至 `knowledge/` 下并更新 `knowledge/index.json`。

---

## 4. 推荐执行命令

### 4.1 初始化运行目录与门禁检查
```bash
python scripts/preflight_check.py --code-url <仓库URL#分支>
```

### 4.2 解析并提取用例
```bash
python scripts/parse_testcases.py --run-dir output/code_review/latest
```

### 4.3 执行基于用例与平台强过滤的代码证据扫描
```bash
python scripts/review_code_evidence.py --run-dir output/code_review/latest --platform "<用户确认的平台名称>"
```

---

## 5. 完成定义
*   已正确执行多仓库拉取及疑问销号，无代码层不可闭环问题阻断。
*   已交互确认数据库平台名称。
*   已基于用例端点和核心词实现双重强关联过滤，无任何非本次需求相关的接口与库表泄露。
*   已深度抓取了接口参数明细并展开了 RequestBody DTO 字段属性。
*   已成功生成 **单元测试接口文档**、**核心流程接口文档**、**表信息文档**。
*   用户最终审批通过后，已生成用例确认 `testcase_confirmation.json` 并完成 `knowledge/` 沉淀。
