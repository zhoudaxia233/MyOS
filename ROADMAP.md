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

### Positioning Charter Baseline (2026-03-10)

The long-term architecture baseline is codified in:

- `docs/MYOS_POSITIONING_CHARTER.md`

Mandatory alignment gate for roadmap items:

- keep MyOS thin (do not rebuild commodity model/tool/orchestration layers)
- keep MyOS model-agnostic (provider adapters are replaceable)
- preserve judgment core durability and governance logic
- enforce audited absorption (`candidate -> review -> promote/reject`) for learning
- keep three-entrypoint operator clarity (Task / Learning / Audit)
- preserve existing extraction/distillation pipelines as first-class substrate

Any roadmap item that fails this gate should be treated as drift and redesigned before implementation.

### Current Execution Roadmap

Keep rollout evolutionary: preserve existing extraction/distillation pipelines as first-class upstream inputs.

#### Runtime Eligibility + Influence Visibility Slice (2026-03-14)

- Why this slice:
  - promotion was still too close to runtime activation
  - owner could see what was promoted, but not cleanly distinguish `promoted truth` from `runtime eligible`, nor inspect what actually influenced a run
- Shipped in this iteration:
  - added append-only runtime eligibility log:
    - `modules/decision/logs/runtime_eligibility.jsonl`
  - promotion now writes a separate runtime eligibility record instead of letting runtime infer solely from promoted existence
  - legacy promoted artifacts are seeded into explicit eligibility records on first read, so the distinction becomes explicit without breaking existing promoted data
  - typed default seriousness baseline is now encoded:
    - `insight / rule / skill` default to `eligible` with `suggest_only`
    - `principle / profile_trait / cognition_revision` default to `holding` with `review_required`
  - runtime loading now consumes runtime eligibility, not just promoted age:
    - loader injects only `eligible + matured + scope-matched` artifacts
    - runtime synthetic context source renamed to `orchestrator://runtime_eligible_artifacts`
  - run/suggestion traces now log actual runtime influences:
    - `runs.jsonl` and `suggestions.jsonl` include `runtime_influences`
    - each influence records artifact ref/type plus promotion/eligibility linkage, scope, autonomy ceiling, and selection reason
  - owner-visible surfaces now show the distinction and the influence path:
    - Audit lifecycle strip adds `Runtime Eligible` between `Promoted` and `Active Runtime`
    - candidate detail now surfaces runtime eligibility, scope, autonomy ceiling, and runtime state
    - suggestion detail and workspace technical view now show active runtime influences for the current run/suggestion
  - follow-up control slice now exists on top of the same model:
    - owners can append explicit `holding / eligible / revoked` runtime eligibility transitions for promoted candidates
    - runtime eligibility changes remain append-only and latest-record-wins, instead of mutating promotion history
    - Audit candidate cards expose minimal runtime governance controls without introducing a generalized policy UI
  - recent runtime influence replay slice now exists:
    - recent run history now summarizes which eligible artifacts were actually active across the latest runs
    - latest run now compares against the nearest prior run (prefer same-module) to surface `added / dropped / stable` runtime influences
    - both Workspace and Audit expose this as a lightweight owner-visible drift panel, without turning it into a policy engine or alerting subsystem
- Kept intentionally minimal:
  - no generalized policy engine
  - runtime eligibility control is status-only; no broad per-type rule editor or policy matrix
  - influence drift is replay-only; no anomaly scoring, threshold alerts, or auto-remediation
  - no broad autonomy feature expansion
  - no changes to `candidate -> review -> promote` safeguards
- Next continuation slice:
  - add owner-report integration or module-scoped drilldown for runtime influence drift when the replay panel proves useful
  - deepen stricter workflows for `principle / profile / cognition` without flattening them into generic runtime rules
- Do not overbuild yet:
  - no policy DSL
  - no delegated action/autonomy system
  - no auto-amend of principle/profile from runtime behavior

#### Typed Runtime Guard Slice (2026-03-14)

