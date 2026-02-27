# Personal Core OS

Personal Core OS is a file-based, plugin-based personal operating system for human + AI collaboration.

It is designed as a **stable core** for long-term consistency:

- Agents execute workflows
- The system preserves judgment, priorities, and memory
- Future actions stay aligned with enduring goals instead of short-term noise

## North Star

Build a durable operating center that separates **execution** from **judgment**.

- Execution: content, projects, research, routine workflows
- Judgment: decisions, tradeoffs, lessons, evolving heuristics

This repository is the control layer that keeps those two coherent over time.

## What This Repo Is (and Is Not)

### Is

- A protocol and memory architecture for AI-assisted work
- A file-first system with SSOT and append-only logs
- A modular plugin structure with low coupling

### Is not

- A monolithic application server
- A database-heavy stack by default
- A tightly coupled agent framework

## Core Principles

1. Small stable kernel, domain logic in modules
2. Progressive disclosure (minimal context loading)
3. Plugin architecture with ID-based references
4. SSOT: canonical content is not duplicated
5. Safety and integrity with append-only JSONL logs
6. Human-readable, Git-versioned system

## Repository Structure

```text
/
  README.md
  README-zh.md
  ROADMAP.md
  CHECKLIST.md
  core/
    ROUTER.md
    RULES.md
    SCHEMAS.md
    GLOSSARY.md
  modules/
    content/
    decision/
    _template/
  scripts/
    append_jsonl.sh
```

## Execution Model (How It Actually Runs)

This repo does not "run" itself like a web app. It is executed by an agent runtime (for example, Codex/ChatGPT workflows) that follows these steps:

1. Load `core/ROUTER.md` (always)
2. Route the user request to one module
3. Load `modules/<name>/MODULE.md`
4. Load only files required for the current task
5. Produce output and/or append logs

Two-hop rule:

- `ROUTER -> MODULE -> DATA`

Do not load unrelated modules.

## Progressive Disclosure

- Level 1: kernel route/index (`core/ROUTER.md`)
- Level 2: module instruction (`modules/<name>/MODULE.md`)
- Level 3: only relevant data/log/template files

This keeps context small and task-focused.

## Modules

### Content (`modules/content`)

Purpose:

- Content workflow from idea to publishing log

Core assets:

- Voice SSOT: `modules/content/data/voice.yaml`
- Anti-patterns: `modules/content/data/anti_patterns.md`
- Templates: `modules/content/data/templates/`
- Logs: `modules/content/logs/ideas.jsonl`, `modules/content/logs/posts.jsonl`
- Skill: `modules/content/skills/write_fahou_message.md`

### Decision (`modules/decision`)

Purpose:

- Preserve decision quality over time through logs and reviews

Core assets:

- Heuristics SSOT: `modules/decision/data/heuristics.yaml`
- Logs: `decisions.jsonl`, `failures.jsonl`, `experiences.jsonl`
- Skills: `log_decision.md`, `weekly_review.md`

### Template (`modules/_template`)

Purpose:

- Starter scaffold for new modules

## Data Integrity Rules

- JSONL logs are append-only
- Never rewrite or delete historical lines
- Deletion uses `"status": "archived"`
- Every JSONL file starts with a `_schema` header on line 1

## How To Use (Quick Start)

### 1) Content generation

- Ask agent: "Write a fahou message about <topic>"
- Agent should route to `modules/content`
- Output is written under `modules/content/outputs/`

### 2) Log a decision

- Ask agent: "Log this decision: ..."
- Agent routes to `modules/decision`
- Append a record in `modules/decision/logs/decisions.jsonl`

### 3) Weekly review

- Ask agent: "Run weekly decision review"
- Agent reads last 7 days from decision logs
- Output saved to `modules/decision/outputs/weekly_review_<YYYYMMDD>.md`

## Safe Log Appending Script

Use:

```bash
scripts/append_jsonl.sh <jsonl_file> '<json_object>'
```

Example:

```bash
scripts/append_jsonl.sh modules/decision/logs/decisions.jsonl '{"id":"dc_20260227_003","created_at":"2026-02-27T09:00:00Z","status":"active","domain":"project","decision":"Ship v1","options":["ship","delay"],"reasoning":"Scope complete","risks":["minor bugs"],"expected_outcome":"faster feedback","time_horizon":"1 week","confidence":7}'
```

## Validation

Before commits, review:

- `CHECKLIST.md`

## Current Version

- v0.1: Stable kernel + content + decision modules + append-only log discipline
- Planned v0.2: deeper personal profile, memory distillation, decision guardrails
