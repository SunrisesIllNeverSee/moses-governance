#!/usr/bin/env python3
"""MO§ES™ PreToolUse gate for Bash, called by hooks/pre-execute.sh.

Exit 0 = allow (stdout may carry an "ask" decision JSON), exit 2 = block.
Any failure while classifying a Bash call blocks it (fail closed).
Write/Edit events are not evaluated here.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT") or Path(__file__).resolve().parents[1])
METACHARS = re.compile(r"[;|&`<>\n]|\$\(")


def block(reason: str) -> int:
    print(f"⛔ MO§ES™ BLOCKED: {reason}", file=sys.stderr)
    return 2


def read_command() -> tuple[str, str | None]:
    """Return (tool, command). command is None when it cannot be read."""
    legacy = os.environ.get("CLAUDE_TOOL_INPUT", "")
    if legacy:
        return "bash", legacy
    raw = sys.stdin.read()
    event = json.loads(raw)  # malformed JSON raises -> caller blocks
    tool = str(event.get("tool_name") or "").lower()
    if tool != "bash":
        return tool, ""
    tool_input = event.get("tool_input")
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    return "bash", command if isinstance(command, str) and command.strip() else None


def is_governance_command(command: str) -> bool:
    """Exactly one call to the plugin's own governance or audit script."""
    flat = command.replace("\\\n", " ").strip()
    roots = [re.escape("${CLAUDE_PLUGIN_ROOT}"), re.escape(str(ROOT))]
    m = re.fullmatch(
        r'python3?\s+"?(?:' + "|".join(roots) + r')/scripts/(?:governance|audit)\.py"?\s+'
        r"(?:set_state|vault_load|vault_unload|vault_list|log_action)\b(?P<rest>.*)",
        flat,
        flags=re.S,
    )
    return bool(m) and not METACHARS.search(m.group("rest"))


def main() -> int:
    state = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "governance_state.json"
    mode = sys.argv[2] if len(sys.argv) > 2 else ""
    try:
        tool, command = read_command()
    except Exception as exc:  # unreadable event
        return block(f"hook event could not be read ({type(exc).__name__})")
    if tool != "bash":
        print(f"✓ MO§ES™ Governance active: {mode}")
        return 0
    if command is None:
        return block("Bash event carried no command")
    if is_governance_command(command):
        print("✓ MO§ES™: Governance system command — exempt")
        return 0

    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "governance.py"), "check_action",
         "--state", str(state), "--", command],
        capture_output=True, text=True, timeout=30,
    )
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        detail = (proc.stderr or "").strip().splitlines()[-1:] or ["no output"]
        return block(f"governance check failed: {detail[0]}")

    if not result.get("permitted", False):
        return block(str(result.get("reason") or "Action blocked by governance"))
    conditions = result.get("conditions") or []
    if conditions:
        reason = "MO§ES™ requires operator confirmation: " + "; ".join(map(str, conditions))
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        }}))
        return 0
    print(f"✓ MO§ES™ Governance active: {mode}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        raise SystemExit(block(f"governance hook error ({type(exc).__name__})"))
