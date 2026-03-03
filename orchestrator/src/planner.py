from __future__ import annotations

from datetime import datetime, timezone


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def plan_task(task: str, module: str, skill_hint: str | None = None, routine_id: str | None = None) -> dict:
    t = task.lower()
    stamp = _stamp()
    routine_suffix = f"_{routine_id}" if routine_id else ""

    if skill_hint:
        return {
            "skill": f"modules/{module}/skills/{skill_hint}.md",
            "output_path": f"modules/{module}/outputs/{skill_hint}_{stamp}{routine_suffix}.md",
        }

    if module == "decision" and "weekly" in t:
        return {
            "skill": "modules/decision/skills/weekly_review.md",
            "output_path": f"modules/decision/outputs/weekly_review_{stamp}.md",
        }
    if module == "decision" and "audit" in t:
        return {
            "skill": "modules/decision/skills/audit_decision_system.md",
            "output_path": f"modules/decision/outputs/decision_audit_{stamp}.md",
        }
    if module == "memory" and ("weekly" in t or "distill" in t):
        return {
            "skill": "modules/memory/skills/distill_weekly.md",
            "output_path": f"modules/memory/outputs/weekly_memory_{stamp}.md",
        }
    if module == "profile" and ("snapshot" in t or "monthly" in t):
        return {
            "skill": "modules/profile/skills/profile_snapshot.md",
            "output_path": f"modules/profile/outputs/profile_snapshot_{stamp}.md",
        }

    return {
        "skill": f"modules/{module}/MODULE.md",
        "output_path": f"modules/{module}/outputs/task_{stamp}.md",
    }
