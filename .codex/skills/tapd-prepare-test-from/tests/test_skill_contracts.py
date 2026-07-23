"""Contract tests for TAPD interface-test preparation resources."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_PATH: Path = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_PATH))

from build_assessment_from_model import merge_assessment
from execute_read_query_plan import QueryPlanError, validate_select
from preparation_contract import PreparationError, load_cases, validation_errors
from render_three_documents import render_flow_document, render_interface_document


def valid_case() -> dict[str, object]:
    return {
        "case_id": "TC001",
        "title": "[API] - [Create] - [Created]",
        "directory": "Module-Create",
        "requirement_id": "1063060",
        "case_type": "功能测试",
        "case_status": "正常",
        "priority": "P0",
        "system_scope": "API",
        "module": "Create",
        "precondition": "A valid user exists.",
        "steps": ["Submit a valid request."],
        "expected_results": ["The resource is created."],
        "requirement_points": ["requirement.md section 13"],
        "remarks": "无",
    }


def write_payload(directory: Path, payload: dict[str, object]) -> Path:
    path: Path = directory / "payload.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


class CaseContractTests(unittest.TestCase):
    def test_load_cases_accepts_authoritative_contract(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            path: Path = write_payload(Path(raw_directory), {"total_count": 1, "cases": [valid_case()]})
            self.assertEqual(len(load_cases(path)), 1)

    def test_load_cases_rejects_legacy_story_id_contract(self) -> None:
        legacy_case: dict[str, object] = valid_case()
        legacy_case["story_id"] = legacy_case.pop("requirement_id")
        with tempfile.TemporaryDirectory() as raw_directory:
            path: Path = write_payload(Path(raw_directory), {"total_count": 1, "cases": [legacy_case]})
            with self.assertRaisesRegex(PreparationError, "requirement_id"):
                load_cases(path)


class AssessmentTests(unittest.TestCase):
    def test_merge_assessment_copies_only_authored_sections(self) -> None:
        shell: dict[str, object] = {
            "source": {"testcase_hash": "hash"},
            "case_catalog": [],
            "interface_cases": [],
            "non_interface_cases": [],
            "core_flows": [],
            "core_flow_blocker_reason": "",
            "real_data_records": [],
        }
        mapping: dict[str, object] = {
            "interface_cases": [{"interface_key": "verified"}],
            "non_interface_cases": [],
            "core_flows": [],
            "core_flow_blocker_reason": "No verified dependency path.",
        }
        real_data: dict[str, object] = {"real_data_records": [{"query_reference": "QRY_1"}]}
        result: dict[str, object] = merge_assessment(shell, mapping, real_data)
        self.assertEqual(result["interface_cases"], mapping["interface_cases"])
        self.assertEqual(result["core_flow_blocker_reason"], "No verified dependency path.")
        self.assertNotIn("reviewed_at", json.dumps(result, ensure_ascii=False))

    def test_validation_rejects_stale_input_hashes(self) -> None:
        assessment: dict[str, object] = {
            "source": {
                "testcase_hash": "case-hash",
                "code_review_run_id": "review-1",
                "input_hashes": {"tapd_cases": "old"},
            },
            "case_catalog": [],
            "real_data_records": [],
            "interface_cases": [],
            "non_interface_cases": [],
            "core_flows": [],
            "core_flow_blocker_reason": "No verified flow.",
        }
        snapshot: dict[str, object] = {
            "testcase_confirmation": {
                "testcase_hash": "case-hash",
                "code_review_run_id": "review-1",
            },
            "input_hashes": {"tapd_cases": "current"},
        }
        errors: list[str] = validation_errors(assessment, [], snapshot)
        self.assertIn("assessment.source.input_hashes 与确认输入快照不一致。", errors)


class QuerySafetyTests(unittest.TestCase):
    def test_validate_select_accepts_read_query(self) -> None:
        validate_select("SELECT id, tenant_id FROM app.activity WHERE is_deleted = 0 LIMIT 20")

    def test_validate_select_rejects_side_effects_and_comments(self) -> None:
        rejected: tuple[str, ...] = (
            "SELECT * FROM app.activity INTO OUTFILE 'x'",
            "SELECT * FROM app.activity FOR UPDATE",
            "SELECT SLEEP(10)",
            "SELECT id FROM app.activity -- hidden",
            "SELECT id FROM app.activity; DELETE FROM app.activity",
        )
        for sql in rejected:
            with self.subTest(sql=sql), self.assertRaises(QueryPlanError):
                validate_select(sql)


class RenderingTests(unittest.TestCase):
    def test_interface_document_redacts_sensitive_headers(self) -> None:
        assessment: dict[str, object] = {
            "environment": {"name": "test", "api_domain": "https://api.example.test"},
            "interface_cases": [
                {
                    "interface_key": "create",
                    "covered_case_keys": ["case_001"],
                    "interface_evidence": {
                        "service": "service",
                        "controller_file": "Controller.java",
                        "controller_method": "create",
                        "http_method": "POST",
                        "path": "/gateway/create",
                    },
                    "request_variants": [
                        {
                            "name": "positive",
                            "variant_type": "positive",
                            "case_keys": ["case_001"],
                            "validation_evidence": [],
                            "headers": {"Authorization": "secret-token", "Content-Type": "application/json"},
                            "parameters": [],
                            "request_body": {},
                            "expected": {
                                "http_status": 200,
                                "response_assertions": [{"path": "$.code", "operator": "equals", "value": "00000"}],
                                "database_assertions": [],
                            },
                            "setup_steps": [],
                            "cleanup_steps": [],
                        }
                    ],
                    "negative_variant_policy": "no_verifiable_validation_rule",
                    "negative_variant_evidence": ["No verified rejection rule."],
                    "audit": {
                        "status": "可审核",
                        "evidence_status": "verified",
                        "reason": "Evidence is linked.",
                        "reviewer": "Codex",
                        "reviewed_at": "2026-07-22T00:00:00+08:00",
                    },
                }
            ],
        }
        snapshot: dict[str, object] = {
            "testcase_confirmation": {"testcase_hash": "hash", "code_review_run_id": "review-1"}
        }
        document: str = render_interface_document(assessment, snapshot)
        self.assertNotIn("secret-token", document)
        self.assertIn('"Authorization": "***"', document)

    def test_flow_document_omits_skeleton_when_flow_is_blocked(self) -> None:
        assessment: dict[str, object] = {
            "core_flows": [],
            "core_flow_blocker_reason": "No verified dependency path.",
        }
        snapshot: dict[str, object] = {
            "testcase_confirmation": {"testcase_hash": "hash", "code_review_run_id": "review-1"}
        }
        document: str = render_flow_document(assessment, snapshot)
        self.assertIn("No verified dependency path.", document)
        self.assertNotIn("selected_flow", document)


if __name__ == "__main__":
    unittest.main()
