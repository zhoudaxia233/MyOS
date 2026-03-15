from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


@dataclass(slots=True)
class SessionRequest:
    session_id: str
    timestamp: str
    raw_input: str
    source: str
    mode: str
    mode_source: str
    cwd: str
    fallback_policy: str = "native_then_manual"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def build_session_request(
    raw_input: str,
    source: str,
    mode: str,
    mode_source: str,
    cwd: Path | None = None,
) -> SessionRequest:
    now = datetime.now(timezone.utc)
    working_directory = cwd or Path.cwd()
    return SessionRequest(
        session_id=_new_session_id(now),
        timestamp=now.isoformat(timespec="seconds"),
        raw_input=raw_input,
        source=source,
        mode=mode,
        mode_source=mode_source,
        cwd=str(working_directory),
    )


def _new_session_id(now: datetime) -> str:
    return f"session_{now.strftime('%Y%m%dT%H%M%S')}_{uuid4().hex[:8]}"
