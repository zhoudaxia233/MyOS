# Skill: Extract Chat Patterns

## Purpose

Extract stable paradigms from recent chat-derived memory events.

## Required Files

1. `modules/memory/data/pattern_taxonomy.yaml`
2. `modules/memory/logs/memory_events.jsonl` (target window)
3. `modules/memory/logs/chat_patterns.jsonl`

## Procedure

1. Filter `memory_events` where `source_type` is `chat`.
2. Cluster events by repeated trigger, behavior, or outcome.
3. Validate each candidate against `pattern_taxonomy.yaml` minimum evidence rules.
4. Append one JSONL line per accepted pattern to `chat_patterns.jsonl`.
5. Return the added pattern IDs and one-line rationale each.

## Required Record Fields

- `id`
- `created_at`
- `status`
- `pattern_class`
- `pattern_statement`
- `evidence`
- `source_refs`
- `confidence`
- `actionable_rule`

## Constraints

- No pattern from a single event.
- Separate facts from inference in `evidence` and `pattern_statement`.
