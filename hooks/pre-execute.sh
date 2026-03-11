#!/bin/bash
# MO§ES™ Pre-Execute Hook
# Runs before Bash, Write, and Edit operations to check governance state.
# Warns when no governance mode is set, but does not block execution.
# Hard-blocks only when a state file exists but is corrupt or invalid.

GOVERNANCE_STATE="${CLAUDE_PLUGIN_ROOT}/data/governance_state.json"

# No state file — governance not yet configured. Warn and allow.
if [ ! -f "$GOVERNANCE_STATE" ]; then
    echo "⚠ MO§ES™: No governance mode set. Use /govern to activate governance."
    exit 0
fi

# State file exists — validate it.
MODE=$(python3 -c "import json; print(json.load(open('$GOVERNANCE_STATE')).get('mode', ''))" 2>/dev/null)

if [ $? -ne 0 ]; then
    echo "⛔ MO§ES™: Governance state file is corrupt. Run /govern to reset."
    exit 1
fi

if [ -z "$MODE" ] || [ "$MODE" = "null" ]; then
    echo "⚠ MO§ES™: Governance state empty. Use /govern to set a mode."
    exit 0
fi

echo "✓ MO§ES™ Governance active: $MODE"
exit 0
