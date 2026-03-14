import json
from pathlib import Path
from tempfile import TemporaryDirectory

from router import route_task, route_trace


def test_route_decision() -> None:
    assert route_task("run decision audit") == "decision"


def test_route_content_direction_to_content() -> None:
    assert route_task("propose a content direction for BTC market regime") == "content"


def test_route_trace_forced_module() -> None:
    trace = route_trace("anything", forced_module="memory")
    assert trace["module"] == "memory"
    assert trace["reason"] == "forced_module"
    assert trace["scoring"]["strategy"] == "forced_module"


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
        assert len(trace["scoring"]["routes_candidates"]) >= 1


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
        assert len(trace["scoring"]["manifest_candidates"]) >= 1


def test_route_trace_does_not_match_partial_words() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        (root / "modules/content").mkdir(parents=True, exist_ok=True)
        (root / "modules/decision").mkdir(parents=True, exist_ok=True)

        (root / "modules/content/module.manifest.yaml").write_text(
            json.dumps(
                {
                    "module": "content",
                    "routing": {"keywords": ["post"]},
                    "planning": {"default_skill": "MODULE", "default_output_prefix": "task", "rules": []},
                }
            ),
            encoding="utf-8",
        )
        (root / "modules/decision/module.manifest.yaml").write_text(
            json.dumps(
                {
                    "module": "decision",
                    "routing": {"keywords": ["postmortem"]},
                    "planning": {"default_skill": "MODULE", "default_output_prefix": "task", "rules": []},
                }
            ),
            encoding="utf-8",
        )

        trace = route_trace("postmortem for project", repo_root=root)
        assert trace["module"] == "decision"
        assert "postmortem" in trace["matched_keywords"]


def test_route_trace_prefers_higher_weight_manifest_match() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        (root / "modules/content").mkdir(parents=True, exist_ok=True)
        (root / "modules/decision").mkdir(parents=True, exist_ok=True)

        (root / "modules/content/module.manifest.yaml").write_text(
            json.dumps(
                {
                    "module": "content",
                    "routing": {
                        "keywords": ["plan"],
                        "keyword_weights": {"plan": 1},
                    },
                    "planning": {"default_skill": "MODULE", "default_output_prefix": "task", "rules": []},
                }
            ),
            encoding="utf-8",
        )
        (root / "modules/decision/module.manifest.yaml").write_text(
            json.dumps(
                {
                    "module": "decision",
                    "routing": {
                        "keywords": ["plan", "postmortem"],
                        "keyword_weights": {"plan": 1, "postmortem": 5},
                    },
                    "planning": {"default_skill": "MODULE", "default_output_prefix": "task", "rules": []},
                }
            ),
            encoding="utf-8",
        )

        trace = route_trace("need a postmortem plan", repo_root=root)
        assert trace["module"] == "decision"
        assert "postmortem" in trace["matched_keywords"]


def test_route_trace_routes_support_negative_keywords() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        cfg = root / "orchestrator/config/routes.json"
        cfg.parent.mkdir(parents=True, exist_ok=True)
        cfg.write_text(
            json.dumps(
                {
                    "default_module": "decision",
                    "routes": [
                        {
                            "module": "content",
                            "keywords": ["post"],
                            "negative_keywords": ["postmortem"],
                            "keyword_weights": {"post": 1, "postmortem": 3},
                        },
                        {
                            "module": "decision",
                            "keywords": ["postmortem"],
                            "keyword_weights": {"postmortem": 4},
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )

        trace = route_trace("postmortem notes", repo_root=root)
        assert trace["module"] == "decision"
        assert trace["reason"] == "routes_keyword_match"
