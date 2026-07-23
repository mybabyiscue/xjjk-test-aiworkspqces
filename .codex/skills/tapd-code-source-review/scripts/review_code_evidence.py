"""Reject the removed legacy evidence generator."""

from __future__ import annotations


def main() -> int:
    raise RuntimeError(
        "review_code_evidence.py was retired because it contained domain-specific mappings and "
        "could write directly to latest. Follow SKILL.md and use prepare_review_run.py plus "
        "analyze_testcase_evidence.py."
    )


if __name__ == "__main__":
    raise SystemExit(main())
