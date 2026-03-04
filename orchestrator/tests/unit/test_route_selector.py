from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

import route_selector


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_select_route_falls_back_without_api_key() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _write(
            root / "modules/decision/module.manifest.yaml",
            json.dumps(
                {
                    "module": "decision",
                    "routing": {"keywords": ["decision"]},
                    "planning": {"default_skill": "MODULE", "default_output_prefix": "task", "rules": []},
                }
            ),
        )

        trace = route_selector.select_route("log a decision", None, root)
        assert trace["module"] == "decision"
        assert trace["reason"] in {"manifest_keyword_match", "routes_keyword_match", "fallback_default"}


def test_select_route_uses_llm_when_api_key_exists(monkeypatch) -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _write(
            root / "modules/content/module.manifest.yaml",
            json.dumps(
                {
                    "module": "content",
                    "routing": {"keywords": ["write"]},
                    "planning": {"default_skill": "MODULE", "default_output_prefix": "task", "rules": []},
                }
            ),
        )
        _write(
            root / "modules/decision/module.manifest.yaml",
            json.dumps(
                {
                    "module": "decision",
                    "routing": {"keywords": ["decision"]},
                    "planning": {"default_skill": "MODULE", "default_output_prefix": "task", "rules": []},
                }
            ),
        )
        _write(
            root / "orchestrator/config/settings.json",
            json.dumps(
                {
                    "openai_api_key": "sk-test",
                    "default_provider": "handoff",
                    "task_model": "gpt-4.1-mini",
                    "routing_model": "gpt-4.1-nano",
                }
            ),
        )

        called = {"ok": False}

        def _fake_llm(task: str, module_names: list[str], model: str, api_key: str) -> dict:
            called["ok"] = True
            assert api_key == "sk-test"
            assert model == "gpt-4.1-nano"
            assert "content" in module_names
            assert "decision" in module_names
            return {"module": "content", "reason": "llm_model_route:test", "matched_keywords": []}

        monkeypatch.setattr(route_selector, "llm_route_trace", _fake_llm)

        trace = route_selector.select_route("write a post", None, root)
        assert called["ok"] is True
        assert trace["module"] == "content"
        assert trace["reason"].startswith("llm_model_route")


def test_select_route_falls_back_when_llm_router_fails(monkeypatch) -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _write(
            root / "modules/content/module.manifest.yaml",
            json.dumps(
                {
                    "module": "content",
                    "routing": {"keywords": ["write"]},
                    "planning": {"default_skill": "MODULE", "default_output_prefix": "task", "rules": []},
                }
            ),
        )
        _write(
            root / "orchestrator/config/settings.json",
            json.dumps(
                {
                    "openai_api_key": "sk-test",
                    "default_provider": "handoff",
                    "task_model": "gpt-4.1-mini",
                    "routing_model": "gpt-4.1-nano",
                }
            ),
        )

        def _raise(*args, **kwargs):  # noqa: ANN002,ANN003
            raise RuntimeError("router down")

        monkeypatch.setattr(route_selector, "llm_route_trace", _raise)

        trace = route_selector.select_route("write a post", None, root)
        assert trace["module"] == "content"
        assert trace["reason"].startswith("llm_route_fallback:RuntimeError:")


def test_select_route_rejects_unknown_forced_module() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _write(
            root / "modules/decision/module.manifest.yaml",
            json.dumps(
                {
                    "module": "decision",
                    "routing": {"keywords": ["decision"]},
                    "planning": {"default_skill": "MODULE", "default_output_prefix": "task", "rules": []},
                }
            ),
        )

        with pytest.raises(ValueError):
            route_selector.select_route("anything", "nonexistent_module", root)
