from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from manifests import load_module_manifest
from scheduling import load_cadence

REF_RE = re.compile(r"(?:core|modules|routines|orchestrator)/[A-Za-z0-9_./-]+\.(?:md|yaml|yml|jsonl|json)")
ID_RE = re.compile(r"^[a-z][a-z0-9]*_[0-9]{8}_[0-9]{3}$")
VALID_STATUS = {"active", "archived"}


def _error(code: str, path: str, message: str) -> dict:
    return {"code": code, "path": path, "message": message}


def _warn(code: str, path: str, message: str) -> dict:
    return {"code": code, "path": path, "message": message}


def _extract_refs(text: str) -> list[str]:
    refs: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        for match in REF_RE.findall(line):
            rel = match.strip()
            if "<" in rel or ">" in rel or "*" in rel:
                continue
            refs.append(rel)
    dedup: list[str] = []
    seen: set[str] = set()
    for ref in refs:
        if ref in seen:
            continue
        seen.add(ref)
        dedup.append(ref)
    return dedup


def _is_iso_utc(ts: str) -> bool:
    if not isinstance(ts, str):
        return False
    if not ts.endswith("Z"):
        return False
    try:
        datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _validate_jsonl_schema(path: Path, errors: list[dict]) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        errors.append(_error("jsonl.empty", str(path), "JSONL file is empty; expected schema header on line 1."))
        return []

    first = lines[0].strip()
    if not first:
        errors.append(_error("jsonl.header_blank", str(path), "Line 1 is blank; expected schema header object."))
        return []

    try:
        obj = json.loads(first)
    except json.JSONDecodeError:
        errors.append(_error("jsonl.header_not_json", str(path), "Line 1 is not valid JSON schema header."))
        return []

    if not isinstance(obj, dict) or "_schema" not in obj or not isinstance(obj["_schema"], dict):
        errors.append(_error("jsonl.schema_missing", str(path), "Schema header must contain an object at key '_schema'."))
        return []

    schema = obj["_schema"]
    for key in ["name", "version", "fields", "notes"]:
        if key not in schema:
            errors.append(_error("jsonl.schema_field_missing", str(path), f"Schema header missing required field '{key}'."))
            return []

    fields = schema.get("fields")
    if not isinstance(fields, list):
        errors.append(_error("jsonl.schema_fields_type", str(path), "Schema 'fields' must be an array."))
        return []

    if not all(isinstance(f, str) and f.strip() for f in fields):
        errors.append(_error("jsonl.schema_fields_invalid", str(path), "Schema 'fields' must be non-empty strings."))
        return []

    if len(set(fields)) != len(fields):
        errors.append(_error("jsonl.schema_fields_duplicate", str(path), "Schema 'fields' contains duplicates."))
        return []

    return [str(f) for f in fields]


def _collect_known_ids(log_files: list[Path]) -> set[str]:
    ids: set[str] = set()
    for path in log_files:
        if not path.exists() or not path.is_file():
            continue
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
            if isinstance(obj, dict) and isinstance(obj.get("id"), str):
                ids.add(obj["id"])
    return ids


