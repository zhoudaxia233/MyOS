from __future__ import annotations

from dataclasses import dataclass

from myos.flows.guided_explore import render_explore_response
from myos.protocol import SessionRequest


@dataclass(slots=True)
class RouteResult:
    text: str
    handler_used: str
    response_kind: str


def route_request(request: SessionRequest) -> RouteResult:
    if request.mode == "explore":
        return RouteResult(
            text=render_explore_response(request),
            handler_used="guided_explore",
            response_kind="guided_response",
        )
    if request.mode == "learn":
        return RouteResult(
            text=_render_learn_fallback(),
            handler_used="guided_fallback_learn",
            response_kind="guided_fallback",
        )
    if request.mode == "create":
        return RouteResult(
            text=_render_create_fallback(),
            handler_used="guided_fallback_create",
            response_kind="guided_fallback",
        )
    if request.mode == "decide":
        return RouteResult(
            text=_render_decide_fallback(),
            handler_used="guided_fallback_decide",
            response_kind="guided_fallback",
        )
    return RouteResult(
        text=_render_mode_notice(request.mode),
        handler_used=f"mode_notice_{request.mode}",
        response_kind="mode_notice",
    )


def _render_learn_fallback() -> str:
    return "\n".join(
        [
            "[learn]",
            "MyOS reads this as learning input.",
            "Next reflective step: identify the one idea that changed your frame, then state why it stuck.",
            "If useful, bring back the specific passage, claim, or source detail that created the shift.",
        ]
    )


def _render_create_fallback() -> str:
    return "\n".join(
        [
            "[create]",
            "MyOS reads this as creation input.",
            "Next structuring step: write the core thesis in one sentence, then list the two or three moves that should carry it.",
            "Do that before drafting full prose.",
        ]
    )


def _render_decide_fallback() -> str:
    return "\n".join(
        [
            "[decide]",
            "MyOS reads this as a decision situation.",
            "Next grounding step: separate facts, constraints, options, and fears before choosing.",
            "Then note the one missing fact that would most change the answer.",
        ]
    )


def _render_mode_notice(mode: str) -> str:
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