- Why this slice:
  - the authority contract was still vulnerable at one high-risk seam: Class C artifacts could be promoted into ledger and then manually released through the same generic runtime path as lighter artifacts
  - that left `profile_trait / principle / cognition_revision` too close to runtime authority before any ratification path existed
- Shipped in this iteration:
  - generic promotion now keeps `profile_trait`, `principle`, and `cognition_revision` explicitly in `holding`
  - the generic `set_runtime_eligibility` path now refuses to mark those three types `eligible`
  - audit UI wording now explains that these serious artifact types are intentionally held pending ratification/canonicalization
  - the generic Audit action surface no longer offers `Mark Eligible` for those held Class C artifacts
- Kept intentionally minimal:
  - no canonicalization engine
  - no ratification UX
  - no schema migration of historical artifacts
  - no loader/runtime redesign
- Next continuation slice:
  - add the first explicit canonicalization / ratification record path for Class C artifacts
  - then allow runtime authority only from that typed path, not from generic promotion history

#### Immediate Priority - Perceivable MVP Flow (2026-03-09)

- Principle:
  - prioritize user-visible interaction and directly testable flows over invisible internal plumbing
- Completed:
  - web Task Console now has one-click `Run MVP Flow (Inspect -> Run -> Review)` path for immediate end-to-end trial
  - web Task Console now has `Run Demo Mode (Decision + Learning + Audit)` for 3-step visible capability walkthrough
  - UI language setting (`zh | en`) with key onboarding hints following current language
  - direct `deepseek` provider support with settings-driven API key/base URL/model for low-cost live runs
- Next:
  - add explicit in-UI completion checklist for first successful run-through (inspect ok / run ok / suggestion reviewed)

#### Learning Operator Clarity Slice (2026-03-10)

- Analysis completed (repo-grounded, end-to-end):
  - workspace learning entry + handoff path + candidate governance path were reviewed across UI/API/log layers
  - key files inspected: `orchestrator/web/index.html`, `orchestrator/web/workspace.js`, `orchestrator/web/audit.html`, `orchestrator/web/app.js`, `orchestrator/src/webapp.py`, `orchestrator/src/learning_ingest.py`, `orchestrator/src/learning_console.py`, `orchestrator/src/loader.py`
- Small high-leverage UX improvement shipped:
  - learning panel now includes visible 3-step flow guide (direct ingest -> handoff import -> audit/promotion)
  - added direct CTA link from learning panel to audit center candidate review
  - post-ingest and post-import summaries now explicitly state write targets / next governance step
  - changed files: `orchestrator/web/index.html`, `orchestrator/web/workspace.js`, `orchestrator/web/styles.css`
- Remaining next slice:
  - align stale docs/onboarding language with current learning UI (remove old “task box one-click ingest” wording)
  - add audit-side candidate triage quality-of-life filters (type/source/age) without backend rewrite
  - keep extraction/distillation substrate unchanged; focus on operator discoverability and governance ergonomics

#### Learning Lifecycle Clarity Slice (2026-03-10, Iteration 2)

- Accomplished in this iteration:
  - audit UI now exposes explicit lifecycle strip: `Imported -> Candidate -> Reviewed -> Promoted -> Active Runtime`
  - candidate cards upgraded to evidence-first review cards (statement/source/rationale/evidence/confidence/status/next action)
  - replaced prompt/confirm-heavy candidate governance with modal-based review/promotion flow (`Accept/Modify/Reject/Promote`)
  - added audit empty-state density control: when no owner todos/candidates/lifecycle signals, manual action clusters are hidden and replaced by a clear “start from workspace learning or quick audit” guidance block
  - moved diagnostics/review-filter actions behind collapsed fold by default to reduce first-screen button overload
  - backend payload enrichment only (no architecture rewrite):
    - `list_recent_learning_candidates(..., include_resolved=True)` now returns lifecycle stage + review/promotion/runtime metadata
    - `summarize_learning_pipeline` now exposes lifecycle counts for UI rendering
  - workspace post-import guidance now explicitly states lifecycle progression, review requirements, and runtime maturity gate
  - terminology normalization landed in UI/docs:
    - `Learning & Evolution` wording on workspace/audit/docs
    - removed stale “Task box one-click ingest / Learning Capture button” references in README surfaces
