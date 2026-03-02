import json
from datetime import datetime, timezone
from pathlib import Path

from metrics import compute_drift_metrics


def _write_jsonl(path: Path, schema_name: str, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    schema = {"_schema": {"name": schema_name, "version": "1.0", "fields": fields, "notes": "append-only"}}
    with path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(schema) + "\n")
        for row in rows:
            f.write(json.dumps(row) + "\n")


def test_compute_drift_metrics_windowed() -> None:
    now = datetime(2026, 3, 2, 12, 0, tzinfo=timezone.utc)

    from tempfile import TemporaryDirectory

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
                    "created_at": "2026-03-01T10:00:00Z",
                    "domain": "invest",
                    "guardrail_check_id": "pc_1",
                },
                {
                    "id": "dc_2",
                    "created_at": "2026-03-01T11:00:00Z",
                    "domain": "project",
                    "guardrail_check_id": None,
                },
                {
                    "id": "dc_3",
                    "created_at": "2026-03-01T12:00:00Z",
                    "domain": "content",
                    "guardrail_check_id": None,
                },
            ],
        )

        _write_jsonl(
            root / "modules/decision/logs/precommit_checks.jsonl",
            "precommit_checks",
            ["id", "created_at", "cooldown_required", "result"],
            [
                {
                    "id": "pc_1",
                    "created_at": "2026-03-01T10:00:00Z",
                    "cooldown_required": True,
                    "result": "pass_with_cooldown",
                },
                {
                    "id": "pc_2",
                    "created_at": "2026-03-01T11:00:00Z",
                    "cooldown_required": True,
                    "result": "blocked",
                },
            ],
        )

        _write_jsonl(
            root / "modules/decision/logs/failures.jsonl",
            "failures",
            ["id", "created_at", "root_cause"],
            [
                {"id": "fx_1", "created_at": "2026-03-01T08:00:00Z", "root_cause": "scope creep"},
                {"id": "fx_2", "created_at": "2026-03-01T09:00:00Z", "root_cause": "scope creep"},
                {"id": "fx_3", "created_at": "2026-03-01T10:00:00Z", "root_cause": "late review"},
            ],
        )

        _write_jsonl(
            root / "modules/profile/logs/trigger_events.jsonl",
            "trigger_events",
            ["id", "created_at", "emotional_weight"],
            [
                {"id": "tr_1", "created_at": "2026-03-01T07:00:00Z", "emotional_weight": 8},
                {"id": "tr_2", "created_at": "2026-03-01T07:30:00Z", "emotional_weight": 4},
            ],
        )

        _write_jsonl(
            root / "modules/profile/logs/psych_observations.jsonl",
            "psych_observations",
            ["id", "created_at", "confidence"],
            [
                {"id": "po_1", "created_at": "2026-03-01T06:00:00Z", "confidence": 9},
                {"id": "po_2", "created_at": "2026-03-01T06:30:00Z", "confidence": 6},
            ],
        )

        snapshot = compute_drift_metrics(root, window_days=7, now=now)

        assert snapshot["metrics"]["precommit_coverage"]["value"] == 0.5
        assert snapshot["metrics"]["precommit_coverage"]["status"] == "fail"
        assert snapshot["metrics"]["cooldown_compliance"]["value"] == 0.5
        assert snapshot["metrics"]["cooldown_compliance"]["status"] == "fail"
        assert round(snapshot["metrics"]["repeat_failure_rate"]["value"], 4) == round(2 / 3, 4)
        assert snapshot["metrics"]["repeat_failure_rate"]["status"] == "fail"
        assert snapshot["metrics"]["profile_drift_rate"]["value"] == 0.5
        assert snapshot["metrics"]["profile_drift_rate"]["status"] == "warn"
