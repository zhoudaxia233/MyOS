# Orchestrator

The orchestrator is the execution engine layer for Personal Core OS.

It reads kernel/module protocols, builds minimal context bundles, optionally retrieves relevant historical records, runs a provider, and writes outputs/logs safely.

## Design Goals

- Keep protocol/data in `core/` and `modules/`
- Keep execution logic in `orchestrator/`
- Preserve append-only integrity for JSONL logs
- Support no-API dry-run/handoff modes and optional API mode
- Add scalable retrieval for long-history memory and audit logs

## Architecture

- `router.py`: map task intent to module
- `loader.py`: load minimal context bundle from selected skill required files
- `planner.py`: pick skill + output target
- `retrieval.py`: build/search lexical index for JSONL histories
- `scheduling.py`: load cadence routines and build cycle tasks
- `metrics.py`: compute drift dashboard metrics from logs
- `guardrails.py`: evaluate domain-specific hardening policies and override requirements
- `owner_report.py`: build one-page owner report from metrics + exceptions + artifacts
- `webapp.py`: local web control center API + static UI serving
- `runner.py`: invoke provider
- `writer.py`: write outputs and append run/query/schedule/metrics/override/owner logs
- `validators.py`: guardrails for JSONL and append-only behavior
- `providers/`: provider adapters (`dry-run`, `handoff`, `openai`)

Routing rules are discovered from each module's `module.manifest.yaml`, so adding module keywords does not require router code changes.
`orchestrator/config/routes.json` remains as legacy fallback.

## Retrieval Scaling

### Index build

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py index
```

Builds derived index file at `orchestrator/retrieval/index.json` from configured JSONL sources.

### Search

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py search --query "cooldown compliance trend" --module decision --top-k 8
```

Search records are logged in `orchestrator/logs/retrieval_queries.jsonl`.

### Run with retrieval

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py run \
  --task "run weekly decision review" \
  --provider dry-run \
  --with-retrieval \
  --retrieval-top-k 6
```

This adds top retrieval hits into the execution context bundle.

## Automation Scheduling

### Run configured cadence cycle

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py schedule-run --cycle weekly --provider dry-run
```

Uses `routines/cadence.yaml` as SSOT and executes each routine item in order.

Schedule execution records are logged in `orchestrator/logs/schedule_runs.jsonl`.

### Cron hint mode

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py schedule-run --cycle weekly --scheduler cron
```

Prints cycle-level cron hint without executing tasks.

## Drift Dashboard

Generate quantitative drift metrics report:

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py metrics --window 7
```

Custom output path:

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py metrics --window 30 --output modules/decision/outputs/metrics_30d.md
```

Metrics snapshot records are logged in `orchestrator/logs/metrics_snapshots.jsonl`.

## Guardrail Hardening

Run domain policy check:

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py guardrail-check \
  --domain invest \
  --decision-ref dc_20260303_001 \
  --guardrail-check-id pc_20260303_001 \
  --downside "Could violate weekly risk budget" \
  --invalidation-condition "Price closes above invalidation level" \
  --max-loss "0.5R" \
  --disconfirming-signal "Falling volume confirmation"
```

Override example:

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py guardrail-check \
  --domain invest \
  --decision-ref dc_20260303_001 \
  --downside "Could violate weekly risk budget" \
  --invalidation-condition "Price closes above invalidation level" \
  --max-loss "0.5R" \
  --disconfirming-signal "Falling volume confirmation" \
  --emotional-weight 8 \
  --override-requested \
  --override-reason "Time-sensitive hedge" \
  --owner-confirmation "approved"
```

Accepted overrides are logged to `modules/decision/logs/guardrail_overrides.jsonl`.

Log decision with enforced gate:

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py log-decision \
  --domain invest \
  --decision "Open bounded-risk momentum position" \
  --option "skip" \
  --option "open small" \
  --confidence 8 \
  --guardrail-check-id pc_20260304_001 \
  --downside "Could lose up to 0.5R" \
  --invalidation-condition "Close below invalidation level" \
  --max-loss "0.5R" \
  --disconfirming-signal "Volume collapse on breakout"
```

Each call appends one record to `modules/decision/logs/decision_gate_checks.jsonl`.  
If gate status is `blocked`, no decision record is appended.

## Owner One-Pager

Generate owner report manually:

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py owner-report --window 7
```

Weekly cadence integration:

- `schedule-run --cycle weekly` automatically appends an owner report run unless `--no-owner-report` is set.
- Use `--owner-window` to control the report window.

Owner report records are logged in `orchestrator/logs/owner_reports.jsonl`.

## Quick Start

### 0) Start V1 Web UI (recommended)

```bash
./start
```

This launcher auto-uses Poetry virtualenv when Poetry is installed.

Alternative:

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py web --open-browser
```

