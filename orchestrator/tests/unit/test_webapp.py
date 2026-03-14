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


def _write_jsonl(path: Path, schema_name: str, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    schema = {"_schema": {"name": schema_name, "version": "1.0", "fields": fields, "notes": "append-only"}}
    with path.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(schema) + "\n")
        for row in rows:
            handle.write(json.dumps(row) + "\n")


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
        assert isinstance(data["recent_runtime_influence_drift"], dict)
        assert isinstance(data["suggestion_review_queue"], dict)
        assert isinstance(data["suggestion_review_summary"], dict)
        assert isinstance(data["suggestion_review_trend"], dict)
        assert "ui_language" in data
        assert "has_deepseek_api_key" in data


def test_api_status_reports_env_api_key(monkeypatch) -> None:
    with TemporaryDirectory() as td:
        root = _copy_repo_subset(Path(td))
        monkeypatch.setenv("OPENAI_API_KEY", "sk-from-env")
        data = api_status(root)
        assert data["has_openai_api_key"] is True


def test_api_settings_roundtrip(monkeypatch) -> None:
    with TemporaryDirectory() as td:
        root = _copy_repo_subset(Path(td))
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        initial = api_get_settings(root)
        assert initial["ok"] is True
        assert initial["default_provider"] == "handoff"
        assert initial["has_openai_api_key"] is False
        assert initial["has_deepseek_api_key"] is False
        assert initial["ui_language"] in {"zh", "en"}
        assert "openai_api_key" not in initial

        updated = api_update_settings(
            root,
            {
                "openai_api_key": "sk-test",
                "deepseek_api_key": "sk-deepseek",
                "default_provider": "dry-run",
                "openai_model": "gpt-4.1-mini",
                "openai_base_url": "https://api.openai.com/v1",
                "deepseek_model": "deepseek-chat",
                "deepseek_base_url": "https://api.deepseek.com/v1",
                "routing_model": "gpt-4.1-nano",
                "decision_provider": "deepseek",
                "decision_model": "deepseek-chat",
                "ui_language": "en",
            },
        )
        assert updated["ok"] is True
        assert updated["default_provider"] == "dry-run"
        assert updated["has_openai_api_key"] is True
        assert updated["has_deepseek_api_key"] is True
        assert updated["openai_model"] == "gpt-4.1-mini"
        assert updated["openai_base_url"] == "https://api.openai.com/v1"
        assert updated["deepseek_model"] == "deepseek-chat"
        assert updated["decision_provider"] == "deepseek"
        assert updated["decision_model"] == "deepseek-chat"
        assert updated["ui_language"] == "en"
        assert "openai_api_key" not in updated

        # Blank key field should keep existing saved key.
        updated2 = api_update_settings(root, {"default_provider": "handoff"})
        assert updated2["default_provider"] == "handoff"
        assert updated2["has_openai_api_key"] is True

        status = api_status(root)
        assert status["default_provider"] == "handoff"
        assert status["has_openai_api_key"] is True
        assert status["has_deepseek_api_key"] is True


def test_api_run_uses_module_profile_provider_when_provider_is_auto() -> None:
    with TemporaryDirectory() as td:
        root = _copy_repo_subset(Path(td))
        api_update_settings(
            root,
            {
                "default_provider": "handoff",
                "decision_provider": "dry-run",
                "decision_model": "custom-decision-model",
            },
        )
        run_result = api_run(
            root,
            {
                "task": "run weekly decision review",
                "provider": "auto",
                "model": "",
                "with_retrieval": False,
            },
        )
        assert run_result["ok"] is True
        assert run_result["module"] == "decision"
        assert run_result["provider"] == "dry-run"


