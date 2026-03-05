from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from chat_ingest import ingest_chat_export, load_chat_messages


def _now_prefix(prefix: str) -> str:
    return datetime.now(timezone.utc).strftime(f"{prefix}_%Y%m%d_")


def _prepare_memory_log(root: Path) -> Path:
    path = root / "modules/memory/logs/memory_events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    schema = {
        "_schema": {
            "name": "memory_events",
            "version": "1.0",
            "fields": ["id", "created_at", "status", "source_type", "event", "why_it_matters", "tags", "source_refs"],
            "notes": "append-only",
        }
    }
    path.write_text(json.dumps(schema) + "\n", encoding="utf-8")
    return path


def test_ingest_chat_export_appends_records_from_json() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        memory_log = _prepare_memory_log(root)

        input_path = root / "chat.json"
        input_payload = [
            {"role": "user", "content": "I should review my decision process weekly."},
            {"role": "assistant", "content": "Use a structured weekly review checklist."},
            {"role": "user", "content": "I need better risk limits for investments."},
        ]
        input_path.write_text(json.dumps(input_payload), encoding="utf-8")

        result = ingest_chat_export(root, input_path, max_events=10, dry_run=False, extra_tags=["work"])
        assert result["event_count"] == 2
        assert result["appended_count"] == 2
        assert len(result["record_ids"]) == 2
        assert all(rid.startswith(_now_prefix("me")) for rid in result["record_ids"])

        lines = memory_log.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 3
        rec = json.loads(lines[-1])
        assert rec["source_type"] == "chat"
        assert rec["status"] == "active"
        assert "imported" in rec["tags"]
        assert "work" in rec["tags"]
        assert isinstance(rec["source_refs"], list)


def test_ingest_chat_export_dry_run_does_not_append() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        memory_log = _prepare_memory_log(root)

        input_path = root / "chat.txt"
        input_path.write_text("User: Note one\nAssistant: Reply one\n", encoding="utf-8")

        result = ingest_chat_export(root, input_path, dry_run=True, extra_tags=[])
        assert result["event_count"] == 1
        assert result["appended_count"] == 0
        assert result["dry_run"] is True

        lines = memory_log.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1


def test_load_chat_messages_parses_text_roles() -> None:
    with TemporaryDirectory() as td:
        path = Path(td) / "chat.md"
        path.write_text(
            "\n".join(
                [
                    "User: first user point",
                    "Assistant: first assistant point",
                    "User: second user point",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        msgs = load_chat_messages(path)
        assert len(msgs) == 3
        assert msgs[0]["role"] == "user"
        assert msgs[1]["role"] == "assistant"
