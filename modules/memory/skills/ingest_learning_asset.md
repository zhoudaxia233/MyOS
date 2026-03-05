# Skill: Ingest Learning Asset

## Purpose

Convert one external learning input (video/article/book notes) into reusable system memory and decision-ready rules.

## Required Files

1. `modules/memory/MODULE.md`
2. `modules/memory/data/memory_policy.yaml`
3. `modules/memory/logs/memory_events.jsonl`
4. `modules/memory/logs/memory_insights.jsonl`

## Minimal Inputs

- Asset title
- Source type (`video` / `article` / `book` / `course`)
- 3-8 core points
- Why it matters for execution/decision quality

## Procedure

1. Append 1-2 records to `memory_events.jsonl` with `source_type=external_observation` or `reflection`.
2. Append 1 record to `memory_insights.jsonl`:
   - crystallize the transferable principle (not just summary),
   - include `source_refs` pointing to the newly appended event IDs.
3. If the principle is operationally stable, propose a small heuristic patch snippet (owner applies in decision module).
4. Return the appended IDs and the suggested heuristic patch.

## Constraints

- Keep events factual; keep insights inferential but testable.
- Do not overwrite old logs; append only.
- Use IDs for cross-module references; do not duplicate full content in multiple places.
