from myos.protocol import build_session_request
from myos.router import route_request


def _request_for(mode: str, raw_input: str) -> object:
    return build_session_request(
        raw_input=raw_input,
        source="argv",
        mode=mode,
        mode_source="heuristic",
    )


def test_routes_explore_to_guided_flow() -> None:
    result = route_request(_request_for("explore", "I keep circling the same thought."))
    assert result.handler_used == "guided_explore"
    assert result.response_kind == "guided_response"
    assert "[explore]" in result.text
    assert "Working frame:" in result.text


def test_routes_learn_to_guided_fallback() -> None:
    result = route_request(_request_for("learn", "I read an article today."))
    assert result.handler_used == "guided_learn"
    assert result.response_kind == "guided_response"
    assert "Input shape:" in result.text


def test_routes_create_to_guided_fallback() -> None:
    result = route_request(_request_for("create", "I want to write an essay."))
    assert result.handler_used == "guided_fallback_create"
    assert result.response_kind == "guided_fallback"
    assert "Next structuring step:" in result.text


def test_routes_decide_to_guided_fallback() -> None:
    result = route_request(_request_for("decide", "Should I move out?"))
    assert result.handler_used == "guided_fallback_decide"
    assert result.response_kind == "guided_fallback"
    assert "Next grounding step:" in result.text


def test_routes_review_to_mode_notice() -> None:
    result = route_request(_request_for("review", "Review this diff."))
    assert result.handler_used == "mode_notice_review"
    assert result.response_kind == "mode_notice"
    assert "MyOS detected review mode." in result.text
