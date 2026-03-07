# Skill: Log Decision

## Purpose

Append a new decision record to `modules/decision/logs/decisions.jsonl` with minimal friction.

## Ask Minimal Questions (Only If Missing)

Required minimum fields to ask for:

- `domain` (`invest` / `project` / `content` / `life`)
- `decision` (what was decided)
- `options` (considered alternatives)
- `confidence` (1-10)

Optional but useful:

- `reasoning`
- `risks`
- `expected_outcome`
- `time_horizon`
- `follow_up_date` (ISO date)
- `guardrail_check_id` (from `precommit_checks.jsonl`, recommended for high-risk decisions)
- `principle_refs` (one or more constitutional clause refs like `pr_0001` for precommit-required domains)
- `exception_ref` (active principle exception record ID, if decision is time-boxed deviation)

## Procedure

1. Read `core/SCHEMAS.md` for ID/timestamp conventions if needed.
2. Read the schema header line in `modules/decision/logs/decisions.jsonl`.
3. Evaluate high-risk gate first:
   - Check `modules/decision/logs/precommit_checks.jsonl` by `guardrail_check_id` when domain requires precommit.
   - Apply domain policy from `modules/decision/data/domain_guardrails.yaml`.
   - For precommit-required domains, require `principle_refs` or active `exception_ref`.
   - Append one gate audit record to `modules/decision/logs/decision_gate_checks.jsonl`.
   - Append one constitutional context record to `modules/decision/logs/decision_constitution_checks.jsonl`.
4. Only when gate status is `pass` or `override_accepted`, append one new line to `decisions.jsonl`.
5. If gate status is `blocked`, do not append decision record.
6. Do not modify prior records.

## Notes

- If `follow_up_date` exists, include it in the new record.
- For high-risk decisions (especially `invest`), run `precommit_check.md` first and reference the check ID.
- For high-risk decisions, include explicit constitutional context (`--principle-ref ...` or `--exception-ref ...`).
- CLI path: `python3 orchestrator/src/main.py log-decision ...` enforces this gate automatically.
- Do not schedule tasks or reminders here; logging only.
- If any required field remains unknown, mark the gap explicitly and confirm before appending.
