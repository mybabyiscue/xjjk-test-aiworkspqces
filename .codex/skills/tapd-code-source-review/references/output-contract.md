# 输出契约与目录结构规范

## 1. 允许写入的根目录

本 skill 现在统一管理源码隔离缓存与测试用例证据审查的输出。允许写入的目录包括：

*   `output/code_sources/`：专用于管理多仓库隔离代码缓存与源元数据。
*   `output/code_review/`：专用于存放基于测试用例的证据分析、代码缺陷和 3 个定制化接口/表文档。
*   `output/latest/`：仅允许在用户“最终通过用例审批”后，写入用例门禁状态文件 `testcase_confirmation.json`。
*   `knowledge/`：仅允许在用例审批通过后，写入测试经验沉淀文件。

---

## 2. 详细的输出目录结构

重构后的总体输出目录如下：

```text
output/
├── code_sources/
│   ├── cache/
│   │   └── <repo_name>/                     # 多仓库隔离代码存放区
│   ├── runs/
│   │   └── <source_run_id>/
│   │       ├── source_manifest.json          # 代码拉取元数据清单
│   │       ├── code_source_confirmation.json  # 初始代码确认状态 (approved: false/true)
│   │       └── input_check.md                # 代码源输入核对
│   └── latest/                               # 最新版代码拉取元数据与确认状态
├── code_review/
│   ├── runs/
│   │   └── <review_run_id>/
│   │       ├── raw/
│   │       │   ├── parsed_test_cases.json    # 解析出的测试用例数据
│   │       │   ├── code_evidence.json        # 扫描到的代码匹配证据
│   │       │   ├── table_evidence.json       # 匹配库表数据
│   │       │   └── interface_evidence.json   # 匹配接口数据
│   │       ├── unit_test_interfaces.md       # 单元测试接口文档 [NEW]
│   │       ├── core_process_interfaces.md    # 核心流程接口文档 [NEW]
│   │       ├── table_information.md          # 表信息文档 [NEW]
│   │       ├── code_review_findings.md       # 扫描到的硬编码/缺陷清单
│   │       ├── issue_tracking.md             # 代码缺陷闭环追踪
│   │       ├── incremental_plan.md           # 增量扫描计划与 Hash
│   │       └── change_summary.md             # 代码变更摘要
│   └── latest/                               # 最新版测试用例证据审查报告(三大文档软链接/副本)
└── latest/
    └── testcase_confirmation.json            # 测试用例最终审计确认门禁 [最终审批后]
```

---

## 3. 三大定制文档结构说明

### 3.1 单元测试接口文档 (`unit_test_interfaces.md`)
*   包含在测试代码目录中扫描到的接口、路由、请求类型，展示参数详细信息（位置、必填、Javadoc描述）以及单测 Mock 信息。

### 3.2 核心流程接口文档 (`core_process_interfaces.md`)
*   包含在正常生产 Controller 目录中提取的、与用例流程匹配的核心 API 接口。对于 `@RequestBody` 参数，递归展开其 DTO/实体类定义的字段类型与注释。

### 3.3 表信息文档 (`table_information.md`)
*   包含与用例流程关联的物理库表。表名称、字段名、类型、是否为空、默认值和物理表注释，必须完全取自所选平台的 `/xjjk-yewu-sql` 元数据文档。

---

## 4. 审批完成门禁契约 (`testcase_confirmation.json`)

仅在用户最终明确同意审批通过后，写入：

```json
{
  "approved": true,
  "approved_at": "2026-07-15T21:42:00+08:00",
  "testcase_hash": "<test_cases.md的SHA-256>",
  "code_review_run_id": "<review_run_id>"
}
```
