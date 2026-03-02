# Skill: Guardrail Override

## Purpose

Log and justify an explicit guardrail override when a decision proceeds despite policy violations.

## Required Files

1. `modules/decision/data/domain_guardrails.yaml`
2. `modules/decision/logs/guardrail_overrides.jsonl`

## Required Inputs

- Domain
- Decision reference (`decision_id` or temporary reference)
- Violations summary
- Override reason
- Owner confirmation

## Procedure

1. Validate override is allowed in the domain policy.
2. Validate required override fields are present.
3. Append one record to `guardrail_overrides.jsonl`.
4. Return override record ID.

## Constraints

- Override logging is mandatory when bypassing a blocking guardrail.
- Keep reasons factual and concise.
- Never edit existing override records.
