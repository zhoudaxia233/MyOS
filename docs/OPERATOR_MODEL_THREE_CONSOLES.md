# MyOS Three-Console Operator Model (Incremental Spec)

## 1) Purpose

This document defines the next operator-facing model for MyOS using three first-class entrypoints:

1. Task Console
2. Learning / Evolution Console
3. Audit Console

This is an additive evolution, not a rewrite. Existing extraction and distillation pipelines remain first-class upstream inputs.

## 2) Repo-Grounded Assessment (Phase 0)

### 2.1 What already exists for Task Console

Existing capabilities:

- Task route + plan + run pipeline:
  - `orchestrator/src/route_selector.py`
  - `orchestrator/src/planner.py`
  - `orchestrator/src/loader.py`
  - `orchestrator/src/runner.py`
- Handoff provider for low-cost task execution:
  - `orchestrator/src/providers/handoff.py`
- Task-facing UI controls:
  - `orchestrator/web/index.html`
  - `orchestrator/web/app.js`
- Task trace logging and suggestion IDs:
  - `orchestrator/src/webapp.py` (`api_inspect`, `api_run`)
  - `orchestrator/logs/runs.jsonl`
  - `orchestrator/logs/suggestions.jsonl` (created on demand)

Assessment:

- Task execution path is real and reusable.
- Traceability is strong enough for a Task Console baseline.

### 2.2 What already exists for Learning / Evolution Console

Existing capabilities:

- Learning ingestion into memory events/insights:
  - `orchestrator/src/learning_ingest.py`
  - `orchestrator/src/webapp.py` action `ingest_learning`
- Chat import and normalization:
  - `orchestrator/src/chat_ingest.py`
- Memory distillation and pattern extraction skills:
  - `modules/memory/skills/distill_weekly.md`
  - `modules/memory/skills/extract_chat_patterns.md`
  - `modules/memory/skills/ingest_learning_asset.md`
- Cognition signal extraction and schema evolution tools:
  - `orchestrator/src/cognition.py`
  - `modules/cognition/skills/*.md`

Assessment:

- Foundations are strong.
- But operator UX is fragmented: "Learning Capture" is a secondary button, not a first-class console.
- No standardized low-cost "external LLM handoff -> paste-back -> candidate queue" flow existed before this iteration.

### 2.3 What already exists for Audit Console

Existing capabilities:

- Metrics + owner report + escalation queue:
  - `orchestrator/src/metrics.py`
  - `orchestrator/src/owner_report.py`
  - `modules/decision/logs/owner_todos.jsonl`
- Guardrail and decision gate audit logs:
  - `modules/decision/logs/decision_gate_checks.jsonl`
  - `modules/decision/logs/guardrail_overrides.jsonl`
  - `modules/decision/logs/decision_constitution_checks.jsonl`
- UI quick actions and trace panel:
  - metrics, owner report, disequilibrium, timeline, schedule

Assessment:

- Audit data and commands are present.
- Operator mental model is still mixed into one chat form and quick-action chips.

### 2.4 What is missing / fragmented

Missing:

- Top-level explicit three-console mental model.
- Learning Handoff packet standard with strict response format.
- Candidate queue layer between imported material and promoted long-term truths.

Fragmented:

- Learning and audit actions are available but not organized as distinct consoles.
- Candidate governance exists in roadmap intent, but not yet as a clear end-to-end operator flow.

### 2.5 What can be reused immediately

Reuse now:

- Existing route/plan/run stack for Task Console.
- Existing memory/cognition extraction pipelines as upstream substrate.
- Existing owner-report and todo queue as Audit Console anchors.
- Existing handoff concept (task provider) as pattern for Learning Handoff.

### 2.6 What should definitely NOT be changed yet

Do not refactor yet:

- Module manifests and progressive loading contracts.
- Append-only JSONL discipline and validator assumptions.
- Existing decision gate / guardrail / owner-report loops.
- Existing memory/cognition extraction pipeline behavior.

Reason:

- These are stable substrate pieces and should remain continuity anchors while operator UX is clarified.

## 3) Three-Entrypoint Model (Phase 1)

## 3.1 Task Console

Purpose:

- Ask MyOS to execute work with traceable routing and outputs.

Typical inputs:

- Draft/write/review/research/summarize style tasks.
- Optional module/provider/retrieval controls.

Typical outputs:

- Output artifact under `modules/<name>/outputs/*.md`
- Route + plan + loaded files trace
- Suggestion/run IDs for audit linkage

Main workflows:

1. Compose task
2. Inspect route and loaded context
3. Run with provider (`dry-run` / `handoff` / `openai`)
4. Review output + trace

Current support:

- `orchestrator/src/webapp.py`: `api_inspect`, `api_run`
- `orchestrator/src/main.py`: `inspect`, `run`
- `orchestrator/web/` task form + trace

Still needed:

- Suggestion detail drill-down and richer invoked-rule trace.

## 3.2 Learning / Evolution Console

Purpose:

- Convert external material and lived signals into owner-reviewable candidate cyber-self artifacts.

Typical inputs:

- Direct text: transcript/article/notes/summary/chat segment
- Source refs for handoff: YouTube/podcast/article URLs

Typical outputs:

- Raw import records
- Memory-only records
- Candidate artifact queue (insight/rule/skill/principle/cognition revision)

Main workflows:

1. Direct Ingest (text already available)
2. Learning Handoff (external analysis)
3. Candidate review and promotion decisions (owner-governed)

Current support:

- Direct ingest and memory extraction in `learning_ingest.py`
- Memory/cognition downstream extractors
- New handoff packet + import parser (this iteration)

Still needed:

- Full candidate review UI actions (`accept/modify/reject/promote`) and promotion automation.

