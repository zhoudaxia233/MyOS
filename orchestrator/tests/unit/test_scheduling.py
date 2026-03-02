from pathlib import Path

from scheduling import routines_for_cycle


def test_routines_for_weekly_loads_expected_entries():
    repo_root = Path(__file__).resolve().parents[3]
    weekly = routines_for_cycle(repo_root, "weekly")
    assert len(weekly) == 3
    assert all("id" in r and "module" in r and "skill" in r and "objective" in r for r in weekly)
