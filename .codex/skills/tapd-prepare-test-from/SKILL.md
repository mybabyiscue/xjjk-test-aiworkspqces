---
name: tapd-prepare-test-from
description: 基于上游产生的 related_tables.md (表结构整理) 和 related_interfaces.md (接口信息)，结合 environments_config.json 中的网络、凭证等配置，自动生成一份面向可执行的《接口测试准备文档》。即使用户笼统地说“帮我准备测试数据”或“准备一下测试”，只要涉及到用例落地、接口前置条件构造，都应主动触发本技能。
compatibility: 需要 Playwright 浏览器自动化能力、数据库连接执行能力（依赖项目配置的数据库连接管理技能）。若运行环境不具备上述能力之一，应在流程最开始明确告知用户具体缺失哪项能力并终止，不做任何降级替代。
---

# tapd-prepare-test-from

## 概述
本技能基于测试用例代码重审输出的物理数据库表结构（`related_tables.md`）和 API 接口报表（`related_interfaces.md`），关联 `environments_config.json` 测试环境元数据，自动生成一份涵盖测试数据来源、构造 SQL、环境前置条件、接口调用配置和测试脚本骨架的《接口测试准备文档》（`interface_test_preparation.md`）以及数据台账明细清单（`test_data_manifest.md`）。

---

## 💾 产出物定义 (Deliverables Definition)

本技能在运行结束后，必须在工作区的 `output/` 目录下生成以下三个标准输出文件，严禁使用敷衍的大纲式摘要：

1. **接口测试准备手册 (单元用例版)**：`output/interface_test_preparation.md`
   * **功能描述**：用于指导单接口单元功能测试及参数边界验证。
   * **内容要求**：其核心小节必须以 `output/tapd_cases.json` 中已审批通过的测试用例（`cases`）的场景进行组织。为每一个用例，展现其调用的 `HTTP Method`、`请求 URL`、`Header` 以及**专属该用例场景的真实/测试 JSON 请求体**（去 Mock 化，正常用例使用数据库反查的主键，异常/校验用例使用故意构造的特定无效值/超长值/非关联租户ID等），并明确写出**单接口成功或拦截的判定标准**（预期 HTTP 状态码、网关 code/msg、数据库字段变动预期）以方便开发和测试对比验证。

2. **集成测试主流程指南 (流程闭环版)**：`output/integration_test_flow.md`
   * **功能描述**：专门用于指导端到端集成测试，保障核心业务的流转通顺。
   * **内容要求**：
     - 从代码实现的审计与分析出发，自动识别并提取出构成该业务/功能模块完整流转的核心集成测试主流程 API 链路。
     - 根据代码依赖关系，为链路中的每个核心接口绑定反查数据库获得的高置信度真实测试数据，提供标准的 HTTP 方法、网关路径、Header 及成功流 JSON 载荷。
     - 在文档尾部提供按串联逻辑编写的集成自动化调用脚本骨架，方便批量校验。

3. **测试数据台账清单**：`output/test_data_manifest.md`
   * **功能描述**：详细记录本轮测试反查、以及写入构造的所有真实数据库数据。
   * **格式要求**：每条数据记录必须严格对齐并输出为：
     `库名:表名:【数据】`
     （【数据】内容格式为对应数据行记录的完整 JSON 字符串，格式模板为：`[数据库名]:[表名]:【{"[列名]": "[列值]"}】`）。

同时，如果发生鉴权失效并重新登录，本技能将自动更新写入：
* **Token 缓存反写**：工作区 `config/environments_config.json` 中的 `authorization` 字段。

---

## 🚫 硬性前置门禁

在执行任何文档生成或数据提取动作之前，**必须**执行以下前置检查，缺少 any 一个条件时必须立即停止，**不做任何降级替代**：

