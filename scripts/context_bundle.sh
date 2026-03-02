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
  scripts/context_bundle.sh --task "write a fahou message about AI workflows"
  scripts/context_bundle.sh --task "log this investment decision" --module decision
USAGE
}

if [[ $# -eq 0 ]]; then
  usage
  exit 1
fi

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
  local t
  t="$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')"
  if [[ "$t" =~ write|publish|thread|tone|edit|message|post|draft ]]; then
    echo "content"
    return
  fi
  if [[ "$t" =~ decision|priority|plan|review|failure|post-mortem|risk|tradeoff|audit|governance|exception ]]; then
    echo "decision"
    return
  fi
  if [[ "$t" =~ profile|goal|value|identity|alignment|temperament|trigger|psych|drift ]]; then
    echo "profile"
    return
  fi
  if [[ "$t" =~ memory|journal|reflect|reflection|insight|distill|summary|paradigm|pattern|extract ]]; then
    echo "memory"
    return
  fi
  echo ""
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
- modules/content/data/templates/fahou_message.md (or x_thread.md if thread task)
- modules/content/skills/write_fahou_message.md (if fahou task)
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
