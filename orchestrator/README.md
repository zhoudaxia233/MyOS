# Orchestrator

The orchestrator is the execution engine layer for Personal Core OS.

It reads kernel/module protocols, builds minimal context bundles, optionally retrieves relevant historical records, runs a provider, and writes outputs/logs safely.

## Design Goals

- Keep protocol/data in `core/` and `modules/`
- Keep execution logic in `orchestrator/`
- Preserve append-only integrity for JSONL logs
- Support both no-API manual mode and optional API mode
- Add scalable retrieval for long-history memory and audit logs

## Architecture

- `router.py`: map task intent to module
- `loader.py`: load two-hop context bundle (`ROUTER -> MODULE -> DATA`)
- `planner.py`: pick skill + output target
- `retrieval.py`: build/search lexical index for JSONL histories
- `scheduling.py`: load cadence routines and build cycle tasks
- `metrics.py`: compute drift dashboard metrics from logs
- `guardrails.py`: evaluate domain-specific hardening policies and override requirements
- `runner.py`: invoke provider
- `writer.py`: write outputs and append run/query/schedule/metrics/override logs
- `validators.py`: guardrails for JSONL and append-only behavior
- `providers/`: provider adapters (`manual`, `openai`)

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
  --provider manual \
  --with-retrieval \
  --retrieval-top-k 6
```

This adds top retrieval hits into the execution context bundle.

## Automation Scheduling

### Run configured cadence cycle

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py schedule-run --cycle weekly --provider manual
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

## Quick Start

### 1) Manual mode (no API)

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py run \
  --task "run weekly decision review" \
  --provider manual
```

### 2) Optional OpenAI mode

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
python3 /Users/closears/MyOS/orchestrator/src/main.py run --task "..." [--provider manual|openai] [--module <name>] [--with-retrieval]
python3 /Users/closears/MyOS/orchestrator/src/main.py schedule-run --cycle <daily|weekly|monthly> [--scheduler manual|cron] [--provider manual|openai]
python3 /Users/closears/MyOS/orchestrator/src/main.py index [--source-glob "modules/decision/logs/*.jsonl"]
python3 /Users/closears/MyOS/orchestrator/src/main.py search --query "..." [--module <name>] [--top-k 8]
python3 /Users/closears/MyOS/orchestrator/src/main.py metrics [--window 7|30] [--output <path>]
python3 /Users/closears/MyOS/orchestrator/src/main.py guardrail-check --domain <invest|project|content> [policy fields...]
```
