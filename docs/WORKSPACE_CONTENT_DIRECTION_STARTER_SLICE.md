# Workspace Content Direction Starter Slice (2026-03-14)

## Problem

The `content direction proposal` skill existed in routing/planning, but there was still no direct Workspace entrypoint for it.

That created a product gap:

- the object model was cleaner in the backend
- but the owner still had to invent the right task wording manually

## What Changed

This slice adds a direct Workspace starter for content-direction work.

- new task starter chip in Workspace:
  - `Content Direction Proposal`
- clicking it now:
  - fills a proposal-producing task brief
  - preselects `content` as the task type when that module is available

The task brief is explicit about the boundary:

- direction proposal, not final draft
- must end with `## Content Direction Proposal`
- should surface gaps instead of fabricating a proposal

## Why This Slice

This is the narrowest way to make the new content-direction object actually usable from the main entrypoint, without redesigning the Workspace shell.

## What Remains Deferred

- no dedicated result card for content-direction proposals yet
- no direct carry-forward from accepted proposal into a draft-generation task yet
- no additional Audit shell changes

## Next Likely Continuation

1. let draft-generation tasks optionally reference an accepted content-direction proposal
2. add a small “from accepted direction” follow-up action in Workspace once the underlying lookup path exists
