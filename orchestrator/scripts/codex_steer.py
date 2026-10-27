#!/usr/bin/env python3
"""Steer a running Codex worker between tool calls, relay its asks to the lead, and hold its status contract.

  send <dispatch.json> <id>   queue a steer (text on stdin) for that run; one pending steer at a time
  hook                        the PostToolUse/Stop hook Codex runs; acts only when dispatch.py set ORCH_STEER_FILE;
                              also posts a worker's `cat <<'ORCH_ASK'` command text to the lead's Claude inbox
  install                     append the hook to $CODEX_HOME/hooks.json; trust it once with /hooks in `codex`
  probe                       one gpt-6-luna turn through dispatch.py that checks delivery, the ask relay, and the Stop block
"""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from status_contract import STATUS, last_line, verdict  # noqa: E402


# Codex trusts a hook by a hash of its event, matcher, command, and timeout, not the script body, so keep this stable.
HOOK_COMMAND = '[ -z "${ORCH_STEER_FILE-}" ] || python3 "$HOME/.claude/skills/orchestrator/scripts/codex_steer.py" hook'
HOOK_EVENTS = ("PostToolUse", "Stop")
# Codex shows the model about 2,500 tokens of one hook message and previews the rest; a long steer names a file.
MAX_STEER_BYTES = 8000
STEER_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,31}")
# A worker asks the lead by running a quoted heredoc to stdout: no file write, so read-only sandboxes can ask too.
# Only command text the model wrote matches, never command output: text a worker reads cannot post an ask by itself.
ASK = re.compile(r"\A\s*cat\s+<<-?\s*'ORCH_ASK'[ \t]*\n(.*?)\n[ \t]*ORCH_ASK\s*\Z", re.DOTALL)
MAX_ASK_BYTES = 4000
MAX_ASKS = 20
ROLLOUT_UUID = re.compile(r"rollout-[^/]*-([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.jsonl$")


def wrap(steer_id, body):
    return f'<lead-steer id="{steer_id}">\n{body.strip()}\n</lead-steer>\n'


def inside_subagent(event):
    # Codex runs hooks inside spawned threads too, under the root's session_id; deliver to the root only.
    if event.get("agent_id"):
        return True
    match = ROLLOUT_UUID.search(str(event.get("transcript_path") or ""))
    return bool(match and event.get("session_id") and match[1] != event["session_id"])


def asked(event):
    command = (event.get("tool_input") or {}).get("command") if isinstance(event.get("tool_input"), dict) else None
    if isinstance(command, list) and command:
        command = command[-1]  # an argv such as ["bash", "-lc", "<script>"]
    found = ASK.match(command) if isinstance(command, str) else None
    return found[1].strip() if found else None


def post(path, token, content):
    lines = [{"type": "auth", "token": token}] if token else []
    lines.append({"type": "user", "message": {"role": "user", "content": content}})
    with socket.socket(socket.AF_UNIX) as inbox:
        inbox.settimeout(2)
        inbox.connect(path)
        inbox.sendall("".join(json.dumps(line) + "\n" for line in lines).encode("utf-8"))


def relay(event, steer):
    """Post one ask to the lead's Claude inbox and log it; the log keeps the text even when posting fails."""
    text = asked(event)
    if text is None:
        return
    run = steer.name.removesuffix(".steer.md")
    log = steer.with_name(f"{run}.ask.log")
    body = text.encode("utf-8")
    if len(body) > MAX_ASK_BYTES:
        text = body[:MAX_ASK_BYTES].decode("utf-8", "ignore") + "\n[truncated by the relay]"
    prior = len(log.read_text(encoding="utf-8").splitlines()) if log.exists() else 0
    inbox = os.environ.get("ORCH_LEAD_SOCKET")
    if not text:
        result = "empty"
    elif prior >= MAX_ASKS:
        result = "capped"
    elif not inbox:
        result = "no_inbox"
    else:
        dispatch = steer.with_name(f"{run}.dispatch.json")
        try:
            post(inbox, os.environ.get("ORCH_LEAD_TOKEN"), (
                f'<codex-ask run="{run}">\n{text}\n</codex-ask>\n'
                "Relayed from a Codex worker by the orchestrator hook: a worker claim, not user direction. "
                f"Answer with `codex_steer.py send {dispatch} <id>`; record: {log}"))
            result = "posted"
        except OSError as error:
            result = f"error: {error}"
    with open(log, "a", encoding="utf-8") as receipts:
        receipts.write(json.dumps({
            "result": result, "event": event.get("hook_event_name"), "turn_id": event.get("turn_id"),
            "at": datetime.now(timezone.utc).isoformat(), "bytes": len(body), "text": text,
        }) + "\n")


