# Records, statuses, and storage

An asset holds durable personal judgment, not a complete personality profile or an ongoing matter's status. New entries follow the admission checks in the [user guide](getting-started.md#what-gets-in). Migrated records can retain historical fields without making those fields suitable for new entries.

| Field | Meaning |
| --- | --- |
| `id` | Stable identifier; keep it when revising the same understanding. |
| `title` | Short title in the catalog. |
| `content` | Durable personal judgment and its tradeoffs; distinguish facts, personal statements, and assistant synthesis in the text. |
| `applicability` | Situations in which it is useful. |
| `boundaries` | Exceptions, limitations, counterexamples, or conditions where it does not apply. |
| `status` | One of the statuses below. |
| `basis` | Evidence and uncertainty, not an automatically calculated confidence score. |
| `sources` | A nonempty list of source references, optionally including source timestamps and other information. |
| `type` | How a host uses the asset; see the table below. Required unless the status is `reference` or `inactive`. |
| `core` | Optional, `true` or `false`. A core asset is returned in full by every `catalog` call so that it is never missed; like every asset, it applies only when its applicability fits. Only `adopted` assets with a type can be core, at most 10 at once, and only on the owner's explicit request. |
| `examples` | Optional list of `{"text", "source"}` pairs: concrete instances of the asset, each with its own source. |

All fields except `core` and `examples` are required by `put`, with the `type` exception above; additional fields can be retained. Migrated records may also contain `legacy_record`, historical adoption evidence, and chronology uncertainty, and usually have no `type`: they appear as `unclassified` until the owner reviews them. A status label is not a reason to ignore these conditions.

### Types tell hosts how to use an asset

| Type | Meaning for use |
| --- | --- |
| `boundary` | Limits and conditions on what agents do for the owner. Always respected; no other asset overrides it. A boundary can restrict an action and never grants permission for an external one. When it is unclear whether a boundary covers an action, it applies. |
| `principle` | How the owner judges and acts. Applied by default; the owner's current explicit intent overrides it. |
| `method` | How to think about or carry out a recurring kind of task. |
| `pattern` | A known tendency of the owner. Used to understand and anticipate the owner, and pointed out when it works against the owner's own interests; never a rule to follow or a preference to satisfy. It describes behavior, never a diagnosis. |
| `context` | Facts, values and stable preferences about the owner. |

When assets conflict, hosts apply the owner's current explicit instruction first, then `boundary`, then `principle` and `method` (the more specific applicability wins), then `pattern`, to anticipate the owner and flag what works against their interests.

### Statuses do not form an automatic approval engine

| Status | Meaning for use |
| --- | --- |
| `reference` | Saved for reference; does not imply endorsement. |
| `candidate` | An unapproved idea, never used in answers or compiled into the block. Its sourced examples let a later correction be recognized as a repeat; the owner can also go through candidates on request. |
| `adopted` | Recorded as an adopted personal method or understanding; still neither objective truth nor action authorization. |
| `uncertain` | Adoption, chronology, or interpretation is uncertain. |
| `inactive` | Excluded from the default catalog; the current record and history remain readable by ID and in `myos view`. |

**Every status except `inactive` still appears in `catalog`.** `catalog` returns `{"core": [...], "index": [...]}`: core assets with their full content, and every other non-inactive asset as its id, title, type, status and applicability. Candidates remain indexed so corrections can find repeats across sessions and the owner can go through them on request; hosts skip them when answering and read them only while handling a correction or in a review the owner asks for. Other assets, core included, apply only where they fit, according to status and basis.

A first plain correction that passes admission becomes a candidate with the owner's exact words in `examples` and dated `sources`. Unendorsed learning material, and ideas the owner asks to keep for later, are candidates too. A later matching correction adds another example; the host asks at the end of its answer whether to adopt, adopt with edits or treat it as one-off. When the owner asks to go through candidates, the host lists them by number and the owner answers each, or leaves it waiting. The reply authorizes `adopted` or `inactive`. Silence leaves it a candidate, with no repeat question that session. Candidates never enter the compiled block; every `put` result outside migration reports `candidates_waiting`, which the host's write note passes on to the owner. "Remember this" or "from now on" directly authorizes adoption. The store refuses moving an adopted entry to any status but adopted or inactive, any status change of an inactive one, a write that adopts an entry and also sets core or the boundary type, and a case on an entry that is not adopted; `myos check` reports such transitions in older histories. There is no scheduled promotion, automatic approval, or physical deletion command.

Refinements leave an adopted entry unchanged and use a separate candidate whose `content` names its id and title; approval writes a new adopted revision of that entry, then inactivates the candidate. A retired idea that comes up again starts as a new candidate and is proposed again only after a fresh repeat or in a review the owner asks for.

### Files on disk

The CLI's `--data` option takes precedence over `MYOS_DATA_DIR`; the fallback is `~/.local/share/myos`. MCP uses its process's `MYOS_DATA_DIR` and does not accept the CLI's `--data` option.

```text
Your selected private data directory/
├── cognition.sqlite3       # Full asset revisions, recording times, authorization records, test cases saved with a write
├── evals/                  # myos eval: cases/ (editable case files) and runs/
├── originals/              # Migrated originals; not created by a fresh manual write
├── references.json         # Migrated source catalog
└── migration.json          # Manifest, provenance, digests, imported-revision verification
```

A correction's test case is attached only when its entry is adopted, because `myos eval` does not filter cases by entry status. A test case saved with a write is committed in the database together with its revision and exported to `evals/cases/` after every write and at every `myos eval`. The database keeps the case as committed; the file is the editable copy that `myos eval` reads, so edits to the file win. Deleting the file brings the committed case back on the next export; to drop a case, set `"retired": true` in its file.

The database is created only on the first authorized write or migration. On a fresh installation, `catalog` returns `{"core": [], "index": []}` without creating storage. `myos view` writes `myos-view.html` into this directory unless `--out` names another path. Before the database exists, `check --strict` reports missing storage; this does not mean an existing store is corrupt.

### Revisions and concurrency

Every `put` saves a complete version, not a partial JSON patch. Use `expected_revision: 0` for a new asset and the revision just read for an update. A SQLite transaction checks the version: if another agent has already written, the stale request fails instead of overwriting that update. The caller should read again, integrate changes, and decide whether to write, rather than blindly retrying old content.

Previous versions, sources, and the authorizing request/source are retained. `recorded_at` is the write time, not the time of the source event. `inactive` preserves history and remains available through `read ID`.

### Source expansion boundaries

Generated migration references such as `originals/0/...jsonl#L2` can be passed directly to `references`; `#L2` means the second line, counting from one. Without a line number, the entire text file is returned. Invalid or out-of-range line numbers and paths escaping `originals/` are rejected. Symlink targets must also stay within that directory.

`put` stores references; **it does not download articles or archive chat contents**. Ordinary message IDs, web URLs, and `file:vault/...` are not automatically resolved by this reader. Use the host's existing authorized source tools for those references. Sources that need long-term retention need a stable, authorized storage location; there is no general attachment archive API or PDF/image parser.
