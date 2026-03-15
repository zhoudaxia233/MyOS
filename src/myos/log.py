from __future__ import annotations

import json
import os
from pathlib import Path

from myos.protocol import SessionRequest
from myos.router import RouteResult

_DEFAULT_LOG_PATH = Path(__file__).resolve().parents[2] / "var" / "logs" / "sessions.jsonl"


def append_session_log(
    request: SessionRequest,
    result: RouteResult,
    log_path: Path | None = None,
) -> dict[str, object]:
    target_path = log_path or resolve_log_path()
    event = build_log_event(request, result)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with target_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=True) + "\n")
    return event


def build_log_event(request: SessionRequest, result: RouteResult) -> dict[str, object]:
    return {
        "session_id": request.session_id,
        "timestamp": request.timestamp,
        "raw_input": request.raw_input,
        "detected_mode": request.mode,
        "mode_source": request.mode_source,
        "normalized_request": request.to_dict(),
        "handler_used": result.handler_used,
        "response_kind": result.response_kind,
    }


def resolve_log_path() -> Path:
    configured = os.environ.get("MYOS_LOG_PATH")
    if configured:
        return Path(configured).expanduser()
    return _DEFAULT_LOG_PATH
