---
name: vault
description: >
  Loads a governance document into active session context. Rules and constraints in the document apply to all subsequent responses. Use when you want to inject a policy, playbook, constitution, or ruleset into the session, or when you say 'load this document', 'vault this', 'apply these rules', or 'add to vault'.
---
Load a governance document into active context. Parse it for rules and constraints, confirm the load with a summary of key rules, and apply to every subsequent response. If multiple documents conflict, flag the conflict and ask which takes precedence. If invoked without content, ask the user to paste or share the document. Track vault contents — report in /status.
