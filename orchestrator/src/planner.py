from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from manifests import load_module_manifest


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _build_plan(module: str, skill: str, output_prefix: str, stamp: str, routine_suffix: str) -> dict:
    if skill == "MODULE":
        return {
            "skill": f"modules/{module}/MODULE.md",
            "output_path": f"modules/{module}/outputs/{output_prefix}_{stamp}{routine_suffix}.md",
        }
    return {
        "skill": f"modules/{module}/skills/{skill}.md",
        "output_path": f"modules/{module}/outputs/{output_prefix}_{stamp}{routine_suffix}.md",
    }


def plan_task(
    task: str,
    module: str,
    skill_hint: str | None = None,
    routine_id: str | None = None,
    repo_root: Path | None = None,
) -> dict:
    t = task.lower()
    stamp = _stamp()
    routine_suffix = f"_{routine_id}" if routine_id else ""

    if skill_hint:
        return _build_plan(module, skill_hint, skill_hint, stamp, routine_suffix)

    if repo_root is None:
        return _build_plan(module, "MODULE", "task", stamp, routine_suffix)

    manifest = load_module_manifest(repo_root, module)
    planning = manifest.get("planning", {})
    rules = planning.get("rules", [])

    for rule in rules:
        match_any = rule.get("match_any", [])
        if any(token in t for token in match_any):
            return _build_plan(
                module,
                str(rule.get("skill", "MODULE")),
                str(rule.get("output_prefix", "task")),
                stamp,
                routine_suffix,
            )

    return _build_plan(
        module,
        str(planning.get("default_skill", "MODULE")),
        str(planning.get("default_output_prefix", "task")),
        stamp,
        routine_suffix,
    )
