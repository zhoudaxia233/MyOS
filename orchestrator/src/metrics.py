from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

COGNITION_METRIC_DIRECTIONS = {
    "unresolved_disequilibrium_rate": "lower",
    "equilibration_quality_rate": "higher",
    "schema_explicitness_rate": "higher",
}


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


def _status_higher_better_no_data_warn(value: float, threshold: float, denominator: int) -> str:
    if denominator <= 0:
        return "warn"
    return _status_higher_better(value, threshold)


def _trend_direction(*, direction: str, value_7d: float, value_30d: float, epsilon: float = 0.02) -> str:
    delta = value_7d - value_30d
    if abs(delta) <= epsilon:
        return "stable"
    if direction == "higher":
        return "improving" if delta > 0 else "worsening"
    return "improving" if delta < 0 else "worsening"


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
    schema_versions = _window_filter(
        _load_jsonl(repo_root / "modules/cognition/logs/schema_versions.jsonl"), now, window_days
    )
    assimilation_events = _window_filter(
        _load_jsonl(repo_root / "modules/cognition/logs/assimilation_events.jsonl"), now, window_days
    )
    disequilibrium_events = _window_filter(
        _load_jsonl(repo_root / "modules/cognition/logs/disequilibrium_events.jsonl"), now, window_days
    )
    accommodation_revisions = _window_filter(
        _load_jsonl(repo_root / "modules/cognition/logs/accommodation_revisions.jsonl"), now, window_days
    )
    equilibration_cycles = _window_filter(
        _load_jsonl(repo_root / "modules/cognition/logs/equilibration_cycles.jsonl"), now, window_days
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

    high_tension_events = [
        e for e in disequilibrium_events if int(e.get("tension_score", 0) or 0) >= 6
    ]
    high_tension_ids = {str(e.get("id", "")).strip() for e in high_tension_events if str(e.get("id", "")).strip()}

    resolved_high_tension_ids: set[str] = set()
    for row in accommodation_revisions:
        refs = row.get("source_refs", [])
        if not isinstance(refs, list):
            continue
        for ref in refs:
            rid = str(ref).strip()
            if rid and rid in high_tension_ids:
                resolved_high_tension_ids.add(rid)

    for row in equilibration_cycles:
        refs = row.get("source_refs", [])
        if not isinstance(refs, list):
            continue
        for ref in refs:
            rid = str(ref).strip()
            if rid and rid in high_tension_ids:
                resolved_high_tension_ids.add(rid)

    unresolved_high_tension = len(high_tension_ids - resolved_high_tension_ids)
    unresolved_disequilibrium_rate = _safe_ratio(unresolved_high_tension, len(high_tension_events))

    high_quality_equilibrations = [
        e for e in equilibration_cycles if int(e.get("coherence_score", 0) or 0) >= 7
    ]
    equilibration_quality_rate = _safe_ratio(len(high_quality_equilibrations), len(equilibration_cycles))

    schema_linked_assimilations = [
        e for e in assimilation_events if str(e.get("schema_version_id", "")).strip()
    ]
    schema_explicitness_rate = _safe_ratio(len(schema_linked_assimilations), len(assimilation_events))

    thresholds = {
        "precommit_coverage": 0.8,
        "cooldown_compliance": 0.9,
        "repeat_failure_rate": 0.3,
        "profile_drift_rate": 0.4,
        "unresolved_disequilibrium_rate": 0.4,
        "equilibration_quality_rate": 0.6,
        "schema_explicitness_rate": 0.9,
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
        "unresolved_disequilibrium_rate": {
            "value": unresolved_disequilibrium_rate,
            "threshold": thresholds["unresolved_disequilibrium_rate"],
            "status": _status_lower_better(
                unresolved_disequilibrium_rate, thresholds["unresolved_disequilibrium_rate"]
            ),
            "numerator": unresolved_high_tension,
            "denominator": len(high_tension_events),
        },
        "equilibration_quality_rate": {
            "value": equilibration_quality_rate,
            "threshold": thresholds["equilibration_quality_rate"],
            "status": _status_higher_better_no_data_warn(
                equilibration_quality_rate,
                thresholds["equilibration_quality_rate"],
                len(equilibration_cycles),
            ),
            "numerator": len(high_quality_equilibrations),
            "denominator": len(equilibration_cycles),
        },
        "schema_explicitness_rate": {
            "value": schema_explicitness_rate,
            "threshold": thresholds["schema_explicitness_rate"],
            "status": _status_higher_better_no_data_warn(
                schema_explicitness_rate,
                thresholds["schema_explicitness_rate"],
                len(assimilation_events),
            ),
            "numerator": len(schema_linked_assimilations),
            "denominator": len(assimilation_events),
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
            "schema_versions": len(schema_versions),
            "assimilation_events": len(assimilation_events),
            "disequilibrium_events": len(disequilibrium_events),
            "accommodation_revisions": len(accommodation_revisions),
            "equilibration_cycles": len(equilibration_cycles),
        },
        "refs": {
            "high_risk_domains": high_risk_domains,
        },
    }


def compute_cognition_trend(repo_root: Path, now: datetime | None = None) -> dict:
    now = now or _now_utc()
    snap_7d = compute_drift_metrics(repo_root, window_days=7, now=now)
    snap_30d = compute_drift_metrics(repo_root, window_days=30, now=now)

    comparisons: list[dict] = []
    for key, direction in COGNITION_METRIC_DIRECTIONS.items():
        metric_7d = snap_7d["metrics"][key]
        metric_30d = snap_30d["metrics"][key]
        value_7d = float(metric_7d["value"])
        value_30d = float(metric_30d["value"])
        comparisons.append(
            {
                "key": key,
                "direction": direction,
                "value_7d": value_7d,
                "status_7d": metric_7d["status"],
                "value_30d": value_30d,
                "status_30d": metric_30d["status"],
                "delta": value_7d - value_30d,
                "trend": _trend_direction(direction=direction, value_7d=value_7d, value_30d=value_30d),
            }
        )

    return {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "windows": {
            "7d": snap_7d,
            "30d": snap_30d,
        },
        "comparisons": comparisons,
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
        ("Unresolved Disequilibrium Rate", "unresolved_disequilibrium_rate", "lower"),
        ("Equilibration Quality Rate", "equilibration_quality_rate", "higher"),
        ("Schema Explicitness Rate", "schema_explicitness_rate", "higher"),
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
            f"- schema_versions: {snapshot['counts']['schema_versions']}",
            f"- assimilation_events: {snapshot['counts']['assimilation_events']}",
            f"- disequilibrium_events: {snapshot['counts']['disequilibrium_events']}",
            f"- accommodation_revisions: {snapshot['counts']['accommodation_revisions']}",
            f"- equilibration_cycles: {snapshot['counts']['equilibration_cycles']}",
            "",
            "## Notes",
            "",
            f"- High-risk domains source: {', '.join(snapshot['refs']['high_risk_domains'])}",
            "- Cognition metrics summarize schema conflict, revision, and coherence quality.",
            "- This report is quantitative and should be paired with weekly/audit narrative outputs.",
        ]
    )

    trend = snapshot.get("cognitive_trend")
    if isinstance(trend, dict):
        comparisons = trend.get("comparisons", [])
        lines.extend(
            [
                "",
                "## Cognition Trend (7d vs 30d)",
                "",
                "| Metric | 7d | 30d | Delta | Trend |",
                "|---|---:|---:|---:|---|",
            ]
        )
        labels = {
            "unresolved_disequilibrium_rate": "Unresolved Disequilibrium",
            "equilibration_quality_rate": "Equilibration Quality",
            "schema_explicitness_rate": "Schema Explicitness",
        }
        for item in comparisons:
            key = str(item.get("key", ""))
            label = labels.get(key, key)
            v7 = _pct(float(item.get("value_7d", 0.0)))
            v30 = _pct(float(item.get("value_30d", 0.0)))
            delta_pp = (float(item.get("delta", 0.0)) * 100.0)
            delta_text = f"{delta_pp:+.1f}pp"
            trend_text = str(item.get("trend", "stable"))
            lines.append(f"| {label} | {v7} | {v30} | {delta_text} | {trend_text} |")

    return "\n".join(lines) + "\n"
