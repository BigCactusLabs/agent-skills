# Code mode: script forms for the orchestrator's mechanics

Read before the first script that dispatches, stops, watches, waits, or calls a control tool, and again before the first one after a compaction. Policy is in `SKILL.md`. Every other reference is the orchestrator skill's own (`~/.claude/skills/orchestrator/references/`, `REFERENCE.md`, `AUDIT.md`); those files are written for a lead with direct tools, and this file gives the script form of each mechanic they name.

Checked 2026-11-16 on claude-code 2.1.326, in a session whose `REPL` calls return `(dispatched #N)`; the Codex mechanics were probed 2026-11-13 on 2.1.325 with codex-cli 0.167.2. A statement here was probed or seen in a session unless it cites the docs or says unprobed; the probes, sessions and counts behind each are in `AUDIT.md` (the 2026-11-14 and 2026-11-16 entries). Not yet run on 2.1.326: a Codex launch, stop, or steer through the helper (a launch and a stop ran on 2.1.325).

## Translation table

| The orchestrator files say | In a script |
|---|---|
| `Bash(run_in_background: true)` for `dispatch.py` | the awaited launch below, with `.timeout(5000)`; read `o.running.taskId` |
| "the harness task handle" | `o.running.taskId`; the command's own output streams to `o.running.outputPath` |
| `TaskStop` on the Bash handle | `await tools.TaskStop({task_id})`, only after `stop_worker.py` reports `still_running` |
| `Agent` tool | `await tools.Agent({description, prompt, subagent_type, effort, isolation})`. It returns at once with `agentId` and `outputFile`, and echoes the whole `prompt`: keep the result in a variable and return only `agentId`, or every brief comes back into your context. The findings arrive with the completion notification, not from this call |
| `SendMessage` | `await tools.SendMessage({...})`; take the parameters from `describeTool("SendMessage")` |
| A failed call to a built-in tool (`Agent`, `TaskStop`, `SendMessage`, `Monitor`, and the rest) | It resolves `{error}` and does not throw (an MCP tool throws). Read `r.error` after each one and stop on it; for `Agent`, check `agentId` before writing the record. Unchecked, a refused dispatch is recorded with no agent, and a failed stop or steer reads as sent. An `isolation: "worktree"` call from a directory that is not a git repository is refused this way |
| Monitor-tool watch | `await tools.Monitor({description, command, timeout_ms})`; `timeout_ms` defaults to 5 minutes and is capped at 30, so re-arm at expiry. Since 2.1.326 a watch that expires with no events says when its command wrote to stderr and names the file holding that output: read it before re-arming, because the watcher may have failed to start |
| Read a file, a report, the manifest | `await file(path).text()`, several at once with `Promise.all` |
| A command in a worktree or another directory | `git -C <dir> ...` for git; otherwise absolute paths, or `.cwd(<dir>)` on the `$` call, which runs as `cd '<dir>' && ...`. Whether a `cd` lasts into later scripts and into workers spawned afterwards has differed between versions, so no command relies on where an earlier one left the shell: each names its directory, and every brief gives absolute paths |
| View an image or a PDF | `await tools.Read({file_path})`; a bare `Read` call outside a script is refused |
| An MCP tool | `tools["mcp__<server>__<tool>"]`, called like any other tool. Copy the name from `searchTools` or `tools.list()`, never guess it: a guess that wrote a hyphenated server's name with underscores failed |

## Launching a Codex run

```js
const o = await $`python3 ~/.claude/skills/orchestrator/scripts/dispatch.py ${runJson}`.nothrow().timeout(5000);
if (o.exitCode !== null) throw new Error("dispatch refused or ended at once: " + o.output);
const handle = o.running.taskId;   // record in the manifest with the run
```

