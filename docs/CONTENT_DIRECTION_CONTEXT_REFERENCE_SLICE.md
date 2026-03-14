# Content Direction Context Reference Slice (2026-03-14)

## Problem

After introducing a dedicated `content_direction_proposal` object and a Workspace starter for it, content drafting still lacked a safe way to reuse an accepted direction judgment.

Without a typed follow-through path, drafting would either:

- ignore accepted direction work and reinvent framing
- or start loading direction judgments implicitly and unpredictably

## What Changed

This slice adds an explicit reference-based context path for content drafting.

### Backend

- content drafting now loads an accepted content-direction proposal only when the task explicitly references its `suggestion_ref`
- supported task-brief forms include:
  - `Accepted content direction proposal ref: sg_...`
  - `内容方向提案 ref：sg_...`
  - `已接受的内容方向提案 ref：sg_...`
- only `accept` and `modify` verdicts qualify
- `reject` or pending proposals are ignored
- `modify` uses the rewritten judgment as the effective direction context

### Context Shape

The loader now injects a virtual support file:

- `orchestrator://accepted_content_direction/<suggestion_id>`

That file contains:

- the accepted suggestion ref
- verdict type
- effective direction
- owner note
- rewrite rationale when present

### Workspace

- Workspace now includes a draft template for:
  - `Draft From Accepted Direction`
- the template makes the explicit `proposal ref` slot visible to the owner instead of hiding the contract in backend-only behavior

## Why This Slice

This keeps the object model layered and explicit:

- accepted direction remains a judgment object
- draft remains an output artifact
- reuse happens only through an explicit bridge, not through hidden auto-governance

## What Remains Deferred

- no lookup UI for browsing accepted direction proposals yet
- no one-click “use this accepted proposal” action from Audit into Workspace yet
- no generalized cross-object reference system across every reviewable artifact

## Next Likely Continuation

1. add a lightweight picker or follow-up action from accepted content-direction proposals into draft tasks
2. then consider the same explicit-reference pattern for other low-seriousness proposal-to-output handoffs
