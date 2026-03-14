from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cognition import log_accommodation_revision, log_schema_version
from idgen import next_id_for_rel_path

COGNITION_CANONICALIZATION_MODES = frozenset({"seed", "revision"})
COGNITION_REVISION_TYPES = frozenset({"weaken", "replace", "split", "merge", "refine"})
COGNITION_PARENT_EFFECTS = frozenset({"supersede", "narrow", "keep-alongside"})
REVISION_SUMMARY_LINEAGE_PREFIX = "Lineage justification:"
REVISION_SUMMARY_PARENT_EFFECT_PREFIX = "Parent effect:"
REVISION_SUMMARY_NOTE_PREFIX = "Ratification note:"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists() or not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        if i == 1 and '"_schema"' in line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _ordered_unique(items: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        text = str(item or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _compose_revision_summary(note: str, lineage_justification: str, parent_effect: str | None = None) -> str:
    lines = [f"{REVISION_SUMMARY_LINEAGE_PREFIX} {lineage_justification}"]
    if _optional_text(parent_effect):
        lines.append(f"{REVISION_SUMMARY_PARENT_EFFECT_PREFIX} {parent_effect}")
    lines.append(f"{REVISION_SUMMARY_NOTE_PREFIX} {note}")
    return "\n".join(lines)


def _extract_summary_segment(summary: Any, prefix: str, next_prefixes: list[str]) -> str | None:
    text = _optional_text(summary)
    if not text:
        return None
    marker = f"{prefix} "
    start = text.find(marker)
    if start < 0:
        return None
    start += len(marker)
    end = len(text)
    for next_prefix in next_prefixes:
        next_marker = f"{next_prefix} "
        idx = text.find(next_marker, start)
        if idx >= 0 and idx < end:
            end = idx
    return _optional_text(text[start:end])


def _extract_lineage_justification(summary: Any) -> str | None:
    return _extract_summary_segment(
        summary,
        REVISION_SUMMARY_LINEAGE_PREFIX,
        [REVISION_SUMMARY_PARENT_EFFECT_PREFIX, REVISION_SUMMARY_NOTE_PREFIX],
    )


def _extract_parent_effect(summary: Any) -> str | None:
    return _extract_summary_segment(summary, REVISION_SUMMARY_PARENT_EFFECT_PREFIX, [REVISION_SUMMARY_NOTE_PREFIX])


def _normalize_revision_type(revision_type: str | None) -> str:
    normalized = str(revision_type or "").strip().lower()
    if normalized not in COGNITION_REVISION_TYPES:
        allowed = ", ".join(sorted(COGNITION_REVISION_TYPES))
        raise ValueError(f"revision_type must be one of: {allowed}")
    return normalized


def _normalize_parent_effect(parent_effect: str | None) -> str:
    normalized = str(parent_effect or "").strip().lower()
    if normalized not in COGNITION_PARENT_EFFECTS:
        allowed = ", ".join(sorted(COGNITION_PARENT_EFFECTS))
        raise ValueError(f"parent_effect must be one of: {allowed}")
    return normalized


def _candidate_row_by_id(repo_root: Path, candidate_ref: str) -> dict[str, Any] | None:
    path = repo_root / "orchestrator" / "logs" / "learning_candidates.jsonl"
    for row in _read_jsonl(path):
        if str(row.get("status", "")).strip().lower() != "active":
            continue
        if str(row.get("id", "")).strip() == candidate_ref:
            return row
    return None


def _promotion_row_by_candidate(repo_root: Path, candidate_ref: str) -> dict[str, Any] | None:
    path = repo_root / "modules" / "decision" / "logs" / "learning_candidate_promotions.jsonl"
    for row in _read_jsonl(path):
        if str(row.get("status", "")).strip().lower() != "active":
            continue
        if str(row.get("candidate_ref", "")).strip() == candidate_ref:
            return row
    return None


def _cognition_sink_row_by_candidate(repo_root: Path, candidate_ref: str) -> dict[str, Any] | None:
    path = repo_root / "modules" / "cognition" / "logs" / "schema_candidates.jsonl"
    for row in _read_jsonl(path):
        if str(row.get("status", "")).strip().lower() != "active":
            continue
        if str(row.get("candidate_ref", "")).strip() == candidate_ref:
            return row
    return None


def _active_schema_versions(repo_root: Path) -> list[dict[str, Any]]:
    path = repo_root / "modules" / "cognition" / "logs" / "schema_versions.jsonl"
    return [
        row
        for row in _read_jsonl(path)
        if str(row.get("status", "")).strip().lower() == "active"
    ]


def _active_accommodation_revisions(repo_root: Path) -> list[dict[str, Any]]:
    path = repo_root / "modules" / "cognition" / "logs" / "accommodation_revisions.jsonl"
    return [
        row
        for row in _read_jsonl(path)
        if str(row.get("status", "")).strip().lower() == "active"
    ]


def cognition_revision_ratification_map(repo_root: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in _active_schema_versions(repo_root):
        refs = [str(item).strip() for item in row.get("source_refs", []) if str(item).strip()]
        for ref in refs:
            if ref.startswith("lc_"):
                out[ref] = {
                    "id": str(row.get("id", "")).strip() or None,
                    "created_at": str(row.get("created_at", "")).strip() or None,
                    "schema_version_id": str(row.get("id", "")).strip() or None,
                    "accommodation_revision_id": None,
                    "revision_type": None,
                    "canonicalization_mode": "seed",
                    "parent_schema_version_id": _optional_text(row.get("parent_schema_version_id")),
                    "parent_effect": None,
                    "lineage_justification": None,
                }
    for row in _active_accommodation_revisions(repo_root):
        refs = [str(item).strip() for item in row.get("source_refs", []) if str(item).strip()]
        for ref in refs:
            if ref.startswith("lc_"):
                out[ref] = {
                    "id": str(row.get("id", "")).strip() or None,
                    "created_at": str(row.get("created_at", "")).strip() or None,
                    "schema_version_id": str(row.get("new_schema_version_id", "")).strip() or None,
                    "accommodation_revision_id": str(row.get("id", "")).strip() or None,
                    "revision_type": str(row.get("revision_type", "")).strip() or None,
                    "canonicalization_mode": "revision",
                    "parent_schema_version_id": _optional_text(row.get("previous_schema_version_id")),
                    "parent_effect": _extract_parent_effect(row.get("revision_summary")),
                    "lineage_justification": _extract_lineage_justification(row.get("revision_summary")),
                }
    return out


def _schema_version_by_id(repo_root: Path, schema_version_id: str | None) -> dict[str, Any] | None:
    target_schema_version_id = str(schema_version_id or "").strip()
    if not target_schema_version_id:
        return None
    for row in _active_schema_versions(repo_root):
        if str(row.get("id", "")).strip() == target_schema_version_id:
            return row
    return None


def list_cognition_schema_options(repo_root: Path) -> list[dict[str, Any]]:
    def sort_key(row: dict[str, Any]) -> tuple[str, str]:
        created_at = _optional_text(row.get("created_at")) or ""
        row_id = _optional_text(row.get("id")) or ""
        return created_at, row_id

    rows = sorted(_active_schema_versions(repo_root), key=sort_key, reverse=True)
    revision_rows = _active_accommodation_revisions(repo_root)
    revision_meta_by_schema_version_id: dict[str, dict[str, Any]] = {}
    for row in revision_rows:
        schema_version_id = _optional_text(row.get("new_schema_version_id"))
        if not schema_version_id:
            continue
        revision_type = _optional_text(row.get("revision_type"))
        parent_effect = _extract_parent_effect(row.get("revision_summary"))
        if revision_type and parent_effect:
            lineage_relation = f"{revision_type}->{parent_effect}"
        elif revision_type:
            lineage_relation = revision_type
        else:
            lineage_relation = "revision"
        revision_meta_by_schema_version_id[schema_version_id] = {
            "canonicalization_mode": "revision",
            "revision_type": revision_type,
            "parent_effect": parent_effect,
            "lineage_justification": _extract_lineage_justification(row.get("revision_summary")),
            "lineage_relation": lineage_relation,
            "accommodation_revision_id": _optional_text(row.get("id")),
        }

    options: list[dict[str, Any]] = []
    for row in rows:
        option_id = _optional_text(row.get("id"))
        if not option_id:
            continue
        parent_schema_version_id = _optional_text(row.get("parent_schema_version_id"))
        revision_meta = revision_meta_by_schema_version_id.get(option_id, {})
        version_raw = row.get("version")
        try:
            version = int(version_raw)
        except (TypeError, ValueError):
            version = None
        if revision_meta:
            canonicalization_mode = "revision"
            lineage_relation = str(revision_meta.get("lineage_relation", "")).strip() or "revision"
        elif parent_schema_version_id is None:
            canonicalization_mode = "seed"
            lineage_relation = "root"
        else:
            canonicalization_mode = "revision"
            lineage_relation = "revision"
        options.append(
            {
                "id": option_id,
                "created_at": _optional_text(row.get("created_at")),
                "schema_name": _optional_text(row.get("schema_name")) or _optional_text(row.get("topic")) or option_id,
                "topic": _optional_text(row.get("topic")),
                "summary": _optional_text(row.get("summary")),
                "version": version,
                "parent_schema_version_id": parent_schema_version_id,
                "lineage_role": "root" if parent_schema_version_id is None else "revision",
                "canonicalization_mode": canonicalization_mode,
                "revision_type": _optional_text(revision_meta.get("revision_type")),
                "parent_effect": _optional_text(revision_meta.get("parent_effect")),
                "lineage_justification": _optional_text(revision_meta.get("lineage_justification")),
                "lineage_relation": lineage_relation,
                "accommodation_revision_id": _optional_text(revision_meta.get("accommodation_revision_id")),
            }
        )
    return options


def _normalize_canonicalization_mode(mode: str | None) -> str:
    normalized = str(mode or "").strip().lower()
    if normalized not in COGNITION_CANONICALIZATION_MODES:
        raise ValueError("canonicalization_mode must be one of: seed, revision")
    return normalized


def _derive_schema_assumptions(statement: str, evidence: list[str]) -> list[str]:
    return _ordered_unique([statement, *evidence[:2]])


def _derive_schema_predictions(title: str, rationale: str | None) -> list[str]:
    if str(rationale or "").strip():
        return [str(rationale).strip()]
    return [f"Applying {title} should reduce repeated cognition mismatch in future review cycles."]


def _derive_schema_boundaries(topic: str) -> list[str]:
    return [f"Use this schema only when evaluating the cognition topic '{topic}' in owner-reviewed context."]


def ratify_cognition_revision_candidate(
    repo_root: Path,
    *,
    candidate_ref: str,
    ratification_note: str,
    canonicalization_mode: str,
    parent_schema_version_id: str | None = None,
    lineage_justification: str | None = None,
    revision_type: str | None = None,
    parent_effect: str | None = None,
) -> dict[str, Any]:
    target_candidate_ref = str(candidate_ref or "").strip()
    if not target_candidate_ref:
        raise ValueError("candidate_ref is required")

    note = str(ratification_note or "").strip()
    if not note:
        raise ValueError("ratification_note is required")
    mode = _normalize_canonicalization_mode(canonicalization_mode)
    parent_schema_version = str(parent_schema_version_id or "").strip() or None
    lineage_justification_text = _optional_text(lineage_justification)
    revision_type_text = _optional_text(revision_type)
    parent_effect_text = _optional_text(parent_effect)

    candidate = _candidate_row_by_id(repo_root, target_candidate_ref)
    if candidate is None:
        raise ValueError(f"candidate not found: {target_candidate_ref}")
    if str(candidate.get("candidate_type", "")).strip() != "cognition_revision":
        raise ValueError("only promoted cognition_revision candidates can be ratified through this path")

    promotion = _promotion_row_by_candidate(repo_root, target_candidate_ref)
    if promotion is None:
        raise ValueError("cognition revision candidate must be promoted before ratification")

    sink_row = _cognition_sink_row_by_candidate(repo_root, target_candidate_ref)
    if sink_row is None:
        raise ValueError("promoted cognition revision candidate is missing cognition sink record")

    existing = cognition_revision_ratification_map(repo_root).get(target_candidate_ref)
    if existing is not None:
        raise ValueError(f"cognition revision candidate already ratified: {target_candidate_ref}")

    title = str(sink_row.get("title", "")).strip() or str(candidate.get("title", "")).strip() or "Cognition Revision"
    statement = str(sink_row.get("statement", "")).strip() or str(candidate.get("statement", "")).strip()
    if not statement:
        raise ValueError("cognition revision candidate is missing statement")

    rationale = str(candidate.get("rationale", "")).strip() or None
    evidence = [str(item).strip() for item in candidate.get("evidence", []) if str(item).strip()]
    topic = title
    source_refs = _ordered_unique(
        [
            target_candidate_ref,
            str(sink_row.get("id", "")).strip(),
            str(sink_row.get("approval_ref", "")).strip(),
            str(sink_row.get("promotion_ref", "")).strip(),
            str(promotion.get("id", "")).strip(),
            next_id_for_rel_path(repo_root, "ap", "modules/cognition/logs/schema_versions.jsonl"),
        ]
    )
    ratification_approval_ref = source_refs[-1]
    tags = ["canonicalized_learning_candidate", "cognition_revision"]

    assumptions = _derive_schema_assumptions(statement, evidence)
    predictions = _derive_schema_predictions(title, rationale)
    boundaries = _derive_schema_boundaries(topic)
    previous_schema = _schema_version_by_id(repo_root, parent_schema_version)

    if mode == "revision":
        if parent_schema_version is None:
            raise ValueError("parent_schema_version_id is required when canonicalization_mode=revision")
        if previous_schema is None:
            raise ValueError(f"parent_schema_version_id not found: {parent_schema_version}")
        if lineage_justification_text is None:
            raise ValueError("lineage_justification is required when canonicalization_mode=revision")
        if revision_type_text is None:
            raise ValueError("revision_type is required when canonicalization_mode=revision")
        revision_type_text = _normalize_revision_type(revision_type_text)
        if revision_type_text == "replace":
            if parent_effect_text is None:
                raise ValueError("parent_effect is required when revision_type=replace")
            parent_effect_text = _normalize_parent_effect(parent_effect_text)
            if parent_effect_text not in {"supersede", "keep-alongside"}:
                raise ValueError("parent_effect for revision_type=replace must be supersede or keep-alongside")
        elif revision_type_text == "weaken":
            if parent_effect_text is None:
                raise ValueError("parent_effect is required when revision_type=weaken")
            parent_effect_text = _normalize_parent_effect(parent_effect_text)
            if parent_effect_text not in {"narrow", "keep-alongside"}:
                raise ValueError("parent_effect for revision_type=weaken must be narrow or keep-alongside")
        else:
            if parent_effect_text is not None:
                raise ValueError("parent_effect applies only to revision_type=replace or revision_type=weaken")
    else:
        if parent_schema_version is not None:
            raise ValueError("parent_schema_version_id must be absent when canonicalization_mode=seed")
        if lineage_justification_text is not None:
            raise ValueError("lineage_justification applies only when canonicalization_mode=revision")
        if revision_type_text is not None:
            raise ValueError("revision_type applies only when canonicalization_mode=revision")
        if parent_effect_text is not None:
            raise ValueError("parent_effect applies only when canonicalization_mode=revision")

    accommodation_revision_id: str | None = None
    revision_type: str | None = None
    schema_record: dict[str, Any]
    canonicalized_at = _utc_now()

    if mode == "revision":
        revision_type = revision_type_text
        result = log_accommodation_revision(
            repo_root,
            topic=topic,
            previous_schema_version_id=parent_schema_version or "",
            revision_type=revision_type,
            failed_assumptions=evidence or [str(previous_schema.get("summary", "")).strip()],
            revision_summary=_compose_revision_summary(note, lineage_justification_text or "", parent_effect_text),
            new_schema_hypothesis=statement,
            create_schema_version=True,
            schema_name=title,
            schema_summary=statement,
            assumptions=assumptions,
            predictions=predictions,
            boundaries=boundaries,
            source_refs=source_refs,
            tags=tags,
        )
        revision = result["revision"]
        schema_record = result["new_schema"]
        accommodation_revision_id = str(revision.get("id", "")).strip() or None
        canonicalized_at = str(revision.get("created_at", "")).strip() or canonicalized_at
    else:
        schema_record = log_schema_version(
            repo_root,
            topic=topic,
            schema_name=title,
            summary=statement,
            assumptions=assumptions,
            predictions=predictions,
            boundaries=boundaries,
            source_refs=source_refs,
            tags=tags,
        )
        canonicalized_at = str(schema_record.get("created_at", "")).strip() or canonicalized_at

    schema_version_id = str(schema_record.get("id", "")).strip() or None
    if not schema_version_id:
        raise ValueError("cognition revision ratification did not create a schema version")

    return {
        "candidate_ref": target_candidate_ref,
        "canonicalization_ref": accommodation_revision_id or schema_version_id,
        "canonicalization_mode": mode,
        "ratification_approval_ref": ratification_approval_ref,
        "parent_schema_version_id": parent_schema_version,
        "parent_effect": parent_effect_text,
        "lineage_justification": lineage_justification_text,
        "canonical_schema_version_id": schema_version_id,
        "accommodation_revision_id": accommodation_revision_id,
        "revision_type": revision_type,
        "canonicalized_at": canonicalized_at,
        "schema_versions_path": str(repo_root / "modules" / "cognition" / "logs" / "schema_versions.jsonl"),
        "accommodation_path": str(repo_root / "modules" / "cognition" / "logs" / "accommodation_revisions.jsonl"),
        "schema_updated": True,
    }
