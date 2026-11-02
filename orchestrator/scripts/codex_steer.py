#!/usr/bin/env python3
"""Steer a running Codex worker between tool calls, relay its asks to the lead, and hold its status contract.

  send <run>... [--id ID] [--re ASK] [--urgent]
                       queue a steer (text on stdin), one pending per run; --re names the ask it answers;
                       --urgent holds the worker's next tool call so it re-plans before acting
  status <run>...      each run's message ledger: asks and their answers, steers, receipts, acknowledgements
  wait [--timeout S]   worker side of a blocking ask (`... wait <<'ORCH_ASK'`): returns once the reply is pending
  hook                 the PreToolUse/PostToolUse/Stop hook Codex runs; acts only when dispatch.py set
                       ORCH_STEER_FILE; relays a worker's `ORCH_ASK` heredoc to the lead's Claude inbox
  install              append the hook to $CODEX_HOME/hooks.json; trust it once with /hooks in `codex`
  probe                one gpt-6-luna turn through dispatch.py that checks steers, both ask kinds, and the Stop block

<run> is `<task>.r<run>` for a run this lead session dispatched, its dispatch record, or any of its artifact paths.
"""

import argparse
import contextlib
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import select
import shlex
import shutil
import socket
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dispatch import run_registry  # noqa: E402
from status_contract import STATUS, last_line, verdict  # noqa: E402


# Codex trusts a hook by a hash of its event, matcher, command, and timeout, not the script body, so keep this stable.
HOOK_COMMAND = '[ -z "${ORCH_STEER_FILE-}" ] || python3 "$HOME/.claude/skills/orchestrator/scripts/codex_steer.py" hook'
HOOK_EVENTS = ("PreToolUse", "PostToolUse", "Stop")
# Codex shows the model about 2,500 tokens of one hook message and previews the rest; a long steer names a file.
MAX_STEER_BYTES = 8000
STEER_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,31}")
HEADER = re.compile(r'<lead-steer id="([^"]+)"(?: re="([^"]+)")?( urgent="true")?>')
HELD = ("\nThe orchestrator hook held the tool call you were about to make so this steer reaches you first; that "
        "call did not run. Re-plan with the steer, and re-issue the call only if it still fits.")
# A worker asks the lead with a quoted heredoc: `cat` to keep working, or the `wait` command to block on the reply.
# Only command text the model wrote matches, never command output: text a worker reads cannot post an ask by itself.
# The pattern follows bash: a `<<` terminator starts its line, `<<-` may tab-indent it, and no body line may end the
# heredoc early (lines after it would run as shell commands).
ASK = re.compile(r"\A\s*(cat|(?:python3?\s+)?\"?(?:\$HOME|\$\{HOME\}|~)?[\w./-]*codex_steer\.py\"?\s+wait"
                 r"(?:\s+--timeout[ =](\d+))?)\s+<<(-?)\s*'ORCH_ASK'[ \t]*\n(.*?)\n(\t*)ORCH_ASK(?:\n\s*)?\Z", re.DOTALL)
EARLY_END = re.compile(r"(?m)^[ \t]*ORCH_ASK[ \t]*$")
MAX_ASK_BYTES = 4000
MAX_ASKS = 20
WAIT_SECONDS = 600
ROLLOUT_UUID = re.compile(r"rollout-[^/]*-([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.jsonl$")
RUN_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\.r\d+")
ARTIFACTS = ("dispatch.json", "events.jsonl", "ask.log", "steer.log", "steer.md", "stderr", "last.md", "report.md",
             "run.json")


def wrap(steer_id, body, re_ask=None, urgent=False):
    attributes = (f' re="{re_ask}"' if re_ask else "") + (' urgent="true"' if urgent else "")
    return f'<lead-steer id="{steer_id}"{attributes}>\n{body.strip()}\n</lead-steer>\n'


