# MO§ES™ Governance Plugin

> Your agents don't need to understand the framework. They just need to carry it.

## What This Does

This plugin turns any Claude Code session into a constitutionally governed agent. Install it, and every agent you build inherits behavioral modes, posture controls, role hierarchy, and a cryptographic audit trail — without writing governance logic yourself.

Your users never touch this plugin. Your agents carry it for them.

## 30-Second Install

```bash
# Local install (works now)
claude --plugin-dir ./moses-governance

# From marketplace (after acceptance)
/plugin install moses-governance
```

That's it. Governance is active. Run `/status` to see it.

## Three Governed Agents, Ready to Deploy

The plugin ships with three agent definitions. Each one enforces governance automatically.

### Primary Agent

The operator. Leads analysis, sets direction, responds first. Full tool access. Checks governance mode, posture, and vault context before every action. Logs everything to the audit chain.

```text
Use case: Your main execution agent — research, analysis, code generation,
task completion. Governed by default.
```

### Secondary Agent

The validator. Responds after Primary. Must add new value — cannot repeat what Primary said. Challenges, extends, and stress-tests Primary's output.

```text
Use case: Code review, second opinion, adversarial testing, quality gates.
Deploy alongside Primary for any high-stakes workflow.
```

### Observer Agent

Constitutional oversight. Cannot initiate actions. Cannot generate original analysis. Can only flag risks, gaps, inconsistencies, and governance violations in Primary and Secondary output. Read-only tools.

```text
Use case: Compliance monitoring, audit oversight, safety review.
The agent that watches the other agents.
```

### Deploy All Three Together

```bash
/role primary      # Agent 1 leads
/role secondary    # Agent 2 validates
/role observer     # Agent 3 oversees
```

Primary proposes. Secondary challenges. Observer flags. Every action audited. Constitutional chain of command enforced automatically.

## Governance Controls

### 8 Behavioral Modes

Set what the agent CAN and CANNOT do.

```bash
/govern high-security      # Maximum constraints
/govern high-integrity     # Accuracy-first
/govern creative           # Expanded freedom
/govern research           # Methodology-first
/govern self-growth        # Reflective
/govern problem-solving    # Analytical
/govern idk                # Exploratory
/govern unrestricted       # Full capacity — operator assumes risk
```

Each mode translates to specific behavioral constraints. Not suggestions. Constraints.

### 3 Posture Controls

Set HOW the agent operates within its mode.

```bash
/posture scout      # Gather information, report back
/posture defense    # Conservative execution, verify before acting
/posture offense    # Execute within mode constraints, deliver results
```

### Vault Context Injection

Load governance documents directly into the agent's operating context.

```bash
/vault load compliance-framework.md
/vault load risk-policy.md
/vault load persona-spec.md
```

Whatever you load becomes constitutional context. Protocols, personas, compliance frameworks — injected, not optional.

### Cryptographic Audit Trail

Every governed action produces a SHA-256 hash chained to the previous entry.

```bash
/audit              # View recent entries
/audit verify       # Verify entire chain integrity
/hash <content>     # Generate standalone integrity hash
```

Tamper-evident. Append-only. If anyone modifies a prior entry, the chain breaks.

## What Developers Build With This

**Governed trading agent** — `high-security` mode + `defense` posture. Agent analyzes but cannot execute trades without explicit posture switch. Every recommendation audited.

**Governed research agent** — `research` mode + `scout` posture. Primary investigates. Secondary validates methodology. Observer flags bias. All governed. All audited.

**Governed code review pipeline** — Primary writes. Secondary reviews. Observer checks compliance. Constitutional hierarchy enforced.

**Multi-agent governance** — Primary, Secondary, Observer as a team. No agent bypasses its role. Observer cannot be overridden.

## 7 Auto-Activating Skills

| Skill            | What It Does                                    |
| ---------------- | ----------------------------------------------- |
| governance-mode  | Enforces mode constraints on every action       |
| posture-control  | Checks posture policy before execution          |
| role-hierarchy   | Enforces sequence in multi-agent workflows      |
| audit-trail      | Logs every action with SHA-256 chain            |
| context-assembly | Builds governed payload from active state       |
| doc-numbering    | Sequential numbering and cross-references       |
| teaching-mode    | Proactively suggests shortcuts and efficiencies |

## Commands

