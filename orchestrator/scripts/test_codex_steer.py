#!/usr/bin/env python3
"""Probes for the Codex steer/status hook, steer queueing, and hook install, run as Codex and the lead run them."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("codex_steer.py")
ROOT_THREAD = "019a0000-0000-7000-8000-000000000001"


class SteerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="orchestrator-steer-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.steer = self.root / "T.r1.steer.md"
        self.log = self.root / "T.r1.steer.log"
        self.events = self.root / "T.r1.events.jsonl"
        self.dispatch = self.root / "T.r1.dispatch.json"
        self.dispatch.write_text(json.dumps({"artifacts": {
            "steer": str(self.steer), "steer_log": str(self.log), "events": str(self.events)}}))

    def run_script(self, args, stdin="", env=None):
        result = subprocess.run([sys.executable, str(SCRIPT), *args], input=stdin, capture_output=True, text=True,
                                timeout=5, env={**os.environ, **(env or {})})
        return result.returncode, (json.loads(result.stdout) if result.stdout.strip() else None), result.stderr

    def hook(self, event, status_line="1", **extra):
        payload = {"session_id": ROOT_THREAD, "turn_id": "turn-1",
                   "transcript_path": f"/h/.codex/sessions/rollout-2026-10-19T10-00-00-{ROOT_THREAD}.jsonl",
                   "hook_event_name": event, **extra}
        code, output, _ = self.run_script(["hook"], json.dumps(payload),
                                          {"ORCH_STEER_FILE": str(self.steer), "ORCH_STATUS_LINE": status_line})
        return code, output

    def send(self, steer_id, text):
        return self.run_script(["send", str(self.dispatch), steer_id], text)

    def test_post_tool_use_delivers_once_with_receipt(self):
        self.assertEqual(self.send("s1", "Also cover the empty list.")[0], 0)
        code, output = self.hook("PostToolUse", tool_name="Bash")
        self.assertEqual(code, 0)
        context = output["hookSpecificOutput"]
        self.assertEqual(context["hookEventName"], "PostToolUse")
        self.assertEqual(context["additionalContext"], '<lead-steer id="s1">\nAlso cover the empty list.\n</lead-steer>\n')
        self.assertFalse(self.steer.exists())
        receipt = json.loads(self.log.read_text())
        self.assertEqual((receipt["steer_id"], receipt["event"], receipt["turn_id"]), ("s1", "PostToolUse", "turn-1"))
        self.assertEqual(self.hook("PostToolUse", tool_name="Bash"), (0, None))

    def test_subagent_hooks_leave_the_steer_for_the_root_thread(self):
        self.send("s1", "Narrow the scope.")
        self.assertEqual(self.hook("PostToolUse", agent_id="019a-child"), (0, None))
        child_rollout = "/h/.codex/sessions/rollout-2026-10-19T10-00-00-019a0000-0000-7000-8000-000000000002.jsonl"
        self.assertEqual(self.hook("PostToolUse", transcript_path=child_rollout), (0, None))
        self.assertEqual(self.hook("Stop", agent_id="019a-child", last_assistant_message="done"), (0, None))
        self.assertTrue(self.steer.exists())

    def test_stop_delivers_a_pending_steer_even_after_a_continuation(self):
        self.send("s2", "Run the integration test before stopping.")
        code, output = self.hook("Stop", stop_hook_active=True, last_assistant_message="All done.\nDONE")
        self.assertEqual((code, output["decision"]), (0, "block"))
        self.assertIn('<lead-steer id="s2">', output["reason"])
        self.assertEqual(json.loads(self.log.read_text())["event"], "Stop")

    def test_stop_holds_the_status_contract_unless_the_run_has_a_schema(self):
        code, output = self.hook("Stop", stop_hook_active=False, last_assistant_message="All finished.")
        self.assertEqual((code, output["decision"]), (0, "block"))
        self.assertIn("status line", output["reason"])
        self.assertEqual(self.hook("Stop", stop_hook_active=False, last_assistant_message="x\nDONE"), (0, None))
        self.assertEqual(self.hook("Stop", stop_hook_active=True, last_assistant_message="All finished."), (0, None))
        self.assertEqual(self.hook("Stop", "0", stop_hook_active=False, last_assistant_message='{"a": 1}'), (0, None))

    def test_hook_is_inert_without_the_dispatch_variables_and_never_exits_2(self):
        self.send("s1", "x")
        result = subprocess.run([sys.executable, str(SCRIPT), "hook"], input='{"hook_event_name": "PostToolUse"}',
                                capture_output=True, text=True, timeout=5,
                                env={k: v for k, v in os.environ.items() if k != "ORCH_STEER_FILE"})
        self.assertEqual((result.returncode, result.stdout), (0, ""))
        self.assertTrue(self.steer.exists())
        code, output, _ = self.run_script(["hook"], "not json", {"ORCH_STEER_FILE": str(self.steer)})
        self.assertEqual((code, output), (0, None))
        code, output, _ = self.run_script(["hook"], json.dumps({"hook_event_name": "PostToolUse"}),
                                          {"ORCH_STEER_FILE": str(self.root / "missing-dir" / "x.steer.md")})
        self.assertEqual(code, 0)

    def test_send_refuses_unsafe_queueing(self):
        self.assertEqual(self.send("s1", "first")[0], 0)
        code, _, error = self.send("s2", "second")
        self.assertEqual(code, 2)
        self.assertIn("still pending", error)
        self.assertIn("first", self.steer.read_text())
        self.hook("PostToolUse")
        self.assertIn("already delivered", self.send("s1", "again")[2])
        self.assertIn("steer id", self.send("bad id", "x")[2])
        self.assertIn("empty", self.send("s3", "  \n")[2])
        self.assertIn("exceeds", self.send("s3", "x" * 9000)[2])
        self.events.write_text(json.dumps({"type": "turn.completed"}) + "\n")
        self.assertIn("turn has ended", self.send("s3", "late")[2])
        self.assertFalse(self.steer.exists())
        self.assertEqual([p.name for p in self.root.iterdir() if p.name.startswith(".")], [])

    def test_send_refuses_a_dispatch_record_without_steering(self):
        self.dispatch.write_text(json.dumps({"artifacts": {"events": str(self.events)}}))
        code, _, error = self.send("s1", "x")
        self.assertEqual(code, 2)
        self.assertIn("predates steering", error)


class InstallTests(unittest.TestCase):
    def test_install_appends_once_and_keeps_existing_hooks_in_place(self):
        with tempfile.TemporaryDirectory(prefix="orchestrator-codex-home-") as home:
            hooks = Path(home) / "hooks.json"
            existing = {"hooks": {"PostToolUse": [{"hooks": [{"type": "command", "command": "other-hook"}]}]},
                        "description": "kept"}
            hooks.write_text(json.dumps(existing))
            hooks.chmod(0o600)

            def install():
                result = subprocess.run([sys.executable, str(SCRIPT), "install", "--codex-home", home],
                                        capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stderr)
                return json.loads(result.stdout)

            self.assertEqual(install()["added"], ["PostToolUse", "Stop"])
            config = json.loads(hooks.read_text())
            self.assertEqual(config["description"], "kept")
            self.assertEqual(config["hooks"]["PostToolUse"][0], existing["hooks"]["PostToolUse"][0])
            ours = config["hooks"]["PostToolUse"][1]["hooks"][0]
            self.assertIn("codex_steer.py\" hook", ours["command"])
            self.assertEqual(config["hooks"]["Stop"][0]["hooks"][0], ours)
            self.assertEqual(hooks.stat().st_mode & 0o777, 0o600)
            self.assertEqual(len(list(Path(home).glob("hooks.json.bak-*"))), 1)
            self.assertEqual(install()["added"], [])
            self.assertEqual(json.loads(hooks.read_text()), config)


if __name__ == "__main__":
    unittest.main()
