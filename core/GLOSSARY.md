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
