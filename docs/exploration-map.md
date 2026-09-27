# MyOS exploration map

Prepared on 2026-09-27, when MyOS moved to this repository with a fresh Git
history. This is project history and contributor guidance, not a roadmap or an
authorization to change the product. Current behavior is defined by the
[README](../README.md) and [usage contract](usage-contract.md).

## What this map preserves

MyOS explored a chat application, a governed runtime, domain workflows and a
personal learning Skill before reaching its current self-model design. The
useful inheritance is the reasoning, useful mechanisms, negative results and
conditions for trying again. Retiring code does not establish that its original
goal was wrong or that its implementation never worked.

The reviewed baseline contains 1,432 reachable commits. This first map follows
the mainline history and selected decisions, implementation changes and review
records, including recent private evaluations outside Git; it is not an audit
of every diff or every local record. It excludes private case narratives,
owner records, conversation excerpts and original evaluation inputs. Historical
sources are mapped to stable lesson IDs in a separate private evidence index.
The public explanations below do not require access to that index.

Evidence labels matter:

- **Implementation:** retained code or a diff establishes a particular change.
  That alone does not establish everyday usefulness.
- **Recorded decision:** a dated document establishes the rationale recorded
  then. It is not a current rule or proof that the rationale was correct.
- **Historical report:** a review describes an outcome. Some original run
  artifacts are unavailable; the report must not become a new acceptance claim.
- **Synthesis:** the proposed lesson and revisit condition below, inferred from
  those records. They remain open to correction.

## Main turns

| Period | Main direction | Subsequent change |
| --- | --- | --- |
| February–March 2026 | Personal modules, append-only logs, routing, providers, scheduling, chat and handoff | The project accumulated its own interaction and runtime responsibilities. |
| April–May 2026 | External-agent access, governed changes, lineage and a governance console | Conversation ownership moved to hosts, while governance and its interfaces expanded. |
| June–August 2026 | Thin integration rules, domain workflows, receipts and context-selection repairs | The distinction between functional machinery and useful assistance became an explicit evaluation concern. |
| September 2026 | Matched comparisons, then removal of the proprietary runtime in favor of a Skill and private revisions | The host took over understanding, relevance, synthesis, communication and memory. |
| Late September 2026 | Self-model types, always-loaded core entries, narrow admission, correction approval and entry-level evaluation | The product focuses on approved judgment; sustained incremental value remains a question to measure. |

Periods overlap. Document dates can precede merge dates, and later snapshots
sometimes amend earlier decisions. The private index pins exact versions rather
than treating the latest text of an old document as its original wording.

## E01 — Owning the conversation and runtime

**Intent.** Make personal context usable through a complete interaction loop,
with API providers and a copy-and-paste fallback.

**Path and outcome.** The project implemented chat, streaming, sessions,
providers, routing and scheduled work. An April decision reported that the
conversation layer had become a competing application without a reliable useful
end-to-end experience. Conversation ownership moved to external hosts, but
runtime components survived that first change. The September Skill refactor
later removed proprietary orchestration, generation and related runtime paths.
These are distinct changes, not one deletion. **Implementation + recorded
decision; the April usability judgment is a historical assessment.**

**Carry forward.** Preserve portable personal judgment and narrow storage
guarantees. Access through an API does not require owning the assistant around
that API. A working host should not need a second conversation engine to apply
MyOS.

**Revisit when.** A concrete required capability is absent from the intended
host, and a bounded integration demonstrates useful behavior that cannot be
obtained through the host's existing extension surface.

## E02 — Selecting context without inventing relevance

**Intent.** Retrieve useful personal context automatically, including across
languages and sessions.

**Path and outcome.** Lexical routing, recent-record fallbacks, broad profile
loading, semantic candidates and compact context were all explored. Retained
changes remove a fallback that supplied recent memory when nothing matched.
Later records distinguish a valid source ID from evidence of relevance. The
current host reads applicable entries; it may select none. Core entries are
available up front, but their applicability still limits their use.
**Implementation + recorded design.**

**Carry forward.** An existing record is not necessarily relevant, and relevance
is not proof of truth or permission. Preserve exceptions and uncertainty when
compressing. Empty retrieval is a legitimate result; filling it with a general
profile can contaminate an unrelated answer. The useful mechanism is scoped
discovery, not the old routing vocabulary.

