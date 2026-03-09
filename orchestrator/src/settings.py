from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULT_SETTINGS = {
    "openai_api_key": "",
    "deepseek_api_key": "",
    "deepseek_base_url": "https://api.deepseek.com/v1",
    "default_provider": "handoff",
    "task_model": "gpt-4.1-mini",
    "deepseek_model": "deepseek-chat",
    "routing_model": "gpt-4.1-nano",
    "ui_language": "zh",
}

VALID_PROVIDERS = {"dry-run", "handoff", "openai", "deepseek"}
VALID_UI_LANGUAGES = {"zh", "en"}


def settings_path(repo_root: Path) -> Path:
    return repo_root / "orchestrator" / "config" / "settings.json"


def _normalize(raw: dict) -> dict:
    data = DEFAULT_SETTINGS.copy()
    data.update(raw)

    provider = str(data.get("default_provider", DEFAULT_SETTINGS["default_provider"]))
    data["default_provider"] = provider if provider in VALID_PROVIDERS else DEFAULT_SETTINGS["default_provider"]

    data["task_model"] = str(data.get("task_model", DEFAULT_SETTINGS["task_model"])) or DEFAULT_SETTINGS["task_model"]
    data["deepseek_model"] = (
        str(data.get("deepseek_model", DEFAULT_SETTINGS["deepseek_model"])) or DEFAULT_SETTINGS["deepseek_model"]
    )
    data["routing_model"] = str(data.get("routing_model", DEFAULT_SETTINGS["routing_model"])) or DEFAULT_SETTINGS[
        "routing_model"
    ]
    data["openai_api_key"] = str(data.get("openai_api_key", "")).strip()
    data["deepseek_api_key"] = str(data.get("deepseek_api_key", "")).strip()
    base_url = str(data.get("deepseek_base_url", DEFAULT_SETTINGS["deepseek_base_url"])).strip()
    data["deepseek_base_url"] = (base_url or DEFAULT_SETTINGS["deepseek_base_url"]).rstrip("/")
    lang = str(data.get("ui_language", DEFAULT_SETTINGS["ui_language"])).strip().lower()
    data["ui_language"] = lang if lang in VALID_UI_LANGUAGES else DEFAULT_SETTINGS["ui_language"]
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
    try:
        os.chmod(path, 0o600)
    except OSError:
        # Best-effort permission hardening; ignore on unsupported platforms.
        pass
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


def get_deepseek_api_key(repo_root: Path) -> str:
    settings = load_settings(repo_root)
    key = str(settings.get("deepseek_api_key", "")).strip()
    if key:
        return key
    return os.getenv("DEEPSEEK_API_KEY", "").strip()


def get_deepseek_base_url(repo_root: Path) -> str:
    settings = load_settings(repo_root)
    base_url = str(settings.get("deepseek_base_url", DEFAULT_SETTINGS["deepseek_base_url"])).strip()
    if base_url:
        return base_url.rstrip("/")
    env_base = os.getenv("DEEPSEEK_BASE_URL", "").strip()
    if env_base:
        return env_base.rstrip("/")
    return DEFAULT_SETTINGS["deepseek_base_url"]


def apply_deepseek_api_key_env(repo_root: Path) -> None:
    key = get_deepseek_api_key(repo_root)
    if key:
        os.environ["DEEPSEEK_API_KEY"] = key
    os.environ["DEEPSEEK_BASE_URL"] = get_deepseek_base_url(repo_root)


def apply_provider_api_key_env(repo_root: Path, provider: str) -> None:
    normalized = str(provider or "").strip().lower()
    if normalized == "openai":
        apply_openai_api_key_env(repo_root)
        return
    if normalized == "deepseek":
        apply_deepseek_api_key_env(repo_root)
        return


def redact_settings(settings: dict) -> dict:
    redacted = {
        "default_provider": settings.get("default_provider", DEFAULT_SETTINGS["default_provider"]),
        "task_model": settings.get("task_model", DEFAULT_SETTINGS["task_model"]),
        "deepseek_model": settings.get("deepseek_model", DEFAULT_SETTINGS["deepseek_model"]),
        "deepseek_base_url": settings.get("deepseek_base_url", DEFAULT_SETTINGS["deepseek_base_url"]),
        "routing_model": settings.get("routing_model", DEFAULT_SETTINGS["routing_model"]),
        "ui_language": settings.get("ui_language", DEFAULT_SETTINGS["ui_language"]),
        "has_openai_api_key": bool(str(settings.get("openai_api_key", "")).strip()),
        "has_deepseek_api_key": bool(str(settings.get("deepseek_api_key", "")).strip()),
    }
    return redacted
