# Core Router (Always Load)

This repository is a plugin-based Personal Core OS: a small stable kernel (`core/`) plus pluggable domain modules (`modules/`). The kernel routes requests and enforces loading discipline. Business logic lives inside modules.

## System Intent

- Separate execution from judgment while keeping both aligned over time.
- Keep MyOS thin and model-agnostic: preserve personal governance layers while attaching to replaceable external model/agent systems.
- Execution-heavy tasks route to domain modules (`content`, `memory` ingest workflows).
- Judgment and direction tasks route to `decision`, `profile`, and `principles`.
- Owner operating defaults are anchored in profile SSOT; operational learning is accumulated in memory logs.
- Constitutional direction and override policy are anchored in principles SSOT.

## Interaction Loop

For any user task:

1. **Route** — Read `core/ROUTER.md`, match keywords to a module.
2. **Load module** — Read `modules/{module}/MODULE.md`.
3. **Select skill** — Read `modules/{module}/skills/{skill}.md`. It declares which data files to load.
4. **Execute** — Follow skill instructions, load only declared files.
5. **Write back** — Append results to the appropriate JSONL log.

Two-hop max: ROUTER → MODULE → DATA.

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

## Skill Directory

| Module | Skill | Purpose |
|--------|-------|---------|
| content | `propose_content_direction` | Draft a reviewable content direction proposal |
| content | `write_after_meal_story` | Write a personal narrative story (output-only) |
| decision | `log_decision` | Log a decision through the entry gate with guardrail checks |
| decision | `precommit_check` | Pre-decision risk checklist for high-stakes action |
| decision | `guardrail_override` | Document a guardrail override with audit trail |
| decision | `weekly_review` | Review decision history, emit owner action proposals |
| decision | `audit_decision_system` | Full audit of decision system health |
| decision | `owner_report` | Consolidated owner one-pager |
| profile | `update_profile` | Update identity/preferences YAML with change log |
| profile | `alignment_check` | Check current behavior against profile baselines |
| profile | `log_trigger_event` | Log a psychological trigger event |
| profile | `log_psych_observation` | Log a pattern observation from behavior data |
| profile | `profile_snapshot` | Monthly profile snapshot |
| memory | `ingest_memory` | Ingest ad-hoc reflection events |
| memory | `ingest_learning_asset` | Convert external learning into candidates |
| memory | `import_chat_export` | Import chat export into memory events |
| memory | `extract_chat_patterns` | Extract behavioral patterns from chat history |
| memory | `distill_weekly` | Distill weekly memory into insights |
| cognition | `log_schema` | Log a new schema version (belief update) |
| cognition | `log_assimilation` | Log a successful assimilation event |
| cognition | `detect_disequilibrium` | Detect contradictions or schema tensions |
| cognition | `log_accommodation` | Log a schema revision from disequilibrium |
| cognition | `log_equilibration` | Log a completed equilibration cycle |
| cognition | `run_equilibration_review` | Full equilibration review |
| cognition | `review_timeline` | Cognitive timeline report |
| principles | `propose_amendment` | Propose a constitutional principle amendment |
| principles | `log_principle_exception` | Log a deviation from a core principle |
| principles | `run_constitutional_audit` | Audit decision system against constitutional principles |

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

## Governance Constraints

Hard rules — not guidelines:

1. **Hierarchy**: Principles > Decisions > Cognition > Profile > Memory.
2. **Append-only**: Never overwrite JSONL records. Archive via `status: archived`. `_schema` is always line 1.
3. **IDs**: Format `<prefix>_<YYYYMMDD>_<3-digit-seq>`. Let MCP tools or CLI generate them.
4. **Review → Promote**: Never auto-promote candidates without owner confirmation.
5. **Cross-module refs**: ID-only references (e.g. `principle_refs: pr_0001`). Never copy content.
6. **Data classification** (in order): long-horizon → `principles`; gate outcome → `decision`; schema revision → `cognition`; stable trait → `profile`; otherwise → `memory`.
