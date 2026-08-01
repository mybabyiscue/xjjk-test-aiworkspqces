"""Build the canonical execution plan from a validated preparation assessment."""

from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path

from preparation_contract import (
    VARIANT_TYPES,
    PreparationError,
    file_sha256,
    read_json_object,
    require_list,
    require_object,
    require_string,
    write_json_object,
)

EXECUTABLE_AUDIT_STATUSES: frozenset[str] = frozenset({"可审核", "已通过"})


def parse_arguments() -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="生成唯一的接口测试执行计划。")
    parser.add_argument("--assessment", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--report", required=True)
    return parser.parse_args()


def machine_assertion(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    return isinstance(value.get("path"), str) and isinstance(value.get("operator"), str) and (
        value.get("operator") == "exists" or "value" in value
    )


def require_authorization_header(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise PreparationError(f"{field_name} 必须是字符串。")
    return value.strip()


def build_request(
    request_id: str,
    case_ids: object,
    variant_type: object,
    interface_evidence: object,
    request_data: dict[str, object],
    dependencies: object,
) -> dict[str, object]:
    evidence: dict[str, object] = require_object(interface_evidence, f"{request_id}.interface_evidence")
    normalized_variant_type: str = require_string(variant_type, f"{request_id}.variant_type")
    if normalized_variant_type not in VARIANT_TYPES:
        raise PreparationError(f"{request_id}.variant_type 不合法。")
    expected: dict[str, object] = require_object(request_data.get("expected"), f"{request_id}.expected")
    assertions: list[object] = require_list(expected.get("response_assertions"), f"{request_id}.response_assertions")
    if not assertions or not all(machine_assertion(item) for item in assertions):
        raise PreparationError(f"{request_id} 缺少机器可判定响应断言。")
    return {
        "id": request_id,
        "case_ids": deepcopy(require_list(case_ids, f"{request_id}.case_ids")),
        "variant_type": normalized_variant_type,
        "method": require_string(evidence.get("http_method"), f"{request_id}.http_method"),
        "path": require_string(evidence.get("path"), f"{request_id}.path"),
        "headers": deepcopy(require_object(request_data.get("headers"), f"{request_id}.headers")),
        "authorization_header": require_authorization_header(
            request_data.get("authorization_header"),
            f"{request_id}.authorization_header",
        ),
        "query": deepcopy(require_object(request_data.get("query"), f"{request_id}.query")),
        "body": deepcopy(request_data.get("request_body")),
        "expected": deepcopy(expected),
        "dependencies": deepcopy(require_list(dependencies, f"{request_id}.dependencies")),
    }


def build_execution_plan(
    assessment: dict[str, object],
    preparation_assessment_sha256: str,
) -> tuple[dict[str, object], dict[str, object]]:
    source: dict[str, object] = require_object(assessment.get("source"), "assessment.source")
    testcase_hash: str = require_string(source.get("testcase_hash"), "assessment.source.testcase_hash")
    code_review_run_id: str = require_string(source.get("code_review_run_id"), "assessment.source.code_review_run_id")
    requests: list[dict[str, object]] = []
    flows: list[dict[str, object]] = []
    blockers: list[str] = []
    data_setup: list[dict[str, object]] = []
    data_cleanup: list[dict[str, object]] = []

    data_preparation: dict[str, object] = require_object(assessment.get("data_preparation"), "data_preparation")
    for entry_index, raw_entry in enumerate(require_list(data_preparation.get("entries"), "data_preparation.entries"), start=1):
        entry: dict[str, object] = require_object(raw_entry, f"data_preparation.entries[{entry_index}]")
        entry_id: str = require_string(entry.get("id"), f"data_preparation.entries[{entry_index}].id")
        strategy: str = require_string(entry.get("strategy"), f"{entry_id}.strategy")
        if strategy not in {"reuse", "api_create", "sql_insert", "manual_create"}:
            blockers.append(f"{entry_id} 使用了不允许的数据策略；禁止 Mock、Fake、Stub 和 Mock seed。")
            continue
        if strategy in {"api_create", "sql_insert"}:
            setup: dict[str, object] = deepcopy(require_object(entry.get("setup"), f"{entry_id}.setup"))
            cleanup: dict[str, object] = deepcopy(require_object(entry.get("cleanup"), f"{entry_id}.cleanup"))
            setup["entry_id"] = entry_id
            cleanup["entry_id"] = entry_id
            data_setup.append(setup)
            data_cleanup.insert(0, cleanup)

    for interface_index, raw_interface in enumerate(
        require_list(assessment.get("interface_cases"), "interface_cases"),
        start=1,
    ):
        interface: dict[str, object] = require_object(raw_interface, f"interface_cases[{interface_index}]")
        interface_key: str = require_string(interface.get("interface_key"), f"interface_cases[{interface_index}].interface_key")
        audit: dict[str, object] = require_object(interface.get("audit"), f"{interface_key}.audit")
        if audit.get("status") not in EXECUTABLE_AUDIT_STATUSES:
            blockers.append(f"{interface_key} 审核状态不允许自动化执行。")
            continue
        evidence: object = interface.get("interface_evidence")
        for variant_index, raw_variant in enumerate(
            require_list(interface.get("request_variants"), f"{interface_key}.request_variants"),
            start=1,
        ):
            variant: dict[str, object] = require_object(raw_variant, f"{interface_key}.request_variants[{variant_index}]")
            parameters: list[object] = require_list(variant.get("parameters"), f"{interface_key}.parameters")
            if any(isinstance(parameter, dict) and parameter.get("source_type") == "unresolved" for parameter in parameters):
                blockers.append(f"{interface_key}/{variant.get('name', '')} 存在 unresolved 参数。")
                continue
            try:
                requests.append(
                    build_request(
                        f"{interface_key}__{variant_index}",
                        variant.get("case_keys"),
                        variant.get("variant_type"),
                        evidence,
                        variant,
                        [],
                    )
                )
            except PreparationError as error:
                blockers.append(str(error))

    for flow_index, raw_flow in enumerate(require_list(assessment.get("core_flows"), "core_flows"), start=1):
        flow: dict[str, object] = require_object(raw_flow, f"core_flows[{flow_index}]")
        flow_key: str = require_string(flow.get("flow_key"), f"core_flows[{flow_index}].flow_key")
        steps: list[dict[str, object]] = []
        try:
            for step_index, raw_step in enumerate(require_list(flow.get("steps"), f"{flow_key}.steps"), start=1):
                step: dict[str, object] = require_object(raw_step, f"{flow_key}.steps[{step_index}]")
                step_key: str = require_string(step.get("step_key"), f"{flow_key}.steps[{step_index}].step_key")
                steps.append(
                    build_request(
                        step_key,
                        step.get("case_keys"),
                        step.get("variant_type"),
                        step.get("interface_evidence"),
                        step,
                        step.get("parameter_dependencies"),
                    )
                )
            flows.append({"id": flow_key, "name": require_string(flow.get("name"), f"{flow_key}.name"), "steps": steps})
        except PreparationError as error:
            blockers.append(str(error))

    plan: dict[str, object] = {
        "version": 2,
        "ready": not blockers,
        "source": {
            "preparation_assessment_sha256": preparation_assessment_sha256,
            "testcase_hash": testcase_hash,
            "code_review_run_id": code_review_run_id,
        },
        "token_error_codes": [],
        "data_setup": data_setup,
        "data_cleanup": data_cleanup,
        "requests": requests,
        "flows": flows,
    }
    report: dict[str, object] = {
        "request_count": len(requests),
        "flow_count": len(flows),
        "data_setup_count": len(data_setup),
        "ready": not blockers,
        "blocker_count": len(blockers),
        "blockers": blockers,
    }
    return plan, report


def main() -> int:
    arguments: argparse.Namespace = parse_arguments()
    assessment_path: Path = Path(arguments.assessment)
    assessment: dict[str, object] = read_json_object(assessment_path)
    plan, report = build_execution_plan(assessment, file_sha256(assessment_path))
    write_json_object(Path(arguments.plan), plan)
    write_json_object(Path(arguments.report), report)
    blockers: list[object] = require_list(report.get("blockers"), "report.blockers")
    if blockers:
        for blocker in blockers:
            print(str(blocker))
        return 1
    print(f"执行计划已就绪：{report['request_count']} 个单接口请求，{report['flow_count']} 个核心流程。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
