---
description: Load governance documents into active context. Documents are injected into all subsequent Claude interactions.
argument-hint: [list|load name|unload name|active]
---

# /vault

Manage vault documents. Action: "$ARGUMENTS". If empty, show currently loaded documents.

## Usage

```
/vault list                        # show available documents by category
/vault load security-protocol      # load a document into active context
/vault unload security-protocol    # remove from active context
/vault active                      # show currently loaded documents
```

## Document Categories

- **Protocol** — Operational rules, compliance frameworks, security procedures
- **Persona** — Behavioral voice, character, communication style
- **Prompt** — Pre-built query templates, analysis frameworks
- **Personal** — Individual preferences and context
- **Professional** — Role-specific workflows and standards
- **Business** — Organizational policies, brand guidelines, domain knowledge

## Behavior

**On `/vault load [name]`:**

Determine if the argument is a file path or a document name. Then:

1. Load document into state file (persists to disk for hook layer):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/governance.py" vault_load "[NAME]" \
  --category "[CATEGORY]" \
  --file "[PATH_IF_FILE]" \
  --state "${CLAUDE_PLUGIN_ROOT}/data/governance_state.json"
```

If the argument is inline content rather than a file path, use `--content "[CONTENT]"` instead of `--file`.

2. Log to audit trail:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/audit.py" log_action \
  --component "vault" \
  --action "vault_load" \
  --detail "{\"name\": \"[NAME]\", \"category\": \"[CATEGORY]\"}" \
  --ledger "${CLAUDE_PLUGIN_ROOT}/data/audit_ledger.jsonl"
```

3. Confirm: `✓ Vault: [name] loaded (category: [cat]). Vault count: N. Audit entry logged.`

**On `/vault unload [name]`:**

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/governance.py" vault_unload "[NAME]" \
  --state "${CLAUDE_PLUGIN_ROOT}/data/governance_state.json"
```

Then log and confirm: `✓ Vault: [name] unloaded. Vault count: N.`

**On `/vault list` or `/vault active`:**

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/governance.py" vault_list \
  --state "${CLAUDE_PLUGIN_ROOT}/data/governance_state.json"
```

Loaded vault documents are injected into every governed context. They are constitutional inputs — not optional attachments.
