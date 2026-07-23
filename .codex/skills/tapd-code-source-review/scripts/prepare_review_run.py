"""Create an isolated review run after all human gates are satisfied."""

from __future__ import annotations

import argparse
import copy
import shutil
from datetime import datetime
from pathlib import Path

from workflow_contract import (
    metadata_connection_names,
    parse_mappings,
    require_exact_service_mappings,
    sha256_file,
    successful_sources,
    validate_approved_source_run,
    write_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare an isolated TAPD code review run.")
    parser.add_argument("--source-run-dir", required=True)
    parser.add_argument("--test-cases", required=True)
    parser.add_argument("--requirement", required=True)
    parser.add_argument("--questions", required=True)
    parser.add_argument("--metadata-document", required=True)
    parser.add_argument("--platform", action="append", required=True)
    parser.add_argument("--gateway-prefix", action="append", required=True)
    parser.add_argument("--gateway-evidence", action="append", required=True)
    parser.add_argument("--gateway-prefix-rule", action="append")
    parser.add_argument("--gateway-evidence-rule", action="append")
    parser.add_argument("--questions-decision", choices=("resolved", "ignored"), required=True)
    parser.add_argument("--questions-note", required=True)
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()

    source_run_dir = Path(args.source_run_dir).resolve()
    test_cases_path = require_file(Path(args.test_cases), "test cases")
    requirement_path = require_file(Path(args.requirement), "requirement")
    questions_path = require_file(Path(args.questions), "questions")
    metadata_path = require_file(Path(args.metadata_document), "metadata document")
    manifest, confirmation = validate_approved_source_run(source_run_dir)
    sources = successful_sources(manifest)
    service_ids = {str(source["service_id"]) for source in sources}

    platforms = parse_mappings(args.platform, "platform")
    gateway_prefixes = parse_mappings(args.gateway_prefix, "gateway prefix")
    gateway_evidence = parse_mappings(args.gateway_evidence, "gateway evidence")
    gateway_prefix_rules = parse_mappings(args.gateway_prefix_rule or [], "gateway prefix rule")
    gateway_evidence_rules = parse_mappings(args.gateway_evidence_rule or [], "gateway evidence rule")
    require_exact_service_mappings(service_ids, platforms, "platform")
    require_exact_service_mappings(service_ids, gateway_prefixes, "gateway prefix")
    require_exact_service_mappings(service_ids, gateway_evidence, "gateway evidence")
    available_connections = metadata_connection_names(metadata_path)
    unknown_platforms = sorted(set(platforms.values()) - available_connections)
    if unknown_platforms:
        raise ValueError(f"Unknown metadata platforms: {unknown_platforms}")
    validate_gateway_mappings(gateway_prefixes, gateway_evidence)
    gateway_rules = validate_gateway_rules(
        service_ids,
        gateway_prefix_rules,
        gateway_evidence_rules,
    )
    if not args.questions_note.strip():
        raise ValueError("Questions decision requires a non-empty note")

    output_root = Path(args.output_root)
    runs_dir = output_root / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    run_id = unique_run_id(runs_dir, datetime.now().strftime("%Y%m%d_%H%M%S_code_review"))
    run_dir = runs_dir / run_id
    run_dir.mkdir(parents=False, exist_ok=False)

    enriched_manifest = copy.deepcopy(manifest)
    enriched_manifest["review_run_id"] = run_id
    for source in enriched_manifest["code_sources"]:
        service_id = str(source["service_id"])
        source["platform"] = platforms[service_id]
        source["metadata_connection"] = platforms[service_id]
        source["platform_name"] = platforms[service_id]
        source["platform_status"] = "confirmed"
        source["gateway_prefix"] = normalize_gateway_prefix(gateway_prefixes[service_id])
        source["gateway_evidence"] = gateway_evidence[service_id]
        source["gateway_prefix_rules"] = gateway_rules.get(service_id, [])

    manifest_path = run_dir / "source_manifest.json"
    confirmation_path = run_dir / "code_source_confirmation.json"
    write_json(manifest_path, enriched_manifest)
    write_json(confirmation_path, confirmation)
    copy_source_review_artifacts(source_run_dir, run_dir)
    context: dict[str, object] = {
        "review_run_id": run_id,
        "source_run_id": manifest.get("source_run_id"),
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "questions": {
            "decision": args.questions_decision,
            "note": args.questions_note.strip(),
            "sha256": sha256_file(questions_path),
        },
        "inputs": {
            "test_cases_path": str(test_cases_path),
            "test_cases_sha256": sha256_file(test_cases_path),
            "requirement_path": str(requirement_path),
            "requirement_sha256": sha256_file(requirement_path),
            "questions_path": str(questions_path),
            "questions_sha256": sha256_file(questions_path),
            "metadata_path": str(metadata_path),
            "metadata_sha256": sha256_file(metadata_path),
            "manifest_sha256": sha256_file(manifest_path),
            "source_confirmation_sha256": sha256_file(confirmation_path),
        },
    }
    write_json(run_dir / "review_context.json", context)
    print(str(run_dir))
    return 0


def require_file(path: Path, label: str) -> Path:
    resolved = path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"Missing {label}: {resolved}")
    return resolved


