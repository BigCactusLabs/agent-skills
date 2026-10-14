#!/usr/bin/env python3
"""Role `Stop` hook (a `SubagentStop` when spawned): block a stop once when the final message lacks a status line."""

import json
import re
import sys


# An optional "Status:" label is accepted; "**Status:** DONE" reaches here as "Status:** DONE".
STATUS = re.compile(r"([Ss]tatus:[\s*_`]*)?(DONE\b|(BLOCKED|ESCALATE|CHECKPOINT):\s*\S)")
DECORATION = " \t*`_>#-"
REASON = (
    "Your final message must end with exactly one status line: DONE, BLOCKED: <what is missing>, "
    "ESCALATE: <reason>, or CHECKPOINT: <what remains>. If a command, check, or subagent you started is "
    "still running, or work your brief assigns remains and nothing blocks it, continue now: wait for it in "
    "the foreground and finish, because ending the turn sends the lead an early report. Otherwise send "
    "your complete final message again (everything your role and brief say to return), ending with that "
    "line. Do not redo finished work."
)


def last_line(text):
    for line in reversed(text.splitlines()):
        line = line.strip(DECORATION)
        if line:
            return line
    return ""


def verdict(event):
    # Block at most once: a second stop after a block always goes through.
    if not isinstance(event, dict) or event.get("stop_hook_active"):
        return None
    message = event.get("last_assistant_message")
    if not isinstance(message, str) or STATUS.match(last_line(message)):
        return None  # an absent field is not evidence of a missing status line
    return {"decision": "block", "reason": REASON}


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    result = verdict(event)
    if result:
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
