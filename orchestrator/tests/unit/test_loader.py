import json
from pathlib import Path
from tempfile import TemporaryDirectory

from loader import load_context_bundle


def _write_jsonl(path: Path, schema_name: str, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    schema = {"_schema": {"name": schema_name, "version": "1.0", "fields": fields, "notes": "append-only"}}
    with path.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(schema) + "\n")
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def test_load_context_bundle_from_skill_required_files() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        (root / "core").mkdir(parents=True, exist_ok=True)
        (root / "core/ROUTER.md").write_text("router", encoding="utf-8")

        (root / "modules/decision").mkdir(parents=True, exist_ok=True)
        (root / "modules/decision/MODULE.md").write_text("decision module", encoding="utf-8")
        (root / "modules/decision/data").mkdir(parents=True, exist_ok=True)
        (root / "modules/decision/logs").mkdir(parents=True, exist_ok=True)
        (root / "modules/decision/skills").mkdir(parents=True, exist_ok=True)

        (root / "modules/decision/data/heuristics.yaml").write_text("h: 1", encoding="utf-8")
        (root / "modules/decision/logs/decisions.jsonl").write_text(
            '{"_schema":{"name":"decisions","version":"1.0","fields":[],"notes":"append-only"}}\n',
            encoding="utf-8",
        )
        (root / "modules/content/data/voice.yaml").parent.mkdir(parents=True, exist_ok=True)
        (root / "modules/content/data/voice.yaml").write_text("should_not_load: true", encoding="utf-8")

        (root / "modules/decision/skills/weekly_review.md").write_text(
            "\n".join(
                [
                    "# Skill",
                    "1. `modules/decision/data/heuristics.yaml`",
                    "2. `modules/decision/logs/decisions.jsonl`",
                    "3. `modules/content/data/voice.yaml`",
                    "4. `modules/decision/logs/failures.jsonl` (only if needed)",
                ]
            ),
            encoding="utf-8",
        )

        bundle = load_context_bundle(
            root,
            module="decision",
            max_chars=10000,
            skill_path="modules/decision/skills/weekly_review.md",
        )
        paths = [f["path"] for f in bundle["files"]]

        assert "core/ROUTER.md" in paths
        assert "modules/decision/MODULE.md" in paths
        assert "modules/decision/skills/weekly_review.md" in paths
        assert "modules/decision/data/heuristics.yaml" in paths
        assert "modules/decision/logs/decisions.jsonl" in paths
        assert "modules/content/data/voice.yaml" not in paths
        assert "modules/decision/logs/failures.jsonl" not in paths


def test_load_context_bundle_includes_only_ready_promoted_candidates() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        (root / "core").mkdir(parents=True, exist_ok=True)
        (root / "core/ROUTER.md").write_text("router", encoding="utf-8")

        (root / "modules/decision").mkdir(parents=True, exist_ok=True)
        (root / "modules/decision/MODULE.md").write_text("decision module", encoding="utf-8")

        _write_jsonl(
            root / "modules/decision/logs/learning_candidate_promotions.jsonl",
            "learning_candidate_promotions",
            ["id", "created_at", "status", "candidate_ref", "promotion_target"],
            [
                {
                    "id": "lp_ready",
                    "created_at": "2020-03-07T00:00:00Z",
                    "status": "active",
                    "candidate_ref": "lc_ready",
                    "promotion_target": "decision",
                },
                {
                    "id": "lp_cooling",
                    "created_at": "2099-03-08T09:00:00Z",
                    "status": "active",
                    "candidate_ref": "lc_cooling",
                    "promotion_target": "decision",
                },
            ],
        )
        _write_jsonl(
            root / "modules/decision/logs/rule_candidates.jsonl",
            "rule_candidates",
            ["id", "created_at", "status", "candidate_type", "title", "statement", "promotion_ref"],
            [
                {
                    "id": "rc_ready",
                    "created_at": "2020-03-07T00:05:00Z",
                    "status": "active",
                    "candidate_type": "rule",
                    "title": "Ready rule",
                    "statement": "This one should be loaded.",
                    "promotion_ref": "lp_ready",
                },
                {
                    "id": "rc_cooling",
                    "created_at": "2099-03-08T09:05:00Z",
                    "status": "active",
                    "candidate_type": "rule",
                    "title": "Cooling rule",
                    "statement": "This one should NOT be loaded yet.",
                    "promotion_ref": "lp_cooling",
                },
            ],
        )
        _write_jsonl(
            root / "modules/decision/logs/skill_candidates.jsonl",
            "skill_candidates",
            ["id", "created_at", "status", "candidate_type", "title", "statement", "promotion_ref"],
            [],
        )

        bundle = load_context_bundle(
            root,
            module="decision",
            max_chars=10000,
            skill_path=None,
        )
        files = bundle["files"]
        paths = [f["path"] for f in files]
        assert "orchestrator://runtime_eligible_artifacts" in paths

        promoted = next(f for f in files if f["path"] == "orchestrator://runtime_eligible_artifacts")
        content = promoted["content"]
        assert "Ready rule" in content
        assert "Cooling rule" not in content
        eligibility_path = root / "modules/decision/logs/runtime_eligibility.jsonl"
        assert eligibility_path.exists()
        eligibility_lines = eligibility_path.read_text(encoding="utf-8").splitlines()
        assert len(eligibility_lines) >= 2
        assert any('"eligibility_status": "eligible"' in line for line in eligibility_lines[1:])


