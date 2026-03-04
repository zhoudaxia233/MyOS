from __future__ import annotations

from pathlib import Path

from llm_router import llm_route_trace
from manifests import discover_module_manifests
from router import route_trace
from settings import get_openai_api_key, load_settings


def select_route(task: str, forced_module: str | None, repo_root: Path) -> dict:
    if forced_module:
        return route_trace(task, forced_module=forced_module, repo_root=repo_root)

    settings = load_settings(repo_root)
    api_key = get_openai_api_key(repo_root)

    if api_key:
        manifests = discover_module_manifests(repo_root)
        module_names = [m for m in sorted(manifests.keys()) if m != "_template"]
        if module_names:
            return llm_route_trace(
                task=task,
                module_names=module_names,
                model=str(settings.get("routing_model", "gpt-4.1-nano")),
                api_key=api_key,
            )

    return route_trace(task, forced_module=None, repo_root=repo_root)
