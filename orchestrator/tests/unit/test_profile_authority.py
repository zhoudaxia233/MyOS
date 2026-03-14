from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from profile_authority import ratify_profile_trait_candidate


def _write_jsonl(path: Path, schema_name: str, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    schema = {"_schema": {"name": schema_name, "version": "1.0", "fields": fields, "notes": "append-only"}}
    with path.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(schema) + "\n")
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def test_ratify_profile_trait_candidate_appends_profile_change_and_psych_profile_trait() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        (root / "modules/profile/data").mkdir(parents=True, exist_ok=True)
        (root / "modules/profile/data/psych_profile.yaml").write_text(
            "\n".join(
                [
                    'profile_type: "operational_non_clinical"',
                    'intent: "Improve self-regulation quality in high-impact decisions and execution cycles."',
                    "",
                    "stabilizers:",
                    '  - "Written precommit checklist for high-risk decisions"',
                    "",
                ]
            ),
            encoding="utf-8",
        )
        _write_jsonl(
            root / "orchestrator/logs/learning_candidates.jsonl",
            "learning_candidates",
            ["id", "created_at", "status", "candidate_type", "title", "statement", "rationale", "source_refs", "proposal_target"],
            [
                {
                    "id": "lc_20260314_001",
                    "created_at": "2026-03-14T09:00:00Z",
                    "status": "active",
                    "candidate_type": "profile_trait",
                    "title": "Slower commitment under stress",
                    "statement": "Prefer slower commitment when stress signals are elevated.",
                    "rationale": "The trait reduces impulsive escalation under pressure.",
                    "source_refs": ["li_20260314_001"],
                    "proposal_target": "profile",
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
                    "candidate_type": "profile_trait",
                    "promotion_target": "profile",
                    "approval_ref": "la_20260314_001",
                }
            ],
        )
        _write_jsonl(
            root / "modules/profile/logs/profile_trait_candidates.jsonl",
            "profile_trait_candidates",
            ["id", "created_at", "status", "candidate_ref", "candidate_type", "title", "statement", "source_refs", "approval_ref", "promotion_ref"],
            [
                {
                    "id": "ptc_20260314_001",
                    "created_at": "2026-03-14T09:10:00Z",
                    "status": "active",
                    "candidate_ref": "lc_20260314_001",
                    "candidate_type": "profile_trait",
                    "title": "Slower commitment under stress",
                    "statement": "Prefer slower commitment when stress signals are elevated.",
                    "source_refs": ["lc_20260314_001", "la_20260314_001", "lp_20260314_001"],
                    "approval_ref": "la_20260314_001",
                    "promotion_ref": "lp_20260314_001",
                }
            ],
        )
        _write_jsonl(
            root / "modules/profile/logs/profile_changes.jsonl",
            "profile_changes",
            [
                "id",
                "created_at",
                "status",
                "change_type",
                "change_summary",
                "reason",
                "expected_effect",
                "source_refs",
                "object_type",
                "proposal_target",
            ],
            [],
        )

        result = ratify_profile_trait_candidate(
            root,
            candidate_ref="lc_20260314_001",
            ratification_note="Approved as a durable self-model update.",
        )

        assert result["candidate_ref"] == "lc_20260314_001"
        assert result["profile_change_record_id"].startswith("pf_")
        assert result["ratification_approval_ref"].startswith("ap_")
        assert result["canonical_profile_trait_id"] == "pft_0001"
        assert result["profile_updated"] is True

        change_lines = (root / "modules/profile/logs/profile_changes.jsonl").read_text(encoding="utf-8").splitlines()
        change_record = json.loads(change_lines[-1])
        assert change_record["change_type"] == "profile_trait_canonicalized"
        assert change_record["change_summary"] == "Slower commitment under stress"
        assert "lc_20260314_001" in change_record["source_refs"]
        assert "pft_0001" in change_record["source_refs"]

        psych_profile_text = (root / "modules/profile/data/psych_profile.yaml").read_text(encoding="utf-8")
        assert "ratified_traits:" in psych_profile_text
        assert 'trait_id: "pft_0001"' in psych_profile_text
        assert 'title: "Slower commitment under stress"' in psych_profile_text
        assert 'statement: "Prefer slower commitment when stress signals are elevated."' in psych_profile_text


def test_ratify_profile_trait_candidate_requires_promoted_profile_trait() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        (root / "modules/profile/data").mkdir(parents=True, exist_ok=True)
        (root / "modules/profile/data/psych_profile.yaml").write_text('profile_type: "operational_non_clinical"\n', encoding="utf-8")
        _write_jsonl(
            root / "orchestrator/logs/learning_candidates.jsonl",
            "learning_candidates",
            ["id", "created_at", "status", "candidate_type", "title", "statement", "source_refs", "proposal_target"],
            [
                {
                    "id": "lc_20260314_002",
                    "created_at": "2026-03-14T09:00:00Z",
                    "status": "active",
                    "candidate_type": "profile_trait",
                    "title": "Unpromoted trait",
                    "statement": "Needs promotion first.",
                    "source_refs": [],
                    "proposal_target": "profile",
                }
            ],
        )

        with pytest.raises(ValueError) as excinfo:
            ratify_profile_trait_candidate(
                root,
                candidate_ref="lc_20260314_002",
                ratification_note="try ratify too early",
            )
        assert "promoted before ratification" in str(excinfo.value)
