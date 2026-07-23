"""Ensure the domain-specific legacy generator cannot run."""

from __future__ import annotations

import pytest

from scripts.review_code_evidence import main


def test_legacy_generator_is_rejected() -> None:
    with pytest.raises(RuntimeError, match="retired"):
        main()
