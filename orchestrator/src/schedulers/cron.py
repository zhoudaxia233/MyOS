from __future__ import annotations

from pathlib import Path

from scheduling import routines_for_cycle


def describe_cron() -> str:
    return "Cron scheduler helper: render cron-style cycle hints."


def cron_hint(repo_root: Path, cycle: str) -> str:
    routines = routines_for_cycle(repo_root, cycle)
    return f"{cycle}: {len(routines)} routines configured in routines/cadence.yaml"
