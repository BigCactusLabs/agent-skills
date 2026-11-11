#!/usr/bin/env python3
"""Regression probes for launch identity, EOF, permissions, sandbox roots, and artifact retention; no live agents."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("dispatch.py")
THREAD = "12345678-1234-1234-1234-123456789abc"
CACHES = {"UV_CACHE_DIR": "uv", "npm_config_cache": "npm", "PIP_CACHE_DIR": "pip", "XDG_CACHE_HOME": "xdg"}
# The stub rejects what codex-cli 0.167.0 rejects: `exec resume` and `exec fork` have no --add-dir.
FAKE = '''#!/usr/bin/env python3
import json, os, pathlib, sys
args = sys.argv[1:]
if args[1:2] in (["resume"], ["fork"]) and "--add-dir" in args:
    print("error: unexpected argument '--add-dir' found", file=sys.stderr)
    sys.exit(2)
prompt = sys.stdin.read()
pathlib.Path(args[args.index("--output-last-message") + 1]).write_text("full report\\nDONE\\n")
print(json.dumps({"type":"thread.started", "thread_id":"12345678-1234-1234-1234-123456789abc"}))
print(json.dumps({"type":"probe", "argv":args, "prompt":prompt, "cwd":os.getcwd(), "pid":os.getpid(),
                  "tmpdir":os.environ.get("TMPDIR"),
                  "caches":{k: os.environ.get(k) for k in ("UV_CACHE_DIR", "npm_config_cache", "PIP_CACHE_DIR", "XDG_CACHE_HOME")}}))
code = int(os.environ.get("STUB_WORKER_EXIT", "0"))
print(json.dumps({"type": "turn.failed" if code else "turn.completed"}))
print("stub stderr", file=sys.stderr)
sys.exit(code)
'''


def writable_roots(argv):
    """The roots passed through `-c sandbox_workspace_write.writable_roots=[...]`, or None when absent."""
    prefix = "sandbox_workspace_write.writable_roots="
    values = [argv[i + 1] for i, flag in enumerate(argv) if flag == "-c" and argv[i + 1].startswith(prefix)]
    return json.loads(values[0][len(prefix):]) if values else None


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
        # TMPDIR makes the test root the lead's temp root, so per-generation temp dirs stay inside the test.
        self.env = {**os.environ, "PATH": f"{binary}{os.pathsep}{os.environ['PATH']}", "TMPDIR": str(self.root)}
        self.brief = self.root / "brief.md"
        self.brief.write_text("Repair the named case.\nSecond paragraph.\n")
        self.record = {
            "task": "TASK-49", "generation": 1, "brief_revision": 1,
            "action": "start", "workspace": str(self.workspace),
            "brief": str(self.brief), "artifact_dir": str(self.root / "artifacts"),
            "model": "gpt-6.1-sol", "effort": "medium", "permission_mode": "read-only",
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

    def test_every_action_ignores_execpolicy_rules(self):
        # An `allow` rule runs a matching simple command outside the sandbox; without this flag the sandbox
        # mode is a label, not a boundary (probed 2026-11-10).
        for run, action in enumerate(("start", "resume", "fork"), start=1):
            for mode in ("read-only", "workspace-write"):
                with self.subTest(action=action, mode=mode):
                    run_number = run * 2 - (mode == "read-only")
                    record = {**self.record, "generation": run_number, "action": action, "permission_mode": mode,
                              **({"thread_id": THREAD} if action != "start" else {})}
                    self.assertEqual(self.run_record(record).returncode, 0)
                    self.assertIn("--ignore-rules", self.probe(run_number)["argv"])

    def test_permission_mode_is_explicit_and_not_promoted(self):
        for run, mode in enumerate(("read-only", "workspace-write"), start=1):
            result = self.run_record({**self.record, "generation": run, "permission_mode": mode})
            self.assertEqual(result.returncode, 0, result.stderr)
            argv = self.probe(run)["argv"]
            self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", argv)
            self.assertNotIn("--add-dir", argv)
            self.assertIn(f'sandbox_mode="{mode}"', argv)
            # workspace-write: the lead's temp root and the artifact dir; network pinned on; worker-only caches
            sandboxed = mode == "workspace-write"
            self.assertEqual(writable_roots(argv), [str(self.root), str(self.root / "artifacts")] if sandboxed else None)
            self.assertEqual("sandbox_workspace_write.network_access=true" in argv, sandboxed)
            redirected = {name: str(self.root / "orchestrator-cache" / sub) for name, sub in CACHES.items()}
            self.assertEqual(self.probe(run)["caches"],
                             redirected if sandboxed else {name: self.env.get(name) for name in CACHES})
            self.assertEqual(json.loads(self.artifact("dispatch.json", run).read_text())["worker_env"],
                             redirected if sandboxed else {})

    def test_workspace_write_resume_and_fork_keep_their_roots(self):
        for run, action in enumerate(("resume", "fork"), start=1):
            record = {**self.record, "generation": run, "action": action, "thread_id": THREAD,
                      "permission_mode": "workspace-write"}
            result = self.run_record(record)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(writable_roots(self.probe(run)["argv"]), [str(self.root), str(self.root / "artifacts")])

    def test_unsupported_permission_modes_never_launch(self):
        for mode in ("bypass", "danger-full-access", "approve-for-me"):
            with self.subTest(mode=mode):
                result = self.run_record({**self.record, "permission_mode": mode})
                self.assertEqual(result.returncode, 2)
                self.assertIn("permission_mode", result.stderr)
                self.assertFalse((self.root / "artifacts").exists())

    def test_network_is_a_workspace_write_boolean(self):
        record = {**self.record, "permission_mode": "workspace-write", "network": False}
        self.assertEqual(self.run_record(record).returncode, 0)
        self.assertIn("sandbox_workspace_write.network_access=false", self.probe()["argv"])
        for bad in ({**record, "network": "yes"}, {**self.record, "network": True}):
            result = self.run_record({**bad, "generation": 2})
            self.assertEqual(result.returncode, 2)
            self.assertIn("network is a boolean and applies only to workspace-write", result.stderr)

    def test_a_linked_worktree_gets_its_commit_paths_but_not_the_repo_config(self):
        common = self.root / "main" / ".git"
        gitdir = common / "worktrees" / "wt"
        for name in ("objects", "refs", "logs", "hooks"):
            (common / name).mkdir(parents=True)
        gitdir.mkdir(parents=True)
        (gitdir / "commondir").write_text("../..\n")
        (self.workspace / ".git").write_text(f"gitdir: {gitdir}\n")
        (self.workspace / "pkg").mkdir()
        record = {**self.record, "permission_mode": "workspace-write", "workspace": str(self.workspace / "pkg")}
        self.assertEqual(self.run_record(record).returncode, 0)
        self.assertEqual(writable_roots(self.probe()["argv"]),
                         [str(self.root), str(self.root / "artifacts"), str(gitdir), str(common / "objects"),
                          str(common / "refs"), str(common / "logs")])
        (self.workspace / ".git").unlink()
        (self.workspace / ".git").mkdir()  # an ordinary checkout: its .git is already inside the workspace
        self.assertEqual(self.run_record({**record, "generation": 2}).returncode, 0)
        self.assertEqual(writable_roots(self.probe(run=2)["argv"]), [str(self.root), str(self.root / "artifacts")])

    def test_an_unreadable_git_pointer_or_a_separate_git_dir_gets_no_git_grant(self):
        record = {**self.record, "permission_mode": "workspace-write"}
        elsewhere = self.root / "separate.git"
        elsewhere.mkdir()  # --separate-git-dir: a gitdir with no commondir
        for run, pointer in enumerate(("not a pointer\n", f"gitdir: {elsewhere}\n"), start=1):
            (self.workspace / ".git").write_text(pointer)
            self.assertEqual(self.run_record({**record, "generation": run}).returncode, 0)
            self.assertEqual(writable_roots(self.probe(run)["argv"]), [str(self.root), str(self.root / "artifacts")])

    def test_writable_roots_survive_quotes_in_paths(self):
        artifacts = self.root / 'odd "quoted" \\ dir'
        record = {**self.record, "permission_mode": "workspace-write", "artifact_dir": str(artifacts)}
        result = self.run_record(record)
        self.assertEqual(result.returncode, 0, result.stderr)
        argv = next(event for event in map(json.loads, (artifacts / "TASK-49.g1.events.jsonl").read_text().splitlines())
                    if event["type"] == "probe")["argv"]
        self.assertEqual(writable_roots(argv), [str(self.root), str(artifacts)])

    def check_worktree(self, path):
        return subprocess.run([sys.executable, str(SCRIPT), "--check-worktree", str(path)], env=self.env,
                              capture_output=True, text=True, timeout=5)

    def git(self, *command):
        env = {**self.env, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false",
                               *command], capture_output=True, text=True, timeout=20, env=env)

    def linked_worktree(self):
        main, linked = self.root / "main", self.root / "linked"
        for command in (["init", "-q", str(main)], ["-C", str(main), "commit", "-q", "--allow-empty", "-m", "base"],
                        ["-C", str(main), "worktree", "add", "-q", str(linked)]):
            result = self.git(*command)
            self.assertEqual(result.returncode, 0, result.stderr)
        return main, linked, main / ".git" / "worktrees" / "linked"

    @unittest.skipUnless(shutil.which("git"), "needs git to build a real linked worktree")
    def test_check_worktree_accepts_what_git_writes(self):
        main, linked, gitdir = self.linked_worktree()
        (linked / "pkg").mkdir()
        result = self.check_worktree(linked)
        self.assertEqual((result.returncode, result.stdout), (0, ""), result.stderr)
        respelled = self.root / "LINKED"
        if respelled.exists():  # a case-insensitive volume: the same worktree under another spelling
            self.assertEqual(self.check_worktree(respelled).returncode, 0)
        if self.git("-C", str(main), "worktree", "add", "-q", "--relative-paths", str(self.root / "relative")).returncode == 0:
            self.assertEqual(self.check_worktree(self.root / "relative").stdout, "")
        result = self.check_worktree(main)  # an ordinary checkout has no pointers to check, and says so
        self.assertEqual(result.returncode, 0)
        self.assertIn("is not a linked worktree", result.stdout)
        for wrong in (linked / "pkg", self.root / "missing"):  # a path inside the worktree is not its root
            self.assertEqual(self.check_worktree(wrong).returncode, 2)
        self.assertEqual(subprocess.run([sys.executable, str(SCRIPT)], env=self.env, capture_output=True).returncode, 2)

    @unittest.skipUnless(shutil.which("git"), "needs git to build a real linked worktree")
    def test_check_worktree_names_each_tampered_pointer(self):
        main, linked, gitdir = self.linked_worktree()
        originals = {name: (gitdir / name).read_bytes() for name in ("commondir", "gitdir")}
        self.assertEqual(originals["commondir"], b"../..\n")
        evil = self.root / "evil"
        evil.mkdir()
        (gitdir / " ..").mkdir()  # with " ../.." git resolves commondir to the gitdir itself; Python's strip() would not
        for name, tampered, expected in (("commondir", f"{evil}\n".encode(), "commondir holds"),
                                         ("commondir", b" ../..\n", "commondir holds"),
                                         ("commondir", f"{main / '.git'}\n".encode(), "commondir holds"),
                                         ("commondir", None, "commondir is missing"),
                                         ("gitdir", f"{evil}/.git\n".encode(), "does not point back at"),
                                         ("gitdir", None, "does not point back at")):
            with self.subTest(name=name, tampered=tampered):
                (gitdir / name).unlink()
                if tampered is not None:
                    (gitdir / name).write_bytes(tampered)
                result = self.check_worktree(linked)
                self.assertEqual(result.returncode, 1)
                self.assertIn("check-worktree: tampered:", result.stdout)
                self.assertIn(expected, result.stdout)
                (gitdir / name).write_bytes(originals[name])
        self.assertEqual(self.check_worktree(linked).returncode, 0)
        (gitdir / "config").write_text("[core]\n\tfsmonitor = /tmp/x\n")
        result = self.check_worktree(linked)
        self.assertEqual(result.returncode, 1)
        self.assertIn("git never writes a config in a worktree's gitdir", result.stdout)

    @unittest.skipUnless(shutil.which("git"), "needs git to build a real linked worktree")
    def test_check_worktree_reports_nested_repositories_and_an_active_worktree_config(self):
        main, linked, gitdir = self.linked_worktree()
        (gitdir / "config.worktree").write_text("[core]\n\tfsmonitor = /tmp/x\n")
        self.assertEqual(self.check_worktree(linked).returncode, 0)  # inert until the repo enables worktreeConfig
        with (main / ".git" / "config").open("a") as config:
            config.write("[extensions]\n\tworktreeConfig = true\n")
        result = self.check_worktree(linked)
        self.assertEqual(result.returncode, 1)
        self.assertIn("check-worktree: inspect:", result.stdout)
        self.assertIn("config.worktree is loaded by git", result.stdout)
        (gitdir / "config.worktree").unlink()
        (linked / "pkg" / "deep" / ".git").mkdir(parents=True)  # a planted repository
        (linked / "vendor").mkdir()
        (linked / "vendor" / ".git").write_text("gitdir: /somewhere\n")  # a submodule-style pointer
        result = self.check_worktree(linked)
        self.assertEqual(result.returncode, 1)
        for folder in ("pkg/deep", "vendor"):
            self.assertIn(f"inspect: repository inside the worktree at {linked / folder}", result.stdout)
        hidden, outside = linked / "locked", self.root / "outside"
        (hidden / ".git").mkdir(parents=True)
        hidden.chmod(0o111)  # cannot be listed, can still be entered: os.walk alone would skip it silently
        self.addCleanup(hidden.chmod, 0o755)
        (outside / ".git").mkdir(parents=True)
        (linked / "link").symlink_to(outside)  # a repository reached through a symlinked directory
        expected = [linked / "locked", linked / "link"]
        if (self.root / "LINKED").exists():  # case-insensitive volume: git finds .GIT when it looks for .git
            (linked / "upper" / ".GIT").mkdir(parents=True)
            expected.append(linked / "upper")
        result = self.check_worktree(linked)
        for folder in expected:
            self.assertIn(f"inspect: repository inside the worktree at {folder}", result.stdout)
        result = self.check_worktree(linked / "pkg" / "deep")  # asked about the planted repository itself
        self.assertEqual(result.returncode, 1)
        self.assertIn(f"sits inside the tree at {linked}", result.stdout)
        forged = gitdir / "worktrees" / "x"  # a pointer file in a subdirectory, aimed inside the writable gitdir
        forged.mkdir(parents=True)
        (forged / "commondir").write_bytes(b"../..\n")
        (linked / "sub").mkdir()
        (linked / "sub" / ".git").write_text(f"gitdir: {forged}\n")
        (forged / "gitdir").write_text(f"{linked / 'sub' / '.git'}\n")
        result = self.check_worktree(linked / "sub")
        self.assertEqual(result.returncode, 1)
        self.assertIn("tampered:", result.stdout)
        self.assertIn("sits inside another worktree's gitdir", result.stdout)
        (gitdir / "commondir").write_bytes(b"/elsewhere\n")
        self.assertTrue(self.check_worktree(linked).stdout.startswith("check-worktree: tampered:"))  # breaches first

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
            # the losing caller made no temp dir: one generation, one TMPDIR
            self.assertEqual(len(list(self.root.glob("orch-TASK-49.g1.*"))), 1)
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
                      {"workspace": "relative"}, {"task": "../escape"}, {"effrot": "max"}, {"user_gated": True},
                      {"lead_inbox": False}):
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

    def test_each_generation_gets_a_private_tmpdir_outside_the_workspace(self):
        self.assertEqual(self.run_record().returncode, 0)
        self.assertEqual(self.run_record({**self.record, "generation": 2}).returncode, 0)
        first, second = (Path(self.probe(run)["tmpdir"]) for run in (1, 2))
        self.assertNotEqual(first, second)
        for run, path in ((1, first), (2, second)):
            self.assertTrue(path.is_dir())
            self.assertEqual(path.parent, self.root)  # under the lead's temp root, not the worktree
            self.assertTrue(path.name.startswith(f"orch-TASK-49.g{run}."))
            self.assertEqual(json.loads(self.artifact("dispatch.json", run).read_text())["tmpdir"], str(path))

    def test_a_temp_root_inside_the_workspace_or_a_repo_is_refused(self):
        self.env["TMPDIR"] = str(self.workspace / "tmp")
        (self.workspace / "tmp").mkdir()
        result = self.run_record()
        self.assertEqual(result.returncode, 2)
        self.assertIn("temp root is inside the workspace", result.stderr)
        respelled = self.root / self.workspace.name.upper() / "tmp"
        if respelled.exists():  # a case-insensitive volume: another spelling of the same directory
            self.env["TMPDIR"] = str(respelled)
            result = self.run_record()
            self.assertEqual(result.returncode, 2)
            self.assertIn("temp root is inside the workspace", result.stderr)
        repo = self.root / "repo"
        (repo / ".git").mkdir(parents=True)
        (repo / "tmp").mkdir()
        self.env["TMPDIR"] = str(repo / "tmp")
        result = self.run_record()
        self.assertEqual(result.returncode, 2)
        self.assertIn("inside the git repository", result.stderr)
        self.assertFalse(self.artifact("dispatch.json").exists())


if __name__ == "__main__":
    unittest.main()
