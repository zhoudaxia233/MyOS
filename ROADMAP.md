# Personal Core OS Roadmap

## Project Intent

Build a stable personal operating center for AI agents, where execution scales but judgment remains coherent, auditable, and aligned with long-term direction.

## Version Timeline

## v0.1 (Completed)

- Kernel in `core/` (routing, rules, schemas, glossary)
- Modules: `content`, `decision`, `_template`
- Append-only JSONL discipline and schema header rule
- Base docs and safe append script

## v0.2 (Completed)

- Added `profile` module (identity + preferences)
- Added `memory` module (ingest + weekly distill)
- Added decision impulse guardrails and precommit workflow
- Added `context_bundle.sh` for route + minimal file planning

## v0.3-first (Completed)

- Profile cyberization layer:
  - `psych_profile.yaml`
  - `psych_observations.jsonl`
  - `profile_snapshot.md`
- Memory paradigm layer:
  - `pattern_taxonomy.yaml`
  - `chat_patterns.jsonl`
  - `extract_chat_patterns.md`
- Decision audit layer:
  - `audit_rules.yaml`
  - `audit_decision_system.md`
  - `decision_audit_report.md` template
- Cadence runbook:
  - `routines/cadence.yaml`
  - `routines/CADENCE.md`
  - `scripts/run_cycle.sh`

## v0.3-orchestrator (Completed)

- Added dedicated `orchestrator/` subsystem as high-level execution engine
- Layered architecture in `orchestrator/src/`:
  - router, loader, planner, runner, writer, validators
  - providers: manual + optional openai
- Added orchestrator runtime logs:
  - `orchestrator/logs/runs.jsonl`
- Added CLI:
  - `inspect` for route/plan visibility
  - `run` for execution packet (manual) or provider-based generation

## v0.4-retrieval (Completed)

1. Retrieval scaling
   - Added index builder and lexical search in orchestrator CLI
   - Added retrieval config and derived index path
   - Added retrieval query logs (`orchestrator/logs/retrieval_queries.jsonl`)
   - Added retrieval-augmented run mode (`--with-retrieval`)

## v0.4-scheduling (Completed)

1. Automation scheduling
   - Added cadence loader and cycle execution command (`schedule-run`)
   - Reads `routines/cadence.yaml` as scheduling SSOT
   - Added schedule execution logs (`orchestrator/logs/schedule_runs.jsonl`)
   - Added cron hint mode for non-executing scheduling integration

## v0.5-drift (Completed)

1. Drift dashboards
   - Added quantitative metrics command (`orchestrator src/main.py metrics`)
   - Added dashboard report generation for 7/30-day windows
   - Added snapshot logs (`orchestrator/logs/metrics_snapshots.jsonl`)
   - Metrics include precommit coverage, cooldown compliance, repeat failure rate, and profile drift rate

## v0.5-next (In Progress)

1. Guardrail hardening
   - Domain-specific policies with override audit trails

## Success Signals

- Better action alignment with long-term priorities
- Lower repeated failure rate in high-risk domains
- Higher precommit coverage and cooldown compliance
- Faster owner audit with clearer exception reports
