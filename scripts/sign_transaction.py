#!/usr/bin/env python3
"""
sign_transaction.py — Signing tool with governance gate (v0.5)

The signing function IS the governance function.
No bypass path exists — by architecture, not by rule.

The MOSES_OPERATOR_SECRET is accessed ONLY inside this tool, ONLY after the
governance gate passes. There is no code path that reaches the key without
first clearing posture/mode/role constraints.

Architecture:
  Agent requests signing ->
    calls sign_transaction.py sign ->
      governance gate checks posture + mode (inside this tool) ->
        BLOCKED? returns error, exits 1. Key never accessed.
        PERMITTED? signs payload, writes audit, returns signed JSON.

Usage:
  python3 sign_transaction.py sign --payload "<text>" --agent <name> [--confirm]
  python3 sign_transaction.py verify --payload "<text>" --sig <hex>
  python3 sign_transaction.py status

(c) 2026 Ello Cello LLC. Patent Pending: Serial No. 63/877,177
"""

import argparse
import datetime
import hashlib
import hmac as _hmac
import json
import os
import sys

_PLUGIN_ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT", os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "moses-governance-mcp"))
from governance.store import GovernanceStore

STATE_PATH = None


# ── governance gate ───────────────────────────────────────────────────────────

class GovernanceBlock(Exception):
    pass


def _load_state() -> dict | None:
    return GovernanceStore().read().state


def _governance_gate(state: dict, confirm: bool) -> dict:
    del state, confirm
    raise GovernanceBlock("Privileged signing is disabled: this package has no trusted operator identity provider. A command-line confirmation flag is not authenticated approval.")


# ── cryptographic primitives ──────────────────────────────────────────────────

def _payload_hash(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _sign(payload: str, secret: str) -> str:
    return _hmac.new(
        secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


# ── audit write ───────────────────────────────────────────────────────────────

def _write_audit(agent: str, action: str, detail: str, gov: dict) -> str:
    """Append to audit ledger. Returns entry hash."""
    from governance.audit import AuditLedger, default_ledger_path
    entry = AuditLedger(default_ledger_path()).log_action(
        component="signing", action=action, detail={"detail": detail},
        governance_mode=gov.get("mode", ""), posture=gov.get("posture", ""),
        role=gov.get("role", ""), agent=agent,
    )
    return entry["hash"][:16]


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_sign(args):
    # Step 1: Load governance state. Key is never touched yet.
    state = _load_state()
    if state is None:
        print(json.dumps({
            "status": "ERROR",
            "reason": "Governance state not initialized. Run /govern to set a mode.",
            "signature": None,
        }, indent=2))
        sys.exit(1)

    # Step 2: Governance gate. Key still untouched.
    try:
        approved = _governance_gate(state, confirm=getattr(args, "confirm", False))
    except GovernanceBlock as e:
        print(json.dumps({
            "status": "BLOCKED",
            "reason": str(e),
            "posture": state.get("posture"),
            "mode": state.get("mode"),
            "signature": None,
        }, indent=2))
        sys.exit(1)

    # Step 3: Key access. Only reachable after gate passes.
    secret = os.environ.get("MOSES_OPERATOR_SECRET", "")
    if not secret:
        print(json.dumps({
            "status": "ERROR",
            "reason": "MOSES_OPERATOR_SECRET not set. Set it in your environment.",
            "signature": None,
        }, indent=2))
        sys.exit(1)

    # Step 4: Sign.
    p_hash = _payload_hash(args.payload)
    sig = _sign(args.payload, secret)
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()

    signed = {
        "status": "SIGNED",
        "payload_hash": p_hash,
        "signature": sig,
        "timestamp": ts,
        "governance_state": approved,
        "agent": args.agent,
    }

    # Step 5: Audit. Atomic with signing.
    try:
        audit_ref = _write_audit(args.agent, "moses_sign_transaction", f"payload_hash={p_hash}", approved)
        signed["audit_ref"] = audit_ref
    except Exception as e:
        signed["audit_warning"] = f"Signing succeeded but audit write failed: {e}"

    print(json.dumps(signed, indent=2))


def cmd_verify(args):
    secret = os.environ.get("MOSES_OPERATOR_SECRET", "")
    if not secret:
        print(json.dumps({"status": "ERROR", "reason": "MOSES_OPERATOR_SECRET not set"}, indent=2))
        sys.exit(1)

    expected = _sign(args.payload, secret)
    match = _hmac.compare_digest(expected, args.sig)
    print(json.dumps({
        "status": "VALID" if match else "INVALID",
        "payload_hash": _payload_hash(args.payload),
        "signature_match": match,
    }, indent=2))
    sys.exit(0 if match else 1)


def cmd_status(_args):
    state = _load_state()
    if state is None:
        print(json.dumps({"gate": "ERROR", "reason": "Governance state not initialized."}, indent=2))
        sys.exit(1)

    posture = (state.get("posture") or "SCOUT").upper()
    try:
        _governance_gate(state, confirm=True)
        gate = "REQUIRES_CONFIRM" if posture == "DEFENSE" else "OPEN"
        note = "Signing unavailable until trusted operator identity is configured."
    except GovernanceBlock as e:
        gate = "BLOCKED"
        note = str(e)

    print(json.dumps({
        "gate": gate,
        "posture": posture,
        "mode": state.get("mode"),
        "role": state.get("role"),
        "note": note,
    }, indent=2))


def main():
    parser = argparse.ArgumentParser(description="MO§ES™ signing tool with governance gate")
    sub = parser.add_subparsers(dest="command")

    p_sign = sub.add_parser("sign", help="Sign a payload (governance gate runs first)")
    p_sign.add_argument("--payload", required=True, help="Payload to sign")
    p_sign.add_argument("--agent", required=True, help="Agent name for audit")
    p_sign.add_argument("--confirm", action="store_true", help="Explicit confirmation (required in DEFENSE)")

    p_verify = sub.add_parser("verify", help="Verify a signature")
    p_verify.add_argument("--payload", required=True, help="Original payload")
    p_verify.add_argument("--sig", required=True, help="Signature hex")

    sub.add_parser("status", help="Show governance gate status")

    args = parser.parse_args()
    cmds = {"sign": cmd_sign, "verify": cmd_verify, "status": cmd_status}
    if args.command in cmds:
        cmds[args.command](args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
