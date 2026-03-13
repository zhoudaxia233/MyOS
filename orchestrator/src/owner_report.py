from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from idgen import next_id_for_path
from learning_console import summarize_learning_pipeline, summarize_learning_pipeline_trend
from metrics import compute_drift_metrics
from validators import append_jsonl

OWNER_TODOS_SCHEMA = {
    "_schema": {
        "name": "owner_todos",
        "version": "1.0",
        "fields": [
            "id",
            "created_at",
            "status",
            "metric",
            "priority",
            "reason",
            "action",
            "owner_report_ref",
            "todo_signature",
            "resolution_of",
            "note",
        ],
        "notes": "append-only",
    }
}


def _parse_iso8601(ts: str) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out: list[dict] = []
    for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        if i == 1 and '"_schema"' in line:
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                out.append(obj)
        except json.JSONDecodeError:
            continue
    return out


def _window_filter(records: list[dict], now: datetime, days: int) -> list[dict]:
    cutoff = now - timedelta(days=days)
    out: list[dict] = []
    for r in records:
        created = _parse_iso8601(str(r.get("created_at", "")))
        if created is None:
            continue
        if created >= cutoff:
            out.append(r)
    return out


def _latest_file(repo_root: Path, pattern: str) -> str | None:
    files = sorted(repo_root.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        return None
    return str(files[0].relative_to(repo_root))


def _read_text(repo_root: Path, rel_path: str | None) -> str:
    if not rel_path:
        return ""
    path = repo_root / rel_path
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def _parse_metrics_status_from_report(text: str) -> dict[str, str]:
    mapping = {
        "precommit coverage": "precommit_coverage",
        "cooldown compliance": "cooldown_compliance",
        "repeat failure rate": "repeat_failure_rate",
        "profile drift rate": "profile_drift_rate",
        "unresolved disequilibrium rate": "unresolved_disequilibrium_rate",
        "equilibration quality rate": "equilibration_quality_rate",
        "schema explicitness rate": "schema_explicitness_rate",
    }
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("|") or line.count("|") < 5:
            continue
        cols = [c.strip().lower() for c in line.strip("|").split("|")]
        if len(cols) < 4:
            continue
        metric_label = cols[0]
        status = cols[3]
        key = mapping.get(metric_label)
        if key and status in {"pass", "warn", "fail"}:
            out[key] = status
    return out


def _to_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _select_previous_owner_summary(repo_root: Path, now: datetime, window_days: int) -> dict | None:
    path = repo_root / "orchestrator/logs/owner_reports.jsonl"
    rows = _load_jsonl(path)
    if not rows:
        return None

    min_age_days = max(1.0, window_days * 0.7)
    max_age_days = max(float(window_days) * 4.0, float(window_days) + 2.0)

    candidates: list[tuple[datetime, dict]] = []
    for row in rows:
        if str(row.get("status", "active")).strip().lower() != "active":
            continue
        if _to_int(row.get("window_days"), -1) != int(window_days):
            continue
        created = _parse_iso8601(str(row.get("created_at", "")))
        if created is None or created >= now:
            continue

        age_days = (now - created).total_seconds() / 86400.0
        if age_days < min_age_days or age_days > max_age_days:
            continue

        summary = row.get("summary")
        if not isinstance(summary, dict):
            continue
        candidates.append((created, summary))

    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0], reverse=True)
    selected = candidates[0]
    return {"created_at": selected[0].isoformat().replace("+00:00", "Z"), "summary": selected[1]}


def _repeat_fail_todos(metric_keys: list[str]) -> list[dict]:
    if not metric_keys:
        return []

    action_map = {
        "precommit_coverage": "Enforce guardrail_check_id for every high-risk decision next week.",
        "cooldown_compliance": "Block high-emotion decisions unless cooldown evidence is logged.",
        "repeat_failure_rate": "Open one root-cause elimination task for repeated failure pattern.",
        "profile_drift_rate": "Run profile stabilizer reset and verify mitigation logs daily.",
        "unresolved_disequilibrium_rate": "Run schema revision cycle for top unresolved tension topic.",
        "equilibration_quality_rate": "Design stricter falsification tests for revised schemas before reuse.",
        "schema_explicitness_rate": "Require schema_version_id in assimilation entries before weekly close.",
    }

    todos: list[dict] = []
    for key in metric_keys:
        todos.append(
            {
                "id": f"two_week_fail_{key}",
                "metric": key,
                "priority": "red",
                "action": action_map.get(key, "Assign owner and correction plan before next weekly cycle."),
            }
        )
    return todos


def _status_with_red_tag(metric_key: str, status: str, red_keys: set[str]) -> str:
    if status == "fail" and metric_key in red_keys:
        return "fail [RED-2W]"
    return status


def _safe_ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return float(numerator) / float(denominator)


def _trend_direction(value_7d: float, value_30d: float, *, higher_better: bool, tolerance: float = 0.05) -> str:
    delta = float(value_7d) - float(value_30d)
    if abs(delta) <= tolerance:
        return "stable"
    if higher_better:
        return "improving" if delta > 0 else "worsening"
    return "improving" if delta < 0 else "worsening"


