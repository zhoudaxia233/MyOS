from __future__ import annotations

from datetime import datetime, timezone


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d")


def plan_task(task: str, module: str) -> dict:
    t = task.lower()
    date = _today()

    if module == "decision" and "weekly" in t:
        return {
            "skill": "modules/decision/skills/weekly_review.md",
            "output_path": f"modules/decision/outputs/weekly_review_{date}.md",
        }
    if module == "decision" and "audit" in t:
        return {
            "skill": "modules/decision/skills/audit_decision_system.md",
            "output_path": f"modules/decision/outputs/decision_audit_{date}.md",
        }
    if module == "memory" and ("weekly" in t or "distill" in t):
        return {
            "skill": "modules/memory/skills/distill_weekly.md",
            "output_path": f"modules/memory/outputs/weekly_memory_{date}.md",
        }
    if module == "profile" and ("snapshot" in t or "monthly" in t):
        return {
            "skill": "modules/profile/skills/profile_snapshot.md",
            "output_path": f"modules/profile/outputs/profile_snapshot_{date}.md",
        }

    return {
        "skill": f"modules/{module}/MODULE.md",
        "output_path": f"modules/{module}/outputs/task_{date}.md",
    }
