# Maintenance

[Reference](reference.md) · [Overview](../README.md)

## Tests

```sh
poetry install --with dev
poetry run pytest -q --strict-markers
```

Tests use temporary stores. An autouse fixture clears `MYOS_DATA_DIR` and the
trace settings, so no test reaches a live store; keep it that way. The suite
covers store and revision rules, the MCP stdio contract, the MyOS block and host
sync, traces, migration and documentation links. It checks mechanics, not
whether answers got better; that needs real answers and the
[offline answer review](answer-review.md).

## Existing stores and migration

A live data directory is never rebuilt because the code changed. To import
legacy material, run `myos migrate --source ROOT` into a new, empty directory;
repeating it on an unchanged destination returns `unchanged`. Compare the result
with the live store before any separately authorized switch, and never delete a
destination to make a migration run again. Legacy source material must be
provided from a separately preserved private location; it is not distributed
with this repository. The [exploration map](exploration-map.md) records the
relevant migration lessons without exposing those sources.

After pointing a host at another data directory, update its executable and
`MYOS_DATA_DIR`, then restart its tool connection. Reading a known asset is a
good smoke test; never write a fake entry into a live store to test a
connection.

## Adding functionality

Use the model's reasoning and the host's own features first. Add code only for
a mechanical or access-control need that the host cannot meet. Do not rebuild
routing, receipts, pipelines or a governance UI. Keep the Skill, the docs and
the actual tool surface consistent.

## Traces

[Local execution traces](tracing.md) are captured at the CLI and FastMCP
boundaries in `personal/tracing.py`; `Store` and tool schemas do not depend on
them. The viewer only reads saved logs. Pending files stay visibly incomplete:
keep the `.pending.jsonl` suffix until capture is complete, and never infer
Skill use from missing calls.
