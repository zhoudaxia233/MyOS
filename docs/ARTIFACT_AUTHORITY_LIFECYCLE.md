# Artifact Authority Lifecycle Contract

Date ratified: 2026-03-14

This document defines what artifact review, promotion, canonical truth, runtime eligibility, and runtime-active authority mean in MyOS.

It exists to stop one overloaded word, `promotion`, from carrying four different meanings at once.

## Purpose

Use this contract when evaluating or implementing any learning, governance, or runtime behavior involving:

- `insight`
- `rule`
- `skill`
- `profile_trait`
- `principle`
- `cognition_revision`
- memory-only imported artifacts

## Non-Negotiable Meanings

1. Promotion means owner-endorsed ledger state.
   - Promotion records that the owner approved an artifact as worth preserving in governed history.
   - Promotion does not, by itself, mean canonical SSOT update.
   - Promotion does not, by itself, mean runtime-active authority.
2. Canonical truth lives only in canonical homes.
   - Canonical truth means the artifact has been ratified into its module's SSOT or versioned canonical lineage.
   - Canonical homes are the module SSOT files and canonical lineage logs, not generic promotion sinks.
3. Runtime authority is separate from promotion and separate from canonicalization.
   - Runtime use requires explicit runtime eligibility.
   - Runtime activity is derived from eligibility + maturity + scope match + actual selection during a run.
4. Higher-seriousness artifacts require additional ratification before they may affect judgment core.
   - `profile_trait`, `principle`, and `cognition_revision` are not allowed to become de facto judgment-core truth merely by being promoted.
5. Append-only history is never erased.
   - Review, promotion, canonicalization, runtime authorization, revocation, and retirement must all preserve historical trail.

## Strictness Classes

### Class A: Descriptive memory artifacts

- `memory_event`
- `memory_insight`
- `insight`

These are descriptive and evidence-oriented. They may inform future work, but they do not define judgment core by default.

### Class B: Operational guidance artifacts

- `rule`
- `skill`

These can influence execution behavior, but promotion alone still does not make them canonical policy.

### Class C: Core-self artifacts

- `profile_trait`
- `principle`
- `cognition_revision`

These touch the owner's baseline, constitution, or schema layer. They require typed ratification before canonical truth or runtime authority.

## Unified State Model

Use one primary authority lifecycle plus one runtime overlay.

### Primary authority lifecycle

1. `imported_evidence`
   - Raw or distilled descriptive material.
   - Retrieval-visible, but not owner-endorsed.
2. `candidate_pending_review`
   - Typed artifact proposal waiting for owner judgment.
3. `reviewed_accept`
   - Owner says the artifact is directionally valid and may be promoted.
4. `reviewed_modify`
   - Owner rejects the current wording and spawns a replacement candidate.
5. `reviewed_reject`
   - Owner rejects the artifact from further authority growth.
6. `promoted_ledger`
   - Owner-endorsed append-only artifact preserved in the proper promotion sink.
   - This is not yet canonical unless the type contract says otherwise.
7. `canonicalized`
   - Ratified into canonical SSOT or canonical lineage home.
8. `retired`
   - No longer current for future use, but preserved historically.

### Runtime overlay

1. `runtime_na`
   - No runtime use path exists or should exist.
2. `holding`
   - Artifact exists, but runtime injection is not currently authorized.
3. `eligible`
   - Explicit runtime authorization exists.
4. `active`
   - Derived state only.
   - Means `eligible` + maturity satisfied + scope matched + selected into a run.
5. `revoked`
   - Runtime authorization has been explicitly withdrawn.

### Transition rules

- `imported_evidence -> candidate_pending_review`
  - Only when an explicit typed candidate is created.
- `candidate_pending_review -> reviewed_accept|reviewed_modify|reviewed_reject`
  - Only through owner review.
- `reviewed_accept -> promoted_ledger`
  - Only through explicit approval/promotion action.
