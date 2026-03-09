from __future__ import annotations

import json
import os
from urllib import request

from prompting import execution_instruction


def _build_prompt(task: str, module: str, plan: dict, bundle: dict) -> str:
    context_lines = []
    for item in bundle.get("files", []):
        context_lines.append(f"FILE: {item['path']}\n{item['content']}\n")

    return (
        f"Task: {task}\n"
        f"Module: {module}\n"
        f"Skill file: {plan['skill']}\n"
        f"Required output path: {plan['output_path']}\n"
        "Execution instruction:\n"
        f"{execution_instruction(task, module)}\n"
        "Return only final output content for the required output path."
        "\n\nContext:\n" + "\n".join(context_lines)
    )


def _run_chat_completion(*, endpoint: str, api_key: str, system_prompt: str, model: str, user_prompt: str) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
    }

    req = request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    return data["choices"][0]["message"]["content"]


def run_openai(task: str, module: str, plan: dict, bundle: dict, model: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    base_url = str(os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).strip().rstrip("/")
    endpoint = f"{base_url}/chat/completions"

    return _run_chat_completion(
        endpoint=endpoint,
        api_key=api_key,
        system_prompt="You are an execution assistant for Personal Core OS.",
        model=model,
        user_prompt=_build_prompt(task, module, plan, bundle),
    )


def run_deepseek(task: str, module: str, plan: dict, bundle: dict, model: str) -> str:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is not set")

    base_url = str(os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")).strip().rstrip("/")
    endpoint = f"{base_url}/chat/completions"

    return _run_chat_completion(
        endpoint=endpoint,
        api_key=api_key,
        system_prompt="You are an execution assistant for Personal Core OS.",
        model=model,
        user_prompt=_build_prompt(task, module, plan, bundle),
    )