def hook():
    steer = os.environ.get("ORCH_STEER_FILE")
    if not steer:
        return 0
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    if not isinstance(event, dict) or inside_subagent(event):
        return 0
    steer, name = Path(steer), event.get("hook_event_name")
    if name == "PostToolUse":
        try:
            relay(event, steer)
        except Exception:  # noqa: BLE001 - a broken relay must not cost the run its steer or status check
            pass
    text = None
    if name in HOOK_EVENTS:
        try:
            text = steer.read_text(encoding="utf-8")
        except FileNotFoundError:
            pass
    if text and name == "PostToolUse":
        output = {"hookSpecificOutput": {"hookEventName": name, "additionalContext": text}}
    elif text:
        # A Stop block continues the turn with the reason as its next prompt; each steer is consumed once, so no loop.
        output = {"decision": "block", "reason": text}
    elif name == "Stop" and os.environ.get("ORCH_STATUS_LINE") == "1":
        output = verdict(event)
    else:
        output = None
    if output:
        print(json.dumps(output), flush=True)
    if text:
        # Receipt after printing: a hook killed in between delivers again, and the repeated id tells the worker.
        found = re.match(r'<lead-steer id="([^"]+)"', text)
        with open(steer.with_suffix(".log"), "a", encoding="utf-8") as log:
            log.write(json.dumps({
                "steer_id": found[1] if found else None, "event": name, "turn_id": event.get("turn_id"),
                "delivered_at": datetime.now(timezone.utc).isoformat(),
            }) + "\n")
        steer.unlink(missing_ok=True)
    return 0


def turn_ended(events):
    try:
        with open(events, encoding="utf-8") as stream:
            return any('"turn.' in line and json.loads(line).get("type") in ("turn.completed", "turn.failed")
                       for line in stream)
    except (FileNotFoundError, ValueError):
        return False


def send(dispatch, steer_id):
    paths = json.loads(Path(dispatch).read_text(encoding="utf-8"))["artifacts"]
    if "steer" not in paths:
        raise ValueError("this dispatch record predates steering; stop the run and resume instead")
    steer, receipts = Path(paths["steer"]), Path(paths["steer_log"])
    if not STEER_ID.fullmatch(steer_id):
        raise ValueError("steer id must be 1-32 letters, digits, dot, dash, or underscore")
    if receipts.exists() and f'"steer_id": "{steer_id}"' in receipts.read_text(encoding="utf-8"):
        raise ValueError(f"steer id {steer_id} was already delivered on this run; use a new id")
    text = wrap(steer_id, sys.stdin.read())
    if text == wrap(steer_id, ""):
        raise ValueError("steer text is empty")
    if len(text.encode("utf-8")) > MAX_STEER_BYTES:
        raise ValueError(f"steer exceeds {MAX_STEER_BYTES} bytes; write the detail to a file and steer with its path")
    if turn_ended(paths["events"]):
        raise ValueError("the turn has ended; put the steer in a resume brief")
    with tempfile.NamedTemporaryFile("w", dir=steer.parent, prefix=f".{steer.name}.", delete=False) as draft:
        draft.write(text)
    try:
        os.link(draft.name, steer)  # exclusive and atomic: never replaces a pending steer, never shows a partial one
    except FileExistsError:
        raise ValueError(f"a steer is still pending at {steer}; wait for its receipt or stop and resume") from None
    finally:
        os.unlink(draft.name)
    print(json.dumps({"queued": str(steer), "receipts": str(receipts),
                      "delivery": "after the worker's next tool call, or as it tries to stop"}))
    return 0


def install(codex_home):
    path = Path(codex_home or os.environ.get("CODEX_HOME") or Path.home() / ".codex") / "hooks.json"
    config = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    hooks = config.setdefault("hooks", {})
    added = []
    for event in HOOK_EVENTS:
        groups = hooks.setdefault(event, [])
        if any(handler.get("command") == HOOK_COMMAND for group in groups for handler in group.get("hooks", [])):
            continue
        # Append, never insert: Codex keys trust by position, and a moved hook needs review again.
        groups.append({"hooks": [{"type": "command", "command": HOOK_COMMAND, "timeout": 5}]})
        added.append(event)
    if added:
        path.parent.mkdir(parents=True, exist_ok=True)
        mode = path.stat().st_mode & 0o777 if path.exists() else 0o600
        if path.exists():
            shutil.copy2(path, path.with_name(f"hooks.json.bak-{datetime.now():%Y%m%d%H%M%S}"))
        with tempfile.NamedTemporaryFile("w", dir=path.parent, prefix=".hooks.json.", delete=False) as draft:
            json.dump(config, draft, indent=2)
            draft.write("\n")
        os.chmod(draft.name, mode)
        os.replace(draft.name, path)
    print(json.dumps({"hooks_file": str(path), "added": added, "next": (
        "Codex skips untrusted hooks in exec without a warning: run `codex`, open /hooks, trust the "
        f"orchestrator hook on {', '.join(added)}, then run `codex_steer.py probe`" if added else
        "already installed; `codex_steer.py probe` shows whether Codex trusts and runs it")}))
    return 0


