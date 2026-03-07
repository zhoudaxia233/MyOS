# Boundary Rules

This file defines operational classification rules across `memory`, `decision`, `profile`, `cognition`, and `principles`.

## Primary Routing Order

Apply these tests in order:

1. **Governing Test**
   - If the statement is cross-domain, long-horizon, and intended to resist routine override, route to `principles`.
2. **Commitment Test**
   - If it records a concrete choice, approval, rejection, gate outcome, or exception, route to `decision`.
3. **Schema Test**
   - If it records interpretation fit, contradiction, or schema revision lineage, route to `cognition`.
4. **Trait/Default Test**
   - If it represents a relatively stable owner trait/default/sensitivity, route to `profile`.
5. **Evidence Default**
   - Otherwise route to `memory`.

## Tie-Break Rules

- Governing beats local policy.
- Normative commitments beat descriptive observations.
- Interpretive structure changes beat preference labels.
- If still uncertain, store in `memory` with explicit uncertainty and `proposal_target` tag.

## Promotion Rules

### Memory -> Profile

Promote only when all are true:

- repeated evidence across multiple events
- persistence across time window
- owner confirmation

### Any Layer -> Principles

Promote only via amendment workflow:

- cross-domain applicability
- durable horizon
- explicit tradeoff and override cost
- owner ratification

### Cognition -> Other Layers

- Cognition outputs proposals, not direct writes.
- Apply `proposal -> approval -> target update`.

## Anti-Patterns (Disallowed)

- Writing constitutional constraints into `profile` defaults.
- Logging one-off events directly into profile baseline files.
- Storing schema revisions as memory insights.
- Encoding ad-hoc tactical rules as principles.
- Allowing retrieval results to mutate SSOT directly.

## Classification Tags (Recommended)

For new logs, include when applicable:

- `object_type`: `memory|decision|profile|cognition|principle`
- `proposal_target`: target layer for proposed promotion
- `approval_ref`: owner approval record ID for ratified changes
- `principle_refs`: principle clause IDs used for decision constraint checks
