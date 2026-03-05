# Memory Module

## Purpose

This module captures evolving operational memory from conversations, reflections, and notable observations. It converts raw short-term inputs into distilled, reusable memory and explicit chat-derived paradigms for future decision and execution quality.

## Scope

- Ingest daily memory snippets from chats, notes, and reflections
- Tag and store memory events in append-only logs
- Extract chat patterns/paradigms from clustered events
- Distill weekly memory summaries with actionable signals
- Provide reusable memory references by ID to other modules

## File Inventory

### Instructions and skills

- `modules/memory/MODULE.md`: Module purpose, workflows, and loading rules
- `modules/memory/module.manifest.yaml`: Routing keywords and planning defaults for orchestrator auto-discovery
- `modules/memory/skills/ingest_memory.md`: Add daily memory records
- `modules/memory/skills/ingest_learning_asset.md`: Convert external learning into reusable memory and rules
- `modules/memory/skills/import_chat_export.md`: Import chat export and normalize into memory events
- `modules/memory/skills/extract_chat_patterns.md`: Derive paradigms from chat-heavy event slices
- `modules/memory/skills/distill_weekly.md`: Build weekly distilled memory output

### Canonical data (SSOT)

- `modules/memory/data/memory_policy.yaml`: Capture rules, tagging, and quality thresholds
- `modules/memory/data/pattern_taxonomy.yaml`: Pattern classes and extraction criteria
- `modules/memory/data/learning_assets/`: External learning source notes (video/article/book) for traceability

### Logs (append-only JSONL)

- `modules/memory/logs/memory_events.jsonl`: Raw events from conversations and reflections
- `modules/memory/logs/memory_insights.jsonl`: Distilled insights extracted from event clusters
- `modules/memory/logs/chat_patterns.jsonl`: Stable paradigms extracted from chat traces

### Outputs

- `modules/memory/outputs/`: Weekly distilled reports and summaries

## Workflows

1. Daily ingest
   - Append raw events with minimal structured fields.
2. External learning ingest
   - Convert video/article/book notes into `memory_events` and one distilled `memory_insights` record.
   - Link insights to source event IDs.
3. Chat export import
   - Normalize chat export messages to `memory_events` records.
   - Append imported records with `source_type=chat` and deterministic tags.
4. Pattern extraction
   - Filter chat events and derive paradigms using pattern taxonomy.
   - Append paradigm records to `chat_patterns.jsonl`.
5. Insight extraction
   - Group related events and append insight records.
6. Weekly distillation
   - Read last 7 days of events/insights/patterns.
   - Produce concise pattern summary and recommended updates.

## Progressive Loading Rules (Required)

- For ingest: load `ingest_memory.md`, `memory_policy.yaml`, and `memory_events.jsonl` schema.
- For external learning ingest: load `ingest_learning_asset.md`, `memory_policy.yaml`, and memory log schemas.
- For chat export import: load `import_chat_export.md`, `memory_policy.yaml`, and `memory_events.jsonl`.
- For pattern extraction: load `extract_chat_patterns.md`, `pattern_taxonomy.yaml`, and recent `memory_events.jsonl`.
- For distillation: load memory logs plus `memory_policy.yaml`.
- Do not load full content/decision logs unless cross-module analysis is explicitly requested.

<instructions>
- Store facts as observed statements; avoid reinterpretation in raw event logs.
- Keep records concise and tagged for retrieval.
- Preserve append-only history in all memory logs.
- Distilled insights must reference source event IDs.
- Chat pattern records must include confidence and source_refs.
- Mark uncertainty explicitly when evidence is thin.
</instructions>
