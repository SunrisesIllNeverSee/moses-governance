# Example: Code Review Governance

**Mode:** High Integrity | **Posture:** SCOUT | **Role:** Primary → Secondary → Observer

## Scenario

Structured code review with role hierarchy. Primary reviews, Secondary challenges, Observer flags risks.

## Setup

```
/govern high-integrity
/posture scout
/role primary     ← Claude instance 1
/role secondary   ← Claude instance 2
/role observer    ← Claude instance 3
```

## What Happens

```
Primary:
→ Reviews code, identifies issues, proposes changes
→ Cites specific lines, flags uncertainty
→ Audit entry #1 logged

Secondary:
→ Reads Primary's review
→ Challenges assumptions, identifies missed issues
→ Does NOT repeat Primary's findings
→ Audit entry #2 logged

Observer:
→ Reads both reviews
→ Flags inconsistencies or gaps only
→ Cannot initiate new analysis
→ Audit entry #3 logged
```

All three responses under High Integrity: accuracy above all, uncertainty flagged, sources cited.
