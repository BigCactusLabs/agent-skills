#!/usr/bin/env python3
"""Stop one dispatched Codex run: SIGINT (exec turns it into turn/interrupt), wait, then SIGTERM.

Reads the run's `.dispatch.json`, signals only a live process whose command line still carries
that run's unique `--output-last-message` path, and never sends SIGKILL: a run still alive after
SIGTERM is left for `TaskStop` on the harness handle. Descendants listed before signalling that
outlive the stop are reported, because they may still write to the worktree.
"""

import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


def ps(pid, field):
    result = subprocess.run(["ps", "-ww", "-o", f"{field}=", "-p", str(pid)], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ""


def alive(pid):
    state = ps(pid, "stat")
    return bool(state) and not state.startswith("Z")  # a zombie has exited; its parent just hasn't reaped it


def descendants(pid):
    found, queue = [], [pid]
    while queue:
        result = subprocess.run(["pgrep", "-P", str(queue.pop())], capture_output=True, text=True)
        for child in map(int, result.stdout.split()):
            found.append({"pid": child, "command": ps(child, "command")})
            queue.append(child)
    return found


def wait_exit(pid, seconds):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if not alive(pid):
            return True
        time.sleep(0.1)
    return not alive(pid)


def last_event(path):
    try:
        lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict) and "type" in event:
            return event
    return None


def stop(dispatch, grace, term_grace):
    record = json.loads(Path(dispatch).read_text(encoding="utf-8"))
    pid, artifacts = record["pid"], record["artifacts"]
    report = {"dispatch": str(dispatch), "pid": pid, "signals": []}
    if not alive(pid):
        report["outcome"] = "not_running"
    else:
        command = ps(pid, "command")
        if "exec" not in command.split() or artifacts["last_message"] not in command:
            report.update(outcome="identity_mismatch", command=command)
            return report, 2
        children = descendants(pid)
        for sig, seconds in ((signal.SIGINT, grace), (signal.SIGTERM, term_grace)):
            try:
                os.kill(pid, sig)
            except ProcessLookupError:
                break  # exited between checks
            report["signals"].append(sig.name)
            if wait_exit(pid, seconds):
                break
        if alive(pid):
            report["outcome"] = "still_running"
        else:
            report["outcome"] = f"stopped_by_{report['signals'][-1].lower()}" if report["signals"] else "not_running"
        report["surviving_descendants"] = [
            child for child in children if alive(child["pid"]) and ps(child["pid"], "command") == child["command"]]
    report["last_event"] = last_event(artifacts["events"])
    return report, 0 if report["outcome"] != "still_running" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("dispatch", type=Path, help="the run's <task>.r<run>.dispatch.json")
    parser.add_argument("--grace", type=float, default=30, help="seconds to wait after SIGINT (default 30)")
    parser.add_argument("--term-grace", type=float, default=10, help="seconds to wait after SIGTERM (default 10)")
    args = parser.parse_args()
    report, code = stop(args.dispatch, args.grace, args.term_grace)
    print(json.dumps(report, indent=2))
    return code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError) as error:
        print(f"stop_worker: {error!r}", file=sys.stderr)
        sys.exit(2)
