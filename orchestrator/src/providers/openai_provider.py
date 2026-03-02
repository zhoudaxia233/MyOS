from __future__ import annotations

import json
import os
from urllib import request


def run_openai(task: str, module: str, plan: dict, bundle: dict, model: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    context_lines = []
    for item in bundle.get("files", []):
        context_lines.append(f"FILE: {item['path']}\n{item['content']}\n")

    prompt = (
        f"Task: {task}\n"
        f"Module: {module}\n"
        f"Skill file: {plan['skill']}\n"
        f"Required output path: {plan['output_path']}\n"
        "Follow progressive disclosure and produce final output content only."
        "\n\nContext:\n" + "\n".join(context_lines)
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an execution assistant for Personal Core OS."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }

    req = request.Request(
        "https://api.openai.com/v1/chat/completions",
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
