# Skill: Write After-Meal Story

## Purpose

Produce a short-form "after-meal story" using the content module SSOT rules and the `after_meal_story` template.

## Inputs

- Required: topic (ask the user if missing)
- Optional: audience, angle, target platform, source notes, idea ID

## Required Files to Load (Progressive Disclosure)

1. `modules/content/MODULE.md`
2. `modules/content/data/voice.yaml`
3. `modules/content/data/anti_patterns.md`
4. `modules/content/data/templates/after_meal_story.md`
5. `modules/content/logs/ideas.jsonl` (only if sourcing topic from backlog or linking an idea ID)

Do not load `x_thread.md` unless the user asks for a thread version.

## Procedure

1. If topic is missing, ask a minimal question: "What topic should the after-meal story cover?"
2. Read the required files listed above.
3. Draft the message strictly in the template section order.
4. Run self-checks before finalizing.
5. Return the final Markdown and write it to:
   - `modules/content/outputs/after_meal_story_<YYYYMMDD>_<topic_slug>.md`

## Self-Checks (Required)

### 1) Anti-pattern scan

- Check banned openings.
- Scan for banned words/phrases by severity tier.
- Verify max 1 em-dash per paragraph.

### 2) Evidence gap scan

- Mark unsupported or uncertain claims with `[NEEDS SOURCE]`.

### 3) Voice alignment check

- Confirm the draft matches the numeric style targets in `voice.yaml`.
- Confirm at least one concrete example/number is present when making a strong claim.
- Confirm at least one counterpoint is included.

## Output Rules

- Keep the exact template headings and order.
- Do not append owner-review proposal sections to this artifact. A finished after-meal story is an output artifact, not a judgment proposal.
- Do not add extra sections.
- If file writing is unavailable, return the exact target path and the full file content ready to save.
