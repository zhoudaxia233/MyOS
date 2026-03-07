# Skill: Propose Amendment

## Purpose

Propose and record a constitutional amendment with explicit evidence and owner approval reference.

## Required Files

1. `modules/principles/data/constitution.yaml`
2. `modules/principles/data/amendment_policy.yaml`
3. `modules/principles/logs/principle_amendments.jsonl`

## Procedure

1. Validate proposal against amendment policy admission criteria.
2. Append one amendment record with `evidence_refs` and `approval_ref`.
3. If approved, apply targeted update to `constitution.yaml` and record effective date.

## Constraints

- No amendment without owner approval reference.
- No cross-module content duplication; use IDs in `source_refs`.
- Keep old constitutional wording traceable via amendment logs.
