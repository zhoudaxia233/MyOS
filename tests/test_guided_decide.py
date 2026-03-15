from myos.flows.guided_decide import render_decide_response
from myos.protocol import build_session_request


def _decide_request(raw_input: str) -> object:
    return build_session_request(
        raw_input=raw_input,
        source="argv",
        mode="decide",
        mode_source="heuristic",
    )


def test_render_decide_response_for_interpersonal_situation() -> None:
    response = render_decide_response(_decide_request("My landlord sent me a message and I am conflicted about how to reply."))
    assert "[decide]" in response
    assert "Situation type: Interpersonal." in response
    assert "facts and emotions" in response


def test_render_decide_response_for_financial_or_procedural_situation() -> None:
    response = render_decide_response(_decide_request("I need to decide whether to pay this fee now or wait until the contract is clarified."))
    assert "Situation type: Financial / procedural." in response
    assert "rules, money, process, or deadlines" in response


def test_render_decide_response_for_strategic_situation() -> None:
    response = render_decide_response(_decide_request("I need to decide the product direction and roadmap for this project."))
    assert "Situation type: Strategic." in response
    assert "directional choice under uncertainty" in response


def test_render_decide_response_for_ambiguous_situation() -> None:
    response = render_decide_response(_decide_request("I need to decide what to do, but I cannot yet tell what the real issue is."))
    assert "Situation type: Ambiguous." in response
    assert "structure it before trying to solve it" in response
