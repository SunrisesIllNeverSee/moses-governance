# MO§ES Governance Plugin Status

## Overall readiness

You’re **not ship-ready yet**. The good news is the ZIP’s JSON/YAML parses cleanly and the Bash/Python files are syntactically valid. The blockers are **spec/layout** and **governance/audit enforcement gaps** relative to what the plugin claims to provide. citeturn14view2turn15view0turn5view1

## What’s blocking shipment

The current top blockers are:

- **Plugin layout is noncompliant for review**: the manifest is expected at `.claude-plugin/plugin.json`; your ZIP is missing the `.claude-plugin/` directory, and the included marketplace file is not at `.claude-plugin/marketplace.json` (required for a marketplace repo). citeturn14view2turn15view0turn14view0turn14view1  
- **PreToolUse enforcement isn’t actually enforcing**: `PreToolUse` must return decisions using `hookSpecificOutput.permissionDecision` for allow/deny/ask. Plain stdout + non-blocking exit codes won’t do what your hook descriptions imply. citeturn5view1turn14view5  
- **Coverage is too narrow for “constitutional governance”**: you don’t have `Stop` or `UserPromptSubmit` hooks, which are the key enforcement points for response-level governance and prompt gating (they always fire). citeturn5view3turn8view1turn17view0  
- **Audit trail is fragile as implemented**: `PostToolUse` is configured as `async: true` (so it can’t control behavior and spawns concurrent background processes), and storing ledger/state under the plugin cache root is vulnerable to cache/version/staleness issues that have been reported. citeturn17view0turn15view0turn2search14  
- **Docs onboarding is currently broken**: README has multiple broken internal links (e.g., `docs/QUICKSTART.md`), which will fail a basic reviewer walkthrough.

## What’s already solid

- **Core component coverage exists**: you do have 9 commands, 3 agents, skills, hooks, and working scripts—so you have the raw materials. citeturn15view0turn16view0  
- **Agents look structurally correct** (name/description + tools/model included), aligned with subagent frontmatter expectations. citeturn3view2  
- Hooks are at the correct path (`hooks/hooks.json`) and use valid event names for the events you included. citeturn9view0turn8view1  

## Fastest path to “green”

If you want the shortest route to something reviewers will accept:

- Fix the **layout** first: add `.claude-plugin/`, move the manifest to `.claude-plugin/plugin.json`, and only keep documented manifest fields. citeturn14view2turn15view0turn7view1  
- Make `PreToolUse` actually **deny/ask** using the documented output schema (or blocking exit semantics) instead of relying on stdout warnings. citeturn5view1turn14view5  
- Add `UserPromptSubmit` (for context injection / prompt gating) and `Stop` (for response-level governance conformance). citeturn5view3turn17view0  
- Move **state + ledger** out of the plugin cache directory (project-scope under `${CLAUDE_PROJECT_DIR}` is the usual safest) and add basic locking before you call the audit “tamper-evident.” citeturn15view0turn17view0turn2search14  
- Fix README links and make the Quickstart pass a “cold install” walkthrough.

If you tell me your target distribution mode (“single local plugin folder” vs “marketplace repo with plugins/ subdir”), I can give you the exact folder tree + the minimal diff list to get approved.