**Revisit when.** Observed misses on current tasks justify a retrieval change.
Compare both recovered requirements and false inclusion, including unrelated
and multilingual controls, before expanding automatic injection.

## E03 — Governance and the difference between evidence and authority

**Intent.** Let the owner control what is adopted, changed or retired, while
keeping a trace of why.

**Path and outcome.** The project separated constitutional rules, principles,
proposals, ratifications and derived tiers. This preserved useful distinctions
but created a large lifecycle and interface surface. The current design uses
source-linked revisions and explicit statuses, with the native host responsible
for establishing authorization. Candidate entries remain unused in answers;
repeated corrections prompt a choice rather than automatic adoption.
**Recorded decisions + current implementation and Skill contract.**

**Carry forward.** Retain the distinctions, not every historical object type:
recorded is not approved; approved is not factually true; approved personal
judgment is not permission to act. A caller's authorization field records a
claim—it cannot independently prove consent. Proposal refinements must not
silently overwrite or demote an adopted entry.

**Revisit when.** A reproducible authorization or competing-write problem cannot
be handled by the existing host boundary and revision model. Name that problem
before introducing another approval lifecycle.

## E04 — Making internal structure into the user interface

**Intent.** Make personal knowledge and its changes inspectable through queues,
maps, source shelves, detail panes and review history.

**Path and outcome.** Several console layouts and terminology passes were
implemented. A corrective design explicitly reported that the browser felt like
a command manual: the owner had to understand payloads, layers and intermediate
states to accomplish a task. Later work emphasized consequences and the next
responsible actor. The full governance console was eventually retired.
**Implementation + recorded diagnosis; no new usability study was run here.**

**Carry forward.** Inspection and provenance were useful goals. Lead a user
surface with what needs attention, what changes and who acts next; disclose
mechanics only when useful. A reference view is not actionable work. A new
layout or favorable simulated review does not demonstrate everyday usefulness.

**Revisit when.** A specific inspection or editing task is awkward in the host
and current local view. Demonstrate that task first, including safe failure and
accessibility, before rebuilding a general console.

## E05 — Domain workflows and the continuity promise

**Intent.** Turn personal judgment into help on real work: correspondence,
ongoing cases, creative work, attention checks and external integrations.

**Path and outcome.** The repository implemented domain-specific packets,
previews, validators and workflows. Integration decisions repeatedly assigned
raw records and external execution to their owning systems. Casework's own
documentation explicitly described a no-write packet model, not a durable case
store. Later audits distinguished recovering context through host history or a
case archive from a MyOS contribution. These workflows were removed from the
current core. **Implementation + recorded decisions + bounded historical reports.**

**Carry forward.** A correct preview does not establish persistence or future
resumption. Keep completed actions, pending actions and evidence distinct when
testing continuity. Useful domain work may belong in a host Skill or separate
project; its usefulness does not establish that it belongs in MyOS. Creative
enjoyment is also a valid goal and should be assessed on its own terms.

**Revisit when.** A real domain task reveals missing personal judgment or a
useful domain capability. Evaluate judgment within MyOS when it fits. If the
capability itself is the need, evaluate it as a separate Skill or project on
its own merits; it need not satisfy MyOS's current self-model positioning.
Admission into the core remains a separate scope decision.

## E06 — Storage simplicity, atomicity and conservative migration

**Intent.** Keep records inspectable and portable without losing their origins
or the owner's choices.

**Path and outcome.** Early decisions retained append-only JSONL to avoid an
unjustified migration. Later documents describe multi-file materialization and
rollback limitations; an archival audit reports concurrency and partial-write
defects whose original reproductions are no longer retained. The current store
uses SQLite transactions and expected revisions. Migration preserves original
sources and uncertainty; follow-up fixes distinguish unknown history from an
unknown retirement date. **Recorded tradeoffs + historical defect reports +
current implementation and regression coverage.**

**Carry forward.** Readability and atomicity solve different problems. Preserve
source bytes, fail on stale writes, and keep inactivation distinct from
deletion. File order or a newer-looking snapshot cannot establish consent or
reactivation. An independently authorized, demonstrably later reactivation
must also remain possible; conservatism must not become permanent paralysis.

