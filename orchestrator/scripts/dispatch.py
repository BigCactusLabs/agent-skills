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
from datetime import datetime, timezone


REQUIRED = {
    "task", "run", "brief_revision", "action", "workspace", "brief",
    "artifact_dir", "model", "effort", "permission_mode",
}
OPTIONAL = {"thread_id", "output_schema", "web_search", "user_gated", "skip_git_repo_check"}
# `ultra` is user-gated per dispatch (SKILL.md); `minimal` is pre-5.6 legacy; `persistent` withholds turn.completed.
EFFORTS = ("none", "low", "medium", "high", "xhigh", "max", "ultra")


def absolute_path(value, name):
    if not isinstance(value, str) or not Path(value).is_absolute():
        raise ValueError(f"{name} must be an absolute path")
    return Path(value).resolve()


def prepare(record):
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
        ("last_message", "last.md"), ("events", "events.jsonl"), ("stderr", "stderr"),
    )}
    for path in paths.values():
        if os.path.lexists(path):
            raise ValueError(f"artifact already exists; advance run: {path}")

    argv = ["codex", "exec"]
    if record["action"] != "start":
        argv.append(record["action"])
    argv += ["-m", record["model"], "-c", f'model_reasoning_effort="{record["effort"]}"']
    if record["permission_mode"] == "bypass":
        argv.append("--dangerously-bypass-approvals-and-sandbox")
    else:
        argv += ["-c", f'sandbox_mode="{record["permission_mode"]}"']
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
    return workspace, brief, artifacts, paths, argv


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path, help="JSON run record; see references/runtime.md")
    args = parser.parse_args()
    record = json.loads(args.record.read_text(encoding="utf-8"))
    workspace, brief, artifacts, paths, argv = prepare(record)
    executable = shutil.which("codex")
    if executable is None:
        raise ValueError("codex is not on PATH")
    artifacts.mkdir(parents=True, exist_ok=True)
    # Exclusive marker reserves this run even if two callers race. Never overwrite evidence.
    with open(paths["dispatch"], "x", encoding="utf-8") as output:
        json.dump({
            "prepared_at": datetime.now(timezone.utc).isoformat(),
            "record": str(args.record.resolve()), "requested": record,
            "workspace": str(workspace), "brief_sha256": hashlib.sha256(brief.read_bytes()).hexdigest(),
            "argv": argv, "executable": executable, "pid": os.getpid(), "artifacts": paths,
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
    os.execv(executable, argv)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        print(f"dispatch: {error}", file=sys.stderr)
        sys.exit(2)
