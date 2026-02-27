# Memory Module

## Purpose

This module captures evolving operational memory from conversations, reflections, and notable observations. It converts raw short-term inputs into distilled, reusable memory so future actions can align with long-term direction.

## Scope

- Ingest daily memory snippets from chats, notes, and reflections
- Tag and store memory events in append-only logs
- Distill weekly memory summaries with actionable signals
- Provide reusable memory references by ID to other modules

## File Inventory

### Instructions and skills

- `modules/memory/MODULE.md`: Module purpose, workflows, and loading rules
- `modules/memory/skills/ingest_memory.md`: Add daily memory records
- `modules/memory/skills/distill_weekly.md`: Build weekly distilled memory output

### Canonical data (SSOT)

- `modules/memory/data/memory_policy.yaml`: Capture rules, tagging, and quality thresholds

### Logs (append-only JSONL)

- `modules/memory/logs/memory_events.jsonl`: Raw events from conversations and reflections
- `modules/memory/logs/memory_insights.jsonl`: Distilled insights extracted from event clusters

### Outputs

- `modules/memory/outputs/`: Weekly distilled reports and summaries

## Workflows

1. Daily ingest
   - Append raw events with minimal structured fields.
2. Insight extraction
   - Group related events and append insight records.
3. Weekly distillation
   - Read the last 7 days of memory events/insights.
   - Produce concise pattern summary and recommended updates.

## Progressive Loading Rules (Required)

- For ingest: load `ingest_memory.md`, `memory_policy.yaml`, and `memory_events.jsonl` schema.
- For distillation: load both memory logs plus `memory_policy.yaml`.
- Do not load full content/decision logs unless cross-module analysis is explicitly requested.

<instructions>
- Store facts as observed statements; avoid reinterpretation in raw event logs.
- Keep records concise and tagged for retrieval.
- Preserve append-only history in all memory logs.
- Distilled insights must reference source event IDs.
- Mark uncertainty explicitly when evidence is thin.
</instructions>
