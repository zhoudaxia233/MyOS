from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from cognition_authority import list_cognition_schema_options, ratify_cognition_revision_candidate


def _write_jsonl(path: Path, schema_name: str, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    schema = {"_schema": {"name": schema_name, "version": "1.0", "fields": fields, "notes": "append-only"}}
    with path.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(schema) + "\n")
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def _prepare_cognition_logs(root: Path, schema_rows: list[dict] | None = None) -> None:
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
        schema_rows or [],
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


def _prepare_promoted_cognition_candidate(
    root: Path,
    *,
    candidate_id: str,
    title: str,
    statement: str,
    evidence: list[str] | None = None,
) -> None:
    _write_jsonl(
        root / "orchestrator/logs/learning_candidates.jsonl",
        "learning_candidates",
        [
            "id",
            "created_at",
            "status",
            "candidate_type",
            "title",
            "statement",
            "rationale",
            "evidence",
            "source_refs",
            "proposal_target",
        ],
        [
            {
                "id": candidate_id,
                "created_at": "2026-03-14T09:00:00Z",
                "status": "active",
                "candidate_type": "cognition_revision",
                "title": title,
                "statement": statement,
                "rationale": "Refines cognition schema interpretation.",
                "evidence": evidence or ["Repeated overload events"],
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
                "candidate_ref": candidate_id,
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
                "candidate_ref": candidate_id,
                "candidate_type": "cognition_revision",
                "title": title,
                "statement": statement,
                "source_refs": [candidate_id, "la_20260314_001", "lp_20260314_001"],
                "approval_ref": "la_20260314_001",
                "promotion_ref": "lp_20260314_001",
            }
        ],
    )


def test_ratify_cognition_revision_candidate_allows_explicit_seed_without_parent() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _prepare_cognition_logs(root)
        _prepare_promoted_cognition_candidate(
            root,
            candidate_id="lc_20260314_001",
            title="Treat repeated overload as schema failure, not motive failure.",
            statement="Treat repeated overload as schema failure, not motive failure.",
        )

        result = ratify_cognition_revision_candidate(
            root,
            candidate_ref="lc_20260314_001",
            ratification_note="Approve a new canonical schema root.",
            canonicalization_mode="seed",
            parent_schema_version_id=None,
        )

        assert result["candidate_ref"] == "lc_20260314_001"
        assert result["canonicalization_mode"] == "seed"
        assert result["canonical_schema_version_id"].startswith("sv_")
        assert result["parent_schema_version_id"] is None
        assert result["accommodation_revision_id"] is None
        assert result["revision_type"] is None
        assert result["schema_updated"] is True

        schema_lines = (root / "modules/cognition/logs/schema_versions.jsonl").read_text(encoding="utf-8").splitlines()
        latest_schema = json.loads(schema_lines[-1])
        assert latest_schema["parent_schema_version_id"] is None
        assert latest_schema["object_type"] == "cognition"
        assert latest_schema["proposal_target"] == "cognition"
        assert "lc_20260314_001" in latest_schema["source_refs"]

        revision_lines = (root / "modules/cognition/logs/accommodation_revisions.jsonl").read_text(encoding="utf-8").splitlines()
        assert len(revision_lines) == 1


