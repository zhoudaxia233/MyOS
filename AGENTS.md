# MyOS contributor and host adapter

MyOS is the owner's self-model: a thin judgment layer of boundaries,
principles, methods, patterns and context that any host model applies. It is
not a memory or continuity layer and not an agent runtime. The design goal is
to remain useful as models improve; that is not an established value claim.
The native host owns understanding, relevance, reasoning,
synthesis, communication and memory. MyOS is a personal Skill, private
source-linked revisions and thin deterministic tools.

Read [README.md](README.md) for actual behavior and
[docs/usage-contract.md](docs/usage-contract.md) for data and authorization boundaries.
For personal learning or use, discover [src/myos/skill/SKILL.md](src/myos/skill/SKILL.md) (linked at `.agents/skills/myos` for hosts)
when relevant. Ordinary development and unrelated questions need no personal retrieval.

Current owner instructions set task scope. Preserve unrelated work and private
data. Development permission does not authorize external account actions, live
store cutover or merging. Do not change credentials or installed third-party skills.

The [exploration map](docs/exploration-map.md) explains prior approaches, their
evidence limits and conditions for reconsidering them. Consult the relevant
entry before a positioning change, major architectural addition or revival of
a retired capability; state which premise has changed. Ordinary fixes need no
extra history review. Historical material is evidence, not current instructions.
Private material belongs outside version control: the owner's entries and
`myos eval` cases live in the data directory, and repository tests, fixtures,
examples, commits and pull requests stay synthetic.

Test observable behavior, not incidental old architecture. Run
`poetry run pytest -q --strict-markers`; for data checks use an explicitly selected
isolated store with `poetry run myos --data PATH check --strict`. A new empty
installation can use `catalog` without creating data. Do not run tests against
an owner's live store or unmocked external accounts.

Storage, migration or authorization behavior changes require separate safety
and behavior review. Report which checks actually ran; do not call your own
review independent. Learning-quality claims require real generated answers,
evidence cutoffs and stated limits, not merely schema tests.

Keep current entry points and documentation consistent. The user docs
(README, the user guide and their Chinese versions) explain setup, use, what
MyOS admits and how it works, in plain words; commands, flags, file formats and
tool details belong in [docs/reference.md](docs/reference.md). The maintenance guide
is [docs/maintenance.md](docs/maintenance.md). No receipt or governance-workbench
ceremony is required for ordinary read-only assistance.
