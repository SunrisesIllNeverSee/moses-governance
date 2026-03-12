#!/bin/bash
# MO§ES™ Session Start Hook
# Fires on every session start. Restores governance state into context.
#
# © 2026 Ello Cello LLC. Patent Pending: Serial No. 63/877,177

CLAUDE_PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
GOVERNANCE_STATE="${CLAUDE_PLUGIN_ROOT}/data/governance_state.json"

if [ -f "$GOVERNANCE_STATE" ]; then
    MODE=$(python3 -c "import json; d=json.load(open('$GOVERNANCE_STATE')); print(d.get('mode','None (Unrestricted)'))" 2>/dev/null)
    POSTURE=$(python3 -c "import json; d=json.load(open('$GOVERNANCE_STATE')); print(d.get('posture','SCOUT'))" 2>/dev/null)
    ROLE=$(python3 -c "import json; d=json.load(open('$GOVERNANCE_STATE')); print(d.get('role','Primary'))" 2>/dev/null)
    echo "✓ MO§ES™ Governance restored"
    echo "  Mode: $MODE | Posture: $POSTURE | Role: $ROLE"
    echo "  Constitutional governance is active. All tool actions are subject to enforcement."
    echo "  Use /status for full state. Use /govern to change mode."
else
    echo "✓ MO§ES™ Governance available. Use /govern to activate."
fi
