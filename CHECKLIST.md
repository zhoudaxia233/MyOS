# Personal Core OS Acceptance Checklist

Use this checklist before merging changes.

## Kernel and Routing

- [ ] `core/ROUTER.md` exists and defines two-hop loading: `ROUTER -> MODULE -> DATA`
- [ ] `core/ROUTER.md` includes explicit routing table for `content` and `decision`
- [ ] `core/RULES.md` includes no-fabrication and append-only integrity rules
- [ ] `core/SCHEMAS.md` defines ID format, timestamp format, and JSONL schema header rule

## Progressive Disclosure

- [ ] Agent workflow always starts from `core/ROUTER.md`
- [ ] Task loading stays inside one target module unless explicitly requested
- [ ] Only files needed for the active task are loaded
- [ ] Unrelated module files are not preloaded

## SSOT and Coupling

- [ ] Canonical domain knowledge lives in `modules/*/data/`
- [ ] `modules/*/skills/` reference SSOT files instead of duplicating canonical content
- [ ] Cross-module references use IDs only (no copied content)

## Logs and Integrity

- [ ] Every `*.jsonl` file starts with a `_schema` header on line 1
- [ ] Existing JSONL records were not edited or removed
- [ ] New log records were appended as new lines only
- [ ] Deletions are represented as `"status": "archived"`

## Module Quality

- [ ] Each module has `MODULE.md` with purpose, inventory, workflows, and `<instructions>`
- [ ] `modules/content/MODULE.md` includes quality gates and template-based workflow
- [ ] `modules/decision/MODULE.md` includes immediate logging + weekly review workflow
- [ ] `modules/_template/` is usable as a starter for new modules

## Operational Readiness

- [ ] `scripts/append_jsonl.sh` exists and is executable
- [ ] Outputs are written under `modules/*/outputs/`
- [ ] Repository remains human-readable and Git-friendly
