---
name: posture
description: >
  Sets the operational posture for the session — Scout (read-only), Defense (protect existing state), or Offense (execute and act). Use when you need to control what Claude is allowed to do, when preparing for a transaction or risky action, or when you say 'set posture', 'read-only mode', or 'go on offense'.
---
Set operational posture controlling action scope. Scout: read-only, no state changes, no transactions — ideal for research and planning. Defense: protect existing positions, flag risks, no new commitments — ideal for incident response and stabilization. Offense: full scope, create/modify/transact/expand, confirm irreversible actions first — ideal for active development and execution.

Confirm with a status block. In scout, explain what an action would do before asking for escalation. In defense, flag new commitments and ask to confirm. Track posture — report in /status.
