from prompting import (
    execution_instruction,
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
