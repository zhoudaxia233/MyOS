# Cognition Module

## Purpose

This module is the cognitive adaptation layer of Personal Core OS.
It tracks how mental models (schemas) are used, where they fail, how they are revised, and whether revisions become more coherent over time.

## Scope

- Represent current schemas as inspectable, versioned records
- Log assimilation events: new input interpreted through current schemas
- Detect disequilibrium: contradictions, repeated confusion, and mismatch signals
- Log accommodation revisions: explicit schema restructuring operations
- Log equilibration cycles: whether revised schemas improve coherence
- Produce review outputs focused on cognitive evolution, not productivity output

## File Inventory

### Instructions and skills

- `modules/cognition/MODULE.md`: Module purpose, workflows, and loading rules
- `modules/cognition/module.manifest.yaml`: Routing keywords and planning defaults for orchestrator auto-discovery
- `modules/cognition/skills/log_schema.md`: Log or version a schema
- `modules/cognition/skills/log_assimilation.md`: Log an assimilation event
- `modules/cognition/skills/detect_disequilibrium.md`: Detect and log cognitive tension signals
- `modules/cognition/skills/log_accommodation.md`: Log an accommodation revision and optional new schema version
- `modules/cognition/skills/log_equilibration.md`: Log an equilibration cycle after revision
- `modules/cognition/skills/run_equilibration_review.md`: Weekly synthesis of schema evolution signals
- `modules/cognition/skills/review_timeline.md`: Build reflective cognitive evolution timeline output

### Canonical data (SSOT)

- `modules/cognition/data/schema_policy.yaml`: Schema quality requirements and minimum structure
- `modules/cognition/data/conflict_taxonomy.yaml`: Disequilibrium signal classes and interpretation criteria
- `modules/cognition/data/revision_operators.yaml`: Allowed accommodation operation types

### Logs (append-only JSONL)

- `modules/cognition/logs/schema_versions.jsonl`: Versioned schema records
- `modules/cognition/logs/assimilation_events.jsonl`: Input-to-schema interpretation events
- `modules/cognition/logs/disequilibrium_events.jsonl`: Productive cognitive tension events
- `modules/cognition/logs/accommodation_revisions.jsonl`: Explicit schema revision events
- `modules/cognition/logs/equilibration_cycles.jsonl`: Post-revision coherence checks

### Outputs

- `modules/cognition/outputs/`: Disequilibrium reports and cognitive evolution summaries

## Workflows

1. Log schema baseline
   - Add or version a schema before heavy interpretation cycles.
2. Log assimilation
   - Capture how new input is interpreted through an active schema.
3. Detect disequilibrium
   - Aggregate mismatch signals across decision/memory/profile logs.
4. Log accommodation
   - Record what failed and how the schema is being revised.
4a. Canonicalize learning candidate
   - `seed`: create a new canonical schema root with no parent lineage.
   - `revision`: extend an existing canonical schema lineage and require explicit `parent_schema_version_id`.
   - Never silently infer `seed` vs `revision` at ratification time.
   - The operator UI should guide this choice explicitly:
     - use `revision` only when the candidate genuinely continues an existing lineage
     - use `seed` when forcing an existing parent would distort lineage history
     - if revision is chosen, the owner must explicitly pick a real parent schema lineage
     - if revision is chosen, the owner must also state why the candidate belongs to that lineage rather than merely sharing a topic
     - if revision is chosen, the owner must explicitly classify the change (`refine`, `replace`, `weaken`, `split`, `merge`)
     - if revision type is `replace`, the owner must explicitly state whether the new schema `supersede`s the parent or should `keep-alongside`
     - if revision type is `weaken`, the owner must explicitly state whether the parent is `narrow`ed or should `keep-alongside`
     - `refine`, `split`, and `merge` must not carry parent-effect semantics
     - lineage viewing should surface this relation back as readable schema context, not only as a buried audit string
     - lineage viewing may also derive current governance state for existing schemas from active child revisions (`current`, `superseded`, `narrowed`, `alongside`)
     - lineage viewing may also derive a runtime-release posture from that governance state (`clear`, `hold`, `review_scope`, `review_coexistence`)
     - this runtime-release posture is guidance only; it must not silently release or revoke runtime authority
     - when a canonicalized cognition candidate is being marked runtime-eligible, Audit should surface that posture at the owner decision point
     - Audit may also surface that posture directly in the learning-candidate queue so runtime release can be triaged before opening detail
     - queue-level triage may filter canonicalized cognition candidates by runtime-release posture without changing runtime policy semantics
     - queue-level triage may also expose direct posture count chips so the owner can jump into `hold` / `review_scope` / `review_coexistence` / `clear` queues in one click
     - canonicalized/runtime candidates may also be surfaced in a dedicated inbox queue where non-`clear` cognition runtime posture is shown first by default
     - Audit may expose a small non-`current` lineage review list so owner can scan affected schemas directly
5. Log equilibration
   - Record whether revision improves explanatory and predictive coherence.
6. Weekly synthesis
   - Summarize recurrent tensions, revisions, and unresolved topics.
7. Reflective timeline
   - Build longitudinal event view of schema evolution.

## Progressive Loading Rules (Required)

- For schema logging: load `log_schema.md`, `schema_policy.yaml`, and `schema_versions.jsonl`.
- For assimilation: load `log_assimilation.md`, latest schema versions, and `assimilation_events.jsonl`.
- For disequilibrium detection: load `detect_disequilibrium.md`, `conflict_taxonomy.yaml`, and relevant cross-module logs.
- For accommodation logging: load `log_accommodation.md`, `revision_operators.yaml`, recent schema versions, and accommodation logs.
- For equilibration logging: load `log_equilibration.md`, schema + accommodation + disequilibrium logs.
- Do not load content templates or unrelated artifacts unless explicitly requested.

<instructions>
- Treat disequilibrium as a high-value signal for model revision, not as noise.
- Separate observations from interpretations in every record.
- Every inference-level record should include `source_refs`.
- Keep schema revisions explicit: what failed, what changed, what improved.
- `revision` requires explicit parent lineage.
- `revision` should carry explicit lineage justification in the audit path.
- `revision` should carry explicit revision type in the audit path.
- `replace` / `weaken` revisions should carry explicit parent-effect semantics in the audit path.
- `seed` must not carry parent lineage and must not write accommodation semantics.
- Guidance may help the owner choose, but the system must not silently decide `seed` vs `revision`.
- Preserve append-only history across all cognition logs.
</instructions>
