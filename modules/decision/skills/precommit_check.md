# Skill: Precommit Check

## Purpose

Run a lightweight guardrail check before high-risk decisions and append the result to `precommit_checks.jsonl`.

## Required Files

1. `modules/decision/MODULE.md`
2. `modules/decision/data/impulse_guardrails.yaml`
3. `modules/decision/logs/precommit_checks.jsonl`

## Inputs

- Domain
- Proposed decision
- Emotional weight (1-10)
- Downside statement
- Invalidation condition
- Max acceptable loss/cost
- Disconfirming signal

## Procedure

1. Load guardrail rules from `impulse_guardrails.yaml`.
2. Validate required fields.
3. If emotional weight exceeds cooldown threshold, mark `cooldown_required: true`.
4. Build one JSON object and append to `precommit_checks.jsonl`.
5. Return a short status: pass / pass_with_cooldown / blocked.

## Constraints

- Do not make the final decision here.
- Do not rewrite existing records.
