from __future__ import annotations

import json
import re
from pathlib import Path

from scheduling import load_cadence

REF_RE = re.compile(r"(?:core|modules|routines|orchestrator)/[A-Za-z0-9_./-]+\.(?:md|yaml|yml|jsonl|json)")


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


def _validate_jsonl_schema(path: Path, errors: list[dict]) -> bool:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        errors.append(_error("jsonl.empty", str(path), "JSONL file is empty; expected schema header on line 1."))
        return False

    first = lines[0].strip()
    if not first:
        errors.append(_error("jsonl.header_blank", str(path), "Line 1 is blank; expected schema header object."))
        return False

    try:
        obj = json.loads(first)
    except json.JSONDecodeError:
        errors.append(_error("jsonl.header_not_json", str(path), "Line 1 is not valid JSON schema header."))
        return False

    if not isinstance(obj, dict) or "_schema" not in obj or not isinstance(obj["_schema"], dict):
        errors.append(_error("jsonl.schema_missing", str(path), "Schema header must contain an object at key '_schema'."))
        return False

    schema = obj["_schema"]
    required = ["name", "version", "fields", "notes"]
    for key in required:
        if key not in schema:
            errors.append(_error("jsonl.schema_field_missing", str(path), f"Schema header missing required field '{key}'."))
            return False
    if not isinstance(schema.get("fields"), list):
        errors.append(_error("jsonl.schema_fields_type", str(path), "Schema 'fields' must be an array."))
        return False
    return True


def _validate_module(repo_root: Path, module_dir: Path, errors: list[dict], warnings: list[dict], checked: dict) -> None:
    module_name = module_dir.name
    module_rel = str(module_dir.relative_to(repo_root))

    required_files = [module_dir / "MODULE.md"]
    required_dirs = [module_dir / "data", module_dir / "logs", module_dir / "skills", module_dir / "outputs"]

    for path in required_files:
        if not path.exists() or not path.is_file():
            errors.append(_error("module.missing_file", str(path), "Required file missing."))
    for path in required_dirs:
        if not path.exists() or not path.is_dir():
            errors.append(_error("module.missing_dir", str(path), "Required directory missing."))

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
                    errors.append(
                        _error("skill.ref_missing", str(skill), f"Referenced file does not exist: {ref}")
                    )
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
    if logs_dir.exists() and logs_dir.is_dir():
        log_files = sorted(logs_dir.glob("*.jsonl"))
        if module_name != "_template" and not log_files:
            warnings.append(_warn("module.no_logs", module_rel, "No JSONL logs found in logs/ directory."))
        for logf in log_files:
            checked["jsonl"] += 1
            _validate_jsonl_schema(logf, errors)


def _validate_routes(repo_root: Path, errors: list[dict], warnings: list[dict]) -> set[str]:
    path = repo_root / "orchestrator/config/routes.json"
    if not path.exists():
        errors.append(_error("routes.missing", str(path), "Route config file is missing."))
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
        errors.append(_error("routes.default_missing", str(path), "Missing required key: default_module."))

    routes = payload.get("routes")
    if not isinstance(routes, list):
        errors.append(_error("routes.list_missing", str(path), "Missing required key: routes (array)."))
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
    checked = {"modules": 0, "skills": 0, "jsonl": 0, "routines": 0}

    modules_root = repo_root / "modules"
    if not modules_root.exists() or not modules_root.is_dir():
        errors.append(_error("modules.missing", str(modules_root), "modules/ directory is missing."))
        return {"ok": False, "errors": errors, "warnings": warnings, "checked": checked}

    modules = sorted([d for d in modules_root.iterdir() if d.is_dir() and not d.name.startswith(".")], key=lambda x: x.name)
    for module_dir in modules:
        checked["modules"] += 1
        _validate_module(repo_root, module_dir, errors, warnings, checked)

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
