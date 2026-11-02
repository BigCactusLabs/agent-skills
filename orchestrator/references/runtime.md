# Reliable dispatch and checks

Read before the first Codex worker launch. Use the dispatch helper for standard starts, resumes, and forks. It makes omitted model/effort flags and reused artifact names fail before launch. It does not choose a tier, approve permissions, enforce review policy, or decide acceptance.

## Dispatch from one record

After reading the current manifest and brief, write a fresh `<task>.r<run>.run.json`:

```json
{
  "task": "TASK-ID",
  "run": 1,
  "brief_revision": 1,
  "action": "start",
  "workspace": "/absolute/worker-worktree",
  "brief": "/absolute/scratchpad/briefs/TASK-ID.r1.md",
  "artifact_dir": "/absolute/scratchpad/artifacts",
  "model": "gpt-6.1-sol",
  "effort": "high",
  "permission_mode": "workspace-write"
}
```

Use the model, effort, and permission mode selected for this task under the existing routing and authorization (the example shows `workspace-write`; the task-surface table defaults implementation legs to `bypass`, so choose deliberately). `permission_mode` is required: `read-only`, `workspace-write`, or `bypass` (the existing explicitly authorized bypass lane). This helper grants no new authority. For resume/fork, set `action` and the exact `thread_id`, advance `run`, and point `brief` to the new complete instructions. Repeat model and effort even when unchanged. Retain old records.

Run with the main session's `Bash(run_in_background: true)`:

```bash
python3 "$HOME/.claude/skills/orchestrator/scripts/dispatch.py" "/absolute/scratchpad/artifacts/TASK-ID.r1.run.json"
```

The helper runs in `workspace` for all three actions, sends the brief through a finite stdin file, and replaces itself with Codex. There is no extra background process or shell evaluation of the prompt. The harness receives the worker's real process exit, while the streams go directly to disk. Save the returned **harness task handle** in the manifest; the PID in the dispatch record is diagnostic, not a substitute for that handle or proof the same process is still alive later.

Artifacts share one prefix: `.dispatch.json` (requested record, argv, PID, paths, brief hash, hook environment), `.events.jsonl`, `.stderr`, `.last.md`, the separately authored `.report.md`, for steers `.steer.md` (pending only) and `.steer.log` (receipts), and `.ask.log` (asks the worker sent the lead). Existing paths cause refusal; reconcile them or use the next run number. A prepared dispatch record proves neither launch success nor completion. Read the current events and last message after the harness completes; keep the existing `turn.completed` / `turn.failed` acceptance checks.

The helper records requested settings, with runtime model/effort initially unknown. If the CLI exposes actual settings, record the observation and its source in the current manifest. Otherwise leave them unknown. Configuration defaults, worker guesses, and the requested argv are not actual-runtime evidence. Extract the thread ID from a `thread.started` event wherever it occurs, not necessarily the first line. Do not sum cumulative usage from multiple resumes; use each thread's final total or per-turn differences when auditing usage.