def _validate_jsonl_records(
    path: Path,
    fields: list[str],
    known_ids: set[str],
    errors: list[dict],
    warnings: list[dict],
    checked: dict,
) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, raw in enumerate(lines[1:], start=2):
        line = raw.strip()
        if not line:
            continue

        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            errors.append(_error("jsonl.record_not_json", f"{path}:{i}", "Record line is not valid JSON."))
            continue

        if not isinstance(obj, dict):
            errors.append(_error("jsonl.record_not_object", f"{path}:{i}", "Record line must be a JSON object."))
            continue

        checked["records"] += 1

        missing_fields = [f for f in fields if f not in obj]
        if missing_fields:
            errors.append(
                _error(
                    "jsonl.record_missing_fields",
                    f"{path}:{i}",
                    f"Record is missing schema fields: {', '.join(missing_fields)}",
                )
            )

        extra_fields = sorted([k for k in obj if k not in fields])
        if extra_fields:
            warnings.append(
                _warn(
                    "jsonl.record_extra_fields",
                    f"{path}:{i}",
                    f"Record has fields not listed in schema: {', '.join(extra_fields)}",
                )
            )

        if "id" in obj:
            rid = obj.get("id")
            if not isinstance(rid, str) or not ID_RE.match(rid):
                errors.append(
                    _error(
                        "jsonl.id_format",
                        f"{path}:{i}",
                        "Field 'id' must match <prefix>_<YYYYMMDD>_<3-digit-seq>.",
                    )
                )

        if "created_at" in obj:
            created_at = obj.get("created_at")
            if not isinstance(created_at, str) or not _is_iso_utc(created_at):
                errors.append(
                    _error(
                        "jsonl.created_at_format",
                        f"{path}:{i}",
                        "Field 'created_at' must be ISO8601 UTC with Z suffix.",
                    )
                )

        if "updated_at" in obj and obj.get("updated_at") is not None:
            updated_at = obj.get("updated_at")
            if not isinstance(updated_at, str) or not _is_iso_utc(updated_at):
                errors.append(
                    _error(
                        "jsonl.updated_at_format",
                        f"{path}:{i}",
                        "Field 'updated_at' must be ISO8601 UTC with Z suffix when present.",
                    )
                )

        if "status" in obj:
            status = obj.get("status")
            if status not in VALID_STATUS:
                errors.append(
                    _error(
                        "jsonl.status_value",
                        f"{path}:{i}",
                        "Field 'status' must be 'active' or 'archived'.",
                    )
                )

        if "source_refs" in obj:
            refs = obj.get("source_refs")
            if not isinstance(refs, list):
                errors.append(
                    _error(
                        "jsonl.source_refs_type",
                        f"{path}:{i}",
                        "Field 'source_refs' must be an array of IDs.",
                    )
                )
            else:
                for ref in refs:
                    if not isinstance(ref, str) or not ID_RE.match(ref):
                        errors.append(
                            _error(
                                "jsonl.source_ref_format",
                                f"{path}:{i}",
                                f"Invalid source ref ID format: {ref}",
                            )
                        )
                        continue
                    if ref not in known_ids:
                        errors.append(
                            _error(
                                "jsonl.source_ref_unknown",
                                f"{path}:{i}",
                                f"source_refs contains unknown ID: {ref}",
                            )
                        )


def _validate_manifest(repo_root: Path, module_name: str, module_dir: Path, errors: list[dict], warnings: list[dict]) -> None:
    manifest_path = module_dir / "module.manifest.yaml"
    if not manifest_path.exists() or not manifest_path.is_file():
        return

    try:
        manifest = load_module_manifest(repo_root, module_name)
    except (ValueError, json.JSONDecodeError) as exc:
        errors.append(_error("manifest.invalid", str(manifest_path), str(exc)))
        return

    if str(manifest.get("module", "")).strip() != module_name:
        errors.append(
            _error(
                "manifest.module_mismatch",
                str(manifest_path),
                f"Manifest module must match directory name '{module_name}'.",
            )
        )

    keywords = manifest.get("routing", {}).get("keywords", [])
    if module_name != "_template" and not keywords:
        warnings.append(_warn("manifest.no_keywords", str(manifest_path), "No routing keywords configured."))

    planning = manifest.get("planning", {})
    default_skill = str(planning.get("default_skill", "MODULE")).strip()
    if default_skill and default_skill != "MODULE":
        default_skill_path = repo_root / f"modules/{module_name}/skills/{default_skill}.md"
        if not default_skill_path.exists():
            errors.append(
                _error(
                    "manifest.default_skill_missing",
                    str(manifest_path),
                    f"Default skill not found: modules/{module_name}/skills/{default_skill}.md",
                )
            )

    rule_ids: set[str] = set()
    for rule in planning.get("rules", []):
        rule_id = str(rule.get("id", "")).strip() or "<unknown>"
        if rule_id in rule_ids:
            warnings.append(_warn("manifest.rule_duplicate", str(manifest_path), f"Duplicate rule id: {rule_id}"))
        rule_ids.add(rule_id)

        skill = str(rule.get("skill", "")).strip()
        if not skill:
            errors.append(_error("manifest.rule_skill_missing", str(manifest_path), f"Rule '{rule_id}' missing skill."))
            continue

        skill_path = repo_root / f"modules/{module_name}/skills/{skill}.md"
        if not skill_path.exists():
            errors.append(
                _error(
                    "manifest.rule_skill_not_found",
                    str(manifest_path),
                    f"Rule '{rule_id}' skill not found: modules/{module_name}/skills/{skill}.md",
                )
            )


