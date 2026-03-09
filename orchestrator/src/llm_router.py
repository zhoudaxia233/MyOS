from __future__ import annotations

import json
import os
import re
from urllib import request

JSON_OBJ_RE = re.compile(r"\{[\s\S]*\}")


def _extract_json_obj(text: str) -> dict:
    text = text.strip()
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    match = JSON_OBJ_RE.search(text)
    if not match:
        raise ValueError("Router model response is not valid JSON")

    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise ValueError("Router model JSON parse failed") from exc

    if not isinstance(data, dict):
        raise ValueError("Router model JSON must be an object")
    return data


def llm_route_trace(task: str, module_names: list[str], model: str, api_key: str) -> dict:
    if not api_key:
        raise ValueError("OPENAI API key is required for LLM routing")
    if not module_names:
        raise ValueError("No modules available for routing")

    modules_csv = ", ".join(module_names)
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a strict task router for Personal Core OS. "
                    "Return ONLY a JSON object: {\"module\":\"<one_of_allowed_modules>\",\"reason\":\"<short_reason>\"}."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Allowed modules: {modules_csv}\n"
                    f"Task: {task}\n"
                    "Choose exactly one module from allowed modules."
                ),
            },
        ],
        "temperature": 0.0,
    }

    base_url = str(os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).strip().rstrip("/")
    req = request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    content = data["choices"][0]["message"]["content"]
    obj = _extract_json_obj(content)

    module = str(obj.get("module", "")).strip()
    if module not in module_names:
        raise ValueError(f"Router model returned invalid module: {module}")

    reason = str(obj.get("reason", "llm_route")).strip() or "llm_route"
    return {
        "module": module,
        "reason": f"llm_model_route:{reason}",
        "matched_keywords": [],
    }
