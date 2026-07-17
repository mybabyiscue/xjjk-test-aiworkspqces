"""Generic contracts for confirmed interface-test preparation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import TypeAlias

JsonObject: TypeAlias = dict[str, object]
AUDIT_STATUSES: frozenset[str] = frozenset({"待审核", "可审核", "阻断", "已通过", "已驳回"})
PARAMETER_SOURCE_TYPES: frozenset[str] = frozenset({"database", "upstream_response", "protocol_constant", "negative_constructed", "unresolved"})
NON_INTERFACE_CLASSIFICATIONS: frozenset[str] = frozenset({"ui_only", "blocked"})
VARIANT_TYPES: frozenset[str] = frozenset({"positive", "negative"})
NEGATIVE_VARIANT_POLICIES: frozenset[str] = frozenset({"covered", "no_verifiable_validation_rule"})


class PreparationError(RuntimeError):
    """Raised when a preparation artifact violates its contract."""


def read_json_object(path: Path) -> JsonObject:
    try:
        raw_content: str = path.read_text(encoding="utf-8-sig")
    except OSError as error:
        raise PreparationError(f"无法读取 JSON 文件：{path}") from error
    try:
        value: object = json.loads(raw_content)
    except json.JSONDecodeError as error:
        raise PreparationError(f"JSON 格式错误：{path}") from error
    if not isinstance(value, dict):
        raise PreparationError(f"JSON 根节点必须是对象：{path}")
    return value


def write_json_object(path: Path, payload: JsonObject) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def file_sha256(path: Path) -> str:
    digest: hashlib._Hash = hashlib.sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def require_string(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PreparationError(f"字段 {field_name} 必须是非空字符串。")
    return value.strip()


def require_object(value: object, field_name: str) -> JsonObject:
    if not isinstance(value, dict):
        raise PreparationError(f"字段 {field_name} 必须是对象。")
    return value


def require_list(value: object, field_name: str) -> list[object]:
    if not isinstance(value, list):
        raise PreparationError(f"字段 {field_name} 必须是数组。")
    return value


def load_cases(path: Path) -> list[JsonObject]:
    payload: JsonObject = read_json_object(path)
    raw_cases: list[object] = require_list(payload.get("cases"), "cases")
    cases: list[JsonObject] = []
    for index, raw_case in enumerate(raw_cases, start=1):
        case: JsonObject = require_object(raw_case, f"cases[{index}]")
        require_string(case.get("title"), f"cases[{index}].title")
        require_string(case.get("directory"), f"cases[{index}].directory")
        require_string(case.get("requirement_id"), f"cases[{index}].requirement_id")
        cases.append(case)
    return cases


def case_key(index: int) -> str:
    return f"case_{index:03d}"


def case_catalog(cases: list[JsonObject]) -> list[JsonObject]:
    catalog: list[JsonObject] = []
    for index, case in enumerate(cases, start=1):
        catalog.append(
            {
                "case_key": case_key(index),
                "case_index": index,
                "title": require_string(case.get("title"), "title"),
                "directory": require_string(case.get("directory"), "directory"),
                "requirement_id": require_string(case.get("requirement_id"), "requirement_id"),
                "precondition": case.get("precondition", ""),
                "steps": case.get("steps", []),
                "expected_results": case.get("expected_results", []),
            }
        )
    return catalog


def audit_errors(value: object, field_name: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return [f"{field_name} 必须是对象。"]
    status: object = value.get("status")
    if status not in AUDIT_STATUSES:
        errors.append(f"{field_name}.status 不合法。")
    for name in ("evidence_status", "reason", "reviewer", "reviewed_at"):
        if not isinstance(value.get(name), str):
            errors.append(f"{field_name}.{name} 必须是字符串。")
    return errors


def validation_errors(assessment: JsonObject, cases: list[JsonObject], snapshot: JsonObject) -> list[str]:
    errors: list[str] = []
    source: object = assessment.get("source")
    if not isinstance(source, dict):
        errors.append("assessment.source 必须是对象。")
    else:
        confirmation: JsonObject = require_object(snapshot.get("testcase_confirmation"), "snapshot.testcase_confirmation")
        if source.get("testcase_hash") != confirmation.get("testcase_hash"):
            errors.append("assessment.source.testcase_hash 与确认文件不一致。")
        if source.get("code_review_run_id") != confirmation.get("code_review_run_id"):
            errors.append("assessment.source.code_review_run_id 与确认文件不一致。")
    expected_keys: set[str] = {case_key(index) for index in range(1, len(cases) + 1)}
    raw_catalog: object = assessment.get("case_catalog")
    if not isinstance(raw_catalog, list) or {item.get("case_key") for item in raw_catalog if isinstance(item, dict)} != expected_keys:
        errors.append("assessment.case_catalog 必须与当前测试用例逐条对应。")
    raw_records: object = assessment.get("real_data_records")
    records: list[object] = raw_records if isinstance(raw_records, list) else []
    if not isinstance(raw_records, list):
        errors.append("assessment.real_data_records 必须是数组。")
    record_references: set[str] = set()
    for index, raw_record in enumerate(records, start=1):
        if not isinstance(raw_record, dict):
            errors.append(f"real_data_records[{index}] 必须是对象。")
            continue
        try:
            reference: str = require_string(raw_record.get("query_reference"), f"real_data_records[{index}].query_reference")
            record_references.add(reference)
            for name in ("connection", "database", "table", "executed_at", "purpose"):
                require_string(raw_record.get(name), f"real_data_records[{index}].{name}")
            require_list(raw_record.get("fields"), f"real_data_records[{index}].fields")
            require_object(raw_record.get("filters"), f"real_data_records[{index}].filters")
            if not isinstance(raw_record.get("row_count"), int):
                errors.append(f"real_data_records[{index}].row_count 必须是整数。")
            require_list(raw_record.get("records"), f"real_data_records[{index}].records")
        except PreparationError as error:
            errors.append(str(error))
    coverage: dict[str, int] = {key: 0 for key in expected_keys}
    raw_interfaces: object = assessment.get("interface_cases")
    if not isinstance(raw_interfaces, list):
        errors.append("assessment.interface_cases 必须是数组。")
        raw_interfaces = []
    for index, raw_interface in enumerate(raw_interfaces, start=1):
        errors.extend(interface_case_errors(raw_interface, index, coverage, record_references))
    raw_non_interface_cases: object = assessment.get("non_interface_cases")
    if not isinstance(raw_non_interface_cases, list):
        errors.append("assessment.non_interface_cases 必须是数组。")
        raw_non_interface_cases = []
    for index, raw_case in enumerate(raw_non_interface_cases, start=1):
        errors.extend(non_interface_case_errors(raw_case, index, coverage, record_references))
    for key, count in coverage.items():
        if count != 1:
            errors.append(f"{key} 必须恰好被可接口测试或不可接口测试集合覆盖一次，当前为 {count} 次。")
    raw_flows: object = assessment.get("core_flows")
    if not isinstance(raw_flows, list):
        errors.append("assessment.core_flows 必须是数组。")
    else:
        for index, raw_flow in enumerate(raw_flows, start=1):
            errors.extend(core_flow_errors(raw_flow, index, expected_keys, record_references))
    reason: object = assessment.get("core_flow_blocker_reason")
    if not isinstance(reason, str):
        errors.append("assessment.core_flow_blocker_reason 必须是字符串。")
    return errors


def interface_case_errors(value: object, index: int, coverage: dict[str, int], record_references: set[str]) -> list[str]:
    field_name: str = f"interface_cases[{index}]"
    errors: list[str] = []
    if not isinstance(value, dict):
        return [f"{field_name} 必须是对象。"]
    try:
        require_string(value.get("interface_key"), f"{field_name}.interface_key")
        evidence: JsonObject = require_object(value.get("interface_evidence"), f"{field_name}.interface_evidence")
        for name in ("service", "controller_file", "controller_method", "http_method", "path"):
            require_string(evidence.get(name), f"{field_name}.interface_evidence.{name}")
        case_keys: list[object] = require_list(value.get("covered_case_keys"), f"{field_name}.covered_case_keys")
        if not case_keys:
            errors.append(f"{field_name}.covered_case_keys 不得为空。")
        for raw_key in case_keys:
            if not isinstance(raw_key, str) or raw_key not in coverage:
                errors.append(f"{field_name} 引用了不存在的 case_key。")
            elif raw_key:
                coverage[raw_key] += 1
        variants: list[object] = require_list(value.get("request_variants"), f"{field_name}.request_variants")
        if not variants:
            errors.append(f"{field_name}.request_variants 不得为空。")
        variant_types: set[str] = set()
        for variant_index, variant in enumerate(variants, start=1):
            variant_types.update(request_variant_errors(variant, f"{field_name}.request_variants[{variant_index}]", record_references, errors))
        if "positive" not in variant_types:
            errors.append(f"{field_name} 至少需要一个 positive 请求变体。")
        policy: object = value.get("negative_variant_policy")
        if policy not in NEGATIVE_VARIANT_POLICIES:
            errors.append(f"{field_name}.negative_variant_policy 不合法。")
        elif policy == "covered" and "negative" not in variant_types:
            errors.append(f"{field_name} 已声明存在可验证反向规则，但缺少 negative 请求变体。")
        elif policy == "no_verifiable_validation_rule":
            evidence: list[object] = require_list(value.get("negative_variant_evidence"), f"{field_name}.negative_variant_evidence")
            if not evidence:
                errors.append(f"{field_name} 未发现可验证反向规则时必须提供证据说明。")
        errors.extend(audit_errors(value.get("audit"), f"{field_name}.audit"))
    except PreparationError as error:
        errors.append(str(error))
    return errors


def request_variant_errors(value: object, field_name: str, record_references: set[str], errors: list[str]) -> set[str]:
    variant_types: set[str] = set()
    if not isinstance(value, dict):
        errors.append(f"{field_name} 必须是对象。")
        return variant_types
    try:
        require_string(value.get("name"), f"{field_name}.name")
        variant_type: str = require_string(value.get("variant_type"), f"{field_name}.variant_type")
        if variant_type not in VARIANT_TYPES:
            errors.append(f"{field_name}.variant_type 不合法。")
        else:
            variant_types.add(variant_type)
            if variant_type == "negative":
                evidence: list[object] = require_list(value.get("validation_evidence"), f"{field_name}.validation_evidence")
                if not evidence:
                    errors.append(f"{field_name} 的 negative 请求变体必须提供校验依据。")
        require_list(value.get("case_keys"), f"{field_name}.case_keys")
        require_object(value.get("headers"), f"{field_name}.headers")
        parameters: list[object] = require_list(value.get("parameters"), f"{field_name}.parameters")
        if "request_body" not in value:
            errors.append(f"{field_name}.request_body 不得缺失。")
        expected: JsonObject = require_object(value.get("expected"), f"{field_name}.expected")
        if not isinstance(expected.get("http_status"), int):
            errors.append(f"{field_name}.expected.http_status 必须是整数。")
        response_assertions: list[object] = require_list(expected.get("response_assertions"), f"{field_name}.expected.response_assertions")
        if not response_assertions:
            errors.append(f"{field_name}.expected.response_assertions 不得为空。")
        require_list(expected.get("database_assertions"), f"{field_name}.expected.database_assertions")
        require_list(value.get("setup_steps"), f"{field_name}.setup_steps")
        require_list(value.get("cleanup_steps"), f"{field_name}.cleanup_steps")
        for parameter_index, parameter in enumerate(parameters, start=1):
            errors.extend(parameter_errors(parameter, f"{field_name}.parameters[{parameter_index}]", record_references))
    except PreparationError as error:
        errors.append(str(error))
    return variant_types


def parameter_errors(value: object, field_name: str, record_references: set[str]) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return [f"{field_name} 必须是对象。"]
    try:
        require_string(value.get("name"), f"{field_name}.name")
        require_string(value.get("type"), f"{field_name}.type")
        source_type: str = require_string(value.get("source_type"), f"{field_name}.source_type")
        if source_type not in PARAMETER_SOURCE_TYPES:
            errors.append(f"{field_name}.source_type 不合法。")
        require_string(value.get("source_reference"), f"{field_name}.source_reference")
        query_reference: object = value.get("query_reference")
        if source_type == "database" and (not isinstance(query_reference, str) or query_reference not in record_references):
            errors.append(f"{field_name} 的 database 来源必须引用真实查询记录。")
        if source_type == "unresolved":
            errors.append(f"{field_name} 存在 unresolved 参数，不能进入可执行接口。")
    except PreparationError as error:
        errors.append(str(error))
    return errors


def non_interface_case_errors(value: object, index: int, coverage: dict[str, int], record_references: set[str]) -> list[str]:
    field_name: str = f"non_interface_cases[{index}]"
    errors: list[str] = []
    if not isinstance(value, dict):
        return [f"{field_name} 必须是对象。"]
    try:
        key: str = require_string(value.get("case_key"), f"{field_name}.case_key")
        if key not in coverage:
            errors.append(f"{field_name}.case_key 不存在。")
        else:
            coverage[key] += 1
        require_string(value.get("title"), f"{field_name}.title")
        classification: object = value.get("classification")
        if classification not in NON_INTERFACE_CLASSIFICATIONS:
            errors.append(f"{field_name}.classification 不合法。")
        require_string(value.get("reason"), f"{field_name}.reason")
        related_interfaces: list[object] = require_list(value.get("related_interfaces"), f"{field_name}.related_interfaces")
        for related_index, related in enumerate(related_interfaces, start=1):
            related_object: JsonObject = require_object(related, f"{field_name}.related_interfaces[{related_index}]")
            for name in ("http_method", "path"):
                require_string(related_object.get(name), f"{field_name}.related_interfaces[{related_index}].{name}")
            require_object(related_object.get("headers"), f"{field_name}.related_interfaces[{related_index}].headers")
            require_list(related_object.get("parameters"), f"{field_name}.related_interfaces[{related_index}].parameters")
        parameter_data: list[object] = require_list(value.get("parameter_data"), f"{field_name}.parameter_data")
        for raw_data in parameter_data:
            if isinstance(raw_data, dict) and raw_data.get("query_reference") not in record_references:
                errors.append(f"{field_name}.parameter_data 引用了不存在的查询记录。")
        require_string(value.get("recommended_test_type"), f"{field_name}.recommended_test_type")
        if classification == "blocked":
            missing_evidence: list[object] = require_list(value.get("missing_evidence"), f"{field_name}.missing_evidence")
            if not missing_evidence:
                errors.append(f"{field_name} 为 blocked 时必须说明缺失证据。")
        errors.extend(audit_errors(value.get("audit"), f"{field_name}.audit"))
    except PreparationError as error:
        errors.append(str(error))
    return errors


def core_flow_errors(value: object, index: int, expected_keys: set[str], record_references: set[str]) -> list[str]:
    field_name: str = f"core_flows[{index}]"
    errors: list[str] = []
    if not isinstance(value, dict):
        return [f"{field_name} 必须是对象。"]
    try:
        require_string(value.get("flow_key"), f"{field_name}.flow_key")
        require_string(value.get("name"), f"{field_name}.name")
        case_keys: list[object] = require_list(value.get("case_keys"), f"{field_name}.case_keys")
        if not case_keys or any(not isinstance(key, str) or key not in expected_keys for key in case_keys):
            errors.append(f"{field_name}.case_keys 必须引用已知用例。")
        evidence: list[object] = require_list(value.get("evidence_references"), f"{field_name}.evidence_references")
        if not evidence:
            errors.append(f"{field_name}.evidence_references 不得为空。")
        steps: list[object] = require_list(value.get("steps"), f"{field_name}.steps")
        if len(steps) < 2:
            errors.append(f"{field_name}.steps 至少包含两个接口步骤。")
        for step_index, step in enumerate(steps, start=1):
            errors.extend(core_flow_step_errors(step, f"{field_name}.steps[{step_index}]", record_references))
    except PreparationError as error:
        errors.append(str(error))
    return errors


def core_flow_step_errors(value: object, field_name: str, record_references: set[str]) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return [f"{field_name} 必须是对象。"]
    try:
        evidence: JsonObject = require_object(value.get("interface_evidence"), f"{field_name}.interface_evidence")
        for name in ("service", "controller_file", "controller_method", "http_method", "path"):
            require_string(evidence.get(name), f"{field_name}.interface_evidence.{name}")
        require_object(value.get("headers"), f"{field_name}.headers")
        parameters: list[object] = require_list(value.get("parameters"), f"{field_name}.parameters")
        if "request_body" not in value:
            errors.append(f"{field_name}.request_body 不得缺失。")
        expected: JsonObject = require_object(value.get("expected"), f"{field_name}.expected")
        if not isinstance(expected.get("http_status"), int):
            errors.append(f"{field_name}.expected.http_status 必须是整数。")
        if not require_list(expected.get("response_assertions"), f"{field_name}.expected.response_assertions"):
            errors.append(f"{field_name}.expected.response_assertions 不得为空。")
        require_list(expected.get("database_assertions"), f"{field_name}.expected.database_assertions")
        require_list(value.get("parameter_dependencies"), f"{field_name}.parameter_dependencies")
        require_string(value.get("interrupt_condition"), f"{field_name}.interrupt_condition")
        require_list(value.get("cleanup_steps"), f"{field_name}.cleanup_steps")
        for parameter_index, parameter in enumerate(parameters, start=1):
            errors.extend(parameter_errors(parameter, f"{field_name}.parameters[{parameter_index}]", record_references))
    except PreparationError as error:
        errors.append(str(error))
    return errors