- `promoted_ledger -> canonicalized`
  - Only through type-specific ratification path.
- `promoted_ledger|canonicalized -> holding|eligible|revoked`
  - Only through explicit runtime eligibility path when the type contract permits it.
- `eligible -> active`
  - Derived during execution; not a direct write.
- `canonicalized -> retired`
  - Only through superseding canonical update, amendment, or typed retirement path.

## Type Contract By Artifact Type

### Memory-only imported artifacts

This includes direct `memory_events` and `memory_insights` created by ingest flows.

- Candidate means:
  - Not applicable by default.
  - Imported memory artifacts are evidence, not candidate authority objects.
- Accept/review means:
  - Not required for evidence storage.
- Promote means:
  - Not applicable unless a separate typed candidate is extracted from the memory.
- Canonical SSOT update:
  - Never. Memory events/insights are descriptive ledger material, not SSOT.
- Runtime eligibility:
  - Not through the learning promotion path.
  - They may still be retrieval-visible as evidence.
- Separate ratification required:
  - Yes, if they are later elevated into `insight`, `rule`, `profile_trait`, `principle`, or `cognition_revision`.
- Runtime-active use without explicit eligibility:
  - No, as governed runtime authority.
- Rollback/revocation means:
  - Archive only if needed; do not delete.
  - If the evidence was over-read, correct the downstream promoted artifact rather than erasing the evidence.

### Insight

- Candidate means:
  - A proposed reusable observation or distilled memory artifact.
- Accept/review means:
  - The owner agrees the observation is worth preserving as an endorsed reusable artifact.
- Promote means:
  - Write the artifact into append-only promoted memory sink state.
  - Meaning: owner-endorsed memory artifact, not canonical self-core truth.
- Canonical SSOT update:
  - No by default.
  - `insight` has no mandatory canonical YAML target in the current repo.
- Runtime eligibility:
  - May be created automatically on promotion as `suggest_only`.
  - This is acceptable because insight remains descriptive and non-binding.
- Separate ratification required:
  - Only if the insight is later elevated into a stronger layer such as profile, principle, or decision heuristic.
- Runtime-active use without explicit eligibility:
  - Never.
- Rollback/revocation means:
  - Revoke runtime eligibility if the insight should stop influencing runs.
  - Keep promotion history intact.

### Rule

- Candidate means:
  - A proposed tactical heuristic, execution rule, or bounded behavioral check.
- Accept/review means:
  - The owner agrees the rule is directionally sound enough to preserve and possibly use.
- Promote means:
  - Write the rule into append-only promoted decision-rule sink state.
  - Meaning: owner-endorsed operational guidance artifact.
- Canonical SSOT update:
  - No by default.
  - Canonicalization requires an additional typed decision:
    - heuristic-level rule -> `modules/decision/data/heuristics.yaml`
    - guardrail-level rule -> `modules/decision/data/impulse_guardrails.yaml` or `domain_guardrails.yaml`
- Runtime eligibility:
  - May be created automatically on promotion as `suggest_only`.
- Separate ratification required:
  - Yes, for canonical policy status.
- Runtime-active use without explicit eligibility:
  - Never.
- Rollback/revocation means:
  - Revoke runtime eligibility to stop injection.
  - If canonicalized later, supersede the canonical rule through explicit file update and keep the old ledger artifact historical.

### Skill

- Candidate means:
  - A proposed reusable procedure or operator pattern.
- Accept/review means:
  - The owner agrees the procedure concept is useful enough to preserve.
- Promote means:
  - Write the skill into append-only promoted skill sink state.
  - Meaning: owner-endorsed procedure concept.
- Canonical SSOT update:
  - No by default.
  - Canonicalization requires materializing the procedure into an explicit skill artifact, usually a concrete `modules/<target>/skills/*.md` workflow.
- Runtime eligibility:
  - May be created automatically on promotion as `suggest_only`.
  - Promotion alone does not make the skill an executable canonical capability.
