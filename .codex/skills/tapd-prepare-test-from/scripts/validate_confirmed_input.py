"""Validate the confirmed testcase and code-review input snapshot."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from preparation_contract import PreparationError, file_sha256, load_cases, read_json_object, require_string, write_json_object


def parse_arguments() -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="校验已确认用例与代码复审输入一致性。")
    parser.add_argument("--confirmation", required=True)
    parser.add_argument("--test-cases", required=True)
    parser.add_argument("--tapd-cases", required=True)
    parser.add_argument("--evidence-index", required=True)
    parser.add_argument("--related-interfaces", required=True)
    parser.add_argument("--related-tables", required=True)
    parser.add_argument("--interface-evidence", required=True)
    parser.add_argument("--table-evidence", required=True)
    parser.add_argument("--code-evidence", required=True)
    parser.add_argument("--environment-name", required=True)
    parser.add_argument("--api-domain", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def existing_path(value: str, field_name: str) -> Path:
    path: Path = Path(value)
    if not path.is_file():
        raise PreparationError(f"{field_name} 不存在或不是文件：{path}")
    return path


def main() -> int:
    arguments: argparse.Namespace = parse_arguments()
    confirmation_path: Path = existing_path(arguments.confirmation, "confirmation")
    test_cases_path: Path = existing_path(arguments.test_cases, "test_cases")
    cases_path: Path = existing_path(arguments.tapd_cases, "tapd_cases")
    load_cases(cases_path)
    evidence_index_path: Path = existing_path(arguments.evidence_index, "evidence_index")
    input_paths: dict[str, Path] = {
        "test_cases": test_cases_path,
        "tapd_cases": cases_path,
        "related_interfaces": existing_path(arguments.related_interfaces, "related_interfaces"),
        "related_tables": existing_path(arguments.related_tables, "related_tables"),
        "interface_evidence": existing_path(arguments.interface_evidence, "interface_evidence"),
        "table_evidence": existing_path(arguments.table_evidence, "table_evidence"),
        "code_evidence": existing_path(arguments.code_evidence, "code_evidence"),
    }
    confirmation: dict[str, object] = read_json_object(confirmation_path)
    evidence_index: dict[str, object] = read_json_object(evidence_index_path)
    if confirmation.get("approved") is not True:
        raise PreparationError("testcase_confirmation.json.approved 必须为 true。")
    expected_hash: str = require_string(confirmation.get("testcase_hash"), "testcase_hash")
    actual_hash: str = file_sha256(test_cases_path)
    if expected_hash != actual_hash:
        raise PreparationError("testcase_confirmation.json.testcase_hash 与当前 test_cases.md 不一致。")
    review_run_id: str = require_string(confirmation.get("code_review_run_id"), "code_review_run_id")
    if evidence_index.get("review_run_id") != review_run_id:
        raise PreparationError("代码复审批次与 testcase_confirmation.json.code_review_run_id 不一致。")
    snapshot: dict[str, object] = {
        "testcase_confirmation": {
            "testcase_hash": expected_hash,
            "code_review_run_id": review_run_id,
            "approved_at": confirmation.get("approved_at", ""),
        },
        "input_hashes": {name: file_sha256(path) for name, path in input_paths.items()},
        "environment": {"name": require_string(arguments.environment_name, "environment_name"), "api_domain": require_string(arguments.api_domain, "api_domain")},
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    write_json_object(Path(arguments.output), snapshot)
    print(f"确认输入校验通过：{review_run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
