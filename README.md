# Personal Core OS

Personal Core OS is a file-based, plugin-based operating system for long-horizon human + AI collaboration.

It provides a stable center so agents can execute workflows while decisions, priorities, and identity remain coherent over time.

## North Star

Separate **execution** from **judgment** without disconnecting them.

- Execution: content production, project workflows, memory ingestion
- Judgment: decisions, tradeoffs, profile alignment, heuristic updates

## What This Repo Is

- A control plane for agent behavior (routing, rules, schemas, skills)
- A file-first memory system (Markdown/YAML/JSONL)
- A modular architecture with low coupling and ID-based references

## Core Principles

1. Small stable kernel, domain logic in modules
2. Progressive disclosure (minimal context loading)
3. SSOT in canonical data files
4. Append-only logs for historical integrity
5. Human-readable and Git-versioned

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
    profile/
    memory/
    _template/
  scripts/
    append_jsonl.sh
    context_bundle.sh
```

## Execution Model

This repository is not a monolithic app server. It is executed by an agent runtime that follows this sequence:

1. Load `core/ROUTER.md` (always)
2. Route the request to one module
3. Load `modules/<name>/MODULE.md`
4. Load only task-required files
5. Produce output and/or append logs

Two-hop loading rule:

- `ROUTER -> MODULE -> DATA`

## Modules

### `modules/content`

- Purpose: content pipeline from idea to post log
- SSOT: `voice.yaml`, `anti_patterns.md`, templates
- Logs: `ideas.jsonl`, `posts.jsonl`
- Skill: `write_fahou_message.md`

### `modules/decision`

- Purpose: decision memory, failure learning, weekly reviews
- SSOT: `heuristics.yaml`, `impulse_guardrails.yaml`
- Logs: `decisions.jsonl`, `failures.jsonl`, `experiences.jsonl`, `precommit_checks.jsonl`
- Skills: `log_decision.md`, `precommit_check.md`, `weekly_review.md`

### `modules/profile`

- Purpose: personal direction and alignment baseline
- SSOT: `identity.yaml`, `operating_preferences.yaml`
- Logs: `profile_changes.jsonl`, `trigger_events.jsonl`
- Skills: `update_profile.md`, `alignment_check.md`

### `modules/memory`

- Purpose: evolving memory ingestion and weekly distillation
- SSOT: `memory_policy.yaml`
- Logs: `memory_events.jsonl`, `memory_insights.jsonl`
- Skills: `ingest_memory.md`, `distill_weekly.md`

### `modules/_template`

- Purpose: starter scaffold for new modules

## How To Use

### 1) Get a context bundle quickly

```bash
scripts/context_bundle.sh --task "write a fahou message about risk discipline"
```

This prints suggested route and minimal files to load.

### 2) Run a content task

- Prompt your agent with the task
- Follow `content` module files from the bundle
- Save outputs under `modules/content/outputs/`

### 3) Run a decision task

- Use precommit check for high-risk decisions
- Log final decision into `modules/decision/logs/decisions.jsonl`

### 4) Update profile or ingest memory

- Profile updates: `modules/profile/skills/update_profile.md`
- Memory ingest: `modules/memory/skills/ingest_memory.md`

## Data Integrity Rules

- JSONL logs are append-only
- Do not rewrite or delete historical records
- Use `"status": "archived"` for deactivation
- Keep `_schema` header object on line 1 of every JSONL file

## Utility Scripts

### Safe append

```bash
scripts/append_jsonl.sh <jsonl_file> '<json_object>'
```

### Route + minimal context planner

```bash
scripts/context_bundle.sh --task "<your request>"
```

## Validation

- Use `CHECKLIST.md` before commit

## Version

- v0.1: kernel + content + decision base
- v0.2: profile + memory modules, decision impulse guardrails, context bundle runner
