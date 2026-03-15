from __future__ import annotations

import re

from myos.protocol import SessionRequest

_URL_RE = re.compile(r"https?://\S+")


def render_learn_response(request: SessionRequest) -> str:
    input_shape, working_frame, prompts = _classify_input(request.raw_input)
    return "\n".join(
        [
            "[learn]",
            "MyOS reads this as learning input.",
            f"Input shape: {input_shape}",
            f"Working frame: {working_frame}",
            "Next step:",
            f"- {prompts[0]}",
            f"- {prompts[1]}",
            f"- {prompts[2]}",
        ]
    )


def _classify_input(raw_input: str) -> tuple[str, str, tuple[str, str, str]]:
    stripped = raw_input.strip()
    if _URL_RE.search(stripped):
        return (
            "URL present.",
            "Treat the link as source material and start from what actually changed in your thinking.",
            (
                "Name the one idea or claim you want to extract from the source.",
                "State what specifically struck you, challenged you, or shifted your frame.",
                "Decide whether this should become a note, question, or follow-up read.",
            ),
        )
    if _looks_like_long_paste(stripped):
        return (
            "Long pasted input.",
            "This looks like source material that needs distillation, not immediate summarization.",
            (
                "Pull out the one or two claims worth keeping.",
                "Mark the passage or concept that changed how you see the topic.",
                "Turn that into a reusable note in your own words.",
            ),
        )
    return (
        "Short reflection / note.",
        "This looks like early learning reflection rather than full source material.",
        (
            "Name the idea you want to keep.",
            "Say why it matters to you now.",
            "State the next question or application this opens.",
        ),
    )


def _looks_like_long_paste(raw_input: str) -> bool:
    return (
        len(raw_input) >= 600
        or raw_input.count("\n") >= 3
        or len(raw_input.split()) >= 120
    )
