---
description: Set role metadata through the shared, generation-checked state store.
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

First run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/governance_store.py" status` and use the returned generation and state hash for this write. If the store reports a stale snapshot, read status again and reassess.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/governance.py" set_state \
  --role "$ARGUMENTS" \
  --expected-generation [GENERATION] \
  --expected-hash [STATE_HASH]
```

**Step 3 — Confirm to operator**:

```
✓ Role set: [ROLE]
Authority: [authority from roles.md]
The transition is recorded in the shared history. Role values are policy metadata, not host-enforced identity.
```

When invoked with no argument, run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/governance_store.py" status` and display the current role + its configured behavior.

Without a trusted operator identity provider, role promotions are rejected. Configure an operator-only identity provider before changing to a more authoritative role.

## Sequence Enforcement

When multiple agents are active, they respond in constitutional order: Primary → Secondary → Observer. An agent cannot respond out of turn.

See `references/roles.md` for full behavioral specifications.
