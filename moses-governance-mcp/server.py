"""
MO§ES™ MCP Governance Server — server.py
© 2026 Ello Cello LLC — Patent pending: Serial No. 63/877,177

FastMCP server exposing 16 governance, vault, and audit tools.
Transport: stdio (local dev / Claude Code)
State:     in-memory GovernanceState per session + persistent JSONL audit ledger

Tools (v1.1):
  Core (13): govern_set_mode, govern_set_posture, govern_set_role,
             govern_check_action, govern_get_status, govern_assemble_context,
             vault_load, vault_list, vault_clear,
             audit_log, audit_verify, audit_recent, audit_hash_session
  v1.1 (+3): govern_check_commitment, govern_oracle_verify, govern_run_swarm_round

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
from governance.store import GovernanceStore, GovernanceStoreError
from governance.commitment import evaluate_commitment, score_commitment
from governance.oracle import grok_verify_sync
from governance.swarm import run_swarm_round, SwarmConfig
from governance.meta import (
    analyze_audit_trail,
    apply_amendment,
    list_proposals,
    get_proposal,
    reject_proposal,
    rollback_amendment,
    constitution_status,
)

# ---------------------------------------------------------------------------
# Server init
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="moses-governance",
    version="1.2.0",
    instructions="Constitutional governance engine for AI agents — MO§ES™",
)

# ---------------------------------------------------------------------------
# Session state (in-memory dict per session)
# ---------------------------------------------------------------------------

_ledgers: dict[str, AuditLedger] = {}

_store = GovernanceStore()
DATA_DIR = _store.data_root
DATA_DIR.mkdir(parents=True, exist_ok=True)
GOVERNANCE_STATE_FILE = _store.state_path


def _get_session(session_id: str) -> GovernanceState:
    """Load the latest verified shared state; MCP sessions never cache authority."""
    snapshot = _store.read()
    return GovernanceState(**snapshot.state)


def _commit_state(session_id: str, operation: str, updates: dict, expected_generation: int | None, expected_hash: str | None, detail: dict | None = None):
    if expected_generation is None or expected_hash is None:
        raise GovernanceStoreError("Protected write requires expected_generation and expected_hash from govern_get_status.")
    result = _store.transition(
        operation, updates=updates, expected_generation=expected_generation,
        expected_hash=expected_hash, actor=f"mcp-session:{session_id}", detail=detail or {},
    )
    return result


def _get_ledger(session_id: str) -> AuditLedger:
    """Return existing AuditLedger or create one for session_id."""
    if session_id not in _ledgers:
        ledger_path = DATA_DIR / "audit_ledger.jsonl"
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


# ---------------------------------------------------------------------------
# GOVERNANCE TOOLS
# ---------------------------------------------------------------------------

@mcp.tool()
def govern_set_mode(mode: str, expected_generation: int | None = None, expected_hash: str | None = None, ctx: Context | None = None) -> dict:
    """
    Set the active governance mode.
    Accepts canonical names or aliases (idk, high-security, self-growth, etc.)
    Updates in-memory GovernanceState and writes governance_state.json.
    Returns: {"mode": canonical_name, "constraints": [...], "prohibited": [...]}
    """
    session_id = _resolve_session(ctx)
    gs = _get_session(session_id)
    canonical = resolve_mode(mode)
    snap = _commit_state(session_id, "govern.set_mode", {"mode": canonical}, expected_generation, expected_hash, {"mode": canonical})
    gs = GovernanceState(**snap.state)

    result = {"mode": canonical, **translate_mode(canonical), **snap.public_metadata()}
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
def govern_set_posture(posture: str, expected_generation: int | None = None, expected_hash: str | None = None, ctx: Context | None = None) -> dict:
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
    if canonical not in POSTURES:
        raise GovernanceStoreError(f"Unsupported posture: {canonical}")
    snap = _commit_state(session_id, "govern.set_posture", {"posture": canonical}, expected_generation, expected_hash, {"posture": canonical})
    gs = GovernanceState(**snap.state)
    result.update(snap.public_metadata())

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
def govern_set_role(role: str, expected_generation: int | None = None, expected_hash: str | None = None, ctx: Context | None = None) -> dict:
    """
    Set hierarchy role: Primary | Secondary | Observer.
    Primary leads. Secondary validates. Observer flags only.
    Returns: {"role": str, "authority": str, "instruction": str, "constraints": [...]}
    """
    session_id = _resolve_session(ctx)
    gs = _get_session(session_id)

    canonical = role.strip().title()
    result = {"role": canonical, **get_role_instruction(canonical)}
    if canonical not in ROLES:
        raise GovernanceStoreError(f"Unsupported role: {canonical}")
    snap = _commit_state(session_id, "govern.set_role", {"role": canonical}, expected_generation, expected_hash, {"role": canonical})
    gs = GovernanceState(**snap.state)
    result.update(snap.public_metadata())

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
    del ctx
    report = _store.inspect()
    if not report.get("valid"):
        return {"store_valid": False, "reason": report.get("reason", "Governance store verification failed."),
                "unverified_snapshot": report.get("unverified_snapshot"), "integrity": report.get("integrity")}
    status = dict(report["state"])
    status["vault_count"] = len(status.get("vault_documents", []))
    status.update({key: report[key] for key in ("generation", "state_hash", "transition_hash")})
    status["store_valid"] = True
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
def vault_load(name: str, content: str, category: str = "general", expected_generation: int | None = None, expected_hash: str | None = None, ctx: Context | None = None) -> dict:
    """
    Load a governance document into the active vault.
    Injected into every governed context via assemble_context().
    Returns: {"loaded": name, "vault_count": int}
    """
    session_id = _resolve_session(ctx)
    gs = _get_session(session_id)

    # Replace if name already exists
    docs = [d for d in gs.vault_documents if d.get("name") != name]
    docs.append({"name": name, "content": content, "category": category})
    snap = _commit_state(session_id, "vault.load", {"vault_documents": docs}, expected_generation, expected_hash, {"name": name, "category": category})
    gs = GovernanceState(**snap.state)

    _get_ledger(session_id).log_action(
        component="vault",
        action="load",
        detail={"name": name, "category": category},
        governance_mode=gs.mode,
        posture=gs.posture,
        role=gs.role,
    )
    return {"loaded": name, "vault_count": len(gs.vault_documents), **snap.public_metadata()}


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
def vault_clear(expected_generation: int | None = None, expected_hash: str | None = None, ctx: Context | None = None) -> dict:
    """
    Clear all documents from the vault.
    Returns: {"cleared": int}
    """
    session_id = _resolve_session(ctx)
    gs = _get_session(session_id)

    count = len(gs.vault_documents)
    snap = _commit_state(session_id, "vault.clear", {"vault_documents": []}, expected_generation, expected_hash, {"cleared": count})
    gs = GovernanceState(**snap.state)

    _get_ledger(session_id).log_action(
        component="vault",
        action="clear",
        detail={"cleared": count},
        governance_mode=gs.mode,
        posture=gs.posture,
        role=gs.role,
    )
    return {"cleared": count, **snap.public_metadata()}


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
# v1.1 TOOLS — Commitment, Oracle, Swarm
# ---------------------------------------------------------------------------

@mcp.tool()
def govern_check_commitment(
    message: str,
    history: list[str] | None = None,
    block_threshold: float = 40.0,
    ctx: Context | None = None,
) -> dict:
    """
    Check semantic commitment drift between a message and conversation history.
    Based on the 2026 McHenry Conservation Law.
    Drift < 5% = green (preserved). Drift > threshold = blocked.
    Returns: {"drift_score": float, "drift_level": str, "commitment_preserved": bool,
              "reason": str, "conditions": [...], "scorer": str}
    """
    session_id = _resolve_session(ctx)
    gs = _get_session(session_id)

    result = evaluate_commitment(message, history=history, block_threshold=block_threshold)

    _get_ledger(session_id).log_action(
        component="commitment",
        action="check_commitment",
        detail={
            "drift_score": result["drift_score"],
            "drift_level": result["drift_level"],
            "commitment_preserved": result["commitment_preserved"],
        },
        governance_mode=gs.mode,
        posture=gs.posture,
        role=gs.role,
    )
    return result


@mcp.tool()
def govern_oracle_verify(
    message: str,
    context: str = "",
    ctx: Context | None = None,
) -> dict:
    """
    Send message to Grok Oracle for independent commitment verification.
    Falls back gracefully if XAI_GROK_API_KEY is not set.
    Returns: {"preserves_commitment": bool, "explanation": str, "source": str}
    """
    session_id = _resolve_session(ctx)
    gs = _get_session(session_id)

    result = grok_verify_sync(
        message=message,
        context=context or f"Governance mode: {gs.mode} | Posture: {gs.posture} | Role: {gs.role}",
    )

    _get_ledger(session_id).log_action(
        component="oracle",
        action="oracle_verify",
        detail={
            "preserves_commitment": result["preserves_commitment"],
            "source": result["source"],
        },
        governance_mode=gs.mode,
        posture=gs.posture,
        role=gs.role,
    )
    return result


@mcp.tool()
def govern_run_swarm_round(
    task: str,
    primary_output: str = "",
    secondary_output: str = "",
    history: list[str] | None = None,
    drift_block_threshold: float = 75.0,
    use_oracle: bool = False,
    ctx: Context | None = None,
) -> dict:
    """
    Run a full governance-enforced swarm round: Primary → Secondary → Observer.
    Enforces commitment conservation between steps.
    Grok Oracle final gate is optional (set use_oracle=True + XAI_GROK_API_KEY).

    Pass primary_output and secondary_output as pre-generated text (from your agents).
    The server enforces the constitutional checks — commitment scoring, governance
    pre-flight, oracle gate — and returns the full verdict.

    drift_block_threshold: float (default 75.0) — drift % above which Secondary vetoes.
    Tune down for stricter sessions (e.g. High Security: 30.0).

    Returns: {"approved": bool, "output": str, "drift_score": float,
              "commitment_preserved": bool, "oracle": dict, "blocked": bool,
              "block_reason": str | None, "steps": [...]}
    """
    session_id = _resolve_session(ctx)
    gs = _get_session(session_id)

    # Build role handlers from provided outputs (or placeholder stubs)
    def make_handler(output: str):
        def handler(role: str, input_text: str) -> str:
            if output:
                return output
            raise NotImplementedError(f"No output provided for {role}")
        return handler

    role_handlers = {
        "Primary": make_handler(primary_output),
        "Secondary": make_handler(secondary_output),
        "Observer": make_handler(""),  # Observer always uses placeholder — flags from full context
    }

    cfg = SwarmConfig(
        drift_block_threshold=drift_block_threshold,
        use_oracle=use_oracle,
    )

    result = run_swarm_round(
        task=task,
        governance=gs,
        role_handlers=role_handlers,
        history=history,
        config=cfg,
    )

    _get_ledger(session_id).log_action(
        component="swarm",
        action="swarm_round",
        detail={
            "task_len": len(task),
            "approved": result["approved"],
            "blocked": result["blocked"],
            "drift_score": result["drift_score"],
            "block_reason": result.get("block_reason"),
        },
        governance_mode=gs.mode,
        posture=gs.posture,
        role=gs.role,
    )
    return result


# ---------------------------------------------------------------------------
# v1.2 TOOLS — Meta-Governance / Constitutional Amendment Protocol
# ---------------------------------------------------------------------------

@mcp.tool()
def meta_analyze_trail(
    timeframe: str = "week",
    focus: list[str] | None = None,
    min_confidence: float = 0.8,
    exclude_tags: list[str] | None = None,
    expected_generation: int | None = None,
    expected_hash: str | None = None,
    ctx: Context | None = None,
) -> dict:
    """
    Analyze the audit trail and generate constitutional amendment proposals.
    The constitution reads its own history and proposes improvements.

    timeframe:     "day" | "week" | "month" | "all"
    focus:         ["modes", "postures", "roles"] — which dimensions to analyze
    min_confidence: 0.0–1.0 — minimum confidence to emit a proposal
    exclude_tags:  Session tags to exclude from analysis (e.g. ["test", "dev", "ci"]).
                   Entries logged with {"session_tag": "test"} in their detail dict
                   will be excluded, preventing acceptance-test traffic from generating
                   false amendment proposals. Always pass ["test"] for production analysis.

    Returns: {"proposals": [...], "entries_analyzed": int, "entries_excluded_by_tag": int,
              "analysis_summary": str}
    """
    session_id = _resolve_session(ctx)
    gs = _get_session(session_id)
    focus = focus or ["modes", "postures", "roles"]

    result = analyze_audit_trail(
        timeframe=timeframe,
        focus=focus,
        min_confidence=min_confidence,
        ledger_name="audit_ledger.jsonl",
        exclude_tags=exclude_tags or [],
        expected_generation=expected_generation,
        expected_hash=expected_hash,
    )

    _get_ledger(session_id).log_action(
        component="meta",
        action="analyze_trail",
        detail={
            "timeframe": timeframe,
            "entries_analyzed": result["entries_analyzed"],
            "entries_excluded_by_tag": result.get("entries_excluded_by_tag", 0),
            "exclude_tags": exclude_tags or [],
            "proposals_generated": len(result["proposals"]),
        },
        governance_mode=gs.mode,
        posture=gs.posture,
        role=gs.role,
    )
    return result


@mcp.tool()
def meta_list_proposals(status: str = "pending", ctx: Context | None = None) -> dict:
    """
    List constitutional amendment proposals by status.
    status: "pending" | "approved" | "rejected"

    Returns: {"proposals": [...], "count": int, "status": str}
    """
    return list_proposals(status)


@mcp.tool()
def meta_apply_amendment(
    proposal_id: str,
    operator_signature: str,
    expected_generation: int | None = None,
    expected_hash: str | None = None,
    ctx: Context | None = None,
) -> dict:
    """
    Apply a pending amendment to the constitution. Atomic write + cryptographic signing.
    Requires operator_signature (non-empty string). Bumps constitution version.
    Moves proposal from pending → approved. Appends to amendments.jsonl.

    Returns: {"success": bool, "new_version": str, "constitution_hash": str, "message": str}
    """
    del proposal_id, operator_signature, expected_generation, expected_hash, ctx
    return {"success": False, "message": "Privileged approval is disabled: no trusted operator identity provider is configured. The requesting model cannot mint approval."}


@mcp.tool()
def meta_reject_proposal(
    proposal_id: str,
    reason: str,
    expected_generation: int | None = None,
    expected_hash: str | None = None,
    ctx: Context | None = None,
) -> dict:
    """
    Reject a pending amendment proposal with a reason.
    Moves proposal from pending → rejected.

    Returns: {"success": bool, "message": str}
    """
    session_id = _resolve_session(ctx)
    if expected_generation is None or expected_hash is None:
        return {"success": False, "message": "Protected write requires expected_generation and expected_hash from govern_get_status."}
    proposal = get_proposal(proposal_id)
    if not proposal:
        return {"success": False, "message": f"Proposal '{proposal_id}' was not found."}
    proposal["status"] = "rejected"
    proposal["rejection_reason"] = reason
    try:
        snap = _store.transition("meta.reject_proposal", expected_generation=expected_generation, expected_hash=expected_hash,
            resource_updates={f"proposals/rejected/{proposal_id}.json": json.dumps(proposal, ensure_ascii=False, indent=2), f"proposals/pending/{proposal_id}.json": None},
            actor=f"mcp-session:{session_id}", detail={"proposal_id": proposal_id, "reason": reason})
    except GovernanceStoreError as exc:
        return {"success": False, "message": str(exc)}
    return {"success": True, "message": f"Proposal '{proposal_id}' rejected.", **snap.public_metadata()}


@mcp.tool()
def meta_constitution_status(ctx: Context | None = None) -> dict:
    """
    Return full meta-governance status: constitution version, signature,
    amendment count, proposal counts, and core principles status.

    Returns: {"constitution_version": str, "constitution_signature": str,
              "amendment_count": int, "proposals": {...}, "core_principles_count": int}
    """
    return constitution_status()


@mcp.tool()
def meta_rollback_amendment(
    amendment_id: str,
    operator_signature: str,
    reason: str,
    ctx: Context | None = None,
) -> dict:
    """
    Emergency operator tool: reverse an applied amendment.

    Records a rollback entry in amendments.jsonl, moves the approved proposal
    to rejected/, and returns a warning reminding the operator to verify that
    constitution.json content was manually restored to the correct prior state.

    IMPORTANT: This tool does NOT automatically rewrite constitution.json content.
    The operator must edit constitution.json directly and re-sign it if the
    amendment modified the document body. Use meta_constitution_status() to
    confirm state after rollback.

    Args:
        amendment_id: ID of the amendment to roll back (from amendments.jsonl)
        operator_signature: Authorization string (non-empty required)
        reason: Human-readable reason for the rollback

    Returns: {"success": bool, "message": str, "warning": str}
    """
    del amendment_id, operator_signature, reason, ctx
    return {"success": False, "message": "Privileged approval is disabled: no trusted operator identity provider is configured. The requesting model cannot mint approval."}


# ---------------------------------------------------------------------------
# Operator Signature Helper
# ---------------------------------------------------------------------------

# No callable approval-minting tool is exposed to the requesting model. A
# trusted operator identity/credential integration is required before approval.


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()  # stdio transport — for Claude Code local dev
