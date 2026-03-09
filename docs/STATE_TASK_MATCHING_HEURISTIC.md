# Lightweight State-Task Matching Heuristic (Yerkes-Dodson)

## 1) Purpose

This is a lightweight orchestration heuristic, not a standalone psychology subsystem.

Primary intent:

- Improve task allocation under real cognitive conditions.
- Reduce bad recommendations caused by state-task mismatch.
- Avoid defaulting to "add pressure" when progress is low.

Explicitly out of scope:

- no heavy trait tracking module
- no pseudo-precise arousal scoring
- no therapy framing
- no manual journaling burden

## 2) Architectural Placement

This belongs inside orchestration and decision preflight paths:

- `orchestrator/src/planner.py`:
  - attach a coarse `task_cognitive_profile` to each planned task.
- `orchestrator/src/main.py` and `orchestrator/src/webapp.py` (`inspect` / `run`):
  - evaluate state-task fit before execution recommendation.
- `orchestrator/src/scheduling.py`:
  - use fit signal to reorder/shape cadence tasks when mismatch is obvious.
- `orchestrator/src/decision_gate.py`:
  - add deferral recommendation for major irreversible decisions under high activation.

Do not create a new top-level module under `modules/`.

## 3) Minimal Internal Data Model

Use coarse buckets only.

### 3.1 Current State Hint

```yaml
state_hint:
  state_bucket: low_activation | stable_activation | high_activation | unknown
  source: explicit_checkin | user_text_inference | behavioral_signal
  signals: [string]     # short tags, max 3
  observed_at: iso8601
  ttl_minutes: 90
```

Notes:

- `signals` examples: `hard_to_start`, `rapid_task_switching`, `agitated_language`, `sleepy`.
- If state is stale (`ttl_minutes` exceeded), fallback to `unknown`.

### 3.2 Task Cognitive Profile

```yaml
task_cognitive_profile:
  reasoning_load: low | medium | high
  execution_mode: convergent | mixed | exploratory
  reversibility: reversible | mixed | hard_to_reverse
  activation_fit: low_to_medium | medium | medium_to_high
```

Examples:

- inbox/admin/cleanup -> `low`, `convergent`, `reversible`, `medium_to_high`
- light coding/simple debug -> `medium`, `convergent`, `reversible`, `medium_to_high`
- architecture/deep writing/research/major strategy -> `high`, `exploratory`, `hard_to_reverse`, `medium`

### 3.3 Match Output

```yaml
state_task_match:
  fit: good | caution | mismatch
  recommended_mode: proceed | warmup_then_proceed | switch_lower_load | defer_major_judgment
  rationale_tags: [string]    # e.g. high_activation_with_high_reasoning_load
  suggested_next_actions: [string]
```

Optional audit log (only when non-`good`):

- `orchestrator/logs/state_task_matches.jsonl`

## 4) Rule Engine (Simple, Readable, Extendable)

### Core rules

1. If `state_bucket = high_activation` and `reasoning_load = high`:
   - default `mismatch`
   - suggest `switch_lower_load` first
   - if `reversibility = hard_to_reverse`, suggest `defer_major_judgment`

2. If `state_bucket = low_activation` and `reasoning_load in {medium, high}`:
   - default `caution`
   - suggest `warmup_then_proceed` with short starter tasks

3. If `state_bucket = stable_activation`:
   - allow `high` reasoning by default (`proceed`)

4. If repeated stalls on same high-load task:
   - prefer `state_task_mismatch` hypothesis before "insufficient effort"
   - branch into:
     - activation needed
     - down-regulation needed
     - task-class switch needed

### Pseudocode

```text
if state is unknown:
  ask short check-in or use conservative plan (medium/low load first)
elif high_activation and task.reasoning_load == high:
  if task.reversibility == hard_to_reverse:
    recommend defer_major_judgment
  else:
    recommend switch_lower_load
elif low_activation and task.reasoning_load in {medium, high}:
  recommend warmup_then_proceed
else:
  recommend proceed
```

## 5) User-Facing Behavior (Neutral Operator Tone)

Use operational language, not moralizing language.

Preferred phrasing:

- "Current state may not be ideal for deep reasoning."
- "Switching to a lower-load task may improve throughput first."
- "Major judgment can be deferred until cognition is more stable."
- "A short warm-up task may reduce start friction."

Avoid:

- personality judgment
- therapeutic labeling
- blame framing ("not disciplined enough")

## 6) Integration Behaviors

### 6.1 Task Routing / Planning

- Keep existing module routing unchanged.
- Add `task_cognitive_profile` after route/skill selection as a planning annotation.

### 6.2 Work Mode Switching

- If mismatch detected:
  - suggest lower-load/convergent mode
  - allow one-click switch to execution-oriented routine
- If fit is good:
  - preserve deep-work plan

### 6.3 Energy / Focus Management

- Optional quick check-in:
  - "state now: low / stable / high"
- No mandatory periodic survey.

### 6.4 Decision Deferral Hygiene

- For high-activation + hard-to-reverse decisions:
  - default to defer recommendation, not forced hard block
  - encourage reversible tasks and capture notes first

### 6.5 Reflective Check-Ins

- Trigger only when:
  - repeated stall on high-load task
  - repeated context switching
  - repeated failed deep-work attempts
- Keep to one short prompt.

## 7) Anti-Overengineering Constraints

- Keep to 3-4 state buckets and 3 task load levels.
- No continuous physiological metric model.
- No dashboard-first implementation.
- No extra module-level SSOT expansion unless later proven necessary.
- Prefer explicit rules over opaque scoring.

## 8) Success Criteria

- Fewer poor-fit deep-work recommendations under overload.
- Better recovery path when under-activated.
- Fewer high-stakes decisions encouraged in agitated state.
- Reduced self-blame language in recommendation output.
