from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from idgen import next_id_for_rel_path
from learning_ingest import ingest_learning_text
from validators import append_jsonl

LEARNING_IMPORTS_SCHEMA = {
    "_schema": {
        "name": "learning_imports",
        "version": "1.0",
        "fields": [
            "id",
            "created_at",
            "status",
            "ingest_mode",
            "source_type",
            "source_ref",
            "title",
            "summary",
            "key_points",
            "raw_payload_hash",
            "source_refs",
            "candidate_count",
            "object_type",
            "proposal_target",
        ],
        "notes": "append-only",
    }
}

LEARNING_CANDIDATES_SCHEMA = {
    "_schema": {
        "name": "learning_candidates",
        "version": "1.0",
        "fields": [
            "id",
            "created_at",
            "status",
            "candidate_type",
            "candidate_state",
            "title",
            "statement",
            "rationale",
            "evidence",
            "confidence",
            "source_refs",
            "source_material_ref",
            "approval_ref",
            "owner_decision",
            "object_type",
            "proposal_target",
        ],
        "notes": "append-only",
    }
}

LEARNING_CANDIDATE_VERDICTS_SCHEMA = {
    "_schema": {
        "name": "learning_candidate_verdicts",
        "version": "1.0",
        "fields": [
            "id",
            "created_at",
            "status",
            "candidate_ref",
            "verdict",
            "owner_note",
            "modified_statement",
            "replacement_candidate_ref",
            "source_refs",
            "object_type",
            "proposal_target",
        ],
        "notes": "append-only",
    }
}

LEARNING_CANDIDATE_APPROVALS_SCHEMA = {
    "_schema": {
        "name": "learning_candidate_approvals",
        "version": "1.0",
        "fields": [
            "id",
            "created_at",
            "status",
            "candidate_ref",
            "approval_note",
            "source_refs",
            "object_type",
            "proposal_target",
        ],
        "notes": "append-only",
    }
}

LEARNING_CANDIDATE_PROMOTIONS_SCHEMA = {
    "_schema": {
        "name": "learning_candidate_promotions",
        "version": "1.0",
        "fields": [
            "id",
            "created_at",
            "status",
            "candidate_ref",
            "candidate_type",
            "promotion_target",
            "approval_ref",
            "promotion_note",
            "source_refs",
            "object_type",
            "proposal_target",
        ],
        "notes": "append-only",
    }
}

