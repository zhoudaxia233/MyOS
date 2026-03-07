from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from cognition import (
    detect_disequilibrium,
    log_accommodation_revision,
    log_assimilation_event,
    log_equilibration_cycle,
    log_schema_version,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_jsonl(path: Path, schema_name: str, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    schema = {"_schema": {"name": schema_name, "version": "1.0", "fields": fields, "notes": "append-only"}}
    with path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(schema) + "\n")
        for row in rows:
            f.write(json.dumps(row) + "\n")


def test_detect_disequilibrium_collects_cross_module_signals() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        now = _utc_now()

        _write_jsonl(
            root / "modules/decision/logs/failures.jsonl",
            "failures",
            ["id", "created_at", "status", "domain", "what_happened", "root_cause", "prevention", "lesson", "emotional_weight"],
            [
                {
                    "id": "fx_20260307_001",
                    "created_at": now,
                    "status": "active",
                    "domain": "invest",
                    "what_happened": "Investing thesis broke after earnings release.",
                    "root_cause": "Model ignored regime shift signal.",
                    "prevention": "Track invalidation signals explicitly.",
                    "lesson": "Narrative fit was stronger than evidence fit.",
                    "emotional_weight": 8,
                }
            ],
        )

        _write_jsonl(
            root / "modules/decision/logs/decision_gate_checks.jsonl",
            "decision_gate_checks",
            [
                "id",
                "created_at",
                "status",
                "domain",
                "decision",
                "guardrail_check_id",
                "precommit_required",
                "precommit_status",
                "guardrail_status",
                "gate_status",
                "violations",
                "missing_override_fields",
                "source_refs",
            ],
            [
                {
                    "id": "dgc_20260307_001",
                    "created_at": now,
                    "status": "active",
                    "domain": "invest",
                    "decision": "Increase investing risk size without downside.",
                    "guardrail_check_id": None,
                    "precommit_required": True,
                    "precommit_status": "missing",
                    "guardrail_status": "blocked",
                    "gate_status": "blocked",
                    "violations": ["missing_required_fields:max_loss"],
                    "missing_override_fields": [],
                    "source_refs": [],
                }
            ],
        )

        _write_jsonl(
            root / "modules/profile/logs/trigger_events.jsonl",
            "trigger_events",
            ["id", "created_at", "status", "context", "trigger_signal", "response", "mitigation", "emotional_weight", "tags"],
            [
                {
                    "id": "tr_20260307_001",
                    "created_at": now,
                    "status": "active",
                    "context": "investing review",
                    "trigger_signal": "A win streak increased overconfidence.",
                    "response": "Wanted larger risk quickly.",
                    "mitigation": "Re-anchor to max-loss rules.",
                    "emotional_weight": 8,
                    "tags": ["investing", "risk"],
                }
            ],
        )

        _write_jsonl(
            root / "modules/memory/logs/memory_events.jsonl",
            "memory_events",
            ["id", "created_at", "status", "source_type", "event", "why_it_matters", "tags", "source_refs"],
            [
                {
                    "id": "me_20260307_001",
                    "created_at": now,
                    "status": "active",
                    "source_type": "reflection",
                    "event": "Investing model feels wrong and does not fit current behavior.",
                    "why_it_matters": "Repeated mismatch around regime interpretation.",
                    "tags": ["investing", "mismatch"],
                    "source_refs": [],
                }
            ],
        )

        result = detect_disequilibrium(root, topic="investing model", window_days=30)
        record = result["record"]

        assert record["tension_score"] >= 6
        assert "prediction_failure" in record["signal_types"]
        assert "guardrail_block" in record["signal_types"]
        assert "emotional_friction" in record["signal_types"]
        assert "explicit_confusion" in record["signal_types"]

        lines = (root / "modules/cognition/logs/disequilibrium_events.jsonl").read_text(encoding="utf-8").splitlines()
        assert len(lines) >= 2


def test_accommodation_creates_new_schema_version_and_equilibration_cycle() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)

        baseline = log_schema_version(
            root,
            topic="investing",
            schema_name="Momentum thesis",
            summary="Use momentum continuation with bounded downside.",
            assumptions=["Momentum persists for 1-3 sessions."],
            predictions=["Breakouts should hold above invalidation."],
            boundaries=["Do not apply in event-driven gaps."],
            tags=["investing"],
        )

        assimilation = log_assimilation_event(
            root,
            topic="investing",
            schema_version_id=baseline["id"],
            input_summary="Earnings gap broke structure quickly.",
            interpreted_as="Possible regime shift invalidating continuation.",
            fit_score=4,
            stretch_points=["Schema does not handle event-driven volatility."],
            source_refs=[],
            tags=["earnings"],
        )
        assert assimilation["fit_score"] == 4

        accommodation = log_accommodation_revision(
            root,
            topic="investing",
            previous_schema_version_id=baseline["id"],
            revision_type="split",
            failed_assumptions=["Momentum persists for 1-3 sessions."],
            revision_summary="Separate normal momentum from event-regime conditions.",
            new_schema_hypothesis="Use separate schema for event-driven sessions.",
            assumptions=["Momentum schema only valid outside event windows."],
            predictions=["Event sessions require separate invalidation logic."],
            boundaries=["Disable baseline schema around earnings events."],
            source_refs=[assimilation["id"]],
            tags=["regime_split"],
        )

        assert accommodation["new_schema"] is not None
        new_schema = accommodation["new_schema"]
        assert new_schema["version"] == 2
        assert new_schema["parent_schema_version_id"] == baseline["id"]

        eq = log_equilibration_cycle(
            root,
            topic="investing",
            from_schema_version_id=baseline["id"],
            to_schema_version_id=new_schema["id"],
            stabilizing_tests=["Apply split schema to next two event windows."],
            residual_tensions=["Need better event-volatility thresholds."],
            coherence_score=7,
            source_refs=[accommodation["revision"]["id"]],
            tags=["equilibration"],
        )
        assert eq["coherence_score"] == 7

        eq_lines = (root / "modules/cognition/logs/equilibration_cycles.jsonl").read_text(encoding="utf-8").splitlines()
        assert len(eq_lines) >= 2
