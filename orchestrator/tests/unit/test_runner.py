from __future__ import annotations

import pytest

from runner import run_with_provider


def _plan() -> dict:
    return {
        "skill": "modules/decision/skills/weekly_review.md",
        "output_path": "modules/decision/outputs/weekly_review_20260304_000000.md",
    }


def _bundle() -> dict:
    return {
        "files": [
            {"path": "core/ROUTER.md", "content": "# Router\n"},
            {"path": "modules/decision/MODULE.md", "content": "# Decision\n"},
        ]
    }


def test_run_with_handoff_provider_returns_copy_block() -> None:
    out = run_with_provider(
        "handoff",
        "run weekly decision review",
        "decision",
        _plan(),
        _bundle(),
        "gpt-4.1-mini",
    )

    assert "[BEGIN PERSONAL CORE OS HANDOFF]" in out
    assert "Task:" in out
    assert "run weekly decision review" in out
    assert "Schema debugger prompts" in out
    assert "Output structure guideline" in out
    assert "## FILE: core/ROUTER.md" in out


def test_run_with_unsupported_provider_raises() -> None:
    with pytest.raises(ValueError):
        run_with_provider(
            "unknown",
            "task",
            "decision",
            _plan(),
            _bundle(),
            "gpt-4.1-mini",
        )
