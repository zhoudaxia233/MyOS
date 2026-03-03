from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from metrics import compute_drift_metrics


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


def build_owner_snapshot(repo_root: Path, window_days: int, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    metrics = compute_drift_metrics(repo_root, window_days=window_days, now=now)

    overrides = _window_filter(
        _load_jsonl(repo_root / "modules/decision/logs/guardrail_overrides.jsonl"),
        now,
        window_days,
    )

    override_domains = Counter(str(o.get("domain", "unknown")).lower() for o in overrides)

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

    decision_audit = _latest_file(repo_root, "modules/decision/outputs/decision_audit_*.md")
    weekly_review = _latest_file(repo_root, "modules/decision/outputs/weekly_review_*.md")
    metrics_report = _latest_file(repo_root, "modules/decision/outputs/metrics_*.md")

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
        },
    }


def render_owner_report(snapshot: dict) -> str:
    metrics = snapshot["metrics"]["metrics"]

    lines = [
        "# Owner Report",
        "",
        f"- Generated at: {snapshot['generated_at']}",
        f"- Window: last {snapshot['window_days']} days",
        "",
        "## Executive Summary",
        "",
        f"- precommit_coverage: {metrics['precommit_coverage']['status']}",
        f"- cooldown_compliance: {metrics['cooldown_compliance']['status']}",
        f"- repeat_failure_rate: {metrics['repeat_failure_rate']['status']}",
        f"- profile_drift_rate: {metrics['profile_drift_rate']['status']}",
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
            "## Source Artifacts",
            "",
            f"- decision_audit: {snapshot['source_artifacts']['decision_audit'] or 'N/A'}",
            f"- weekly_review: {snapshot['source_artifacts']['weekly_review'] or 'N/A'}",
            f"- metrics_report: {snapshot['source_artifacts']['metrics_report'] or 'N/A'}",
            "",
            "## Owner Actions",
            "",
            "- Approve or reject any guardrail overrides with unresolved violations.",
            "- If any metric is `fail`, assign one corrective action with owner + due date.",
            "- If two consecutive windows show the same exception, escalate policy depth.",
        ]
    )

    return "\n".join(lines) + "\n"
