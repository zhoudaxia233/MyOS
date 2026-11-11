# MyOS reference

[User guide](getting-started.md) · [Overview](../README.md)

Commands, tools and configuration, for developers and for setting MyOS up by
hand. Everyday use is in the [user guide](getting-started.md).

## Install

`uv tool install git+https://github.com/zhoudaxia233/MyOS` installs the `myos`
and `myos-mcp` commands with the Skill inside the package; uv fetches the
Python 3.13 they need. To work on MyOS, clone it and run `poetry install
--with dev` with [Poetry](https://python-poetry.org/docs/#installation);
`python -m myos` and `python -m myos.personal.mcp` work in that environment.

The store is one private data directory: the CLI's `--data` option, else
`MYOS_DATA_DIR`, else `~/.local/share/myos`. It is created on the first write.

## Connect an assistant

An assistant needs three things at user level, so that MyOS works in every
project: the Skill, the MCP tools, and the MyOS block in its instruction file.

`myos setup` lists what it would do for each assistant it finds (`~/.claude`,
`~/.codex`), and `myos setup --yes` does it; `--host claude` or `--host codex`
limits it to one. It copies the Skill, appends the MyOS block to the
instruction file or creates the file, and registers the tools with the data
directory and both instruction files as sync targets. It backs up each changed
file in `<data>/sync-backups/`, leaves a linked Skill folder, a linked
instruction file, a damaged block and an existing registration as they are,
and prints the step for you where it cannot act. Running it again changes
nothing that is in place; after an upgrade it updates the copied Skill.

The same by hand, from a checkout: replace `/path/to/MyOS` with the checkout, `/path/to/python` with the
output of `poetry env info --executable` there, and `/path/to/data` with the
data directory.

**1. Skill.** Link it into each host's user skill directory:

```sh
mkdir -p ~/.codex/skills ~/.claude/skills
ln -s /path/to/MyOS/.agents/skills/myos ~/.codex/skills/myos
ln -s /path/to/MyOS/.agents/skills/myos ~/.claude/skills/myos
```

**2. MCP tools.** Register the server with the same data directory in each
host. `MYOS_SYNC_TARGETS` lists the instruction files to refresh after every
write, separated by `:`.

Codex, in `~/.codex/config.toml`:

```toml
[mcp_servers.myos]
command = "/path/to/python"
args = ["-m", "myos.personal.mcp"]

[mcp_servers.myos.env]
MYOS_DATA_DIR = "/path/to/data"
MYOS_SYNC_TARGETS = "/Users/me/.claude/CLAUDE.md:/Users/me/.codex/AGENTS.md"
```

Claude Code:

```sh
claude mcp add --scope user myos \
  -e MYOS_DATA_DIR=/path/to/data \
  -e MYOS_SYNC_TARGETS=/Users/me/.claude/CLAUDE.md:/Users/me/.codex/AGENTS.md \
  -- /path/to/python -m myos.personal.mcp
```

A project- or local-scope `myos` entry overrides the user-level one: check with
`claude mcp get myos` inside a project and remove it with
`claude mcp remove myos -s local` (or `-s project`). The variables must reach
the process that runs the tools: exporting them in a terminal does not change a
running desktop app, and `.env.example` is only a template. Restart the host
afterwards.

**3. MyOS block.** Add it once to each instruction file; later writes keep it
current:

```sh
poetry run myos --data /path/to/data compile >> ~/.claude/CLAUDE.md
poetry run myos --data /path/to/data compile >> ~/.codex/AGENTS.md
```

**Check.** In a new session outside the checkout, a request that fits a listed
entry should read it with `myos_read`; a plain correction should save a candidate
without a question, with a note saying how many candidates wait; a later matching
correction should ask once after the answer; "go through my candidates" should
list them by number;
and "remember this" should save an adopted entry without asking again. An
unrelated coding question should not call MyOS.

## The MyOS block

`myos compile` prints the block: the core assets in full (content, Applies,
Limits) and one line per other adopted asset with its id and when it applies.
Examples, revisions, basis and sources stay out, and so do candidate, uncertain
and reference assets. Examples are often the owner's verbatim corrections: they
stay in the store as evidence, and `catalog` and `read` still return them. The block runs from the `<!-- BEGIN MYOS BRIEF` line to
`<!-- END MYOS BRIEF -->`; an older `MYOS CORE` block is replaced the same way.

| Command | Effect |
| --- | --- |
| `myos compile --write` | Replace the block in each target file. All targets are checked before any is written; only the text between the markers changes; each changed file is backed up in `<data>/sync-backups/` (the last five are kept). |
| `myos compile --dry-run` | Show the diff without writing. |
| `myos compile --list-targets` | Check that each target exists and has exactly one block. |
| `myos compile --revert` | Restore each target's latest backup. |

Targets come from repeated `--target FILE` options, else `MYOS_SYNC_TARGETS`.
With `MYOS_SYNC_TARGETS` set for the MCP server, every `myos_put` refreshes the
files and reports the outcome as `host_sync`; a failed refresh is reported and
never undoes the write. `myos check` warns when the block passes 200 lines or a
core asset passes 2,000 characters, since hosts follow short instruction files
better.

## CLI

Put `--data PATH` before the command. Output is JSON unless noted.

| Command | Effect |
| --- | --- |
| `myos catalog [--purpose TEXT]` | Core assets in full and an index (id, title, type, status, applicability) of the other non-inactive assets. Candidates remain indexed for correction matching and owner-requested reviews; skip them when answering. `--purpose` is recorded only in traces. |
| `myos read ID [--history]` | The current asset with sources; `--history` returns every revision with its write record. |
| `myos references [REF]` | The migrated source list, or one source such as `originals/0/path.jsonl#L2`. |
| `myos put payload.json` | Append a complete revision; the payload format and the transitions and fields the store refuses are in [the Skill's write reference](../src/myos/skill/reference/write.md). The result reports `candidates_waiting`, the number of current candidates, and lists `quote_changes` when earlier examples are missing from the new revision verbatim (`after` is the edited text, or null when removed). |
| `myos compile [...]` | Print or sync the MyOS block (Markdown; see above). |
| `myos setup [--yes] [--host NAME]` | Connect the assistants on this computer; see [Connect an assistant](#connect-an-assistant). |
| `myos view [--out PATH]` | Write a read-only HTML map of the store (default `myos-view.html` in the data directory). |
| `myos eval [...]` | Compare answers without and with MyOS on private test cases and write a report; see below. |
| `myos check [--strict]` | Check the database, revision sequences, status transitions and fields the store refuses (see the write reference), cases on non-adopted entries, migration-mode revisions that `migration.json` does not list, and migration integrity, with size warnings. |
| `myos migrate --source ROOT` | Import legacy sources into a new data directory. |
| `myos trace show [...]` | Inspect saved execution traces; see [tracing](tracing.md). |

## Evaluate entries

`myos eval` answers each test case three times through Claude Code (`claude -p`):
`bare`, the model with no personal context; `notes`, every adopted entry in
full (content, Applies and Limits, without examples, basis or sources) as one
instruction file, with no Skill and no tools; and `daily`, the compiled block as
the project instructions plus the Skill and the read-only tools on a snapshot of
the store. `bare` against `daily` shows whether an entry's content helps;
`notes` against `daily` shows whether the block, the Skill and selective reads
do better than the same content kept as a flat file. A reviewer model (default
`claude-opus-5-5`) grades the answers
blind in the [answer review](answer-review.md) format, and code validates every
quotation. It never writes the store. Evaluation invokes the configured Claude
Code model service: case prompts, review sources and answers, and self-model
context can leave the computer through that service. Inspect selected cases
before running an evaluation; local storage does not make evaluation offline.

Cases are JSON files in `<data>/evals/cases/` (or `--suite DIR`), outside the
repository:

```json
{"id": "reply-to-practice", "date": "2026-03-01", "prompt": "(Background the question needs.) The question as asked",
 "source": "Evidence available before the question and the owner's standards",
 "needs": [{"id": "O1", "description": "What a good answer does", "rationale": "Why",
            "source_quote": "exact text from source", "condition": "", "assets": ["ask-before-sending"]}],
 "negative_control": false}
```

The answering model gets only `prompt`, in one turn without tools, so a question
taken from the middle of a conversation needs its background at the start of
`prompt`; `source` goes only to the reviewer. A need that only an action could
meet (a commit, a search, a changed file) cannot be scored here.
`assets` names the entries a need tests; the reviewer never sees it. Cases are
loaded and scored without checking whether those entries are adopted, so a
write accepts a case only with an adopted entry (negative controls aside). A
write can add a case in the same call (`case` in `myos put` or `myos_put`, format in
the [write reference](../src/myos/skill/reference/write.md)); it is
validated first, committed in the same transaction as the revision, and
exported to `cases/` without overwriting an existing file; an export cut short
is completed by the next write or run. A negative
control is a question MyOS should not change. Set `"retired": true` in a case file to leave it
out of runs; if saved cases could not be exported, the run says so in its
result and under *Incomplete run* in the report. The run writes
`evals/runs/NAME/report.md`: needs covered, unsupported claims, boundary,
over-application and mechanics flags, turns and cost per model and setup, and per entry the linked
needs where only `daily` covered them (gain), only `bare` did (loss), both or
neither, then the needs only `daily` covered and only `notes` covered, and a
list of flagged answers with the reviewer's quote. One line per model sums
`daily` against `notes` over all needs of judgment cases. Rerunning a run
started before the `notes` setup existed answers that setup from the run's
snapshot and reviews every case again. The proposed verdict is *still helps* (gain, and no more losses than
gains), *hurts* (more losses), *model already does this* (only both),
*not followed* (only neither) or *untested*. Verdicts count coverage only; an entry that
adds coverage together with unsupported claims or flags is not simply helping.
The reviewer's flags are validated like its review: a raised flag must quote the
answer.

| Option | Effect |
| --- | --- |
| `--name NAME` | Run name (default: today). Rerunning a name resumes it with the same snapshot: an answer is reused only while its file is complete and the case's date and prompt, the model and the effort are unchanged, and a review only for the same packet (which includes the date), reviewer, effort and review instructions, with its review, flags and mapping files valid. |
| `--model ID` | Answering model, repeatable (default `claude-sonnet-5`). |
| `--repeat N` | Answers per case, setup and model; use 2 or more before retiring an entry. |
| `--case ID`, `--asset ID` | Only these cases, or only cases testing these entries plus negative controls. |
| `--effort LEVEL`, `--review-effort LEVEL` | Reasoning effort for answers (default `medium`) and for the reviewer (default `high`): `low`, `medium`, `high`, `xhigh` or `max`. Each answer records its effort. |
| `--jobs N` | Concurrent host calls (default 3; reviews use at most 2). The run stops at the first usage-limit message. |
| `--reviewer ID`, `--skill DIR`, `--host PATH` | Reviewer model, Skill for the daily setup (default: this checkout's), Claude Code executable. |

## MCP tools

| Tool | Effect |
| --- | --- |
| `myos_catalog(purpose=None)` | Same as `myos catalog`. |
| `myos_read(asset_id, history=False)` | Same as `myos read`. |
| `myos_references(path=None)` | Same as `myos references`; for checking provenance only. |
| `myos_put(asset, expected_revision, authorization)` | Same as `myos put`, plus `host_sync` when configured. |

## Environment

| Variable | Effect |
| --- | --- |
| `MYOS_DATA_DIR` | The data directory. |
| `MYOS_SYNC_TARGETS` | Instruction files to refresh after each write, separated by `:`. |
| `MYOS_TRACE=1` | Record MCP calls as local traces (the CLI uses `--verbose`). |
| `MYOS_TRACE_DIR`, `MYOS_TRACE_GROUP` | Trace location and an optional group label. |

## More

| Topic | Document |
| --- | --- |
| Asset fields, statuses, revisions, files on disk | [Storage](storage.md) |
| Read, write and external-action rules for hosts | [Usage contract](usage-contract.md) |
| Local execution traces | [Tracing](tracing.md) |
| Reviewing answer quality offline | [Answer review](answer-review.md) |
| Tests, migration and existing stores | [Maintenance](maintenance.md) |