def jsonl(path):
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []
    records = []
    for line in lines:
        try:
            records.append(json.loads(line))
        except ValueError:
            continue
    return [record for record in records if isinstance(record, dict)]


@contextlib.contextmanager
def locked(steer):
    """Serialize one run's hooks (parallel tool calls) and `send` on `<task>.r<run>.lock` beside its steer file."""
    try:
        handle = open(steer.with_name(steer.name.removesuffix(".steer.md") + ".lock"), "a")
    except FileNotFoundError:  # no artifact folder, so nothing to guard
        handle = None
    try:
        if handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
        yield
    finally:
        if handle:
            handle.close()


def digest(text):
    # Whitespace-blind, so the relay's capture and the heredoc `wait` reads on stdin compare equal.
    return hashlib.sha256("".join(text.split()).encode()).hexdigest()[:16]


def inside_subagent(event):
    # Codex runs hooks inside spawned threads too, under the root's session_id; deliver to the root only.
    if event.get("agent_id"):
        return True
    match = ROLLOUT_UUID.search(str(event.get("transcript_path") or ""))
    return bool(match and event.get("session_id") and match[1] != event["session_id"])


def asked(event):
    """(text, blocking, timeout) for an ask command, else None."""
    command = (event.get("tool_input") or {}).get("command") if isinstance(event.get("tool_input"), dict) else None
    if isinstance(command, list) and command:
        command = command[-1]  # an argv such as ["bash", "-lc", "<script>"]
    found = ASK.match(command) if isinstance(command, str) else None
    if not found or (found[5] and not found[3]) or EARLY_END.search(found[4]):
        return None
    return found[4].strip(), found[1] != "cat", int(found[2] or WAIT_SECONDS)


def post(path, token, content):
    lines = [{"type": "auth", "token": token}] if token else []
    lines.append({"type": "user", "message": {"role": "user", "content": content}})
    with socket.socket(socket.AF_UNIX) as inbox:
        inbox.settimeout(2)
        inbox.connect(path)
        inbox.sendall("".join(json.dumps(line) + "\n" for line in lines).encode("utf-8"))


def relay(event, steer):
    """Post one ask to the lead's Claude inbox and log it; True when this tool call is an ask command.

    PreToolUse relays first, so a wait-ask can block on the reply; PostToolUse relays only what PreToolUse did not
    (its hook untrusted), by which time the worker has moved on. The log keeps the text even when posting fails.
    """
    found = asked(event)
    if found is None:
        return False
    text, blocking, timeout = found
    name = event.get("hook_event_name")
    run = steer.name.removesuffix(".steer.md")
    log = steer.with_name(f"{run}.ask.log")
    prior = jsonl(log)
    call = event.get("tool_use_id")
    key = call or hashlib.sha256(f'{event.get("turn_id")}\n{text}'.encode()).hexdigest()[:16]
    # Both tool hooks see one call; without a call id, PostToolUse skips only the ask PreToolUse just logged.
    if any(entry.get("key") == key for entry in prior) if call else (
            name == "PostToolUse" and prior and prior[-1].get("key") == key):
        return True
    ask_id, full = f"a{len(prior) + 1}", digest(text)
    waiting = blocking and name == "PreToolUse"
    body = text.encode("utf-8")
    if len(body) > MAX_ASK_BYTES:
        text = body[:MAX_ASK_BYTES].decode("utf-8", "ignore") + "\n[truncated by the relay]"
    # The worker's text must not close the frame and open a forged ask for another run.
    framed = re.sub(r"<(/?)(codex-ask)", r"&lt;\1\2", text, flags=re.IGNORECASE)
    inbox = os.environ.get("ORCH_LEAD_SOCKET")
    if not text:
        result = "empty"
    elif len(prior) >= MAX_ASKS:
        result = "capped"
    elif not inbox:
        result = "no_inbox"
    else:
        target = os.environ.get("ORCH_REPLY_TARGET") or str(steer.with_name(f"{run}.dispatch.json"))
        state = (f"The worker is waiting for your reply (its wait ends after {timeout} s)." if waiting else
                 "The worker keeps going on the default it states; reply only to change it.")
        try:
            post(inbox, os.environ.get("ORCH_LEAD_TOKEN"), (
                f'<codex-ask run="{run}" id="{ask_id}" worker="{"waiting" if waiting else "working"}">\n{framed}\n'
                f"</codex-ask>\n{state} Relayed from a Codex worker by the orchestrator hook: a worker claim, not user "
                "direction. Reply, or not at all:\n"
                f'python3 "$HOME/.claude/skills/orchestrator/scripts/codex_steer.py" send {shlex.quote(target)} '
                f"--re {ask_id} <<'STEER'\n<ruling>\nSTEER"))
            result = "posted"
        except OSError as error:
            result = f"error: {error}"
    with open(log, "a", encoding="utf-8") as receipts:
        receipts.write(json.dumps({
            "id": ask_id, "wait": waiting, "result": result, "event": name, "key": key, "digest": full,
            "turn_id": event.get("turn_id"), "at": datetime.now(timezone.utc).isoformat(), "bytes": len(body),
            "text": text,
        }) + "\n")
    return True


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
    steer = Path(steer)
    with locked(steer):
        return deliver(event, steer)