def test_load_context_bundle_promoted_candidates_intent_ranking_and_fallback() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        (root / "core").mkdir(parents=True, exist_ok=True)
        (root / "core/ROUTER.md").write_text("router", encoding="utf-8")

        (root / "modules/decision").mkdir(parents=True, exist_ok=True)
        (root / "modules/decision/MODULE.md").write_text("decision module", encoding="utf-8")

        _write_jsonl(
            root / "modules/decision/logs/learning_candidate_promotions.jsonl",
            "learning_candidate_promotions",
            ["id", "created_at", "status", "candidate_ref", "promotion_target"],
            [
                {
                    "id": "lp_high",
                    "created_at": "2020-03-07T00:00:00Z",
                    "status": "active",
                    "candidate_ref": "lc_high",
                    "promotion_target": "decision",
                },
                {
                    "id": "lp_low",
                    "created_at": "2020-03-08T00:00:00Z",
                    "status": "active",
                    "candidate_ref": "lc_low",
                    "promotion_target": "decision",
                },
                {
                    "id": "lp_none",
                    "created_at": "2020-03-09T00:00:00Z",
                    "status": "active",
                    "candidate_ref": "lc_none",
                    "promotion_target": "decision",
                },
            ],
        )
        _write_jsonl(
            root / "modules/decision/logs/rule_candidates.jsonl",
            "rule_candidates",
            ["id", "created_at", "status", "candidate_type", "title", "statement", "promotion_ref"],
            [
                {
                    "id": "rc_high",
                    "created_at": "2020-03-07T00:05:00Z",
                    "status": "active",
                    "candidate_type": "rule",
                    "title": "Risk cooldown rule",
                    "statement": "Delay irreversible decision when risk and cooldown signals spike.",
                    "promotion_ref": "lp_high",
                },
                {
                    "id": "rc_low",
                    "created_at": "2020-03-08T00:05:00Z",
                    "status": "active",
                    "candidate_type": "rule",
                    "title": "Decision checklist",
                    "statement": "Use quick review before committing.",
                    "promotion_ref": "lp_low",
                },
                {
                    "id": "rc_none",
                    "created_at": "2020-03-09T00:05:00Z",
                    "status": "active",
                    "candidate_type": "rule",
                    "title": "Admin cleanup",
                    "statement": "Clear inbox and archive old logs.",
                    "promotion_ref": "lp_none",
                },
            ],
        )
        _write_jsonl(
            root / "modules/decision/logs/skill_candidates.jsonl",
            "skill_candidates",
            ["id", "created_at", "status", "candidate_type", "title", "statement", "promotion_ref"],
            [],
        )

        intent_bundle = load_context_bundle(
            root,
            module="decision",
            max_chars=10000,
            intent_text="risk cooldown decision",
        )
        files = intent_bundle["files"]
        promoted = next(f for f in files if f["path"] == "orchestrator://runtime_eligible_artifacts")
        content = promoted["content"]
        assert "intent_filter: matched_only" in content
        assert "Risk cooldown rule" in content
        assert "Decision checklist" in content
        assert "Admin cleanup" not in content
        assert content.index("Risk cooldown rule") < content.index("Decision checklist")

        fallback_bundle = load_context_bundle(
            root,
            module="decision",
            max_chars=10000,
            intent_text="biochemistry molecule synthesis",
        )
        fallback_files = fallback_bundle["files"]
        fallback_promoted = next(f for f in fallback_files if f["path"] == "orchestrator://runtime_eligible_artifacts")
        fallback_content = fallback_promoted["content"]
        assert "intent_filter: recent_fallback" in fallback_content
        assert "Admin cleanup" in fallback_content


