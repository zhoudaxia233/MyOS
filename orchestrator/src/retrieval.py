from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

TOKEN_RE = re.compile(r"[a-z0-9_]{2,}")
STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "are",
    "was",
    "were",
    "into",
    "then",
    "than",
    "have",
    "has",
    "had",
    "you",
    "your",
    "not",
    "but",
    "can",
    "will",
    "just",
    "all",
    "any",
    "one",
    "two",
    "three",
}

DEFAULT_CFG = {
    "source_globs": [
        "modules/decision/logs/*.jsonl",
        "modules/memory/logs/*.jsonl",
        "modules/profile/logs/*.jsonl",
        "modules/content/logs/*.jsonl",
        "modules/cognition/logs/*.jsonl",
    ],
    "index_path": "orchestrator/retrieval/index.json",
    "query_log_path": "orchestrator/logs/retrieval_queries.jsonl",
    "max_text_chars": 600,
}


def load_retrieval_config(repo_root: Path) -> dict:
    path = repo_root / "orchestrator" / "config" / "retrieval.json"
    if not path.exists():
        return DEFAULT_CFG.copy()
    data = json.loads(path.read_text(encoding="utf-8"))
    cfg = DEFAULT_CFG.copy()
    cfg.update(data)
    return cfg


def _tokenize(text: str) -> list[str]:
    tokens = TOKEN_RE.findall(text.lower())
    return [t for t in tokens if t not in STOPWORDS]


def _flatten(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return " ".join(_flatten(v) for v in value)
    if isinstance(value, dict):
        return " ".join(_flatten(v) for v in value.values())
    return str(value)


def _extract_docs_from_jsonl(repo_root: Path, path: Path, max_text_chars: int) -> list[dict]:
    docs: list[dict] = []
    rel = str(path.relative_to(repo_root))
    for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        if i == 1 and '"_schema"' in line:
            continue

        record_id = None
        text = line
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                record_id = obj.get("id")
            text = _flatten(obj)
        except json.JSONDecodeError:
            pass

        docs.append(
            {
                "path": rel,
                "line": i,
                "record_id": record_id,
                "text": text[:max_text_chars],
            }
        )
    return docs


def _source_files(repo_root: Path, globs: list[str]) -> list[Path]:
    files: list[Path] = []
    seen: set[str] = set()
    for pattern in globs:
        for p in sorted(repo_root.glob(pattern)):
            rel = str(p.relative_to(repo_root))
            if not p.is_file() or rel in seen:
                continue
            seen.add(rel)
            files.append(p)
    return files


def build_index(repo_root: Path, source_globs: list[str] | None = None) -> dict:
    cfg = load_retrieval_config(repo_root)
    globs = source_globs or cfg["source_globs"]
    max_text_chars = int(cfg["max_text_chars"])

    raw_docs: list[dict] = []
    for src in _source_files(repo_root, globs):
        if src.suffix == ".jsonl":
            raw_docs.extend(_extract_docs_from_jsonl(repo_root, src, max_text_chars))

    doc_entries: list[dict] = []
    df: dict[str, int] = defaultdict(int)
    postings: dict[str, list[list[int]]] = defaultdict(list)

    for idx, doc in enumerate(raw_docs):
        tokens = _tokenize(doc["text"])
        if not tokens:
            continue
        counts = Counter(tokens)
        doc_entries.append(
            {
                "doc_id": idx,
                "path": doc["path"],
                "line": doc["line"],
                "record_id": doc["record_id"],
                "text": doc["text"],
            }
        )
        for token in counts:
            df[token] += 1
        for token, tf in counts.items():
            postings[token].append([idx, int(tf)])

    payload = {
        "_schema": {
            "name": "retrieval_index",
            "version": "1.0",
            "fields": [
                "built_at",
                "sources",
                "doc_count",
                "docs",
                "df",
                "postings",
            ],
            "notes": "derived-index",
        },
        "built_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "sources": globs,
        "doc_count": len(doc_entries),
        "docs": doc_entries,
        "df": df,
        "postings": postings,
    }

    index_path = repo_root / cfg["index_path"]
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(payload, ensure_ascii=True), encoding="utf-8")
    return payload


def load_index(repo_root: Path) -> dict:
    cfg = load_retrieval_config(repo_root)
    path = repo_root / cfg["index_path"]
    if not path.exists():
        raise FileNotFoundError(f"Retrieval index not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def search_index(repo_root: Path, query: str, top_k: int = 8, module: str | None = None) -> list[dict]:
    idx = load_index(repo_root)
    tokens = _tokenize(query)
    if not tokens:
        return []

    docs = {int(d["doc_id"]): d for d in idx.get("docs", [])}
    n = max(int(idx.get("doc_count", 0)), 1)
    df = idx.get("df", {})
    postings = idx.get("postings", {})

    scores: dict[int, float] = defaultdict(float)
    matched_tokens: dict[int, set[str]] = defaultdict(set)

    for token in tokens:
        plist = postings.get(token, [])
        token_df = int(df.get(token, 0))
        idf = math.log((n + 1) / (token_df + 1)) + 1.0
        for doc_id, tf in plist:
            if module:
                path = docs.get(int(doc_id), {}).get("path", "")
                if not path.startswith(f"modules/{module}/"):
                    continue
            scores[int(doc_id)] += float(tf) * idf
            matched_tokens[int(doc_id)].add(token)

    ranked = sorted(
        scores.items(),
        key=lambda item: (item[1], len(matched_tokens[item[0]])),
        reverse=True,
    )

    results: list[dict] = []
    for doc_id, score in ranked[:top_k]:
        d = docs.get(doc_id)
        if not d:
            continue
        results.append(
            {
                "doc_id": doc_id,
                "score": round(score, 4),
                "matched_tokens": sorted(matched_tokens[doc_id]),
                "path": d.get("path"),
                "line": d.get("line"),
                "record_id": d.get("record_id"),
                "text": d.get("text"),
            }
        )
    return results


def format_hits(hits: list[dict]) -> str:
    out: list[str] = []
    for h in hits:
        head = f"- {h['path']}:{h['line']} score={h['score']}"
        if h.get("record_id"):
            head += f" id={h['record_id']}"
        out.append(head)
        out.append(f"  tokens={','.join(h['matched_tokens'])}")
        out.append(f"  text={h['text']}")
    return "\n".join(out)
