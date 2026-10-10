#!/usr/bin/env python3
"""Probes for the status-contract and message-guard role hooks, run as the harness runs them."""

import json
from pathlib import Path
import subprocess
import sys
import unittest


HERE = Path(__file__).parent


def run(script, payload):
    raw = payload if isinstance(payload, str) else json.dumps(payload)
    result = subprocess.run([sys.executable, str(HERE / script)], input=raw, capture_output=True, text=True, timeout=5)
    return result.returncode, (json.loads(result.stdout) if result.stdout.strip() else None)


class StatusContractTests(unittest.TestCase):
    def stop(self, message, **extra):
        return run("status_contract.py", {"hook_event_name": "SubagentStop", "stop_hook_active": False,
                                          "last_assistant_message": message, **extra})

    def test_status_lines_pass(self):
        for message in ("Report at /tmp/r.md\nDONE", "path\n\nBLOCKED: no fixture\n", "x\n**ESCALATE: scope**",
                        "x\n`CHECKPOINT: two files left`", "DONE"):
            with self.subTest(message=message):
                self.assertEqual(self.stop(message), (0, None))

    def test_missing_or_misplaced_status_blocks_once(self):
        for message in ("All finished.", "DONE\nThen one more remark.", "BLOCKED:", "done", ""):
            with self.subTest(message=message):
                code, output = self.stop(message)
                self.assertEqual((code, output["decision"]), (0, "block"))
                self.assertIn("Do not redo the work", output["reason"])
        self.assertEqual(self.stop("All finished.", stop_hook_active=True), (0, None))

    def test_absent_field_or_bad_input_fails_open(self):
        self.assertEqual(run("status_contract.py", {"hook_event_name": "Stop", "stop_hook_active": False}), (0, None))
        self.assertEqual(run("status_contract.py", "not json"), (0, None))
        self.assertEqual(run("status_contract.py", "[]"), (0, None))


class MessageGuardTests(unittest.TestCase):
    def send(self, tool_input):
        code, output = run("message_guard.py", {"hook_event_name": "PreToolUse", "tool_name": "SendMessage",
                                                "tool_input": tool_input})
        self.assertEqual(code, 0)
        return output and output["hookSpecificOutput"]["permissionDecision"]

    def test_only_main_is_a_recipient(self):
        self.assertIsNone(self.send({"to": "main", "message": "ESCALATE: schema migration drops a column"}))
        for to in ("implementer-1", "a1b2c3d4", "worker [3fa9c1]", "Main", "", None):
            with self.subTest(to=to):
                self.assertEqual(self.send({"to": to, "message": "please also edit x.py"}), "deny")

    def test_idle_subscription_is_denied_even_to_main(self):
        self.assertEqual(self.send({"to": "main", "notify_when_idle": True}), "deny")

    def test_shutdown_reply_is_allowed(self):
        self.assertIsNone(self.send({"to": "team-lead", "message": {
            "type": "shutdown_response", "request_id": "r1", "approve": True}}))

    def test_unreadable_input_is_denied(self):
        for payload in ("not json", "[]", {"tool_name": "SendMessage"}):
            with self.subTest(payload=payload):
                code, output = run("message_guard.py", payload)
                self.assertEqual((code, output["hookSpecificOutput"]["permissionDecision"]), (0, "deny"))


if __name__ == "__main__":
    unittest.main()
