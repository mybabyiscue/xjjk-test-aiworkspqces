"""Contract tests for TAPD interface-test preparation resources."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_PATH: Path = Path(__file__).resolve().parents[1] / "scripts"
SKILL_PATH: Path = SCRIPTS_PATH.parent
sys.path.insert(0, str(SCRIPTS_PATH))

from build_assessment_from_model import merge_assessment
from build_api_execution_plan import build_execution_plan
from execute_read_query_plan import QueryPlanError, validate_select
from preparation_contract import PreparationError, data_preparation_errors, file_sha256, load_cases, validation_errors
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


class ConfirmedInputContractTests(unittest.TestCase):
    def test_current_code_review_artifacts_are_the_complete_input_contract(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory: Path = Path(raw_directory)
            test_cases: Path = directory / "test_cases.md"
            tapd_cases: Path = directory / "tapd_cases.json"
            confirmation: Path = directory / "testcase_confirmation.json"
            evidence_index: Path = directory / "evidence_index.json"
            unit_interfaces: Path = directory / "unit_test_interfaces.md"
            core_interfaces: Path = directory / "core_process_interfaces.md"
            table_information: Path = directory / "table_information.md"
            source_manifest: Path = directory / "source_manifest.json"
            snapshot: Path = directory / "confirmed_input_snapshot.json"

            test_cases.write_text("# Test cases\n", encoding="utf-8")
            tapd_cases.write_text(
                json.dumps({"total_count": 1, "cases": [valid_case()]}, ensure_ascii=False),
                encoding="utf-8",
            )
            confirmation.write_text(
                json.dumps({
                    "approved": True,
                    "testcase_hash": file_sha256(test_cases),
                    "code_review_run_id": "review-1",
                    "approved_at": "2026-07-23T00:00:00+08:00",
                }),
                encoding="utf-8",
            )
            for path in (unit_interfaces, core_interfaces, table_information):
                path.write_text(f"# {path.stem}\n", encoding="utf-8")
            source_manifest.write_text("{}\n", encoding="utf-8")
            evidence_index.write_text(
                json.dumps({
                    "review_run_id": "review-1",
                    "artifacts": {
                        "unit_test_interfaces.md": file_sha256(unit_interfaces),
                        "core_process_interfaces.md": file_sha256(core_interfaces),
                        "table_information.md": file_sha256(table_information),
                        "source_manifest.json": file_sha256(source_manifest),
                    },
                }),
                encoding="utf-8",
            )

            completed: subprocess.CompletedProcess[bytes] = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_PATH / "validate_confirmed_input.py"),
                    "--confirmation", str(confirmation),
                    "--test-cases", str(test_cases),
                    "--tapd-cases", str(tapd_cases),
                    "--evidence-index", str(evidence_index),
                    "--unit-interface-evidence", str(unit_interfaces),
                    "--core-interface-evidence", str(core_interfaces),
                    "--table-evidence", str(table_information),
                    "--code-evidence", str(source_manifest),
                    "--environment-name", "Test",
                    "--api-domain", "https://api.example.test",
                    "--output", str(snapshot),
                ],
                check=True,
                capture_output=True,
            )

            self.assertEqual(completed.returncode, 0)
            payload: dict[str, object] = json.loads(snapshot.read_text(encoding="utf-8"))
            self.assertEqual(
                set(payload["input_hashes"]),
                {
                    "test_cases",
                    "tapd_cases",
                    "evidence_index",
                    "unit_interface_evidence",
                    "core_interface_evidence",
                    "table_evidence",
                    "code_evidence",
                },
            )


class WorkspaceConfigurationContractTests(unittest.TestCase):
    def test_database_commands_use_workspace_configuration_only(self) -> None:
        skill_text: str = (SKILL_PATH / "SKILL.md").read_text(encoding="utf-8")
        workflow_text: str = (SKILL_PATH / "references" / "execution-workflow.md").read_text(encoding="utf-8")
        configuration_text: str = (SKILL_PATH / "references" / "configuration.md").read_text(encoding="utf-8")
        combined: str = "\n".join((skill_text, workflow_text, configuration_text))

        self.assertIn("config/connections.json", combined)
        self.assertNotIn(".codex/skills/xjjk-yewu-sql/state/connections.json", combined)
        self.assertNotIn("C:\\Users\\Administrator\\.codex\\skills", combined)

    def test_token_gate_requires_an_authenticated_endpoint_and_application_code(self) -> None:
        configuration_text: str = (SKILL_PATH / "references" / "configuration.md").read_text(encoding="utf-8")

        self.assertIn("不能只填写不校验鉴权的 `api_domain` 根地址", configuration_text)
        self.assertIn("healthcheck_headers", configuration_text)
        self.assertIn("healthcheck_success_code", configuration_text)
        self.assertIn("healthcheck_unauthorized_codes", configuration_text)


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
            "data_preparation": {"entries": []},
            "interface_cases": [{"interface_key": "verified"}],
            "non_interface_cases": [],
            "core_flows": [],
            "core_flow_blocker_reason": "No verified dependency path.",
        }
        real_data: dict[str, object] = {"real_data_records": [{"query_reference": "QRY_1"}]}
        result: dict[str, object] = merge_assessment(shell, mapping, real_data)
        self.assertEqual(result["data_preparation"], mapping["data_preparation"])
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


class ExecutionPlanTests(unittest.TestCase):
    def test_builds_canonical_requests_and_flows(self) -> None:
        expected: dict[str, object] = {
            "http_status": 200,
            "response_assertions": [{"path": "$.code", "operator": "equals", "value": 0}],
            "database_assertions": [],
        }
        evidence: dict[str, object] = {
            "service": "service",
            "controller_file": "Controller.java",
            "controller_method": "query",
            "http_method": "GET",
            "path": "/gateway/resource",
        }
        request_data: dict[str, object] = {
            "name": "positive",
            "variant_type": "positive",
            "case_keys": ["case_001"],
            "validation_evidence": [],
            "headers": {"Accept": "application/json"},
            "authorization_header": "Authorization",
            "query": {"id": 17},
            "parameters": [],
            "request_body": None,
            "expected": expected,
            "setup_steps": [],
            "cleanup_steps": [],
        }
        flow_step: dict[str, object] = {
            **request_data,
            "step_key": "query_resource",
            "interface_evidence": evidence,
            "parameter_dependencies": [],
            "interrupt_condition": "任一断言失败时中止。",
        }
        assessment: dict[str, object] = {
            "source": {"testcase_hash": "approved-hash", "code_review_run_id": "review-1"},
            "data_preparation": {"entries": []},
            "interface_cases": [
                {
                    "interface_key": "query_resource",
                    "interface_evidence": evidence,
                    "request_variants": [request_data],
                    "audit": {"status": "已通过"},
                }
            ],
            "core_flows": [
                {
                    "flow_key": "resource_flow",
                    "name": "资源流程",
                    "steps": [flow_step, {**flow_step, "step_key": "query_resource_again"}],
                }
            ],
        }

        plan, report = build_execution_plan(assessment, "assessment-sha256")

        self.assertTrue(report["ready"])
        self.assertEqual(plan["version"], 2)
        self.assertTrue(plan["ready"])
        self.assertEqual(plan["data_setup"], [])
        self.assertEqual(plan["data_cleanup"], [])
        self.assertEqual(
            plan["source"],
            {
                "preparation_assessment_sha256": "assessment-sha256",
                "testcase_hash": "approved-hash",
                "code_review_run_id": "review-1",
            },
        )
        self.assertEqual(plan["requests"][0]["query"], {"id": 17})
        self.assertEqual(plan["flows"][0]["steps"][0]["id"], "query_resource")

    def test_rejects_mock_data_strategy(self) -> None:
        errors: list[str] = data_preparation_errors(
            {
                "entries": [
                    {
                        "id": "target",
                        "case_keys": ["case_001"],
                        "strategy": "mock_seed",
                        "evidence_references": ["table_information.md#target"],
                        "verification_query_reference": "QRY_TARGET",
                        "setup": None,
                        "cleanup": None,
                    }
                ]
            },
            {"case_001"},
            {"QRY_TARGET"},
        )

        self.assertTrue(any("禁止 Mock" in error for error in errors))

    def test_accepts_reused_real_record_without_mutation(self) -> None:
        errors: list[str] = data_preparation_errors(
            {
                "entries": [
                    {
                        "id": "target",
                        "case_keys": ["case_001"],
                        "strategy": "reuse",
                        "evidence_references": ["table_information.md#target"],
                        "verification_query_reference": "QRY_TARGET",
                        "setup": None,
                        "cleanup": None,
                    }
                ]
            },
            {"case_001"},
            {"QRY_TARGET"},
        )

        self.assertEqual(errors, [])


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
            "data_preparation": {"entries": []},
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
