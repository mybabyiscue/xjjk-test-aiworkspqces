"""Tests for external source fetch retry behavior."""

from __future__ import annotations

import logging
import subprocess

import pytest

from scripts.fetch_code_sources import retry_external_operation


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
