"""Build testcase-driven interface, call-chain, table, and test-data evidence."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Pattern

from review_policy import read_policy, require_pattern, require_positive_int, require_ratio, require_section, require_string, require_string_list, require_string_map

def main() -> int:
    parser = argparse.ArgumentParser(description="Generate testcase-driven code evidence reports.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--test-cases", required=True)
    parser.add_argument("--metadata-document", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--platform", action="append", help="Runtime platform mapping as service=platform.")
    parser.add_argument("--metadata-connection", action="append", help="Runtime metadata mapping as service=connection.")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    policy = read_policy(Path(args.policy))
    source_policy = require_section(policy, "source_scan")
    testcase_policy = require_section(policy, "testcase_parsing")
    interface_policy = require_section(policy, "interface_detection")
    matching_policy = require_section(policy, "case_matching")
    table_policy = require_section(policy, "table_analysis")
    unit_test_policy = require_section(policy, "unit_test_detection")
    extensions = set(require_string_list(source_policy, "extensions"))
    primary_source_extensions = set(require_string_list(source_policy, "primary_source_extensions"))
    excluded_directories = set(require_string_list(source_policy, "excluded_directories"))
    max_file_bytes = require_positive_int(source_policy, "max_file_bytes")
    case_heading_pattern = require_pattern(testcase_policy, "case_heading_pattern")
    route_literal_pattern = require_pattern(testcase_policy, "route_literal_pattern")
    frontend_route_pattern = require_pattern(interface_policy, "frontend_route_pattern")
    method_declaration_pattern = require_pattern(interface_policy, "method_declaration_pattern")
    table_annotation_pattern = require_pattern(interface_policy, "table_annotation_pattern")
    mapping_names = require_string_list(interface_policy, "http_mapping_annotations")
    http_mapping_pattern = re.compile(r"@(" + "|".join(re.escape(name) for name in mapping_names) + r")\s*\(([^)]*)\)")
    generic_tokens = set(require_string_list(matching_policy, "generic_tokens"))
    maximum_chinese_ngram_length = require_positive_int(matching_policy, "maximum_chinese_ngram_length")
    minimum_chinese_ngram_length = require_positive_int(matching_policy, "minimum_chinese_ngram_length")
    identifier_minimum_length = require_positive_int(matching_policy, "identifier_minimum_length")
    if minimum_chinese_ngram_length > maximum_chinese_ngram_length:
        raise ValueError("minimum_chinese_ngram_length cannot exceed maximum_chinese_ngram_length")
    sql_template_grades = set(require_string_list(table_policy, "sql_template_grades"))
    manifest = read_json_object(Path(args.manifest), "source manifest")
    cases = parse_test_cases(Path(args.test_cases), case_heading_pattern, route_literal_pattern, generic_tokens, minimum_chinese_ngram_length, maximum_chinese_ngram_length, identifier_minimum_length)
    metadata = load_metadata(Path(args.metadata_document))
    services = validate_services(manifest)
    services = apply_runtime_mappings(services, parse_mapping_args(args.platform), parse_mapping_args(args.metadata_connection))
    raw_dir = run_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    java_files, other_files = collect_source_files(services, extensions, primary_source_extensions, excluded_directories, max_file_bytes)
    dto_index = build_java_file_index(java_files)
    frontend_calls = scan_frontend_calls(other_files, frontend_route_pattern, set(require_string_list(interface_policy, "excluded_route_segments")), generic_tokens, identifier_minimum_length)
    entries = scan_java_entries(java_files, dto_index, http_mapping_pattern, method_declaration_pattern, interface_policy, generic_tokens, minimum_chinese_ngram_length, maximum_chinese_ngram_length, identifier_minimum_length)
    selected_entries = select_business_entries(entries, cases)
    mapped_entries = map_cases_to_entries(selected_entries, cases, matching_policy)
    call_chains = build_call_chains(mapped_entries, java_files, method_declaration_pattern, interface_policy)
    require_platforms(mapped_entries, services)
    tables = resolve_tables(mapped_entries, call_chains, java_files, metadata, services, table_annotation_pattern, require_pattern(interface_policy, "entity_reference_pattern"), interface_policy, table_policy)
    findings = find_unclosed_cases(cases, mapped_entries)

    write_json(raw_dir / "parsed_test_cases.json", {"cases": cases})
    write_json(raw_dir / "code_entry_index.json", {"entries": entries, "frontend_calls": frontend_calls})
    write_json(raw_dir / "testcase_interface_evidence.json", {"interfaces": mapped_entries})
    write_json(raw_dir / "call_chain_evidence.json", {"call_chains": call_chains})
    write_json(raw_dir / "table_evidence.json", {"tables": tables})
    write_json(raw_dir / "table_resolution.json", {"tables": tables})
    write_json(raw_dir / "test_data_plan.json", {"tables": [table for table in tables if table["grade"] in sql_template_grades]})

    write_core_interfaces(run_dir / "core_process_interfaces.md", mapped_entries, findings)
    write_unit_interfaces(run_dir / "unit_test_interfaces.md", mapped_entries, call_chains, java_files, findings, require_string_list(unit_test_policy, "test_path_segments"))
    write_table_report(run_dir / "test_case_tables.md", tables, findings, require_positive_int(table_policy, "max_report_fields"))
    write_test_data(run_dir / "test_case_data.md", mapped_entries, tables, sql_template_grades)
    write_summary(run_dir / "testcase_evidence_summary.md", cases, mapped_entries, tables, findings)
    update_code_review_report(run_dir / "code_review_report.md", cases, mapped_entries, tables, findings)
    manifest["testcase_analysis_status"] = "completed"
    manifest["testcase_evidence_summary"] = {
        "case_count": len(cases),
        "interface_count": len(mapped_entries),
        "table_count": len(tables),
        "unclosed_case_count": len(findings),
    }
    write_json(Path(args.manifest), manifest)
    update_confirmation(run_dir / "code_source_confirmation.json", manifest, mapped_entries, tables, findings)
    sync_latest(run_dir)
    print(json.dumps({
        "case_count": len(cases),
        "interface_count": len(mapped_entries),
        "table_count": len(tables),
        "unclosed_case_count": len(findings),
    }, ensure_ascii=False))
    return 0


def read_json_object(path: Path, label: str) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"Missing {label}: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Invalid {label}: root must be an object: {path}")
    return value


def validate_services(manifest: dict[str, object]) -> list[dict[str, object]]:
    raw_services = manifest.get("code_sources")
    if not isinstance(raw_services, list):
        raise TypeError("source_manifest.json.code_sources must be a list")
    services: list[dict[str, object]] = []
    for raw_service in raw_services:
        if not isinstance(raw_service, dict):
            raise TypeError("Each code source must be an object")
        if raw_service.get("fetch_status") != "success":
            continue
        cache_path = raw_service.get("cache_path")
        service_id = raw_service.get("service_id")
        if not isinstance(cache_path, str) or not Path(cache_path).exists():
            raise FileNotFoundError(f"Unreadable cache path for {service_id}: {cache_path}")
        services.append(raw_service)
    if not services:
        raise ValueError("No successful code sources are available")
    return services


def parse_mapping_args(values: list[str] | None) -> dict[str, str]:
    mappings: dict[str, str] = {}
    for value in values or []:
        service, separator, mapped_value = value.partition("=")
        if not separator or not service.strip() or not mapped_value.strip():
            raise ValueError(f"Invalid mapping {value}; expected service=value")
        mappings[service.strip()] = mapped_value.strip()
    return mappings


def apply_runtime_mappings(services: list[dict[str, object]], platforms: dict[str, str], connections: dict[str, str]) -> list[dict[str, object]]:
    updated_services: list[dict[str, object]] = []
    for service in services:
        updated = dict(service)
        service_id = str(service.get("service_id", ""))
        if service_id in platforms:
            updated["platform_id"] = platforms[service_id]
            updated["platform_name"] = platforms[service_id]
            updated["platform_status"] = "confirmed"
        if service_id in connections:
            updated["metadata_connection"] = connections[service_id]
        updated_services.append(updated)
    return updated_services


def require_platforms(entries: list[dict[str, object]], services: list[dict[str, object]]) -> None:
    referenced_services = {str(entry.get("service_id", "")) for entry in entries}
    missing = [
        str(service.get("service_id", ""))
        for service in services
        if str(service.get("service_id", "")) in referenced_services
        and service.get("platform_status") != "confirmed"
        and not service.get("platform_name")
    ]
    if missing:
        raise ValueError(f"Platform confirmation required before table resolution: {', '.join(missing)}")


def parse_test_cases(path: Path, case_heading_pattern: Pattern[str], route_literal_pattern: Pattern[str], generic_tokens: set[str], minimum_chinese_ngram_length: int, maximum_chinese_ngram_length: int, identifier_minimum_length: int) -> list[dict[str, object]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing test cases: {path}")
    text = path.read_text(encoding="utf-8")
    matches = list(case_heading_pattern.finditer(text))
    cases: list[dict[str, object]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end():end].strip()
        case_id = match.group(1).replace("_", "-")
        title = match.group(2).strip(" -")
        cases.append({
            "case_id": case_id,
            "title": title,
            "body": body,
            "tokens": sorted(extract_tokens(f"{title}\n{body}", generic_tokens, minimum_chinese_ngram_length, maximum_chinese_ngram_length, identifier_minimum_length)),
            "routes": sorted(set(route_literal_pattern.findall(f"{title}\n{body}"))),
        })
    if not cases:
        raise ValueError(f"No TC headings found in {path}")
    return cases


def collect_source_files(services: list[dict[str, object]], extensions: set[str], primary_source_extensions: set[str], excluded_directories: set[str], max_file_bytes: int) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    java_files: list[dict[str, str]] = []
    other_files: list[dict[str, str]] = []
    for service in services:
        service_id = str(service.get("service_id", ""))
        root = Path(str(service["cache_path"]))
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in extensions:
                continue
            if any(part in excluded_directories for part in path.parts):
                continue
            if path.stat().st_size > max_file_bytes:
                continue
            item = {"service_id": service_id, "path": str(path), "text": path.read_text(encoding="utf-8", errors="ignore")}
            (java_files if path.suffix.lower() in primary_source_extensions else other_files).append(item)
    return java_files, other_files


def build_java_file_index(java_files: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {}
    for item in java_files:
        index[Path(item["path"]).stem] = item
    return index


def scan_frontend_calls(files: list[dict[str, str]], frontend_route_pattern: Pattern[str], excluded_route_segments: set[str], generic_tokens: set[str], identifier_minimum_length: int) -> list[dict[str, object]]:
    calls: list[dict[str, object]] = []
    for item in files:
        for match in frontend_route_pattern.finditer(item["text"]):
            route = match.group("route")
            if not is_api_route(route, excluded_route_segments):
                continue
            symbol = match.group("symbol") or ""
            calls.append({
                "service_id": item["service_id"],
                "symbol": symbol,
                "route": route,
                "tokens": sorted(extract_identifier_tokens(f"{symbol} {route}", generic_tokens, identifier_minimum_length)),
                "file": item["path"],
                "line": line_number(item["text"], match.start()),
            })
    return dedupe(calls, ("service_id", "route", "file"))


def is_api_route(route: str, excluded_route_segments: set[str]) -> bool:
    lowered = route.lower()
    return route.startswith("/") and not any(segment.lower() in lowered for segment in excluded_route_segments)


def scan_java_entries(java_files: list[dict[str, str]], dto_index: dict[str, dict[str, str]], http_mapping_pattern: Pattern[str], method_declaration_pattern: Pattern[str], interface_policy: dict[str, object], generic_tokens: set[str], minimum_chinese_ngram_length: int, maximum_chinese_ngram_length: int, identifier_minimum_length: int) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    controller_filename_markers = require_string_list(interface_policy, "controller_filename_markers")
    listener_annotations = require_string_list(interface_policy, "listener_annotations")
    validation_annotations = set(require_string_list(interface_policy, "validation_annotations"))
    class_mapping_annotations = require_string_list(interface_policy, "class_mapping_annotations")
    request_method_pattern = require_pattern(interface_policy, "request_method_pattern")
    http_annotation_methods = require_string_map(interface_policy, "http_annotation_methods")
    class_declaration_pattern = require_pattern(interface_policy, "class_declaration_pattern")
    dto_field_pattern = require_pattern(interface_policy, "dto_field_pattern")
    generic_type_pattern = require_pattern(interface_policy, "generic_type_pattern")
    javadoc_pattern = require_pattern(interface_policy, "javadoc_pattern")
    method_declaration_search_characters = require_positive_int(interface_policy, "method_declaration_search_characters")
    class_mapping_search_characters = require_positive_int(interface_policy, "class_mapping_search_characters")
    for item in java_files:
        text = item["text"]
        if not any(marker in Path(item["path"]).name for marker in controller_filename_markers) and not any(annotation in text for annotation in listener_annotations):
            continue
        class_name = extract_class_name(text, class_declaration_pattern)
        class_route = extract_class_route(text, class_mapping_annotations)
        for mapping in http_mapping_pattern.finditer(text):
            if is_class_mapping(text, mapping.start(), method_declaration_pattern, class_mapping_search_characters):
                continue
            declaration = method_declaration_pattern.search(text, mapping.end(), mapping.end() + method_declaration_search_characters)
            if declaration is None:
                continue
            route = join_routes(class_route, extract_mapping_route(mapping.group(2)))
            annotation_name = mapping.group(1)
            http_method = http_annotation_methods.get(annotation_name)
            if http_method is None:
                raise ValueError(f"Missing HTTP method mapping for annotation: {annotation_name}")
            if http_method == "FROM_ARGUMENTS":
                http_method = extract_request_method(mapping.group(2), request_method_pattern)
            method_end = find_block_end(text, declaration.end() - 1)
            params = parse_parameters(declaration.group(3), dto_index, validation_annotations, generic_type_pattern, dto_field_pattern)
            context = extract_leading_javadoc(text, mapping.start(), javadoc_pattern) + text[mapping.start():method_end]
            param_evidence = " ".join(
                f"{param.get('name', '')} {param.get('type', '')} "
                + " ".join(str(field.get("name", "")) for field in param.get("fields", []) if isinstance(field, dict))
                for param in params
            )
            entries.append({
                "service_id": item["service_id"],
                "entry_type": "HTTP",
                "http_method": http_method,
                "route": route,
                "class_name": class_name,
                "method_name": declaration.group(2),
                "return_type": declaration.group(1).strip(),
                "params": params,
                "context": context,
                "body": text[declaration.end():method_end],
                "tokens": sorted(extract_tokens(f"{class_name} {declaration.group(2)} {route} {context} {param_evidence}", generic_tokens, minimum_chinese_ngram_length, maximum_chinese_ngram_length, identifier_minimum_length)),
                "file": item["path"],
                "line": line_number(text, mapping.start()),
            })
    return dedupe(entries, ("service_id", "http_method", "route", "file"))


def extract_leading_javadoc(text: str, index: int, javadoc_pattern: Pattern[str]) -> str:
    prefix = text[:index]
    matches = list(javadoc_pattern.finditer(prefix))
    if not matches or prefix[matches[-1].end():].strip():
        return ""
    return matches[-1].group(0)


def extract_class_name(text: str, class_declaration_pattern: Pattern[str]) -> str:
    match = class_declaration_pattern.search(text)
    return match.group(1) if match else "unknown"


def extract_class_route(text: str, class_mapping_annotations: list[str]) -> str:
    annotation_pattern = "|".join(re.escape(annotation) for annotation in class_mapping_annotations)
    class_match = re.search(r"@(?:" + annotation_pattern + r")\s*\(([^)]*)\).*?\bclass\s+\w+", text, re.DOTALL)
    return extract_mapping_route(class_match.group(1)) if class_match else ""


def is_class_mapping(text: str, index: int, method_declaration_pattern: Pattern[str], class_mapping_search_characters: int) -> bool:
    next_code = text[index:index + class_mapping_search_characters]
    class_match = re.search(r"\bclass\s+\w+", next_code)
    method_match = method_declaration_pattern.search(next_code)
    return class_match is not None and (method_match is None or class_match.start() < method_match.start())


def extract_mapping_route(arguments: str) -> str:
    quoted = re.findall(r"[\"']([^\"']+)[\"']", arguments)
    for value in quoted:
        if value.startswith("/"):
            return value
    return ""


def extract_request_method(arguments: str, request_method_pattern: Pattern[str]) -> str:
    match = request_method_pattern.search(arguments)
    return match.group(1) if match else "UNKNOWN"


def join_routes(base: str, child: str) -> str:
    return "/" + "/".join(part.strip("/") for part in (base, child) if part.strip("/"))


def parse_parameters(raw_params: str, dto_index: dict[str, dict[str, str]], validation_annotations: set[str], generic_type_pattern: Pattern[str], dto_field_pattern: Pattern[str]) -> list[dict[str, object]]:
    params: list[dict[str, object]] = []
    for raw_param in split_parameters(raw_params):
        cleaned = re.sub(r"@\w+(?:\([^)]*\))?\s*", "", raw_param).strip()
        tokens = cleaned.split()
        if len(tokens) < 2:
            continue
        param_type = tokens[-2]
        name = tokens[-1]
        fields = parse_dto_fields(dto_index.get(strip_generic(param_type, generic_type_pattern)), validation_annotations, dto_field_pattern)
        params.append({"name": name, "type": param_type, "fields": fields})
    return params


def split_parameters(value: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    for character in value:
        if character in "(<[":
            depth += 1
        elif character in ")>]":
            depth -= 1
        if character == "," and depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(character)
    if current:
        parts.append("".join(current))
    return parts


def strip_generic(type_name: str, generic_type_pattern: Pattern[str]) -> str:
    match = generic_type_pattern.search(type_name)
    return match.group(1) if match else type_name


def parse_dto_fields(item: dict[str, str] | None, validation_annotations: set[str], dto_field_pattern: Pattern[str]) -> list[dict[str, object]]:
    if item is None:
        return []
    lines = item["text"].splitlines()
    fields: list[dict[str, object]] = []
    annotations: list[str] = []
    comments: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("@"):
            annotations.append(stripped)
            continue
        if stripped.startswith("*") and not stripped.startswith("*/"):
            comment = stripped.lstrip("*").strip()
            if comment and not comment.startswith("@"):
                comments.append(comment)
            continue
        match = dto_field_pattern.search(stripped)
        if match:
            annotation_names = {annotation.split("(", 1)[0].lstrip("@").split(".")[-1] for annotation in annotations}
            fields.append({
                "name": match.group(2),
                "type": match.group(1).strip(),
                "required": bool(annotation_names & validation_annotations),
                "description": comments[-1] if comments else "无",
            })
            annotations = []
            comments = []
        elif stripped and not stripped.startswith(("//", "/*", "*")):
            annotations = []
            comments = []
    return fields


def select_business_entries(entries: list[dict[str, object]], cases: list[dict[str, object]]) -> list[dict[str, object]]:
    route_roots = infer_testcase_route_roots(entries, cases)
    if not route_roots:
        return []
    return [
        entry for entry in entries
        if route_root(str(entry["route"])) in route_roots
    ]


def infer_testcase_route_roots(entries: list[dict[str, object]], cases: list[dict[str, object]]) -> set[str]:
    entry_roots = {route_root(str(entry["route"])) for entry in entries}
    roots: set[str] = set()
    for case in cases:
        for literal in as_string_list(case.get("routes", [])):
            segments = route_segments(literal)
            roots.update(root for root in entry_roots if root and root in segments)
    return roots


def route_segments(route: str) -> list[str]:
    return [segment for segment in route.split("?")[0].strip("/").split("/") if segment]


def route_root(route: str) -> str:
    segments = route_segments(route)
    return segments[0] if segments else ""


def routes_match(entry_route: str, consumer_route: str) -> bool:
    entry_segments = route_segments(entry_route)
    consumer_segments = route_segments(consumer_route)
    return bool(entry_segments) and len(consumer_segments) >= len(entry_segments) and consumer_segments[-len(entry_segments):] == entry_segments


def map_cases_to_entries(entries: list[dict[str, object]], cases: list[dict[str, object]], matching_policy: dict[str, object]) -> list[dict[str, object]]:
    minimum_score = require_positive_int(matching_policy, "minimum_score")
    max_inferred_cases_per_entry = require_positive_int(matching_policy, "max_inferred_cases_per_entry")
    minimum_token_document_frequency = require_positive_int(matching_policy, "minimum_token_document_frequency")
    maximum_token_document_frequency_ratio = require_ratio(matching_policy, "maximum_token_document_frequency_ratio")
    minimum_scored_token_length = require_positive_int(matching_policy, "minimum_scored_token_length")
    long_token_length = require_positive_int(matching_policy, "long_token_length")
    short_token_weight = require_positive_int(matching_policy, "short_token_weight")
    long_token_weight = require_positive_int(matching_policy, "long_token_weight")
    token_frequency: Counter[str] = Counter()
    for entry in entries:
        token_frequency.update(set(as_string_list(entry["tokens"])))
    mapped: list[dict[str, object]] = []
    for entry in entries:
        scored_cases = [
            (case_entry_score(case, entry, token_frequency, len(entries), minimum_token_document_frequency, maximum_token_document_frequency_ratio, minimum_scored_token_length, long_token_length, short_token_weight, long_token_weight), str(case["case_id"]))
            for case in cases
        ]
        literal_matches = [
            str(case["case_id"])
            for case in cases
            if any(routes_match(str(entry["route"]), literal) for literal in as_string_list(case.get("routes", [])))
        ]
        positive = [item for item in scored_cases if item[0] >= minimum_score]
        positive.sort(reverse=True)
        clone = dict(entry)
        clone.pop("context", None)
        clone.pop("body", None)
        inferred_matches = [case_id for _, case_id in positive[:max_inferred_cases_per_entry] if case_id not in literal_matches]
        clone["case_ids"] = literal_matches + inferred_matches
        mapped.append(clone)
    return mapped


def case_entry_score(case: dict[str, object], entry: dict[str, object], token_frequency: Counter[str], entry_count: int, minimum_token_document_frequency: int, maximum_token_document_frequency_ratio: float, minimum_scored_token_length: int, long_token_length: int, short_token_weight: int, long_token_weight: int) -> int:
    case_tokens = set(as_string_list(case["tokens"]))
    entry_tokens = set(as_string_list(entry["tokens"]))
    maximum_frequency = max(minimum_token_document_frequency, int(entry_count * maximum_token_document_frequency_ratio))
    shared = {
        token for token in case_tokens & entry_tokens
        if len(token) >= minimum_scored_token_length and token_frequency[token] <= maximum_frequency
    }
    return sum(long_token_weight if len(token) >= long_token_length else short_token_weight for token in shared)


def build_call_chains(entries: list[dict[str, object]], java_files: list[dict[str, str]], method_declaration_pattern: Pattern[str], interface_policy: dict[str, object]) -> list[dict[str, object]]:
    java_index = build_java_file_index(java_files)
    dependency_type_suffixes = require_string_list(interface_policy, "dependency_type_suffixes")
    implementation_suffixes = require_string_list(interface_policy, "implementation_suffixes")
    response_wrapper_prefixes = require_string_list(interface_policy, "response_wrapper_prefixes")
    injected_field_pattern = require_pattern(interface_policy, "injected_field_pattern")
    chains: list[dict[str, object]] = []
    for entry in entries:
        source = java_index.get(str(entry["class_name"]))
        if source is None:
            continue
        fields = parse_field_types(source["text"], injected_field_pattern)
        method_body = find_method_body(source["text"], str(entry["method_name"]), method_declaration_pattern)
        calls = re.findall(r"\b(\w+)\.(\w+)\s*\(", method_body)
        chain = [f"{entry['class_name']}#{entry['method_name']}"]
        dependencies: list[str] = []
        for variable, method in calls:
            target_type = fields.get(variable)
            if not target_type or any(target_type.startswith(prefix) for prefix in response_wrapper_prefixes):
                continue
            chain.append(f"{target_type}#{method}")
            dependencies.append(target_type)
            target = find_implementation(java_index, target_type, implementation_suffixes) or java_index.get(target_type)
            if target:
                nested_chain, nested_dependencies = trace_method_calls(target, method, java_index, set(), method_declaration_pattern, dependency_type_suffixes, implementation_suffixes, injected_field_pattern)
                chain.extend(nested_chain)
                dependencies.extend(nested_dependencies)
        chains.append({
            "signature": f"{entry['service_id']}::{entry['class_name']}#{entry['method_name']}",
            "case_ids": entry.get("case_ids", []),
            "chain": list(dict.fromkeys(chain)),
            "dependencies": list(dict.fromkeys(dependencies)),
        })
    return chains


def trace_method_calls(source: dict[str, str], method_name: str, java_index: dict[str, dict[str, str]], visited: set[str], method_declaration_pattern: Pattern[str], dependency_type_suffixes: list[str], implementation_suffixes: list[str], injected_field_pattern: Pattern[str]) -> tuple[list[str], list[str]]:
    source_name = Path(source["path"]).stem
    visit_key = f"{source_name}#{method_name}"
    if visit_key in visited:
        return [], []
    next_visited = set(visited)
    next_visited.add(visit_key)
    text = source["text"]
    body = find_method_body(text, method_name, method_declaration_pattern)
    fields = parse_field_types(text, injected_field_pattern)
    chain: list[str] = []
    dependencies: list[str] = []
    for variable, called_method in re.findall(r"\b(\w+)\.(\w+)\s*\(", body):
        target_type = fields.get(variable)
        if not target_type:
            continue
        chain.append(f"{target_type}#{called_method}")
        dependencies.append(target_type)
        if any(suffix in target_type for suffix in dependency_type_suffixes):
            continue
        target = find_implementation(java_index, target_type, implementation_suffixes) or java_index.get(target_type)
        if target:
            nested_chain, nested_dependencies = trace_method_calls(target, called_method, java_index, next_visited, method_declaration_pattern, dependency_type_suffixes, implementation_suffixes, injected_field_pattern)
            chain.extend(nested_chain)
            dependencies.extend(nested_dependencies)
    local_methods = {declaration.group(2) for declaration in method_declaration_pattern.finditer(text)}
    qualified_calls = {called_method for _, called_method in re.findall(r"\b(\w+)\.(\w+)\s*\(", body)}
    for called_method in re.findall(r"(?<![\w.])(\w+)\s*\(", body):
        if called_method == method_name or called_method in qualified_calls or called_method not in local_methods:
            continue
        chain.append(f"{source_name}#{called_method}")
        nested_chain, nested_dependencies = trace_method_calls(source, called_method, java_index, next_visited, method_declaration_pattern, dependency_type_suffixes, implementation_suffixes, injected_field_pattern)
        chain.extend(nested_chain)
        dependencies.extend(nested_dependencies)
    return list(dict.fromkeys(chain)), list(dict.fromkeys(dependencies))


def parse_field_types(text: str, injected_field_pattern: Pattern[str]) -> dict[str, str]:
    return {name: field_type for field_type, name in injected_field_pattern.findall(text)}


def find_implementation(index: dict[str, dict[str, str]], interface_name: str, implementation_suffixes: list[str]) -> dict[str, str] | None:
    for suffix in implementation_suffixes:
        implementation = index.get(f"{interface_name}{suffix}")
        if implementation is not None:
            return implementation
    return None


def find_method_body(text: str, method_name: str, method_declaration_pattern: Pattern[str]) -> str:
    for declaration in method_declaration_pattern.finditer(text):
        if declaration.group(2) != method_name:
            continue
        end = find_block_end(text, declaration.end() - 1)
        return text[declaration.end():end]
    return ""


def resolve_tables(entries: list[dict[str, object]], chains: list[dict[str, object]], java_files: list[dict[str, str]], metadata: dict[str, list[dict[str, object]]], services: list[dict[str, object]], table_annotation_pattern: Pattern[str], entity_reference_pattern: Pattern[str], interface_policy: dict[str, object], table_policy: dict[str, object]) -> list[dict[str, object]]:
    selected_identifiers = infer_domain_identifiers(entries)
    persistence_type_suffixes = require_string_list(interface_policy, "persistence_type_suffixes")
    validation_annotations = set(require_string_list(interface_policy, "validation_annotations"))
    dto_field_pattern = require_pattern(interface_policy, "dto_field_pattern")
    tenant_filter_fields = require_string_list(interface_policy, "tenant_filter_fields")
    sql_operations = require_string_list(table_policy, "sql_operations")
    max_sql_table_distance_characters = require_positive_int(table_policy, "max_sql_table_distance_characters")
    operation_fallback_label = require_string(table_policy, "operation_fallback_label")
    unresolved_schema_label = require_string(table_policy, "unresolved_schema_label")
    mapper_names = {
        dependency for chain in chains for dependency in as_string_list(chain["dependencies"])
        if any(suffix in dependency for suffix in persistence_type_suffixes)
    }
    java_index = build_java_file_index(java_files)
    entity_cases: dict[str, set[str]] = defaultdict(set)
    entity_chains: dict[str, set[str]] = defaultdict(set)
    for chain in chains:
        signature = str(chain["signature"])
        for dependency in as_string_list(chain["dependencies"]):
            mapper_source = java_index.get(dependency)
            if mapper_source is None or not any(suffix in dependency for suffix in persistence_type_suffixes):
                continue
            for entity_name in entity_reference_pattern.findall(mapper_source["text"]):
                entity_cases[entity_name].update(as_string_list(chain.get("case_ids", [])))
                entity_chains[entity_name].add(signature)
    service_platform = {str(service.get("service_id", "")): service for service in services}
    tables: list[dict[str, object]] = []
    for item in java_files:
        path_identifier = normalize_identifier(item["path"])
        class_name = Path(item["path"]).stem
        annotation = table_annotation_pattern.search(item["text"])
        if annotation is None:
            continue
        if selected_identifiers and not any(identifier in path_identifier for identifier in selected_identifiers):
            continue
        if class_name not in entity_chains:
            continue
        table_name = annotation.group(1)
        service = service_platform.get(item["service_id"], {})
        configured_connection = service.get("metadata_connection")
        all_matches = metadata.get(table_name, [])
        matches = [
            match for match in all_matches
            if not configured_connection or match.get("connection") == configured_connection
        ]
        platform_confirmed = service.get("platform_status") == "confirmed" or bool(service.get("platform_name"))
        if len(matches) == 1 and platform_confirmed:
            grade = "B"
            qualified_name = f"{matches[0]['schema']}.{table_name}"
            status = "confirmed"
        elif len(matches) > 1:
            grade = "-"
            qualified_name = " / ".join(f"{match['schema']}.{table_name}" for match in matches)
            status = "multiple_matches"
        else:
            grade = "C" if platform_confirmed else "D"
            qualified_name = f"{unresolved_schema_label}.{table_name}"
            status = "metadata_unresolved"
        tables.append({
            "service_id": item["service_id"],
            "platform": service.get("platform_name") or "待确认",
            "table_name": table_name,
            "qualified_name": qualified_name,
            "grade": grade,
            "status": status,
            "case_ids": sorted(entity_cases[class_name]),
            "call_chains": sorted(entity_chains[class_name]),
            "source_file": item["path"],
            "source_line": line_number(item["text"], annotation.start()),
            "fields": matches[0].get("columns", []) if len(matches) == 1 else parse_dto_fields(item, validation_annotations, dto_field_pattern),
            "indexes": matches[0].get("indexes", {}) if len(matches) == 1 else {},
            "constraints": matches[0].get("constraints", {}) if len(matches) == 1 else {},
            "operations": infer_operations(table_name, java_files, mapper_names, sql_operations, max_sql_table_distance_characters, operation_fallback_label),
            "tenant_isolation": infer_tenant_isolation(table_name, java_files, tenant_filter_fields),
        })
    return dedupe(tables, ("service_id", "table_name"))


def infer_domain_identifiers(entries: list[dict[str, object]]) -> set[str]:
    return {
        normalize_identifier(route_root(str(entry["route"])))
        for entry in entries
        if route_root(str(entry["route"]))
    }


def infer_operations(table_name: str, java_files: list[dict[str, str]], mapper_names: set[str], sql_operations: list[str], max_sql_table_distance_characters: int, operation_fallback_label: str) -> list[str]:
    operations: set[str] = set()
    for item in java_files:
        if mapper_names and Path(item["path"]).stem not in mapper_names and table_name not in item["text"]:
            continue
        lowered = item["text"].lower()
        for operation in sql_operations:
            if re.search(rf"\b{re.escape(operation)}\b[\s\S]{{0,{max_sql_table_distance_characters}}}\b{re.escape(table_name)}\b", lowered):
                operations.add(operation.upper())
    return sorted(operations) or [operation_fallback_label]


def infer_tenant_isolation(table_name: str, java_files: list[dict[str, str]], tenant_filter_fields: list[str]) -> str:
    for item in java_files:
        lowered = item["text"].lower()
        matched_fields = [field for field in tenant_filter_fields if field.lower() in lowered]
        if table_name.lower() in lowered and matched_fields:
            return f"存在租户字段代码证据（{', '.join(matched_fields)}），仍需逐条 SQL 复核"
    return "未在同一代码片段中确认策略定义的租户字段过滤"


def load_metadata(path: Path) -> dict[str, list[dict[str, object]]]:
    document = read_json_object(path, "metadata document")
    result: dict[str, list[dict[str, object]]] = defaultdict(list)
    connections = document.get("connections")
    if not isinstance(connections, list):
        raise TypeError("metadata_document.json.connections must be a list")
    for connection in connections:
        if not isinstance(connection, dict):
            continue
        connection_info = connection.get("connection")
        connection_name = connection_info.get("name") if isinstance(connection_info, dict) else None
        schemas = connection.get("schemas")
        if not isinstance(schemas, list):
            continue
        for schema in schemas:
            if not isinstance(schema, dict) or not isinstance(schema.get("name"), str):
                continue
            tables = schema.get("tables")
            if not isinstance(tables, list):
                continue
            for table in tables:
                if not isinstance(table, dict) or not isinstance(table.get("name"), str):
                    continue
                result[str(table["name"])].append({
                    "connection": connection_name,
                    "schema": schema["name"],
                    "columns": table.get("columns", []),
                    "indexes": table.get("indexes", {}),
                    "constraints": table.get("constraints", {}),
                })
    return result


def find_unclosed_cases(cases: list[dict[str, object]], entries: list[dict[str, object]]) -> list[dict[str, str]]:
    covered = {case_id for entry in entries for case_id in as_string_list(entry.get("case_ids", []))}
    return [
        {"case_id": str(case["case_id"]), "reason": "未在代码中找到满足入口判定规则的关联方法，需人工确认"}
        for case in cases if str(case["case_id"]) not in covered
    ]


def write_core_interfaces(path: Path, entries: list[dict[str, object]], findings: list[dict[str, str]]) -> None:
    lines = [
        "# 核心流程接口文档", "", "## 一、核心流程接口清单", "",
        "| 用例编号 | 接口名称/描述 | 接口类型与地址 | 请求参数 | 返回参数 | 调用链路 | 代码位置 |",
        "|---|---|---|---|---|---|---|",
    ]
    for entry in entries:
        params = format_params(entry.get("params", []))
        cases = ", ".join(as_string_list(entry.get("case_ids", []))) or "未映射"
        location = f"{entry['service_id']} - {entry['file']}#L{entry['line']}"
        lines.append(f"| {cases} | {entry['class_name']}#{entry['method_name']} | {entry['http_method']} {entry['route']} | {params} | {entry['return_type']} | 见 call_chain_evidence.json | {location} |")
    append_unclosed(lines, findings)
    write_markdown(path, lines)


def write_unit_interfaces(path: Path, entries: list[dict[str, object]], chains: list[dict[str, object]], java_files: list[dict[str, str]], findings: list[dict[str, str]], test_path_segments: list[str]) -> None:
    tests = [item for item in java_files if any(segment.lower() in item["path"].lower() for segment in test_path_segments)]
    lines = [
        "# 单元测试接口文档", "", "## 一、单元测试目标接口清单", "",
        "| 用例编号 | 方法签名 | 输入边界场景 | 需隔离的外部依赖 | 当前覆盖状态 | 代码位置 |",
        "|---|---|---|---|---|---|",
    ]
    chain_map = {str(chain["signature"]): chain for chain in chains}
    for entry in entries:
        signature = f"{entry['service_id']}::{entry['class_name']}#{entry['method_name']}"
        chain = chain_map.get(signature, {})
        dependencies = ", ".join(as_string_list(chain.get("dependencies", []))) or "无明确外部依赖"
        coverage = "已覆盖" if any(str(entry["method_name"]) in test["text"] for test in tests) else "未覆盖"
        cases = ", ".join(as_string_list(entry.get("case_ids", []))) or "未映射"
        params = format_params(entry.get("params", []))
        lines.append(f"| {cases} | {entry['class_name']}#{entry['method_name']}({params}) | 正常/异常/边界值以关联用例为准 | {dependencies} | {coverage} | {entry['service_id']} - {entry['file']}#L{entry['line']} |")
    append_unclosed(lines, findings)
    write_markdown(path, lines)


def write_table_report(path: Path, tables: list[dict[str, object]], findings: list[dict[str, str]], max_report_fields: int) -> None:
    lines = [
        "# 用例中所使用的数据表文档", "", "## 一、关联数据表清单", "",
        "| 用例编号 | 所属平台 | 库.表名 | 确认等级 | 判定依据说明 | 关键字段 | 读/写类型 | 租户隔离 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for table in tables:
        fields = table.get("fields", [])
        field_names = ", ".join(str(field.get("name", "")) for field in fields[:max_report_fields] if isinstance(field, dict)) if isinstance(fields, list) else ""
        cases = ", ".join(as_string_list(table.get("case_ids", []))) or "未映射"
        reason = table_grade_reason(str(table["grade"]), str(table["status"]))
        operations = "/".join(as_string_list(table.get("operations", [])))
        lines.append(f"| {cases} | {table['platform']} | {table['qualified_name']} | {table['grade']} | {reason} | {field_names or '未解析'} | {operations} | {table['tenant_isolation']} |")
    append_unclosed(lines, findings)
    write_markdown(path, lines)


def write_test_data(path: Path, entries: list[dict[str, object]], tables: list[dict[str, object]], sql_template_grades: set[str]) -> None:
    lines = [
        "# 测试数据文档", "",
        "> **安全声明**：本文档中的 SQL 仅供测试/预发环境参考使用，字段完整性未经 DBA 复核，禁止直接在生产环境执行。执行前必须人工确认 NOT NULL、唯一索引、外键及目标环境；所有 TODO 必须补全后才可执行。",
        "",
    ]
    confirmed = [table for table in tables if table["grade"] in sql_template_grades]
    case_routes: dict[str, list[str]] = defaultdict(list)
    for entry in entries:
        for case_id in as_string_list(entry.get("case_ids", [])):
            case_routes[case_id].append(f"{entry['http_method']} {entry['route']}")
    for case_id, routes in sorted(case_routes.items()):
        lines.extend([f"## {case_id}", "", "### 接口", "", *[f"- {route}" for route in sorted(set(routes))], "", "### 涉及数据表", ""])
        if not confirmed:
            lines.extend(["- 无 A/B 级表；待人工确认平台和库归属后补充 SQL。", ""])
            continue
        lines.extend(["| 库.表名 | 确认等级 |", "|---|---|"])
        lines.extend(f"| {table['qualified_name']} | {table['grade']} |" for table in confirmed)
        lines.extend(["", "### 测试数据构造 SQL", "", "```sql"])
        for table in confirmed:
            lines.append(f"-- TODO: 根据 {case_id} 场景补全 {table['qualified_name']} 的真实主键和全部 NOT NULL 字段。")
            lines.append(f"-- INSERT INTO {table['qualified_name']} (...) VALUES (...);")
        lines.extend(["```", "", "### 清理 SQL", "", "```sql", "-- TODO: 仅允许使用主键、策略定义的租户字段或唯一测试标识清理。", "```", ""])
    write_markdown(path, lines)


def write_summary(path: Path, cases: list[dict[str, object]], entries: list[dict[str, object]], tables: list[dict[str, object]], findings: list[dict[str, str]]) -> None:
    grades = Counter(str(table["grade"]) for table in tables)
    lines = [
        "# 用例驱动代码证据摘要", "",
        f"- 用例数量：{len(cases)}",
        f"- 核心流程接口：{len(entries)}",
        f"- 关联数据表：{len(tables)}（A={grades['A']}，B={grades['B']}，C={grades['C']}，D={grades['D']}，待确认={grades['-']}）",
        f"- 未闭环用例：{len(findings)}",
    ]
    write_markdown(path, lines)


def update_code_review_report(path: Path, cases: list[dict[str, object]], entries: list[dict[str, object]], tables: list[dict[str, object]], findings: list[dict[str, str]]) -> None:
    start_marker = "<!-- testcase-evidence:start -->"
    end_marker = "<!-- testcase-evidence:end -->"
    grades = Counter(str(table["grade"]) for table in tables)
    conflicts = sum(1 for table in tables if table["grade"] == "-")
    section = "\n".join([
        start_marker,
        "## 五、用例驱动的接口与数据表识别摘要",
        "",
        f"- 用例覆盖：共分析 {len(cases)} 条，识别核心流程接口 {len(entries)} 个，关联数据表 {len(tables)} 张。",
        f"- 表等级：A={grades['A']}，B={grades['B']}，C={grades['C']}，D={grades['D']}，待人工确认={grades['-']}。",
        f"- 三方一致性：存在 {conflicts} 张多库同名或冲突表。",
        f"- 未闭环用例：{len(findings)} 条。",
        "- 详情：[核心流程接口](core_process_interfaces.md) | [单元测试目标](unit_test_interfaces.md) | [关联数据表](test_case_tables.md) | [测试数据](test_case_data.md)",
        end_marker,
    ])
    existing = path.read_text(encoding="utf-8") if path.exists() else "# 代码审查报告\n"
    pattern = re.compile(re.escape(start_marker) + r"[\s\S]*?" + re.escape(end_marker))
    updated = pattern.sub(section, existing) if pattern.search(existing) else existing.rstrip() + "\n\n" + section + "\n"
    path.write_text(updated, encoding="utf-8", newline="\n")


def update_confirmation(path: Path, manifest: dict[str, object], entries: list[dict[str, object]], tables: list[dict[str, object]], findings: list[dict[str, str]]) -> None:
    existing = read_json_object(path, "code source confirmation") if path.exists() else {}
    services = validate_services(manifest)
    commits = {
        str(service.get("service_id", "")): str(service.get("commit", ""))
        for service in services
    }
    payload = dict(existing)
    payload.update({
        "approved": False,
        "reason": "用例证据分析已完成，等待用户显式批准本轮代码源结果。",
        "source_run_id": manifest.get("source_run_id"),
        "commits": commits,
        "testcase_analysis_status": "completed",
        "interface_count": len(entries),
        "table_count": len(tables),
        "unclosed_case_count": len(findings),
    })
    write_json(path, payload)


def append_unclosed(lines: list[str], findings: list[dict[str, str]]) -> None:
    lines.extend(["", "## 二、未闭环用例", "", "| 用例编号 | 说明 |", "|---|---|"])
    if findings:
        lines.extend(f"| {finding['case_id']} | {finding['reason']} |" for finding in findings)
    else:
        lines.append("| 无 | 无 |")


def format_params(raw_params: object) -> str:
    if not isinstance(raw_params, list) or not raw_params:
        return "无（源码方法确认为无参）"
    values: list[str] = []
    for param in raw_params:
        if not isinstance(param, dict):
            continue
        fields = param.get("fields")
        field_text = ""
        if isinstance(fields, list) and fields:
            field_text = " {" + "; ".join(
                f"{field.get('name')}:{field.get('type')}{'*' if field.get('required') else ''}"
                for field in fields if isinstance(field, dict)
            ) + "}"
        values.append(f"{param.get('name')}:{param.get('type')}{field_text}")
    return "；".join(values)


def table_grade_reason(grade: str, status: str) -> str:
    if grade == "A":
        return "SQL 中出现完整库.表名"
    if grade == "B":
        return "代码表名与平台元数据唯一匹配"
    if grade == "C":
        return "Entity 注解与平台已确认，元数据未唯一匹配"
    if grade == "D":
        return "仅有代码表名，平台或元数据未确认"
    return "代码与元数据存在多库同名或冲突，需人工确认"


def extract_tokens(value: str, generic_tokens: set[str], minimum_chinese_ngram_length: int, maximum_chinese_ngram_length: int, identifier_minimum_length: int) -> set[str]:
    tokens = extract_identifier_tokens(value, generic_tokens, identifier_minimum_length)
    for sequence in re.findall(rf"[\u4e00-\u9fff]{{{minimum_chinese_ngram_length},}}", value):
        maximum = min(maximum_chinese_ngram_length, len(sequence))
        for size in range(minimum_chinese_ngram_length, maximum + 1):
            tokens.update(sequence[index:index + size] for index in range(len(sequence) - size + 1))
    return {token for token in tokens if token not in generic_tokens}


def extract_identifier_tokens(value: str, generic_tokens: set[str], identifier_minimum_length: int) -> set[str]:
    expanded = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    return {
        token.lower() for token in re.findall(rf"[A-Za-z][A-Za-z0-9]{{{identifier_minimum_length - 1},}}", expanded)
        if token.lower() not in generic_tokens
    }


def normalize_identifier(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def as_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def find_block_end(text: str, opening_brace_index: int) -> int:
    depth = 0
    for index in range(opening_brace_index, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return index + 1
    return len(text)


def dedupe(items: list[dict[str, object]], keys: tuple[str, ...]) -> list[dict[str, object]]:
    seen: set[tuple[str, ...]] = set()
    result: list[dict[str, object]] = []
    for item in items:
        signature = tuple(str(item.get(key, "")) for key in keys)
        if signature in seen:
            continue
        seen.add(signature)
        result.append(item)
    return result


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")


def write_markdown(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8", newline="\n")


def sync_latest(run_dir: Path) -> None:
    if run_dir.name == "latest":
        return
    output_root = run_dir.parent.parent
    latest_dir = output_root / "latest"
    if latest_dir.exists():
        shutil.rmtree(latest_dir)
    shutil.copytree(run_dir, latest_dir)


if __name__ == "__main__":
    raise SystemExit(main())
