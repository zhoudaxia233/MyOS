# Skill: Log Assimilation Event

## Purpose

Record how new input is interpreted through an existing schema.

## Required Files

1. `modules/cognition/logs/schema_versions.jsonl`
2. `modules/cognition/logs/assimilation_events.jsonl`

## Procedure

1. Identify the active schema version.
2. Capture input summary and interpretation lens.
3. Score fit (`fit_score`) and list stretch points.
4. Append one record to `assimilation_events.jsonl`.

## Constraints

- Keep interpretation distinct from raw observation.
- Fit score must be explicit (1-10).
- Low fit should trigger disequilibrium review.
