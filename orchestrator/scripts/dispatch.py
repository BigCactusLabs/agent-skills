#!/usr/bin/env python3
"""Pin a Codex start/resume/fork from one run record; then replace this process."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone


REQUIRED = {
    "task", "run", "brief_revision", "action", "workspace", "brief",
    "artifact_dir", "model", "effort", "permission_mode",
}
OPTIONAL = {"thread_id", "output_schema", "web_search", "user_gated", "skip_git_repo_check", "lead_inbox", "network"}
# Package caches a sandboxed worker writes: its own store under the lead's temp root, never the user's ~/.cache, so
# a worker cannot plant a build artifact that an unsandboxed process later runs (probed: ~/.cache/uv is denied).
WORKER_CACHES = {"UV_CACHE_DIR": "uv", "npm_config_cache": "npm", "PIP_CACHE_DIR": "pip", "XDG_CACHE_HOME": "xdg"}
# `ultra` is user-gated per dispatch (SKILL.md); `minimal` is pre-5.6 legacy; `persistent` withholds turn.completed.
EFFORTS = ("none", "low", "medium", "high", "xhigh", "max", "ultra")
# The lead's Claude inbox. Only the hook gets it, renamed; worker shells get neither name (Codex shell exclude),
# nor the lead's session id, which names its run registry.
LEAD_INBOX = {"CLAUDE_CODE_MESSAGING_SOCKET": "ORCH_LEAD_SOCKET", "CLAUDE_CODE_MESSAGING_TOKEN": "ORCH_LEAD_TOKEN"}
WORKER_ENV_EXCLUDE = 'shell_environment_policy.exclude=["CLAUDE_CODE_MESSAGING_*", "ORCH_LEAD_*", "CLAUDE_CODE_SESSION_ID"]'


def run_registry(environ=os.environ):
    """This lead session's run names, so `codex_steer.py send <task>.r<run>` needs no path; None outside a session."""
    session = environ.get("CLAUDE_CODE_SESSION_ID")
    if not session or not re.fullmatch(r"[A-Za-z0-9-]+", session):
        return None
    return Path(tempfile.gettempdir()) / "orchestrator-runs" / session


def lead_temp_root(workspace):
    """The lead's temp root, which must sit outside the workspace and every git repo; each run gets a TMPDIR under it.

    Workers read file-ownership rules as a fence on all writes and moved TMPDIR into their worktree, which broke
    tests that need temp paths outside the repo (2026-11-06). A named private directory removes the reason to.
    Containment is compared by inode: on a case-insensitive volume a differently-cased spelling of the workspace
    is the same directory and a string comparison misses it.
    """
    base = Path(tempfile.gettempdir()).resolve()
    if any(os.path.samefile(p, workspace) for p in (base, *base.parents)):
        raise ValueError(f"temp root is inside the workspace: {base}")
    repo = next((p for p in (base, *base.parents) if (p / ".git").exists()), None)
    if repo is not None:
        raise ValueError(f"temp root is inside the git repository {repo}: {base}")
    return base


def worktree_git_roots(workspace):
    """Git metadata a commit writes when the workspace is a linked worktree: its gitdir and the shared objects/refs/logs.

    Under workspace-write they sit outside every writable root, so `git commit` fails on index.lock. Granting the
    repo's `.git` whole is no fix: the worktree's gitdir stays denied while config and hooks become writable (probed
    on 0.166.0 and 0.167.0), so the subdirectories are granted instead and config and hooks stay read-only. Read
    from the on-disk layout (gitrepository-layout(5)) without spawning git.
    """
    top = next((p for p in (workspace, *workspace.parents) if (p / ".git").exists()), None)
    if top is None or not (top / ".git").is_file():
        # Not a repo, or an ordinary checkout. At the checkout root Codex keeps the workspace's own .git read-only;
        # in a subdirectory the .git is outside every writable root. Either way no grant: a committing leg needs
        # a linked worktree.
        return []
    pointer = (top / ".git").read_text(encoding="utf-8").strip()
    if not pointer.startswith("gitdir:"):
        return []
    gitdir = (top / pointer[len("gitdir:"):].strip()).resolve()
    commondir = gitdir / "commondir"
    if not commondir.is_file():
        return []  # --separate-git-dir: no shared repo to reach
    common = (gitdir / commondir.read_text(encoding="utf-8").strip()).resolve()
    return [gitdir, *(common / name for name in ("objects", "refs", "logs") if (common / name).is_dir())]