- Separate ratification required:
  - Yes, for canonical executable-skill status.
- Runtime-active use without explicit eligibility:
  - Never.
- Rollback/revocation means:
  - Revoke runtime eligibility to stop suggestion injection.
  - If a canonical skill file was created later, retire or supersede that skill explicitly rather than deleting history.

### Profile Trait

- Candidate means:
  - A proposed change to stable owner traits, defaults, sensitivities, or stabilizers.
- Accept/review means:
  - The owner agrees the trait proposal is serious enough to preserve for ratification consideration.
- Promote means:
  - Write the trait into append-only promoted profile-trait sink state.
  - Meaning: owner-endorsed trait proposal, not owner baseline yet.
- Canonical SSOT update:
  - No by default.
  - Canonicalization requires explicit profile update path:
    - current implemented path: `psych_profile.yaml` `ratified_traits`
    - broader future targets may include `identity.yaml` or `operating_preferences.yaml`
    - corresponding `profile_changes.jsonl` record
- Runtime eligibility:
  - Must not become runtime-eligible merely because it is promoted.
  - Current implemented contract: remain `holding` until canonicalized.
  - After canonicalization, runtime release may be granted only through a separate explicit eligibility action.
- Separate ratification required:
  - Yes, always.
- Runtime-active use without explicit eligibility:
  - Never.
- Rollback/revocation means:
  - Revoke any runtime eligibility if it had been granted.
  - If canonicalized, supersede via new `profile_changes.jsonl` event plus targeted YAML update.

### Principle

- Candidate means:
  - A proposed constitutional clause or durable cross-domain governing constraint.
- Accept/review means:
  - The owner agrees the proposal is worthy of amendment consideration.
- Promote means:
  - Write the principle into append-only promoted principle sink state.
  - Meaning: owner-endorsed amendment candidate, not constitution yet.
- Canonical SSOT update:
  - No by default.
  - Canonicalization requires principle amendment or exception path:
    - `principle_amendments.jsonl` and targeted `constitution.yaml` update
    - or `principle_exceptions.jsonl` for time-bounded deviation
- Runtime eligibility:
  - Must not be granted merely from promotion.
  - Desired contract: runtime principle authority should come from canonical constitution/exception records, not generic promoted candidate sinks.
- Separate ratification required:
  - Yes, always.
- Runtime-active use without explicit eligibility:
  - Never.
- Rollback/revocation means:
  - Revoke runtime eligibility if any was granted.
  - Canonical rollback must happen through amendment/supersession or exception closure, never by deleting prior clause history.

### Cognition Revision

- Candidate means:
  - A proposed schema revision, interpretive patch, or new model of disequilibrium/accommodation.
- Accept/review means:
  - The owner agrees the revision deserves explicit schema-ratification work.
- Promote means:
  - Write the cognition revision into append-only promoted cognition sink state.
  - Meaning: owner-endorsed schema proposal, not active schema lineage yet.
- Canonical SSOT update:
  - No by default.
  - Canonicalization requires explicit cognition lineage write:
    - `canonicalization_mode=seed` creates a new canonical root in `schema_versions.jsonl`
    - `canonicalization_mode=revision` requires explicit `parent_schema_version_id`
    - revision mode may append `accommodation_revisions.jsonl`
- Runtime eligibility:
  - Must not be granted merely from promotion.
  - Current implemented contract: remain `holding` until explicit schema-ratification path is completed.
  - After canonicalization, runtime release may be granted only through a separate explicit eligibility action.
- Separate ratification required:
  - Yes, always.
- Runtime-active use without explicit eligibility:
  - Never.
- Rollback/revocation means:
  - Revoke runtime eligibility if any existed.
  - Supersede with a later schema version or accommodation record rather than erasing history.

## Canonicalization Targets

When an artifact becomes canonical, its authority home must be explicit:

- `insight`
  - no default canonical home required
- `rule`
  - `modules/decision/data/heuristics.yaml`
  - or stricter guardrail files when the rule is truly guardrail-level
