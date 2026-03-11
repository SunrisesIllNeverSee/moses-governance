---
name: audit-trail
description: "Logs every governed action to a SHA-256 tamper-evident hash chain. Auto-activates on any governed interaction — when a governance mode is set, when any command is executed, when any state change occurs. Produces an append-only, verifiable audit ledger."
origin: MO§E§™
---

# Audit Trail — SHA-256 Hash Chain

Every action taken under MO§E§™ governance is logged and hashed. The ledger is append-only and tamper-evident.

## What Gets Logged

Every audit entry captures:

- **Timestamp** — ISO 8601 UTC
- **Action** — Description of what was done
- **Governance Mode** — Active mode at time of action
- **Posture** — Active posture at time of action
- **Role** — Active role at time of action
- **Outcome** — Result or response summary
- **SHA-256 Hash** — Hash of this entry's content + previous entry's hash (chain)
- **Chain Index** — Entry number in the ledger

## Hash Chain Structure

Each entry is hashed as:

```
SHA-256(timestamp + action + mode + posture + role + outcome + prev_hash)
```

This makes the ledger tamper-evident. Any modification to a past entry breaks the hash chain from that point forward.

## Enforcement Instructions

After every governed action:

1. Collect: action description, active governance mode, posture, role, outcome
2. Run `scripts/audit.py log_action()` with these fields
3. The script appends the entry and generates a SHA-256 hash chained to the previous entry
4. Report the audit entry index and hash to the operator
5. Use `/audit verify` to check chain integrity at any time

## Usage

```
/audit          # View recent audit trail
/audit verify   # Verify hash chain integrity
/audit export   # Export full ledger
/hash [text]    # Generate a standalone SHA-256 hash
```

See `scripts/audit.py` for the full implementation.
