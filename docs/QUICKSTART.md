# Quickstart — MO§ES™ Governance in 5 Minutes

## Install

```
/plugin install moses-governance@claude-plugin-directory
```

## Set Governance

```
/govern high-security
```

Claude now operates under High Security constraints. Every action is verified. Every claim requires evidence. Destructive operations require confirmation.

## Set Posture

```
/posture scout
```

Claude is now read-only. No transactions, no file modifications, no state changes. Gather and analyze only.

## Check Status

```
/status
```

See your full governance state: mode, posture, role, vault, audit count.

## Do Work

Ask Claude to do anything. The governance skill automatically enforces your mode and posture constraints. If Claude tries to do something prohibited, it will explain why and suggest alternatives.

## Check Audit

```
/audit
```

Every governed action has been logged with SHA-256 hashes. Full tamper-evident trail.

## Change as Needed

```
/govern research
/posture offense
/role primary
/command depth deep
```

Governance is real-time. Change modes mid-session. The audit trail tracks every change.

## MCP Server Setup (Constitutional Amendment Layer)

The MCP server powers the self-amending constitution, commitment conservation, and Grok Oracle. It starts automatically when the plugin is installed. One optional env var unlocks cryptographically signed amendments:

```bash
export MOSES_OPERATOR_SECRET="your-secret-key-here"
```

Without it: amendment signatures are advisory (plain string, warned).
With it: amendments require HMAC-SHA256 — nothing amends the constitution without the key.

Generate a signature for any amendment proposal:

```text
/govern → then use meta_generate_sig tool in Claude Code MCP panel
```

## Learn More

- `/govern` — 8 governance modes
- `/posture` — 3 operational postures
- `/role` — 3 hierarchy roles
- `/vault` — governance document injection
- `/command` — fine-grained operational controls
- `/hash` — session integrity verification
- `/audit` — full audit trail
- `/status` — complete state snapshot
