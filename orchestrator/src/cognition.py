from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from idgen import next_id_for_path
from validators import append_jsonl

SCHEMA_VERSIONS_SCHEMA = {
    "_schema": {
        "name": "schema_versions",
        "version": "1.0",
        "fields": [
            "id",
            "created_at",
            "status",
            "schema_id",
            "version",
            "topic",
            "schema_name",
            "summary",
            "assumptions",
            "predictions",
            "boundaries",
            "parent_schema_version_id",
            "source_refs",
            "tags",
        ],
        "notes": "append-only",
    }
}

ASSIMILATION_EVENTS_SCHEMA = {
    "_schema": {
        "name": "assimilation_events",
        "version": "1.0",
        "fields": [
            "id",
            "created_at",
            "status",
            "topic",
            "schema_version_id",
            "input_summary",
            "interpreted_as",
            "fit_score",
            "stretch_points",
            "source_refs",
            "tags",
        ],
        "notes": "append-only",
    }
}

DISEQUILIBRIUM_EVENTS_SCHEMA = {
    "_schema": {
        "name": "disequilibrium_events",
        "version": "1.0",
        "fields": [
            "id",
            "created_at",
            "status",
            "topic",
            "schema_version_id",
            "tension_score",
            "signal_types",
            "conflict_summary",
            "unresolved_questions",
            "source_refs",
            "tags",
        ],
        "notes": "append-only",
    }
}

ACCOMMODATION_REVISIONS_SCHEMA = {
    "_schema": {
        "name": "accommodation_revisions",
        "version": "1.0",
        "fields": [
            "id",
            "created_at",
            "status",
            "topic",
            "previous_schema_version_id",
            "new_schema_version_id",
            "revision_type",
            "failed_assumptions",
            "revision_summary",
            "new_schema_hypothesis",
            "source_refs",
            "tags",
        ],
        "notes": "append-only",
    }
}

EQUILIBRATION_CYCLES_SCHEMA = {
    "_schema": {
        "name": "equilibration_cycles",
        "version": "1.0",
        "fields": [
            "id",
            "created_at",
            "status",
            "topic",
            "from_schema_version_id",
            "to_schema_version_id",
            "stabilizing_tests",
            "residual_tensions",
            "coherence_score",
            "source_refs",
            "tags",
        ],
        "notes": "append-only",
    }
}

