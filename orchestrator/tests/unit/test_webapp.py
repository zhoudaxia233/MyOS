from __future__ import annotations

import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from webapp import api_action, api_inspect, api_run, api_status


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


def test_api_inspect_and_run_writes_output() -> None:
    with TemporaryDirectory() as td:
        root = _copy_repo_subset(Path(td))

        inspect_payload = {
            "task": "run weekly decision review",
            "provider": "manual",
            "with_retrieval": False,
        }
        inspect_result = api_inspect(root, inspect_payload)

        assert inspect_result["ok"] is True
        assert inspect_result["module"] == "decision"
        assert inspect_result["route"]["reason"] in {
            "manifest_keyword_match",
            "routes_keyword_match",
            "forced_module",
            "fallback_default",
        }
        assert inspect_result["plan"]["skill"].endswith(".md")
        assert len(inspect_result["loaded_files"]) >= 2

        run_result = api_run(root, inspect_payload)
        assert run_result["ok"] is True
        assert run_result["output_path"].endswith(".md")
        assert len(run_result["output_hash"]) == 64
        assert isinstance(run_result["output_preview"], str)
        assert len(run_result["output_preview"]) > 0
        assert (root / run_result["output_path"]).exists()


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
                "provider": "manual",
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