This opens a local chat-style control center where you can:

- inspect route + context load plan
- run tasks with dry-run/handoff/openai provider
- open `⚙` Settings popup to configure API key, routing model, and task model
- when Module = Auto route and API key is configured, routing is selected by the routing model
- if model routing fails, it automatically falls back to manifest/keyword routing
- handoff output panel includes token usage for copy block (`tiktoken` exact if installed, else estimated)
- trigger validate, metrics, owner-report, and weekly cycle actions
- audit route reason, matched keywords, loaded files, and output hash

API key handling:

- Settings API never returns raw API key values.
- Key is stored locally in `orchestrator/config/settings.json` (gitignored).

If you prefer direct server launch:

```bash
python3 /Users/closears/MyOS/orchestrator/src/webapp.py --open-browser
```

### 1) Debug mode (dry-run, no API)

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py run \
  --task "run weekly decision review" \
  --provider dry-run
```

`run` prints:

- route module
- route reason + matched keywords
- selected skill
- exact files loaded into context

### 2) Handoff mode (no API, copy-paste block)

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py run \
  --task "run weekly decision review" \
  --provider handoff
```

This writes a ready-to-copy model handoff block with task + selected context payload.

### 3) Optional OpenAI mode

Set env vars:

- `OPENAI_API_KEY`
- `OPENAI_MODEL` (optional, defaults from config)

Run:

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py run \
  --task "run weekly decision review" \
  --provider openai
```

## CLI

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py inspect --task "..." [--module <name>] [--with-retrieval]
python3 /Users/closears/MyOS/orchestrator/src/main.py run --task "..." [--provider dry-run|handoff|openai] [--module <name>] [--with-retrieval]
python3 /Users/closears/MyOS/orchestrator/src/main.py schedule-run --cycle <daily|weekly|monthly> [--scheduler manual|cron] [--provider dry-run|handoff|openai]
python3 /Users/closears/MyOS/orchestrator/src/main.py ingest-chat --input <chat_export.json|jsonl|md|txt> [--max-events 50] [--tag <tag>] [--dry-run]
python3 /Users/closears/MyOS/orchestrator/src/main.py index [--source-glob "modules/decision/logs/*.jsonl"]
python3 /Users/closears/MyOS/orchestrator/src/main.py search --query "..." [--module <name>] [--top-k 8]
python3 /Users/closears/MyOS/orchestrator/src/main.py metrics [--window 7|30] [--output <path>]
python3 /Users/closears/MyOS/orchestrator/src/main.py guardrail-check --domain <invest|project|content> [policy fields...]
python3 /Users/closears/MyOS/orchestrator/src/main.py log-decision --domain <name> --decision "..." --option <value> --confidence <1-10> [gate fields...]
python3 /Users/closears/MyOS/orchestrator/src/main.py owner-report [--window 7|30] [--output <path>]
python3 /Users/closears/MyOS/orchestrator/src/main.py validate [--strict]
python3 /Users/closears/MyOS/orchestrator/src/main.py web [--host 127.0.0.1] [--port 8765] [--open-browser]
```

## Contract Validation

Run validation before execution and in CI:

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py validate --strict
```

It checks:

- module contract structure (`MODULE.md`, `data/`, `logs/`, `skills/`, `outputs/`)
- module manifest presence and parseability (`module.manifest.yaml`)
- skill file references resolve to existing files
- skill references stay in-module (or `core/`)
- JSONL schema header integrity on line 1
- JSONL record-level integrity:
  - `id` format (`<prefix>_<YYYYMMDD>_<3-digit-seq>`)
  - `created_at` / `updated_at` ISO8601 UTC `Z`
  - `status` in `active|archived`
  - `source_refs` format and resolvability
- optional legacy route config module references in `orchestrator/config/routes.json`
- cadence module/skill references in `routines/cadence.yaml`

## Output Naming

- Planner-generated outputs use UTC timestamp suffixes (`YYYYMMDD_HHMMSS`) to avoid same-day overwrite.
- `metrics` and `owner-report` default outputs also use UTC timestamp suffixes.

## Test Coverage

- Unit tests cover router/planner/guardrails/metrics/owner-report/writer/validator flows.
- Integration tests cover command chain execution:
  - `validate --strict`
  - `inspect`
  - `run --provider dry-run`
  - `ingest-chat`
  - `log-decision`
  - `metrics`
  - `owner-report`
  - `schedule-run`

## Runtime Audit Log

Each `run` appends a record to `orchestrator/logs/runs.jsonl` including:

- `route_reason`
- `matched_keywords`
- `loaded_files`
- `skill`
- `output_hash` (SHA-256 of generated output content)
