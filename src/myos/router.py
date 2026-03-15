from __future__ import annotations

from dataclasses import dataclass

from myos.flows.fallbacks import render_fallback
from myos.flows.guided_decide import render_decide_response
from myos.flows.guided_learn import render_learn_response
from myos.flows.guided_explore import render_explore_response
from myos.protocol import SessionRequest

_REAL_FLOW_RENDERERS = {
    "explore": render_explore_response,
    "learn": render_learn_response,
    "decide": render_decide_response,
}


@dataclass(slots=True)
class RouteResult:
    text: str
    handler_used: str
    response_kind: str


def route_request(request: SessionRequest) -> RouteResult:
    renderer = _REAL_FLOW_RENDERERS.get(request.mode)
    if renderer is not None:
        return RouteResult(
            text=renderer(request),
            handler_used=f"guided_{request.mode}",
            response_kind="guided_response",
        )

    return RouteResult(
        text=render_fallback(request.mode),
        handler_used=_fallback_handler_used(request.mode),
        response_kind=_fallback_response_kind(request.mode),
    )


def _fallback_handler_used(mode: str) -> str:
    if mode in {"create"}:
        return f"guided_fallback_{mode}"
    return f"mode_notice_{mode}"


def _fallback_response_kind(mode: str) -> str:
    if mode in {"create"}:
        return "guided_fallback"
    return "mode_notice"
