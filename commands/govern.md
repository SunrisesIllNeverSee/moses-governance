---
description: Set the active MO§ES™ governance mode. Writes mode to state file so all hooks enforce it immediately.
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

**Step 1 — Persist the mode** (this wires enforcement — do not skip):
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/governance.py" set_state \
  --mode "$ARGUMENTS" \
  --state "${CLAUDE_PLUGIN_ROOT}/data/governance_state.json"
```

**Step 2 — Log to audit trail**:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/audit.py" log_action \
  --component "governance" \
  --action "mode_change" \
  --mode "$ARGUMENTS" \
  --ledger "${CLAUDE_PLUGIN_ROOT}/data/audit_ledger.jsonl"
```

**Step 3 — Confirm to operator**:
```
✓ Governance mode set: [CANONICAL MODE NAME]
Active constraints: [list 2-3 key constraints]
Hook enforcement active. All subsequent tool actions evaluated under this mode.
Audit entry logged.
```

When invoked with no argument, run:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/governance.py" translate_mode \
  "$(python3 -c "import json; print(json.load(open('${CLAUDE_PLUGIN_ROOT}/data/governance_state.json')).get('mode','None (Unrestricted)'))")"
```
Display current mode + its active constraints.

See `references/modes.md` for full constraint definitions.
