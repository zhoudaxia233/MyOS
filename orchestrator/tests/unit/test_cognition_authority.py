from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from cognition_authority import ratify_cognition_revision_candidate


def _write_jsonl(path: Path, schema_name: str, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    schema = {"_schema": {"name": schema_name, "version": "1.0", "fields": fields, "notes": "append-only"}}
    with path.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(schema) + "\n")
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def test_ratify_cognition_revision_candidate_appends_schema_lineage() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _write_jsonl(
            root / "modules/cognition/logs/schema_versions.jsonl",
            "schema_versions",
            [
                "id",
                "created_at",
                "status",
                "schema_id",
                "version",
                "topic",
                "schema_name",
                "summary",
                "assumptions",
                "predictions",
                "boundaries",
                "parent_schema_version_id",
                "source_refs",
                "tags",
                "object_type",
                "proposal_target",
            ],
            [
                {
                    "id": "sv_20260314_001",
                    "created_at": "2026-03-14T09:00:00Z",
                    "status": "active",
                    "schema_id": "sm_treat_repeated_overload_as_schema_failure_not_motive_failure",
                    "version": 1,
                    "topic": "Treat repeated overload as schema failure, not motive failure.",
                    "schema_name": "Treat repeated overload as schema failure, not motive failure.",
                    "summary": "Baseline schema before refinement.",
                    "assumptions": ["Baseline assumption"],
                    "predictions": ["Baseline prediction"],
                    "boundaries": ["Baseline boundary"],
                    "parent_schema_version_id": None,
                    "source_refs": [],
                    "tags": ["baseline"],
                    "object_type": "cognition",
                    "proposal_target": "cognition",
                }
            ],
        )
        _write_jsonl(
            root / "modules/cognition/logs/accommodation_revisions.jsonl",
            "accommodation_revisions",
            [
                "id",
                "created_at",
                "status",
                "topic",
                "previous_schema_version_id",
                "new_schema_version_id",
                "revision_type",
                "failed_assumptions",
                "revision_summary",
                "new_schema_hypothesis",
                "source_refs",
                "tags",
                "object_type",
                "proposal_target",
            ],
            [],
        )
        _write_jsonl(
            root / "orchestrator/logs/learning_candidates.jsonl",
            "learning_candidates",
            ["id", "created_at", "status", "candidate_type", "title", "statement", "rationale", "evidence", "source_refs", "proposal_target"],
            [
                {
                    "id": "lc_20260314_001",
                    "created_at": "2026-03-14T09:00:00Z",
                    "status": "active",
                    "candidate_type": "cognition_revision",
                    "title": "Treat repeated overload as schema failure, not motive failure.",
                    "statement": "Treat repeated overload as schema failure, not motive failure.",
                    "rationale": "This improves schema-level diagnosis under repeated overload.",
                    "evidence": ["Repeated overload events"],
                    "source_refs": ["li_20260314_001"],
                    "proposal_target": "cognition",
                }
            ],
        )
        _write_jsonl(
            root / "modules/decision/logs/learning_candidate_promotions.jsonl",
            "learning_candidate_promotions",
            ["id", "created_at", "status", "candidate_ref", "candidate_type", "promotion_target", "approval_ref"],
            [
                {
                    "id": "lp_20260314_001",
                    "created_at": "2026-03-14T09:10:00Z",
                    "status": "active",
                    "candidate_ref": "lc_20260314_001",
                    "candidate_type": "cognition_revision",
                    "promotion_target": "cognition",
                    "approval_ref": "la_20260314_001",
                }
            ],
        )
        _write_jsonl(
            root / "modules/cognition/logs/schema_candidates.jsonl",
            "schema_candidates",
            ["id", "created_at", "status", "candidate_ref", "candidate_type", "title", "statement", "source_refs", "approval_ref", "promotion_ref"],
            [
                {
                    "id": "cc_20260314_001",
                    "created_at": "2026-03-14T09:10:00Z",
                    "status": "active",
                    "candidate_ref": "lc_20260314_001",
                    "candidate_type": "cognition_revision",
                    "title": "Treat repeated overload as schema failure, not motive failure.",
                    "statement": "Treat repeated overload as schema failure, not motive failure.",
                    "source_refs": ["lc_20260314_001", "la_20260314_001", "lp_20260314_001"],
                    "approval_ref": "la_20260314_001",
                    "promotion_ref": "lp_20260314_001",
                }
            ],
        )

        result = ratify_cognition_revision_candidate(
            root,
            candidate_ref="lc_20260314_001",
            ratification_note="Approved as an explicit schema-lineage refinement.",
        )

        assert result["candidate_ref"] == "lc_20260314_001"
        assert result["canonical_schema_version_id"].startswith("sv_")
        assert result["accommodation_revision_id"].startswith("ar_")
        assert result["revision_type"] == "refine"
        assert result["schema_updated"] is True

        schema_lines = (root / "modules/cognition/logs/schema_versions.jsonl").read_text(encoding="utf-8").splitlines()
        latest_schema = json.loads(schema_lines[-1])
        assert latest_schema["parent_schema_version_id"] == "sv_20260314_001"
        assert latest_schema["object_type"] == "cognition"
        assert latest_schema["proposal_target"] == "cognition"
        assert "lc_20260314_001" in latest_schema["source_refs"]

        revision_lines = (root / "modules/cognition/logs/accommodation_revisions.jsonl").read_text(encoding="utf-8").splitlines()
        latest_revision = json.loads(revision_lines[-1])
        assert latest_revision["previous_schema_version_id"] == "sv_20260314_001"
        assert latest_revision["new_schema_version_id"] == result["canonical_schema_version_id"]
        assert latest_revision["revision_type"] == "refine"
        assert latest_revision["object_type"] == "cognition"
        assert latest_revision["proposal_target"] == "cognition"


def test_ratify_cognition_revision_candidate_requires_promoted_candidate() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _write_jsonl(
            root / "modules/cognition/logs/schema_versions.jsonl",
            "schema_versions",
            [
                "id",
                "created_at",
                "status",
                "schema_id",
                "version",
                "topic",
                "schema_name",
                "summary",
                "assumptions",
                "predictions",
                "boundaries",
                "parent_schema_version_id",
                "source_refs",
                "tags",
                "object_type",
                "proposal_target",
            ],
            [],
        )
        _write_jsonl(
            root / "modules/cognition/logs/accommodation_revisions.jsonl",
            "accommodation_revisions",
            [
                "id",
                "created_at",
                "status",
                "topic",
                "previous_schema_version_id",
                "new_schema_version_id",
                "revision_type",
                "failed_assumptions",
                "revision_summary",
                "new_schema_hypothesis",
                "source_refs",
                "tags",
                "object_type",
                "proposal_target",
            ],
            [],
        )
        _write_jsonl(
            root / "orchestrator/logs/learning_candidates.jsonl",
            "learning_candidates",
            ["id", "created_at", "status", "candidate_type", "title", "statement", "source_refs", "proposal_target"],
            [
                {
                    "id": "lc_20260314_002",
                    "created_at": "2026-03-14T09:00:00Z",
                    "status": "active",
                    "candidate_type": "cognition_revision",
                    "title": "Unpromoted schema revision",
                    "statement": "Needs promotion first.",
                    "source_refs": [],
                    "proposal_target": "cognition",
                }
            ],
        )

        with pytest.raises(ValueError) as excinfo:
            ratify_cognition_revision_candidate(
                root,
                candidate_ref="lc_20260314_002",
                ratification_note="try ratify too early",
            )
        assert "promoted before ratification" in str(excinfo.value)
