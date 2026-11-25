#!/bin/bash
# MO§ES™ Pre-Execute Hook
# Runs before Bash, Write, and Edit operations. Only Bash commands are
# evaluated; Write/Edit pass once a valid governance state exists.
# exit 0 = allow | exit 2 = block (Claude Code spec)
#
# © 2026 Ello Cello LLC. Patent Pending: Serial No. 63/877,177

CLAUDE_PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
GOVERNANCE_STATE="${CLAUDE_PLUGIN_ROOT}/data/governance_state.json"
ERROR_LOG="${CLAUDE_PLUGIN_ROOT}/data/hook_errors.log"

# Ensure data directory exists
mkdir -p "${CLAUDE_PLUGIN_ROOT}/data"

# Check Python availability — required for governance checks
if ! command -v python3 >/dev/null 2>&1; then
    echo "⚠ MO§ES™: Python 3 not found — governance checks disabled. Install Python 3 to enable."
    exit 0
fi

# No state file — governance not yet configured. Warn and allow.
if [ ! -f "$GOVERNANCE_STATE" ]; then
    echo "⚠ MO§ES™: No governance mode set. Use /govern to activate."
    exit 0
fi

# Validate state file is readable and parse mode
MODE=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('mode',''))" "$GOVERNANCE_STATE" 2>>"$ERROR_LOG")
if [ $? -ne 0 ]; then
    echo "⛔ MO§ES™: Governance state corrupt. Run /govern to reset." >&2
    exit 2
fi

if [ -z "$MODE" ] || [ "$MODE" = "null" ]; then
    echo "⚠ MO§ES™: Governance state empty. Use /govern to set a mode."
    exit 0
fi

# Evaluate the Bash command (read from the stdin event) against the active rules.
# scripts/hook_gate.py exits 0 to allow (or prints an "ask" decision) and 2 to
# block. Any other exit means the gate itself failed: block (fail closed).
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/hook_gate.py" "$GOVERNANCE_STATE" "$MODE"
STATUS=$?
if [ "$STATUS" -eq 0 ]; then
    exit 0
fi
[ "$STATUS" -eq 2 ] || echo "⛔ MO§ES™ BLOCKED: governance gate failed (exit $STATUS)" >&2
exit 2
