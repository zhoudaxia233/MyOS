# Core Router (Always Load)

This repository is a plugin-based Personal Core OS: a small stable kernel (`core/`) plus pluggable domain modules (`modules/`). The kernel routes requests and enforces loading discipline. Business logic lives inside modules.

## System Intent

- Separate execution from judgment while keeping both aligned over time.
- Execution-heavy tasks route to domain modules (`content`, `memory` ingest workflows).
- Judgment and direction tasks route to `decision`, `profile`, and `principles`.
- Owner operating defaults are anchored in profile SSOT; operational learning is accumulated in memory logs.
- Constitutional direction and override policy are anchored in principles SSOT.

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
| decision audit, risk governance, exception reports | `modules/decision` | Audit-first owner review outputs |
| profile updates, values, goals, personal alignment checks | `modules/profile` | Identity and operating preference SSOT |
| psychological patterning, trigger analysis, drift snapshot | `modules/profile` | Non-clinical psych profiling and stabilizers |
| memory ingest, reflection capture, weekly distillation | `modules/memory` | Append raw memory, distill reusable insights |
| chat pattern extraction, paradigm mining | `modules/memory` | Extract recurring patterns from chat events |
| schema mapping, mental model versioning, cognitive conflict analysis | `modules/cognition` | Schema-layer cognitive adaptation workflows |
| assimilation, accommodation, disequilibrium, equilibration tracking | `modules/cognition` | Structural cognition evolution over time |
| constitution updates, enduring principles, strategic constraints | `modules/principles` | Governing charter and amendment protocol |
| principle exceptions, constitutional audits, drift at governance layer | `modules/principles` | Exception trail and owner-facing constitutional review |

## Exact Routing Instructions (Required)

1. First determine the target module from the user intent.
2. Then load `modules/<name>/MODULE.md` only.
3. Then load only the specific data/log/template files explicitly referenced in that module for the current task.
4. Do not load files from other modules unless the user explicitly requests cross-module work and the module instructions permit it.

## Kernel Boundaries

- Kernel files define routing, global rules, schemas, and shared terms.
- Ontology and classification rules are defined in `core/ONTOLOGY.md` and `core/BOUNDARY_RULES.md`.
- Modules own domain workflows, SSOT data, and append-only logs.
- Cross-module references are ID-only (no content duplication).
- Runtime keyword routing rules are discovered from `modules/<name>/module.manifest.yaml` (with optional legacy fallback from `orchestrator/config/routes.json`).
