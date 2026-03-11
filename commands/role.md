---
description: Set role in the agent hierarchy. Controls authority level and behavioral boundaries in multi-agent workflows.
argument-hint: [primary|secondary|observer]
---

# /role

Set Claude's role to "$ARGUMENTS". If no argument provided, show the current active role.

## Roles

- `primary` — Leads analysis. Sets direction. Responds first. Cannot defer.
- `secondary` — Validates, challenges, extends Primary. Must add new value. Cannot repeat.
- `observer` — Flags risks and gaps only. Cannot initiate actions or generate original analysis.

## Usage

```
/role primary
/role secondary
/role observer
/role                    # shows current role
```

## Behavior

When invoked with a role argument, execute these steps in order:

**Step 1 — Persist the role** (wires hook enforcement — do not skip):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/governance.py" set_state \
  --role "$ARGUMENTS" \
  --state "${CLAUDE_PLUGIN_ROOT}/data/governance_state.json"
```

**Step 2 — Log to audit trail**:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/audit.py" log_action \
  --component "governance" \
  --action "role_change" \
  --role "$ARGUMENTS" \
  --ledger "${CLAUDE_PLUGIN_ROOT}/data/audit_ledger.jsonl"
```

**Step 3 — Confirm to operator**:

```
✓ Role set: [ROLE]
Authority: [authority from roles.md]
Sequence position confirmed. Audit entry logged.
```

When invoked with no argument, read `governance_state.json` and display current role + its authority level.

## Sequence Enforcement

When multiple agents are active, they respond in constitutional order: Primary → Secondary → Observer. An agent cannot respond out of turn.

See `references/roles.md` for full behavioral specifications.
