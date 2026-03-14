from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

RUN_LOG_PATH = "orchestrator/logs/runs.jsonl"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists() or not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        if i == 1 and '"_schema"' in line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _parse_iso8601(ts: str) -> datetime | None:
    text = str(ts or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def _truncate(text: str, limit: int = 72) -> str:
    value = " ".join(str(text or "").split())
    if len(value) <= limit:
        return value
    return value[: max(0, limit - 3)].rstrip() + "..."


def _normalize_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _influence_key(item: dict[str, Any]) -> str:
    artifact_ref = _normalize_text(item.get("artifact_ref"))
    if artifact_ref:
        return artifact_ref
    artifact_type = _normalize_text(item.get("artifact_type")) or "artifact"
    title = _normalize_text(item.get("title")) or _normalize_text(item.get("source_summary")) or "unknown"
    return f"{artifact_type}:{title}"


def _normalize_influence(item: Any) -> dict[str, Any] | None:
    if not isinstance(item, dict):
        return None
    summary = {
        "artifact_ref": _normalize_text(item.get("artifact_ref")),
        "artifact_type": _normalize_text(item.get("artifact_type")) or "artifact",
        "title": _normalize_text(item.get("title")) or _normalize_text(item.get("artifact_ref")) or "artifact",
        "source_summary": _normalize_text(item.get("source_summary")),
        "selection_reason": _normalize_text(item.get("selection_reason")),
        "scope_modules": [str(part).strip() for part in item.get("scope_modules", []) if str(part).strip()]
        if isinstance(item.get("scope_modules"), list)
        else [],
    }
    summary["_key"] = _influence_key(summary)
    return summary


def _public_influence(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_ref": summary.get("artifact_ref"),
        "artifact_type": summary.get("artifact_type"),
        "title": summary.get("title"),
        "source_summary": summary.get("source_summary"),
        "selection_reason": summary.get("selection_reason"),
        "scope_modules": list(summary.get("scope_modules", [])),
    }


def list_recent_runtime_influence_runs(
    repo_root: Path,
    *,
    limit_runs: int = 6,
) -> list[dict[str, Any]]:
    rows = _read_jsonl(repo_root / RUN_LOG_PATH)
    run_rows: list[tuple[datetime, dict[str, Any]]] = []
    for row in rows:
        if str(row.get("status", "active")).strip().lower() != "active":
            continue
        created_at = _parse_iso8601(str(row.get("created_at", "")))
        if created_at is None:
            continue
        run_rows.append((created_at, row))

    run_rows.sort(key=lambda item: item[0], reverse=True)

    recent: list[dict[str, Any]] = []
    for _, row in run_rows[: max(1, int(limit_runs))]:
        raw_influences = row.get("runtime_influences")
        seen: set[str] = set()
        influences: list[dict[str, Any]] = []
        if isinstance(raw_influences, list):
            for item in raw_influences:
                normalized = _normalize_influence(item)
                if normalized is None:
                    continue
                key = str(normalized.get("_key", "")).strip()
                if not key or key in seen:
                    continue
                seen.add(key)
                influences.append(normalized)

        recent.append(
            {
                "run_ref": _normalize_text(row.get("id")),
                "created_at": _normalize_text(row.get("created_at")),
                "module": _normalize_text(row.get("module")) or "unknown",
                "task_preview": _truncate(str(row.get("task", "")).strip(), limit=84) or "-",
                "influence_count": len(influences),
                "influences": [_public_influence(item) for item in influences],
                "_influence_map": {str(item.get("_key")): item for item in influences},
            }
        )
    return recent


def summarize_recent_runtime_influence_drift(
    repo_root: Path,
    *,
    limit_runs: int = 6,
    top_limit: int = 6,
) -> dict[str, Any]:
    recent_runs = list_recent_runtime_influence_runs(repo_root, limit_runs=limit_runs)
    if not recent_runs:
        return {
            "window_runs": max(1, int(limit_runs)),
            "runs_considered": 0,
            "recent_runs": [],
            "top_artifacts": [],
            "latest_delta": {
                "latest_run_ref": None,
                "previous_run_ref": None,
                "comparison_basis": "none",
                "latest_influence_total": 0,
                "previous_influence_total": 0,
                "stable_total": 0,
                "added": [],
                "dropped": [],
                "changed": False,
            },
        }

    counter: Counter[str] = Counter()
    first_seen_order: dict[str, int] = {}
    examples: dict[str, dict[str, Any]] = {}
    for run_index, run in enumerate(recent_runs):
        influence_map = run.get("_influence_map", {})
        if not isinstance(influence_map, dict):
            continue
        for key, item in influence_map.items():
            counter[str(key)] += 1
            first_seen_order.setdefault(str(key), run_index)
            if isinstance(item, dict) and key not in examples:
                examples[str(key)] = item

    top_keys = sorted(counter.keys(), key=lambda key: (-counter[key], first_seen_order.get(key, 9999), key))
    top_artifacts: list[dict[str, Any]] = []
    for key in top_keys[: max(1, int(top_limit))]:
        example = examples.get(key, {})
        top_artifacts.append(
            {
                **_public_influence(example),
                "run_count": int(counter[key]),
                "run_share": round(float(counter[key]) / float(len(recent_runs)), 3),
            }
        )

    latest = recent_runs[0]
    previous: dict[str, Any] | None = None
    comparison_basis = "none"
    for candidate in recent_runs[1:]:
        if str(candidate.get("module", "")).strip() == str(latest.get("module", "")).strip():
            previous = candidate
            comparison_basis = "same_module_previous"
            break
    if previous is None and len(recent_runs) > 1:
        previous = recent_runs[1]
        comparison_basis = "previous_any"

    latest_map = latest.get("_influence_map", {}) if isinstance(latest.get("_influence_map"), dict) else {}
    previous_map = previous.get("_influence_map", {}) if isinstance((previous or {}).get("_influence_map"), dict) else {}
    latest_keys = set(latest_map.keys())
    previous_keys = set(previous_map.keys())
    added_keys = sorted(latest_keys - previous_keys)
    dropped_keys = sorted(previous_keys - latest_keys)

    latest_delta = {
        "latest_run_ref": latest.get("run_ref"),
        "previous_run_ref": (previous or {}).get("run_ref"),
        "comparison_basis": comparison_basis,
        "latest_influence_total": len(latest_keys),
        "previous_influence_total": len(previous_keys),
        "stable_total": len(latest_keys & previous_keys),
        "added": [_public_influence(latest_map[key]) for key in added_keys if key in latest_map],
        "dropped": [_public_influence(previous_map[key]) for key in dropped_keys if key in previous_map],
        "changed": bool(added_keys or dropped_keys),
    }

    public_runs: list[dict[str, Any]] = []
    for run in recent_runs:
        public_runs.append(
            {
                "run_ref": run.get("run_ref"),
                "created_at": run.get("created_at"),
                "module": run.get("module"),
                "task_preview": run.get("task_preview"),
                "influence_count": run.get("influence_count"),
                "influences": run.get("influences", []),
            }
        )

    return {
        "window_runs": max(1, int(limit_runs)),
        "runs_considered": len(public_runs),
        "recent_runs": public_runs,
        "top_artifacts": top_artifacts,
        "latest_delta": latest_delta,
    }