def summarize_suggestion_reviews(
    repo_root: Path,
    *,
    window_days: int = 30,
    now: datetime | None = None,
    verdict_filter: str | None = None,
    limit: int = 12,
) -> dict:
    now = now or datetime.now(timezone.utc)
    normalized_filter = str(verdict_filter or "").strip().lower() or None
    if normalized_filter not in {None, "accept", "modify", "reject"}:
        normalized_filter = None

    suggestions_rows = _window_filter(
        _load_jsonl(repo_root / "orchestrator/logs/suggestions.jsonl"),
        now,
        window_days,
    )
    suggestions_by_id: dict[str, dict] = {}
    for row in suggestions_rows:
        sid = str(row.get("id", "")).strip()
        if sid:
            suggestions_by_id[sid] = row

    verdict_rows = _window_filter(
        _load_jsonl(repo_root / "orchestrator/logs/owner_verdicts.jsonl"),
        now,
        window_days,
    )
    verdict_rows = [r for r in verdict_rows if str(r.get("status", "active")).strip().lower() == "active"]
    if normalized_filter:
        verdict_rows = [r for r in verdict_rows if str(r.get("verdict", "")).strip().lower() == normalized_filter]

    correction_rows = _window_filter(
        _load_jsonl(repo_root / "orchestrator/logs/owner_corrections.jsonl"),
        now,
        window_days,
    )
    correction_rows = [r for r in correction_rows if str(r.get("status", "active")).strip().lower() == "active"]
    correction_by_verdict_ref: dict[str, dict] = {}
    for row in correction_rows:
        verdict_ref = str(row.get("verdict_ref", "")).strip()
        if verdict_ref and verdict_ref not in correction_by_verdict_ref:
            correction_by_verdict_ref[verdict_ref] = row

    reviewed_suggestion_ids = {
        str(row.get("suggestion_ref", "")).strip()
        for row in verdict_rows
        if str(row.get("suggestion_ref", "")).strip()
    }
    reviewed_suggestion_ids = {sid for sid in reviewed_suggestion_ids if sid in suggestions_by_id}
    pending_total = max(0, len(suggestions_by_id) - len(reviewed_suggestion_ids))

    verdict_counter = Counter(str(row.get("verdict", "")).strip().lower() for row in verdict_rows)
    reviewed_total = sum(verdict_counter.values())

    rows_sorted = sorted(verdict_rows, key=lambda row: str(row.get("created_at", "")), reverse=True)
    recent_reviews: list[dict] = []
    for row in rows_sorted:
        suggestion_ref = str(row.get("suggestion_ref", "")).strip()
        verdict_id = str(row.get("id", "")).strip()
        suggestion = suggestions_by_id.get(suggestion_ref, {})
        correction = correction_by_verdict_ref.get(verdict_id)
        recent_reviews.append(
            {
                "verdict_id": verdict_id,
                "suggestion_ref": suggestion_ref,
                "verdict": str(row.get("verdict", "")).strip().lower(),
                "owner_note": str(row.get("owner_note", "")).strip(),
                "correction_ref": str((correction or {}).get("id", "")).strip() or None,
                "module": str(suggestion.get("module", "")).strip() or None,
                "task_raw": str(suggestion.get("task_raw", "")).strip() or None,
                "created_at": str(row.get("created_at", "")).strip(),
            }
        )
        if len(recent_reviews) >= max(1, int(limit)):
            break

    corrections_total = len(correction_rows)

    return {
        "window_days": int(window_days),
        "verdict_filter": normalized_filter,
        "suggestions_total": len(suggestions_by_id),
        "reviewed_total": reviewed_total,
        "pending_total": pending_total,
        "review_coverage_rate": _safe_ratio(len(reviewed_suggestion_ids), len(suggestions_by_id)),
        "verdicts": {
            "accept": int(verdict_counter.get("accept", 0)),
            "modify": int(verdict_counter.get("modify", 0)),
            "reject": int(verdict_counter.get("reject", 0)),
        },
        "corrections_total": corrections_total,
        "correction_ratio": _safe_ratio(corrections_total, reviewed_total),
        "recent_reviews": recent_reviews,
    }


