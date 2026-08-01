# Execution Plan Contract

This file is generated only by `tapd-prepare-test-from/scripts/build_api_execution_plan.py`. The execution skill validates and consumes it without regenerating or repairing it.

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
| `version` | integer | Must equal `2`; version 1 plans must be regenerated |
| `ready` | boolean | Must strictly equal `true`; blocked or partial plans cannot execute |
| `source` | object | Immutable preparation source identity described below |
| `data_setup` | array | Ordered real HTTP or controlled SQL creation actions |
| `data_cleanup` | array | Reverse-ordered cleanup actions, one for every setup entry |
| `requests` | array | Standalone request objects |
| `flows` | array | Core flow objects |

`source` requires:

- `preparation_assessment_sha256`: SHA-256 of the exact `preparation_assessment.json` bytes used to generate the plan.
- `testcase_hash`: must equal the assessment and approved confirmation hashes.
- `code_review_run_id`: must equal the assessment and approved confirmation review run IDs.

At execution time, rebuild the canonical plan from the current assessment with the bundled preparation builder and compare the complete JSON object. Any difference in data setup/cleanup, method, path, headers, query, body, assertions, database assertions, flow order, or dependencies must stop execution.

Do not place environment domains or credentials in this file. Select the environment at runtime from `environments_config.json`.

## Data lifecycle actions

`data_setup` accepts only evidence-backed `http` and `sql_insert` actions. `data_cleanup` accepts only `http` and `sql_delete` actions. Mock, Fake, Stub, Mock seed, arbitrary update, DDL and unbounded cleanup actions are invalid.

HTTP actions contain `id`, `entry_id`, `type`, `evidence_reference`, `method`, `path`, `headers`, `authorization_header`, `query`, `body`, machine assertions in `expected`, and a non-sensitive `manifest` record.

SQL actions additionally contain `database`, `table`, `sql`, `parameters` and `expected_affected_rows`. An insert is one parameterized `INSERT` with explicit columns. A cleanup is one parameterized `DELETE` with a single exact or prefix `TEST_` identity. SQL actions require a separately user-confirmed connection with `access_mode=controlled-write`, the same `environment_name`, and matching database/table allowlists.

The environment must explicitly set `environment_type: test` and `allow_test_data_mutation: true`. Cleanup runs in reverse order in `finally`, including after assertion failure, setup failure or Token failure. A cleanup failure records the fixture as residual and makes execution fail. A SQL cleanup that affects zero rows is successful because the tested delete behavior may already have removed the isolated target; affecting more rows than the evidence-backed limit fails and rolls back.

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
  "version": 2,
  "ready": true,
  "source": {
    "preparation_assessment_sha256": "64-character-sha256",
    "testcase_hash": "approved-hash",
    "code_review_run_id": "review-20260801"
  },
  "data_setup": [],
  "data_cleanup": [],
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
