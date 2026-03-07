# Skill: Log Principle Exception

## Purpose

Log a temporary constitutional exception with explicit risk acknowledgment and owner confirmation.

## Required Files

1. `modules/principles/data/constitution.yaml`
2. `modules/principles/data/amendment_policy.yaml`
3. `modules/principles/logs/principle_exceptions.jsonl`

## Procedure

1. Identify the affected `principle_id` and context.
2. Require exception reason, risk acknowledgment, owner confirmation, and expiry.
3. Append one exception record and link related decision IDs.

## Constraints

- Exceptions are temporary; include expiry.
- Missing owner confirmation blocks the write.
- Track closure outcome as follow-up append record.
