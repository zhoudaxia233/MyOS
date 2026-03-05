from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from validators import append_jsonl

MEMORY_EVENTS_SCHEMA = {
    "_schema": {
        "name": "memory_events",
        "version": "1.0",
        "fields": ["id", "created_at", "status", "source_type", "event", "why_it_matters", "tags", "source_refs"],
        "notes": "append-only",
    }
}

ROLE_RE = re.compile(r"^(user|assistant|system|human|ai)\s*:\s*(.*)$", re.IGNORECASE)
KEYWORD_TAGS = {
    "decision": "decision",
    "risk": "risk",
    "review": "review",
    "pattern": "pattern",
    "alignment": "alignment",
    "goal": "alignment",
    "scope": "scope",
    "trigger": "trigger",
    "emotion": "emotion",
    "invest": "risk",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clip(text: str, limit: int = 220) -> str:
    clean = " ".join(str(text).strip().split())
    if len(clean) <= limit:
        return clean
    return clean[: max(0, limit - 3)] + "..."


def _normalize_time(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    raw = value.strip()
    if not raw:
        return None
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    except ValueError:
        return None


def _next_id(path: Path, prefix: str = "me") -> str:
    date = datetime.now(timezone.utc).strftime("%Y%m%d")
    max_seq = 0

    if path.exists() and path.is_file():
        for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            line = raw.strip()
            if not line:
                continue
            if i == 1 and '"_schema"' in line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict):
                continue
            rid = str(obj.get("id", ""))
            if not rid.startswith(f"{prefix}_{date}_"):
                continue
            tail = rid.rsplit("_", 1)[-1]
            if tail.isdigit():
                max_seq = max(max_seq, int(tail))

    return f"{prefix}_{date}_{max_seq + 1:03d}"


def _normalize_content(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            if isinstance(item, str):
                out.append(item)
                continue
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    out.append(text)
        return "\n".join(out)
    if isinstance(value, dict):
        parts = value.get("parts")
        if isinstance(parts, list):
            return _normalize_content(parts)
        text = value.get("text")
        if isinstance(text, str):
            return text
    return ""


def _as_message(raw: object) -> dict | None:
    if not isinstance(raw, dict):
        return None

    role_raw = raw.get("role") or raw.get("speaker") or raw.get("author") or raw.get("type")
    role = str(role_raw or "").strip().lower()
    if role == "human":
        role = "user"
    if role == "ai":
        role = "assistant"
    if role not in {"user", "assistant", "system"}:
        return None

    content = (
        _normalize_content(raw.get("content"))
        or _normalize_content(raw.get("text"))
        or _normalize_content(raw.get("message"))
        or _normalize_content(raw.get("body"))
    )
    content = content.strip()
    if not content:
        return None

    ts = _normalize_time(raw.get("created_at") or raw.get("timestamp") or raw.get("time") or raw.get("date"))
    return {"role": role, "content": content, "created_at": ts}


def _load_messages_from_json(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    items: list[object]
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        for key in ("messages", "conversation", "items", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                items = value
                break
        else:
            items = []
    else:
        items = []

    messages: list[dict] = []
    for item in items:
        msg = _as_message(item)
        if msg is not None:
            messages.append(msg)
    return messages


def _load_messages_from_jsonl(path: Path) -> list[dict]:
    messages: list[dict] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = _as_message(obj)
        if msg is not None:
            messages.append(msg)
    return messages


def _load_messages_from_text(path: Path) -> list[dict]:
    messages: list[dict] = []
    role = "user"
    buf: list[str] = []

    def flush() -> None:
        if not buf:
            return
        content = "\n".join(buf).strip()
        if content:
            messages.append({"role": role, "content": content, "created_at": None})
        buf.clear()

    current_role = role
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        match = ROLE_RE.match(line.strip())
        if match:
            flush()
            current_role = match.group(1).lower()
            if current_role == "human":
                current_role = "user"
            if current_role == "ai":
                current_role = "assistant"
            role = current_role if current_role in {"user", "assistant", "system"} else "user"
            remainder = match.group(2).strip()
            if remainder:
                buf.append(remainder)
            continue
        buf.append(line.strip())
    flush()
    return messages


def load_chat_messages(input_path: Path) -> list[dict]:
    if not input_path.exists() or not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    suffix = input_path.suffix.lower()
    if suffix == ".json":
        return _load_messages_from_json(input_path)
    if suffix == ".jsonl":
        return _load_messages_from_jsonl(input_path)
    return _load_messages_from_text(input_path)


def _derive_tags(text: str, extra_tags: list[str]) -> list[str]:
    tags: list[str] = ["chat", "imported"]
    lowered = text.lower()
    for keyword, tag in KEYWORD_TAGS.items():
        if keyword in lowered:
            tags.append(tag)
    tags.extend([t.strip().lower() for t in extra_tags if str(t).strip()])

    dedup: list[str] = []
    seen: set[str] = set()
    for tag in tags:
        if tag in seen:
            continue
        seen.add(tag)
        dedup.append(tag)
    return dedup[:6]


def normalize_messages_to_events(messages: list[dict], extra_tags: list[str]) -> list[dict]:
    events: list[dict] = []
    i = 0

    while i < len(messages):
        msg = messages[i]
        role = str(msg.get("role", "")).lower()
        if role != "user":
            i += 1
            continue

        user_text = str(msg.get("content", "")).strip()
        if not user_text:
            i += 1
            continue

        assistant_text = ""
        j = i + 1
        while j < len(messages):
            next_msg = messages[j]
            next_role = str(next_msg.get("role", "")).lower()
            if next_role == "user":
                break
            if next_role == "assistant":
                assistant_text = str(next_msg.get("content", "")).strip()
                break
            j += 1

        event_text = f"User: {_clip(user_text, 170)}"
        if assistant_text:
            event_text += f" | Assistant: {_clip(assistant_text, 120)}"

        created_at = _normalize_time(msg.get("created_at")) or _utc_now()
        tags = _derive_tags(user_text + " " + assistant_text, extra_tags)

        events.append(
            {
                "created_at": created_at,
                "status": "active",
                "source_type": "chat",
                "event": event_text,
                "why_it_matters": "Imported from chat export for downstream pattern extraction and weekly distillation.",
                "tags": tags,
                "source_refs": [],
            }
        )
        i = j if j > i else i + 1

    return events


def ingest_chat_export(
    repo_root: Path,
    input_path: Path,
    *,
    max_events: int = 50,
    dry_run: bool = False,
    extra_tags: list[str] | None = None,
) -> dict:
    tags = extra_tags or []
    messages = load_chat_messages(input_path)
    events = normalize_messages_to_events(messages, tags)
    if max_events > 0:
        events = events[-max_events:]

    memory_log = repo_root / "modules" / "memory" / "logs" / "memory_events.jsonl"
    if not events:
        return {
            "input_path": str(input_path),
            "message_count": len(messages),
            "event_count": 0,
            "appended_count": 0,
            "record_ids": [],
            "dry_run": dry_run,
            "preview": [],
        }

    record_ids: list[str] = []
    preview: list[dict] = []

    for event in events:
        record = dict(event)
        record["id"] = _next_id(memory_log, "me")
        record_ids.append(record["id"])
        preview.append(
            {
                "id": record["id"],
                "created_at": record["created_at"],
                "event": record["event"],
                "tags": record["tags"],
            }
        )
        if not dry_run:
            append_jsonl(memory_log, record, schema_header=MEMORY_EVENTS_SCHEMA)

    return {
        "input_path": str(input_path),
        "message_count": len(messages),
        "event_count": len(events),
        "appended_count": 0 if dry_run else len(events),
        "record_ids": record_ids,
        "dry_run": dry_run,
        "preview": preview[:5],
    }
