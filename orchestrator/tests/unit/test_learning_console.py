from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from learning_console import (
    apply_learning_candidate_verdict,
    build_learning_handoff_packet,
    ingest_learning_handoff_response,
    list_recent_learning_candidates,
    promote_learning_candidate,
)


def _prepare_memory_logs(root: Path) -> None:
    events = root / "modules/memory/logs/memory_events.jsonl"
    insights = root / "modules/memory/logs/memory_insights.jsonl"
    events.parent.mkdir(parents=True, exist_ok=True)

    events_schema = {
        "_schema": {
            "name": "memory_events",
            "version": "1.1",
            "fields": [
                "id",
                "created_at",
                "status",
                "source_type",
                "event",
                "why_it_matters",
                "tags",
                "source_refs",
                "object_type",
                "proposal_target",
            ],
            "notes": "append-only",
        }
    }
    insights_schema = {
        "_schema": {
            "name": "memory_insights",
            "version": "1.1",
            "fields": [
                "id",
                "created_at",
                "status",
                "insight",
                "evidence",
                "source_refs",
                "confidence",
                "tags",
                "object_type",
                "proposal_target",
            ],
            "notes": "append-only",
        }
    }

    events.write_text(json.dumps(events_schema) + "\n", encoding="utf-8")
    insights.write_text(json.dumps(insights_schema) + "\n", encoding="utf-8")


def test_build_learning_handoff_packet_has_schema_block() -> None:
    packet = build_learning_handoff_packet(
        "https://www.youtube.com/watch?v=abc123",
        title="Interview X",
        source_type="video",
    )
    assert packet["source_ref"].startswith("https://")
    assert packet["source_type_hint"] == "video"
    assert "required_response_schema" in packet["packet_text"]
    assert "candidate_artifacts" in packet["packet_text"]


def test_ingest_learning_handoff_response_appends_import_and_candidates() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _prepare_memory_logs(root)

        response = {
            "source": {
                "title": "Long Interview",
                "url": "https://www.youtube.com/watch?v=xyz",
                "source_type": "video",
            },
            "summary": "The speaker emphasizes decision hygiene and explicit schema checks.",
            "key_points": [
                "Use falsification checks before committing to a high-risk move.",
                "Track repeated mismatch as schema signal.",
            ],
            "candidate_artifacts": {
                "insights": [
                    {
                        "title": "Decision hygiene",
                        "statement": "High-risk moves need explicit disconfirming signal.",
                        "evidence": ["Repeated failures came from missing invalidation tests."],
                        "confidence": 0.8,
                    }
                ],
                "rules": [
                    {
                        "title": "Falsification-first",
                        "rule": "If a decision is high-risk, define downside and disconfirming signal first.",
                        "when_to_apply": "Before final commitment",
                        "evidence": ["Interview examples and failure stories"],
                        "confidence": 0.7,
                    }
                ],
            },
        }

        text = "```json\n" + json.dumps(response) + "\n```"
        result = ingest_learning_handoff_response(root, text, tags=["unit_test"])

        assert result["dry_run"] is False
        assert result["candidate_total"] == 2
        assert len(result["memory_record_ids"]) == 2
        assert result["import_record_id"].startswith("li_")
        assert all(cid.startswith("lc_") for cid in result["candidate_record_ids"])

        imports_path = root / "modules/memory/logs/learning_imports.jsonl"
        candidates_path = root / "orchestrator/logs/learning_candidates.jsonl"
        assert imports_path.exists()
        assert candidates_path.exists()

        import_rows = imports_path.read_text(encoding="utf-8").splitlines()
        candidate_rows = candidates_path.read_text(encoding="utf-8").splitlines()
        assert len(import_rows) == 2
        assert len(candidate_rows) == 3

        import_record = json.loads(import_rows[-1])
        assert import_record["candidate_count"] == 2
        assert import_record["object_type"] == "memory"
        assert import_record["proposal_target"] == "memory"

        candidate_record = json.loads(candidate_rows[-1])
        assert candidate_record["candidate_state"] == "pending_review"
        assert candidate_record["object_type"] == "system"
        assert candidate_record["proposal_target"] in {"memory", "decision", "system", "principle", "cognition"}


