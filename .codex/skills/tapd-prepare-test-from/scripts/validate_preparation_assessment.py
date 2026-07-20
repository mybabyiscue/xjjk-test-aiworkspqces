"""Validate a completed interface-test preparation assessment."""

from __future__ import annotations

import argparse
from pathlib import Path

from preparation_contract import load_cases, read_json_object, validation_errors, write_json_object


def parse_arguments() -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="校验接口测试准备评估包。")
    parser.add_argument("--assessment", required=True)
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--tapd-cases", required=True)
    parser.add_argument("--report", required=True)
    return parser.parse_args()


def main() -> int:
    arguments: argparse.Namespace = parse_arguments()
    assessment: dict[str, object] = read_json_object(Path(arguments.assessment))
    snapshot: dict[str, object] = read_json_object(Path(arguments.snapshot))
    cases: list[dict[str, object]] = load_cases(Path(arguments.tapd_cases))
    errors: list[str] = validation_errors(assessment, cases, snapshot)
    interface_groups: object = assessment.get("interface_cases", [])
    interface_case_count: int = sum(
        len(group.get("covered_case_keys", []))
        for group in interface_groups
        if isinstance(group, dict) and isinstance(group.get("covered_case_keys"), list)
    ) if isinstance(interface_groups, list) else 0
    report: dict[str, object] = {
        "input_case_count": len(cases),
        "interface_group_count": len(interface_groups) if isinstance(interface_groups, list) else 0,
        "interface_case_count": interface_case_count,
        "non_interface_case_count": len(assessment.get("non_interface_cases", [])) if isinstance(assessment.get("non_interface_cases"), list) else 0,
        "core_flow_count": len(assessment.get("core_flows", [])) if isinstance(assessment.get("core_flows"), list) else 0,
        "valid": not errors,
        "errors": errors,
    }
    write_json_object(Path(arguments.report), report)
    if errors:
        for error in errors:
            print(error)
        return 1
    print(f"准备评估包校验通过：{len(cases)} 条用例。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
