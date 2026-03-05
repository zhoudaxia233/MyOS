from __future__ import annotations

import json
from pathlib import Path

from guardrails import evaluate_guardrail, load_domain_guardrails

PASSING_PRECOMMIT_RESULTS = {"pass", "pass_with_cooldown"}


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
) -> dict:
    policy = load_domain_guardrails(repo_root)
    domains = policy.get("domains", {})
    domain_key = str(domain or "").strip().lower()
    if not domain_key:
        domain_key = "content"

    domain_policy = domains.get(domain_key, domains.get("content", {}))
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

    violations = [*precommit_violations, *guardrail_result.get("violations", [])]
    if precommit_violations or guardrail_result.get("status") == "blocked":
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
    }
