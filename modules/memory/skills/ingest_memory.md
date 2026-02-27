# Skill: Ingest Memory

## Purpose

Capture one memory event from a conversation, reflection, or observation.

## Required Files

1. `modules/memory/MODULE.md`
2. `modules/memory/data/memory_policy.yaml`
3. `modules/memory/logs/memory_events.jsonl`

## Minimal Inputs

- Event summary
- Why it matters
- Tags (1-4)

## Procedure

1. If fields are missing, ask minimal follow-up questions.
2. Create one JSONL record with a new ID and UTC timestamp.
3. Append to `memory_events.jsonl`.
4. Return the appended object.

## Constraints

- Keep event statement factual and concise.
- No rewriting old records.
