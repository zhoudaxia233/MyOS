# Personal Core OS

Personal Core OS is a file-based operating system for human + AI collaboration.

It is designed as a durable control plane:

- Agents execute workflows
- The system preserves identity, memory, and decision discipline
- The owner audits exceptions and approves strategic changes

## North Star

Separate execution from judgment while keeping them aligned over time.

- Execution: content work, project throughput, daily memory capture
- Judgment: decisions, guardrails, profile alignment, drift control

## Core Architecture

1. Small stable kernel in `core/`
2. Pluggable modules in `modules/`
3. Progressive disclosure: `ROUTER -> MODULE -> DATA`
4. SSOT in canonical YAML/MD files
5. Append-only JSONL logs for historical integrity

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
  routines/
    cadence.yaml
    CADENCE.md
  scripts/
    append_jsonl.sh
    context_bundle.sh
    run_cycle.sh
```

## Modules

### `modules/content`

- Role: content pipeline from idea to publication log
- SSOT: voice, anti-patterns, templates
- Logs: ideas and posts

### `modules/decision`

- Role: decision memory + risk governance + audit outputs
- SSOT: heuristics, impulse guardrails, audit rules
- Logs: decisions, failures, experiences, precommit checks
- Owner-facing output: decision audit report

### `modules/profile`

- Role: personal identity, operating preferences, psych stabilizers
- SSOT: identity, operating preferences, psych profile
- Logs: profile changes, trigger events, psych observations

### `modules/memory`

- Role: daily memory ingestion + pattern extraction + weekly distillation
- SSOT: memory policy, pattern taxonomy
- Logs: memory events, memory insights, chat paradigms

## Runtime Model

This repository is executed by an agent runtime (not by a monolithic app server):

1. Load `core/ROUTER.md`
2. Determine target module
3. Load `modules/<name>/MODULE.md`
4. Load only task-required files
5. Produce output and/or append one log line per record

## Fast Usage

### 1) Get a route and minimal context bundle

```bash
scripts/context_bundle.sh --task "extract chat paradigms from this week"
```

### 2) Run daily/weekly/monthly cycle checklist

```bash
scripts/run_cycle.sh daily
scripts/run_cycle.sh weekly
scripts/run_cycle.sh monthly
```

### 3) High-risk decision flow

1. Run precommit check (`modules/decision/skills/precommit_check.md`)
2. Log decision with `guardrail_check_id`
3. Include in weekly review and audit report

### 4) Pattern extraction flow

1. Ingest chat/reflection events (`ingest_memory.md`)
2. Extract paradigms (`extract_chat_patterns.md`)
3. Distill weekly memory (`distill_weekly.md`)

### 5) Profile adaptation flow

1. Log trigger events and psych observations
2. Run monthly profile snapshot
3. Update profile YAML baselines with append-only change log

## Data Integrity

- Never overwrite JSONL logs; append only
- Preserve `_schema` header on line 1
- Archive by `"status": "archived"`
- Cross-module references are ID-only

## Current Version

- v0.1: Kernel + content + decision base
- v0.2: Profile + memory modules + guardrails
- v0.3-first: Chat paradigm extraction, psych profiling, audit-first decision view, cadence runbook