def list_suggestion_review_queue(
    repo_root: Path,
    *,
    window_days: int = 30,
    now: datetime | None = None,
    limit: int = 8,
) -> dict:
    now = now or datetime.now(timezone.utc)

    suggestions_rows = _window_filter(
        _load_jsonl(repo_root / "orchestrator/logs/suggestions.jsonl"),
        now,
        window_days,
    )
    suggestions_rows = [row for row in suggestions_rows if str(row.get("status", "active")).strip().lower() == "active"]
    suggestions_rows = sorted(suggestions_rows, key=lambda row: str(row.get("created_at", "")), reverse=True)

    verdict_rows = _window_filter(
        _load_jsonl(repo_root / "orchestrator/logs/owner_verdicts.jsonl"),
        now,
        window_days,
    )
    verdict_rows = [row for row in verdict_rows if str(row.get("status", "active")).strip().lower() == "active"]
    verdict_rows = sorted(verdict_rows, key=lambda row: str(row.get("created_at", "")), reverse=True)

    correction_rows = _window_filter(
        _load_jsonl(repo_root / "orchestrator/logs/owner_corrections.jsonl"),
        now,
        window_days,
    )
    correction_rows = [row for row in correction_rows if str(row.get("status", "active")).strip().lower() == "active"]
    correction_rows = sorted(correction_rows, key=lambda row: str(row.get("created_at", "")), reverse=True)

    latest_verdict_by_suggestion: dict[str, dict] = {}
    for row in verdict_rows:
        suggestion_ref = str(row.get("suggestion_ref", "")).strip()
        if suggestion_ref and suggestion_ref not in latest_verdict_by_suggestion:
            latest_verdict_by_suggestion[suggestion_ref] = row

    correction_by_verdict_ref: dict[str, dict] = {}
    correction_by_suggestion_ref: dict[str, dict] = {}
    for row in correction_rows:
        verdict_ref = str(row.get("verdict_ref", "")).strip()
        suggestion_ref = str(row.get("suggestion_ref", "")).strip()
        if verdict_ref and verdict_ref not in correction_by_verdict_ref:
            correction_by_verdict_ref[verdict_ref] = row
        if suggestion_ref and suggestion_ref not in correction_by_suggestion_ref:
            correction_by_suggestion_ref[suggestion_ref] = row

    def queue_item(suggestion: dict, verdict: dict | None = None, correction: dict | None = None) -> dict:
        payload = {
            "id": str(suggestion.get("id", "")).strip(),
            "created_at": str(suggestion.get("created_at", "")).strip(),
            "module": str(suggestion.get("module", "")).strip() or None,
            "task_raw": str(suggestion.get("task_raw", "")).strip() or None,
            "recommendation_path": str(suggestion.get("recommendation_path", "")).strip() or None,
            "run_ref": str(suggestion.get("run_ref", "")).strip() or None,
            "output_hash": str(suggestion.get("output_hash", "")).strip() or None,
        }
        if verdict is None:
            return payload

        verdict_id = str(verdict.get("id", "")).strip()
        payload["owner_review"] = {
            "verdict_id": verdict_id or None,
            "verdict": str(verdict.get("verdict", "")).strip().lower() or None,
            "owner_note": str(verdict.get("owner_note", "")).strip() or None,
            "reviewed_at": str(verdict.get("created_at", "")).strip() or None,
            "correction_ref": str((correction or {}).get("id", "")).strip() or None,
            "target_layer": str((correction or {}).get("target_layer", "")).strip() or None,
            "replacement_judgment": str((correction or {}).get("replacement_judgment", "")).strip() or None,
            "unlike_me_reason": str((correction or {}).get("unlike_me_reason", "")).strip() or None,
        }
        return payload

    pending: list[dict] = []
    recently_reviewed: list[dict] = []
    for suggestion in suggestions_rows:
        suggestion_id = str(suggestion.get("id", "")).strip()
        if not suggestion_id:
            continue

        verdict = latest_verdict_by_suggestion.get(suggestion_id)
        if verdict is None:
            pending.append(queue_item(suggestion))
            continue

        verdict_id = str(verdict.get("id", "")).strip()
        correction = correction_by_verdict_ref.get(verdict_id) or correction_by_suggestion_ref.get(suggestion_id)
        recently_reviewed.append(queue_item(suggestion, verdict, correction))

    recently_reviewed.sort(
        key=lambda row: str(((row.get("owner_review") or {}).get("reviewed_at") or row.get("created_at") or "")),
        reverse=True,
    )

    return {
        "window_days": int(window_days),
        "pending_total": len(pending),
        "reviewed_total": len(recently_reviewed),
        "pending": pending[: max(1, int(limit))],
        "recently_reviewed": recently_reviewed[: max(1, int(limit))],
    }


