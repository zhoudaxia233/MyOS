# Module Template

## Purpose

Describe the domain this module owns and the outcomes it supports.

## Scope

- Define what this module is responsible for
- Define what this module explicitly does not own
- List the primary tasks routed here from `core/ROUTER.md`
- Clarify which outputs are generated vs which records are logged

## File Inventory

- `modules/<name>/MODULE.md`: Module instructions, workflows, and rules
- `modules/<name>/data/`: Canonical SSOT data (YAML/MD/JSON as needed)
- `modules/<name>/logs/`: Append-only JSONL logs with schema header line
- `modules/<name>/skills/`: Task instructions that reference SSOT paths
- `modules/<name>/outputs/`: Generated outputs and reports

## Workflow (Example)

1. Route into the module from `core/ROUTER.md`
2. Load this `MODULE.md`
3. Load only required files for the task
4. Produce output or append a log record

## Suggested Checklists

- Quality gate checklist for generated outputs
- Logging checklist for required fields before append
- Validation notes for schema/header preservation
- Common failure modes and how to avoid them

## Progressive Loading Rules

- Keep two-hop loading: `ROUTER -> MODULE -> DATA`
- Do not load unrelated modules
- Load only the files needed for the active task

<instructions>
- Keep canonical content in `data/` (SSOT).
- Keep task procedures in `skills/` and reference SSOT paths instead of duplicating content.
- Use append-only JSONL for logs; preserve `_schema` header lines.
- Archive records by setting `status: archived` instead of deleting them.
</instructions>
