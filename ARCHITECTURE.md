# QueryPilot AI architecture

## User-visible flow

`question → question parsing → schema linking → read-only SQL → execution → validation → evidence-backed answer or abstention`

Each step is represented in `AnalysisRecord`, which contains the question ID, schema references, SQL, dialect, duration, row count, validation checks, repair attempts, assumptions, and warnings.

## Security boundaries

- `src/security/sql_policy.py` rejects multi-statement and mutating/admin operations.
- `src/database/safe_executor.py` only executes validated SQL and caps returned rows.
- Model prompts contain schema metadata and samples, never connection credentials.
- Query history excludes connection strings and passwords.
- The app reports sanitized database errors.

## Evaluation

Pytest provides repeatable local tests for correctness boundaries. For a larger benchmark, add JSON cases containing a question, expected tables, expected SQL semantics, expected answer, and whether abstention is required; record execution accuracy, answer accuracy, repair success, and latency percentiles.
