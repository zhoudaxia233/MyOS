from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

import main


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_jsonl(path: Path, schema_name: str, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    schema = {"_schema": {"name": schema_name, "version": "1.0", "fields": fields, "notes": "append-only"}}
    with path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(schema) + "\n")
        for row in rows:
            f.write(json.dumps(row) + "\n")


def _setup_repo(root: Path) -> None:
    _write(
        root / "modules/decision/data/domain_guardrails.yaml",
        "\n".join(
            [
                "domains:",
                "  invest:",
                "    require_precommit: true",
                "    require_guardrail_check_id: true",
                "    max_emotional_without_cooldown: 6",
                "    required_cooldown_hours_when_high_emotion: 12",
                "    max_loss_limit_r: 0.5",
                "    required_fields:",
                "      - downside",
                "      - invalidation_condition",
                "      - max_loss",
                "      - disconfirming_signal",
                "    allow_override: true",
                "    require_owner_confirmation_for_override: true",
                "    override_required_fields:",
                "      - override_reason",
                "      - owner_confirmation",
                "",
                "global:",
                "  block_when_missing_required_fields: true",
                "  block_when_high_emotion_without_cooldown: true",
                "  block_when_max_loss_exceeds_limit: true",
                "  block_when_cooldown_hours_insufficient: true",
            ]
        )
        + "\n",
    )
    _write(
        root / "modules/principles/data/constitution.yaml",
        "\n".join(
            [
                "constitution:",
                "  version: \"1.0\"",
                "clauses:",
                "  - clause_id: \"pr_0001\"",
                "    title: \"Long-term compounding\"",
                "    statement: \"Prefer long-term compounding over short-term noise.\"",
            ]
        )
        + "\n",
    )
    _write_jsonl(
        root / "modules/principles/logs/principle_exceptions.jsonl",
        "principle_exceptions",
        [
            "id",
            "created_at",
            "status",
            "object_type",
            "principle_id",
            "request_context",
            "exception_reason",
            "risk_acknowledged",
            "owner_confirmation",
            "decision_ref",
            "expires_at",
            "resolution_status",
            "source_refs",
        ],
        [],
    )

    _write_jsonl(
        root / "modules/decision/logs/decisions.jsonl",
        "decisions",
        [
            "id",
            "created_at",
            "status",
            "domain",
            "decision",
            "options",
            "reasoning",
            "risks",
            "expected_outcome",
            "time_horizon",
            "confidence",
            "guardrail_check_id",
            "follow_up_date",
            "outcome",
        ],
        [],
    )
    _write_jsonl(
        root / "modules/decision/logs/precommit_checks.jsonl",
        "precommit_checks",
        [
            "id",
            "created_at",
            "status",
            "domain",
            "proposed_decision",
            "emotional_weight",
            "downside",
            "invalidation_condition",
            "max_loss",
            "disconfirming_signal",
            "cooldown_required",
            "override_reason",
            "owner_confirmation",
            "result",
        ],
        [
            {
                "id": "pc_20260305_001",
                "created_at": "2026-03-05T11:00:00Z",
                "status": "active",
                "domain": "invest",
                "proposed_decision": "Open a bounded risk position",
                "emotional_weight": 5,
                "downside": "bounded to 0.5R",
                "invalidation_condition": "close below invalidation",
                "max_loss": "0.5R",
                "disconfirming_signal": "volume breakdown",
                "cooldown_required": False,
                "override_reason": None,
                "owner_confirmation": None,
                "result": "pass",
            }
        ],
    )


def _line_count(path: Path) -> int:
    if not path.exists():
        return 0
    return len(path.read_text(encoding="utf-8").splitlines())


def test_cmd_log_decision_blocks_and_does_not_append_decision(monkeypatch) -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _setup_repo(root)
        monkeypatch.setattr(main, "repo_root", lambda: root)

        decisions = root / "modules/decision/logs/decisions.jsonl"
        before_decisions = _line_count(decisions)

        args = Namespace(
            domain="invest",
            decision="Increase leverage immediately",
            option=["hold", "increase"],
            confidence=7,
            reasoning="Momentum looked strong",
            risk=["Could violate risk budget"],
            expected_outcome=None,
            time_horizon=None,
            guardrail_check_id=None,
            downside=None,
            invalidation_condition=None,
            max_loss=None,
            disconfirming_signal=None,
            emotional_weight=8,
            cooldown_applied=False,
            cooldown_hours=0,
            override_requested=False,
            override_reason=None,
            owner_confirmation=None,
            principle_ref=[],
            exception_ref=None,
            follow_up_date=None,
            outcome=None,
            provider="dry-run",
            notes=None,
        )

        with pytest.raises(RuntimeError):
            main.cmd_log_decision(args)

        after_decisions = _line_count(decisions)
        gate_checks = root / "modules/decision/logs/decision_gate_checks.jsonl"

        assert after_decisions == before_decisions
        assert gate_checks.exists()
        assert _line_count(gate_checks) >= 2


def test_cmd_log_decision_appends_when_gate_passes(monkeypatch) -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _setup_repo(root)
        monkeypatch.setattr(main, "repo_root", lambda: root)

        decisions = root / "modules/decision/logs/decisions.jsonl"
        before_decisions = _line_count(decisions)

        args = Namespace(
            domain="invest",
            decision="Open bounded-risk position",
            option=["skip", "open small"],
            confidence=8,
            reasoning="Edge is present and downside is bounded",
            risk=["execution slippage"],
            expected_outcome="Risk-adjusted return",
            time_horizon="3 days",
            guardrail_check_id="pc_20260305_001",
            downside="bounded to 0.5R",
            invalidation_condition="close below invalidation",
            max_loss="0.5R",
            disconfirming_signal="volume breakdown",
            emotional_weight=4,
            cooldown_applied=False,
            cooldown_hours=0,
            override_requested=False,
            override_reason=None,
            owner_confirmation=None,
            principle_ref=["pr_0001"],
            exception_ref=None,
            follow_up_date=None,
            outcome=None,
            provider="dry-run",
            notes=None,
        )

        rc = main.cmd_log_decision(args)
        assert rc == 0

        after_decisions = _line_count(decisions)
        gate_checks = root / "modules/decision/logs/decision_gate_checks.jsonl"
        assert after_decisions == before_decisions + 1
        assert gate_checks.exists()
