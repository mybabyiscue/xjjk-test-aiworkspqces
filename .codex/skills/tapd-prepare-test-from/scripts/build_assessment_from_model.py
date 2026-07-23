"""Merge model-authored mappings and real query records into an assessment."""

from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path

from preparation_contract import read_json_object, require_list, require_string, write_json_object


def parse_arguments() -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Merge evidence-backed mappings and real query records into an assessment."
    )
    parser.add_argument("--assessment-shell", required=True)
    parser.add_argument("--model-mapping", required=True)
    parser.add_argument("--real-data", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def merge_assessment(
    assessment_shell: dict[str, object],
    model_mapping: dict[str, object],
    real_data: dict[str, object],
) -> dict[str, object]:
    assessment: dict[str, object] = deepcopy(assessment_shell)
    assessment["interface_cases"] = deepcopy(
        require_list(model_mapping.get("interface_cases"), "model_mapping.interface_cases")
    )
    assessment["non_interface_cases"] = deepcopy(
        require_list(model_mapping.get("non_interface_cases"), "model_mapping.non_interface_cases")
    )
    assessment["core_flows"] = deepcopy(
        require_list(model_mapping.get("core_flows"), "model_mapping.core_flows")
    )
    blocker_reason: object = model_mapping.get("core_flow_blocker_reason")
    if blocker_reason == "":
        assessment["core_flow_blocker_reason"] = ""
    else:
        assessment["core_flow_blocker_reason"] = require_string(
            blocker_reason,
            "model_mapping.core_flow_blocker_reason",
        )
    assessment["real_data_records"] = deepcopy(
        require_list(real_data.get("real_data_records"), "real_data.real_data_records")
    )
    return assessment


def main() -> int:
    arguments: argparse.Namespace = parse_arguments()
    assessment_shell: dict[str, object] = read_json_object(Path(arguments.assessment_shell))
    model_mapping: dict[str, object] = read_json_object(Path(arguments.model_mapping))
    real_data: dict[str, object] = read_json_object(Path(arguments.real_data))
    assessment: dict[str, object] = merge_assessment(assessment_shell, model_mapping, real_data)
    write_json_object(Path(arguments.output), assessment)
    print("Assessment built from evidence-backed model mappings and real query records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
