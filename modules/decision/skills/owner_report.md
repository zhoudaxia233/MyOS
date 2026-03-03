# Skill: Owner Report

## Purpose

Generate a one-page owner audit report that consolidates drift metrics, guardrail exceptions, and recent decision artifacts.

## Required Files

1. `modules/decision/logs/guardrail_overrides.jsonl`
2. `modules/decision/outputs/decision_audit_<YYYYMMDD>.md` (latest if available)
3. `modules/decision/outputs/weekly_review_<YYYYMMDD>.md` (latest if available)
4. `modules/decision/outputs/metrics_<YYYYMMDD>.md` (latest if available)

## Output Sections

- Executive summary (metric statuses)
- Top exceptions
- Source artifacts
- Owner actions

## Save Path

- `modules/decision/outputs/owner_report_<YYYYMMDD>.md`

## Constraints

- Prioritize exception visibility over long narrative.
- Keep actionable owner decisions explicit.
- Do not mutate historical logs.