TOKEN_RE = re.compile(r"[a-z0-9_]{2,}")
CONFUSION_MARKERS = (
    "confused",
    "unclear",
    "does not fit",
    "doesn't fit",
    "mismatch",
    "contradiction",
    "not convinced",
    "feels wrong",
)
GAP_MARKERS = (
    "cannot explain",
    "can't explain",
    "unable to explain",
    "not sure why",
    "unclear why",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_iso8601(ts: str) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists() or not path.is_file():
        return []

    out: list[dict] = []
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
        if isinstance(obj, dict):
            out.append(obj)
    return out


def _flatten(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return " ".join(_flatten(v) for v in value)
    if isinstance(value, dict):
        return " ".join(_flatten(v) for v in value.values())
    return str(value)


def _clip(text: str, limit: int = 220) -> str:
    clean = " ".join(str(text).split())
    if len(clean) <= limit:
        return clean
    return clean[: max(0, limit - 3)] + "..."


def _normalize_list(items: list[str] | None) -> list[str]:
    if not items:
        return []
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        text = str(item).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _topic_tokens(topic: str) -> list[str]:
    return TOKEN_RE.findall(str(topic).lower())


def _topic_match(text: str, topic_tokens: list[str]) -> bool:
    if not topic_tokens:
        return True
    norm = str(text).lower()
    hit_count = sum(1 for token in topic_tokens if token in norm)
    required = 1 if len(topic_tokens) <= 2 else 2
    return hit_count >= required


def _slug(text: str) -> str:
    tokens = _topic_tokens(text)
    if not tokens:
        return "schema"
    return "_".join(tokens[:6])


def _schema_logs_root(repo_root: Path) -> Path:
    return repo_root / "modules" / "cognition" / "logs"


def _schema_versions_path(repo_root: Path) -> Path:
    return _schema_logs_root(repo_root) / "schema_versions.jsonl"


def _assimilation_events_path(repo_root: Path) -> Path:
    return _schema_logs_root(repo_root) / "assimilation_events.jsonl"


def _disequilibrium_events_path(repo_root: Path) -> Path:
    return _schema_logs_root(repo_root) / "disequilibrium_events.jsonl"


def _accommodation_revisions_path(repo_root: Path) -> Path:
    return _schema_logs_root(repo_root) / "accommodation_revisions.jsonl"


def _equilibration_cycles_path(repo_root: Path) -> Path:
    return _schema_logs_root(repo_root) / "equilibration_cycles.jsonl"


def _find_schema_version(repo_root: Path, schema_version_id: str) -> dict | None:
    target = str(schema_version_id).strip()
    if not target:
        return None
    for row in _load_jsonl(_schema_versions_path(repo_root)):
        if str(row.get("id", "")).strip() == target:
            return row
    return None


def _next_schema_version(repo_root: Path, schema_id: str) -> int:
    versions: list[int] = []
    for row in _load_jsonl(_schema_versions_path(repo_root)):
        if str(row.get("schema_id", "")).strip() != schema_id:
            continue
        try:
            versions.append(int(row.get("version", 0)))
        except (TypeError, ValueError):
            continue
    return max(versions, default=0) + 1


def log_schema_version(
    repo_root: Path,
    *,
    topic: str,
    schema_name: str,
    summary: str,
    assumptions: list[str] | None = None,
    predictions: list[str] | None = None,
    boundaries: list[str] | None = None,
    schema_id: str | None = None,
    parent_schema_version_id: str | None = None,
    source_refs: list[str] | None = None,
    tags: list[str] | None = None,
    status: str = "active",
) -> dict:
    topic_text = str(topic).strip()
    schema_name_text = str(schema_name).strip()
    summary_text = str(summary).strip()
    if not topic_text:
        raise ValueError("topic is required")
    if not schema_name_text:
        raise ValueError("schema_name is required")
    if not summary_text:
        raise ValueError("summary is required")

    schema_id_text = str(schema_id).strip() if schema_id is not None else ""
    if not schema_id_text:
        schema_id_text = f"sm_{_slug(schema_name_text or topic_text)}"

    path = _schema_versions_path(repo_root)
    record = {
        "id": next_id_for_path(path, "sv"),
        "created_at": _utc_now(),
        "status": status,
        "schema_id": schema_id_text,
        "version": _next_schema_version(repo_root, schema_id_text),
        "topic": topic_text,
        "schema_name": schema_name_text,
        "summary": _clip(summary_text, 320),
        "assumptions": _normalize_list(assumptions),
        "predictions": _normalize_list(predictions),
        "boundaries": _normalize_list(boundaries),
        "parent_schema_version_id": str(parent_schema_version_id).strip() or None,
        "source_refs": _normalize_list(source_refs),
        "tags": _normalize_list(tags),
    }
    append_jsonl(path, record, schema_header=SCHEMA_VERSIONS_SCHEMA)
    return record


def log_assimilation_event(
    repo_root: Path,
    *,
    topic: str,
    schema_version_id: str,
    input_summary: str,
    interpreted_as: str,
    fit_score: int,
    stretch_points: list[str] | None = None,
    source_refs: list[str] | None = None,
    tags: list[str] | None = None,
    status: str = "active",
) -> dict:
    topic_text = str(topic).strip()
    schema_version_id_text = str(schema_version_id).strip()
    input_summary_text = str(input_summary).strip()
    interpreted_as_text = str(interpreted_as).strip()
    if not topic_text:
        raise ValueError("topic is required")
    if not schema_version_id_text:
        raise ValueError("schema_version_id is required")
    if not input_summary_text:
        raise ValueError("input_summary is required")
    if not interpreted_as_text:
        raise ValueError("interpreted_as is required")
    if fit_score < 1 or fit_score > 10:
        raise ValueError("fit_score must be in range 1..10")
    if _find_schema_version(repo_root, schema_version_id_text) is None:
        raise ValueError(f"schema_version_id not found: {schema_version_id_text}")

    path = _assimilation_events_path(repo_root)
    record = {
        "id": next_id_for_path(path, "as"),
        "created_at": _utc_now(),
        "status": status,
        "topic": topic_text,
        "schema_version_id": schema_version_id_text,
        "input_summary": _clip(input_summary_text, 320),
        "interpreted_as": _clip(interpreted_as_text, 320),
        "fit_score": int(fit_score),
        "stretch_points": _normalize_list(stretch_points),
        "source_refs": _normalize_list(source_refs),
        "tags": _normalize_list(tags),
    }
    append_jsonl(path, record, schema_header=ASSIMILATION_EVENTS_SCHEMA)
    return record


def _in_window(record: dict, cutoff: datetime) -> bool:
    created = _parse_iso8601(str(record.get("created_at", "")))
    if created is None:
        return False
    return created >= cutoff


def _signal_entry(signal_type: str, record: dict, note: str) -> dict:
    return {
        "signal_type": signal_type,
        "record_id": str(record.get("id", "")).strip(),
        "note": _clip(note, 200),
    }


def _build_unresolved_questions(type_counts: Counter[str]) -> list[str]:
    questions: list[str] = []
    if type_counts.get("prediction_failure", 0) > 0:
        questions.append("Which assumption repeatedly fails to predict outcomes in this topic?")
    if type_counts.get("guardrail_block", 0) > 0:
        questions.append("Is the model missing required constraints or only missing process discipline?")
    if type_counts.get("emotional_friction", 0) > 0:
        questions.append("Which interpretation step is driving emotional load and risk distortion?")
    if type_counts.get("explicit_confusion", 0) > 0:
        questions.append("What distinction is absent in the current schema, causing repeated confusion?")
    if type_counts.get("explanatory_gap", 0) > 0:
        questions.append("What mechanism remains unexplained by the current schema?")
    if not questions:
        questions.append("No strong unresolved tension detected in the selected window.")
    return questions[:5]


def _collect_disequilibrium_signals(repo_root: Path, topic: str, window_days: int) -> list[dict]:
    tokens = _topic_tokens(topic)
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
    signals: list[dict] = []

    failures = _load_jsonl(repo_root / "modules/decision/logs/failures.jsonl")
    for row in failures:
        if not _in_window(row, cutoff):
            continue
        text = _flatten(row)
        if not _topic_match(text, tokens):
            continue
        note = str(row.get("root_cause", "")).strip() or str(row.get("what_happened", "")).strip()
        signals.append(_signal_entry("prediction_failure", row, note))

    gate_checks = _load_jsonl(repo_root / "modules/decision/logs/decision_gate_checks.jsonl")
    for row in gate_checks:
        if not _in_window(row, cutoff):
            continue
        if str(row.get("gate_status", "")).strip().lower() != "blocked":
            continue
        text = _flatten(row)
        if not _topic_match(text, tokens):
            continue
        note = ", ".join(str(v).strip() for v in row.get("violations", []) if str(v).strip())
        if not note:
            note = str(row.get("decision", "")).strip()
        signals.append(_signal_entry("guardrail_block", row, note or "Decision gate blocked."))

    trigger_events = _load_jsonl(repo_root / "modules/profile/logs/trigger_events.jsonl")
    for row in trigger_events:
        if not _in_window(row, cutoff):
            continue
        if int(row.get("emotional_weight", 0) or 0) < 7:
            continue
        text = _flatten(row)
        if not _topic_match(text, tokens):
            continue
        note = str(row.get("trigger_signal", "")).strip() or str(row.get("context", "")).strip()
        signals.append(_signal_entry("emotional_friction", row, note))

    psych_observations = _load_jsonl(repo_root / "modules/profile/logs/psych_observations.jsonl")
    for row in psych_observations:
        if not _in_window(row, cutoff):
            continue
        if int(row.get("confidence", 0) or 0) < 8:
            continue
        text = _flatten(row)
        if not _topic_match(text, tokens):
            continue
        note = str(row.get("observation", "")).strip() or "High-confidence psych friction signal."
        signals.append(_signal_entry("emotional_friction", row, note))

    memory_events = _load_jsonl(repo_root / "modules/memory/logs/memory_events.jsonl")
    for row in memory_events:
        if not _in_window(row, cutoff):
            continue
        text = _flatten(row)
        if not _topic_match(text, tokens):
            continue
        lowered = text.lower()
        if any(marker in lowered for marker in CONFUSION_MARKERS):
            note = str(row.get("event", "")).strip() or str(row.get("why_it_matters", "")).strip()
            signals.append(_signal_entry("explicit_confusion", row, note))

    memory_insights = _load_jsonl(repo_root / "modules/memory/logs/memory_insights.jsonl")
    for row in memory_insights:
        if not _in_window(row, cutoff):
            continue
        text = _flatten(row)
        if not _topic_match(text, tokens):
            continue
        lowered = text.lower()
        if any(marker in lowered for marker in GAP_MARKERS):
            note = str(row.get("insight", "")).strip()
            signals.append(_signal_entry("explanatory_gap", row, note))

    dedup: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for item in signals:
        key = (str(item.get("signal_type", "")), str(item.get("record_id", "")))
        if key in seen:
            continue
        seen.add(key)
        dedup.append(item)
    return dedup


def detect_disequilibrium(
    repo_root: Path,
    *,
    topic: str,
    window_days: int = 30,
    schema_version_id: str | None = None,
    source_refs: list[str] | None = None,
    tags: list[str] | None = None,
    status: str = "active",
) -> dict:
    topic_text = str(topic).strip()
    if not topic_text:
        raise ValueError("topic is required")
    if window_days <= 0:
        raise ValueError("window_days must be > 0")

    schema_version_id_text = str(schema_version_id).strip() if schema_version_id is not None else ""
    if schema_version_id_text and _find_schema_version(repo_root, schema_version_id_text) is None:
        raise ValueError(f"schema_version_id not found: {schema_version_id_text}")

    signals = _collect_disequilibrium_signals(repo_root, topic_text, window_days)
    type_counts: Counter[str] = Counter(str(s.get("signal_type", "")) for s in signals if s.get("signal_type"))
    signal_types = sorted(type_counts.keys())

    signal_count = len(signals)
    unique_type_count = len(signal_types)
    if signal_count == 0:
        tension_score = 1
        conflict_summary = "Low signal window: no strong disequilibrium evidence for the selected topic."
    else:
        raw_score = 1.0 + signal_count * 1.25 + unique_type_count * 1.1
        tension_score = int(max(1, min(10, round(raw_score))))
        top = ", ".join(f"{k}:{v}" for k, v in type_counts.most_common(3))
        conflict_summary = f"Detected {signal_count} tension signals across {unique_type_count} classes ({top})."

    unresolved = _build_unresolved_questions(type_counts)
    merged_refs = [str(s.get("record_id", "")).strip() for s in signals if str(s.get("record_id", "")).strip()]
    merged_refs.extend(_normalize_list(source_refs))
    merged_refs = _normalize_list(merged_refs)

    path = _disequilibrium_events_path(repo_root)
    record = {
        "id": next_id_for_path(path, "dq"),
        "created_at": _utc_now(),
        "status": status,
        "topic": topic_text,
        "schema_version_id": schema_version_id_text or None,
        "tension_score": tension_score,
        "signal_types": signal_types,
        "conflict_summary": conflict_summary,
        "unresolved_questions": unresolved,
        "source_refs": merged_refs,
        "tags": _normalize_list(tags),
    }
    append_jsonl(path, record, schema_header=DISEQUILIBRIUM_EVENTS_SCHEMA)
    return {
        "record": record,
        "signals": signals,
        "type_counts": dict(type_counts),
        "window_days": window_days,
    }


def render_disequilibrium_report(result: dict) -> str:
    record = result["record"]
    signals = result.get("signals", [])
    type_counts = result.get("type_counts", {})
    window_days = int(result.get("window_days", 30))

    lines = [
        "# Disequilibrium Report",
        "",
        f"- Event ID: {record['id']}",
        f"- Topic: {record['topic']}",
        f"- Window: last {window_days} days",
        f"- Tension score: {record['tension_score']}/10",
        f"- Linked schema version: {record.get('schema_version_id') or 'n/a'}",
        "",
        "## Signal Summary",
        "",
        f"- Conflict summary: {record['conflict_summary']}",
    ]

    if type_counts:
        for key in sorted(type_counts.keys()):
            lines.append(f"- {key}: {type_counts[key]}")
    else:
        lines.append("- No classified signals in this window.")

    lines.extend(
        [
            "",
            "## Unresolved Questions",
            "",
        ]
    )
    for q in record.get("unresolved_questions", []):
        lines.append(f"- {q}")

    lines.extend(
        [
            "",
            "## Source Signals",
            "",
        ]
    )
    if signals:
        for item in signals[:30]:
            lines.append(f"- [{item['signal_type']}] {item.get('record_id')}: {item.get('note')}")
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "## Suggested Next Step",
            "",
            "- If tension score >= 6, run `log-accommodation` with failed assumptions from top signals.",
            "- If tension score < 6, continue assimilation logging and recheck next cycle.",
            "",
        ]
    )
    return "\n".join(lines)


