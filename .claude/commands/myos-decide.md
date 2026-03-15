Record a decision in MyOS with full guardrail evaluation and decision gate checks.

Decision to log: $ARGUMENTS

Steps:

1. **Read the decision skill** — Read `modules/decision/skills/log_decision.md` for the full protocol.

2. **Identify domain** — Determine the decision domain from the task description: `invest`, `project`, or `content`. For invest or project domains, read `modules/decision/data/domain_guardrails.yaml`.

3. **Run guardrail check** — Use `myos_guardrail_check` MCP tool (or `python3 orchestrator/src/main.py guardrail-check`) to evaluate the decision against domain guardrail policy. Note the check ID.

4. **Log the decision** — Use the CLI command to log the decision through the entry gate:
   ```
   python3 orchestrator/src/main.py log-decision \
     --domain <domain> \
     --decision "<decision text>" \
     --option "<option A>" \
     --option "<option B>" \
     --confidence <1-10> \
     --guardrail-check-id <pc_ID> \
     --downside "<downside>" \
     --invalidation-condition "<condition>" \
     --max-loss "<loss>" \
     --disconfirming-signal "<signal>"
   ```

5. **Report result** — Show the decision ID, gate status, guardrail status, and principle context status.

If the gate is blocked, explain the violations and what is required to proceed.
If override is needed, ask the owner for confirmation before proceeding.
