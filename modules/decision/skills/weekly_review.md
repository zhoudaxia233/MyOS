# Skill: Weekly Review

## Purpose

Review the last 7 days of decisions, failures, experiences, and precommit checks to extract patterns and propose small heuristic improvements.

## Required Files to Load (Progressive Disclosure)

1. `modules/decision/MODULE.md`
2. `modules/decision/data/heuristics.yaml`
3. `modules/decision/logs/decisions.jsonl` (last 7 days by `created_at`)
4. `modules/decision/logs/failures.jsonl` (last 7 days by `created_at`)
5. `modules/decision/logs/experiences.jsonl` (last 7 days by `created_at`)
6. `modules/decision/logs/precommit_checks.jsonl` (last 7 days by `created_at`)
7. `modules/decision/logs/guardrail_overrides.jsonl` (last 7 days by `created_at`)

## Output Format (Required)

- `3 patterns noticed`
- `3 keep doing`
- `3 stop doing`
- `3 experiments next week`
- `1 heuristics.yaml patch suggestion` (show as YAML diff snippet)

## Procedure

1. Filter each log to records in the last 7 days using `created_at`.
2. Separate observed facts from inferred patterns.
3. Include at least one observation about guardrail quality (coverage, cooldowns, override frequency).
4. Produce the required sections with concise bullets.
5. Draft one small, specific `heuristics.yaml` patch suggestion as a YAML diff snippet.
6. Save the review to:
   - `modules/decision/outputs/weekly_review_<YYYYMMDD>.md`

## Constraints

- Do not rewrite log records.
- Do not moralize; focus on repeatable behavior changes.
- If there are too few records, state the sample-size limitation explicitly.
