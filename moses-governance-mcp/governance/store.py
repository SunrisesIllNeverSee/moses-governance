"""Transactional, project-local governance state and transition history.

SQLite is the canonical store. ``governance_state.json`` and the legacy
constitution/proposal files are compatibility exports. State and transition
history are committed in one SQLite transaction; callers must supply the
generation and state hash they read before proposing a write.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

GENESIS_HASH = "0" * 64
_STATE_METADATA_KEY = "_governance_store"
_DEFAULT_STATE = {
    "mode": "None (Unrestricted)",
    "posture": "SCOUT",
    "role": "Primary",
    "reasoning_mode": "Deductive",
    "reasoning_depth": "MODERATE",
    "response_style": "Direct",
    "output_format": "Conversational",
    "narrative_strength": 0.5,
    "expertise_level": "Expert",
    "interaction_mode": "Executing",
    "domain": "General",
    "communication_pref": "Concise",
    "goal": "Tactical Execution",
    "vault_documents": [],
    "agent_name": "",
}
_ALLOWED_STATE_FIELDS = frozenset(_DEFAULT_STATE)


class GovernanceStoreError(RuntimeError):
    """Base error for invalid or unavailable governance state."""


class StaleStateError(GovernanceStoreError):
    """The caller's snapshot is no longer current."""


class CorruptStoreError(GovernanceStoreError):
    """The canonical state or transition chain failed verification."""


@dataclass(frozen=True)
class StateSnapshot:
    state: dict[str, Any]
    generation: int
    state_hash: str
    transition_hash: str
    projection_error: str | None = None

    def public_metadata(self) -> dict[str, Any]:
        metadata = {
            "generation": self.generation,
            "state_hash": self.state_hash,
            "transition_hash": self.transition_hash,
        }
        if self.projection_error:
            metadata["projection_warning"] = self.projection_error
        return metadata


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def digest_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def default_state_path() -> Path:
    configured = os.environ.get("MOSES_GOVERNANCE_STATE_FILE")
    if configured:
        return Path(os.path.expandvars(configured)).expanduser().resolve()
    return (Path(__file__).resolve().parent.parent / "data" / "governance_state.json")


