"""Build an execution plan from approved interface-test records."""

from __future__ import annotations

import argparse
from pathlib import Path

from preparation_contract import VARIANT_TYPES, read_json_object, require_list, require_object, require_string, write_json_object

EXECUTABLE_AUDIT_STATUSES: frozenset[str] = frozenset({"可审核", "已通过"})


def parse_arguments() -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="生成接口自动化执行计划。")
    parser.add_argument("--assessment", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--report", required=True)
    return parser.parse_args()


def machine_assertion(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    return isinstance(value.get("path"), str) and isinstance(value.get("operator"), str) and "value" in value


def main() -> int:
    arguments: argparse.Namespace = parse_arguments()
    assessment: dict[str, object] = read_json_object(Path(arguments.assessment))
    executions: list[dict[str, object]] = []
    blockers: list[str] = []
    for raw_interface in require_list(assessment.get("interface_cases"), "interface_cases"):
        interface: dict[str, object] = require_object(raw_interface, "interface_case")
        interface_key: str = require_string(interface.get("interface_key"), "interface_key")
        audit: dict[str, object] = require_object(interface.get("audit"), "audit")
        if audit.get("status") not in EXECUTABLE_AUDIT_STATUSES:
            blockers.append(f"{interface_key} 审核状态不允许自动化执行。")
            continue
        for raw_variant in require_list(interface.get("request_variants"), "request_variants"):
            variant: dict[str, object] = require_object(raw_variant, "request_variant")
            variant_type: str = require_string(variant.get("variant_type"), "request_variant.variant_type")
            if variant_type not in VARIANT_TYPES:
                blockers.append(f"{interface_key}/{variant.get('name', '')} 的请求变体类型不合法。")
                continue
            parameters: list[object] = require_list(variant.get("parameters"), "request_variant.parameters")
            if any(isinstance(parameter, dict) and parameter.get("source_type") == "unresolved" for parameter in parameters):
                blockers.append(f"{interface_key}/{variant.get('name', '')} 存在 unresolved 参数。")
                continue
            expected: dict[str, object] = require_object(variant.get("expected"), "expected")
            assertions: list[object] = require_list(expected.get("response_assertions"), "response_assertions")
            if not assertions or not all(machine_assertion(item) for item in assertions):
                blockers.append(f"{interface_key}/{variant.get('name', '')} 缺少机器可判定响应断言。")
                continue
            executions.append({"interface_key": interface_key, "interface_evidence": interface.get("interface_evidence"), "request_variant": variant})
    plan: dict[str, object] = {"source": assessment.get("source"), "environment": assessment.get("environment"), "executions": executions}
    report: dict[str, object] = {"api_case_count": len(executions), "ready": not blockers, "blocker_count": len(blockers), "blockers": blockers}
    write_json_object(Path(arguments.plan), plan)
    write_json_object(Path(arguments.report), report)
    if blockers:
        for blocker in blockers:
            print(blocker)
        return 1
    print(f"接口执行计划已就绪：{len(executions)} 个请求变体。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
