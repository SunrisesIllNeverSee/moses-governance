#!/usr/bin/env python3
"""MO§ES™ PreToolUse gate for Bash, called by hooks/pre-execute.sh.

Exit 0 = allow (stdout may carry an "ask" decision JSON), exit 2 = block.
Any failure while classifying a Bash call blocks it (fail closed).
Other tools are not evaluated, except that file tools may not touch the
plugin's own data/, hooks/ or scripts/.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT") or Path(__file__).resolve().parents[1])
OPERATOR_CHARS = ";|&<>\n"
SUBSTITUTION = re.compile(r"`|\$\(")
PROTECTED_DIRS = ("data", "hooks", "scripts")
ERROR_LOG = ROOT / "data" / "hook_errors.log"


def block(reason: str) -> int:
    print(f"⛔ MO§ES™ BLOCKED: {reason}", file=sys.stderr)
    return 2


def log_error(text: str) -> None:
    try:
        with open(ERROR_LOG, "a", encoding="utf-8") as fh:
            fh.write(text.rstrip() + "\n")
    except OSError:
        pass


def read_event() -> tuple[str, dict]:
    """Return (tool, tool_input) from the stdin event.

    The legacy CLAUDE_TOOL_INPUT variable is used only when stdin is empty.
    Malformed JSON or a missing tool_name raises, and the caller blocks.
    """
    raw = "" if sys.stdin.isatty() else sys.stdin.read()
    if not raw.strip():
        legacy = os.environ.get("CLAUDE_TOOL_INPUT", "")
        if legacy:
            return "bash", {"command": legacy}
        raise ValueError("empty hook event")
    event = json.loads(raw)
    tool = str(event.get("tool_name") or "").strip().lower()
    if not tool:
        raise ValueError("hook event has no tool_name")
    tool_input = event.get("tool_input")
    return tool, tool_input if isinstance(tool_input, dict) else {"value": tool_input}


def touches_protected_path(tool_input: dict) -> str | None:
    """A file tool aimed at the plugin's own state, hooks or scripts."""
    for key in ("file_path", "notebook_path", "path"):
        value = tool_input.get(key)
        if not isinstance(value, str) or not value:
            continue
        target = Path(value).expanduser().resolve()
        for name in PROTECTED_DIRS:
            guarded = (ROOT / name).resolve()
            if target == guarded or guarded in target.parents:
                return value
    return None


def has_shell_operators(text: str) -> bool:
    """True when text carries an unquoted shell operator or any substitution."""
    if SUBSTITUTION.search(text):
        return True
    try:
        lexer = shlex.shlex(text, posix=True, punctuation_chars=OPERATOR_CHARS)
        lexer.whitespace = " \t\r"
        tokens = list(lexer)
    except ValueError:  # unbalanced quotes
        return True
    return any(tok and set(tok) <= set(OPERATOR_CHARS) for tok in tokens)


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
    return bool(m) and not has_shell_operators(m.group("rest"))


def main() -> int:
    state = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "governance_state.json"
    mode = sys.argv[2] if len(sys.argv) > 2 else ""
    try:
        tool, tool_input = read_event()
    except Exception as exc:  # unreadable event
        log_error(f"hook_gate: unreadable event: {exc!r}")
        return block(f"hook event could not be read ({type(exc).__name__})")
    if tool != "bash":
        protected = touches_protected_path(tool_input)
        if protected:
            return block(f"{tool} on the plugin's own governance files is not allowed: {protected}")
        print(f"MO§ES™: {tool} not evaluated (only Bash commands are checked)")
        return 0
    command = tool_input.get("command")
    if not isinstance(command, str) or not command.strip():
        return block("Bash event carried no command")
    if is_governance_command(command):
        print("✓ MO§ES™: Governance system command — exempt")
        return 0

    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "governance.py"), "check_action",
         "--state", str(state), "--", command],
        capture_output=True, text=True, timeout=30,
    )
    if proc.stderr.strip():
        log_error(f"hook_gate: check_action stderr:\n{proc.stderr}")
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
