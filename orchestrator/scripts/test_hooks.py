#!/usr/bin/env python3
"""Probes for the hooks that ship with the skill (status contract, message guard, compaction re-read), run as the harness runs them."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
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
                        "x\n`CHECKPOINT: two files left`", "DONE", "x\nStatus: DONE", "x\n**Status:** DONE",
                        "x\nstatus: BLOCKED: no fixture"):
            with self.subTest(message=message):
                self.assertEqual(self.stop(message), (0, None))

    def test_missing_or_misplaced_status_blocks_once(self):
        for message in ("All finished.", "DONE\nThen one more remark.", "BLOCKED:", "done", "",
                        "Waiting for the test run to finish.", "Status: pending", "VERDICT: APPROVE"):
            with self.subTest(message=message):
                code, output = self.stop(message)
                self.assertEqual((code, output["decision"]), (0, "block"))
                self.assertIn("Do not redo finished work", output["reason"])
                self.assertIn("wait for it in the foreground", output["reason"])
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



class CompactRereadTests(unittest.TestCase):
    SKILL_CALL = {"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Skill", "input": {"skill": "orchestrator"}}]}}
    SLASH = {"type": "user", "message": {"content":
             "<command-message>cm-orchestrator</command-message>\n<command-name>/cm-orchestrator</command-name>"}}
    REATTACHED = {"type": "attachment", "attachment": {"type": "invoked_skills", "skills": [
        {"name": "cm-orchestrator", "path": "userSettings:cm-orchestrator"}]}}

    def fire(self, records, source="compact", **extra):
        with tempfile.TemporaryDirectory() as tmp:
            transcript = Path(tmp) / "session.jsonl"
            transcript.write_text("".join(json.dumps(record) + "\n" for record in records))
            payload = {"hook_event_name": "SessionStart", "source": source, "transcript_path": str(transcript), **extra}
            result = subprocess.run([sys.executable, str(HERE / "compact_reread.py")], input=json.dumps(payload),
                                    capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0)
        return result.stdout

    def test_each_invocation_record_prompts_the_reread(self):
        for record, edition in ((self.SKILL_CALL, "orchestrator"), (self.SLASH, "cm-orchestrator"),
                                (self.REATTACHED, "cm-orchestrator")):
            with self.subTest(record=record["type"]):
                output = self.fire([{"type": "user", "message": {"content": "hello"}}, record])
                self.assertIn(f"invoked the {edition} skill", output)
                self.assertIn("run manifest", output)
                self.assertEqual("code-mode.md" in output, edition == "cm-orchestrator")
        self.assertIn("cm-orchestrator and orchestrator", self.fire([self.SKILL_CALL, self.SLASH]))

    def test_quoted_mentions_and_other_sessions_stay_silent(self):
        quoted = '<command-name>/orchestrator</command-name> {"name": "Skill", "input": {"skill": "orchestrator"}}'
        quiet = [
            {"type": "user", "message": {"content": [{"type": "tool_result", "content": quoted}]}},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": quoted}]}},
            {"type": "user", "message": {"content": "see " + quoted}},
            {"type": "assistant", "isSidechain": True, "message": self.SKILL_CALL["message"]},
            {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Skill", "input": {"skill": "frontier-search"}}]}},
            {"type": "attachment", "attachment": {"type": "skill_mention", "skillName": "orchestrator"}},
        ]
        self.assertEqual(self.fire(quiet), "")
        self.assertEqual(self.fire([self.SKILL_CALL], source="resume"), "")
        self.assertEqual(self.fire([self.SKILL_CALL], agent_id="a1", agent_type="implementer-opus"), "")

    def test_unreadable_input_fails_open(self):
        for raw in ("not json", "[]", '{"source": "compact"}',
                    '{"source": "compact", "transcript_path": "/nonexistent/session.jsonl"}'):
            with self.subTest(raw=raw):
                result = subprocess.run([sys.executable, str(HERE / "compact_reread.py")], input=raw,
                                        capture_output=True, text=True, timeout=5)
                self.assertEqual((result.returncode, result.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()
