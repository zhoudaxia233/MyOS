from __future__ import annotations

import hashlib
import json
from math import ceil
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from idgen import next_id_for_rel_path
from learning_ingest import ingest_learning_text
from principles_authority import principle_ratification_map
from runtime_eligibility import (
    RUNTIME_MATURITY_HOURS,
    candidate_runtime_eligibility_map,
    create_promotion_runtime_eligibility,
    summarize_runtime_eligibility,
)
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

MODULE_CANDIDATE_SCHEMA_FIELDS = [
    "id",
    "created_at",
    "status",
    "candidate_ref",
    "candidate_type",
    "title",
    "statement",
    "evidence",
    "source_refs",
    "approval_ref",
    "promotion_ref",
    "object_type",
    "proposal_target",
]

INSIGHT_CANDIDATES_SCHEMA = {
    "_schema": {
        "name": "insight_candidates",
        "version": "1.0",
        "fields": MODULE_CANDIDATE_SCHEMA_FIELDS,
        "notes": "append-only",
    }
}

RULE_CANDIDATES_SCHEMA = {
    "_schema": {
        "name": "rule_candidates",
        "version": "1.0",
        "fields": MODULE_CANDIDATE_SCHEMA_FIELDS,
        "notes": "append-only",
    }
}

SKILL_CANDIDATES_SCHEMA = {
    "_schema": {
        "name": "skill_candidates",
        "version": "1.0",
        "fields": MODULE_CANDIDATE_SCHEMA_FIELDS,
        "notes": "append-only",
    }
}

PROFILE_TRAIT_CANDIDATES_SCHEMA = {
    "_schema": {
        "name": "profile_trait_candidates",
        "version": "1.0",
        "fields": MODULE_CANDIDATE_SCHEMA_FIELDS,
        "notes": "append-only",
    }
}

SCHEMA_CANDIDATES_SCHEMA = {
    "_schema": {
        "name": "schema_candidates",
        "version": "1.0",
        "fields": MODULE_CANDIDATE_SCHEMA_FIELDS,
        "notes": "append-only",
    }
}

PRINCIPLE_CANDIDATES_SCHEMA = {
    "_schema": {
        "name": "principle_candidates",
        "version": "1.0",
        "fields": MODULE_CANDIDATE_SCHEMA_FIELDS,
        "notes": "append-only",
    }
}

CANDIDATE_SINK_CONFIG: dict[str, dict[str, Any]] = {
    "insight": {
        "path": "modules/memory/logs/insight_candidates.jsonl",
        "prefix": "ic",
        "schema": INSIGHT_CANDIDATES_SCHEMA,
        "object_type": "memory",
        "proposal_target": "memory",
    },
    "rule": {
        "path": "modules/decision/logs/rule_candidates.jsonl",
        "prefix": "rc",
        "schema": RULE_CANDIDATES_SCHEMA,
        "object_type": "decision",
        "proposal_target": "decision",
    },
    "skill": {
        "path": "modules/decision/logs/skill_candidates.jsonl",
        "prefix": "sc",
        "schema": SKILL_CANDIDATES_SCHEMA,
        "object_type": "decision",
        "proposal_target": "decision",
    },
    "profile_trait": {
        "path": "modules/profile/logs/profile_trait_candidates.jsonl",
        "prefix": "ptc",
        "schema": PROFILE_TRAIT_CANDIDATES_SCHEMA,
        "object_type": "profile",
        "proposal_target": "profile",
    },
    "cognition_revision": {
        "path": "modules/cognition/logs/schema_candidates.jsonl",
        "prefix": "cc",
        "schema": SCHEMA_CANDIDATES_SCHEMA,
        "object_type": "cognition",
        "proposal_target": "cognition",
    },
    "principle": {
        "path": "modules/principles/logs/principle_candidates.jsonl",
        "prefix": "prc",
        "schema": PRINCIPLE_CANDIDATES_SCHEMA,
        "object_type": "principle",
        "proposal_target": "principle",
    },
}

PROMOTION_MATURITY_HOURS = RUNTIME_MATURITY_HOURS
PROMOTION_READINESS_PREVIEW_LIMIT = 5

