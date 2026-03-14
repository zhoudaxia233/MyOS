from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from math import ceil
from pathlib import Path
from typing import Any

from idgen import next_id_for_rel_path
from validators import append_jsonl

RUNTIME_MATURITY_HOURS = 24
RUNTIME_ELIGIBILITY_LOG_PATH = "modules/decision/logs/runtime_eligibility.jsonl"
RUNTIME_ARTIFACT_SINK_PATHS: dict[str, list[str]] = {
    "memory": ["modules/memory/logs/insight_candidates.jsonl"],
    "decision": [
        "modules/decision/logs/rule_candidates.jsonl",
        "modules/decision/logs/skill_candidates.jsonl",
    ],
    "profile": ["modules/profile/logs/profile_trait_candidates.jsonl"],
    "cognition": ["modules/cognition/logs/schema_candidates.jsonl"],
    "principles": ["modules/principles/logs/principle_candidates.jsonl"],
}

DEFAULT_SCOPE_BY_ARTIFACT_TYPE = {
    "insight": ["memory"],
    "rule": ["decision"],
    "skill": ["decision"],
    "profile_trait": ["profile"],
    "cognition_revision": ["cognition"],
    "principle": ["principles"],
}

DEFAULT_AUTONOMY_BY_ARTIFACT_TYPE = {
    "insight": "suggest_only",
    "rule": "suggest_only",
    "skill": "suggest_only",
    "profile_trait": "review_required",
    "cognition_revision": "review_required",
    "principle": "review_required",
}

DEFAULT_STATUS_BY_ARTIFACT_TYPE = {
    "insight": "eligible",
    "rule": "eligible",
    "skill": "eligible",
    "profile_trait": "holding",
    "cognition_revision": "holding",
    "principle": "holding",
}

RUNTIME_ELIGIBILITY_SCHEMA = {
    "_schema": {
        "name": "runtime_eligibility",
        "version": "1.0",
        "fields": [
            "id",
            "created_at",
            "status",
            "artifact_ref",
            "artifact_type",
            "candidate_ref",
            "approval_ref",
            "promotion_ref",
            "eligibility_status",
            "maturity_hours",
            "scope_modules",
            "autonomy_ceiling",
            "change_note",
            "replaces_eligibility_ref",
            "source_refs",
            "object_type",
            "proposal_target",
        ],
        "notes": "append-only",
    }
}


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


