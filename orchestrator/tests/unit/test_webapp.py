from __future__ import annotations

import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from webapp import (
    api_action,
    api_get_settings,
    api_inspect,
    api_output,
    api_output_meta,
    api_run,
    api_status,
    api_suggestion,
    api_update_settings,
)


def _copy_repo_subset(dst_root: Path) -> Path:
    src_root = Path(__file__).resolve().parents[3]

    for rel in ["core", "modules", "routines", "orchestrator/config", "orchestrator/logs"]:
        src = src_root / rel
        dst = dst_root / rel
        shutil.copytree(src, dst, dirs_exist_ok=True)

    return dst_root


def test_api_status_lists_modules() -> None:
    with TemporaryDirectory() as td:
        root = _copy_repo_subset(Path(td))
        data = api_status(root)

        assert data["ok"] is True
        assert "content" in data["modules"]
        assert "decision" in data["modules"]
        assert isinstance(data["cognition_cards"], list)
        assert isinstance(data["learning_candidates"], list)
        assert isinstance(data["candidate_pipeline_summary"], dict)
        assert isinstance(data["candidate_pipeline_trend"], dict)


def test_api_status_reports_env_api_key(monkeypatch) -> None:
    with TemporaryDirectory() as td:
        root = _copy_repo_subset(Path(td))
        monkeypatch.setenv("OPENAI_API_KEY", "sk-from-env")
        data = api_status(root)
        assert data["has_openai_api_key"] is True


def test_api_settings_roundtrip() -> None:
    with TemporaryDirectory() as td:
        root = _copy_repo_subset(Path(td))
        initial = api_get_settings(root)
        assert initial["ok"] is True
        assert initial["default_provider"] == "handoff"
        assert initial["has_openai_api_key"] is False
        assert "openai_api_key" not in initial

        updated = api_update_settings(
            root,
            {
                "openai_api_key": "sk-test",
                "default_provider": "dry-run",
                "task_model": "gpt-4.1-mini",
                "routing_model": "gpt-4.1-nano",
            },
        )
        assert updated["ok"] is True
        assert updated["default_provider"] == "dry-run"
        assert updated["has_openai_api_key"] is True
        assert "openai_api_key" not in updated

        # Blank key field should keep existing saved key.
        updated2 = api_update_settings(root, {"default_provider": "handoff"})
        assert updated2["default_provider"] == "handoff"
        assert updated2["has_openai_api_key"] is True

        status = api_status(root)
        assert status["default_provider"] == "handoff"
        assert status["has_openai_api_key"] is True