def test_load_context_bundle_respects_typed_runtime_holding() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        (root / "core").mkdir(parents=True, exist_ok=True)
        (root / "core/ROUTER.md").write_text("router", encoding="utf-8")

        (root / "modules/principles").mkdir(parents=True, exist_ok=True)
        (root / "modules/principles/MODULE.md").write_text("principles module", encoding="utf-8")

        _write_jsonl(
            root / "modules/decision/logs/learning_candidate_promotions.jsonl",
            "learning_candidate_promotions",
            ["id", "created_at", "status", "candidate_ref", "promotion_target"],
            [
                {
                    "id": "lp_principle",
                    "created_at": "2020-03-07T00:00:00Z",
                    "status": "active",
                    "candidate_ref": "lc_principle",
                    "promotion_target": "principle",
                }
            ],
        )
        _write_jsonl(
            root / "modules/principles/logs/principle_candidates.jsonl",
            "principle_candidates",
            ["id", "created_at", "status", "candidate_ref", "candidate_type", "title", "statement", "approval_ref", "promotion_ref"],
            [
                {
                    "id": "prc_ready",
                    "created_at": "2020-03-07T00:05:00Z",
                    "status": "active",
                    "candidate_ref": "lc_principle",
                    "candidate_type": "principle",
                    "title": "Hold principle",
                    "statement": "This should not auto-enter runtime.",
                    "approval_ref": "la_principle",
                    "promotion_ref": "lp_principle",
                }
            ],
        )

        bundle = load_context_bundle(
            root,
            module="principles",
            max_chars=10000,
            skill_path=None,
        )
        paths = [f["path"] for f in bundle["files"]]
        assert "orchestrator://runtime_eligible_artifacts" not in paths

        eligibility_path = root / "modules/decision/logs/runtime_eligibility.jsonl"
        assert eligibility_path.exists()
        eligibility_lines = eligibility_path.read_text(encoding="utf-8").splitlines()
        assert any('"eligibility_status": "holding"' in line for line in eligibility_lines[1:])


