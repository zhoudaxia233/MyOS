# Skill: Update Profile

## Purpose

Update personal baseline data safely while preserving evolution history.

## Required Files

1. `modules/profile/MODULE.md`
2. `modules/profile/data/identity.yaml`
3. `modules/profile/data/operating_preferences.yaml`
4. `modules/profile/data/psych_profile.yaml`
5. `modules/profile/logs/profile_changes.jsonl`

## Procedure

1. Ask what changed in one sentence (goal, value, preference, boundary, or trigger).
2. Draft the exact YAML delta before editing canonical files (`identity`, `operating_preferences`, or `psych_profile`).
3. Append a new line to `profile_changes.jsonl` capturing:
   - change summary
   - reason
   - expected effect
4. Apply minimal edits to the YAML SSOT files.
5. Return a short "before -> after" diff summary.

## Constraints

- Never delete past change records.
- Use concrete language that can be validated in behavior.
- If the request is ambiguous, ask one clarifying question before editing.
