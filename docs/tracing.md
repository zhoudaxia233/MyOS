# Local execution traces

Tracing is **off by default**. It saves full private arguments, payload text,
record/revision bodies, authorization notes, source text and returned results.
It does not ask a model to explain itself and makes no model calls.

## Enable and inspect

CLI global options precede the command. Omit `--verbose` to disable tracing:

```sh
poetry run myos --verbose catalog --purpose "Reply to the landlord's email"
poetry run myos --verbose read RECORD_ID --history
poetry run myos catalog
poetry run myos trace show
poetry run myos trace show --run RUN_ID
poetry run myos trace show --group REPLAY_CASE
poetry run myos trace show --call CALL_ID
poetry run myos trace show --file /absolute/path/to/call.jsonl --call CALL_ID
poetry run myos trace show --group REPLAY_CASE --html --out /private/path/pipeline.html
```

Replace uppercase IDs with actual IDs from the catalog or trace timeline.
`trace show` emits a deterministic, indented JSON timeline with categories,
errors, elapsed milliseconds, selected store root, handler outcomes and completion
status. Elapsed time ends at the last saved event, not host or transport delivery.
`--call` includes **all saved input/output events**, with no truncation.
`--file` restricts reading to one
file; `--dir PATH` selects another log directory. `--group` filters the external
group label. Viewing never opens the cognition database or source files,
sends data to a model, or saves cognition.
JSON escapes newlines reversibly; Chinese text remains readable and list order
is preserved. A catalog result lists the core and an index; neither a catalog
entry nor a full read proves that an asset was applied.

`--purpose` on `catalog` (`purpose` on `myos_catalog`) is a one-line summary of
the request. It changes nothing in the result and is recorded so a timeline
shows what the lookup was for.

`--html` writes the selected calls as a read-only page instead of printing JSON.
Calls are separated by `MYOS_TRACE_GROUP`, else by MCP server process (one host
session), and ungrouped CLI calls form one stream. Within a stream, calls are in
time order and every catalog call starts a new request, headed by its purpose.
Each step summarizes what was loaded, read or written, with all saved events
collapsed underneath. The page has no scripts or external resources and shows
tool calls only: the host's reasoning and final answer are not captured.

The page goes to `--out`, or to `pipeline.html` in the trace directory. The parent
directory must already exist, a different name inside the trace directory is
refused, and an existing file is replaced only if it is an earlier MyOS pipeline
page. The file is written with mode 0600 and renamed into place.

For a host-launched MCP process, explicitly configure:

```sh
MYOS_TRACE=1 \
MYOS_TRACE_DIR="$HOME/.local/state/myos/traces" \
MYOS_TRACE_GROUP=optional-replay-case \
MYOS_DATA_DIR=/absolute/private/myos-data \
poetry run myos-mcp
```

Unset `MYOS_TRACE`, or set it to `0`, and restart the MCP connection to disable.
CLI enabling is **only** `--verbose`; it ignores `MYOS_TRACE`.
`MYOS_TRACE_DIR` and optional `MYOS_TRACE_GROUP` apply to both entry points.
These are process settings, not chat instructions. A desktop host must pass them
to its tool process; terminal exports do not reconfigure an existing desktop host.

Each call has a generated UUID and its own JSONL file. `run_id` identifies a
process (PID plus generated nonce), not a conversation. The optional group is
an external label for correlating CLI processes or replay cases; it is not an
authenticated conversation ID. No model-supplied run ID is required.

## Isolated executable example

This example reads an empty temporary store and a synthetic source, without
creating `cognition.sqlite3` or touching an owner's store:

```sh
TRACE_DEMO="$(mktemp -d)"
mkdir -p "$TRACE_DEMO/store/originals"
printf '第一行\n第二行\n' > "$TRACE_DEMO/store/originals/example.txt"
MYOS_TRACE_DIR="$TRACE_DEMO/traces" MYOS_TRACE_GROUP=example \
  poetry run myos --data "$TRACE_DEMO/store" --verbose catalog
MYOS_TRACE_DIR="$TRACE_DEMO/traces" MYOS_TRACE_GROUP=example \
  poetry run myos --data "$TRACE_DEMO/store" --verbose references 'originals/example.txt#L2'
poetry run myos trace show --dir "$TRACE_DEMO/traces"
```

Copy a `call_id` from that timeline:

```sh
poetry run myos trace show --dir "$TRACE_DEMO/traces" --call CALL_ID
```

For an isolated `put`, point `--data` and `MYOS_TRACE_DIR` at a temporary
directory and add `--verbose` before `put`. The log includes the decoded payload text, parsed request, expected revision,
and actual returned revision or conflict. It does not fabricate a before/after
diff or independently verify the authorization note.

## Capture boundaries and coverage