def test_api_inspect_and_run_writes_output() -> None:
    with TemporaryDirectory() as td:
        root = _copy_repo_subset(Path(td))

        inspect_payload = {
            "task": "run weekly decision review",
            "provider": "dry-run",
            "with_retrieval": False,
        }
        inspect_result = api_inspect(root, inspect_payload)

        assert inspect_result["ok"] is True
        assert inspect_result["module"] == "decision"
        reason = inspect_result["route"]["reason"]
        assert reason in {
            "manifest_keyword_match",
            "routes_keyword_match",
            "forced_module",
            "fallback_default",
        } or reason.startswith("llm_")
        assert inspect_result["plan"]["skill"].endswith(".md")
        assert len(inspect_result["loaded_files"]) >= 2
        assert isinstance(inspect_result["debug_prompts"], list)
        assert isinstance(inspect_result["debug_sections"], list)

        run_result = api_run(root, inspect_payload)
        assert run_result["ok"] is True
        assert run_result["output_path"].endswith(".md")
        assert len(run_result["output_hash"]) == 64
        assert run_result["suggestion_id"].startswith("sg_")
        assert isinstance(run_result["output_preview"], str)
        assert len(run_result["output_preview"]) > 0
        assert isinstance(run_result["debug_prompts"], list)
        assert isinstance(run_result["debug_sections"], list)
        assert (root / run_result["output_path"]).exists()

        output_payload = api_output(root, run_result["output_path"])
        assert output_payload["ok"] is True
        assert output_payload["path"] == run_result["output_path"]
        assert "Execution Packet" in output_payload["content"]

        output_meta = api_output_meta(root, run_result["output_path"], "gpt-4.1-mini")
        assert output_meta["ok"] is True
        assert output_meta["path"] == run_result["output_path"]
        assert isinstance(output_meta["prompt_tokens"], int)
        assert output_meta["prompt_tokens"] > 0
        assert output_meta["count_method"] in {"tiktoken", "estimate_utf8"}

        runs_path = root / "orchestrator/logs/runs.jsonl"
        run_lines = runs_path.read_text(encoding="utf-8").splitlines()
        run_record = json.loads(run_lines[-1])
        assert "|s=" in str(run_record["route_reason"])
        assert run_record["object_type"] == "system"
        assert run_record["proposal_target"] is None

        suggestions_path = root / "orchestrator/logs/suggestions.jsonl"
        suggestion_lines = suggestions_path.read_text(encoding="utf-8").splitlines()
        suggestion_record = json.loads(suggestion_lines[-1])
        assert suggestion_record["id"] == run_result["suggestion_id"]
        assert suggestion_record["run_ref"] == run_record["id"]
        assert suggestion_record["object_type"] == "system"
        assert suggestion_record["proposal_target"] is None
        assert isinstance(suggestion_record["invoked_rules"], list)
        assert isinstance(suggestion_record["invoked_traits"], list)
        assert any(str(item).startswith("route_reason:") for item in suggestion_record["invoked_rules"])
        assert any(str(item).startswith("plan_skill:") for item in suggestion_record["invoked_rules"])

        suggestion_detail = api_suggestion(root, run_result["suggestion_id"])
        assert suggestion_detail["ok"] is True
        assert suggestion_detail["suggestion"]["id"] == run_result["suggestion_id"]
        assert suggestion_detail["suggestion"]["run_ref"] == run_record["id"]
        assert isinstance(suggestion_detail["suggestion"]["invoked_rules"], list)
        assert isinstance(suggestion_detail["suggestion"]["invoked_traits"], list)
        assert suggestion_detail["run"] is not None
        assert suggestion_detail["run"]["id"] == run_record["id"]
        assert suggestion_detail["output_path"] == run_result["output_path"]
        assert isinstance(suggestion_detail["output_preview"], str)
        assert len(suggestion_detail["output_preview"]) > 0


def test_api_suggestion_rejects_missing_or_unknown_id() -> None:
    with TemporaryDirectory() as td:
        root = _copy_repo_subset(Path(td))
        with pytest.raises(ValueError):
            api_suggestion(root, "")
        with pytest.raises(ValueError):
            api_suggestion(root, "sg_missing")


