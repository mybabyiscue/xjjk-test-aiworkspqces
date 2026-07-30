"""Tests for external source fetch retry behavior."""

from __future__ import annotations

import logging
from pathlib import Path
import subprocess

import pytest

from scripts import fetch_code_sources
from scripts.fetch_code_sources import fetch_git, retry_external_operation


def test_fetch_git_fast_forwards_existing_branch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "repo"
    (target / ".git").mkdir(parents=True)
    commands: list[list[str]] = []

    def record_git(command: list[str]) -> str:
        commands.append(command)
        if command[-2:] == ["rev-parse", "HEAD"]:
            return "new-commit\n"
        if command[-3:] == ["rev-parse", "--abbrev-ref", "HEAD"]:
            return "feature-123\n"
        return ""

    monkeypatch.setattr(fetch_code_sources, "run_git", record_git)
    source: dict[str, str] = {
        "input_url": "https://example.test/service.git",
        "branch": "feature-123",
    }

    fetch_git(source, target)

    assert ["git", "-C", str(target), "merge", "--ff-only", "origin/feature-123"] in commands
    assert source["commit"] == "new-commit"
    assert source["branch"] == "feature-123"


def test_retry_external_operation_succeeds_after_retry(
    caplog: pytest.LogCaptureFixture,
) -> None:
    attempts: list[int] = []

    def operation() -> str:
        attempts.append(len(attempts) + 1)
        if len(attempts) < 3:
            raise OSError("temporary failure")
        return "success"

    with caplog.at_level(logging.WARNING):
        result = retry_external_operation(operation, "download", {"url": "https://example.test/source.zip"}, 3)

    assert result == "success"
    assert attempts == [1, 2, 3]
    assert [record.attempt for record in caplog.records] == [1, 2]
    assert all(record.operation == "download" for record in caplog.records)


def test_retry_external_operation_raises_last_error() -> None:
    errors = [
        subprocess.CalledProcessError(1, ["git", "fetch"]),
        subprocess.CalledProcessError(2, ["git", "fetch"]),
    ]

    def operation() -> str:
        raise errors.pop(0)

    with pytest.raises(subprocess.CalledProcessError) as caught:
        retry_external_operation(operation, "git", {"command": ["git", "fetch"]}, 2)

    assert caught.value.returncode == 2
    assert errors == []