def test_load_context_bundle_includes_explicitly_referenced_accepted_content_direction() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        (root / "core").mkdir(parents=True, exist_ok=True)
        (root / "core/ROUTER.md").write_text("router", encoding="utf-8")

        (root / "modules/content").mkdir(parents=True, exist_ok=True)
        (root / "modules/content/MODULE.md").write_text("content module", encoding="utf-8")
        (root / "modules/content/skills").mkdir(parents=True, exist_ok=True)
        (root / "modules/content/skills/write_after_meal_story.md").write_text("# Skill", encoding="utf-8")

        _write_jsonl(
            root / "orchestrator/logs/suggestions.jsonl",
            "suggestions",
            [
                "id",
                "created_at",
                "status",
                "module",
                "proposal_kind",
                "proposal_title",
                "proposal_summary",
                "proposal_statement",
                "recommendation_path",
            ],
            [
                {
                    "id": "sg_content_1",
                    "created_at": "2026-03-14T10:00:00Z",
                    "status": "active",
                    "module": "content",
                    "proposal_kind": "content_direction_proposal",
                    "proposal_title": "Content direction proposal: BTC as behavior-shift story",
                    "proposal_summary": "Frame BTC regime as behavior shift, not prediction.",
                    "proposal_statement": "- Frame BTC regime as a behavior-shift story.\n- Lead with one concrete contrast.\n- Avoid prediction-first framing.",
                    "recommendation_path": "modules/content/outputs/content_direction_20260314_btc.md",
                }
            ],
        )
        _write_jsonl(
            root / "orchestrator/logs/owner_verdicts.jsonl",
            "owner_verdicts",
            ["id", "created_at", "status", "suggestion_ref", "verdict", "owner_note", "correction_ref", "source_refs"],
            [
                {
                    "id": "ov_content_1",
                    "created_at": "2026-03-14T10:05:00Z",
                    "status": "active",
                    "suggestion_ref": "sg_content_1",
                    "verdict": "accept",
                    "owner_note": "Use this framing for the draft.",
                    "correction_ref": None,
                    "source_refs": ["sg_content_1"],
                }
            ],
        )

        bundle = load_context_bundle(
            root,
            module="content",
            max_chars=10000,
            skill_path="modules/content/skills/write_after_meal_story.md",
            intent_text="write an after-meal story about BTC market regime\nAccepted content direction proposal ref: sg_content_1",
        )
        paths = [f["path"] for f in bundle["files"]]
        context_path = "orchestrator://accepted_content_direction/sg_content_1"
        assert context_path in paths
        context_file = next(f for f in bundle["files"] if f["path"] == context_path)
        assert "Effective Direction" in context_file["content"]
        assert "behavior-shift story" in context_file["content"]
        assert "Use this framing for the draft." in context_file["content"]


def test_load_context_bundle_uses_modified_content_direction_replacement_judgment() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        (root / "core").mkdir(parents=True, exist_ok=True)
        (root / "core/ROUTER.md").write_text("router", encoding="utf-8")

        (root / "modules/content").mkdir(parents=True, exist_ok=True)
        (root / "modules/content/MODULE.md").write_text("content module", encoding="utf-8")
        (root / "modules/content/skills").mkdir(parents=True, exist_ok=True)
        (root / "modules/content/skills/write_after_meal_story.md").write_text("# Skill", encoding="utf-8")

        _write_jsonl(
            root / "orchestrator/logs/suggestions.jsonl",
            "suggestions",
            [
                "id",
                "created_at",
                "status",
                "module",
                "proposal_kind",
                "proposal_statement",
            ],
            [
                {
                    "id": "sg_content_2",
                    "created_at": "2026-03-14T11:00:00Z",
                    "status": "active",
                    "module": "content",
                    "proposal_kind": "content_direction_proposal",
                    "proposal_statement": "- Old framing that should be replaced.",
                }
            ],
        )
        _write_jsonl(
            root / "orchestrator/logs/owner_verdicts.jsonl",
            "owner_verdicts",
            ["id", "created_at", "status", "suggestion_ref", "verdict", "owner_note", "correction_ref", "source_refs"],
            [
                {
                    "id": "ov_content_2",
                    "created_at": "2026-03-14T11:05:00Z",
                    "status": "active",
                    "suggestion_ref": "sg_content_2",
                    "verdict": "modify",
                    "owner_note": "Use the rewritten framing instead.",
                    "correction_ref": "oc_content_2",
                    "source_refs": ["sg_content_2"],
                }
            ],
        )
        _write_jsonl(
            root / "orchestrator/logs/owner_corrections.jsonl",
            "owner_corrections",
            [
                "id",
                "created_at",
                "status",
                "suggestion_ref",
                "verdict_ref",
                "target_layer",
                "replacement_judgment",
                "unlike_me_reason",
                "source_refs",
            ],
            [
                {
                    "id": "oc_content_2",
                    "created_at": "2026-03-14T11:06:00Z",
                    "status": "active",
                    "suggestion_ref": "sg_content_2",
                    "verdict_ref": "ov_content_2",
                    "target_layer": "content",
                    "replacement_judgment": "- Frame BTC regime as a behavior/adaptation story, not a market-call story.",
                    "unlike_me_reason": "The original version sounded too prediction-heavy.",
                    "source_refs": ["sg_content_2", "ov_content_2"],
                }
            ],
        )

        bundle = load_context_bundle(
            root,
            module="content",
            max_chars=10000,
            skill_path="modules/content/skills/write_after_meal_story.md",
            intent_text="write an after-meal story about BTC market regime\n内容方向提案 ref：sg_content_2",
        )
        context_path = "orchestrator://accepted_content_direction/sg_content_2"
        context_file = next(f for f in bundle["files"] if f["path"] == context_path)
        assert "behavior/adaptation story" in context_file["content"]
        assert "prediction-heavy" in context_file["content"]
        assert "Old framing that should be replaced." not in context_file["content"]


