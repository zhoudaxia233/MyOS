from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from decision_gate import evaluate_decision_entry_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_precommit(path: Path, rows: list[dict]) -> None:
    schema = {
        "_schema": {
            "name": "precommit_checks",
            "version": "1.0",
            "fields": [
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
            "notes": "append-only",
        }
    }
    path.parent.mkdir(parents=True, exist_ok=True)
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


def test_decision_gate_pass_with_valid_precommit_and_guardrail_fields() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _setup_repo(root)
        _write_precommit(
            root / "modules/decision/logs/precommit_checks.jsonl",
            [
                {
                    "id": "pc_20260305_001",
                    "created_at": "2026-03-05T10:00:00Z",
                    "status": "active",
                    "domain": "invest",
                    "proposed_decision": "Open a position",
                    "emotional_weight": 5,
                    "downside": "limited to 0.5R",
                    "invalidation_condition": "close below support",
                    "max_loss": "0.5R",
                    "disconfirming_signal": "momentum divergence",
                    "cooldown_required": False,
                    "override_reason": None,
                    "owner_confirmation": None,
                    "result": "pass",
                }
            ],
        )

        result = evaluate_decision_entry_gate(
            root,
            domain="invest",
            guardrail_check_id="pc_20260305_001",
            downside="loss bounded",
            invalidation_condition="close below support",
            max_loss="0.5R",
            disconfirming_signal="momentum divergence",
            emotional_weight=4,
            cooldown_applied=False,
            cooldown_hours=0,
            override_requested=False,
            override_reason=None,
            owner_confirmation=None,
        )

        assert result["gate_status"] == "pass"
        assert result["precommit_status"] == "pass"
        assert result["guardrail_status"] == "pass"
        assert result["violations"] == []


def test_decision_gate_blocked_when_precommit_missing() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _setup_repo(root)
        _write_precommit(root / "modules/decision/logs/precommit_checks.jsonl", [])

        result = evaluate_decision_entry_gate(
            root,
            domain="invest",
            guardrail_check_id=None,
            downside="loss bounded",
            invalidation_condition="close below support",
            max_loss="0.5R",
            disconfirming_signal="momentum divergence",
            emotional_weight=4,
            cooldown_applied=False,
            cooldown_hours=0,
            override_requested=False,
            override_reason=None,
            owner_confirmation=None,
        )

        assert result["gate_status"] == "blocked"
        assert "precommit_ref_missing" in result["violations"]


def test_decision_gate_override_accepted_when_fields_complete() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _setup_repo(root)
        _write_precommit(
            root / "modules/decision/logs/precommit_checks.jsonl",
            [
                {
                    "id": "pc_20260305_002",
                    "created_at": "2026-03-05T10:10:00Z",
                    "status": "active",
                    "domain": "invest",
                    "proposed_decision": "Increase position size",
                    "emotional_weight": 8,
                    "downside": "bounded",
                    "invalidation_condition": "close below invalidation",
                    "max_loss": "0.8R",
                    "disconfirming_signal": "volume collapse",
                    "cooldown_required": True,
                    "override_reason": None,
                    "owner_confirmation": None,
                    "result": "pass_with_cooldown",
                }
            ],
        )

        result = evaluate_decision_entry_gate(
            root,
            domain="invest",
            guardrail_check_id="pc_20260305_002",
            downside="bounded",
            invalidation_condition="close below invalidation",
            max_loss="0.8R",
            disconfirming_signal="volume collapse",
            emotional_weight=9,
            cooldown_applied=False,
            cooldown_hours=0,
            override_requested=True,
            override_reason="time-sensitive hedge",
            owner_confirmation="approved",
        )

        assert result["gate_status"] == "override_accepted"
        assert result["guardrail_status"] == "override_accepted"
        assert result["precommit_status"] == "pass_with_cooldown"
