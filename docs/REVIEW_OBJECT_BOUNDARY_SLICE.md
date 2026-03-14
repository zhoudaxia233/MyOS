# Review Object Boundary Slice (2026-03-14)

## Problem Identified

The repo had a real object-model conflation in owner review:

- `task`
- `run`
- `output`
- `suggestion`

were too loosely treated as if they were the same kind of review object.

Concrete failure mode:

- every `api_run` / CLI `run` appended a `suggestion` record regardless of whether the output contained a real proposal
- the audit inbox then surfaced those records like owner-review objects
- owners saw raw task shells or execution packets next to `Accept / Modify / Reject`

This made ordinary execution residue look like governance work.

## What Changed

This slice does **not** redesign the whole app shell.

It introduces one tighter boundary:

1. Every run still records a follow-up object in `orchestrator/logs/suggestions.jsonl`.
2. That object is now explicitly classified as either:
   - `execution_trace`
   - `judgment_proposal`
3. Only `judgment_proposal` objects enter the suggestion review inbox and summary/trend loop.
4. `execution_trace` objects remain visible only as secondary support detail / history, not as owner-review inbox items.

## Implemented Contract

### Suggestion Review

- Scope:
  - true run-derived judgment proposals only
- Current backend gate:
  - `review_object_type == judgment_proposal`
- Current review actions:
  - lighter owner-verdict language (`keep / rewrite & keep / do not keep`)

### Learning Candidate Review

- Scope:
  - external-learning / ingestion derived candidates
- Unchanged in this slice:
  - existing verdict / promotion / canonicalization / runtime safeguards

### Serious Authority Review

- Scope:
  - high-seriousness authority / exception work already escalated into owner todo flows
- Current UI treatment:
  - relabeled more explicitly as a separate seriousness class
- Unchanged in this slice:
  - no new ratification workflows were added

## What Was Implemented In Code

- Added conservative run-output classification in `orchestrator/src/review_objects.py`
- Added new suggestion-record fields:
  - `review_object_type`
  - `proposal_kind`
  - `proposal_heading`
  - `proposal_title`
  - `proposal_summary`
  - `proposal_statement`
  - `review_reason`
- Updated `api_run` / CLI `run` to stamp those fields on suggestion records
- Updated owner-review queue + summary logic so only reviewable proposal objects count
- Blocked `review_suggestion` for non-reviewable execution traces
- Reframed audit UI wording:
  - suggestion review now reads as proposal review
  - learning candidate review keeps candidate-specific language
  - owner todo area now reads as serious authority review

## What Remains Unresolved

- `suggestions.jsonl` still stores both `execution_trace` and `judgment_proposal`
  - this is an intentional compatibility compromise for this slice
  - a future split into dedicated run-followup logs may still be worth considering
- proposal extraction is conservative
  - many dry-run / handoff outputs remain `execution_trace`
  - this is correct for now because those outputs are packets, not owner-review objects
- module-specific proposal emitters are still thin
  - today only explicit proposal/action sections become proposal objects

## What Should Be Tackled Next

Only after this boundary is stable:

1. add explicit proposal blocks to modules that genuinely need owner verdicts
2. improve proposal extraction for real decision/content outputs
3. decide whether `execution_trace` should stay in `suggestions.jsonl` or move into a dedicated follow-up sink

## What Should NOT Yet Be Redesigned

- do not collapse learning review and suggestion review into one mega inbox
- do not turn ordinary suggestions into constitution-style ratification flows
- do not broaden this slice into runtime/delegation redesign
- do not weaken promotion/canonicalization/runtime safeguards already present in learning and authority paths
