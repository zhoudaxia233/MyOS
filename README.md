# Personal Core OS

Personal Core OS is a file-based operating system for human + AI collaboration.

It is designed as a durable control plane:

- Agents execute workflows
- The system preserves identity, memory, and decision discipline
- The owner audits exceptions and approves strategic changes

## North Star

Separate execution from judgment while keeping them aligned over time.

- Execution: content work, project throughput, daily memory capture
- Judgment: decisions, guardrails, profile alignment, drift control

## Core Architecture

1. Small stable kernel in `core/`
2. Pluggable modules in `modules/`
3. Progressive disclosure: `ROUTER -> MODULE -> DATA`
4. SSOT in canonical YAML/MD files
5. Append-only JSONL logs for historical integrity
6. Route rules are plugin-driven from `modules/<name>/module.manifest.yaml`

## Repository Structure

```text
/
  README.md
  README-zh.md
  ROADMAP.md
  CHECKLIST.md
  core/
    ROUTER.md
    RULES.md
    SCHEMAS.md
    GLOSSARY.md
  modules/
    content/
      module.manifest.yaml
    decision/
      module.manifest.yaml
    profile/
      module.manifest.yaml
    memory/
      module.manifest.yaml
    _template/
      module.manifest.yaml
  routines/
    cadence.yaml
    CADENCE.md
  orchestrator/
    README.md
    config/
      routes.json
      runtime.yaml
      providers.yaml
      retrieval.json
    web/
    retrieval/
    src/
    logs/
  scripts/
    append_jsonl.sh
    context_bundle.sh
    run_cycle.sh
```

## Modules

### `modules/content`

- Role: content pipeline from idea to publication log
- SSOT: voice, anti-patterns, templates
- Logs: ideas and posts

### `modules/decision`

- Role: decision memory + risk governance + audit outputs
- SSOT: heuristics, impulse guardrails, audit rules
- Logs: decisions, failures, experiences, precommit checks
- Owner-facing output: decision audit report

### `modules/profile`

- Role: personal identity, operating preferences, psych stabilizers
- SSOT: identity, operating preferences, psych profile
- Logs: profile changes, trigger events, psych observations

### `modules/memory`

- Role: daily memory ingestion + pattern extraction + weekly distillation
- SSOT: memory policy, pattern taxonomy
- Logs: memory events, memory insights, chat paradigms

## Runtime Model

This repository is executed by an agent runtime (not by a monolithic app server):

1. Load `core/ROUTER.md`
2. Determine target module
3. Load `modules/<name>/MODULE.md`
4. Load only task-required files
5. Produce output and/or append one log line per record

Routing is automatic and auditable:

- `inspect` and `run` print route reason, matched keywords, selected skill, and loaded files.
- Route keyword rules are editable in each module manifest (`modules/<name>/module.manifest.yaml`) with no kernel rewrite required.

Execution engines can be:

- Human-triggered agent runs (chat-driven)
- `orchestrator/` CLI (dry-run/handoff or API provider mode)

## Fast Usage

### 0) Start the V1 Web UI (recommended)

```bash
./start
```

This is the shortest startup command. It uses Poetry virtualenv automatically when Poetry is available.

Alternative:

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py web --open-browser
```

You get a local chat-like control center with:

- task inspect/run
- route + loaded-files audit trace
- `⚙` settings popup for API key, routing model (lighter), and task model (main)
- with Module = Auto route, configured API key triggers model-based module selection
- route selection auto-falls back to manifest/keyword routing if model routing fails
- in `handoff` mode, Output Preview shows token usage for the copy block (`tiktoken` exact when available, otherwise estimate)
- quick actions: validate, metrics, owner report, weekly cycle, retrieval index

### 1) Get a route and minimal context bundle

```bash
scripts/context_bundle.sh --task "extract chat paradigms from this week"
```

### 2) Run daily/weekly/monthly cycle checklist

```bash
scripts/run_cycle.sh daily
scripts/run_cycle.sh weekly
scripts/run_cycle.sh monthly
```

### 3) Run orchestrator (high-level execution engine)

Validate plugin contract first:

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py validate --strict
```

This checks module structure, skill references, JSONL schema headers and record-level integrity (`id` / timestamp / `status` / `source_refs`), routes config, and cadence references before execution.

Inspect route + plan:

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py inspect --task "run weekly decision review"
```

The output includes:

- Route module
- Route reason (`manifest_keyword_match` / `routes_keyword_match` / `forced_module` / `fallback_default`)
- Matched keywords
- Exact files loaded into context

Run with no API (debug dry-run packet generation):

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py run --task "run weekly decision review" --provider dry-run
```

