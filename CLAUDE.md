# CLAUDE.md — MyOS Repo Maintenance

MyOS is a governance-first personal OS for AI agents. For MyOS tasks, start from `core/ROUTER.md`.

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

## Compact Instructions

When compressing context, preserve in priority order:

1. Architecture decisions (NEVER summarize)
2. Modified files and their key changes
3. Current verification status (pass/fail)
4. Open TODOs and rollback notes
5. Tool outputs (can delete, keep pass/fail only)

## CLI Fallback

```bash
python3 orchestrator/src/main.py log-decision --domain <name> --decision "..." --option "A" --option "B" --confidence <1-10>
python3 orchestrator/src/main.py metrics --window [7|30]
python3 orchestrator/src/main.py validate --strict
python3 orchestrator/src/main.py index
python3 orchestrator/src/main.py search --query "..."
```