def test_api_status_uses_deepseek_default_model_when_provider_is_deepseek() -> None:
    with TemporaryDirectory() as td:
        root = _copy_repo_subset(Path(td))
        api_update_settings(
            root,
            {
                "default_provider": "deepseek",
                "deepseek_model": "deepseek-chat",
                "ui_language": "zh",
            },
        )
        data = api_status(root)
        assert data["default_provider"] == "deepseek"
        assert data["default_model"] == "deepseek-chat"
        assert data["ui_language"] == "zh"


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
        assert isinstance(inspect_result["runtime_influences"], list)
        assert isinstance(inspect_result["recent_runtime_influence_drift"], dict)

        run_result = api_run(root, inspect_payload)
        assert run_result["ok"] is True
        assert run_result["output_path"].endswith(".md")
        assert len(run_result["output_hash"]) == 64
        assert run_result["suggestion_id"].startswith("sg_")
        assert isinstance(run_result["output_preview"], str)
        assert len(run_result["output_preview"]) > 0
        assert isinstance(run_result["debug_prompts"], list)
        assert isinstance(run_result["debug_sections"], list)
        assert isinstance(run_result["runtime_influences"], list)
        assert isinstance(run_result["recent_runtime_influence_drift"], dict)
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
        assert isinstance(run_record["runtime_influences"], list)


def test_api_suggestion_includes_recent_runtime_influence_drift() -> None:
    with TemporaryDirectory() as td:
        root = _copy_repo_subset(Path(td))
        run_result = api_run(
            root,
            {
                "task": "run weekly decision review",
                "provider": "dry-run",
                "with_retrieval": False,
            },
        )

        suggestion_payload = api_suggestion(root, run_result["suggestion_id"])
        assert suggestion_payload["ok"] is True
        assert isinstance(suggestion_payload["recent_runtime_influence_drift"], dict)

        runs_path = root / "orchestrator/logs/runs.jsonl"
        run_lines = runs_path.read_text(encoding="utf-8").splitlines()
        run_record = json.loads(run_lines[-1])
        suggestions_path = root / "orchestrator/logs/suggestions.jsonl"
        suggestion_lines = suggestions_path.read_text(encoding="utf-8").splitlines()
        suggestion_record = json.loads(suggestion_lines[-1])
        assert suggestion_record["id"] == run_result["suggestion_id"]
        assert suggestion_record["run_ref"] == run_record["id"]
        assert suggestion_record["object_type"] == "system"
        assert suggestion_record["proposal_target"] is None
        assert isinstance(suggestion_record["runtime_influences"], list)
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
        assert isinstance(suggestion_detail["suggestion"]["runtime_influences"], list)
        assert suggestion_detail["run"] is not None
        assert suggestion_detail["run"]["id"] == run_record["id"]
        assert isinstance(suggestion_detail["run"]["runtime_influences"], list)
        assert suggestion_detail["output_path"] == run_result["output_path"]
        assert isinstance(suggestion_detail["output_preview"], str)
        assert len(suggestion_detail["output_preview"]) > 0


def test_api_run_logs_runtime_influences_from_runtime_eligibility() -> None:
    with TemporaryDirectory() as td:
        root = _copy_repo_subset(Path(td))
        _write_jsonl(
            root / "modules/decision/logs/learning_candidate_promotions.jsonl",
            "learning_candidate_promotions",
            ["id", "created_at", "status", "candidate_ref", "promotion_target", "approval_ref"],
            [
                {
                    "id": "lp_runtime",
                    "created_at": "2020-03-07T00:00:00Z",
                    "status": "active",
                    "candidate_ref": "lc_runtime",
                    "promotion_target": "decision",
                    "approval_ref": "la_runtime",
                }
            ],
        )
        _write_jsonl(
            root / "modules/decision/logs/rule_candidates.jsonl",
            "rule_candidates",
            ["id", "created_at", "status", "candidate_ref", "candidate_type", "title", "statement", "approval_ref", "promotion_ref"],
            [
                {
                    "id": "rc_runtime",
                    "created_at": "2020-03-07T00:05:00Z",
                    "status": "active",
                    "candidate_ref": "lc_runtime",
                    "candidate_type": "rule",
                    "title": "Runtime review guard",
                    "statement": "Use a short review pass before irreversible decisions.",
                    "approval_ref": "la_runtime",
                    "promotion_ref": "lp_runtime",
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
                    "id": "re_runtime",
                    "created_at": "2020-03-07T00:06:00Z",
                    "status": "active",
                    "artifact_ref": "rc_runtime",
                    "artifact_type": "rule",
                    "candidate_ref": "lc_runtime",
                    "approval_ref": "la_runtime",
                    "promotion_ref": "lp_runtime",
                    "eligibility_status": "eligible",
                    "maturity_hours": 24,
                    "scope_modules": ["decision"],
                    "autonomy_ceiling": "suggest_only",
                }
            ],
        )

        run_result = api_run(
            root,
            {
                "task": "run weekly decision review",
                "provider": "dry-run",
                "with_retrieval": False,
            },
        )
        assert run_result["ok"] is True
        assert any(item["artifact_ref"] == "rc_runtime" for item in run_result["runtime_influences"])

        run_record = json.loads((root / "orchestrator/logs/runs.jsonl").read_text(encoding="utf-8").splitlines()[-1])
        suggestion_record = json.loads((root / "orchestrator/logs/suggestions.jsonl").read_text(encoding="utf-8").splitlines()[-1])
        assert any(item["artifact_ref"] == "rc_runtime" for item in run_record["runtime_influences"])
        assert any(item["artifact_ref"] == "rc_runtime" for item in suggestion_record["runtime_influences"])

        suggestion_detail = api_suggestion(root, run_result["suggestion_id"])
        assert any(item["artifact_ref"] == "rc_runtime" for item in suggestion_detail["suggestion"]["runtime_influences"])


