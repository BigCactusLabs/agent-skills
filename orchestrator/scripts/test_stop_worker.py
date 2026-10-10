#!/usr/bin/env python3
"""Stop-helper probes against a stub Codex launched through dispatch.py; no live agents."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest


HERE = Path(__file__).parent
FAKE = '''#!/usr/bin/env python3
import json, os, signal, subprocess, sys, time
mode = os.environ.get("STUB_MODE", "interrupt")
def interrupted(*_):
    sys.exit(1)  # like exec on 0.160.0: an interrupted turn writes no closing event
if mode == "child":
    child = subprocess.Popen(["sleep", "60"], start_new_session=True)
    print(json.dumps({"type": "child", "pid": child.pid}), flush=True)
if mode in ("interrupt", "child"):
    signal.signal(signal.SIGINT, interrupted)
else:
    signal.signal(signal.SIGINT, signal.SIG_IGN)
if mode == "stubborn":
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
print(json.dumps({"type": "turn.started"}), flush=True)
while True:
    time.sleep(0.05)
'''


class StopWorkerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="orchestrator-stop-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        binary = self.root / "bin"
        binary.mkdir()
        (binary / "codex").write_text(FAKE)
        (binary / "codex").chmod(0o755)
        self.env = {**os.environ, "PATH": f"{binary}{os.pathsep}{os.environ['PATH']}"}
        (self.root / "brief.md").write_text("Work until stopped.\n")
        self.record = {
            "task": "TASK-7", "run": 1, "brief_revision": 1, "action": "start",
            "workspace": str(self.root), "brief": str(self.root / "brief.md"),
            "artifact_dir": str(self.root / "artifacts"), "model": "gpt-6-luna",
            "effort": "max", "permission_mode": "read-only",
        }
        self.dispatch = self.root / "artifacts" / "TASK-7.r1.dispatch.json"
        self.events = self.root / "artifacts" / "TASK-7.r1.events.jsonl"

    def launch(self, mode):
        (self.root / "run.json").write_text(json.dumps(self.record))
        worker = subprocess.Popen([sys.executable, str(HERE / "dispatch.py"), str(self.root / "run.json")],
                                  env={**self.env, "STUB_MODE": mode}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(lambda: worker.poll() is None and (worker.kill(), worker.wait()))
        deadline = time.monotonic() + 5
        while '"turn.started"' not in (self.events.read_text() if self.events.exists() else ""):
            self.assertLess(time.monotonic(), deadline, "stub never started")
            time.sleep(0.05)
        return worker

    def stop(self, path=None, grace="2", term_grace="1"):
        result = subprocess.run([sys.executable, str(HERE / "stop_worker.py"), str(path or self.dispatch),
                                 "--grace", grace, "--term-grace", term_grace], capture_output=True, text=True, timeout=15)
        return result.returncode, (json.loads(result.stdout) if result.stdout else None), result.stderr

    def test_sigint_interrupts_and_worker_exit_code_is_one(self):
        worker = self.launch("interrupt")
        code, report, _ = self.stop()
        self.assertEqual(code, 0)
        self.assertEqual(report["outcome"], "stopped_by_sigint")
        self.assertEqual(report["signals"], ["SIGINT"])
        self.assertEqual(report["last_event"], {"type": "turn.started"})
        self.assertEqual(worker.wait(timeout=5), 1)

    def test_ignored_sigint_escalates_to_sigterm(self):
        worker = self.launch("ignore_int")
        code, report, _ = self.stop()
        self.assertEqual((code, report["outcome"], report["signals"]), (0, "stopped_by_sigterm", ["SIGINT", "SIGTERM"]))
        self.assertEqual(worker.wait(timeout=5), -15)

    def test_survivor_is_reported_never_killed(self):
        worker = self.launch("stubborn")
        code, report, _ = self.stop(grace="1", term_grace="1")
        self.assertEqual((code, report["outcome"]), (1, "still_running"))
        self.assertNotIn("SIGKILL", report["signals"])
        self.assertIsNone(worker.poll())

    def test_surviving_descendant_is_listed(self):
        self.launch("child")
        child = next(json.loads(line)["pid"] for line in self.events.read_text().splitlines() if '"child"' in line)
        self.addCleanup(lambda: subprocess.run(["kill", str(child)], capture_output=True))
        code, report, _ = self.stop()
        self.assertEqual((code, report["outcome"]), (0, "stopped_by_sigint"))
        self.assertEqual([entry["pid"] for entry in report["surviving_descendants"]], [child])

    def test_reused_pid_is_not_signalled(self):
        bystander = subprocess.Popen(["sleep", "30"])
        self.addCleanup(lambda: (bystander.kill(), bystander.wait()))
        self.dispatch.parent.mkdir()
        self.dispatch.write_text(json.dumps({"pid": bystander.pid, "artifacts": {
            "last_message": str(self.root / "artifacts" / "TASK-7.r1.last.md"), "events": str(self.events)}}))
        code, report, _ = self.stop()
        self.assertEqual((code, report["outcome"]), (2, "identity_mismatch"))
        self.assertIsNone(bystander.poll())

    def test_finished_run_is_not_running(self):
        worker = self.launch("interrupt")
        worker.send_signal(2)
        worker.wait(timeout=5)
        code, report, _ = self.stop()
        self.assertEqual((code, report["outcome"], report["signals"]), (0, "not_running", []))

    def test_missing_dispatch_record_fails_closed(self):
        code, report, stderr = self.stop(self.root / "absent.dispatch.json")
        self.assertEqual((code, report), (2, None))
        self.assertIn("stop_worker", stderr)


if __name__ == "__main__":
    unittest.main()