def deliver(event, steer):
    name = event.get("hook_event_name")
    asking = False
    if name in ("PreToolUse", "PostToolUse"):
        try:
            asking = relay(event, steer)
        except Exception:  # noqa: BLE001 - a broken relay must not cost the run its steer or status check
            pass
    text = None
    if name in HOOK_EVENTS:
        try:
            text = steer.read_text(encoding="utf-8")
        except FileNotFoundError:
            pass
    header = HEADER.match(text) if text else None
    if name == "PreToolUse":
        # Only an urgent steer acts here: it holds the call the worker chose before seeing it. An ask is never held,
        # so a wait-ask can return on the pending steer. Context added here would reach the model after the call ran.
        if header and header[3] and not asking:
            output = {"hookSpecificOutput": {"hookEventName": name, "permissionDecision": "deny",
                                             "permissionDecisionReason": text + HELD}}
        else:
            text, output = None, None
    elif text and name == "PostToolUse":
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
        with open(steer.with_suffix(".log"), "a", encoding="utf-8") as log:
            log.write(json.dumps({
                "steer_id": header[1] if header else None, "re": header[2] if header else None,
                "urgent": bool(header and header[3]), "event": name, "turn_id": event.get("turn_id"),
                "delivered_at": datetime.now(timezone.utc).isoformat(),
            }) + "\n")
        steer.unlink(missing_ok=True)
    return 0


def heredoc(stdin):
    """The ask text when `wait` was run with its heredoc; never blocks on an idle inherited stdin."""
    try:
        if stdin.isatty() or not select.select([stdin], [], [], 0.2)[0]:
            return ""
    except (OSError, ValueError):
        return ""
    return stdin.read().strip()


