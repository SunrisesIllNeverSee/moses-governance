import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "moses-governance-mcp"))

from governance.audit import AuditLedger
from governance.meta import _verify_operator_sig, apply_amendment, rollback_amendment
from governance.store import CorruptStoreError, GovernanceStore, GovernanceStoreError, StaleStateError, digest_json


class PolicyBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.state_file = Path(self.temp.name) / "data" / "governance_state.json"
        self.store = GovernanceStore(self.state_file)

    def use_offense_fixture(self):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps({"mode": "High Security", "posture": "OFFENSE", "role": "Primary", "vault_documents": []}))
        self.store = GovernanceStore(self.state_file)

    def test_transition_survives_restart_and_exports_recovery_view(self):
        self.use_offense_fixture()
        first = self.store.read()
        committed = self.store.transition("test.set_mode", updates={"mode": "High Security"},
            expected_generation=first.generation, expected_hash=first.state_hash)
        reopened = GovernanceStore(self.state_file)
        self.assertEqual(reopened.read().state["mode"], "High Security")
        self.assertTrue(reopened.verify()["valid"])
        self.assertEqual(reopened.export()["generation"], committed.generation)
        exported = json.loads(self.state_file.read_text())
        self.assertEqual(exported["_governance_store"]["transition_hash"], committed.transition_hash)

    def test_stale_generation_and_hash_rejected(self):
        self.use_offense_fixture()
        stale = self.store.read()
        self.store.transition("first", updates={"role": "Observer"}, expected_generation=stale.generation, expected_hash=stale.state_hash)
        with self.assertRaises(StaleStateError):
            self.store.transition("stale", updates={"role": "Secondary"}, expected_generation=stale.generation, expected_hash=stale.state_hash)

    def test_concurrent_transition_only_one_snapshot_wins(self):
        self.use_offense_fixture()
        base = self.store.read()
        outcomes = []
        barrier = threading.Barrier(2)

        def commit(value):
            barrier.wait()
            try:
                self.store.transition("concurrent", updates={"role": value}, expected_generation=base.generation, expected_hash=base.state_hash)
                outcomes.append("committed")
            except StaleStateError:
                outcomes.append("stale")

        threads = [threading.Thread(target=commit, args=(role,)) for role in ("Observer", "Secondary")]
        for thread in threads: thread.start()
        for thread in threads: thread.join()
        self.assertCountEqual(outcomes, ["committed", "stale"])
        self.assertTrue(self.store.verify()["valid"])

    def test_corrupt_state_and_transition_fail_closed(self):
        snap = self.store.read()
        con = self.store._connect()
        try:
            con.execute("UPDATE governance_state SET state_json='{}' WHERE singleton=1")
        finally:
            con.close()
        with self.assertRaises(CorruptStoreError):
            self.store.transition("blocked", updates={"role": "Observer"}, expected_generation=snap.generation, expected_hash=snap.state_hash)

    def test_audit_malformed_line_is_reported_and_append_refused(self):
        path = Path(self.temp.name) / "bad.jsonl"
        path.write_text('{"id":0}\nnot-json\n')
        ledger = AuditLedger(path)
        report = ledger.verify_integrity()
        self.assertFalse(report["valid"])
        self.assertEqual(report["line"], 2)
        with self.assertRaises(ValueError):
            ledger.log_action("test", "append", {})

    def test_approval_fails_closed_for_all_signature_shapes(self):
        for signature in ("", "operator:root", "hmac:" + "a" * 64, "broken"):
            valid, reason = _verify_operator_sig(signature, "proposal")
            self.assertFalse(valid)
            self.assertTrue("trusted operator" in reason or "malformed" in reason)

    def test_direct_privileged_mutators_do_not_write(self):
        self.store.read()
        before = self.store.read()
        self.assertFalse(apply_amendment("proposal", "hmac:" + "a" * 64)["success"])
        self.assertFalse(rollback_amendment("amendment", "operator:root", "test")["success"])
        self.assertEqual(self.store.read(), before)

    def test_codex_hook_event_shape_and_corrupt_store_denial(self):
        event = {"tool_name": "Bash", "tool_input": {"command": "touch /tmp/policy-test"}}
        env = {**os.environ, "MOSES_GOVERNANCE_STATE_FILE": str(self.state_file)}
        proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "pre_tool_use.py")], input=json.dumps(event), text=True, capture_output=True, env=env)
        # An ordinary Bash write is intercepted and denied under the default SCOUT posture.
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")
        con = self.store._connect()
        try:
            con.execute("UPDATE governance_state SET state_json='not-json' WHERE singleton=1")
        finally:
            con.close()
        proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "pre_tool_use.py")], input=json.dumps(event), text=True, capture_output=True, env=env)
        self.assertEqual(json.loads(proc.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")

        read_event = {"tool_name": "mcp__moses_governance__govern_get_status", "tool_input": {}}
        proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "pre_tool_use.py")], input=json.dumps(read_event), text=True, capture_output=True, env=env)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout, "")

    def test_codex_hook_fails_closed_when_governance_store_is_absent(self):
        missing = Path(self.temp.name) / "missing" / "governance_state.json"
        event = {"tool_name": "apply_patch", "tool_input": {"patch": "*** Begin Patch"}}
        env = {**os.environ, "MOSES_GOVERNANCE_STATE_FILE": str(missing)}
        proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "pre_tool_use.py")], input=json.dumps(event), text=True, capture_output=True, env=env)
        self.assertEqual(json.loads(proc.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_direct_vault_mutator_requires_snapshot_authority(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        import vault
        with self.assertRaises(Exception):
            vault.load_document("direct-call", content="must not bypass policy", state_path=str(self.state_file))

    def test_legacy_json_migrates_and_can_be_recovered(self):
        legacy_path = Path(self.temp.name) / "legacy" / "governance_state.json"
        legacy_path.parent.mkdir()
        legacy_path.write_text(json.dumps({"mode": "High Security", "posture": "DEFENSE", "role": "Primary", "vault_documents": []}))
        migrated = GovernanceStore(legacy_path)
        self.assertEqual(migrated.read().state["mode"], "High Security")
        self.assertTrue(migrated.verify()["valid"])
        migrated.export()
        self.assertEqual(json.loads(legacy_path.read_text())["_governance_store"]["generation"], 0)

    def test_resource_tampering_detected(self):
        self.use_offense_fixture()
        snap = self.store.read()
        self.store.transition("resource", expected_generation=snap.generation, expected_hash=snap.state_hash,
            resource_updates={"proposals/pending/test.json": '{"version":"1"}'})
        con = self.store._connect()
        try:
            con.execute("UPDATE resources SET content=? WHERE path='proposals/pending/test.json'", (b'{"version":"2"}',))
        finally:
            con.close()
        self.assertFalse(self.store.verify()["valid"])

    def test_read_rejects_corrupt_transition_history(self):
        self.use_offense_fixture()
        snap = self.store.read()
        snap = self.store.transition("test.change", updates={"response_style": "Detailed"}, expected_generation=snap.generation, expected_hash=snap.state_hash)
        con = self.store._connect()
        try:
            con.execute("UPDATE transitions SET record_json='not-json' WHERE generation=?", (snap.generation,))
        finally:
            con.close()
        with self.assertRaises(CorruptStoreError):
            self.store.read()
        report = self.store.inspect()
        self.assertFalse(report["valid"])
        self.assertIn("unverified_snapshot", report)

    def test_verifier_reports_json_transition_with_wrong_shape(self):
        self.use_offense_fixture()
        snap = self.store.read()
        committed = self.store.transition("test.change", updates={"response_style": "Detailed"},
            expected_generation=snap.generation, expected_hash=snap.state_hash)
        con = self.store._connect()
        try:
            con.execute("UPDATE transitions SET record_json='[]' WHERE generation=?", (committed.generation,))
        finally:
            con.close()
        report = self.store.verify()
        self.assertFalse(report["valid"])
        self.assertIn("malformed record", report["reason"])

    def test_operation_label_cannot_bypass_field_policy(self):
        snap = self.store.read()
        with self.assertRaises(GovernanceStoreError):
            self.store.transition("govern.set_role", updates={"vault_documents": [{"name": "bypass"}]},
                expected_generation=snap.generation, expected_hash=snap.state_hash)

    def test_privileged_resources_require_trusted_operator(self):
        self.use_offense_fixture()
        snap = self.store.read()
        with self.assertRaises(GovernanceStoreError):
            self.store.transition("constitution.direct_write", expected_generation=snap.generation,
                expected_hash=snap.state_hash, resource_updates={"constitution.json": '{"version":"changed"}'})

    def test_h01_conditions_never_silently_authorize_actions(self):
        """DEFENSE and High Security approvals require verified authority."""
        for posture, mode, tool_name, payload in (
            ("DEFENSE", "None (Unrestricted)", "mcp__mock__send", {"message": "synthetic"}),
            ("DEFENSE", "None (Unrestricted)", "mcp__mock__transfer", {"amount": 10}),
            ("OFFENSE", "High Security", "Bash", {"command": "rm -f /synthetic/mock.txt"}),
        ):
            state = Path(self.temp.name) / f"{posture}-{len(tool_name)}-{len(str(payload))}.json"
            state.write_text(json.dumps({"mode": mode, "posture": posture, "role": "Primary", "vault_documents": []}))
            env = {**os.environ, "MOSES_GOVERNANCE_STATE_FILE": str(state),
                   "MOSES_GOVERNANCE_AUDIT_FILE": str(Path(self.temp.name) / "empty_audit.jsonl")}
            event = {"tool_name": tool_name, "tool_input": payload}
            result = subprocess.run([sys.executable, str(ROOT / "scripts" / "pre_tool_use.py")],
                input=json.dumps(event), text=True, capture_output=True, env=env)
            self.assertEqual(result.returncode, 0)
            output = json.loads(result.stdout)["hookSpecificOutput"]
            self.assertEqual(output["permissionDecision"], "deny", event)
            self.assertIn("Unfulfilled governance conditions", output["permissionDecisionReason"])

    def test_h01_untrusted_read_named_tool_cannot_bypass_scout(self):
        from scripts.pre_tool_use import _tool_action
        protected, detail = _tool_action("mcp__untrusted__read", {"operation": "delete", "id": "synthetic"})
        self.assertTrue(protected, detail)
        event = {"tool_name": "mcp__untrusted__read", "tool_input": {"operation": "delete", "id": "synthetic"}}
        env = {**os.environ, "MOSES_GOVERNANCE_STATE_FILE": str(self.state_file),
               "MOSES_GOVERNANCE_AUDIT_FILE": str(Path(self.temp.name) / "audit_empty.jsonl")}
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / "pre_tool_use.py")],
            input=json.dumps(event), text=True, capture_output=True, env=env)
        self.assertEqual(json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_h01_git_c_status_is_read_only_but_git_write_is_not(self):
        from scripts.pre_tool_use import _tool_action
        self.assertFalse(_tool_action("Bash", {"command": "git -C /synthetic/repo status"})[0])
        self.assertTrue(_tool_action("Bash", {"command": "git -C /synthetic/repo clean -fd"})[0])

    def test_hook_shell_allowlist_rejects_write_capable_flags(self):
        env = {**os.environ, "MOSES_GOVERNANCE_STATE_FILE": str(self.state_file)}
        for command in ("git clean -fd", "sed -i s/a/b/file", "find . -delete"):
            event = {"tool_name": "Bash", "tool_input": {"command": command}}
            proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "pre_tool_use.py")], input=json.dumps(event), text=True, capture_output=True, env=env)
            self.assertEqual(json.loads(proc.stdout)["hookSpecificOutput"]["permissionDecision"], "deny", command)

    def test_scout_blocks_protected_write_but_preserves_governance_recovery(self):
        snap = self.store.read()
        with self.assertRaises(GovernanceStoreError):
            self.store.transition("vault.clear", updates={"vault_documents": []}, expected_generation=snap.generation, expected_hash=snap.state_hash)
        with self.assertRaises(GovernanceStoreError):
            self.store.transition("govern.set_posture", updates={"posture": "DEFENSE"}, expected_generation=snap.generation, expected_hash=snap.state_hash)
        recovered = self.store.transition("govern.set_mode", updates={"mode": "High Security"}, expected_generation=snap.generation, expected_hash=snap.state_hash)
        self.assertEqual(recovered.state["mode"], "High Security")

    def test_model_cannot_relax_posture_or_escalate_role(self):
        snap = self.store.read()
        with self.assertRaises(GovernanceStoreError):
            self.store.transition("govern.set_posture", updates={"posture": "OFFENSE"}, expected_generation=snap.generation, expected_hash=snap.state_hash)
        with self.assertRaises(GovernanceStoreError):
            demoted = self.store.transition("govern.set_role", updates={"role": "Observer"}, expected_generation=snap.generation, expected_hash=snap.state_hash)
            self.store.transition("govern.set_role", updates={"role": "Primary"}, expected_generation=demoted.generation, expected_hash=demoted.state_hash)

    def test_state_json_and_matching_hash_tamper_is_not_in_transition_history(self):
        self.use_offense_fixture()
        snap = self.store.read()
        snap = self.store.transition("govern.set_role", updates={"role": "Observer"}, expected_generation=snap.generation, expected_hash=snap.state_hash)
        forged_state = {**snap.state, "posture": "SCOUT"}
        con = self.store._connect()
        try:
            con.execute("UPDATE governance_state SET state_json=?,state_hash=? WHERE singleton=1", (json.dumps(forged_state), digest_json(forged_state)))
        finally:
            con.close()
        self.assertFalse(self.store.verify()["valid"])

    def test_transition_surfaces_projection_failure(self):
        snap = self.store.read()
        self.store._project_snapshot = lambda _snapshot: (_ for _ in ()).throw(OSError("read-only projection"))
        result = self.store.transition("govern.set_role", updates={"role": "Observer"}, expected_generation=snap.generation, expected_hash=snap.state_hash)
        self.assertIn("projection_warning", result.public_metadata())
        self.assertEqual(self.store.read().state["role"], "Observer")


if __name__ == "__main__":
    unittest.main()
