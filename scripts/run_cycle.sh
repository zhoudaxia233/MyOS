#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/run_cycle.sh <daily|weekly|monthly>

Purpose:
  Print actionable routine tasks and required files for the selected cycle.
USAGE
}

if [[ $# -ne 1 ]]; then
  usage
  exit 1
fi

cycle="$1"

case "$cycle" in
  daily)
    cat <<'OUT'
Cycle: daily

1) Memory ingest
- Module: modules/memory
- Skill: modules/memory/skills/ingest_memory.md
- Logs: modules/memory/logs/memory_events.jsonl

2) Trigger logging (if event occurred)
- Module: modules/profile
- Skill: modules/profile/skills/log_trigger_event.md
- Log: modules/profile/logs/trigger_events.jsonl
OUT
    ;;
  weekly)
    cat <<'OUT'
Cycle: weekly

1) Decision weekly review
- Module: modules/decision
- Skill: modules/decision/skills/weekly_review.md
- Output: modules/decision/outputs/weekly_review_<YYYYMMDD>.md

2) Memory weekly distillation
- Module: modules/memory
- Skill: modules/memory/skills/distill_weekly.md
- Output: modules/memory/outputs/weekly_memory_<YYYYMMDD>.md

3) Decision audit report
- Module: modules/decision
- Skill: modules/decision/skills/audit_decision_system.md
- Template: modules/decision/outputs/templates/decision_audit_report.md
- Output: modules/decision/outputs/decision_audit_<YYYYMMDD>.md
OUT
    ;;
  monthly)
    cat <<'OUT'
Cycle: monthly

1) Profile snapshot
- Module: modules/profile
- Skill: modules/profile/skills/profile_snapshot.md
- Output: modules/profile/outputs/profile_snapshot_<YYYYMMDD>.md
OUT
    ;;
  *)
    usage
    exit 1
    ;;
esac