def test_api_suggestion_rejects_missing_or_unknown_id() -> None:
    with TemporaryDirectory() as td:
        root = _copy_repo_subset(Path(td))
        with pytest.raises(ValueError):
            api_suggestion(root, "")
        with pytest.raises(ValueError):
            api_suggestion(root, "sg_missing")


def test_api_action_review_suggestion_writes_verdict_and_correction() -> None:
    with TemporaryDirectory() as td:
        root = _copy_repo_subset(Path(td))
        run_result = api_run(
            root,
            {
                "task": "run weekly decision review",
                "provider": "dry-run",
                "with_retrieval": False,
            },
        )
        suggestion_id = run_result["suggestion_id"]

        accept_result = api_action(
            root,
            {
                "action": "review_suggestion",
                "suggestion_id": suggestion_id,
                "verdict": "accept",
                "owner_note": "Aligned with current operating intent.",
            },
        )
        assert accept_result["ok"] is True
        assert accept_result["verdict"] == "accept"
        assert accept_result["verdict_record_id"].startswith("ov_")
        assert accept_result["correction_record_id"] is None
        assert isinstance(accept_result["suggestion_detail"], dict)

        accept_detail = api_suggestion(root, suggestion_id)
        assert accept_detail["owner_review"]["verdict"] is not None
        assert accept_detail["owner_review"]["verdict"]["id"] == accept_result["verdict_record_id"]
        assert accept_detail["owner_review"]["correction"] is None

        with pytest.raises(ValueError):
            api_action(
                root,
                {
                    "action": "review_suggestion",
                    "suggestion_id": suggestion_id,
                    "verdict": "modify",
                    "owner_note": "Needs refinement.",
                },
            )

        modify_result = api_action(
            root,
            {
                "action": "review_suggestion",
                "suggestion_id": suggestion_id,
                "verdict": "modify",
                "owner_note": "Direction good, framing should be tighter.",
                "replacement_judgment": "Use narrower scope and defer irreversible commitment.",
                "unlike_me_reason": "Current wording overcommits under uncertainty.",
                "correction_target_layer": "decision",
            },
        )
        assert modify_result["ok"] is True
        assert modify_result["verdict"] == "modify"
        assert modify_result["verdict_record_id"].startswith("ov_")
        assert modify_result["correction_record_id"].startswith("oc_")

        modify_detail = api_suggestion(root, suggestion_id)
        verdict_row = modify_detail["owner_review"]["verdict"]
        correction_row = modify_detail["owner_review"]["correction"]
        assert verdict_row is not None
        assert correction_row is not None
        assert verdict_row["id"] == modify_result["verdict_record_id"]
        assert correction_row["id"] == modify_result["correction_record_id"]
        assert correction_row["target_layer"] == "decision"
        assert correction_row["verdict_ref"] == modify_result["verdict_record_id"]


