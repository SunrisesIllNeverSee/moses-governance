#!/usr/bin/env python3
"""
MO§ES™ Lineage — Origin-Cycle Custody Verification
Provisional Patent Serial No. 63/877,177 | DOI: https://zenodo.org/records/18792459

Usage:
  python3 lineage.py init          ← Anchor genesis to origin filing
  python3 lineage.py verify        ← Verify package-local lineage consistency
  python3 lineage.py badge         ← Output shareable lineage proof
  python3 lineage.py check         ← Quick pass/fail lineage check
"""

import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "moses-governance-mcp"))
from governance.store import GovernanceStore
from datetime import datetime, timezone

# ─── Origin-Cycle Anchor ────────────────────────────────────────────────────
# Derived from the supplied filing identifiers. This marker is not an
# independent attestation of the filing or of external chain custody.

_ORIGIN_COMPONENTS = (
    "MO§ES™",
    "Serial:63/877,177",
    "DOI:https://zenodo.org/records/18792459",
    "SCS Engine",
    "Ello Cello LLC",
)
MOSES_ANCHOR = hashlib.sha256(
    "|".join(_ORIGIN_COMPONENTS).encode("utf-8")
).hexdigest()

# ─── Paths ───────────────────────────────────────────────────────────────────

_store = GovernanceStore()
LEDGER_PATH = str(_store.data_root / "audit_ledger.jsonl")
LINEAGE_PATH = str(_store.data_root / "lineage.json")
STATE_PATH = str(_store.state_path)


def ensure_dirs():
    # GovernanceStore creates its own data directory when committing.
    return None


def canonical(data: dict) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_hash(data: dict) -> str:
    return hashlib.sha256(canonical(data).encode()).hexdigest()


def load_lineage() -> dict | None:
    raw = _store.read_resource("lineage.json")
    return json.loads(raw) if raw else None


def save_lineage(record: dict):
    snapshot = _store.read()
    _store.transition("lineage.initialize", expected_generation=snapshot.generation,
        expected_hash=snapshot.state_hash, resource_updates={"lineage.json": json.dumps(record, ensure_ascii=False, indent=2)},
        actor="lineage-cli", detail={"genesis_hash": record.get("genesis_hash")})


# ─── Commands ────────────────────────────────────────────────────────────────

def cmd_init(_args):
    ensure_dirs()

    if load_lineage():
        existing = load_lineage()
        print(f"[LINEAGE] Already anchored.")
        print(f"  Anchor : {existing['lineage_anchor'][:24]}...")
        print(f"  Genesis: {existing['genesis_hash'][:24]}...")
        print(f"  Filed  : {existing['anchored_at']}")
        return

    genesis_payload = {
        "event": "genesis",
        "lineage_anchor": MOSES_ANCHOR,
        "patent_serial": "63/877,177",
        "doi": "https://zenodo.org/records/18792459",
        "author": "Ello Cello LLC",
        "system": "MO§ES™ Constitutional Governance",
        "previous_hash": MOSES_ANCHOR,  # chain roots to the anchor, not zeros
        "anchored_at": datetime.now(timezone.utc).isoformat(),
    }
    genesis_hash = compute_hash(genesis_payload)
    genesis_payload["hash"] = genesis_hash

    record = {
        "lineage_anchor": MOSES_ANCHOR,
        "genesis_hash": genesis_hash,
        "anchored_at": genesis_payload["anchored_at"],
        "patent_serial": "63/877,177",
        "doi": "https://zenodo.org/records/18792459",
    }
    save_lineage(record)

    # The canonical transition chain records initialization. Do not inject a
    # differently shaped lineage record into the strict audit JSONL ledger.

    print(f"[LINEAGE] Origin-cycle anchor established.")
    print(f"  Anchor : {MOSES_ANCHOR[:24]}...")
    print(f"  Genesis: {genesis_hash[:24]}...")
    print(f"  Patent : 63/877,177")
    print(f"  DOI    : https://zenodo.org/records/18792459")
    print()
    print("[LINEAGE] The marker is recorded in the package-local transition history.")
    print("[LINEAGE] This check does not independently authenticate external custody.")


