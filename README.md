# QueryPilot AI — The Self-Validating AI Data Analyst

QueryPilot is a local-first Streamlit application for asking business questions in plain English and receiving evidence-backed answers. It explores a SQL schema, creates a read-only query, executes it, validates the returned data, and explicitly abstains when the connected database cannot support the question.

The bundled demo uses clearly labelled synthetic data with schools, districts, academic years, enrolment, customers, products, orders, and order items. It intentionally includes missing placeholders, a malformed date, numeric text, and duplicate-like records.

## Quick start (Windows PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/create_demo_db.py
streamlit run app.py
```

Open the URL printed by Streamlit, normally `http://localhost:8501`.

## Demo workflow (about three minutes)

1. Open **Home** and confirm the connected `data/demo.db` status and live profiler metrics.
2. Open **Analyst** and run: `Which schools had falling enrolment between the last two complete academic years, and which districts had the largest percentage decline?`
3. Expand **SQL used**, inspect the CTE and the result table, then open **Validation report**. The result is calculated from the database; no result is hardcoded in the UI.
4. Ask `Which fields contain missing values in customers?` to show dirty-data profiling.
5. Ask `Can you tell me about student attendance?` to demonstrate explicit abstention because there is no attendance table.
6. Open **Database explorer** and **Query history** to show schema evidence and saved analysis records.

## Model configuration

The default **Offline deterministic demo planner** is reproducible and works without a model download. It is not presented as generated AI output. To use an open-weight model, install Ollama, download an eligible model of no more than 8B parameters, and run it locally:

```powershell
ollama pull qwen2.5:7b
$env:QUERYPILOT_MODEL_NAME = "qwen2.5:7b"
$env:QUERYPILOT_MODEL_URL = "http://localhost:11434"
streamlit run app.py
```

Turn off the planner toggle in **AI Analyst** to use Ollama. If inference is unavailable, QueryPilot displays a clear error/abstention instead of fabricating an answer. The adapter validates structured JSON with Pydantic and never receives database credentials.

## Connections

SQLite is supported immediately: `sqlite:///data/demo.db` or `sqlite:///C:/absolute/path/file.db`. Optional SQLAlchemy URLs:

- PostgreSQL: `postgresql+psycopg2://user:password@host:5432/database`
- MySQL: `mysql+pymysql://user:password@host:3306/database`

Use read-only database credentials. Connection strings are masked in the status display and are not written to query history.

## Checks

```powershell
pytest -q
```

The test suite covers SQL safety, schema linking, dirty-data detection, arithmetic validation, abstention, and the full demo workflow. The benchmark page deliberately reports no fabricated BIRD score; generate measurements from your own evaluation set.

## Architecture

```text
Streamlit UI
   │
   ├── Connection + introspection ── SQLAlchemy ── SQLite/Postgres/MySQL
   │       └── schema metadata, samples, nulls, unique counts, relationships
   │
   └── QueryPilot Orchestrator
       ├── question parser / schema linker
       ├── open-weight adapter (Ollama, optional)
       ├── SQL generator + read-only policy
       ├── safe executor with row limits
       ├── result validator + conservative repair loop (max 3)
       └── answer + Plotly evidence + JSON query history
```

## Limitations and next improvements

- The deterministic planner intentionally supports a focused set of common intents; broader language coverage needs an available model or additional intent templates.
- Query timeout enforcement is delegated to the driver/database and should be hardened with dialect-specific read-only roles and statement timeouts in production.
- Relationship detection currently uses declared foreign keys; inferred relationships and semantic business rules should be expanded.
- Benchmark reporting provides the test harness foundation, not an official BIRD score.
- Production deployments should use an encrypted server-side history store, audit logging, stronger tenant isolation, and database-native row-level security.