def check_worktree(top):
    """Reasons not to run git in a linked worktree after a workspace-write worker used it; empty when none is found.

    The commit grant above makes the worktree's gitdir writable, and with it the `commondir` and `gitdir` files
    git follows to find the repository. A worker that rewrites `commondir` points the lead's next unsandboxed git
    command at a config of the worker's choosing (core.fsmonitor, hooks: code execution). A repository planted in
    a subdirectory does the same for git run inside it, and for `git status` at the root once it is staged. The
    worktree's own `.git` pointer and the repo's config stay read-only to the worker (probed on 0.166.0 and 0.167.0), so the
    check takes the worktree root as given, starts from that pointer, and holds the rest to the exact bytes `git
    worktree add` writes: git and Python trim paths differently, so nothing is compared after trimming. Nothing is
    compared against a value stored at dispatch either, because the run's artifacts are worker-writable too.
    `tampered:` reasons are layouts git never writes; `inspect:` reasons can come from the repo's own setup.
    An empty result covers git run at the worktree root: a symlinked directory is not followed, so git run from
    inside one is not covered.
    """
    pointer_file = top / ".git"
    if not os.path.lexists(pointer_file):
        raise ValueError(f"no .git in {top}: pass the worktree root, not a path inside it")
    problems = []

    def unlisted(error):
        problems.append(f"inspect: cannot list {error.filename}: nothing inside it was checked")

    for folder, folders, _ in os.walk(top, onerror=unlisted):
        descend = []
        for name in folders:
            path = os.path.join(folder, name)
            if Path(folder) == top and os.path.samefile(path, pointer_file):
                continue  # an ordinary checkout's own .git
            # Ask the filesystem for ".git" as git does: a name comparison misses ".GIT" on a case-insensitive
            # volume, and a directory that cannot be listed can still hold one.
            if os.path.lexists(os.path.join(path, ".git")):
                problems.append(f"inspect: repository inside the worktree at {path}: git run there, or at the "
                                "root once it is staged, loads a config the worker could write")
            else:
                descend.append(name)
        folders[:] = descend
    if len(problems) > 10:
        problems[10:] = [f"inspect: {len(problems) - 10} more repositories inside the worktree"]
    outer = next((p for p in top.parents if os.path.lexists(p / ".git")), None)
    if outer is not None and (pointer_file.is_dir() or (outer / ".git").is_file()):
        # a repository in a subdirectory of a worker's tree is one the worker could have planted
        problems.append(f"inspect: {top} sits inside the tree at {outer}: if that is the worker's worktree, check "
                        "that root, and run no git here")
    if pointer_file.is_dir():
        if not problems:
            print(f"note: {top} is not a linked worktree; only repositories inside it were looked for")
        return problems
    pointer = pointer_file.read_text(encoding="utf-8").strip()
    if pointer_file.is_symlink() or not pointer.startswith("gitdir:"):
        return [f"tampered: {pointer_file} is not a gitdir pointer", *problems]
    gitdir = (top / pointer[len("gitdir:"):].strip()).resolve()
    commondir = gitdir / "commondir"
    if gitdir.parent.name != "worktrees":
        # --separate-git-dir gets no grant; a commondir there is a layout this check does not know
        return [*([f"inspect: {commondir} exists outside a worktrees/ directory"] if commondir.exists() else []), *problems]
    common = gitdir.parent.parent
    if common.parent.name == "worktrees" or os.path.lexists(common / "commondir"):
        problems.append(f"tampered: {gitdir} sits inside another worktree's gitdir, which a worker can write")
    if commondir.is_symlink() or not commondir.is_file():
        problems.append(f"tampered: {commondir} is missing or not a regular file: git would read its config from {gitdir}")
    elif commondir.read_bytes() not in (b"../..\n", b"../.."):
        problems.append(f"tampered: {commondir} holds {commondir.read_bytes()[:200]!r}, not the '../..' that git "
                        f"writes: git would read its config from somewhere other than {common}")
    if os.path.lexists(gitdir / "config"):
        problems.append(f"tampered: {gitdir / 'config'} exists; git never writes a config in a worktree's gitdir")
    back = gitdir / "gitdir"
    target = gitdir / back.read_text(encoding="utf-8", errors="replace").rstrip("\r\n") if back.is_file() else None
    if target is None or not target.exists() or not os.path.samefile(target, pointer_file):
        problems.append(f"tampered: {back} does not point back at {pointer_file}")
    config = common / "config"
    if os.path.lexists(gitdir / "config.worktree") and config.is_file() \
            and "worktreeconfig" in config.read_text(encoding="utf-8", errors="replace").lower():
        problems.append(f"inspect: {gitdir / 'config.worktree'} is loaded by git (extensions.worktreeConfig) and the "
                        "worker could write it: read it before running git here")
    return sorted(problems, key=lambda reason: not reason.startswith("tampered:"))


