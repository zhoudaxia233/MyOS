# MyOS

**English** | [简体中文](README-zh.md)

**Correct your AI assistant once. After you approve, every assistant you use follows it.**

![A correction becomes a candidate, the second time the assistant asks, and after "adopt" both Claude Code and Codex get the rule](docs/demo.svg)

MyOS keeps the rules for how you want to be helped: your limits, how you
judge, how you like work done, and the habits you want pointed out.

- **You approve every rule.** A correction is saved with your own words and
  waits. It becomes a rule when you say so, never because an assistant guessed.
- **One place, every assistant.** Claude Code and Codex read the same rules,
  and a change reaches both.
- **It can push back.** A rule can describe a habit of yours, such as widening
  a project when it goes well. The assistant points it out instead of going
  along with it.
- **Judgment, not a chat log.** No transcripts, dates or to-dos: only what
  changes how an assistant should act for you.
- **Yours.** One private folder on your computer, with the history of every
  rule. Rules your assistant reads are handled by its model provider like the
  rest of your conversation.

## Install

You need Claude Code or Codex, and [uv](https://docs.astral.sh/uv/).

```sh
uv tool install git+https://github.com/zhoudaxia233/MyOS
myos setup          # shows what it would change
myos setup --yes    # makes the changes
```

Restart your assistant and say: *"Set up MyOS with me."* It goes through the
rules you already keep for it, proposes entries, and saves the ones you approve.

## What is shown, and what is not

Not shown: that answers get better for you. In one private run (55 questions,
one model, graded by another model), MyOS covered more of what its owner
wanted than the same rules in one plain file, and made more unsupported
claims. Earlier, smaller comparisons found no consistent advantage, and the
effort of keeping rules current is not measured. What MyOS gives you for
certain is control: approval, one source for every assistant, and history. See
the [exploration map](docs/exploration-map.md#e08--proving-usefulness-rather-than-successful-machinery).

## Read more

- [User guide](docs/getting-started.md): daily use, teaching it, what it
  refuses to store, and how it works.
- [Reference](docs/reference.md): commands, tools and manual setup.

Contributors: start with [AGENTS.md](AGENTS.md) and run
`poetry run pytest -q --strict-markers`.
