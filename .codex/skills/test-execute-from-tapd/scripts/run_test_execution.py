"""Execute an approved, business-neutral HTTP and database assertion plan."""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import TypeAlias

import pymysql
from pymysql.connections import Connection

JsonObject: TypeAlias = dict[str, object]
HttpResult: TypeAlias = tuple[int, str]
SUPPORTED_OPERATORS: frozenset[str] = frozenset({"equals", "not_equals", "exists", "contains", "in"})
SUPPORTED_VARIANTS: frozenset[str] = frozenset({"positive", "negative"})
RETRYABLE_HTTP_STATUSES: frozenset[int] = frozenset({429, 500, 502, 503, 504})
SENSITIVE_TOKENS: frozenset[str] = frozenset({"authorization", "cookie", "password", "secret", "token", "api-key", "apikey"})
SQL_FORBIDDEN_PATTERN: re.Pattern[str] = re.compile(
    r"\b(insert|update|delete|replace|alter|drop|create|truncate|grant|revoke|call|load|outfile|dumpfile|lock|unlock)\b",
    re.IGNORECASE,
)
PATH_TOKEN_PATTERN: re.Pattern[str] = re.compile(r"(?:^|\.)([A-Za-z_][A-Za-z0-9_-]*)|\[(\d+)\]")