def absolute_path(value, name):
    if not isinstance(value, str) or not Path(value).is_absolute():
        raise ValueError(f"{name} must be an absolute path")
    return Path(value).resolve()


def prepare(record, environ=os.environ):
    if not isinstance(record, dict):
        raise ValueError("run record must be a JSON object")
    if REQUIRED - record.keys():
        raise ValueError(f"missing fields: {', '.join(sorted(REQUIRED - record.keys()))}")
    if record.keys() - REQUIRED - OPTIONAL:
        raise ValueError(f"unknown fields: {', '.join(sorted(record.keys() - REQUIRED - OPTIONAL))}")
    for name in ("task", "model"):
        if not isinstance(record[name], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]*", record[name]):
            raise ValueError(f"{name} must be a non-empty identifier")
    if "/" in record["task"]:
        raise ValueError("task cannot contain a path separator")
    for name in ("run", "brief_revision"):
        if type(record[name]) is not int or record[name] < 1:
            raise ValueError(f"{name} must be a positive integer")
    if record["action"] not in ("start", "resume", "fork"):
        raise ValueError("action must be start, resume, or fork")
    if record["effort"] not in EFFORTS:
        raise ValueError("effort must be one of none, low, medium, high, xhigh, max, ultra (minimal and persistent are refused)")
    if "user_gated" in record and record["user_gated"] is not True:
        raise ValueError("user_gated, when present, must be true")
    if record["effort"] == "ultra" and record.get("user_gated") is not True:
        raise ValueError("effort ultra needs explicit user permission for this dispatch: set user_gated to true")
    if record["permission_mode"] not in ("read-only", "workspace-write", "bypass"):
        raise ValueError("permission_mode must be read-only, workspace-write, or bypass")
    thread = record.get("thread_id")
    if record["action"] == "start":
        if thread is not None:
            raise ValueError("start cannot have a thread_id")
    elif not isinstance(thread, str) or not re.fullmatch(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}", thread):
        raise ValueError("resume/fork requires an exact thread UUID")

    workspace = absolute_path(record["workspace"], "workspace")
    brief = absolute_path(record["brief"], "brief")
    artifacts = absolute_path(record["artifact_dir"], "artifact_dir")
    if not workspace.is_dir():
        raise ValueError(f"workspace is missing: {workspace}")
    if not brief.is_file() or not brief.read_text(encoding="utf-8").strip():
        raise ValueError(f"brief is missing or empty: {brief}")
    paths = {name: str(artifacts / f'{record["task"]}.r{record["run"]}.{suffix}') for name, suffix in (
        ("dispatch", "dispatch.json"), ("report", "report.md"),
        ("last_message", "last.md"), ("events", "events.jsonl"), ("stderr", "stderr"), ("steer_log", "steer.log"),
        ("ask_log", "ask.log"),
    )}
    for path in paths.values():
        if os.path.lexists(path):
            raise ValueError(f"artifact already exists; advance run: {path}")
    # Pending-steer file for codex_steer.py; the hooks act only on runs that carry these variables.
    paths["steer"] = str(artifacts / f'{record["task"]}.r{record["run"]}.steer.md')
    hook_env = {"ORCH_STEER_FILE": paths["steer"], "ORCH_STATUS_LINE": "0" if "output_schema" in record else "1",
                # What a relayed ask tells the lead to reply to: the short run name when the registry can resolve it.
                "ORCH_REPLY_TARGET": f'{record["task"]}.r{record["run"]}' if run_registry(environ) else paths["dispatch"]}
    if "lead_inbox" in record and type(record["lead_inbox"]) is not bool:
        raise ValueError("lead_inbox must be a boolean")
    if record.get("lead_inbox", True):  # false for untrusted-input legs: the run then cannot post to the lead
        hook_env.update({ours: environ[theirs] for theirs, ours in LEAD_INBOX.items() if environ.get(theirs)})

    argv = ["codex", "exec"]
    if record["action"] != "start":
        argv.append(record["action"])
    argv += ["-m", record["model"], "-c", f'model_reasoning_effort="{record["effort"]}"', "-c", WORKER_ENV_EXCLUDE]
    if record["permission_mode"] == "bypass":
        argv.append("--dangerously-bypass-approvals-and-sandbox")
    else:
        # An execpolicy `allow` rule runs a matching simple command outside the sandbox, and the user's
        # ~/.codex/rules allow bare rm, git, cp, python3, npm, curl and more (probed 2026-11-10 on 0.166.0 and
        # 0.167.0: a bare `touch ~/x` wrote under read-only). Without this flag neither mode is a boundary.
        argv += ["--ignore-rules", "-c", f'sandbox_mode="{record["permission_mode"]}"']
    if "network" in record and (type(record["network"]) is not bool or record["permission_mode"] != "workspace-write"):
        raise ValueError("network is a boolean and applies only to workspace-write")
    worker_env = {}
    if record["permission_mode"] == "workspace-write":
        # Network defaults on (user decision 2026-11-06: installs and uv must work); false for untrusted-input legs.
        argv += ["-c", f'sandbox_workspace_write.network_access={str(record.get("network", True)).lower()}']
        # The sandbox's temp root follows the per-run TMPDIR, but macOS mktemp(1) and other tools that read
        # DARWIN_USER_TEMP_DIR still write to the lead's temp root, so it stays writable too. The artifact dir
        # takes reports and check logs wherever the lead's scratchpad lives. Roots go through -c, not --add-dir:
        # `exec resume` and `exec fork` reject --add-dir (codex-cli 0.167.0), and the config key works on all three.
        temp_root = Path(tempfile.gettempdir()).resolve()
        roots = [str(root) for root in (temp_root, artifacts, *worktree_git_roots(workspace))]
        argv += ["-c", f"sandbox_workspace_write.writable_roots={json.dumps(roots)}"]
        worker_env = {name: str(temp_root / "orchestrator-cache" / sub) for name, sub in WORKER_CACHES.items()}
    if "skip_git_repo_check" in record and type(record["skip_git_repo_check"]) is not bool:
        raise ValueError("skip_git_repo_check must be a boolean")
    if record.get("skip_git_repo_check", False):
        argv.append("--skip-git-repo-check")  # opt-in; the default keeps Codex's outside-a-repo guard
    argv += ["--json", "--output-last-message", paths["last_message"]]
    if "web_search" in record:
        if record["web_search"] not in ("disabled", "cached", "live"):
            raise ValueError("web_search must be disabled, cached, or live")
        argv += ["-c", f'web_search="{record["web_search"]}"']
    if "output_schema" in record:
        schema = absolute_path(record["output_schema"], "output_schema")
        if not schema.is_file():
            raise ValueError(f"output_schema is missing: {schema}")
        argv += ["--output-schema", str(schema)]
    if record["action"] != "start":
        argv.append(thread)
    argv.append("-")
    return workspace, brief, artifacts, paths, argv, hook_env, worker_env


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path, nargs="?", help="JSON run record; see references/runtime.md")
    parser.add_argument("--check-worktree", metavar="WORKTREE", help="check a worker's linked worktree (its root) "
                        "before running git in it: exit 0 when nothing was found, 1 with the reasons otherwise")
    args = parser.parse_args()
    if args.check_worktree is not None:
        top = absolute_path(args.check_worktree, "workspace")
        if not top.is_dir():
            raise ValueError(f"workspace is missing: {top}")
        problems = check_worktree(top)
        for problem in problems:
            print(f"check-worktree: {problem}")
        sys.exit(1 if problems else 0)
    if args.record is None:
        parser.error("a run record is required")
    record = json.loads(args.record.read_text(encoding="utf-8"))
    workspace, brief, artifacts, paths, argv, hook_env, worker_env = prepare(record)
    executable = shutil.which("codex")
    if executable is None:
        raise ValueError("codex is not on PATH")
    artifacts.mkdir(parents=True, exist_ok=True)
    temp_root = lead_temp_root(workspace)
    registry = run_registry()
    if registry:
        # A name already held by another live record keeps it; this run is then answered by its record path.
        try:
            registry.mkdir(parents=True, exist_ok=True)
            link = registry / Path(paths["dispatch"]).name
            if link.exists() and link.resolve() != Path(paths["dispatch"]).resolve():
                hook_env["ORCH_REPLY_TARGET"] = paths["dispatch"]
            else:
                link.unlink(missing_ok=True)
                link.symlink_to(paths["dispatch"])
        except OSError:
            hook_env["ORCH_REPLY_TARGET"] = paths["dispatch"]
    # Exclusive marker reserves this run even if two callers race. Never overwrite evidence.
    with open(paths["dispatch"], "x", encoding="utf-8") as output:
        # Made only once the run is reserved, so a caller that loses the race leaves no directory behind.
        try:
            tmpdir = tempfile.mkdtemp(prefix=f'orch-{record["task"]}.r{record["run"]}.', dir=temp_root)
        except OSError:
            os.unlink(paths["dispatch"])  # nothing launched: do not spend the run number on an empty record
            raise
        json.dump({
            "prepared_at": datetime.now(timezone.utc).isoformat(),
            "record": str(args.record.resolve()), "requested": record,
            "workspace": str(workspace), "brief_sha256": hashlib.sha256(brief.read_bytes()).hexdigest(),
            "argv": argv, "executable": executable, "pid": os.getpid(), "artifacts": paths, "tmpdir": tmpdir, "worker_env": worker_env,
            "hook_env": {name: "<redacted>" if name == "ORCH_LEAD_TOKEN" else value for name, value in hook_env.items()},
            "runtime_model": None, "runtime_effort": None,
            "note": "Prepared dispatch only; not completion or acceptance evidence. Runtime settings unknown until observed.",
        }, output, indent=2)
        output.write("\n")
    print(json.dumps({"dispatch": paths["dispatch"], "pid": os.getpid(), "events": paths["events"]}), flush=True)
    # No shell and no detached child: the harness keeps this PID and the worker's real exit code.
    # The finite brief supplies stdin EOF even when the invoking harness leaves stdin open.
    with brief.open("rb") as prompt, open(paths["events"], "xb") as events, open(paths["stderr"], "xb") as errors:
        os.dup2(prompt.fileno(), 0)
        os.dup2(events.fileno(), 1)
        os.dup2(errors.fileno(), 2)
    os.chdir(workspace)
    for name in LEAD_INBOX:
        os.environ.pop(name, None)
    os.environ.update(hook_env)
    os.environ.update(worker_env)
    os.environ["TMPDIR"] = tmpdir  # inherited by worker shells; workspace-write adds $TMPDIR to its writable roots
    os.execv(executable, argv)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        print(f"dispatch: {error}", file=sys.stderr)
        sys.exit(2)
