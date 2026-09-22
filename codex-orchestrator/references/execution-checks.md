# Worktree readiness and check evidence

Apply to native and CLI workers when their leg runs checks. Use existing repo setup/selection tools and the current manifest; this does not add an agent or a new review gate. Native dispatch uses [native-agents.md](native-agents.md); the sandbox-only CLI helper is described in [cli-workers.md](cli-workers.md). Restricted Claude reviewers return reproduction requests to Astra and do not gain shell access from these examples.

## Test ownership and reuse

The lead defines contract-derived acceptance cases. The existing implementation worker authors and runs routine regressions in its owned paths, reusing established fixtures and harnesses. Assign shared harness changes one owner and extend that harness only when a case needs it; do not regenerate DOM, HTTP, or UI setup for successive increments. If a harness is missing, assign the smallest necessary setup with the implementation.

The lead independently inspects the integrated diff and test assertions, with targeted integration probes where needed. Additional lead-authored tests address a named uncovered risk. Independence does not require a duplicate harness or a standing second test agent. Preserve meaningful regression coverage and required gates.

## Prepare the worktree once

Before launch, run the repo-owned bootstrap/readiness command in each new worktree, using the pinned toolchain and required per-process environment. Check dependencies, test discovery, and offline assets required by that leg. Reuse existing setup/doctor tools; do not invent a project-specific command in this generic skill. If no readiness command exists, perform the smallest equivalent check and record its result. Do not run the full suite as a readiness probe.

Share a discovered environment fix with affected workers. Repair missing prerequisites before a same-worker/tier continuation; environment recovery alone is not a reason to raise model or effort. If a worker already produced a usable commit and only a lead-owned check remains, the lead can verify and record it without a worker turn solely for validation/report cleanup.

## Preserve check scope, logs, and process handles

Before a costly check, inspect its selection/dry-run output when available. A command named `fast` may select the full suite. Record the selected scope and reason, assign the full check to its owner, and retain repository-required gates. Do not suppress unknown paths or evidence-bearing fixtures merely to obtain a smaller selection.

For each long check, record owner, exact command/cwd/environment requirements, tested SHA **and dirty-state description**, selected scope, fresh log path, harness handle, and final exit/result. Keep secrets out of these records. Use the repo's check wrapper when it provides this evidence; otherwise a shell wrapper can preserve the true exit status:

```bash
set -C
log="/absolute/scratchpad/artifacts/TASK-ID.g1.check-name.log"
result="/absolute/scratchpad/artifacts/TASK-ID.g1.check-name.exit"
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

## Focused evidence and bookkeeping

Before reading a large artifact, name the question it must answer. Prefer focused diffs, selected source ranges, and compact command results with full logs saved for diagnostics. Preserve process handles, real exit status, generation and snapshot identity, and evidence paths when limiting output. Read full context when needed; do not repeatedly reread unrelated or unchanged material. Never discard essential evidence or force fresh tasks on a schedule to avoid compaction.

For large data, inspect keys/types and extract needed fields with source paths and exact arithmetic. Escalate schema ambiguity rather than infer units or dump entire payloads.

Reuse repo or skill helpers for recurring snapshot capture, result parsing, artifact copying, and task-state updates. Use a small direct edit for one-off work. A reusable helper is justified by repeated concrete need, not by a desire for a new orchestration framework. Helpers preserve evidence and execute decided updates; the lead still rules on acceptance and authority.
