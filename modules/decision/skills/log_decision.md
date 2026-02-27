# Skill: Log Decision

## Purpose

Append a new decision record to `modules/decision/logs/decisions.jsonl` with minimal friction.

## Ask Minimal Questions (Only If Missing)

Required minimum fields to ask for:

- `domain` (`invest` / `project` / `content` / `life`)
- `decision` (what was decided)
- `options` (considered alternatives)
- `confidence` (1-10)

Optional but useful:

- `reasoning`
- `risks`
- `expected_outcome`
- `time_horizon`
- `follow_up_date` (ISO date)

## Procedure

1. Read `core/SCHEMAS.md` for ID/timestamp conventions if needed.
2. Read the schema header line in `modules/decision/logs/decisions.jsonl`.
3. Build a new JSON object matching the file schema.
4. Append exactly one new JSON line.
5. Do not modify prior records.

## Notes

- If `follow_up_date` exists, include it in the new record.
- Do not schedule tasks or reminders here; logging only.
- If any required field remains unknown, mark the gap explicitly and confirm before appending.
