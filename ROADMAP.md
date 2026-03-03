# Personal Core OS Roadmap

## Project Intent

Build a stable personal operating center for AI agents, where execution scales but judgment remains coherent, auditable, and aligned with long-term direction.

## Version Timeline

## v0.1 (Completed)

- Kernel in `core/` (routing, rules, schemas, glossary)
- Modules: `content`, `decision`, `_template`
- Append-only JSONL discipline and schema header rule
- Base docs and safe append script

## v0.2 (Completed)

- Added `profile` module (identity + preferences)
- Added `memory` module (ingest + weekly distill)
- Added decision impulse guardrails and precommit workflow
- Added `context_bundle.sh` for route + minimal file planning

## v0.3-first (Completed)

- Profile cyberization layer:
  - `psych_profile.yaml`
  - `psych_observations.jsonl`
  - `profile_snapshot.md`
- Memory paradigm layer:
  - `pattern_taxonomy.yaml`
  - `chat_patterns.jsonl`
  - `extract_chat_patterns.md`
- Decision audit layer:
  - `audit_rules.yaml`
  - `audit_decision_system.md`
  - `decision_audit_report.md` template
- Cadence runbook:
  - `routines/cadence.yaml`
  - `routines/CADENCE.md`
  - `scripts/run_cycle.sh`

## v0.3-orchestrator (Completed)

- Added dedicated `orchestrator/` subsystem as high-level execution engine
- Layered architecture in `orchestrator/src/`:
  - router, loader, planner, runner, writer, validators
  - providers: manual + optional openai
- Added orchestrator runtime logs:
  - `orchestrator/logs/runs.jsonl`
- Added CLI:
  - `inspect` for route/plan visibility
  - `run` for execution packet (manual) or provider-based generation

## v0.4-retrieval (Completed)

1. Retrieval scaling
   - Added index builder and lexical search in orchestrator CLI
   - Added retrieval config and derived index path
   - Added retrieval query logs (`orchestrator/logs/retrieval_queries.jsonl`)
   - Added retrieval-augmented run mode (`--with-retrieval`)

## v0.4-scheduling (Completed)

1. Automation scheduling
   - Added cadence loader and cycle execution command (`schedule-run`)
   - Reads `routines/cadence.yaml` as scheduling SSOT
   - Added schedule execution logs (`orchestrator/logs/schedule_runs.jsonl`)
   - Added cron hint mode for non-executing scheduling integration

## v0.5-drift (Completed)

1. Drift dashboards
   - Added quantitative metrics command (`orchestrator src/main.py metrics`)
   - Added dashboard report generation for 7/30-day windows
   - Added snapshot logs (`orchestrator/logs/metrics_snapshots.jsonl`)
   - Metrics include precommit coverage, cooldown compliance, repeat failure rate, and profile drift rate

## v0.5-guardrails (Completed)

1. Guardrail hardening
   - Added domain policy file (`modules/decision/data/domain_guardrails.yaml`)
   - Added guardrail override audit log (`modules/decision/logs/guardrail_overrides.jsonl`)
   - Added orchestrator command (`guardrail-check`) for policy evaluation
   - Added override logging path with owner confirmation requirements

## v0.6-owner-report (Completed)

1. Dashboard integration
   - Added consolidated owner one-pager command (`owner-report`)
   - Aggregates drift metrics, guardrail overrides, and latest decision artifacts
   - Added owner report logs (`orchestrator/logs/owner_reports.jsonl`)
   - Weekly schedule-run now auto-generates owner report by default

## v0.6-next (In Progress)

1. Guardrail policy depth
   - Add richer per-domain constraints and escalation paths
2. Cross-report quality
   - Add consistency checks between weekly review, decision audit, and owner report

## v0.7-academic-review-plugin (Planned)

1. Academic review as a standalone plugin
   - Add `modules/review_academic/` (domain plugin, not a generic principles bucket)
   - Canonical SSOT files:
     - `modules/review_academic/data/reviewer_question_bank.yaml`
     - `modules/review_academic/data/checklists/paper_pre_submit.yaml`
   - Append-only logs:
     - `modules/review_academic/logs/review_findings.jsonl`
     - `modules/review_academic/logs/check_runs.jsonl`

2. Reviewer feedback distillation workflow
   - Ingest reviewer comments / rebuttal feedback
   - Distill them into reusable review questions with IDs
   - Attach each question to stages (idea, method, experiment, writing, rebuttal)

3. Submission gate workflow
   - Before paper finalization, run `paper_pre_submit` checklist skill
   - Output blocking findings, weak evidence points, and required revisions
   - Append run result to `check_runs.jsonl`; feed recurring misses into weekly review

4. Progressive disclosure and composability
   - Router loads `modules/review_academic/MODULE.md` only for academic-review intents
   - Other modules reference findings/check items by ID only
   - Plugin can be removed without changing internals of content/decision/profile/memory

## v0.8-principles-layer (Planned)

1. Cross-plugin abstraction (after enough domain modules exist)
   - Add optional `modules/principles/` as a synthesis layer
   - Aggregate stable principles from multiple plugins (academic, investing, projects)
   - Keep principle IDs as cross-domain references, never duplicate source content

## Existing Alignment (Already Present)

- Chat pattern extraction is already implemented in `modules/memory/skills/extract_chat_patterns.md`
- Weekly memory distillation is already implemented in `modules/memory/skills/distill_weekly.md`

## Success Signals

- Better action alignment with long-term priorities
- Lower repeated failure rate in high-risk domains
- Higher precommit coverage and cooldown compliance
- Faster owner audit with clearer exception reports
