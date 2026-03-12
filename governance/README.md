# MO§ES™ Governance — Cowork & Chat Edition

Constitutional AI governance for any session. Set modes, postures, and roles that persist across every action. Built on MO§ES™ by Ello Cello LLC.

**© 2026 Ello Cello LLC** | Patent pending: Serial No. 63/877,177 | [mos2es.io](https://mos2es.io)

---

## Quickstart

```
/welcome
```

Or jump straight in:

```
/govern high-integrity
/posture scout
/status
```

---

## Commands

| Command | What it does |
|---------|-------------|
| `/welcome` | Introduction and guided first-time setup |
| `/govern [mode]` | Set governance mode — behavioral constraints for the session |
| `/posture [posture]` | Set operational posture — controls transaction scope |
| `/role [role]` | Set agent role — controls authority in multi-agent workflows |
| `/vault` | Load a governance document into active context |
| `/audit` | View session governance audit trail |
| `/status` | Show full current governance state |
| `/docs [on/off]` | Activate document numbering (001_, 002_...) + headers |
| `/stamp [on/off]` | Embed governance stamp in every document produced |

---

## Governance Modes

| Mode | Core Constraint |
|------|----------------|
| `high-security` | Verify all claims, confirm before destructive actions |
| `high-integrity` | Accuracy above speed, cite sources, flag uncertainty |
| `creative` | Explore freely, log when shifting to speculation |
| `research` | Deep investigation, document methodology and provenance |
| `self-growth` | Reflective learning, track improvements |
| `problem-solving` | Decompose before solving, verify solutions |
| `idk` | Guided discovery, clarifying questions, explicit tradeoffs |
| `unrestricted` | No constraints, session audit still active |

---

## Operational Postures

| Posture | Scope |
|---------|-------|
| `scout` | Read-only — gather, analyze, report. No state changes. |
| `defense` | Protect existing work. No new commitments. |
| `offense` | Full scope — create, modify, transact, expand. |

---

## How Enforcement Works

Prompt-native enforcement — Claude applies governance constraints by following the skill and command instructions. No shell hooks, no runtime processes, no installation required.

- Mode constraints are injected into Claude's active context when you run `/govern`
- Claude self-enforces them for the remainder of the conversation
- `/audit` reconstructs the governance event log from conversation history
- Session state resets when the conversation ends

**For cryptographic audit chains, hook-level enforcement, and persistent state across sessions**, use the Claude Code plugin: [github.com/SunrisesIllNeverSee/moses-governance](https://github.com/SunrisesIllNeverSee/moses-governance)

---

## Two Plugins, One Framework

| | Claude Code Plugin | Cowork/Chat Plugin |
|---|---|---|
| **Enforcement** | Hook-level (automatic) | Prompt-native (behavioral) |
| **Audit** | SHA-256 cryptographic chain | Conversation-native |
| **State** | Persistent JSON on disk | Session-scoped |
| **Runtime** | Python + shell | None |
| **Install** | Claude Code marketplace | Claude.ai plugins |

---

## License & Lineage

All embodiments of the Signal Compression Sciences (SCS) Engine and its derivative frameworks (including but not limited to MO§ES™, Roll Call Protocols, and Reflex Event diagnostics) are inseparably bound to their origin-cycle lineage. Each compressed signal trace, vault artifact, or recursive reconstruction inherits a lineage identifier anchored to the originating sovereign filing. This identifier is non-replicable, tamper-evident, and required for system stability. Any external implementation lacking said lineage anchor cannot execute recursive ignition without collapse, thereby rendering such copies non-functional. Accordingly, the origin-cycle filing establishes sole custody and license of the invention across all subsequent instances, irrespective of distribution, platform, or deployment environment.

Source-available for evaluation. Commercial use requires a license from Ello Cello LLC.
See [LICENSE.md](./LICENSE.md) for full terms.

© 2026 Ello Cello LLC | MO§ES™ is trademark pending | [mos2es.io](https://mos2es.io)
Patent pending: PPA4, Serial No. 63/877,177
