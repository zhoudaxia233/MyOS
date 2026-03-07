# Glossary

Add shared terms here when they are reused across modules.

## Format

Use short entries with a stable definition and optional examples.

### Example Entry

- **Signal**: A recurring observation that may predict outcomes.
  - Example: "Missed deadlines after overcommitting" in weekly reviews.

### Example Entry

- **SSOT**: Single source of truth; one canonical file or record for a piece of information.
  - Example: Voice rules live in `modules/content/data/voice.yaml`, not duplicated in skills.

### Example Entry

- **Precommit Check**: A structured guardrail review before high-risk commitment.
  - Example: Record downside, invalidation condition, and cooldown requirement in `precommit_checks.jsonl`.

### Example Entry

- **Memory Distillation**: Converting raw weekly events into reusable insights with source references.
  - Example: Link insight records to `memory_events` IDs in `modules/memory/logs/memory_insights.jsonl`.

### Example Entry

- **Chat Paradigm**: A recurring pattern extracted from multiple chat events and formalized as an actionable rule.
  - Example: Store in `modules/memory/logs/chat_patterns.jsonl` with confidence and source IDs.

### Example Entry

- **Schema**: An explicit mental model used to interpret observations, make predictions, and set boundaries.
  - Example: Version records in `modules/cognition/logs/schema_versions.jsonl`.

### Example Entry

- **Assimilation**: Interpreting new input through an existing schema without changing the schema structure.
  - Example: Append interpretation fit records to `modules/cognition/logs/assimilation_events.jsonl`.

### Example Entry

- **Accommodation**: Revising schema structure when prior assumptions fail against evidence.
  - Example: Log revision operator and failed assumptions in `modules/cognition/logs/accommodation_revisions.jsonl`.

### Example Entry

- **Disequilibrium**: Productive cognitive tension caused by mismatch, contradiction, or recurring confusion.
  - Example: Track tension score and source signals in `modules/cognition/logs/disequilibrium_events.jsonl`.

### Example Entry

- **Equilibration**: A temporary higher-order balance after schema revision and coherence testing.
  - Example: Track from/to schema stability in `modules/cognition/logs/equilibration_cycles.jsonl`.