def test_load_context_bundle_ignores_unaccepted_content_direction_reference() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        (root / "core").mkdir(parents=True, exist_ok=True)
        (root / "core/ROUTER.md").write_text("router", encoding="utf-8")

        (root / "modules/content").mkdir(parents=True, exist_ok=True)
        (root / "modules/content/MODULE.md").write_text("content module", encoding="utf-8")
        (root / "modules/content/skills").mkdir(parents=True, exist_ok=True)
        (root / "modules/content/skills/write_after_meal_story.md").write_text("# Skill", encoding="utf-8")

        _write_jsonl(
            root / "orchestrator/logs/suggestions.jsonl",
            "suggestions",
            ["id", "created_at", "status", "module", "proposal_kind", "proposal_statement"],
            [
                {
                    "id": "sg_content_3",
                    "created_at": "2026-03-14T12:00:00Z",
                    "status": "active",
                    "module": "content",
                    "proposal_kind": "content_direction_proposal",
                    "proposal_statement": "- Unaccepted direction.",
                }
            ],
        )
        _write_jsonl(
            root / "orchestrator/logs/owner_verdicts.jsonl",
            "owner_verdicts",
            ["id", "created_at", "status", "suggestion_ref", "verdict", "owner_note", "correction_ref", "source_refs"],
            [
                {
                    "id": "ov_content_3",
                    "created_at": "2026-03-14T12:05:00Z",
                    "status": "active",
                    "suggestion_ref": "sg_content_3",
                    "verdict": "reject",
                    "owner_note": "Do not use this angle.",
                    "correction_ref": None,
                    "source_refs": ["sg_content_3"],
                }
            ],
        )

        bundle = load_context_bundle(
            root,
            module="content",
            max_chars=10000,
            skill_path="modules/content/skills/write_after_meal_story.md",
            intent_text="write an after-meal story\nAccepted content direction proposal ref: sg_content_3",
        )
        paths = [f["path"] for f in bundle["files"]]
        assert "orchestrator://accepted_content_direction/sg_content_3" not in paths


def test_load_context_bundle_does_not_inject_direction_context_into_direction_skill() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        (root / "core").mkdir(parents=True, exist_ok=True)
        (root / "core/ROUTER.md").write_text("router", encoding="utf-8")

        (root / "modules/content").mkdir(parents=True, exist_ok=True)
        (root / "modules/content/MODULE.md").write_text("content module", encoding="utf-8")
        (root / "modules/content/skills").mkdir(parents=True, exist_ok=True)
        (root / "modules/content/skills/propose_content_direction.md").write_text("# Skill", encoding="utf-8")

        _write_jsonl(
            root / "orchestrator/logs/suggestions.jsonl",
            "suggestions",
            ["id", "created_at", "status", "module", "proposal_kind", "proposal_statement"],
            [
                {
                    "id": "sg_content_4",
                    "created_at": "2026-03-14T13:00:00Z",
                    "status": "active",
                    "module": "content",
                    "proposal_kind": "content_direction_proposal",
                    "proposal_statement": "- Existing accepted direction.",
                }
            ],
        )
        _write_jsonl(
            root / "orchestrator/logs/owner_verdicts.jsonl",
            "owner_verdicts",
            ["id", "created_at", "status", "suggestion_ref", "verdict", "owner_note", "correction_ref", "source_refs"],
            [
                {
                    "id": "ov_content_4",
                    "created_at": "2026-03-14T13:05:00Z",
                    "status": "active",
                    "suggestion_ref": "sg_content_4",
                    "verdict": "accept",
                    "owner_note": "Accepted.",
                    "correction_ref": None,
                    "source_refs": ["sg_content_4"],
                }
            ],
        )

        bundle = load_context_bundle(
            root,
            module="content",
            max_chars=10000,
            skill_path="modules/content/skills/propose_content_direction.md",
            intent_text="propose a content direction\nAccepted content direction proposal ref: sg_content_4",
        )
        paths = [f["path"] for f in bundle["files"]]
        assert "orchestrator://accepted_content_direction/sg_content_4" not in paths


