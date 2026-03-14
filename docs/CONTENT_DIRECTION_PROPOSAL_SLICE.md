# Content Direction Proposal Slice (2026-03-14)

## Problem

After the review-boundary fix and explicit weekly-review proposal emitter, the content module still lacked a dedicated way to produce a true reviewable object.

That meant content work had two bad options:

- overload normal draft artifacts with governance semantics
- or have no clean owner-review object for content direction at all

## What Changed

This slice introduces a dedicated content-strategy path:

- new skill:
  - `modules/content/skills/propose_content_direction.md`
- new template:
  - `modules/content/data/templates/content_direction_proposal.md`
- new manifest route:
  - `content direction`
  - `content angle`
  - `content framing`
  - `editorial angle`

The new skill is explicitly proposal-producing:

- support analysis stays in the artifact body
- the review object appears only in the final `## Content Direction Proposal` section

At the same time, normal draft skills remain output-only:

- `write_after_meal_story` still produces a draft artifact
- it must not append proposal-review sections

## Why This Slice

This is the smallest way to give content a real reviewable object without polluting everyday drafting.

It preserves the layered model:

- draft -> output artifact
- content direction -> judgment proposal

## What Remains Deferred

- no new content publishing workflow
- no automatic handoff from direction proposal to draft generation
- no unified proposal schema across every module
- no UI redesign beyond the existing proposal-review lane

## Next Likely Continuation

If this holds up:

1. add a one-click workspace starter for `content direction proposal`
2. let content draft tasks optionally reference an accepted direction proposal as input context
3. decide whether proposal artifacts should later gain typed metadata beyond markdown section conventions