- What remains next:
  - add candidate triage filters/sorts in audit (`type/source/stage/age`) for higher-volume queues
  - add evidence drill-down panel (raw snippet context) without changing candidate governance contracts
  - add lightweight batch review actions for low-risk homogeneous candidates
- Deferred intentionally (do not refactor yet):
  - no changes to learning ingestion architecture, extraction pipeline, or promotion/maturity safeguards
  - no auto-promotion/autonomous learning path
  - no provider-coupled memory/runtime rewrite

#### Operator Action Hierarchy Slice (2026-03-12)

- Why this slice:
  - the main friction was not missing capability, but that operator flow was still visually organized like internal control panels
  - both Workspace and Audit needed the same correction: bring the next owner action to the top, push machine detail into support
- Shipped in this iteration:
  - Workspace now reads as a task launcher instead of a mixed tutorial/control page:
    - explicit primary execution modes: `direct execute`, `handoff`, `dry run`
    - handoff copy reframed as a normal low-cost mode, not an error fallback
    - task starter chips now fill structured task-brief templates instead of auto-running immediately
    - result area now prioritizes `summary -> next action -> details`
    - file path / tokens / full markdown are downgraded into secondary folds
  - Audit now reads as an Owner Review Inbox instead of a monitoring dashboard:
    - top-level triage counts for `pending review`, `ready to promote`, `owner todos`
    - primary queues split by judgment stage instead of one blended candidate/status list
    - lifecycle, report summaries, and machine traces moved into support rail / progressive disclosure
    - quick audit remains available but is visually supportive, not dominant over review decisions
  - Follow-up inbox triage refinement shipped immediately after:
    - client-side candidate filters for `stage / type / source / age`
    - dynamic type options derived from current candidate queue
    - filtered queue counts + filter meta so operators can quickly narrow review scope without changing backend contracts
  - Follow-up evidence drill-down shipped:
    - candidate cards now include expandable review context for `evidence / source refs / owner note / modified statement / runtime state`
    - detailed judgment context stays inside the review object instead of forcing operators back into machine trace
  - Follow-up triage preset views shipped:
    - default inbox views for `all / needs review / ready to promote / last 7d`
    - preset selection is remembered client-side so the audit page can reopen in the owner's usual queue
    - manual filter edits still work and automatically fall back to a custom view without changing backend contracts
  - Follow-up suggestion review inbox shipped:
    - task suggestions now have a dedicated review queue in Audit instead of living only as summary metrics + the latest trace detail
    - owner can review any pending suggestion from the inbox with a guided modal instead of `window.prompt`
    - execution suggestion judgment is now visually separated from learning candidate governance while keeping the same review contract
  - Follow-up structured suggestion detail support shipped:
    - the suggestion support panel now shows structured review context first: task, status, output artifact, focus points, owner note, correction, and next action
    - raw suggestion payload is still available, but moved behind progressive disclosure instead of dominating the review surface
    - selecting a suggestion from the inbox now also syncs the support-side output preview, so review context and artifact preview stay aligned
  - Follow-up recent execution judgment fold shipped:
    - recently reviewed suggestions are now visible in a secondary fold, so owners can audit their latest execution judgments without reopening the main action queue
    - reviewed suggestion cards surface verdict, timing, owner note, and correction target at a glance
    - reviewed items remain read-oriented with `Open Detail` only, preserving the distinction between pending judgment and completed judgment
  - Follow-up shared audit timeline shipped:
    - recently reviewed execution suggestions and resolved learning candidates now share one chronological secondary timeline
    - pending queues remain object-specific; chronology now applies only to completed judgments
    - reviewed learning entries keep expandable evidence and source context inside the timeline, so chronology does not remove auditability
  - Follow-up timeline-scoped replay filters shipped:
    - the shared audit timeline now has its own `object / judgment / time` filters instead of borrowing the pending inbox filters
    - owners can replay only `execution suggestions`, only `learning candidates`, or narrow to `accept / modify / reject / promote` decisions
    - completed-judgment replay stays separate from pending triage, preserving the difference between doing judgment and revisiting judgment
  - Follow-up cross-object detail pane shipped:
    - the right-side support detail is no longer suggestion-only; reviewed learning judgments can now open the same support area from the timeline
    - support chrome now switches by object type: suggestion items keep raw snapshot + output preview, while learning items clear unrelated output state and render structured judgment detail instead
    - reviewed suggestion detail is now read-oriented from the timeline, so completed replay no longer exposes the same action buttons as pending review
  - Follow-up shared evidence compaction shipped:
    - learning evidence/source refs and suggestion focus points now render as compact summaries first, with full content available only on demand
    - support detail cards now add a small snapshot summary (`fields / approx size / list entries`) before the raw JSON fold
    - replay surfaces stay operator-readable even when source refs or evidence snippets get longer, without removing the underlying audit trail
