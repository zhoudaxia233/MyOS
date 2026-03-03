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
   - Added richer per-domain constraints (cooldown hours, max loss caps, override confirmation)
   - Next: escalation-path policy suggestions by repeated exception patterns
2. Cross-report quality
   - Added consistency checks between weekly review, decision audit, and owner report
3. Routing and loading auditability
   - Added manifest-driven route rules (`modules/<name>/module.manifest.yaml`)
   - Added route reason + keyword visibility in `inspect`/`run`
   - Switched context loading to skill-driven required files (reduced hardcoded preload)
4. Contract enforcement
   - Added `orchestrator/src/main.py validate` command
   - Added plugin contract validator for module structure, skill refs, JSONL schema headers, routes, and cadence refs
   - Added CI gate: `validate --strict` before test execution

## v0.7-plugin-contract (Planned)

1. Module contract standardization
   - Define a strict plugin contract for `modules/<name>/`:
     - `MODULE.md` (purpose, workflow, progressive loading rules)
     - `skills/*.md` (task entrypoints with required files)
     - `data/*` (SSOT)
     - `logs/*.jsonl` (append-only with schema header)
   - Add a plugin acceptance checklist and validation script

2. Router extensibility without kernel edits
   - Keep kernel docs stable
   - Add route registration in module manifests
   - New plugin onboarding should require config + module files, not Python code edits

3. Task loading by skill contract
   - Loader should resolve data files from selected skill’s required-file section
   - Avoid module-wide preload
   - Keep `ROUTER -> MODULE -> SKILL -> REQUIRED DATA` with minimal context budget

4. Example plugin templates (non-binding)
   - Provide two example domain plugin blueprints:
     - review/checklist plugin (e.g., paper review)
     - project execution plugin
   - Keep as templates/examples, not hardcoded roadmap commitments

## v0.8-principles-layer (Planned)

1. Cross-plugin synthesis (optional abstraction)
   - Add optional `modules/principles/` after multiple domain plugins exist
   - Aggregate stable principles from plugin outputs
   - Keep principle IDs as references to source plugin records, never content duplication

## Existing Alignment (Already Present)

- Chat pattern extraction is already implemented in `modules/memory/skills/extract_chat_patterns.md`
- Weekly memory distillation is already implemented in `modules/memory/skills/distill_weekly.md`

## Success Signals

- Better action alignment with long-term priorities
- Lower repeated failure rate in high-risk domains
- Higher precommit coverage and cooldown compliance
- Faster owner audit with clearer exception reports
