---
name: vault
description: >
  Loads a governance document into active session context so it applies to all subsequent responses. Use when you want a policy, constitution, or reference document to govern all outputs, or when you say 'load this into vault', 'apply this document', or 'govern with this'.
---
# MO§ES™ Vault

Vault loads governance documents — constitutions, operating agreements, role definitions, constraint sets — into the active session context so Claude applies them throughout the conversation.

## Usage

**Load by name** (user references a document they've shared or will share):
```
/vault constitution
/vault operating-agreement
/vault role-definitions
```

**Load by pasting content** (user pastes the document directly):
```
/vault
[document content pasted below]
```

## Behavior

When invoked:

1. If a document name is provided but no content is visible in the conversation, ask the user to paste or share the document content.

2. If document content is provided (either pasted or previously shared in the conversation):
   - Acknowledge the document
   - Summarize its key governance rules in 3-5 bullet points
   - Confirm it is now active
   - Apply its rules to all subsequent responses

3. Confirm with:
```
✓ Vault loaded: [DOCUMENT NAME]
Key rules active:
  • [rule 1]
  • [rule 2]
  • [rule 3]
Document governance applied to this session.
```

4. If multiple documents are loaded across the session, maintain all of them. If they conflict, flag the conflict explicitly and ask the operator which takes precedence.

5. Track loaded documents — report them when `/status` is called.

## Note

In the Claude Code plugin, vault loads files from disk. In this Cowork/Chat version, documents are injected directly into conversation context. Content is session-scoped — it does not persist across conversations.
