# Skill: Audit Decision System

## Purpose

Generate an owner-audit report so the user can review exceptions quickly instead of reading every raw log line.

## Required Files

1. `modules/decision/data/audit_rules.yaml`
2. `modules/decision/logs/decisions.jsonl` (selected window)
3. `modules/decision/logs/failures.jsonl` (selected window)
4. `modules/decision/logs/precommit_checks.jsonl` (selected window)
5. `modules/decision/logs/guardrail_overrides.jsonl` (selected window)
6. `modules/decision/data/heuristics.yaml`
7. `modules/decision/outputs/templates/decision_audit_report.md`

## Output Requirements

- Compute key metrics from `audit_rules.yaml`.
- Identify top exceptions and recurring drift patterns.
- Propose corrective actions with owners and deadlines.
- Save report to:
  - `modules/decision/outputs/decision_audit_<YYYYMMDD>.md`

## Constraints

- Prioritize exceptions over narrative.
- Separate facts from inferences.
- Cite log IDs for every finding.
