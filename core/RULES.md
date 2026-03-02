# Global Rules

These rules apply across all modules and tasks.

## Behavior and Quality

- No fabrication. If unsure, explicitly mark assumptions and request data.
- When relevant, separate `Facts I Read` from `Inferences` in outputs.
- Prefer concise, structured outputs over long prose.
- Respect module boundaries and progressive disclosure.
- Use the module's canonical data files as SSOT; do not duplicate canonical content into skills or logs.

## Logging and Data Integrity

- Any change to logs must be append-only and preserve history.
- Never overwrite JSONL files; only append new lines.
- Do not delete historical records.
- To remove something from active use, set `"status": "archived"` instead of deleting it.
- Preserve the `_schema` header line at the top of every JSONL file.

## Module-Specific Compliance

- When generating content, obey the voice and anti-pattern rules from `modules/content/data/`.
- When logging decisions or reviews, use the schemas and fields defined by the decision module and `core/SCHEMAS.md`.
- For high-risk decisions, run decision precommit guardrails before commitment when the decision module provides that workflow.
- For personal alignment-sensitive tasks, consult profile SSOT before final output.
- Keep psych profiling non-clinical and operational; do not present medical diagnosis claims.
- If a required file is missing, stop and state the missing dependency instead of inventing it.
