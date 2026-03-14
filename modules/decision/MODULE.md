# Decision Module

## Purpose

This module stores judgment memory for decisions, failures, meaningful experiences, and audit outputs. Its goal is decision stability over time: capture choices as they happen, preserve reasoning, enforce guardrails, and continuously audit drift from operating principles.

## Scope

- Log decisions immediately after they occur
- Record failures and post-mortems
- Record notable experiences/signals
- Run precommit guardrail checks for high-risk decisions
- Run weekly pattern reviews
- Produce audit-first views for owner oversight
- Propose heuristic updates without rewriting history

## File Inventory

### Instructions and skills

- `modules/decision/MODULE.md`: Module purpose, workflows, loading rules, and behavioral instructions
- `modules/decision/module.manifest.yaml`: Routing keywords and planning defaults for orchestrator auto-discovery
- `modules/decision/skills/log_decision.md`: Minimal workflow for appending a decision record
- `modules/decision/skills/precommit_check.md`: Guardrail check before committing high-risk decisions
- `modules/decision/skills/guardrail_override.md`: Override logging workflow for blocked guardrails
- `modules/decision/skills/weekly_review.md`: Weekly review workflow and output format
- `modules/decision/skills/audit_decision_system.md`: Generate concise audit report for owner review
- `modules/decision/skills/owner_report.md`: One-page owner report integrating key signals

### Canonical data (SSOT)

- `modules/decision/data/heuristics.yaml`: Current heuristics, priorities, and risk rules
- `modules/decision/data/impulse_guardrails.yaml`: Precommit check rules and cooldown policy
- `modules/decision/data/domain_guardrails.yaml`: Domain-specific guardrail hardening policies
- `modules/decision/data/audit_rules.yaml`: Thresholds and scoring rules for audit outputs

### Logs (append-only JSONL)

- `modules/decision/logs/decisions.jsonl`: Decision records and expected outcomes
- `modules/decision/logs/failures.jsonl`: Failure post-mortems and prevention steps
- `modules/decision/logs/experiences.jsonl`: High-signal experiences and why they mattered
- `modules/decision/logs/precommit_checks.jsonl`: Guardrail checks before high-risk commitments
- `modules/decision/logs/guardrail_overrides.jsonl`: Explicit override audit trail records
- `modules/decision/logs/decision_gate_checks.jsonl`: Gate outcomes before decision append (pass/blocked/override)
- `modules/decision/logs/decision_constitution_checks.jsonl`: Principle context checks (`principle_refs`/`exception_ref`) per decision gate
- `modules/decision/logs/owner_todos.jsonl`: Owner escalation todo queue derived from repeated risk signals

### Outputs

- `modules/decision/outputs/`: Weekly reviews and audit artifacts
- `modules/decision/outputs/templates/decision_audit_report.md`: Report structure template

## Workflows

1. Log decision immediately after it happens
   - Append to `decisions.jsonl` while reasoning is fresh.
2. Log failure post-mortem
   - Append to `failures.jsonl` with root cause and prevention.
3. Run precommit check for high-risk decisions
   - Use `impulse_guardrails.yaml` and append one record to `precommit_checks.jsonl`.
   - If emotional load is high, enforce cooldown before final commitment.
4. Guardrail hardening check
   - Validate domain policy in `domain_guardrails.yaml` before committing risky actions.
   - If blocked but overridden, append one record to `guardrail_overrides.jsonl`.
   - Always append one gate audit record to `decision_gate_checks.jsonl` before writing `decisions.jsonl`.
5. Principle context check
   - For precommit-required domains, require `principle_refs` or an active `exception_ref`.
   - Append one constitutional context record to `decision_constitution_checks.jsonl`.
6. Weekly review
   - Read the last 7 days of logs.
   - Include precommit checks and guardrail overrides to spot policy drift.
   - Summarize patterns and propose heuristic updates.
   - If the review produces a real owner-facing recommendation, end the output with an explicit `## Owner Action Proposal` section so owner review sees the proposal object instead of the run shell.
7. Decision audit
   - Score recent behavior against `audit_rules.yaml`.
   - Produce owner-facing exception report with actions.

## Progressive Loading Rules (Required)

- For decision logging: load `log_decision.md`, `precommit_checks.jsonl`, `domain_guardrails.yaml`, `modules/principles/data/constitution.yaml` (when present), `modules/principles/logs/principle_exceptions.jsonl` (when exception is provided), and `decisions.jsonl`.
- For precommit checks: load `precommit_check.md`, `impulse_guardrails.yaml`, and `precommit_checks.jsonl`.
- For guardrail hardening: load `guardrail_override.md`, `domain_guardrails.yaml`, and `guardrail_overrides.jsonl`.
- For weekly review: load `weekly_review.md`, recent log slices, `heuristics.yaml`, `precommit_checks.jsonl`, and `guardrail_overrides.jsonl`.
- For audits: load `audit_decision_system.md`, `audit_rules.yaml`, recent logs, and report template.
- Do not load unrelated modules unless explicit cross-module analysis is requested.

<instructions>
- Never moralize; focus on tradeoffs, decision quality, and pattern extraction.
- Always separate decision-time reasoning from post-hoc review.
- Treat `heuristics.yaml` as tactical guidance; constitutional constraints are owned by `modules/principles/`.
- For high-risk calls, require explicit downside, invalidation condition, and disconfirming signal.
- For precommit-required domains, require explicit principle context (`principle_refs` or active `exception_ref`) before appending decisions.
- Keep outputs audit-friendly: concise exceptions, metrics, and actions.
- When a decision output truly needs owner judgment, emit an explicit proposal section (`## Judgment Proposal` or `## Owner Action Proposal`) instead of expecting task/run metadata to stand in for the proposal.
- Preserve append-only integrity; never rewrite or delete history.
- Use explicit uncertainty language when evidence is incomplete.
</instructions>
