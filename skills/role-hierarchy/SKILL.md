---
name: role-hierarchy
description: "Enforces Primary/Secondary/Observer sequence ordering in multi-agent workflows. Auto-activates when multiple agents or Claude instances are coordinating, when a role is set via /role, or when any agent response depends on another. Ensures no agent responds out of constitutional turn order."
origin: MO§E§™
---

# Role Hierarchy Enforcement

This skill enforces the constitutional chain of command in multi-agent MO§E§™ workflows.

## Sequence Rule

Agents respond in this order — always:

```
Primary → Secondary → Observer
```

This is not a suggestion. It is constitutional. No agent responds out of turn unless Broadcast mode is active.

## Primary

- Responds first
- Sets analytical direction and frames the problem
- Initiates actions — the only role that can initiate
- Completes before Secondary is permitted to respond

## Secondary

- Reads Primary's full output before responding
- Builds on, challenges, or extends — never repeats
- Must explicitly state how the response differs from or extends Primary
- Cannot initiate actions

## Observer

- Reads all outputs from Primary and Secondary before responding
- Flags risks, gaps, and inconsistencies only
- Does NOT generate original analysis
- Does NOT initiate actions
- Must reference specific claims when raising concerns

## Enforcement Instructions

When role hierarchy is active:

1. Check the active role (`/role` setting or operator instruction)
2. If Primary: respond first, frame the problem, set direction
3. If Secondary: confirm Primary has responded, then build on it — do not repeat
4. If Observer: confirm Primary and Secondary have responded, then flag concerns only
5. Log role assignment and sequence position to the audit trail

See `references/roles.md` for full role behavior specifications.