**Revisit when.** A measured storage requirement exceeds the existing model.
Choose the smallest change that preserves concurrent-write, migration and
recovery guarantees. Reconsider multi-file transactions if a bounded comparison
shows they meet the concrete requirement better than the current store without
weakening those guarantees. Their past removal alone is not a veto.

## E07 — Knowing a fact does not make it suitable for an outward draft

**Intent.** Preserve useful situational details when helping the owner decide
or communicate.

**Path and outcome.** Retained repair records describe drafts that attributed a
previous question to the wrong recipient and carried internal preparation
details into outward text. The repair sharpened communication-evidence and
disclosure requirements. The generated-answer findings are historical reports;
the corresponding code and synthetic checks remain in Git history.
**Historical report + implementation.**

**Carry forward.** Internal context can inform reasoning without belonging in
the message. A prior communication claim needs evidence for the same recipient,
substance and state. Draft, approval, execution and receipt are separate facts.
Preserve necessary conditions while minimizing disclosure; indiscriminately
shortening the answer can remove the very condition the owner needs to check.

**Revisit when.** A concrete outward task exposes a missing boundary. Test the
actual final draft with synthetic facts, not only whether a packet retained
its fields. No historical example supplies current sending permission.

## E08 — Proving usefulness rather than successful machinery

**Intent.** Establish that MyOS improves assistance over a capable native host.

**Path and outcome.** The project built structural evaluators, receipts, blind
comparison tooling, compact-context comparisons and later entry-level
evaluation. Several archived evaluations report mixed, tied or negative
outcomes. Some original inputs, answers or reviews are unavailable. A later
cold-start report records a working discovery/transport chain without a
distinctive decision benefit, and records additional context/call burden.
**Implementation + historical reports, not newly reproduced outcomes.**

Private comparisons on September 26–27, 2026 tested a bare host, the same
personal records as flat notes, a Skill with selective reads, and the daily
configuration, followed by two delivery refinements. Flat notes improved
model-reviewed requirement coverage over the bare host; the tool-using
conditions did not establish a consistent advantage over the same content as
notes. Neither result shows equivalence. The owner's blind review of the
first-round Opus answers, registered as the primary measure, found no real
difference in 7 of 12 cases and no consistent advantage for any condition:
the bare host was best or tied-best in three cases, and the Skill condition
led flat notes 3–2 where the owner separated them. The model-reviewed gain
from flat notes was therefore not confirmed by the owner's review. The reports
identify concrete failure mechanisms:

- **Trigger and reading gaps.** Project and research tasks sometimes did not
  activate the Skill, despite relevant entries applying to them. Some runs read
  the catalog without opening a relevant entry; successful discovery did not
  ensure that the needed judgment reached the answer.
- **Rules applied at the wrong scale or in the wrong situation.** A simple
  appointment confirmation received the full analytical procedure for a
  consequential message. In the first rerun, a thank-you note received a
  dispute strategy. More personal context could increase friction or import
  an inappropriate stance.
- **A missed acceptance criterion.** The first rerun required coverage no lower
  than flat notes on each model. Both the full and layered instruction variants
  missed that bar: one fewer covered requirement on Sonnet and three fewer on
  Opus. Choosing the layered variant afterward did not turn that miss into a
  pass. Its recorded length constraint and prospective scaling rationale were
  separate from demonstrated answer quality.
- **Evaluation-environment interference.** Date objections persisted even in
  single-turn runs. The report attributed the problem mainly to the host's
  current date conflicting with the replay date, not only to stored metadata.
  A replay-environment defect must not be misdiagnosed as a retrieval defect.

The next refinement reduced turns relative to the earlier layered variant,
but still did not establish an advantage over flat notes, which had lower
reported cost. The initial comparison used 12 judgment cases and three controls
with two models and one answer per case and condition. The report includes the
owner's completed blind review of the first-round Opus answers; that review
does not cover subsequent reruns. Small samples, model-based grading and
requirements partly derived from known owner standards limit generalization.
These are reported results, not a fresh reproduction.
Private case labels, personal circumstances and monetary amounts are omitted.

