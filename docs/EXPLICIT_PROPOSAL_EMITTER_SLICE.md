# Explicit Proposal Emitter Slice (2026-03-14)

## Problem

The previous boundary slice stopped raw task/run/output shells from entering owner review, but proposal production was still mostly implicit.

That left one weak seam:

- owner-reviewable suggestions depended mainly on post-hoc extraction heuristics
- modules were not yet told, in a stable contract, when to emit a real proposal object
- some output-only skills still risked drifting toward accidental governance language

## What Changed

This slice adds an explicit proposal-emission contract at the prompt and skill level.

### Decision / Weekly Review

- `weekly_review` is now instructed to end with exactly one `## Owner Action Proposal` section when, and only when, the review yields a real owner-facing recommendation
- the proposal block must contain distilled recommendation bullets, not task/run/output metadata
- if evidence is thin, the output should stay review-body-only and omit the proposal block

### Content / After-Meal Story

- `write_after_meal_story` is now explicitly marked output-only
- the draft must not append proposal-review sections
- if owner direction judgment is needed, that should happen in a separate proposal-producing task, not inside the draft artifact

### Extraction Layer

- explicit proposal headings now preserve their real kind:
  - `Owner Action Proposal` -> `owner_action_proposal`
  - `Content Direction Proposal` -> `content_direction_proposal`
  - `Judgment Proposal` -> `retained_judgment`

## Why This Slice

This is the narrowest next step after the review-boundary fix:

- it improves the quality of true review objects
- it avoids broadening owner review to ordinary output artifacts
- it keeps review semantics lighter for ordinary suggestions and stricter only where warranted

## What Remains Deferred

- no generalized sidecar proposal-file system yet
- no new content-strategy skill yet
- no rewrite of output schemas across every module
- no expansion into runtime/delegation/governance machinery

## Next Likely Continuation

If this contract proves stable:

1. add explicit proposal blocks to the next small set of decision/report skills that truly need owner verdicts
2. add the first dedicated content-strategy skill that emits `## Content Direction Proposal` as a primary artifact
3. decide whether proposal objects should stay embedded in output artifacts or later move to a typed sidecar record
