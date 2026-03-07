from __future__ import annotations

import json
import re
from pathlib import Path

from guardrails import evaluate_guardrail, load_domain_guardrails

PASSING_PRECOMMIT_RESULTS = {"pass", "pass_with_cooldown"}
ID_RE = re.compile(r"^[a-z][a-z0-9]*_[0-9]{8}_[0-9]{3}$")
PRINCIPLE_CLAUSE_RE = re.compile(r"^pr_[0-9]{4}$")


def _read_jsonl_records(path: Path) -> list[dict]:
    if not path.exists() or not path.is_file():
        return []

    records: list[dict] = []
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
            records.append(obj)
    return records


def _find_by_id(path: Path, record_id: str | None) -> dict | None:
    if not record_id:
        return None
    for record in _read_jsonl_records(path):
        if str(record.get("id", "")).strip() == record_id:
            return record
    return None


def _normalize_refs(refs: list[str] | None) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for raw in refs or []:
        value = str(raw).strip()
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


def _load_constitution_clause_ids(repo_root: Path) -> tuple[bool, set[str]]:
    path = repo_root / "modules/principles/data/constitution.yaml"
    if not path.exists() or not path.is_file():
        return False, set()

    clause_ids: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if "clause_id:" not in line:
            continue
        _, value = line.split(":", 1)
        clause = value.strip().strip('"').strip("'")
        if clause:
            clause_ids.add(clause)
    return True, clause_ids


def _validate_principle_refs(repo_root: Path, refs: list[str] | None) -> tuple[list[str], list[str]]:
    normalized = _normalize_refs(refs)
    violations: list[str] = []
    constitution_exists, clause_ids = _load_constitution_clause_ids(repo_root)

    for ref in normalized:
        if not PRINCIPLE_CLAUSE_RE.match(ref):
            violations.append(f"invalid_principle_ref_format:{ref}")
            continue
        if constitution_exists and clause_ids and ref not in clause_ids:
            violations.append(f"unknown_principle_ref:{ref}")

    return normalized, violations


def _validate_exception_ref(repo_root: Path, exception_ref: str | None) -> tuple[str | None, list[str], list[str]]:
    ref = str(exception_ref or "").strip() or None
    if ref is None:
        return None, [], []

    violations: list[str] = []
    source_refs: list[str] = []
    if not ID_RE.match(ref):
        violations.append(f"invalid_exception_ref_format:{ref}")
        return ref, violations, source_refs

    path = repo_root / "modules/principles/logs/principle_exceptions.jsonl"
    if not path.exists() or not path.is_file():
        violations.append("exception_ref_log_missing")
        return ref, violations, source_refs

    record = _find_by_id(path, ref)
    if record is None:
        violations.append("exception_ref_not_found")
        return ref, violations, source_refs

    if str(record.get("status", "active")).strip().lower() != "active":
        violations.append("exception_ref_not_active")
        return ref, violations, source_refs

    source_refs.append(ref)
    return ref, violations, source_refs


