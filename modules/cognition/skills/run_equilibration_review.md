# Skill: Run Equilibration Review

## Purpose

Summarize weekly cognitive evolution and identify next schema upgrades.

## Required Files

1. `modules/cognition/logs/schema_versions.jsonl` (target window)
2. `modules/cognition/logs/assimilation_events.jsonl` (target window)
3. `modules/cognition/logs/disequilibrium_events.jsonl` (target window)
4. `modules/cognition/logs/accommodation_revisions.jsonl` (target window)
5. `modules/cognition/logs/equilibration_cycles.jsonl` (target window)

## Output Format

- `Schemas updated this week`
- `Top disequilibrium clusters`
- `Accommodations executed`
- `Equilibration quality`
- `Open tensions next week`

Save to:

- `modules/cognition/outputs/equilibration_review_<YYYYMMDD>.md`

## Constraints

- Keep old vs new schema links explicit by ID.
- Separate observed conflicts from speculative conclusions.
