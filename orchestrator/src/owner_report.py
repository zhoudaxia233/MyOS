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
        },
        "consistency_alerts": consistency_alerts,
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
        f"- unresolved_disequilibrium_rate: {metrics['unresolved_disequilibrium_rate']['status']}",
        f"- equilibration_quality_rate: {metrics['equilibration_quality_rate']['status']}",
        f"- schema_explicitness_rate: {metrics['schema_explicitness_rate']['status']}",
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
            "## Owner Actions",
            "",
            "- Approve or reject any guardrail overrides with unresolved violations.",
            "- If any metric is `fail`, assign one corrective action with owner + due date.",
            "- If cognition metrics fail (`unresolved_disequilibrium_rate` or `equilibration_quality_rate`), trigger a schema revision cycle.",
            "- If two consecutive windows show the same exception, escalate policy depth.",
        ]
    )

    return "\n".join(lines) + "\n"
