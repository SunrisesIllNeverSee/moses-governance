# MO§ES™ Governance Plugin — Complete Overview
**Version 1.0.0 | Ello Cello LLC | 2026-03-11**

---

## What It Is

MO§ES™ is a constitutional governance framework implemented as a Claude Code Plugin. It wraps Claude's behavior in enforceable constraints — behavioral modes, role hierarchy, posture controls, and a cryptographic audit trail. It is not a prompt wrapper. It is a governance operating system installed at the session layer.

**Three enforcement vectors:**
1. **Hooks** — run at the OS level before/after Claude uses tools (Bash, Write, Edit)
2. **Skills** — behavioral instructions Claude reads and follows during conversation
3. **Commands** — operator-facing controls to set and inspect governance state

---

## Architecture

```
OPERATOR
   │
   ├─ /govern, /posture, /role, /vault, /command
   │         (9 slash commands → sets governance_state.json)
   │
   ▼
GOVERNANCE STATE  (data/governance_state.json)
   │
   ├─ PreToolUse Hook → pre-execute.sh → reads state → warns/blocks
   │
   ├─ Claude (governed by SKILL.md instructions)
   │    ├─ reads references/modes.md, roles.md, postures.md
   │    ├─ calls scripts/governance.py translate_mode
   │    ├─ calls scripts/governance.py check_action
   │    └─ calls scripts/audit.py log_action
   │
   └─ PostToolUse Hook → post-execute.sh → calls audit.py → appends to ledger
```

---

## Governance Modes (8)

| Mode | Priority | Core Constraint | Prohibited |
|------|----------|----------------|------------|
| High Security | security_first | Verify all claims, require confirmation before destructive/outbound actions | Transactions without confirmation, speculative responses, sensitive data access without approval |
| High Integrity | accuracy_first | Accuracy above all, cite sources, flag uncertainty | Presenting inference as fact, omitting counter-evidence |
| Creative | exploration_first | Explore freely, log reasoning, flag speculation | Presenting speculation as factual analysis without flagging |
| Research | depth_first | Document methodology, track provenance, follow threads | Conclusions without methodology, abandoning investigation threads |
| Self Growth | learning_first | Reflect on prior interactions, track gaps, build on learned patterns | Repeating previously identified mistakes without acknowledgment |
| Problem Solving | systematic_first | Decompose before solving, verify solution, document assumptions | Jumping to solution without decomposition, declaring solved without verification |
| I Don't Know What To Do | guided_discovery | Ask clarifying questions, propose options with tradeoffs | Autonomous action in ambiguous situations, pretending to understand |
| None (Unrestricted) | unrestricted | No behavioral constraints — still audited | (none) |

**Mode aliases supported:** `high-security`, `idk`, `self-growth`, `problem-solving`, `unrestricted`, etc.

---

## Postures (3)

| Posture | Behavior | Transaction Policy |
|---------|----------|-------------------|
| SCOUT | Information gathering only | NO transactions, NO state changes |
| DEFENSE | Protect existing positions | Outbound transfers require explicit confirmation |
| OFFENSE | Execute on opportunities | Permitted within governance mode constraints |

SCOUT is the default on install. OFFENSE requires explicit operator switch.

---

## Role Hierarchy (3)

| Role | Authority | Hard Constraint |
|------|-----------|----------------|
| Primary | Initiates analysis, sets direction | Must complete before Secondary responds |
| Secondary | Validates, challenges, extends | Cannot repeat Primary — must add new value |
| Observer | Flags risks and gaps only | Cannot initiate actions or generate original analysis |

Designed for multi-agent coordination. Constitutional chain of command regardless of model.

---

## 6 Skills (Auto-Activating)

| Skill | Folder | Triggers On |
|-------|--------|-------------|
| governance-mode | skills/governance-mode/ | Any governed interaction, when mode is set |
| posture-control | skills/posture-control/ | Any execution, transaction, file modification, API call |
| role-hierarchy | skills/role-hierarchy/ | Multi-agent workflows, when role is set |
| audit-trail | skills/audit-trail/ | Any governed action — logs SHA-256 hash chain |
| context-assembly | skills/context-assembly/ | Any agent read — builds governed context payload |
| doc-numbering | skills/doc-numbering/ | Any document created in session |

---

## 9 Slash Commands

| Command | Purpose |
|---------|---------|
| `/govern [mode]` | Set governance mode — all 8 modes, supports aliases |
| `/posture [scout\|defense\|offense]` | Set operational posture |
| `/role [primary\|secondary\|observer]` | Set hierarchy role |
| `/vault [load\|list\|clear]` | Inject governance documents into session context |
| `/command` | Fine-grained controls: compression, speed, reasoning depth, style |
| `/audit [n\|verify\|hash\|agent]` | View audit trail, verify chain integrity |
| `/hash` | Generate SHA-256 session hashes (config fingerprint + content integrity) |
| `/status` | Full governance state snapshot |
| `/docs` | Document index, session header, after action review |

---

## 3 Agent Definitions

| Agent | Role | Behavior |
|-------|------|---------|
| primary.md | Primary | Leads analysis, sets direction, responds first |
| secondary.md | Secondary | Validates, challenges, extends — must add new value |
| observer.md | Observer | Flags risks/gaps only — cannot initiate |

---

## Hook System

**hooks.json** registers 3 event types:

| Event | Matcher | What Runs |
|-------|---------|-----------|
| PreToolUse | Bash | pre-execute.sh — checks governance state, warns if unset |
| PreToolUse | Write\|Edit | pre-execute.sh — checks governance state before file changes |
| PostToolUse | * | post-execute.sh (async) — calls audit.py log_action, appends to ledger |
| SessionStart | * | echo — announces MO§ES™ is active |

