# Global Schemas and Conventions

## ID Format

Use:

- `<prefix>_<YYYYMMDD>_<3-digit-seq>`

Examples:

- `ct_20260226_001`
- `dc_20260226_001`
- `fx_20260226_001`

## Timestamp Format

- ISO 8601 in UTC with `Z` suffix
- Example: `2026-02-26T10:30:00Z`

## Common Fields (Shared Conventions)

Use these when applicable:

- `id` (string)
- `created_at` (ISO 8601 string)
- `updated_at` (ISO 8601 string, optional)
- `status` (`active` or `archived`)
- `tags` (array of strings)
- `source_refs` (array of IDs)

## Cross-Module References (SSOT)

- Cross-module references must use IDs only.
- Never copy canonical content across modules.
- If content from another module is needed, reference its ID and load the source file only when required.

## JSONL Schema Header Rule (Required)

- The first line of every JSONL file MUST be a schema header object.
- Required schema header format:
  - `{"_schema":{"name":"<file_stem>","version":"1.0","fields":[...],"notes":"append-only"}}`
- The schema header line must never be deleted.
- Data records begin on line 2.