def test_list_recent_learning_candidates_filters_pending() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        path = root / "orchestrator/logs/learning_candidates.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        schema = {
            "_schema": {
                "name": "learning_candidates",
                "version": "1.0",
                "fields": [
                    "id",
                    "created_at",
                    "status",
                    "candidate_type",
                    "candidate_state",
                    "title",
                    "statement",
                    "rationale",
                    "evidence",
                    "confidence",
                    "source_refs",
                    "source_material_ref",
                    "approval_ref",
                    "owner_decision",
                    "object_type",
                    "proposal_target",
                ],
                "notes": "append-only",
            }
        }
        rows = [
            schema,
            {
                "id": "lc_20260308_001",
                "created_at": "2026-03-08T10:00:00Z",
                "status": "active",
                "candidate_type": "insight",
                "candidate_state": "pending_review",
                "title": "keep",
                "statement": "keep me",
                "rationale": None,
                "evidence": [],
                "confidence": 7,
                "source_refs": ["li_20260308_001"],
                "source_material_ref": "x",
                "approval_ref": None,
                "owner_decision": None,
                "object_type": "system",
                "proposal_target": "memory",
            },
            {
                "id": "lc_20260308_002",
                "created_at": "2026-03-08T09:00:00Z",
                "status": "active",
                "candidate_type": "rule",
                "candidate_state": "promoted",
                "title": "drop",
                "statement": "drop me",
                "rationale": None,
                "evidence": [],
                "confidence": 7,
                "source_refs": ["li_20260308_001"],
                "source_material_ref": "x",
                "approval_ref": "or_20260308_001",
                "owner_decision": "accept",
                "object_type": "system",
                "proposal_target": "decision",
            },
        ]
        with path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row) + "\n")

        result = list_recent_learning_candidates(root, limit=10)
        assert len(result) == 1
        assert result[0]["id"] == "lc_20260308_001"


def test_apply_learning_candidate_verdict_accept_hides_candidate_from_queue() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _prepare_memory_logs(root)
        result = ingest_learning_handoff_response(
            root,
            json.dumps(
                {
                    "source": {"title": "A", "url": "u", "source_type": "video"},
                    "summary": "s",
                    "key_points": ["p"],
                    "candidate_artifacts": {"insights": [{"statement": "candidate one"}]},
                }
            ),
        )
        candidate_id = result["candidate_record_ids"][0]

        verdict = apply_learning_candidate_verdict(
            root,
            candidate_id=candidate_id,
            verdict="accept",
            owner_note="Aligned with current judgment.",
        )
        assert verdict["verdict"] == "accept"
        assert verdict["candidate_ref"] == candidate_id

        pending = list_recent_learning_candidates(root, limit=10)
        assert all(item["id"] != candidate_id for item in pending)


def test_apply_learning_candidate_verdict_modify_creates_replacement() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _prepare_memory_logs(root)
        result = ingest_learning_handoff_response(
            root,
            json.dumps(
                {
                    "source": {"title": "B", "url": "u2", "source_type": "video"},
                    "summary": "s2",
                    "key_points": ["p2"],
                    "candidate_artifacts": {"rules": [{"rule": "if high risk then check downside"}]},
                }
            ),
        )
        candidate_id = result["candidate_record_ids"][0]

        verdict = apply_learning_candidate_verdict(
            root,
            candidate_id=candidate_id,
            verdict="modify",
            owner_note="Need stricter boundary.",
            modified_statement="If decision is high-risk, require downside + invalidation + disconfirming signal.",
        )
        replacement_id = verdict["replacement_candidate_ref"]
        assert replacement_id is not None

        pending = list_recent_learning_candidates(root, limit=10)
        pending_ids = [item["id"] for item in pending]
        assert candidate_id not in pending_ids
        assert replacement_id in pending_ids


def test_promote_learning_candidate_requires_accept_and_creates_records() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _prepare_memory_logs(root)
        result = ingest_learning_handoff_response(
            root,
            json.dumps(
                {
                    "source": {"title": "P", "url": "u3", "source_type": "video"},
                    "summary": "s3",
                    "key_points": ["p3"],
                    "candidate_artifacts": {"insights": [{"statement": "candidate promo"}]},
                }
            ),
        )
        candidate_id = result["candidate_record_ids"][0]

        try:
            promote_learning_candidate(root, candidate_id=candidate_id, approval_note="try")
            assert False, "promotion should require accepted verdict"
        except ValueError as exc:
            assert "accepted before promotion" in str(exc)

        apply_learning_candidate_verdict(
            root,
            candidate_id=candidate_id,
            verdict="accept",
            owner_note="accept first",
        )
        promotion = promote_learning_candidate(
            root,
            candidate_id=candidate_id,
            approval_note="approved for promotion",
        )
        assert promotion["approval_record_id"].startswith("la_")
        assert promotion["promotion_record_id"].startswith("lp_")
        assert promotion["candidate_ref"] == candidate_id
        assert promotion["module_candidate_ref"].startswith("ic_")
        assert promotion["module_candidate_path"] == "modules/memory/logs/insight_candidates.jsonl"
