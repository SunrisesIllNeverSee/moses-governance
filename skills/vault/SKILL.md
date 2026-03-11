---
name: vault
description: Manages the governance document vault — load, inject, and unload constitutional documents that are woven into every governed context.
---

# MO§ES™ Vault Skill

The vault is the document layer of constitutional governance. Loaded documents are injected into every governed context via `assemble_context()` — they are not optional attachments, they are constitutional inputs.

## Activation

This skill activates automatically when:
- `/vault load` is called
- A vault document is referenced in the session
- `govern_assemble_context()` is invoked (MCP v1.1)

## Document Categories

| Category | Purpose |
|----------|---------|
| `protocol` | Operational rules and procedures |
| `persona` | Role definition and behavioral constraints |
| `prompt` | Constitutional instructions for agent behavior |
| `personal` | Operator-specific preferences and context |
| `professional` | Domain expertise, role context, credentials |
| `business` | Org-level policies, compliance frameworks, SLAs |
| `general` | Catch-all for ungrouped governance documents |

## Behavior

**On `/vault load [name]`:**
1. Read the named document into the active vault
2. Set category (default: `general`)
3. Confirm load: `Vault: [name] loaded (category: [cat]). Vault count: N.`
4. Log to audit trail: `vault_load — [name]`

**On every governed action:**
- All vault documents are injected into the governed context payload under `vault_context`
- Documents are provided to Claude alongside `constitutional_governance` and `role_assignment`
- Vault content is treated as constitutional — it constrains behavior, not just informs it

**On `/vault list`:**
- Return all currently loaded documents with name and category
- If vault is empty: `Vault is empty. Use /vault load [name] to add governance documents.`

**On `/vault unload [name]`:**
- Remove named document from active vault
- Confirm: `Vault: [name] unloaded. Vault count: N.`
- Log to audit trail: `vault_unload — [name]`

## Integration with Governance Engine

The vault plugs directly into `assemble_context()` in `scripts/governance.py`:

```python
"vault_context": [
    {"name": doc["name"], "category": doc["category"], "content": doc["content"]}
    for doc in governance.vault_documents
]
```

Every document in the vault becomes part of the constitutional payload every agent receives. This is why vault documents must be governance-grade — they operate at the same authority level as the mode, posture, and role.

## Audit Logging

All vault operations are logged to the audit trail:
- `vault_load` — document name, category, timestamp, hash
- `vault_unload` — document name, timestamp
- `vault_clear` — count cleared, timestamp

## State Persistence

Vault contents are stored in `data/governance_state.json` under `vault_documents`. They persist across commands within a session and are restored on `SessionStart` via `session-start.sh`.

---

© 2026 Ello Cello LLC. Patent Pending: Serial No. 63/877,177
