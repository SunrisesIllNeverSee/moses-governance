#!/usr/bin/env python3
"""Compatibility entry point forwarding to the single shared audit implementation."""
from pathlib import Path
import runpy
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "moses-governance-mcp"))
from governance.audit import *  # noqa: F401,F403,E402

if __name__ == "__main__":
    runpy.run_module("governance.audit", run_name="__main__")