def test_api_status_suggestion_review_queue_tracks_pending_items() -> None:
    with TemporaryDirectory() as td:
        root = _copy_repo_subset(Path(td))
        run_a = api_run(
            root,
            {
                "task": "run weekly decision review",
                "provider": "dry-run",
                "with_retrieval": False,
            },
        )
        run_b = api_run(
            root,
            {
                "task": "draft a short market narrative",
                "provider": "dry-run",
                "with_retrieval": False,
            },
        )

        initial_status = api_status(root)
        queue = initial_status["suggestion_review_queue"]
        pending_ids = {row["id"] for row in queue["pending"]}
        assert queue["pending_total"] >= 2
        assert run_a["suggestion_id"] in pending_ids
        assert run_b["suggestion_id"] in pending_ids

        api_action(
            root,
            {
                "action": "review_suggestion",
                "suggestion_id": run_a["suggestion_id"],
                "verdict": "accept",
                "owner_note": "Aligned with current operating intent.",
            },
        )

        updated_status = api_status(root)
        updated_queue = updated_status["suggestion_review_queue"]
        updated_pending_ids = {row["id"] for row in updated_queue["pending"]}
        reviewed_items = updated_queue["recently_reviewed"]

        assert run_a["suggestion_id"] not in updated_pending_ids
        assert any(
            row["id"] == run_a["suggestion_id"] and row["owner_review"]["verdict"] == "accept"
            for row in reviewed_items
        )


def test_api_action_suggestion_review_summary_filters() -> None:
    with TemporaryDirectory() as td:
        root = _copy_repo_subset(Path(td))
        run_a = api_run(
            root,
            {
                "task": "decision review A",
                "provider": "dry-run",
                "with_retrieval": False,
            },
        )
        run_b = api_run(
            root,
            {
                "task": "decision review B",
                "provider": "dry-run",
                "with_retrieval": False,
            },
        )

        api_action(
            root,
            {
                "action": "review_suggestion",
                "suggestion_id": run_a["suggestion_id"],
                "verdict": "accept",
                "owner_note": "Accept for execution.",
            },
        )
        api_action(
            root,
            {
                "action": "review_suggestion",
                "suggestion_id": run_b["suggestion_id"],
                "verdict": "reject",
                "owner_note": "Not aligned with current context.",
            },
        )

        all_result = api_action(root, {"action": "suggestion_review_summary", "window_days": 30})
        assert all_result["ok"] is True
        assert all_result["action"] == "suggestion_review_summary"
        assert isinstance(all_result["suggestion_review_summary"], dict)
        assert isinstance(all_result["suggestion_review_trend"], dict)
        assert all_result["suggestion_review_summary"]["reviewed_total"] >= 2

        accept_result = api_action(
            root,
            {"action": "suggestion_review_summary", "window_days": 30, "verdict_filter": "accept"},
        )
        summary = accept_result["suggestion_review_summary"]
        assert summary["verdict_filter"] == "accept"
        assert summary["verdicts"]["accept"] >= 1
        assert summary["verdicts"]["reject"] == 0


def test_api_action_set_runtime_eligibility_updates_lightweight_learning_candidate_state() -> None:
    with TemporaryDirectory() as td:
        root = _copy_repo_subset(Path(td))
        import_result = api_action(
            root,
            {
                "action": "learning_handoff_import",
                "response_text": json.dumps(
                    {
                        "source": {"title": "P", "url": "u", "source_type": "video"},
                        "summary": "s",
                        "key_points": ["p"],
                        "candidate_artifacts": {"insights": [{"statement": "keep runtime hints lightweight"}]},
                    }
                ),
            },
        )
        candidate_id = import_result["candidate_record_ids"][0]
        api_action(
            root,
            {
                "action": "review_learning_candidate",
                "candidate_id": candidate_id,
                "verdict": "accept",
                "owner_note": "accept first",
            },
        )
        promote_result = api_action(
            root,
            {
                "action": "promote_learning_candidate",
                "candidate_id": candidate_id,
                "approval_note": "approved for promotion",
            },
        )
        assert promote_result["runtime_eligibility_status"] == "eligible"

        hold_result = api_action(
            root,
            {
                "action": "set_runtime_eligibility",
                "candidate_id": candidate_id,
                "eligibility_status": "holding",
                "change_note": "pause lightweight runtime influence",
            },
        )
        assert hold_result["ok"] is True
        assert hold_result["runtime_eligibility"]["runtime_eligibility_status"] == "holding"
        candidates = hold_result["learning_candidates"]
        matched = next(item for item in candidates if item["id"] == candidate_id)
        assert matched["runtime_eligibility_status"] == "holding"
        assert matched["runtime_change_note"] == "pause lightweight runtime influence"

        eligibility_result = api_action(
            root,
            {
                "action": "set_runtime_eligibility",
                "candidate_id": candidate_id,
                "eligibility_status": "eligible",
                "change_note": "allow insight to influence runtime explicitly",
            },
        )
        assert eligibility_result["ok"] is True
        assert eligibility_result["runtime_eligibility"]["runtime_eligibility_status"] == "eligible"
        candidates = eligibility_result["learning_candidates"]
        matched = next(item for item in candidates if item["id"] == candidate_id)
        assert matched["runtime_eligibility_status"] == "eligible"
        assert matched["runtime_change_note"] == "allow insight to influence runtime explicitly"