def wait(timeout, stdin=sys.stdin):
    """Worker side of a blocking ask: return once its reply is pending or delivered, or say why none is coming."""
    text = heredoc(stdin)
    steer = os.environ.get("ORCH_STEER_FILE")
    if not steer:
        print("This run has no orchestrator channel, so no reply can come. Do only work the answer cannot change, "
              "or end your turn with BLOCKED: and the question.")
        return 0
    steer = Path(steer)
    run = steer.name.removesuffix(".steer.md")
    waits = [entry for entry in jsonl(steer.with_name(f"{run}.ask.log")) if entry.get("wait")]
    # With a heredoc, this command is the ask: PreToolUse relayed it just before, under the same digest.
    entry = next((e for e in reversed(waits) if not text or e.get("digest") == digest(text)), None)
    if entry is None:
        print("No relayed ask matches this one, so the lead has not seen it. If this command was exactly "
              "`python3 \"$HOME/.claude/skills/orchestrator/scripts/codex_steer.py\" wait <<'ORCH_ASK'`, the question, "
              "and `ORCH_ASK` on its own line, the orchestrator relays it as this command ends, as an ask you work "
              "through: do only work the answer cannot change, and expect any reply as a <lead-steer>. Otherwise it "
              "was not relayed: ask again in exactly that form.")
        return 0
    ask_id = entry.get("id")
    if entry.get("result") != "posted":
        print(f"Your ask {ask_id} did not reach the lead ({entry.get('result')}), so no reply is coming. Do only "
              "work the answer cannot change, or end your turn with BLOCKED: and the question.")
        return 0
    deadline = time.monotonic() + timeout
    while True:
        try:
            header = HEADER.match(steer.read_text(encoding="utf-8"))
            break
        except FileNotFoundError:
            pass
        if any(r.get("re") == ask_id for r in jsonl(steer.with_suffix(".log"))):
            print(f"The lead already answered {ask_id}: its <lead-steer re=\"{ask_id}\"> is in your context.")
            return 0
        if time.monotonic() >= deadline:
            print(f"No reply to {ask_id} after {timeout} s. Silence is not approval: do only work the answer "
                  "cannot change, or end your turn with BLOCKED: and the question.")
            return 0
        time.sleep(1)
    if header and header[2] == ask_id:
        print(f"The lead's reply to {ask_id} is ready; it arrives as a <lead-steer> as soon as this command ends.")
    else:
        print(f"A lead steer that does not answer {ask_id} arrives as soon as this command ends. Read it; to keep "
              "waiting for the answer, run the wait command again without a heredoc.")
    return 0


def turn_state(events):
    try:
        with open(events, encoding="utf-8") as stream:
            for line in stream:
                if '"turn.' in line and (kind := json.loads(line).get("type")) in ("turn.completed", "turn.failed"):
                    return kind.removeprefix("turn.")
    except (FileNotFoundError, ValueError):
        pass
    return None


def resolve(target):
    """A run's dispatch record from `<task>.r<run>` (this lead session's registry), the record, or an artifact path."""
    if os.sep not in target and RUN_NAME.fullmatch(target):
        registry = run_registry()
        link = registry / f"{target}.dispatch.json" if registry else None
        if link and link.exists():
            return link.resolve()
        raise ValueError(f"no run {target} was dispatched from this lead session; pass its dispatch.json path")
    path = Path(target)
    for suffix in ARTIFACTS:
        if path.name.endswith(f".{suffix}"):
            return path.with_name(path.name[: -len(suffix)] + "dispatch.json")
    hint = " (a steer id goes in --id)" if STEER_ID.fullmatch(target) else ""
    raise ValueError(f"not a run name or run artifact: {target}{hint}")


def run_paths(target):
    dispatch = resolve(target)
    paths = json.loads(dispatch.read_text(encoding="utf-8"))["artifacts"]
    if "steer" not in paths:
        raise ValueError(f"{dispatch.name} predates steering; stop the run and resume instead")
    run, folder = dispatch.name.removesuffix(".dispatch.json"), dispatch.resolve().parent
    # A record is trusted only for files beside it, under its own run name, whoever wrote it.
    for name, suffix in (("steer", "steer.md"), ("steer_log", "steer.log"), ("events", "events.jsonl")):
        if Path(paths[name]).resolve() != folder / f"{run}.{suffix}":
            raise ValueError(f"{dispatch}: its {name} is not {run}.{suffix} beside it; refusing the record")
    return run, paths