- Remaining next:
  - consider richer saved views only if operators need per-owner custom presets beyond the shipped defaults
  - consider severity-based ranking inside replay history only if completed-judgment volume grows beyond the current timeline filters
  - consider selective transcript chunk previews if evidence items become much longer than the current compaction layer can comfortably summarize
- Do not change yet:
  - do not collapse `accept` and `promote`
  - do not weaken runtime maturity / promotion gates
  - do not move learning back into a generic task box
  - do not refactor backend governance architecture just to satisfy UI structure

#### Stage 1 - Transparent Suggestion Pipeline (Current)

- Completed:
  - structured suggestion records at `orchestrator/logs/suggestions.jsonl`
  - `run` / web `api_run` return `suggestion_id`
  - classification consistency for runtime logs (`object_type` / `proposal_target`)
  - suggestion detail query API by `suggestion_id`
  - web trace panel support for full suggestion detail view
  - clearer `invoked_rules` / `invoked_traits` fields in suggestion records
  - bridge suggestion detail to owner verdict/correction actions (`suggestion_id` as first-class review handle)
  - owner report + audit quick filters now include suggestion review summary/trend (`accept|modify|reject`, correction ratio, 7d vs 30d)
- Next:
  - close Stage 1 with lightweight replay ergonomics for session-level trace continuity (feeds HF-1)
- Exit criteria:
  - end-to-end trace from task input to suggestion, run record, output artifact, and loaded context
  - owner can inspect why a recommendation was produced

#### Stage 2 - Structured Owner Feedback Loop

- New records:
  - `orchestrator/logs/owner_verdicts.jsonl`
  - `orchestrator/logs/owner_corrections.jsonl`
- Implemented baseline:
  - web/API action `review_suggestion` with `accept | modify | reject`
  - `modify` captures correction payload (`target_layer`, `replacement_judgment`, `unlike_me_reason`)
  - suggestion detail API now returns linked owner review context
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
  - runtime uses explicit runtime-eligible promoted truths only, not raw candidates
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
- No drift into a broad "do everything" automation platform clone
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
- Added audit visibility for candidate pipeline quality:
  - owner report includes candidate pipeline summary (pending/reviewed/verdict/promoted/conversion)
  - web status/trace exposes `candidate_pipeline_summary` for Audit Console
- Added candidate trend + drift visibility (7d vs 30d):
  - new trend aggregation `summarize_learning_pipeline_trend` (backlog pressure / reject ratio / promotion conversion)
  - owner report now includes trend section and candidate drift exceptions/auto-triggers
  - web status/action payloads expose `candidate_pipeline_trend` and UI trace shows trend lines
- Added promotion readiness policy baseline:
  - pipeline summary now includes `promotion_readiness` (maturity window + ready/cooling counts)
  - owner report surfaces cooling backlog exceptions/auto-triggers for promotion governance
  - UI trace now shows promotion readiness by target
- Added first consumption wiring for promoted artifacts:
  - originally `load_context_bundle` appended `orchestrator://promoted_candidates_ready`
  - this has now been superseded by runtime eligibility gating (`orchestrator://runtime_eligible_artifacts`)
  - runtime no longer treats promoted existence as sufficient for injection