def evaluate_decision_entry_gate(
    repo_root: Path,
    *,
    domain: str,
    guardrail_check_id: str | None,
    downside: str | None,
    invalidation_condition: str | None,
    max_loss: str | None,
    disconfirming_signal: str | None,
    emotional_weight: int,
    cooldown_applied: bool,
    cooldown_hours: int,
    override_requested: bool,
    override_reason: str | None,
    owner_confirmation: str | None,
    principle_refs: list[str] | None,
    exception_ref: str | None,
) -> dict:
    policy = load_domain_guardrails(repo_root)
    domains = policy.get("domains", {})
    domain_key = str(domain or "").strip().lower()
    if not domain_key:
        domain_key = "content"

    domain_policy = domains.get(domain_key, domains.get("content", {}))
    global_policy = policy.get("global", {})
    precommit_required = bool(domain_policy.get("require_precommit", False))

    precommit_path = repo_root / "modules/decision/logs/precommit_checks.jsonl"
    precommit_record = _find_by_id(precommit_path, guardrail_check_id)
    precommit_status = "not_required"
    precommit_violations: list[str] = []
    source_refs: list[str] = []

    if precommit_required:
        precommit_status = "missing"
        if not guardrail_check_id:
            precommit_violations.append("precommit_ref_missing")
        elif precommit_record is None:
            precommit_violations.append("precommit_ref_not_found")
        else:
            precommit_status = str(precommit_record.get("result", "")).strip().lower() or "unknown"
            if str(precommit_record.get("status", "active")).strip().lower() != "active":
                precommit_violations.append("precommit_not_active")
            precommit_domain = str(precommit_record.get("domain", "")).strip().lower()
            if precommit_domain and precommit_domain != domain_key:
                precommit_violations.append("precommit_domain_mismatch")
            if precommit_status not in PASSING_PRECOMMIT_RESULTS:
                precommit_violations.append(f"precommit_not_pass:{precommit_status}")

            precommit_id = str(precommit_record.get("id", "")).strip()
            if precommit_id:
                source_refs.append(precommit_id)

    principle_refs_norm, principle_ref_violations = _validate_principle_refs(repo_root, principle_refs)
    exception_ref_norm, exception_ref_violations, principle_source_refs = _validate_exception_ref(repo_root, exception_ref)

    require_principle_context = bool(global_policy.get("require_principle_ref_when_precommit_required", True))
    allow_exception_without_principle_ref = bool(global_policy.get("allow_exception_ref_without_principle_ref", True))

    principle_violations: list[str] = []
    if precommit_required and require_principle_context:
        if not principle_refs_norm and not exception_ref_norm:
            principle_violations.append("missing_principle_context")
        if exception_ref_norm and not allow_exception_without_principle_ref and not principle_refs_norm:
            principle_violations.append("missing_principle_ref")

    payload = {
        "guardrail_check_id": guardrail_check_id,
        "downside": downside,
        "invalidation_condition": invalidation_condition,
        "max_loss": max_loss,
        "disconfirming_signal": disconfirming_signal,
        "emotional_weight": emotional_weight,
        "cooldown_applied": cooldown_applied,
        "cooldown_hours": cooldown_hours,
        "override_requested": override_requested,
        "override_reason": override_reason,
        "owner_confirmation": owner_confirmation,
    }
    guardrail_result = evaluate_guardrail(policy, domain_key, payload)

    violations = [
        *precommit_violations,
        *guardrail_result.get("violations", []),
        *principle_ref_violations,
        *exception_ref_violations,
        *principle_violations,
    ]

    principle_context_blocked = bool(principle_ref_violations or exception_ref_violations or principle_violations)

    if principle_source_refs:
        source_refs.extend(principle_source_refs)

    if precommit_violations or principle_context_blocked or guardrail_result.get("status") == "blocked":
        gate_status = "blocked"
    elif guardrail_result.get("status") == "override_accepted":
        gate_status = "override_accepted"
    else:
        gate_status = "pass"

    return {
        "domain": domain_key,
        "guardrail_check_id": guardrail_check_id,
        "precommit_required": precommit_required,
        "precommit_status": precommit_status,
        "guardrail_status": guardrail_result.get("status", "blocked"),
        "gate_status": gate_status,
        "violations": violations,
        "missing_override_fields": guardrail_result.get("missing_override_fields", []),
        "cooldown_required": bool(guardrail_result.get("cooldown_required", False)),
        "required_cooldown_hours": int(guardrail_result.get("required_cooldown_hours", 0) or 0),
        "source_refs": source_refs,
        "principle_refs": principle_refs_norm,
        "exception_ref": exception_ref_norm,
        "principle_context_status": "blocked" if principle_context_blocked else "pass",
        "principle_violations": [*principle_ref_violations, *exception_ref_violations, *principle_violations],
        "principle_source_refs": principle_source_refs,
    }
