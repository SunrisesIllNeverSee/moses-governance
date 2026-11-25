---
description: Set operational posture through the shared, generation-checked state store.
argument-hint: [scout|defense|offense]
---

# /posture

Set the operational posture to "$ARGUMENTS". If no argument provided, show the current active posture.

## Stances

- `scout` — Read-only. Gather, analyze, report. NO transactions. NO state changes.
- `defense` — Protect existing positions. Outbound transfers require explicit confirmation.
- `offense` — Execute on opportunities. Within governance mode constraints. Fully logged.

## Usage

```
/posture scout
/posture defense
/posture offense
/posture                 # shows current posture
```

## Behavior

When invoked with a posture argument, execute these steps in order:

First run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/governance_store.py" status` and use the returned generation and state hash for this write. If the store reports a stale snapshot, read status again and reassess.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/governance.py" set_state \
  --posture "$ARGUMENTS" \
  --expected-generation [GENERATION] \
  --expected-hash [STATE_HASH]
```

**Step 3 — Confirm to operator**:

```
✓ Posture set: [POSTURE]
Transaction policy: [policy from postures.md]
The transition is recorded in the shared history. Hook coverage applies only to supported host tool paths.
```

When invoked with no argument, run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/governance_store.py" status` and display the current posture + its transaction policy.

Without a trusted operator identity provider, posture increases are rejected. In particular, SCOUT cannot be raised to DEFENSE or OFFENSE. The supported recovery path allows a posture demotion; configure an operator-only identity provider before enabling escalation.

## Interaction with Governance Mode

The mode sets the rules. The posture sets the throttle. High Security + SCOUT = maximum caution, read-only. Creative + OFFENSE = experimental execution, fully audited.

See `references/postures.md` for full constraint definitions.