- **Why a short timeout.** A command that outlives its timeout moves to the background: the await resolves with `exitCode: null` and `running: {taskId, outputPath}`, the script goes on, and the worker keeps running. The helper replaces itself with `codex exec`, so the handle tracks the worker's real process. A record the helper refuses fails inside the 5 seconds and comes back as an exit code instead (the timeout path was probed with a 25 s timeout; a refusal has not been provoked).
- **Completion.** When the worker's process exits, a `task-notification` event for that `taskId` arrives with the exit status. It means the process exited, as the orchestrator files say of the same signal: Codex completion is still the run's `turn.completed` plus a non-empty `.last.md`.
- **Every Codex question goes through the helper,** a one-off read-only sweep included. A bare `codex exec` skips the helper's preflight and sandbox configuration (`runtime.md`) and can run at an effort that is not a rung.
- **Several launches** go in one script, one `await` each in sequence, so each handle is recorded against its run before the next starts.
- **Never un-awaited, and never `&`, `nohup`, or `setsid`.** An un-awaited `$` gives no task handle, and in a session that waits on scripts it is stopped when the script ends, which would kill the worker. With `&`, `nohup`, or `setsid` the harness tracks the wrong process.
- **A session that waits on scripts.** Scripts run in the background only in a session started in auto or `bypassPermissions` mode. A session started in another mode, switched out of its starting mode, picked from the `claude --resume` list, or started with tool names passed to `--tools` waits on each script and stops it after ten minutes ([long-running code](https://code.claude.com/docs/en/code-mode#long-running-code)). When `REPL` calls stop returning `(dispatched #N)`, one of these is the cause and nothing is broken. The remedy is the user's and differs by case, before the next dispatch: a switched mode, Shift+Tab back to the starting mode; a session picked from the resume list, exit and run `claude --continue --permission-mode auto` (the form the docs give); a session started in another mode or with `--tools`, start again in auto or `bypassPermissions` without that flag. Whether a command moved to the background at its timeout survives the script's end in such a session is unprobed: check the worker is alive (`ps -p <pid>` from `.dispatch.json`) right after the first launch.
- **A launch that does not start** either throws, or returns an exit code or `o.error` and no handle, which the check above catches. Read `o.output` and `o.error` before repairing the run record, because the refusal may not be the helper's:
  - *The harness.* A `null` or `undefined` `${}` value throws before anything runs, so a `runJson` an earlier script never assigned fails loudly. A command holding a control character (NUL, ESC, CR, BEL; tab and newline pass) does not run, and under `.nothrow()` comes back as `exitCode: 1` with `command contains control characters that would be hidden in the approval dialog` in `o.stderr`. 2.1.326 also asks about or refuses more sandboxed commands (its changelog does not list which).
  - *A hook.* Every in-script call reaches `PreToolUse` hooks under its usual tool name, a `$` command as `Bash` ([permission checks](https://code.claude.com/docs/en/code-mode#permission-checks)). In Code Mode a hook that cannot start, is killed, exits 126, 127 or above 128, or times out refuses the call even with no `onFailure` set ([docs](https://code.claude.com/docs/en/code-mode#tool-call-refused-by-a-hook)). `the hook failed` or `the hook did not finish` is a defect in a hook (`destructive-guard.py` and `ensure-output-dir.py` both run on every `$` command), not in the run record or the brief: tell the user, and do not retry the launch.
- **Long runs.** An interactive terminal lead has no time limit on background commands, a command moved at its timeout included; the 30-minute and 2-hour limits in `runtime.md` apply to `-p`, SDK, CI and cloud runs ([tools reference](https://code.claude.com/docs/en/tools-reference#time-limit-for-background-commands)). Two things can still stop a worker under an idle lead. When the operating system reports critical memory pressure and the session has been idle 30 minutes with no turn or subagent running, Claude Code stops its background tasks, and a Codex worker is one ([how backgrounding works](https://code.claude.com/docs/en/interactive-mode#how-backgrounding-works); the debug log says why; `CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP=1` turns it off and is not set here). A task whose output passes 5 GB is stopped too. For a run expected past 30 minutes, arm `watch_events.py` and treat a missing notification as a cue to check the PID.

## Cross-model review of a Claude diff

```js
const r = await $`codex review --base main > ${reviewFile} 2>&1`.cwd(worktree).nothrow().timeout(5000);
// r.running.taskId; the verdict is the last lines of reviewFile when the task notification arrives
```

`--base` takes no prompt argument (they are mutually exclusive), so the review runs bare from the worktree whose branch holds the diff. It is a Codex process in the worker's tree, so it runs only after that worker has ended. The output file is the full transcript, often over 100K characters: read its tail, not the file. Read the [review brief](../../orchestrator/references/briefs-and-repairs.md#verification-and-review-brief) first as for any review; `codex review` takes no brief, so its rules apply to how you rule on the findings. Run once this way, with `cd` in place of `.cwd()`.

When the diff is already a pull request and the repository has the Codex GitHub review connected, `gh pr comment <n> --body "@codex review"` asks for a review of the pushed head, so it comes after a push the user has authorized. [Waiting for it](#waiting-on-something-that-sends-no-notification) has its own section below.

## Stopping and steering

`stop_worker.py`, `codex_steer.py send`, and `dispatch.py --check-worktree` are ordinary awaited commands. A steer body goes through a heredoc exactly as `runtime.md` shows: build it in a JS string and pass it with `${{raw: ...}}` only when it contains no worker-supplied text, otherwise write it to a file and redirect stdin from the file. The file route is also the only one for a body with a carriage return or an escape sequence (pasted worker output, a CRLF file), which `$` refuses.

## The drain script

"Drain, then act" is one script per wake:

1. Read the manifest and, for every run a notification named, its `.last.md`, the tail of `.events.jsonl`, and `.ask.log`, in one `Promise.all`. From a Claude worker's report file take the status line and verdict first (its tail), then only the sections a ruling needs: a fleet's reports returned whole can fill the context and force a compaction.
2. Return those to yourself. Rule on them in your reply, not in the script: classification of findings and asks is judgment.
3. Send the steers, replies and manifest updates in the next script, all in one.

**Run records.** Keep them in a REPL variable (`runs[task] = {runJson, handle, agentId, base, status, repairs, notes}`) and rewrite the whole manifest from it after every change (`write(manifest, render(runs))`, with the object also saved as JSON beside it so a restarted session can reload it). Do not patch the manifest with string replacement: an anchor such as `status: running` matches several records and edits the first one. The manifest file is the record: variables survive a compaction, but not a restart, resume, fork, or wake.

**After a compaction the first script is a re-read,** before any dispatch, steer, or ruling: this file, the reference for the next step, the manifest, and the current brief, each returned whole, never a `preview()` or a `.slice()` of one. `compact_reread.py`, a `SessionStart` hook registered in user settings (`REFERENCE.md`, standing roles), prints this instruction after a compaction in a session that invoked the skill (the hooks reference says the matcher covers automatic compaction too; only a manual `/compact` was probed); where it is not installed, the summary at the top of the context is the only cue. `runs` is still there after a compaction, but the text of the references is not: leads that skipped or cut the re-read then sent a brief without its standing clauses, left a worker out of the manifest, and returned whole `Agent` results. The summary can be older than the context it opens, so the manifest outranks it.

**Waiting.** End the turn: the notification starts your next one, and the wait costs no turns. `Poll` waits too, but with nothing to deliver it returns shortly before the prompt cache would expire (about five minutes), and each return is a round that re-reads the conversation. So call `Poll` for a wait that should end within a few minutes or to collect events that arrive close together, and end the turn for a longer one. Unmeasured: whether a `Poll` call the harness adds to your reply returns the same way. Do not write a polling loop that sleeps on a worker. An `Agent` completion arrives as a `task-notification` beside a `Poll` result of `(no pending events)`: that result is the wake, not an idle turn.

## Waiting on something that sends no notification

A worker's exit and an `Agent` completion wake you. A review bot on GitHub, CI checks, a pull request's mergeability, a lock another session holds, and your own long build do not. Three facts decide the form of the wait:

- **A script is stopped after 600,000 ms of its own time,** whatever `timeout` the call asked for, and no setting changes that ([long-running code](https://code.claude.com/docs/en/code-mode#long-running-code)). `sleep()` counts toward it; time inside an awaited tool call does not. A `while (...) { ...; await sleep(45000) }` loop holds the turn for ten minutes and then ends with `REPL execution timed out`.
- **An awaited long command holds the turn** for as long as its `.timeout()` allows (7,200,000 ms at most), and the user hears nothing until it returns.
- **A command that outlives its `.timeout()` moves to the background and notifies on exit,** as a Codex launch does. One that starts with `sleep` is stopped at its timeout instead, so a wait never begins with `sleep`.

So the wait is a shell loop with a bound, launched with a short timeout. For the Codex GitHub review of head `sha` on pull request `pr`:

```js
const test = `gh api repos/{owner}/{repo}/issues/${pr}/comments --paginate --jq '.[] | select(.user.login=="chatgpt-codex-connector[bot]") | .body' | grep -F 'codex-review-state:v1' | grep -F '"commit_sha":"${sha}"' | grep -qF '"status":"completed"'`;
const once = await $`${{raw: test}}`.cwd(repo).nothrow();   // exit 1 with empty output: the test runs and is not yet true
const w = await $`for i in $(seq 60); do ${{raw: test}} && exit 0; sleep 30; done; exit 1`.cwd(repo).nothrow().timeout(3000);
// record w.running.taskId; "completed" means the review is in, "failed with exit code 1" means 30 minutes passed without one
```

- **Run the test once before the loop,** and read its output. A test that can never match (`jq` escaping inside the template was the cause once) runs to its bound past a review that has already landed. `test` goes in with `{raw: ...}`, so build it only from values you produced (a PR number, a SHA).
- **The Codex connector** keeps one summary comment per pull request and edits it in place. The comment carries `<!-- codex-review-state:v1 {"code_review":{"commit_sha":...,"has_any_findings":...,"status":"running"|"completed"}, ...} -->`. A clean pass appears only there, not as a review. After the wait, read `has_any_findings` from the same marker and then the pull request's review comments. The format is the connector's and can change: a test that stops matching is the first thing to check.
- **CI checks:** `gh pr checks <n> --watch --fail-fast > ${log} 2>&1`, launched the same way (not run here).
- **A long build, gate, or sweep of your own:** the same launch, output redirected to a log. Before ending the turn, tell the user what is running and how long it should take. On the notification read the log; never rerun the command for its output.

## Which workers run in code mode

Code mode is on by default here (`CLAUDE_CODE_EXPERIMENTAL_CODE_MODE` in the user settings `env`). It applies per session, and Codex workers and some Claude surfaces run without it, so a fleet is mixed:

| Worker | Mode | Basis |
|---|---|---|
| Lead (interactive CLI, Fable 5.2 or a 5.5 model) | code mode | observed |
| Codex workers | not applicable | — |
| `pr-reviewer-opus`, `scout-sonnet`, `researcher-opus`, `implementer-opus`, `general-purpose` | code mode | observed: their transcripts hold `REPL` and `Poll` calls |
| `docs-sync-sonnet`, `Explore`, `Plan` | expect code mode | not observed |
| `claude --bg` sessions | plain | Code Mode docs: refused with `it doesn't work in background jobs`; not observed |
| `claude -p` | plain, always | docs; observed |
| Teammates, in a session launched with teams on | in-process: code mode; split pane: plain | Code Mode docs (requirements); not observed |

Consequences:

- **Write briefs that work in both modes.** Name outcomes and commands, not tool calls: "run `cargo test -p x`", never "use the Bash tool".
- **A worker cannot `write()` its report.** A read-only role's script API lists `write`, and the call throws `Write tool is not available in this REPL context`. A `general-purpose` worker has Write, but the harness refuses a report file from a subagent (`Subagents should return findings as text, not write report files`). So the `Reports:` line of every brief that names a report file says: "If your tools are REPL and Poll, `write()` is not available to you: write the file with a shell redirect from a script." (`printf %s ${text} > ${path}` round-trips backticks, quotes and `$`.) The sentence in the brief is what has worked; the same sentence in the reviewer and researcher role files is unconfirmed. Do not add Write to a read-only role instead: its tool list is a guarantee.
- **A worker's REPL is its own.** It does not see your variables, it starts in the session's current directory, and its scripts draw eval numbers from the same counter as yours, so your numbers jump while workers run.
- **Hooks fire on the shell commands a script runs, yours and a Claude worker's:** `destructive-guard.py` on all of them, `role-guard.py` on a read-only role's (its refusal comes back as `exitCode: 1` with the reason in `o.error`). Each ask from `destructive-guard.py` interrupts the user. It is silent for untracked content under an agent worktree and for targets under temp roots, which include the scratchpad, so a write brief tells the worker to build into fresh directories instead of clearing old ones. Keep following the confirm-first rule yourself. If a `UserPromptSubmit` hook is ever added to user settings, it will also run on script output that `Poll` delivers (`source: poll_event`) and can withhold a drain result ([docs](https://code.claude.com/docs/en/code-mode#code-output-withheld-by-a-hook)); none is registered now.
- **An isolated subagent is refused some git.** In a harness worktree that is `git bisect run`, `git maintenance register|start`, `scalar` set-up, some commands that can rewrite branches shared with your checkout (2.1.326; neither the changelog nor the docs list them), git pointed at the main checkout (`git -C`, `--git-dir`, `GIT_DIR` or `GIT_WORK_TREE`, or a `cd` there first), and any command whose git the harness cannot verify from its text (a computed command name, `${!name}`, syntax it cannot parse), which the worker is told to split into plain commands ([the checks](https://code.claude.com/docs/en/worktrees#how-claude-code-enforces-isolation)). A worker that reports a refused git command has hit this, not a brief defect: rule on whether the command was needed. The checks do not track writes (`cp` or a shell redirect into the main checkout is not refused), and Codex workers and un-isolated legs get no check at all, so the brief's path rules and the destructive-command floor stay in every brief.
- **Teams.** They are off in user settings, so in a default session `Agent` has no `name` parameter and workers are addressed by agent ID. A job whose workers must message each other is relaunched with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 claude` after the user confirms, and can stay under `/cm-orchestrator`: with both variables set the session starts in Code Mode, in-process teammates run in it, and split-pane teammates run plain ([requirements](https://code.claude.com/docs/en/code-mode#requirements)). In that session the naming trap in `claude-workers.md` applies, since the [agent teams docs](https://code.claude.com/docs/en/agent-teams#how-claude-starts-agent-teams) state it with no Code Mode exception: run `describeTool("Agent")` first, and pass `name` only together with `isolation`. Unprobed: no team has been run from a code-mode lead here. A root-cause question does not need a team ([diagnosis legs](../../orchestrator/references/routing.md#diagnosis-legs)).
- **A lead started in auto mode** (not the default here, which is `bypassPermissions`). The classifier reviews a script once, not each call, and sending a second script while the first still runs drops the first one's review. Its next call that needs approval shows the user a two-minute countdown, and after one countdown expires, later calls are refused without a prompt until the user sends a message ([docs](https://code.claude.com/docs/en/code-mode#permission-prompt-with-a-countdown)). The 2.1.326 binary also holds refusal text for an `Agent` or `SendMessage` call that the review did not cover. So in auto mode each dispatch goes in a script that ends before the next is sent. Not provoked here.

## Script pitfalls

- **Names a script cannot declare.** `log`, `file`, `write`, `edit`, `sleep`, `preview`, `running`, `tools`, `self`, `console`, and every tool name (`Agent`, `Read`, `Bash`, `SendMessage`, ...) are globals: `const log = ...` is refused. `process` and `require` do not exist.
- **A script that throws leaves its later `const` and `let` names defined and `undefined`.** The next script reads them with no ReferenceError. `$` refuses an undefined value, but `tools.*` drops an undefined field and a template string prints `undefined` (an email draft was created with no body this way). Rebuild the value before the next script uses it.
- **What ran before a throw stays done.** The error lists the tool calls that completed, and a worker launched before the throw is running. Sending a dispatching script again launches every worker a second time, so first read what launched (`runs`, each run's `.dispatch.json`, the handles the script logged) and send only the steps that did not happen. Send a whole script again only when nothing in it had taken effect, and put nothing that can throw between a dispatch and its manifest write.
- **`$` runs zsh.** An unquoted glob or regex in the template text that matches no file fails with `no matches found` (`--include=*.py`). Pass it as a `${}` value, which `$` quotes.
- **`$` reports the last stage of a pipeline.** `gate | tail -6` returns 0 over a failing gate. Redirect to a log and read the command's own `exitCode`, or `set -o pipefail`.
- **One command per key when you will compare outputs.** Two commands chained into one output read as one list.
- **`write()` and `edit()` are the Write and Edit tools.** `write()` refuses a file a shell command changed since you read it (`File has been modified since read`): read it again with `file()`. A batch `edit` applies nothing when one anchor is missing or matches twice, so copy anchors from the file, not from a `grep` that may return two lines. `await` every `write()`, the manifest's first of all.
- **A backtick ends a template literal.** Build text that holds backticks (Markdown, shell) in ordinary quotes, or read it from a file.
- **After resolving a conflict by script,** run `git diff --check`: a scripted resolver can leave conflict markers behind.

## Keeping in step

`SKILL.md` here is `orchestrator/SKILL.md` (sha256 `2ed71b78feea…`, 2026-11-16) with these changes: the code-mode paragraph and table row, reference links pointed at `../orchestrator/references/`, the Codex and Claude dispatch bullets (the `name` clause is conditional on teams being on, see the worker-modes section above), `tools.` prefixes on `TaskStop` and `Monitor`, and wording trims to stay under 20,000 characters (the starting-rung mapping and report-ownership detail point to their references; the `Scripts:` line, the tier-routing evidence pointer, and half of the bypass-worker rationale are gone). No policy differs.

- A policy change goes into `orchestrator/SKILL.md` first, with its `policy-checks.md`, `AUDIT.md` and `test_skill_docs` steps, and is then mirrored here. A change to script mechanics goes here only.
- To see drift: `diff <(sed 's#(references/#(../orchestrator/references/#g' ~/.claude/skills/orchestrator/SKILL.md) ~/.claude/skills/cm-orchestrator/SKILL.md`.
- Both files must stay under 20,000 characters, because that is all Claude Code re-attaches after a compaction.
- Evidence stays out of this file. It is read whole before the first dispatch and after every compaction, so a probe date, a session count, or an incident goes in `AUDIT.md`, and this file keeps the instruction and the one reason a lead needs.
- Re-run the probes behind this file after a Claude Code upgrade that changes how scripts background commands, and update the date in the second paragraph.