- `skill`
  - explicit skill file under `modules/<target>/skills/`
- `profile_trait`
  - `modules/profile/data/identity.yaml`
  - `modules/profile/data/operating_preferences.yaml`
  - `modules/profile/data/psych_profile.yaml`
  - plus `modules/profile/logs/profile_changes.jsonl`
- `principle`
  - `modules/principles/data/constitution.yaml`
  - plus `modules/principles/logs/principle_amendments.jsonl`
  - or `principle_exceptions.jsonl` for temporary deviation
- `cognition_revision`
  - `modules/cognition/logs/schema_versions.jsonl`
  - and/or `accommodation_revisions.jsonl`

## Current Repo Mapping

Today the repo already implements these layers:

- candidate queue:
  - `orchestrator/logs/learning_candidates.jsonl`
- owner review:
  - `modules/decision/logs/learning_candidate_verdicts.jsonl`
- approval + promotion:
  - `modules/decision/logs/learning_candidate_approvals.jsonl`
  - `modules/decision/logs/learning_candidate_promotions.jsonl`
- type-specific promotion sinks:
  - `modules/memory/logs/insight_candidates.jsonl`
  - `modules/decision/logs/rule_candidates.jsonl`
  - `modules/decision/logs/skill_candidates.jsonl`
  - `modules/profile/logs/profile_trait_candidates.jsonl`
  - `modules/cognition/logs/schema_candidates.jsonl`
  - `modules/principles/logs/principle_candidates.jsonl`
- runtime overlay:
  - `modules/decision/logs/runtime_eligibility.jsonl`
  - active injection derived by `orchestrator/src/loader.py`

What is not yet generic in the repo:

- a first-class canonicalization record layer for promoted artifacts
- a single derived field that distinguishes `promoted_ledger` from `canonicalized`
- canonicalization-backed runtime release path for high-seriousness artifacts after ratification

## Implementation Note: First Hard Typed Guard (2026-03-14)

This contract is now partially enforced in code at the generic runtime-authority boundary:

- generic promotion still creates append-only runtime eligibility records for all promoted artifacts
- but `profile_trait`, `principle`, and `cognition_revision` are forced to remain `holding`
- the generic `set_runtime_eligibility` path now refuses to mark those three types `eligible`
- the resulting meaning is explicit:
  - promotion preserves owner-endorsed ledger history
  - runtime authority for Class C artifacts remains blocked until a future typed ratification/canonicalization path exists

What remains deferred:

- explicit canonicalization / ratification records
- typed owner UX for ratifying `profile_trait`, `principle`, and `cognition_revision`
- canonical-source-backed runtime release for those artifact types

## Implementation Note: First Principle Canonicalization Path (2026-03-14)

The repo now has a first explicit Class C ratification path, but only for `principle`:

- scope is intentionally narrow:
  - only promoted `principle` candidates
  - only `add_clause` style canonicalization
- the path writes:
  - one append-only amendment record in `modules/principles/logs/principle_amendments.jsonl`
  - one targeted clause append into `modules/principles/data/constitution.yaml`
- this means:
  - `principle` can now move from `promoted_ledger` to `canonicalized` through an explicit owner action
  - constitutional authority comes from `constitution.yaml` + amendment trail, not from runtime eligibility on the promoted candidate sink
- follow-up guard now in code:
  - a canonicalized `principle` may be explicitly marked runtime-eligible
  - but that release still does not happen automatically at ratification time
  - runtime authority therefore remains a separate owner action after canonical truth exists
- what remains deferred:
  - amendment of existing clauses
  - exception-driven canonicalization flows from promoted candidates
  - equivalent ratification paths for `profile_trait` and `cognition_revision`

## Implementation Note: First Profile Trait Canonicalization Path (2026-03-14)

The repo now has a second explicit Class C ratification path for `profile_trait`:

