# Skill: Detect Disequilibrium

## Purpose

Detect productive cognitive tension around a topic by scanning multi-source mismatch signals.

## Required Files

1. `modules/cognition/data/conflict_taxonomy.yaml`
2. `modules/cognition/logs/schema_versions.jsonl`
3. `modules/cognition/logs/disequilibrium_events.jsonl`
4. Relevant decision/profile/memory signals from the same time window (runtime-supplied)

## Procedure

1. Filter records by topic and time window.
2. Classify signals using conflict taxonomy.
3. Compute a tension score and summarize mismatch patterns.
4. Append one `disequilibrium_events` record with `source_refs`.
5. Produce a report with unresolved questions and candidate revision directions.

## Constraints

- Treat repeated conflicts as structural, not merely informational, unless evidence suggests otherwise.
- If no strong signals exist, return explicit low-signal result.
