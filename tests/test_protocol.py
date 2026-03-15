from pathlib import Path

from myos.protocol import build_session_request


def test_build_session_request_keeps_required_fields() -> None:
    request = build_session_request(
        raw_input="I keep thinking about this.",
        source="argv",
        mode="explore",
        mode_source="heuristic",
        cwd=Path("/tmp/myos"),
    )

    assert request.raw_input == "I keep thinking about this."
    assert request.source == "argv"
    assert request.mode == "explore"
    assert request.mode_source == "heuristic"
    assert request.cwd == "/tmp/myos"
    assert request.fallback_policy == "native_then_manual"
    assert request.session_id.startswith("session_")
