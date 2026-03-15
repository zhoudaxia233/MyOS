# CLAUDE.md — MyOS

MyOS is a governance-first personal OS for AI agents. Start from `core/ROUTER.md` for task routing.

## Commands

```bash
# Tests
poetry run pytest -q orchestrator/tests/

# Validate module contracts
poetry run python orchestrator/src/main.py validate --strict

# Web UI
./start
```

Tests must pass before committing. Fix failures before pushing.

## Architecture

- `core/` — Kernel: ROUTER, RULES, SCHEMAS, ONTOLOGY
- `orchestrator/` — Execution engine (CLI + web UI)
- `modules/` — Domain plugins, each with `module.manifest.yaml`
- `src/myos/` — Thin terminal CLI (`myos "..."`)

Routing is plugin-driven, two-hop max: ROUTER → module → data. Records are append-only JSONL; never overwrite.

## MCP Tools

Available when `myos` server is running:

| Tool | Purpose |
|------|---------|
| `myos_append_log` | Append validated record to a JSONL log |
| `myos_search` | Search retrieval index |
| `myos_validate` | Plugin contract validation |
| `myos_metrics` | Drift metrics report |
| `myos_guardrail_check` | Domain guardrail evaluation |
| `myos_build_index` | Rebuild retrieval index |

## Compact Instructions

When compressing context, preserve in priority order:

1. Architecture decisions (NEVER summarize)
2. Modified files and their key changes
3. Current verification status (pass/fail)
4. Open TODOs and rollback notes
5. Tool outputs (can delete, keep pass/fail only)