def _validate_module(
    repo_root: Path,
    module_dir: Path,
    errors: list[dict],
    warnings: list[dict],
    checked: dict,
) -> list[Path]:
    module_name = module_dir.name
    module_rel = str(module_dir.relative_to(repo_root))

    required_files = [module_dir / "MODULE.md", module_dir / "module.manifest.yaml"]
    required_dirs = [module_dir / "data", module_dir / "logs", module_dir / "skills", module_dir / "outputs"]

    for path in required_files:
        if not path.exists() or not path.is_file():
            errors.append(_error("module.missing_file", str(path), "Required file missing."))
    for path in required_dirs:
        if not path.exists() or not path.is_dir():
            errors.append(_error("module.missing_dir", str(path), "Required directory missing."))

    _validate_manifest(repo_root, module_name, module_dir, errors, warnings)

    skills_dir = module_dir / "skills"
    if skills_dir.exists() and skills_dir.is_dir():
        skill_files = sorted(skills_dir.glob("*.md"))
        if module_name != "_template" and not skill_files:
            warnings.append(_warn("module.no_skills", module_rel, "No markdown skill files found."))
        for skill in skill_files:
            checked["skills"] += 1
            skill_text = skill.read_text(encoding="utf-8")
            refs = _extract_refs(skill_text)
            for ref in refs:
                ref_path = repo_root / ref
                if not ref_path.exists():
                    errors.append(_error("skill.ref_missing", str(skill), f"Referenced file does not exist: {ref}"))
                    continue
                if ref.startswith("modules/") and not ref.startswith(f"modules/{module_name}/"):
                    errors.append(
                        _error(
                            "skill.cross_module_ref",
                            str(skill),
                            f"Cross-module file reference is not allowed in plugin contract: {ref}",
                        )
                    )

    logs_dir = module_dir / "logs"
    log_files = sorted(logs_dir.glob("*.jsonl")) if logs_dir.exists() and logs_dir.is_dir() else []
    if module_name != "_template" and not log_files:
        warnings.append(_warn("module.no_logs", module_rel, "No JSONL logs found in logs/ directory."))

    checked["jsonl"] += len(log_files)
    return log_files


def _validate_routes(repo_root: Path, errors: list[dict], warnings: list[dict]) -> set[str]:
    path = repo_root / "orchestrator/config/routes.json"
    if not path.exists():
        warnings.append(_warn("routes.missing", str(path), "Legacy routes config file not found; manifest routing is active."))
        return set()

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        errors.append(_error("routes.invalid_json", str(path), "Route config is not valid JSON."))
        return set()

    if not isinstance(payload, dict):
        errors.append(_error("routes.invalid_shape", str(path), "Route config root must be an object."))
        return set()

    if "default_module" not in payload:
        warnings.append(_warn("routes.default_missing", str(path), "Missing key: default_module."))

    routes = payload.get("routes")
    if not isinstance(routes, list):
        warnings.append(_warn("routes.list_missing", str(path), "Missing key: routes (array)."))
        return set()

    modules: set[str] = set()
    seen_modules: set[str] = set()
    for i, item in enumerate(routes):
        if not isinstance(item, dict):
            errors.append(_error("routes.item_type", str(path), f"Route item #{i} is not an object."))
            continue
        module = str(item.get("module", "")).strip()
        keywords = item.get("keywords")
        if not module:
            errors.append(_error("routes.module_missing", str(path), f"Route item #{i} missing module."))
            continue
        if not isinstance(keywords, list) or not keywords:
            errors.append(_error("routes.keywords_missing", str(path), f"Route item '{module}' has empty keywords."))
            continue
        if module in seen_modules:
            warnings.append(_warn("routes.duplicate_module", str(path), f"Duplicate route module entry: {module}"))
        seen_modules.add(module)
        modules.add(module)

    default_module = str(payload.get("default_module", "")).strip()
    if default_module:
        modules.add(default_module)
    return modules


