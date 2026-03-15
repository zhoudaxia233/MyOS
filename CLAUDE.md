# CLAUDE.md — MyOS Operating Protocol

MyOS is a governance-first personal OS for AI agents. This file is the Claude Code entry point.

## Interaction Loop

For any user task:

1. **Route** — Read `core/ROUTER.md`, match keywords to a module.
2. **Load module** — Read `modules/{module}/MODULE.md`.
3. **Select skill** — Read `modules/{module}/skills/{skill}.md`. It declares which data files to load.
4. **Execute** — Follow skill instructions, load only declared files.
5. **Write back** — Use `myos_append_log` MCP tool, or CLI fallback if MCP unavailable.

Two-hop max: ROUTER → MODULE → DATA.

## Skill Directory

| Module | Skill | Purpose |
|--------|-------|---------|
| content | `propose_content_direction` | Draft a reviewable content direction proposal |
| content | `write_after_meal_story` | Write a personal narrative story (output-only) |
| decision | `log_decision` | Log a decision through the entry gate with guardrail checks |
| decision | `precommit_check` | Pre-decision risk checklist for high-stakes action |
| decision | `guardrail_override` | Document a guardrail override with audit trail |
| decision | `weekly_review` | Review decision history, emit owner action proposals |
| decision | `audit_decision_system` | Full audit of decision system health |
| decision | `owner_report` | Consolidated owner one-pager |
| profile | `update_profile` | Update identity/preferences YAML with change log |
| profile | `alignment_check` | Check current behavior against profile baselines |
| profile | `log_trigger_event` | Log a psychological trigger event |
| profile | `log_psych_observation` | Log a pattern observation from behavior data |
| profile | `profile_snapshot` | Monthly profile snapshot |
| memory | `ingest_memory` | Ingest ad-hoc reflection events |
| memory | `ingest_learning_asset` | Convert external learning into candidates |
| memory | `import_chat_export` | Import chat export into memory events |
| memory | `extract_chat_patterns` | Extract behavioral patterns from chat history |
| memory | `distill_weekly` | Distill weekly memory into insights |
| cognition | `log_schema` | Log a new schema version (belief update) |
| cognition | `log_assimilation` | Log a successful assimilation event |
| cognition | `detect_disequilibrium` | Detect contradictions or schema tensions |
| cognition | `log_accommodation` | Log a schema revision from disequilibrium |
| cognition | `log_equilibration` | Log a completed equilibration cycle |
| cognition | `run_equilibration_review` | Full equilibration review |
| cognition | `review_timeline` | Cognitive timeline report |
| principles | `propose_amendment` | Propose a constitutional principle amendment |
| principles | `log_principle_exception` | Log a deviation from a core principle |
| principles | `run_constitutional_audit` | Audit decision system against constitutional principles |

## Governance Constraints

Hard rules — not guidelines:

1. **Hierarchy**: Principles > Decisions > Cognition > Profile > Memory.
2. **Append-only**: Never overwrite JSONL records. Archive via `status: archived`. `_schema` is always line 1.
3. **IDs**: Format `<prefix>_<YYYYMMDD>_<3-digit-seq>`. Let MCP tools or CLI generate them.
4. **Review → Promote**: Never auto-promote candidates without owner confirmation.
5. **Cross-module refs**: ID-only references (e.g. `principle_refs: pr_0001`). Never copy content.
6. **Data classification** (in order): long-horizon → `principles`; gate outcome → `decision`; schema revision → `cognition`; stable trait → `profile`; otherwise → `memory`.

## After Code Changes

After modifying any code file:

1. Run `poetry run pytest -q orchestrator/tests/` — all tests must pass.
2. Run `poetry run python orchestrator/src/main.py validate --strict` — must pass.
3. If both pass: commit all changes with a clear English commit message, then push to remote.
4. If tests fail: fix the issue before committing.

## MCP Tools

Available when `myos` server is running:

| Tool | Purpose |
|------|---------|
| `myos_append_log` | Append validated record to a JSONL log (auto ID + timestamp) |
| `myos_search` | Search retrieval index |
| `myos_validate` | Plugin contract validation |
| `myos_metrics` | Drift metrics report |
| `myos_guardrail_check` | Domain guardrail evaluation |
| `myos_build_index` | Rebuild retrieval index |

## CLI Fallback

```bash
python3 orchestrator/src/main.py log-decision --domain <name> --decision "..." --option "A" --option "B" --confidence <1-10>
python3 orchestrator/src/main.py metrics --window [7|30]
python3 orchestrator/src/main.py validate --strict
python3 orchestrator/src/main.py index
python3 orchestrator/src/main.py search --query "..."
```
