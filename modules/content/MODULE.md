# Content Module

## Purpose

This module handles the content creation pipeline for short-form writing, thread drafting, editing, and publishing logs. It stores canonical voice/tone constraints, anti-patterns, templates, and append-only records for ideas and published posts.

## Scope

- Content ideation support
- Drafting and editing using templates
- Voice consistency enforcement
- Post publication logging

## File Inventory

### Instructions and skills

- `modules/content/MODULE.md`: Module purpose, workflows, loading rules, and behavioral instructions
- `modules/content/skills/write_fahou_message.md`: Task-specific skill for producing a short-form "fahou" message

### Canonical data (SSOT)

- `modules/content/data/voice.yaml`: Voice profile and numeric style targets
- `modules/content/data/anti_patterns.md`: Banned openings, banned phrases, and structural traps
- `modules/content/data/templates/fahou_message.md`: Required output structure for fahou messages
- `modules/content/data/templates/x_thread.md`: X/Twitter thread skeleton template

### Logs (append-only JSONL)

- `modules/content/logs/ideas.jsonl`: Idea backlog and scoring
- `modules/content/logs/posts.jsonl`: Published post registry and metrics snapshots

### Outputs

- `modules/content/outputs/`: Generated drafts and finalized content artifacts

## Workflow

1. Idea
   - Read `ideas.jsonl` only if sourcing from backlog.
   - Select idea by ID when possible.
2. Outline
   - Load the relevant template only (`fahou_message.md` or `x_thread.md`).
3. Draft
   - Load `voice.yaml` and write into the chosen template structure.
4. Edit
   - Load `anti_patterns.md` and run quality gates.
5. Publish
   - Finalize copy for target platform.
6. Post-log
   - Append a record to `posts.jsonl` (never overwrite existing records).

## Progressive Loading Rules (Required)

- Default load for writing tasks: `voice.yaml` + `anti_patterns.md` + one relevant template.
- Do not load both templates unless the user explicitly asks to compare formats.
- Only load `ideas.jsonl` if the task requires idea selection or linkage.
- Only load `posts.jsonl` if the task requires publication logging or performance lookup.

## Quality Gates Checklist

- Hook clarity: Is the opening concrete and immediately understandable?
- Specificity: Are there numbers, named entities, or concrete claims where appropriate?
- Banned words scan: Check against `anti_patterns.md` before finalizing.
- Evidence check: Mark unsupported claims as `[NEEDS SOURCE]`.

<instructions>
- Follow `modules/content/data/voice.yaml` numeric style targets.
- Avoid all banned openings, banned phrases, and structural traps in `modules/content/data/anti_patterns.md`.
- Keep output in the exact section structure required by the selected template.
- Flag unsourced or uncertain claims with `[NEEDS SOURCE]`.
- Prefer precise nouns and verbs over hype language.
- If the user asks for a platform-specific variant, adapt wording but keep the template structure unless explicitly told otherwise.
</instructions>