## 3.3 Audit Console

Purpose:

- Inspect how MyOS is acting like the owner and where drift/risk appears.

Typical inputs:

- Report generation actions
- Todo resolution actions
- Candidate queue inspection

Typical outputs:

- Owner reports, metrics, cognitive timelines
- Open escalation todos
- Pending learning candidates

Main workflows:

1. Run metric/report actions
2. Review exceptions and queue
3. Resolve todos and register owner decisions

Current support:

- `metrics`, `owner_report`, owner todo queue, disequilibrium, cognitive timeline
- New learning candidate queue feed in status/audit view (this iteration)

Still needed:

- Unified suggestion review and candidate promotion dashboard.

## 4) Learning / Evolution Console Design (Phase 2)

### 4.1 Mode A: Direct Ingest

Input form:

- `learning_text` (required)
- `title` (optional)
- `source_type` (video/article/book/podcast/conversation/notes)
- confidence/tags

System behavior:

- Append memory-only artifacts:
  - `modules/memory/logs/memory_events.jsonl`
  - `modules/memory/logs/memory_insights.jsonl`

Operator expectation:

- Fast capture when material is already text-ready.

### 4.2 Mode B: Learning Handoff

Input form:

- source reference (URL/ref)
- optional title/source type hints

Packet generation:

- MyOS generates "Learning Handoff Packet" with:
  - source metadata
  - extraction objective
  - constraints (evidence-linked, uncertainty explicit)
  - strict JSON schema for external response

External response format:

- JSON object with:
  - `source`
  - `summary`
  - `key_points`
  - `candidate_artifacts`:
    - `insights`
    - `rules`
    - `skills`
    - `principles`
    - `cognition_revisions`

Paste-back flow:

1. Owner pastes external JSON response
2. MyOS parses and normalizes
3. MyOS appends raw import + memory-only + candidate queue records

Outcome:

- External material becomes explicit, inspectable candidates under owner review, not auto-promoted truths.

## 5) Candidate Extraction / Review / Promotion Model (Phase 3)

## 5.1 Layer separation

1. Raw imported material
- Log all external handoff imports as provenance records.

2. Memory-only artifacts
- Append to memory events/insights for retrieval and downstream distillation.

3. Candidate artifacts
- Queue typed candidates:
  - insight
  - rule
  - skill
  - principle
  - cognition_revision

4. Approved/promoted artifacts
- Must require explicit owner approval refs.
- Never mutate canonical long-term state directly from raw imports.

## 5.2 Logging policy

Raw import log:

- `modules/memory/logs/learning_imports.jsonl`

Candidate queue log:

- `orchestrator/logs/learning_candidates.jsonl`

Candidate record state:

- `pending_review` (this iteration)
- future: `accepted`, `modified`, `rejected`, `promoted`

## 5.3 Access policy

Without explicit promotion:

- Candidates are visible for suggestion and audit context only.
- Canonical SSOT remains unchanged.

With explicit promotion:

- Future iteration will write promoted candidates into module-specific candidate/promotion logs with `approval_ref`.

## 6) Minimal Frontend Evolution Pattern (Phase 4)

## 6.1 Intermediate UI state (implemented foundation)

- Add top-level selector:
  - Task Console
  - Learning / Evolution Console
  - Audit Console
- Keep current architecture and controls; reorganize presentation by console intent.

## 6.2 Learning Console interaction pattern

- Direct Ingest panel:
  - text + source metadata -> ingest action
- Learning Handoff panel:
  - generate packet -> copy to external LLM
  - paste JSON response -> parse to candidate queue

## 6.3 Candidate visibility pattern

- Show pending learning candidates in trace/audit side panel.
- Keep promotion actions out of this slice to avoid unsafe state mutation.

## 7) Implemented Slice in This Iteration (Phase 5)

Chosen slice:

- "Learning Handoff foundation": packet generation + paste-back parsing + candidate queue logging + minimal UI shell.

Why this first:

- Highest leverage for low-cost learning flow.
- Preserves and reuses existing extraction pipelines.
- Creates a transparent bridge from external material to governed candidate artifacts.

Implemented components:

- Backend:
  - `orchestrator/src/learning_console.py`
  - web actions:
    - `learning_handoff_packet`
    - `learning_handoff_import`
- Logs:
  - `modules/memory/logs/learning_imports.jsonl` (on first write)
  - `orchestrator/logs/learning_candidates.jsonl` (on first write)
  - `modules/decision/logs/learning_candidate_verdicts.jsonl` (owner review trail)
- Candidate review action (minimal):
  - `review_learning_candidate` with `accept | modify | reject`
  - `modify` creates a replacement pending candidate for second-pass review
- Candidate promotion action (minimal):
  - `promote_learning_candidate` requires accepted verdict first
  - append-only approval/promotion trail:
    - `modules/decision/logs/learning_candidate_approvals.jsonl`
    - `modules/decision/logs/learning_candidate_promotions.jsonl`
- UI:
  - three-entrypoint selector
  - Learning Console direct ingest inputs
  - Learning Handoff packet/import controls
  - candidate queue view in trace panel
- Preservation hardening:
  - memory ingest/chat ingest now write classification fields (`object_type`, `proposal_target`) aligned with current schema governance.

## 8) Continuation Plan (Phase 6 Pointer)

Next implementation slice should focus on:

1. Module-specific promotion sinks
- write promoted records into decision/profile/cognition/principles-specific candidate logs
- keep approval linkage and append-only guarantees

2. Audit integration
- show candidate drift / acceptance rates in owner report

3. Safety guardrails
- enforce that pending candidates cannot overwrite canonical SSOT without explicit promotion.
