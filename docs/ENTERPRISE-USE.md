# Enterprise Use — MO§ES™ Governance

## Why Enterprise Teams Need This

Every enterprise using Claude today has the same problem: no governance layer between operators and the model. Individual users set their own behavior expectations via prompting. There's no organizational standard, no audit trail, no enforced compliance.

MO§ES™ solves this at the framework level.

## Deployment Patterns

**Team-wide governance defaults:** Set `config.toml` with organizational defaults — High Integrity for research teams, High Security for finance teams, Problem Solving for engineering. Every team member starts with the right governance mode.

**Compliance mapping:** High Security mode's constraints map to SOC 2 control requirements. The audit trail provides evidence of governed AI operations. Session hashes provide cryptographic proof of what governance was active when.

**Multi-agent oversight:** Primary/Secondary/Observer hierarchy gives enterprise teams the same chain-of-command structure they use in human operations. Primary leads. Secondary validates. Observer oversees. Constitutional, not conversational.

**Vault-based policy injection:** Load organizational policies, compliance frameworks, and security protocols into the vault. They're injected into every governed interaction. Policy isn't a suggestion — it's constitutional context.

## Compliance Evidence

The audit trail generates compliance-ready evidence:

- What governance mode was active during any operation
- What posture controlled transaction policy
- What vault documents informed the interaction
- Cryptographic hash chain proving no records were modified
- Session integrity hashes for independent verification

## Security Posture — Current Limitations

**Amendment signing:** Constitutional amendments require HMAC-SHA256 signatures via `MOSES_OPERATOR_SECRET`. The secret is mandatory — no amendment proceeds without it. Current limitation: the signature verifies knowledge of the secret but does not bind to a specific operator identity. A valid signature generated for one proposal could be replayed against another. This is a known v2.0 item. Mitigation: store the secret in a secrets manager, rotate it after any suspected compromise, and treat the amendment ledger (`amendments.jsonl`) as an auditable record of what changed and when.

**Tool-use vs. conversational enforcement:** Technical enforcement (exit 2 blocking) fires on Bash, Write, and Edit tool calls. Conversational responses are governed by skill instructions. Enterprise deployments requiring hard interception of all model outputs should plan for v2.0 MCP-layer enforcement or combine MO§ES™ with network-level proxy controls.

**Oracle fail-open behavior:** When the Grok Oracle is unreachable (network error, rate limit, timeout), it returns `preserves_commitment: True` — governance proceeds, the Oracle gate is silently skipped. This is availability-over-security by design. If your threat model requires the Oracle gate to be hard-blocking, set `XAI_GROK_API_KEY` and implement a circuit breaker at the infrastructure layer.

## Scaling

Governance modes, postures, and roles are framework-level abstractions. They apply identically whether governing 1 agent or 100. Set governance once, apply everywhere.
