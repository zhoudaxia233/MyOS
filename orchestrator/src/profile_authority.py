from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from idgen import next_id_for_rel_path
from validators import append_jsonl

PROFILE_CHANGES_SCHEMA = {
    "_schema": {
        "name": "profile_changes",
        "version": "1.1",
        "fields": [
            "id",
            "created_at",
            "status",
            "change_type",
            "change_summary",
            "reason",
            "expected_effect",
            "source_refs",
            "object_type",
            "proposal_target",
        ],
        "notes": "append-only",
    }
}

PROFILE_TRAIT_CHANGE_TYPE = "profile_trait_canonicalized"
PROFILE_TRAIT_ID_RE = re.compile(r"^pft_(\d{4})$")


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


def _profile_sink_row_by_candidate(repo_root: Path, candidate_ref: str) -> dict[str, Any] | None:
    path = repo_root / "modules" / "profile" / "logs" / "profile_trait_candidates.jsonl"
    for row in _read_jsonl(path):
        if str(row.get("status", "")).strip().lower() != "active":
            continue
        if str(row.get("candidate_ref", "")).strip() == candidate_ref:
            return row
    return None


def _active_profile_changes(repo_root: Path) -> list[dict[str, Any]]:
    path = repo_root / "modules" / "profile" / "logs" / "profile_changes.jsonl"
    return [
        row
        for row in _read_jsonl(path)
        if str(row.get("status", "")).strip().lower() == "active"
        and str(row.get("change_type", "")).strip() == PROFILE_TRAIT_CHANGE_TYPE
    ]


def profile_trait_ratification_map(repo_root: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in _active_profile_changes(repo_root):
        refs = [str(item).strip() for item in row.get("source_refs", []) if str(item).strip()]
        for ref in refs:
            if ref.startswith("lc_"):
                out[ref] = row
    return out


def _next_profile_trait_id(repo_root: Path) -> str:
    path = repo_root / "modules" / "profile" / "data" / "psych_profile.yaml"
    if not path.exists() or not path.is_file():
        raise ValueError("psych_profile.yaml is required for profile trait ratification")

    max_seq = 0
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if "trait_id:" not in line:
            continue
        _, value = line.split(":", 1)
        text = value.strip().strip('"').strip("'")
        match = PROFILE_TRAIT_ID_RE.match(text)
        if match:
            max_seq = max(max_seq, int(match.group(1)))
    return f"pft_{max_seq + 1:04d}"


def _yaml_scalar(value: str) -> str:
    return json.dumps(str(value or "").strip(), ensure_ascii=False)


def _append_psych_profile_trait(
    repo_root: Path,
    *,
    trait_id: str,
    title: str,
    statement: str,
    rationale: str,
) -> str:
    path = repo_root / "modules" / "profile" / "data" / "psych_profile.yaml"
    if not path.exists() or not path.is_file():
        raise ValueError("psych_profile.yaml is required for profile trait ratification")

    text = path.read_text(encoding="utf-8")
    if f'trait_id: "{trait_id}"' in text or f"trait_id: '{trait_id}'" in text or f"trait_id: {trait_id}" in text:
        raise ValueError(f"profile trait already exists: {trait_id}")

    block = "\n".join(
        [
            f'  - trait_id: "{trait_id}"',
            f"    title: {_yaml_scalar(title)}",
            f"    statement: {_yaml_scalar(statement)}",
            f"    rationale: {_yaml_scalar(rationale)}",
        ]
    )
    if "ratified_traits:" not in text:
        updated = text.rstrip("\n") + "\n\nratified_traits:\n" + block + "\n"
    else:
        updated = text.rstrip("\n") + "\n" + block + "\n"
    path.write_text(updated, encoding="utf-8")
    return str(path)


def ratify_profile_trait_candidate(
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
    if str(candidate.get("candidate_type", "")).strip() != "profile_trait":
        raise ValueError("only promoted profile_trait candidates can be ratified through this path")

    promotion = _promotion_row_by_candidate(repo_root, target_candidate_ref)
    if promotion is None:
        raise ValueError("profile trait candidate must be promoted before ratification")

    sink_row = _profile_sink_row_by_candidate(repo_root, target_candidate_ref)
    if sink_row is None:
        raise ValueError("promoted profile trait candidate is missing profile sink record")

    existing = profile_trait_ratification_map(repo_root).get(target_candidate_ref)
    if existing is not None:
        raise ValueError(f"profile trait candidate already ratified: {target_candidate_ref}")

    trait_id = _next_profile_trait_id(repo_root)
    change_path = "modules/profile/logs/profile_changes.jsonl"
    change_id = next_id_for_rel_path(repo_root, "pf", change_path)
    approval_ref = next_id_for_rel_path(repo_root, "ap", change_path)
    effective_from = _utc_now()

    title = str(sink_row.get("title", "")).strip() or str(candidate.get("title", "")).strip() or trait_id
    statement = str(sink_row.get("statement", "")).strip() or str(candidate.get("statement", "")).strip()
    if not statement:
        raise ValueError("profile trait candidate is missing statement")

    expected_effect = (
        "Adds the owner-ratified profile trait to psych_profile SSOT so future alignment checks can reference it."
    )
    source_refs = _ordered_unique(
        [
            target_candidate_ref,
            str(sink_row.get("id", "")).strip(),
            str(sink_row.get("approval_ref", "")).strip(),
            str(sink_row.get("promotion_ref", "")).strip(),
            str(promotion.get("id", "")).strip(),
            approval_ref,
            trait_id,
        ]
    )

    change_record = {
        "id": change_id,
        "created_at": effective_from,
        "status": "active",
        "change_type": PROFILE_TRAIT_CHANGE_TYPE,
        "change_summary": title,
        "reason": note,
        "expected_effect": expected_effect,
        "source_refs": source_refs,
        "object_type": "profile",
        "proposal_target": "profile",
    }
    append_jsonl(repo_root / change_path, change_record, schema_header=PROFILE_CHANGES_SCHEMA)
    psych_profile_path = _append_psych_profile_trait(
        repo_root,
        trait_id=trait_id,
        title=title,
        statement=statement,
        rationale=note,
    )

    return {
        "candidate_ref": target_candidate_ref,
        "profile_change_record_id": change_id,
        "ratification_approval_ref": approval_ref,
        "canonical_profile_trait_id": trait_id,
        "canonicalized_at": effective_from,
        "psych_profile_path": psych_profile_path,
        "change_type": change_record["change_type"],
        "profile_updated": True,
    }
