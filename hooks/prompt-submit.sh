#!/bin/bash
# MO§ES™ UserPromptSubmit Hook
# Fires before Claude processes each user prompt.
# Injects active governance state into context so every response is governed.
#
# © 2026 Ello Cello LLC. Patent Pending: Serial No. 63/877,177

CLAUDE_PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
GOVERNANCE_STATE="${CLAUDE_PLUGIN_ROOT}/data/governance_state.json"

if [ -f "$GOVERNANCE_STATE" ]; then
    python3 -c "
import json, sys
with open('$GOVERNANCE_STATE') as f:
    s = json.load(f)
mode = s.get('mode', 'None (Unrestricted)')
posture = s.get('posture', 'SCOUT')
role = s.get('role', 'Primary')
if mode != 'None (Unrestricted)':
    print(f'[GOVERNANCE ACTIVE: {mode} | {posture} | {role}]')
" 2>/dev/null
fi
exit 0