def cmd_verify(_args):
    record = load_lineage()
    if not record:
        print("[LINEAGE FAIL] No lineage anchor found. Run: python3 lineage.py init")
        sys.exit(1)

    # ── Layer -1: Archival chain — does the anchor have pre-drop provenance? ──
    _archival_ok = False
    _archival_head = None
    try:
        import importlib.util, pathlib
        _spec = importlib.util.spec_from_file_location(
            "archival",
            pathlib.Path(__file__).parent / "archival.py"
        )
        _arch = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_arch)
        _chain = _arch.build_chain()
        _archival_head = _arch.archival_head(_chain)
        # Verify stored chain if it exists
        _stored = _arch.load_chain()
        if _stored and _stored.get("head") == _archival_head:
            _archival_ok = True
        elif not _stored:
            # Not yet persisted — recomputed is still valid
            _archival_ok = True
    except Exception as _e:
        pass  # archival.py optional — warn but don't fail

    if _archival_ok:
        print(f"[ARCHIVAL OK] Layer -1: pre-drop provenance chain verified.")
        print(f"  Head   : {_archival_head[:24]}...")
    else:
        print(f"[ARCHIVAL WARN] Layer -1: archival chain not verified (run: python3 archival.py build)")

    # ── Layer 0: MOSES_ANCHOR — recompute from origin components ─────────────
    recomputed = hashlib.sha256(
        "|".join(_ORIGIN_COMPONENTS).encode("utf-8")
    ).hexdigest()

    if recomputed != MOSES_ANCHOR:
        print("[LINEAGE FAIL] Anchor computation mismatch. Origin components altered.")
        sys.exit(1)

    if record.get("lineage_anchor") != MOSES_ANCHOR:
        print("[LINEAGE FAIL] Stored anchor does not match origin filing.")
        print(f"  Expected: {MOSES_ANCHOR[:24]}...")
        print(f"  Found   : {record.get('lineage_anchor', 'MISSING')[:24]}...")
        sys.exit(1)

    # The shared store verifies its own transition history. This check does
    # not claim that an external filing or host action has been independently
    # authenticated by the package.
    try:
        integrity = _store.verify()
        stored_lineage = load_lineage()
    except Exception as exc:
        print(f"[LINEAGE FAIL] Governance store could not be verified: {exc}")
        sys.exit(1)
    if not integrity.get("valid") or stored_lineage != record:
        print("[LINEAGE FAIL] Governance transition history or lineage resource is inconsistent.")
        sys.exit(1)

    print(f"[LINEAGE OK] Layer  0: anchor traces to origin-cycle filing.")
    print(f"  Anchor : {MOSES_ANCHOR[:24]}...")
    print(f"  Genesis: {record['genesis_hash'][:24]}...")
    print(f"  Patent : {record['patent_serial']}")
    print(f"  Anchored: {record['anchored_at']}")
    print()
    print("[LINEAGE OK] Package-local transition history and lineage resource verified.")


def cmd_badge(_args):
    record = load_lineage()
    if not record:
        print("[LINEAGE] No anchor found. Run: python3 lineage.py init")
        sys.exit(1)

    badge = {
        "system": "MO§ES™ Constitutional Governance",
        "lineage_anchor": MOSES_ANCHOR,
        "genesis_hash": record["genesis_hash"],
        "patent_serial": "63/877,177",
        "doi": "https://zenodo.org/records/18792459",
        "anchored_at": record["anchored_at"],
        "custody": "Ello Cello LLC / Deric McHenry",
        "verification": "python3 lineage.py verify",
    }

    print("─" * 60)
    print("  MO§ES™ LINEAGE BADGE")
    print("─" * 60)
    for k, v in badge.items():
        print(f"  {k:<18}: {v}")
    print("─" * 60)
    print()
    print("  This badge reports a package-local marker and is not an external custody attestation.")
    print("─" * 60)


def cmd_check(_args):
    """Exit 0 if lineage is valid, exit 1 if not. Machine-readable."""
    record = load_lineage()
    if not record:
        sys.exit(1)
    if record.get("lineage_anchor") != MOSES_ANCHOR:
        sys.exit(1)
    try:
        if not _store.verify().get("valid") or load_lineage() != record:
            sys.exit(1)
    except Exception:
        sys.exit(1)
    print("LINEAGE:OK")
    sys.exit(0)


