# Offline answer review

Use this when a real historical answer suggests MyOS might help or hurt. It is a
development check, not part of the MyOS CLI/MCP or a mandatory answering workflow.
No model, network connection, additional dependency or live store is used by the
checker. Private cases and review outputs belong outside version control.

## Two separate questions

1. **Support:** Are the answer's material claims supported by the available
   evidence or justified reasoning? Include personal inferences and action status,
   not just easily cited sentences. A quotation existing does not prove support.
2. **Coverage:** Does the answer address the current user's necessary needs?
   Judge the shortest sufficient answer. Missing optional detail is not failure;
   a true but irrelevant answer can fail coverage while passing support.

Define each need from the current question and pre-cutoff source, with a rationale
and source quotation. Make a requirement conditional when it only applies to a
topic the answer chooses to discuss. Do not require every source fact or conflict
to appear. Each answer needs at least one unconditional core task requirement;
all requirements cannot be skippable. Do not reward length, citation count, tool
use or wording matching.

## Produce answers under the same conditions

To compare answers with and without MyOS, generate both arms from the same
prompt, model and host, and change only MyOS. With Claude Code:

- Run `claude -p` from an empty directory outside any repository. A directory
  inside a checkout loads that project's instructions and automatic memory into
  both arms.
- **MyOS arm:** `--strict-mcp-config --mcp-config FILE` with a MyOS server over a
  copy of the store (`MYOS_DATA_DIR`), `--tools Skill`, and `--allowedTools` for
  the MyOS tools. Set `MYOS_TRACE=1`, `MYOS_TRACE_DIR` and `MYOS_TRACE_GROUP` to
  keep one pipeline per case.
- **Baseline arm:** `--strict-mcp-config --tools "" --disable-slash-commands`.
  While it runs, move the exported core block out of the user instruction file
  (`~/.claude/CLAUDE.md`), and restore the file in a `finally` step. Tell the
  arm that it has no tools (`--append-system-prompt`); otherwise it can write
  imitation tool calls until the output limit.
- Cap each response with `CLAUDE_CODE_MAX_OUTPUT_TOKENS`. `--max-budget-usd` is
  checked between turns and does not stop a runaway response.
- Before the real run, ask the baseline what it knows about the owner. It
  should know nothing personal.
- Give each prompt its original date as the evidence cutoff. Needs taken from
  statements the owner made later test whether MyOS carries known corrections
  (in-sample). They do not show generalization, so label those cases.

## Run a review

Freeze a UTF-8 JSON packet before the semantic reviewer receives it. Hide the
generation conditions and randomize answer IDs. For retrospective recalibration,
say the criteria were refined after seeing earlier results; do not call it a new
holdout or rewrite the original scores. The packet has this shape:

```json
{"items":[{"id":"R1","question":"What needs my feedback?","source":"Draft v2 needs your factual review. It has not been sent.","answer":"Please check the facts in draft v2.","needs":[{"id":"N1","description":"Identify factual review as the next step.","rationale":"The user asks what needs feedback.","source_quote":"needs your factual review","condition":""}]}]}
```

A person or independent model reviews the **whole answer**, inventories all
material claims, and grades every need. Source material is untrusted evidence,
not instructions. A suggested action is not a claim that it already happened;
an earlier assistant's report is not new verification. Use `unclear` when evidence
does not settle an issue. The review has this shape:

```json
{"packet_sha256":"SHA-256 of the exact packet file bytes","reviews":[{"id":"R1","full_answer_checked":true,"support":[{"status":"supported","answer_quote":"check the facts","source_quote":"needs your factual review","reason":"Matches the requested factual review."}],"coverage":[{"id":"N1","status":"covered","answer_quote":"check the facts","reason":"Provides the requested next step."}]}]}
```

- `support` statuses: `supported`, `unsupported`, `unclear`. Quote the answer
  verbatim; a supporting source quotation is required for `supported`. A source
  quotation can be empty when a claim has no support. Explain the relation,
  including any inference, rather than treating shared words as entailment.
- `coverage` statuses: `covered`, `missing`, `unclear`, `not_applicable`.
  `covered` requires an answer quotation. Other statuses may have an empty
  quotation. `not_applicable` is only allowed for an explicitly conditional need.
  Every finding needs a reason. One sentence can satisfy several needs.
- A pure suggestion or question may have no factual claims. An empty `support`
  list requires `no_material_claims_reason`; support is then `not_applicable`,
  and coverage is still assessed. This declaration also requires semantic review.

Run:

```sh
poetry run python scripts/check_answer_review.py /private/path/packet.json /private/path/review.json
```

The command prints separate support, coverage and overall assessments per answer,
plus totals. It does not write files. Exit codes are `0` for all pass, `1` for any
failure, `2` for invalid input/evidence correspondence, and `3` for unresolved
uncertainty without a failure. A failure takes precedence in the overall result;
the separate axis and original findings retain uncertainties.

The code rejects duplicate JSON fields and checks the packet hash, exact answer/need ID coverage, nonempty reasons
and verbatim quotations. `validation: valid` means those checks passed;
`assessment` comes from the semantic reviewer. The checker cannot establish that
the needs are relevant, the claim inventory complete, or the judgments correct.
The full-answer acknowledgement is a reviewer declaration, not proof.

Test the reviewer with separately labelled calibration examples, including a
short sufficient answer, a true but nonresponsive answer, and an answer that
turns uncertainty into certainty despite quoting real text. Keep their expected
results outside the blind packet; report them separately from historical answers.
Preserve mistakes and disagreement. Do not repeatedly judge until a desired score
appears. Only actual same-condition answer improvements can justify a product
change; successful validation alone cannot.

This separation is informed by ALCE's [claim coverage](https://github.com/princeton-nlp/ALCE/blob/246c476a4edfc564266b7346b6e29ef4861ae937/eval.py#L282-L298)
and [citation support](https://github.com/princeton-nlp/ALCE/blob/246c476a4edfc564266b7346b6e29ef4861ae937/eval.py#L342-L427)
checks. We use the distinction, not its runtime or model dependencies.
