from myos.flows.guided_learn import render_learn_response
from myos.protocol import build_session_request


def _learn_request(raw_input: str) -> object:
    return build_session_request(
        raw_input=raw_input,
        source="argv",
        mode="learn",
        mode_source="heuristic",
    )


def test_render_learn_response_for_url_input() -> None:
    response = render_learn_response(_learn_request("I read this today: https://example.com/article"))
    assert "[learn]" in response
    assert "Input shape: URL present." in response
    assert "Treat the link as source material" in response


def test_render_learn_response_for_long_pasted_input() -> None:
    raw_input = "\n".join(
        [
            "Paragraph one about a surprising idea.",
            "Paragraph two extending the argument with more detail.",
            "Paragraph three showing why the argument matters.",
            "Paragraph four making the source long enough to count as pasted material.",
        ]
    )
    response = render_learn_response(_learn_request(raw_input))
    assert "Input shape: Long pasted input." in response
    assert "needs distillation" in response


def test_render_learn_response_for_short_reflection_note() -> None:
    response = render_learn_response(_learn_request("This article made me rethink how MyOS should stay thin."))
    assert "Input shape: Short reflection / note." in response
    assert "early learning reflection" in response
