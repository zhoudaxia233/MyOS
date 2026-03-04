from __future__ import annotations

from providers.handoff import run_handoff
from providers.manual import run_manual
from providers.openai_provider import run_openai


def run_with_provider(provider: str, task: str, module: str, plan: dict, bundle: dict, model: str) -> str:
    if provider == "dry-run":
        return run_manual(task, module, plan, bundle)
    if provider == "handoff":
        return run_handoff(task, module, plan, bundle)
    if provider == "openai":
        return run_openai(task, module, plan, bundle, model)
    raise ValueError(f"Unsupported provider: {provider}")
