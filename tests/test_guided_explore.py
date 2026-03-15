from myos.flows.guided_explore import render_explore_response
from myos.protocol import build_session_request


def test_guided_explore_response_infers_signal() -> None:
    request = build_session_request(
        raw_input="I keep thinking there is something here but I can't name it.",
        source="argv",
        mode="explore",
        mode_source="heuristic",
    )

    response = render_explore_response(request)

    assert "[explore]" in response
    assert "The signal is present, but the shape is still unnamed." in response
    assert "Next step:" in response
