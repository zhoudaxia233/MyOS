from __future__ import annotations


def route_task(task: str, forced_module: str | None = None) -> str:
    if forced_module:
        return forced_module

    t = task.lower()
    if any(k in t for k in ["write", "publish", "thread", "tone", "edit", "post", "draft"]):
        return "content"
    if any(k in t for k in ["decision", "priority", "review", "failure", "risk", "audit", "tradeoff"]):
        return "decision"
    if any(k in t for k in ["profile", "goal", "value", "alignment", "psych", "drift", "trigger"]):
        return "profile"
    if any(k in t for k in ["memory", "reflect", "insight", "distill", "paradigm", "pattern", "chat"]):
        return "memory"
    return "decision"
