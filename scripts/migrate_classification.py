#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

ID_RE = re.compile(r"^[a-z][a-z0-9]*_[0-9]{8}_[0-9]{3}$")

OBJECT_TYPE_BY_PREFIX = {
    "modules/memory/logs/": "memory",
    "modules/decision/logs/": "decision",
    "modules/profile/logs/": "profile",
    "modules/cognition/logs/": "cognition",
    "modules/principles/logs/": "principle",
    "modules/content/logs/": "content",
    "orchestrator/logs/": "system",
}

MEMORY_TO_DECISION = {
    "decision",
    "risk",
    "tradeoff",
    "guardrail",
    "invalidation",
    "downside",
    "precommit",
}
MEMORY_TO_PROFILE = {
    "profile",
    "identity",
    "value",
    "values",
    "trigger",
    "psych",
    "alignment",
    "preference",
}
MEMORY_TO_COGNITION = {
    "schema",
    "mental model",
    "cognition",
    "disequilibrium",
    "assimilation",
    "accommodation",
    "equilibration",
    "contradiction",
    "mismatch",
}
MEMORY_TO_PRINCIPLE = {
    "principle",
    "constitution",
    "constitutional",
    "non-negotiable",
    "enduring",
    "north star",
    "governing",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def norm_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return " ".join(norm_text(item) for item in value)
    if isinstance(value, dict):
        return " ".join(norm_text(v) for v in value.values())
    return str(value)


def detect_object_type(rel_path: str) -> str | None:
    for prefix, object_type in OBJECT_TYPE_BY_PREFIX.items():
        if rel_path.startswith(prefix):
            return object_type
    return None


def infer_proposal_target(object_type: str, rel_path: str, record: dict[str, Any]) -> str | None:
    text = " ".join(
        [
            norm_text(record.get("tags")),
            norm_text(record.get("event")),
            norm_text(record.get("why_it_matters")),
            norm_text(record.get("insight")),
            norm_text(record.get("pattern_statement")),
            norm_text(record.get("actionable_rule")),
            norm_text(record.get("decision")),
            norm_text(record.get("reasoning")),
            norm_text(record.get("observation")),
            norm_text(record.get("suggested_stabilizer")),
            norm_text(record.get("signal_types")),
            norm_text(record.get("conflict_summary")),
            norm_text(record.get("revision_summary")),
            norm_text(record.get("unresolved_questions")),
            norm_text(record.get("change_summary")),
            norm_text(record.get("metric")),
            norm_text(record.get("action")),
        ]
    ).lower()

    if object_type == "memory":
        if any(k in text for k in MEMORY_TO_PRINCIPLE):
            return "principle"
        if any(k in text for k in MEMORY_TO_COGNITION):
            return "cognition"
        if any(k in text for k in MEMORY_TO_PROFILE):
            return "profile"
        if any(k in text for k in MEMORY_TO_DECISION):
            return "decision"
        return None

    if object_type == "decision":
        if rel_path.endswith("owner_todos.jsonl"):
            return "principle"
        if "schema" in text or "mismatch" in text or "disequilibrium" in text:
            return "cognition"
        return None

    if object_type == "profile":
        if "principle" in text or "constitution" in text:
            return "principle"
        if "precommit" in text or "guardrail" in text or "invalidation" in text:
            return "decision"
        return None

    if object_type == "cognition":
        if "guardrail_block" in text or "prediction_failure" in text:
            return "decision"
        if "identity" in text or "trigger" in text:
            return "profile"
        return None

    return None


def load_jsonl(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise ValueError(f"Empty JSONL: {path}")

    header = json.loads(lines[0])
    if not isinstance(header, dict) or not isinstance(header.get("_schema"), dict):
        raise ValueError(f"Missing _schema header: {path}")

    records: list[dict[str, Any]] = []
    for i, raw in enumerate(lines[1:], start=2):
        line = raw.strip()
        if not line:
            continue
        obj = json.loads(line)
        if not isinstance(obj, dict):
            raise ValueError(f"Non-object record at {path}:{i}")
        records.append(obj)
    return header, records


def bump_version(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return "1.1"
    parts = text.split(".")
    if len(parts) != 2 or not all(p.isdigit() for p in parts):
        return text
    major, minor = int(parts[0]), int(parts[1])
    return f"{major}.{minor + 1}"


def dump_jsonl(path: Path, header: dict[str, Any], records: list[dict[str, Any]]) -> None:
    out = [json.dumps(header, ensure_ascii=True)]
    out.extend(json.dumps(row, ensure_ascii=True) for row in records)
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def iter_log_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for pattern in ("modules/*/logs/*.jsonl", "orchestrator/logs/*.jsonl"):
        files.extend(sorted(root.glob(pattern)))
    return sorted({f.resolve() for f in files})


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Backfill object_type/proposal_target into historical JSONL logs.")
    p.add_argument("--apply", action="store_true", help="Write changes to files (default is dry-run).")
    p.add_argument("--overwrite-existing", action="store_true", help="Override existing object_type/proposal_target values.")
    p.add_argument("--root", default=str(ROOT), help="Repository root path.")
    p.add_argument("--report", default=None, help="Custom markdown report output path.")
    p.add_argument("--mapping", default=None, help="Custom mapping JSONL output path.")
    return p


def main() -> int:
    args = build_parser().parse_args()
    root = Path(args.root).expanduser().resolve()

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_path = Path(args.report) if args.report else root / f"modules/decision/outputs/classification_backfill_{ts}.md"
    mapping_path = Path(args.mapping) if args.mapping else root / f"modules/decision/outputs/classification_backfill_map_{ts}.jsonl"
    backup_root = root / f"modules/decision/outputs/migration_backups/{ts}"

    files = iter_log_files(root)
    totals = Counter()
    object_counts = Counter()
    target_counts = Counter()
    file_changes: list[tuple[str, int, int]] = []
    mapping_rows: list[dict[str, Any]] = []

    for path in files:
        rel = str(path.relative_to(root)).replace("\\", "/")
        object_type = detect_object_type(rel)
        if not object_type:
            continue

        header, records = load_jsonl(path)
        schema = header.get("_schema", {})
        fields = list(schema.get("fields") or [])
        header_changed = False
        if "object_type" not in fields:
            fields.append("object_type")
            header_changed = True
        if "proposal_target" not in fields:
            fields.append("proposal_target")
            header_changed = True

        record_changes = 0
        for idx, record in enumerate(records, start=2):
            totals["records_scanned"] += 1
            changed_fields: list[str] = []

            if args.overwrite_existing or "object_type" not in record or record.get("object_type") in (None, ""):
                if record.get("object_type") != object_type:
                    record["object_type"] = object_type
                    changed_fields.append("object_type")

            inferred_target = infer_proposal_target(object_type, rel, record)
            if args.overwrite_existing or "proposal_target" not in record:
                if "proposal_target" not in record or record.get("proposal_target") != inferred_target:
                    record["proposal_target"] = inferred_target
                    changed_fields.append("proposal_target")
            elif record.get("proposal_target") == "" and inferred_target is not None:
                record["proposal_target"] = inferred_target
                changed_fields.append("proposal_target")

            object_counts[str(record.get("object_type") or "<missing>")] += 1
            target_value = record.get("proposal_target")
            if target_value:
                target_counts[str(target_value)] += 1

            if changed_fields:
                record_changes += 1
                rid = str(record.get("id") or f"line_{idx}")
                mapping_rows.append(
                    {
                        "id": rid,
                        "log_path": rel,
                        "object_type": record.get("object_type"),
                        "proposal_target": record.get("proposal_target"),
                        "changed_fields": changed_fields,
                    }
                )

        if header_changed:
            schema["fields"] = fields
            schema["version"] = bump_version(str(schema.get("version", "1.0")))
            header["_schema"] = schema

        if header_changed or record_changes > 0:
            totals["files_changed"] += 1
            file_changes.append((rel, record_changes, 1 if header_changed else 0))
            if args.apply:
                backup_path = backup_root / rel
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                backup_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
                dump_jsonl(path, header, records)
        totals["files_scanned"] += 1

    totals["records_changed"] = len(mapping_rows)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Classification Backfill Report",
        "",
        f"- Generated at (UTC): {utc_now()}",
        f"- Mode: {'apply' if args.apply else 'dry-run'}",
        f"- Files scanned: {totals['files_scanned']}",
        f"- Files changed: {totals['files_changed']}",
        f"- Records scanned: {totals['records_scanned']}",
        f"- Records changed: {totals['records_changed']}",
        "",
        "## Object Type Distribution",
    ]
    for key, value in sorted(object_counts.items(), key=lambda kv: kv[0]):
        lines.append(f"- {key}: {value}")

    lines.append("")
    lines.append("## Proposal Target Distribution (non-null)")
    if target_counts:
        for key, value in sorted(target_counts.items(), key=lambda kv: kv[0]):
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("## File Changes")
    if file_changes:
        for rel, record_changes, header_changes in sorted(file_changes):
            lines.append(f"- {rel}: records_changed={record_changes}, schema_header_changed={header_changes}")
    else:
        lines.append("- no changes")

    if args.apply:
        lines.append("")
        lines.append(f"- Backup root: `{backup_root}`")

    lines.append("")
    lines.append(f"- Mapping file: `{mapping_path}`")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    mapping_path.parent.mkdir(parents=True, exist_ok=True)
    mapping_header = {
        "_schema": {
            "name": "classification_backfill",
            "version": "1.0",
            "fields": ["id", "log_path", "object_type", "proposal_target", "changed_fields"],
            "notes": "generated migration map",
        }
    }
    mapping_lines = [json.dumps(mapping_header, ensure_ascii=True)]
    mapping_lines.extend(json.dumps(row, ensure_ascii=True) for row in mapping_rows)
    mapping_path.write_text("\n".join(mapping_lines) + "\n", encoding="utf-8")

    print(f"Mode: {'apply' if args.apply else 'dry-run'}")
    print(f"Files scanned: {totals['files_scanned']}")
    print(f"Files changed: {totals['files_changed']}")
    print(f"Records scanned: {totals['records_scanned']}")
    print(f"Records changed: {totals['records_changed']}")
    print(f"Report: {report_path}")
    print(f"Mapping: {mapping_path}")
    if args.apply:
        print(f"Backup: {backup_root}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
