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
  "model": "gpt-6-sol",
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

Artifacts share one prefix: `.dispatch.json` (requested record, argv, PID, paths, brief hash), `.events.jsonl`, `.stderr`, `.last.md`, and the separately authored `.report.md`. Existing paths cause refusal; reconcile them or use the next run number. A prepared dispatch record proves neither launch success nor completion. Read the current events and last message after the harness completes; keep the existing `turn.completed` / `turn.failed` acceptance checks.

The helper records requested settings, with runtime model/effort initially unknown. If the CLI exposes actual settings, record the observation and its source in the current manifest. Otherwise leave them unknown. Configuration defaults, worker guesses, and the requested argv are not actual-runtime evidence. Extract the thread ID from a `thread.started` event wherever it occurs, not necessarily the first line. Do not sum cumulative usage from multiple resumes; use each thread's final total or per-turn differences when auditing usage.

Optional fields are `output_schema` (absolute file path), `web_search` (`disabled`, `cached`, or `live`), `skip_git_repo_check` (boolean, default false; set it only for a workspace outside a Git repo, since the default keeps Codex's outside-a-repo guard), and `user_gated: true`, which is **required** when `effort` is `ultra` and records that the user authorized this dispatch; the helper refuses `ultra` without it and refuses `minimal` and `persistent` outright. The helper intentionally covers the ordinary CLI surface only. A specialized invocation such as `--approve-for-me` must keep its existing permission controls and use the same explicit model/effort, cwd, finite stdin, and unique-artifact contract; do not switch permission mode to fit the helper. Inspect current CLI help before using an unsupported flag. Validate the helper locally with `python3 scripts/test_dispatch.py`; its CLI is a stub, so no worker tokens are used. Argv was checked against `codex exec`, `exec resume`, and `exec fork --help` on codex-cli 0.154.0 (2026-09-11).

## Test ownership and reuse

The lead defines contract-derived acceptance cases. The existing implementation worker authors and runs routine regressions in its owned paths, reusing established fixtures and harnesses. Assign shared harness changes one owner and extend that harness only when a case needs it; do not regenerate DOM, HTTP, or UI setup for successive increments. If a harness is missing, assign the smallest necessary setup with the implementation.

The lead independently inspects the integrated diff and test assertions, with targeted integration probes where needed. Additional lead-authored tests address a named uncovered risk. Independence does not require a duplicate harness or a standing second test agent. Preserve meaningful regression coverage and required gates.

## Prepare the worktree once

Before launch, run the repo-owned bootstrap/readiness command in each new worktree, using the pinned toolchain and required per-process environment. Check dependencies, test discovery, and offline assets required by that leg. Reuse existing setup/doctor tools; do not invent a Proofset or other project command in this generic skill. If no readiness command exists, perform the smallest equivalent check and record its result. Do not run the full suite as a readiness probe.

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

For large data inputs, inspect keys, types, row counts, and the few fields needed for the acceptance claim first. Extract compact results with source paths and exact arithmetic. Escalate a real schema ambiguity; do not repeatedly dump whole JSON files into context or invent a field from its name.

## Focused evidence and bookkeeping

Before reading a large artifact, name the question it must answer. Prefer focused diffs, selected source ranges, and compact command results, with full logs saved for diagnostics. Preserve process handles, real exit status, run and snapshot identity, and evidence paths when limiting output. Read full context when needed; do not repeatedly reread unrelated or unchanged material, and never discard essential evidence or restart tasks on a schedule to avoid compaction.

Reuse repo or skill helpers for recurring snapshot capture, result parsing, artifact copying, and task-state updates. Use a small direct edit for one-off work. A reusable helper is justified by repeated concrete need, not by a desire for a new orchestration framework. Helpers preserve evidence and execute decided updates; the lead still rules on acceptance and authority.
