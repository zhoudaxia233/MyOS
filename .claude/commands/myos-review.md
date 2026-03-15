Review pending proposals, owner todos, and candidates in MyOS.

Scope (optional): $ARGUMENTS

Steps:

1. **Load review skill** — Read `modules/decision/skills/weekly_review.md` for the review protocol and proposal emission rules.

2. **Gather pending items** — Check these sources for items awaiting owner review:
   - `modules/decision/logs/owner_todos.jsonl` — items with `status: active`
   - Any module suggestion/candidate logs with `status: candidate`:
     - `modules/memory/logs/memory_insights.jsonl`
     - `modules/cognition/logs/accommodation_revisions.jsonl`
     - `modules/principles/logs/principle_amendments.jsonl`
   - Use `myos_search` MCP tool with query "status:candidate" for broader discovery.

3. **Present items** — For each pending item, show:
   - Item ID, type, and summary
   - Created date and source module
   - What action is being proposed

4. **Collect owner verdicts** — For each item, ask the owner: accept / reject / defer.

5. **Record verdicts** — Use `myos_append_log` MCP tool to append verdict records to the appropriate log, or use `python3 orchestrator/src/main.py` commands for owner verdicts.

Governance rules:
- Never auto-promote candidates without explicit owner confirmation
- Accepted items get `status: promoted`; rejected items get `status: rejected`
- Deferred items keep `status: candidate` with an updated note
