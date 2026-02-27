# Personal Core OS Roadmap

## Project Intent

Build a stable personal operating center for AI agents, where execution scales through automation but long-term judgment remains coherent.

Core direction:

- Separate execution from judgment
- Preserve personal alignment over time
- Keep architecture modular and low-coupled
- Reduce short-term noise with structured memory and guardrails

## Version Timeline

## v0.1 (Completed)

- Kernel in `core/`:
  - Routing, rules, schemas, glossary
- Modules:
  - `content` (voice, anti-patterns, templates, logs)
  - `decision` (decisions, failures, experiences, weekly review)
- Safety foundations:
  - Append-only JSONL discipline
  - Schema header rule
  - `append_jsonl.sh`
- Documentation:
  - `README.md`, `README-zh.md`, `CHECKLIST.md`

## v0.2 (Completed)

- Added `profile` module:
  - Personal north star, values, preferences, boundaries
  - Profile changes and trigger event logs
  - Alignment check workflow
- Added `memory` module:
  - Daily memory event ingestion
  - Insight extraction and weekly distillation workflow
- Extended `decision` module:
  - Impulse guardrails (`impulse_guardrails.yaml`)
  - Precommit checks log and skill
- Added context planner utility:
  - `scripts/context_bundle.sh` for route + minimal file bundle

## v0.3 (Next)

1. Orchestration layer
   - Optional API runner to execute route/module workflows automatically
   - Configurable task entry points
2. Retrieval and scale
   - Optional index/retrieval layer for large history
   - Chunking and reference policies for long logs
3. Personal adaptation loop
   - Scheduled profile/memory calibration prompts
   - Drift detection between daily actions and north-star goals
4. Safety hardening
   - Domain-specific guardrails (invest/project/content)
   - Escalation thresholds and override audits

## Operating Principles for Future Versions

- Keep kernel small and stable
- Keep modules independent and replaceable
- Preserve append-only historical integrity
- Prefer explicit IDs and references over duplicated content
- Optimize for progressive disclosure and low context cost

## Success Signals

- Faster execution with less context confusion
- Fewer repeated mistakes in high-risk decisions
- Better alignment between weekly actions and long-term direction
- Clear audit trail of what changed, why it changed, and what improved
