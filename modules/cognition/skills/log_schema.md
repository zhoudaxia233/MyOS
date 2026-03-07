# Skill: Log Schema Version

## Purpose

Create or version a schema as an explicit cognitive structure.

## Required Files

1. `modules/cognition/data/schema_policy.yaml`
2. `modules/cognition/logs/schema_versions.jsonl`

## Procedure

1. Capture topic, schema name, summary, assumptions, predictions, and boundaries.
2. Assign `schema_id` and increment version.
3. Append one schema version record to `schema_versions.jsonl`.
4. Return schema version ID and key deltas vs parent version (if any).

## Constraints

- Never overwrite old schema versions.
- Assumptions and predictions should be testable where possible.
- Include `parent_schema_version_id` when this is a revision lineage.
