from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULT_SETTINGS = {
    "openai_api_key": "",
    "default_provider": "handoff",
    "task_model": "gpt-4.1-mini",
    "routing_model": "gpt-4.1-nano",
}

VALID_PROVIDERS = {"dry-run", "handoff", "openai"}


def settings_path(repo_root: Path) -> Path:
    return repo_root / "orchestrator" / "config" / "settings.json"


def _normalize(raw: dict) -> dict:
    data = DEFAULT_SETTINGS.copy()
    data.update(raw)

    provider = str(data.get("default_provider", DEFAULT_SETTINGS["default_provider"]))
    data["default_provider"] = provider if provider in VALID_PROVIDERS else DEFAULT_SETTINGS["default_provider"]

    data["task_model"] = str(data.get("task_model", DEFAULT_SETTINGS["task_model"])) or DEFAULT_SETTINGS["task_model"]
    data["routing_model"] = str(data.get("routing_model", DEFAULT_SETTINGS["routing_model"])) or DEFAULT_SETTINGS[
        "routing_model"
    ]
    data["openai_api_key"] = str(data.get("openai_api_key", "")).strip()
    return data


def load_settings(repo_root: Path) -> dict:
    path = settings_path(repo_root)
    if not path.exists() or not path.is_file():
        return DEFAULT_SETTINGS.copy()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return DEFAULT_SETTINGS.copy()
    if not isinstance(raw, dict):
        return DEFAULT_SETTINGS.copy()
    return _normalize(raw)


def save_settings(repo_root: Path, payload: dict) -> dict:
    current = load_settings(repo_root)
    merged = current.copy()
    merged.update(payload)
    normalized = _normalize(merged)

    path = settings_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(normalized, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return normalized


def get_openai_api_key(repo_root: Path) -> str:
    settings = load_settings(repo_root)
    key = str(settings.get("openai_api_key", "")).strip()
    if key:
        return key
    return os.getenv("OPENAI_API_KEY", "").strip()


def apply_openai_api_key_env(repo_root: Path) -> None:
    key = get_openai_api_key(repo_root)
    if key:
        os.environ["OPENAI_API_KEY"] = key