def validate_gateway_mappings(prefixes: dict[str, str], evidence: dict[str, str]) -> None:
    for service_id, prefix in prefixes.items():
        if not prefix.startswith("/"):
            raise ValueError(f"Gateway prefix must start with '/': {service_id}={prefix}")
        normalized_prefix = normalize_gateway_prefix(prefix)
        validate_gateway_evidence(normalized_prefix, evidence[service_id], service_id)


def validate_gateway_rules(
    service_ids: set[str],
    prefixes: dict[str, str],
    evidence: dict[str, str],
) -> dict[str, list[dict[str, str]]]:
    if set(prefixes) != set(evidence):
        missing = sorted(set(prefixes) - set(evidence))
        extra = sorted(set(evidence) - set(prefixes))
        raise ValueError(f"Invalid gateway rule evidence mappings; missing={missing}, extra={extra}")
    rules: dict[str, list[dict[str, str]]] = {}
    for rule_key, prefix in prefixes.items():
        service_id, separator, path_fragment = rule_key.partition(":")
        normalized_service_id = service_id.strip()
        normalized_fragment = path_fragment.replace("\\", "/").strip("/")
        if not separator or not normalized_service_id or not normalized_fragment:
            raise ValueError(
                f"Invalid gateway rule key {rule_key}; expected service_id:path_fragment"
            )
        if normalized_service_id not in service_ids:
            raise ValueError(f"Unknown service in gateway rule: {normalized_service_id}")
        if not prefix.startswith("/"):
            raise ValueError(f"Gateway rule prefix must start with '/': {rule_key}={prefix}")
        normalized_prefix = normalize_gateway_prefix(prefix)
        evidence_value = evidence[rule_key]
        validate_gateway_evidence(normalized_prefix, evidence_value, rule_key)
        rules.setdefault(normalized_service_id, []).append(
            {
                "path_fragment": normalized_fragment,
                "prefix": normalized_prefix,
                "evidence": evidence_value,
            }
        )
    for service_rules in rules.values():
        service_rules.sort(key=lambda item: len(item["path_fragment"]), reverse=True)
    return rules


def validate_gateway_evidence(prefix: str, evidence_value: str, label: str) -> None:
    path_text, separator, line_text = evidence_value.rpartition(":")
    if not separator or not line_text.isdigit() or int(line_text) < 1:
        raise ValueError(f"Gateway evidence must use path:line: {label}={evidence_value}")
    evidence_path = Path(path_text)
    if not evidence_path.is_file():
        raise FileNotFoundError(f"Gateway evidence file does not exist: {path_text}")
    lines = evidence_path.read_text(encoding="utf-8").splitlines()
    line_number = int(line_text)
    if line_number > len(lines):
        raise ValueError(f"Gateway evidence line is outside the file: {evidence_value}")
    if prefix and prefix not in lines[line_number - 1]:
        raise ValueError(f"Gateway evidence line does not contain {prefix}: {evidence_value}")


def normalize_gateway_prefix(prefix: str) -> str:
    normalized = "/" + prefix.strip("/")
    return "" if normalized == "/" else normalized


def copy_source_review_artifacts(source_run_dir: Path, review_run_dir: Path) -> None:
    source_files = {
        source_run_dir / "code_prepare_findings.md": review_run_dir / "code_prepare_findings.md",
        source_run_dir / "code_review_report.md": review_run_dir / "code_review_report.md",
        source_run_dir / "raw" / "prepare_findings.json": review_run_dir / "raw" / "prepare_findings.json",
    }
    for source, target in source_files.items():
        if not source.is_file():
            raise FileNotFoundError(f"Missing source review artifact: {source}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def unique_run_id(runs_dir: Path, base_run_id: str) -> str:
    candidate = base_run_id
    counter = 1
    while (runs_dir / candidate).exists():
        candidate = f"{base_run_id}_{counter:02d}"
        counter += 1
    return candidate


if __name__ == "__main__":
    raise SystemExit(main())
