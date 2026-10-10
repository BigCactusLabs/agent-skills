#!/usr/bin/env python3
"""Follow one Codex run's events for the Monitor tool: print a line only when the lead should look.

Alerts: an edit outside the owned paths, the same command failing --repeat times, no new event for
--stall-seconds, and the turn ending (or the process exiting without a turn end), after which the
watch exits. Events before --from-offset (default: the file's size at start) are counted, not
alerted, so a re-armed watch stays quiet about them. An alert is a cue to read the events file; completion evidence is still the current
run's `turn.completed` plus a non-empty `.last.md`.
"""

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import sys
import time


def running(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        pass
    return True


class Watch:
    def __init__(self, owned, repeat):
        self.owned = [str(Path(path).resolve()) for path in owned]
        self.repeat = repeat
        self.failures = Counter()
        self.flagged = set()

    def outside(self, path):
        path = str(Path(path).resolve())
        return not any(path == root or path.startswith(root.rstrip("/") + "/") for root in self.owned)

    def alerts(self, event):
        kind, item = event.get("type"), event.get("item") or {}
        if kind in ("turn.completed", "turn.failed"):
            detail = (event.get("error") or {}).get("message") or ""
            return [f"turn ended: {kind} {detail}".rstrip()], True
        if kind == "error":  # may be a retry notice rather than the end of the turn
            return [f"error event: {str(event.get('message', ''))[:160]}"], False
        if kind != "item.completed":
            return [], False
        found = []
        if item.get("type") == "file_change":
            for change in item.get("changes") or []:
                path = change.get("path", "")
                if path and path not in self.flagged and self.owned and self.outside(path):
                    self.flagged.add(path)
                    found.append(f"edit outside owned paths: {change.get('kind', 'change')} {path}")
        if item.get("type") == "command_execution" and item.get("status") == "failed":
            command = item.get("command", "")
            self.failures[command] += 1
            if self.failures[command] == self.repeat:
                found.append(f"same command failed {self.repeat} times: {command[:160]}")
        return found, False


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("dispatch", type=Path, help="the run's <task>.r<run>.dispatch.json")
    parser.add_argument("--own", action="append", default=[], help="an owned path (repeatable); omit to skip the scope check")
    parser.add_argument("--repeat", type=int, default=3, help="identical failed commands before an alert (default 3)")
    parser.add_argument("--stall-seconds", type=float, default=600, help="quiet time before a stall alert (default 600)")
    parser.add_argument("--from-offset", type=int, help="alert on events from this byte offset; 0 on the first arm "
                        "(default: the file's size at start, so a re-armed watch stays quiet about old events)")
    parser.add_argument("--poll", type=float, default=1.0, help=argparse.SUPPRESS)
    args = parser.parse_args()
    record = json.loads(args.dispatch.read_text(encoding="utf-8"))
    label, events, pid = args.dispatch.name.removesuffix(".dispatch.json"), Path(record["artifacts"]["events"]), record["pid"]
    start = args.from_offset if args.from_offset is not None else (events.stat().st_size if events.exists() else 0)
    watch, buffer, offset, position = Watch(args.own, args.repeat), b"", 0, 0
    last_event, stalled = time.monotonic(), False
    while True:
        try:
            with events.open("rb") as stream:
                stream.seek(offset)
                chunk = stream.read()
                offset = stream.tell()
        except FileNotFoundError:
            chunk = b""
        *lines, buffer = (buffer + chunk).split(b"\n")
        for line in lines:
            position += len(line) + 1
            old = position <= start
            try:
                event = json.loads(line.decode("utf-8", "replace"))
            except ValueError:
                continue
            if not isinstance(event, dict):
                continue
            last_event, stalled = time.monotonic(), False
            found, ended = watch.alerts(event)
            if not old:
                for alert in found:
                    print(f"{label}: {alert}", flush=True)
            if ended:
                if old:
                    print(f"{label}: turn already ended before the watch started", flush=True)
                return 0
        if not running(pid):
            print(f"{label}: worker process {pid} exited without a turn end", flush=True)
            return 0
        if not stalled and time.monotonic() - last_event >= args.stall_seconds:
            stalled = True
            print(f"{label}: no new event for {args.stall_seconds:g}s", flush=True)
        time.sleep(args.poll)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError) as error:
        print(f"watch_events: {error!r}", flush=True)
        sys.exit(2)