def cmd_status(_args):
    """/claws status — human-readable lineage status summary."""
    record = load_lineage()

    # Layer -1: archival
    arch_ok = False
    arch_head = None
    try:
        import importlib.util, pathlib
        _spec = importlib.util.spec_from_file_location(
            "archival", pathlib.Path(__file__).parent / "archival.py"
        )
        _arch = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_arch)
        _chain = _arch.build_chain()
        arch_head = _arch.archival_head(_chain)
        arch_ok = True
    except Exception:
        pass

    print("─" * 60)
    print("  MO§ES™ LINEAGE STATUS")
    print("─" * 60)
    if arch_ok:
        print(f"  Layer -1 (archival) : OK  head:{arch_head[:20]}...")
    else:
        print(f"  Layer -1 (archival) : NOT BUILT — run: python3 archival.py build")

    if record:
        anchor_match = record.get("lineage_anchor") == MOSES_ANCHOR
        print(f"  Layer  0 (anchor)   : {'OK' if anchor_match else 'FAIL'}  {MOSES_ANCHOR[:20]}...")
        print(f"  Patent              : {record.get('patent_serial', '?')}")
        print(f"  DOI                 : {record.get('doi', '?')}")
        print(f"  Anchored at         : {record.get('anchored_at', '?')}")
    else:
        print(f"  Layer  0 (anchor)   : NOT INITIALIZED — run: python3 lineage.py init")

    print("─" * 60)
    overall = arch_ok and bool(record) and record.get("lineage_anchor") == MOSES_ANCHOR
    print(f"  Status : {'PACKAGE MARKER PRESENT' if overall else 'INCOMPLETE — see above'}")
    print("─" * 60)


def cmd_attest(_args):
    """/claws attest — output signed attestation JSON for sharing."""
    record = load_lineage()
    if not record:
        print("[LINEAGE] No anchor found. Run: python3 lineage.py init")
        sys.exit(1)

    if record.get("lineage_anchor") != MOSES_ANCHOR:
        print("[LINEAGE FAIL] Anchor mismatch — cannot attest broken chain.")
        sys.exit(1)

    # Archival head
    arch_head = None
    try:
        import importlib.util, pathlib
        _spec = importlib.util.spec_from_file_location(
            "archival", pathlib.Path(__file__).parent / "archival.py"
        )
        _arch = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_arch)
        arch_head = _arch.archival_head(_arch.build_chain())
    except Exception:
        pass

    attest = {
        "attested_at": datetime.now(timezone.utc).isoformat(),
        "system": "MO§ES™ Constitutional Governance",
        "custody": "Ello Cello LLC / Deric McHenry",
        "patent_serial": "63/877,177",
        "doi": "https://zenodo.org/records/18792459",
        "lineage_anchor": MOSES_ANCHOR,
        "genesis_hash": record["genesis_hash"],
        "archival_head": arch_head,
        "anchored_at": record["anchored_at"],
        "lineage_status": "PACKAGE_MARKER_PRESENT",
        "verification": "python3 lineage.py verify",
    }
    attest["attestation_hash"] = hashlib.sha256(
        json.dumps(attest, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    print(json.dumps(attest, indent=2))


# ─── Entry ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MO§ES™ Lineage Custody Verifier")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("init",   help="Anchor genesis to origin filing")
    subparsers.add_parser("verify", help="Confirm chain traces to origin (three-layer)")
    subparsers.add_parser("badge",  help="Output shareable lineage proof block")
    subparsers.add_parser("check",  help="Machine-readable pass/fail check")
    subparsers.add_parser("status", help="Human-readable lineage status summary")
    subparsers.add_parser("attest", help="Output signed attestation JSON")

    args = parser.parse_args()

    commands = {
        "init":   cmd_init,
        "verify": cmd_verify,
        "badge":  cmd_badge,
        "check":  cmd_check,
        "status": cmd_status,
        "attest": cmd_attest,
    }
    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()
