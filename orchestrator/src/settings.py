from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULT_SETTINGS = {
    "openai_api_key": "",
    "openai_base_url": "https://api.openai.com/v1",
    "deepseek_api_key": "",
    "deepseek_base_url": "https://api.deepseek.com/v1",
    "default_provider": "handoff",
    "openai_model": "gpt-4.1-mini",
    "deepseek_model": "deepseek-chat",
    "routing_model": "gpt-4.1-nano",
    "decision_provider": "",
    "decision_model": "",
    "content_provider": "",
    "content_model": "",
    "cognition_provider": "",
    "cognition_model": "",
    "ui_language": "zh",
}

VALID_PROVIDERS = {"dry-run", "handoff", "openai", "deepseek"}
VALID_UI_LANGUAGES = {"zh", "en"}
PROFILE_MODULES = ("decision", "content", "cognition")


def settings_path(repo_root: Path) -> Path:
    return repo_root / "orchestrator" / "config" / "settings.json"


def _normalize(raw: dict) -> dict:
    data = DEFAULT_SETTINGS.copy()
    data.update(raw)
    legacy_openai_model = str(raw.get("task_model", "")).strip()
    if legacy_openai_model and not str(raw.get("openai_model", "")).strip():
        data["openai_model"] = legacy_openai_model

    provider = str(data.get("default_provider", DEFAULT_SETTINGS["default_provider"]))
    data["default_provider"] = provider if provider in VALID_PROVIDERS else DEFAULT_SETTINGS["default_provider"]

    data["openai_model"] = (
        str(data.get("openai_model", DEFAULT_SETTINGS["openai_model"])) or DEFAULT_SETTINGS["openai_model"]
    )
    data["deepseek_model"] = (
        str(data.get("deepseek_model", DEFAULT_SETTINGS["deepseek_model"])) or DEFAULT_SETTINGS["deepseek_model"]
    )
    data["routing_model"] = str(data.get("routing_model", DEFAULT_SETTINGS["routing_model"])) or DEFAULT_SETTINGS[
        "routing_model"
    ]
    data["openai_api_key"] = str(data.get("openai_api_key", "")).strip()
    data["deepseek_api_key"] = str(data.get("deepseek_api_key", "")).strip()
    openai_base_url = str(data.get("openai_base_url", DEFAULT_SETTINGS["openai_base_url"])).strip()
    data["openai_base_url"] = (openai_base_url or DEFAULT_SETTINGS["openai_base_url"]).rstrip("/")
    base_url = str(data.get("deepseek_base_url", DEFAULT_SETTINGS["deepseek_base_url"])).strip()
    data["deepseek_base_url"] = (base_url or DEFAULT_SETTINGS["deepseek_base_url"]).rstrip("/")
    for module_name in PROFILE_MODULES:
        provider_key = f"{module_name}_provider"
        model_key = f"{module_name}_model"
        provider_override = str(data.get(provider_key, "")).strip().lower()
        data[provider_key] = provider_override if provider_override in VALID_PROVIDERS else ""
        data[model_key] = str(data.get(model_key, "")).strip()
    data["task_model"] = data["openai_model"]
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
    os.environ["OPENAI_BASE_URL"] = get_openai_base_url(repo_root)


def get_deepseek_api_key(repo_root: Path) -> str:
    settings = load_settings(repo_root)
    key = str(settings.get("deepseek_api_key", "")).strip()
    if key:
        return key
    return os.getenv("DEEPSEEK_API_KEY", "").strip()


def get_openai_base_url(repo_root: Path) -> str:
    settings = load_settings(repo_root)
    base_url = str(settings.get("openai_base_url", DEFAULT_SETTINGS["openai_base_url"])).strip()
    if base_url:
        return base_url.rstrip("/")
    env_base = os.getenv("OPENAI_BASE_URL", "").strip()
    if env_base:
        return env_base.rstrip("/")
    return DEFAULT_SETTINGS["openai_base_url"]


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
        "openai_model": settings.get("openai_model", DEFAULT_SETTINGS["openai_model"]),
        "task_model": settings.get("openai_model", DEFAULT_SETTINGS["openai_model"]),
        "openai_base_url": settings.get("openai_base_url", DEFAULT_SETTINGS["openai_base_url"]),
        "deepseek_model": settings.get("deepseek_model", DEFAULT_SETTINGS["deepseek_model"]),
        "deepseek_base_url": settings.get("deepseek_base_url", DEFAULT_SETTINGS["deepseek_base_url"]),
        "routing_model": settings.get("routing_model", DEFAULT_SETTINGS["routing_model"]),
        "decision_provider": settings.get("decision_provider", ""),
        "decision_model": settings.get("decision_model", ""),
        "content_provider": settings.get("content_provider", ""),
        "content_model": settings.get("content_model", ""),
        "cognition_provider": settings.get("cognition_provider", ""),
        "cognition_model": settings.get("cognition_model", ""),
        "ui_language": settings.get("ui_language", DEFAULT_SETTINGS["ui_language"]),
        "has_openai_api_key": bool(str(settings.get("openai_api_key", "")).strip()),
        "has_deepseek_api_key": bool(str(settings.get("deepseek_api_key", "")).strip()),
    }
    return redacted
