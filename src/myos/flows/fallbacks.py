from __future__ import annotations


def render_fallback(mode: str) -> str:
    renderer = {
        "create": render_create_fallback,
        "decide": render_decide_fallback,
    }.get(mode)
    if renderer is not None:
        return renderer()
    return render_mode_notice(mode)


def render_create_fallback() -> str:
    return "\n".join(
        [
            "[create]",
            "MyOS reads this as creation input.",
            "Next structuring step: write the core thesis in one sentence, then list the two or three moves that should carry it.",
            "Do that before drafting full prose.",
        ]
    )


def render_decide_fallback() -> str:
    return "\n".join(
        [
            "[decide]",
            "MyOS reads this as a decision situation.",
            "Next grounding step: separate facts, constraints, options, and fears before choosing.",
            "Then note the one missing fact that would most change the answer.",
        ]
    )


def render_mode_notice(mode: str) -> str:
    prompts = {
        "review": "State the artifact and the standard you want it judged against.",
        "plan": "State the goal, the constraint, and the next irreversible step.",
        "capture": "State what should be saved and why it will matter later.",
    }
    return "\n".join(
        [
            f"[{mode}]",
            f"MyOS detected {mode} mode.",
            prompts.get(mode, "This thin slice is keeping the core intentionally small."),
        ]
    )