- Added promotion consumption tuning baseline:
  - runtime-eligible artifact loading supports intent-aware ranking from current task text
  - when intent terms match, context load prioritizes matched eligible artifacts
  - when no intent match exists, loading falls back to recent eligible artifacts (no empty context drop)
- Added minimal UI evolution toward three-entrypoint model:
  - Task Console / Learning Console / Audit Console selector
  - Learning Console direct ingest and handoff controls
  - candidate queue visibility + review buttons in audit-side trace
- Preserved continuity with extraction foundations:
  - memory/chat ingestion keeps append-only behavior
  - no direct mutation of canonical long-term truths from external imports

Remaining next:

- Dedicated Audit Console candidate-review panel (batch triage, filters by type/source/age)
- Owner-tunable readiness policy (per-candidate-type maturity hours + explicit override path)

Dependencies / blockers:

- Need owner policy for per-candidate-type maturity windows and explicit override/fast-track conditions
- Need ranking/filtering policy so loaded promoted candidates stay high-signal under larger volumes

Do not refactor yet:

- Router/planner/module manifest architecture
- Existing memory distillation, pattern extraction, cognition extraction pipelines
- Decision gate and owner report control loops

### Handoff-First Interaction Track (Token-Efficient UX) (2026-03-09)

Intent:

- Keep `handoff` as the default low-cost execution path to control token spend.
- Preserve direct `openai` / API execution as an optional high-leverage path.
- Make both modes share one operator flow, one trace model, and one audit story.

Operator policy baseline:

- Default mode remains `handoff`; API mode is explicit opt-in per task/session.
- No hidden full-context API calls inside a handoff workflow.
- No split-product UX where handoff feels like a degraded fallback path.

Unified interaction contract (single flow across modes):

1. Draft task -> inspect route/plan/context.
2. Select depth/budget profile (`lite | standard | deep`).
3. Execute:
   - handoff mode: generate packet + copy + paste structured response.
   - API mode: run provider directly.
4. Parse/validate/trace with the same review surface.
5. Review/promote/log outcomes with the same governance controls.

Roadmap milestones:

#### HF-1 - Unified Session State Model

- Add explicit session-level state model shared by handoff/API:
  - `draft -> inspected -> packet_ready|api_running -> response_ready -> reviewed -> finalized`
- Add stable `session_id` and `interaction_mode` fields to runtime/suggestion traces.
- Make web trace render session progression instead of only final action snapshots.

Exit criteria:

- One session timeline can be replayed regardless of execution mode.

#### HF-2 - Token Budget Controls for Handoff

- Add packet depth profiles: `lite`, `standard`, `deep`.
- Add packet token estimate before copy, with budget warning thresholds.
- Add delta handoff mode for follow-up turns (send only changed context + unresolved questions).

Exit criteria:

- Owner can bound handoff payload size intentionally before each external call.

#### HF-3 - Robust Structured Paste-Back

- Keep strict JSON response contract for external LLM output.
- Add tolerant parse-repair for minor formatting issues (without changing semantic fields).
- Add clear field-level validation errors and retry guidance in UI.

Exit criteria:

- Most paste-back failures are recoverable in UI without manual log surgery.

#### HF-4 - Seamless Mode Switching

- Allow switching `handoff <-> openai` inside the same session without losing trace continuity.
- Keep shared review/promote actions and identical governance gates after mode switch.
- Add budget-triggered suggestion path: when API budget risk is high, suggest handoff continuation.

Exit criteria:

- Mode switch does not force operator to restart workflow or lose audit context.

#### HF-5 - Cost and UX Auditability

- Add interaction efficiency telemetry:
  - packet size estimates, mode usage ratio, parse retry rate, time-to-finalized
- Surface these in owner report / audit console as first-class UX-health signals.

Exit criteria:

- Owner can verify that handoff-first operation improves cost predictability without UX regression.

Explicit non-goals for this track:

