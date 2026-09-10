# CLI fallback workers

Use only when native delegation is unavailable or a separate CLI process is needed, and delegation is permitted. These are worker processes; Astra remains the lead. Do not start an external process to evade native limits, tool restrictions, sandboxing, or an approval rejection.

## Preflight

Read local help once before the first CLI dispatch:

```bash
codex --version
codex login status
codex exec --help
codex exec resume --help
```

The examples below match local `codex-cli 0.153.4` help (checked 2026-09-09). They were syntax-checked, not validated by a live CLI worker job. Recheck flags when the version differs. If auth is absent, report it; login is a user action. Do not print credential files.

Pin `-m` and `-c model_reasoning_effort` on every dispatch and resume. The installed default may be Astra, which must not become an accidental bulk worker. Rungs: `-m gpt-5.6-luna -c model_reasoning_effort=max`, `-m gpt-5.6-terra -c model_reasoning_effort=xhigh`, `-m gpt-6-astra -c model_reasoning_effort=low`; Terra `max` is off the ladder. Use `-s read-only` for inspection or `-s workspace-write` for an authorized isolated write task. Do not use permission-bypass flags, ignore user rules, or widen writable roots to work around a denied action. Route any required escalation through the parent session's approval mechanism.

## Start a worker

Prepare the worker's worktree and brief first, and create the output directory. Use task-specific absolute paths. A prompt file through stdin avoids shell interpolation of user text; do not construct shell code with JSON.stringify or unescaped message text.

Illustrative shell command after the named files and directory exist:

```bash
codex exec \
  -m gpt-5.6-terra -c model_reasoning_effort=xhigh \
  -s workspace-write \
  --cd /absolute/worker-worktree \
  --json \
  --output-last-message /absolute/task-scratch/implementation.md \
  - < /absolute/task-scratch/brief.txt \
  > /absolute/task-scratch/implementation.jsonl \
  2> /absolute/task-scratch/implementation.stderr
```

Use `tools.exec_command` with a short `yield_time_ms`; keep its returned process `session_id` if still running. Do not append `&` or detach another process. Poll that process with `tools.write_stdin` as needed, with waits no longer than 60 seconds. If `functions.exec` itself yields a cell ID, use `functions.wait` only for that running cell. These two IDs manage different layers.

For read-only work, change the model to Luna where the routing test permits it and use `-s read-only`. `--skip-git-repo-check` is only needed outside a Git repository. For prompt-as-argument calls, close stdin with `</dev/null`; a prompt file redirection already ends stdin at EOF.

Record the `thread_id` from the `thread.started` JSONL event separately from the shell process ID. The thread ID is needed for resume. Keep stdout JSONL separate from stderr. Parse event types; do not assume the first output line is the thread record. Inspect command failures and file changes rather than reading every reasoning event.

Track task/revision/generation using [communication.md](communication.md). Treat a run as successful only after process completion, a successful terminal turn event, a nonempty final artifact for that generation, and passing acceptance checks. A failed turn, nonzero exit, absent final artifact, or truncated stream is incomplete. Preserve diagnostics and partial edits before deciding on a bounded retry. Do not automatically retry quota, rate-limit, or auth failures. A process with no recent output may still be running a long command; inspect its state against the task-specific time expectation before interrupting, not merely after a fixed number of quiet polls.

## Resume

Use the exact thread ID. Run the shell tool with `workdir` set to the worker's absolute worktree and re-pin model, effort, sandbox, JSON output, and final artifact. The local resume parser lacks `--cd` and `-s`; use the command working directory and the sandbox config override instead:

```bash
codex exec resume \
  -m gpt-5.6-terra -c model_reasoning_effort=xhigh \
  -c 'sandbox_mode="workspace-write"' \
  --json \
  --output-last-message /absolute/task-scratch/repair-1.md \
  THREAD_UUID - < /absolute/task-scratch/repair-1.txt \
  > /absolute/task-scratch/repair-1.jsonl \
  2> /absolute/task-scratch/repair-1.stderr
```

Resume only after the previous process has stopped. Preserve prior artifacts by using a new output path/generation per round, retaining the task ID and corrective-retry count even when switching models. Seed replacements from the actual checkpoint path. Use a fresh dispatch for a poisoned context or an independent reviewer. Do not use `--ephemeral` for a worker that may need resume.

For live steering, prefer native workers. Do not assume CLI queue, fork, or external-child messaging behavior based on old source notes; verify the available control surface before depending on it.

## Tool and output limits

CLI workers do not automatically inherit session connectors or browser state. Check the required tool before assigning a tool-bound leg. If a lookup requires web access, verify the installed search configuration; do not copy old boolean web-search flags. Carry the user's required HTTP user agent, `OpenAI File Downloader, XaiImageApiFetch/1.0`, into any brief that makes configurable web requests.

If the user specifically requests a Codex CLI review, use a read-only `codex exec` brief with the exact snapshot and acceptance contract. This avoids assuming that custom prompts can be combined with scoped `codex review` flags. The default independent reviewer remains Claude.

`--output-schema` can constrain a final JSON result, but the lead must still validate the artifact and substantive claims. For a tool-heavy leg, prefer an ordinary work report and a separate bounded formatting pass if machine-readable output is actually required. Do not add formatting turns to normal coding tasks.
