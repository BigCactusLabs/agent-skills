# CLI fallback workers

Use only when native delegation is unavailable or a separate CLI process is needed, and delegation is permitted. These are bounded workers; the invoking Astra session remains the sole lead. Never copy its orchestration role into a CLI worker. Do not start an external process to evade native limits, tool restrictions, sandboxing, or an approval rejection.

## Preflight

Every CLI write worker needs its own manually prepared worktree (`git worktree add -b <task> <path>`), with a verified base and required inputs. The 2026-09-11 probe of Codex 0.154.0's native `--worktree` was not adopted: detached HEAD, resume ran in the invoking cwd, and `resume --worktree` was refused. This dated probe is not a claim about later versions; preserve explicit workspace control unless a new probe supports a change.

Read local help once before the first CLI dispatch:

```bash
codex --version
codex login status
codex exec --help
codex exec resume --help
```

The examples below match local `codex-cli 0.154.0` help (checked 2026-09-11; `exec`, `exec resume`, and `exec fork` all accept the helper's flags). They were syntax-checked, not validated by a live CLI worker job. Recheck flags when the version differs. If auth is absent, report it; login is a user action. Do not print credential files.

Pin `-m` and `-c model_reasoning_effort` on every dispatch and resume. The installed default may be Astra, which must not become an accidental bulk worker. Rungs: `-m gpt-6-luna -c model_reasoning_effort=max`, `-m gpt-6-sol -c model_reasoning_effort=high`, `-m gpt-6-astra -c model_reasoning_effort=low`; Terra and every `gpt-5.6-*` tier are off the ladder, and Sol `medium` is not a rung. Before the first Sol dispatch in a session, run a one-turn `-m gpt-6-sol -s read-only` probe to confirm access. Its catalog entry sets `node_repl_auto_review_required`, as Astra's does; a read-only probe on 2026-09-22 ran shell and Node REPL calls with no approval or review reported. Use `-s read-only` for inspection or `-s workspace-write` for an authorized isolated write task. Do not use permission-bypass flags, ignore user rules, or widen writable roots to work around a denied action. Route any required escalation through the parent session's approval mechanism.

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
  "model": "gpt-6-sol",
  "effort": "high",
  "permission_mode": "workspace-write"
}
```

Choose model/effort from the existing routing. `permission_mode` accepts only `read-only` or `workspace-write`; bypass modes are rejected before launch. Native workers inherit the parent sandbox and use native tool arguments instead of this JSON. Do not copy the Claude orchestrator's bypass-capable launcher: this skill has its own self-contained version with Codex boundaries.

Run the helper through `tools.exec_command` with a short `yield_time_ms`, preserving the **whole returned result**, including its process `session_id`:

```bash
python3 "$HOME/.codex/skills/codex-orchestrator/scripts/dispatch.py" "/absolute/task-scratch/TASK-ID.g1.run.json"
```

In code-mode, expose `text(await tools.exec_command(...))`, not only `result.output`. Do not append `&` or detach another process. The helper uses the assigned workspace as cwd, feeds the brief through a finite stdin file, and replaces itself with Codex. The harness retains the worker process and its real exit status. Poll that process with `tools.write_stdin`, with waits no longer than 60 seconds. Use the handle as the primary completion signal; after startup inspection, read logs for failures, missed milestones, or specific decisions, not between routine waits merely to confirm activity. If `functions.exec` itself yields a cell ID, use `functions.wait` only for that running cell; these IDs manage different layers. A PID is diagnostic and can be reused later; it is not a substitute for the managed session handle.

Artifacts share `<task>.g<generation>`: `.dispatch.json`, `.events.jsonl`, `.stderr`, `.last.md`, and a separately authored `.report.md`. The helper creates the artifact directory and refuses any existing output path for that generation. Keep old files and advance the generation instead of overwriting them. Its exclusive dispatch marker also prevents two callers from launching the same generation through this helper. The marker records requested argv, cwd, brief hash, and paths; it proves preparation, not completion or acceptance. Update the current manifest record after launch, result collection, and adjudication; appended history alone is insufficient.

Assign a write worker's detailed report to its owned writable `.report.md` path; the CLI owns `.last.md`. A read-only worker returns its full report as the final response for Astra to persist from `.last.md`. A denied optional report write is reported once with the content returned; do not widen permissions or repeat the write through another tool. Apply [report ownership](briefs-and-repairs.md#report-ownership-and-recovery).

Record the thread ID from `thread.started` wherever it occurs in the JSONL stream, separately from the process handle. Keep requested model/effort separate from actual settings exposed by the runtime. The helper initializes runtime values as unknown; do not infer them from config defaults, requested argv, or worker guesses. If observed later, record the evidence source in the current manifest. When auditing usage, use each thread's final cumulative total or per-turn differences; do not sum cumulative terminal totals across resumed generations.

Optional JSON fields: `thread_id` (required for resume/fork), `output_schema` (absolute existing file), `web_search` (`disabled`, `cached`, or `live`), and `skip_git_repo_check` (boolean, false by default; only needed outside Git). Effort accepts `none`, `low`, `medium`, `high`, `xhigh`, `max`; `ultra`, `minimal`, and `persistent` are refused. No arbitrary extra CLI arguments are accepted. For a specialized invocation that the helper does not support, inspect current CLI help and preserve explicit model/effort/sandbox, finite stdin, assigned cwd, distinct artifacts, and the existing approval boundaries. Unsupported fields or denied actions do not authorize permission bypass.

Track task/revision/generation using [communication.md](communication.md). Treat a run as successful only after process completion, a successful terminal turn event, a nonempty final artifact for that generation, and passing acceptance checks. A failed turn, nonzero exit, absent final artifact, or truncated stream is incomplete. Inspect command failures and file changes rather than reading every reasoning event. Preserve diagnostics and partial edits before recovery or retry. If the process and child writes stopped and saved current-generation evidence suffices, Astra can verify the output and write a recovery report. Keep acceptance separate; the interrupted CLI turn remains incomplete. Do not resume merely to obtain a final message, or automatically retry auth/quota/rate-limit failures. Quiet output may mean a long command is still running; inspect its state against the task-specific expectation before interrupting.

## Resume and fork

Apply the [resume check](briefs-and-repairs.md#task-record-and-resume-check), including counters and the recorded user/project review policy. Wait for the prior process and owned writes to stop, advance `generation`, and retain task identity and earlier evidence. Set `action` to `resume` with the exact thread UUID, point `brief` to the new instructions, and repeat model, effort, workspace, and permission mode even for same-tier environment recovery. Invoke the same helper; it supplies the cwd and sandbox config because resume lacks `--cd` and `-s`.

For a fork, verify `codex exec fork --help` on the installed CLI first, then use `action: fork` with the source UUID and a fresh generation. Record the new thread ID from the result. Forking preserves the source context, so it does not cure a poisoned approach or provide a fresh independent reviewer. A fresh replacement gets a self-contained brief seeded from the actual checkpoint, with task identity, counters, and resolved policy preserved.

The resumed brief assigns the new generation's detailed report path when the worker owns one. Never use `--ephemeral` for a worker that may need resume. For live steering, prefer native workers. Do not assume CLI queue or external-child messaging behavior based on source notes; verify the available control surface before depending on it.

## Tool and output limits

CLI workers do not automatically inherit session connectors or browser state. Check the required tool before assigning a tool-bound leg. If a lookup requires web access, verify the installed search configuration; do not copy old boolean web-search flags. Carry the user's required HTTP user agent, `OpenAI File Downloader, XaiImageApiFetch/1.0`, into any brief that makes configurable web requests.

If the user specifically requests a Codex CLI review, use a read-only `codex exec` brief with the exact snapshot and acceptance contract. This avoids assuming that custom prompts can be combined with scoped `codex review` flags. The default independent reviewer remains Claude.

`--output-schema` can constrain a final JSON result, but the lead must still validate the artifact and substantive claims. For a tool-heavy leg, prefer an ordinary work report and a separate bounded formatting pass if machine-readable output is actually required. Do not add formatting turns to normal coding tasks.
