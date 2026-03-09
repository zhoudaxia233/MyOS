from __future__ import annotations

from pathlib import Path

from llm_router import llm_route_trace
from manifests import discover_module_manifests
from router import route_trace
from settings import apply_openai_api_key_env, get_openai_api_key, load_settings


def _available_modules(repo_root: Path) -> list[str]:
    manifests = discover_module_manifests(repo_root)
    return [m for m in sorted(manifests.keys()) if m != "_template"]


def select_route(task: str, forced_module: str | None, repo_root: Path) -> dict:
    module_names = _available_modules(repo_root)

    if forced_module:
        if forced_module not in module_names:
            raise ValueError(f"Unknown module: {forced_module}")
        return route_trace(task, forced_module=forced_module, repo_root=repo_root)

    settings = load_settings(repo_root)
    api_key = get_openai_api_key(repo_root)

    if api_key and module_names:
        try:
            apply_openai_api_key_env(repo_root)
            route = llm_route_trace(
                task=task,
                module_names=module_names,
                model=str(settings.get("routing_model", "gpt-4.1-nano")),
                api_key=api_key,
            )
            route["scoring"] = {
                "strategy": "llm_model_route",
                "manifest_candidates": [],
                "routes_candidates": [],
            }
            return route
        except Exception as exc:  # noqa: BLE001
            fallback = route_trace(task, forced_module=None, repo_root=repo_root)
            fallback["reason"] = f"llm_route_fallback:{exc.__class__.__name__}:{fallback['reason']}"
            return fallback

    return route_trace(task, forced_module=None, repo_root=repo_root)