def summarize_suggestion_review_trend(repo_root: Path, *, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    snap_7 = summarize_suggestion_reviews(repo_root, window_days=7, now=now, limit=5)
    snap_30 = summarize_suggestion_reviews(repo_root, window_days=30, now=now, limit=5)

    reviewed_7 = int(snap_7.get("reviewed_total", 0))
    reviewed_30 = int(snap_30.get("reviewed_total", 0))
    verdicts_7 = snap_7.get("verdicts", {})
    verdicts_30 = snap_30.get("verdicts", {})

    modify_ratio_7 = _safe_ratio(int(verdicts_7.get("modify", 0)), reviewed_7)
    modify_ratio_30 = _safe_ratio(int(verdicts_30.get("modify", 0)), reviewed_30)
    correction_ratio_7 = float(snap_7.get("correction_ratio", 0.0) or 0.0)
    correction_ratio_30 = float(snap_30.get("correction_ratio", 0.0) or 0.0)
    coverage_7 = float(snap_7.get("review_coverage_rate", 0.0) or 0.0)
    coverage_30 = float(snap_30.get("review_coverage_rate", 0.0) or 0.0)

    comparisons = [
        {
            "key": "review_coverage_rate",
            "value_7d": round(coverage_7, 3),
            "value_30d": round(coverage_30, 3),
            "delta": round(coverage_7 - coverage_30, 3),
            "trend": _trend_direction(coverage_7, coverage_30, higher_better=True),
        },
        {
            "key": "modify_ratio",
            "value_7d": round(modify_ratio_7, 3),
            "value_30d": round(modify_ratio_30, 3),
            "delta": round(modify_ratio_7 - modify_ratio_30, 3),
            "trend": _trend_direction(modify_ratio_7, modify_ratio_30, higher_better=False),
        },
        {
            "key": "correction_ratio",
            "value_7d": round(correction_ratio_7, 3),
            "value_30d": round(correction_ratio_30, 3),
            "delta": round(correction_ratio_7 - correction_ratio_30, 3),
            "trend": _trend_direction(correction_ratio_7, correction_ratio_30, higher_better=False),
        },
    ]

    return {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "windows": {
            "7d": {
                "suggestions_total": int(snap_7.get("suggestions_total", 0)),
                "reviewed_total": reviewed_7,
                "verdicts": snap_7.get("verdicts", {}),
                "corrections_total": int(snap_7.get("corrections_total", 0)),
                "review_coverage_rate": round(coverage_7, 3),
                "correction_ratio": round(correction_ratio_7, 3),
            },
            "30d": {
                "suggestions_total": int(snap_30.get("suggestions_total", 0)),
                "reviewed_total": reviewed_30,
                "verdicts": snap_30.get("verdicts", {}),
                "corrections_total": int(snap_30.get("corrections_total", 0)),
                "review_coverage_rate": round(coverage_30, 3),
                "correction_ratio": round(correction_ratio_30, 3),
            },
        },
        "comparisons": comparisons,
    }


def build_owner_snapshot(repo_root: Path, window_days: int, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    metrics = compute_drift_metrics(repo_root, window_days=window_days, now=now)
    previous_summary = _select_previous_owner_summary(repo_root, now=now, window_days=window_days)

    overrides = _window_filter(
        _load_jsonl(repo_root / "modules/decision/logs/guardrail_overrides.jsonl"),
        now,
        window_days,
    )

    override_domains = Counter(str(o.get("domain", "unknown")).lower() for o in overrides)
    candidate_pipeline = summarize_learning_pipeline(repo_root, window_days=window_days, now=now)
    candidate_pipeline_trend = summarize_learning_pipeline_trend(repo_root, now=now)
    suggestion_review = summarize_suggestion_reviews(repo_root, window_days=window_days, now=now, limit=12)
    suggestion_review_trend = summarize_suggestion_review_trend(repo_root, now=now)

    failed_metrics = [k for k, v in metrics["metrics"].items() if v["status"] == "fail"]
    warned_metrics = [k for k, v in metrics["metrics"].items() if v["status"] == "warn"]

    top_exceptions: list[dict] = []
    for key in failed_metrics:
        item = metrics["metrics"][key]
        top_exceptions.append(
            {
                "type": "metric_fail",
                "label": key,
                "detail": f"{item['numerator']}/{item['denominator']} ({item['status']})",
            }
        )
    for key in warned_metrics:
        item = metrics["metrics"][key]
        top_exceptions.append(
            {
                "type": "metric_warn",
                "label": key,
                "detail": f"{item['numerator']}/{item['denominator']} ({item['status']})",
            }
        )

    for domain, count in override_domains.items():
        top_exceptions.append(
            {
                "type": "override",
                "label": f"guardrail_overrides.{domain}",
                "detail": f"{count} overrides in window",
            }
        )

    pending_total = int(candidate_pipeline.get("pending_total", 0))
    verdicts = candidate_pipeline.get("verdicts", {})
    reject_count = int(verdicts.get("reject", 0)) if isinstance(verdicts, dict) else 0
    accept_count = int(verdicts.get("accept", 0)) if isinstance(verdicts, dict) else 0
    reviewed_total = int(candidate_pipeline.get("reviewed_total", 0))
    promoted_total = int(candidate_pipeline.get("promoted_total", 0))
    promotion_readiness = candidate_pipeline.get("promotion_readiness", {})
    readiness_ready_total = (
        _to_int(promotion_readiness.get("ready_total"), 0) if isinstance(promotion_readiness, dict) else 0
    )
    readiness_cooling_total = (
        _to_int(promotion_readiness.get("cooling_total"), 0) if isinstance(promotion_readiness, dict) else 0
    )

    trend_map: dict[str, dict] = {}
    trend_comparisons = candidate_pipeline_trend.get("comparisons", [])
    if isinstance(trend_comparisons, list):
        for item in trend_comparisons:
            if not isinstance(item, dict):
                continue
            key = str(item.get("key", "")).strip()
            if key:
                trend_map[key] = item

    backlog_trend = trend_map.get("backlog_pressure", {})
    reject_ratio_trend = trend_map.get("reject_ratio", {})
    conversion_trend = trend_map.get("promotion_conversion_rate", {})

    backlog_is_worsening = (
        str(backlog_trend.get("trend", "")).strip().lower() == "worsening"
        and _to_float(backlog_trend.get("value_7d"), 0.0) >= 2.0
    )
    reject_ratio_is_worsening = (
        str(reject_ratio_trend.get("trend", "")).strip().lower() == "worsening"
        and _to_float(reject_ratio_trend.get("value_7d"), 0.0) >= 0.5
        and _to_int(candidate_pipeline_trend.get("windows", {}).get("7d", {}).get("reviewed_total"), 0) >= 2
    )
    conversion_is_worsening = (
        str(conversion_trend.get("trend", "")).strip().lower() == "worsening"
        and (_to_float(conversion_trend.get("value_30d"), 0.0) - _to_float(conversion_trend.get("value_7d"), 0.0))
        >= 0.2
        and _to_int(candidate_pipeline_trend.get("windows", {}).get("7d", {}).get("verdicts", {}).get("accept"), 0) >= 1
    )

    if pending_total >= 10:
        top_exceptions.append(
            {
                "type": "candidate_backlog",
                "label": "learning_candidates.pending",
                "detail": f"{pending_total} pending candidates",
            }
        )
    if reviewed_total >= 4 and reject_count > accept_count:
        top_exceptions.append(
            {
                "type": "candidate_drift",
                "label": "learning_candidates.review_quality",
                "detail": f"reject({reject_count}) > accept({accept_count}) in window",
            }
        )
    if accept_count >= 3 and promoted_total == 0:
        top_exceptions.append(
            {
                "type": "candidate_promotion_gap",
                "label": "learning_candidates.promotion_gap",
                "detail": "accepted candidates exist but none promoted",
            }
        )
    if readiness_cooling_total >= 3 and readiness_ready_total == 0:
        top_exceptions.append(
            {
                "type": "candidate_promotion_cooling",
                "label": "learning_candidates.promotion_readiness",
                "detail": f"{readiness_cooling_total} promoted candidates still cooling",
            }
        )
    if backlog_is_worsening:
        top_exceptions.append(
            {
                "type": "candidate_backlog_trend",
                "label": "learning_candidates.backlog_pressure",
                "detail": (
                    f"7d={_to_float(backlog_trend.get('value_7d'), 0.0):.1f} vs "
                    f"30d={_to_float(backlog_trend.get('value_30d'), 0.0):.1f} (worsening)"
                ),
            }
        )
    if reject_ratio_is_worsening:
        top_exceptions.append(
            {
                "type": "candidate_review_drift_trend",
                "label": "learning_candidates.reject_ratio",
                "detail": (
                    f"7d={_to_float(reject_ratio_trend.get('value_7d'), 0.0):.3f} vs "
                    f"30d={_to_float(reject_ratio_trend.get('value_30d'), 0.0):.3f} (worsening)"
                ),
            }
        )
    if conversion_is_worsening:
        top_exceptions.append(
            {
                "type": "candidate_promotion_slowdown",
                "label": "learning_candidates.promotion_conversion",
                "detail": (
                    f"7d={_to_float(conversion_trend.get('value_7d'), 0.0):.3f} vs "
                    f"30d={_to_float(conversion_trend.get('value_30d'), 0.0):.3f} (worsening)"
                ),
            }
        )

    suggestion_review_coverage = float(suggestion_review.get("review_coverage_rate", 0.0) or 0.0)
    suggestion_reviewed_total = int(suggestion_review.get("reviewed_total", 0))
    suggestion_total = int(suggestion_review.get("suggestions_total", 0))
    suggestion_verdicts = suggestion_review.get("verdicts", {})
    suggestion_modify_ratio = _safe_ratio(int(suggestion_verdicts.get("modify", 0)), suggestion_reviewed_total)
    suggestion_correction_ratio = float(suggestion_review.get("correction_ratio", 0.0) or 0.0)

    if suggestion_total >= 3 and suggestion_review_coverage < 0.5:
        top_exceptions.append(
            {
                "type": "suggestion_review_backlog",
                "label": "suggestions.review_coverage",
                "detail": (
                    f"coverage={suggestion_review_coverage:.3f} "
                    f"({suggestion_reviewed_total}/{suggestion_total})"
                ),
            }
        )
    if suggestion_reviewed_total >= 3 and suggestion_modify_ratio >= 0.5:
        top_exceptions.append(
            {
                "type": "suggestion_review_drift",
                "label": "suggestions.modify_ratio",
                "detail": f"modify_ratio={suggestion_modify_ratio:.3f}",
            }
        )

    decision_audit = _latest_file(repo_root, "modules/decision/outputs/decision_audit_*.md")
    weekly_review = _latest_file(repo_root, "modules/decision/outputs/weekly_review_*.md")
    metrics_report = _latest_file(repo_root, "modules/decision/outputs/metrics_*.md")
    cognition_timeline = _latest_file(repo_root, "modules/cognition/outputs/cognitive_timeline_*.md")

    consistency_alerts: list[str] = []

    metrics_report_text = _read_text(repo_root, metrics_report)
    if metrics_report_text:
        reported_status = _parse_metrics_status_from_report(metrics_report_text)
        for key, current in metrics["metrics"].items():
            reported = reported_status.get(key)
            if reported and reported != current["status"]:
                consistency_alerts.append(
                    f"metrics_mismatch:{key}:latest_report={reported},owner_snapshot={current['status']}"
                )

    decision_audit_text = _read_text(repo_root, decision_audit).lower()
    if decision_audit_text and ("no major exceptions" in decision_audit_text or "no exceptions" in decision_audit_text):
        if len(top_exceptions) > 0:
            consistency_alerts.append("decision_audit_conflict:reports_no_exceptions_but_current_exceptions_exist")

    weekly_review_text = _read_text(repo_root, weekly_review).lower()
    if weekly_review_text and ("sample-size limitation" in weekly_review_text or "too few records" in weekly_review_text):
        observed = metrics["counts"]["decisions"] + metrics["counts"]["precommit_checks"] + metrics["counts"]["failures"]
        if observed >= 3:
            consistency_alerts.append("weekly_review_conflict:sample_size_limitation_vs_nontrivial_record_count")

    m = metrics["metrics"]
    auto_triggers: list[dict] = []

    if m["unresolved_disequilibrium_rate"]["status"] == "fail":
        auto_triggers.append(
            {
                "id": "schema_revision_unresolved_tension",
                "reason": "unresolved_disequilibrium_rate is fail",
                "action": "Trigger schema revision cycle on top high-tension topic within 48h.",
            }
        )
    if m["equilibration_quality_rate"]["status"] == "fail":
        auto_triggers.append(
            {
                "id": "schema_revision_low_equilibration_quality",
                "reason": "equilibration_quality_rate is fail",
                "action": "Run accommodation + falsification design review before next high-risk decision.",
            }
        )
    if m["schema_explicitness_rate"]["status"] == "fail":
        auto_triggers.append(
            {
                "id": "schema_revision_low_explicitness",
                "reason": "schema_explicitness_rate is fail",
                "action": "Require schema_version_id in assimilation logs for next window.",
            }
        )
    if (
        m["unresolved_disequilibrium_rate"]["status"] in {"warn", "fail"}
        and m["equilibration_quality_rate"]["status"] in {"warn", "fail"}
        and metrics["counts"]["disequilibrium_events"] >= 3
    ):
        auto_triggers.append(
            {
                "id": "schema_revision_compound_signal",
                "reason": "disequilibrium pressure + weak equilibration under non-trivial sample",
                "action": "Escalate to owner-approved schema split/replace decision this week.",
            }
        )
    if backlog_is_worsening:
        auto_triggers.append(
            {
                "id": "learning_queue_triage_backlog_pressure",
                "reason": "candidate backlog pressure worsened in 7d vs 30d",
                "action": "Run learning candidate triage and clear highest-impact backlog within 72h.",
            }
        )
    if reject_ratio_is_worsening:
        auto_triggers.append(
            {
                "id": "learning_candidate_alignment_review",
                "reason": "candidate reject ratio worsened in 7d vs 30d",
                "action": "Audit external ingestion quality and tighten candidate extraction prompt constraints.",
            }
        )
    if conversion_is_worsening:
        auto_triggers.append(
            {
                "id": "learning_candidate_promotion_policy_review",
                "reason": "promotion conversion worsened in 7d vs 30d",
                "action": "Review promotion criteria and unblock accepted candidates pending promotion.",
            }
        )
    if readiness_cooling_total >= 3 and readiness_ready_total == 0:
        auto_triggers.append(
            {
                "id": "learning_candidate_promotion_readiness_review",
                "reason": "all promoted candidates are still in cooling period",
                "action": "Review maturity window and queue follow-up review for cooling promotions.",
            }
        )
    if suggestion_total >= 3 and suggestion_review_coverage < 0.5:
        auto_triggers.append(
            {
                "id": "suggestion_review_coverage_triage",
                "reason": "suggestion review coverage is low relative to generated suggestions",
                "action": "Review pending suggestions and submit verdicts before next weekly report.",
            }
        )
    if suggestion_reviewed_total >= 3 and suggestion_correction_ratio >= 0.5:
        auto_triggers.append(
            {
                "id": "suggestion_quality_refinement",
                "reason": "correction ratio is high in suggestion reviews",
                "action": "Tighten planning/routing context and update suggestion quality constraints.",
            }
        )

    consecutive_fail_metrics: list[str] = []
    if previous_summary and isinstance(previous_summary.get("summary"), dict):
        prev = previous_summary["summary"]
        for key, item in m.items():
            current_status = str(item.get("status", "")).strip().lower()
            prev_status = str(prev.get(key, "")).strip().lower()
            if current_status == "fail" and prev_status == "fail":
                consecutive_fail_metrics.append(key)

    escalation_todos = _repeat_fail_todos(consecutive_fail_metrics)

    return {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "window_days": window_days,
        "metrics": metrics,
        "override_count": len(overrides),
        "override_domains": dict(override_domains),
        "top_exceptions": top_exceptions[:7],
        "source_artifacts": {
            "decision_audit": decision_audit,
            "weekly_review": weekly_review,
            "metrics_report": metrics_report,
            "cognition_timeline": cognition_timeline,
            "owner_todos": None,
        },
        "consistency_alerts": consistency_alerts,
        "auto_triggers": auto_triggers,
        "candidate_pipeline_summary": candidate_pipeline,
        "candidate_pipeline_trend": candidate_pipeline_trend,
        "suggestion_review_summary": suggestion_review,
        "suggestion_review_trend": suggestion_review_trend,
        "previous_summary": previous_summary,
        "consecutive_fail_metrics": consecutive_fail_metrics,
        "escalation_todos": escalation_todos,
    }


def render_owner_report(snapshot: dict) -> str:
    metrics = snapshot["metrics"]["metrics"]
    red_keys = set(snapshot.get("consecutive_fail_metrics", []))

    lines = [
        "# Owner Report",
        "",
        f"- Generated at: {snapshot['generated_at']}",
        f"- Window: last {snapshot['window_days']} days",
        "",
        "## Executive Summary",
        "",
        f"- precommit_coverage: {_status_with_red_tag('precommit_coverage', metrics['precommit_coverage']['status'], red_keys)}",
        f"- cooldown_compliance: {_status_with_red_tag('cooldown_compliance', metrics['cooldown_compliance']['status'], red_keys)}",
        f"- repeat_failure_rate: {_status_with_red_tag('repeat_failure_rate', metrics['repeat_failure_rate']['status'], red_keys)}",
        f"- profile_drift_rate: {_status_with_red_tag('profile_drift_rate', metrics['profile_drift_rate']['status'], red_keys)}",
        f"- unresolved_disequilibrium_rate: {_status_with_red_tag('unresolved_disequilibrium_rate', metrics['unresolved_disequilibrium_rate']['status'], red_keys)}",
        f"- equilibration_quality_rate: {_status_with_red_tag('equilibration_quality_rate', metrics['equilibration_quality_rate']['status'], red_keys)}",
        f"- schema_explicitness_rate: {_status_with_red_tag('schema_explicitness_rate', metrics['schema_explicitness_rate']['status'], red_keys)}",
        f"- guardrail_override_count: {snapshot['override_count']}",
        "",
        "## Top Exceptions",
        "",
    ]

    if not snapshot["top_exceptions"]:
        lines.append("- No major exceptions in window.")
    else:
        for e in snapshot["top_exceptions"]:
            lines.append(f"- [{e['type']}] {e['label']}: {e['detail']}")

    lines.extend(
        [
            "",
            "## Learning Candidate Pipeline",
            "",
        ]
    )

    pipeline = snapshot.get("candidate_pipeline_summary", {})
    if isinstance(pipeline, dict):
        verdicts = pipeline.get("verdicts", {})
        lines.append(f"- pending_total: {int(pipeline.get('pending_total', 0))}")
        lines.append(f"- reviewed_total: {int(pipeline.get('reviewed_total', 0))}")
        lines.append(
            f"- verdicts: accept={int(verdicts.get('accept', 0))} "
            f"modify={int(verdicts.get('modify', 0))} reject={int(verdicts.get('reject', 0))}"
        )
        lines.append(f"- promoted_total: {int(pipeline.get('promoted_total', 0))}")
        lines.append(f"- promotion_conversion_rate: {float(pipeline.get('promotion_conversion_rate', 0.0)):.3f}")
        readiness = pipeline.get("promotion_readiness", {})
        if isinstance(readiness, dict):
            lines.append(
                f"- promotion_readiness: ready={int(readiness.get('ready_total', 0))} "
                f"cooling={int(readiness.get('cooling_total', 0))} "
                f"maturity_hours={int(readiness.get('maturity_hours', 0))}"
            )
        pending_by_type = pipeline.get("pending_by_type", {})
        if isinstance(pending_by_type, dict) and pending_by_type:
            lines.append("- pending_by_type:")
            for key in sorted(pending_by_type.keys()):
                lines.append(f"  - {key}: {int(pending_by_type[key])}")
        promoted_by_target = pipeline.get("promoted_by_target", {})
        if isinstance(promoted_by_target, dict) and promoted_by_target:
            lines.append("- promoted_by_target:")
            for key in sorted(promoted_by_target.keys()):
                lines.append(f"  - {key}: {int(promoted_by_target[key])}")
        if isinstance(readiness, dict):
            ready_by_target = readiness.get("ready_by_target", {})
            if isinstance(ready_by_target, dict) and ready_by_target:
                lines.append("- ready_by_target:")
                for key in sorted(ready_by_target.keys()):
                    lines.append(f"  - {key}: {int(ready_by_target[key])}")
            cooling_by_target = readiness.get("cooling_by_target", {})
            if isinstance(cooling_by_target, dict) and cooling_by_target:
                lines.append("- cooling_by_target:")
                for key in sorted(cooling_by_target.keys()):
                    lines.append(f"  - {key}: {int(cooling_by_target[key])}")
    else:
        lines.append("- no pipeline summary")

    lines.extend(
        [
            "",
            "## Learning Candidate Trend (7d vs 30d)",
            "",
        ]
    )

    trend = snapshot.get("candidate_pipeline_trend", {})
    if isinstance(trend, dict):
        inflow = trend.get("inflow", {})
        if isinstance(inflow, dict):
            lines.append(f"- inflow: 7d={int(inflow.get('7d', 0))} 30d={int(inflow.get('30d', 0))}")
        comparisons = trend.get("comparisons", [])
        if isinstance(comparisons, list) and comparisons:
            for item in comparisons:
                if not isinstance(item, dict):
                    continue
                lines.append(
                    f"- {str(item.get('key', 'unknown'))}: "
                    f"7d={_to_float(item.get('value_7d'), 0.0):.3f} "
                    f"30d={_to_float(item.get('value_30d'), 0.0):.3f} "
                    f"delta={_to_float(item.get('delta'), 0.0):.3f} "
                    f"trend={str(item.get('trend', 'stable'))}"
                )
        else:
            lines.append("- no trend comparisons")
    else:
        lines.append("- no trend summary")

    lines.extend(
        [
            "",
            "## Suggestion Review Loop",
            "",
        ]
    )

    suggestion_review = snapshot.get("suggestion_review_summary", {})
    if isinstance(suggestion_review, dict):
        verdicts = suggestion_review.get("verdicts", {})
        lines.append(f"- suggestions_total: {int(suggestion_review.get('suggestions_total', 0))}")
        lines.append(f"- reviewed_total: {int(suggestion_review.get('reviewed_total', 0))}")
        lines.append(f"- pending_total: {int(suggestion_review.get('pending_total', 0))}")
        lines.append(f"- review_coverage_rate: {float(suggestion_review.get('review_coverage_rate', 0.0)):.3f}")
        lines.append(
            f"- verdicts: accept={int(verdicts.get('accept', 0))} "
            f"modify={int(verdicts.get('modify', 0))} reject={int(verdicts.get('reject', 0))}"
        )
        lines.append(f"- corrections_total: {int(suggestion_review.get('corrections_total', 0))}")
        lines.append(f"- correction_ratio: {float(suggestion_review.get('correction_ratio', 0.0)):.3f}")
    else:
        lines.append("- no suggestion review summary")

    lines.extend(
        [
            "",
            "## Suggestion Review Trend (7d vs 30d)",
            "",
        ]
    )

    suggestion_review_trend = snapshot.get("suggestion_review_trend", {})
    if isinstance(suggestion_review_trend, dict):
        comparisons = suggestion_review_trend.get("comparisons", [])
        if isinstance(comparisons, list) and comparisons:
            for item in comparisons:
                if not isinstance(item, dict):
                    continue
                lines.append(
                    f"- {str(item.get('key', 'unknown'))}: "
                    f"7d={_to_float(item.get('value_7d'), 0.0):.3f} "
                    f"30d={_to_float(item.get('value_30d'), 0.0):.3f} "
                    f"delta={_to_float(item.get('delta'), 0.0):.3f} "
                    f"trend={str(item.get('trend', 'stable'))}"
                )
        else:
            lines.append("- no trend comparisons")
    else:
        lines.append("- no trend summary")

    lines.extend(
        [
            "",
            "## Source Artifacts",
            "",
            f"- decision_audit: {snapshot['source_artifacts']['decision_audit'] or 'N/A'}",
            f"- weekly_review: {snapshot['source_artifacts']['weekly_review'] or 'N/A'}",
            f"- metrics_report: {snapshot['source_artifacts']['metrics_report'] or 'N/A'}",
            f"- cognition_timeline: {snapshot['source_artifacts']['cognition_timeline'] or 'N/A'}",
            "",
            "## Consistency Alerts",
            "",
        ]
    )

    if snapshot["consistency_alerts"]:
        for alert in snapshot["consistency_alerts"]:
            lines.append(f"- {alert}")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Auto Triggers",
            "",
        ]
    )

    if snapshot["auto_triggers"]:
        for trigger in snapshot["auto_triggers"]:
            lines.append(f"- [{trigger['id']}] {trigger['reason']} -> {trigger['action']}")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Escalation Todos (2W Fail)",
            "",
        ]
    )

    escalation_todos = snapshot.get("escalation_todos", [])
    if escalation_todos:
        for todo in escalation_todos:
            lines.append(f"- [{todo['priority'].upper()}] {todo['metric']}: {todo['action']}")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Owner Actions",
            "",
            "- Approve or reject any guardrail overrides with unresolved violations.",
            "- If any metric is `fail`, assign one corrective action with owner + due date.",
            "- If cognition metrics fail (`unresolved_disequilibrium_rate` or `equilibration_quality_rate`), trigger a schema revision cycle.",
            "- If two consecutive windows show the same exception, escalate policy depth.",
        ]
    )

    return "\n".join(lines) + "\n"