def log_accommodation_revision(
    repo_root: Path,
    *,
    topic: str,
    previous_schema_version_id: str,
    revision_type: str,
    failed_assumptions: list[str] | None,
    revision_summary: str,
    new_schema_hypothesis: str,
    create_schema_version: bool = True,
    schema_id: str | None = None,
    schema_name: str | None = None,
    schema_summary: str | None = None,
    assumptions: list[str] | None = None,
    predictions: list[str] | None = None,
    boundaries: list[str] | None = None,
    source_refs: list[str] | None = None,
    tags: list[str] | None = None,
    status: str = "active",
) -> dict:
    topic_text = str(topic).strip()
    previous_id = str(previous_schema_version_id).strip()
    revision_type_text = str(revision_type).strip().lower()
    revision_summary_text = str(revision_summary).strip()
    hypothesis_text = str(new_schema_hypothesis).strip()
    if not topic_text:
        raise ValueError("topic is required")
    if not previous_id:
        raise ValueError("previous_schema_version_id is required")
    if not revision_type_text:
        raise ValueError("revision_type is required")
    if revision_type_text not in {"weaken", "replace", "split", "merge", "refine"}:
        raise ValueError("revision_type must be one of: weaken, replace, split, merge, refine")
    if not revision_summary_text:
        raise ValueError("revision_summary is required")
    if not hypothesis_text:
        raise ValueError("new_schema_hypothesis is required")

    previous_schema = _find_schema_version(repo_root, previous_id)
    if previous_schema is None:
        raise ValueError(f"previous_schema_version_id not found: {previous_id}")

    new_schema_record: dict | None = None
    if create_schema_version:
        resolved_schema_id = str(schema_id).strip() if schema_id else str(previous_schema.get("schema_id", "")).strip()
        resolved_name = str(schema_name).strip() if schema_name else str(previous_schema.get("schema_name", "")).strip()
        resolved_summary = str(schema_summary).strip() if schema_summary else revision_summary_text
        resolved_assumptions = assumptions if assumptions else list(previous_schema.get("assumptions", []))
        resolved_predictions = predictions if predictions else list(previous_schema.get("predictions", []))
        resolved_boundaries = boundaries if boundaries else list(previous_schema.get("boundaries", []))
        new_schema_record = log_schema_version(
            repo_root,
            topic=topic_text,
            schema_name=resolved_name or f"{topic_text} revised schema",
            summary=resolved_summary,
            assumptions=resolved_assumptions,
            predictions=resolved_predictions,
            boundaries=resolved_boundaries,
            schema_id=resolved_schema_id or None,
            parent_schema_version_id=previous_id,
            source_refs=source_refs,
            tags=tags,
            status=status,
        )

    path = _accommodation_revisions_path(repo_root)
    record = {
        "id": next_id_for_path(path, "ar"),
        "created_at": _utc_now(),
        "status": status,
        "topic": topic_text,
        "previous_schema_version_id": previous_id,
        "new_schema_version_id": new_schema_record["id"] if new_schema_record else None,
        "revision_type": revision_type_text,
        "failed_assumptions": _normalize_list(failed_assumptions),
        "revision_summary": _clip(revision_summary_text, 320),
        "new_schema_hypothesis": _clip(hypothesis_text, 320),
        "source_refs": _normalize_list(source_refs),
        "tags": _normalize_list(tags),
    }
    append_jsonl(path, record, schema_header=ACCOMMODATION_REVISIONS_SCHEMA)
    return {"revision": record, "new_schema": new_schema_record}


