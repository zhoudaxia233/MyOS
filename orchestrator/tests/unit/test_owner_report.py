import json
from datetime import datetime, timezone
from pathlib import Path

from owner_report import build_owner_snapshot, render_owner_report


def _write_jsonl(path: Path, schema_name: str, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    schema = {"_schema": {"name": schema_name, "version": "1.0", "fields": fields, "notes": "append-only"}}
    with path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(schema) + "\n")
        for row in rows:
            f.write(json.dumps(row) + "\n")


def test_owner_snapshot_and_render() -> None:
    from tempfile import TemporaryDirectory

    now = datetime(2026, 3, 3, 10, 0, tzinfo=timezone.utc)

    with TemporaryDirectory() as td:
        root = Path(td)

        (root / "modules/decision/data").mkdir(parents=True, exist_ok=True)
        (root / "modules/decision/data/impulse_guardrails.yaml").write_text(
            "high_risk_domains:\n  - \"invest\"\n  - \"project\"\n", encoding="utf-8"
        )

        _write_jsonl(
            root / "modules/decision/logs/decisions.jsonl",
            "decisions",
            ["id", "created_at", "domain", "guardrail_check_id"],
            [
                {
                    "id": "dc_1",
                    "created_at": "2026-03-02T10:00:00Z",
                    "domain": "invest",
                    "guardrail_check_id": None,
                }
            ],
        )

        _write_jsonl(
            root / "modules/decision/logs/precommit_checks.jsonl",
            "precommit_checks",
            ["id", "created_at", "cooldown_required", "result"],
            [
                {
                    "id": "pc_1",
                    "created_at": "2026-03-02T10:00:00Z",
                    "cooldown_required": True,
                    "result": "pass_with_cooldown",
                }
            ],
        )

        _write_jsonl(
            root / "modules/decision/logs/failures.jsonl",
            "failures",
            ["id", "created_at", "root_cause"],
            [{"id": "fx_1", "created_at": "2026-03-02T09:30:00Z", "root_cause": "review latency"}],
        )

        _write_jsonl(
            root / "modules/profile/logs/trigger_events.jsonl",
            "trigger_events",
            ["id", "created_at", "emotional_weight"],
            [],
        )

        _write_jsonl(
            root / "modules/profile/logs/psych_observations.jsonl",
            "psych_observations",
            ["id", "created_at", "confidence"],
            [],
        )

        _write_jsonl(
            root / "modules/decision/logs/guardrail_overrides.jsonl",
            "guardrail_overrides",
            ["id", "created_at", "domain"],
            [{"id": "go_1", "created_at": "2026-03-02T11:00:00Z", "domain": "invest"}],
        )

        (root / "modules/decision/outputs").mkdir(parents=True, exist_ok=True)
        (root / "modules/decision/outputs/decision_audit_20260302.md").write_text(
            "No major exceptions in this window.", encoding="utf-8"
        )
        (root / "modules/decision/outputs/weekly_review_20260302.md").write_text(
            "Sample-size limitation noted.", encoding="utf-8"
        )
        (root / "modules/decision/outputs/metrics_20260302.md").write_text(
            "\n".join(
                [
                    "# Drift Dashboard",
                    "",
                    "| Metric | Value | Threshold | Status | Detail |",
                    "|---|---:|---:|---|---|",
                    "| Precommit Coverage | 90.0% | 80.0% | pass | 9/10 |",
                    "| Cooldown Compliance | 100.0% | 90.0% | pass | 1/1 |",
                    "| Repeat Failure Rate | 0.0% | 30.0% | pass | 0/1 |",
                    "| Profile Drift Rate | 0.0% | 40.0% | pass | 0/0 |",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (root / "modules/cognition/outputs").mkdir(parents=True, exist_ok=True)
        (root / "modules/cognition/outputs/cognitive_timeline_20260302.md").write_text(
            "Cognitive Evolution Timeline", encoding="utf-8"
        )

        snapshot = build_owner_snapshot(root, window_days=7, now=now)
        report = render_owner_report(snapshot)

        assert snapshot["override_count"] == 1
        assert any(a.startswith("metrics_mismatch:precommit_coverage:") for a in snapshot["consistency_alerts"])
        assert any(a.startswith("decision_audit_conflict:") for a in snapshot["consistency_alerts"])
        assert any(a.startswith("weekly_review_conflict:") for a in snapshot["consistency_alerts"])
        assert isinstance(snapshot["auto_triggers"], list)
        assert "guardrail_overrides.invest" in report
        assert "Consistency Alerts" in report
        assert "Auto Triggers" in report
        assert "Owner Report" in report
        assert "Executive Summary" in report
        assert "cognition_timeline" in report