def _owner_todos_path(repo_root: Path) -> Path:
    return repo_root / "modules/decision/logs/owner_todos.jsonl"


def _open_owner_todos(repo_root: Path) -> dict[str, dict]:
    path = _owner_todos_path(repo_root)
    rows = _load_jsonl(path)
    closed_ids: set[str] = set()
    active: dict[str, dict] = {}

    for row in rows:
        if str(row.get("status", "")).strip().lower() == "archived":
            ref = str(row.get("resolution_of", "")).strip()
            if ref:
                closed_ids.add(ref)

    for row in rows:
        if str(row.get("status", "")).strip().lower() != "active":
            continue
        todo_id = str(row.get("id", "")).strip()
        if not todo_id or todo_id in closed_ids:
            continue
        sig = str(row.get("todo_signature", "")).strip()
        if not sig:
            continue
        active[sig] = row
    return active


def list_open_owner_todos(repo_root: Path) -> list[dict]:
    open_map = _open_owner_todos(repo_root)
    rows = list(open_map.values())
    rows.sort(key=lambda row: str(row.get("created_at", "")), reverse=True)
    out: list[dict] = []
    for row in rows:
        out.append(
            {
                "id": str(row.get("id", "")).strip(),
                "metric": str(row.get("metric", "")).strip(),
                "priority": str(row.get("priority", "red")).strip().lower() or "red",
                "reason": str(row.get("reason", "")).strip(),
                "action": str(row.get("action", "")).strip(),
                "created_at": str(row.get("created_at", "")).strip(),
                "owner_report_ref": str(row.get("owner_report_ref", "")).strip() or None,
            }
        )
    return out


