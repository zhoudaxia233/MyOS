from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso8601(ts: str) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def _safe_ratio(num: int, den: int) -> float:
    if den <= 0:
        return 0.0
    return num / den


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


def _load_high_risk_domains(path: Path) -> list[str]:
    if not path.exists():
        return ["invest", "project"]

    domains: list[str] = []
    in_section = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped == "high_risk_domains:":
            in_section = True
            continue

        if in_section:
            if line.startswith("  - "):
                domains.append(stripped[2:].strip().strip('"').strip("'"))
                continue
            if not line.startswith("  "):
                break

    return domains or ["invest", "project"]


def _status_lower_better(value: float, threshold: float) -> str:
    if value <= threshold:
        return "pass"
    if value <= threshold + 0.15:
        return "warn"
    return "fail"


def _status_higher_better(value: float, threshold: float) -> str:
    if value >= threshold:
        return "pass"
    if value >= max(0.0, threshold - 0.15):
        return "warn"
    return "fail"


def compute_drift_metrics(repo_root: Path, window_days: int, now: datetime | None = None) -> dict:
    now = now or _now_utc()

    decisions = _window_filter(
        _load_jsonl(repo_root / "modules/decision/logs/decisions.jsonl"), now, window_days
    )
    precommit_checks = _window_filter(
        _load_jsonl(repo_root / "modules/decision/logs/precommit_checks.jsonl"), now, window_days
    )
    failures = _window_filter(
        _load_jsonl(repo_root / "modules/decision/logs/failures.jsonl"), now, window_days
    )
    trigger_events = _window_filter(
        _load_jsonl(repo_root / "modules/profile/logs/trigger_events.jsonl"), now, window_days
    )
    psych_observations = _window_filter(
        _load_jsonl(repo_root / "modules/profile/logs/psych_observations.jsonl"), now, window_days
    )

    high_risk_domains = _load_high_risk_domains(repo_root / "modules/decision/data/impulse_guardrails.yaml")

    high_risk_decisions = [
        d for d in decisions if str(d.get("domain", "")).lower() in {x.lower() for x in high_risk_domains}
    ]
    covered_high_risk = [d for d in high_risk_decisions if d.get("guardrail_check_id") not in (None, "", "null")]
    precommit_coverage = _safe_ratio(len(covered_high_risk), len(high_risk_decisions))

    cooldown_required = [c for c in precommit_checks if bool(c.get("cooldown_required", False))]
    cooldown_compliant = [
        c
        for c in cooldown_required
        if str(c.get("result", "")).lower() in {"pass_with_cooldown", "pass"}
    ]
    cooldown_compliance = _safe_ratio(len(cooldown_compliant), len(cooldown_required))

    root_causes = [str(f.get("root_cause", "")).strip().lower() for f in failures if str(f.get("root_cause", "")).strip()]
    root_counts = Counter(root_causes)
    repeated_failures = [
        f
        for f in failures
        if root_counts.get(str(f.get("root_cause", "")).strip().lower(), 0) > 1
    ]
    repeat_failure_rate = _safe_ratio(len(repeated_failures), len(failures))

    high_trigger = [t for t in trigger_events if int(t.get("emotional_weight", 0)) >= 7]
    high_psych = [p for p in psych_observations if int(p.get("confidence", 0)) >= 8]
    drift_signal_count = len(high_trigger) + len(high_psych)
    drift_base_count = len(trigger_events) + len(psych_observations)
    profile_drift_rate = _safe_ratio(drift_signal_count, drift_base_count)

    thresholds = {
        "precommit_coverage": 0.8,
        "cooldown_compliance": 0.9,
        "repeat_failure_rate": 0.3,
        "profile_drift_rate": 0.4,
    }

    metrics = {
        "precommit_coverage": {
            "value": precommit_coverage,
            "threshold": thresholds["precommit_coverage"],
            "status": _status_higher_better(precommit_coverage, thresholds["precommit_coverage"]),
            "numerator": len(covered_high_risk),
            "denominator": len(high_risk_decisions),
        },
        "cooldown_compliance": {
            "value": cooldown_compliance,
            "threshold": thresholds["cooldown_compliance"],
            "status": _status_higher_better(cooldown_compliance, thresholds["cooldown_compliance"]),
            "numerator": len(cooldown_compliant),
            "denominator": len(cooldown_required),
        },
        "repeat_failure_rate": {
            "value": repeat_failure_rate,
            "threshold": thresholds["repeat_failure_rate"],
            "status": _status_lower_better(repeat_failure_rate, thresholds["repeat_failure_rate"]),
            "numerator": len(repeated_failures),
            "denominator": len(failures),
        },
        "profile_drift_rate": {
            "value": profile_drift_rate,
            "threshold": thresholds["profile_drift_rate"],
            "status": _status_lower_better(profile_drift_rate, thresholds["profile_drift_rate"]),
            "numerator": drift_signal_count,
            "denominator": drift_base_count,
        },
    }

    return {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "window_days": window_days,
        "metrics": metrics,
        "counts": {
            "decisions": len(decisions),
            "precommit_checks": len(precommit_checks),
            "failures": len(failures),
            "trigger_events": len(trigger_events),
            "psych_observations": len(psych_observations),
        },
        "refs": {
            "high_risk_domains": high_risk_domains,
        },
    }


def _pct(value: float) -> str:
    return f"{(value * 100):.1f}%"


def render_metrics_report(snapshot: dict) -> str:
    m = snapshot["metrics"]

    lines = [
        "# Drift Dashboard",
        "",
        f"- Generated at: {snapshot['generated_at']}",
        f"- Window: last {snapshot['window_days']} days",
        "",
        "## Metrics",
        "",
        "| Metric | Value | Threshold | Status | Detail |",
        "|---|---:|---:|---|---|",
    ]

    rows = [
        ("Precommit Coverage", "precommit_coverage", "higher"),
        ("Cooldown Compliance", "cooldown_compliance", "higher"),
        ("Repeat Failure Rate", "repeat_failure_rate", "lower"),
        ("Profile Drift Rate", "profile_drift_rate", "lower"),
    ]

    for label, key, _dir in rows:
        item = m[key]
        detail = f"{item['numerator']}/{item['denominator']}"
        lines.append(
            f"| {label} | {_pct(item['value'])} | {_pct(item['threshold'])} | {item['status']} | {detail} |"
        )

    lines.extend(
        [
            "",
            "## Window Counts",
            "",
            f"- decisions: {snapshot['counts']['decisions']}",
            f"- precommit_checks: {snapshot['counts']['precommit_checks']}",
            f"- failures: {snapshot['counts']['failures']}",
            f"- trigger_events: {snapshot['counts']['trigger_events']}",
            f"- psych_observations: {snapshot['counts']['psych_observations']}",
            "",
            "## Notes",
            "",
            f"- High-risk domains source: {', '.join(snapshot['refs']['high_risk_domains'])}",
            "- This report is quantitative and should be paired with weekly/audit narrative outputs.",
        ]
    )

    return "\n".join(lines) + "\n"
