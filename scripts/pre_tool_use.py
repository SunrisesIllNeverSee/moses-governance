#!/usr/bin/env python3
"""Fail-closed policy adapter for supported Codex PreToolUse event payloads."""
from __future__ import annotations

import json
import os
import re
import shlex
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "moses-governance-mcp"))

from governance.engine import GovernanceState, check_action_permitted  # noqa: E402
from governance.store import GovernanceStore, GovernanceStoreError  # noqa: E402
from governance.audit import AuditLedger, default_ledger_path  # noqa: E402


def _tool_action(tool_name: str, tool_input: dict) -> tuple[bool, str]:
    name = tool_name.lower()
    read_only = {"read", "search", "glob", "grep", "list", "web_search", "web_fetch",
                 "govern_check_action", "govern_get_status", "govern_assemble_context",
                 "vault_list", "audit_verify", "audit_recent", "audit_hash_session",
                 "meta_list_proposals", "meta_constitution_status"}
    leaf = name.rsplit("__", 1)[-1]
    if name in read_only or (name.startswith("mcp__moses_governance__") and leaf in read_only):
        return False, ""
    if name.startswith("mcp__") and leaf in {"govern_set_mode", "govern_set_posture", "govern_set_role"}:
        # Governance configuration is the control-plane recovery path. Its
        # handler still requires a fresh generation/hash and verified store.
        return False, ""
    if name == "bash":
        command = str(tool_input.get("command", ""))
        if re.search(r"[;|&<>`$\n]", command):
            return True, f"write/update governance state via shell action: {command}"
        try:
            words = shlex.split(command)
        except ValueError:
            words = []
        safe_commands = {"pwd", "ls", "cat", "head", "tail", "rg"}
        if words and words[0] in safe_commands:
            return False, ""
        # Accept only harmless git -C <path> prefixes before known read commands.
        # Do not widen the allowlist for arbitrary git global options.
        git_words = words[:]
        while len(git_words) >= 3 and git_words[:2] == ["git", "-C"]:
            git_words = ["git", *git_words[3:]]
        if len(git_words) >= 2 and git_words[0] == "git" and git_words[1] in {"status", "diff", "log", "show", "branch", "rev-parse"}:
            if not any(arg in {"-c", "--exec-path", "--config-env", "--output"} for arg in words[1:]):
                return False, ""
        if words and words[0] == "sed" and all(arg not in {"-i", "--in-place"} and not arg.startswith("-i") for arg in words[1:]):
            return False, ""
        if words and words[0] == "find" and not any(arg in {"-delete", "-exec", "-execdir", "-ok", "-okdir", "-fprint", "-fprintf"} for arg in words[1:]):
            return False, ""
        if len(words) >= 3 and words[0] in {"python", "python3"} and words[1].endswith("governance_store.py") and words[2] in {"status", "verify"}:
            return False, ""
        if len(words) >= 3 and words[0] in {"python", "python3"} and words[1].endswith("governance.py") and words[2] == "set_state":
            return False, ""
        if len(words) >= 3 and words[0] in {"python", "python3"} and words[1].endswith("audit.py") and words[2] in {"verify", "recent"}:
            return False, ""
        return True, f"write/update governance state via shell action: {command}"
    writes = {"bash", "apply_patch", "edit", "write", "create", "delete", "move", "rename"}
    if name in writes or name.startswith("mcp__"):
        return True, f"write/update governance state via {json.dumps({'tool_name': tool_name, 'tool_input': tool_input}, ensure_ascii=False)}"
    return True, f"write/update governance state via {json.dumps({'tool_name': tool_name, 'tool_input': tool_input}, ensure_ascii=False)}"


def main() -> int:
    raw = sys.stdin.read()
    try:
        event = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "deny",
            "permissionDecisionReason": "Malformed hook event; protected action could not be classified.",
        }}))
        return 0
    tool_name = event.get("tool_name") or event.get("toolName") or os.environ.get("CLAUDE_TOOL_NAME", "")
    tool_input = event.get("tool_input") or event.get("toolInput") or {}
    if not tool_name and os.environ.get("CLAUDE_TOOL_INPUT"):
        tool_name, tool_input = "Bash", {"command": os.environ["CLAUDE_TOOL_INPUT"]}
    if not isinstance(tool_input, dict):
        tool_input = {"value": tool_input}
    is_write, action = _tool_action(str(tool_name), tool_input)
    if not is_write:
        return 0

    reason = ""
    try:
        store = GovernanceStore()
        if not store.db_path.exists() and not store.state_path.exists():
            raise GovernanceStoreError("Governance state has not been initialized.")
        snapshot = store.read()
        audit = AuditLedger(default_ledger_path()).verify_integrity()
        if not audit.get("valid"):
            raise GovernanceStoreError(f"Audit ledger verification failed: {audit.get('reason', 'unknown error')}")
        state = GovernanceState(**snapshot.state)
        decision = check_action_permitted(action, state)
        if not decision.get("permitted", False):
            reason = decision.get("reason") or "Action blocked by governance policy."
        elif decision.get("conditions"):
            # The engine reports confirmation requirements as conditions, but
            # neither this event nor the host supplies authenticated approval.
            # A conditional permit MUST NOT silently turn into an allow.
            reason = "Unfulfilled governance conditions: " + "; ".join(
                str(condition) for condition in decision["conditions"]
            )
    except Exception as exc:
        reason = f"Governance state could not be verified; protected write blocked ({type(exc).__name__})."

    if not reason:
        return 0
    if event:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }}))
        return 0
    print(f"MO§ES governance blocked the write: {reason}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
