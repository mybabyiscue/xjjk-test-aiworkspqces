# Execution Plan Contract

## Contents

- [Root object](#root-object)
- [Request object](#request-object)
- [Assertions](#assertions)
- [Flow dependencies](#flow-dependencies)
- [Example](#example)

## Root object

Use UTF-8 JSON with these required fields:

| Field | Type | Contract |
|---|---|---|
| `version` | integer | Must equal `1` |
| `testcase_hash` | string | Must equal the approved confirmation hash |
| `requests` | array | Standalone request objects |
| `flows` | array | Core flow objects |

Do not place environment domains or credentials in this file. Select the environment at runtime from `environments_config.json`.

## Request object

Each request requires:

- `id`: unique non-empty string.
- `case_ids`: non-empty string array.
- `variant_type`: `positive` or `negative`.
- `method`: HTTP method proven by source annotations.
- `path`: relative gateway path beginning with `/`.
- `headers`: non-sensitive string map.
- `authorization_header`: Header name used for runtime Token injection, or an empty string when authentication is not required.
- `query`: query parameter object.
- `body`: JSON value or `null`.
- `expected`: assertion object.

`expected` requires `http_status`, `response_assertions`, and `database_assertions`.

## Assertions

Response assertions use:

```json
{"path":"$.code","operator":"equals","value":0}
```

Supported operators are `equals`, `not_equals`, `exists`, `contains`, and `in`.

Database assertion objects require:

```json
{
  "database": "database_name",
  "table": "table_name",
  "sql": "SELECT status FROM table_name WHERE id = %s",
  "parameters": [123],
  "assertions": [
    {"path":"$[0].status","operator":"equals","value":1}
  ]
}
```

SQL must be a single parameterized `SELECT`. Do not include comments, semicolons, writes, DDL, or transaction statements. The database and table must match code-review metadata and the query evidence recorded by the preparation stage.

## Flow dependencies

A flow requires `id`, `name`, and an ordered `steps` array. Each step contains a request object plus `dependencies`:

```json
{
  "source_step": "receive_reward",
  "source_path": "$.data.id",
  "target": "body",
  "target_path": "$.rewardId"
}
```

`source_step` must refer to an earlier step. `target` must be `body` or `query`. A missing source value interrupts the flow.

## Example

```json
{
  "version": 1,
  "testcase_hash": "approved-hash",
  "requests": [
    {
      "id": "case_001_positive",
      "case_ids": ["case_001"],
      "variant_type": "positive",
      "method": "POST",
      "path": "/gateway/resource/query",
      "headers": {"Content-Type": "application/json"},
      "authorization_header": "Authorization",
      "query": {},
      "body": {"resourceId": 123},
      "expected": {
        "http_status": 200,
        "response_assertions": [{"path":"$.code","operator":"equals","value":0}],
        "database_assertions": []
      }
    }
  ],
  "flows": []
}
```