- scope is intentionally narrow:
  - only promoted `profile_trait` candidates
  - only append into `psych_profile.yaml` `ratified_traits`
- the path writes:
  - one append-only canonicalization record in `modules/profile/logs/profile_changes.jsonl`
  - one targeted trait append into `modules/profile/data/psych_profile.yaml`
- this means:
  - `profile_trait` can now move from `promoted_ledger` to `canonicalized` through an explicit owner action
  - profile baseline authority comes from `psych_profile.yaml` + `profile_changes.jsonl`, not from generic promoted candidate sinks
- follow-up guard now in code:
  - a canonicalized `profile_trait` may be explicitly marked runtime-eligible
  - but that release still does not happen automatically at ratification time
  - runtime authority therefore remains a separate owner action after canonical self-model truth exists
- what remains deferred:
  - canonical writes into `identity.yaml` or `operating_preferences.yaml`
  - typed supersession/edit flows for already-canonical profile traits
  - equivalent ratification path for `cognition_revision`

## Implementation Note: First Cognition Revision Canonicalization Path (2026-03-14)

The repo now has a third explicit Class C ratification path for `cognition_revision`:

- scope is intentionally narrow:
  - only promoted `cognition_revision` candidates
  - explicit `canonicalization_mode` is now required at ratification time
  - `seed` creates a new canonical schema root
  - `revision` requires explicit `parent_schema_version_id`
- the path writes:
  - `seed` writes one new canonical record in `modules/cognition/logs/schema_versions.jsonl`
  - `revision` writes one new canonical schema version and one append-only revision record in `modules/cognition/logs/accommodation_revisions.jsonl`
- this means:
  - `cognition_revision` can now move from `promoted_ledger` to `canonicalized` through an explicit owner action
  - cognition authority comes from schema lineage logs, not from generic promoted candidate sinks
  - the system no longer silently infers `seed` vs `revision`
- follow-up guard now in code:
  - a canonicalized `cognition_revision` may be explicitly marked runtime-eligible
  - but that release still does not happen automatically at ratification time
  - runtime authority therefore remains a separate owner action after canonical schema lineage exists
- owner guidance now in code:
  - Audit exposes explicit `Ratify Schema Seed` vs `Ratify Schema Revision` guidance at the decision point
  - revision ratification now uses a visible parent-lineage selector with schema summary context
  - revision ratification now also requires explicit lineage justification: why the candidate belongs to that lineage rather than merely sharing a topic
  - revision ratification now also requires explicit `revision_type`; the system no longer defaults cognition revisions to `refine`
  - `replace` and `weaken` revisions now also require explicit `parent_effect` in the audit path:
    - `replace` must say whether the new schema `supersede`s the parent or should `keep-alongside`
    - `weaken` must say whether the parent is `narrow`ed or should `keep-alongside`
    - `refine`, `split`, and `merge` must not carry parent-effect semantics
  - the UI guides the owner toward the right choice, but still does not infer `seed` vs `revision`
- what remains deferred:
  - candidate-taxonomy split between schema-seed vs schema-revision artifacts
  - broader lineage browser / graph exploration beyond the current parent selector
  - richer lineage-effect ontology beyond the current narrow `parent_effect` audit field

## Near-Term Guardrails

Until a dedicated canonicalization layer exists:

- do not interpret `promoted_total` as canonical truth count
- do not interpret runtime-active injection as canonical truth
- do not treat `candidate_state` inside `learning_candidates.jsonl` as the full lifecycle source of truth
- derive lifecycle from verdict + promotion + runtime eligibility logs

## Decision Rule For Future Changes

Any future implementation touching artifact authority should answer these questions explicitly:

1. Is this change only review state, or is it changing authority?
2. If authority changes, is it only `promoted_ledger`, or is it canonicalizing into SSOT?
3. If runtime behavior changes, where is the explicit runtime eligibility decision recorded?
4. For Class C artifacts, what is the ratification path before judgment-core use?

If those answers are unclear, the change should not be implemented yet.