def test_api_action_validate_metrics_and_schedule() -> None:
    with TemporaryDirectory() as td:
        root = _copy_repo_subset(Path(td))

        validate_result = api_action(root, {"action": "validate", "strict": True})
        assert validate_result["action"] == "validate"
        assert validate_result["status"] in {"pass", "warn", "fail"}

        metrics_result = api_action(root, {"action": "metrics", "window_days": 7})
        assert metrics_result["ok"] is True
        assert metrics_result["action"] == "metrics"
        assert isinstance(metrics_result["output_preview"], str)
        assert "cognitive_trend" in metrics_result
        assert isinstance(metrics_result["cognition_cards"], list)
        assert (root / metrics_result["output_path"]).exists()

        owner_result = api_action(root, {"action": "owner_report", "window_days": 7})
        assert owner_result["ok"] is True
        assert owner_result["action"] == "owner_report"
        assert "source_artifacts" in owner_result
        assert "owner_todos" in owner_result["source_artifacts"]
        assert "candidate_pipeline_summary" in owner_result
        assert "candidate_pipeline_trend" in owner_result
        assert "owner_todo_queue" in owner_result

        owner_todos_log = root / "modules/decision/logs/owner_todos.jsonl"
        owner_todos_log.write_text(
            "\n".join(
                [
                    '{"_schema":{"name":"owner_todos","version":"1.0","fields":["id","created_at","status","metric","priority","reason","action","owner_report_ref","todo_signature","resolution_of","note"],"notes":"append-only"}}',
                    '{"id":"ot_20260307_001","created_at":"2026-03-07T10:00:00Z","status":"active","metric":"precommit_coverage","priority":"red","reason":"two_week_fail_precommit_coverage","action":"Enforce guardrail_check_id for every high-risk decision next week.","owner_report_ref":"or_20260307_001","todo_signature":"precommit_coverage|Enforce guardrail_check_id for every high-risk decision next week.","resolution_of":null,"note":null}',
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        resolved = api_action(
            root,
            {
                "action": "resolve_owner_todo",
                "todo_id": "ot_20260307_001",
                "note": "Guardrail check requirement applied.",
            },
        )
        assert resolved["ok"] is True
        assert resolved["resolved_todo"] == "ot_20260307_001"
        assert isinstance(resolved["owner_todos"], list)

        with pytest.raises(ValueError):
            api_action(
                root,
                {
                    "action": "resolve_owner_todo",
                    "todo_id": "ot_missing",
                    "note": "test",
                },
            )

        schedule_result = api_action(
            root,
            {
                "action": "schedule_cycle",
                "cycle": "weekly",
                "provider": "dry-run",
                "limit": 1,
                "no_owner_report": True,
            },
        )
        assert schedule_result["ok"] is True
        assert schedule_result["action"] == "schedule_cycle"
        assert schedule_result["routine_count"] == 1
        assert len(schedule_result["runs"]) == 1
        assert isinstance(schedule_result["runs"][0]["output_preview"], str)
        assert (root / schedule_result["runs"][0]["output_path"]).exists()

        events_path = root / "modules/memory/logs/memory_events.jsonl"
        insights_path = root / "modules/memory/logs/memory_insights.jsonl"
        events_before = len(events_path.read_text(encoding="utf-8").splitlines())
        insights_before = len(insights_path.read_text(encoding="utf-8").splitlines())

        ingest_result = api_action(
            root,
            {
                "action": "ingest_learning",
                "task": "Reverse thinking: when A/B fail, find option C. Align incentives with motives. Check value chain.",
                "source_type": "video",
                "max_points": 6,
                "confidence": 8,
                "tags": ["web_test"],
            },
        )
        assert ingest_result["ok"] is True
        assert ingest_result["action"] == "ingest_learning"
        assert ingest_result["appended_events"] == 1
        assert ingest_result["appended_insights"] == 1
        assert len(ingest_result["record_ids"]) == 2

        events_after = len(events_path.read_text(encoding="utf-8").splitlines())
        insights_after = len(insights_path.read_text(encoding="utf-8").splitlines())
        assert events_after == events_before + 1
        assert insights_after == insights_before + 1

        packet_result = api_action(
            root,
            {
                "action": "learning_handoff_packet",
                "source_ref": "https://www.youtube.com/watch?v=abc123",
                "title": "Interview ABC",
                "source_type": "video",
            },
        )
        assert packet_result["ok"] is True
        assert packet_result["action"] == "learning_handoff_packet"
        assert "candidate_artifacts" in packet_result["packet_text"]

        handoff_response = json.dumps(
            {
                "source": {
                    "title": "Interview ABC",
                    "url": "https://www.youtube.com/watch?v=abc123",
                    "source_type": "video",
                },
                "summary": "Extract stable judgment structures from long interview.",
                "key_points": [
                    "Always define downside and invalidation before commitment.",
                    "Repeated mismatch is schema pressure.",
                ],
                "candidate_artifacts": {
                    "insights": [
                        {
                            "title": "Downside-first",
                            "statement": "High-risk commitments require downside + invalidation pair.",
                            "evidence": ["Interview examples"],
                            "confidence": 0.8,
                        }
                    ],
                    "rules": [
                        {
                            "title": "Mismatch loop",
                            "rule": "If mismatch repeats, trigger schema review within 48h.",
                            "when_to_apply": "After second repeated contradiction",
                            "evidence": ["Multiple stories from source"],
                            "confidence": 0.7,
                        }
                    ],
                },
            }
        )
        handoff_import = api_action(
            root,
            {
                "action": "learning_handoff_import",
                "source_ref": "https://www.youtube.com/watch?v=abc123",
                "response_text": handoff_response,
                "source_type": "video",
                "confidence": 8,
                "tags": ["web_test"],
            },
        )
        assert handoff_import["ok"] is True
        assert handoff_import["action"] == "learning_handoff_import"
        assert handoff_import["candidate_total"] == 2
        assert handoff_import["import_record_id"].startswith("li_")
        assert len(handoff_import["candidate_record_ids"]) == 2
        assert isinstance(handoff_import["learning_candidates"], list)
        assert len(handoff_import["learning_candidates"]) >= 1
        assert isinstance(handoff_import["candidate_pipeline_summary"], dict)
        assert isinstance(handoff_import["candidate_pipeline_trend"], dict)

        review_result = api_action(
            root,
            {
                "action": "review_learning_candidate",
                "candidate_id": handoff_import["candidate_record_ids"][0],
                "verdict": "accept",
                "owner_note": "Aligned and accepted.",
            },
        )
        assert review_result["ok"] is True
        assert review_result["action"] == "review_learning_candidate"
        assert review_result["verdict"] == "accept"
        assert review_result["candidate_ref"] == handoff_import["candidate_record_ids"][0]
        assert isinstance(review_result["learning_candidates"], list)
        assert isinstance(review_result["candidate_pipeline_summary"], dict)
        assert isinstance(review_result["candidate_pipeline_trend"], dict)

        promote_result = api_action(
            root,
            {
                "action": "promote_learning_candidate",
                "candidate_id": handoff_import["candidate_record_ids"][0],
                "approval_note": "Approved for promotion.",
            },
        )
        assert promote_result["ok"] is True
        assert promote_result["action"] == "promote_learning_candidate"
        assert promote_result["candidate_ref"] == handoff_import["candidate_record_ids"][0]
        assert promote_result["approval_record_id"].startswith("la_")
        assert promote_result["promotion_record_id"].startswith("lp_")
        assert promote_result["module_candidate_ref"].startswith("ic_")
        assert promote_result["module_candidate_path"] == "modules/memory/logs/insight_candidates.jsonl"
        assert isinstance(promote_result["learning_candidates"], list)
        assert isinstance(promote_result["candidate_pipeline_summary"], dict)
        assert isinstance(promote_result["candidate_pipeline_trend"], dict)

        diseq_result = api_action(
            root,
            {
                "action": "detect_disequilibrium",
                "task": "invest risk model",
                "window_days": 30,
            },
        )
        assert diseq_result["ok"] is True
        assert diseq_result["action"] == "detect_disequilibrium"
        assert isinstance(diseq_result["tension_score"], int)
        assert (root / diseq_result["output_path"]).exists()

        timeline_result = api_action(
            root,
            {
                "action": "cognition_timeline",
                "task": "invest risk model",
                "window_days": 180,
            },
        )
        assert timeline_result["ok"] is True
        assert timeline_result["action"] == "cognition_timeline"
        assert isinstance(timeline_result["event_count"], int)
        assert (root / timeline_result["output_path"]).exists()


def test_api_output_rejects_non_output_and_escape_paths() -> None:
    with TemporaryDirectory() as td:
        root = _copy_repo_subset(Path(td))
        with pytest.raises(ValueError):
            api_output(root, "core/ROUTER.md")
        with pytest.raises(ValueError):
            api_output(root, "../README.md")
        with pytest.raises(ValueError):
            api_output(root, "modules/decision/outputs/../../../README.md")
        with pytest.raises(ValueError):
            api_output_meta(root, "modules/decision/outputs/../../../README.md")


def test_api_run_rejects_unknown_module() -> None:
    with TemporaryDirectory() as td:
        root = _copy_repo_subset(Path(td))
        with pytest.raises(ValueError):
            api_run(
                root,
                {
                    "task": "do something",
                    "module": "nonexistent_module",
                    "provider": "dry-run",
                },
            )
