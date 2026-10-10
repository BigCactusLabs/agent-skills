#!/usr/bin/env python3
"""Watch-script probes against a hand-written events file; no live agents."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("watch_events.py")


def command(text, status="failed"):
    return {"type": "item.completed", "item": {"type": "command_execution", "command": text,
                                               "status": status, "exit_code": 1 if status == "failed" else 0}}


def edit(path):
    return {"type": "item.completed", "item": {"type": "file_change", "changes": [{"path": path, "kind": "update"}]}}


class WatchEventsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="orchestrator-watch-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.events = self.root / "TASK-3.r2.events.jsonl"
        self.events.touch()
        self.dispatch = self.root / "TASK-3.r2.dispatch.json"
        self.dispatch.write_text(json.dumps({"pid": os.getpid(), "artifacts": {"events": str(self.events)}}))
        self.owned = self.root / "worktree"

    def append(self, *events):
        with self.events.open("a") as stream:
            for event in events:
                stream.write(json.dumps(event) + "\n")

    def watch(self, *extra):
        process = subprocess.Popen([sys.executable, str(SCRIPT), str(self.dispatch), "--own", str(self.owned),
                                    "--poll", "0.05", *extra], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(lambda: process.poll() is None and (process.kill(), process.communicate()))
        return process

    def test_alerts_scope_repeats_and_turn_end_then_exits(self):
        process = self.watch("--from-offset", "0")
        self.append({"type": "turn.started"}, edit(str(self.owned / "a.py")), edit("/etc/hosts"), edit("/etc/hosts"),
                    command("pytest"), command("pytest", "completed"), command("pytest"), command("pytest"),
                    command("pytest"), {"type": "turn.completed", "usage": {}})
        out, _ = process.communicate(timeout=10)
        self.assertEqual(process.returncode, 0)
        self.assertEqual(out.splitlines(), [
            "TASK-3.r2: edit outside owned paths: update /etc/hosts",
            "TASK-3.r2: same command failed 3 times: pytest",
            "TASK-3.r2: turn ended: turn.completed",
        ])

    def test_rearmed_watch_does_not_repeat_old_alerts(self):
        self.append(edit("/etc/hosts"), command("make"), command("make"))
        process = self.watch("--from-offset", str(self.events.stat().st_size))
        self.append(command("make"), {"type": "turn.failed", "error": {"message": "boom"}})
        out, _ = process.communicate(timeout=10)
        self.assertEqual(out.splitlines(), ["TASK-3.r2: same command failed 3 times: make",
                                            "TASK-3.r2: turn ended: turn.failed boom"])

    def test_turn_already_ended_is_reported_once(self):
        self.append({"type": "turn.completed"})
        out, _ = self.watch().communicate(timeout=10)
        self.assertEqual(out.splitlines(), ["TASK-3.r2: turn already ended before the watch started"])

    def test_stall_alerts_once_and_error_event_does_not_end_watch(self):
        process = self.watch("--stall-seconds", "0.5", "--from-offset", "0")
        self.append({"type": "error", "message": "Reconnecting... 1/5"})
        self.assertEqual(process.stdout.readline(), "TASK-3.r2: error event: Reconnecting... 1/5\n")
        self.assertEqual(process.stdout.readline(), "TASK-3.r2: no new event for 0.5s\n")
        self.append({"type": "turn.completed"})
        out, _ = process.communicate(timeout=10)
        self.assertEqual(out.splitlines(), ["TASK-3.r2: turn ended: turn.completed"])

    def test_exit_without_turn_end_is_reported(self):
        gone = subprocess.Popen(["true"])
        gone.wait()
        self.dispatch.write_text(json.dumps({"pid": gone.pid, "artifacts": {"events": str(self.events)}}))
        out, _ = self.watch().communicate(timeout=10)
        self.assertEqual(out.splitlines(), [f"TASK-3.r2: worker process {gone.pid} exited without a turn end"])


if __name__ == "__main__":
    unittest.main()
