# Skill: Propose Content Direction

## Purpose

Distill a topic into one reviewable content-direction proposal before drafting. This skill is for framing, angle, and emphasis judgment, not for writing the final post.

## Inputs

- Required: topic
- Optional: audience, platform, objective, source notes, idea ID

## Required Files to Load (Progressive Disclosure)

1. `modules/content/MODULE.md`
2. `modules/content/data/voice.yaml`
3. `modules/content/data/anti_patterns.md`
4. `modules/content/data/templates/content_direction_proposal.md`
5. `modules/content/logs/ideas.jsonl` (only if sourcing from backlog or linking an idea ID)

## Procedure

1. If the topic is missing, ask one minimal clarifying question.
2. Read voice constraints and anti-patterns before proposing any angle.
3. Consider 2-4 plausible directions internally; surface only the best ones in the artifact.
4. Write the support sections in the template order.
5. If the context supports a stable recommendation, end with exactly one `## Content Direction Proposal` section.
6. Keep the proposal section distilled: 1-3 bullets only, focused on the direction itself.
7. Save the artifact to:
   - `modules/content/outputs/content_direction_<YYYYMMDD>_<topic_slug>.md`

## Constraints

- Do not write a full after-meal story or thread draft here.
- Do not use the task title, file path, or run metadata as proposal text.
- Keep the proposal focused on angle, framing, and what to emphasize or avoid.
- If evidence is thin or context is missing, state what is missing and do not fabricate a `## Content Direction Proposal` section.