**Carry forward.** Distinguish four questions: did it run; did it retrieve and
apply the right material; did the answer improve; did actual use justify the
total effort? Support and request coverage are separate. A shorter answer,
more citations, a trace or a valid review packet is not a quality verdict.
Reported ties and regressions are evidence to preserve, not inconvenient cases
to tune away. Local traces do not capture the complete host prompt or prove
that a retrieved entry influenced the answer. Preserve missed acceptance
criteria when a design is adopted for other reasons. Test simple replies and
inapplicable contexts as well as demanding tasks; respect applicability and
explicit exceptions instead of applying every procedure at full strength.
Check the replay environment before attributing failures to the product.

**Revisit when.** A concrete improvement is predicted. Compare native help,
a realistically maintained note when relevant, and MyOS under matched model,
tools, source access and evidence cutoffs. Retain actual inputs, outputs,
settings, mappings and reviews privately; label exposed cases, missing evidence
and setup cost. Use new cases for generalization claims and real use for owner
burden claims. Do not invent results from a passing schema or test suite.
Include private evaluation reports outside Git when assembling project history;
keep their source locators private and publish only generalized mechanisms and
qualified results.

## E09 — A self-model instead of a transcript or a frozen personality

**Intent.** Carry durable personal judgment across interactions without making
the owner maintain a general archive inside MyOS.

**Path and outcome.** The September refactor reduced the system to a personal
Skill, private source-linked revisions and thin tools. Subsequent changes
introduced asset types, core entries available in host instructions, narrow
admission and explicit correction adoption. The current Skill excludes events,
task status and generic good advice from new judgment entries. These are
implemented design choices; longitudinal learning and superiority over a simple
maintained note are not established by this map. **Implementation + current
contract; sustained value remains unproven here.**

**Carry forward.** Store what changes judgment in a named kind of situation,
with boundaries and evidence. Do not treat an inferred pattern as an order or
old preferences as current intent. Project exploration belongs in project
records such as this map, not in the owner's self-model. The host's ability to
read a correction is a mechanism result, not proof of good future application.

**Revisit when.** Actual use exposes missing judgment or excessive maintenance.
Test a scoped correction in a fresh interaction, including an exception and an
unrelated task. Simplify or retire entries that add burden without useful effect.

## E10 — Keeping history without shipping private evidence or stale instructions

**Intent.** Preserve hard-earned exploration while keeping the distributable
project understandable and private material private.

**Path and outcome.** Runtime/source separation was repaired incrementally.
Retired material was collected into an archive with preservation references,
then removed from the active tree after migration. The material remains in old
Git history. At the reviewed baseline, contributor instructions pointed to an
old commit for that history; such references cannot resolve in an independent
new repository and need replacement during export.
**Implementation + current documentation.**

**Carry forward.** A clean current tree does not establish clean history. Keep
the public explanation self-contained and the exact evidence private. Do not
copy the old Git directory, raw records or historical policies into a public
bootstrap. An old accepted decision explains a past choice; it does not make
the old architecture authoritative again. Ignored local evidence also needs
preservation separately from a hosted repository archive.

**Revisit when.** Preparing a concrete export. Review the exact file allowlist,
contents, examples, links, metadata and initial commit; verify operation without
old history or a live personal store. Preserve required attribution. Public
release and archival remain separate actions requiring the owner's instruction.

## How to use this map

For a positioning change, a major architectural addition or reintroduction of
a retired capability, consult the matching entry and state:

1. Which current need is unmet, with evidence.
2. Which old assumption has changed, or which old conclusion is being challenged.
3. What small comparison would justify continuing, and what result would stop it.

This is contributor guidance, not a new gate for ordinary fixes. Where
the old outcome is unverified, say so instead of treating it as a veto. When a
new result contradicts a lesson, retain the old result and add the changed
conditions rather than rewriting the past as inevitable.

## Open questions

- How much does the current self-model improve real assistance compared with
  native memory or a small maintained instruction file, after maintenance cost?
- Does correction adoption work reliably across different hosts and new tasks,
  including exceptions and changes of mind?
- Does always-loaded personal context prevent omissions without creating
  irrelevant influence or avoidable disclosure?
- Which private historical lessons are still missing from this first map?

This document is an initial synthesis, not a privacy clearance, independent
review or fresh product-value evaluation.
