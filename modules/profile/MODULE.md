# Profile Module

## Purpose

This module is the personal identity and direction layer of Personal Core OS. It stores long-horizon goals, operating preferences, risk boundaries, and recurring trigger patterns so agent execution remains aligned with the user's enduring priorities.

## Scope

- Maintain stable personal north star and values
- Record profile changes as append-only events
- Track trigger patterns and safety boundaries
- Provide alignment checks before major strategic actions

## File Inventory

### Instructions and skills

- `modules/profile/MODULE.md`: Module purpose, workflows, loading rules, and instructions
- `modules/profile/skills/update_profile.md`: Procedure for updating profile via append-only change log
- `modules/profile/skills/alignment_check.md`: Quick check for goal/value alignment

### Canonical data (SSOT)

- `modules/profile/data/identity.yaml`: Long-term goals, values, strengths, blind spots
- `modules/profile/data/operating_preferences.yaml`: Working style preferences and guardrails

### Logs (append-only JSONL)

- `modules/profile/logs/profile_changes.jsonl`: Profile evolution events and rationale
- `modules/profile/logs/trigger_events.jsonl`: Trigger observations and mitigations

### Outputs

- `modules/profile/outputs/`: Alignment reports and summaries

## Workflows

1. Update profile baseline
   - Review current profile YAML files.
   - Append a change record in `profile_changes.jsonl`.
   - Then apply targeted edits to canonical YAML.
2. Record trigger event
   - Append an event in `trigger_events.jsonl` with signal and mitigation.
3. Alignment check
   - Compare a proposed plan against `identity.yaml` and `operating_preferences.yaml`.
   - Output pass/fail with short rationale and adjustments.

## Progressive Loading Rules (Required)

- For profile updates: load `update_profile.md`, both data YAML files, and `profile_changes.jsonl`.
- For alignment checks: load only the two data YAML files plus this module file.
- For trigger logging: load `trigger_events.jsonl` schema and append one line.
- Do not load content or memory logs unless the user requests cross-module synthesis.

<instructions>
- Treat profile data as SSOT for personal direction and constraints.
- Never overwrite or delete historical log entries.
- Keep changes specific: what changed, why, expected impact.
- If unsure about personal preference, label it as assumption and ask for confirmation.
- Prefer behaviorally testable statements over abstract personality labels.
</instructions>
