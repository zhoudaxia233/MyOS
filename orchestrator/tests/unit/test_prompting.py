from prompting import (
    execution_instruction,
    review_object_instruction,
    schema_debugger_enabled,
    schema_debugger_output_sections,
    schema_debugger_questions,
)


def test_schema_debugger_enabled_for_core_modules() -> None:
    assert schema_debugger_enabled("decision", "run weekly review")
    assert schema_debugger_enabled("cognition", "any task")
    assert not schema_debugger_enabled("content", "write a post")


def test_schema_debugger_enabled_for_keyword_task() -> None:
    assert schema_debugger_enabled("content", "analyze schema contradiction in this idea")


def test_execution_instruction_includes_debugger_prompts_when_enabled() -> None:
    text = execution_instruction("review schema mismatch in investing", "decision")
    prompts = schema_debugger_questions("decision", "review schema mismatch in investing")
    sections = schema_debugger_output_sections("decision", "review schema mismatch in investing")
    assert "Schema debugger prompts" in text
    assert "Output structure guideline" in text
    assert len(prompts) >= 6
    assert len(sections) >= 8
    assert prompts[0] in text
    assert sections[0] in text


def test_review_object_instruction_adds_explicit_weekly_review_contract() -> None:
    text = review_object_instruction(
        "run weekly decision review and output top 3 owner actions with risk notes",
        "decision",
        "modules/decision/skills/weekly_review.md",
    )
    assert "Owner-review object contract" in text
    assert "## Owner Action Proposal" in text
    assert "do not emit the proposal block" in text


def test_review_object_instruction_marks_after_meal_story_as_output_only() -> None:
    text = review_object_instruction(
        "write an after-meal story about BTC market regime",
        "content",
        "modules/content/skills/write_after_meal_story.md",
    )
    assert "Review-object boundary" in text
    assert "draft artifact" in text
    assert "Do not append any `## Content Direction Proposal`" in text
    assert "accepted content-direction proposal" in text


def test_review_object_instruction_requires_content_direction_proposal_for_strategy_skill() -> None:
    text = review_object_instruction(
        "propose a content direction for BTC market regime",
        "content",
        "modules/content/skills/propose_content_direction.md",
    )
    assert "Owner-review object contract" in text
    assert "## Content Direction Proposal" in text
    assert "1-3 distilled bullets" in text
