from __future__ import annotations

from dataclasses import dataclass

from myos.flows.fallbacks import (
    render_create_fallback,
    render_decide_fallback,
    render_learn_fallback,
    render_mode_notice,
)
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
            text=render_learn_fallback(),
            handler_used="guided_fallback_learn",
            response_kind="guided_fallback",
        )
    if request.mode == "create":
        return RouteResult(
            text=render_create_fallback(),
            handler_used="guided_fallback_create",
            response_kind="guided_fallback",
        )
    if request.mode == "decide":
        return RouteResult(
            text=render_decide_fallback(),
            handler_used="guided_fallback_decide",
            response_kind="guided_fallback",
        )
    return RouteResult(
        text=render_mode_notice(request.mode),
        handler_used=f"mode_notice_{request.mode}",
        response_kind="mode_notice",
    )
