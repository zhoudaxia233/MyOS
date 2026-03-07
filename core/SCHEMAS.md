# Global Schemas and Conventions

## ID Format

Use:

- `<prefix>_<YYYYMMDD>_<3-digit-seq>`

Examples:

- `ct_20260226_001`
- `dc_20260226_001`
- `fx_20260226_001`
- `pf_20260227_001`
- `me_20260227_001`
- `pc_20260227_001`
- `po_20260228_001`
- `cp_20260228_001`
- `run_20260303_001`
- `rq_20260303_001`
- `sr_20260303_001`
- `sv_20260307_001`
- `as_20260307_001`
- `dq_20260307_001`
- `ar_20260307_001`
- `eq_20260307_001`
- `pam_20260307_001`
- `pex_20260307_001`
- `ap_20260307_001`

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
- `object_type` (`memory` / `decision` / `profile` / `cognition` / `principle` / `content` / `system`)
- `approval_ref` (ID, required when an owner approval is required by policy)

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
