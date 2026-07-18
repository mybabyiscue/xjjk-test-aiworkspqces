"""Approve a completed code source review after explicit user confirmation."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Approve a completed code source review run.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--approver", required=True)
    parser.add_argument("--approval-note", required=True)
    parser.add_argument("--ignored-finding", action="append")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    manifest_path = run_dir / "source_manifest.json"
    confirmation_path = run_dir / "code_source_confirmation.json"
    manifest = read_json_object(manifest_path, "source manifest")
    confirmation = read_json_object(confirmation_path, "code source confirmation")
    validate_review_outputs(run_dir, manifest)

    confirmation.update({
        "approved": True,
        "reason": args.approval_note,
        "approved_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "approver": args.approver,
        "manual_ignored_findings": args.ignored_finding or [],
    })
    write_json(confirmation_path, confirmation)
    sync_latest_confirmation(run_dir, manifest, confirmation)
    print(str(confirmation_path))
    return 0


def read_json_object(path: Path, label: str) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"Missing {label}: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Invalid {label}: root must be an object: {path}")
    return value


def validate_review_outputs(run_dir: Path, manifest: dict[str, object]) -> None:
    sources = manifest.get("code_sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("source_manifest.json.code_sources must contain at least one source")
    failed = [
        str(source.get("service_id", ""))
        for source in sources
        if isinstance(source, dict) and source.get("fetch_status") != "success"
    ]
    if failed:
        raise ValueError(f"Cannot approve sources that were not fetched successfully: {', '.join(failed)}")
    required = ["code_review_report.md", "code_prepare_findings.md"]
    if manifest.get("testcase_analysis_status") == "completed":
        required.extend([
            "core_process_interfaces.md",
            "unit_test_interfaces.md",
            "test_case_tables.md",
            "test_case_data.md",
        ])
    missing = [name for name in required if not (run_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"Cannot approve incomplete review outputs: {', '.join(missing)}")


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")


def sync_latest_confirmation(run_dir: Path, manifest: dict[str, object], confirmation: dict[str, object]) -> None:
    if run_dir.name == "latest" or run_dir.parent.name != "runs":
        return
    latest_dir = run_dir.parent.parent / "latest"
    latest_manifest_path = latest_dir / "source_manifest.json"
    if not latest_manifest_path.exists():
        return
    latest_manifest = read_json_object(latest_manifest_path, "latest source manifest")
    if latest_manifest.get("source_run_id") != manifest.get("source_run_id"):
        raise ValueError("Latest source run differs from the approved run; approval was not copied to latest")
    write_json(latest_dir / "code_source_confirmation.json", confirmation)


if __name__ == "__main__":
    raise SystemExit(main())
