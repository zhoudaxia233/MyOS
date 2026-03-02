from __future__ import annotations

from pathlib import Path

DEFAULT_POLICY = {
    "domains": {
        "invest": {
            "require_precommit": True,
            "require_guardrail_check_id": True,
            "max_emotional_without_cooldown": 6,
            "required_fields": ["downside", "invalidation_condition", "max_loss", "disconfirming_signal"],
            "allow_override": True,
            "override_required_fields": ["override_reason", "owner_confirmation"],
        },
        "project": {
            "require_precommit": True,
            "require_guardrail_check_id": False,
            "max_emotional_without_cooldown": 7,
            "required_fields": ["downside", "invalidation_condition"],
            "allow_override": True,
            "override_required_fields": ["override_reason", "owner_confirmation"],
        },
        "content": {
            "require_precommit": False,
            "require_guardrail_check_id": False,
            "max_emotional_without_cooldown": 8,
            "required_fields": [],
            "allow_override": False,
            "override_required_fields": [],
        },
    },
    "global": {
        "block_when_missing_required_fields": True,
        "block_when_high_emotion_without_cooldown": True,
    },
}


def _parse_scalar(v: str):
    val = v.strip().strip('"').strip("'")
    if val.lower() in {"true", "false"}:
        return val.lower() == "true"
    if val.isdigit():
        return int(val)
    if val == "[]":
        return []
    return val


def load_domain_guardrails(repo_root: Path) -> dict:
    path = repo_root / "modules/decision/data/domain_guardrails.yaml"
    if not path.exists():
        return DEFAULT_POLICY

    data = {"domains": {}, "global": {}}
    section = None
    current_domain = None
    current_list_key = None

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped == "domains:":
            section = "domains"
            current_domain = None
            current_list_key = None
            continue
        if stripped == "global:":
            section = "global"
            current_domain = None
            current_list_key = None
            continue

        if section == "domains":
            if line.startswith("  ") and stripped.endswith(":") and not line.startswith("    "):
                current_domain = stripped[:-1]
                data["domains"][current_domain] = {}
                current_list_key = None
                continue

            if current_domain and line.startswith("    ") and ":" in stripped and not line.startswith("      - "):
                k, v = stripped.split(":", 1)
                key = k.strip()
                val = v.strip()
                parsed = _parse_scalar(val) if val else None
                if parsed is None:
                    data["domains"][current_domain][key] = []
                    current_list_key = key
                else:
                    data["domains"][current_domain][key] = parsed
                    current_list_key = None
                continue

            if current_domain and current_list_key and line.startswith("      - "):
                item = stripped[2:].strip().strip('"').strip("'")
                data["domains"][current_domain][current_list_key].append(item)
                continue

        if section == "global" and line.startswith("  ") and ":" in stripped:
            k, v = stripped.split(":", 1)
            data["global"][k.strip()] = _parse_scalar(v)

    out = DEFAULT_POLICY.copy()
    out_domains = {**DEFAULT_POLICY["domains"], **data.get("domains", {})}
    out_global = {**DEFAULT_POLICY["global"], **data.get("global", {})}

    for domain, policy in out_domains.items():
        base = DEFAULT_POLICY["domains"].get("content", {})
        merged = {**base, **policy}
        if not isinstance(merged.get("required_fields"), list):
            merged["required_fields"] = []
        if not isinstance(merged.get("override_required_fields"), list):
            merged["override_required_fields"] = []
        out_domains[domain] = merged

    return {"domains": out_domains, "global": out_global}


def evaluate_guardrail(policy: dict, domain: str, payload: dict) -> dict:
    domains = policy.get("domains", {})
    global_policy = policy.get("global", {})

    domain_key = domain.lower().strip()
    p = domains.get(domain_key, domains.get("content", {}))

    violations: list[str] = []

    if p.get("require_precommit", False):
        missing = [f for f in p.get("required_fields", []) if not payload.get(f)]
        if missing:
            violations.append(f"missing_required_fields:{','.join(missing)}")

    if p.get("require_guardrail_check_id", False) and not payload.get("guardrail_check_id"):
        violations.append("missing_guardrail_check_id")

    emotional_weight = int(payload.get("emotional_weight", 0) or 0)
    threshold = int(p.get("max_emotional_without_cooldown", 7) or 7)
    cooldown_required = emotional_weight >= threshold
    cooldown_applied = bool(payload.get("cooldown_applied", False))

    if cooldown_required and not cooldown_applied and global_policy.get("block_when_high_emotion_without_cooldown", True):
        violations.append("high_emotion_without_cooldown")

    override_requested = bool(payload.get("override_requested", False)) or bool(payload.get("override_reason"))
    override_allowed = bool(p.get("allow_override", False))

    missing_override_fields = []
    if override_requested:
        missing_override_fields = [f for f in p.get("override_required_fields", []) if not payload.get(f)]

    if not violations:
        status = "pass"
    elif override_requested and override_allowed and not missing_override_fields:
        status = "override_accepted"
    elif override_requested and (not override_allowed or missing_override_fields):
        status = "blocked"
    else:
        status = "blocked"

    return {
        "status": status,
        "domain": domain_key,
        "violations": violations,
        "cooldown_required": cooldown_required,
        "missing_override_fields": missing_override_fields,
        "override_allowed": override_allowed,
    }
