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

1. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/governance_store.py" status` to read the current generation and state hash. Use those exact values for the write; if stale, read status again and reassess.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/governance.py" vault_load "[NAME]" \
  --category "[CATEGORY]" \
  --file "[PATH_IF_FILE]" \
  --expected-generation [GENERATION] \
  --expected-hash [STATE_HASH]
```

If the argument is inline content rather than a file path, use `--content "[CONTENT]"` instead of `--file`.

2. Confirm the returned generation, state hash, and vault count. The committed transition is recorded in the shared history.

**On `/vault unload [name]`:**

First read the current generation and state hash with `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/governance_store.py" status`.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/governance.py" vault_unload "[NAME]" \
  --expected-generation [GENERATION] \
  --expected-hash [STATE_HASH]
```

Confirm the returned generation, state hash, and vault count.

**On `/vault list` or `/vault active`:**

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/governance.py" vault_list
```

Loaded vault documents are available to the package context assembly function when an integration routes context through it.
