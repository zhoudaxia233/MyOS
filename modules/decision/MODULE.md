# Decision Module

## Purpose

This module stores judgment memory for decisions, failures, and meaningful experiences. Its goal is decision stability over time: capture choices as they happen, preserve reasoning, and review patterns weekly to improve heuristics.

## Scope

- Log decisions immediately after they occur
- Record failures and post-mortems
- Record notable experiences/signals
- Run precommit guardrail checks for high-risk decisions
- Run weekly pattern reviews
- Propose heuristic updates without rewriting history

## File Inventory

### Instructions and skills

- `modules/decision/MODULE.md`: Module purpose, workflows, loading rules, and behavioral instructions
- `modules/decision/skills/log_decision.md`: Minimal workflow for appending a decision record
- `modules/decision/skills/precommit_check.md`: Guardrail check before committing high-risk decisions
- `modules/decision/skills/weekly_review.md`: Weekly review workflow and output format

### Canonical data (SSOT)

- `modules/decision/data/heuristics.yaml`: Current heuristics, priorities, and risk rules (editable SSOT)
- `modules/decision/data/impulse_guardrails.yaml`: Precommit check rules and cooldown policy

### Logs (append-only JSONL)

- `modules/decision/logs/decisions.jsonl`: Decision records and expected outcomes
- `modules/decision/logs/failures.jsonl`: Failure post-mortems and prevention steps
- `modules/decision/logs/experiences.jsonl`: High-signal experiences and why they mattered
- `modules/decision/logs/precommit_checks.jsonl`: Guardrail checks before high-risk commitments

### Outputs

- `modules/decision/outputs/`: Weekly reviews and analysis artifacts

## Workflows

1. Log decision immediately after it happens
   - Append to `decisions.jsonl` while reasoning is still fresh.
2. Log failure post-mortem
   - Append to `failures.jsonl` with root cause and prevention.
3. Run precommit check for high-risk decisions
   - Use `impulse_guardrails.yaml` and append one record to `precommit_checks.jsonl`.
   - If emotional load is high, enforce cooldown before final commitment.
4. Weekly review
   - Read the last 7 days of decision/failure/experience logs.
   - Include precommit checks to spot impulse patterns and override frequency.
   - Summarize patterns and propose heuristic updates.
   - Save review output to `outputs/`.

## Progressive Loading Rules (Required)

- For decision logging: load only `modules/decision/skills/log_decision.md` and `decisions.jsonl` schema/records as needed.
- For precommit checks: load `precommit_check.md`, `impulse_guardrails.yaml`, and `precommit_checks.jsonl`.
- For weekly review: load `weekly_review.md`, relevant log slices (last 7 days), `heuristics.yaml`, and `precommit_checks.jsonl`.
- Do not load content module files unless the user explicitly requests a cross-module analysis.

<instructions>
- Never moralize; focus on tradeoffs, decision quality, and pattern extraction.
- Always separate "decision-time reasoning" from "post-hoc review" when both appear.
- For high-risk calls, require explicit downside, invalidation condition, and disconfirming signal.
- Preserve append-only log integrity; never rewrite or delete history.
- Use explicit uncertainty language when memory or evidence is incomplete.
- Prefer short, concrete descriptions over abstract self-judgment.
</instructions>