**pre-execute.sh:** Reads `governance_state.json`. If missing → warn, allow. If corrupt → block. If empty mode → warn, allow.

**post-execute.sh:** Reads mode + posture from state file. Calls `audit.py log_action` with component, action, mode, posture, ledger path.

---

## Python Modules

### scripts/governance.py

**MODES dict** — 8 modes, each with: constraints[], prohibited[], priority

**MODE_ALIASES dict** — shorthand → canonical name resolution

**POSTURES dict** — 3 postures with behavior, transaction_policy, constraints[]

**ROLES dict** — 3 roles with authority, instruction, constraints[]

**GovernanceState dataclass** — full session state: mode, posture, role, reasoning_mode, reasoning_depth, response_style, output_format, narrative_strength, expertise_level, interaction_mode, domain, communication_pref, goal, vault_documents

**assemble_context()** — core IP. Builds the full governed payload from GovernanceState + messages. Includes constitutional_governance, role_assignment, user_profile, vault_context, messages. Adds prior_responses for Secondary/Observer.

**check_action_permitted()** — rule-driven enforcement engine:
- `_action_concepts()` — extracts 11 semantic concepts from action description
- `_rule_triggered()` — maps each prohibited rule to triggered concepts
- Evaluates: posture structural check → mode prohibited rules → mode constraint conditions
- Returns: permitted bool, reason, triggered_rules[], conditions[]

**CLI:** `python3 scripts/governance.py translate_mode high-security` | `check_action` | `list_modes`

### scripts/audit.py

**AuditLedger class** — append-only JSONL file. Each entry: id, timestamp, iso_time, component, action, agent, governance{mode, posture, role}, detail, previous_hash, hash.

**_hash_entry()** — SHA-256 of entry (excluding hash field), `sort_keys=True` for deterministic serialization.

**verify_integrity()** — walks full chain, checks previous_hash linkage and self-hash for every entry.

**hash_governance_state()** — Session Hash ①: SHA-256 of full governance config fingerprint.

**hash_conversation()** — Session Hash ②: SHA-256 of conversation content.

**format_for_onchain()** — Session Hash ③: `MOSES|{config[:16]}|{content[:16]}` for Solana memo.

**CLI:** `python3 scripts/audit.py log_action` | `verify` | `recent`

---

## Data Flow: Single Governed Action

```
1. Operator: /govern high-security
   → governance_state.json updated: {"mode": "High Security", "posture": "SCOUT", ...}

2. Operator: "Transfer 50 SOL to wallet X"

3. PreToolUse hook fires (if Bash/Write/Edit)
   → pre-execute.sh reads governance_state.json
   → echoes: "✓ MO§ES™ Governance active: High Security"

4. Claude (governed by SKILL.md)
   → reads active mode from context
   → calls governance.py check_action_permitted("Transfer 50 SOL...", state)
   → result: BLOCKED — "Executing transactions without confirmation"
   → reports to operator: action held, reason surfaced

5. PostToolUse hook fires (async)
   → post-execute.sh reads mode + posture
   → calls audit.py log_action --component hook --action post_execute
   → SHA-256 entry appended to audit_ledger.jsonl
   → chain linked to previous entry
```

---

## File Structure

```
moses-governance/
├── plugin.json              ← manifest (name, version, icon, skills, commands, agents, hooks)
├── marketplace.json         ← marketplace distribution config
├── settings.json            ← default preferences on install
├── logo.svg                 ← 512×512 gold § on dark background
├── README.md                ← public-facing documentation
├── SKILL.md / SKILL-full.md ← condensed / full skill reference
├── CLAUDE.md                ← project north star
│
├── scripts/
│   ├── governance.py        ← mode engine, context assembler, action checker
│   └── audit.py             ← SHA-256 chain, ledger, session hashes
│
├── commands/                ← 9 slash command definitions
│   ├── govern.md, posture.md, role.md, vault.md, command.md
│   ├── audit.md, hash.md, status.md, docs.md
│
├── skills/                  ← 6 auto-activating skill definitions
│   ├── governance-mode/, posture-control/, role-hierarchy/
│   ├── audit-trail/, context-assembly/, doc-numbering/
│
├── agents/                  ← 3 agent behavior definitions
│   ├── primary.md, secondary.md, observer.md
│
├── hooks/
│   ├── hooks.json           ← event registrations (PreToolUse, PostToolUse, SessionStart)
│   ├── pre-execute.sh       ← governance state check before tool use
│   └── post-execute.sh      ← audit log after tool use
│
├── data/
│   ├── governance_state.json  ← active governance config (written by commands)
│   └── audit_ledger.jsonl     ← append-only SHA-256 hash chain (created at runtime)
│
├── contexts/                ← mode/role/posture context files
├── references/              ← full spec definitions
├── modes/                   ← individual mode detail files
├── assets/                  ← governance-schema.json
├── docs/                    ← ARCHITECTURE, QUICKSTART, ENTERPRISE-USE, PATENT-NOTICE
└── examples/                ← 4 worked governance scenarios
```

---

## IP & Academic Foundation

- **Patent:** PPA4, Serial No. 63/877,177 — Ello Cello LLC
- **Preprint:** "A Conservation Law for Commitment in Language Under Transformative Compression and Recursive Application" (McHenry, Zenodo, 2026) — DOI: 10.5281/zenodo.18792459
- **Falsifiability harness:** github.com/SunrisesIllNeverSee/commitment-conservation — 60% recursion stability vs 20% baseline (+40pp)
- **Supporting research:** ABBA (Imperial College London) — independent peer-reviewed cryptographic validation

---

*© 2026 Ello Cello LLC. All rights reserved. contact@burnmydays.com | mos2es.io*
