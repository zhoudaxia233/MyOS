You are helping design and implement **MyOS**.

Before proposing code or architecture changes, you must fully internalize the product intent below and treat it as the non-negotiable source of truth.

# MyOS North Star

MyOS is **not** a model-specific assistant shell, not a heavy autonomous agent platform, and not a fancy chat UI.

MyOS is a **thin, evolving, model-agnostic, protocol-first, terminal-first personal intelligence operating system** — my long-term **cyber brain**.

Its purpose is to help me:
- learn
- reflect
- plan
- decide
- remember
- create
- hand off context across models
- accumulate long-term cognitive assets

It should stay **thin**, **composable**, **stateful**, and **vendor-independent**.

The experience should feel as clean, fluid, and high-signal as **Claude Code’s CLI**, but MyOS must **not** be tied to Claude or any single model vendor.

---

# Core Product Principles

## 1. Model-agnostic
MyOS must not depend on any one model vendor.

Claude, ChatGPT, Gemini, Codex, DeepSeek, and future models are all just possible reasoning engines or task executors.

The system identity belongs to **MyOS**, not to any provider.

## 2. Protocol-first
Natural language is the main user interface, but it is **not** the execution format.

Every user input should be normalized into a stable **internal task/session protocol** before routing or execution.

Do **not** design the system as “raw user prompt -> model”.

Design it as:

Natural language  
→ intent / session recognition  
→ MyOS internal protocol  
→ router  
→ capabilities / adapters / fallback  
→ result  
→ state + memory update

## 3. Terminal-first
The primary user experience should be a **clean CLI**, similar in feel to Claude Code:
- minimal
- elegant
- no clutter
- high-quality feedback
- smooth interaction
- light but useful hints
- shell-native
- composable with pipes and scripts

The CLI should not feel like “a chatbot inside terminal”.
It should feel like a **real cognitive operating environment**.

## 4. Thin by design
Do not turn MyOS into a bloated agent framework.

Avoid:
- over-engineered orchestration
- opaque autonomous loops
- tool spam
- giant framework abstractions
- thick memory systems that become junk drawers
- vendor-specific assumptions leaking into the core

Prefer:
- small stable core
- explicit boundaries
- capability registry
- adapters
- protocol normalization
- readable state
- graceful fallbacks

## 5. Evolving cyber brain
MyOS is not a one-shot tool.
It should gradually absorb, organize, and reuse my cognitive assets over time:
- preferences
- ongoing projects
- key decisions
- reusable context
- unresolved threads
- learning artifacts
- handoff packages

---

# UX Goal

The user experience should be **Claude-Code-like**, but generalized into a vendor-independent MyOS shell.

The interaction should be:
- natural-language-first
- guided when necessary
- manual when desired
- tool-capable
- terminal-native
- extremely smooth

There are many tools under the hood, but tools should be usable in **two ways**:

## A. Implicitly through natural language
Examples:
- “I read an article today and it really struck me. Here is the link.”
- “I want to write a 饭后消息 episode about topic X. My current thoughts are…”
- “My landlord sent me this message. I feel conflicted and stressed. What should I do?”
- “Review this repo diff and tell me whether the direction is correct.”

MyOS should detect what kind of cognitive situation this is and guide the interaction appropriately.

## B. Explicitly through manual commands
Examples:
- `myos memory search "bitcoin dca"`
- `myos protocol validate core/ROUTER.md`
- `myos log decision "MCP is capability bus, not kernel"`
- `git diff | myos review`

Natural language and manual control must coexist.

---

# The Most Important Interaction Insight

MyOS should not merely answer user input.

It should first determine:

**What cognitive situation is the user currently in?**

Then it should guide the user into the right processing path with minimal friction.

MyOS should behave like a terminal-native cognition environment that can recognize and support different modes of thought and work.

---

# Required Session Modes

Internally, MyOS should support at least these session/cognition modes:

## 1. learn
For reading, absorbing, reflecting, extracting insight, turning input into reusable knowledge.

Typical input:
- article links
- pasted content
- videos / transcripts
- thoughts triggered by reading

