"""Execute a validated read-only query plan and render real-data records."""

from __future__ import annotations

import argparse
import json
import logging
import time
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pymysql
from pymysql.connections import Connection
from pymysql.cursors import DictCursor


JsonObject = dict[str, object]


class QueryPlanError(RuntimeError):
    """Raised when a query plan or connection configuration is invalid."""


def parse_arguments() -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Execute a read-only database query plan.")
    parser.add_argument("--connections", required=True)
    parser.add_argument("--connection-name", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--manifest", required=True)
    return parser.parse_args()


def read_json_object(path: Path) -> JsonObject:
    value: object = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise QueryPlanError(f"JSON root must be an object: {path}")
    return value


def require_string(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise QueryPlanError(f"{field_name} must be a non-empty string")
    return value.strip()


def require_list(value: object, field_name: str) -> list[object]:
    if not isinstance(value, list):
        raise QueryPlanError(f"{field_name} must be an array")
    return value


def select_connection(payload: JsonObject, name: str) -> JsonObject:
    rows: list[object] = require_list(payload.get("connections"), "connections")
    for row in rows:
        if isinstance(row, dict) and row.get("name") == name and row.get("enabled", True) is True:
            return row
    raise QueryPlanError(f"Enabled connection not found: {name}")


def connect_with_retry(config: JsonObject, attempts: int) -> Connection:
    last_error: pymysql.MySQLError | None = None
    for attempt in range(1, attempts + 1):
        try:
            return pymysql.connect(
                host=require_string(config.get("host"), "connection.host"),
                port=int(config.get("port")),
                user=require_string(config.get("username"), "connection.username"),
                password=require_string(config.get("password"), "connection.password"),
                charset="utf8mb4",
                autocommit=True,
                cursorclass=DictCursor,
                connect_timeout=5,
                read_timeout=60,
                write_timeout=60,
                ssl_disabled=True,
            )
        except pymysql.MySQLError as error:
            last_error = error
            logging.warning(json.dumps({"event": "db_connect_retry", "attempt": attempt, "connection": config.get("name")}, ensure_ascii=False))
            if attempt < attempts:
                time.sleep(1)
    if last_error is None:
        raise QueryPlanError("Database connection failed without an error")
    raise last_error


def validate_select(sql: str) -> None:
    normalized: str = sql.strip().lower()
    if not normalized.startswith("select "):
        raise QueryPlanError("Only SELECT statements are allowed")
    forbidden: tuple[str, ...] = (" insert ", " update ", " delete ", " drop ", " alter ", " truncate ", " replace ", ";")
    padded: str = f" {normalized} "
    if any(token in padded for token in forbidden):
        raise QueryPlanError("Query contains a forbidden statement token")


def execute_query(connection: Connection, sql: str, attempts: int, query_reference: str) -> list[JsonObject]:
    last_error: pymysql.MySQLError | None = None
    for attempt in range(1, attempts + 1):
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                return list(cursor.fetchall())
        except pymysql.MySQLError as error:
            last_error = error
            logging.warning(json.dumps({"event": "db_query_retry", "attempt": attempt, "query_reference": query_reference}, ensure_ascii=False))
            if attempt < attempts:
                time.sleep(1)
    if last_error is None:
        raise QueryPlanError(f"Query failed without an error: {query_reference}")
    raise last_error


def serialize_value(value: object) -> object:
    if isinstance(value, (datetime, date)):
        return value.isoformat(sep=" ") if isinstance(value, datetime) else value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, bytes):
        return value.hex()
    return value


def serialize_row(row: JsonObject) -> JsonObject:
    return {key: serialize_value(value) for key, value in row.items()}


def build_records(connection: Connection, connection_name: str, plan: JsonObject) -> list[JsonObject]:
    records: list[JsonObject] = []
    executed_at: str = datetime.now().astimezone().isoformat()
    for index, raw_query in enumerate(require_list(plan.get("queries"), "queries"), start=1):
        if not isinstance(raw_query, dict):
            raise QueryPlanError(f"queries[{index}] must be an object")
        query_reference: str = require_string(raw_query.get("query_reference"), f"queries[{index}].query_reference")
        database: str = require_string(raw_query.get("database"), f"queries[{index}].database")
        table: str = require_string(raw_query.get("table"), f"queries[{index}].table")
        purpose: str = require_string(raw_query.get("purpose"), f"queries[{index}].purpose")
        sql: str = require_string(raw_query.get("sql"), f"queries[{index}].sql")
        validate_select(sql)
        rows: list[JsonObject] = [serialize_row(row) for row in execute_query(connection, sql, 3, query_reference)]
        fields: list[str] = sorted({key for row in rows for key in row})
        records.append(
            {
                "query_reference": query_reference,
                "connection": connection_name,
                "database": database,
                "table": table,
                "executed_at": executed_at,
                "purpose": purpose,
                "fields": fields,
                "filters": {"sql": sql},
                "row_count": len(rows),
                "records": rows,
            }
        )
    return records


def write_outputs(records: list[JsonObject], output_path: Path, manifest_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({"real_data_records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    lines: list[str] = ["# 测试数据台账清单", "", "## 数据台账明细", ""]
    for record in records:
        database: str = str(record["database"])
        table: str = str(record["table"])
        rows: object = record["records"]
        if isinstance(rows, list):
            for row in rows:
                lines.append(f"{database}:{table}:【{json.dumps(row, ensure_ascii=False, separators=(',', ':'))}】")
    if len(lines) == 4:
        lines.append("无可用真实数据。")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    arguments: argparse.Namespace = parse_arguments()
    connections: JsonObject = read_json_object(Path(arguments.connections))
    plan: JsonObject = read_json_object(Path(arguments.plan))
    config: JsonObject = select_connection(connections, arguments.connection_name)
    connection: Connection = connect_with_retry(config, 3)
    try:
        records: list[JsonObject] = build_records(connection, arguments.connection_name, plan)
    finally:
        connection.close()
    write_outputs(records, Path(arguments.output), Path(arguments.manifest))
    print(json.dumps({"query_count": len(records), "row_count": sum(int(item["row_count"]) for item in records)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

