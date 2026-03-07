from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from learning_ingest import ingest_learning_asset, ingest_learning_text


def _now_prefix(prefix: str) -> str:
    return datetime.now(timezone.utc).strftime(f"{prefix}_%Y%m%d_")


def _prepare_logs(root: Path) -> tuple[Path, Path]:
    events = root / "modules/memory/logs/memory_events.jsonl"
    insights = root / "modules/memory/logs/memory_insights.jsonl"
    events.parent.mkdir(parents=True, exist_ok=True)

    events_schema = {
        "_schema": {
            "name": "memory_events",
            "version": "1.0",
            "fields": ["id", "created_at", "status", "source_type", "event", "why_it_matters", "tags", "source_refs"],
            "notes": "append-only",
        }
    }
    insights_schema = {
        "_schema": {
            "name": "memory_insights",
            "version": "1.0",
            "fields": ["id", "created_at", "status", "insight", "evidence", "source_refs", "confidence", "tags"],
            "notes": "append-only",
        }
    }
    events.write_text(json.dumps(events_schema) + "\n", encoding="utf-8")
    insights.write_text(json.dumps(insights_schema) + "\n", encoding="utf-8")
    return events, insights


def test_ingest_learning_asset_appends_event_and_insight() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        events_log, insights_log = _prepare_logs(root)

        source = root / "learning.md"
        source.write_text(
            "\n".join(
                [
                    "# Reverse Thinking Stories",
                    "",
                    "- When A/B fail, search option C.",
                    "- Align incentives with human motives.",
                    "- Inspect value-chain mechanism before commitment.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        result = ingest_learning_asset(
            root,
            source,
            source_type="video",
            max_points=6,
            confidence=8,
            dry_run=False,
            extra_tags=["strategy"],
        )

        assert result["appended_events"] == 1
        assert result["appended_insights"] == 1
        assert len(result["record_ids"]) == 2
        assert result["event_ids"][0].startswith(_now_prefix("me"))
        assert result["insight_ids"][0].startswith(_now_prefix("mi"))

        event_lines = events_log.read_text(encoding="utf-8").splitlines()
        insight_lines = insights_log.read_text(encoding="utf-8").splitlines()
        assert len(event_lines) == 2
        assert len(insight_lines) == 2

        event = json.loads(event_lines[-1])
        insight = json.loads(insight_lines[-1])
        assert event["source_type"] == "external_observation"
        assert "learning_asset" in event["tags"]
        assert "strategy" in event["tags"]
        assert insight["source_refs"] == [event["id"]]
        assert insight["confidence"] == 8


def test_ingest_learning_asset_dry_run_does_not_append() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        events_log, insights_log = _prepare_logs(root)

        source = root / "notes.txt"
        source.write_text("Key lesson: design better checks before execution.\n", encoding="utf-8")

        result = ingest_learning_asset(root, source, dry_run=True)
        assert result["dry_run"] is True
        assert result["appended_events"] == 0
        assert result["appended_insights"] == 0

        assert len(events_log.read_text(encoding="utf-8").splitlines()) == 1
        assert len(insights_log.read_text(encoding="utf-8").splitlines()) == 1


def test_ingest_learning_asset_reads_json_payload() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _prepare_logs(root)

        source = root / "asset.json"
        source.write_text(
            json.dumps(
                {
                    "title": "Negotiation Lessons",
                    "summary": "Focus on alignment, not force.",
                    "core_points": [
                        "Model the counterpart's motive.",
                        "Offer choices that preserve optionality.",
                    ],
                }
            ),
            encoding="utf-8",
        )

        result = ingest_learning_asset(root, source, source_type="article", dry_run=False)
        assert result["title"] == "Negotiation Lessons"
        assert result["source_type"] == "article"
        assert result["core_points_count"] >= 2


def test_ingest_learning_text_appends_from_inline_content() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        events_log, insights_log = _prepare_logs(root)

        result = ingest_learning_text(
            root,
            "When A/B fail, try option C. Align motives. Inspect hidden value chain.",
            title="Inline learning",
            source_type="video",
            confidence=7,
            dry_run=False,
            extra_tags=["inline"],
        )
        assert result["input_path"] == "<inline>"
        assert result["title"] == "Inline learning"
        assert result["appended_events"] == 1
        assert result["appended_insights"] == 1
        assert len(events_log.read_text(encoding="utf-8").splitlines()) == 2
        assert len(insights_log.read_text(encoding="utf-8").splitlines()) == 2
