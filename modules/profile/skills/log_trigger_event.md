# Skill: Log Trigger Event

## Purpose

Append one trigger event record when a high-pressure or high-emotion pattern appears.

## Required Files

1. `modules/profile/logs/trigger_events.jsonl`

## Required Inputs

- Context
- Trigger signal
- Immediate response
- Mitigation action
- Emotional weight (1-10)
- Tags

## Procedure

1. Build one JSON object following the schema header fields.
2. Append one line to `trigger_events.jsonl`.
3. Return the appended record ID.

## Constraints

- Keep language factual.
- No edits to historical lines.
