from __future__ import annotations

from myos.protocol import SessionRequest


def render_explore_response(request: SessionRequest) -> str:
    signal = _infer_signal(request.raw_input)
    return "\n".join(
        [
            "[explore]",
            "MyOS reads this as exploratory thinking.",
            f"Working frame: {signal}",
            "Next step:",
            "- Name the tension or live question in one sentence.",
            "- Separate what you observed from what you inferred.",
            "- Decide whether this should become a note, open question, or project.",
        ]
    )


def _infer_signal(raw_input: str) -> str:
    lowered = raw_input.lower()
    if any(phrase in lowered for phrase in ("can't name", "cannot name", "something here", "not sure what")):
        return "The signal is present, but the shape is still unnamed."
    if any(phrase in lowered for phrase in ("keep thinking", "circling", "returning to", "stuck on")):
        return "This looks like a recurring thread rather than a one-off thought."
    if "?" in raw_input or any(word in lowered for word in ("why ", "how ", "what ")):
        return "There is a live question here; name it cleanly before you solve it."
    return "This looks like early-stage sense-making, not execution yet."
