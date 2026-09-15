#!/usr/bin/env python3
"""Regression probes for launch identity, EOF, permissions, and artifact retention; no live agents."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("dispatch.py")
THREAD = "12345678-1234-1234-1234-123456789abc"
FAKE = '''#!/usr/bin/env python3
import json, os, pathlib, sys
args = sys.argv[1:]
prompt = sys.stdin.read()
pathlib.Path(args[args.index("--output-last-message") + 1]).write_text("full report\\nDONE\\n")
print(json.dumps({"type":"thread.started", "thread_id":"12345678-1234-1234-1234-123456789abc"}))
print(json.dumps({"type":"probe", "argv":args, "prompt":prompt, "cwd":os.getcwd(), "pid":os.getpid()}))
code = int(os.environ.get("STUB_WORKER_EXIT", "0"))
print(json.dumps({"type": "turn.failed" if code else "turn.completed"}))
print("stub stderr", file=sys.stderr)
sys.exit(code)
'''


class DispatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="orchestrator-dispatch-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.workspace = self.root / "worktree with spaces"
        self.workspace.mkdir()
        binary = self.root / "bin"
        binary.mkdir()
        (binary / "codex").write_text(FAKE)
        (binary / "codex").chmod(0o755)
        self.env = {**os.environ, "PATH": f"{binary}{os.pathsep}{os.environ['PATH']}"}
        self.brief = self.root / "brief.md"
        self.brief.write_text("Repair the named case.\nSecond paragraph.\n")
        self.record = {
            "task": "TASK-49", "generation": 1, "brief_revision": 1,
            "action": "start", "workspace": str(self.workspace),
            "brief": str(self.brief), "artifact_dir": str(self.root / "artifacts"),
            "model": "gpt-5.6-sol", "effort": "medium", "permission_mode": "read-only",
        }

    def args(self, record=None):
        path = self.root / "run.json"
        path.write_text(json.dumps(self.record if record is None else record))
        return [sys.executable, str(SCRIPT), str(path)]

    def run_record(self, record=None, **kwargs):
        return subprocess.run(self.args(record), env=self.env, capture_output=True, text=True, timeout=5, **kwargs)

    def artifact(self, suffix, run=1):
        return self.root / "artifacts" / f"TASK-49.g{run}.{suffix}"

    def probe(self, run=1):
        return next(event for event in map(json.loads, self.artifact("events.jsonl", run).read_text().splitlines()) if event["type"] == "probe")

    def test_start_preserves_cwd_prompt_and_process_identity(self):
        result = self.run_record()
        self.assertEqual(result.returncode, 0, result.stderr)
        probe = self.probe()
        dispatch = json.loads(self.artifact("dispatch.json").read_text())
        self.assertEqual(probe["cwd"], str(self.workspace))
        self.assertEqual(probe["prompt"], self.brief.read_text())
        self.assertEqual(probe["pid"], dispatch["pid"])
        self.assertIsNone(dispatch["runtime_model"])
        self.assertIsNone(dispatch["runtime_effort"])
        self.assertFalse(self.artifact("report.md").exists())
        self.assertEqual(self.artifact("last.md").read_text(), "full report\nDONE\n")
        self.assertIn("stub stderr", self.artifact("stderr").read_text())

    def test_missing_fields_fail_before_launch(self):
        for field in ("model", "effort", "workspace", "permission_mode", "generation", "brief_revision"):
            with self.subTest(field=field):
                record = {key: value for key, value in self.record.items() if key != field}
                result = self.run_record(record)
                self.assertEqual(result.returncode, 2)
                self.assertIn(field, result.stderr)
                self.assertFalse((self.root / "artifacts").exists())

    def test_resume_and_fork_pin_settings_and_retain_old_runs(self):
        self.assertEqual(self.run_record().returncode, 0)
        prior = self.artifact("last.md").read_bytes()
        for run, action in enumerate(("resume", "fork"), start=2):
            record = {**self.record, "generation": run, "action": action, "thread_id": THREAD,
                      "model": "gpt-6-astra", "effort": "low"}
            result = self.run_record(record)
            self.assertEqual(result.returncode, 0, result.stderr)
            argv = self.probe(run)["argv"]
            self.assertEqual(argv[:2], ["exec", action])
            self.assertEqual(argv[argv.index("-m") + 1], "gpt-6-astra")
            self.assertIn('model_reasoning_effort="low"', argv)
            self.assertIn('sandbox_mode="read-only"', argv)
            self.assertEqual(argv[-2:], [THREAD, "-"])
            self.assertNotIn("--cd", argv)
            self.assertNotIn("-s", argv)
            self.assertEqual(self.artifact("last.md").read_bytes(), prior)

    def test_permission_mode_is_explicit_and_not_promoted(self):
        for run, mode in enumerate(("read-only", "workspace-write"), start=1):
            result = self.run_record({**self.record, "generation": run, "permission_mode": mode})
            self.assertEqual(result.returncode, 0, result.stderr)
            argv = self.probe(run)["argv"]
            self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", argv)
            self.assertIn(f'sandbox_mode="{mode}"', argv)

    def test_unsupported_permission_modes_never_launch(self):
        for mode in ("bypass", "danger-full-access", "approve-for-me"):
            with self.subTest(mode=mode):
                result = self.run_record({**self.record, "permission_mode": mode})
                self.assertEqual(result.returncode, 2)
                self.assertIn("permission_mode", result.stderr)
                self.assertFalse((self.root / "artifacts").exists())

    def test_skip_repo_check_requires_an_explicit_boolean(self):
        self.assertEqual(self.run_record().returncode, 0)
        self.assertNotIn("--skip-git-repo-check", self.probe()["argv"])
        record = {**self.record, "generation": 2, "skip_git_repo_check": True}
        self.assertEqual(self.run_record(record).returncode, 0)
        self.assertIn("--skip-git-repo-check", self.probe(2)["argv"])
        self.assertEqual(self.run_record({**record, "generation": 3, "skip_git_repo_check": "false"}).returncode, 2)
        self.assertFalse(self.artifact("dispatch.json", 3).exists())

    def test_duplicate_launch_keeps_all_existing_bytes(self):
        self.assertEqual(self.run_record().returncode, 0)
        saved = {path: path.read_bytes() for path in (self.root / "artifacts").iterdir()}
        result = self.run_record()
        self.assertEqual(result.returncode, 2)
        self.assertIn("advance generation", result.stderr)
        self.assertTrue(all(path.read_bytes() == data for path, data in saved.items()))

    def test_existing_report_is_not_overwritten(self):
        self.artifact("report.md").parent.mkdir()
        self.artifact("report.md").write_text("earlier evidence")
        self.assertEqual(self.run_record().returncode, 2)
        self.assertEqual(self.artifact("report.md").read_text(), "earlier evidence")
        self.assertFalse(self.artifact("dispatch.json").exists())

    def test_racing_callers_launch_one_worker_for_the_generation(self):
        args = self.args()
        first = subprocess.Popen(args, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        second = subprocess.Popen(args, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            first.communicate(timeout=5)
            second.communicate(timeout=5)
            self.assertEqual(sorted([first.returncode, second.returncode]), [0, 2])
            events = list(map(json.loads, self.artifact("events.jsonl").read_text().splitlines()))
            self.assertEqual(sum(event["type"] == "probe" for event in events), 1)
        finally:
            for process in (first, second):
                if process.poll() is None:
                    process.kill()
                process.communicate(timeout=5)

    def test_open_parent_stdin_cannot_hold_worker_open(self):
        process = subprocess.Popen(self.args(), env=self.env, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            self.assertEqual(process.wait(timeout=5), 0)
            self.assertEqual(self.probe()["prompt"], self.brief.read_text())
        finally:
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=5)

    def test_prompt_is_literal_not_shell_code(self):
        marker = self.root / "must-not-exist"
        self.brief.write_text(f'$(touch "{marker}")\n`touch "{marker}"`\n"quotes" \\ literal\n')
        self.assertEqual(self.run_record().returncode, 0)
        self.assertEqual(self.probe()["prompt"], self.brief.read_text())
        self.assertFalse(marker.exists())

    def test_worker_failure_exit_is_not_masked(self):
        self.env["STUB_WORKER_EXIT"] = "7"
        self.assertEqual(self.run_record().returncode, 7)
        self.assertIn('"turn.failed"', self.artifact("events.jsonl").read_text())

    def test_bad_thread_identity_or_unknown_fields_fail_closed(self):
        for extra in ({"action": "resume"}, {"thread_id": THREAD},
                      {"action": "resume", "thread_id": "--last"},
                      {"effort": "persistent"}, {"effort": "ultra"}, {"effort": "minimal"}, {"model": ""}, {"generation": True},
                      {"workspace": "relative"}, {"task": "../escape"}, {"effrot": "max"}):
            with self.subTest(extra=extra):
                self.assertEqual(self.run_record({**self.record, **extra}).returncode, 2)
                self.assertFalse((self.root / "artifacts").exists())

    def test_optional_schema_and_web_search_are_passed_literally(self):
        schema = self.root / "schema with spaces.json"
        schema.write_text('{"type":"object"}')
        self.assertEqual(self.run_record({**self.record, "web_search": "live", "output_schema": str(schema)}).returncode, 0)
        argv = self.probe()["argv"]
        self.assertIn('web_search="live"', argv)
        self.assertEqual(argv[argv.index("--output-schema") + 1], str(schema))


if __name__ == "__main__":
    unittest.main()
