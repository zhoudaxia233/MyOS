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
- `seed` must not carry parent lineage and must not write accommodation semantics.
- Guidance may help the owner choose, but the system must not silently decide `seed` vs `revision`.
- Preserve append-only history across all cognition logs.
</instructions>
