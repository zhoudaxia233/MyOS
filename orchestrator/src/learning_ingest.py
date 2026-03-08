from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from idgen import next_id_for_path
from validators import append_jsonl

MEMORY_EVENTS_SCHEMA = {
    "_schema": {
        "name": "memory_events",
        "version": "1.1",
        "fields": [
            "id",
            "created_at",
            "status",
            "source_type",
            "event",
            "why_it_matters",
            "tags",
            "source_refs",
            "object_type",
            "proposal_target",
        ],
        "notes": "append-only",
    }
}

MEMORY_INSIGHTS_SCHEMA = {
    "_schema": {
        "name": "memory_insights",
        "version": "1.1",
        "fields": [
            "id",
            "created_at",
            "status",
            "insight",
            "evidence",
            "source_refs",
            "confidence",
            "tags",
            "object_type",
            "proposal_target",
        ],
        "notes": "append-only",
    }
}

BULLET_RE = re.compile(r"^(?:[-*•]\s+|\d+[.)]\s+)")
KEYWORD_TAGS = {
    "reverse": "reverse_thinking",
    "option c": "reverse_thinking",
    "逆向": "reverse_thinking",
    "博弈": "game_thinking",
    "game": "game_thinking",
    "商业": "business_mechanism",
    "value chain": "business_mechanism",
    "机制": "business_mechanism",
    "decision": "decision",
    "决策": "decision",
    "strategy": "strategy",
    "策略": "strategy",
    "execution": "execution",
    "执行": "execution",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clip(text: str, limit: int = 260) -> str:
    clean = " ".join(str(text).strip().split())
    if len(clean) <= limit:
        return clean
    return clean[: max(0, limit - 3)] + "..."


def _load_input_text(input_path: Path) -> tuple[str, str]:
    if not input_path.exists() or not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    suffix = input_path.suffix.lower()
    text = input_path.read_text(encoding="utf-8")
    inferred_title = input_path.stem.replace("_", " ").strip()

    if suffix == ".json":
        payload = json.loads(text)
        if isinstance(payload, dict):
            inferred_title = str(payload.get("title") or payload.get("topic") or inferred_title).strip() or inferred_title
            lines: list[str] = []
            summary = payload.get("summary")
            if isinstance(summary, str) and summary.strip():
                lines.append(summary.strip())
            points = payload.get("core_points")
            if isinstance(points, list):
                for point in points:
                    if isinstance(point, str) and point.strip():
                        lines.append(f"- {point.strip()}")
            content = payload.get("content")
            if isinstance(content, str) and content.strip():
                lines.append(content.strip())
            if lines:
                text = "\n".join(lines)

    # Markdown heading as title takes precedence when available.
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("#"):
            heading = line.lstrip("#").strip()
            if heading:
                inferred_title = heading
                break

    return inferred_title or "learning asset", text


def _extract_points(text: str, max_points: int) -> list[str]:
    points: list[str] = []
    seen: set[str] = set()
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        cleaned = BULLET_RE.sub("", line).strip()
        if len(cleaned) < 12:
            continue
        norm = cleaned.lower()
        if norm in seen:
            continue
        seen.add(norm)
        points.append(cleaned)
        if len(points) >= max_points:
            break

    if points:
        return points

    chunks = re.split(r"[。！？.!?]\s*", text)
    for chunk in chunks:
        cleaned = " ".join(chunk.strip().split())
        if len(cleaned) < 12:
            continue
        norm = cleaned.lower()
        if norm in seen:
            continue
        seen.add(norm)
        points.append(cleaned)
        if len(points) >= max_points:
            break
    return points


def _derive_why_it_matters(text: str, points: list[str]) -> str:
    keys = ("why it matters", "takeaway", "总结", "感悟", "启发")
    for raw in text.splitlines():
        line = raw.strip()
        lower = line.lower()
        if any(k in lower for k in keys):
            candidate = line.split(":", 1)[-1].strip() if ":" in line else line
            if len(candidate) >= 12:
                return _clip(candidate, 220)

    if points:
        return _clip(f"Provides reusable decision and execution checks: {points[0]}", 220)
    return "Provides reusable decision and execution checks from external learning material."


def _derive_tags(text: str, source_type: str, extra_tags: list[str]) -> list[str]:
    tags: list[str] = ["learning_asset", "imported", source_type]
    lowered = text.lower()
    for keyword, tag in KEYWORD_TAGS.items():
        if keyword in lowered:
            tags.append(tag)
    tags.extend([str(tag).strip().lower() for tag in extra_tags if str(tag).strip()])

    dedup: list[str] = []
    seen: set[str] = set()
    for tag in tags:
        if tag in seen:
            continue
        seen.add(tag)
        dedup.append(tag)
    return dedup[:8]


def _build_insight(title: str, points: list[str]) -> str:
    if not points:
        return f"{title}: convert learning into explicit checks before execution."
    if len(points) == 1:
        return _clip(f"{title}: {points[0]}", 260)
    return _clip(f"{title}: {'; '.join(points[:3])}", 260)


def _ingest_learning_content(
    repo_root: Path,
    *,
    input_ref: str,
    text: str,
    title: str,
    source_type: str,
    max_points: int,
    confidence: int,
    dry_run: bool,
    extra_tags: list[str] | None,
) -> dict:
    points = _extract_points(text, max_points=max_points)
    why_it_matters = _derive_why_it_matters(text, points)
    tags = _derive_tags(text, source_type=source_type, extra_tags=extra_tags or [])
    now = _utc_now()

    events_log = repo_root / "modules" / "memory" / "logs" / "memory_events.jsonl"
    insights_log = repo_root / "modules" / "memory" / "logs" / "memory_insights.jsonl"

    event_id = next_id_for_path(events_log, "me")
    event_record = {
        "id": event_id,
        "created_at": now,
        "status": "active",
        "source_type": "external_observation",
        "event": _clip(f"Learning asset [{source_type}] {title}: {'; '.join(points[:3])}", 260),
        "why_it_matters": why_it_matters,
        "tags": tags,
        "source_refs": [],
        "object_type": "memory",
        "proposal_target": None,
    }

    insight_id = next_id_for_path(insights_log, "mi")
    insight_record = {
        "id": insight_id,
        "created_at": now,
        "status": "active",
        "insight": _build_insight(title, points),
        "evidence": points[: max(1, min(5, len(points)))],
        "source_refs": [event_id],
        "confidence": confidence,
        "tags": [tag for tag in tags if tag != "imported"][:8],
        "object_type": "memory",
        "proposal_target": None,
    }

    if not dry_run:
        append_jsonl(events_log, event_record, schema_header=MEMORY_EVENTS_SCHEMA)
        append_jsonl(insights_log, insight_record, schema_header=MEMORY_INSIGHTS_SCHEMA)

    return {
        "input_path": input_ref,
        "title": title,
        "source_type": source_type,
        "core_points_count": len(points),
        "event_count": 1,
        "insight_count": 1,
        "appended_events": 0 if dry_run else 1,
        "appended_insights": 0 if dry_run else 1,
        "record_ids": [event_id, insight_id],
        "event_ids": [event_id],
        "insight_ids": [insight_id],
        "dry_run": dry_run,
        "preview": {
            "event": {"id": event_id, "event": event_record["event"], "tags": event_record["tags"]},
            "insight": {"id": insight_id, "insight": insight_record["insight"], "confidence": confidence},
        },
    }


def ingest_learning_text(
    repo_root: Path,
    learning_text: str,
    *,
    title: str | None = None,
    source_type: str = "video",
    max_points: int = 6,
    confidence: int = 7,
    dry_run: bool = False,
    extra_tags: list[str] | None = None,
) -> dict:
    text = str(learning_text or "").strip()
    if not text:
        raise ValueError("learning_text is required")
    if max_points <= 0:
        raise ValueError("max_points must be > 0")
    if confidence < 1 or confidence > 10:
        raise ValueError("confidence must be in range 1..10")

    final_title = str(title).strip() if title is not None else ""
    if not final_title:
        first_line = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
        final_title = first_line.lstrip("#").strip()[:80] or "learning asset"

    return _ingest_learning_content(
        repo_root,
        input_ref="<inline>",
        text=text,
        title=final_title,
        source_type=source_type,
        max_points=max_points,
        confidence=confidence,
        dry_run=dry_run,
        extra_tags=extra_tags,
    )


def ingest_learning_asset(
    repo_root: Path,
    input_path: Path,
    *,
    title: str | None = None,
    source_type: str = "video",
    max_points: int = 6,
    confidence: int = 7,
    dry_run: bool = False,
    extra_tags: list[str] | None = None,
) -> dict:
    if max_points <= 0:
        raise ValueError("max_points must be > 0")
    if confidence < 1 or confidence > 10:
        raise ValueError("confidence must be in range 1..10")

    inferred_title, text = _load_input_text(input_path)
    final_title = str(title).strip() if title is not None else ""
    final_title = final_title or inferred_title
    return _ingest_learning_content(
        repo_root,
        input_ref=str(input_path),
        text=text,
        title=final_title,
        source_type=source_type,
        max_points=max_points,
        confidence=confidence,
        dry_run=dry_run,
        extra_tags=extra_tags,
    )