FENCED_JSON_RE = re.compile(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", re.IGNORECASE)

CANDIDATE_SECTION_KEYS = {
    "insight": ["insights", "insight_candidates"],
    "rule": ["rules", "rule_candidates"],
    "skill": ["skills", "skill_candidates"],
    "profile_trait": ["profile_traits", "trait_candidates"],
    "principle": ["principles", "principle_candidates"],
    "cognition_revision": ["cognition_revisions", "schema_revisions", "schema_candidates"],
}

PROPOSAL_TARGET_BY_TYPE = {
    "insight": "memory",
    "rule": "decision",
    "skill": "decision",
    "profile_trait": "profile",
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
            "profile_traits": [
                {
                    "title": "<trait label>",
                    "statement": "<candidate trait update>",
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
        "profile_trait": 0,
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


def _parse_iso8601(ts: str) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def _window_filter(rows: list[dict[str, Any]], now: datetime, window_days: int) -> list[dict[str, Any]]:
    cutoff = now - timedelta(days=window_days)
    out: list[dict[str, Any]] = []
    for row in rows:
        created = _parse_iso8601(str(row.get("created_at", "")).strip())
        if created is None:
            continue
        if created >= cutoff:
            out.append(row)
    return out


def _safe_ratio(num: int, den: int) -> float:
    if den <= 0:
        return 0.0
    return num / den


def _trend_direction(*, direction: str, value_7d: float, value_30d: float, epsilon: float = 0.02) -> str:
    delta = value_7d - value_30d
    if abs(delta) <= epsilon:
        return "stable"
    if direction == "higher":
        return "improving" if delta > 0 else "worsening"
    return "improving" if delta < 0 else "worsening"


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


def _append_module_candidate_sink(
    repo_root: Path,
    *,
    candidate: dict[str, Any],
    approval_id: str,
    promotion_id: str,
) -> tuple[str | None, str | None]:
    candidate_type = str(candidate.get("candidate_type", "")).strip()
    config = CANDIDATE_SINK_CONFIG.get(candidate_type)
    if config is None:
        return None, None

    path_rel = str(config["path"])
    sink_id = next_id_for_rel_path(repo_root, str(config["prefix"]), path_rel)
    sink_record = {
        "id": sink_id,
        "created_at": _utc_now(),
        "status": "active",
        "candidate_ref": str(candidate.get("id", "")).strip(),
        "candidate_type": candidate_type,
        "title": _clip(candidate.get("title", ""), 96),
        "statement": _clip(candidate.get("statement", ""), 320),
        "evidence": candidate.get("evidence") if isinstance(candidate.get("evidence"), list) else [],
        "source_refs": [str(candidate.get("id", "")).strip(), approval_id, promotion_id],
        "approval_ref": approval_id,
        "promotion_ref": promotion_id,
        "object_type": str(config["object_type"]),
        "proposal_target": str(config["proposal_target"]),
    }
    append_jsonl(repo_root / path_rel, sink_record, schema_header=config["schema"])
    return sink_id, path_rel


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

    sink_record_id, sink_path = _append_module_candidate_sink(
        repo_root,
        candidate=target,
        approval_id=approval_id,
        promotion_id=promotion_id,
    )
    eligibility_record = None
    if sink_record_id is not None:
        eligibility_record = create_promotion_runtime_eligibility(
            repo_root,
            candidate=target,
            artifact_ref=sink_record_id,
            promotion_ref=promotion_id,
            approval_ref=approval_id,
        )

    return {
        "approval_record_id": approval_id,
        "promotion_record_id": promotion_id,
        "candidate_ref": target_candidate_id,
        "promotion_target": promotion_record["promotion_target"],
        "module_candidate_ref": sink_record_id,
        "module_candidate_path": sink_path,
        "runtime_eligibility_ref": str((eligibility_record or {}).get("id", "")).strip() or None,
        "runtime_eligibility_status": str((eligibility_record or {}).get("eligibility_status", "")).strip() or None,
    }


def summarize_learning_pipeline(
    repo_root: Path,
    *,
    window_days: int = 30,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    import_path = repo_root / "modules" / "memory" / "logs" / "learning_imports.jsonl"
    candidate_path = repo_root / "orchestrator" / "logs" / "learning_candidates.jsonl"
    verdict_path = repo_root / "modules" / "decision" / "logs" / "learning_candidate_verdicts.jsonl"
    promotion_path = repo_root / "modules" / "decision" / "logs" / "learning_candidate_promotions.jsonl"

    imports = _window_filter(_read_jsonl(import_path), now, window_days)
    candidates = _read_jsonl(candidate_path)
    candidates_window = _window_filter(
        [
            row
            for row in candidates
            if str(row.get("status", "")).strip().lower() == "active"
        ],
        now,
        window_days,
    )
    verdicts = _window_filter(_read_jsonl(verdict_path), now, window_days)
    promotions = _window_filter(_read_jsonl(promotion_path), now, window_days)
    reviewed_candidate_refs = set(_active_verdict_map(repo_root).keys())
    promoted_candidate_refs = set(_active_promotion_map(repo_root).keys())

    pending_rows = [
        row
        for row in candidates
        if str(row.get("status", "")).strip().lower() == "active"
        and str(row.get("candidate_state", "")).strip().lower() == "pending_review"
        and str(row.get("id", "")).strip() not in reviewed_candidate_refs
        and str(row.get("id", "")).strip() not in promoted_candidate_refs
    ]
    pending_by_type = Counter(str(row.get("candidate_type", "unknown")).strip() or "unknown" for row in pending_rows)

    verdict_counter = Counter(str(row.get("verdict", "")).strip().lower() for row in verdicts)
    promotion_by_target = Counter(str(row.get("promotion_target", "")).strip() or "unknown" for row in promotions)

    reviewed_total = sum(verdict_counter.values())
    accepted_total = verdict_counter.get("accept", 0)
    promoted_total = len(promotions)
    promotion_conversion_rate = (promoted_total / accepted_total) if accepted_total > 0 else 0.0
    promotion_readiness = summarize_promotion_readiness(repo_root, now=now)
    runtime_eligibility = summarize_runtime_eligibility(repo_root, now=now)

    return {
        "window_days": window_days,
        "imported_total": len(imports),
        "candidate_total": len(candidates_window),
        "pending_total": len(pending_rows),
        "pending_by_type": dict(pending_by_type),
        "reviewed_total": reviewed_total,
        "verdicts": {
            "accept": accepted_total,
            "modify": verdict_counter.get("modify", 0),
            "reject": verdict_counter.get("reject", 0),
        },
        "promoted_total": promoted_total,
        "promoted_by_target": dict(promotion_by_target),
        "promotion_conversion_rate": round(promotion_conversion_rate, 3),
        "promotion_readiness": promotion_readiness,
        "runtime_eligibility": runtime_eligibility,
        "lifecycle": {
            "imported": len(imports),
            "candidate": len(candidates_window),
            "reviewed": reviewed_total,
            "promoted": promoted_total,
            "runtime_eligible": int(runtime_eligibility.get("eligible_total", 0)),
            "active_runtime": int(runtime_eligibility.get("active_total", 0)),
        },
    }


def summarize_promotion_readiness(
    repo_root: Path,
    *,
    now: datetime | None = None,
    maturity_hours: int = PROMOTION_MATURITY_HOURS,
) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    required_hours = max(0, int(maturity_hours))
    path = repo_root / "modules" / "decision" / "logs" / "learning_candidate_promotions.jsonl"
    promotions = [
        row
        for row in _read_jsonl(path)
        if str(row.get("status", "")).strip().lower() == "active"
    ]

    ready_by_target: Counter[str] = Counter()
    cooling_by_target: Counter[str] = Counter()
    cooling_candidates: list[dict[str, Any]] = []

    for row in promotions:
        created = _parse_iso8601(str(row.get("created_at", "")).strip())
        target = str(row.get("promotion_target", "")).strip() or "unknown"
        candidate_ref = str(row.get("candidate_ref", "")).strip()
        promotion_ref = str(row.get("id", "")).strip()
        if created is None:
            cooling_by_target[target] += 1
            if len(cooling_candidates) < PROMOTION_READINESS_PREVIEW_LIMIT:
                cooling_candidates.append(
                    {
                        "promotion_ref": promotion_ref,
                        "candidate_ref": candidate_ref,
                        "promotion_target": target,
                        "hours_remaining": required_hours,
                    }
                )
            continue

        age_hours = max(0.0, (now - created).total_seconds() / 3600.0)
        if age_hours >= required_hours:
            ready_by_target[target] += 1
            continue

        cooling_by_target[target] += 1
        if len(cooling_candidates) < PROMOTION_READINESS_PREVIEW_LIMIT:
            cooling_candidates.append(
                {
                    "promotion_ref": promotion_ref,
                    "candidate_ref": candidate_ref,
                    "promotion_target": target,
                    "hours_remaining": max(0, int(ceil(required_hours - age_hours))),
                }
            )

    return {
        "maturity_hours": required_hours,
        "ready_total": sum(ready_by_target.values()),
        "cooling_total": sum(cooling_by_target.values()),
        "ready_by_target": dict(ready_by_target),
        "cooling_by_target": dict(cooling_by_target),
        "cooling_candidates": cooling_candidates,
    }


def summarize_learning_pipeline_trend(
    repo_root: Path,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    snap_7d = summarize_learning_pipeline(repo_root, window_days=7, now=now)
    snap_30d = summarize_learning_pipeline(repo_root, window_days=30, now=now)

    candidate_path = repo_root / "orchestrator" / "logs" / "learning_candidates.jsonl"
    candidates = [
        row
        for row in _read_jsonl(candidate_path)
        if str(row.get("status", "")).strip().lower() == "active"
    ]
    inflow_7d = len(_window_filter(candidates, now, 7))
    inflow_30d = len(_window_filter(candidates, now, 30))

    verdicts_7d = snap_7d.get("verdicts", {})
    verdicts_30d = snap_30d.get("verdicts", {})
    reviewed_7d = int(snap_7d.get("reviewed_total", 0))
    reviewed_30d = int(snap_30d.get("reviewed_total", 0))
    reject_7d = int(verdicts_7d.get("reject", 0)) if isinstance(verdicts_7d, dict) else 0
    reject_30d = int(verdicts_30d.get("reject", 0)) if isinstance(verdicts_30d, dict) else 0

    backlog_pressure_7d = inflow_7d - reviewed_7d
    backlog_pressure_30d = inflow_30d - reviewed_30d
    reject_ratio_7d = _safe_ratio(reject_7d, reviewed_7d)
    reject_ratio_30d = _safe_ratio(reject_30d, reviewed_30d)
    conversion_7d = float(snap_7d.get("promotion_conversion_rate", 0.0))
    conversion_30d = float(snap_30d.get("promotion_conversion_rate", 0.0))

    comparisons = [
        {
            "key": "backlog_pressure",
            "direction": "lower",
            "value_7d": float(backlog_pressure_7d),
            "value_30d": float(backlog_pressure_30d),
            "delta": float(backlog_pressure_7d - backlog_pressure_30d),
            "trend": _trend_direction(
                direction="lower",
                value_7d=float(backlog_pressure_7d),
                value_30d=float(backlog_pressure_30d),
                epsilon=0.1,
            ),
        },
        {
            "key": "reject_ratio",
            "direction": "lower",
            "value_7d": round(reject_ratio_7d, 3),
            "value_30d": round(reject_ratio_30d, 3),
            "delta": round(reject_ratio_7d - reject_ratio_30d, 3),
            "trend": _trend_direction(
                direction="lower",
                value_7d=reject_ratio_7d,
                value_30d=reject_ratio_30d,
            ),
        },
        {
            "key": "promotion_conversion_rate",
            "direction": "higher",
            "value_7d": round(conversion_7d, 3),
            "value_30d": round(conversion_30d, 3),
            "delta": round(conversion_7d - conversion_30d, 3),
            "trend": _trend_direction(
                direction="higher",
                value_7d=conversion_7d,
                value_30d=conversion_30d,
            ),
        },
    ]

    return {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "windows": {
            "7d": snap_7d,
            "30d": snap_30d,
        },
        "inflow": {
            "7d": inflow_7d,
            "30d": inflow_30d,
        },
        "comparisons": comparisons,
    }


def list_recent_learning_candidates(
    repo_root: Path,
    *,
    limit: int = 20,
    include_resolved: bool = False,
) -> list[dict[str, Any]]:
    path = repo_root / "orchestrator" / "logs" / "learning_candidates.jsonl"
    rows = _read_jsonl(path)
    verdict_map = _active_verdict_map(repo_root)
    promotion_map = _active_promotion_map(repo_root)
    principle_ratifications = principle_ratification_map(repo_root)
    now = datetime.now(timezone.utc)
    runtime_map = candidate_runtime_eligibility_map(repo_root, now=now)
    maturity_hours = max(0, int(PROMOTION_MATURITY_HOURS))

    stage_rank = {
        "candidate": 1,
        "reviewed": 2,
        "promoted": 3,
        "canonicalized": 4,
        "active_runtime": 5,
    }

    staged_rows: list[tuple[int, str, dict[str, Any]]] = []
    for row in rows:
        if str(row.get("status", "")).strip().lower() != "active":
            continue
        candidate_state = str(row.get("candidate_state", "")).strip().lower()
        if not include_resolved and candidate_state != "pending_review":
            continue
        candidate_id = str(row.get("id", "")).strip()
        if not candidate_id:
            continue
        verdict_row = verdict_map.get(candidate_id)
        promotion_row = promotion_map.get(candidate_id)
        principle_ratification = principle_ratifications.get(candidate_id)
        runtime_row = runtime_map.get(candidate_id)

        lifecycle_stage = "candidate"
        verdict = None
        owner_note = None
        modified_statement = None
        can_review = True
        can_promote = False
        runtime_hours_remaining: int | None = None
        reviewed_at: str | None = None
        promoted_at: str | None = None

        if promotion_row is not None:
            can_review = False
            can_promote = False
            promoted_at = str(promotion_row.get("created_at", "")).strip() or None
            lifecycle_stage = "promoted"
            if principle_ratification is not None:
                lifecycle_stage = "canonicalized"
            if runtime_row is not None:
                runtime_hours_remaining = runtime_row.get("runtime_hours_remaining")
                if runtime_row.get("runtime_active") is True:
                    lifecycle_stage = "active_runtime"
                    runtime_hours_remaining = 0
        elif verdict_row is not None:
            lifecycle_stage = "reviewed"
            verdict = str(verdict_row.get("verdict", "")).strip().lower() or None
            owner_note = str(verdict_row.get("owner_note", "")).strip() or None
            modified_statement = str(verdict_row.get("modified_statement", "")).strip() or None
            reviewed_at = str(verdict_row.get("created_at", "")).strip() or None
            can_review = False
            can_promote = verdict == "accept"

        if not include_resolved and lifecycle_stage != "candidate":
            continue

        evidence_list = [str(item).strip() for item in row.get("evidence", []) if str(item).strip()]
        evidence_preview = " | ".join(evidence_list[:2]) if evidence_list else None
        source_refs = [str(item).strip() for item in row.get("source_refs", []) if str(item).strip()]
        source_import_ref = next((ref for ref in source_refs if ref.startswith("li_")), None)

        out_row = {
            "id": candidate_id,
            "candidate_type": str(row.get("candidate_type", "")).strip(),
            "title": str(row.get("title", "")).strip(),
            "statement": str(row.get("statement", "")).strip(),
            "rationale": str(row.get("rationale", "")).strip() if row.get("rationale") is not None else None,
            "evidence": evidence_list[:3],
            "evidence_preview": evidence_preview,
            "confidence": _coerce_confidence(row.get("confidence"), default=7),
            "proposal_target": str(row.get("proposal_target", "")).strip() or None,
            "created_at": str(row.get("created_at", "")).strip(),
            "candidate_state": str(row.get("candidate_state", "")).strip(),
            "source_material_ref": str(row.get("source_material_ref", "")).strip() or None,
            "source_refs": source_refs[:5],
            "source_import_ref": source_import_ref,
            "lifecycle_stage": lifecycle_stage,
            "verdict": verdict,
            "owner_note": owner_note,
            "modified_statement": modified_statement,
            "can_review": can_review,
            "can_promote": can_promote,
            "reviewed_at": reviewed_at,
            "promoted_at": promoted_at,
            "runtime_hours_remaining": runtime_hours_remaining,
            "promotion_target": str(promotion_row.get("promotion_target", "")).strip() if promotion_row else None,
            "can_ratify": bool(
                str(row.get("candidate_type", "")).strip() == "principle"
                and promotion_row is not None
                and principle_ratification is None
            ),
            "canonicalization_ref": str((principle_ratification or {}).get("id", "")).strip() or None,
            "canonicalized_at": str((principle_ratification or {}).get("created_at", "")).strip() or None,
            "canonical_clause_id": str((principle_ratification or {}).get("principle_id", "")).strip() or None,
            "runtime_active": lifecycle_stage == "active_runtime",
            "runtime_eligible": bool(runtime_row and str(runtime_row.get("eligibility_status", "")).strip() == "eligible"),
            "runtime_eligibility_ref": str((runtime_row or {}).get("eligibility_ref", "")).strip() or None,
            "runtime_eligibility_status": str((runtime_row or {}).get("eligibility_status", "")).strip() or None,
            "runtime_scope_modules": list(runtime_row.get("scope_modules", [])) if runtime_row else [],
            "runtime_autonomy_ceiling": str((runtime_row or {}).get("autonomy_ceiling", "")).strip() or None,
            "runtime_state": str((runtime_row or {}).get("runtime_state", "")).strip() or None,
            "runtime_maturity_hours": int((runtime_row or {}).get("maturity_hours", maturity_hours) or maturity_hours),
            "runtime_change_note": str((runtime_row or {}).get("change_note", "")).strip() or None,
        }
        staged_rows.append((stage_rank.get(lifecycle_stage, 9), str(row.get("created_at", "")), out_row))

    if include_resolved:
        staged_rows.sort(key=lambda item: item[1], reverse=True)
        staged_rows.sort(key=lambda item: item[0])
    else:
        staged_rows.sort(key=lambda item: item[1], reverse=True)
    out: list[dict[str, Any]] = []
    for _, _, row in staged_rows[: max(1, min(limit, 100))]:
        out.append(row)
    return out
