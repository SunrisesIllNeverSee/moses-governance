# MO§ES™ Governance — Constitutional Control for Claude

> Every AI agent operates without constraints. No behavioral rules. No audit trail. No chain of command. MO§ES™ changes that.

**MO§ES™** is a constitutional governance framework that gives operators enforceable control over how Claude behaves. Not prompting. Not filtering. Constitutional governance — with modes, hierarchy, postures, and cryptographic audit trails.

**Patent pending.** Serial No. 63/877,177. [Preprint →](https://zenodo.org/records/18792459) · [Falsifiability harness →](https://github.com/SunrisesIllNeverSee/commitment-conservation) · [COMMAND demo →](https://mos2es.io)

## Install

```bash
# From the official marketplace (after acceptance)
/plugin install moses-governance@claude-plugin-directory

# From the MO§ES™ marketplace directly
/plugin marketplace add sunrisesillneversee/moses-governance

# Or test locally during development
claude --plugin-dir ./moses-governance
```

## Quick Start

```
/govern high-security     # Set behavioral constraints
/posture defense          # Set transaction policy
/role primary             # Set hierarchy position
/status                   # See full governance state
/audit                    # View audit trail
```

## Enforcement Architecture

**Tool-use layer (v1.0):** Every Bash command, file write, and file edit is evaluated against the active governance mode before execution — prohibited actions are blocked with exit code 2. Every user prompt injects the active governance context. Every response and tool action is logged to the cryptographic audit trail. Conversational responses are governed by skill instructions, which Claude follows as constitutional directives.

**MCP server layer (v1.1, shipped):** A standalone FastMCP server exposes 23 governance tools — mode/posture/role control, vault management, cryptographic audit, commitment conservation scoring, Grok Oracle verification, agent swarm coordination, and a self-amending living constitution with HMAC-signed amendments. Starts automatically on plugin install. Both layers share `governance_state.json` — state is consistent across hooks and MCP tools.

## What You Get

**8 Governance Modes** — High Security, High Integrity, Creative, Research, Self Growth, Problem Solving, IDK, Unrestricted. Each translates to specific behavioral constraints Claude must follow.

**3 Posture Controls** — SCOUT (read-only), DEFENSE (protect assets), OFFENSE (execute within constraints). Real-time throttle on agent authority.

**3 Role Hierarchy** — Primary (leads), Secondary (validates), Observer (oversees). Constitutional chain of command for multi-agent workflows.

**Cryptographic Audit Trail** — Every governed action SHA-256 hashed. Each entry chains to the previous. Tamper-evident. Append-only. Verifiable with `/audit verify`.

**Vault Context Injection** — Load governance documents (protocols, personas, compliance frameworks) into every interaction. Context isn't optional — it's constitutional.

**COMMAND Bar** — Fine-grained controls: compression, speed, reasoning depth, reasoning mode, response style, output format, narrative strength.

## 9 Slash Commands

| Command | What it does |
|---------|-------------|
| `/govern` | Set governance mode |
| `/posture` | Set operational posture |
| `/role` | Set hierarchy role |
| `/vault` | Load governance documents |
| `/command` | Fine-grained operational controls |
| `/audit` | View audit trail |
| `/hash` | Generate integrity hashes |
| `/status` | Full governance state snapshot |
| `/docs` | Document index, session header, after action review |

## 6 Auto-Activating Skills

Skills are namespaced under the plugin name. When installed, they appear as:

- **moses-governance:governance-mode** — Enforces active mode on every action
- **moses-governance:posture-control** — Checks transaction policy before execution
- **moses-governance:role-hierarchy** — Enforces sequence ordering in multi-agent
- **moses-governance:audit-trail** — Logs everything with SHA-256 hash chain
- **moses-governance:context-assembly** — Builds governed payload from all active state
- **moses-governance:doc-numbering** — Sequential numbering, timestamps, topic tags, and cross-references on every document created

## 3 Agent Definitions

- **Primary** — Leads analysis, sets direction, responds first
- **Secondary** — Validates, challenges, extends. Must add new value.
- **Observer** — Flags risks and gaps. Cannot initiate. Constitutional oversight.

## Examples

- [Treasury Governance](examples/treasury-governance/) — Governed financial operations
- [Code Review Governance](examples/code-review-governance/) — Structured review with role hierarchy
- [Research Governance](examples/research-governance/) — Methodology-first investigation
- [Multi-Agent Governance](examples/multi-agent-governance/) — Primary/Secondary/Observer workflow

## Current Limitations

**Conversational enforcement:** The hook system fires on tool use (Bash, Write, Edit) — not on every message. Conversational responses are governed by skill instructions that Claude follows as constitutional directives. A sufficiently insistent operator could argue Claude out of compliance in pure conversation. This is a constraint of the current Claude Code architecture, not a MO§ES™ failure. The MCP server layer moves enforcement into programmatic territory; full pre-response interception requires inference-layer access only Anthropic can provide.

**HMAC operator identity:** Amendment signatures are single-factor on the secret key (`MOSES_OPERATOR_SECRET`). The key is required — nothing amends without it — but proposal-ID binding to a specific operator identity is not yet enforced. A valid signature for one proposal could technically be replayed on another. Operator identity scoping is a v2.0 item. See [Enterprise Use](ENTERPRISE-USE.md) for full security posture.

**Signal-word concept extraction:** `check_action_permitted()` uses keyword matching to detect prohibited concepts. Domain-specific jargon (financial, legal, technical) that doesn't appear in the signal lists may not be caught. The current list covers common vectors and known paraphrase patterns; it is not exhaustive.

These limitations are documented, bounded, and tracked. The self-stress-testing in `Stresstesting/STRESS-TEST-CONCERNS.md` covers every known gap with severity ratings and fix paths.

## Documentation

- [Architecture](ARCHITECTURE.md) — System design and data flow
- [Patent Notice](PATENT-NOTICE.md) — IP and patent status
- [Notice](NOTICE.md) — Preprint citation and validation

## Why This Exists

Every other Claude skill teaches Claude a workflow. This one changes how Claude *operates*. The governance modes aren't prompts — they're behavioral constraint systems backed by patent filings and mathematical formalism.

GitLab governs code. Harvey governs legal. Snowflake governs data. **COMMAND governs Claude.**

## About

**MO§ES™** (Modus Operandi System for Signal Encoding and Scaling Expansion) is developed by [Ello Cello LLC](https://mos2es.io). Patent pending. [Preprint →](https://zenodo.org/records/18792459) · [Falsifiability harness →](https://github.com/SunrisesIllNeverSee/commitment-conservation) — empirically validated: 60% recursion stability vs 20% baseline (+40pp).

**COMMAND** is the visual governance console for MO§ES™. [Live at mos2es.io →](https://mos2es.io)

Contact: contact@burnmydays.com

## License

Source-available. See [LICENSE.md](LICENSE.md).

© 2026 Ello Cello LLC. All rights reserved.