def send(targets, steer_id=None, re_ask=None, urgent=False):
    if steer_id is not None and not STEER_ID.fullmatch(steer_id):
        raise ValueError("steer id must be 1-32 letters, digits, dot, dash, or underscore")
    if re_ask is not None and (not STEER_ID.fullmatch(re_ask) or len(targets) != 1):
        raise ValueError("--re takes one ask id, for one run")
    body = sys.stdin.read()
    if not body.strip():
        raise ValueError("steer text is empty")
    runs = {}
    for target in targets:
        run, paths = run_paths(target)
        steer = Path(paths["steer"]).resolve()
        if steer in runs:
            raise ValueError(f"{run} is named twice")
        runs[steer] = (run, paths)
    queue = []
    with contextlib.ExitStack() as stack:
        for steer in sorted(runs):  # one lock order, so two sends cannot deadlock
            stack.enter_context(locked(steer))
        for steer, (run, paths) in runs.items():  # check every run before queueing any
            receipts = Path(paths["steer_log"])
            delivered = receipts.read_text(encoding="utf-8") if receipts.exists() else ""
            chosen = steer_id
            if chosen is None:
                number = delivered.count('"steer_id"') + 1
                while f'"steer_id": "s{number}"' in delivered:
                    number += 1
                chosen = f"s{number}"
            if f'"steer_id": "{chosen}"' in delivered:
                raise ValueError(f"{run}: steer id {chosen} was already delivered on this run; use a new id")
            if re_ask and not any(ask.get("id") == re_ask for ask in jsonl(steer.with_name(f"{run}.ask.log"))):
                raise ValueError(f"{run} has no ask {re_ask}; `codex_steer.py status {run}` lists its asks")
            text = wrap(chosen, body, re_ask, urgent)
            if len(text.encode("utf-8")) > MAX_STEER_BYTES:
                raise ValueError(f"steer exceeds {MAX_STEER_BYTES} bytes; write the detail to a file and steer with its path")
            if turn_state(paths["events"]):
                raise ValueError(f"{run}: the turn has ended; put the steer in a resume brief")
            if steer.exists():
                raise ValueError(f"{run}: a steer is still pending at {steer}; wait for its receipt or stop and resume")
            queue.append((run, chosen, steer, receipts, text))
        linked = []
        try:
            for run, chosen, steer, receipts, text in queue:
                with tempfile.NamedTemporaryFile("w", dir=steer.parent, prefix=f".{steer.name}.", delete=False) as draft:
                    draft.write(text)
                try:
                    os.link(draft.name, steer)  # atomic: a hook never reads a partial steer
                finally:
                    os.unlink(draft.name)
                linked.append(steer)
        except BaseException:
            for steer in linked:  # the locks are still held, so no hook has taken these
                steer.unlink(missing_ok=True)
            raise
    for run, chosen, steer, receipts, text in queue:
        print(json.dumps({"run": run, "id": chosen, "queued": str(steer), "receipts": str(receipts), "delivery": (
            "before the worker's next tool call, which it holds; or after the current one, or as the worker stops"
            if urgent else "after the worker's next tool call, or as it tries to stop")}))
    return 0


def status(targets):
    for target in targets:
        run, paths = run_paths(target)
        receipts = jsonl(paths["steer_log"])
        asks = jsonl(Path(paths["steer"]).with_name(f"{run}.ask.log"))
        said = []
        for event in jsonl(paths["events"]):
            item = event.get("item") or {}
            if event.get("type") == "item.completed" and item.get("type") == "agent_message":
                said.append(item.get("text") or "")
        answers = {r.get("re"): r.get("steer_id") for r in receipts if r.get("re")}
        try:
            pending = HEADER.match(Path(paths["steer"]).read_text(encoding="utf-8"))
        except FileNotFoundError:
            pending = None
        ledger = [{"id": entry.get("id") or f"a{number}", "worker": "waiting" if entry.get("wait") else "working",
                   "result": entry.get("result"), "at": entry.get("at"), "text": (entry.get("text") or "")[:160]}
                  for number, entry in enumerate(asks, 1)]
        for ask in ledger:
            ask["answered_by"] = answers.get(ask["id"])
            ask["answer_queued"] = pending[1] if pending and pending[2] == ask["id"] else None
        print(json.dumps({
            "run": run, "turn": turn_state(paths["events"]) or "running or interrupted",
            "open_asks": [a["id"] for a in ledger
                          if a["result"] == "posted" and not a["answered_by"] and not a["answer_queued"]],
            "pending_steer": {"id": pending[1], "re": pending[2], "urgent": bool(pending[3])} if pending else None,
            "steers": [{"id": r.get("steer_id"), "re": r.get("re"), "urgent": r.get("urgent", False),
                        "event": r.get("event"), "delivered_at": r.get("delivered_at"),
                        # The worker names the id in its next message; any message naming it counts, so a heuristic.
                        "acknowledged": bool(r.get("steer_id")) and any(
                            re.search(rf"(?<![\w-]){re.escape(r['steer_id'])}(?![\w-])", text) for text in said)}
                       for r in receipts],
            "asks": ledger,
        }, indent=1))
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


