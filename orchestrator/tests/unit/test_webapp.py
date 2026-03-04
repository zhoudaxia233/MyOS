from __future__ import annotations

import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from webapp import api_action, api_get_settings, api_inspect, api_output, api_run, api_status, api_update_settings


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

        run_result = api_run(root, inspect_payload)
        assert run_result["ok"] is True
        assert run_result["output_path"].endswith(".md")
        assert len(run_result["output_hash"]) == 64
        assert isinstance(run_result["output_preview"], str)
        assert len(run_result["output_preview"]) > 0
        assert (root / run_result["output_path"]).exists()

        output_payload = api_output(root, run_result["output_path"])
        assert output_payload["ok"] is True
        assert output_payload["path"] == run_result["output_path"]
        assert "Execution Packet" in output_payload["content"]


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
        assert (root / metrics_result["output_path"]).exists()

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


def test_api_output_rejects_non_output_and_escape_paths() -> None:
    with TemporaryDirectory() as td:
        root = _copy_repo_subset(Path(td))
        with pytest.raises(ValueError):
            api_output(root, "core/ROUTER.md")
        with pytest.raises(ValueError):
            api_output(root, "../README.md")


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
