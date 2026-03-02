# Profile Module

## Purpose

This module is the personal identity and adaptation layer of Personal Core OS. It stores long-horizon goals, operating preferences, and psychological patterns so agent execution remains aligned with enduring direction while adapting to behavioral drift.

## Scope

- Maintain stable personal north star and values
- Record profile changes as append-only events
- Track trigger patterns and mitigation quality
- Maintain a non-clinical psych profile for operational self-regulation
- Provide alignment checks before major strategic actions

## File Inventory

### Instructions and skills

- `modules/profile/MODULE.md`: Module purpose, workflows, loading rules, and instructions
- `modules/profile/skills/update_profile.md`: Procedure for updating profile via append-only change log
- `modules/profile/skills/alignment_check.md`: Quick check for goal/value alignment
- `modules/profile/skills/log_trigger_event.md`: Append one trigger event record
- `modules/profile/skills/log_psych_observation.md`: Append one psych observation record
- `modules/profile/skills/profile_snapshot.md`: Generate periodic psych + alignment snapshot

### Canonical data (SSOT)

- `modules/profile/data/identity.yaml`: Long-term goals, values, strengths, blind spots
- `modules/profile/data/operating_preferences.yaml`: Working style preferences and guardrails
- `modules/profile/data/psych_profile.yaml`: Behavioral tendencies, triggers, and stabilizers

### Logs (append-only JSONL)

- `modules/profile/logs/profile_changes.jsonl`: Profile evolution events and rationale
- `modules/profile/logs/trigger_events.jsonl`: Trigger observations and mitigations
- `modules/profile/logs/psych_observations.jsonl`: Pattern observations and confidence over time

### Outputs

- `modules/profile/outputs/`: Alignment reports and profile snapshots

## Workflows

1. Update profile baseline
   - Review profile YAML files.
   - Append a change record in `profile_changes.jsonl`.
   - Apply targeted edits to canonical YAML.
2. Record trigger event
   - Append an event in `trigger_events.jsonl` with signal and mitigation.
3. Record psych observation
   - Append pattern observation with confidence to `psych_observations.jsonl`.
4. Alignment check
   - Compare a proposed plan against identity, preferences, and psych profile constraints.
5. Periodic profile snapshot
   - Summarize drift risk, stable strengths, and proposed adjustments.

## Progressive Loading Rules (Required)

- For profile updates: load `update_profile.md`, profile YAML files, and `profile_changes.jsonl`.
- For alignment checks: load only profile data YAML files plus this module file.
- For trigger logging: load `trigger_events.jsonl` schema and append one line.
- For psych observation logging: load `psych_observations.jsonl` schema and append one line.
- For snapshots: load profile data + last 30 days of trigger/psych logs.
- Do not load content or decision logs unless cross-module synthesis is explicitly requested.

<instructions>
- Treat profile data as SSOT for personal direction and constraints.
- Keep psych profiling operational and non-clinical.
- Never overwrite or delete historical log entries.
- Keep changes specific: what changed, why, expected impact.
- If unsure about personal preference, label it as assumption and ask for confirmation.
- Prefer behaviorally testable statements over abstract labels.
</instructions>
