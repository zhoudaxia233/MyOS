Generate MyOS drift metrics and owner report.

Window (days): $ARGUMENTS (default: 7)

Steps:

1. **Determine window** — Parse the argument as an integer (7 or 30). Default to 7 if not specified.

2. **Generate metrics** — Use `myos_metrics` MCP tool with the specified window:
   ```
   myos_metrics(window_days=<window>)
   ```
   Or CLI fallback:
   ```
   python3 orchestrator/src/main.py metrics --window <window>
   ```

3. **Display report** — Show the full metrics report including:
   - Decision drift indicators
   - Memory ingest rate
   - Profile alignment signals
   - Cognitive schema evolution trend

4. **Generate owner report** (optional, ask if not specified) — Run:
   ```
   python3 orchestrator/src/main.py owner-report --window <window>
   ```

5. **Flag concerns** — If any metric shows RED or WARN status, highlight it and suggest next actions based on the governance hierarchy.