def test_ratify_cognition_revision_candidate_requires_explicit_parent_for_revision() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _prepare_cognition_logs(
            root,
            schema_rows=[
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
        _prepare_promoted_cognition_candidate(
            root,
            candidate_id="lc_20260314_002",
            title="Treat repeated overload as schema failure, not motive failure.",
            statement="Treat repeated overload as schema failure, not motive failure.",
        )

        result = ratify_cognition_revision_candidate(
            root,
            candidate_ref="lc_20260314_002",
            ratification_note="Approved as an explicit schema-lineage refinement.",
            canonicalization_mode="revision",
            parent_schema_version_id="sv_20260314_001",
            lineage_justification="This candidate directly refines the existing overload-diagnosis lineage instead of starting a new root.",
            revision_type="replace",
        )

        assert result["canonicalization_mode"] == "revision"
        assert result["canonical_schema_version_id"].startswith("sv_")
        assert result["accommodation_revision_id"].startswith("ar_")
        assert result["parent_schema_version_id"] == "sv_20260314_001"
        assert result["lineage_justification"].startswith("This candidate directly refines")
        assert result["revision_type"] == "replace"

        schema_lines = (root / "modules/cognition/logs/schema_versions.jsonl").read_text(encoding="utf-8").splitlines()
        latest_schema = json.loads(schema_lines[-1])
        assert latest_schema["parent_schema_version_id"] == "sv_20260314_001"

        revision_lines = (root / "modules/cognition/logs/accommodation_revisions.jsonl").read_text(encoding="utf-8").splitlines()
        latest_revision = json.loads(revision_lines[-1])
        assert latest_revision["previous_schema_version_id"] == "sv_20260314_001"
        assert latest_revision["new_schema_version_id"] == result["canonical_schema_version_id"]
        assert latest_revision["revision_type"] == "replace"
        assert latest_revision["object_type"] == "cognition"
        assert latest_revision["proposal_target"] == "cognition"
        assert "Lineage justification:" in latest_revision["revision_summary"]
        assert "Ratification note:" in latest_revision["revision_summary"]


def test_ratify_cognition_revision_candidate_requires_promoted_candidate() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _prepare_cognition_logs(root)
        _write_jsonl(
            root / "orchestrator/logs/learning_candidates.jsonl",
            "learning_candidates",
            ["id", "created_at", "status", "candidate_type", "title", "statement", "source_refs", "proposal_target"],
            [
                {
                    "id": "lc_20260314_003",
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
                candidate_ref="lc_20260314_003",
                ratification_note="try ratify too early",
                canonicalization_mode="seed",
            )
        assert "promoted before ratification" in str(excinfo.value)


def test_ratify_cognition_revision_candidate_rejects_revision_without_parent() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _prepare_cognition_logs(root)
        _prepare_promoted_cognition_candidate(
            root,
            candidate_id="lc_20260314_004",
            title="Need an explicit parent",
            statement="Revision without parent should fail.",
        )

        with pytest.raises(ValueError) as excinfo:
            ratify_cognition_revision_candidate(
                root,
                candidate_ref="lc_20260314_004",
                ratification_note="should fail without parent",
                canonicalization_mode="revision",
                parent_schema_version_id=None,
                lineage_justification="This still tries to revise an existing lineage.",
            )
        assert "parent_schema_version_id is required" in str(excinfo.value)


def test_ratify_cognition_revision_candidate_rejects_revision_with_missing_parent() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _prepare_cognition_logs(root)
        _prepare_promoted_cognition_candidate(
            root,
            candidate_id="lc_20260314_005",
            title="Need an existing parent",
            statement="Revision with missing parent should fail.",
        )

        with pytest.raises(ValueError) as excinfo:
            ratify_cognition_revision_candidate(
                root,
                candidate_ref="lc_20260314_005",
                ratification_note="should fail with unknown parent",
                canonicalization_mode="revision",
                parent_schema_version_id="sv_missing",
                lineage_justification="This candidate claims to extend the missing lineage.",
            )
        assert "parent_schema_version_id not found" in str(excinfo.value)


def test_ratify_cognition_revision_candidate_rejects_revision_without_lineage_justification() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _prepare_cognition_logs(
            root,
            schema_rows=[
                {
                    "id": "sv_20260314_011",
                    "created_at": "2026-03-14T09:00:00Z",
                    "status": "active",
                    "schema_id": "sm_existing_revision_root",
                    "version": 1,
                    "topic": "Existing revision root",
                    "schema_name": "Existing revision root",
                    "summary": "Baseline schema.",
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
        _prepare_promoted_cognition_candidate(
            root,
            candidate_id="lc_20260314_007",
            title="Revision needs a lineage reason",
            statement="Revision without lineage justification should fail.",
        )

        with pytest.raises(ValueError) as excinfo:
            ratify_cognition_revision_candidate(
                root,
                candidate_ref="lc_20260314_007",
                ratification_note="parent exists, but rationale is missing",
                canonicalization_mode="revision",
                parent_schema_version_id="sv_20260314_011",
                lineage_justification=None,
                revision_type="refine",
            )
        assert "lineage_justification is required" in str(excinfo.value)


def test_ratify_cognition_revision_candidate_rejects_revision_without_revision_type() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _prepare_cognition_logs(
            root,
            schema_rows=[
                {
                    "id": "sv_20260314_012",
                    "created_at": "2026-03-14T09:00:00Z",
                    "status": "active",
                    "schema_id": "sm_existing_revision_type_root",
                    "version": 1,
                    "topic": "Existing revision type root",
                    "schema_name": "Existing revision type root",
                    "summary": "Baseline schema.",
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
        _prepare_promoted_cognition_candidate(
            root,
            candidate_id="lc_20260314_008",
            title="Revision needs an explicit type",
            statement="Revision without type should fail.",
        )

        with pytest.raises(ValueError) as excinfo:
            ratify_cognition_revision_candidate(
                root,
                candidate_ref="lc_20260314_008",
                ratification_note="type is still missing",
                canonicalization_mode="revision",
                parent_schema_version_id="sv_20260314_012",
                lineage_justification="This candidate clearly extends the selected lineage.",
                revision_type=None,
            )
        assert "revision_type is required" in str(excinfo.value)


def test_ratify_cognition_revision_candidate_rejects_seed_with_parent() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _prepare_cognition_logs(
            root,
            schema_rows=[
                {
                    "id": "sv_20260314_010",
                    "created_at": "2026-03-14T09:00:00Z",
                    "status": "active",
                    "schema_id": "sm_existing",
                    "version": 1,
                    "topic": "Existing schema",
                    "schema_name": "Existing schema",
                    "summary": "Baseline schema.",
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
        _prepare_promoted_cognition_candidate(
            root,
            candidate_id="lc_20260314_006",
            title="Seed must not carry a parent",
            statement="Seed with parent should fail.",
        )

        with pytest.raises(ValueError) as excinfo:
            ratify_cognition_revision_candidate(
                root,
                candidate_ref="lc_20260314_006",
                ratification_note="seed must reject parent lineage",
                canonicalization_mode="seed",
                parent_schema_version_id="sv_20260314_010",
            )
        assert "must be absent when canonicalization_mode=seed" in str(excinfo.value)


def test_ratify_cognition_revision_candidate_rejects_seed_with_revision_type() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _prepare_cognition_logs(root)
        _prepare_promoted_cognition_candidate(
            root,
            candidate_id="lc_20260314_009",
            title="Seed must not carry a revision type",
            statement="Seed with revision type should fail.",
        )

        with pytest.raises(ValueError) as excinfo:
            ratify_cognition_revision_candidate(
                root,
                candidate_ref="lc_20260314_009",
                ratification_note="seed must reject revision-only semantics",
                canonicalization_mode="seed",
                parent_schema_version_id=None,
                revision_type="refine",
            )
        assert "revision_type applies only when canonicalization_mode=revision" in str(excinfo.value)


def test_list_cognition_schema_options_exposes_parent_context() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _prepare_cognition_logs(
            root,
            schema_rows=[
                {
                    "id": "sv_20260314_001",
                    "created_at": "2026-03-14T09:00:00Z",
                    "status": "active",
                    "schema_id": "sm_root",
                    "version": 1,
                    "topic": "Root schema",
                    "schema_name": "Root schema",
                    "summary": "Baseline cognition root.",
                    "assumptions": ["baseline"],
                    "predictions": ["predict"],
                    "boundaries": ["bound"],
                    "parent_schema_version_id": None,
                    "source_refs": [],
                    "tags": ["baseline"],
                    "object_type": "cognition",
                    "proposal_target": "cognition",
                },
                {
                    "id": "sv_20260314_002",
                    "created_at": "2026-03-14T10:00:00Z",
                    "status": "active",
                    "schema_id": "sm_root",
                    "version": 2,
                    "topic": "Root schema revised",
                    "schema_name": "Root schema revised",
                    "summary": "A later revision in the same lineage.",
                    "assumptions": ["refined"],
                    "predictions": ["predict better"],
                    "boundaries": ["bound"],
                    "parent_schema_version_id": "sv_20260314_001",
                    "source_refs": [],
                    "tags": ["revision"],
                    "object_type": "cognition",
                    "proposal_target": "cognition",
                },
            ],
        )

        options = list_cognition_schema_options(root)

        assert [item["id"] for item in options] == ["sv_20260314_002", "sv_20260314_001"]
        assert options[0]["lineage_role"] == "revision"
        assert options[0]["parent_schema_version_id"] == "sv_20260314_001"
        assert options[1]["lineage_role"] == "root"
        assert options[1]["parent_schema_version_id"] is None
