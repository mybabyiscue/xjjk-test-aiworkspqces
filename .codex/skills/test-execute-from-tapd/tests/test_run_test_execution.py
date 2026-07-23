"""Smoke tests for the generic TAPD execution runner."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType


class TestHandler(BaseHTTPRequestHandler):
    """Serve deterministic HTTP responses for the integration smoke test."""

    def do_GET(self) -> None:
        if self.path == "/forbidden":
            self.send_response(403)
            payload: bytes = b'{"code":"TOKEN_EXPIRED"}'
        else:
            self.send_response(200)
            payload = b'{"code":0,"data":{"id":17}}'
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args: object) -> None:
        return


def write_json(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def request_plan(path: str) -> dict[str, object]:
    return {
        "version": 1,
        "testcase_hash": "approved-hash",
        "token_error_codes": ["TOKEN_EXPIRED"],
        "requests": [
            {
                "id": "case_001",
                "case_ids": ["case_001"],
                "variant_type": "positive",
                "method": "GET",
                "path": path,
                "headers": {"Accept": "application/json"},
                "authorization_header": "",
                "query": {},
                "body": None,
                "expected": {
                    "http_status": 200,
                    "response_assertions": [{"path": "$.code", "operator": "equals", "value": 0}],
                    "database_assertions": [],
                },
            }
        ],
        "flows": [],
    }


def run_runner(workspace: Path, environment_name: str) -> subprocess.CompletedProcess[str]:
    script_path: Path = Path(__file__).resolve().parents[1] / "scripts" / "run_test_execution.py"
    return subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--workspace",
            str(workspace),
            "--plan",
            "execution_plan.json",
            "--confirmation",
            "confirmation.json",
            "--environment-config",
            "environments_config.json",
            "--environment-name",
            environment_name,
            "--output-dir",
            "output",
            "--manifest",
            "output/test_data_manifest.md",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def load_runner_module() -> ModuleType:
    script_path: Path = Path(__file__).resolve().parents[1] / "scripts" / "run_test_execution.py"
    spec = spec_from_file_location("run_test_execution", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load runner module: {script_path}")
    module: ModuleType = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RunnerSmokeTest(unittest.TestCase):
    """Exercise the runner against a real local HTTP server."""

    def setUp(self) -> None:
        self.server: ThreadingHTTPServer = ThreadingHTTPServer(("127.0.0.1", 0), TestHandler)
        self.thread: threading.Thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def prepare_workspace(self, root: Path, path: str) -> None:
        domain: str = f"http://127.0.0.1:{self.server.server_port}"
        write_json(root / "execution_plan.json", request_plan(path))
        write_json(root / "confirmation.json", {"approved": True, "testcase_hash": "approved-hash"})
        write_json(root / "environments_config.json", {"environments": [{"name": "local", "api_domain": domain}]})

    def test_generates_reports_for_successful_request(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root: Path = Path(temporary_directory)
            self.prepare_workspace(root, "/ok")
            result: subprocess.CompletedProcess[str] = run_runner(root, "local")
            self.assertEqual(result.returncode, 0, result.stderr)
            report: str = (root / "output" / "interface_test_execution_report.md").read_text(encoding="utf-8")
            self.assertIn("| case_001 | case_001 | positive | PASS | 200 |", report)
            self.assertTrue((root / "output" / "core_flow_test_execution_report.md").exists())

    def test_returns_token_exit_code_for_403(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root: Path = Path(temporary_directory)
            self.prepare_workspace(root, "/forbidden")
            result: subprocess.CompletedProcess[str] = run_runner(root, "local")
            self.assertEqual(result.returncode, 10, result.stderr)
            self.assertIn("[TOKEN_EXPIRED_ERROR] local", result.stderr)

    def test_rejects_database_write_sql(self) -> None:
        runner: ModuleType = load_runner_module()
        with self.assertRaisesRegex(ValueError, "只能包含 SELECT"):
            runner.validate_read_only_sql("UPDATE account SET status = 1", "sql")

    def test_rejects_select_with_embedded_delete(self) -> None:
        runner: ModuleType = load_runner_module()
        with self.assertRaisesRegex(ValueError, "包含禁止"):
            runner.validate_read_only_sql("SELECT 1 FROM account WHERE id IN (DELETE FROM account)", "sql")


if __name__ == "__main__":
    unittest.main()
