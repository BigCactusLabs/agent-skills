#!/usr/bin/env python3
"""Read-only roles' `PreToolUse(SendMessage)` hook: the lead (`main`) is the only recipient.

Without it, a read-only subagent holding SendMessage could resume a completed write-capable
sibling under its own direction, or message another local session. Wired without `|| true`:
a missing or broken script exits non-zero and the send is blocked, not allowed.
"""

import json
import sys


def denial(event):
    tool_input = event.get("tool_input") if isinstance(event, dict) else None
    if not isinstance(tool_input, dict):
        return "SendMessage input was unreadable; message not sent."
    message = tool_input.get("message")
    if isinstance(message, dict) and message.get("type") == "shutdown_response":
        return None
    if tool_input.get("notify_when_idle"):
        return "notify_when_idle is reserved for the lead."
    to = tool_input.get("to")
    if isinstance(to, str) and to.strip() == "main":
        return None
    return (f"Read-only roles may message only `main` (the lead), not {to!r}. A finding that affects "
            "another agent goes to the lead, who decides; anything else belongs in your final report.")


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        event = None
    reason = denial(event)
    if reason:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
