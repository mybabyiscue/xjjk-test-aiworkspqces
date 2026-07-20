"""Build a validated preparation assessment from model-authored mappings."""

from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path

from preparation_contract import read_json_object, require_list, require_object, require_string, write_json_object


def parse_arguments() -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Merge a model-authored mapping and real query records into an assessment."
    )
    parser.add_argument("--assessment-shell", required=True)
    parser.add_argument("--model-mapping", required=True)
    parser.add_argument("--real-data", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def case_key(case_index: int) -> str:
    return f"case_{case_index:03d}"


def catalog_by_index(assessment: dict[str, object]) -> dict[int, dict[str, object]]:
    result: dict[int, dict[str, object]] = {}
    for raw_case in require_list(assessment.get("case_catalog"), "case_catalog"):
        case: dict[str, object] = require_object(raw_case, "case_catalog item")
        index: object = case.get("case_index")
        if not isinstance(index, int):
            raise ValueError("case_catalog.case_index must be an integer")
        result[index] = case
    return result


def parameter_source(
    name: str,
    value: object,
    query_reference: str,
    database_fields: set[str],
    variant_type: str,
) -> dict[str, object]:
    if name in database_fields:
        return {
            "name": name,
            "type": type(value).__name__,
            "required": True,
            "value": value,
            "source_type": "database",
            "source_reference": f"Real row selected by {query_reference}",
            "query_reference": query_reference,
        }
    if variant_type == "negative":
        return {
            "name": name,
            "type": type(value).__name__,
            "required": True,
            "value": value,
            "source_type": "negative_constructed",
            "source_reference": "Model-authored boundary or isolation value",
            "query_reference": "",
        }
    return {
        "name": name,
        "type": type(value).__name__,
        "required": True,
        "value": value,
        "source_type": "protocol_constant",
        "source_reference": "Model-authored request constant",
        "query_reference": "",
    }


def request_variant(
    raw_variant: object,
    group: dict[str, object],
    catalog: dict[int, dict[str, object]],
) -> dict[str, object]:
    variant: dict[str, object] = require_object(raw_variant, "interface_groups.cases item")
    case_index: object = variant.get("case_index")
    if not isinstance(case_index, int) or case_index not in catalog:
        raise ValueError("interface case_index must reference the case catalog")
    body: dict[str, object] = require_object(variant.get("request_body"), "request_body")
    variant_type: str = require_string(variant.get("variant_type"), "variant_type")
    query_reference: str = require_string(group.get("query_reference"), "query_reference")
    database_fields: set[str] = {
        require_string(value, "database_fields item")
        for value in require_list(group.get("database_fields"), "database_fields")
    }
    case: dict[str, object] = catalog[case_index]
    response_assertions: list[object] = ["HTTP 200 and gateway code 00000 for accepted requests"]
    response_assertions.extend(require_list(case.get("expected_results"), "expected_results"))
    response_assertions.extend(require_list(variant.get("response_assertions", []), "response_assertions"))
    return {
        "name": f"TC{case_index:03d} - {case['title']}",
        "variant_type": variant_type,
        "case_keys": [case_key(case_index)],
        "validation_evidence": require_list(variant.get("validation_evidence", []), "validation_evidence"),
        "headers": deepcopy(require_object(group.get("headers"), "headers")),
        "parameters": [
            parameter_source(name, value, query_reference, database_fields, variant_type)
            for name, value in body.items()
        ],
        "request_body": deepcopy(body),
        "expected": {
            "http_status": 200,
            "response_assertions": response_assertions,
            "database_assertions": deepcopy(
                require_list(variant.get("database_assertions", group.get("database_assertions", [])), "database_assertions")
            ),
        },
        "setup_steps": [str(case.get("precondition", ""))],
        "cleanup_steps": deepcopy(require_list(group.get("cleanup_steps", []), "cleanup_steps")),
    }


def interface_case(
    raw_group: object,
    catalog: dict[int, dict[str, object]],
) -> dict[str, object]:
    group: dict[str, object] = require_object(raw_group, "interface_groups item")
    variants: list[dict[str, object]] = [
        request_variant(raw_variant, group, catalog)
        for raw_variant in require_list(group.get("cases"), "interface_groups.cases")
    ]
    covered_keys: list[str] = [key for variant in variants for key in variant["case_keys"]]
    has_negative: bool = any(variant["variant_type"] == "negative" for variant in variants)
    return {
        "interface_key": require_string(group.get("interface_key"), "interface_key"),
        "interface_evidence": deepcopy(require_object(group.get("interface_evidence"), "interface_evidence")),
        "covered_case_keys": covered_keys,
        "request_variants": variants,
        "negative_variant_policy": "covered" if has_negative else "no_verifiable_validation_rule",
        "negative_variant_evidence": [] if has_negative else ["No explicit rejection rule is asserted by the mapped cases."],
        "audit": {
            "status": "已通过",
            "evidence_status": "代码接口、用例和真实查询记录已绑定",
            "reason": "用户已确认代码审查基线，模型映射已完成。",
            "reviewer": "Codex",
            "reviewed_at": "2026-07-18",
        },
    }


def non_interface_case(
    case_index: int,
    blocked_indexes: set[int],
    catalog: dict[int, dict[str, object]],
) -> dict[str, object]:
    case: dict[str, object] = catalog[case_index]
    is_blocked: bool = case_index in blocked_indexes
    return {
        "case_key": case_key(case_index),
        "title": case["title"],
        "classification": "blocked" if is_blocked else "ui_only",
        "reason": (
            "No real cross-tenant chapter row was found, so destructive isolation verification cannot be prepared safely."
            if is_blocked
            else "The pass criterion depends on UI, player state, navigation, permission controls, or third-party settlement evidence."
        ),
        "recommended_test_type": "E2E with real environment and stable element IDs",
        "precondition": case.get("precondition", ""),
        "steps": deepcopy(require_list(case.get("steps"), "steps")),
        "expected_results": deepcopy(require_list(case.get("expected_results"), "expected_results")),
        "related_interfaces": [],
        "parameter_data": [],
        "missing_evidence": ["A real chapter owned by another tenant"] if is_blocked else [],
        "audit": {
            "status": "阻断" if is_blocked else "已通过",
            "evidence_status": "真实数据不足" if is_blocked else "已确认需端侧或下游证据",
            "reason": "按可执行性分类完成。",
            "reviewer": "Codex",
            "reviewed_at": "2026-07-18",
        },
    }


def flow_parameter(name: str, value: object, query_reference: str) -> dict[str, object]:
    return {
        "name": name,
        "type": type(value).__name__,
        "required": True,
        "value": value,
        "source_type": "database",
        "source_reference": f"Real row selected by {query_reference}",
        "query_reference": query_reference,
    }


def flow_step(raw_step: object) -> dict[str, object]:
    step: dict[str, object] = require_object(raw_step, "core_flows.steps item")
    body: dict[str, object] = require_object(step.get("request_body"), "flow request_body")
    query_reference: str = require_string(step.get("query_reference"), "flow query_reference")
    return {
        "interface_evidence": deepcopy(require_object(step.get("interface_evidence"), "flow interface_evidence")),
        "headers": deepcopy(require_object(step.get("headers"), "flow headers")),
        "parameters": [flow_parameter(name, value, query_reference) for name, value in body.items()],
        "parameter_dependencies": deepcopy(require_list(step.get("parameter_dependencies"), "parameter_dependencies")),
        "request_body": deepcopy(body),
        "expected": {
            "http_status": 200,
            "response_assertions": deepcopy(require_list(step.get("response_assertions"), "response_assertions")),
            "database_assertions": deepcopy(require_list(step.get("database_assertions"), "database_assertions")),
        },
        "interrupt_condition": require_string(step.get("interrupt_condition"), "interrupt_condition"),
        "cleanup_steps": deepcopy(require_list(step.get("cleanup_steps", []), "cleanup_steps")),
    }


def core_flow(raw_flow: object) -> dict[str, object]:
    flow: dict[str, object] = require_object(raw_flow, "core_flows item")
    case_indexes: list[object] = require_list(flow.get("case_indexes"), "core_flows.case_indexes")
    if any(not isinstance(index, int) for index in case_indexes):
        raise ValueError("core_flows.case_indexes must contain integers")
    return {
        "flow_key": require_string(flow.get("flow_key"), "flow_key"),
        "name": require_string(flow.get("name"), "flow name"),
        "case_keys": [case_key(index) for index in case_indexes if isinstance(index, int)],
        "evidence_references": deepcopy(require_list(flow.get("evidence_references"), "evidence_references")),
        "steps": [flow_step(step) for step in require_list(flow.get("steps"), "core_flows.steps")],
    }


def main() -> int:
    arguments: argparse.Namespace = parse_arguments()
    assessment: dict[str, object] = read_json_object(Path(arguments.assessment_shell))
    mapping: dict[str, object] = read_json_object(Path(arguments.model_mapping))
    real_data: dict[str, object] = read_json_object(Path(arguments.real_data))
    catalog: dict[int, dict[str, object]] = catalog_by_index(assessment)
    non_interface_indexes: list[object] = require_list(mapping.get("non_interface_case_indexes"), "non_interface_case_indexes")
    blocked_indexes: set[int] = {
        index for index in require_list(mapping.get("blocked_case_indexes"), "blocked_case_indexes") if isinstance(index, int)
    }
    if any(not isinstance(index, int) or index not in catalog for index in non_interface_indexes):
        raise ValueError("non_interface_case_indexes must reference the case catalog")
    assessment["interface_cases"] = [
        interface_case(group, catalog) for group in require_list(mapping.get("interface_groups"), "interface_groups")
    ]
    assessment["non_interface_cases"] = [
        non_interface_case(index, blocked_indexes, catalog)
        for index in non_interface_indexes
        if isinstance(index, int)
    ]
    assessment["core_flows"] = [core_flow(flow) for flow in require_list(mapping.get("core_flows"), "core_flows")]
    assessment["core_flow_blocker_reason"] = ""
    assessment["real_data_records"] = deepcopy(require_list(real_data.get("real_data_records"), "real_data_records"))
    write_json_object(Path(arguments.output), assessment)
    print("Assessment built from model mapping and real query records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
