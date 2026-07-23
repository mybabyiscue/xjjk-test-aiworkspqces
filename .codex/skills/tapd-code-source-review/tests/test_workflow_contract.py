"""Regression tests for workflow gates and evidence isolation."""

from __future__ import annotations

import json
from pathlib import Path
import re

import pytest

from scripts.analyze_testcase_evidence import (
    apply_gateway_prefixes,
    build_http_mapping_pattern,
    confirmed_tables,
    entry_intersects_changed_ranges,
    find_block_end,
    map_cases_to_entries,
    parse_test_cases,
    scan_java_entries,
    select_business_entries,
    unresolved_tables,
)
from scripts.workflow_contract import (
    parse_code_url,
    sha256_file,
    validate_approved_source_run,
    write_json,
)


def test_parse_code_url_requires_explicit_git_branch() -> None:
    url, source_type, branch = parse_code_url(
        "https://git.example/team/service.git#feature-123"
    )

    assert url == "https://git.example/team/service.git"
    assert source_type == "git"
    assert branch == "feature-123"

    with pytest.raises(ValueError, match="explicit #branch"):
        parse_code_url("https://git.example/team/service.git")


def test_source_approval_is_bound_to_manifest_and_codegraph(tmp_path: Path) -> None:
    run_dir = tmp_path / "source_run"
    cache_dir = tmp_path / "cache"
    (cache_dir / ".codegraph").mkdir(parents=True)
    (cache_dir / ".codegraph" / "codegraph.db").write_bytes(b"index")
    run_dir.mkdir()
    manifest_path = run_dir / "source_manifest.json"
    write_json(manifest_path, {
        "source_run_id": "source-1",
        "code_sources": [{
            "service_id": "service_001",
            "source_type": "git",
            "branch": "feature-123",
            "commit": "abc123",
            "cache_path": str(cache_dir),
            "fetch_status": "success",
            "codegraph_status": "healthy",
        }],
    })
    write_json(run_dir / "code_source_confirmation.json", {
        "approved": True,
        "source_run_id": "source-1",
        "manifest_sha256": sha256_file(manifest_path),
    })

    validate_approved_source_run(run_dir)

    manifest_path.write_text(manifest_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="changed after approval"):
        validate_approved_source_run(run_dir)


def test_source_gate_rejects_failed_service(tmp_path: Path) -> None:
    run_dir = tmp_path / "source_run"
    run_dir.mkdir()
    manifest_path = run_dir / "source_manifest.json"
    write_json(manifest_path, {
        "source_run_id": "source-1",
        "code_sources": [{
            "service_id": "service_001",
            "source_type": "git",
            "branch": "feature-123",
            "commit": "",
            "cache_path": "",
            "fetch_status": "failed",
            "codegraph_status": "",
        }],
    })
    write_json(run_dir / "code_source_confirmation.json", {
        "approved": True,
        "source_run_id": "source-1",
        "manifest_sha256": sha256_file(manifest_path),
    })

    with pytest.raises(ValueError, match="not fetched successfully"):
        validate_approved_source_run(run_dir)


def test_gateway_prefix_and_table_resolution_are_isolated() -> None:
    entries = [{"service_id": "service_001", "route": "/mp/activity"}]
    services = [{"service_id": "service_001", "gateway_prefix": "/product"}]
    tables = [
        {"table_name": "confirmed_table", "status": "confirmed", "grade": "B"},
        {"table_name": "unknown_table", "status": "metadata_unresolved", "grade": "C"},
    ]

    updated = apply_gateway_prefixes(entries, services)

    assert updated[0]["route"] == "/product/mp/activity"
    assert updated[0]["controller_route"] == "/mp/activity"
    assert [table["table_name"] for table in confirmed_tables(tables)] == ["confirmed_table"]
    assert [table["table_name"] for table in unresolved_tables(tables)] == ["unknown_table"]


