# Skill: Log Accommodation Revision

## Purpose

Record explicit schema restructuring when old interpretation fails.

## Required Files

1. `modules/cognition/data/revision_operators.yaml`
2. `modules/cognition/logs/schema_versions.jsonl`
3. `modules/cognition/logs/accommodation_revisions.jsonl`

## Procedure

1. Identify failed assumptions from a prior schema version.
2. Select one revision operator (`weaken|replace|split|merge|refine`).
3. Write revision summary and new schema hypothesis.
4. Optionally create a new schema version linked to the old one.
5. Append one accommodation record.

## Constraints

- Revision type must be explicit and justified.
- Keep failure diagnosis separate from new hypothesis.
- Include source references for triggering evidence.