def test_load_context_bundle_includes_explicitly_enabled_principle_runtime() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        (root / "core").mkdir(parents=True, exist_ok=True)
        (root / "core/ROUTER.md").write_text("router", encoding="utf-8")

        (root / "modules/principles").mkdir(parents=True, exist_ok=True)
        (root / "modules/principles/MODULE.md").write_text("principles module", encoding="utf-8")

        _write_jsonl(
            root / "modules/decision/logs/learning_candidate_promotions.jsonl",
            "learning_candidate_promotions",
            ["id", "created_at", "status", "candidate_ref", "promotion_target", "approval_ref"],
            [
                {
                    "id": "lp_principle",
                    "created_at": "2020-03-07T00:00:00Z",
                    "status": "active",
                    "candidate_ref": "lc_principle",
                    "promotion_target": "principle",
                    "approval_ref": "la_principle",
                }
            ],
        )
        _write_jsonl(
            root / "modules/principles/logs/principle_candidates.jsonl",
            "principle_candidates",
            ["id", "created_at", "status", "candidate_ref", "candidate_type", "title", "statement", "approval_ref", "promotion_ref"],
            [
                {
                    "id": "prc_ready",
                    "created_at": "2020-03-07T00:05:00Z",
                    "status": "active",
                    "candidate_ref": "lc_principle",
                    "candidate_type": "principle",
                    "title": "Enabled principle",
                    "statement": "This should enter runtime only after explicit eligibility.",
                    "approval_ref": "la_principle",
                    "promotion_ref": "lp_principle",
                }
            ],
        )
        _write_jsonl(
            root / "modules/decision/logs/runtime_eligibility.jsonl",
            "runtime_eligibility",
            [
                "id",
                "created_at",
                "status",
                "artifact_ref",
                "artifact_type",
                "candidate_ref",
                "approval_ref",
                "promotion_ref",
                "eligibility_status",
                "maturity_hours",
                "scope_modules",
                "autonomy_ceiling",
            ],
            [
                {
                    "id": "re_principle",
                    "created_at": "2020-03-07T00:06:00Z",
                    "status": "active",
                    "artifact_ref": "prc_ready",
                    "artifact_type": "principle",
                    "candidate_ref": "lc_principle",
                    "approval_ref": "la_principle",
                    "promotion_ref": "lp_principle",
                    "eligibility_status": "eligible",
                    "maturity_hours": 24,
                    "scope_modules": ["principles"],
                    "autonomy_ceiling": "review_required",
                }
            ],
        )

        bundle = load_context_bundle(
            root,
            module="principles",
            max_chars=10000,
            skill_path=None,
        )
        paths = [f["path"] for f in bundle["files"]]
        assert "orchestrator://runtime_eligible_artifacts" in paths
        runtime_block = next(f for f in bundle["files"] if f["path"] == "orchestrator://runtime_eligible_artifacts")
        assert "Enabled principle" in runtime_block["content"]
        assert any(item["artifact_ref"] == "prc_ready" for item in bundle["runtime_influences"])
