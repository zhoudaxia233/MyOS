#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/append_jsonl.sh <jsonl_file> '<json_object>'

Examples:
  scripts/append_jsonl.sh modules/decision/logs/decisions.jsonl '{"id":"dc_20260227_003","created_at":"2026-02-27T09:00:00Z","status":"active","domain":"project","decision":"Ship v1","options":["ship","delay"],"reasoning":"Scope complete","risks":["minor bugs"],"expected_outcome":"faster feedback","time_horizon":"1 week","confidence":7}'

Notes:
  - This script APPENDS one line; it never rewrites historical records.
  - The target file must already exist and have a _schema header on line 1.
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || $# -lt 2 ]]; then
  usage
  exit 0
fi

file="$1"
json_line="$2"

if [[ ! -f "$file" ]]; then
  echo "Error: file not found: $file" >&2
  exit 1
fi

first_line="$(head -n 1 "$file")"
if [[ "$first_line" != *'"_schema"'* ]]; then
  echo "Error: first line must contain a _schema header object." >&2
  exit 1
fi

trimmed="$(printf '%s' "$json_line" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')"
if [[ "$trimmed" != \{*\} ]]; then
  echo "Error: second argument must be a single JSON object string." >&2
  exit 1
fi

if [[ "$trimmed" == *$'\n'* ]]; then
  echo "Error: JSON object must be single-line for JSONL." >&2
  exit 1
fi

printf '%s\n' "$trimmed" >> "$file"
echo "Appended 1 JSONL record to $file"
