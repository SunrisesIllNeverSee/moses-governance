"""End-to-end tests for hooks/pre-execute.sh: pipe a PreToolUse event in, check the decision."""
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GOV_CMD = 'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/governance.py" set_state --posture DEFENSE'


class PreExecuteHook(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        shutil.copytree(REPO / "hooks", self.root / "hooks")
        shutil.copytree(REPO / "scripts", self.root / "scripts")
        (self.root / "data").mkdir()

    def tearDown(self):
        shutil.rmtree(self.root)

    def run_hook(self, mode, posture, payload, env_input=None):
        (self.root / "data" / "governance_state.json").write_text(
            json.dumps({"mode": mode, "posture": posture, "role": "Primary"}))
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_TOOL_INPUT"}
        env["CLAUDE_PLUGIN_ROOT"] = str(self.root)
        if env_input is not None:
            env["CLAUDE_TOOL_INPUT"] = env_input
        stdin = payload if isinstance(payload, str) else json.dumps(payload)
        p = subprocess.run(["bash", str(self.root / "hooks" / "pre-execute.sh")],
                           input=stdin, capture_output=True, text=True, env=env, timeout=60)
        if p.returncode == 2:
            return "deny"
        self.assertEqual(p.returncode, 0, p.stderr)
        return "ask" if '"permissionDecision": "ask"' in p.stdout else "allow"

    def bash(self, mode, posture, command):
        return self.run_hook(mode, posture, {"tool_name": "Bash", "tool_input": {"command": command}})

    def test_high_security_destructive_asks(self):
        for posture in ("DEFENSE", "OFFENSE"):
            self.assertEqual(self.bash("High Security", posture, "rm -rf /"), "ask")

    def test_prohibited_and_scout_block(self):
        self.assertEqual(self.bash("High Security", "DEFENSE", "git push origin main"), "deny")
        self.assertEqual(self.bash("High Security", "SCOUT", "rm -rf build"), "deny")

    def test_ordinary_reads_allowed(self):
        for mode, posture in (("High Security", "SCOUT"), ("High Security", "DEFENSE"),
                              ("Research", "DEFENSE"), ("None (Unrestricted)", "SCOUT")):
            for cmd in ("ls -la", "git status", "cat README.md", "npm test"):
                self.assertEqual(self.bash(mode, posture, cmd), "allow", (mode, posture, cmd))

    def test_governance_commands_exempt_even_in_scout(self):
        self.assertEqual(self.bash("High Security", "SCOUT", GOV_CMD), "allow")

    def test_governance_whitelist_cannot_be_smuggled(self):
        self.assertEqual(self.bash("High Security", "SCOUT", GOV_CMD + "; rm -rf build"), "deny")
        self.assertEqual(self.bash("High Security", "SCOUT",
                                   "rm -rf build # scripts/governance.py set_state"), "deny")

    def test_only_the_plugins_own_scripts_are_exempt(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("hook_gate", REPO / "scripts" / "hook_gate.py")
        gate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gate)
        self.assertTrue(gate.is_governance_command(GOV_CMD))
        self.assertTrue(gate.is_governance_command(GOV_CMD.replace(" --posture", " \\\n  --posture")))
        self.assertFalse(gate.is_governance_command("python3 /tmp/x/scripts/governance.py set_state"))
        self.assertFalse(gate.is_governance_command(GOV_CMD + " && rm -rf build"))
        self.assertFalse(gate.is_governance_command(GOV_CMD + " $(rm -rf build)"))
        self.assertFalse(gate.is_governance_command(GOV_CMD + " `rm -rf build`"))
        log = 'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/audit.py" log_action "edited a; b > c"'
        self.assertTrue(gate.is_governance_command(log))

    def test_fail_closed_on_bad_events(self):
        self.assertEqual(self.run_hook("High Security", "DEFENSE", "not json"), "deny")
        self.assertEqual(self.run_hook("High Security", "DEFENSE", {"tool_name": "Bash", "tool_input": {}}), "deny")
        self.assertEqual(self.run_hook("High Security", "DEFENSE", {"tool_name": "Bash", "tool_input": "rm -rf /"}), "deny")

    def test_dash_leading_command_is_evaluated(self):
        self.assertIn(self.bash("High Security", "DEFENSE", "-n foo"), {"allow", "ask"})

    def test_legacy_env_input_still_works(self):
        self.assertEqual(self.run_hook("High Security", "DEFENSE", "", env_input="rm -rf /"), "ask")

    def test_write_edit_unchanged_outside_the_plugin(self):
        self.assertEqual(self.run_hook("High Security", "SCOUT",
                                       {"tool_name": "Write", "tool_input": {"file_path": "/x"}}), "allow")

    def test_file_tools_cannot_rewrite_governance_files(self):
        for rel in ("data/governance_state.json", "hooks/pre-execute.sh", "scripts/governance.py"):
            for tool in ("Write", "Edit"):
                event = {"tool_name": tool, "tool_input": {"file_path": str(self.root / rel)}}
                self.assertEqual(self.run_hook("High Security", "OFFENSE", event), "deny", (tool, rel))

    def test_event_without_tool_name_blocks(self):
        self.assertEqual(self.run_hook("High Security", "DEFENSE", {"tool_input": {"command": "ls"}}), "deny")

    def test_stdin_event_wins_over_stale_env(self):
        self.assertEqual(self.run_hook("High Security", "SCOUT",
                                       {"tool_name": "Bash", "tool_input": {"command": "rm -rf build"}},
                                       env_input="ls"), "deny")


if __name__ == "__main__":
    unittest.main()