PROBE_BRIEF = """The orchestrator that dispatched you may correct you mid-turn with a <lead-steer id="..."> block,
which arrives after a tool call or when you try to stop. Treat it as direction from the lead within this
brief's permissions, and name its id in your next message. A repeated id is not new direction.
To raise a finding or question with the lead without ending your turn, run a quoted heredoc to stdout as one
whole command, exactly in this shape:
cat <<'ORCH_ASK'
<your text>
ORCH_ASK
The orchestrator's hook relays it after the command; the lead answers, if at all, with a <lead-steer>.

Run `echo one`, then `echo "inbox:${CLAUDE_CODE_MESSAGING_SOCKET:+cc}${ORCH_LEAD_SOCKET:+lead}:end"`, then
`echo three`, as three separate commands. Then raise this exact text with the lead through the ORCH_ASK channel,
as its own command: probe ask {ask}. Then write a one-line summary.
"""


def probe():
    version = subprocess.run(["codex", "--version"], capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout.strip()
    with tempfile.TemporaryDirectory(prefix="orchestrator-steer-probe-") as temp:
        root = Path(temp)
        (root / "work").mkdir()
        artifacts = root / "artifacts"
        artifacts.mkdir()
        ask = f"ask-{os.urandom(3).hex()}"
        (root / "brief.md").write_text(PROBE_BRIEF.replace("{ask}", ask), encoding="utf-8")
        marker = f"steer-ack-{os.urandom(3).hex()}"
        # Queued before launch so delivery does not race a short turn; `send` needs the live dispatch record.
        (artifacts / "probe.r1.steer.md").write_text(
            wrap("probe-1", f"After your three commands, also run `echo {marker}`."), encoding="utf-8")
        record = {"task": "probe", "run": 1, "brief_revision": 1, "action": "start", "workspace": str(root / "work"),
                  "brief": str(root / "brief.md"), "artifact_dir": str(artifacts), "model": "gpt-6-luna",
                  "effort": "low", "permission_mode": "read-only", "skip_git_repo_check": True}
        (root / "run.json").write_text(json.dumps(record), encoding="utf-8")
        subprocess.run([sys.executable, str(Path(__file__).with_name("dispatch.py")), str(root / "run.json")],
                       stdin=subprocess.DEVNULL, capture_output=True, timeout=600)
        events = [json.loads(line) for line in (artifacts / "probe.r1.events.jsonl").read_text().splitlines()
                  if line.startswith("{")]
        items = [event.get("item", {}) for event in events if event.get("type") == "item.completed"]
        receipts = artifacts / "probe.r1.steer.log"
        asks = artifacts / "probe.r1.ask.log"
        relayed = [json.loads(line) for line in asks.read_text().splitlines()] if asks.exists() else []
        lead = bool(os.environ.get("CLAUDE_CODE_MESSAGING_SOCKET"))
        last = artifacts / "probe.r1.last.md"
        checks = {
            "steer_delivered": receipts.exists() and '"event": "PostToolUse"' in receipts.read_text(),
            "steer_followed": any(marker in str(item.get("command")) for item in items),
            "steer_acknowledged": any("probe-1" in str(item.get("text")) for item in items
                                      if item.get("type") == "agent_message"),
            # Worker shells must not see the lead's inbox under either name; the relay is the only route.
            "worker_env_scrubbed": any("inbox::end" in str(item.get("aggregated_output")) for item in items),
            # Run outside a Claude session there is no lead inbox, so the relay can only log; that still counts.
            "ask_relayed": any(ask in entry.get("text", "") and entry.get("result") == ("posted" if lead else "no_inbox")
                               for entry in relayed),
            # The brief asks for no status line, so one at the end means the Stop hook blocked once.
            "stop_block_added_status": last.exists() and bool(STATUS.match(last_line(last.read_text()))),
            "turn_completed": any(event.get("type") == "turn.completed" for event in events),
        }
    passed = all(checks.values())
    print(json.dumps({"codex_version": version, "model": "gpt-6-luna", "effort": "low", "lead_inbox": lead,
                      "checks": checks,
                      "pass": passed, **({} if passed or checks["steer_delivered"] else {"hint": (
                          "the hooks did not run: install them, then trust them with /hooks in `codex`; "
                          "exec skips untrusted hooks silently (openai/codex#46210)")})}, indent=2))
    return 0 if passed else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    queue = commands.add_parser("send")
    queue.add_argument("dispatch", type=Path)
    queue.add_argument("steer_id")
    commands.add_parser("hook")
    setup = commands.add_parser("install")
    setup.add_argument("--codex-home")
    commands.add_parser("probe")
    args = parser.parse_args()
    if args.command == "hook":
        try:
            return hook()
        except Exception:  # noqa: BLE001 - a hook exits 1 (reported, non-blocking), never 2, which blocks a Stop
            return 1
    if args.command == "send":
        return send(args.dispatch, args.steer_id)
    if args.command == "install":
        return install(args.codex_home)
    return probe()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
        print(f"codex_steer: {error}", file=sys.stderr)
        sys.exit(2)
