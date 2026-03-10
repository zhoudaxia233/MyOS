# MyOS Positioning Charter

Date ratified: 2026-03-10

This charter is the long-term positioning and architecture baseline for MyOS.
Roadmap updates, UX changes, and implementation proposals should be evaluated against this document first.

## Core Positioning

MyOS is a thin, model-agnostic cyber-self layer that preserves the owner's judgment core, learns through audited absorption, and attaches seamlessly to external intelligence systems.

MyOS is not intended to become:

- a foundation model replacement
- a generic AI app shell
- a generic RAG chatbot
- a monolithic agent platform
- a clone of broad "do everything" automation systems

## What "Cyber-Self" Means

The cyber-self is not a static profile or memory vault.
It is a governable personal layer with four responsibilities:

- personal judgment layer
- personal learning layer
- personal governance layer
- personal delegation layer

Goal:

- preserve judgment continuity
- enable owner-reviewed growth
- keep behavior transparent and corrigible

Non-goal:

- blind imitation
- silent style drift
- frozen bias preservation

## Design Principles

1. Thin, not heavy
   - Do not rebuild commodity model reasoning, generic orchestration, generic tool-use infrastructure, or provider-native ecosystems.
   - Focus on judgment continuity, governance, promotion logic, and delegation policy.
2. Model-agnostic by design
   - Keep providers replaceable.
   - Avoid lock-in to a single provider memory/persona/tool framework.
3. Preserve judgment core
   - Protect principles, defaults, heuristics, anti-patterns, risk boundaries, style invariants, and drift definitions from noisy overwrite.
4. Learn through audited absorption
   - Require candidate extraction, owner review, promotion or rejection, and revision history.
   - No silent direct promotion into long-term truths.
5. Operator clarity first
   - Keep a clear three-entrypoint model:
     - Task Console
     - Learning / Evolution Console
     - Audit Console
6. Transparency before autonomy
   - Required path: suggestion -> audit -> learning -> partial delegation -> bounded low-risk autonomy.
   - Do not jump to black-box autonomy.

## Three-Layer Architecture Baseline

1. Self Core (protected)
   - principles
   - approved defaults/rules/skills
   - anti-patterns and risk boundaries
   - promoted schemas and stable profile traits
2. Learning Membrane (evolution gateway)
   - external ingest
   - candidate extraction
   - owner review and verdict
   - promotion/rejection with history
3. Model/Agent Adapter Layer (replaceable attachment)
   - handoff packets
   - provider adapters and runtime injection
   - suggestion traces
   - delegation gating
   - tool/skill attachment and future ecosystem integration

## Preservation Mandate

Existing extraction and distillation pipelines are foundational and must be preserved as first-class substrate:

- conversation rule extraction
- repeated-pattern and skill extraction
- learning ingestion
- memory distillation
- decision-pattern extraction
- cognition-signal extraction

These pipelines should feed candidate generation, review, promotion, and long-term refinement.
They should not be deprecated as architecture gets cleaner.

## Low-Cost Learning Handoff Requirement

Learning should support a transparent low-cost path for expensive source analysis:

1. Owner provides source
2. MyOS generates Learning Handoff Packet
3. External LLM performs analysis
4. Owner pastes response back
5. MyOS extracts candidate artifacts
6. Owner reviews and promotes

## Architectural Red Lines

Avoid the following failure modes:

- generic note-taking product drift
- generic RAG chatbot drift
- monolithic assistant platform drift
- single-provider lock-in
- silent overwrite from noisy material
- black-box suggestion or action paths
- weakening extraction/distillation substrate
- thickening MyOS by rebuilding commodity infrastructure
- confusing tool power with cyber-self quality

## Decision Gate For All Proposals

Every roadmap/architecture/implementation proposal should answer this question:

Does this strengthen MyOS as a thin, model-agnostic cyber-self layer that preserves judgment core, learns through audited absorption, and attaches cleanly to external intelligence systems?

If no, treat it as likely drift and redesign before implementation.

## Working Rules Derived From This Charter

- Use promoted and approved artifacts for runtime behavior; raw candidates remain non-authoritative.
- Keep every learning and governance step auditable and append-only.
- Keep interfaces adapter-friendly so provider swaps do not break cyber-self continuity.
- Expand delegation gradually and only within explicit risk boundaries.