def log_equilibration_cycle(
    repo_root: Path,
    *,
    topic: str,
    from_schema_version_id: str,
    to_schema_version_id: str,
    stabilizing_tests: list[str] | None,
    residual_tensions: list[str] | None,
    coherence_score: int,
    source_refs: list[str] | None = None,
    tags: list[str] | None = None,
    status: str = "active",
) -> dict:
    topic_text = str(topic).strip()
    from_id = str(from_schema_version_id).strip()
    to_id = str(to_schema_version_id).strip()
    if not topic_text:
        raise ValueError("topic is required")
    if not from_id:
        raise ValueError("from_schema_version_id is required")
    if not to_id:
        raise ValueError("to_schema_version_id is required")
    if coherence_score < 1 or coherence_score > 10:
        raise ValueError("coherence_score must be in range 1..10")
    if _find_schema_version(repo_root, from_id) is None:
        raise ValueError(f"from_schema_version_id not found: {from_id}")
    if _find_schema_version(repo_root, to_id) is None:
        raise ValueError(f"to_schema_version_id not found: {to_id}")

    path = _equilibration_cycles_path(repo_root)
    record = {
        "id": next_id_for_path(path, "eq"),
        "created_at": _utc_now(),
        "status": status,
        "topic": topic_text,
        "from_schema_version_id": from_id,
        "to_schema_version_id": to_id,
        "stabilizing_tests": _normalize_list(stabilizing_tests),
        "residual_tensions": _normalize_list(residual_tensions),
        "coherence_score": int(coherence_score),
        "source_refs": _normalize_list(source_refs),
        "tags": _normalize_list(tags),
    }
    append_jsonl(path, record, schema_header=EQUILIBRATION_CYCLES_SCHEMA)
    return record