FENCED_JSON_RE = re.compile(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", re.IGNORECASE)

CANDIDATE_SECTION_KEYS = {
    "insight": ["insights", "insight_candidates"],
    "rule": ["rules", "rule_candidates"],
    "skill": ["skills", "skill_candidates"],
    "principle": ["principles", "principle_candidates"],
    "cognition_revision": ["cognition_revisions", "schema_revisions", "schema_candidates"],
}

PROPOSAL_TARGET_BY_TYPE = {
    "insight": "memory",
    "rule": "decision",
    "skill": "system",
    "principle": "principle",
    "cognition_revision": "cognition",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clip(value: Any, limit: int = 260) -> str:
    text = " ".join(str(value or "").strip().split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)] + "..."


def _coerce_list(value: Any, *, max_items: int, max_len: int) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        items = [value]
    elif isinstance(value, list):
        items = value
    else:
        items = [value]

    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        text = _clip(item, max_len)
        if not text:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(text)
        if len(out) >= max_items:
            break
    return out


def _coerce_confidence(value: Any, *, default: int = 7) -> int:
    if isinstance(value, float):
        if 0.0 <= value <= 1.0:
            return max(1, min(10, int(round(value * 10))))
    try:
        ivalue = int(value)
    except (TypeError, ValueError):
        return default
    return max(1, min(10, ivalue))


def _parse_json_payload(raw: str) -> dict[str, Any]:
    text = str(raw or "").strip()
    if not text:
        raise ValueError("response_text is required")

    try:
        payload = json.loads(text)
        if isinstance(payload, dict):
            return payload
    except json.JSONDecodeError:
        pass

    for match in FENCED_JSON_RE.finditer(text):
        block = match.group(1).strip()
        try:
            payload = json.loads(block)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload

    first = text.find("{")
    last = text.rfind("}")
    if first >= 0 and last > first:
        block = text[first : last + 1]
        try:
            payload = json.loads(block)
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            pass

    raise ValueError("Could not parse a JSON object from response_text")


def _extract_candidate_sections(payload: dict[str, Any]) -> dict[str, Any]:
    sections = payload.get("candidate_artifacts")
    if not isinstance(sections, dict):
        sections = payload.get("artifacts")
    if isinstance(sections, dict):
        return sections
    return {}


def _candidate_statement_from_dict(item: dict[str, Any]) -> str:
    for key in [
        "statement",
        "insight",
        "rule",
        "principle",
        "revision",
        "proposal",
        "summary",
        "description",
        "change",
    ]:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return _clip(value, 320)
    return ""


def _normalize_candidate_item(item: Any, candidate_type: str) -> dict[str, Any] | None:
    if isinstance(item, str):
        statement = _clip(item, 320)
        if not statement:
            return None
        return {
            "candidate_type": candidate_type,
            "title": _clip(statement, 96),
            "statement": statement,
            "rationale": None,
            "evidence": [],
            "confidence": 7,
        }

    if not isinstance(item, dict):
        return None

    title = _clip(item.get("title") or item.get("name") or item.get("skill_name") or "", 96)
    statement = _candidate_statement_from_dict(item)
    rationale = _clip(
        item.get("rationale")
        or item.get("why")
        or item.get("when_to_apply")
        or item.get("trigger")
        or item.get("scope")
        or "",
        220,
    )
    evidence = _coerce_list(item.get("evidence") or item.get("signals") or item.get("examples"), max_items=6, max_len=200)
    confidence = _coerce_confidence(item.get("confidence"), default=7)

    if not statement and title:
        statement = title
    if not statement:
        return None
    if not title:
        title = _clip(statement, 96)

    return {
        "candidate_type": candidate_type,
        "title": title,
        "statement": statement,
        "rationale": rationale or None,
        "evidence": evidence,
        "confidence": confidence,
    }


def _normalize_payload(
    payload: dict[str, Any],
    *,
    fallback_source_ref: str | None,
    fallback_title: str | None,
    fallback_source_type: str | None,
) -> dict[str, Any]:
    source = payload.get("source")
    source_obj = source if isinstance(source, dict) else {}

    source_ref = _clip(
        source_obj.get("url")
        or source_obj.get("source_ref")
        or payload.get("source_ref")
        or fallback_source_ref
        or "<external_material>",
        500,
    )
    title = _clip(
        source_obj.get("title") or payload.get("title") or payload.get("material_title") or fallback_title or "learning handoff material",
        120,
    )
    source_type = _clip(
        source_obj.get("source_type")
        or source_obj.get("type")
        or payload.get("source_type")
        or fallback_source_type
        or "external",
        32,
    ).lower()
    summary = _clip(payload.get("summary") or payload.get("material_summary") or payload.get("synthesis") or "", 1200)
    key_points = _coerce_list(
        payload.get("key_points") or payload.get("core_points") or payload.get("highlights"),
        max_items=12,
        max_len=240,
    )

    sections = _extract_candidate_sections(payload)
    candidates: list[dict[str, Any]] = []
    for candidate_type, keys in CANDIDATE_SECTION_KEYS.items():
        raw_items: Any = []
        for key in keys:
            if key in sections:
                raw_items = sections.get(key)
                break
            if key in payload:
                raw_items = payload.get(key)
                break
        if isinstance(raw_items, dict):
            raw_items = [raw_items]
        if not isinstance(raw_items, list):
            continue
        for item in raw_items[:8]:
            candidate = _normalize_candidate_item(item, candidate_type)
            if candidate is not None:
                candidates.append(candidate)

    return {
        "source_ref": source_ref,
        "title": title,
        "source_type": source_type,
        "summary": summary,
        "key_points": key_points,
        "candidates": candidates,
    }


def _compose_memory_text(payload: dict[str, Any]) -> str:
    lines: list[str] = [f"# {payload['title']}"]
    if payload["summary"]:
        lines.extend(["", payload["summary"]])
    if payload["key_points"]:
        lines.append("")
        for point in payload["key_points"]:
            lines.append(f"- {point}")
    return "\n".join(lines).strip()


def build_learning_handoff_packet(
    source_ref: str,
    *,
    title: str | None = None,
    source_type: str | None = None,
    owner_goal: str | None = None,
    max_candidates_per_type: int = 3,
) -> dict[str, Any]:
    source = _clip(source_ref, 500)
    if not source:
        raise ValueError("source_ref is required")

    normalized_title = _clip(title or "learning material", 120)
    normalized_type = _clip(source_type or "external", 32).lower()
    goal = _clip(
        owner_goal or "Extract candidate cyber-self artifacts with evidence and uncertainty markers.",
        320,
    )
    cap = max(1, min(8, int(max_candidates_per_type)))

    response_schema = {
        "source": {
            "title": "<string>",
            "url": "<string>",
            "source_type": "<video|podcast|article|book|conversation|notes>",
        },
        "summary": "<120-300 words>",
        "key_points": ["<point_1>", "<point_2>"],
        "candidate_artifacts": {
            "insights": [
                {
                    "title": "<short label>",
                    "statement": "<candidate insight>",
                    "evidence": ["<evidence_1>", "<evidence_2>"],
                    "confidence": 0.0,
                }
            ],
            "rules": [
                {
                    "title": "<rule label>",
                    "rule": "<if/then style rule>",
                    "when_to_apply": "<boundary>",
                    "evidence": ["<evidence_1>", "<evidence_2>"],
                    "confidence": 0.0,
                }
            ],
            "skills": [
                {
                    "name": "<skill name>",
                    "description": "<what this skill does>",
                    "trigger": "<when to use>",
                    "steps": ["<step_1>", "<step_2>"],
                    "evidence": ["<evidence_1>", "<evidence_2>"],
                    "confidence": 0.0,
                }
            ],
            "principles": [
                {
                    "title": "<principle label>",
                    "principle": "<durable principle statement>",
                    "scope": "<where it applies>",
                    "evidence": ["<evidence_1>", "<evidence_2>"],
                    "confidence": 0.0,
                }
            ],
            "cognition_revisions": [
                {
                    "title": "<schema revision label>",
                    "change": "<what schema should be revised>",
                    "signals": ["<signal_1>", "<signal_2>"],
                    "evidence": ["<evidence_1>", "<evidence_2>"],
                    "confidence": 0.0,
                }
            ],
        },
    }

    prompt_lines = [
        "[BEGIN MYOS LEARNING HANDOFF PACKET]",
        f"source_ref: {source}",
        f"title_hint: {normalized_title}",
        f"source_type_hint: {normalized_type}",
        f"owner_goal: {goal}",
        "task: analyze the source and produce candidate artifacts for owner-reviewed promotion.",
        "constraints:",
        "- keep claims evidence-linked and mark uncertainty explicitly.",
        f"- return at most {cap} candidates per artifact type.",
        "- return valid JSON only, no markdown.",
        "required_response_schema:",
        json.dumps(response_schema, ensure_ascii=True, indent=2),
        "[END MYOS LEARNING HANDOFF PACKET]",
    ]

    return {
        "source_ref": source,
        "title_hint": normalized_title,
        "source_type_hint": normalized_type,
        "max_candidates_per_type": cap,
        "packet_text": "\n".join(prompt_lines),
    }


def ingest_learning_handoff_response(
    repo_root: Path,
    response_text: str,
    *,
    source_ref: str | None = None,
    title: str | None = None,
    source_type: str | None = None,
    confidence: int = 7,
    dry_run: bool = False,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    payload = _parse_json_payload(response_text)
    normalized = _normalize_payload(
        payload,
        fallback_source_ref=source_ref,
        fallback_title=title,
        fallback_source_type=source_type,
    )
    memory_text = _compose_memory_text(normalized)
    learning_tags = list(tags or []) + ["learning_handoff", "external_model"]
    memory = ingest_learning_text(
        repo_root,
        memory_text,
        title=normalized["title"],
        source_type=normalized["source_type"],
        max_points=8,
        confidence=_coerce_confidence(confidence, default=7),
        dry_run=dry_run,
        extra_tags=learning_tags,
    )

    now = _utc_now()
    import_id = next_id_for_rel_path(repo_root, "li", "modules/memory/logs/learning_imports.jsonl")
    import_record = {
        "id": import_id,
        "created_at": now,
        "status": "active",
        "ingest_mode": "learning_handoff",
        "source_type": normalized["source_type"],
        "source_ref": normalized["source_ref"],
        "title": normalized["title"],
        "summary": normalized["summary"],
        "key_points": normalized["key_points"],
        "raw_payload_hash": hashlib.sha256(response_text.encode("utf-8")).hexdigest(),
        "source_refs": memory["record_ids"],
        "candidate_count": len(normalized["candidates"]),
        "object_type": "memory",
        "proposal_target": "memory",
    }

    candidate_records: list[dict[str, Any]] = []
    base_source_refs = [import_id] + list(memory["record_ids"])
    for item in normalized["candidates"]:
        candidate_type = str(item["candidate_type"])
        target = PROPOSAL_TARGET_BY_TYPE.get(candidate_type, "system")
        record = {
            "id": next_id_for_rel_path(repo_root, "lc", "orchestrator/logs/learning_candidates.jsonl"),
            "created_at": now,
            "status": "active",
            "candidate_type": candidate_type,
            "candidate_state": "pending_review",
            "title": item["title"],
            "statement": item["statement"],
            "rationale": item["rationale"],
            "evidence": item["evidence"],
            "confidence": item["confidence"],
            "source_refs": base_source_refs,
            "source_material_ref": normalized["source_ref"],
            "approval_ref": None,
            "owner_decision": None,
            "object_type": "system",
            "proposal_target": target,
        }
        candidate_records.append(record)

    if not dry_run:
        append_jsonl(
            repo_root / "modules" / "memory" / "logs" / "learning_imports.jsonl",
            import_record,
            schema_header=LEARNING_IMPORTS_SCHEMA,
        )
        for record in candidate_records:
            append_jsonl(
                repo_root / "orchestrator" / "logs" / "learning_candidates.jsonl",
                record,
                schema_header=LEARNING_CANDIDATES_SCHEMA,
            )

    counts = {
        "insight": 0,
        "rule": 0,
        "skill": 0,
        "principle": 0,
        "cognition_revision": 0,
    }
    for record in candidate_records:
        ctype = str(record["candidate_type"])
        if ctype in counts:
            counts[ctype] += 1

    return {
        "ingest_mode": "learning_handoff",
        "dry_run": dry_run,
        "source_ref": normalized["source_ref"],
        "title": normalized["title"],
        "source_type": normalized["source_type"],
        "summary": normalized["summary"],
        "memory_record_ids": memory["record_ids"],
        "import_record_id": import_id,
        "candidate_record_ids": [record["id"] for record in candidate_records],
        "candidate_counts": counts,
        "candidate_total": len(candidate_records),
        "preview": {
            "import": {
                "id": import_id,
                "title": normalized["title"],
                "candidate_count": len(candidate_records),
            },
            "candidates": [
                {
                    "id": record["id"],
                    "candidate_type": record["candidate_type"],
                    "title": record["title"],
                    "proposal_target": record["proposal_target"],
                }
                for record in candidate_records[:8]
            ],
        },
    }


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


def _active_verdict_map(repo_root: Path) -> dict[str, dict[str, Any]]:
    path = repo_root / "modules" / "decision" / "logs" / "learning_candidate_verdicts.jsonl"
    rows = _read_jsonl(path)
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        if str(row.get("status", "")).strip().lower() != "active":
            continue
        candidate_ref = str(row.get("candidate_ref", "")).strip()
        if not candidate_ref:
            continue
        out[candidate_ref] = row
    return out


def apply_learning_candidate_verdict(
    repo_root: Path,
    *,
    candidate_id: str,
    verdict: str,
    owner_note: str,
    modified_statement: str | None = None,
) -> dict[str, Any]:
    target_candidate_id = str(candidate_id or "").strip()
    if not target_candidate_id:
        raise ValueError("candidate_id is required")

    normalized_verdict = str(verdict or "").strip().lower()
    if normalized_verdict not in {"accept", "modify", "reject"}:
        raise ValueError("verdict must be one of: accept, modify, reject")

    note = _clip(owner_note, 500)
    if not note:
        raise ValueError("owner_note is required")

    candidate_path = repo_root / "orchestrator" / "logs" / "learning_candidates.jsonl"
    candidates = _read_jsonl(candidate_path)
    target: dict[str, Any] | None = None
    for row in candidates:
        if str(row.get("id", "")).strip() != target_candidate_id:
            continue
        if str(row.get("status", "")).strip().lower() != "active":
            continue
        target = row
        break
    if target is None:
        raise ValueError(f"candidate not found: {target_candidate_id}")

    verdict_map = _active_verdict_map(repo_root)
    if target_candidate_id in verdict_map:
        raise ValueError(f"candidate already reviewed: {target_candidate_id}")

    modified_text = _clip(modified_statement, 320) if modified_statement is not None else ""
    replacement_candidate: dict[str, Any] | None = None

    verdict_path = repo_root / "modules" / "decision" / "logs" / "learning_candidate_verdicts.jsonl"
    verdict_id = next_id_for_rel_path(repo_root, "lv", "modules/decision/logs/learning_candidate_verdicts.jsonl")
    verdict_record = {
        "id": verdict_id,
        "created_at": _utc_now(),
        "status": "active",
        "candidate_ref": target_candidate_id,
        "verdict": normalized_verdict,
        "owner_note": note,
        "modified_statement": None,
        "replacement_candidate_ref": None,
        "source_refs": [target_candidate_id],
        "object_type": "decision",
        "proposal_target": str(target.get("proposal_target", "")).strip() or "system",
    }

    if normalized_verdict == "modify":
        if not modified_text:
            raise ValueError("modified_statement is required for modify verdict")
        replacement_id = next_id_for_rel_path(repo_root, "lc", "orchestrator/logs/learning_candidates.jsonl")
        replacement_candidate = {
            "id": replacement_id,
            "created_at": _utc_now(),
            "status": "active",
            "candidate_type": str(target.get("candidate_type", "")).strip() or "insight",
            "candidate_state": "pending_review",
            "title": _clip(str(target.get("title", "")).strip() or "modified_candidate", 96),
            "statement": modified_text,
            "rationale": str(target.get("rationale")) if target.get("rationale") is not None else None,
            "evidence": target.get("evidence") if isinstance(target.get("evidence"), list) else [],
            "confidence": _coerce_confidence(target.get("confidence"), default=7),
            "source_refs": list(target.get("source_refs", [])) + [target_candidate_id, verdict_id],
            "source_material_ref": str(target.get("source_material_ref", "")).strip() or "<modified>",
            "approval_ref": None,
            "owner_decision": None,
            "object_type": "system",
            "proposal_target": str(target.get("proposal_target", "")).strip() or "system",
        }
        verdict_record["modified_statement"] = modified_text
        verdict_record["replacement_candidate_ref"] = replacement_id

    append_jsonl(verdict_path, verdict_record, schema_header=LEARNING_CANDIDATE_VERDICTS_SCHEMA)
    if replacement_candidate is not None:
        append_jsonl(candidate_path, replacement_candidate, schema_header=LEARNING_CANDIDATES_SCHEMA)

    return {
        "verdict_record_id": verdict_id,
        "candidate_ref": target_candidate_id,
        "verdict": normalized_verdict,
        "replacement_candidate_ref": verdict_record["replacement_candidate_ref"],
    }


def _active_promotion_map(repo_root: Path) -> dict[str, dict[str, Any]]:
    path = repo_root / "modules" / "decision" / "logs" / "learning_candidate_promotions.jsonl"
    rows = _read_jsonl(path)
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        if str(row.get("status", "")).strip().lower() != "active":
            continue
        candidate_ref = str(row.get("candidate_ref", "")).strip()
        if not candidate_ref:
            continue
        out[candidate_ref] = row
    return out


def promote_learning_candidate(
    repo_root: Path,
    *,
    candidate_id: str,
    approval_note: str,
) -> dict[str, Any]:
    target_candidate_id = str(candidate_id or "").strip()
    if not target_candidate_id:
        raise ValueError("candidate_id is required")

    note = _clip(approval_note, 500)
    if not note:
        raise ValueError("approval_note is required")

    candidate_path = repo_root / "orchestrator" / "logs" / "learning_candidates.jsonl"
    candidates = _read_jsonl(candidate_path)
    target: dict[str, Any] | None = None
    for row in candidates:
        if str(row.get("id", "")).strip() != target_candidate_id:
            continue
        if str(row.get("status", "")).strip().lower() != "active":
            continue
        target = row
        break
    if target is None:
        raise ValueError(f"candidate not found: {target_candidate_id}")

    verdict_row = _active_verdict_map(repo_root).get(target_candidate_id)
    if verdict_row is None or str(verdict_row.get("verdict", "")).strip().lower() != "accept":
        raise ValueError("candidate must be accepted before promotion")

    promotion_map = _active_promotion_map(repo_root)
    if target_candidate_id in promotion_map:
        raise ValueError(f"candidate already promoted: {target_candidate_id}")

    approval_path = repo_root / "modules" / "decision" / "logs" / "learning_candidate_approvals.jsonl"
    promotion_path = repo_root / "modules" / "decision" / "logs" / "learning_candidate_promotions.jsonl"

    approval_id = next_id_for_rel_path(repo_root, "la", "modules/decision/logs/learning_candidate_approvals.jsonl")
    approval_record = {
        "id": approval_id,
        "created_at": _utc_now(),
        "status": "active",
        "candidate_ref": target_candidate_id,
        "approval_note": note,
        "source_refs": [target_candidate_id, str(verdict_row.get("id", "")).strip()],
        "object_type": "decision",
        "proposal_target": str(target.get("proposal_target", "")).strip() or "system",
    }
    append_jsonl(approval_path, approval_record, schema_header=LEARNING_CANDIDATE_APPROVALS_SCHEMA)

    promotion_id = next_id_for_rel_path(repo_root, "lp", "modules/decision/logs/learning_candidate_promotions.jsonl")
    promotion_record = {
        "id": promotion_id,
        "created_at": _utc_now(),
        "status": "active",
        "candidate_ref": target_candidate_id,
        "candidate_type": str(target.get("candidate_type", "")).strip() or "insight",
        "promotion_target": str(target.get("proposal_target", "")).strip() or "system",
        "approval_ref": approval_id,
        "promotion_note": note,
        "source_refs": [target_candidate_id, approval_id],
        "object_type": "decision",
        "proposal_target": str(target.get("proposal_target", "")).strip() or "system",
    }
    append_jsonl(promotion_path, promotion_record, schema_header=LEARNING_CANDIDATE_PROMOTIONS_SCHEMA)

    return {
        "approval_record_id": approval_id,
        "promotion_record_id": promotion_id,
        "candidate_ref": target_candidate_id,
        "promotion_target": promotion_record["promotion_target"],
    }


def list_recent_learning_candidates(repo_root: Path, *, limit: int = 20) -> list[dict[str, Any]]:
    path = repo_root / "orchestrator" / "logs" / "learning_candidates.jsonl"
    rows = _read_jsonl(path)
    resolved = set(_active_verdict_map(repo_root).keys())
    filtered = [
        row
        for row in rows
        if str(row.get("status", "")).strip().lower() == "active"
        and str(row.get("candidate_state", "")).strip().lower() == "pending_review"
        and str(row.get("id", "")).strip() not in resolved
    ]
    filtered.sort(key=lambda row: str(row.get("created_at", "")), reverse=True)
    out: list[dict[str, Any]] = []
    for row in filtered[: max(1, min(limit, 100))]:
        out.append(
            {
                "id": str(row.get("id", "")).strip(),
                "candidate_type": str(row.get("candidate_type", "")).strip(),
                "title": str(row.get("title", "")).strip(),
                "proposal_target": str(row.get("proposal_target", "")).strip() or None,
                "created_at": str(row.get("created_at", "")).strip(),
                "candidate_state": str(row.get("candidate_state", "")).strip(),
            }
        )
    return out
