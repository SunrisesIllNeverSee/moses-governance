#!/bin/sh
# Shared pre-tool policy adapter. It consumes Codex hook JSON from stdin and
# retains the legacy Claude environment input path when invoked by that host.
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}"
exec python3 "${PLUGIN_ROOT}/scripts/pre_tool_use.py"
