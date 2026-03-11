#!/bin/bash
# MO§ES™ Pre-Execute Hook
# Runs before Bash, Write, and Edit operations.
# exit 0 = allow | exit 2 = block (Claude Code spec)
#
# © 2026 Ello Cello LLC. Patent Pending: Serial No. 63/877,177

GOVERNANCE_STATE="${CLAUDE_PLUGIN_ROOT}/data/governance_state.json"

# No state file — governance not yet configured. Warn and allow.
if [ ! -f "$GOVERNANCE_STATE" ]; then
    echo "⚠ MO§ES™: No governance mode set. Use /govern to activate."
    exit 0
fi

# Validate state file is readable and parse mode
MODE=$(python3 -c "import json; print(json.load(open('$GOVERNANCE_STATE')).get('mode', ''))" 2>/dev/null)
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
    RESULT=$(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/governance.py" check_action "$ACTION" --state "$GOVERNANCE_STATE" 2>/dev/null)
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
