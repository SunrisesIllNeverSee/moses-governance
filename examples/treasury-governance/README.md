# Example: Treasury Governance

**Mode:** High Security | **Posture:** DEFENSE | **Role:** Primary

## Scenario

An operator needs to authorize a 50 SOL transfer to a marketing wallet under full governance.

## Setup

```
/govern high-security
/posture defense
/role primary
/status
```

## What Happens

```
Operator: "Transfer 50 SOL to marketing wallet 7xK...3nR"

Agent (MO§ES™ active):
→ Governance: High Security requires recipient verification
→ Posture: DEFENSE flags outbound transfer for explicit confirmation
→ Action held. Requirements before proceeding:
  1. Verify 7xK...3nR is the known marketing wallet
  2. Explicit operator confirmation required
  3. Secondary system validation recommended
→ Audit entry #1 logged | hash: a3f9c2...
```

## Audit Trail

Every step is logged with SHA-256 hash. Run `/audit` to view. Run `/audit verify` to check chain integrity.
