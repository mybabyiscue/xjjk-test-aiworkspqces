"""Strict CodeGraph environment and per-project index management."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Final


SETUP_SCRIPT_NAME: Final[str] = "setup_codegraph.ps1"


class CodeGraphEnvironmentError(RuntimeError):
    """Raised when CodeGraph cannot be used safely by the review workflow."""


class CodeGraphCommandError(RuntimeError):
    """Raised when a CodeGraph command fails."""


@dataclass(frozen=True)
class CodeGraphEnvironment:
    executable: Path
    version: str
    codex_config: Path


@dataclass(frozen=True)
class CodeGraphIndexResult:
    project_root: Path
    action: str
    status_output: str


def setup_script_path() -> Path:
    return Path(__file__).resolve().with_name(SETUP_SCRIPT_NAME)


def codex_config_path() -> Path:
    codex_home = os.environ.get("CODEX_HOME", "").strip()
    return Path(codex_home) / "config.toml" if codex_home else Path.home() / ".codex" / "config.toml"


def read_codex_mcp_registration(config_path: Path) -> tuple[str, tuple[str, ...], bool]:
    if not config_path.is_file():
        return "", (), False
    try:
        payload = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise CodeGraphEnvironmentError(f"Cannot read Codex MCP config {config_path}: {exc}") from exc
    servers = payload.get("mcp_servers")
    if not isinstance(servers, dict):
        return "", (), False
    registration = servers.get("codegraph")
    if not isinstance(registration, dict):
        return "", (), False
    command = registration.get("command")
    args = registration.get("args")
    enabled = registration.get("enabled", True)
    command_text = command.strip() if isinstance(command, str) else ""
    arg_values = tuple(value for value in args if isinstance(value, str)) if isinstance(args, list) else ()
    return command_text, arg_values, enabled is not False


def assert_codegraph_environment() -> CodeGraphEnvironment:
    executable_text = shutil.which("codegraph")
    remediation = (
        f"Run PowerShell script: {setup_script_path()}\n"
        "After it completes, restart Codex and run tapd-code-source-review again."
    )
    if executable_text is None:
        raise CodeGraphEnvironmentError(f"CodeGraph CLI is not installed or is not on PATH.\n{remediation}")

    executable = Path(executable_text).resolve()
    version_result = run_codegraph_command(executable, ["version"], Path.cwd(), 30)
    version = version_result.stdout.strip()
    if not version:
        raise CodeGraphEnvironmentError(f"CodeGraph returned an empty version.\n{remediation}")

    config_path = codex_config_path()
    command, args, enabled = read_codex_mcp_registration(config_path)
    registered_command = Path(command).name.lower() in {"codegraph", "codegraph.cmd", "codegraph.exe", "codegraph.ps1"}
    registered_args = "serve" in args and "--mcp" in args
    if not (registered_command and registered_args and enabled):
        raise CodeGraphEnvironmentError(
            f"CodeGraph MCP is not registered and enabled in {config_path}.\n{remediation}"
        )
    return CodeGraphEnvironment(executable=executable, version=version, codex_config=config_path)


def prepare_codegraph_index(environment: CodeGraphEnvironment, project_root: Path) -> CodeGraphIndexResult:
    resolved_root = project_root.resolve()
    if not resolved_root.is_dir():
        raise CodeGraphCommandError(f"CodeGraph project root does not exist: {resolved_root}")
    database_path = resolved_root / ".codegraph" / "codegraph.db"
    action = "sync" if database_path.is_file() else "init"
    run_codegraph_command(environment.executable, [action, str(resolved_root)], resolved_root, 900)
    status = run_codegraph_command(environment.executable, ["status", str(resolved_root)], resolved_root, 120)
    if not database_path.is_file():
        raise CodeGraphCommandError(
            f"CodeGraph {action} completed without creating the index database: {database_path}"
        )
    return CodeGraphIndexResult(project_root=resolved_root, action=action, status_output=status.stdout.strip())


def run_codegraph_json(
    environment: CodeGraphEnvironment,
    arguments: list[str],
    project_root: Path,
    timeout_seconds: int,
) -> dict[str, object]:
    completed = run_codegraph_command(environment.executable, arguments, project_root, timeout_seconds)
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise CodeGraphCommandError(
            f"CodeGraph returned invalid JSON for arguments {arguments}: {completed.stdout}"
        ) from exc
    if not isinstance(payload, dict):
        raise CodeGraphCommandError(f"CodeGraph returned a non-object JSON payload for arguments {arguments}")
    return payload


def run_codegraph_command(
    executable: Path,
    arguments: list[str],
    working_directory: Path,
    timeout_seconds: int,
) -> subprocess.CompletedProcess[str]:
    command = [str(executable), *arguments]
    try:
        return subprocess.run(
            command,
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=True,
        )
    except subprocess.TimeoutExpired as exc:
        raise CodeGraphCommandError(
            f"CodeGraph command timed out after {timeout_seconds}s: {command}; stdout={exc.stdout}; stderr={exc.stderr}"
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise CodeGraphCommandError(
            f"CodeGraph command failed: {command}; exit_code={exc.returncode}; stdout={exc.stdout}; stderr={exc.stderr}"
        ) from exc

