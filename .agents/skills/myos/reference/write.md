# Writing a MyOS asset

Send one complete asset through `myos_put` (or `poetry run myos put payload.json`):

```json
{"asset":{"id":"stable-id","title":"Short title","type":"principle","content":"Personal interpretation; label claims and synthesis","applicability":"When useful","boundaries":["Exceptions and limits"],"status":"candidate","basis":"Explicit statement / synthesis / inference, with uncertainty","sources":[{"ref":"authorized source path or message ID","timestamp":"source time if known"}],"examples":[{"text":"A concrete instance","source":"message ID"}]},"expected_revision":0,"authorization":{"request":"Exact scoped owner instruction","source":"Message or authorized source reference"}}
```

- `type` is required except for `reference` and `inactive` assets.
- Set `core: true`, and write or change a `boundary` or an existing core entry, only on the owner's explicit instruction: both change every future session. Core holds at most 10 adopted assets; when it is full, ask the owner which one to drop.
- Send the complete asset with the current revision as `expected_revision`; on a conflict, read again and integrate before writing.
- The store refuses these writes outside migration, so do not plan around them: moving an adopted entry to any status but `adopted` or `inactive` (inactivate it, or write a separate candidate); any status change of an `inactive` entry (a returning idea gets a new id); a write that makes an entry `adopted` and also sets `core` or changes the type to `boundary`, whatever status it came from (adopt first, then make that change in a separate revision on the owner's explicit instruction); a `case` on an entry that is not `adopted`, unless it is a negative control; a case `date` that is not YYYY-MM-DD. `myos check` reports these transitions in existing stores.
- Field format: `title`, `applicability` and each item of `boundaries` are one line of visible text (no line breaks, control or direction characters), because they become single lines of the host instructions; put details in `content`, which may span lines. An `id` has no whitespace, backticks or invisible characters. Never set `authorization.mode`: `"migration"` is reserved for `myos migrate`, and a payload holds only `asset`, `expected_revision`, `authorization` and an optional `case`. `myos check` reports these fields on each entry's current revision, and migration-mode revisions that `migration.json` does not list.
- For a plain refinement, leave the adopted entry unchanged and write a separate candidate whose `content` begins "Refines `ID` (Title):". Adoption writes the approved revised wording to that adopted entry, preserving its sources and unaffected applicability and adding the correction examples and sources, then marks the refinement candidate `inactive`; refusal inactivates only the candidate. At adoption, update `basis` with the date and that the owner adopted it. Both writes use the owner's reply as authorization, and only the adopted revision carries a test case.
- `authorization` records the owner's exact request and its source; the host verifies actual permission. A plain correction authorizes a candidate write, not adoption. "Remember this" / "from now on" directly authorizes adoption; after a repeat or in a review the owner asked for, the owner's adoption reply (including any supplied edits) is `authorization.request`, and `authorization.source` names the item when one reply answers several. A refusal authorizes `inactive`. Do not request a second approval.
- Store interpretation with sources, never secrets or whole chats. Change the store only through `put`. `inactive` hides an asset from the catalog and keeps its history.
- Keep each correction's exact quote in `examples[].text`, the message reference in `source`, and its known date in the matching `sources[].timestamp`. Add the later quote without losing the first. No new fields are needed.
- Copy existing quotes from the asset you read and write them as plain UTF-8 text; never retype them or turn them into `\u` escapes, which can silently swap a character. After the write, check `quote_changes` in the result: every listed change must be one you intended.
- The catalog keeps candidates discoverable for correction matching and owner-requested reviews; they are never used in answers or listed in the always-loaded block. Every write result outside migration reports `candidates_waiting` for the write note.

## Test case from a correction

When writing `adopted` for an entry learned from a correction to a real answer, add `case` next to `asset` in the same write; until then the candidate keeps only its sourced correction examples. When one revision adopts several corrections, attach the most recent one's case and say the others have none.

```json
"case":{"id":"short-unique-id","date":"YYYY-MM-DD of the request","prompt":"The request exactly as the owner asked it","source":"What you knew before answering, then: Owner's correction: <the owner's words>","needs":[{"id":"C1","description":"What the corrected answer does","rationale":"Why the owner wants it","source_quote":"exact text from source","condition":""}]}
```

- One need per point the correction makes; each `source_quote` is copied exactly from `source`. Needs without `assets` are linked to the written entry.
- Keep only what the question needs: no secrets, no unrelated people. The case stays in the data directory beside the store.
- Build the case from an actual corrected request and its available evidence, not the later adoption question; do not invent missing context. Material or "remember this" without a corrected real answer, candidates and a one-off reply create no case. An existing case id is refused; pick another.
