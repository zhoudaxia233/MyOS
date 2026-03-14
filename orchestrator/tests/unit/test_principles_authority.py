from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from principles_authority import ratify_principle_candidate


def _write_jsonl(path: Path, schema_name: str, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    schema = {"_schema": {"name": schema_name, "version": "1.0", "fields": fields, "notes": "append-only"}}
    with path.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(schema) + "\n")
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def test_ratify_principle_candidate_appends_amendment_and_constitution_clause() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        (root / "modules/principles/data").mkdir(parents=True, exist_ok=True)
        (root / "modules/principles/data/constitution.yaml").write_text(
            "\n".join(
                [
                    'constitution:',
                    '  version: "1.0"',
                    '  owner: "zdx"',
                    '  intent: "Preserve long-term judgment continuity under delegated execution."',
                    "",
                    "clauses:",
                    '  - clause_id: "pr_0001"',
                    '    title: "Execution and judgment separation"',
                    '    statement: "Execution scales, but judgment remains owner-governed."',
                    '    rationale: "Protects strategic control."',
                    '    override_policy: "allowed_with_owner_confirmation"',
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
                    "candidate_type": "principle",
                    "title": "Protect downside first",
                    "statement": "Across domains, avoid strategies that sacrifice bounded downside discipline.",
                    "rationale": "The clause preserves capital and judgment continuity under stress.",
                    "source_refs": ["li_20260314_001"],
                    "proposal_target": "principle",
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
                    "candidate_type": "principle",
                    "promotion_target": "principle",
                    "approval_ref": "la_20260314_001",
                }
            ],
        )
        _write_jsonl(
            root / "modules/principles/logs/principle_candidates.jsonl",
            "principle_candidates",
            ["id", "created_at", "status", "candidate_ref", "candidate_type", "title", "statement", "source_refs", "approval_ref", "promotion_ref"],
            [
                {
                    "id": "prc_20260314_001",
                    "created_at": "2026-03-14T09:10:00Z",
                    "status": "active",
                    "candidate_ref": "lc_20260314_001",
                    "candidate_type": "principle",
                    "title": "Protect downside first",
                    "statement": "Across domains, avoid strategies that sacrifice bounded downside discipline.",
                    "source_refs": ["lc_20260314_001", "la_20260314_001", "lp_20260314_001"],
                    "approval_ref": "la_20260314_001",
                    "promotion_ref": "lp_20260314_001",
                }
            ],
        )
        _write_jsonl(
            root / "modules/principles/logs/principle_amendments.jsonl",
            "principle_amendments",
            [
                "id",
                "created_at",
                "status",
                "object_type",
                "principle_id",
                "change_type",
                "proposal_summary",
                "rationale",
                "evidence_refs",
                "approval_ref",
                "effective_from",
                "source_refs",
                "proposal_target",
            ],
            [],
        )

        result = ratify_principle_candidate(
            root,
            candidate_ref="lc_20260314_001",
            ratification_note="Approved as a durable constitutional clause.",
        )

        assert result["candidate_ref"] == "lc_20260314_001"
        assert result["amendment_record_id"].startswith("pam_")
        assert result["ratification_approval_ref"].startswith("ap_")
        assert result["canonical_clause_id"] == "pr_0002"
        assert result["constitution_updated"] is True

        amendment_lines = (root / "modules/principles/logs/principle_amendments.jsonl").read_text(encoding="utf-8").splitlines()
        amendment_record = json.loads(amendment_lines[-1])
        assert amendment_record["principle_id"] == "pr_0002"
        assert amendment_record["change_type"] == "add_clause"
        assert amendment_record["approval_ref"].startswith("ap_")
        assert "lc_20260314_001" in amendment_record["source_refs"]

        constitution_text = (root / "modules/principles/data/constitution.yaml").read_text(encoding="utf-8")
        assert 'clause_id: "pr_0002"' in constitution_text
        assert 'title: "Protect downside first"' in constitution_text
        assert 'statement: "Across domains, avoid strategies that sacrifice bounded downside discipline."' in constitution_text


def test_ratify_principle_candidate_requires_promoted_principle() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        (root / "modules/principles/data").mkdir(parents=True, exist_ok=True)
        (root / "modules/principles/data/constitution.yaml").write_text("constitution:\n\nclauses:\n", encoding="utf-8")
        _write_jsonl(
            root / "orchestrator/logs/learning_candidates.jsonl",
            "learning_candidates",
            ["id", "created_at", "status", "candidate_type", "title", "statement", "source_refs", "proposal_target"],
            [
                {
                    "id": "lc_20260314_002",
                    "created_at": "2026-03-14T09:00:00Z",
                    "status": "active",
                    "candidate_type": "principle",
                    "title": "Unpromoted principle",
                    "statement": "Needs promotion first.",
                    "source_refs": [],
                    "proposal_target": "principle",
                }
            ],
        )

        with pytest.raises(ValueError) as excinfo:
            ratify_principle_candidate(
                root,
                candidate_ref="lc_20260314_002",
                ratification_note="try ratify too early",
            )
        assert "promoted before ratification" in str(excinfo.value)
