# Writing a MyOS asset

Send one complete asset through `myos_put` (or `poetry run myos put payload.json`):

```json
{"asset":{"id":"stable-id","title":"Short title","type":"principle","content":"Personal interpretation; label claims and synthesis","applicability":"When useful","boundaries":["Exceptions and limits"],"status":"candidate","basis":"Explicit statement / synthesis / inference, with uncertainty","sources":[{"ref":"authorized source path or message ID","timestamp":"source time if known"}],"examples":[{"text":"A concrete instance","source":"message ID"}]},"expected_revision":0,"authorization":{"request":"Exact scoped owner instruction","source":"Message or authorized source reference"}}
```

- `type` is required except for `reference` and `inactive` assets.
- Set `core: true`, and write or change a `boundary` or an existing core entry, only on the owner's explicit instruction: both change every future session. Candidate promotion never creates or changes either. Core holds at most 10 adopted assets; when it is full, ask the owner which one to drop.
- Send the complete asset with the current revision as `expected_revision`; on a conflict, read again and integrate before writing.
- Never demote an adopted entry to candidate. For a plain refinement, leave it unchanged and write a separate candidate whose `content` names its id and title. Adoption writes the approved revised wording to that adopted entry, preserving its sources and unaffected applicability and adding the correction examples and sources, then marks the refinement candidate `inactive`; refusal inactivates only the candidate. Both writes use the owner's reply as authorization, and only the adopted revision carries a test case. This never bypasses the boundary/core restriction above.
- `authorization` records the owner's exact request and its source; the host verifies actual permission. A plain correction authorizes a candidate write, not adoption. "Remember this" / "from now on" directly authorizes adoption; after a repeat, the owner's adoption reply (including any supplied edits) is `authorization.request`. A refusal authorizes `inactive`. Do not request a second approval.
- Store interpretation with sources, never secrets or whole chats. Change the store only through `put`. `inactive` hides an asset from the catalog and keeps its history.
- Keep each correction's exact quote in `examples[].text`, the message reference in `source`, and its known date in the matching `sources[].timestamp`. Add the later quote without losing the first. No new fields are needed.
- The catalog keeps candidates discoverable for correction matching; they are never used in answers.

## Test case from a correction

When writing `adopted` for an entry learned from a correction to a real answer, add `case` next to `asset` in the same write. For a candidate, keep only its sourced correction examples; wait for adoption before attaching a case. `myos eval` loads saved cases and scores their needs regardless of the linked entry's status, so a candidate's case would test an unapproved rule.

```json
"case":{"id":"short-unique-id","date":"YYYY-MM-DD of the request","prompt":"The request exactly as the owner asked it","source":"What you knew before answering, then: Owner's correction: <the owner's words>","needs":[{"id":"C1","description":"What the corrected answer does","rationale":"Why the owner wants it","source_quote":"exact text from source","condition":""}]}
```

- One need per point the correction makes; each `source_quote` is copied exactly from `source`. Needs without `assets` are linked to the written entry.
- Keep only what the question needs: no secrets, no unrelated people. The case stays in the data directory beside the store.
- Build the case from an actual corrected request and its available evidence, not the later adoption question; do not invent missing context. Material or "remember this" without a corrected real answer, candidates and a one-off reply create no case. An existing case id is refused; pick another.
