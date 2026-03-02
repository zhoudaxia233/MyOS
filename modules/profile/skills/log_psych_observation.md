# Skill: Log Psych Observation

## Purpose

Append one operational psych observation based on repeated behavior patterns.

## Required Files

1. `modules/profile/data/psych_profile.yaml`
2. `modules/profile/logs/psych_observations.jsonl`

## Required Inputs

- Observation statement
- Evidence
- Source refs (IDs)
- Confidence (1-10)
- Suggested stabilizer
- Tags

## Procedure

1. Validate the statement is non-clinical and behavior-focused.
2. Build one JSON object matching the schema.
3. Append to `psych_observations.jsonl`.
4. Return observation ID and confidence.

## Constraints

- No diagnosis language.
- Evidence must cite IDs when available.