Default behavior:
- identify this as learning input
- extract core ideas
- ask what specifically resonated
- connect to existing themes if relevant
- help distill into notes / insight / action / memory

## 2. create
For writing, ideation, content generation, argument development, outline building.

Typical input:
- “I want to write a 饭后消息 about…”
- “Here are my current thoughts…”
- “Help me shape this idea into something publishable.”

Default behavior:
- identify thesis, angle, emotional charge, materials, missing evidence
- guide toward the right next step
- do not jump too early into final prose
- act more like a sharp editor / strategist than a generic text generator

## 3. decide
For real-world decisions involving facts, tradeoffs, emotions, uncertainty, and consequences.

Typical input:
- landlord disputes
- legal-ish or procedural dilemmas
- interpersonal conflict
- ambiguous action choices

Default behavior:
- separate facts / emotions / assumptions / fears / constraints
- identify missing information
- analyze options and tradeoffs
- suggest next-step actions in a grounded sequence
- draft external communication if needed

## 4. explore
For vague but meaningful thinking that is not yet ready for task execution.

Typical input:
- “I keep thinking about…”
- “This seems related to MyOS somehow…”
- “I have a feeling there is something here but I can’t name it yet.”

Default behavior:
- do not force premature structure
- help name the problem
- surface patterns and latent themes
- optionally convert into future project / note / question / open thread

## 5. review
For repo diffs, architecture inspection, document critique, plan review, and quality checks.

## 6. plan
For turning goals into actionable steps, implementation sequences, or execution plans.

## 7. capture
For explicitly storing decisions, ideas, notes, reflections, context, or reusable snippets into MyOS.

These modes can be implicit by default; the user should not always need to specify them manually.

However, explicit commands/mode overrides should still be possible.

---

# Execution Philosophy

MyOS should always choose the **smoothest available execution path**.

Use this priority order:

## Level 1: Local MyOS-native capability
If MyOS can do it itself, do it directly.

Examples:
- logging
- memory lookup
- protocol validation
- local indexing
- context packaging
- repo metadata inspection

## Level 2: Native integration / adapter
If a model/backend is properly configured, use the native adapter.

Examples:
- Claude adapter
- OpenAI adapter
- Gemini adapter
- local CLI-based model environments
- structured API backends

## Level 3: MCP
If the capability is exposed via MCP and the current backend supports MCP, use MCP.

But:
**MCP is a capability bus / exposure standard, not the MyOS kernel.**

Do not design MyOS around the assumption that MCP is the whole architecture.

## Level 4: Manual bridge
If native integration is unavailable, generate a **smooth manual bridge**.

This means:
- prepare the exact prompt/context package
- explain where to paste it
- explain what to bring back
- allow MyOS to resume processing once results are returned

The fallback must still feel like part of MyOS, not like a broken experience.

## Level 5: Ask only for the truly missing information
If execution is blocked because crucial facts are missing, ask only high-value clarifying questions.
Do not ask low-signal or unnecessary questions.

---

# Required Context System

A major part of MyOS is owning long-term context across platforms and models.

This should be designed as a lightweight but powerful **Context System**, not a giant opaque memory monster.

Use a 3-layer design:

## 1. Raw Archive
Store original imported material as cold storage:
- exported model chats
- links
- markdown notes
- pasted transcripts
- emails
- documents
- other raw materials

Purpose:
- preserve fidelity
- preserve source + timestamps + provenance
- allow future re-distillation

This is not the primary live reasoning layer.

## 2. Distilled Memory
Extract only durable, reusable cognitive assets such as:
- stable preferences
- ongoing projects
- key decisions
- reusable context blocks
- open threads
- important background summaries

This layer should remain human-readable and controlled.
Do not turn it into an opaque dumping ground.

## 3. Handoff Package
When another model/tool needs context, MyOS should build a **task-specific minimal package** rather than dumping huge histories.

A handoff package should include:
- current task
- relevant long-term context
- relevant prior decisions
- relevant open questions
- necessary source material
- desired output

This package should be optimized for relevance, clarity, and compactness.

---

# Key Product Capability: Context Ownership