def build_cognitive_timeline(
    repo_root: Path,
    *,
    topic: str | None = None,
    window_days: int = 90,
) -> dict:
    if window_days <= 0:
        raise ValueError("window_days must be > 0")

    topic_text = str(topic).strip()
    topic_tokens = _topic_tokens(topic_text)
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)

    events: list[dict] = []

    def include_row(row: dict) -> bool:
        if not _in_window(row, cutoff):
            return False
        if not topic_text:
            return True
        text = " ".join(
            [
                str(row.get("topic", "")),
                str(row.get("schema_name", "")),
                str(row.get("summary", "")),
                _flatten(row),
            ]
        )
        return _topic_match(text, topic_tokens)

    def created(row: dict) -> str:
        return str(row.get("created_at", "")).strip()

    for row in _load_jsonl(_schema_versions_path(repo_root)):
        if not include_row(row):
            continue
        events.append(
            {
                "created_at": created(row),
                "event_type": "schema_version",
                "id": str(row.get("id", "")).strip(),
                "topic": str(row.get("topic", "")).strip(),
                "summary": f"Schema v{row.get('version', '?')} {row.get('schema_name', '')}: {row.get('summary', '')}",
                "source_refs": _normalize_list(row.get("source_refs", [])),
            }
        )

    for row in _load_jsonl(_disequilibrium_events_path(repo_root)):
        if not include_row(row):
            continue
        events.append(
            {
                "created_at": created(row),
                "event_type": "disequilibrium",
                "id": str(row.get("id", "")).strip(),
                "topic": str(row.get("topic", "")).strip(),
                "summary": f"Tension {row.get('tension_score', '?')}/10: {row.get('conflict_summary', '')}",
                "source_refs": _normalize_list(row.get("source_refs", [])),
            }
        )

    for row in _load_jsonl(_accommodation_revisions_path(repo_root)):
        if not include_row(row):
            continue
        events.append(
            {
                "created_at": created(row),
                "event_type": "accommodation",
                "id": str(row.get("id", "")).strip(),
                "topic": str(row.get("topic", "")).strip(),
                "summary": f"{row.get('revision_type', '')}: {row.get('revision_summary', '')}",
                "source_refs": _normalize_list(row.get("source_refs", [])),
            }
        )

    for row in _load_jsonl(_equilibration_cycles_path(repo_root)):
        if not include_row(row):
            continue
        events.append(
            {
                "created_at": created(row),
                "event_type": "equilibration",
                "id": str(row.get("id", "")).strip(),
                "topic": str(row.get("topic", "")).strip(),
                "summary": f"Coherence {row.get('coherence_score', '?')}/10 from {row.get('from_schema_version_id')} to {row.get('to_schema_version_id')}",
                "source_refs": _normalize_list(row.get("source_refs", [])),
            }
        )

    events.sort(
        key=lambda event: (_parse_iso8601(str(event.get("created_at", ""))) or datetime.min.replace(tzinfo=timezone.utc))
    )
    type_counts = Counter(str(event.get("event_type", "")) for event in events)

    unresolved: list[dict] = []
    for event in events:
        if event["event_type"] != "disequilibrium":
            continue
        # Keep only high-tension events as unresolved candidates.
        match = re.search(r"Tension\s+([0-9]+)/10", event["summary"])
        if not match:
            continue
        if int(match.group(1)) < 6:
            continue
        unresolved.append({"id": event["id"], "summary": event["summary"]})

    return {
        "generated_at": _utc_now(),
        "window_days": window_days,
        "topic": topic_text or None,
        "counts": {
            "events": len(events),
            "schema_version": type_counts.get("schema_version", 0),
            "disequilibrium": type_counts.get("disequilibrium", 0),
            "accommodation": type_counts.get("accommodation", 0),
            "equilibration": type_counts.get("equilibration", 0),
        },
        "events": events,
        "unresolved_high_tension": unresolved[:10],
    }


