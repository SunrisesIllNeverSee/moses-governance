#!/bin/bash
# MO§ES™ Pre-Execute Hook
# Runs before Bash, Write, and Edit operations.
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

# Whitelist governance system commands — always allow, never self-block.
# These are internal MO§ES™ operations (set_state, vault_load, audit log_action).
# Blocking them would prevent governance from functioning at all.
_ACTION_PREVIEW="${CLAUDE_TOOL_INPUT:-}"
if echo "$_ACTION_PREVIEW" | grep -qE "(governance\.py|audit\.py).*(set_state|vault_load|vault_unload|vault_list|log_action)"; then
    echo "✓ MO§ES™: Governance system command — exempt"
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

# Evaluate proposed action against active governance rules
ACTION="${CLAUDE_TOOL_INPUT:-}"
if [ -n "$ACTION" ]; then
    RESULT=$(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/governance.py" check_action "$ACTION" --state "$GOVERNANCE_STATE" 2>>"$ERROR_LOG")
    if echo "$RESULT" | python3 -c "import sys,json; r=json.load(sys.stdin); exit(0 if r.get('permitted',True) else 1)" 2>/dev/null; then
        echo "✓ MO§ES™ Governance active: $MODE"
        exit 0
    else
        REASON=$(echo "$RESULT" | python3 -c "import sys,json; r=json.load(sys.stdin); print(r.get('reason','Action blocked by governance'))" 2>/dev/null || echo "Action blocked by MO§ES™ governance")
        echo "⛔ MO§ES™ BLOCKED: $REASON" >&2
        exit 2
    fi
fi

echo "✓ MO§ES™ Governance active: $MODE"
exit 0
