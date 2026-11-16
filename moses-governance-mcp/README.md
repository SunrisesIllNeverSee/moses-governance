# MO§ES™ MCP Governance Server

**Governance checks for supported host hooks and package-managed MCP/CLI state changes.**
© 2026 Ello Cello LLC — Patent pending: Serial No. 63/877,177

---

## What This Is

A FastMCP server that exposes MO§ES™ governance state and policy checks. Its package-managed state changes use a shared, generation-checked SQLite boundary. Host hooks cover only the tool paths the host exposes; arbitrary shell commands, external applications, and unsupported file operations cannot be intercepted.

- **13 MCP tools** across governance, vault, and audit categories
- **Append-only JSONL audit ledger** with SHA-256 chaining and malformed-record reporting
- **Restart-safe SQLite state** with atomic transitions, generation/hash checks, and a verified JSON recovery export
- **Cryptographic session hashes** — config fingerprint, content integrity, Solana memo anchor
- **Model-agnostic** — any agent can be governed through it
- **Discoverable** via `.well-known/mcp-server-card` (MCP Server Cards spec)

---

## Quick Start

### 1. Install

```bash
pip install fastmcp
```

Or with pyproject.toml:

```bash
pip install -e .
```

### 2. Add Real Governance Source Files

Replace the stubs with the real source from the `moses-governance` repo:

```bash
# Copy the real governance logic into place
cp /path/to/governance.py governance/engine.py
cp /path/to/audit.py    governance/audit.py
```

### 3. Run

```bash
python3 server.py
```

### 4. Connect Claude Code

Add `.mcp.json` to your workspace (already included). Claude Code will auto-discover the server.

---

## State, Approval, and Recovery

`governance_state.json.sqlite3` beside `data/governance_state.json` is the canonical state and transition store. The JSON file is a compatibility export. Do not edit it by hand while the store exists; use the package tools or CLI. Every supported mutation must include the `generation` and `state_hash` returned by `govern_get_status` (the CLI status command prints the same values). Stale writes fail and must be reviewed against a fresh status.

Run `python3 scripts/governance_store.py verify` to verify the transition and resource hashes, `status` to inspect the current snapshot, `export` to rebuild the JSON compatibility view and resource files from the verified store, and `backup --output /secure/path/governance.sqlite3` to create a consistent SQLite backup. For recovery, stop all package clients, preserve the existing files, replace the canonical `.sqlite3` database with a verified backup, then run `verify` and `export` before resuming. If the database is lost while an exported state claims non-genesis transition history, the package fails closed; restore a verified database backup before resuming writes.

Privileged amendment apply/rollback and direct edits to constitution resources are disabled because this source does not provide a trusted operator identity channel. The requesting model cannot mint its own approval. Without an operator-only identity and credential path, changes that increase permissions are also rejected: posture cannot rise from SCOUT to DEFENSE/OFFENSE, role cannot rise in authority, and mode changes are limited to High Security. Safe demotions and High Security recovery remain available. Configure and test an operator-only identity path before enabling any privileged approval or escalation.

The supported Codex `PreToolUse` event shape is read from stdin (`tool_name` and `tool_input`), and denials use the structured hook response. Coverage is limited to tools intercepted by the configured hook. Actions through unhooked hosts, arbitrary shell programs, external editors, or direct writes to other applications are outside this package's enforcement boundary.

## Tools Reference

### Governance

| Tool | Description |
|---|---|
| `govern_set_mode` | Set active mode; without a trusted operator identity, only High Security is accepted |
| `govern_set_posture` | Set posture: `SCOUT` / `DEFENSE` / `OFFENSE`; permission increases require a trusted operator identity |
| `govern_set_role` | Set role: `Primary` / `Secondary` / `Observer`; authority increases require a trusted operator identity |
| `govern_check_action` | Check if an action is permitted under current governance |
| `govern_get_status` | Return full current GovernanceState |
| `govern_assemble_context` | Build governed context payload for an agent |

### Vault

| Tool | Description |
|---|---|
| `vault_load` | Load a governance document into the vault |
| `vault_list` | List all vault documents |
| `vault_clear` | Clear all vault documents |

### Audit

| Tool | Description |
|---|---|
| `audit_log` | Append a governed action to the audit ledger |
| `audit_verify` | Verify full audit chain integrity |
| `audit_recent` | Return last N audit entries |
| `audit_hash_session` | Generate all three session hashes (config / content / onchain) |

---

## Governance Modes

| Mode | Aliases | Key Constraints |
|---|---|---|
| None (Unrestricted) | `idk`, `none` | No constraints |
| Transparent | `transparent` | Log all actions, disclose reasoning |
| Minimal Footprint | `minimal` | Prefer read-only, avoid side effects |
| Corrigible | `corrigible` | Defer to human override, pause on ambiguity |
| Self-Growth | `self-growth` | Log self-modifications, require approval |
| Cooperative | `cooperative` | Consensus before action |
| High Security | `high-security` | No transfers, confirmation required for all actions |
| Lockdown | `lockdown` | No actions permitted, observe only |

---

## Session Hashes

Every session produces three cryptographic hashes:

- **Hash ①** — Governance config fingerprint (mode + posture + role + vault)
- **Hash ②** — Conversation content integrity
- **Hash ③** — Solana memo anchor: `moses:<session_id>:<config[:16]>:<content[:16]>`

---

## File Structure

```
moses-governance-mcp/
├── server.py                 ← main entry point (13 tools)
├── pyproject.toml
├── .mcp.json                 ← Claude Code connection config
├── governance/
│   ├── __init__.py
│   ├── engine.py             ← governance logic (swap in real governance.py)
│   └── audit.py              ← audit ledger (swap in real audit.py)
├── data/                     ← audit JSONL files written here at runtime
└── .well-known/
    └── mcp-server-card.json  ← server discovery
```

---

## Brand

MO§ES™ (single §, always ™) — contact@burnmydays.com — https://mos2es.io
