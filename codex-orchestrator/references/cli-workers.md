# CLI fallback workers

Use only when native delegation is unavailable or a separate CLI process is needed, and delegation is permitted. These are bounded workers; the invoking Astra session remains the sole lead. Never copy its orchestration role into a CLI worker. Do not start an external process to evade native limits, tool restrictions, sandboxing, or an approval rejection.

## Preflight

Every CLI write worker needs its own manually prepared worktree (`git worktree add -b <task> <path>`), with a verified base and required inputs. The 2026-09-11 probe of Codex 0.154.0's native `--worktree` was not adopted: detached HEAD, resume ran in the invoking cwd, and `resume --worktree` was refused. This dated probe is not a claim about later versions; preserve explicit workspace control unless a new probe supports a change. Codex 0.164.0 retired the `worktrees` feature flag ([PR #54175](https://github.com/openai/codex/pull/54175)), but `exec --worktree` still refuses `resume` (and `review`, `--ephemeral`, `--ignore-user-config`), so a resumed worker would lose its worktree; the manual worktree stays (checked 2026-10-26, not re-probed live). In 0.166.0 and 0.167.0 help, `exec resume` and `exec fork` also list `--worktree`; whether resume still refuses it or runs outside the managed tree was not re-probed (checked 2026-11-10, help only), so the manual worktree rule is unchanged. Use a linked worktree (`git worktree add`), not a copy or an ordinary checkout: under `workspace-write` a commit needs the linked worktree's git paths, which the helper grants ([sandbox grants](#sandbox-grants-and-limits)).

Read local help once before the first CLI dispatch:

```bash
codex --version
codex login status
codex exec --help
codex exec resume --help
```

The examples below match local `codex-cli 0.167.0` help (checked 2026-11-10; `exec`, `exec resume`, and `exec fork` all accept the helper's flags; `--cd`, `-s`, and `--add-dir` exist on `exec` only, which is why the helper sets `sandbox_mode` and writable roots through `-c`). A helper start and a `workspace-write` resume ran live on luna `low` on 2026-11-10. Recheck flags when the version differs. If auth is absent, report it; login is a user action. Do not print credential files.

Pin `-m` and `-c model_reasoning_effort` on every dispatch and resume. The installed default is `gpt-6.1-sol` at `low` since CLI 0.159.1 (Astra before that); neither may become an accidental setting. Rungs: `-m gpt-6-luna -c model_reasoning_effort=max`, `-m gpt-6.1-sol -c model_reasoning_effort=medium` (machine-checked) or `xhigh` (review-checked), `-m gpt-6-astra -c model_reasoning_effort=low` (terminal-heavy loops, Sol retry); Terra, `gpt-6-sol` and every `gpt-5.6-*` tier are off the ladder, and Sol `high` is not a rung (2026-09-30 eval: same recall as `medium` at 1.6× the cost). Before the first Sol dispatch in a session, run a one-turn `-m gpt-6.1-sol -s read-only` probe to confirm access. Its catalog entry sets `node_repl_auto_review_required`, as Astra's does; a gpt-6-sol read-only probe on 2026-09-22 ran shell and Node REPL calls with no approval or review reported, and 45 gpt-6.1-sol bypass runs on 2026-09-30 (`medium`, `high`, `xhigh`) raised no approval or auto-review item without calling the REPL. Use `-s read-only` for inspection or `-s workspace-write` for an authorized isolated write task. Do not use permission-bypass flags or widen writable roots to work around a denied action. Route any required escalation through the parent session's approval mechanism.

**Execpolicy rules defeat the sandbox unless ignored.** A `.rules` `prefix_rule(..., decision="allow")` runs a matching simple command outside the sandbox. `~/.codex/rules/default.rules` allows bare `rm`, `cp`, `mv`, `touch`, `chmod`, `git`, `python3`, `npm`, `curl`, `docker`, and many more, so on 2026-11-10 a luna worker's bare `touch ~/…` wrote under both `read-only` and `workspace-write` (0.166.0 and 0.167.0), while the same write inside a compound command was denied and `codex sandbox` denied it too. With `--ignore-rules` the bare write was denied. The helper therefore passes `--ignore-rules` on every action. The user's rules hold only `allow` decisions, so this removes no protection; recheck that before relying on it if `forbidden` or `prompt` rules appear. A manual `codex exec` outside the helper needs the same flag. Native workers and the lead still load the rules (see [native agents](native-agents.md#permission-and-configuration-checks)). `codex sandbox` does not apply execpolicy rules, so a sandbox probe through it does not show what a worker can do.

## Start a worker

Prepare the worker's worktree and brief first using [execution checks](execution-checks.md#prepare-the-worktree-once). For standard Codex CLI starts/resumes/forks, use the bundled sandbox-only `scripts/dispatch.py`. It is a local argument/artifact helper, not an alternative to native delegation or an authority to launch a worker. It does not change this skill's model ladder, approvals, or review policy.

Write one fresh task/generation JSON record in authorized scratch space. All fields below are required:

```json
{
  "task": "TASK-ID",
  "generation": 1,
  "brief_revision": 1,
  "action": "start",
  "workspace": "/absolute/worker-worktree",
  "brief": "/absolute/task-scratch/TASK-ID.g1.brief.txt",
  "artifact_dir": "/absolute/task-scratch/artifacts",
  "model": "gpt-6.1-sol",
  "effort": "medium",
  "permission_mode": "workspace-write"
}
```

Choose model/effort from the existing routing (Sol `high` is not a rung). `permission_mode` accepts only `read-only` or `workspace-write`; bypass modes are rejected before launch. Native workers inherit the parent sandbox and use native tool arguments instead of this JSON. Do not copy the Claude orchestrator's bypass-capable launcher: this skill has its own self-contained version with Codex boundaries.

Run the helper through `tools.exec_command` with a short `yield_time_ms`, preserving the **whole returned result**, including its process `session_id`:

```bash
python3 "$HOME/.codex/skills/codex-orchestrator/scripts/dispatch.py" "/absolute/task-scratch/TASK-ID.g1.run.json"
```

In code-mode, expose `text(await tools.exec_command(...))`, not only `result.output`. Do not append `&` or detach another process. The helper uses the assigned workspace as cwd, feeds the brief through a finite stdin file, and replaces itself with Codex. The harness retains the worker process and its real exit status. Poll that process with `tools.write_stdin`, with waits no longer than 60 seconds. Use the handle as the primary completion signal; after startup inspection, read logs for failures, missed milestones, or specific decisions, not between routine waits merely to confirm activity. If `functions.exec` itself yields a cell ID, use `functions.wait` only for that running cell; these IDs manage different layers. A PID is diagnostic and can be reused later; it is not a substitute for the managed session handle.

Artifacts share `<task>.g<generation>`: `.dispatch.json`, `.events.jsonl`, `.stderr`, `.last.md`, and a separately authored `.report.md`. The helper creates the artifact directory and refuses any existing output path for that generation. Keep old files and advance the generation instead of overwriting them. Its exclusive dispatch marker also prevents two callers from launching the same generation through this helper. The marker records requested argv, cwd, brief hash, paths, the generation's `tmpdir`, and any cache redirects (`worker_env`); it proves preparation, not completion or acceptance. Update the current manifest record after launch, result collection, and adjudication; appended history alone is insufficient.

Assign a write worker's detailed report to its owned writable `.report.md` path; the CLI owns `.last.md`. A read-only worker returns its full report as the final response for Astra to persist from `.last.md`. A denied optional report write is reported once with the content returned; do not widen permissions or repeat the write through another tool. Apply [report ownership](briefs-and-repairs.md#report-ownership-and-recovery).

Record the thread ID from `thread.started` wherever it occurs in the JSONL stream, separately from the process handle. Keep requested model/effort separate from actual settings exposed by the runtime. The helper initializes runtime values as unknown; do not infer them from config defaults, requested argv, or worker guesses. If observed later, record the evidence source in the current manifest. When auditing usage, use each thread's final cumulative total or per-turn differences; do not sum cumulative terminal totals across resumed generations.

Optional JSON fields: `thread_id` (required for resume/fork), `network` (boolean, `workspace-write` only, default true; `false` for an untrusted-input write leg), `output_schema` (absolute existing file), `web_search` (`disabled`, `cached`, or `live`), and `skip_git_repo_check` (boolean, false by default; only needed outside Git). Effort accepts `none`, `low`, `medium`, `high`, `xhigh`, `max`; `ultra`, `minimal`, and `persistent` are refused. No arbitrary extra CLI arguments are accepted. For a specialized invocation that the helper does not support, inspect current CLI help and preserve explicit model/effort/sandbox, finite stdin, assigned cwd, distinct artifacts, and the existing approval boundaries. Unsupported fields or denied actions do not authorize permission bypass.

Track task/revision/generation using [communication.md](communication.md). Treat a run as successful only after process completion, a successful terminal turn event, a nonempty final artifact for that generation, and passing acceptance checks. A failed turn, nonzero exit, absent final artifact, or truncated stream is incomplete. Inspect command failures and file changes rather than reading every reasoning event. `exec` can drop item events under backpressure and recovers them only at turn end (openai/codex#57800, 0.166.0), so a scope or progress judgment comes from the final diff, not from a quiet stream. Preserve diagnostics and partial edits before recovery or retry. If the process and child writes stopped and saved current-generation evidence suffices, Astra can verify the output and write a recovery report. Keep acceptance separate; the interrupted CLI turn remains incomplete. Do not resume merely to obtain a final message, or automatically retry auth/quota/rate-limit failures. Quiet output may mean a long command is still running; inspect its state against the task-specific expectation before interrupting.

## Sandbox grants and limits

Ported from the Claude orchestrator's helper (2026-11-06 and 2026-11-09), with writable roots moved to `-c` and `--ignore-rules` added on 2026-11-10.

**Every generation gets a fresh `TMPDIR`** (`orch-<task>.g<generation>.*` under the lead's temp root, recorded as `tmpdir`). The helper refuses to dispatch when that root sits inside the workspace or a git repository. Workers that read their ownership as a fence on every write had moved `TMPDIR` into the worktree, which broke tests that need temp paths outside a repo. Do not put a `TMPDIR=` override in a brief's commands or reuse a hand-made temp path across generations.

**Under `workspace-write` the helper also sets** `sandbox_workspace_write.writable_roots` to: the lead's temp root (the sandbox's temp root follows `TMPDIR`, but macOS `mktemp(1)` ignores it); the artifact dir, for the owned report and check logs; and, in a linked worktree, the worktree's gitdir plus the repository's shared `objects`, `refs`, and `logs`, so `git commit` works while the repository's `config` and `hooks` stay read-only. It pins `sandbox_workspace_write.network_access` from `network` and points `UV_CACHE_DIR`, `npm_config_cache`, `PIP_CACHE_DIR`, and `XDG_CACHE_HOME` at `orchestrator-cache/` under the lead's temp root; the real `~/.cache` stays read-only. Other tool caches (cargo, pnpm, Go) are not redirected; a worker that hits a denied write reports it, and the lead redirects that cache or keeps the leg local. Never add the repository's `.git` itself as a root: the worktree's `index.lock` stays denied while the repository's `config` and `hooks/` become writable (probed on 0.166.0 and 0.167.0). An ordinary checkout cannot commit under `workspace-write`; committing legs use linked worktrees.

**What the sandbox does not stop.** Probed with `codex sandbox` on 0.166.0 and 0.167.0 (Claude orchestrator `AUDIT.md`, 2026-11-09), which applies the policy but not execpolicy rules. With `--ignore-rules` a worker's commands get that policy: the 2026-11-10 helper smoke matched it for `~` (denied), `TMPDIR`, `mktemp`, and a linked-worktree commit (allowed). A `workspace-write` worker can write its worktree, its `TMPDIR`, the lead's whole temp root, `/private/tmp`, the artifact dir, and in a linked worktree its gitdir plus the repository's shared `objects`, `refs`, and `logs`. `read-only` denies all of these, `TMPDIR` included. What follows:

- **The files git reads inside the worktree.** The gitdir grant covers `commondir` and `gitdir`, which git follows from the worktree to the repository's config. A worker that rewrites `commondir` makes the next git command inside that worktree load a config it chose (`core.fsmonitor`, hooks), which runs code outside the worker's sandbox. A repository planted in a subdirectory does the same for git run inside it, and for `git status` or `git diff` at the worktree root once it is staged.
  - **Work from your own checkout.** `git -C <lead checkout> diff <base>..<sha>`, `log`, `merge`, `branch -D`, and `worktree list` read none of those files. Review and integrate there, by SHA.
  - **Before any git command inside the worktree,** run `python3 "$HOME/.codex/skills/codex-orchestrator/scripts/dispatch.py" --check-worktree <worktree root>` after the generation has ended and no child command is still writing, and again after every later generation there. Plain `git worktree remove` counts: it runs `git status` inside the tree. Exit 0: nothing found, which covers git run at the worktree root (a symlinked directory is not followed). Exit 1: one reason per line, and no git runs in that tree. `tampered:` reasons are layouts git never writes and are a scope breach; `inspect:` reasons can come from the repository's own setup (submodules, vendored repositories, a `config.worktree`, an unlistable directory) but name a config the worker could have written. Exit 2 is a usage error, such as a path that is not the worktree root.
  - **After a failed check,** copy out anything needed, then remove the tree with `git worktree remove --force` from your checkout, which does not run git inside it. Removal is a destructive action under the usual user authorization.
  - **Exit 0 does not cover the worker's files.** Tests, build scripts, and a hooks path inside the tree (husky) are worker-written code like the rest of the diff; read the diff before running them.
- **Every ref and object in the repository.** `refs/heads/*` is writable, `main` included. Record the base SHA and each branch tip relied on, bind review and merge to resolved SHAs, and confirm `main` and the integration branch still sit at the recorded SHAs before integrating.
- **Other generations' artifacts and the shared caches.** Briefs, task records, and every generation's artifacts sit in writable directories, and `orchestrator-cache/` is one store for every sandboxed worker. A worker that follows injected text can rewrite a sibling's report or plant a cache entry the next worker installs; nothing in the helper detects it.

Narrowing this (closing `/private/tmp`, per-generation output and cache directories) is an open user decision in the Claude skill as well. Until then, pick the weakest sandbox that works: an untrusted-input leg that needs no writes runs `read-only`, and an untrusted-input write leg sets `network: false`.

## Stop a worker

Stop a running CLI worker with `tools.write_stdin({session_id, chars: "\u0003"})` on the helper's session handle. The Ctrl-C reaches `codex exec` as SIGINT, which it turns into a turn interrupt. Do not `kill` the recorded PID from a sandboxed command: under `workspace-write`, signalling a process that another command started fails with `Operation not permitted` (checked 2026-10-03 with `codex sandbox`). This route was checked in parts on 2026-10-03, not end to end: a 0.160.0 `write_stdin` Ctrl-C ended a `sleep` with exit 130, a terminal Ctrl-C reached a sandboxed process whose stdin was a file (as under the helper), and a live 0.160.0 `exec` run showed the interrupt behavior below.

An interrupted `exec` exits 1 (about 1.5 seconds after the signal in that run) and writes no `turn.completed` or `turn.failed` event and no `.last.md`. The rollout records `turn_aborted`, the worker's child commands die, and `exec resume` continues the thread with the interrupted turn visible. Read that exit 1 together with the recorded stop, not as a failed implementation. Record the stop in the task record before any resume, and confirm no child command is still writing before a replacement takes the worktree. If the session is still running 30 seconds after the Ctrl-C, report its handle and PID; an escalated `kill -TERM` needs the user's approval.

## Resume and fork

Apply the [resume check](briefs-and-repairs.md#task-record-and-resume-check), including counters and the recorded user/project review policy. Wait for the prior process and owned writes to stop, advance `generation`, and retain task identity and earlier evidence. Set `action` to `resume` with the exact thread UUID, point `brief` to the new instructions, and repeat model, effort, workspace, and permission mode even for same-tier environment recovery. Invoke the same helper; it supplies the cwd and sandbox config because resume lacks `--cd` and `-s`.

For a fork, verify `codex exec fork --help` on the installed CLI first, then use `action: fork` with the source UUID and a fresh generation. Record the new thread ID from the result. Forking preserves the source context, so it does not cure a poisoned approach or provide a fresh independent reviewer. A fresh replacement gets a self-contained brief seeded from the actual checkpoint, with task identity, counters, and resolved policy preserved.

The resumed brief assigns the new generation's detailed report path when the worker owns one. Never use `--ephemeral` for a worker that may need resume. A CLI worker has no mid-turn steer: `codex queue` adds a follow-up after the turn through the shared daemon (openai/codex#48928) and does not reach a running `exec` turn. A correction is a [stop](#stop-a-worker) and a resume generation; for live steering, prefer native workers.

## Tool and output limits

CLI workers do not automatically inherit session connectors or browser state. Check the required tool before assigning a tool-bound leg. Under `read-only`, zsh, `/bin/sh`, and `/bin/bash` 3.2 cannot run a heredoc (`can't create temp file for here document`; probed 2026-11-09 on 0.167.0), so a read-only brief must not depend on one. If a lookup requires web access, verify the installed search configuration; do not copy old boolean web-search flags.

If the user specifically requests a Codex CLI review, use a read-only `codex exec` brief with the exact snapshot and acceptance contract. This avoids assuming that custom prompts can be combined with scoped `codex review` flags. The default independent reviewer remains Claude.

`--output-schema` can constrain a final JSON result, but the lead must still validate the artifact and substantive claims. For a tool-heavy leg, prefer an ordinary work report and a separate bounded formatting pass if machine-readable output is actually required. Do not add formatting turns to normal coding tasks.