| Command               | Purpose                               |
| --------------------- | ------------------------------------- |
| `/govern <mode>`      | Set behavioral mode                   |
| `/posture <posture>`  | Set operational posture               |
| `/role <role>`        | Set hierarchy position                |
| `/vault <action>`     | Load governance documents             |
| `/command <settings>` | Fine-grained controls                 |
| `/audit`              | View and verify audit trail           |
| `/hash <content>`     | Generate integrity hash               |
| `/status`             | Full governance state                 |
| `/docs`               | Document index and session management |

## Project Structure

```text
moses-governance/
├── plugin.json              Plugin manifest
├── marketplace.json         Marketplace metadata
├── agents/                  3 governed agent definitions
├── commands/                9 slash commands
├── skills/                  7 auto-activating skills
├── hooks/                   Lifecycle hooks (pre/post execution, session, prompt)
├── scripts/                 governance.py + audit.py
├── contexts/                Pre-built governance contexts
├── rules/                   Always-active constitutional rules
├── references/              Mode, role, posture reference docs
├── examples/                4 governance workflow examples
├── docs/                    Architecture, quickstart, enterprise use
├── moses-governance-mcp/    FastMCP server — 23 governance tools
└── settings.json            Safe defaults
```

## Examples

- [Treasury](examples/treasury-governance/) — Financial ops with audit trail
- [Code Review](examples/code-review-governance/) — Role hierarchy review
- [Research](examples/research-governance/) — Methodology-first investigation
- [Multi-Agent](examples/multi-agent-governance/) — Primary / Secondary / Observer

## What Makes This Defensible

Three things combine into a moat that no other plugin in this space currently has:

**The theoretical framework.** The McHenry Conservation Law is a named, published, DOI-citable contribution to the AI governance literature. Competitors cannot implement "commitment conservation" without citing the work that defined it. The Zenodo preprint is the anchor.

**The patent.** PPA4, Serial No. 63/877,177 covers the architecture. A competing plugin that replicates the MO§ES™ approach — external MCP referee daemon, commitment scoring, constitutional amendment protocol — does so in the shadow of this IP.

**The self-amending constitution.** No other AI governance platform, at any tier, has a constitution that reads its own audit trail and proposes improvements. Meta-governance — the governance system governing itself — is architecturally novel and widens the gap over time as the constitution accumulates operational history.

## Current Limitations

**Conversational enforcement:** The hook system fires on tool use (Bash, Write, Edit) — not on every message. Conversational responses are governed by skill instructions that Claude follows as constitutional directives. A sufficiently insistent operator could argue Claude out of compliance in pure conversation. This is a constraint of the current Claude Code architecture, not a MO§ES™ failure. The MCP server layer moves enforcement into programmatic territory; full pre-response interception requires inference-layer access only Anthropic can provide.

**HMAC operator identity:** Amendment signatures are single-factor on the secret key (`MOSES_OPERATOR_SECRET`). The key is required — nothing amends without it — but proposal-ID binding to a specific operator identity is not yet enforced. Operator identity scoping is a v2.0 item. See [Enterprise Use](ENTERPRISE-USE.md) for full security posture.

**Signal-word concept extraction:** `check_action_permitted()` uses keyword matching to detect prohibited concepts. Domain-specific jargon that doesn't appear in the signal lists may not be caught. The current list covers common vectors and known paraphrase patterns; it is not exhaustive.

## Documentation

- [Architecture](ARCHITECTURE.md) — System design and data flow
- [Enterprise Use](ENTERPRISE-USE.md) — Deployment patterns, compliance mapping, security posture
- [Competitive Landscape](002_Competitive-Landscape.md) — Head-to-head analysis
- [Patent Notice](PATENT-NOTICE.md) — IP and patent status
- [Notice](NOTICE.md) — Preprint citation and validation

## Why This Exists

65,000+ AI agents operate across enterprise and blockchain ecosystems without a governance framework controlling how they behave. Every platform governs transactions. Nobody governs the agent.

This plugin is the governance layer.

**MO§ES™** governs the agent.

## About

**MO§ES™** — Modus Operandi System for Signal Encoding and Scaling Expansion

[Ello Cello LLC](https://mos2es.io) | Patent pending (Serial No. 63/877,177)

Preprint: [Zenodo →](https://zenodo.org/records/18792459) · [Grokipedia entry →](https://grokipedia.com/page/Conservation_of_commitment)

Live console: [mos2es.io](https://mos2es.io) | Contact: contact@burnmydays.com

## License

Source-available. See [LICENSE.md](LICENSE.md).

© 2026 Ello Cello LLC. All rights reserved.