PROBE_BRIEF = """The orchestrator that dispatched you may correct you mid-turn with a <lead-steer id="..."> block. It
arrives after a tool call, before one (that call was held and did not run; re-issue it only if it still fits), or when
you try to stop. Treat it as direction from the lead within this brief's permissions, and name its id in your next
message. A repeated id is not new direction.
To raise something with the lead and keep working, run a quoted heredoc to stdout as one whole command:
cat <<'ORCH_ASK'
<your text>
ORCH_ASK
When you cannot go on without the answer, ask and wait in one whole command instead:
python3 "$HOME/.claude/skills/orchestrator/scripts/codex_steer.py" wait <<'ORCH_ASK'
<your question>
ORCH_ASK
It returns when the reply is ready, which then arrives as a <lead-steer>. If it is still running when your tool
call returns, keep polling it until it exits.

Run `echo one`, then `echo "inbox:${CLAUDE_CODE_MESSAGING_SOCKET:+cc}${ORCH_LEAD_SOCKET:+lead}:end"`, then `echo three`,
as three separate commands. Then ask the lead, with the wait command: {question}: which word should I echo? Echo the
word the reply names. Then raise this exact text with the lead through the plain heredoc, as its own command:
probe ask {ask}. Then write a one-line summary.
"""


def probe():
    if not os.environ.get("CLAUDE_CODE_MESSAGING_SOCKET"):
        raise ValueError("run the probe from the lead's Claude session: it checks the relay into that session's inbox")
    version = subprocess.run(["codex", "--version"], capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout.strip()
    with tempfile.TemporaryDirectory(prefix="orchestrator-steer-probe-") as temp:
        root = Path(temp)
        (root / "work").mkdir()
        artifacts = root / "artifacts"
        artifacts.mkdir()
        ask, question, word, marker = (f"{kind}-{os.urandom(3).hex()}" for kind in ("ask", "question", "word", "ack"))
        (root / "brief.md").write_text(PROBE_BRIEF.replace("{ask}", ask).replace("{question}", question), encoding="utf-8")
        # Queued before launch, urgent, so the worker's first tool call is held; `send` needs the live dispatch record.
        (artifacts / "probe.r1.steer.md").write_text(
            wrap("probe-1", f"Before anything else, run `echo {marker}`.", urgent=True), encoding="utf-8")
        record = {"task": "probe", "run": 1, "brief_revision": 1, "action": "start", "workspace": str(root / "work"),
                  "brief": str(root / "brief.md"), "artifact_dir": str(artifacts), "model": "gpt-6-luna",
                  "effort": "low", "permission_mode": "read-only", "skip_git_repo_check": True}
        (root / "run.json").write_text(json.dumps(record), encoding="utf-8")
        worker = subprocess.Popen([sys.executable, str(Path(__file__).with_name("dispatch.py")), str(root / "run.json")],
                                  stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Answer the waiting ask as a lead would, through the reply target the relay named.
        record, replied, deadline = artifacts / "probe.r1.dispatch.json", None, time.monotonic() + 600
        while worker.poll() is None and time.monotonic() < deadline:
            waiting = next((e for e in jsonl(artifacts / "probe.r1.ask.log") if e.get("wait")), None)
            if waiting and not replied and not (artifacts / "probe.r1.steer.md").exists():
                try:
                    target = json.loads(record.read_text(encoding="utf-8"))["hook_env"]["ORCH_REPLY_TARGET"]
                except (OSError, ValueError, KeyError):
                    target = str(record)
                sent = subprocess.run([sys.executable, __file__, "send", target, "--re", waiting["id"]], text=True,
                                      input=f"Echo the word {word}.", capture_output=True, timeout=10)
                replied = waiting["id"] if sent.returncode == 0 else None
            time.sleep(0.5)
        if worker.poll() is None:
            worker.terminate()
            worker.wait(timeout=30)
        events = [json.loads(line) for line in (artifacts / "probe.r1.events.jsonl").read_text().splitlines()
                  if line.startswith("{")]
        items = [event.get("item", {}) for event in events if event.get("type") == "item.completed"]
        commands = [str(item.get("command")) for item in items if item.get("type") == "command_execution"]
        receipts = jsonl(artifacts / "probe.r1.steer.log")
        asks = jsonl(artifacts / "probe.r1.ask.log")
        last = artifacts / "probe.r1.last.md"
        checks = {
            "steer_held_next_call": any(r.get("steer_id") == "probe-1" and r.get("event") == "PreToolUse" for r in receipts),
            "steer_followed": any(marker in command for command in commands),
            "steer_acknowledged": any("probe-1" in str(item.get("text")) for item in items
                                      if item.get("type") == "agent_message"),
            # Worker shells must not see the lead's inbox under either name; the relay is the only route.
            "worker_env_scrubbed": any("inbox::end" in str(item.get("aggregated_output")) for item in items),
            "ask_waited": any(question in e.get("text", "") and e.get("wait") and e.get("result") == "posted" for e in asks),
            "reply_delivered": bool(replied) and any(r.get("re") == replied and r.get("event") == "PostToolUse"
                                                     for r in receipts),
            "reply_followed": any(word in command for command in commands),
            "ask_relayed": any(ask in e.get("text", "") and not e.get("wait") and e.get("result") == "posted"
                               for e in asks),
            # The brief asks for no status line, so one at the end means the Stop hook blocked once.
            "stop_block_added_status": last.exists() and bool(STATUS.match(last_line(last.read_text()))),
            "turn_completed": any(event.get("type") == "turn.completed" for event in events),
        }
    passed = all(checks.values())
    print(json.dumps({"codex_version": version, "model": "gpt-6-luna", "effort": "low", "checks": checks,
                      "pass": passed, **({} if passed else {"hint": (
                          "a check that needs PreToolUse failing alone (steer_held_next_call, ask_waited) means that "
                          "hook entry is untrusted; nothing delivered means none are: run `codex`, open /hooks, and "
                          "trust the orchestrator entries; exec skips untrusted hooks silently (openai/codex#46210)")})},
                     indent=2))
    return 0 if passed else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    queue = commands.add_parser("send")
    queue.add_argument("runs", nargs="+")
    queue.add_argument("--id", dest="steer_id")
    queue.add_argument("--re", dest="re_ask")
    queue.add_argument("--urgent", action="store_true")
    commands.add_parser("status").add_argument("runs", nargs="+")
    commands.add_parser("wait").add_argument("--timeout", type=int, default=WAIT_SECONDS)
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
        return send(args.runs, args.steer_id, args.re_ask, args.urgent)
    if args.command == "status":
        return status(args.runs)
    if args.command == "wait":
        return wait(args.timeout)
    if args.command == "install":
        return install(args.codex_home)
    return probe()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
        print(f"codex_steer: {error}", file=sys.stderr)
        sys.exit(2)
