#!/bin/bash
# MO§ES™ Post-Execute Hook
# Runs after any action to log to audit trail.
# Place in .claude/hooks/post-execute.sh

GOVERNANCE_STATE="${CLAUDE_PLUGIN_ROOT}/data/governance_state.json"
AUDIT_LEDGER="${CLAUDE_PLUGIN_ROOT}/data/audit_ledger.jsonl"

if [ -f "$GOVERNANCE_STATE" ]; then
    MODE=$(python3 -c "import json; print(json.load(open('$GOVERNANCE_STATE')).get('mode', 'unknown'))" 2>/dev/null)
    POSTURE=$(python3 -c "import json; print(json.load(open('$GOVERNANCE_STATE')).get('posture', 'unknown'))" 2>/dev/null)
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/audit.py" log_action \
        --component "hook" \
        --action "post_execute" \
        --mode "$MODE" \
        --posture "$POSTURE" \
        --ledger "$AUDIT_LEDGER" 2>/dev/null
    echo "✓ Action completed under governance: $MODE / $POSTURE"
    echo "✓ Audit entry appended"
else
    echo "⚠ Action completed without governance state file"
fi
