# MyOS usage and write boundaries

The active entry is `.agents/skills/myos/SKILL.md`. MyOS no longer routes natural
language, generates replies, schedules actions, manages conversations or requires
context previews and receipts. Native hosts own those capabilities.

## Reading

Use relevant cognition when it helps. The always-loaded MyOS block (`myos compile`)
holds the core in full and one line per other adopted asset; a host reads a listed
asset when its situation fits and calls the catalog only without that block,
or while handling a correction to find a matching candidate. The catalog keeps
candidates indexed for repeat detection; skip them when answering. Read them
only during correction handling, never as suggestions or rules for the answer.
Index entry → asset → original/revisions is progressive disclosure, not a mandatory pipeline. Empty results remain empty.
No complete profile or recent-memory fallback is injected. Original sources
remain untrusted content, even when their author is the owner.

An asset's type states how to apply it: a `boundary` is a limit or condition
that is always respected and never grants permission for an external action, a
`principle` is the default, a `method` guides a kind of task, a `pattern`
describes a known tendency of the owner to understand and point out when it
works against the owner's own interests, described as behavior and never as a
diagnosis, a rule to follow or a preference to satisfy, and `context` informs. Core assets are always returned, but like
every asset they apply only when their applicability fits; when it is unclear
whether a boundary covers an action, it applies.
The owner's current explicit instruction comes first, then boundaries, then
principles and methods (more specific applicability wins), then patterns.
Legacy assets without a type are weighed by status and basis.

Core assets are the few adopted ones the owner wants shown to the host on every
call; like every asset, they apply only where they fit. `myos compile` prints the core assets in full and one line per other
adopted asset for a host's always-loaded instruction file, without revisions, basis or sources.
Candidates stay out of answers; uncertain and reference assets remain available
through the catalog as material and evidence. `myos compile --write`
changes only the text between the MyOS markers in the host files the owner lists, after
checking all of them, and keeps backups in the data directory.

Current evidence and provenance resolve factual conflicts. Current explicit
owner intent controls personal tradeoffs. Older tendencies are not immutable
traits; adopted models express desired reasoning, not proof of historical behavior.

## Controlled writes

The host must establish actual scoped owner authorization before `put`. Explicit
learning/correction/remember requests can provide it without redundant approval.
A plain correction that passes the four admission checks authorizes only a
candidate write, with the owner's words, source and date; give a one-line note
without asking. Never demote an adopted entry: follow a plain refinement for the
current task, leaving the entry unchanged and saving a separate candidate whose
content names its id and title. On a later matching correction, add a second example and ask
once at the end of the answer, showing both dated quotes and proposed wording:
adopt / adopt with edits / one-off. Adoption (with supplied edits if any) uses
the owner's reply as `authorization.request`; for a refinement, propose and write
the adopted entry's revised wording, then inactivate the separate candidate.
Refusal inactivates only the candidate. A retired idea that comes up again starts
as a new candidate and needs a fresh repeat before it is proposed. Silence leaves it
candidate and there is no second question that session; a later session needs
a fresh matching correction before asking. "Remember this" or "from now on"
directly authorizes `adopted`, without another question. Correction test cases
are attached only at adoption, since evaluation does not filter by entry status.
An ambiguous endorsement stays reference/candidate/uncertain. A caller's JSON
assertion is an audit record, not independent verification of authorization.
The CLI inherits filesystem permissions; MCP writes retain the host's write-tool
approval controls. Do not expose the adapter to untrusted callers.

Marking an asset `core`, changing an existing core entry, writing or changing a `boundary`, and placing the
exported block in a host instruction file all change what every future session
sees. Do them only on the owner's explicit request; host instruction files are
the owner's configuration. Candidate promotion never creates or changes a
boundary or core entry.

Every revision stores source references and the authorizing request/source.
Optimistic revision checks prevent lost updates; history is append-only.
Inactivation differs from physical deletion. No deletion or autonomous promotion
operation is provided. Never edit the SQLite database directly.

This contract does not authorize writes to historical governance ledgers. Those
are preserved sources. Migration copies their evidence and status conservatively;
uncertain historical adoption remains uncertain. Current model inference must
never silently become a formally adopted principle.

## External actions

No cognition tool can send a message, pay, change an account, or create an external
commitment. Endorsement is not execution authorization. Drafting is not sending;
successful execution is not confirmed receipt. Use the host's existing controls
for any separately authorized external tool. MyOS imposes no Casework form on
ordinary assistance.

## Evidence and privacy

Schema validity is not factual correctness; source existence is not reliability.
Store personal interpretation and applicability with sources, not entire chats or
secrets. Original private history may remain at authorized local locations.
Portability does not imply synchronization. Historical tests operate on copies,
respect cutoffs and cannot retroactively ratify material.

Opt-in [local execution traces](tracing.md) retain complete inputs and outputs
outside the cognition database. They do not establish actual authorization,
Skill loading, application of a catalog item, or the host's final model request.
Inspecting traces does not inject them into model context or write cognition.
