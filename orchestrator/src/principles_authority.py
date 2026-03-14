from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from idgen import next_id_for_rel_path
from validators import append_jsonl

PRINCIPLE_AMENDMENTS_SCHEMA = {
    "_schema": {
        "name": "principle_amendments",
        "version": "1.1",
        "fields": [
            "id",
            "created_at",
            "status",
            "object_type",
            "principle_id",
            "change_type",
            "proposal_summary",
            "rationale",
            "evidence_refs",
            "approval_ref",
            "effective_from",
            "source_refs",
            "proposal_target",
        ],
        "notes": "append-only",
    }
}

ID_RE = re.compile(r"^[a-z][a-z0-9]*_[0-9]{8}_[0-9]{3}$")
CLAUSE_ID_RE = re.compile(r"^pr_(\d{4})$")
DEFAULT_OVERRIDE_POLICY = "allowed_with_owner_confirmation"


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


def _principle_sink_row_by_candidate(repo_root: Path, candidate_ref: str) -> dict[str, Any] | None:
    path = repo_root / "modules" / "principles" / "logs" / "principle_candidates.jsonl"
    for row in _read_jsonl(path):
        if str(row.get("status", "")).strip().lower() != "active":
            continue
        if str(row.get("candidate_ref", "")).strip() == candidate_ref:
            return row
    return None


def _active_principle_amendments(repo_root: Path) -> list[dict[str, Any]]:
    path = repo_root / "modules" / "principles" / "logs" / "principle_amendments.jsonl"
    return [
        row
        for row in _read_jsonl(path)
        if str(row.get("status", "")).strip().lower() == "active"
    ]


def principle_ratification_map(repo_root: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in _active_principle_amendments(repo_root):
        refs = [str(item).strip() for item in row.get("source_refs", []) if str(item).strip()]
        for ref in refs:
            if ref.startswith("lc_"):
                out[ref] = row
    return out


def _next_clause_id(repo_root: Path) -> str:
    path = repo_root / "modules" / "principles" / "data" / "constitution.yaml"
    if not path.exists() or not path.is_file():
        raise ValueError("constitution.yaml is required for principle ratification")

    max_seq = 0
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if "clause_id:" not in line:
            continue
        _, value = line.split(":", 1)
        text = value.strip().strip('"').strip("'")
        match = CLAUSE_ID_RE.match(text)
        if match:
            max_seq = max(max_seq, int(match.group(1)))
    return f"pr_{max_seq + 1:04d}"


def _yaml_scalar(value: str) -> str:
    return json.dumps(str(value or "").strip(), ensure_ascii=False)


def _append_constitution_clause(
    repo_root: Path,
    *,
    clause_id: str,
    title: str,
    statement: str,
    rationale: str,
    override_policy: str = DEFAULT_OVERRIDE_POLICY,
) -> str:
    path = repo_root / "modules" / "principles" / "data" / "constitution.yaml"
    if not path.exists() or not path.is_file():
        raise ValueError("constitution.yaml is required for principle ratification")

    text = path.read_text(encoding="utf-8")
    if "clauses:" not in text:
        raise ValueError("constitution.yaml is missing clauses section")
    if f'clause_id: "{clause_id}"' in text or f"clause_id: '{clause_id}'" in text or f"clause_id: {clause_id}" in text:
        raise ValueError(f"principle clause already exists: {clause_id}")

    block = "\n".join(
        [
            f'  - clause_id: "{clause_id}"',
            f"    title: {_yaml_scalar(title)}",
            f"    statement: {_yaml_scalar(statement)}",
            f"    rationale: {_yaml_scalar(rationale)}",
            f"    override_policy: {_yaml_scalar(override_policy)}",
        ]
    )
    path.write_text(text.rstrip("\n") + "\n\n" + block + "\n", encoding="utf-8")
    return str(path)


def ratify_principle_candidate(
    repo_root: Path,
    *,
    candidate_ref: str,
    ratification_note: str,
) -> dict[str, Any]:
    target_candidate_ref = str(candidate_ref or "").strip()
    if not target_candidate_ref:
        raise ValueError("candidate_ref is required")

    note = str(ratification_note or "").strip()
    if not note:
        raise ValueError("ratification_note is required")

    candidate = _candidate_row_by_id(repo_root, target_candidate_ref)
    if candidate is None:
        raise ValueError(f"candidate not found: {target_candidate_ref}")
    if str(candidate.get("candidate_type", "")).strip() != "principle":
        raise ValueError("only promoted principle candidates can be ratified through this path")

    promotion = _promotion_row_by_candidate(repo_root, target_candidate_ref)
    if promotion is None:
        raise ValueError("principle candidate must be promoted before ratification")

    sink_row = _principle_sink_row_by_candidate(repo_root, target_candidate_ref)
    if sink_row is None:
        raise ValueError("promoted principle candidate is missing principle sink record")

    existing = principle_ratification_map(repo_root).get(target_candidate_ref)
    if existing is not None:
        raise ValueError(f"principle candidate already ratified: {target_candidate_ref}")

    clause_id = _next_clause_id(repo_root)
    amendment_path = "modules/principles/logs/principle_amendments.jsonl"
    amendment_id = next_id_for_rel_path(repo_root, "pam", amendment_path)
    approval_ref = next_id_for_rel_path(repo_root, "ap", amendment_path)
    effective_from = _utc_now()

    title = str(sink_row.get("title", "")).strip() or str(candidate.get("title", "")).strip() or clause_id
    statement = str(sink_row.get("statement", "")).strip() or str(candidate.get("statement", "")).strip()
    if not statement:
        raise ValueError("principle candidate is missing statement")

    candidate_rationale = str(candidate.get("rationale", "")).strip()
    rationale = candidate_rationale or note

    candidate_source_refs = [str(item).strip() for item in candidate.get("source_refs", []) if str(item).strip()]
    sink_source_refs = [str(item).strip() for item in sink_row.get("source_refs", []) if str(item).strip()]
    evidence_refs = _ordered_unique(
        [
            ref
            for ref in [*candidate_source_refs, *sink_source_refs, target_candidate_ref]
            if ID_RE.match(ref)
        ]
    )
    source_refs = _ordered_unique(
        [
            target_candidate_ref,
            str(sink_row.get("id", "")).strip(),
            str(sink_row.get("approval_ref", "")).strip(),
            str(sink_row.get("promotion_ref", "")).strip(),
            str(promotion.get("id", "")).strip(),
            approval_ref,
        ]
    )

    amendment_record = {
        "id": amendment_id,
        "created_at": effective_from,
        "status": "active",
        "object_type": "principle",
        "principle_id": clause_id,
        "change_type": "add_clause",
        "proposal_summary": title,
        "rationale": note,
        "evidence_refs": evidence_refs,
        "approval_ref": approval_ref,
        "effective_from": effective_from,
        "source_refs": source_refs,
        "proposal_target": "principle",
    }
    append_jsonl(repo_root / amendment_path, amendment_record, schema_header=PRINCIPLE_AMENDMENTS_SCHEMA)
    constitution_path = _append_constitution_clause(
        repo_root,
        clause_id=clause_id,
        title=title,
        statement=statement,
        rationale=rationale,
    )

    return {
        "candidate_ref": target_candidate_ref,
        "amendment_record_id": amendment_id,
        "ratification_approval_ref": approval_ref,
        "canonical_clause_id": clause_id,
        "canonicalized_at": effective_from,
        "constitution_path": constitution_path,
        "change_type": amendment_record["change_type"],
        "constitution_updated": True,
    }
