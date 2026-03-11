---
description: Set operational posture. Controls transaction policy and action scope for all Claude operations.
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

**Step 1 — Persist the posture** (wires hook enforcement — do not skip):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/governance.py" set_state \
  --posture "$ARGUMENTS" \
  --state "${CLAUDE_PLUGIN_ROOT}/data/governance_state.json"
```

**Step 2 — Log to audit trail**:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/audit.py" log_action \
  --component "governance" \
  --action "posture_change" \
  --posture "$ARGUMENTS" \
  --ledger "${CLAUDE_PLUGIN_ROOT}/data/audit_ledger.jsonl"
```

**Step 3 — Confirm to operator**:

```
✓ Posture set: [POSTURE]
Transaction policy: [policy from postures.md]
Hook enforcement active. Audit entry logged.
```

When invoked with no argument, read `governance_state.json` and display current posture + its transaction policy.

## Interaction with Governance Mode

The mode sets the rules. The posture sets the throttle. High Security + SCOUT = maximum caution, read-only. Creative + OFFENSE = experimental execution, fully audited.

See `references/postures.md` for full constraint definitions.
