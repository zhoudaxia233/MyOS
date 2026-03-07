# Skill: Run Constitutional Audit

## Purpose

Generate an owner-facing audit of constitutional amendments, exceptions, and unresolved governance risks.

## Required Files

1. `modules/principles/data/constitution.yaml`
2. `modules/principles/logs/principle_amendments.jsonl` (selected window)
3. `modules/principles/logs/principle_exceptions.jsonl` (selected window)
4. `modules/principles/outputs/templates/constitutional_audit_report.md`

## Output Requirements

- Summarize amendment and exception counts by principle.
- Highlight unresolved exceptions and repeat override patterns.
- Provide concrete actions with owner review priority.
- Save report to:
  - `modules/principles/outputs/constitutional_audit_<YYYYMMDD>.md`

## Constraints

- Prioritize governance exceptions over narrative.
- Separate facts from inference.
- Cite record IDs for each finding.
