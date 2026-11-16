---
description: Set the active MO§ES™ governance mode using the shared, generation-checked state store.
argument-hint: [high-security|high-integrity|creative|research|self-growth|problem-solving|idk|unrestricted]
---

# /govern

Set the governance mode to "$ARGUMENTS".

If no argument provided, show the current active mode AND present a quick picker:

```
Current mode: [active mode or "none"]

Pick a mode:
  /govern high-security     — verify claims, confirm before destructive actions
  /govern high-integrity    — accuracy first, cite sources, flag uncertainty
  /govern creative          — explore freely, log reasoning shifts
  /govern research          — deep investigation, document methodology
  /govern problem-solving   — decompose, solve, verify
  /govern idk               — guided discovery, clarifying questions
  /govern unrestricted      — no constraints (still audited)
```

## Modes

- `high-security` — Verify all claims, require confirmation before destructive actions, log reasoning chain
- `high-integrity` — Accuracy above all, cite sources, flag uncertainty
- `creative` — Explore freely, log reasoning, flag when shifting to speculation
- `research` — Deep investigation, document methodology, track provenance
- `self-growth` — Reflective learning, track improvements, identify gaps
- `problem-solving` — Decompose before solving, verify solutions, document assumptions
- `idk` — Guided discovery, clarifying questions, propose next steps with tradeoffs
- `unrestricted` — No constraints, all actions still audited

## Usage

```
/govern high-security
/govern research
/govern creative
/govern                  # shows current mode
```

## Behavior

When invoked with a mode argument, execute these steps in order:

**Step 1 — Read the current state generation and hash:**
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/governance_store.py" status
```
Use the returned `generation` and `state_hash` for this write. If the write reports stale state, read status again and reassess.

**Step 2 — Persist the mode through the shared boundary:**
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/governance.py" set_state \
  --mode "$ARGUMENTS" \
  --expected-generation [GENERATION] \
  --expected-hash [STATE_HASH]
```

**Step 3 — Confirm to operator**:
```
✓ Governance mode set: [CANONICAL MODE NAME]
Active constraints: [list 2-3 key constraints]
The transition is recorded in the shared hash-chained history. Hook coverage applies only to supported host tool paths.
```

When invoked with no argument, run:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/governance_store.py" status
```
Display current mode + its active constraints.

Without a trusted operator identity provider, the shared policy boundary accepts only High Security as a mode change. Other mode changes require the operator-only identity setup described in the MCP README; a fresh generation/hash alone is not operator authorization.

See `references/modes.md` for full constraint definitions.
