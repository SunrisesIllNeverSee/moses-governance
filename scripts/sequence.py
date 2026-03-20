"""MO§ES™ Sequence Engine — Role ordering + hierarchy enforcement.

Manages Primary/Secondary/Observer hierarchy and sequence-ordered execution.
Agents respond in constitutional order, not by @mention parsing.

© 2026 Ello Cello LLC. All rights reserved.
Patent Pending: Serial No. 63/877,177
"""

import json
import sys
from pathlib import Path


ROLE_ORDER = {"Primary": 1, "Secondary": 2, "Observer": 3}
ROLE_AUTHORITY = {
    "Primary": {
        "authority": "Full — initiates analysis, sets direction, responds first",
        "can": ["initiate", "execute", "delegate", "decide"],
        "cannot": [],
    },
    "Secondary": {
        "authority": "Scoped — validates, challenges, extends Primary output",
        "can": ["validate", "challenge", "extend", "flag"],
        "cannot": ["repeat Primary", "initiate new threads", "override Primary"],
    },
    "Observer": {
        "authority": "Read-only — flags risks, gaps, inconsistencies",
        "can": ["observe", "flag", "report"],
        "cannot": ["initiate", "execute", "generate original analysis", "modify state"],
    },
}


def get_sequence(systems: list[dict]) -> list[dict]:
    """Return systems sorted by role hierarchy then explicit sequence number."""
    def sort_key(s):
        role = s.get("role", "Observer")
        seq = s.get("seq") or 99
        return (ROLE_ORDER.get(role, 99), seq)
    return sorted(systems, key=sort_key)


def next_in_sequence(systems: list[dict], last_responder: str | None) -> dict | None:
    """Given who just responded, return the next system in sequence."""
    ordered = get_sequence(systems)
    if not ordered:
        return None
    if last_responder is None:
        return ordered[0]
    for i, s in enumerate(ordered):
        if s.get("id") == last_responder or s.get("name") == last_responder:
            return ordered[i + 1] if i + 1 < len(ordered) else None
    return None


def get_role_instruction(role: str, sequence_position: int, total: int) -> str:
    """Generate behavioral instruction based on role assignment."""
    if role == "Primary":
        return (
            f"You are Primary (position {sequence_position}/{total}). "
            "Respond first. Set the analytical direction. "
            "Other systems will build on your response."
        )
    elif role == "Secondary":
        return (
            f"You are Secondary (position {sequence_position}/{total}). "
            "The Primary system has already responded. "
            "Build on, challenge, or extend their analysis. Do not repeat."
        )
    elif role == "Observer":
        return (
            f"You are Observer (position {sequence_position}/{total}). "
            "Read all responses. Flag inconsistencies, gaps, or risks. "
            "Do not generate original analysis."
        )
    return f"Role: {role} (position {sequence_position}/{total})."


def check_sequence_violation(agent_role: str, action: str) -> dict:
    """Check if an agent is attempting something outside its role authority."""
    spec = ROLE_AUTHORITY.get(agent_role, {})
    violations = []
    action_lower = action.lower()

    for forbidden in spec.get("cannot", []):
        if any(word in action_lower for word in forbidden.lower().split()):
            violations.append(f"{agent_role} cannot: {forbidden}")

    return {
        "permitted": len(violations) == 0,
        "role": agent_role,
        "violations": violations,
    }


# ── CLI Entry Point ────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MO§ES™ Sequence Engine CLI")
    subparsers = parser.add_subparsers(dest="command")

    # get_order — show sequence for active systems
    go = subparsers.add_parser("get_order", help="Show execution order for systems")
    go.add_argument("--state", default="./data/governance_state.json")

    # next — who responds next
    nx = subparsers.add_parser("next", help="Get next responder in sequence")
    nx.add_argument("--after", default=None, help="Name/ID of last responder")
    nx.add_argument("--state", default="./data/governance_state.json")

    # instruction — get role instruction for an agent
    ins = subparsers.add_parser("instruction", help="Get role instruction")
    ins.add_argument("role", help="Primary | Secondary | Observer")
    ins.add_argument("--position", type=int, default=1)
    ins.add_argument("--total", type=int, default=1)

    # check — check if action violates role constraints
    chk = subparsers.add_parser("check", help="Check action against role constraints")
    chk.add_argument("role", help="Agent role")
    chk.add_argument("action", help="Proposed action")

    args = parser.parse_args()

    if args.command == "get_order":
        # For now, show role hierarchy
        for role, order in sorted(ROLE_ORDER.items(), key=lambda x: x[1]):
            spec = ROLE_AUTHORITY[role]
            print(f"  {order}. {role} — {spec['authority']}")

    elif args.command == "next":
        print(json.dumps({"note": "Sequence requires active system list from runtime"}))

    elif args.command == "instruction":
        print(get_role_instruction(args.role, args.position, args.total))

    elif args.command == "check":
        result = check_sequence_violation(args.role, args.action)
        print(json.dumps(result, indent=2))

    else:
        parser.print_help()
