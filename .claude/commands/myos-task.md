Execute a MyOS task through the full governance loop.

Task: $ARGUMENTS

Follow this exact interaction loop:

1. **Route** — Read `core/ROUTER.md`. Match the task description to the appropriate module using the routing keyword table.

2. **Load module** — Read `modules/{matched_module}/MODULE.md`. Understand the module's purpose, workflows, and file inventory.

3. **Select skill** — From the skill directory in CLAUDE.md or from MODULE.md, identify the skill that best matches the task. Read `modules/{module}/skills/{skill}.md`.

4. **Load declared files** — The skill file will list which data files to load. Load only those files (progressive disclosure — do not preload the entire module).

5. **Execute** — Follow the skill instructions against the loaded context. Produce the output the skill specifies.

6. **Write back** — Append results to the appropriate JSONL log:
   - If `myos` MCP server is available: use `myos_append_log` tool with the correct log path and id_prefix
   - If MCP is unavailable: use the appropriate CLI command (see CLAUDE.md CLI Fallback Protocol)

Governance rules that must hold throughout:
- Governance hierarchy: Principles > Decisions > Cognition > Profile > Memory
- Append-only: never overwrite JSONL records
- Cross-module: reference by ID only, never copy content
- Two-hop max: ROUTER → MODULE → DATA, no further chaining
