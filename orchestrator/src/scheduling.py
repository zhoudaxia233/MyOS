from __future__ import annotations

from pathlib import Path

VALID_CYCLES = {"daily", "weekly", "monthly"}


def load_cadence(repo_root: Path) -> dict[str, list[dict[str, str]]]:
    path = repo_root / "routines" / "cadence.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Cadence file not found: {path}")

    data: dict[str, list[dict[str, str]]] = {"daily": [], "weekly": [], "monthly": []}
    current_cycle: str | None = None
    current_item: dict[str, str] | None = None

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped == "routines:":
            continue

        if line.startswith("  ") and stripped.endswith(":") and not line.startswith("    "):
            if current_cycle and current_item:
                data[current_cycle].append(current_item)
            cycle = stripped[:-1]
            current_cycle = cycle if cycle in VALID_CYCLES else None
            current_item = None
            continue

        if current_cycle is None:
            continue

        if line.startswith("    - "):
            if current_item:
                data[current_cycle].append(current_item)
            current_item = {}
            payload = stripped[2:]
            if ":" in payload:
                k, v = payload.split(":", 1)
                current_item[k.strip()] = v.strip().strip('"')
            continue

        if line.startswith("      ") and current_item is not None and ":" in stripped:
            k, v = stripped.split(":", 1)
            current_item[k.strip()] = v.strip().strip('"')

    if current_cycle and current_item:
        data[current_cycle].append(current_item)

    for cycle in ("daily", "weekly", "monthly"):
        for item in data[cycle]:
            for req in ("id", "module", "skill", "objective"):
                if req not in item:
                    raise ValueError(f"Missing field '{req}' in cadence item: {item}")

    return data


def routines_for_cycle(repo_root: Path, cycle: str) -> list[dict[str, str]]:
    cycle_norm = cycle.strip().lower()
    if cycle_norm not in VALID_CYCLES:
        raise ValueError(f"Unsupported cycle: {cycle}")
    cadence = load_cadence(repo_root)
    return cadence[cycle_norm]


def task_from_routine(cycle: str, routine: dict[str, str]) -> str:
    return f"[{cycle}] {routine['objective']}"
