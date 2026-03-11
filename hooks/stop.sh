#!/bin/bash
# MO§ES™ Stop Hook
# Fires after every Claude response. Logs response completion to audit trail.
#
# © 2026 Ello Cello LLC. Patent Pending: Serial No. 63/877,177

GOVERNANCE_STATE="${CLAUDE_PLUGIN_ROOT}/data/governance_state.json"
AUDIT_LEDGER="${CLAUDE_PLUGIN_ROOT}/data/audit_ledger.jsonl"

if [ -f "$GOVERNANCE_STATE" ]; then
    MODE=$(python3 -c "import json; print(json.load(open('$GOVERNANCE_STATE')).get('mode','unknown'))" 2>/dev/null)
    POSTURE=$(python3 -c "import json; print(json.load(open('$GOVERNANCE_STATE')).get('posture','unknown'))" 2>/dev/null)
    ROLE=$(python3 -c "import json; print(json.load(open('$GOVERNANCE_STATE')).get('role','unknown'))" 2>/dev/null)
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/audit.py" log_action \
        --component "response" \
        --action "stop" \
        --mode "$MODE" \
        --posture "$POSTURE" \
        --role "$ROLE" \
        --ledger "$AUDIT_LEDGER" 2>/dev/null
fi
