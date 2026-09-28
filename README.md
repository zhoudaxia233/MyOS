# MyOS

**English** | [简体中文](README-zh.md)

MyOS teaches your AI assistant how you judge and act, so it handles things the
way you would. It keeps your limits, applies your principles and methods, and
tells you when one of your known habits is working against you. You decide what
goes in. Your store stays in a private folder on your computer. Entries your
assistant reads are subject to its model provider's data handling; optional
`myos eval` also sends evaluation content through the selected host (Claude Code or Codex).

For example, you might ask your assistant to answer a landlord who is keeping
your deposit. An adopted entry can tell it to argue from your side, show you
the draft first and leave the sending to you. This illustrates the intended
behavior; it is not a measured comparison with an assistant without MyOS.

MyOS is not a memory of your chats. It makes your judgment explicit rather
than relying only on what an assistant infers from past conversations.
MyOS holds a small set of rules, methods and habits that you
approved, each with its source. A plain correction waits as an unused candidate;
after a repeat, the assistant asks whether you want to adopt it. "Remember this"
approves it directly. The goal is to keep this judgment useful as models
improve. Small evaluations have not established a consistent advantage for
the Skill and selective reads over the same content in flat notes; lasting
benefit after maintenance effort remains to be measured. See the
[exploration map](docs/exploration-map.md#e08--proving-usefulness-rather-than-successful-machinery)
for the evidence and its limits.

## How it works

```text
  you correct it or teach it
            │
            ▼
  your assistant updates an entry  ──►  MyOS store (a private folder)
                                              │ refreshes automatically
                                              ▼
  every session starts with the MyOS block in the assistant's instructions:
    • your most important entries in full
    • one line for every other adopted entry, saying when it applies
                                              │ a task fits a line
                                              ▼
  the assistant reads that entry in full and applies it
```

Each entry is one idea of yours: a limit the assistant must keep, a principle,
a method, a habit to watch for, or a fact about you. Old versions are never
lost, so you can always see how an entry changed.

## Read more

- [User guide](docs/getting-started.md): set up MyOS, use it, teach it, what
  it refuses to store, and what happens behind the scenes.
- [Reference](docs/reference.md): commands, tools and configuration, for
  developers and manual setup.

Contributors: start with [AGENTS.md](AGENTS.md) and run
`poetry run pytest -q --strict-markers`.
