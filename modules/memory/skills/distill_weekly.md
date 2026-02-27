# Skill: Distill Weekly Memory

## Purpose

Convert the last 7 days of raw memory into reusable operational signals.

## Required Files

1. `modules/memory/data/memory_policy.yaml`
2. `modules/memory/logs/memory_events.jsonl` (last 7 days)
3. `modules/memory/logs/memory_insights.jsonl` (last 7 days)

## Output

- 3 recurring patterns
- 3 helpful shifts to keep
- 3 risks to monitor
- 3 experiments for next week
- Source event IDs per pattern

Save to:

- `modules/memory/outputs/weekly_memory_<YYYYMMDD>.md`

## Constraints

- Separate facts from inferences.
- Each inferred pattern must cite `source_refs` IDs.