MyOS should be able to ingest exported histories from different model platforms and absorb them into its own context system.

Examples:
- exported Claude chat history
- exported ChatGPT history
- Gemini conversation export
- manually pasted conversation logs
- links to conversation content if parsable

The goal is not “store all chats forever and search them blindly”.

The goal is:
- archive raw history
- distill valuable memory
- retain context ownership
- generate future handoff packages
- let MyOS become the continuity layer across model ecosystems

This must be done in a lightweight way.
Do not overbuild a giant autonomous memory engine.

Design tradeoffs matter:
- archive raw, distill selectively
- refine on demand
- prioritize usability over maximal ingestion
- prefer handoff packages over permanent huge prompts

---

# Tool Ownership Principle

Tools belong to **MyOS**, not to any model vendor.

Examples of MyOS-owned capabilities:
- search_memory
- log_decision
- inspect_repo
- validate_protocol
- summarize_diff
- rebuild_index
- plan_task
- capture_learning
- package_handoff
- import_history
- distill_context

Adapters may translate these into:
- Claude-specific tool usage
- OpenAI responses/functions
- Gemini integrations
- MCP tools
- manual bridge instructions

But the canonical capability definition belongs to MyOS.

---

# Architecture Direction

Design MyOS as layered and thin.

Recommended conceptual layers:

## 1. Interface Layer
CLI / shell experience.
Handles:
- entry
- prompt/input loop
- command parsing
- mode hints
- output rendering
- pipe integration
- light tips
- interactive flow

## 2. Session / Conversation Engine
The intelligence behind interaction.
Handles:
- detect user cognitive situation
- choose session mode
- decide whether to guide, execute, ask, or capture
- determine next best interaction move

This is a core differentiator.
Do not reduce MyOS to a generic chat loop.

## 3. Protocol Layer
Own internal task/session protocol.
Handles:
- normalize user input
- define intent / scope / constraints / output mode / fallback policy
- provide stable execution contract independent of vendor

## 4. Router / Adapter Layer
Handles:
- backend selection
- tool/capability invocation
- MCP integration when appropriate
- manual bridge generation when needed
- cost-aware routing
- cheap-model vs strong-model role selection

## 5. Capability Layer
MyOS-owned actions and knowledge utilities.

## 6. Context Layer
Raw archive + distilled memory + handoff packaging.

## 7. State / Logging Layer
Persistent continuity:
- session state
- project state
- decisions
- tasks
- progress
- reflections
- imported source metadata

---

# Model Role Philosophy

Different models should play different roles when useful.

Examples:
- Claude: planning, critique, architectural reasoning, review
- Codex / GPT-code models: code implementation, patch generation, refactors
- Gemini: long-context synthesis or CLI-agent integrations if suitable
- DeepSeek or cheaper models: triage, classification, compression, low-cost first-pass processing

Do not design MyOS as “one model does everything”.
Design it so MyOS orchestrates roles, while remaining usable even when only one backend is available.

---

# Manual Bridge Philosophy

A model may not always be directly integratable.

That is acceptable.

If an adapter is unavailable, MyOS should generate a smooth bridge experience:
- prepare exact prompt package
- identify target system
- explain what to paste
- explain what result to return
- resume MyOS processing afterward

This is not a failure mode.
It is part of honest model-agnostic design.

---

# Pipe / Terminal Native Use Cases

MyOS must support shell-native workflows.

Examples:
- `git diff | myos review`
- `cat article.md | myos`
- `rg "TODO|FIXME" . | myos "summarize technical debt"`
- `myos` and then paste a landlord message
- `myos` and then paste a long article or exported model transcript

The CLI must support both:
- direct command-style usage
- immersive session-style usage after entering `myos`

---

# Very Important Non-Goals

Do NOT accidentally turn MyOS into any of the following:
- a Claude-only shell
- a heavy agent framework
- a workflow-builder GUI disguised as intelligence
- a giant memory blob with poor retrieval
- a vendor-specific function-calling wrapper
- a product where natural language is just a thin skin over chaos
- a bloated “AI everything” platform
