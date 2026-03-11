"""
MO§ES™ MCP Governance Server — server.py
© 2026 Ello Cello LLC — Patent pending: Serial No. 63/877,177

FastMCP server exposing 13 governance, vault, and audit tools.
Transport: stdio (local dev / Claude Code)
State:     in-memory GovernanceState per session + persistent JSONL audit ledger

Run:
    python3 server.py

Connect via .mcp.json (Claude Code) — see repo root.
"""

import json
import os
import uuid
from pathlib import Path

from fastmcp import FastMCP, Context

from governance.engine import (
    GovernanceState,
    translate_mode,
    translate_posture,
    get_role_instruction,
    assemble_context,
    check_action_permitted,
    resolve_mode,
    MODES,
    POSTURES,
    ROLES,
)
from governance.audit import (
    AuditLedger,
    hash_governance_state,
    hash_conversation,
    format_for_onchain,
)

# ---------------------------------------------------------------------------
# Server init
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="moses-governance",
    version="1.1.0",
    instructions="Constitutional governance engine for AI agents — MO§ES™",
)

# ---------------------------------------------------------------------------
# Session state (in-memory dict per session)
# ---------------------------------------------------------------------------

_sessions: dict[str, GovernanceState] = {}
_ledgers: dict[str, AuditLedger] = {}

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

GOVERNANCE_STATE_FILE = DATA_DIR / "governance_state.json"


def _get_session(session_id: str) -> GovernanceState:
    """Return existing GovernanceState or create default for session_id."""
    if session_id not in _sessions:
        _sessions[session_id] = GovernanceState()
    return _sessions[session_id]


def _get_ledger(session_id: str) -> AuditLedger:
    """Return existing AuditLedger or create one for session_id."""
    if session_id not in _ledgers:
        ledger_path = DATA_DIR / f"audit_{session_id}.jsonl"
        _ledgers[session_id] = AuditLedger(ledger_path)
    return _ledgers[session_id]


def _resolve_session(ctx: Context | None) -> str:
    """Resolve session ID from MCP context, or use 'default'."""
    try:
        if ctx and hasattr(ctx, "session_id") and ctx.session_id:
            return str(ctx.session_id)
    except Exception:
        pass
    return "default"


def _persist_state(gs: GovernanceState):
    """Write governance state snapshot to governance_state.json."""
    import dataclasses
    snapshot = dataclasses.asdict(gs)
    GOVERNANCE_STATE_FILE.write_text(json.dumps(snapshot, indent=2))


# ---------------------------------------------------------------------------
# GOVERNANCE TOOLS
# ---------------------------------------------------------------------------

@mcp.tool()
def govern_set_mode(mode: str, ctx: Context | None = None) -> dict:
    """
    Set the active governance mode.
    Accepts canonical names or aliases (idk, high-security, self-growth, etc.)
    Updates in-memory GovernanceState and writes governance_state.json.
    Returns: {"mode": canonical_name, "constraints": [...], "prohibited": [...]}
    """
    session_id = _resolve_session(ctx)
    gs = _get_session(session_id)

    canonical = resolve_mode(mode)
    gs.mode = canonical
    _persist_state(gs)

    result = {"mode": canonical, **translate_mode(canonical)}
    _get_ledger(session_id).log_action(
        component="govern",
        action="set_mode",
        detail={"mode": canonical},
        governance_mode=gs.mode,
        posture=gs.posture,
        role=gs.role,
    )
    return result


@mcp.tool()
def govern_set_posture(posture: str, ctx: Context | None = None) -> dict:
    """
    Set operational posture: SCOUT | DEFENSE | OFFENSE.
    SCOUT = read-only, no state changes.
    DEFENSE = protect assets, outbound requires confirmation.
    OFFENSE = execute within governance constraints.
    Returns: {"posture": str, "behavior": str, "transaction_policy": str}
    """
    session_id = _resolve_session(ctx)
    gs = _get_session(session_id)

    canonical = posture.strip().upper()
    result = {"posture": canonical, **translate_posture(canonical)}
    gs.posture = canonical
    _persist_state(gs)

    _get_ledger(session_id).log_action(
        component="govern",
        action="set_posture",
        detail={"posture": gs.posture},
        governance_mode=gs.mode,
        posture=gs.posture,
        role=gs.role,
    )
    return result


@mcp.tool()
def govern_set_role(role: str, ctx: Context | None = None) -> dict:
    """
    Set hierarchy role: Primary | Secondary | Observer.
    Primary leads. Secondary validates. Observer flags only.
    Returns: {"role": str, "authority": str, "instruction": str, "constraints": [...]}
    """
    session_id = _resolve_session(ctx)
    gs = _get_session(session_id)

    canonical = role.strip().title()
    result = {"role": canonical, **get_role_instruction(canonical)}
    gs.role = canonical
    _persist_state(gs)

    _get_ledger(session_id).log_action(
        component="govern",
        action="set_role",
        detail={"role": gs.role},
        governance_mode=gs.mode,
        posture=gs.posture,
        role=gs.role,
    )
    return result


@mcp.tool()
def govern_check_action(action_description: str, ctx: Context | None = None) -> dict:
    """
    Check if a proposed action is permitted under current governance.
    Uses concept extraction + rule-driven evaluation against active mode's prohibited list.
    Returns: {"permitted": bool, "reason": str, "triggered_rules": [...], "conditions": [...]}
    """
    session_id = _resolve_session(ctx)
    gs = _get_session(session_id)

    result = check_action_permitted(action_description, gs)

    _get_ledger(session_id).log_action(
        component="govern",
        action="check_action",
        detail={"action_description": action_description, "permitted": result["permitted"]},
        governance_mode=gs.mode,
        posture=gs.posture,
        role=gs.role,
    )
    return result


