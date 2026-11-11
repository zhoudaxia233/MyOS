# MyOS user guide

[中文](getting-started-zh.md) · [Overview](../README.md)

This guide covers setup, daily use, teaching MyOS, and how it works. Commands
and configuration details are in the [reference](reference.md).

## Set up

You need Claude Code or Codex, and [uv](https://docs.astral.sh/uv/).

1. Install MyOS and connect it:

   ```sh
   uv tool install git+https://github.com/zhoudaxia233/MyOS
   myos setup          # shows what it would change
   myos setup --yes    # makes the changes
   ```

   Setup adds the MyOS Skill and tools to each assistant it finds, and a MyOS
   block to the instructions that assistant reads at the start of every
   session. The rest of your instruction file stays as it is, and a backup is
   kept. To do it by hand, follow
   [Connect an assistant](reference.md#connect-an-assistant).

2. Restart your assistant and say: *"Set up MyOS with me."* It asks which of
   your existing rules to look at, such as your `CLAUDE.md`, proposes entries
   from them, and asks a few questions if there is little to go on. You answer
   each proposal: adopt, adopt with edits, keep for later, or skip. Nothing is
   saved before you answer.

3. Check it: in a new session, ask *"What does MyOS say about how I want
   messages to other people handled?"* The answer should come from your entries.

## Use it

Work with your assistant as usual; there is nothing to run. MyOS changes how
the assistant judges, not what it knows. The examples below are what entries
ask the assistant to do; it can still miss an entry or apply one where it does
not fit (see the
[exploration map](exploration-map.md#e08--proving-usefulness-rather-than-successful-machinery)):

- Asked to write to someone you are in a dispute with, it takes your side and
  shows you the draft before anything goes out.
- Stuck on a problem, it offers the approach your methods suggest next to the
  obvious one.
- When you start widening a project's scope, it points out that this is a
  habit of yours.

An entry applies only where it fits, so an unrelated coding question should be
unaffected. What you say in the moment always wins over a stored entry.
MyOS itself cannot send, pay or post anything, and your assistant's own
approval rules still apply.

## Teach it

MyOS learns only from you, in three ways:

| You say | What happens |
| --- | --- |
| A correction: *"For weekend plans, show me the quiet option first."* | If it passes the checks below, saved as a **candidate**, with your words and their source. Just a one-line note, saying how many candidates now wait; no question. If you later make the same kind of correction, it asks at the end of its answer whether to adopt it. |
| *"Remember this"* or *"From now on…"* | Saved as **adopted**: followed from then on. Your words are the approval; it does not ask again. |
| Something to learn from, such as an article, your notes or a past decision, plus what you agree with: *"Read this; points 2 and 3 are how I think."* | It keeps only what changes how you judge, one idea per entry, with the source. Saved as a **candidate** unless you endorse it; say *"go through my candidates"* when you want to decide. |

### What gets in

MyOS stores judgment, not memory. Before saving anything, the assistant checks
four things, and all four must hold:

1. **It changes a future decision.** It alters what the assistant would do or
   advise in a kind of situation you can name. *"Push back when a company
   blames me for its own system's error"* passes; *"I called the insurer
   today"* does not.
2. **It lasts.** Events, conversation summaries, the status of a task,
   deadlines and facts that go stale stay out.
3. **It is yours.** A good assistant would not do it anyway. *"Be polite"* is
   everyone's default; *"in a dispute, argue from my side"* is yours.
4. **It is new.** If an entry already covers the idea, the assistant improves
   that entry, for example with an exception or an example, instead of adding
   another.

Anything that fails is not saved, and the assistant tells you where it belongs
instead:

| This | Belongs in |
| --- | --- |
| What happened, what you discussed | Your assistant's own memory or chat history |
| Open matters, dates, to-dos | Your notes or task list |
| How a project works | That project's own instruction file |
| Documents, secrets, passwords | Where they are now; MyOS keeps at most the lesson and a link |

So *"remember that my flight leaves at 9"* goes to the assistant's memory,
while *"remember: I'd rather take a later flight than a tight connection"*
goes into MyOS.

### Candidates and adoption

A candidate never influences answers: it stays out of your assistant's
instructions until you adopt it. It keeps your words so a later session can
spot a repeat. To keep an idea for later on purpose, say *"save this as a
candidate"*. Each time a candidate is saved or decided, the one-line note says
how many still wait, if any.

A candidate comes up for a decision in two ways:

- **You correct the same thing again.** The assistant shows your quotes with
  dates and the proposed wording, then offers **adopt / adopt with edits /
  one-off**.
- **You say *"go through my candidates"*.** It lists them by number, each with
  your words, the proposed wording, and whether an existing entry already
  covers it. Answer by number: adopt, adopt with edits, one-off, or keep waiting.

Your reply is the whole approval step: adopt makes it a rule (with your edits
if supplied); one-off retires the candidate. No answer leaves it a candidate,
with no second question that session. A retired idea that comes up again
starts as a new candidate. You can also say *"drop the entry about X"*; its
history stays.

### Boundaries and core

Two kinds of change need your explicit word, because every future session
sees them: **boundaries**, the limits the assistant must keep, and **core**
entries, the ten or fewer shown in full everywhere. Say *"make this a
boundary"* or *"make this core"*. Adopting a candidate never creates or
changes either.

When an adopted entry changes, your assistant's instructions refresh by
themselves, and new sessions see the change.

## See what it holds

- Ask your assistant: *"What's in MyOS about how I handle disputes?"* or
  *"List my boundaries."*
- For the whole picture, run `poetry run myos view` in the `MyOS` folder and
  open the page it names. Entries are grouped by kind with the core first;
  each one opens to its text, examples, sources and history.

## Keep it lean

Models get better, and some of your entries become things a good assistant
does anyway. Now and then, for example after a new model comes out, ask your
assistant to *"run the MyOS eval"*. It answers your own test questions three
times: without MyOS, with your entries as one plain notes file, and with MyOS.
Another model compares the answers without knowing which is which. For each entry you get a verdict:
still helps, the model already does this, hurts, or not tested. Nothing
changes until you say so: retire what the model already does, fix what hurts.

Your test questions stay in your MyOS folder, next to your entries. A correction
to a real answer adds a question when you adopt the entry: the request, and
what you wanted instead. Candidates do not add test questions.

## How it works

### Entries

Your self-model is a set of short entries. Each holds one idea, the situations
it applies to, its limits, one or two examples and where it came from. Its
kind tells the assistant how to use it:

| Kind | What it is | How the assistant uses it |
| --- | --- | --- |
| Boundary | A limit on what it does for you | Always keeps it. A boundary can stop an action; it never permits one. |
| Principle | How you judge and act | Follows it by default. |
| Method | How you handle a recurring kind of task | Uses it for that kind of task. |
| Pattern | A habit of yours | Points it out when it works against you; never follows it as a rule. |
| Context | Facts and preferences about you | Takes them into account. |

When entries pull in different directions, what you say now comes first, then
boundaries, then principles and methods (the more specific one wins), then
patterns.

Only **adopted** entries act as rules. **Candidate** entries are read only when
handling a correction to spot a repeat, or when you ask to go through them,
never to answer a request. **Uncertain**
entries are weighed as suggestions, and **reference** entries count as evidence.
**Inactive** entries are kept in the view and history, outside the catalog.

### Always loaded, or read when needed

An assistant follows a short instruction file better than a long one, and both
Codex and Claude Code recommend keeping it short. So MyOS writes a compact
block into the file the assistant reads at the start of every session
(`~/.codex/AGENTS.md` and `~/.claude/CLAUDE.md`):

- your **core** entries in full;
- one line for every other adopted entry, saying when it applies.

When a task matches a line, the assistant opens that entry in full. Candidates
and other unadopted entries stay out of the block.

### Learning

A plain correction becomes a candidate; an adopted entry stays unchanged while
its proposed refinement is saved separately, naming the entry it would revise.
The assistant follows the correction for this task; when the candidate comes
up for a decision, it proposes the adopted entry's revised wording. Your approval updates that entry and retires
the separate candidate. "Remember this" still adopts directly. The block contains
only adopted entries and refreshes when they change. Nothing is overwritten:
every earlier version is kept together with the request that changed it, so you
can see how an entry evolved and go back.

### Your data

Your store and local outputs live in a private folder on your computer
(`~/.local/share/myos` by default). Keep it outside the code checkout. Core
storage operations do not call a model; entries your assistant reads reach its
configured model provider like the rest of your conversation.

Optional `myos eval` launches Claude Code to generate and review answers. Case
prompts, source excerpts, answers and self-model context can reach the configured
model service. Review the selected case content before running it.

### What MyOS leaves to the assistant

MyOS does not record your chats, act on your behalf, or run a model of its
own. Your assistant does the understanding and reasoning; MyOS supplies the
judgment it should apply. The goal is for that judgment to remain useful as
models improve. Whether this adds value over the same content in one
plain file, after the effort of keeping it current, is not settled: one
model-graded run favored MyOS, earlier ones did not.