def sync_owner_todos(
    repo_root: Path,
    snapshot: dict,
    *,
    owner_report_ref: str | None = None,
) -> dict:
    todos = snapshot.get("escalation_todos", [])
    if not isinstance(todos, list) or not todos:
        return {"appended_ids": [], "existing_ids": [], "all_ids": []}

    path = _owner_todos_path(repo_root)
    open_todos = _open_owner_todos(repo_root)
    appended_ids: list[str] = []
    existing_ids: list[str] = []
    all_ids: list[str] = []

    for item in todos:
        metric = str(item.get("metric", "")).strip()
        action = str(item.get("action", "")).strip()
        reason = str(item.get("id", "")).strip() or "two_week_fail"
        priority = str(item.get("priority", "red")).strip().lower() or "red"
        if not metric or not action:
            continue
        signature = f"{metric}|{action}"

        current = open_todos.get(signature)
        if current:
            tid = str(current.get("id", "")).strip()
            if tid:
                existing_ids.append(tid)
                all_ids.append(tid)
            continue

        record = {
            "id": next_id_for_path(path, "ot"),
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "status": "active",
            "metric": metric,
            "priority": priority,
            "reason": reason,
            "action": action,
            "owner_report_ref": str(owner_report_ref).strip() or None,
            "todo_signature": signature,
            "resolution_of": None,
            "note": None,
        }
        append_jsonl(path, record, schema_header=OWNER_TODOS_SCHEMA)
        appended_ids.append(record["id"])
        all_ids.append(record["id"])
        open_todos[signature] = record

    return {
        "appended_ids": appended_ids,
        "existing_ids": existing_ids,
        "all_ids": all_ids,
    }


