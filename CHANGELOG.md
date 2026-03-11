# Changelog

All notable changes to the MO§ES™ Governance plugin will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioned per [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-03-11

### Added
- MCP server (moses-governance-mcp/): 23 governance tools via FastMCP stdio transport
  - Core: govern_set_mode/posture/role, govern_check_action, govern_get_status, govern_assemble_context
  - Vault: vault_load, vault_list, vault_clear
  - Audit: audit_log, audit_verify, audit_recent, audit_hash_session
  - Commitment: govern_check_commitment (TF-IDF cosine drift scoring — McHenry Conservation Law)
  - Oracle: govern_oracle_verify (Grok xAI gate, graceful degradation without API key)
  - Swarm: govern_run_swarm_round (Primary→Secondary→Observer with commitment check)
  - Meta-governance: meta_analyze_trail, meta_apply_amendment, meta_rollback_amendment,
    meta_constitution_status, meta_list_proposals, meta_reject_proposal, meta_generate_sig
- Self-amending living constitution (data/constitution.json) with 7 immutable core principles
- HMAC-SHA256 operator signatures on all constitutional amendments (MOSES_OPERATOR_SECRET)
- Test session tagging: analyze_audit_trail() accepts exclude_tags to filter boundary-probe traffic
- UserPromptSubmit and Stop hooks — governance context injected before every prompt, every response logged
- session-start.sh — governance state restored from disk on every session start
- plugin.json now declares mcpServers — MCP server starts automatically on plugin install

### Fixed
- Commands (/govern, /posture, /role, /vault) now write to governance_state.json on execution —
  hooks and MCP server were previously reading stale defaults
- pre-execute.sh now calls check_action_permitted() via CLI — enforcement was checking state file
  existence but never evaluating whether the action was permitted
- Hook exit code corrected: exit 2 (block) instead of exit 1 (error)
- _rule_triggered(): removed "execut" from execution rule-text signals — prevented false positive
  where "run portfolio analysis" triggered "Executing transactions without confirmation"
- Expanded _CONCEPT_SIGNALS with synonym sets (remit, liquidate, disburse) to close paraphrase bypass

### Notes
- Patent pending: PPA4, Serial No. 63/877,177
- Preprint: Zenodo 10.5281/zenodo.18792459 — 60% recursion stability vs 20% baseline (+40pp)
- Grokipedia indexed

## [1.0.0] - 2026-03-07

### Added
- 9 slash commands: /govern, /posture, /role, /vault, /command, /audit, /hash, /status, /docs
- 6 auto-activating skills: governance-mode, posture-control, role-hierarchy, audit-trail, context-assembly, doc-numbering
- 3 agent definitions: Primary, Secondary, Observer
- 2 Python scripts: governance.py (mode translation + context assembly), audit.py (SHA-256 hash chain)
- 4 context files: high-security, research, creative, defense
- 1 rules file: constitutional governance rules (always-follow)
- Hooks: PreToolUse governance check, PostToolUse audit logging, SessionStart announcement
- 4 worked examples: treasury governance, code review, research pipeline, multi-agent coordination
- Documentation: Quickstart, Architecture, Enterprise Use, Patent Notice
- settings.json with safe defaults (Unrestricted mode + SCOUT posture)
- marketplace.json for plugin discovery
- Full patent and license documentation

### Notes
- Patent pending: PPA4, Serial No. 63/877,177
- Preprint published with independent validation
- Live demo at mos2es.io
