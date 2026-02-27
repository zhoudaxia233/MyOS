# Personal Core OS Roadmap

## Context Summary (from current conversations)

This project exists to become a **stable personal operating center for AI agents**, not a one-off automation script collection.

Key intent:

- Separate **execution** from **judgment**
- Let agents run workflows while preserving long-term direction
- Keep architecture modular and low-coupled
- Reduce short-term noise by grounding actions in stable memory and priorities

## What We Have Already Built (v0.1)

- File-based kernel in `core/` (routing + rules + schemas + glossary)
- Plugin modules in `modules/`
  - `content`: content workflow, voice SSOT, anti-patterns, templates, logs
  - `decision`: decision/failure/experience logs + weekly review skill
  - `_template`: starter module scaffold
- Append-only JSONL logs with schema header line
- Acceptance checklist: `CHECKLIST.md`
- Safe JSONL append utility: `scripts/append_jsonl.sh`

## Clarified User Questions and Decisions

### 1) "Why is this a project if it's mostly Markdown?"

Decision:

- This repo is the **control plane** (protocol + memory layout), not the runtime engine.
- Runtime execution is done by AI agents/tools that read this repo.

### 2) "Where are API calls?"

Decision:

- v0.1 intentionally keeps no API dependency.
- First goal is stable structure and operating protocol.
- API-driven orchestration can be added later without changing module semantics.

### 3) "How does context work?"

Decision:

- Use strict progressive disclosure:
  - Hop 1: `core/ROUTER.md`
  - Hop 2: `modules/<name>/MODULE.md`
  - Hop 3: only task-specific data files

### 4) "Where is my personal profile in the system?"

Decision:

- v0.1 is foundational and not deeply personalized yet.
- v0.2 should add explicit user profile + evolving memory modules.

### 5) "Can this evolve with my changing thinking?"

Decision:

- Yes. Keep kernel stable, evolve data and heuristics via append-only logs and periodic reviews.

## v0.2 Priorities (Next)

1. Add personal profile module
   - Goals, values, constraints, temperament triggers
   - "Do / don't" operating preferences
2. Add memory distillation module
   - Capture daily conversations/reflections
   - Produce weekly/monthly distilled memory snapshots
3. Add impulse guardrails in decisions
   - Pre-commit checks for high-risk decisions
   - Cooldown/second-check fields
4. Add lightweight runner (optional)
   - Build minimal context bundles automatically from route + module + task

## v0.3+ Direction

- Optional API orchestrator for automated ingestion and scheduled reviews
- Optional retrieval layer/vector index for large-scale historical memory
- Optional dashboards generated from logs (still file-first)

## Success Criteria

- Actions increasingly align with long-term priorities
- Fewer repeated decision mistakes
- Faster execution with less cognitive overhead
- Clear audit trail of why decisions were made and how heuristics evolved
