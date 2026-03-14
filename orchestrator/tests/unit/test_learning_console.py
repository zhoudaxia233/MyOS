from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from learning_console import (
    apply_learning_candidate_verdict,
    build_learning_handoff_packet,
    ingest_learning_handoff_response,
    list_recent_learning_candidates,
    promote_learning_candidate,
    summarize_learning_pipeline,
    summarize_learning_pipeline_trend,
)
from cognition_authority import ratify_cognition_revision_candidate
from profile_authority import ratify_profile_trait_candidate
from principles_authority import ratify_principle_candidate
from runtime_eligibility import set_runtime_eligibility


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


def _prepare_principles_foundation(root: Path) -> None:
    constitution = root / "modules/principles/data/constitution.yaml"
    constitution.parent.mkdir(parents=True, exist_ok=True)
    constitution.write_text(
        "\n".join(
            [
                "constitution_version: 1",
                "clauses:",
                '  - clause_id: "pr_0001"',
                '    title: "Existing principle"',
                '    statement: "Keep a stable anchor under change."',
                '    rationale: "Baseline constitutional guidance."',
                '    override_policy: "allowed_with_owner_confirmation"',
                "",
            ]
        ),
        encoding="utf-8",
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


def _prepare_profile_foundation(root: Path) -> None:
    psych_profile = root / "modules/profile/data/psych_profile.yaml"
    psych_profile.parent.mkdir(parents=True, exist_ok=True)
    psych_profile.write_text(
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


def _prepare_cognition_foundation(root: Path) -> None:
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


def _write_jsonl(path: Path, schema_name: str, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    schema = {"_schema": {"name": schema_name, "version": "1.0", "fields": fields, "notes": "append-only"}}
    with path.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(schema) + "\n")
        for row in rows:
            handle.write(json.dumps(row) + "\n")


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
        assert promotion["runtime_eligibility_ref"].startswith("re_")
        assert promotion["runtime_eligibility_status"] == "eligible"

        eligibility_lines = (root / "modules/decision/logs/runtime_eligibility.jsonl").read_text(encoding="utf-8").splitlines()
        eligibility_record = json.loads(eligibility_lines[-1])
        assert eligibility_record["artifact_ref"] == promotion["module_candidate_ref"]
        assert eligibility_record["promotion_ref"] == promotion["promotion_record_id"]
        assert eligibility_record["eligibility_status"] == "eligible"
        assert eligibility_record["scope_modules"] == ["memory"]
        assert eligibility_record["autonomy_ceiling"] == "suggest_only"


def test_summarize_learning_pipeline_trend_compares_7d_vs_30d() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        now = datetime(2026, 3, 8, 10, 0, tzinfo=timezone.utc)

        _write_jsonl(
            root / "orchestrator/logs/learning_candidates.jsonl",
            "learning_candidates",
            ["id", "created_at", "status", "candidate_type", "candidate_state", "proposal_target"],
            [
                {
                    "id": "lc_1",
                    "created_at": "2026-03-07T10:00:00Z",
                    "status": "active",
                    "candidate_type": "insight",
                    "candidate_state": "pending_review",
                    "proposal_target": "memory",
                },
                {
                    "id": "lc_2",
                    "created_at": "2026-03-05T10:00:00Z",
                    "status": "active",
                    "candidate_type": "rule",
                    "candidate_state": "pending_review",
                    "proposal_target": "decision",
                },
                {
                    "id": "lc_3",
                    "created_at": "2026-02-20T10:00:00Z",
                    "status": "active",
                    "candidate_type": "insight",
                    "candidate_state": "pending_review",
                    "proposal_target": "memory",
                },
                {
                    "id": "lc_4",
                    "created_at": "2026-02-16T10:00:00Z",
                    "status": "active",
                    "candidate_type": "principle",
                    "candidate_state": "pending_review",
                    "proposal_target": "principle",
                },
            ],
        )
        _write_jsonl(
            root / "modules/decision/logs/learning_candidate_verdicts.jsonl",
            "learning_candidate_verdicts",
            ["id", "created_at", "status", "candidate_ref", "verdict"],
            [
                {
                    "id": "lv_1",
                    "created_at": "2026-03-07T11:00:00Z",
                    "status": "active",
                    "candidate_ref": "lc_1",
                    "verdict": "reject",
                },
                {
                    "id": "lv_2",
                    "created_at": "2026-03-05T11:00:00Z",
                    "status": "active",
                    "candidate_ref": "lc_2",
                    "verdict": "accept",
                },
                {
                    "id": "lv_3",
                    "created_at": "2026-02-20T11:00:00Z",
                    "status": "active",
                    "candidate_ref": "lc_3",
                    "verdict": "accept",
                },
            ],
        )
        _write_jsonl(
            root / "modules/decision/logs/learning_candidate_promotions.jsonl",
            "learning_candidate_promotions",
            ["id", "created_at", "status", "candidate_ref", "promotion_target"],
            [
                {
                    "id": "lp_1",
                    "created_at": "2026-02-20T12:00:00Z",
                    "status": "active",
                    "candidate_ref": "lc_3",
                    "promotion_target": "memory",
                }
            ],
        )

        trend = summarize_learning_pipeline_trend(root, now=now)
        assert trend["windows"]["7d"]["reviewed_total"] == 2
        assert trend["windows"]["30d"]["reviewed_total"] == 3
        assert trend["inflow"]["7d"] == 2
        assert trend["inflow"]["30d"] == 4

        comparisons = {item["key"]: item for item in trend["comparisons"]}
        assert comparisons["reject_ratio"]["trend"] == "worsening"
        assert comparisons["promotion_conversion_rate"]["trend"] == "worsening"
        assert comparisons["backlog_pressure"]["trend"] == "improving"


def test_set_runtime_eligibility_still_allows_lightweight_artifacts() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _prepare_memory_logs(root)
        result = ingest_learning_handoff_response(
            root,
            json.dumps(
                {
                    "source": {"title": "P", "url": "u4", "source_type": "video"},
                    "summary": "s4",
                    "key_points": ["p4"],
                    "candidate_artifacts": {"insights": [{"statement": "keep runtime heuristics lightweight"}]},
                }
            ),
        )
        candidate_id = result["candidate_record_ids"][0]
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
        assert promotion["runtime_eligibility_status"] == "eligible"

        held = set_runtime_eligibility(
            root,
            candidate_ref=candidate_id,
            eligibility_status="holding",
            change_note="pause lightweight runtime influence",
        )
        assert held["runtime_eligibility_status"] == "holding"
        assert held["runtime_change_note"] == "pause lightweight runtime influence"

        updated = set_runtime_eligibility(
            root,
            candidate_ref=candidate_id,
            eligibility_status="eligible",
            change_note="owner explicitly allows lightweight runtime influence now",
        )
        assert updated["runtime_eligibility_status"] == "eligible"
        assert updated["runtime_state"] in {"cooling", "active"}
        assert updated["runtime_change_note"] == "owner explicitly allows lightweight runtime influence now"

        eligibility_lines = (root / "modules/decision/logs/runtime_eligibility.jsonl").read_text(encoding="utf-8").splitlines()
        assert len(eligibility_lines) >= 4
        latest = json.loads(eligibility_lines[-1])
        assert latest["candidate_ref"] == candidate_id
        assert latest["eligibility_status"] == "eligible"
        assert latest["replaces_eligibility_ref"]


def test_class_c_artifacts_remain_held_pending_ratification() -> None:
    cases = [
        ("profile_traits", "profile_trait", "Prefer slower commitment under stress."),
        ("principles", "principle", "Protect downside first across domains."),
        ("cognition_revisions", "cognition_revision", "Treat repeated overload as schema failure, not motive failure."),
    ]

    for section_key, candidate_type, statement in cases:
        with TemporaryDirectory() as td:
            root = Path(td)
            _prepare_memory_logs(root)
            result = ingest_learning_handoff_response(
                root,
                json.dumps(
                    {
                        "source": {"title": "P", "url": f"u-{candidate_type}", "source_type": "video"},
                        "summary": "serious artifact candidate",
                        "key_points": ["typed seriousness"],
                        "candidate_artifacts": {section_key: [{"statement": statement}]},
                    }
                ),
            )
            candidate_id = result["candidate_record_ids"][0]
            apply_learning_candidate_verdict(
                root,
                candidate_id=candidate_id,
                verdict="accept",
                owner_note="accepted for ledger only",
            )
            promotion = promote_learning_candidate(
                root,
                candidate_id=candidate_id,
                approval_note="approved for ledger promotion",
            )
            assert promotion["runtime_eligibility_status"] == "holding"

            recent = list_recent_learning_candidates(root, include_resolved=True)
            matched = next(item for item in recent if item["id"] == candidate_id)
            assert matched["candidate_type"] == candidate_type
            assert matched["runtime_eligibility_status"] == "holding"
            assert "ratification" in str(matched.get("runtime_change_note") or "")

            try:
                set_runtime_eligibility(
                    root,
                    candidate_ref=candidate_id,
                    eligibility_status="eligible",
                    change_note="attempt generic release",
                )
                assert False, f"{candidate_type} should not become runtime-eligible through the generic path"
            except ValueError as exc:
                message = str(exc)
                assert candidate_type in message
                assert "ratification" in message or "canonicalization" in message


def test_principle_can_be_runtime_eligible_after_canonicalization() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _prepare_memory_logs(root)
        _prepare_principles_foundation(root)

        result = ingest_learning_handoff_response(
            root,
            json.dumps(
                {
                    "source": {"title": "P", "url": "u-principle", "source_type": "video"},
                    "summary": "principle candidate",
                    "key_points": ["typed seriousness"],
                    "candidate_artifacts": {"principles": [{"statement": "Protect downside first across domains."}]},
                }
            ),
        )
        candidate_id = result["candidate_record_ids"][0]
        apply_learning_candidate_verdict(
            root,
            candidate_id=candidate_id,
            verdict="accept",
            owner_note="accept for ledger",
        )
        promotion = promote_learning_candidate(
            root,
            candidate_id=candidate_id,
            approval_note="approve ledger promotion",
        )
        assert promotion["runtime_eligibility_status"] == "holding"

        ratified = ratify_principle_candidate(
            root,
            candidate_ref=candidate_id,
            ratification_note="Approve constitution write.",
        )
        assert ratified["canonical_clause_id"].startswith("pr_")

        updated = set_runtime_eligibility(
            root,
            candidate_ref=candidate_id,
            eligibility_status="eligible",
            change_note="release runtime authority after canonicalization",
        )
        assert updated["runtime_eligibility_status"] == "eligible"

        recent = list_recent_learning_candidates(root, include_resolved=True)
        matched = next(item for item in recent if item["id"] == candidate_id)
        assert matched["lifecycle_stage"] == "canonicalized"
        assert matched["runtime_eligibility_status"] == "eligible"
        assert matched["canonicalized_at"]


def test_profile_trait_can_be_runtime_eligible_after_canonicalization() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _prepare_memory_logs(root)
        _prepare_profile_foundation(root)

        result = ingest_learning_handoff_response(
            root,
            json.dumps(
                {
                    "source": {"title": "P", "url": "u-profile", "source_type": "video"},
                    "summary": "profile trait candidate",
                    "key_points": ["typed seriousness"],
                    "candidate_artifacts": {
                        "profile_traits": [{"statement": "Prefer slower commitment when stress signals are elevated."}]
                    },
                }
            ),
        )
        candidate_id = result["candidate_record_ids"][0]
        apply_learning_candidate_verdict(
            root,
            candidate_id=candidate_id,
            verdict="accept",
            owner_note="accept for ledger",
        )
        promotion = promote_learning_candidate(
            root,
            candidate_id=candidate_id,
            approval_note="approve ledger promotion",
        )
        assert promotion["runtime_eligibility_status"] == "holding"

        ratified = ratify_profile_trait_candidate(
            root,
            candidate_ref=candidate_id,
            ratification_note="Approve psych profile update.",
        )
        assert ratified["canonical_profile_trait_id"].startswith("pft_")

        updated = set_runtime_eligibility(
            root,
            candidate_ref=candidate_id,
            eligibility_status="eligible",
            change_note="release runtime authority after canonicalization",
        )
        assert updated["runtime_eligibility_status"] == "eligible"

        recent = list_recent_learning_candidates(root, include_resolved=True)
        matched = next(item for item in recent if item["id"] == candidate_id)
        assert matched["lifecycle_stage"] == "canonicalized"
        assert matched["runtime_eligibility_status"] == "eligible"
        assert matched["canonicalized_at"]
        assert matched["canonical_profile_trait_id"]


def test_cognition_revision_can_be_runtime_eligible_after_canonicalization() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _prepare_memory_logs(root)
        _prepare_cognition_foundation(root)

        result = ingest_learning_handoff_response(
            root,
            json.dumps(
                {
                    "source": {"title": "P", "url": "u-cognition", "source_type": "video"},
                    "summary": "cognition revision candidate",
                    "key_points": ["typed seriousness"],
                    "candidate_artifacts": {
                        "cognition_revisions": [
                            {"statement": "Treat repeated overload as schema failure, not motive failure."}
                        ]
                    },
                }
            ),
        )
        candidate_id = result["candidate_record_ids"][0]
        apply_learning_candidate_verdict(
            root,
            candidate_id=candidate_id,
            verdict="accept",
            owner_note="accept for ledger",
        )
        promotion = promote_learning_candidate(
            root,
            candidate_id=candidate_id,
            approval_note="approve ledger promotion",
        )
        assert promotion["runtime_eligibility_status"] == "holding"

        ratified = ratify_cognition_revision_candidate(
            root,
            candidate_ref=candidate_id,
            ratification_note="Approve schema lineage write.",
            canonicalization_mode="seed",
            parent_schema_version_id=None,
        )
        assert ratified["canonical_schema_version_id"].startswith("sv_")
        assert ratified["canonicalization_mode"] == "seed"

        updated = set_runtime_eligibility(
            root,
            candidate_ref=candidate_id,
            eligibility_status="eligible",
            change_note="release runtime authority after canonicalization",
        )
        assert updated["runtime_eligibility_status"] == "eligible"

        recent = list_recent_learning_candidates(root, include_resolved=True)
        matched = next(item for item in recent if item["id"] == candidate_id)
        assert matched["lifecycle_stage"] == "canonicalized"
        assert matched["runtime_eligibility_status"] == "eligible"
        assert matched["canonicalized_at"]
        assert matched["canonical_schema_version_id"]
        assert matched["canonicalization_mode"] == "seed"
        assert matched["canonical_lineage_justification"] is None
        assert matched["canonical_parent_schema_version_id"] is None


def test_summarize_learning_pipeline_includes_promotion_readiness() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        now = datetime(2026, 3, 8, 10, 0, tzinfo=timezone.utc)

        _write_jsonl(
            root / "orchestrator/logs/learning_candidates.jsonl",
            "learning_candidates",
            ["id", "created_at", "status", "candidate_type", "candidate_state", "proposal_target"],
            [
                {
                    "id": "lc_1",
                    "created_at": "2026-03-07T10:00:00Z",
                    "status": "active",
                    "candidate_type": "insight",
                    "candidate_state": "pending_review",
                    "proposal_target": "memory",
                }
            ],
        )
        _write_jsonl(
            root / "modules/decision/logs/learning_candidate_promotions.jsonl",
            "learning_candidate_promotions",
            ["id", "created_at", "status", "candidate_ref", "promotion_target"],
            [
                {
                    "id": "lp_old",
                    "created_at": "2026-03-06T09:00:00Z",
                    "status": "active",
                    "candidate_ref": "lc_old",
                    "promotion_target": "memory",
                },
                {
                    "id": "lp_new",
                    "created_at": "2026-03-08T02:00:00Z",
                    "status": "active",
                    "candidate_ref": "lc_new",
                    "promotion_target": "decision",
                },
            ],
        )

        summary = summarize_learning_pipeline(root, window_days=30, now=now)
        readiness = summary["promotion_readiness"]
        assert readiness["maturity_hours"] == 24
        assert readiness["ready_total"] == 1
        assert readiness["cooling_total"] == 1
        assert readiness["ready_by_target"]["memory"] == 1
        assert readiness["cooling_by_target"]["decision"] == 1
