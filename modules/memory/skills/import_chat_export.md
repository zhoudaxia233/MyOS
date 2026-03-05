# Skill: Import Chat Export

## Purpose

Normalize exported chat messages into append-only `memory_events` records.

## Required Files

1. `modules/memory/MODULE.md`
2. `modules/memory/data/memory_policy.yaml`
3. `modules/memory/logs/memory_events.jsonl`

## Inputs

- Required: input chat export file path (`.json` / `.jsonl` / `.md` / `.txt`)
- Optional: `max_events` (default 50), extra tags, dry-run mode

## Procedure

1. Parse chat messages from export file.
2. Normalize into factual memory event records with:
   - `source_type = chat`
   - concise `event`
   - fixed `why_it_matters`
   - deterministic tags
3. Append normalized records to `memory_events.jsonl` (or preview only in dry-run).
4. Return appended record IDs.

## CLI Entry

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py ingest-chat --input <chat_export_path> [--max-events 50] [--tag focus] [--dry-run]
```

## Constraints

- Never rewrite existing records.
- Keep imported records concise and machine-searchable.
- If no valid messages are parsed, return zero append result instead of fabricating records.
