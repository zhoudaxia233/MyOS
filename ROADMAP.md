# Personal Core OS Roadmap

## Project Intent

Build a core personal operating system for AI agents, not just a task automation stack.

The system is a stable, extensible operating center where:

- Agents scale execution across workflows (content, research, projects)
- Shared memory preserves decisions, priorities, principles, and drift signals
- Owner judgment stays auditable and aligned with long-term direction

### Enduring Principles

1. Separate execution from judgment.
2. Keep memory and decision history append-only and auditable.
3. Prefer modular plugin extension over kernel coupling.
4. Scale by adding modules and contracts, not by rewriting the core.
5. Optimize for long-term consistency over short-term noise.

### Evolving Direction

- From automation to governance (guardrails, audits, exception handling)
- From logging history to shaping future decisions (memory + retrieval)
- From isolated tasks to cadence-driven operations (daily/weekly/monthly loops)
- From scattered tools to a unified control center (orchestrator + UI)

### Current Execution Next Steps

- See `NEXT_STEPS.md` for the stage-by-stage execution plan toward a transparent cyber-self suggestion mirror.
- Keep the rollout evolutionary: preserve existing extraction/distillation pipelines as first-class upstream inputs.

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
  - providers: dry-run + handoff + optional openai
- Added orchestrator runtime logs:
  - `orchestrator/logs/runs.jsonl`
- Added CLI:
  - `inspect` for route/plan visibility
  - `run` for execution packet (dry-run) or provider-based generation

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
   - Added plugin contract validator for module structure, skill refs, JSONL schema + record integrity (`id`/timestamps/`status`/`source_refs`), routes, and cadence refs
   - Added CI gate: `validate --strict` before test execution
5. End-to-end reliability
   - Added integration command-chain test covering `validate/inspect/run/metrics/owner-report/schedule-run`
   - Fixed path canonicalization in runtime logs for `/var` vs `/private/var` compatibility
6. Runtime audit logging
   - Added run-log fields for route/load traceability (`route_reason`, `matched_keywords`, `loaded_files`, `skill`, `output_hash`)
   - Integrated coverage in end-to-end test assertions

## v1-ui (Completed)

1. Intuitive local control center
   - Added lightweight web interface (`orchestrator/web/`) with chat-style task input and trace panel
   - Added backend server (`orchestrator/src/webapp.py`) using Python standard library (`http.server`)
   - No frontend framework and no new runtime dependencies required
2. Action visibility and auditability
   - UI exposes route reason, matched keywords, selected skill, loaded files, output path, and output hash
   - Added one-click actions for validate, metrics, owner report, weekly cycle run, and retrieval index build
3. Unified launch path
   - Added `web` subcommand in orchestrator CLI (`python3 orchestrator/src/main.py web`)
   - Supports `--host`, `--port`, and `--open-browser`

## v1.1-hardening (In Progress)

1. Routing resilience and boundary checks
   - Auto-route with API key now requires graceful fallback when model routing fails
   - Forced module selection must validate against existing plugin modules
2. Output path safety
   - Restrict generated report/artifact writes to `modules/<name>/outputs/`
   - Block accidental writes to kernel/config/SSOT files via custom output paths
3. Secrets hygiene
   - Keep local settings key file gitignored
   - Avoid returning raw API keys via web settings APIs
4. Decision gate enforcement
   - Added `log-decision` command with hard gate checks (precommit + domain guardrail)
   - Block decision appends when gate status is `blocked`
   - Added append-only gate audit log (`modules/decision/logs/decision_gate_checks.jsonl`)

## v1.2-learning-loop (In Progress)

1. External learning ingestion
   - Added memory skill for learning assets (`modules/memory/skills/ingest_learning_asset.md`)
   - Route rule supports requests like "video summary" / "extract principles"
   - Added orchestrator command `ingest-learning` to append `memory_events` + `memory_insights` from notes
   - Converted reverse-thinking video summary into structured memory records and linked insight

## v1.3-cognitive-architecture (In Progress)

1. Piaget-inspired cognition module
   - Added `modules/cognition/` as dedicated schema-evolution layer
   - Added cognition SSOT data (`schema_policy`, `conflict_taxonomy`, `revision_operators`)
   - Added append-only logs for:
     - `schema_versions`
     - `assimilation_events`
     - `disequilibrium_events`
     - `accommodation_revisions`
     - `equilibration_cycles`
2. Orchestrator cognition commands
   - Added `log-schema`, `log-assimilation`, `detect-disequilibrium`, `log-accommodation`, and `log-equilibration`
   - Added disequilibrium report output generation under `modules/cognition/outputs/`
3. Routing and workflow integration
   - Added cognition routing keywords and weighted matching in manifest/routes fallback
   - Added weekly cadence routine `rt_weekly_equilibration_review`
   - Added web quick action for disequilibrium detection

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

## v0.8-principles-layer (In Progress)

1. Constitutional governance layer
   - Added `modules/principles/` with module manifest, skills, SSOT, outputs, and append-only logs
   - Added constitutional SSOT files (`constitution.yaml`, `amendment_policy.yaml`)
   - Added principle lifecycle logs (`principle_amendments.jsonl`, `principle_exceptions.jsonl`)
2. Boundary refactor contracts
   - Added kernel ontology and boundary standards (`core/ONTOLOGY.md`, `core/BOUNDARY_RULES.md`)
   - Updated routing/docs/checklists/scripts to include `principles` as first-class module

## Existing Alignment (Already Present)

- Chat pattern extraction is already implemented in `modules/memory/skills/extract_chat_patterns.md`
- Weekly memory distillation is already implemented in `modules/memory/skills/distill_weekly.md`

## Success Signals

- Better action alignment with long-term priorities
- Lower repeated failure rate in high-risk domains
- Higher precommit coverage and cooldown compliance
- Faster owner audit with clearer exception reports
