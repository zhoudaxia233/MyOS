from __future__ import annotations

from pathlib import Path

from scheduling import routines_for_cycle


def describe_manual() -> str:
    return "Manual scheduler: execute configured cadence cycles from CLI."


def get_cycle(repo_root: Path, cycle: str) -> list[dict[str, str]]:
    return routines_for_cycle(repo_root, cycle)