def test_api_action_blocks_generic_runtime_release_for_principle_candidate() -> None:
    with TemporaryDirectory() as td:
        root = _copy_repo_subset(Path(td))
        import_result = api_action(
            root,
            {
                "action": "learning_handoff_import",
                "response_text": json.dumps(
                    {
                        "source": {"title": "P", "url": "u", "source_type": "video"},
                        "summary": "s",
                        "key_points": ["p"],
                        "candidate_artifacts": {"principles": [{"statement": "protect downside first"}]},
                    }
                ),
            },
        )
        candidate_id = import_result["candidate_record_ids"][0]
        api_action(
            root,
            {
                "action": "review_learning_candidate",
                "candidate_id": candidate_id,
                "verdict": "accept",
                "owner_note": "accept first",
            },
        )
        promote_result = api_action(
            root,
            {
                "action": "promote_learning_candidate",
                "candidate_id": candidate_id,
                "approval_note": "approved for promotion",
            },
        )
        assert promote_result["runtime_eligibility_status"] == "holding"
        matched = next(item for item in promote_result["learning_candidates"] if item["id"] == candidate_id)
        assert matched["runtime_eligibility_status"] == "holding"
        assert "ratification" in str(matched.get("runtime_change_note") or "")

        with pytest.raises(ValueError) as excinfo:
            api_action(
                root,
                {
                    "action": "set_runtime_eligibility",
                    "candidate_id": candidate_id,
                    "eligibility_status": "eligible",
                    "change_note": "attempt generic principle release",
                },
            )
        message = str(excinfo.value)
        assert "principle" in message
        assert "ratification" in message or "canonicalization" in message


def test_api_action_ratifies_promoted_principle_candidate_into_constitution() -> None:
    with TemporaryDirectory() as td:
        root = _copy_repo_subset(Path(td))
        import_result = api_action(
            root,
            {
                "action": "learning_handoff_import",
                "response_text": json.dumps(
                    {
                        "source": {"title": "P", "url": "u", "source_type": "video"},
                        "summary": "s",
                        "key_points": ["p"],
                        "candidate_artifacts": {"principles": [{"statement": "Protect downside first across domains."}]},
                    }
                ),
            },
        )
        candidate_id = import_result["candidate_record_ids"][0]
        api_action(
            root,
            {
                "action": "review_learning_candidate",
                "candidate_id": candidate_id,
                "verdict": "accept",
                "owner_note": "accept first",
            },
        )
        api_action(
            root,
            {
                "action": "promote_learning_candidate",
                "candidate_id": candidate_id,
                "approval_note": "approved for promotion",
            },
        )

        ratify_result = api_action(
            root,
            {
                "action": "ratify_principle_candidate",
                "candidate_id": candidate_id,
                "ratification_note": "Approved as constitutional guidance.",
            },
        )
        assert ratify_result["ok"] is True
        assert ratify_result["action"] == "ratify_principle_candidate"
        assert ratify_result["candidate_ref"] == candidate_id
        assert ratify_result["amendment_record_id"].startswith("pam_")
        assert ratify_result["ratification_approval_ref"].startswith("ap_")
        assert ratify_result["canonical_clause_id"].startswith("pr_")
        assert ratify_result["constitution_updated"] is True

        matched = next(item for item in ratify_result["learning_candidates"] if item["id"] == candidate_id)
        assert matched["lifecycle_stage"] == "canonicalized"
        assert matched["canonicalization_ref"] == ratify_result["amendment_record_id"]
        assert matched["canonical_clause_id"] == ratify_result["canonical_clause_id"]
        assert matched["can_ratify"] is False

        constitution_text = (root / "modules/principles/data/constitution.yaml").read_text(encoding="utf-8")
        assert ratify_result["canonical_clause_id"] in constitution_text
        assert "Protect downside first across domains." in constitution_text

        eligibility_result = api_action(
            root,
            {
                "action": "set_runtime_eligibility",
                "candidate_id": candidate_id,
                "eligibility_status": "eligible",
                "change_note": "release runtime authority after canonicalization",
            },
        )
        assert eligibility_result["runtime_eligibility"]["runtime_eligibility_status"] == "eligible"
        matched = next(item for item in eligibility_result["learning_candidates"] if item["id"] == candidate_id)
        assert matched["lifecycle_stage"] == "canonicalized"
        assert matched["runtime_eligibility_status"] == "eligible"
        assert matched["runtime_state"] == "cooling"

        with pytest.raises(ValueError):
            api_action(
                root,
                {
                    "action": "ratify_principle_candidate",
                    "candidate_id": candidate_id,
                    "ratification_note": "second ratification should fail",
                },
            )


