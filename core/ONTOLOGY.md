# Core Ontology

This file defines the first-class judgment objects of Personal Core OS.

## Purpose

- Keep judgment continuity stable under delegated execution.
- Prevent semantic overlap across modules.
- Enforce one primary home for each new record.

## Object Classes

### Memory

- **Is**: an evidence ledger of what was observed, captured, or distilled.
- **Is not**: a policy authority or identity baseline.
- **Belongs here**:
  - raw events
  - distilled insights with evidence
  - observed recurring patterns
- **Must not go here**:
  - commitments and approvals
  - constitutional constraints
  - schema revision records
- **Stability**: highly dynamic
- **Type**: descriptive

### Decision

- **Is**: a commitment and governance ledger of what was chosen, blocked, approved, overridden, and reviewed.
- **Is not**: a raw observation archive.
- **Belongs here**:
  - decisions and alternatives
  - precommit checks and gate outcomes
  - guardrail overrides and failure post-mortems
  - audit outcomes and owner escalation todos
- **Must not go here**:
  - stable owner traits
  - constitutional clauses
  - schema operators and model lineage
- **Stability**: dynamic (append-only historical records)
- **Type**: normative + audit

### Profile

- **Is**: the owner operating model (stable traits, defaults, sensitivities, and working preferences).
- **Is not**: a global constitution or event dump.
- **Belongs here**:
  - long-horizon owner traits and defaults
  - trigger maps and stabilizers
  - profile-level change rationale
- **Must not go here**:
  - one-off events
  - tactical per-case decisions
  - non-negotiable constitutional constraints
- **Stability**: semi-stable
- **Type**: descriptive + normative defaults

### Cognition

- **Is**: the schema evolution layer (interpretive model use, failure, revision, and stabilization).
- **Is not**: generic note summaries or preference storage.
- **Belongs here**:
  - schema versions
  - assimilation fit logs
  - disequilibrium signals
  - accommodation revisions
  - equilibration checks
- **Must not go here**:
  - tactical commitments
  - owner preference defaults
  - raw evidence without interpretation context
- **Stability**: dynamic event stream + semi-stable schema versions
- **Type**: interpretive

### Principle / Constitution

- **Is**: the governing charter for enduring direction and override-resistant constraints.
- **Is not**: a preference list or temporary heuristic file.
- **Belongs here**:
  - cross-domain directional constraints
  - constitutional clauses and rationale
  - amendment policies and exception protocols
- **Must not go here**:
  - mood-driven short-term rules
  - single-case tactics
  - unratified observations
- **Stability**: relatively stable
- **Type**: governing

## Ownership Rule

Each incoming record must have one primary home.

- Secondary relevance is represented by `source_refs`, not by duplication.
- Cross-module synthesis must reference IDs only.

## Update Authority

- Memory: append-only by agent workflows.
- Decision: append-only by decision workflows and gates.
- Profile: revision-based with explicit change log.
- Cognition: append-only lineage records.
- Principles: amendment-based updates with owner approval.
