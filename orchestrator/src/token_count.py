from __future__ import annotations

import math


def count_text_tokens(text: str, model: str | None = None) -> dict:
    model_name = (model or "").strip()

    try:
        import tiktoken  # type: ignore
    except ImportError:
        tiktoken = None

    if tiktoken is not None:
        enc = None
        if model_name:
            try:
                enc = tiktoken.encoding_for_model(model_name)
            except KeyError:
                enc = None
        if enc is None:
            for name in ("o200k_base", "cl100k_base"):
                try:
                    enc = tiktoken.get_encoding(name)
                    break
                except Exception:  # noqa: BLE001
                    continue
        if enc is not None:
            return {
                "prompt_tokens": len(enc.encode(text)),
                "count_method": "tiktoken",
                "model": model_name,
            }

    est = max(1, math.ceil(len(text.encode("utf-8")) / 3.2))
    return {
        "prompt_tokens": est,
        "count_method": "estimate_utf8",
        "model": model_name,
    }
