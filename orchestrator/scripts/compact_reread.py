#!/usr/bin/env python3
"""SessionStart(compact) hook: after a compaction, tell an orchestrating lead to re-read what the summary dropped.

Registered in user settings (REFERENCE.md, standing roles), because a SessionStart hook declared in SKILL.md
frontmatter does not fire (probed on claude-code 2.1.326). It prints nothing unless the session's own transcript
shows the orchestrator or cm-orchestrator skill was invoked, and it exits 0 on any error. It also prints nothing
when a subagent compacts (the input then carries agent_id): the instruction is the lead's.
"""

import json
import re
import sys

EDITIONS = ("cm-orchestrator", "orchestrator")
COMMAND = re.compile(r"<command-name>/((?:cm-)?orchestrator)</command-name>")


def skills_in(record):
    """Names of the editions this transcript record shows being invoked."""
    if record.get("isSidechain"):
        return set()
    found = set()
    attachment = record.get("attachment")
    if isinstance(attachment, dict) and attachment.get("type") == "invoked_skills":
        found.update(s.get("name") for s in attachment.get("skills") or [] if isinstance(s, dict))
    message = record.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    blocks: list = [{"type": "text", "text": content}] if isinstance(content, str) else content or []
    for block in blocks:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "tool_use" and block.get("name") == "Skill":
            tool_input = block.get("input")
            found.add(tool_input.get("skill") if isinstance(tool_input, dict) else None)
        elif block.get("type") == "text" and record.get("type") == "user":
            text = block.get("text") or ""
            if text.lstrip().startswith("<command-"):
                found.update(COMMAND.findall(text))
    return found & set(EDITIONS)


def invoked(transcript_path):
    found = set()
    with open(transcript_path, errors="replace") as handle:
        for line in handle:
            if "orchestrator" not in line:
                continue
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if isinstance(record, dict):
                found |= skills_in(record)
    return found


def message(found):
    names = " and ".join(name for name in EDITIONS if name in found)
    first = ("~/.claude/skills/cm-orchestrator/references/code-mode.md, then the reference for the next step"
             if "cm-orchestrator" in found else "the reference for the next step")
    return (
        f"Context was just compacted, and this session invoked the {names} skill. If workers are running or "
        "more will be dispatched, the next thing you do is a re-read, before any dispatch, steer, stop, wait, or "
        f"ruling: the run manifest, the current brief, and {first} in the skill's \"Read at the step\" table. "
        "Read each whole, not a preview or a slice. The summary above is not those files, and the manifest "
        "outranks it. If the orchestration has finished, ignore this."
    )


def main():
    try:
        payload = json.load(sys.stdin)
        if payload.get("source", "compact") != "compact" or payload.get("agent_id"):
            return
        found = invoked(payload["transcript_path"])
    except Exception:
        return
    if found:
        print(message(found))


if __name__ == "__main__":
    main()