- No OpenClaw-style heavy always-on token streaming requirement.
- No API-only redesign that sidelines handoff workflow.
- No bypass of existing candidate review/promotion governance.

### Lightweight State-Task Matching Heuristic (Yerkes-Dodson) (2026-03-09)

Design source:

- `docs/STATE_TASK_MATCHING_HEURISTIC.md`

Intent:

- Add a lightweight state-task matching heuristic in orchestration/decision paths.
- Improve recommendation quality under cognitive mismatch.
- Reduce default "add pressure" responses when progress is low.

Scope boundary:

- Keep this as scheduling/decision hygiene logic, not a standalone psychology module.
- Use coarse buckets only:
  - state: `low_activation | stable_activation | high_activation | unknown`
  - task load: `low | medium | high` (+ reversibility and execution mode hints)
- Prefer explicit rules and neutral operational language.

Milestones:

#### ST-1 - Minimal State + Task Profile Contract

- Add design-level contract for:
  - `state_hint`
  - `task_cognitive_profile`
  - `state_task_match`
- Keep all fields coarse and auditable; avoid pseudo-precision.

Exit criteria:

- Planning path can represent state-task fit with simple categories.

#### ST-2 - Inspect/Run Recommendation Layer

- Before execution recommendation, run state-task fit check.
- If mismatch:
  - high activation + high-load task -> lower-load/convergent alternatives first
  - low activation + medium/high-load task -> warm-up starter tasks first

Exit criteria:

- Inspect output can explain task switch suggestion using fit rationale tags.

#### ST-3 - Deep Work Protection + Decision Hygiene

- Recommend high-load deep work only when state is sufficiently stable.
- For high activation + hard-to-reverse decision contexts:
  - suggest defer/notes/reversible tasks before major commitment.

Exit criteria:

- System avoids encouraging irreversible strategic moves under overloaded state by default.

#### ST-4 - Low-Friction Check-In + Cadence Integration

- Add optional short check-in (`low/stable/high`) only when state is unclear or mismatch repeats.
- Integrate fit signal with cadence task ordering (execution-first vs deep-work-first).

Exit criteria:

- No heavy journaling workflow; one-step state hint is sufficient when needed.

#### ST-5 - Anti-Self-Blame Correction Loop

- When repeated stalls occur on complex tasks, include mismatch-first diagnosis:
  - needs activation
  - needs down-regulation
  - needs task-class switch
- Keep wording operational and non-moralizing.

Exit criteria:

- Recommendation language avoids implicit laziness/discipline framing in mismatch cases.

Explicit non-goals for this capability:

- No large psychology subsystem.
- No fake precision scoring (`arousal = 73.2` style outputs).
- No dashboard-heavy implementation before practical recommendation value is proven.
- No therapy-style persona or paternalistic tone.

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

## v1.4-handoff-first-interaction (Planned)

1. Unified handoff/API interaction loop
   - Shared session state machine and trace model across both execution modes
   - Consistent inspect -> execute -> review flow in web UI
2. Token-aware handoff ergonomics
   - Packet depth profiles (`lite | standard | deep`) with pre-copy token estimates
   - Delta handoff support for follow-up turns
3. Robust structured import UX
   - Better paste-back validation and repair hints
   - Higher completion rate for handoff loops without leaving the UI
4. Cost governance visibility
   - Owner-report metrics for token efficiency and interaction friction

## v1.5-state-task-matching (Planned)

1. Lightweight Yerkes-Dodson scheduling heuristic
   - Coarse state buckets (`low/stable/high/unknown`) and coarse task cognitive profiles
   - State-task fit recommendation in inspect/run flows (no heavy scoring engine)
2. Deep-work protection and decision hygiene
   - Avoid default high-load recommendations when overloaded
   - Encourage defer/reversible paths for high-activation major decisions
3. Low-friction operational UX
   - Optional one-step check-in only when needed
   - Neutral operator phrasing (no therapeutic or moralizing framing)
4. Anti-overengineering guardrails
   - Keep rules explicit, practical, and maintainable
   - Avoid pseudo-scientific precision and dashboard bloat

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
