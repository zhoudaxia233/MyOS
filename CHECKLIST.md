# Personal Core OS Acceptance Checklist

Use this checklist before merging changes.

## Kernel and Routing

- [ ] `core/ROUTER.md` defines two-hop loading: `ROUTER -> MODULE -> DATA`
- [ ] Routing table covers `content`, `decision`, `profile`, and `memory`
- [ ] `core/RULES.md` includes no-fabrication and append-only integrity rules
- [ ] `core/SCHEMAS.md` defines ID and timestamp conventions

## Progressive Disclosure

- [ ] Agent flow starts from `core/ROUTER.md`
- [ ] Task loading stays inside one target module unless explicitly requested
- [ ] Only task-required files are loaded
- [ ] Unrelated module files are not preloaded

## SSOT and Coupling

- [ ] Canonical domain knowledge lives in `modules/*/data/`
- [ ] Skills reference SSOT paths instead of duplicating canonical content
- [ ] Cross-module references use IDs only

## Logs and Integrity

- [ ] Every `*.jsonl` starts with `_schema` on line 1
- [ ] Existing historical records were not deleted
- [ ] New records are appended as new lines only
- [ ] Deactivation uses `"status": "archived"`

## Module Quality

- [ ] Every module has `MODULE.md` with purpose, inventory, workflows, and `<instructions>`
- [ ] `modules/decision/` includes precommit + weekly review + audit workflow
- [ ] `modules/profile/` includes psych profile and snapshot workflow
- [ ] `modules/memory/` includes chat pattern extraction workflow
- [ ] `modules/_template/` remains usable as starter scaffold

## Cadence and Operations

- [ ] `routines/cadence.yaml` and `routines/CADENCE.md` are consistent
- [ ] `scripts/run_cycle.sh` reflects daily/weekly/monthly routines
- [ ] `scripts/context_bundle.sh` includes new v0.3-first routes

## Orchestrator Layer

- [ ] `orchestrator/` exists as a separate execution subsystem
- [ ] `orchestrator/src/main.py inspect` prints route + file plan
- [ ] `orchestrator/src/main.py run --provider manual` writes execution output
- [ ] `orchestrator/logs/runs.jsonl` preserves `_schema` header and append-only records

## Retrieval Layer

- [ ] `orchestrator/src/main.py index` builds retrieval index successfully
- [ ] `orchestrator/src/main.py search --query \"...\"` returns expected matches
- [ ] `orchestrator/config/retrieval.json` source globs match intended logs
- [ ] `orchestrator/logs/retrieval_queries.jsonl` preserves `_schema` header and append-only records

## Operational Readiness

- [ ] `scripts/append_jsonl.sh` is executable
- [ ] `scripts/context_bundle.sh` is executable
- [ ] `scripts/run_cycle.sh` is executable
- [ ] Outputs are written under `modules/*/outputs/`
