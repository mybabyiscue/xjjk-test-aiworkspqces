"""Validate and refresh one configured API environment token."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import TYPE_CHECKING, Literal, NotRequired, TypeAlias, TypedDict, cast
from urllib.parse import SplitResult, parse_qsl, urlencode, urlsplit, urlunsplit

JsonValue: TypeAlias = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
GateStatus: TypeAlias = Literal["valid", "expired", "error"]

SENSITIVE_HEADER_NAMES: frozenset[str] = frozenset(
    {"authorization", "cookie", "proxy-authorization", "x-api-key", "api-key"}
)
STANDARD_UNAUTHORIZED_STATUSES: frozenset[int] = frozenset({401, 403})

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


class TokenProbeConfig(TypedDict):
    url: str
    headers: dict[str, str]
    response_code_path: str
    success_codes: list[str]
    unauthorized_codes: list[str]


class EnvironmentConfig(TypedDict):
    name: str
    api_domain: str
    authorization: str
    login_url: NotRequired[str]
    account: NotRequired[str]
    password: NotRequired[str]
    token_probe: NotRequired[TokenProbeConfig]


class HttpResult(TypedDict):
    status: int
    body: str


class ProbeEvaluation(TypedDict):
    status: GateStatus
    response_code: str
    reason: str
    http_status: int
    response_body: str


class GateResult(TypedDict):
    environment_name: str
    status: Literal["valid", "refreshed"]
    authorization_updated: bool


class TokenGateError(RuntimeError):
    """Raised when the configured token cannot be validated or refreshed."""


def require_object(value: object, field_name: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise TokenGateError(f"{field_name} 必须是对象。")
    return cast(dict[str, object], value)


def require_list(value: object, field_name: str) -> list[object]:
    if not isinstance(value, list):
        raise TokenGateError(f"{field_name} 必须是数组。")
    return cast(list[object], value)


def require_string(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TokenGateError(f"{field_name} 必须是非空字符串。")
    return value.strip()


def optional_string(value: object, field_name: str) -> str | None:
    if value is None:
        return None
    return require_string(value, field_name)


def require_string_list(value: object, field_name: str) -> list[str]:
    raw_items: list[object] = require_list(value, field_name)
    items: list[str] = []
    for index, raw_item in enumerate(raw_items):
        items.append(require_string(raw_item, f"{field_name}[{index}]"))
    return items


def validate_probe(value: object, api_domain: str, field_name: str) -> TokenProbeConfig:
    raw_probe: dict[str, object] = require_object(value, field_name)
    url: str = require_string(raw_probe.get("url"), f"{field_name}.url")
    if url.rstrip("/") == api_domain.rstrip("/"):
        raise TokenGateError(f"{field_name}.url 不能是 api_domain 根地址。")
    raw_headers: dict[str, object] = require_object(raw_probe.get("headers"), f"{field_name}.headers")
    headers: dict[str, str] = {}
    for raw_name, raw_value in raw_headers.items():
        header_name: str = require_string(raw_name, f"{field_name}.headers.name")
        if header_name.lower() in SENSITIVE_HEADER_NAMES:
            raise TokenGateError(f"{field_name}.headers 禁止包含敏感 Header：{header_name}。")
        headers[header_name] = require_string(raw_value, f"{field_name}.headers.{header_name}")
    response_code_path_value: object = raw_probe.get("response_code_path")
    if not isinstance(response_code_path_value, str):
        raise TokenGateError(f"{field_name}.response_code_path 必须是字符串。")
    response_code_path: str = response_code_path_value.strip()
    success_codes: list[str] = require_string_list(raw_probe.get("success_codes"), f"{field_name}.success_codes")
    unauthorized_codes: list[str] = require_string_list(
        raw_probe.get("unauthorized_codes"),
        f"{field_name}.unauthorized_codes",
    )
    if response_code_path and not response_code_path.startswith("$."):
        raise TokenGateError(f"{field_name}.response_code_path 只支持以 $. 开头的对象路径。")
    if response_code_path and not success_codes:
        raise TokenGateError(f"{field_name}.success_codes 在配置应用响应码路径时不得为空。")
    if not response_code_path and (success_codes or unauthorized_codes):
        raise TokenGateError(f"{field_name} 未配置应用响应码路径时，业务码数组必须为空。")
    return {
        "url": url,
        "headers": headers,
        "response_code_path": response_code_path,
        "success_codes": success_codes,
        "unauthorized_codes": unauthorized_codes,
    }


def validate_environment(value: object, field_name: str) -> EnvironmentConfig:
    raw_environment: dict[str, object] = require_object(value, field_name)
    forbidden_fields: tuple[str, ...] = (
        "credentials_ref",
        "healthcheck_success_code",
        "healthcheck_unauthorized_codes",
    )
    present_forbidden_fields: list[str] = [name for name in forbidden_fields if name in raw_environment]
    if present_forbidden_fields:
        joined_fields: str = ", ".join(present_forbidden_fields)
        raise TokenGateError(f"{field_name} 包含不再支持的旧字段：{joined_fields}。")
    name: str = require_string(raw_environment.get("name"), f"{field_name}.name")
    api_domain: str = require_string(raw_environment.get("api_domain"), f"{field_name}.api_domain")
    authorization: str = require_string(raw_environment.get("authorization"), f"{field_name}.authorization")
    login_url: str | None = optional_string(raw_environment.get("login_url"), f"{field_name}.login_url")
    account: str | None = optional_string(raw_environment.get("account"), f"{field_name}.account")
    password: str | None = optional_string(raw_environment.get("password"), f"{field_name}.password")
    login_values: tuple[str | None, str | None, str | None] = (login_url, account, password)
    if any(item is not None for item in login_values) and not all(item is not None for item in login_values):
        raise TokenGateError(f"{field_name} 的 login_url、account、password 必须同时存在或同时不存在。")
    environment: EnvironmentConfig = {
        "name": name,
        "api_domain": api_domain,
        "authorization": authorization,
    }
    if login_url is not None and account is not None and password is not None:
        environment = {
            **environment,
            "login_url": login_url,
            "account": account,
            "password": password,
        }
    raw_probe: object = raw_environment.get("token_probe")
    if raw_probe is not None:
        environment = {
            **environment,
            "token_probe": validate_probe(raw_probe, api_domain, f"{field_name}.token_probe"),
        }
    return environment


def load_configuration(config_path: Path) -> dict[str, object]:
    try:
        raw_text: str = config_path.read_text(encoding="utf-8-sig")
    except FileNotFoundError as error:
        raise TokenGateError(f"环境配置不存在：{config_path}。修复建议：创建工作区本地配置文件。") from error
    try:
        raw_payload: JsonValue = cast(JsonValue, json.loads(raw_text))
    except json.JSONDecodeError as error:
        raise TokenGateError(f"环境配置不是合法 JSON：{config_path}。修复建议：修复第 {error.lineno} 行。") from error
    return require_object(raw_payload, "config")


def select_environment(config_path: Path, environment_name: str) -> EnvironmentConfig:
    payload: dict[str, object] = load_configuration(config_path)
    raw_environments: list[object] = require_list(payload.get("environments"), "config.environments")
    matches: list[tuple[int, object]] = []
    for index, raw_environment in enumerate(raw_environments):
        environment_object: dict[str, object] = require_object(raw_environment, f"config.environments[{index}]")
        if environment_object.get("name") == environment_name:
            matches.append((index, raw_environment))
    if len(matches) != 1:
        raise TokenGateError(
            f"环境名必须唯一匹配，实际匹配数：{len(matches)}。请求参数：environment_name={environment_name!r}。"
        )
    selected_index: int = matches[0][0]
    return validate_environment(matches[0][1], f"config.environments[{selected_index}]")


def sanitize_url(url: str) -> str:
    parts: SplitResult = urlsplit(url)
    redacted_query: str = urlencode([(name, "***") for name, _ in parse_qsl(parts.query, keep_blank_values=True)])
    return urlunsplit((parts.scheme, parts.netloc, parts.path, redacted_query, ""))


def redact_text(value: str, secrets: tuple[str, ...]) -> str:
    redacted: str = value
    for secret in secrets:
        if secret:
            redacted = redacted.replace(secret, "***")
    patterns: tuple[str, ...] = (
        r'(?i)("?(?:authorization|password|account|token|cookie)"?\s*[:=]\s*")[^"]*(")',
        r"(?i)((?:authorization|password|account|token|cookie)\s*[:=]\s*)[^\s,;]+",
    )
    for pattern in patterns:
        redacted = re.sub(pattern, r"\1***\2" if pattern.endswith('(")') else r"\1***", redacted)
    return redacted[:2000]


def emit_warning(
    environment_name: str,
    url: str,
    attempt: int,
    retry_count: int,
    evaluation: ProbeEvaluation,
    secrets: tuple[str, ...],
) -> None:
    warning: dict[str, object] = {
        "level": "warning",
        "event": "token_probe_failed",
        "environment_name": environment_name,
        "url": sanitize_url(url),
        "attempt": attempt,
        "retry_count": retry_count,
        "http_status": evaluation["http_status"],
        "reason": evaluation["reason"],
        "response_body": redact_text(evaluation["response_body"], secrets),
        "suggestion": "检查探测规则、网络状态或登录能力。",
    }
    print(json.dumps(warning, ensure_ascii=False), file=sys.stderr)


def request_probe(probe: TokenProbeConfig, authorization: str, timeout_seconds: int) -> HttpResult:
    headers: dict[str, str] = {**probe["headers"], "Authorization": authorization}
    request: urllib.request.Request = urllib.request.Request(probe["url"], headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            status: int = response.status
            body: str = response.read().decode("utf-8", errors="replace")
            return {"status": status, "body": body}
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        return {"status": error.code, "body": body}
    except urllib.error.URLError as error:
        reason: str = str(error.reason)
        return {"status": 0, "body": f"network_error: {reason}"}


def extract_response_code(body: str, response_code_path: str) -> str:
    try:
        payload: JsonValue = cast(JsonValue, json.loads(body))
    except json.JSONDecodeError as error:
        raise TokenGateError("Token 探测响应不是合法 JSON。修复建议：检查 response_code_path 或探测端点。") from error
    current: JsonValue = payload
    for field_name in response_code_path[2:].split("."):
        if not isinstance(current, dict) or field_name not in current:
            raise TokenGateError(
                f"Token 探测响应缺少配置路径 {response_code_path}。修复建议：核对 token_probe.response_code_path。"
            )
        current = current[field_name]
    if not isinstance(current, (str, int, float)) or isinstance(current, bool):
        raise TokenGateError(f"Token 探测响应路径 {response_code_path} 必须指向字符串或数字。")
    return str(current)


def evaluate_probe(result: HttpResult, probe: TokenProbeConfig) -> ProbeEvaluation:
    http_status: int = result["status"]
    body: str = result["body"]
    if http_status in STANDARD_UNAUTHORIZED_STATUSES:
        return {
            "status": "expired",
            "response_code": "",
            "reason": "HTTP 鉴权状态表示 Token 无效。",
            "http_status": http_status,
            "response_body": body,
        }
    if http_status < 200 or http_status >= 300:
        return {
            "status": "error",
            "response_code": "",
            "reason": "探测端点返回非成功 HTTP 状态。",
            "http_status": http_status,
            "response_body": body,
        }
    response_code_path: str = probe["response_code_path"]
    if not response_code_path:
        return {
            "status": "valid",
            "response_code": "",
            "reason": "HTTP 鉴权探测成功。",
            "http_status": http_status,
            "response_body": body,
        }
    response_code: str = extract_response_code(body, response_code_path)
    if response_code in probe["unauthorized_codes"]:
        return {
            "status": "expired",
            "response_code": response_code,
            "reason": "应用响应码表示 Token 无效。",
            "http_status": http_status,
            "response_body": body,
        }
    if response_code in probe["success_codes"]:
        return {
            "status": "valid",
            "response_code": response_code,
            "reason": "应用鉴权探测成功。",
            "http_status": http_status,
            "response_body": body,
        }
    return {
        "status": "error",
        "response_code": response_code,
        "reason": "应用响应码既非成功码也非未授权码。",
        "http_status": http_status,
        "response_body": body,
    }


def probe_token(
    environment: EnvironmentConfig,
    authorization: str,
    timeout_seconds: int,
    retry_count: int,
) -> ProbeEvaluation:
    probe: TokenProbeConfig = environment["token_probe"]
    secrets: tuple[str, ...] = (
        environment.get("account", ""),
        environment.get("password", ""),
        authorization,
    )
    last_evaluation: ProbeEvaluation | None = None
    for attempt in range(1, retry_count + 1):
        result: HttpResult = request_probe(probe, authorization, timeout_seconds)
        evaluation: ProbeEvaluation = evaluate_probe(result, probe)
        if evaluation["status"] == "valid":
            return evaluation
        emit_warning(environment["name"], probe["url"], attempt, retry_count, evaluation, secrets)
        last_evaluation = evaluation
    if last_evaluation is None:
        raise TokenGateError("retry_count 必须大于 0。")
    return last_evaluation


def has_login_capability(environment: EnvironmentConfig) -> bool:
    return all(field_name in environment for field_name in ("login_url", "account", "password"))


def stable_locator(page: Page, candidate_selector: str, field_name: str) -> Locator:
    candidates: Locator = page.locator(candidate_selector)
    stable_candidates: list[Locator] = []
    for index in range(candidates.count()):
        candidate: Locator = candidates.nth(index)
        if not candidate.is_visible():
            continue
        test_id: str | None = candidate.get_attribute("data-testid")
        element_id: str | None = candidate.get_attribute("id")
        aria_label: str | None = candidate.get_attribute("aria-label")
        resolved: Locator | None = None
        if test_id:
            resolved = page.get_by_test_id(test_id)
        elif element_id:
            resolved = page.locator(f"[id={json.dumps(element_id)}]")
        elif aria_label:
            resolved = page.get_by_label(aria_label, exact=True)
        if resolved is not None and resolved.count() == 1:
            stable_candidates.append(resolved)
    if len(stable_candidates) != 1:
        raise TokenGateError(
            f"无法为{field_name}确定唯一 Stable ID、Test ID 或 Accessibility ID。"
            "修复建议：为登录控件增加唯一稳定标识。"
        )
    return stable_candidates[0]


def refresh_token_with_browser(environment: EnvironmentConfig, browser_timeout_ms: int) -> str:
    from playwright.sync_api import Browser, Error as PlaywrightError, Locator, Page, Request, sync_playwright

    if not has_login_capability(environment):
        raise TokenGateError("Token 已失效且环境没有完整登录能力。修复建议：更新 authorization 或补齐登录字段。")
    login_url: str = environment["login_url"]
    account: str = environment["account"]
    password: str = environment["password"]
    api_netloc: str = urlsplit(environment["api_domain"]).netloc.lower()
    current_authorization: str = environment["authorization"]
    captured_authorizations: set[str] = set()

    def capture_authorization(request: Request) -> None:
        request_netloc: str = urlsplit(request.url).netloc.lower()
        authorization: str = request.headers.get("authorization", "").strip()
        if request_netloc == api_netloc and authorization and authorization != current_authorization:
            captured_authorizations.add(authorization)

    try:
        with sync_playwright() as playwright:
            browser: Browser = playwright.chromium.launch(headless=True)
            try:
                page: Page = browser.new_page()
                page.set_default_timeout(browser_timeout_ms)
                page.goto(login_url, wait_until="domcontentloaded")
                account_locator: Locator = cast(
                    Locator,
                    stable_locator(
                        page,
                        "input:not([type=password]):not([type=hidden]):not([type=checkbox]):"
                        "not([type=radio]):not([type=submit])",
                        "账号输入框",
                    ),
                )
                password_locator: Locator = cast(
                    Locator,
                    stable_locator(page, "input[type=password]", "密码输入框"),
                )
                submit_locator: Locator = cast(
                    Locator,
                    stable_locator(page, "button[type=submit],input[type=submit]", "登录提交控件"),
                )
                account_locator.fill(account)
                password_locator.fill(password)
                page.on("request", capture_authorization)
                submit_locator.click()
                deadline: float = time.monotonic() + browser_timeout_ms / 1000
                while not captured_authorizations and time.monotonic() < deadline:
                    page.wait_for_timeout(100)
            finally:
                browser.close()
    except PlaywrightError:
        raise TokenGateError(
            "Playwright 登录失败。修复建议：检查登录页、稳定控件标识、验证码或租户选择状态。"
        ) from None
    if len(captured_authorizations) != 1:
        raise TokenGateError(
            f"登录后捕获到的不同 Authorization 数量为 {len(captured_authorizations)}。"
            "修复建议：处理登录失败、租户歧义或多 Token 来源。"
        )
    return next(iter(captured_authorizations))


def update_authorization(config_path: Path, environment_name: str, authorization: str) -> None:
    payload: dict[str, object] = load_configuration(config_path)
    raw_environments: list[object] = require_list(payload.get("environments"), "config.environments")
    match_count: int = 0
    updated_environments: list[object] = []
    for index, raw_environment in enumerate(raw_environments):
        environment_object: dict[str, object] = require_object(raw_environment, f"config.environments[{index}]")
        if environment_object.get("name") == environment_name:
            match_count += 1
            updated_environments.append({**environment_object, "authorization": authorization})
        else:
            updated_environments.append(environment_object)
    if match_count != 1:
        raise TokenGateError(f"写回 Token 时环境匹配数为 {match_count}，已拒绝修改。")
    updated_payload: dict[str, object] = {**payload, "environments": updated_environments}
    serialized: str = json.dumps(updated_payload, ensure_ascii=False, indent=2) + "\n"
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=config_path.parent,
            prefix=f".{config_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_file.write(serialized)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
            temporary_path = Path(temporary_file.name)
        os.replace(temporary_path, config_path)
    except OSError as error:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
        raise TokenGateError(f"原子写回环境 Token 失败：{config_path}。修复建议：检查文件权限。") from error


def ensure_git_ignored(config_path: Path) -> None:
    repository_path: Path = config_path.resolve().parent.parent
    try:
        relative_path: Path = config_path.resolve().relative_to(repository_path)
    except ValueError as error:
        raise TokenGateError("环境配置必须位于当前工作区 config 目录。") from error
    completed: subprocess.CompletedProcess[str] = subprocess.run(
        ["git", "-C", str(repository_path), "check-ignore", "--quiet", str(relative_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise TokenGateError(
            f"环境配置未被 Git 忽略：{config_path}。修复建议：先将该本地凭证文件加入 .gitignore。"
        )


def run_token_gate(
    config_path: Path,
    environment_name: str,
    request_timeout_seconds: int,
    retry_count: int,
    browser_timeout_ms: int,
) -> GateResult:
    if request_timeout_seconds < 1 or retry_count < 1 or browser_timeout_ms < 1:
        raise TokenGateError("超时和重试参数必须为正整数。")
    environment: EnvironmentConfig = select_environment(config_path, environment_name)
    probe: TokenProbeConfig | None = environment.get("token_probe")
    if probe is not None:
        evaluation: ProbeEvaluation = probe_token(
            environment,
            environment["authorization"],
            request_timeout_seconds,
            retry_count,
        )
        if evaluation["status"] == "valid":
            return {"environment_name": environment_name, "status": "valid", "authorization_updated": False}
        if evaluation["status"] == "error":
            raise TokenGateError(
                "Token 探测失败且不能判定为鉴权失效。"
                f"请求参数：url={sanitize_url(probe['url'])}；HTTP Status Code：{evaluation['http_status']}；"
                f"Response Body：{redact_text(evaluation['response_body'], (environment['authorization'],))}；"
                "修复建议：核对 token_probe 数据规则和端点状态。"
            )
    if not has_login_capability(environment):
        raise TokenGateError(
            "Token 无法验证或已失效，且环境没有完整登录能力。"
            "修复建议：更新 authorization，或同时配置 login_url、account、password。"
        )
    refreshed_authorization: str = refresh_token_with_browser(environment, browser_timeout_ms)
    refreshed_environment: EnvironmentConfig = {**environment, "authorization": refreshed_authorization}
    if probe is not None:
        refreshed_evaluation: ProbeEvaluation = probe_token(
            refreshed_environment,
            refreshed_authorization,
            request_timeout_seconds,
            retry_count,
        )
        if refreshed_evaluation["status"] != "valid":
            raise TokenGateError(
                "新 Token 复验失败。修复建议：检查登录账号权限、探测规则或租户选择。"
            )
    update_authorization(config_path, environment_name, refreshed_authorization)
    return {"environment_name": environment_name, "status": "refreshed", "authorization_updated": True}


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--environment-name", required=True)
    parser.add_argument("--request-timeout-seconds", required=True, type=int)
    parser.add_argument("--retry-count", required=True, type=int)
    parser.add_argument("--browser-timeout-ms", required=True, type=int)
    return parser.parse_args(arguments)


def main(arguments: list[str]) -> int:
    parsed: argparse.Namespace = parse_arguments(arguments)
    config_path: Path = Path(parsed.config)
    try:
        ensure_git_ignored(config_path)
        result: GateResult = run_token_gate(
            config_path,
            str(parsed.environment_name),
            int(parsed.request_timeout_seconds),
            int(parsed.retry_count),
            int(parsed.browser_timeout_ms),
        )
    except TokenGateError as error:
        print(str(error), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