@mcp.tool()
def govern_get_status(ctx: Context | None = None) -> dict:
    """
    Return full current GovernanceState.
    Returns: {"mode": str, "posture": str, "role": str, "vault_documents": [...], ...all fields}
    """
    session_id = _resolve_session(ctx)
    gs = _get_session(session_id)

    import dataclasses
    status = dataclasses.asdict(gs)
    status["vault_count"] = len(gs.vault_documents)
    return status


@mcp.tool()
def govern_assemble_context(
    messages: list[dict],
    agent_name: str = "agent",
    previous_responses: list[dict] | None = None,
    ctx: Context | None = None,
) -> dict:
    """
    Build the full governed context payload for an agent.
    This is the core IP — every agent read passes through here.
    Returns full governed payload: constitutional_governance, role_assignment,
    user_profile, vault_context, messages, [prior_responses if Secondary/Observer]
    """
    session_id = _resolve_session(ctx)
    gs = _get_session(session_id)
    gs.agent_name = agent_name

    payload = assemble_context(gs, messages, agent_name, previous_responses)

    _get_ledger(session_id).log_action(
        component="govern",
        action="assemble_context",
        detail={"agent_name": agent_name, "message_count": len(messages)},
        governance_mode=gs.mode,
        posture=gs.posture,
        role=gs.role,
        agent=agent_name,
    )
    return payload


# ---------------------------------------------------------------------------
# VAULT TOOLS
# ---------------------------------------------------------------------------

@mcp.tool()
def vault_load(name: str, content: str, category: str = "general", ctx: Context | None = None) -> dict:
    """
    Load a governance document into the active vault.
    Injected into every governed context via assemble_context().
    Returns: {"loaded": name, "vault_count": int}
    """
    session_id = _resolve_session(ctx)
    gs = _get_session(session_id)

    # Replace if name already exists
    gs.vault_documents = [d for d in gs.vault_documents if d.get("name") != name]
    gs.vault_documents.append({"name": name, "content": content, "category": category})
    _persist_state(gs)

    _get_ledger(session_id).log_action(
        component="vault",
        action="load",
        detail={"name": name, "category": category},
        governance_mode=gs.mode,
        posture=gs.posture,
        role=gs.role,
    )
    return {"loaded": name, "vault_count": len(gs.vault_documents)}


@mcp.tool()
def vault_list(ctx: Context | None = None) -> dict:
    """
    List all documents currently in the vault.
    Returns: {"documents": [{"name": str, "category": str}]}
    """
    session_id = _resolve_session(ctx)
    gs = _get_session(session_id)

    return {
        "documents": [
            {"name": d["name"], "category": d.get("category", "general")}
            for d in gs.vault_documents
        ]
    }


@mcp.tool()
def vault_clear(ctx: Context | None = None) -> dict:
    """
    Clear all documents from the vault.
    Returns: {"cleared": int}
    """
    session_id = _resolve_session(ctx)
    gs = _get_session(session_id)

    count = len(gs.vault_documents)
    gs.vault_documents = []
    _persist_state(gs)

    _get_ledger(session_id).log_action(
        component="vault",
        action="clear",
        detail={"cleared": count},
        governance_mode=gs.mode,
        posture=gs.posture,
        role=gs.role,
    )
    return {"cleared": count}


# ---------------------------------------------------------------------------
# AUDIT TOOLS
# ---------------------------------------------------------------------------

@mcp.tool()
def audit_log(
    component: str,
    action: str,
    detail: dict,
    agent: str = "",
    ctx: Context | None = None,
) -> dict:
    """
    Append a governed action to the audit ledger.
    Automatically captures active mode/posture/role from GovernanceState.
    Returns: {"id": int, "hash": str, "iso_time": str}
    """
    session_id = _resolve_session(ctx)
    gs = _get_session(session_id)

    return _get_ledger(session_id).log_action(
        component=component,
        action=action,
        detail=detail,
        governance_mode=gs.mode,
        posture=gs.posture,
        role=gs.role,
        agent=agent,
    )


@mcp.tool()
def audit_verify(ctx: Context | None = None) -> dict:
    """
    Verify the entire audit chain integrity.
    Returns: {"valid": bool, "entries_checked": int, "first_failure": int | None}
    """
    session_id = _resolve_session(ctx)
    return _get_ledger(session_id).verify_integrity()


@mcp.tool()
def audit_recent(n: int = 10, ctx: Context | None = None) -> dict:
    """
    Return the last N audit entries.
    Returns: {"entries": [...], "count": int}
    """
    session_id = _resolve_session(ctx)
    entries = _get_ledger(session_id).recent(n)
    return {"entries": entries, "count": len(entries)}


@mcp.tool()
def audit_hash_session(messages: list[dict], ctx: Context | None = None) -> dict:
    """
    Generate all three session hashes.
    ① Config fingerprint (governance state)
    ② Content integrity (conversation)
    ③ Onchain anchor (Solana memo format)
    Returns: {"hash_config": str, "hash_content": str, "hash_onchain": str}
    """
    session_id = _resolve_session(ctx)
    gs = _get_session(session_id)

    # vault_docs: list[str] (names only), systems: list[dict] (not in GovernanceState — pass empty)
    vault_doc_names = [d.get("name", "") for d in gs.vault_documents]
    hash_config = hash_governance_state(
        mode=gs.mode,
        posture=gs.posture,
        role=gs.role,
        vault_docs=vault_doc_names,
        systems=[],
    )
    hash_content = hash_conversation(messages)
    hash_onchain = format_for_onchain(hash_config, hash_content, session_id)

    return {
        "hash_config": hash_config,
        "hash_content": hash_content,
        "hash_onchain": hash_onchain,
    }


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()  # stdio transport — for Claude Code local dev