def _parse_iso8601(ts: str) -> datetime | None:
    text = str(ts or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


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


def _normalize_scope_modules(artifact_type: str, scope_modules: list[str] | None = None) -> list[str]:
    values = [str(item or "").strip() for item in (scope_modules or []) if str(item or "").strip()]
    if values:
        return _ordered_unique(values)
    return list(DEFAULT_SCOPE_BY_ARTIFACT_TYPE.get(str(artifact_type or "").strip(), []))


def _normalize_autonomy_ceiling(artifact_type: str, autonomy_ceiling: str | None = None) -> str:
    text = str(autonomy_ceiling or "").strip().lower()
    if text in {"suggest_only", "review_required", "auto_low_risk"}:
        return text
    return DEFAULT_AUTONOMY_BY_ARTIFACT_TYPE.get(str(artifact_type or "").strip(), "suggest_only")


def _normalize_eligibility_status(artifact_type: str, eligibility_status: str | None = None) -> str:
    text = str(eligibility_status or "").strip().lower()
    if text in {"holding", "eligible", "revoked"}:
        return text
    return DEFAULT_STATUS_BY_ARTIFACT_TYPE.get(str(artifact_type or "").strip(), "holding")


def _artifact_rows(repo_root: Path) -> dict[str, dict[str, Any]]:
    rows_by_id: dict[str, dict[str, Any]] = {}
    for sink_paths in RUNTIME_ARTIFACT_SINK_PATHS.values():
        for rel_path in sink_paths:
            module_name = Path(rel_path).parts[1] if len(Path(rel_path).parts) >= 2 else ""
            for row in _read_jsonl(repo_root / rel_path):
                if str(row.get("status", "")).strip().lower() != "active":
                    continue
                artifact_ref = str(row.get("id", "")).strip()
                if not artifact_ref:
                    continue
                enriched = dict(row)
                enriched["artifact_path"] = rel_path
                enriched["artifact_module"] = module_name
                rows_by_id[artifact_ref] = enriched
    return rows_by_id


def _promotion_rows_by_id(repo_root: Path) -> dict[str, dict[str, Any]]:
    rows = _read_jsonl(repo_root / "modules" / "decision" / "logs" / "learning_candidate_promotions.jsonl")
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        if str(row.get("status", "")).strip().lower() != "active":
            continue
        promotion_ref = str(row.get("id", "")).strip()
        if promotion_ref:
            out[promotion_ref] = row
    return out


def _latest_runtime_eligibility_by_artifact(repo_root: Path) -> dict[str, dict[str, Any]]:
    rows = _read_jsonl(repo_root / RUNTIME_ELIGIBILITY_LOG_PATH)
    latest: dict[str, dict[str, Any]] = {}
    for row in rows:
        if str(row.get("status", "")).strip().lower() != "active":
            continue
        artifact_ref = str(row.get("artifact_ref", "")).strip()
        if artifact_ref:
            latest[artifact_ref] = row
    return latest


def _build_runtime_eligibility_record(
    repo_root: Path,
    *,
    artifact_ref: str,
    artifact_type: str,
    candidate_ref: str | None,
    approval_ref: str | None,
    promotion_ref: str,
    proposal_target: str | None,
    scope_modules: list[str] | None = None,
    autonomy_ceiling: str | None = None,
    eligibility_status: str | None = None,
    maturity_hours: int = RUNTIME_MATURITY_HOURS,
    change_note: str | None = None,
    replaces_eligibility_ref: str | None = None,
    source_refs: list[str] | None = None,
) -> dict[str, Any]:
    normalized_type = str(artifact_type or "").strip() or "unknown"
    candidate_id = str(candidate_ref or "").strip() or None
    approval_id = str(approval_ref or "").strip() or None
    promotion_id = str(promotion_ref or "").strip()
    if not artifact_ref or not promotion_id:
        raise ValueError("artifact_ref and promotion_ref are required")

    return {
        "id": next_id_for_rel_path(repo_root, "re", RUNTIME_ELIGIBILITY_LOG_PATH),
        "created_at": _utc_now(),
        "status": "active",
        "artifact_ref": str(artifact_ref).strip(),
        "artifact_type": normalized_type,
        "candidate_ref": candidate_id,
        "approval_ref": approval_id,
        "promotion_ref": promotion_id,
        "eligibility_status": _normalize_eligibility_status(normalized_type, eligibility_status),
        "maturity_hours": max(0, int(maturity_hours)),
        "scope_modules": _normalize_scope_modules(normalized_type, scope_modules),
        "autonomy_ceiling": _normalize_autonomy_ceiling(normalized_type, autonomy_ceiling),
        "change_note": str(change_note or "").strip() or None,
        "replaces_eligibility_ref": str(replaces_eligibility_ref or "").strip() or None,
        "source_refs": _ordered_unique([str(item) for item in (source_refs or []) if str(item).strip()]),
        "object_type": "decision",
        "proposal_target": str(proposal_target or "").strip() or None,
    }


def _append_runtime_eligibility_record(repo_root: Path, record: dict[str, Any]) -> dict[str, Any]:
    append_jsonl(repo_root / RUNTIME_ELIGIBILITY_LOG_PATH, record, schema_header=RUNTIME_ELIGIBILITY_SCHEMA)
    return record


def create_promotion_runtime_eligibility(
    repo_root: Path,
    *,
    candidate: dict[str, Any],
    artifact_ref: str,
    promotion_ref: str,
    approval_ref: str | None,
) -> dict[str, Any]:
    artifact_type = str(candidate.get("candidate_type", "")).strip() or "unknown"
    candidate_ref = str(candidate.get("id", "")).strip() or None
    proposal_target = str(candidate.get("proposal_target", "")).strip() or None
    record = _build_runtime_eligibility_record(
        repo_root,
        artifact_ref=artifact_ref,
        artifact_type=artifact_type,
        candidate_ref=candidate_ref,
        approval_ref=approval_ref,
        promotion_ref=promotion_ref,
        proposal_target=proposal_target,
        source_refs=[candidate_ref or "", promotion_ref, approval_ref or ""],
    )
    return _append_runtime_eligibility_record(repo_root, record)


def seed_missing_runtime_eligibility(repo_root: Path) -> list[dict[str, Any]]:
    latest_by_artifact = _latest_runtime_eligibility_by_artifact(repo_root)
    promotions_by_id = _promotion_rows_by_id(repo_root)
    artifact_rows = _artifact_rows(repo_root)

    created: list[dict[str, Any]] = []
    for artifact_ref, artifact in artifact_rows.items():
        if artifact_ref in latest_by_artifact:
            continue
        promotion_ref = str(artifact.get("promotion_ref", "")).strip()
        if not promotion_ref or promotion_ref not in promotions_by_id:
            continue
        record = _build_runtime_eligibility_record(
            repo_root,
            artifact_ref=artifact_ref,
            artifact_type=str(artifact.get("candidate_type", "")).strip() or "unknown",
            candidate_ref=str(artifact.get("candidate_ref", "")).strip() or None,
            approval_ref=str(artifact.get("approval_ref", "")).strip() or None,
            promotion_ref=promotion_ref,
            proposal_target=str(artifact.get("proposal_target", "")).strip() or None,
            change_note="seeded_from_promotion",
            source_refs=[
                str(artifact.get("candidate_ref", "")).strip(),
                promotion_ref,
                str(artifact.get("approval_ref", "")).strip(),
            ],
        )
        created.append(_append_runtime_eligibility_record(repo_root, record))

    return created


def list_runtime_eligibility(
    repo_root: Path,
    *,
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    now = now or datetime.now(timezone.utc)
    seed_missing_runtime_eligibility(repo_root)

    latest_by_artifact = _latest_runtime_eligibility_by_artifact(repo_root)
    promotions_by_id = _promotion_rows_by_id(repo_root)
    artifact_rows = _artifact_rows(repo_root)

    rows: list[dict[str, Any]] = []
    for artifact_ref, eligibility in latest_by_artifact.items():
        artifact = artifact_rows.get(artifact_ref, {})
        artifact_type = str(eligibility.get("artifact_type", "")).strip() or str(artifact.get("candidate_type", "")).strip()
        promotion_ref = str(eligibility.get("promotion_ref", "")).strip() or str(artifact.get("promotion_ref", "")).strip()
        promotion = promotions_by_id.get(promotion_ref, {})
        scope_modules = _normalize_scope_modules(
            artifact_type,
            eligibility.get("scope_modules") if isinstance(eligibility.get("scope_modules"), list) else None,
        )
        maturity_hours = max(0, int(eligibility.get("maturity_hours", RUNTIME_MATURITY_HOURS) or RUNTIME_MATURITY_HOURS))
        eligibility_status = _normalize_eligibility_status(artifact_type, str(eligibility.get("eligibility_status", "")).strip())
        promoted_at = str(promotion.get("created_at", "")).strip() or None
        promotion_created = _parse_iso8601(promoted_at or "")

        runtime_state = "holding"
        runtime_hours_remaining: int | None = None
        runtime_active = False
        if eligibility_status == "revoked":
            runtime_state = "revoked"
        elif eligibility_status == "eligible":
            if promotion_created is None:
                runtime_state = "cooling"
                runtime_hours_remaining = maturity_hours
            else:
                age_hours = max(0.0, (now - promotion_created).total_seconds() / 3600.0)
                if age_hours >= maturity_hours:
                    runtime_state = "active"
                    runtime_hours_remaining = 0
                    runtime_active = True
                else:
                    runtime_state = "cooling"
                    runtime_hours_remaining = max(0, int(ceil(maturity_hours - age_hours)))

        rows.append(
            {
                "eligibility_ref": str(eligibility.get("id", "")).strip() or None,
                "created_at": str(eligibility.get("created_at", "")).strip() or None,
                "artifact_ref": artifact_ref,
                "artifact_type": artifact_type or "unknown",
                "candidate_ref": str(eligibility.get("candidate_ref", "")).strip() or str(artifact.get("candidate_ref", "")).strip() or None,
                "approval_ref": str(eligibility.get("approval_ref", "")).strip() or str(artifact.get("approval_ref", "")).strip() or None,
                "promotion_ref": promotion_ref or None,
                "proposal_target": str(eligibility.get("proposal_target", "")).strip()
                or str(artifact.get("proposal_target", "")).strip()
                or None,
                "title": str(artifact.get("title", "")).strip() or None,
                "statement": str(artifact.get("statement", "")).strip() or None,
                "artifact_path": str(artifact.get("artifact_path", "")).strip() or None,
                "artifact_module": str(artifact.get("artifact_module", "")).strip() or None,
                "eligibility_status": eligibility_status,
                "runtime_eligibility_status": eligibility_status,
                "runtime_state": runtime_state,
                "runtime_active": runtime_active,
                "runtime_hours_remaining": runtime_hours_remaining,
                "maturity_hours": maturity_hours,
                "scope_modules": scope_modules,
                "autonomy_ceiling": _normalize_autonomy_ceiling(
                    artifact_type,
                    str(eligibility.get("autonomy_ceiling", "")).strip(),
                ),
                "change_note": str(eligibility.get("change_note", "")).strip() or None,
                "runtime_change_note": str(eligibility.get("change_note", "")).strip() or None,
                "replaces_eligibility_ref": str(eligibility.get("replaces_eligibility_ref", "")).strip() or None,
                "promoted_at": promoted_at,
            }
        )

    rows.sort(key=lambda row: str(row.get("promoted_at") or row.get("created_at") or ""), reverse=True)
    return rows


def candidate_runtime_eligibility_map(
    repo_root: Path,
    *,
    now: datetime | None = None,
) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in list_runtime_eligibility(repo_root, now=now):
        candidate_ref = str(row.get("candidate_ref", "")).strip()
        if candidate_ref:
            out[candidate_ref] = row
    return out


def list_runtime_influence_candidates(
    repo_root: Path,
    module: str,
    *,
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    target_module = str(module or "").strip()
    if not target_module:
        return []
    return [
        row
        for row in list_runtime_eligibility(repo_root, now=now)
        if row.get("runtime_active") is True and target_module in (row.get("scope_modules") or [])
    ]


def summarize_runtime_eligibility(
    repo_root: Path,
    *,
    now: datetime | None = None,
    limit: int = 6,
) -> dict[str, Any]:
    rows = list_runtime_eligibility(repo_root, now=now)
    status_counter = Counter(str(row.get("eligibility_status", "")).strip() or "holding" for row in rows)
    state_counter = Counter(str(row.get("runtime_state", "")).strip() or "holding" for row in rows)

    preview: list[dict[str, Any]] = []
    for row in rows[: max(1, int(limit))]:
        preview.append(
            {
                "artifact_ref": row.get("artifact_ref"),
                "artifact_type": row.get("artifact_type"),
                "title": row.get("title"),
                "eligibility_status": row.get("eligibility_status"),
                "runtime_state": row.get("runtime_state"),
                "scope_modules": row.get("scope_modules"),
                "autonomy_ceiling": row.get("autonomy_ceiling"),
                "runtime_hours_remaining": row.get("runtime_hours_remaining"),
            }
        )

    return {
        "total": len(rows),
        "eligible_total": int(status_counter.get("eligible", 0)),
        "holding_total": int(status_counter.get("holding", 0)),
        "revoked_total": int(status_counter.get("revoked", 0)),
        "active_total": int(state_counter.get("active", 0)),
        "cooling_total": int(state_counter.get("cooling", 0)),
        "preview": preview,
    }


def set_runtime_eligibility(
    repo_root: Path,
    *,
    candidate_ref: str,
    eligibility_status: str,
    change_note: str,
) -> dict[str, Any]:
    target_candidate_ref = str(candidate_ref or "").strip()
    if not target_candidate_ref:
        raise ValueError("candidate_ref is required")

    normalized_status = _normalize_eligibility_status("unknown", eligibility_status)
    if normalized_status not in {"holding", "eligible", "revoked"}:
        raise ValueError("eligibility_status must be one of: holding, eligible, revoked")

    note = str(change_note or "").strip()
    if not note:
        raise ValueError("change_note is required")

    current = candidate_runtime_eligibility_map(repo_root).get(target_candidate_ref)
    if current is None:
        raise ValueError("runtime eligibility not found for candidate; promote it first")

    record = _build_runtime_eligibility_record(
        repo_root,
        artifact_ref=str(current.get("artifact_ref", "")).strip(),
        artifact_type=str(current.get("artifact_type", "")).strip() or "unknown",
        candidate_ref=target_candidate_ref,
        approval_ref=str(current.get("approval_ref", "")).strip() or None,
        promotion_ref=str(current.get("promotion_ref", "")).strip(),
        proposal_target=str(current.get("proposal_target", "")).strip() or None,
        scope_modules=list(current.get("scope_modules", [])) if isinstance(current.get("scope_modules"), list) else None,
        autonomy_ceiling=str(current.get("autonomy_ceiling", "")).strip() or None,
        eligibility_status=normalized_status,
        maturity_hours=int(current.get("maturity_hours", RUNTIME_MATURITY_HOURS) or RUNTIME_MATURITY_HOURS),
        change_note=note,
        replaces_eligibility_ref=str(current.get("eligibility_ref", "")).strip() or None,
        source_refs=[
            target_candidate_ref,
            str(current.get("promotion_ref", "")).strip(),
            str(current.get("eligibility_ref", "")).strip(),
        ],
    )
    _append_runtime_eligibility_record(repo_root, record)
    updated = candidate_runtime_eligibility_map(repo_root).get(target_candidate_ref)
    if updated is None:
        raise ValueError("runtime eligibility update failed")
    return updated
