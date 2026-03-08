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

### Current Execution Roadmap

Keep rollout evolutionary: preserve existing extraction/distillation pipelines as first-class upstream inputs.

#### Stage 1 - Transparent Suggestion Pipeline (Current)

- Completed:
  - structured suggestion records at `orchestrator/logs/suggestions.jsonl`
  - `run` / web `api_run` return `suggestion_id`
  - classification consistency for runtime logs (`object_type` / `proposal_target`)
- Next:
  - suggestion detail query API by `suggestion_id`
  - web trace panel support for full suggestion detail view
  - clearer `invoked_rules` / `invoked_traits` fields in suggestion records
- Exit criteria:
  - end-to-end trace from task input to suggestion, run record, output artifact, and loaded context
  - owner can inspect why a recommendation was produced

#### Stage 2 - Structured Owner Feedback Loop

- New records:
  - `orchestrator/logs/owner_verdicts.jsonl`
  - `orchestrator/logs/owner_corrections.jsonl`
- Required behavior:
  - verdict: `accept | modify | reject`
  - correction captures "unlike-me" reason, replacement judgment, and target layer
  - web UI includes review controls and structured submit path
- Exit criteria:
  - every suggestion can be reviewed with explicit verdict + correction trail

#### Stage 3 - Candidate Promotion Workflows

- New candidate logs:
  - `modules/decision/logs/rule_candidates.jsonl`
  - `modules/decision/logs/skill_candidates.jsonl`
  - `modules/profile/logs/profile_trait_candidates.jsonl`
  - `modules/cognition/logs/schema_candidates.jsonl`
  - `modules/principles/logs/principle_candidates.jsonl`
- Required behavior:
  - candidate lifecycle: `candidate -> reviewed -> promoted|rejected`
  - promotion requires explicit `approval_ref`
  - runtime uses promoted truths only, not raw candidates
- Exit criteria:
  - extraction outputs become governable candidates without directly mutating canonical state

#### Stage 4 - Limited Delegation With Explicit Review

- New records:
  - `modules/decision/logs/delegated_action_proposals.jsonl`
  - `modules/decision/logs/delegated_action_runs.jsonl`
- Required behavior:
  - low-risk whitelist scope only
  - pre-approval by owner remains default
  - full proposal/run/result audit chain
- Exit criteria:
  - limited delegated execution works with complete transparency and rollback path

#### Stage 5 - Governed Higher Autonomy

- Direction:
  - gradually expand low-risk auto-execution after Stage 1-4 stability
  - shift owner focus to audit, exception handling, and strategic correction
  - continuous drift monitoring to prevent black-box behavior
- Exit criteria:
  - higher execution autonomy with unchanged or stronger auditability and governance

#### Explicit Non-Goals

- No greenfield rewrite
- No removal of extraction/distillation pipelines
- No collapse into generic note app or pure RAG assistant
- No direct overwrite of long-term truths from noisy inputs
- No high-risk autonomy without owner oversight

### Three-Entrypoint Operator UX Track (2026-03-08 Iteration)

This track phases in a clearer operator mental model while preserving current architecture and extraction substrate.

Completed in this iteration:

- Added repo artifact defining the three-entrypoint operator model:
  - `docs/OPERATOR_MODEL_THREE_CONSOLES.md`
- Implemented Learning Handoff foundation (low-cost learning path):
  - packet generation for external LLM (`learning_handoff_packet`)
  - pasted-response parsing and normalization (`learning_handoff_import`)
  - raw import + candidate queue append-only logs:
    - `modules/memory/logs/learning_imports.jsonl`
    - `orchestrator/logs/learning_candidates.jsonl`
- Added minimal owner review loop for learning candidates:
  - `review_learning_candidate` supports `accept | modify | reject`
  - append-only owner verdict trail:
    - `modules/decision/logs/learning_candidate_verdicts.jsonl`
  - `modify` creates replacement pending candidate for second-pass review
- Added minimal promotion gate for accepted candidates:
  - `promote_learning_candidate` requires prior `accept` verdict
  - append-only approval and promotion logs:
    - `modules/decision/logs/learning_candidate_approvals.jsonl`
    - `modules/decision/logs/learning_candidate_promotions.jsonl`
- Added module-specific promotion sinks (append-only):
  - `modules/memory/logs/insight_candidates.jsonl`
  - `modules/decision/logs/rule_candidates.jsonl`
  - `modules/decision/logs/skill_candidates.jsonl`
  - `modules/profile/logs/profile_trait_candidates.jsonl`
  - `modules/cognition/logs/schema_candidates.jsonl`
  - `modules/principles/logs/principle_candidates.jsonl`
- Added minimal UI evolution toward three-entrypoint model:
  - Task Console / Learning Console / Audit Console selector
  - Learning Console direct ingest and handoff controls
  - candidate queue visibility + review buttons in audit-side trace
- Preserved continuity with extraction foundations:
  - memory/chat ingestion keeps append-only behavior
  - no direct mutation of canonical long-term truths from external imports

Remaining next:

- Audit views for candidate drift and promotion quality over time
- Promotion availability policy (when promoted items become suggestion-eligible by default)

Dependencies / blockers:

- Need owner policy for when promoted candidates become suggestion-eligible by default
- Need explicit retrieval/routing rule for whether promoted candidates are loaded by default or by task intent

Do not refactor yet:

- Router/planner/module manifest architecture
- Existing memory distillation, pattern extraction, cognition extraction pipelines
- Decision gate and owner report control loops

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
