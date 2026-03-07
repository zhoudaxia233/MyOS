#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/context_bundle.sh --task "<request text>" [--module <content|decision|profile|memory|cognition|principles>]

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
import re
import sys
from pathlib import Path

repo_root = Path(sys.argv[1])
task = sys.argv[2].lower()
default_module = "decision"
token_re = re.compile(r"[a-z0-9]+")


def norm_tokens(text: str) -> list[str]:
    return token_re.findall(str(text).lower())


def norm_keyword(text: str) -> str:
    return " ".join(norm_tokens(text))


def match_keywords(task_tokens: list[str], keywords: list[str]) -> list[str]:
    task_token_set = set(task_tokens)
    task_norm = " ".join(task_tokens)
    matched: list[str] = []
    for raw in keywords:
        keyword = norm_keyword(raw)
        if not keyword:
            continue
        kw_tokens = keyword.split()
        if not kw_tokens:
            continue
        if len(kw_tokens) == 1:
            if kw_tokens[0] in task_token_set:
                matched.append(keyword)
            continue
        if " ".join(kw_tokens) in task_norm:
            matched.append(keyword)
    return matched


def norm_weights(raw: object) -> dict[str, int]:
    if not isinstance(raw, dict):
        return {}
    out: dict[str, int] = {}
    for key, value in raw.items():
        keyword = norm_keyword(str(key))
        if not keyword:
            continue
        try:
            weight = int(value)
        except (TypeError, ValueError):
            continue
        out[keyword] = max(1, min(weight, 100))
    return out


def weight_for(keyword: str, weights: dict[str, int]) -> int:
    configured = weights.get(keyword)
    if configured is not None:
        return configured
    return 2 if " " in keyword else 1


def score_match(task_tokens: list[str], positives: list[str], negatives: list[str], weights: dict[str, int]):
    pos = match_keywords(task_tokens, positives)
    if not pos:
        return None
    neg = match_keywords(task_tokens, negatives)
    score = sum(weight_for(k, weights) for k in pos) - sum(weight_for(k, weights) for k in neg)
    if score <= 0:
        return None
    return score, len(pos), -len(neg)


task_tokens = norm_tokens(task)
manifest_candidates: list[tuple[int, int, int, int, str]] = []

modules_root = repo_root / "modules"
if modules_root.exists():
    module_dirs = sorted([d for d in modules_root.iterdir() if d.is_dir() and not d.name.startswith(".")], key=lambda p: p.name)
    for idx, module_dir in enumerate(module_dirs):
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
        negatives = data.get("routing", {}).get("negative_keywords", [])
        if isinstance(negatives, str):
            negatives = [negatives]
        if not isinstance(negatives, list):
            negatives = []
        weights = norm_weights(data.get("routing", {}).get("keyword_weights"))

        hit = score_match(task_tokens, keywords, negatives, weights)
        if hit:
            score, pos_count, neg_count = hit
            manifest_candidates.append((score, pos_count, neg_count, -idx, module_dir.name))

if manifest_candidates:
    print(max(manifest_candidates)[4])
    raise SystemExit(0)

cfg_path = repo_root / "orchestrator/config/routes.json"
if cfg_path.exists():
    try:
        data = json.loads(cfg_path.read_text(encoding="utf-8"))
        default_module = str(data.get("default_module", default_module))
        routes = [r for r in data.get("routes", []) if isinstance(r, dict)]
    except json.JSONDecodeError:
        routes = []
    route_candidates: list[tuple[int, int, int, int, str]] = []
    for idx, rule in enumerate(routes):
        module = str(rule.get("module", "")).strip()
        keywords = [str(k).lower().strip() for k in rule.get("keywords", [])]
        negatives = [str(k).lower().strip() for k in rule.get("negative_keywords", [])]
        weights = norm_weights(rule.get("keyword_weights"))
        hit = score_match(task_tokens, keywords, negatives, weights)
        if hit and module:
            score, pos_count, neg_count = hit
            route_candidates.append((score, pos_count, neg_count, -idx, module))

    if route_candidates:
        print(max(route_candidates)[4])
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
  cognition)
    cat <<'LIST'
- modules/cognition/data/schema_policy.yaml
- modules/cognition/data/conflict_taxonomy.yaml
- modules/cognition/data/revision_operators.yaml
- modules/cognition/skills/log_schema.md or detect_disequilibrium.md or log_accommodation.md or run_equilibration_review.md
- modules/cognition/logs/schema_versions.jsonl (plus assimilation/disequilibrium/accommodation/equilibration logs when needed)
LIST
    ;;
  principles)
    cat <<'LIST'
- modules/principles/data/constitution.yaml
- modules/principles/data/amendment_policy.yaml
- modules/principles/skills/propose_amendment.md or log_principle_exception.md or run_constitutional_audit.md
- modules/principles/logs/principle_amendments.jsonl (plus principle_exceptions.jsonl when needed)
LIST
    ;;
  *)
    echo "Unsupported module: $module" >&2
    exit 1
    ;;
esac
