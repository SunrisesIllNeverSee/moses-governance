"""MO§ES™ Vault Engine — Document storage and governance context injection.

Manages vault documents that get injected into agent context.
Every load/unload is audited. Documents are categorized and tracked.

© 2026 Ello Cello LLC. All rights reserved.
Patent Pending: Serial No. 63/877,177
"""

import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "moses-governance-mcp"))
from governance.store import GovernanceStore, GovernanceStoreError, default_state_path

DEFAULT_STATE = str(default_state_path())

CATEGORIES = [
    "protocols",
    "patents",
    "preprints",
    "lineage",
    "personal",
    "professional",
    "business",
    "agents",
    "general",
]


def _load_state(state_path: str) -> dict:
    return GovernanceStore(os.path.expandvars(state_path)).read().state


def _save_state(state_path: str, state: dict):
    raise GovernanceStoreError("Direct vault snapshot writes are disabled; use a generation-checked mutation.")


def _transition(state_path: str, operation: str, docs: list[dict], expected_generation: int | None, expected_hash: str | None, detail: dict) -> dict:
    if expected_generation is None or expected_hash is None:
        raise GovernanceStoreError("Protected write requires expected_generation and expected_hash from governance status.")
    snap = GovernanceStore(os.path.expandvars(state_path)).transition(
        operation, updates={"vault_documents": docs}, expected_generation=expected_generation,
        expected_hash=expected_hash, actor="vault-cli", detail=detail,
    )
    return snap.public_metadata()


def load_document(name: str, category: str = "general", content: str = "", file_path: str | None = None, state_path: str = DEFAULT_STATE, expected_generation: int | None = None, expected_hash: str | None = None) -> dict:
    """Load a document into the active vault."""
    s = _load_state(state_path)
    if "vault_documents" not in s:
        s["vault_documents"] = []

    # Read from file if provided
    if file_path and os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

    # Remove existing with same name, then add
    s["vault_documents"] = [d for d in s["vault_documents"] if d.get("name") != name]
    s["vault_documents"].append({"name": name, "category": category, "content": content})
    metadata = _transition(state_path, "vault.load", s["vault_documents"], expected_generation, expected_hash, {"name": name, "category": category})

    return {"loaded": name, "category": category, "vault_count": len(s["vault_documents"]), **metadata}


def unload_document(name: str, state_path: str = DEFAULT_STATE, expected_generation: int | None = None, expected_hash: str | None = None) -> dict:
    """Remove a document from the active vault."""
    s = _load_state(state_path)
    before = len(s.get("vault_documents", []))
    s["vault_documents"] = [d for d in s.get("vault_documents", []) if d.get("name") != name]
    after = len(s["vault_documents"])
    if after == before:
        return {"error": f"Document '{name}' not found in vault"}
    metadata = _transition(state_path, "vault.unload", s["vault_documents"], expected_generation, expected_hash, {"name": name})
    return {"unloaded": name, "vault_count": after, **metadata}


def list_documents(state_path: str = DEFAULT_STATE) -> list[dict]:
    """List all loaded vault documents."""
    s = _load_state(state_path)
    return s.get("vault_documents", [])


def get_context_payload(state_path: str = DEFAULT_STATE) -> list[dict]:
    """Return vault documents formatted for context injection."""
    docs = list_documents(state_path)
    return [
        {"name": d.get("name", ""), "category": d.get("category", "general"), "content": d.get("content", "")}
        for d in docs
    ]


def clear_vault(state_path: str = DEFAULT_STATE, expected_generation: int | None = None, expected_hash: str | None = None) -> dict:
    """Remove all documents from the vault."""
    s = _load_state(state_path)
    count = len(s.get("vault_documents", []))
    s["vault_documents"] = []
    metadata = _transition(state_path, "vault.clear", [], expected_generation, expected_hash, {"cleared": count})
    return {"cleared": count, "vault_count": 0, **metadata}


# ── CLI Entry Point ────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MO§ES™ Vault Engine CLI")
    subparsers = parser.add_subparsers(dest="command")

    # load
    lo = subparsers.add_parser("load", help="Load a document into the vault")
    lo.add_argument("name", help="Document name/identifier")
    lo.add_argument("--category", default="general", help="Document category")
    lo.add_argument("--content", default="", help="Document content (inline)")
    lo.add_argument("--file", default=None, help="Path to document file")
    lo.add_argument("--state", default=DEFAULT_STATE)
    lo.add_argument("--expected-generation", type=int, required=True)
    lo.add_argument("--expected-hash", required=True)

    # unload
    ul = subparsers.add_parser("unload", help="Remove a document from the vault")
    ul.add_argument("name", help="Document name to remove")
    ul.add_argument("--state", default=DEFAULT_STATE)
    ul.add_argument("--expected-generation", type=int, required=True)
    ul.add_argument("--expected-hash", required=True)

    # list
    ls = subparsers.add_parser("list", help="List loaded vault documents")
    ls.add_argument("--state", default=DEFAULT_STATE)

    # context
    ctx = subparsers.add_parser("context", help="Get vault context payload for injection")
    ctx.add_argument("--state", default=DEFAULT_STATE)

    # clear
    cl = subparsers.add_parser("clear", help="Clear all vault documents")
    cl.add_argument("--state", default=DEFAULT_STATE)
    cl.add_argument("--expected-generation", type=int, required=True)
    cl.add_argument("--expected-hash", required=True)

    # categories
    subparsers.add_parser("categories", help="List available document categories")

    args = parser.parse_args()

    if args.command == "load":
        result = load_document(args.name, args.category, args.content, args.file, args.state, args.expected_generation, args.expected_hash)
        print(json.dumps(result))

    elif args.command == "unload":
        result = unload_document(args.name, args.state, args.expected_generation, args.expected_hash)
        print(json.dumps(result))

    elif args.command == "list":
        docs = list_documents(args.state)
        if docs:
            for d in docs:
                print(f"  [{d.get('category', 'general')}] {d.get('name', '')}")
        else:
            print("  Vault is empty.")

    elif args.command == "context":
        payload = get_context_payload(args.state)
        print(json.dumps(payload, indent=2))

    elif args.command == "clear":
        result = clear_vault(args.state, args.expected_generation, args.expected_hash)
        print(json.dumps(result))

    elif args.command == "categories":
        for cat in CATEGORIES:
            print(f"  {cat}")

    else:
        parser.print_help()