def test_api_action_ratifies_promoted_profile_trait_candidate_into_psych_profile() -> None:
    with TemporaryDirectory() as td:
        root = _copy_repo_subset(Path(td))
        import_result = api_action(
            root,
            {
                "action": "learning_handoff_import",
                "response_text": json.dumps(
                    {
                        "source": {"title": "P", "url": "u", "source_type": "video"},
                        "summary": "s",
                        "key_points": ["p"],
                        "candidate_artifacts": {
                            "profile_traits": [{"statement": "Prefer slower commitment when stress signals are elevated."}]
                        },
                    }
                ),
            },
        )
        candidate_id = import_result["candidate_record_ids"][0]
        api_action(
            root,
            {
                "action": "review_learning_candidate",
                "candidate_id": candidate_id,
                "verdict": "accept",
                "owner_note": "accept first",
            },
        )
        api_action(
            root,
            {
                "action": "promote_learning_candidate",
                "candidate_id": candidate_id,
                "approval_note": "approved for promotion",
            },
        )

        ratify_result = api_action(
            root,
            {
                "action": "ratify_profile_trait_candidate",
                "candidate_id": candidate_id,
                "ratification_note": "Approved as a durable profile baseline update.",
            },
        )
        assert ratify_result["ok"] is True
        assert ratify_result["action"] == "ratify_profile_trait_candidate"
        assert ratify_result["candidate_ref"] == candidate_id
        assert ratify_result["profile_change_record_id"].startswith("pf_")
        assert ratify_result["ratification_approval_ref"].startswith("ap_")
        assert ratify_result["canonical_profile_trait_id"].startswith("pft_")
        assert ratify_result["profile_updated"] is True

        matched = next(item for item in ratify_result["learning_candidates"] if item["id"] == candidate_id)
        assert matched["lifecycle_stage"] == "canonicalized"
        assert matched["canonicalization_ref"] == ratify_result["profile_change_record_id"]
        assert matched["canonical_profile_trait_id"] == ratify_result["canonical_profile_trait_id"]
        assert matched["can_ratify"] is False

        psych_profile_text = (root / "modules/profile/data/psych_profile.yaml").read_text(encoding="utf-8")
        assert ratify_result["canonical_profile_trait_id"] in psych_profile_text
        assert "Prefer slower commitment when stress signals are elevated." in psych_profile_text

        eligibility_result = api_action(
            root,
            {
                "action": "set_runtime_eligibility",
                "candidate_id": candidate_id,
                "eligibility_status": "eligible",
                "change_note": "release runtime authority after canonicalization",
            },
        )
        assert eligibility_result["runtime_eligibility"]["runtime_eligibility_status"] == "eligible"
        matched = next(item for item in eligibility_result["learning_candidates"] if item["id"] == candidate_id)
        assert matched["lifecycle_stage"] == "canonicalized"
        assert matched["runtime_eligibility_status"] == "eligible"
        assert matched["runtime_state"] == "cooling"

        with pytest.raises(ValueError):
            api_action(
                root,
                {
                    "action": "ratify_profile_trait_candidate",
                    "candidate_id": candidate_id,
                    "ratification_note": "second ratification should fail",
                },
            )


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
        assert "suggestion_review_summary" in owner_result
        assert "suggestion_review_trend" in owner_result
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
