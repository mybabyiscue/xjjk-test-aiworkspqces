"""Initialize a business-neutral assessment shell from confirmed inputs."""

from __future__ import annotations

import argparse
from pathlib import Path

from preparation_contract import case_catalog, load_cases, read_json_object, require_object, write_json_object


def parse_arguments() -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="初始化接口测试准备评估包。")
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--tapd-cases", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    arguments: argparse.Namespace = parse_arguments()
    snapshot: dict[str, object] = read_json_object(Path(arguments.snapshot))
    confirmation: dict[str, object] = require_object(snapshot.get("testcase_confirmation"), "snapshot.testcase_confirmation")
    cases: list[dict[str, object]] = load_cases(Path(arguments.tapd_cases))
    assessment: dict[str, object] = {
        "source": {
            "testcase_hash": confirmation.get("testcase_hash"),
            "code_review_run_id": confirmation.get("code_review_run_id"),
            "input_hashes": snapshot.get("input_hashes", {}),
        },
        "environment": snapshot.get("environment", {}),
        "case_catalog": case_catalog(cases),
        "interface_cases": [],
        "non_interface_cases": [],
        "core_flows": [],
        "core_flow_blocker_reason": "",
        "real_data_records": [],
    }
    write_json_object(Path(arguments.output), assessment)
    print(f"已初始化 {len(cases)} 条用例的准备评估包。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
