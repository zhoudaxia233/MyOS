from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from runtime_influence import summarize_recent_runtime_influence_drift


def _write_jsonl(path: Path, schema_name: str, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    schema = {"_schema": {"name": schema_name, "version": "1.0", "fields": fields, "notes": "append-only"}}
    with path.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(schema) + "\n")
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def test_summarize_recent_runtime_influence_drift_detects_added_and_dropped_artifacts() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _write_jsonl(
            root / "orchestrator/logs/runs.jsonl",
            "runs",
            ["id", "created_at", "status", "task", "module", "runtime_influences"],
            [
                {
                    "id": "run_old",
                    "created_at": "2026-03-10T10:00:00Z",
                    "status": "active",
                    "task": "older decision run",
                    "module": "decision",
                    "runtime_influences": [
                        {"artifact_ref": "rule_keep", "artifact_type": "rule", "title": "Keep downside small"},
                        {"artifact_ref": "skill_drop", "artifact_type": "skill", "title": "Momentum entry"},
                    ],
                },
                {
                    "id": "run_new",
                    "created_at": "2026-03-11T10:00:00Z",
                    "status": "active",
                    "task": "latest decision run",
                    "module": "decision",
                    "runtime_influences": [
                        {"artifact_ref": "rule_keep", "artifact_type": "rule", "title": "Keep downside small"},
                        {"artifact_ref": "principle_add", "artifact_type": "principle", "title": "Protect downside first"},
                    ],
                },
            ],
        )

        summary = summarize_recent_runtime_influence_drift(root, limit_runs=6)

        assert summary["runs_considered"] == 2
        assert summary["latest_delta"]["comparison_basis"] == "same_module_previous"
        assert summary["latest_delta"]["latest_run_ref"] == "run_new"
        assert summary["latest_delta"]["previous_run_ref"] == "run_old"
        assert summary["latest_delta"]["stable_total"] == 1
        assert [item["artifact_ref"] for item in summary["latest_delta"]["added"]] == ["principle_add"]
        assert [item["artifact_ref"] for item in summary["latest_delta"]["dropped"]] == ["skill_drop"]
        top_refs = [item["artifact_ref"] for item in summary["top_artifacts"]]
        assert top_refs[:2] == ["rule_keep", "principle_add"]


def test_summarize_recent_runtime_influence_drift_falls_back_to_previous_any_module() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _write_jsonl(
            root / "orchestrator/logs/runs.jsonl",
            "runs",
            ["id", "created_at", "status", "task", "module", "runtime_influences"],
            [
                {
                    "id": "run_decision",
                    "created_at": "2026-03-10T10:00:00Z",
                    "status": "active",
                    "task": "decision run",
                    "module": "decision",
                    "runtime_influences": [{"artifact_ref": "rule_keep", "artifact_type": "rule", "title": "Keep downside small"}],
                },
                {
                    "id": "run_content",
                    "created_at": "2026-03-11T10:00:00Z",
                    "status": "active",
                    "task": "content run",
                    "module": "content",
                    "runtime_influences": [],
                },
            ],
        )

        summary = summarize_recent_runtime_influence_drift(root, limit_runs=6)

        assert summary["latest_delta"]["latest_run_ref"] == "run_content"
        assert summary["latest_delta"]["previous_run_ref"] == "run_decision"
        assert summary["latest_delta"]["comparison_basis"] == "previous_any"
        assert summary["latest_delta"]["latest_influence_total"] == 0
        assert summary["latest_delta"]["previous_influence_total"] == 1
        assert [item["artifact_ref"] for item in summary["latest_delta"]["dropped"]] == ["rule_keep"]
