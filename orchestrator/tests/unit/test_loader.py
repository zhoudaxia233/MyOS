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
        assert "orchestrator://promoted_candidates_ready" in paths

        promoted = next(f for f in files if f["path"] == "orchestrator://promoted_candidates_ready")
        content = promoted["content"]
        assert "Ready rule" in content
        assert "Cooling rule" not in content


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
        promoted = next(f for f in files if f["path"] == "orchestrator://promoted_candidates_ready")
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
        fallback_promoted = next(f for f in fallback_files if f["path"] == "orchestrator://promoted_candidates_ready")
        fallback_content = fallback_promoted["content"]
        assert "intent_filter: recent_fallback" in fallback_content
        assert "Admin cleanup" in fallback_content