| Layer | Captured evidence |
| --- | --- |
| CLI input | Parsed invocation options, handler parameters including defaults; payload text from the actual file read before JSON parsing (Python text decoding/newline normalization). Not raw file or shell bytes. |
| MCP input | Name and arguments reaching the public `FastMCP.call_tool` method, then validated/coerced handler parameters. |
| Handler result | Full Python result snapshot, including IDs, revisions and sources actually returned. Catalog returns no `sources` lists (core examples carry their own `source` label); none are invented or fetched for tracing. |
| CLI output | Exact JSON text plus newline after Python stdout write returns. Downstream delivery/flush is not verified. |
| MCP conversion | FastMCP converted result, serialized into the trace using Pydantic JSON representations. This is **not** the final `CallToolResult`, protocol envelope or raw network response. |
| Host request | **Not collected**: native Skill reads, pre-existing context, compaction, final model request. |

Covered operations: `catalog` core and index; `read` full current record and `--history`
revision list; `references` list, full source text and `#Ln` line; `put` attempts,
returned committed revisions and exceptions. MCP unknown tool names and input
validation errors reaching `FastMCP.call_tool` are captured even when the
business handler does not run. No SDK fork, monkeypatch or upgrade is used.

Not covered: CLI argument-parser rejection and failures before trace creation;
MCP transport parsing, initialization/listing/cancellation protocol messages,
low-level SDK output validation and final protocol serialization/sending;
direct Python `Store` calls; `migrate` and `check`. A process exit may interrupt
any capture. No MyOS calls does **not** prove the Skill was absent or that MyOS
had no influence. A tool trace is not a complete prompt replay or evidence of
improved answers.

## Format, failure and privacy

Format version 1 uses `started`, `store_selected`, `handler_input`, `handler_result` or
`handler_error`, output-layer events and `completed`. Every event includes
process/call IDs, UTC time, monotonic elapsed milliseconds and entry/operation.
The start records a Git commit/dirty flag where determinable, installed package
versions, source-file SHA-256 values and observation limits. Source hashes
identify files on disk at call start, not loaded bytecode in a long-lived process.
Null metadata means unavailable. `snapshot_utf8_bytes` counts compact
`ensure_ascii=False` JSON UTF-8 bytes of event data, excluding the common envelope
and the size field; it is **not a token count**. Snapshots are never replaced
with hashes, summaries or fresh database/source reads.

The default directory is `~/.local/state/myos/traces`, outside this repository
and independent of `cognition.sqlite3`. Use a dedicated private directory for
`MYOS_TRACE_DIR`, never a checkout or shared folder. On POSIX, the final trace
directory is created with 0700 and files with 0600; an existing final directory
must already be 0700. Ancestor directory modes follow the system's mkdir defaults.
Tracing rejects a symlink as the final directory and does not change permissions
of an existing directory. No environment scan, credentials scan, chat-history
capture or full database export is performed. Only the named trace settings are
read for trace configuration. Trace files are not appended to tool responses.

Each call owns an exclusively created file, so concurrent calls/processes do
not interleave records. Each event is flushed with `fsync`. Active files end in
`.pending.jsonl`; only a flushed completion event and successful close allow
renaming to `.jsonl`. The viewer shows pending files as incomplete/unknown even
if they contain a completion event, and reports the handler outcome separately.
Keep these filenames when copying logs. `capture_status: finalized` means capture
completed at the stated adapter boundary, not that the host received a response.
This is local observability, not a tamper-proof audit system or a guarantee
against filesystem/hardware data loss. Interrupted, empty or malformed files
are reported as incomplete/unknown; no missing completion is invented.
A saved handler success followed by missing completion means the handler
returned, but later capture/output completion is unknown. In particular, a
write may have committed even if its success event could not be saved.

Any trace creation/write/flush/close/finalization failure emits **`MyOS trace INCOMPLETE` to stderr**
with the call ID and reason. The affected logger stops; business execution
continues without retries. A committed `put` result remains successful even if
logging fails. Monitor MCP process stderr in the host; do not infer complete
logging from a successful tool call. If no file could be created, the viewer
cannot reconstruct that call. Check the actual business response and revision
before considering any retry. If the host also closes or breaks stderr, that
diagnostic cannot be delivered; logging still must not change a committed write
into a business failure. Keep stderr available when tracing.

There is no automatic retention, upload or cleanup. Stop tracing before cleanup.
Use `trace show --file ...` to inspect a selected log and then delete that exact
JSONL file with your file manager or `rm /absolute/path/to/call.jsonl`. Removing
logs does not remove cognition. The temporary example can be removed by deleting
its `$TRACE_DEMO` directory after inspection. Normal filesystem deletion is not
a guarantee of secure erasure from backups or storage media.
