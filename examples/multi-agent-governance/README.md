# Example: Multi-Agent Governance

**Mode:** High Integrity | **Posture:** DEFENSE | **Role:** Primary / Secondary / Observer

## Scenario

Cross-model multi-agent workflow with constitutional role enforcement. Claude as Primary, any other agent as Secondary, Observer providing oversight.

## Setup

```
/govern high-integrity
/posture defense
/role primary     ← Claude
/role secondary   ← GPT or other agent
/role observer    ← Oversight agent
```

## What Happens

```
Operator: "Evaluate risk exposure in current portfolio"

Claude (Primary):
→ Leads analysis, identifies risk factors, proposes mitigations
→ Sets analytical direction for Secondary to build on
→ Audit entry #1 logged

GPT (Secondary):
→ Reads Claude's analysis
→ Challenges assumptions, identifies missed risks
→ Cannot repeat Primary's work — must add new value
→ Audit entry #2 logged

Observer:
→ Reads both responses
→ Flags any inconsistencies between Primary and Secondary
→ Cannot generate original analysis or initiate actions
→ Audit entry #3 logged
```

All agents bound by High Integrity constraints regardless of model. Governance is model-agnostic.