Run with no API (copy-paste handoff block for external model):

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py run --task "run weekly decision review" --provider handoff
```

Optional API mode:

```bash
OPENAI_API_KEY=... python3 /Users/closears/MyOS/orchestrator/src/main.py run --task "run weekly decision review" --provider openai
```

Settings note:

- UI/API never returns raw API key values.
- API key is stored locally in `orchestrator/config/settings.json` (gitignored).

### 4) Automation scheduling (cadence execution)

Run a full cadence cycle from `routines/cadence.yaml`:

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py schedule-run --cycle weekly --provider dry-run
```

Cron hint mode (no execution):

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py schedule-run --cycle weekly --scheduler cron
```

### 5) Drift dashboard (quantified trend view)

Generate 7-day dashboard:

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py metrics --window 7
```

Generate 30-day dashboard:

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py metrics --window 30
```

### 6) Owner one-pager (single audit view)

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py owner-report --window 7
```

Weekly cycle auto-includes owner report unless `--no-owner-report` is set.

### 7) Guardrail hardening (domain policy + override trail)

Run domain guardrail check:

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py guardrail-check --domain invest --decision-ref dc_20260303_001 --guardrail-check-id pc_20260303_001 --downside "Could violate weekly risk budget" --invalidation-condition "Price closes above invalidation level" --max-loss "0.5R" --disconfirming-signal "Falling volume confirmation"
```

If override is required and approved, use override flags to create audit trail entries in `modules/decision/logs/guardrail_overrides.jsonl`.

### 8) Retrieval scaling (long-history lookup)

Build index:

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py index
```

Search:

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py search --query "momentum" --top-k 5
```

Run with retrieval context:

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py run --task "run weekly decision review" --provider dry-run --with-retrieval --retrieval-top-k 6
```

### 9) High-risk decision flow

1. Run precommit check (`modules/decision/skills/precommit_check.md`)
2. Log decision with `guardrail_check_id`
3. Include in weekly review and audit report

### 10) Pattern extraction flow

1. Import chat export into memory events:
   - `python3 /Users/closears/MyOS/orchestrator/src/main.py ingest-chat --input <chat_export.json|jsonl|md|txt> --max-events 50`
2. Ingest extra reflection events (`ingest_memory.md`) when needed
3. Extract paradigms (`extract_chat_patterns.md`)
4. Distill weekly memory (`distill_weekly.md`)

### 11) Profile adaptation flow

1. Log trigger events and psych observations
2. Run monthly profile snapshot
3. Update profile YAML baselines with append-only change log

## Testing

Run orchestrator test suite:

```bash
poetry run pytest -q /Users/closears/MyOS/orchestrator/tests
```

Includes integration chain coverage for `validate`, `inspect`, `run`, `metrics`, `owner-report`, and `schedule-run`.

## Data Integrity

- Never overwrite JSONL logs; append only
- Preserve `_schema` header on line 1
- Archive by `"status": "archived"`
- Cross-module references are ID-only
- Orchestrator output files use UTC timestamp suffixes (`YYYYMMDD_HHMMSS`) to avoid same-day overwrite
- Runtime run logs include route/load audit fields (`route_reason`, `matched_keywords`, `loaded_files`, `skill`, `output_hash`)

## Current Version

- v0.1: Kernel + content + decision base
- v0.2: Profile + memory modules + guardrails
- v0.3-first: Chat paradigm extraction, psych profiling, audit-first decision view, cadence runbook
- v0.3-orchestrator: Added `orchestrator/` execution engine abstraction (dry-run + optional OpenAI provider)
- v0.4-retrieval: Added optional retrieval index + search + retrieval-augmented runs
- v0.4-scheduling: Added cadence-driven `schedule-run` with schedule execution logs
- v0.5-drift: Added drift dashboard metrics command and snapshot logging
- v0.5-guardrails: Added domain guardrail hardening and override audit trail
- v0.6-owner-report: Added consolidated owner one-pager and weekly auto-generation
- v0.6-next: Added manifest-driven routing (`module.manifest.yaml`), skill-driven minimal context loading, and explicit route audit output in `inspect`/`run`
- v0.6-next: Added plugin contract validator command (`validate`) and CI validation gate
- v0.6-next: Added integration tests for end-to-end command chain reliability
- v1-ui: Added local web control center (`orchestrator/src/main.py web`) with chat-style task entry and execution trace visibility