Optional fields are `lead_inbox` (boolean, default true; `false` for an untrusted-input leg, so the run cannot post to the lead), `output_schema` (absolute file path), `web_search` (`disabled`, `cached`, or `live`), `skip_git_repo_check` (boolean, default false; set it only for a workspace outside a Git repo, since the default keeps Codex's outside-a-repo guard), and `user_gated: true`, which is **required** when `effort` is `ultra` and records that the user authorized this dispatch; the helper refuses `ultra` without it and refuses `minimal` and `persistent` outright. The helper intentionally covers the ordinary CLI surface only. A specialized invocation such as `--approve-for-me` must keep its existing permission controls and use the same explicit model/effort, cwd, finite stdin, and unique-artifact contract; do not switch permission mode to fit the helper. Inspect current CLI help before using an unsupported flag. Validate the helper locally with stdin closed (`python3 -m unittest scripts.test_dispatch`); its CLI is a stub, so no worker tokens are used. Argv is checked against `codex exec`, `exec resume`, and `exec fork --help` at the codex-cli version pinned in `SKILL.md`'s footer.

## Stop and watch a run

`scripts/stop_worker.py <task>.r<run>.dispatch.json [--grace 30] [--term-grace 10]` stops one run. It signals the recorded PID only while that process's command line still carries the run's `--output-last-message` path, so a reused PID is refused (`identity_mismatch`, exit 2). It sends SIGINT, which `exec` turns into a turn interrupt, then SIGTERM after the grace period, and never SIGKILL; SIGTERM also covers a SIGINT that lands before the session is configured, when `exec` has no handler yet. It lists the process's descendants before signalling and reports any that outlive the stop. Outcomes: `stopped_by_sigint` or `stopped_by_sigterm` (exit 0), `not_running` (exit 0), `still_running` (exit 1: use `TaskStop` on the harness handle). The report includes the events file's last event. An interrupted `exec` turn exits 1 and writes no `turn.completed`/`turn.failed` event and no `.last.md`, so the harness reports exit 1 for a clean stop and the stop report is the only record of it; read the exit with that report, not as a failed implementation. Record the stop and its outcome in the manifest before any resume, and confirm no descendant is still writing before a replacement takes the worktree.

`scripts/watch_events.py <dispatch.json> --own <path> [--own <path>] --from-offset 0` is a Monitor-tool watch: it prints one line per alert (an edit outside the owned paths, the same command failing `--repeat` times (default 3), `--stall-seconds` without an event (default 600), `--idle-items` tool calls in a row with no file change and no first-seen command (default 0, off; arm it at about 20 on write legs, since a read-only leg legitimately edits nothing), an `error` event, the turn's end, or the process exiting without one) and exits when the turn ends. The idle alert fires once per streak and re-arms after an edit or a new command; it catches a worker busy without new state, which the stall alert cannot see. Pass Monitor's deadline explicitly: 5 min by default, 30 at most, 10 in `-p`. Omit `--own` to skip the scope check. Since codex-cli 0.166.0 `exec` may drop item notifications under backpressure and recovers them only when the turn completes (openai/codex#57800; whether recovered items reach the JSON stream is unprobed), so a quiet `--own` watch is not proof of scope: the final diff is. Re-arm without `--from-offset`, which starts at the file's current size, so alerts for earlier events are not repeated. An alert is a cue to read the events file; completion still needs the current run's `turn.completed` and a non-empty `.last.md`.

Tests: `python3 -m unittest scripts.test_stop_worker scripts.test_watch_events` with stdin closed; both use stub processes and spend no model usage. The SIGINT handling they model was checked live on codex-cli 0.160.0 (`AUDIT.md`).

## Steer a running Codex worker

`scripts/codex_steer.py` is one Codex hook, on `PreToolUse`, `PostToolUse`, and `Stop`, that acts only when the dispatch helper set `ORCH_STEER_FILE`; every other Codex session runs it as a no-op. Set it up once per machine:

1. `python3 "$HOME/.claude/skills/orchestrator/scripts/codex_steer.py" install` appends the hook to `$CODEX_HOME/hooks.json` after any existing hooks, so their trust keys don't move, and keeps a timestamped backup. It adds only the events missing.
2. The **user** runs `codex`, opens `/hooks`, and trusts the three orchestrator entries. `codex exec` skips an untrusted hook without a warning, and only the interactive CLI records trust (openai/codex#46210). Trust covers the hook definition, not the script, so script edits keep it; a change to its command or timeout needs review again. Never give a worker `--dangerously-bypass-hook-trust`: it waives trust for every user, project, and plugin hook in that invocation. Without a trusted `PreToolUse` entry, urgent steers land after the call instead of before it, and waiting asks fall back to working asks.
3. `codex_steer.py probe` runs one gpt-6-luna `low` read-only turn through the dispatch helper. It checks that an urgent steer held the first call and was followed and acknowledged, that the worker environment is scrubbed, that a waiting ask was relayed before its command ran and its `--re` reply delivered and followed, that a working ask was relayed, the `Stop` block, and `turn.completed`. Run it from the lead's Claude session: its two asks land there as `<codex-ask run="probe.r1" id="a1" worker="waiting">` and `id="a2" worker="working"`, and the probe answers the waiting one itself through the reply target the relay named, so neither needs a reply from you. Run it again after each CLI upgrade.

Send a steer, one or more runs at a time:

```sh
python3 "$HOME/.claude/skills/orchestrator/scripts/codex_steer.py" send <task>.r<run> [<task>.r<run> ...] [--urgent] [--re <ask id>] <<'STEER'
<correction>
STEER
```

A run name resolves through this lead session's registry: when `CLAUDE_CODE_SESSION_ID` is set, the dispatch helper links `<task>.r<run>.dispatch.json` under `$TMPDIR/orchestrator-runs/<session>/`. A name already held by another live record keeps it, and the newer run is answered by its record path, which the relay then names. A dispatch record or any artifact path of the run works from any session; `send` trusts a record only for files beside it under its own run name. The id defaults to the next `s<n>` on that run, and `--id` sets one; a positional id after the record path is refused. `send` takes each run's lock (`<task>.r<run>.lock`, shared with the hook), checks every run, then writes each `<task>.r<run>.steer.md` atomically, so one refusal queues none and a failed write rolls back the others; it prints one JSON line per run. It refuses a run named twice, a second pending steer, a reused id, a `--re` id the run never asked, more than 8,000 bytes (Codex previews hook text past about 2,500 tokens, so name a file for detail), and a run whose turn already ended.

A plain steer arrives as developer context after the worker's next local tool call (shell, `apply_patch`, MCP, code-mode nested calls; hosted web search fires no hook), or, if the worker tries to stop first, as a `Stop` block whose reason becomes its next prompt. `--urgent` also holds the worker's next tool call: `PreToolUse` denies it with the steer as the reason, so the worker reads the correction before acting rather than after a call it chose without it. Use `--urgent` when the next call could act on the wrong premise (an edit, a migration, a long test run); a plain steer suffices when the correction can wait one call. An ask command is never held. With parallel tool calls the hooks take the run's lock in turn, so one call is held and the others run. On delivery the hook appends a receipt (id, `re`, `urgent`, event, turn) to `<task>.r<run>.steer.log` and removes the pending file. The receipt proves delivery; the worker's next `agent_message` naming the id is the acknowledgement; only the diff or report shows the steer applied. A worker inside one long command sees even an urgent steer only when that command reports back; when that is too late, stop and resume. A steer still pending at the turn's end was never delivered: put it in the resume brief.

`codex_steer.py status <task>.r<run> ...` prints each run's message ledger: turn state, the pending steer, every ask with the steer that answered it (`answered_by`) or the queued reply (`answer_queued`), `open_asks` (posted, with neither), and every delivered steer with whether any worker message names it (`acknowledged`, a heuristic: read the message).

### Asks: a Codex worker messages the lead

A worker asks by running one quoted heredoc as a whole command, in one of two forms:

- **Working ask:** `cat <<'ORCH_ASK'` … `ORCH_ASK`. The worker states the default it is proceeding on and keeps going. It writes nothing, so read-only sandboxes can ask.
- **Waiting ask:** `python3 "$HOME/.claude/skills/orchestrator/scripts/codex_steer.py" wait [--timeout S] <<'ORCH_ASK'` … `ORCH_ASK`, for a question the worker cannot work around. `PreToolUse` relays it before the command runs; `wait` then polls up to 600 s and returns once the reply is pending, and the reply arrives as `<lead-steer re="a<n>">` when the command reports back. On timeout it tells the worker that silence is not approval: do only work the answer cannot change, or end the turn with `BLOCKED:`. When no relayed ask matches (the `PreToolUse` entry untrusted, or a command not in the documented form), `wait` returns at once and says so; the `PostToolUse` relay still posts a documented-form ask, as a working ask. The brief tells the worker to keep polling a `wait` that is still running when its tool call returns.

The hook posts the text, capped at 4,000 bytes, to the lead's Claude inbox socket as `<codex-ask run="<task>.r<run>" id="a<n>" worker="waiting|working">`, then a line saying whether the worker is blocked and the `send … --re a<n>` command that answers it, naming the run by its short name when the registry has it. A lead that is idle starts a turn on it. One tool call relays once, though both tool hooks see it; asks are numbered under the run's lock. Every ask, posted or not, is logged in `<task>.r<run>.ask.log` with its id, kind, text, and result (`posted`, `no_inbox`, `capped` after 20, `empty`, or `error: …`). Only command text matches, never command output, so a file the worker reads cannot post an ask by itself. The match follows bash's heredoc rules: anything before the opener or after the terminator, a terminator bash would not accept, or a body line that would end the heredoc early means the command is not an ask, so shell commands cannot ride inside one. Text that would close or open a `<codex-ask>` frame is escaped. A worker following injected text can still ask, so an ask is a worker claim. Answer with `send --re`, or not at all: silence on a working ask leaves the stated default standing. Asks from a worker's own Codex subagents are not relayed.

The dispatch helper moves the lead's `CLAUDE_CODE_MESSAGING_SOCKET`/`_TOKEN` to `ORCH_LEAD_SOCKET`/`_TOKEN` for the hook, records the token as `<redacted>`, and passes `-c shell_environment_policy.exclude=["CLAUDE_CODE_MESSAGING_*", "ORCH_LEAD_*", "CLAUDE_CODE_SESSION_ID"]`, which replaces any `exclude` list in config.toml; the session id names the run registry, so worker shells don't get it either. Without that, a bypass worker's shell inherits both variables and could post anything into the lead session. Hooks keep the variables because Codex builds their environment from its own process environment, not the shell policy (the probe's `worker_env_scrubbed` and `ask_relayed` checks). Same-user processes can still find the socket on disk, so this closes the inherited route, not every route. Likewise the registry sits under `$TMPDIR`, which a `workspace-write` sandbox can write, and a worker can write its own pending-steer file; the record checks in `send` limit a tampered link to a misdirected steer. Set `lead_inbox: false` on untrusted-input legs, and answer them by record path.

Codex runs hooks inside a worker's spawned subagents too, under the root thread's `session_id`; the hook delivers only to the root thread (no `agent_id`, and the rollout id matches the session id). On `Stop` it also applies `status_contract.py`'s rule to Codex workers, except on `output_schema` runs (`ORCH_STATUS_LINE=0`), whose final reply must stay pure JSON. Models refuse instructions that arrive through hook context unless the brief says the channel exists, so a Codex brief keeps the template's steer clause ([worker brief](briefs-and-repairs.md#worker-brief)). Source and probe evidence: `REFERENCE.md`, Codex hooks fine print. Tests: `python3 -m unittest scripts.test_codex_steer scripts.test_dispatch` with stdin closed.

## Test ownership and reuse

The lead defines contract-derived acceptance cases. The existing implementation worker authors and runs routine regressions in its owned paths, reusing established fixtures and harnesses. Assign shared harness changes one owner and extend that harness only when a case needs it; do not regenerate DOM, HTTP, or UI setup for successive increments. If a harness is missing, assign the smallest necessary setup with the implementation.

The lead independently inspects the integrated diff and test assertions, with targeted integration probes where needed. Additional lead-authored tests address a named uncovered risk. Independence does not require a duplicate harness or a standing second test agent. Preserve meaningful regression coverage and required gates.

## Prepare the worktree once

Before launch, run the repo-owned bootstrap/readiness command in each new worktree, using the pinned toolchain and required per-process environment. Check dependencies, test discovery, and offline assets required by that leg. Reuse existing setup/doctor tools; do not invent a project-specific command in this generic skill. If no readiness command exists, perform the smallest equivalent check and record its result. Do not run the full suite as a readiness probe.

Share a discovered environment fix with affected workers. Repair missing prerequisites before a same-tier continuation; environment recovery alone is not a reason to raise model or effort. If a worker already produced a usable commit and only a lead-owned check remains, the lead can verify and record it without a worker turn solely for validation/report cleanup.

## Preserve check scope, logs, and process handles

Before a costly check, inspect its selection/dry-run output when available. A command named `fast` may select the full suite. Record the selected scope and reason, assign the full check to its owner, and retain repository-required gates. Do not suppress unknown paths or evidence-bearing fixtures merely to obtain a smaller selection.

For each long check, record owner, exact command/cwd/environment requirements, tested SHA **and dirty-state description**, selected scope, fresh log path, harness handle, and final exit/result. Keep secrets out of these records. Use the repo's check wrapper when it provides this evidence; otherwise a shell wrapper can preserve the true exit status:

```bash
set -C
log="/absolute/scratchpad/artifacts/TASK-ID.r1.check-name.log"
result="/absolute/scratchpad/artifacts/TASK-ID.r1.check-name.exit"
exec 3>"$result" || exit 2
exec 4>"$log" || exit 2
# Replace this argv with the assigned command; do not wrap it in eval.
check_rc=0
npm run check:fast >&4 2>&1 || check_rc=$?
printf '%s\n' "$check_rc" >&3
tail -n 40 "$log"
exit "$check_rc"
```

Use fresh names. An empty `.exit` file means no final result was recorded; it is not a pass. Keep the process under one harness-managed background/yielded call, with no additional `&`. In Codex code-mode, expose the whole tool result (for example `text(await tools.exec_command(...))`), including `session_id`, instead of printing only `.output`. Poll that same handle until completion. For a tail, read the existing log. Never rerun a check just to recover its output, and never launch the same check while its earlier process may still be running. If a handle is lost, reconcile the saved log and process evidence first; do not infer completion from a quiet log or wrapper exit 0.

Record which snapshot actually ran. A later docs-only commit can inherit a check after the lead inspects the intervening diff and confirms it cannot affect that check; keep `tested_sha`, `accepted_sha`, and the carry-forward reason separate. Docs may drive generated code or bind evidence, so this requires an actual diff read. Do not relabel a check onto the later SHA or rerun solely to obtain a newer label.