def parse_arguments() -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="执行已审批的 TAPD 接口测试计划。")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--confirmation", required=True)
    parser.add_argument("--environment-config", required=True)
    parser.add_argument("--environment-name", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--manifest", required=True)
    return parser.parse_args()


def resolve_workspace_path(workspace: Path, relative_path: str, field_name: str) -> Path:
    candidate: Path = Path(relative_path)
    if candidate.is_absolute():
        raise ValueError(f"{field_name} 必须是工作区相对路径：{relative_path}")
    resolved: Path = (workspace / candidate).resolve()
    try:
        resolved.relative_to(workspace)
    except ValueError as error:
        raise ValueError(f"{field_name} 超出工作区边界：{relative_path}") from error
    return resolved


def read_json_object(path: Path, field_name: str) -> JsonObject:
    try:
        raw_content: str = path.read_text(encoding="utf-8-sig")
    except OSError as error:
        raise FileNotFoundError(f"无法读取 {field_name}：{path}；请生成或修复该前置文件。") from error
    try:
        value: object = json.loads(raw_content)
    except json.JSONDecodeError as error:
        raise ValueError(f"{field_name} 不是合法 JSON：{path}；请修复第 {error.lineno} 行。") from error
    return require_object(value, field_name)


def require_object(value: object, field_name: str) -> JsonObject:
    if not isinstance(value, dict):
        raise TypeError(f"{field_name} 必须是对象。")
    return value


def require_list(value: object, field_name: str) -> list[object]:
    if not isinstance(value, list):
        raise TypeError(f"{field_name} 必须是数组。")
    return value


def require_string(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{field_name} 必须是非空字符串。")
    return value.strip()


def require_integer(value: object, field_name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{field_name} 必须是整数。")
    return value


def validate_relative_api_path(value: object, field_name: str) -> str:
    path: str = require_string(value, field_name)
    parsed: urllib.parse.SplitResult = urllib.parse.urlsplit(path)
    if not path.startswith("/") or parsed.scheme or parsed.netloc:
        raise ValueError(f"{field_name} 必须是以 / 开头的相对网关路径。")
    return path


def validate_headers(value: object, field_name: str) -> dict[str, str]:
    raw_headers: JsonObject = require_object(value, field_name)
    headers: dict[str, str] = {}
    for raw_name, raw_value in raw_headers.items():
        name: str = require_string(raw_name, f"{field_name}.name")
        header_value: str = require_string(raw_value, f"{field_name}.{name}")
        if any(token in name.lower() for token in SENSITIVE_TOKENS):
            raise ValueError(f"{field_name}.{name} 不得保存敏感凭证；请使用 authorization_header。")
        headers[name] = header_value
    return headers


def validate_assertion(value: object, field_name: str) -> JsonObject:
    assertion: JsonObject = require_object(value, field_name)
    require_string(assertion.get("path"), f"{field_name}.path")
    operator: str = require_string(assertion.get("operator"), f"{field_name}.operator")
    if operator not in SUPPORTED_OPERATORS:
        raise ValueError(f"{field_name}.operator 不支持：{operator}")
    if operator != "exists" and "value" not in assertion:
        raise ValueError(f"{field_name}.value 不得缺失。")
    return assertion


def validate_read_only_sql(sql: str, field_name: str) -> str:
    normalized: str = sql.strip()
    if not re.match(r"^select\b", normalized, re.IGNORECASE):
        raise ValueError(f"{field_name} 只能包含 SELECT。")
    if ";" in normalized or "--" in normalized or "/*" in normalized or SQL_FORBIDDEN_PATTERN.search(normalized):
        raise ValueError(f"{field_name} 包含禁止的多语句、注释或写操作。")
    return normalized


def validate_database_assertion(value: object, field_name: str) -> JsonObject:
    assertion: JsonObject = require_object(value, field_name)
    require_string(assertion.get("database"), f"{field_name}.database")
    require_string(assertion.get("table"), f"{field_name}.table")
    sql: str = require_string(assertion.get("sql"), f"{field_name}.sql")
    validate_read_only_sql(sql, f"{field_name}.sql")
    require_list(assertion.get("parameters"), f"{field_name}.parameters")
    assertions: list[object] = require_list(assertion.get("assertions"), f"{field_name}.assertions")
    if not assertions:
        raise ValueError(f"{field_name}.assertions 不得为空。")
    for index, raw_assertion in enumerate(assertions, start=1):
        validate_assertion(raw_assertion, f"{field_name}.assertions[{index}]")
    return assertion


def validate_expected(value: object, field_name: str) -> JsonObject:
    expected: JsonObject = require_object(value, field_name)
    require_integer(expected.get("http_status"), f"{field_name}.http_status")
    response_assertions: list[object] = require_list(expected.get("response_assertions"), f"{field_name}.response_assertions")
    if not response_assertions:
        raise ValueError(f"{field_name}.response_assertions 不得为空。")
    for index, raw_assertion in enumerate(response_assertions, start=1):
        validate_assertion(raw_assertion, f"{field_name}.response_assertions[{index}]")
    database_assertions: list[object] = require_list(expected.get("database_assertions"), f"{field_name}.database_assertions")
    for index, raw_assertion in enumerate(database_assertions, start=1):
        validate_database_assertion(raw_assertion, f"{field_name}.database_assertions[{index}]")
    return expected


def validate_request(value: object, field_name: str) -> JsonObject:
    request: JsonObject = require_object(value, field_name)
    require_string(request.get("id"), f"{field_name}.id")
    case_ids: list[object] = require_list(request.get("case_ids"), f"{field_name}.case_ids")
    if not case_ids:
        raise ValueError(f"{field_name}.case_ids 不得为空。")
    for index, case_id in enumerate(case_ids, start=1):
        require_string(case_id, f"{field_name}.case_ids[{index}]")
    variant_type: str = require_string(request.get("variant_type"), f"{field_name}.variant_type")
    if variant_type not in SUPPORTED_VARIANTS:
        raise ValueError(f"{field_name}.variant_type 不支持：{variant_type}")
    require_string(request.get("method"), f"{field_name}.method")
    validate_relative_api_path(request.get("path"), f"{field_name}.path")
    validate_headers(request.get("headers"), f"{field_name}.headers")
    authorization_header: object = request.get("authorization_header")
    if not isinstance(authorization_header, str):
        raise TypeError(f"{field_name}.authorization_header 必须是字符串。")
    require_object(request.get("query"), f"{field_name}.query")
    if "body" not in request:
        raise ValueError(f"{field_name}.body 不得缺失。")
    validate_expected(request.get("expected"), f"{field_name}.expected")
    return request


def validate_dependency(value: object, field_name: str, prior_step_ids: set[str]) -> JsonObject:
    dependency: JsonObject = require_object(value, field_name)
    source_step: str = require_string(dependency.get("source_step"), f"{field_name}.source_step")
    if source_step not in prior_step_ids:
        raise ValueError(f"{field_name}.source_step 必须引用更早的步骤：{source_step}")
    require_string(dependency.get("source_path"), f"{field_name}.source_path")
    target: str = require_string(dependency.get("target"), f"{field_name}.target")
    if target not in {"body", "query"}:
        raise ValueError(f"{field_name}.target 只能是 body 或 query。")
    require_string(dependency.get("target_path"), f"{field_name}.target_path")
    return dependency


def validate_plan(plan: JsonObject, confirmation: JsonObject) -> None:
    if require_integer(plan.get("version"), "plan.version") != 1:
        raise ValueError("plan.version 必须等于 1。")
    if confirmation.get("approved") is not True:
        raise PermissionError("testcase_confirmation.json.approved 必须为 true；请先完成人工审批。")
    testcase_hash: str = require_string(plan.get("testcase_hash"), "plan.testcase_hash")
    approved_hash: str = require_string(confirmation.get("testcase_hash"), "confirmation.testcase_hash")
    if testcase_hash != approved_hash:
        raise PermissionError("执行计划的 testcase_hash 与审批文件不一致；请重新生成并审批计划。")
    seen_ids: set[str] = set()
    for index, raw_request in enumerate(require_list(plan.get("requests"), "plan.requests"), start=1):
        request: JsonObject = validate_request(raw_request, f"plan.requests[{index}]")
        request_id: str = require_string(request.get("id"), f"plan.requests[{index}].id")
        if request_id in seen_ids:
            raise ValueError(f"请求 ID 重复：{request_id}")
        seen_ids.add(request_id)
    for flow_index, raw_flow in enumerate(require_list(plan.get("flows"), "plan.flows"), start=1):
        flow: JsonObject = require_object(raw_flow, f"plan.flows[{flow_index}]")
        require_string(flow.get("id"), f"plan.flows[{flow_index}].id")
        require_string(flow.get("name"), f"plan.flows[{flow_index}].name")
        steps: list[object] = require_list(flow.get("steps"), f"plan.flows[{flow_index}].steps")
        if len(steps) < 2:
            raise ValueError(f"plan.flows[{flow_index}].steps 至少包含两个步骤。")
        prior_step_ids: set[str] = set()
        for step_index, raw_step in enumerate(steps, start=1):
            step_name: str = f"plan.flows[{flow_index}].steps[{step_index}]"
            step: JsonObject = validate_request(raw_step, step_name)
            step_id: str = require_string(step.get("id"), f"{step_name}.id")
            if step_id in prior_step_ids:
                raise ValueError(f"流程步骤 ID 重复：{step_id}")
            for dependency_index, raw_dependency in enumerate(require_list(step.get("dependencies"), f"{step_name}.dependencies"), start=1):
                validate_dependency(raw_dependency, f"{step_name}.dependencies[{dependency_index}]", prior_step_ids)
            prior_step_ids.add(step_id)


def select_environment(config: JsonObject, environment_name: str) -> JsonObject:
    matches: list[JsonObject] = []
    for index, raw_environment in enumerate(require_list(config.get("environments"), "environment_config.environments"), start=1):
        environment: JsonObject = require_object(raw_environment, f"environment_config.environments[{index}]")
        if require_string(environment.get("name"), f"environment_config.environments[{index}].name") == environment_name:
            matches.append(environment)
    if not matches:
        available: list[str] = [
            str(item.get("name")) for item in require_list(config.get("environments"), "environment_config.environments") if isinstance(item, dict)
        ]
        raise LookupError(f"未找到用户确认的平台 {environment_name}；可选平台：{available}")
    if len(matches) != 1:
        raise LookupError(f"平台名称 {environment_name} 存在 {len(matches)} 个候选；请修复配置后重新确认。")
    require_string(matches[0].get("api_domain"), f"environment[{environment_name}].api_domain")
    return matches[0]


def path_tokens(path: str) -> list[str | int]:
    if path == "$":
        return []
    if not path.startswith("$"):
        raise ValueError(f"JSON 路径必须以 $ 开头：{path}")
    suffix: str = path[1:]
    tokens: list[str | int] = []
    position: int = 0
    for match in PATH_TOKEN_PATTERN.finditer(suffix):
        if match.start() != position:
            raise ValueError(f"不支持的 JSON 路径：{path}")
        tokens.append(match.group(1) if match.group(1) is not None else int(match.group(2)))
        position = match.end()
    if position != len(suffix):
        raise ValueError(f"不支持的 JSON 路径：{path}")
    return tokens


def extract_path(value: object, path: str) -> tuple[bool, object]:
    current: object = value
    for token in path_tokens(path):
        if isinstance(token, str) and isinstance(current, dict) and token in current:
            current = current[token]
        elif isinstance(token, int) and isinstance(current, list) and token < len(current):
            current = current[token]
        else:
            return False, None
    return True, current


def replace_path(value: object, path: str, replacement: object) -> object:
    cloned: object = copy.deepcopy(value)
    tokens: list[str | int] = path_tokens(path)
    if not tokens:
        return copy.deepcopy(replacement)
    current: object = cloned
    for token in tokens[:-1]:
        if isinstance(token, str) and isinstance(current, dict) and token in current:
            current = current[token]
        elif isinstance(token, int) and isinstance(current, list) and token < len(current):
            current = current[token]
        else:
            raise ValueError(f"依赖目标路径不存在：{path}")
    final_token: str | int = tokens[-1]
    if isinstance(final_token, str) and isinstance(current, dict) and final_token in current:
        current[final_token] = copy.deepcopy(replacement)
    elif isinstance(final_token, int) and isinstance(current, list) and final_token < len(current):
        current[final_token] = copy.deepcopy(replacement)
    else:
        raise ValueError(f"依赖目标路径不存在：{path}")
    return cloned


def assertion_passed(actual_root: object, assertion: JsonObject) -> tuple[bool, str]:
    path: str = require_string(assertion.get("path"), "assertion.path")
    operator: str = require_string(assertion.get("operator"), "assertion.operator")
    exists, actual = extract_path(actual_root, path)
    expected: object = assertion.get("value")
    if operator == "exists":
        passed: bool = exists
    elif operator == "equals":
        passed = exists and actual == expected
    elif operator == "not_equals":
        passed = exists and actual != expected
    elif operator == "contains":
        if isinstance(actual, str):
            passed = exists and isinstance(expected, str) and expected in actual
        elif isinstance(actual, list):
            passed = exists and expected in actual
        elif isinstance(actual, dict):
            passed = exists and isinstance(expected, str) and expected in actual
        else:
            passed = False
    elif operator == "in":
        if isinstance(expected, str):
            passed = exists and isinstance(actual, str) and actual in expected
        elif isinstance(expected, list):
            passed = exists and actual in expected
        elif isinstance(expected, dict):
            passed = exists and isinstance(actual, str) and actual in expected
        else:
            passed = False
    else:
        raise ValueError(f"不支持的断言操作符：{operator}")
    detail: str = json.dumps({"path": path, "operator": operator, "expected": expected, "actual": actual, "exists": exists}, ensure_ascii=False)
    return passed, detail


def structured_warning(operation: str, attempt: int, reason: str) -> None:
    print(json.dumps({"level": "WARNING", "operation": operation, "attempt": attempt, "reason": reason}, ensure_ascii=False), file=sys.stderr)


def request_once(url: str, method: str, headers: dict[str, str], body: object) -> HttpResult:
    data: bytes | None = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    request: urllib.request.Request = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", errors="replace")


def send_request(url: str, method: str, headers: dict[str, str], body: object) -> HttpResult:
    last_error: urllib.error.URLError | None = None
    for attempt in range(1, 4):
        try:
            status, response_body = request_once(url, method, headers, body)
        except urllib.error.URLError as error:
            last_error = error
            if attempt < 3:
                structured_warning("http_request", attempt, str(error.reason))
                time.sleep(float(attempt))
                continue
            raise ConnectionError(
                f"HTTP 请求失败；method={method}；url={url}；status=不可用；response_body=不可用；"
                f"原因={error.reason}；修复建议=检查网络、域名和测试环境服务状态。"
            ) from error
        if status in RETRYABLE_HTTP_STATUSES and attempt < 3:
            structured_warning("http_request", attempt, f"HTTP {status}: {response_body}")
            time.sleep(float(attempt))
            continue
        return status, response_body
    raise ConnectionError(f"HTTP 请求重试耗尽：{last_error}")


def parse_response_body(response_body: str) -> object:
    try:
        return json.loads(response_body)
    except json.JSONDecodeError:
        return response_body


def is_token_expired(status: int, response: object, token_error_codes: set[str]) -> bool:
    if status in {401, 403}:
        return True
    if not isinstance(response, dict):
        return False
    raw_code: object = response.get("code", response.get("Code"))
    return raw_code is not None and str(raw_code) in token_error_codes


def open_database_connection(database_config: JsonObject) -> Connection:
    required_fields: tuple[str, ...] = ("host", "user", "password", "database")
    values: dict[str, str] = {field: require_string(database_config.get(field), f"database.{field}") for field in required_fields}
    port: int = require_integer(database_config.get("port"), "database.port")
    try:
        return pymysql.connect(
            host=values["host"],
            port=port,
            user=values["user"],
            password=values["password"],
            database=values["database"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )
    except pymysql.MySQLError as error:
        raise ConnectionError(
            f"数据库连接失败；host={values['host']}；port={port}；database={values['database']}；"
            f"原因={error}；修复建议=确认用户选择的平台对应只读连接配置和网络权限。"
        ) from error


def execute_database_assertion(connection: Connection, assertion: JsonObject) -> tuple[list[JsonObject], list[tuple[bool, str]]]:
    sql: str = validate_read_only_sql(require_string(assertion.get("sql"), "database_assertion.sql"), "database_assertion.sql")
    parameters: list[object] = require_list(assertion.get("parameters"), "database_assertion.parameters")
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, tuple(parameters))
            raw_rows: list[JsonObject] = list(cursor.fetchall())
    except pymysql.MySQLError as error:
        raise RuntimeError(
            f"数据库断言查询失败；sql={sql}；parameters={parameters}；status=不适用；response_body=不适用；"
            f"原因={error}；修复建议=核对准备阶段登记的只读 SQL、参数和表结构。"
        ) from error
    results: list[tuple[bool, str]] = [
        assertion_passed(raw_rows, validate_assertion(item, "database_assertion.assertion"))
        for item in require_list(assertion.get("assertions"), "database_assertion.assertions")
    ]
    return raw_rows, results


def redact(value: object) -> object:
    if isinstance(value, dict):
        return {
            str(key): "***" if any(token in str(key).lower() for token in SENSITIVE_TOKENS) else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def build_headers(request: JsonObject, environment: JsonObject) -> dict[str, str]:
    headers: dict[str, str] = validate_headers(request.get("headers"), "request.headers")
    authorization_header: object = request.get("authorization_header")
    if isinstance(authorization_header, str) and authorization_header:
        token: str = require_string(environment.get("authorization"), f"environment[{environment.get('name')}].authorization")
        headers[authorization_header] = token
    return headers


def request_url(environment: JsonObject, request: JsonObject) -> str:
    api_domain: str = require_string(environment.get("api_domain"), "environment.api_domain").rstrip("/")
    path: str = validate_relative_api_path(request.get("path"), "request.path")
    query: JsonObject = require_object(request.get("query"), "request.query")
    query_string: str = urllib.parse.urlencode(query, doseq=True)
    return f"{api_domain}{path}" + (f"?{query_string}" if query_string else "")


def run_request(
    request: JsonObject,
    environment: JsonObject,
    database_config: JsonObject | None,
    token_error_codes: set[str],
) -> tuple[JsonObject, list[tuple[str, str, JsonObject]]]:
    url: str = request_url(environment, request)
    headers: dict[str, str] = build_headers(request, environment)
    method: str = require_string(request.get("method"), "request.method").upper()
    body: object = request.get("body")
    started_at: str = datetime.now(timezone.utc).isoformat()
    status, response_body = send_request(url, method, headers, body)
    parsed_response: object = parse_response_body(response_body)
    if is_token_expired(status, parsed_response, token_error_codes):
        print(f"[TOKEN_EXPIRED_ERROR] {environment.get('name')}", file=sys.stderr)
        raise SystemExit(10)
    expected: JsonObject = require_object(request.get("expected"), "request.expected")
    assertion_results: list[tuple[bool, str]] = []
    expected_status: int = require_integer(expected.get("http_status"), "request.expected.http_status")
    assertion_results.append((status == expected_status, f"HTTP status expected={expected_status}, actual={status}"))
    for raw_assertion in require_list(expected.get("response_assertions"), "request.expected.response_assertions"):
        assertion_results.append(assertion_passed(parsed_response, validate_assertion(raw_assertion, "response_assertion")))
    manifest_rows: list[tuple[str, str, JsonObject]] = []
    database_result_details: list[JsonObject] = []
    database_assertions: list[object] = require_list(expected.get("database_assertions"), "request.expected.database_assertions")
    if database_assertions:
        if database_config is None:
            raise RuntimeError("执行计划包含数据库断言，但 environments_config.json 缺少 database 配置。")
        connection: Connection = open_database_connection(database_config)
        try:
            for raw_database_assertion in database_assertions:
                database_assertion: JsonObject = validate_database_assertion(raw_database_assertion, "database_assertion")
                rows, database_results = execute_database_assertion(connection, database_assertion)
                assertion_results.extend(database_results)
                database_name: str = require_string(database_assertion.get("database"), "database_assertion.database")
                table_name: str = require_string(database_assertion.get("table"), "database_assertion.table")
                manifest_rows.extend((database_name, table_name, row) for row in rows)
                database_result_details.append({"database": database_name, "table": table_name, "row_count": len(rows), "assertions": [detail for _, detail in database_results]})
        finally:
            connection.close()
    passed: bool = all(result for result, _ in assertion_results)
    result: JsonObject = {
        "id": request.get("id"),
        "case_ids": request.get("case_ids"),
        "variant_type": request.get("variant_type"),
        "started_at": started_at,
        "method": method,
        "url": url,
        "headers": redact(headers),
        "body": redact(body),
        "http_status": status,
        "response_body": redact(parsed_response),
        "assertions": [{"passed": item_passed, "detail": detail} for item_passed, detail in assertion_results],
        "database_results": database_result_details,
        "status": "PASS" if passed else "FAIL",
    }
    return result, manifest_rows


def apply_dependencies(step: JsonObject, prior_results: dict[str, JsonObject]) -> JsonObject:
    prepared: JsonObject = copy.deepcopy(step)
    for raw_dependency in require_list(step.get("dependencies"), "flow_step.dependencies"):
        dependency: JsonObject = require_object(raw_dependency, "flow_step.dependency")
        source_step: str = require_string(dependency.get("source_step"), "dependency.source_step")
        source_result: JsonObject = prior_results[source_step]
        exists, source_value = extract_path(source_result.get("response_body"), require_string(dependency.get("source_path"), "dependency.source_path"))
        if not exists:
            raise LookupError(f"步骤 {source_step} 的响应缺少依赖路径 {dependency.get('source_path')}。")
        target: str = require_string(dependency.get("target"), "dependency.target")
        target_path: str = require_string(dependency.get("target_path"), "dependency.target_path")
        prepared[target] = replace_path(prepared.get(target), target_path, source_value)
    return prepared


def execution_error_result(request: JsonObject, error: Exception) -> JsonObject:
    return {
        "id": request.get("id"),
        "case_ids": request.get("case_ids"),
        "variant_type": request.get("variant_type"),
        "status": "EXECUTION_ERROR",
        "error_type": type(error).__name__,
        "error": str(error),
    }


def execute_standalone_requests(
    requests: list[object],
    environment: JsonObject,
    database_config: JsonObject | None,
    token_error_codes: set[str],
) -> tuple[list[JsonObject], list[tuple[str, str, JsonObject]]]:
    results: list[JsonObject] = []
    manifest_rows: list[tuple[str, str, JsonObject]] = []
    for index, raw_request in enumerate(requests, start=1):
        request: JsonObject = validate_request(raw_request, f"requests[{index}]")
        try:
            result, request_rows = run_request(request, environment, database_config, token_error_codes)
            results.append(result)
            manifest_rows.extend(request_rows)
        except SystemExit:
            raise
        except (ConnectionError, LookupError, RuntimeError, TypeError, ValueError) as error:
            results.append(execution_error_result(request, error))
    return results, manifest_rows


def execute_flows(
    flows: list[object],
    environment: JsonObject,
    database_config: JsonObject | None,
    token_error_codes: set[str],
) -> tuple[list[JsonObject], list[tuple[str, str, JsonObject]]]:
    flow_results: list[JsonObject] = []
    manifest_rows: list[tuple[str, str, JsonObject]] = []
    for raw_flow in flows:
        flow: JsonObject = require_object(raw_flow, "flow")
        step_results: list[JsonObject] = []
        prior_results: dict[str, JsonObject] = {}
        interrupted: bool = False
        interruption_reason: str = ""
        for raw_step in require_list(flow.get("steps"), "flow.steps"):
            step: JsonObject = require_object(raw_step, "flow.step")
            step_id: str = require_string(step.get("id"), "flow.step.id")
            if interrupted:
                step_results.append({"id": step_id, "case_ids": step.get("case_ids"), "status": "NOT_EXECUTED", "reason": interruption_reason})
                continue
            try:
                prepared_step: JsonObject = apply_dependencies(step, prior_results)
                result, step_rows = run_request(prepared_step, environment, database_config, token_error_codes)
                step_results.append(result)
                prior_results[step_id] = result
                manifest_rows.extend(step_rows)
                if result.get("status") != "PASS":
                    interrupted = True
                    interruption_reason = f"步骤 {step_id} 断言失败。"
            except SystemExit:
                raise
            except (ConnectionError, LookupError, RuntimeError, TypeError, ValueError) as error:
                error_result: JsonObject = execution_error_result(step, error)
                step_results.append(error_result)
                prior_results[step_id] = error_result
                interrupted = True
                interruption_reason = f"步骤 {step_id} 执行异常：{error}"
        flow_results.append(
            {
                "id": flow.get("id"),
                "name": flow.get("name"),
                "status": "INTERRUPTED" if interrupted else "PASS",
                "interruption_reason": interruption_reason,
                "steps": step_results,
            }
        )
    return flow_results, manifest_rows


def markdown_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def render_interface_report(results: list[JsonObject], environment_name: str) -> str:
    executed: list[JsonObject] = [item for item in results if item.get("status") in {"PASS", "FAIL"}]
    passed_count: int = sum(1 for item in executed if item.get("status") == "PASS")
    pass_rate: float = (passed_count / len(executed) * 100.0) if executed else 0.0
    lines: list[str] = [
        "# 单接口测试执行报告",
        "",
        f"- 生成时间：{datetime.now(timezone.utc).isoformat()}",
        f"- 测试平台：{environment_name}",
        f"- 计划用例数：{len(results)}",
        f"- 实际断言用例数：{len(executed)}",
        f"- 通过率：{pass_rate:.2f}%",
        "",
        "| 请求 ID | Case IDs | 类型 | 状态 | HTTP 状态 |",
        "|---|---|---|---|---:|",
    ]
    for result in results:
        lines.append(f"| {result.get('id')} | {', '.join(str(item) for item in result.get('case_ids', []))} | {result.get('variant_type')} | {result.get('status')} | {result.get('http_status', '')} |")
    for result in results:
        lines.extend(["", f"## {result.get('id')}", "", "```json", markdown_json(result), "```"])
    return "\n".join(lines).strip() + "\n"


def render_flow_report(results: list[JsonObject], environment_name: str) -> str:
    lines: list[str] = [
        "# 核心流程测试执行报告",
        "",
        f"- 生成时间：{datetime.now(timezone.utc).isoformat()}",
        f"- 测试平台：{environment_name}",
    ]
    if not results:
        lines.extend(["", "- 本次计划未定义核心流程。"])
    for result in results:
        lines.extend(["", f"## {result.get('name')}", "", f"- 流程 ID：{result.get('id')}", f"- 状态：{result.get('status')}", f"- 中断原因：{result.get('interruption_reason') or '无'}", "", "```json", markdown_json(result), "```"])
    return "\n".join(lines).strip() + "\n"


def append_manifest(path: Path, rows: list[tuple[str, str, JsonObject]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    existing: str = path.read_text(encoding="utf-8-sig") if path.exists() else "# 测试数据台账\n"
    execution_lines: list[str] = ["", f"## 执行校验 {datetime.now(timezone.utc).isoformat()}"]
    execution_lines.extend(
        f"{database}:{table}:【{json.dumps(row, ensure_ascii=False, separators=(',', ':'))}】"
        for database, table, row in rows
    )
    path.write_text(existing.rstrip() + "\n" + "\n".join(execution_lines) + "\n", encoding="utf-8", newline="\n")


def write_reports(output_dir: Path, interface_report: str, flow_report: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "interface_test_execution_report.md").write_text(interface_report, encoding="utf-8", newline="\n")
    (output_dir / "core_flow_test_execution_report.md").write_text(flow_report, encoding="utf-8", newline="\n")


def main() -> int:
    arguments: argparse.Namespace = parse_arguments()
    workspace: Path = Path(arguments.workspace).resolve()
    if not workspace.is_dir():
        raise NotADirectoryError(f"工作区不存在：{workspace}")
    plan_path: Path = resolve_workspace_path(workspace, arguments.plan, "--plan")
    confirmation_path: Path = resolve_workspace_path(workspace, arguments.confirmation, "--confirmation")
    environment_path: Path = resolve_workspace_path(workspace, arguments.environment_config, "--environment-config")
    output_dir: Path = resolve_workspace_path(workspace, arguments.output_dir, "--output-dir")
    manifest_path: Path = resolve_workspace_path(workspace, arguments.manifest, "--manifest")
    plan: JsonObject = read_json_object(plan_path, "execution_plan")
    confirmation: JsonObject = read_json_object(confirmation_path, "testcase_confirmation")
    environment_config: JsonObject = read_json_object(environment_path, "environment_config")
    validate_plan(plan, confirmation)
    environment: JsonObject = select_environment(environment_config, arguments.environment_name)
    raw_token_error_codes: list[object] = require_list(plan.get("token_error_codes", []), "plan.token_error_codes")
    token_error_codes: set[str] = {require_string(item, "plan.token_error_codes[]") for item in raw_token_error_codes}
    raw_database_config: object = environment_config.get("database")
    database_config: JsonObject | None = require_object(raw_database_config, "environment_config.database") if raw_database_config is not None else None
    interface_results, interface_rows = execute_standalone_requests(
        require_list(plan.get("requests"), "plan.requests"), environment, database_config, token_error_codes
    )
    flow_results, flow_rows = execute_flows(
        require_list(plan.get("flows"), "plan.flows"), environment, database_config, token_error_codes
    )
    write_reports(
        output_dir,
        render_interface_report(interface_results, arguments.environment_name),
        render_flow_report(flow_results, arguments.environment_name),
    )
    append_manifest(manifest_path, interface_rows + flow_rows)
    has_execution_errors: bool = any(result.get("status") == "EXECUTION_ERROR" for result in interface_results)
    has_flow_errors: bool = any(result.get("status") == "INTERRUPTED" for result in flow_results)
    has_failures: bool = any(result.get("status") == "FAIL" for result in interface_results)
    return 1 if has_execution_errors or has_flow_errors or has_failures else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ConnectionError, FileNotFoundError, LookupError, NotADirectoryError, PermissionError, RuntimeError, TypeError, ValueError) as error:
        print(f"[EXECUTION_ERROR] {type(error).__name__}: {error}", file=sys.stderr)
        raise SystemExit(2) from error