class GovernanceStore:
    """One transactional store shared by MCP, hooks, and supported CLIs."""

    def __init__(self, state_path: str | Path | None = None):
        self.state_path = Path(state_path).expanduser().resolve() if state_path else default_state_path()
        self.data_root = self.state_path.parent.resolve()
        self.db_path = self.state_path.with_suffix(self.state_path.suffix + ".sqlite3")

    def _connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(self.db_path, timeout=15.0, isolation_level=None)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA busy_timeout = 15000")
        con.execute("PRAGMA foreign_keys = ON")
        con.execute("PRAGMA journal_mode = WAL")
        con.execute("PRAGMA synchronous = FULL")
        self._initialize(con)
        return con

    def _initialize(self, con: sqlite3.Connection) -> None:
        con.execute("BEGIN IMMEDIATE")
        try:
            con.execute(
                "CREATE TABLE IF NOT EXISTS governance_state ("
                "singleton INTEGER PRIMARY KEY CHECK(singleton = 1), "
                "generation INTEGER NOT NULL, state_json TEXT NOT NULL, "
                "state_hash TEXT NOT NULL, transition_hash TEXT NOT NULL)"
            )
            con.execute(
                "CREATE TABLE IF NOT EXISTS transitions ("
                "generation INTEGER PRIMARY KEY, record_json TEXT NOT NULL, "
                "transition_hash TEXT NOT NULL UNIQUE)"
            )
            con.execute(
                "CREATE TABLE IF NOT EXISTS resources ("
                "path TEXT PRIMARY KEY, content BLOB NOT NULL, updated_at REAL NOT NULL)"
            )
            con.execute("CREATE TABLE IF NOT EXISTS store_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
            row = con.execute("SELECT generation FROM governance_state WHERE singleton=1").fetchone()
            if row is None:
                state, generation = self._read_legacy_state()
                state_hash = digest_json(state)
                con.execute(
                    "INSERT INTO governance_state(singleton,generation,state_json,state_hash,transition_hash) "
                    "VALUES(1,?,?,?,?)",
                    (generation, canonical_json(state), state_hash, GENESIS_HASH),
                )
                self._import_legacy_resources(con)
            metadata_count = con.execute("SELECT COUNT(*) FROM store_metadata WHERE key IN ('base_generation','base_state_hash')").fetchone()[0]
            if metadata_count != 2:
                first_transition = con.execute("SELECT generation,record_json FROM transitions ORDER BY generation LIMIT 1").fetchone()
                if first_transition:
                    try:
                        first_record = json.loads(first_transition["record_json"])
                        base_generation = first_transition["generation"] - 1
                        base_state_hash = first_record["previous_state_hash"]
                    except Exception as exc:
                        raise CorruptStoreError("First transition is malformed; cannot establish the history baseline.") from exc
                else:
                    current = con.execute("SELECT generation,state_hash FROM governance_state WHERE singleton=1").fetchone()
                    base_generation, base_state_hash = current["generation"], current["state_hash"]
                con.execute("INSERT OR REPLACE INTO store_metadata(key,value) VALUES('base_generation',?)", (str(base_generation),))
                con.execute("INSERT OR REPLACE INTO store_metadata(key,value) VALUES('base_state_hash',?)", (base_state_hash,))
            con.commit()
        except Exception:
            con.rollback()
            raise

    def _read_legacy_state(self) -> tuple[dict[str, Any], int]:
        if not self.state_path.exists():
            return dict(_DEFAULT_STATE), 0
        try:
            raw = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CorruptStoreError(f"Legacy governance state cannot be read: {exc}") from exc
        if not isinstance(raw, dict):
            raise CorruptStoreError("Legacy governance state must be a JSON object.")
        metadata = raw.pop(_STATE_METADATA_KEY, {})
        state = {**_DEFAULT_STATE, **raw}
        self._validate_state(state)
        generation = metadata.get("generation", 0) if isinstance(metadata, dict) else 0
        if not isinstance(generation, int) or generation < 0:
            raise CorruptStoreError("Legacy state generation is invalid.")
        expected_hash = metadata.get("state_hash") if isinstance(metadata, dict) else None
        if expected_hash and expected_hash != digest_json(state):
            raise CorruptStoreError("Legacy state hash does not match its contents.")
        if isinstance(metadata, dict) and metadata.get("transition_hash") not in (None, GENESIS_HASH):
            raise CorruptStoreError("Transition database is missing but the exported state claims committed history; restore the SQLite store or use a verified recovery export.")
        return state, generation

    def _import_legacy_resources(self, con: sqlite3.Connection) -> None:
        allowed_root = {"constitution.json", "core_principles.json", "amendments.jsonl"}
        for name in allowed_root:
            path = self.data_root / name
            if path.is_file() and not path.is_symlink():
                con.execute(
                    "INSERT OR IGNORE INTO resources(path,content,updated_at) VALUES(?,?,?)",
                    (name, path.read_bytes(), time.time()),
                )
        proposals = self.data_root / "proposals"
        if proposals.exists():
            for path in proposals.rglob("*.json"):
                if path.is_file() and not path.is_symlink():
                    rel = path.relative_to(self.data_root).as_posix()
                    if rel.startswith("proposals/"):
                        con.execute(
                            "INSERT OR IGNORE INTO resources(path,content,updated_at) VALUES(?,?,?)",
                            (rel, path.read_bytes(), time.time()),
                        )

    @staticmethod
    def _validate_state(state: dict[str, Any]) -> None:
        if not isinstance(state, dict):
            raise CorruptStoreError("Governance state must be a JSON object.")
        if state.get("posture") not in {"SCOUT", "DEFENSE", "OFFENSE"}:
            raise CorruptStoreError("Governance state has an unknown posture.")
        if not isinstance(state.get("mode"), str) or not state["mode"].strip():
            raise CorruptStoreError("Governance state has an invalid mode.")
        if state.get("role") not in {"Primary", "Secondary", "Observer"}:
            raise CorruptStoreError("Governance state has an unknown role.")
        docs = state.get("vault_documents", [])
        if not isinstance(docs, list) or any(not isinstance(doc, dict) for doc in docs):
            raise CorruptStoreError("Governance vault_documents must be a list of objects.")

    def _snapshot_from_row(self, row: sqlite3.Row) -> StateSnapshot:
        try:
            state = json.loads(row["state_json"])
        except json.JSONDecodeError as exc:
            raise CorruptStoreError("Canonical governance state JSON is corrupt.") from exc
        self._validate_state(state)
        actual_hash = digest_json(state)
        if actual_hash != row["state_hash"]:
            raise CorruptStoreError("Canonical governance state hash mismatch.")
        return StateSnapshot(state, row["generation"], actual_hash, row["transition_hash"])

    def read(self) -> StateSnapshot:
        con = self._connect()
        try:
            row = con.execute("SELECT * FROM governance_state WHERE singleton=1").fetchone()
            if row is None:
                raise CorruptStoreError("Canonical governance state is missing.")
            snapshot = self._snapshot_from_row(row)
            self._assert_verified(con)
            return snapshot
        finally:
            con.close()

    def transition(
        self,
        operation: str,
        *,
        expected_generation: int,
        expected_hash: str,
        updates: dict[str, Any] | None = None,
        resource_updates: dict[str, str | bytes | None] | None = None,
        actor: str = "local-tool",
        detail: dict[str, Any] | None = None,
    ) -> StateSnapshot:
        """Atomically commit state/resource changes and their hash-chained record."""
        if not isinstance(expected_generation, int) or expected_generation < 0:
            raise StaleStateError("A non-negative expected_generation is required.")
        if not isinstance(expected_hash, str) or len(expected_hash) != 64:
            raise StaleStateError("A 64-character expected_hash is required.")
        if not operation or not actor:
            raise GovernanceStoreError("Transition operation and actor are required.")
        updates = updates or {}
        resource_updates = resource_updates or {}
        unknown = set(updates) - _ALLOWED_STATE_FIELDS
        if unknown:
            raise GovernanceStoreError(f"Unsupported state fields: {', '.join(sorted(unknown))}")

        con = self._connect()
        projection_snapshot: StateSnapshot
        try:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT * FROM governance_state WHERE singleton=1").fetchone()
            if row is None:
                raise CorruptStoreError("Canonical governance state is missing.")
            current = self._snapshot_from_row(row)
            integrity = self._verify_transitions(con, current)
            if not integrity["valid"]:
                raise CorruptStoreError(
                    f"Transition history is corrupt at generation {integrity['first_failure']}: {integrity['reason']}"
                )
            if current.generation != expected_generation or current.state_hash != expected_hash:
                raise StaleStateError(
                    f"Stale governance state: current generation is {current.generation}; "
                    f"caller supplied {expected_generation}. Read status and retry."
                )

            # This is the common policy boundary. Every caller (MCP, CLI,
            # scripts, and hooks that commit state) receives identical checks.
            from .audit import AuditLedger
            from .engine import GovernanceState, check_action_permitted
            audit = AuditLedger(self.data_root / "audit_ledger.jsonl").verify_integrity()
            if not audit.get("valid"):
                raise CorruptStoreError(f"Audit ledger verification failed: {audit.get('reason', 'unknown error')}")
            control_plane_operations = {"govern.set_mode", "govern.set_posture", "govern.set_role", "cli.set_state"}
            operation_fields = {
                "govern.set_mode": {"mode"},
                "govern.set_posture": {"posture"},
                "govern.set_role": {"role"},
                "cli.set_state": {"mode", "posture", "role"},
                "vault.load": {"vault_documents"},
                "vault.unload": {"vault_documents"},
                "vault.clear": {"vault_documents"},
                "cli.vault_load": {"vault_documents"},
                "cli.vault_unload": {"vault_documents"},
                "meta.analyze_trail": set(),
                "meta.reject_proposal": set(),
                "lineage.initialize": set(),
            }
            if operation in operation_fields:
                if set(updates) - operation_fields[operation]:
                    raise GovernanceStoreError(f"Operation {operation} cannot update unrelated state fields.")
                if operation in control_plane_operations and resource_updates:
                    raise GovernanceStoreError(f"Operation {operation} cannot update resources.")
                if operation not in control_plane_operations and updates:
                    raise GovernanceStoreError(f"Operation {operation} is resource-only.")
            if set(resource_updates) & {"constitution.json", "core_principles.json", "amendments.jsonl"}:
                raise GovernanceStoreError("Privileged constitution changes require a trusted operator identity provider, which is not configured.")
            if operation not in control_plane_operations:
                decision = check_action_permitted(f"write/update governance state for operation {operation}", GovernanceState(**current.state))
                if not decision.get("permitted", False):
                    raise GovernanceStoreError(decision.get("reason") or "Governance policy denied this mutation.")

            next_state = {**current.state, **updates}
            self._validate_state(next_state)
            self._authorize_state_delta(current.state, next_state)
            normalized_resources: dict[str, bytes | None] = {}
            resource_hashes: dict[str, str | None] = {}
            for rel, content in resource_updates.items():
                safe_rel = self._validate_resource_path(rel)
                normalized = content.encode("utf-8") if isinstance(content, str) else content
                if normalized is not None and not isinstance(normalized, bytes):
                    raise GovernanceStoreError(f"Resource content for {safe_rel} must be text, bytes, or None.")
                normalized_resources[safe_rel] = normalized
                resource_hashes[safe_rel] = hashlib.sha256(normalized).hexdigest() if normalized is not None else None

            new_generation = current.generation + 1
            new_state_hash = digest_json(next_state)
            record = {
                "generation": new_generation,
                "timestamp": time.time(),
                "operation": operation,
                "actor": actor,
                "previous_state_hash": current.state_hash,
                "state_hash": new_state_hash,
                "previous_transition_hash": current.transition_hash,
                "resource_hashes": resource_hashes,
                "detail": detail or {},
            }
            transition_hash = digest_json(record)
            record["transition_hash"] = transition_hash
            con.execute(
                "INSERT INTO transitions(generation,record_json,transition_hash) VALUES(?,?,?)",
                (new_generation, canonical_json(record), transition_hash),
            )
            for rel, content in normalized_resources.items():
                if content is None:
                    con.execute("DELETE FROM resources WHERE path=?", (rel,))
                else:
                    con.execute(
                        "INSERT INTO resources(path,content,updated_at) VALUES(?,?,?) "
                        "ON CONFLICT(path) DO UPDATE SET content=excluded.content,updated_at=excluded.updated_at",
                        (rel, content, time.time()),
                    )
            con.execute(
                "UPDATE governance_state SET generation=?,state_json=?,state_hash=?,transition_hash=? WHERE singleton=1",
                (new_generation, canonical_json(next_state), new_state_hash, transition_hash),
            )
            con.commit()
            projection_snapshot = StateSnapshot(next_state, new_generation, new_state_hash, transition_hash)
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

        # JSON/files are projections only. A failed projection cannot undo a
        # committed transition; callers receive explicit repair information.
        projection_errors = []
        try:
            self._project_snapshot(projection_snapshot)
        except Exception as exc:
            projection_errors.append(f"state export: {exc}")
        for rel, content in normalized_resources.items():
            try:
                self._project_resource(rel, content)
            except Exception as exc:
                projection_errors.append(f"{rel}: {exc}")
        if projection_errors:
            projection_snapshot = StateSnapshot(
                **{**projection_snapshot.__dict__, "projection_error": "; ".join(projection_errors)}
            )
        return projection_snapshot

    @staticmethod
    def _authorize_state_delta(current: dict[str, Any], proposed: dict[str, Any]) -> None:
        """Without an authenticated operator channel, accept only safer state changes."""
        if proposed.get("mode") != current.get("mode") and proposed.get("mode") != "High Security":
            raise GovernanceStoreError("Changing to a less restrictive or unranked mode requires a trusted operator identity provider, which is not configured.")
        posture_rank = {"SCOUT": 0, "DEFENSE": 1, "OFFENSE": 2}
        old_posture, new_posture = current.get("posture"), proposed.get("posture")
        if posture_rank.get(new_posture, -1) > posture_rank.get(old_posture, -1):
            raise GovernanceStoreError("Increasing operational permissions requires a trusted operator identity provider, which is not configured.")
        role_rank = {"Observer": 0, "Secondary": 1, "Primary": 2}
        if role_rank.get(proposed.get("role"), -1) > role_rank.get(current.get("role"), -1):
            raise GovernanceStoreError("Increasing role authority requires a trusted operator identity provider, which is not configured.")

    def _verify_transitions(self, con: sqlite3.Connection, snapshot: StateSnapshot) -> dict[str, Any]:
        rows = con.execute("SELECT generation,record_json,transition_hash FROM transitions ORDER BY generation").fetchall()
        previous_hash = GENESIS_HASH
        metadata = {row["key"]: row["value"] for row in con.execute("SELECT key,value FROM store_metadata WHERE key IN ('base_generation','base_state_hash')").fetchall()}
        try:
            base_generation = int(metadata["base_generation"])
            previous_state_hash = metadata["base_state_hash"]
        except (KeyError, TypeError, ValueError):
            return {"valid": False, "entries_checked": 0, "first_failure": 0, "reason": "history baseline is missing or malformed"}
        expected_generation = base_generation + 1
        # Legacy seeded state may start above zero but has no transition history.
        if not rows:
            if snapshot.generation != base_generation or snapshot.state_hash != previous_state_hash or snapshot.transition_hash != GENESIS_HASH:
                return {"valid": False, "entries_checked": 0, "first_failure": snapshot.generation, "reason": "missing history"}
            return {"valid": True, "entries_checked": 0, "first_failure": None}
        for index, row in enumerate(rows):
            try:
                record = json.loads(row["record_json"])
            except (json.JSONDecodeError, TypeError):
                return {"valid": False, "entries_checked": index, "first_failure": row["generation"], "reason": "malformed record"}
            if not isinstance(record, dict):
                return {"valid": False, "entries_checked": index, "first_failure": row["generation"], "reason": "malformed record: expected an object"}
            claimed = record.pop("transition_hash", None)
            if row["generation"] != expected_generation or record.get("generation") != expected_generation:
                return {"valid": False, "entries_checked": index, "first_failure": row["generation"], "reason": "generation gap"}
            if record.get("previous_transition_hash") != previous_hash:
                return {"valid": False, "entries_checked": index, "first_failure": row["generation"], "reason": "previous transition hash mismatch"}
            if record.get("previous_state_hash") != previous_state_hash:
                return {"valid": False, "entries_checked": index, "first_failure": row["generation"], "reason": "previous state hash mismatch"}
            if not isinstance(record.get("resource_hashes", {}), dict):
                return {"valid": False, "entries_checked": index, "first_failure": row["generation"], "reason": "malformed resource hash map"}
            computed = digest_json(record)
            if claimed != computed or row["transition_hash"] != computed:
                return {"valid": False, "entries_checked": index, "first_failure": row["generation"], "reason": "transition hash mismatch"}
            previous_hash = computed
            previous_state_hash = record.get("state_hash")
            expected_generation += 1
        # Verify each resource against its most recent committed transition.
        # Resources imported before the first transition have no transition hash
        # and remain part of the explicitly documented legacy baseline.
        last_resource_hashes: dict[str, str | None] = {}
        for row in rows:
            record = json.loads(row["record_json"])
            for resource_path, content_hash in record.get("resource_hashes", {}).items():
                last_resource_hashes[resource_path] = content_hash
        for resource_path, expected_resource_hash in last_resource_hashes.items():
            stored = con.execute("SELECT content FROM resources WHERE path=?", (resource_path,)).fetchone()
            actual_resource_hash = hashlib.sha256(bytes(stored["content"])).hexdigest() if stored else None
            if actual_resource_hash != expected_resource_hash:
                return {"valid": False, "entries_checked": len(rows), "first_failure": snapshot.generation, "reason": f"resource hash mismatch: {resource_path}"}
        if rows[-1]["generation"] != snapshot.generation or previous_hash != snapshot.transition_hash:
            return {"valid": False, "entries_checked": len(rows), "first_failure": snapshot.generation, "reason": "head does not match state"}
        if previous_state_hash != snapshot.state_hash:
            return {"valid": False, "entries_checked": len(rows), "first_failure": snapshot.generation, "reason": "head state hash does not match canonical state"}
        return {"valid": True, "entries_checked": len(rows), "first_failure": None}

    def verify(self) -> dict[str, Any]:
        con = self._connect()
        try:
            row = con.execute("SELECT * FROM governance_state WHERE singleton=1").fetchone()
            if row is None:
                return {"valid": False, "entries_checked": 0, "first_failure": 0, "reason": "state missing"}
            try:
                snapshot = self._snapshot_from_row(row)
            except CorruptStoreError as exc:
                return {"valid": False, "entries_checked": 0, "first_failure": row["generation"], "reason": str(exc)}
            return self._verify_transitions(con, snapshot)
        finally:
            con.close()

    def inspect(self) -> dict[str, Any]:
        """Return read-only diagnostics, keeping invalid snapshots non-authoritative."""
        integrity = self.verify()
        con = self._connect()
        try:
            row = con.execute("SELECT * FROM governance_state WHERE singleton=1").fetchone()
            if row is None:
                return {"valid": False, "reason": integrity.get("reason", "state missing")}
            try:
                snapshot = self._snapshot_from_row(row)
            except CorruptStoreError as exc:
                return {"valid": False, "reason": str(exc), "integrity": integrity}
            if not integrity.get("valid"):
                return {
                    "valid": False,
                    "reason": integrity.get("reason", "transition history is invalid"),
                    "unverified_snapshot": {**snapshot.public_metadata(), "state": snapshot.state},
                    "integrity": integrity,
                }
            return {"valid": True, **snapshot.public_metadata(), "state": snapshot.state, "integrity": integrity}
        finally:
            con.close()

    def read_resource(self, relative_path: str) -> bytes | None:
        safe_rel = self._validate_resource_path(relative_path)
        con = self._connect()
        try:
            self._assert_verified(con)
            row = con.execute("SELECT content FROM resources WHERE path=?", (safe_rel,)).fetchone()
            return bytes(row["content"]) if row else None
        finally:
            con.close()

    def list_resources(self, prefix: str) -> list[str]:
        con = self._connect()
        try:
            self._assert_verified(con)
            rows = con.execute("SELECT path FROM resources WHERE path LIKE ? ORDER BY path", (prefix.replace("%", "\\%") + "%",)).fetchall()
            return [row["path"] for row in rows]
        finally:
            con.close()

    def _assert_verified(self, con: sqlite3.Connection) -> None:
        row = con.execute("SELECT * FROM governance_state WHERE singleton=1").fetchone()
        if row is None:
            raise CorruptStoreError("Canonical governance state is missing.")
        snapshot = self._snapshot_from_row(row)
        report = self._verify_transitions(con, snapshot)
        if not report.get("valid"):
            raise CorruptStoreError(f"Governance store verification failed: {report.get('reason', 'unknown error')}")

    def export(self) -> dict[str, Any]:
        """Rebuild compatibility files from the verified canonical database."""
        integrity = self.verify()
        if not integrity["valid"]:
            raise CorruptStoreError(f"Cannot export corrupt store: {integrity['reason']}")
        snapshot = self.read()
        self._project_snapshot(snapshot)
        con = self._connect()
        try:
            rows = con.execute("SELECT path,content FROM resources ORDER BY path").fetchall()
        finally:
            con.close()
        for row in rows:
            self._project_resource(row["path"], bytes(row["content"]))
        return {**integrity, **snapshot.public_metadata(), "exported_resources": len(rows)}

    def _validate_resource_path(self, relative_path: str) -> str:
        if not isinstance(relative_path, str) or not relative_path or "\\" in relative_path:
            raise GovernanceStoreError("Resource path must be a non-empty relative POSIX path.")
        path = Path(relative_path)
        if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
            raise GovernanceStoreError("Resource path must stay within the governance data directory.")
        rel = path.as_posix()
        if rel not in {"constitution.json", "core_principles.json", "amendments.jsonl", "lineage.json"} and not rel.startswith("proposals/"):
            raise GovernanceStoreError("Resource path is not a supported governance resource.")
        return rel

    def _project_snapshot(self, snapshot: StateSnapshot) -> None:
        value = dict(snapshot.state)
        value[_STATE_METADATA_KEY] = snapshot.public_metadata()
        self._atomic_write(self.state_path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

    def _project_resource(self, relative_path: str, content: bytes | None) -> None:
        safe_rel = self._validate_resource_path(relative_path)
        path = self.data_root / safe_rel
        resolved_parent = path.parent.resolve()
        if self.data_root != resolved_parent and self.data_root not in resolved_parent.parents:
            raise GovernanceStoreError("Resource projection escaped the governance data directory.")
        if content is None:
            try:
                path.unlink()
            except FileNotFoundError:
                pass
            return
        self._atomic_write(path, content)

    @staticmethod
    def _atomic_write(path: Path, content: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, path)
            dir_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        finally:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass
