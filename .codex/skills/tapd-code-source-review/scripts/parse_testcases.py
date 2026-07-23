"""解析待最终确认的测试用例并输出结构化上下文。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


CASE_HEADING = re.compile(r"^###\s+(TC\d+)\s+(.+)$")
FIELD_LINE = re.compile(r"^- ([^：]+)：(.*)$")


def main() -> int:
    parser = argparse.ArgumentParser(description="解析 test_cases.md 为结构化上下文。")
    parser.add_argument("--run-dir", required=True, help="Isolated code_review run directory.")
    parser.add_argument("--testcase-path", required=True, help="Testcase Markdown path.")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    if run_dir.name == "latest":
        raise ValueError("latest cannot be used as a testcase parsing work directory")
    testcase_path = Path(args.testcase_path)
    raw_dir = run_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    markdown = testcase_path.read_text(encoding="utf-8")
    cases = parse_markdown_cases(markdown)
    if not cases:
        cases = parse_table_cases(markdown)

    payload = {
        "source": str(testcase_path.as_posix()),
        "testcase_hash": hashlib.sha256(markdown.encode("utf-8")).hexdigest(),
        "case_count": len(cases),
        "cases": cases,
    }
    write_json(raw_dir / "parsed_test_cases.json", payload)
    write_context_markdown(run_dir / "testcase_context.md", payload)
    update_index(run_dir / "evidence_index.json", payload)
    print(len(cases))
    return 0


def parse_markdown_cases(markdown: str) -> list[dict[str, Any]]:
    lines = markdown.splitlines()
    cases: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    current_section = ""
    list_buffer: list[str] = []

    def flush_buffer() -> None:
        nonlocal list_buffer, current_section, current
        if current is None or not current_section or not list_buffer:
            list_buffer = []
            return
        current[current_section] = normalize_multiline(list_buffer)
        list_buffer = []

    for line in lines:
        heading_match = CASE_HEADING.match(line.strip())
        if heading_match:
            flush_buffer()
            if current is not None:
                cases.append(normalize_case(current))
            current = {
                "case_id": heading_match.group(1).strip(),
                "heading_title": heading_match.group(2).strip(),
            }
            current_section = ""
            continue

        if current is None:
            continue

        field_match = FIELD_LINE.match(line.strip())
        is_known_field = False
        if field_match:
            field_name = field_match.group(1).strip().replace("*", "")
            mapped_key = map_field_name(field_name)
            known_keys = {
                "title", "directory", "requirement_id", "case_type", "case_status", "priority",
                "system_scope", "module", "test_point", "precondition", "steps", "test_data",
                "expected_results", "requirement_points", "remarks", "case_id", "编号", "用例名称",
                "用例目录", "需求ID", "用例类型", "用例状态", "用例等级", "所属端/角色/系统", "所属角色",
                "功能模块", "测试点", "前置条件", "测试步骤", "测试数据", "预期结果", "关联需求点", "备注"
            }
            if field_name in known_keys or mapped_key in known_keys:
                is_known_field = True

        if field_match and (current_section not in {"steps", "expected_results"} or is_known_field):
            flush_buffer()
            field_name = field_match.group(1).strip().replace("*", "")
            field_value = field_match.group(2).strip()
            mapped_key = map_field_name(field_name)
            current[mapped_key] = field_value
            current_section = ""
            if mapped_key in {"steps", "expected_results"}:
                current_section = mapped_key
                list_buffer = []
            continue

        stripped = line.strip()
        if not stripped:
            continue

        if current_section in {"steps", "expected_results"} and re.match(r"^(\d+\.|-)\s+", stripped):
            list_buffer.append(stripped)
            continue

        if current_section in {"steps", "expected_results"} and stripped:
            list_buffer.append(stripped)
            continue

    flush_buffer()
    if current is not None:
        cases.append(normalize_case(current))
    return cases


def parse_table_cases(markdown: str) -> list[dict[str, Any]]:
    table_lines = [line for line in markdown.splitlines() if line.strip().startswith("|")]
    if len(table_lines) < 3:
        return []
    headers = [item.strip() for item in table_lines[0].strip("|").split("|")]
    cases: list[dict[str, Any]] = []
    for row in table_lines[2:]:
        values = [item.strip() for item in row.strip("|").split("|")]
        if len(values) != len(headers):
            continue
        raw_case = {map_field_name(header): value for header, value in zip(headers, values)}
        raw_case.setdefault("case_id", raw_case.get("id", ""))
        raw_case.setdefault("heading_title", raw_case.get("title", ""))
        cases.append(normalize_case(raw_case))
    return cases


def map_field_name(name: str) -> str:
    mapping = {
        "用例名称": "title",
        "用例目录": "directory",
        "需求ID": "requirement_id",
        "用例类型": "case_type",
        "用例状态": "case_status",
        "用例等级": "priority",
        "优先级": "priority",
        "所属端/角色/系统": "system_scope",
        "功能模块": "module",
        "测试点": "test_point",
        "前置条件": "precondition",
        "测试步骤": "steps",
        "测试数据": "test_data",
        "预期结果": "expected_results",
        "关联需求点": "requirement_points",
        "备注": "remarks",
        "备注/风险点": "remarks",
        "编号": "case_id",
        "测试标题": "title",
    }
    return mapping.get(name.strip(), name.strip())


def normalize_case(raw_case: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": str(raw_case.get("case_id", "")).strip(),
        "title": str(raw_case.get("title") or raw_case.get("heading_title") or "").strip(),
        "priority": str(raw_case.get("priority", "")).strip(),
        "system_scope": str(raw_case.get("system_scope", "")).strip(),
        "module": str(raw_case.get("module", "")).strip(),
        "test_point": str(raw_case.get("test_point", "")).strip(),
        "precondition": str(raw_case.get("precondition", "")).strip(),
        "steps": as_list(raw_case.get("steps")),
        "test_data": str(raw_case.get("test_data", "")).strip(),
        "expected_results": as_list(raw_case.get("expected_results")),
        "requirement_points": str(raw_case.get("requirement_points", "")).strip(),
        "remarks": str(raw_case.get("remarks", "")).strip(),
        "directory": str(raw_case.get("directory", "")).strip(),
        "requirement_id": str(raw_case.get("requirement_id", "")).strip(),
        "case_type": str(raw_case.get("case_type", "")).strip(),
        "case_status": str(raw_case.get("case_status", "")).strip(),
    }


def as_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [normalize_step(item) for item in value if str(item).strip()]
    if isinstance(value, str):
        if not value.strip():
            return []
        parts = re.split(r"\n+", value.strip())
        return [normalize_step(item) for item in parts if item.strip()]
    return []


def normalize_multiline(lines: list[str]) -> list[str]:
    return [normalize_step(line) for line in lines if line.strip()]


def normalize_step(text: str) -> str:
    return re.sub(r"^(\d+\.|-)\s*", "", text.strip())


def write_context_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# 测试用例上下文",
        "",
        f"- 来源文件：{payload['source']}",
        f"- 用例数量：{payload['case_count']}",
        "",
        "## 用例摘要",
        "",
        "| 编号 | 优先级 | 模块 | 用例名称 | 关联需求点 |",
        "|---|---|---|---|---|",
    ]
    for case in payload["cases"]:
        lines.append(
            f"| {case['case_id'] or '无'} | {case['priority'] or '无'} | {case['module'] or '无'} | {case['title'] or '无'} | {case['requirement_points'] or '无'} |"
        )
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8", newline="\n")


def update_index(path: Path, payload: dict[str, Any]) -> None:
    index = safe_read_json(path)
    index["testcase_source"] = payload["source"]
    index["testcase_hash"] = payload["testcase_hash"]
    index["parsed_case_count"] = payload["case_count"]
    write_json(path, index)


def safe_read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    raise SystemExit(main())
