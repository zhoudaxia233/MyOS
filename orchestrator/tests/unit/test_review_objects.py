from review_objects import (
    REVIEW_OBJECT_TYPE_JUDGMENT_PROPOSAL,
    REVIEW_OBJECT_TYPE_TRACE,
    build_run_review_object,
)


def test_build_run_review_object_extracts_explicit_owner_action_proposal() -> None:
    content = "\n".join(
        [
            "# Weekly Review",
            "",
            "## 3 patterns noticed",
            "- Guardrails were mostly present.",
            "",
            "## Owner Action Proposal",
            "- Keep the review to the top 3 reversible actions | risk: could miss lower-priority compounding work.",
            "- Add one-line risk notes before acting | risk: may create false certainty if evidence stays weak.",
        ]
    )

    review_object = build_run_review_object(
        module="decision",
        skill="modules/decision/skills/weekly_review.md",
        content=content,
    )

    assert review_object["review_object_type"] == REVIEW_OBJECT_TYPE_JUDGMENT_PROPOSAL
    assert review_object["proposal_kind"] == "owner_action_proposal"
    assert review_object["proposal_heading"] == "Owner Action Proposal"
    assert "top 3 reversible actions" in review_object["proposal_summary"]


def test_build_run_review_object_preserves_content_direction_kind() -> None:
    content = "\n".join(
        [
            "# Content Notes",
            "",
            "## Content Direction Proposal",
            "- Frame BTC regime as a behavior-shift story, not a price prediction thread.",
            "- Lead with one concrete market-behavior contrast before making the claim.",
        ]
    )

    review_object = build_run_review_object(
        module="content",
        skill="modules/content/skills/strategy_direction.md",
        content=content,
    )

    assert review_object["review_object_type"] == REVIEW_OBJECT_TYPE_JUDGMENT_PROPOSAL
    assert review_object["proposal_kind"] == "content_direction_proposal"
    assert review_object["proposal_heading"] == "Content Direction Proposal"


def test_build_run_review_object_keeps_execution_packet_as_trace() -> None:
    review_object = build_run_review_object(
        module="decision",
        skill="modules/decision/skills/weekly_review.md",
        content="# Execution Packet\n\n- Task: run weekly decision review\n",
    )

    assert review_object["review_object_type"] == REVIEW_OBJECT_TYPE_TRACE
    assert review_object["proposal_kind"] is None