def _validate_cadence(repo_root: Path, errors: list[dict], checked: dict) -> None:
    cadence_path = repo_root / "routines/cadence.yaml"
    try:
        cadence = load_cadence(repo_root)
    except (FileNotFoundError, ValueError) as exc:
        errors.append(_error("cadence.invalid", str(cadence_path), str(exc)))
        return

    for cycle in ("daily", "weekly", "monthly"):
        for item in cadence.get(cycle, []):
            module = str(item.get("module", "")).strip()
            skill = str(item.get("skill", "")).strip()
            if not module or not skill:
                continue
            module_dir = repo_root / f"modules/{module}"
            if not module_dir.exists():
                errors.append(
                    _error(
                        "cadence.module_missing",
                        str(cadence_path),
                        f"Routine '{item.get('id')}' references missing module: {module}",
                    )
                )
            skill_path = repo_root / f"modules/{module}/skills/{skill}.md"
            if not skill_path.exists():
                errors.append(
                    _error(
                        "cadence.skill_missing",
                        str(cadence_path),
                        f"Routine '{item.get('id')}' references missing skill: modules/{module}/skills/{skill}.md",
                    )
                )
            checked["routines"] += 1


def validate_repo(repo_root: Path) -> dict:
    errors: list[dict] = []
    warnings: list[dict] = []
    checked = {"modules": 0, "skills": 0, "jsonl": 0, "records": 0, "routines": 0}

    modules_root = repo_root / "modules"
    if not modules_root.exists() or not modules_root.is_dir():
        errors.append(_error("modules.missing", str(modules_root), "modules/ directory is missing."))
        return {"ok": False, "errors": errors, "warnings": warnings, "checked": checked}

    modules = sorted([d for d in modules_root.iterdir() if d.is_dir() and not d.name.startswith(".")], key=lambda x: x.name)

    module_log_files: list[Path] = []
    for module_dir in modules:
        checked["modules"] += 1
        module_log_files.extend(_validate_module(repo_root, module_dir, errors, warnings, checked))

    orchestrator_log_files: list[Path] = []
    orchestrator_logs_dir = repo_root / "orchestrator/logs"
    if orchestrator_logs_dir.exists() and orchestrator_logs_dir.is_dir():
        orchestrator_log_files = sorted(orchestrator_logs_dir.glob("*.jsonl"))
        checked["jsonl"] += len(orchestrator_log_files)

    all_log_files = sorted({p for p in module_log_files + orchestrator_log_files}, key=lambda p: str(p))
    known_ids = _collect_known_ids(all_log_files)

    schema_map: dict[Path, list[str]] = {}
    for log_path in all_log_files:
        fields = _validate_jsonl_schema(log_path, errors)
        if fields:
            schema_map[log_path] = fields

    for log_path, fields in schema_map.items():
        _validate_jsonl_records(log_path, fields, known_ids, errors, warnings, checked)

    route_modules = _validate_routes(repo_root, errors, warnings)
    module_names = {d.name for d in modules}
    for m in sorted(route_modules):
        if m not in module_names:
            errors.append(
                _error(
                    "routes.module_not_found",
                    "orchestrator/config/routes.json",
                    f"Route refers to unknown module: {m}",
                )
            )

    _validate_cadence(repo_root, errors, checked)

    return {"ok": len(errors) == 0, "errors": errors, "warnings": warnings, "checked": checked}
