#!/usr/bin/env python3
"""Manage MySQL connections, schema caches, and document-based metadata search."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pymysql


SKILL_DIR = Path(__file__).resolve().parent.parent
STATE_DIR = SKILL_DIR / "state"
CACHE_DIR = STATE_DIR / "cache"
DOCUMENT_DIR = STATE_DIR / "documents"
CONNECTIONS_FILE = STATE_DIR / "connections.json"
DOMAIN_FILE = SKILL_DIR / "references" / "business_domains.json"
DOCUMENT_JSON_FILE = DOCUMENT_DIR / "metadata_document.json"
DOCUMENT_MD_FILE = DOCUMENT_DIR / "metadata_document.md"
SYSTEM_SCHEMAS = {"information_schema", "mysql", "performance_schema", "sys"}
EXCLUDED_SCHEMA_PREFIXES = ("aigis", "aj", "bak")

DEFAULT_CONNECTIONS = {
    "connections": [
        {
            "name": "丝路测试",
            "db_type": "mysql",
            "jdbc": "jdbc:mysql://192.168.70.89:3306",
            "host": "192.168.70.89",
            "port": 3306,
            "username": "silkroad",
            "password": "83lchichucrodrl",
            "enabled": True,
            "notes": "初始登记连接",
        }
    ]
}

DEFAULT_DOMAINS = {
    "订单": {
        "aliases": ["订单", "order", "orders", "trade", "交易", "下单", "销售单", "商城订单", "预约单", "工单"]
    },
    "用户": {
        "aliases": ["用户", "user", "users", "member", "会员", "客户", "customer", "account", "账号"]
    },
    "支付": {
        "aliases": ["支付", "pay", "payment", "payments", "refund", "退款", "收款", "结算", "账单", "billing"]
    },
    "优惠券": {
        "aliases": ["优惠券", "coupon", "voucher", "折扣", "促销", "活动券", "卡券"]
    },
}


def ensure_state() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    DOCUMENT_DIR.mkdir(parents=True, exist_ok=True)
    if not CONNECTIONS_FILE.exists():
        save_json(CONNECTIONS_FILE, DEFAULT_CONNECTIONS)
    if not DOMAIN_FILE.exists():
        save_json(DOMAIN_FILE, DEFAULT_DOMAINS)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sanitize_name(name: str) -> str:
    value = re.sub(r"[^0-9A-Za-z_\-\u4e00-\u9fff]+", "_", name.strip())
    return value.strip("_") or "connection"


def cache_file(name: str) -> Path:
    return CACHE_DIR / f"{sanitize_name(name)}.json"


def extract_host_port(jdbc: str) -> tuple[str, int]:
    match = re.match(r"jdbc:mysql://([^:/?#]+)(?::(\d+))?", jdbc.strip())
    if not match:
        raise ValueError(f"Unsupported JDBC format: {jdbc}")
    return match.group(1), int(match.group(2) or 3306)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage MySQL metadata caches and documents.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    upsert_parser = subparsers.add_parser("upsert-connection", help="Add or update a connection by name.")
    upsert_parser.add_argument("--name", required=True)
    upsert_parser.add_argument("--jdbc", required=True)
    upsert_parser.add_argument("--username", required=True)
    upsert_parser.add_argument("--password", required=True)
    upsert_parser.add_argument("--notes", default="")

    list_parser = subparsers.add_parser("list-connections", help="List saved connections.")
    list_parser.add_argument("--show-disabled", action="store_true")

    refresh_parser = subparsers.add_parser("refresh", help="Refresh caches and rebuild the internal document.")
    refresh_parser.add_argument("--connection", help="Refresh only one named connection.")

    subparsers.add_parser("rebuild-docs", help="Rebuild internal documents from existing caches.")

    search_parser = subparsers.add_parser("search", help="Search the internal metadata document.")
    search_parser.add_argument("query", help='User query, for example: "订单表"')
    search_parser.add_argument("--connection", help="Search only one named connection.")
    search_parser.add_argument("--max-tables", type=int, default=80)

    return parser.parse_args()


def load_connections() -> list[dict[str, Any]]:
    ensure_state()
    return load_json(CONNECTIONS_FILE).get("connections", [])


def save_connections(connections: list[dict[str, Any]]) -> None:
    save_json(CONNECTIONS_FILE, {"connections": connections})


def get_domains() -> dict[str, Any]:
    ensure_state()
    return load_json(DOMAIN_FILE)


def list_connections(show_disabled: bool) -> None:
    for row in load_connections():
        if not show_disabled and not row.get("enabled", True):
            continue
        print(
            f"{row['name']}\t{row['db_type']}\t{row['jdbc']}\t"
            f"{row['username']}\t{'enabled' if row.get('enabled', True) else 'disabled'}"
        )


def select_connections(name: str | None) -> list[dict[str, Any]]:
    rows = [row for row in load_connections() if row.get("enabled", True)]
    if name:
        rows = [row for row in rows if row["name"] == name]
    if not rows:
        raise SystemExit(f"No enabled connection found for: {name}")
    return rows


def upsert_connection(name: str, jdbc: str, username: str, password: str, notes: str) -> str:
    host, port = extract_host_port(jdbc)
    payload = {
        "name": name,
        "db_type": "mysql",
        "jdbc": jdbc,
        "host": host,
        "port": port,
        "username": username,
        "password": password,
        "enabled": True,
        "notes": notes,
    }
    connections = load_connections()
    existing = next((item for item in connections if item["name"] == name), None)
    if existing is None:
        connections.append(payload)
        action = "added"
    else:
        existing.update(payload)
        action = "updated"
    save_connections(connections)
    return action


def fetch_all(cursor: pymysql.cursors.Cursor, sql: str) -> list[dict[str, Any]]:
    cursor.execute(sql)
    return list(cursor.fetchall())


@dataclass
class ConnectionResult:
    name: str
    ok: bool
    message: str
    cache_path: str | None = None
    issue_count: int = 0


def refresh_connection(connection: dict[str, Any]) -> ConnectionResult:
    client = None
    max_retries = 3
    connect_timeout = 5
    retry_delay = 1.0
    
    for attempt in range(1, max_retries + 1):
        try:
            client = pymysql.connect(
                host=connection["host"],
                port=int(connection["port"]),
                user=connection["username"],
                password=connection["password"],
                charset="utf8mb4",
                autocommit=True,
                ssl_disabled=True,
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=connect_timeout,
                read_timeout=120,
                write_timeout=120,
            )
            break
        except Exception as exc:
            if attempt == max_retries:
                return ConnectionResult(connection["name"], False, f"connect failed after {max_retries} attempts: {exc}")
            print(f"  [warn] Connection attempt {attempt} failed for {connection['name']}, retrying in {retry_delay}s... (Error: {exc})")
            time.sleep(retry_delay)

    try:
        with client.cursor() as cursor:
            schemas = fetch_all(cursor, "SELECT SCHEMA_NAME, DEFAULT_CHARACTER_SET_NAME, DEFAULT_COLLATION_NAME FROM information_schema.SCHEMATA ORDER BY SCHEMA_NAME")
            tables = fetch_all(cursor, "SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE, ENGINE, TABLE_COLLATION, TABLE_COMMENT FROM information_schema.TABLES ORDER BY TABLE_SCHEMA, TABLE_NAME")
            columns = fetch_all(cursor, "SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, ORDINAL_POSITION, COLUMN_TYPE, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_KEY, EXTRA, COLUMN_COMMENT FROM information_schema.COLUMNS ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION")
            statistics = fetch_all(cursor, "SELECT TABLE_SCHEMA, TABLE_NAME, INDEX_NAME, NON_UNIQUE, SEQ_IN_INDEX, COLUMN_NAME FROM information_schema.STATISTICS ORDER BY TABLE_SCHEMA, TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX")
            constraints = fetch_all(cursor, "SELECT tc.TABLE_SCHEMA, tc.TABLE_NAME, tc.CONSTRAINT_NAME, tc.CONSTRAINT_TYPE, kcu.COLUMN_NAME, kcu.REFERENCED_TABLE_SCHEMA, kcu.REFERENCED_TABLE_NAME, kcu.REFERENCED_COLUMN_NAME, kcu.ORDINAL_POSITION FROM information_schema.TABLE_CONSTRAINTS tc LEFT JOIN information_schema.KEY_COLUMN_USAGE kcu ON kcu.CONSTRAINT_SCHEMA = tc.CONSTRAINT_SCHEMA AND kcu.TABLE_SCHEMA = tc.TABLE_SCHEMA AND kcu.TABLE_NAME = tc.TABLE_NAME AND kcu.CONSTRAINT_NAME = tc.CONSTRAINT_NAME ORDER BY tc.TABLE_SCHEMA, tc.TABLE_NAME, tc.CONSTRAINT_NAME, kcu.ORDINAL_POSITION")
            routines = fetch_all(cursor, "SELECT ROUTINE_SCHEMA, ROUTINE_NAME, ROUTINE_TYPE FROM information_schema.ROUTINES ORDER BY ROUTINE_SCHEMA, ROUTINE_NAME")
            triggers = fetch_all(cursor, "SELECT TRIGGER_SCHEMA, TRIGGER_NAME, EVENT_MANIPULATION, EVENT_OBJECT_TABLE FROM information_schema.TRIGGERS ORDER BY TRIGGER_SCHEMA, TRIGGER_NAME")
    except Exception as exc:
        return ConnectionResult(connection["name"], False, f"metadata query failed: {exc}")
    finally:
        client.close()

    payload = build_cache_payload(connection, schemas, tables, columns, statistics, constraints, routines, triggers)
    payload["issues"] = detect_issues(payload)
    target = cache_file(connection["name"])
    save_json(target, payload)
    summary = payload["summary"]
    message = f"refreshed {summary['business_schema_count']} schemas, {summary['base_table_count']} tables, {summary['view_count']} views"
    return ConnectionResult(connection["name"], True, message, str(target), len(payload["issues"]))


def build_cache_payload(connection: dict[str, Any], schemas: list[dict[str, Any]], tables: list[dict[str, Any]], columns: list[dict[str, Any]], statistics: list[dict[str, Any]], constraints: list[dict[str, Any]], routines: list[dict[str, Any]], triggers: list[dict[str, Any]]) -> dict[str, Any]:
    schema_map: dict[str, Any] = {}
    for schema in schemas:
        schema_name = schema["SCHEMA_NAME"]
        schema_map[schema_name] = {
            "name": schema_name,
            "default_character_set_name": schema["DEFAULT_CHARACTER_SET_NAME"],
            "default_collation_name": schema["DEFAULT_COLLATION_NAME"],
            "is_system_schema": schema_name in SYSTEM_SCHEMAS,
            "tables": {},
            "routines": [],
            "triggers": [],
        }

    for table in tables:
        schema_entry = schema_map.get(table["TABLE_SCHEMA"])
        if schema_entry is None:
            continue
        schema_entry["tables"][table["TABLE_NAME"]] = {
            "name": table["TABLE_NAME"],
            "table_type": table["TABLE_TYPE"],
            "engine": table["ENGINE"],
            "table_collation": table["TABLE_COLLATION"],
            "table_comment": table["TABLE_COMMENT"] or "",
            "columns": [],
            "indexes": defaultdict(list),
            "constraints": defaultdict(list),
        }

    for column in columns:
        schema_entry = schema_map.get(column["TABLE_SCHEMA"])
        if schema_entry is None:
            continue
        table_entry = schema_entry["tables"].get(column["TABLE_NAME"])
        if table_entry is None:
            continue
        table_entry["columns"].append(
            {
                "name": column["COLUMN_NAME"],
                "ordinal_position": column["ORDINAL_POSITION"],
                "column_type": column["COLUMN_TYPE"],
                "data_type": column["DATA_TYPE"],
                "is_nullable": column["IS_NULLABLE"] == "YES",
                "default": column["COLUMN_DEFAULT"],
                "column_key": column["COLUMN_KEY"],
                "extra": column["EXTRA"] or "",
                "comment": column["COLUMN_COMMENT"] or "",
            }
        )

    for index in statistics:
        schema_entry = schema_map.get(index["TABLE_SCHEMA"])
        if schema_entry is None:
            continue
        table_entry = schema_entry["tables"].get(index["TABLE_NAME"])
        if table_entry is None:
            continue
        table_entry["indexes"][index["INDEX_NAME"]].append(
            {"column_name": index["COLUMN_NAME"], "seq_in_index": index["SEQ_IN_INDEX"], "non_unique": bool(index["NON_UNIQUE"])}
        )

    for constraint in constraints:
        schema_entry = schema_map.get(constraint["TABLE_SCHEMA"])
        if schema_entry is None:
            continue
        table_entry = schema_entry["tables"].get(constraint["TABLE_NAME"])
        if table_entry is None:
            continue
        key = f"{constraint['CONSTRAINT_NAME']}|{constraint['CONSTRAINT_TYPE']}"
        table_entry["constraints"][key].append(
            {
                "column_name": constraint["COLUMN_NAME"],
                "referenced_table_schema": constraint["REFERENCED_TABLE_SCHEMA"],
                "referenced_table_name": constraint["REFERENCED_TABLE_NAME"],
                "referenced_column_name": constraint["REFERENCED_COLUMN_NAME"],
                "ordinal_position": constraint["ORDINAL_POSITION"],
            }
        )

    for routine in routines:
        schema_entry = schema_map.get(routine["ROUTINE_SCHEMA"])
        if schema_entry is not None:
            schema_entry["routines"].append({"name": routine["ROUTINE_NAME"], "type": routine["ROUTINE_TYPE"]})

    for trigger in triggers:
        schema_entry = schema_map.get(trigger["TRIGGER_SCHEMA"])
        if schema_entry is not None:
            schema_entry["triggers"].append({"name": trigger["TRIGGER_NAME"], "event_manipulation": trigger["EVENT_MANIPULATION"], "event_object_table": trigger["EVENT_OBJECT_TABLE"]})

    normalized_schemas = []
    business_schema_count = 0
    base_table_count = 0
    view_count = 0
    for schema_name in sorted(schema_map):
        schema_entry = schema_map[schema_name]
        tables_payload = []
        for table_name in sorted(schema_entry["tables"]):
            table_entry = schema_entry["tables"][table_name]
            table_entry["indexes"] = {name: sorted(values, key=lambda item: item["seq_in_index"]) for name, values in sorted(table_entry["indexes"].items())}
            table_entry["constraints"] = {name: sorted(values, key=lambda item: item["ordinal_position"] or 0) for name, values in sorted(table_entry["constraints"].items())}
            tables_payload.append(table_entry)
            if table_entry["table_type"] == "BASE TABLE":
                base_table_count += 1
            elif table_entry["table_type"] == "VIEW":
                view_count += 1
        schema_entry["tables"] = tables_payload
        normalized_schemas.append(schema_entry)
        if not schema_entry["is_system_schema"]:
            business_schema_count += 1

    return {
        "connection": {"name": connection["name"], "db_type": connection["db_type"], "jdbc": connection["jdbc"], "host": connection["host"], "port": connection["port"], "username": connection["username"]},
        "refreshed_at": utc_now(),
        "summary": {"business_schema_count": business_schema_count, "base_table_count": base_table_count, "view_count": view_count},
        "schemas": normalized_schemas,
    }


def detect_issues(payload: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    non_innodb: list[str] = []
    no_primary_key: list[str] = []
    unusual_schemas: list[str] = []
    for schema in payload.get("schemas", []):
        schema_name = schema["name"]
        if schema.get("is_system_schema"):
            continue
        if re.search(r"[^0-9A-Za-z_]", schema_name):
            unusual_schemas.append(schema_name)
        for table in schema.get("tables", []):
            if table["table_type"] != "BASE TABLE":
                continue
            if (table.get("engine") or "").upper() != "INNODB":
                non_innodb.append(f"{schema_name}.{table['name']}")
            has_primary_key = any(key.endswith("|PRIMARY KEY") for key in table["constraints"])
            if not has_primary_key:
                no_primary_key.append(f"{schema_name}.{table['name']}")
    if unusual_schemas:
        issues.append({"type": "unusual_schema_name", "count": len(unusual_schemas), "samples": unusual_schemas[:20]})
    if non_innodb:
        issues.append({"type": "non_innodb_table", "count": len(non_innodb), "samples": non_innodb[:20]})
    if no_primary_key:
        issues.append({"type": "table_without_primary_key", "count": len(no_primary_key), "samples": no_primary_key[:20]})
    return issues


def refresh(name: str | None) -> int:
    results = [refresh_connection(connection) for connection in select_connections(name)]
    exit_code = 0
    for result in results:
        status = "ok" if result.ok else "error"
        print(f"[{status}] {result.name}: {result.message}")
        if result.cache_path:
            print(f"  cache={result.cache_path}")
        if result.issue_count:
            print(f"  issues={result.issue_count}")
        if not result.ok:
            exit_code = 1
    rebuild_document()
    print(f"document_json={DOCUMENT_JSON_FILE}")
    print(f"document_md={DOCUMENT_MD_FILE}")
    return exit_code


def load_cache_for_connection(name: str) -> dict[str, Any] | None:
    path = cache_file(name)
    return load_json(path) if path.exists() else None


def schema_allowed(
    schema_name: str,
    focus_schemas: list[str] | None,
    focus_schema_prefixes: list[str] | None = None,
) -> bool:
    lowered = schema_name.lower()
    if lowered.startswith(EXCLUDED_SCHEMA_PREFIXES):
        return False
    exact_allowed = {item.lower() for item in (focus_schemas or [])}
    prefix_allowed = tuple(item.lower() for item in (focus_schema_prefixes or []))
    if exact_allowed or prefix_allowed:
        return lowered in exact_allowed or lowered.startswith(prefix_allowed)
    return True


def business_only_connection(
    cache: dict[str, Any],
    focus_schemas: list[str] | None = None,
    focus_schema_prefixes: list[str] | None = None,
) -> dict[str, Any]:
    schemas = [
        schema
        for schema in cache.get("schemas", [])
        if not schema.get("is_system_schema")
        and schema_allowed(schema["name"], focus_schemas, focus_schema_prefixes)
    ]
    total_tables = sum(1 for schema in schemas for table in schema.get("tables", []) if table.get("table_type") == "BASE TABLE")
    total_views = sum(1 for schema in schemas for table in schema.get("tables", []) if table.get("table_type") == "VIEW")
    payload = dict(cache)
    payload["schemas"] = schemas
    payload["summary"] = {
        "business_schema_count": len(schemas),
        "base_table_count": total_tables,
        "view_count": total_views,
    }
    payload["issues"] = detect_issues(payload)
    return payload


def render_document_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Metadata Document", "", f"- Generated At: {payload['generated_at']}", f"- Connection Count: {payload['connection_count']}", ""]
    for connection in payload.get("connections", []):
        info = connection["connection"]
        lines.extend([f"## 连接: {info['name']}", "", f"- JDBC: `{info['jdbc']}`", f"- Username: `{info['username']}`", f"- Refreshed At: `{connection['refreshed_at']}`"])
        summary = connection.get("summary", {})
        lines.append(f"- Summary: `{summary.get('business_schema_count', 0)}` schemas, `{summary.get('base_table_count', 0)}` tables, `{summary.get('view_count', 0)}` views")
        if connection.get("issues"):
            lines.append("- Issues:")
            for issue in connection["issues"]:
                lines.append(f"  - {issue['type']}: {issue['count']} ({', '.join(issue.get('samples', [])[:5])})")
        lines.append("")
        for schema in connection.get("schemas", []):
            if schema.get("is_system_schema"):
                continue
            lines.extend([f"### 库: {schema['name']}", "", f"- Charset: `{schema['default_character_set_name']}` | Collation: `{schema['default_collation_name']}`", ""])
            for table in schema.get("tables", []):
                lines.extend([f"#### 表: {table['name']} ({table['table_type']}, {table.get('engine') or 'UNKNOWN'})", ""])
                if table.get("table_comment"):
                    lines.append(f"- 表注释: {table['table_comment']}")
                lines.append("- 字段:")
                for column in table.get("columns", []):
                    lines.append(f"  - {column['name']} | {column['column_type']} | nullable={'YES' if column.get('is_nullable') else 'NO'} | default={column.get('default')} | comment={column.get('comment') or '-'}")
                lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def rebuild_document() -> dict[str, Any]:
    ensure_state()
    connections = [row for row in load_connections() if row.get("enabled", True)]
    docs = []
    for connection in connections:
        cache = load_cache_for_connection(connection["name"])
        if cache is not None:
            docs.append(
                business_only_connection(
                    cache,
                    connection.get("focus_schemas"),
                    connection.get("focus_schema_prefixes"),
                )
            )
    payload = {"generated_at": utc_now(), "connection_count": len(docs), "connections": docs}
    save_json(DOCUMENT_JSON_FILE, payload)
    DOCUMENT_MD_FILE.write_text(render_document_markdown(payload), encoding="utf-8")
    return payload


def load_document() -> dict[str, Any]:
    ensure_state()
    return load_json(DOCUMENT_JSON_FILE) if DOCUMENT_JSON_FILE.exists() else rebuild_document()


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", "", value or "").lower()


def identifier_tokens(value: str) -> set[str]:
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value or "")
    return {token for token in re.split(r"[^0-9A-Za-z\u4e00-\u9fff]+", text.lower()) if token}


def contains_term(raw_text: str, term: str) -> bool:
    if not term:
        return False
    if re.fullmatch(r"[a-z0-9_]+", term):
        return term in identifier_tokens(raw_text)
    return term in normalize_text(raw_text)


def derive_terms(query: str, domains: dict[str, Any]) -> list[str]:
    compact = normalize_text(query)
    terms: list[str] = []
    for domain_name, config in domains.items():
        candidates = [domain_name] + list(config.get("aliases", []))
        if any(normalize_text(candidate) in compact for candidate in candidates if candidate):
            terms.extend(candidates)
    if terms:
        return sorted({normalize_text(term) for term in terms if term})
    fallback = re.split(r"[\s,，、/]+", query.strip())
    stopwords = {"相关", "有关", "的", "表", "信息", "库", "字段", "数据", "一下", "哪些"}
    return sorted({normalize_text(item) for item in fallback if normalize_text(item) not in stopwords})


def score_table(table: dict[str, Any], terms: list[str]) -> tuple[int, list[str], list[dict[str, Any]]]:
    table_text = " ".join([table["name"], table.get("table_comment", ""), table.get("engine", "") or ""])
    score = 0
    reasons: list[str] = []
    matched_columns: list[dict[str, Any]] = []
    for term in terms:
        if contains_term(table_text, term):
            score += 8
            reasons.append(f"table:{term}")
    for column in table.get("columns", []):
        column_text = " ".join([column["name"], column.get("comment", "")])
        hits = [term for term in terms if contains_term(column_text, term)]
        if hits:
            score += 3 + len(hits)
            matched_columns.append(column)
            reasons.extend(f"column:{term}" for term in hits)
    unique_columns = []
    seen = set()
    for column in matched_columns:
        if column["name"] not in seen:
            unique_columns.append(column)
            seen.add(column["name"])
    return score, sorted(set(reasons)), unique_columns


def render_search(query: str, connection_name: str | None, max_tables: int) -> int:
    document = load_document()
    terms = derive_terms(query, get_domains())
    if not terms:
        print("No searchable terms found.")
        return 1
    matched_total = 0
    for connection in document.get("connections", []):
        info = connection["connection"]
        if connection_name and info["name"] != connection_name:
            continue
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for schema in connection.get("schemas", []):
            if schema.get("is_system_schema"):
                continue
            for table in schema.get("tables", []):
                score, reasons, matched_columns = score_table(table, terms)
                if score > 0:
                    grouped[schema["name"]].append({"score": score, "table": table, "reasons": reasons, "matched_columns": matched_columns})
        print(f"连接: {info['name']}")
        print(f"JDBC: {info['jdbc']}")
        print(f"关键词: {', '.join(terms)}")
        if not grouped:
            print("  未命中任何库表")
            continue
        rendered = 0
        for schema_name in sorted(grouped):
            print(f"  库: {schema_name}")
            for item in sorted(grouped[schema_name], key=lambda row: (-row['score'], row['table']['name'])):
                rendered += 1
                if rendered > max_tables:
                    break
                table = item["table"]
                print(f"    表: {table['name']} [{table['table_type']}, {table.get('engine') or 'UNKNOWN'}]")
                if table.get("table_comment"):
                    print(f"      表注释: {table['table_comment']}")
                print(f"      匹配原因: {', '.join(item['reasons'])}")
                print("      字段:")
                columns_to_show = item["matched_columns"] or table.get("columns", [])[:5]
                for column in columns_to_show[:12]:
                    print(f"        - {column['name']} | {column['column_type']} | nullable={'YES' if column.get('is_nullable') else 'NO'} | default={column.get('default')} | comment={column.get('comment') or '-'}")
            if rendered > max_tables:
                print("    ... 已达到输出上限")
                break
        matched_total += rendered
    return 0 if matched_total else 1


def main() -> int:
    ensure_state()
    args = parse_args()
    if args.command == "upsert-connection":
        action = upsert_connection(args.name, args.jdbc, args.username, args.password, args.notes)
        print(f"[{action}] {args.name}")
        return 0
    if args.command == "list-connections":
        list_connections(args.show_disabled)
        return 0
    if args.command == "refresh":
        return refresh(args.connection)
    if args.command == "rebuild-docs":
        rebuild_document()
        print(f"document_json={DOCUMENT_JSON_FILE}")
        print(f"document_md={DOCUMENT_MD_FILE}")
        return 0
    if args.command == "search":
        return render_search(args.query, args.connection, args.max_tables)
    return 1


if __name__ == "__main__":
    sys.exit(main())
