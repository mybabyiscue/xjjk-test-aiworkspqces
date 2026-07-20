# Cache And Document Model

## Purpose

Use this skill to keep connection metadata in two layers:

1. Raw per-connection cache for each reachable MySQL connection
2. A combined internal metadata document used for later retrieval
Only business schemas are stored in this combined document. System schemas are excluded.
Schemas whose names start with `aigis`, `aj`, or `bak` are also excluded.

## Files

- `state/connections.json`: registered MySQL connections
  Each connection may also define `focus_schemas` to keep only specific business schemas in the combined document.
  Each connection may also define `focus_schema_prefixes` to keep schemas by prefix in the combined document.
- `state/cache/<connection>.json`: raw cache for one connection
- `state/documents/metadata_document.json`: combined retrieval document for business schemas only
- `state/documents/metadata_document.md`: human-readable combined document for business schemas only
- `references/business_domains.json`: business keyword aliases used during semantic lookup

## Refresh Behavior

`refresh` should:

1. Read the saved connection config
2. Connect to one or all requested connections
3. Pull schema metadata without reading business rows
4. Rewrite each connection cache file
5. Rebuild the combined internal document from the latest caches, excluding system schemas and excluded schema prefixes
6. If a connection has `focus_schemas` or `focus_schema_prefixes`, keep only matching schemas in the combined document

## Stored Structure

Each raw cache stores:

- Connection identity: name, JDBC, host, port, username
- Refresh timestamp
- Summary counts: business schema count, table count, view count
- Schemas: charset, collation, routines, triggers
- Tables: table type, engine, collation, comment
- Columns: name, type, nullable, default, key flag, extra, comment
- Indexes: index name, uniqueness, ordered columns
- Constraints: primary key, unique key, foreign key metadata
- Issues: non-InnoDB tables, tables without primary keys, unusual schema names

The combined internal document stores the same information for every reachable connection, grouped by:

- 连接
- 库
- 表
- 字段

For field-level answers, the default response should include the field description/comment, not just the field name.

System schemas such as `information_schema`, `mysql`, `performance_schema`, and `sys` must not be written into the combined document.
Schemas whose names start with `aigis`, `aj`, or `bak` must not be written into the combined document either.
If a connection defines `focus_schemas` or `focus_schema_prefixes`, every other schema for that connection must be excluded from the combined document.

## Search Strategy

When the user asks for a business area such as `订单表`, search the internal document instead of reconnecting.
Score matches using:

1. Table name
2. Table comment
3. Column name
4. Column comment

Prefer table-level matches, but keep field-level matches because many business tables are named indirectly.

## Extension Rule

To support more domains such as inventory, invoice, merchant, or shipment, add a new top-level key in `references/business_domains.json` and provide Chinese and English aliases.