def test_gateway_prefix_uses_longest_matching_module_rule() -> None:
    entries = [
        {
            "service_id": "service_001",
            "file": "cache/mall4cloud-product/src/StartLimitActivityController.java",
            "route": "/mp/start_limit_activity",
        },
        {
            "service_id": "service_001",
            "file": "cache/mall4cloud-order/src/OrderController.java",
            "route": "/order/confirm",
        },
        {
            "service_id": "service_001",
            "file": "cache/other/src/HealthController.java",
            "route": "/health",
        },
    ]
    services = [{
        "service_id": "service_001",
        "gateway_prefix": "",
        "gateway_prefix_rules": [
            {"path_fragment": "mall4cloud-product", "prefix": "/product"},
            {"path_fragment": "mall4cloud-order", "prefix": "/order"},
        ],
    }]

    updated = apply_gateway_prefixes(entries, services)

    assert [entry["route"] for entry in updated] == [
        "/product/mp/start_limit_activity",
        "/order/order/confirm",
        "/health",
    ]


def test_business_tokens_select_entries_when_cases_have_no_routes() -> None:
    entries = [
        {
            "service_id": "service_001",
            "route": "/mp/start_limit_activity",
            "tokens": ["起售限购活动", "活动保存"],
        },
        {
            "service_id": "service_001",
            "route": "/health",
            "tokens": ["健康检查"],
        },
    ]
    cases = [{"case_id": "TC001", "routes": [], "tokens": ["起售限购活动", "活动保存"]}]
    policy = {
        "minimum_score": 3,
        "max_inferred_cases_per_entry": 5,
        "max_inferred_entries_per_case": 3,
        "minimum_token_document_frequency": 1,
        "maximum_token_document_frequency_ratio": 1.0,
        "minimum_scored_token_length": 4,
        "minimum_chinese_scored_token_length": 2,
        "long_token_length": 5,
        "short_token_weight": 2,
        "long_token_weight": 3,
        "chinese_token_weight": 6,
        "identifier_aliases": {},
    }

    selected = select_business_entries(entries, cases, set())
    mapped = map_cases_to_entries(selected, cases, policy)

    assert [entry["route"] for entry in mapped] == ["/mp/start_limit_activity"]
    assert mapped[0]["case_ids"] == ["TC001"]


def test_identifier_aliases_map_changed_purchase_routes_to_chinese_cases() -> None:
    entries = [
        {"service_id": "service_001", "route": "/product/ma/spu/prod_info", "tokens": ["prod", "info"]},
        {"service_id": "service_001", "route": "/product/shop_cart/info", "tokens": ["shop", "cart", "info"]},
        {"service_id": "service_001", "route": "/order/order/confirm", "tokens": ["order", "confirm"]},
        {"service_id": "service_001", "route": "/order/order/submit", "tokens": ["order", "submit"]},
        {"service_id": "service_001", "route": "/product/inner/start_limit_activity/validate_submit", "tokens": ["start", "limit", "validate", "submit"]},
        {"service_id": "service_001", "route": "/product/inner/start_limit_activity/rules", "tokens": ["start", "limit", "rules"]},
    ]
    cases = [
        {"case_id": "TC001", "routes": [], "tokens": ["商品详情"]},
        {"case_id": "TC002", "routes": [], "tokens": ["购物车"]},
        {"case_id": "TC003", "routes": [], "tokens": ["结算"]},
        {"case_id": "TC004", "routes": [], "tokens": ["提交订单", "提交"]},
        {"case_id": "TC005", "routes": [], "tokens": ["起售", "限购", "校验"]},
        {"case_id": "TC006", "routes": [], "tokens": ["起售", "限购", "规则"]},
    ]
    policy = {
        "minimum_score": 6,
        "max_inferred_cases_per_entry": 5,
        "max_inferred_entries_per_case": 3,
        "minimum_token_document_frequency": 1,
        "maximum_token_document_frequency_ratio": 1.0,
        "minimum_scored_token_length": 4,
        "minimum_chinese_scored_token_length": 2,
        "long_token_length": 5,
        "short_token_weight": 2,
        "long_token_weight": 3,
        "chinese_token_weight": 6,
        "identifier_aliases": {
            "cart": ["购物车"],
            "confirm": ["结算"],
            "info": ["商品详情"],
            "limit": ["限购"],
            "rules": ["规则"],
            "start": ["起售"],
            "submit": ["提交"],
            "validate": ["校验"],
        },
    }

    mapped = map_cases_to_entries(entries, cases, policy)

    assert {entry["route"] for entry in mapped} == {entry["route"] for entry in entries}


