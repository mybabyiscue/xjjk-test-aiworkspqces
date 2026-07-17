# 输出契约

## 输出根目录

本 skill 只写入：

```text
output/code_sources/
```

不得写入或修改：

```text
output/latest/
output/runs/
```

## 目录结构

```text
output/code_sources/
├── cache/
│   ├── repos/
│   └── archives/
├── runs/
│   └── <source_run_id>/
│       ├── input_check.md
│       ├── source_manifest.json
│       ├── code_fetch_result.md
│       ├── code_prepare_findings.md
│       ├── code_source_confirmation.json
│       └── raw/
│           └── prepare_findings.json
└── latest/
    ├── input_check.md
    ├── source_manifest.json
    ├── code_fetch_result.md
    ├── code_prepare_findings.md
    └── code_source_confirmation.json
```

## 确认文件

`code_source_confirmation.json` 默认写入：

```json
{
  "approved": false,
  "reason": "代码已获取并完成初步审查，等待人工确认。",
  "source_run_id": "",
  "approved_at": "",
  "approver": ""
}
```

只有人工确认后才允许写入 `approved: true`。

## latest 同步

每次执行完成后，将当前 run 目录同步到：

```text
output/code_sources/latest/
```

后续 `tapd-testcase-code-review` 只读取 latest 下的 `source_manifest.json` 和 `code_source_confirmation.json`。
