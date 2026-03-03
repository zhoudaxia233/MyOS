from pathlib import Path
from tempfile import TemporaryDirectory

from guardrails import evaluate_guardrail, load_domain_guardrails


def _write_policy(root: Path) -> None:
    path = root / "modules/decision/data/domain_guardrails.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """
domains:
  invest:
    require_precommit: true
    require_guardrail_check_id: true
    max_emotional_without_cooldown: 6
    required_fields:
      - downside
      - invalidation_condition
      - max_loss
      - disconfirming_signal
    allow_override: true
    override_required_fields:
      - override_reason
      - owner_confirmation

global:
  block_when_missing_required_fields: true
  block_when_high_emotion_without_cooldown: true
""".strip()
        + "\n",
        encoding="utf-8",
    )


def test_guardrail_pass_with_cooldown_and_required_fields() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _write_policy(root)
        policy = load_domain_guardrails(root)

        result = evaluate_guardrail(
            policy,
            "invest",
            {
                "guardrail_check_id": "pc_1",
                "downside": "loss risk",
                "invalidation_condition": "price invalidates",
                "max_loss": "0.4R",
                "disconfirming_signal": "volume divergence",
                "emotional_weight": 7,
                "cooldown_applied": True,
                "cooldown_hours": 12,
            },
        )

        assert result["status"] == "pass"
        assert result["violations"] == []
        assert result["required_cooldown_hours"] == 12


def test_guardrail_block_when_required_fields_missing() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _write_policy(root)
        policy = load_domain_guardrails(root)

        result = evaluate_guardrail(
            policy,
            "invest",
            {
                "emotional_weight": 3,
                "cooldown_applied": False,
            },
        )

        assert result["status"] == "blocked"
        assert any(v.startswith("missing_required_fields") for v in result["violations"])


def test_guardrail_override_accepted_when_fields_present() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _write_policy(root)
        policy = load_domain_guardrails(root)

        result = evaluate_guardrail(
            policy,
            "invest",
            {
                "guardrail_check_id": None,
                "downside": "loss risk",
                "invalidation_condition": "price invalidates",
                "max_loss": "1R",
                "disconfirming_signal": "volume divergence",
                "emotional_weight": 8,
                "cooldown_applied": False,
                "override_requested": True,
                "override_reason": "time-sensitive hedge",
                "owner_confirmation": "approved",
            },
        )

        assert result["status"] == "override_accepted"
        assert result["override_allowed"] is True


def test_guardrail_block_on_insufficient_cooldown_and_risk_limit() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _write_policy(root)
        policy = load_domain_guardrails(root)

        result = evaluate_guardrail(
            policy,
            "invest",
            {
                "guardrail_check_id": "pc_2",
                "downside": "loss risk",
                "invalidation_condition": "price invalidates",
                "max_loss": "0.8R",
                "disconfirming_signal": "volume divergence",
                "emotional_weight": 9,
                "cooldown_applied": True,
                "cooldown_hours": 2,
            },
        )

        assert result["status"] == "blocked"
        assert "insufficient_cooldown_hours" in result["violations"]
        assert "max_loss_exceeds_limit" in result["violations"]