def resolve_owner_todo(
    repo_root: Path,
    *,
    todo_id: str,
    note: str,
    owner_report_ref: str | None = None,
) -> dict:
    target = str(todo_id).strip()
    note_text = str(note).strip()
    if not target:
        raise ValueError("todo_id is required")
    if not note_text:
        raise ValueError("note is required")

    open_todos = _open_owner_todos(repo_root)
    active_row: dict | None = None
    for row in open_todos.values():
        if str(row.get("id", "")).strip() == target:
            active_row = row
            break
    if active_row is None:
        raise ValueError(f"active todo not found: {target}")

    path = _owner_todos_path(repo_root)
    record = {
        "id": next_id_for_path(path, "ot"),
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "archived",
        "metric": str(active_row.get("metric", "")).strip(),
        "priority": str(active_row.get("priority", "red")).strip().lower() or "red",
        "reason": "resolved",
        "action": str(active_row.get("action", "")).strip(),
        "owner_report_ref": str(owner_report_ref).strip() or None,
        "todo_signature": str(active_row.get("todo_signature", "")).strip(),
        "resolution_of": target,
        "note": note_text,
    }
    append_jsonl(path, record, schema_header=OWNER_TODOS_SCHEMA)
    return record


def render_owner_todos(snapshot: dict) -> str:
    todos = snapshot.get("escalation_todos", [])
    lines = [
        "# Owner Escalation Todos",
        "",
        f"- Generated at: {snapshot.get('generated_at', '')}",
        f"- Window: last {snapshot.get('window_days', '')} days",
        "",
    ]

    if not todos:
        lines.extend(
            [
                "## Todos",
                "",
                "- none",
                "",
            ]
        )
        return "\n".join(lines)

    lines.extend(["## Todos", ""])
    for item in todos:
        metric = str(item.get("metric", "unknown"))
        priority = str(item.get("priority", "red")).upper()
        action = str(item.get("action", "")).strip()
        lines.append(f"- [ ] ({priority}) {metric}: {action}")

    lines.extend(
        [
            "",
            "## Completion Rule",
            "",
            "- Mark done only after evidence is appended in decision/profile/cognition logs.",
            "",
        ]
    )
    return "\n".join(lines)
