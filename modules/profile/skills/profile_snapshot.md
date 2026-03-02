# Skill: Profile Snapshot

## Purpose

Generate a periodic profile snapshot for audit-first oversight.

## Required Files

1. `modules/profile/data/identity.yaml`
2. `modules/profile/data/operating_preferences.yaml`
3. `modules/profile/data/psych_profile.yaml`
4. `modules/profile/logs/trigger_events.jsonl` (last 30 days)
5. `modules/profile/logs/psych_observations.jsonl` (last 30 days)

## Output Format

- `Stable strengths (3)`
- `Drift risks (3)`
- `Trigger patterns (top 3)`
- `Mitigation quality` (pass / mixed / weak with rationale)
- `Next 2 profile adjustments`

Save to:

- `modules/profile/outputs/profile_snapshot_<YYYYMMDD>.md`

## Constraints

- Keep language operational and non-clinical.
- Separate facts from inferences.
- Every inference must cite log IDs.
