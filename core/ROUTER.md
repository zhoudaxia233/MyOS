# Core Router (Always Load)

This repository is a plugin-based Personal Core OS: a small stable kernel (`core/`) plus pluggable domain modules (`modules/`). The kernel routes requests and enforces loading discipline. Business logic lives inside modules.

## System Intent

- Separate execution from judgment while keeping both aligned over time.
- Execution-heavy tasks route to domain modules (`content`, `memory` ingest workflows).
- Judgment and direction tasks route to `decision` and `profile`.
- Personal direction is anchored in profile SSOT; operational learning is accumulated in memory logs.

## Progressive Disclosure Rules (Required)

- Level 1 (always load): `core/ROUTER.md`
- Level 2 (load only if relevant): `modules/<module>/MODULE.md`
- Level 3 (load only when needed): specific files referenced by that module (YAML/JSONL/Markdown/templates)
- Do not preload all module data.
- Do not load unrelated modules.

## Two-Hop Maximum Principle

Use this path only:

- `ROUTER -> MODULE -> DATA`

Do not go beyond two hops unless the module explicitly instructs a necessary file read for the current task.

## Routing Decision Table

| User intent / task | Route to module | Notes |
|---|---|---|
| writing, publishing, editing, tone, messaging, thread drafting | `modules/content` | Content creation and post logging |
| ideas for posts, content templates, hook improvement | `modules/content` | Load templates only if needed |
| decisions, prioritization, planning tradeoffs, review patterns | `modules/decision` | Decision logs + heuristics |
| post-mortem, failure analysis, lessons learned | `modules/decision` | Use failures / experiences logs |
| weekly review of choices and patterns | `modules/decision` | Use weekly review workflow |
| profile updates, values, goals, personal alignment checks | `modules/profile` | Identity and operating preference SSOT |
| memory ingest, reflection capture, weekly distillation | `modules/memory` | Append raw memory, distill reusable insights |

## Exact Routing Instructions (Required)

1. First determine the target module from the user intent.
2. Then load `modules/<name>/MODULE.md` only.
3. Then load only the specific data/log/template files explicitly referenced in that module for the current task.
4. Do not load files from other modules unless the user explicitly requests cross-module work and the module instructions permit it.

## Kernel Boundaries

- Kernel files define routing, global rules, schemas, and shared terms.
- Modules own domain workflows, SSOT data, and append-only logs.
- Cross-module references are ID-only (no content duplication).
