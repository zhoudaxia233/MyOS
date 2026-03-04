#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/context_bundle.sh --task "<request text>" [--module <content|decision|profile|memory>]

What it does:
  - Suggests a target module (if --module is not provided)
  - Prints a minimal file bundle following two-hop loading

Examples:
  scripts/context_bundle.sh --task "write an after-meal story about AI workflows"
  scripts/context_bundle.sh --task "log this investment decision" --module decision
USAGE
}

if [[ $# -eq 0 ]]; then
  usage
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

task=""
module=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --task)
      task="${2:-}"
      shift 2
      ;;
    --module)
      module="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$task" && -z "$module" ]]; then
  echo "Error: provide --task or --module." >&2
  exit 1
fi

route_from_task() {
  python3 - "$REPO_ROOT" "$1" <<'PY'
import json
import sys
from pathlib import Path

repo_root = Path(sys.argv[1])
task = sys.argv[2].lower()
default_module = "decision"

modules_root = repo_root / "modules"
if modules_root.exists():
    for module_dir in sorted([d for d in modules_root.iterdir() if d.is_dir() and not d.name.startswith(".")], key=lambda p: p.name):
        manifest = module_dir / "module.manifest.yaml"
        if not manifest.exists():
            continue
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        keywords = data.get("routing", {}).get("keywords", [])
        if not isinstance(keywords, list):
            keywords = []
        keywords = [str(k).strip().lower() for k in keywords if str(k).strip()]
        if any(k in task for k in keywords):
            print(module_dir.name)
            raise SystemExit(0)

cfg_path = repo_root / "orchestrator/config/routes.json"
if cfg_path.exists():
    try:
        data = json.loads(cfg_path.read_text(encoding="utf-8"))
        default_module = str(data.get("default_module", default_module))
        routes = [r for r in data.get("routes", []) if isinstance(r, dict)]
    except json.JSONDecodeError:
        routes = []
    for rule in routes:
        module = str(rule.get("module", "")).strip()
        keywords = [str(k).lower().strip() for k in rule.get("keywords", [])]
        if any(k and k in task for k in keywords):
            print(module)
            raise SystemExit(0)

print(default_module)
PY
}

if [[ -z "$module" ]]; then
  module="$(route_from_task "$task")"
fi

if [[ -z "$module" ]]; then
  echo "Route: unknown"
  echo "Suggestion: clarify intent or pass --module explicitly."
  exit 0
fi

echo "Route: modules/$module"
echo "Load Level 1: core/ROUTER.md"
echo "Load Level 2: modules/$module/MODULE.md"
echo "Load Level 3 (minimal set):"

case "$module" in
  content)
    cat <<'LIST'
- modules/content/data/voice.yaml
- modules/content/data/anti_patterns.md
- modules/content/data/templates/after_meal_story.md (or x_thread.md if thread task)
- modules/content/skills/write_after_meal_story.md (if after-meal story task)
LIST
    ;;
  decision)
    cat <<'LIST'
- modules/decision/data/heuristics.yaml
- modules/decision/data/impulse_guardrails.yaml (for high-risk decisions)
- modules/decision/data/audit_rules.yaml (for audit tasks)
- modules/decision/skills/log_decision.md or weekly_review.md or precommit_check.md or audit_decision_system.md
- modules/decision/logs/decisions.jsonl (plus failures/experiences/precommit_checks when needed)
LIST
    ;;
  profile)
    cat <<'LIST'
- modules/profile/data/identity.yaml
- modules/profile/data/operating_preferences.yaml
- modules/profile/data/psych_profile.yaml
- modules/profile/skills/update_profile.md or alignment_check.md or profile_snapshot.md or log_trigger_event.md or log_psych_observation.md
- modules/profile/logs/profile_changes.jsonl (if updating profile)
LIST
    ;;
  memory)
    cat <<'LIST'
- modules/memory/data/memory_policy.yaml
- modules/memory/data/pattern_taxonomy.yaml (for pattern extraction)
- modules/memory/skills/ingest_memory.md or extract_chat_patterns.md or distill_weekly.md
- modules/memory/logs/memory_events.jsonl (plus memory_insights.jsonl / chat_patterns.jsonl when needed)
LIST
    ;;
  *)
    echo "Unsupported module: $module" >&2
    exit 1
    ;;
esac