1. **输入文件检查**：
   * 检查当前工作目录下是否**同时存在**以下四个文件：
     - [table_information.md](file:///./output/code_review/latest/table_information.md)
     - [core_process_interfaces.md](file:///./output/code_review/latest/core_process_interfaces.md)
     - [tapd_cases.json](file:///./output/tapd_cases.json)
     - [testcase_confirmation.json](file:///./output/latest/testcase_confirmation.json)
   * **阻断处理**：如果任一文件不存在，必须立即停止，并明确提示用户：
     > 「未检测到 output/code_review/latest/table_information.md / output/code_review/latest/core_process_interfaces.md / output/tapd_cases.json / output/latest/testcase_confirmation.json，请先运行测试用例代码审计与生成技能生成前置资料后再使用本技能。」

2. **用例确认状态/审批门禁检查**：
   * 读取 `output/latest/testcase_confirmation.json`，校验里面的 `"approved"` 是否为 `true`。
   * **阻断处理**：若不为 `true`，必须立即停止，并明确提示用户：
     > 「检测到当前测试用例尚未完成审批确认（approved 标志不为 true），请先完成用例确认后再使用本技能进行数据准备。」

3. **运行环境兼容性检查 (compatibility)**：
   * **Playwright 能力校验**：校验当前运行环境是否具备 **Playwright 浏览器自动化** 能力（如 Playwright 依赖包与无头浏览器已安装可用）。
   * **数据库连接能力校验**：校验当前是否具备 **数据库连接与执行** 能力（即可以成功从绑定的数据库管理技能中获取配置并建立真实连接）。
   * **阻断处理**：若不具备上述两项能力之一，必须在流程最开始明确告知用户具体缺失哪项能力并**立即终止，不做任何降级替代**。

---

## ⚙️ 环境配置与真实数据查询规范

在生成文档与构造测试数据时，本技能必须摒弃传统的“假 Mock/空占位数据”形式，实现**基于真实数据库的动态查询与数据准备**：

* **环境与数据库配置绑定**：读取工作区 `config/environments_config.json`（使用现有环境元数据配置字段：`name`, `login_url`, `api_domain`, `account`, `password`, `authorization`）和数据库配置管理技能。
* **平台选择与定向校验规范**：
  * 读取 `config/environments_config.json` 中已注册的平台列表。
  * **无论平台数量为几个，都必须**在交互中向用户展示所有可供选择的平台列表（名称 + api_domain），并向用户发起确认提问，等待用户确认选择。
  * **支持多选与单选**：交互应允许用户选择单个平台，或一次性选择多个平台进行批量测试准备。**严禁自行猜测或默认选择——即使列表中只有一个平台，也要让用户明确确认后才能锁定，不得自动跳过此步骤**。
  * 校验**所有被选中的平台**对应的 `authorization` 是否有效（分别发起轻量级请求探测，返回 401 视为失效）。
  * 若某选定平台的 Token 已失效，按 Token 续期规则处理（见 Playwright 模拟登录续期说明，任一平台续期失败则立即终止整个流程，不重试不降级）。
  * 跳过所有**未被选中**的其他平台环境配置，保持其 Token 历史缓存不变。
* **Playwright 模拟登录续期**：若选定的目标平台 Token (`authorization`) 已失效（通过测试请求返回 401 判定），本技能必须使用 **Playwright 浏览器自动化功能**，无头访问对应平台的 `login_url`，模拟输入对应的 `account` 和 `password`，点击登录跳转后拦截网络请求或读取 LocalStorage，提取最新的 Token 并更新回 JSON 缓存文件中的 `authorization` 字段。若续期失败，必须立即终止流程，不进行重试也不降级替代。
  * **无账号密码平台例外规约**：若选定的目标平台在配置中未提供登录地址、账号或密码（如部分无登录页面的客户端网关环境等），则无法进行浏览器自动化重登。在此情况下，若检测到 `authorization` 已失效，技能执行必须立即终止流程，并明确报错提示用户人工更新缓存配置文件（不做任何降级替代）。
* **连接真实数据库查询（防 Mock 占位与个性化入参生成）**：
  - **严禁使用编造的假 Mock 数据**。对于接口调用所必需的字段，使用项目对应的数据库管理技能，执行真实的 `SELECT` 查询以获取系统中已有的真实关联主键和数据字段，并将其回填至接口测试的请求参数及请求体中。
  - **异常及边界流参数构造**：如果测试用例中对应的是逻辑拦截场景，本技能应自动根据字段类型生成特定格式的参数（如无效主键、空值、越界数字、越权ID等），作为该异常用例的入参，以测试接口的防错拦截表现。
* 如果在环境中确实缺少某个必填的配置字段，生成的 Markdown 文档中对应位置必须明确标注 `⚠️ 待补充：[具体字段描述]`。

---

## 📝 核心工作流程

1. **执行前置门禁检查**：
   * 确认 `output/code_review/latest/table_information.md` 和 `output/code_review/latest/core_process_interfaces.md` 同时存在。
   * 确认 `output/tapd_cases.json` 和 `output/latest/testcase_confirmation.json` 存在。
   * 确认 `output/latest/testcase_confirmation.json` 中 `"approved"` 字段为 `true`。
   * 确认具备 Playwright 浏览器组件及数据库连接组件，如不兼容则立即报错并终止。
2. **加载环境配置文件**：加载工作区 `config/environments_config.json` 并提取所有注册的平台列表，重登时原地更新该文件。
3. **平台选择与定向校验**：
   * 在终端向用户展示已有的平台列表（名称 + api_domain）。
   * 无论列表内有几个平台，**都必须**发起确认提问：“当前测试需求属于哪些平台（支持单选或输入逗号分隔进行多选）？”，等待用户回复并锁定这一个或多个平台。严禁在此步骤自动猜测、默认选择或直接跳过。
   * 循环遍历所有选定的平台，校验对应的 `authorization` 是否有效（发起轻量级请求探测，返回 401 视为失效）。
   * 若某选定平台已失效且配置了登录凭证，利用 `Playwright` 模拟登录提取最新 Token 并更新。若重登失败，流程报错终止。
   * 若某选定平台已失效且没有配置登录凭证（如部分没有前端管理界面的系统网关平台），则跳过重登，直接抛出阻断性错误，提示用户人工补全 Token 并终止。
   * **跳过非用户选择的平台环境配置，保持其 Token 历史缓存不变**。
4. **数据库真实数据反查与多场景用例参数构造**：
   * 建立数据库连接，解析 `output/tapd_cases.json` 中的 `cases` 列表。
   * 遍历每一个 `cases` 元素，将其映射至调用的 API（结合 `output/code_review/latest/core_process_interfaces.md`）和表（结合 `output/code_review/latest/table_information.md`）。
   * 针对每一个用例，如果是正常流，反查数据库关联的物理主键 and 数据字段存入内存；如果是异常/边界值流，生成对应的异常字段参数，为后续测试进行准备。
5. **解析接口与表结构输入**：
   * 从 `output/code_review/latest/table_information.md` 提取物理表名、字段列表、类型和物理注释。
   * 从 `output/code_review/latest/core_process_interfaces.md` 提取接口名称、请求方法、参数定义及 DTO 详情。
 6. **生成测试准备文档与数据清单**：
    * 生成 `output/interface_test_preparation.md`：
      - 仅保留 **用例驱动的单接口单元参数**。以 `tapd_cases.json` 中加载的所有用例场景与编号为主线组织，展现其专属定制的异常流/正常流请求体载荷以及判定成败的断言标准。
    * 生成 `output/integration_test_flow.md`：
      - 记录由开发源码实现的审计与分析推导出的核心集成测试主流程 API 链路，列明其调用依赖顺序、各接口的入参规范，并在尾部提供全流程自动化测试的脚本骨架。
    * 生成 `output/test_data_manifest.md`：
      - 将本轮测试反查得到的数据，按 `库名:表名:【数据】` 格式集中记录为数据台账明细清单。
7. **列出待确认事项清单**：
   * 汇总所有未明字段，集中呈现于文档末尾。

---

## 📐 架构实现约束 (Implementation Constraint)

为防止在大用例量场景下目标文档体积过大导致 Token 溢出，同时保证本技能代码在面对不同发版业务需求时的通用性，必须遵循以下解耦实现架构：

1. **业务规则解耦**：
   禁止在任何生成脚本中硬编码特定需求的业务判定条件、接口路径或参数字段。
2. **模型驱动设计**：
   测试场景的语义匹配、接口映射、依赖推导及输入参数生成，必须由智能体在线分析完成，并作为结构化配置中间态存盘。
3. **通用脚本渲染**：
   物理文件的拼装与文档格式渲染必须由通用的渲染脚本完成。该脚本仅负责模板替换与数据合并，不得包含任何特定需求的业务分支控制逻辑。
