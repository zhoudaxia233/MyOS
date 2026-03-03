import json
from pathlib import Path
from tempfile import TemporaryDirectory

from router import route_task, route_trace


def test_route_decision() -> None:
    assert route_task("run decision audit") == "decision"


def test_route_trace_forced_module() -> None:
    trace = route_trace("anything", forced_module="memory")
    assert trace["module"] == "memory"
    assert trace["reason"] == "forced_module"


def test_route_trace_uses_config_rules() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        cfg = root / "orchestrator/config/routes.json"
        cfg.parent.mkdir(parents=True, exist_ok=True)
        cfg.write_text(
            json.dumps(
                {
                    "default_module": "decision",
                    "routes": [
                        {"module": "memory", "keywords": ["diary"]},
                    ],
                }
            ),
            encoding="utf-8",
        )

        trace = route_trace("summarize my diary notes", repo_root=root)
        assert trace["module"] == "memory"
        assert trace["reason"] == "routes_keyword_match"
        assert "diary" in trace["matched_keywords"]


def test_route_trace_uses_module_manifest_rules_first() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        manifest = root / "modules/memory/module.manifest.yaml"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(
            json.dumps(
                {
                    "module": "memory",
                    "routing": {"keywords": ["diary"]},
                    "planning": {"default_skill": "MODULE", "default_output_prefix": "task", "rules": []},
                }
            ),
            encoding="utf-8",
        )

        trace = route_trace("summarize my diary notes", repo_root=root)
        assert trace["module"] == "memory"
        assert trace["reason"] == "manifest_keyword_match"
        assert "diary" in trace["matched_keywords"]