def test_changed_line_ranges_exclude_unchanged_methods_in_modified_file(tmp_path: Path) -> None:
    controller = tmp_path / "OrderController.java"
    controller.write_text("class OrderController {}\n", encoding="utf-8")
    entries = [
        {"route": "/order/confirm", "file": str(controller), "line": 20, "end_line": 80},
        {"route": "/order/pay_info", "file": str(controller), "line": 100, "end_line": 120},
    ]
    changed_ranges = {str(controller.resolve()).casefold(): [(45, 50)]}

    selected = select_business_entries(entries, [{"routes": []}], changed_ranges)

    assert [entry["route"] for entry in selected] == ["/order/confirm"]
    assert entry_intersects_changed_ranges(entries[0], changed_ranges)
    assert not entry_intersects_changed_ranges(entries[1], changed_ranges)


def test_method_declaration_pattern_handles_throws_clause() -> None:
    policy_path = Path(__file__).resolve().parents[1] / "assets" / "review-policy.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    pattern = re.compile(policy["interface_detection"]["method_declaration_pattern"])
    source = """
public String confirm(OrderDTO request) throws ExecutionException, InterruptedException {
    if (request != null) {
        return "ok";
    }
    return "empty";
}
""".strip()

    declaration = pattern.search(source)

    assert declaration is not None
    assert declaration.group(2) == "confirm"
    assert find_block_end(source, declaration.end() - 1) == len(source)


def test_interface_tokens_exclude_method_body_business_noise(tmp_path: Path) -> None:
    policy_path = Path(__file__).resolve().parents[1] / "assets" / "review-policy.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    interface_policy = policy["interface_detection"]
    source = """
@RestController
@RequestMapping("/order")
public class OrderController {
    /** 订单结算。 */
    @PostMapping("/confirm")
    public String confirm(OrderDTO request) {
        String unrelated = "退款售后库存优惠券";
        return unrelated;
    }
}
""".strip()
    controller = tmp_path / "OrderController.java"
    controller.write_text(source, encoding="utf-8")

    entries = scan_java_entries(
        [{"service_id": "service_001", "path": str(controller), "text": source}],
        {},
        build_http_mapping_pattern(interface_policy["http_mapping_annotations"]),
        re.compile(interface_policy["method_declaration_pattern"]),
        interface_policy,
        set(policy["case_matching"]["generic_tokens"]),
        2,
        6,
        3,
    )

    assert "结算" in entries[0]["tokens"]
    assert "退款" not in entries[0]["tokens"]


def test_testcase_parser_stops_before_next_section(tmp_path: Path) -> None:
    test_cases = tmp_path / "test_cases.md"
    test_cases.write_text(
        "# 测试用例\n\n## 三、P2\n\n### TC001 - 活动查询\n"
        "- **预期结果**：返回活动\n\n## BLAST 测试点矩阵\n\n"
        "| TP001 | TC001 | unrelated appendix token |\n",
        encoding="utf-8",
    )

    cases = parse_test_cases(
        test_cases,
        re.compile(r"^###\s+(TC\d{3})\s+-\s+(.+)$", re.MULTILINE),
        re.compile(r"(/[A-Za-z0-9_./{}-]+)"),
        set(),
        2,
        6,
        3,
    )

    assert "unrelated appendix token" not in cases[0]["body"]


def test_http_mapping_pattern_accepts_annotations_without_arguments() -> None:
    pattern = build_http_mapping_pattern(["GetMapping", "PostMapping"])

    no_arguments = pattern.search("@GetMapping\npublic String detail()")
    with_arguments = pattern.search('@PostMapping("/save")')

    assert no_arguments is not None
    assert no_arguments.group(1) == "GetMapping"
    assert no_arguments.group(2) is None
    assert with_arguments is not None
    assert with_arguments.group(2) == '"/save"'
