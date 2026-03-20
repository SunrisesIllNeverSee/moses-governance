#!/bin/bash
# MO§ES™ Post-Execute Hook
# Runs after any action to log to audit trail.
# Place in .claude/hooks/post-execute.sh

CLAUDE_PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
GOVERNANCE_STATE="${CLAUDE_PLUGIN_ROOT}/data/governance_state.json"
AUDIT_LEDGER="${CLAUDE_PLUGIN_ROOT}/data/audit_ledger.jsonl"
ERROR_LOG="${CLAUDE_PLUGIN_ROOT}/data/hook_errors.log"

# Ensure data directory exists
mkdir -p "${CLAUDE_PLUGIN_ROOT}/data"

# Check Python availability
if ! command -v python3 >/dev/null 2>&1; then
    echo "⚠ MO§ES™: Python 3 not found — audit logging disabled."
    exit 0
fi

if [ -f "$GOVERNANCE_STATE" ]; then
    MODE=$(python3 -c "import json; print(json.load(open('$GOVERNANCE_STATE')).get('mode', 'unknown'))" 2>>"$ERROR_LOG")
    POSTURE=$(python3 -c "import json; print(json.load(open('$GOVERNANCE_STATE')).get('posture', 'unknown'))" 2>>"$ERROR_LOG")
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/audit.py" log_action \
        --component "hook" \
        --action "post_execute" \
        --mode "$MODE" \
        --posture "$POSTURE" \
        --ledger "$AUDIT_LEDGER" 2>>"$ERROR_LOG"
    echo "✓ Action completed under governance: $MODE / $POSTURE"
    echo "✓ Audit entry appended"
else
    echo "⚠ Action completed without governance state file"
fi