def render_cognitive_timeline(snapshot: dict) -> str:
    lines = [
        "# Cognitive Evolution Timeline",
        "",
        f"- Generated at: {snapshot['generated_at']}",
        f"- Window: last {snapshot['window_days']} days",
        f"- Topic filter: {snapshot.get('topic') or 'all'}",
        "",
        "## Event Counts",
        "",
        f"- total events: {snapshot['counts']['events']}",
        f"- schema versions: {snapshot['counts']['schema_version']}",
        f"- disequilibrium events: {snapshot['counts']['disequilibrium']}",
        f"- accommodation revisions: {snapshot['counts']['accommodation']}",
        f"- equilibration cycles: {snapshot['counts']['equilibration']}",
        "",
        "## Timeline",
        "",
    ]

    events = snapshot.get("events", [])
    if not events:
        lines.append("- No cognition events in this window.")
    else:
        for event in events:
            lines.append(
                f"- {event['created_at']} [{event['event_type']}] {event['id']} | topic={event.get('topic') or 'n/a'}"
            )
            lines.append(f"  {event['summary']}")
            refs = event.get("source_refs", [])
            if refs:
                lines.append(f"  source_refs={','.join(refs)}")

    lines.extend(
        [
            "",
            "## Unresolved High-Tension Events",
            "",
        ]
    )
    unresolved = snapshot.get("unresolved_high_tension", [])
    if not unresolved:
        lines.append("- None.")
    else:
        for item in unresolved:
            lines.append(f"- {item['id']}: {item['summary']}")

    lines.append("")
    return "\n".join(lines)
