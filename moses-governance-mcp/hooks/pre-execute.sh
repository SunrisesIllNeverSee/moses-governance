#!/bin/sh
# Compatibility entry point into the common supported-host policy adapter.
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
exec python3 "${SCRIPT_DIR}/../../scripts/pre_tool_use.py"
