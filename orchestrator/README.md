# Orchestrator

The orchestrator is the execution engine layer for Personal Core OS.

It reads kernel/module protocols, builds minimal context bundles, runs a provider, and writes outputs/logs safely.

## Design Goals

- Keep protocol/data in `core/` and `modules/`
- Keep execution logic in `orchestrator/`
- Preserve append-only integrity for JSONL logs
- Support both no-API manual mode and optional API mode

## Architecture

- `router.py`: map task intent to module
- `loader.py`: load two-hop context bundle (`ROUTER -> MODULE -> DATA`)
- `planner.py`: pick skill + output target
- `runner.py`: invoke provider
- `writer.py`: write outputs and append run logs
- `validators.py`: guardrails for JSONL and append-only behavior
- `providers/`: provider adapters (`manual`, `openai`)

## Quick Start

### 1) Manual mode (no API)

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py run \
  --task "run weekly decision review" \
  --provider manual
```

This creates an execution packet file for an agent to execute.

### 2) Optional OpenAI mode

Set env vars:

- `OPENAI_API_KEY`
- `OPENAI_MODEL` (optional, defaults from config)

Run:

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py run \
  --task "run weekly decision review" \
  --provider openai
```

## CLI

```bash
python3 /Users/closears/MyOS/orchestrator/src/main.py run --task "..." [--provider manual|openai] [--module <name>]
python3 /Users/closears/MyOS/orchestrator/src/main.py inspect --task "..."
```
