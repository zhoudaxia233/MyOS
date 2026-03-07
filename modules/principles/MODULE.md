# Principles Module

## Purpose

This module is the constitutional governance layer of Personal Core OS.
It stores enduring directional constraints, amendment rules, and exception trails so delegated execution remains aligned with long-term judgment.

## Scope

- Maintain constitutional clauses as governing SSOT
- Define amendment criteria and approval protocol
- Record principle amendment proposals and decisions
- Record principle exception requests and closures
- Produce owner-facing constitutional drift and exception audit outputs

## File Inventory

### Instructions and skills

- `modules/principles/MODULE.md`: Module purpose, workflows, and loading rules
- `modules/principles/module.manifest.yaml`: Routing keywords and planning defaults for orchestrator auto-discovery
- `modules/principles/skills/propose_amendment.md`: Propose and record constitutional amendment changes
- `modules/principles/skills/log_principle_exception.md`: Log principle exception request and decision trail
- `modules/principles/skills/run_constitutional_audit.md`: Generate constitutional drift and exception digest

### Canonical data (SSOT)

- `modules/principles/data/constitution.yaml`: Governing clauses and rationale
- `modules/principles/data/amendment_policy.yaml`: Admission criteria and amendment workflow

### Logs (append-only JSONL)

- `modules/principles/logs/principle_amendments.jsonl`: Amendment proposals, approvals, and effective changes
- `modules/principles/logs/principle_exceptions.jsonl`: Exception requests, approvals, and closure status

### Outputs

- `modules/principles/outputs/`: Constitutional audits and owner review artifacts
- `modules/principles/outputs/templates/constitutional_audit_report.md`: Report structure template

## Workflows

1. Amendment proposal
   - Evaluate proposal against amendment policy.
   - Record proposal and evidence references.
   - Require owner approval before constitution update.
2. Constitutional update
   - Apply targeted edits to `constitution.yaml` only after approved amendment record exists.
3. Principle exception logging
   - Record temporary exception context, risk acknowledgment, owner confirmation, and expiry.
4. Constitutional audit
   - Summarize amendment/exception trends and unresolved risks.
   - Produce owner-facing report with concrete actions.

## Progressive Loading Rules (Required)

- For amendment proposals: load `propose_amendment.md`, `constitution.yaml`, `amendment_policy.yaml`, and `principle_amendments.jsonl`.
- For exception logging: load `log_principle_exception.md`, `constitution.yaml`, `amendment_policy.yaml`, and `principle_exceptions.jsonl`.
- For constitutional audits: load `run_constitutional_audit.md`, both principle logs, and audit template.
- Do not load unrelated module files unless explicit cross-module synthesis is requested.

<instructions>
- Treat constitutional clauses as governing, not advisory defaults.
- Keep amendments explicit: what changed, why, and approval reference.
- Keep exceptions explicit: scope, duration, risk, and owner confirmation.
- Preserve append-only history in all principle logs.
- Use cross-module IDs only; never duplicate canonical content.
</instructions>
