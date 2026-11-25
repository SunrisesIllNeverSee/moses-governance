#!/usr/bin/env python3
"""Inspect and recover the shared governance state store."""
import argparse
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "moses-governance-mcp"))
from governance.store import GovernanceStore, default_state_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Shared governance state status and recovery")
    parser.add_argument("command", choices=("status", "verify", "export", "backup"))
    parser.add_argument("--state", default=None, help="Canonical governance state path")
    parser.add_argument("--output", help="SQLite backup destination (backup only)")
    args = parser.parse_args()
    store = GovernanceStore(args.state or default_state_path())
    if args.command == "status":
        report = store.inspect()
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report.get("valid") else 1
    if args.command == "verify":
        report = store.verify()
        print(json.dumps(report, indent=2))
        return 0 if report.get("valid") else 1
    if args.command == "export":
        print(json.dumps(store.export(), indent=2))
        return 0
    verification = store.verify()
    if not verification.get("valid"):
        print(json.dumps(verification, indent=2))
        return 1
    if not args.output:
        parser.error("backup requires --output")
    target = Path(args.output).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(store.db_path) as source, sqlite3.connect(target) as destination:
        source.backup(destination)
    print(json.dumps({"backup": str(target), **store.read().public_metadata()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
